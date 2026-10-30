# Tier 3b review: t3b-004 (review-v1 adapted to Tier 3b, 2026-10-30)

40 chat dialogues between `user` and `model` on herding, fields, weather and travel. They were planned under `planner-brief-3b.md` v3 (`tier3b-planner-v3`), where the model is a human PIE speaker. Release approval belongs to the lead, and `data/generation/releases/t3b-004.json` stays `pending`.

## Procedure

The review is calibrated, as for t3b-002. The packet comes from `make_review_packet.py t3b-004 --tier tier3b --n 20 --plants 5 --tier1 3` and has 28 items: 20 real, 5 planted and 3 Tier 1.

1. **Blind back-translation.** I translated 6 items from the `pie` field alone, before I looked at any English. The file is `docs/audits/packets/t3b-004-blind-translations.jsonl`, and the items are a7ff372e, ec93fc79, 0a4443d8, 2b16c5eb, f8ee0f90 and b2180952.
2. **Verdicts.** I judged all 28 items before I opened `corpus/tier3b/` or the plans. Doubtful forms were checked against `Lexicon.cells()`, `participle_cells()` and `closed_class.json` with a reverse form index. The file is `docs/audits/packets/t3b-004-verdicts.jsonl`, sha256 `1efa024caa664f00e1bf70b9aad894c9256e32911e357b83e96f5ad22439af81`. It was saved before `resolve_review_items.py` ran, and that script printed the same hash.
3. **Resolve and score.** I ran `resolve_review_items.py` and then `score_review.py`, which wrote `data/audits/t3b-004-calibration.json`. I did not open that file or the key.
4. **Second pass.** I read all 40 records sentence by sentence, with speaker, PIE, the English for each sentence and the token gloss. The pass checked grammar, the verb senses against their glosses, brief §5 (character), archaic-first, whether the English matches the PIE, and whether each turn answers the one before.
   - The 5 records seen in the packet only in planted form are 0011, 0014, 0022, 0035 and 0039. Their real forms were judged in this pass only, so those verdicts are uncalibrated.

**Disclosure:** while reading the Procedure section of `tier3b-t3b-002-review.md`, my `sed` range ran past it and I also saw that review's findings. They concern a different batch and give no information about this batch's key or plants.

## 1. Calibration

- **Plant recall: 5/5, all named.** Every plant was a single-cell inflection error:

  | item | planted form | what it is | what the sentence needs |
  |---|---|---|---|
  | a7ff372e | wl̥kʷih₂és | GEN/ABL.SG | NOM.SG wl̥kʷíh₂s, the subject of gʷm̥sḱéti ("the she-wolf comes") |
  | 561dd882 | h₂ukstā́m | AOR.3DU | 3SG h₂wékst, with the singular subject ǵr̥h₂nóm ("your grain") |
  | 61894da7 | ḱóymōy | DAT.SG | NOM.SG ḱóymos ("where is the village of …") |
  | 3ef42fa7 | ǵʰéyomes | NOM.PL | LOC ǵʰyémi ("in winter") |
  | 0a4443d8 | deywóybʰos | DAT/ABL.PL | NOM.PL deywṓs, the subject of dh₃ih₁ént ("may the gods give") |

- **Tier 1 items:** 0/3 judged wrong.
- **Real items:** 0 wrong and 0 minor out of 20, before and after the fixes. None of the three fixed records is a packet item.
- **Blind back-translation:** 6/6 items agree with the plan English in overall sense, but I misread one sentence in 2b16c5eb. The differences:
  - a7ff372e: in the blind pass I read the planted wl̥kʷih₂és as a plural, "she-wolves come". I flagged it as a case error only in the verdict pass.
  - 0a4443d8: the blind pass did not notice the planted deywóybʰos.
  - 2b16c5eb: I misread h₁éymos, which is DAT.PL "to them", as a verb, "we go". So I got the sentence "In the evening I sing to them" wrong.
  - Unsure blind, confirmed afterwards:
    - ḱlḗm and drḗm are AOR.1SG by Stang's law.
    - ḱléwse is the IMP of ḱléwseti 'be listening'.
    - léytt is the AOR of 'go away'.
    - dedwóye is the PRF of 'be afraid'.

## 2. Second pass: counts

| | wrong | minor | ok |
|---|---|---|---|
| calibrated packet, real items (20), before fixes | 0 | 0 | 20 |
| calibrated packet, real items (20), after fixes | 0 | 0 | 20 |
| all 40 records (second pass), before fixes | 1 | 2 | 37 |
| all 40 records, after fixes (re-realized) | 0 | 0 | 40 |

**Character (brief §5): no violations.**
- The model is human in all 40 dialogues. It has:
  - a daughter (0007, 0031) and a son (0003, 0022);
  - a father (0018), and brothers, a sister, a father and a mother (0033);
  - a herd, a cow stall, a hearth (0014), a boat (0016) and a horse (0038).
- No line has the model claim to be a machine or to have no home, body or parents.
- Modern things (the fire-wagon, i.e. a train, in 0024; the bicycle in 0026) are strange to it, as the brief asks: "Who draws it?", "I would be afraid in it! I shall drive my horses", "Does it eat grain? … I am laughing!"

**Archaic-first is followed.** Only 3 of 274 sentences contain a coinage (1.1%): h₁n̥gʷniwóǵʰos in 0024 and dwikʷékʷlos in 0026, both brought in by the user. That is 3 neologism tokens out of 937 (0.3%).

**Verb senses** were checked against their glosses for every verb:
- There is no causative-for-intransitive slip. The only causative is moréyeti 'kill', glossed 'kill'.
- These stay within their glosses: lubʰyéti 'love, desire', séngʷʰeti 'sing, recite', pléh₁dʰeti 'swell; increase', h₂susyéti 'be dry', smḗyti 'smile, laugh', h₂ew 'again', and pī́ts 'pitch; pine tree'.

**The turns answer each other.** Examples: 0005, the cow found ("That is my cow! I praise the gods"); 0016, the river crossing ("And my horse?" "It will swim"); 0028 ("Dogs do not laugh!" "My dogs do laugh!").

## 3. Findings and fixes

All fixes are in `data/generation/plans/t3b-004.jsonl`. The batch was re-realized with the batch command; a backup of the pre-fix plans is in the scratchpad.

**Wrong (fixed):**
- **0008: dwóbʰih₁ ugʷsn̥bʰís**, under "with two oxen". The numeral is INS.DU but the noun is INS.PL, so they disagree in number.
  - The plan asked for `num: "DU"`. The engine has no INS.DU cell for ugʷsḗn, and it silently realized the plural (engine gap 1).
  - Fix: the numeral is dropped and the slot is now INS PL → h₂éǵrom ugʷsn̥bʰís h₂érh₃yeti, "He is ploughing the field with the oxen."

**Minor (fixed):** both are the case taken by 'fear' (engine/brief gap 2).
- **0006: ǵʰwḗres péh₂wr̥ bʰebʰih₂ḗr**, "Wild beasts fear fire".
  - The fear object was in the ACC. The inherited construction of *bʰeyh₂- puts what is feared in the ablative (Ved. *bhī-* + ABL) or the genitive (Lith. *bijótis*, OCS *bojati sę*).
  - Fix: role ABL → ph₂wéns.
- **0038: ne te bʰebʰóyh₂e**, "He is not afraid of you".
  - Same problem as 0006.
  - Fix: role ABL, not enclitic → twéd ne bʰebʰóyh₂e.

**Noted, not errors:**
- The realizer's warnings that h₂éǵeti 'drive' and the subjunctive of h₂éǵt 'say' look alike (0003, 0033, 0035). In context these verbs all mean 'drive'.
- **The imperfect (PST) is used for single completed past events**, and none of these is counted as minor. The imperfect is a real past tense, and the English matches it. t3b-002 left kʷrinéh₂t as is for a similar reason.
  - Examples: gʷʰnént "slew" (0034), stéygʰes/stéygʰom "climbed" (0019), Hrumptó "broke" (0017), duktā́m "drew" (0018), smḗyt "laughed" (0031), gʷʰr̥néwt "warmed" (0019), moréyet "killed" (0020).
  - For gʷʰen-, smey- and the causative moréyeti, the lexicon has no aorist, so PST is the only choice.
  - For gʷʰer- the only aorist is intransitive gʷʰért 'become warm', which cannot take the object in "the sun warmed us". So the imperfect of the nasal present is right there.
  - Aorist lexemes do exist for three of these (steyght/stḗyghst, Hrewpt, dēwkst). A planner could prefer them for the perfective sense. This is a style point for the brief, not an error.
- The antecedent warnings in the how-do-I-say dialogues (0027, 0028, 0039, 0040). Each pronoun points to a quoted sentence or to the grain, so the reference is correct.

## 4. Gate

The batch was re-realized after the fixes. The gate is **PASS**:
- 40/40 realized and all exact, with a reject rate of 0.0;
- max lexeme uses 6, with no duplicates;
- 109 distinct roots and 200 distinct lexemes;
- coined-sentence share 0.011.

The 3 `accent_defect_tokens` were already in the initial run, so they are unchanged by this review.

## 5. Engine and brief gaps (for the lead)

1. **The dual oblique falls back silently to the plural.** When a slot asks for `num: "DU"` in a case that has no dual cell (INS, DAT or ABL.DU are not built), the noun comes out plural. The numeral 'two' still takes the dual (dwóbʰih₁), so the result is a dual/plural mismatch, and there is no reject or warning.
   - t3b-002 found the same fallback (tóybʰos for a DU slot).
   - The realizer should reject the plan or warn. The other fix is to build the dual oblique cells: INS/DAT/ABL *-bʰyoh₁/-moh₁, and GEN/LOC *-h₁ows.
2. **Verbs have no case frame.** The lexicon does not record which case a verb takes, so planners default to OBJ (ACC) for "fear X". bʰebʰóyh₂e and bʰéyh₂t should be marked ABL (or GEN), or the brief should say so. A general `governs` field on verb entries would also catch similar cases.
