# Tier-3 review: packet t029 (28 items)

The packet has 20 real items, 5 plants and 3 Tier 1 lines. The real items cover herding, work songs and weather-lore; the Tier 1 lines are a King and God line and two Schleicher fable lines. The reviewer built the packet with `make_review_packet.py t029 --n 20 --plants 5 --tier1 3` and worked from handbook knowledge (Fortson, Beekes, Ringe, LIV², Mallory & Adams). Every token was checked through a reverse index of `Lexicon.cells()`, `participle_cells()` and `closed_class.json`. Verdicts are in `docs/audits/packets/t029-verdicts.jsonl`.

The grades follow the t021/t023 calibration:
- **wrong**: ungrammatical, or the meaning changes.
- **minor**: ablaut, accent, notation, or a stretched sense.

## Calibration

`score_review.py t029`: plant recall **5/5**, all five named. No Tier 1 line was judged wrong. Real items judged wrong: **2/20** (rate 0.10).

| real items | ok | minor | wrong |
|------------|----|-------|-------|
| before fixes | 12 | 6 | 2 |
| after fixes  | 14 | 4 | 0 |

## Blind back-translation

Six items (4e1c835b, c38970f8, c11b8924, acae918c, e77b16b4, d014779f) were translated from the `pie` field and lexicon glosses alone, before any English field was opened. The results are in `docs/audits/packets/t029-blind-translations.jsonl`.

All six agree with the English in substance. Two of the blind uncertainties turned out to be plants: the 2pl memn̥té addressed to one grandson, and the 1pl dʰégʷʰome 'we burned' where the English has 'the fire was burning'. A third uncertainty was cleared by the English: widóm 'I found' after the son as subject is meant. Remaining differences are only tense nuance, from gnomic aorists and injunctives.

## Wrong (2 real), with fixes

- **15a6b441 = t3-t029-00025 (agreement).** `nu yúH nogʷṓs` 'now you are naked' is said to the sheep. h₂ówis is feminine, and the batch's own anaphor h₁íh₂n̥s in 00005 treats it so, but the predicate adjective came out masculine.
  - Cause: the `closed:personal/2` slot had no gender, and the engine defaults it to masculine.
  - Fix: `"gender": "f"` on that slot. The text now reads → `nu yúH nogʷéh₂es`.
- **2f3fde63 = t3-t029-00037 (content omitted).** The English says 'Mother Earth, feed the cattle!', but the plan had no object slot, so the PIE said only 'nourish!'.
  - Fix: add the OBJ slot gʷṓws (PL). The text now reads → `dʰéǵʰom méh₂ter gʷṓs h₂éle`. gʷṓws goes from 5 to 6 uses, which is still within the cap.

## Plants (5/5 caught)

Each of the five originals was checked in `corpus/tier3/t029.jsonl` and is correct:
- c746d65b: abl. h₂erh₃wṓd where the original has acc. h₂erh₃wóm.
- c38970f8: 2pl memn̥té where the original has memn̥dʰí.
- c11b8924: 1pl dʰégʷʰome where the original has dʰégʷʰet.
- bf09f687: acc. pl. n̥bʰróns where the original has voc. ń̥bʰre.
- a6f0c394: loc. wédni where the original has acc. wódr̥.

## Minor (real)

- **716daa9e (00019):** stunddʰí 'push' is used for 'strike', a stretched sense. The English 'strike' is said twice; the PIE has it once.
- **acae918c (00009):** kúdʰe 'where' is used for 'where from'. The ablative péruns in the answer carries the 'from'.
- **d21a0f3e (00007):** the reflexive swā́s h₂ówins sits in a clause whose subject is ǵʰwḗr, so strictly it says 'the beast's own sheep'; the intended owner is the herdsman. Graded minor because the scored verdict was already filed, but it is close to wrong. **Fixed:** the swos MOD slot became a POSS slot for `closed:anaphoric_i` (m), so the text now reads `ǵʰwḗr h₁ésyo h₂ówins ne lémbʰt`.
- **fc3e9315 (00003):** pótni 'mistress, lady' was translated 'wife'. **Fixed:** the plan's English now says 'Mistress'. This change was optional, since Ved. pátnī also means 'wife'.
- **d96fc98e (00036):** a substitute caused by the cap; see below. 'Do not drive the pigs to the mountain' and 'lead the son home' stand where calves or cattle are expected. pérwr̥ is ambiguous between 'ford' and 'rock'.
- **f6304263 (00020):** wr̥h₁ḗn 'lamb' is shown sipping the cows' milk, standing in for a calf.

## Accepted conventions (not penalised)

- h₁yód 'when' introduces the weather rules.
- Gnomic aorists and injunctives (h₂wérst, térst, séngʷt, déh₃t) stand for an English present.
- Prohibitions are mē + injunctive.
- Middles are used where expected: ḱéyor, Hrumptór, wéndʰetor.
- An accusative of goal follows verbs of motion (kólHonm̥, pérwr̥, ḱóymom).
- kʷékʷlos stands for 'wagon' (Gk κύκλα).
- The three Tier 1 lines are in source notation.

## Engine and tooling findings (reported, not changed)

1. **The gender of a personal pronoun defaults to masculine without a warning** (00025). In a nominal sentence, a 1st/2nd-person pronoun with no `gender` makes a masculine predicate adjective, even when the vocative it refers back to is feminine. `plan_warnings` could flag a PRED adjective whose pronoun subject has no gender after a feminine vocative. The planner brief could also say that you/we take a gender when an adjective is predicated of them.
2. **The theme core missed the batch's main animal.** `make_slice.py` picks `theme_core` from keyword hits. `hits()` matches whole words in the gloss (verified), so the keyword 'cow' matched gʷowsth₂ós 'cow-stall' but not gʷṓws, whose gloss is 'cattle'. The core has only 6 of its 8 slots filled, and gʷṓws is not among them. So the batch's main animal got the ordinary cap of 6 instead of the theme cap of 15. See the cap verdict below.

## The cap and the substitutes

**Cap arithmetic.** The cap is max(6, round(0.02 × 40), round(0.005 × 716)) = 6. It binds widely: dog, sheep, lamb, wolf, night, beast, step/come, sun, herdsman, home and field all sit at exactly 6. The herd (stéh₂dʰh₁om) and the rain-cloud (n̥bʰrós) are theme core and are used 15 times each.

**How unnatural the substitutes are:**
- **Pigs (3 uses).** 00031 'when the pigs are afraid, the wind blows' is plausible folk lore. 00006 'the pigs became afraid' in a night-raid story is fine. 00036 'do not drive the pigs to the mountain' is odd.
- **Wild beast (6 uses).** Natural: it names a predator, not cattle.
- **Grandson (1 use, 00014).** Natural in a family herding scene.
- **'The herd' (15 uses).** It is the generic noun of the genre and reads naturally, although it is repetitive.
- **Truly odd: three spots in two texts.** 00036 has 'lead the son home' as a weather rule, and 00020 has a lamb drinking cows' milk.
- **Grammar.** None of the substitutes is ungrammatical. The cost is semantic oddity in about 2 of 40 texts.

**Whether the cap or the planner is the cause:**
- The cap rule itself is not what squeezed cattle. The squeeze comes from the slice's theme-core selection, which left out gʷṓws while two core slots were empty. With gʷṓws in the core it would have had 15 uses.
- The planner also shares the blame. gʷṓws was used only 5 times against a cap of 6. One English sentence (00037) even mentions cattle, but its plan has no cattle slot.

**Recommendation.** Keep the global cap. Rebuild herding slices with `--core` that includes gʷṓws, or make the core picker match keywords against synonyms (cow → cattle).

## Fix log

- `data/generation/plans/t029.jsonl` was changed in four plans:
  - 0025: gender f on yúH.
  - 0037: gʷṓws added as the OBJ of h₂éle.
  - 0003: the English 'Wife' changed to 'Mistress'.
  - 0007: the reflexive swos on the sheep was replaced by the anaphoric genitive h₁ésyo.
- The batch was re-realized with `realize_plans.py … --batch t029 --model claude-sonnet-5-5 --prompt-id tier3-planner-v4`.
- The gate is **PASS** with max_lexeme_uses 6 against a cap of 6, all_exact 40/40 and 0 rejects.
- The release status is left to the lead.
