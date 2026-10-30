# Tier 3b review: t3b-005 (review-v1 adapted to Tier 3b, 2026-10-30)

40 chat dialogues between `user` and `model` on food, feasts, guests, gifts and trade, planned under
`planner-brief-3b.md` v3 (`tier3b-planner-v3`). Release approval is the lead's: `data/generation/releases/t3b-005.json`
is left untouched.

## Procedure

Calibrated, as in t3b-002. The packet came from `make_review_packet.py t3b-005 --tier tier3b --n 20 --plants 5 --tier1 3`
and has 28 items: 20 real, 5 planted and 3 Tier 1.

1. **Blind back-translation.** I translated 6 items from `pie` alone, before reading any English:
   `docs/audits/packets/t3b-005-blind-translations.jsonl` (sha256 `2ef8e125…a81d2e8`).
2. **Verdicts.** All 28 items were judged before I opened `corpus/tier3b/` or the plans:
   `docs/audits/packets/t3b-005-verdicts.jsonl`, sha256
   `6c23e0446ae2678a9a596ad3716f0fe39fb5e6e4f4876758343b7b47a532018b`. `resolve_review_items.py` printed that same hash.
   Nothing under `data/audits/` was read.
3. **Score.** Ran `score_review.py`. Its result is in `data/audits/t3b-005-calibration.json`.
4. **Second pass.** I read all 40 records in full, sentence by sentence: speaker, PIE, the English for each sentence,
   and the gloss. This pass checked brief §5 (character), archaic-first, whether the English matches the PIE, and
   whether each turn answers the one before it.
   - Five records appeared in the packet only in planted form: 0011, 0014, 0022, 0035 and 0039.
   - Verdicts on those five come from this pass alone and are **uncalibrated**.

## 1. Counts

| | before fixes | after fixes |
|---|---|---|
| Plant recall | **5/5** (all 5 named) | — |
| Tier 1 judged wrong | 0/3 | — |
| Real packet items wrong | 0/20 | 0/20 |
| Real packet items minor | 3/20 | 3/20 (gnomic-aorist and goal-accusative notes; not changed) |
| Second pass: records wrong | 1/40 (0022) | 0/40 |
| Second pass: records with minor issues | 7 | 5 |
| Character (§5) violations | 1 (0022, see below); 0 machine-identity lines | 0 |
| Gate | PASS | PASS |

Plants caught (verdict wrong, and the planted form named in the issue):
- 3649a822: h₂életes, PRS 2DU/3DU for 1PL h₂élomes ("We feed him").
- 3f2e75c5: widmé, 1PL for 1SG ("I do not know").
- 6ac9850b: ph₂tr̥bʰós, DAT/ABL.PL for NOM.SG ph₂tḗr.
- 5bfa4ab2: sh₂l̥bʰós, DAT/ABL.PL for NOM.SG "salt".
- cd8f27d8: pótn̥yeh₂su, LOC.PL for NOM.SG pótnih₂.

Blind-translation agreement:
- **3/6 items agree fully** with the plan English: 54961dcc, 26a9297c and 9c59d49e.
- **3 items agree in part:**
  - **16ec9fad:** I read kʷíd as "what (gifts)"; the plan has "why". Both readings are legitimate.
  - **3f2e75c5:** I read péḱu as "cattle", and the English has "money". This mismatch led me to the one real wrong record
    (below). The item also carries a plant: I translated the planted 1PL widmé without flagging the person.
  - **cd8f27d8:** the planted LOC.PL left the sentence's sense unclear; I put that in `uncertain`.
- Senses I did not recognise blind were h₁opéye- "make reach, give" and h₁áyto (MID) "received".

## 2. Wrong items and fixes

**0022, "Wool for money?" (second pass; also the record behind plant 3f2e75c5).**
- **What it said.** The user offered "money": `pie-neo-money`. The model answered "Money? I do not know money."
- **Why it is wrong.** `pie-neo-money` is a calque, and its form is **péḱu**, identical to the inherited péḱu
  "livestock, cattle". So the PIE says "I shall give you cattle." "Cattle? I do not know cattle." The PIE and the
  English say different things.
- **Why it breaks §5.** §5 gives the speaker a herd (péḱu), and here he claims not to know it.
- **Fix (plan).** The user now offers a machine, `pie-neo-kwertrom`, a thing that is strange to the speaker as §5
  intends: "kʷértrom toy h₁opéyōh₂." "kʷértrom?" "kʷértreh₂ ne wóydh₂e." ("I do not know machines.")
  - The OBJ in the last of these was set to PL so that it matches "machines".
  - The plan's title, sentence English and plan English were updated to match.
  - The number of coined sentences is unchanged.

No other line is wrong. In no line does the model say it is, or call itself, a machine, a program or a made mind, or
say it lacks a body, home or parents. The model consistently has a wife (pótnih₂), sons, daughters, brothers, a
sister, a mother and father, a mother's brother who is a smith, cattle, sheep, horses, a wagon and a hearth. Modern
things are strange to it: the machine in 0028, and now in 0022.

## 3. Minor items

Fixed in the plan:
- **0021: the cow's gender.** gʷṓws was realized masculine (ḱósyo, h₁ím) under the English "cow". gʷṓws has common
  gender, so I set it to f: the record now has ḱósyeh₂s gʷéws and h₁íh₂m̥.
- **0030: "I have nothing."** This line was followed directly by "I have cattle, sheep and horses." The PIE,
  ne kʷid (n.), refers back to gold (n.), so I changed the English to "I have none."

Left as they are (notes for the lead):
- **Gnomic aorist with generic-present English.** The lexeme is aorist-only in each case:
  - swéh₂dt "becomes tasty" (0007, packet 095db374);
  - h₁áyt "gives" (0017, packet 16ec9fad);
  - h₂ḱh₃ént "men do not eat gold" (0030).

  These are defensible as gnomic aorists.
- **n̥smé (ACC) as the goal of "come"** (0010, packet 63f59bc6; also 0016). I flagged it as minor in the verdicts.
  On reflection it is acceptable: Vedic gam- takes the accusative of a person as goal.
- **gʷerh₃- "swallow, devour" for plain "eat"** (0005, 0013, 0029). This stretches the sense a little. Both it and
  h₁ed- are inherited, and h₁ed- was near its cap.
- **"Give those eight"** (0021): oḱtṓw tā́s is a demonstrative plus a numeral, so the English is slightly odd but
  matches the PIE.

Archaic-first holds:
- 6 of the 231 sentences (2.6%) contain a coinage.
- The coinages are pie-neo-welcome (0004) and pie-neo-kwertrom (0022, 0028).
- Every other concept uses an inherited word: guest-friendship, gifts (dóh₃r̥ and its collective déh₃ōr, déh₃rom,
  déh₃nom), bride price h₁wédmn̥, sale price wósn̥, buying kʷrineh₂-, selling perh₂-, and exchanging kʷreyh₂-.

Every turn answers the one before it. The how-do-I-say dialogues (0032, 0033 and 0038) follow §2: the model repeats
the sentence and adds one more.

## 4. Gate

`realize_plans.py data/generation/plans/t3b-005.jsonl --batch t3b-005 --tier3b --model claude-opus-5-5 --prompt-id tier3b-planner-v3`:
- 40/40 realized, all exact, reject rate 0.0.
- 83 distinct roots and 139 distinct lexemes; max lexeme uses 6.
- Neologism tokens: 6 (0.7%). Coined sentences: 0.026.
- **Gate: PASS.**
- 5 anaphor-antecedent warnings, all benign: the antecedent sits more than two clauses back (0011, 0021) or is a
  deictic "that" (0024, 0032, 0038).

## 5. For the lead (engine and brief)

1. **The form of `pie-neo-money` is identical to inherited péḱu "livestock".** That is correct as a calque (Lat.
   *pecūnia*, Goth. *faihu*). Under the v3 persona, though, "money is a strange modern thing" cannot be said: it comes
   out as "I don't know cattle". No gate can catch this. Two possible fixes:
   - a note in `planner-brief-3b.md` §5, or in the neologism's gloss, saying that péḱu is the speaker's own herd and
     must not be presented as unfamiliar;
   - dropping `pie-neo-money` from Tier 3b slices.
2. **Aorist-only lexemes.** swéh₂dt, h₁áyt and h₂éḱh₃t force an aorist under a generic present in the English. The
   brief could tell planners to write past or perfect English for these, or to accept them as gnomic.

Files changed: `data/generation/plans/t3b-005.jsonl` (plans 0021, 0022 and 0030). Re-realized output:
`corpus/tier3b/t3b-005.jsonl`. Nothing was committed.
