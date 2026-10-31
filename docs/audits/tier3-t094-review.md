# Tier 3 batch t094 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on dreams, omens and signs (`tier3-dialogue-inworld-v1`).
Reviewer: calibrated agent review following docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t094 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items, done from the `pie` field only before any English was printed:
   `docs/audits/packets/t094-blind-translations.jsonl`.
3. Verdicts written and saved before corpus/ or the plans were opened:
   `docs/audits/packets/t094-verdicts.jsonl`, sha256
   `3a64ff58816263529a348c831b969075e446425f78a95c8bc098c4cbb4f58c56`.
4. `resolve_review_items.py t094`, then `score_review.py t094`.
5. Second pass: all 40 records read in full against planner-brief-v4 and the in-world dialogue brief.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong (as scored) | 1/20 |
| real items judged minor | 4/20 |

Plants caught (packet spelling): swépnōs (NOM.PL for LOC "in sleep"), ǵʰóysoh₁ (VOC.DU for ACC.PL "the spears"),
gʰóstih₁ (DU for VOC.SG "guest"), h₂éndʰesih₁ (DU for ACC.SG "a flower"), ǵʰh₂n̥sṓm (GEN.PL for the NOM.PL subject
"the geese").

**Withdrawn wrong.** The one real item scored wrong was b5e829a4 (t3-t094-00032), where I read h₁éy in
"h₁éy h₃reǵtós dyḗm-kʷe stéygʰeti" as IMP.2SG "go!". It is the anaphoric masc. NOM.SG *h₁éy* "he/it" (Ringe 2017
p. 56; data/morph/closed_class.json), referring to the smoke (dʰuh₂mós, m.), so "It is straight, and it climbs to the
sky" is correct. My form search checked lexeme cells only and missed the closed class. **Real wrong after
review: 0/20.**

## Real items: minor findings and fixes

| packet item | record | finding | action |
|---|---|---|---|
| 99d93131 | t3-t094-00003 | "Will you sit with me in the night?": the PIE has no word for "in the night" | English changed to "Will you sit with me?" |
| 906057e5 | t3-t094-00007 | "shall we not die?" was `neg: true` + 1PL SBJV, so it came out as mē méromes "let us not die" (v4 rule 11) | `neg: "ne"`, now ne méromes |
| 8b7a83cf | t3-t094-00017 | the two calves were "them" with anaphoric_i PL (h₁íns), which has no dual | OBJ is now demonstrative_so DU (tóh₁), as v4 §Pronouns says; "their" is demonstrative_so DU (plural fallback tóysōm); the IO slot "for the calves" is now DU (the engine falls back to the plural wetsóybʰos, as expected) |
| 7939ac26 | t3-t094-00029 | "it returned unharmed": no slot for "unharmed". The gnomic aorist mért for "dies" stands: mert has no present (v4 rule 8) | English changed to "it returned." |

## Second pass (all 40 records)

No modern or coined content. Every dialogue has two in-world speakers, the user speaks first, and each sentence has
its own English. Turns answer each other.

- **Tense.** Dreams are told in the past (AOR for events, PST for background: "was leading", "was weeping"), with PRF
  for states (dedórḱh₂e "I have seen", bʰebʰóyh₂h₂e "I am afraid"). What may come is SBJV ("he will live", "shall I
  go?") or OPT for wishes ("may the gods guard you").
- **Left and right.** sewyós + ǵʰéstos "(on/from) the left hand" (LOC sewyóy ǵʰóstoy, ABL sewyṓd ǵʰóstōd) and the
  adverb déḱs "on the right" are used consistently for bad and good omens.
- **Fearing.** Fearing takes the ablative everywhere: wĺ̥kʷōd bʰéyh₂s, ḱasṓd dedwóyth₂e, h₁ésyo dn̥ǵʰuh₂és
  bʰebʰóyh₂h₂e, h₁sn̥tés ne bʰebʰóyh₂h₂e (athematic ABL in -és), h₁ésmōd mē tréses.
- **Verb senses, checked against the full glosses.** "Show / mean" is déyḱeti 'show, point out'; "give a sign" is
  séh₂gyeti 'seek out, give a sign'. h₃roǵéyeti 'make straight' ("keep the boat straight") is a true causative, used
  causatively. m̥néh₁yeti is 'stay'; h₂éyeri 'early, in the morning' stands for "tomorrow", which is the lexq idiom.
- **Predicate adjectives with a dropped subject agree in gender:** kéh₂ileh₂ (to a mistress), ḱubʰréh₂ (Dawn),
  lewkóm (the knife, n.), ǵr̥h₂éntih₂ (grandmother).
- **Short answers take the right case.** "Toward the home of the old shepherd" is ACC ḱóymom, answering "toward which
  home?".
- **Rule 13.** t3-t094-00006 "He said nothing" answered wéwket with sékʷt. It now repeats wéwket (a nit, fixed at
  the source).

Remaining WARNs (10), each checked and harmless:
- "Is that true?" (0002) points back to the previous turn.
- Six 3rd-person verbs next to a vocative have a 3rd-person subject in context: the wolf (0003), the dead mother
  (0019), the mortal (0025), the sick son (0026) and the dog (0036). The other is impersonal "it thunders" (0016).
- Three "verb-only clause after a PL subject" warnings are a 3sg eagle (0011), a 3sg wolf (0021) and an impersonal
  "thunders" (0025).

## Blind back-translation agreement

All six items were translated before any English was seen. Agreement was substantive on 4 of 6 (99d93131 and
906057e5 in full; 937a206e and 7a77ae17 apart from single words). Where the translation diverged:

| item | what the blind translation got wrong |
|---|---|
| 369bda24 | missed trḗm 'I trembled' and gólonti 'they are cold' |
| a03b17f2 | read ḱóm h₂stérm̥ as "with a star" (it is deictic "this star"); the last clause gʷéHyōmes 'let us sing' was taken as "go/live" |
| 937a206e | ǵʰóysoh₁ read as a dual: this is the plant |
| 7a77ae17 | m̥néh₁yeti read as 'remind' instead of 'stay' |

None of these divergences points to an error in the PIE.

## Engine or brief notes (report only)

- The realizer's referent warning ("demonstrative_so OBJ m DU matches no referent") fires when the antecedent is a
  dual referred to by a plural-fallback oblique or by a dual given only through a numeral. It is a false positive
  for dual referents, which the brief tells planners to use. Low priority.
- No engine gaps were found in the forms.

## Result

- Re-realized with `realize_plans.py data/generation/plans/t094.jsonl --batch t094 --model claude-opus-5-5
  --prompt-id tier3-dialogue-inworld-v1`: 40/40 realized, 0 rejects, max lexeme uses 7. **Gate: PASS.**
- Release rule: recall 5/5 (needs ≥ 4/5), real wrong after fixes 0/20 (needs ≤ 2/20), gate PASS. All three
  conditions hold; the approval decision is the lead's.
- Plans backup before the fixes: scratchpad `t094-plans-before-review.jsonl`. Nothing is committed.
