# Tier 3 review: batch t050 (28-item packet + full second pass)

Batch t050 has 40 in-world two-speaker dialogues about travel and homecoming: fords, bridges, passes, ice, ferries, guests, exiles, and returns home. The review followed `docs/generation/reviewer-brief.md` (review-v1):
- The packet was built with `make_review_packet.py t050 --n 20 --plants 5 --tier1 3`.
- Six items were back-translated blind, from the `pie` field only, before any English was read.
- The verdicts were written and hashed before `corpus/` or the plans were opened.
- `resolve_review_items.py` and then `score_review.py` were run. Nothing under `data/audits/` was opened.

Checks used: handbook knowledge (Fortson, Beekes, Ringe, LIV², Mallory & Adams, as remembered), `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json`, `Lexicon.cells()` / `.participle_cells()` and `scripts/lexq.py --id`.

- Verdicts: `docs/audits/packets/t050-verdicts.jsonl`, sha256 `d926c8df0ebf9c059bf079bf01aa3d8d83e20e4515f272f06450f9bfb85e21bf`. The hash was recorded before the corpus or plans were opened.
- Blind translations: `docs/audits/packets/t050-blind-translations.jsonl`.

## Calibration (score_review.py)

| items | plants caught / named | plant recall | Tier 1 judged wrong | real wrong | real minor |
|---|---|---|---|---|---|
| 28 | 5 / 5 | **1.00** | 0 / 3 | 0 / 20 (0.00) | 5 |

All 5 items judged wrong were plants. Each is a single-cell slip, and each was found by checking the cell in `Lexicon.cells()`:
- 6911accc: ACC.PL h₂énh₁mons used as the subject of 3sg Hrunépt ('the wind broke it').
- de5d75d5: IMP.3SG memóntu used for 'remember me' said to a 2sg addressee (IMP.2SG memn̥dʰí).
- 4a132e5b: NOM.PL poh₂iménes used for 'the song of the shepherds' (GEN.PL poh₂imnṓm).
- 66419242: fem. DAT/ABL.PL h₁étereh₂bʰos used as the subject 'the other one (path)'. It should be NOM.SG m. h₁éteros, since stéygʰs is masculine.
- 9309a7ac: PRS.1DU kh₂nówos used with the subject h₂néres 'the men' (3pl kh₂nónti).

## Real packet items: verdicts after lookup

| | wrong | minor |
|---|---|---|
| as scored | 0 / 20 | 5 |
| after lookup | 0 / 20 | 1 (lexicon) |

Four of the 5 minors were withdrawn after lookup, because the glosses support them:
- **19a04195 (00033), e7b4c3d0 (00019), 9f6af227 (00026):** I flagged 'unharmed' / 'safe' as added English. `pie-lex-nest` nést is glossed 'to escape, return home unharmed' (cf. Gk νόστος), so the English is right. The extra 'I too' in 00033 is a trivial English gloss.
- **2ae27d97 (00037):** I flagged réydʰeti 'rocks (you)' as a stretched sense. `pie-proj-reydheti` is glossed 'to ride; to move, swing, rock', so the sense is right.

One minor stands, and it comes from the lexicon. No plan was changed for it:
- **2a38a6ef (00012), 'Lead the first cow, and the others will follow … I will lead it'.** The tokens are h₂élyōs (m. NOM.PL) and h₁ím (m. ACC). `pie-lex-gwoxws` gʷṓws 'cattle' is m. only, and `pie-lex-h2elyos` is listed as a m. noun, so the agreement follows the lexicon. For a cow, Vedic gáuḥ and Greek βοῦς are feminine. **Lexicon note:** consider giving gʷṓws gender m/f, so that 'cow' can take feminine agreement (h₂élyeh₂es, h₁íh₂m̥). Report only.

## Blind back-translation (6 items)

Agreement was good on all six: the participants, the plot and the moods were recovered. These were the misses:
- **fa2fda40 (00029):**
  - h₂éwh₂e was read as 'grandfather', but the English has 'Uncle'. The gloss is 'maternal grandfather; maternal uncle', so both readings fit.
  - stéh₂dʰh₁eh₂ was unsure; it is the 'herds' plural.
  - h₃pusyéh₁t 'may increase' was read as 'flourish', which is close.
- **1f2adf5f (00007):** wékʷos 'word' was misread as 'horse' (h₁éḱwos). The text is correct.
- **a7b94d9f (00003):** I read úd stéygʰōwos as 'we climbed', but it is SBJV 'let us climb', and the later SBJVs as pasts. These are mood misreadings on my side.
- **efd56b90 (00004):** I took súHnew for 'dry'; it is VOC 'son'. ssdʰí 'sleep!' was unsure.
- **6911accc (planted; 00035):** ln̥dʰént 'sank' was left uncertain. The planted h₂énh₁mons was read as 'the winds' without noticing the case error, so the blind pass alone would not have caught that plant.
- **e7b4c3d0 (00019):** h₂énHe 'grandmother' was misread, and nésm̥ was given the wrong person. 'Grandfather kept guest-friendship' is my misreading of 'my uncle held my hand' (ǵʰóstom 'hand', not ǵʰóstis 'guest').

## Second pass: all 40 records

All 40 records were read in full against `planner-brief-v4.md` and the top part of `planner-brief-dialogue-inworld.md`.

**Wrong: none.**
- Nothing is modern or coined. The `pie-proj-*` project reconstructions (`pie-proj-spelom` spélom, `pie-proj-h2enHos` h₂énHos, `pie-proj-kjasnos` ḱásnos, `pie-proj-gwhermos` gʷʰermós, `pie-proj-poxlHos` pṓlHos, `pie-proj-reydheti` réydʰeti) are allowed.
- Every turn answers the one before it.

**The checklist:**
- **In-world, in character, two speakers of the PIE world:** all 40 pass. The speakers are kin, guests, ferrymen, a messenger, an exile, herders and children. The user always speaks first, and the vocatives and the speaker tags agree turn by turn. Examples: 00005 (the model is Of-True-Fame), 00011 (the model is the sister of the man at the ford), 00009 (the user is the returning lord).
- **Per-sentence English:** present on every sentence-initial clause, and it matches the PIE.
- **Pronouns track their referents:**
  - boat (f.) → h₁íh₂m̥ / h₁íh₂ / h₁ésyeh₂i (00028, 00035, 00040);
  - ice, wheel, star, foal, ox, foot, hand (m.) → h₁ím / h₁éy;
  - river, sea, bridge (n.) → h₁íd.
  - The only mismatch is the cow in 00012, which follows the lexicon (above).
- **Verb senses match their glosses.**
  - troméyeti is glossed 'tremble (in fear)', so it is not a causative.
  - skérdʰeti is 'become pierced', bʰoréyeti 'carry around', wodʰéyeti 'lead', dʰoréyeti 'hold', and sokʷéyeti 'say' (Gmc. *sagjan-).
  - No causative is used for a plain verb.
- **Verbs of fearing take the ablative everywhere:** wĺ̥kʷoybʰos (00003), nékʷts (00004), wédn̥s (00021), sruméns (00034), pérkʷunōd (00035). bʰéyh₂- has no object in 00012, 00018 and 00022.
- **Athematic nouns in oblique cases are correct:**
  - LOC: pr̥wéni (ford), péruni (mountain), ph₂wéni, dʰǵʰémi, kl̥Héni, ǵʰiméni, wésni, sruméni, ḱérdi, h₂Hséh₂i;
  - GEN/ABL: dʰǵʰmés, bʰr̥h₁wéns, h₃r̥nés, ugʷsnés, pedés, nékʷts, wédn̥s, méh₂tr̥s;
  - INS: h₂ḱm̥néh₁, ph₂tréh₁, drúh₁, h₃kʷbʰís;
  - LOC.PL: gʷéwsu, drúsu, pn̥th₁sú.
  - The number is right throughout: duals for feet, knees, eyes and two paths, and the plural for 'with my eyes' (INS).
- **Enclitics are in Wackernagel position throughout.**
- **Motion verbs:**
  - The goal is an accusative or próti + acc. Examples: dṓm, wóyḱom, móri, pérwōr, h₂éǵrons, dʰh₁tléh₂m, sóh₂wl̥, kéh₃tum, h₁réypeh₂m, kʷérom h₁n̥dó. dʰéǵʰōm is ACC.SG = NOM.SG in this paradigm (cf. Ved. kṣā́m).
  - The source is an ablative: wóyḱōd, kʷósmōd, h₂óǵmōd, déh₂nus.

**Engine notes (report only):**
- **00019, 'my uncle held my hand':** the plan has two enclitic POSS `closed:personal/1` slots, but the PIE has a single moy (h₂éwh₂os moy ǵʰóstom dʰoréyet). This is deliberate: the `_doubled_enclitics` docstring in `pie/realize.py` says that the same cell twice is merged by realize_clause. The result is still acceptable ('my uncle held the hand'), but the second 'my' is silent. A non-enclitic possessive (or `pie-lex-swos`) would keep it. No change was made.
- **The vocative `ph₂ter` (00012)** is written unaccented, as Vedic writes non-initial vocatives; it was not flagged. The batch file reports `accent_defect_tokens: 4` and `accent_representation_tokens: 1`. The tokens carry no accent field, so I could not identify those tokens. Not gate-relevant.

## Fixes and gate

- No plan errors were found, so `data/generation/plans/t050.jsonl` is unchanged and nothing was re-realized.
- The 5 wrong items were all plants. The corpus already has the right forms: h₂énh₁mos, memn̥dʰí, poh₂imnṓm, h₁éteros, kh₂nónti.
- Gate (`data/generation/batches/t050.json`): **PASS**, with 40/40 realized and all exact, reject_rate 0.0, max_lexeme_uses 7 ≤ 8, roots/sentence 4.93, and no duplicates.

## Release rule check (for the lead)

- Plant recall is 5/5 (≥ 4/5).
- Real items judged wrong are 0/20 after fixes (≤ 2/20).
- The gate is PASS.

All three conditions hold. Approval is left to the lead.
