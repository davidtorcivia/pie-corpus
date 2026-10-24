# Mapping precision: east group (ae, hit, lv, cu, xcl)

Overrides: `data/research/formulas/mapping-overrides/east.json`. It has 450 lemma rows and no form rows: hit 191, lv 100, ae 76, cu 68, xcl 15. Every row has `lex_id`, `erratum` and `note`. `apply_rec_overrides` reads `row["erratum"]`, so that field is required as well as the `note` the brief asks for. No code, lexicon or shared file was changed.

## Method

- **Corpora and counts.** Each corpus was rebuilt the way `scripts/formula_search.py` (R3) builds it:
  - `load_proiel` for xcl and cu (TOROT list);
  - `load_hittite` for hit;
  - `dainas_units` + `FormLemmatizer` for lv;
  - `avesta_units` + `AvestanLemmatizer` for ae.

  Content-lemma token counts were taken from these corpora. The mappings are the shipped tables in `data/research/formulas/mapping/<c>.jsonl`. "After" means `apply_table_overrides` semantics with `east.json`.
- **Samples.** Types were drawn weighted by token frequency, without replacement (Efraimidis–Spirakis keys, `random.Random(seed)`). Two samples were taken per seed:
  - **S_all**: 100 types from all content types (the brief's sample). It gives the unmapped-but-mappable rate. For hit and ae only 11–26 of its types are mapped.
  - **S_map**: 100 types from mapped types only. Precision comes from this sample (n = 100).

  The before/after × seed 0/1 grid was judged in full, so the effect of the overrides can be separated from sampling noise. One caveat: in a weighted sample the frequent types recur, so seed 1 overlaps seed 0 heavily, and both overlap the top-300 review.
- **Verdicts.**
  - c = correct.
  - w = wrong: false or speculative etymology, homograph root, lemmatizer collision, or loanword.
  - p = partial: the root is right but the formation is wrong, or the id set contains the right id plus a wrong one.
  - u = unmapped but securely mappable.
  - n = unmapped and correctly so: function word, name, loan, or no etymology.

  Mapping to the right root counts as c. As in round 3, a Wiktionary-only speculative etymon counts as w. Strict precision is c / mapped; lenient is (c + p) / mapped.
- **Review set.** I checked every mapped lemma in the top 300 by frequency plus both samples. This covered all mapped hit types. Dictionaries were read with grep and `python3 -I`:
  - Kloekhorst EDHIL, with printed pages. Its text layer drops ḫ and w, so headwords were matched on damaged forms.
  - EWAia and Cheung for Avestan.
  - Derksen Slavic and Baltic.
  - Martirosyan.

## Results (S_map, n = 100 each; strict / lenient)

| corpus | seed 0 before | seed 0 after | seed 1 before | seed 1 after | override-touched items in after sample (s0/s1) | content-token coverage |
|---|---|---|---|---|---|---|
| hit | 0.85 / 0.87 | 1.00 | 0.87 / 0.88 | 1.00 | 65 / 65 | 15.5% → 36.2% |
| ae | 0.88 / 0.94 | 0.97 / 1.00 | 0.84 / 0.92 | 0.98 / 1.00 | 31 / 30 | 21.8% → 30.0% |
| cu | 0.88 / 0.93 | 0.96 / 0.99 | 0.85 / 0.90 | 0.97 / 1.00 | 16 / 11 | 47.3% → 49.2% |
| lv | 0.75 / 0.78 | 0.96 / 0.98 | 0.74 / 0.78 | 0.95 / 0.98 | 4 / 4 | 34.1% → 27.7% |
| xcl | 0.89 / 0.91 | 0.97 / 1.00 | 0.89 / 0.91 | 0.96 / 1.00 | 4 / 3 | 47.8% → 45.8% |

S_all (seed 0, all content types). Here "mapped n" is how many of the 100 sampled types are mapped:

| corpus | precision before | mapped n before | u before | precision after | mapped n after | u after |
|---|---|---|---|---|---|---|
| hit | 0.82 | 11 | 16 | 1.00 | 26 | 0 |
| ae | 0.67 | 21 | 22 | 0.92 | 26 | 13 |
| cu | 0.84 | 45 | 14 | 0.98 | 56 | 2 |
| lv | 0.68 | 37 | 17 | 0.96 | 27 | 17 |
| xcl | 0.90 | 38 | 2 | 0.97 | 37 | 0 |

**Caveats.**
- The "after" figures are my own verdicts on my own fixes; up to 65% of the hit after-sample consists of override rows.
- Seed 1 is not independent of the review.
- Read the after numbers as "no remaining error that I can see", not as an independent estimate. An independent re-check of a sample of `east.json` would settle it.
- lv and xcl lose coverage because the overrides unmap more than they add.

## Override counts and main error types

| corpus | remap | add | unmap |
|---|---|---|---|
| hit | 6 (+variants) | 168 | 17 |
| ae | 10 | 36 | 30 |
| cu | 21 | 27 | 20 |
| lv | 9 | 0 | 91 |
| xcl | 2 | 2 | 11 |

1. **Hittite: Kloekhorst damaged-key collisions.** The h/ḫ/w-free key matched the wrong headword:
   - ann=a- 'mother' → *h₂en- 'on';
   - gan=u- 'knee' → *énu;
   - kuw=an- 'dog' → *gʷʰen-;
   - nat=a- 'reed' → *ne 'not';
   - ḫanz= → 'we';
   - ta=aš → taš-;
   - zaḫar=i- (a name) → zē- 'cook';
   - dašš=u- → *de.

   There are also homograph and speculative cases:
   - dai- 'put' → *deh₃- 'give' (Kloekhorst p. 806–807: *dʰh₁-ói-);
   - ištanana- 'altar' → *steh₂- (rejected, p. 413);
   - ḫuppar- 'bowl' → a kaikki *h₂weph₁-.
2. **Hittite: coverage.** The biggest cause of low Hittite coverage was the gloss filter and kaikki gaps, not wrong etymologies. I added 168 frequent lemmas, counting circled-marker variants such as `Ⓐ …`. Each one has its Kloekhorst PIE line and printed page. Examples:
   - pai- 'go', eku- 'drink', dā- 'take', šipant- 'libate';
   - uwa- 'come', tiya- 'step', ēd- 'eat', eš- 'be/sit', ki- 'lie';
   - šunna-, tarna-, ḫuwai-, nai-, ḫark-, zinna- and others.
3. **Avestan: lemmatizer stem collisions.** The `AvestanLemmatizer` prefix-matched surfaces to the wrong word:
   - pərəsa: forms of pərəs- 'ask' → *pórḱos 'piglet';
   - mana → *nogʷnós 'naked';
   - dāšta → *deḱ-;
   - gāθāhva → gaēθā- 'beings';
   - aēta, vasah, fravāti.
4. **Avestan: kaikki chains and homographs.**
   - xᵛarənah- 'glory' → *pleh₁- 'fill' (7 keys, about 430 tokens);
   - speculative: vīspa (EWAia II 562f. 'vielleicht'), sarəδa, mərəγa, gaoša;
   - wrong root: xšnuta → *ksneu- 'sharpen' (Cheung p. 457), garō → 'swallow' instead of *gʷerH- 'praise', raēša → 'root'.

   I also added 36 frequent unlemmatized `?` keys whose surfaces are one word: yazamaide, aša- and ašavan- forms, ratu-, āp-, aspa-, gav- and others.
5. **OCS.**
   - Suppletion: бꙑти was mapped to *h₁ésti; it is *bʰuH- (Derksen p. 71).
   - Homograph roots: зьрѣти 'see' → 'grow old'; обрѣсти 'find' → 'post'; вьсь 'all' → 'poison'.
   - Prefixes taken as etyma: начѧти, съпасти, разоумъ (the same error in Armenian nstim).
   - Unknown etymology: сила (Derksen p. 451); мъногъ is *mnogʰ- (p. 334), not *meǵh₂-.
   - I added common prefixed verbs: сътворити, прѣдати, познати, …
6. **Latvian.** 22% of the frequency-weighted mapped sample was wrong:
   - Wiktionary-only pseudo-etyma: liels, sils, kāja, mazs, gribēt, …
   - Root-gloss mismatches: tēvs → *te 'thee'; viegls → 'we'; garš → 'praise'; valoda, zars, ola → *wel-/*ǵʰer- roots.
7. **Armenian.** Fewer errors than reported in round 3:
   - utem 'eat' → *gʷerh₃- (Martirosyan p. 644: *h₁ed-);
   - ertʻam → *steh₂- (p. 263);
   - xawsim (p. 327: 'unsatisfactory');
   - Wiktionary pseudo-etyma: hogi, marmin, ptuł;
   - spas, an Iranian loan.

## What remains

- **Partial mappings left as they are:**
  - compounds and formations: mazdayasna, aoxta, mazišta, ustāna;
  - homograph pairs where both readings occur: OCS пасти 'graze'/'fall', градъ was fixed;
  - Latvian ambiguous `a|b` lemmas;
  - ar̄nem with three *h₂er- roots.
- **Verdicts I could not settle from the dictionaries; left mapped:**
  - Armenian linim, Tēr, ownim (no Martirosyan headword found);
  - Avestan tkaēša, taoxman, yaona-type chains;
  - OCS храмъ, скотъ;
  - Latvian ozols, darīt.
- **Avestan coverage is still low (30%).** Most frequent unmapped tokens are `?` keys for particles and pronouns (correctly unmapped) or for names and disputed words (fravaši-, Zaraθuštra). Lemma rows are the only lever, because `AvestanLemmatizer` ignores form overrides.
- **Hittite.** The suppletive te-/tar- 'speak' stays on *dʰeh₁- (tē- < *dʰéh₁-ti, Kloekhorst p. 857; tar- < *ter-, p. 870). A few frequent verbs remain unmapped because Kloekhorst has no secure etymon: iya- 'do', mema-, parš-, ḫalzai-, ḫumant-, apa-.
- **Some override notes cite no dictionary page.** About 85 of the 100 lv rows are in this group. Rows marked "speculative Wiktionary-only etymon" or "lexicon root gloss does not fit" rest on the kaikki pseudo id or on an obvious gloss mismatch (tēvs → *te 'thee', viegls → *wéy 'we'). The same goes for the xcl pseudo-etymon rows and the cu "as X" rows (prefixed verbs mapped like their base verb). Only these lv rows cite Derksen EDBIL: tēvs, lācis, gulēt (p. 193) and krūms (p. 260). The reason is practical: Derksen Baltic's headwords are Lithuanian and its text layer is damaged, so looking each word up through its cognate was slow. These rows are the first candidates for a dictionary re-check.
- **Pipeline fixes, for whoever touches the code:**
  - Hittite: require the Kloekhorst damaged key to agree with the TLHdig gloss.
  - Avestan: require a minimum stem length or an ending check per stem class in `AvestanLemmatizer`.
  - All: drop roots whose gloss contradicts the daughter gloss when a chain ends in a homograph root.

Scratch files are session-scoped and will not survive; `east.json` and this report are the durable outputs. They were in `/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/`:
- `east_verdicts_<c>.jsonl`: all verdicts;
- `east_spec_<c>.json`: the override sources, built into `east.json` by `east_build.py`;
- `east_lib.py`: sampling and evaluation.
