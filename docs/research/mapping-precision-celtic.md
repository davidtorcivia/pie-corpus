# Mapping precision, Celtic (Stage C): lemmatizer and lemma → PIE tables

Stage C of the 8c formula-reading experiment needs Celtic pivots. Its preregistration (docs/research/8c-preregistration.md, Stage C) says that Celtic text without lemmas is mapped through form tables. A unit whose content words are less than 30% mapped still counts as a pivot. This report covers the lemmatizer and the three tables built for that purpose:

- `celt`: Irish. CELT plus the round-4 Irish OCR editions. One table for Old, Middle and Early Modern Irish.
- `sga-glosses`: the Old Irish glosses, Würzburg and St Gall.
- `cy`: Welsh. The round-4 Welsh editions.

## What was built

- **Code.**
  - `pie/celtic_mapping.py` holds the tokenizer, mutation stripping, orthographic keys, the lemmatizer, the mapping builder and the CELT licence tags.
  - `scripts/build_celtic_mapping.py` writes the tables and the coverage file:
    `uv run python scripts/build_celtic_mapping.py [--sample-dir D --seed 7]`, about 50 s.
  - Neither file executes anything under raw/.
- **Tables.**
  - `data/research/formulas/mapping/{celt,sga-glosses,cy}.jsonl` use the round-3 row format (corpus, lang, lemma, word, lex_id, path, how, confidence, sources).
  - `celt` rows also carry `celt_licence`. This lists the licence tags of the CELT sources in which the lemma string occurs:
    - `research` for G400001–G400058, the 58 files with the OUP notice;
    - `consent-train` for every other CELT file;
    - `[]` when the string occurs only as a dictionary headword or in the OCR editions.

    The coverage file reports `licence:research` separately.
  - Size (round 1): celt 15,434 rows, sga-glosses 12,174, cy 6,996. Round 2 figures are in the round-2 section.
  - Each table holds two kinds of row:
    - every mapped headword key of the language, so that any Irish or Welsh text can use it through the same lemmatizer;
    - every lemma string the lemmatizer produced on the corpora, including `a|b` unions.
  - There are no rows for function words.
- **Overrides.** `data/research/formulas/mapping-overrides/celtic.json` held 182 lemma rows (127 of them unmaps) and 49 form rows after round 1 (round 2: see below). Each row has a note citing kaikki or eDIL via kaikki, Matasović's EDPC (file page), or the gloss corpus. Form rows use `lang: "sga"` only, because `load_overrides` keys form rows with `KEYS[lang]`. Six rows marked `after_measurement` (uair, gnúis and cían, each for celt and sga-glosses) and the *maith* entry of `SUPPLETIVE` (*ferr*) were added after the final sample was drawn. All of them only remove links. The tables were rebuilt with them, so they are not covered by the measurement.
- **Coverage file.** `data/research/formulas/celtic-coverage.json`.
- **Added data.** `raw/daughters/kaikki-all-20261021/split/{irish,welsh,scottish-gaelic}.jsonl` are lines copied verbatim from the all-languages dump, filtered on top-level `lang_code` ga / cy / gd. There are 38,988, 28,601 and 18,271 lines. They are not in MANIFEST.md yet.
- **Use from the Stage C builder.**
  ```
  maps = cm.build_mappings()
  lz = cm.irish_lemmatizer(maps)        # or cm.welsh_lemmatizer(maps, diplomatic=True/False)
  words = cm.irish_words(text)          # keeps h-/n-/t- hyphens, d'
  lems = cm.lemmatize_words(lz, words)  # round 2: context rules (tig after isin / i / ina … → tech)
  ids = cm.read_table("celt").get(lems[i])
  ```
  Content words follow `cm.content_of(lm, lemma, surface, lz)`: no function words (`cm.is_function_word`), no 1-letter tokens, and no 2-letter tokens matched only after mutation stripping or by skeleton.

## Method

**Lemmatizer** (`CelticLemmatizer`). The form tables are built from four sources:

- the inflection tables of kaikki Old Irish, Middle Irish and Irish entries (and Old Welsh, Middle Welsh and Welsh);
- form-of entries;
- the glosses' (form, lemma) pairs: Würzburg (Doyle), St Gall (UD DipSGG), DipWBG, and the Middle Irish CritMITB.

A surface form is looked up at these levels in turn. The first hit wins.

1. As written (exact key, then the accent-free key). A form that is a headword and also a form of other lemmas returns every lemma whose table count is at least a third of the best one, as `a|b`. Examples: MW *benn* 'cart' and the soft-mutated *penn* 'head'; Ir. *cur* 'hero' and the verbal noun of *cuirid*.
2. Mutation-stripped variants (`irish_demutate`). The hyphen decides when the edition writes one (*h-Iarthar*, *m-Murbulg*, *c-céd*, *duit-siu*, *bliadain-sin*).
   - Otherwise only clusters impossible word-initially are stripped: mb- nd- ng- bp- dt- gc- bhf- ts-, and the written lenitions ḟ ṡ bh mh dh gh fh sh ch th ph.
   - h- before a vowel is stripped, and n-/t- only before a capital vowel.
   - Elided d'/m'/t'/b' are stripped too.
   - Welsh (`welsh_demutate`) undoes the soft, nasal and aspirate mutations and h-prothesis.
3. The orthographic skeleton (`irish_skeleton` / `welsh_skeleton`). This step is used only when the skeleton names three lemmas or fewer.
   - Irish: no length marks; ae/oe/ao → ai, ea → e, io → i; bh dh gh mh fh sh → b d g m f s; nd → n, mb → m; doubled consonants made single; post-vocalic c t p → g d b; final -th → -d.
   - Welsh: k → c, v → f, dd → d, doubled letters made single, final t c p → d g b.
   - The diplomatic Welsh editions also get OCR repair: O/6 inside a word → w, z/2 → r.

Preverb compounds and infixed pronouns are not analysed. A form that is not in a table stays unknown (`?…`).

**Lemma → PIE.** `formula_search_multi.build_lang_mapping` runs for each stage. It covers chain, descendants trees, lexicon reflexes, form-of entries and same-language base words, through the kaikki Proto-Celtic and Proto-Brythonic dumps. The Celtic languages are added to its registries with `setdefault`, so nothing existing changes. On top of that:

- **Daughter-aware steps.**
  - `chain-<lang>`: a Middle Irish or Irish entry whose etymology is "from Old Irish X" takes X's mapping.
  - `later-<lang>`: an Old Irish headword with no etymology takes the proto-language chain of a Middle Irish, Irish or Scottish Gaelic entry that cites it.
- **Rejections the generic parser leaves open.**
  - An entry with a source outside its ancestry next to a PIE link is dropped (Ir. *uair* < Latin *hōra*; *fiabhras* < Old French; *pós* < Latin).
  - So is an entry whose etymology text calls itself unknown or speculative: "Unclear", "Unknown", "of uncertain etymology", "further etymology is unknown", "tentatively", "MacBain", "Morris Jones".
- **Suppletion** (`SUPPLETIVE`). Forms from another stem do not inherit the lemma's etymon. Examples: the b-forms of *at·tá* and the copula; *ruc*/*rug* of *beirid*; *do·rat*/*tuc* of *do·beir*; *luid* of *téit*; *do·rochair* of *do·tuit*; *ad·cuaid* of *ad·fét*; *ferr* of *maith* (added after the measurement); MW *goreu* of *da*; the non-b forms of *bot*.
- **Form-of conflicts.** A key known only as an inflected form keeps no mapping from elsewhere unless the two agree. MW *bu* 'was' had been mapped to *bāus* 'cow'.
- **Stage merge.** A headword's own mapping beats a mapping inherited by an inflected form: Ir. *bia* 'food' beats OIr. *bia* 'will be'. Stages that disagree on the root group leave the key unmapped, unless the earliest stage has the word's own chain.
- **Homograph roots.**
  - When a mapping names two or more lexicon roots of one form (*wel-* ×3, *h₂ey-* ×3, *ḱey-*), the root whose meaning shares a word with the glosses along the path is kept.
  - With no shared word, all are kept. The sample counts these as P.
- **Matasović's EDPC.** A headword's Goidelic or Welsh forms are joined to an unmapped key on the accent-free key, unique on both sides. The OCR'd PIE line is matched with `FuzzyPie` (z→₂ repair), whole form only. The PIE line's own gloss must share a word with the lexicon meaning, which drops *gel-* 'call' read as *gel-* 'be cold'. This yields only a few dozen rows, because kaikki already covers most EDPC entries.
- **Unions.** In an `a|b` union, every candidate that is a dictionary headword must be mapped, and all candidates must agree on the root group. Otherwise the type is left unmapped.

**Precision protocol.** This follows the east independent check:

- **Draw.** 100 mapped content types per table, token-weighted, without replacement, by repeated `random.Random(7).choices`. Types are sorted before the draw. A type is the corpus lookup: the lowercased surface for CELT and Welsh, the corpus lemma for tagged glosses, the surface for untagged glosses.
- **Verdicts.**
  - C (etymon right at root or lexeme level; preverb compounds mapped to the verb count as C);
  - P (root right and formation wrong, a compound mapped to one member, or the right id plus a homograph id);
  - W (false, rejected or speculative etymology, homograph id, borrowing, or the dominant reading of the surface is another word);
  - N (no entry in EDPC or kaikki to confirm or refute; not counted as wrong).
- **Precision.** Strict = C/(C+P+W), lenient = (C+P)/(C+P+W), conservative = C/100, with Wilson 95% intervals.
- **Sources for verdicts.** Verdicts were judged against EDPC (`raw/books/text/matasovic-pcelt`, file pages) and kaikki's etymology text, which cites eDIL / LEIA / GPC. eDIL itself was unreachable. Rows that came from EDPC were judged against kaikki.
- **Re-measurement.** It used the same seed-7 procedure after the fixes. The fixes changed the population, so 90 / 75 / 69 of the 100 types per table were new draws. Verdicts were carried over only for identical (type, lemma, ids).
- **Caveats.** One judge (this agent), not blind: the same agent built the mappings. The after sample contains 9 / 5 / 1 override rows, all judged by their author. Treat the numbers as an upper estimate until an independent check is done, as for the east group.

## Precision

| table | sample | C | P | W | N | strict (95% CI) | lenient (95% CI) | conservative |
|---|---|---|---|---|---|---|---|---|
| celt | before | 52 | 11 | 34 | 3 | 0.54 (0.44–0.63) | 0.65 (0.55–0.74) | 0.52 |
| celt | after | 63 | 10 | 18 | 9 | **0.69** (0.59–0.78) | 0.80 (0.71–0.87) | 0.63 |
| sga-glosses | before | 61 | 9 | 19 | 11 | 0.69 (0.58–0.77) | 0.79 (0.69–0.86) | 0.61 |
| sga-glosses | after | 76 | 4 | 5 | 15 | **0.89** (0.81–0.94) | 0.94 (0.87–0.97) | 0.76 |
| cy | before | 54 | 4 | 35 | 7 | 0.58 (0.48–0.68) | 0.62 (0.52–0.72) | 0.54 |
| cy | after | 60 | 8 | 12 | 20 | **0.75** (0.65–0.83) | 0.85 (0.76–0.91) | 0.60 |

The before and after populations differ. The before sample was drawn before the function-word stoplist existed, so it contains types such as *léo*, *cona*, *nit*, *bo* and *feil*. These were judged W, and the after population excludes them by construction. Part of the 54→69 and 58→75 gains is therefore population change, not mapping repair.

Two variants of the after numbers:

- Leaving out the override rows that I judged myself, strict precision is 0.66 for celt, 0.90 for sga-glosses and 0.75 for cy.
- By lemmatizer level, the skeleton is the weak step. In Irish it scored 3 C / 1 P / 5 W (2 N), and 8 C / 2 P / 4 W in Welsh. Without the skeleton items, strict precision is 0.73 for celt and 0.79 for cy. `CelticLemmatizer(use_skeleton=False)` turns the step off. The tables were built with it on.

Samples and verdicts are in `data/research/formulas/celtic-precision/`: `round0-*` (before) and `round3-*` (after). They hold lemma strings, ids and verdicts only, no corpus text.

## Coverage (content tokens, after)

Content tokens exclude function words. The first column counts all content tokens. The second excludes capitalised non-initial tokens (names). The tagged glosses use UPOS NOUN, VERB, ADJ and PROPN.

| source | content tokens | mapped | mapped, names excluded |
|---|---|---|---|
| CELT, all | 1,911,512 | 34.0% | 36.9% |
| CELT, Old Irish (sga, ≤ 900) | 199,079 | 34.7% | 38.1% |
| CELT, Middle Irish (mga) | 650,814 | 33.9% | 36.4% |
| CELT, Early Modern (ga-early) | 990,396 | 33.8% | 37.0% |
| CELT, Modern / undated | 51,220 / 20,003 | 35.6% / 33.0% | 37.7% / 37.4% |
| CELT, licence research (G400001–058) | 5,770 | 40.4% | 40.9% |
| CELT, by genre | | annals 35.3%, saga 37.6%, verse 36.2%, religious 32.9%, medical 28.5% | annals 43.4% |
| Glosses, tagged (Wb + Sg) | 9,757 | 49.7% (Wb 54.3%, Sg 48.1%) | 50.1% |
| Glosses, untagged Würzburg | 10,021 | 16.4% | 16.4% |
| Irish OCR, by edition (Irish-voting lines) | 623,389 | 12% (Ancient Laws) to 30% (Windisch's Táin, Irische Texte); Ériu 27%, ZCP 21%, Félire 23%, Saltair 21% | |
| Welsh, print-normalised (Skene v2, Myvyrian, Gododdin, Owen) | 387,432 | 19.8% (Myvyrian 22.6%, Owen's laws 12.9%) | 20.2% |
| Welsh, diplomatic (Evans, Rhŷs & Evans) | 169,539 | 15.3% | 16.0% |

Unit-level figures:

- 58.2% of the 250,343 CELT units have at least 30% of their content words mapped. By period this ranges from 57% to 60%.
- 51.3% of CELT units have two or more mapped content tokens, which is the Stage B partner threshold.

**Lemmatizer levels on CELT content tokens.** These shares are of all 1.91M CELT content tokens. The figure in parentheses is the share of that level's tokens that map.

| level | share of content tokens | of which mapped |
|---|---|---|
| form | 47% | 55% |
| unknown | 36% | 0% |
| skeleton | 11% | 40% |
| mutation-stripped | 3% | 58% |
| form override | 2% | 90% |

**Before the fixes.** Coverage was CELT 37.5%, tagged glosses 54%, untagged Würzburg 17% and Welsh 26.5%. Those figures use a looser content definition (no stoplist) and include the wrong mappings above. The fixes traded about 3–8 points of coverage for 15–20 points of precision.

## Error types found and fixed (before sample, then the 300 most frequent types)

1. **Homographs and function-word readings taken as the dominant reading** (about 15 of the 34 W in the celt before-sample; about 15 of the 35 in cy).
   - Examples: *uair* 'hour' as *úar* 'cold'; *bai*/*bo*/*bud* 'was' as *bó* 'cow'; *cur* 'putting' as *cur* 'hero'; *t-slóg* 'host' as *slog* 'swallow'; *aidche* 'night' as the verb *adaig*.
   - Welsh examples: soft-mutated *benn*/*ben* 'head' as *benn* 'cart'; *gwyr* 'men' as *gŵyr* 'crooked'; *oed* 'was' as *oed* 'age'.
   - Fixes: the one-third rule and the headword-agreement rule for unions; the function-word stoplists (`IR_FUNCTION`, `CY_FUNCTION`, with copula and substantive-verb forms); the stage merge; the form-of conflict rule; form rows (*fir* → *fer*, *ele*/*oile* → *aile*, *duine*, *ben*, *bás*, *éc*-spellings, *marbad*-spellings, *atbert*, *táinic*).
2. **Borrowings mapped to the PIE source of the loan** (4–5 in celt; 3 in cy).
   - Ir. *uair*, *fiabhras*, *pós*, *ór*, *muinter*, *légaid*; W *Sais*, *eur*, *modd*, *sain*.
   - Fix: reject entries with a foreign source; unmaps.
3. **Suppletive stems** (5–6 in celt; 1–2 in the glosses; 2 in cy). Examples: *bá*, *bia*, *bís*, *robad*, *rug*, *do·rochair*, *ad·cuaid*, *goreu*, *bu*. Fix: `SUPPLETIVE`, plus b-stem forms of 'be' → *bʰuH-* (override).
4. **Speculative etymologies** that kaikki itself hedges (about 8 in celt; 3 in cy): *druimm*, *tol*, *lá* 'day', *Níall*, *Laigin*, *daear*, *dull*, *hawdd*, *olc*, *mall*. Fix: the `_HEDGE` rejection and unmaps.
5. **Wrong or homograph lexicon ids.**
   - *cenél*/*kenedyl* → *sken-*, corrected to *ken-* 'begin' (EDPC p0212).
   - *muin* 'neck' → *mon-* 'man'.
   - MW *gallu* → *gelH-* 'naked'.
   - *ingen* 'daughter' → *h₃nṓgʰs* 'nail'.
   - *fír* 'true' → *wiHrós*.
   - Fix: overrides; homograph roots disambiguated by gloss (*fili*, *aois*, *Conall*/*Cathal*).
6. **Latin and sigla in the untagged Würzburg glosses** (*deo*, *per*, *híc*, *sup.*). Fix: Latin vocabulary taken from the tagged Latin tokens.
7. **Bad EDPC joins** (*gall*, *rind*, MW *galw*, *bel*). Fix: the gloss check on the PIE line.

## What remains, and limitations

- **Precision is lower than for the other branches.** It was 0.69–0.89 strict after the fixes, against 0.95+ for the east group after its overrides.
  - Most remaining W are homographs whose reading depends on context. The lemmatizer has no context.
  - Middle Welsh base-word chains (`how: base`) scored 3 C / 6 W in the cy sample.
  - The Irish skeleton level scored 3 C / 5 W in the celt sample.
  - Stage C partners need at least 2 shared roots, so a single wrong id rarely makes a partner on its own. A Celtic claim should still be checked by hand against EDPC or eDIL before it is accepted.
- **Coverage is about a third of CELT content tokens, a fifth of Welsh and half of the tagged glosses.** It is limited by three things:
  - Unknown forms (36% of CELT content tokens). These are mostly inflected forms not in any table: Early Modern dative plurals in -(a)ibh, Middle Irish verb forms, OCR damage, names.
  - Words without a PIE etymology in kaikki or EDPC (*cenn*, *mac* in part, *tigerna* if not chained, the many Latin loans).
  - The conservative union rule.
- **Unlemmatized OCR.**
  - The Irish OCR editions mix text with translation, apparatus and glossary. Coverage counts only lines that vote Irish by function words, and the vote is rough.
  - The diplomatic Welsh editions get only light character repair.
  - Ériu, ZCP and Revue celtique are research-only (US-PD). The tables hold no text from them.
- **Preverb compounds and infixed pronouns are not segmented** (*nocretim*, *donécomnacht*, *atrullai*). They map only when a form table or gloss pair has the exact form. That is why the untagged Würzburg tokens, written in scriptio continua with their proclitics, map at 16%. The tagged ones map at 50%. Compound verbs map to the verbal root (*as·beir* → *bʰer-*), and the report counts that as correct.
- **Licence.** G400001–G400058 are tagged `research`, which matches the "58 files G4000xx" count. However:
  - 24 further files are numbered G400065–G400090;
  - 9 of the 58 do not contain the string "Oxford University Press";
  - G301012, G402570–5 and G6000xx do contain it.

  The set is `cm.CELT_RESEARCH_ONLY` and can be changed in one place.

## Round 2: fixes after the independent blind check

The independent check (`docs/research/mapping-precision-celtic-independent.md`, verdicts in
`data/research/formulas/celtic-precision/independent/`) put token-level precision at 0.61 (celt), 0.80 (glosses)
and 0.81 (Welsh). Round 2 fixes the causes it found, at the source where a rule exists and by override rows
otherwise, then re-measures on a new sample.

### Fixes

1. **The *tig* form row.** *tig* is the dat. sg. of *tech* 'house' after a preposition or article (415 of 925 CELT
   tokens) and ·*tic* of *do·icc* 'comes' elsewhere. The lemmatizer has no context, so:
   - the form row now gives the union `tech|doicc`, which the tables leave unmapped;
   - `cm.CONTEXT_FORMS` + `cm.lemmatize_words(lz, words)` resolve *tig* / *thig* from the preceding word
     (*isin, i, hi, ina, dia, da, don, din, ón, ic, oc, is* … → *tech*; *ní, má, mar thig* → *do·icc*).
     The build script uses it for CELT and the Irish OCR lines; Stage C must call it instead of `lz(w)`.
   - Cost: *tig* without a deciding word before it (about 550 of the 925 tokens: 134 sentence-initial, *a*, *agus*,
     *sin* …; mostly 'comes') is now unmapped. About 370 resolve to *tech*.
   - Same cause checked: *tic* (779 tokens) has no preposition peak before it (190 sentence-initial, then *sin,
     tan, noch*), so its row stays. *thig* (304) had inherited the *tig* row through mutation stripping; it is now
     context-resolved too.
2. ***tuc / tucus / tuctar* → *h₁unékti*.** The cause is one kaikki table that mixes two verbs: *do·ucai*
   'understands' (*h₁ewk-*, EDPC p0417 *u-n-k-o-*) and *do·uccai* 'brings' (·*tuc*, ·*tucus*, ·*tuctar*, the
   perfective stem of *do·beir*; kaikki sga *do·uic*: causative of *do·icc*, *h₂neḱ-*; EDPC p0042 *ank-o-*).
   `cm.STEM_SPLITS` moves the non-palatal ·*tuc(c)-* forms (18 table forms: *tuc, tucus, tuctar, tucsat, tucatar,
   tuctais, tucthar, tucfa* …) to a lemma `douccai` that takes *do·icc*'s mapping (*h₂neḱ-*). The palatal
   *tuicci*, *tucci* and the deuterotonic *do·ucci* forms keep 'understand'. In CELT the moved table forms carry
   about 2,250 tokens (*tuc* 1,564, *tucsat* 440, *tucatar* 77, *tucus* 75, *tucthar* 44, *tuctar* 31 …);
   *tucad*, *tucc* and the other Middle Irish spellings are not table forms and stay unknown. The forms kaikki
   lists for the present of 'understand' (·*tucai*, ·*tuccai*, ·*tucu*, ·*tucat*) move too; none is among the
   frequent CELT surfaces.
3. **Matasović over Wiktionary, as a builder rule** (`cm.matasovic_precedence`, run after `add_matasovic`).
   An EDPC entry speaks to a mapped headword when its first Goidelic / Welsh form has the headword's accent-free
   key (one headword only) and its head gloss shares a word with the kaikki senses. Then:
   - no PIE line, and the ETYM calls the word's etymology unknown, non-IE, onomatopoeic, 'not convincing',
     'improbable' or 'will not do' → unmapped (loan remarks are not used: EDPC often says a *neighbour* borrowed
     the word);
   - a PIE line (or a '< PIE \*x' derivation in ETYM) that resolves, whole form, to lexicon ids whose gloss fits,
     and shares no root group with the kaikki ids → EDPC's ids replace them; if it shares one, ids that are mere
     homographs of it are dropped;
   - EDPC doubting its own line ('this etymology is quite uncertain', *nesso-*, *lugri*) → no change;
   - the decision is carried to keys that inherit the changed word along a chain (*aimsir* ← *aimser*,
     *atal* ← *daly*, *trachwant* ← *chwant*).
   It changed 37 Irish and 27 Welsh headwords directly (17 / 15 unmapped) and 20 / 15 more by propagation; the
   full list is `data/research/formulas/celtic-precision/systematic-rules-log.json` (written by every build).
   Examples: unmapped *lucht, caill, bran, aimser, mess, mucc, sel, gairr, ler*, W *amser, brân, celli, chwant,
   daly, meth, pridd*; replaced *toísech* → *weyd-*, *berbaid* → *bʰerw-*, *canaid* → *kan-*, *fillid* → *wel-*.
   Two parser bugs had hidden EDPC's verdicts and were fixed with it: an OCR line starting with a starred form
   inside ETYM (p0265 '\*lewg- 'break'') opened a bogus entry and cut the real ETYM short, and the loan test
   fired on remarks about Germanic loans *from* Celtic. The parser fix costs one older EDPC row (*rún*, whose full
   ETYM now shows a loan remark) and adds 20 entries to the loan-free pool.
   Where EDPC's etymon is not in the lexicon the rule cannot replace ids; those went to override rows instead:
   *bres / bris / brisid* (*bʰres-t-*), *fo·ceird* (*kerd-* 'swing'), *búaid* (*bʰewd-*), *lóeg* (*leh₂p-*
   'cattle'), *cuil* (*ḱuH-ló-*). It also misses keys whose own kaikki chain bypasses the Old Irish word
   (*taoiseach*, *coill*: rows added) and keys the EDPC join does not reach (W *gof*, *caer*, *da*, *teg*: rows).
4. **Preverb-only mappings** (`cm.drop_preverb_only`): a noun, verb or adjective whose only ids are PIE adverbs
   (*de, ḱóm, h₁épi, péri, upó* …) reached through a bare prefix (*kom-*, *exs-*) or without any Proto-Celtic word
   is unmapped: 66 Irish and 67 Welsh keys (*íadaid*, *Cymru*, *cof*, *gwely*, *cyfyng*, *abair*, *iarr* …).
   Words derived from the adverb itself keep it (*úasal*, MW *uchel* < *ouxselos*).
5. **Stoplist.** *íad / iad / íat* 'they' (235 CELT tokens had gone to *íadaid*); Welsh *tano / tanaw* and *wc*
   (OCR of English 'we' in Owen's facing translation).
6. **Override rows** (`celtic.json`, rows marked `"round2": true`): 85 lemma rows and 12 form rows, each with a
   dictionary note. Fixed: the homographs *caín|cáin, clúain, rígaid|téit, ailid|ailt|alt, féil|fial|fíal,
   saer, cuil, lóeg*; EDPC etyma *rann* → *perh₃-*, *commar* → *bʰer-*, *iress* → *péri* + *dʰeh₁-*, *bás* → root
   *gʷeh₂-*, W *cael|gael* → *kagʰ-*, *diwedd* → *wedʰ-*, *Cymru* → *ḱóm* + *mórǵs*; extra ids dropped (*cuir,
   cocar, tonn, anim, incoisig, domeil, anudon*); compounds completed (*Domnall, Dónall* + *h₂welh₁-*); unmapped
   *cruind, meth, lasta, urchóideach, croch, labraithir, dag, deg*, W *galanas, da, gof, teg, caer*; form rows
   *mág* → *mac*, *luidh* → ?*luid*, *béos* → ?*beos*, *béin* → *benaid*, *caích* → *cách*, *isairi*, *ascoir*,
   *tuillti*.
   Left as they were: the Welsh lemmatizer homographs *cly*, *hof* (→ *gof*), *nud* (→ *tud*), *dygoyd*, *goant*,
   because Welsh form rows are not supported (`load_overrides` keys form rows with `KEYS['sga']`); the P items
   for compounds with an unknown element (*Lugaid*, *Fergus*, *macaomh*) and *sál*, *legaid*.

Tables after round 2: celt 15,195 rows, sga-glosses 12,059, cy 6,864. Overrides: 265 lemma rows (180 unmaps),
60 form rows. Content-token coverage: CELT 32.8% (was 34.0%), tagged glosses 48.8% (49.7%), Welsh
print-normalised 18.8% (19.8%), diplomatic 14.7% (15.3%).

### Re-measurement on a new sample (self-judged)

Sample: seed 31, 100 mapped types per table, token-weighted, without replacement, skeleton off, mapping as
applied (`cm.read_table`, context rules on), drawn after all fixes with a copy of the independent sampler.
Files: `round2-sample-{table}-seed31.jsonl`, `round2-verdicts-{table}-seed31.jsonl`.

**These are my verdicts on my own mapping**, made under the independent check's rules (joint verdict: the
lemmatization must be right and the etymology strictly right; EDPC wins where it rejects or calls the etymology
unknown). 9 / 18 / 10 items were identical (type, lemma, ids) to items of the independent sample and carry its
verdicts. N (not verified in the time available) is left out of the denominator; there are many N, so the
conservative C/100 is given too.

| table | C | P | W | N | strict C/(C+P+W) [95% CI] | lenient | conservative C/100 |
|---|---|---|---|---|---|---|---|
| celt | 71 | 7 | 14 | 8 | **0.77** [0.68–0.85] | 0.85 | 0.71 |
| sga-glosses | 73 | 4 | 6 | 17 | **0.88** [0.79–0.93] | 0.93 | 0.73 |
| cy | 68 | 7 | 9 | 16 | **0.81** [0.71–0.88] | 0.89 | 0.68 |

Against the independent check's 0.61 / 0.80 / 0.81 this is +16 points for celt, +8 for the glosses and none for
Welsh; the intervals overlap for the glosses and Welsh, and a self-judge is lenient, so read celt as the only
clear gain. What the W are:

- **Same causes, rows the fixes did not reach** (found by this sample, not fixed after the draw, to keep the
  measurement honest): Irish *bua* (Modern key of *búaid*, 2 items, 366 tokens), *úair* lemmatized to *úar*
  'cold' (the existing *úair* row does not cover the lemma *úar*); Welsh *dal* (×2; *daly*'s EDPC verdict did not
  propagate), *budd* (= *búaid*), *crwn* (= *cruind*), OW *coret* (*cored* was unmapped), *daioni* (derived from
  *da*: an override row does not reach keys that inherit through `base`).
- 2026-10-25: Fixed the remaining *bua*, *úar* (hour), *dal*, *budd*, *crwn*, and *coret* rows with reviewed overrides; *daioni* now inherits the reviewed *da* decision through `base` (regression tested). The sample above remains the original measurement.
- **EDPC hedges** counted W: *bliadain* (3 items, about 1,100 tokens: *bʰleyd-* 'possible formally … semantic
  connection weak'), *glan*, *léir*. Counting EDPC-hedged / disputed items as correct raises strict celt to 0.83.
- **Lemmatizer homographs**: *bíu* → *benaid*, Latin *ego* → *aig*, *comain* → *tiomáin*, *nós* → *os*, tagged
  *bith* 'world' through *bíth*, *dos* 'bush' through *gus*, Welsh *ytir*, *ga*, *creir*.
- Wrong ids: *frithaire* (*aire* 'noble' for 'watch'), *cuan* 'harbour' → 'dog', *ecal*, *do·indnaig*, *étig*.

### The independent sample re-scored under the fixed mapping (biased toward the fixes)

Each of the 300 independent items was looked up again under the round-2 mapping
(`round2-independent-rescore.jsonl`). Unchanged (lemma, ids) keep the independent verdict; changed and still
mapped items got my re-verdict (28 items, all C); items now unmapped leave the denominator.

| table | before (independent) | after | items / tokens now unmapped |
|---|---|---|---|
| celt | 0.61 [0.51–0.70] | 0.97 [0.91–0.99] (n = 76) | 24 / 6,825 |
| sga-glosses | 0.80 [0.71–0.87] | 0.97 [0.91–0.99] (n = 89) | 8 / 50 |
| cy | 0.81 [0.72–0.87] | 0.92 [0.85–0.96] (n = 90) | 8 / 913 |

This is not a precision estimate: the fixes were made on exactly these items, and most of the gain is items
leaving the denominator by being unmapped. The 6,825 celt tokens include the 925 of the old (*tig*, *do·icc*) type,
of which about 370 now map to *tech* under the context rule. Welsh *wc* and *tano*, now stoplisted, are still counted W here, and
six Welsh diplomatic items (*amoc, dygoyd, golat, llano, dzoc, goant*) could only be looked up approximately
(the sample stores lowercased types, which loses the O/6 → w repair). The seed-31 table above is the estimate to
use.
