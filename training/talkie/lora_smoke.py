"""MLX LoRA smoke test for talkie-1930-13b-it.

Runs rank-8 LoRA on all seven projections of every layer, using N chat
examples rendered with the model's chat template. The examples are packed
into 1024-token rows and the loss covers assistant tokens only. All packed
rows go in one batch, which is trained for S steps.

  python -I lora_smoke.py <it_safetensors_dir> <train_mix.jsonl> [N=32] [S=10]
"""

import json
import os
import sys
import time

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten
from mlx_lm.tuner.lora import LoRALinear
from transformers import PreTrainedTokenizerFast

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mlx_talkie  # noqa: E402

d, data = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 32
STEPS = int(sys.argv[4]) if len(sys.argv) > 4 else 10
SEQ, RANK, LR = 1024, 8, 2e-4
TARGETS = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")

tok = PreTrainedTokenizerFast.from_pretrained(d)
model = mlx_talkie.load_talkie(d)
model.freeze()
for blk in model.layers:
    for parent in (blk.attn, blk.mlp):
        for name in TARGETS:
            if hasattr(parent, name):
                setattr(parent, name, LoRALinear.from_base(getattr(parent, name), r=RANK, scale=2.0))
n_train = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
print(f"trainable LoRA params: {n_train:,}", flush=True)

# render, tokenize, mask (assistant content + <|end|> only), pack
ids, mask = [], []
with open(data) as f:
    for line, _ in zip(f, range(N)):
        msgs = json.loads(line)["messages"]
        prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True)
        full = tok.apply_chat_template(msgs, tokenize=False)
        assert full.startswith(prompt)
        p = tok(prompt, add_special_tokens=False)["input_ids"]
        a = tok(full[len(prompt):], add_special_tokens=False)["input_ids"]
        ids += p + a + [tok.convert_tokens_to_ids("<|endoftext|>")]
        mask += [0] * len(p) + [1] * len(a) + [0]
rows = max(1, len(ids) // (SEQ + 1))
pad = rows * (SEQ + 1) - len(ids)
if pad > 0:
    ids, mask = ids + [0] * pad, mask + [0] * pad
ids = np.array(ids[: rows * (SEQ + 1)]).reshape(rows, SEQ + 1)
mask = np.array(mask[: rows * (SEQ + 1)]).reshape(rows, SEQ + 1)
x, y, m = mx.array(ids[:, :-1]), mx.array(ids[:, 1:]), mx.array(mask[:, 1:], dtype=mx.float32)
print(f"{N} examples -> {len(ids.flatten())} tokens packed into batch {rows} x {SEQ}; supervised tokens {int(mask.sum())}", flush=True)


def loss_fn(model, x, y, m):
    logits = model(x)
    ce = nn.losses.cross_entropy(logits, y, reduction="none")
    return (ce * m).sum() / m.sum()


opt = optim.Adam(learning_rate=LR)
step = nn.value_and_grad(model, loss_fn)
times = []
for s in range(STEPS):
    t0 = time.time()
    loss, grads = step(model, x, y, m)
    opt.update(model, grads)
    mx.eval(loss, model.trainable_parameters(), opt.state)
    dt = time.time() - t0
    times.append(dt)
    print(f"step {s + 1:2d}  loss {loss.item():.4f}  {dt:.1f}s  {rows * SEQ / dt:.0f} tok/s  peak mem {mx.get_peak_memory() / 1e9:.1f} GB", flush=True)
steady = times[1:] or times
print(f"steady-state: {rows * SEQ * len(steady) / sum(steady):.0f} tokens/s (batch {rows} x {SEQ}, steps 2-{STEPS})")
