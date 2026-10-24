# Mapping precision: Classical Armenian (PROIEL + DMHP), Tocharian A, Old Albanian

These are the lemma → PIE tables for Stage C of the 8c reading experiment (`docs/research/8c-preregistration.md`, Stage C) for three of the newly acquired corpora:

- **DMHP**: the 5th-century Classical Armenian authors, 570k tokens, automatic lemmas, CC BY 4.0.
- **TITUS 2.0 Tocharian A**: Sieg & Siegling, research only (CC BY-NC-SA).
- **TITUS 2.0 Old Albanian**: Buzuku 1555, Bogdani 1685, Bardhi 1635, research only.

The existing `xcl` table was extended to DMHP rather than duplicated. The error types found by the independent check (`mapping-precision-east-independent.md`, strict 0.90) are fixed at source.

## What was built

| file | content |
|---|---|
| `pie/arm_toch_alb_mapping.py` | normalisers, lemmatizers, Martirosyan index, systematic fixes, table builders |
| `scripts/build_arm_toch_alb_mapping.py` | writes the three tables and `data/research/formulas/arm-toch-alb-coverage.json`; `--sample-dir/--seed` draws the precision samples |
| `data/research/formulas/mapping/xcl.jsonl` | 635 rows: 307 → 271 PROIEL rows, plus 364 DMHP-only rows |
| `data/research/formulas/mapping/xto.jsonl` | 202 rows, keyed by the lemmatizer's lemma key (or `a\|b`) |
| `data/research/formulas/mapping/sqo.jsonl` | 437 rows, keyed by kaikki Albanian lemma key |
| `data/research/formulas/mapping-overrides/arm-toch-alb.json` | 13 hand rows (12 xcl, 1 sqo), each with a dictionary note |
| `tests/test_mapping_arm_toch_alb.py` | 11 tests |

Every row has a `licence` dict naming each source that contributed to it:
- the corpus: `proiel`, `dmhp`, `titus-xto` or `titus-sqo`;
- `kaikki` (CC BY-SA);
- `lexicon`, when a lexicon reflex list was used;
- `martirosyan`, when Martirosyan's gloss chose between homographs.

xcl rows also carry `corpora` (`proiel` / `dmhp`). Rows used by DMHP carry `dmhp_lemmas`, the Armenian-script lemmas they serve.

**How the Stage C builder should look things up:**
- **DMHP lemma** → `am.DmhpLemma(am.proiel_lemmas())(lemma)` gives the table string. This is PROIEL's transliteration, with PROIEL's own lemma where the key matches: տէր → `Tēr`, ունիմ → `ownim`. One override row therefore covers both Armenian corpora.
- **Tocharian A** → `am.build_xto(...).lemmatizer` and `am.toch_lines`.
- **Old Albanian** → `am.build_sqo(...).lemmatizer(surface, text)` and `am.alb_units`.
- In all cases, apply `fm.apply_table_overrides(corpus, …)` as usual.

**Hazard.** `scripts/formula_search.py::write_mapping_tables` (round 3) still rewrites `xcl.jsonl` with PROIEL rows only, without the source fixes. If it is rerun, rerun `scripts/build_arm_toch_alb_mapping.py` afterwards. The hand corrections are in the override file and survive either way; a test asserts that the DMHP rows exist. Without `--all-dump`, the builder reads the 3 GB kaikki all-languages `.gz` once (≈1–2 min) for the Proto-Albanian (214) and Proto-Tocharian (141) pages.

`east.json` was **not changed**. Its 15 xcl rows still apply, now to DMHP as well, and no lemma has a row in both files (tested). No other table or override file was touched.

## Sources per corpus

**Armenian**
- Mapping: the kaikki Old Armenian chain, the lexicon's reflex lists, and Martirosyan's EDAIL (`raw/books/text/martirosyan-arm`; file page = printed page + 14).
- `MIndex` parses Martirosyan's head paragraphs and ●ETYM sections into 971 entries. They are used for homograph glosses, the hand rows and judging.
- Many common words have no Martirosyan entry, or one that the parser cannot find: kam, tesanem, erewim, jeṙn, sēr. Martirosyan's selection is the reason the N share is high.
- DMHP's own lemma and POS columns are used; content = N+Com, A or V in any `@` part.
- DMHP lemmas are automatic. Precision here is lemma → PIE, not token → PIE.

**Tocharian A**
- Lemmatizer: no lemmas in the source. The kaikki Tocharian A forms tables and headwords, with exact and then loose key. Then one secondary-case or plural ending stripped to reach a noun/adjective table form, or a verb ending stripped to reach a verb-root headword. A form is kept only if exactly one lemma is reached.
- Mapping: the kaikki A chain (Proto-Tocharian through the lexicon's 243 reflexes and the dump's pages) and the lexicon's A reflexes. A words *without an etymology of their own* also take the Tocharian B cognate's chain, but only if the A and B glosses share a word.
- Adams' *Dictionary of Tocharian B* (`raw/books/text/adams-tochb`) is local and was used for checking. Its "TchA X" citations are too OCR-damaged to extract automatically: a trial gave pairs such as A päñ under B etsuwai.

**Old Albanian**
- **No Albanian etymological dictionary is local** (no Orel, no Demiraj), so the mapping is kaikki and lexicon only. The precision figure is therefore partly circular: it tests the lemmatizer, homograph, loan and resolver errors, not the etymologies themselves.
- `alb_norm` normalises each orthography:
  - Buzuku: ſ, ћ, ξ, ɣ, ɛ, ɿ, gñ, final -eh;
  - Bogdani and Bardhi (Italianate): sc, ch/chi, kj, gi, gn, ξξ/ξ, λ, ü, è.
- `alb_skeleton` then absorbs s/sh, th/dh, r/rr, q/gj/ç and final ë. Lookup is exact first, then by skeleton against every kaikki form and its regular Gheg variants (rhotacism, ua/ue, -uar/-ue(m), -ur/-un(ë)).
- A skeleton shared by more than one lemma stays unmapped.
- `ALB_FORMS` fixes 117 frequent forms: function words, Gheg forms of jam/kam, and Hyj 'God', which kaikki lacks.
- Latin, Romance, Greek, Slavic and Turkish loans are unmapped by the resolver.

## Systematic fixes (in `postprocess`, applied to all three)

| rule | what it does | xcl | xto | sqo |
|---|---|---|---|---|
| hedged | every entry of the key opens "origin uncertain / unknown / disputed / left open / of uncertain (further) origin". The chain, lexicon-reflex and descendants links are all dropped (e.g. hanem, linim, leaṙn, glux, hayim, hacʻ, ǰur, tʻołum, ancʻanem) | 143 | 2 | 54 |
| borrowed | every entry of the key is a borrowing, so a lexicon-reflex link is dropped too (bažanem, agarak, naw: "a borrowing from the Iranian cognate is formally possible") | 14 | 2 | 13 |
| homograph | ids are homograph roots. One root is kept if the template gloss, the word's gloss or Martirosyan's ETYM gloss singles it out (aṙnem → *h₂er- 'fit'); otherwise the key is dropped | 38 + 5 resolved | 2 + 1 | 80 + 21 |
| root-gloss-mismatch | a single root id whose meaning shares no word with the template's gloss of the etymon (Alb. lut 'pray' ← *lew- 'sound', not the lexicon's *lew- 'dirt') | 5 | 3 | 54 |
| mixed-homograph (xto, sqo; plus strict homographs) | an unlemmatized surface cannot be assigned to one of two homographs (Alb. regj 'tan' vs regj 'king' < Lat. rēgem; Toch. wäs 'gold' vs 'poison') | – | – | 36 |
| key ō | the generic `key_xcl` dropped ō, so ōd 'air', -ōn and others collided with the clitics d, n, cʻ. The module key keeps ō | 3 junk rows gone | | |

Form-of and base-word rows copied from a dropped key are dropped with it (the `via-…` counts in the coverage file).

**Hand rows (`arm-toch-alb.json`).** These cover the independent check's W and P items not handled by a rule:
- ownim → *h₁ep- (Martirosyan p. 636);
- Tēr → *dṓm + *h₂nḗr (*ti-ayr, p. 61);
- tikin likewise;
- buṙn unmapped (p. 194);
- mard and mardik → *mr̥tós only (p. 452);
- ayg → *h₂éwsōs only (p. 54);
- haw → 'bird' (p. 398);
- aregakn → both members;
- hawt unmapped (p. 400);
- ełanim unmapped;
- **gam → *weh₂dʰ-** (p. 196). Martirosyan does not have *gʷem-, so the independent check's C verdict for gam was itself wrong;
- sqo kam → *kap- (the suppletive present).

## Coverage (content tokens; final build)

| corpus | content tokens | mapped | share | mapped types |
|---|---|---|---|---|
| DMHP (xcl) | 329,644 | 84,312 | **0.256** (by text 0.20 Koriwn – 0.31 Eznik) | 574 |
| PROIEL Armenian (xcl) | 9,430 | 3,918 | 0.416 (was 0.458 after east.json; the drop is the hedged and loan rules) | 227 |
| Tocharian A | 30,455 (non-fragment words; unknown forms counted as content) | 2,793 | **0.092**; 0.50 of tokens whose lemma is known | 177 |
| Old Albanian, all | 109,820 (unknown forms of more than 3 letters counted as content) | 9,698 | **0.088**; 0.30 of known-lemma tokens | 368 |
| — Buzuku / Bogdani / Bardhi | 49,076 / 54,595 / 6,149 | | 0.070 / 0.107 / 0.067 | |

The Bogdani loader reads `<p>` paragraphs only. About 7k words in its 489 `<ab>` blocks (and the contents lists) are not counted; adding them is a one-line change for Stage C.

DMHP's unmapped mass is largely genuine loans and names: Astowac, ašxarh, tʻagawor, hraman, zawr, azg, Kʻristos, ekełecʻi and others. Tocharian A coverage is bounded by kaikki's 504 A entries: 8,798 of 9,653 surface types are unknown to the lemmatizer. Old Albanian coverage is bounded by the orthographies: 17,419 skeleton types are unknown and 1,277 ambiguous.

## Precision

**Method.**
- Sample: 100 mapped content types per corpus, token-weighted. Repeated `random.choices` draws with repeats rejected (as in the Celtic builder).
- Seeds: seed 7 before the second round of fixes; seed 8 after (the single re-measure).
- Type definitions:
  - DMHP: table lemma;
  - Tocharian and Albanian: (surface form, lemma) pairs, so lemmatizer errors count. The exception is Tocharian seed 7, which was drawn on lemma types before this was changed.
- Verdicts:
  - **C** correct;
  - **P** right root plus a wrong id, or one member of a compound;
  - **W** wrong (false etymon, loan, homograph id, wrong lemma);
  - **N** the reference cannot confirm or refute.
- Reference:
  - Armenian: Martirosyan;
  - Tocharian: kaikki and lexicon, with Adams spot checks;
  - Albanian: kaikki only.
- Strict = C/(C+P+W); lenient = (C+P)/(C+P+W); conservative = C/n. Wilson 95% intervals.

| corpus | sample | C | P | W | N | strict (95% CI) | lenient | conservative |
|---|---|---|---|---|---|---|---|---|
| DMHP | seed 7, before | 73 | 3 | 1 | 23 | 0.95 (0.87–0.98) | 0.99 | 0.73 (0.64–0.81) |
| DMHP | **seed 8, after** | 78 | 1 | 0 | 21 | **0.99 (0.93–1.00)** | 1.00 | 0.78 (0.69–0.85) |
| PROIEL xcl | the independent check's 100, re-scored (its verdicts kept; changed rows re-judged); 16 items now unmapped | 67 | 0 | 0 | 17 | 1.00 (0.95–1.00) of 84 still mapped | 1.00 | 0.80 (0.70–0.87) |
| Tocharian A | seed 7, before (lemma types) | 85 | 4 | 5 | 6 | 0.90 (0.83–0.95) | 0.95 | 0.85 |
| Tocharian A | **seed 8, after** | 88 | 1 | 5 | 6 | **0.94 (0.87–0.97)** | 0.95 | 0.88 |
| Old Albanian | seed 7, before | 62 | 1 | 29 | 8 | 0.67 (0.57–0.76) | 0.69 | 0.62 |
| Old Albanian | **seed 8, after** | 80 | 2 | 10 | 8 | **0.87 (0.79–0.92)** | 0.89 | 0.80 (0.71–0.87) |

The 16 PROIEL items that are now unmapped held 4 of the independent check's 6 W (hanem, agarak, buṙn, bažanem). They also held 7 C, 5 of which the check itself called weak: leaṙn, glux, hayim, hacʻ, naw. The other 2 W (ownim, Tēr) and both P (aṙnem, ayg) are now C.

**After seed 8 (not re-measured).** Two further fixes target 8 of the 15 non-C, non-N seed-8 Tocharian and Albanian types:
- The B-cognate fill no longer refills keys that have their own etymology or were dropped as homographs. This removes Tocharian wäs and ko, i.e. 4 of the 5 W types (verified in the table).
- `ALB_FORMS` now covers këtë, qenë, bëhet, vërtet and gjallë. Of the 10 Albanian W types, this addresses 4: ketè, cheteh, chene, bahetè.

So the seed-8 figures are a lower bound for the shipped tables, but they have not been re-measured.

## Remaining error types

**DMHP**
- Almost all of the residue is N (21–23%). These are words that Martirosyan omits or that the parser cannot find: kam, tesanem, erewim, jeṙn, sēr, pʻokʻr, owsowcʻanem. The kaikki etymology for each is unhedged.
- One P: əntʻanam, a union of two etyma.
- Lemmatization errors are DMHP's own, and they are not measured here.

**Tocharian A**
- Homograph roots taken by the loose key: käm- 'come' → kam 'tooth'.
- Lexemes of two roots in one row: āñcäm.

**Old Albanian**
- The orthographies are ambiguous. Buzuku's ſ and ξ, and the loss of ë, make the skeleton collide: leu → lyej, ћall, verteh, lechietè.
- One wrong Proto-Albanian reflex: shtie → *steríh₂s.
- Suppletive verbs: kam is mapped to *kap-, which is wrong for its *pot- past forms (pata, pasha).

A larger Gheg form list, or Orel/Demiraj from David, would be needed for real progress.

**Overall caveats**
- These are single-judge verdicts by the agent that also wrote the fixes. An independent re-check, as was done for east, would be the next step.
- The Tocharian and Albanian references are the same kaikki data the mappings came from.

## Appendix: verdicts

The seed-7 and seed-8 lists below give lemma, token count, verdict and locator. Martirosyan locators are file pages `pNNNN`; printed page = file page − 14.

**DMHP seed 7.** C at: em p0268, asem p0131, kin p0376, anown p0110, gorc p0240, anjn p0107, get p0218, am p0058, ariwn p0152, otn/het p0548 (s.v. ot), aṙnem p0126, tam p0609, town p0632, dnem p0253, aṙnum p0126, ordi p0549, hiwtʻ p0423, gtanem/gitem p0225, ankanim p0103, awr p0169, lnum p0336, duṙn p0257, mēǰ p0480, lsem p0327, ałbewr p0046, hayr p0400, gom p0235, meṙanim p0477, gam p0210, meł p0476, sirt p0590, hin p0422, erkar p0280, ownim p0650, krkin p0392, ǰan p0570, Tēr p0075, ban p0180, pʻoytʻ p0665, arawt p0139, surb p0602, utem p0658, cer p0353, ayr p0075, hur p0440, barjr p0184, loys p0325, li p0323, mit p0484, acem p0030, jor p0452, arew p0150, baṙnam p0182, tawn p0623, gorcem p0240, tur p0336, mec p0472, zgest p0288, awn p0169, ełbayr p0265, kočʻem p0385, nor p0875, nstim p0519, tiw p0630, ayrem p0077, hot p0433, gišer p0229, ezr p0261, mnam p0485, jew p0446.

The non-C items in DMHP seed 7:
- **P**:
  - aregakn: one member;
  - mardik: + *smr̥tós;
  - haw: 'bird' + 'grandfather'.
- **W**: hawt (p0414: Martirosyan rejects *peh₂-).
- **N**: kam, owsanim, howp, erewim, sermn, mart, tʻałem, lam, imanam, ełanim, erkin, tesanem, nerkʻin, serem, banam, yaṙnem, cnoł, eresun, pʻčʻem, du, stēp, ger, bun.

**DMHP seed 8** (60 types overlap seed 7):
- **P**: əntʻanam.
- **N**: tesanem, erkin, erewim, čʻowem, kam, hog, mart, erdnum, tʻałem, jeṙn, artasukʻ, manr, sēr, lucʻanem, beran, iǰanem, pʻokʻr, usucʻanem, du, sur, yaṙnem.
- **C**: all others. New C locators: keam p0370, hing p0422, sor p0597, tasn p0616, gin p0227, awd p0164, arǰ p0157, giwt p0225, akn p0036, čanačʻem p0454, erēk p0276, hnocʻ p0428, erknčʻim p0282, awcanem p0166, tʻurc p0311, unayn p0649, berem p0190, boys p0201, lur p0336, art p0159, utʻ p0645, oskr p0547, harcʻanem p0410, ənkenum p0294.

**Tocharian A seed 7**
- **W**:
  - ke 'chance' (filled from B kaiyye 'cattle');
  - ype (*h₁ep- for 'land');
  - wäs ('gold'/'poison');
  - āl (kaikki: of uncertain further origin);
  - tsmār (from B witsako, which Adams p0673 [printed 657] calls a probable Iranian loan).
- **P**: wäl, āñcäm, ko, pärk (unions).
- **N**: lyāk, tāśśi, mem, ok, tsno, ārśi.
- Adams p0187 confirms mäsk- < *mn̥-sḱe/o-.

**Tocharian A seed 8**
- **W**: wasäṃ, was, wäs (wäs homographs refilled by the B cognate; fixed afterwards); ko (filled from B kau- 'kill'; fixed afterwards); käm (loose key → kam 'tooth').
- **P**: āñcäm.
- **N**: lyāk, memaṣ, mem, är, śākwis, ārśi.

**Old Albanian seed 7.** 29 W:
- 18 lemmatizer errors, e.g.:
  - hi (article) → hi 'ash';
  - endeh/endè (ende/edhe) → endë 'pollen';
  - ender (ndër) → ëndërr 'dream';
  - kjanè/cheneh (qenë) → qaj/kam;
  - ξom (thom) → dhomë 'room';
  - flit (flet) → fli;
  - ћis (kish) → qit;
- the forms of kam mapped to *pótis;
- Hyj 'God' → hyj 'enter';
- homographs: dua 'want' vs 'bundle', mund, regj 'king' (Lat. loan);
- the root id *lew- 'dirt' for lut;
- magar (substrate per kaikki);
- kallëzoj (three roots).

Seed 7 also has 1 P (paam, suppletive) and 8 N.

**Old Albanian seed 8.**
- **W**:
  - hüje → hyll;
  - ketè and cheteh (këtë) → kam;
  - leu → lyej;
  - ћall → qall;
  - verteh → vërri;
  - chene (qenë) → kam;
  - lechietè → lak;
  - bahetè → bahe;
  - ſtiim → *steríh₂s.
- **P**: ћella (two roots), paſcha (suppletive aorist).
- **N**: gjegj ×2 (no etymology in kaikki), mberat, trimit, degna, siλatè, ћigneh, hiim.
