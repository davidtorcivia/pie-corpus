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

## Stage 5 (rl5-nemotron-e3, 2026-11-03)

- **Earlier RL prompts were memorized.** Every translation and dialogue prompt of the rl3/rl5 sets, train and
  validation, is verbatim in the SFT export e3 was trained on, and e3 reproduces 82–89% of them exactly. Their
  validation measures recall (translation stays at 1.00 from step 1). Stage 6 (make_rl6.py) builds prompts from
  Tier 3 batches held out of every export (`pie.export.RL_HELDOUT_PREFIX = "rl6-"`, with a test).
- **Shared reference.** A second full copy of the 120B as the KL reference peaked at 223 GB. Zeroing the LoRA
  scales for the reference forward (`PIE_REF_SHARED=1`, grpo.py AdapterOff) gives the same reference at 138–154 GB.
- **100 steps (one pass over 743 kept prompts), about 2 min a step, KL peaked at 0.10.** Validation 1 → 100:
  English→PIE vocabulary 0.48 → 0.61 (only 9 prompts: noisy), dialogue 0.88 → 0.93, the rest flat. Frozen sets:
  v1 flat (chrF 73.0 → 72.9; each drop one prompt), drills_v2 paradigm cells 0.887 → 0.898, inflection 0.885 both.
- **Benchmark v2 (round 10): 87.7 lenient / 86.2 strict, against e3's 88.5 / 86.2.** EN→PIE strict 81.0 → 83.9,
  paradigm 88.4 → 89.5, PIE→EN 88.7 → 85.1 (about 1.5 of 42 items), dialogue 87.1 → 85.5 (one of 64). A tie
  within noise. Caveats: e3 was benchmarked in bf16 on Tinker, rl5 in the local 5-bit quant (e1 showed the quant
  costs nothing measurable, 87.6 vs 87.1), and 89% of rl5's answers are word for word e3's. Lesson: RL on prompts
  the model has memorized moves little; RL needs prompts it has not seen (stage 6).
- **Never let two after_run.sh evals overlap.** Restarting run_rl5.sh left the earlier pipeline's after_run.sh
  waiting; when the trainer exited both ran, two Nemotron copies OOMed Metal and one eval (drills_v2 base) was lost.
  Kill the old pipeline's waiters when restarting a pipeline.
- **zsh does not word-split `${x:+--flag $x}`:** it passes one argument "--flag value" (argparse: unrecognized
  argument). Use arrays.

## Stage 6 (rl6-nemotron-unseen + rl6b-resume50, 2026-11-03/04)

- **Prompts from unseen text.** 1603 kept prompts (pass rate on e3 below 1): EN→PIE 600, PIE→EN 360, dialogue
  328, vocabulary 280 (EN→PIE 200, PIE→EN 80), drills 35. Validation is 232 held-out prompts (unseen text only;
  vocabulary split by lemma), all scored at each check (val_batches 29, about 38 min).
- **A model loaded beside the trainer killed it.** At step 61 an omlx client loaded an 87 GB model beside the
  150 GB trainer; the trainer died without an error line, and the default after_run.sh then started an eval beside
  omlx. omlx's unload endpoint did not exist for that model, so the service was stopped
  (`launchctl bootout gui/501/ai.omlx.serve`) for the rest of the stage. Lesson: stop omlx (or anything else that
  can load a model) before a long Mac run, and restart it after the evals. The run resumed from the step-50 adapter
  (resume_rl6.sh: weights resume, the schedule restarts, so the cosine is set to continue from 4.35e-6).
- **201 steps moved nothing measurable on held-out text.** Validation, rl6 step 1 → the end of rl6b: dialogue
  0.39 → 0.43–0.46 (40 prompts; noisy), EN→PIE 0.921 → 0.924, PIE→EN 0.934 → 0.931, EN→PIE vocabulary
  0.293 → 0.297 (32 prompts), PIE→EN vocabulary 0.764 → 0.741, drills at the ceiling. Frozen sets, base → final:
  v1 chrF 73.05 → 73.09, drills_v2 paradigm cells 0.887 → 0.904 (the one gain, as in stage 5).
- **Why: too little signal per prompt.** Training rewards (5-step means) sat at 0.60–0.87 with a within-group σ of 0.04–0.17:
  most groups' 8 samples scored alike, so the advantages were near zero, and at a peak LR of about 5e-6 the KL never
  passed 0.16. Next: refilter on the current policy to prompts it passes sometimes (pass rate about 0.1–0.6),
  weight dialogue and EN→PIE vocabulary (the kinds with room), and raise the LR to about 1e-5 with the KL stop as
  the guard.
- **after_run.sh's scorer failed** on a corrupted uv cache (`/tmp/pie-uv-cache`, a wheel without METADATA); the
  generations were fine and were rescored with a fresh UV_CACHE_DIR. Check summary.txt for `error:` lines.
- **Benchmark v2 (round 11, Opus judge only; GPT/Sol judging unavailable): rl6 final 86.1 lenient / 84.5
  strict, against rl5's 87.0 / 85.5 and e3's 88.3 / 86.1 on Opus verdicts alone.** Segments (strict): inflection
  89.0, paradigm 89.6, EN→PIE 82.1, PIE→EN 86.9, dialogue 75.0 (rl5 80.5). The gap is the judge, not the model: on
  the 41 dialogue items where rl6's answer is word for word rl5's, the round-11 judge gave 31.5 against round 10's
  35.5 (12 disagreements). On the 23 dialogue answers
  that differ, rl6 16.5 vs rl5 16.0. 90% of rl6's answers (594 of 659) are rl5's. Lessons: stage 6 is a tie with
  rl5 and e3; a lone-contestant round with one judge carries about ±1 point of judge noise on the overall score, so
  compare verdicts on identical answers across rounds before reading a difference.
