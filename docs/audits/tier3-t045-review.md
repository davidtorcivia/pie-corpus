# Tier 3 review: t045 (in-world dialogues: exchange, bargaining, gifts, bride-price, debts)

Reviewer: calibrated reviewer (claude-opus-5-5), brief `review-v1`, 2026-10-30/31.

## Procedure
- Packet: `scripts/make_review_packet.py t045 --n 20 --plants 5 --tier1 3` (28 items).
- Blind back-translation of 6 items (037da19b, 2fa7d4d4, 8673c8d8, 0939ebd4, 88975e91, 1d2dcc96) done first, with
  only the `pie` field printed: `docs/audits/packets/t045-blind-translations.jsonl`.
- Verdicts saved before opening corpus or plans: `docs/audits/packets/t045-verdicts.jsonl`,
  **sha256 6aba1a52ed0f6ba0b9258a7268e67a806e7642cb41423d7a19179682ef922354**.
- `resolve_review_items.py t045`, then `score_review.py t045`. data/audits/ was not opened.

## Calibration
| | |
|---|---|
| Plant recall | **5/5** (all caught, all named) |
| Tier 1 judged wrong | 0/3 |
| Real items wrong | **0/20** |
| Real items minor | 5/20 |

The five plants were: wédʰes 2sg for "I led" (8673c8d8), lubʰyómes 1pl with subject "kings" (0939ebd4), gʷíh₃woh₂
1sg for "a song lives" (f896f14c), déh₃tu 3sg imperative for "Give me" (077dd849), h₁énosmōd ḱr̥h₂nóybʰos singular
demonstrative with a plural noun (17215812).

## Blind back-translation
All six agree with the English in substance: the trade, the speakers' moves and the numbers. My blind reading
differed only where the English depends on context. In 2fa7d4d4, *méne wóǵʰos* is the owner's "My wagon!"; I had
glossed it flatly. In 0939ebd4 I could not identify *góleti* ("is cold"). In 88975e91 I read *gʰóstey* as a
greeting rather than the vocative, but -ey is the regular i-stem vocative.

## Packet minors (real items)
- t3-t045-00019 (037da19b): the English "he eats much grass" had no "much" in the PIE. **Fixed** in the English.
  I first flagged *sméyomes* "let us laugh" as indicative. That was my error: it is the short-vowel subjunctive of
  athematic smḗyti, so it is correct.
- t3-t045-00005 (88975e91): *dwóbʰih₁ moysṓys*. The numeral has a dual oblique but the noun falls back to the
  plural. **Fixed** (see the lead's new `_check_two_oblique` below).
- t3-t045-00003 (16ab2550): salt is nom. *sḗh₂l* (no -s) beside acc. *séh₂lm̥*, both masculine. This is an engine
  paradigm question, not a planning error. Report only.
- t3-t045-00025 (cc6684cd): *ǵʰéslom h₂éwibʰis*. "Thousand" is the indeclinable `closed:numerals/indeclinable/1000`,
  so it does not take the instrumental of price. This follows the engine's design (Vedic sahásra- declines).
  Report only.
- t3-t045-00032 (98118bd0): *woǵʰéyōh₂* is glossed "to cause to bring, transport". It was a causative used for the
  plain "I will bring". **Fixed** to wéǵʰeti (*wéǵʰōh₂*).

## Second pass: all 40 records
I read all 40 records against planner-brief-v4 and the in-world dialogue brief (top part). Every dialogue stays in
the world of herds, hearth and kin. Neither speaker is modern. There is no money, coin or market institution:
silver and gold are goods (00035 "What is silver? I do not know it"), and "assembly" is dʰh₁tléh₂. The turns answer
each other.

Points checked and found correct:
- Fearing takes the ablative: 00002 *h₁ésmōd dedwiyḗr*, 00039 *tósmōd bʰéyh₂m̥*.
- Instrumental kʷíh₁ is read correctly as "how" (00008, 00010 "How did he deceive you?", 00028) and as "for
  what" (00010, 00025, 00036).
- The planner wrote around missing words and the PIE still says what the English says:
  - "owe" = dʰl̥gʰéti, glossed "owe";
  - "lent cow" (00004): the PIE says "I drove you a cow … you owe me";
  - "repay later" (00034): *tód moy yéh₁ni h₁opéye*;
  - "worth/price" = wósn̥;
  - "wage" = misdʰós.
- Numerals agree: tísrn̥s/tisr̥bʰí/tisr̥sú are feminine with h₂ówis and ǵʰéyōm, kʷétesrn̥s with bʰoréh₂, and
  tríh₂ with neuter médesh₂.
- Enclitics are in second position.
- Athematic obliques are correct: h₃dóntn̥s, pódn̥s, gʷéwh₁, gʷéws, m̥lités, h₂l̥bʰités, h₂n̥réy.
- Causatives that are glossed with plain senses (wodʰéyeti "lead", wolh₁éyeti "choose", sokʷéyeti "say") are
  correct. The one glossed causative-only (woǵʰéyeti) was fixed.

Fixed in data/generation/plans/t045.jsonl:
1. **t045-0030 (wrong → fixed): agreement.** The adjective gʷérdus "heavy" has no feminine cells. It produced
   *h₂wĺ̥h₁neh₂ … gʷérdus* and *séh₂ gʷérdus* with a feminine subject, three times. I switched it to
   pie-lex-gwreh2us, which gives *gʷr̥h₂éwih₂*, as 00007 already uses.
2. **t045-0037 (pronoun tracking).** "She is gone", right after "His wife was angry", was rendered with masculine
   *só*. The referent is the cow (gʷṓws is masculine in the lexicon). I renamed the subject with the noun: *gʷṓws
   lelóykʷe*, "The cow is gone, and we sing the song."
3. **t045-0013, t045-0008 (×2), t045-0028: missing "?".** A `question` flag on the first clause of a
   multi-clause sentence did not reach the sentence end. Examples: "Do you want a white garment, or … a red one?"
   and "If he desires four sheep, what shall I say?". I put the flag on the closing clause as well.
4. **t045-0032**: woǵʰéyeti → wéǵʰeti (above).
5. **t045-0019**: dropped "much" from the English (above).
6. **Lead's note on `_check_two_oblique`.** I rephrased both clauses that had "two" in an oblique case, keeping
   PIE and English matched:
   - t045-0005: "My brother got it in trade; he gave two rams." → *bʰréh₂tēr moy tód kʷréyh₂t dwóh₁ moysóh₁ déh₃t*
     (the dual is now accusative);
   - t045-0006: "I will give you two lambs for five sheep." → *dwóh₁ toy h₂egʷnóh₁ pénkʷe h₂éwibʰis déh₃oh₂*.

Real wrong items: 0 before and 0 after in the packet sample. In the full batch, 1 wrong (t045-0030 agreement) and
about 8 minor findings were fixed at the source.

## Engine / brief findings (report only)
- **`question` flag placement.** The engine reads `question` from the sentence's last clause. Brief v4 says
  `question` means "its sentence ends with '?'" and planners set it on the sentence-initial clause. Either the
  engine should honor the flag on any clause of the sentence, or the brief should say "last clause". Four
  sentences in this batch were affected.
- **u-stem adjectives without `pos`** (e.g. pie-lex-gwerdus, a derivative) get no feminine -wih₂ cells, and the
  engine silently uses the masculine form with a feminine head. The checker should reject this, or the
  feminine should be built.
- *h₁ā́m* (AOR.1SG of h₁áyt, in 00040): this applies Stang's law to *-aym̥*. It is questionable; *h₁áym̥* is
  expected. Minor.
- gʷṓws is masculine in the lexicon, so cows are referred to as *só/tóm* while the English says "she". PIE gʷṓws
  was of common gender (Ved. gáuḥ, a cow, is feminine). A feminine option for "cow" would let the pronouns follow
  the referent. Minor.
- *sḗh₂l* nominative without -s (see above); ǵʰéslom is indeclinable (see above).

## Gate
After the fixes: re-realized with `realize_plans.py … --batch t045 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`. Result: 40/40 realized, reject_rate 0.0, all_exact, **gate PASS**. There are 18 warnings,
all antecedent-distance or say/drive homophone checks, and I verified each as correct. The release approval is
left to the lead.
