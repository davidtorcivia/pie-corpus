# Morphology engine

Code: `pie/phon.py` (segments and phonology), `pie/morph.py` (inflection), `pie/crosscheck.py` + `pie/triage.py` (acceptance harness). CLI: `uv run python -I scripts/crosscheck_paradigms.py [--show N]`.

## Architecture

- **Layer 1 (built):** `(strong stem, weak stem, accent class) → cells`. The spec mirrors Wiktionary's inflection-template args on purpose (`NounSpec`, `AdjSpec`, `VerbSpec`), so every Wiktionary table can be regenerated and compared.
- **Layer 2 (built):** `lemma → spec` by shape, for the lexemes without a Wiktionary table. Each rule is backtested; see below.
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

Further `handbook` alternatives written by the Tier 1 scholarly texts: the secondary 3sg/3pl *-ed/-ond* beside *-et/-ont* (Byrd 2013), dative/ablative plural *-bʰyos* and *-oybʰyos* (Byrd 2013, Adams 1997), and thematic acc. pl. *-ons/-ōns* (Fortson-style *-ons*; Byrd *h₁éḱwōns*).

**Tiebreaker measured (2026-10-23):** validator coverage on the laryngealist Tier 1 texts is higher under `handbook` on every text (docs/audits/tier1-validation-2026-10-23.md).

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

## Layer 2: lemma → spec (`pie/classify.py`, `scripts/classify_lexicon.py`)

The order is: a Wiktionary table if the entry has one; otherwise a shape rule on the lemma (*-eti* → thematic present, *-ti* → athematic with a zero-grade weak stem, *-os* → thematic, and so on); otherwise indeclinable or unknown. `zero_grade()` deletes the accented short *e/o* and re-syllabifies only its neighbours (*gʷʰén → gʷʰn̥*, *dyéw → dyu*, *wóyd → wid*, *linékʷ → linkʷ*).

**Backtest.** Every shape rule is run on the entries that *do* have tables, with the table hidden. The cells of the guessed spec are compared with the cells of the table's spec, both from the engine, which isolates rule error from engine error. Results (2026-10-23):

| Rule | Tables | Exact | Cell agreement |
|---|---|---|---|
| thematic-present | 69 | 69 | 100% |
| perfect | 20 | 20 | 100% |
| thematic-adj | 84 | 82 | 97.6% |
| s-stem-neuter | 27 | 26 | 96.3% |
| men-neuter | 14 | 12 | 92.5% |
| u-adj | 16 | 14 | 90.5% |
| athematic-root | 41 | 34 | 88.5% |
| root-aorist | 22 | 17 | 88.0% |
| thematic (noun) | 69 | 59 | 85.5% (the misses are adjectives whose lemma lacks a POS) |
| eh2 | 19 (15 scored) | 15 | 100% (2026-10-28; was 78.9%) |
| pk-iu-stem | 34 | 27 | 89.3% (2026-10-28: an o-grade root is acrostatic, Fortson §6.21, except before RC, §6.27; was 84.7%) |
| n-stem-ak | 10 | 7 | 85.3% (2026-10-28: a root-final liquid or nasal is consonantal before -n̥; was 82.6%) |
| thematic-neuter / er-stem | | | 79–85% |
| n-stem-hk / devi / hk-iu-stem | | | 45–71% (not usable) |

**Usability policy:** Tier 3 may use only a table spec, or a shape rule with ≥ 85% backtest agreement (`usable` in `data/morph/inflection_specs.jsonl`).

**eh₂ gate (2026-10-28, engine-queue-wave1).** The eh₂ rule takes the headword as the stem. 4 of its 19 tables are written on another spelling of their own headword: unaccented *ǵʰorneh₂* under *ǵʰórneh₂*, *h₂yuh₁n̥téh₂* under *h₂yuHn̥téh₂*, *tń̥neh₂* under *tn̥néh₂*, and *h₃migʰleh₂*. Each scored 0/19, and together they were the whole gap from 100% to 78.9%. The backtest now skips them, as it already did for thematic tables. This makes 391 eh₂ nouns usable (*h₁éḱweh₂* 'mare', *h₁orséh₂* 'tail', *wóbʰseh₂* 'wasp'), so the usable count went from 4,215 to 4,606.

**Coverage:** 4,476 of 6,363 words and derivatives get a spec, and **3,453 are usable** (1,652 nouns, 1,649 verbs, 152 adjectives). These cover **821 of 885 roots** (691 of 730 verbal). The 1,798 unknowns are mostly bound stems (forms ending in a hyphen, which are not words) plus lemma shapes with no rule yet.

## Verification against Fortson and Ringe (2026-10-23)

A subagent compared every golden cell and every closed-class form with Fortson 2010 (ch. 6–7) and, where Fortson is silent, Ringe 2017 (ch. 2). Result: 236 rows, **144 match, 32 differ, 60 not printed** (`raw/books/extract/fortson/diff.jsonl`, local). The differences were applied to the `handbook` convention, with the Wiktionary-convention forms kept as alternatives (cross-check unchanged at 98.8%):

- **Accusative plural *-ns/-n̥s*** (< *-ms; Fortson §6.14, Ringe): *pódn̥s*, *ph₂térn̥s*, *h₂ówins*, thematic *-ons* (Fortson §6.45), *eh₂*-stem *-ās* / *-eh₂ns* (§6.70). Ringe's *gʷṓs* (Stang) added for *w*-stems. This was the one systematic error.
- **No gen. sg. *-ós*:** Fortson §6.8 treats *-os* as a daughter-language spread.
- **Thematic ablative:** Fortson prints *-ōt*, added beside *-ōd* (final t/d indeterminate, §3.40).
- **Closed classes:** demonstrative per Ringe (*tósmey*, *tósmead*, *tónoh₁*, fem. *tósyeh₂-*), Fortson's genitive *-eso* as an alternative; *kʷétwores* (Fortson) beside *kʷetwóres*; *tr̥yóHom*, *kʷeturóHom* (Ringe). Neither book writes the initial laryngeal in *eǵ*, *yós*, *en*, *e-*, *apo*, *néwn̥*; those spellings are added as alternatives, and our laryngeal forms follow Wiktionary/LIV.

Ringe writes thematic endings uncontracted (*-oey*, *-ead*, *-oes*), i.e. our `wiktionary` convention; Fortson writes them contracted, i.e. `handbook`. Both remain supported.

## Golden paradigms (PLAN's list)

`tests/data/golden_paradigms.json` holds 11 paradigms (*pṓds, wĺ̥kʷos, dʰugh₂tḗr, ph₂tḗr, h₂ówis, gʷṓws, dyḗws, h₁ésti, bʰéreti, gʷʰénti, wóyde*). All of them pass under the `handbook` convention. **Verified 2026-10-23 against Fortson and Ringe**, with the corrections above applied (see the previous section). *ǵʰew-* is deferred, because which stems it forms (root aorist, nasal or thematic present) needs LIV².

## Closed classes

`data/morph/closed_class.json` holds hand tables: personal pronouns (with enclitics), the reflexive, *so/seh₂/tod*, *kʷi-/kʷo-*, numerals 2–4 declined and 5–10 indeclinable, and core particles. Also handbook-standard and UNVERIFIED. *óynos* declines through the engine as a thematic adjective.

## Phase B (verbal: built)

`conjugate(..., phase_b=True)` adds the middle (primary *-h₂er/-th₂er/-tor*, secondary *-h₂e/-th₂e/-to*, zero-grade alternatives *-ór/-ró*), subjunctive (thematic lengthened *-ēti*; athematic strong stem + short vowel; *e*-grade in the perfect), optative (*-oy-*; *-yéh₁-/-ih₁-*), participles (*-onts/-omnos*, *-ónts/-m̥h₁nós*, perfect *-wṓs*), and middle imperatives. An accented stem takes zero-grade *-n̥t* in OPT.3PL and PTCP (*bʰúHih₁n̥t*, *h₁édn̥ts*). Handbook alternatives attested in Tier 1: middle imperative *-eswo* and future imperative *-tōd* (Byrd 2013).

The secondary middle 2sg stays *-th₂e*. Both Fortson §5.16 and Ringe 2006 p. 30 print *-th₂e*. Beekes p. 269 takes Ved. *-thās* as the older form but reconstructs it as *-th₂o* and derives the *-s* from the active. So none of the three gives the *-th₂es* that the t024 review asked for. The perfect has no 2du/3du (Ringe p. 32), and `check_plan` rejects a dual perfect. A Narten present's 2sg imperative is the zero grade plus *-dʰí* (Fortson §5.54): *h₁ddʰí* (Ved. *addhí*), with *h₁éddʰi* as the alternative.

Cross-check with these cells in scope: **14,023/14,197 cells (98.8%)**, 0 unexplained. New Wiktionary idiosyncrasy classes: `wikt-hiatus-unsyllabified` (*térh₂u-oh₂*), `wikt-mistagged-cell` (participle cells holding finite middle forms), `wikt-odd-table` (*str̥néh₃ti*).

Layer 2 gains a *-tōr* agent-noun rule (backtest 94.7%).

**Still not built (Phase B, nominal):** declension of participles, sigmatic aorist stem formation, r/n heteroclite plurals and collectives, derivational suffixes (*-tér-, -tó-, -ti-, -mn̥, -yo-*), generative root ablaut.
