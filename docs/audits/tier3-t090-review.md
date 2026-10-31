# Tier 3 batch t090 review (courtship and love, 40 in-world dialogues)

Reviewer: calibrated reviewer (Claude Opus 5.5), 2026-10-31, procedure `review-v1` (docs/generation/reviewer-brief.md).

## Packet and calibration

- Packet: `scripts/make_review_packet.py t090 --n 20 --plants 5 --tier1 3` → 28 items (20 real, 5 planted, 3 Tier 1).
- Blind back-translation of 6 items was done first, from the `pie` field only:
  `docs/audits/packets/t090-blind-translations.jsonl`.
- Verdicts were saved before I opened corpus/ or the plans: `docs/audits/packets/t090-verdicts.jsonl`,
  sha256 `6bd44635edb5ca8363bcf656a129a6dc1e9ed33901efde63c10ab2bf1bfed408` (resolve_review_items.py printed the same hash).
- `score_review.py t090`: **plant recall 5/5** (all 5 named). Tier 1 judged wrong: 0/3. **Real items: 0 wrong, 0 minor of 20.**

Plants flagged (all confirmed planted by resolve_review_items.py):

| item | planted form | why it is wrong |
|---|---|---|
| 2a4d5f24 | usménōm | GEN.PL of wésmn̥; the object of téksi with tód h₁rudʰróm needs ACC.SG wésmn̥ |
| 9d946f47 | h₂énHoh₁ | INS.SG / NOM-ACC.DU of h₂énHos; "I sang to your grandmother" needs DAT h₂énHōy |
| af638d17 | pótēy | LOC.SG of pótis; the subject "an old husband" needs NOM pótis |
| 9fc335e7 | tewh₂séh₂m | FEM ACC.SG; the predicate of masculine h₂r̥Hmós needs tewh₂sós |
| cfbce96f | mā́dsoh₁ | INS.SG / DU of mā́dsos; the object of pékʷet "cooked food" needs ACC mā́dsom |

## Blind back-translation agreement

Checked against the packet English after the verdicts were saved:
- c6ce6f9c, 983a53da, c782448f: they agree in substance. I read léymonm̥ as "meadow"; the English says "lake".
- 4d41bba3: mostly agrees. I read h₂éyeri as "near" where the English has "in the morning", and I read h₁suménēs as "Good-mind" where the English has "Kindly".
- 1f214b40: partly agrees. I misread ǵʰoysóh₁ "with the spear" as "goatherd".
- 9d946f47 (a planted item): partly agrees. I misread h₂wíbʰos as "grandfathers" instead of "birds".

The disagreements came from my own lexical slips. None of them points to a defect in the PIE.

## Second pass: all 40 records

I read every record's PIE, tokens and plan against planner-brief-v4 and the in-world dialogue brief. Checks made:
- nothing modern, coined or explicit;
- every turn answers the one before;
- speakers and per-sentence English;
- every he/she pronoun and its antecedent;
- feminine PREDs with dropped subjects (all carry `gender: "f"`: 0002, 0005, 0013, 0017, 0039);
- h₂éǵeti and h₂éǵomes in 0009 (×2), 0020, 0033 and 0036, each confirmed as 'drive';
- fearing with the ablative (0003, 0013, 0016, 0034, 0037);
- the case of short answers (0001 ACC, 0007 ACC, 0014 DAT, 0036 ACC/GEN, 0025 NOM after a possessive dative);
- athematic obliques and enclitic placement;
- doubtful senses against their full glosses: dʰegʷʰh₂- 'pass by', ḱlowséyeti 'heed', leloykʷe 'be gone', wenH- 'come to love', h₁éh₁ugʰos 'boast', gʰr̥h₁mn̥ 'grass', h₁opéyeti 'make reach; give', skérdʰeti 'become cut'.

**Wrong: 0.** **Minor: 6.** Each is a place where the English said more than the plan. All were fixed in the plan, and the batch was re-realized:

| record | issue | fix |
|---|---|---|
| t090-0008 | "Once he left a flower" has no word for "once" | English: "He left a flower on my path." |
| t090-0018 | "I have never spoken" is plain ne + PST | English: "I have not spoken to him." |
| t090-0024 | "he passed by me": the clause has no "me" (dʰégʷʰh₂t has no object) | English: "he passed by at the spring and did not see me." |
| t090-0036 | "Sleep flees from me" is rendered with an aorist (bʰéwgt) | English: "Sleep has fled from me." |
| t090-0040 | "the dawn in my house": the engine realized only one `moy` for two enclitic POSS personal/1 in one clause | removed the second POSS; English: "in the house" |
| t090-0040 | "Cook it": the clause had no object | added OBJ anaphoric_i n PL (h₁íh₂ pékʷe); English: "Cook them" (meat and barley) |

After the fixes: real items wrong 0/20 and minor 0/20; across all 40 records, 0 wrong and 0 open minors.

## Gate after re-realization

`realize_plans.py data/generation/plans/t090.jsonl --batch t090 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`:
**PASS**.
- Plans: 40/40 realized and exact; reject rate 0.
- max_lexeme_uses = 8, at the cap (ǵérh₂onts, dʰugh₂tḗr, suHnús, gʷṓws, h₁éḱwos).
- Distinct lexemes 284; distinct roots 158; 40.35 words per record.
- Warnings: 6.
  - Four are h₂éǵeti / h₂éǵomes homograph warnings. All four mean 'drive'.
  - One flags tósyeh₂ey in 0036 clause 8. It refers back three clauses to the goose-girl, which is correct.
  - One flags h₁íh₂ in 0040 clause 10. It refers to "meat and barley", two coordinated neuter nouns.

## Engine and brief notes (report only; for the lead)

1. **A duplicate enclitic is dropped silently** (t090-0040). A clause with two `closed:personal/1` enclitic POSS slots
   (wife … my house) came out with only one `moy`, without a warning. The second possessor was lost while the
   English kept it. The realizer should warn or reject when an enclitic is merged this way.
2. **The antecedent warning misses coordinated nouns.** It does not treat two coordinated neuter singulars as a
   neuter plural referent, so 0040's "them" (h₁íh₂ = meat and barley) was flagged by mistake.
3. **ḱóm "with" + pronoun takes the dative.** It comes out as méǵʰye ḱóm and tébʰye ḱóm, but a noun takes the
   instrumental (ph₂tréh₁ ḱóm, 0011). This may be deliberate, since personal pronouns have no instrumental, but it
   is worth stating in the brief.
4. **Comparatives addressed to women are common gender**: túH … ḱéwbʰyōs (0012), swéh₂dyōs (0005), h₁wésyōs (0007),
   h₂érǵyōs (0036), kéh₂yōs (0040). This is defensible, since Greek -ίων and Latin -ior are common gender, but
   Sanskrit has the feminine -īyasī. I did not count these as errors.
5. Tier 1 item 3d55cce1 (Schleicher-style fable) has "eḱwos wewekur", a singular-looking form with a 3pl verb.
   Tier 1 is not judged, so I note it only.
