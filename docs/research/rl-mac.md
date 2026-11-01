# RL on the Mac (2026-11-01)

After the Qwen3.6-35B-A3B fine-tune (docs/research/training-runs.md), the plan is to stop fine-tuning and correct the
model's errors with RL, on the Mac's M3 Ultra (256 GB), with a local reward and a Claude judge only where the engine
cannot decide (owner, 2026-10-31 and 2026-11-01). Stage 1, tonight: engine-checkable drills only, no judge.

## Where to run it

A research pass (2026-11-01, official pricing pages) on the workload of 300–500 GRPO steps at 256 rollouts per step
(about 50–65 M sampled tokens):

| Option | Est. total | Notes |
|---|---|---|
| Mac (M3 Ultra, mlx-lm-lora) | $0 | ~70 s per 64-rollout step; a 256-rollout run would take 22–37 h |
| Tinker | $135–200 | $1.335 / M sampled, $1.177 / M trained, $0.45 / M prefill (64K tier) |
| Self-hosted, 2x H200 (RunPod, Prime Intellect, Modal) | $60–190 compute, $150–400 with debugging | vLLM LoRA on the fused MoE is fragile for qwen3_5_moe |
| Together Post-Training | ~$500–900 | the one managed service documenting Qwen3.6-35B-A3B + LoRA + own rewards; 8x B200 example |
| Prime Intellect hosted RL | $300–800+ (unverified) | LoRA retired; full-parameter only |
| Fireworks | n/a | managed RFT deprecated |

The Mac wins: free, overnight, and no inference billing. Tinker stays the fallback.

## Speed (mlx-lm-lora 5.10.2, e3 at oQ5e, 3-step benchmarks)

| Setup | Generation | Step | Memory |
|---|---|---|---|
| Library default (decodes `--batch-size` sequences at once) | 30 s / 32 rollouts | ~46 s | 63 GB |
| All 32 rollouts decoding together | 15 s | ~36 s | 63 GB |
| 64 rollouts (8 prompts x 8), all at once, no gradient checkpointing | 24 s | ~67 s | 136 GB |

- Decode concurrency is the one large win: generate_grpo caps the BatchGenerator at `--batch-size`, so a group of 8
  rollouts per prompt decodes 4 or 8 at a time. training/rl/grpo.py lifts the cap.
- The update (policy and reference forward, backward) is the rest of the step, about 40 s for 64 rollouts. A smaller
  LoRA does not shorten it: the cost is the passes through the frozen 35B, not the adapter.
- The first run without gradient checkpointing was killed at step 7, with no traceback, when a 4-prompt eval loaded
  a second copy of the model beside it. Runs keep gradient checkpointing on (about 65 GB), so omlx or an eval can
  run alongside.

## Stage 1: engine drills (rl1-engine-drills-e3)

**Prompts** (training/rl/make_rl_prompts.py; tests/test_rl.py): 4,000 drills from 1,585 training-split lexemes, in
the export's own prompt format. Inflection drills ask for cells the SFT export did not drill, 4 per lexeme, 10 per
ablauting lexeme. Paradigm drills ask for every gender of an ablauting adjective and every ABLAUT_BLOCKS block of an
ablauting verb. About a third of the prompts are paradigms, ablauting ones first. Mix: 1,876 ablauting and 791
regular inflections; 967 ablauting and 366 regular paradigms.

Held out (the test checks it): every lexeme with an eval task and every lexeme of the frozen v1 and v2 prompt sets
(264 lexemes). The valid split is 64 prompts of whole lexemes kept out of train.

**Reward** (training/rl/reward_engine.py), built against reward hacking, since the policy only sees this number:

- **Inflection:** 1 only if the whole answer is one of the cell's admissible forms; two forms, a hedge or
  commentary score 0.
- **Paradigm:** scored line by line. Each cell scores when its first row gives the engine's form. Every other line
  costs half a cell: a repeated cell (a second guess), a cell the table lacks, a row with two forms, or prose. The
  best answer is exactly the table.
- **Checked against the official scorer:** on e3's v2 generations the reward equals training/score_generations.py
  (paradigm cells 0.808, inflection exact 0.763). All 4,000 references score 1.0. The exploit cases (a second guess,
  padding, a hedged row, prose) score below 1 (tests/test_rl.py).
- **What the reward cannot see** (translation, chat, meaning) is held by the KL term to e3 (beta 0.1). It is also
  checked outside the loop: after the run, training/rl/after_run.sh re-scores the frozen v1 and v2 sets on the e3
  baseline and checkpoints 100, 250 and final, all through the same mlx_lm path (eval_ckpt.py).
- **Signs of hacking** (watched on the dashboard's /rl page): a rising train reward with flat v2; rising KL; a jump
  in tokens per rollout or in the share of rollouts hitting the cap.

**Config** (training/rl/engine_drills.yaml):
- 8 prompts x 8 rollouts per step, temperature 1.0, cap 384, as configured; **as run, 4 rollouts and a 512-token
  cap** (found 2026-11-01). mlx-lm-lora applies a YAML value only when the matching CLI option is None, so options
  with parser defaults (group_size 4, max_completion_length 512) ignored the config. Stage 1 was 32 rollouts per
  step. training/rl/grpo.py now passes those keys explicitly (yaml_wins);
- lr 5e-6, beta 0.1, a new rank-8 LoRA over the quantized e3, gradient checkpointing;
- 500 steps, checkpoints every 25, validation every 50.

Started 2026-11-01 about 01:00.

Early steps: train reward ~0.88–0.98. Many groups score 8/8, so they carry no advantage; the learning signal comes
from the prompts where rollouts disagree (dashboard "group σ").

**Running it:**
- `training/rl/setup.sh` makes the venv (/Users/david/AI/pie-runs/rl/.venv).
- `training/rl/run.sh NAME CONFIG` starts a run under caffeinate. Stop it with `kill $(cat RUN/pid)`.
- `training/rl/after_run.sh NAME` evaluates the checkpoints once training is done.
- `training/rl/sync_dashboard.sh NAME` copies the logs to tr-desktop's dashboard (`/rl`) every 5 minutes.

## Stage 2 (with the API key): the judge for what the engine cannot decide

Tiered, so most rewards never reach an LLM:

1. **The engine:** drills right or wrong. Hard fails score 0: an unknown word, an English or modern word in a PIE
   answer, an empty, truncated or looping answer, or the wrong language.
2. **Local checks on translation and dialogue:**
   - clearly right (the reference, or high chrF with every word analyzed and the reference's lemmas) earns full
     reward;
   - clearly broken (failed case or agreement, low lemma overlap) earns low reward.
3. **The judge, for the rest:** Haiku 5.5 (high), one rollout per call, with the engine analysis of every word
   inline (all readings, grouped by lexeme, and every sense), at most 6 calls in parallel, identical answers cached.

Proposed, pending the owner (who chose Haiku with Sonnet checking its flags): round 3 of the judge test
(docs/research/judge-test-2026-10-31.md, 2026-11-01) argues for dropping the Sonnet confirmation tier. Sonnet low,
without the engine tool it had in round 1, Sonnet low cleared real errors Haiku had caught (two dropped negations), and Haiku high alone
catches 34/35 with 2 false alarms at $1.36 per 1,000 judgments. Expected: 10–20% of rollouts reach the judge, about
$5–15 per run.

### Result (finished 2026-11-01 05:31 EST; 500 steps in about 4.5 h)

- **Speed:** steps averaged about 33 s, between 20 and 40 s depending on how many paradigms the batch held.
- **Training metrics:**
  - train reward 0.81–0.95, noisy per batch;
  - KL to e3 stayed at 0.04–0.13;
  - tokens per rollout 40–90, with no rollout hitting the cap.
- **Checkpoint scores:** the frozen prompts were re-scored greedily through mlx_lm (eval_ckpt.py). "base" is e3 itself
  on the same path; its v1 numbers sit within a point of the omlx ones.

| v2 drills (371, held-out lexemes) | inflect exact | abl / non | paradigm cells | abl / non |
|---|---|---|---|---|
| e3 (base) | 79.4% | 69.6% / 91.5% | 83.5% | 72.6% / 93.9% |
| step 100 | 76.0% | 67.7% / 86.0% | 82.4% | 67.4% / 96.7% |
| step 250 | 76.3% | 70.9% / 82.9% | 81.5% | 70.3% / 92.3% |
| **step 500** | 78.4% | **70.9%** / 87.6% | **87.5%** | **76.0% / 98.5%** |

| v1 (246) | chrF | inflect exact | paradigm cells | EN→PIE task / app | PIE→EN task / app | dialogue (4 kinds) |
|---|---|---|---|---|---|---|
| e3 (base) | 61.1 | 85.4% | 86.9% | 43.6 / 52.7 | 55.5 / 61.9 | 27.8 / 29.7 / 30.1 / 26.9 |
| step 500 | 61.2 | 85.4% | 87.0% | 42.9 / 52.4 | 58.8 / 62.7 | 27.0 / 25.6 / 29.3 / 30.5 |

**What it did:**
- **Gains:** paradigm tables of held-out lexemes improved by 4 points, both ablauting (+3.4) and regular (+4.6).
  Single ablauting forms are slightly better (+1.3).
- **Losses:** single forms of regular lexemes are worse (91.5% → 87.6%).
- **Unchanged:** translation and dialogue are flat within single-reference noise, so the KL term held them.

**The regression has a recognizable pattern.** Of the inflections step 250 lost, most were duals that gained a stray *-e*:
- *h₁óloh₁* → *h₁óloh₁e*;
- *donḱéh₂h₁* → *donḱéh₂h₁e*;
- *dʰubʰréh₂h₁* → *dʰubʰréh₂h₁e*.

The cause looks like the mix:
- Every one of its 50 *-h₁e* dual targets (the consonant-stem ending) came from ablauting lexemes.
- 71% of the prompts were ablauting.

The model spread *-h₁e* to thematic and *eh₂* stems. Steps 100 and 250 were worse than e3 overall, and step 500 recovered most of that: early RL churns before it settles.

**No sign of reward hacking:**
- rollout lengths stayed short, and none hit the cap;
- the train reward moved with the held-out scores;
- the exploit cases score below 1 by construction.

**Group σ in stage 1 was measured over 4 rollouts per prompt**, not 8 (see Config), which makes a 4/4 group more
likely than an 8/8 one: part of the weak signal.

**Next round (stage 1b):**
- **Balance the mix:** regular lexemes at about their natural share, so known endings are rehearsed.
- **Raise the learning signal:** filter to prompts e3 does not reliably get right. Most groups scored 8/8 and taught
  nothing; group σ fell to 0.03 by step 400.
- **Run longer from step 500,** or from e3 with the new mix.

## Stage 1b: balanced drills + judged EN→PIE (rl2-mix-e3)

Owner, 2026-11-01: agreed on the plan below; the judge is Haiku/Haiku, and only what the local checks cannot decide
reaches it; everything runs unattended (training/rl/pipeline.sh).

- **Candidates** (make_rl_prompts.py --mix v2): every training lexeme at its natural share; per lexeme 2 undrilled
  cells, 1 cell the SFT export drilled (an anchor), and a dual for half the nominals; paradigms of every family;
  EN→PIE translation of training-split records of up to 35 English words. 3,000 inflection, 1,200 paradigm and
  1,543 translation candidates.
- **Pass-rate filter** (passrate.py): e3 samples each candidate 4 times at temperature 1.0, scored locally. Drills
  e3 always gets right are dropped (at most a quarter of the kept ones are never right); translations it reproduces
  exactly every time are dropped. Train: up to 4,000 prompts, 40% inflection, 20% paradigm, 40% translation.
- **Reward** (reward_rl.py): drills as stage 1. Translation: local zero for an empty, multi-line or padded answer
  or any unknown or near-spelled word (which is how an English word fails); local one for a reference; else the
  judge (judge.py: Haiku high, a second Haiku high call on its flags, wrong only if both say so): ok = 1 (0.95 per
  word matched only without its accent), wrong = 0, no verdict = 0.5. Every judge call is logged (RUN/judge.jsonl).
- **Validation by stratum:** 180 prompts of held-out lexemes (2–3 per stem class) and 24 held-out records, logged
  per kind, ablauting or not, and an inflection's number, on the /rl page every 100 steps.
- **From e3**, 500 steps of 8 prompts x 8 rollouts, other settings as stage 1.
- **Smoke test** (2 steps, 64 rollouts per step): generation 34–46 s per step; the judge added 26 s on a step with
  translations; $0.012 for 2 steps.
