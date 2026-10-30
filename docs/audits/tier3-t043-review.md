# Tier 3 batch t043 review (review-v1, 2026-10-30)

Batch: 40 texts (proverbs, wisdom sayings, an elder's advice), planner prompt `tier3-planner-v4`, model
`claude-opus-5-5`. Reviewer: Claude Opus 5.5 (calibrated reviewer, following docs/generation/reviewer-brief.md).

## Procedure

1. Packet: `make_review_packet.py t043 --n 20 --plants 5 --tier1 3` → 28 items (20 real, 5 planted, 3 Tier 1).
   data/audits/ was not opened.
2. Blind back-translation of 6 items, done from the `pie` field alone before any English was printed:
   `docs/audits/packets/t043-blind-translations.jsonl`.
3. Verdicts written before corpus/ or plans were opened: `docs/audits/packets/t043-verdicts.jsonl`,
   sha256 `8178350f36aefd5789e29fe060fc00c0f9abd94c59252f63457c12e7b104ae83`.
4. `resolve_review_items.py t043`, then `score_review.py t043`.
5. Second pass: all 40 records and plans read in full against planner-brief-v4.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (5 caught, 5 named) |
| Tier 1 judged wrong | 0/3 |
| real items wrong | **0/20** |
| real items minor | 2/20 |

Plants caught (all case or number errors): ins. pl. h₁sn̥tyṓys for nom. sg. 'true man'; h₁usuyéh₂bʰos for
h₁wésus 'the good man'; ins. wiHróh₁ for gen. 'of a man'; ins. pl. pl̥h₁úbʰis for acc. pl. 'many (winters)';
neut. pl. ménesh₂ for sg. 'the mind'.

## Blind back-translation

4/6 agree with the English. The other 2 disagreements were my own misreadings, not faults in the corpus:
- I read stéh₂yeti as 'stands'. The lexicon gloss is 'steal' (*(s)teh₂-, Hitt. tāye-), which is what the English says.
- I took ǵérh₂ont as the subject ('who is a dear old man?'). It is a vocative ('Old man, who is a friend?').
- 8fb8d5aa was unreadable, and it turned out to be a plant.

So the blind pass found no faults in the real items.

## Real items flagged in the packet (minor)

- **t3-t043-00034** (0e8fc0b8): "He who deceives a guest deceives the gods" uses the aorist dʰréwgʰt, though the
  present dʰrugʰyéti exists (a separate lexeme).
- **t3-t043-00005** (1e1fdffd): "Cattle die … the mortal dies" uses the aorist m̥rént/mért, though the deponent
  present mr̥yétor exists.

Both are allowed by v4 §8, which says an aorist-only lexeme takes the gnomic aorist in a proverb. I left both
unchanged:
- mért → mr̥yétor would lower attested_in from 14 to 3, against v4 §15.
- I tried dʰréwgʰt → dʰrugʰyéti (00034 ×2, 00040). It pushed dʰrugʰyéti to 9 uses, so the
  `max_lexeme_uses<=6` gate failed, and I reverted it.

These two stay minor and are stylistic only.

## Second pass (all 40 records)

- **Modern or coined words:** none. mógʰus 'young man' (00008, 00017, 00027) is `pie-proj-moghus`, a sanctioned
  project reconstruction (PLAN.md "Project reconstructions": Gmc. *maguz, Celtic). It is in the default lexq pool
  and carries `coined: "project"`. It is not a neologism.
- **Tense:**
  - Proverbs use the present, the perfect for states (dedórḱe 'sees', wóyde 'knows', bʰebʰóyh₂e 'is afraid',
    stestóh₂e 'stands'), nominal sentences, or the gnomic aorist of aorist-only verbs (néḱt, térh₃t, h₃sléydʰt,
    yéwgt, wélh₁t, séngʷt, h₁áyto).
  - The narrative past appears only in the framed stories (00023, 00028, 00038), where it belongs.
  - **Fixed:** 00028 (plan t043-0028). The wise man's general claim "The truth overpowers them" used the aorist
    wént (attested_in 0). It is now the present séǵʰeti 'overpower' (attested_in 2): *h₁sónt h₁íns séǵʰeti.*
  - I left wélh₁t 'chooses' (00011) as it is. The alternative, wolh₁éyeti, has the o-grade + -éye- causative or
    iterative shape the brief warns about, and lower attestation.
- **Meaning:** every proverb says what its English says.
- **Pronouns:**
  - h₁ésyo 'his' tracks the wise or bad man (00002), the king (00018) and the wolf (00038).
  - tóm … h₁yós h₁ím (00003) is right: 'him who carries it'.
  - Reflexive swós is used with a subject antecedent (00017, 00021).
  - h₁íd and h₁íh₂ agree with neuter truth or fame and with feminine tongue.
  - The engine warns on 00028 that the masc. pl. h₁íns has no matching referent. Its antecedents are mixed
    (mead n., king m., woman f.), so the masculine plural is the normal resolution: OK.
- **Verb senses:**
  - The causative gʰroméyeti 'anger (someone)' is used transitively (00019), which is right.
  - The plain verb gʰrémeti 'rage' is used intransitively (00039), also right.
  - The verb of fearing takes the ablative: bʰéh₂esos bʰebʰóyh₂e 'fears the light' (00001).
  - The engine's one-letter warnings h₂éǵt 'said' / h₂éǵet 'drove' were checked (00023, 00028, 00038). Each
    matches its English.
- **lexq-found words**, checked against their glosses: wikéti 'fight', séngʷt 'fall, sink', ḱréddʰeh₁ti 'trust'
  (+dat.), sokʷéyeti 'say', tḱéyti 'dwell', winédti 'find', tl̥néh₂ti 'lift', kapyéti 'grasp', misdʰós 'reward',
  ǵʰoysós 'spear', somHós 'same', h₂ew 'again', Hn̥dʰí 'under', dʰéh₁lom 'deed', wisós 'poison'. All are used in
  their glossed sense; h₂ew 'again' (00004) is slightly stretched.

## Fix and re-realization

- **Plan edit:** data/generation/plans/t043.jsonl, t043-0028, clause 6: `pie-lex-went` AOR → `pie-lex-segjheti`
  PRS IND ACT.
- **Command:** `realize_plans.py data/generation/plans/t043.jsonl --batch t043 --model claude-opus-5-5 --prompt-id tier3-planner-v4`.
- **Result:** 40/40 realized, all exact, reject_rate 0.0, max_lexeme_uses 6, 4 warnings (reviewed above).
  **gate: PASS.**
- **Determinism:** I compared the corpus before and after the re-run. Only t3-t043-00028 changed.

## Counts

| | wrong | minor |
|---|---|---|
| real packet items, before fixes | 0/20 | 2/20 |
| real packet items, after fixes | 0/20 | 2/20 (v4-compliant gnomic aorists, kept) |
| second pass, all 40 | 0 | 1 fixed (00028), plus h₂ew 'again' stretched (00004) |

**Violations:**
- No coined, modern, case, agreement or pronoun errors in the real records.
- One tense-choice issue, now fixed (00028).

**Engine gaps:** none.

**Brief observation:** the lead may want to look at how v4 §8 (gnomic aorist for aorist-only lexemes) interacts
with §15 (prefer higher attested_in). Together they let an aorist-only lexeme beat a present-stem synonym in
proverbs: mért beats mr̥yétor, dʰréwgʰt beats dʰrugʰyéti. With the diversity cap, the present cannot always be used.

The release approval is not set (lead's decision).
