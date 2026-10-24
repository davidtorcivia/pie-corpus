# Mapping precision: Balto-Slavic round-4 corpora (vuk, byliny, dainos, ccmh)

These are word → PIE mappings for the four Balto-Slavic text sets added in round 4, made for Stage C of the 8c reader experiment (`docs/research/8c-preregistration.md`). None of the texts is lemmatized.

- **Code:** `pie/bsl_mapping.py` (new module) and `scripts/build_bsl_mapping.py`.
- **Tables:** `data/research/formulas/mapping/{vuk,byliny,dainos,ccmh}.jsonl`.
- **Coverage:** `data/research/formulas/bsl-coverage.json`.
- **Precision verdicts (all 800):** `data/research/formulas/bsl-precision-verdicts.json`.
- **Hand corrections:** `data/research/formulas/mapping-overrides/balto-slavic-new.json`.
- **Tests:** `tests/test_mapping_bsl_new.py`.

No other mapping table, override file, lexicon or engine file was changed. I did not touch git.

## Sources (what feeds each table)

| corpus | lang | editions (licence in each row's `licence` field) | line filter | word tokens |
|---|---|---|---|---|
| vuk | sh | Vuk, *Srpske narodne pjesme*, sr.wikisource (CC BY-SA; text PD) | line numbers and footnote marks stripped; editorial lines dropped (digits, `стр.`, `Караџић`, `издање`, Latin words, > 14 words) | 705k |
| byliny | ru | ru.wikisource Kirsha Danilov / Rybnikov pt. I / 2 Hilferding (CC BY-SA); OCR Hilferding 1896–1900, Kireevsky 1860–74, Rybnikov 1861–67 (PD) | wikisource: every line. OCR: verse-like lines only (2–8 words, ≥ 85% Cyrillic, no 2-digit number, no final hyphen) | 798k |
| dainos | lt | Rhesa, Nesselmann, Schleicher, Leskien–Brugmann, Bartsch, Juškevič (all PD OCR) | a line is kept when its Lithuanian evidence outweighs its German evidence (`lt_line`); hyphenated breaks joined | 356k |
| ccmh | cu | CCMH Marianus, Zographensis (+ Zogr-B), Assemanianus, Savvina, Suprasliensis (CC BY) | all lines; `{…}` dropped; words under titlo (abbreviations) and words with `?` skipped | 266k |

Notes on the sources:
- Rybnikov pt. I is in both the wikisource and the OCR sets, about 15k tokens counted twice.
- The CCMH Vitae (later copies) are left out.
- The kaikki Serbo-Croatian and Russian entries are not in any per-language kaikki extract. I cut them from the all-languages dump into `raw/daughters/kaikki-all-20261021/split/{serbo-croatian,russian}-trimmed.jsonl`. These are trimmed fields, not verbatim lines; `bm.ensure_split` regenerates them if missing. `raw/MANIFEST.md` should get a line for them.

## Method

### Lemmatizer (`BslLemmatizer`)

A surface form is looked up in the kaikki form tables: inflection tables, form-of pages, and multiword table forms reduced to their main word.

- **Order of lookup:** the exact key first, then the loose key, then edition-specific spelling variants. A variant that is a diminutive guess must hit a noun or adjective headword itself.
- **Ambiguity:** a form that belongs to several lemmas gives `a|b`. A union is mapped only if every part is mapped to the same root group. An unmapped part does not block the union only when it is one of these:
  - an ijekavian/ekavian spelling variant;
  - a same-stem word (common prefix of 4 or more letters) that has no etymology of its own in kaikki. A word whose etymology was vetoed or did not resolve does block (`lm.etym_keys`), so SCr. `drag|draga` stays unmapped;
  - a junk form-of string.

  Otherwise the form stays unmapped.
- **Keys:**
  - `key_sh`: Cyrillic → Gaj Latin, tone marks off. ć and č are kept apart, so Vuk's ћу 'I will' is not чу 'hear'.
  - `key_ru`: stress off; ё → е; pre-reform ѣ і ѳ ѵ normalised; word-final ъ off.
  - `key_lt`: tone marks off; ą č ę ė į š ų ū ž kept.
  - CCMH: the codex transliteration tables → Cyrillic → `key_cu`.
- **Spelling variants by edition:**
  - **Vuk:** elision (ил' → или), jotated ђ/ћ (ђевојка → дјевојка), dropped х, ijekavian long endings (-ијем), ije ↔ je.
  - **Russian:** -аго / -ыя / -ія; Kirsha's -ова; dialect -ой / -ол; contracted byliny adjectives (чисту); OCR $ / Ъ / 1 / ф for ѣ and і; hypocoristic diminutives; preverb stripping.
  - **Lithuanian:** sz cz ż w ů ł; Polish-style aj/ej; Juškevič's -ej and y for i; diminutives; particles and preverbs. Verb forms are generated from the three principal parts (`lt_verb_forms`), because kaikki has few Lithuanian verb tables. Personal and reflexive pronoun forms (manęs, manės, mane, manę, tavęs …) are pinned to their pronoun (`LT_PRONOUNS`).
  - **OCS:** the TOROT/PROIEL (form, lemma) pairs are added to the kaikki OCS table, so CCMH lemmas are TOROT lemmas.
- **Suppletion:** for the present *h₁es- forms of 'be' (Serbian jesam / sam / je; OCS естъ / есмь / нѣстъ), a separate lemma maps to *h₁es-.
  - The SUPPLETIVE patterns plus a first-letter check keep шёл, люди, лучше, išao and ljudi from inheriting their lemma's etymon.
  - SCr. sam therefore becomes `sam|jesam` and stays unmapped, because it is ambiguous.
- **Names:** a capitalised word that is not line-initial is treated as a name and is not mapped (`bm.is_name`). The Stage C builder must apply the same rule.

### Lemma → PIE

This step runs kaikki etymology chains through `formula_search_multi.build_lang_mapping`, with these additions:
- Russian resolves through Old East Slavic, and Russian and Serbian through OCS (Church Slavonicisms).
- Borrowings inside the branch (Ru. солнце 'learned borrowing from Middle Russian') are followed.
- Proto-level affix derivations are followed (*junakъ = *junъ + *-akъ; *vъzęti = *vъz- + *ęti).
- Wiktionary homograph anchors (`#Etymology 2`, `<id:say>`) are honoured.

Loans and unclear etymologies are vetoed at the proto level:
- a Proto-Slavic / Proto-Balto-Slavic / Proto-Baltic page with a non-ancestral source next to the PIE link (*rajь);
- a page whose etymology text says loan from Iranian, Turkic, Germanic and so on, or says the etymology is unknown;
- the `LOAN_PROTO` list (Derksen: *bogъ and its family).

A daughter word that reaches PIE only through a vetoed page gets no mapping, not even from a root template, a lexicon reflex list or a stage entry (Ru. бог → orv богъ → *bogъ).

The following are also left unmapped:
- a key that names two dictionary words of different etymology (SCr. grad 'city' / 'hail', pasti 'graze' / 'fall');
- a key that names a borrowed homograph (SCr. beg 'bey').

When the ids of a mapping fall in two homograph lexicon roots, only the root whose gloss matches the word's gloss is kept (aušra → *h₂ews- 'dawn', not 'draw water').

Derksen's EDSIL and EDBIL are parsed for headword, Ru./SCr./OCS forms, the PIE line (font damage repaired) and loan notes (`derksen_*_entries`). They serve as the judging aid and as a source for 2 Lithuanian headwords. The text layer is too damaged for automatic Slavic mapping: only about 120 of 700 PIE lines resolve.

### Hand corrections (`balto-slavic-new.json`)

Every row cites a dictionary and printed page, or states that Derksen has no entry and the Wiktionary chain is speculative. The file holds three kinds of row:
- **5 lemma rows**, in the standard format. For example, byliny град is a homograph, and ccmh богъ / божии / божьство / богатъ are the Iranian loan.
- **30 `proto` rows.** They change a Proto-Slavic page, and every daughter word built on it follows. There are 4 remaps:
  - *byti and *byvati → *bʰuH-;
  - *pьsati → *peiḱ- 'paint';
  - *kloniti → *ḱley- 'lean'.

  The other 26 are unmaps, for etyma that Derksen calls unclear (*dorgъ, *bъrzъ, *bystrъ, *krotъkъ, *ľutъ, *topiti II), for the wrong homograph root (*golsъ), or for Wiktionary-only speculation (*sokolъ, *dvignǫti → 'two', *xvatiti → 'self', *raziti / *razъ / *obrazъ, and others).
- **40 `key` rows.** They change a daughter headword, including its base-word and preverb derivatives:
  - SCr. vesti and pasti are homographs. The -vesti compounds → *wedʰ- 'lead' (Derksen p. 517).
  - Other SCr. rows: dijete → *dʰeh₁(i)-; primiti → *h₁em-.
  - Ru. быть → *bʰuH-; пасть → *pod- (p. 392); посол is a homograph.
  - Lith. aukštas → *h₂eug- (EDBIL p. 70); bėda is a loan; mesti and others are unmapped.

  A key row reaches a derived word only through the word's daughter-level path elements (`<lang>:`, `base:`, `form-of:`), never through a proto-form.

`fm.load_overrides` reads only the lemma rows, and the file has no form rows. Form rows for sh, ru or lt would make `load_overrides` fail in any process that has not imported this module. The `proto` and `key` rows are applied by `bsl_mapping.build_mappings`.

## Coverage (content tokens; names counted as unmapped / left out)

| corpus | content tokens | before: mapped | after: mapped | after, no names | unknown forms |
|---|---|---|---|---|---|
| vuk | 417k | 0.386 | 0.326 | 0.382 | 25% |
| byliny | 482k | 0.363 | 0.326 | 0.382 | 33% |
| dainos | 233k | 0.250 | 0.211 | 0.231 | 63% |
| ccmh | 127k | 0.586 | 0.582 | 0.582 | 8% |

In the "before" column, names were mapped. Before, without names: vuk 0.439, byliny 0.406, dainos 0.259, ccmh 0.586.

Coverage by source:
- **Byliny:** wikisource 0.46 and Hilferding 0.41 (both without names), Kireevsky 0.36.
- **Dainos:** Leskien–Brugmann 0.32, Nesselmann 0.31, Juškevič 0.21. Rhesa, Bartsch and Schleicher are 0.00–0.07: their OCR (Gothic type, German) gives almost no readable Lithuanian, so these three editions are effectively absent from the dainos table.

The tables hold:
- every mapped lemma string the lemmatizer produced on the corpus;
- every other mapped headword of the language.

The table sizes are vuk 8,306 rows, byliny 38,745, dainos 5,967 and ccmh 3,204.

## Precision

**Sample.** 100 mapped content types per corpus. A type is a (surface, lemma) pair, so lemmatizer errors count. The draw is weighted by tokens, as in the east independent check: `random.Random(seed).choices` over sorted types, rejecting duplicates.

**Verdicts.**
- **C:** the etymon is right at root-group level.
- **P:** the right id plus a wrong one, or the compound member only.
- **W:** a wrong or speculative etymon, a homograph root, a loan, or a wrong lemma.

The verdicts were judged against Derksen EDSIL and EDBIL (read with `python3 -I`) where they have an entry. Otherwise they were judged on the kaikki etymology. Intervals are Wilson 95%.

The "after" sample is a fresh seed, 8, drawn on the shipped tables. A first seed-8 draw, made before the last fixes (the union rule, key-row matching, Lithuanian pronouns, *razъ), was replaced by a new draw. Items present in both draws with the same ids kept their verdict: 29 / 16 / 21 / 26 of the 100 in vuk / byliny / dainos / ccmh. Every other item was judged anew.

The "before" sample (seed 7, first build) still mapped proper names (Иве → iva 'willow'). That widens the before → after gap a little.

| corpus | before (seed 7): C / P / W | strict (95% CI) | after (seed 8): C / P / W | strict (95% CI) | lenient after |
|---|---|---|---|---|---|
| vuk | 79 / 5 / 16 | 0.79 (0.70–0.86) | 95 / 0 / 5 | 0.95 (0.89–0.98) | 0.95 |
| byliny | 85 / 2 / 13 | 0.85 (0.77–0.91) | 90 / 3 / 7 | 0.90 (0.83–0.94) | 0.93 |
| dainos | 81 / 9 / 10 | 0.81 (0.72–0.87) | 84 / 5 / 11 | 0.84 (0.76–0.90) | 0.89 |
| ccmh | 92 / 0 / 8 | 0.92 (0.85–0.96) | 98 / 1 / 1 | 0.98 (0.93–0.99) | 0.99 |

In the after-sample, the C types carry this share of the sampled tokens: vuk 0.99, byliny 0.97, dainos 0.94, ccmh 1.00.

**Caveats.**
- I wrote the fixes and also judged the after-sample, so this is not an independent estimate. An independent re-check, like the one done for the east group, should follow.
- Some C verdicts rest on a kaikki chain that Derksen does not cover. The "not in Derksen" rows of the override file show how often that happens among the frequent words.
- Dainos did not improve beyond sampling noise.

## Main error types found (and fixed)

1. **Homograph keys.** One spelling, two words of different etymology:
   - SCr. grad, pasti, vesti, pitati, desni, danak and nit (`nit'` = niti), and sam 'alone' / sam 'I am';
   - Ru. град, посол, пасть.

   Fixed by the homograph rule, the key rows and the strict union rule.
2. **Suppletion.**
   - быть and бывать → *h₁es- (495 + 220 tokens in byliny).
   - OCS естъ / есмь → *bʰuH- through the TOROT lemma бꙑти.
   - Lith. manę 'me' read as a form of manyti.
3. **Speculative or rejected Wiktionary etyma** in the Proto-Slavic pages: *bъrzъ → *mréǵʰus, *dorgъ → *der-, *dvignǫti → 'two', *xvatiti → 'self', *topnǫti → 'not', *golsъ → *gelH- 'naked', and the *sokolъ, *svěžь, *guja, *slěpъ group. These are proto rows.
4. **Lemmatizer collisions.**
   - The loose key merged ć and č, so ћу 'I will' (1,643 tokens) was read as čuti.
   - Diminutive guesses landed on verb forms (brėlu → bristi).
   - Short OCR tokens were read as dictionary abbreviations (vard. → vardininkas).
   - Vuk's elided нит' was read as nit 'thread'.
   - Names were mapped (Иве → iva 'willow').
5. **Wrong preverb or base splits:** primiti → miti 'wash'; pobjeći → po; odvesti → *vezti 'convey'; tikras, губа, брдо, частый → a suffix.
6. **Iranian, Germanic and Turkic loans.** These were mostly caught by kaikki's `bor` templates. The proto veto now also stops the routes that went through stage entries and root templates. The test asserts that бог / bog / богъ / божии, рай, собака, топор, князь, хлеб, шлем, богатырь, лошадь, царь, knjiga, kula, puška, sablja and vino are absent from the tables.

## What remains

The P and W items of both samples are listed in the appendix. These errors turned up in the samples or the top-300 review but were not fixed:

- **vuk.**
  - jad / jadan → *h₂eyd- 'swell'. It should be *h₁ed-, from *ědъ 'poison'.
  - viknuti / *vykati → *h₂ewH- 'put on'. This is a homograph root.
  - rujan → *h₃rew-.
  - Speculative kaikki chains: kititi, okrenuti / krenuti, lud, plašiti, ruho, čekati.
  - predaše is lemmatized as presti 'spin', but it is the aorist of predati.
- **byliny.**
  - Unions of homograph roots remain P: ясный, копье, стук.
  - цвет is chained to *ḱwoyt- 'light', but *květъ is a different word.
  - род → *wréh₂ds 'root'.
  - Speculative chains: лоб, луг, бросать, гаркнуть, древний.
  - OCR fragments: полото, вфсомъ.
- **dainos.**
  - OCR is the main problem: 63% of the content forms are unknown, and short OCR fragments still get mapped (ės, geg, bėdės, kos).
  - Homograph roots: šalna / šaltas, kalbėti, kilnus.
  - Speculative roots: didis, paukštis, džiaugtis, koja, and šarka → *ḱḗr 'heart'.
  - mažas 'small' → *méǵh₂s 'big'.
  - pjauti → *peh₂w- 'few'.
- **ccmh.**
  - The round-3 `cu` rows (east.json) are kept unchanged, except that the loan veto removes rows built on a vetoed proto-form (богъ).
  - The proto unmaps (*strojiti) do not reach round-3 rows such as ооустроити.
- **Not done:** Derksen as an automatic Slavic source (the text layer is too damaged); the Kireevsky commentary filter beyond the verse-length heuristic; deduplication of Rybnikov pt. I; the CCMH Vitae.

## Using the tables in Stage C

```python
from pie import bsl_mapping as bm
maps = bm.build_mappings(); ocs = bm.ocs_mapping(maps)        # ~70 s
lz = bm.lemmatizer("vuk", maps, ocs); table = bm.read_table("vuk")
for locus, units, text in bm.UNITS["vuk"]():
    for i, w in enumerate(bm.corpus_words("vuk", text)):
        ids = None if bm.is_name("vuk", w, i) else table.get(lz(w))
```

`read_table` applies every override file, and `apply_table_overrides` strips the blocked ids. The tables hold no corpus text.

## Appendix: P and W verdicts

All 800 verdicts, including the C items, are in `data/research/formulas/bsl-precision-verdicts.json`, with token counts and ids. Each entry below is `surface [lemma] → mapped id: verdict, reason`. Page numbers are printed pages of Derksen EDSIL (Slavic) and EDBIL (Baltic).

**Before (seed 7, first build).**

- **vuk**
  - подигоше [podići] → *dwóh₁ 'two': W (speculative; not in EDSIL)
  - брже [brz] → *mréǵʰus: W (EDSIL p. 70: 'dubious')
  - граду [grad]: P (union of 'city' and 'hail')
  - јавну [javni]: P (two homograph roots *h₂ew-)
  - одведоше, поведе, доведени [-vesti] → *weǵʰ-: W (the forms have -ved-, so *wedʰ-; p. 517)
  - бију, бјеше [biti]: P (union of 'be' and 'beat')
  - допаде [dopasti] → *peh₂- 'graze': W (pasti II 'fall', p. 392)
  - драги [drag] → *der-: W (p. 113: 'Etymology unclear')
  - сокола, бистра, свежи, гују: W (speculative)
  - кака [kaka] 'faeces': W (Vuk's kaka means kakva)
  - сам [sam] 'alone': W (usually 'I am')
  - ћу [čuti]: W (the loose key merged ć and č)
  - иве [iva], мирко [mirko]: W (names)
  - тврде [tvrd]: P (homograph roots)
- **byliny**
  - спохватится → *swé: W
  - быть, бывать → *h₁es-: W (p. 71)
  - выражены, образцовъ → *wreh₁ǵ-: W (speculative)
  - заметало → *smeyt-: W
  - застрахованы, платье, отстроенная: W (speculative)
  - сукрой, истори: W (wrong lemma)
  - утонуль → *ne: W
  - голосомъ → *gelH- 'naked': W (p. 176)
  - прощене: P (only one member of a compound)
  - писаному: P (homograph roots)
- **dainos**
  - brėlu, avėlu, krutu, nukris: W (diminutive guess or wrong lemma)
  - minę, auszrele, kalbėti, pakėlsi, pakelė, užkėlė, užteka, numirs: P (homograph roots or mixed union)
  - aukszta → *h₂weks-: P (EDBIL p. 70 has *h₂eug-)
  - ti, da: W (short tokens)
  - manę [manyti]: W (the pronoun 'me')
  - reiks: W
  - žvirblis, šaltiniu: W (speculative or homograph root)
- **ccmh**
  - естъ, есмъ, нѣсмъ → *bʰuH-: W (suppletive forms of *h₁es-)
  - кротъкъ: W (p. 250)
  - слѣпъ, рѫгати, винꙑ, чрѣвиемъ: W (speculative)

**After (seed 8, shipped tables).**

- **vuk**
  - јадна [jadan] → *h₂eyd-: W
  - искићене [iskititi] → *kewh₂-: W
  - рујно [rujan] → *h₃rew-: W
  - предаше [presti]: W (wrong lemma; it is predati)
  - окренути → *skert-: W (speculative)
- **byliny**
  - цвътъ [цвет] → *ḱwoytós: W
  - гаркнули, бросали, лобъ, луга: W (speculative or onomatopoeic)
  - полото: W (OCR)
  - род → *wréh₂ds: W
  - ясныя, копьемъ: P (homograph roots)
  - нельзя: P (only one member of a compound, *ne)
- **dainos**
  - šarka → *ḱḗr: W
  - didis, džiaugės, džiaugėsi, paukštėlės, kojėlų: W (speculative roots)
  - vainelė [vaina]: W (wrong lemma)
  - ės, geg, bėdės: W (OCR fragments)
  - szalnelės [šalna]: W (homograph roots)
  - žėntaj, ves, kalbėti, kalbi, kilnu: P (homograph roots or an extra id)
- **ccmh**
  - боурѫ [боурѧ] → *bʰer-: W
  - начьнете: P (union with *sken-)
