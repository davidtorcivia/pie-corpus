# RL lessons (running notes)

Notes taken while the RL stages run, for designing the next ones. Each note gives what happened and what to do
next time. Details of each stage are in `rl-mac.md`; this file is the short list of what to change.
Started 2026-11-01 (owner: "Take notes as we go so we can note how to improve future RL").

## Configuration

- **Check the config the trainer actually used, not the YAML.** mlx-lm-lora applies a YAML key only when the CLI
  option is None, so stage 1 ran with group size 4 and a 512-token cap instead of 8 and 384. `grpo.py`'s
  `yaml_wins()` now passes those keys on the command line. Next time: read the `start` event in
  `metrics.jsonl` (argv) and the first metrics row (generated-token counts) before trusting a run.
- **`judge_usd` in `rewards.jsonl` is cumulative.** Read the last row; don't sum the rows.

## Prompt mix

- **Filter by pass rate before training.** 81% of the inflection candidates for stage 1b were always right at
  k=4, temperature 1.0: those groups give no gradient. `passrate.py` keeps only drills the policy sometimes
  misses. The filter costs about an hour of sampling (4,760 candidates); it's worth it.
- **Keep plain single forms in the mix** (owner, stage 1b) so the drilled skills don't degrade. They're in. Even
  so, in stage 3 (rl3), inflection validation went 0.88 → 0.78 → 0.81 and paradigms 0.95 → 0.89 → 0.87 over
  steps 1/100/200 while dialogue and translation rose. Possible fixes for next time: a larger anchor share of
  easy drills, a higher KL beta (0.1 now), or a reward that never lets an already-right skill go unrewarded.
  *Watch the step 250/400 evals before deciding.*
- **Hard drills can be too hard.** EN→PIE vocabulary drills score 0.0 in many validation batches. A group where
  all 8 rollouts score 0 teaches nothing, the same as a group where all score 1. To do: log the share of
  zero-variance groups per kind. Drop or reword kinds that are mostly all-zero, for example by giving the
  English gloss's sense or part of speech.

- **rl3 drifted after ~step 450 (overall).** Resumed as rl3b from step 275: KL to e3 spiked to ~0.3 on single
  batches from step 85, then rose for good: 0.18 → 0.36 → 0.43 → 0.66 over overall steps 465–480, with validation loss
  0.013 → 0.023. Validation per skill, rl3b step 1 / 100 / 200 (overall 276 / 375 / 475): dialogue .73/.70/.65,
  inflect .83/.79/.75, PIE→EN vocab .73/.70/.58, paradigm flat .86/.85/.88. The best weights by validation are
  step 275's. Stopped at 205 of 225. Next time: watch KL as well as rewards (a sustained climb past ~0.3 is the
  stop signal here), keep beta higher than 0.1 or decay the learning rate, and plan fewer steps per stage.

- **RL on top of a merged adapter degrades fast (stage 4, 2026-11-02).** From the 0.5 rl1 + 0.5 rl3-275 merge (benchmark
  84.5, our best), with KL to the merge itself (beta 0.2), lr 5e-6 cosine, rank 16: by step 25 the drills fell .801 → .704
  exact and chrF 89.9 → 85.6 (v1 exact .854 → .833); step-50 validation fell in 5 of 7 skills (dialogue .67 → .51, inflect
  .90 → .80, EN→PIE .67 → .55) at KL only ~0.13. Likely: Adam moves each weight by ~lr whatever its size, and the merge
  halved both adapters' B, so the same lr is about twice the relative change, on a balanced point between two skill sets.
  Next time: train each new skill as its own delta from e3 and merge (the deltas are orthogonal: cos ~0.000), or scale
  lr by the merge weight. Stopped at 50 by the val-loss rule, which itself was wrong here (a ratio to a ~0 first loss;
  fixed: a 0.02 floor).

## Validation

- **Read per-skill validation on fixed batches, not batch training rewards.** Training-batch means per kind swing
  by ±0.2 from batch to batch because each batch draws different prompts. The per-stratum validation is the
  signal. Each validation pass takes about 11 minutes (22 batches).
- **Every kind must be scored in validation.** rl3's `valid.jsonl` has 16 `translate_pie_en` items (and 24
  EN→PIE), but no PIE→EN reward appears in the validation strata, and EN→PIE appears only rarely. Validation
  runs `val_batches` 22 × batch 8 = 176 of the 228 items, so the longest prompts (the translations) probably
  fall outside the evaluated batches. As a result, the skill the benchmark says is weakest goes unmeasured
  during training. Fix: set `val_batches` to cover the whole file (29), or order and size the validation file
  so every kind is in the evaluated batches. Then check the strata keys on the step 1 validation.

## Judge

- **Haiku 5.5 high screen + second Haiku confirm on flags** (wrong only if both say so): 31–33/35 recall, 1
  false alarm in the judge test; about $1.36 per 1,000 judgments. rl3 has spent about $1 in its first ~200 steps:
  4,491 judgments, 28% judged wrong, 57% of them dialogue.
- **One brief per kind.** The EN→PIE brief misjudged PIE→EN answers; the dialogue brief passed echoes of the
  turn. Each new kind needs its own brief and a check against Opus on ~100 items before it goes into the
  reward. Agreement with Opus was 79% for PIE→EN and 85% for dialogue. PIE→EN still has 28 false negatives,
  so it's the brief to improve next.
- **Cheap local checks first.** The local echo check (≥90% overlap with the turn), the modern-word regex,
  English/Gloss markers and unknown words decide many dialogue rollouts without an API call.
- **API limits.** 6 concurrent requests (16 got 429s); a regex fallback for unparsable JSON.

## Running evals during training

- **Never run checkpoint inference on the Mac while a GRPO run is training.** On 2026-11-01 at 22:05 I started
  a step-250 eval (a second copy of the 35B with its adapter) beside rl3. The trainer (85 GB) died silently at
  step 288, about 3 minutes later: no traceback, only a leaked-semaphore warning. after_run.sh then started its
  own eval, and both evals hung for 11 hours, one in uninterruptible state (`UN`). Steps 276–288 were lost, and
  the run has to be resumed from the step-275 adapter. Next time, evaluate checkpoints only after the trainer
  exits, or on another machine. If an eval must run mid-training, first pause training at a checkpoint.
  The wedged GPU recovered without a reboot: the stuck process finished exiting on its own about 12 h in, and
  94 GB of wired memory came free. Resumed as rl3b-resume275-e3 (`training/rl/resume_rl3.sh`). Guards now:
  `eval_ckpt.py` refuses while a `grpo.py` trainer is alive; `watch.sh` alerts on a dead or stalled trainer;
  and the agent schedules check-ins on every run it starts (owner: "You need to be checking on in the run").
- **Step 250 of rl3, v1 prompts, compared with base:** inflection exact 0.854 → 0.812, paradigm cells 0.869 →
  0.826, chrF 61.1 → 59.7, and the first modern-word slip ("machine" for bʰórom 'load', in a PIE→EN app item).
  rl1 also dipped at step 250 (cells 0.817) and recovered by its final step (0.870). The modern-word check should
  cover every kind with English output, not only dialogue.

## Speed

- About 80 s per step at batch 8 × group 8, with a 384-token cap. Generation is 55–75 s of that; the judge runs
  inside generation time. 500 steps is about 11 h, plus about 1 h of validation.

## Measuring

- **Benchmark first, then choose the RL target.** The v2 benchmark (benchmarks/) showed where we trail the
  frontier models: PIE→EN 83 vs 91–98, dialogue 80 vs 96. That is why stage 3 added those kinds. Re-run the
  benchmark on each stage's final and best checkpoints.
