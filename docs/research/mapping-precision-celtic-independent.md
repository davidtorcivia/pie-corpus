# Mapping precision, Celtic: independent blind check

This is a second measurement of the Celtic word → PIE mappings (`pie/celtic_mapping.py`; tables `data/research/formulas/mapping/{celt,sga-glosses,cy}.jsonl`; overrides `data/research/formulas/mapping-overrides/celtic.json`). It was made by a different agent from the one that built them.

**Blindness.** All 300 verdicts were written down before I read any of the following:

- the self-report, `docs/research/mapping-precision-celtic.md`;
- its samples and verdicts, `data/research/formulas/celtic-precision/`;
- the notes in `celtic.json`.

While judging, I used only two things from `celtic.json`: whether a sampled lemma has an override row, and whether a form was lemmatized by a form row. The comparison section was written afterwards.

No verdict was changed after I read the self-report. Only the evidence note on celt item 1 (*tig*) was expanded with a full count.

The scratch files are in `/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/`:

- `celtind-sample.py`: the sampler;
- `celtind-sample-{corpus}.jsonl`: the samples;
- `celtind-rules.md`: the rules;
- `celtind-judgements-{celt,sga-glosses,cy}.jsonl`: the 300 per-item verdicts with locators;
- `celtind-lookup.py`, `celtind-ctx.py`: the evidence tools.

These files are session-scoped and should be copied into `data/research/formulas/celtic-precision/` if they are to be kept.

## Bottom line

| table | etymology correct (strict) | etymology correct or partial | lemmatizer correct (module only) | **token lands on the right etymon** | self-report, strict "after" |
|---|---|---|---|---|---|
| celt (CELT) | 66/100 = 66% [56–75] | 75% [66–82] | 92/100 = 92% [85–96] | **61/100 = 61% [51–70]** | 0.69 [0.59–0.78]; 0.73 without skeleton |
| sga-glosses | 81/97 = 84% [75–90] | 94% [87–97] | 28/31 = 90% [75–97] | **78/97 = 80% [71–87]** | 0.89 [0.81–0.94] |
| cy (Welsh) | 85/98 = 87% [79–92] | 89% [81–94] | 92/99 = 93% [86–97] | **79/98 = 81% [72–87]** | 0.75 [0.65–0.83]; 0.79 without skeleton |

Notes on the table:

- Brackets are Wilson 95% intervals.
- "Token lands on the right etymon" requires both a correct lemmatization and a strictly correct etymology. It is the figure comparable to the self-report's strict C/(C+P+W), because that report also counts a wrong reading of the surface as W.
- The n per table is 100 minus the items I could not judge (0 / 3 / 2).

What the numbers say:

- **Irish (celt)** is the weak table. About 4 tokens in 10 of mapped CELT content words get a wrong or only partly right PIE id. My estimate falls inside the self-report's interval, but its point value is 8 points lower.
- **Glosses.** My estimate is 9 points lower than the self-report, at the edge of its interval. Most of the difference is items the self-report left out as N (unverifiable), which I could resolve against EDPC.
- **Welsh.** My estimate is 6 points higher than the self-report. The likely reason is that this sample was drawn with the skeleton level off, the setting Stage C uses. The self-report's skeleton-off figure, 0.79, matches mine.

## Method

**Population (the mapping as applied).** The sample script, `celtind-sample.py` in my scratchpad, does the following:

- builds `cm.build_mappings()`;
- lemmatizes with `cm.irish_lemmatizer(maps, use_skeleton=False)` and `cm.welsh_lemmatizer(maps, diplomatic, use_skeleton=False)`;
- looks up each lemma string in `cm.read_table(corpus)`, which applies `apply_table_overrides`, including `celtic.json` and the shared override files;
- keeps a token when `cm.content_of(...)` is true, the lemma is not a function-word lemma, and the table gives a non-empty id list.

The corpora and type definitions are exactly those of `scripts/build_celtic_mapping.py`, which I imported but did not run:

- **celt**: the CELT units (`celt_tokens`). The Irish OCR editions count towards coverage only, so they are not in this population.
- **sga-glosses**: Würzburg (Doyle) plus St Gall DipSGG.
  - Tagged tokens are typed `=lemma`, with UPOS NOUN, VERB, ADJ or PROPN.
  - Untagged tokens are typed by their surface and go through the lemmatizer.
- **cy**: the 11 Welsh editions. Only lines that vote Welsh are used (`ocr_lines`, `CY_FUNC`).

A type is (surface lowercased, lemma string). The population sizes:

| corpus | content tokens | mapped content tokens | mapped types |
|---|---|---|---|
| celt | 1,941,106 | 567,396 (29.2%) | 30,380 |
| sga-glosses | 19,879 | 6,384 (32.1%) | 1,763 |
| cy | 563,762 | 85,793 (15.2%) | 7,580 |

**Draw.**

- 100 types per table, token-weighted, without replacement.
- The procedure is the build script's: sorted types, then `random.Random(23).choices` with token weights, repeated and skipping repeats.
- No sampled item came from the skeleton level. The levels drawn were: form 85 / 30 / 88; override 6 / 1 / 0; mutation-stripped and loose 9 / 0 / 12; tagged gloss lemma 69 (sga-glosses only).

On estimation:

- Each sampled type counts once. Under probability-proportional-to-tokens sampling, the simple proportion estimates *token-weighted* precision.
- It is slightly biased, because drawing without replacement saturates the very frequent types (*mac*: 41,937 tokens).
- Summing tokens over the sample is not a valid estimator, and I do not report it.

**Rules.** The rules were fixed in writing before item 1, in `celtind-rules.md` in my scratchpad.

- **L, lemmatization.** Is the surface really a form of the lemma, in its dominant reading in this corpus?
  - Verdicts: ok / wrong.
  - na-tagged applies to `=lemma` types, where the annotators lemmatized and not the module.
  - For a union `a|b`, ok means the right lemma is among the parts.
- **E, etymology of the lemma that was assigned.**
  - **Correct**: the etymon is named, as the exact formation or its root. Extra ids for the same root are allowed (flag `multi`).
  - **Partial**: the root is right but the formation wrong, or the right id comes with an unrelated extra id (`extra`), or a two-element compound is mapped to one element (`compound-one-element`).
  - **Wrong** covers:
    - a wrong root or a homograph id;
    - a loan mapped to PIE;
    - a preverb- or prefix-only mapping;
    - an etymology that EDPC rejects, or calls unknown or non-IE, which the mapping asserts anyway (flag `sources-disagree` where kaikki/Wiktionary has it).
  - **Unclear**: no source in reach decides. Excluded from the denominators (0 / 3 / 2 items).
- **Joint**: L ok or na-tagged, and E correct.

**Sources.**

- Matasović, EDPC: the OCR in `raw/books/text/matasovic-pcelt/pNNNN.txt`. The locator is file:line plus the headword. OCR loses length marks and garbles laryngeals.
- kaikki: Old and Middle Irish, Middle Welsh, Proto-Celtic, and the `split/` Irish, Scottish Gaelic, Old Welsh and Welsh dumps. The locator is dump:headword.
- eDIL and GPC can be reached only through kaikki, and kaikki rarely cites them:
  - 7 Old Irish entries carry a dil.ie link;
  - 645 Irish entries carry an eDIL reference;
  - 50 Welsh entries cite GPC.

  In practice, Welsh verdicts rest on EDPC and kaikki etymology text that follows GPC.
- Where a verdict rests on handbook knowledge (GOI, LEIA, KPV) rather than a file, it is flagged `uncertain-own` (5 items).

**Contexts.** I pulled random corpus contexts for every form-override item, every union, and every surface that might be a homograph. The tools are `celtind-ctx.py` (read-only, `python3 -I`) and direct reads of the Würzburg JSON and St Gall conllu files.

Nothing under raw/ was executed.

**Suppletive forms.** I judged them at the lemma level: *do·cer* → *do·tuit*, *ndechaid* → *téit* and *eirg-siu* → *téit* count as E correct, with the flag `suppletive-stem`. The self-report's SUPPLETIVE policy is token-level: a form from another stem does not inherit the lemma's etymon. Under that standard these 3 items (221 tokens) are W, and celt joint falls to 58/100 [48–67].

## Override rows against the rest

| table | group | n | E strict | joint |
|---|---|---|---|---|
| celt | lemma-override row | 2 (*fír*, *bí\|beith\|bheadh*) | 2/2 | 2/2 |
| celt | form-override lemmatization | 6 (*tig*, *tanic*, *tháinic*, *duine*, *mharbhadh*, *eile*) | 6/6 | **5/6** |
| celt | untouched | 92 | 58/92 = 63% [53–72] | 54/92 = 59% [48–68] |
| sga-glosses | lemma-override row | 6 (*dobeir*, *ingen*, *bás*×2, *cenél*, *fír*) | 4/6 (2 P) | 4/6 |
| sga-glosses | untouched | 94 | 77/91 = 85% [76–91] | 74/91 = 81% [72–88] |
| cy | lemma-override row | 1 (*cenedl*) | 1/1 | 1/1 |
| cy | untouched | 99 | 84/97 = 87% [78–92] | 78/97 = 80% [71–87] |

The override rows are mostly right. Two problems stand out:

- **The form row *tig* → *do·icc* is wrong for about half of its tokens, and it carries one of the largest token counts in the celt sample (925).**
  - I classified every *tig* in CELT by the word before it. 415 of the 925 follow a preposition or article that marks the dative of *tech* 'house': *isin / i / ina / dia / is / don / asin / hi / issin / ic tig* (*isin tig*, *i tig Conchobuir*). 45 more follow an ambiguous *a*.
  - In 30 random contexts, 15 are 'house' and 15 are 'comes'. Most sentence-initial occurrences are 'comes'.
  - The row's note justifies it as "prototonic present ·tic of do·icc". That holds for only about half of the tokens.
  - I counted the item as a lemmatization error. Counting it as right would raise celt L to 93% and joint to 62%.
- ***bás* → `pie-lex-gwh2yeti`.** EDPC p0064:9 gives the root (*bāsto-* < *gʷeh₂-*). The id is the lexeme of the present *baïd*, not *bás*'s own formation, so it counts as P.

## Lemmatization errors (separate from etymology)

Module lemmatizer only, tagged gloss lemmas excluded:

- celt: 8 / 100 wrong;
- untagged glosses: 3 / 31 wrong;
- Welsh: 7 / 99 wrong.

Every one is a homograph or a word the content filter should not have passed. None is a form-table bug.

| type | what it is (evidence) | lemmatized to |
|---|---|---|
| celt *tig* (925) | about half are the dative of *tech* 'house' (preceding-word count) | *do·icc* (form override) |
| celt *luidh* (374) | *luid* 'went', the preterite of *téit* (6/6 contexts) | Ir. *luigh* 'lie' |
| celt *mág* (240) | *Mág* = *Mac* in surnames (*Mág Uidhir*, 6/6) | *mag* 'plain' |
| celt *íad* (235) | the pronoun 'they, them' (6/6) | *íadaid* 'closes' |
| celt *bhéos* (18) | the adverb *beos* 'still, yet' | *beoigh* 'enliven' |
| celt *bhéin* (8) | the verbal noun of *benaid* (*do bhéin díbh*) | *ben* 'woman' |
| celt *last* (3), *tuillti* (3) | English 'last' / *tuilled* 'addition' | *lasta*, *tuill* (*toll*) |
| glosses *isairi* (23) | *is airi* 'it is therefore' (copula + *ar* + pronoun) | *aireach* |
| glosses *caích* (5) | the genitive of *cách* 'everyone' (*imballaib caích*) | *cáech* 'one-eyed' |
| glosses *ascoir* (2) | *as chóir* 'as is proper' | *scor* |
| cy *nud* (51) | the personal name *Nudd* (*Edern vab Nud*) | *tud* 'people' |
| cy *wc* (19) | OCR of English *we* in Owen's facing translation | *dwg* (*dwyn*) |
| cy *cly* (17) | an OCR-split *clyw-* 'hear' (*cly wed*) | *clo* 'lock' |
| cy *hof* (14) | *hoff* 'dear, pleasing' (*Hof gan …*, 5/5) | *gof* 'smith' |
| cy *dygoyd*, *goant*, *tano* | *dygwydd-* 'fell'; *gwant* 'pierced'; *tanaw* 'under him' | *dwyn*, *gwybot*, *tanio* |

Two error types stand out:

- Function words and English or OCR noise reach the content stream: the pronoun *íad*, the preposition *trés*, *tano*, *wc*.
- A homograph that is a name or a frequent verb form takes a noun's etymology: *mág*, *nud*, *luidh*.

## Etymology errors (the lemma's own etymon)

The counts below are W items (celt 25, glosses 6, cy 11) plus P items (celt 9, glosses 10, cy 2).

1. **Homograph confusion inside the etymology step** (celt 8 W, glosses 2 W). The headword string is right, but the ids belong to another word spelled the same.
   - ***doucai*: *tuc* (1,564 tokens), *tucus* and *tuctar* 'gave, brought', mapped to *h₁unékti* 'get used to'.** That is the etymon of *do·ucci* 'understands'.
     - kaikki sga:doucai itself notes that DIL files the word under *do·uic*, the perfective of *do·beir* (< *to-ud-ícc-*, *h₂neḱ-*).
     - The SUPPLETIVE rule names "*tuc* of *do·beir*", yet the table still maps these forms.
   - *clúain* 'meadow' → *ḱlównis* 'buttock'. EDPC p0221 has two homograph headwords, *klowni-* 'meadow' and *klowni-* 'thigh'.
   - The union *caín|cáin* takes the 'law' etymon, but the contexts are *caín* 'fair'.
   - *ailid|ailt|alt* takes 'nourish / high', but the contexts are *alt* 'joint'.
   - *rígaid|téit* takes *steygʰ-*. The contexts are *do rigad* 'was made king'; EDPC p0327:21 has *rigaid* 'will go' as the homograph.
   - *lóeg* 'calf' → *leh₂p-* 'flash up'. The right root is *leh₂p-* 'cattle'.
   - Glosses: *saer* (ADJ = *sóer* 'free') → *sep-*; *cuil* 'gnat' → *(s)kewH-* 'corner'.
2. **Wiktionary/kaikki etymology where EDPC disagrees or calls the word unknown** (celt 13, glosses 3, cy 9 W; flagged `sources-disagree`, `speculative`, `uncertain` or unflagged).
   - *bris(id)*, *bres* → *bʰreyH-* 'cut' (EDPC p0081:58 *bʰres-t-* 'break'; kaikki sga:brisid agrees with EDPC).
   - *lucht* → *lewǵ-* (EDPC p0265: "not convincing").
   - *cruind* (EDPC: unknown, perhaps non-IE).
   - *caill/coill* → *kl̥h₂d-* (EDPC p0197 rejects it).
   - *bran* → *werneh₂-* (EDPC p0078: a loan).
   - *búaid* → *gʷowdʰ-* (EDPC: *bʰewd-*).
   - *aimser* → *h₂mh₁-eh₂* (EDPC: unknown, perhaps *h₂emos*).
   - *meth* → *meyh₁-* (EDPC: no IE etymology).
   - *toísech* → *wedʰ-* 'lead' (EDPC p0402 rules out *wedʰ-tu-*).
   - *commar* → *bʰrewh₁-* (EDPC p0226: *kom-* + *ber-* 'carry').
   - *rann* → *h₂rey-* (EDPC p0146: *perh₃-*).
   - *labraithir* → *pl̥b-* (EDPC: probably onomatopoeic).
   - *fo·ceird* → *sker-* 'cut' (EDPC p0214: *kerd-* 'swing').
   - Welsh:
     - *atal/daly* → *delǵʰ-*: EDPC p0100 calls IEW's connection improbable.
     - *caer* → *kagʰrós*: EDPC p0196 says probably non-IE.
     - *da*, from *cystal* → *déḱos*: EDPC p0091 says no etymology has been proposed.
     - *teg* → *tenk-*: Stokes's guess.
     - *trachwant* → *h₁su-*: EDPC says uncertain.
     - *galanas* → *gʷʰen-*: *gal* 'enmity', flagged own judgement.
     - *gael* (soft-mutated *cael*) → *gʰeh₁bʰ-*: the *f*-less forms are from *kag-* by both kaikki and EDPC.
     - *gof* (from *hof*) → *gʷʰobʰ-*: EDPC p0174 says the IE etymology is unknown.
   - Some of these W items carry the flags `sources-disagree`, `speculative`, `uncertain` or `uncertain-own`, meaning a dictionary does support the mapped etymon. Counting those as correct raises strict E to 71% / 85% / 94%. That is the ceiling if the lexicon's Wiktionary etymologies are accepted against EDPC.
   - Also wrong: Irish *urchóideach* → *wedʰ-* 'bind/lead'. *ar·coat* belongs with *wedʰh₁-* 'strike'; this is my own judgement.
3. **Extra homograph ids** (P; celt 6, glosses 5, cy 1). The right root comes with a second, unrelated id. Examples:
   - *cuir*, *cocar*: *sker-* 'turn' + 'cut off';
   - *áel*: *h₂ews-* ×2;
   - *tonn*: *(s)tewd-* + *tend-*;
   - *anim*, *sál*, *incoisig* (*sekʷ-* ×3), *do·meil* (*melh₂-* ×2), *legaid*;
   - *anudon*: *h₁óytos* + *h₂óytos*.

   Most come from the "no shared gloss word: keep all" branch of the homograph-root rule.
4. **Prefix or preverb only** (W). These lose the lexical root:
   - Welsh *diwedd* → *de*;
   - *Cymru* → *ḱóm*;
   - Irish *íadaid* → *h₁epi*.
5. **Compounds mapped to one element** (P). Examples: *Domnall* / *Dónall* (only *dubno-*), *Lugaid*, *Fergus*, *macaomh*, *Cymry*. Counting these as correct moves strict E to 70% / 85% / 88%.
6. **Loans** (W): *croch* < Latin *crux* (glosses); *féil* < Latin *vigilia*, the dominant reading of *féil|fial|fíal*, which is moreover mapped to `pie-lex-wey` 'we'.

## Comparison with the self-report (written after judging)

**The two sets of numbers.**

- The self-report's "after" sample (seed 7, skeleton on, strict C/(C+P+W)) gives:
  - celt 0.69;
  - glosses 0.89;
  - cy 0.75, or 0.79 for Welsh without skeleton items (0.73 for celt).
- My joint figures are 0.61 [0.51–0.70], 0.80 [0.71–0.87] and 0.81 [0.72–0.87].
- The intervals overlap for all three tables. The differences have three sources:
  - **celt (−8 to −12 points).**
    - The *doucai* homograph: the self-report judged *tug* and *tucatar* → *h₁unékti* as C.
    - The *tig* form override, which the self-report added.
    - Etymologies that EDPC rejects. The self-report judged *lucht* → *lewǵ-* as C; it judged *búaid* and *aimser* as N, which I judged W.
  - **glosses (−9).** Of the self-report's 15 N, many have an EDPC entry. In the overlap, *rann* was N there and W here, and *laithe* and *accomol* were N there and C here. Unresolved N items are left out of its denominator, so the self-report's 0.89 is an average over the easier items.
  - **cy (+2 against skeleton-off).** Within sampling error. My sample has no skeleton items, because Stage C uses `use_skeleton=False`.

**Agreement on identical items.** The two samples share 9 + 24 + 11 identical (type, lemma) items, and we agree on 37 of the 44 (84%). The 7 disagreements:

- celt *lucht*: C there, W here (EDPC p0265 rejects the etymology);
- glosses *labraithir*: C there, W here;
- glosses *rann*: N there, W here;
- glosses *anim*: W there, P here;
- glosses *día*: P there, C here;
- glosses *laithe* and *accomol*: N there, C here.

On the same lemma with a different surface, the self-report also passed *bein* → *ben* (C), while here *bhéin* is the verbal noun of *benaid*. That case is a lemmatization difference, not an etymology one.

**Error types.** The self-report lists homograph readings, loans, suppletion and speculative etymologies. All four recur here. It does not mention two error types that are frequent in this sample:

- ids taken from Wiktionary that EDPC explicitly rejects;
- form overrides that are right for only a minority reading (*tig*).

Its claim that the remaining W are "mostly homographs whose reading depends on context" holds for the lemmatizer side. On the etymology side, sources-disagree errors are as common as homographs in celt.

**Override rows.** The self-report rightly flags that it judged its own override rows. Here, 7 of the 9 lemma-override items are strictly correct and 2 are P (*bás* in both glosses items). Of 6 form-override items, 5 are right; the exception, *tig*, is a large-token error affecting about half of its tokens.

## Fixes this check suggests (not applied; no file was changed)

1. Remove or restrict the *tig* form row, for example to sentence-initial position. *tig* after a preposition or article is *tech*.
2. Map *tuc* / *tug* / *tuc-* forms (lemma *doucai*) to *h₂neḱ-* via *do·uic*. The alternative is to unmap them, since *do·ucci* 'understand' is rare in CELT.
3. Correct *bris(id)*, *bres*, *brised* → *bʰres-* (EDPC p0081). Unmap *lucht*, *cruind*, *caill*, *bran*, *meth*, *caer*, *teg*. Fix *rann* → *perh₃-* and *commar* → *bʰer-*.
4. Fix the homograph ids: *clúain*, *lóeg* (*leh₂p-* 'cattle'), *cuil*, *saer* (ADJ).
5. Add stoplist or form rows for *íad*, *mág* (→ *mac*), *luidh* (→ *téit*), *caích* (→ *cách*), *isairi*; for Welsh *nud*, *tano*, *hof* (→ *hoff*); and for English *wc* in the Owen translation.
6. Do not keep a mapping whose only id is a preverb's (*Cymru*, *diwedd*, *íadaid*).
7. If the token-level SUPPLETIVE policy is meant to hold, extend it to *do·cer* (of *do·tuit*), *·dechaid* and *eirg* (of *téit*). In this sample they still inherit the present stem's etymon.

## Limitations

- One judge. The judging was blind to the builder's verdicts and notes, but not double-coded.
- I read EDPC through OCR. Where EDPC has no entry, kaikki was the only source. eDIL and GPC were never read directly.
- *Unclear* items (5) are excluded from the denominators. Counting them as wrong lowers the joint figures by at most 3 points per table.
- The context checks used small random samples, typically 6 contexts, except *tig*, where all 925 tokens were classified by the preceding word.
- The glosses' lemmatizer figure rests on only 31 untagged types.
