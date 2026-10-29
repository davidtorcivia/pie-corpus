# Meter census (2026-10-28)

The exact meter metric over every stored Tier 3 batch: b001–b004, t001–t033, and pilot and pilot2 for completeness. Nothing was re-realized. Each batch was computed from its stored `corpus/tier3/<batch>.jsonl` records (`pie` and `genre`) with the audited syllabifier (`pie/meter.py`). Stored batch reports, release metadata and records are unchanged.

Reproduce with `uv run python -I scripts/meter_report.py --census`. Per-line repair lists come from `scripts/meter_report.py <batch> --misses`.

## Definitions

- **Verse line.** A sentence (split at . ? !), as `realize_plans._meter` has always defined it. Each sentence is the run of plan clauses from one `"break": true` to the next. The tool checks that the two segmentations agree, and they do on every plan.
- **Metered genres.** `pie.meter.METERED_GENRES`: hymn, prayer, charm, praise, lament, wedding (the six already scored) plus **work song** (new). Work songs were not scored before, so t014 and t029 now have lines that have no stored counts.
- **exact.** Lines with exactly 8 or 11 syllables. A text that declares `"meter": 12` also scores 12, but no stored plan declares it. This is the gated number: `meter_exact>=0.90`.
- **stored exact.** The same share from the stored `meter.line_syllables`, i.e. the syllabifier each batch was realized with.
- **near.** Lines within ±1 of 8 or 11, the old `meter_fit` window (any length from 7 to 12).
- **misses / ±1 / 1 edit / neutral.** Repair columns:
  - *misses*: lines that are not exact;
  - *±1*: misses one syllable off target;
  - *1 edit*: misses where `meter_report.py` finds at least one single measured, `check_plan`-valid edit that makes the line exact;
  - *neutral*: misses where such an edit leaves the content words alone (particle nu/-ge, clause -kʷe, or a split or merge at a clause boundary).

  These columns come from realizing the stored plans in memory with the current engine. For every batch the line counts and exact counts agree with the stored records.

## Census

| batch | records | metered texts | lines | exact | exact share | stored exact | near | misses / ±1 / 1 edit / neutral |
|---|---|---|---|---|---|---|---|---|
| b001 | 250 | – | 0 | – | – | – | – | – |
| b002 | 250 | praise 30 | 32 | 6 | **0.188** | 0.219 | 0.750 | 26 / 18 / 19 / 17 |
| b003 | 250 | hymn 80, prayer 60, charm 50 | 218 | 30 | **0.138** | 0.174 | 0.615 | 188 / 104 / 133 / 110 |
| b004 | 250 | – | 0 | – | – | – | – | – |
| pilot | 145 | praise 16 | 16 | 3 | **0.188** | 0.312 | 0.875 | 13 / 11 / 11 / 9 |
| pilot2 | 140 | praise 23 | 23 | 4 | **0.174** | 0.174 | 0.652 | 19 / 11 / 11 / 6 |
| t001 | 40 | – | 0 | – | – | – | – | – |
| t002 | 40 | hymn 20, prayer 12, charm 8 | 338 | 94 | **0.278** | 0.269 | 0.796 | 244 / 175 / 203 / 139 |
| t003 | 40 | – | 0 | – | – | – | – | – |
| t004 | 40 | – | 0 | – | – | – | – | – |
| t005 | 40 | hymn 30, prayer 10 | 490 | 179 | **0.365** | 0.376 | 0.990 | 311 / 306 / 299 / 203 |
| t006 | 40 | hymn 10, charm 2, prayer 3 | 96 | 38 | **0.396** | 0.385 | 0.969 | 58 / 55 / 53 / 33 |
| t007 | 40 | – | 0 | – | – | – | – | – |
| t008 | 40 | wedding 8, lament 10, praise 14 | 267 | 78 | **0.292** | 0.262 | 0.768 | 189 / 127 / 153 / 94 |
| t009 | 30 | – | 0 | – | – | – | – | – |
| t010 | 40 | – | 0 | – | – | – | – | – |
| t011 | 40 | hymn 30, prayer 6, charm 4 | 152 | 46 | **0.303** | 0.322 | 0.987 | 106 / 104 / 92 / 65 |
| t012 | 40 | – | 0 | – | – | – | – | – |
| t013 | 40 | – | 0 | – | – | – | – | – |
| t014 | 40 | work song 2, prayer 7, charm 1 | 71 | 23 | **0.324** | 0.360 | 0.803 | 48 / 34 / 42 / 26 |
| t015 | 40 | – | 0 | – | – | – | – | – |
| t016 | 40 | charm 1, prayer 1, hymn 8 | 94 | 35 | **0.372** | 0.394 | 0.979 | 59 / 57 / 56 / 42 |
| t017 | 40 | prayer 3, charm 7 | 29 | 7 | **0.241** | 0.276 | 0.897 | 22 / 19 / 21 / 13 |
| t018 | 40 | prayer 4, charm 2 | 45 | 13 | **0.289** | 0.289 | 0.978 | 32 / 31 / 29 / 23 |
| t019 | 40 | – | 0 | – | – | – | – | – |
| t020 | 40 | prayer 2, charm 1, wedding 1, lament 2 | 60 | 18 | **0.300** | 0.283 | 0.967 | 42 / 40 / 39 / 25 |
| t021 | 40 | – | 0 | – | – | – | – | – |
| t022 | 40 | – | 0 | – | – | – | – | – |
| t023 | 40 | charm 14, lament 13 | 125 | 30 | **0.240** | 0.232 | 0.960 | 95 / 90 / 90 / 63 |
| t024 | 40 | – | 0 | – | – | – | – | – |
| t025 | 40 | – | 0 | – | – | – | – | – |
| t026 | 40 | hymn 13, prayer 13 | 159 | 54 | **0.340** | 0.365 | 0.987 | 105 / 103 / 96 / 70 |
| t027 | 40 | – | 0 | – | – | – | – | – |
| t028 | 40 | – | 0 | – | – | – | – | – |
| t029 | 40 | work song 13 | 51 | 14 | **0.275** | – | 0.686 | 37 / 21 / 24 / 16 |
| t030 | 40 | – | 0 | – | – | – | – | – |
| t031 | 40 | – | 0 | – | – | – | – | – |
| t032 | 40 | charm 14, lament 13 | 160 | 49 | **0.306** | 0.306 | 0.950 | 111 / 103 / 105 / 73 |
| t033 | 40 | wedding 13 | 154 | 17 | **0.110** | 0.110 | 0.325 | 137 / 33 / 71 / 38 |

**All batches:** 2,580 metered lines, 738 exact (**0.286**). Under the old window 2,180 (0.845) were near. No batch reaches 0.90 exact; the best are t006 (0.396), t016 (0.372) and t005 (0.365).

Of the 1,842 misses:
- 1,442 are ±1;
- 1,547 have a single measured edit that makes them exact;
- 1,065 have one that leaves the content words alone.

The worst batches have many lines far off target, which single edits will not fix:
- t033 (wedding, 0.110): lines run from 2 to 52 syllables;
- b003 (0.138): 84 lines are 2 or more syllables off;
- t008 (0.292): one 28-syllable sentence and several over 20.

These need sentences split or rewritten. `meter_report.py` lists splits at clause boundaries.

## Cadence (information only, not gated)

Exact lines were tested for the Vedic close over their last four syllables:
- 8 syllables, iambic ⏑ – ⏑ ×: 66 of 503 (0.131);
- 11 syllables, trochaic – ⏑ – ×: 23 of 235 (0.098).

Weight is computed over the whole line as one stream, across word boundaries. A syllable is heavy if its vowel is long or two or more consonants follow it; laryngeals and diphthong glides count as consonants. Laryngeals make many syllables heavy by position, so a planner aiming at cadence must count them. Nothing in the planner brief asks for cadence yet. The figures are per batch in `meter_cadence` and in the `--census` JSON.

## Syllabifier audit (why some counts moved)

The audit compared `pie/meter.py` with the handbook rules and with Vedic and Greek reflexes. It made two changes: one bug fix (1) and one new convention (2), which is a decision the lead can veto. Both are documented in the module docstring and `docs/STATUS.md`. The test cases are in `tests/test_meter.py::test_audited_counts`.

1. **A word-final laryngeal after a consonant was never counted.** The old rule required a segment on both sides of the laryngeal. Now:
   - méǵh₂ = 2 (Ved. máhi, Gk μέγα), 130 tokens, was 1;
   - h₃ésth₁ = 2 (Ved. ásthi);
   - wékʷesh₂ = 3 (Gk ἔπεα).

   Two refinements came with this fix:
   - of -CHH- only the first laryngeal vocalizes (h₃ésth₁h₂ = 2);
   - a word-initial laryngeal cluster stays consonantal like #HC (h₂Hséh₂i = 2, where the old rule counted the second laryngeal).
2. **New convention (reversible): a laryngeal after a diphthong in -y is not a syllable.** The old rule counted it. It now joins the diphthong. To revert, delete the `prev.base == "y"` branch in `pie.meter._syllabic_laryngeals`:
   - the thematic optative -oyh₁t = Ved. -et, Gk -οι: bʰéroyh₁t = 2 (Ved. bháret), gʷíh₃woyh₁t = 2 (Ved. jī́vet), both were 3;
   - dwóyh₁ = 1 (Ved. dvé);
   - dayh₂wḗr = 2 (Ved. devár-), was 3;
   - péyh₂wr̥ = 2 (Ved. pī́var-).

   This affected 423 tokens. After -w the laryngeal still vocalizes (kréwh₂s = Ved. kravíṣ 2; mléwHt = Ved. ábravīt 2), as do -RHC- (ǵénh₁tor = Ved. janitár- 3) and -CHC- (ph₂tḗr 2, dʰugh₂tḗr 3).

**Checked and unchanged:**
- #HC stays non-syllabic (h₂stḗr 1; the Indo-Iranian treatment, not the Greek prothetic vowel);
- r̥ l̥ m̥ n̥ i u are nuclei exactly as the engine marks them;
- -eh₂m and -ih₂m keep a consonantal m;
- glides are not split (dyḗws 1; no Lindeman);
- Sievers stays off by default, and its heavy-syllable test is correct.

**Effect on stored counts:** of 2,508 previously scored lines, 218 changed by 1–2 syllables (126 down, 92 up). 72 lines left 8/11 and 63 reached it. The corpus-wide exact share is about the same: 0.291 under the old counts, 0.286 now including work songs. The t026 and t032 review figures (37% and 29% exact) were made with the old syllabifier.

**Engine-form note, not a meter issue:** h₃wth₂dʰí and h₃wth₂ént (4 tokens) have a consonantal w between consonants. It probably should be *h₃uth₂-*. The meter module trusts the engine's syllabicity marks, so these count one syllable short. Reported for the engine queue; pie/realize.py and pie/morph.py were not touched.

## For repair planning

- **The gate:** `meter_exact>=0.90` is added by `scripts/realize_plans.py` to the `gates` of any batch with metered lines. It is folded into PASS/FAIL like the other gates. `pie.batch_release` needed no change.
- **Stored batches:** their recorded gates are untouched and still admit them. A batch is judged by the new gate only when it is re-realized, so every batch above with metered lines would FAIL if re-realized as it stands.
- **Order of work:** the ±1 lines (1,442) are the cheap bulk, mostly fixable by a particle, -kʷe or an epithet. The far-off lines in t033, b003, t008 and t002 need sentence splits.
