# Tier 3 batch t092 review (review-v1, 2026-10-31)

Batch: 40 in-world two-speaker dialogues, stories told at the fire on request (serpent-slayer, fox, cattle-raid,
first man and twin). Prompt `tier3-dialogue-inworld-v1`. Brief: docs/generation/reviewer-brief.md.

## Procedure

- Packet: `make_review_packet.py t092 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).
- I did the blind back-translation first, printing only the `pie` field:
  `docs/audits/packets/t092-blind-translations.jsonl` (6 items).
- Verdicts: `docs/audits/packets/t092-verdicts.jsonl`, saved before I opened corpus/ or the plans.
  sha256 `9380ce9506487024ce6fd993fd4105af0382dc33c71150f99bccc11c29e3faf8` (resolve_review_items.py confirmed it).
- I checked forms against `Lexicon.cells()`, built into a reverse index of forms, plus closed_class.json. I read
  full glosses with `Lexicon.meaning`. I did not read data/audits/.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 judged wrong | 0/3 |
| real items wrong | 0/20 |
| real items minor | 1/20 |

The plants I caught, in the packet's spelling:
- 8f4943ed: pḱúbʰos (DAT/ABL.PL) as the object of klépet 'stole the cattle'. It needs ACC.
- 95c448ef: deywóh₁ (NOM.DU) in "Was he a god?". It needs deywós.
- 5c1cdca9: luǵréh₂bʰos (f DAT/ABL.PL) modifying spélom. It needs luǵróm.
- 4c63c692: h₂ŕ̥tḱons (ACC.PL) where 'a wolf and a bear' is the subject. It needs h₂ŕ̥tḱos.
- e6331862: dóm (VOC.SG) for the goal 'to the house'. It needs dṓm.

Real minor (packet): f1b33abc = t3-t092-00025. tóysōm (GEN.PL) 'their' refers to the two horses. This is the
engine's expected dual-oblique fallback (v4 rule 17), so I made no fix.

## Blind back-translation

3 of 6 agree fully (50a35794, 05ce161c, 942cc12b). 8f4943ed agrees except for the planted pḱúbʰos, which I flagged
as uncertain while translating blind. 3164579b and 3ac207c2 agree only in part. In both, the misses were my own
misparses: kʷíh₁ 'how' read as kʷís 'who', póyḱōm 'of the enemies' read as 'how many', lowbʰóm read as 'leaves'
where it means 'bark', r̥h₁tmé read as 'moved' where it means 'found'. On re-check, the PIE in both says what its
English says. None of the misses is a fault in the text.

## Second pass: all 40 records

I read every clause of every plan against its realized PIE. I checked:
- speakers and the per-sentence English;
- narrative tense (AOR or PST where a verb has no aorist; present for the listener's questions);
- short answers' case: ABL in 0004 and 0005, LOC in 0019, GEN in 0022, ACC in 0040, VOC in 0034, NOM in 0015 and 0024;
- fear + ablative (0001, 0011, 0017, 0021, 0032);
- predicate adjectives' gender with dropped subjects (péh₂ureh₂ for the female speaker in 0018, ǵn̥h₃réh₂ for the
  f. bird in 0006, n̥ḱéwih₂ for the f. fox in 0012);
- athematic obliques (déms/démi, h₂ḱméni, mréys, diwés/dyéwi, ḱunés, wédn̥s, h₁h₃sés, h₃r̥nés, limnés, ḱr̥h₂snés);
- enclitic placement;
- every h₂eǵ- look-alike WARN: each 'say' is pie-lex-h2egjt and each 'drive' is h2egjeti, as the English says.

**Pronoun WARNs.** I checked all 31, not a sample. Each antecedent sits more than two clauses back and is correct:
- 0020: h₁íh₂ f is the fox and h₁éy m is the bear.
- 0021: h₁íh₂m̥ is the king's daughter.
- 0024: h₁ésmey is the youngest brother.
- 0027 and 0036: h₁íd n is the sun.
- 0028: tóybʰos m pl is the dogs.
- 0029: tṓys is the villagers.
- 0031: tā́s is the cows.
- 0032: h₁éy is the wolf.
- 0035: tóybʰos is the wolf and the bear.
- 0037: tóybʰos is the captors.
- 0039: h₁íd is 'it'.
- 0040: tód is 'that'.
- The "VOC is near" WARNs are all genuinely 3rd person.

**Glosses.** I checked every questionable sense against its full gloss, and all are allowed:
- pérwr̥ 'rock; mountain', wiHrós 'warrior, hero', gʰrémeti 'rumble, roar', ǵnéh₃t 'to meet';
- h₂ew and h₂éti 'again', h₂éwh₂os 'maternal uncle', pótis 'husband', pótnih₂ 'wife', stégos 'roof, house';
- térmn̥ 'end', nes- 'return home', wédʰeti-2 'marry', h₁opéyeti 'to give', némos 'sacrifice', snusós 'bride';
- kʷékʷlos 'wagon', éti 'still, too', dóru 'wood'.

Nothing is modern or coined (spélom 'story' is a project reconstruction, as the slice allows). Every turn answers
its question.

**Real errors found: wrong 0; minor 6 (5 fixed).**

| record | issue | fix in plans/t092.jsonl |
|---|---|---|
| 0004 c3–c4 | "Were they brothers? They were brothers" written as nominal sentences. v4 says a past needs a verbal clause with h₁ésti. | added h₁ésti PST 3DU: tóh₁ bʰréh₂terh₁e h₁stā́m |
| 0008 c11 | English "praise him in song": "in song" has no slot | English → "We still praise him." |
| 0018 c5 | "with his spear" written as ḱóm + INS, which is comitative ('together with') | bare instrumental: swóh₁ ǵʰoysóh₁ |
| 0030 c2 | "in their village": the reflexive swóy is not controlled by the clause's subject (food) | demonstrative GEN.PL: tóysōm ḱóymoy |
| 0033 c1 | "fought with a hundred enemies": ḱóm + INS reads 'fought alongside' | próti + ACC, "fought against": ḱm̥tóm póyḱons próti |
| 0025 c11 | tóysōm GEN.PL for a dual referent | none (engine fallback) |

Left as is: wos 2pl for 'you two' in 0035 (no dual enclitic offered); the gnomic-aorist prḗḱsm̥ 'I ask you' in 0012;
"grew angry" written with PST gʰrémet in 0023.

Real wrong/minor in the packet: 0/1 before the fixes and 0/1 after them. The batch-wide second pass found
wrong 0 / minor 6 before the fixes and wrong 0 / minor 1 after them.

## Re-realization and gate

`realize_plans.py data/generation/plans/t092.jsonl --batch t092 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1` gives:
- 40/40 realized, reject_rate 0, all_exact;
- max_lexeme_uses 8, the cap: h₂éwh₂os, gʷʰen-, h₂yuHn̥ḱós, h₂wĺ̥pis and gʷṓws are at 8;
- 312 distinct lexemes, 181 roots, 31 WARNs, all reviewed above;
- **gate PASS**.

A backup of the pre-fix plans is at
/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/t092-plans-before-review.jsonl.

## Engine and brief notes (report only)

- The lexicon gives gʷṓws masculine, so the anaphoric for the cows comes out as h₁íns (0003). Other dialogues use tā́s
  (f) for the same cows. Both are defensible, but the batch is inconsistent. A lead decision on a feminine 'cow'
  reading would settle it (idioms.json already lists "a feminine cow").
- realize_plans reports accent_defect_tokens 3. This is not a finding of this review. The lead may want to look.
- I found no engine errors.

Release rule: recall 5/5 ≥ 4/5; real wrong 0/20 ≤ 2/20; gate PASS. I did not set the approval; that is the lead's call.
