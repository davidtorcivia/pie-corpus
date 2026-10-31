# Tier-3 review: batch t103 (horses and wagons, 40 in-world dialogues)

The reviewer followed `docs/generation/reviewer-brief.md` (review-v1). The packet was built with `scripts/make_review_packet.py t103 --n 20 --plants 5 --tier1 3`: 28 items, of which 20 are real, 5 are planted and 3 are Tier 1. Nothing under `data/audits/` was opened.

Order of work:
1. Blind back-translation of 6 items (`docs/audits/packets/t103-blind-translations.jsonl`), done from the `pie` field only, before any English was printed.
2. Verdicts on all 28 items (`docs/audits/packets/t103-verdicts.jsonl`). Forms were checked against a reverse index of every `Lexicon.cells()` form plus `closed_class.json`, and senses against the full glosses. The verdicts file was saved before `corpus/` or the plans were opened.
   - **Verdicts sha256:** `cd864fd814e99a16503319b4e60f31e4cfceb7ef71bf1c6ab00432f7d19e5d2f`
3. `resolve_review_items.py t103`, then `score_review.py t103`.
4. Second pass: all 40 records read in full against planner-brief-v4 and the in-world dialogue brief.

## Calibration

| plants caught | plant recall | real wrong | real minor | Tier 1 judged wrong |
|---|---|---|---|---|
| 4/5 | 0.80 | 0/20 | 2/20 | 0/3 |

Plants caught (each in a short turn, and each named with its fix):
- 40f60e9b: `kʷíd moy déh₃etes?` is a 2/3du subjunctive addressed to one man. It should be 2sg déh₃esi.
- 91d2513d: `misdʰóm wn̥tóm?` is a 2du aorist for "Did he win?". It should be 3sg wént, which the answer already has.
- 66190224: `dweh₂róybʰos h₂éǵrom` puts a dat./abl. plural adjective on an acc. sg. noun. It should be dweh₂róm.
- 3b7fb8ee: `gʷmih₁tā́m` is a 3du optative for "may you come back", said to one sister. It should be 2sg gʷm̥yéh₁s.

One plant was missed. Its key was not opened.

## Blind back-translation

All six items (40f60e9b, 39f2a2ed, 0041bb05, 336daecb, a4039fbd, 3a8808b4) agree with their English in substance. The differences:
- In 40f60e9b, h₁áyso was uncertain in the blind pass. It is the 2sg middle imperative of h₁ay- ("take").
- In 0041bb05, the blind pass read pérkʷum déh₂newi as "the oak, the river". The English has "the oak at the river".
- In 39f2a2ed, the blind pass read h₁éwkoh₂ as "I am used to it". The English has "I will learn", which the full gloss also gives.

The blind pass flagged the genitive yéwgesos with a verb of fearing. In an s-stem the genitive and ablative have the same form, and the plan sets ABL, so this is not an error.

## Real items: minor (packet)

- d026f003 (t3-t103-00033): `pṓds h₂égʰos` uses the neuter noun h₂égʰos "distress" as the predicate for "bad". The lexicon has the adjective h₂egʰós "bad, evil" (pie-lex-h2eghos-2). **Fixed.**
- 94082e79 (t3-t103-00010): spélom "story" is a project reconstruction. Project reconstructions are allowed in Tier 3; this is noted only.
- The Tier 1 items d73e665f (Schleicher 1868) and 55152a3a (Byrd 2013) are faithful to their sources. Their notation clashes with the corpus, as in t023.

## Second pass: all 40 records

**Structure.** A script checked every plan for the following, and all 40 pass:
- `speaker` on every clause;
- exactly two speakers, with `user` first;
- every speaker change starts a new sentence;
- per-sentence `english` on every sentence-initial clause and on no other clause, and these join to the plan's `english`;
- 4–14 clauses and 2–8 turns.

**Turn coherence.** Every turn answers or follows the one before it. Two are weak:
- 00026 ends with "This is the knife. Show me!", where it is unclear what is to be shown.
- 00013 has the host change the subject to food. This is normal hospitality.

Neither is counted as wrong.

**Mares.** Every mare slot is feminine, and so are its pronouns and adjectives. This was checked in 16 records, for example:
- ḱā́m h₁éḱwom, h₁íh₂m̥ (00014, 00028);
- ḱásneh₂ey h₁éḱwōy (00003);
- albʰā́s márkons, tā́s, téh₂sōm (00016);
- márkōs méǵh₂ih₂es (00022);
- HeHḱuyéh₂s márkosyo (00037);
- ǵr̥h₂éntih₂m h₁éḱwom (00040);
- dual dwóyh₁ ǵr̥h₂éntih₂h₁ gʷr̥déwih₂h₁ márkoh₁ (00006).

Grammatically masculine words for foals, stallions and mixed herds are correct where they occur.

**Races.** ǵénh₁os appears only inside the name deywóǵenh₁ēs "Of-Divine-Race" (00031), where it means lineage. It never means a contest. The race English matches the PIE:
- drive: h₁elh₂-, h₂eǵ-, ǵʰey-;
- win: wén-;
- take the prize: misdʰóm sléh₂gʷ-;
- "has passed": dʰégʷʰh₂t, whose full gloss includes "pass by".

**Anachronism.** Every vehicle is a wóǵʰos "wagon" with solid wheels: rótos, ǵómbʰos "peg", h₂éḱsis "axle", grease. There are no spokes and no chariot. One borderline case: dwirótos wóǵʰos "two-wheeled wagon" (00007) can be read as a cart and is acceptable. Riding (00019, 00024, 00027) is plausible for the period. Nothing is modern. The project reconstructions used (pṓlHos, ḱásnos, h₂énHos, spélom, kólsos) are allowed under planner-brief-v4.

**Formulas.** The batch report counts 7 records with formulas (9 hits). Checked one by one:
- Used in their sense:
  - h₁nómn̥ dʰeh₁- "set a name" (00003);
  - HeHḱús h₁éḱwos "swift horses" (00006, 00010);
  - déh₃tōr h₁uséwōm "giver of good things" (00006);
  - dyéw … ph₂ter "Father Sky" (00008);
  - h₂éwsōs diwés dʰugh₂tḗr "Dawn, daughter of Sky" (00010);
  - sh₂wéns kʷékʷlos "wheel of the sun" (00025);
  - ḱléwos ń̥dʰgʷʰitom "imperishable fame" (00037).
- Not a real use: "famous name" in 00012. There, ḱlutós modifies h₂eǵós "driver" and h₁nómn̥ stands in another sentence. The counter `_formula_uses` only tests whether the lexemes co-occur in a record, so it over-counts (reported below).

**Other checks.** All of these pass:
- **Verbs of fearing** take the ablative: yéwgesos and h₁ésmōd (00004), h₁ésmōd (00011), tósmōd (00019).
- **h₂élyos** is gendered: h₂élyons m. acc. pl. (00037).
- **Predicate adjectives** with dropped subjects agree: kéh₂ilos h₁ési/h₁ésmi for the son (00001); h₁íh₂ gʷr̥déwih₂ (00027).
- **Short answers** take the right case:
  - ACC: 00005, 00007, 00008, 00027, 00036, 00037, 00038;
  - LOC: 00030;
  - NOM: 00004, 00006, 00021, 00029, 00031.
- **Athematic obliques** are as the engine builds them: h₁wédmn̥ (nom./acc. only), sh₂iménh₁, kh₂n̥ménh₁, h₃sth₁éy, h₁sh₂éney, gʰr̥h₁méni, pr̥wéni, ph₂wéni, déh₃n̥bʰis, pérwōr.
- **Enclitics** stand in second position.
- **Reflexive swós** refers to the subject in every case except one (00039, below).

**Senses.** Doubtful senses were checked against the full glosses, and all are fine:
- márkos "horse; wild horse" (00024 "wild horse");
- h₂éwh₂os "maternal grandfather; maternal uncle";
- snusós "bride";
- tl̥h₂tóm "bridge, ford";
- stólos "seat, table";
- Hyowdʰéyeti "cause to move", which fits "the team does not move the wagon";
- h₁opéyeti "give";
- ǵómbʰos "peg";
- h₁éwkt "learn";
- dʰégʷʰh₂t "pass by".

Other minor points:
- 00002: bʰéndʰom is an imperfect for "I have tied". The verb has no aorist, so rule 8 allows it. Not fixed.
- 00008: sedéh₁yōnti was 3pl for the dropped neuter-plural subject "children", against 3sg sedéh₁yēti in the question before it. **Fixed** to 3sg, so the record follows the neuter-plural rule throughout.

**Project reconstructions (lead to confirm).** The lead's instructions say "count as wrong: anything modern or coined". This batch uses five project reconstructions (`coined: "project"`): pṓlHos "foal" ×19, ḱásnos "grey" ×4, h₂énHos "grandmother" ×3, kólsos "neck" ×2 and spélom "story" ×1. They are treated here as allowed, under planner-brief-v4 §Project reconstructions ("may be used in Tier 3 like any other lexeme"), and none is counted as wrong. If the lead reads "coined" as covering them, pṓlHos alone touches most of the batch, and the verdict changes.

## Fixes (plan file data/generation/plans/t103.jsonl)

| record | before | after | issue |
|---|---|---|---|
| t103-0015 | `h₁ésyo rótos h₂égʰos` | `h₁ésyo rótos h₂egʰós` | noun "distress" replaced by the adjective "bad" (pie-lex-h2eghos-2) |
| t103-0033 | `márkosyo pṓds h₂égʰos` | `márkosyo pṓds h₂egʰós` | same |
| t103-0039 | `swóm me ḱóymom wéǵʰet` | `méne me ḱóymom wéǵʰet` | **wrong:** reflexive swós refers to the subject (the horse), so the PIE says "his own village" where the English says "my village". Now POSS 1sg; the stressed form is used because the clause already has enclitic me (the checker rejects two 1sg enclitics). |
| t103-0008 | `méǵʰye ḱóm sedéh₁yōnti` | `méǵʰye ḱóm sedéh₁yēti` | 3pl → 3sg for the dropped neuter-plural subject, matching the question |

Counts:
- **Packet:** real wrong 0/20 before and after the fixes. Real minor 2/20 before; 1 after (h₂égʰos is fixed; spélom is only noted).
- **Second pass:** 1 meaning error, in 00039, which is not a packet item (its packet copy was the plant 91d2513d). Fixed at source, so 0 remain. Minors fixed: 00015 (h₂égʰos) and 00008.

**Re-realization:** `realize_plans.py data/generation/plans/t103.jsonl --batch t103 --model claude-opus-5-5 --prompt-id tier3-dialogue-inworld-v1`
- Result: 40/40 realized and exact, 0 rejects, gate **PASS**.
- Other numbers: max_lexeme_uses 7 (cap 7), theme_core_uses ≤22, formula_uses 7, 1450 tokens. h₁éḱwos is unchanged at 21 uses, one below the theme cap; no fix touched it.
- The first attempt at the 00039 fix used an enclitic POSS and was rejected (two 1sg enclitics). The second run passed, and so did the final run after the 00008 fix.

## Engine and report findings (report only)

1. **`_formula_uses` over-counts.** It counts a formula when its lexemes co-occur anywhere in a record. In 00012, ḱlutós and h₁nómn̥ stand in different sentences, so the batch figure of 7 is really 6 records.
2. **Leftover initial-run file.** `corpus/tier3/t103-initial.jsonl` is still present. Planner-brief-v4 says to delete it after the initial run. The reviewer left it in place; the lead should decide.
3. **Lexeme choice.** The noun h₂égʰos (pie-lex-h2eghos) and the adjective h₂egʰós (pie-lex-h2eghos-2) have the same spelling apart from the accent. lexq's "bad" returns only the adjective, but planners still reach the noun, perhaps through the slice. A slice or checker hint ("noun: distress; use -2 for 'bad'") would prevent this.

## Release-rule inputs

- Plant recall: 4/5.
- Real items judged wrong after the fixes: 0/20 in the packet, and 0 in the full batch (the one second-pass error is fixed).
- Project reconstructions are allowed under planner-brief-v4 but need the lead's confirmation (see above).
- Gate: PASS.

The release approval was not set.
