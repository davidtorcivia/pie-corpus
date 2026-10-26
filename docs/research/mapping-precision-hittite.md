# Mapping precision: Hittite (TLHdig → PIE, EDHIL route)

The later [review of the 200 most frequent unmapped lemmas](mapping-precision-hittite-reviewed.md)
adds explicit decisions against existing lexicon entries and reports updated coverage. In particular,
the historical discussion below understates the lexicon: warp- resolves to *werp-, šakk- to *sekH-
(not *sekʷ-), and mēḫur to the diminishing *meyH- family after reviewing the entry discussions.

Table: `data/research/formulas/mapping/hit.jsonl`. It is regenerated alone by `uv run python -I scripts/formula_search.py mapping --corpus hit`. The code is in `pie/hittite_mapping.py` (`hittite_table`), and the round-3 `R3._hittite` calls the same function. The loader rules are in `pie/formula_search_multi.py` (`hit_analysis`, `hit_word_kind`, `hit_pos`, `hit_lemma_stems`, `kloekhorst_entries`). Tests are in `tests/test_hittite_mapping.py`.

The precision figures below are **my own judgment of my own rules**. An independent blind check is still to come.

## Method

### 1. Content words and names (loader rule)

TLHdig tags every word with a morphological analysis and an inflection-class number. `hit_word_kind` reads TLHdig's own tags; there is no list of frequent items.

- **Function words** are not content. A word counts as a function word when every analysis's leading class tag is:
  - a connective: `CONNn`, `CONNt`, `CONNs` (the chains n=at, n=aš=kan, nu=war=an, ta=aš);
  - a pronoun: `PPRO*`, `DEM*`, `REL`, `INT`, `INDF*`, `INDoth`, `POSS`;
  - a particle, negation or conjunction: `PTC`, `NEG`, `CNJ`, `IRR`;
  - a numeral: `QUANcar`, `QUANmul`.

  A lemma without a gloss that starts with a connective (`n=`, `nu=`, `ta=`, `t=`, `šu=`, `š=`) is a function word as well.
  - Before, `CONNn=PPRO.3SG.N.NOM` counted as a noun because its morphology string contains "NOM".
  - `apa-` 'he, that' (DEM) is now a function word, like pronouns in the other corpora.
  - `ḫumant-` 'all, whole' (`QUANall`) stays content, as an adjective would.
- **Names** are not content and are never mapped (`pos = "name"`).
  - A name has a name tag (`DN`, `GN`, `PNm`, `PNf`, `PPNf`, `Nm`, …) in any analysis, or a TLHdig name inflection class: 35 divine, 37 and 38 personal, 39 geographical.
  - The class covers analyses without a name tag, such as `…:D/L.SG` of Ḫepat.
  - This follows the Stage C builder's rule for the tagged DMHP corpus (N+Top/N+Ant are not content).
  - Coverage is given both ways: names left out of the denominator, and names counted as unmapped content (the Celtic and Balto-Slavic reports do the same).
- **Selection marks.** TLHdig marks such as ①, Ⓐ, ⓷Ⓐ, ⓶ⓑⒸ are removed from the lemma. Before, `Ⓐ apa-@er` and `apa-@er` were two types. A token whose proposals differed only in the mark was dropped as ambiguous.
  - In `mapping-overrides/east.json`, the 72 hit rows keyed by a marked lemma were exact duplicates (same `lex_id`) of rows for the unmarked lemma. They are removed; nothing else in the file changed.

### 2. TLHdig lemma keys

`hit_lemma_stems` and `hm.lemma_keys` normalise the TLHdig lemma as follows:

- `/` between stems is split: `ēd-/ad-`, `ḫaršar/ḫarš(ša)n-`.
- A one-vowel alternation is expanded in place: `iye/a-` → iye, iya; `kara/ep(p)-` → karap(p), karep(p). Before, `iye/a-` was split into "iye" and "a".
- A consonant before the slash marks two stems: `išpart/za-` → išpart, išparza.
- `, ` separates alternants: `šak(k)-, šek(k)-`.
- Parenthesised optional letters are expanded: `ā(e)`, `(k)`, `(ya)`.
- `=`, `˽` and homograph digits (`kurš=i-2`) are removed.
- For a segmented lemma, the stem without its last short segment is also tried: arr=a- → arr, mem=išk- → mem, pešš=iye/a- → pešš.

The damaged key (`hit_damaged_key`) deletes ḫ, h, w, y and j, unmarks vowels, and makes geminates and plene spellings single. y is new; EDHIL's i̯ glyph is lost in the text layer.

### 3. EDHIL (Kloekhorst 2008) headwords

`kloekhorst_entries` was rewritten. It now reads:

- headwords separated by `, ` as well as ` / ` (`parši-a(ri), parš-a(ri)` was not parsed before);
- starred heads (`*arma-`, the reading of a logogram);
- an entry that follows a running head or page-number line;
- the class label and Kloekhorst's English gloss;
- the printed page number from the page header.

Rules for the PIE line:

- It is split at `, `, ` / `, `;`, ` or `. `h1/3` and `é/ó` are not split. Before, `*h1/3rs-` was parsed as `*h1`.
- A `?` anywhere on the line marks the entry as **doubtful**.
- An entry without a PIE line, or with a foreign label (Luw., Hurr., Hatt.), stays unmapped.

The result is 900 entries: 590 with a PIE line, of which 126 are doubtful.

The text layer replaces the glyphs of a private-use font with control characters, and the code depends on the font:

- In headwords, `\x02` is ḫ or ē, `\x04` is ā, `\x05` is i̯ or ū, `\x06` is w.
- In PIE lines, `\x05` is i̯, `\x06` is u̯, and runs of `\x02`–`\x04` are dorsals (ḱ, ǵ, ǵʰ).

A headword stem therefore becomes a regex on the damaged key in which each lost glyph matches an optional vowel (`edhil_stem_pattern`).

### 4. Choosing the headword

The candidates are the entries whose stem pattern matches a key of the lemma. The headword must also **agree in meaning**: an English word of Kloekhorst's gloss must equal a translation of the TLHdig German gloss.

- The translations come from `fm.HIT_DE_EN` united with `hm.DE_EN_MORE`. `DE_EN_MORE` is a general German–English vocabulary; it is used only for comparing glosses and never to choose an etymon.
- Words are stemmed, irregular forms are mapped (ground → grind), and stop words and light verbs are dropped.
- If no candidate agrees, the lemma stays unmapped. Several agreeing candidates are accepted only if they resolve to the same ids.

The old route accepted any unique damaged-key match with no gloss check, which let in kuwa= 'kosten' → kuen- 'to kill'. That route is gone.

### 5. Resolving the PIE line to lexicon ids

- **Whole form** (`resolve_form`, how `kloekhorst`): `FuzzyPie` matches the whole form, with a key of at least 4 letters.
  - A single lexeme (or one root group) is taken as is.
  - Root ids, homographs of several groups, and short stems (`*h₂us-`, a tree-path stub of *h₂ews- 'draw water') are kept only if their meaning, or their parents' meaning, agrees.
  - A form with a lost glyph is skipped. Its plain key drops a consonant: ark- *h₁orǵ-ei would become *h₁órei 'arrive'.
- **Root** (`resolve_root`, how `kloekhorst-root`). The root is the first hyphen segment, or the second after a reduplication syllable (*mé-molh₂- → m l H₂). It becomes a consonant skeleton:
  - e/o/a, length and accent are dropped (ablaut grade);
  - i/u are y/w;
  - laryngeals are kept with their index, where H matches any and h1/3 matches h₁ or h₃;
  - palatal and plain velars fold together, and a labiovelar is a velar + w;
  - aspiration and voicing are kept;
  - Kloekhorst's K and T, and the lost dorsal glyphs, are wildcards for their class.

  The skeleton must agree with a lexicon root (`kind == "root"`, forms and variants), **and** `gloss_agrees` must hold. That is, an English word must be shared by the root's meaning and Kloekhorst's gloss or the translated TLHdig gloss, or a German word must be shared by the TLHdig gloss and LIV's `meaning_de`. Exactly one root group must pass, or the lemma stays unmapped.
  - Unit test: parš- 'to break' *bʰr̥s- has the same skeleton as the lexicon's *bʰers- 'top, tip, point'. The meaning check rejects it (and Kloekhorst's `?` would reject it anyway).
- **Validation of the root resolver** against the 42 EDHIL entries resolved at the whole-form level (lexemes): the resolver returns the lexeme's root group for 19 entries and abstains on 23. It returns a different root for none.
  - It abstains when the lexicon has no root of that skeleton, or when the root's gloss does not fit, as with *h₂meh₁- 'mow' for ḫamešḫa- 'spring'.

## Coverage

Content tokens of TLHdig (Hittite-language lines; every token belongs to a paragraph unit, so the paragraph-unit and token figures are the same). Overrides are applied as `_table("hit")` applies them.

| | content tokens | mapped | coverage | names as unmapped content | content types | types mapped |
|---|---|---|---|---|---|---|
| (i) old loader, table on disk (the lead's figure) | 185,489 | 67,180 | 36.2% | — | 9,751 | 316 |
| (ii) new loader, table on disk | 135,038 | 57,169 | 42.3% | 36.3% | 5,916 | 181 |
| (iii) new loader, new table | 135,038 | 60,415 | **44.7%** | **38.4%** | 5,916 | **302** |

- (i) → (ii) only changes the denominator. 50,451 tokens drop out: function words and names (22,385 name tokens).
- (ii) → (iii) is the mapping gain: +3,246 tokens, +121 types net. 127 types are newly mapped (3,305 tokens): 57 `kloekhorst-root`, 69 `kloekhorst`, 1 `chain`. 6 old `kloekhorst` lemmas (59 tokens) were dropped:
  - by the gloss rule: arku- 'bitten' (EDHIL arku- 'to chant'), tarkuwant- 'zornig blickend', takš- 'zusammenfügen', tepšu- 'trocken';
  - by Kloekhorst's '?': šalk- 'verrühren', kinā- 'filtern'.

  No lemma mapped in both tables changed its ids.
- Of the 200 most frequent unmapped content types of (ii), **11 are now mapped**: kiš- 'werden', mēmal 'Grütze', arr- 'waschen', walḫ- 'schlagen', wekk- 'wünschen', tāye- 'stehlen', ḫatt- 'stechen', ānš- 'abwischen', app=išk- 'fassen', ḫamešḫa- 'Frühling', naḫḫ- 'fürchten'.
- Top unmapped share after: top 50 17.6%, top 200 29.3%, top 500 38.2% of content tokens (before, on the same denominator: 18.0 / 30.4 / 39.7%).

Rows by `how`:

| | rows | chain | lexicon | pseudo | root | kloekhorst | kloekhorst-root | erratum |
|---|---|---|---|---|---|---|---|---|
| on disk before | 184 | 100 | 29 | 21 | 6 | 28 | — | — |
| regenerated | 311 | 42 | 14 | 10 | 1 | 81 | 57 | 106 |

`erratum` rows are lemmas that `east.json` decides. The table on disk predated those overrides; consumers already applied them when reading it. The regenerated table writes them in, as `write_mapping_tables` does after `apply_rec_overrides`.

- Because of this, `tests/test_mapping_resolution.py::test_added_only_override_row_is_used_by_the_checker` no longer finds ≥168 Hittite rows with status 'added'. The assertion now checks its stated intent: every lemma that an override maps is in the resolved population, with its decision.
- The drop in chain, lexicon and pseudo rows has three causes:
  - lemma variants differing only by a selection mark are merged;
  - rows decided by an override now count as `erratum`;
  - names and clitic chains get no rows.

  Adverbs, preverbs and pronouns keep their kaikki rows (anda → *h₁n̥dó, peran → *péro, kui- → *kʷis) even though they are not content words. These rows are evidence for the Tier 2 secure check.
- The standalone driver builds the Hittite `LangMapping` from a `ProtoDB` limited to Hittite descendants. With the old loader it reproduced the on-disk rows apart from the override decisions.

### Why the frequent lemmas stay unmapped

Reasons for the top 200 unmapped content types after the change, by tokens:

| reason | tokens |
|---|---|
| Kloekhorst marks the PIE line doubtful (`?`) | 10,121 |
| no EDHIL headword | 9,792 |
| no candidate headword agrees in gloss | 7,345 |
| PIE line not resolvable (no lexicon root with that skeleton, or meaning disagrees) | 6,150 |
| headword without a PIE line | 3,303 |
| TLHdig gloss not translatable | 2,870 |

Examples of each:

- **Doubtful.** The four most frequent unmapped content words are all marked doubtful by Kloekhorst:
  - parš- 'to break', *bʰr̥s- ?, p. 642;
  - mēma- 'to speak', two alternatives, both ??, p. 573;
  - iya- 'to do, to make', *HH-ie/o- ?, p. 381;
  - ḫūmant- 'all', p. 361.

  By the stated rule they stay unmapped. **The most frequent content lemma, parš- (2,878 tokens), is unmapped on purpose.**
- **No headword.** Mostly cultic and material terms that EDHIL does not treat: palwatalla-, takarmu-, aḫrušḫi-, šaramma-. Also derived stems whose base entry the key does not reach: ḫandae- 'ordnen', ḫuittiye/a- 'ziehen'.
- **No gloss agreement.** Often a different word with the same damaged key, as with ḫuppar- 'Schale' and ḫāppar- 'business'. Sometimes the glosses differ too much, as with ḫatrae- 'mitteilen' and 'to write'. That last case was added by hand to the vocabulary ('report').
- **PIE line not resolvable.** The lexicon lacks the root:
  - ḫalzai- 'call', *h₂lt-;
  - šakk- 'know', *sókh₁-;
  - mēḫur 'time', *méih₂-ur;
  - warp- 'wash', *u̯erp-.

  Or the meaning disagrees: nai- 'turn' and *neiH- 'lead'.

## Precision (self-judged)

**Sample.** 60 lemmas newly mapped relative to (ii), drawn with seed 20261025, stratified by route: 30 `kloekhorst-root`, 29 `kloekhorst`, and the 1 new `chain` lemma. They cover 38 distinct EDHIL entries.

**How each was judged.** I compared each mapping with Kloekhorst's entry: the headword, its gloss and the PIE line, and for unclear cases the discussion around the PIE line, read as text. A mapping counts as correct if the lexicon id is Kloekhorst's etymon. That is either the lexeme he reconstructs, or the root of his reconstruction with the same meaning. A derivative mapped to its base verb's lexeme (marnu- → *mér-) also counts as correct.

**Result.** 60 / 60 correct. Wilson 95% interval: 0.940–1.000.

- This is my own judgment of my own rules.
- The sample repeats etymons: papparš- ×3, walḫ- ×4, arr- ×3. Independence is therefore closer to 38 entries than to 60. For 38/38, the Wilson interval is 0.908–1.000.

| # | lemma (TLHdig) | → lexicon id | EDHIL headword, page | verdict |
|---|---|---|---|---|
| 1 | par=ai-@blasen | pie-root-preh1-blow_on | parai-i / pari-, p. 631 | c |
| 2 | papparš=@(be)spritzen | pie-root-pers-sprinkle | papparš-i, p. 627 | c |
| 3 | ḫark=iya-@umkommen | pie-root-h3erg-perish | ḫark-zi, p. 306 | c |
| 4 | mall=iye/a-@mahlen | pie-root-melh2-grind | malla-i / mall-, p. 547 | c |
| 5 | link-/lik-@schwören | pie-root-h1lengjh-assert_on_oath | li(n)k-zi, p. 526 | c |
| 6 | šuppar=iya-@schlafen | pie-root-swep-sleep | šuppariye/a-zi, p. 788 | c |
| 7 | ḫan=@schöpfen | pie-root-h2en-draw | ḫān-i / ḫan-, p. 281 | c |
| 8 | warš=iye/a-@(ab)ernten | pie-root-wers-wipe | warš-i, p. 968 | c |
| 9 | t=aye/a-@stehlen | pie-root-teh2-steal | tāye/a-zi, p. 809 | c |
| 10 | arr=iye/a-@waschen | pie-root-h1erH-wash | ārr-i / arr-, p. 197 | c |
| 11 | papparš=išk-@(be)spritzen | pie-root-pers-sprinkle | papparš-i, p. 627 | c |
| 12 | paparš=@(be)spritzen | pie-root-pers-sprinkle | papparš-i, p. 627 | c |
| 13 | išḫuw=ai-@schütten | pie-root-sh2ew-pour | išḫuwai-i / išḫui-, p. 396 | c |
| 14 | išpant=@libieren | pie-root-spend-libate | išpānt-i / išpant-, p. 404 | c |
| 15 | arr=a-@waschen | pie-root-h1erH-wash | ārr-i / arr-, p. 197 | c |
| 16 | nekum=ant-@nackt | pie-root-negw-bare | nekumant-, p. 602 | c |
| 17 | ḫan=išk-@schöpfen | pie-root-h2en-draw | ḫān-i / ḫan-, p. 281 | c |
| 18 | ḫuš=u-@lebendig | pie-root-h2wes-dwell | ḫuiš-zi / ḫuš-, p. 353 | c |
| 19 | ḫan=iye/a-@schöpfen | pie-root-h2en-draw | ḫān-i / ḫan-, p. 281 | c |
| 20 | nekumm=ant-@nackt | pie-root-negw-bare | nekumant-, p. 602 | c |
| 21 | arr=išk-@waschen | pie-root-h1erH-wash | ārr-i / arr-, p. 197 | c |
| 22 | tekušš=iye/a-@zeigen | pie-root-dekws-show | tekkuššiye/a-zi, p. 864 | c |
| 23 | ark=@aufteilen | pie-root-h1erk-cut_up | ārk-i / ark-, p. 204 (cognate Lat. ercīscō) | c |
| 24 | zamank=ur-@Bart | pie-root-smekj-beard | zama(n)kur, p. 1029 | c |
| 25 | ie-@gehen | pie-root-h1ey-go | iye/a-tta(ri), p. 380 | c |
| 26 | warš=@(ab)ernten | pie-root-wers-wipe | warš-i, p. 968 | c |
| 27 | ḫuišw=a(e)-@leben | pie-root-h2wes-dwell | ḫuiš-zi / ḫuš-, p. 353 | c |
| 28 | link=išk-@schwören | pie-root-h1lengjh-assert_on_oath | li(n)k-zi, p. 526 | c |
| 29 | mall=išk-@mahlen | pie-root-melh2-grind | malla-i / mall-, p. 547 | c |
| 30 | tiy=a-@treten | pie-root-steh2-stand | tiye/a-zi, p. 879 | c |
| 31 | ḫatt=a-@stechen | pie-lex-h2etox | ḫatt-a(ri), p. 330 | c |
| 32 | arš=@fließen | pie-lex-h1ersti | ārš-zi / arš-, p. 208 | c |
| 33 | anš=iye/a-@abwischen | pie-lex-h2omh1sey | ānš-i, p. 182 | c |
| 34 | unuw=ā(e)-@schmücken | pie-lex-h3unewti | unu-zi, p. 918 | c |
| 35 | nipi=š-@Himmel | pie-lex-nebhos | nēpiš-, p. 603 | c |
| 36 | ânš=@abwischen | pie-lex-h2omh1sey | ānš-i, p. 182 | c |
| 37 | taru=@tanzen | pie-lex-terkwti | tar(k)u-zi, p. 842 | c |
| 38 | ḫatt=anna-@stechen | pie-lex-h2etox | ḫatt-a(ri), p. 330 | c |
| 39 | ištamman=a-@Ohr | pie-lex-steh3mn | ištāman- / ištamin-, p. 411 (the lexicon lists the Hittite word as a reflex) | c |
| 40 | u=nu-@schmücken | pie-lex-h3unewti | unu-zi, p. 918 | c |
| 41 | karš=iye/a-@abschneiden | pie-lex-kerst, pie-lex-kerst-2 | karš(iye/a)-zi, p. 454 | c |
| 42 | išparr=iešk-@hin-/ausbreiten | pie-lex-sporey | išpār-i / išpar-, p. 406 | c |
| 43 | arš=nu-@fließen lassen | pie-lex-h1ersti | ārš-zi / arš-, p. 208 | c |
| 44 | ḫat=eš-@trocken werden | pie-lex-h2odey | ḫāt-i / ḫat-, p. 328 | c |
| 45 | ḫant=i-@zur Stirn gehörig | pie-root-h2ent-face | ḫant-, p. 287 | c |
| 46 | ḫatuk=i-@furchtbar | pie-lex-h2tewgti | ḫatuk-zi, p. 336 | c |
| 47 | anš=išk-@abwischen | pie-lex-h2omh1sey | ānš-i, p. 182 | c |
| 48 | luk=eš-@allmählich hell werden | pie-lex-lewkt | lukk-tta, p. 530 | c |
| 49 | išḫ=ar@Blut | pie-lex-h1esh2r | ēšḫar / išḫan-, p. 256 | c |
| 50 | ḫappin=aḫḫ-@reich werden | pie-lex-h3epeno | ḫappina-, p. 296 | c |
| 51 | uiten=ant-@(ERG) Wasser | pie-lex-wodr | wātar / witēn-, p. 987 | c |
| 52 | walaḫḫ=išk-@schlagen | pie-lex-welh3ti | walḫ-zi, p. 945 | c |
| 53 | arš=iya-@fließen | pie-lex-h1ersti | ārš-zi / arš-, p. 208 | c |
| 54 | ḫat-@vertrocknen | pie-lex-h2odey | ḫāt-i / ḫat-, p. 328 | c |
| 55 | išpar-@hin-/ausbreiten | pie-lex-sporey | išpār-i / išpar-, p. 406 | c |
| 56 | walaḫḫ=anna-@schlagen | pie-lex-welh3ti | walḫ-zi, p. 945 | c |
| 57 | walḫ=išk-@schlagen | pie-lex-welh3ti | walḫ-zi, p. 945 | c |
| 58 | tarku=išk-@tanzen | pie-lex-terkwti | tar(k)u-zi, p. 842 | c |
| 59 | karp=iye/a-@heben | pie-lex-kerpt | karp(iye/a)-zi, p. 452 | c |
| 60 | šupp=a-@schlafen | pie-lex-swept (kaikki chain) | šupp-(tt)a(ri), p. 788 | c |

## Doubtful tier (retrieval only)

The low-confidence tier was added on request (2026-10-25). It covers EDHIL entries whose PIE line Kloekhorst marks with `?` or `??`.

**Machinery.** These entries go through the same steps as the main tier: `kloekhorst_hittite(doubtful=True)` and `resolve_entry(doubtful=True)` use the same headword choice, the same gloss agreement, and the same form and root resolvers.

- When Kloekhorst gives alternatives joined by "or" (stored by `kloekhorst_entries` as `pie_alts`), every alternative must resolve, and all to one root group. Otherwise the entry is skipped (`alternatives_disagree` / `pie_unresolved`).
- Only content lemmas that the main table leaves unmapped, and that no override decides, are considered.

**Output.** The rows go to `data/research/formulas/mapping/hit-doubtful.jsonl`, with how `kloekhorst-doubtful`, confidence `low`, and a `note` giving the EDHIL headword, page and PIE form. They are **not** in `hit.jsonl`.

- `pie/mapping.py` `table_corpora` now skips files ending in `-doubtful` (`RETRIEVAL_ONLY_SUFFIX`). Without that, the resolved population, the audits and the Tier 2 secure check would have read the file, because they glob `mapping/*.jsonl`.
- `hm.read_union_table(root, doubtful=True)` returns `hit.jsonl` with the errata applied, plus the doubtful rows for lemmas that are still unmapped and undecided. A Stage C-S builder can opt in through it. No consumer is wired to it.

**Result: 1 row.** wep- 'weben' → `pie-lex-webhti` (*webʰ-), EDHIL s.v. wēp-zi, p. 1001, PIE *(h₁)u̯ébʰ-ti ?.

- Coverage of content tokens with the tier: 44.74% (60,417 tokens, 303 types); without it: 44.74% (60,415 tokens, 302 types).
- **Self-judged sample: all 1 row (fewer than the 30 asked for exist): correct**. It is the etymology Kloekhorst proposes, doubt included.
- The first build of the tier had 4 rows. Three of them were kīnu- / kenu- 'öffnen' → *ǵeyH- 'burst open'. That is **wrong**: Kloekhorst proposes *ǵʰih₁-neu- (OHG ginēn 'to yawn', Lat. hiscō, p. 477), and the lost-glyph dorsal had been read without its aspiration. The fix: a lost-glyph dorsal followed by h is now an aspirate (`K*h`, which agrees only with gʰ / ǵʰ). The lexicon has no *ǵʰeiH- 'gape', so the lemma stays unmapped. The main table was unchanged by this fix.

**Why so few.** Most doubtful lines fail the same meaning check as the main tier. Kloekhorst's proposals often join words of different meaning:

- mēma- 'speak' with *h₁em- 'take', p. 573;
- punušš- 'ask' with *pneuH- 'regain consciousness', p. 681;
- ḫurtai- 'curse' with *h₂wert- 'swear', p. 372.

Others have no lexicon root: iya- *HH-ie/o-, ḫūmant- *h₂u-ient-, ḫeu- 'rain' *h₂eih₃-(e)u-. parš- 'break' *bʰr̥s- meets only *bʰers- 'top'.

## Known weaknesses

- **Lexicon conflation.** kuer- 'to cut' (p. 486; Kloekhorst *kʷer- 'cut') goes to `pie-root-kwer-do`. That is the lexicon's single *kʷer- root, which glosses 'to do, make, build' and 'to carve, cut to shape'; LIV separates 'cut' from 'make'. It is not in the sample, but a strict reviewer would call it wrong.
- **Lost glyphs.** A run of control characters in a PIE line is read as a dorsal of unknown series. For iškiye/a- 'to smear' (p. 401) the line reads *s + lost glyphs + (h)-ié/ó-, and the mapping is *seǵ- 'anoint' (LIV 'salben'). This depends on that reading.
- **German–English vocabulary.** Headword choice depends on `HIT_DE_EN` / `DE_EN_MORE`. A missing translation only costs coverage (2,870 tokens in the top 200 have an untranslated gloss). A generic shared word (make, do, go, turn) can still let a wrong headword through when the skeleton also agrees. kiš- 'werden' → *ǵeis- 'turn' passed on 'turn out to be', and checking p. 480 shows it is indeed Kloekhorst's etymology (OHG kēran 'to turn').
- **Conservative abstention.** Correct etymologies with a meaning shift are rejected at the root level: nai- 'to turn' and *neiH- 'lead'; ḫuek- 'to slaughter' and *h₂weg- 'stab'. ḫuek-/ḫuk- is also one TLHdig lemma for two EDHIL homonyms ('to conjure', doubtful; 'to slaughter'), so it stays unmapped.
- **Whole-form route without a meaning check.** A single lexeme matched on a whole form of 5 or more letters is accepted without a meaning check, as in the old route. ištāman- 'ear' → *stéh₃mn̥ 'mouth' is accepted because the lexicon lists the Hittite word under that entry. A wrong single-lexeme homograph with no meaning would not be caught.
- **Headword parsing.** About 1,575 content types have candidate headwords but no gloss agreement. Some are true misses: a different English wording, or a TLHdig gloss given as a category such as '(Brot oder Gebäck)'.
- **Determinatives.** A determinative written with a lost glyph, such as `(NA₄)aku-`, is not stripped, so that headword never matches.
- **Short keys.** Keys of 1–2 letters (wēḫ- → e, iye/a- → ie/ia) reach the candidate index. Gloss agreement is the only filter on them.
- **Consumers.** Rebuilding 8c Stage B or C-S with the new loader changes the Hittite content-word sets: names and clitic chains drop out, and marked lemma variants merge. The builders were not touched. `load_hittite` and `_hit_lines` keep the same token order, because both use `hit_lemma`.
- **Stale counts in another report.** `mapping-precision-east.md` gives east.json as 450 rows, 191 of them hit. After the 72 duplicate rows were removed it has 378 rows, 119 of them hit.


## Entry-boundary audit (2026-10-25)

This supersedes the earlier sample for **PIE-line ownership**, not the separate
lexicon-semantic limitations above. All 138 automatic main-table rows and all
8 doubtful rows were checked (146 rows, 79 distinct cited headword/page pairs).
Result: **146 ok; 0 wrong (misattributed); 0 changed-by-fix table rows**.
The reported parser contamination is real, but none of those contaminated entries
survived into these current tables. Rebuilding both tables produces byte-identical
files. No override decisions were added or changed.

### Cause and repair

The old parser ended the current entry only after accepting an indexable next
headword. Enclitics, cross-references, unsupported stems, and entries with unquoted
descriptions therefore failed to end it. Boundary detection now runs before those
eligibility checks, recognizing header syntax even for rejected entries. It excludes
page-top attestation continuations with manuscript/citation parentheses. Physical
LF lines are preserved: PDF font control codes, including CR, VT and FS, must not
be treated as line breaks or create spurious headwords. A labelled but unsupported
PIE line also closes the pending reconstruction slot; it cannot fall through to a
later line. Discussion-only reconstructions remain excluded.

Invented fixtures cover rejected enclitics, unquoted descriptions, cross-references,
syllabic transliterations, page continuations, control glyphs, discussion-only forms,
and labelled PIE lines. Existing root/gloss/doubt tests remain in force.

Confirmed contamination examples (entry page → actual owner of borrowed form):

- šāwītra-/šāwātar-, p. 740 → =šše, p. 741, *-soi.
- tušk(iye/a)-zi, p. 901 → MUNUSduttariyata/i-, p. 902,
  *dhuégh₂-tr / *dhugh₂-tér-m / *dhugh₂-tr-ós.
- wāppu-/wāppaw-, p. 958 → =wa(r)=, p. 958, *uerh₁-.

### Coverage and file verification

Before = after: main table 334 rows; 325 content lemma types;
63,977 / 135,038 content tokens (47.377%). Doubtful table: 8 additional types,
1,705 tokens. Retrieval union: 333 types, 65,682 / 135,038 tokens (48.640%).
These are final on-disk tables including overrides, unlike the builder's
pre-override `final` coverage diagnostic (0.2927).

Every changed table row: **none**. SHA-256 comparison of mapping tables, corpus
JSONL and export files against the pre-work snapshot verifies no artifact changes,
including byte-identical regenerated Hittite tables. No Tier 2/Tier 3/export builder
was run. STATUS.md was not edited.

### Frequent deferred candidates for the lead

Counts are content tokens per TLHdig lemma; no automatic mappings or new reviewed
overrides were introduced. These are the requested candidate families, ranked by
their highest-frequency lemma, not a claim of exhaustive discussion extraction.

| Lemma | Tokens | EDHIL evidence / disposition |
|---|---:|---|
| parku=i-@rein | 136 | pp. 637–639: *prkʷ-(e)i-, *prkʷ-yé/o-. Correction to premise: p. 638 has an explicitly labelled PIE line, not just discussion. Parser deliberately requires initial `*`; grammatical labels remain unsupported. |
| ḫeš(š)-/ḫaš(š)-@öffnen | 125 | pp. 321–322: discussion *h₂es- or *h₂eNs-; no own PIE line; no convincing cognate identification. |
| parku=nu-@reinigen | 119 | Same reviewed candidate family as parkui-; derivative needs separate review. |
| in=an-@Krankheit | 47 | p. 386: discussion *(H)in-on-, *(H)ien-; no own PIE line. Distinguish erman-, which DOES have *h₁érmn / *h₁rméns on p. 248. |
| tarupp=@sammeln | 29 | pp. 850–852: discussion *Treup-, conditional and unresolved; no own PIE line. |
| parku=eš-@rein werden | 24 | Same parkui- family; review derivative and homonymy before mapping. |
| parkunuš=k-@reinigen | 18 | Same parkui- family. |
| tarup=@sammeln | 9 | Same tarupp- family. |
| ḫaš=@öffnen | 5 | Same opening-verb family; distinguish the separate birth verb. |

### Complete row ledger

`ok` means the cited entry owns the reconstruction used by the row, with existing
whole-form/root normalization retained. It is not an independent endorsement of
all lexicon conflations or semantic decisions (notably kuer-). Reviewed doubtful
rows are identified separately: their normalized forms and derivative assignments
are explicit reviewed decisions, not newly inferred by this parser. The evidence
column gives the actual PIE-line printed page and LF line in the supplied text
file (file number = printed page + 8), which can differ from the entry-start page
in a row. Lost font glyphs are shown as `·`. No running book prose is reproduced.

| Table | Lemma | Cited headword | Mapped reconstruction | Own PIE line (page:line) | Verdict |
|---|---|---|---|---|---|
| hit | akk=iške/a-@sterben | ·k-i / akk- | *h1/3ók-ei | 168:10 | ok |
| hit | akku=išk-@trinken | eku-zi / aku- | *h1egwh-ti | 237:5 | ok |
| hit | anš=@abwischen | ·nš-i | *h2ómh1-s-ei | 182:38 | ok |
| hit | anš=iye/a-@abwischen | ·nš-i | *h2ómh1-s-ei | 182:38 | ok |
| hit | anš=išk-@abwischen | ·nš-i | *h2ómh1-s-ei | 182:38 | ok |
| hit | app=išk-@fassen | epp-zi / app- | *h1ép-ti | 243:20 | ok |
| hit | ar=a-@waschen | ·rr-i / arr- | *h1órh1-ei | 197:45 | ok |
| hit | ark=@aufteilen | ·rk-i / ark- | *h1or···-ei | 204:35 | ok |
| hit | arr=a-@waschen | ·rr-i / arr- | *h1órh1-ei | 197:45 | ok |
| hit | arr=iye/a-@waschen | ·rr-i / arr- | *h1órh1-ei | 197:45 | ok |
| hit | arr=išk-@waschen | ·rr-i / arr- | *h1órh1-ei | 197:45 | ok |
| hit | arš=@fließen | ·rš-zi / arš- | *h1ers-ti | 209:20 | ok |
| hit | arš=iya-2@fließen | ·rš-zi / arš- | *h1ers-ti | 209:20 | ok |
| hit | arš=iya-@fließen | ·rš-zi / arš- | *h1ers-ti | 209:20 | ok |
| hit | arš=nu-@fließen lassen | ·rš-zi / arš- | *h1ers-ti | 209:20 | ok |
| hit | erm=an-@Krankheit | erman / armn- | *h1érmn | 248:24 | ok |
| hit | ie-@gehen | ·e/a-tta(ri) | *h1i-·e/o- | 380:36 | ok |
| hit | išk=iye/a-@bestreichen | iški·e/a-zi | *s···(h)-·é/ó- | 402:6 | ok |
| hit | išp=ai-@sich satt essen | išpai-i / išpi- | *sph1-ói-ei | 404:4 | ok |
| hit | išpant=@libieren | išp·nt-i / išpant- | *spónd-ei | 405:34 | ok |
| hit | išpar-@hin-/ ausbreiten | išp·r-i / išpar- | *spór-ei | 406:46 | ok |
| hit | išpar-@hin-/ausbreiten | išp·r-i / išpar- | *spór-ei | 406:46 | ok |
| hit | išpar=anna-@hin-/ausbreiten | išp·r-i / išpar- | *spór-ei | 406:46 | ok |
| hit | išpar=nu-@ausbreiten | išp·r-i / išpar- | *spór-ei | 406:46 | ok |
| hit | išparr=e/a-@hin-/ausbreiten | išp·r-i / išpar- | *spór-ei | 406:46 | ok |
| hit | išparr=iešk-@hin-/ausbreiten | išp·r-i / išpar- | *spór-ei | 406:46 | ok |
| hit | išpart/za-@entkommen | išpart-zi | *sperdh-ti | 410:26 | ok |
| hit | ištam=an-@Ohr | (UZU)išt·man- / ištamin- | *stéh3-mn | 412:40 | ok |
| hit | ištaman=a-@Ohr | (UZU)išt·man- / ištamin- | *stéh3-mn | 412:40 | ok |
| hit | ištamman=a-@Ohr | (UZU)išt·man- / ištamin- | *stéh3-mn | 412:40 | ok |
| hit | išḫ=ar@Blut | ·š·ar / iš·an- | *h1ésh2-r | 258:23 | ok |
| hit | išḫuw=ai-@schütten | iš·u·ai-i / iš·ui- | *sh2u-ói-ei | 397:20 | ok |
| hit | karp=iye/a-@heben | karp(i·e / a)-zi | *(s)kérp-t | 453:17 | ok |
| hit | karš=iye/a-@abschneiden | karš(i·e / a)-zi | *kérs-t | 455:22 | ok |
| hit | kiš=@werden | k·š-a(ri) / kiš- | *···éis-o | 480:10 | ok |
| hit | kiš=ā(e)-@kämmen | kiš-zi | *kés-ti | 481:44 | ok |
| hit | kišš=@kämmen | kiš-zi | *kés-ti | 481:44 | ok |
| hit | kur=išk-@schneiden | kuer-zi / kur- / ku·ar- | *kwér-t | 487:12 | ok |
| hit | lap=@glühen | l·pp-zi / lapp- | *leh2p- | 519:43 | ok |
| hit | link-/lik-@schwören | li(n)k-zi | *h1lén···h-ti | 527:24 | ok |
| hit | link=išk-@schwören | li(n)k-zi | *h1lén···h-ti | 527:24 | ok |
| hit | luk=eš-@allmählich hell werden | lukk-tta | *léuk-t | 531:11 | ok |
| hit | lukk=išk-@anzünden | lukk-tta | *léuk-t | 531:11 | ok |
| hit | mall=iye/a-@mahlen | malla-i / mall- | *mólh2-ei | 547:21 | ok |
| hit | mall=išk-@mahlen | malla-i / mall- | *mólh2-ei | 547:21 | ok |
| hit | mar=nu-@verschwinden lassen | mer-zi / mar- | *mér-t | 577:54 | ok |
| hit | mem=al-@Grütze | m·mall- | *mé-molh2- | 575:27 | ok |
| hit | memm=al-@Grütze | m·mall- | *mé-molh2- | 575:27 | ok |
| hit | mer-/mar-@verschwinden | mer-zi / mar- | *mér-t | 577:54 | ok |
| hit | mer=nu-@verschwinden lassen | mer-zi / mar- | *mér-t | 577:54 | ok |
| hit | merr=ant-@verschwinden | mer-zi / mar- | *mér-t | 577:54 | ok |
| hit | mili=t-@Honig | militt- / malitt- | *mél-it | 580:26 | ok |
| hit | naḫ=@fürchten | n··-i / na··- | *nóh2-ei | 592:13 | ok |
| hit | naḫ=išk-@fürchten | n··-i / na··- | *nóh2-ei | 592:13 | ok |
| hit | naḫḫ=@fürchten | n··-i / na··- | *nóh2-ei | 592:13 | ok |
| hit | nekum=ant-@nackt | nekumant- | *negw-no-nt- | 603:10 | ok |
| hit | nekumm=ant-@nackt | nekumant- | *negw-no-nt- | 603:10 | ok |
| hit | nepiš=ant-@(ERG) Himmel | n·piš- | *nébh-os | 603:43 | ok |
| hit | nipi=š-@Himmel | n·piš- | *nébh-os | 603:43 | ok |
| hit | padd=a-@graben | padda-i / padd- | *bhódhh2-ei | 655:4 | ok |
| hit | paparš=@(be)spritzen | papparš-i | *pórs-ei | 628:4 | ok |
| hit | papparš=@(be)spritzen | papparš-i | *pórs-ei | 628:4 | ok |
| hit | papparš=@(be)spritzen) | papparš-i | *pórs-ei | 628:4 | ok |
| hit | papparš=išk-@(be)spritzen | papparš-i | *pórs-ei | 628:4 | ok |
| hit | par=ai-@blasen | parai-i / pari- | *prh1-(o)i- | 631:33 | ok |
| hit | paḫḫuen=ant-@(ERG) Feuer | pa··ur / pa··uen- | *péh2-ur | 613:30 | ok |
| hit | t=aye/a-@stehlen | t··e/a-zi | *teh2-·e/o- | 809:42 | ok |
| hit | tar=u-@Holz | (GIŠ)t·ru- | *dóru- | 849:45 | ok |
| hit | tarku=@tanzen | tar(k)u-zi | *térkw-ti | 842:35 | ok |
| hit | tarku=išk-@tanzen | tar(k)u-zi | *térkw-ti | 842:35 | ok |
| hit | tarr=u-@stark | tar·u-zi | *terh2-u-ti | 836:49 | ok |
| hit | taru=@tanzen | tar(k)u-zi | *térkw-ti | 842:35 | ok |
| hit | taru=išk-@tanzen | tar(k)u-zi | *térkw-ti | 842:35 | ok |
| hit | taruḫḫ=išk-@mächtig sein | tar·u-zi | *terh2-u-ti | 836:49 | ok |
| hit | tarš=@trocknen | tarš- | *ters- | 848:16 | ok |
| hit | tekkušš=iye/a-@zeigen | tekkušši·e/a-zi | *dekws-·e/o- | 865:10 | ok |
| hit | tekušš=iye/a-@zeigen | tekkušši·e/a-zi | *dekws-·e/o- | 865:10 | ok |
| hit | tepaw=aḫḫ-@gering machen | t·pu- / t·pa·- | *dhébh-u- | 869:37 | ok |
| hit | tiy=a-@treten | ti·e/a-zi | *(s)th2-·e/o- | 880:16 | ok |
| hit | tiy=atar@Setzen | dai-i / ti- | *dhh1-ói-ei | 807:27 | ok |
| hit | u=nu-@schmücken | unu-zi | *h3u-néu-ti | 918:39 | ok |
| hit | uddan=ant-@(ERG) Wort | uttar / uddan- | *uéth2-r | 932:35 | ok |
| hit | uiten=ant-@(ERG) Wasser | ··tar / ·it·n- | *uód-r | 987:43 | ok |
| hit | unuw=a-@schmücken | unu-zi | *h3u-néu-ti | 918:39 | ok |
| hit | unuw=ā(e)-@schmücken | unu-zi | *h3u-néu-ti | 918:39 | ok |
| hit | walaḫḫ=anna-@schlagen | ·al·-zi | *uélh3-ti | 946:18 | ok |
| hit | walaḫḫ=išk-@schlagen | ·al·-zi | *uélh3-ti | 946:18 | ok |
| hit | walḫ=@schlagen | ·al·-zi | *uélh3-ti | 946:18 | ok |
| hit | walḫ=išk-@schlagen | ·al·-zi | *uélh3-ti | 946:18 | ok |
| hit | warr=ā(e)-@zu Hilfe kommen | ·r-i / ar- | *h1ór-ei | 197:8 | ok |
| hit | warš=@(ab)ernten | ·arš-i | *uórs-ei | 968:47 | ok |
| hit | warš=@(ab)ernten) | ·arš-i | *uórs-ei | 968:47 | ok |
| hit | warš=iya-@erfrischen | ·arš-tta(ri) / ·arši·e/a-zi | *uérs-to | 969:36 | ok |
| hit | warš=iye/a-@(ab)ernten | ·arš-i | *uórs-ei | 968:47 | ok |
| hit | warš=iye/a-@erfrischen | ·arš-tta(ri) / ·arši·e/a-zi | *uérs-to | 969:36 | ok |
| hit | wed=ā(e)-@(her)bringen | ·edae-zi | *uedh-o-·e/o- | 1009:33 | ok |
| hit | wek=@wünschen | ·ekk-zi | *ué·-ti | 996:24 | ok |
| hit | wek=išk-@wünschen | ·ekk-zi | *ué·-ti | 996:24 | ok |
| hit | wekk=@wünschen | ·ekk-zi | *ué·-ti | 996:24 | ok |
| hit | zamak=ur-@Bart | zama(n)kur | *smó·-ur | 1029:21 | ok |
| hit | zamank=ur-@Bart | zama(n)kur | *smó·-ur | 1029:21 | ok |
| hit | ânš=@abwischen | ·nš-i | *h2ómh1-s-ei | 182:38 | ok |
| hit | šar=u-@Beute | š·ru- | *sór-u- | 738:42 | ok |
| hit | šaš=nu-@zum Schlafen veranlassen | šeš-zi / šaš- | *sés-ti | 747:4 | ok |
| hit | šuppar=iya-@schlafen | šuppari·e/a-zi | *sup-r-·e/o- | 788:41 | ok |
| hit | šuppar=iye/a-@schlafen | šuppari·e/a-zi | *sup-r-·e/o- | 788:41 | ok |
| hit | šuu-@voll | š·u- / š··a·- | *souh1/3-(o)u- | 794:24 | ok |
| hit | ḫamešḫ=a-@Frühling | ·ameš·a- | *h2meh1-sh2o- | 280:21 | ok |
| hit | ḫammešḫ=a-@Frühling | ·ameš·a- | *h2meh1-sh2o- | 280:21 | ok |
| hit | ḫan=@schöpfen | ··n-i / ·an- | *h2ón-ei | 281:46 | ok |
| hit | ḫan=iye/a-@schöpfen | ··n-i / ·an- | *h2ón-ei | 281:46 | ok |
| hit | ḫan=išk-@schöpfen | ··n-i / ·an- | *h2ón-ei | 281:46 | ok |
| hit | ḫant-@Stirn | ·ant- | *h2ent- | 288:33 | ok |
| hit | ḫant=i-@zur Stirn gehörig | ·ant- | *h2ent- | 288:33 | ok |
| hit | ḫappin=a-@reich | ·appina- | *h3ep-en-o- | 296:41 | ok |
| hit | ḫappin=aḫḫ-@reich werden | ·appina- | *h3ep-en-o- | 296:41 | ok |
| hit | ḫark=iya-@umkommen | ·ark-zi | *h3erg-ti | 306:34 | ok |
| hit | ḫaršar/ḫarš(ša)n-@Kopf | ·aršar / ·aršn- | *h3ers-r | 314:22 | ok |
| hit | ḫat-@vertrocknen | ··t-i / ·at- | *h2ód-ei | 329:12 | ok |
| hit | ḫat=@stechen | ·att-a(ri) / ·azzi·e/a-zi | *h2ét-o | 331:9 | ok |
| hit | ḫat=@vertrocknen | ··t-i / ·at- | *h2ód-ei | 329:12 | ok |
| hit | ḫat=eš-@trocken werden | ··t-i / ·at- | *h2ód-ei | 329:12 | ok |
| hit | ḫat=nu-@zum Vertrocknen bringen | ··t-i / ·at- | *h2ód-ei | 329:12 | ok |
| hit | ḫatt=a-@stechen | ·att-a(ri) / ·azzi·e/a-zi | *h2ét-o | 331:9 | ok |
| hit | ḫatt=anna-@stechen | ·att-a(ri) / ·azzi·e/a-zi | *h2ét-o | 331:9 | ok |
| hit | ḫatuk=@schrecklich sein | ·atuk-zi | *h2téug-ti | 336:36 | ok |
| hit | ḫatuk=i-@furchtbar | ·atuk-zi | *h2téug-ti | 336:36 | ok |
| hit | ḫaš(š)-@Asche | ··šš- | *h2éh1s-s | 318:24 | ok |
| hit | ḫaš=@zeugen | ··š-i / ·ašš- | *h2óms-ei | 319:29 | ok |
| hit | ḫašte=r-@Stern | ·ašter(a)- | *h2ster- | 326:17 | ok |
| hit | ḫašš=@zeugen | ··š-i / ·ašš- | *h2óms-ei | 319:29 | ok |
| hit | ḫuišw=a(e)-@leben | ·uiš-zi / ·uš- | *h2·es- | 354:37 | ok |
| hit | ḫuišw=atar@Leben | ·uiš-zi / ·uš- | *h2·es- | 354:37 | ok |
| hit | ḫuišš=u-@lebendig | ·uiš-zi / ·uš- | *h2·es- | 354:37 | ok |
| hit | ḫurk=i-@Rad | GIŠ·urki- | *h2urg-i- | 364:20 | ok |
| hit | ḫuš=nu-@leben lassen | ·uiš-zi / ·uš- | *h2·es- | 354:37 | ok |
| hit | ḫuš=u-@lebendig | ·uiš-zi / ·uš- | *h2·es- | 354:37 | ok |
| hit | ḫušw=atar@Leben | ·uiš-zi / ·uš- | *h2·es- | 354:37 | ok |
| hit-doubtful (reviewed) | arun=a-@Meer | aruna- | *h₃r-éu-no- | 212:34 | ok |
| hit-doubtful (reviewed) | palw=ā(e)-@anstimmen | palwae-zi | *bʰl̥h₁-u̯o-yé/ó- | 623:16 | ok |
| hit-doubtful (reviewed) | palwatall=a-@Anstimmer | palwae-zi | *bʰl̥h₁-u̯o-yé/ó- | 623:16 | ok |
| hit-doubtful (reviewed) | palwattall=a-@Anstimmer | palwae-zi | *bʰl̥h₁-u̯o-yé/ó- | 623:16 | ok |
| hit-doubtful (reviewed) | punušš=@fragen | punušš-zi | *pneuH-s- | 682:12 | ok |
| hit-doubtful | wep=@weben | ·ep-zi | *(h1)uébh-ti | 1001:39 | ok |
| hit-doubtful (reviewed) | šuḫḫ=a-@schütten | šuḫḫa-i / šuḫḫ- | *suh₂-énti | 773:42 | ok |
| hit-doubtful (reviewed) | ḫurt=ai-@Fluch | ḫuwart-i / ḫurt- | *h₂u̯órt-ei / *h₂urt-énti | 373:12 | ok |

Validation: `uv run pytest -q tests/test_hittite_mapping.py`: **21 passed**.
Final `uv run pytest -q`: **2,573 passed** (388.53 s). Commands used
`UV_CACHE_DIR=/tmp/uv-pie-cache` because the default cache is outside the writable
sandbox. Final artifact checksums remain unchanged after the suite.
