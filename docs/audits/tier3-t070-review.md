# Tier 3 batch t070 review (review-v1, 2026-10-31)

Batch: 40 in-world two-speaker dialogues (hunting, the wild, far places), prompt `tier3-dialogue-inworld-v1`.
Reviewer: calibrated reviewer (claude-opus-5-5). Procedure: docs/generation/reviewer-brief.md.

## Order of work
1. Re-realized the batch once at the start so the records include today's engine fixes ("?" when any clause of
   a sentence has `question`; check_plan rejects 'two' in an oblique case). Gate PASS, 40/40 exact. The
   realizer printed WARN lines with record ids and a few glosses. That was before the packet was made, and no
   packet English was seen.
2. Packet `make_review_packet.py t070 --n 20 --plants 5 --tier1 3`: 28 items (20 real, 5 planted, 3 Tier 1).
3. Blind back-translation of 6 items, PIE field only: `docs/audits/packets/t070-blind-translations.jsonl`.
4. Verdicts on all 28 items, saved before opening corpus/ or plans:
   `docs/audits/packets/t070-verdicts.jsonl`,
   **sha256 `c5e543f80e127888a7243e117d00faa9d6f5fdf68053cbc78600274419116329`**.
5. `resolve_review_items.py t070`, then `score_review.py t070`. Nothing under data/audits/ was read.
6. Second pass: all 40 records read sentence by sentence (speaker, per-sentence English, PIE, token glosses),
   checked against planner-brief-v4.md and the top part of planner-brief-dialogue-inworld.md.

## Calibration
| | |
|---|---|
| Plant recall | **5/5** (all 5 named with the right defect) |
| Tier 1 judged wrong | 0/3 |
| Real items judged wrong | **0/20** (rate 0.00) |
| Real items judged minor | 5/20 |

Plants caught:
- b637c519: séngʷs (AOR.2SG) where the English has 'they go under'.
- 0f3cbff7: ǵérh₂onth₁e (NOM/ACC.DU) as the recipient 'to the old men'.
- 90e27e5d: suHnúbʰos (DAT/ABL.PL) as the address 'Son'.
- 771893ee: bʰéwdʰōh₂? (1sg) where the English is 'Will you stay awake?'.
- 64a23aef: tr̥syétes (2/3DU) where the English is 'I am thirsty'.

The real records have the correct forms in each case (sn̥gʷént, ǵr̥h₂n̥tbʰós, súHnew, bʰéwdʰēsi, tr̥syóh₂).

## Blind back-translation
Agreement was substantive on 5 of the 6 items. Misreadings:
- 771893ee: I read ǵʰḗr 'hedgehog' as ǵʰwḗr 'wild beast'. This was my error, not the record's.
- 0f3cbff7: I did not recognise h₁ést 'shot' (h₁es- 'throw, shoot').
- dd089d0b: I first took wéwke for a perfect. It is the reduplicated thematic aorist imperative, which is correct.

On 771893ee, the blind reading followed the PIE faithfully ("Shall I stay awake?"), which exposed that plant before
the English was seen. In b637c519 I took séngʷs as a participle ('diving'). That plant, and the dual in 0f3cbff7,
were caught later, by looking up the forms in the review pass.

## Real minor items (packet)
| Item → record | Issue | Action |
|---|---|---|
| c735ffd9 → t3-t070-00005 | dóru ḱénesi (SBJV) glossed 'Can you climb a tree?'; ability isn't expressed | **Fixed**: English is now "Will you climb a tree?" |
| 97ae01fb → t3-t070-00036 | bʰoréyōh₂ is the iterative 'carry around', used for plain 'I shall carry' | **Fixed**: lexeme changed to bʰéreti, so the form is now bʰérōh₂ |
| 57650356 → t3-t070-00007 | déh₂nu éti 'beyond the river' | No change. The lexeme's gloss is "beyond, over", so on re-check this is acceptable |
| bf6e9cec → t3-t070-00004 | méǵʰye ḱóm: the dative pronoun with ḱóm | No change. This is the documented `case_fallback` (v4 brief: pronouns have no instrumental) |
| a86e6a52 → t3-t070-00029 | póntoh₁m̥ follows the lexicon's póntoh₁s; the standard form is *pónteh₂s / *póntoh₂m̥ | Lexicon issue, reported below |

## Second pass: all 40 records
**Wrong: 0.** I found nothing modern and nothing coined in the neologism sense. Every turn answers the one before it.

What I checked across all 40 records, with no error found:
- **Speakers.** Both speakers belong to the PIE world: kin, elders, guests, hunters, a wife greeting her husband. Speaker tags and the per-sentence English are correct.
- **Pronouns.** Each pronoun matches the gender and number of its referent. The engine's 19 antecedent warnings were checked one by one and are all benign: doe f, elk f, fox f, geese f, the net tn̥tlós m, the river déh₂nu n, the hide skéwHtis f.
- **Fearing.** Every verb of fearing takes the ablative: tn̥tlṓd, n̥sméd, h₂ŕ̥tḱōd, h₁ésmōd, h₂wl̥péys.
- **Animal words.** Each is used in its real sense:
  - h₁ólh₁nih₂ 'doe'; táwros 'wild bull, aurochs'; wl̥kʷíh₂s 'she-wolf'; udréh₂ 'otter'.
  - tworḱós 'boar'; ǵʰḗr 'hedgehog'; skʷálos 'large fish'.
- **Written-around words.** The PIE says what the English says:
  - 'woods' is drúbʰos 'from the trees'; 'bow string' is tónos 'something stretched'.
  - 'shoot' is h₁es- 'throw, shoot'; 'lair' is légʰos; 'hole' is h₃okʷéh₂.
  - 'honey from the oaks' stands in for bees.
- **Athematic obliques.** Number and case are right throughout: h₂éḱmonn̥s, limn̥sú, kl̥Hn̥bʰós, h₃dn̥tbʰís, h₂ḱmn̥bʰís, neh₂ubʰós, démbʰos, pérunbʰos, ǵʰh₂n̥sés, tr̥méns, ǵr̥h₂n̥tbʰós.
- **Motion verbs.** Goal accusatives, ablatives of source and the adpositions are all right.
- **Enclitics.** They stand in Wackernagel position, including nókʷtm̥-kʷe te pér.
- **Causatives.** Causatives appear only where the gloss is causative: moréye- 'kill', wodʰéye- 'lead', logʰéye- 'lay', sodéye- 'set'.
- **Engine fixes.** 00015 now ends in "?", and no 'two' appears in an oblique case.

**Minor (second pass, fixed): t3-t070-00026.** ḱód memónh₂e (PRF 1SG, 'I have this in mind') was glossed "I shall remember this". The English is now "I remember this."

**After fixes: real wrong 0/20, real minor 3/20** (57650356, bf6e9cec and a86e6a52 are left as they are, for
the reasons above).

## Fixes made (plan only)
- `data/generation/plans/t070.jsonl`, three edits:
  - t070-0005: English changed to "Will you climb a tree?"
  - t070-0026: English changed to "I remember this."
  - t070-0036: pie-lex-bhoreyeti changed to pie-lex-bhereti.
- Re-realized with `scripts/realize_plans.py data/generation/plans/t070.jsonl --batch t070 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`.
- Result: **gate PASS**. 40/40 realized and exact, reject rate 0, max lexeme uses 7, 337 distinct lexemes, 181 roots.

## Engine, lexicon and brief notes (report only)
1. **póntoh₁s 'path'** (pie-lex-pontoh1s). The handbook form is *pónteh₂s (Ved. pánthāḥ, Av. pantå). The lexicon has an h₁ where an h₂ is expected. **Lexicon.**
2. **ḱlḗm, AOR.1SG of ḱléwt** (00022): a **probable engine defect**.
   - `Lexicon.cells` gives ḱlḗm both for ḱléwt 'hear' and for ḱléyt 'lean'. So the 1sg root aorist of every -ew-/-ey- root is contracted.
   - Other roots are not: h₁épm̥, léytm̥.
   - Stang's law (*dyḗm, *gʷṓm) applies before a non-syllabic word-final *-m. It does not apply before the syllabic 1sg ending *-m̥, so the expected form is *ḱléwm̥.
   - The meaning is intact, so this is minor. **Engine.**
3. **h₃wáth₂t 'wound'** (pie-lex-h3wath2t). The lexicon spells this root with *a*, and nothing in the context colours the vowel. Treated as the lexicon's form, not as a batch error. **Lexicon, possible.**
4. **Project reconstructions.** The batch uses five: spélom 'story', h₂énHos 'grandmother', ḱásnos 'grey', ḱasós 'hare' and gʷʰermós 'warm'.
   - They are flagged `coined: "project"` and allowed by the v4 brief. The records carry `neologism: false`.
   - I did not count them as coinages. If the lead reads "coined" to include project reconstructions, they need a separate decision.
5. **ǵŕ̥h₂enti, VOC.SG f of ǵérh₂onts** (00028 'Old woman'). The f paradigm is NOM ǵr̥h₂éntih₂, ACC ǵr̥h₂éntih₂m, GEN ǵr̥h₂n̥tyéh₂s.
   - The nominative and accusative have a full-grade suffix with *-ih₂*. The genitive has a zero-grade suffix, the Vedic jaratī́ pattern.
   - The first vocative variant, ǵŕ̥h₂enti, has the accent retracted onto the zero-grade root.
   - The ablaut of the f paradigm is internally mixed. Minor. **Engine.**
6. **skélesh₂ 'legs'** (00029). Plural, where v4 rule 17 asks for the dual of a natural pair. ḱeḱómh₂e is a perfect, and the perfect has no 3du, so the planner had no dual option. Minor, no fix.
7. **Gloss display only.** pós is displayed with its first sense, 'afterwards', but it is used as 'by, at', which its gloss also gives. h₂ew is displayed as 'away from' but used as 'again', also in its gloss. The forms are correct.

The release approval was not set. No corpus file was edited by hand, and nothing was committed.
