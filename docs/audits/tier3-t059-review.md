# Tier 3 batch t059 review (`review-v1`, 2026-10-30)

Batch: 40 in-world two-speaker dialogues, children and teaching (`tier3-dialogue-inworld-v1`, claude-opus-5-5).
Procedure: docs/generation/reviewer-brief.md. Packet `scripts/make_review_packet.py t059 --n 20 --plants 5 --tier1 3`
(28 items: 20 real, 5 planted, 3 Tier 1). Nothing under data/audits/ was opened.

## Order of work and integrity

1. Blind back-translation of 6 items, reading only the `pie` field. Saved as
   `docs/audits/packets/t059-blind-translations.jsonl`.
2. Verdicts on all 28 items, checked against `Lexicon.cells()` and the lexicon. Saved as
   `docs/audits/packets/t059-verdicts.jsonl` before corpus/ or the plans were opened.
   **sha256 `9b54593223b67c509cafed45907de630ac346e624f5c9f660235e2013b5a4fd9`.**
3. `resolve_review_items.py t059`, then `score_review.py t059`. Only after that did I read the corpus and the plans.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **4/5** (all 4 caught were named correctly) |
| Tier 1 judged wrong | 0/3 |
| real items wrong | **0/20** (rate 0.0) |
| real items minor | 3/20 |

Plants caught (all `wrong`):
- 69eec48a: `h₁ésete` (SBJV.2PL) for one addressee; the record has `h₁ésesi`.
- 42071f9b: `gʷnéh₂s` (GEN/ABL.SG) used as the vocative "Woman"; the record has `gʷḗn`.
- 19e13465: `widwé` (PRF.1DU) for "I do not know"; the record has `wóydh₂e`.
- fca6f82f: `téksi` (PRS.2SG) for "I am weaving"; the record has `téksmi`.

Missed plant: 8259d4ae (the washing dialogue). In the packet, "knees" is `ǵónwih₁` (NOM/ACC.DU); record 00035 has
`ǵónuh₂` (ACC.PL). I worked this out from memory after reading the records; I did not diff the packet against the corpus.
For knees, a natural pair, the dual is defensible under planner-brief rule 17, so the planted form is arguably not an
error. The lead can judge whether this miss counts as a reviewer lapse.

## Blind back-translation agreement

Of 6 items, 4 agree closely: 69eec48a, 8259d4ae, 15458d25, 920e7376. In 8259d4ae I read `médʰu` as "mead". The English
says "honey", which is also in the gloss ("honey; honey wine, mead"), so this is not an error. Two items agree only
partly:
- b3e1d9a2: I read "afraid *for* my father's (flock)". The record means "afraid of my father": `ph₂trés` is ablative
  with the perfect of fearing, which is correct.
- 6b85d4ab: I read `wéwke` as a 3sg past. It is IMP.2SG "say!".

Neither is a defect in the PIE. On 69eec48a I flagged `h₁ésete` while translating blind, and it was a plant.

## Real items flagged (packet pass)

All minor. None was wrong.
- **ac0b4e46 = t3-t059-00003; 77b0a9dc = t3-t059-00009** (and the same pattern in 00030, outside the packet).
  "With two hands/arms" comes out as `dwóbʰih₁ ǵʰóstōys` / `dwóbʰih₁ bʰeh₂ǵʰúbʰis`: the numeral is in INS.DU and the
  noun in INS.PL. Rule 17 makes the engine use the plural for an oblique dual, and that is expected. Only the numeral is
  inconsistent: it keeps a dual oblique form that the noun cannot have. **Engine convention, reported. No plan edit.**
- **47d63835 = t3-t059-00027**: `yéwgs` (AOR.2SG, "how did you yoke") for the habitual question "how do you yoke the
  horses?". Fixed below.

## Second pass: all 40 records against planner-brief-v4 and the in-world dialogue brief

Checked: modern or coined content; whether each turn answers the one before; whether elders explain nature in the PIE
world's own terms; speakers; per-sentence English; pronoun referents; verb senses against glosses; fearing with the
ablative; athematic obliques; numerals; enclitic placement.

**Found nothing wrong in:**
- *Modern content or coinages.* There are none. The elders' explanations stay mythic and in-world: the tired sun carried
  under the earth by horses (00001); Sky filling the clouds (00002); Perkunos striking the serpent that hides the rains
  (00026); Father Sky above and Mother Earth below (00034); men received words and beasts tails (00040).
- *Fearing with the ablative.* Correct throughout: `ph₂trés … bʰebʰóyh₂h₂e`, `méd h₂epó bʰebʰóyh₂e`,
  `ḱunés dedwóye`, `tósmōd bʰebʰóyh₂h₂e`, `gʰrómōd ne h₂eh₂ógʰh₂e`, `wĺ̥kʷōd ne trésōh₂`.
- *-éye- verbs.* Every one is used in its glossed sense, so there is no causative standing in for a plain verb:
  bʰoréye "carry around", dʰoréye "hold", wodʰéye "lead", Hmolḱéye "touch repeatedly", logʰéye "lay",
  woséye "clothe", h₁opéye "make reach, give", ǵonh₁éye "bring forth", sokʷéye "say".
- *Athematic obliques.* All correct: `h₁uHdʰéni`, `sh₁méns`, `ḱunés`, `n̥h₂séh₁`, `déh₂nus`, `kl̥Héni`, `sh₂wéns`,
  `ǵn̥h₁tr̥bʰós`, `h₁n̥gʷl̥sú`.
- *Numerals.* `dwóh₁ ugʷsénh₁e`, `dwóh₁ ḱr̥h₂nóh₁ … h₁stés`, `tríh₂ h₂ōwyéh₂ … h₁ésti`, `kʷetwóres h₂egʷnṓs`,
  `h₁néwn̥ / déḱm̥ + PL` are all right. Two coordinated subjects take a dual verb: `snóygʷʰos h₁yégos-kʷe gʷm̥tā́m`.
- *Enclitics.* All are in second position.

**Plan fixes made** (data/generation/plans/t059.jsonl):

| record | before | after | why |
|---|---|---|---|
| t3-t059-00003 | `wéy-kʷe h₁éymos h₂mélǵos dh₃mé` (deh3t AOR) | `… dedh₃més` (dedeh3ti PRS 1PL) | Habitual "we give them milk", parallel to `dédh₃n̥ti` in the same sentence. The aorist read "we gave". |
| t3-t059-00023 | `swóm nos ǵénh₁os ḱérh₃eti` | `h₁ésyo nos ǵénh₁os ḱérh₃eti`; English "his own kin" → "his kin" | `swós` is reflexive, so it refers to the subject (the kin itself), not to the guest. A pronoun referent error (rule 19). |
| t3-t059-00027 | `kʷíh₁ … h₁éḱwons yéwgs?` (yewgt-2 AOR 2SG) | `… yunégsi?` (yunegti PRS 2SG) | The aorist meant "how did you yoke". The root's nasal present is in the lexicon, so the gnomic-aorist exception of rule 8 does not apply. |

**Kept, with a note:**
- 00003 clause 0: `ǵʰumé` (AOR 1PL "why do we pour"). `gjhewt-2` has only aorist forms, and the present `gjheweti` is
  `gloss_approximate` with attested_in 1, so rule 8's gnomic aorist applies. The same holds for other aorist-only
  lexemes in general statements: `séngʷt` (00001), `h₂wérst` (00002), `h₂wékst` (00019), `h₁n̥dʰént` (00011),
  `h₁réh₁t` (00028), `Hyéh₁km̥` (00024).
- 00016: "His name lives in our hearts" is phrased sentimentally, but heart-as-memory and fame-after-death are both
  inherited; it is not modern.

**Brief-level observation (report only, no edit).** The in-world brief says `model` is "a man or woman of a household".
In five dialogues, though, the `model` is the child and the `user` is the elder:
- 00005: the father asks his son;
- 00011: a sister answers her brother;
- 00025: the child who licked the honey;
- 00034: the elder quizzes the boy;
- 00035: the child who refuses to wash.

The plans themselves are consistent: every speaker label matches the turn's content, and the user speaks first. In a
batch about teaching, though, these dialogues train the model to play the child. Swapping the labels would break "the
user first". This is for the lead to decide; the brief could say that the model plays the adult in teaching dialogues.

## Engine and brief findings (for the lead)

1. **Dual numeral with a plural noun in oblique cases** (00003, 00009, 00030): `dwóbʰih₁` INS.DU beside `ǵʰóstōys` /
   `bʰeh₂ǵʰúbʰis` INS.PL. Consider giving the numeral the same plural fallback that the noun gets.
2. **Model/user role** in teaching dialogues (above).

## Gate after the fixes

Re-realized with
`scripts/realize_plans.py data/generation/plans/t059.jsonl --batch t059 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`.
The result is 40/40 exact_pass, reject_rate 0.0, max_lexeme_uses 7, and **gate PASS**. There were 18 warnings: pronoun
antecedents more than two clauses back, and one near-homograph `h₂éǵt`/`h₂éǵet`. I checked them all; the referents are
correct and `h₂éǵt` does mean "said".

I compared the corpus before and after by record id. Only the three intended records changed: 00003, 00023 (also its
English) and 00027. There was no drift from concurrent lexicon or engine work.

**Counts:** real wrong 0/20 before and 0/20 after. Real minor 3/20 before. After the fixes, 2 remain: the engine
numeral convention. The 00027 tense issue is fixed. Release approval has not been set.

## Follow-up fix (lead request, 2026-10-31): dual numeral in an oblique case

The engine turns a dual noun in an oblique case into the plural without saying so (docs/NEXT.md, "Silent cell
substitution"). That left `dwóbʰih₁` (INS.DU) standing with a plural noun, which is ungrammatical. In all three clauses
I dropped the numeral, set the noun to `num: "PL"` and made the English match:

| record | before | after | English |
|---|---|---|---|
| t3-t059-00003 | `tód moy dwóbʰih₁ ǵʰóstōys ǵʰéwoh₂.` | `tód moy ǵʰóstōys ǵʰéwoh₂.` | "I will pour it with my hands." |
| t3-t059-00009 | `néwom péh₃tlom dwóbʰih₁ ǵʰóstōys kapyé.` | `néwom toy péh₃tlom ǵʰóstōys kapyé.` | "And hold the new cup with your hands." |
| t3-t059-00030 | `tóm dwóbʰih₁ bʰeh₂ǵʰúbʰis stunddʰí gʷéHye-kʷe.` | `tóm toy bʰeh₂ǵʰúbʰis stunddʰí gʷéHye-kʷe.` | "Push it with your arms, and sing." |

In 00009 and 00030 I added an enclitic `toy` "your" (POSS of the instrument noun). The engine puts it in second
position, Wackernagel's slot. As a result, `néwom toy péh₃tlom` can also be read "your new cup". This is an engine
placement question, not a grammar error.

Re-realized with the same command. The result is 40/40 exact_pass, reject_rate 0.0 and **gate PASS**. I compared the
corpus by record id before and after: only these three records changed. With this fix, no real minor items remain.
