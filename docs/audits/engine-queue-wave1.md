# Engine and brief queue from the Tier 3 wave-1 reviews (2026-10-28)

These are fixed centrally after wave 1, before wave 2 starts. Each item names the review that found it.

- **PRF 2du/3du cells missing**: a dual request silently becomes plural, with no warning or reject (t024 00010; t023 66dc51f8). Either reject the plan or mark the token, as the existing dual-fallback flag does.
- **Middle 2sg secondary ending**: the engine gives *-th₂e*; the handbooks give \*-th₂es (Skt -thās) (t024). Check against Fortson and Ringe.
- **Per-lexeme cap too tight** at about 700 tokens per batch (cap 6). It forces unnatural substitutions (t029: pigs and "the herd" standing in for cattle) and short texts (16–19 words). Waiting on the t029 reviewer's verdict.
- **Conversation gaps**: question words, names, greetings (agent in progress); "here" (project reconstructions / deictic_ki).
- **Slice keyword gaps**: fox, fly, nest, beak and hunger were not offered (t028).
- **The PIE text doesn't mark who is speaking**, so dialogue reads as a run of lines (t024 review).
- **neg + 1st-person subjunctive always gives *mē***: "I shall not …" comes out as "let me not …", and plans have no way to ask for *ne* (t028).
- **Say/drive verbs share some forms**: *h₂éǵt* stood where a 'drive' form was meant. Add a warning for homophonous cells (t030).
- **Pronoun number**: the brief lists SG|PL only, although DU works, and pronoun number isn't checked against the English (t030).
- **Antecedent checker**: its two-clause window gives false positives on story topics (t028).
- **Cap verdict (t029 reviewer): keep the cap formula.** The squeeze came from the slice: the theme-core picker matches whole gloss words, so "cow" missed gʷṓws (glossed "cattle"), and 2 of the 8 core slots stayed empty. Wave-2 slices pass `--core` explicitly, and the picker should match synonyms.
- **Ungendered "you"/"we"** silently takes masculine adjectives, with no warning (t029).
- **Colour words specced as masculine nouns** (bʰl̥Hós 'white', h₂r̥ǵrós 'shining'): they can't agree with a neuter head, and check_plan doesn't flag it (t031).
- **A verb-only clause defaults to 3sg** even when the plural subject is understood (t031; brief rule 9 tells planners to set the number, but the engine doesn't warn).
- **Gender on a predicate slot is silently ignored** (t031).
- **391 eh₂-stem nouns are unusable** because they fall below the shape-backtest threshold (mare h₁éḱweh₂, tail, wasp, …). Other core words are also unusable: ugʷsḗn 'ox', sḗh₂l 'salt', 'louse', 'bee', 'nit'; fox h₂wl̥pis needs an override. This is a large vocabulary loss and the highest-priority engine item (project-reconstructions agent).
- **ḱe 'here'** is a particle, so make_slice never offers it as an adverb. Add a deictic 'here' adverb.
- **Slice keywords to add in wave 2**: nest, fly, thirst, hunger/hungry (needs `--derived`).
- **Imperative with no `person` defaults to 3sg** ("let him take"), with no warning even when a vocative is present, and brief v4 never says imperatives need `person`. This caused 12 of the 14 wrong items in t027. Older approved batches have IMP verbs without person: t003 (6), t006 (1), t007 (2), t015 (21), t023 (18). These are being audited.
- **Accents on the new imperatives** h₁éddʰi and tétḱdʰi are wrong (t027).
- **meter_fit is lenient.** Its ±1 window around 8 and 11 accepts any line of 7–12 syllables. t032's 0.963 means "lines are 7–12 syllables"; only 29% have exactly 8 or 11, and cadence isn't checked. Report the exact-count share as well, and don't describe meter_fit as "scans" (t032).
- **closed:indefinite_kwi with no gender** defaults to animate kʷim ("no one" where "nothing" was meant) (t032).
- **The antecedent warning checks only gender and number**, so it misses same-gender ambiguity (wolf vs dog). Nothing checks reflexive swo- (t032).
