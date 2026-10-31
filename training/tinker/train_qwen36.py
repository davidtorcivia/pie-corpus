"""Qwen3.6-35B-A3B LoRA on Tinker (tinker 0.36.0 / tinker-cookbook 0.5.9, in Q:\\AI\\PIE\\tinker\\.venv on tr-desktop).

    Q:\\AI\\PIE\\tinker\\.venv\\Scripts\\python.exe -u Q:\\AI\\PIE\\tinker\\train_qwen36.py

Data: train_mix_1102.jsonl (export e2b6d78), the set queue 6 trains the 4B on.
- Renderer qwen3_5_disable_thinking: the generation prompt pre-fills an empty <think></think>, as the demo will
  sample. The qwen3_5 renderer would open a real <think> at generation that training never shows.
- One example per assistant turn (the conversation up to it, LAST_ASSISTANT_MESSAGE). Qwen3.5's template strips
  <think> from earlier assistant turns, so the renderer lacks the extension property, and training every assistant
  turn of one rendering would show earlier turns a prefix generation never builds. 42,751 conversations become
  53,454 examples, 10.5 M tokens per epoch (8.95 M as conversations).
- reduction="none": token-sum loss, every trained token weighted alike, as train_lora.py's token-mean over a batch.
  The cookbook default ("mean") would weigh a one-token inflect answer like a whole dialogue reply.
Recipe: the 4B's (LoRA rank 16, lr 2e-4 cosine), 3 epochs, a checkpoint at the end of each epoch; about 14 k
tokens per step like the 4B's (batch 64 examples, 835 steps per epoch). Scored afterwards on the frozen prompts
(sample_qwen36.py).
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

MODEL_NAME = "Qwen/Qwen3.6-35B-A3B"
RENDERER = "qwen3_5_disable_thinking"
TRAIN = r"Q:\AI\PIE\data\train_mix_1102.jsonl"
RUN = "qwen36-35b-a3b-r16-lr2e-4-export1102"
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
    learning_rate=2e-4,
    lr_schedule="cosine",
    num_epochs=EPOCHS,
    lora_rank=16,
    save_every=STEPS_PER_EPOCH,
    eval_every=0,
    ttl_seconds=14 * 86400,     # the epoch checkpoints outlive the scoring (default 7 days); the final one is kept
)

if __name__ == "__main__":
    asyncio.run(train.main(config))
