# Meter repair: t033

Plan file `data/generation/plans/t033.jsonl`. Re-realized with `scripts/realize_plans.py data/generation/plans/t033.jsonl --batch t033 --model claude-sonnet-5-5 --prompt-id tier3-planner-v4 --engine-version f7639e1`. HEAD moved from 14a9e68 to f7639e1 during the work because other agents committed. Nothing is committed here.

## Result

| | before | after |
|---|---|---|
| meter_exact | 17/154 = **0.110** | 144/153 = **0.941** |
| gate | FAIL (meter only) | **PASS** (every gate) |
| max_lexeme_uses (cap 11) | 11 | 11 |
| theme_core_uses | ≤32 | ≤33 |
| rejects / exact | 0 / 40 | 0 / 40 |
| tokens | 2123 | 2172 |
| formula_uses | 18 | 18 |
| plan warnings | 36 | 36, the same set (two clause indices moved after a split) |

- **Scope.** Only the 13 wedding texts (t033-0028 … 0040) were edited. The 27 prose texts (dialogue, family) have unchanged plans and unchanged `pie`. Their corpus records differ only in `generator.engine_version` and in two `gloss` strings, where the current engine glosses stérg- as "love" (an engine/lexicon change, not mine).
- **Engine version.** The working tree has uncommitted edits in `pie/*mapping*.py`, `pie/formula_search.py` and `pie/material_units.py`. They are not mine. The realizer output for the prose texts did not change.

## Method and rules applied

A verse line is a sentence. Most of the gain came from moving `break`s and from particles. Edits, in order of preference:
1. **Splitting or merging sentences.** Free; no English words change, only punctuation.
2. **Particles.**
   - Particle `nu` is rendered "now/then"; `ge` is rendered "indeed". This is the t002/t005 convention.
   - Adding or dropping a clause `-kʷe` adds or removes "and".
   - Dropping an existing `nu` removes "Then".
   - I never stacked a particle on a `-kʷe` clause. The tool's measured edits produce `nu-kʷe` and `-kʷe-ge`, and I rejected those.
3. **Added or dropped words.** Each one is in the per-text list below and in the English.

**Speaker boundaries were treated as hard.** I never merged two different speakers' quotes into one sentence. Two exceptions are flagged below:
- in 0034 and 0037, adjacent *unattributed* quotes were joined as one speaker's turn;
- in 0034 and 0035, two exchanges were re-paired.

An inquit was allowed to share a sentence with its own speaker's speech.

**English check.** I diffed every text's English word by word against the pre-repair file. The only deltas are now/then/indeed/and, punctuation, and the added or dropped words listed below. None of the 49 review fixes was reverted: no "Hail/Welcome" came back, and "Sky", not "Father Sky", stands over bare dyḗws.

## head/dep integrity (tool bug)

`meter_report.candidate_edits` inserts an added vocative at slot 0 without renumbering `head`/`dep`. I hit the same class of bug in my own inserts at index 0. I compared every (slot → head-target) pair in each changed plan, before and after:
- **t033-0030 c20 (fixed during work).** A VOC ph₂ter was inserted at slot 0, which moved MOD ń̥dʰgʷʰitos onto the IO. The realizer produced *ń̥dʰgʷʰitoybʰos tóybʰos* and check_plan passed. The fix moved the VOC to the end, and the line now reads `ph₂ter tóybʰos ń̥dʰgʷʰitom ḱléwos dh₃dʰí`.
- **t033-0034 c21 (fixed at the end).** A SUBJ yúH was inserted at slot 0, which moved POSS "our" (personal/1 DU) onto the pronoun. The realized text happened to look right. The fix points `head` back at bʰoydʰéh₂ (index 1). The count is unchanged.
- All other inserts at index 0 (0028 c6, c7; 0033 c7; 0034 c0, c15, c17, c19; 0035 c4) were in clauses with no head/dep slots.
- The final comparison shows only the intended additions and removals of MOD/POSS links.

I stopped using the tool's vocative edits after the first case. It also proposes semantically wrong vocatives, for example "husband's brother" in a prayer to Sky.

## Lines not fixed (9), and why

All nine are short quoted utterances by one speaker. Each is an independent quote that cannot be merged with a neighbour of another speaker. Reaching 8 would need 3–6 added syllables of new content, and the slice's suitable "dear/good" adjectives (lewbʰós, ḱéywos, h₁wésus) are all at the lexeme cap of 11.
- 0033 L11 `snúse` (2) and L12 `dáyh₂wer` (2): the paired greetings "Daughter-in-law!" "Husband's brother!".
- 0034 L5 `twé péh₂soh₂` (3) and L6 `twé stérgōh₂` (3): the separate vows "I shall protect you." "I shall love you."
- 0037:
  - L2 `wiḱdʰí` (2), "Enter.";
  - L6 `péh₂wr̥ toy moy péh₂wr̥ h₁nómn̥-kʷe toy moy h₁nómn̥` (13): no −2 edit keeps the content, though it would be exact under `"meter": 12` if `-kʷe` were dropped;
  - L10 `ḱéh₂-kʷe moy méh₂tēr` (5).
- 0038 L9 `bʰréh₂ter gʷm̥sḱé` (4), "Come, brother."
- 0040 L12 `n̥smé ḱl̥nuté` (5), "hear us!".

The brief's greeting pattern, VOC + gʷm̥dʰí "come!", would fix the 0033 greetings, but it adds a verb, so I left it for the lead to decide.

## Decisions the lead should check

- **`"meter": 12` declared on t033-0035.** Its first line, "It was getting dark; the guests arrived; the cook was cooking", is 12 and is exact only as jagatī. No 8/11 partition of c0–c2 exists without new content, because c0 (3 syllables) cannot stand alone. To reach 12 I dropped that clause's `nu` and `-kʷe`.
- **Reordering:**
  - 0035: the Q/Q/A/A order became "Who is this man, and who is that one yonder?" "This is the husband's brother; that is the wife's brother." The `-kʷe` on the second question now matches the English "And who…", which before had no PIE.
  - 0034: the vows became groom "I marry you (wedʰ-); do you take me?" and bride "I marry you (snewbʰ-), and I take you". This assumes the man's verb wedʰ- and the woman's snewbʰ-. Inside one quote, "Let us live together, and let us eat. Now let us two drink wine" was also reordered.
- **Quotes joined as one turn, both unattributed in the English:**
  - 0034 "May the fire hear us; may we two not go apart."
  - 0037 "Now I have heard your words; you are indeed dear to me."
- **Lexeme and tense swaps (same meaning):**
  - 0035 c9 dédeh₃t 'was giving' (PST) → déh₃t AOR 'gave', following brief rule 8, a single past event.
  - Because that put deh3t at 12 > cap, 0028 c26 went from deh3t OPT dh₃yéh₁t to the synonym pie-lex-deh3ut OPT duh₃yéh₁t, which has the same count. deh3ut has attested_in 0 against 10 for deh3t, and is already used 10× in the batch.
- **Clause splits:**
  - 0032 c10, the 20-syllable list, is now two clauses with bʰéret each: "she brought wool, silver, a yoke; she brought a plough, two horses, ten cattle".
  - 0035 c11 "they drank wine and beer" is now "they drank wine, and they drank beer".
- **Pre-existing English/plan mismatches fixed in passing:**
  - 0032 "A wife for our brother" had no verb, but the PIE has h₂isḱómes; it now reads "We seek a wife…".
  - 0040 "I hear you" had no OBJ; twé was added.
  - 0040 c16 had `and` on the last vocative, with no "and" in the English; it was dropped.
  - 0035 "And who…" now has its `-kʷe`.
- **Pronoun-subject drops (pro-drop, 3sg):** 0036 c3 "may she grow strong" and 0036 c10 "and may it (the lamb) not die".

## Per-text edits

Clause numbers are those of the new plan.

- **0028** (17 lines, all exact):
  - +nu c2, c8, c11, c13;
  - −kʷe c5, c10, c16, c22, c28;
  - c6 +VOC ǵm̥rós "son-in-law";
  - c7 +VOC swéḱuros "father-in-law" and +ge;
  - c27 −POSS "your" (song of praise);
  - c26 deh3t→deh3ut;
  - breaks moved.
- **0029** (9/9):
  - c0 +nu ("Now dawn…");
  - c2 −kʷe, +MOD lewbʰós "dear mother";
  - −nu c3, c8, c13;
  - −kʷe c4, c7, c17;
  - c15 −MOD HéHḱus ("the two swift horses" → "the two horses");
  - inquits joined to their speech.
- **0030** (12/12):
  - c1 −POSS "our" ("Hear the words");
  - c4 +ge (relative clause: "who indeed placed");
  - c8 +nu;
  - c9 +VOC ph₂ter "Father";
  - c10 +nu;
  - c11 +numeral dwóh₁ (the English already said "two") and +ge;
  - c14 −kʷe;
  - c15 −MOD h₁wésus ("Good Dawn" → "Dawn");
  - c18 +nu;
  - c20 +VOC ph₂ter;
  - c21 −kʷe;
  - c23 −kʷe, +MOD h₁wésus "good shepherd".
- **0031** (15/15):
  - c1 +nu;
  - c3 +nu ("Well, is he…");
  - c5 −kʷe;
  - c6 +VOC gʰósteyes "guests";
  - c9 +nu (apodosis "then we shall give her");
  - c11 +IO wos "for you";
  - c12 +VOC gʰósteyes;
  - c15 +nu;
  - c20: +nu, +MOD deictic ("Now let this pledge be between us", was "Let there be a pledge between us");
  - c22: SUBJ h₂nḗr PL + deictic + MOD polh₁ús ("Who are these many men?"), which fills the "men" that had no slot;
  - c23: +MOD ḱéywos, +ge ("These are indeed my dear brothers").
- **0032** (11/11):
  - c2 −kʷe;
  - c3 joined with its question;
  - c8 −nu, c9 −nu ("They gave the bride price; the father took it");
  - c10 split into c10/c11;
  - c12 −nu;
  - c14 −kʷe;
  - c15 +MOD h₁wésus "good beer";
  - c17 +MOD ḱéywos, c18 +kʷe ("Dear father-in-law, and son-in-law!");
  - c5 English fix.
- **0033** (10/12; 2 misses):
  - c0 +numeral dwóh₁, +nu;
  - c2 −kʷe ("…; she became glad");
  - c3 +GOAL n̥smé "to us";
  - c4 +ge;
  - c6 +nu, +VOC snusós;
  - c7 +OBJ tóm "it" (the wine);
  - c8 −nu;
  - c9 +nu;
  - c11 −nu;
  - c12 −IO toy "for you".
- **0034** (15/17; 2 misses):
  - reorders as above;
  - c0 +SUBJ h₁eǵóh₂ (emphatic "I");
  - c3 +kʷe;
  - c6 +nu, +SUBJ wéh₁ "we two";
  - c9 +nu;
  - c12 +nu;
  - c13 −kʷe;
  - c15, c17, c19 +SUBJ h₁eǵóh₂ (the witnesses' "I have heard / seen / am satisfied");
  - c20 +nu;
  - c21 +SUBJ yúH, +ge ("you, indeed, hear our pledge").
- **0035** (13/13 with meter 12):
  - c1 −nu, c2 −kʷe;
  - c4 +SUBJ tóh₁ "the two" (the English already said "the two");
  - c5: SUBJ h₂nḗr + deictic ("this man", the English already said "man"), +nu;
  - c6 +kʷe;
  - Q/A reorder;
  - c9 −nu, PST→AOR déh₃t;
  - c10 −nu;
  - c11 split;
  - c15 −kʷe;
  - c17 +nu;
  - c18 POSS wos→toy (sg) +VOC ǵm̥rós ("May your fame be great, son-in-law");
  - c23 +nu;
  - c24 +ADV h₁n̥dó "inside".
- **0036** (10/10):
  - c0 +MOD pléth₂us, +POSS "our" ("Broad Earth, our mother!": the inherited *pléth₂wih₂ dʰéǵʰōm);
  - c3 −SUBJ (pro-drop);
  - c4 −`and` (asyndeton "the rye, the tree");
  - +nu c6, c7;
  - c7 +POSS "our enclosure";
  - +ge c8, c11;
  - c10 −SUBJ (pro-drop "it");
  - c13 +kʷe.
- **0037** (8/11; 3 misses):
  - c0 −MOD deictic ("of this household" → "of the household");
  - c3 +SUBJ h₁eǵóh₂;
  - c8 +MOD méǵh₂s "my great heart";
  - c11 +nu, c12 +ge (joined);
  - c13 +ADV úd "up" (the English already said "stood up");
  - c18 +nu, c19 +kʷe ("Now, brother-in-law and father-in-law!").
- **0038** (8/9; 1 miss):
  - c1 +ge;
  - c2 +SUBJ h₁eǵóh₂, +ge;
  - c3 +nu;
  - c8 +nu, +VOC snusós, +IO n̥sméy ("Now, daughter-in-law, you will become accustomed to us");
  - c10 −kʷe.
- **0039** (5/5): +nu c5, +ge c6 (the exclamations); c10 −kʷe.
- **0040** (11/12; 1 miss):
  - +nu c1, c4, c7, c9, c11;
  - c6 −kʷe;
  - c7 +OBJ twé;
  - c12 −nu;
  - c16 −`and`.

## Tool findings (not fixed: tools untouched)

1. `meter_report.candidate_edits` vocative insert at index 0 does not renumber `head`/`dep`, as described above. check_plan accepts the result.
2. `candidate_edits` "merge" raises a KeyError when the next clause has no `break` key (`p["clauses"][nxt].pop("break")`). It only works on plans where every clause carries `break`.
3. Tool edits stack particles (`nu-kʷe`, `-kʷe-ge`), and the tool proposes vocatives with no regard to the addressee.
4. `nu` at a speech or inquit boundary in narrative wedding texts is the main source of the "now/then" padding. Many dialogue-heavy texts can't reach 8/11 per utterance, so a dialogue genre inside `wedding` is costly under the exact gate.

## Line-by-line record (old and new sentences with counts; old and new English)

### t033-0028 (t3-t033-00028) Blessing the Wedding

Old lines:

1. `dyéw ph₂ter dʰéǵʰom méh₂ter` (7)
2. `h₂wistóm nos` (3)
3. `duh₃tóm ḱósyeh₂ey pótn̥yeh₂ey ḱléwos` (11 ok)
4. `gʷíh₃woyh₁t ǵn̥h₁yóyh₁ro-kʷe suHnéwes h₁ésyeh₂ey` (12)
5. `h₁íh₂m̥ toy dédeh₃mi` (6)
6. `h₁íh₂m̥ wn̥h₁sḱṓh₂` (4)
7. `péh₂wr̥ h₂ékʷeh₂-kʷe h₁íh₂m̥ h₂léksoyh₁tām` (10)
8. `h₂uksyéh₁t Hrugʰís dóru-kʷe sth₂éh₁yoyh₁t` (9)
9. `dr̥myéh₁t sréwmn̥ kólHō-kʷe stesth₂yéh₁t` (10)
10. `tr̥syéh₁t sélos h₁ógʷʰis-kʷe mē sérpoyh₁t` (10)
11. `bʰugyéh₁t ǵʰwḗr sprongʰós-kʷe wos Hrugʰím mē h₂ḱh₃yéh₁t` (12)
12. `lukyéh₁t Héh₂mr̥ nókʷts-kʷe gʷʰr̥yéh₁t` (8 ok)
13. `h₁syéh₁t wos wénh₁os kóh₂mos-kʷe wos méǵh₂s h₁syéh₁t` (11 ok)
14. `Hwr̥dʰyéh₁t toy krépos h₂yuHn̥téh₂-kʷe toy lukyéh₁t` (12)
15. `h₁syéh₁t wos ḱwoytós` (4)
16. `bʰudʰtóh₁ h₁sih₁tóm` (4)
17. `wéyHs toy h₂uksyéh₁t` (4)
18. `dh₃yéh₁t wos déh₃tōr misdʰóm` (7)
19. `h₁erkʷós wos ḱluwih₁tó ḱluwih₁tó-kʷe wos kéh₂nmn̥` (13)

New lines:

1. `dyéw ph₂ter dʰéǵʰom méh₂ter nu nos h₂wistóm` (11 ok)
2. `duh₃tóm ḱósyeh₂ey pótn̥yeh₂ey ḱléwos` (11 ok)
3. `gʷíh₃woyh₁t ǵn̥h₁yóyh₁ro suHnéwes h₁ésyeh₂ey` (11 ok)
4. `ǵḿ̥re toy h₁íh₂m̥ dédeh₃mi` (8 ok)
5. `swéḱure-ge h₁íh₂m̥ wn̥h₁sḱṓh₂` (8 ok)
6. `nu péh₂wr̥ h₂ékʷeh₂-kʷe h₁íh₂m̥ h₂léksoyh₁tām` (11 ok)
7. `h₂uksyéh₁t Hrugʰís dóru sth₂éh₁yoyh₁t` (8 ok)
8. `nu dr̥myéh₁t sréwmn̥ kólHō-kʷe stesth₂yéh₁t` (11 ok)
9. `nu tr̥syéh₁t sélos h₁ógʷʰis-kʷe mē sérpoyh₁t` (11 ok)
10. `bʰugyéh₁t ǵʰwḗr sprongʰós wos Hrugʰím mē h₂ḱh₃yéh₁t` (11 ok)
11. `lukyéh₁t Héh₂mr̥ nókʷts-kʷe gʷʰr̥yéh₁t` (8 ok)
12. `h₁syéh₁t wos wénh₁os kóh₂mos-kʷe wos méǵh₂s h₁syéh₁t` (11 ok)
13. `Hwr̥dʰyéh₁t toy krépos h₂yuHn̥téh₂ toy lukyéh₁t` (11 ok)
14. `h₁syéh₁t wos ḱwoytós bʰudʰtóh₁ h₁sih₁tóm` (8 ok)
15. `wéyHs toy h₂uksyéh₁t duh₃yéh₁t wos déh₃tōr misdʰóm` (11 ok)
16. `h₁erkʷós ḱluwih₁tó ḱluwih₁tó wos kéh₂nmn̥` (11 ok)

Old English: Father Sky! Mother Earth! Hear us. Give this wife fame. May she live, and may sons be born to her. "I give her to you." "I shall love her." May fire and water protect her. May the rye grow, and may the tree stand. May the stream run, and may the hill stand firm. May the marsh dry up, and may the snake not creep. May the beast flee, and may the locust not eat your rye. May the day become bright, and may the night become warm. May love be between you, and may your desire be great. May your body grow strong, and may your youth become bright. May the light be yours. May you two be watchful. May your strength grow. May the giver give you a reward. May your song of praise be heard, and may your song be heard.

New English: Father Sky! Mother Earth! Now hear us. Give this wife fame. May she live; may sons be born to her. "I give her to you, son-in-law." "Father-in-law, I shall indeed love her." Now may fire and water protect her. May the rye grow; may the tree stand. Now may the stream run, and may the hill stand firm. Now may the marsh dry up, and may the snake not creep. May the beast flee; may the locust not eat your rye. May the day become bright, and may the night become warm. May love be between you, and may your desire be great. May your body grow strong; may your youth become bright. May the light be yours; may you two be watchful. May your strength grow; may the giver give you a reward. May the song of praise be heard; may your song be heard.

### t033-0029 (t3-t033-00029) The Bride Leaves Her Father's House

Old lines:

1. `h₂éwsōs h₂wést nu yéwgt ph₂tḗr dwóh₁ h₁éḱwoh₁ woséyet-kʷe méh₂tēr snéwbʰontih₂m tā́m nu wédʰet ph₂tḗr tā́m h₁éǵʰs bʰréh₂tēr-kʷe sékʷeto nu swidyét séh₂ tréset-kʷe gʷéh₂t-kʷe nu HréwdHt méh₂tēr` (47)
2. `h₁mé memn̥dʰí h₂ew-kʷe gʷm̥sḱé` (8 ok)
3. `ḱléwesh₁ h₁idʰí` (5)
4. `mē bʰéyh₂s nu wéwket ph₂tḗr` (7)
5. `h₂léksoyh₁t te dyḗws nu dr̥mtā́m HeHḱúh₁ h₁éḱwoh₁ póntoh₁i nu stestóh₂e méh₂tēr spéḱyet-kʷe` (23)

New lines:

1. `nu h₂éwsōs h₂wést nu yéwgt ph₂tḗr dwóh₁ h₁éḱwoh₁` (11 ok)
2. `woséyet lewbʰéh₂ méh₂tēr snéwbʰontih₂m tā́m` (11 ok)
3. `wédʰet ph₂tḗr tā́m h₁éǵʰs bʰréh₂tēr sékʷeto` (11 ok)
4. `nu swidyét séh₂ tréset-kʷe gʷéh₂t` (8 ok)
5. `HréwdHt méh₂tēr h₁mé memn̥dʰí` (8 ok)
6. `h₂ew-kʷe gʷm̥sḱé ḱléwesh₁ h₁idʰí mē bʰéyh₂s` (11 ok)
7. `wéwket ph₂tḗr h₂léksoyh₁t te dyḗws` (8 ok)
8. `nu dr̥mtā́m h₁éḱwoh₁ póntoh₁i` (8 ok)
9. `nu stestóh₂e méh₂tēr spéḱyet` (8 ok)

Old English: Dawn became bright. Then the father yoked the two horses, and the mother dressed the one who was marrying. Then the father led her out, and the brother followed. Then she was sweating, and she was trembling, and she went. Then the mother cried out: "Remember me, and come again. Go with fame. Do not be afraid." Then the father said: "May Sky protect you." Then the two swift horses ran along the path. Then the mother stood and looked on.

New English: Now dawn became bright. Then the father yoked the two horses. The dear mother dressed the one who was marrying. The father led her out; the brother followed. Then she was sweating, and she was trembling; she went. The mother cried out: "Remember me, and come again. Go with fame. Do not be afraid." The father said: "May Sky protect you." Then the two horses ran along the path. Then the mother stood; she looked on.

### t033-0030 (t3-t033-00030) Prayer for the Wedding Chariot

Old lines:

1. `dyéw ph₂ter h₁uséwōm déh₃tor` (8 ok)
2. `ḱludʰí nos wékʷesh₂` (6)
3. `yéwgs h₁yós HeHḱúns h₁éḱwons` (6)
4. `h₁yós sh₂wéns kʷékʷlom ǵʰéys` (6)
5. `dʰéh₁s h₁yós sóh₂wl̥` (4)
6. `h₁yós h₁ógʷʰim wéns` (4)
7. `spérs h₁yós h₂ékʷeh₂m h₁yós-kʷe dʰéǵʰōm stoh₂éyes` (11 ok)
8. `ḱl̥nudʰí` (3)
9. `tóybʰos h₂r̥ǵn̥tóm gʷṓs-kʷe duh₃dʰí` (9)
10. `sh₂wéns kʷékʷlos pró h₁iyéh₁t` (7)
11. `bʰéroyh₁tām h₁éḱwoh₁ tóh₁ h₂éwsos` (8 ok)
12. `gʷm̥sḱé léwkm̥-kʷe bʰére h₁úsewi h₂éwsos` (12)
13. `tóybʰos h₂usdʰí` (4)
14. `péh₂wr̥ mē n̥ḱyéh₁t` (5)
15. `h₁syéh₁t tóysōm h₁nómn̥ ḱlutóm méǵh₂-kʷe ḱléwos tóybʰos h₁syéh₁t` (15)
16. `tóybʰos ń̥dʰgʷʰitom ḱléwos dh₃dʰí wénh₁os-kʷe dh₃dʰí` (14)
17. `h₃rḗǵs h₃rḗǵnih₂-kʷe gʷíh₃woyh₁tām h₁syéh₁t-kʷe poh₂imḗn bʰudʰtós` (14)

New lines:

1. `dyéw ph₂ter h₁uséwōm déh₃tor` (8 ok)
2. `ḱludʰí wékʷesh₂ yéwgs h₁yós HeHḱúns h₁éḱwons` (11 ok)
3. `h₁yós sh₂wéns kʷékʷlom ǵʰéys dʰéh₁s-ge h₁yós sóh₂wl̥` (11 ok)
4. `h₁yós h₁ógʷʰim wéns spérs h₁yós h₂ékʷeh₂m` (8 ok)
5. `h₁yós-kʷe dʰéǵʰōm stoh₂éyes nu ḱl̥nudʰí` (11 ok)
6. `ph₂ter tóybʰos h₂r̥ǵn̥tóm gʷṓs-kʷe duh₃dʰí` (11 ok)
7. `nu sh₂wéns kʷékʷlos pró h₁iyéh₁t` (8 ok)
8. `bʰéroyh₁tām-ge dwóh₁ h₁éḱwoh₁ tóh₁` (8 ok)
9. `h₂éwsos gʷm̥sḱé léwkm̥ bʰére` (8 ok)
10. `h₂éwsos tóybʰos h₂usdʰí péh₂wr̥ mē n̥ḱyéh₁t` (11 ok)
11. `nu h₁syéh₁t tóysōm h₁nómn̥ ḱlutóm` (8 ok)
12. `méǵh₂-kʷe ḱléwos tóybʰos h₁syéh₁t` (8 ok)
13. `ph₂ter tóybʰos ń̥dʰgʷʰitom ḱléwos dh₃dʰí` (11 ok)
14. `wénh₁os dh₃dʰí h₃rḗǵs h₃rḗǵnih₂-kʷe gʷíh₃woyh₁tām` (11 ok)
15. `h₁syéh₁t h₁wésus poh₂imḗn bʰudʰtós` (8 ok)

Old English: Father Sky, giver of good things! Hear our words. You who yoked the swift horses, you who drove on the wheel of the sun, you who placed the sun, you who overpowered the serpent, you who freed the water, and you who made the earth stand: hear! Give the two of them silver and cattle. May the wheel of the sun go forward. May the two horses carry them. Dawn! Come, and bring light! Good Dawn! Become bright for them. May the fire not go out. May their name be famous, and may they have great fame. Give them imperishable fame, and give love. May the king and the queen live, and may the shepherd be watchful.

New English: Father Sky, giver of good things! Hear the words, you who yoked the swift horses, you who drove on the wheel of the sun, you who indeed placed the sun, you who overpowered the serpent, you who freed the water, and you who made the earth stand: now hear! Father, give the two of them silver and cattle. Now may the wheel of the sun go forward. May the two horses indeed carry them. Dawn! Come, bring light! Dawn! Become bright for them. May the fire not go out. Now may their name be famous, and may they have great fame. Father, give them imperishable fame. Give love; may the king and the queen live. May the good shepherd be watchful.

### t033-0031 (t3-t033-00031) The Wedding Party Arrives

Old lines:

1. `gʷm̥mé` (2)
2. `bʰréh₂trey nos pótnih₂m séh₂gyomes` (8 ok)
3. `kʷís wos bʰréh₂tēr` (4)
4. `h₁éy wérsēn` (3)
5. `h₁éy ḱm̥tógʷus h₁éy-kʷe h₁léwdʰeros` (9)
6. `nu wiḱté sdté-kʷe` (5)
7. `h₁yód h₁wédmn̥ déh₃ete tā́m déh₃womes` (10)
8. `déḱm̥ gʷṓs ḱm̥tóm h₂ówins dédeh₃omes h₂r̥ǵn̥tóm-kʷe h₂wĺ̥h₁neh₂m-kʷe bʰéromes` (21)
9. `téh₂ logʰéyete` (5)
10. `séh₂ nos ḱéyweh₂ séh₂-kʷe nos ḱḗr` (8 ok)
11. `tā́m ph₂sté séh₂-kʷe usmé h₂élēti` (10)
12. `séh₂ h₁nédʰtu` (3)
13. `spéḱyete` (3)
14. `séh₂ léwks` (2)
15. `h₁éstu bʰoydʰéh₂ n̥sméy` (6)
16. `kʷéḱt poh₂imḗn tā́m déh₂newi` (8 ok)
17. `kʷéyes ḱóy` (3)
18. `ḱóy moy bʰréh₂teres` (5)

New lines:

1. `gʷm̥mé nu nos bʰréh₂trey pótnih₂m séh₂gyomes` (11 ok)
2. `kʷís wos bʰréh₂tēr nu h₁éy wérsēn` (8 ok)
3. `h₁éy ḱm̥tógʷus h₁éy h₁léwdʰeros` (8 ok)
4. `nu gʰósteyes wiḱté sdté-kʷe` (8 ok)
5. `h₁yód h₁wédmn̥ déh₃ete nu tā́m déh₃womes` (11 ok)
6. `déḱm̥ gʷṓs ḱm̥tóm h₂ówins dédeh₃omes` (11 ok)
7. `h₂r̥ǵn̥tóm-kʷe wos h₂wĺ̥h₁neh₂m-kʷe bʰéromes` (11 ok)
8. `gʰósteyes téh₂ logʰéyete` (8 ok)
9. `séh₂ nos ḱéyweh₂ séh₂-kʷe nos ḱḗr` (8 ok)
10. `nu tā́m ph₂sté séh₂-kʷe usmé h₂élēti` (11 ok)
11. `séh₂ h₁nédʰtu spéḱyete séh₂ léwks` (8 ok)
12. `nu h₁éstu ḱéh₂ bʰoydʰéh₂ n̥sméy` (8 ok)
13. `kʷéḱt poh₂imḗn tā́m déh₂newi` (8 ok)
14. `kʷéyes ḱóy polh₁éwes h₂néres` (8 ok)
15. `ḱóy-ge moy ḱéywōs bʰréh₂teres` (8 ok)

Old English: "We have arrived. We seek a wife for our brother." "Who is your brother? Is he a virile man?" "He possesses a hundred cows, and he is a free man." "Then enter, and sit down. If you give a bride price, we shall give her. We shall give ten cattle and a hundred sheep, and we carry silver and wool. Lay them down. She is dear to us, and she is our heart. Protect her, and she will nourish you. Let her come out. Look: she is a light." "Let there be a pledge between us." "The shepherd saw her at the river." "Who are these men?" "These are my brothers."

New English: "We have arrived. Now we seek a wife for our brother." "Who is your brother? Well, is he a virile man?" "He possesses a hundred cows; he is a free man." "Then enter, guests, and sit down. If you give a bride price, then we shall give her. We shall give ten cattle and a hundred sheep, and we carry silver and wool for you. Lay them down, guests. She is dear to us, and she is our heart. Now protect her, and she will nourish you. Let her come out. Look: she is a light." "Now let this pledge be between us." "The shepherd saw her at the river." "Who are these many men?" "These are indeed my dear brothers."

### t033-0032 (t3-t033-00032) The Bride Price Is Paid

Old lines:

1. `gʰóstins ḱléwsonts ph₂tḗr tóns h₁n̥dó wédʰet nu dʰédʰeh₁t méh₂tēr h₂ólut sdént-kʷe nu h₂éǵt ph₂tḗr` (24)
2. `kʷíd h₂isḱéte` (4)
3. `bʰréh₂trey nos pótnih₂m h₂isḱómes` (8 ok)
4. `h₁wédmn̥ duh₃té tā́m-kʷe h₁áydʰwe nu h₁wédmn̥ dh₃ént nu h₁áyto ph₂tḗr tód nu bʰéret séh₂ h₂wĺ̥h₁neh₂m h₂r̥ǵn̥tóm yugóm h₂érh₃trom dwóh₁ h₁éḱwoh₁ déḱm̥ gʷṓs nu h₂éǵt méh₂tēr` (42)
5. `tā́m ph₂sté tā́m-kʷe mē dʰrugʰyéte nu h₂ólut ph₃ént sh₂ént-kʷe` (15)
6. `swéḱure ǵḿ̥re` (5)

New lines:

1. `gʰóstins ḱléwsonts ph₂tḗr tóns h₁n̥dó wédʰet` (11 ok)
2. `nu dʰédʰeh₁t méh₂tēr h₂ólut sdént` (8 ok)
3. `nu h₂éǵt ph₂tḗr kʷíd h₂isḱéte` (8 ok)
4. `bʰréh₂trey nos pótnih₂m h₂isḱómes` (8 ok)
5. `h₁wédmn̥ duh₃té tā́m-kʷe h₁áydʰwe` (8 ok)
6. `h₁wédmn̥ dh₃ént h₁áyto ph₂tḗr tód` (8 ok)
7. `nu bʰéret séh₂ h₂wĺ̥h₁neh₂m h₂r̥ǵn̥tóm yugóm` (11 ok)
8. `bʰéret h₂érh₃trom dwóh₁ h₁éḱwoh₁ déḱm̥ gʷṓs` (11 ok)
9. `h₂éǵt méh₂tēr tā́m ph₂sté tā́m mē dʰrugʰyéte` (11 ok)
10. `nu h₁wésu h₂ólut ph₃ént sh₂ént-kʷe` (8 ok)
11. `ḱéywe swéḱure ǵḿ̥re-kʷe` (8 ok)

Old English: The father, listening to the guests, led them inside. Then the mother set out the beer, and they sat down. Then the father said: "What do you seek?" "A wife for our brother." "Give the bride price, and take her." Then they gave the bride price. Then the father took it. Then she brought wool, silver, a yoke, a plough, two horses, and ten cattle. Then the mother said: "Protect her, and do not deceive her." Then they drank beer and were sated. "Father-in-law! Son-in-law!"

New English: The father, listening to the guests, led them inside. Then the mother set out the beer; they sat down. Then the father said: "What do you seek?" "We seek a wife for our brother." "Give the bride price, and take her." They gave the bride price; the father took it. Then she brought wool, silver, a yoke; she brought a plough, two horses, ten cattle. The mother said: "Protect her; do not deceive her." Then they drank good beer and were sated. "Dear father-in-law, and son-in-law!"

### t033-0033 (t3-t033-00033) The Daughter-in-Law Arrives

Old lines:

1. `HeHḱúh₁ h₁éḱwoh₁ gʷm̥tā́m nu widét wiHrósyo méh₂tēr snusóm méwdt-kʷe` (18)
2. `snúse h₁n̥dó gʷm̥sḱé` (6)
3. `péh₂wr̥ nos toy lewbʰóm h₁syéh₁t nu bʰéret dayh₂wḗr wéyh₁onm̥` (15)
4. `sddʰí píph₃e-kʷe nu déh₃ut wiHrósyo méh₂tēr snusṓy poyḱóm` (16)
5. `tóm h₁áyso tóm-kʷe wéso nu sékʷt snusós` (11 ok)
6. `h₂wĺ̥h₁neh₂m toy h₂r̥ǵn̥tóm-kʷe bʰéroh₂` (9)
7. `h₁eǵóh₂ toy snusós` (5)
8. `twé stérgōh₂` (3)
9. `snúse` (2)
10. `dáyh₂wer` (2)

New lines:

1. `nu HeHḱúh₁ dwóh₁ h₁éḱwoh₁ gʷm̥tā́m` (8 ok)
2. `nu widét wiHrósyo méh₂tēr snusóm méwdt` (11 ok)
3. `snúse n̥smé h₁n̥dó gʷm̥sḱé` (8 ok)
4. `péh₂wr̥-ge nos toy lewbʰóm h₁syéh₁t` (8 ok)
5. `nu bʰéret dayh₂wḗr wéyh₁onm̥` (8 ok)
6. `nu snúse sddʰí tóm-kʷe píph₃e` (8 ok)
7. `déh₃ut wiHrósyo méh₂tēr snusṓy poyḱóm` (11 ok)
8. `nu tóm h₁áyso tóm-kʷe wéso` (8 ok)
9. `sékʷt snusós h₂wĺ̥h₁neh₂m h₂r̥ǵn̥tóm-kʷe bʰéroh₂` (11 ok)
10. `h₁eǵóh₂ toy snusós twé stérgōh₂` (8 ok)
11. `snúse` (2 MISS)
12. `dáyh₂wer` (2 MISS)

Old English: The two swift horses arrived. Then the husband's mother saw the daughter-in-law and became glad. "Daughter-in-law, come inside. May our fire be dear to you." Then the husband's brother brought wine. "Sit down and drink." Then the husband's mother gave the daughter-in-law an ornament. "Take it, and wear it." Then the daughter-in-law said: "I bring wool and silver for you. I am your daughter-in-law. I shall love you." "Daughter-in-law!" "Husband's brother!"

New English: Now the two swift horses arrived. Then the husband's mother saw the daughter-in-law; she became glad. "Daughter-in-law, come inside to us. May our fire indeed be dear to you." Then the husband's brother brought wine. "Now sit down, daughter-in-law, and drink it." The husband's mother gave the daughter-in-law an ornament. "Now take it, and wear it." The daughter-in-law said: "I bring wool and silver. I am your daughter-in-law. I shall love you." "Daughter-in-law!" "Husband's brother!"

### t033-0034 (t3-t033-00034) The Vows

Old lines:

1. `twé wédʰoh₂` (3)
2. `tébʰye snéwbʰoh₂` (4)
3. `h₁mé h₁áyth₂e` (3)
4. `twé h₁áyh₂e` (3)
5. `ḱóm gʷíh₃wōwos` (4)
6. `wéyh₁onm̥ píph₃ōwos h₁édowos-kʷe` (10)
7. `twé péh₂soh₂` (3)
8. `twé stérgōh₂` (3)
9. `péh₂wr̥ péri h₁éyowos` (7)
10. `péh₂wr̥ n̥h₃mé ḱluyéh₁t` (6)
11. `wí mē litih₁wé` (5)
12. `sh₂wéns nos kʷékʷlos bʰoydʰéh₂m dedórḱtu ḱl̥néwtu-kʷe dʰéǵʰōm méh₂tēr tā́m nu h₂éǵt snusósyo bʰréh₂tēr` (26)
13. `h₂wéysm̥ nu h₂éǵt dayh₂wḗr` (6)
14. `kʷéḱm̥ nu h₂éǵt méh₂tēr` (6)
15. `térpm̥` (2)
16. `snúse ǵḿ̥re dáyh₂wer swḗḱure-kʷe` (10)
17. `bʰoydʰéh₂m nos ḱl̥nuté` (6)

New lines:

1. `h₁eǵóh₂ twé wédʰoh₂ h₁mé h₁áyth₂e` (8 ok)
2. `tébʰye snéwbʰoh₂ twé-kʷe h₁áyh₂e` (8 ok)
3. `ḱóm gʷíh₃wōwos h₁édowos-kʷe` (8 ok)
4. `nu wé wéyh₁onm̥ píph₃ōwos` (8 ok)
5. `twé péh₂soh₂` (3 MISS)
6. `twé stérgōh₂` (3 MISS)
7. `nu péh₂wr̥ péri h₁éyowos` (8 ok)
8. `péh₂wr̥ n̥h₃mé ḱluyéh₁t wí mē litih₁wé` (11 ok)
9. `nu nos sh₂wéns kʷékʷlos bʰoydʰéh₂m dedórḱtu` (11 ok)
10. `ḱl̥néwtu dʰéǵʰōm méh₂tēr tā́m` (8 ok)
11. `nu h₂éǵt snusósyo bʰréh₂tēr h₁eǵóh₂ h₂wéysm̥` (11 ok)
12. `nu h₂éǵt dayh₂wḗr h₁eǵóh₂ kʷéḱm̥` (8 ok)
13. `nu h₂éǵt méh₂tēr h₁eǵóh₂ térpm̥` (8 ok)
14. `nu snúse ǵḿ̥re dáyh₂wer swḗḱure-kʷe` (11 ok)
15. `yúH-ge nos bʰoydʰéh₂m ḱl̥nuté` (8 ok)

Old English: "I marry you." "I marry you." "Do you take me?" "I take you." "Let us two live together. Let us drink wine, and let us eat." "I shall protect you." "I shall love you." "Let us two go around the fire." "May the fire hear us." "May we two not go apart." "Let the wheel of the sun see our pledge, and let Mother Earth hear it." Then the daughter-in-law's brother said: "I have heard." Then the husband's brother said: "I have seen." Then the mother said: "I am satisfied." "Daughter-in-law, son-in-law, husband's brother, and wife's brother: hear our pledge!"

New English: "I marry you; do you take me?" "I marry you, and I take you." "Let us two live together, and let us eat. Now let us two drink wine." "I shall protect you." "I shall love you." "Now let us two go around the fire." "May the fire hear us; may we two not go apart." "Now let the wheel of the sun see our pledge. Let Mother Earth hear it." Then the daughter-in-law's brother said: "I have heard." Then the husband's brother said: "I have seen." Then the mother said: "I am satisfied." "Now, daughter-in-law, son-in-law, husband's brother, and wife's brother: you, indeed, hear our pledge!"

### t033-0035 (t3-t033-00035) The Wedding Feast

Old lines:

1. `h₁regʷesyét nu gʷm̥sḱónt gʰósteyes pékʷtōr-kʷe pékʷet nu h₁ludʰétām h₃rḗǵs h₃rḗǵnih₂-kʷe sdtā́m-kʷe` (24)
2. `kʷís ḱós` (2)
3. `ḱós dayh₂wḗr` (3)
4. `kʷís h₁énos` (3)
5. `h₁énos swēḱurós nu dédeh₃t ph₂tḗr tóybʰos wéyh₁onm̥ nu wr̥h₁énm̥ gʷr̥h₃ónt wéyh₁onm̥-kʷe h₂ólut-kʷe srobʰéyont kéh₂nmn̥-kʷe mluHént nu térpt pékʷtōr wérh₁t-kʷe poh₂imḗn h₁erkʷóm nu wéwket h₃rḗǵs` (52)
6. `ḱós moy ḱóymos ḱéywos` (6)
7. `ḱléwos wos méǵh₂ h₁syéh₁t nu bʰh₂tā́m bʰréh₂terh₁e h₁erkʷóm nu stéh₂t snusósyo bʰréh₂tēr h₂éǵt-kʷe` (23)
8. `tr̥pté` (2)
9. `stéwdt nókʷts nu l̥gʰént` (5)

New lines:

1. `h₁regʷesyét gʷm̥sḱónt gʰósteyes pékʷtōr pékʷet` (12 ok)
2. `nu h₁ludʰétām h₃rḗǵs h₃rḗǵnih₂-kʷe tóh₁-kʷe sdtā́m` (11 ok)
3. `nu kʷís ḱós h₂nḗr kʷís-kʷe h₁énos` (8 ok)
4. `ḱós dayh₂wḗr h₁énos swēḱurós` (8 ok)
5. `déh₃t ph₂tḗr tóybʰos wéyh₁onm̥` (8 ok)
6. `wr̥h₁énm̥ gʷr̥h₃ónt wéyh₁onm̥ srobʰéyont` (11 ok)
7. `h₂ólut-kʷe srobʰéyont kéh₂nmn̥-kʷe mluHént` (11 ok)
8. `nu térpt pékʷtōr wérh₁t poh₂imḗn h₁erkʷóm` (11 ok)
9. `nu wéwket h₃rḗǵs nu moy ḱós ḱóymos ḱéywos` (11 ok)
10. `ǵḿ̥re toy ḱléwos méǵh₂ h₁syéh₁t` (8 ok)
11. `nu bʰh₂tā́m bʰréh₂terh₁e h₁erkʷóm` (8 ok)
12. `nu stéh₂t snusósyo bʰréh₂tēr h₂éǵt-kʷe tr̥pté` (11 ok)
13. `nu stéwdt nókʷts nu h₁n̥dó l̥gʰént` (8 ok)

Old English: It was getting dark. Then the guests arrived, and the cook was cooking. Then the king and the queen arrived, and the two sat down. "Who is this man?" "This is the husband's brother." "And who is that one yonder?" "That is the wife's brother." Then the father gave wine to them. Then they ate the lamb, and they drank wine and beer, and they spoke a song. Then the cook was content, and the shepherd spoke a song of praise. Then the king said: "This household is dear to me. May your fame be great." Then the two brothers spoke a song of praise. Then the daughter-in-law's brother stood up and said: "Be content!" The night became cold. Then they lay down.

New English: It was getting dark; the guests arrived; the cook was cooking. Then the king and the queen arrived, and the two sat down. "Now who is this man, and who is that one yonder?" "This is the husband's brother; that is the wife's brother." The father gave wine to them. They ate the lamb; they drank wine, and they drank beer, and they spoke a song. Then the cook was content; the shepherd spoke a song of praise. Then the king said: "Now this household is dear to me. May your fame be great, son-in-law." Then the two brothers spoke a song of praise. Then the daughter-in-law's brother stood up and said: "Be content!" Then the night became cold. Then they lay down inside.

### t033-0036 (t3-t033-00036) Prayer to Mother Earth for the Bride

Old lines:

1. `dʰéǵʰom méh₂ter` (4)
2. `h₁yéh₂ gʷṓs mórtons-kʷe h₂élesi` (8 ok)
3. `duh₃dʰí ḱósyeh₂ey polh₁úns suHnúns` (9)
4. `Hwr̥dʰyéh₁t h₁íh₂` (3)
5. `h₁yéh₂ Hrugʰím dóru-kʷe h₂élesi` (9)
6. `ḱludʰí nos` (3)
7. `wĺ̥kʷos h₂ówins mē lm̥bʰyéh₁t` (7)
8. `mē wiḱyéh₁t ǵʰwḗr gʰórtom` (6)
9. `sprongʰós Hrugʰím mē h₂ḱh₃yéh₁t` (7)
10. `mē kʷis stéh₂yoyh₁t wr̥h₁énm̥ wr̥h₁ḗn-kʷe mē mr̥yéh₁t` (13)
11. `mē Hrumpyéh₁t h₁éḱwos yugóm` (7)
12. `h₂ékʷeh₂ mē pléh₁dʰoyh₁t` (5)
13. `gʷíh₃woyh₁t` (2)

New lines:

1. `pĺ̥th₂ewi nos dʰéǵʰom méh₂ter` (8 ok)
2. `h₁yéh₂ gʷṓs mórtons-kʷe h₂élesi` (8 ok)
3. `duh₃dʰí ḱósyeh₂ey polh₁úns suHnúns Hwr̥dʰyéh₁t` (11 ok)
4. `h₁yéh₂ Hrugʰím dóru h₂élesi ḱludʰí nos` (11 ok)
5. `nu wĺ̥kʷos h₂ówins mē lm̥bʰyéh₁t` (8 ok)
6. `nu nos mē wiḱyéh₁t ǵʰwḗr gʰórtom` (8 ok)
7. `sprongʰós-ge Hrugʰím mē h₂ḱh₃yéh₁t` (8 ok)
8. `mē kʷis stéh₂yoyh₁t wr̥h₁énm̥ mē-kʷe mr̥yéh₁t` (11 ok)
9. `mē-ge Hrumpyéh₁t h₁éḱwos yugóm` (8 ok)
10. `h₂ékʷeh₂ mē pléh₁dʰoyh₁t gʷíh₃woyh₁t-kʷe` (8 ok)

Old English: Mother Earth, you who nourish cattle and mortals! Give this one many sons. May she grow strong. You who nourish the rye and the tree, hear us! May the wolf not seize the sheep. May the beast not enter the enclosure. May the locust not eat the rye. May no one steal the lamb, and may the lamb not die. May the horse not break the yoke. May the water not swell. May she live.

New English: Broad Earth, our mother! You who nourish cattle and mortals! Give this one many sons; may she grow strong. You who nourish the rye, the tree, hear us! Now may the wolf not seize the sheep. Now may the beast not enter our enclosure. May the locust indeed not eat the rye. May no one steal the lamb, and may it not die. May the horse indeed not break the yoke. May the water not swell, and may she live.

### t033-0037 (t3-t033-00037) At the Threshold

Old lines:

1. `túH ḱósyo ḱóymosyo pótnih₂ h₁eǵóh₂-kʷe wiHrós` (13)
2. `wiḱdʰí` (2)
3. `wéyḱm̥` (2)
4. `twé h₁n̥dóm wéǵʰōh₂` (5)
5. `mē h₃sléydʰs` (2)
6. `ne dedwóyh₂e` (4)
7. `krépos moy Hwérdʰt ḱḗr-kʷe moy tetórpe` (10)
8. `péh₂wr̥ toy moy péh₂wr̥ h₁nómn̥-kʷe toy moy h₁nómn̥` (13)
9. `wékʷesh₂ toy ḱlḗm` (5)
10. `túH moy lewbʰós` (4)
11. `nu stéh₂t séh₂ léwkt-kʷe péh₂wr̥ nu h₂éǵt wiHrósyo méh₂tēr` (14)
12. `ḱós moy bʰréh₂tēr ḱéh₂-kʷe moy méh₂tēr` (9)
13. `swḗḱure swéḱure` (6)

New lines:

1. `túH ḱóymosyo pótnih₂ h₁eǵóh₂-kʷe wiHrós` (11 ok)
2. `wiḱdʰí` (2 MISS)
3. `h₁eǵóh₂ wéyḱm̥ twé h₁n̥dóm wéǵʰōh₂ mē h₃sléydʰs` (11 ok)
4. `ne dedwóyh₂e krépos moy Hwérdʰt` (8 ok)
5. `méǵh₂-kʷe moy ḱḗr tetórpe` (8 ok)
6. `péh₂wr̥ toy moy péh₂wr̥ h₁nómn̥-kʷe toy moy h₁nómn̥` (13 MISS)
7. `nu toy wékʷesh₂ ḱlḗm túH-ge moy lewbʰós` (11 ok)
8. `nu stéh₂t séh₂ úd léwkt-kʷe péh₂wr̥` (8 ok)
9. `nu h₂éǵt wiHrósyo méh₂tēr ḱós moy bʰréh₂tēr` (11 ok)
10. `ḱéh₂-kʷe moy méh₂tēr` (5 MISS)
11. `nu swḗḱure swéḱure-kʷe` (8 ok)

Old English: "You are the mistress of this household, and I am the man." "Enter." "I enter. I shall carry you in. Do not slip." "I am not afraid. My body has grown strong, and my heart is content." "Your fire is my fire, and your name is my name." "I have heard your words." "You are dear to me." Then she stood up, and the fire shone. Then the husband's mother said: "This is my brother, and this is my mother." "Brother-in-law! Father-in-law!"

New English: "You are the mistress of the household, and I am the man." "Enter." "I enter. I shall carry you in. Do not slip." "I am not afraid. My body has grown strong, and my great heart is content." "Your fire is my fire, and your name is my name." "Now I have heard your words; you are indeed dear to me." Then she stood up, and the fire shone. Then the husband's mother said: "This is my brother, and this is my mother." "Now, brother-in-law and father-in-law!"

### t033-0038 (t3-t033-00038) The Husband's Brother Greets the Bride

Old lines:

1. `h₁eǵóh₂ toy dayh₂wḗr` (5)
2. `bʰréh₂tēr toy h₁ésoh₂` (5)
3. `dáyh₂wer tetórph₂e` (5)
4. `wiHrós moy kúdʰe h₁ésti` (7)
5. `h₁éḱwons wédʰeti` (5)
6. `gʷm̥yḗti nu sdtā́m dayh₂wḗr swēḱurós-kʷe` (11 ok)
7. `spéḱye ḱóm h₂éǵrom h₁énom-kʷe kólHonm̥` (11 ok)
8. `h₁éwkesi` (3)
9. `ḱós moy swēḱurós h₁énos-kʷe moy swéḱuros` (12)
10. `bʰréh₂ter gʷm̥sḱé` (4)

New lines:

1. `h₁eǵóh₂ toy dayh₂wḗr bʰréh₂tēr-ge toy h₁ésoh₂` (11 ok)
2. `dáyh₂wer-ge h₁eǵóh₂ tetórph₂e` (8 ok)
3. `nu moy wiHrós kúdʰe h₁ésti` (8 ok)
4. `h₁éḱwons wédʰeti gʷm̥yḗti` (8 ok)
5. `nu sdtā́m dayh₂wḗr swēḱurós-kʷe` (8 ok)
6. `spéḱye ḱóm h₂éǵrom h₁énom-kʷe kólHonm̥` (11 ok)
7. `nu snúse n̥sméy h₁éwkesi` (8 ok)
8. `ḱós moy swēḱurós h₁énos moy swéḱuros` (11 ok)
9. `bʰréh₂ter gʷm̥sḱé` (4 MISS)

Old English: "I am a husband's brother to you. I shall be a brother to you." "I am content, husband's brother. Where is my husband?" "He is leading the horses. He will come." Then the husband's brother and the wife's brother sat down. "Look at this field and at that hill yonder. You will become accustomed." "This is my wife's brother, and that one yonder is my father-in-law." "Come, brother."

New English: "I am a husband's brother to you; I shall indeed be a brother to you." "I am indeed content, husband's brother. Now where is my husband?" "He is leading the horses. He will come." Then the husband's brother and the wife's brother sat down. "Look at this field and at that hill yonder. Now, daughter-in-law, you will become accustomed to us." "This is my wife's brother; that one yonder is my father-in-law." "Come, brother."

### t033-0039 (t3-t033-00039) Wedding Song

Old lines:

1. `h₁éḱwōs HeHḱéwes` (5)
2. `só wérsēn séh₂-kʷe léwks` (6)
3. `tóysōm dyéwmn̥ ń̥dʰgʷʰitom` (7)
4. `wénh₁os méǵh₂ lewbʰéh₂ h₂éwsōs ń̥dʰgʷʰitom ḱléwos` (13)
5. `dayh₂wḗr mléwHti swēḱurós mléwHti swéḱuros mléwHti ǵm̥rós-kʷe mléwHti` (23)

New lines:

1. `h₁éḱwōs HeHḱéwes só wérsēn séh₂-kʷe léwks` (11 ok)
2. `tóysōm dyéwmn̥ ń̥dʰgʷʰitom wénh₁os méǵh₂` (11 ok)
3. `nu lewbʰéh₂ h₂éwsōs ń̥dʰgʷʰitom-ge ḱléwos` (11 ok)
4. `dayh₂wḗr mléwHti swēḱurós mléwHti` (11 ok)
5. `swéḱuros mléwHti ǵm̥rós mléwHti` (11 ok)

Old English: Swift are the horses. He is a virile man, and she is a light. Their splendor is imperishable. Love is great. Beloved dawn! Imperishable fame! The husband's brother speaks, the wife's brother speaks, the father-in-law speaks, and the son-in-law speaks.

New English: Swift are the horses; he is a virile man, and she is a light. Their splendor is imperishable; love is great. Now, beloved dawn! Imperishable fame indeed! The husband's brother speaks, the wife's brother speaks; the father-in-law speaks, the son-in-law speaks.

### t033-0040 (t3-t033-00040) The Father Advises the Groom

Old lines:

1. `wédʰes` (2)
2. `ph₂sdʰí toy pótnih₂m stérge-kʷe` (8 ok)
3. `h₁íh₂m̥ mē dʰrugʰyés` (5)
4. `déh₃ut toy téwe swéḱuros h₁íh₂m̥` (10)
5. `h₂éǵrom h₂érh₃ye gʷṓs-kʷe h₂lékse` (9)
6. `ḱléwsoh₂ memónh₂e-kʷe` (6)
7. `h₁sdʰí toy swēḱurṓy ḱéywos h₁éy-kʷe toy ḱéywos h₁éseti` (15)
8. `dh₃yéh₁t dʰéǵʰōm usméy polh₁úns suHnúns nu h₂éǵt swéḱuros` (15)
9. `túH moy ǵm̥rós h₁eǵóh₂-kʷe toy swéḱuros` (11 ok)
10. `ḱóm píph₃ōmes` (4)
11. `swéḱure ǵḿ̥re swḗḱure-kʷe` (9)
12. `n̥smé ḱl̥nuté` (5)

New lines:

1. `wédʰes nu toy ph₂sdʰí pótnih₂m` (8 ok)
2. `stérge-kʷe h₁íh₂m̥ mē dʰrugʰyés` (8 ok)
3. `nu toy déh₃ut téwe swéḱuros h₁íh₂m̥` (11 ok)
4. `h₂éǵrom h₂érh₃ye gʷṓs h₂lékse` (8 ok)
5. `nu twé ḱléwsoh₂ memónh₂e-kʷe` (8 ok)
6. `nu toy h₁sdʰí swēḱurṓy ḱéywos` (8 ok)
7. `h₁éy-kʷe toy ḱéywos h₁éseti` (8 ok)
8. `nu dh₃yéh₁t dʰéǵʰōm usméy polh₁úns suHnúns` (11 ok)
9. `h₂éǵt swéḱuros túH moy ǵm̥rós` (8 ok)
10. `h₁eǵóh₂-kʷe toy swéḱuros ḱóm píph₃ōmes` (11 ok)
11. `swéḱure ǵḿ̥re swḗḱure` (8 ok)
12. `n̥smé ḱl̥nuté` (5 MISS)

Old English: "You have married. Protect your wife, and love her. Do not deceive her. Your father-in-law gave her to you. Plough the field, and guard the cattle." "I hear you, and I remember." "Be a friend to your brother-in-law, and he will be a friend to you. May the Earth give you two many sons." Then the father-in-law said: "You are my son-in-law, and I am your father-in-law. Let us drink together." "Father-in-law, son-in-law, brother-in-law: hear us!"

New English: "You have married; now protect your wife, and love her. Do not deceive her. Now your father-in-law gave her to you. Plough the field; guard the cattle." "Now I hear you, and I remember." "Now be a friend to your brother-in-law, and he will be a friend to you. Now may the Earth give you two many sons." The father-in-law said: "You are my son-in-law, and I am your father-in-law. Let us drink together." "Father-in-law, son-in-law, brother-in-law: hear us!"
