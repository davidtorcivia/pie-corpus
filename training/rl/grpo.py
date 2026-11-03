"""mlx-lm-lora GRPO on the Mac, with the three fixes our model needs and a metrics log for the dashboard.

    PIE_RL_RUN_DIR=DIR python -I training/rl/grpo.py --config training/rl/engine_drills.yaml [mlx-lm-lora args]

1. Decode concurrency: mlx-lm-lora's generate_grpo caps the BatchGenerator at --batch-size sequences, so a step's
   batch x group rollouts decode 4 or 8 at a time. Here all of them decode together: 2x faster generation on the
   M3 Ultra (32 rollouts: 30 s -> 15 s; docs/research/rl-mac.md).
2. Thinking off: the SFT renderer was qwen3_5_disable_thinking (an empty think block), but GRPODataset applies the
   chat template with its default, which opens a think block. Prompts are built with enable_thinking=False.
3. A metrics log: every report and eval goes to DIR/metrics.jsonl with the step's generation time, plus
   per-kind reward means from training/rl/reward_engine.py or reward_rl.py (DIR/rewards.jsonl), and every judge
   call (DIR/judge.jsonl).
"""
import json
import os
import sys
import time
from pathlib import Path

import mlx_lm_lora.train as tr
import mlx_lm_lora.trainer.datasets as ds
import mlx_lm_lora.trainer.grpo_trainer as g
from mlx_lm.tuner.callbacks import TrainingCallback

RUN = Path(os.environ["PIE_RL_RUN_DIR"])
RUN.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("PIE_RL_REWARD_LOG", str(RUN / "rewards.jsonl"))
os.environ.setdefault("PIE_RL_JUDGE_LOG", str(RUN / "judge.jsonl"))       # every judge call (reward_rl.py)
LOG = open(RUN / "metrics.jsonl", "a", encoding="utf-8")
GEN = {"s": 0.0, "tokens": 0, "rollouts": 0}


def nums(info: dict) -> dict:
    out = {}
    for k, v in info.items():
        try:
            out[k] = float(v)
        except (TypeError, ValueError):
            pass
    return out


def log(row: dict):
    LOG.write(json.dumps({"t": time.time(), **row}, default=float) + "\n")
    LOG.flush()


_BG = g.BatchGenerator


class AllAtOnce(_BG):
    def __init__(self, *a, **k):
        k["completion_batch_size"] = k["prefill_batch_size"] = 1 << 10
        super().__init__(*a, **k)


g.BatchGenerator = AllAtOnce

_generate = g.generate_grpo


def generate(*a, **k):
    t = time.time()
    out = _generate(*a, **k)
    GEN["s"] += time.time() - t
    GEN["tokens"] += sum(len(c) for c in out[0])
    GEN["rollouts"] += len(out[0])
    return out


g.generate_grpo = generate

_init = ds.GRPODataset.__init__


def init(self, data, tokenizer, *a, **k):
    apply = tokenizer.apply_chat_template
    tokenizer.apply_chat_template = lambda m, **kw: apply(m, **{"enable_thinking": False, **kw})
    try:
        _init(self, data, tokenizer, *a, **k)
    finally:
        tokenizer.apply_chat_template = apply


ds.GRPODataset.__init__ = init


REF_ADAPTER = os.environ.get("PIE_REF_ADAPTER")           # stage 4: KL to the policy RL starts from (base + merge)
KL_STOP = float(os.environ.get("PIE_KL_STOP", "0"))          # stop after 2 reports in a row above it (0 = off)
VAL_STOP = float(os.environ.get("PIE_VAL_STOP", "0"))        # stop when val loss > VAL_STOP x the first one (0 = off)

if REF_ADAPTER:
    def _load_ref(args):
        from mlx_lm import load
        print(f"Loading reference model {args.model} + adapter {REF_ADAPTER}")
        model, _ = load(args.model, adapter_path=REF_ADAPTER)
        return model.freeze()
    tr.load_reference_model = _load_ref


class Stop(Exception):
    pass


class Metrics(TrainingCallback):
    """Logs every report; stops the run on drift (rl3 drifted after ~450 steps: KL 0.18 -> 0.66, val loss x1.7;
    docs/research/rl-lessons.md). The last saved checkpoint (save_every) is the one to use."""
    high = 0
    val0 = None

    def on_train_loss_report(self, info: dict):
        log({"event": "train", **nums(info),
             "gen_s": GEN["s"], "gen_tokens": GEN["tokens"], "gen_rollouts": GEN["rollouts"]})
        GEN.update(s=0.0, tokens=0, rollouts=0)
        kl = nums(info).get("train_kl")
        if KL_STOP and kl is not None:
            self.high = self.high + 1 if kl > KL_STOP else 0
            if self.high >= 2:
                log({"event": "stop", "why": f"KL above {KL_STOP} on 2 reports", "iteration": info.get("iteration")})
                raise Stop(f"KL above {KL_STOP} on 2 reports in a row")

    def on_val_loss_report(self, info: dict):
        log({"event": "val", **nums(info)})
        v = nums(info).get("val_loss")
        if VAL_STOP and v is not None:
            if self.val0 is None:
                self.val0 = v
            # with the reference = the starting policy the first val loss is ~0 (stage 4: -2e-9), so a ratio to it
            # stops on any positive loss: use a floor (the GRPO val loss is ~KL-scale, not a quality measure)
            elif v > VAL_STOP * max(self.val0, 0.02):
                log({"event": "stop", "why": f"val loss {v:.4f} > {VAL_STOP} x {self.val0:.4f}", "iteration": info.get("iteration")})
                raise Stop("validation loss rose")


_run = tr.run
tr.run = lambda args, training_callback=None: _run(args, Metrics())

def yaml_wins(argv: list[str]) -> list[str]:
    """mlx-lm-lora applies a config value only when the matching CLI option is None, so an option with a parser
    default (group_size 4, max_completion_length 512) silently ignores the YAML: stage 1 ran with 4 rollouts per
    prompt, not the configured 8 (found 2026-11-01). Pass those keys explicitly; explicit CLI args still win."""
    import yaml
    if "--config" not in argv:
        return argv
    cfg = yaml.load(open(argv[argv.index("--config") + 1]), Loader=tr.yaml_loader)
    parser = tr.build_parser()
    defaults = vars(parser.parse_args([]))
    given = {a.lstrip("-").replace("-", "_") for a in argv if a.startswith("--")}
    extra = []
    for k, v in cfg.items():
        if defaults.get(k) is not None and defaults[k] != v and k not in given:
            flag = next(o for a in parser._actions if a.dest == k for o in a.option_strings if o.startswith("--"))
            extra += [flag] if v is True else [] if v is False else [flag, str(v)]
    return argv + extra


if __name__ == "__main__":
    sys.argv = [sys.argv[0]] + yaml_wins(sys.argv[1:])
    log({"event": "start", "argv": sys.argv[1:]})
    try:
        tr.main()
        log({"event": "done"})
    except Stop as e:
        print(f"STOPPED: {e}", flush=True)
        log({"event": "done", "stopped": str(e)})
