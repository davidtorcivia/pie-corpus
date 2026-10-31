# Re-realize pass (2026-10-31)

The pass that docs/NEXT.md "Re-realize pass due" asked for, after the Part A engine fixes of the same day.
**Release records are not touched**: every `data/generation/releases/<batch>.json` is byte-identical to HEAD
(realize_plans.py rewrote them to `pending`; they were restored with `git checkout`). The lead rebinds them.
Nothing is committed.

## What changed in the engine and data before the pass

- **APPOS number** (`pie/realize.py` realize_clause `settle`, `_check_appos`): an apposition takes its head's
  case; its number is its own when the slot (or a numeral MOD on it) sets one, otherwise its head's. The old
  check_plan rule "an APPOS takes its head's number" is gone (`_chain_num` removed). Test:
  `tests/test_recurring_gaps.py::test_apposition_keeps_its_own_number` ("the blood-price, a hundred cows" =
  kʷoynéh₂m … ḱm̥tóm gʷṓs, ACC.SG + ACC.PL). No approved record changed: plans that relied on it were rejected
  before, or (t076, t086) were rephrased in review.
- **np answers**: the mechanism already existed (`"case"` on a `"type": "np"` clause takes any case). It is now
  documented in docs/generation/planner-brief-v4.md (short answers take the case of what the question asks), and
  `plan_warnings` warns when an np clause directly after a question about a non-nominative constituent sets no
  case (`_answer_case_warnings`). Tests: `test_np_answer_takes_the_case_the_plan_sets`,
  `test_np_answer_without_case_warns`. No record changed (t086-0009 already had `"case": "ACC"`).
- **Middle 2du/3du**: Ringe 2006 p. 32 (raw/books/text/ringe/p0043.txt) says the mediopassive dual endings are
  unreconstructable (only Greek and Indo-Iranian attest them, and they disagree). So the plural fallback is kept,
  no forms are invented. realize already flagged it (`num_fallback: "du->pl"`); `plan_warnings` now warns
  (`_dual_fallback_warnings`, computed by realizing the clause, so it says exactly what realize does). Documented in
  docs/morphology.md. Tests: `test_dual_middle_falls_back_flagged_and_warns`,
  `test_no_dual_warning_where_the_dual_cell_exists`. No record changed (warning only).
- **solh₂wós 'whole, all' is an adjective**: an override `pos: "adj"` (data/lexicon/overrides.jsonl), then
  scripts/build_lexicon.py and scripts/classify_lexicon.py; the only spec change is this lexeme
  (shape:thematic → shape:thematic-adj). The lexicon round 3 Notes support it (Gk ὅλος/ὅλη, Skt sárva-/sárvā are
  adjectives). Test: `test_all_is_an_adjective`. Masculine uses (t026, t076, t079) are unchanged; t003's two
  feminine uses become solh₂wéh₂. **t088 also uses it** (two masculine plural SUBJ slots: the forms should not change,
  but t088 was left alone as instructed. t076-0026 has the identical slot shape and did not change in the scan, so t088 is not expected to change).
- **t022-0010** (pending, not approved): clause 5 "The word of two men is strong" had 'two' in the genitive,
  which check_plan now rejects. Rephrased as a condition, in the style of the law: *h₁yód dwóh₁ wiHróh₁ wékʷos
  h₂éǵetes tód stuh₂róm* "if two men say the word, that is strong". The plan's English is unchanged
  (byte-identical).

## Method

1. Every non-initial batch with a release record except t088, pilot and pilot2 (71 batches) was realized with
   scripts/realize_plans.py's own `main()` into a scratch ROOT, using each batch's model and prompt id from its
   records' `generator` fields (the batch json holds neither) and its records' own engine_version. Every record
   was compared field by field with corpus/.
2. Classes found: '?' punctuation, the 'two' rephrase, the 'all' adjective, and gloss-line drift. No PIE or token
   change outside the expected classes, and no APPOS/np/dual change (as expected, see above).
   - The '?' fix: 32 sentences in 15 batches here. The other 3 of NEXT.md's 35 are in t053, whose committed records
     already end in '?' (t053 was realized after b3016b1), so t053 does not change.
3. The 16 batches whose PIE changes were re-realized for real into corpus/ with their own command:
   `uv run python -I scripts/realize_plans.py data/generation/plans/<b>.jsonl --batch <b> --model <m> --prompt-id <p>
   --engine-version 47e9553+wip [--tier3b]`. `47e9553+wip` is HEAD plus these uncommitted changes: replace it at
   commit time if needed. Gates: all PASS as before, except t022 and t025, which still FAIL on the lexeme cap (both
   pending, not approved, as before).

## Not re-realized (reported only)

- **Gloss-line drift only (PIE, tokens and plans unchanged)**: b001–b004, t001, t002, t004–t006, t009–t018,
  t020, t021, t023, t024, t026, t027, t031–t033, t039–t041, t044, t053, t056, t059, t084. The gloss strings
  have moved since these were realized (e.g. be.carrying → carry, cry.(vocally) → weep, pay~ → punish). The
  re-realized batches below pick up the same drift. A full refresh of the glosses would need every batch re-realized.
- **t3b-003, t3b-004, t3b-005**: PIE unchanged. Only the stored `generator.plan` would differ: split_english_only
  (0266f5d, after those batches were realized) writes `"break": false` on clause 0, a no-op. Plus gloss drift in 3–5
  records each.
- **t3b-001**: the current gate rejects all 20 plans ("a Tier 3b sentence needs its own english on its first clause",
  a later brief rule), so its own command can't reproduce it. Realizing its stored plans directly gives PIE and
  tokens identical to corpus/, so nothing to re-realize. Its plans need per-sentence `english` before any future
  re-run.
- t007, t030, t038, t042, t045, t062, t064, t065, t070, t073, t076, t079, t085, t086, t087: no change at all.

## Gate-report changes in the re-realized batches (not records)

data/generation/batches/<b>.json differ only in statistics. `warnings` goes up. The two new warnings of this pass
fire only in t022 and t025 (both pending). Every other increase comes from warnings added after those batches were last
realized (e.g. the predicate-gender warning, 4080b71).
  - Dual middle: t022-0028 clause 13 (sléh₂gʷontor MID.SBJV.3PL) and t025-0008 clause 22 (h₂linHn̥tó MID.PST.3PL).
    Both are correct fallbacks, now flagged.
  - np answer case: **t025-0008 clause 2** ("Which did he seize?" "The red lamb.") and **t025-0029 clause 3** ("What
    do you give?" "Three cattle."). Both are true positives, the t086 bug in a pending batch: the answers are
    nominative where the accusative is meant. They are not fixed here, because a fix changes PIE outside this pass's
    classes. Set `"case": "ACC"` on those np clauses when t025 is reworked for its lexeme cap.
`distinct_lexemes` drops by 1–2: the reflexive swós has been exempt from the cap since 4080b71. `words_per_sentence`
drops in t003 (37.75 → 4.09) and t029 (17.77 → 4.09): the script's sentence counter changed since those runs. t022's
tokens go from 1581 to 1584 (the rephrase). No gate flips.

## Test suite

`uv run --group translator python -I -m pytest -q -p no:cacheprovider`: **1 failed, 3930 passed, 5 skipped**, exit 1.
The one failure is `tests/test_batch_release.py::test_shipped_migration`: "an approved batch whose binding went
stale" (it stops at the first one, t043: stale records and gate_report evidence). This is the expected effect of
re-realizing approved batches without rebinding their release records. It should pass once the lead rebinds the
14 approved batches here (t003, t008, t019, t028, t029, t034–t037, t043, t050, t3b-002, t3b-006, t3b-007). t022 and t025 are pending, which the test allows.

## New sha256 prefixes (for rebinding; records / plans / gate report)

| batch | records | plans | gate_report |
|---|---|---|---|
| t003 | a77c071aaf8d | 29bec60137ed | c6f5e017c46a |
| t008 | fb3632738f33 | 111c7e907556 | f99d5896c06a |
| t019 | 83e3aae73172 | 3a1921bcbbc9 | 03814803c35a |
| t022 | 114defb37ddb | b721b8888f37 | c14d31a9a8bc |
| t025 | 3dadd91cf6f5 | 748aea0bb17a | d2cc971d66b6 |
| t028 | 93a701c654a2 | 1ccfa4f6905d | 2deddde4ea9f |
| t029 | 8214c8984a66 | 926052632af5 | 5b73c28c3f61 |
| t034 | 127d85e7252d | 176214473786 | 8627a4c2194d |
| t035 | 7772ff3dfc40 | 6c395cd2637d | cbb46049d3f9 |
| t036 | aecb72737bd3 | 2dcb531a6d22 | bdc243eeca63 |
| t037 | 4c449b741bfb | be738610e5ac | a5ff66b6d553 |
| t043 | 45dc856e7ddc | 72f700c399e0 | d5f3a7148ca0 |
| t050 | 608514685d35 | d7bb5360ee4a | 793d70e8c0c7 |
| t3b-002 | 8f4fccd87bf6 | b718d3e236eb | a100174a140e |
| t3b-006 | 14c98e74ff29 | 235362376aa6 | eaf50549cde0 |
| t3b-007 | 9f1d17cc15e0 | 0e521093255d | a51b92d89ed2 |

## Changed records, per batch

### t003

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t003-00033 | solh₂wós somHósyo dʰugh₂tḗr h₁ésti. → **solh₂wéh₂ somHósyo dʰugh₂tḗr h₁ésti.**<br>solh₂wós h₂wĺ̥h₁neh₂m wésto. → **solh₂wéh₂ h₂wĺ̥h₁neh₂m wésto.** | solh₂wós is an adjective: feminine solh₂wéh₂ (lexicon override) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 13 records: 00001, 00002, 00003, 00004, 00005, 00009, 00010, 00011, 00012, 00014, 00022, 00028, 00039. Changes: pay~-IMP.3SG → punish-IMP.3SG ×6; be.carrying-IMP.3SG → carry-IMP.3SG ×4; be.carrying-IMP.2SG → carry-IMP.2SG ×2; pay~-INJ.3SG → punish-INJ.3SG; be.pointing.out-IMP.3SG → show-IMP.3SG; be.carrying-SBJV.3SG → carry-SBJV.3SG; pay~-IMP.3DU → punish-IMP.3DU; be.carrying-PST.3SG → carry-PST.3SG.

### t008

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t008-00011 | kʷíh₁ séngʷs h₂ówins ph₂sónts túH tr̥méni séngʷs. → **kʷíh₁ séngʷs h₂ówins ph₂sónts túH tr̥méni séngʷs?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t008-00013 | kʷís te h₁épt nu-kʷe te mértis kʷsépi h₁épt. → **kʷís te h₁épt nu-kʷe te mértis kʷsépi h₁épt?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 10 records: 00001, 00002, 00007, 00008, 00009, 00015, 00016, 00017, 00018, 00022. Changes: be.walking-PST.3SG → walk-PST.3SG ×2; be.carrying-IMP.2SG → carry-IMP.2SG ×2; be.carrying-PRS.1SG → carry-PRS.1SG ×2; be.walking-PST.3DU → walk-PST.3DU; be.carrying-PRS.1PL → carry-PRS.1PL; be.carrying-PST.3PL → carry-PST.3PL; be.carrying-PRS.3SG → carry-PRS.3SG; be.carrying-OPT.3PL → carry-OPT.3PL.

### t019

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t019-00015 | kʷíd méd ǵeǵónh₁e twé-kʷe gʷm̥yéti. → **kʷíd méd ǵeǵónh₁e twé-kʷe gʷm̥yéti?**<br>kʷíd dʰǵʰémi légʰyeti twé-kʷe h₂wékst. → **kʷíd dʰǵʰémi légʰyeti twé-kʷe h₂wékst?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 19 records: 00003, 00004, 00005, 00007, 00008, 00012, 00013, 00016, 00017, 00020, 00022, 00023, 00024, 00025, 00026, 00033, 00034, 00035, 00040. Changes: cry.(vocally)-PST.3SG → weep-PST.3SG ×7; be.carrying-PRS.1SG → carry-PRS.1SG ×5; cry.(vocally)-PST.3SG=and → weep-PST.3SG=and ×4; be.carrying-PST.3SG → carry-PST.3SG ×4; be.walking-PST.3SG → walk-PST.3SG ×3; cry.(vocally)-SBJV.3SG → weep-SBJV.3SG; be.carrying-PRS.2SG → carry-PRS.2SG; be.carrying-PRS.3SG → carry-PRS.3SG ….

### t022

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t022-00010 | dwóyh₁s wiHrṓm wékʷos stuh₂róm. → **h₁yód dwóh₁ wiHróh₁ wékʷos h₂éǵetes tód stuh₂róm.** | 'two' in an oblique case: plan rephrased (check_plan _check_two_oblique); gloss line also refreshed |
| t3-t022-00033 | h₁ím stunédm̥ h₁ím ne stunédm̥. → **h₁ím stunédm̥ h₁ím ne stunédm̥?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 5 records: 00004, 00018, 00019, 00020, 00029. Changes: be.carrying-OPT.3SG → carry-OPT.3SG ×2; cry.(vocally)-IMP.3SG → weep-IMP.3SG; be.carrying-IMP.3SG → carry-IMP.3SG; cry.(vocally)-PTCP.ACT.ACC.SG=and → weep-PTCP.ACT.ACC.SG=and; cry.(vocally)-PTCP.ACT.ACC.PL → weep-PTCP.ACT.ACC.PL; be.carrying-PTCP.ACT.ACC.SG → carry-PTCP.ACT.ACC.SG.

### t025

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t025-00024 | só kú tḱéyti h₁yós HeHḱúns h₁éḱwons wédʰeti. → **só kú tḱéyti h₁yós HeHḱúns h₁éḱwons wédʰeti?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 13 records: 00002, 00004, 00008, 00009, 00011, 00012, 00013, 00015, 00017, 00018, 00019, 00022, 00023. Changes: cry.(vocally)-PST.3SG=and → weep-PST.3SG=and ×6; be.carrying-IMP.2SG → carry-IMP.2SG ×2; cry.(vocally)-SBJV.1PL → weep-SBJV.1PL; be.carrying-OPT.3SG → carry-OPT.3SG; be.carrying-PST.3SG → carry-PST.3SG; be.carrying-PTCP.ACT.NOM.PL → carry-PTCP.ACT.NOM.PL; be.carrying-PTCP.ACT.NOM.SG → carry-PTCP.ACT.NOM.SG; be.carrying-PRS.2SG → carry-PRS.2SG ….

### t028

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t028-00029 | kʷíd swésor h₁ḗdti ne-kʷe pléh₁dʰeti. → **kʷíd swésor h₁ḗdti ne-kʷe pléh₁dʰeti?**<br>kʷíd wódr̥ píph₃eti mért-kʷe. → **kʷíd wódr̥ píph₃eti mért-kʷe?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t028-00032 | kʷís wiHrṓy wésmn̥ dédeh₃ti gʷíh₃weti-kʷe. → **kʷís wiHrṓy wésmn̥ dédeh₃ti gʷíh₃weti-kʷe?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t028-00035 | kʷíd swésor gʷm̥sḱéti swóm-kʷe stérh₃mn̥ ne linékʷti. → **kʷíd swésor gʷm̥sḱéti swóm-kʷe stérh₃mn̥ ne linékʷti?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t028-00037 | kʷís ph₂wéns ǵn̥h₁yétor ḱóymōd-kʷe úd h₁éyti. → **kʷís ph₂wéns ǵn̥h₁yétor ḱóymōd-kʷe úd h₁éyti?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t028-00039 | kʷíd népot h₂nḗr dédeh₃ti h₁íd-kʷe kapyéti. → **kʷíd népot h₂nḗr dédeh₃ti h₁íd-kʷe kapyéti?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 5 records: 00004, 00005, 00010, 00021, 00033. Changes: be.carrying-PRS.3SG → carry-PRS.3SG ×2; be.carrying-PRS.1SG → carry-PRS.1SG; be.carrying-PST.3SG → carry-PST.3SG; cry.(vocally)-PST.3SG → weep-PST.3SG; cry.(vocally)-PST.3SG=and → weep-PST.3SG=and; cry.(vocally)-PRS.3SG → weep-PRS.3SG.

### t029

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t029-00016 | gʷnéh₂s wókʷm̥ ḱléwsete kʷíd gʷḗn tḗtḱt tónom tḗtḱt. → **gʷnéh₂s wókʷm̥ ḱléwsete kʷíd gʷḗn tḗtḱt tónom tḗtḱt?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 5 records: 00004, 00005, 00006, 00022, 00031. Changes: cry.(vocally)-PST.3SG=and → weep-PST.3SG=and ×2; be.carrying-IMP.2SG → carry-IMP.2SG ×2; be.carrying-IMP.2PL → carry-IMP.2PL; cry.(vocally)-PRS.3SG → weep-PRS.3SG.

### t034

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t034-00016 | h₁ógʷʰis deywṓy wéwket kʷós túH. → **h₁ógʷʰis deywṓy wéwket kʷós túH?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 5 records: 00007, 00017, 00025, 00029, 00038. Changes: cry.(vocally)-PST.3SG → weep-PST.3SG ×3; cry.(vocally)-PST.3PL → weep-PST.3PL ×2.

### t035

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t035-00023 | kʷíd ḱósyeh₂i sporéh₂i h₁ésti wéwket h₁suh₁éḱwos. → **kʷíd ḱósyeh₂i sporéh₂i h₁ésti wéwket h₁suh₁éḱwos?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 3 records: 00012, 00018, 00036. Changes: cry.(vocally)-PRS.3PL → weep-PRS.3PL; cry.(vocally)-PST.3SG=and → weep-PST.3SG=and; cry.(vocally)-PRS.3SG → weep-PRS.3SG.

### t036

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t036-00012 | kʷís h₁íh₂m̥ h₂élēti h₁yód méromesdʰh₂. → **kʷís h₁íh₂m̥ h₂élēti h₁yód méromesdʰh₂?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t036-00018 | h₂nér h₂éǵros h₁idʰé h₂susyéti ḱóymom linékʷomes. → **h₂nér h₂éǵros h₁idʰé h₂susyéti ḱóymom linékʷomes?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t036-00019 | méh₂ter moy wr̥h₁dʰí kʷíh₁ wiHróm ǵn̥néh₃oh₂ h₁yós dʰrugʰyéti. → **méh₂ter moy wr̥h₁dʰí kʷíh₁ wiHróm ǵn̥néh₃oh₂ h₁yós dʰrugʰyéti?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t036-00025 | kʷís túH kʷósyeh₂s-kʷe tewh₂téh₂s h₁ési. → **kʷís túH kʷósyeh₂s-kʷe tewh₂téh₂s h₁ési?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t036-00031 | ḱéywe moy wr̥h₁dʰí kúdʰe tḱéysi. → **ḱéywe moy wr̥h₁dʰí kúdʰe tḱéysi?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t036-00040 | ǵérh₂ont kʷyéh₁tim h₂isḱṓmes kóryom-wē h₁éyomes. → **ǵérh₂ont kʷyéh₁tim h₂isḱṓmes kóryom-wē h₁éyomes?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 2 records: 00002, 00011. Changes: cry.(vocally)-PRS.3PL → weep-PRS.3PL; cry.(vocally)-INJ.2SG → weep-INJ.2SG.

### t037

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t037-00037 | sékʷt ḱód swópniyom h₁ést deywósyo-wē dṓm h₁ést. → **sékʷt ḱód swópniyom h₁ést deywósyo-wē dṓm h₁ést?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 7 records: 00010, 00015, 00017, 00021, 00025, 00028, 00040. Changes: cry.(vocally)-PST.3SG → weep-PST.3SG ×5; cry.(vocally)-PST.3SG=and → weep-PST.3SG=and; cry.(vocally)-PST.3PL → weep-PST.3PL.

### t043

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t043-00028 | h₃rḗǵs ǵn̥h₃róm prḗḱst kʷíd ḱuh₁róm. → **h₃rḗǵs ǵn̥h₃róm prḗḱst kʷíd ḱuh₁róm?** | '?': a clause of the sentence has question (realize, b3016b1) |

### t050

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t050-00006 | kʷís túH ne te ǵn̥néh₃mi. → **kʷís túH ne te ǵn̥néh₃mi?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t050-00023 | tr̥h₃ént te h₁ésh₂r̥ toy ǵʰóstoy h₁ésti. → **tr̥h₃ént te h₁ésh₂r̥ toy ǵʰóstoy h₁ésti?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t050-00031 | kʷís ǵérh₂ont túH wésmn̥ toy dért. → **kʷís ǵérh₂ont túH wésmn̥ toy dért?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t050-00033 | kʷíd gʷéh₂esi tósmōd kʷis h₂óǵmōd ne nést. → **kʷíd gʷéh₂esi tósmōd kʷis h₂óǵmōd ne nést?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t050-00036 | kʷís túH kʷíd-kʷe swéh₂m tewh₂téh₂m linékʷs. → **kʷís túH kʷíd-kʷe swéh₂m tewh₂téh₂m linékʷs?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 1 records: 00014. Changes: cry.(vocally)-INJ.2SG → weep-INJ.2SG.

### t3b-002

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t3b-002-00016 | stéygʰesi neh₂wéh₁-wē h₁éysi. → **stéygʰesi neh₂wéh₁-wē h₁éysi?** | '?': a clause of the sentence has question (realize, b3016b1) |

### t3b-006

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t3b-006-00031 | kéh₂nmn̥ memónth₂e h₁yód dʰǵʰyés séngʷʰome. → **kéh₂nmn̥ memónth₂e h₁yód dʰǵʰyés séngʷʰome?** | '?': a clause of the sentence has question (realize, b3016b1) |
| t3-t3b-006-00039 | h₃rḗǵs wéwket kʷís túH. → **h₃rḗǵs wéwket kʷís túH?** | '?': a clause of the sentence has question (realize, b3016b1) |

Gloss line only (PIE and tokens unchanged; the gloss lexicon has moved since this batch was realized): 2 records: 00004, 00028. Changes: cry.(vocally)-PST.3SG → weep-PST.3SG; cry.(vocally)-PRS.3SG → weep-PRS.3SG.

### t3b-007

| record | old PIE → new PIE (changed sentences only) | why |
|---|---|---|
| t3-t3b-007-00009 | h₁yód h₂nḗr méreti kúdʰe h₁éyti. → **h₁yód h₂nḗr méreti kúdʰe h₁éyti?** | '?': a clause of the sentence has question (realize, b3016b1) |
