# Tier 3 batch t035 review (farm instruction, household and farm life; 40 texts)

Brief: docs/generation/reviewer-brief.md (`review-v1`). Reviewer: claude-opus-5-5, 2026-10-30.

## Procedure

- Packet: `scripts/make_review_packet.py t035 --n 20 --plants 5 --tier1 3`, giving 28 items (20 real, 5 planted, 3 Tier 1). Nothing under data/audits/ was read.
- Blind back-translation came first. Six items were translated from the `pie` field alone, and the English was never printed. Output: `docs/audits/packets/t035-blind-translations.jsonl`.
- Verdicts: `docs/audits/packets/t035-verdicts.jsonl`, sha256 `2f0d06d2bd1a7a294e76e522d74539867f04238954d4517044848c2605f17ad2`.
  - Saved before corpus/ or the plans were opened.
  - Every token was checked against `Lexicon.cells()`, `.participle_cells()` and closed_class.json, using a scratch script that maps each form to its cell.
- Then `resolve_review_items.py t035` and `score_review.py t035` were run.

## Calibration

| | |
|---|---|
| Plant recall | **4/5** (all 4 caught plants named) |
| Tier 1 judged wrong | 0/3 |
| Real items wrong | **0/20** |
| Real items minor | 7/20 |

The 4 plants caught, each a valid PIE form put in the wrong cell:
- `b967ccc3` péh₂urih₁: NOM.DU 'two fires', where the singular 'the fire' is meant.
- `b5128e60` h₂éḱesi: LOC.SG used as the object of 'cut off the ears'.
- `5d6229c8` widétām: AOR.3DU with a singular subject.
- `b3575981` wérǵōy: DAT.SG used as the object of 'did the work'.

The fifth plant was not found. Every remaining token in the packet resolves to a valid engine cell that fits its context.

## Blind back-translation agreement

- **Good:** 95b4d699, b5128e60, 1038c36b. The sense matched clause by clause. The only doubts were single words: tinéh₁eti 'thaws', h₃roǵéye 'straighten', stéwdt.
- **Partial:** 7f887dad and f53fb470.
  - 7f887dad: I read gʷr̥néHomes as 'swallow' (it means 'praise') and missed h₂roh₁dʰéyet 'spoke'.
  - f53fb470: I read dʰoHnéh₂m as 'a gift' (it means 'grain').
- **Weak:** 9b3c9d80. I read dʰéh₁leh₂ (neuter plural of dʰéh₁lom 'deed') as a noun 'nursing woman'. That was the reviewer's error, not the text's.

## Wrong items

None among the real packet items. The 4 wrong verdicts were all plants and need no fix.

## Minor items (packet)

- **7f887dad, 1c8b761d, 67e1bd14, 03fe84e6, 2e1b9054:** h₂roh₁dʰéyeti is used as 'speak'.
  - The lexicon gloss is 'to speak', so the plans follow their gloss.
  - But that sense rests on Germanic alone (Goth. rodjan), and pie/glosses.py derives 'to think' for it.
  - This is a lexicon question, not a plan error. Reported; no plan change.
- **9b3c9d80:** bʰéwdʰt (AOR) for 'at dawn it wakes'.
  - The verb has only aorist forms, so the gnomic aorist is what brief rule 8 asks for. Acceptable.
  - ph₂wéns wékʷesh₂ 'words of the fire' is translated as 'words about the fire'. This is a slight stretch; left as is.
- **Withdrawn after review:**
  - f53fb470: légʰeti is the subjunctive of légʰt, which correctly renders 'let him lie down'.
  - 2e1b9054: tóybʰos standing for a dual is expected (brief rule 17).

## Second pass: all 40 records against planner-brief-v4

- **Modern or coined words:** none.
  - The compounds ń̥werǵos 'workless' and ń̥h₂eydʰos 'fireless' are privative bahuvrihis built by the engine.
  - mógʰus and pṓlHos are flagged project reconstructions.
- **Instructions:** they read as instructions.
  - Imperatives keep a 2sg addressee throughout (00001–03, 09, 14, 16, 24, 29, 32, 36, 38, 40; 00031 is a household rule).
  - Conditions and temporal clauses are marked with h₁yód plus a subjunctive.
  - Laws of the type 'whoever …' use h₁yós … só.
- **h₂éǵeti:** used only for 'drive' (00003, 04, 12, 18, 24, 31, 36). The realizer's 'say' (h₂egjt) homophone warnings were each checked, and all of them mean 'drive'.
- **Fear verbs:** bʰéyh₂t appears in 00018 and 00035, both times with no complement, so no ablative is needed.

Plan fixes in data/generation/plans/t035.jsonl:

| Record | Problem | Fix |
|---|---|---|
| 00011, 00016, 00039 | bʰoréyeti 'to be carrying around' (iterative-causative) used for a single act of carrying (the same kind of slip as the earlier causative-for-plain-verb finding) | 00016 → bʰéreti 'carry'. 00011 and 00039 → wédʰeti 'bring', with the English changed to "bring it to the master" and "brought it to his own mother". A third bʰéreti would have exceeded the per-lexeme cap of 8. 00006 keeps bʰoréyeti, where "carried the seed about" is correct. |
| 00015 | English "The mistress of the house": pótnih₂ is only 'mistress' | English changed to "The mistress led him to the hearth." |
| 00028 | Number drift: the mother addressed the children with a 2pl imperative (bʰérete); then "the two went off" and "the two sat" were dual; then "the children sang" was plural | The children are dual throughout: IO DU, IMP 2DU bʰéretom, final clause ǵénh₁m̥nih₁ … kh₂nétām. English: "the two children" |

Records checked and left alone:
- 00038: the nominal clause "h₁éḱwos HeHḱús", then drémt …
- kʷékʷlos 'chariot' and 'wagon': the gloss includes 'cart; wagon; chariot'.
- 00013 h₁éwkt 'learned': the gloss is 'become accustomed (to), learn'.
- 00002 dʰéwgʰti 'is fruitful'.

## Re-realization and gate

`realize_plans.py data/generation/plans/t035.jsonl --batch t035 --model claude-opus-5-5 --prompt-id tier3-planner-v4`:

- **Gate: PASS.** 40/40 realized, reject rate 0.0, all_exact.
- **Lexeme use:** the most-used lexeme appears 8 times, at the cap of 8.
- **Vocabulary:** 258 distinct lexemes, 159 distinct roots.
- **Other figures:** 12 formula uses, 35.65 words per record, 27 warnings (antecedent and homophone notices, all checked).
- **First re-run:** it failed with bʰéreti used 10 times; this was fixed by the substitution described above.

## Engine and lexicon findings (report only; for the lead)

1. **The oblique plural of gʷṓws is built on e-grade gʷéw-.**
   - The forms are gen. pl. gʷéwōm, dat. pl. gʷéwbʰos (00008 has gʷéwōm).
   - Ved. gávām and Gk βοῶν point to o-grade *gʷówōm.
   - Check the gʷṓws spec.
2. **MID.INJ.2SG is realized with -th₂e.**
   - Examples: mē wérteth₂e in 00002, mē ḱl̥nith₂é in 00024.
   - The usual secondary middle 2sg is *-so (Ved. -thās is the alternative). The engine's choice should be documented, or *-so used for the injunctive in prohibitions.
3. **h₂roh₁dʰéyeti 'to speak' rests on Germanic alone.**
   - The derived gloss in pie/glosses.py says 'to think'.
   - Consider marking the gloss as approximate or single-branch, so planners prefer wéwket, sokʷéyeti or mléwHti for 'speak'.

No release approval was set, and nothing was committed.
