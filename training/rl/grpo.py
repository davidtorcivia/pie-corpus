"""mlx-lm-lora GRPO on the Mac, with the three fixes our model needs and a metrics log for the dashboard.

    PIE_RL_RUN_DIR=DIR python -I training/rl/grpo.py --config training/rl/engine_drills.yaml [mlx-lm-lora args]

1. Decode concurrency: mlx-lm-lora's generate_grpo caps the BatchGenerator at --batch-size sequences, so a step's
   batch x group rollouts decode 4 or 8 at a time. Here all of them decode together: 2x faster generation on the
   M3 Ultra (32 rollouts: 30 s -> 15 s; docs/research/rl-mac.md).
2. Thinking off: the SFT renderer was qwen3_5_disable_thinking (an empty think block), but GRPODataset applies the
   chat template with its default, which opens a think block. Prompts are built with enable_thinking=False.
3. A metrics log: every report and eval goes to DIR/metrics.jsonl with the step's generation time, plus
   per-kind reward means from training/rl/reward_engine.py (DIR/rewards.jsonl).
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


class Metrics(TrainingCallback):
    def on_train_loss_report(self, info: dict):
        log({"event": "train", **nums(info),
             "gen_s": GEN["s"], "gen_tokens": GEN["tokens"], "gen_rollouts": GEN["rollouts"]})
        GEN.update(s=0.0, tokens=0, rollouts=0)

    def on_val_loss_report(self, info: dict):
        log({"event": "val", **nums(info)})


_run = tr.run
tr.run = lambda args, training_callback=None: _run(args, Metrics())

if __name__ == "__main__":
    log({"event": "start", "argv": sys.argv[1:]})
    tr.main()
    log({"event": "done"})
