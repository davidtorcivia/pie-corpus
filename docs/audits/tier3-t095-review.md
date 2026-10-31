# Tier 3 batch t095 review (`review-v1`, 2026-10-31)

Batch: 40 in-world two-speaker dialogues on sickness and healing (a child's fever, wounds from horn and blade, the
healer's herbs and spoken charms, a sprain charm, a sick cow, an old man who will not recover, recoveries, prayers
for health), `tier3-dialogue-inworld-v1`. Reviewer: calibrated agent review following
docs/generation/reviewer-brief.md. Approval is not set here.

## Procedure

1. Packet: `make_review_packet.py t095 --n 20 --plants 5 --tier1 3` (28 items).
2. Blind back-translation of 6 items from the `pie` field alone, before any English was printed:
   `docs/audits/packets/t095-blind-translations.jsonl`.
3. Doubtful forms were checked against `Lexicon.cells()` with a reverse form index, and full glosses were read with
   `Lexicon.meaning()`. The verdicts were written and saved before corpus/ or the plans were opened:
   `docs/audits/packets/t095-verdicts.jsonl`, sha256
   `aef8a647f1559af46bc92f31b062cc12e75015c93273b8ddb06eabb7999bcbda`.
4. `resolve_review_items.py t095`, then `score_review.py t095`.
5. Second pass: all 40 plans read clause by clause (speaker, per-sentence English, every realized word with its
   features, gender and full gloss), checked against planner-brief-v4 and the in-world dialogue brief.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all 5 caught and named) |
| Tier 1 controls judged wrong | 0/3 |
| real items judged wrong (as scored) | 1/20 |
| real items judged minor (as scored) | 1/20 (withdrawn below: 0/20) |

Plants caught (packet spelling):
- légʰtu: IMP.3SG "let him lie", where the wife tells her husband "Lie down" (2SG);
- ḱolHtéh₂h₁: fem. INS.SG/NOM.DU, where the predicate of masc. h₂énh₁mos "the wind is cold" needs ḱolHtós;
- gʷʰéresos: GEN/ABL.SG as the subject of "Heat brings bad dreams" (NOM gʷʰéros);
- th₂kéh₁yetes: PRS.2DU/3DU for "Friend, why are you silent?" (2SG th₂kéh₁yesi);
- liǵʰtés: PRS.2DU/3DU for "the cow licks it" (3SG léyǵʰti).

**Scored wrong, reason corrected.** 4f533c87 (t3-t095-00007). I marked the closing "Be well, friend!" (príHe kéh₂ilos
h₁sdʰí) as masculine said to the woman. The plan shows that the woman (model) says this line to the user, whose gender
is not stated, so the masculine is fine. The record is still wrong for another reason, found in the second pass:
"Woman, why are you rejoicing? ... Did you not know?" is answered with "I knew." (ǵn̥néh₃m̥). A speaker who has just
asked why she is rejoicing cannot have known, so the turn does not answer the one before. Fixed to "I did not know."
(ne ǵn̥néh₃m̥). The count stays the same: **real wrong 1/20 before the fixes, 0/20 after.**

**Withdrawn minor.** 7475f6a7 (t3-t095-00032). I guessed that "Thunderer, drive the heat out of my body!" fell to the
healthy wife. The plan gives that turn to the sick husband (model), so moy is correct. **Real minor: 0/20.**

## Blind back-translation agreement

Six items, translated from the PIE alone (4f533c87, 4b2f61ea, cadd326e, 74812d07, 5c4e374e, 1e8730ac). All six
match the English in substance. The differences come from the reader, not the text:
- ḱósmi dinóy is "today" ("on this day"); I read it as an ordinal;
- in 4f533c87 the blind reader split the turns differently ("gʷémoh₂" is "I will come", not praise);
- h₂énHos is "grandmother" (project word); the blind reader guessed "grandfather";
- úderos is "belly", not "udder"; skéwHtim is "skin", not "bark";
- kapyṓh₂ "shall I grasp (a spear)": the object gʷéru was misread.

None of these shows a defect in the PIE.

## Second pass (all 40 records)

Checked on every record: speakers (two, user first, a new speaker starts a new sentence) and the English of each
sentence; the 30 pronoun and VOC WARNs, one by one; verb senses against the full glosses; formulas; cow gender;
h₂élyos; the gender of predicate adjectives with dropped subjects; the case of short answers; athematic obliques;
enclitics.

- **Pronoun WARNs (30):** none is real. Each 3rd-person verb next to a vocative has a 3rd-person subject (the horse,
  the cow, the lamb, the baby, the boy). Each anaphor out of the window has a clear antecedent: h₁ésyeh₂ey is the
  daughter in 0001, h₁ím the horse in 0004 and 0027, h₁íd the sore in 0030, téh₂ "the words" in 0033, tód the
  charm in 0010. h₂éǵes in 0027 is correctly 'drive'.
- **Healing vocabulary:** térh₃t and h₃wáth₂t are glossed "to wound"; mḗdeti is "to heal, treat (the sick)", used
  with an object and absolutely ("the tongue of a dog heals"); kéh₂ilos is "healthy; whole"; fever is tépos /
  gʷʰéros "heat" with h₁éwseti "burn", lelóykʷe "is gone", léykʷeti "will leave". The sickness and charm words are
  plain verbs and glossed nouns: Hrupyéti "suffer pain", kʷéh₂se "cough", swidyéti "sweat", púHyeti "rot", h₁élḱos
  "sore", púHos "pus", wisós "poison", kʷŕ̥mis "worm", h₂roh₁dʰéye "speak (against)", yunégti "join". No word is
  stretched past its gloss, apart from the two English fixes below.
- **Formulas (5), all used in their sense:** great fame (0040), imperishable fame (0024), Father Sky (0008, dyéw nos
  ph₂ter ḱludʰí), Dawn, daughter of Sky (0026), giver of good things as thanks (0028).
- **Cows:** gʷṓws is "f" with feminine pronouns in 0005 (albʰéh₂ gʷṓws, h₁íh₂) and 0039. The gʷṓs of 0024 is cattle
  driven off in a raid (generic, m). Bull and calf are uksḗn and wetsós.
- **h₂élyos:** not used. **Verbs of fearing:** none in the batch.
- **Predicate gender:** all correct: snúse ḱuh₁réh₂ h₁sdʰí, gʷḗn túH ḱuh₁réh₂, h₁íh₂ péh₂ureh₂ ml̥déwih₂-kʷe, the
  user's ḱéwh₁yōs (fem. NOM, common-gender comparative), méh₂tēr toy ml̥déwih₂, h₁súmenes (f) ... túH ḱéyweh₂.
- **Short answers:** gʰóstis (NOM, it answers "who"), deḱsiwós pṓds (NOM), sewyóm (ACC, it answers "which foot
  did it bite"), mḗms + relative (ACC, it answers "what did you eat"), kʷód kéh₂nmn̥ (ACC), "five men and two
  children" (NOM, subject of "lie dead"), "the herbs of the wise woman..." (NOM, subject of "healed").
- **Athematic obliques:** h₃sth₁éh₁, h₁sh₂énh₁, sn̥h₁wénh₁, h₃n̥gʷénh₁, m̥dʰúh₁, m̥dʰéws, gʷrúh₁, h₂épesh₁,
  skuHtíh₁, dʰǵʰémi, h₁éh₃si, wésni, sh₂wéns and sh₂léh₁ are all correct cells.
- **Enclitics:** moy, toy, me, te, nos and wos stand in second position throughout, with no doubles.
- **Format (checked by script on the final plans):** every clause has a speaker, there are exactly two speakers, and
  the user speaks first. Every change of speaker starts a new sentence, and there is English on every
  sentence-initial clause and nowhere else. The per-sentence English, joined, equals the plan's English in all 40.
- **Accepted idiom:** "Can you stand?" / "I cannot stand" (0040) and "Can you lift your arm?" / "I cannot lift it"
  (0017) are plain presents in the PIE. The English ability modal is a normal reading of the present here, so they
  are not counted.

### Wrong (1, fixed)

| record | issue | fix (plan) |
|---|---|---|
| t3-t095-00007 | "Why are you rejoicing? ... Did you not know?" answered with "I knew." (ǵn̥néh₃m̥): the turn contradicts the question before it | clause 3 `neg: true`, English "I did not know." → ne ǵn̥néh₃m̥ |

### Minor (6 in 5 records, fixed)

| record | issue | fix (plan) |
|---|---|---|
| 0013 | "I will pray to the Dawn for her": no slot for "for her" | IO anaphoric_i f → h₁ésyeh₂ey h₂éwsosm̥ gʷʰédʰyōh₂ |
| 0014 | swéh₂h₁ h₂éwih₁ ḱóm is "with its own ewe"; the English said "with its mother" | English "with its ewe" |
| 0016 | "if you drink it" (tód): the antecedent (the water) is seven clauses back | OBJ wódr̥, English "if you drink the water" |
| 0021 | "I will remember it" was PRF IND memónh₂e ("I remember"), answering SBJV meménesi | PRF SBJV → meménoh₂ |
| 0021 | "I boil it": pékʷeti is glossed "cook; ripen" | English "I cook it" |
| 0035 | "Friend, why are you silent? There are tears on your face." was one PIE sentence with no "?" | clause 0 `question`, clause 1 `break` with its own English |

Before the fixes: 1 wrong and 6 minor over 40 records. After the fixes: 0 and 0.

## Re-realization

`realize_plans.py data/generation/plans/t095.jsonl --batch t095 --model claude-opus-5-5 --prompt-id
tier3-dialogue-inworld-v1`: 40/40 realized, 40 exact, reject 0.0, max lexeme uses 7, distinct lexemes 340,
roots 197, formula_uses 5, warnings 29 (all checked above; rechecked after the fixes: the 0016 WARN is gone, and the new IO in 0013 adds none), **gate PASS**.

## Engine notes (report only, not fixed here)

- Water INS.SG is wédn̥h₁, with an acrostatic weak stem wédn-. The handbook proterokinetic paradigm has udénh₁ /
  udnés (Beekes; cf. h₁sh₂énh₁, sn̥h₁wénh₁ in the same batch). This is not scored, because it is the lexicon's own
  cell, but the lead may want to review the wódr̥ paradigm.
- ḱléwt AOR.1SG is ḱlḗm (0018), apparently from a Stang's-law rule. The root aorist would have *ḱléwm̥, and Stang's
  law applies to -Vwm with a non-syllabic m (dyḗm, gʷṓm), so this is worth checking.
- As noted in the task, realize_plans does not enforce speakers or per-sentence English for Tier 3. All 40 records
  were checked by hand: two speakers, user first, English on every sentence-initial clause.
- One caveat for packet reviews: gender of address cannot be judged from the packet alone when the speaker split
  is ambiguous. In both of my withdrawn calls (00007, 00032) the plan's speaker field settled the question.
