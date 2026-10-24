# Plan edits made to satisfy the checker: audit (2026-10-24)

David found that `check_plan`, `realize` and the exporter each worked out grammatical properties on their own,
so they disagreed. Plans were then edited to satisfy the checker's wrong answer. The worst case was the
vocative rule: `check_plan` dropped the vocative marked `"and": true` and compared the verb with the first
singular addressee only. So 'Sky and Earth, hear me!' passed with IMP.2SG ḱludʰí and failed with the correct
dual ḱlutóm.

The engine is now fixed (branch `fix/grammar`). Agreement is computed once, in `clause_controller` and
`group_agreement`. Admissible cells are worked out once, in `Lexicon.admissible_cells`. check_plan, realize,
plan_warnings, inflection_tasks and token_variants all use these. This file covers every plan edit made since
the agreement rule came in (db82a83) and the doubled-enclitic and pronoun rules came in (764386f). For each
edit it says whether the edit fixed a real error or was **induced** by a checker defect. Induced edits are
reverted.

Method: I ran `git log -p` over `data/generation/plans/` and `data/tier2/plans/` from db82a83 to the branch
point (569dedd), then compared each plan clause by clause (old slots against new). The `*.initial.jsonl`
drafts are not edited. For each kept edit I checked the plan's English, and for the doubled enclitics I checked
the realized words of the old clause.

## Commits that edited stored plans

| commit | what | plan edits |
|---|---|---|
| db82a83 | agreement rule: explicit verb person/num vs subject and vocative | 19 clauses (7 subject, 12 vocative) |
| 764386f | blocklist, noun-used adjectives with gender, doubled-enclitic rule, pronoun-antecedent warnings, t020 review | 102 slot edits in 82 clauses |
| 1a2f2a1, d417bea | Tier 2 copula workarounds turned into nominal sentences, np utterances and apposition (David's review) | 14 Tier 2 plans; requested by David, not checker-induced; kept |
| 913ce54, a8cfff7, f014997, 5ad9e65, fedbddd | new Tier 2 branch-pair lines | additions only |

## db82a83: the agreement rule

### Reverted: 11 coordinated vocatives (induced)

Each clause addresses two singular conjuncts (X Y-kʷe). The checker dropped the second conjunct, saw one
singular addressee and demanded a singular verb, so the correct dual was changed to singular. The verb is now
the dual again. Where the earlier stored version had a plural, the dual replaces it, because the 2du cell exists
for every one of these verbs and two addressees take the dual (Fortson §8.16). Under the shared logic, the
singular in each of these clauses is now an error.

| plan | clause | addressees | verb | before db82a83 | after db82a83 | now |
|---|---|---|---|---|---|---|
| t001-0009 | 13 | ph₂tḗr, méh₂tēr-kʷe | h₂lékseti IMP | 2PL | 2SG | 2DU h₂léksetom |
| t008-0004 | 1 | pótis, pótnih₂-kʷe | gʷeh₂- AOR IMP, neg | 2DU | 2SG | 2DU (injunctive) |
| t008-0020 | 0 | dyḗws, dʰéǵʰōm-kʷe | ḱlew- AOR IMP | 2DU | 2SG | 2DU ḱlutóm |
| t008-0022 | 0 | dyḗws, dʰéǵʰōm-kʷe | ḱlew- AOR IMP | 2DU | 2SG | 2DU ḱlutóm |
| t008-0024 | 4 | dyḗws, dʰéǵʰōm-kʷe | ḱlew- AOR IMP | 2DU | 2SG | 2DU ḱlutóm |
| t009-0018 | 13 | údros, bʰérǵʰus-kʷe (m) | powǵéyeti IMP, neg | 2DU | 2SG | 2DU (injunctive) |
| t013-0033 | 0 | ph₂tḗr (and), méh₂tēr | ḱlew- IMP | 2PL | 2SG | 2DU ḱlutóm |
| t016-0039 | 0 | dyḗws, dʰéǵʰōm-kʷe | ḱlew- AOR IMP | 2DU | 2SG | 2DU ḱlutóm |
| t018-0038 | 0 | wĺ̥kʷos, bʰṓr-kʷe | bʰewg- IMP | 2PL | 2SG | 2DU bʰugtóm |
| t019-0018 | 15 | dyḗws, méh₂tēr-kʷe | dedeh₃ti PRS IND | 2PL | 2SG | 2DU dedh₃tés |
| t019-0020 | 2 | h₂énh₁mos, h₁n̥gʷnís-kʷe | dremt AOR IMP | 2DU | 2SG | 2DU dr̥mtóm |

These are the eleven corpus clauses David counted (t3-t008-00020 'Sky and Earth, hear me!' among them). The
lead's re-realization will produce the dual.

### Kept: 8 real fixes

| plan | clause | edit | why it is real |
|---|---|---|---|
| b003-0020 | 1 | gʷówes PL + verb 3SG → num dropped (3PL) | the cattle are plural and not neuter: 'gʷówes trémt' was the error David found |
| t006-0040 | 3 | h₂ékʷeh₂ PL (f.) + IMP 3SG → num dropped (3PL) | a feminine plural subject takes a plural verb |
| b003-0129 | 0 | h₂égōr PL (n.) + OPT 3PL → num dropped (3SG) | the engine treats a neuter plural as a collective (singular verb). The realizer already forced 3SG, so the output did not change |
| b003-0231 | 1 | the same, h₂égōr PL + AOR 3PL | same as b003-0129 |
| t011-0001 | 7 | wédōr PL (n.) + AOR 3PL → num dropped | same as b003-0129 |
| t011-0020 | 3 | wédōr PL + AOR 3PL | same as b003-0129 |
| t011-0022 | 2 | wédōr PL + AOR 3PL | same as b003-0129 |
| t019-0035 | 3 | h₁léwdʰis VOC SG + IMP 2PL → 2SG ('Wake up, people!') | the addressee is a singular collective noun. A plural verb here would be agreement by sense, which the engine does not model; the singular is grammatical. The alternative (VOC num PL 'peoples') changes the meaning |

## 764386f: post-integration cleanup

All of these edits are kept. None was induced by a checker defect: the doubled-enclitic rule is correct for
every clause it fired on, and the pronoun edits follow each plan's English.

- **Noun-used adjectives given the gender of their referent (61 slots)**, after five words were reclassified
  as adjectives. The rule that an adjective used as a noun names its gender is correct. The genders chosen
  follow the referent:
  - sḿ̥teros: 16 slots (b001-0034, -0055, -0058, -0211, -0212, -0213; genealogy-018; t006-0028 ×2;
    t007-0026 ×2, t007-0037 ×2; t012-0010; t012-0036 ×2)
  - dʰegʷʰrós: 7 slots (b001-0179, -0207, -0208 n. 'the burning'; t003-0040 ×4 m.)
  - mr̥wós: 14 slots (b003-0164, -0176, -0189, -0213, -0217, -0226; b004-0008, -0033, -0070, -0081, -0174;
    t003-0015 ×2; t018-0033)
  - néḱus: 2 slots (pilot law-002, law-017)
  - ḱuh₁rós: 8 slots (t009-0003)
  - ḱéywos: 14 slots (t009-0023; t010-0009 ×2, -0019, -0021, -0026, -0027; t012-0002, -0007, -0036 ×2;
    t018-0016; t020-0007 ×2)
- **Blocked lexemes replaced (14 slots).** ǵʰéyos became h₁éḱwos in 12 pilot/pilot2 slots (fable-002, -005,
  -009, -019, -021, -028, -036, -039 ×2, -043, riddle-009, -020). kʷetwóres became closed:numerals/4 in
  b003-0065 and b003-0203. These lexemes are on the blocklist, which is a lexical decision, not a checker
  defect.
- **Doubled enclitics (10 clauses), enclitic → stressed:** t005-0013 c1, t005-0024 c6, t008-0002 c2,
  t008-0006 c2, t008-0011 c2, t008-0022 c10, t008-0039 c3, t016-0033 c11, t019-0029 c6, t019-0039 c1. I
  realized each old clause with the current engine. Every one really put two enclitics of one person and
  number side by side: `toy te` (GEN + ACC 2SG) in seven clauses, `moy me` in two, `nos nos` in t016-0033.
  This is the t019/t020 review finding. The counting rule (`_doubled_enclitics`, the realizer's own words)
  had no defect.
- **Pronoun gender and number (16 clauses), each checked against the English:**

  | plan | clause | edit | antecedent |
  |---|---|---|---|
  | b002-0239 | 1 | tóm m → n | the vow, h₁éh₁ugʰos (n.) |
  | b004-0042 | 0 | h₂ówis OBJ → PL | 'protect the sheep … not seize *them*' |
  | t004-0040 | 2 | n → m | the field, h₂éǵros (m.) |
  | t005-0037 | 10 | f → m | the serpent, h₁ógʷʰis (m.) |
  | t007-0030, -0036, -0039 | 2, 8, 6 | PL f → m | the plan's 'sheep' are moysós 'rams' (m.) |
  | t010-0012 | 6 | PL → DU | brother and sister |
  | t010-0036 | 5 | m → n | the ploughed field, h₂erh₃tós used as a neuter noun (h₂erh₃tóm) |
  | t013-0039 | 2, 5 | PL m → f | h₂óweyes, feminine in the lexicon |
  | t014-0019 | 5 | PL → DU | the two cattle of the previous clause |
  | t020-0018 | 2 | 'their' PL → DU | the two wives |
  | t020-0031 | 14 | h₁íns m PL → h₁íd n SG | the flock (t020 review) |
  | t020-0020 | 6 | POSS 1PL deleted | doubled possessive (t020 review) |
  | t020-0033 | 9 | 'your' → PL | plural command (t020 review) |
  | t020-0039 | 2 | f SUBJ inserted | 'she said to him' (t020 review) |

## Status of every stored plan under the shared logic

I ran `check_plan` and `realize` on every plan in `data/generation/plans/*.jsonl` and `data/tier2/plans/*.jsonl`
(4,391 plans, `.initial` drafts included). The baseline was the engine at 569dedd, run on the same plans.

**Current plans (not `.initial`)**

- No plan that passed before has different output, apart from the 11 reverted clauses, which now realize the
  dual.
- No plan newly passes.
- **12 plans newly fail (13 clauses).** In each, the verb has an explicit plural num and the subject is dual:
  two coordinated singulars, or a noun or pronoun with num DU. The dual cell exists. The old checker accepted
  a plural for any dual subject. The shared rule allows the plural only where the dual cell is missing (the
  middle and the perfect). Under the shared logic these are agreement errors. I did not edit them: the rule's
  strictness is the lead's call. The fix in each case is to set the verb's num to DU, or drop it.

  | plan | clause | subject | English |
  |---|---|---|---|
  | b001-0139 | 0 | wéyHs, séǵʰos-kʷe | Strength and might were in him. |
  | b002-0238 | 0 | h₂ówis, moysós-kʷe | May the sheep and the ram be satisfied. |
  | b003-0077 | 0, 1 | two rivers (DU); tóh₁ (DU) | The two rivers carry water, and they swell. |
  | b003-0101 | 0 | ph₂tḗr, méh₂tēr-kʷe | May the father and the mother live … |
  | b003-0206 | 0 | swésorh₁e (DU) | The two sisters went to the border … |
  | b004-0059 | 0 | dyḗws, dʰéǵʰōm-kʷe | May the sky and the earth hear the oath. |
  | t001-0008 | 0 | wiHrós, yemHós-kʷe | Man and Twin dwelt in darkness. |
  | t001-0029 | 2 | Hyudʰsmós, ǵm̥rós-kʷe | A warrior and his son-in-law grasped spears … |
  | t002-0013 | 0 | dyḗws, dʰéǵʰōm-kʷe | Sky and Earth are the parents of the gods. |
  | t014-0036 | 6 | moysós, kápros-kʷe | May they live … |
  | t016-0009 | 13 | dʰéǵʰōm, dyḗws-kʷe | (the twin's body becomes the world) |
  | t016-0030 | 1 | his wife and his sister | His wife and his sister cried out … |

**`.initial` drafts (not edited)**

- 13 newly fail, on the same rule as above (b001-0139, b002-0238, b003-0077, -0101, -0206, b004-0059, -0071,
  t001-0008, -0029, t002-0013, t013-0013, -0039, t014-0036).
- 6 newly pass: t008-0004, -0020, -0024, t009-0018, t016-0039, t019-0020. These are the dual vocatives the old
  checker rejected.
- 6 change only their error text:
  - t001-0009, t013-0033, t018-0038 and t019-0018 still have their original 2PL, and the addressee error
    now names the dual;
  - t008-0022 now fails only on its doubled enclitic;
  - in t020-0028 the 'form not generated' message now names the lexeme.
- One output changed, t019-0012 clause 20 ('Sun, you are great'). Its verb has no person, so it realizes as
  3SG. The predicate adjective no longer agrees with the vocative: only a 2nd-person verb makes the addressee
  its subject. In the current t019, the verb has person 2.

## Not decidable from the plan: several same-role slots without "and"

Several VOC or SUBJ slots without "and" can mean two different things:

- one referent named twice: dyḗws ph₂tḗr 'Father Sky'
- several referents in asyndeton: 'Father, Mother, give us good things' (t016-0016)

Likewise, four slots with one -kʷe can be four referents or two epithet pairs: dyḗws ph₂tḗr dʰéǵʰōm méh₂tēr-kʷe
(t004-0005, t008-0019, t008-0025, t011-0006, sky-father-001).

The shared logic reads such slots as one referent by default. Accordingly, with three or more coordinated
singular slots, each slot is one referent. An explicit verb number can pick the other reading (Agreement.alt):
the dual for two pairs or for an asyndetic pair. A number that no reading allows is still an error, such as a
singular verb for a coordinated group.

Without this, the first version of the shared rule rejected 7 correct dual verbs. The old checker had silently
skipped these clauses, because more than one vocative remained after it dropped the conjunct marked "and".

t002-0013 clause 6 ('Father Sky and Mother Earth, hear us', 4 slots, no -kʷe, 2PL) passes as a possible
4-referent reading, though it means two. Writing epithets as APPOS makes the count explicit.
