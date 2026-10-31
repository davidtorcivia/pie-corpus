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
  (that version has no `<think>` blocks). TypewriterLM SFT: its own template, `<|begin_of_text|>` then
  `<|im_start|>role content<|im_end|> `. Base models: `plain` (`System: … / User: … / Assistant: …`, each reply ended
  by the model's own end-of-text token); see lesson 8 for why base models can't use ChatML.
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
8. **Base models need a format whose stop token they already know.** Under LoRA the embeddings stay frozen, and a
   base model's `<|im_start|>`/`<|im_end|>` embeddings were never trained: Qwen3-4B-Base under ChatML never emitted
   `<|im_end|>`, ran past every answer into junk and invented new user turns (inflection exact match 0%). Fix: the
   `plain` template, replies ended by `<|endoftext|>` / `<|end_of_text|>`. (Alternative: train the embedding and
   LM-head rows for those tokens.)
9. **Two epochs.** Eval loss bottoms at epoch 2 on both Qwen runs and rises at 3 while train loss keeps falling
   (instruct 0.28): ~1.1 M trained tokens per epoch is memorized fast, and the drills restate the same forms.
7. A 30-step smoke test (eval loss 3.13 → 1.53, chrF 19, 22% recognized words) before any long run caught the slow
   generation; short PIE replies were already sensible, longer outputs looped.

## Queue 1 (2026-10-30): base vs instruct vs pre-modern

| run | model | lr | epochs | status |
|---|---|---|---|---|
| qwen4b-instruct-r16-lr2e-4 | Qwen3-4B-Instruct-2507 | 2e-4 | 3 | done, 38 min |
| qwen4b-base-r16-lr2e-4 | Qwen3-4B-Base | 2e-4 | 3 | done, 41 min (ChatML: invalid, lesson 8) |
| typewriter-sft-r16-lr1e-4 | TypewriterLM 1913 SFT | 1e-4 | 3 | running |
| typewriter-base-r16-lr1e-4 | TypewriterLM 1913 base | 1e-4 | 3 | skipped: rerun on `plain` in queue 2 |

Questions it answers: how many epochs (the per-epoch eval decides; the grammar drills repeat material across task
formats, so overfitting may come early); instruct vs base; a modern model vs one that never saw the modern world.
Results follow below as each epoch is scored.

**Results** (scores: Mac scorer on 8 eval prompts per kind, ~110 prompts; chrF overall; recognized = share of output
PIE words that are engine forms):

| run | eval loss e0 → e1 → e2 → e3 | chrF e1 / e2 / e3 | recognized e3 | inflect exact e1 / e2 / e3 | modern |
|---|---|---|---|---|---|
| qwen4b-instruct | 3.13 → 1.20 → **1.198** → 1.25 | 32 / 38.5 / 39.1 | 70% | 38 / 50 / 50%* | 0 |
| qwen4b-base (ChatML) | 2.34 → 1.40 → 1.41 → 1.49 | 22 / 24 / 25 | 73% | 0 / 0 / 0% | 0 |

\* inflect over 8 prompts; overall exact (inflect + cognates) 19% at e2.

Reading the instruct outputs (epoch 2): short, mostly well-formed PIE replies in character ("Sister, is the fire
burning?" → *h₁íd dʰégʷʰeti*; "Eat in my house, and drink there!" → *gʷm̥dʰí h₁ddʰí-kʷe*; "Put your trust in him!"
→ *h₁ésmey bʰebʰóydʰe*, right frame, another verb); *steh₂weróysu* exact. Meaning is often a near-miss, longer
translations drift, cognate reconstruction is weak (chrF 7–22). The base model's PIE words are as real (73%
recognized) but every reply runs on (lesson 8), so its scores say nothing about the base model itself.

## Queue 2 (2026-10-30): fair base runs, two instruct variants, 2 epochs each

| run | model | template | lr | rank | question |
|---|---|---|---|---|---|
| typewriter-base-plain-r16-lr1e-4 | TypewriterLM 1913 base | plain | 1e-4 | 16 | pre-modern base |
| qwen4b-base-plain-r16-lr2e-4 | Qwen3-4B-Base | plain | 2e-4 | 16 | base vs instruct, fairly |
| qwen4b-instruct-r16-lr1e-4 | Qwen3-4B-Instruct-2507 | chatml | 1e-4 | 16 | gentler lr: epoch-2 quality, less memorizing? |
| qwen4b-instruct-r32-lr2e-4 | Qwen3-4B-Instruct-2507 | chatml | 2e-4 | 32 | more capacity for translation? |
