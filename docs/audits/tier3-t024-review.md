# Tier-3 review: packet t024 (28 items)

The packet covers dialogues, greetings and household scenes, plus three Tier 1 fable lines. It has 28 items: 20 real, 5 planted and 3 Tier 1. The review followed `docs/generation/reviewer-brief.md` (review-v1) and the grading of t021/t023. The reviewer worked from handbook knowledge only: Fortson, Beekes, Ringe, LIV² and Mallory & Adams, as remembered. Every packet token was looked up in a reverse index built from `Lexicon.cells()`, `participle_cells()` and `closed_class.json`. Doubtful senses were checked in `data/lexicon/lexicon.jsonl`. Verdicts are in `docs/audits/packets/t024-verdicts.jsonl` and blind translations in `docs/audits/packets/t024-blind-translations.jsonl`.

## Calibration (scripts/score_review.py)

| plants caught | plants named | real wrong | real minor | Tier 1 judged wrong |
|---|---|---|---|---|
| 5/5 | 5/5 | 1/20 (5%) | 2/20 | 0/3 |

The 6 items judged wrong were the 5 plants plus one real item.

## Counts (real items)

| | ok | minor | wrong |
|---|---|---|---|
| before fixes | 17 | 2 | 1 |
| after fixes | 19 | 1 | 0 |

The 3 Tier 1 fable lines are minor on notation and are not counted above.

## Wrong (6 = 1 real + 5 planted)

**Real:**
- **db70fa16 (t3-t024-00010), number.** Two brothers are addressed in the dual: VOC.DU bʰréh₂terh₁e, with the 2du imperatives sdtóm, h₁édtom and ph₃tóm. But the perfect gʷegʷmé is 2pl, and the pronouns and predicates are plural (yúH, wéy, suHnéwes, priHṓs).
  - Cause: the plan asked for PRF 2DU. The engine has no PRF.2DU cell and fell back silently to 2pl, which is an **engine gap** (see below). The planner had also written PL on the pronoun and predicate slots.
  - **Fixed in the plan:** the aorist of *h₁er- 'arrive' (AOR.2DU h₁r̥tóm), with every slot in the dual. The realized text is now `bʰréh₂terh₁e h₁r̥tóm. sdtóm. kʷósyo suHnúh₁ yú? wé h₃rēǵés suHnúh₁. h₁édtom médʰu-kʷe ph₃tóm. yú moy priHóh₁.`
  - gʷemt AOR.2DU gʷm̥tóm was tried first. It pushed pie-lex-gwemt to 7 uses, over the cap of 6, so h₁ert was used instead.

**Planted (all caught and named):**
- 0e0a825a: DAT.SG pótn̥yeh₂ey stands where the subject needs NOM pótnih₂.
- 9df9f66f: INS.PL démbʰis stands for the goal 'home', which needs acc. dṓm.
- 10db36f9: PRS.3PL h₁yénti stands in 'where are you going?', which needs 2sg h₁éysi.
- a3d0c45c: PRS.2SG h₁ési has a plural list of animals as its subject, which needs 3pl h₁sénti.
- 8ac7f519: NOM/ACC.PL médʰuh₂ stands for the mass singular médʰu.

## Minor

- afeea165 (00019): táwros is glossed 'wild bull, aurochs' and is yoked to a plough. The daughters (ταῦρος, taurus) mean a domestic bull, so the problem is the gloss more than the text. Left unchanged.
- 3f7fe825 (00026): bʰérmn̥ has no lexicon gloss (derived 'bear~') and was used for 'gift'. **Fixed:** replaced with pie-lex-deh3nom déh₃nom 'gift'.
- 10db36f9 (planted item, inherited from the real 00014): kú 'where' has a plain velar. This is the lexicon's own form, the same clash as kúdʰe in t023.
- Tier 1 lines:
  - 10c7f844: root-accented súHnum and the spelling h₃rḗḱs.
  - f097f194: Schleicher-type text, with no laryngeals, no accents and the spellings eest and yāi.
  - 30b98abd: (y) in parentheses and the spellings weukʷét and moi.
  - All three are faithful to their sources but clash with corpus notation.

## Outside the packet (the other 20 texts, scanned)

- One more number fix: in t3-t024-00040, two quarrelling brothers were addressed as súHnewes with a 2pl injunctive. This goes against brief rule 17, which puts natural pairs in the dual. **Fixed** to VOC.DU súHnuh₁ with mē HrudHtóm (INJ.2DU).
- Nothing else is wrong. Agreement checks that came out correct:
  - h₁ím agrees with masc. h₁ólos 'awl'.
  - Fem. tísres agrees with h₂óweyes.
  - Fem. méǵh₂ih₂m agrees with dʰwórm̥.
- One possible engine issue: in 00023, the middle 2sg secondary ending is -th₂e (sékʷeth₂e). Handbooks usually reconstruct *-th₂es (Ved. -thās). This is engine-wide, not a plan error.

After the fixes the gate is PASS: 40/40 exact, max lexeme uses 6 against a cap of 6, and 0 rejects.

## Blind back-translation

Six real-looking items were translated from the `pie` field alone, before any English was read: 4e14c8cb, 0e0a825a, 3bfdac0a, 2a9dc88d, 3c8b904e, 23747f69. All six agree in substance with their English.

| item | difference |
|---|---|
| 3c8b904e | none; exact match |
| 4e14c8cb | tense only ('I heard' against 'I hear') |
| 3bfdac0a | gerh₂ḗn was read as the common noun 'old man' rather than the name 'Crane' (a reviewer misreading) |
| 2a9dc88d | h₁opéy- and h₂éǵmn̥ were uncertain; the lexicon confirms 'give' and 'flock' |
| 23747f69 | wósh₂r̥ was uncertain; it is 'garlic' |

0e0a825a turned out to be a plant (DAT pótn̥yeh₂ey). The blind pass read through the wrong case to the intended meaning, so a back-translation alone does not catch case plants. The item-by-item grammar pass did catch it.

## Engine gaps (for the lead)

1. **The perfect has no 2DU/3DU cells, and the realizer falls back silently to the plural** (`num_fallback` du→pl). A plan that asks for the dual, as brief rule 17 says it should, gets a plural verb inside an otherwise dual clause, with no warning and no rejection. t023 66dc51f8 had the same root cause. The engine should either build PRF.2DU and PRF.3DU (*-(h₁)tóm? / Ved. -athur, -atur) or reject the request so that the planner picks the aorist.
2. The middle 2sg secondary ending is -th₂e, against the handbooks' *-th₂es. This should be checked centrally.

## Conversational quality

The batch is the most conversational Tier 3 batch so far and reads as real exchanges.

**What works:**
- **Question and answer is natural and idiomatic.** Yes/no questions are answered by echoing the verb, the inherited IE pattern (Lat. *venisne? venio*): h₂éǵrom h₂érh₃yesi? – h₂érh₃yoh₂; dedwóyth₂e? – dedwóyh₂e; gʷémesi? – gʷémoh₂. Wh-questions use kʷís, kʷíd, kú and kʷíh₁ correctly, and the answers pick up the questioned constituent.
- **Greetings have real formulas:**
  - 'kʷís gʰóstey túH? – h₁eǵóh₂ … h₁nómn̥-kʷe moy …', a name exchange.
  - 'kʷíh₁ gʷíh₃wesi?', 'how do you live?'.
  - The wishes gʷíh₃woyh₁s 'may you live' and dyḗws … h₂léksoyh₁t.
  - Welcomes with the perfect: gʷegʷómth₂e and h₂eh₂nóḱth₂e.
  - The guest-host script: sit, eat, drink, 'you are dear to me'.
- **Register is marked well.** Vocatives open nearly every turn. Enclitic moy, toy, nos and te stand in Wackernagel position. Imperatives, mē + injunctive, the optative of wish and the subjunctive of intention are kept apart.
- **Child and parent speech is distinct.** 'méh₂ter tr̥syóh₂' and the awl quarrel, with an appeal to the father, read as natural family talk.

**Weaknesses:**
- **Turn boundaries are not marked in the PIE.** The English has quotation marks, but the PIE runs the turns together, so a model cannot tell who is speaking. In 2a9dc88d the turns are 'give me the dog' / 'no' / 'I'll give two sheep' / 'no'. A speaker or turn marker in the record format would help much more than anything in the plans.
- **Formulas repeat across texts:**
  - 'kʷís gʰóstey túH' appears 2×.
  - 'l̥gʰdʰí swépnom-kʷe h₁áyso' appears 2×.
  - 'ḱḗr-kʷe moy méwdt' appears 3×.
  - 'pékʷtōr h₁édnom h₂réydʰeti' appears 3×.
  This is good for formula learning but narrow.
- **Some speech acts are missing.** The batch has no thanks, no farewell formula (beyond 'go, and may the gods lead you') and no polite request.
- **The texts are short.** They average 17 words, so most exchanges have only 2 to 4 turns.

**Verdict:** natural, well-registered beginner dialogue. It is suitable for teaching basic conversation, but turn segmentation is the main missing piece.

## Release-rule check (for the lead)

- Plant recall: 5/5. This meets the threshold of ≥ 4/5.
- Real wrong after fixes: 0/20. This is within the limit of ≤ 2/20.
- Gate: PASS.

This review does not set approval.
