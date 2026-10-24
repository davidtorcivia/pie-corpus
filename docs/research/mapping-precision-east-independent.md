# Mapping precision, east group: independent check (hit, ae, cu, lv, xcl)

This is an independent re-measurement of the lemma → PIE mappings for Hittite, Avestan, Old Church Slavonic, Latvian and Classical Armenian. It covers the mappings as they stand after `data/research/formulas/mapping-overrides/east.json`. The east agent reported 0.95–1.00 precision after its fixes (`docs/research/mapping-precision-east.md`), but it judged its own fixes. I did not read that report or the `east.json` notes until all 500 judgements below were recorded. No code, data or override file was changed. Only this file was written.

## Method

- **Population.**
  - Mapping tables: `data/research/formulas/mapping/<corpus>.jsonl`, with every override applied by `load_overrides` / `apply_table_overrides`. This uses all files in `mapping-overrides/` plus the shared `mapping-overrides.json`, which has no rows for these corpora. Rows that the overrides add, and that are absent from the table, are part of the population.
  - Token counts: the corpora were rebuilt exactly as `scripts/formula_search.py` R3 builds them:
    - `load_proiel` for xcl and for cu (the TOROT list);
    - `load_hittite` for hit;
    - `dainas_units` + `FormLemmatizer` with `lv_diminutive_variants` for lv;
    - `avesta_units` + `AvestanLemmatizer` for ae.

    Only content tokens (`Token.content`) were counted.
  - The coverage computed this way matches the east report's "after" coverage (hit 36.2%, ae 30.0%, cu 49.2%, xcl 45.8%), so both checks sample the same population.

  | corpus | content tokens | mapped content tokens | content types | mapped types |
  |---|---|---|---|---|
  | hit | 185,489 | 67,180 | 9,751 | 316 |
  | ae | 103,999 | 31,198 | 11,749 | 759 |
  | cu | 112,896 | 55,542 | 7,814 | 1,157 |
  | lv | 5,967 | 1,646 | 2,433 | 341 |
  | xcl | 9,430 | 4,323 | 1,498 | 251 |

- **Sample.**
  - 100 mapped content types per corpus.
  - Weighted by token frequency, without replacement: repeated `random.Random(7).choices(types, weights)`, with duplicates rejected.
  - Types are sorted by lemma string before the draw.
- **Blinding.**
  - Override membership was computed into a separate file. I did not consult it while judging.
  - `east.json` notes and the east report were opened only after the verdicts were final.
  - Seed 7 differs from the east agent's seeds 0 and 1. Frequent types still recur across seeds, so the samples overlap partly.
- **Verdicts.** Each verdict is against the named dictionary, read with grep / `python3 -I` from `raw/books/text/`.
  - **C**: the mapped id is the word's etymon, at root or lexeme level.
    - Daughter-internal derivatives mapped to their base count as C (učenikъ → učiti; Hitt. tepawešš- → tepu-).
    - So do imperfectives mapped to the simplex and preverb compounds mapped to the verb.
    - So does a verb mapped to a PIE verbal lexeme of its root, even if the lexicon offers only another stem.
  - **P** (partial):
    - the root is right but the formation is wrong (superlative → comparative lexeme; -men- stem → -mo- lexeme);
    - a nominal compound is mapped to one member only;
    - the id set holds the right id plus a wrong one;
    - a lemmatizer union `a|b` joins words of different etyma and the mapping fits only one of them.
  - **W**:
    - a false or rejected etymology;
    - an etymon other than the one the dictionary gives;
    - a homograph lexicon id;
    - a borrowing mapped to the PIE source of the loan. The brief treats borrowings as unmaps.
  - **N**: the word has no entry in the named dictionary (Kloekhorst, EWAia/Cheung, Derksen Slavic/Baltic, Martirosyan), so the dictionary can neither confirm nor refute the mapping. Martirosyan and Derksen cover only inherited vocabulary and are selective, so **N is not "wrong"**. Some N items have a standard etymology elsewhere, and the mapping may well be right. In a second pass every page-less "s.v." verdict was resolved either to a page or to N.
- **Precision.**
  - Strict = C / (C + P + W).
  - Lenient = (C + P) / (C + P + W).
  - Conservative = C / 100, which treats every N as unconfirmed.
  - Intervals are Wilson 95% intervals on the judged n.
- **Locators** are text-file pages `raw/books/text/<dir>/pNNNN`, not printed pages. Known offsets: Kloekhorst file page = printed page + 8; Derksen Baltic and Martirosyan file page = printed page + 14. The EWAia offset varies by volume.
  - K = Kloekhorst `kloekhorst-hitt`.
  - EWAia v1/v2 = `ewaia-v1`/`ewaia-v2`.
  - Cheung = `cheung-iranian`.
  - DS = Derksen Slavic `derksen-slavic`.
  - DB = Derksen Baltic `derksen-baltic`.
  - M = Martirosyan `martirosyan-arm`.

  Every judgement and its locator is in the appendix.

## Results

The headline figure is strict precision. N items are left out of its denominator, and the conservative column puts them back in.

| corpus | n | C | P | W | N | judged | strict C/judged (95% CI) | lenient (C+P)/judged (95% CI) | conservative C/n (95% CI) | C share of judged sample tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| hit | 100 | 99 | 0 | 1 | 0 | 100 | 0.99 (0.95–1.00) | 0.99 (0.95–1.00) | 0.99 (0.95–1.00) | 0.99 |
| ae | 100 | 91 | 6 | 2 | 1 | 99 | 0.92 (0.85–0.96) | 0.98 (0.93–0.99) | 0.91 (0.84–0.95) | 0.96 |
| cu | 100 | 86 | 0 | 3 | 11 | 89 | 0.97 (0.91–0.99) | 0.97 (0.91–0.99) | 0.86 (0.78–0.91) | 0.93 |
| lv | 100 | 81 | 5 | 2 | 12 | 88 | 0.92 (0.84–0.96) | 0.98 (0.92–0.99) | 0.81 (0.72–0.87) | 0.96 |
| xcl | 100 | 70 | 2 | 6 | 22 | 78 | 0.90 (0.81–0.95) | 0.92 (0.84–0.96) | 0.70 (0.60–0.78) | 0.89 |

**Sensitivity to policy-dependent W verdicts.** Each line shows the strict figure if the contested verdict were counted C.

- hit: tarna- would be C (Kloekhorst p0855 rejects *terh₂-; Oettinger and LIV accept it). Strict 0.99 → 1.00.
- cu: богъ and божии would be C. Derksen p0061 supports the Iranian-loan view, and the two types share one decision worth about 2,000 tokens. Strict 0.97 → 0.99.
- ae: varədati would be C (EWAia II p0549: link to *h₃erdʰ- "bleibt problematisch"). Strict 0.92 → 0.93.
- xcl: Tēr and ownim, the two the east agent left as "not settled", would be N rather than W. Strict 0.90 → 0.92.

**Sensitivity in the other direction.** Some C verdicts rest on an etymology that the dictionary itself calls uncertain. If those were W, strict precision would fall:

| corpus | weak C verdicts | strict if they were W |
|---|---|---|
| xcl | leaṙn (M p0320: "uncertain", HAB leaves it open), glux (p0234: "quite uncertain"), hayim (p0400: "does not seem impossible"), hacʻ (p0405: "uncertain"), naw (p0514: possibly an Iranian loan) | 65/78 = 0.83 |
| ae | puθra (EWAia gives *putló- but no root), urvata (EWAia II p0623: any root assignment "willkürlich") | 89/99 = 0.90 |
| lv | gals (DB p0176: no PIE given), sūtīt (p0413: "not completely straightforward"), patikt (p0479: "seems plausible") | 78/88 = 0.89 |
| cu | сълати (DS p0490: "remains to be seen") | 85/89 = 0.96 |

The uncertainty around the strict figures therefore runs both ways. For xcl this makes the non-confirmation of the self-report stronger.

**Bounds from N.** If every N were correct, strict precision would be:
- cu 0.97;
- lv 0.93;
- xcl 0.92.

If every N were wrong, the conservative column applies. The Armenian figure is the least certain of the five: 22% of its sample could not be checked in Martirosyan. These include linim (234 tok.), tesanem (105) and kam (66).

## Override rows vs non-override rows

"east.json row" means the sampled lemma has a lemma row in `east.json`.
- In hit, 70 of the 72 such rows are lemmas absent from the base table, i.e. mappings the override added (the `word = None` rows).
- In ae, 27 of 30 are additions, mostly the `?…` unlemmatized keys.
- No sampled type had a row in the shared `mapping-overrides.json`.

| corpus | cell | n | C/P/W/N | judged | strict (95% CI) | lenient (95% CI) |
|---|---|---|---|---|---|---|
| hit | east.json row | 72 | 71/0/1/0 | 72 | 0.99 (0.93–1.00) | 0.99 (0.93–1.00) |
| hit | no override row | 28 | 28/0/0/0 | 28 | 1.00 (0.88–1.00) | 1.00 (0.88–1.00) |
| ae | east.json row | 30 | 29/1/0/0 | 30 | 0.97 (0.83–0.99) | 1.00 (0.89–1.00) |
| ae | no override row | 70 | 62/5/2/1 | 69 | 0.90 (0.81–0.95) | 0.97 (0.90–0.99) |
| cu | east.json row | 13 | 11/0/1/1 | 12 | 0.92 (0.65–0.99) | 0.92 (0.65–0.99) |
| cu | no override row | 87 | 75/0/2/10 | 77 | 0.97 (0.91–0.99) | 0.97 (0.91–0.99) |
| lv | east.json row | 6 | 4/0/0/2 | 4 | 1.00 (0.51–1.00) | 1.00 (0.51–1.00) |
| lv | no override row | 94 | 77/5/2/10 | 84 | 0.92 (0.84–0.96) | 0.98 (0.92–0.99) |
| xcl | east.json row | 4 | 4/0/0/0 | 4 | 1.00 (0.51–1.00) | 1.00 (0.51–1.00) |
| xcl | no override row | 96 | 66/2/6/22 | 74 | 0.89 (0.80–0.94) | 0.92 (0.83–0.96) |

**The override rows are accurate.** Across the five corpora they score 119 C, 1 P and 2 W out of 122 judged. The two W:
- tarna-: the note cites Kloekhorst's *tr-nó-h₁/₃- but maps to the *terh₂- nasal present, the one etymology Kloekhorst rejects on that page.
- божии: mapped "as богъ", which is an Iranian loan per Derksen.

**The remaining errors sit almost entirely in rows that no override touched:**
- all 8 ae non-C verdicts but one;
- 2 of the 3 cu W;
- all lv P/W;
- all xcl P/W.

The hit and ae override cells are large enough to bear a figure: hit 0.99 (n = 72), ae 0.97 (n = 30). The cu (n = 12 judged), lv (4) and xcl (4) override cells are too small to quote a precision. They only show no error.

## Error types found

1. **Borrowing mapped to the PIE etymon of its source.** This is policy-dependent.
   - cu богъ (1,507 tokens) and божии (482): Derksen DS p0061 supports an Iranian loan (no Winter's law).
   - xcl bažanem: Martirosyan p0751, "borrowed from Iran.".
   - xcl agarak: M p0018; it cannot continue *h₂eǵ-ro- regularly and is a loan from a lost IE language or from Sumerian.
2. **The dictionary rejects the etymology, finds it problematic, or calls the etymon unknown.**
   - hit tarna- (K p0854–0855).
   - ae varədati → *h₃erdʰ- (EWAia II p0548–0549).
   - xcl hanem: M p0403, "etymology uncertain", and neither proposal there is the mapped *ph₂-nH-.
   - lv cauna → *ḱew-: DB p0256, "Etymology unknown".
3. **An etymon other than the one the dictionary gives.**
   - xcl ownim → *sesónh₂e: M p0650 has *h₁ep-, Skt āpnóti.
   - xcl Tēr → *dṓm 'house': M p0075 has *ti-ayr 'master', with ayr 'man'.
   - xcl bowṙn → *bʰṓr 'thief': M p0208 has Skt bhū́rṇi-.
   - ae asūra → *h₂eḱ- 'sharp': EWAia II p0678 has a-sūra- 'weak', from *ḱuh₁ro-.
4. **Homograph lexicon id.** The id has the right shape but belongs to a different entry. This points at the resolver.
   - cu авити → *h₂ew 'away, off': DS p0041 has *avě < *h₂u-i-, Skt āvís.
   - lv kaukt 'howl' → *kú 'where?'.
5. **Extra wrong id in a multi-id mapping (P).**
   - ae zəmō: + *ǵʰéyōm 'winter'.
   - lv tecēt: + *tek- 'take', where DB p0476 has *tekʷ-.
   - xcl aṙnem: + two homograph *h₂er- roots.
   - xcl ayg 'morning': + *h₁eyHw- 'yew', which belongs to aygi.
   - lv mēļš|mēle: + *melh₂- 'grind'.
6. **Lemma-union collisions (P).** The lemmatizer joined words of different etyma.
   - lv karāties|karš, krist|krīts and dēlis|delis|dēle.
   - ae daēnu|daēnā.
7. **Formation (P).**
   - ae mazišta → the comparative lexeme *méǵh₂yos.
   - ae dunman- → *dʰuh₂mós.
   - ae barəšnu- → *bʰérǵʰō.
   - ae mazdayasna: a compound mapped to its second member only.

The east report already lists 5, 6 and 7 as known partials that it left in place, and it lists Tēr, ownim and linim as unresolved. Types 1–4 outside Hittite were not caught. Those items are the next candidates for override rows, as unmaps or remaps, and need the dictionary notes above.

## Comparison with the self-reported numbers

The east report gives these "after" figures as strict / lenient on S_map, n = 100, for seed 0 and seed 1:

| corpus | east, seed 0 | east, seed 1 | this check, seed 7: strict / lenient (judged n) | conservative C/100 |
|---|---|---|---|---|
| hit | 1.00 | 1.00 | 0.99 / 0.99 (100) | 0.99 |
| ae | 0.97 / 1.00 | 0.98 / 1.00 | 0.92 / 0.98 (99) | 0.91 |
| cu | 0.96 / 0.99 | 0.97 / 1.00 | 0.97 / 0.97 (89) | 0.86 |
| lv | 0.96 / 0.98 | 0.95 / 0.98 | 0.92 / 0.98 (88) | 0.81 |
| xcl | 0.97 / 1.00 | 0.96 / 1.00 | 0.90 / 0.92 (78) | 0.70 |

- **hit and cu.** The self-report is confirmed within sampling error. For cu, the self-report's 0.96–0.97 is computed over all 100 types, so it implicitly counts as judged the 11 types that I could not find in Derksen. My hit sample is 72% override rows; the east report says 65%. Those rows checked out against Kloekhorst page by page. The only error is tarna-, and its classification depends on which authority one follows.
- **ae and lv.** Lenient precision agrees (0.98). Strict precision is 4–6 points lower here. The gap comes mostly from partials in untouched rows, plus two W in ae (varədati, asūra) and two in lv (cauna, kaukt) that the east review did not flag. The intervals overlap: ae 0.85–0.96 vs 0.97, and lv 0.84–0.96 vs 0.95–0.96. The self-reported strict figures are at or above the top of my intervals.
- **xcl.** The self-report is not confirmed. Strict precision is 0.90 (0.81–0.95) against 0.96–0.97, and lenient 0.92 against 1.00. Six W fall in rows that no override touched. Another 22 types have no Martirosyan entry. The east report has no "unverifiable" class: its n = 100 counts such items as judged.
- **Coverage of the dictionaries.** The east report's 0.95–1.00 should be read as precision on what its reviewer judged. For cu, lv and xcl, 11–22% of a frequency-weighted sample cannot be confirmed from the named dictionaries at all.

**Caveats.**
- These are single-judge verdicts, by a different agent but against the same OCR-damaged dictionaries.
- Some C verdicts rest on the dictionary's PIE line and cognate list rather than a full reading of the entry.
- For `a|b` lemmas I did not inspect the corpus surfaces.
- Samples were drawn with replacement-rejection rather than Efraimidis–Spirakis keys. Both are frequency-weighted without replacement.

## Appendix: all 500 judgements

Column "ovr" is E when the lemma has a row in `east.json`.

### hit

| # | lemma | tok | mapped to | ovr | v | locator / note |
|---|---|---|---|---|---|---|
| 1 | kui-@welcher | 4356 | kwis, kwis-2 |  | C | K p0496-0497 kui- *kwi- |
| 2 | dā-/d-@nehmen | 3066 | doh3ey | E | C | K p0148 dā- < *doh3- |
| 3 | tep=u-@wenig | 473 | dhebhus |  | C | K p0877 tepu- *dhébh-u- |
| 4 | dai-/te-/ti(ya)-@setzen | 5175 | root:dheh1-do | E | C | K p0814-0815 dai- *dhh1-ói- |
| 5 | pai-/pā-@gehen | 5378 | root:h1ey-go | E | C | K p0669, p0388 pai- 'go' < *h1poi + *h1ei- |
| 6 | ašš=u-@gut | 429 | kaikki:h₁su |  | C | K p0231 aššu- ~ Gk eu-, Skt su- |
| 7 | au(š)-/u(wa)-@sehen | 366 | root:h2ew-perceive | E | C | K p0235 au- *h2óu-ei |
| 8 | nepi=š-@Himmel | 170 | nebhos |  | C | K p0107 nepiš < *nébhos |
| 9 | mekk=i-@viel | 296 | megjh2s | E | C | K p0580 mekki- *me(ǵ)h2- |
| 10 | ēp(p)-/ap(p)-@fassen | 2424 | h1epti |  | C | K p0250-0251 epp- *h1ép-ti |
| 11 | eku-/aku-@trinken | 3352 | h1egwhti | E | C | K p0244-0245 eku- *h1egwh- |
| 12 | tarn=a-@lassen | 425 | trneh2ti | E | W | K p0854-0855 tarna- *terh1/3-; *terh2- explicitly rejected (contested: Oettinger/LIV accept) |
| 13 | ḫar(k)-@haben | 1839 | h2erkti |  | C | K p0132 ḫar(k)- < *h2erk- |
| 14 | kuiški@irgendein | 1815 | kwis, kwis-2 | E | C | K p0496 kuiški |
| 15 | ḫašš=a-@Herd | 725 | h2eHsh2 | E | C | K p0083, p0330 ḫašša- *h2eh1s-eh2 |
| 16 | aš=nu-@versorgen | 215 | root:h1es-be | E | C | K p0224-0225 aš(ša)nu- *h1s-neu- |
| 17 | kara/ep(p)-@fressen | 62 | ghrebh2t | E | C | K p0450 karāp- *ghrebh1- (lexicon *ghrebh2-: same root) |
| 18 | dukk=@gesehen werden | 58 | tukori | E | C | K p0904 tukk- *tuk-ó-ri |
| 19 | kuen-/kun-@schlagen | 220 | gwhenti |  | C | K p0493 kuen- *gwhén-ti |
| 20 | zinn=a-@beendigen | 251 | tineh1ti | E | C | K p1044-1045 zinni- *ti-ne-h1- |
| 21 | paḫḫaš=@beschützen | 60 | peh2sti | E | C | K p0161 paḫš- *péh2s-o |
| 22 | te-/tar-@sprechen | 592 | dheh1t |  | C | K p0866 tē- < *dheh1- (suppletive tar- p0878 *ter- not covered) |
| 23 | ašša=nu-@versorgen | 263 | root:h1es-be | E | C | K p0224-0225 |
| 24 | tiye/a-@treten | 1302 | sth2yeti | E | C | K p0887-0888 tiye/a- *(s)th2- |
| 25 | kuer-/kur-@schneiden | 259 | kwert |  | C | K p0494-0495 kuer- *kwér-t |
| 26 | ped=a-@Platz | 524 | pedom |  | C | K p0680 peda- *pédo- |
| 27 | pai-/pe-/piya-@geben | 3487 | root:h1ep-grab |  | C | K p0622-0623 pai- 'give' < *h1p-ói- (root *h1ep-) |
| 28 | ki=@liegen | 604 | kjeytor | E | C | K p0481-0482 ki- *ḱéi-to |
| 29 | zik=ke/a-@setzen | 285 | root:dheh1-do | E | C | K p0815 zikke/a- *dhh1-sé/ó- |
| 30 | ud=a-@(her)bringen | 1119 | root:deh3-give | E | C | K p0068 uda- univerbation *h2ou + dā- |
| 31 | eš-@sitzen | 582 | h1eh1sti | E | C | K p0161 eš- *h1éh1s-o |
| 32 | šipant=@libieren | 2765 | root:spend-libate | E | C | K p0412-0413 išpant- *spónd-ei |
| 33 | uš=k-@sehen | 258 | root:h2ew-perceive | E | C | K p0235 (impf. of au-) |
| 34 | ka-@dieser | 1217 | kjis | E | C | K p0079 kā- < *ḱós |
| 35 | ḫu=a-@laufen | 129 | h2uh1oyey | E | C | K p0374-0375 ḫuwai- *h2uh1-ói- |
| 36 | laḫ=u-@gießen | 413 | loh3wey | E | C | K p0519-0520 lāḫu- *lóh2u-ei (lexicon *loh3w-: same root) |
| 37 | wē-/uwa-@kommen | 2320 | root:h1ey-go | E | C | K p0388 uwe- < *h2ou + *h1ei- |
| 38 | ped=a-@hinschaffen | 1110 | root:deh3-give | E | C | K p0149 peda- < *h1poi-doh3- |
| 39 | paḫš=@beschützen | 122 | peh2sti |  | C | K p0161 paḫš- |
| 40 | udd=ar@Wort; Sache | 52 | weth2r | E | C | K p0940 uttar *uéth2-r |
| 41 | tek=an-/tag=n-@Erde | 566 | dhegjhoxm |  | C | K p0866-0867 tēkan *dhéǵh-m |
| 42 | Ⓐ eku-/aku-@trinken | 13 | h1egwhti | E | C | K p0244-0245 |
| 43 | ēd-/ad-@essen | 647 | h1edti | E | C | K p0269-0270 ed- *h1éd-ti |
| 44 | ar=@stehen | 660 | h3rto |  | C | K p0203-0204 ar- 'stand' *h3r-to |
| 45 | šall=i-@groß | 165 | solh2is |  | C | K p0717-0718 šalli- *solH-i- |
| 46 | iya-@gehen | 413 | root:h1ey-go | E | C | K p0388 iya- *h1ei- |
| 47 | akk-@sterben | 360 | root:h1ekj-die | E | C | K p0151 āk- 'die' *h1/3ok- |
| 48 | peḫu=te-@hinschaffen | 357 | root:dheh1-do | E | C | K p0670 peḫute- *h1poi-h2ou-dheh1- |
| 49 | zik@du | 1128 | tuh2 |  | C | K p0021, p0078 zīk 'you' (Anat. *tiǵ- beside *tu-) |
| 50 | penn=iye/a-@(hin)treiben | 71 | root:neyH-lead | E | C | K p0672-0673 penna- *h1poi + *noiH- |
| 51 | ešḫ=ar@Blut | 186 | h1esh2r |  | C | K p0264-0266 ešḫar *h1ésh2-r |
| 52 | ḫuiš=u-@lebendig | 116 | root:h2wes-dwell | E | C | K p0361-0362 ḫuiš- *h2ues- |
| 53 | war=nu-@verbrennen | 343 | wrnewti | E | C | K p0932 warnu- (uarr- *urh1-) |
| 54 | iy=anna-@gehen | 133 | root:h1ey-go | E | C | K p0388 (impf. of iya-) |
| 55 | ḫuw=ai-@laufen | 319 | h2uh1oyey | E | C | K p0374-0375 |
| 56 | titta=nu-@hinstellen | 367 | root:dheh1-do | E | C | K p0890-0892 titta(nu)- *dhi-dhh1-neu- |
| 57 | wātar@Wasser | 694 | wodr |  | C | K p0995 wātar *uód-r |
| 58 | ze=a-@kochen | 184 | tyeh1o | E | C | K p1041 zeya- *tiéh1-o |
| 59 | uwa=te-@(her)bringen | 326 | root:dheh1-do | E | C | K p0670 (uwate- *h2ou-dheh1-) |
| 60 | ar-/er-@ankommen | 399 | h1orei | E | C | K p0205 ār- 'arrive' *h1ór-ei |
| 61 | karp=@heben | 233 | kerpt | E | C | K p0460-0461 karp(iye)- *(s)kérp-t |
| 62 | eš-@sein | 247 | h1esti | E | C | K p0131 eš- 'be' *h1es- |
| 63 | paḫḫur@Feuer | 170 | peh2wr |  | C | K p0621 paḫḫur *péh2-ur |
| 64 | lukk=i/a-@anzünden | 78 | lukyeti | E | C | K p0538-0540 lukk- *leuk- |
| 65 | šunn=a-@füllen | 514 | suneHti | E | C | K p0793 šunna- *su-nó-H- |
| 66 | p=išk-@geben | 675 | root:h1ep-grab | E | C | K p0623 (impf. of pai-) |
| 67 | šipanza=k-@libieren | 87 | root:spend-libate | E | C | K p0413 |
| 68 | penn=a-@(hin)treiben | 225 | root:neyH-lead | E | C | K p0672-0673 |
| 69 | uk@ich | 1142 | egjh2 |  | C | K p0920 ūk 'I' |
| 70 | dašš=u-@stark | 63 | root:dens-become_skilled | E | C | K p0861-0862 daššu- *de/oNs-u- |
| 71 | ḫaršar/ḫarš(ša)n-@Kopf | 12 | h3ersr |  | C | K p0322 ḫaršar *h3ers-r |
| 72 | n=ai-@(sich) drehen | 293 | root:neyH-lead | E | C | K p0153 nai- *noih1/3- |
| 73 | utt=ar@Wort; Sache | 10 | weth2r |  | C | K p0940 |
| 74 | išḫ=a-@Herr | 71 | h1esh2os | E | C | K p0398 išḫa- *h1esh2-ó- |
| 75 | mald=@äußern | 70 | moldhey | E | C | K p0151 māld- *meld- |
| 76 | ud=a-@(her)bringen) | 81 | root:deh3-give | E | C | K p0068 |
| 77 | šēš-/šaš-@schlafen | 156 | sesti |  | C | K p0754-0755 šeš- *sés-ti |
| 78 | išpanduzz=i-@Libation | 141 | root:spend-libate | E | C | K p0413 išpantuzzi- |
| 79 | ašaš-/ašeš-@(hin)setzen | 193 | root:h1eh1s-sit | E | C | K p0132 ašaš-/ašeš- 'seat' |
| 80 | karapp=@heben | 86 | kerpt |  | C | K p0461 karp- 'lift' |
| 81 | walaḫḫ=@schlagen | 59 | welh3ti |  | C | K p0953-0954 walḫ- *uélh3-ti |
| 82 | ḫueš=u-@lebendig | 98 | root:h2wes-dwell | E | C | K p0361 |
| 83 | wer=iye/a-@rufen | 57 | weryeti | E | C | K p0084, p0381 werii̯e- *uerh1- |
| 84 | gank=@hinhängen | 49 | kjonkei | E | C | K p0445 kānk- *ḱónk-ei |
| 85 | ḫar=ni(n)k-@zerstören | 244 | root:h3erg-perish | E | C | K p0314 ḫarnink- *h3rg- |
| 86 | ḫark=@umkommen | 200 | h3ergt | E | C | K p0314 ḫark- *h3erg- |
| 87 | tepaw=eš-@wenig werden | 48 | dhebhus | E | C | K p0877 tepawešš- (derivative of tepu-) |
| 88 | ḫuiš=nu-@leben lassen | 52 | root:h2wes-dwell | E | C | K p0361 |
| 89 | azik=k-@essen | 107 | root:h1ed-eat | E | C | K p0269 (azzikk- impf. of ed-) |
| 90 | walḫ=anna-@schlagen | 55 | welh3ti | E | C | K p0954 |
| 91 | daš=k-@nehmen | 222 | root:deh3-give | E | C | K p0148 (impf. of dā-) |
| 92 | ar=nu-@fortbringen | 376 | h3rnewti | E | C | K p0216 arnu- *h3r-neu- |
| 93 | antuḫš=a-@Mensch | 342 | kaikki:h₁n̥dʰweh₂os |  | C | K p0196-0197 antuḫš- *h1n-dhuéh2-s |
| 94 | ḫašt=ai-@Knochen | 46 | h3esth1 |  | C | K p0333 ḫaštai- *h3ésth1-i |
| 95 | šunn=išk-@füllen | 25 | suneHti | E | C | K p0793 |
| 96 | ⓷Ⓐ akk-@sterben | 1 | root:h1ekj-die | E | C | K p0151 |
| 97 | tarḫu=@mächtig sein | 268 | terh2uti | E | C | K p0843-0844 tarḫu- *terh2-u- |
| 98 | šippant=@libieren | 161 | root:spend-libate | E | C | K p0413 |
| 99 | unn=a-@herschicken; herfahren | 78 | root:neyH-lead | E | C | K p0065 unna- < *h2ou + nai- |
| 100 | wak=@(ab)beißen | 98 | kaikki:uh₂genti |  | C | K p0947 wāk- *uóh2g-ei |

### ae

| # | lemma | tok | mapped to | ovr | v | locator / note |
|---|---|---|---|---|---|---|
| 1 | ahura | 1536 | root:h2ems-give_birth |  | C | EWAia v1 p0202-0203 ásura- ~ Hitt. ḫas- 'beget' *h2s-u(ro)- |
| 2 | ?manaŋha | 118 | menos | E | C | EWAia v2 p0337 mánas- |
| 3 | mazišta | 73 | kaikki:meǵh₂yos |  | P | EWAia v2 p0366 mahā́nt- (superlative *-isto-; mapped to comparative lexeme *méǵh2yos) |
| 4 | ?asaono | 495 | root:h2er-fit | E | C | EWAia v1 p0309 ṛtá- |
| 5 | haca/hacā | 559 | sekweh2 |  | C | EWAia v2 p0716 sácā |
| 6 | aməṣa | 471 | nmrtos |  | C | EWAia v2 p0347-0348 MAR 'sterben' (amṛ́ta-) |
| 7 | ?asaonim | 166 | root:h2er-fit | E | C | EWAia v1 p0309 ṛtá- |
| 8 | garō | 78 | root:gwerH-express_approval | E | C | EWAia v1 p0541 gír- |
| 9 | ?asahe | 943 | h2rtos | E | C | EWAia v1 p0309 ṛtá- |
| 10 | cašman | 54 | kwekjsmn |  | C | EWAia v1 p0578 cákṣaṇa-; Cheung *čaš- |
| 11 | ?asaum | 444 | root:h2er-fit | E | C | EWAia v1 p0309 ṛtá- |
| 12 | bərəti | 61 | bhertis |  | C | EWAia v2 p0276 BHAR (bhṛtí-) |
| 13 | tarō | 56 | trh2es |  | C | EWAia v1 p0701 tirás |
| 14 | ?asem | 148 | h2rtos | E | C | EWAia v1 p0309 ṛtá- |
| 15 | ?yazamaide | 2609 | h1yagjeti | E | C | EWAia v2 p0420 YAJ |
| 16 | mazdā | 1590 | root:mensdhh1-vivacious |  | C | EWAia v2 p0406 medhā́- |
| 17 | yaθā | 550 | Hyos |  | C | EWAia v2 p0418 yáthā |
| 18 | katāra | 6 | kwoteros |  | C | EWAia v1 p0340 katará- |
| 19 | asti/astī | 265 | h1esti | E | C | EWAia v1 p0199 AS 'sein' |
| 20 | zaoθra/zaoθrā | 250 | root:gjhew-pour | E | C | EWAia v2 p0849 hótrā- |
| 21 | ?asaonam | 208 | root:h2er-fit | E | C | EWAia v1 p0309 ṛtá- |
| 22 | varədati | 41 | h3erdh |  | W | EWAia v2 p0548-0549 VARDH: link with ūrdhvá-/*h3erdh- 'bleibt problematisch'; *h1u̯eldh- preferred |
| 23 | ?henti | 150 | h1esti | E | C | EWAia v1 p0199 AS 'sein' |
| 24 | ?asaya | 265 | h2rtos | E | C | EWAia v1 p0309 ṛtá- |
| 25 | stāta/stāti | 10 | steh2tis, sth2tos |  | C | EWAia v2 p0792 STHĀ |
| 26 | ?raθβe | 117 | h2ertus | E | C | EWAia v1 p0312 ṛtú- |
| 27 | kəhrpəm | 107 | kerps-2 |  | C | EWAia v1 p0448 kṛ́p- |
| 28 | anašita | 1 | tkjitos |  | C | EWAia v1 p0482 KṢAY2 *tḱei- |
| 29 | ?yasnaica | 175 | h1yagjnos | E | C | EWAia v2 p0422 yajñá- |
| 30 | mąθra | 262 | root:men-think |  | C | EWAia v2 p0339 mántra- |
| 31 | bərəzō | 73 | bhergjhs |  | C | EWAia v2 p0242 BARH |
| 32 | manō | 90 | menos |  | C | EWAia v2 p0337 mánas- |
| 33 | daēnu/daēnā | 211 | dheyh2en | E | P | EWAia v1 p0850 dhénā-/DHĪ; lemma union daēnu/daēnā: daēnu 'female animal' is *dheh1(i)- 'suck', not *dheyh2- |
| 34 | ?yesti | 319 | root:h1yagj-sacrifice | E | C | EWAia v2 p0420 YAJ |
| 35 | spənta | 989 | kjwentos |  | C | EWAia v2 p0706 śvāntá- |
| 36 | nmāna | 276 | root:demh2-join | E | C | EWAia v1 p0750 dám- |
| 37 | jasati | 58 | gwmskjeti |  | C | EWAia v1 p0520 GAM |
| 38 | gaēθanąm/gaēθā/gaēθābiš | 249 | root:gweyh3-live |  | C | EWAia v1 p0649 jīvá- |
| 39 | vaŋhī | 292 | h1wesus |  | C | EWAia v2 p0561 vásu- |
| 40 | puθra | 297 | root:peh2w-few |  | C | EWAia v2 p0172 putrá- *putló- (~ Lat. puer); root assignment not stated |
| 41 | barəšna | 11 | bhergjhox |  | P | EWAia v2 p0242 BARH (barəšnu- -snu- stem; lexeme *bʰérǵʰō a different formation) |
| 42 | razišta | 135 | root:h3regj-straighten |  | C | EWAia v2 p0453 RAJ2 'sich gerade ausstrecken' |
| 43 | dāman/dāmąn/dąman | 147 | dheh1mn |  | C | EWAia v1 p0838 dhā́man- |
| 44 | mraoti | 358 | mlewHti |  | C | EWAia v2 p0265 BRAV |
| 45 | raθa | 4 | Hroth2os |  | C | EWAia v2 p0457 rátha- |
| 46 | mazdayasna | 324 | h1yagjnos |  | P | compound Mazda-yasna-: only the second member mapped (EWAia v2 p0422 yajñá-) |
| 47 | urvarā | 316 | kaikki:h₂r̥h₃wereh₂ |  | C | EWAia v1 p0283 urvárā- |
| 48 | yazati | 49 | h1yagjeti |  | C | EWAia v2 p0420 YAJ |
| 49 | drujō/drujəm | 45 | dhrewks |  | C | EWAia v1 p0812 DRUH/DROGH |
| 50 | īzaēna | 5 | root:h2eygj-goat |  | N | īzaēna- not in EWAia (ajá- v1 p0106 is 'goat' *ag-ó-, different word) |
| 51 | sūra | 141 | kjuh1ros |  | C | EWAia v2 p0678 śū́ra- |
| 52 | arəθa | 35 | kaikki:h₁erthom |  | C | EWAia v1 p0172 ártha- |
| 53 | daēva/daēvī | 211 | deywih2, deywos |  | C | EWAia v1 p0795 devá- |
| 54 | ?ratum | 385 | h2ertus | E | C | EWAia v1 p0312 ṛtú- |
| 55 | sava | 9 | kjewh1os |  | C | EWAia v2 p0651 śávas- |
| 56 | ?aspahe | 120 | h1ekjwos | E | C | EWAia v1 p0194 áśva- |
| 57 | vaŋh/vaŋhī | 208 | h1wesus | E | C | EWAia v2 p0561 vásu- |
| 58 | dasa/dasā | 41 | dekjm |  | C | EWAia v1 p0761 dáśa |
| 59 | vazati | 4 | wegjheti |  | C | EWAia v2 p0563 VAH |
| 60 | barati | 61 | bhereti |  | C | EWAia v2 p0276 BHAR |
| 61 | vaštī | 2 | wekjti |  | C | EWAia v2 p0555 VAŚ 'wollen' |
| 62 | dvarə/dvarəm | 45 | dhwoxr |  | C | EWAia v1 p0817 dvā́r- |
| 63 | maza | 6 | megjh2s |  | C | EWAia v2 p0366 mahā́nt- |
| 64 | ?apo | 204 | root:h2ep-water | E | C | EWAia v1 p0136 áp- |
| 65 | basta | 17 | bhndhtos |  | C | EWAia v2 p0238 BANDH |
| 66 | hištənti | 28 | stisteh2ti |  | C | EWAia v2 p0792 STHĀ |
| 67 | nasu | 168 | nekjus |  | C | EWAia v2 p0058 NAŚ2 'umkommen' |
| 68 | gaēθanąm | 285 | root:gweyh3-live |  | C | EWAia v1 p0649 |
| 69 | måŋh/måŋha/māŋh | 63 | mexh1ns |  | C | EWAia v2 p0380 mā́s- |
| 70 | ?asaone | 153 | root:h2er-fit | E | C | EWAia v1 p0309 ṛtá- |
| 71 | vīspati | 9 | wikjpotis |  | C | EWAia v2 p0589 viśpáti- |
| 72 | asūra | 3 | root:h2ekj-sharp |  | W | EWAia v2 p0678 śū́ra-: aav. a-sūra- 'weak' (*ḱuh1ro-), not *h2eḱ- 'sharp' |
| 73 | ?asavanem | 410 | root:h2er-fit | E | C | EWAia v1 p0309 ṛtá- |
| 74 | ?ratavo | 157 | h2ertus | E | C | EWAia v1 p0312 ṛtú- |
| 75 | ?asava | 123 | root:h2er-fit | E | C | EWAia v1 p0309 ṛtá- |
| 76 | urvata/urvāta | 22 | root:werh1-speak |  | C | EWAia v2 p0623 vratá-: *u̯erh1- is the favoured (but 'arbitrary') option |
| 77 | dunman | 8 | dhuh2mos |  | P | EWAia v1 p0848 dhūmá- (dunman- is a -men- stem; mapped to *dhuh2mós) |
| 78 | tašta | 11 | tetkjto |  | C | EWAia v1 p0667 TAKṢ |
| 79 | ?raevato | 149 | Hreh1is | E | C | EWAia v2 p0466 rayí- (revánt- ~ raēvant-) |
| 80 | gaēθāvyō | 8 | root:gweyh3-live |  | C | EWAia v1 p0649 |
| 81 | vayōi | 54 | way |  | C | EWAia v2 p0615 vái |
| 82 | gāθā | 61 | gweHtH |  | C | EWAia v1 p0538-0539 GĀ/gāthá- (*geh2-) |
| 83 | staotā | 25 | stewtoxr |  | C | EWAia v2 p0789 STAV/stotár- |
| 84 | zəmō | 115 | dhegjhoxm, gjheyoxm |  | P | EWAia v1 p0479 kṣám- correct; extra id *ǵʰéyōm 'winter' is a homograph |
| 85 | uγra | 43 | h2ugros |  | C | EWAia v1 p0266 ugrá- |
| 86 | srīrō | 101 | root:kjreyH-distinguish_oneself | E | C | EWAia v2 p0697 śrī́- (śrīrá-) |
| 87 | sāstī | 5 | kjeh1sti |  | C | EWAia v2 p0654 ŚĀS |
| 88 | pərəne | 117 | plneh2ti |  | C | EWAia v2 p0119 PAR2 'füllen' |
| 89 | amavant | 71 | root:h3emh3-grab |  | C | EWAia v1 p0151-0152 AM1 'anpacken, schwören' (*h3emh3-) |
| 90 | darəγa | 109 | dlh1ghos |  | C | EWAia v1 p0781 dīrghá- |
| 91 | yazata/yazati | 313 | h1yagjeti, root:h1yagj-sacrifice |  | C | EWAia v2 p0420 YAJ |
| 92 | ?vahistem | 123 | h1wesus | E | C | EWAia v2 p0561 vásu- (superlative of the base) |
| 93 | ?vaŋhuya | 222 | h1wesus | E | C | EWAia v2 p0561 |
| 94 | vīvīse | 1 | wewoykje |  | C | Cheung p0440 *u̯ais 'enter' (perf. vīuuīse) |
| 95 | druxš | 245 | dhrewks |  | C | EWAia v1 p0812 |
| 96 | maēza | 2 | h3meygjhos, h3moygjhos |  | C | EWAia v2 p0409 MEH |
| 97 | miθra | 238 | mitro |  | C | EWAia v2 p0382 mitrá- |
| 98 | xvafsa | 2 | supskjeti |  | C | EWAia v2 p0819 SVAP |
| 99 | ratu | 144 | h2ertus |  | C | EWAia v1 p0312 ṛtú- |
| 100 | zaoša | 24 | gjewsos |  | C | EWAia v1 p0654 JOṢ |

### cu

| # | lemma | tok | mapped to | ovr | v | locator / note |
|---|---|---|---|---|---|---|
| 1 | дати | 568 | dedeh3ti |  | C | DS p0107 *dàti *deh3- |
| 2 | бꙑти | 6171 | root:bhuH-be | E | C | DS p0082 *bỳti *bhHu- |
| 3 | оученикъ | 387 | h1owkeyeti | E | C | DS p0517 *učìti *h1ouk-eie- (učenikъ derivative) |
| 4 | молити | 302 | moldheyeti |  | C | DS p0331 *modlìti *mold- |
| 5 | дъщи | 64 | dhugh2texr |  | C | DS p0140 *dъkti *dugh2-tér- |
| 6 | бѣжати | 54 | bhegwyeh2ti |  | C | DS p0050 *běžati *bheg- |
| 7 | людиѥ | 235 | h1lewdhis |  | C | DS p0293 *ľudьje |
| 8 | божии | 482 | root:bheh2g-divide | E | W | DS p0061 *bogъ: borrowing from Iranian (no Winter's law); bož- derivative |
| 9 | изгънати | 68 | gwhenti |  | C | DS p0208 *gъnati |
| 10 | зълъ | 241 | kaikki:ǵʰwel |  | C | DS p0562 *zъlъ, BSl *ǵʰul-, cf. Skt hvárate (*ǵʰwel-) |
| 11 | сестра | 31 | swesoxr |  | C | DS p0456 *sestrà |
| 12 | врѣмѧ | 185 | wertmn |  | C | DS p0527 *vermę |
| 13 | отьць | 637 | atta |  | C | DS p0394 *otьcь |
| 14 | творити | 536 | tworHeyeti |  | C | DS p0512 *tvorìti |
| 15 | не бꙑти | 279 | root:bhuH-be | E | C | DS p0082 |
| 16 | жити | 166 | gwih3weti |  | C | DS p0573 *žìti |
| 17 | чоудо | 149 | kaikki:kewdos |  | C | DS p0266 *čudo *(s)koud- (s-stem) |
| 18 | болии | 100 | bolyisyo |  | C | DS p0063 *boľьjь 'bigger' |
| 19 | слꙑшати | 453 | kjlew |  | C | DS p0466 *slyšati (*ḱleu-s-) |
| 20 | господь | 1438 | ghostipotis |  | C | DS p0191 *gospodь *gost(i)-pot- |
| 21 | грѧсти | 177 | kaikki:gʰrindʰ |  | C | DS p0199 *grę̄sti *gri-n-d- (lexicon *gʰrendʰ-: same etymon, Go. grids) |
| 22 | свѧтъ | 880 | kjwentos |  | C | DS p0487 *svętъ *ḱuen-to- |
| 23 | вещь | 23 | wekwtis |  | N | not in Derksen (*veťь); proposed *wekʷ- 'speak' uncertain |
| 24 | небесьнъ | 66 | nebhos |  | C | DS p0358 *nebo |
| 25 | оумрѣти | 165 | mryetor |  | C | DS p0319 *merti *mer- |
| 26 | дьнь | 609 | dinos |  | C | DS p0145 *dьnь *d(e)i-n- |
| 27 | мрьтвъ | 154 | mrtwos |  | C | DS p0353 *mъrtvъ |
| 28 | бꙑвати | 123 | root:bhuH-be |  | C | DS p0082 |
| 29 | бѣсъ | 169 | bheyh2dheti |  | C | DS p0051 *běsъ *bhoiH-d-so- (root 'fear') |
| 30 | вльна | 25 | h2wlh1neh2 |  | C | DS p0548 *vьlna |
| 31 | повелѣти | 292 | root:welh1-choose |  | C | DS p0525 *velěti *uelh1- |
| 32 | зѫбъ | 31 | gjombhos |  | C | DS p0560 *zǫbъ |
| 33 | небо | 320 | nebhos |  | C | DS p0358 |
| 34 | имѣти | 769 | root:h1em-take |  | C | DS p0222 *jьměti (*h1m-) |
| 35 | градъ | 350 | ghordhos | E | C | DS p0189 *gordъ *gord-o- |
| 36 | рѣшити | 8 | root:wreykj-twist |  | N | not in Derksen (*rěšiti) |
| 37 | посълати | 291 | slh1eh2ti |  | C | DS p0490 *sъlati *selH- |
| 38 | вѣдѣти | 386 | woyde |  | C | DS p0529 *věděti |
| 39 | начѧти | 189 | root:ken-arise | E | C | DS p0356 *načęti *n+k(e)n- |
| 40 | миръ | 256 | kaikki:meyhros |  | C | DS p0329 *mirъ *meiH-ro- |
| 41 | стоꙗти | 145 | sth2eh1yeti |  | C | DS p0479 *stojati |
| 42 | прѣити | 68 | h1eyti |  | C | DS p0227 *jьti *h1ei- |
| 43 | чьсть | 98 | kweyt |  | C | DS p0105 *čьstь (p0100 *čisti) |
| 44 | злато | 35 | gjholh3tos |  | C | DS p0558 *zolto |
| 45 | рещи | 2098 | root:rek-arrange | E | C | DS p0444 *rekti *rek- (LIV 506) |
| 46 | кратъ | 27 | sker |  | C | DS p0247 *kortъ *korto- ((s)ker- 'cut') |
| 47 | пити | 90 | peh3y, pih3 |  | C | DS p0412 *piti *ph3i- |
| 48 | начинати | 12 | sken |  | C | DS p0356 |
| 49 | даръ | 111 | deh3rom |  | C | DS p0107 *darъ *deh3-ro- |
| 50 | новъ | 82 | newos |  | C | DS p0368 *novъ |
| 51 | имѧ | 438 | h1nomn |  | C | DS p0223 *jьmę |
| 52 | слово | 587 | kjlewos |  | C | DS p0465 *slovo *ḱleu-os- |
| 53 | ити | 652 | h1eyti |  | C | DS p0227 |
| 54 | пасти | 117 | peh2sti, peh2y |  | C | DS p0403 *pasti I |
| 55 | поѩти | 76 | h1emeti, h1emt |  | C | DS p0169 *jęti *h1m- |
| 56 | оустроити | 30 | root:sterh3-spread |  | N | not in Derksen (*strojiti) |
| 57 | ѩти | 203 | h1emeti, h1emt |  | C | DS p0169 |
| 58 | дѣти | 41 | dheh1t, dheh1tis |  | C | DS p0115 *děti/*dějati |
| 59 | пища | 42 | peyh2tu |  | C | DS p0412 *pišča/*pitati |
| 60 | богъ | 1507 | root:bheh2g-divide |  | W | DS p0061 *bogъ: Iranian loan |
| 61 | искати | 153 | h2iskjeti |  | C | DS p0225 *jьskati *h2is-sk- |
| 62 | вѣкъ | 398 | woykos |  | N | not in Derksen (*věkъ) |
| 63 | жена | 220 | gwexn |  | C | DS p0569 *žena |
| 64 | стати | 113 | stneh2ti |  | C | DS p0476 *stati |
| 65 | мьнии | 23 | minuyoxs |  | C | DS p0352 *mьńьjь *mi-n- |
| 66 | страхъ | 98 | kaikki:streg |  | N | not in Derksen (*straxъ) |
| 67 | срьдьце | 299 | root:kjerd-heart | E | C | DS p0496 *sьrdьce *ḱrd- |
| 68 | землꙗ | 521 | dhegjhoxm |  | C | DS p0553 *zemľà *dʰǵʰ-em- |
| 69 | дроугъ | 242 | dhrowghos-2 |  | C | DS p0132 *drugъ |
| 70 | строи | 11 | kaikki:stroyos |  | N | not in Derksen (*strojь) |
| 71 | тръжьство | 2 | kaikki:tregʰ |  | N | not in Derksen (*tъrgъ; origin disputed) |
| 72 | варити | 35 | woxr |  | C | DS p0523 *varìti, lengthened-grade causative of *uerh1- |
| 73 | възлюбити | 117 | lowbheyeti |  | C | DS p0292 *ľubìti *leubh- |
| 74 | възнести | 77 | h1nekjeti |  | C | DS p0361 *nestì *h1neḱ- |
| 75 | клѧти | 48 | root:kelh1-call_out_to | E | N | not in Derksen (*klęti) |
| 76 | вѣчьнъ | 109 | woykos |  | N | not in Derksen (*věčьnъ (< *věkъ)) |
| 77 | бесѣда | 35 | root:sed-sit |  | N | not in Derksen (*besěda) |
| 78 | змиꙗ | 24 | dhegjhoxm |  | C | DS p0556 *zmьja: derivative of the word for 'earth' |
| 79 | мѫка | 113 | monkeh2 |  | C | DS p0339 *mǫčiti *monHk- |
| 80 | поминати | 17 | root:men-think | E | C | DS p0351 *mьněti (po-minati) |
| 81 | мати | 148 | meh2texr |  | C | DS p0314 *màti |
| 82 | отъврѣщи | 125 | wregeti |  | C | DS p0526 *vergti *uerg- |
| 83 | братръ | 144 | bhreh2texr |  | C | DS p0071 *bràtrъ |
| 84 | сънъ | 45 | supnos |  | C | DS p0492 *sъnъ *sup-n-o- |
| 85 | рѫка | 400 | kaikki:wrenk |  | C | DS p0450 *rǭka |
| 86 | животъ | 120 | gwih3wos | E | C | DS p0574 *životъ |
| 87 | оубоꙗти | 89 | bhebhoyh2e | E | C | DS p0061 *bojati sę *bhoiH- |
| 88 | вода | 189 | wodr |  | C | DS p0534 *vodà |
| 89 | домъ | 265 | doxm |  | C | DS p0124 *domъ |
| 90 | авити | 141 | h2ew |  | W | DS p0041 *avě/*aviti < *h2u-i- (Skt āvís); mapped to the adverb *h2ew 'away, off' |
| 91 | дрѣво | 105 | doru |  | C | DS p0133 *dervo *dru(H)-o- |
| 92 | око | 218 | h3okws |  | C | DS p0376 *oko |
| 93 | доухъ | 316 | root:dhwes-breathe |  | C | DS p0135 *duxъ |
| 94 | слоушати | 17 | kjlewseti |  | C | DS p0466 *slušati *ḱlous- |
| 95 | исто | 4 | h2idstes |  | C | DS p0226 *isto *h2id-st-es- |
| 96 | квасъ | 10 | root:kweth2-bubble |  | C | DS p0269 *kvasъ |
| 97 | достоꙗти | 47 | sth2eh1yeti |  | C | DS p0479 |
| 98 | глава | 113 | golHweh2 |  | C | DS p0187 *golvà *golH-u-eh2 |
| 99 | скръбь | 36 | root:skerbh-scratch |  | N | not in Derksen (*skъrbь) |
| 100 | молитва | 235 | moldheyeti | E | C | DS p0331 |

### lv

| # | lemma | tok | mapped to | ovr | v | locator / note |
|---|---|---|---|---|---|---|
| 1 | jauns | 33 | h2yewHox |  | C | DB p0223 jaunas |
| 2 | cirst | 5 | sker |  | C | DB p0261 kirsti |
| 3 | rudzi | 44 | Hrughis |  | N | not in Derksen Baltic (rudzi/rugỹs) |
| 4 | balts | 40 | bholHtos |  | C | DB p0094 baltas |
| 5 | mīļš | 6 | kaikki:mei |  | C | DB p0330 mielas |
| 6 | karāties/karš | 4 | koryos |  | P | DB p0240 karas *korio- correct for karš, but lemma union with karāties 'hang' (DB p0243 *kerH-) |
| 7 | augt/augusts/augs | 14 | h2ewgeti |  | C | DB p0082 augti |
| 8 | māte/mate | 26 | meh2texr |  | C | DB p0337 motė |
| 9 | augs/augt | 32 | h2ewgeti |  | C | DB p0082 augti |
| 10 | likt | 18 | root:leykw-leave |  | C | DB p0301 likti |
| 11 | ledus | 3 | kaikki:ledʰus |  | C | DB p0291 ledas |
| 12 | tecēt | 14 | teketi, tekweti, tekwti |  | P | DB p0476 tekėti *tekʷ-; extra id *tek- 'take' (tekti) wrong |
| 13 | bāls | 16 | bholHos |  | C | DB p0092 balas |
| 14 | dzimt | 3 | gwemt |  | C | DB p0191 gim̃ti *gʷm- |
| 15 | rasa | 7 | h1roxs |  | C | DB p0390 rasa |
| 16 | zoss | 1 | gjhh2ens |  | C | DB p0528 žąsis |
| 17 | ozols | 8 | kaikki:anǵol |  | C | DB p0089 ąžuolas |
| 18 | kvieši | 9 | root:kjweyt-shine | E | N | not in Derksen Baltic (kvieši/kviečiai) |
| 19 | ņemt | 26 | nemeti |  | C | DB p0214 imti |
| 20 | augt | 14 | h2ewgeti |  | C | DB p0082 augti |
| 21 | vedekla | 3 | wedheti, wedheti-2 |  | C | DB p0513 vesti |
| 22 | galva | 9 | golHweh2 |  | C | DB p0176 galva |
| 23 | bērzs | 8 | bherHgjos |  | C | DB p0102 beržas |
| 24 | brāls | 4 | bhreh2texr |  | C | DB p0115 brolis |
| 25 | iet | 31 | h1eyti |  | C | DB p0165 eiti |
| 26 | tauta | 39 | tewteh2 |  | C | DB p0475 tauta |
| 27 | dievs | 35 | deywos |  | C | DB p0142 dievas |
| 28 | palikt | 5 | root:leykw-leave |  | C | DB p0301 likti |
| 29 | raut | 11 | HruHyeti |  | C | DB p0392 rauti |
| 30 | klausīt/klausit | 1 | kjlew |  | C | DB p0263 klausyti |
| 31 | nakts | 18 | nokwts |  | C | DB p0341 naktis |
| 32 | dzeltens | 9 | gjhlh3tos |  | C | DB p0183 geltas |
| 33 | sacīt/sacit | 6 | sokweyeti |  | C | DB p0401 sakyti |
| 34 | paparde | 5 | poptorHtis |  | C | DB p0358 papártis *po-porH-ti- |
| 35 | maize | 12 | kaikki:meyǵ |  | N | not in Derksen (Latv. maize) |
| 36 | tauriņš | 1 | tawros |  | C | DB p0474 tauras: tauriņš 'butterfly' diminutive of 'aurochs' |
| 37 | saule | 34 | soh2wl |  | C | DB p0404 saulė |
| 38 | dēls | 16 | root:dheh1y-suckle | E | N | not in Derksen Baltic (dēls 'son' (only dėlė 'leech' p0134)) |
| 39 | otrs | 10 | h2enteros |  | C | DB p0071 antras |
| 40 | mēness | 5 | mexh1ns |  | C | DB p0325 mėnuo |
| 41 | vārds | 7 | werdhom |  | C | DB p0503 vardas |
| 42 | silts | 4 | kjltos-2 |  | C | DB p0462 šiltas |
| 43 | lauks | 19 | lowkos |  | C | DB p0289 laukas |
| 44 | suns | 8 | kjwox |  | C | DB p0469 šuo |
| 45 | migla | 10 | h3mighleh2 |  | C | DB p0331 migla |
| 46 | surs/sūrs | 20 | suHros |  | C | DB p0450 sūras |
| 47 | pazīt | 7 | gjnh3skjeti |  | C | DB p0533 žinoti |
| 48 | vasara | 15 | wosr |  | C | DB p0506 vasara |
| 49 | zirnis | 12 | gjrh2nom |  | C | DB p0534 žirnis |
| 50 | melns | 11 | melh2n |  | C | DB p0324 mėlas (melns: suffix -n-) |
| 51 | šķist | 5 | skweytt |  | N | not in Derksen (Latv. šķist) |
| 52 | gals | 28 | gwolHos |  | C | DB p0176 galas: cf. OE cwelan (*gʷelH-); no PIE given |
| 53 | koks | 6 | kewk |  | N | not in Derksen (Latv. koks 'tree') |
| 54 | ass | 7 | h2ekjs |  | C | DB p0077 ašis |
| 55 | malt | 13 | melh2eti, melh2ti |  | C | DB p0316 malti |
| 56 | diena/dienēt | 6 | deynos |  | C | DB p0141 diena |
| 57 | brālis/bralis | 10 | bhreh2texr |  | C | DB p0115 brolis |
| 58 | ezers | 16 | kaikki:h₁eǵʰerom |  | C | DB p0172 ežeras |
| 59 | krist/krīts | 2 | krnetti |  | P | DB p0271-0273 kristi (*kret-/*krit-) correct for krist; lemma union with krīts 'chalk' (loan) |
| 60 | vilnis | 4 | root:welH-roll | E | C | DB p0518 vilnis |
| 61 | vējš | 11 | h2weh1yus |  | C | DB p0510 vėjas |
| 62 | vilks | 5 | wlkwos |  | C | DB p0517 vilkas |
| 63 | kalns | 28 | root:kelH-rise | E | C | DB p0235 kalnas |
| 64 | ābols | 8 | h2eboxl |  | C | DB p0353 obuolys |
| 65 | dzīvošana | 2 | gwih3weti |  | C | DB p0193 gyvas |
| 66 | dēlis/delis/dēle | 4 | root:dheh1y-suckle |  | P | DB p0134 dėlė (*dheh1-) correct for dēle; lemma union with dēlis 'board' |
| 67 | miets | 1 | kaikki:meyt |  | N | not in Derksen Baltic (miets/mietas) |
| 68 | patikt | 2 | teketi |  | C | DB p0479 tikti 'please': ultimately cognate with tekti *tek- (p0476) |
| 69 | gads | 12 | ghodhos |  | N | not in Derksen Baltic (gads 'year' (p0208 guodas lists Latv. guods only)) |
| 70 | akmens | 4 | h2ekjmox |  | C | DB p0061 akmuo |
| 71 | kauns | 4 | kaikki:kaunos |  | N | not in Derksen (Latv. kauns) |
| 72 | oga | 11 | h2ogr |  | C | DB p0494 uoga |
| 73 | ābele | 6 | kaikki:h₂ebl̥ |  | C | DB p0353 obelis |
| 74 | sauja | 1 | sewh1yeh2 |  | N | not in Derksen Baltic (sauja/saujà) |
| 75 | pīt | 7 | spnh1ti |  | C | DB p0370 pinti |
| 76 | rūgtums | 2 | root:h1rewg-belch |  | C | DB p0399 rūgti |
| 77 | zaļš | 25 | root:gjhelh3-green |  | C | DB p0525 žalas |
| 78 | sēja | 8 | seh1yeti |  | C | DB p0409 sėti |
| 79 | krusa | 2 | kruseh2 |  | C | DB p0275 kruša |
| 80 | bite | 12 | bhey |  | C | DB p0105 bitė |
| 81 | ašs | 1 | h2ekju |  | C | DB p0077 ašis |
| 82 | deva/dot | 1 | dedeh3ti |  | C | DB p0160 duoti |
| 83 | acs | 3 | h3okws |  | C | DB p0061 akis |
| 84 | pāriet | 2 | h1eyti |  | C | DB p0165 eiti |
| 85 | cauna | 1 | kaikki:ḱew,kew |  | W | DB p0256 kiáunė / Latv. cauna: 'Etymology unknown' |
| 86 | vdrs/vēders | 2 | uderos |  | C | DB p0508 vėdaras |
| 87 | medus | 2 | medhu |  | C | DB p0323 medus |
| 88 | miegs | 2 | kaikki:meygʰ |  | C | DB p0329 miẽgas *h3meigh- |
| 89 | trakums | 1 | kaikki:terk |  | N | not in Derksen (Latv. traks) |
| 90 | deva | 2 | dedeh3ti |  | C | DB p0160 duoti |
| 91 | zīle | 1 | gwlh2eh1 |  | C | DB p0189 gilė |
| 92 | mēļš | 3 | root:melh2-black | E | C | DB p0324 mėlas *melh2- |
| 93 | bērzs/bērza | 5 | bherHgjos |  | C | DB p0102 beržas |
| 94 | vest | 5 | wedheti, wedheti-2 |  | C | DB p0513 vesti |
| 95 | kaukt | 1 | ku |  | W | onomatopoeic 'howl' mapped to *kú 'where?' (homograph id) |
| 96 | diena | 6 | deynos |  | C | DB p0141 diena |
| 97 | sutit/sūtīt | 4 | root:sent-go | E | C | DB p0413 siųsti *snt- (LIV *sent- tentative) |
| 98 | mēļš/mēle | 6 | root:melh2-black, root:melh2-grind |  | P | DB p0324 mėlas correct for mēļš; extra *melh2- 'grind' from lemma union with mēle 'tongue' |
| 99 | vecs/vcs | 12 | wetusos |  | C | DB p0514 vetušas |
| 100 | slaukt | 1 | root:kjlewH-clean |  | N | Latv. slaukt not in Derksen Baltic (p0467 šluoti *ḱleh3u- lists slota only) |

### xcl

| # | lemma | tok | mapped to | ovr | v | locator / note |
|---|---|---|---|---|---|---|
| 1 | bažak | 5 | bheh2geti |  | N | bažak 'cup' not in Martirosyan (baž- words are Iranian loans, p0751) |
| 2 | asem | 538 | root:h1egj-say |  | C | M p0131 asem *h1eǵ- |
| 3 | kin | 45 | gwexn |  | C | M p0377 kin |
| 4 | anown | 39 | h1nomn |  | C | M p0110 anun |
| 5 | gitem | 54 | woyde |  | C | M p0225 *gēt- / gitem < *u̯oid-h2e |
| 6 | em | 525 | h1esti |  | C | M p0269 em 'to be' |
| 7 | anjn | 40 | h2enh1gjh |  | C | M p0107 anjn *h2enh1- 'breathe' |
| 8 | gam | 137 | root:gwem-come |  | C | M p0210 gam |
| 9 | am | 15 | root:semh2-summer |  | C | M p0059 am |
| 10 | ar̄nem | 117 | root:h2er-fit, root:h2er-speak_weightily_loudly, root:h2er-take |  | P | M p0126 aṙnem *h2er- 'fit' correct; two extra homograph *h2er- roots |
| 11 | ordi | 86 | kaikki:portiyo |  | C | M p0550 ordi *por-ti-o- |
| 12 | jer̄n | 28 | gjhesoxr |  | N | no entry in Martirosyan: jeṙn (mention only, p0548) |
| 13 | tesanem | 105 | root:derkj-see |  | N | no entry in Martirosyan: tesanem (mentions only) |
| 14 | hanem | 39 | kaikki:ph₂nheti |  | W | M p0403 hanem: 'Etymology uncertain' (Skt sanóti or Hitt. ḫan-); mapped *ph2-nH- |
| 15 | tʻołowm | 37 | tlneh2ti |  | N | t‘oɫum not found in Martirosyan text |
| 16 | ancʻanem | 26 | sntskjeti |  | N | anc‘anem: no etymology in Martirosyan (p0287) |
| 17 | owsowcʻanem | 17 | root:h1ewk-become_accustomed |  | N | usuc‘anem/usanim not found in Martirosyan |
| 18 | ayrem | 1 | h2eh1ter |  | C | M p0077 ayrem < *ayr- 'fire' *HeHter- |
| 19 | ban | 60 | bheh2nis |  | C | M p0180 ban *bheh2-ni- |
| 20 | hangčʻim | 3 | smkwih1 |  | C | M p0402 hangč‘im *sm̥-kwiH- |
| 21 | kam | 66 | gwigweh2ti |  | N | kam not found in Martirosyan |
| 22 | gom | 13 | root:h2wes-dwell |  | C | M p0235 go- 'to be, exist' < *h2ues- (perfect *u̯ose) |
| 23 | ankanim | 31 | kaikki:sn̥gʷ |  | C | M p0104-0105 ankanim *sn̥gw- |
| 24 | lear̄n | 13 | root:kjley-lean |  | C | M p0320 leaṙn ~ *ḱlei- (uncertain) |
| 25 | banam | 13 | bhh2nyeti |  | N | banam not found (only HAB reference p0177) |
| 26 | harcʻanem | 24 | prkjskjeti, prskjeti |  | C | M p0410 harc‘anem *pr̥ḱ-sḱe/o- |
| 27 | aǰ | 6 | kaikki:shdʰyo |  | C | M p0113 aǰ ~ Skt sādhú- |
| 28 | mit | 13 | mexdos |  | C | M p0484 mit *med- |
| 29 | linim | 234 | kjleyn |  | N | linim not found in Martirosyan |
| 30 | awcanem | 6 | h3nnegwti |  | C | M p0034 awcanem (s.v. awji-k‘; *h3engw-) |
| 31 | sirt | 21 | kjexr |  | C | M p0590 sirt |
| 32 | ayr | 67 | h2nexr |  | C | M p0075 ayr |
| 33 | yar̄nem | 29 | h3rnewti |  | N | yaṙnem not found in Martirosyan |
| 34 | lsem | 67 | kjlunesti |  | C | M p0327-0328 lsem *ḱleu- |
| 35 | ezn | 6 | h2egjh |  | C | M p0261 ezn ~ Skt ahī́- |
| 36 | kočʻem | 55 | gwotyeti |  | C | M p0385 koč‘em *gwot-i̯e- |
| 37 | mard | 38 | mrtos, smrtos |  | C | M p0466 mard |
| 38 | hayim | 20 | peh2y |  | C | M p0400 hayim *peh2i- 'does not seem impossible' |
| 39 | ownim | 69 | sesonh2e |  | W | M p0650 unim ~ Skt āpnóti (*h1ep-); mapped *sesónh2e (*senh2-) |
| 40 | erg | 1 | h1erkwos |  | C | M p0273 erg |
| 41 | ǰowr | 8 | kaikki:yuhr |  | N | ǰur 'water' entry not found (only cross-references) |
| 42 | Tēr | 108 | doxm |  | W | M p0075 tēr < *ti-ayr 'master'; mapped *dṓm 'house' (not supported) |
| 43 | ar̄nowm | 40 | kaikki:h₂rnu |  | C | M p0126 aṙnum *h2r-nu- |
| 44 | awr | 76 | Heh2mr |  | C | M p0170 awr |
| 45 | pʻokʻr | 4 | root:peh2w-few |  | N | p‘ok‘r not in Martirosyan |
| 46 | ar̄awawt | 3 | h2ewsoxs |  | C | M p0123 aṙawawt |
| 47 | sowrb | 21 | kjubhros |  | C | M p0602-0603 surb *ḱu-bh-ro- |
| 48 | owtem | 38 | root:h1ed-eat | E | C | M p0658 utem |
| 49 | srbem | 8 | kjubhros | E | C | M p0602 (srbem derivative of surb) |
| 50 | town | 61 | doxm |  | C | M p0632 tun |
| 51 | erknčʻim | 22 | root:dwey-fear |  | C | M p0282 erknč‘im: *du̯ei- 'fear' endorsed |
| 52 | hat | 2 | root:h2ed-dry |  | C | M p0406 hat < *h2edos- 'grain' |
| 53 | gtanem | 46 | winedti |  | C | M p0748 gtanem |
| 54 | howr | 6 | peh2wr |  | C | M p0440 hur |
| 55 | lam | 12 | kaikki:pla |  | N | lam not in Martirosyan (mentioned p0327 as onomatopoeic) |
| 56 | tam | 161 | root:deh3-give |  | C | M p0614 tam |
| 57 | mec | 26 | megjh2s |  | C | M p0472 mec |
| 58 | mēǰ | 23 | medhyos |  | C | M p0217 mēǰ |
| 59 | dnem | 34 | root:dheh1-do |  | C | M p0254 dnem |
| 60 | aganim | 7 | h2us |  | C | M p0018 aganim |
| 61 | hin | 5 | senos |  | C | M p0422 hin |
| 62 | dowstr | 9 | dhugh2texr |  | C | M p0258 dustr |
| 63 | ayg | 2 | h2ewsoxs, root:h1eyHw-yew |  | P | M p0068 ayg 'morning' < *h2(e)us- correct; extra id *h1eyHw- 'yew' belongs to aygi (p0070) |
| 64 | tik | 4 | kaikki:digʰ |  | C | M p0627 tik *dig- |
| 65 | gar̄n | 1 | wrh1exn |  | C | M p0212 gaṙn |
| 66 | agarak | 6 | h2egjros |  | W | M p0018 agarak: cannot continue *h2eǵ-ro- regularly; loan (lost IE language or Sumerian) |
| 67 | beran | 8 | bherano |  | N | beran not found in Martirosyan |
| 68 | nstim | 24 | root:sed-sit | E | C | M p0519 nstim |
| 69 | yłi | 3 | plh1nos |  | C | M p0507 yɫi (y- + *pleh1-) |
| 70 | nor | 10 | newos |  | C | M p0875 nor |
| 71 | lnowm | 18 | plneh1ti |  | C | M p0336 lnum |
| 72 | akn | 35 | h3okws |  | C | M p0036 akn |
| 73 | čanačʻem | 11 | gjnh3skjeti |  | C | M p0454 čanač‘em |
| 74 | erkin | 35 | diwin |  | N | erkin entry not found in Martirosyan text |
| 75 | mer̄anim | 25 | mers |  | C | M p0459 meṙanim |
| 76 | bowr̄n | 1 | bhoxr |  | W | M p0208 buṙn ~ Skt bhū́rṇi-; mapped *bʰṓr 'thief' |
| 77 | ačem | 22 | h2ewgeti |  | C | M p0057 ačem |
| 78 | erewim | 7 | prepeti |  | N | erewim not found as entry |
| 79 | gorcem | 27 | wergjom | E | C | M p0240 gorc/gorcem |
| 80 | bažanem | 9 | bheh2geti |  | W | M p0751 bažanem: 'borrowed from Iran.' |
| 81 | himn | 4 | kaikki:semen |  | N | himn not found as entry (p0423 mention only) |
| 82 | goł | 2 | kaikki:wol |  | N | goɫ: no etymology (p0597 mention only) |
| 83 | tʻałem | 3 | root:telh2-bear, root:telh2-ground |  | N | t‘aɫem not found |
| 84 | ēš | 2 | h1ekjwos |  | C | M p0290 ēš |
| 85 | orovayn | 8 | kropnyo |  | N | orovayn not found as entry |
| 86 | barjr | 7 | bhergjhus |  | C | M p0185 barjr |
| 87 | ber̄n | 2 | bherno |  | N | no entry in Martirosyan: beṙn (mention only, p0182) |
| 88 | aygi | 7 | root:h1eyHw-yew |  | C | M p0070 aygi < *h1eiH-u̯eh2- |
| 89 | ayl | 32 | h2elyos |  | C | M p0071 ayl |
| 90 | hacʻ | 9 | kaikki:peh₂ssk |  | C | M p0405 hac‘: *peh2s- considered (uncertain) |
| 91 | naw | 8 | neh2us |  | C | M p0514 naw (native vs Iranian loan disputed) |
| 92 | ownkn | 7 | h2oxws |  | C | M p0651 unkn |
| 93 | ayri | 9 | kaikki:n̥h₂neryeh₂ |  | C | M p0078 ayri *n̥-nēr-iyā |
| 94 | gorc | 9 | wergjom |  | C | M p0240 gorc |
| 95 | ełbayr | 24 | bhreh2texr |  | C | M p0266 eɫbayr |
| 96 | ost | 1 | h3osdos |  | C | M p0547 ost |
| 97 | owłi | 1 | h2ewlos |  | N | uɫi 'road' not in Martirosyan (p0168 is awɫi 'beer') |
| 98 | astł | 1 | h2stexr |  | C | M p0134 astɫ |
| 99 | glowx | 8 | root:gelH-naked |  | C | M p0234 glux ~ BSl *galvā (uncertain) |
| 100 | aycʻ | 3 | root:h2eys-wish |  | C | M p0078 ayc‘ *h2eis- |
