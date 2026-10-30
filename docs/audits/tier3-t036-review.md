# Tier 3 batch t036 review (review-v1, 2026-10-30)

Batch: 40 in-world dialogues (council, war and peace, elders), `prompt_id: tier3-dialogue-inworld-v1`.
Reviewer: calibrated reviewer (claude-opus-5-5). Procedure: docs/generation/reviewer-brief.md.

## Procedure

1. Packet: `make_review_packet.py t036 --n 20 --plants 5 --tier1 3` → 28 items (20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items (PIE field only) before any English was printed:
   `docs/audits/packets/t036-blind-translations.jsonl`.
3. Verdicts written from the packet alone, checked against `Lexicon.load().cells()` (reverse lookup of every
   packet token) and `closed_class.json`: `docs/audits/packets/t036-verdicts.jsonl`,
   **sha256 `b1727383256c0d5c1cc4204c11e9791f43bb5d40acf024a81af10ec32d8db78d`**. Saved before corpus/ or the
   plans were opened.
4. `resolve_review_items.py t036`, then `score_review.py t036`. data/audits/ was never read.
5. Second pass: all 40 records read in full (speaker, PIE, per-sentence English, gloss) against
   planner-brief-dialogue-inworld.md.

## Calibration

| | |
|---|---|
| Plant recall | **5/5** (all 5 named; all flagged items marked wrong were the plants) |
| Tier 1 judged wrong | 0/3 |
| Real items wrong | **0/20** |
| Real items minor | 3/20 |

The plants found: fa0a6b2f (déh₃owos 1DU for 'we' the tribe), 93a3e33c (wékʷesos GEN where NOM is needed),
ae31aaa2 (h₁r̥sḱḗsi 2SG for 'I shall go'), 528fb4a5 (ih₂tés 2/3DU to one old man), 9e991aa0 (gʷm̥té 2PL to one son).
In each case I checked the corpus record and it has the correct form (déh₃omes, wékʷos, h₁r̥sḱṓh₂, yéh₂si, gʷm̥dʰí).

One self-correction before saving the verdicts: I first read 4b47e6dc's gʰóstis as palatal ǵʰóstis. A code-point
check showed it is plain g (U+0067), so the item stayed ok.

## Counts before and after fixes (whole batch, 40 records)

| | before | after |
|---|---|---|
| wrong | 0 | 0 |
| minor (sample, 20 real) | 3 recorded | 1 (t036-0005, a brief issue); 1 fixed (0012); 1 withdrawn (0017, reviewer error) |
| minor (whole batch, second pass) | 8 (0005, 0012, 0014, 0018, 0021, 0022, 0024, 0030) | 7 (0012 fixed) |

## Wrong items

None. Neither the packet nor the second pass found a real wrong item.

## Minor items and fixes

Fixed at the source (data/generation/plans/t036.jsonl, re-realized):
- **t036-0012** (packet 428c2ab4): `méromes` was the active subjunctive of mer- 'die', which is a middle verb
  (mr̥yétor). The slot is now voice MID, which realizes as `méromesdʰh₂`.
Withdrawn (reviewer error):
- **t036-0017** (packet 60915c6b): the verdict file records "wédōr is singular; English 'the waters'". That is
  wrong. The engine tags wédōr as NOM.PL, the collective (cf. Hitt. widār 'waters'), and a singular verb (mélh₃t)
  with a neuter plural subject is regular PIE agreement. The English "the waters came forth" was right. I briefly
  changed the plan's English to "the water", then reverted it before the final re-realization. The plan and the
  record are unchanged. The verdict file is sha-locked and still says minor; this report withdraws that verdict.

Left as they are (recorded):
- **t036-0005 and t036-0021**: the user asks "How do I say this?" (kʷíh₁ mléwHmi / kʷíh₁ ḱéywe sokʷéyoh₂), says a
  sentence, and the model repeats it word for word. The in-world brief allows this, since it imports 3b §2
  "Requests (How do you say …?)". But when both speakers already speak PIE, the echo carries no content, and it
  reads as a translation exercise left over from 3b. **Brief issue (for the lead):** inside the in-world brief,
  either drop the "How do you say" request type or have the model answer it by correcting or improving the
  phrasing.
- **t036-0014, 0018, 0024, 0030**: a bare accusative of a *person* used as the goal of motion: h₁íns h₁r̥sḱṓh₂ 'I
  shall go to them', h₁íns h₂éǵōmes, dusménesn̥s wédʰēti, twé … gʷm̥sḱéti. Elsewhere (00008, 00018 last clause) the
  batch uses próti + ACC. A bare goal accusative is safest with places. Stretched, not wrong.
- **t036-0022**: h₂éwgmn̥, glossed 'enlargement', is translated "strength". This is a stretched sense
  (cf. Lat. augmentum).
- **t036-0019**: sékʷeth₂e (MID.INJ.2SG) uses the engine's -th₂e. Not a plan error; see the engine notes below.

## Second-pass checks (all 40)

- **Modern or coined content:** none. No record has `neologism: true`, and no token is coined (`Lexicon.coined`
  is empty for every token). All themes are herds, kin, raids, wergild, oaths, bride-price, councils, Perkʷunos,
  Father Sky and Earth Mother.
- **Format:** every record has exactly two speakers, the user speaks first, every turn starts a new sentence, and
  each record has 2–8 turns. The ways of addressing the other speaker vary (kin terms, bahuvrīhi names, king,
  elder, friend, old woman, mistress); no single greeting opens more than a quarter of the dialogues.
- **Turn coherence:** every turn answers the one before it. The two echo dialogues (0005, 0021) are the only weak
  ones. Engine warnings about anaphora and person (0002, 0014, 0017, 0022, 0024, 0027, 0032, 0033) were each
  checked by hand: in every case the referent is in context and the person is the intended 3rd person.
- **Verb senses against glosses:** no swopéyeti-type misuse. The fear verbs (dedwóyh₂e, bʰebʰóyh₂e, bʰéyh₂t) never
  take a direct object. Other senses checked: h₁áy- MID 'receive' (override gloss: active 'give', middle
  'take/receive'); bʰoydʰéh₂ 'oath' (gloss 'pledge, oath'); kʷeḱ- 'catch sight of'; der- 'split' for 'divide'
  (0038); h₁ewk- 'become accustomed' for 'learn' (0033); h₂roh₁dʰéye- 'speak' (Goth. rōdjan). All are acceptable.
- **English against PIE:** this matches throughout, apart from the minor items above.

## Blind back-translation agreement (6 items)

| item | agreement |
|---|---|
| bb819bdd | full |
| 39db7a13 | substantial (took h₂érh₃yowos as an unclear noun phrase, not 'we two plough') |
| 5a39d49d | substantial (missed wéwke 'tell' in the 4th sentence) |
| d7701d98 | substantial (kʷósmōd read as 'why' instead of 'from whom'; the h₂éwih₁ 'with a sheep' clause was uncertain) |
| cc49d075 | partial (read ǵʰóstoh₁ as 'two guests' instead of 'hands', so the middle of the dialogue was lost) |
| 93a3e33c | partial (h₂roh₁dʰéye- read as 'succeed', tl̥nh₂dʰí as 'hold back'). This item turned out to be a plant. |

So 1 full, 3 substantial and 2 partial. Every divergence was a lexical misreading by the reviewer, not a
grammatical defect in the PIE.

## Engine and brief notes (report only)

- **Middle secondary 2sg ending (a convention to document, not a gap).** For MID.PST and MID.INJ 2SG the engine
  builds -th₂e (sékʷeth₂e), and for the primary forms -th₂er (MID.SBJV.2SG méreth₂er). This is the Ringe/Jasanoff
  system, and it is internally consistent. Fortson gives *-th₂es (Ved. -thās). It is worth stating in the
  morphology docs, because -th₂e is identical to the perfect 2sg ending.
- **Brief:** the "How do you say …?" echo request in in-world dialogues (see t036-0005 and t036-0021 above).
- **Gate lint:** accent_defect_tokens = 7 and accent_representation_tokens = 2. These are reported, not gated, and
  were not investigated in this review.

## Re-realization check

I diffed the corpus before and after the fixes. Only t3-t036-00012 changed its PIE (méromes → méromesdʰh₂), and
t3-t036-00017 is identical to before. The gloss strings of 00008, 00033, 00036 and 00038 also changed
(be.carrying → carry, be.walking → walk, be.pointing.out → show). Their PIE did not change. The cause is lexicon
gloss edits made by other agents while this review ran, which `realize_plans` picks up when it re-reads the
lexicon. These are not review changes.

## Gate

After re-realization (`realize_plans.py data/generation/plans/t036.jsonl --batch t036 --model claude-opus-5-5
--prompt-id tier3-dialogue-inworld-v1`): **PASS**. 40/40 plans realized and all are exact (all_exact), reject
rate 0.0, max lexeme uses 6, no duplicates.

## Release rule status (for the lead)

- plant recall 5/5 (≥ 4/5): met.
- real items wrong 0/20 after fixes (≤ 2/20): met.
- gate PASS: met.

Release approval was not set; that is the lead's decision.
