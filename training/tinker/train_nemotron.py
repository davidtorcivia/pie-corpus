"""Nemotron 3.5 Super (VL, 120B-A12B) LoRA on Tinker (tinker 0.36.0 / tinker-cookbook 0.5.9, in
Q:\\AI\\PIE\\tinker\\.venv on tr-desktop). The demo model.

    Q:\\AI\\PIE\\tinker\\.venv\\Scripts\\python.exe -u Q:\\AI\\PIE\\tinker\\train_nemotron.py

Settings come from the environment, so the LR sweep and the full run share one script:
    PIE_OPT        dimuon (default) | adamw
    PIE_LR         peak learning rate (default 2e-3, Dimuon)
    PIE_RANK       LoRA rank (default 16)
    PIE_MAX_STEPS  stop after N steps (sweep probes); the schedule still spans 3 epochs, so a probe sees the same LR
                   as the full run's first N steps
    PIE_RUN        run name (default from the settings)

Data: train_mix_1103.jsonl (export 5b754f0: the 35B's set plus Tier 1 as training data), measured with
measure_nemotron.py: 42,932 conversations become 53,635 per-turn examples, 10.80 M tokens per epoch (longest 1,222).
Held-out: eval_1103.jsonl (export/chat/eval.jsonl, 713 conversations), scored as test NLL and bits per byte every
EVAL_EVERY steps. That is a forward (prefill) pass on a sampler snapshot, not generation: about 0.15 M tokens at the
prefill price per evaluation. Generation is scored locally, never on Tinker.
- Renderer nemotron3_ultra_disable_thinking (the cookbook's for 3.5 Super with reasoning off): the demo samples with
  thinking off. It lacks the extension property, so one example per assistant turn (LAST_ASSISTANT_MESSAGE), as the
  35B run did.
- reduction="none": token-sum loss, every trained token weighted alike (as the 35B run).
- Dimuon (TML's LoRA optimizer, tinker-docs /tinker/optimizers): cookbook 0.5.9 builds tinker.AdamParams for every
  step, so the optimizer is patched in as in the owner's TRON35 run (B:\\Dropbox\\Dropbox\\AI\\TRON35). The docs: LR
  10-100x AdamW's (about 15x best in SFT), beta1 0.9, no clipping, benefits from rank more than AdamW. The cookbook
  resumes with create_training_client_from_state_with_optimizer, which keeps Dimuon's state.
Recipe otherwise the 35B's: cosine over 3 epochs, batch 64 (about 12.9 k tokens per step), 838 steps per epoch, a
checkpoint at each epoch end. Cost at $1.276 per M training tokens: 3 x 10.80 M = 32.4 M tokens, about $41.
"""
import asyncio
import functools
import json
import os

import chz
import datasets
import tinker

os.environ["TINKER_API_KEY"] = open(r"B:\Dropbox\Dropbox\AI BRAIN\tinker.txt").read().strip()

from tinker_cookbook.renderers import TrainOnWhat
from tinker_cookbook.supervised import train
from tinker_cookbook.supervised.data import SupervisedDatasetFromHFDataset, conversation_to_datum
from tinker_cookbook.supervised.types import ChatDatasetBuilder, ChatDatasetBuilderCommonConfig, SupervisedDataset

MODEL_NAME = "nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16"
RENDERER = "nemotron3_ultra_disable_thinking"
TRAIN = r"Q:\AI\PIE\data\train_mix_1103.jsonl"
EVAL = r"Q:\AI\PIE\data\eval_1103.jsonl"
BATCH = 64
EPOCHS = 3
EVAL_EVERY = 50

OPT = os.environ.get("PIE_OPT", "dimuon")
LR = float(os.environ.get("PIE_LR", "2e-3" if OPT == "dimuon" else "2e-4"))
RANK = int(os.environ.get("PIE_RANK", "16"))
MAX_STEPS = int(os.environ["PIE_MAX_STEPS"]) if os.environ.get("PIE_MAX_STEPS") else None
RUN = os.environ.get("PIE_RUN", f"nemotron35-super-{OPT}-r{RANK}-lr{LR:g}-export1103" + (f"-probe{MAX_STEPS}" if MAX_STEPS else ""))
LOG_PATH = rf"Q:\AI\PIE\tinker\runs\{RUN}"

if OPT == "dimuon":
    tinker.AdamParams = lambda learning_rate, **_: tinker.types.DimuonParams(learning_rate=learning_rate)
    _create = tinker.ServiceClient.create_lora_training_client_async
    tinker.ServiceClient.create_lora_training_client_async = functools.partialmethod(
        _create, optimizer=tinker.types.DimuonOptimizerConfig())
elif OPT != "adamw":
    raise SystemExit(f"PIE_OPT must be dimuon or adamw, not {OPT}")


def turn_examples(path: str) -> list[dict]:
    """Each conversation split into one example per assistant turn: the messages up to and including it."""
    out = []
    for line in open(path, encoding="utf-8"):
        msgs = json.loads(line)["messages"]
        out += [{"messages": msgs[:i + 1]} for i, m in enumerate(msgs) if m["role"] == "assistant"]
    return out


@chz.chz
class PieDatasetBuilder(ChatDatasetBuilder):
    def __call__(self) -> tuple[SupervisedDataset, SupervisedDataset | None]:
        renderer, max_length = self.renderer, self.common_config.max_length

        def to_datum(ex):
            return conversation_to_datum(ex["messages"], renderer, max_length=max_length,
                                         train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE, reduction="none")

        def ds(path):
            return SupervisedDatasetFromHFDataset(datasets.Dataset.from_list(turn_examples(path)),
                                                  batch_size=self.common_config.batch_size, map_fn=to_datum)

        return ds(TRAIN), ds(EVAL)


dataset_builder = PieDatasetBuilder(
    common_config=ChatDatasetBuilderCommonConfig(
        model_name_for_tokenizer=MODEL_NAME, renderer_name=RENDERER, max_length=4096, batch_size=BATCH))

STEPS_PER_EPOCH = len(turn_examples(TRAIN)) // BATCH

config = train.Config(
    log_path=LOG_PATH,
    model_name=MODEL_NAME,
    recipe_name=RUN,
    renderer_name=RENDERER,
    dataset_builder=dataset_builder,
    learning_rate=LR,
    lr_schedule="cosine",
    num_epochs=EPOCHS,
    lora_rank=RANK,
    max_steps=MAX_STEPS,
    save_every=STEPS_PER_EPOCH,
    eval_every=EVAL_EVERY,
    infrequent_eval_every=0,
    ttl_seconds=14 * 86400,     # the epoch checkpoints outlive the scoring (default 7 days); the final one is kept
)

if __name__ == "__main__":
    print(f"PIE run {RUN}: optimizer {OPT}, lr {LR:g}, rank {RANK}, max_steps {MAX_STEPS}, {STEPS_PER_EPOCH} steps/epoch",
          flush=True)
    asyncio.run(train.main(config))
