# Tier 3 batch t034, second calibrated review (review-v1, 2026-10-30)

A second, independent review. The first review (docs/audits/tier3-t034-review.md) caught 3/5 plants, below the 4/5
release rule. Procedure: docs/generation/reviewer-brief.md, with a fresh packet. I did not read anything under
data/audits/, and I did not open the first review's packet, verdicts or report before my verdicts were saved.

## Order of work and hashes
1. Packet: `make_review_packet.py t034 --n 20 --plants 5 --tier1 3 --seed 2` (28 items: 20 real, 5 planted, 3 Tier 1).
   `docs/audits/packets/t034-packet.jsonl` sha256 `e501af11765136bbfdbbadb5ae4a78f4430d21be9093ff2150cf91ba5bb81b82`.
2. I printed only the `pie` fields and wrote a blind back-translation of 6 items:
   `docs/audits/packets/t034-blind-translations.jsonl` (sha256 `540015db9965e93b28856cb3fe1e868339681f44b38b6066394a2448344ad85d`).
3. Then I read the English and checked every token with a reverse index over `Lexicon.load().cells()`
   (adjectives in all three genders) and closed_class.json. Verdicts:
   `docs/audits/packets/t034-verdicts.jsonl`, **sha256 `bf899549152b397f7472b5d94802fa42e489be230e31915e9dfd1b7d2388fa4d`**.
   This file was saved before I opened corpus/, the plans or the first review.
4. `resolve_review_items.py t034`, then `score_review.py t034`.

## Calibration (score_review.py)
| measure | value |
|---|---|
| plant recall | **5/5 (1.0)**, all 5 named exactly |
| Tier 1 judged wrong | 0/3 |
| real items wrong | 0/20 (upper bound 0.0) |
| real items minor | 2/20 |

The five plants, each judged wrong, with the planted form named:
- 994a6cbb: h₂yuHn̥ḱósyo (GEN.SG) where it should agree with DAT.PL h₂nr̥bʰós.
- 91127f7c: déywe (VOC) as the subject of "the god went away".
- c5fdd2d0: moréyowe (PST.1DU) for "the hero … killed it" (3SG).
- 0faa04d1: gʷʰn̥tóm (PST.2DU, or the participle) for "Who slew …?" (3SG gʷʰént).
- 687a2527: h₁és (2SG) for "There was a young man" (3SG h₁ést).

## Blind back-translation agreement
All 6 items (994a6cbb, a14cf6a9, 9536c3d2, 4ab78b5c, b49b404d, 2f18e3a8) match the English in substance. The differences:
- 994a6cbb: I read the opening as "told the young warriors' (story)", following the planted GEN.SG.
  The PIE was right and I had misread it.
- 4ab78b5c, b49b404d: I read sepelyé- as "bury" (Lat. sepeliō). The lexicon gloss is "honor" (Ved. saparyáti), which the English follows.
- 9536c3d2: I read somHós as "the same"; "alone" is the lexicon's second sense.
- 994a6cbb: I was unsure about h₂roh₁dʰéye- "spoke". The confirmed gloss is "to speak" (Celtic, Germanic).

## Real packet items: minor (both fixed)
- **24965c01 = t3-t034-00022.** `mē tréses pós h₂wérst` was an aorist indicative ("afterwards it rained") in the father's prediction.
  It also repeated the next clause's `nu h₂wérst` word for word.
  - Fix: aorist subjunctive, `pós h₂wérseti`.
  - English: "afterwards it will rain".
  - The first review had left this as minor.
- **f3a94c4f = t3-t034-00014.** The English said "He struck it once with a spear", but the PIE has no word for "once".
  dwís and trís render "twice" and "three times", and the lexicon has no "once" adverb.
  - Fix: the English now reads "He struck it with a spear".

## Second pass: the first review's fixes and what it missed
I read all 40 records (PIE, English and token features) after resolving.

**The first review's fixes hold:**
- 00020 now has a single wheel and yoke, as the English says.
- 00006: lóygeti is singular.
- 00008: deywóm.
- 00012: 2sg throughout.
- 00026: "sang of him".
- 00033: 3rd-person optative.
- 00036: 2sg.

One note on 00010: ḱóm is the deictic ACC.SG "this one", so the old English "Take this" was accurate. The change to "Take it" does no harm.

**Missed by the first review (LOC used for motion, the same kind of error as the plant it missed):**
- **t3-t034-00008**, "It ran out over the fields": the PIE had `h₂éǵroysu upér tékʷet`, a LOC.PL with a verb of motion.
- **t3-t034-00025**, "The rivers flowed up over the fields": the PIE had `déh₂nuh₂ úd h₂éǵroysu upér sréwet`, also LOC.PL.
- I judge both minor, not wrong, because upér + LOC can be read as the place where something flows ("on the fields"). But the English describes water spreading onto the fields, which is a goal. The plan
  role was LOC in both. Fixed to GOAL: `h₂éǵrons upér tékʷet` and `déh₂nuh₂ úd h₂éǵrons upér sréwet`.
  (In my verdicts I noted the 00025 form on its planted copy c5fdd2d0.)
- 00014 ("once") and 00022 (tense) are listed above.

**Checked and accepted:**
- Every other goal is accusative: dṓm drémt, déh₂nu tékʷome, móri h₁n̥dó, h₂ewlóm h₁n̥dó ní h₁éyt, sóh₂wl̥ upó, léwkm̥ úd,
  pótim h₂ew, péh₃tleh₂ h₁n̥dó, h₁suḱléwesm̥ gʷémt.
- Every LOC is static: lie, sit, hide, shut in, "above the house".
- Agreement holds throughout: neuter plural subjects with singular verbs, duals (stéygʰetām, gʷh₂tā́m,
  h₁stā́m, bʰuHtā́m, méwdetām), and pronoun gender against its antecedent (h₁íh₂ for wédōr, h₁íd for soksóm, pérwr̥, gʰréh₁mn̥, spélom; h₁ésyeh₂s
  for tewh₂téh₂).
- 00031: dʰéh₁si "in a sacred place" uses the lexicon's second sense of dʰéh₁s.
- Still minor and left as is (as in the first review): 00010 tḗtḱt "made", and the -kʷe on the vocative in 00036.

## Counts before and after the fixes
- Real packet items: 0 wrong and 2 minor before; 0 wrong and 0 minor after.
- Whole batch: no wrong records. Minor and fixed in this pass: 00008, 00014, 00022, 00025.
  Minor and left: 00010 (tḗtḱt; oak gender, an engine question), 00036 (the vocative with -kʷe).

## Fixes made (plans only; data/generation/plans/t034.jsonl)
| plan | change |
|---|---|
| t034-0008 clause 6 | h2egjros role LOC → GOAL |
| t034-0025 clause 12 | h2egjros role LOC → GOAL |
| t034-0014 clause 1 | English: "once" removed (clause and text) |
| t034-0022 clause 9 | h2werst mood IND → SBJV; English "afterwards it will rain" |

Re-realized with `realize_plans.py data/generation/plans/t034.jsonl --batch t034 --model claude-opus-5-5 --prompt-id tier3-planner-v4`:
- 40/40 realized, with 0 rejects and all 40 exact.
- meter_exact 80/80.
- max_lexeme_uses 9 ≤ 9. The token count is unchanged at 1713, so the cap did not move.
- formula_uses 23.
- **gate PASS.**

Only the four records above changed.

## Engine/brief findings (reported, not fixed)
1. **The prohibitive mē is tagged as `closed:particle:ne`.** In the tokens of 00011, 00022 and 00034, the form mē carries
   lex_id `closed:particle:ne`. The cause is pie/realize.py:1566, which builds the particle as `Word("mē" if … else "ne", "closed:particle:ne", …)`.
   closed_class.json lists mē as its own particle, so the exporter and validator see a ne token with the form mē.
   A separate `closed:particle:mē` id (or a feature) would keep the two apart.
2. **Planner guidance on motion over a surface.** Planners reach for LOC with upér/úd when the English says "flowed over the fields".
   A one-line note in planner-brief-v4 would help: a verb of motion with "over/onto/into" takes GOAL (accusative).
   The engine cannot catch this, since both cases are grammatical PIE.
3. Agreed with the first review: pie-lex-perkus is masculine, while the usual reconstruction is feminine.

The release approval is not set; the lead decides.
