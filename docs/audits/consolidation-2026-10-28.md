# Tier 3 post-merge consolidation (2026-10-28)

All 37 Tier 3 batches (b001–b004, t001–t033; not pilot/pilot2) were re-realized at one engine stamp,
**26aa48d**. Each batch used its own model and prompt id (b00x: claude-sonnet-5-5 / tier3-planner-v3; t001, t005,
t008, t009: claude-opus-5-5 / tier3-planner-v4; all others: claude-sonnet-5-5 / tier3-planner-v4), with
`--engine-version 26aa48d`. A previous agent had re-realized b001–t016 at bc388e3 and edited plans without
committing. Its plan edits were kept after checking (they are listed below), and its corpus output was replaced by this
sweep. Between bc388e3 and 26aa48d no engine file changed. The one change, in `scripts/realize_plans.py`, is a Tier 3b-only
gate (45c415d).

**Approvals are not set.** Every realization resets the release to `pending`, including the 18 batches that were
approved before. The lead re-approves.

**Result:** 35/37 gates PASS. The two FAILs are t022 and t025, the known lexeme-cap failures, which are unchanged.
Every previously approved batch passes, and so do t026 and t033. Every batch with verse has meter_exact ≥ 0.90 (lowest:
t006 0.906, t011 0.908, t002 0.91).

Commits: 2232701 (b001–b002), f3d156e (b003–b004), 4f6f0f7 (t001–t004), 7dd0fb0 (t005, t007, t009, t010), 05f53b5
(t012–t018), 965c56e (t006, t008, t011), 9b3903c (t019–t026), 9b9c0ec (t027–t033).

## Step 1: scripts/meter_report.py

Both fixes were already committed at **bc388e3**:
- `_insert()` renumbers every head/dep at or after the insertion point.
- `cap_uses()`/`over_cap()` use the gate's own rules (CAP_EXEMPT, theme_core, theme_cap), so added epithets and vocatives are flagged.

The tests are in `tests/test_meter_report.py`: renumbering, an added vocative keeps its epithet's head, the cap note
matches the gate, and every epithet/vocative edit in t026 is flagged exactly when the gate would fail. They pass (6/6).
No further change was needed.

## Method

**Classification (step 2).** Every record of the new corpus was compared with the last committed corpus before this
pass (870f092), matching by plan. The classes:
- **(a) engine:** same plan, different output. Every token change is one of two known fixes:
  - h₁éddʰi → h₁ddʰí, IMP.2SG of 'eat' (388f35a/5346e8f, the imperative accent fix): 22 records in 13 batches;
  - h₂r̥ǵrós → h₂r̥ǵróm, 'shining' agreeing with a neuter subject (e0b722c, white and shining made adjectives): t031-0015.

  Two more kinds of (a) touch no token:
  - the `syllables` field recounted by the b453c9c syllabifier: 216 records in batches realized before it;
  - the gloss of 'sing' changed from recite~ to sing (3b2905c): 5 b002 records.
- **(b) meter repair:** the repairs were committed together with their re-realized corpora, so against 870f092 class (b)
  is empty. Each repaired batch was therefore also compared with the corpus last approved before its repair (the repair
  commit's parent). Every record whose plan changed is named in the batch's meter-repair doc (`b-repair`). Records also
  edited in this pass are marked `+d`.
- **(d) plan edited in this pass:** check_plan fixes, restorations and meter-neutral edits (the counts are given per batch).
- **(c) unexpected:** none in any batch, against either baseline. Each first-pass candidate was investigated: the
  syllables-only and gloss-only differences above, and in t014 (against the pre-repair corpus) bʰl̥Hós → bʰl̥Héh₂
  'white' agreeing with a feminine noun (e0b722c).

**check_plan (step 3).** Of the plans in the task brief:
- At the start, check_plan rejected only b002-0250, t010-0012, t027-0016, t027-0022 and t027-0025. All five are fixed.
- **t026-0010 has no dual perfect.** Its only perfect is bʰebʰóyh₂h₂e PRF.1SG ('I am not afraid'), beside a dual
  *present* (trésetes); check_plan accepts it, and it is the same at the t026 approval (1aced48).
- **t027-0001/08/12/14/18/30/40:** every IMP in them already has `person: 2`. The t027 review set person 2 on all 51
  such imperatives (its release rationale says so), and the committed t027 corpus already has h₁n̥dʰdʰí IMP.2SG etc.
  Nothing is rejected, and nothing was changed.
- t005-0016 (a dual perfect) had been turned into a plural by the t005 meter repair (c7ba2bf); it stays plural.

**Restorations (step 4).** For every repaired batch:
- The structural differences between each pre-repair plan and the current plan were listed: dropped slots, number
  changes, clause restructures.
- The repair's meaning edits are: dropped objects, possessors, numerals, epithets, adverbs and vocatives, and changed
  number. Each still-missing one was re-applied to the current plan and the line measured.
- Where the line went off target, a meter-neutral compensation was searched for first: toggling particles nu / -ge and
  clause -kʷe in the same line, then a split/merge or an epithet.
- Restorations that left a line off target were accepted only within each batch's budget (lines that may be off target
  while meter_exact stays ≥ 0.90), in priority order:
  1. formulas and named addressees ("Father Sky", "Mother Earth", "givers of good things", "imperishable fame");
  2. objects;
  3. noun possessors;
  4. number;
  5. pronoun possessors.
- Meaning-neutral edits were left: pro-dropped personal subjects, the copula dropped in a nominal sentence, and
  asyndeton for -kʷe. Dual for plural was also left where the English says "two".
- Some lines were improved without any meaning change: -kʷe for asyndeton, particles, and merging two short lines.
- Three restorations were swapped or undone because they broke the lexeme cap (see t006, t008, t011, t026).

**Head/dep (step 5).** For every repaired batch (b002 and b003 in full; the others too, not just a spot check):
- The links were compared, pre-repair plan against current plan, as multisets of (dependent lex_id, role) → (target
  lex_id, role) per aligned clause.
- A link whose dependent already existed but now points elsewhere would be misdirected. There are none in any batch.
- The single flag, t026-0022, is an epithet the repair added ("Dear mistress"), not a moved link.
- One misdirected possessor that my own restoration tool produced (t008-0001 c3: "her sister" restored onto "head")
  was caught before writing and fixed. So was a slot deletion in t026-0029 that would have left an epithet pointing at
  the verb.
- No head/dep index is out of range or self-referential in any batch.

**Spot check (step 8).**
- Population: the verse lines of metered-genre records in the 17 meter-repaired batches, after the sweep. A line is
  meter-changed if it is not among the verse lines of the same plan's record in the pre-repair corpus (1,698 lines);
  otherwise it is unchanged (806 lines).
- Draw: `rng = random.Random(0)`; 40 = `rng.sample(sorted(changed), 40)`, then 10 = `rng.sample(sorted(unchanged), 10)`.
  The keys are (batch, record id, line index).
- Each line was judged against the record's English and gloss by the reviewer-brief criteria (wrong = ungrammatical or
  meaning changed; minor = ablaut/accent/notation/stretched sense).
- Results:
  - **Meter-changed lines: 0 wrong, 1 minor, 39 ok.**
  - **Controls: 0 wrong, 0 minor, 10 ok.**
- The judgments are not blind; I edited these plans.

## Per batch

### b001

- **Gate:** PASS; 250/250 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 14; a-engine (token: h₁éddʰi→h₁ddʰí) 1; unchanged 235. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### b002

- **Gate:** PASS; 250/250 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** 28/30 = 0.933 (last committed: 29/30 = 0.967).
- **Changed records vs the last committed corpus (870f092):** a-engine (gloss recite~→sing, 3b2905c) 5; d-plan 2; unchanged 243. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (24b607e^):** b-repair 22; d-plan-only+d 1; unchanged 227. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** b002-0250: the nominalized adjective h₂r̥ǵrós ("the shining one", OBJ) given gender m.
- **Meanings restored** (1 of the repair's meaning edits now undone): b002-0223 VOC pie-lex-potis
- **Not restored:** 1 meaning edits: b002-0238 SUBJ pie-lex-h2owis num null→"PL" (repair) . Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=0 (pre-repair 24b607e^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** no line of this batch was drawn.

### b003

- **Gate:** PASS; 250/250 realized, reject rate 0.0, max lexeme uses 7.
- **meter_exact:** 189/206 = 0.917 (last committed: 192/206 = 0.932).
- **Changed records vs the last committed corpus (870f092):** d-plan 5; unchanged 245. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (24b607e^):** b-repair 150; b-repair+d 5; unchanged 95. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (3 of the repair's meaning edits now undone): b003-0013 VOC pie-lex-meh2texr (SG); b003-0040 VOC pie-lex-h2ekweh2 (PL); b003-0065 MOD closed:numerals/4
- **Restructured by the repair (clauses split, merged or recast; read by hand, meaning kept; the slot-level diff is not meaningful):** b003-0005, b003-0033, b003-0038.
- **Not restored:** 0 meaning edits. Plus 16 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=7 (pre-repair 24b607e^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 2 meter-changed lines ({'ok': 2}), 0 controls ({}).

### b004

- **Gate:** PASS; 250/250 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 12; a-engine (token: h₁éddʰi→h₁ddʰí) 1; unchanged 237. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t001

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 13.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 13; unchanged 27. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t002

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 9.
- **meter_exact:** 302/332 = 0.91 (last committed: 300/332 = 0.904).
- **Changed records vs the last committed corpus (870f092):** d-plan 4; unchanged 36. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (67718c4^):** b-repair 36; b-repair+d 4. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (3 of the repair's meaning edits now undone): t002-0023 POSS closed:personal/1 (SG); t002-0040 POSS closed:personal/1 (PL); t002-0040 POSS closed:personal/1 (PL)
- **Not restored:** 3 meaning edits: t002-0006 SUBJ pie-lex-h1ekjwos num "PL"→"DU" (repair) ; t002-0008 LOC pie-lex-h3osdos num null→"PL" (repair) ; t002-0023 SUBJ pie-lex-h1ekjwos num "PL"→"DU" (repair) . Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=44 (pre-repair 67718c4^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 6 meter-changed lines ({'ok': 6}), 1 controls ({'ok': 1}).

### t003

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 8.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 13; a-engine (token: h₁éddʰi→h₁ddʰí) 2; unchanged 25. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t004

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 11.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 17; unchanged 23. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t005

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 13.
- **meter_exact:** 461/490 = 0.941 (last committed: 490/490 = 1.0).
- **Changed records vs the last committed corpus (870f092):** d-plan 37; unchanged 3. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (c7ba2bf^):** b-repair 3; b-repair+d 37. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (68 of the repair's meaning edits now undone): t005-0001 POSS closed:personal/1 (PL); t005-0002 VOC pie-lex-dyexws; t005-0003 VOC pie-lex-dyexws; t005-0005 MOD closed:demonstrative_so; t005-0006 IO pie-lex-bhreh2texr num "PL"→"SG" (repair) ; t005-0007 ADV pie-lex-h2ew; t005-0008 POSS closed:personal/2 (SG); t005-0009 LOC pie-lex-mrtwos num "PL"→"SG" (repair) ; t005-0009 ADV pie-lex-ud; t005-0009 ADV pie-lex-h2ew; t005-0009 POSS closed:personal/1 (PL); t005-0010 POSS closed:personal/2 (SG); t005-0010 POSS closed:personal/2 (SG); t005-0011 POSS closed:personal/1 (PL); t005-0012 POSS closed:personal/1 (PL); t005-0012 POSS closed:personal/1 (PL); t005-0013 POSS closed:personal/2 (SG); t005-0013 ADV pie-lex-h1egjhs; t005-0013 POSS closed:personal/1 (PL); t005-0014 LOC pie-lex-wodr num "PL"→"SG" (repair) ; t005-0015 POSS closed:personal/1 (PL); t005-0016 POSS closed:personal/1 (PL); t005-0017 VOC pie-lex-h1ngwnis; t005-0017 LOC pie-lex-ghordhos num "PL"→"SG" (repair) ; t005-0017 POSS closed:personal/2 (SG); t005-0017 VOC pie-lex-deh3toxr; t005-0017 POSS pie-lex-h1wesus (PL); t005-0018 POSS closed:personal/1 (PL); t005-0018 POSS closed:personal/2 (SG); t005-0019 POSS closed:personal/1 (PL); t005-0019 VOC pie-lex-h1ngwnis; t005-0020 OBJ pie-lex-wekwos num "PL"→"SG" (repair) ; t005-0020 ADV pie-lex-h2epo; t005-0020 POSS closed:personal/2 (PL); t005-0021 SUBJ pie-lex-wreh2ds num "PL"→"SG" (repair) ; t005-0021 POSS closed:personal/2 (PL); t005-0021 POSS closed:personal/1 (PL); t005-0022 MOD closed:numerals/indeclinable/7; t005-0022 SUBJ pie-lex-kjwox num "PL"→"SG" (repair) ; t005-0022 PRED pie-lex-meh2texr num "PL"→"SG" (repair) ; t005-0023 POSS pie-lex-dyexws; t005-0023 POSS closed:personal/1 (PL); t005-0025 ADV pie-lex-ud; t005-0026 POSS closed:personal/1 (PL); t005-0026 POSS closed:personal/1 (PL); t005-0027 SUBJ pie-lex-h2egjros num "PL"→"SG" (repair) ; t005-0027 SUBJ pie-lex-h2owis num "PL"→"SG" (repair) ; t005-0027 POSS closed:personal/2 (SG); t005-0027 POSS closed:personal/2 (SG); t005-0027 ADV pie-lex-h2mbhi; t005-0028 VOC pie-lex-deywos (PL); t005-0029 POSS pie-lex-dyexws; t005-0029 POSS closed:personal/1 (PL); t005-0030 POSS pie-lex-dyexws; t005-0031 ADV pie-lex-h2ew; t005-0033 POSS closed:personal/1 (SG); t005-0033 ADV pie-lex-h2ew; t005-0034 POSS closed:personal/1 (SG); t005-0035 IO closed:personal/2 (SG); t005-0036 POSS closed:personal/1 (SG); t005-0037 POSS closed:personal/1 (SG); t005-0037 POSS closed:personal/1 (SG); t005-0037 SUBJ pie-lex-ph2texr; t005-0038 SUBJ pie-lex-kjwox num "PL"→"SG" (repair) ; t005-0038 POSS closed:personal/1 (SG); t005-0039 POSS closed:personal/2 (SG); t005-0040 ADV pie-lex-kjom; t005-0040 ADV pie-lex-h2ew
- **Not restored:** 3 meaning edits: t005-0016 SUBJ pie-lex-wlkwos num null→"PL" (repair) ; t005-0016 SUBJ pie-lex-h1ogwhis num null→"PL" (repair) ; t005-0026 SUBJ closed:demonstrative_so. Plus 10 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=9 (pre-repair c7ba2bf^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 8 meter-changed lines ({'ok': 8}), 2 controls ({'ok': 2}).

### t006

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 8.
- **meter_exact:** 87/96 = 0.906 (last committed: 96/96 = 1.0).
- **Changed records vs the last committed corpus (870f092):** d-plan 8; unchanged 32. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (c7ba2bf^):** b-repair 7; b-repair+d 8; unchanged 25. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (10 of the repair's meaning edits now undone): t006-0002 INS pie-lex-h2ekjmox; t006-0006 SUBJ pie-lex-h2owis num "PL"→"DU" (repair) ; t006-0008 OBJ closed:personal/1 (PL); t006-0008 POSS closed:personal/1 (PL); t006-0010 PRED pie-lex-meh2texr num "PL"→"SG" (repair) ; t006-0015 VOC pie-lex-ph2texr; t006-0026 MOD pie-lex-HeHkjus; t006-0026 POSS pie-lex-h1wesus (PL); t006-0029 POSS closed:demonstrative_so; t006-0034 VOC pie-lex-deywih2 num "PL"→"SG" (repair) 
- **Not restored:** 4 meaning edits: t006-0006 ADV pie-lex-pro-2; t006-0021 POSS closed:personal/2; t006-0031 POSS closed:personal/2; t006-0034 SUBJ closed:relative_yo (PL). Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=1 (pre-repair c7ba2bf^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 2 meter-changed lines ({'ok': 2}), 0 controls ({}).

### t007

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 3; unchanged 37. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t008

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 9.
- **meter_exact:** 246/269 = 0.914 (last committed: 269/269 = 1.0).
- **Changed records vs the last committed corpus (870f092):** d-plan 16; unchanged 24. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (3375553^):** b-repair 16; b-repair+d 16; unchanged 8. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (33 of the repair's meaning edits now undone): t008-0001 IO pie-lex-potis; t008-0001 OBJ pie-lex-kwekwlos; t008-0001 POSS closed:demonstrative_so; t008-0001 POSS closed:demonstrative_so; t008-0001 POSS closed:demonstrative_so; t008-0001 SUBJ pie-lex-dhugh2texr (PL); t008-0002 POSS closed:personal/2; t008-0002 LOC pie-lex-h2ewsoxs; t008-0003 MOD pie-lex-h2yewHox; t008-0003 MOD pie-lex-newos; t008-0004 MOD closed:demonstrative_so; t008-0005 MOD pie-lex-h2yewHox; t008-0005 OBJ pie-lex-wedhmn; t008-0005 ADV pie-lex-h2epo; t008-0007 MOD pie-lex-diwyos; t008-0007 POSS closed:demonstrative_so; t008-0007 MOD pie-lex-diwyos; t008-0009 MOD closed:demonstrative_so; t008-0010 OBJ pie-lex-h2wlh1neh2; t008-0011 POSS pie-lex-dheh1mn; t008-0011 POSS closed:personal/2; t008-0011 POSS closed:personal/2; t008-0011 POSS closed:personal/2; t008-0012 POSS closed:personal/1 (PL); t008-0012 POSS closed:personal/2; t008-0015 POSS closed:demonstrative_so; t008-0028 MOD closed:numerals/3; t008-0030 OBJ pie-lex-keh2nmn; t008-0030 ADV pie-lex-pro-2; t008-0034 MOD closed:numerals/4; t008-0034 OBJ closed:demonstrative_so; t008-0036 POSS closed:personal/1; t008-0039 POSS closed:personal/2
- **Not restored:** 11 meaning edits: t008-0002 VOC pie-lex-h2yewHox; t008-0005 MOD closed:numerals/2; t008-0006 SUBJ pie-lex-dhugh2texr; t008-0006 POSS pie-lex-dyexws; t008-0014 MOD closed:numerals/2; t008-0015 ADV pie-lex-h2enti; t008-0027 MOD pie-lex-HeHkjus; t008-0028 MOD closed:demonstrative_so; t008-0034 MOD closed:demonstrative_so; t008-0037 MOD closed:numerals/2; t008-0038 MOD closed:numerals/2. Plus 8 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=8 (pre-repair 3375553^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 4 meter-changed lines ({'ok': 4}), 1 controls ({'ok': 1}).

### t009

- **Gate:** PASS; 30/30 realized, reject rate 0.0, max lexeme uses 11.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 11; unchanged 19. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t010

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 8; a-engine (token: h₁éddʰi→h₁ddʰí) 2; d-plan 1; unchanged 29. (c) unexplained: 0.
- **check_plan fixes:** t010-0012 c6: dual perfect tetórpe → aorist terpt-2 (tr̥ptā́m 3du, "they were satisfied").

### t011

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** 138/152 = 0.908 (last committed: 144/152 = 0.947).
- **Changed records vs the last committed corpus (870f092):** d-plan 6; unchanged 34. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (bbe64b3^):** b-repair 32; b-repair+d 5; unchanged 3. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (7 of the repair's meaning edits now undone): t011-0006 VOC pie-lex-dyexws; t011-0006 VOC pie-lex-dyexws; t011-0007 VOC pie-lex-dyexws; t011-0015 VOC pie-lex-soh2wl; t011-0024 VOC pie-lex-dhegjhoxm; t011-0025 VOC pie-lex-dhegjhoxm; t011-0028 VOC pie-lex-deywos (PL)
- **Not restored:** 11 meaning edits: t011-0001 MOD pie-lex-megjh2s; t011-0001 VOC pie-lex-gwhonos; t011-0003 MOD pie-lex-megjh2s; t011-0003 VOC pie-lex-perkwunos; t011-0009 VOC pie-lex-h2ewsoxs; t011-0009 MOD pie-lex-lewkos; t011-0017 VOC pie-lex-h1ngwnis; t011-0018 POSS closed:personal/1 (PL); t011-0021 POSS closed:personal/1 (PL); t011-0026 POSS closed:personal/1 (PL); t011-0029 VOC pie-lex-deywos (PL). Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=12 (pre-repair bbe64b3^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 4 meter-changed lines ({'ok': 4}), 1 controls ({'ok': 1}).

### t012

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 7.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 5; a-engine (token: h₁éddʰi→h₁ddʰí) 1; unchanged 34. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t013

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 7.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 16; a-engine (token: h₁éddʰi→h₁ddʰí) 1; unchanged 23. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t014

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 7.
- **meter_exact:** 67/67 = 1.0 (last committed: 67/67 = 1.0).
- **Changed records vs the last committed corpus (870f092):** unchanged 40. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (3375553^):** a-engine 1; b-repair 10; c-unexpected 2; unchanged 27. `+d` = the plan was edited again in this pass. The two `c-unexpected` records (t014-0005, t014-0027) and one `a-engine` record differ only by bʰl̥Hós → bʰl̥Héh₂ 'white' agreeing with a feminine noun (e0b722c, white/shining made adjectives) and h₁éddʰi → h₁ddʰí: engine fixes, not unexpected.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (0 of the repair's meaning edits now undone): none.
- **Not restored:** 0 meaning edits. Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=15 (pre-repair 3375553^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 1 controls ({'ok': 1}).

### t015

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 7.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 10; a-engine (token: h₁éddʰi→h₁ddʰí) 3; unchanged 27. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t016

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 10.
- **meter_exact:** 89/94 = 0.947 (last committed: 91/94 = 0.968).
- **Changed records vs the last committed corpus (870f092):** d-plan 4; unchanged 36. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (bbe64b3^):** a-engine 1; b-repair 6; b-repair+d 4; unchanged 29. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (4 of the repair's meaning edits now undone): t016-0033 POSS closed:personal/2; t016-0034 POSS closed:personal/1 (PL); t016-0038 VOC pie-lex-kwseps; t016-0040 ADV pie-lex-Hndhi
- **Not restored:** 0 meaning edits. Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=6 (pre-repair bbe64b3^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 2 controls ({'ok': 2}).

### t017

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** 29/29 = 1.0 (last committed: 29/29 = 1.0).
- **Changed records vs the last committed corpus (870f092):** unchanged 40. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (67718c4^):** b-repair 9; unchanged 31. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (0 of the repair's meaning edits now undone): none.
- **Not restored:** 1 meaning edits: t017-0038 PRED pie-lex-plh2seh2 num null→"PL" (repair) . Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=4 (pre-repair 67718c4^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 0 controls ({}).

### t018

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 10.
- **meter_exact:** 42/45 = 0.933 (last committed: 44/45 = 0.978).
- **Changed records vs the last committed corpus (870f092):** d-plan 2; unchanged 38. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (67718c4^):** a-engine 1; b-repair 4; b-repair+d 2; unchanged 33. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (2 of the repair's meaning edits now undone): t018-0037 POSS closed:anaphoric_i; t018-0039 POSS closed:personal/2
- **Not restored:** 0 meaning edits. Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=5 (pre-repair 67718c4^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 0 controls ({}).

### t019

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 14.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 14; a-engine (token: h₁éddʰi→h₁ddʰí) 1; unchanged 25. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t020

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 11.
- **meter_exact:** 57/60 = 0.95 (last committed: 60/60 = 1.0).
- **Changed records vs the last committed corpus (870f092):** d-plan 2; unchanged 38. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (3375553^):** a-engine 1; b-repair 4; b-repair+d 2; unchanged 33. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (4 of the repair's meaning edits now undone): t020-0006 VOC pie-lex-kjwox; t020-0040 VOC pie-lex-ph2texr; t020-0040 VOC pie-lex-meh2texr; t020-0040 POSS closed:anaphoric_i
- **Not restored:** 3 meaning edits: t020-0006 ADV pie-lex-h2epo; t020-0015 SUBJ pie-lex-h1ekjwos num "PL"→"DU" (repair) ; t020-0035 SUBJ pie-lex-wekwos num null→"PL" (repair) . Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=9 (pre-repair 3375553^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 1 controls ({'ok': 1}).

### t021

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 10.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 15; unchanged 25. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t022

- **Gate:** FAIL (fails max_lexeme_uses<=8); 40/40 realized, reject rate 0.0, max lexeme uses 18.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 18; unchanged 22. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t023

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** 114/125 = 0.912 (last committed: 121/125 = 0.968).
- **Changed records vs the last committed corpus (870f092):** d-plan 14; unchanged 26. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (bbe64b3^):** b-repair 13; b-repair+d 14; unchanged 13. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (17 of the repair's meaning edits now undone): t023-0001 ADV pie-lex-h1egjhs; t023-0002 MOD closed:relative_yo; t023-0003 ADV pie-lex-h1egjhs; t023-0006 APPOS pie-lex-deh3toxr; t023-0006 POSS pie-lex-h1wesus (PL); t023-0007 VOC pie-lex-kjwox; t023-0008 MOD closed:deictic_ki; t023-0009 VOC pie-lex-bhoxr; t023-0013 VOC pie-lex-h2ewsoxs; t023-0013 VOC pie-lex-nokwts; t023-0014 VOC pie-lex-soh2wl; t023-0014 MOD pie-lex-swos; t023-0021 MOD pie-lex-mrwos; t023-0023 POSS closed:personal/2; t023-0025 VOC pie-lex-h1ekjwos (DU); t023-0025 MOD pie-lex-HeHkjus; t023-0027 MOD pie-lex-ndhgwhitos
- **Not restored:** 0 meaning edits. Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=8 (pre-repair bbe64b3^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 1 controls ({'ok': 1}).

### t024

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 6; a-engine (token: h₁éddʰi→h₁ddʰí) 2; unchanged 32. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t025

- **Gate:** FAIL (fails max_lexeme_uses<=9, theme_core_uses<=27); 40/40 realized, reject rate 0.0, max lexeme uses 25.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 12; a-engine (token: h₁éddʰi→h₁ddʰí) 3; unchanged 25. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t026

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 7.
- **meter_exact:** 148/158 = 0.937 (last committed: 157/158 = 0.994).
- **Changed records vs the last committed corpus (870f092):** d-plan 11; unchanged 29. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (d762b90^):** b-repair 15; b-repair+d 11; unchanged 14. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (15 of the repair's meaning edits now undone): t026-0017 OBJ pie-lex-kjexr num "PL"→"SG" (repair) ; t026-0017 MOD pie-lex-HeHkjus; t026-0017 SUBJ closed:relative_yo; t026-0018 SUBJ pie-lex-kwekwlos; t026-0018 POSS pie-lex-soh2wl; t026-0019 POSS pie-lex-deywos (PL); t026-0021 POSS pie-lex-lewks; t026-0027 MOD pie-lex-prh2wos; t026-0028 POSS closed:personal/1 (PL); t026-0029 POSS closed:personal/1; t026-0030 POSS closed:personal/1 (SG); t026-0033 POSS closed:personal/1 (PL); t026-0038 POSS closed:personal/1 (SG); t026-0038 POSS closed:personal/1 (SG); t026-0039 POSS closed:personal/1 (PL)
- **Not restored:** 3 meaning edits: t026-0021 MOD pie-lex-lewbhos; t026-0029 MOD pie-lex-swos; t026-0032 MOD pie-lex-lewbhos. Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=1 links on added slots=3 (pre-repair d762b90^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 0 controls ({}).

### t027

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 7.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 12; a-engine (token: h₁éddʰi→h₁ddʰí) 1; d-plan 3; unchanged 24. (c) unexplained: 0.
- **check_plan fixes:** t027-0016 c0 and t027-0025 c6: dual perfect stestóh₂e → perfect 3pl stesth₂ḗr ("they stood"; English "Two stood" → "They stood" / "the two stood" → "they stood"); t027-0022 c0: → past (imperfect) 3du sth₂éh₁yetām of sth₂éh₁yeti. The first fix (all three to sth₂éh₁yeti) put that lexeme at 9 uses, over the cap of 7, and stéh₂t was already at 7.

### t028

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 3; unchanged 37. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t029

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** 39/42 = 0.929 (last committed: 42/42 = 1.0).
- **Changed records vs the last committed corpus (870f092):** d-plan 3; unchanged 37. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (d762b90^):** b-repair 10; b-repair+d 3; unchanged 27. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (3 of the repair's meaning edits now undone): t029-0016 SUBJ pie-lex-gwexn; t029-0016 POSS pie-lex-gwexn; t029-0025 LOC pie-lex-peh2wr
- **Not restored:** 1 meaning edits: t029-0015 MOD closed:numerals/2. Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=9 (pre-repair d762b90^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 1 meter-changed lines ({'ok': 1}), 0 controls ({}).

### t030

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 4; a-engine (token: h₁éddʰi→h₁ddʰí) 2; unchanged 34. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t031

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 8.
- **meter_exact:** no verse lines (no metered genre).
- **Changed records vs the last committed corpus (870f092):** a-engine (syllable recount, b453c9c) 10; a-engine (token: h₂r̥ǵrós→h₂r̥ǵróm) 1; unchanged 29. (c) unexplained: 0.
- **check_plan fixes:** none needed (0 rejects).

### t032

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 6.
- **meter_exact:** 150/157 = 0.955 (last committed: 157/157 = 1.0).
- **Changed records vs the last committed corpus (870f092):** d-plan 11; unchanged 29. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (d762b90^):** b-repair 16; b-repair+d 11; unchanged 13. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (17 of the repair's meaning edits now undone): t032-0003 POSS pie-lex-soh2wl; t032-0013 POSS closed:personal/2; t032-0013 POSS closed:anaphoric_i; t032-0013 POSS closed:personal/2; t032-0028 POSS closed:personal/2; t032-0028 MOD pie-lex-kjlutos; t032-0029 POSS closed:personal/1; t032-0031 POSS pie-lex-h2engjhos; t032-0031 POSS closed:personal/1; t032-0032 MOD pie-lex-kjlutos; t032-0034 POSS closed:personal/1; t032-0034 POSS closed:personal/1; t032-0035 POSS closed:personal/1 (PL); t032-0036 POSS closed:personal/1; t032-0038 POSS closed:personal/1; t032-0039 POSS closed:personal/1; t032-0039 POSS closed:personal/2
- **Restructured by the repair (clauses split, merged or recast; read by hand, meaning kept; the slot-level diff is not meaningful):** t032-0005.
- **Not restored:** 0 meaning edits. Plus 0 meaning-neutral edits left as they are (pro-dropped personal subjects, copula dropped in a nominal sentence, coordination by -kʷe replaced by asyndeton).
- **Head/dep:** issues=0 links on added slots=17 (pre-repair d762b90^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 3 meter-changed lines ({'ok': 3}), 0 controls ({}).

### t033

- **Gate:** PASS; 40/40 realized, reject rate 0.0, max lexeme uses 11.
- **meter_exact:** 142/152 = 0.934 (last committed: 144/153 = 0.941).
- **Changed records vs the last committed corpus (870f092):** d-plan 4; unchanged 36. (c) unexplained: 0.
- **Vs the corpus last approved before the meter repair (d380b8d^):** b-repair 9; b-repair+d 4; unchanged 27. `+d` = the plan was edited again in this pass.
- **check_plan fixes:** none needed (0 rejects).
- **Meanings restored** (3 of the repair's meaning edits now undone): t033-0028 POSS closed:personal/2 (PL); t033-0029 MOD pie-lex-HeHkjus; t033-0030 POSS closed:personal/1 (PL)
- **Restructured by the repair:** the wedding dialogues (t033-0028 to 0037, 0040) were split, merged and recast, so the slot-level diff is not meaningful. Read by hand against the pre-repair plans: 0032 (the bride's goods split over two clauses), 0034 ("I marry you; do you take me?"), 0035 (questions merged, "they drank wine, and they drank beer") and 0028 (the giver verb) keep their meaning.
- **Restored:** 0028 "your song of praise", 0029 "the two swift horses", 0030 "our words" (plus one meter-neutral merge in 0034, L6+L7).
- **Not restored (minor, within a budget of 6 kept for margin):** 0030 "good Dawn" (+3 syllables), 0033 "silver for you", 0037 "this household", 0031 "these men" (the repair turned the SUBJ into a MOD with "many"), 0036 two subjects now pro-dropped ("she", "the lamb" → "it"), 0035 "your fame" now addressed to the son-in-law (SG) rather than the couple (PL), matching the English.
- **Head/dep:** issues=0 links on added slots=14 (pre-repair d380b8d^ vs now; links compared as (dependent lex, role) → (target lex, role)).
- **Spot check:** 3 meter-changed lines ({'ok': 2, 'minor': 1}), 0 controls ({}).

## Spot-check lines

| # | batch | plan | line | syl | PIE | verdict | note |
|---|---|---|---|---|---|---|---|
| ch1 | t008 | t008-0002 | L11 | 8 | nu-kʷe te deywṓs ph₂sih₁ént | ok |  |
| ch2 | t032 | t032-0038 | L4 | 8 | nu-kʷe kʷís h₁mé woséyēti | ok |  |
| ch3 | t008 | t008-0012 | L8 | 11 | Hróth₂os toy sth₂éh₁yeti kʷís tóm h₂éǵeti | ok |  |
| ch4 | b003 | b003-0064 | L1 | 8 | bʰuHyéh₁t léwkos tód-kʷe kʷḱih₁mé | ok |  |
| ch5 | t005 | t005-0017 | L8 | 8 | bʰéh₂esh₁ h₁nédʰs tód h₂epó ǵʰéys | ok |  |
| ch6 | t014 | t014-0017 | L5 | 11 | h₂nḗr wos sékʷetor nu-kʷe séh₁mn̥ séh₁yoh₂ | ok |  |
| ch7 | t011 | t011-0018 | L2 | 8 | nu h₁yós deywóns h₁éysi h₁ludʰés | ok |  |
| ch8 | t008 | t008-0008 | L2 | 11 | sélpos dʰéyǵʰesi h₂linHdʰí h₁n̥gʷnéy sddʰí | ok |  |
| ch9 | t033 | t033-0031 | L8 | 8 | gʰósteyes téh₂ logʰéyete | ok |  |
| ch10 | t005 | t005-0029 | L10 | 11 | gʷówes gʷíh₃wonti wédōr-kʷe gʷíh₃weti | ok |  |
| ch11 | t011 | t011-0012 | L2 | 8 | nu h₁yéh₂ ḱwinétsi h₁nédʰs léwks-kʷe | ok |  |
| ch12 | t006 | t006-0017 | L8 | 8 | nu-kʷe tóh₁ stóygʰoh₁ h₁éyomes | ok |  |
| ch13 | t018 | t018-0040 | L7 | 11 | méǵh₂i h₂éwsos téwe léwki bʰudʰyéh₁m̥ | ok |  |
| ch14 | t005 | t005-0005 | L12 | 8 | ḱludʰí-kʷe tód h₁áyso-kʷe tód | ok |  |
| ch15 | t011 | t011-0033 | L3 | 8 | ḱléwse-ge nos gʰóstim ph₂sdʰí | ok |  |
| ch16 | t002 | t002-0017 | L2 | 8 | nu-kʷe nos méǵh₂es h₂stéres sth₂ént | ok |  |
| ch17 | t005 | t005-0024 | L2 | 8 | nu gʷṓs h₁éḱwons-kʷe bʰéresi | ok |  |
| ch18 | t002 | t002-0017 | L3 | 8 | péh₂wr̥ bʰéwdʰt péh₂wr̥ dʰégʷʰeti | ok |  |
| ch19 | t032 | t032-0037 | L2 | 8 | ǵʰwḗres tr̥syónti tr̥syómes | ok |  |
| ch20 | t002 | t002-0001 | L9 | 8 | ḱlutóm toy h₁nómn̥ gʷéHyomes | ok |  |
| ch21 | t023 | t023-0009 | L1 | 8 | swépne-ge gʷh₂tósyo bʰréh₂ter | ok |  |
| ch22 | t033 | t033-0034 | L8 | 11 | nu nos sh₂wéns kʷékʷlos bʰoydʰéh₂m dedórḱtu | minor | perfect imperative dedórḱtu "let it see": a rare formation (cf. Vedic perfect imperatives); kept as minor |
| ch23 | t005 | t005-0015 | L3 | 11 | nu-kʷe nos deywóybʰos h₂óytons wéǵʰesi | ok |  |
| ch24 | t016 | t016-0024 | L7 | 11 | nu polh₁éwes bʰuHih₁ént nu h₂uksih₁ént | ok |  |
| ch25 | t029 | t029-0023 | L1 | 8 | nu kʷékʷlom pitséh₁ h₂linHdʰí | ok |  |
| ch26 | t033 | t033-0036 | L4 | 11 | h₁yéh₂ Hrugʰím dóru h₂élesi ḱludʰí nos | ok |  |
| ch27 | t020 | t020-0040 | L1 | 13 | ph₂ter stóygʰoh₁ h₁idʰí ph₂trṓm-kʷe stóygʰoh₁ h₁idʰí | ok |  |
| ch28 | t002 | t002-0019 | L3 | 8 | nu-kʷe tód wódr̥ lowkéyet | ok |  |
| ch29 | t005 | t005-0031 | L5 | 8 | h₂óytōm-ge nos wéǵʰtōr h₁ési | ok |  |
| ch30 | t002 | t002-0002 | L7 | 8 | nu wédʰe tóns sweh₂dú wódr̥ | ok |  |
| ch31 | t032 | t032-0011 | L2 | 8 | nu pérkʷune pérkʷum stunddʰí | ok |  |
| ch32 | b003 | b003-0143 | L1 | 8 | gʷh₂dʰí bʰór h₂éǵrōd mē dʰégʷʰh₂s | ok |  |
| ch33 | t026 | t026-0033 | L6 | 11 | nu n̥sméy priHós h₁sdʰí n̥smé mē linékʷs | ok |  |
| ch34 | t005 | t005-0036 | L10 | 8 | lewkóm-kʷe toy táwrom déh₃oh₂ | ok |  |
| ch35 | t011 | t011-0008 | L1 | 8 | nu léwke dyéw h₁regʷesyéti | ok |  |
| ch36 | t017 | t017-0032 | L1 | 11 | h₁wésu dʰénwr̥ Hwr̥dʰdʰí dʰénwr̥ mē Hrumpth₂é | ok |  |
| ch37 | t002 | t002-0003 | L7 | 8 | nu kʷséps swésōr tósyeh₂s h₁ésti | ok |  |
| ch38 | t006 | t006-0015 | L3 | 8 | dʰéǵʰom-kʷe nos méh₂ter ḱléwse | ok |  |
| ch39 | t008 | t008-0018 | L4 | 11 | h₁ésh₂r̥ toy h₂éǵroy térst ḱwónes tód liǵʰént | ok |  |
| ch40 | t005 | t005-0033 | L4 | 8 | twé kh₂nóh₂ twé-kʷe moldʰéyoh₂ | ok |  |
| co1 | t020 | t020-0015 | L14 | 8 | dyéw nos ph₂ter wékʷos ḱludʰí | ok |  |
| co2 | t023 | t023-0019 | L2 | 11 | wésmn̥ toy wésh₂er yugóm-kʷe toy spéḱyoh₂ | ok |  |
| co3 | t005 | t005-0011 | L3 | 8 | médʰyom h₂éḱmonm̥ stéygʰesi | ok |  |
| co4 | t016 | t016-0033 | L7 | 8 | ḱléwos toy ń̥dʰgʷʰitom h₁ésti | ok |  |
| co5 | t011 | t011-0006 | L3 | 12 | dyéw h₂wérs dʰéǵʰom wédos péh₃s h₂orkéyetom nos | ok |  |
| co6 | t008 | t008-0033 | L3 | 11 | déḱm̥ moy pórḱons kʷékʷlom-kʷe h₁opéyet | ok |  |
| co7 | t014 | t014-0018 | L3 | 11 | wérǵom pl̥h₁úbʰis ǵʰóstōys HeHḱú h₁ésti | ok |  |
| co8 | t005 | t005-0022 | L6 | 8 | h₁n̥gʷnís wos wédn̥su tḱéyti | ok |  |
| co9 | t002 | t002-0006 | L6 | 8 | nu kʷékʷlom sh₂wéns gʷéHyōmes | ok |  |
| co10 | t016 | t016-0033 | L1 | 11 | dyéw nos ph₂ter h₁uséwōm déh₃tor ḱludʰí | ok |  |

## For the lead

- **Not restored, by budget.** t006 (0.906) and t011 (0.908) are at the floor, so their remaining items are listed above
  and need the lead's choice.
  - t006: "go forth", "your field", "your light", "you who dwell".
  - t011: "great striker", "Perkʷunos" (vocative), "Fire" (vocative), "gods" (vocative), "our ×2"; also "Bright Dawn"
    (0009), because restoring "Dawn" alone gives a 10-syllable line.
- **Dropped by the cap, not by meter.** Some meter-repair drops were cap-driven: re-adding them broke max_lexeme_uses.
  These were undone:
  - t026: "dear radiance", "dear mistress", "my own sheep";
  - t008: "Dawn, the daughter of Sky" (t008-0006), because dʰugh₂tḗr reached 10 > 9;
  - t006: "Great gods" became "Famous gods";
  - t011: "Great Mother Earth".
- **Dual for plural.** Number changes (dual for plural in "the two horses", etc.) were left where the English was
  updated to "two".
- **Two meaning changes in this pass.** t027-0016 and t027-0025 now use a plural perfect ("they stood") where the plan
  had a dual: the cap left no dual-capable 'stand' verb (sth₂éh₁yeti and stéh₂t are both at 7).
- **Untouched files.** The modified `tests/test_*_w*.py` files (cq2 follow-up) and the `pie/export_chat.py`, t3b-002
  and tts files in the tree belong to other sessions and were not touched.
- **Scratch files.** All `zz-t005-*` and `zz-t006-*` files were deleted (they were superseded by the committed t005/t006
  repairs).
- **Full test suite** (before the test fix below): 3750 passed, 5 skipped, 2 failed, 14 errors.
  - `test_shipped_migration` fails, as expected until the lead re-approves.
  - `test_meter_exact_gate` failed because it read the live t023-0001 plan as its example of a failing charm, and that
    plan has been exact since the t023 meter repair (bbe64b3). It now reads the pre-repair plan from
    `tests/data/meter_gate_t023-0001.jsonl`, as bc388e3 did for t032-0002, and passes.
  - The 14 `tests/test_export_chat.py` setup errors are `ValueError: Tier 3b neologism share 82.2% ... exceeds the 15%
    cap`. With every Tier 3 release back at pending, almost all admitted training words are Tier 3b, so the cap check
    trips. This should clear when the lead re-approves Tier 3.
