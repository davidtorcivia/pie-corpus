# Tier-3 review: packet t033 (28 items)

The batch has 40 texts: dialogues, family narratives and wedding pieces (`tier3-planner-v4`, Sonnet planner, repair pass a full rewrite at about 48 words per text). The packet held 20 real items, 5 plants and 3 Tier 1 fable lines (`--n 20 --plants 5 --tier1 3`). The review used handbook knowledge only (Fortson, Beekes, Ringe, LIV², Mallory–Adams), with doubtful forms checked against `Lexicon.cells()`, `participle_cells()` and `closed_class.json` through a reverse index of every form to its cell.

## Procedure and blindness

- The blind back-translation (6 items: 615a7f36, 84628fcb, 8f183ccb, 0a6cd3e9, 1d5de31a, aff70d4a) was done from the `pie` field alone, before any English was printed: `docs/audits/packets/t033-blind-translations.jsonl`.
- The verdicts were written and saved before `corpus/tier3/` or the plans were opened: `docs/audits/packets/t033-verdicts.jsonl`, **sha256 `2c4a215e332059eca4b0708fd842f5e4b6ac731f248c19885a809a577863f165`**.
- The packet was never diffed against the corpus, and nothing under `data/audits/` was opened. Records were found only with `scripts/resolve_review_items.py t033`.

**Plant recall is therefore blind: 5/5 caught, 4/5 named.** The blind pass by itself already flagged two of them (the dual verbs in 615a7f36 and 1d5de31a).

## Counts (score_review.py)

| | ok | minor | wrong |
|---|---|---|---|
| real (20) | 11 | 8 | 1 |
| Tier 1 (3) | 0 | 3 | 0 |
| plants (5) | 0 | 2 | 3 |

Real items judged wrong: 1/20 (0.05) as saved. **After re-examination and fixes: 0/20.**

### Plants (5, all caught)

- 615a7f36: tóy séh₂etes, a masc. plural pronoun with a 2/3du verb.
- 972e1dfd: dayh₂wḗr mluHénti, a 3pl verb with a singular subject, among 3sg mléwHti.
- 1d5de31a: dyḗws kúdʰe h₁stés, a 2/3du 'be' with singular Sky.
- 9097f17e and 9fbf1626: flagged minor (the instrumental plural wih₁n̥bʰís, and tense drift in 9fbf1626).

### The one real "wrong", withdrawn on re-examination

- 0aab5d7f → t3-t033-00020: I graded `sérpet-kʷe h₁éy próti` as a nominative after an adposition. The plan shows h₁éy is the clause's SUBJ ("it", the wolf), which is correctly nominative, and próti is a bare adverb. The real defect is the English: "toward them" had no slot. **Fix:** a GOAL slot `demonstrative_so` DU m was added, so the clause now reads `sérpet-kʷe h₁éy tóh₁ próti`. The English "protect the sheep" also stood over the pronoun tā́s and became "protect them". The verdict file is left as saved (its hash is the calibration record). The plural tóybʰos/usméy for two brothers is the expected oblique dual (planner brief rule 17), not an error.

## Minor items (real)

- t3-t033-00027 (f42c6b50): "My body is strong" stood over the aorist Hwérdʰt. Now "has grown strong".
- t3-t033-00034 (3709770e): "the brother of the bride" stood over bare bʰréh₂tēr. POSS snusós added: "the daughter-in-law's brother".
- t3-t033-00029 (704f25b9): "Father Sky" stood over bare dyḗws, and "looked after them" had no object. Now "Sky" and "looked on".
- t3-t033-00010 (5b310cb7): "has heard" stood over present ḱl̥néwti, and "Father Sky" over dyḗws. Now "is listening to" and "Sky".
- t3-t033-00032 (bb732f97): "Hail" added before bare vocatives. Also, the guests were a second object of 'led' rather than the object of the participle 'listening' (now `dep`). mē + present for a prohibition is accepted.
- t3-t033-00019 (cd3e9e84): "crept toward us" had no "us". GOAL personal/1 PL added (ǵʰwḗr n̥smé próti).
- t3-t033-00037 (a1afa04e): "at the door" and "Hail" had no PIE, and "My body is strong" stood over an aorist. All three corrected.
- t3-t033-00033 (c429d61e): "mother" (no vocative in the PIE) and "Welcome/Hail" over bare vocatives. All three were dropped from the English (a VOC méh₂ter would exceed the theme-core cap).

The Tier 1 lines (Schleicher 1868 ×2, Lühr 2008) are faithful to their sources, but their notation clashes with the corpus (minor, as in t030–t032).

## English/plan sweep (brief rule 14): 49 mismatches fixed across 23 texts

All the lead-reported items are fixed:
- 24: OBJ kéh₂nmn̥ was added for "a song". The clause "the mother gave water" had no SUBJ, so the English now says "he" (the father, continuing). Adding SUBJ méh₂tēr would have put the theme-core lexeme over its cap of 32.
- 32, 33, 37: Hail/Welcome removed.
- 15: "the child/newborn" became "him". 31: "the woman" became "her".
- 22: "she was my desire" was a verbless clause, which can only be present. It is now a verbal clause with h₁ést (PST). "I built" over a present verb became PST démom (the verb has no aorist). "I trusted" over a perfect became "I trust".

Further drift found and fixed, in the plan when the meaning was intended and in the English otherwise:
- **Father Sky / Mother Earth over bare dyḗws/dʰéǵʰōm:** 10, 14, 23, 24, 29.
- **Pronouns or objects with no slot:**
  - "toward them" (20) and "toward us" (19): GOAL added.
  - "has reached my household" (2): GOAL personal/1 added ("has reached me"); adding ḱóymos would exceed the lexeme cap of 11.
  - "before me" (1), "with you" (23), "hear us" (30), "before them" (30), "give them love" (30), "to him" (14), "us" in "above us" (14): English changed.
- **Tense:** "is strong" over an aorist (27, 37) became "has grown strong", and "may your body be strong" (28) became "grow strong".
- **Senses:**
  - "sings" over mléwH- 'speak' (39) became "speaks".
  - "hymn" over h₁erkʷós (28) became "song of praise".
  - "exchange words" (2) became "speak words".
  - "the waters" over a singular (30) became "the water".
  - "under the tree" over a locative (7) became "by the tree".
  - "too" (5) and "And" (14) were dropped.
  - "the husband/the wife" over so/séh₂ (39) became "he/she".
  - "your father, and your mother" without POSS (27) became "remember father and mother".
  - "brother of the bride" (34, 35) became "daughter-in-law's brother".

## Padding

- **Text 28 (35-clause optative litany): cut.** Clauses 27–32 (the duck, dog, shepherd, cook, king and queen) are batch vocabulary with no link to the couple. They were removed from both the plan and the English (29 clauses remain). The apotropaic run on the fields and beasts (clauses 9–18) is a coherent Atharvaveda-style blessing and stays.
- **"Who is this? / This is my X" (8 texts): keep.** In each text it is 2–4 clauses long and fits the genre (introductions at a wedding or a visit). Across the batch, though, it is a stock filler. The planner brief should ask for at most one such block per batch. The block in text 37 (the husband's mother: "This is my brother, and this is my mother") is a non-sequitur, but it is grammatical and matches its English.

## Engine and brief findings (not fixed here)

- Adverbs/adpositions (próti) take no object. "Toward X" needs a separate GOAL slot. The planner often omitted that slot and wrote the pronoun only in the English.
- stérg- is glossed "protect~" (approximate) but is used batch-wide for "love" (Gk στέργω). The gloss should say "love, cherish".
- There is no 'sing' lexeme in the slice, so the planners write mléwH- 'speak' as "sing".
- The brief could state outright that a verbless (nominal) clause is present-only. Text 22 put "was" over one.

## Gate

Re-realized with `scripts/realize_plans.py data/generation/plans/t033.jsonl --batch t033 --model claude-sonnet-5-5 --prompt-id tier3-planner-v4`:
- 40/40 texts realized, 40 exact, 0 rejects. 48.1 words per text, 247 distinct lexemes, 144 roots, 18 formula uses.
- max_lexeme_uses 11 ≤ 11, theme_core ≤ 32, duplicates 0: all PASS.
- **The overall gate is FAIL, on one gate only: `meter_exact>=0.90` (0.11, 17 of 154 verse lines).** This gate was added to `scripts/realize_plans.py` and `pie/meter.py` at 21:47 today, during this review. My first re-run, before that change, showed no meter gate.
- No batch planned before this gate existed can pass it without a metrical rewrite. `wedding` is in `METERED_GENRES`, so every sentence of the 13 wedding texts counts, including their dialogue and narrative. That is the lead's call (narrow the gate's scope, or run a meter pass), so it is not attempted here.
- The 19 antecedent warnings are the expected cross-clause pronoun warnings: "them" for two people, and speech-initial pronouns.
