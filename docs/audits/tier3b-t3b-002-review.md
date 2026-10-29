# Tier 3b review: t3b-002 (review-v1 adapted to Tier 3b, 2026-10-29)

40 everyday "modern PIE" chat dialogues between `user` and `model`, planned under `planner-brief-3b.md` (v2,
`tier3b-planner-v2`). Release approval is the lead's: `data/generation/releases/t3b-002.json` stays `pending`.

## Procedure

Calibrated, as in t3b-001. The packet was built with `make_review_packet.py t3b-002 --tier tier3b --n 20 --plants 5 --tier1 3`,
which gave 28 items: 20 real, 5 planted and 3 Tier 1.

1. **Blind back-translation.** I translated 6 items seeing only `pie`, before I looked at any English:
   `docs/audits/packets/t3b-002-blind-translations.jsonl`.
   - All 6 agree in sense with the plan English.
   - My blind notes flagged two forms that later proved to be plants: h₁ési (157a7221) and stóygʰoh₁. The items with stóygʰoh₁ were not in the blind six.
   - Two senses I didn't recognise blind:
     - stewd- 'become cold' (LIV);
     - séngʷm̥ 'fell' (sengʷ- 'sink, fall down').
2. **Verdicts.** I judged all 28 items before opening the corpus or the plans: `docs/audits/packets/t3b-002-verdicts.jsonl`,
   sha256 `d3b563bc1ad5ebaf8fa891405a04947b958fbdf039e03d4608a4d9928902ac28`. The file was committed in 02efc2f before
   `resolve_review_items.py` was run.
3. **Score** (`data/audits/t3b-002-calibration.json`):
   - **Plant recall: 4/5**, and all 4 caught plants were named.
     - 157a7221: h₁ési, 2SG for 3SG.
     - 3c7d505c: ph₂teres, NOM.PL for NOM.SG.
     - 6ad8f0fd: stérgetes, DU for 1SG.
     - 9516a835: stóygʰoh₁, INS/DU for NOM.SG.
   - **The missed plant** was 37a8f92b, the otter dialogue: wédesbʰis (INS.PL) for LOC.SG wédesi, under "swift in the water". I had marked the item ok.
     - I found it during the second-pass read of record 0022, not by diffing the packet.
     - Grading this as a miss is correct: an instrumental plural can be read as "in the waters", so I let it pass.
   - Tier 1 items judged wrong: 0/3.
   - Real items: 0 wrong and 5 minor out of 20.
4. **Second pass.** I read all 40 records in full, sentence by sentence, with speaker, PIE, per-sentence English and gloss.
   - This pass checked character (brief §5), archaic-first, the English-to-PIE match, and whether each turn answers the one before.
   - The 5 records seen only in planted form are 0003, 0011, 0014, 0022 and 0039. Their verdicts come only from this pass and are **uncalibrated**.

## 1. Counts

| | wrong | minor | ok |
|---|---|---|---|
| calibrated packet, real items (20), before fixes | 0 | 5 | 15 |
| calibrated packet, real items (20), after fixes | 0 | 2 | 18 |
| all 40 records (second pass), before fixes | 0 | 9 | 31 |
| all 40 records, after fixes (re-realized) | 0 | 6 | 34 |

Grammar was clean everywhere outside the plants:
- agreement and case were correct;
- person was correct, including the model's 1st person (h₁eǵóh₂ kʷértrom, ne h₁ḗdmi, dṓm moy ne h₁ésti, sóh₂wl̥ ne dedórḱh₂e);
- voice was correct (wésh₂er, ḱéyor, ǵn̥h₁yéto, nésomedʰh₂).

The archaic morphology was handled well:
- the neuter plural takes a singular verb (nébʰesh₂ gʷm̥sḱéti, 0002);
- the perfect 3PL in -ēr (stesth₂ḗr, bʰebʰih₂ḗr);
- the Narten present ne h₁ḗdmi;
- the subjunctive used as a future (bʰúHeti, déh₃eti, séngʷʰōh₂);
- the 2DU optative ḱóm sméyih₁tom.

## 2. Findings and fixes

**Fixed in the plans** (re-realized):

- **0021 (character, brief §5):** "Come in, guest! Be dear to us! Drink this wine and sit down." Here the model plays a host with a house and a household ("us"), but the brief says it has no home.
  - Rewritten so that the guest is the user's, and the model gives advice:
    - "gʰóstis moy ḱóymom h₁ludʰét. tr̥syéti ḱémh₂t-kʷe." "A guest arrived at my village. He is thirsty, and he has grown tired."
    - "h₁ésmey wéyh₁onm̥ bʰére h₁ím-kʷe h₂Hséh₂i sodéye." "Bring him wine, and seat him at the hearth!"
    - "píph₃eti méwdt-kʷe." "He is drinking, and he has grown glad."
    - "túH h₁suménēs." "You are kindly."
  - The genre changed from greeting to dialogue. Every lexeme is inherited, and none is over its cap.
- **0009 (English):** "*But* the shepherd's dog guarded them" had no slot for "but" → "The shepherd's dog guarded them."
- **0010 (English tense):** mélh₃t and méwdt are aorists, but the English said "comes forth" and "grows glad" → "has come forth", "has grown glad".
- **0030 (English sense):** wr̥h₁ḗn is glossed 'lamb' (Gk ἀρήν), but the English had "ram" → "He gave me a lamb."

**Minor, left as is** (each with its reason):

- **0007, 0019, 0030: déh₃ut.** These use `pie-lex-deh3ut`, the AOR of the LIV-uncertain deh₃w- (Lat. *duit*), for "gave". The standard déh₃t is used elsewhere in the batch.
  - The form is well built, but the batch mixes the two "give" aorists.
  - Switching is blocked: `pie-lex-deh3t` is already at the 6-use cap.
  - The planner presumably chose déh₃ut to stay under the cap. The lead may want the brief to say which "give" aorist to use.
- **0007: kʷrinéh₂t.** This is the imperfect of the nasal present, under "bought". kʷreyh₂- has no aorist in the lexicon, so the engine's PST is the only choice.
- **0012: moḱs 'soon, quickly' under "early"** ("I woke up early"). This stretches the sense.
  - The better wording, h₂usési "at dawn", is blocked because `pie-lex-h2ewsoxs` is at the 6-use cap.
- **0014: tóybʰos (DAT.PL) for a plan slot marked DU** ("Give them" = the father and mother, after ACC.DU tóh₁). This is an engine data gap; see §4.
- **0040: linékʷmi "I am leaving".** leykʷ- is transitive ('leave something behind'), so with no object it stretches to 'depart'.

**Reclassified ok in the second pass:** 0029 séngʷm̥ "I fell into the water". The lexicon glosses the AOR as 'fall down', so the verb stays within its gloss.

## 3. Conversational quality

**Verdict: good. This batch reads like a living language you converse with, not a talking dictionary.**

What works:
- **Topics:** 35 of the 40 dialogues are everyday: weather, cattle, buying a horse, selling wool, family, an old dog, a snake in the field, a sea trip, a newborn nephew, travel and partings.
- **Model as machine:** only 5 dialogues are about the model (0031–0034, 0036), within the brief's limit of 1 in 5. In those, the model is honest and playful:
  - "wékʷesh₂ píph₃oh₂" "I drink words!" in 0032;
  - "smimń̥bʰos smḗymi" "I laugh at jokes", followed by a joke, in 0036.
- **Requests** are realistic and are about a quarter of the batch:
  - How do I say …? in 0003, 0005, 0026 and 0039;
  - Tell me / sing / write in 0009, 0010, 0024, 0028 and 0034;
  - What is …? in 0022 and 0025.
- **Replies answer the turn before** and often add something: advice, a follow-up question, a joke or a blessing. Examples:
  - 0004: "Do not drink much!" "I know. I am not a boy."
  - 0029: "Why was he laughing?" "I fell into the water."
  - 0035: "Has it become warm at your home?" "I have no home. I have not seen the sun. Tell me of your sun!"
- **Idioms** come from the daughters, not from coinages:
  - "Be well" (kéh₂ilos h₁sdʰí);
  - "May the gods guard you on the path";
  - "giver of good things", h₁uséwōm déh₃tōr (Ved. *dātā vasūnām*);
  - the dawn hymn in 0024;
  - the sun riddle in 0023.

Weak spots (none fixed, since none is an error):
- 0012: "Now cook something!" → "I am drinking water." is only loosely responsive.
- 0028: "Then you are well!" is a slight non sequitur after "I walked to the field".
- 0001: the model's opening "Come, dear one!" is the brief's greeting formula, but it sits a little oddly on a speaker with no place to come to.

**Archaic-first:** 12 of 261 sentences contain a coinage (4.6%), all in the machine dialogues or in the brief's thanks idiom (0036). Neologism tokens are 13/801 (1.6%). No coinage stands where an inherited word exists, and joy is mówdos throughout.

**Held-out roots:** no token in t3b-002 belongs to a root family held out by `pie.export.eval_root`.

## 4. Gate

`realize_plans.py data/generation/plans/t3b-002.jsonl --batch t3b-002 --tier3b --model claude-opus-5-5 --prompt-id tier3b-planner-v2`:
- 40/40 realized exact, 0 rejects;
- **gate PASS**, including `coined_sentence_share<=0.25` (0.046) and the per-sentence English check;
- 195 distinct lexemes and 113 roots;
- max lexeme uses 6;
- 2 antecedent warnings (0001, 0015): neuter tód "that" refers to the preceding event, which is fine.

`tests/test_neologisms.py`: 14 passed.

## 5. For the lead (engine and brief)

- **No oblique dual in `closed:demonstrative_so`.** Only NOM/ACC.DU tóh₁ exist, so a DU IO silently takes the flagged `du->pl` fallback (0014 tóybʰos). Adding DAT/ABL/INS.DU *tóybʰyoh₁* (Ved. *tā́bhyām*), GEN/LOC.DU *tóyh₁ows* would fix it.
- **`words_per_sentence` equals `words_per_record`** (19.15) in the batch report. With 801 tokens and 261 sentences, the true figure is about 3.1 words per sentence, so the metric seems to divide by records.
- **Two "give" aorists.** déh₃t (deh₃-) and déh₃ut (LIV-uncertain deh₃w-) both enter chat data. The brief could name déh₃t as the default and point to dédeh₃ti or a subjunctive when the cap bites.
- **Caps on everyday words.** The 6-use cap on everyday words (h₂éwsōs, déh₃t, dṓm, gʷémt, h₁wésus) already blocks the natural fix in two places in a 40-dialogue batch.
- **drḗm** (AOR.1SG of drem-, from *drém-m̥) is an engine convention, not an error in this batch.

## 6. t3b-001 record 0019

Not changed, on the coordinator's instruction: the owner ruled that *h₁ewH- 'help' is core vocabulary and must not be held out, and another agent is protecting it.

## 7. Sample dialogues after the fixes

**0035**: *sóh₂wl̥ h₁idʰé mélh₃t. démi toy gʷʰért? — dṓm moy ne h₁ésti. sóh₂wl̥ ne dedórḱh₂e. sóh₂wl̥ moy toy mluHdʰí. — h₁íd gʷʰermóm h₂éweyes-kʷe kh₂nónti.*
"The sun has come out here. Has it become warm at your home?" "I have no home. I have not seen the sun. Tell me of your sun!" "It is warm, and the birds are singing."

**0004**: *méh₂tēr moy mélit déh₃t. — mélit swéh₂dos. h₁íd h₂éḱh₃s? — h₁íd h₂éḱh₃m̥ médʰu-kʷe péh₃m̥. — médʰu mówdom dédeh₃ti. polh₁ú mē péh₃s. — wóydh₂e. h₁eǵóh₂ ne mógʰus.*
"Mother gave me honey." "Honey is a pleasure. Did you eat it?" "I ate it, and I drank mead." "Mead gives joy. Do not drink much!" "I know. I am not a boy."
