# Tier 3 batch t084 review (humor: flyting, trickster tales, comic household, mock praise, riddles)

Reviewer: Claude Opus 5.5, 2026-10-30, procedure `review-v1` (docs/generation/reviewer-brief.md).
Not approved here; the release decision is the lead's.

## Procedure

1. Packet: `scripts/make_review_packet.py t084 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items from the `pie` field only, done before any English was printed:
   `docs/audits/packets/t084-blind-translations.jsonl`.
3. Verdicts written before opening corpus/ or plans: `docs/audits/packets/t084-verdicts.jsonl`,
   **sha256 `e4b1ff3dbf28d7ebdd5d38808ccd962630ae02bd94ffcd4dbc618eceb733f89a`** (confirmed by resolve_review_items.py).
4. `resolve_review_items.py t084`, then `score_review.py t084`. data/audits/ was not opened.
5. Second pass: all 40 records read in full against planner-brief-v4.md and the "Humor (batch t084)" section of
   planner-brief-dialogue-inworld.md.

## Calibration

| | |
|---|---|
| plant recall | **5/5** (all caught and named) |
| Tier 1 judged wrong | 0/3 |
| real items judged wrong | **0/20** |
| real items judged minor | 4/20 (at the time of the verdicts; 3 withdrawn, below) |

Plants caught (packet spelling): spr̥sú as the subject of "the sparrow said" (LOC.PL, needs NOM.SG spḗr);
kʷíh₁ wóydh₂e "how do *you* know?" (PRF.1SG, needs 2sg wóydth₂e); h₂ówis widét "she saw the sheep" (NOM.SG as object,
needs ACC.PL h₂ówins); widḗtes "when she sees" (SBJV 3DU, needs 3sg widḗti); HrudHtóm addressed to the plural
múHses bʰréh₂teres (IMP.2DU, needs 2pl HrudHté). I did not flag one candidate: bʰebʰóyh₂e as a 3sg looks like a 1sg,
but the root is bʰeyh₂-, so the 3sg is bʰebʰóyh₂e, which is correct.

## Blind back-translation agreement

All 6 items (t3-t084-00019, -00020, -00010, -00022, -00009, -00011) came back with the meaning of their English.
- I got two senses wrong on the first read: léwbʰa "beloved" (I read it as "gladly") and mógʰew, the vocative "boy".
- I read kʷíh₁ wóydh₂e as "how did you know?", which is the 2sg. That item was the wóydh₂e plant, so the blind pass
  missed it; the review pass caught it.
- The jokes survive the back-translation. The drunk who sees two wives, the fox that praises the gods and loses the
  sparrow, the lazy son who goes back to bed, and the wife whose wool-drying brings rain all came through.

## Real items: verdicts and second look

No real item was wrong. These were the packet minors:
- **t3-t084-00005 (flyting, drank a lake)**, minor, kept. The joke falls flat. "Yesterday I was pissing in that lake"
  is answered by "Then the water tasted good", and the logic of the comeback is muddy. The urine is in-world
  (flyting), but the item sits at the edge of "crude for its own sake". The grammar is correct.
- **t3-t084-00031 (riddle, fire)**: withdrawn. mért is a gnomic aorist of an aorist-only verb (pie-lex-mert), which
  v4 rule 8 prescribes.
- **t3-t084-00034 (riddle, fart)**: withdrawn for the same reason (litént, aorist-only pie-lex-leytt).
- **t3-t084-00026 (fable, fox and she-wolf)**: withdrawn. h₂én (pie-lex-h2en-2) is glossed "there, yonder, on the
  other side", so the English matches.

## Second pass: all 40 records

**Nothing modern or coined.** No out-of-world reference appears anywhere. Everything is herds, hearth, kin, guests,
Perkʷunos, the feast, the field.

**Verbs of fearing:** every one takes the ablative. muHsés dedwóye (00007), h₁ésyeh₂s dedwóye (00002, 00035),
h₂wl̥péys dedwóyh₂e (00014), méd trémt (00023), h₁ésmōd trésonti (00032).

**Glosses checked in full:** gʰrémeti is glossed "be angry, rage; roar, rumble", so 00029 "Perkʷunos rumbled" and 00030
"roars" use a listed sense. steh₂urós is glossed "stake" (reflex-confirmed). ḱóm is glossed "with; beside, near", so
h₂Hséh₂h₁ ḱóm "beside the hearth" (00036) is fine.

**Causatives:** only true ones are used: h₂sowséyeti "make dry" with wool as its object, and sokʷéyet /
h₂roh₁dʰéyeti, whose lexicon glosses are "say" / "speak". troméyonti is pie-lex-tromeyeti, glossed "tremble (in fear)"
and intransitive (Gk τρομέω), not a causative.

### Fixed at the source

- **t3-t084-00023** (bear and mouse), pronoun tracking.
  - Before, "It trembled." had no subject, right after "the bear seized the mouse". It read as the bear trembling,
    which spoils the punchline, where the mouse boasts "the bear trembled before me".
  - Fix: SUBJ pie-lex-muHs, English "The mouse trembled." The PIE is now múHs trémt.

### Minor (left, with reason)

- **t3-t084-00028** (goat on the cart), pronoun tracking.
  - In "só mléwHt" ("He said: Come, dear guest!"), the speaker could be the cart, the goat or the bear.
  - Naming the bear would be a 7th use of pie-lex-h2rtkjos, over the cap of 6, and the gate failed when I tried it
    (reverted).
  - The vocative "dear guest" makes the bear the speaker, and topic-switching só supports that reading. A planner
    could free a token in 00023 to make the change.
- **t3-t084-00021** (the princess who never laughed). "If my daughter laughs, I will give her to that man" leaves
  "that man" without a referent ("the man who makes her laugh"). The story is still clear, and the goat-fart turn
  lands.
- **t3-t084-00040** (mock praise of the lazy son). "he eats the ram, and he drinks" has the AOR péh₃t among habitual
  presents. píph₃eti would add 2 syllables to an 8-syllable line, so I left it.
- **t3-t084-00005**: as above.

### Does the joke survive?

Yes in every record but 00005. The punchlines are built from the situation and the words, never from puns, and they
make it into the PIE intact. Some examples:
- the lifted earth and the brother's neck (00003);
- Perkʷunos "rumbled" and "heard me" (00029);
- the cow walks home while two thieves quarrel (00024);
- the satirist's threat, which the cattle and the king's wife ignore (00006);
- the guest: "now you have nothing, and you have a friend" (00015);
- the husband snoring like Perkʷunos (00030);
- "the fox is full" (00014);
- mock-epic ḱléwos ń̥dʰgʷʰitom for a mouse-killer (00036).

Earthy items (the fart jokes 00018, 00021, 00029, 00034, and 00005) are in-world, as the brief asks. Only 00005 is
borderline.

## Gate after fixes

`realize_plans.py data/generation/plans/t084.jsonl --batch t084 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`
- **gate: PASS**
- 40/40 realized, reject 0.0, all_exact
- meter_exact 25/25 = 1.0
- max_lexeme_uses 6
- formula_uses 5, 181 distinct lexemes, 110 distinct roots

## Counts

| | before fixes | after fixes |
|---|---|---|
| real wrong (packet) | 0/20 | 0/20 |
| real minor (packet) | 4/20 as scored (3 withdrawn on second look: gnomic aorists per v4 rule 8, h₂én gloss); 1 standing | 1 standing |
| whole-batch wrong (40) | 0 | 0 |
| whole-batch minor (40) | 5 (00005, 00021, 00023, 00028, 00040) | 4 (00023 fixed) |

## Engine / lexicon notes (report only)

- **pie-lex-gwoxws gʷṓws has gender m.** The texts refer to a cow with feminine pronouns (h₁íh₂m̥ / h₁ésyeh₂s, 00012
  and 00024) and to cattle with masculine h₁íns (00019). Each choice is defensible, but the lexicon gender should
  probably be f or common for "cow" (Ved. gáuḥ f.), so that the checker and the realizer agree.
- **Homograph warning:** h₂éǵeti / h₂éǵt "say" vs h₂éǵeti / h₂éǵet "drive" draws a realizer warning in 6 records.
  The senses are right in each, but a lexicon-level disambiguation note would quiet it.
- **Brief:** the lexeme cap (6) blocks the natural fix for pronoun ambiguity in a two-animal fable. A per-text
  allowance for re-naming characters (v4 rule 19) would help.

## Two jokes that land best

1. **t3-t084-00003 (flyting):** "Brother, I lifted a foal… a horse… two horses and a wagon… the earth." "Then where
   were you standing?" "On your neck, brother. Did you not notice?"
2. **t3-t084-00029 (tale):** an elder farts while praising Perkʷunos at the feast, and the young men laugh. "Do not
   laugh! Perkʷunos rumbled. He heard me." Then the young men praised Perkʷunos.
