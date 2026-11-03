"""Nemotron 3.5 Super (VL, 120B-A12B) LoRA on Tinker (tinker 0.36.0 / tinker-cookbook 0.5.9, in
Q:\\AI\\PIE\\tinker\\.venv on tr-desktop). The demo model.

    Q:\\AI\\PIE\\tinker\\.venv\\Scripts\\python.exe -u Q:\\AI\\PIE\\tinker\\train_nemotron.py

Data: train_mix_1103.jsonl (export 5b754f0: the 35B's set plus Tier 1 as training data), measured with
measure_nemotron.py: 42,932 conversations become 53,635 per-turn examples, 10.80 M tokens per epoch (longest 1,222).
- Renderer nemotron3_ultra_disable_thinking (the cookbook's for 3.5 Super with reasoning off): the demo samples with
  thinking off. It lacks the extension property, so one example per assistant turn (LAST_ASSISTANT_MESSAGE), as the
  35B run did.
- reduction="none": token-sum loss, every trained token weighted alike (as the 35B run).
Recipe: the 35B's (LoRA rank 16, cosine, 3 epochs, batch 64 = about 12.9 k tokens per step, 838 steps per epoch, a
checkpoint at each epoch end), except the learning rate. The cookbook has no calibrated LR for Nemotron; the 35B ran
at 0.4x its recommendation (2e-4 of 5e-4). At hidden size 4096 the cookbook's Qwen formula gives 4.7e-4 and its Llama
formula 2.9e-4; 0.4x of those is 1.9e-4 and 1.1e-4. LR 1.5e-4 sits between.
Cost at $1.276 per M training tokens: 3 x 10.80 M = 32.4 M tokens, about $41. Never sample on Tinker: download the
epoch adapters and score them locally.
"""
import asyncio
import json
import os

import chz
import datasets

from tinker_cookbook.renderers import TrainOnWhat
from tinker_cookbook.supervised import train
from tinker_cookbook.supervised.data import SupervisedDatasetFromHFDataset, conversation_to_datum
from tinker_cookbook.supervised.types import ChatDatasetBuilder, ChatDatasetBuilderCommonConfig, SupervisedDataset

os.environ["TINKER_API_KEY"] = open(r"B:\Dropbox\Dropbox\AI BRAIN\tinker.txt").read().strip()

MODEL_NAME = "nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16"
RENDERER = "nemotron3_ultra_disable_thinking"
TRAIN = r"Q:\AI\PIE\data\train_mix_1103.jsonl"
RUN = "nemotron35-super-r16-lr1.5e-4-export1103"
LOG_PATH = rf"Q:\AI\PIE\tinker\runs\{RUN}"
BATCH = 64
EPOCHS = 3


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
        ds = datasets.Dataset.from_list(turn_examples(TRAIN))
        renderer, max_length = self.renderer, self.common_config.max_length

        def to_datum(ex):
            return conversation_to_datum(ex["messages"], renderer, max_length=max_length,
                                         train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE, reduction="none")

        return SupervisedDatasetFromHFDataset(ds, batch_size=self.common_config.batch_size, map_fn=to_datum), None


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
    learning_rate=1.5e-4,
    lr_schedule="cosine",
    num_epochs=EPOCHS,
    lora_rank=16,
    save_every=STEPS_PER_EPOCH,
    eval_every=0,
    ttl_seconds=14 * 86400,     # the epoch checkpoints outlive the scoring (default 7 days); the final one is kept
)

if __name__ == "__main__":
    asyncio.run(train.main(config))
