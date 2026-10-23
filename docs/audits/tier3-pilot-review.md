# Tier 3 pilot: review of 50 sampled sentences

**Status:** provisional, knowledge-based review (no browsing; judgements are from handbook knowledge: Fortson, Ringe, Beekes, Mallory & Adams, LIV)
**Date:** 2026-10-23
**Sample:** `docs/audits/tier3-pilot-sample-50.jsonl` (50 records)

How to read the table:
- **Verdicts.** *ok* means no error a mainstream handbook would reject (a note may still be given). *minor* means a defect that leaves the sentence readable: a non-standard variant, an accent, or a weak lexeme choice. *wrong* means a form a handbook would reject, or a misreading of the meaning.
- **Confidence** is my confidence in the verdict, not in the sentence.
- **Codes.** Issue codes in [brackets] point to the patterns in the "Systematic patterns" section.
- **Engine evidence.** In a few places I checked `data/morph/inflection_specs.jsonl`, `data/lexicon/paradigms.jsonl` and `pie/morph.py` to find where a recurring error comes from. The verdicts themselves are argued from the grammar.

## Per-record table

| id | verdict | form issues | meaning issues | syntax issues | confidence |
|---|---|---|---|---|---|
| t3-pilot-00031 | minor | *déh₂nu* as LOC.SG is the bare stem, i.e. the nom./acc. form. A u-stem locative needs *-ew(i)*/*-ēw* (e.g. *dh₂néw(i)*, or the paradigm's own alternative *déh₂n̥wi*) [P3] | none (*udrós* "aquatic/water-snake" + *h₂éngʷʰis* is redundant but fine) | none | high |
| t3-pilot-00082 | wrong | *dedwóy* (IMP.2SG of the perfect) is just the 3sg stem with *-e* removed. The only well-supported perfect imperative type is zero grade + *-dʰí* (cf. *widdʰí*: Ved. *viddhí*, Gk *ἴσθι*), so expect *dedwidʰí*, which the paradigm lists second [P2] | none | Prohibitive *mē* is normally construed with the injunctive (Vedic *mā́* + inj.); *mē* + imperative is Greek-only (μή + present imperative). Perfect imperatives are marginal anyway [P8] | medium |
| t3-pilot-00129 | minor | none | none | *tóm* (masc.) resumes *sóh₂wl̥*, a neuter; it should be *tód* [P6] | high |
| t3-pilot-00132 | ok | none (endingless LOC *ḱérd* is fine) | none | none | high |
| t3-pilot-00027 | ok | *bʰórm̥* (short o) follows the Schindler/Szemerényi acrostatic pattern (*pṓds*, acc. *pódm̥*). Greek φῶρα and Latin *fūrem* generalise the long vowel, so this is a school difference | none | none | medium |
| t3-pilot-00058 | ok | GEN *h₃réǵs* is possible only as a Narten-type acrostatic (ē/e); many would write *h₃r̥ǵés* or *h₃rēǵés* | none | none | medium |
| t3-pilot-00143 | wrong | *téwh₂om*: *téwh₂os* is a neuter s-stem (the lexicon itself lists gen. *téwh₂esos*), so ACC.SG = NOM = *téwh₂os*. The engine declined it as a thematic masculine [P1] | none | none (clitic *toy* after the vocative is acceptable) | high |
| t3-pilot-00108 | ok | none (*gʷʰn̥sḱḗti*, a thematic long-vowel subjunctive, is correct) | none ("shall not" as *ne* + SBJV is fine) | none (temporal LOC *kʷsép* is fine; a genitive of time would also do) | high |
| t3-pilot-00141 | ok | none (*stesth₂ḗr*, the 3pl perfect, is good) | none (the stative perfect is exactly right for "are standing") | none | high |
| t3-pilot-00126 | ok | none | none | none | high |
| t3-pilot-00113 | ok | none (*dʰédʰeh₁eti* is a correct short-vowel subjunctive) | Note: a present-stem subjunctive for a single future act; an aorist subjunctive would be more natural | none (LOC with "place" is idiomatic) | high |
| t3-pilot-00062 | ok | none | none | none | high |
| t3-pilot-00001 | ok | none | none | none | high |
| t3-pilot-00021 | minor | *déh₂nu* LOC.SG is the bare stem again [P3] | none | none (*-kʷe* placement is good) | high |
| t3-pilot-00029 | ok | none (*pḱtnéh₁* is a good INS) | Note: *ksnew-* "scrape, sharpen" for combing wool is a stretch, but acceptable | none | medium |
| t3-pilot-00074 | ok | none | Note: *ḱóymos* is "home/village" more than "household" | none | medium |
| t3-pilot-00026 | wrong | *widih₁ént*: *widé-* is a thematic aorist, so the optative must be thematic, *widoyh₁n̥t* / *-oyh₁ent* (Gk ἴδοιεν). The form given is the athematic *-ih₁-* type [P4] | none | *ne* + optative in a negative wish is defensible (Vedic *ná* + opt.), but *mē* is more usual for wishes (Gk μή); not counted [P8] | high |
| t3-pilot-00116 | ok | none | none | Note: no correlative *só* in the main clause; the typical diptych is *yós … só …*, but the correlative is omissible | medium |
| t3-pilot-00003 | minor | IMP.2SG *péh₂s* is a bare full-grade athematic stem. Handbook default: zero grade + *-dʰí* (*ph₂sdʰí*), though Hittite-style bare stems exist [P2]. VOC *poh₂imén* keeps the stem accent; expected *póh₂imen* [P5] | none | none (ABL *wĺ̥kʷōd* with "guard from" is idiomatic: Ved. *pāhí … aṃhasaḥ*) | medium |
| t3-pilot-00142 | ok | none | none | Note: overt *wéy* with a hortative is emphatic and redundant [P9] | high |
| t3-pilot-00081 | ok | none | none | none (ACC of goal *ḱóymom* is idiomatic, cf. Lat. *domum*) [P9 note: overt *wéy*] | high |
| t3-pilot-00054 | ok | none | Note: *ǵeǵónh₁e* means "is born" (Gk γέγονα) in one branch but "has begotten" (Ved. *jajā́na*) in the other. Acceptable [P7] | none | medium |
| t3-pilot-00102 | ok | Note: *dʰugtréy* has no *h₂*. This is Wiktionary's weak stem (*dʰugtr-*); most handbooks write *dʰugh₂tréy*. Treated as a school difference | none | none | medium |
| t3-pilot-00033 | ok | none (*h₂eh₂ógʰe*, the stative perfect, is good) | none | none | high |
| t3-pilot-00045 | ok | none (LOC *dréw* is fine) | none | none | high |
| t3-pilot-00119 | ok | none | none | none | high |
| t3-pilot-00046 | ok | none (*ḱwón* VOC is fine) | none | Note: verbs of hearing often take a genitive of the person (Gk ἀκούω + gen.); ACC is acceptable | medium |
| t3-pilot-00104 | wrong | *werdʰom* has no accent (passed through from the lexicon headword) [P10] | *ḱeḱlówe* is an active perfect, "has heard" (Ved. *śuśráva*), whose subject is the hearer. With *werdʰom* as subject the sentence says "the word … has heard", not "is heard". A passive needs a middle form (cf. Ved. *śr̥ṇve*, *śrūyate*) [P7] | none | medium |
| t3-pilot-00049 | ok | none | none | none (fem. *h₁óyneh₂* with *h₂ówis* is fine) | high |
| t3-pilot-00096 | ok | none | none | none | high |
| t3-pilot-00066 | wrong | GEN.SG *wiḱpótis* is identical to the NOM. This comes from Wiktionary's acrostatic i-stem template. Expected *wiḱpotéys* (or *-oys*); the paradigm offers *potéys* for simplex *pótis* [P3b] | The sentence reads as "the clan chief, the mother, was a king's daughter": the possessive relation is lost | none | medium |
| t3-pilot-00149 | minor | VOC *dʰugh₂tér*: expected an initial accent (Ved. *dúhitar*, Gk θύγατερ), or none at all in non-initial position [P5] | none | none (enclitic *nos* is ambiguous between ACC and DAT, so "to us" is fine) | medium |
| t3-pilot-00010 | ok | none | none | none | high |
| t3-pilot-00093 | ok | none | none | Note: overt *wéy* [P9] | high |
| t3-pilot-00044 | minor | Lexeme *pérkus* should be *pérkʷus* (Lat. *quercus* requires *kʷ*); the error is in the lexicon headword | none | none | medium |
| t3-pilot-00012 | ok | none | none | Note: bare ACC for "toward" an animal is ambiguous with a direct object; a preverb or adverb would be clearer | low |
| t3-pilot-00072 | minor | LOC *wésn̥* is the oblique stem without a locative suffix. Expected *wesén(i)*, the endingless *-én* locative of r/n-stems; the engine gets this right for *ph₂wén* in 00019 [P3] | none | none (ACC of goal *ḱóymom* and temporal LOC are both good) | medium |
| t3-pilot-00069 | ok | none | none | none | high |
| t3-pilot-00038 | ok | none | none | none | high |
| t3-pilot-00037 | minor | *waylos* has no accent [P10]. A rare lexeme (Celtic/Armenian only) when *wĺ̥kʷos* is available | none | none | medium |
| t3-pilot-00059 | minor | NOM.SG *h₃ókʷ* is a neuter bare stem, but the lexicon headword is *h₃ókʷs* (animate). One of the two is wrong; the dual *-ih₁* suggests neuter, so the headword is probably at fault | none | none | low |
| t3-pilot-00019 | ok | none (LOC *ph₂wén* is good) | Note: *wédos* "water" is a thinly supported lexeme; *wódr̥* / *h₂ékʷeh₂* are standard | none | medium |
| t3-pilot-00083 | ok | none (*dh₃ih₁ént*, an athematic aorist optative, is correct) | none | none | high |
| t3-pilot-00091 | minor | VOC *dʰugh₂tér* accent [P5] | none | none (*toy* in second position is good; *tód* agrees with neuter *dóh₃r̥*) | medium |
| t3-pilot-00092 | minor | none | none | *tóm* (masc.) for an unspecified inanimate "it"; neuter *tód* expected [P6] | low |
| t3-pilot-00135 | minor | IMP.2SG *déh₃* is a bare stem. Standard *dh₃dʰí* (Ved. *dehí*, Av. *dāidī*), which the paradigm lists second [P2]. VOC *n̥mr̥té* should carry an initial accent [P5] | none | none | medium |
| t3-pilot-00040 | ok | none (ACC.PL *h₃énHōs*, the neuter s-stem collective *-ōs* < *-os-h₂*, is defensible) | none | none | medium |
| t3-pilot-00004 | ok | none (*wókʷm̥* matches Gk ὄπα) | none | none | high |
| t3-pilot-00107 | minor | none | *der-* means "tear, flay, split", not "divide or share out". A distributive root such as *deh₂(y)-* (Gk δαίομαι) would fit "divide the barley" | none | medium |
| t3-pilot-00048 | minor | VOC *poh₂imén* accent [P5] | none | none (*twéh₂m̥s*, fem. acc. pl. agreeing with *h₂ówims*, is fine) | medium |

## Systematic patterns

These are errors that recur, or that a single example traces to a general rule in the engine or the lexicon. They are listed by importance.

**P1. Neuter s-stems are declined as thematic masculines.** 00143 *téwh₂om* should be *téwh₂os*. In `inflection_specs.jsonl` the lexeme is routed to `shape:thematic` with gender `m`, even though the lexicon gives its genitive stem as *téwh₂esos*. A quick count finds **43** `shape:thematic` nouns whose lexicon stems include an *-esos* genitive, for example *ǵʰéh₂os*, *h₃épos*, *h₂érkos*, *kʷélh₁os*, *légʰos* and *krépos*. All of them will produce *-om* accusatives, *-ōs* nominative plurals, *-oy* datives and so on, all wrong for neuters. By contrast, lexemes classified as `shape:s-stem-neuter` come out right: *h₃énHōs* (00040) and *wédos* (00019). **Fix:** route any noun whose lexicon stems show *-es-* in the oblique to the s-stem class.

**P2. Athematic IMP.2SG defaults to the bare full-grade stem.** `morph.py` sets `IMP.2SG = [strong, weak + dʰí]`, and the planner or realizer takes item [0]. The results are 00003 *péh₂s* (for *ph₂sdʰí*), 00135 *déh₃* (for *dh₃dʰí*), and 00082 *dedwóy*, a perfect imperative that matches no attested type. Bare-stem imperatives exist (Hittite *ēš*, *ep*), but the handbook default for athematic verbs is zero grade + *-dʰí*. **Fix:** put the *-dʰí* form first. For perfects, generate only *-dʰí* on the weak stem.

**P3. A paradigm cell's first variant is taken even when it is the odd one.** Table-driven lexemes inherit Wiktionary's variant order, and item [0] is used:
- (a) LOC.SG *déh₂nu* (00031, 00021) is identical to the nom./acc.; the paradigm's *déh₂n̥wi* comes second.
- (a) LOC.SG *wésn̥* (00072) is chosen over the *usén(i)* / *wesén* forms.
- (b) GEN.SG *wiḱpótis* (00066) is identical to the NOM; only the acrostatic template is present.

The common failure is a case form that coincides with the nominative/accusative or with the bare stem. That makes the role unreadable and teaches a model that LOC or GEN can be unmarked. **Fix:** when a cell's first variant equals the NOM/ACC form or the bare stem, prefer an alternative that carries an ending. Separately, audit acrostatic i-stem and u-stem locatives and genitives across the lexicon.

**P4. A thematic aorist is classified as an athematic root aorist.** The spec for *widét* is `shape:root-aorist`, strong *widé*, weak *wid*. The 3sg comes out right by accident (*widé-t*). The non-indicative moods, however, use athematic morphology: OPT *widih₁ént* (00026) instead of *widoyh₁n̥t*. SBJV and IMP will be off in the same way. In the current specs this is the only aorist with a strong stem in *-é* and a weak stem. The other thematic aorists (*h₁ludʰét*, *likʷét*, *wéwket*) have no weak stem and are presumably handled as thematic. **Fix:** treat a strong stem ending in an accented *-é* as thematic, whatever the weak stem is.

**P5. Vocatives keep the paradigm accent.** The vocatives are *dʰugh₂tér* (00149, 00091), *poh₂imén* (00003, 00048) and *n̥mr̥té* (00135). In PIE (Vedic + Greek: *dúhitar*, θύγατερ, πάτερ) a vocative is accented on its first syllable when clause-initial and is unaccented otherwise. The forms come straight from the paradigm tables, so this is a paradigm-source convention rather than a planner error. It is minor, but it is in every vocative that is not already initial-accented. Confidence: medium.

**P6. Anaphoric *so/tod* defaults to the masculine.** 00129 *tóm* refers back to neuter *sóh₂wl̥*, and 00092 *tóm* stands for an inanimate "it". When the plan has no antecedent link, the pronoun gets ACC.SG masculine. **Fix:** in the plan schema, carry the antecedent's gender to anaphors, and default unspecified inanimate "it/this" to the neuter *tód*.

**P7. Lexicon glosses that turn active perfects into passives.** *ḱeḱlówe* is glossed "to be heard, audible", and the planner uses it with the thing heard as subject (00104), which is wrong: Vedic *śuśráva* means "has heard". *ǵeǵónh₁e* "to be begotten, born" (00054) is safe only thanks to Greek γέγονα. These are lexicon-gloss problems that lead the planner into errors of voice. **Fix:** review the glosses of every `stat` lexeme for who the subject is (experiencer or patient).

**P8. Choice of negation.** The engine maps `particle:ne` to *mē* in prohibitions (00082, with the imperative) but keeps *ne* in an optative wish (00026). The mainstream pattern is *mē* + injunctive for prohibitions, and *mē* is common in wishes. Low confidence, and only 2 cases, but it is a rule: either generate injunctive prohibitives, or accept *mē* + present imperative as a Greek-style option.

**P9. Overt 1pl subject pronoun with hortatives (stylistic).** *wéy … déh₃omos / gʷéh₂omos* appears in 00142, 00081 and 00093, i.e. every 1pl hortative in the sample. PIE is pro-drop, so an overt *wéy* is emphatic. This is not counted as an error, but the planner should drop it by default.

**P10. Unaccented headwords pass through to the output:** *werdʰom* (00104) and *waylos* (00037). Accentless lexicon entries need either an accent or a flag before generation.

**One-off lexeme or sense slips (not systematic):**
- *der-* "flay" for "divide" (00107).
- *pérkus* for *pérkʷus* (00044).
- The NOM/headword mismatch for *h₃ókʷ(s)* (00059).
- Rare or thin lexemes such as *waylos* and *wédos*.
- Three different "gift" nouns are used (*déh₃nom*, *déh₃rom*, *dóh₃r̥*). This is not an error, but it is noise for a training corpus.

**What is consistently right** (worth keeping):
- Thematic and athematic present/imperfect forms, root aorists and perfects (*stesth₂ḗr*, *h₂eh₂ógʰe*).
- Thematic and short-vowel subjunctives.
- The athematic optative *dh₃ih₁ént*.
- Dative for recipients, ablative for "guard from", accusative of goal (*ḱóymom*), locative for place and time, and instrumental for means.
- Placement of *-kʷe* and of the Wackernagel enclitics (*toy*, *moy*, *nos*).
- Stative perfects used for states.

## Counts

| verdict | n |
|---|---|
| ok | 31 |
| minor | 14 |
| wrong | 5 |

| issue kind (records with at least one counted issue) | n |
|---|---|
| form | 16 (00031, 00082, 00143, 00021, 00026, 00003, 00104, 00066, 00149, 00044, 00072, 00037, 00059, 00091, 00135, 00048) |
| meaning | 3 (00104, 00066, 00107) |
| syntax | 3 (00082, 00129, 00092) |

How the counts were made:
- Only issues that drive a verdict are counted; rows marked "Note" are not. The overt *wéy* (P9), the dropped *h₂* in *dʰugtréy*, the missing correlative, and ACC with hearing are therefore excluded.
- 00026's *ne* + OPT is listed under syntax but not counted, because it is defensible.
- The 5 *wrong* records are 00082, 00143, 00026, 00104 and 00066. Four are engine or paradigm errors (P1, P2, P3b, P4) and one is a lexicon gloss (P7). None of them is a planner error in role or case assignment.

---

## Triage (main session, 2026-10-23)

| # | Pattern | Verdict | Action |
|---|---|---|---|
| 1 | Neuter s-stems declined as thematic | **Classifier bug, confirmed.** *téwh₂os* had stems *téwh₂os ~ téwh₂esos*, but the classifier used only the lemma | Fixed: s-stem evidence in `stems`/`variants` routes to the s-stem neuter rule (now 50 lexemes) |
| 2 | Athematic 2sg imperative = bare stem | Convention order (Wiktionary lists the bare stem first) | Fixed for handbook: zero grade + *-dʰí* first (*h₁sdʰí*); bare stem kept as alternative |
| 3 | First cell form is the endingless locative or the stem | Convention order | Fixed for handbook: *-i* locative first (*déh₂n̥wi*). The genitive *wiḱpótis* = nominative is **Wiktionary's own table**; logged as a disputed source reading |
| 4 | *widé-* treated as athematic root aorist | **Classifier bug, confirmed** | Fixed: new rule `thematic-aorist` (*widóyh₁n̥t*) |
| 5 | Vocative keeps paradigm accent | Missing handbook rule | Fixed: initial-accent vocative first (*dʰúgh₂ter*, cf. Ved. *pítar*); paradigm form kept as alternative |
| 6 | "it" → masculine *tóm* for a neuter | The plan schema had no gender for pronoun slots during the pilot | `gender` field added; next planner brief requires it |
| 7 | *ḱeḱlówe* glossed "be heard" | Wiktionary gloss | Logged for the books check |
| 8 | Prohibitive with *mē* | The injunctive fix was already in; the remaining cases used a **perfect**, which has no injunctive | Plan checker now rejects prohibitives on perfects (2 pilot plans; reject rate 1.3%) |
| 9 | Overt *wéy* in "let us" sentences | Planner style | Next brief: pronoun subjects only for emphasis |
| 10 | Unaccented headwords (*werdʰom*) | The source gives no accent | Kept: an unknown accent stays unmarked rather than being guessed |

After the fixes, 37 of 150 pilot sentences changed, and the cross-check stays at 98.8% (all fixes are handbook-side).
