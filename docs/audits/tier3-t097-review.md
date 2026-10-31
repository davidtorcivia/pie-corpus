# Tier 3 batch t097 review (fields and harvest; 40 in-world dialogues)

Reviewer brief `review-v1`. Packet: `scripts/make_review_packet.py t097 --n 20 --plants 5 --tier1 3` (28 items).
I did the blind back-translation first (`docs/audits/packets/t097-blind-translations.jsonl`, 6 items) and printed
only the `pie` field. I saved the verdicts (`docs/audits/packets/t097-verdicts.jsonl`) before I opened corpus/ or
the plans. I did not read anything under data/audits/.

- **Verdicts sha256:** `a2a6ec08570b9c9b5f3757548c8e99879f021ddde1c3979a4631e63987304fab`
- **Score (`score_review.py`):** plant recall **5/5**, all 5 named correctly. 20 real items: 1 wrong, 9 minor.
  Tier 1: 0 of 3 judged wrong.
- **Gate after fixes:** PASS. 40/40 realized, reject rate 0.0, max lexeme uses 7 (cap 7), all_exact, 7 WARNs
  (all checked, below). The gate already passed before my run. The initial run's lexeme-cap failure had been
  repaired in `t097.jsonl`.

## Plants caught (in the packet's own spelling)
| item | what was wrong |
|---|---|
| f9034085 | *pótibʰos* is DAT/ABL.PL "to/from the masters". The address "Master" needs the vocative *pótey* |
| e2746fdc | *mórtōs-kʷe kénkome*: *kénkome* is PST.1PL, but the subject "men" needs 3PL *kénkont* |
| 2350f5fc | *kʷóti h₂erh₃tṓys … luHté*: INS.PL. "How many fields did you cut" needs ACC.PL *h₂erh₃tóns*, as in the answer |
| 9ac56eca | *nu toy dʰóHneh₂h₁ déh₃oh₂*: an INS.SG/NOM-ACC.DU form, with an accent not in the table. "I will give you bread" needs ACC.SG *dʰoHnéh₂m* |
| bf85d190 | *wédʰetām* is 3DU (PST/IMP). "Lead my oxen and plough!" is addressed to one person and needs IMP.2SG *wédʰe*; *h₂érh₃ye* beside it is 2SG |

## Blind back-translation
All 6 items (2eafdb07, dbca59fa, 731ee19e, b7d6cdb4, aa21a94b, 627629dd) agree with the packet English in
substance. The differences:
- *ḱéstreh₂* (b7d6cdb4): I read "knives", the packet has "blades". The gloss gives both, so this is fine.
- *dʰoHnéh₂* (731ee19e): I read "grain", the packet has "bread". This led to the bread fix below.
- *h₁ím* in aa21a94b: I marked it uncertain, since the masculine "it" follows neuter *ǵr̥h₂nóm*. Fixed below.
- *n̥bʰróm*: I read "rain-cloud", the packet has "rain". The gloss allows "rain".

## Real items: wrong and minor, with their resolution
| item → record | verdict | finding | resolution |
|---|---|---|---|
| 73900bc8 → 00010 | wrong | *ḱwṓ-kʷe h₁ím péh₂sti*: masc. *h₁ím* for the neuter grain *ǵr̥h₂nóm* | **fixed**: gender n → *h₁íd* |
| aa21a94b → 00025 | minor | *h₁ím … péh₂somes*: masc. "it" after neuter *ǵr̥h₂nóm* (one of the planner's WARNs) | **fixed**: gender n → *h₁íd* |
| 62542018 → 00031 | minor | "And the wheat?" echoes the object of "sow", but the np is NOM *puHrós* | **fixed**: `case: "ACC"` → *puHróm* |
| 731ee19e → 00029, 45c27dba → 00033, a9101f1e → 00009, f5f3ba82 → 00034 | minor | *dʰoHnéh₂* is glossed only "grain", but the English says "bread" | **fixed**: the English now says "grain" (also in 00022; titles of 00022/00033) |
| f5f3ba82 → 00034 | minor | *h₁áyto* MID.AOR for "receives" | **withdrawn**: h₁ayt- has only aorist cells, so it is a gnomic aorist (brief rule 8) |
| 7ba59295 → 00017 | minor | *pédt* AOR for "falls" | **withdrawn**: pédt has only aorist cells, so it is a gnomic aorist |
| b7d6cdb4 → 00007 | minor | "there by the stone" | **withdrawn**: *h₂én* is "there" and *h₁épi* is "on, at, near" |
| 7a4d2584 → 00012 | minor | *h₂énHos* is a project reconstruction | **withdrawn**: project reconstructions are allowed in Tier 3 (brief v4), and t096 treated them the same way |

Real items wrong: **1/20 before the fixes, 0/20 after**. Real minors: 9 items before, 0 after: 6 fixed and 3 withdrawn (7ba59295, b7d6cdb4, 7a4d2584). f5f3ba82's bread finding was fixed and its h₁áyto finding was withdrawn.

**Bread:** lexq has no PIE word for 'bread', only the paraphrase idiom *dʰoHnéh₂* 'grain (prepared as food)' (M&A 2006 §16.1). The plans use that idiom correctly, so the fix makes only the English literal.

## Second pass (all 40 records against planner-brief-v4 and the in-world dialogue brief)
I aligned each record to its plan clause by clause: speaker, per-sentence English, and realized token features.

**Wrong, fixed in `data/generation/plans/t097.jsonl`:**
- **00006** "Do you have milk *for them*, neighbour?": the PIE has no "for them" (*wóyḱe toy h₂mélǵos h₁ésti?*).
  The English is now "Do you have milk, neighbour?"
- **00008**: the sentence English "They tread the ears with their feet." left out its -kʷe clause
  *ǵr̥h₂nóm-kʷe h₁éǵʰs h₁nédʰt* "and the grain came forth". It now reads "They tread the ears with their feet, and the grain comes out."
- **00010**: pronoun gender (above).

**Minor, fixed:** 00025 pronoun gender; 00031 np case; "bread" → "grain" for *dʰoHnéh₂* in 00009, 00022, 00029,
00033 and 00034, including the 00022/00033 titles and themes; 00030 "*Our* neighbours gave us seed" had no
"our" in the PIE (*woyḱṓs nos … dh₃ént*), so it now reads "The neighbours gave us seed"; 00009's theme said
"barley" where the grain is *puHrós*, now "wheat".

**Checked and fine:**
- **Speakers and English:** I checked every record with a script. Each has a speaker on every clause and exactly
  user + model, with the user first. Every change of speaker starts a sentence, and every sentence-initial clause
  has its `english`. The joined English equals the plan's English. All records have 4–14 clauses and 2–8 turns.
  Every turn answers the one before.
- **Nothing modern.** The only project reconstructions are *h₂énHos* "grandmother", *mógʰus* "boy" and *spélom*
  "story", which are used as in t096.
- **The planner's paraphrases:**
  - *ḱéstrom* "knife; blade" for the sickle.
  - *bʰendʰ-* "bind" + *sh₂éymn̥* "rope" for sheaves.
  - Oxen treading the ears with *pedt-* "tread".
  - Winnowing as *úd Hyéh₁komes* + *h₂énh₁mos h₂élyeh₂ h₂epó bʰéreti*. Here *dérōmes* "separate" is in the
    gloss ("splitting, separating").
  - *pékʷ-* "cook; ripen".
  - Pots buried from the mice.

  In each the English now says what the PIE says. Other senses I checked against the full gloss:
  - *h₂éwh₂os* "maternal uncle" (00021 "Uncle")
  - *ǵénh₁mn̥* "offspring, seed"
  - *wetsós* "calf"
  - *ǵʰelh₃wós* "yellow"
  - *gʰrómos* "thunder"
  - *mā́dsos* "mush"
  - *h₂léh₁wr̥* "flour"
  - *ḱubʰrós* "clean"
  - *tewtéh₂* "heap"
  - *stéygʰ-* "climb"
  - *wóyḱos* "villager" → "neighbour"
  - *h₁áyt-* MID "take, receive"
- **Fearing takes the ablative:**
  - *tóybʰos bʰebʰóyh₂th₂e* (00001)
  - *h₂wíbʰos mē tréses* (00005)
  - *gʷoldʰṓd bʰebʰóyh₂h₂e* (00006)
  - *kh₂n̥mń̥bʰos bʰebʰih₂ḗr* (00003)
  - *pérkʷunōd trésesi* (00011)
  - *nékʷts bʰebʰóyh₂th₂e*, *ph₂wéns trésonti* (00025)
- **Formulas (4 counted):**
  - "Mother Earth" in 00012 (*dʰéǵʰom … méh₂ter h₂éle*) and 00038 (*dʰéǵʰōm nos méh₂tēr*), and "giver of good
    things" in 00026 (*h₁uséwōm … déh₃tores*). All three are used in their sense.
  - The 4th count, "Father Sky" in **00020**, is a false positive of `_formula_uses`. That record has *ph₂ter*
    (a human father) and *dyéwi Hn̥dʰí* "under the sky" in separate sentences, so there are really 3 uses.
- **Cows as female animals:**
  - *gʷówes* "the cows gave us milk" (00006, f).
  - *ǵr̥h₂éntih₂ gʷṓws* (00014, f).
  - *ǵr̥h₂éntih₂n̥s gʷṓs* (00036, f).
  - Oxen are m: *gʷówes … dukénti* (00015), *HeHḱéwes gʷówes* (00024), *gʷówh₁e wédʰe* (00027).
  - The generic "do you have cattle?" (00014) has no gender. Nothing agrees with it.
- **h₂élyos with gender:**
  - *h₂élyeh₂* n.pl "the other things" (00008)
  - *h₂élyos* m, for the wheat (00016)
  - *h₂élyōs* m.pl, for the bags (00019, *bʰólǵʰis* m)
  - *h₂élyod* n, for the seed (00021) and as MOD of *spélom* (00030)
  - *h₂élyeh₂m* f, for the grain *dʰoHnéh₂* (00022)
- **Predicate adjectives with dropped subjects:**
  - *gʷḗn kéh₂ileh₂ h₁sdʰí* (f)
  - *h₁súḱlewes kéh₂ilos h₁sdʰí* (m)
  - *gʰóstey … priHós h₁sdʰí*
  - *h₁yód péh₂ureh₂ h₁ésm̥*, for the girl speaker (00012, f)
- **Short answers:**
  - LOC *déh₂newi* (00001), *h₁wersóy h₂éǵroy* (00031)
  - ACC *káprom h₂mélǵos-kʷe* (00002), *dṓm* (00004), *h₁néwn̥ lóysās* (00024), *dwóh₁ bʰólǵʰih₁* (00037),
    *mā́dsom h₂ólut-kʷe* (00039)
  - GEN "my husband's and my sons'" (00004)
  - NOM for subject questions (00017)
  - 00031 is now ACC
- **Pronoun WARNs (7 after the fixes, 8 before):**
  - The 8 the planner left were in 00021, 00022, 00023, 00025, 00029 (×2), 00033 and 00034. I fixed 00025.
  - The rest are fine:
    - *tód* for a proposition (00021, 00033)
    - fem. *h₁íh₂m̥* for *dʰoHnéh₂* (00022, 00023)
    - the impersonal *h₂wérst* beside a VOC (00029)
    - neuter *h₁íd* "it (the rain/sound)" (00029)
    - *h₁íd* for *kéh₂nmn̥* (00034)
  - 00010's masculine *h₁ím* raised no WARN, and I fixed it.
- **Enclitics:** all *moy/toy/nos/me/te* stand in second position or right after a fronted VOC or question word.

## Engine / brief notes (report only; not fixed here)
1. **`_formula_uses` over-counts.** It counts a record that has the lexemes of a formula anywhere in the text
   (00020 "Father Sky"). It should require the formula's construction (adjacency or apposition), or be reported
   as a lexeme co-occurrence.
2. **Athematic obliques, one question:** ABL *déh₂nus* (00027) keeps the root in full grade, where a
   proterokinetic u-neuter would have *dh₂néws*. Please check the spec of pie-lex-deh2nu. The other obliques I
   saw (*kh₂n̥mń̥bʰos*, *sh₂imń̥bʰis*, *h₂wíbʰos*, acrostatic *bʰólǵʰis* GEN/ABL) are the expected patterns of
   their stem classes.
3. **wéwket:** the lexicon headword *wéwket* "say" (IMP *wéwke*) has no labiovelar. LIV has the reduplicated
   aorist *u̯é-u̯kʷ-e-*. Worth checking the entry.
4. **realize_plans does not check speakers or per-sentence English for Tier 3.** 00008's sentence English
   omitted a whole -kʷe clause and passed the gate. A check that every clause's content is covered by the sentence English would catch it.
