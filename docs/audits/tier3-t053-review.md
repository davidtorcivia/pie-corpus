# Tier 3 review: t053 (family and wedding, 40 in-world dialogues)

Reviewer: claude-opus-5-5, brief `review-v1` (docs/generation/reviewer-brief.md), 2026-10-31.

I re-realized the batch once at the start, so the records include today's engine fixes (a "?" when any clause has
`question`; check_plan rejects 'two' in an oblique case). Run: 40/40 realized, exact 40, reject 0.0, gate PASS.

## Packet and calibration

- Packet: `scripts/make_review_packet.py t053 --n 20 --plants 5 --tier1 3` → 28 items (20 real, 5 planted, 3 Tier 1).
- Blind back-translation of 6 items (1652a5d7, 23db7b4b, e231eff9, c675324a, 3650527e, 42ca23d1), done from the
  `pie` field alone before any English was seen: `docs/audits/packets/t053-blind-translations.jsonl`.
- Verdicts: `docs/audits/packets/t053-verdicts.jsonl`, sha256
  `7828f9a3e08b2d95aab252b7ecad4ad7a5b1e4ff8144e9fc3f78d938f78cc2c7`. Saved before corpus/ or the plans were opened.
- Score (`scripts/score_review.py t053`): **plant recall 5/5** (all five named); real items judged wrong 0/20,
  minor 4/20; Tier 1 items judged wrong 0/3.

Plants caught (in the packet's spelling):
| item | planted form | what is wrong |
|---|---|---|
| f7f76bc4 | wíHrōs | vocative plural for the nominative singular subject wiHrós |
| 23db7b4b | somHṓy | dative masc. singular for the feminine predicate somHéh₂ ("you will not be alone, mother") |
| 8724e70b | h₂ówih₁ | dual for plural h₂óweyes ("how many sheep") |
| ff836c8e | mówdoysu | locative plural "in joys" for the exclamation mówdos "Joy!" |
| e3231cae | wĺ̥kʷoybʰos | dative/ablative plural for the nominative subject wĺ̥kʷos |

Blind translation agreement: all 6 match the English in sense. Speaker turns were reconstructed correctly in 5 of 6.
Places where I hesitated: 42ca23d1 h₂énkuleh₂, which I read as "ring" (the lexicon has "belt"); e231eff9 h₂Hséh₂s
"of the hearth"; 23db7b4b góleti, which I read as "grows cold" (English "is cold").

Real items marked minor in the packet, with what the second pass found:
- c675324a (t3-t053-00003): n̥smé h₁entér "between us" is plural, but the two brothers use dual verbs elsewhere.
  **Fixed:** the pronoun slot is now `num: DU`, giving n̥h₃mé h₁entér.
- 3650527e (t3-t053-00032): wésth₂e "you were wearing", MID.PST.2SG of wéstor. The ending is the engine's middle
  secondary 2sg (-th₂e). Engine note only.
- e88100bf (t3-t053-00036): **withdrawn.** With the speakers known, the teasing makes sense: the married brother
  threatens to tell the shepherd's daughter that the *user* loves her.
- 1d90172e (t3-t053-00029): **withdrawn.** The lexicon glosses éti (`pie-lex-eti-2`) as "beyond, over".
- 3982de25 (Tier 1, Byrd's "King and God"): h₃réḱs used as a possessor. This is the Tier 1 source text; no action.

## Second pass: all 40 records

I read every record sentence by sentence, with its speaker, English and token glosses, against planner-brief-v4 and
the in-world dialogue brief (top part).

**Wrong (1, fixed):**
- t053-0015 "If you are dear to him, he will love you." The mother says this to her daughter, but the predicate came
  out masculine (h₁ésmey **ḱéywos** h₁ésesi). The clause drops its subject and has no vocative, so the adjective took
  the default gender. **Fix:** `gender: "f"` on the PRED slot → ḱéyweh₂.

**Minor, left as they are:**
- t053-0013 péh₂ure "little one": péh₂uros "small, little" used as a vocative noun. A stretched sense.
- t053-0016 "I have come home safe": the "safe" comes only from the sense of *nes-. "Herded" is péh₂s- "guard".
  "Your sister has run to him" uses a bare accusative of a person as the goal (h₁ím drémt).
- t053-0024 "the name Of-Good-Fame": the name h₁suḱléwesm̥ is masc. ACC in apposition to neuter h₁nómn̥.
  Defensible, since the name is the person's.
- t053-0028 "I too became afraid": -ge "indeed" stands for "too".
- t053-0031 "I fell into the water": séngʷt is glossed "fall down, go under, sink", so this is acceptable.
- t053-0032 wésth₂e (above).

**Checks that passed:**
- In-world: nothing modern and no coinages. pie-proj spélom, mógʰus, pṓlHos, h₂énHos and réydʰ- are project
  reconstructions, which the brief allows.
- Every turn answers the one before. Exactly two speakers in each dialogue, the user first. Speakers and per-sentence
  English are correct throughout.
- Pronouns: I checked every he/she/it/them, including the 12 engine "no referent nearby" warnings. All point to the
  right antecedent: father vs. daughter, the belt (f), meat and barley (n. pl.), the child (n), and the fire as "him".
- Kinship r-stems in the oblique cases are right: méh₂tr̥s, ph₂trés, dʰugh₂tréy, bʰréh₂tr̥bʰis, ǵn̥h₁tryéh₂s.
- Verbs of fearing take the ablative: wĺ̥kʷōd, ǵn̥h₁tryéh₂s, h₁ésyeh₂s (troméye- "tremble"), déms, wédn̥s.
- Causatives are used only where they are meant: woséye- "clothe" (MID "put on"), sodéye- "seat",
  h₁opéye- "give (in marriage)". troméye- is glossed "tremble".
- h₁áyt: active "give" (0006 "my brother will give the horse"), middle "take, receive" (0026, 0027, 0035).
- Missing words written around:
  - bride: pótnih₂ / néweh₂ pótnih₂.
  - wedding: wédʰ- "lead home, marry", plus the procession h₂éǵmn̥.
  - mother-in-law: "his mother" / "our mother", ǵénh₁trih₂.
  - weep: "tears flow from my eyes" (0028), HréwdH- "cry out" (0038).
  In each case the PIE says what the English says.
- Enclitics stand in second position. Every question ends in "?".

## Counts

| | before fixes | after fixes |
|---|---|---|
| packet real items wrong | 0/20 | 0/20 |
| packet real items minor | 4/20 | 1/20 (wésth₂e; one fixed, two withdrawn) |
| second pass, all 40 records: wrong | 1 (0015) | 0 |
| second pass, all 40 records: minor | 7 | 6 |

Procedure violations: none. data/audits/ was never opened. The verdicts were saved and hashed before corpus/ or the
plans were opened, and the packet was never diffed against the corpus. I did see record ids in the realizer's
warnings at the first re-realize, but those don't link packet items to records.

Final re-realize, after editing plans t053-0003 and t053-0015: 40/40, exact 40, reject 0.0, max lexeme uses 8,
**gate PASS**.

## Engine and brief notes (report only)

1. **Predicate-adjective gender with pro-drop.** A 2nd-person PRED adjective in a clause with no SUBJ and no VOC
   defaults to masculine (0015). Clauses that had a vocative (0011, 0012) came out right. check_plan could warn
   when such a PRED has no `gender`, or the brief could require one.
2. **MID.PST.2SG -th₂e** (wésth₂e): this has the same shape as the perfect 2sg. Consider -th₂es.
3. **h₂énkuleh₂** is glossed "belt" in the lexicon (Wiktionary); its reflexes may point rather to "hook, ring".
   Worth a lexicon check.
