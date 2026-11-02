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

## Speed

- About 80 s per step at batch 8 × group 8, with a 384-token cap. Generation is 55–75 s of that; the judge runs
  inside generation time. 500 steps is about 11 h, plus about 1 h of validation.

## Measuring

- **Benchmark first, then choose the RL target.** The v2 benchmark (benchmarks/) showed where we trail the
  frontier models: PIE→EN 83 vs 91–98, dialogue 80 vs 96. That is why stage 3 added those kinds. Re-run the
  benchmark on each stage's final and best checkpoints.
