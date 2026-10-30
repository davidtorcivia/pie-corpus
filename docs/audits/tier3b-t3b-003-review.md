# Tier 3b review: t3b-003 (home, family and daily life)

Reviewer: calibrated reviewer agent (claude-opus-5-5), 2026-10-30. Brief: docs/generation/reviewer-brief.md (`review-v1`),
adapted for Tier 3b as in t3b-002. The second pass also checks docs/generation/planner-brief-3b.md v3, mainly §5.
Release approval is the lead's call.

## Procedure

1. **Packet:** `make_review_packet.py t3b-003 --tier tier3b --n 20 --plants 5 --tier1 3` gave 28 items: 20 real, 5 planted and 3 Tier 1.
2. **Blind back-translation:** 6 dialogue items, translated from the `pie` field only, before I saw any English.
   The file is `docs/audits/packets/t3b-003-blind-translations.jsonl`.
3. **Verdicts:** I judged all 28 items before opening `corpus/tier3b/` or the plans.
   - File: `docs/audits/packets/t3b-003-verdicts.jsonl`.
   - sha256 `32328225b828f0b2d97b000331a7c29cb0d29ccb81284bba92834ffd8c3d7daa`. `resolve_review_items.py` printed the same hash.
   - I then ran `resolve_review_items.py` and `score_review.py`. I opened nothing under data/audits/.
4. **Second pass:** I read all 40 records in full: speaker, PIE, per-sentence English and gloss, sentence by sentence.
   - It checked character (§5), whether each turn answers the one before, the English-to-PIE match, archaic-first, and grammar.
   - Records 0011, 0014, 0022, 0035 and 0039 were seen in the packet only in planted form, so their second-pass verdicts are **uncalibrated**.

## 1. Counts

| | wrong | minor |
|---|---|---|
| Calibrated, 20 real packet items, before fixes | 0/20 | 4/20 |
| Calibrated, 20 real packet items, after fixes | 0/20 | 2/20 |
| Second pass, 40 records, before fixes | 3 (0015, 0030, 0040), plus 0010 with the same defect, graded minor in the saved verdicts | 5 (0006, 0010, 0019, 0029, 0033) |
| Second pass, 40 records, after fixes | 0 | 2 (0019, 0033) |

- The 4 calibrated minor items are 30d85e78 (record 0033), e34c87f8 (0010), 239fcb90 (0019) and 2411c36b (0029). The fixes cleared 0010 and 0029.
- Tier 1 items judged wrong: 0/3.

**Character violations (§5): none.**
- In no line is the model a machine, program or made mind, or does it say it lacks a body, home or parents.
- Every modern thing belongs to the user, and the model only wonders at it:
  - 0027: the user cooks with a "machine". The model asks whether there is fire in it, then how it heats.
  - 0028: the user came by train. The model asks what it is, then says "A horseless wagon! My horses are swift."
  - 0029: the user has a lamp. The model answers that its family watches the fire and its mother guards it.
- Everywhere else the model is a member of a household: father, mother, brothers and sisters, a wife or husband, sons, grandparents, herds, hearth and dog.

**Coinage:** 7 of 223 sentences (3.1%) contain a neologism. Many dialogues have none, so the batch is archaic-first.

**Turn coherence:** every turn answers the one before. Two small oddities are left as ok:
- 0039: the user says "I have become full", and the host replies "Eat, friend!". This reads as a host pressing food on a guest.
- 0018: the user both reports the sister's joy and asks why she is joyful.

## 2. Plant recall: 5/5 (all 5 named)

| item | record | plant | my verdict |
|---|---|---|---|
| f9ced093 | 0035 | suHnóws GEN.SG for NOM.SG suHnús ("His son is my husband") | wrong |
| f2a04269 | 0022 | woséyesi 2SG for 3SG woséyeti | wrong |
| fd3ddce5 | 0011 | gʷéHyonti 3PL for 3SG ("What does he sing?") | wrong |
| e9d6212c | 0039 | pótnih₂n̥s ACC.PL for NOM.SG pótnih₂ (subject) | wrong |
| c873b7d6 | 0014 | wr̥h₁tóm (verbless participle) for wérh₁t AOR.3SG ("Did he speak to you?") | minor (caught) |

`data/audits/t3b-003-calibration.json` gives:
- plant_recall 1.0;
- real_wrong 0/20 and real_minor 4/20;
- wrong-rate upper bound 0.0.

## 3. Blind-translation agreement: 6/6 in sense

All six blind translations agree in sense with the plan English (fb9500e4, 30d85e78, 04581340, fd3ddce5, 2411c36b, 7d147294).
- The blind pass itself caught two problems:
  - the plant in fd3ddce5 (question in 3PL, answer in 3SG);
  - the dual/plural inconsistency in 30d85e78.
- Two senses I did not recognise blind:
  - h₂roh₁dʰéyeti, which I guessed as "counsels, recounts". The plan has "speaks", and this is right: Goth. *rōdjan* 'speak' < *Hroh₁dʰéye-.
  - léwktrom, which I read as "light". It is the coinage "lamp".
- In 2411c36b I read gʷʰr̥néwti as "the roof gets warm". The plan has "(the fire) heats the house": the omitted subject and neuter stégos make both readings possible.

## 4. Wrong items and fixes (all in data/generation/plans/t3b-003.jsonl)

**swopéyeti, the causative "put to sleep", is used as intransitive "sleep"** in four records.
- The evidence for swopéyeti (Gmc *swabjaną, Skt svāpáyati) means "put to sleep". The lexicon's confirmed gloss "to sleep" led the planner astray (see §6).
- As realized, the lines said:
  - 0015 "I did not put (anyone) to sleep";
  - 0030 "Put to sleep, my son!", twice;
  - 0040 "I am putting to sleep!";
  - 0010 "You put to sleep in daylight".
- Fixes:
  - 0010 and 0040: changed to pie-lex-sesti (sési, sésmi). Both stay intransitive "sleep".
  - 0015, 0030 and 0031: changed to pie-lex-swept-2, the root aorist "fall asleep". This also keeps sesti within the lexeme cap of 6.
    - 0015: nékʷti ne swépm̥ "I did not fall asleep in the night".
    - 0030: súHnew moy supdʰí "Go to sleep, my son!".
    - 0031: ḱéywe supdʰí supdʰí "Go to sleep, dear one, go to sleep!". 0031 itself was correct with ssdʰí; it was moved only for the cap.
  - The clause English and the plan-level English were updated to match.

## 5. Minor items

**Fixed:**
- **0029** (2411c36b): léwkt is an aorist, but the English had a present, "becomes bright". The English now reads "At night my lamp has lit up."
- **0006**: stéwdt had the same problem with "becomes cold". The English now reads "At night the house has grown cold."

**Left minor:**
- **0033** (30d85e78): nésōntor MID.SBJV.3PL after the dual "two brothers" (h₁stés 3DU).
  - Homeric Greek mixes dual and plural freely, so this is tolerable.
  - It can't be fixed: the engine has no MID.SBJV.3DU cell for pie-lex-nesetor. This is an engine gap (§6).
- **0019** (239fcb90): h₂n̥réy DAT for the person asked.
  - preḱ- takes the accusative of the person (Lat. *poscere aliquem aliquid*, Ved. *pṛcchati* + acc.).
  - The plan has only an IO slot. I did not test whether the engine allows a second OBJ (double accusative).

## 6. Engine and brief gaps (for the lead; not fixed here)

1. **Lexicon gloss:**
   - `data/lexicon/confirmed_glosses.jsonl` gives pie-lex-swopeyeti the gloss "to sleep" by the `head` rule, but its own evidence lines say "to put to sleep".
   - `derived_glosses.jsonl` gives "to sleep [-éyeti: causative/iterative]".
   - Both should read "put to sleep", or other batches will repeat this error.
   - It is worth scanning all `-éyeti` causatives whose confirmed gloss copies the root's intransitive sense.
2. **Missing cells:** pie-lex-nesetor has no MID.SBJV.3DU (only MID.SBJV.1DU), so a middle verb can't agree with a dual subject. The 3DU middle endings are probably missing for middle verbs generally.
3. **Double accusative:** "ask X (person) Y (thing)" with preḱ- has no planner pattern. Planners fall back on a dative.
4. **Remaining warnings:** the realizer reported 8 warnings, all antecedent heuristics. I checked each one by reading the records, and none is an error:
   - h₂éǵeti 'drive' vs 'say';
   - ḱód and tód pointing back to a whole utterance;
   - h₁íd 'it' for an activity;
   - 0013 ḱéyror, which correctly sets 3PL.

## 7. Gate after fixes

`realize_plans.py data/generation/plans/t3b-003.jsonl --batch t3b-003 --tier3b --model claude-opus-5-5 --prompt-id tier3b-planner-v3`:

| measure | result |
|---|---|
| realized | 40/40, all exact |
| reject rate | 0.0 |
| max lexeme uses | 6 |
| distinct lexemes / roots | 155 / 90 |
| neologism tokens | 7 (1.0%) |
| coined sentences | 7/223 (3.1%) |
| **gate** | **PASS** |

The first re-run failed max_lexeme_uses (sesti 11). I fixed that with the swept-2 redistribution in §4.

The `-initial` files were left alone. Nothing was committed, and the release approval was not set.
