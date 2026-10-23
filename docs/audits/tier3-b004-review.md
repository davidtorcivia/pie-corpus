# Tier 3 batch b004: review of 50 sampled sentences

**Status:** provisional review from handbook knowledge, done without browsing. The judgements rest on Fortson, Ringe, Beekes, Mallory & Adams and LIV, and nothing was checked against the books in this pass.
**Date:** 2026-10-23
**Sample:** `docs/audits/tier3-b004-sample-50.jsonl` (50 records: law 15, genealogy 13, epic 9, dialogue 8, proverb 5)

**Summary.**

| genre | ok | minor | wrong |
|---|---|---|---|
| law | 11 | 3 | 1 |
| genealogy | 11 | 2 | 0 |
| epic | 6 | 3 | 0 |
| dialogue | 8 | 0 | 0 |
| proverb | 4 | 1 | 0 |
| **all (50)** | **40** | **9** | **1** |

- **Wrong rate:** 2% (1/50). The one wrong record (00027) comes from a LIV gloss that merges the active and middle meanings of *h₁ai̯-* ("give; take") [U2]. No wrong record traces to the engine, and none to case or role assignment.
- **Minor:** the minors come from three new causes: law protases with no word for "if" [U1]; subjunctives in main clauses forced by aorist-only LIV verbs [U3]; *tósyo* used for a possessor who is the subject, where PIE uses a reflexive [U5]. The rest are thin derived lexemes (R1/R3) and synonyms pushed in by the diversity cap [U4].
- **What the four points of interest show:**
  - **Laws.** The 41 *h₁yós* ("whoever") laws are uniformly well formed: the protasis is always SBJV, and the apodosis is IMP (21), SBJV (12, 9 of them MID) or OPT (7). The weak spot is the 13 "if" laws, which have no subordinator [U1].
  - **Genealogy.** Case work is clean: GEN of kin terms, dative of possession, the predicate nominative with *bʰúHt*. Two possessives should be reflexive [U5]. The obliques of *péh₂tōr* "protector" are homophonous with those of *ph₂tḗr* "father" [U6].
  - **LIV root aorists.** They are morphologically sound throughout, and they reverse the b001 tense skew (S3): 109 aorists vs 34 imperfects, 75 of the aorists from LIV. Their costs: one voice-merged gloss [U2], and no present stem, which pushes gnomic presents into the subjunctive [U3].
  - **Derived pronoun cells (`_derived`).** None is used in b004. Every pronoun token comes from a book-printed cell (*só, tóm, tósyo, tósmey, tā́m, tósyeh₂ey, tóns, h₁yós, kʷís, kʷíd, kʷésyo*).
- **Verdict:** scale, after the U2 gloss fix and the U1/U3 brief rules.

How to read the table:
- **Verdicts.** The scale is the same as in the earlier reviews (`tier3-b001-review.md`, `tier3-b002-review.md`).
  - *ok*: nothing a mainstream handbook would reject. A "Note" may still be given, but notes are not counted.
  - *minor*: a defect that leaves the sentence readable. Examples: a non-standard variant, a weak or thinly attested lexeme, a tense/mood choice that shifts the nuance, or a missing function word whose sense is still recoverable from context.
  - *wrong*: the PIE does not say the English, or a form is mis-inflected in a way that changes the reading.
- **Confidence** is my confidence in the verdict, not in the sentence.
- **Codes** in [brackets] point to "Systematic patterns" below.
  - P-codes come from pilot 1, Q-codes from pilot 2, R-codes from b002 and S-codes from b001.
  - U-codes are new in this batch.
- **Engine evidence.** To trace errors and count recurrences I checked:
  - `data/lexicon/lexicon.jsonl` (including the LIV `source: liv2` entries and `aorist_weak`), `data/lexicon/derived_glosses.jsonl` and `data/morph/inflection_specs.jsonl`;
  - `data/morph/closed_class.json` (`_derived`, `_refs`);
  - `data/generation/plans/b004.jsonl`, `data/generation/slices/b004.json` and `docs/generation/planner-brief.md`;
  - `corpus/tier3/b004.jsonl` (250 records);
  - `pie/realize.py` (`Lexicon.gender`), `pie/morph.py` and `pie/phon.py` (`stang`, `contract_eh2m`).

  The verdicts themselves are argued from the grammar.
- **Not counted as errors**, following the earlier reviews and the 2026-10-23 engine verification:
  - *-dt-*, *-tt-*, *-dʰdʰ-* clusters (*h₁édtu*, *léytt*, *muddʰí*);
  - long-vowel thematic subjunctives and short-vowel root-aorist subjunctives (*pékʷēti*, *déh₃eti*, *méreti*);
  - ACC.PL *-ns*;
  - thematic optative *-oyh₁-*;
  - GEN.SG without *-ós*;
  - i-stem LOC *-ēy*;
  - augmentless past indicatives.
- **Also not counted:**
  - LIV's *gʰrebh₂-* (*b* + *h₂*, not *bʰ*). LIV prints it that way and so does Wiktionary.
  - The middle used for an English passive ("shall be given", *déh₃etor*), which is the PIE mediopassive (see the low-confidence notes).

## Per-record table

| id | verdict | form issues | meaning issues | syntax issues | confidence |
|---|---|---|---|---|---|
| t3-b004-00061 | ok | none (root aorists *mért*, *bʰúHt*, Ved. *ábhūt*) | none | none (*tósyo* = the father, not the clause subject: correct non-reflexive; predicate NOM *h₃rḗǵs*) | high |
| t3-b004-00078 | ok | none (PRF *wóyde* "knows"; GEN *ǵm̥rósyo*) | none | none | high |
| t3-b004-00027 | **wrong** | none (MID SBJV *déh₃etor*; DAT *dayh₂uréy*; IMP *h₁áytu*) | Active *h₁áytu* means "let her **give**". *h₁ai̯-* is "give" in the active (Hitt. *pai-* < \**pe-h₁ai-*, Toch. *ai-*) and "take" only in the middle (Gk αἴνυμαι). The lexicon gloss "to give; take" (LIV 'geben; nehmen') hides the split, and 00007 uses the same form for "give". The English is inverted [U2] | No word for "if": the protasis is a bare subjunctive and reads as "a sister shall be given …" [U1] | medium |
| t3-b004-00185 | ok | none (LIV root aorist *Hwérdʰt*; LIV's *R* (r or l) is normalized to *r*, cf. Ved. *vṛdh-*) | none. Note: *h₂wékst* "grow (up), become large" (6 uses) was also in the slice | none. Note: overt unemphatic *só* [P9] | medium |
| t3-b004-00102 | ok | none (*bʰéroh₂*) | none | none (Q/A repeat the verb: R4 rule held) | high |
| t3-b004-00123 | ok | none | none (iterative *bʰoréye-* "carry around", Gk φορέω, fits "are you carrying") | none | high |
| t3-b004-00040 | minor | none (*pékʷēti*; ACC *ǵʰh₂énsm̥*; *h₁édtu*) | none. Note: f. *tā́m* for the goose (Gk ἡ χήν, Gmc *\*gans* f.) is fine | No word for "if": parataxis of SBJV + IMP reads as two injunctions [U1] | medium |
| t3-b004-00024 | ok | none (OPT *h₂woldʰéyoyh₁t*, *gʷíh₃woyh₁t*; ACC *h₁léwdʰim*) | none (*h₂woldʰéye-*, Lith. *valdýti*, OE *wieldan*: the derived gloss holds) | none | medium |
| t3-b004-00018 | ok | none (ABL *sruméns*; IMP of the LIV root aorist *séh₂tu*, cf. Gk ἆσαι) | none | none (ACC of goal *h₂éǵrom*). Note: correlative *só* after the verb, where *sá* usually opens the apodosis | medium |
| t3-b004-00006 | ok | none (*Hrunépeti* SBJV; *gʷr̥h₃étu*) | none (*bʰoydʰéh₂m Hrunép-*, cf. Lat. *foedus rumpere*) | none | high |
| t3-b004-00103 | ok | none (thematic aorist *widés*, *widóm*) | none | none | high |
| t3-b004-00141 | ok | none | none (f. *tā́m* for the sheep, Lat. *ovis* f.) | none | high |
| t3-b004-00235 | ok | none (SBJV *tr̥syḗti* in a general relative) | none | none | high |
| t3-b004-00075 | ok | none (*sédt*, *stéh₂t*, Ved. *ásthāt*) | none | none | high |
| t3-b004-00205 | minor | none (LIV root aorist *bʰéyh₂t*, cf. Ved. *mā́ bhes*) | *bʰéh₂os* "word" is a derived *-os* gloss on *bʰeh₂-* "speak". Its listed reflexes are Skt. *bhāṣā* (an *s*-extension) and Lat. *fās* "divine law", and the same string means "light" in 6 other records. *wékʷos* (Ved. *vácas*, Gk ἔπος) is in the lexicon but not in the slice [R1, U6] | none (repeated *só-kʷe* for the same subject, P9: not counted) | medium |
| t3-b004-00196 | ok | none (*léytt-kʷe*, LIV *lei̯t-* 'go away') | none. Note: imperfect *tl̥néh₂t* "was lifting" for "lifted"; the slice had no aorist of *telh₂-* [S3, not counted] | none | medium |
| t3-b004-00016 | ok | none (*woséyēti*; MID SBJV *dédeh₃etor*) | none. Note: middle as passive [low-confidence notes] | none (DAT *tósmey* resumes *h₁yós*) | medium |
| t3-b004-00057 | ok | none (neuter comparative *méǵh₂yos* agrees with *dóh₃r̥* (ACC) and with *h₁nómn̥* (NOM); OPT *h₁syéh₁t*) | none | none | high |
| t3-b004-00134 | ok | none (LOC *ǵʰémi* from the spec *ǵʰém*, cf. Gk χαμαί; MID *ḱéytor*) [Q1 holds] | none | none | high |
| t3-b004-00138 | ok | none (ACC *dyḗm*) | none | none | high |
| t3-b004-00093 | ok | none (MID PST *sékʷeto*; ACC *péh₂torm̥*) | none | none | high |
| t3-b004-00071 | ok | none (PRF *stestóh₂e*). Note: the spec gives *snusós* m. [S6, masked] | none | none | high |
| t3-b004-00200 | minor | none | none. Note: intransitive active *dʰégʷʰet* "burned" (Lith. *dègti* is intransitive, Ved. *dáhati* transitive) [S1, low] | "Put fire **to** the heap" has the goal in the ACC: *péh₂wr̥ kéh₂wpom dʰéh₁t*. With *dʰeh₁-* "put; make", two accusatives read as "made the fire a heap". LOC *kéh₂wpey* is expected, as in 00025 *h₂éǵroy dʰéh₁eti* [U7] | medium |
| t3-b004-00045 | ok | none (GEN *twósyo bʰréh₂tr̥s*; prohibitive *mē* + aorist injunctive *gʰrébh₂s*) | none | none | high |
| t3-b004-00212 | ok | none | none | none | high |
| t3-b004-00028 | ok | none (*h₁ludʰḗti*; MID SBJV of the causative, *sodéyētor*) | none ("seat himself" or "be seated": both fit) | none | medium |
| t3-b004-00068 | ok | none (amphikinetic GEN *dh₃trés*; *swēḱurós*, Gmc *\*swēgraz*) | none | none | high |
| t3-b004-00055 | ok | none (*h₂isḱḗti*; MID SBJV *sékʷētor*) | none | none | high |
| t3-b004-00007 | ok | none (*ḱélēti*; neuter dual *déh₃roy*) | none (*h₁áytu* active = "give": correct here). Note: "gift" switches lexeme within the sentence, *dóh₃r̥* → *déh₃roy* [Q2/U4] | none | medium |
| t3-b004-00213 | ok | none | none | none (copula-initial) | high |
| t3-b004-00165 | ok | none (s-stem ACC *krépos*; neuter *tód* resumes it; LIV *lémbʰt*) | none | none | high |
| t3-b004-00207 | minor | none | LIV *kʷéḱt* is "caught sight of", so "he found rest" becomes "he saw rest". *widét* "see, **find**, notice" (Ved. *ávidat* "found") was in the slice and had only 4 uses. Note: *h₁r̥h₁mós* "rest" is a thin derivative [R3] [U4] | none | medium |
| t3-b004-00067 | ok | none (GEN *neptyéh₂s*; f. *widtéh₂* agrees with the ti-stem) | none (*-tó-* adjective + copula as a passive) | none | medium |
| t3-b004-00236 | ok | none | none | none | high |
| t3-b004-00070 | ok | none (GEN *pkʷtrés*) | Note: *mr̥wós* "dead" has one reflex (Celtic *\*marwos*). *mr̥tós* (Ved. *mṛtá-*) is in the lexicon but was not offered [R3] | none | medium |
| t3-b004-00050 | ok | none (OPT of the LIV root aorist *sn̥gʷyéh₁t*: zero grade + *-yéh₁-*, correct) | none | none | high |
| t3-b004-00043 | minor | none (ACC *gʷṓm*; IMP *h₁éptu*, cf. Hitt. *ēpdu*) | none (*tósyo* = the father's: correct non-reflexive). Note: sg. *gʷṓm* "the cow" for "cattle" | No word for "if" [U1] | medium |
| t3-b004-00080 | minor | none | "His (own) daughter-in-law", with the lord as possessor, is *tósyo*, i.e. "that man's". PIE marks a subject possessor with the reflexive *swós* (Ved. *svá-*, Lat. *suus*, Gk ἑός), which exists in the lexicon but was not offered [U5] | none | medium-low |
| t3-b004-00237 | minor | none (SBJV *ḱémh₂eti*) | The main clause *légʰeti* is SBJV ("he will/shall lie down") for a gnomic "lies down". LIV *légʰt* has no present, so SBJV was the only non-past mood offered [U3] | none | medium-low |
| t3-b004-00161 | ok | none | none. Note: *moréyet* "was killing" where *gʷʰénti* would give the dragon-slaying formula (*gʷʰen-* + snake); *gʷʰénti* was at its 6-use cap [U4]. *gʷeyós* "victory" = Ved. *jayá-* m. | none | medium |
| t3-b004-00188 | ok | none (s-stem *bʰéh₂os* "light", cf. Ved. *bhā́s*; LIV *h₁nédʰt*) | none. Note: homograph of *bʰéh₂os* "word" [U6] | none | medium |
| t3-b004-00096 | minor | none (VOC *méh₂ter*) | *géwHeti* "call" is a derived thematic present whose reflexes are ON *kjá* and Iranian *\*gáwbati* (with *b*, not *H*), and its root has one uncertain Skt. reflex. The standard "call" root is *ǵʰewH-* (Ved. *hávate*), which was not offered [R1, R3] | none | medium-low |
| t3-b004-00023 | minor | none | *bʰoréyetu* "let him carry around" for "let him bring". *bʰéreti* (Gk φέρω "bring") was at its 6-use cap [Q2, U4] | none | medium |
| t3-b004-00156 | ok | none (LIV *léwkt*; neuter *tód* for the sun) | none | none | high |
| t3-b004-00087 | ok | none (DAT f. *tósyeh₂ey*) | Note: *ǵenh₁ós* "born" survives only as a compound member (Lat. *-genus*). *ǵn̥h₁tós* (Lat. *nātus*, Ved. *jātá-*) is in the lexicon but not in the slice [R3] | none | medium |
| t3-b004-00172 | ok | none (*gʰrébh₂t*; ACC *h₃réǵm̥*) | none (emotion as the subject of "seize": cf. Hom. χόλος ἔλλαβε). Note: *ḱéh₂dos* is a neuter s-stem (Gk κῆδος, -εος) routed as m. thematic; NOM is unaffected [R2, latent] | none | medium |
| t3-b004-00100 | ok | none (GEN *suHnóws*, Goth. *sunaus*) | none | none | high |
| t3-b004-00130 | ok | none (*h₁ddʰí*; aorist IMP *muddʰí*) | none | none | high |
| t3-b004-00064 | ok | none (*h₁ludʰét*; causative *sodéyet*) | none | none | high |
| t3-b004-00046 | ok | none (GEN *h₂n̥rés*; dual *gʷówh₁*; *dédeh₃tu*). Note: ACC *dn̥ǵʰwéh₂m̥* vs *-eh₂m* elsewhere [low-confidence notes] | none (wergild formula) | none | high |

## Systematic patterns

**Earlier patterns: status in b004.**

| pattern | evidence (b004, 250 records) |
|---|---|
| S3 (imperfect as the default narrative tense) | **Reversed:** 109 AOR vs 34 non-copular PST (b001: 40 vs 110). 75 of the 109 aorists are LIV root aorists |
| P10 (unaccented headwords) | 0 unaccented content tokens |
| Q1 (middle-only verbs) | *ḱéytor*, *ḱéyto*, *sékʷetor*, *sékʷeto*: all MID |
| R4 (Q/A verb switch) | Every dialogue answer in the sample repeats its question's verb |
| S6 (spec gender) | Still wrong in the specs (*méh₂tēr*, *swésōr*, *dʰugh₂tḗr*, *snusós*, *néptih₂*, *méntis*, *ǵénh₁tis* are m.) but **masked**: `Lexicon.gender` in `pie/realize.py` reads lexicon gender first and forces f. on *-ih₂/-eh₂* forms, so agreement comes out right (00065 *ǵenh₁éh₂*, 00067 *widtéh₂*) |

Also right throughout:
- LIV root aorist morphology in all its moods: zero-grade optatives (*sn̥gʷyéh₁t, bʰih₂yéh₁t, sh₂yéh₁t, h₃slidʰyéh₁t, l̥gʰyéh₁t, h₂wisyéh₁t*), imperatives in *-dʰí* (*muddʰí, h₁idʰí, bʰudʰdʰí, duh₃dʰí, h₂wisdʰí*), 3pl *h₂uksént*, *h₁l̥h₂éntu*, and 3sg IMP *-tu* on the full grade;
- the *mē* + aorist injunctive prohibitive (*mē gʰrébh₂s, mē bʰéyh₂s, mē léyts*);
- the neuter comparative *méǵh₂yos* vs m. *méǵh₂yōs* (00057, 00177).

**U1. "If" has no exponent (new; closed class + brief).**
- **Count:** all 13 English "If …" laws (00011, 00020, 00027, 00031, 00032, 00035, 00038, 00040, 00043, 00044, 00049, 00056, 00060). That is 22% of the 60 law records. Sample: 00027, 00040, 00043, counted *minor*.
- **What the PIE says:** the protasis is a bare subjunctive followed by an IMP/OPT/SBJV apodosis. That reads as two injunctions ("a cook shall cook a goose; let him eat it"). Asyndetic conditionals do occur in archaic legal prose, so the sense is recoverable, but every daughter law code marks the condition (Ved. *yád/yádi*, Gk εἰ/αἰ, Lat. *sī*, Hitt. *takku*).
- **Source:** the slice's closed list has no subordinator, and `realize.py` has no clause-level conjunction other than *-kʷe*. The planner had nothing to put there.
- **Fixes:**
  1. Add a closed-class subordinator with neuter relative *h₁yód* "if, when" (Ved. *yád*), realized clause-initially and allowing SBJV.
  2. Until then, add to the brief: "render 'if X' as a *h₁yós* 'whoever' law where the subject is human".
  3. In the plan checker, flag English "if" with no subordinator.
  4. Re-realize the 13 records.

**U2. A LIV gloss merges the active and middle meanings (new; LIV entry; the only source of a *wrong* record).**
- *pie-lex-h1ayt* (*h₁áyt*), from LIV 1.*h₁ai̯-* 'geben; nehmen', is glossed "to give; take". In the daughters, active = "give" (Hitt. *pai-*, Toch. *ai-*) and middle = "take" (Gk αἴνυμαι). The Wiktionary root entry linked to it (*pie-root-h2ey-give*) states the split: "to give"; "to be given; to receive, take".
- **Count:** 4 records. 2 are right ("give", active: 00007, 00048). 2 are **wrong** ("take", active: 00027, and outside the sample 00125 "Take it! I take it." = *tód h₁idʰí … h₁ā́m*, which reads "Give it! I give it").
- This is S1 in a new form: the voice split is carried by the gloss, and the planner reads the English gloss.
- **Fixes:**
  1. Re-gloss as "to give (ACT); MID: to take, receive".
  2. Re-realize 00027 and 00125 with MID or with *sléh₂gʷt*/*h₁épt*.
  3. Have the checker reject *h₁áyt* ACT where the English verb is "take".
  4. Audit the other 238 LIV verb glosses that contain ";" for the same voice split. Most are inchoative/stative pairs ("become tired; toil", "dry up; become thirsty"), which are harmless.

**U3. Aorist-only LIV verbs push English gnomic presents into the subjunctive (new; lexicon coverage + brief).**
- LIV entries are admitted as root aorists only (`aspect: pf`, no PRS features in the slice). For an English plain present, the planner's only non-past option was SBJV, which in a main clause is prospective or volitive ("shall, will").
- **Count:** 7 of the 40 proverbs. 2 have no relative clause: 00230 "Death takes the body" = *sléh₂gʷeti* "death shall take"; 00231 *ne néḱeti*. 5 are apodoses of *h₁yós* clauses: 00237, 00243, 00245, 00247, 00248. Sample: 00237, counted *minor*.
- The law apodoses with SBJV are fine ("shall"), and so are the subjunctive protases.
- **Fixes:**
  1. Add to the brief: "for a gnomic present with an aorist-only verb, use AOR IND (gnomic aorist, as in Greek proverbs) or a present-stem verb; SBJV in a main clause only for English *shall/will/let*".
  2. In the checker, warn on a main-clause SBJV whose English has no modal.
  3. Longer term, import LIV's Präsens stems alongside the aorists (the LIV records already carry them in `liv[].stems`).

**U4. The diversity cap without a `theme_core` forces marginal synonyms for the batch's theme words (new; slice + gate).**
- The b004 slice has keywords *give, gift, law, …* but **no `theme_core`**, so every lexeme was capped at 6.
- **"Give" and "gift" saturated the cap:**
  - "give": *déh₃t* 6, *déh₃ut* 6, *dédeh₃ti* 6, *h₁opéyeti* 4, and the overflow onto *h₁áyt* 5 [U2];
  - "gift": *dóh₃r̥* 6, *déh₃nom* 6, *déh₃rom* 6;
  - "carry/bring": *bʰéreti* 6, then *bʰoréyeti* for "bring" (00015, 00023);
  - "seize": *gʰrébh₂t* 6, *lémbʰt* 6, *h₁épt* 4, *sléh₂gʷt* 4;
  - "kill": *gʷʰénti* 6, *moréyeti* 6.
- **Visible costs:**
  - lexeme switches inside one sentence for the same English noun: 00007 *dóh₃r̥ … déh₃roy*; 00014; 00111 "Give me a gift! I give you a gift" = *déh₃rom … déh₃nom*;
  - "carry around" for "bring" (00023, minor);
  - the missed *gʷʰen-* + snake formula (00161, note).
- *kʷéḱt* for "find" (00033, 00207, 00247) is a planner choice, not cap pressure: *widét* "see, find" had only 4 uses. It breaks brief rule 9, because LIV entries carry low `attested_in` (often 0), so the rule cannot tell the planner which lexeme is better. Counted *minor* in 00207.
- **Fixes:**
  1. Fill `theme_core` for every slice from its keywords (here *déh₃t, dóh₃r̥, h₃rḗǵs, bʰoydʰéh₂*).
  2. Or cap by root rather than by lexeme.
  3. Add to the brief: "the same English noun in one sentence takes the same lexeme".
  4. Give LIV entries an `attested_in` from the branches LIV cites, so that rule 9 works.

**U5. Possessive "his (own)" for the clause subject uses the demonstrative (new; slice closed list).**
- *tósyo* is the anaphoric "that one's". When the possessor is the subject, the daughters use the reflexive possessive *swós* (Ved. *svá-*, Lat. *suus*, Gk ἑός/ὅς). *pie-lex-swos* exists, but neither it nor `closed:personal/refl` was offered.
- **Count:** 2 records (00079 "The brother gave his sister", 00080). Sample: 00080, *minor*.
- The other 18 POSS-*tósyo* uses are correct: either the possessor is not the subject (00043, 00044, 00061), or the possessive modifies the subject itself ("his name was great").
- **Fix:**
  1. Offer `closed:personal/refl` or *swós* in every slice.
  2. Add to the brief: "a possessor that is the subject of its own clause → *swós* (MOD) agreeing with the head".

**U6. Homographs between lexemes (new; lexicon derivatives + engine stem rule).**
- **"Word" and "light":** *bʰéh₂os* means "word" (*pie-lex-bheh2os-2*, 00037, 00113, 00127, 00166, 00176, 00205) and "light" (*pie-lex-bheh2os*, 00175, 00188, 00206, 00209, 00215, 00222): **12 records**, 6 each.
  - "Light" is sound (Ved. *bhā́s*).
  - "Word" is an R1 derived gloss: *-os* action noun on *bʰeh₂-* "speak", supported only by Skt. *bhāṣā* (an *s*-extension) and Lat. *fās*.
  - A model trained on this sees one form meaning both things, and in 00215 "Victory is light" vs 00113 "He says a word" nothing disambiguates it.
  - **Fix:** block *pie-lex-bheh2os-2* and offer *wékʷos* "word" (Ved. *vácas*, Gk ἔπος), giving it a plain gloss.
- **"Protector" and "father":** *péh₂tōr* "protector" (`shape:tor-agent`, weak stem *ph₂tr̥*) has GEN *ph₂trés* and DAT *ph₂tréy*, identical to the obliques of *ph₂tḗr* "father".
  - **Count:** 3 records, none in the sample: 00063 "daughter of the protector", 00066, 00083 "gave a daughter to the protector". In a genealogy batch each reads as "of/to the father". I would grade them *wrong*.
  - The zero-grade root in the weak cases is the theoretical amphikinetic pattern. The daughters generalize the full grade (Ved. *pātár-*, Gk δώτορος, Lat. *datōris*).
  - **Fix:** give `shape:tor-agent` nouns a full-grade weak stem (*péh₂tr-és*), or keep *péh₂tōr* out of slices that contain *ph₂tḗr*.

**U7. The goal of "put" comes out as an accusative (new; planner; 1 record).**
- 00200 has role GOAL on *kéh₂wpos* with *dʰéh₁t*, giving the double ACC *péh₂wr̥ kéh₂wpom dʰéh₁t*. With *dʰeh₁-* "put; make" this invites the reading "made the fire a heap".
- 00025 uses LOC correctly (*h₂éǵroy dʰéh₁eti*).
- **Fix:** add to the brief: "GOAL (ACC of direction) only with verbs of motion; with *dʰeh₁-*, *logʰéye-*, *sodéye-* use LOC".

**R1/R3 (recur). Thin derived lexemes and missing core words in the slice.**
- **Derived-gloss stretches (R1):**
  - *bʰéh₂os* "word" ×6 [U6];
  - *géwHeti* "call" ×3 (00031, 00084, 00096): the reflexes need *\*gewb-*, and the root has one uncertain reflex;
  - *h₁r̥h₁mós* "rest" ×4 and *gʷeyós* "victory" ×5 are acceptable (Ved. *jayá-*), but each rests on one or two branches.
- **Thin lexemes offered while the standard word was not (R3):**
  - *mr̥wós* "dead" ×6 (Celtic only; *mr̥tós* not offered);
  - *ǵenh₁ós* "born" ×5 (compound-only; *ǵn̥h₁tós* not offered);
  - *géwHeti* with *ǵʰewH-* not offered;
  - *bʰéh₂os* "word" with *wékʷos* not offered.
- **Count:** these 6 lexemes touch **29 records** (11.6%). Counted *minor* in 00205 and 00096, where the meaning itself is strained. The others are notes.
- **Fix:** as in b002 (R3): restrict the random fill to plain-glossed lexemes, and always offer the core word of a concept (*mr̥tós*, *ǵn̥h₁tós*, *wékʷos*, a *ǵʰewH-* verb) when a thin synonym is included.

**R2 (recurs, latent). *-os* derivatives with neuter s-stem reflexes routed as thematic masculines.**
- *ḱéh₂dos* "hatred" (Gk κῆδος, -εος n.) and *h₂éwgos* "increase" (Ved. *ójas* n.) are both `shape:thematic`, m.
- **Count:** 8 records, mostly NOM, so they are invisible. One visible error, outside the sample: 00195 *ḱéh₂dos dʰubʰnós* (m.) for neuter *dʰubʰnóm*.
- **Fix:** the b002 R2 routing rule, extended to the Greek *-ος/-εος* neuter check.

**S1 (recurs, low). Intransitive active of *dʰégʷʰeti*.**
- 00144 "the fire burns", 00197, 00200. Lith. *dègti* is intransitive, Ved. *dáhati* transitive. Not counted.
- *h₁éwseti* now carries `valency: tr` and was always used transitively.
- **Fix:** tag *dʰégʷʰeti* "burn (tr.); MID or Lith.-style intr. use doubtful".

**Derived pronoun cells (`_derived`, new in `closed_class.json`).**
- 0 tokens in b004. The 83 derived cells are oblique relative and interrogative forms (*h₁yósyo*, *kʷósmead*, …). The batch used only *h₁yós* (NOM) and *kʷís/kʷíd/kʷésyo*.
- Nothing to judge yet. The pattern itself (*yo-* and *kʷo-* inflect like *so/tod*: Ringe) is mainstream. The *-sm-* datives in the derived cells will need a books check once they appear.

**Low-confidence observations (not counted):**
- **Middle for an English passive** ("shall be given/killed/seated/let go"; *déh₃etor*, *gʷʰénetor*, *noḱéyētor*, *sodéyētor*, *léh₁etor*, *h₁opéyētor*): 12 law records. This is the inherited mediopassive (Fortson) and is accepted here. Note, though, that the Vedic middle of *dā-* often means "receive", which makes 00027's protasis double-edged.
- **Stang's law applied to the 1sg verbal ending.** `pie/morph.py` `sg_or_pl` passes the 1sg *-m̥* through `stang`, giving *h₁ā́m* for *h₁áy-m̥* (00125; b002 *ḱlḗm*). Ved. *ā́yam* and *áśravam* show *-am* < *-m̥* after a glide. `contract_eh2m` (*stā́m*, *gʷā́m* = Ved. *ásthām*, *ágām*) is right. Fix: skip `stang` for verbal 1sg.
- **ACC.SG after a laryngeal:**
  - *dn̥ǵʰwéh₂m̥* (00046, 00223, 00224) and *néptih₂m̥* (00084) come from the athematic table path;
  - *bʰoydʰéh₂m* and *twéh₂m* come from the eh₂ and adjective paths. The two paths meet in one phrase in 00223 (*twéh₂m dn̥ǵʰwéh₂m̥*);
  - handbooks write *-eh₂m*, *-ih₂m* (Ved. *jihvā́m*);
  - same note as b001/b002.
- **LIV notation:**
  - *Hwérdʰt* normalizes LIV *R* (r or l) to *r*;
  - *gʰrebh₂-* keeps LIV's *b* + *h₂*.

  Both are faithful to the source.
- ***ḱl̥wih₁ént*** (00059, OPT 3pl of *ḱlew-*) is syllabified on *l* where *ḱluwih₁ént* is expected from the weak stem *ḱlu-*.
- **Overt unemphatic *só*** in epic narrative (00185, 00205) [P9].

## Counts

| verdict | n | records |
|---|---|---|
| ok | 40 | |
| minor | 9 | 00040, 00043, 00023, 00080, 00096, 00205, 00200, 00207, 00237 |
| wrong | 1 | 00027 |

| genre | n | ok | minor | wrong |
|---|---|---|---|---|
| law | 15 | 11 | 3 (00040, 00043, 00023) | 1 (00027) |
| genealogy | 13 | 11 | 2 (00080, 00096) | 0 |
| epic | 9 | 6 | 3 (00205, 00200, 00207) | 0 |
| dialogue | 8 | 8 | 0 | 0 |
| proverb | 5 | 4 | 1 (00237) | 0 |
| **all** | **50** | **40** | **9** | **1** |

| issue kind (records with at least one counted issue) | n | records |
|---|---|---|
| form | 0 | |
| meaning | 7 | 00027, 00205, 00207, 00080, 00237, 00096, 00023 |
| syntax | 4 | 00027, 00040, 00043, 00200 |

Records touched, by pattern (counted issues only, except where marked):

| pattern | sample | full batch (250) | source |
|---|---|---|---|
| U1 no "if" | 3 (00027, 00040, 00043) | 13 | closed class + realizer + brief |
| U2 give/take voice merged | 1 (00027) | 2 wrong (00027, 00125) | LIV gloss |
| U3 gnomic present as SBJV | 1 (00237) | 7 | LIV aorist-only coverage + brief |
| U4 cap-driven synonyms | 2 (00023, 00207) | ~10 visible (bring ×2, gift switch ×3, find ×3, …) | slice (no `theme_core`) + gate + rule 9 with LIV `attested_in` |
| U5 non-reflexive possessive | 1 (00080) | 2 | slice closed list |
| U6 homographs | 1 (00205) | 12 (*bʰéh₂os*) + 3 (*péh₂tōr* = *ph₂tḗr*, likely wrong) | derived gloss; `shape:tor-agent` weak stem |
| U7 ACC goal with "put" | 1 (00200) | 1 | planner |
| R1/R3 thin derivatives | 2 (00205, 00096) | 29 | derived gloss + slice builder |
| R2 s-stem as thematic | 0 (latent in 00172) | 1 visible (00195), 8 latent | engine classifier |
| S1 intr. *dʰégʷʰeti* (not counted) | 0 | 3 | lexicon valency tag |

## Verdict on scaling

- **Wrong rate:** **1/50 = 2%** (Wilson 95% interval about 0.4–10.5%). That is the lowest of the reviewed batches (pilot 1 10%, pilot 2 2%, b001 4%, b002 4%), and well under the 10% threshold. **b004 passes: scale.**
- **Batch-wide:** the known wrongs outside the sample are 00125 (U2) and probably the three *péh₂tōr* obliques (U6). That gives 5/250 (2%), still inside the band.
- **Causes of the wrong records:** the one sample wrong record and the batch-level wrongs each trace to a single entry: the *h₁áyt* gloss and the `tor-agent` weak stem. The morphology engine produced no wrong form, and the new LIV root aorists are well formed in every mood.
- **The *minor* mass (18%) has changed character.**
  - Accent and stem-class defects (P10, S5, R2) have almost disappeared.
  - What is left is mostly expressive gaps in the plan schema:
    - no subordinator for "if" (U1);
    - no reflexive possessive (U5);
    - aorist-only verbs with no present (U3).
  - These are cheap to close. U1 alone touches 22% of the law genre.
- **Recommended before b005:**
  1. **Re-gloss *h₁áyt* by voice** ("give" ACT, "take" MID), audit the ";" glosses of the LIV verbs, and re-realize 00027 and 00125 (U2).
  2. **Close the schema gaps:**
     - a *h₁yód* "if" subordinator (U1);
     - *swós*/`personal/refl` in every slice (U5);
     - a brief rule for gnomic aorist vs SBJV with aorist-only verbs (U3).
  3. **Fix the slice inputs:**
     - fill `theme_core` from the keywords, or cap by root (U4);
     - give LIV entries a branch count for rule 9;
     - block *bʰéh₂os* "word" in favour of *wékʷos* (U6/R1);
     - always offer the core synonym (*mr̥tós*, *ǵn̥h₁tós*) (R3);
     - give `tor-agent` nouns a full-grade weak stem so that "protector" does not collide with "father" (U6).
