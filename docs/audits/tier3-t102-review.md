# Tier 3 batch t102 review (`review-v1`)

Batch: 40 in-world dialogues on the lord and his war-band (prompt `tier3-dialogue-inworld-v1`, model claude-opus-5-5).
Procedure: docs/generation/reviewer-brief.md. Packet: `make_review_packet.py t102 --n 20 --plants 5 --tier1 3`
(28 items: 20 real, 5 planted, 3 Tier 1).

## Calibration

- Verdicts: `docs/audits/packets/t102-verdicts.jsonl`, sha256
  `7dd0f54929329bea120a503e3ff39da2fbd46c88aa6ce5ec2bfa57e513353875`. I saved this file before opening corpus/ or the plans.
- `score_review.py t102`: **plant recall 4/5** (4 named), Tier 1 judged wrong 0/3, real items judged wrong 3/20, minor 3/20.
- Plants caught: 08697d39 (ḱósyeh₂i sémeh₂bʰis, INS.PL), 1ee11283 (kʷótereh₂s, f. gen. sg.), 1350f876 (dʰl̥gʰónti, 3pl),
  56f934fb (pl̥nh₁tés, 3du).
- Plant missed: 24b4e3ff "h₃órbʰe h₁éḱwōs **wédn̥s** ph₃ént?". The record (t3-t102-00014) has acc. wódr̥. I read the
  abl./gen. as a partitive. This is the "short turns hide plants" pattern again: the wrong case is in a one-line question.

## Blind back-translation (6 items, PIE only)

`docs/audits/packets/t102-blind-translations.jsonl`. Five of the six agree with the English in substance (fce5cbe8,
1ee11283, 22493af3, 2131be13 and b370e9b1 apart from details). The differences were my own misreadings, not faults in the
items:
- b370e9b1: I took h₂énHe as a particle. It is the vocative "grandmother" (project word pie-proj-h2enHos).
- b370e9b1: I read "will a foal fall to me" for h₁opéyēti, which means "make reach; give".
- 9462cf30: I read wéwke as a 3sg past. It is the thematic-aorist IMP.2SG "tell", which fits "Tell me a story".
- 2131be13: I read "what do you eat" and "will judge rightly". The English has "why should you eat it" (kʷíd = why) and
  "may the lord point out what is right" (optative).

## Packet verdicts against the engine, after checking

| item | record | verdict | finding | outcome |
|---|---|---|---|---|
| da675c3b | t3-t102-00017 | wrong | "I do not deserve it": h₁ím (m.), but "it" is the gift déh₃rom (n.) | **fixed** in the plan (gender n → h₁íd) |
| 7c79127c | t3-t102-00005 | wrong → **withdrawn** | dwóyh₁ h₂ówih₁ ("two sheep", f.) | not an error: `closed:numerals/2` has one f./n. cell dwóyh₁ (Ringe 2017 p. 53; Ved. dvé is both f. and n.) |
| 3c2a2a63 | t3-t102-00034 | wrong → **withdrawn** | the same dwóyh₁ h₂ówih₁, twice | as above (t3-t102-00013 has it as well) |
| b370e9b1 | t3-t102-00033 | minor | h₂énHe and pṓlHos are project reconstructions | allowed by planner-brief-v4; no change |
| 9462cf30 | t3-t102-00019 | minor | spélom "story" is a project reconstruction | allowed; no change |
| 3295968b | t3-t102-00003 | minor | h₁íns (m.) for gʷṓs | the English says "cattle", not cows, so m. is acceptable; no change |

Real items judged wrong: 3/20 as scored. After the check, 2 are withdrawn (engine data, not the plan) and 1 is fixed at
the source, so **0/20 remain wrong**. Minor: 3, all accepted as they stand.

## Second pass: all 40 records against planner-brief-v4 and the in-world dialogue brief

Structure (scripted check over every plan): every clause has a speaker; each dialogue has exactly two speakers, the user
first; a change of speaker always starts a new sentence; every sentence-initial clause has its own English, and those
sentences joined give the plan's English; each dialogue has 4–14 clauses and 2–8 turns. No problems. No turn fails to
answer the one before. Nothing is modern. The only words outside the inherited set are project reconstructions, which the
brief allows: mógʰus (0001, 0021), h₂énHos (0033), pṓlHos (0033, 0034), spélom (0019).

Checks the task asked for:
- **Pronoun WARNs (5)**: abstract tód "it" in 0002 ("Do you swear it?") and twice in 0030 ("He will not see it",
  "I did not mean it"); cataphoric ḱód "this" in 0032 ("Say this:"); "their" in 0021, which goes back to póyḱōm four
  clauses earlier. All five read correctly, and they are the deliberate set the task named.
- **Other pronouns**: 0017 h₁ím → h₁íd (fixed, above). 0023 "Our father followed our lord all his life" was realized
  with h₁ím "him", whose nearest m. sg. antecedent is h₁énos, "the one yonder". So the English said more than the PIE.
  **Fixed**: OBJ is now wiḱpótim + POSS nos. wiḱpótis is theme-core and now at 21, which is within its cap of 21.
  0031 "their king" (h₁éysōm) had no plural antecedent except the horses one clause earlier; it is fixed in the second
  round.
- **Senses against the full glosses**:
  - márkos is "horse"; it is in the lexicon, inherited (Celtic, Germanic) and used in its sense.
  - kóryos is "war, troops", which covers both "troop" and "in the war".
  - h₂elgʷʰ- "be worth; deserve", h₁opéye- "make reach; give", nes- "return home unharmed" (0024 "come home unharmed" is
    exact), sepelyé- "honor", bʰoydʰéye- "persuade", gʷr̥dús "slow; heavy; dull", ḱéstrom "knife, blade" (for sword),
    h₂óyu "lifetime" and mḗd- "heal" all match their glosses.
  - The paraphrases are faithful: shame is "your name is bad" or fear of a bad name; the coward is "a child who flees";
    tomorrow is "in the morning"; the arm-ring is "gold on your arm"; the hall is "hearth".
  - Stretched but acceptable (minor, unchanged): wéḱm̥ "I did not mean it" (0030; the verb means "want"); sn̥gʷént
    "fell" for "were killed" (0008; gloss "fall down").
  - The o-grade *-éye-* verbs (dʰoréye-, ḱlowséye-, h₁wogʷʰéye-, bʰoydʰéye-) all have plain senses in their glosses, so
    they pass the causative rule.
- **Fearing with the ablative**: bʰeyh₂-, bʰebʰóyh₂e + ABL (wédn̥s, ǵʰoysóybʰos, h₁éymos, kʷosmōd, h₂egʰṓd h₁némn̥s).
  All correct.
- **Formulas (4 uses)**: swift horses (0014, 0039, and the compound HeHḱuh₁éḱwos in 0016); ḱléwos ń̥dʰgʷʰitom (0016);
  déh₃tōr h₁uséwōm (0016, 0037); deywṓs h₁wésuh₂ dh₃ih₁ént (0016). All are used in their sense. 0040's
  "déh₃tor déh₃nōm" is a variation built on the formula and is fine.
- **Cows**: gender f. in 0005, 0006, 0021 and 0040. 0003 says "cattle", with m.
- **h₂élyos**: used as an adjective with a gender every time (0005 "the others" m., 0022 m., 0036 MOD).
- **Predicate adjectives with dropped subjects**: ḱuh₁rós (the arm, m.), bʰeydʰós, h₂yuHn̥ḱós, dʰérsistos. All agree.
- **Short answers**: 0021 "A hundred cows" is np `case: ACC`. Correct.
- **Athematic obliques**: kh₃téws, kh₃téwi, gʷréwi, gʷrúh₁, déh₂newi, ph₂wéni, h₂ḱméni, dʰǵʰémi, méh₁nsi, skélesi,
  wésni, yéh₁ni, h₂nr̥sú, kl̥Hn̥sú, kl̥Hn̥bʰós, déh₃n̥bʰis, wiḱpóteyey, wiḱpótih₁. All match the engine's cells.
- **Enclitics**: toy, moy, te, me, nos are in second position throughout.
- **Prohibitive**: mē + injunctive replaced ne + optative: gʷéh₂s, spéḱyes, spr̥néHs, sés, mléwHs, gʷʰn̥té (2pl). This
  is the inherited construction (Ved. mā́ + injunctive). Correct.

Second-pass totals: wrong 2 before (0017, 0023), 0 after. Minor 4 after the first fix round (0031, 0030, 0008, 0027);
0 after the second round (below).

## Second fix round (lead, before approval: every minor fixed at the source)

| record | minor | change |
|---|---|---|
| t102-0031 | h₁éysōm "their king": the only plural antecedent is the horses | POSS → gʰóstis PL: gʰostéyōm h₃rēǵés skéytom sléh₂gʷm̥, English "But I took the shield of the strangers' king." póyḱos is at its cap of 7; gʰóstis is now at 5 |
| t102-0030 | "I did not mean it" for weḱ- "want" | English → "I did not want it." The PIE is unchanged (tód ne wéḱm̥) |
| t102-0027 | two enclitic moy in one clause came out as one, so "my spear" had no token of its own | second POSS dropped; English → "Then my brother will carry the spear." (nu moy bʰréh₂tēr gʷéru bʰérēti) |
| t102-0023 | the same collapse, which my first fix created ("our father … our lord" gave one nos) | second POSS dropped; English → "Our father followed the lord all his life." The lord is "our lord" in the turn before. wiḱpótis stays at 21 (cap 21) |
| t102-0008 | sn̥gʷént "fell" | **withdrawn, no change**: the gloss is "fall down, go under, sink" and the English says "fell". My note ("were killed") read more into it than either text says |

Re-realized with the same command: 40/40 realized, all exact, max_lexeme_uses 7, theme_core ≤ 21, formula_uses 4, and the
same 5 deliberate WARNs. **Gate: PASS.**

**Counts.** Real packet items judged wrong: 3/20 as scored; after review and fixes, 0. Second pass: wrong 2 → 0, minor
4 → 0 (3 fixed, 1 withdrawn). Packet minors (3: two project reconstructions, which are allowed, and m. "cattle") are
accepted as they stand.

## Fixes at source

`data/generation/plans/t102.jsonl`:
- t102-0017, clause 2: anaphoric_i gender m → n (h₁íd ne h₂élgʷʰoh₂).
- t102-0023, "Our father followed our lord all his life": anaphoric_i OBJ → pie-lex-wikjpotis + POSS closed:personal/1
  PL enclitic (ph₂tḗr nos wiḱpótim h₂óyu sékʷeto).

Re-realized with `scripts/realize_plans.py data/generation/plans/t102.jsonl --batch t102 --model claude-opus-5-5
--prompt-id tier3-dialogue-inworld-v1`: 40/40 realized, all exact, reject 0.0, max_lexeme_uses 7, theme_core ≤ 21,
formula_uses 4, 5 WARNs (the deliberate set). **Gate: PASS.** The release approval was not touched (status pending).

## Engine and data notes (report only)

1. **Two tables disagree on the f. dual of "two"**: `closed:numerals/2` (fn: dwóyh₁, Ringe) and `pie-lex-dwoh1`
   (f.: dwéh₂h₁ / dwéh₂ih₁). The engine uses the closed table, which is defensible, but two sources for one fact break
   the single-source rule. Choose one, or record the other as an alternative.
2. **Two enclitic possessives of the same person in one clause come out as a single clitic.** 0027 "my brother will
   carry my spear" gives nu moy bʰréh₂tēr gʷéru bʰérēti; 0023 now gives ph₂tḗr nos wiḱpótim. One Wackernagel clitic can
   stand for both, but the engine does not say so: no token flag, and the gloss shows only one POSS. Worth a flag or a WARN.
3. In the scratch run with batch name `t102-revscratch`, the theme-core cap was not applied (FAIL on max_lexeme_uses).
   The cap is keyed to the batch name, which is expected. The scratch outputs, including
   data/generation/releases/t102-revscratch.json, were deleted.
