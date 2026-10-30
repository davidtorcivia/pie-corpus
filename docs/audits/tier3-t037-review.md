# Tier 3 batch t037 review (sleep, dreams, night, waking, fear)

Reviewer brief: `review-v1` (docs/generation/reviewer-brief.md). Second pass against docs/generation/planner-brief-v4.md.

## Procedure

1. Packet: `scripts/make_review_packet.py t037 --n 20 --plants 5 --tier1 3` (28 items: 20 real, 5 planted, 3 Tier 1).
2. Blind back-translation of 6 items from the `pie` field only. This was done before any English was printed:
   `docs/audits/packets/t037-blind-translations.jsonl`.
3. Verdicts were written before corpus/ or the plans were opened: `docs/audits/packets/t037-verdicts.jsonl`,
   sha256 `e8354676b9ac1745718ecc6a34e7b144c8d52397e73e011973462ef4078e510e`.
   Doubtful forms were checked against `Lexicon.cells()`, `participle_cells()` and closed_class.json, using a reverse index
   from surface form to (lexeme, cell). data/audits/ was never read, and the packet was not diffed against the corpus.
4. Then `resolve_review_items.py t037` and `score_review.py t037` were run.

## Calibration (score_review.py)

| | |
|---|---|
| plant recall | **5/5** (all caught, all named) |
| Tier 1 judged wrong | 0/3 |
| real items wrong | **0/20** |
| real items minor | 3/20 |

Plants caught, in the packet's own spelling:
- f69de38b `yugmé`: AOR.1PL for 3sg "he yoked". The record has yéwgt.
- ffe82b47 `h₂wésm̥`: AOR.1SG for "it dawned". The record has h₂wést.
- 4a124e97 `dedórḱe`: PRF.3SG for "I have seen". The record has dedórḱh₂e.
- 9c74867d `ḱlutā́m`: 3DU for the plural command "Hear!". The record has ḱluté.
- c379316d `h₁imń̥bʰis`: INS.PL where the English needs an object. The record has ACC h₁éymn̥. I judged this one minor.

## Blind back-translation agreement

All 6 items were read correctly in substance. Where I went wrong:
- ffe82b47: I read ḱóm as "together" (it is "this one"). I read tetólh₂h₂e as 3sg; it is 1sg, "I am holding him up". I flagged
  h₂wésm̥ in the blind pass (a plant).
- a948ebf4: I read Hwr̥tā́m as "vowed"; it is "enclosed". ḱéym̥h₁nom "lying" was unclear to me.
- 237f5286: I took h₁eh₁lówdʰth₂e as "you have come"; it is "you are grown". The root h₁lewdʰ- has both senses.
- 801b6e19, b1f70ccf and 4a124e97 matched the English. In 4a124e97 I flagged the person of the perfect (a plant).

## Real minor items (packet)

| item | record | issue | action |
|---|---|---|---|
| 12684c47 | t3-t037-00009 | "and it was warm": anaphoric h₁éy NOM.SG m used as a dummy subject of an impersonal verb (breaks brief rule 7) | **fixed**: subject slot removed, now `gʷʰréh₁yet-kʷe` |
| 492e081d | t3-t037-00025 | "said to the guardian": ph₂tréy is identical to the DAT.SG of ph₂tḗr "father" | **engine gap**, reported below |
| 1d51cd92 | t3-t037-00033 | séngʷt (aorist) for the general "it sinks" | kept: sengʷ- has only aorist forms, so this is a gnomic aorist, which brief rule 8 allows |

## Second pass: all 40 records

All 40 records were read in full: PIE, gloss and English. I found nothing modern. spélom "tale" (00035) is the only
`coined: project` reconstruction, and planner-brief v4 allows those. Sleep verbs are used in their glossed senses:
- swopéyeti always means "put to sleep" (00002, 00026, 00031), never "sleep".
- ses- means "sleep".
- légʰ- (AOR) means "lie down"; légʰyeti means "be lying down".
- ḱey- (MID) means "lie".
- bʰewdʰ- (AOR) means "wake up"; bʰéwdʰeti means "be awake".
- h₁ger- means "wake up".
- ń̥supnos means "sleepless".

Verbs of fearing with an object take the ablative: nékʷts bʰéyh₂t (00001), h₁ésmōd bʰih₂ént (00023). The other fear
verbs have no object. Stories cohere, and pronouns track their referents except where fixed below.

Fixes in data/generation/plans/t037.jsonl (all minor):
- **t037-0009**: the dummy subject described above.
- **t037-0028**: "The cattle drank, and they praised Perkʷunos" made the cattle the praisers (3pl carried over from gʷówes).
  The praise clause now has SUBJ h₁léwdʰis PL: "and the people praised Perkʷunos". I picked h₁léwdʰis because poh₂imḗn and
  h₂nḗr were at the lexeme cap.
- **t037-0040**: "There it is running and seizing the beast" was realized with aorists drémt, lémbʰt for a present
  description. It now uses the presents tékʷeti and kapyéti. "She gave it grease" now has an overt demonstrative SUBJ
  (séh₂), so the subject is clearly the daughter and not the dog.

Counts: before, 0 real wrong and 3 real minor. After, 0 wrong and 2 minor: one engine gap and one gnomic aorist the brief
allows.

## Engine / lexicon findings (report only)

1. **péh₂tōr "guardian" declension:** the obliques are ph₂tr- (DAT.SG ph₂tréy, DAT.PL ph₂tr̥bʰós), identical to ph₂tḗr
   "father". This affects 00025 and 00016 ("said to the guardians"). A root-accented -tor agent noun should keep a
   distinct oblique stem, so this needs the noun spec in data/morph.
2. **anaphoric_i m NOM.SG:** closed_class.json lists h₁éy (also NOM.PL) as the first NOM.SG form, so "he" comes out as
   h₁éy (00014 "h₁éy h₁uséwōm déh₃tōr"). The handbook form is *h₁ís (Lat. is, Goth. is). Worth checking the ordering.
3. **gʷʰen- "slay" has no aorist** in the lexicon. Single events ("he slew the serpent", 00006, 00028) are therefore
   realized as imperfects gʷʰént, gʷʰénm̥, gʷʰéns, which the brief allows when no aorist exists.

## Gate

Re-realized with `scripts/realize_plans.py data/generation/plans/t037.jsonl --batch t037 --model claude-opus-5-5
--prompt-id tier3-planner-v4`: **PASS**. 40/40 realized and exact, reject rate 0. max_lexeme_uses is 10 (cap 10). There
are 300 distinct lexemes and 170 roots, 45.45 words per record and 16 formula uses. The batch has no metered genres.

Release approval was not set and nothing was committed.
