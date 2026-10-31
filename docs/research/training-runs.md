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
7. A 30-step smoke test (eval loss 3.13 → 1.53, chrF 19, 22% recognized words) before any long run caught the slow
   generation; short PIE replies were already sensible, longer outputs looped.
8. **Base models need a format whose stop token they already know.** Under LoRA the embeddings stay frozen, and a
   base model's `<|im_start|>`/`<|im_end|>` embeddings were never trained: Qwen3-4B-Base under ChatML never emitted
   `<|im_end|>`, ran past every answer into junk and invented new user turns (inflection exact match 0%). Fix: the
   `plain` template, replies ended by `<|endoftext|>` / `<|end_of_text|>`. (Alternative: train the embedding and
   LM-head rows for those tokens.)
9. **Two epochs.** Eval loss bottoms at epoch 2 on both Qwen runs and rises at 3 while train loss keeps falling
   (instruct 0.28): ~1.1 M trained tokens per epoch is memorized fast, and the drills restate the same forms.

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

**Results so far** (2026-10-30 22:55; chrF overall, scorer as above):

| run | eval loss e0 → e1 → e2 (→ e3) | chrF e1 / e2 (/ e3) | recognized | exact |
|---|---|---|---|---|
| typewriter-sft (queue 1, 3 ep) | 3.23 → **1.10** → 1.13 → 1.19 | 24.7 / 27.4 / 28.6 | 74–76% | 0–6% |
| typewriter-base-plain | 4.08 → 1.13 → 1.18 | 22.5 / 22.8 | 63–70% | 0% |
| qwen4b-base-plain | 2.25 → 1.21 → 1.23 | 33.4 / 33.9 | 63–67% | 0% |
| qwen4b-instruct-lr1e-4 | 3.13 → 1.23 → 1.24 | 31.9 / … | 66% | 12% |

- **Eval loss is not comparable across tokenizers** (TypewriterLM's 32 k Llama vocabulary splits PIE into ~35% more
  tokens, so its per-token loss is lower for the same text). Compare chrF and the read outputs.
- **Plain format rescued the base model**: Qwen3-4B-Base chrF 25 → 34, eval loss 1.40 → 1.21, replies stop. Still
  behind instruct (39): the instruct tuning helps follow the many task formats.
- **TypewriterLM trails** both Qwens (27–29) and wraps short answers in extra PIE (dialogue chrF 15–16); its pre-modern
  prior buys nothing visible at this data size. Eval loss bottoms at epoch 1 for it.
- **Every model regularizes paradigms**: *kólHō* (an n-stem) declined as a thematic o-stem by both base Qwen and
  TypewriterLM. The models learn the common patterns, not each lemma's stem class; more drills per lemma, or a
  lemma-class cue in the prompt, would target this.
- ~~Cognate reconstruction stays weak everywhere~~ **Correction:** `cognates_to_pie` is never in the training mix
  (TARGET_MIX 0%: a speaker doesn't know the daughter languages), so the eval measured an untrained task. The
  scorer now reports it under "untrained", outside the summary.


## Corpus build-out (2026-10-30, owner: "include ALL the grammar drills … get back to the percentages")

Diagnosis of queue 1–2:
- The mix was sized by conversation (all 2,663 examples = 20%), so it used only 44% of the grammar drills (3,994 of
  9,170) and 46% of the translations, picked by hash: the drills a model saw were proportional to the lexicon's
  1,120-thematic-noun skew.
- The regularized paradigms (*kólHō*, *h₂óḱris*) are eval hold-out lexemes (5% of lexemes keep their drills in eval),
  so the test is inferring a class from the lemma; exposure to each ablauting class decides it.

Changes:
1. **Every grammar drill in the mix.** `select_mix` keeps the grammar group whole (`MIX_ANCHOR`), which sets the size;
   conversation and translation fill up to 20% / 50% as the corpus grows. Export of 2026-10-30 23:40: 26,874
   examples, 4.5 M Qwen tokens: conversation 2,663 (9.9%), translation 14,369 (53.5%, all of it), grammar 9,842
   (36.6%).
2. **Stem-class drills.** Every ablauting lexeme (1,569 usable, spec with a weak stem) also gets its key cell (noun
   GEN.SG, adjective M.GEN.SG, verb indicative 3PL) and a weak-stem cell when its 3 random cells lack them; the random
   cells are drawn exactly as before. Inflection drills 4,863 → 5,560.
3. **Measurement.** A frozen prompt set, `training/gen_prompts_v1.jsonl` (246 prompts from the current eval: inflect
   48, paradigm 40, translations 72, dialogue 64, gloss 12, continuation 10; with each prompt's lexeme id), used by
   `train_lora.py --gen-file` and `gen_eval.py`, so later exports are compared on the same prompts. The scorer adds
   paradigm per-cell exact and inflect / paradigm scores by stem class (spec rule, ablauting or not). Baseline:
   every queue 1–2 adapter re-generated on it (`baseline_v1.ps1`).
4. **Conversation.** A dialogue record with speakers gives 2.7 conversation, 5.1 translation and 1.0 grammar (gloss)
   examples, so 20% conversation needs about 1,850 more such records (~46 batches of 40). Wave 3a: in-world dialogue
   batches t044, t045, t050, t053, t056, t059 (greeting, bargaining, travel, family, council, teaching), each asked
   for longer exchanges (8–14 clauses, 4–8 turns) and a spread of athematic nouns in oblique cases.

## Queue 2 final and the frozen-prompt baseline (2026-10-30 23:45)

Per-epoch samples (old 8-per-kind set): instruct lr1e-4 chrF 31.9 → 34.2; instruct r32 37.6 → 39.8. Then every
adapter on the frozen set `gen_prompts_v1.jsonl` (246 prompts, no cognates; `baseline_v1.ps1`, scores
`scores-v1eN.json`):

| adapter | chrF | recognized | inflect exact | paradigm cells | dialogue chrF | EN→PIE chrF (task / app) | inflect abl / non | paradigm abl / non |
|---|---|---|---|---|---|---|---|---|
| **qwen4b-instruct r16 lr2e-4 e2** | **45.2** | **74%** | 35% | **30%** | **23.0** | **37.4** / 44.6 | **33%** / 37% | **26%** / 32% |
| qwen4b-instruct r32 lr2e-4 e2 | 45.4 | 73% | **40%** | 25% | 22.7 | 36.5 / **45.6** | 22% / **50%** | 17% / 29% |
| qwen4b-instruct r16 lr1e-4 e2 | 40.4 | 63% | 19% | 22% | 20.0 | 32.6 / 42.2 | 6% / 27% | 12% / 27% |
| qwen4b-base-plain r16 lr2e-4 e1 | 36.9 | 58% | 6% | 18% | 19.9 | 27.7 / 37.6 | 11% / 3% | 12% / 20% |
| typewriter-sft r16 lr1e-4 e1 | 26.2 | 66% | 0% | 7% | 21.1 | 16.0 / 18.1 | 0% / 0% | 4% / 8% |

(inflect n = 48: 18 ablauting, 30 not; paradigm n = 40.)

- **Recipe: Qwen3-4B-Instruct, LoRA r16/α32, lr 2e-4, 2 epochs.** Rank 32 ties on chrF; its edge on regular
  inflection is offset by worse ablauting forms and paradigms (more capacity memorized the frequent pattern
  harder). lr 1e-4 underfits in 2 epochs.
- **The stem-class gap is real and measurable now:** every model is worse on ablauting lexemes' paradigms than on
  thematic ones (26% vs 32% for the best). This is the baseline for the stem-class drills of the build-out.
- **TypewriterLM is out** of the comparison (no licence to ship, and last on every task but dialogue).

## Queue 3 (2026-10-31): the recipe on the built-out export

Export of 2026-10-31 (commit 88d96ad): every grammar drill, the stem-class drills, and 18 new batches (t044–t088:
14 in-world dialogue batches and the 4-batch Horrors wave, 720 texts, each through a calibrated review). Mix: 32,820
examples, 5.9 M Qwen tokens: conversation 4,524 (13.8%), translation 17,685 (53.9%), grammar 10,611 (32.3%). Run
`qwen4b-instruct-r16-lr2e-4-export1031`: Qwen3-4B-Instruct, LoRA r16/α32, lr 2e-4, 2 epochs, generations on the
frozen `gen_prompts_v1.jsonl`, compared with baseline_v1 (above). Note: the eval loss is on the new eval split
(it grew with the stem-class drills), so it is not comparable with queue 1–2's; the frozen prompts are.
Provenance: the run trained on `train_mix_1031.jsonl` (88d96ad; 422 steps/epoch), but its config.json says
`export_provenance.commit` b7f351e, because train_lora.py read the one shared `provenance.json` in Q:\AI\PIE\data
(queue 1–2's export, e30f146 built from b7f351e plus t041). Fixed afterwards: train_lora.py prefers
`<train stem>.provenance.json` and records `train_sha256`.

The corpus process, for the write-up: each batch is written by a planner agent as plans (never PIE), realized by
the engine, gated (reject rate, exact forms, lexeme caps, meter), then reviewed blind by a calibrated reviewer agent
on 20 sampled items with 5 planted errors (≥4/5 recall required, else a second reviewer with fresh plants: t073,
t087), plus a full read of all 40 records; fixes go into the plans and are re-realized; the lead approves by binding
the records' hashes. Wave 3: 18 batches, 2 second reviews; errors found per batch 0–5, almost all agreement
(gender of pronouns and predicate adjectives), number (dual/plural) and verb sense (causatives); engine gaps found
by reviewers were fixed at the source (question marks of multi-clause questions, 'two' in an oblique case,
predicate-adjective gender warning, the reflexive exempt from the lexeme cap).

**Result** (62 min; frozen prompts, same scorer; baseline = queue 1's recipe run, epoch 2):

| | chrF | recognized | inflect exact | paradigm cells | dialogue chrF | EN→PIE (task / app) | inflect abl / non | paradigm abl / non |
|---|---|---|---|---|---|---|---|---|
| baseline (export 10-30) | 45.2 | 74% | 35% | 30% | 23.0 | 37.4 / 44.6 | 33% / 37% | 26% / 32% |
| export 10-31, e1 | 44.6 | 70% | 33% | 28% | 22.0 | 33.7 / 45.1 | 17% / 43% | 23% / 31% |
| **export 10-31, e2** | **47.0** | **76%** | **44%** | **39%** | 22.6 | 35.8 / **50.2** | 28% / **53%** | 25% / **46%** |

Eval loss 3.16 → 1.14 → 1.20 (new eval split; lowest at epoch 1, but every generation score is better at epoch 2:
keep epoch 2).

- **All the grammar drills in the mix pays off on the regular classes:** inflection exact 37% → 53%, paradigm cells
  32% → 46% for non-ablauting lexemes (the mix's grammar drills went from 3,994 to 10,611).
- **The stem-class drills did not close the ablauting gap; it widened** (inflection 33% → 28%, 6 → 5 of 18 prompts;
  paradigm cells 26% → 25%). A held-out ablauting lexeme must be inferred from its lemma; two extra cells per
  training lexeme did not teach that. Next: paradigm drills (whole declensions) for more ablauting lexemes, and a
  larger ablauting sample in the frozen prompts (18 inflection prompts is too few to move).
- **Translation into PIE (app form) +5.6 chrF**; dialogue flat (22.6 vs 23.0): conversation is still 13.8% of the mix.
