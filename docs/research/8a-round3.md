# Phase 8a, round 3 (2026-10-23): every branch with a corpus

**Verdict: the infrastructure works, and the measurement shows no gain on the classical core yet.**
- **What was built.** The search now covers 15 corpora in 8 branches, with a lemma → PIE mapping for 13 daughter languages. On Vedic + Homer alone the N-branch code reproduces round 2's ranking exactly.
- **What adding corpora did.** The new corpora do not raise recall on the 24-item sanity set. Recall@200 is 0.46 vs 0.50, and recall@50 falls from 0.29 to 0.17. Only 5 of the 24 known items gain a third-branch witness.
- **What the candidate lists contain.** The top of each new ranking is mostly known merisms, generic collocations and mapping errors. The ranking is one-sided by construction: a pair very significant in one branch and merely present in another ranks high.
- **Status.** None of the candidates below is a finding. All are unreviewed. The confirmatory evaluation on the Schmitt/Matasović set comes later, from a separate agent. Nothing here was read from or tuned on that set.

Code:
- `pie/formula_search_multi.py`: mapping chains, keys, loaders, N-branch scoring.
- `scripts/formula_search.py round3`: about 75 s end to end.
- Tests: `tests/test_formula_search_multi.py`.

Outputs, in `data/research/formulas/`:
- `mapping/<corpus>.jsonl`: corpus lemma, dictionary word, lexicon ids, path, how, confidence and sources. No corpus text.
- `evaluation-r3.json`: coverage, the sanity rows, the regression check, third-branch witnesses, the shuffled baseline and the GLAUx subset.
- `candidates-r3-{a,b,c}.jsonl`: top 100 per ranking.
- `spot_checks_r3.json`: every spot-check verdict.

## 1. Data and licences
| corpus | branch | what | unit | licence |
|---|---|---|---|---|
| rv | Indo-Iranian | Rigveda, VedaWeb (round-2 corpus and mapping) | pāda | CC BY |
| av | Indo-Iranian | DCS: Atharvaveda Śaunaka (text 464) and Paippalāda, Ṛgvedakhilāni. Excluded: the DCS Ṛgveda (it duplicates VedaWeb), the Saṃhitās with Brāhmaṇa prose (TS, MS), and all later texts | DCS sentence (≈ half-verse) | CC BY 4.0 |
| ae | Indo-Iranian | Avesta, CAB Linguistic Corpus, all `ab` except Pahlavi | `ab` segment | **NC** |
| hom | Greek | Iliad + Odyssey, AGDT (round 2) | line | CC BY-SA |
| grp | Greek | GLAUx archaic/classical poetry (below) | verse line | CC BY(-SA); 23 texts NA/NC/other |
| lat | Italic | LASLA: Plautus, Lucretius, Catullus, Cato | line | **NC** |
| xum | Italic | Iguvine Tables, Buck 1904 OCR | OCR line, Umbrian column | PD |
| non | Germanic | Poetic Edda, Finnur Jónsson 1926 OCR | verse line | PD |
| ang | Germanic | Beowulf + Finnsburh (Gutenberg), plus Grein's *Bibliothek* I–II OCR (Grein's Beowulf skipped) | line | PD |
| got | Germanic | Gothic Bible, PROIEL | sentence | **NC**, translation |
| sga | Celtic | UD Old Irish (Würzburg/St Gall glosses) | sentence | CC BY-SA / NC |
| cu | Balto-Slavic | OCS: Marianus, Zographensis, Suprasliensis, Psalterium Sinaiticum, Vita Constantini, Vita Methodii, Kiev Missal, Chrabr, Euchologium (PROIEL/TOROT) | sentence | **NC**, translation |
| lv | Balto-Slavic | Latvian dainas quoted «…» in the book in `raw/books/text/dainas-endzelins` | quotation | OCR, copyright not checked |
| xcl | Armenian | Classical Armenian NT, PROIEL | sentence | **NC**, translation |
| hit | Anatolian | TLHdig, every manuscript, Hittite-language lines | tablet line | CC BY 4.0 |

**Licences of derived files.** The mapping tables for corpora with NC annotation (`got`, `xcl`, `cu`, `ae`, `lat`) are lemma lists derived from that annotation. They contain no text, but they inherit research-only status. None of the NC corpora may feed released training data.

**GLAUx subset.** 137 texts: ENDDATE ≤ −400 and genre Epic poetry, Lyric poetry or Tragedy, TLG 0012 (Homer) excluded. That is 395,721 tokens by metadata, 340,300 words after dropping punctuation.
- Contents: Hesiod (0020), the Homeric Hymns (0013, 32 texts), Theognis, Pindar, Bacchylides, Simonides, Aeschylus, Sophocles, Euripides, plus the epic and lyric fragments.
- Licences: 105 texts CC BY-SA 4.0, 9 CC BY 4.0. Research-only: 21 texts marked NA (Hesiod Fragmenta 0020-004/-007, Epigoni, Thebaïs, Archilochus Fragmenta lyrica, Septem Sapientes…), 1 CC BY-NC-ND (Margites) and 1 OpenEdition (Anacreon 0237-003).
- The full list with ids is in `evaluation-r3.json` (`glaux_subset`).

**Used for the mapping only:**
- kaikki daughter dumps.
- The proto-language dumps: PGmc, PCelt, PBryth, PBSl, PSlav, PIIr, PIran, PItal.
- The all-languages split files: Avestan, Proto-Norse, PWGmc, PIA, Proto-Armenian and Proto-Baltic, filtered by `lang_code`. The `proto-hellenic` and `proto-anatolian` split files contain only PIE pages, so they add nothing.
- The lexicon's reflex lists.
- Kloekhorst's EDHIL: headwords and PIE lines only, nothing of the running text stored; see §2.

**Not used:**
- *Thesaurus Palaeohibernicus*: only 17–19% of its OCR words lemmatize. Its Irish is mixed with Latin and English and badly recognized. Celtic is therefore UD only, 820 tokens: effectively absent.
- The Old Russian TOROT texts.
- The other Leiden dictionaries (Kroonen, Matasović PCelt, Derksen, de Vaan, Martirosyan), Beekes EDG, Cheung and EWAia: not needed beyond kaikki in the time available.
- Schmitt 1967, Matasović 1996, `eval-r3/`: not read (held out).

## 2. Mapping
A daughter lemma reaches a PIE lexicon entry through:
1. **Chain.** Its kaikki entry's inh/der/inh+/der+/uder/etymon templates, followed through the proto-language dumps (e.g. `cu:сꙑнъ > ine-bsl-pro:*sū́ˀnus > ine-pro:*suHnús`). Only sources in the language's own ancestry count.
2. **Desc.** A proto-page `descendants` tree that lists the word and is not marked borrowed.
3. **Lexicon.** The lexicon's reflex lists.
4. **Base.** A one-base derivation from a mapped same-language word.
5. **Form-of.** A form-of page pointing to a mapped lemma.

At each proto step, a lexicon-listed proto-form is preferred, because it gives the lexeme rather than the root.

Rejection rules:
- Any borrowing template (bor/lbor/bor+…) rejects the entry.
- A `der`/`inh` from outside the ancestry rejects it when no inherited link exists. Examples: Latin in OCS, Iranian in Armenian, `qfa-sub`.
- With an inherited link present, the entry is only *disputed*, which lowers its confidence to low.
- A proto-page that is itself a borrowing breaks the chain (PGmc *kaisaraz).

Confidence:
- **high**: a lexicon lexeme via chain/lexicon in ≤ 2 steps, or two agreeing sources.
- **low**: pseudo etymon (not in our lexicon), root-only, base chain, disputed, or several candidate lemmas.
- **medium**: the rest.

**Unlemmatized corpora.** These are lemmatized through the kaikki inflection tables and form-of pages:
- Exact key first, then a length-free key.
- Old Norse clitic stripping (*hefk, munk*).
- Latvian diminutive stripping (*kalniņā* → *kalns*).
- A form with several candidate lemmas of different etyma is dropped.
- A lemma that is also a function word in the dictionary (ON *ok* 'and'/'yoke', *á* 'on'/'river') is not counted as content.

**Avestan** has no inflection tables. A CAB form is matched to the longest dictionary stem (≥ 4 letters, length-free) followed by a listed ending. Forms under 4 letters are skipped.

**Hittite.**
- The TLHdig lemma is used only when the analysis is unique: one selected analysis, or all proposals sharing the lemma. Sumerograms and Akkadograms are dropped, also as stems (`LUGAL=u-`).
- Kaikki citation forms (3sg / nom.sg) are reduced to stems.
- Because stems collide (*pāi* 'gives' / *paizzi* 'goes'), a key whose candidates disagree is dropped.
- A match is also kept only if TLHdig's German gloss agrees with the English gloss. This uses a **hand-written table of about 230 German glosses** in the code (`HIT_DE_EN`). It is a curation step, and it sets a coverage ceiling: lemmas with uncovered glosses are dropped.
- Coverage of content tokens:

| Hittite source | coverage |
|---|---|
| kaikki + lexicon, raw | 30.1% |
| after the gloss check | 15.2% |
| Kloekhorst alone | +0.55% |
| final | 15.5% |

- **Kloekhorst was asked for as the primary source but could not be.** The extracted text layer drops the private-font glyphs (ḫ, w, some long vowels) from headwords *and* PIE lines: *ḫalki-* appears as *alki-*, *šiu-* as *šu-*. A damaged-key matcher (h/ḫ/w deleted on both sides, unique on both sides) finds about 40 lemmas. On the overlap with kaikki, 1 agrees and 2 disagree. Its leading-segment fallback was wrong in 2 of 3 checked cases and was removed. EDHIL is therefore only a second source.
- A known error survives the gloss check: *dai-* 'setzen' → *dóh₃ey* (it should be *dʰeh₁-*).

**DCS and GLAUx** use the round-2 machinery:
- DCS lemmas join the RV mapping by accent-free key, then the round-2 kaikki Sanskrit links.
- GLAUx lemmas use the round-2 kaikki Greek mapping with the round-1 rules as backoff.
- Note: round-2's Sanskrit and Greek links still accept `bor` templates.

### Coverage and precision
Content tokens mapped (types = distinct content lemmas). "Lexeme-level" is the share of mapped tokens that reach a lexeme or pseudo entry, not only a root.

| corpus | tokens | content tokens | units | mapped content tokens | mapped types | lexeme-level | spot check (30 types) |
|---|---:|---:|---:|---:|---:|---:|---:|
| rv | 164,758 | 118,887 | 39,832 | 65.4% | 1,829 / 9,599 | 69% | (round 2: 30/30 incl. homographs) |
| hom | 200,145 | 116,533 | 27,760 | 70.1% | 2,750 / 8,165 | 72% | (round 2) |
| lat | 144,786 | 73,932 | 18,420 | 57.2% | 1,863 / 7,865 | 71% | (round 2) |
| av (DCS) | 114,639 | 75,828 | 14,733 | 61.5% | 1,570 / 7,084 | 68% | 23/30 |
| grp (GLAUx) | 340,300 | 190,580 | 57,781 | 69.4% | 4,046 / 16,967 | 66% | 29/30 |
| ae | 103,999 | 103,999 (no POS) | 15,234 | 21.8% | 753 / 11,749 | 72% | 25/30 (surface→lemma 20/20) |
| got | 56,315 | 27,583 | 5,457 | 73.7% | 1,646 / 3,018 | 78% | 25/30 |
| non | 48,387 | 31,166 | 13,801 | 52.2% | 1,724 / 8,739 | 83% | 27/30 (surface 12/20 before the function-word fix) |
| ang | 104,566 | 57,798 | 15,606 | 44.2% | 3,176 / 19,257 | 84% | 26/30 (surface 19/20) |
| sga | 820 | 329 | 98 | 54.1% | 125 / 246 | 72% | 21/30 |
| cu | 213,654 | 112,896 | 23,991 | 47.3% | 1,150 / 7,814 | 81% | 25/30 |
| lv | 7,815 | 5,967 | 727 | 34.1% | 434 / 2,433 | 86% | 21/30 (surface 16/20) |
| xcl | 21,060 | 9,430 | 1,916 | 47.8% | 260 / 1,498 | 70% | 20/30 |
| hit | 255,181 | 185,489 | 145,617 | 15.5% | 165 / 9,751 | 85% | 27/30 (types deduplicated) |
| xum | 8,775 | 8,723 (no POS) | 2,218 | 13.3% | 319 / 2,879 | 92% | 28/30 |

**How the spot check was run.**
- The sample is uniform over mapped *types* (seed 7). That is harsher than round 2's token-weighted sample.
- Wiktionary's speculative etymologies count as wrong. Most of the Armenian errors are of this kind.
- For the unlemmatized corpora, a second sample of 20 tokens checks surface → lemma → etymon as a whole.
- Verdicts and reasons are in `spot_checks_r3.json`.

**Error sources, most frequent first:**
1. Homograph entries: *mǣre* 'famous' vs 'border'; *ingen* 'daughter' vs 'nail'.
2. Speculative or suffix etyma: endings mapped to *-oms*, *-ālis*.
3. Loose-key collisions: OIr *nóib* → *nau*.
4. Inherited round-2 RV errors: √śr̥ 'crush' → *ḱlew-*; *vṛtrá-* → *h₂wer-*.

**Lexeme granularity.** In the new branches, 70–92% of mapped tokens reach a lexeme or pseudo entry. The other 8–30% stop at a root and cannot meet a lexeme-level Vedic/Greek id. Only lexeme level was run. The group-level variant for rankings (a)/(b) was planned but not done.

## 3. Method
- **Counting:** content words, lexeme level as in round 2, presence per unit.
- **Per branch:** one one-sided test for each pair.
  - With one testable corpus (both lexemes occur), it is the exact hypergeometric test of round 2.
  - With several, it is a stratified test: Poisson on the summed co-occurrences with λ = Σ K·d/N, so each corpus keeps its own base rates.
  - Within-branch independence is not modelled. The Atharvaveda repeats roughly a seventh of the RV, and the stratified test sums their counts.
- **Translation witnesses:** Gothic, OCS and Armenian are translations from Greek, so they merge into one witness. Its p is the minimum p × the number of branches it merges.
- **Calques:**
  - Removed: co-occurrences in an NT verse where PROIEL's Greek NT has the same lexeme pair.
  - Not covered: Suprasliensis and the Psalter, which have no Greek source here.
  - Not caught: a translation of a *non-cognate* Greek pair. For example, OCS *nebo i zemlja* renders οὐρανὸς καὶ γῆ.
- **Candidates:**
  - A pair must co-occur in ≥ 2 witnesses and have p < 0.05 in at least one.
  - Score: Fisher's method over the witnesses where it co-occurs. Branches without a co-occurrence do not enter.
  - Two homograph entries of one written form are never paired.
  - Rankings: **(a)** ≥ 3 witnesses; **(b)** exactly 2, not Greek + Indo-Iranian; **(c)** exactly Greek + Indo-Iranian.
  - Pairs are deduplicated by root group, as in round 2. Homograph twins (the same counts under another entry) are folded into `homograph_alternatives`.
- **Regression:** on rv + hom without the significance filter, the new code's top 200 equals round 2's final ranking (200/200, same order).

## 4. Sanity measurement (24-item round-2 set, not confirmatory)
These are fixed settings, with no cross-validation and nothing selected. The set was used for tuning in round 2, so these numbers are descriptive only. The CIs are 95% bootstraps over items. The last column is the paired difference against the round-2 final setting at k = 200.

| setting | recall@50 / 100 / 200 | CI@200 | Δ@200 vs round 2 (paired CI) |
|---|---|---|---|
| round-2 final (rv + hom) | 0.29 / 0.46 / 0.50 | 0.29–0.71 | — |
| N-branch code, rv + hom, p < 0.05 in one | 0.29 / 0.46 / 0.50 | 0.29–0.71 | 0.00 |
| diagnostic: rv + hom + GLAUx | 0.33 / 0.46 / 0.50 | 0.29–0.71 | 0.00 (−0.13…+0.13) |
| diagnostic: rv + DCS-AV + hom | 0.25 / 0.33 / 0.46 | 0.25–0.67 | −0.04 (−0.13…0.00) |
| diagnostic: rv + Avesta + hom | 0.33 / 0.42 / 0.46 | 0.25–0.67 | −0.04 (−0.13…0.00) |
| all core corpora (rv, av, ae, hom, grp), core score | 0.17 / 0.42 / 0.46 | 0.25–0.67 | −0.04 (−0.17…+0.08) |
| all corpora, pairs with Greek + II witnesses, Fisher over all witnesses | 0.17 / 0.42 / 0.46 | 0.25–0.67 | −0.04 (−0.17…+0.08) |
| all corpora, every candidate pair (any branches) | 0.13 / 0.25 / 0.33 | 0.17–0.54 | −0.17 (−0.33…−0.04) |
| shuffled baseline (all corpora, Greek + II pairs; 3 seeds) | 0.01 / 0.03 / 0.04 | | |

**Reading the table.**
- The loss at k = 50 comes from adding the Atharvaveda (and Avestan) to the Indo-Iranian branch test, before any third branch enters. GLAUx alone is neutral to slightly positive.
- Third-branch witnesses change nothing, because few known items have them. Ranking all pairs together pushes the Graeco-Aryan items down among new pairs from other branch combinations, as expected.

**Items that gain a third-branch witness: 5 of 24** (one of them only through a translation):
1. *médʰu* + *sweh₂d-* 'sweet mead': OE *swētne medo* (Finnsburh 39).
2. *méǵh₂s* + *ḱlew-* 'great fame': OCS NT only, a translation.
3. *dyew-* + *peh₂-* 'Father Sky': Latin.
4. *sóh₂wl̥* + *deyḱ-*: Latin, at rank 1,965.
5. *gʷʰen-* + *serp-*: Latin, at rank 2,352.

## 5. Candidates
**Shuffled baseline.** Root labels were permuted within each corpus (3 seeds).

| class | real pairs | shuffled pairs | shuffled pairs above the real top-100 cutoff |
|---|---:|---:|---:|
| a | 470 | 388–477 | 1–4 (cutoff −log₁₀p 3.8) |
| b | 2,684 | 2,554–2,618 | 1 (cutoff 9.6) |
| c | 936 | 697–753 | 0 (cutoff 7.1) |

So the bulk of each class is chance, and only the top ~100 sits clearly above the shuffle. The shuffle cannot detect mapping artefacts, though: homograph roots, Avestan stem collisions and inherited round-2 errors. These are the main error source at the top.

**One-sided by construction.**
- Top 100 with ≥ 2 witnesses at p < 0.05: (a) 53, (b) 44, (c) 32.
- Top 100 whose weakest witness has p ≥ 0.5: (a) 38, (b) 19, (c) 31.
- Top 100 relying on the merged translation witness: (a) 53, (b) 42.
- This reproduces round 2's finding: the ranking mostly finds pairs strongly significant in one branch and merely present in another. `weakest_witness_neglog10p` and `n_witnesses_p05` are in every record, so a reviewer can filter.

Below are my preliminary judgements, from the loci and mapping paths only. **K** = known (in `formulas.jsonl` or West), **G** = generic collocation or merism, **M** = mapping error, **T** = rests on a translation witness, **I** = interesting.

**(a) ≥ 3 witnesses**

| # | pair | witnesses (co-occurrences / −log₁₀p) | judgement |
|---|---|---|---|
| 1 | *méh₂tēr* + *ph₂tḗr* | II 79/68.7, Gk 70/13.0, It 11/7.9, Gmc 3/2.9 | K/G: parental merism (round-2 review) |
| 2 | *gʷṓws* + *h₁éḱwos* | II 102/85.2, Gk 5/0.4, It 1/1.0 | G: cattle and horses |
| 3 | *h₂wéh₁n̥ts* + *h₁weh₂-* | II 39/65.0, It 1, Gmc 1 | M: vā́ta 'wind' + √vā homographs |
| 4 | *lówksneh₂* + *sóh₂wl̥* | II 2, It 17/25.3, OCS 9/20.4 | G/T: sun and moon; OCS is NT |
| 5 | *gʷṓws* + *h₂ówis* | II 12/7.6, Gk 13/13.6, It 6/11.5 | G: cattle and sheep (Cato) |
| 6 | *dyḗws* + *sóh₂wl̥* | II 95/22.6, Gk 3/0.2, It 13/8.4 | G/M: Latin *dies* + *sol* |
| 7 | *dyḗws* + *ph₂tḗr* | II 26/1.3, Gk 144/29.4, It 1 | K: Father Sky |
| 8 | *dyḗws* + *nókʷts* | II 5, Gk 8, It 24/28.3 | G: 'day and night' (Lat. *dies noctesque*) |
| 9 | *médʰu* + *swéh₂dus* | II 4/3.6, Gk 10/19.0, Gmc 1/2.6 | K + I: 'sweet mead' gains OE *swētne medo* (Finnsburh 39) |
| 10 | *dʰeh₁-* + *welh₁-* | II 12/0.0, It 145/23.7, OCS 1 | G/M: Cato's *facito … uolo*; RV p = 1 |
| 11 | *h₂éwis* + *peth₂-* | II 16/22.5, Gk 1, It 1 | G: birds fly |
| 12 | *méh₂tēr* + *peh₂w-* | II 29/22.4, Gk 1, It 1 | G: mother + son (putrá- < *peh₂w-*) |
| 13 | *dṓm* + *h₁éyti* | Gk 33/5.6, It 17/6.2, OCS 43/10.7 | G/T: 'go home' |
| 14 | *h₁régʷos* + *nókʷts* | II 2, Gk 12/17.7, Got 1 | G (Hesiod's Erebos and Night); Gothic is NT |
| 15 | *wortéyeti* + *dʰeh₁y-* | II 2/0.0, It 50/19.2, OCS 1 | M/G: Cato |

**(b) two witnesses, not Greek + Indo-Iranian**

| # | pair | witnesses | judgement |
|---|---|---|---|
| 1 | *gʷʰénti* + *h₂wer-* | II 128/94.0, OCS 1/1.9 | M: Vedic *vṛtrám han-* with vṛtrá- under *h₂wer-*. The Vedic dragon formula is real, the OCS hit is noise |
| 2 | *dʰéǵʰōm* + *nébʰos* | Hitt 34/45.7, OCS 80/49.9 | K/T: 'heaven and earth', Hittite *nēbis dēgan* (West ch. 9). The Slavic witness is NT |
| 3 | *gʷʰénti* + *welh₁-* | II 128/90.1, OCS 3 | M: as 1, another homograph |
| 4 | *séǵʰos* + *suHnús* | II 44/69.8, OE 1/0.3 | G: Vedic *sūnúḥ sáhasaḥ*; OE noise |
| 5 | *h₂wéh₁n̥ts* + *pleh₁-* | Av 58/57.9, Got 2 | M/T: Avestan stem collision in a repeated Yašt litany |
| 6 | *h₂eh₁ter-* + *peh₂w-* | Av 36/49.8, Lat 1 | G: Avestan-internal *ātar … puθra*; Latin noise |
| 7 | *sóh₂wl̥* + *dyew-* | II 132/38.0, It 3 | G |
| 8 | *h₁wésus* + *ḱwentos* | Av 116/39.3, OCS 1 | G: Avestan-internal *vohu*, *spənta* |
| 9 | *dédeh₃ti* + *déh₃rom* | Gk 46/31.8, OCS 13/6.2 | G/T: figura etymologica 'give gifts'; OCS NT |
| 10 | *wéyHs* + *dʰeh₁y-* | II 50/33.2, It 13/0.0 | M/G: Vedic *váyo dhā-*; Latin homograph |
| 11 | *wéyHs* + *dʰeh₁-* | II 47/31.8, It 13/0.0 | as 10 |
| 12 | *deḱsinos* + *sewyós* | Av 6/9.2, OCS 9/21.6 | G/T: right and left |
| 13 | *gʷm̥yéti* + *h₁éyti* | Gk 82/30.2, It 5 | G: come and go |
| 14 | *wéyh₁ō* + *dʰeh₁-* | Gk 3, It 55/27.8 | G: Cato's wine-making |
| 15 | *h₂ówis* + *peh₂-* | Gk 12/23.4, It 1 | G |

**(c) Greek + Indo-Iranian only**

| # | pair | witnesses | judgement |
|---|---|---|---|
| 1 | *ph₂tḗr* + *peh₂w-* | II 67/52.7, Gk 1/0.0 | G: father + son |
| 2 | *méh₂tēr* + *pótnih₂* | II 1/0.3, Gk 42/43.5 | K (Greek-internal πότνια μήτηρ); the AV witness is weak |
| 3 | *h₂éwsōs* + *sóh₂wl̥* | II 65/38.2, Gk 3/3.6 | G (round-2 review) |
| 4 | *médʰu* + *peh₃-* | II 62/34.3, Gk 5/7.4 | G (round-2 review) |
| 5 | *HéHḱus* + *h₁éḱwos* | II 8/6.0, Gk 40/33.8 | K: swift horses |
| 6 | *gʷṓws* + *welH-* | II 7/4.8, Gk 32/34.8 | M: valá- vs εἰλίπους (round-2 review) |
| 7 | *mensdʰh₁-* + *peh₂w-* | Av 98/35.3, Gk 1 | G: Avestan *mazdā … puθra*; Greek noise |
| 8 | *bʰéh₂os* + *sóh₂wl̥* | II 2/1.4, Gk 28/33.5 | K: φάος ἠελίοιο, the 'light of the sun' type (West ch. 2); the Vedic witness is weak |
| 9 | *dʰédʰeh₁ti* + *wéyHs* | II 47/34.0, Gk 1 | G: Vedic *váyo dhā-* |
| 10 | *dʰgʷʰey-* + *gʷeyh₃-* | II 22/32.3, Gk 1 | M: √kṣi homographs in the RV 10.58 refrain |
| 11 | *sóh₂wl̥* + *derḱ-* | II 47/31.0, Gk 1/0.7 | K: 'see the sun' = live (West ch. 2 cites RV 1.23.21); the Greek witness is weak |
| 12 | *dyḗws* + *wekʷ-* | II 7/0.0, Gk 34/30.1 | G/M: Greek-internal |
| 13 | *ḱey-* + *sel-* | II 1/0.3, Gk 14/28.1 | M: homograph roots (5 alternatives) |
| 14 | *dyḗws* + *lewk-* | II 51/28.0, Gk 1 | G: Vedic *rocanā́ diváḥ* |
| 15 | *h₂éwis* + *péth₂eti* | II 16/22.5, Gk 4/5.2 | G: birds fly |

**Nothing in these 45 rows is a new finding.**
- Known: 8 rows, among them the Hittite–Slavic 'heaven and earth' and the 'see the sun' type.
- Generic: 27 rows.
- Mapping error: 10 rows.
- Counts use each row's first label.
- The one useful result is confirmatory: 'sweet mead' gains an Old English witness (*swētne medo*, Finnsburh 39), independent of Vedic and Greek. An independent reviewer should check that it is an inherited collocation and not a natural one.

## 6. Limitations
- **Mapping is still the bottleneck.**
  - Coverage is low for Hittite (15%), Umbrian (13%), Avestan (22%) and Latvian (34%).
  - Precision is 67–97% per corpus on a harsh type sample.
  - The surviving errors are systematic (homographs, speculative Wiktionary etyma), so the same wrong pair can appear in several branches. The shuffle does not detect this.
- **Corpus quality.**
  - The Grein OCR: only lines with ≥ 60% lemmatizable words are kept, the raw rate is 57%, and loci are OCR line numbers.
  - The Edda OCR includes some of Finnur Jónsson's notes.
  - The Umbrian column split is heuristic, leaving about 1.2k mapped tokens.
  - The dainas are 727 quotations in a prose book, not an anthology.
  - Celtic is absent (820 tokens).
  - Hittite counts every manuscript of a composition, and tablet lines cut clauses.
- **Genre mismatch.** Gothic, OCS and Armenian are Bible translations. Merging them into one witness and removing aligned calques limits the damage. Translations of non-cognate Greek pairs still pass.
- **Statistics.**
  - Fisher over branches rewards one strong branch.
  - The within-branch stratified test treats the AV and RV as independent, though they share verses.
  - Only lexeme level was run.
- **The sanity set is small** (24 items, CI ±0.2) and was used in round 2. The real test is the Schmitt/Matasović set, which this round has not read.

## Next steps
1. Fix the systematic mapping errors at source: the round-2 RV homographs (vṛtrá-, √śr̥, √kṣi), suffix entries in kaikki, and the OIr loose key. Then rerun.
2. Add a second-witness requirement as a pre-declared variant (p < 0.05 in ≥ 2 witnesses). Report it beside the Fisher ranking on the confirmatory set.
3. Send the top of each ranking to an independent reviewer, as round 2's review was done. First in line: 'sweet mead' (OE), Hittite 'heaven and earth', and any pair with ≥ 2 significant non-translation witnesses.

## Erratum (2026-10-23)
The Old English witness for 'sweet mead' reported above (*swētne medo*, Finnsburh 39) is Ettmüller's emendation; the manuscript reads *hwitne* 'white' (Grein's apparatus; Tier 2 review r3, docs/audits/tier2-review-r3.md). 'Sweet mead' therefore has no Germanic witness in our corpora; the count of known formulas gaining a third-branch witness falls from 5 to 4.
