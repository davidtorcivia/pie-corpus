# Tier 3 batch b001: review of 50 sampled sentences

**Status:** provisional review from handbook knowledge, done without browsing. The judgements rest on Fortson, Ringe, Beekes, Mallory & Adams and LIV, and nothing was checked against the books in this pass.
**Date:** 2026-10-23
**Sample:** `docs/audits/tier3-b001-sample-50.jsonl` (50 records: epic 24, dialogue 12, riddle 8, law 6)

**Summary.**

| genre | ok | minor | wrong |
|---|---|---|---|
| epic | 16 | 7 | 1 |
| dialogue | 10 | 1 | 1 |
| riddle | 6 | 2 | 0 |
| law | 6 | 0 | 0 |
| **all (50)** | **38** | **10** | **2** |

- **Wrong rate:** 4%. Both wrong records come from one planner/gloss cause (S1, active voice for "the wheel breaks"). No wrong record traces to the engine.
- **Minor:** most of the minors are unaccented or tree-derived lexemes (P10, S5), plus tense/aspect choices (S2, S3).
- **Verdict:** scale, after the S1 fix.

How to read the table:
- **Verdicts.** The scale is the same as in the pilot reviews (`tier3-pilot-review.md`, `tier3-pilot2-review.md`).
  - *ok*: nothing a mainstream handbook would reject. A "Note" may still be given, but notes are not counted.
  - *minor*: a defect that leaves the sentence readable. Examples: a non-standard variant, a missing accent, a weak lexeme choice, or a tense/aspect choice that shifts the nuance without changing what happened.
  - *wrong*: the PIE does not say the English, or a form is mis-inflected in a way that changes the reading.
- **Confidence** is my confidence in the verdict, not in the sentence.
- **Codes** in [brackets] point to "Systematic patterns" below. P-codes come from pilot 1, Q-codes from pilot 2, and S-codes are new in this batch.
- **Engine evidence.** To trace errors and count recurrences I checked:
  - `data/lexicon/lexicon.jsonl` and `data/morph/inflection_specs.jsonl`;
  - `data/morph/closed_class.json`;
  - `data/generation/plans/b001.jsonl` and `data/generation/slices/b001.json` (which features the planner was offered);
  - `corpus/tier3/b001.jsonl` (250 records);
  - `pie/morph.py` (`_locative`, the GEN.SG rule) and `tests/data/golden_paradigms.json`.

  The verdicts themselves are argued from the grammar.
- **Not counted as errors**, following the conventions of the earlier reviews and the 2026-10-23 engine verification:
  - *-dt-* clusters (*sédt*, *h₁édt*, *bʰéydt*, *stunédti*);
  - thematic DAT *-ōy*;
  - long-vowel thematic subjunctives and short-vowel root-aorist subjunctives (*déh₃eti*);
  - ACC.PL *-ns*;
  - GEN.SG without *-ós*.

## Per-record table

| id | verdict | form issues | meaning issues | syntax issues | confidence |
|---|---|---|---|---|---|
| t3-b001-00230 | ok | none (*h₁rṓs* m. (cf. Lat. *rōs* m.) with m. *swéh₂dus*; imperfect *h₁ést*) | none | none | high |
| t3-b001-00206 | minor | none (proterokinetic GEN *gʷtéws*: good) | *tr̥nós* "sharp" has no adjectival reflex. In the daughters it is a noun: Gmc *\*þurnuz* "thorn", OCS *trŭnŭ*, Ved. *tṛ́ṇa-* "blade of grass". *h₂eḱrós* "sharp" was in the slice and is attested in 6 branches [Q2] | none | medium |
| t3-b001-00214 | minor | LOC *h₂éḱri* is the bare weak stem with no ending. The handbook i-stem locative is *-ey/-ēy* (Fortson; Ved. *-ā/-au*, Hom. *-ηι*), so expected *h₂éḱrey* [S4] | *spéḱyet* is "was looking at, watching" (the lexicon gloss is "keep looking at"). "It saw the duck" is a perception, and *widét* "saw, caught sight of" was in the slice [S3] | none (VSO with a clause-level *-kʷe*: good) | medium-low |
| t3-b001-00006 | ok | none (*diwés* ABL, thematic aorist *widét*, ACC *tóm*) | none (imperfect *kapyét* "was gripping" is exactly the English). Note: *moysós* is the only "sheep/ram" word in the slice; *h₂ówis* was not offered [Q2] | none | high |
| t3-b001-00035 | ok | none (*wédʰēti* long-vowel SBJV; *déh₃eti*; DAT *h₁esh₂ṓy*; devi ACC *pótnih₂m̥*). Note: the spec tags *pótnih₂* as m. This has no visible effect here [S6] | Note: *wédʰmn̥* "bride price" has no reflexes in the lexicon. Gk ἕδνα points to *\*(h₁)wedʰ-no-* [S5]. The pairing *wédʰ-* "lead home (a bride)" … *wédʰmn̥* is a nice touch | none (*yo-*/*so-* correlative, SBJV in a general relative: good) | medium |
| t3-b001-00196 | ok | none | none (dative of possession for "was with": idiomatic) | none | medium |
| t3-b001-00197 | ok | none (*h₁ludʰét*, Gk ἤλυθε, OIr. *luid*) | none (*kóryos* collective "army") | none (ACC of goal *térmn̥*) | high |
| t3-b001-00125 | ok | none | none | none | high |
| t3-b001-00229 | ok | none (imperfect *ǵn̥néh₃t*) | none (*dʰéh₁mn̥* "ordinance": cf. Ved. *dhā́man* "statute") | none (*-kʷe* after the first word of clause 2) | medium |
| t3-b001-00056 | ok | none (IMP.3SG *ḱléwsetu*) | none | none | high |
| t3-b001-00237 | **wrong** | none (*Hru-né-p-t*: well formed) | Active *Hrunépt* is transitive ("was breaking [something]"; Ved. *lumpáti*, Lat. *rumpō*). "The wheel was breaking" is anticausative and needs the middle (cf. Ved. *lumpáte*, Lat. *rumpitur*). MID was offered in the slice [S1] | none | medium |
| t3-b001-00127 | ok | none (2SG perfect *dedórḱth₂e*, Ved. *dadárśitha*) | none (perfect for "have you seen" is the right use). Note: Gk οἶδμα has *o*-grade, against the headword's *e*-grade *h₂éydmn̥*; the lexeme is thin [S5] | none (fronted object in a question) | medium |
| t3-b001-00017 | ok | none. *pérkus* NOM vs *pr̥kʷéw-* in the obliques is the boukólos rule (*kʷ > k* next to *u*), not a lost labiovelar | none (Dyēus "splitting" the oak: a good riddle) | none (ACC *kʷím*, root aorist *bʰéydt*) | medium |
| t3-b001-00217 | ok | none (*h₁édt* vs Narten *h₁ḗdt*: school difference) | none | none (neuter *tód* for *yókʷr̥*: good) | high |
| t3-b001-00116 | ok | none | none | Note: the overt *só* in the answer is emphatic but natural | high |
| t3-b001-00098 | ok | none | Note: *lelóykʷe* is a transitive perfect ("has left"). The object (the nest) is recoverable from the previous clause, so "has left [it] = is gone" works | none | medium |
| t3-b001-00057 | ok | none (IMP.3SG *péh₂stu*) | none | none | high |
| t3-b001-00152 | ok | none (thematic aorist *likʷét*, root aorist *gʷéh₂t*) | none | none | high |
| t3-b001-00156 | ok | none (s-stem ABL *h₁élḱesos*) | none (*h₁élḱos* = Homeric ἕλκος "wound"; *kréwh₂s* "gore", cf. Lat. *cruor*) | none | high |
| t3-b001-00238 | minor | ACC *h₁eh₂nom* has no accent [P10] | Note: imperfect *dʰédʰeh₁t* for "placed"; the aorist *dʰéh₁t* was in the slice [S3] | none | high |
| t3-b001-00246 | ok | none (MID imperfect *sékʷeto*, Ved. *ásacata*, Gk ἕπετο: Q1 fix holds) | none | none (ACC object: Lat. *sequor* + ACC) | high |
| t3-b001-00167 | ok | none (*tḱyént* for *tḱiyént* (Ved. *kṣiyánti*) is a notation choice) | Note: imperfect *h₁r̥sḱónt* for "arrived"; *h₁ludʰét* was available [S3] | none (ACC of goal) | medium |
| t3-b001-00185 | minor | *sterḱos* has no accent [P10]. It is routed as a m. thematic, but Lat. *stercus, -oris* n. points to a neuter s-stem *stérḱos*, *-es-* (invisible in the NOM) [S5]. LOC *h₂éḱri* [S4] | none (stative imperfect *légʰyet* "lay": ideal) | none | medium |
| t3-b001-00054 | ok | none (*tr̥syḗti* SBJV; aorist IMP.3SG *péh₃tu*) | none | none | high |
| t3-b001-00027 | ok | none (perfect *dedwóye*, Gk δέδοικε; ABL *h₁résos*; *pérkum* is boukólos) | none (ABL with "fear", Vedic *bhī-* + ABL). Note: *dʰegʷʰrós* "the burning" rests on Gk τέφρα and Lat. *febris*, neither of which is a masculine o-stem. The slice had no "fire" noun [Q2, S5] | none | medium |
| t3-b001-00003 | minor | *só plówyos*: the daughters say neuter (Gk πλοῖον n., Gmc *\*flawją* n.; Lat. *pluvius* is the adjective). Expected *tód plówyom* [S5] | none (iterative *bʰoréyeti* "carries about": exact) | none | medium |
| t3-b001-00195 | ok | none (imperfect *térh₂ut*, Hitt. *tarḫuzzi*). Note: Celtic *\*katu-* and Gmc *\*haþu-* point to short *\*kat-u-* rather than *kéh₃tus* (low confidence) | none | none (neuter *séǵʰos* as a transitive subject: fine for Late PIE) | medium |
| t3-b001-00232 | ok | none (*tn̥tóm* is n. ACC = m. ACC; *tl̥néh₂t*) | none | none | high |
| t3-b001-00059 | ok | none (*h₃éronm̥*) | none | none (*mē* + injunctive: P8 fix holds) | high |
| t3-b001-00007 | ok | none (INS *ḱoph₂óh₁*, *stunédti*, *h₂nérm̥*) | none (*h₁éḱwos*: Q2 fix holds) | none | high |
| t3-b001-00025 | minor | ACC *dinom* has no accent [P10] | none (MID *ḱéytor*: Q1 fix holds) | none (*-kʷe … ne* placement good) | high |
| t3-b001-00179 | ok | none | Note: *dʰegʷʰrós* as above | none (VSO) | high |
| t3-b001-00100 | minor | ACC *ḱerh₂wom* has no accent; expected *ḱerh₂wóm* (Gk κεραός) [P10] | none (causative *woydéye* "show": Ved. *vedáyati*) | none (Wackernagel *moy*) | high |
| t3-b001-00031 | ok | none (*moréyēti*, *kʷoynéh₂m*) | none (*kʷoynéh₂* "blood-price", Gk ποινή: apt) | none | high |
| t3-b001-00139 | ok | none (LOC *tósmi*, imperfect 3PL *h₁sént*). Note: the spec has *wéyHs* m., but Lat. *vīs* and Gk ἴς are f.; invisible here [S6] | none | none (plural verb with conjoined subjects) | high |
| t3-b001-00121 | ok | none (OPT *h₁syéh₁t* + verbal adjective *gʷr̥Htós*, Ved. *gūrtá-*) | none | none | high |
| t3-b001-00066 | ok | none (*kapyé*, cf. Lat. *cape*). Note: *sth₂dʰí* has zero grade where Gk στῆθι has full grade. This matches *dh₃dʰí* (Ved. *dehí*), which was accepted in pilot 2; low confidence [Q5] | none | none | high |
| t3-b001-00186 | minor | ACC *h₂eysom* has no accent [P10]. The lexeme rests on Lat. *aeruscō* only [S5] | none (*némos kʷért* "made obeisance" = Ved. *námas kar-*: excellent) | none | high |
| t3-b001-00001 | ok | none (GEN *wóǵʰosyo*; m. *tóm* resumes m. *bʰórom*) | none (figura etymologica *bʰórom bʰéreti*) | none | high |
| t3-b001-00146 | minor | none | *bʰebʰóyh₂e* is a present-stative perfect ("he is in fear", Ved. *bibhā́ya*). In a past narrative after the imperfect *gʷʰn̥sḱét*, "he trembled" comes out as "and he is afraid"; the imperfect of *tremti*/*tréseti* was in the slice [S2]. Note: iterative *-sḱé-* for a single "struck" [S3] | none (*só* marks the switch of subject: good) | low-medium |
| t3-b001-00008 | ok | none | none (f. *séh₂* for the goose follows the English "she" and matches Gmc and Gk f.) | none | high |
| t3-b001-00069 | ok | none (athematic OPT *ph₂syéh₁t*) | none | none (enclitic *te* in second position) | high |
| t3-b001-00176 | ok | none (LOC *bʰudʰméni*) | none | none | high |
| t3-b001-00109 | ok | none | none | none | high |
| t3-b001-00111 | **wrong** | none | Active *Hrunépti* means "the wheel is breaking [something]", the same defect as 00237. The second clause (causative *stoh₂éye* "stop") is good [S1] | none | medium |
| t3-b001-00202 | ok | none (f. *pl̥h₁néh₂* agrees with f. *séh₂* < *kʷoynéh₂*) | none | none | high |
| t3-b001-00082 | ok | none (*gʷʰr̥nudʰí*, cf. Ved. *śṛṇudhí*; SBJV.1SG *wr̥ǵyṓh₂*) | Note: the reflexes of the *nu*-present are mostly intransitive (Arm. *ǰeṙnum* "become warm", Gmc *\*brinnaną* "burn"), so a transitive "heat the bronze" is not well supported (low confidence) | none | medium |
| t3-b001-00247 | minor | NOM *ḱerh₂wos* has no accent [P10] | Note: *ḱl̥néyt* "leaned". Gk κλίνω is transitive, with an intransitive middle, but Gmc *\*hlinōn* is intransitive; borderline S1 | none | high |
| t3-b001-00115 | ok | none (aorist IMP *bʰiddʰí*, i.e. /bʰidzdʰí/) | none | none | high |
| t3-b001-00136 | ok | none (proterokinetic LOC *ḱlunéy*; m. *h₂eḱróm*) | none (LOC of goal with a verb of thrusting: Vedic usage) | Note: the overt *só* subject is unemphatic [P9] | high |

## Systematic patterns

**Fixed since pilot 2, confirmed in this batch.**

| pattern | evidence (b001, 250 records) |
|---|---|
| Q1 (middle-only verbs) | All 5 MID tokens in the batch are correct (*ḱéytor*, *wéstor* ×2, *sékʷeto*, *sékʷeso*). No *-tor* lemma comes out active |
| Q2, "horse" | *h₁éḱwos* 6/6, *ǵʰéyos* 0 |
| P7 (*ḱeḱlówe*) | 0 uses; the blocklist holds |
| P9 (overt *wéy*) | Only one personal-pronoun subject in 250 records (00079, contrastive *túH … h₁eǵ*) |
| P1, P2, P3, P5, P8 | Neuter s-stems (*h₂éyos*, *némos*, *séǵʰos*); athematic *-dʰí* imperatives (*sth₂dʰí*, *gʷʰr̥nudʰí*, *bʰiddʰí*); LOC with an ending in consonant and u-stems (*bʰudʰméni*, *kh₃téwi*); *mē* + injunctive |

Also right throughout the sample:
- case roles: dative of possession, ABL source, ACC goal, LOC of goal, INS;
- *-kʷe* placement;
- *yo-/so-* correlatives;
- subjunctives, optatives and imperatives.

Planner and lexicon together found genuine formulas: *némos kʷért* (Ved. *námas kar-*), *bʰórom bʰéreti*, *wédʰ- … wédʰmn̥*.

**S1. Anticausative or reflexive meanings come out active (new; the only source of *wrong* records).**
- *Hrunépti* (00111, 00237) and *Hréwpt* (00162 "the wheel broke") are transitive stems used with a patient subject and no object. *wesnudʰí* "dress yourself!" (00130) has the same defect: the active of Gk ἕννυμι means "clothe (someone else)", and putting on clothes is middle (Ved. *váste*).
- **Count:** 4 records in the batch (1.6%), all 4 intransitive uses of these lemmas. The 3 transitive uses of *Hréwpt* (00039, 00114, 00160) are fine.
- **Source:** planner, misled by the lexicon gloss.
  - The slice offered `IND PRS MID` / `IND AOR MID` for all three lemmas, but every plan says `voice: ACT`.
  - The glosses "to be breaking" and "to dress oneself" read as intransitive in English.
- **Fixes:**
  1. Re-gloss the stems by their object: "to break (something)"; "to clothe (someone); MID: to dress oneself".
  2. Add a rule to the brief: "a transitive verb with the patient as subject (*X breaks*, *X opened*, *dress yourself*) takes `voice: MID`".
  3. In the plan checker, flag ACT with no OBJ on lexemes marked transitive. Seed list: *Hrunépti*, *Hréwpt*, *wesnéwti*, *bʰinédti*, *ḱl̥néyti*.
  4. Re-realize the 4 records.

**S2. The present-stative perfect is used for English past events (new).**
- 27 PRF tokens in the batch. Most are correct present states:
  - *dedwóye* "is afraid";
  - *lelóykʷe* "is gone";
  - *dedórḱth₂e* "have you seen";
  - *wóydh₂e* "I know".
- 9 records use a perfect for an English past: 00140, 00146, 00148, 00154, 00223, 00225, 00234, 00240, 00243.
  - Past *states* ("was afraid", "stood steady", "was stretched", "was productive") are readable as a state that holds within the narrative, and the Rigveda uses the perfect as a past. **Not counted.**
  - *Dynamic events* are a real tense mismatch: "he trembled" = *bʰebʰóyh₂e* "he is in fear" (00146, 00223). Counted *minor* in 00146.
- **Source:** planner. The slice had present-stem imperfects for the same idea (*tremti* "be trembling", used ×4 elsewhere; *tréseti*).
- **Fix:** add to the brief: "PRF only for an English present state or a present perfect (*is afraid*, *has seen*). For past events use AOR or PST; for past states prefer the imperfect of a stative present (*légʰyeti*, *tremti*) and use the perfect only when none exists." Do not build a pluperfect: it is not securely reconstructible for PIE (Fortson treats it as doubtful).

**S3. The imperfect carries most narrative past tenses (new; mostly defensible).** This answers the brief's question about tense choice.
- **Numbers:** 110 non-copular imperfects against 40 aorists.
- **Cause:** the slice offered 21 aorist lemmas against 107 present-stem lemmas. `docs/morphology.md` lists sigmatic aorist formation as not yet built.
- **Verdict on the choice:** the imperfect as the unmarked narrative past is good Vedic practice (the imperfect is the narrative tense of the Brāhmaṇas) and well paralleled in Homer. So *pékʷet … h₁édt* "he cooked … he ate", *tl̥néh₂t* "lifted" and *térh₂ut* "overcame" are acceptable. **Not counted.**
- **Where it costs something:**
  1. The present stem's lexical meaning differs from the English. *spéḱyet* "was watching" for "saw" (00214, counted with S4) is the clear case.
  2. Iterative *-sḱé-* presents are used for single blows: *gʷʰn̥sḱét* "struck" (00146; plain *gʷʰénti* was in the slice).
  3. In 22 of the 110 imperfects, an aorist of the same root was in the slice and was not used. Examples:
     - *ǵn̥néh₃t* ×4 vs *ǵnéh₃t*;
     - *bʰuHyét* ×3 vs *bʰúHt*;
     - *Hrunépt* vs *Hréwpt*;
     - *wéǵʰet* vs *wḗǵʰst*.

     (*dʰédʰeh₁t* "placed", 00238, with *dʰéh₁t* in the slice, is the same kind of case; the root-id count missed it.)
- **Fixes:**
  1. Add to the brief: "for a single completed past event use AOR when the slice has an aorist of the root; otherwise PST".
  2. Raise aorist coverage in the slices (build the sigmatic aorist; admit LIV aorist stems).

  This is a corpus-balance issue more than an error: a model trained on b001 sees the aorist as rare.

**S4. Acrostatic i-stems get a bare locative (new; engine).**
- `pie/morph.py` `_locative`, line 280: `# i-stem: bare only (h₂éwi)`. This gives LOC *h₂éḱri*, identical to the weak stem and with no case ending.
- The handbook i-stem locative is *-ēy/-ey* (Fortson; Ved. *agnā́/agnáu*, Gk πόληι). The golden *h₂ówis* paradigm has no LOC cell, so this rule was never verified.
- **Count:** 4 tokens in 4 records (00185, 00208, 00214, 00215). Proterokinetic i-stems are fine (*ḱlunéy*, *mréy*).
- **Second i-stem defect:** when the spec has no weak stem, GEN.SG is strong stem + *-s*, which equals the NOM. *gʰóstipotis* GEN in 00044 (outside the sample) makes "whoever splits the lord's tooth" read as "whoever, the lord, splits the tooth". Expected *gʰóstipoteys* (Ved. *-es*, Goth. *-ais*, Lith. *-iẽs*). Count: 1.
- **Fix:** make *-ey* (and *-ēy*) the first handbook LOC for i-stems, with bare *-i* as an alternative. Make *-eys* the GEN for i-stems that have no weak stem. Add both cells to the golden *h₂ówis* after a books check. Confidence: medium.

**S5. Lexemes derived from Wiktionary root-page trees get a guessed class, gender and accent (new; lexicon/spec).**
- `kind: derivative`, `pos: null` lexemes account for **80 tokens in 70 of 250 records (28%)**.
- Their specs come from shape rules: `shape:thematic` defaults to masculine, and some headwords have no accent.
- Several rest on a single branch: *h₂eysos* and *sterḱos* (Latin only), *h₂éydmn̥*, *widéh₁yeti*, and *wédʰmn̥* (no reflexes at all).
- **Visible errors:**
  - *só plówyos* (00003), where the daughters require neuter *plówyom* (6 uses, but only this one is NOM);
  - *sterḱos* routed as a m. thematic instead of a neuter s-stem (latent in its only use).
- Six of the eight unaccented headwords behind P10 are derivatives: *ḱerh₂wos*, *dinos*, *h₂eysos*, *sterḱos*, *medos*, *ǵʰleystos*.
- **Fixes:**
  1. Take gender from the reflexes when the daughters agree (all neuter → *-om*, n.).
  2. Route *-os* derivatives whose Latin or Greek reflex is a neuter s-stem (*-us, -oris*; *-ος, -ους*) to the s-stem class.
  3. Keep a derivative out of the slices unless it has an accent and reflexes in at least two branches.

**P10 (recurs, now larger). Unaccented headwords.**
- **Count:** 37 tokens in 34/250 records (13.6%), from 8 lexemes: *ḱerh₂wos* ×6, *dinos* ×6, *werdʰom* ×6, *h₁eh₂nos* ×6, *ǵʰleystos* ×4, *medos* ×4, *h₂eysos* ×4, *sterḱos* ×1. In the sample, 6 records (counted *minor*).
- The pilot-2 triage kept these unmarked by design. At 14% of records, though, the training corpus will teach accentless forms.
- **Fix:** accent the 8 headwords by hand (e.g. *ḱerh₂wós* after Gk κεραός), or apply the S5 gate.

**Q2 (recurs in a new form). The slice offers marginal synonyms or lacks the core word.**
- **"Sharp":** *tr̥nós* (3 uses: 00206, 00219, 00236) has no adjectival reflex in any branch, and *h₂eḱrós* (5 uses) was also in the slice. Counted *minor* in 00206.
- **"Sheep/ram":** *moysós* is used ×6 because *h₂ówis* was not offered.
- **"Fire":** the slice has no fire noun, so *dʰegʷʰrós* "the burning" is used ×4.
- *gʰóstipotis* "lord", *pótis* "ruler" and *h₁esh₂ós* "master" are each used 6 times. They map one-to-one onto distinct English words, so this is not drift.
- **Fix:** offer one preferred lexeme per concept in each slice, always include the core vocabulary items (*h₂ówis*, *h₁n̥gʷnís*/*péh₂wr̥*), and demote lexemes whose gloss mixes a noun sense with an adjective sense.

**S6. Spec gender errors with no visible effect yet (new; spec).**
- 4 devi feminines are tagged m.: *pótnih₂*, *déywih₂*, *h₃rḗǵnih₂*, *néptih₂*.
- *snusós* is m. (Gk νυός, Ved. *snuṣā́*, Lat. *nurus* are all f.).
- *wéyHs* is m. (Lat. *vīs*, Gk ἴς are f.).
- **Count:** 0 visible errors in b001, because the plan supplies anaphor gender. The first agreeing adjective will expose them.
- **Fix:** force f. for `devi: true` and correct the two headwords.

**Low-confidence observations (not counted):**
- *sth₂dʰí* has zero grade where Gk has στῆθι (see Q5).
- *kéh₃tus*: Celtic and Germanic point to short *\*kat-*.
- *gʷʰr̥néwti* is transitive here, but its reflexes are intransitive.
- *ḱl̥néyt* "leaned" is borderline S1.
- Overt unemphatic *só* subjects in narrative (00136, 00137).

## Counts

| verdict | n | records |
|---|---|---|
| ok | 38 | |
| minor | 10 | 00206, 00214, 00238, 00185, 00003, 00025, 00100, 00186, 00146, 00247 |
| wrong | 2 | 00237, 00111 |

| genre | n | ok | minor | wrong |
|---|---|---|---|---|
| epic | 24 | 16 | 7 | 1 (00237) |
| dialogue | 12 | 10 | 1 | 1 (00111) |
| riddle | 8 | 6 | 2 | 0 |
| law | 6 | 6 | 0 | 0 |
| **all** | **50** | **38** | **10** | **2** |

| issue kind (records with at least one counted issue) | n | records |
|---|---|---|
| form | 8 | 00214, 00238, 00185, 00003, 00025, 00100, 00186, 00247 |
| meaning | 5 | 00206, 00214, 00237, 00111, 00146 |
| syntax | 0 | |

Records touched, by pattern (counted issues only):

| pattern | sample | full batch (250) | source |
|---|---|---|---|
| S1 anticausative in ACT | 2 (00237, 00111) | 4 records | planner + lexicon gloss |
| S2 perfect for a past event | 1 (00146) | 9 records use PRF for an English past; 2 are dynamic events | planner |
| S3 imperfect with a different lexical meaning | 1 (00214) | 110 imperfects vs 40 aorists; 22 with a same-root aorist available | planner + slice composition |
| S4 i-stem LOC/GEN | 2 (00214, 00185) | 5 tokens (4 LOC, 1 GEN) | engine |
| S5 tree-derived lexemes | 2 (00003, 00185) | 80 tokens in 70 records use one; 2 visible class/gender errors | lexicon/spec |
| P10 unaccented | 6 | 34 records | lexicon |
| Q2 lexeme choice | 1 (00206) | 3 (*tr̥nós*) | slice + planner |

## Verdict on scaling

- **Wrong rate:** **2/50 = 4%** (Wilson 95% interval about 1–13.5%). The pilot review files record 10% for pilot 1 and 2% for pilot 2, so b001 is at or below the pilot range. Against a threshold of "under 10% wrong, and every wrong traced to a fixable cause", **b001 passes: scale.**
- **Causes of the wrong records:**
  - Both come from a single cause, S1, which touches only 4 records in the full batch (1.6%).
  - The fix is a gloss change plus a checker rule, and MID is already wired end to end (Q1).
  - No wrong record came from the engine, and none from case/role assignment.
- **The *minor* mass (20%) does not block scaling, but it is a corpus-quality cost:**
  - **Unaccented forms:** 7 of the 10 minors involve unaccented or tree-derived lexemes (P10, S5), so they come from about a dozen lexicon entries. The S5 gate and hand-accenting the 8 headwords would remove most of them.
  - **Tense/aspect skew:** S2/S3 is the subtler issue. In b001 the imperfect is the default narrative tense and the aorist appears only where the slice happens to have one, so a model trained on it will learn that skew.
- **Recommended before b003:**
  1. the S1 gloss and checker fix;
  2. the S2/S3 tense rules in the brief, with more aorists in the slices;
  3. the S5/P10 gate on derivative lexemes;
  4. the S4 i-stem locative (one engine line).

  S6 can wait for the first agreement error.
