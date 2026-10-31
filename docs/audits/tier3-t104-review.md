# Tier 3 batch t104 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on contests and games (`tier3-dialogue-inworld-v1`): wrestling at a feast,
footraces, throwing the stone and the spear, prizes set out, a loser who says he was cheated, boys' games,
knucklebones ("the bones"), boasting and teasing. Reviewer: calibrated agent review following
docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t104 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items, from the `pie` field only, before any English was printed:
   `docs/audits/packets/t104-blind-translations.jsonl`.
3. Verdicts written and saved before corpus/ or the plans were opened:
   `docs/audits/packets/t104-verdicts.jsonl`, sha256
   `ae2b0ed48532f1d0b975c313a550c8f6c3bdc6a39ab6dc7a76141d5994b1d51a`.
4. `resolve_review_items.py t104`, then `score_review.py t104`. data/audits/ was not read.
5. Second pass: I read all 40 records in full against planner-brief-v4 and the in-world dialogue brief (top part),
   sentence by sentence, with the speaker and English for each sentence, the gloss of every token, `Lexicon.cells()`,
   the full glosses (`Lexicon.meaning`) and the 37 planner WARNs.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong | 0/20 |
| real items judged minor (as scored) | 1/20 |

Plants caught (packet spelling):
- 762387d5: h₁éy **ish₁réh₂s**? for "Is he strong?" (the foal). It is not a cell; it needs NOM.SG.M ish₁rós, as in the answer.
- 60dc1191: h₁ím-kʷe **Hyéh₁ketes** (SBJV.2DU/3DU) for "I will throw him" (1sg Hyéh₁koh₂).
- 1158eb97: **gʰostíbʰos** (DAT.PL "to the guests") with no subject, for "The stranger sings songs of wolves" (NOM.SG gʰóstis).
- b7cfd96a: toy **ḱéstroh₁** (INS.SG) as the subject of h₁ésti in "the villager's son has your knife" (NOM ḱéstrom).
- 0377688f: **sésetes**-kʷe (SBJV.2DU/3DU) for "and you will sleep" (2sg sésesi).

## Real packet items: minor findings

| packet item | record | finding | action |
|---|---|---|---|
| cde45152 | t3-t104-00009 | the arms are dual (h₂r̥Hmóh₁) in one turn, then ABL.PL h₂r̥Hmóybʰos in the reply | **withdrawn as an error**: only NOM/ACC/VOC dual exist, and the engine gives the plural form for an oblique dual (brief rule 17), so the surface is correct. The plan slot said `num: "PL"`; I set it to `"DU"` so the token features match the meaning. The PIE is unchanged |

Real items after review: **0/20 wrong, 0/20 minor.**

## Second pass (all 40 records)

**Fixed in the plan (data/generation/plans/t104.jsonl):**
- t104-0028 "Father Sky, hear me!": the enclitic me split the inherited vocative phrase (dyéw **me** ph₂ter ḱludʰí). The
  pronoun is now orthotonic: dyéw ph₂ter h₁mé ḱludʰí. Minor. The orthotonic form adds an emphasis ("hear *me*") that
  the English does not show. The lead may prefer to keep the enclitic.
- Natural pairs not in the dual (brief rule 17), minor: 0018 "your legs" skélesh₂ → skélesih₁; 0030 "your arms are
  growing" h₂r̥Hmṓs … bʰuHyónti → h₂r̥Hmóh₁ … bʰuHyétes (0001 and 0009 already have the dual h₂r̥Hmóh₁); 0023 "we
  were playing" (two brothers) lóygome → lóygowe.
- One `english` value for two English sentences over one PIE sentence, minor: 0032 "I heard you! You are lying in the
  grass." and 0038 "Run away! The old man is angry." Each second clause now has `break` and its own `english`, so
  `align_english` pairs them one to one (ḱlḗm te. gʰr̥h₁méni légʰyesi.; dr̥h₂dʰí. ǵérh₂onts gʰrémeti.).
- t104-0009 clause 4: `num` PL → DU on the arms (see above). The surface is unchanged.

Second pass: 0 wrong and 6 minor before the fixes (counting each record once: 0018, 0023, 0028, 0030, 0032, 0038);
0 wrong and 0 minor after.

**Checked, with no error found:**
- **Speakers and English:** every sentence has a speaker, user first, two speakers. The English of each sentence matches
  its PIE, and every turn answers the one before. Nothing modern or coined appears (the wool "bag" that is kicked in
  0031 is bʰólǵʰis, a skin bag).
- **Pronouns (37 WARNs):** I checked all of them. Each default masculine fits a male speaker or a masculine referent
  (the foal, the arm, the prize misdʰós, the bag, the stone h₂éḱmō). Each "VOC near" verb is a true 3rd person (the
  spear fell, it lies in the river, "it is getting dark"). Each distant antecedent resolves (h₁íns = the horses in
  0012, the boys in 0019; tód = the act). Every record with a woman or girl sets feminine agreement where needed:
  0008 péh₂ureh₂/dʰr̥séwih₂/pr̥h₂téh₂/pr̥h₂wéh₂/ish₁réh₂; 0011 h₁uséwih₂ (grandmother); 0015 léwbʰa, pr̥h₂téh₂,
  gʷr̥déwih₂, and the girl's "I am swifter" h₁eǵóh₂ HéHḱyōs is correct, since the -yōs comparative has one form
  for masculine and feminine (`degree_cells` gives the same NOM.SG for m and f); 0029 h₂yúHn̥ḱa, and the girl's pr̥h₂téh₂ in the last turn is hers; 0037 ǵr̥h₂éntih₂, gʷr̥déwih₂, h₁íh₂es
  (cows); 0010 h₂élyos "another man" is masculine on purpose.
- **Senses against the full glosses:** wikéti "fight" (wrestling), h₁ép-/lembʰ- "seize", Hyéh₁kt, déyḱt
  (pie-lex-deykjt "throw", not deyḱ- "show"), h₁ést (pie-lex-h1est "throw, shoot", the homophone of "be"), gʷélh₁t
  "hit, throw"; h₃ésth₁ "the bones" (knucklebones). "Ran faster" is HéHḱyōs h₁ésm̥ "was swifter". Hyudʰsmós "warrior";
  pr̥h₂wós and pr̥h₂tós both "first"; h₂éwh₂os "grandfather / maternal uncle"; h₃órbʰos "servant"; wetsós "calf";
  pótis/pótnih₂ "husband/wife"; gʰóstipotis "host, lord"; ḱéywos "dear"; HréwdH- "cry out, howl"; h₃sléydʰ- "slip,
  go astray"; h₂én "otherwise"; h₂éti "again"; éti "too, still"; h₁ewk- "learn"; Hyowdʰéye- MID "the earth moved"
  (the gloss has "become agitated", so it is not a causative-only misuse).
- **Formulas (4 records):** 0019 swift horses (HeHḱéwes h₁éḱwōs, gnomic "swift horses fall too"); 0022 the men who slew
  the serpent; 0028 Father Sky (vocative, now unsplit); 0040 great fame, imperishable fame, famous name. All are used
  in their sense. The menu also matches "Mother Earth" in 0019, but that is a coincidence (VOC méh₂ter + LOC dʰǵʰémi),
  not a use of the formula.
- **Fearing + ablative:** méd, kʷosmōd, wiḱpóteys, deywóybʰos, twéd are all ABL.
- **h₂élyos** takes the gender of its referent (h₂élyōs mógʰewes; h₂élyos "another man").
- **Short answers** (`np case`): ACC for object answers (a horse and a cup; a ram of my sheep; your young dog; my new
  shield; the cup?; my cow?); NOM for echoes of subjects or predicates (my knife?; a man?; a wolf!; a cauldron!).
- **Comparatives:** the standard is always ABL (mogʰúbʰos, h₁ésmōd, soksṓd, h₂ŕ̥tḱōd, moysóybʰos, kh₂n̥méns, méd), and
  neuter comparatives agree (dwéh₂yos, swéh₂dyos, méǵyos). The dual ḱéwh₁yosh₁e is correct.
- **Athematic obliques:** n̥ptéh₁, uksnéh₁, h₃rēǵés, gʰostéys, poh₂imnéy, h₂n̥réy, déh₂newi, gʰr̥h₁méni, swesr̥bʰós,
  h₁suḱléwesos, and wódr̥: INS wédn̥h₁, LOC wédni (the engine's paradigm).
- **Enclitics:** every two-enclitic run is in second position and reads correctly (moy toy after a vocative in 0003 and
  0014; swésorm̥ moy toy; ḱwónm̥ moy toy; ǵʰóstoh₁ me toy; kʷíd moy toy).

## Blind back-translation

Four of the six agree with the record English on content. My two misreadings came from homophones, not from the texts:
- 1f75208d (horses): matches. I took méǵʰye as "very"; it is the orthotonic DAT "to me" ("you are dear to me").
- 762387d5 (nine prizes): matches, except that I read wéwke as "told"; it is the IMP "tell". The planted ish₁réh₂s was
  flagged here too.
- 3d1503f2 (the spear): matches. I read déyḱt as "pointed" (it is "threw", pie-lex-deykjt) and gʰréh₁mn̥ as "thicket"
  (it is "grass").
- 60dc1191 (wrestling): mostly matches. I could not read wikóm ("I fought") and I read ní … déyḱt as "showed down".
- 1158eb97 (singing): matches. The planted gʰostíbʰos was flagged here too.
- 8917b208 (ram against dog): I misread méǵʰye ḱóm as "very far" (it is "with me") and h₁sdʰí as "be!" (it is
  "throw!", h₁ést).

## Engine and brief notes (report only)

1. **Homophones of "throw".** h₁ést "throw, shoot" (h₁sdʰí, h₁ésoh₂, h₁ést) shares every surface form with h₁ésti
   "be", and déyḱt "throw" (diḱdʰí) shares its forms with deyḱ- "show" (déyḱs, déyḱe). Both are correct, but a reader
   cannot tell them apart without the gloss, and both misled my blind reading. A planner note could prefer Hyéh₁kt or
   gʷélh₁t for "throw" when the context does not decide.
2. **Identical enclitics merged:** 0009 "your mouth … than your arms" has two `closed:personal/2` POSS slots and comes
   out with one toy (h₁óh₃s toy h₂r̥Hmóybʰos méǵyos). The reading is still clear, but the engine drops the second
   enclitic silently.
3. The formula counter counts "Mother Earth" in 0019, where the two words only co-occur. It needs a syntactic relation,
   not just the presence of both lexemes.

## Gate

Re-realized (final run after all plan edits) with `realize_plans.py data/generation/plans/t104.jsonl --batch t104
--model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`: 40/40 realized, 40 exact, reject_rate 0.0, max_lexeme_uses 6, formula_uses 4, 37 WARNs
(all checked, none an error), **gate PASS**. The plan as it was before review is kept at
`/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/t104-plans-before-review.jsonl`.

Release rule inputs: plant recall 5/5; 0/20 real items wrong after fixes; gate PASS.
