# Tier 3 t038 review (`review-v1`, 2026-10-30)

Batch: 40 texts (hymns, prayers, ritual instructions: fire, sacrifice, libations, mead). Reviewer: claude-opus-5-5,
following docs/generation/reviewer-brief.md. Nothing under data/audits/ was read.

## Procedure

1. Packet: `make_review_packet.py t038 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items, from the `pie` field only, written to
   `docs/audits/packets/t038-blind-translations.jsonl` before any English was printed.
3. Verdicts: `docs/audits/packets/t038-verdicts.jsonl`, saved before corpus/ or the plans were opened.
   **sha256 `02a628736b030359f3fc45ca688f5b28f01c6b2ac57c3ceae384acef325f5a34`** (confirmed by resolve_review_items.py).
   Doubtful forms were checked against `Lexicon.cells()` and the lexicon. A scan of every packet token against all
   engine cells found no form the engine does not build, so the plants had to be wrong cells of real words.
4. `resolve_review_items.py t038`, then `score_review.py t038`.
5. Second pass: all 40 records read in full against planner-brief-v4. Each token was checked against its lexeme's gloss,
   including the words found with lexq rather than the slice.

## Score

| | |
|---|---|
| Plant recall | **4/5** (all 4 caught were named correctly) |
| Tier 1 judged wrong | 0/3 |
| Real items wrong | **0/20** |
| Real items minor | 2/20 as scored; both withdrawn on lookup (below), so 0 after |

Plants caught:
- 872084b1: `déywōs` (VOC.PL) used as the subject of h₃édonti. The nominative is deywṓs.
- 78f75378: `néwoybʰos dóru`, a DAT/ABL.PL adjective on an ACC.SG noun.
- 629fc071: `h₂epó h₂óweyes`, a NOM.PL after "away from". The ablative is h₂éwibʰos.
- 66b546eb: `dʰh₁sbʰós` (DAT.PL) where the English has "for the god" (singular).

One plant was missed.

Minors withdrawn after the lookup (verdicts file unchanged):
- e1cb290b / t3-t038-00007: I flagged `m̥lités` as a bare genitive for "from honey". The token is ABL.SG. Gen and abl
  have the same form here, and the case is right.
- 51cb20f4 / t3-t038-00034: I flagged `h₂én` rendered "there". The adverb's gloss is "there, yonder", so the sense is right.

## Blind back-translation

| Item | Agreement |
|---|---|
| e1cb290b | full (I read "you are born", the English has "were born": a past middle without augment, fine) |
| 872084b1 | full (a plant; the déywōs case error was not noticed in the blind pass) |
| 2a464c6a | full |
| 769c2fad | structure agrees. I misread séykʷeti as "follow"; it is "pour out", as in the English |
| 1e4d87dd | structure agrees. I guessed the rare words gʷoh₂mós ("altar") and gʷéru ("spit") wrong |
| ae399e51 | full |

There is no structural disagreement. Two items lost rare lexical items only.

## Second pass (all 40 records)

No modern or coined words. Two project reconstructions are used, gʷʰermós "warm" (Gk θερμός, Ved. gharmá-) and
the NIL theonym nébʰtus (Lat. Neptūnus, OIr. Nechtan). Both are allowed by the brief. Causatives are used in
their causative sense: lowkéyeti "light up" + OBJ, and sodéyeti "seat" + OBJ. srobʰéyeti is used as "sip", which
its gloss gives ("to be sipping"). No text has a verb of fearing. Aorist-only verbs in present-tense
description (bʰérǵʰt "rises") are gnomic aorists, as rule 8 allows. 00015 uses the inherited "Vāyav Índraś ca"
pattern correctly: a vocative plus a nominative with -kʷe.

Fixed in data/generation/plans/t038.jsonl:

1. **t038-0015 / t3-t038-00015 (wrong: addressee number).** Earth and Sky are addressed in the dual
   (dh₃tóm, h₁stóm, ph₂stóm). The plan asked h₁áyt "take (MID)" for IMP 2DU. The engine has no 2du middle, and
   it silently produced the 2PL `h₁áydʰwe`. Fix: h₁émt "to take" (pie-lex-h1emt-2), AOR IMP ACT 2DU → `h₁m̥tóm`.
   The English is unchanged and the line is still 11 syllables.
2. **t038-0006 / t3-t038-00006 (person of address).** Dawn and Fire are 3rd person for four lines. The last line
   switched to a 2DU imperative with vocatives. Fix: a 3rd-person optative wish, `h₂éwsōs nos h₁n̥gʷnís-kʷe
   h₁léwdʰins h₂léksoyh₁tām`, with the English "May Dawn and Fire protect our people!" The line is still 11 syllables.

Observation, not changed: 00002 has `dyéwi dʰǵʰémi-kʷe h₁entér`, "between" with the locative. The brief gives
the accusative for pronouns. Vedic antár takes the locative as well, so this is acceptable.

## Gate after fixes

`realize_plans.py ... --batch t038`: 40/40 realized, reject_rate 0.0, meter_exact 124/124 (1.000), max lexeme
uses 6, formula_uses 8, 201 distinct lexemes, 123 roots, 20.38 words/record. **gate PASS.**

## Engine gap (for the lead)

- **A missing cell silently becomes a different person or number.** A verb slot with `voice: MID, mood: IMP,
  num: DU` was realized as MID.IMP.**2PL** with no rejection and no warning. The token's features said 2PL, so the
  checker accepted it. The engine should reject, or mark a fallback the way `case_fallback` does, when the asked
  person or number cell is missing (2du/3du middle, 2du/3du perfect). Otherwise dual-addressee texts can lose
  agreement unnoticed.
- The 2nd-person pronoun has no dual oblique, so `usméy` (2PL) addresses a pair in 00015. This is expected, but a
  `case_fallback`-style mark would make it explicit.

Release approval is not set here. Nothing was committed.
