# Tier 3 pilot 2: review of 50 sampled sentences

**Status:** provisional, knowledge-based review (no browsing; judgements are from handbook knowledge: Fortson, Ringe, Beekes, Mallory & Adams, LIV)
**Date:** 2026-10-23
**Sample:** `docs/audits/tier3-pilot2-sample-50.jsonl` (50 records)

How to read the table:
- **Verdicts.** The scale is the same as in the pilot-1 review (`tier3-pilot-review.md`).
  - *ok*: no error that a mainstream handbook would reject. A "Note" may still be given; notes are not counted.
  - *minor*: a defect that leaves the sentence readable, such as a non-standard variant, a missing accent, a headword misspelling, a weak or marginal lexeme choice, or a wrong voice on a verb whose active is still attested in some branch.
  - *wrong*: the PIE does not say the English, or a form is mis-inflected in a way that changes the reading.
- **Confidence** is my confidence in the verdict, not in the sentence.
- **Codes.** Codes in [brackets] point to the patterns in "Systematic patterns" below. Q-codes are new in pilot 2. P-codes are pilot-1 patterns that recur here.
- **Engine evidence.** Where an error recurs, I checked `data/lexicon/lexicon.jsonl`, `data/lexicon/paradigms.jsonl`, `data/morph/inflection_specs.jsonl`, `data/lexicon/soundlaw_warnings.jsonl`, `data/generation/plans/pilot2.jsonl` and `corpus/tier3/pilot2.jsonl` (150 records) to find its source and to count how often it occurs. The verdicts themselves are argued from the grammar.

## Per-record table

| id | verdict | form issues | meaning issues | syntax issues | confidence |
|---|---|---|---|---|---|
| t3-pilot2-00028 | minor | ACC.SG *yéwos* = NOM. The paradigm (Wiktionary table) declines *yéwos* as a neuter s-stem. The daughters point to a masculine thematic noun (Ved. *yáva-* m., Lith. *javaĩ* m.pl.), which gives ACC *yéwom*. Only Hitt. *euwan-* is neuter, and it is not an s-stem [Q4]. Note: DAT.PL *-oybʰos* (vs *-obʰos*) is a school difference | *ǵʰéyos* "horse" is marginal (Indo-Iranian *haya-* + Arm. *ji* only); standard *h₁éḱwos* is in the lexicon and was offered [Q2] | none (DAT recipient, IMP *dh₃dʰí*: good) | medium (form low-medium) |
| t3-pilot2-00119 | ok | none (*sh₂wéney* is a good DAT of the heteroclitic; *déh₃omos* is a good short-vowel aorist subjunctive). Note: *kéh₂nmn̥* is a lexicon derivative (Lat. *carmen*); Lat. *canō* with short *a* argues for a root *kan-* rather than *keh₂n-* | none | Note: overt *wéy* with a hortative [P9] | medium |
| t3-pilot2-00021 | minor | none (*h₂ówim*, *h₂éǵrom*: fine) | *ǵʰéyos* for "horse" [Q2] | none (*-kʷe* after the second conjunct is good. Three bare accusatives, one of them a goal, are readable but ambiguous; a preverb would help) | high |
| t3-pilot2-00004 | ok | none (*ḱléwt*, the root aorist, is good: Ved. *áśrot*) | none | none | high |
| t3-pilot2-00083 | ok | none (*twéh₂m*, *dʰugh₂térm̥*: good) | none | none (Wackernagel *moy* splits *twéh₂m … dʰugh₂térm̥*; this hyperbaton is well paralleled) | high |
| t3-pilot2-00104 | ok | none (LOC *kʷsépi*: fine) | none | none (fem. *lewkéh₂* agrees with fem. *lówksneh₂*: good) | high |
| t3-pilot2-00047 | ok | none (*wr̥h₁énm̥* matches Gk ἄρνα; *h₂lékseti* matches ἀλέξω) | none | none | high |
| t3-pilot2-00103 | ok | none | none | Note: a verb-initial copula in a plain predication is marked (presentational); not an error | high |
| t3-pilot2-00144 | ok | none (the accent of *tr̥syéti* follows the LIV convention for *-yé-* presents; Ved. *tṛ́ṣyati* has root accent, a school difference) | none (plural *gʷówes* for "cattle" is good) | none | high |
| t3-pilot2-00090 | ok | Note: GEN *h₃réǵs* is acrostatic (see 00061) | none | none | medium |
| t3-pilot2-00046 | ok | none (*séh₂gyeti* matches Lat. *sāgiō*, Goth. *sōkjan*) | none | none | high |
| t3-pilot2-00071 | ok | none (*swésores*, *dʰugh₂téres*: good) | none | none | medium |
| t3-pilot2-00074 | ok | Note: AOR *bʰúHt* is Wiktionary's form. LIV posits a full-grade *bʰwéh₂-t*; Ved. *ábhūt* and Gk ἔφῡ are compatible with either. School difference | none | none (clause-level *suHnús-kʷe* is correct; predicate NOM with "become" is good) | medium |
| t3-pilot2-00020 | ok | none (SBJV *h₁éyomos*: good) | none | none (ACC of goal is idiomatic). Note: overt *wéy* [P9] | high |
| t3-pilot2-00088 | ok | none (*h₁syéh₁t*: good) | none | none | high |
| t3-pilot2-00078 | minor | IMP *h₁ddʰí* is zero grade + *-dʰí*. The witnesses point to *e*-vocalism: Ved. *addhí* (a zero grade *h₁d-* would give Ved. *d-*), Gk ἔσθι, Lat. *ēs*. Hitt. *adanzi* is ambiguous. Many handbooks take *h₁ed-* as a Narten root (*h₁ḗd-/h₁éd-*). Expected *h₁éddʰi*, or a bare *h₁éd* (the paradigm's first variant) [Q5]. Note: i-stem VOC *gʰósti* in bare *-i* (Gk type) vs *-ey* (Ved. *-e*, Lith. *-ie*) is a school difference | none (*gʰóstipotis* is glossed "lord, master" in the lexicon; OCS *gospodĭ* supports this) | Note: 3sg jussive by SBJV *píph₃ēti* is fine (Vedic). IMP.3SG *píph₃etu* is the more direct option | medium-low |
| t3-pilot2-00018 | minor | *sékʷeti* is active, but the lemma is the middle *sékʷetor* (Gk ἕπομαι, Lat. *sequitur*, OIr. *sechithir*). The active has some support (Ved. *sácati*, Lith. *sekù*), so this is minor, not wrong [Q1] | none | none (VSO: fine) | medium |
| t3-pilot2-00066 | ok | none (*péh₂sti* matches Hitt. *paḫš-*. Wiktionary's *déywih₂* vs Ved. *devī́* (final accent) is a school difference) | none (collective sg. *h₁léwdʰim*, cf. OCS *ljudĭ*: fine) | none | high |
| t3-pilot2-00133 | ok | none (LOC *liméni*, *ǵʰh₂éns*, *snéh₂ti*: good) | Note: *léymō* "lake" is thin (Greek λίμνη / λειμών / λιμήν). *lókus* (Lat. *lacus*, OIr. *loch*) is better attested and is in the lexicon (`pie-lex-lokus`) [Q2] | none | medium |
| t3-pilot2-00109 | wrong | none (*ḱeḱlówe*, *dyéwi*: well formed) | *ḱeḱlówe* is an active perfect, "has heard" (Ved. *śuśráva*); its subject is the hearer. With *kéh₂nmn̥* as subject the sentence says "the song has heard (something) in the sky". A passive "is heard" needs a middle (cf. Ved. *śr̥ṇvé*, *śrūyáte*), and the plan schema never produces one [P7, Q1] | none | high |
| t3-pilot2-00130 | minor | LOC *wekʷsperoy* has no accent; the headword is unaccented (expected *wékʷsperoy*, cf. Gk ἕσπερος) [P10] | none | none (temporal LOC; fronted *kʷíd* as subject: good) | high |
| t3-pilot2-00059 | ok | none (*h₁ludʰét* matches Gk ἤλυθε; *snusós* is a fem. o-stem) | none | none (ACC of goal *ḱóymom*: idiomatic) | high |
| t3-pilot2-00041 | ok | Note: *h₂éryeti* lacks the root *h₃* of *h₂erh₃-*. This is Wiktionary's headword and is justified by Pinault's law (*CHy > Cy*); cf. OCS *orjǫ*, Goth. *arjan* | none | none | medium |
| t3-pilot2-00094 | ok | none (*ḱóymosyo* is good; *h₁esh₂ós* rests on Hitt. *išḫa-* and Lat. *erus*) | none | none | high |
| t3-pilot2-00113 | ok | none (causative *lowkéyeti*; neuter *Héh₂mr̥* ACC = NOM) | none | none | high |
| t3-pilot2-00044 | ok | none | none | none | high |
| t3-pilot2-00108 | ok | none (thematic OPT *h₂léksoyt*, Gk ἀλέξοι: good) | none | none | high |
| t3-pilot2-00045 | ok | none | none | none | high |
| t3-pilot2-00121 | ok | none | none | Note: neuter *sréwmn̥* as the subject of a transitive verb is fine for Late PIE. Anatolian would need an ergative | high |
| t3-pilot2-00029 | minor | *gʰr̥bnéh₂ti* should be *gʰr̥bʰnéh₂ti*: the root is *gʰrebʰ(h₂)-* (Ved. *gr̥bʰṇā́ti*, Av. *gərəβnāiti*). This is a headword error that `soundlaw_warnings.jsonl` already flags (aspirate, Skt.) [Q4] | none. Note: this is the second "snake" lexeme in the sample (*h₁ógʷʰis* here, *h₂éngʷʰis* in 00004 and 00048) [Q2] | none (VSO: fine) | high |
| t3-pilot2-00051 | ok | none (proterokinetic GEN *h₁ludʰéys*: good) | none | none | high |
| t3-pilot2-00129 | ok | none (*dóru* ACC = NOM) | none | none (fronted ACC *kʷíd*; VSO answer: fine) | high |
| t3-pilot2-00049 | ok | none (*gʷm̥yóyt*: good) | none | Note: *ne* + optative in a negative wish has Vedic support (*ná* + opt.); Gk μή is the alternative [P8] | medium |
| t3-pilot2-00148 | ok | none (s-stem LOC *wétesi*: good) | Note: *bʰuHyéti* is glossed "become". "Grow" of a plant is fine via Gk φύομαι | none | medium |
| t3-pilot2-00111 | minor | ACC *werdʰom* has no accent [P10] | none | none (*dyéw* VOC, then *ḱludʰí*, Ved. *śrudhí*, Gk κλῦθι: very good) | high |
| t3-pilot2-00102 | ok | Note: DAT *ǵʰméy* follows Wiktionary's weak stem *ǵʰm-* (others write *dʰǵʰméy*); a school difference | none (*léwkos* is a neuter s-stem, Ved. *rócas*: ACC = NOM is right) | none | medium |
| t3-pilot2-00060 | ok | none (*gʷénh₂m̥*: good) | none (*wedʰ-* "lead home (a bride)" is apt) | none | high |
| t3-pilot2-00048 | ok | none (*tr̥h₂uyéh₁t*, a zero-grade athematic optative of the *u*-present, cf. Hitt. *tarḫu-*: good) | none | none | medium |
| t3-pilot2-00095 | ok | none (root aorist *péh₃t*, Ved. *ápāt*) | none | none | high |
| t3-pilot2-00101 | ok | none (initial-accent VOC *h₁ń̥gʷni*; thematic IMP *lowkéye*). Note: bare *-i* vocative (see 00078) | none | none | high |
| t3-pilot2-00128 | ok | none (LOC *kl̥Héni*: fine) | none | none (neuter *tód* with *péh₂wr̥*: good; P6 is fixed) | high |
| t3-pilot2-00079 | ok | none (DAT *gʰostéyey*, cf. Lat. *hostī*; *ǵr̥h₂nóm*; *dh₃dʰí*) | Note: a second "grain" lexeme (*yéwos* in 00028) [Q2] | none | medium |
| t3-pilot2-00124 | ok | none (thematic INJ *ḱéles*) | none (*ḱel-* "hide", Lat. *cēlō*, OE *helan*) | none (*mē* + present injunctive, Vedic *mā́* type: good; P8 is fixed. VOC of a neuter = NOM) | high |
| t3-pilot2-00016 | ok | none (*moréyeti*, Ved. *māráyati*; *wl̥kʷíh₂s*, Ved. *vr̥kī́s*) | none | none | high |
| t3-pilot2-00099 | ok | none (*h₁ési*: good) | none | Note: a yes/no question with no marker. No PIE question particle is secure, so this is not an error | medium |
| t3-pilot2-00025 | ok | none | none | none | high |
| t3-pilot2-00100 | minor | NOM.SG *gʷénh₂s*: no daughter has *-s* (Ved. *gnā́*, Gk γυνή, OIr. *ben*, Arm. *kin*), and the lexicon headword is *gʷḗn*. The paradigm table puts *gʷḗn* in the VOC cell and *gʷénh₂s* in the NOM [Q3] | none | none (fem. *séh₂* resumes *gʷénh₂s*: good. Note: an overt anaphoric subject is emphatic) | medium |
| t3-pilot2-00008 | ok | Note: *h₁édti* vs Narten *h₁ḗdti* (Lat. *ēst*, Lith. *ėsti*) is a school difference | none | none | high |
| t3-pilot2-00042 | ok | none | none | none | high |
| t3-pilot2-00061 | minor | *sékʷonti* is active on the middle lemma *sékʷetor* [Q1]. Note: ACC *h₃réǵm̥* has a short root vowel while NOM has *ē* and GEN *e*. This is a hybrid: Narten would give ACC *h₃rḗǵm̥* (Lat. *rēgem*); the Schindler type would give GEN *h₃r̥ǵés*. Defensible, low confidence | none (NOM.PL *h₁léwdʰeyes*, cf. Gmc *liudīz*: fine) | none | medium |

## Systematic patterns

**Fixed since pilot 1, confirmed in this sample.** These are consistently right now:

| pattern | evidence in this sample |
|---|---|
| P1 (neuter s-stems) | *léwkos* ACC (00102, 00124), LOC *wétesi* (00148) |
| P2 (athematic imperatives) | *dh₃dʰí* (×3), *ḱludʰí* |
| P3 (endingless locatives) | LOC *liméni*, *kl̥Héni*, *kʷsépi*, *dyéwi*, all with an ending |
| P5 (vocative accent) | initial-accent VOC *h₁ń̥gʷni*, *gʰóstipoti* |
| P6 (anaphor gender) | neuter *tód* with *péh₂wr̥* (00128); fem. *séh₂* for "she" (00100) |
| P8 (prohibitives) | *mē* + injunctive (00124) |

Also right throughout:
- optatives: *h₁syéh₁t*, *h₂léksoyt*, *gʷm̥yóyt*, *tr̥h₂uyéh₁t*;
- short- and long-vowel subjunctives;
- root and thematic aorists;
- case roles: DAT recipient, LOC place/time, ACC goal, GEN possessor;
- *-kʷe* placement;
- fronted interrogatives.

No record in the sample has a planner error in case or role assignment.

**Q1. The plan schema never produces middle voice, so middle-only lemmas come out active and passives cannot be expressed.** This is the most important open defect, and it explains the one *wrong* record.
- All **188/188** verb slots in `data/generation/plans/pilot2.jsonl` have `"voice": "ACT"`, and `corpus/tier3/pilot2.jsonl` has **0** MID tokens.
- The engine's MID cells exist (`_TH_MID_PRS` etc. in `pie/morph.py`), but nothing ever asks for them.
- `inflection_specs.jsonl` has **41** verb lemmas whose headword ends in *-tor*. Every token of them in pilot 2 is active:
  - *sékʷetor* → *sékʷeti*/*sékʷonti*, ×5 in the corpus (00018, 00061 in this sample);
  - *ḱéytor* → *ḱéyti*, ×1 ("The stone lies in the river").
- *ḱéyti* is the stronger case: Ved. *śáye*, Gk κεῖται and Hitt. *kitta(ri)* are all middle, and an active is attested nowhere.
- The same gap pushes the planner into P7 (below): to say "is heard", the only option it has is the active perfect.

**Fixes:**
1. The validator should reject `voice: ACT` on a lemma whose headword ends in *-tor*/*-or* (media tantum), or the engine should force MID for it.
2. Allow `voice: MID` in the planner brief, with passive/anticausative use, e.g. "is heard" = *ḱluyétor* (Ved. *śrūyáte*) or *ḱl̥nutór* (Ved. *śr̥ṇvé*).
3. Re-run the 6 affected corpus records.

**P7 (recurs, still open). An active perfect read as a passive.**
- 00109 *ḱeḱlówe kéh₂nmn̥* "the song has heard" is **wrong**.
- Both uses of *ḱeḱlówe* in the 150-record corpus have the thing heard as subject. The other one is "The name of the queen is heard."
- The pilot-1 triage only logged the lexicon gloss ("to be heard, audible") for a books check. Until that gloss is corrected (to "has heard, is a hearer"), or the lexeme is barred from patient subjects, every use will be wrong.
- This should block the next run. The fix belongs in the lexicon gloss, plus Q1.

**Q2. Lexemes are chosen by exact gloss-string match, which favours marginal words and lets synonyms drift.**
- *ǵʰéyos* (gloss "horse"; Indo-Iranian + Armenian only) is used **10/10** times for "horse" in pilot 2.
- *h₁éḱwos* (gloss "stallion, horse"; attested in every branch) was offered in all three slices and never chosen.
- This is a planner/lexicon-gloss interaction, not an engine error. Gloss ranking should prefer the first or core sense of a well-attested lexeme, or the slice should carry a preferred-lexeme flag per English concept.
- The sample also shows synonym noise, which matters for a training corpus:

  | concept | lexemes used |
  |---|---|
  | snake | *h₂éngʷʰis* (00004, 00048) vs *h₁ógʷʰis* (00029) |
  | grain | *yéwos* (00028) vs *ǵr̥h₂nóm* (00079) |
  | light | adjective *lewkós* vs neuter *léwkos* (not a clash) |
  | lord | *gʰóstipotis*, used for "lord" throughout (00078, 00079, 00099), where *pótis* "master, ruler" also exists |

- Thin lexemes also appear: *léymō* "lake" (00133) and the derived *kéh₂nmn̥* "song" (00119).
- Counted as *minor* only for "horse" (00028, 00021).

**Q3. A paradigm's NOM.SG differs from the lexicon headword.**
- 00100 *gʷénh₂s* (headword *gʷḗn*) is the same defect class as *h₃ókʷ(s)* in pilot 1 (00059).
- A scan of `paradigms.jsonl` finds **20** lexemes whose NOM.SG cell does not contain the headword. Some differences are trivial (accent, variant order). Others are substantive:
  - *gʷḗn* → *gʷénh₂s*;
  - *h₃ókʷs* → *h₃ók*;
  - *h₁óngʷl̥* → *h₁óngʷōl*;
  - *h₂elut-* → *h₂ólut*;
  - *ḱm̥tógʷus* → *ḱm̥tógus*.
- Two of the 20 are used in pilot 2: *gʷḗn* and *suH-*.
- **Fix:** a pre-generation check that flags NOM.SG ≠ headword. For *gʷḗn*, the NOM and VOC cells look swapped, or the proterokinetic template has added *-s* to an h₂-final stem.

**Q4. Source-table and headword errors pass straight through.**
- *gʰr̥bnéh₂ti* for *gʰr̥bʰnéh₂ti* (00029) is already listed in `soundlaw_warnings.jsonl`, but nothing gates on that list.
- Of the 7 pilot-2 lexemes with warnings, the others are mostly false positives (*ǵʰh₂éns*/Lat. *ānser*, *wĺ̥kʷos*/*lupus*, *ḱel-*/*occulō*, *twós*/σός). The aspirate warning on *gʰr̥bnéh₂ti* is real.
- *yéwos* as a neuter s-stem (00028) is Wiktionary's own table against the daughter evidence (low-medium confidence).
- **Fix:** have a human triage the aspirate- and laryngeal-class warnings once, then gate on the confirmed ones.

**Q5. The P2 imperative fix over-applies to roots whose weak stem keeps full grade.**
- *h₁ddʰí* (00078) puts a zero grade where Ved. *addhí* requires *e*.
- The rule "weak stem + *-dʰí* first" is right for genuinely ablauting roots: *dh₃dʰí*, *ḱludʰí*, *h₁sdʰí*.
- It should not apply to Narten roots, whose weak stem keeps full grade.
- The criterion cannot be root shape: *h₁es-* has the same shape and *h₁sdʰí* (Ved. *edhí*) is correct.
- **Fix:** exempt roots flagged Narten, or roots whose spec weak stem is full grade, rather than reverting P2. Confidence: low-medium.

**P9 (recurs). Overt *wéy* in hortatives.**
- The plans carry an explicit `closed:personal/1` SUBJ slot in **3/3** 1pl hortatives in the corpus (00119 and 00020 in this sample) and in 1 indicative ("We give the fire a gift").
- If the pilot-2 brief already said "pronoun subjects only for emphasis", the planner is not complying, and the validator should drop or flag unemphatic 1/2-person SUBJ pronouns.
- Not counted as an error.

**P10 (by design, still visible). Unaccented headwords.** *werdʰom* (00111) and *wekʷsperoy* (00130). The triage decided to keep these unmarked. They are counted as *minor* here so the rate stays visible: 2/50.

**Low-confidence observations (not counted):**
- **i-stem vocatives in bare *-i*:** *gʰósti*, *gʰóstipoti*, *h₁ń̥gʷni*. The *-ey* vocative (Ved. *agne*) is at least as standard. This is consistent across the sample, so it is a paradigm-template choice.
- **The *h₃rēǵ-* paradigm mixes two ablaut types:** NOM *ē*, ACC *e*, GEN *e* (see 00061).
- **Thematic DAT.PL *-oybʰos*:** a school difference.

## Counts

| verdict | n | records |
|---|---|---|
| ok | 40 | |
| minor | 9 | 00028, 00021, 00078, 00018, 00130, 00029, 00111, 00100, 00061 |
| wrong | 1 | 00109 |

| issue kind (records with at least one counted issue) | n | records |
|---|---|---|
| form | 8 | 00028, 00078, 00018, 00130, 00029, 00111, 00100, 00061 |
| meaning | 3 | 00028, 00021, 00109 |
| syntax | 0 | |

Records touched, by pattern (counted issues only):

| pattern | records |
|---|---|
| Q1 voice | 3 (00018, 00061, 00109) |
| P7 | 1 (00109) |
| Q2 lexeme choice | 2 (00028, 00021) |
| Q3 NOM ≠ headword | 1 (00100) |
| Q4 source/headword | 2 (00028, 00029) |
| Q5 *-dʰí* over-applied | 1 (00078) |
| P10 accentless | 2 (00130, 00111) |

How the counts were made:
- Only issues that drive a verdict are counted. "Note" items are excluded:
  - overt *wéy* (P9);
  - bare-*-i* vocatives;
  - the *h₃rēǵ-* ablaut;
  - school differences (*-oybʰos*, *bʰúHt*, *h₁édti*, *ǵʰméy*, *déywih₂*);
  - thin but defensible lexemes (*léymō*, *kéh₂nmn̥*);
  - *ne* + optative.
- Compared with pilot 1 (31 ok / 14 minor / 5 wrong), the engine-side fixes have held: no P1–P6 recurrences.
- What remains is upstream of the morphology engine:
  - the plan schema's missing middle voice (Q1);
  - one lexicon gloss (P7);
  - gloss-match lexeme selection (Q2);
  - source-paradigm and headword defects that no check catches (Q3, Q4).

---

## Triage (main session, 2026-10-23)

| # | Pattern | Action |
|---|---|---|
| Q1 | Middle-only (deponent) verbs realized as active | **Fixed:** slices list only MID features for *-tor/-toy* lemmas, and the plan checker rejects ACT for them |
| P7 | *ḱeḱlówe* glossed passive ("be heard") | **Blocked** from generation (`data/generation/blocklist.jsonl`, with reason) until the books check |
| Q2 | Marginal synonym chosen by exact gloss match (*ǵʰéyos* over *h₁éḱwos*) | **Fixed in slices:** each lexeme carries `attested_in` (daughter languages with a reflex), keyword hits are sorted by it, and the next brief tells planners to prefer well-attested words |
| Q3 | Paradigm nominative ≠ headword (*gʷénh₂s* for *gʷḗn*) | **Fixed:** for table-derived nouns the headword leads NOM.SG |
| Q4 | Sound-law warnings not used as a gate | **Partly adopted.** Blocking all 277 warnings was tried and rejected: they are mostly textbook irregularities (Lat. *lupus*, Gk *sós* < *twós*, *quercus*) and would have banned "wolf". Only triaged lexemes are blocked (*gʰr̥bnéh₂ti*, missing its *bʰ*) |
| Q5 | *-dʰí* imperative over-applied to Narten roots (*h₁ddʰí*) | Logged; low-medium confidence; revisit with Fortson/LIV² |
| P9/P10 | Overt *wéy*; unaccented headwords | The pro-drop `num` on V already landed after these plans were written; unaccented headwords stay unmarked by design |

After the fixes, the old pilot plans re-realize with real rejects only: 3.3% (pilot 1) and 5.3% (pilot 2).
