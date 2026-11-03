"""Training dashboard: serves the runs directory and a live page (standard library only).

    python dashboard.py [--runs Q:\\AI\\PIE\\runs] [--tinker Q:\\AI\\PIE\\tinker\\runs] [--rl Q:\\AI\\PIE\\rl\\runs] [--port 8790]
    then open http://127.0.0.1:8790 (fine-tuning) or http://127.0.0.1:8790/rl (RL on the Mac)

GET /api/runs        every run: its config.json and metrics.jsonl; Tinker runs (training/tinker) as "tinker/<run>",
                     their cookbook logs converted to the same events (tinker_run)
GET /api/gens?run=R&epoch=N   that run's generations-eN.jsonl (and its scores-eN.json when the Mac has scored it)
GET /api/tts         the Kokoro fine-tune on tr-desktop (training/tts_monitor.sh mirrors its WSL logs to --tts): per-stage
                     loss series, step time and memory, validation losses, GPU samples, checkpoints
GET /api/rl          every RL run (training/rl, synced from the Mac by training/rl/sync_dashboard.sh): its
                     config.yaml, metrics.jsonl, per-kind rewards (rewards.jsonl, in windows) and the frozen-prompt
                     scores of its checkpoints (eval/summary.txt)
"""
import argparse
import json
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent


def read_jsonl(p: Path) -> list:
    if not p.exists():
        return []
    out = []
    for line in p.read_text("utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:          # a line being written right now
            pass
    return out


TINKER_WINDOW = 10      # Tinker logs every step; the 4B logs every 5. Mean train loss over windows of this many steps


def tinker_run(d: Path) -> dict:
    """A tinker_cookbook supervised run's log dir (config.json, metrics.jsonl, checkpoints.jsonl) as a dashboard run:
    the per-step train_mean_nll (nats per trained token, the 4B's loss) averaged over TINKER_WINDOW steps, the lr, and
    tokens per second of step time. Done when checkpoints.jsonl has its "final" row."""
    cfg = json.loads((d / "config.json").read_text("utf-8")) if (d / "config.json").exists() else {}
    rows = [m for m in read_jsonl(d / "metrics.jsonl") if "train_mean_nll" in m]
    epochs = cfg.get("num_epochs") or 1
    total = round((rows[-1]["step"] + 1) / rows[-1]["progress"]) if rows and rows[-1].get("progress") else None
    metrics, elapsed = [], 0.0
    for i in range(0, len(rows), TINKER_WINDOW):
        w = rows[i:i + TINKER_WINDOW]
        secs = sum(m.get("time/step") or 0 for m in w)
        elapsed += secs
        metrics.append({"event": "train", "step": w[-1]["step"], "epoch": round(w[-1]["progress"] * epochs, 3),
                        "loss": round(sum(m["train_mean_nll"] for m in w) / len(w), 4), "lr": w[-1]["learning_rate"],
                        "tok_per_s": round(sum(m["num_tokens"] for m in w) / secs) if secs else None,
                        "elapsed_min": round(elapsed / 60, 1)})
    ckpts = read_jsonl(d / "checkpoints.jsonl")
    if any(c.get("name") == "final" for c in ckpts):
        metrics.append({"event": "done", "step": rows[-1]["step"] if rows else 0, "elapsed_min": round(elapsed / 60, 1)})
    return {"name": f"tinker/{d.name}", "metrics": metrics,
            "config": {"model": cfg.get("model_name", ""), "lr": cfg.get("learning_rate"), "rank": cfg.get("lora_rank"),
                       "total_steps": total, "backend": "tinker",
                       "checkpoints": [c.get("name") for c in ckpts]},
            "epochs": sorted(int(p.stem.split("-e")[-1]) for p in d.glob("generations-e*.jsonl"))}


RL_WINDOW = 5           # rewards.jsonl has a row per step; mean per kind over windows of this many


def rl_run(d: Path) -> dict:
    """An RL run's synced log dir as the /rl page's run: train/val events as logged by training/rl/grpo.py, the
    per-kind reward means in RL_WINDOW-step windows, and each "<run> generations-<set>-<ckpt> {summary}" line that
    training/score_generations.py printed into eval/summary.txt."""
    allrows = read_jsonl(d / "rewards.jsonl")
    # stage 1b logs the valid split's strata with a "v." prefix (training/rl/reward_rl.py): those rows are the
    # validation rounds, one run of consecutive rows each, at the steps of the metrics log's val events
    rows = [r for r in allrows if not any(k.startswith("reward/v.") for k in r)]
    kinds = sorted({k for r in rows for k in r if k.startswith("reward/")})
    rewards = []
    for i in range(0, len(rows), RL_WINDOW):
        w = rows[i:i + RL_WINDOW]
        rewards.append({"step": i + len(w), **{k: round(sum(r[k] for r in w if k in r) / max(1, sum(k in r for r in w)), 4)
                                               for k in kinds if any(k in r for r in w)},
                        **({"judge_usd": w[-1]["judge_usd"]} if "judge_usd" in w[-1] else {}),
                        **({"judge_s": round(sum(r.get("judge_s", 0) for r in w) / len(w), 1)} if "judge_s" in w[-1] else {})})
    vsteps = [m.get("iteration") for m in read_jsonl(d / "metrics.jsonl") if m.get("event") == "val"]
    rounds, prev = [], False
    for r in allrows:
        isv = any(k.startswith("reward/v.") for k in r)
        if isv and not prev:
            rounds.append([])
        if isv:
            rounds[-1].append(r)
        prev = isv
    val_strata = []
    for j, w in enumerate(rounds):
        ks = sorted({k for r in w for k in r if k.startswith("reward/v.")})
        val_strata.append({"step": vsteps[j] if j < len(vsteps) else None,
                           **{k.removeprefix("reward/v."): round(sum(r[k] * r["n"] for r in w if k in r) /
                                                                  max(1, sum(r["n"] for r in w if k in r)), 4) for k in ks}})
    evals = []
    sm = d / "eval" / "summary.txt"
    for line in (sm.read_text("utf-8").splitlines() if sm.exists() else []):
        parts = line.split(" ", 2)
        if len(parts) == 3 and parts[1].startswith("generations-") and parts[2].startswith("{"):
            st, _, ck = parts[1].removeprefix("generations-").rpartition("-")
            try:
                evals.append({"set": st, "ckpt": ck, **json.loads(parts[2])})
            except json.JSONDecodeError:
                pass
    cfg = d / "config.yaml"
    man = d / "manifest.json"
    files = [f for f in d.rglob("*") if f.is_file()]
    return {"name": d.name, "metrics": read_jsonl(d / "metrics.jsonl"), "rewards": rewards, "evals": evals,
            "val_strata": val_strata, "pipeline": rl_pipeline(d / "pipeline.log"),
            "updated": max((f.stat().st_mtime for f in files), default=0),
            "data": json.loads(man.read_text("utf-8")).get("passrate") if man.exists() else None,
            "config": cfg.read_text("utf-8") if cfg.exists() else ""}


PASSRATE = re.compile(r"(\d+)/(\d+) candidates, (\d+) s, eta (\d+) min")


def rl_pipeline(p: Path):
    """The stage pipeline's log (run_rl5.sh and later, synced as pipeline.log): which phase it is in, and the prompt
    filter's progress while it runs."""
    if not p.exists():
        return None
    phase, prog = "starting", None
    for line in p.read_text("utf-8", errors="replace").splitlines():
        if line.endswith(" passrate"):
            phase = "filtering"
        elif m := PASSRATE.search(line):
            prog = {"done": int(m[1]), "total": int(m[2]), "elapsed_s": int(m[3]), "eta_min": int(m[4])}
        elif line.endswith(" train"):
            phase = "training"
        elif "waiting for the trainer" in line:
            phase = "training"
        elif line.endswith("pipeline done"):
            phase = "done"
    return {"phase": phase, "filter": prog, "tail": p.read_text("utf-8", errors="replace").splitlines()[-1:]}


LOSS = re.compile(r"([A-Za-z0-9]+(?: [A-Za-z0-9]+)?) Loss: ([-0-9.e]+|nan)")
STEP = re.compile(r"Epoch \[(\d+)/(\d+)\], Step \[(\d+)/(\d+)\]")
PIE_STEP = re.compile(r"PIE_STEP (\d+) ([0-9.]+) s/step\s+peak ([0-9.]+) GiB")
VAL = re.compile(r"(?:Validation|val)[ _]?(?:mel )?loss[: ]+([0-9.]+)", re.I)


def tts_stage(p: Path) -> dict:
    """One stage's train log (StyleTTS2 train_first/train_second, with the PIE_STEP timer) as series."""
    out = {"points": [], "timing": [], "val": [], "epochs": None, "steps_per_epoch": None, "tail": [], "exit": None,
           "errors": []}
    if not p.exists():
        return out
    lines = p.read_text("utf-8", errors="replace").splitlines()
    # the Stage 2 hand-off writes its smoke test's last lines before the real run's: parse only the real run
    start = max((i for i, l in enumerate(lines) if "starting Stage 2" in l), default=-1) + 1
    resumed = False
    for line in lines[start:]:
        m = STEP.search(line)
        if m:
            e, ne, st, ns = map(int, m.groups())
            if resumed:                                 # a resume redoes epoch e: drop what crashed attempts logged from it
                for k in ("points", "timing", "val"):
                    out[k] = [q for q in out[k] if q["epoch"] < e]
                resumed = False
            out["epochs"], out["steps_per_epoch"] = ne, ns
            losses = {k.strip(): (None if v == "nan" else float(v)) for k, v in LOSS.findall(line)}
            m2 = re.search(r"\], Loss: ([-0-9.e]+|nan)", line)      # Stage 2 prints the mel loss as plain "Loss:"
            if m2 and "Mel" not in losses:
                losses["Mel"] = None if m2[1] == "nan" else float(m2[1])
            out["points"].append({"epoch": e, "step": st, "x": round(e - 1 + st / ns, 4), **losses})
            continue
        m = PIE_STEP.search(line)
        if m:
            out["timing"].append({"i": int(m[1]), "s_per_step": float(m[2]), "peak_gib": float(m[3]),
                                  "epoch": out["points"][-1]["epoch"] if out["points"] else 1})
            continue
        m = VAL.search(line)
        if m and out["points"]:
            out["val"].append({"epoch": out["points"][-1]["epoch"], "loss": float(m[1])})
        if "resuming Stage 2" in line:                  # a resume: earlier errors and exit belong to the run before
            out["errors"], out["exit"] = [], None
            resumed = True
        if " EXIT " in line:
            out["exit"] = line.strip()
        if re.search(r"Traceback|OutOfMemory|CUDA error|Error:", line):
            out["errors"].append(line.strip()[:300])
    out["tail"] = lines[-12:]
    return out


def tts_status(d: Path) -> dict:
    gpu = []
    g = d / "gpu.csv"
    for line in (g.read_text().splitlines()[-1500:] if g.exists() else []):
        try:
            t, used, total, util, temp, power = line.split(",")[:6]
            gpu.append({"t": int(t), "used": int(used), "total": int(total), "util": int(util), "temp": int(temp),
                        "power": float(power)})
        except ValueError:
            pass
    ck = d / "ckpts.txt"
    ckpts = [dict(zip(("t", "bytes", "path"), l.split())) for l in (ck.read_text().splitlines() if ck.exists() else []) if l.strip()]
    up = d / "updated.txt"
    upd = int(up.read_text().strip()) if up.exists() and up.read_text().strip().isdigit() else None
    stages = {s: tts_stage(d / f"{s}.log") for s in ("stage1", "stage2")}
    off = stages["stage1"]["epochs"] or 0               # one timeline: Stage 2 continues after Stage 1's epochs
    for p in stages["stage2"]["points"]:
        p["x"] = round(p["x"] + off, 4)
    stages["stage2"]["x_offset"] = off
    return {"now": int(time.time()), "updated": upd, "gpu": gpu, "checkpoints": ckpts, "stages": stages}


def make_handler(runs: Path, tinker: Path, rl: Path, tts=None):
    class H(BaseHTTPRequestHandler):
        def send(self, code, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def json(self, obj):
            self.send(200, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            if u.path in ("/", "/index.html"):
                return self.send(200, (HERE / "dashboard.html").read_bytes(), "text/html; charset=utf-8")
            if u.path in ("/rl", "/rl.html"):
                return self.send(200, (HERE / "rl.html").read_bytes(), "text/html; charset=utf-8")
            if u.path in ("/tts", "/tts.html"):
                return self.send(200, (HERE / "tts.html").read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/tts":
                return self.json(tts_status(tts) if tts else {})
            if u.path == "/api/rl":
                out = [rl_run(d) for d in rl.iterdir() if d.is_dir()] if rl.is_dir() else []
                return self.json(sorted(out, key=lambda r: -r["updated"]))      # newest first
            if u.path == "/api/runs":
                out = []
                for d in sorted(p for p in runs.iterdir() if p.is_dir()):
                    cfg = json.loads((d / "config.json").read_text("utf-8")) if (d / "config.json").exists() else {}
                    epochs = sorted(int(p.stem.split("-e")[-1]) for p in d.glob("generations-e*.jsonl"))
                    out.append({"name": d.name, "config": cfg, "metrics": read_jsonl(d / "metrics.jsonl"),
                                "epochs": epochs})
                if tinker.is_dir():
                    out += [tinker_run(d) for d in sorted(p for p in tinker.iterdir() if p.is_dir())]
                return self.json(out)
            if u.path == "/api/gens":
                name = q.get("run", [""])[0]
                root = tinker if name.startswith("tinker/") else runs
                d = root / name.removeprefix("tinker/")
                e = q.get("epoch", ["1"])[0]
                if not d.resolve().is_relative_to(root.resolve()):
                    return self.send(400, b"bad run", "text/plain")
                sc = d / f"scores-e{e}.json"
                return self.json({"gens": read_jsonl(d / f"generations-e{e}.jsonl"),
                                  "scores": json.loads(sc.read_text("utf-8")) if sc.exists() else None})
            self.send(404, b"not found", "text/plain")

        def log_message(self, *a):
            pass
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=r"Q:\AI\PIE\runs")
    ap.add_argument("--tinker", default=r"Q:\AI\PIE\tinker\runs")
    ap.add_argument("--rl", default=r"Q:\AI\PIE\rl\runs")
    ap.add_argument("--tts", default=r"C:\Users\David\Downloads\PIE\tts-corpus-v1\kokoro-monitor")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8790)
    a = ap.parse_args()
    runs = Path(a.runs)
    runs.mkdir(parents=True, exist_ok=True)
    print(f"dashboard on http://{a.host}:{a.port}")
    ThreadingHTTPServer((a.host, a.port), make_handler(runs, Path(a.tinker), Path(a.rl), Path(a.tts))).serve_forever()


if __name__ == "__main__":
    main()
