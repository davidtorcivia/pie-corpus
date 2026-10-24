# Mapping precision, Germanic-new and Balto-Slavic-new: independent check (seed 41)

This is a blind re-measurement of the eight Stage C word → PIE tables built in round 4:

- **Germanic:** `menota`, `icepahc`, `rea-goh`, `rea-osx`. Built by `pie/germanic_new_mapping.py`, with overrides in `mapping-overrides/germanic-new.json`, including its `proto` rows.
- **Balto-Slavic:** `vuk`, `byliny`, `dainos`, `ccmh`. Built by `pie/bsl_mapping.py`, with overrides in `balto-slavic-new.json`.

Both building agents judged their own "after" samples, partly on items they had already fixed. Their reports are `mapping-precision-germanic-new.md` and `mapping-precision-bsl-new.md`.

**Outputs:**
- Per-item verdicts: `data/research/formulas/independent-checks/gmc-bsl-seed41.jsonl` (480 rows).
- Each row has the table, the lemma (and the surface form for BSL), tokens, ids, the verdict, the lemmatization verdict, the error type, the locator, a note, and who judged it.

No other file was changed.

## Method

**Blinding.** The self-reports, `bsl-precision-verdicts.json` and the override notes were not opened until all 480 verdicts were written. Only then were the self-reports read for the comparison below.

**Population.** The mappings were applied exactly as the modules apply them; nothing was rebuilt or written.

- **Germanic.**
  - Tokens come from `load_menota`, `load_icepahc` (default `max_year=1400`, as in the self-report sample) and `load_rea` (rea-goh / rea-osx).
  - Only content tokens (`Token.content`) count.
  - The mapping is `gm.read_table(corpus)`, with the overrides applied.
  - The unit is the corpus lemma string, as in the Germanic self-report.
- **Balto-Slavic.**
  - Built with `bm.build_mappings`, then `ocs_mapping`, then `add_derksen_lt`, as `scripts/build_bsl_mapping.py` does. Then `bm.UNITS[c]`, `bm.corpus_words` and `bm.lemmatizer(c, …)`.
  - Content filter: `lm.is_content`.
  - Proper names are skipped with `bm.is_name` (capitalised, not line-initial).
  - The mapping is `bm.read_table(corpus)`.
  - The unit is the (lowercased surface, lemma string) pair, as in the BSL self-report, so lemmatizer errors can be judged.
- The mapped content tokens match the coverage both reports give, so these are the same populations:

  | table | mapped types | mapped content tokens |
  |---|---:|---:|
  | menota | 4,306 | 495,743 |
  | icepahc | 2,170 | 77,378 |
  | rea-goh | 3,785 | 108,666 |
  | rea-osx | 1,495 | 21,362 |
  | vuk | 9,438 | 135,951 |
  | byliny | 26,110 | 157,189 |
  | dainos | 9,669 | 49,117 |
  | ccmh | 13,702 | 73,764 |

**Sample.**
- 60 types per table, weighted by tokens: repeated `random.Random(41).choices` over the sorted types, with duplicates rejected.
- The self-reports drew differently: Germanic used Efraimidis–Spirakis keys at seed 7; BSL used the same `choices` draw at seed 8. All three draws are token-weighted, so the rates are comparable but the items differ.
- Overlap with the BSL seed-8 sample is 26 (surface, lemma) pairs. The two checks disagree on one of them: ccmh приѩсѧ, which I judge W.

**Verdicts.** Rubric fixed before judging:
- **Correct:** every id names the word's PIE etymon, a PIE lexeme the dictionary derives it from, or the right root. A suppletive lemma counts as correct when it has all its paradigm roots (vera, wesan, sīn: *h₁es- + *h₂wes-).
- **Partial:** the root is right but something else is off. Error types:
  - **sister-formation:** the right root, but a different PIE formation that is not the word's source (*faraną → *píporti);
  - **extra-homonym:** the right id plus a homonymous root;
  - **compound-member:** only one member of a compound or name is mapped.
- **Wrong:** a wrong root; a homograph; a loan; an etymology the dictionary rejects; or an etymology the dictionary calls unknown or uncertain where the mapped root is only one suggestion ("insecure-etymology").
- **Lemmatization** is judged separately (ok / wrong / unverifiable):
  - **BSL:** is the surface form an inflection of the lemma?
  - **Germanic:** is the corpus lemma's dictionary headword the right word? Menota tokens carry no surface, so its form-table lemmatization is not checked.
- **Sources:**
  - Germanic: Kroonen 2013 (`raw/books/text/kroonen-pgmc/`, scan page as locator), and otherwise the kaikki Proto-Germanic or daughter entry.
  - Balto-Slavic: Derksen EDSIL / EDBIL (`derksen-slavic/`, `derksen-baltic/`, scan page) and kaikki.
  - All read with grep / `python3 -I`; nothing under `raw/` was executed.
  - Kroonen's OCR hides many headwords (ū → ii, ō → 6), so about 40% of Germanic locators are kaikki entries.
- **Who judged.** I judged the four Germanic tables. Two forks of this checker judged the BSL tables, each with the same rubric file: vuk + byliny, and dainos + ccmh. They were equally blind. I then reviewed all 240 BSL verdicts and left the verdicts unchanged; three error-type labels were harmonised (see Errors).
- **Intervals:** Wilson 95%, n = 60.
- **Comparison test:** two-sided Fisher exact test against the self-report's after-sample (n = 100).

## Results

Three readings of the same verdicts:
- **strict:** only *correct* counts.
- **root-level:** comparable to the self-reports' C. Sister-formation partials count as correct, because both self-reports judge at root-group level. A wrong lemma counts as W, as in the BSL self-report.
- **lenient:** correct + partial, with a wrong lemma counted as W. Comparable to the self-reports' lenient C + P.

| table | C / P / W (n = 60) | strict | root-level | lenient | lemmatization wrong | token share of C | self-report after: C / P / W (n = 100) | self root-level | self lenient | Fisher p (root / lenient) |
|---|---|---|---|---|---|---:|---|---|---|---|
| menota | 56 / 2 / 2 | 93% (84–97) | 95% (86–98) | 97% (89–99) | 0 | 0.95 | 96 / 3 / 1 | 96% (90–98) | 99% (95–100) | 1.00 / 0.56 |
| icepahc | 50 / 6 / 4 | 83% (72–91) | 87% (76–93) | 93% (84–97) | 1 | 0.94 | 93 / 7 / 0 | 93% (86–97) | 100% (96–100) | 0.26 / **0.02** |
| rea-goh | 53 / 3 / 4 | 88% (78–94) | 92% (82–96) | 93% (84–97) | 0 | 0.96 | 98 / 2 / 0 | 98% (93–99) | 100% (96–100) | 0.10 / **0.02** |
| rea-osx | 49 / 7 / 4 | 82% (70–89) | 85% (74–92) | 92% (82–96) | 1 | 0.80 | 96 / 3 / 1 | 96% (90–98) | 99% (95–100) | **0.02** / **0.03** |
| vuk | 55 / 1 / 4 | 92% (82–96) | 92% (82–96) | 93% (84–97) | 0 | 0.99 | 95 / 0 / 5 | 95% (89–98) | 95% (89–98) | 0.50 / 0.73 |
| byliny | 57 / 0 / 3 | 95% (86–98) | 95% (86–98) | 95% (86–98) | 0 | 0.99 | 90 / 3 / 7 | 90% (83–94) | 93% (86–97) | 0.37 / 0.74 |
| dainos | 53 / 4 / 3 | 88% (78–94) | 85% (74–92) | 90% (80–95) | 3 (+1 unverifiable) | 0.95 | 84 / 5 / 11 | 84% (76–90) | 89% (81–94) | 1.00 / 1.00 |
| ccmh | 55 / 1 / 4 | 92% (82–96) | 93% (84–97) | 93% (84–97) | 0 | 0.97 | 98 / 1 / 1 | 98% (93–99) | 99% (95–100) | 0.20 / 0.07 |

Notes on the table:
- The C / P / W column is the etymology verdict only, with each lemma taken as given.
- Dainos root-level is below strict because three etymologically correct items have a wrong lemma.
- "Token share of C" is the share of the sampled tokens that fall on correct items with a correct lemma.

**Pooled (240 per group):**

| group | strict | root-level | lenient | self root-level (n = 400) | self lenient | Fisher p (root / lenient) |
|---|---|---|---|---|---|---|
| Germanic | 87% (82–90) | 90% (85–93) | 94% (90–96) | 96% (93–97) | 99.5% (98–100) | **0.003** / **< 0.001** |
| Balto-Slavic | 92% (87–95) | 91% (87–94) | 93% (89–96) | 92% (89–94) | 94% (91–96) | 0.88 / 0.62 |

## Comparison with the self-reports

**Germanic: overstated.**
- Root-level precision is 90% (85–93), against the self-reported 96%. Lenient is 94%, against 99.5%.
- The gap is significant pooled, and per table for rea-osx, and for the lenient reading of icepahc and rea-goh.
- Menota alone agrees with its self-report.
- The self-report itself warned that its after-figures were biased upward: 36 of 400 items mapped through an override, and the fixes were written after seeing the before-sample. This check confirms the bias: on a fresh seed, about 1 type in 10 is still partly or wholly wrong at root level.
- None of the 14 Germanic W items below is touched by `germanic-new.json`: no lemma or proto row names them.
- The `proto` row for *kannijaną says the *ǵenh₁- 'beget' id was dropped. OS kennian / antkennian still carry `pie-lex-gjonh1eyeti`, reached through the lexicon reflex list. The self-report flags this as a known residual.

**Balto-Slavic: confirmed.**
- Pooled 91–93%, against the self-reported 92–94%.
- No table differs significantly. byliny comes out higher (95% vs 90%) and ccmh lower (93% vs 98%; lenient p = 0.07).
- The BSL agent's caveat that its after-sample was not independent turns out not to matter.
- Dainos is the weakest table in both checks. Its lemmatization errors (3/60, 5%) are the only lemmatizer errors found in any BSL table.

## Errors found

### Etymology vs lemmatization

| table | etymology wrong (W) | etymology partial (P) | lemmatization wrong |
|---|---:|---:|---:|
| Germanic, 4 tables | 14 | 18 | 2 |
| Balto-Slavic, 4 tables | 14 | 6 | 3 |

**Lemmatization errors.**
- **Germanic.** Corpus lemma strings that merge two words: ReA OS *god* 'God' / *gōd* 'good' (880 tokens; both etyma mapped, P). IcePaHC *val* 'choice' was read as the prefix *val-* 'foreign' and mapped to *wĺ̥kʷos 'wolf' plus *welh₁- (W).
- **Dainos.** These are surface → lemma errors:
  - bėdės → besti 'dig' should be bėda 'trouble';
  - pįsi → pisti should be pinsi, from pinti 'plait';
  - girėlė → gira 'kvass' should be girelė 'little wood'.

  The etymology of each wrong lemma is itself right, so these count only in the root-level and lenient readings.
- **vuk, byliny, ccmh:** none found among the mapped items. Several OCR'd pre-reform byliny forms (рфкъ, рёк, свфтъ) were checked against the OCR text and are lemmatized correctly.

### Error types (W and P), with every sampled case

**Homographs in the kaikki chain** (W, 10; IcePaHC *val* is listed under lemmatization above):
- IcePaHC *sótt* 'sickness' (< *suhtiz) went through the supine *sótt* of *sǿkja* to *séh₂gyeti.
- IcePaHC name *Áki* (< *anô 'ancestor') went to *h₂en- 'on, onto'.
- OHG *muos* 'food' (*mōsą) went to *musą 'moss'.
- OS *malt*, glossed first 'Malter (Getreidemaß)', went to *moldos.
- vuk *podići* 'raise' (2 types) went through the homograph pod- + ići to *h₁ey- 'go'. The BSL self-report fixed the earlier *dvignǫti → 'two' error by unmapping. The form now falls through to the other kaikki homograph, so the fix introduced this error.
- dainos *tarti* 'say' (2 types) went to *ter- 'tender' instead of *ter- 'cry out'.
- ccmh приѧти 'receive' went through приꙗти 'be pleasing' to *priH-.

**Wrong root** (W, 5):
- OHG *sceinen* 'show' went to *skey- 'split'. It belongs to the 'shine' root (Kroonen p0485 *skīnan-).
- OS *thiustri* 'dark' went to *tewh₂- 'swell'. Kroonen p0577 has *þemestra- < *temh₁es-ro-.
- OS *slitan* 'tear' went to two *leyd- roots ('let', 'play').
- IcePaHC *ógurligr* went to *h₂óḱris 'sharp edge'. It comes from ǿgr < ǿgja 'frighten'.
- byliny терять went to *ter- 'tender' through the suffix *-tḗr in its path.

**Etymology rejected by the dictionary** (W, 6):
- Menota *smár*: Kroonen p0496 says 'exclusively Germanic'.
- vuk *prsa*: Derksen p0440 says 'better abandoned'.
- vuk *porod* < *rodъ: Derksen p0448 says 'only Balto-Slavic'.
- byliny кость → *kes-: Derksen p0250 does not give it.
- ccmh отъвѣщати and съвѣтъ → *wekʷ-: Derksen p0531 says the root of *větъ is only Balto-Slavic.

**Insecure etymology** (W, 7). The dictionary calls the etymology unknown or uncertain, and the mapping takes one suggestion:
- Menota *krefja*;
- OHG *folgen*;
- OHG and OS *folk* (*fulką, 2 types);
- byliny ряд;
- dainos *paukštis*;
- ccmh рꙑба.

This is the softest W category. Counting it as correct would raise Germanic root-level to 91% and BSL to 92.5%. In the jsonl, the forks had labelled the three BSL cases `false-etymology`; I harmonised them to `insecure-etymology`, with a note.

**Sister formation** (P, 9):
- ON *fara* / OHG and OS *faran* → *píporti, in all four Germanic tables. This is the single largest error by tokens: 11,148 sampled tokens, and Menota *fara* alone has about 8.9k tokens. Kroonen p0168 gives *por-e-, and Skt. píparti is only a cognate. The lexicon reflex link sends *faraną to the reduplicated present.
- IcePaHC *bót* → *bʰódeti.
- OHG *bidecken* (*þakjaną) → *(s)togo-.
- OS *wīti* (chained as a form of *witan*) → perfect *wóyde.
- dainos *sėsti* → *sísdeti.
- ccmh възбоꙗти → perfect *bʰebʰóyh₂e.

**Extra homonymous root** (P, 9):
- Menota *leyfi* (both *lewbʰ-);
- OHG *gilouba* (adds *laubą 'leaf');
- IcePaHC *haukr* (both *kap-);
- OS *kennian* / *antkennian* (*ǵenh₁- kept);
- vuk *kopati* (both *skep-);
- dainos *vesti*, *vadinti*, and the union *giria|girti*.

**Compound or name member only** (P, 5): IcePaHC *rannsaka*, *hátíð*, *Gunnarr*; OS *herusēl*, *sigidrohtin*. In most of these the mapped member is not the head.

## Caveats

- **Sample size.** n = 60 per table, so single-table intervals are about ±8–12 points. Only the pooled Germanic difference is robust.
- **Two judges.**
  - The Germanic tables were judged by me and the BSL tables by two forks of this checker, all on one written rubric, blind to the self-reports.
  - On review, the forks were if anything more lenient on formation than I was. For example, мощи → perfect *memógʰe and vėjas → *h₂weh₁yús were left correct because kaikki derives them from that etymon or root. The root-level column is insensitive to this.
- **Thin evidence for some verdicts.**
  - About 40% of the Germanic locators and many ccmh locators are kaikki entries, because the Kroonen and Derksen OCR could not be searched reliably for the headword.
  - Those items were judged on the kaikki etymology plus standard handbook knowledge. A "correct" on such an item means not contradicted, not confirmed by Kroonen or Derksen.
- **Disagreements with the Germanic agent's rubric.** Its P includes "one component of a compound" (slíkr = *swa + *-līkaz). I treated *-līkaz as a suffix and judged slíkr correct. This choice is in its favour.
- **Not covered.**
  - Coverage, and mappable but unmapped words, were not checked.
  - The Menota form-table lemmatization was not checked: there is no surface in the tokens.
