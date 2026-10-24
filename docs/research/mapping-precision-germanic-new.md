# Mapping precision: Germanic, new corpora (Menota, IcePaHC, ReA OHG and Old Saxon)

This report covers the Stage C lemma → PIE tables for four newly acquired corpora (docs/research/8c-preregistration.md, Stage C; sources in docs/research/daughter-sources.md and raw/MANIFEST.md).

## What was built

| corpus code | source | licence | tokens | content tokens | table rows |
|---|---|---|---:|---:|---:|
| `menota` | Menota, West Norse documents only (catalogue language isl, nor, non; the Old Swedish and Old Danish texts are left out) | CC BY-SA 4.0 | 1,651,610 | 965,752 | 4,547 |
| `icepahc` | IcePaHC 2024.03, files dated ≤ 1400 (the table also covers the later files) | CC BY 4.0 | 255,971 (≤ 1400) | 119,313 | 3,778 |
| `rea-goh` | Referenzkorpus Altdeutsch 1.2, tokens with lang `goh` | **CC BY-NC-SA 3.0: NC, research only** | 344,503 | 147,812 | 4,096 |
| `rea-osx` | the same, lang `osx` | **CC BY-NC-SA 3.0: NC, research only** | 59,706 | 30,445 | 1,664 |

- **Code.** `pie/germanic_new_mapping.py` holds the loaders (`load_menota`, `load_icepahc`, `load_rea`, or `load_corpus(code)`), the mapping, and `read_table(code)`, which applies the overrides. `scripts/build_germanic_new_mapping.py` writes the tables and `data/research/formulas/germanic-new-coverage.json`.
- **Tables.** `data/research/formulas/mapping/{menota,icepahc,rea-goh,rea-osx}.jsonl` use the round-3 row format plus `licence` and `research_only`. Every ReA row has `research_only: true` and an NC licence string. The rows are keyed by the corpus lemma string exactly as the loaders yield it, so the Stage C builder should use these loaders.
- **Corrections.** `data/research/formulas/mapping-overrides/germanic-new.json` holds 198 `lemma` rows (70 of them unmaps) and 45 `proto` rows (24 unmaps), and no `form` rows. Each row has a dictionary note.
  - `lemma` rows have the format of the other override files. Inside the module they are also applied to each `|`-alternative of a lemma string and to the base of a prefixed lemma.
  - `proto` rows are new. Each one corrects a Proto-Germanic or Proto-West-Germanic term while the tables are built, so the fix reaches every daughter word whose etymology chain passes through that term. `load_overrides` ignores the key.
- **Tests.** `tests/test_mapping_germanic_new.py` has 21 tests; the loader tests are skipped when `raw/` is absent. The full suite gives `2414 passed`.

**Content words.** Content words are nouns, proper names, adjectives and all verbs, auxiliaries included, as PROIEL's V is for Gothic. The tags are Menota xNC/xNP/xAJ/xVB, IcePaHC N/NS/NPR/ADJ/VB/BE/HV/MD/RD/DO/VAN/VAG, and ReA posLemma NA/NE/ADJ*/VV/VA/VM. A ReA lemma with alternatives counts as content only if every alternative does.

## Method

**Lemmas.** Every corpus supplies its own lemmas.

- **Menota.** In a lemmatized document the lemma is the `lemma` attribute, with Menota entities decoded (`&oogon;` → ǫ, `&aeligacute;` → ǽ).
  - The 21 unlemmatized West Norse documents include Codex Wormianus, the Hauksbók Vǫluspá, the c. 1700 Heimskringla copies and the law codes. They get their lemma from a form → lemma table built from the lemmatized documents.
  - That table uses only the normalized or diplomatic form, after Menota's letter-variant entities and characters (ſ, ꝛ, ꝼ, small capitals, enlarged initials) are reduced to their base letters. A form gets a lemma only if it was seen at least 3 times with a two-thirds majority; otherwise its lemma is `?form`.
- **ReA.** Alternatives (`abawesan¦…¦wesan¦sin`) become `a|b`. Tokens with mixed language codes (osx-goh) and Latin or Middle High German tokens are dropped.

**Lemma → PIE.**

1. The fm steps (chain / desc / lexicon / form-of / base) run over the kaikki Old Norse, Old High German and Old Saxon dumps.
2. Proto-West-Germanic and Proto-Norse pages, and the Icelandic entries, are cut from the all-languages dump. The `split/proto-west-germanic.jsonl` in raw/ holds only 72 gmw-pro pages, so OHG and OS chains through `gmw-pro:*X` failed before.
3. `BaseResolver` adds three things to the standard resolver:
   - A PGmc derivative takes the chain of its base (*hailagaz ← *hailaz; parse_entry misses parts written `*-gaz`).
   - No chain may pass through an affix page (*ga-, *-ī, *sin-).
   - The `proto` rows are applied.
4. IcePaHC lemmas are Modern Icelandic. They go through the Icelandic kaikki entry's Old Norse source (`is-bridge`). Failing that, they are matched against Modern → Old Norse spelling variants (maður → maðr, -ast → -ask, ft → pt). An Icelandic entry whose Old Norse source is a borrowing gives nothing (herra < OS hērro).
5. Lemma keys are tried exactly first, then without accents. For OHG/OS (ReA has no length marks) the accent-free key may match a headword; for Old Norse, where vowel length is written, it may not (lið 'host' ≠ líð 'ale'). A loose spelling skeleton comes last (Menota segia = segja, Old Norwegian lutr = hlutr). That skeleton is never used for a word that is itself a dictionary headword. Any loose match must name a single root group.
6. Prefixes are stripped (gi-, fir-, ir-, bi-, ú-, ó-, …), but never from a headword: kaikki gives a prefixed headword's base itself.
7. A proper name maps only through a kaikki name entry, never through a similar common noun (ReA *Aram* is not *aram* 'poor').
8. **Kroonen 2013** (facts only) is used in two ways:
   - **Bridge.** Each entry's OHG/OS/ON reflex words lead to its PGmc headword, which is matched to a kaikki PGmc page by stem key (unique matches only). This gives about 1,100 tokens, all at low confidence.
   - **Citation.** It is the dictionary cited in the override notes and used for the verdicts.

**Sample.** For each corpus, 100 mapped content types are drawn with token-frequency weights, using Efraimidis–Spirakis keys u^(1/count). Here u is derived from sha256("7:" + lemma) rather than from a list position, so seed 7 draws the same item for a lemma before and after the fixes. IcePaHC is sampled on the files dated ≤ 1400.

**Verdicts.**

- **C:** every id is a correct etymon of the lemma, at root-group level.
- **P:** the right root plus a wrong extra id, or one component of a compound or name only.
- **W:** no correct id.

The verdicts were judged against Kroonen (page cited in the verdict notes) and, for words Kroonen lacks, against the kaikki chain unless I knew it to be wrong. Intervals are 95% Wilson intervals at n = 100.

**Re-measurement.** After the fixes the same seed-7 procedure was rerun on the final tables. Of the 400 items, 342 kept both their mapping and their earlier verdict. The rest are new entrants (types that became mapped, e.g. the copula) or changed mappings, and were judged fresh.

## Results

| corpus | before: C / P / W | strict (95% CI) | lenient | after: C / P / W | strict (95% CI) | lenient (95% CI) |
|---|---|---|---|---|---|---|
| menota | 81 / 5 / 14 | 81% (72–87) | 86% | 96 / 3 / 1 | **96% (90–98)** | 99% (95–100) |
| icepahc | 79 / 11 / 10 | 79% (70–86) | 90% | 93 / 7 / 0 | **93% (86–97)** | 100% (96–100) |
| rea-goh | 89 / 4 / 7 | 89% (81–94) | 93% | 98 / 2 / 0 | **98% (93–99)** | 100% (96–100) |
| rea-osx | 84 / 5 / 11 | 84% (76–90) | 89% | 96 / 3 / 1 | **96% (90–98)** | 99% (95–100) |

**The "after" figures are biased upward.**

- 36 of the 400 after-items map through an override row (lemma or proto): 7 menota, 11 icepahc, 10 rea-goh and 8 rea-osx.
- Several of the fixes were written after the before-sample showed the error: Kroonen-rejected etyma, homonymous roots, the copula.
- Most fixes are systematic, made at the PGmc term or in the resolver rules, and reach words the sample never saw. Still, the gain on the sampled items overstates the gain on unseen ones.
- 166 of the 198 lemma rows concern lemmas outside both samples (frequent errors found in the etymon review, and Edda rows from `germanic.json` ported to Menota and IcePaHC spellings). They were not re-measured on a fresh seed.

**Coverage** (content tokens with a mapping):

| corpus | first build | final |
|---|---|---|
| menota | 48.5% | 51.3% (lemmatized documents 67.9%, form-table documents 33.6%) |
| icepahc ≤ 1400 | 61.3% | 64.8% (all years 62.0%) |
| rea-goh | 72.7% | 73.5% |
| rea-osx | 69.5% | 70.2% |

The first build's figures still contained wrong mappings, notably OHG *sin* 'to be' (9.8k tokens) mapped through the prefix *sin-*, and Menota form-table garbage such as *kall*, *kúla* and *rá* from unread ſ and enlarged-letter entities. Removing those offsets the gains: the copula (*vera*, *wesan*, *sīn*: 66k tokens), gmw-pro pages, prefix stripping, PGmc base chains. 90% of mapped tokens are lexeme-level. For comparison, the older Germanic corpora reach got 73%, non (Edda) 52% and ang 42%.

## Main error types and fixes

1. **Missing Proto-West-Germanic pages.** OHG and OS chains run through gmw-pro, so they failed until the pages were cut from the all-languages dump (source fix).
2. **The copula.** *vera/vesa*, *wesan* and OHG *sīn* resolved to the blocked `pie-lex-sh1es` or to the prefix *sin-*. They are now mapped to `pie-lex-h1esti` and `pie-lex-h2weseti` (Kroonen *wesan- 1, p0622), including inside ReA's alternative strings and prefixed forms (aba-, ana-, furi-wesan). *synd*, *sunta* and *sundea* go to `pie-root-h1es-be`.
3. **Etymologies Kroonen rejects or calls unknown** (proto rows, so all four corpora are fixed at once):
   - **No certain etymology:** *hugi- (hugr, hyggja, hugi, gihuggen), *mawi-, *ginnan-, *wintru-, *swerda-, *deurja-, *þeuba-, *aiþa-.
   - **Wrong root:** *managa- (not *meǵh₂-), *handu- (not *ḱomt), *bagma- (not *bʰuH-), *breusta- ('swell', not 'break'), *haleþ-, *þwahan-.
   - **Loans:** *rīk- from Celtic, *lēkja- from Celtic, *scrīban* from Latin.
   - **Lemma rows:** gamall, lítill/luzzil, eyrir (< Lat. aureus).
4. **Homonymous root sets** (a root string expanding to several lexicon roots) were narrowed to one root by proto or lemma rows: *gangan- (drop *h₁eh₁oye), *haitan-, *weraldi-, *Harjawaldaz, *walda-, *neutan-, *wlītan-, *brinnan-, *kannjan-, and sýna/sjón, bjǫrn, dróttning.
5. **Homographs in the dictionaries.**
   - Desc-tree or key collisions, each fixed by a lemma row: gǫrr 'ready' → *gurą 'dung'; merki → *mari 'sea'; bót → *buhtiz; vetr → *wihti-; OHG wār 'true' → *wiHrós 'man'; OS hēr → *ḱís 'this'.
   - Kroonen re-dates *maþla- (*mad-tlo-, to *mōtan- 'meet'), so ON mál/mæla 'speech, speak' go to *meh₂d- 'meet', not to *mēla- 'time'.
   - Kroonen says *mati- 'food' is *med- 'satiate', and calls the link with *meh₂d- 'be wet' 'erroneous'. Note that `germanic.json` maps ON matr to `be_wet`, which Kroonen's own entry contradicts.
6. **Source rules added after seeing errors:**
   - no chain through affix pages (OHG *truoben* → *-ī → *iz 'he');
   - prefix remainders matched exactly or without accents only (OHG *zellen* → ze- + *len* 'soft');
   - no loose match for a headword;
   - no prefix split of a headword (IcePaHC *andlegur* → and- + legr);
   - names only through name entries;
   - Icelandic bridge refused when its Old Norse source is a borrowing;
   - no `and-` prefix in Old Norse;
   - Kroonen bridge on remainders of at least 4 letters.

## What remains

- **Residual P and W items after the fixes.**
  - Lemma strings that cover two words cannot be split, because the tables are keyed by lemma alone: OS *god* 'God'/'good', ON *hár*, *mál* 'time', OHG *rad*.
  - Names and compounds get only one component (Gunnarr → *harjaz; slíkr → *swa).
  - *halda* (*kel- 'drive' plus a ḱ- lexeme: Kroonen's entry is unreadable in the OCR).
  - Ids entered through the lexicon's own reflex lists, which proto rows cannot reach (OS *ankennian* keeps a *ǵenh₁- id).
  - The Old Norwegian h-loss skeleton maps Icelandic *raun* 'trial' to *hraun* 'lava'. It is right for ross, ryggr, hlutr and hlaupa; *raun* is the one sampled error, and *rata* is at risk.
- **Coverage gaps that are not mapping errors.**
  - Frequent words with no PIE etymology in kaikki or Kroonen: ON *gera*, *skip*, *hús*, *jarl*; OHG/OS *mennisco*, *heilant*, *sela*. OHG *magan* is unmapped only because ReA uses the Köbler lemma, while kaikki and Kroonen have *mugan*.
  - Latin and Christian loans: *Krist*, *biskup*, *kirkja*, *engil*, *muddi*.
  - Names.
  - In Menota's unlemmatized documents a third of content tokens get no lemma (form-table coverage 33.6%), so Codex Wormianus and the law codes are only partly mapped.
- **For the Stage C builder.**
  - Load with `germanic_new_mapping.load_corpus(code)` and look lemmas up in `read_table(code)`.
  - Keep ReA material research-only (NC), and keep its derived units NC as well.
  - Menota tokens carry `units['lemma_source']`. Units whose words came from the form table are less reliable; the builder may want to report them separately.
  - IcePaHC spelling is modernized, and its pre-1400 texts are prose; there is no eddic verse in it.
- **Not done.**
  - No fresh-seed re-measurement.
  - The 300-most-frequent check was done per PGmc etymon over all four corpora (the top 400 of 3,682 etyma, covering 86% of mapped content tokens), not as 300 lemmas per corpus.
  - Kroonen's OCR is too damaged (6 for ó, ii for ú, lost ḱ/h₂) to use his PIE lines directly.

## Appendix: sampled items judged P or W (seed 7)

**Before the fixes.**

- `menota`: P: hár 'high': kówkos right, kesróm 'hair' and *kewh2- wrong extra (homograph); W: raun 'trial' joined to hraun 'lava' (h-loss skeleton key); P: name Gunnarr: only -arr (*harjaz) mapped, gunnr missing; W: Kroonen *lekinon-/*lekja- p0371: probably borrowed from Celtic; W: eyrir < Lat. aureus (loan); W: Kroonen *managa- p0392: *monogh-o-, not *megh2-; W: mæla 'speak' < *maþlijan- (Kroonen *maþla- p0398), not *mēla- 'time'; W: Kroonen *handu- (< *hinþan-, *ḱont-u-), not *ḱomt; W: Odin name Hjarrandi, no secure etymology; P: halda: *kel- 'drive' plus a second root; W: Kroonen *hugi- p0292 no certain etymology; W: grǫf < *gʰrebʰ- 'dig', id is *gʰrebh2- 'seize'; W: Kroonen *mawi- p0399 obscure; W: Kroonen *þwahan- p0595: not *twek- 'physical appearance'; W: Kroonen *gamala- p0206 uncertain; P: reinn: *krey- right, *ḱerh2- wrong extra; W: ríki < Celtic *rīg- (loan); P: sýna: *sekʷ- 'see' plus 'follow'/'say' homonyms; W: gǫrr 'ready' (*garwa-) joined to *gurą 'dung' (desc homograph).
- `icepahc`: W: raun 'trial' joined to hraun 'lava' (h-loss skeleton key); P: hár: kówkos right, 'hair' and *kewh2- extra; W: Kroonen *handu-: *ḱont-u-, not *ḱomt; W: Odin name, no secure etymology; P: Haraldr: *ker- 'army' plus two *sker- homonyms; -valdr missing; W: Kroonen *deurja- p0134: no accepted etymology; P: hǫpt: *kap- 'seize' plus 'head' homonym; P: nám: *nem- right, *né 'not' extra; P: halda: *kel- 'drive' plus a second root; W: Kroonen *gamala- p0206 uncertain; W: Kroonen *þeuba- p0579 *teup- 'cower', etymology unclear; not *(s)tewp-; P: bjǫrn: 'brown' plus 'pierce' homonym; P: sýna: 'see' plus 'follow'/'say'; W: Kroonen *hugi- p0292 no certain etymology; P: heita: *ḱeyd- right plus extra id; P: Gunnarr: only -arr mapped; W: mæla 'speak' < *maþlijan-, not *mēla-; P: Kroonen *uzda- p0603 *uz-dhh1-o-: only *úd; W: Kroonen *hardu- p0251 *kort-u-, not *(s)kert-; W: herr 'army' (*kóryos) mapped to *ḱerh2-; P: dróttning: *dʰrewgʰ- 'follow' plus 'deceive' homonym.
- `rea-goh`: W: Kroonen *ginnan- p0218: no certain etymology; W: Kroonen *hugi- p0292 no certain etymology; W: sīn 'to be' (*h1es-) mapped to *sem-/a lexeme of another root; P: rad: 'wheel' right, *krot- from rad 'quick' extra; W: luzzil < *lūtila- (Kroonen *lītila- p0379 problematic); *minuyōs wrong; W: scrīban < Lat. scrībere (loan); W: wār 'true' (*weh1ro-) mapped to *wiHrós 'man'; P: weralt: *h2el- 'grow' plus two homonyms; *wiHro- missing; W: firtān joined through OCR'd Kroonen reflex 'taan' to *dēan- 'suckle'; P: wān 'opinion': *wenh1- right plus two 'lacking' ids; P: hurski: two roots.
- `rea-osx`: W: Kroonen *hugi- p0292 no certain etymology; P: alowaldo: *h2welh1- 'rule' plus 'wool' homonym; W: Kroonen *ginnan- p0218 no certain etymology; W: githuld mapped through its prefix gi- (*ḱóm), not þuld; W: Kroonen *breusta- p0114 *bʰreus- 'swell', not 'break'; P: bihaldan: *kel- 'drive' plus a second root; W: brengian: *ḱóm wrong (Kroonen *brengan-); P: god: lemma covers 'God' and 'good', both ids; W: Kroonen *handu-: not *ḱomt; W: hold 'gracious' (*ḱl̥-to- 'inclined'): id 'warm' is another root; W: Kroonen *managa- p0392 *monogh-, not *megh2-; P: ankennian: *ǵneh3- right, *ǵenh1- extra; P: beda: *gʷʰedʰ- right, *bʰedʰ- extra; W: Kroonen *bagma- p0085 *bhh2gh-mo-, not *bʰuH-; W: Kroonen *haleþ- p0244 *kHl-et-, not *ḱel-; W: hēr 'venerable' (*haira-) mapped to *ḱís 'this'.

**After the fixes.**

- `menota`: W: raun 'trial' joined to hraun 'lava' (h-loss skeleton key); P: name Gunnarr: only -arr (*harjaz) mapped, gunnr missing; P: halda: *kel- 'drive' plus a second root; P: only *swa 'so' of *swa-līka-.
- `icepahc`: P: hǫpt: *kap- 'seize' plus 'head' homonym; P: nám: *nem- right, *né 'not' extra; P: halda: *kel- 'drive' plus a second root; P: newd- 'use' plus 'push' homonym; P: Gunnarr: only -arr mapped; P: *weyd- right, the pronoun vit 'we two' extra; P: Kroonen *uzda- p0603 *uz-dhh1-o-: only *úd.
- `rea-goh`: P: rad: 'wheel' right, *krot- from rad 'quick' extra; P: hurski: two roots.
- `rea-osx`: P: bihaldan: *kel- 'drive' plus a second root; P: god: lemma covers 'God' and 'good', both ids; W: hold 'gracious' (*ḱl̥-to- 'inclined'): id 'warm' is another root; P: ankennian: *ǵneh3- right, *ǵenh1- extra.

