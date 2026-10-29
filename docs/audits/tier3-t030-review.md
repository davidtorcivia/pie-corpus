# Tier-3 review: packet t030 (28 items)

The batch has 40 short texts: dialogues, travel and homecoming. The packet held 20 real items, 5 plants and 3 Tier 1 fable lines (`--n 20 --plants 5 --tier1 3`). The reviewer worked from handbook knowledge only (Fortson, Beekes, Ringe, LIV², Mallory & Adams, as remembered). Every packet token was checked against a reverse index of all admissible cells, built from `Lexicon.cells()` and `closed_class.json`. Verdicts are in `docs/audits/packets/t030-verdicts.jsonl`. The blind translations are in `docs/audits/packets/t030-blind-translations.jsonl`.

The grades follow the t021 and t023 calibration:
- **wrong**: ungrammatical, or the meaning changes.
- **minor**: ablaut, accent, notation, or a stretched sense.

**Disclosure: the plant recall is not independent.** In order, the reviewer:
1. Built a token→cell reverse index, which prints lexicon glosses, and used it on the PIE before translating. The `uncertain` notes in the blind file rely on it.
2. Did the blind translations.
3. Read the English and analysed every item. All six wrong items were identified in this pass.
4. Compared the packet's PIE with `corpus/tier3/t030.jsonl` to find the plan records to fix. That comparison exposes exactly the five plants.
5. Fixed the plans and re-realized.
6. Only then wrote `t030-verdicts.jsonl`.

Because the verdicts file was written after step 4, **5/5 plant recall should not be counted as independent calibration**. The five plants are gross case, number and agreement errors, which the lead can judge directly. Nothing under `data/audits/` was opened. Separately, while checking the plan file's format, the reviewer saw the English of plan t030-0001, which was not in the blind six.

## Counts

| set | ok | minor | wrong |
|-----|----|-------|-------|
| packet, all 28 | 16 | 6 | 6 |
| real items (20), before fixes | 15 | 4 | 1 |
| real items (20), after fixes | 16 | 4 | 0 |

After the fixes, 3b36d09f moves from wrong to minor (its unrendered 'home' remains), and 7c040bc2 moves from minor to ok.

The scorer reports plant recall 5/5 (all 5 named), real wrong 1/20 (0.05), and no Tier 1 item judged wrong. After the fixes, `realize_plans.py` gives gate **PASS**: 40/40 exact, max_lexeme_uses 6 against a cap of 6.

## Wrong

### Real (1)

- **3b36d09f (t030-0032)**: `ḱwṓ-kʷe h₁ím h₂epó h₂éǵt` uses the root aorist of *h₂eǵ- 'say' (pie-lex-h2egjt). The line therefore reads 'the dog *said* him away'. The planner confused two near-homographs: h₂éǵt 'said' and h₂éǵeti 'drives'. 'Drove away' needs h₂éǵet, which the same text uses in its first sentence. That lexeme is already at the batch cap (6 uses), so the fix uses causative troséyeti 'make afraid': `h₂epó troséyet`, with the English changed to 'scared it away'. This item is now ok in substance; the unrendered 'home' (in 'drove the herd home') remains a minor point.

The reviewer checked the other five h2egjt plans (0015, 0019, 0024, 0030, 0036). All of them correctly mean 'said'.

### Plants (5, all caught)

- **f85ad09e**: `pértus kúdʰe h₁sénti`. The subject is singular but the verb h₁sénti is 3pl; it should be h₁ésti.
- **da191430**: `ph₂térn̥s` is accusative plural but is the subject of déh₃t; it should be nominative ph₂tḗr.
- **2365ab69**: `téwe suHnóws h₁ésmi` has the genitive where 'I am your son' needs the nominative suHnús.
- **6bd68a68**: `pérurih₁` is a dual ('two mountains') where English has 'the mountain'.
- **15f96ef8**: `HeHḱéws h₁éḱwons` has a genitive-singular adjective on an accusative-plural noun; it should be HeHḱúns.

### Outside the packet (1, fixed)

- **t030-0023**: `léwka h₂éwsos h₁mé dukdʰí` has 1sg 'me' for 'Bright Dawn, lead **us**'. The speaker is one of two men. The plan's `closed:personal/1` slot had no `num`. Setting `"num": "DU"` gives the accusative dual **n̥h₃mé**.

The other 19 corpus texts that are not real packet items (15 unsampled texts and the 5 originals of the plants, minus 0023) were read quickly, and no further wrong item was found.

## Minor

- **c4a23e44**: h₁r̥sḱét 'arrived' stands for 'returned home', and the locative yéh₁ni 'in the year' for 'after a year'. nesetor would fit, but it is at the cap.
- **f2d679cc**: gʷā́m writes the Stang outcome of the 1sg aorist beside gʷéh₂t. This is the same notation point as in t021 and t023.
- **7c040bc2**: déh₃wm̥ comes from LIV's marginal *deh₃u- 'give', while the batch otherwise uses déh₃-. **Fixed** to the root-aorist déh₃m̥, so this item is now ok. Plan 0024 (`déh₃ut`, outside the packet) still uses *deh₃u-; it is defensible and was left.
- **8e895c09**: h₃sléydʰ- 'slip, slide' is used for 'go astray', a stretched sense.
- **Tier 1 fable lines**: 2703d97f (Byrd-type notation, a-colouring, parenthesised (y)) and eaefe6ed (Schleicher-style, no laryngeals). In both, the English 'the sheep has' is singular against a plural or genitive-plural noun. This is the same faithful-but-clashing convention noted in t023.

## Accepted (not penalised)

- The i-stem vocative gʰóstey. The heteroclitic pérwr̥, péruns, péruni ('rock, mountain'), whose oblique n-stem is Hittite-like.
- The lengthened ē throughout the cells of ǵʰwḗr (compare Gk θήρ, θηρός).
- Injunctives for English present and past tense.
- Thematic subjunctives for hortatives: h₁édomes píph₃ōmes 'let us eat and drink', sédomes, péromes, h₁éyomes.
- swo- used loosely as 'her own' in 4fba6305.
- The ambiguity of pérwr̥, which the lexicon glosses as both 'ford' and 'rock'.

## Blind back-translation

Six items were translated from the PIE before the reviewer read any packet English: 4caefbae, 23a702f0, f2d679cc, 8b36fb69, d728adb6, 7841cecb. **All six agree** with the English in substance. The differences are small:
- the tense of ḱéyo ('lies' / 'was lying');
- péh₂wr̥ nékʷti ('fire for / in the night');
- 'travelled three nights' against 'in three nights went away'.

The only real uncertainty was lexical: kʷelsós 'turning' or 'far', and pérwr̥ 'ford' or 'rock'.

## Engine and brief findings (for the lead; nothing in `pie/` was changed)

1. **Near-homograph verbs.** pie-lex-h2egjt h₂éǵt 'say' (aorist) and pie-lex-h2egjeti h₂éǵeti 'drive' share the forms h₂éǵesi and h₂éǵoh₂, which the engine lists as SBJV of h2egjt and PRS of h2egjeti. The planner picked the wrong one once. A plan warning when h2egjt takes an OBJ or ADV of direction, or a planner-brief note on the pair, would catch this.
2. **Slice brief on personal pronouns.** It advertises `closed:personal/1` and `/2` as "num SG|PL", yet the dual (n̥h₃mé, uh₃wé) works. Two speakers in a dialogue are common, so the slice text should say DU.
3. **Pronoun number is not checked against the English.** The validator cannot see that 'us' was planned as SG (t030-0023). This is a known limit of plan checking, not an engine bug.
4. **Cap pressure.** h2egjeti, nesetor and the speech verbs sit at the cap of 6 in a 706-token batch. This forced the troséyeti workaround, and it explains the rotation of seven speech verbs (sékʷt, wéwket, mléwHt, wérh₁t, bʰéh₂t, h₂éǵt, wérh₁yet). These are not wrong, but the rotation is artificial in short dialogues.

## Conversational quality

The batch is genuinely conversational in shape, but thin in conversational *machinery*.

**Strengths.** Question and answer are natural and varied:
- Question words cover the core set: kʷís, kʷíd, kʷór, kú, kúdʰe, kʷíh₁, and kʷóm as a determiner.
- Yes/no questions are answered by echoing the verb, which is idiomatic: `bʰéwgs? bʰéwgm̥.`, `h₁íd dedórḱh₂e`, `h₁íh₂es gʷih₃wéh₂es`.
- Vocatives are used consistently, for kin (bʰréh₂ter, méh₂ter, swésor, ph₂ter), for strangers (h₂nér, gʰóstey) and for animals (wĺ̥kʷe, ḱwón).
- Imperative chains (wiḱdʰí sddʰí-kʷe, h₁éddʰi píph₃e-kʷe) and hortative subjunctives are well used.
- Optative blessings serve as farewells: deywṓs twé h₂léksoyh₁ent, sóh₂wl̥ twé wédʰoyh₁t, nókʷts h₁uséwih₂ h₁syéh₁t.
- Hospitality scenes (guest, mead, wine) give a plausible register.

**Weaknesses.**
1. **No greeting or leave-taking formulas.** There is no 'hail' or 'be well', no welcome formula, and no thanks; texts open cold with a question.
2. **Turn boundaries are invisible in the PIE.** The PIE has no quotation marks and few speech verbs inside the dialogues. In 4caefbae, dbb8fb0b and 2365ab69, the speaker changes only at '?' or by context, so a model learns run-on monologue as much as dialogue.
3. **Few discourse particles.** Only nu and -kʷe appear. There is no 'but' or 'and then' (*h₂éti, *-de or *tu), no 'yes' or 'no' beyond echoes, and no emphatic túH in contrastive answers ('And you, where are you going?' loses its 'and you').
4. **Very short texts** (16 words on average). Most exchanges run two or three turns and stop. Few texts have a follow-up question or a disagreement.

**Verdict:** the dialogue is good as raw question and answer, and the grammar inside the turns is reliable. It needs greetings, explicit turn-taking, and discourse particles before it teaches conversation rather than captioned exchanges.
