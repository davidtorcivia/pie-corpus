# Tier 3 review: t073 (elders and old age, 40 in-world dialogues)

Reviewer brief `review-v1` (docs/generation/reviewer-brief.md). Reviewer: claude-opus-5-5, 2026-10-31.
Release approval not set (lead's decision).

## Procedure

1. Packet: `scripts/make_review_packet.py t073 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items from the `pie` field only:
   `docs/audits/packets/t073-blind-translations.jsonl`.
3. Verdicts: `docs/audits/packets/t073-verdicts.jsonl`, saved before corpus/ or the plans were opened.
   **sha256 `cf6e1d1014b4519d85d0ae96d721d8e295bf0b38e94807112f93e179c87399b8`**.
4. `resolve_review_items.py t073`, then `score_review.py t073`.
5. Second pass: all 40 records read in full against planner-brief-v4 and planner-brief-dialogue-inworld (top part).

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **3/5 (0.60)**, all 3 caught plants named correctly |
| Tier 1 judged wrong | 0/3 |
| real items judged wrong | 1/20 (0.05; upper 0.083) |
| real items judged minor | 0/20 |

Plants caught: 65499b9b (h₃reǵtéh₂ for acc. h₃reǵtóm), 9c9cef0b (sg. h₂ṓws with a dual adjective),
37ad57f3 (dat./abl. pl. pótn̥yeh₂bʰos as the vocative "Wife").

Plants missed. I found these when I read the records in the second pass, after scoring. I did not diff the packet:
- 94767244: "mówdoh₁ HréwdHsi" (2sg) where the English says "I weep for joy" (the record has HréwdHmi). I read it
  as the answer and missed the person.
- 317aca37: "kʷóti dinṓys" (instr. pl.) where the answer has acc. pl. dinóns. I took it for an instrumental of time.
  It also got past the blind translation.

So recall is below the release rule's 4/5. Both misses were person/case swaps inside short question-answer pairs.
The review should check each answer against its question's verb person and case.

## Real items: wrong before and after

- **Before (as judged in the packet): 1 wrong**, 548b3a43 = t3-t073-00007, "túH moy ḱéyweh₂" (I read it as a feminine
  addressed to the father-in-law). **This was a false positive.** The record's speakers show that the
  father-in-law (user) says "You are dear to me" to his daughter-in-law, so the feminine ḱéyweh₂ is correct. No
  fix needed. The packet has no speaker labels, so I could not see this from the packet alone.
- **True real wrong: 0/20 before and 0/20 after.**

## Second pass (all 40 records)

All checks were clean except the items below. In-world and in character: no modern items, no coinages, and the
healing texts use roots, flowers, leaves, bark, honey and water. Both speakers belong to the PIE world in every
dialogue. Every turn answers the one before it. Speakers and per-sentence English are correct. Memories are in
the past: PST/AOR in 0001, 0002, 0007, 0012, 0013, 0021, 0024, 0027, 0029, 0035, 0037. Every verb of fearing takes
the ablative: mórōd (0015), wĺ̥kʷōd (0033), deywóybʰos with tres- (0027), ph₂wéns (0037). Where the planner wrote
around a missing word, the PIE says what the English says: herbs are roots and flowers (0005, 0039), grey hair is
"head has become grey" (0028), ancestors are "my fathers" (0004, 0040), tears are the verb "weep" (0011, 0027), and
fever is "is warm" / "the heat" (0039). Athematic obliques are right: bʰr̥h₁wéns, wédni, dréws, ph₂wéns, ḱr̥h₂séni,
gʷéwbʰos (the engine's paradigm), ǵʰiméni (pie-lex-gjheymn loc.). Enclitics sit in Wackernagel position.

I checked full glosses (`Lexicon.meaning`) before judging any sense; none was stretched:
- kʷékʷlos includes "wagon"; h₃órbʰos "heir"; nes- "return home unharmed"; ḱubʰrós "beautiful";
  tewtéh₂ "people"; kóryos "troops".
- somHós "alone"; h₂éti "again"; éti "also, too"; stĺ̥neh₂ "gravestone"; ses- "sleep"; pérun- "mountain".
- men- "wait (for)"; h₁ewk- "learn"; wen- "overpower, win" ("I beat them", 0021); népōts "nephew" (0040).
- One sense is stretched slightly: woyḱós "villager" for "neighbor" (0034). It is acceptable in a settlement setting and was not changed.

### Minor (fixed)
- **t073-0017** (t3-t073-00017), "They heal; my mother showed them to me". The pro-dropped verb had a 3pl ending
  (mḗdonti) for the neuter-plural "leaves", while the question used the inherited singular verb (ḱéh₂ péth₂leh₂
  mḗdeti). Plan fix: clause 5 verb `num` PL → SG. It now reads "mḗdeti méh₂tēr moy méǵʰye h₁íh₂ déyḱet", so the
  answer repeats the question's form (v4 rules 13 and 17).

### Minor (engine gap, report only)
- **t073-0006**: "dwóh₁-kʷe moy bʰréh₂terh₁e ne nésonto". A dual subject takes a 3pl middle verb because the
  engine's middle paradigm has no 3du cell (nes- is deponent). Lead: add the middle 3du (cf. Ved. -āte, Gk
  -σθον) or document the fallback.

### Noted, left as is
- 0030: the old mother says "I will see your grandson" to her daughter. This works if the daughter is herself a
  grandmother, and the PIE matches the English.
- 0009: "swóm h₂óyu" is literally "his own lifetime" for "all his life". Acceptable.
- 0033: gnomic "bʰugént" (AOR). The flee lexeme has no present, so v4 rule 8 allows it.

## Blind back-translation agreement

All six agree with the English in substance (1f72ec20, 99b5aec5, 65499b9b, 548b3a43, 77162374, 317aca37).
- 1f72ec20: I didn't recognise n̥sdʰí (nes- "come home unharmed").
- 548b3a43: I guessed "frost on the roof" for "ice on the path" (stóygʰos / stéygʰom).
- 65499b9b: the planted h₃reǵtéh₂ left the sense unclear.
- 317aca37: the planted dinṓys was not noticed.

## Re-realization and gate

`realize_plans.py data/generation/plans/t073.jsonl --batch t073 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`: 40/40 realized, reject_rate 0.0, max_lexeme_uses 7 (cap 7), 311 lexemes,
181 roots. **Gate PASS.** The 8 warnings are antecedent heuristics for abstract "that/this" objects, plus a
homograph note on h₂éǵomes "we drive" (0040). I checked all 8 and none is an error.

## Engine findings
0. `accent_defect_tokens` is 1 in the batch report. I could not find the token from the record fields; the lead should look up which one it is.
1. There is no middle 3du (see 0006).
2. The packet has no speaker labels, so gender agreement with the addressee cannot be checked from it (the cause
   of my one false positive). Suggestion: add a `speaker` prefix per sentence to the packet's `english`.

## Second review (seed 2)

Reviewer: claude-opus-5-5, 2026-10-31. Brief `review-v1` followed. This review used a new packet, so the first
review's verdicts above do not count toward release. Release approval not set.

### Procedure
1. Packet: `make_review_packet.py t073 --n 20 --plants 5 --tier1 3 --seed 2` (28 items: 20 real, 5 planted,
   3 Tier 1). It overwrote the first packet file.
2. Blind back-translation of 6 items from the `pie` field only (f3c2cafa, 425aae04, b206d8d9, 7baf132d, 9c646ab5,
   1f001f6c): `docs/audits/packets/t073-blind-translations.jsonl` (overwritten).
3. Every token was checked against `Lexicon.cells()` through a reverse form index, and doubtful senses against
   full glosses. Verdicts were saved before I opened corpus/, the plans or the first review:
   `docs/audits/packets/t073-verdicts.jsonl`, **sha256 `7c4b58c9765a37ed3ed939684eceb583b3d9bd15a20fd280b83e86d08935c9a5`**.
4. `resolve_review_items.py t073`, then `score_review.py t073`.
5. Second pass: all 40 records read in full against planner-brief-v4 and the in-world dialogue brief.

### Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5 (1.00)**, all 5 named correctly |
| Tier 1 judged wrong | 0/3 |
| real items judged wrong | 0/20 |
| real items judged minor | 1/20 (withdrawn, below) |

Plants caught (all from person, number or case checks):
- f6bb3697: ǵr̥h₂n̥tyéh₂su (fem. loc. pl. of ǵérh₂onts) used to address "Old man"; the voc. ǵérh₂ont is needed.
- e56ebcbe: "the oxen do not obey me" with ḱlowséyesi (2sg) where the 3pl subject gʷówes needs ḱlowséyonti.
- 118d03be: "I will see your grandson" with widḗtes (sbjv. 2du/3du) where a 1sg is needed.
- 8c34c18b: "for many days I looked at the road" with spéḱyes (2sg) where 1sg spéḱyom is needed.
- d5f0f40e: "many names are in my head" with ḱr̥h₂snéy (dat.) where the loc. ḱr̥h₂séni is needed.

### Real items: wrong before and after
- **Wrong: 0/20 before and 0/20 after.** No plan edits were needed.
- Minor, **withdrawn**: 201839ed = t3-t073-00033, gnomic "wolves flee from dogs" with aorist bʰugént. pie-lex-bhewgt-3
  has no present cells, so v4 rule 8 (gnomic aorist) applies. The first review reached the same conclusion.

### Second pass (all 40 records)
The batch is clean, and I agree with the first review's account of it. Every record is in-world, with no modern
items and no coinages; both speakers are people of the household world; every turn answers the one before it. The
per-sentence English and the speaker labels match the PIE. Pronoun and adjective genders follow the speakers
(ḱéyweh₂ 0007, ǵr̥h₂éntih₂ 0036, ḱásneh₂ 0036, h₁súmenes f. 0039). Memories are in the past (PST/AOR), and the
narrative PST verbs I checked (gʷʰen- 'kill', sekʷ- 'follow') have no aorist. Fearing takes the ablative everywhere
(mórōd, wĺ̥kʷōd, ph₂wéns, deywóybʰos with tres-). Athematic obliques are right (bʰr̥h₁wéns, wédni, dréws, ph₂wéns,
ḱr̥h₂séni, dʰwr̥sú, pérunbʰos), and enclitics are in second position. In the short question-and-answer pairs, every
answer has the person, number and case its question needs. Senses I checked against the full glosses, all of them
within the gloss: h₁opéye- 'give', wenH- 'come to love', leh₁- 'let go', wreg- 'hunt', steygʰ- 'walk', stunéd-
'hit', ḱeHs- 'teach', h₂én 'there', pró 'before', bʰoydʰéh₂ 'pledge', ǵénh₁trih₂ 'mother'. In 0031, téḱneh₂ …
h₁éseti and h₁íh₂ … wikḗti are neuter plurals with singular verbs, which is correct PIE.

The in-memory realization of the current plans equals corpus/tier3/t073.jsonl for all 40 records (check_plan finds no errors), so
there was nothing to re-realize. **Gate: PASS** (data/generation/batches/t073.json: 40/40 realized, reject_rate 0.0,
max_lexeme_uses 7 of 7, all_exact).

### Engine findings (report only)
1. The first review's `accent_defect_tokens` = 1 is **moḱs** 'quickly' in t3-t073-00003 ("swérgʰos te moḱs
   likʷyéh₁t"). The adverb comes out with no accent, so its headword or its spec needs one. (The 9
   `accent_representation_tokens` are the frozen voc. ph₂ter.)
2. There is still no middle 3du (0006 "dwóh₁ … bʰréh₂terh₁e ne nésonto"); see the first review.
3. In 0008 ("h₁égʷʰis wiHrósyo-kʷe spélom") the gen. sg. h₁égʷʰis is the engine's first cell for pie-lex-h1ogwhis
   (an acrostatic i-stem: nom. h₁ógʷʰis, gen. h₁égʷʰis or h₁égʷʰeys), so the record is correct by the paradigm. But
   the first choice is the form that differs from the nominative only in its root vowel. The lead might put
   h₁égʷʰeys first. Paradigm question only; no change to the counts or the gate.

### Blind back-translation agreement
All six agree with the English in substance. My differences:
- b206d8d9: I read ǵénh₁tri as "knee" and the line as "does your knee hurt?". It is the voc. of ǵénh₁trih₂ 'mother'.
- b206d8d9: I read diwés as "by day". It is the abl. "from the sky".
- 9c646ab5: I read ǵŕ̥h₂enti as a dative. It is the fem. voc. "Old woman".
- 1f001f6c: I read woyḱṓy as "house". It is "villager" (the English says "neighbor").
- 1f001f6c: I left the turns of the debt exchange unclear.
- 425aae04 and 7baf132d: no differences.
