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
- 8 prompts x 8 rollouts per step, temperature 1.0, cap 384;
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
3. **The judge, for the rest:**
   - Haiku 5.5 (high) screens the remaining fluent, valid answers that differ from the reference;
   - Sonnet 5.5 (low), with the engine tools, re-checks only the samples Haiku flags;
   - calls run in parallel during the next step's generation, and identical answers are cached.

Expected: 5–15% of rollouts reach tier 3, about $10–20 per run. The first step with the key is a repeat of the
Haiku-high judge test (training/judge_test) to confirm its 34/35.
