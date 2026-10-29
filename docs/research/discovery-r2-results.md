# Formula discovery, round D2: results (2026-10-28)

Pre-registration: `docs/research/discovery-r2-preregistration.md` (commit 4dac0a3). Script:
`scripts/discovery_d2.py` (subcommands `extract`, `count`, `split`, `tune`, `test`, `packet`).
Index: `data/research/8c/search-index/corpora.sqlite` as it stood (mtime 2026-10-28 22:41, 2,354,298,880 bytes),
the same index as D1. The D2 extract is identical to D1's cache in every array and in key numbering.

**Outcome: the success criterion fails. Test-half recall is 0.250 (8/32), below the pre-registered 0.30.
The false rate is 0.138, within the ≤ 0.20 cap. Under the pre-registration, the D2 candidate list is reported as
uninformative, and D2 stops here.** No candidate was read. The review set, decoys, packet and key were not built.
`packet` refuses to run when the criterion is not met, so its dry run was not run either.

## Implementation decisions

These were fixed in the script header and committed in b8026a6, before any D2 count was computed.

- **Layers.** These are the Stage C-S builder's layer function as applied to this index.
  `scripts/search_corpora.py` calls `build_8c_stageCS.prepare` and `Classifier` and stores each unit's
  `layer_status`: "included" for the Stage C-S comparable layers, including the thin-corpus amendment, and "excluded"
  otherwise. A layer is (corpus, layer_status), and both statuses are layers, because the pre-registration's own
  list names "later Greek" as a stratum. Corpora are not merged; Rigveda and Atharvaveda, for example, are separate
  rows in the Stage C-S table. Genre classes do not split layers, because the builder keeps the layer filter and the
  genre classes as separate rules. D1's 8 branches and its units are kept. There are 40 layers:

  | branch | layer (units / keyed words) |
  |---|---|
  | Indo-Iranian | rv 39,832 / 77,240; av 13,800 / 43,683; ae 16,466 / 31,143; sa-ep 206,208 / 474,412 (all included) |
  | Greek | hom 27,760 / 73,659; grc included 76,136 / 214,068; grc excluded 205,528 / 872,652; grc-late (excluded) 624,778 / 2,923,013 |
  | Italic | lat 18,841 / 44,347; xum 2,221 / 1,375 |
  | Celtic | sga incl 21,323 / 27,356, excl 18,901 / 15,876; sga-gl (excl) 6,958 / 6,073; mga incl 61,884 / 75,769, excl 88,656 / 108,214; ga-early incl 2,053 / 2,284, excl 125,521 / 243,666; cy incl 16,843 / 11,748, excl 26,525 / 20,599 |
  | Germanic | non 12,591 / 13,856; menota incl 95,154 / 352,311, excl 29,105 / 136,763; icepahc incl 15,996 / 48,069, excl 6,345 / 28,979; ang incl 11,726 / 19,504, excl 3,760 / 4,095; rea-goh incl 190 / 1,018, excl 17,950 / 107,648; rea-osx incl 5 / 40, excl 7,061 / 21,322 |
  | Balto-Slavic | vuk 146,775 / 135,621; byliny 149,640 / 154,408; dainos 79,771 / 44,793; lv 751 / 1,636; orv 14,570 / 21,389 (all included); ccmh (excl) 41,606 / 73,764 |
  | Armenian | xcl incl 20,633 / 56,716, excl 9,717 / 26,896 |
  | Anatolian | hit incl 46,338 / 63,447, excl 671 / 1,240 |

  The full list is in `data/research/discovery/d2/layers.json`.
- **Window-based O and E.** The window is D1's: two keyed content-word slots of one unit at distance ≤ 4 in
  the unit's `words` list. Per layer L:
  - W_L is the number of such slot pairs, S_L is the number of keyed slots, and n_L(x) is the number of slots that carry key x.
  - O_L(x, y) is the number of slot pairs with x on one slot and y on the other. This is an event count: each
    attestation adds 1, so a single attestation gives O = 1. As in D1, same-group pairs are dropped.
  - E_L = 2·n_L(x)·n_L(y)·W_L / S_L², the expected O_L when key sets are placed on slots independently at their
    layer frequencies.

  The within-layer shuffle permutes key sets among the keyed slots of each layer. The check: over all
  different-group pairs, Σ O / Σ E is 0.998 on every shuffle (0.9979–0.9986; per layer 0.98–1.12, with the high
  end on the tiny layers). On the real index it is 0.983. D1's E was unit-level while its O was window-level, so the identity was not expected to hold there, and it was not checked.
- **Branch rule.** A pair qualifies in a layer if O_L ≥ min O and O_L/E_L ≥ min O/E. It qualifies in a branch if it
  qualifies in any of that branch's layers, and the branch's log₂ O/E is the maximum over its qualifying layers.
  The pair's score is the minimum over its qualifying branches, of which there must be at least 2. The rule is the
  same for real and null runs.
- **Exclusions.** D1's frozen function-word list (125 keys, including `function-extra.json`) and D1's top-50
  root groups (the list in D1's `summary.json`, asserted equal) are applied identically before the threshold.
- **Threshold.** The threshold is the given percentile of the null scores, pooled over the 20 shuffles (seeds 0–19)
  after exclusions. A candidate's score must be strictly greater.
- **Items.** The items are the 65 distinct best pairs of D1's control diagnostics: 62 distinct key pairs, plus 3
  formulas whose spec pairs a word with itself (mortal + self, brother + self, wish + self, all "never co-occurs" in
  D1). Same-group pairs are dropped, so these 3 cannot be recovered. They fall 2 in tune and 1 in test.
  - **Split.** The hash string is the two key ids sorted and joined by "|" (`<id>|<id>` for a self item). Items are
    sorted by the sha256 hex digest; the first 33 are tune and the last 32 are test (`split.json`).
  - **Recovery.** An item is recovered if any candidate key pair has the item's root-group pair, since the
    pre-registered unit is the root-group pair.
  - **Shared group pair.** Two items share one group pair: name + fame (`h1nomn|kjlewos` and
    `h1nomn|kjlew-hear`). Both are in test, so there is no tune-to-test leak.
- **False rate.** For each grid cell, the mean over the 20 seeds of null candidates (key pairs after exclusions,
  score > threshold) divided by the real candidates (key pairs).
- **Tune choice.** Among the cells with false rate ≤ 0.20, the cell with the highest tune recall is chosen. Ties go
  to the lower false rate, then the higher percentile, then the higher O/E, then the higher min O.

## Tune grid (33 tune items; `tune-grid.json`)

| min O | O/E | pct | threshold log₂ | real candidates | null candidates (mean) | false rate | tune recall |
|---|---|---|---|---|---|---|---|
| **2** | **2** | **95** | **2.278** | **3,086** | **427.4** | **0.138** | **0.394 (13/33)** |
| 2 | 2 | 99 | 2.952 | 1,472 | 85.5 | 0.058 | 0.242 (8/33) |
| 2 | 3 | 95 | 2.824 | 1,820 | 124.0 | 0.068 | 0.333 (11/33) |
| 2 | 3 | 99 | 3.464 | 885 | 24.8 | 0.028 | 0.121 (4/33) |
| 2 | 4 | 95 | 3.213 | 1,221 | 48.1 | 0.039 | 0.152 (5/33) |
| 2 | 4 | 99 | 3.778 | 658 | 9.7 | 0.015 | 0.121 (4/33) |
| 3 | 2 | 95 | 1.881 | 2,104 | 108.0 | 0.051 | 0.333 (11/33) |
| 3 | 2 | 99 | 2.341 | 1,214 | 21.6 | 0.018 | 0.303 (10/33) |
| 3 | 3 | 95 | 2.431 | 1,180 | 16.6 | 0.014 | 0.333 (11/33) |
| 3 | 3 | 99 | 2.819 | 782 | 3.4 | 0.004 | 0.273 (9/33) |
| 3 | 4 | 95 | 2.804 | 839 | 4.0 | 0.005 | 0.273 (9/33) |
| 3 | 4 | 99 | 3.202 | 535 | 0.8 | 0.001 | 0.152 (5/33) |

All 12 cells meet the false-rate cap.

**Frozen parameters** (`frozen-params.json`, commit 6cc5221, "D2 parameters frozen", made before test recall was
computed): min O 2, O/E 2, null 95th percentile, threshold log₂ 2.278 (O/E > 4.85 in every qualifying branch),
≥ 2 branches, window 4, seeds 0–19. The 13 tune items recovered were (gloss: key pair as in `split.json`):
- dyew + mer: `pie-root-dyew-be_bright|pie-root-mer-die`
- fame + great: `pie-lex-kjlewos|pie-lex-megjh2s`
- livestock + men: `pie-lex-pekju|pie-lex-wiHros`
- swift + horse: `pie-lex-HeHkjus|pie-lex-h1ekjwos`
- lie + sleep: `pie-root-kjey-be_lying_down|pie-root-swep-sleep`
- upright + stand: `pie-root-h3erdh-upright|pie-root-steh2-stand`
- immortal + dyew: `pie-lex-nmrtos|pie-root-dyew-be_bright`
- fame + decline: `pie-lex-kjlewos|pie-root-dhgwhey-decline`
- dawn + shine: `pie-lex-h2ewsoxs|pie-root-bheh2-shine`
- immortal + eat: `pie-lex-nmrtos|pie-root-h1ed-eat`
- earth + cloud: `pie-lex-dhegjhoxm|pie-root-nebh-become_damp`
- mead + sweet: `pie-lex-medhu|pie-lex-sweh2dus`
- white + dress: `pie-root-h2ergj-white|pie-root-wes-dress`

## Test (measured once; `test-results.json`)

**Test recall 8/32 = 0.250; false rate 0.138 (427.4 null vs 3,086 real candidates, 2,361 root-group pairs).
The criterion is not met.**

Each item below gives its best key pair within the root-group pair and the layers with the most O.

**Recovered (8):**

| item | formulas | score log₂ | layers with most O (O, O/E) |
|---|---|---|---|
| raw + eat | west_ch02_f08 | 4.67 | grc-late 37 ×14.1; grc excl 12 ×25.5; av 6 ×25.5 |
| broad + spread | west_ch04_f14, f15, f16 | 5.53 | rv 7 ×46.3; grc excl 3 ×49.8 |
| dyew + cloud | west_ch04_f03, f04 | 3.63 | sa-ep 6 ×12.4; hom 5 ×12.3 |
| cloud + dress | west_ch02_f48 | 3.09 | hom 3 ×8.5; rv 2 ×61.6 |
| goods + menos | west_ch02_f35 | 3.24 | ae 137 ×9.5; hom 6 ×29.7 |
| sun + wheel | west_ch05_f09 | 3.23 | grc excl 59 ×11.4; rv 7 ×9.4; grc incl 7 ×14.5 |
| sun + see | west_ch02_f26, f29 | 3.23 | rv 25 ×12.4; av 23 ×11.7; ga-early excl 8 ×10.9 |
| menos + bold | west_ch02_f36 | 2.65 | rv 5 ×9.5; grc-late 4 ×6.3 |

**Missed (24), by the rule step that drops the item:**

| step | n | items |
|---|---|---|
| O ≥ 2 in ≥ 2 branches, but O/E ≥ 2 in at most one | 10 | word + fashion (craft words, 5 rows); serpent + slay (13 rows: rv 22 ×34.9, av 14 ×7.0, but Greek only ×1.7); immortal + speech; name + dear; great + drive (chariot path); see + see/know (3 rows); star + hew; slay + be; great + sun; speech + spread (Homer 129 ×6.0, no second branch) |
| qualifies in ≥ 2 branches, score ≤ threshold | 10 | giver + goods (1.88); cow + drive (1.59); famous name: name + fame, both items (1.48); man + fame (1.54); horse + man (1.05); earth + mother (3 rows, 1.27); slay + lie (slain lies, 1.86); fame + spread (2 rows, 1.70); sun + run (1.32) |
| O ≥ 2 in at most one branch | 2 | wolf + grey (Greek only); worm + slay (av 25 ×19.0 only; 4 rows) |
| excluded (top-50 groups) | 1 | dyew + beget (west_ch03_f07; both groups in the top 50) |
| self pair | 1 | mortal + self (west_ch02_f94) |

The glosses in the two tables above map to key pairs as follows (all 32 test items):

| key pair | result | formulas |
|---|---|---|
| `pie-root-nebh-become_damp|pie-root-wes-dress` | recovered | west_ch02_f48 |
| `pie-lex-h2eh3mos|pie-root-h1ed-eat` | recovered | west_ch02_f08 |
| `pie-lex-h1wesus|pie-lex-menos` | recovered | west_ch02_f35 |
| `pie-root-h1werH-broad|pie-root-pleth2-spread` | recovered | west_ch04_f14, west_ch04_f15, west_ch04_f16 |
| `pie-lex-menos|pie-root-dhers-be_bold` | recovered | west_ch02_f36 |
| `pie-lex-kwekwlos|pie-lex-soh2wl` | recovered | west_ch05_f09 |
| `pie-lex-soh2wl|pie-root-derkj-see` | recovered | west_ch02_f26, west_ch02_f29 |
| `pie-lex-dyexws|pie-lex-nbhros` | recovered | west_ch04_f03, west_ch04_f04 |
| `pie-lex-woxkws|pie-root-tetkj-create` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | craft-words, craft-the-formula, west_ch01_f05, west_ch01_f06, west_ch01_f07 |
| `pie-lex-h1ogwhis|pie-root-gwhen-strike` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | hero-slay-serpent, slew-the-serpent-egwhent-ogwhim, basic-formula-with-weapon-companion, who-slew-relative-clause, slayer-slain-reciprocal, slay-serpent-with-companion, slay-gwhen-serpent-ogwhi, egwhent-ogwhim-augment, slay-serpent-slaying-ring, serpent-slay-adversary, serpent-slayer-man-slayer-epithets, west_ch06_f01, west_ch06_f02 |
| `pie-lex-deh3toxr|pie-lex-h1wesus` | qualifies in >= 2 branches, score <= threshold | west_ch03_f20 |
| `pie-lex-gwoxws|pie-root-h2egj-drive` | qualifies in >= 2 branches, score <= threshold | hero-slay-three-headed-drive-off-cows |
| `pie-lex-wlkwos|pie-root-pelH-pale` | O >= min O in <= 1 branch | west_ch02_f20 |
| `pie-lex-h1nomn|pie-lex-kjlewos` | qualifies in >= 2 branches, score <= threshold | famous-name |
| `pie-lex-nmrtos|pie-lex-wekwos` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | west_ch02_f43 |
| `pie-lex-h1nomn|pie-lex-priHos` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | west_ch10_f18 |
| `pie-root-dyew-be_bright|pie-root-gjenh1-produce` | excluded (function / top-50) | west_ch03_f07 |
| `pie-lex-kwrmis|pie-root-gwhen-strike` | O >= min O in <= 1 branch | kill-serpent-germanic-bidirectional, slay-the-worm-charm, slay-adversary-plus-marrow-list-charm, west_ch08_f26 |
| `pie-lex-h2nexr|pie-root-kjlew-hear` | qualifies in >= 2 branches, score <= threshold | west_ch10_f15, west_ch01_f17 |
| `pie-lex-h1nomn|pie-root-kjlew-hear` | qualifies in >= 2 branches, score <= threshold | west_ch10_f16 |
| `pie-lex-h1ekjwos|pie-lex-h2nexr` | qualifies in >= 2 branches, score <= threshold | west_ch12_f17 |
| `pie-lex-megjh2s|pie-root-h2egj-drive` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | great-path-of-chariot, west_ch05_f11 |
| `pie-root-derkj-see|pie-root-weyd-see` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | quantifier-argument-negated-argument, seen-and-unseen-disease, west_ch02_f72 |
| `pie-lex-h2stexr|pie-root-peykj-hew` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | west_ch09_f10 |
| `pie-root-gwhen-strike|pie-root-h1es-be` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | be-the-death-of |
| `pie-lex-soh2wl|pie-root-Hreth2-run` | qualifies in >= 2 branches, score <= threshold | west_ch05_f10 |
| `pie-lex-megjh2s|pie-lex-soh2wl` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | west_ch05_f01 |
| `pie-lex-mrtos|pie-lex-mrtos` | self pair (one word with itself): same-group pairs are not counted | west_ch02_f94 |
| `pie-lex-dhegjhoxm|pie-lex-meh2texr` | qualifies in >= 2 branches, score <= threshold | west_ch04_f12, west_ch04_f22, west_ch04_f23 |
| `pie-lex-wekwos|pie-root-peth2-spread_out` | O >= min O in >= 2 branches, but O/E >= min O/E in <= 1 | west_ch01_f12 |
| `pie-root-gwhen-strike|pie-root-kjey-be_lying_down` | qualifies in >= 2 branches, score <= threshold | slain-lies |
| `pie-lex-kjlewos|pie-root-pleth2-spread` | qualifies in >= 2 branches, score <= threshold | west_ch10_f06, west_ch02_f02 |

The per-layer O, E and O/E for every test item are in `test-results.json`.

## Observations for any later round

These are untested and were not used to change anything in D2.

- **Tune and test differ.** Tune recall was 0.394, test recall 0.250. The 13/33 against 8/32 gap is within
  sampling noise for halves this size. Still, choosing the loosest cell on tune did not carry over.
- **The weak-second-branch pattern remains.** Ten test items fail because only one branch reaches O/E ≥ 2. Their
  second branch has O at the epic or prose base rate: Greek ×1.7 for serpent + slay, Indo-Iranian ×0.8–2.1 in
  sa-ep for several items. Ten more qualify but fall below the null threshold, which needs O/E > 4.85 in every
  qualifying branch.
- **Layers help but sometimes pick the late stratum.** Some recoveries use the excluded or late layers (grc-late,
  grc excluded, ga-early excluded) as a qualifying branch. A layer split lets a formula show at high O/E in a
  small early stratum, but nothing restricts the qualifying layer to the early ones.
- **The null pool is wide.** At min O 2, the shuffles qualify about 8,500 pairs per seed against 13,972 real. Many
  null pairs are O = 2 on rare keys in small layers, which keeps the 95th-percentile threshold high.

## What was not done (by rule)

- No review set, decoys, packet (`docs/research/discovery/d2-packet.jsonl` does not exist) or key
  (`data/audits/keys/d2-key.json` was not written).
- The packet code, including its dry run, was not executed because the criterion failed. It is still untested.
- Candidates exist only in the binary caches (`run-real.npz`). They were never printed or read. `tune` and `test`
  print only counts and known-formula items.

## Runtime (32-core machine)

| step | time |
|---|---|
| extract (2.31M units, 24 processes) | 21 s |
| count (real + 20 within-layer shuffles, 10 processes, ~13–15 s each) | 38 s wall |
| split | < 1 s |
| tune (12 cells × 21 runs) | 3 s |
| test | 1 s |

## Files

- Committed, in `data/research/discovery/d2/`:
  - `extract-stats.json`, `layers.json`, `keys.json` and `split.json`;
  - `count-stats.json`, which includes the Σ O / Σ E check per run;
  - `tune-grid.json` and `frozen-params.json`;
  - `test-results.json`.
- Gitignored and reproducible with `discovery_d2.py extract` and `count`: `words.npz`, `run-*.npz` and
  `real-full.npz`.
