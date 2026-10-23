# Phase 8a: confirmatory evaluation of the formula search on eval-r3 (2026-10-23)

*This run scores the frozen rankings of round 2 and round 3 on the eval-r3 set, following the pre-registered protocol in `8a-eval-set.md`. It was run once. No method, setting, mapping or corpus was changed, and nothing was re-run.*

**Result:**
- **Held-out core, the headline:** only R3-c (round 3, Greek + Indo-Iranian) is above the shuffled maximum on held-out formulas, and only at k = 200: recall 0.31 (95% CI 0.12–0.56, n = 16), against a shuffled maximum of 0.06.
  - At k = 50 and 100 its CI reaches 0.
  - The result rests on round 3's homograph-twin folding. Without the folding, 2 of the 5 hits fall below rank 200, and recall is 0.19 (0.00–0.38).
  - Round 2 does not clear the baseline on the held-out core at any k: recall@200 is 0.12 (0.00–0.31, n = 16).
- **All eligible items:** both Graeco-Aryan rankings are clearly above chance at every k. Most of these items are famous formulas that round 2 may have tuned on.
- **Round 3 vs round 2:** round 3 does not beat round 2. On the held-out core, R3-c − R2 at k = 200 is +0.19 (paired CI 0.00…+0.38), so the CI does not exclude 0. On all 61 items the difference is negative at every k, also with CIs that include 0.
- **The new branch rankings:** R3-a (≥ 3 witnesses) and R3-b (other branch pairs) find nothing held out: 0 of 2 and 0 of 8 items.

## 1. Integrity checks
- **Eval set hash:** sha256 of `data/research/formulas/eval-r3/formulas-eval.jsonl` = `1f4668366af9f5c6c2d127f6c7e395c88bc4b2be9c56aa996d4625b71fba2e0f`. That is the value recorded in `8a-eval-set.md`, so it **matches**. The scoring script checks it again before generating and before scoring.
- **Code:**
  - Commit `6cdc57b1e3301e366d571fd7fef725fb327be56d`.
  - `git status` shows no change to `pie/formula_search.py`, `pie/formula_search_multi.py`, `scripts/formula_search.py` or `final_setting.json`.
  - Other files in the working tree were already modified or untracked before this run (`pie/morph.py`, `pie/tier2_secure.py`, `tests/test_morph_r2_fixes.py`). Tier-2 files changed during the run (`corpus/tier2/fame.jsonl`, `scripts/build_tier2.py`, `tests/test_tier2_secure.py`). None of them is imported by the search code, and this run wrote none of them.
- **Reproduction:** the regenerated rankings reproduce the saved candidate files exactly, in pairs, order and scores:
  - R2, filtered by `known_pairs`, reproduces `candidates.jsonl` (200/200).
  - R3-a, R3-b and R3-c reproduce `candidates-r3-{a,b,c}.jsonl` (100/100 each).
  - Scoring was gated on these checks.
- **New files:**
  - `scripts/score_eval_r3.py`: `generate` runs the frozen code, `score` applies the protocol.
  - `tests/test_score_eval_r3.py`.
  - `data/research/formulas/confirmatory-r3.json`.
  - Any output the search code would write was redirected to a scratch directory. It wrote nothing there either.

## 2. Rankings
Every ranking is the complete list the frozen code produces, not a top 100. The JSON stores the top 200 of each, plus the rank of every `pairs_root` pair of every eligible item where that pair ranks at all.

| ranking | what it is | how it was produced | ranked pairs |
|---|---|---|---:|
| **R2** | round 2's final setting (`final_setting.json`) on RV pāda × Homer line | `Env.rank_full(final_cfg)` | 1,081 |
| **R3-c** | round 3, exactly Greek + Indo-Iranian witnesses | `r3_rank(r3, ALL_R3)` (defaults as in `run_round3`) → `ranking_class == "c"` → root-group dedup and homograph-twin folding, copied verbatim from `write_candidates_r3` without its top-100 cap | 702 |
| **R3-a** | round 3, ≥ 3 witnesses | same, class a | 386 |
| **R3-b** | round 3, two witnesses, not Greek + Indo-Iranian | same, class b | 1,871 |

**Level used: root group.** All four rankings are lists of distinct root-group pairs: counts are made at lexeme level, then deduplicated by root group. Hits are therefore matched through `pairs_root`, as the protocol prescribes for a root-group ranking, and an item's rank is the minimum over its pairs.
- Strictness check: some of these hits are not the exact lexeme pair. Of the hits at k ≤ 200, the ranked lexeme pair is one of the item's `pairs` (lexeme ids) in:
  - R2: 15 of 19
  - R3-c: 12 of 17
  - R3-a: 3 of 5
  - R3-b: 1 of 1
- The other hits match at root-group level only.

## 3. Readings I had to choose (the most conservative, stated in advance of scoring)
- **Eligibility for R3-a and R3-b.** The protocol's rule ("`phrase_branches` contains both X and Y") is written for two-branch rankings. I applied it to the 8 branches that have a corpus; Tocharian and Phrygian have none.
  - R3-a: ≥ 3 covered branches, 21 items.
  - R3-b: the item contains some covered branch pair other than Greek + Indo-Iranian, 44 items. This includes the ≥ 3-branch items, so the denominator is the larger one.
  - The alternative reading, exactly two branches and not Greek + Indo-Iranian, gives 23 items (6 held out). R3-b would still hit only 1.
- **Corpus-confirmed subset.**
  - R2 and R3-c: `phrase_corpora_confirmed` includes an Indo-Iranian corpus and a Greek corpus (any of rv/av/avesta and homer/glaux). This is the protocol's branch-level wording, so I did **not** restrict R2 to rv + homer.
  - R3-a: confirmed in ≥ 3 covered branches.
  - R3-b: confirmed in an eligible branch pair.
  - Corpus → branch: rv, av, avesta → Indo-Iranian; homer, glaux → Greek; latin → Italic; edda, oe → Germanic; hittite → Anatolian.
- **Homograph twins.** Round 3's ranking folds a pair into a kept pair when it has identical per-corpus counts under a homograph entry. This is the frozen definition of rankings a/b/c, and it is what the candidate files contain, so it is the primary ranking here.
  - A folded pair has no rank of its own, and I count it as not ranked.
  - Folding also moves every later pair up. In R3-c, five items change hit status at some k:

| item | held out | rank folded | rank unfolded | effect of folding |
|---|---|---|---|---|
| "Dawn shines" | no | not ranked (folded into the *bʰeh₂-* 'speak' + *h₂ews-* twin) | 36 | loses a hit at k = 50, 100 and 200 |
| "drive the cows" | **yes** | 86 | 101 | gains a hit at k = 100 |
| "sun, watcher of the whole world" | **yes** | 185 | 216 | gains a hit at k = 200 |
| "born of Sky/Zeus" (contested) | **yes** | 200 | 233 | gains a hit at k = 200 |
| "clothed in a cloud" | no | 178 | 209 | gains a hit at k = 200 |

  - Folding changes no hit in R3-a or R3-b.
  - R3-c unfolded, for comparison only (the ranks are stored per pair in the JSON, under `unfolded_subsets`):

| subset | recall@50 | recall@100 | recall@200 |
|---|---|---|---|
| all | 0.11 (0.03–0.20), n = 61 | 0.20 (0.10–0.31), n = 61 | 0.25 (0.15–0.36), n = 61 |
| held-out core | 0.12 (0.00–0.31), n = 16 | 0.12 (0.00–0.31), n = 16 | 0.19 (0.00–0.38), n = 16 |
| corpus-confirmed | 0.12 (0.05–0.21), n = 57 | 0.21 (0.12–0.32), n = 57 | 0.26 (0.16–0.39), n = 57 |
| uncontested | 0.08 (0.02–0.16), n = 50 | 0.18 (0.08–0.30), n = 50 | 0.24 (0.14–0.36), n = 50 |
- **Missing pairs.** The 2 primary items with no `pairs_root` stay in the denominators as misses.
- **Shuffled baseline.**
  - Seeds 0–4. Round 3 itself used 3 seeds; the protocol says 5.
  - It is the same code with PIE labels permuted across tokens within each corpus: `Env.rank_full(cfg, seed)` for R2, `r3_rank(..., seed=s)` with the same class split and folding for R3.
  - Each seed's ranking is scored on the same items.
- **Headline subset.** The held-out core is the headline for *every* ranking. Round 2's final setting was tuned on E2 (formulas.jsonl plus West silver pairs). Round 3 inherits that setting and mapping, and its sanity checks used E2.

## 4. Results (primary items; recall with 95% bootstrap CI, 2,000 resamples, seed 0)
`n` = eligible items in the cell. The baseline columns give the shuffled recall as mean / maximum over 5 seeds, for the same items.

### R2: round 2 final setting, RV + Homer (61 eligible)
| subset | recall@50 | recall@100 | recall@200 | shuffled @50 / @100 / @200 (mean / max) |
|---|---|---|---|---|
| all | 0.18 (0.08–0.28), n = 61 | 0.26 (0.15–0.38), n = 61 | 0.31 (0.20–0.43), n = 61 | 0.00/0.00 · 0.00/0.02 · 0.01/0.03 |
| **held-out core** | 0.06 (0.00–0.19), n = 16 | 0.12 (0.00–0.31), n = 16 | 0.12 (0.00–0.31), n = 16 | 0.00/0.00 · 0.00/0.00 · 0.01/0.06 |
| corpus-confirmed | 0.19 (0.10–0.30), n = 57 | 0.28 (0.17–0.40), n = 57 | 0.33 (0.21–0.44), n = 57 | 0.00/0.00 · 0.00/0.02 · 0.01/0.04 |
| uncontested | 0.20 (0.10–0.32), n = 50 | 0.30 (0.18–0.44), n = 50 | 0.34 (0.22–0.48), n = 50 | 0.00/0.00 · 0.00/0.02 · 0.02/0.04 |

### R3-c: round 3, Greek + Indo-Iranian (61 eligible)
| subset | recall@50 | recall@100 | recall@200 | shuffled @50 / @100 / @200 (mean / max) |
|---|---|---|---|---|
| all | 0.10 (0.03–0.18), n = 61 | 0.20 (0.10–0.31), n = 61 | 0.28 (0.16–0.39), n = 61 | 0.00/0.02 · 0.01/0.02 · 0.01/0.02 |
| **held-out core** | 0.12 (0.00–0.31), n = 16 | 0.19 (0.00–0.38), n = 16 | 0.31 (0.12–0.56), n = 16 | 0.00/0.00 · 0.01/0.06 · 0.01/0.06 |
| corpus-confirmed | 0.10 (0.04–0.19), n = 57 | 0.21 (0.10–0.32), n = 57 | 0.30 (0.17–0.42), n = 57 | 0.00/0.02 · 0.01/0.02 · 0.01/0.02 |
| uncontested | 0.06 (0.00–0.14), n = 50 | 0.18 (0.08–0.30), n = 50 | 0.26 (0.14–0.38), n = 50 | 0.00/0.02 · 0.00/0.02 · 0.01/0.02 |

### R3-a: round 3, ≥ 3 witnesses (21 eligible)
| subset | recall@50 | recall@100 | recall@200 | shuffled @50 / @100 / @200 (mean / max) |
|---|---|---|---|---|
| all | 0.10 (0.00–0.24), n = 21 | 0.14 (0.00–0.29), n = 21 | 0.24 (0.10–0.43), n = 21 | 0.02/0.05 · 0.02/0.05 · 0.08/0.14 |
| **held-out core** | 0.00 (0.00–0.00), n = 2 | 0.00 (0.00–0.00), n = 2 | 0.00 (0.00–0.00), n = 2 | 0.00/0.00 · 0.00/0.00 · 0.10/0.50 |
| corpus-confirmed | 0.00 (0.00–0.00), n = 1 | 0.00 (0.00–0.00), n = 1 | 1.00 (1.00–1.00), n = 1 | 0.00/0.00 · 0.00/0.00 · 0.20/1.00 |
| uncontested | 0.11 (0.00–0.28), n = 18 | 0.17 (0.00–0.33), n = 18 | 0.28 (0.11–0.50), n = 18 | 0.02/0.06 · 0.02/0.06 · 0.09/0.17 |

### R3-b: round 3, other two-witness pairs (44 eligible)
| subset | recall@50 | recall@100 | recall@200 | shuffled @50 / @100 / @200 (mean / max) |
|---|---|---|---|---|
| all | 0.02 (0.00–0.07), n = 44 | 0.02 (0.00–0.07), n = 44 | 0.02 (0.00–0.07), n = 44 | 0.00/0.02 · 0.00/0.02 · 0.01/0.02 |
| **held-out core** | 0.00 (0.00–0.00), n = 8 | 0.00 (0.00–0.00), n = 8 | 0.00 (0.00–0.00), n = 8 | 0.00/0.00 · 0.00/0.00 · 0.00/0.00 |
| corpus-confirmed | 0.12 (0.00–0.38), n = 8 | 0.12 (0.00–0.38), n = 8 | 0.12 (0.00–0.38), n = 8 | 0.00/0.00 · 0.00/0.00 · 0.05/0.12 |
| uncontested | 0.00 (0.00–0.00), n = 39 | 0.00 (0.00–0.00), n = 39 | 0.00 (0.00–0.00), n = 39 | 0.00/0.00 · 0.00/0.00 · 0.01/0.03 |

R3-b's single hit is the contested Hittite–Slavic "heaven and earth", at rank 2. Its Slavic witness is the NT, a translation.

### Paired comparison: R3-c − R2, on the same 61 items (paired bootstrap, 2,000 resamples, seed 0)
| subset | n | Δ recall@50 | Δ recall@100 | Δ recall@200 |
|---|---:|---|---|---|
| all | 61 | −0.08 (−0.20…+0.03) | −0.07 (−0.18…+0.05) | −0.03 (−0.15…+0.08) |
| **held-out core** | 16 | +0.06 (0.00…+0.19) | +0.06 (0.00…+0.19) | +0.19 (0.00…+0.38) |
| corpus-confirmed | 57 | −0.09 (−0.21…+0.04) | −0.07 (−0.19…+0.05) | −0.04 (−0.16…+0.09) |
| uncontested | 50 | −0.14 (−0.26…−0.02) | −0.12 (−0.24…0.00) | −0.08 (−0.18…+0.02) |

Of these 12 cells, one CI excludes 0: R3-c is *worse* on uncontested items at k = 50. The 12 cells were not corrected for multiplicity.

## 5. Held-out core items (23): best rank per ranking
"not eligible" = the item's `phrase_branches` do not meet the ranking's eligibility rule. "not ranked" = none of its `pairs_root` appears in the ranking at all.

| item | label | R2 | R3-c | R3-a | R3-b |
|---|---|---|---|---|---|
| r3e-f1c5d30a44 | Dawn being born (uṣáso jā́yamānāḥ ~ Ἠὼς ἠριγένεια) | not ranked | not ranked | not eligible | not eligible |
| r3e-3ca93d7504 | Dawn rises | 943 | not ranked | not eligible | not eligible |
| r3e-9f441685b0 | bear/carry the word (= speak) | not ranked | not ranked | 364 | not ranked |
| r3e-ba04b21ab8 | born of Sky/Zeus (divojā́- ~ διογενής), contested | 341 | **200** | not eligible | not eligible |
| r3e-77521f31f7 | carry / spread fame | 307 | not ranked | not eligible | not eligible |
| r3e-71d58d197e | come, go! (pleonastic imperatives) | not ranked | not ranked | not eligible | not eligible |
| r3e-51a76d5a12 | divine Dawn (uṣā́s devī́) | **20** | **38** | not eligible | not eligible |
| r3e-247480293b | drive (off) the cows | **63** | **86** | not ranked | not ranked |
| r3e-6213df3e9e | give a gift (figura etymologica) | not eligible | not eligible | not eligible | not ranked |
| r3e-d73c03f1b4 | go together = heal (saman renna ~ sám ṛ-) | not eligible | not eligible | not eligible | not ranked |
| r3e-988d3d0dd0 | golden apple(s) | not eligible | not eligible | not eligible | not ranked |
| r3e-74babd1ff2 | good spirit (μένος ἠΰ ~ vohu manah), contested | 383 | **22** | not eligible | not eligible |
| r3e-705741da60 | great father (maháḥ pitúḥ ~ πατὴρ μέγας) | 842 | not ranked | not eligible | not eligible |
| r3e-65f6946052 | great name (= great fame) | not ranked | not ranked | not eligible | not eligible |
| r3e-eda6ce1cfc | have/take a name (= fame) | not eligible | not eligible | not eligible | not ranked (no `pairs_root`) |
| r3e-3e74be1eaa | horses of the sun | 468 | 532 | not eligible | not eligible |
| r3e-cf3d2783e2 | make the fury dwindle (mināti manyúm ~ μινύθει μένος) | not ranked | not ranked | not eligible | not eligible |
| r3e-d7e5e808d5 | moulded and painted (Tocharian ~ Latin) | not eligible | not eligible | not eligible | not eligible |
| r3e-83d65a183f | put the fire (on the altar) | not eligible | not eligible | not eligible | not ranked |
| r3e-cf0093b7cb | put/place the word | 767 | not ranked | not eligible | not eligible |
| r3e-56b0f26d45 | sun, watcher of the whole world | not ranked | **185** | not eligible | not eligible |
| r3e-c42817e76d | ten months (gestation) | not eligible | not eligible | not eligible | not ranked |
| r3e-de8a68bd45 | utter a word solemnly | not ranked | not ranked | not eligible | not eligible |

Bold = hit at k ≤ 200. R3-c's 5 held-out hits include 2 contested items, "born of Sky" (at exactly rank 200) and "good spirit". R2's 2 held-out hits are both also hit by R3-c.

## 6. Secondary table: other lexical items (not primary; descriptive only)
There are 87 lexical items that fail `primary`. Many have no phrase in two branches: 48 have empty `phrase_branches`. So eligibility here uses `branches`, the branches where the cognates are attested, with the same rules as above. Items without a two-root pair stay in as misses.

An item can have several exclusion reasons and is counted under each.

| ranking | subset | recall@50 | recall@100 | recall@200 |
|---|---|---|---|---|
| R2 | all | 0.03 (0.00–0.08), n = 60 | 0.05 (0.00–0.12), n = 60 | 0.07 (0.02–0.13), n = 60 |
| R2 | compound/name (phrase in < 2 branches) | 0.04, n = 51 | 0.04, n = 51 | 0.06, n = 51 |
| R2 | single root | 0.00, n = 12 | 0.00, n = 12 | 0.00, n = 12 |
| R2 | rejected by source | 0.17, n = 6 | 0.17, n = 6 | 0.17, n = 6 |
| R2 | function word | 0.00, n = 3 | 0.33, n = 3 | 0.33, n = 3 |
| R3-c | all | 0.02 (0.00–0.05), n = 60 | 0.03 (0.00–0.08), n = 60 | 0.05 (0.00–0.10), n = 60 |
| R3-c | compound/name | 0.02, n = 51 | 0.04, n = 51 | 0.06, n = 51 |
| R3-c | single root | 0.00, n = 12 | 0.00, n = 12 | 0.00, n = 12 |
| R3-c | rejected by source | 0.17, n = 6 | 0.17, n = 6 | 0.17, n = 6 |
| R3-c | function word | 0.00, n = 3 | 0.00, n = 3 | 0.00, n = 3 |
| R3-a | all | 0.00, n = 24 | 0.00, n = 24 | 0.00, n = 24 |
| R3-b | all | 0.00, n = 45 | 0.00, n = 45 | 0.00, n = 45 |

Hits at k ≤ 200, in R2 and R3-c:
- "master of the house" (*déms pótis*)
- "having yoked horses" (a name; rejected by its source)
- "fallen from the sky"
- R2 only: "hear me!" (a function-word pair)

The per-reason rows for R3-a and R3-b are all zero and are in the JSON.

## 7. Conclusion
- **Better than chance:** yes, for the two Graeco-Aryan rankings on the full eligible set.
  - R2 and R3-c rank 0.26–0.34 of the eligible primary items in their top 200, depending on the subset.
  - The shuffled maxima are 0.02–0.04, and every CI lower bound is above them.
  - Most of these items are in formulas.jsonl or E2, which round 2 tuned on, so this result is not independent.
- **On the held-out core (n = 16), the protocol's headline:**
  - Only R3-c at k = 200 is above the shuffled maximum: 5/16 = 0.31, CI 0.12–0.56, against a shuffled maximum of 0.06. That lower bound is 2 hits in 16, and the shuffled maximum is 1 hit in 16.
  - At k = 50 and 100, and for R2 at every k, the CI reaches 0.
  - The result is fragile:
    - It rests on round 3's homograph-twin folding. Unfolded, 2 of the 5 hits (ranks 185 and 200) fall below rank 200, and the CI reaches 0 (0.19, 0.00–0.38).
    - Two of the five hits are contested items, one of them at exactly rank 200.
  - So the held-out core gives at most weak evidence that the search finds formulas it was not tuned on.
- **Round 3 vs round 2:** the data do not show that round 3 beats round 2.
  - On the held-out core, R3-c is ahead (+0.19 at k = 200), but the paired CI includes 0.
  - On all items it is behind at every k, with CIs that include 0.
  - On uncontested items at k = 50 it is significantly behind (−0.14). That is one of 12 uncorrected comparisons.
- **The new branch rankings:**
  - R3-b (other two-branch pairs) finds 1 of 44 eligible items, at the shuffle level.
  - R3-a (≥ 3 witnesses) finds 5 of 21. Its CI lower bound (0.10) is below the shuffled maximum (0.14).
  - Neither finds any held-out item (n = 2 and 8).
  - So adding branches has not yet produced evidence of finding inherited formulas outside Graeco-Aryan.
