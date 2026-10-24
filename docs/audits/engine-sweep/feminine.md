# Engine sweep: feminine eh₂- and ih₂-stems

Auditor family: ā-stems (*-eh₂*), devī́- and vr̥kī́-type *-ih₂/-yeh₂-* stems, the other feminine h₂-stems
(*gʷḗn*, *dn̥ǵʰwéh₂s*, *h₂éHsh₂*), and the feminine of adjectives and participles. Engine read: `pie/morph.py`
`_eh2`, `_athematic` (devī branch), `AdjSpec.genders`, `decline_participle`; `pie/phon.py` `stang`,
`contract_eh2m`. Corpus: `corpus/tier3/*.jsonl` (27 files). Scratch: `fem_*` in the session scratchpad.

**Summary.** 12 defects: 5 in the engine, 6 in specs, and 1 (D4) in both. Applying every fix below changes the
primary form of **59 corpus tokens** out of 844 family tokens. The patched engine passes `tests/test_morph.py`, `test_morph_r2_fixes.py`,
`test_realize.py`, `test_validate.py` and `test_backtest.py` (run on a scratch copy of the repo), plus the new test at
the end of this file.

| D# (= rank) | defect | kind | tokens changed |
|---|---|---|---|
| 1 | devī-type acc. sg. *-ih₂m̥* → *-ih₂m* (Stang) | engine | 22 |
| 2 | eh₂ vocative *-eh₂* → *-a* | engine | 17 |
| 3 | *h₃mígʰleh₂* 'mist': table stem unaccented | spec | 7 |
| 4 | gʷḗn 'woman': vocative *gʷénh₂* ≠ Ringe *gʷḗn*; unsourced nom. *gʷénh₂s* | engine + spec | 5 |
| 5 | devī-type acc. pl. *-ih₂n̥s* → *-ih₂ns* | engine | 4 |
| 6 | athematic *-eh₂* stems (*dn̥ǵʰwéh₂s*) skip Stang: acc. *-eh₂m̥*, *-eh₂n̥s* | engine | 3 |
| 7 | *ǵʰórneh₂* 'gut': table stem unaccented | spec | 1 (+1 voc.) |
| 8 | *h₂yuHn̥téh₂* 'youth': table *h₁* vs lemma *H* | spec | 1 |
| 9 | eh₂ instr. sg. and dual lack *-eh₂eh₁*, *-eh₂ih₁* | engine (alternatives only) | 0 |
| 10 | *tn̥néh₂* 'stretch': lemma vs table accent | spec | 0 |
| 11 | *sḗm* 'one' f. *sih₂* (m lost) | spec | 0 |
| 12 | *ḱm̥tógʷus*: two accents in m. weak and both f. stems | spec | 0 (6 m. tokens unaffected) |

Plus one housekeeping item (gender `m` in the ih₂ noun specs, no cell changes) and two items for other auditors.

## 1. Inventory

Usable lexemes (`inflection_specs.jsonl`, `usable: true`), grouped by how the engine declines them:

| sub-type | engine path | lexemes | corpus tokens |
|---|---|---|---|
| ā-stem nouns (*-eh₂*, no weak stem) | `_eh2` | 20 table: bʰardʰéh₂, bʰoréh₂, bʰoydʰéh₂, bʰugéh₂, dʰoHnéh₂, ǵʰórneh₂, gʷriHwéh₂, h₂ékʷeh₂, h₂wĺ̥h₁neh₂, h₂yuHn̥téh₂, h₃mígʰleh₂, ḱleytéh₂, ḱléytreh₂, kʷoynéh₂, lówksneh₂, lóyseh₂, písdeh₂, pĺ̥h₂seh₂, tn̥néh₂, tpḗrsneh₂ | 402 |
| devī́ nouns (*-ih₂ / -yeh₂-*) | `_athematic`, asigmatic nom. | déywih₂, h₃rḗǵnih₂, néptih₂, pótnih₂ | 136 |
| vr̥kī́ noun (*-íh₂s / -ih₂-*) | `_athematic`, `nom_sg` | wl̥kʷíh₂s | 27 |
| other feminine h₂-stems | `_athematic` | gʷḗn (PK *gʷénh₂/gʷnéh₂*), dn̥ǵʰwéh₂s (HK), h₂éHsh₂ (PK, hand spec) | 80 |
| thematic adjectives, f. *-eh₂* | `AdjSpec` 1 arg → `_eh2` | 206 (111 shape, 95 table) | 123 |
| athematic adjectives, f. *-ih₂/-yeh₂-* | `AdjSpec` 4 args, `devi=True` | 30: 19 u-stems (*-éwih₂/-uyéh₂-*), 3 nt-stems, 3 comparatives (*-yesih₂/-isyeh₂-*), méǵh₂ih₂, h₂yuHénih₂, sih₂ (sḗm 'one', D11), plus tísr̥ / kʷétesr̥ (numerals, *-sr-*, out of scope) | 61 |
| participles, f. | `decline_participle` | athematic *-n̥tíh₂/-n̥tyéh₂-*, thematic *-ontih₂/-ontyeh₂-*, middle *-mh₁neh₂* | 15 |

Not usable, so not in the corpus: 391 `shape:eh2` and 47 `shape:devi` nouns. They were not audited lexeme by
lexeme. The engine fixes below apply to them automatically when they become usable.

## 2. ā-stems (`_eh2`)

**Right.** Every handbook cell checked:

- nom. *-eh₂*, asigmatic (Fortson §6.70; Ringe §2.3.4, pp. 49–50; Beekes p. 200; Mallory & Adams Table 4.6).
- acc. sg. *-eh₂m* with consonantal *m*, not *-eh₂m̥*: Stang (Fortson §3.38, §6.70; Ringe *dʰoHnéh₂m (-ām)*).
  *-ām* follows as the alternative.
- acc. pl. *-ās* first, then *-eh₂ns* (Fortson §6.70; Ringe *dʰoHnéh₂ns (-ās)*; Beekes, M&A *-eh₂ns*).
- gen./abl. *-eh₂s* (Ringe), with *-eh₂es* as an alternative (Beekes, L&Y).
- dat. *-eh₂ey*, loc. *-eh₂i* / *-eh₂* (Ringe *-eh₂(i)*).
- nom. pl. *-eh₂es*; obl. pl. *-eh₂bʰ-*, *-eh₂m-*, *-eh₂su*.
- gen. pl. *-eh₂ōm* (contracted, the project's handbook convention), with Ringe's *-eh₂oHom* second.
- The accent stays on the stem syllable it starts on (oxytone *bʰoréh₂*, barytone *h₂ékʷeh₂*), as in Ringe's
  *dʰoHnéh₂* / *h₂wĺ̥h₁neh₂*.
- The feminine of thematic adjectives is built as o → eh₂ with the accent kept (*néwos* → *néweh₂*,
  *h₁rudʰrós* → *h₁rudʰréh₂*), as in Ringe's *pl̥h₁néh₂* (p. 51) and M&A §4.3.

**D2. Vocative (17 tokens: 7 nouns, 10 adjectives).** The engine gives *-eh₂* (= nom.), with the accent moved to
the first syllable (*h₂ékʷeh₂*, *léwkeh₂*). What the books give:
- Fortson §6.70: *-a* with retracted accent (Gk *-a*, Umbr. *-a*, OCS *-o*; from *-ah₂* with the laryngeal lost
  before a pause).
- Ringe §2.3.4–5: *h₂wĺ̥h₁n[a]*, *dʰoHn[á]*, *pl̥h₁n[á]*, with *-a* but no retraction.
- Beekes p. 200: *-h₂e?*, with a question mark.
- Mallory & Adams Table 4.6: *-eh₂*.

Two handbooks against one, so the handbook convention should make *-a* primary, retracted as Fortson has it (and as
the engine already retracts the vocative in every other declension). Ringe's unretracted form comes second, and the
*-eh₂* forms stay as alternatives. Fix: hunk 1 of the diff in §7. Results: *h₂ékʷa*, *bʰóra | bʰorá | bʰóreh₂ |
bʰoréh₂*, *néwa*, *léwka*. Syllabic-laryngeal onsets stay unaccented under the existing `_initial_accent` convention
(*dʰh₁ta | dʰh₁tá*).

**D9. Missing alternatives (no token changes).**
- instr. sg.: Ringe *-eh₂(e)h₁* and M&A *-eh₂eh₁*, but the engine has only *-eh₂h₁*. Add *-eh₂eh₁* as an
  alternative.
- nom.-acc. du.: Beekes §13.2.11 (p. 217) reconstructs *-eh₂-ih₁* for the ā-stems (Ved. *-e*, OCS *-ě*). Ringe
  gives "???" for the feminine dual (p. 51), and Fortson §6.13 has only the generic *-h₁/-h₁e*. Add *-eh₂ih₁* as an
  alternative and keep *-eh₂h₁* primary. The 1 dual token (*tpḗrsneh₂h₁*) is unchanged. Promote it to primary only if
  the project wants to follow Beekes against the silence of the others.
- (Not proposed) M&A gen. *-eh₂os* and Beekes *-h₂os* are not in the cell. They are notation variants of the
  *-eh₂es* already listed.

**Spec checks: all 20 ā-stem nouns.** 16 are clean. Four disagree with their lemma, because the Wiktionary table
stem differs from the headword and only NOM.SG gets the lemma (`realize.Lexicon.cells`):
- **D3** *h₃mígʰleh₂* 'mist, cloud': the table stem *h₃migʰleh₂* has no accent, so 17 of 18 cells are unaccented.
  Corpus: *h₃migʰleh₂i* ×2, *-s*, *-m*, *-es*, *-bʰos* (7 tokens). Root accent as in the lemma (Gk ὀμίχλη).
- **D7** *ǵʰórneh₂* 'gut': the table stem *ǵʰorneh₂* has no accent. Corpus: *ǵʰorneh₂m* ×1.
- **D8** *h₂yuHn̥téh₂* 'youth': the table writes *h₂yuh₁n̥téh₂-*, so the corpus has NOM *h₂yuHn̥téh₂* but LOC
  *h₂yuh₁n̥téh₂i* for the same word. No handbook has this word. Follow the lemma, which matches the masculine
  *h₂yéwHō / h₂yuHn-* (`pie-lex-h2yewHox`).
- **D10** *tn̥néh₂* 'a stretch': the lemma is oxytone and the table stem is *tń̥neh₂*, so NOM.SG = [tn̥néh₂, tń̥neh₂]
  and the oblique cells are root-accented. No handbook has the word, so the books cannot settle it. Proposal: follow
  the lemma, like the other *-néh₂* abstracts in the list (dʰoHnéh₂, kʷoynéh₂). 0 tokens.

Housekeeping: *bʰoydʰéh₂*, *h₃mígʰleh₂*, *ḱleytéh₂*, *pĺ̥h₂seh₂* have no lexicon gender. `Lexicon.gender` gets `f`
from the *-eh₂* ending, but `validate.py:174` records the analysis with `e.get("gender")` = None. Add `"gender": "f"`
when you touch them.

## 3. devī́-type (*-ih₂ / -yeh₂-*)

**Right.**
- Strong *-ih₂* in nom. sg., acc. sg., nom./acc. pl. and du. (Ringe *tn̥h₂éwih₂es*, *-ih₂n̥s*, p. 50); weak *-yéh₂-*
  in gen./abl./dat./instr./loc. sg. and **every** oblique plural (Ringe *tn̥h₂uyéh₂bʰi, -mos, -oHom, -su*). The engine
  matches this split exactly.
- Asigmatic nom. (Fortson §6.71; Beekes p. 204 *-ih₂*; L&Y §2.1.3).
- gen. *-yéh₂s* (Ved. *devyā́s*; Fortson §6.71; Beekes *-ieh₂-s*; Ringe *-yéh₂s*).
- loc. on the weak stem (Ringe *-yéh₂(i)*).
- voc. short *-i* (Ringe *tn̥h₂éwi*, *h₁sónti*, *sémi*), with the convention's initial accent.

Weak stems of all four nouns check out against Vedic: *diwyéh₂-* (devyā́s), *neptyéh₂-* (naptyā́s), *pótn̥yeh₂-*
(pátnyās), *h₃rḗǵn̥yeh₂-* (rā́jñyās).

**D1. Acc. sg. *-ih₂m̥* (22 tokens).** The general athematic rule syllabifies *-ih₂ + m* as *-ih₂m̥*. The books:
- Fortson §17.12: *-ih₂-m*, which Tocharian also continues.
- Beekes §13.2.6 (p. 204): PD ih₂-stem acc. *-ih₂-m*, Ved. *-ī́m*.
- L&Y §2.1.3 (Table 122.3 note): the long vowel of the acc. sg. of *deiw-íh₂* / *h₁ék̑w-eh₂* comes from Stang's law.
- Ringe §2.3.5–6: *tn̥h₂éwih₂m̥*, *h₁sóntih₂m̥*, *sémih₂m̥*.

Three books against one. The project already applies Stang's law to *-eh₂m*, so *-ih₂m* is consistent with that.
Fix: hunk 3 of the diff makes *-ih₂m* primary and keeps Ringe's *-ih₂m̥* second. The closed-class anaphoric *ih₂*
already lists Beekes' *ih₂m* beside Ringe's *íh₂m̥*. Tokens changed: pótnih₂m ×10, h₃rḗǵnih₂m ×4, néptih₂m,
h₁uséwih₂m ×2, pl̥h₁éwih₂m ×2, h₁wr̥Héwih₂m, méǵh₂ih₂m, h₂yuHénih₂m.

**D5. Acc. pl. *-ih₂n̥s* (4 tokens, *pl̥h₁éwih₂n̥s*).** Ringe writes *-ih₂n̥s*. Beekes §15.2.1 (p. 229) writes *ih₂ns*
for the feminine pronoun, and Fortson §6.70 derives *-eh₂ns* by the same Stang step. *-ih₂ns* goes first, Ringe's
form second (hunk 4). Lower confidence than D1: no book gives a devī́ noun acc. pl. outright, apart from Ringe.

**Accent: books disagree, no change.**
- u-stem adjective feminines: the engine follows Wiktionary and Ringe, root/suffix *-éwih₂* / weak *-uyéh₂-*
  (*tn̥h₂éwih₂*). L&Y §3.2 argue for *-ih₂* taking the accent after u-stems, *pl̥th₂wíh₂* (Ved. *pr̥thvī́*,
  *svādvī́*, Gk *Plataiaí*). The engine has nothing to generate that type, and Ringe and Wiktionary agree with each
  other. Keep the current convention and record L&Y as the dissent.
- athematic participle feminines: the engine has zero grade + accented *-íh₂* (*h₁sn̥tíh₂*; Fortson §6.71 *i̯ung-n̥t-ih₂*,
  Ved. *satī́*, *yuñjatī́*). Ringe p. 51 has strong *h₁sóntih₂* (o-grade, root/suffix accent). Keep the engine's. It
  would be worth adding Ringe's form as an alternative cell, but `decline_participle` has no slot for one, so this is
  not proposed here.

**Spec checks: all 30 athematic adjective feminines.** The u-stems all follow Ringe's pattern; the nt-stems and
comparatives are self-consistent.
- **D11** *sḗm* 'one' (`pie-lex-sexm`): `f_strong: "sih₂"`, with no `f_weak`. The *m* is lost, and the weak stem
  falls back to the strong one (gen. *sih₂és*). Fortson §7.16 and Beekes p. 237 have *sm-ih₂* (Gk μία, Arm. *mi*);
  Ringe §2.3.6(i), p. 52 has *sémih₂*, instr. *sm̥yéh₂(e)h₁*. Use *sm̥íh₂ / sm̥yéh₂*. 0 tokens: 'one' goes through
  the closed class.
- **D12** *ḱm̥tógʷus* 'possessing 100 cows': `m_weak ḱm̥tógʷów`, `f_strong ḱm̥tógʷówih₂`, `f_weak ḱm̥tógʷuyéh₂`
  each carry two accents, so all 18 feminine cells are double-accented. This is a bahuvrihi with the accent on the
  first member (L&Y §3.1–3.2 BAP; Ved. *śatá-*). The proposal keeps the single first-member accent. 0 feminine
  tokens; the 6 masculine NOM.SG *ḱm̥tógus* tokens are unchanged.
- *h₁léngʰus*: `m_weak h₁ln̥gʷʰéw` has the labiovelar while the strong stem and both feminine stems have *gʰ*. The
  feminine is consistent, so this goes to the u-stem/masculine auditor.

## 4. vr̥kī́-type (*wl̥kʷíh₂s*)

Right as it stands:
- sigmatic nom. *wl̥kʷíh₂s* (L&Y §2.1.3 *wl̥kʷíhₓs*; Ringe *wl̥kʷíh₂*).
- gen. *wl̥kʷih₂és* (Ved. *vr̥kías*; Beekes p. 201 *-iH-os*).
- nom. pl. *-íh₂es*.
- acc. sg. *wl̥kʷíh₂m̥*: Ved. *vr̥kíyam* is disyllabic, and Beekes p. 201 has *-ieH-m*. Unlike the devī́ type, the
  *m* is not tautosyllabic, so the D1 fix deliberately leaves this type alone: its `nom_sg` is sigmatic, so `nom is
  strong` is false.

No defects found.

## 5. Other feminine h₂-stems

- *dn̥ǵʰwéh₂s* 'tongue' (HK). Ringe §2.3.4 (p. 49) gives the full paradigm, and every weak cell matches
  (*dn̥ǵʰuh₂és*, *-éy*, *-éh₁*, *-bʰí*, *-oHom*, *-su*), as do nom. pl. and voc. *dń̥ǵʰweh₂*.
  **D6:** acc. sg. *dn̥ǵʰwéh₂m̥* and acc. pl. *dn̥ǵʰwéh₂n̥s*, where Ringe has *dn̥ǵʰwéh₂m (-ām)* and *dn̥ǵʰwéh₂ns (-ās)*.
  Cause: `_athematic` calls `phon.stang`, which only knows *-V(w|y|m)m#*, and the hand-written Stang in `_eh2` never
  runs for stems with a weak stem. Fix: hunks 3–4. Any *-eh₂* final non-neuter athematic stem gets *-eh₂m* and
  *-ās, -eh₂ns*; *-eh₂m̥* stays as an alternative. 3 tokens, but the fix covers the whole class, including any future
  HK eh₂ nouns.
  The guard is narrow by design: C+H stems keep *-m̥* (Ringe *gʷénh₂m̥*, hand-checked *h₂éHsh₂m̥*), and so does
  *póntoh₁m̥* (Beekes p. 199: Indo-Iranian *pánthām* scans disyllabic).
- *gʷḗn* 'woman' (PK *gʷénh₂ / gʷnéh₂-*). Weak cells match Ringe p. 48 (*gʷnéh₂s, -ey, -(e)h₁, -bʰi*), and so does
  acc. *gʷénh₂m̥*.
  **D4:** the vocative is *gʷénh₂* (5 tokens); Ringe gives voc. = nom. = *gʷḗn*. NOM.SG also has *gʷénh₂s* as an
  alternative, which comes from the generic sigmatic nominative and has no source (Beekes p. 204 *gʷen-h₂*, Fortson
  §6.70 *gʷen-h₂*: asigmatic). Fix: spec `nom_sg: "gʷḗn"` (override O4) plus hunk 2. An asigmatic h₂-stem with a
  lexical nominative then gets voc. = nom., and the bare stem *gʷénh₂* becomes the alternative nominative.
  Separately, *gʷénh₂h₁* nom. du. (4 tokens) versus Ringe *gʷénh₂h₁e* is the general athematic *-h₁* first
  convention, not a feminine defect.
- *h₂éHsh₂* 'hearth' (44 tokens). The hand-checked override declines it like *gʷénh₂*. None of the five handbooks
  has the word: M&A writes an ā-stem *h₂ehₓseh₂*, according to the override note. It cannot be verified, but it
  parallels Ringe's PK h₂-stem. No change; with hunk 2 its vocative stays *h₂éHsh₂*.

## 6. Proposed spec overrides (`data/lexicon/overrides.jsonl`), ranked

```json
{"id": "pie-lex-h3mighleh2", "gender": "f", "spec": {"strong": "h₃mígʰleh₂"}, "note": "engine sweep (feminine.md D3): Wiktionary's table stem was unaccented, so 17/18 cells had no accent; root accent as in the lemma (Gk ὀμίχλη, Lith. miglà)"}
{"id": "pie-lex-gwexn", "spec": {"nom_sg": "gʷḗn", "gender": "f"}, "note": "engine sweep (feminine.md D4): asigmatic nom. = voc. gʷḗn (Ringe §2.3.4 p. 48); bare *gʷénh₂ (Fortson §6.70, Beekes §13.2.6) as the alternative, no sigmatic *gʷénh₂s; needs hunk 2 of the morph.py diff"}
{"id": "pie-lex-gjhorneh2", "spec": {"strong": "ǵʰórneh₂"}, "note": "engine sweep (feminine.md D7): table stem unaccented; accent as in the lemma"}
{"id": "pie-lex-h2yuHnteh2", "spec": {"strong": "h₂yuHn̥téh₂"}, "note": "engine sweep (feminine.md D8): table h₁ vs lemma H split nom. h₂yuHn̥téh₂ and loc. h₂yuh₁n̥téh₂i; follow the lemma and the masculine h₂yéwHō/h₂yuHn-"}
{"id": "pie-lex-tnneh2", "spec": {"strong": "tn̥néh₂"}, "note": "engine sweep (feminine.md D10): lemma oxytone, table root-accented; no handbook has the word; follow the lemma like the other -néh₂ abstracts"}
{"id": "pie-lex-sexm", "spec": {"f_strong": "sm̥íh₂", "f_weak": "sm̥yéh₂"}, "note": "engine sweep (feminine.md D11): 'one' f. was sih₂ with no weak stem; Fortson §7.16 and Beekes p. 237 *sm-ih₂ (Gk μία, Arm. mi), Ringe §2.3.6(i) weak sm̥yéh₂-"}
{"id": "pie-lex-kjmtogwus", "spec": {"m_weak": "ḱm̥tógʷow", "f_strong": "ḱm̥tógʷowih₂", "f_weak": "ḱm̥tógʷuyeh₂"}, "note": "engine sweep (feminine.md D12): the table had two accents per form; bahuvrihi keeps the first member's accent (L&Y §3.1-3.2, BAP)"}
```

Housekeeping (no cell changes; fixes `validate.py`'s analysis gender):

```json
{"id": "pie-lex-deywih2", "spec": {"gender": "f"}, "note": "engine sweep (feminine.md): ih₂ nouns had spec gender m"}
{"id": "pie-lex-h3rexgjnih2", "gender": "f", "spec": {"gender": "f"}, "note": "engine sweep (feminine.md)"}
{"id": "pie-lex-neptih2", "gender": "f", "spec": {"gender": "f"}, "note": "engine sweep (feminine.md)"}
{"id": "pie-lex-potnih2", "spec": {"gender": "f"}, "note": "engine sweep (feminine.md)"}
{"id": "pie-lex-wlkwih2s", "spec": {"gender": "f"}, "note": "engine sweep (feminine.md)"}
```

The ā-stems with no lexicon gender (bʰoydʰéh₂, ḱleytéh₂, pĺ̥h₂seh₂) can take `"gender": "f"` the same way.

Overrides merge into the spec in `scripts/classify_lexicon.py` (`{**spec, **spec_override}`), so
`inflection_specs.jsonl` has to be regenerated after these are added.

## 7. Proposed engine change (`pie/morph.py`)

The four hunks are independent of other families. Hunk 1 touches only `_eh2`'s handbook branch. Hunks 2–4 fire
only for non-neuter athematic stems ending in *-eh₂*, an asigmatic devī́ *-ih₂*, or C+*h₂* with a lexical `nom_sg`.
Every replaced form stays as an alternative.

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
@@ -160,8 +160,17 @@
                          render(stem + [Seg("n", "R"), Seg("s", "C")])]
         for k in ("ABL.PL", "DAT.PL", "INS.PL"):
             out[k] = out[k][::-1]
-        # vocative with initial accent (Ved. ámba, Gk νύμφα), as in the other declensions
-        out["VOC.SG"] = _uniq([render(_initial_accent(stem))] + out["VOC.SG"])
+        # vocative *-a (Fortson §6.70: *-ah₂ with the laryngeal lost before a pause; Ringe §2.3.4 *-[a]) with the
+        # retracted accent of Fortson §6.70 (Gk νύμφα, OCS ženo); Ringe's unretracted *-á, then the
+        # nominative-like *-eh₂ forms (Mallory & Adams Table 4.6) follow as alternatives
+        voc_a = stem[:-2] + [Seg("a", "V", acc=stem[-2].acc)]
+        out["VOC.SG"] = _uniq([render(_initial_accent(voc_a)), render(voc_a), render(_initial_accent(stem))]
+                              + out["VOC.SG"])
+        # instr. sg. *-eh₂eh₁ beside *-eh₂h₁ (Ringe *-eh₂(e)h₁; Mallory & Adams Table 4.6)
+        out["INS.SG"] = _uniq(out["INS.SG"] + [render(_add(stem, "eh₁"))])
+        # nom.-acc. du. *-eh₂ih₁ (Beekes §13.2.11: Ved. -e, OCS -ě need *-ai) beside the generic *-h₁/-h₁e
+        for k in ("NOM.DU", "VOC.DU", "ACC.DU"):
+            out[k] = _uniq(out[k] + [render(_add(stem, "ih₁"))])
         # gen. sg. *-eh₂es beside -eh₂s (Beekes, Lundquist & Yates)
         out["GEN.SG"] = _uniq(out["GEN.SG"] + [render(_add(stem, "es"))])
     return out
@@ -196,6 +205,7 @@
         return render(_add(st, plain_ending if has_accent(st) else acc_ending))
 
     out: Cells = {}
+    vh2 = False     # stem in *-eh₂ (dn̥ǵʰwéh₂-) or asigmatic devī *-ih₂: Stang's law in acc. sg./pl.
     # --- singular, strong
     if neuter:
         out["NOM.SG"] = out["VOC.SG"] = out["ACC.SG"] = [render(strong)]
@@ -225,8 +235,22 @@
                 # Ved. pŕ̥thivi, dévi. Ringe's unretracted form and the -ih₂ forms follow as alternatives.
                 short = strong[:-1]
                 out["VOC.SG"] = _uniq([render(_initial_accent(short)), render(short)] + out["VOC.SG"])
+        if hb and spec.nom_sg and len(strong) > 1 and strong[-1].base == "h2" and not strong[-2].vocalic:
+            # asigmatic h₂-stem with a lexical nominative (gʷḗn): voc. = nom. (Ringe §2.3.4, gʷḗn), and the
+            # bare stem *gʷénh₂ (Fortson §6.70, Beekes §13.2.6) as an alternative nominative
+            out["NOM.SG"] = _uniq(out["NOM.SG"] + [render(strong)])
+            out["VOC.SG"] = _uniq([render(nom)] + out["VOC.SG"])
         acc = stang(_add(strong, "m"))
         out["ACC.SG"] = [render(contract_eh2m(acc) if not hb else acc)]
+        # not the vr̥kī́ type (sigmatic nom_sg): Ved. vr̥kíyam, Beekes p. 201 *-ieH-m; nor *-oh₁ (Ved. pánthām
+        # scanned disyllabic, Beekes p. 199)
+        vh2 = len(strong) > 1 and strong[-1].base == "h2" and (
+            (strong[-2].kind == "V" and strong[-2].base == "e")
+            or (nom is strong and strong[-2].syl and strong[-2].base == "y"))
+        if hb and vh2:
+            # Stang's law after the laryngeal (Fortson §3.38, §6.70): *-eh₂m, not *-eh₂m̥ (Ringe dn̥ǵʰwéh₂m);
+            # devī-type *-ih₂m (Fortson §17.12, Beekes §13.2.6 p. 204; Ved. devī́m), Ringe's *-ih₂m̥ kept second
+            out["ACC.SG"] = _uniq([render(strong + [Seg("m", "R")])] + out["ACC.SG"])
     # --- singular, weak
     if not weak_acc:
         # primary -és; -ós as an alternative (Beekes, Lundquist & Yates; Fortson §6.8 calls it a spread)
@@ -293,6 +317,13 @@
             if len(strong) > 1 and strong[-1].base == "w" and not strong[-1].syl and strong[-2].kind == "V":
                 # Stang's law first: gʷṓs (Ringe; Ved. gā́s, Gk dial. βῶς), not the pre-form gʷówn̥s
                 acc_pl.insert(0, render(lengthen_last_vowel(strong[:-1]) + [Seg("s", "C")]))
+            if vh2:
+                # *-eh₂ns > *-ās (Fortson §6.70; Ringe dn̥ǵʰwéh₂ns (-ās)); devī *-ih₂ns (Beekes §15.2.1 *ih₂ns),
+                # Ringe's *-ih₂n̥s kept second
+                vhs = [render(strong + [Seg("n", "R"), Seg("s", "C")])]
+                if strong[-2].kind == "V":
+                    vhs.insert(0, render(strong[:-2] + [Seg("a", "V", long=True, acc=strong[-2].acc), Seg("s", "C")]))
+                acc_pl = vhs + acc_pl
             out["ACC.PL"] = acc_pl + out["ACC.PL"]
     out["GEN.PL"] = ([w("ṓm", "ōm")] if hb else []) + [w("óHom", "oHom")]
     mos, bhos = w("mós", "mos", obl_pl), w("bʰós", "bʰos", obl_pl)
```

What changes, per hunk:
1. eh₂ voc. *-a* (D2); instr. *-eh₂eh₁* and du. *-eh₂ih₁* as alternatives (D9).
2. *gʷḗn* voc. = nom. (D4).
3. acc. sg. Stang for *-eh₂* and devī́ *-ih₂* (D1, D6).
4. acc. pl. *-ās / -eh₂ns* and devī́ *-ih₂ns* (D5, D6).

Checked on these stems: vr̥kī́ *wl̥kʷíh₂m̥*, *gʷénh₂m̥*, *póntoh₁m̥*, *súHm̥* unchanged; *dn̥ǵʰwéh₂m | dn̥ǵʰwéh₂m̥ |
dn̥ǵʰwā́m*; *déywih₂m | déywih₂m̥*; *tn̥h₂éwih₂m*; *h₁sn̥tíh₂m*.

Test to add (`tests/test_morph_feminine.py`; passes with the diff applied):

```python
"""Feminine eh₂/ih₂ stems: engine sweep fixes (docs/audits/engine-sweep/feminine.md)."""

import pytest

from pie.morph import AdjSpec, NounSpec, decline, decline_adj


@pytest.mark.parametrize("spec,feat,want", [
    # eh₂ vocative *-a, accent retracted (Fortson §6.70), Ringe's unretracted *-á second (Ringe §2.3.4)
    (NounSpec("h₂ékʷeh₂", gender="f"), "VOC.SG", ["h₂ékʷa", "h₂ékʷeh₂"]),
    (NounSpec("bʰoréh₂", gender="f"), "VOC.SG", ["bʰóra", "bʰorá", "bʰóreh₂", "bʰoréh₂"]),
    # athematic eh₂: Stang's law (Ringe §2.3.4: dn̥ǵʰwéh₂m (-ām), dn̥ǵʰwéh₂ns (-ās))
    (NounSpec("dn̥ǵʰwéh₂", "dn̥ǵʰuh₂", "hysterokinetic", "f", nom_sg="dn̥ǵʰwéh₂s"), "ACC.SG",
     ["dn̥ǵʰwéh₂m", "dn̥ǵʰwéh₂m̥", "dn̥ǵʰwā́m"]),
    (NounSpec("dn̥ǵʰwéh₂", "dn̥ǵʰuh₂", "hysterokinetic", "f", nom_sg="dn̥ǵʰwéh₂s"), "ACC.PL",
     ["dn̥ǵʰwā́s", "dn̥ǵʰwéh₂ns", "dn̥ǵʰwéh₂n̥s", "dn̥ǵʰwéh₂m̥s"]),
    # devī: *-ih₂m, *-ih₂ns first (Fortson, Beekes p. 204, L&Y Table 122.3 note), Ringe's -m̥/-n̥s second
    (NounSpec("déywih₂", "diwyéh₂", "proterokinetic", "f"), "ACC.SG", ["déywih₂m", "déywih₂m̥"]),
    (NounSpec("déywih₂", "diwyéh₂", "proterokinetic", "f"), "ACC.PL", ["déywih₂ns", "déywih₂n̥s", "déywih₂m̥s"]),
    # unchanged: vr̥kī́ type (Ved. vr̥kíyam), C+H stems (Ringe gʷénh₂m̥), *-oh₁ (Ved. pánthām, disyllabic)
    (NounSpec("wl̥kʷíh₂", "wl̥kʷih₂", "hysterokinetic", "f", nom_sg="wl̥kʷíh₂s"), "ACC.SG", ["wl̥kʷíh₂m̥"]),
    (NounSpec("gʷénh₂", "gʷnéh₂", "proterokinetic", "f"), "ACC.SG", ["gʷénh₂m̥"]),
    (NounSpec("póntoh₁", "pn̥th₁", "hysterokinetic"), "ACC.SG", ["póntoh₁m̥"]),
])
def test_feminine_cells(spec, feat, want):
    assert decline(spec, "handbook")[feat] == want


def test_feminine_adjectives():
    f = decline_adj(AdjSpec("néwo"), "handbook")["f"]
    assert f["VOC.SG"][0] == "néwa"
    f = decline_adj(AdjSpec("ténh₂u", "tn̥h₂éw", "tn̥h₂éwih₂", "tn̥h₂uyéh₂", "proterokinetic"), "handbook")["f"]
    assert f["ACC.SG"][:2] == ["tn̥h₂éwih₂m", "tn̥h₂éwih₂m̥"]
    assert f["GEN.SG"][0] == "tn̥h₂uyéh₂s"
```

## 8. For other auditors / conventions

- **Thematic adjectives (cross-family).** Nine thematic-adjective lemmas are unaccented in the lexicon itself, so
  every masculine, feminine and neuter cell is unaccented: ǵʰeh₁ros, h₃enHostos, h₁uh₂nos, h₁weh₂nos, moldos,
  negʷnos, polh₂nos (shape rule); dlongʰos, weh₁ros (table). The feminine inherits the problem; the fix belongs to
  the thematic/adjective auditor. Corpus: *ǵʰeh₁ros* ×1 (masculine).
- **instr. pl. *-bʰis* vs *-bʰi*.** Ringe (*-eh₂bʰi*), Beekes (*-h₂bʰi*) and M&A (*-eh₂bʰi*) all write *-bʰi*; the
  engine puts *-bʰis* first in every athematic and eh₂ paradigm. This is a cross-family convention question, not
  something to change for the feminine alone.
- **Numerals tísr̥ / kʷétesr̥.** These go through `AdjSpec.genders()` with `devi=True`. That is harmless, since they
  are plural only, but the *-sr-* feminine is not an ih₂ formation (Fortson §6.71). The closed class has its own
  table for them.
