# Tier-3 review: batch t085 (Horrors wave: raid and captivity)

The batch has 40 texts: 20 two-speaker dialogues, plus 7 tales, 6 laments, a quern song (`work song`), 5 charms (3 of them curses: 00035, 00038, 00040) and a prayer. Every sense used was checked against the full gloss, including éti 'also, too' (pie-lex-eti-2: "beyond, over; still, also, too"). The procedure was `docs/generation/reviewer-brief.md` (review-v1). I worked from handbook knowledge (Fortson, Beekes, Ringe, LIV², Mallory–Adams) and checked doubtful forms against a reverse index of every engine cell (`Lexicon.cells()`, `.participle_cells()`, closed class) and against full glosses (`Lexicon.meaning`). I did not read anything under `data/audits/`.

## 1. Calibrated packet

- Packet: `make_review_packet.py t085 --n 20 --plants 5 --tier1 3`. It has 28 items: 20 real, 5 planted, 3 Tier 1.
- Blind back-translation: I translated 6 items (fdc2a0ce, 636f0be6, 3efc0f93, 9491857e, 560dd235, 5ac851da) from the `pie` field alone, before seeing any English. The translations are in `docs/audits/packets/t085-blind-translations.jsonl`.
  - **Agreement: 6/6 in substance.** Three small differences:
    - 3efc0f93: I took h₂énHos to be the grandfather. It is pie-proj 'grandmother', so the error was mine.
    - 9491857e: I read the opening verb as "they carried". That reading came from the planted 3du.
    - 5ac851da: I read smḗyt as "smiled"; the English has "laughed". Both are senses in the gloss.
- Verdicts: `docs/audits/packets/t085-verdicts.jsonl`, saved before I opened `corpus/` or the plans. **sha256 `9330d5756162fc70c4b973fcbfe0e6e3eb5a1a119f8565f3195e4379241336e6`.**

| ok | minor | wrong |
|----|-------|-------|
| 21 | 2     | 5     |

**Score (`score_review.py`):** plant recall **5/5**, all 5 named. 0/3 Tier 1 items were judged wrong. Real items judged wrong: **0/20**; real minors: 2/20.

The 5 wrongs, all plants. Forms are given in the packet's spelling:
- ea46f9f0: `dṓm toy lubʰyómes?` is PRS.1PL; the English "Do you long for your home?" needs lubʰyési.
- 4240f7e6: `sḱéh₃ih₂h₁` is NOM/ACC.DU; "cover me with shadow" needs INS.SG sḱh₃yéh₂h₁.
- e6d7481d: `témHesos` is GEN/ABL; "burn in the darkness" needs LOC témHesi.
- 9491857e: `bʰéretām` is 3DU; "Wife, bring" needs IMP.2SG bʰére.
- 7bec75e5: `lewbʰóyh₁` is neuter NOM/ACC.DU; the address "beloved!" needs VOC.SG léwbʰe.

The 2 real minors (resolved through `resolve_review_items.py`):
- **t3-t085-00029** (3efc0f93): `h₁ésyeh₂s … népotm̥` and `h₁esh₂ṓy h₁ésyeh₂s h₂r̥ǵn̥tóm` use the anaphoric genitive "her" for the subject's own grandson and silver. Brief rule 19 asks for pie-lex-swos.
- **t3-t085-00017** (77b365ed): `ḱm̥tóm gʷṓs` puts acc. pl. 'cows' in apposition to 'hundred', where a genitive plural is the commoner inherited construction. This is how the engine builds numeral + MOD. It is a convention, not a plan error, so I am reporting it only.

## 2. Second pass: all 40 records

I read all 40 records sentence by sentence (speaker, PIE, per-sentence English, token cells) against planner-brief-v4, the in-world dialogue brief and its section "Horrors (wave t085–t088)".

**Horrors limits: no violations.**
- No sexual violence is depicted. Captivity is only named: girls and women are "carried off" or "sold to men of the sea", and they grind, weave or pour mead for their masters (00002, 00004, 00014, 00021, 00031, 00034, 00037, 00038).
- No gore for its own sake. The worst images are inherited epic ones: "may dogs and birds eat you" (00035), the unburied husband at the fence (00021), the dead brothers at the door (00005).
- No modern moral commentary. Vengeance, blood-price and curses are spoken in character (00005, 00016, 00038, 00040).
- Nothing modern and no coinages. pie-proj h₂énHos 'grandmother' and mógʰus 'boy' are flagged project reconstructions, which v4 allows in Tier 3.

**Format.** Every dialogue has exactly two speakers, and the user speaks first. Every turn answers the previous one, and answers repeat the verb of the question (gʷíh₃weti / gʷíh₃weti; ḱlush₁yési / ḱlush₁yóh₂; kénkesi / kénkoh₂).

**Points checked:**
- **Verbs of fearing:** `téwe deywóybʰos ne dedwóyh₂e` "I do not fear your gods" (00002) takes the ablative. The other fear verbs (bʰebʰóyh₂h₂e, bʰéyh₂m̥, tréset, troméyet) have no object.
- **Words the planners wrote around:**
  - raid = h₂éǵ- 'drive off' (cattle);
  - ransom = kʷoynéh₂ (its gloss includes "ransom") + kʷinéwti 'pay';
  - serve = grind, weave, carry water, with h₃órbʰos 'servant' (gloss: "servant, slave");
  - captive = kaptéh₂;
  - "price" = h₂elgʷʰós 'value, price'.
  In each case the PIE says what the English says.
- **Senses checked against the full gloss:**
  - h₂ewsér "at dawn" (sense 2), úd dr̥mént "ran out" (sense: "out"), nésm̥/nést "came home unharmed" (gloss: "escape, return home unharmed").
  - bʰr̥dʰént "captured" ("plunder, capture"), tḱéyti "lives" ("dwell"), téntlom "loom", stundénti "beat" ("push, hit"), mórtōs "men" ("mortal, man").
- **Athematic obliques, all correct:** pérunsu/pérunbʰos, bʰr̥h₁wéni, nékʷti/nékʷtsu, h₂ḱm̥néh₁, gʷénh₂n̥s, poh₂imn̥bʰós, h₂nr̥bʰós, swesr̥bʰís, ph₂wéni, dʰǵʰémi, mréy/mréys, h₂Hséh₂s/h₂Hséh₂i, h₃rēǵés/h₃rēǵéy, kh₃téwi, gʰostísu.
- **Enclitics:** all stand in second position, as in `swéh₂s me h₂Hséh₂s`.
- **Pronouns:** each he/she/it/they was checked against its referent. Two examples: neuter h₁íd for péḱu (00001), feminine h₁íh₂m̥ for kʷoynéh₂ (00017). The engine's 21 antecedent warnings were checked by hand, and all are correct: the antecedent sits more than two clauses back, the clause is impersonal, or the subject is singular.

**Second-pass findings (all minor; no new wrongs):**
1. **t3-t085-00029** (the packet minor above). **Fixed:** the plan's clause 3 now uses swos MOD, giving "she saw her own grandson" (`swóm … népotm̥`). Clause 4 ("her silver") still uses the anaphoric genitive, because pie-lex-swos is now at the batch cap of 7.
2. **t3-t085-00031:** `h₁ésyeh₂s-kʷe ḱóymosyo kéh₂nmn̥h₂` "she sang the songs of her village" has the same non-reflexive genitive. **Left unfixed** because of the same cap. The non-reflexive reading is grammatical; Vedic asya is used this way.
3. **t3-t085-00016:** the English "But I remember him." had no PIE counterpart for "But". **Fixed** in the plan's English: "I remember him."

**Real wrongs: 0 before the fixes, 0 after. Real minors: 2 in the packet, 3 including the second pass. 2 are fixed; 2 remain (00031, and the clause-4 genitive in 00029).** The 00017 numeral construction is an engine convention, not counted as a plan minor.

## 3. Fixes and gate

- **Plan edits** in `data/generation/plans/t085.jsonl`: t085-0029 clause 3 (POSS anaphoric_i → MOD pie-lex-swos, with the English updated) and t085-0016 clause 8 (English only).
- **Re-realized** with `realize_plans.py … --batch t085 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`.
- **Result:** 40/40 realized, 40 exact; 0 rejects; meter_exact 78/78 = 1.000; max lexeme uses 7 (swos); 1346 tokens; 270 distinct lexemes and 167 roots. **Gate: PASS.**

## 4. Engine and brief notes (report only)

- **Middle dual.** t085-0029 clause 7 plans a dual subject ("grandmother and grandson returned") with nesetor MID. The engine has no 3du middle cell, so the output is 3pl `nésonto`. This is a known engine limitation.
- **Numeral + noun.** ḱm̥tóm / déḱm̥ + a noun is built as an indeclinable MOD agreeing in case (`ḱm̥tóm gʷṓs`). A gen.-pl. option (*ḱm̥tóm gʷówom*) could be offered for "a hundred (of) cows".
- **Lexeme cap.** The cap stopped a correct reflexive (rule 19) in two places. The lead could exempt pie-lex-swos from the cap, as the copula is exempt.

## 5. Tone

The batch lands its tone. The horror is in plain facts: the father at the fence, the boats going west, the old woman who has forgotten her village's name, the ransom refused with a laugh. Grief, fear, anger and endurance run through it without relish or modern comment.

## 6. Follow-up (lead, after pie-lex-swos was exempted from the cap)

The two remaining reflexive slips now use swós:
- **t085-0029 clause 4:** now `h₁esh₂ṓy swóm h₂r̥ǵn̥tóm déh₃t` "She gave the master her own silver."
- **t085-0031 clause 10:** now `swósyo-kʷe ḱóymosyo kéh₂nmn̥h₂` "the songs of her own village".

After re-realizing, the gate is **PASS**: 40/40 exact, meter 78/78, max capped lexeme 6. **Real minors remaining: none.** The 00017 numeral construction is an engine convention, not counted.
