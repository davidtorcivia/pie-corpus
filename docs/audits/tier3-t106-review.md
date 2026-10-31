# Tier 3 batch t106 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues about crafts at work, between craftsmen and their customers (the smith and
his price, an ordered blade, a cracked pot brought back, firing clay, tanning a hide, a carpenter shaping a yoke,
trading work for food, a borrowed tool that broke; copper and bronze only), `tier3-dialogue-inworld-v1`. Reviewer:
a calibrated agent review following docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t106 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items from the `pie` field only, done before any English was printed:
   `docs/audits/packets/t106-blind-translations.jsonl`.
3. Every packet token was checked against a reverse form index built from `Lexicon.cells()`,
   `.participle_cells()` (all genders) and the closed class. Doubtful senses were checked against the full glosses.
   The verdicts were written and saved before corpus/ or the plans were opened:
   `docs/audits/packets/t106-verdicts.jsonl`, sha256
   `072d307eb2d847ac05a91f3cb8b46e9f06b82a89c50b3d52f870de95839cc122`.
4. Ran `resolve_review_items.py t106`, then `score_review.py t106`.
5. Second pass: all 40 plans and records were read in full against planner-brief-v4 and the in-world dialogue brief.
   Speakers, turns, per-sentence English, and clause and turn counts were also checked by script over all 40 plans.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong | 0/20 |
| real items judged minor (as scored) | 4/20 (1 withdrawn below; 3 fixed) |

Plants caught (in the packet's spelling):
- sénosyo: GEN.SG used for the standard of comparison "than the old one". The ablative sénōd is needed, and the
  record has it.
- skéwHteyes: NOM.PL used for "from the hides of sheep". The ablative skuHtíbʰos is needed, and the record has it.
- péh₃tloy: ACC.DU used with déḱm̥ "ten cups". The plural péh₃tleh₂ is needed.
- dʰélbʰetes: SBJV.2DU/3DU used for "Will you hollow it out quickly?", said to one person. The 2SG dʰélbʰesi is needed.
- wr̥ǵmé: AOR.1PL used for "I made it for her". The 1SG wérǵm̥ is needed.

**Real minors and their outcome:**

| item → record | finding | outcome |
|---|---|---|
| 7b870ce6 → 00009 | térdt (AOR) in the general statement "an awl does not bore through bone" | **withdrawn**: térdt has only aorist forms, so the gnomic aorist is the rule (v4 rule 8) |
| 2293e196 → 00012 | swéh₂m "its own hide" in a verbless answer, with no subject to bind the reflexive | fixed: the swos slot is dropped; English "The boar's fangs and hide." (tworḱósyo dénḱtreh₂ skéwHtim-kʷe) |
| a722d9ee → 00031 | h₁l̥ḱéys is "elk" (h₁ólḱis), but the English said "stag" | fixed: English "Find me the horn of an elk."; a stray `gender: m` on the f noun slot was removed |
| 4746bbfb → 00036 | swóm "your own knife": the reflexive is not bound by the clause subject, which is the knife itself | fixed: POSS → closed:personal/2 enclitic (kúdʰe toy ḱéstrom h₁ésti?); English "Where is your knife?" |

**Real wrong: 0/20 before and after the fixes. Real minor: 3/20 before (after the withdrawal), 0/20 after.**

## Blind back-translation agreement

All six were translated before any English was seen. They agree in substance on all six. Where they differ, the
difference is a single word, and none points to an error in the PIE:

| item | divergence |
|---|---|
| 7dd40500 | ǵʰóstoh₁ read loosely ("with a stick/guest?"); it is INS "with the hand" |
| 3de17488 | none of substance; sh₂yéh₁s was read as a jussive "so be it" (OPT "may you be sated") |
| e3e54294 | pr̥kʷéws ("from an oak") was missed; sh₁ésō ("harvest time") was not identified |
| d8f88cda | réh₁dʰesi was read as "take for it" (it is "complete"); péyḱoh₂ was read as "carve", correctly |
| 2293e196 | h₂éydʰom was read as "for fire" (it means "to my fire"); the rest matches |
| 4746bbfb | dinóm was read as "for a day", correctly; dʰl̥gʰési "you owe much" (the PIE has no "much": "you owe me") |

## Second pass (all 40 records)

Structure: every plan has a speaker on every clause, exactly two speakers, the user first, and a new sentence at
every change of speaker. Per-sentence English is on every sentence-initial clause and nowhere else. The joined
English equals the plan's English. Each plan has 9–13 clauses in 5–8 turns. All of this was checked by script.

Content: nothing is modern or coined. The metal is always h₂éyos "copper, bronze": knives and cauldrons are "poured",
which means cast. There is no iron and no anachronistic tool. The two project reconstructions, gʷʰermós "warm" (00003,
00032) and spélom "story" (00035), are allowed by v4. The model speaker converses in the order dialogues as well:
it asks back (the price, how many, which material, "Who made it?", "When will you complete it?", "What did you cook
in it?", "Who are you? Where are you going?"). Turns answer each other. One loose spot is 00031 "Will they not
become angry?", whose "they" points back two turns to the oxen. A SUBJ uksḗn would make it plain, but uksḗn is
already at the cap (7), so it was left as is.

Checks the lead asked for:
- **Paraphrased craft words, read against the full glosses.** Each English says what its PIE says:
  - axe = gʷr̥h₂ú ḱéstrom "heavy blade" (00002); ḱéstrom "knife, cutting tool; blade";
  - clay = dʰéǵʰōm "earth" (00004, 00011 "the earth of the river");
  - potter: the potter is addressed as gʷḗn "woman" or wóyḱe "neighbour". The smith is dʰh₂bʰrós, whose gloss
    reads "craftsman, smith";
  - tanning = ksnéwti "scrape" + h₂linéHti "smear" with fat + tn̥néwti "stretch" + h₂sowséyeti "dry" (00005), and
    urine with oak bark loosening the wool (00006: léwHt "cut off, loosen", gnomic aorist);
  - anvil = h₂éḱmō, whose gloss gives "anvil" as a sense (00010), so "on the anvil" stands;
  - mend = "make a new one" (néwom … kʷr̥dʰí / péyḱoh₂);
  - crack = bʰeyd- "split" (the pot, the plough, the wheel: MID AOR bʰidtó, PRED bʰidtós).
  - Other senses checked: wédʰeti "lead; bring" for loads and grain; púHyeti "rot, stink"; gʷr̥dús "dull" (of a
    knife); ḱubʰrós "beautiful"; péh₂uros "few"; h₂m̥bʰí "in exchange for"; déh₁ "without"; ḱóm "beside"; wetsós
    "calf"; h₁yáǵeti "sacrifice"; pérwr̥ "mountain"; h₂éwh₂os "maternal uncle"; wiHrós "warrior"; pótnih₂ "wife";
    bʰólǵʰis "bellows"; h₁éh₁ugʰos "boast"; h₂ewsér "at dawn".
- **Fearing**: no verb of fearing occurs in the batch.
- **Cows**: 00039 "I milk my cows" is gʷṓws PL with `gender: "f"`; oxen are uksḗn throughout.
- **h₂élyos** always has a gender that matches its referent: m for the pot, the cauldron and the vessel
  (h₂élyom: 00003, 00008, 00020, 00037); n for "something else" (h₂élyod, 00034).
- **Predicate adjectives with dropped subjects** agree with the referent: ml̥dú h₁ést (the yoke, n), ḱuh₁rós
  h₁éseti / sénōd ḱéwh₁yōs (the wheel, m), h₂eḱróm h₁ést (the knife, n), méǵyōs h₁ést (the cauldron, m), ḱubʰréh₂
  h₁sih₁ént (the cups, n PL), gʷḗn túH ǵn̥h₃réh₂ (f), túH h₁suménēs / ḱéywos (m).
- **Short answers** take the case of the constituent asked about:
  - ACC: "Seven oaks", "Nine days", "Salt", "Stones and bones", "Beavers and fish", "Two loads"/"Three loads",
    "Four lambs", "A big one", "My sons' garments", "The wool of five sheep";
  - ABL: "From a bull", "From horn";
  - INS: "With oxen", "A knife?", "With joy!";
  - LOC: "On a stone?";
  - NOM: "Four sacks", "Two loads" (the subjects of "do you have"), "My uncle, a wise carpenter" (the subject of
    "who taught you"), and the echoes "A hundred men!" and "My dog?".
- **Athematic obliques** are all the engine's: ph₂wéni/ph₂wénh₁, dʰǵʰméh₁/dʰǵʰmés, sh₂wéni, sh₁séni, kʷsépi,
  h₂Hséh₂i, démi/démey/déms, dʰurés, h₃sth₁és/h₃sth₁éh₁, h₂ḱméni/h₂ḱm̥néh₁, uksn̥bʰís/uksnés, sn̥h₁wénh₁/sn̥h₁wéns,
  wésni, ǵʰwērés (cf. Gk θηρός), pótn̥yeh₂ey, h₁n̥gʷl̥sú, ph₂tréh₁, dʰugh₂tréy, kh₃téwi, déh₂newi/déh₂nus, pérunsu,
  h₃n̥gʷénh₁, sémeh₂i, h₁l̥ḱéys, skuHtíbʰos/skuHtísu/skuHtéys. The 1SG aorist ǵʰḗm "I poured" (00023) follows
  Stang's law from *ǵʰéwm̥. No error was found.
- **Enclitics** stand in second position: moy/toy/nos/te/me after the first word (or after a vocative), toy moy
  in sequence (00019), and -kʷe on the first word of its clause or on the last conjunct (gʰéldʰōh₂-kʷe toy,
  ǵʰóstoh₁-kʷe moy mē h₁éwses, skéwHtim-kʷe).

Plan fixes from the second pass, beyond the three packet minors above:

| record | finding | fix |
|---|---|---|
| t3-t106-00022 | the same h₁ólḱis "elk" was rendered "stag", and the f noun slot carried `gender: m` | English → "Bring me the horn of an elk."; gender key removed |

## Engine or brief notes (report only)

- `formula_uses` is 0, although 00028 builds "may the gods give me good things" as v4 says, and the greeting "be
  well!" (00038) is the v4 build. The same counter/export mismatch was noted in t099.
- closed:anaphoric_i gives h₁éy as NOM.SG m (00016, 00020: "it" for the stone and the cauldron). Handbooks usually
  give *(h₁)ís / *só for that cell; worth a check in the closed class. Low priority.
- The cap blocks small clarity fixes: in 00031 the subject "the oxen" could not be made overt because uksḗn is at
  the cap of 7. It is a plain-English improvement only, not an error.
- Some sentence-level English connectives ("But I will build…", "And I will pay…", "And what is the price…") have
  no PIE word. These are not content words, so they were left.
- No engine gaps were found in the forms.

## Result

- Re-realized with `realize_plans.py data/generation/plans/t106.jsonl --batch t106 --model claude-opus-5-5
  --prompt-id tier3-dialogue-inworld-v1`: 40/40 realized, 0 rejects, all exact, max lexeme uses 7 (at the cap), 0
  WARNs. **Gate: PASS.**
- Release rule: recall 5/5 (needs ≥ 4/5), real wrong after the fixes 0/20 (needs ≤ 2/20), gate PASS. All three
  conditions hold; the approval decision is the lead's.
- Backup of the plans before the fixes: scratchpad `t106-plans-before-review.jsonl`. Nothing is committed.
