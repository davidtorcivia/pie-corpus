# Tier 3 batch t062 review (review-v1, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on weather and the seasons (`tier3-dialogue-inworld-v1`).
Reviewer: calibrated reviewer (claude-opus-5-5). Procedure: docs/generation/reviewer-brief.md.

## Procedure

1. Re-realized the plans once at the start so the records carry today's engine fixes (a "?" when any clause of a
   sentence has `question`; check_plan rejects 'two' in an oblique case). The gate passed with 0 rejects.
2. Packet: `make_review_packet.py t062 --n 20 --plants 5 --tier1 3` (28 items).
3. Blind back-translation of 6 dialogue items from the `pie` field only:
   `docs/audits/packets/t062-blind-translations.jsonl`.
4. Verdicts written before opening corpus/ or the plans: `docs/audits/packets/t062-verdicts.jsonl`,
   sha256 `e476a542792c515120061df0cfd89330648c0f2a6f41ab83fd20380730041d42`.
5. Ran `resolve_review_items.py t062`, then `score_review.py t062`.
6. Second pass: read all 40 records (each sentence's speaker, PIE, gloss and English) against planner-brief-v4 and
   the top part of planner-brief-dialogue-inworld.

## Calibration

| | |
|---|---|
| Plant recall | **5/5** (all 5 named) |
| Tier 1 controls judged wrong | 0/3 |
| Real items wrong (scored) | 0/20 |
| Real items wrong (true) | **1/20 before the fixes, 0/20 after** (I passed 544fbcea = 00004 as ok and caught it in the full read) |
| Real items minor | 4/20 scored; 2 left after the fixes (00019 sense accepted, 00033 engine gap) |

The plants were 37b3c7b9 (1PL for "shall I"), 018d59f8 (DAT/ABL.PL for the vocative "Father"), 71a199cc
(NOM/ACC.DU 'embers' for the locative), 69eeec04 (INS.PL 'stalls' after h₂énti for LOC.SG) and e9aa1adf
(plural 'butter'). I judged the last one minor; the other four wrong.

## Blind back-translation

Blind 6/6 agreed with the English on the main sense. The differences were:
- 407a1811: read ǵʰleynóm h₁éseti as "there will be frost". The English has "it will be clear"; the lexeme means 'bright'.
- 37b3c7b9: read péromes correctly as "shall we cross". The English said "I", which turned out to be a plant.
- 544fbcea: middle sentences unsure. The blind pass flagged the gender clash between séh₂ and the neuter h₁íd for
  'snow', but my verdict marked the item ok, which was a reviewer miss. It is record t3-t062-00004, fixed below.
- 733fbba1: read gʰrémeti as 'thunders'. The English has "is angry"; the lexeme's gloss carries both senses.
- 5ca70994: read pérkʷum as 'oak' correctly, and dweh₂rós as 'far'.

## Packet minors (real items) and fixes

| Item | Record | Finding | Action |
|---|---|---|---|
| 8b203550 | 00005 | "your sheep" said to the one old man came out as wos (2PL) | plan: POSS personal/2 → SG (now toy) |
| 8fd1cf65 | 00017 | h₂én 'there' translated "to the other side" | English → "Shall we walk over there on the ice?" |
| 733fbba1 | 00019 | gʰrémeti "is angry": the gloss allows 'be angry, rage' and 'roar' | none (the sense is in the gloss) |
| 83b506e7 | 00033 | ǵn̥h₁yónto is 3PL middle with a dual subject | none: **engine gap**, the middle has no 3DU (cells hold only MID.*.1DU). tóybʰos for the dual dative is expected (brief rule 17) |

## Second pass (all 40 records): further fixes

- **00004 = packet 544fbcea (wrong, pronoun; missed in the verdicts):** 'snow' (snígʷʰs, f.) was referred to with neuter h₁íd + ḱolHtóm albʰóm. The very
  next sentences use feminine h₁íh₂ ml̥déwih₂. Plan: gender f → h₁íh₂ ǵʰiméni ḱolHtéh₂ albʰéh₂-kʷe bʰuHyéti.
- **00014 (minor):** "waiting for me on the other side" for h₂én 'there' → "over there".
- **00025 (minor):** "the dog smells the goats" used káprons (PL), but the text is about the two goats that fled →
  DU káproh₁.

Re-realized with the batch command after the fixes. The gate is **PASS**: 40/40 exact, reject rate 0, max lexeme uses 6.
Every record's PIE "?" count matches its English.

## Checked and found sound

- In-world and in character throughout. Speakers are of the household: a herd-boy and his master, siblings,
  husband and wife, a grandmother and grandchild, a guest, a shepherd met in the mist. Turns answer each other.
- Speakers and per-sentence English are right in all 40. Vocatives and the person of verbs fit the speaker
  assignments.
- **Impersonal weather verbs** are all 3SG with no subject: h₂wérst, snéygʷʰet/snéygʷʰetu, góleti, gʷʰért.
- **Verbs of fearing** take the ablative everywhere: gʰrómōd, wĺ̥kʷoybʰos, h₁éymos, sríHǵesos. No causative
  stands for a plain verb; moréyeti 'kills' and h₂sowséye 'dry (tr.)' are causative in sense.
- **Predicate adjectives** agree with their subjects, including the gendered addresses: ḱéyweh₂, ǵn̥h₃réh₂,
  h₁uséwih₂ and luǵréh₂ for women, h₁wersós for the guest.
- **Missing words.** Summer is gʷʰéresi "in the heat / warm weather", and the English says that. No storm or
  month word is claimed. Lightning appears only as "Perkʷunos strikes the oak".
- **Enclitics.** The clusters are licit: toy + wos, moy + h₁mé, toy + tébʰye (possessive + dative) and nos after nu.
  No enclitic is doubled within one function.
- **00028, the water cycle** (the snow melts into rivers and the sea, the sun lifts it and it falls in winter):
  kept. It is the Vedic picture, not modern science (RV 1.164.51: the same water rises and falls with the days).

- **Gloss senses** were checked against the full `meaning` lists. Every sense the English uses is in the list:
  n̥bʰrós 'rain-cloud, narrowed to rain', h₁rṓs 'dew', dewk- 'lead', h₁ewk- 'learn', gʰrómos 'thunder',
  gʰrémeti 'be angry, roar', steh₂rós 'old', moḱs 'early', h₂ew 'again', téḱnom 'young of an animal'.
- Left as is: in 00037 the subject téḱneh₂ (neuter plural) takes a singular verb, drémt, as the inherited rule
  has it, but the next clauses use plural verbs (dr̥méntu, bʰebʰih₂ḗr) for the same children.

## Engine / brief notes (for the lead)

1. **The middle voice has no 3DU** (only MID 1DU cells), so a dual subject of a middle verb comes out 3PL
   (00033 ǵn̥h₁yónto).
2. **pie-lex-sriHgos has a velar mismatch:** the nominative is sríHgos (plain g) but the oblique cells are
   sríHǵ- (palatal). Lat. frīgus and Gk ῥῖγος point to a plain velar.
3. Gnomic aorists of aorist-only lexemes (séngʷt, h₂wékst, h₃slidʰént, h₁éwHt, bʰérǵʰt) render English presents.
   This is within brief rule 8; it is listed only because it recurs in this batch.

## Release inputs

Plant recall 5/5 (≥ 4/5). Real items wrong: 1/20 before the fixes (544fbcea/00004, which my verdicts missed) and
0/20 after. Gate PASS. Approval is left to the lead.
