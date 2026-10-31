# Tier 3 t044 review (review-v1, 2026-10-30)

Batch: 40 in-world two-speaker dialogues (greeting, guests, the household), prompt `tier3-dialogue-inworld-v1`.

## Procedure

- Packet: `scripts/make_review_packet.py t044 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).
- I never opened anything under data/audits/.
- Blind back-translation first: 6 items, from the `pie` field only (`docs/audits/packets/t044-blind-translations.jsonl`).
- Verdicts were written before I opened corpus/ or the plans: `docs/audits/packets/t044-verdicts.jsonl`,
  sha256 `bda3fcd4138d5018b5c8cab5acf015320647c55d0062df7bf743c0f8f5d237c6`.
- Then `resolve_review_items.py t044` and `score_review.py t044`.
- Second pass: all 40 records, read against planner-brief-v4 and the in-world dialogue brief (top part).

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (5 caught, 5 named) |
| Tier 1 judged wrong | 0/3 |
| real items wrong | 0/20 |
| real items minor | 4/20 |

The five plants, all judged wrong, with the form each should have:
- d836521c: démbʰos (DAT/ABL.PL) where GEN.SG is needed; should be déms.
- 489c2ce8: wéǵʰontu (3pl imperative) where a 2sg command is needed; should be wéǵʰe.
- 7992df60: méh₂term̥ (ACC) where the subject needs NOM; should be méh₂tēr.
- 550c2581: pn̥th₁és (GEN) where the subject needs NOM; should be póntoh₁s.
- 1490a27b: stégesos (GEN) where the object needs ACC; should be stégos.

## Blind back-translation

All 6 items agree with their English on content, speakers and turn structure. These are the only differences:
- 909f22ee (t3-t044-00019): I read sélǵt 'released' as "sent", which is the English. I did not resolve méne moy at
  first; it is GEN 'my' plus DAT 'me': "tell me my grandfather's story".
- a22c8fcb (00033): I could not read h₁ésmi. It is the locative of the anaphoric, "over it", and correct.
- 32517922 (00007): this one led to the "first" finding (below).
- 489c2ce8: the planted wéǵʰontu, which I flagged blind.
- d836521c and 6de3d0b6: they match the English.

## Findings on real records

**Wrong:** none, before or after the fixes.

**Minor (4 in the packet):**
1. t3-t044-00007: the English "Eat with us first" has no word for "first" in the plan. **Fixed** in the plan's
   English (now "Eat with us."), then re-realized.
2. t3-t044-00026: "I have stayed many days" uses a locative plural (pl̥h₁úsu dinóysu) where an accusative of
   extent would be the normal choice. Left as it is: the plan schema has no role for duration (engine/brief gap).
3. t3-t044-00012: the neuter participle dʰégʷʰont with dóru. The engine's neuter active participle is the bare stem
   -ont where -n̥t is expected. Engine issue; reported only.
4. t3-t044-00004: prḗḱst (aorist) for a generic "asks". The lexeme has only aorist forms, so planner-brief rule 8's
   gnomic aorist applies. Acceptable.

**Second pass (all 40):** I found nothing modern or coined. Every turn answers the one before it, both speakers belong
to the PIE world, and the speaker labels and per-sentence English line up in every record.

Specific checks, all of which pass:
- Pronoun referents are right; I checked each of the 9 realizer warnings by hand:
  - 0001, 0002, 0004, 0018 and 0021 have correct 3rd-person verbs (impersonal "it is getting dark", or he/she).
  - 0015's cataphoric "this" is correct.
  - In 0028, 0037 and 0040 the pronoun's antecedent is more than two clauses back.
- Verbs of fearing take the ablative: h₁ésmōd bʰebʰóyh₂h₂e / dedwóyh₂e / mē tréses, and ǵʰwērbʰós ne tréseti.
- I found no causative standing for a plain verb.
- Enclitics sit in second position.
- Athematic oblique cases are right: déms, déh₂newi, kl̥Héni, ǵʰesrés, h₂Hséh₂s, pn̥th₁sú, m̥lités and others.

Senses I checked against the lexicon and accepted:
- h₂éwh₂os "uncle" (glossed 'maternal grandfather, maternal uncle').
- de "but", ḱóymos "household", sédos "dwelling", pérwr̥ "mountains", h₂ew "back/again", éti "beyond", h₂én "there".

**Engine notes (report only):**
- The neuter active participle has a bare-stem nominative/accusative: dʰégʷʰont, where dʰégʷʰn̥t is expected.
- Feminine of ǵérh₂ont-: the vocative is ǵŕ̥h₂enti (zero-grade root with e-grade suffix), in 00018 and 00037.
  Expected ǵérh₂n̥ti.
- The oblique stem of pérwr̥ 'rock' (pie-lex-perwr-2) is pérun- (pérunbʰos, péruns). pie-lex-perwr 'ford' uses
  pr̥wén-. The two r/n paradigms disagree.
- Lexicon form wéwket 'say' has lost its labiovelar (the Tier 1 fable has ewewkʷet).
- The plan schema has no accusative-of-duration role.

## Fix and gate

- Plan edit: t044-0007, the sentence English "Eat with us first." became "Eat with us." (and the full English to match).
- Re-realized with `realize_plans.py data/generation/plans/t044.jsonl --batch t044 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`.
- Result: 40/40 realized, exact_pass 40, reject_rate 0.0, max_lexeme_uses 6, 1329 tokens, 277 distinct lexemes,
  154 distinct roots. **Gate: PASS.**
- No corpus file was edited by hand. The release approval was not set.

## Release-rule inputs

- Plant recall is 5/5.
- 0/20 real items are wrong, both before and after the fix.
- The gate passes.

All three conditions for approval hold; the decision is the lead's.
