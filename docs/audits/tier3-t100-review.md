# Tier 3 batch t100 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on ordinary death and mourning (`tier3-dialogue-inworld-v1`): an old
mother dying at home, sitting with the dead, the women's lament, the pyre and the grave, grave goods, the funeral
feast, a widow and her kin, naming a child after a dead grandfather, the dead remembered at the hearth, fame that
does not die. Reviewer: calibrated agent review following docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t100 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items, from the `pie` field only, before any English was printed:
   `docs/audits/packets/t100-blind-translations.jsonl`.
3. Verdicts written and saved before corpus/ or the plans were opened:
   `docs/audits/packets/t100-verdicts.jsonl`, sha256
   `23ea10210ccd0109229088bfac8b785905e7dea5c5857545c35b0db1f2a89530`.
4. `resolve_review_items.py t100`, then `score_review.py t100`. data/audits/ was not read.
5. Second pass: all 40 records read in full against planner-brief-v4 and the in-world dialogue brief (top part).
   Each token was checked against `Lexicon.cells()` and the closed class, and every sense against the full gloss.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong | 0/20 |
| real items judged minor (as scored) | 2/20 |

Plants caught (packet spelling):
- 1ed222d2: dʰr̥sús **h₁ési** (2sg) for "I am bold" (1sg h₁ésmi), a short answer.
- c6aefb60: tód h₁idʰé **bʰéretu** (IMP.3SG) for "Bring it here" to the mother-in-law (2sg bʰére).
- 68a4217b: **solh₂wóm yéh₁n̥s**: the adjective is NOM/ACC.SG and the noun GEN.SG, so they don't agree ("a whole year").
- 408a07b4: **wiḱpóteyes** (NOM/VOC.PL) h₁wídʰewh₂ for "widow of the chief" (GEN.SG wiḱpóteys).
- b47df29b: **lubʰyónt** te (3pl) for "She loved you" (3sg lubʰyét; the next verb wéḱti is 3sg).

**Tier 1 control.** b1c39970 (t1-schleicher-fable-danka-1986-0001), title *owis eḱwoi kʷe*: I scored it minor
because nom. pl. -oi is the pronominal ending, while o-stem nouns take -ōs. The text follows its source (Danka 1986),
so nothing is changed.

## Real packet items: minor findings

| packet item | record | finding | action |
|---|---|---|---|
| 530a8b55 | t3-t100-00019 | wíḱpotey translated "Master of the house" | **withdrawn**: the full gloss of wiḱpótis has "master of a household" |
| ffbaab33 | t3-t100-00012 | "I drink it, and I pour it out": píph₃oh₂ PRS beside ǵʰḗm AOR.1SG "I poured" | the present píph₃oh₂ was correct, and only the aorist was off. ǵʰew- (gjhewt-2) has no plain present, so both verbs are now SBJV, which keeps the clause uniform: píph₃ōh₂ … ǵʰéwoh₂, English "I will drink it, and I will pour it out on the earth for him." |

Real items after review: **0/20 wrong, 0/20 minor.**

## Blind back-translation

All six agree with the record English on the content, with small lexical slips:
- e56f8348 (the herd): matches. I read meménonti as "they remember"; it is SBJV "they will remember".
- 1ed222d2 (fame): matches, and the planted h₁ési was flagged here too.
- 25ea3f38 (grave goods): I read h₂réydʰ- as "haul"; the gloss is "prepare, make ready". I took usménh₁/tóh₁ for duals;
  they are INS.SG "with the garment".
- 90982e8c (the women weep): matches.
- 63f16813 (the dark path): I read h₂éwh₂os as "grandfather" and the record has "uncle" (the gloss has both). I read
  somHós as "together"; the record has "alone".
- 67b67330 (cooking for the feast): kʷíd taken as "what" (the record has "why"); h₁súmenes taken as an adjective on
  the guests (the record has the vocative "Kindly One"). Both readings are possible from the PIE.

## Second pass (all 40 records)

No modern content and no neologisms. Four lexemes are project reconstructions, flagged `coined: "project"` in the
tokens: h₂énHos "grandmother", gʷʰermós "warm", pṓlHos "foal" and spélom "story". Planner-brief-v4 §Project
reconstructions allows them in Tier 3; the in-world brief's "no coinages" is aimed at the Tier 3b neologisms. They are
not counted as wrong. The structural rules hold everywhere. Every clause has a speaker. There are exactly two
speakers and the user speaks first. A change of speaker always starts a sentence. Every sentence-initial clause has
its own English, and those join to the plan English. Each dialogue has 4–14 clauses and 5–8 turns. realize_plans does
not check these for Tier 3, so they were checked by script.

### Findings and fixes (plans/t100.jsonl)

| record | finding | verdict | fix |
|---|---|---|---|
| t3-t100-00023 | "In the evenings I look for **him** at the door": no man is named anywhere in the dialogue. h₁ím (m.) can only point to dṓm "house" in the clause before, which is also why the antecedent check gave no WARN | wrong | OBJ is now pótis + enclitic moy: *pótim moy wékʷsperoysu dʰwóri h₂isḱóh₂*, "I look for my husband" |
| t3-t100-00005 | the quoted lament line "Who will sit at our hearth now?" came out with a full stop | minor | `question: true`; now ends in "?" |
| t3-t100-00012 | tense mix, above | minor | above |
| t3-t100-00017 | "my uncle" for h₂éwh₂os, which is maternal only | minor | English "my mother's brother" |
| t3-t100-00024 | "Your grandfather is thirsty, son" for h₂éwh₂os, but the speaker's sex is not given, so the English must say which side | minor | English "Your mother's father is thirsty, son." (the vocative "grandfather" inside the prayer stays) |
| t3-t100-00021 | "at **his own** hearth": the PIE has no swós or POSS | minor | English "at the hearth" |
| t3-t100-00022 | "I do not know, **my child**": no slot | minor | English "I do not know." |
| t3-t100-00026 | *nu toy séh₂ téwe wókʷh₁ …*: a stray enclitic POSS toy on the pronoun séh₂ ("your she"), not in the English | minor | slot removed: *nu séh₂ téwe wókʷh₁ h₂éti kh₂néti* |

Second pass before the fixes: 1 wrong, 7 minor in 40 records. After the fixes: 0, 0.

### Questions back (in-world brief §3)

The model asked a real question in 14 of 40 dialogues. The lament quote in 00005 is not one. In grief this is mostly
right. The model is usually the elder, the dying person or the bereaved, and is the one who gets asked: a child asks
why the women weep, a widow is asked how her husband died. Still, in four dialogues the model is a host, a widow
receiving a visitor, or a kinsman keeping watch, and there a question back reads more naturally. Those four now have
one:
- 00003 (the neighbour's visit): the widow asks "Will you drink mead for him?" and gets "I will drink it for him."
  (h₁ésmey médʰu péh₃esi? / h₁ésmey tód péh₃oh₂.)
- 00013 (the night watch): "Sing to her, sister." becomes "Will you sing to her, sister?" (gʷéHyēsi), which the next
  line answers.
- 00028 (the healer's visit): the widow asks "Will you eat with us?" and gets "I will eat with you."
  (n̥sméy ḱóm h₁édesi? / usméy ḱóm h₁édoh₂.)
- 00033 (grass on the stone): the father-in-law asks "Will you stay among us?" and gets "I will stay among you."
  (n̥sméy médʰi ménēsi? / usméy médʰi ménōh₂.)

The count is now 18/40. ḱóm had reached 12 against the cap of 8, so 00003 and 00033 avoid it. It now stands at 8
(at the cap), with h₁édti, pótis, pótnih₂ and séngʷʰeti, also at 8.

### Checked and correct

- **Pronoun WARNs (18).** I checked each one; all are fine. The referent is the dead man, woman or thing named a few
  clauses back, and there is no rival of the same gender: 00003 h₁ésmey "for him" (the husband), 00004, 00008, 00010
  tóm (the brother), 00011, 00013 (the mother), 00014, 00017, 00018 tód ×2 (the utterance, the deed), 00026, 00028,
  00029, 00033 ×2, 00038 ×2, 00040. The one real antecedent fault (00023) raised no WARN, as shown above.
- **Verb senses against full glosses.** wédʰeti "lead; bring" (fire, mead, a spear); kʷéyt "gather, pile up" (logs);
  bʰuHyéti "be growing" (grass); h₂réydʰeti "prepare"; logʰéyeti "lay, make lie"; moréyeti "kill" (the horse);
  stoh₂éyeti "cause to stand" (raise a stone); h₁opéyeti "make reach; give"; dʰoréyeti "maintain, hold"; ǵonh₁éyeti
  "bring forth"; ḱlowséyeti "heed". Each o-grade -éye- verb is used in a sense its gloss gives (the 2026-10-31 rule).
  h₁épi "on, at, near"; térmn̥ "end"; h₂óyu "lifetime" (ne h₂óyu "never"; dl̥h₁gʰṓd h₂yéws "than a long life");
  téntlom "loom"; gʷr̥dús "heavy" (hands, voice); ish₁rós "strong" (word); somHós "alone"; wiḱpótis "master of a
  household".
- **supnós** occurs once (00035), as "sleep" in "sleep took him", which is the English too; its "death" sense is not
  claimed. 00036 uses swépnos "a long sleep" as the euphemism, and its English says "sleep". **stĺ̥neh₂** "pillar,
  gravestone" is "pillar" (00010), "grandmother's stone" (00020) and "my husband's stone" (00033). **h₂éwh₂os** is
  "mother's father" in 00004 and 00029, now explicit in 00017 and 00024, and a vocative "Grandfather" in 00010 and 00030.
- **Formulas (10 counted).** Seven records use a formula in its sense: famous name (00004), set a name (00009),
  imperishable fame (00011, 00035), swift horse + giver of good things (00012), Mother Earth (00015), great fame
  (00040). The other three counts come from the lexemes simply occurring in the same record, with no formula in the
  text: 00016 (dʰeh₁ "put the bones" + "his name"), 00022 (dʰǵʰméy "to the earth" + "your mother was born"), 00029
  (ǵénh₁os ḱlutóm "famous lineage" + h₁nómn̥ elsewhere). This is a counter issue, not a text error (see below).
- **Gender of women.** Subjects and PRED adjectives with dropped subjects agree with the women: somHéh₂ "alone" (the
  widows of 00003 and 00008), séneh₂ (00002, 00015), h₂yuHn̥ḱéh₂ (00038), mr̥twéh₂ (00019), deywóǵenh₁ēs f. (00038),
  vocatives ǵŕ̥h₂enti, h₁wídʰewh₂, swéḱruh₂, h₁súmenes (f., 00031). luǵrós "do not be sad" (00028) is masculine
  because the widow says it to the (male) healer; ḱéywos "you are dear to me" is said to male addressees (00019, 00028).
- **h₂élyos** occurs once, as an adjective agreeing with its noun: h₂élyōd ḱóymōd (m. ABL, 00019).
- **Short answers** (np `case`): ACC "his knife and his cup" (00007) and "ten cows and a hundred sheep" (00027); INS
  "with the white one" (00014); LOC "in the pot" (00016); NOM "a hundred men and their wives" (00031, answers the
  subject). "And your horse?" (00018) is a NOM topic.
- **Athematic obliques** are all correct: ph₂wéni, ǵʰiméni, kl̥Héni, h₂ḱméni/h₂ḱm̥néh₁, h₁éh₃si, dʰǵʰémi/dʰǵʰméy,
  déh₂newi, kʷsépi, déms/démi, ḱunés, n̥ḱéws, h₂Hséh₂s, kh₃téws/kh₃téwi, swesrés, pótn̥yeh₂s/-h₁, h₁nómn̥h₂, uksnés,
  drúsu, h₂mélǵesh₁, h₃rēǵés, ph₂tréh₁, yéh₁ni, wésni, sweh₂déws m̥dʰéws, n̥ptbʰós.
- **Enclitics** stand in second position (te, me, moy, toy, nos, -kʷe, ne-kʷe "and not").

## Gate

Re-realized with `realize_plans.py data/generation/plans/t100.jsonl --batch t100 --model claude-opus-5-5
--prompt-id tier3-dialogue-inworld-v1`: 40/40 realized, all exact, **gate PASS**. max_lexeme_uses is 8 (at the cap),
with 18 WARNs (the same 18 as before), 305 distinct lexemes, 176 roots and 38.85 words per record.

## Engine / tooling issues (report only)

1. **formula_uses counts lexemes, not phrases.** `_formula_uses` in scripts/realize_plans.py counts a record if all
   of a formula's lexemes occur anywhere in it, so 3 of the 10 t100 counts are false (00016, 00022, 00029). A
   phrase-level check (head and modifier in the same NP or clause) would make the number mean what it says.
2. **The antecedent WARN matches on gender and number only.** In 00023 h₁ím "him" (the husband, never mentioned)
   matched dṓm "house" in the clause before, so no WARN was raised. The check cannot tell a person from a thing.
   Flagging an animate-intent pronoun whose only match is inanimate would need animacy data in the lexicon.
