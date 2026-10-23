# Phase 8b backtest: can a model rediscover the laryngeals?

First experiment, 2026-10-23. Code: `pie/backtest.py` (data, matching, metrics; tested in
`tests/test_backtest.py`) and `scripts/run_backtest.py` (training and evaluation). Numbers:
`data/research/backtest/results.json` (primary) and `results_secondary.json`; dev grid in `tune.json`;
probabilities in `results_eval.npz` and `results_oof.npz` (and `_secondary` variants), so the analysis can be redone
without retraining.

## Verdict

**Not demonstrated.** On the pre-registered test (held-out eval families, context-matched controls), the
difference at laryngeal positions is not significant for any metric, in either run. Too few eval slots
have a valid matched control (10 in the primary run, 26 in the secondary), so the test cannot decide
either way.

A better-powered secondary analysis (out-of-fold over train+dev) finds a modest excess of **surprisal and
error** at laryngeal positions that survives subtracting both baselines, but only for two of the four
effect kinds:

- **loss**, mostly medial vowels right after a lost laryngeal. Primary: +0.30 nats [0.05, 0.60] beyond the
  shuffled-input model.
- **a-coloring**, in the secondary run only.

**Entropy** rises no more than the shuffled model's (+0.09 against +0.10): the model is systematically wrong
at these positions, not more uncertain.
Long vowels from a laryngeal are no harder than lengthened-grade long vowels. The free symbols do not land
on laryngeal positions. The Hittite check cannot be run on this data. By the PLAN 8b acceptance rule this
is a negative result, with a lead worth a larger eval set.

## Setup

- **Data.** `primary.jsonl` has 1,785 cognate sets from attested languages only (train 1,422 / dev 189 /
  eval 174, split by root family). `secondary.jsonl` adds PGmc, PItal and PCelt (3,188 sets). The target is
  PIE written the pre-laryngeal way.
- **Units.** Targets are split into phoneme units: a base letter plus its marks, e.g. ḗ, dʰ, gʷʰ, r̥̄
  (55 types). Each decoding step is one unit, and the end of the word is a slot too. Gold effect offsets
  are mapped onto unit slots. A loss effect points at the unit after the lost laryngeal.
- **Model.** A character-level transformer, trained from scratch on this data only, with no LLM and no
  phonological prior:
  - Encoder: 3 layers, d=128. Each input token is an NFD character (so length and accent marks are
    separate symbols), plus a language embedding and its position within the form. Languages come in a
    fixed order (training frequency), with up to 2 forms per language and at most 120 tokens.
  - Decoder: 2 layers.
  - Training augmentation: languages are dropped at random (p=0.2).
  - Tuning: an 8-config grid chosen on dev NLL. The final runs use 40 epochs with dev early stopping.
  - The main model is an ensemble of 3 seeds, scored once on eval.
  - CPU time: each training run takes about 2.5 minutes; the whole pipeline takes 10 minutes (primary)
    and 19 minutes (secondary).
- **Metrics.** All are teacher-forced, per slot: error (argmax ≠ gold), entropy, and surprisal (−log p of
  the gold unit). Surprisal has the most statistical power.
- **Control matching.** Each effect slot is compared with non-effect slots in the same stratum:
  - Exact stratum: the same unit (base, length, accent) in the same word position (initial, medial,
    final, end). This is the headline. Word position matters: most loss slots are word-initial, and
    vowel-initial slots are hard for the model (entropy around 1.6–2.2), while consonant-initial slots are
    often easy. Nearly all vowel-initial slots are loss effects.
  - Class stratum: vowel or consonant, length, accent and position only (weaker).
  - Controls come from the same word when it has any, otherwise from other words. A stratum is used only
    if its controls come from at least 3 root families. This rule was added after the first analysis:
    single stray controls (kā́ps for medial ā́, gugā for final ā, átta for initial á) were standing in for
    65, 58 and 44 effect slots.
  - Contrast: the mean of per-effect (effect − mean of its controls). 95% CI from a 2,000-sample percentile
    bootstrap over root families (an entry with no root is its own family).
- **Baselines.**
  - (a) The same model with daughter forms shuffled across training sets.
  - (b) A frequency baseline: unigram and bigram unit models of the training targets.
  - Their per-slot surprisal is subtracted from the model's ("− shuffled", "− bigram"), so what remains is
    what the daughter evidence adds beyond target statistics.
- **Out-of-fold (OOF).** 5 folds by root family over train+dev, eval untouched, 30 fixed epochs. For each
  fold there is a real model, a shuffled model and a bigram model fit on that fold's training part.
  Labeled secondary: it was added after the eval run turned out to be underpowered.

## Testability

Testable means the stratum has controls from at least 3 root families. Counts are effect slots over all
1,785 sets.

| | slots | exact-testable | why not |
|---|---|---|---|
| schwa | 167 | 0 | every ə comes from a laryngeal |
| ā, ā́, ī, ū, R̥̄ | ~300 | 0 | almost no PIE long a/i/u or long resonant without a laryngeal |
| loss at an initial vowel (except é-) | ~130 | 0 | the lexicon has almost no vowel-initial words without a laryngeal |
| loss at initial r- | 45 | 0 | no non-laryngeal initial r- |
| color a/á medial, ō/ṓ | ~60 | yes | |
| length ē/ḗ/ō/ṓ vs lengthened grade | ~120 | yes | |
| loss at a medial vowel, or initial w/y/l/m/n/s | ~250 | yes | |

So the testable part is the part that *looks* normal on the surface. The untestable part (ā, ə, initial
vowels) is exactly where Saussure saw the anomaly: there, the signal is that the segment is rare in the
first place, and matching on segment identity cannot measure that.

## Results

### Primary run, eval (the pre-registered test)

The model is weak:

- Real model: greedy exact match 4.6%, unit error rate 0.58–0.60. On train: 25% and 0.35.
- Shuffled model: 0% exact match, unit error rate about 1.0. So the real model does use the daughter forms.

Contrasts (95% CI):

| eval, primary | n matched / 101 | surprisal (nats) | error | entropy |
|---|---|---|---|---|
| exact | 10 | +0.24 [−0.72, +1.67] | +0.11 [−0.15, +0.41] | +0.28 [−0.18, +0.87] |
| class | 73 | +0.71 [+0.19, +1.37] | +0.10 [+0.01, +0.22] | +0.07 [−0.08, +0.26] |
| class − bigram | 73 | −0.39 [−1.19, +0.25] | | |
| class − shuffled | 73 | +0.23 [−0.12, +0.62] | | |

- The bigram baseline alone gives +1.10 [+0.49, +1.95] at class level, so the class-level effect is fully
  explained by the rarity of the units.
- Per seed, the exact surprisal difference is +0.25, +0.29 and +0.43.
- Secondary run, eval (283 sets, 26 exact slots): surprisal +0.76 [−0.48, +1.87], and +0.17 [−0.78, +1.11]
  after subtracting the shuffled model. Also null.

### Out-of-fold over train+dev (secondary analysis, powered)

Exact strata only. Surprisal in nats: raw, then after subtracting each baseline.

| | n (families) | raw | − bigram | − shuffled |
|---|---|---|---|---|
| **primary, all** | 337 (207) | +0.65 [+0.42, +0.91] | +0.38 [+0.15, +0.62] | +0.27 [+0.08, +0.48] |
| color | 48 (34) | +0.70 [+0.12, +1.31] | −0.15 [−0.84, +0.55] | +0.24 [−0.20, +0.72] |
| length | 110 (76) | −0.06 [−0.29, +0.20] | −0.00 [−0.37, +0.37] | +0.22 [−0.00, +0.46] |
| loss | 228 (151) | +1.00 [+0.69, +1.35] | +0.54 [+0.24, +0.88] | +0.30 [+0.05, +0.60] |
| **secondary, all** | 638 (315) | +0.71 [+0.47, +0.96] | +0.44 [+0.21, +0.66] | +0.22 [+0.01, +0.44] |
| color | 99 (60) | +1.79 [+1.17, +2.43] | +0.91 [+0.30, +1.55] | +1.20 [+0.84, +1.62] |
| length | 233 (142) | −0.39 [−0.64, −0.12] | −0.23 [−0.48, +0.04] | −0.24 [−0.50, +0.04] |
| loss | 409 (214) | +1.33 [+1.02, +1.66] | +0.78 [+0.49, +1.08] | +0.45 [+0.18, +0.74] |

**Error and entropy.** Primary run, exact strata:

- Error: +8.2 points [+4.2, +12.2]; the shuffled model gives +4.4 [+1.8, +7.0].
- Entropy: +0.09 [+0.02, +0.17]; the shuffled model gives +0.10 [+0.04, +0.17].

So the model makes extra errors at laryngeal positions, but its extra uncertainty there is no more than
target statistics alone produce.

**What drives it.**

- **Loss.** Mostly medial vowels right after a lost laryngeal (CHV, VHV: o, ó, e, é, a medial, +1.2 to
  +2.9 nats). Initial w-, y-, l- after a lost #H add only +0.1 to +0.5.
- **Color.** Mostly colored a/á against the few plain-a words (7 control families).
- **ṓ.** Colored and lengthened ṓ shows nothing.

**Schwa** has no exact controls. Against short vowels (class level) it is +0.46 [+0.16, +0.78] after
subtracting the bigram baseline and +0.75 [+0.50, +1.02] after subtracting the shuffled model (primary).
The daughter forms help less at ə than at other short vowels. But ə is already a symbol in the target, and
class matching only partly controls for its rarity, so this is weaker evidence.

**Training variance.** Before the 3-family rule, two OOF trainings gave exact surprisal +0.49 and +0.54:
the training variance is small compared with the CI.

### Free symbols (stronger variant)

**Method.**

- k=4 extra target symbols.
- Seeding: a symbol is inserted before each training unit whose OOF surprisal is in the top 10% of
  training slots, 831 slots in all.
- Assignment: k-means on the OOF predictive distribution at that slot (no gold labels).
- Refinement: two hard-EM rounds that reassign which symbol goes where.

**Train side.** 25% of the seeded slots are laryngeal-effect slots, against a base rate of 9.9%. So the
seeding does follow irregularity. Under the model's own likelihood, "no symbol" would have won at 237 of
the 831 slots.

**Eval.** We measure the free-symbol probability mass at each gold slot.

- Unmatched: 0.089 at effect slots against 0.044 elsewhere.
- Matched: no difference.
  - Class level: −0.003 [−0.023, +0.021].
  - Exact level: −0.014 [−0.049, +0.040].
  - Loss alone: +0.056 [+0.012, +0.110] (n=17).
  - Length: negative.
- No eval slot gets more than 0.5 of the mass.
- Secondary run: class −0.005 [−0.017, +0.008].

**Reading.** The symbols track where the model is irregular. They do not mark laryngeal positions beyond
what the segment class already predicts.

### Hittite confirmation

- 86 primary sets have a Hittite reflex. Only 12 have a usable ḫ: most are logograms or have no ḫ.
- Eval: 3 sets, 6 ḫ. Three of those are the verbal suffix -aḫḫ- of *gʰr̥yéti*, not a root laryngeal.
  2 of the 6 sit on a top-quartile-entropy slot, against 0.41 expected by chance.
- OOF: 10 ḫ, hit rate 0.50 against 0.55 expected. Secondary OOF: 16 ḫ, 0.50 against 0.53.

The original confirmation cannot be run with this little Hittite.

## Failure cases

- **Colored ā is decoded as ē or e.** Examples: *dwārós* → dwḗros, *nā́us* → nḗws, *swā́dus* → swḗwst,
  *néwāti* → néweti.
  - This is Saussure's "e-vowel behind the a", but the confusion tables are mixed.
  - OOF, exact color slots: predicted as the e-vowel 23% of the time against 14% at controls (primary);
    10% against 3% (secondary).
  - At class level it reverses in the secondary run: 3.9% against 14.8%.
  - So it is not a reliable signal.
- **Initial vowels after loss are untestable,** and the model mostly gets them wrong anyway: *ólos* →
  árǵe, *nómn̥* → énwen, *ṓws* → wésus. The prothetic vowel of Greek and Armenian is the evidence there.
- **Length shows nothing.** Laryngeal ḗ, ē, ō are, if anything, easier than lengthened-grade ḗ (*pətḗr*,
  *dyḗws*). Both are mostly decoded as short é.
- **The model is weak:** 4.6% exact match on eval. Most control slots are also wrong (error 0.6–0.7 in
  matched strata), so the error metric is close to its ceiling, and surprisal is the informative metric.
  1,422 training sets are too few for a stronger reconstructor. The secondary run, with more data,
  reaches 13% exact match.

## Stated limit (PLAN 8b)

Wiktionary's cognate grouping already assumes coloring and prothesis, i.e. which Greek word belongs to
which root. Saussure's Neogrammarian groupings were mostly the same, so the test stands. But even a
positive result would only mean "the inference is recoverable from these correspondences", not "a naive
learner would make it".

The dataset adds a second limit. The lexicon is laryngealist, so the pre-laryngeal targets contain
almost no long a, i, u, no ə and no vowel-initial words that are *not* laryngeal reflexes. Where the
laryngeal theory makes its strongest claims, there is nothing to match against. The matched-control
design can only test the surface-normal residue.

## Deviations from the brief

- **Control rule added after first contact with the data.** The 3-family minimum was added after seeing
  the OOF analysis, not the eval. The eval predictions were computed twice, before and after the rule
  (retraining is deterministic: identical eval accuracy). Both versions are null.
- **OOF analysis and secondary run added.** Both were added after the eval run proved underpowered. They
  are labeled secondary, and no hyperparameters were retuned for them.
- **One tuned value reaches the OOF models.** They use 30 fixed epochs, chosen from dev NLL, and the dev rows
  are also in the OOF held-out pool. This is one scalar hyperparameter, a mild leak, but it is another
  reason the OOF analysis is labeled secondary.
- **Schedule shortened.** The grid ran a 120-epoch schedule and dev NLL was best at epoch 25, so the
  final runs use a 40-epoch schedule; this is recorded in `tune.json`.
