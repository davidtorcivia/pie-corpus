# Phase 8c Stage C: build report (2026-10-24)

The build follows the pre-registration (docs/research/8c-preregistration.md, sections "Stage C" and "Stage C build deviations"). The builder is `scripts/build_8c_stageC.py`. It imports the Stage B builder and reuses its retrieval, bundling, decoy and slab-packing code unchanged. Tests are in `tests/test_8c_stageC.py`.

**These are preliminary numbers.** They come from the mapping tables as of 2026-10-24 05:00, which include Celtic mapping round 2 (CELT coverage 32.8%; `lemmatize_words` is applied to every Celtic word sequence, including the untagged gloss tokens). The final build will be rerun after the fix/mapres merge (see "Re-running").

## Re-running

The whole build is one command (about 25 minutes from scratch on this machine, 32 cores):

```
uv run python -I scripts/build_8c_stageC.py --refreeze
```

- `--refreeze` recomputes `data/research/8c/stageC/params.json` using the same rule (the 0.90 quantile). Use it only while no Stage C slab has been read.
- Without `--refreeze`, the builder reads the floor that is frozen in that file.
- `--cache-dir DIR` reuses pickles from one loader group to the next. Delete them after any mapping change.
- Options that depart from the pre-registration, all off by default:
  - `--celtic-max-date 1250`
  - `--include-ccmh`

**What changes after fix/mapres and the Celtic fixes:**
- Every mapping-dependent number: mapped shares, indexed and pivot units, the < 30% counts, the score distribution, the floor, the null, bundles, decoys, slabs, tokens and readers.
- Unit counts and token counts do not change unless the loaders or the Celtic layer change.

## Outputs

| file | content | git |
|---|---|---|
| `data/research/8c/stageC/params.json` | frozen floor and rules, score distribution, null comparison | committed |
| `data/research/8c/stageC/stats.json` | everything below | committed |
| `data/research/8c/stageC/assignment.json` | one reader per slab (RC001…) | committed |
| `data/research/8c/stageC/slabs-loci/SC-*.json` | loci-only copies (ids, loci, licence tags) | committed |
| `data/research/8c/stageC/slabs/SC-*.json` | slabs with text (466 MB) | gitignored |
| `data/audits/keys/8c-stageC-key.json` | blinding key: kind, real and decoy partners, pivot witness metadata | gitignored |
| `data/research/8c/stageC/reader-brief.md` | reader instructions | committed |

## Corpora

**Pivots.** The pivots are the Celtic layer (`raw/daughters/celtic-stageC/units.jsonl`), then the other new traditions, in that reading order.
- Every Celtic unit with `dup_of` null is included; 49,536 duplicates are skipped.
- How translations, apparatus and notes were removed from the Irish OCR is documented in docs/research/celtic-stageC-units.md.

**Partners.** Partners come from every corpus held.

**Column definitions.**
- *Content words*: the words that can carry a mapping (function words are excluded).
- *Mapped*: the share of content words with a PIE etymon.
- *Indexed*: units with at least one mapped root group, after exact repeats are removed. These units are the pivots or the partner pool.

| corpus | role | branch | units | tokens | content words | mapped | indexed | indexed < 30% mapped | licence tags (units) |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| sga-gl Old Irish glosses (Wb, Sg) | pivot | Celtic | 6,958 | 38,746 | 19,578 | 31.1% | 3,177 | 614 | cc-by 3,548, nc 3,410 |
| sga Old Irish (CELT, editions, journals) | pivot | Celtic | 40,260 | 349,550 | 198,370 | 22.1% | 23,131 | 9,196 | consent-train 32,199, research 5,035, pd 3,021, nc 5 |
| mga Middle Irish | pivot | Celtic | 150,666 | 1,529,523 | 836,858 | 22.3% | 94,183 | 42,507 | consent-train 112,471, research 27,716, pd 10,344, nc 135 |
| cy Middle (and 2 Old) Welsh | pivot | Celtic | 43,372 | 417,153 | 257,401 | 12.6% | 21,621 | 14,791 | pd 34,778, research 8,594 |
| ga-early Early Modern Irish | pivot | Celtic | 127,922 | 2,056,833 | 1,093,017 | 23.0% | 99,667 | 57,312 | consent-train 106,672, research 13,473, nc 6,813, pd 964 |
| menota Old Norse (Menota) | pivot | Germanic | 125,843 | 1,668,132 | 965,752 | 51.3% | 107,957 | 12,886 | cc-by-sa |
| icepahc Old Icelandic (IcePaHC ≤ 1400) | pivot | Germanic | 22,516 | 255,971 | 119,313 | 64.8% | 20,477 | 758 | cc-by |
| rea-goh Old High German (ReA) | pivot | Germanic | 18,140 | 337,765 | 147,812 | 73.5% | 17,417 | 196 | nc |
| rea-osx Old Saxon (ReA) | pivot | Germanic | 7,066 | 58,868 | 30,445 | 70.2% | 6,792 | 209 | nc |
| vuk Serbian songs (Vuk) | pivot | Slavic | 146,777 | 703,184 | 416,749 | 32.6% | 77,558 | 8,552 | cc-by-sa |
| byliny | pivot | Slavic | 153,744 | 808,140 | 482,352 | 32.6% | 82,757 | 16,833 | pd 140,784, cc-by-sa 12,960 |
| dainos Lithuanian | pivot | Baltic | 84,802 | 363,840 | 232,935 | 21.1% | 25,766 | 5,653 | pd |
| xcl Classical Armenian (DMHP) | pivot | Armenian | 30,443 | 551,142 | 329,644 | 25.6% | 27,581 | 16,256 | cc-by |
| xto Tocharian A | pivot | Tocharian | 5,026 | 32,456 | 30,455 | 9.2% | 1,929 | 1,487 | nc |
| sqo Old Albanian (Buzuku, Bogdani) | pivot | Albanian | 8,038 | 227,500 | 103,671 | 9.0% | 4,975 | 4,745 | nc |
| rv Rigveda | partner | Indo-Iranian | 39,832 | 166,865 | 118,887 | 65.1% | 32,875 | 751 | cc-by |
| av Atharvaveda | partner | Indo-Iranian | 13,800 | 107,134 | 70,660 | 61.8% | 11,626 | 832 | cc-by |
| ae Avesta | partner | Indo-Iranian | 16,466 | 102,447 | 103,999 | 30.0% | 8,400 | 3,256 | nc |
| hom Homer | partner | Greek | 27,760 | 200,145 | 116,533 | 64.5% | 23,717 | 1,823 | cc-by-sa |
| grc GLAUx ≤ 300 BC | partner | Greek | 282,885 | 3,809,801 | 1,644,522 | 71.8% | 250,850 | 5,266 | cc-by-sa 276,023, unchecked 6,629, cc-by 206, nc 27 |
| non Poetic Edda | partner | Germanic | 12,789 | 42,404 | 26,349 | 54.6% | 7,964 | 144 | pd |
| ang Old English poetry | partner | Germanic | 15,627 | 96,710 | 57,108 | 42.3% | 12,724 | 2,321 | pd |
| hit Hittite | partner | Anatolian | 318,800 | 876,848 | 185,489 | 36.2% | 17,427 | 943 | cc-by |
| lat Latin (LASLA) | partner | Italic | 18,841 | 144,788 | 73,932 | 59.8% | 16,872 | 1,107 | nc |
| xum Umbrian | partner | Italic | 2,221 | 8,775 | 8,723 | 15.7% | 745 | 263 | pd |
| lv Latvian dainas | partner | Baltic | 753 | 7,865 | 5,967 | 27.6% | 628 | 320 | unchecked |
| orv Early Old Russian (TOROT) | partner | Slavic | 14,662 | 123,312 | 66,927 | 32.2% | 10,540 | 3,276 | nc |
| sa-ep Mahābhārata, Rāmāyaṇa (DCS) | partner | Indo-Iranian | 206,208 | 1,409,567 | 987,133 | 48.2% | 180,459 | 34,178 | cc-by |
| grc-late GLAUx after 300 BC (727 texts) | partner | Greek | 632,158 | 10,657,541 | 4,845,187 | 65.2% | 580,541 | 20,533 | cc-by-sa 623,456, nc 8,334, gpl 300, cc-by 68 |

**Index size.** 1,770,356 indexed units and 3,372 root groups. 614,988 of these units are Stage C pivots.

### Celtic by language, period, genre and licence

Period is the century of the date midpoint. *Pivots* are the indexed units.

| lang | units | tokens | content words | mapped | pivots | pivots < 30% |
|---|---:|---:|---:|---:|---:|---:|
| sga (texts + glosses) | 47,218 | 388,296 | 217,948 | 22.9% | 26,308 | 9,810 |
| mga | 150,666 | 1,529,523 | 836,858 | 22.3% | 94,183 | 42,507 |
| ga-early | 127,922 | 2,056,833 | 1,093,017 | 23.0% | 99,667 | 57,312 |
| wlm | 43,370 | 417,139 | 257,394 | 12.6% | 21,620 | 14,790 |
| owl | 2 | 14 | 7 | 28.6% | 1 | 1 |

| period | units | tokens | mapped | pivots | period | units | tokens | mapped | pivots |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 5th c. | 487 | 5,885 | 22.1% | 309 | 12th c. | 70,250 | 672,844 | 22.3% | 42,341 |
| 6th c. | 385 | 2,802 | 18.8% | 229 | 13th c. | 18,369 | 196,725 | 18.1% | 10,932 |
| 7th c. | 756 | 5,544 | 21.6% | 450 | 14th c. | 36,978 | 457,511 | 16.4% | 22,357 |
| 8th c. | 12,595 | 109,781 | 23.2% | 7,322 | 15th c. | 33,993 | 561,979 | 22.1% | 26,254 |
| 9th c. | 29,443 | 251,213 | 23.6% | 17,158 | 16th c. | 23,729 | 358,479 | 22.1% | 17,846 |
| 10th c. | 10,967 | 104,293 | 22.0% | 6,948 | 17th c. | 22,506 | 459,177 | 26.1% | 18,905 |
| 11th c. | 108,720 | 1,205,572 | 21.6% | 70,728 | | | | | |

**Genre** (units / mapped / pivots):

| genre | units | mapped | pivots |
|---|---:|---:|---:|
| saga | 71,440 | 22.8% | 46,517 |
| annals | 69,903 | 21.3% | 51,438 |
| religious | 62,631 | 23.0% | 41,151 |
| verse | 42,478 | 19.6% | 21,958 |
| genealogy | 30,344 | 20.0% | 16,257 |
| history | 20,485 | 20.6% | 15,181 |
| adaptation | 17,474 | 21.3% | 14,490 |
| dindshenchas | 13,857 | 26.4% | 8,514 |
| medical-scientific | 11,204 | 21.9% | 9,636 |
| prose | 7,736 | 12.6% | 4,444 |
| glosses | 7,384 | 29.8% | 3,356 |
| scholarship | 4,990 | 22.1% | 3,261 |
| other | 3,865 | 18.5% | 2,318 |
| law | 3,362 | 24.9% | 2,093 |
| wisdom | 2,025 | 25.0% | 1,165 |

**Licence** (units / mapped / pivots):

| licence | units | mapped | pivots |
|---|---:|---:|---:|
| consent-train | 251,342 | 23.0% | 174,297 |
| research | 54,818 | 18.4% | 32,613 |
| pd | 49,107 | 14.2% | 25,398 |
| nc | 10,363 | 32.3% | 7,864 |
| cc-by | 3,548 | 22.0% | 1,607 |

**Why Celtic mapped shares (about 22–23% for Irish) are below the 32.8% CELT coverage of the mapping report.**
- Names are not mapped here. Capitalised non-initial words make up about 22% of Irish content words. Of these, 35.7k Middle Irish tokens would otherwise have been mapped: *Mac*, *Find*, *Fer*, *Loch*, *Mag*, *Día*.
- The skeleton fallback is off. At the skeleton level, 40% of the 11% of tokens there had mapped.
- The OCR editions and journals map less well than CELT does.

**Mapping junk seen in a slab, for the mapping fixes.** A kaikki key, `alsoindicatingtheulsterpronunciation`, appears inside an Irish lemma union (`…|croidhe|croí`).

### Licence tags

Every passage carries `licence` and `licence_tag`, and every slab lists its tag counts. `research_only` is true for the tags research, nc, nd and unchecked; for the Stage B corpora it is Stage B's own flag (e.g. GLAUx texts outside CC BY / CC BY-SA 4.0 stay research_only, as in Stage B). CELT files are tagged as the Celtic layer tags them:
- 58 OUP-notice files G400001–G400058 are `research`.
- The CC BY-NC-SA files G100055/56 and G600019/31 are `nc`.
- **Mismatch to settle with David.** The layer also tags 1,429 units of G400065–G400090 as `research`, but `celtic_mapping.CELT_RESEARCH_ONLY` (G400001–058) would make them `consent-train`. The build keeps the stricter tag.

ReA, Tocharian A and Old Albanian are `nc`, as are PROIEL-derived TOROT and the CAB Avesta.

### Non-Celtic pivots: period and genre

The key holds witness metadata (date, genre, licence) for Celtic pivots only. For the pre-registered secondary measure (archaic verse; early prose and glosses; late oral traditions) the other pivots are classed by `pivot_corpus`:

| corpus | witness period | genre |
|---|---|---|
| menota | Old Norse MSS, 13th–16th c. (some c. 1700 copies) | mixed: sagas, laws, homilies, Eddic and skaldic verse; classing by genre needs the Menota catalogue by document id |
| icepahc | texts to 1400 | sagas, religious prose |
| rea-goh, rea-osx | 8th–11th c. | glosses, translations, Otfrid, Heliand, Notker |
| vuk, byliny, dainos | records of the 18th–19th c. | late oral tradition |
| xcl | 5th c. | historiography, theology |
| xto | MSS of the 6th–8th c. | Buddhist texts, largely translated or adapted |
| sqo | 1555 (Buzuku), 1685 (Bogdani) | liturgy, theology |

## Low-mapped pivots (the pre-registered < 30% rule)

These units stay pivots and find partners only through their mapped words.

| | count |
|---|---:|
| Stage C pivots | 614,988 |
| pivots with < 30% of content words mapped | 191,995 |
| of which have any partner | 59,391 |
| of which are in a bundle | 962 |

Units with no mapped root (or exact repeats of an earlier unit) are not indexed and cannot be pivots: 127,399 of the 369,178 Celtic units.

## Retrieval, floor and null

Stage B's rules are used unchanged:
- a partner must share at least 2 matched root groups with the pivot, one of them outside the 50 most frequent;
- the score is the sum of idf;
- the top 6 partners are kept;
- the merge cap is 12.

idf is computed over all 1.77M indexed units. Retrieval runs from the Stage C pivots only. 279,685 of the 614,988 pivots have at least one partner.

**Floor.** The floor is the 0.90 quantile of the best-partner score: **14.7906**, frozen in params.json. Stage B's 12.35 does not carry over, because the idf base differs.

Best-partner quantiles:

| quantile | 0.5 | 0.75 | 0.9 | 0.95 | 0.99 | 0.999 |
|---|---:|---:|---:|---:|---:|---:|
| score | 11.34 | 13.05 | 14.79 | 15.90 | 18.01 | 20.58 |

**Null.** In the null, each content word's root set is shuffled within its corpus, and retrieval runs from the same pivots. As in Stage B, real texts do not have more high-scoring pivots than the null except in the far tail:

| floor | real pivots ≥ floor | null pivots ≥ floor |
|---:|---:|---:|
| 13.05 | 69,924 | 90,654 |
| 14.79 | 27,975 | 37,727 |
| 15.90 | 13,985 | 18,513 |
| 17.15 | 5,594 | 7,040 |
| 18.01 | 2,797 | 3,348 |
| 18.81 | 1,399 | 1,541 |
| 20.58 | 280 | 264 |

At the floor, the Celtic pivots are real 5,469 against null 7,700. Retrieval is therefore a frequency-driven sample of root-sharing pairs, as in Stage B. The embedded decoys are the control.

## Bundles, decoys, slabs, readers

**Bundles.**
- 27,975 pivots are above the floor. They give **24,754 bundles**; 1,695 bundles had other bundles merged into them.
- Bundle sizes, in passages:

  | size | 2 | 3 | 4 | 5 | 6 | 7 | 8–12 |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | bundles | 11,104 | 4,444 | 2,345 | 1,534 | 1,004 | 3,863 | 460 |

**Decoys.**
- **19,803 bundles are real and 4,951 are embedded decoys (20.0%)**. The decoy draw hit its target exactly.
- The decoy share per slab ranges from 0.188 to 0.216.
- Each decoy partner shares no root group outside the 50 most frequent with its pivot, and at most one root group in all. This is tested.

**Slabs and readers.**
- **188 slabs** (ids `SC-xxxx`, bundles `BC-xxxxx`), of 118k–703k tokens each.
- Slab tokens total **125.2M**, or about **162.7M with reader overhead**. Stage B had 32.0M and 41.6M.
- **Proposed reader count at Stage B's capacity** (one reader per slab, target 600k and maximum 700k tokens): **188 readers**, plus blind review.

**Bundles by pivot group.**

| pivot | bundles | of which decoys |
|---|---:|---:|
| **Celtic** | **4,686** | 938 |
| sga-gl | 37 | |
| sga | 300 | |
| mga | 1,467 | |
| cy | 146 | |
| ga-early | 2,736 | |
| **Other** | **20,068** | 4,013 |
| menota | 11,296 | |
| rea-goh | 4,426 | |
| xcl | 2,025 | |
| icepahc | 1,501 | |
| byliny | 273 | |
| rea-osx | 238 | |
| vuk | 179 | |
| dainos | 96 | |
| sqo | 23 | |
| xto | 11 | |

**Celtic pivot bundles by witness date** (date midpoint):

| date | bundles |
|---|---:|
| ≤ 900 | 331 |
| 901–1200 | 1,778 |
| 1201–1250 | 77 |
| > 1250 | 2,500 |

Of the 2,736 ga-early bundles, 2,413 have a pivot whose witness year (annal year, else `date_from`: the rule of `--celtic-max-date`) is after 1250. A cut at 1250 would remove about that many bundles (exact numbers need a rebuild: the floor and merges shift).

**By genre:** religious 1,290, saga 828, annals 622, history 485, adaptation 465, medical-scientific 454, verse 132, genealogy 100, others ≤ 78.

**Partner slots by corpus:**

| corpus | slots |
|---|---:|
| grc-late | 39,636 |
| grc | 11,099 |
| sa-ep | 3,743 |
| menota | 1,775 |
| lat | 1,656 |
| ga-early | 1,229 |
| rea-goh | 1,057 |
| mga | 795 |
| av | 790 |
| xcl | 674 |
| orv | 636 |
| others | < 400 each |
| hit | 39 |

## Floor alternatives (decision for the lead / David before reading)

The 0.90 rule was Stage B's size rule for a budget of 30–60M tokens. Applied to Stage C, it gives four times Stage B's size, and only 19% of the bundles have a Celtic pivot. The pre-registration sets no Stage C budget.

The alternatives below are estimates without deduplication, so they run slightly higher than the packed figures:

| quantile | floor | bundles | Celtic-pivot bundles | slab tokens (est.) | read tokens (est.) |
|---|---:|---:|---:|---:|---:|
| **0.90 (frozen)** | 14.79 | 24,754 | 4,686 | 130.7M | 169.9M |
| 0.95 | 15.90 | 12,410 | 1,907 | 59.2M | 77.0M |
| 0.97 | 16.60 | 7,537 | 1,045 | 33.8M | 43.9M |
| 0.98 | 17.15 | 5,066 | 658 | 21.5M | 28.0M |
| 0.99 | 18.01 | 2,561 | 296 | 10.3M | 13.3M |

A higher floor shrinks the Celtic share further, because Celtic maps worse and so scores lower. Any change has to be made by `--refreeze` with a stated rule before reading.

## Implementation notes

- **Mapping.** Only the public API is used:
  - `apply_table_overrides` / `apply_lemma_overrides` through each module's `read_table` (or directly, for xcl, xto and sqo);
  - the per-module loaders and lemmatizers: `celtic_mapping` with `use_skeleton=False` and `lemmatize_words`, `bsl_mapping.lemmatizer` with `is_name`, `arm_toch_alb_mapping.build_xto` / `build_sqo` / `DmhpLemma`, and `germanic_new_mapping.read_table`.
- **Surface forms.** The Germanic and DMHP loaders drop surface forms, so the builder rereads them alongside each loader and asserts the same lemma sequence: Menota (normalized or diplomatic form), IcePaHC (word), ReA (relANNIS `edition` token at the lemma span's start) and DMHP.
  - 6,740 Old High German and 838 Old Saxon tokens had no edition form. They show as empty forms in the passage text.
- **Stage B's module** is loaded as a private instance, and the Stage C corpora and branches are added to that instance, so Stage B's own build and tests are unaffected.
- **Not loaded:**
  - Perseus Latin: no loader or table exists.
  - CCMH: Bible translations, not pre-registered.
  - Bardhi's dictionary: 4,870 entries.
  - Stage B's 99 UD Old Irish units: replaced by the full Würzburg and St Gall glosses (6,915 gloss units joined to their tagged tokens).
