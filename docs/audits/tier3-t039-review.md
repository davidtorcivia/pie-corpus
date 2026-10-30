# Tier 3 batch t039 review (review-v1, 2026-10-30)

Batch: 40 in-world dialogues in which an elder or parent teaches a child (`tier3-dialogue-inworld-v1`).
Reviewer: calibrated reviewer (Claude Opus 5.5). Procedure: docs/generation/reviewer-brief.md.

## Procedure

1. Packet: `make_review_packet.py t039 --n 20 --plants 5 --tier1 3`, giving 28 items (20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items, done before any English was printed (only the `pie` field was shown):
   `docs/audits/packets/t039-blind-translations.jsonl`.
3. Verdicts on all 28 items were written before opening corpus/ or the plans: `docs/audits/packets/t039-verdicts.jsonl`,
   **sha256 `9dfaa43f6ff161ba689999759d026948f41b99c89bd8c1749b99ac3e81f3e3a7`**. Nothing under data/audits/ was read.
4. `resolve_review_items.py t039`, then `score_review.py t039`.
5. Second pass: all 40 records read in full (speaker, PIE, per-sentence English, gloss, plan slots) against
   planner-brief-dialogue-inworld.md.

## Scores

| | value |
|---|---|
| Plant recall | **5/5** (all 5 caught and named) |
| Tier 1 judged wrong | 0/3 |
| Real items judged wrong (packet) | **0/20** before fixes, 0/20 after |
| Real items judged minor (packet) | 6/20 as filed; 2 held up after checking the records (see below) |

The five plants: 604e7b75 (dʰéwgʰesi 2sg for 3sg), b469410e (kéh₂ileh₂bʰos DAT/ABL.PL for NOM.SG), 017235db
(bʰoydʰéh₂h₁ dual for singular), ea155795 (wĺ̥kʷoh₁ dual for singular), 7880faf5 (gʰbʰestéyey DAT for NOM).
In 7880faf5 I also flagged só + ǵʰédos as a gender clash. That was my mistake: the lexicon segments ǵʰéd-o-s as a
masculine o-stem, so só is correct, and the unplanted record t3-t039-00022 is fine.

## Packet minors, checked against the records

| item | record | verdict filed | outcome |
|---|---|---|---|
| de28893a | 00003 | minor: masculine anaphor for the cow; plural instrumental for "both hands" | **Real, fixed** (see Fixes). |
| 7dfbd21b | 00036 | minor: woséyoh₂e (MID.PST.1SG) rendered as "I have dressed myself" | Real but slight: the imperfect is a fair rendering, since the causative has no perfect. Left as is. |
| af5846c5 | 00034 | minor: péh₂sm̥ taken as an s-aorist | **Reviewer error.** The gloss is PST.1SG of athematic *peh₂s-* (imperfect), so "I used to guard" is right. |
| c1daab15 | 00004 | minor: h₂én used as "there" | **Reviewer error.** pie-lex-h2en-2 *h₂én* means "there, yonder". |
| 8f774b4e | 00033 | minor: full-grade wéyḱeti | **Reviewer error.** This is the aorist subjunctive of root-aorist weykjt-2, so full grade is correct. |
| b4122050 | 00037 | minor: yéwgoh₂ taken as an indicative | **Reviewer error.** This is the short-vowel subjunctive of root-aorist yewgt-2 and is correct. |

## Second pass (all 40 records)

- **In-world violations: none.** Nothing modern appears. The only flagged lexemes are the project reconstructions
  pie-proj-moghus (*mógʰus* "boy"; Goth. *magus*, OIr. *mug*) and pie-proj-poxlHos (*pṓlHos* "foal"; Gk. πῶλος,
  Goth. *fula*). Both are inherited words reconstructed from cognates, not neologisms, and the record says
  `neologism: false`. They are listed here so the lead can decide whether "no coinages" covers them.
- **Turn coherence:** every turn answers the one before. Weak spots, all acceptable:
  - 00017: "What is his name?" is answered "Set him a famous name", which implies the dog has none.
  - 00002: the child says seven cattle; the elder says eight and points at the one by the stone. This is intended.
- **Verb senses vs glosses:**
  - Causatives are all used for transitive or causative meanings: Hyowdʰéye- "move (arms)" and "agitate";
    sodéye- "seat"; moréye- "kill"; ǵorh₂éye- "make old"; swopéye- "put to sleep"; woséye- "clothe".
    No causative is used for a plain verb.
  - *sokʷéye-* "say" (00027) follows Germanic *sagjan*; it is fine.
- **Wrong: 0.**
- **Minor (fear construction): 2, both fixed.**
  - **00011** `tóm dedwóyh₂e` "I am afraid of that one", and **00024** `n̥bʰróm dedwiyḗr? h₁ím ne dedwiyḗr` "Are they
    afraid of the rain? / They are not afraid of it".
  - The thing feared was put in the accusative. The house standard (tier3b-t3b-004 review, gap 2) is the ablative
    (Ved. *bhī-* + ABL). Greek δείδω + ACC makes the accusative defensible, which is why these count as minor.
- **Minor, not fixed:**
  - 00021: moḱs "quickly" rendered as "early" ("Why did you wake up early?"). The sense is stretched.
  - 00036: covered in the packet table above.

## Fixes (data/generation/plans/t039.jsonl)

| plan | change | new PIE |
|---|---|---|
| t039-0003 | `ghebhestis` INS: num DU → PL, and the English "with both hands" → "with the hands". The engine has no oblique dual cells (engine gap 1 below). The cow's anaphors: gender m → f. | h₁íh₂m̥ … h₁íh₂m̥ gʰbʰestíbʰis h₂ml̥ǵdʰí … h₁íh₂-ge méwdt |
| t039-0011 | thing feared: OBJ → ABL | **tósmōd** dedwóyh₂e |
| t039-0024 | thing feared: OBJ → ABL (2 clauses) | h₁íh₂es **n̥bʰrṓd** dedwiyḗr? **h₁ésmōd** ne dedwiyḗr |

I re-realized with `realize_plans.py data/generation/plans/t039.jsonl --batch t039 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`:
- 40/40 realized, 40/40 exact, reject rate 0.0.
- max_lexeme_uses 6, 0 duplicates, **gate PASS**.
- The 14 warnings are antecedent-heuristic and homophone notices. I checked each one and found nothing wrong.
- Only the 3 edited plans changed. The realizer is a deterministic engine pass, so the other 37 records are the same as in the second pass.

**Counts before and after the fixes** (real records, second pass): wrong 0 → 0; minor 5 → 2. The 5 minors before
the fixes were 00003, 00011, 00024, 00021 and 00036.

## Blind back-translation agreement (6 items)

| item | agreement |
|---|---|
| 0e1bc771 | full |
| 3dc4dc01 | full |
| 2a7a613b | near-full: I took the last turns "wéwke" as narrative rather than "Say:" |
| 604e7b75 | full on structure. I translated the 2sg literally ("you make the earth yield"), which is the planted error. |
| 874437a1 | partial: I missed tḱéyti "dwells" and h₁éwset "burned"; "You grasped it" was right |
| 3242cf10 | partial: I missed kʷíh₁ "how", wédni "on the water" and the arms clause; "afraid / do not tremble / I hold you / swim / learned" were right |

That is 3 full, 1 near-full and 2 partial. The partial misses come from rare lexemes, not from errors in the PIE.

## Engine and brief gaps (report only)

1. **No oblique dual cells, and the engine falls back to the plural silently.**
   - `Lexicon.cells('pie-lex-ghebhestis')` has only NOM/VOC/ACC.DU.
   - A plan asking for `num: DU` in the INS realized gʰbʰestíbʰis, glossed INS.PL, with no warning or rejection.
   - The engine should either decline the oblique dual (*-bʰih₁*/*-bʰyoh₁*, *-oh₁s*) or reject the slot. A silent
     change of number lets the English ("both hands") drift from the PIE.
2. **Verbs still have no case frame (recurring; t3b-004 gap 2).** Planners still put the thing feared in OBJ (ACC)
   with dedwóye. A `governs: ABL` on dedwoye, bʰeyh₂t and bʰebʰoyh₂e, or a line in planner-brief-v4, would stop
   this recurring.
3. **Brief:** the in-world brief should say whether `coined: "project"` reconstructions (mógʰus, pṓlHos) count as
   coinages.
