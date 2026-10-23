# Morphology engine

Code: `pie/phon.py` (segments and phonology), `pie/morph.py` (inflection), `pie/crosscheck.py` + `pie/triage.py` (acceptance harness). CLI: `uv run python -I scripts/crosscheck_paradigms.py [--show N]`.

## Architecture

- **Layer 1 (built):** `(strong stem, weak stem, accent class) → cells`. The spec mirrors Wiktionary's inflection-template args on purpose (`NounSpec`, `AdjSpec`, `VerbSpec`), so every Wiktionary table can be regenerated and compared.
- **Layer 2 (next):** `lemma → spec` by shape, for the lexemes without a Wiktionary table. Its coverage ("inflectable entries / words") is what actually gates Tier 3.
- **Not built:** generative root + suffix + ending ablaut. That is derivational morphology, which is Phase B.

Every cell is a **list** of forms, primary first. Forms are produced as segment lists (`phon.Seg`: vowel / resonant ± syllabic / consonant, ± long, ± accent) and rendered to canonical NFC.

## Conventions

| | `wiktionary` | `handbook` (default for the corpus) |
|---|---|---|
| Thematic NOM.PL / DAT.SG / ABL.SG | *-oes / -oey / -ead* (uncontracted) | *-ōs / -ōy / -ōd* |
| GEN.PL | *-oHom* | *-ōm* (with *-oHom* as alternative) |
| DAT/ABL/INS.PL order | *-mos, -bʰos* | *-bʰos, -mos* |
| Athematic GEN.SG (unaccented stem) | *-és* | *-és* ~ *-ós* |
| eh₂-stem ACC.SG, *-eh₂m#* | *-ām* | *-eh₂m* |
| Proterokinetic oblique plural | zero-grade accented suffix (*bʰeh₂ǵʰú-mos*) | weak stem (*bʰeh₂ǵʰéw-mos*) |
| Pinault's law (*CHy → Cy*) | applied | not applied |
| Perfect *R-H* + C laryngeal loss | applied (*tetólth₂e*) | not applied |

With `alternatives=True` (the default), each cell lists the other convention's forms after the primary ones.

**The default is `handbook`. This is my interpretation of the fixed decision, not a reopening of it.** PLAN §1 makes Wiktionary/LIV canonical for **notation** (symbols). I read that as governing symbols, not paradigm reconstructions. The corpus argument for contracted thematics is that the Tier 1 scholarly texts (Byrd, Kortlandt, …) use them, so Tier 3 would otherwise differ from Tier 1 in a way the model would learn. **Empirical tiebreaker:** Phase 3 validator coverage on Tier 1 texts under each convention. Nothing is lost either way, because the alternatives stay in every cell.

## Phonological rules (all in `phon.py`)

| Rule | Example | Status |
|---|---|---|
| Junction syllabification: a stem-final vocalic resonant before a vowel-initial ending becomes consonantal, cascading left | *dyu+és → diwés*, *ḱwn̥+és → ḱunés*, *deh₂nu+és → deh₂n̥wés* | standard |
| Ending-initial resonants are syllabic unless next to a vowel | *ph₂tér+ms → ph₂térm̥s*, *h₂ówi+m → h₂ówim* | standard |
| An accented stem de-accents the ending | *gʷéw+s*, *ped+és* | standard (accent-ablaut classes) |
| *s+s → s* at the junction | *h₁és+si → h₁ési* | standard |
| Szemerényi's law *-VRs# → -V̄R#* (R = r n m l s), then *-ōn# → -ō#* | *ph₂tḗr*, *dʰéǵʰōm*, *ḱwṓ*, but *bʰudʰmḗn* | standard |
| Stang's law *-V(w|y|m)m# → -V̄m#* | *dyḗm*, *gʷṓm*, *h₁ḗm*, *gʷḗm* | standard |
| Boukólos rule (Wiktionary's scope): kʷ → k after w, before w, before unaccented u | *wéwke-*, *linkwós*, *ḱm̥tógu-* | standard rule; scope from Wiktionary |
| *-eh₂m# → -ām#* | *bʰā́m*, eh₂-stem acc. | Wiktionary convention |
| Pinault's law, perfect laryngeal loss | see above | Wiktionary convention only |

Deliberately **not** implemented: cluster assimilations (*wóydth₂e* stays). Every source we compare against writes underlying forms.

## Acceptance: regenerating Wiktionary's tables

The 625 clean tables in `data/lexicon/paradigms.jsonl` come from one independent implementation (Wiktionary's Lua module). The harness builds a spec from each table's args, runs the engine under the `wiktionary` convention with no alternatives, and compares every in-scope cell. Nouns and adjectives are compared exactly. For verbs, Wiktionary puts active and middle forms in one cell, so the check is that the cell's first (active) form is produced and every engine form appears in the cell.

**Result (2026-10-23): 11,136 / 11,255 in-scope cells match (98.9%); 582 / 615 tables are fully exact.**

| Template \| class | Cells | |
|---|---|---|
| noun-mf (thematic) | 1562/1562 | 100% |
| noun-mf hysterokinetic | 399/399 | 100% |
| noun-mf proterokinetic | 665/666 | 99.8% |
| noun-mf acrostatic | 321/323 | 99.4% |
| noun-mf amphikinetic | 862/882 | 97.7% |
| noun-n acrostatic / proterokinetic / amphikinetic / thematic | 571/571 · 441/444 · 96/100 · 444/467 | |
| adj thematic | 1990/2004 | 99.3% |
| adj athematic (all classes) | 482/521 | 92.5% |
| verb impf / pf (aorist) / stat (perfect) | 2735/2738 · 314/318 · 254/260 | |

Out of scope: subjunctive, optative, middle-only verbs, participles, collective and heteroclite plurals, and phrases (Phase B). That is 3,379 cells in 10 tables.

### Triage of every remaining mismatch (`pie/triage.py`)

**0 cells are unexplained.** `tests/test_morph.py::test_crosscheck_agreement_and_no_unexplained` enforces this: agreement must stay ≥ 98.5%, and any mismatch no detector explains fails the build.

| Class | Cells (forms) | What Wiktionary does | Verdict |
|---|---|---|---|
| wikt-laryngeal-dropped | 42 (4) | drops a laryngeal its own stem args contain (*méǵh₂yos* → *méǵyōs*; *lówh₃trom* → *lówtrom*) | Wiktionary idiosyncrasy |
| wikt-final-deaspiration | 26 (17) | delabializes and deaspirates bare word-final stops (*bʰérǵʰ* → *bʰérǵ*, *h₃ókʷ* → *h₃ók*) | idiosyncrasy, not standard |
| wikt-subset | 17 (2) | partial table (*Hroth₂ós* without feminine forms) | extraction or table scope |
| wikt-inconsistent-delabialization | 10 (1) | the same cell has both *-gʷʰu-* and *-gʰu-* | inconsistent |
| wikt-inconsistent-syllabification | 10 (2) | *h₂imn̥+és* → *h₂ym̥nés*, but *poh₂imn̥+és* → *poh₂imnés* | inconsistent; we keep *-imn-* |
| numeral-hand-table | 6 (2) | special numeral tables | our numerals are hand tables |
| wikt-final-laryngeal-lengthening | 4 (4) | bare *tetólh₂* → *tetṓl*, *gʷénh₂* → *gʷḗn* | idiosyncrasy |
| lexical-exception | 4 (1) | *ḱérd-* nom. *ḱḗr* | needs a lexical `nom_sg` override |

**Engine bugs found and fixed through this loop** (each one moved the agreement figure):
- Stang's law never fired after junction syllabification.
- *n*-loss was applied after *ē*.
- Szemerényi's law ran on stems that already end in *-s*.
- Several gaps: the proterokinetic zero-grade oblique, neuter collectives, the *-éy* locative, i-stem plurals, the 1sg secondary *-m̥*, the zero-grade 3pl after accented stems, boukólos.

## Golden paradigms (PLAN's list)

`tests/data/golden_paradigms.json` holds 11 paradigms (*pṓds, wĺ̥kʷos, dʰugh₂tḗr, ph₂tḗr, h₂ówis, gʷṓws, dyḗws, h₁ésti, bʰéreti, gʷʰénti, wóyde*). All of them pass under the `handbook` convention. **Their source is "handbook-standard, UNVERIFIED".** They were written from knowledge of the handbooks, not copied from them, so passing them shows agreement with myself, not with Fortson. They must be checked against Fortson ch. 6–7 and Ringe ch. 2 when the books arrive. *ǵʰew-* is deferred, because which stems it forms (root aorist, nasal or thematic present) needs LIV².

## Closed classes

`data/morph/closed_class.json` holds hand tables: personal pronouns (with enclitics), the reflexive, *so/seh₂/tod*, *kʷi-/kʷo-*, numerals 2–4 declined and 5–10 indeclinable, and core particles. Also handbook-standard and UNVERIFIED. *óynos* declines through the engine as a thematic adjective.

## Phase B (not built)

Middle and mediopassive endings, subjunctive, optative, participles (*-ent-*, *-mh₁no-*, *-wos-*), sigmatic aorist stem formation, r/n heteroclite plurals and collectives, derivational suffixes (*-tér-, -tó-, -ti-, -mn̥, -yo-*), generative root ablaut.
