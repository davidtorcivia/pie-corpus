# 8c corpus-quality fix batch 2 (cq2, 2026-10-28/29)

Same method as batch 1 (`docs/research/8c-corpus-quality-batch1.md`):
- every item was checked against the source, the production loader and a dictionary before it was fixed;
- fixes are made at the source (shared cq loader, rule modules, z-cq override tables);
- rules are general, with exception lists;
- tests run on the production path.

Read slabs, claims and committed Stage C-S and Tier 2 records are unchanged. The fixes apply to future
builds and to the search index.

Inputs:
- the lead decisions left open by batch 1;
- the Tier 2 drafter's "Mapping errors found" (`docs/audits/tier2-round3-drafts.md`);
- the builder errors of Tier 2 review round 6 (`docs/audits/tier2-review-r6.md` §4);
- batch 1's deferred structural items (scan 42 compound members, scan 30 clitics);
- five lead-expansion mapping errors (`data/research/formulas/mapping-errors-lead-expansion.jsonl`, 64bdaad).

## Ledger

`data/research/8c/corpus-quality/error-verdicts-cq2.jsonl` holds 33 records: 31 confirmed, 1 rejected, 1 unclear.

| source | records | confirmed / rejected / unclear |
|---|---:|---|
| lead decisions (gan, Dia, Greek capitals, byliny capitals, Bessonov, dos, fichi) | 7 | 7 / 0 / 0 |
| Tier 2 round-3 drafter | 12 | 11 / 1 / 0 (rejected: VedaWeb RV 1.113.13a, whose token layer has purā́ and uṣā́ḥ apart; RV 7.75.3b is recorded as a reading note) |
| Tier 2 r6 builder errors (ἠέλιος, √śī-, saē-, janāni) | 4 | 4 / 0 / 0 (νεφέλη, maṣ̌iia-, dhr̥ṣ-, εἰμί, ūrdhva are counted with the round-3 records) |
| batch-1 deferred (scan 42, scan 30) | 2 | 1 / 0 / 1 |
| lead expansion (√dam, damáyantam, dama, deint, focal) + dáma-/dám- found while verifying | 6 | 6 / 0 / 0 |
| found while verifying: empty headword key; sa-ep rows ignored by the index loader | 2 | 2 / 0 / 0 |

## A bug in this batch's first commit (decd105), fixed

**What happened.** The round-3 key row for Avestan maṣ̌iia- was written in Avestan script (𐬨𐬀𐬴𐬌𐬌𐬀).
`key_ae` keys transliteration only, so that row keyed to the empty string. `pie.mapping.path_decision`
then matched it against every Avestan-script term in a dictionary path.

**Effect on the index built from decd105** (`corpora.sqlite` at 23:50 on 2026-10-28):
- 16,232 of 103,999 Avestan words were keyed *mr̥tós: mazdā 1,590, ahura 1,536, vohu 253, and others;
- the pre-cq2 index has 17;
- in the secure check, vohu- lost *h₁wésus, so epic-diction-008 fell from exact to none.

**Fix.** `pie.mapping.headword_key` never returns an empty key: a word the keyer cannot read keys to
itself (NFC, lower-case).
- Key rows use it at load, and path terms use it at lookup.
- A `form` row whose key is empty now raises an error at load.
- Regression test: `tests/test_cq2.py::test_unreadable_headword_key_matches_only_itself`.

## General rules added

**Greek capitalised lemmas** (`pie/cq2_other.greek_capitalised`). A GLAUx/treebank lemma with a capital
and a lower-case letter is decided by `pie.name_mapping.name_lemma`:
- `THEONYMS` keep their lemma and ids;
- every other name becomes "(name)", non-content.

Exception lists:
- capitalised function words (`GREEK_FUNCTION_CAPITALS`): lower-cased, non-content;
- pronominal adjectives, quantifiers and ordinals (`GREEK_ADJECTIVE_CAPITALS`): lower-cased;
- verbs (citation form -ω, -μαι, -μι): lower-cased;
- the measured list `data/research/formulas/cq2-greek-capitalised.json` (534 types, 1,751 tokens; `scripts/cq2_greek_capitals.py`): lower-cased.

All-capital lemmas (letter labels, inscriptions) are non-content. Ἀοῦς lemmatised Ἀών becomes Ἠώς.

**Irish** (`pie/celtic_mapping._cq2_irish_rule`):
- Medial capital Dia/Dhia/Día becomes día@god: content, *deywós, as the lead decided.
- Dia before a weekday name becomes día@day.
- Dia before a nasalised word is left unchanged unless an attribute follows (`_CQ2_DIA_NASAL_GOD`).
- dos becomes dos@bush (unmapped), or do before a verb (`_CQ2_DOS_VERB_NEXT`).
- fichi becomes fiche (non-content numeral).

**Byliny, dainos, Vuk sentence-initial capitals** (`pie.bsl_mapping.name_flags`, used by `load_bsl`).
A capitalised word that is not line-initial and follows . ! ? … : or an opening quote or dash is not a
name if its lower-case form occurs in the corpus.

**Material units**:
- `material-unit-rules-cq2-other.json` excludes Rybnikov vol. 2 (narod72) lines 21980-38731: the letters extract and Bessonov's essay, 2,730 units.
- `same-work-cq2.json` gives CELT G301008 and G301900 #25 (Síaburcharpat Con Culaind) one work id. Both copies stay.

**Armenian.** gam@present becomes gam everywhere, as the lead decided.

**Welsh.** deint with the surface neint becomes nant (`pie/cq2_other.py`). All 10 tokens read mean "streams, valleys".

**Theonyms whose word is a derivative of the right lexeme** (`pie.name_mapping.THEONYM_DERIVATIVES`).
Helios (grc ἥλιος) and Sūrya (sa sūrya) are the -iyo- derivative of *sóh₂wl̥, so the secure check
counts them at root level. They still keep their roots as theonyms. The narrowing rule excludes wrong
lexemes (Νηρεύς, Τρίτων, Ῥέα); these two have the right lexeme in another formation.

**This is a reading of the approved narrowing rule, not part of it. Please review it.** Without the
exception, the ἥλιος derivative row would turn the god Ἥλιος (494 grc and grc-late tokens) into
"(name)". Homeric Ἠέλιος was "(name)" before and still is, because it is not on `THEONYMS`.

## Mapping rows (`data/research/formulas/mapping-overrides/z-cq2-formulas.json`)

Each item gives the before and after secure-check level where relevant.

**Tier 2 round 3:**
- νεφέλη goes to *nebʰelos (*nébʰos: exact becomes root).
- εἰμί goes to *h₁ésti (root becomes exact).
- √dhr̥ṣ-, dhṛṣ go to *dʰers- (exact becomes root).
- √vas- 2 goes to *wéstor (root becomes exact).
- ūrdhvá-, ūrdhva go to *h₃r̥dʰwós (root becomes exact).
- mártya-, martya and Avestan maṣ̌iia- are derivatives of *mr̥tós (exact becomes root).
- ποίκιλμα is a derivative of *poyḱós (was unmapped).

**Tier 2 r6:**
- hom ἠέλιος, ἥλιος and grp ἥλιος, ἠέλιος are derivatives of *sóh₂wl̥ (exact becomes root).
- rv √śī-, av and sa-ep śī go to *ḱéytor plus the root (root becomes exact). The √ was never the problem: `tier2_secure.key` strips it.
- Avestan saē, saēte, sōire go to *ḱéytor. The dictionary route had gone to the u-stem *ḱéy-u-s.
- Avestan jan, janāni go to *gʷʰénti. CAB has no lemmas, so the ae table is keyed by form.

**Lead expansion:**
- sa-ep dam and rv √damⁱ- go to *domh₂éyeti plus *demh₂- "tame". This drops *dṓm "house" and *demh₂- "join".
- sa-ep dama goes to "tame" only (26 units read, all "self-restraint").
- Found while verifying: rv dám- "house" goes to *dṓm, and rv dáma- and av dama "house" are derivatives of *dṓm. All three had the "tame"/"join" ids.
- cy deint goes to *h₃dónts (was *dm̥tós).
- celt, sga and sga-glosses focal/focul are unmapped: the word is a loan from Latin vocabulum.

**Left open:** Welsh nant is keyed *nem- "distribute" through a lexicon-reflex route. Matasović's *nanto- has an unclear origin. Not verified, so not changed.

## Structural items

**Compound members (scan 42): implemented as a search layer** (`pie/compound_members.py`).
- Members come from the Kaikki etymology templates ({{af}}, {{compound}}, {{prefix}} and similar) for Greek, Sanskrit and Latin.
- Otherwise the word is split at a closed first member: εὐ-/su-, δυσ-/dus-, πολυ-/puru-, ἡμι-/sāmi-, and the numerals.
- Prefix members take reviewed ids (*h₁su-, *n̥-, *dus-, *pélh₁u-, *sēmi-). Other members take the production ids of the same-language lemma.
- Preverbs are excluded. The privative is used only where a template names it.

Index words carry `member_ids` / `member_groups`, posted as root terms. `collocates_8c.py` counts them as keys.

Members are never lexeme ids and never secure-check evidence. *Hn̥dʰér "under" is a preposition, so it belongs with scan 30.

**Clitics and particles (scan 30): decision recorded.** They stay non-content (unchanged).
- Posting them would change the content-word windows and counts of every corpus.
- A clitic-aware scan needs a separate function-word layer in the index. That is deferred.

## Tests

- `tests/test_cq2.py` (82 tests): Greek capitals, Ἀοῦς, gam, the Tier 2 rows, the empty-key regression, the late rows, neint, the Irish rules, byliny capitals, the Bessonov boundaries, same-work ids, compound members (including index posting), and DCS verse citations.
- Assertions that the new general rules supersede were updated, with a comment: `test_celtic_w5.py`, `test_mapping_w7_other.py`, `test_mapping_w9_other.py`, `test_stagecs_w5_other.py`, `test_stagecs_w6_other.py`, `test_stagecs_w8_other.py`, `test_cq1_celtic.py`.

**Full suite** (2026-10-29, at 9297a88 plus the working tree): 3,726 passed, 6 failed, 3 skipped (786 s).
- `test_mapping_resolution.py::test_every_override_file_and_key_is_loaded` failed because it still keyed rows with the language keyer. It now uses `headword_key` (5cb5499) and passes when rerun alone (20 passed).
- `test_batch_release.py::test_shipped_migration` and `::test_meter_exact_gate` also fail in a clean worktree at HEAD (Tier 3 t023 is not admitted). This is generation work, not mappings.
- `test_export_chat.py` failures vary from run to run (3, then 7) and appear only in the shared tree, because of another agent's uncommitted chat-export edits. All 49 tests of the two files pass in a clean worktree at HEAD except the two batch-release tests above.
- After 645326c: `tests/test_cq2.py` and `test_mapping_resolution.py` give 104 passed.

**Final full suite at 4ed5b1a:** 3,750 passed, 2 failed, 5 skipped, 14 errors (790 s).
- The 2 failures are the same two `test_batch_release.py` tests (rerun alone: 2 failed, 21 passed).
- The 14 errors are all in `test_export_chat.py`. The export fixture raises because the Tier 3b neologism share is over the cap. That comes from the parallel Tier 3b/export work, not from mappings.

## Search index

Rebuilt with a fresh loader cache, as batch 1 did:
`UV_CACHE_DIR=/tmp/pie-uv-cache uv run python -I scripts/search_corpora.py --build --index <new> --cache-dir data/research/8c/search-index/cache-cq2`
(1,241 s), then moved to `corpora.sqlite`.

Index files in `data/research/8c/search-index/`:
- `corpora.pre-cq2.sqlite`: before this batch.
- `corpora.cq2-decd105.sqlite` and `cache-cq2-decd105/`: the first cq2 build, with the Avestan empty-key fault. Do not use it.
- `corpora.sqlite` and `cache-cq2/`: the final build, at 645326c.

Units: 2,323,653 -> 2,312,634.

| corpus | change | why |
|---|---:|---|
| byliny | -2,730 | Bessonov essay |
| grc | -1,301 | presumably capitalised names becoming non-content and windows re-cut (not measured) |
| grc-late | -7,122 | same as grc |
| ga-early | +88 | Dia "God" became content |
| mga | +38 | same as ga-early |
| sga | +8 | same as ga-early |

**Found while checking the rebuild: epic Sanskrit corpus rows were ignored.**
- Cause: `build_8c_stageC.load_extra` read the shared `av` table and the `av` errata only, so a `sa-ep` lemma row reached the index only when an `av` row said the same thing.
- Effect: in the first rebuild, AV dama "house" leaked into epic dama "self-restraint", and the epic dam row did not apply.
- Fix: `sa-ep` decisions now apply after the `av` table (645326c).
- Avestan forms: CAB's lemmatizer left janāni and sōire unlemmatised (?janani, ?soire). Form rows now send them to jan and saē.

Words and ids, before (pre-cq2) -> after (final):

| item | before | after |
|---|---|---|
| ae words keyed *mr̥tós | 17 (decd105 build: 16,232) | 17 |
| ae vohu | *h₁wésus (decd105: *mr̥tós) | *h₁wésus |
| sa-ep dam (209) | domh₂éyeti, dṓm, join, tame | domh₂éyeti, tame |
| sa-ep dama (229) | join, tame | tame |
| rv dáma- (51), dám- (9), av dama (5) | join, tame (dám- also dṓm, domh₂éyeti) | dṓm |
| rv √damⁱ- (2) | domh₂éyeti, dṓm, join, tame | domh₂éyeti, tame |
| cy deint | 14 words, *dm̥tós | 4 words, *h₃dónts (10 neint -> nant) |
| Irish focal/focul (sga, mga, ga-early) | 286 words, *wókʷtlom | unmapped |
| ae janāni (4), sōire (1) | unlemmatised | jan *gʷʰénti, saē *ḱéytor |
| compound members | none | 115,320 words with member_ids (1,939 lemma types; grc-late 71,761, grc 26,871, sa-ep 11,049, hom 2,681, rv 2,123, av 778, lat 57) |
| root postings *h₁su- / *n̥- / *dus- | 0 / 0 / 1 | 15,820 / 45,119 / 4,542 units |

Greek ἥλιος/ἠέλιος keep their ids, because formation affects only the secure check. Ἥλιος stays a content theonym.

**Pair checks** (`collocates_8c.py --pair`, ±4 content words; target units per branch, then pair hits).
Members count as keys. Before = pre-cq2; the decd105 build is shown where it differed.

| spec | before | after |
|---|---|---|
| house (*dṓm) + hear (*ḱlew-) | Indo-Iranian 217 units, p6 | Indo-Iranian 64 units, p0 (the dāntau … śrutau type gone); Greek p33 unchanged |
| word (*wókʷtlom) + speak | Celtic 260 units, p2 | Celtic 6 units, p0 |
| good (*h₁wésus) + mind (*ménos) | Indo-Iranian p133 (decd105: p6) | Indo-Iranian p135 |
| lie (*ḱéytor) + slain (*gʷʰn̥tós) | Indo-Iranian 1 unit, p0 | Indo-Iranian 561 units, p1 |
| mortal (*mr̥tós) + god (*deywós) | Indo-Iranian 24 units, p2 (decd105: 9,021, p50) | Indo-Iranian 434 units, p52 (mártya- now keyed *mr̥tós as a derivative) |
| tame (*demh₂-) target | Indo-Iranian 495 units | 433 |
| tooth (*h₃dónts) target | Celtic 143 units | 147 |
| good (*h₁su-) + horse | no target units | Greek p125, Indo-Iranian p20 (compound members: εὔιππος, suáśva-) |
| bad (*dus-) + mind | Greek 1 unit | Greek p2, Indo-Iranian p8 (δυσμενής, durmánas-) |
| *wéstor 'wear' | Indo-Iranian 6 units, p2 (with *wes-) | 95 units, p7 |
| νεφέλη (*nebʰelos) | Greek 0 | Greek 343 units |
| sun+see, dawn+sun | Greek p7 / p38 | p7 / p39 (unchanged by the ἥλιος derivative row) |

## Tier 2 lines (secure check under `scripts/build_tier2.py`'s `checks_for`; corpus/tier2 not written)

"Before" is the committed record (the clean build at 4f54115/cf9010e). "After" is the current tree.

| line | lexeme | before | after | cause |
|---|---|---|---|---|
| dawn-sun-016 | *sóh₂wl̥ | exact | root | ἠέλιος is a derivative |
| death-otherworld-012 | *h₁ésti | root | exact | εἰμί row |
| epic-diction-008 | *h₁wésus | exact | exact | the decd105 tree gave none (empty-key fault); fixed |
| epic-diction-013 | *mr̥tós | exact | root | maṣ̌iia- is a derivative |

Other r6 items:
- death-otherworld-004 *ḱéytor: root -> exact (√śī-, saē-).
- dragon-slaying-016 *gʷʰénti: root, because the Greek φονεύς is an agent noun. The Avestan side is now exact.
- dawn-sun-009 *sóh₂wl̥: exact -> root.

All of these are on unchanged plans, so the lines need re-review before their levels are used. Per r6 §5, dawn-sun-001, -018, healing-charms-001 and sky-father-006 should also be checked again when this batch lands.
