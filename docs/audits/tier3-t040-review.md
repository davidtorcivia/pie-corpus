# Tier 3 review: batch t040 (28-item packet + full second pass)

Batch t040 has 40 texts (24 epic, 16 parley) about cattle raids and parleys between warriors. The review followed `docs/generation/reviewer-brief.md` (review-v1):
- The packet was built with `make_review_packet.py t040 --n 20 --plants 5 --tier1 3`.
- Six items were back-translated blind, from the `pie` field only, before any English was read.
- The verdicts were written and hashed before `corpus/` or the plans were opened.
- `resolve_review_items.py` and then `score_review.py` were run. Nothing under `data/audits/` was opened.

Checks used: handbook knowledge (Fortson, Beekes, Ringe, LIV², Mallory & Adams, as remembered), `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json`, `Lexicon.cells()` and `scripts/lexq.py`.

- Verdicts: `docs/audits/packets/t040-verdicts.jsonl`, sha256 `7d3ae5e2294943440201db67121d9227b684e7aa47b6611abeaae3705495d40b`. The hash was recorded before the corpus or plans were opened.
- Blind translations: `docs/audits/packets/t040-blind-translations.jsonl`.

## Calibration (score_review.py)

| items | plants caught / named | plant recall | Tier 1 judged wrong | real wrong | real minor |
|---|---|---|---|---|---|
| 28 | 5 / 5 | **1.00** | 0 / 3 | 1 / 20 (0.05) | 7 |

The 5 flagged items that `resolve_review_items.py` identified as plants were these. Each is a single-cell slip:
- e279464b: GEN.PL gʷréwōm used as the object of 'found'.
- 1a41b5b2: 1sg bʰúHm̥ for 'that one became'.
- 4e2503a9: fem. ACC sweh₂déwih₂m as a predicate to neuter h₂mélǵos.
- 4cc5816e: INS.PL Hyudʰsmṓys for the nominative 'young warriors'.
- 08bc03a6: DAT/ABL.PL suHnúbʰos for 'the son'.

## Real packet items: verdicts after lookup

- **39bfbfb2 = t3-t040-00019, `h₁égʷʰis kréwh₂s` 'the blood of the serpent'. Scored wrong; reclassified engine-supported.** I judged this wrong because I took h₁égʷʰis for a misspelled nominative. `Lexicon.cells('pie-lex-h1ogwhis')`, however, is a deliberate acrostatic o/e paradigm: strong h₁ógʷʰi-, weak h₁égʷʰi-, GEN.SG h₁égʷʰis (alternative h₁égʷʰeys), cf. Gk ὄφις / ἔχις. The token is GEN.SG of the same lexeme, so the plan is right. **Engine note:** the primary GEN.SG has the same shape as a nominative. Readers, and the blind check, will take it as a second subject. Consider making h₁égʷʰeys primary. Report only.
- **25dc6b86 = 00009, `h₁ím h₂ewsér wédʰet` 'led ten horses to him'. Minor; fixed.** The goal was a person in the accusative. It is now IO, so the clause reads dusménēs h₁ésmey déḱm̥ márkons h₂ewsér wédʰet.
- **The minors below were withdrawn after lookup.** The lexicon or the engine supports each one:
  - 1169b9f0 / 25abfeb4 (00029, 00010): h₂elgʷʰ- is glossed 'bring in (as proceeds)'.
  - 315a1bef (00031): h₂éǵete is PST.2PL, i.e. the imperfect, not the present.
  - 14fb6857 (00007): h₂m̥bʰí is glossed 'in exchange for'.
  - d54c4b11 (00037): ǵnéh₃t is glossed 'to get to know, to meet'.
- **3761a04e = 00003, `bʰgih₁tó`. Minor; engine.** The `pie-lex-bhagt` spec has the weak stem `bʰg` for a root bʰeh₂g-. Zero grade should keep the laryngeal (bʰh₂g-). Report only.

Real packet items:

| | wrong | minor |
|---|---|---|
| as scored | 1 / 20 | 7 |
| after lookup and fixes | 0 / 20 | 1 |

- The scored wrong item (39bfbfb2) was withdrawn because the form is the engine's acrostatic GEN.SG.
- Of the 7 minors, 1 was fixed (00009) and 5 were withdrawn as gloss-supported.
- The 1 minor left is the engine-side bʰgih₁tó.
- Also checked: 00016 'removes' for méyth₂t is in its gloss ('change, exchange, remove').

## Blind back-translation (6 items)

Agreement was good on all six: the plot, the participants and most verb senses were recovered. These were the misses:
- **753f31f2 (00020):** péruns was unclear. It is ABL.SG of pérwr̥ 'rock' ('out of the mountain'), which is correct.
- **25dc6b86 (00009):**
  - The opening clause ('lay on the earth … stood over him') was misparsed.
  - néseto 'returned home' and wikétām 'fought' were left uncertain.
- **1169b9f0 (00029):** méwdont 'rejoiced' was unsure, and ǵʰyént 'drove' was unsure.
- **c71da05c (00032):** gʰórtons 'enclosures' and nutā́m 'bowed' were recovered only tentatively.
- **14fb6857 (00007):** léytt 'went away to his people' was misread.
- **d54c4b11 (00037):**
  - stóygʰos was read as 'hall'; the text means 'road'.
  - sokʷéyet 'answered' seemed odd as a reply.

## Second pass: all 40 records against planner-brief-v4

Nothing modern or coined was found. The second pass checked:
- verb senses against their glosses, including the lexq-sourced words, causatives (h₁opéyeti 'make reach' = hand over, wodʰéyeti), the ablative with fearing (gʷrúbʰos mē tréses, ph₂wéns … dedwimé, dʰn̥wéns trésont, h₁éymos mē bʰebʰéyh₂omes, pérkʷunōd bʰebʰóyh₂e: all ablative), and pronoun tracking;
- whether speeches answer each other.

### Wrong (1), fixed

- **00002 (parley: Man-Minded and Of-True-Fame at the ford). The narrative contradicted itself.**
  - What the text said: Of-True-Fame keeps the raided cattle and pays ten horses 'in exchange for them'. Man-Minded takes the horses, and then 'the cattle followed Man-Minded'. The closing speaker, 'the other' ('I live, and horses are born again'), can only be the man who lost the horses, i.e. Of-True-Fame.
  - Fix: the cattle now follow Of-True-Fame (h₁sn̥tyóḱlewesm̥), and the closing speaker is named as Of-True-Fame instead of the unclear h₁éteros.

### Minor, fixed

- **00015, the English said more than the PIE.**
  - 'and only a small cow sank': 'only' has no PIE word. It now reads 'and a small cow sank'.
  - 'On the other side they ate grass': the PIE has h₂én 'there'. The pro-drop 3pl also read as 'the men ate grass'. The clause now has the overt subject gʷówes: 'There the cattle ate grass and lay down.'
- **00022, the referent was unclear.** In 'In the morning they came; they found spears, they did not find livestock. They were hungry, and they fled', the last subject was 'the warriors', so the warriors seemed to find spears and flee.
  - Fix: an overt subject, h₁énoy 'those (yonder) men'. It picks up the earlier 'Who are those men yonder?' (kʷéyes h₁énoy h₂néres).
  - bʰóres 'thieves' was tried first, but it pushed bʰṓr to 13 uses, over the cap of 12.
- **00009:** the dative goal (above).

### Minor, left as they are

- 00016, 00035: `ǵn̥h₃n̥tó` is a 3pl middle with a dual subject. The engine seems to lack the 3du middle. This is an engine gap; report only.
- 00014: the gnomic aorist `m̥rént … mért` is used for 'cattle die, kin die'. Brief rule 8 prefers the present for proverbs.

## Padding

In the repair pass the planner added sentences to almost every text to raise the token-scaled caps. Most of them are real episodes: pursuits, speeches, rewards, mothers' reactions, omens, closing images that echo the theme (the snow melting in 00011, the stars in 00039). I judged five added sentences to be flat filler with no function in their story, and trimmed them. The gate still passes.

| record | trimmed sentence |
|---|---|
| 00002 | 'Then the sun sank, and the night was cold.' |
| 00003 | 'The dogs licked the cauldron.' |
| 00015 | 'The men trembled with cold.' (the text now ends on the mead offered to the river) |
| 00037 | 'The road was long.' |
| 00040 | 'The sun shone on the feast.' |

These were kept as borderline: 00001 'Wolves cried on the black hills' (tension), 00029 'The snow on the hills was deep' (the wild life of the wolf-youths), and 00025 'The meat was sweet, and the mead was strong' (contrast with the widow's silence).

## Fix and gate

The plan edits are in `data/generation/plans/t040.jsonl`. The corpus was re-realized with `scripts/realize_plans.py data/generation/plans/t040.jsonl --batch t040 --model claude-opus-5-5 --prompt-id tier3-planner-v4`. Seven records changed: 00002, 00003, 00009, 00015, 00022, 00037, 00040.

| | before | after |
|---|---|---|
| gate | PASS | **PASS** |
| reject rate | 0 | 0 |
| tokens | 2325 | 2308 |
| words / record | 54.1 | 53.7 |
| max lexeme uses (cap 12) | 12 | 12 |
| distinct lexemes / roots | 351 / 195 | 349 / 194 |
| formula uses | 18 | 18 |

Release status was not set and nothing was committed.

## Violations

- Procedure: none. Verdicts were saved and hashed before `corpus/` or the plans were opened, and nothing under `data/audits/` was read.
- Brief: none outside the minors above. The planner's added episodes were mostly genuine; the five filler sentences are the exception.

## Engine items for the lead (report only)

1. The h₁ógʷʰis acrostatic GEN.SG primary form h₁égʷʰis reads as a nominative. Consider h₁égʷʰeys as primary.
2. The `pie-lex-bhagt` weak stem `bʰg` drops the root laryngeal (expected bʰh₂g-, as in bʰh₂gih₁tó).
3. A dual subject with a middle aorist comes out 3pl (ǵn̥h₃n̥tó). The 3du middle cell is missing.
