# Tier 3 batch t101 review (river dialogues: ford, boat, nets and weirs, trade, flood, a child in the water, offerings)

Reviewer: calibrated review per `docs/generation/reviewer-brief.md` (review-v1), 2026-10-31.
Packet: `make_review_packet.py t101 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).

## Procedure

1. Blind back-translation of 6 items (ab9ca866, 6600fc69, d6056f07, 29aed314, 07c8af89, 55e329c9), done
   from the `pie` field alone before any English was printed: `docs/audits/packets/t101-blind-translations.jsonl`.
2. Verdicts written before opening `corpus/` or the plans: `docs/audits/packets/t101-verdicts.jsonl`,
   **sha256 `940ce121500d8afcf4d539a9994997a29223b671bf1d40057b06fb368bb50fca`**. Each word was checked against
   `Lexicon.cells()` through a reverse form index (scratch script; no corpus access).
3. `resolve_review_items.py t101`, then `score_review.py t101`.
4. Second pass: all 40 records read sentence by sentence (speaker, per-sentence English, tokens) against
   planner-brief-v4 and the in-world dialogue brief.

## Score

| | |
|---|---|
| plant recall | **5/5** (4 named the planted word) |
| Tier 1 judged wrong | 0/3 |
| real items wrong (before fixes) | 1/20 (0.05) |
| real items minor (before fixes) | 1/20 |
| real items wrong / minor after fixes | 0/20 / 0/20 (the minor was withdrawn after the record check, not fixed; the verdicts file and the calibration still count it) |

The four named plants: góleti for 'I am freezing' (ab9ca866), méh₂tern̥s ACC.PL for 'my mother' (22d5220f),
h₁édme 1PL for 'she ate' (d6056f07), méh₂teres NOM.PL for 'your mother' (55e329c9). The fifth (2508c38a) was
flagged **minor for a different reason**: a turn that does not answer the one before. That issue is real and is
fixed below. The planted word was not identified, so the recall on that item was luck.

## Blind back-translation agreement

5 of 6 agree in substance. Misses, all lexical rather than grammatical:
- 6600fc69: n̥bʰtéwey / nébʰtus read as an unclear recipient. It is the water deity, and the English says so.
- d6056f07: sn̥h₂ént read as 'stood' (homophone of the senh₂- 'catch' aorist); gʰrémont read as 'grumbled'.
  The English 'grew angry' is in the gloss.
- 07c8af89: póyḱōs read as 'fish/fishers'. It is 'enemies'.
- 29aed314: tl̥h₂tóm left uncertain (see R27 below).
- ab9ca866: góleti translated 'scolds?', which is consistent with the planted person error.

## Real items flagged in the packet

- **411ec685 = t3-t101-00020, wrong.** woǵʰéye / woǵʰéyōh₂ (gloss 'cause to bring, transport', the brief's own
  example of a causative-only gloss) is used for plain 'Bring me gold from the trade!' / 'I will bring you gold'.
  **Fix:** pie-lex-h1opeyeti ('make reach; give') → h₂éh₂usom moy wesṓd **h₁opéye**; príHa toy h₂éh₂usom
  **h₁opéyōh₂**. bʰereti would have put that lexeme over the cap of 8.
- **8391c5d5 = t3-t101-00034, minor, withdrawn.** h₁uséwih₂ (FEM) 'may you be fortunate'. The record shows that
  the speaker is the ox-driver (user) wishing the cow's owner (model) well. The model's sex is never stated, and
  the plan sets `gender: f` on purpose. This is not an error.

## Second pass over all 40 records

Before fixes: **2 wrong and 1 minor**, all fixed. After fixes: 0 and 0.

- **t3-t101-00020, wrong:** the causative above.
- **t3-t101-00039, wrong (a turn that does not answer the one before).** The boatman says "Give me copper."; the
  warrior replies "Do not rock it!" and never answers the demand. The pronoun h₁íh₂m̥ also had no antecedent
  within reach (WARN). **Fix:** the user's clause is replaced, not supplemented, by the answer "I will give you
  copper." (h₂éyos toy déh₃oh₂, AOR SBJV 1SG). The record stays at 14 clauses, the in-world brief's maximum; an
  inserted clause would have made 15. The boatman's "Be silent, bold one: here the current is strong" still
  follows. A final check over all 40 plans: 4–14 clauses, 2–8 turns, and the per-sentence English joins exactly
  to `plan.english`.
- **t3-t101-00027, minor (sense and archaism of tl̥h₂tóm).** The lexicon glosses it 'bridge, ford', but 'bridge'
  rests on Balto-Slavic alone (Lith. tiltas, Latv. tilts). The Sanskrit tīrthá listed beside it is usually derived
  from *terh₂- 'cross', not *telh₂-. The English "Go down to the bridge, and walk on the thick ice" also reads
  oddly. **Fix:** pie-lex-pertus 'crossing' (Av. pərətu-, Lat. portus) → **pértum** ní gʷh₂dʰí …; the English is
  now "Go down to the crossing, and walk on the thick ice."

Checked and found correct:
- **Speakers and English:** every sentence has a speaker and its own English. Both speakers belong to the world
  (child, wife, neighbour, trader, stranger, elder), nothing in them is modern, and nothing is coined. The
  project reconstructions h₂énHos, spélom, mógʰus and gʷʰermós are allowed for Tier 3.
- **Requests (7):** 'how do I say' ×2 (R10, R40) plus tell a story (R11), teach me to swim (R09), sing a hymn
  (R33), show me how you weave (R32) and 'what is an otter?' (R24). All 7 stay in-world. In both 'how do I say'
  dialogues a stranger asks a local how to phrase a request to a ferryman or to fishwives, and the local answers
  in the situation ("Say this to my brother: he has a boat"; "Say that, and they will give you the fattest fish").
  Neither is a lesson about the language.
- **Pronoun WARNs (12):** all false positives.
  - Impersonal h₂wérst / góleti next to a VOC: 0004, 0027, 0038.
  - Antecedents two or more clauses back but unambiguous: 0005 ×2 (the son).
  - Cataphoric ḱód / tód 'this/that' introducing the quoted phrase: 0010 ×2, 0013, 0040 ×3.
  - tṓys (n PL) for grain and honey, both neuter: 0020.
- **Senses checked against full glosses:**
  - dʰgʷʰh₂wé 'almost reach' covers "we have almost reached the land".
  - troméyeti / tréseti 'tremble (in fear)'; ḱubʰrós 'pure, clean' (for salt) and 'pretty'.
  - h₂éwh₂os 'maternal grandfather; maternal uncle'; plowéyeti 'float'; Hyowdʰéyeti 'cause to move' (rock the
    boat, move the feet); dʰoréyeti 'hold, keep'; h₂éyeri 'tomorrow' (the idioms.json paraphrase).
  - sokʷéyeti 'say' (the brief's own plain-sense causative); h₁opéyeti 'give, make reach'.
- **Paraphrases:**
  - shore = "toward the land" dʰéǵʰōm próti; flood = "the river has grown great" Hwérdʰt.
  - weir = stakes (steh₂urós) with branches bound between them, and the fish "come into the fence" gʰórdʰom.
  - drown = "died in the water" wédni mért; "the other side" = h₂én.
  - No oar, reed or island occurs (rowing is the verb h₁erh₁-).
- **Fearing with the ablative:** wédn̥s (R09), ḱwn̥bʰós (R15, R24), déh₂nus (R28, R34, R35), h₁ésmōd and kʷosmōd
  (R39).
- **Cows:** gʷṓws has `gender: f` in R06 and R34, with tā́m / séh₂. The herd in R04 (gʷówes … tóns) is mixed
  cattle, so the masculine is acceptable.
- **h₂élyos agrees with its noun or gender:** h₂élyōs wiHrṓs, h₂élyons (cords, m).
- **Predicate adjectives with dropped subjects** agree with the addressee: ḱéyweh₂ to the woman (R01), ḱéywos to
  the man and to the young man (R05, R16), ǵn̥h₃réh₂ to the grandmother (R27), dʰr̥sús to the brother (R09).
- **Short answers take the right case:** ACC in R08, R20, R30, R38 and R04 (goal); NOM in R19 and R39.
- **Athematic obliques:**
  - pérwr̥ → pr̥wéni; sréwmn̥ → sruméni, sruméns; sh₂éymn̥ → sh₂iménh₁; térmn̥ ACC.
  - h₂ḱméni, kl̥Héni, bʰudʰméni, ph₂wéni / ph₂wénh₁, wédni / wédn̥s / wédn̥h₁, bʰr̥h₁wéns.
- **Enclitics:** moy, toy, nos, wos, me and te all stand in second position.

## Gate

Final run: `realize_plans.py data/generation/plans/t101.jsonl --batch t101 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`. Result: 40/40 realized, all exact, max_lexeme_uses 8 (cap 8), theme core within cap,
theme_core_uses<=23 met, 12 WARNs (all false positives, above), **gate PASS**. The first re-run with bʰereti in R20 failed the lexeme cap
(9), which is why R20 uses h₁opéyeti.

## For the lead (lexicon and engine, report only)

1. **pie-lex-tlh2tom** 'bridge, ford': the Wiktionary tree file puts Skt tīrthá under *telh₂- next to Baltic
   tiltas. The usual etymology derives tīrthá from *terh₂-, which leaves 'bridge' with one branch. Consider
   marking it one-branch, or glossing it 'plank bridge (Baltic)'.
2. **WARN heuristics:** impersonal weather verbs next to a VOC, and cataphoric ḱód / tód ("how do I say *this*?"),
   make up 9 of the 12 WARNs. Exempting them would make the remaining WARNs worth reading.
3. **woǵʰéyeti** keeps being picked for plain 'bring'. A slice-time note ("causative only: use bʰéreti or
   h₁opéyeti") would stop this at the plan.

Not done: no corpus file was edited by hand, the release approval was not set, and nothing was committed.
