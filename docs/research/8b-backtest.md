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

## Replication (pre-registered)

Plan: `docs/research/8b-preregistration.md`, written before the data existed. Run 2026-10-23.

**Verdict: underpowered, not run.** The fresh data has **1** effect slot with an exact-matched control,
against the pre-registered minimum of 150. As the pre-registration requires, no model was trained, no
surprisal was computed, and H1 (loss) and H2 (colouring) were not tested. The first run's out-of-fold lead
(+0.27 nats beyond the shuffled model) is still a hypothesis: it is neither confirmed nor refuted.

**Data.** Code: `scripts/build_replication.py`. Output: `data/research/backtest/replication.jsonl`; all
counts are in `replication_meta.json`. Sources: the kaikki.org Sanskrit, Ancient Greek and Latin dumps
(`raw/daughters/kaikki-*/`), parsed only with `python -I`.

- **Links.** `{{inh}}`, `{{inh+}}`, `{{der}}` and `{{der+}}` from `ine-pro`, plus `{{etymon}}` `:inh`/`:der`.
  Excluded:
  - borrowings and uncertain links;
  - entries with an affix or compound template, or linked to two word-level PIE etyma;
  - root-only links (terms ending in `-`);
  - roots, affixes and inflected-form pages.
- **Forms.** Sanskrit and Greek romanizations, Latin canonical (macron) forms. The Greek breve was stripped;
  macrons and accents were kept.
- **Same rules as the first run.**
  - Attested languages only. The laryngeal-notation scan found 0% for all three languages.
  - No Anatolian or Tocharian.
  - Targets come from the unchanged `pie/prelaryngeal.py`.
  - At least 2 languages per set.
- **Freshness, at root-family level.** A set was dropped if its etymon or any linked root resolves to a
  lexicon family found in `primary.jsonl` or `secondary.jsonl`. It was also dropped if its target matches
  a first-run target, or if it shares a (language, form) pair with a first-run input.

| step | count |
|---|---|
| PIE-linked entries (sa / grc / la) | 3,707 / 3,225 / 3,190 |
| distinct word-level etyma | 2,065 |
| attested in only one language | −1,675 |
| root family already in the first run | −358 |
| shares an input form with the first run / same etymon | −8 / −1 |
| **fresh cognate sets** | **23** (23 families: 8 resolved through the lexicon, 15 pseudo-families) |
| sets with a laryngeal effect | 9 |
| effect slots (colour 6, length 5, loss 4; schwa 0; one slot can carry two kinds) | 9 |
| **effect slots with exact-matched controls (≥ 3 control families)** | **1** (loss 1, colour 0) |

**Why so few.** Wiktionary's PIE pages already list most of their Sanskrit, Greek and Latin descendants,
and the lexicon was built from those pages. Of the 390 etyma attested in two or more of these languages,
358 belong to a root family the first run already used. What is left is small and has only two languages
per set. With this few target words, almost no stratum has controls from 3 families.

**Sensitivity bound (exploratory, not a substitute test).** To check that the shortfall does not come
from a strict rule, the build was repeated with the loosest reasonable rules:

- affix, compound and multi-etymon entries kept;
- every word-level link counted;
- etyma merged by accent-free key.

(`scripts/replication_sensitivity.py`.) That gives 75 sets, 27 effect slots and 5 exact-matched slots (12 even with a 1-family control rule).
No reading of the pre-registered data source comes near 150.

**What a confirmatory replication would need.** A data source outside Wiktionary's PIE pages: for
example LIV² or handbook cognate tables, or other branches' dictionaries. That needs a new
pre-registration. The present one is closed: underpowered.

## Replication 2 (pre-registered, NIL daughters)

Plan: `docs/research/8b-preregistration-2.md`, written before the data was built. Run 2026-10-23.

**Verdict: underpowered, not run.** The NIL data has **46** effect slots with an exact-matched control,
against the pre-registered minimum of 150. As the plan requires, no model was trained, no surprisal was
computed, and H1 (loss) and H2 (colouring) were not tested. No Holm decision exists because no test was
run. The first run's out-of-fold lead (+0.27 nats beyond the shuffled model) is still a hypothesis,
neither confirmed nor refuted. Colouring is the weaker side: only **2** colour slots have a matched control.

**Normalization.** 291 of the 2,259 daughter words that reached normalization could not be normalized:
**12.9%**, under the 20% caveat threshold. The reasons:

- 158 have a character the first run's inputs never show for that language;
- 99 are fragments (a leading `-`, e.g. ved. *-reká-*);
- 18 are capitalized (names);
- 16 have optional letters (*an(n)udon*).

Slavic is the worst: OCS 23/77, Russian 15/31, Old East Slavic 13/14. NIL's scholarly transliteration
differs from Wiktionary's there. Greek, Sanskrit and Avestan fail at 6–11%. Code:
`scripts/build_replication2.py`. Output: `data/research/backtest/replication2.jsonl`, with all counts in
`replication2_meta.json`. Input: `data/lexicon/nil.jsonl` only (the whole transcribed book, 207 roots,
3,044 formations). Nothing in `raw/` was read.

**Rules fixed before the build.** These are the plan's rules, plus readings the plan left open. All of
them are in the builder's docstring.

- **Formations.**
  - Dropped: ‡ (571), ˣ (46), ** (18), uncertain (488), and those for which `pie.nil.stem()` gives no stem
    (657).
  - Formations with the same stem were merged into one set (14).
- **Daughter words.**
  - Parsing: per language segment of an evidence string, the first word after the abbreviation and its
    labels. A string can cover several languages: "air. dét n., mkymr. dant m." gives two segments, and
    "aav., jav. garəma-" gives one word to both languages.
  - Dropped by the first run's `usable()` rule (no uncertain, no analogical reflexes): `?`-marked words
    (247) and words in NIL's remodelling bracket `[` (335).
  - Also dropped:
    - proto-forms (germ. \*, kelt. \* …: 235); their attested daughters after "in" are kept;
    - starred words (21);
    - Anatolian, including Palaic `pal.` (58), and Tocharian (38);
    - names (56), oblique case forms (34), words cited inside compounds (16), Mitanni and non-IE (7).
- **Normalization** to the Wiktionary romanizations of the training inputs:
  - Greek script → Wiktionary transliteration. Checked on the lexicon's 2,373 Greek reflexes that have both
    a script form and a romanization: 99.8% identical (`build_replication2.py --check-greek`).
  - Sanskrit r̥ → ṛ; Avestan ϑ → θ; Slavonic ь ъ → ĭ ŭ; Armenian ʿ → ʻ.
  - Stem and morpheme hyphens are removed.
  - A word fails if, after this, it has a character outside the model's input vocabulary or outside that
    language's first-run inputs. Failed words are dropped, not fed as `<unk>`.
- **Languages.** NIL's abbreviations are mapped to the first-run labels: ved./ai. → Sanskrit, jav./aav.
  → Avestan, arm. → Old Armenian, and so on. A set needs at least 2 languages.
- **Independence (per formation).** The plan's "stem matches a target up to accent and length" barely
  bites: NIL cites bare stems (*h₂ówi-*), the first run cites nominatives (*h₂ówis*). It was tightened in
  two ways, both of which can only remove sets:
  - the stem, its pre-laryngeal target and its expected nominatives (`pie.nil.expected`) are also
    matched against first-run targets and modern forms, with and without -os/-om/-s/-m;
  - a formation is dropped if `pie.nil.apply()` linked it to a first-run row's lexicon entry.
- **Target and family.**
  - Target: `convert(stem)`, the bare stem, as pre-registered.
  - Family: the lexicon root linked to the NIL root, else the NIL root itself.

| step | count |
|---|---|
| NIL formations | 3,044 |
| after marker, uncertainty and stem filters (14 merged) | 1,250 |
| fewer than 2 languages after word filters | −770 |
| transducer failed | −4 |
| linked to a first-run lexicon entry / stem or nominative matches a first-run form | −148 / −54 |
| **cognate sets** | **274** (122 families, 76 of them lexicon roots) |
| sets with a laryngeal effect | 183 |
| effect slots (colour 96, length 111, schwa 34, loss 93; one slot can carry two kinds) | 235 |
| **effect slots with exact-matched controls (≥ 3 control families)** | **46** (loss 42, colour 2, length 3; 31 families) |

**Why so few.** There are three reasons:

- Most NIL formations have one usable language. NIL cites at most four daughters, often from one
  branch, and once ‡, `?`, `[`, proto-forms and Anatolian/Tocharian are removed, 770 of 1,250
  formations are left with fewer than two languages.
- The independence rule removes 202 of the remaining 476. They are the common, well-attested formations
  the first run already trained on.
- In the 274 surviving targets, the colour and length slots fall in strata with no non-laryngeal
  controls from 3 families. The largest is stem-final ā (the eh₂-stems, 46 colour slots); then come
  initial a and medial ā/ō. What does get matched is mostly loss:
  - stem-final o after a lost laryngeal: 23 of the 46 slots. This is a position that bare-stem targets
    create and the nominative-trained model never saw;
  - initial w-, s-, y-: 11 slots.

### Exploratory (not a substitute test)

**Sensitivity bound.** `scripts/replication2_sensitivity.py` reran the build without writing data. Output:
`replication2_sensitivity.json`. Exact-matched slots under looser readings:

| reading | sets | exact-matched slots |
|---|---|---|
| pre-registered | 274 | 46 |
| keep `?` and `[` daughter words | 372 | 70 |
| literal independence only (bare stem vs first-run target) | 457 | 74 |
| both of the above | 594 | 105 |
| also keep ‡/**/ˣ/uncertain formations (the plan excludes them) | 774 | 154 |
| no independence rule (first-run formations included) | 800 | 188 |

No reading consistent with the plan reaches 150. The two readings that do reach it either admit
formations the plan explicitly excludes, or drop the independence rule, which admits sets whose targets
the model was trained on and would make the test circular.

Other observations:

- 38 of the 274 sets share at least one (language, form) pair with a first-run input. The plan does not
  exclude these; this is a descriptive count only.
- 146 of the 274 sets, holding 25 of the 46 matched slots, have their languages from a single branch
  (Sanskrit + Avestan, Lithuanian + Latvian, Greek dialects). The ≥ 2-language rule counts them, as it
  did in the first run. As independent evidence, the 46 is if anything an overcount.
- No target unit falls outside the training vocabulary.

**What a confirmatory replication would need.** More independent cognate sets with at least two
attested languages each: roughly three times this yield (150/46). Somewhat less might do, because
a larger set also lets more strata pass the 3-family rule. Alternatively, a design whose controls do not have to come from the evaluation words
themselves, e.g. controls matched from the training targets. That would be a new pre-registration. This
one is closed: underpowered.
