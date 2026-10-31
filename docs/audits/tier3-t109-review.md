# Tier 3 batch t109 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on the sky and the reckoning of time (stars on a night watch, the moon
counting months, nights until the full moon, dawn and the sun's path, when winter ends, counting a child's winters,
the year's feasts, an old man who remembers many winters), `tier3-dialogue-inworld-v1`. Reviewer: a calibrated
agent review following docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t109 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items from the `pie` field only, done before any English was printed:
   `docs/audits/packets/t109-blind-translations.jsonl`.
3. Every suspect packet form was looked up in a reverse index over `Lexicon.cells()` and the closed class.
   Doubtful senses were checked against the full glosses (`Lexicon.meaning`). The verdicts were written and saved
   before corpus/ or the plans were opened: `docs/audits/packets/t109-verdicts.jsonl`, sha256
   `f33ee5b43b1ebd7903f78a8c3be391f5a53f44d932e79b619519a6136c118a15`.
4. Ran `resolve_review_items.py t109`, then `score_review.py t109`.
5. Second pass: all 40 plans and records were read in full against planner-brief-v4 and the in-world dialogue
   brief. Speakers (two, user first, a new speaker starts a new sentence), per-sentence English (present on every
   sentence-initial clause and joining exactly to the plan English), and the 4–14 clause and 2–8 turn limits were
   also checked by script over all 40 plans. All passed.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong | 2/20 (both fixed, so 0/20 after the fixes) |
| real items judged minor (as scored) | 2/20 (both withdrawn below) |

Plants caught (in the packet's spelling):
- snúsōs: VOC.PL for one daughter-in-law. VOC.SG snúse is needed, and the record has it.
- h₁élh₂etes: SBJV.2DU/3DU for "let us drive the sheep". 1PL h₁élh₂omes is needed, and the record has it.
- memn̥tóm: IMP.2DU for "remember me, son". 2SG memn̥dʰí is needed, and the record has it.
- ǵʰéymn̥h₂: NOM.PL "winters" for "why is the winter cold?". NOM.SG ǵʰéymn̥ is needed, and the record has it.
- wédʰētes: SBJV.2DU/3DU for "when will a man lead me home?". 3SG wédʰēti is needed, and the record has it.

## Real wrong items and fixes

| item | record | finding | fix (plan) |
|---|---|---|---|
| ea681b61 | t3-t109-00007 | déh₃ete SBJV.2PL "what will you give to the gods?", said to one friend (VOC príHe; later gʷm̥dʰí 2SG) | clause 5 verb num PL→SG: now déh₃esi |
| 13802d2e | t3-t109-00020 | English "Good." has no PIE counterpart (PIE and English differ) | "Good." removed from clause 8 and the plan English |

## Real minors (withdrawn)

- 2a517f1d / t3-t109-00012 h₁n̥dʰént (AOR) for "the stars come forth", and 3c00ca47 / t3-t109-00004 séngʷt (AOR) for
  "it sinks under the earth". Both verbs (h₁nédʰt, séngʷt) have only aorist cells, so the gnomic aorist is what
  planner-brief rule 8 prescribes. Withdrawn.

## Second pass (all 40 records)

Found and fixed beyond the packet:
- t3-t109-00009 "It is far away, in the west": wékʷsperos is glossed 'evening' only, so "west" stretched the sense.
  The LOC slot was dropped and the English is now "It is far away." (minor)
- t3-t109-00018 "What did you eat?" (h₁édti) was answered "We ate…" with a different lexeme, h₂éḱh₃t. Rule 13 asks
  that an answer repeat the question's verb. Changed to h₁édti PST 1PL: h₁édme. (minor)

Checked and found correct:
- **Numerals:** septḿ̥, tísrn̥s/tréyes, pénkʷe, swéḱs, déḱm̥, ḱm̥tóm, h₁óyneh₂i "one" and pr̥h₂wós "first" all
  match their English. Fem. tísrn̥s goes with nókʷts, sémeh₂ and ǵʰéyōm, which is feminine in the lexicon; masc.
  tréyes méh₁nses. 'Two' occurs only as dwóh₁ méh₁nsh₁e ACC.DU, which is not an oblique case. No English number is
  missing from the PIE.
- **kʷóti / "has seen or lived N winters":** the PRF dedórḱe ("have seen") and the PRS gʷíh₃weti with an accusative
  of duration ("has lived") both match their English.
- **solh₂wós:** used only in t3-t109-00012, as solh₂wóns ACC.PL m "them all" (the stars, masc.). It agrees.
- **Sky words:** dyḗws ('sky, heaven; sky god, Dyeus') is a plain noun in 6 records (dyéwi, diwés "from the sky",
  "the sky was red") and the deity in 5 (Sky the father, daughter of Sky, "sing to Sky"). h₂éwsōs ('dawn; goddess
  of dawn') is the plain noun in t3-t109-00004, 00008, 00025 and the goddess in 00013 and 00040. h₂ewsér ('toward
  dawn, east; at dawn') means "at dawn" or "in the east". léwks 'light' and nébʰos 'cloud' (nébʰesh₂ NOM.PL with a
  sg. verb) are correct. mḗh₁n̥s 'month; moon' is masc. (pronoun "him") and lówksneh₂ 'moon' is fem. ("she").
  Each record uses one or the other consistently.
- **Pronoun WARNs (7):** tód/ḱód in 0001, 0006, 0022, 0023, 0039 point back to a statement. h₂éǵt in 0011 is 'said'
  (the WARN is a one-letter look-alike of h₂éǵet 'was driving'). In 0036, tóy n.DU "both" covers a sheep (f.) and
  milk (n.); the neuter for mixed genders is defensible. All seven are fine.
- **Fearing:** bʰebʰóyh₂h₂e + wĺ̥kʷoybʰos ABL.PL (0011). The other fear verbs have no object.
- **Formulas (5 records counted):** swift horses and wheel of the sun (0004), Dawn daughter of Sky (0013, 0040),
  Father Sky dyḗm ph₂térm̥ (0031): each is used in its sense. **0017 "Mother Earth" is a false positive.** The
  record has méh₂ter as a VOC ("Mother, when was I born?") and dʰǵʰémi "on the earth", which is no formula, so the
  real count is 4 records.
- **h₂élyos:** not used.
- **Predicate adjectives with dropped subjects** agree with their referents: pl̥h₁nós m. (the moon), dweh₂rós m.
  (the village), h₂yuHn̥ḱéh₂ f. (Dawn, daughter, woman), priHós/h₁wésus m. (guest/host), albʰós HeHḱús m. (the star),
  sényos n. (the tree, 0033).
- **Short-answer cases:** ACC for "Two moons", "Three nights", "Six winters", "A bull and sweet mead", "Into the
  river", "To the far field" and "Those seven stars". LOC for "And in summer?". NOM for the name and the
  exclamation. All correct.
- **Athematic obliques:** h₃rēǵés, dómn̥s, ǵʰiméns/ǵʰiméni/ǵʰimń̥su, yéh₁n̥s/yéh₁ni, sh₂wéns, méh₁nsi, h₂usés,
  diwés/diwéy, dréws, sh₁snés/sh₁séni, poh₂imnés and h₂str̥bʰós are all correct.
- **Enclitics:** moy/toy/nos/me/te are in second position everywhere, after a question word, nu, or the first
  constituent. A vocative counts as outside the clause.
- **Register:** nothing modern. The project reconstructions (h₂énHos, spélom, mógʰus, gʷʰermós) are allowed. Every
  turn answers the one before it.

## Blind back-translation agreement

84c3514b agreed fully, and 43815c92 agreed apart from the planted form. Four items differed by one word each:
- In 2a517f1d and 5aaa0874 the reader took h₂énHos for "grandfather". It is the project word for "grandmother".
- In 9d07d46c h₃réǵ was read as a genitive. It is the vocative "King".
- In 13802d2e h₂éwh₂e ménesi was read as "what did you have in mind". It means "Uncle, why are you waiting".
None of these readings is a defect in the PIE. The reader did not notice that "Good." was missing.

## Engine and brief notes (report only)

- `_formula_uses` counts a record whenever all of a formula's lexemes occur anywhere in it, so 0017 counts as
  "Mother Earth" with no formula in the text. Requiring the formula's syntax (head plus MOD, APPOS or POSS) would
  fix this.
- tr̥yóHom (GEN.PL of 'three', 0010) spells the first syllable as r̥. The handbooks write *tri-óHom (Lat. trium,
  Gk τριῶν). This is a notation minor in the closed class.

## Result

After the fixes, re-realized with `realize_plans.py data/generation/plans/t109.jsonl --batch t109 --model
claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`. 40/40 realized, exact_pass 40, reject 0. Five lexemes are
at the cap of 7 (no edit added a use). 7 WARNs (the same seven, all judged fine). **Gate PASS.**

Release-rule inputs: plant recall 5/5. Real items wrong 2/20 before the fixes and 0/20 after. Gate PASS.
