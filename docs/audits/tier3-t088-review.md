# Tier 3 batch t088 review (review-v1, calibrated)

Batch t088 has 40 texts in the Horrors wave (t085–t088), on the strands *death unprotected* and *the gods' cruelty*:
20 two-speaker dialogues, 5 laments, 2 prayers, 1 charm, 6 myths and 6 tales.
Prompt `tier3-dialogue-inworld-v1`, model `claude-opus-5-5`.

## Procedure

- Packet: `scripts/make_review_packet.py t088 --n 20 --plants 5 --tier1 3`, giving 28 items (20 real, 5 planted, 3 Tier 1).
- Blind back-translation came first: 6 items, translated from the `pie` field alone
  (`docs/audits/packets/t088-blind-translations.jsonl`).
- Verdicts were saved before anything under corpus/ or the plans was opened.
  File: `docs/audits/packets/t088-verdicts.jsonl`, sha256 `cb1482a94fef4ae866bfa3dae14b0aedcc1fc521651ceb3f989a89a46a23f259`.
- Then `resolve_review_items.py` and `score_review.py` were run. data/audits/ was not read.
- Second pass: all 40 records, read against planner-brief-v4, the in-world dialogue brief and its "Horrors" section.
  Every lexeme the batch uses was checked against its full gloss and coinage flag.

## Calibration

| | |
|---|---|
| Plant recall | **5/5** (all caught, all named) |
| Tier 1 judged wrong | 0/3 |
| Real items wrong | **0/20** |
| Real items minor | 3/20 as judged; 2/20 after 00031 was withdrawn (see below) |

The five plants, all marked wrong, in the packet's spelling:

- fd104fdd: `sréwmn̥-kʷe méǵh₂ h₁sént`. This is 3pl; the singular stream needs h₁ést.
- 9333a206: `péh₂urōy h₃ésth₁h₂`. This is DAT.SG; the sentence needs neuter ACC.PL péh₂ureh₂.
- a6b15ad1: `nu toy dʰúgh₂ter … sténeti`. This is the VOC; the subject needs NOM dʰugh₂tḗr.
- 54a1b01d: `gʰrómoh₁ kl̥h₂tóm`. This is the AOR/IMP 2DU of kelh₂; "Perkʷunos struck it" needs kélh₂t.
- 2c9adcde: `solh₂wṓs h₃rēǵsú trésont`. This is LOC.PL; fearing takes the ablative of one king, h₃rēǵés.

Three of the five plants sit in short clauses, as the brief warns.

## Blind back-translation

All 6 items (139effcb, 54a1b01d, 9c3f5c77, fe0651dc, 2c9adcde, 6208a269) agree in substance with the English.
- In 2c9adcde I misread two verbs: h₁ért as "spoke" (it is "came") and kh₂nét as "dug" (it is "chanted").
- Three forms were uncertain and were cleared by the lexicon: tl̥h₂tóy is the ford, not "bank"; pérwr̥ is the ford;
  h₁yód is "if" rather than "because".
- The blind pass had already flagged both plants it met (kl̥h₂tóm, h₃rēǵsú) as suspect.

## Real items: minors (packet)

- t3-t088-00027 (9c3f5c77), the prayer over the bull: the enclitic `nos` falls inside the two-word address
  *pérkʷune nos déywe*.
- t3-t088-00026 (390cae73), the prayer at the grave: the enclitic `toy` falls inside *méh₂ter toy dʰéǵʰom*.
  Also, *tébʰye h₁én* "in you" uses the dative pronoun with h₁én, because the closed class has no 2sg locative.
- t3-t088-00031 (fe0651dc), the god under the ford: the aorist sléh₂gʷt stands for the habitual "he takes".
  sleh₂gʷt-2 has no present stem, so this is a defensible gnomic aorist. Withdrawn as a real fault; no fix.

## Second pass: all 40 records

**No wrong items were found.**

Checks run on every record:
- Person, number and case of every word in its own sentence.
- Speakers alternate correctly, the user speaks first, and each turn answers the one before.
- Pronouns track their referents.
- Verbs of fearing take the ablative everywhere: déh₂nus, h₁ésmōd, pérkʷunōd, ḱéstrōd, deywṓd, h₃rēǵés.
- Predicate adjectives agree with their nouns: ḱolHtéh₂ with the hearth (h₂éHsh₂), somHéh₂ with the daughter,
  dʰubʰróm with the stream.
- Causatives fit their glosses: moréyeti "kill", noḱéyeti "cause death", stoh₂éyeti "cause to stand",
  Hyowdʰéyeti "cause to move", h₁opéyeti "give", woséyeti "clothe".
- The verbs for 'take', 'drown' and 'bury' follow the brief: sléh₂gʷt for 'take'; h₃élh₁t, h₁r̥h₁pyéti and séngʷt
  for drowning; logʰéyeti dʰǵʰémi and h₂ḱmn̥sú Hn̥dʰí for burial; kéwdʰeti where the English says "hide".
- No word is coined. The only project words are gʷʰermós, h₂énHos, kónHis ("ashes", in kénHēy) and mógʰus.

**Fixed at the source (minor).** In t3-t088-00015 (plan t088-0015), *snóygʷʰos stóygʰom ḱélet h₃sléydʰt-kʷe* read as
"the snow … went astray", because the null subject carried over from the snow.
- Fix: added SUBJ anaphoric_i (m) to the second clause.
- New text: *snóygʷʰos stóygʰom ḱélet h₁éy-kʷe h₃sléydʰt*.

**Flagged, not fixed (minor, engine).** In t3-t088-00024 the lament opens *ph₂trés-ge moy te dʰéh₁mn̥* "House of my
father". The realizer puts the genitive first and then hangs the enclitics -ge, moy and te inside the address.
- This record, 00026 and 00027 show the same rule at work: Wackernagel placement after the first word, with the VOC
  always fronted. That rule splits multi-word vocative phrases.
- Plan reordering cannot avoid it: the realizer refronts the VOC.
- A stressed pronoun would add a syllable and break the exact 8/11 meter.
- Reported for the lead; no plan fix.

**Considered and accepted:**
- Gnomic aorists in the myths: l̥h₁tā́m (00032), h₁épt (00033).
- wiḱpótis for "master of the house": its gloss includes "master of a household".
- Root-aorist 1sg ǵʰḗm (00024): Stang's law, consistent with dyḗm.
- The h₂éwisu ablaut (00005).
- The 26 realizer WARN lines: every one was checked and each realizes the intended person or referent.

## Horrors limits

No violations.
- Nothing modern and no coinages.
- No sexual violence.
- No gore for its own sake. The hardest lines are told plainly and briefly, in the epic manner, with no added
  description: birds at the unburied brother's eyes (00023), the king's daughter killed at the altar (00030), and
  "they found only blood" (00036).
- The sacrifices that cost a life are told, not endorsed or condemned: the brother chosen for the water god (00008),
  the twin myth (00029), the king's daughter (00030), the funeral horse (00040).
- The gods' silence is stated as fact: "The gods saw it, and they were silent" (00005); "the gods were silent"
  (00034).

## Tone

The batch lands its tone: grief, fear and endurance, with the facts said plainly.
- The laments and the prayer at the grave scan exactly (53/53 lines).
- The dialogues read as people of that world talking about their dead.

## Gate (after the fix)

Re-realized with `scripts/realize_plans.py data/generation/plans/t088.jsonl --batch t088 --model claude-opus-5-5
--prompt-id tier3-dialogue-inworld-v1`. **Gate: PASS**.

| Check | Result |
|---|---|
| Realized | 40/40 |
| exact_pass | 40 |
| Reject rate | 0.0 |
| max_lexeme_uses | 8 (cap 8) |
| meter_exact | 53/53 |
| Duplicates | 0 |
| Roots per sentence | 4.375 |

## Counts

| | Before | After |
|---|---|---|
| Real wrong (packet) | 0/20 | 0/20 |
| Real minor (packet) | 3/20 | 2/20: 00031 withdrawn as a gnomic aorist; 00026 and 00027 remain as an engine report, not fixable in the plan |
| Second pass wrong | 0 | 0 |
| Second pass minor | 2 (00015, 00024) | 1: 00015 fixed at the source; 00024 remains as an engine report |

After the re-realization, the record text of only t3-t088-00015 changed; the other 39 records have the same PIE as before.
The release metadata is still pending; this review does not approve the batch.

## Engine and brief reports (for the lead)

1. **Enclitics inside multi-word addresses.** The Wackernagel enclitic lands inside a multi-word VOC phrase:
   - pérkʷune nos déywe (00027)
   - méh₂ter toy dʰéǵʰom (00026)
   - ph₂trés-ge moy te dʰéh₁mn̥ (00024)

   A rule is needed that places enclitics after the whole address, or treats the address as outside the clause.
2. **No 2sg locative pronoun.** The closed class has none, so "in you" comes out as tébʰye h₁én (00026).
