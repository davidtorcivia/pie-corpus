# Tier 3 review: t056 (council, parley, deciding for the tribe; 40 in-world dialogues)

Reviewer brief `review-v1`. Prompt id `tier3-dialogue-inworld-v1`, model `claude-opus-5-5`.

## Procedure

- Packet: `scripts/make_review_packet.py t056 --n 20 --plants 5 --tier1 3`, which gave 28 items (20 real, 5 planted, 3 Tier 1).
- Blind back-translation of 6 items, from the `pie` field only, written before any English was shown:
  `docs/audits/packets/t056-blind-translations.jsonl` (sha256 `3ec8eba6…0f28`).
- Verdicts written and saved before opening corpus/ or the plans: `docs/audits/packets/t056-verdicts.jsonl`,
  sha256 **`8d5b5f250486811fbdf26b95ed7650f880b75d4a6d6298a50eb25362dd190e1d`** (resolve_review_items.py
  printed the same hash).
- Then `resolve_review_items.py t056` and `score_review.py t056`. Nothing under data/audits/ was opened.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught, all 5 named) |
| Tier 1 judged wrong | 0/3 |
| real items judged wrong | 1/20 (0.05) |
| real items judged minor | 4/20 |

All five plants were flagged as wrong, each with the planted error named:
- instrumental kóryoh₁ with a verb of fearing;
- sréwmn̥ h₁épi (nominative/accusative where the locative belongs);
- gʷṓws (NOM.SG) used as the object;
- wiHróh₁ (INS) for the genitive;
- pérunbʰos h₁épi (dative/ablative plural).

## Blind back-translation

Overall agreement: 5 of 6 items close, 1 partial.
- **0793726b:** gist right. I read sésti as "sits" where it means "sleeps", mógʰewes as "mighty" where it means
  "young men", and ǵn̥h₃rós as "known" where it means "wise".
- **a8685620:** close. I took kéwdʰoh₂e as "they hide"; it is "I hid" (1sg middle).
- **2f5ca9c1:** close. I read pérwr̥ as "across"; here it means "mountain" (the lexicon has two homographs, ford
  and rock/mountain).
- **f2ae18b7:** partial. I took h₁éymos as "leader" (it is "to them") and could not read kénkonti ("are hungry").
- **97a3b2e1:** close. I read h₁yégom ménōmes as "stay the winter"; it is "wait for the ice".
- **8a958fa6:** close. I read sénōs as "compensation"; it is the vocative "old men".

None of these disagreements was a defect in the PIE.

## Packet items: real verdicts and what became of them

| item → record | verdict | finding | after |
|---|---|---|---|
| 1d3768c5 → t3-t056-00010 | **wrong** | déḱm̥ h₁éḱwom "ten horses": ACC.SG. The plan had the horses as an APPOS with `num: PL`; the engine gave them the head's number (SG) and said nothing. Also *me* (see engine findings). | Fixed: "He has asked for a bride price; he has asked for ten horses." Now h₁wédmn̥ prḗḱst déḱm̥ h₁éḱwons prḗḱst; *me* changed to médʰi. |
| c8da3ac9 → t3-t056-00012 | minor | The dual subject (two tribes) was followed by a 3pl verb. | Fixed: 3DU tl̥nh₂tā́m. "Between them" now feminine h₁íh₂n̥s, tracking the tribes. |
| 2f5ca9c1 → 00020 | minor | withdrawn: h₂roh₁dʰéyeti is glossed "to speak" (reflex-confirmed), so the sense is not stretched | none |
| caf9b710 → 00036 | minor | withdrawn: the POSS has `num: DU`, and a genitive dual surfaces as the plural by design (planner brief §17) | none |
| 442cd81a → 00005 | minor | withdrawn: gʷṓws is masculine in the lexicon, so tóns is correct | none |

**Before the fixes:** 1 real item wrong and 4 minor. After the fixes and withdrawals, 0 are wrong and 0 minor.
Three of the four minors were my over-calls.

## Second pass: all 40 records, against planner-brief-v4 and the in-world brief

Checked throughout:
- Both speakers belong to the PIE world (chiefs, elders, herdsmen, widows, kin). Nothing is modern or coined.
- The user speaks first, with two speakers alternating, and every turn answers the one before it.
- Each sentence's English pairs correctly with its PIE.
- Verbs of fearing take the ablative: kóryōd, twéd, sénoybʰos, h₂yuHn̥ḱóybʰos.
- Where the planner wrote around a missing verb, the PIE still says what the English says:
  - "pay" = kʷoynéh₂m déh₃t;
  - "ask for payment" = kʷoynéh₂m h₁réh₁t / préḱst;
  - "persuade/obey" are avoided;
  - "trust" = bʰéydʰ-;
  - "swear" = h₃m̥néh₃-;
  - "avenge" = "seek payment" (kʷoynéh₂m h₂isḱ-), which says the same thing.
- moréyeti is glossed "to kill" in the lexicon, so it is not a misused causative.
- The gnomic aorists unént, h₁réh₁t and bʰugént are allowed: these verbs have only aorist forms (rule 8).

Found and fixed in data/generation/plans/t056.jsonl:

| record | class | finding | fix |
|---|---|---|---|
| 00010 | wrong | ten horses came out in the singular (above) | split into two clauses |
| 00023, 00035, 00038 (4×), 00010 | wrong | the adposition `pie-lex-me` "among, by" comes out as *me*, sitting in second position away from its object, so it reads as the 1sg enclitic *me*: kʷíd me Hyudʰsmṓm méh₂ter …, h₁ésmey me h₁ludʰísu …, gʷénh₂es me méǵʰye … | `pie-lex-medhi` + LOC (planner brief: "among us = médʰi + LOC"). It now follows its object: ǵr̥h₂n̥tsú médʰi, h₁ludʰísu médʰi, tébʰye médʰi. In 00038 "stand by you/me" became "stand with you/me". |
| 00018 | wrong | "them" = our grandmothers, three times as masculine tóns | gender f: tā́s |
| 00001, 00008 | minor | "send a man to their chief / two men to the son": a bare accusative of goal for a person | ADV próti + GOAL: wiḱpótim próti, suHnúm próti |
| 00012 | minor | dual/3pl mismatch, and "between them" was masculine | as above |
| 00015 | minor | "They drove the horses …" was realized as tóns ("them"), and the last plural referent was the thieves | OBJ márkons (márkos "horse"; h₁éḱwos is at its cap) |

Second pass, before the fixes: 5 records wrong (00010, 00018, 00023, 00035, 00038) and 4 minor (00001, 00008,
00012, 00015). After the fixes: 0 wrong and 0 minor.

Left as they are: h₃órbʰos "captive" in 00024 is a slight stretch of "orphan; servant, slave". The engine's
antecedent warnings, all of which I checked, point to referents more than two clauses back or across turns, and
all are correct.

## Re-realization and gate

Re-realized with `scripts/realize_plans.py data/generation/plans/t056.jsonl --batch t056 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`:
- 40/40 realized, 40/40 exact, reject rate 0.0;
- 282 distinct lexemes, 160 roots, 38.2 words per record;
- max lexeme uses 8.

The first re-run failed the cap: ḱóm reached 11 and h₁éḱwos 9. I moved those uses to médʰi and márkos, and the
second run passed. **Gate: PASS.** No corpus file was edited by hand, and the release approval is not set.

## Engine findings (report only)

1. **`pie-lex-me` (ADV "in the middle of, by, with") is placed in clause-second position**, away from its `dep`
   object. médʰi in the same plans is placed correctly. Its surface form is the same as the 1sg accusative
   enclitic *me*, so a reader takes it as "me". It was used 7 times in this batch, and it is attested in only 2
   branches. Suggestions:
   - block it, or fix its placement;
   - point planners to médʰi.
2. **APPOS with an explicit `num` is silently overridden** by the head's number. "a bride price, ten horses"
   (`num: PL`) came out as déḱm̥ h₁éḱwom. Two more defects came with it:
   - a numeral MOD on a singular noun passed the checker unflagged;
   - the gloss says ACC.SG for déḱm̥.

   The checker should either reject an APPOS whose `num` differs from its head's, or keep the APPOS's own number
   (an apposition with a different number is ordinary in the daughter languages).
