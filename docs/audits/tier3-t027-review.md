# Tier-3 review: packet t027 (28 items)

The batch has 40 texts: epic, challenge and farewell. The packet has 20 real items, 5 planted items and 3 Tier 1 lines (`scripts/make_review_packet.py t027 --n 20 --plants 5 --tier1 3`). The reviewer worked from handbook knowledge only (Fortson, Beekes, Ringe, LIV², Mallory & Adams, as remembered). Doubtful forms were checked against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json` and `Lexicon.cells()`, using a reverse index from each form to its cell.

Order of work, as the review-v1 brief requires:
1. The blind translation was done first, from the `pie` field only. Its tokens were glossed with the reverse index, but no English field was shown.
2. All 28 verdicts were saved: `docs/audits/packets/t027-verdicts.jsonl`, sha256 `f3caacafa241cb551b7aed77e668ba04b4952ee5475639915297af2c9576c8b8`.
3. The review was scored.
4. Only then were the flagged items resolved with `scripts/resolve_review_items.py t027`.

The packet was never diffed against the corpus, and nothing under `data/audits/` was opened.

The grades follow the t021/t023 calibration:
- **wrong**: ungrammatical, or the meaning changes.
- **minor**: ablaut, accent, notation, or a stretched sense.

## Calibration

| plant recall | real wrong | real minor | real ok | Tier 1 judged wrong |
|---|---|---|---|---|
| 4/5 (blind) | 14 | 3 | 3 | 0 |

These are the `score_review.py` figures, written to `data/audits/t027-calibration.json`. Four plants were caught:
- 1acb32dd: dréms, 2sg, with a plural subject.
- b71d41ac: instrumental ph₂wénh₁ in a string of vocatives.
- 6e87f096: LOC.SG.f ń̥dʰgʷʰiteh₂i as a predicate to neuter ḱléwos.
- 32df2538: PRF.1DU stesth₂wé for narrative 'two stood'.

The fifth plant sits in an item graded ok. The reviewer did not try to identify it.

**After the fixes (re-judged from the re-realized records):**

| real wrong | real minor | real ok |
|---|---|---|
| 0 | 9 | 11 |

## Blind back-translation

Six items were translated from the PIE alone (`docs/audits/packets/t027-blind-translations.jsonl`): 0f8701f1, c3471a67, 6b3aae19, 2104a016, 84dc906d, 66b4bd9f.
- **Agreement with the English:**
  - 5/6 match fully.
  - 2104a016 matches in part: `nókʷtm̥ h₁nédʰt` was read as 'night came on', where the English has 'he went out into the night'. The accusative of goal is legitimate, but it was not obvious.
- **Errors found blind:** in 5 of the 6 items the blind pass flagged the 3rd-singular imperatives inside 2nd-person addresses before any English was seen. That is the batch's main error (below), so the PIE really did say 'let him take', not 'take'.

## Wrong (14 real) and their fixes

**Imperatives realized as 3rd singular in 2nd-person commands.** This error is in 12 of the 14 wrong items:
- 0f8701f1 / t3-t027-00007: sléh₂gʷtu, mē HréwdHt
- f15fbbb4 / 00012: sédtu, h₁ḗdtu
- d6ab83b5 / 00020: stnéh₂tu, h₁éptu, mē stunédt
- 451e0a87 / 00036: linékʷtu, memóntu, gʷm̥yétu
- 6b3aae19 / 00029: ḱléwsetu, mē dʰrugʰyét, mē bʰéwgt, h₁éytu
- 2381ee0c / 00019: déh₃tu
- 2ae8fc44 / 00031: péh₃tu, memóntu, h₁r̥sḱétu
- bb38c9b7 / 00037: sékʷtu
- 84dc906d / 00027: léyttu
- 31804539 / 00010: tḗtḱtu, sléh₂gʷtu, mē dédeh₃t
- 66b4bd9f / 00026: dʰéh₁tu, sléh₂gʷtu
- 2d88a4f3 / 00025: gʷémtu

The same error was also in the planted items' source records (6e87f096 péh₂stu, 32df2538 dʰéh₁tu).

- **Cause:** 51 of the batch's 64 IMP verb slots carry no `person`. `clause_controller` falls back to `Agreement(person or 3)`, and it uses a VOC only when `person == "2"` is explicit. As a result, the IMP.3SG cell is realized even for 'Serpent, come forth!' (h₁ógʷʰey h₁nédʰtu) and 'Gods, protect him' (déywōs … péh₂stu).
- **Fix:** every person-less IMP slot in `data/generation/plans/t027.jsonl` now has `person: 2`. Each was checked against its English: all 51 are addressed to one hearer, so `num: SG`, except t027-0014 'Gods', which is PL.
- **Results:**
  - 2sg imperatives: sl̥h₂gʷdʰí, dh₃dʰí, dʰh₁dʰí, ph₃dʰí, ḱludʰí, ḱl̥nudʰí, gʷm̥dʰí, h₁idʰí, h₁sdʰí, memn̥dʰí; thematic sédye, ḱléwse, h₂lékse, h₁r̥sḱé.
  - Plural: ph₂sté.
  - Prohibitives: mē HréwdHs, mē dʰrugʰyés, mē bʰéwgs, mē dédeh₃s, mē stunéds, mē tréses.

**The remaining wrong items:**
- **d6ab83b5 / 00020** (also above): the dual subject bʰréh₂terh₁e sédyetām is followed by 3SG píph₃et-kʷe. The verb is now set to 3DU: píph₃etām. In the same item, 'Stand!' used stnéh₂ti 'place'. It is now sth₂éh₁ye (pie-lex-sth2eh1yeti). The same change was made in t027-0021, which had the same stnéh₂tu.
- **89df9abb / 00005:** h₁éḱwōs … pró-kʷe drémt had a 3SG verb for the plural horses. It is now 3PL: dr̥mént.
- **7b3ed0e8 / 00004:** péh₂wr̥ h₁ím dʰéh₁t had a masculine anaphor for feminine dʰwórm̥. It is now h₁íh₂m̥, as 84dc906d already has.

Other plan fixes made while there:
- t027-0009: added an overt subject, wiHrós-kʷe h₁ím wédʰet. The PIE had said the horse led the hero.
- t027-0022: added the subject h₁énos-kʷe mért. The PIE had said Sky died.
- t027-0033: 'many nights' had polh₁úm with its head pointing at the pronoun. It now agrees with nékʷtsu: pl̥h₁uyéh₂su.
- t027-0032: added the missing dative usméy ('I leave you').
- t027-0017: added h₁énos as the subject of 'came against him' (see Pronouns).

After the fixes, `realize_plans.py … --batch t027 --model claude-sonnet-5-5 --prompt-id tier3-planner-v4` reports **gate PASS**:
- 40/40 plans realized, all exact.
- reject rate 0.
- max lexeme uses 7. Two edits first pushed swós and stéh₂t to 9; they were reworked to stay within the cap.
- 26 warnings.

A plan-to-plan diff against a backup confirms that only the edits above changed: 31 plans were edited and 9 are untouched.

## Minor

- **mē + 1sg subjunctive for 'I will not …'**: 2381ee0c mē déh₃woh₂, 66b4bd9f mē moréyōh₂, 7b3ed0e8 mē bʰéwgoh₂, b71d41ac mē h₁ludʰṓh₂, and in plans t027-0015 and 0021. The engine forces mē on neg + SBJV 1st person ('let me not'), but a refusal or future wants ne. This is an engine gap (below).
- **Accent of new 2sg imperatives** (engine cells): h₁éddʰi (00012) should be *h₁ddʰí (Ved. addhí). tétḱdʰi (00010) is unaccented.
- **Omissions and stretched senses:**
  - 'wounded' (0f8701f1) and 'wild' (60aa9a1d) are not rendered.
  - gʷéru 'spit, spike' (Lat. verū) is used throughout as 'spear' beside ǵʰoysós.
  - gʰóstis is used for 'enemy' (the Lat. hostis sense; 2d88a4f3).
  - h₁opéyetām 'made reach' is used for 'gave' (66b4bd9f).
  - h₁éterōs 'the other (of two)' is used for 'the others' of many (7b3ed0e8).
  - yugóm is a double accusative for 'to the yoke' (89df9abb).
- **Non-reflexive h₁ésyo 'his'** where swós is expected: b71d41ac, 2d88a4f3. It is left in 2d88a4f3 because swós is at the lexeme cap.
- **Tier 1 lines** use their sources' notation:
  - Schleicher 1868: awis akwāsas ka.
  - Byrd: gʷah₂t, h₃rḗḱs, súHnum, wl̥nh₁to.

## Pronouns: the 26 antecedent warnings

All 26 warnings were read in the plans with clause-by-clause PIE. **24 are unambiguous**, and the heuristic fires on them for these reasons:
- **The referent is a dual or pro-drop group** that it does not count. The ḱós/h₁énos 'this one / that one' pairs are 'the two' in t027-0016 c1 and c13, 0020 c2, and 0037 c1 and c6.
- **The antecedent is more than two clauses back but clear:**
  - 0002 c8 h₁énos = the spear-bearer, h₁ím = the enemy.
  - 0004 c7 h₁éymos = the attackers.
  - 0005 c6, 0014 c6 and 0028 c11 h₁ím = the hero or son.
  - 0006 c9 h₁íns = the cattle.
  - 0011 c8 h₁íns = the three men.
  - 0020 c14, 0030 c9 and 0037 c7 h₁íh₂(m̥)/h₁ésyeh₂ey = the mother.
  - 0027 c11 h₁íh₂m̥ = the door.
- **ḱós and h₁énos keep the roles they were given earlier:**
  - 0015 c14 h₁énos = the boaster.
  - 0021 c7 ḱós = the fleeing enemy, as opposed to the pursuer h₁énos.
  - 0025 c8 h₁énos = the enemy.
- **Other cases:**
  - 0029 c4 ḱód 'this' sums up the father's precepts.
  - 0036 c0 h₁ésmey 'him' is the husband from outside the text, which opens mid-scene by design.

**Ambiguous ones, now fixed:**
- **t027-0017 c8 'He came against him, and this one fell':** the second speaker was never introduced and the subject was dropped, so 'he' could not be resolved. It is now h₁énos h₁ím próti h₁r̥sḱét ḱós-kʷe séngʷt, and the English reads 'That one came against him'.
- **t027-0016 c0 'Two stood by their horses':** non-reflexive gen. h₁éysōm (plural for a dual) had no antecedent. The possessor is dropped, and the English is now 'by the horses'. The reflexive swóysu would put swós over the cap.

Two ambiguities did not raise a warning and were fixed above: the subject-continuity slips in t027-0009 and t027-0022.

The heuristic's false-positive rate on two-speaker texts is high (about 24/26).

## Engine and brief gaps (reported, not changed)

1. **The IMP person defaults to 3SG.** In `pie/realize.py`, `clause_controller` and `verb_person_number` give an imperative without `person` 3rd person, even when a VOC is in the clause. `check_plan` does not warn. planner-brief-v4 never says an imperative needs `person: 2`. This one omission caused 12 of the 14 real wrong items. Suggested fixes: default IMP to person 2 (with the VOC's number), or reject IMP without a person.
2. **neg + SBJV 1st person always gives mē** (`neg_wish` in `realize_clause`). The planner cannot write 'I will not give' (ne + subjunctive).
3. **Accent of some 2sg imperative cells:** h₁éddʰi for *h₁ddʰí; tétḱdʰi is unaccented.
4. **The antecedent warning ignores pro-drop dual subjects and ḱós/h₁énos role tracking,** so most of its warnings in dialogue are false positives.
5. **Known gap:** there is no PRF 3DU cell; stesth₂ḗr (3pl) stands in.

## Quality after the repair

The texts still read as complete small epics and challenge or farewell scenes:
- Each has a setting, one or two speeches, and a closing deed or formula: ḱléwos ń̥dʰgʷʰitom, h₁suḱléwēs wiHrós, h₂éwsōs léwkt, the horses addressed in the vocative plural.
- The English and PIE now match apart from the minor omissions listed above.
- None is truncated.

The weaknesses are of style, not grammar:
- Almost every sentence opens with nu.
- The syntax is flat parataxis, with few relative clauses or epithet chains.
- Duel endings recur: 'they hurled their spears, and that one sank down' in t027-0015 and 0025, and close variants in 0017 and 0027.
- The lexeme caps visibly force gʷéru ~ ǵʰoysós and stéh₂t ~ sth₂éh₁yeti alternations.

Verdict: acceptable epic, coherent and in the right genre, but formulaic and flatter than t023's laments.

## Release (for the lead)

- Plant recall 4/5: meets ≥ 4/5.
- Real wrong after the fixes: 0/20, within ≤ 2/20.
- Gate: PASS.

The reviewer does not set approval.
