# Tier 3 batch t098 review (oaths, law and judgment; 40 in-world dialogues)

Reviewer brief `review-v1`. Packet: `make_review_packet.py t098 --n 20 --plants 5 --tier1 3` (28 items).
Verdicts file `docs/audits/packets/t098-verdicts.jsonl`, sha256
`a4f2430dd3a52b6a41547019436d142c574a630f857e8afce9c588a568b0c7a6`. I saved it before opening the corpus or the plans.
I did not read anything under data/audits/.

## Calibration (score_review.py)

| measure | value |
|---|---|
| plant recall | **5/5** (all named) |
| Tier 1 judged wrong | 0/3 |
| real items wrong | **0/20** |
| real items minor | 3/20, 2 after one was withdrawn (below) |

The five plants I caught:
- 3bd11160: `sémeh₂h₁` (INS/NOM.DU) where "the summer has gone" needs NOM.SG.
- 86e1b064: `stéh₂yete` (2PL) for "I did not steal".
- 4f86abdb: `kʷinéwonti` (3PL) for "if he does not pay".
- 15ee0406: `dʰl̥gʰṓh₂` (1SG) for "he too will owe".
- 5cbd02d2: `bʰh₂énti` (3PL) for "you speak what is true".

Minor items among the real ones:
- t3-t098-00020: `kʷóm-kʷe` "and when?" puts -kʷe on the fronted interrogative, where kʷómkʷe reads as the indefinite "whenever". Fixed.
- t3-t098-00031: the English "pay me the debt himself" has no PIE word for "himself". Fixed by dropping "himself" from the English.
- t3-t098-00034: `h₂énti` + LOC for "before the women". **Withdrawn.** The full gloss of h2enti is "opposite; near; in front", so the use is in sense. The same use in 00008 is also ok.

## Blind back-translation (6 items, `t098-blind-translations.jsonl`)

All six items were translated from the PIE alone. They agree with the English in substance.
- Two of the six turned out to be plants, and the blind pass already showed the slot that was wrong:
  - 3bd11160 (summer): the translator was unsure of the `sémeh₂h₁` form.
  - 5cbd02d2: `bʰh₂énti` read as a doubtful "speaking" form.
- 8898d1bd, 7a28b0e3 and f65c56ac were close matches.
- The remaining differences were the translator's own slips, not errors in the text:
  - `gʰr̥h₁méni` was read as "stone"; it means "grass".
  - The h₁suḱléwes address was misattributed.
  - `h₃eh₃óde` was read as "hated" and the following `ǵnéh₃meh₂m` as "kinship". The English has "judgment", which is the gloss.

## Second pass: all 40 records

Records were checked against planner-brief-v4 and the in-world dialogue brief.
- **Speakers and English:** every plan opens with the user and has exactly two speakers. Every speaker change starts a new sentence. Every sentence-initial clause has English, and the per-sentence English joins to the plan's English. Clause and turn counts are within the limits.
  - In 00001 the model asks "Will you follow his tracks?" and the user answers. This is coherent: the owner follows the tracks, the herdsman testifies. I left it unchanged.
- **Nothing modern or coined.** h₂énHos, spelom and pṓlHos are project reconstructions, which are allowed. Every turn answers the one before.
- **23 planner WARNs, checked one by one; none is real:**
  - 5 are "VOC near → 3rd person". Each clause really is 3rd person: 0014 "she took", 0022 "he asks", 0026 "he did", 0028 "it rained" (impersonal), 0031 "he went".
  - 17 are a neuter-singular so/ki pronoun for a whole statement ("this/that/it").
  - 1 is 0022 `h₂éǵs` "say", which is correct.
- **Verb senses** were checked against the full glosses. Two paraphrases from data/lexicon/idioms.json are used as their `how` says and say what the English says:
  - "Judge" is "show what is right": `h₃reǵtóm déyḱ-`, the lexq idiom.
  - "Witness" is "the one who saw".
  - Other paraphrases also stay in their glosses: "forgive" as "be kindly to him", "surety" as bʰoydʰéh₂ "pledge", "false oath" as "swear a lie".
  - Nothing is stretched past its gloss. The o-grade verbs moréyeti, h₁wogʷʰéyeti and h₁opéyeti carry plain senses in their glosses.
- **Lead note (lexq judge/oath/swear/witness/forgive/false):** lexq offers bʰoydʰéh₂, h₁óytos and h₃m̥néh₃ti, which t098 already uses in their own senses. "Judge" and "witness" come back as idioms that t098 already follows. Nothing comes back for forgive or false. **No word could replace a weaker paraphrase, so I changed nothing for this note.**
- **Fear verbs take the ablative:** h₁ésmōd (00004), deywóybʰos (00010) and pérkʷunōd (00021) are all correct.
- **Cows as female animals:** correct everywhere except 00012, where the APPOS "a hundred cows" was tagged masculine. Fixed (gender f). The surface form is unchanged.
- **h₂élyos** takes a gender in both uses: h₂élyās f (00003) and h₂élyons m (00033).
- **Predicate adjectives with dropped subjects:** 00038 kéh₂ilos (m, addressee) and 00040 h₁suménēs (f, the female speaker) are correct. The overt-subject cases are correct too (00023 h₁eǵóh₂ f, 00027 m).
- **Short answers take the asked case:** ACC in 00003, 00016, 00018 and 00017; LOC in 00006 and 00020; ABL in 00030; NOM where the answer is the subject. All correct.
- **Athematic obliques** follow the engine paradigms and are acceptable (h₃rēǵéy, dómn̥s, gʷnéh₂su, ḱunés, ǵʰiméns, ph₂wénh₁, tr̥méns, drúsu). Enclitics stand in second position.

## Wrong and minor counts

- **Packet:** 0 real items wrong, both before and after the fixes. Minor: 2 (00020, 00031), both fixed.
- **Second pass:** 0 wrong. 3 minor, all fixed in data/generation/plans/t098.jsonl:
  - 00012: the cow gender (above).
  - 00033: `kúdʰe-kʷe` "and where?" was the same -kʷe-on-interrogative construction as 00020. I passed it as ok in the packet (7a28b0e3) and fixed it here for consistency.
  - 00031: "himself" (above).
- **After the fixes:** 0 wrong, 0 minor known.

## Re-realization

`realize_plans.py ... --batch t098 --prompt-id tier3-dialogue-inworld-v1`: 40/40 realized, all exact, **gate PASS**. The highest lexeme count is 8, at the cap of 8. Compared with the corpus before the fixes, only 00012 (token gender), 00020, 00031 and 00033 changed.

## Engine and tooling notes (report only)

- **formula_uses = 5 overcounts.** 00010 "Father Sky" (the child's father and Dyēus) and 00012 "Mother Earth" (dʰǵʰémi … méh₂tēr) only have the formula's words in the same text; they are not uses of the formula. The real uses in their sense are 3: 00003 "Father Sky", 00005 "swift horse" and 00017 "giver of good things". `_formula_uses` should require the formula's words to be adjacent, or at least in the same phrase.
- **`conj: kʷe` on a clause that opens with a question word** attaches -kʷe to that word (kʷómkʷe, kúdʰekʷe), which reads as an indefinite. The engine could put it on the next word, or the checker could warn.
- **The paradigm of bʰṓr 'thief'** has zero-grade obliques (dat. bʰréy, gen. bʰrés). Lat. fūr-, Gk φωρ- point to a long vowel in every case, so these obliques are doubtful.

No release approval set; nothing committed.
