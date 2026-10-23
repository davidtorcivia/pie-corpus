# Phase 8a: an independent evaluation set of inherited formulas (eval-r3)

*Built 2026-10-23 from the scholarship alone. The protocol at the end was written before any round-3 result existed. Neither I nor the extraction agents opened the round-3 candidates, mapping, report or code: I checked every agent's tool calls for those paths, and none matched. The merge script (`merge.py`) and the corpus query tools are in the session scratchpad, not the repo, because code was out of scope. The merge rules are written out below, and the script can be moved into `scripts/` on request.*

**Result:** 177 lexical items, 90 of them primary (scoreable by a co-occurrence search). 61 primary items are eligible for an Indo-Iranian × Greek ranking. The held-out core is 23 primary items, which are in neither formulas.jsonl nor E2. 97.5% of the primary items' locally checkable phrase attestations were confirmed in a corpus.

Files:
- `data/research/formulas/eval-r3/formulas-eval.jsonl`: the set, 637 items (177 lexical, 269 partial, 191 schema). sha256 `1f4668366af9f5c6c2d127f6c7e395c88bc4b2be9c56aa996d4625b71fba2e0f`.
- `data/research/formulas/eval-r3/extraction/`: provenance. It holds the 10 per-source extraction files and `review_overrides.json` (68 manual corrections, each with a reason).

## How the set was built
1. **Sources, read in full:**
   - Schmitt 1967 (§§ 8–637). Read from the Tesseract Greek re-OCR (`schmitt-1967-tess/`), checked against the macOS OCR where needed.
   - Matasović 1996 (all pages).
   - Watkins 1995 (pdf pp. 18–561, plus the indexes as a completeness check). Read from `watkins-tess/` and the PDF text layer.
   - West 2007 (chapters 1–12).
   
   Ten extraction passes (S1–S4, M, W1–W2, WE1–WE3) each covered one range. They recorded every equation the author states as words, lemmas, loci and § or page. Nothing came from memory, and running text was never quoted.
2. **West and Watkins:** every one of the 389 formulas.jsonl records was re-read in its source and relabelled (281 West, 108 Watkins). Equations the earlier extraction had missed were added (197 new items before merging).
3. **Lexicon mapping:** each cognate word is mapped to lexicon ids, a lexeme where one exists and always its root group. Inflection-spec `usable` flags are recorded per lexeme. If no lexeme exists (e.g. some ákṣiti-/ti-derivatives), only the root id is given.
4. **Locus check:** each attestation's locus was checked in the local corpora with a scratch query tool over cached segments:
   - rv: VedaWeb pāda
   - homer: line
   - glaux: Hesiod, Hymns, Pindar, Bacchylides, drama and other early poetry
   - av: DCS Śaunaka and Paippalāda
   - avesta: CAB, with Geldner numbers
   - edda, oe, hittite (TLHdig line), latin (LASLA)
5. **Merge:** items from different sources are merged when their cognate words fall in the same root groups. Each merged item keeps every source's § or page, label and verdict. Single-root items (polyptoton, figura etymologica) are never merged.
6. **Review and labels:**
   - I re-read every lexical item and made 68 overrides:
     - strength changes, e.g. ari- = ἐρι- is unproven, so those items are partial, and bhadrá- is not from *bʰeh₂-
     - exclusion of non-cognate attestations kept as parallels, e.g. γαῖα καὶ οὐρανός in the Hittite–Avestan heaven-and-earth item
     - verdicts where an author rejects or doubts an equation
     - function-word pairs
     - equations the extraction agent composed itself rather than the author
   - Strength labels:
     - `lexical`: every content word is cognate in at least two branches. Indo-Iranian counts as one branch.
     - `partial`: one word is cognate, the other a synonym.
     - `schema`: the meaning matches, the words do not.
   - Indo-Iranian-only equations (134) are not in the main file. They are in `eval-r3/single-branch.jsonl`, for reference only.
7. **`primary`**, the scoreable population, requires all of the following:
   - the item is lexical
   - it has ≥ 2 distinct cognate root groups
   - it is not a pronoun or particle pair
   - at least one source does not reject it
   - the author states it, rather than an agent composing it
   - it is a phrase, two separate tokens, in ≥ 2 branches (`phrase_branches`)
   
   Lexical items that fail are kept with their `exclusion_reasons`:

   | exclusion reason | lexical items |
   |---|---|
   | compound or name in all but one branch | 70 |
   | single root | 23 |
   | rejected by the source | 8 |
   | function word | 5 |
   | agent-built equation | 2 |

   (An item can have more than one reason.)
8. **Overlap:** `overlap.formulas_jsonl` lists formulas.jsonl ids, by id or by an agent's mapping. `overlap.formulas_jsonl_text_match` is a deliberately conservative check: both attested forms of one attestation occur in a formulas.jsonl record's text. `overlap.E2` gives the round-2 item whose root pair the item contains. `held_out_core` is true when all three are empty.

## Counts
| | items | primary |
|---|---|---|
| lexical | 177 | 90 |
| partial | 269 | — |
| schema | 191 | — |

**Primary items by branch pair**, counted by `phrase_branches`:

| branches | primary items | held-out core |
|---|---|---|
| Indo-Iranian + Greek only | 45 | 14 |
| ≥ 3 branches | 21 | 2 |
| other two-branch pairs | 24 | 7 |
| **eligible for an Indo-Iranian × Greek ranking** (contains both) | **61** | **16** |
| eligible for Indo-Iranian × Italic | 16 | 4 |
| eligible for Greek × Italic | 11 | 2 |
| eligible for Indo-Iranian × Balto-Slavic / Greek × Balto-Slavic | 9 / 8 | 0 / 0 |
| eligible for Indo-Iranian × Celtic / Indo-Iranian × Germanic / Greek × Germanic | 7 / 6 / 5 | 1 / 1 / 0 |
| eligible for Anatolian × Indo-Iranian | 4 | 0 |

The 24 other two-branch pairs:
- Indo-Iranian–Italic: 7
- Indo-Iranian–Celtic, Indo-Iranian–Balto-Slavic, Indo-Iranian–Germanic: 3 each
- Greek–Germanic: 2
- Anatolian–Indo-Iranian, Balto-Slavic–Italic, Balto-Slavic–Germanic, Celtic–Italic, Balto-Slavic–Greek, Italic–Tocharian: 1 each

**Sources of the primary items:**

| source | primary items |
|---|---|
| West | 59 |
| Schmitt | 43 |
| Matasović | 27 |
| Watkins | 19 |

- 39 primary items are attested by two or more of the four books.
- The held-out core is 12 Schmitt, 10 Matasović, 3 West and 2 Watkins items. (An item can come from more than one book.)

**Overlap of the 90 primary items:**
- 59 are in formulas.jsonl by id, and 8 more by text match.
- 16 contain an E2 pair. Across the whole set, 16 of E2's 24 items are covered. The 8 not covered are the -kʷe and demonstrative pairs, three other pairs (sun + 'point out', 'three' + 'few', Sky + 'first'), and the *gʷʰen-* + 'lie' and *gʷʰen-* + *serp-* pairs, for which the sources give partial items here.

**Mapping:**
- 74 of the 90 primary items have a lexeme id for every cognate word, and 88 have root groups.
- 19 of the primary items' 183 cognate words have no lexeme id, and 2 have no root group either. They stay in the denominator.

## Confirmation
Counted over the primary items' phrase attestations (538):

| status | attestations |
|---|---|
| `at_locus` | 344 |
| `other_locus` | 78 |
| `text_not_local` | 105 |
| `not_found` | 11 |

- **Confirmation rate** over the locally checkable attestations: (344 + 78) / 433 = **97.5%**.
- **Loci the authors cite**, where the text is local: 341 of 354 confirmed at the cited locus. Another 10 were found at a corrected locus, mostly printing or OCR slips that the extraction notes record, such as RV 4.96.9 for 4.36.9 and Y. 39.10 for 33.10.
- **Items with ≥ 2 local branches:** 64 of 65 are confirmed in ≥ 2 branches.
- **Corpus-confirmed subsets:**
  - 57 primary items are confirmed in an Indo-Iranian corpus and a Greek corpus.
  - 34 primary items are confirmed in both the RV and Homer specifically.
- **Source check:**
  - For each of the 182 (primary item × source) pairs, I checked that the cited pages or chapter contain the attested forms. 178 passed outright.
  - The other 4 were checked by hand and are correct: Cyrillic OCR, a West section with names only, and one Watkins page.
  - I also read 20 random primary items in full, sources and corpus hits. That read produced 2 corrections: Greek and Latin dropped from "there was a king, N his name", and a note that Vedic "wide fame" rests on the compound urugāyá-.

## Known weaknesses
- **OCR:**
  - Schmitt's Greek is reliable only in the tess re-OCR.
  - Matasović pp. 20–21 (§§ 13–16, the ḱléwos system) are empty files, so his own "good fame" item is missing. Other sources supply it.
  - Watkins's Avestan, Luvian and Armenian forms had to be decoded; 11 W2 items carry `ocr_uncertain`.
  - The Edda and OE corpora are OCR without verse numbers. Their header labels are wrong in places, and some poems are missing: the Metrical Charms, and the Exeter Gnomes, Elene and Andreas. A few `not_found` results there are coverage gaps.
- **Avestan numbering:** CAB numbering differs from the standard one. Loci are given as CAB id plus Geldner number.
- **Scholarly disagreement:** 15 primary items are `contested`, meaning one source doubts or rejects them. Examples are swift horses (Matasović: uninformative), great sun (Schmitt: chance), slay the serpent (the Greek is Watkins's restoration) and μένος ἠΰ (Schmitt doubts *h₁su- = *h₁wesu-). `verdict_by_source` lets these be dropped.
- **Cognacy judgements:**
  - About 22 West items rest on cognations that West sets out but does not state, e.g. τρεῖς νύκτας ~ tri noći. They are noted in `notes`.
  - My overrides are one reviewer's calls; each is listed with its reason.
- **Selection bias:**
  - The set is dominated by Graeco-Aryan fame, Sky and Dawn formulas (61 of 90 primary are eligible for Indo-Iranian × Greek). That is the shape of the field, not a sampling choice.
  - Non-Graeco-Aryan items are mostly in texts that are not local (Old Irish, Baltic songs, Umbrian).
- **Phrase test:** the `phrase` flag is a heuristic: ≥ 2 cognate words with distinct lemmas, with no compound parts. Items whose Vedic side is a compound inside a phrase (urugāyám śrávaḥ) stay primary.
- **Eligibility is coarse:** it is set by branch, so an Indo-Iranian attestation may be Avestan only.
- **Residual eligibility errors:** the 20-item read found one non-cognate attestation inflating `phrase_branches`. Roughly 1 primary item in 20 may still have an inflated branch list. If an item looks wrong, re-check its `attestations[].phrase` against `words`.
- **Unscoreable words:** 2 primary items have a cognate word with no root group. They can only count as misses, at either level.
- **Confirmation was done by the extraction agents**, with the same query tool, not by an independent checker. `other_locus` includes collocations the agent found itself where the author gave no locus.
- **Independence:**
  - The held-out core is small (23 primary items). With n = 23, a recall of 0.5 has a 95% CI of about ±0.2. For all 90 primary items it is about ±0.10, and for the 61 Indo-Iranian × Greek items about ±0.13.
  - Most famous formulas are in formulas.jsonl or E2 already, and round 3 may have tuned on them.

## Pre-registered protocol

The first draft was written before extraction began. It was revised once, after the set was built and before any round-3 number existed. The revision narrowed the population from all lexical items to `primary` and added the uncontested subset.
- **Population:**
  - Score only items with `primary == true`. These are lexical, with two separate cognate content words in ≥ 2 branches.
  - Report the other lexical items (compounds, single-root, contested) only as a secondary table.
  - `partial` and `schema` items are never scored.
- **Eligibility per ranking:** a ranking built from corpora in branches X and Y is scored on the primary items whose `phrase_branches` contains both X and Y. Eligibility comes from the scholarship, not from our confirmation. Items whose words have no lexeme id stay in the denominator: a lexeme-level ranking counts them as misses unless it matches them through `pairs_root`.
- **Hit:**
  - An item is hit at k if any pair in `pairs` (lexeme ids) is at rank ≤ k. For a root-group ranking, use `pairs_root` instead.
  - Its rank is the minimum over its pairs.
  - The level actually used is stated.
- **Primary metric:** recall@k for k = 50, 100, 200, per ranking. 95% percentile CI from 2,000 bootstrap resamples of items, seed 0.
- **Subsets**, each reported with its own n and CI:
  1. All eligible primary items.
  2. Held-out core (`held_out_core == true`). If round 3 used formulas.jsonl, E2 or West's text in any tuning or design step, this is the headline number.
  3. Corpus-confirmed: `phrase_corpora_confirmed` includes a corpus of each branch of the ranking.
  4. Uncontested: `verdict == "accepted"`.
- **Comparisons:**
  - Paired bootstrap over the same items, 2,000 resamples, reported as a difference with its CI.
  - Baseline: the same method on corpora whose PIE labels are permuted across tokens, 5 seeds as in round 2. Report the mean and maximum recall@k.
- **Rules:**
  - The set is frozen at the sha256 above, and the round-3 report records that hash.
  - Nothing is added, removed or relabelled after any ranking has been scored on it. Errors found later go in an erratum, and results are reported on both versions.
  - No tuning on this set. If tuning is unavoidable, split by `sha1(item_id) mod 2`, tune on half A, and report half B once.
  - The number of eligible items is printed next to every recall figure.
