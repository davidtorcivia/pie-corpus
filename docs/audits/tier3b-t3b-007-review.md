# Tier 3b review: t3b-007 (review-v1 adapted to Tier 3b, 2026-10-30)

40 "curious visitor" dialogues (planner-brief-3b.md §8): a modern user meets a human PIE speaker. Planned under
`tier3b-planner-v3`. Release approval is the lead's: `data/generation/releases/t3b-007.json` was not touched.

## Procedure

Calibrated, as in t3b-002. The packet was built with `make_review_packet.py t3b-007 --tier tier3b --n 20 --plants 5 --tier1 3`,
which gave 28 items: 20 real, 5 planted and 3 Tier 1. I did not open anything under data/audits/.

1. **Blind back-translation.** I translated 6 items seeing only `pie`, before I looked at any English:
   `docs/audits/packets/t3b-007-blind-translations.jsonl` (7d26835b, 7bcb83e6, 9bd93edd, 225a7447, 45e359f8, 44a69528).
   - All 6 agree in sense with the plan English.
   - 7bcb83e6 was the planted item among the six. Blind, I read h₂éǵroybʰos as plural "in the fields" and did **not** flag it. I caught the case error only in the verdicts pass. Blind, I did flag HrewdH- ('shout' or 'weep'?; see 0022 below) and h₁ésmi.
   - Three blind doubts were cleared once I checked the lexicon:
     - h₁yód 'when' is a conjunction;
     - spéleh₂ is the NOM/ACC.PL of neuter spélom;
     - h₁íns can resume gʷṓs because gʷṓws is masculine in the lexicon.
   - One reading was off: blind, I parsed the sentence "dʰugh₂trṓm toy moy suHnéwes ph₂téres" wrongly. Its meaning is "the sons of your daughters are my fathers".
2. **Verdicts.** I judged all 28 items before opening the corpus or the plans:
   - file: `docs/audits/packets/t3b-007-verdicts.jsonl`;
   - sha256: `7fbaeb7649616fbed948042a3b2ad528ac38d8c4bcab0cb0282338b4a9575679`.
   - After that I ran `resolve_review_items.py` and then `score_review.py`.
3. **Score** (`data/audits/t3b-007-calibration.json`):
   - **Plant recall: 5/5.** All five plants were named:
     - 7bcb83e6: h₂éǵroybʰos, DAT/ABL.PL for LOC.SG "in the field";
     - b9371fb8: gʷémtu, IMP.3SG for 2SG "Come back";
     - c5313e12: márkons, ACC.PL for NOM.PL, the subject of h₁sénti;
     - ec9bf972: ḱósmi dinósyo, GEN for LOC dinóy "today";
     - de7b860d: nékʷth₁, INS for ABL after a verb of fearing.
   - Tier 1 items judged wrong: 0/3.
   - Real items: 0 wrong and 2 minor out of 20.
4. **Second pass.** I read all 40 records in full, each turn with its PIE, English and tokens, against brief §5 and §8.
   - I also read the plan clauses for the 10 `english_only` sentences, which the record's `generator.plan` leaves out.
   - The 5 planted records were seen only in planted form in the packet: 0011, 0014, 0022, 0035 and 0039. Their verdicts come only from this pass and are **uncalibrated**.

## 1. Counts

| | wrong | minor | ok |
|---|---|---|---|
| calibrated packet, real items (20), before fixes | 0 | 2 | 18 |
| calibrated packet, real items (20), after fixes | 0 | 0 | 20 |
| all 40 records (second pass), before fixes | 0 | 5 | 35 |
| all 40 records, after fixes (re-realized) | 0 | 0 | 40 |

- Packet minor 98b026e3 (0037) was **reclassified ok**. I had flagged wéydsoh₂ under "I want to see him" as a stretched sense, but `pie-lex-weydseti` is glossed 'to want to see', so it is exact.
- The other packet minor, c427b214 (0009), is fixed (see below).
- Grammar outside the plants was clean throughout:
  - duals: tkswós 1DU, h₂éǵetes and h₂léksetes 3DU, tkstés, dwóh₁ wiHróh₁;
  - ablatives of fear: mr̥téys, kʷósmōd, h₁némn̥s, wĺ̥kʷoybʰos, nékʷts;
  - optatives: dh₃ih₁ént, ph₂syéh₁t, h₂uksyéh₁t, mē … gʰrémoyh₁ent, mē tḱiyéh₁m̥;
  - subjunctives used as futures: méroh₂, gʷíh₃wēti, gʷr̥néHoh₂, péh₃omes;
  - the bahuvrihi names (h₁suḱléwēs, h₂nr̥ménēs, h₁suh₁éḱweh₂m, HeHḱuwĺ̥kʷom).

## 2. Findings and fixes

All five were fixed in `data/generation/plans/t3b-007.jsonl` and re-realized.

- **0022 (verb sense):** "Do you cry out to her? / I do not cry out. / I cry out to my sister in the field."
  - The verb was HréwdHti, whose root is HrewdH- 'to weep' (Ved. *róditi*). Calling to someone far away is not weeping.
  - Changed to `pie-lex-gjhuHeyeti` ǵʰuHéyeti 'call (upon)' (Ved. *hávate*), with an ACC object.
  - It now reads: h₁íh₂m̥ ǵʰuHéyesi? — ne ǵʰuHéyoh₂. … swésorm̥ moy h₂éǵroy ǵʰuHéyoh₂ ḱlush₁yéti-kʷe me. "Do you call to her?" "I do not call." … "I call to my sister in the field, and she hears me."
- **0009 (tense):**
  - widét (AOR) stood under "There he *finds* his fathers". It is now SBJV widḗti, "There he will find".
  - gʷíh₃weti (PRS.IND) stood under "my fame *will live*". It is now SBJV gʷíh₃wēti, the form 0034 already uses.
- **0014 (English tense):** h₁ludʰét is an aorist, but the English was "sleep comes to me". Changed to "And then sleep came to me!"
- **0006 (English):**
  - The PIE is deywóybʰos h₁erkʷóns gʷr̥néHti (DAT gods, ACC hymns), but the English said "praises the gods with hymns". Changed to "sings hymns of praise to the gods" (gloss: 'praise, extol (in song)').
  - "I *also* sit in the evening" had no slot for "also", so "also" was dropped.
- **0028 (English):** "*But* he lies under the earth" had no slot for "but", so "But" was dropped.

Not changed:
- **0031:** h₂éwh₂os stands under "uncle", and the lexicon gloss includes 'maternal uncle', so this is ok. Elsewhere in the batch h₂éwh₂os means "grandfather" (0005, 0006, 0016, 0023, 0028).
- **0012:** "Did they kill them? — They killed two men, and three fled." The pronoun reference is loose, but the PIE and the English match.
- **0040:** stéygʰoh₂ "I will walk" is the present used as a future, which is acceptable.

## 3. Character (§5) and the curious visitor (§8)

**Violations: 0 character, 0 §8.**

- **The model is a person.** Nowhere is the model a machine, and it never says it lacks a body, a home or parents:
  - it has a body: "I am real; touch my hand. Is it warm?" (0025);
  - it has a home: "You are in my home" (0029), "sit down at my fire" (0001);
  - it is mortal: "gods do not die, and I shall die" (0026);
  - it has a family: a grandmother, grandfather, brothers, sisters, a husband and children (0002, 0004, 0005, 0014).
- **Coinages:** none in any turn. Neologism tokens are 0/1185 and coined sentences 0/301.
- **Modern things.** These dialogues are 0019–0024, 6 of 40, within the brief's 1 in 4. The model never knows a modern thing:
  - it asks "What is that?" or says "I do not know that word / those words";
  - it then compares the thing with its own world:
    - a car is "a wagon that burns!… May my horses never hear of it!";
    - an airplane is "a wagon of the sky! Did you see Father Sky?";
    - electric light gets "Is it the Dawn? Do you carry a star in your hands?… Then you are gods!";
    - a phone gets "Is a god in it?";
    - a city gets "Who feeds them?… May I never dwell there!".
- **english_only.** The batch has 10 such sentences, all spoken by the user, each one a whole sentence carrying a modern word: phone, car, engine/gasoline, electric lights, airplane/machine, city of ten million, supermarket. One is borderline: 0019 "I come from the future, from the year 2026" carries no single modern word, but year counting is modern. It is acceptable.
  - Every model turn after an english_only sentence makes sense ("What is that?").
  - In every case the user then explains in PIE.
- **Every dialogue opens with the user.** The openings are about half greetings and half straight questions.
- **§8 coverage.** All seven ask-types appear:
  - who are you (0001–0005);
  - your world (0007–0012);
  - your language (0013, 0015–0018);
  - then and now (0019–0024);
  - testing (0025–0029);
  - small talk, including an insult answered with wit (0030–0035);
  - advice (0036–0040).
- **Turn-taking.** Each turn answers the one before. The speaker asks back in most dialogues ("And what did you eat?", "And what is your name?", "Now you sing me a song!").

## 4. Gate

The batch was re-realized with `realize_plans.py data/generation/plans/t3b-007.jsonl --batch t3b-007 --tier3b --model claude-opus-5-5 --prompt-id tier3b-planner-v3`:
- 40/40 realized exact, 0 rejects;
- **gate PASS**;
- 186 distinct lexemes and 111 roots;
- max lexeme uses 6;
- coined_sentence_share 0.0.

The 10 warnings are all benign:
- h₂éǵ- 'drive' forms are homographs with h₂eǵ- 'say' SBJV;
- 4 antecedent warnings point at referents outside the window: h₁ésmi "in it" = the phone in an english_only sentence, tód = the phrase being taught;
- the impersonal "It rained" stands next to a VOC.

## 5. For the lead (engine and brief)

- **`accent_defect_tokens` = 4.** All four are the adverb h₂ew 'back' (`pie-lex-h2ew`, 0012, 0035 ×2, 0040), which carries no accent. It is a lexicon or accent-lint item, not a plan error.
- **The record's `generator.plan.clauses` omits english_only clauses.** They are present in the record's `english` text and its `english_only` field, which `pie/export_chat.py` (`english_only_dialogue`) reads, so the export is fine. A reviewer reading only the clause list sees "What is that?" with nothing before it. This is a reviewing hazard, not a data error.
- **HrewdH- gloss.** `pie-lex-HrewdHti` is glossed "to cry (vocally)". The ambiguous English "cry" invited the "cry out / call" use in 0022. The gloss 'to weep, wail' would prevent this.

## 6. Favourite exchange (0023)

*móri dedórḱth₂e? — h₁íd ne dedórḱh₂e, h₂éwh₂os moy h₁íd dedórḱe. móri méǵh₂ wódr̥.* [EN: "I flew over the sea in an airplane."] *— kʷíd tód?* [EN: "It is a big machine that flies like a bird."] *— diwés wóǵʰos! ph₂térm̥ dyḗm widés? — h₁ím ne widóm. — nu me móri wédʰe.*

"Have you seen the sea?" "I have not seen it; my grandfather has. The sea is a great water." "I flew over the sea in an airplane." "What is that?" "It is a big machine that flies like a bird." "A wagon of the sky! Did you see Father Sky?" "I did not see him." "Then lead me to the sea!"
