# Tier 3 batch b003: review of 50 sampled sentences

**Status:** provisional review from handbook knowledge, done without browsing. The judgements rest on Fortson, Ringe, Beekes, LIV², Mallory & Adams, and West (*Indo-European Poetry and Myth*) for hymnic style. Nothing was checked against the books in this pass.
**Date:** 2026-10-23
**Sample:** `docs/audits/tier3-b003-sample-50.jsonl` (50 records: myth 16, hymn 13, charm 13, prayer 8)

**Summary.**

| genre | ok | minor | wrong |
|---|---|---|---|
| myth | 15 | 1 | 0 |
| hymn | 10 | 2 | 1 |
| charm | 8 | 5 | 0 |
| prayer | 6 | 0 | 2 |
| **all (50)** | **39** | **8** | **3** |

- **Wrong rate:** 6% (3/50). All three wrong records come from lexicon glosses, not from the engine or from the new aorists:
  - *gʷegʷóme* "stand steady" is really the perfect of *gʷem-* "come" (T1), in 00061 and 00121;
  - the derived gloss of *bʰéh₃g-* "roast" was turned into "light (a fire)" (R1), in 00122.
- **Prayers:** both wrong prayers are gloss errors. The moods in them (OPT, SBJV, IMP) are right.
- **Batch-wide:** the same two causes touch 6 of 250 records (2.4%). That is the better estimate of the true wrong rate.
- **Aorists (the question for this batch):** the LIV² root aorists are well formed in every cell the batch uses, with one laryngeal bug in a single LIV entry (T7). They are also used correctly: in myth, 88 aorists against 32 imperfects, and every imperfect is either an English progressive or a root with no aorist. In b001 the ratio was 40 aorists to 110 imperfects. The S3 skew is gone.
- **Optatives and imperatives in prayers and charms:** the formation is right throughout (*-yéh₁-/-ih₁-*, thematic *-oyh₁-*, zero-grade *-dʰí*, *mē* + injunctive). The one mood defect is that negated wishes take *ne* instead of *mē* (T6, engine).
- **Minor:** the minors come from:
  - LIV duplicates of core verbs (T2);
  - a horse-word regression (Q2);
  - a ghost derivative (*mr̥wós*);
  - two accent-less spec stems (T3);
  - the animate/inanimate fire pair (T5);
  - T6.
- **Verdict:** scale, after the T1 regloss, the T6 negator rule and the LIV merge (T2/T4).

How to read the table:
- **Verdicts.** The scale is the same as in the pilot reviews and b001/b002.
  - *ok*: nothing a mainstream handbook would reject. A "Note" may still be given, but notes are not counted.
  - *minor*: a defect that leaves the sentence readable. Examples: a non-standard variant, a missing accent, a weak or duplicate lexeme choice, or a construction that has a better-attested alternative.
  - *wrong*: the PIE does not say the English, or a form is mis-inflected in a way that changes the reading.
- **Confidence** is my confidence in the verdict, not in the sentence.
- **Codes** in [brackets] point to "Systematic patterns" below. P-codes come from pilot 1, Q-codes from pilot 2, R-codes from b002, S-codes from b001, and T-codes are new in this batch.
- **Engine evidence.** To trace errors and count recurrences I checked:
  - `data/lexicon/lexicon.jsonl`, `data/lexicon/liv2.jsonl` (the 239 `source: liv2` entries with `aorist_weak`) and `data/morph/inflection_specs.jsonl`;
  - `data/morph/closed_class.json`;
  - `data/generation/plans/b003.jsonl`, `data/generation/slices/b003.json` and `docs/generation/planner-brief.md`;
  - `pie/classify.py`, `pie/morph.py` and `pie/realize.py`;
  - `corpus/tier3/b003.jsonl` (250 records).
- **Not counted as errors**, following the earlier reviews and the 2026-10-23 engine verification:
  - ACC.PL *-ns*;
  - thematic optative *-oyh₁-*;
  - middle 2PL *-dʰwe*;
  - i-stem LOC *-ēy*;
  - unassimilated *-dʰdʰí*, *-ddʰí* and *-dt-* clusters;
  - short-vowel root-aorist subjunctives (*péh₃omos*, *gʷʰéromos*) and long-vowel thematic subjunctives;
  - augmentless (injunctive-shaped) aorists and imperfects as narrative pasts;
  - boukólos delabialization (*wéwket*);
  - *tósyeh₂ey* (the handbook first variant; `closed_class.json` also lists *tésyeh₂ey*);
  - acrostatic DAT *h₃réǵey* (from the Wiktionary table).

## Per-record table

| id | verdict | form issues | meaning issues | syntax issues | confidence |
|---|---|---|---|---|---|
| t3-b003-00061 | **wrong** | none (*dʰéh₁ses* NOM.PL, cf. Arm. *dikʻ* "gods" < *\*dʰēses*; PRF.3PL *deduyḗr* follows the resonant-syllabification rule) | *gʷegʷmḗr* is the perfect of *gʷem-* "come". The lexicon's own reflexes (Ved. *jagāma*, Gmc *\*kwam*, Lat. *vēnī*, Av. *jaγmuš-*) all mean "has come/came". So the clause says "they have come", not "they are standing steady" [T1] | none | medium |
| t3-b003-00152 | minor | none (root-aorist IMP *l̥h₁dʰí* of LIV *leh₁-*; *litdʰí*) | *ǵʰéyos* (`attested_in` 2: Ved. *háya-*, Arm. *ji*) was chosen although *h₁éḱwos* (12) was in the slice. This breaks brief rule 9, and b001's "horse" fix has regressed [Q2] | none | medium |
| t3-b003-00140 | ok | none (VOC *stéwtor*, Ved. *stotar*; DAT *tósmey*; IMP *h₂ǵdʰí* of LIV 2.*h₂eǵ-* "say"; aorist OPT *ǵn̥h₃yéh₁t*, zero grade + *-yéh₁-*) | Note: "say a song" where *gʷéHye* "sing" was available. *kéh₂nmn̥* rests on Lat. *carmen* alone [S5] | none (the overt *só* marks the switch from 2nd to 3rd person) | high |
| t3-b003-00034 | minor | *duh₃dʰí* comes from LIV's separate root *deh₃u̯-* (Lat. *duim*, Cypr. δοϝεναι). No daughter has an imperative from it. The core *dh₃dʰí* (Ved. *dehí*) of *déh₃t* (`attested_in` 10) was in the slice [T2] | none (*ḱludʰí*, Ved. *śrudhí*, Gk κλῦθι: the inherited hymn opening; *h₂éwgmn̥*, Lat. *augmen*) | none (Wackernagel *nos* after *duh₃dʰí-kʷe*) | medium |
| t3-b003-00095 | ok | none (short-vowel SBJV *bʰéh₂omos* of an athematic stem; OPT.3PL *ǵn̥h₃ih₁ént* with plural *-ih₁-*) | none | none | high |
| t3-b003-00235 | ok | none (thematic aorist *widét*, root aorist *péh₃t*; m. *tóm* resumes m. *sokʷós*) | none (*spéḱs* "watcher", Ved. *spáś-*, Lat. *-spex*) | none | high |
| t3-b003-00155 | minor | VOC *ǵʰorneh₂* has no accent. Two causes: the spec's table stem has lost the headword accent, and eh₂ vocatives never get the initial-accent rule. The word is clause-initial, so expected *ǵʰórneh₂* [T3, P5] | none (*ḱr̥mh₂dʰí*, *tr̥pdʰí*) | none | high |
| t3-b003-00122 | **wrong** | Note: *bʰh₃gdʰí* treats *bʰeh₃g-* as an ablauting athematic present, but both reflexes are thematic. SBJV *gʷʰéromos* is fine | *bʰeh₃g-* means "roast, bake" (Gk φώγω "roast", Gmc *\*bakaną* "bake"). The derived gloss "to ignite, set fire to (for cooking?)" turns "light the fire" into "roast the fire" [R1] | none | medium |
| t3-b003-00161 | ok | none (nasal present *h₂linéHmi*; INS *sokʷóh₁*; aorist OPT *h₂wisyéh₁t* of LIV *h₂weys-*, cf. Gk ἀΐω; n. *tód* for n. *h₂ṓws*) | none | none | high |
| t3-b003-00149 | ok | none (VOC *ḱwón*; IMP *bʰéwdʰe*, *ḱléwse*) | none | none | high |
| t3-b003-00017 | ok | none (*stonh₂éyeti*, Ved. *stanáyati*, Lat. *tonat*; PRF.1PL *dedwimé* = Gk δέδιμεν) | none (stative perfect for "we are afraid") | none | high |
| t3-b003-00156 | ok | none (aorist IMP *pl̥h₁dʰí*, *sth₂dʰí*; VOC of the neuter *yókʷr̥* = NOM) | none | none | high |
| t3-b003-00004 | ok | none (initial-accent VOC *déywe*; *h₁ési*; *ǵn̥néh₃si*) | none | none | high |
| t3-b003-00233 | ok | none (imperfect *trémt*; LIV root aorist *bʰéyh₂t* "became afraid") | none (a stative imperfect followed by an ingressive aorist: the aspect contrast exactly). Note: *bʰénǵʰistHos* (Ved. *báṃhiṣṭha*, Gk πάχιστος) as a character follows the English | none | high |
| t3-b003-00215 | ok | none (f. *udréh₂*) | none | none | high |
| t3-b003-00121 | **wrong** | none (thematic OPT *trésoyh₁me*; perfect OPT *gʷegʷmih₁mé*) | *gʷegʷmih₁mé* is "may we have come", not "may we stand steady" [T1] | *ne* + wish optative. Gk μή + OPT and Indo-Iranian *mā́* point to *mē* [T6] | medium |
| t3-b003-00067 | ok | none (proterokinetic INS *kh₂nménh₁*; 3PL *ḱl̥nwénti*, Ved. *śṛṇvánti*) | Note: *kéh₂nmn̥* is attested in Latin only [S5] | none (*-kʷe* on the first word of clause 2) | high |
| t3-b003-00142 | ok | none (aorist INJ *gʰrébh₂s* after *mē*, the Vedic *mā́* + aorist-injunctive type; IMP *sh₁dʰí* of LIV *seh₁(i̯)-* "let go") | none | none | high |
| t3-b003-00060 | ok | none (IMP *l̥h₂pdʰí*; OPT.1PL *ǵn̥h₃ih₁mé*). Note: eh₂ VOC = NOM *lówksneh₂*. Gk νύμφα and Ved. *amba* suggest a short *-a*; this is a school difference (low confidence) | none | none | high |
| t3-b003-00050 | ok | none (LOC *h₂usési* = Ved. *uṣási*; LIV aorist *bʰéwdʰt*; imperfect *kh₂nét*) | none (aorist for the waking; the imperfect "sang" has no aorist in the slice) | Note: the overt *só* has no change of subject [P9] | high |
| t3-b003-00184 | minor | none (causative IMP *stoh₂éye*) | *ǵʰéyos* over *h₁éḱwos* [Q2] | none | medium |
| t3-b003-00245 | minor | ACC *sh₂eytlom* has no accent. The table spec stem *sh₂eytlo-* lost the headword's accent (*sh₂éytlom*) [T3] | *déh₃ut* (LIV *deh₃u̯-*, `attested_in` 0) was chosen over *déh₃t* (10) [T2]. LIV *h₃pews-* "become rich" is apt | none | medium |
| t3-b003-00139 | ok | none (perfect OPT *tetr̥pih₁mé*; root-aorist OPT *sh₂ih₁mé*) | none (two near-synonyms, as in the English) | none | medium |
| t3-b003-00236 | ok | none (LIV aorist *h₁épt*, Hitt. *ēpzi*; imperfect *gʷʰént*, correct under rule 11 because *gʷʰen-* has no root aorist) | Note: *dʰénwr̥* "bow" rests on Ved. *dhánvan*; Gk θέναρ and OHG *tenar* mean "palm" | none | medium |
| t3-b003-00141 | ok | none (ABL.PL *h₂éwibʰos*; *mē* + present INJ *gʷm̥yés*) | none (ABL with "go away from") | none | high |
| t3-b003-00243 | ok | none (LIV aorists *réh₁dʰt*, *térpt*) | Note: LIV glosses *reh₁dʰ-* as transitive "carry out successfully"; intransitive "succeed" is middle in Vedic (*rā́dhyate*). Low confidence | none | medium |
| t3-b003-00102 | ok | none (aorist OPT *suh₂dyéh₁t* of LIV *sweh₂d-*; aorist SBJV *péh₃omos*) | none | none | high |
| t3-b003-00164 | minor | none (VOC *mŕ̥we*; *mē* + aorist INJ *dʰégʷʰh₂s*; IMP *l̥gʰdʰí*) | *mr̥wós* is a tree-path back-projection of Celtic *\*marwos*. The lexicon's own *mr̥tós* entry marks that *-w-* as analogical (after *\*gʷih₃wós*). *mr̥tós* (Ved. *mṛtá-*, Gk βροτός) was not in the slice [S5, R3] | none | medium |
| t3-b003-00221 | ok | none (root aorist 3PL *h₁rént*; reduplicated aorist *wéwkont*, Gk εἶπον) | Note: "the two" is *dwoyṓs* (Hom. δοιοί "two, both") with a plural verb; the dual *dwóh₁* was not in the slice [Q2] | none | medium |
| t3-b003-00039 | ok | none (DAT *h₃réǵey*; LIV aorist *méwdt* "became joyful") | none | none | high |
| t3-b003-00232 | ok | none (ACC of goal *pértum*; imperfect *sísdet* "was sitting down") | none | none | high |
| t3-b003-00163 | ok | none (aorist OPT *n̥ḱyéh₁t*, LIV *neḱ-* "vanish", Ved. *naś-*; *pl̥h₁yéh₁t*) | Note: *dʰwḗsos* "possessed one" rests on Germanic alone (MHG *getwās* "ghost") [S5] | none | medium |
| t3-b003-00222 | ok | none (LIV *Hwérdʰt*, Ved. *vṛdh-*; *lémbʰt*) | Note: the slice offers three "seize" aorists (*gʰrébh₂t*, *h₁épt*, *lémbʰt*) [T2] | none | high |
| t3-b003-00134 | ok | none (LOC *ḱleytéh₂i*: the P3 fix holds; long-vowel SBJV *sísdōmos*, *h₂isḱṓmos*) | none | none | high |
| t3-b003-00100 | ok | none (causative IMP *woydéye* with a double ACC, cf. Ved. *vedáyati*; athematic SBJV *ǵn̥néh₃omos*) | Note: *deḱsiwós* is "right (hand), favourable" in most daughters (Gk δεξιός, Lat. *dexter*), so "what is right" in the moral sense is a stretch | none | medium |
| t3-b003-00190 | minor | none (thematic OPT *skérdʰoyh₁t*; aorist OPT *pl̥h₁yéh₁t*; f. *séh₂* resumes *ǵʰórneh₂*) | none | negated wish with *ne* + OPT; expected *mē* [T6] | medium-low |
| t3-b003-00238 | ok | none (LIV aorists *h₂éḱh₃t*, *séh₂t*; NOM/ACC.PL *h₂ógr̥h₂*) | Note: the lexicon gives *h₂ógr̥* "berry" no reflexes (cf. Goth. *akran*, W. *aeron*) | none | medium |
| t3-b003-00172 | ok | none (VOC *spér*; *mē* + INJ *tréms*; IMP *gʷíh₃we*) | none | none | high |
| t3-b003-00199 | ok | none (ACC of goal *bʰréh₁wr̥*; aorists *gʷéh₂t*, *péh₃t*) | none | none | high |
| t3-b003-00240 | ok | none (LIV aorist *yéwǵHt*; imperfect *stonh₂éyet*) | none | none | high |
| t3-b003-00041 | ok | none (VOC.PL = NOM.PL; *h₁sté*; IMP.2PL *h₁opéyete*) | none ("Waters, you are mothers" matches the Vedic *ā́po … mātáraḥ* address; West). Note: *h₁opéyete* "make reach" for "give" is the Wiktionary sense; *dh₃té* was available | none | high |
| t3-b003-00195 | ok | none (LIV aorist *h₂wérst*, Ved. *várṣati*) | none | none | high |
| t3-b003-00249 | ok | none (LOC *h₂éwsteroy*; LIV aorists *h₂wést*, *h₁élh₂t*, Gk ἤλασα; neuter s-stem ACC *yéwgos* = Gk ζεῦγος) | none (dawn "growing bright" with *h₂wes-*, as in Ved. *uṣás*/*vas-*) | none | high |
| t3-b003-00011 | minor | none | The deified fire is the animate *h₁n̥gʷnís* (Ved. *Agní-*, Lat. *ignis*). Calling the inanimate neuter *péh₂wr̥* "a god" goes against the animate/inanimate pair; both nouns were in the slice [T5] | none (n. *tód*) | medium-low |
| t3-b003-00078 | ok | none (long-vowel SBJV *h₂éryōmos*, *wr̥ǵyṓmos*) | none | none | high |
| t3-b003-00200 | ok | none (f. ACC *bʰoséh₂m*; *widét*, *méwdt*) | none | none | high |
| t3-b003-00008 | ok | none (LOC *kʷsépi*; m. *bʰeh₂nós* agrees with *h₂stḗr*) | none (*spéḱyomos* "keep looking at") | none | high |
| t3-b003-00069 | ok | none (LOC *wédni*, Hitt. *witeni*; LIV aorists *h₂wékst*, *bʰwéh₂t*) | Note: *dyéwmn̥* has no reflexes (Ved. *dyumná-* is a thematic neuter) [S5]. The English itself repeats "grew" | none | medium |
| t3-b003-00225 | ok | none (imperfect *stunédt*; MID aorist *bʰidtó* for intransitive "split": the S1 fix holds) | none | none | high |
| t3-b003-00153 | ok | none (IMP *gʷʰr̥dʰí*; *mē* + INJ *tréses*) | none | none | high |

## Systematic patterns

**Fixed since b001/b002, confirmed in this batch.**

| pattern | evidence (b003, 250 records) |
|---|---|
| S3 (imperfect as default past) | In myth, 88 AOR against 32 PST. All 32 imperfects are English progressives ("was trembling", "were lying down") or verbs whose root has no aorist in the slice (*gʷʰénti*, *stonh₂éyeti*, *gʷéHyeti*). All four real same-root pairs (*légʰyeti*/*légʰt*, *pléh₁dʰeti*/*pléh₁t*, *sédyeti* and *sísdeti*/*sédt*) are progressives, so the imperfect is right. Rule 11 works |
| S2 (perfect for past events) | 13 PRF.IND, all English present states (*dedwimé* "we are afraid", *dedórḱe*) |
| S1 (anticausatives) | MID for intransitive "split" and "break": *bʰidtó*, *bʰidn̥tó*, *Hrumptó*, *Hrumpih₁tó*. 18 MID tokens in the batch |
| P10 (unaccented headwords) | 0 tokens from unaccented headwords. The only accentless forms come from spec stems (T3) |
| R1 (derived glosses) | 11 `gloss_approximate` lexemes in 31 records. All but one fit (*kh₂néti*, *stéwtōr*, *gʷéHyeti*, *moldʰéyeti*, *h₁yáǵyeti*, *stonh₂éyeti*). The exception is *bʰéh₃gti* (below) |
| P3, P8, Q1 | LOC *ḱleytéh₂i*; *mē* + injunctive in all 22 prohibitions; deponent *ḱéytor* in MID |

Also right throughout the sample:
- case roles: ABL of separation, ACC of goal, INS, LOC, DAT of the recipient;
- *-kʷe* placement;
- Wackernagel enclitics;
- anaphor gender (*tód* for neuters, *séh₂* for *ǵʰórneh₂*, *tóm* for *sokʷós*).

**The LIV aorists (main question of this batch).**
- **Use:** 170 tokens from 52 LIV lexemes, in 129 of 250 records.
- **Cells checked:** every cell the batch uses was checked against the handbook root-aorist paradigm. All are well formed:
  - **Indicative:** 3SG full grade + *-t* (*bʰéyh₂t*, *méwdt*, *h₂wérst*); 3PL zero grade + *-ént* (*h₁rént*, *bʰuh₂ént*, *ml̥h₃ént*).
  - **Imperative:** 2SG zero grade + *-dʰí* (*pl̥h₁dʰí*, *ḱludʰí*, and *pih₃dʰí* = Gk πῖθι); 2PL zero grade + *-té* (*h₂wisté*, *mudté* = Gk κλῦτε type); 3SG full grade + *-tu* (*ḱléwtu*, Ved. *śrótu*).
  - **Optative:** SG *-yéh₁-*, PL *-ih₁-*, both on the zero grade (*n̥ḱyéh₁t*, *ǵn̥h₃ih₁ént*).
  - **Injunctive:** full grade after *mē* (*gʰrébh₂s*, *dʰégʷʰh₂s*, *léyts*).
  - **Subjunctive:** short-vowel (*méwdomos*).
- **Meaning:** LIV's ingressive glosses ("become afraid / joyful / bright / sated") give exactly the right reading for single past events in myth (*bʰéyh₂t* "became afraid" after *trémt* "was trembling").
- **Defects:** the problems are in how the LIV entries were merged into the lexicon (T2, T4, T7), not in the paradigms.

**T1. *gʷegʷóme* is glossed "to have the feet planted, to stand steady" (new; lexicon gloss; the main source of *wrong*).**
- The perfect of *gʷem-* "come" means "has come, is here". The lexicon's own reflexes show this: Ved. *jagā́ma*, Gmc *\*kwam*, Lat. *vēnī*, Av. *jaγmuš-*, Toch. B *kekamu*. No daughter has "stand firm". The Wiktionary gloss reads a theoretical stative into it; the Greek "stand firm" perfect βέβηκα belongs to *gʷeh₂-*.
- **Count:** 5 records (00061, 00121, 00125, 00127, 00154), all for "stand steady/firm", including IMP *gʷegʷm̥dʰí* and OPT *gʷegʷmih₁mé*. Counted *wrong* in 00061 and 00121.
- **Fixes:**
  1. Regloss it as "to have come, to be present".
  2. Use *stestóh₂e* "to be standing" (Ved. *tasthau*, Gk ἕστηκα) for "stand firm". It was in the b003 slice and is used correctly in 00023 and 00054, so the misleading gloss is the only reason the planner reached for *gʷegʷóme*.
  3. Re-realize the 5 records.

**R1 (recurs, once). A derived gloss contradicts the reflexes.**
- *bʰéh₃gti* is glossed "to ignite, set fire to (for cooking?)" [-ti], but Gk φώγω means "roast" and Gmc *\*bakaną* "bake". In 00122, "light the fire" comes out as "roast the fire" (*wrong*). It is also a `tree_path` derivative with no `meaning` and an athematic shape that neither reflex supports.
- **Count:** 1 record.
- **Fix:** block it, or regloss it as "to roast, bake". Require `attested_in` ≥ 2 for the bare *-ti* label as well (b002's R1 gate covered *-os*, *-nós* and *-yeti*).

**T2. LIV entries duplicate core lemmas and bypass rule 9 (new; LIV merge + planner).**
- **Mechanism:** every LIV lexeme has `attested_in` 0 in the slice, because LIV entries carry no reflex list. Rule 9 ("prefer the higher `attested_in`") cannot rank them, and the planner does not apply it.
- **Duplicates in the b003 slice:**
  - "give": *déh₃ut* (LIV *deh₃u̯-*, 0) vs *déh₃t* (10);
  - "drink": *péh₃t* (LIV *peh₃(i̯)-*, `pie-lex-peh3t-2`, 0) vs *péh₃t* (Wiktionary, 5). The 3SG forms are identical but the imperatives differ (*pih₃dʰí* vs *ph₃té*);
  - "hear": *h₂wéyst* (0) vs *ḱléwt* (9);
  - "seize": *gʰrébh₂t*, *h₁épt*, *lémbʰt*;
  - "let go": *léh₁t*, *séh₁t*;
  - "come forth": *h₁nédʰt*, *mélh₃t*.
- **Count:**
  - *déh₃ut* in 6 records (00034, 00082, 00197, 00201, 00245, 00250). It is counted *minor*: LIV itself treats *deh₃u̯-* as a marginal by-root, and *duh₃dʰí* has no daughter support.
  - *péh₃t-2* in 4 records and *h₂wéyst* in 6. Not counted: these are good roots.
- **Fixes:**
  1. When a LIV root matches an existing Wiktionary lemma of the same root and meaning, attach `aorist_weak` to that lemma instead of creating `-2` lemmas. LIV's *pih₃-* is the better weak stem for "drink".
  2. Give LIV entries an `attested_in` from the branches LIV cites, so rule 9 can rank them.
  3. Keep *deh₃u̯-* out of slices.

**T3. Table spec stems with a wrong accent (new; spec).**
- Three noun specs have an accentless stem under an accented headword: *ǵʰorneh₂* (*ǵʰórneh₂*), *sh₂eytlo-* (*sh₂éytlom*) and *h₃migʰleh₂*. This gives ACC *sh₂eytlom* and *ǵʰorneh₂m*, and VOC *ǵʰorneh₂*.
- The verb spec of *bʰúHt* has weak = *bʰúH* (accented), which gives OPT *bʰúHyeh₁t* (00064) instead of *bʰuHyéh₁t* (Ved. *bhūyā́t*; compare the correct *bʰuh₂yéh₁t*). Its `extra_specs` already holds the unaccented *bʰuH*.
- **Count:** 7 records (00079, 00083, 00245, 00250, 00155, 00160, 00064). In the sample: 00155 and 00245.
- **Fixes:**
  1. When a table stem has no accent, copy the headword accent into it.
  2. For root aorists, take the weak stem without accent (prefer the `extra_specs` variant).

**T4. LIV homographs are linked to the wrong root (new; LIV merge; metadata).**
- The form-based match attaches LIV entries to a Wiktionary root of the same shape, ignoring LIV's homograph numbers:
  - *h₂wést* "become bright" (1.*h₂u̯es-*) → `pie-root-h2wes-dwell`;
  - *dʰéh₁t* "place" (*dʰeh₁-*) → `pie-root-dheh1y-suckle`;
  - *h₂éǵt* "say" (2.*h₂eǵ-*) → `pie-root-h2egj-drive`;
  - *stéwdt* "become cold" (2.*steu̯d-*) → `pie-root-stewd-push`.
  - The roots of *ḱérh₂t*, *dʰémbʰt*, *skélHt* and *wénHt* carry two or three LIV homographs each.
- **Count:** 11 records have a wrong `root_id` on a token and in `roots` (00002, 00030, 00087, 00140, 00158, 00198, 00208, 00214, 00220, 00230, 00249). No sentence is wrong because of it, since the planner chose by gloss.
- **Risk:** the same link drives rule 11 ("use AOR when the slice has an aorist of that root"). It currently offers *stéwdt* "became cold" as the aorist of *stunédti* "hit", and *h₂éǵt* "said" as the aorist of *h₂éǵeti* "drive". A checker that enforced rule 11 would introduce errors.
- **Fixes:**
  1. Match on homograph number plus gloss.
  2. Create a separate root id for each LIV homograph.
  3. Re-derive `roots` for the 11 records.

**T5. Inanimate *péh₂wr̥* is personified (new; slice gloss + planner).**
- The animate/inanimate pairs are *h₁n̥gʷnís*/*péh₂wr̥* and *h₂ép-*/*wódr̥*. The deified, addressed fire is *h₁n̥gʷnís* (Ved. *Agní-*).
- **Count:** 3 records treat *péh₂wr̥* as a person: 00011 "Fire is a god", 00043 "Fire is the brother of the waters", 00165 VOC *péh₂wr̥* "Fire, burn the thief". Counted *minor* in 00011.
- The planner handles the pair correctly elsewhere (VOC *h₁ń̥gʷni*, "let us praise Fire" *h₁n̥gʷním*).
- **Fix:** gloss the pair in slices as "fire (the element; inanimate)" and "fire, Agni (animate, deified; use for address and praise)".

**T6. Negated wishes get *ne* + optative (new; engine).**
- `pie/realize.py:373` picks *mē* only for `neg` + IMP, and *ne* for everything else.
- Negative wishes are *mē* + optative in Greek (μὴ γένοιτο) and *mā́* in Indo-Iranian. *ne* + optative is the potential ("would not").
- **Count:** 9 records (00091, 00108, 00121, 00132, 00169, 00176, 00179, 00188, 00190). Counted *minor* in 00190 (00121 is already *wrong* from T1).
- **Fix:** use *mē* for `neg` + OPT (and for a negated hortative SBJV, of which there is none yet), and re-realize the 9 records. Confidence: medium; some handbooks allow *ne* + OPT for wishes as well.

**T7. A LIV weak stem without its initial laryngeal (new; LIV entry).**
- LIV prints *h₃pews-* with the weak aorist *pus-* (its own present is *h₃pus-i̯é-*), so `aorist_weak` is "pus". This gives OPT *pusih₁mé* (00118) instead of *h₃pusih₁mé*.
- **Count:** 1 of the 239 LIV entries with `aorist_weak`; 1 record.
- **Fix:** when the strong stem begins with a laryngeal and `aorist_weak` does not, prefix it, or correct the entry by hand.

**R2 (recurs through a new route). Neuter s-stems declined as thematic masculines.**
- The b002 fix routes an *-os* noun to the s-stem when `stems` shows *-es*. The test in `pie/classify.py` (around line 159) is `x.endswith(("esos", "és", "es"))`, but Wiktionary tree-path stems are written with a trailing hyphen (*sélpes-*), so they never match.
- **Batch:** *sélpos* "fat" (Gk ἔλπος n.) comes out as ACC *sélpom* and INS *sélpoh₁* in **4 records** (00105, 00159, 00160, 00180). Expected ACC *sélpos*, INS *sélpesh₁*.
- **Lexicon:** 16 lexemes are misrouted the same way, among them *spéndos*, *swéydos*, *téḱos*, *tyégʷos*, *témh₁nos* (Gk τέμενος), *sméros*, *bʰéh₂wos* and *yéh₂os*.
- **Fix:** apply `.rstrip("-")` to each stem before the `endswith` test, then re-realize the 4 records.

**P5 (recurs, engine). Vocatives without the initial accent.**
- **eh₂ vocatives:** `_eh2` in `pie/morph.py` sets VOC.SG = NOM and never calls `_initial_accent`. Result: *albʰéh₂*, *bʰeh₂néh₂*, *kr̥snéh₂*, *bʰardʰéh₂* (00058, 00059, 00070, 00175), and the accentless *ǵʰorneh₂* (00155, with T3).
- **Laryngeal first syllable:** `_initial_accent` skips a syllabic laryngeal, so *ph₂tér* stays final-accented (00035, 00092). Ved. *pítar* and Gk πάτερ require *ph₂́ter* (written *ph₂ter* or *pə́ter*, depending on notation).
- **Count:** 6 records, plus 00155.
- **Fix:**
  1. Call `_initial_accent` for the VOC.SG in `_eh2`.
  2. In `_initial_accent`, accept an interconsonantal laryngeal as the first syllable (or choose a notation for its accent).

**Q2 (regression). *ǵʰéyos* "horse".**
- b001 reported *h₁éḱwos* 6/6 after the Q2 fix. b003 has *ǵʰéyos* in **6 records** (00114, 00136, 00148, 00151, 00152, 00184) against *h₁éḱwos* in 5, with both in the slice.
- Counted *minor* in 00152 and 00184 (rule 9 broken, as with b002's *gʷéyh₃ti*).
- Also: "the two" uses *dwoyós* (00221, 00234) because the dual *dwóh₁* was not in the slice. Not counted.
- **Fix:** keep *ǵʰéyos* out of slices that contain *h₁éḱwos*, and add a plan-checker warning when a lexeme is chosen over a same-gloss lexeme with `attested_in` at least 3 higher.

**S5 / R3 (recur). Thin tree-path derivatives without their core synonym.**
- **Ghost lexeme:** *mr̥wós* "dead" is a back-projection of Celtic *\*marwos*. The lexicon's own *mr̥tós* entry marks that form as analogical. *mr̥tós* was not in the slice. Used in **6 records** (00164, 00176, 00189, 00213, 00217, 00226); counted *minor* in 00164.
- **Single-branch or reflexless lexemes (notes only):**
  - *dʰwḗsos* (Germanic only, 6 records);
  - *kéh₂nmn̥* (Latin only, 6);
  - *dyéwmn̥* (no reflexes, 2);
  - *h₂ógr̥* (no reflexes, 3).
- **Overall:** 78 derivative tokens in 63 records.
- **Fix:**
  1. Drop a tree-path derivative when a `word` lexeme of the same root and gloss exists (*mr̥tós*), or when its only reflex carries an "analogical" note.
  2. Apply R3's attestation gate to tree-path nouns too.

**Low-confidence observations (not counted):**
- *deduyḗr* vs *dedwiyḗr*: a syllabification convention.
- eh₂ vocative = NOM vs a short *-a*.
- Intransitive *réh₁dʰt* "succeeded" (00243).
- *deḱsiwós* "what is right" (00100, 00099).
- *dʰénwr̥* "bow".
- *h₁opéyete* "give".
- Overt *só* in 00050 [P9].

## Counts

| verdict | n | records |
|---|---|---|
| ok | 39 | |
| minor | 8 | 00152, 00034, 00155, 00184, 00245, 00164, 00190, 00011 |
| wrong | 3 | 00061, 00121, 00122 |

| genre | n | ok | minor | wrong |
|---|---|---|---|---|
| myth | 16 | 15 | 1 (00245) | 0 |
| hymn | 13 | 10 | 2 (00034, 00011) | 1 (00061) |
| charm | 13 | 8 | 5 (00152, 00155, 00184, 00164, 00190) | 0 |
| prayer | 8 | 6 | 0 | 2 (00121, 00122) |
| **all** | **50** | **39** | **8** | **3** |

| issue kind (records with at least one counted issue) | n | records |
|---|---|---|
| form | 3 | 00034, 00155, 00245 |
| meaning | 8 | 00061, 00121, 00122, 00152, 00184, 00245, 00164, 00011 |
| syntax | 2 | 00121, 00190 |

Records touched, by pattern (counted issues only):

| pattern | sample | full batch (250) | source |
|---|---|---|---|
| T1 *gʷegʷóme* "stand steady" | 2 (00061, 00121) | 5 | lexicon gloss (Wiktionary) |
| R1 derived gloss | 1 (00122) | 1 | derived gloss |
| T2 LIV duplicate (*déh₃ut*) | 2 (00034, 00245) | 6 (*déh₃ut*); 16 counting *péh₃t-2* and *h₂wéyst* | LIV merge + planner (rule 9) |
| T3 spec stem accent | 2 (00155, 00245) | 7 | spec (table) |
| T4 LIV root mislink | 0 visible | 11 (`roots` metadata) | LIV merge |
| T5 inanimate fire personified | 1 (00011) | 3 | slice gloss + planner |
| T6 *ne* + wish OPT | 2 (00121, 00190) | 9 | engine (`realize.py`) |
| T7 LIV weak stem | 0 | 1 | LIV entry |
| R2 s-stem as thematic | 0 | 4 (16 lexemes misrouted) | engine classifier |
| P5 VOC accent | 1 (00155) | 7 | engine (`morph.py`) |
| Q2 *ǵʰéyos* | 2 (00152, 00184) | 6 | slice + planner |
| S5/R3 *mr̥wós* | 1 (00164) | 6 | lexicon (tree path) + slice |

## Verdict on scaling

- **Wrong rate:** **3/50 = 6%** (Wilson 95% interval about 2–16%).
  - The batch-wide count of wrong-type errors is 6/250 (2.4%: T1 ×5, R1 ×1).
  - For comparison: pilot 1 10%, pilot 2 2%, b001 4%, b002 4% (b002's batch-wide estimate was 6–9%).
  - Against the threshold "under 10% wrong, and every wrong traced to a fixable cause", **b003 passes: scale.**
- **Causes of the wrong records:**
  - All 3 come from two lexicon glosses, *gʷegʷóme* and *bʰéh₃gti*. The fix is one gloss change and one block, plus re-realizing 6 records.
  - None comes from the LIV aorists, the engine, or case/role assignment.
- **The LIV addition is a success for the corpus:**
  - Narrative tense is now balanced (88 aorists against 32 imperfects in myth).
  - Every aorist paradigm cell the batch uses is handbook-correct.
  - Prayers and charms finally use the aorist imperative and optative (62 AOR IMP and 53 AOR OPT tokens in the batch).
  - Its costs are in the merge step: duplicates (T2), homograph mislinks (T4) and one stripped laryngeal (T7). They are cheap to fix and should be fixed before LIV coverage grows further.
- **The minor mass (16%)** is spread over small mechanical causes: T2, T3, T6, Q2 and *mr̥wós*. Most are one-line fixes.
- **Recommended before b004 scales:**
  1. Regloss *gʷegʷóme* "to have come, be present" and block or regloss *bʰéh₃gti* (T1, R1). Re-realize the 6 records.
  2. Merge each LIV aorist into the existing lemma of its root, link LIV homographs by number and gloss, and give LIV entries an `attested_in` (T2, T4, T7). Rule 11 depends on correct root links.
  3. Engine one-liners:
     - *mē* for negated OPT (T6, 9 records);
     - initial-accent VOC for eh₂ stems and laryngeal-initial syllables (P5);
     - `.rstrip("-")` in the s-stem test (R2, 16 lexemes);
     - headword accent copied into accentless table stems (T3).
