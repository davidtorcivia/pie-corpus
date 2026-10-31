# Tier 3 batch t108 review (food and cooking, in-world dialogues)

Reviewer: calibrated reviewer (`review-v1`, docs/generation/reviewer-brief.md), 2026-10-31.
Batch: 40 two-speaker dialogues, `prompt_id: tier3-dialogue-inworld-v1`, model claude-opus-5-5.

## Procedure

1. Packet: `scripts/make_review_packet.py t108 --n 20 --plants 5 --tier1 3` → 28 items (20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items from the `pie` field only (no English printed):
   `docs/audits/packets/t108-blind-translations.jsonl`.
3. Verdicts written and saved before opening corpus/ or plans:
   `docs/audits/packets/t108-verdicts.jsonl`,
   **sha256 `b9925aad528e9238120bf80a2b4fda6a582d9dc9dba5390fe922428947079c04`** (confirmed by resolve_review_items.py).
4. `resolve_review_items.py t108`, then `score_review.py t108`. data/audits/ was not opened.
5. Second pass: all 40 records read in full against planner-brief-v4.md and the in-world dialogue brief.

## Calibration result

| | |
|---|---|
| Plant recall | **5/5** (all named correctly) |
| Real items judged wrong | **0/20** |
| Real items judged minor | 0/20 |
| Tier 1 items judged wrong | 0/3 |

All five flagged items were plants:
- 7a80196e: `gʷm̥yétes` (PRS 2/3 dual) with the plural subject gʰósteyes. The corpus has gʷm̥yónti.
- cffac6cd: `dedh₃wós` (PRS 1du, "we two give") where the gods are the subject. The corpus has dédh₃n̥ti.
- 3e063b9c: `topéyonti` (3pl) where the cook says "I heat stones". The corpus has topéyoh₂.
- 802f72b6: herd in the dat./abl. pl. (`stéh₂dʰh₁oybʰos`), so the PIE reads "I drive the mountains for the herds". The corpus has stéh₂dʰh₁om pérwōr.
- 40167b33: `dʰr̥ǵʰtéh₂` (fem.) as the predicate of neuter mḗms. The corpus has dʰr̥ǵʰtóm.

Corrections to my own verdict notes, made after checking the cells:
- On 3e063b9c I also noted the aorist Hyéh₁km̥ as a minor. I withdraw that: Hyeh1kt is aorist-only, so a gnomic aorist is correct. The same holds for bhest and denkjt-2.
- On df4b64b5 I read `nos` as a dative. In the record it is POSS GEN.PL "our", so the English "our uncle" is exact.

### Blind back-translation agreement

5 of 6 items agree closely: bd27c80c, 80dbd155, df4b64b5, 920c9038, 8414aaba.
- 80dbd155: I read h₂énHe as "grandfather". It is the project reconstruction h₂énHos "grandmother", and the English is right.
- 8414aaba: I was unsure about masc. h₁éy/ḱóm. mā́dsos is masculine, so they agree.
- 7a80196e (a plant): I did not recognise moréye as the imperative of moréyeti "kill" and read it as "on the spit". I still flagged the item, for the dual verb.

## Second pass: all 40 records

**Real wrong before fixes: 0. After fixes: 0. Minor: 3 before, 0 after.** At the lead's request (2026-10-31), the 3 minors
were fixed at the source, and 12 of the 15 records where the model never asked back now have a model question.
See "Fixes after the lead's request" below.

Checks made on every record:
- **Speakers and per-sentence English:** every clause has a speaker, there are exactly two speakers and the user speaks first.
  Every speaker change starts a new sentence, and every sentence-initial clause has its English. The English
  fields joined together equal the plan English. Each record has 4–14 clauses and 2–8 turns. No problems.
- **Turns answer each other:** yes, in all 40.
  - 0010 and 0031 ("How do I say …?") follow the 3b §2 request pattern.
  - In 0020 the son tells the user "I fear my father". This is coherent if the user (who says "Son") is the mother. If the user is the father, "I fear you" would be expected. PIE and English agree, so this is not counted.
- **Nothing modern or coined.** The project reconstructions (h₂énHos, spelom, gʷʰermós) are allowed.
- **Senses checked against the full glosses:**
  - gʷéru "spit, skewer" (0001, 0025, 0034).
  - dʰoHnéh₂ "grain" for the bread theme (0006, 0027). The English says "grain".
  - bʰn̥ǵʰú h₂mélǵos "thick milk" for cheese (0003, 0037). The English says "thick milk".
  - wóyḱos-2 "settler, villager" = "neighbour".
  - piḱrós "pointed, bitter".
  - sph₁rós "thriving; fat".
  - dweh₂rós "long; far away".
  - móros "death; plague".
  - moḱs "quickly; early".
  - ml̥dús "soft, weak".
  - éti "also, too".
  - wedʰ- "lead; bring".
  - h₂éwh₂os "maternal grandfather / uncle".
  - gʰóstipotis "host".
  - h₂ólut "beer".
- **Causatives:** the gloss decides, and all are correct.
  - topéyeti "make hot", used transitively.
  - moréyeti "kill".
  - sodéyeti "set".
  - logʰéyeti "lay".
  - h₂sowséyeti "make dry".
  - srobʰéyeti "sip, suck".
  - h₁opéyeti "make reach; give".
  - wortéyeti "turn".
  - troméyeti "tremble (in fear)" (reflex-confirmed, intransitive).
- **Fearing with the ablative:** tóybʰos (0005), ph₂trés (0020), wĺ̥kʷoybʰos (0025), ǵʰimés (0037). All correct.
- **Cows are feminine** (gender f, with fem. adjectives and pronouns) in 0003, 0012, 0027, 0035, 0037 and 0039.
- **h₂élyos** is used as an adjective: a MOD in 0007 and 0031, and with a gender in 0007 (m) and 0034 (n).
- **Predicate adjectives with dropped subjects** take the right gender:
  - suHróm/bʰn̥ǵʰú (n, milk), 0003.
  - h₂yuHn̥ḱéh₂ (f, grandmother), 0016.
  - sph₁rós (m, pig), 0026.
  - gʷʰermós (m, pot), 0028.
  - ḱéyweh₂ (f, the woman addressed), 0010 and 0019.
- **Short-answer case:** all 16 np answers have the case the question asks for (LOC, ABL, ACC, or NOM for subjects).
- **Athematic obliques** match the cells and the paradigm types:
  m̥lités, m̥dʰéwi, h₂éluts, gʷréws/gʷréwi, déh₂nus/déh₂newi, pr̥kʷéws, ǵʰimés, ǵʰyémi, ǵʰiméni, h₂Hséh₂i, mémsi,
  ph₂wéni, skuHtíh₁ and gʷr̥h₂unés.
- **Enclitics** are in second position, or after a -kʷe host. téwe/méne are the full forms, used beside the clitic te/me.

### The 9 realizer WARNs (all checked; all fine)

| Record | Warning | Ruling |
|---|---|---|
| 0001 c1 | 3rd person beside a VOC | Fine. The subject is "it" = the meat. |
| 0005 c7 | h₂éǵomes drive/say homograph | Fine. It means "drive away" with smoke. |
| 0035 c0 | h₂éǵoh₂ drive/say homograph | Fine. It means "drive the herd". |
| 0038 c6 | h₂éǵeti drive/say homograph | Fine. It means "drives away plague". |
| 0010 c4 | so n SG has no referent | Fine. tód "that" is the phrase just taught. |
| 0031 c3 | so n SG has no referent | Fine. tód is the phrase just taught. |
| 0015 c6 | so m SG has no referent | Fine. só is the guest (clause 0). |
| 0029 c2 | i n PL has no referent | Fine. h₁íh₂ is honey + water (np clause 1). |
| 0034 c3 | i f SG has no referent | Fine. h₁íh₂m̥ is the goose ǵʰh₂éns (f, clause 0). |

### Minor items (fixed afterwards: see below)

- 0030 c7–8: ssénti and sh₂ént are plural, with téḱneh₂ as the dropped subject. The same record has téḱneh₂ h₁ésti in the
  singular. Plural agreement with animate neuter plurals is attested (Greek), so this is minor.
- 0013 and 0017: wedʰ- "lead, bring" is used for a fish and for wood. The gloss allows "bring", but bʰer- would fit better.
- 0010: moḱs h₁éwks is an aorist ("you have learned quickly") for the English "you learn quickly".

### Brief compliance (for the lead)

- **The model asks things back** in 25 of 40 records. It never asks a question in 15:
  0002, 0005, 0006, 0010, 0015, 0016, 0020, 0026, 0027, 0029, 0031, 0032, 0036, 0038, 0039.
  The in-world brief says the model "asks things back". Twelve of these now have a model question (see below).
  0036, 0038 and 0039 still have none.
- **Openings are varied:** 17 different first addresses, plus 6 with none. The most common, ph₂tér, h₂éwh₂os and h₂énHos,
  open 4/40 each, well under the one-quarter limit.

## Fixes after the lead's request (plans edited, batch re-realized)

The pre-fix plans were backed up to a scratch copy, t108-plans-before.jsonl.
The edits are in `data/generation/plans/t108.jsonl` and were re-realized with the batch's own command.

Result: gate **PASS**.
- 40/40 realized, all exact, reject_rate 0.
- max_lexeme_uses 6 (cap 7 at 1303 tokens). theme_core uses ≤ 20.
- 10 WARNs. The new one is 0002 c11 (h₁íns "them" = the brothers, c8). It is fine.

Minors:
- **0010:** the English now says "You have learned quickly", which matches the aorist h₁éwks. h1ewkt-2 is aorist-only.
- **0030:** the verbs in c7–8 are now 3sg (sésti moḱs séh₂t), in agreement with téḱneh₂, as in the record's own téḱneh₂ h₁ésti.
- **0017:** wood is carried with bʰer- in c5 and c7: bʰére "bring!", bʰérom "I brought".
- **0013:** the fish is no longer "led" with wedʰ- in c5–6. It is given with déh₃t: méh₂trey nos h₁ím déh₃omes?
  "Shall we give it to our mother?" and h₁ésyeh₂ey … ḱérh₂sonm̥ déh₃omes "We will give her its head".
- To keep bʰer- under the cap, two other records changed:
  - **0023:** "Give me one tomorrow! I will give you two fish" now uses déh₃t (dh₃dʰí, déh₃oh₂).
  - **0039:** Fire now *conveys* the offering with wéǵʰeti, the Vedic havya-vāh- image.

The model now asks back in these records. In each, the user's next turn answers the question.
| Record | Model question | User answer |
|---|---|---|
| 0002 | kúdʰe toy bʰréh₂teres h₁sénti? | h₂éǵroy h₁sénti. Then the model: h₂éǵrom h₁idʰí h₁íns-kʷe moḱs wédʰe. This replaces "Bring your brothers … / I am going …" |
| 0005 | mélit lubʰyési? | h₁íd lubʰyóh₂. Then the user's own question about milk follows. |
| 0006 | kúdʰe téḱneh₂ h₁ésti? | h₂Hséh₂i. (np LOC) |
| 0010 | kúdʰe h₁éysi? | ḱóymom moy. (np ACC, goal) |
| 0015 | só n̥sméy h₃ésth₁h₂ léykʷeti? | ne kʷid léykʷeti. |
| 0016 | kéh₂nmn̥ wóydth₂e? | h₁íd ne wóydh₂e. |
| 0020 | h₂éydʰom h₂éydʰoh₂? | h₁ím h₂idʰdʰí. |
| 0026 | súHm̥ h₁élh₂esi? | h₁ím h₁élh₂oh₂. |
| 0027 | mh₂ḱróm méh₁nsm̥ dedórḱth₂e? | h₁óynom ne dedórḱh₂e. This is inside the existing turns. |
| 0029 | nu yéwHs wéḱsi? | yéwHs ne wéḱmi. |
| 0031 | pékʷtorm̥ wóydth₂e? | h₁ím ne wóydh₂e. |
| 0032 | h₁éwkesi? | h₁éwkoh₂. |

Every answer repeats the question's verb. The speaker, turn and per-sentence-English checks still pass: 4–14 clauses and
≤ 8 turns in every record. The model now asks back in 37 of the 40 records.

## Engine notes (report only; the lead fixes these centrally)

- `pie-lex-h1ayt` MID: the secondary 2sg ending is given as *-th₂e* (AOR h₁áyth₂e, used as the injunctive in 0002 c7:
  mē h₁áyth₂e). The handbook ending is *-th₂es* (Ved. -thās). The Hittite -tta type may be the source. Worth checking
  whether this is intended across all middle paradigms.
- `pie-lex-bholgjhis` ABL/GEN.SG: the first alternative is the acrostatic *bʰólǵʰis*, which is the same as the nominative (0023:
  séh₂lm̥ bʰólǵʰis h₁áyso "take salt from the bag"). It is defensible, but it is ambiguous for a learner. skéwHtis in the
  same batch takes the proterokinetic skuHtéys. Consider making bʰólǵʰeys the first alternative.

## Release inputs

- Plant recall 5/5 (≥ 4/5 required).
- Real wrong 0/20 in the packet, and 0/40 in the full read, after fixes. Minors 0 after the fixes.
- Gate PASS after the re-realization.

Approval is the lead's decision. No release metadata was written.
