"""PIE run support for train_first.py / train_second.py (2026-11-08, native Windows on tr-desktop):

  stop/resume   last.pth in the log dir holds everything needed to continue mid-epoch: weights, optimizer moments,
                epoch, step within the epoch, iters, the absolute epoch bounds, RNG states. Written atomically
                (last.pth.tmp -> os.replace; the previous one kept as prev.pth) every PIE_SAVE_MIN minutes (default 20),
                at each epoch end, and when a STOP file appears in the log dir (then the trainer exits 0).
                A start with last.pth present resumes from it; PIE_FRESH=1 ignores it.
  data order    EpochSampler: the shuffle of epoch e is a fixed permutation (seed + e), so a resume at step k skips
                exactly the batches already trained (indices only, no audio is loaded for them).
  logging       metrics.jsonl (one JSON event per line: run start/resume, train every log_interval steps with every
                loss, lr, s/step and peak memory, val per epoch, checkpoint, stop, done), manifest.json (config, git-free
                environment: torch/cuda/triton versions, GPU, env switches, dataset counts), gpu.csv (nvidia-smi every 30 s).
"""
import json, os, random, subprocess, threading, time

import numpy as np
import torch
from torch.utils.data import Sampler


def unwrap(m):
    """the plain module under DataParallel / accelerate wrappers (state_dict keys without 'module.')"""
    while hasattr(m, "module"):
        m = m.module
    return m


class EpochSampler(Sampler):
    def __init__(self, n, seed=1234):
        self.n, self.seed, self.epoch, self.skip = n, seed, 0, 0

    def set_epoch(self, epoch, skip_samples=0):
        self.epoch, self.skip = epoch, skip_samples

    def __iter__(self):
        g = torch.Generator().manual_seed(self.seed + self.epoch)
        return iter(torch.randperm(self.n, generator=g)[self.skip:].tolist())

    def __len__(self):
        return self.n - self.skip


class Run:
    def __init__(self, log_dir, stage, config):
        self.dir, self.stage = log_dir, stage
        os.makedirs(log_dir, exist_ok=True)
        self.metrics = open(os.path.join(log_dir, "metrics.jsonl"), "a", encoding="utf-8")
        self.save_every = float(os.environ.get("PIE_SAVE_MIN", "20")) * 60
        self.last_save = time.time()
        self.t_start = time.time()
        self._gpu_thread()
        self.write_manifest(config)

    # ---- logging
    def log(self, event, **kw):
        row = {"event": event, "stage": self.stage, "t": round(time.time(), 1), **kw}
        self.metrics.write(json.dumps(row, ensure_ascii=False, default=float) + "\n")
        self.metrics.flush()

    def write_manifest(self, config):
        try:
            import triton
            tv = triton.__version__
        except Exception:
            tv = None
        man = {"stage": self.stage, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "config": config,
               "torch": torch.__version__, "cuda": torch.version.cuda, "cudnn": torch.backends.cudnn.version(),
               "triton": tv, "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
               "env": {k: v for k, v in os.environ.items() if k.startswith("PIE_") or k in ("ACCELERATE_MIXED_PRECISION",)}}
        for split in ("train_data", "val_data"):
            p = config.get("data_params", {}).get(split)
            if p and os.path.exists(p):
                rows = [l.rstrip("\n").split("|") for l in open(p, encoding="utf-8") if l.strip()]
                man[split] = {"path": p, "files": len(rows), "per_speaker": {s: sum(r[2] == s for r in rows) for s in sorted({r[2] for r in rows})}}
        path = os.path.join(self.dir, "manifest.json")
        hist = []
        if os.path.exists(path):
            try:
                old = json.load(open(path, encoding="utf-8"))
                hist = old.get("history", []) + [{k: old.get(k) for k in ("started", "env")}]
            except Exception:
                pass
        man["history"] = hist
        json.dump(man, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)

    def _gpu_thread(self):
        path = os.path.join(self.dir, "gpu.csv")

        def loop():
            while True:
                try:
                    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw",
                                        "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.strip()
                    with open(path, "a") as f:
                        f.write(f"{int(time.time())},{q.replace(' ', '')}\n")
                except Exception:
                    pass
                time.sleep(30)
        threading.Thread(target=loop, daemon=True).start()

    # ---- stop / resume
    def stop_requested(self):
        return os.path.exists(os.path.join(self.dir, "STOP"))

    def due(self):
        return time.time() - self.last_save >= self.save_every

    def save(self, model, optimizer, epoch, step, iters, bounds, why):
        t = time.time()
        state = {"net": {k: unwrap(model[k]).state_dict() for k in model}, "optimizer": optimizer.state_dict(),
                 "epoch": epoch, "step": step, "iters": iters, "bounds": bounds,
                 "rng": {"torch": torch.get_rng_state(), "cuda": torch.cuda.get_rng_state_all(),
                         "numpy": np.random.get_state(), "python": random.getstate()}}
        last, tmp, prev = (os.path.join(self.dir, n) for n in ("last.pth", "last.pth.tmp", "prev.pth"))
        torch.save(state, tmp)
        if os.path.exists(last):
            os.replace(last, prev)
        os.replace(tmp, last)
        self.last_save = time.time()
        self.log("checkpoint", file="last.pth", epoch=epoch, step=step, iters=iters, why=why,
                 seconds=round(time.time() - t, 1), bytes=os.path.getsize(last))

    def resume_state(self):
        p = os.path.join(self.dir, "last.pth")
        if os.environ.get("PIE_FRESH") == "1" or not os.path.exists(p):
            return None
        return torch.load(p, map_location="cpu", weights_only=False)

    def restore(self, st, model, optimizer):
        for k in model:
            if k in st["net"]:
                unwrap(model[k]).load_state_dict(st["net"][k], strict=True)
        optimizer.load_state_dict(st["optimizer"])
        torch.set_rng_state(st["rng"]["torch"]); torch.cuda.set_rng_state_all(st["rng"]["cuda"])
        np.random.set_state(st["rng"]["numpy"]); random.setstate(st["rng"]["python"])
        self.log("resume", epoch=st["epoch"], step=st["step"], iters=st["iters"], bounds=st["bounds"])
        print(f"PIE resume: epoch index {st['epoch']}, step {st['step']}, iters {st['iters']}", flush=True)


def annotate(named):
    """PIE_PROFILE: label each module's forward (and so its kernels) in the profiler, as 'pie:<name>'"""
    import functools
    from torch.profiler import record_function

    def wrap(name, f):
        @functools.wraps(f)
        def g(*a, **k):
            with record_function(f"pie:{name}"):
                return f(*a, **k)
        return g
    for name, m in named.items():
        m = unwrap(m)
        m.forward = wrap(name, m.forward)
        for sub_name, sub in m.named_children():          # one level down too (e.g. text_aligner.asr_s2s)
            sub.forward = wrap(f"{name}.{sub_name}", sub.forward)


MEM = {}


def annotate_memory(named):
    """PIE_MEMPROF: per module, the GPU memory its forward leaves allocated (activations kept for backward), summed
    over the step's calls; printed by mem_report()"""
    def wrap(name, f):
        def g(*a, **k):
            before = torch.cuda.memory_allocated()
            out = f(*a, **k)
            MEM[name] = MEM.get(name, 0) + torch.cuda.memory_allocated() - before
            return out
        return g
    for name, m in named.items():
        m = unwrap(m)
        m.forward = wrap(name, m.forward)


def mem_report(step):
    print(f"PIE_MEM step {step}: " + ", ".join(f"{k} {v / 2**30:.2f}" for k, v in sorted(MEM.items(), key=lambda x: -x[1])) +
          f"  | peak {torch.cuda.max_memory_allocated() / 2**30:.2f} GiB", flush=True)
    MEM.clear()


def checkpoint_modules(model, names):
    """PIE_CKPT=msd,mpd,decoder: activation checkpointing on those modules' forward (recomputed in backward instead of
    stored). Exact (RNG state preserved for any dropout); costs a second forward on an otherwise idle GPU, and frees the
    memory that capped the batch size (Stage 1, batch 4: msd 6.4, decoder 5.4, mpd 3.1 GiB of activations)."""
    import functools
    from torch.utils.checkpoint import checkpoint
    for name in names:
        m = unwrap(model[name])
        f = m.forward

        @functools.wraps(f)
        def g(*a, _f=f, **k):
            if not torch.is_grad_enabled():
                return _f(*a, **k)
            return checkpoint(_f, *a, use_reentrant=False, **k)
        m.forward = g
        print("PIE checkpointed", name, flush=True)
