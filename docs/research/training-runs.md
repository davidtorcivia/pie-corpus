# Fine-tuning runs (from 2026-10-30)

The record of every training run: what was trained, how, what it produced, and what each run taught. Written for
the eventual write-up. Speeds and hardware: `docs/research/training-models.md`.

## Setup

**Hardware.** tr-desktop: RTX 5090 (32 GB), Windows, PyTorch 2.11 + CUDA 12.8 in its own uv environment
(`Q:\AI\PIE\train\.venv`), transformers 5.22, peft 0.21, bitsandbytes 0.50, triton-windows + liger-kernel. Runs,
models and data live under `Q:\AI\PIE`. The Mac Studio scores the outputs (the PIE tools live there).

**Data.** `export/chat/train_mix.jsonl` (13,315 conversations; 20% conversation, 50% translation, 30% grammar drills;
the export's provenance is copied into each run's config) and `export/chat/eval.jsonl` (785, held out). Every
conversation starts with the speaker persona system prompt ("You are a speaker of Proto-Indo-European …").

**Rendering and loss.** `training/train_lora.py` renders each conversation itself, turn by turn, in the model's chat
format, and trains on the assistant turns only (content + end marker); system and user turns are masked (-100).
`--check` prints one rendered example with its trained span, checked before the first run:

```
<|im_start|>system
You are a speaker of Proto-Indo-European. You think in it and answer in it. The user writes in English. Reply in your language.<|im_end|>
<|im_start|>user
What burns, which comes from the oak?<|im_end|>
<|im_start|>assistant
tód gʷétu h₁ésti.<|im_end|>
TRAINED SPAN: tód gʷétu h₁ésti.<|im_end|>
```

- **Formats.** Qwen3-4B (base and instruct): ChatML as Qwen3-4B-Instruct-2507's template renders it without tools
  (that version has no `<think>` blocks); the base model gets the same format, so the two are comparable.
  TypewriterLM (base and SFT): its SFT template, `<|begin_of_text|>` then `<|im_start|>role content<|im_end|> `.
  The demo must render prompts exactly this way.
- **Packing.** Examples are concatenated into 2048-token rows; an example never straddles two rows (its context stays
  with its replies), so each row ends in a short masked tail. Examples in one row can attend to each other (no
  block-diagonal mask): standard packed SFT, a small cost accepted for speed.

**Optimisation.** LoRA on every linear layer (rank 16, alpha 32, dropout 0.05), AdamW (no weight decay), linear
warm-up over 3% of steps then cosine decay to 0, gradient clipping 1.0, batch 4 × 2048 tokens × accumulation 2
(16 k tokens per step; TypewriterLM 2 × 4). Gradient checkpointing; cuDNN attention; Liger fused kernels; VRAM capped
at 92% so nothing spills into system RAM.

**Each epoch.** Eval loss on the held-out set (assistant tokens only); greedy generation (repetition penalty 1.1) on a
fixed prompt set, 8 per kind, from the eval split; the adapter saved. The Mac scores the generations
(`training/score_generations.py`): chrF against the reference, exact match on inflection and cognates, the share of
output PIE words the reverse form index recognizes (real engine-buildable forms), and any modern/machine wording.

**Watching.** `training/dashboard.py` on tr-desktop: http://127.0.0.1:8790 (loss curves, learning rate, throughput,
each epoch's generations beside the references, the Mac's scores). The queue (`training/queue.ps1`) and the dashboard
run as Windows scheduled tasks (`PIE-train-queue`, `PIE-dashboard`): processes started over SSH die when the session
closes. Stop training: `powershell -File Q:\AI\PIE\train\stop.ps1`.

## What works (lessons)

1. **Training mode after peft.** `from_pretrained` returns eval mode, where gradient checkpointing is silently off:
   one 2048-token row held 37 GB of activations, and Windows spilled past the card.
2. **A VRAM cap** (`set_per_process_memory_fraction(0.92)`) turns a spill into a clean OOM.
3. **cuDNN attention** on Windows/Blackwell: no flash or memory-efficient SDPA kernel ships for the 5090; the math
   fallback is 6× slower with 10× the memory.
4. **Liger fused linear cross-entropy**: never materializes the 152 k-vocab logits (9.3 GB at batch 8).
5. **Detached runs on Windows** need Task Scheduler, not Start-Process over SSH.
6. **Batched, left-padded generation** for the per-epoch samples: one prompt at a time took ~30 min per epoch.
7. A 30-step smoke test (eval loss 3.13 → 1.53, chrF 19, 22% recognized words) before any long run caught the slow
   generation; short PIE replies were already sensible, longer outputs looped.

## Queue 1 (2026-10-30): base vs instruct vs pre-modern

| run | model | lr | epochs | status |
|---|---|---|---|---|
| qwen4b-instruct-r16-lr2e-4 | Qwen3-4B-Instruct-2507 | 2e-4 | 3 | running |
| qwen4b-base-r16-lr2e-4 | Qwen3-4B-Base | 2e-4 | 3 | queued |
| typewriter-sft-r16-lr1e-4 | TypewriterLM 1913 SFT | 1e-4 | 3 | queued |
| typewriter-base-r16-lr1e-4 | TypewriterLM 1913 base | 1e-4 | 3 | queued |

Questions it answers: how many epochs (the per-epoch eval decides; the grammar drills repeat material across task
formats, so overfitting may come early); instruct vs base; a modern model vs one that never saw the modern world.
Results follow below as each epoch is scored.
