# Mapping precision: Italic (lat, xum)

Corpora: `lat` (LASLA Latin: Plautus, Lucretius, Catullus, Cato; mapped live by `pie/formula_search.py`) and `xum` (Umbrian Iguvine Tables, Buck 1904 OCR; `data/research/formulas/mapping/xum.jsonl`).
Corrections: `data/research/formulas/mapping-overrides/italic.json`.
Main dictionary: de Vaan 2008 (`raw/books/text/devaan-latin`). Page numbers are printed pages (file number − 14). De Vaan's Umbrian word index (pp. 769–774) was used to find where each Umbrian form is discussed. Buck's glossary was used for Umbrian glosses.

## Method

- **Mapping as used.** Latin: `build_kaikki_mapping("la", …, build_latin_mapping(…), pseudo=True)`, then `apply_lemma_overrides`, which is the call `build_8c_stageB.live` makes. Umbrian: `build_lang_mapping("xum")`, then `umbrian_lines`, `FormLemmatizer`, `multi_lemma_mapping` and the rec and lemma overrides, which is the R3 pipeline. Content words are LASLA NOUN/VERB/ADJ for Latin and the dictionary POS for Umbrian. Before = shared overrides only. After = with `italic.json`.
- **Sample.** 100 content-word types per corpus, drawn without replacement and weighted by token count. The keys are u^(1/n) (Efraimidis–Spirakis) with `random.Random(seed)`: seed 0 before, seed 1 after.
- **Verdicts.**
  - C = correct. A union of ids is C when every id is the etymon of one of the words that the lemma merges (the `av: pad` precedent).
  - P = the right etymon plus a spurious homograph root, or the right root with the wrong formation.
  - W = wrong.
  - U = unmapped but has a secure etymology.
  - N = unmapped and has none.
  - A mapping counts as wrong when de Vaan says the etymology is unknown or disputed, or that the word is a loan.
- **Precision** = C / mapped (strict), with (C+P) / mapped also given (lenient).
- **Frequent-error pass.**
  - Latin: the 300 most frequent mapped lemmas were checked by hand. De Vaan was read for every doubtful item.
  - Umbrian: all 319 mapped types were checked. Each was cross-checked against the Latin headword under which de Vaan cites it (270 of the 319 are in his Umbrian index).
  - Frequent unmapped Latin compounds and derivatives were also added (54 lemmas) when de Vaan gives a secure base. Examples: abeo → eo, oculus, terra, frater, auris.

## Numbers

| corpus | sample | mapped in sample | C | P | W | strict precision | lenient |
|---|---|---:|---:|---:|---:|---:|---:|
| lat before | seed 0 | 68 | 44 | 9 | 15 | **64.7%** | 77.9% |
| lat after | seed 1 | 53 | 47 | 2 | 4 | **88.7%** | 92.5% |
| lat after, same seed-0 types | seed 0 | 63 | 55 | 3 | 5 | 87.3% | 92.1% |
| xum before | seed 0 | 13 | 11 | 0 | 2 | 84.6% | 84.6% |
| xum after | seed 1 | 14 | 14 | 0 | 0 | 100% | 100% |
| xum census, all mapped types before | – | 319 | 283 | 8 | 28 | 88.7% (91.0% of tokens) | 91.2% |

- **Unmapped in the samples.**
  - Latin: before 18 U and 14 N; after 27 U and 20 N.
  - Umbrian: before, seed 0 has 39 types that are English or Latin text from Buck's translation and commentary leaking into the "Umbrian" column (*the, of, sacrifice, Iguvinae, piato*) or OCR noise. Another 48 are Umbrian forms the lemmatizer leaves as `?…`.
  - Umbrian: after, seed 1 has 38 of the leaked types, 44 unresolved forms and 4 unmapped content lemmas (*feitu* U; *śihitu, mutu, arsmor* N).
- **Coverage of content tokens.**
  - lat: 57.2% → 59.8% (1,863 → 1,884 mapped types).
  - xum: 13.3% → 15.7%. The gain comes from 11 `form` rows, for example *totar, tote, totaper* → *totam*, *nomneper* → *nomne*, *ocriper* → *ocre*. 23 unmaps take some coverage away.
- **Overrides.**
  - 175 lemma rows. Latin: 33 unmaps, 52 corrections, 54 additions. Umbrian: 23 unmaps, 13 corrections.
  - 11 Umbrian form rows.
  - Every row cites a source. Most cite a de Vaan page. Two cite Beekes EDG (*oleum*, *mina*).
  - Ten Umbrian rows cite Buck instead. Some cite a Buck glossary line. The OCR-fragment rows (*are, alem, tu, iu, trum*) cite the text location.
  - No other group file touches `lat` or `xum`.
  - Note: *possum* now carries *pótis* as well as *h₁es-*. This follows de Vaan p.484, and it means *possum* will pair with 'master' lexemes in other branches.
- **Caveat.** The after figures were judged by the same person who wrote the overrides. Seed 1 is a fresh draw, but its high-frequency types overlap the top 300 that were corrected. The xum samples are tiny; the census is the better Umbrian figure.

## Main error types (Latin top 300: 84 of 300 wrong or partial)

1. **Spurious homograph roots in a union (≈ 35, mostly P).** A Wiktionary root with several numbered homographs comes through whole. Examples:
   - *facio, do, familia* + *dʰeh₁y-* 'suckle'
   - *possum* + *h₁es-* 'throw' and *sh₁es-* 'harvest'
   - *aetas, aeternus* + *h₂ey-* 'day' and 'give'
   - *uinco* with three *weyk-*
   - *fugio* + 'enjoy', *sentio* + 'go', *tango* + 'order', *uendo* + 'dress' and 'graze'

   The Umbrian *anclar* (+ *skelh₁-*) and *fiktu* show the same error.
2. **Speculative Wiktionary etymologies where de Vaan has none (≈ 30, W).** Examples:
   - *locus* (*stel-* rejected) and *bonus*
   - *miser, malus, licet, varius, mundus, labor, finis, crassus, latus, frons, populus, publicus, patior, herba, niger, pudeo, digitus, saxum, spatium*
   - loans: *oleum* (Greek) and *lapis* (Mediterranean)

   All unmapped.
3. **Wrong root (≈ 12).** Examples:
   - *pars* → *perh₂-* 'sell'; de Vaan derives it from *pario*
   - *soleo* → *swé*
   - *oro* → *h₂er-*; it is denominal to *ōs*
   - *mos* → *med-*; it is *meh₁-*
   - *amicus* → the particle *íh₁*
   - *simulacrum* → the suffix *-trom*
   - *purgo* → 'fire'
   - *tener* → *ten-*
   - *muto* → a "cross-reference only" stub
4. **LASLA lemma merges.** `load_latin` keys on the lemma string, and LiLa ids show the merged words. Examples:
   - *os* is ōs 'mouth' (87 tokens) plus os 'bone' (27). It had only 'bone'; it now has both.
   - *edo* is 'eat' plus ēdo 'give out'.
   - *uolo* is 'want' plus 'fly'.
   - *sero* is 'sow' plus 'join'.
   - *leuis* is 'light' plus 'smooth'.
   - *cedo* is 'give!' plus 'go'.
   - *ius* is 'law' plus 'broth'.

   Policy: keep both ids when both are secure and the minor sense has at least about 25% of the tokens. Otherwise keep the dominant sense, which is noted in the row.
5. **Right root, wrong lexeme.** *modus* → *módos* 'intoxication'; *genus* → *ǵenh₁ós* 'born'.
6. **Umbrian-specific errors.**
   - Suffix etyma for OCR fragments and English: *are* (English "are"), *alem*, *iu*, *trum*.
   - The postposition *-tu* mapped to *dwi-*.
   - *sve, sue* 'si' → *swé*; it is *so-*.
   - *uerfale* → 'word'; it is *urbs*.
   - *urnasier* → 'spring'; de Vaan derives it from *orior*.
   - *mani, manf* → *sméh₂r̥*.
   - *pars* (it belongs with *par*).
   - *śihitu* → *kenk-* 'hunger'.

## What remains

- **Latin below rank 300** is unchecked. The seed-1 errors are typical: *carcer, nuntius, plaustrum* (no etymology), *consuesco* (prefix only). Partials remain: *pluuius* ('ship' lexeme), *significo* (+ 'suckle'), *ciuis, celo, ruo*. The same union patterns (items 1 and 4) surely recur in the tail.
- **Coverage gaps.** Many frequent compounds stay unmapped (*ualidus, educo, dego, intelligo, cogito, perspicio*), and so do lemmas with no secure etymology (*uxor, causa, pectus, aequus*). A rule mapping prefixed compounds to their base verb would add much more than hand rows.
- **Lexicon gaps.** These words were unmapped because their correct etymon is not in the lexicon:
  - *manus* 'hand' (*mon-u-*)
  - lēvis 'smooth' (*leh₁i-u-*)
  - *ius* 'broth' (kept out by the dominant-sense rule)
  - the ōs-derived *ora*
- **The Umbrian text** is the limiting factor, not the etymologies. Over a third of the sampled "Umbrian" types are Buck's English or Latin. Most real forms (*Iiouina, Fisiu, Cerfi, pesnimu, serfer, futu, feitu, tefer*) never reach a lemma. Better ways forward than more lemma overrides:
  - a stricter column split, for example dropping lines inside the commentary
  - more `form` rows, for example *feitu* → *fetu* and *tefre/tefer* → *tefra*
- **Test conflict.** `tests/test_mapping_overrides.py::test_override_table_covers_the_errata` asserts that the merged override set equals the shared errata. It fails once any group file exists, and so fails for every group. It needs updating outside this task.
