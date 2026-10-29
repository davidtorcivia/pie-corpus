# Formula discovery, round D1: results, part 1 (2026-10-28)

Pre-registration: `docs/research/discovery-r1-preregistration.md` (commit d29b672). Script:
`scripts/discovery_d1.py` (subcommands `extract`, `count`, `freq`, `control`, `diagnose`, `packet`).
Index: `data/research/8c/search-index/corpora.sqlite` as rebuilt after corpus-quality batch 1 (not rebuilt here).

**Outcome: the positive control fails. Recall of the 120 multi-branch known formulas among the candidates
is 0.100 (12/120), below the pre-registered 0.30. Under the pre-registration the candidate list is reported
as uninformative and D1 stops here.** No candidate was read. The review set, the decoys, the packet and the
key were not built (`packet` was never run), and no blind review should be dispatched for D1.

## Implementation decisions (not fixed by the pre-registration; set before any candidate was computed)

- **Branches.** The 8 pre-registered branches. The index's Baltic and Slavic are merged into Balto-Slavic.
  Albanian and Tocharian are left out. Units: 2,310,589 (Greek 934,202, Balto-Slavic 433,113, Celtic
  368,664, Indo-Iranian 276,306, Germanic 199,883, Anatolian 47,009, Armenian 30,350, Italic 21,062).
- **Keys and window.** As in `collocates_8c.py`, a word's keys are `root_ids ∪ root_groups`, and the window
  is a distance of ≤ 4 in the unit's `words` list. That list holds content words only, mapped and unmapped;
  the index has already dropped function words. A pair is two keys on different words, counted once per
  unit. E_b = n_b(x)·n_b(y)/N_b, where n_b is the number of units that contain the key in branch b,
  recomputed for each shuffled index. The index has 6,580,692 keyed words, 7,105 keys and 3,298 root groups
  (`group_of`, with group splits). On every keyed word (all 6,580,692 carry `root_ids`), the payload's `root_groups` equal `{group_of(r) for r in root_ids}`; the check runs in `extract`.
  - Checked against `collocates_8c.py --pair` on horse + swift: Greek O = 70 and Indo-Iranian O = 8 in both
    tools.
- **Same-group pairs** are dropped: a lexeme with its own root group on another word is not a two-word phrase.
- **Shuffle.** Within each corpus, the key sets of keyed word slots are permuted with seeds 0–19. Unkeyed
  slots and all positions stay fixed. This keeps unit size, the number of keyed words per unit, and each
  corpus's root token frequencies.
- **Null threshold.** The cross-branch score (the minimum over qualifying branches of log₂ O/E) is pooled
  over every null-qualifying pair in all 20 shuffles, after exclusions. The threshold is the 99th
  percentile of that pool. A real pair is a candidate if its score is strictly greater than the threshold.
- **Exclusions.** Exclusions are applied identically to the real and null runs before the threshold.
  - **Function-word ids:** lexicon pos ∈ {pron, particle, det, conj, intj, adv, prefix, suffix, infix}, any
    `closed:*` id, and the copula \*h₁es- (root group). The copula was added from a top-130 key frequency
    dump made before any candidate was computed (`data/research/discovery/d1/function-extra.json`). This
    gives 125 function keys.
  - **Top-50:** the 50 root groups with the most units across the 8 branches. A pair is excluded when both
    sides' groups are in that set. The list is in `summary.json`.
- **Positive-control match.** The control list is the 120 witness-scan rows with `class = multi-branch` and
  source West or Watkins; the 9 `formula_menu.json (core)` rows are not in formulas.jsonl. A formula counts
  as recovered if, for any of its specs, a candidate pair has one side in A′ and the other in B′. Here A′
  and B′ are each spec id together with its root group. The whole candidate list is used, before any
  novelty filter.

## Counts

| | real | null (per shuffle, mean; range) |
|---|---|---|
| distinct key pairs in window | 1,247,526 | ≈ 1,490,000 |
| qualifying (O ≥ 3, O/E ≥ 3 in ≥ 2 branches), before exclusions | 1,370 | 90 (71–105) |
| qualifying, after exclusions | 1,322 | 82 (65–97) |
| candidates (score > null 99th pct) | **247 key pairs = 176 root-group pairs** | — |

**Null score distribution.** The pool holds 1,645 null-qualifying pairs over 20 shuffles, after exclusions.
Their log₂ min O/E has these quantiles:

| percentile | 1 | 5 | 25 | 50 | 75 | 90 | 95 | 99 | 99.9 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| log₂ O/E | 1.59 | 1.60 | 1.69 | 1.80 | 2.00 | 2.27 | 2.49 | **3.05** | 3.51 | 4.28 |

The threshold is therefore log₂ = 3.048, so a candidate needs O/E > 8.27 in every qualifying branch. The
null pairs are mostly O = 3–5 on rare keys. The real index has about 16 times as many qualifying pairs as
a shuffle, so the real list is far from noise. It is, however, dominated by pairs that do not include the
known formulas.

## Positive control

**Recall 12/120 = 0.100**: lexical 8/102, partial-lexical 4/18. The 12 rows rest on three distinct pairs:

- **fame + imperishable** (\*ḱléwos n̥dʰgʷʰitóm): Indo-Iranian O = 3, O/E 11.5; Greek O = 4, O/E 9.2. Seven
  rows depend on it: imperishable-fame, imperishable-fame-be-dative, imperishable-fame-get-nominative,
  god-grant-imperishable-fame, have-imperishable-fame-schema, west_ch10_f01 and west_ch02_f01.
- **raw + eat** (west_ch02_f08, raw-eaters): Indo-Iranian O = 4, O/E 16.3; Greek O = 47, O/E 12.7.
- **earth + cloud**, at root-group level: west_ch09_f01, f02, f03 and west_ch08_f08 ("heaven and earth").
  These count only through a secondary spec. The qualifying branches are Balto-Slavic (O/E 12.5) and
  Anatolian (21.1), not the formula's attested branches (Indo-Iranian, Anatolian). Under a stricter rule
  requiring the hit to fall in the attested branches, recall would be 8/120.

**Missed (108).** Each formula's best spec pair is classed by the rule step that drops it
(`data/research/discovery/d1/control-diagnostics.json`, from `discovery_d1.py diagnose`). The rows are
120 formulas over 65 distinct best pairs; for example, 14 dragon-slaying rows share slay + serpent.

| step that drops it | formulas | distinct pairs |
|---|---|---|
| O ≥ 3 in ≥ 2 branches, but O/E ≥ 3 in at most one | 68 | 38 |
| O ≥ 3 in at most one branch | 19 | 11 |
| qualifies (≥ 2 branches), score ≤ null threshold | 18 | 10 |
| pair never co-occurs within the window | 3 | 3 |
| recovered | 12 | 3 |

Examples:

| formula | branch: O, O/E | what fails |
|---|---|---|
| swift horses | Greek 70, ×15.5; Indo-Iranian 8, ×5.2 | score 2.38 < 3.05 |
| dems-potis | Indo-Iranian 6, ×3.5; Greek 14, ×3.9 | below the threshold |
| hero slays serpent (14 rows) | Indo-Iranian 36, ×10.5; Greek 4, ×1.2 | Greek O/E < 3 |
| great fame | Indo-Iranian 17, ×1.8; Greek 66, ×3.6 | Indo-Iranian O/E < 3 |
| men and cattle | Indo-Iranian 20, ×2.7; Italic 9, ×20 | Indo-Iranian O/E < 3 |
| famous name | Indo-Iranian 3, ×6.1; Greek 13, ×1.3; Celtic 10, ×2.4 | |

Two rows (west_ch05_f14, west_ch04_f26) have a qualifying pair that the function-word / top-50 rule
excludes. The full per-formula lists of recovered and missed rows, with reasons, are in `summary.json` and
`control-diagnostics.json`.

**Sensitivity (diagnostic only; it does not change the outcome).** Without the null threshold, the rule
"O ≥ 3 and O/E ≥ 3 in ≥ 2 branches" alone would recover 30/120 = 0.25. That is still under 0.30.

## Why the list is uninformative

These are observations for the design of a later round. Nothing below was tested here.

1. **O/E is diluted by the base rate per branch.** Greek is 67% later prose (grc-late, 625k of 934k units), and
   Indo-Iranian is 75% epic Sanskrit (sa-ep). A formula that is frequent in Homer or the Rigveda is rare
   relative to these large prose and epic bases, so its branch O/E falls to 1–3. Of the Greek branches that
   have O ≥ 3 for a known formula, only 49% reach O/E ≥ 3; the median is 2.5. Of the Germanic branches,
   0 of 4 do. "Within a branch, every corpus counts" is pre-registered, and that is what produces this
   effect.
2. **O and E are defined on different spans.** O needs the pair within ±4 words, but E is a unit-level
   co-occurrence expectation. Long units (prose sentences, byliny passages, Hittite paragraphs) raise E
   without raising O. This favours short-unit corpora (dainas, Hittite) and rare keys.
3. **The null threshold is strict for two-branch formulas.** The 99th percentile of pooled null scores is
   O/E > 8.3 in every qualifying branch. A known formula usually has one strong branch and one weaker one
   (swift horses: ×15.5 and ×5.2).
4. **Recall is counted in formula rows, not distinct phrases.** The 120 rows collapse to 65 best pairs, and
   one pair can decide up to 14 rows. Recall in distinct pairs is 3/65.

## What was not done (by rule)

- There is no review set, no decoys, no packet (`docs/research/discovery/d1-packet.jsonl` does not exist)
  and no key (`data/audits/keys/d1-key.json` was not written).
- Novelty and Tier 2 linkage were not computed. The `packet` subcommand is in the script but was not run.
- Candidates were written only to the binary cache (`run-real.npz`) and were never printed or read. The
  `control` and `diagnose` steps print only counts and known-formula ids.

## Runtime (32-core machine)

| step | time |
|---|---|
| extract (one pass over 2.31M units, 24 processes) | 15 s |
| real count | 20 s |
| 20 shuffles (10 processes, ~25 s each) | 52 s wall |
| control | < 1 s |
| diagnose | ~25 s |

## Files

- Committed, in `data/research/discovery/d1/`:
  - `summary.json`: parameters, threshold, null quantiles, counts, and the positive control with
    recovered and missed ids.
  - `control-diagnostics.json`: per-branch O, E, O/E for each control formula.
  - `extract-stats.json`, `count-stats.json`.
  - `keys.json`: key, group and corpus tables.
  - `function-extra.json`.
- Gitignored and reproducible with `discovery_d1.py extract` and `count`: `words.npz` (266 MB) and the
  per-run `run-*.npz` and `real-pairs.npz`.
