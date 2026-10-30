# Tier 3 batch t042 review: in-world dialogues, weather and the seasons (`review-v1`)

Reviewer: Claude Opus 5.5 (calibrated reviewer), 2026-10-30. Procedure: docs/generation/reviewer-brief.md.
Release approval is the lead's decision. This review does not set it.

## Packet and calibration

- Packet: `scripts/make_review_packet.py t042 --n 20 --plants 5 --tier1 3`. It produced 28 items: 20 real, 5 planted, 3 Tier 1.
- Blind back-translation of 6 items was done before any English was printed: `docs/audits/packets/t042-blind-translations.jsonl`, sha256 `0dd70977…4850`.
- Verdicts were written before corpus/ or the plans were opened: `docs/audits/packets/t042-verdicts.jsonl`.
  - sha256 `3ca4db50653d28a1b4c3c4fc56859540da6fd02b9651e3bb80330079b8b25bec`. `resolve_review_items.py` confirmed the same hash.
- Score (`scripts/score_review.py t042`):
  - **plant recall 5/5**, all 5 named by their exact form;
  - Tier 1 items judged wrong: 0/3;
  - real items: **0 wrong, 2 minor** out of 20.

Plants caught, each with the issue as written in the verdicts:

| item | planted form | issue |
|---|---|---|
| c0b71eea | sríHǵesh₁ | instrumental used as the subject of h₁épt |
| d820f739 | ph₂teres | VOC.PL used to address one father |
| b27ddb79 | h₁ités | dual verb with a plural subject (geese) |
| 74a4cc4a | wetséh₂i | does not agree with masc. nom. uksḗn |
| 7164edc2 | yéh₂ete | 2PL where "let us" needs 1PL |

### Blind-translation agreement

Agreement was good on all 6 items. Gaps came from vocabulary I did not know, not from the grammar:

| item | agreement | notes |
|---|---|---|
| 0f8e27ff | full | rendered h₁súmenes as "kind one" |
| f2d53c40 | full | |
| 37784b8d | 5/6 sentences | could not identify stéwd- 'become cold' |
| 69dcd7ed | 3/4 | stéwdt again |
| f9cb0381 | 4/5 | misread h₁uséwōm … déh₃tor 'giver of good things' |
| d24b0e20 | about 5/7 | h₁áyso read as 'ask', not 'take'; ḱéyweh₂ 'dear' read as a verb |

None of the misreadings shows an error in the PIE.

## Second pass: all 40 records against planner-brief-dialogue-inworld.md

Each record was read in full: speakers, PIE, English per sentence, and gloss. Results:

- **In-world:** no modern or coined content in any record. The world is herds, hearth, kin, guests, the king, Perkʷunos, wolves, the seasons. The thanks and welcome idioms follow the brief: túH moy ḱéyweh₂ 'you are dear to me', and priHós h₁sdʰí 'be dear to us'.
- **Turns:** each turn answers the one before in all 40 dialogues.
- **Weather verbs:** all are impersonal, with no dummy subject: h₂wérst, h₂wérseti, snéygʷʰeti, snéygʷʰet, snéygʷʰēti, léwkt, stéwdt (00018), gʷʰért, gʷʰréh₁yeti, h₁regʷesyéti.
  - In 00002, h₁íd stéwdt has a real referent: the water of the previous sentence.
  - In 00019 and 00029 the subjects are real (wódr̥, dʰéǵʰōm).

### Counts

| | wrong | minor |
|---|---|---|
| Packet, 20 real items, as scored (before fixes) | 0 | 2 |
| Full batch of 40, before fixes | 2 | 6 |
| Full batch of 40, after fixes | 0 | 2 (left as they are; see below) |

### Wrong items, fixed in the plan

1. **t042-0035 (record 00035):** 'fear' took a direct object. The forms were snígʷʰm̥ dedwóyth₂e? and tā́m ne dedwóyh₂e. The corpus convention is the ablative of the thing feared (twéd bʰebʰih₂ḗr, tóybʰos bʰebʰóyh₂h₂e).
   - Fix: c1 `snigwhs` role OBJ→ABL; c2 `demonstrative_so` role OBJ→ABL.
   - Result: **snigʷʰés dedwóyth₂e? tósyeh₂s ne dedwóyh₂e.**
   - This item's packet copy was the sríHǵesh₁ plant. The resolver's "planted: no fix needed" covers only the planted form, not this real error.
2. **t042-0038 (record 00038):** the causative wodʰéyeti was used for plain "shall I lead it to him". The plain verb wédʰeti 'lead, bring' exists and the batch uses it elsewhere (0006, 0016).
   - Fix: c2 `pie-lex-wodheyeti` → `pie-lex-wedheti`.
   - Result: **… tósmey h₁ím wédʰōh₂?**

### Minor items

- **Fixed: 0027 c5 and 0030 c2, c4, c5.** The pronoun for the cows being milked was masculine (tóns, tóybʰos). Set `gender: f`, which gives **tā́s** and **téh₂bʰos**. The realizer now warns "matches no referent of that gender", because the lexicon gives gʷṓws one gender. The warning is harmless here: milked cows are female.
- **Fixed: 0011 c0 and 0034 c0.** The vocative adjective h₁súmenes (bahuvrihi, f) was translated "Kindly", as if it were an adverb. The English is now **"Kind one, …"**, changed in both the clause English and the plan English.
- **Left as is: 0030 c3.** h₂susyónti 'they are dry' for cows not giving milk. The PIE is grammatical, but the sense looks like an English idiom carried over.
- **Left as is: 0038 c1.** h₂roh₁dʰéye 'tell me' is an -éye- formation with no lexicon gloss. Its Balto-Slavic reflexes mean 'show, advise'. I kept it because the brief asks for varied verbs of saying.
- **Not counted:** gnomic or future aorists in generic statements (stéwdt, séngʷt, h₂wékst, bʰéwgt in 0002, 0005, 0029, 0040). This is accepted usage.

### Gate

Re-realized with `scripts/realize_plans.py data/generation/plans/t042.jsonl --batch t042 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`.
- Results: 40/40 realized, 40/40 exact pass, reject rate 0.0, max lexeme uses 6, duplicates 0.
- **Gate: PASS.**

The packet was not regenerated, so the verdicts and the calibration stand as recorded.

## Engine and brief gaps (reported only, not fixed)

1. **Gloss of h₂ew.** The gloss always uses the first lexicon sense, "away.from". In 0011, 0032, 0033, 0036 and 0040 the English means 'again' or 'back', which is the lexicon's second sense. PIE and English agree, but the gloss is misleading.
2. **Gender of common-gender nouns.** gʷṓws has a single lexicon gender. Female referents (cows being milked) therefore trigger a false "no referent" warning when the pronoun is set to f.
3. **Case for 'fear' (brief gap).** No brief states the case of the thing feared. Other batches' plans use both OBJ and ABL with `pie-lex-dedwoye`. A planner-brief rule ("the thing feared is ablative with dwey- and bʰeyh₂-"), or a check in the checker, would stop this recurring.
4. **Thematic 'drive' versus 'say'.** The realizer warns that h₂éǵonti and h₂éǵoh₂ ('drive') are also subjunctives of h₂eǵ- 'say' (0025, 0028). The English means 'drive' in both places, so nothing needs to change.
