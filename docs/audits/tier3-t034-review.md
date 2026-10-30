# Tier 3 batch t034 review (review-v1, 2026-10-30)

Batch: 40 texts on the inherited dragon-slaying myth (14 myth, 13 dragon-slaying, 13 praise).
Procedure: docs/generation/reviewer-brief.md. Packet: `make_review_packet.py t034 --n 20 --plants 5 --tier1 3`
(28 items: 20 real, 5 planted, 3 Tier 1). I did not read anything under data/audits/.

## Order of work and hashes
1. Packet made. I printed only the `pie` fields, then wrote a blind back-translation of 6 items:
   `docs/audits/packets/t034-blind-translations.jsonl` (sha256 `6a5cd11624cb1f7b9d6575a8bd8aa1e956916cad537adc2192de8273fb6a8cad`).
2. Then I read the English and wrote the verdicts, `docs/audits/packets/t034-verdicts.jsonl`.
   **sha256 `688e9771755529dfc1144e42d5ddeb7eddb039d91ca711a62d146b8229202e50`**. It was saved before I opened corpus/ or the plans.
   I checked doubtful forms with a reverse index over `Lexicon.load().cells()` and closed_class.json. Every token in the 25 Tier 3 items is a cell the engine builds, so all the errors are wrong-cell or sense errors.
3. `resolve_review_items.py t034`, then `score_review.py t034`.

## Calibration (score_review.py)
| measure | value |
|---|---|
| plant recall | **3/5 (0.6)**: 3 caught, 2 named exactly |
| Tier 1 judged wrong | 0/3 |
| real items wrong | 1/20 (0.05; upper bound 0.083) |
| real items minor | 4/20 |

Plants caught: d04fe301 (pérkʷunoybʰos DAT/ABL.PL used for the vocative, named), 5687fb5f (ḱlutóybʰos DAT/INS.PL modifying ACC.SG h₁nómn̥, named), and 3786282b (flagged minor for other reasons; the plant was ph₂tḗr NOM for ACC ph₂térm̥ after prḗḱst, which I missed).
Two plants were missed outright. After the verdicts were frozen, reading t034-00035 for the second pass showed one of them: cdd9eef8 had LOC déh₂newi for GOAL déh₂nu ("drove his horses to the river"). I had passed it as a dative of direction. The fifth plant is unknown to me. **Recall is below the 4/5 release threshold.**

## Blind back-translation agreement
5 of the 6 items agree in substance (a704590d, 88633508, fed62024, 152a65d6, and c0cd2694 apart from one word):
- c0cd2694: I read h₂éyeri as "in spring"; the English has "early".
- 3786282b: I read `wédōr h₂ew gʷm̥sḱéti` as "the water comes down"; the English has "It comes back to the waters". This is the same h₂ew sense question as the minor verdict below.
- 152a65d6: I misread h₁éymos (DAT.PL "to them").
- 88633508: I did not know h₂r̥Hmós "arm".

## Real items: wrong
- **dee92a79 = t3-t034-00020** (number). The PIE had kʷékʷlons, yugéh₂ (ACC.PL, in apposition to plural déh₃reh₂), so it said "wheels and yokes". The English says "a wheel and a yoke".
  - Fix: the engine forces an APPOS to take its head's number, and a first attempt with SG appositions was rejected. Instead, déh₃rom was dropped and kʷékʷlos and yugom became singular OBJ.
  - New PIE: `h₁ésmey-kʷe kʷékʷlom yugóm-kʷe dh₃ént`. New English: "and gave him a wheel and a yoke."

## Real items: minor
- c0cd2694 = 00026: I objected to h₁ím ("him") against the English "sang of it". Fixed in the English ("sang of him", meaning the god).
  My second objection was wrong: h₁íh₂ correctly resumes wédōr, the collective plural of wódr̥ (plan num PL).
- c23f0081 = 00033 (praise): the addressee shifted. Dawn was 3rd person, then 2pl to the audience, then a 2sg vocative to Dawn.
  Fixed: the last line is now a 3rd-person optative, `nu nos h₂éwsōs h₁wésuh₂ bʰéroyh₁t` "May Dawn bring us good things now!", 8 syllables.
- 6ec9b32c = 00012 (praise): the god was "he" (moréyet, spért) and then "you" (ḱludʰí …). Fixed to 2sg throughout:
  `tébʰye néwom h₁erkʷóm gʷéHyoh₂. h₁ógʷʰim-ge h₂ḱm̥néh₁ moréyes. nu dʰǵʰmés h₁ludʰíbʰos wédōr spérs.` All lines still scan.
- 4ed2edbc = 00010: bʰérǵʰontm̥ (masc) agrees with pérkʷum "oak". The engine's gender for pie-lex-perkus is m; PIE *pérkʷus is usually reconstructed feminine (Lat. quercus f.). **Engine/lexicon question, reported only.**

## Second pass: all 40 records against planner-brief-v4
- **Modern or coined:** none. pie-proj-spelom "story" (4 uses) is a flagged project reconstruction, which the brief allows.
- **Myth coherence:** coherent in every record. The slayer is always the god (Perkʷunos / gʰrómosyo dʰéh₁s / bʰágos) or a named hero (h₁suḱléwēs, h₂nr̥ménēs, deywóḱlewēs, h₁wesuḱléwēs, h₁sn̥tyóḱlewēs, h₁suh₁éḱwos), and the serpent, beast or enemy is always the one slain. 00037 (gods choose Perkʷunos, Father Sky sends his son) and 00010 (Father Sky makes the stone that returns to the hand) agree with each other.
- **Formulas:** *gʷʰen- h₁ógʷʰim* (00001, 00003, 00004, 00024, 00026, 00028, 00030) and *ḱléwos ń̥dʰgʷʰitom* (00003, 00024, 00026) are used correctly. 23 formula uses in all.
- **Genre labels:** "dragon-slaying" is not a metered genre, but all 13 such records are third-person prose narratives with no hymnic address or praise frame. The label is honest, not a dodge of the meter gate. All 13 praise texts are metered and scan: 80/80 lines exact.
- **Verb senses:**
  - Causatives are used correctly: moréye- "kill", stoh₂éye- "set up", h₂sowséye- "make dry", dʰoréye- "hold".
  - troméye- is glossed "tremble (in fear)", so `mē troméyes` is acceptable.
  - The ablative with fearing is correct: h₁ésmōd trésont (00011), h₁ésmōd ne bʰebʰóyh₂h₂e (00013), twéd (00006).
  - lexq-sourced verbs (h₁néǵʰt "stab", h₂wégt "pierce", dʰégʷʰh₂t "come near", spért "free", h₁nédʰt "come forth", téwkt "strike", sésti "rest") match their glosses.
- **Further fixes in the plans:**
  - 00006 (praise): `téḱneh₂ … gʷíh₃weti lóygonti-kʷe`. The neuter plural subject took a singular verb and then a plural one. The second verb is now singular (lóygeti), and the line still scans.
  - 00008: "honored him" was ambiguous right after the dead worm. It is now deywóm "honored the god".
  - 00036 (praise): the god moved from 3rd to 2nd person. It now reads `h₁eǵóh₂ poh₂imḗn dʰéh₁s-kʷe te sepelyóh₂` "I praise you, god" (11 syllables) and `túH h₁íd sélǵs` "you set it free". The -kʷe on the vocative is a little awkward but grammatical.
  - English-only fixes: 00010 ("Take it", since no "this" is in the PIE) and 00015 ("out of the hollow of the rock", for péruns h₂ewlṓd).
- **Left as minor:**
  - 00022: h₂ew carries "back/again", a stretched sense of "away, off". `mē tréses pós h₂wérst` is aorist where the English has "rains".
  - 00010: tḗtḱt (PST "was creating") is rendered "made".
  - 00001: pro-drop sréwont is 3pl after collective wédōr.

## Counts before and after the fixes
- Real packet items wrong: 1/20 before, 0/20 after. Minor: 4 before, 1 after (00010 oak gender, an engine question).
- Whole batch (second pass): 1 wrong (00020), now fixed. Minor, fixed in the plans: 00006, 00008, 00012, 00026, 00033, 00036, plus English-only fixes in 00010 and 00015. Minor, left as is: 00001, 00010 (tḗtḱt "made"; oak gender), 00022.

## Gate
`realize_plans.py data/generation/plans/t034.jsonl --batch t034 --model claude-opus-5-5 --prompt-id tier3-planner-v4`:
- 40/40 realized, 0 rejects;
- meter_exact 80/80 (1.0);
- max_lexeme_uses 9 ≤ 9;
- formula_uses 23, words_per_record 38.9;
- **gate PASS**.

## Engine/brief findings (reported, not fixed)
1. **The lexeme cap sits on a knife edge.** The cap is derived from batch tokens (0.5% of 1713 gives 9). An intermediate fix that removed tokens dropped the total to 1663 tokens and the cap to 8. Five lexemes already at 9 then failed the gate (theme-core cap 26 → 25 also failed). A fix that shortens a text can therefore fail a batch for unrelated texts. Consider computing the cap from the initial run, or adding a margin.
2. pie-lex-perkus: gender m. The usual reconstruction is f. The headword "pérkus" also differs in labiovelar spelling from the realized form pérkʷum.
3. The APPOS head-number rule forbids "gifts: a wheel and a yoke" (singular appositions to a plural head). The rule is correct in general; I note it for planners.

The release approval is not set (the lead decides). Plant recall of 3/5 fails the ≥4/5 rule, so the batch should stay pending, or get a second calibrated review.
