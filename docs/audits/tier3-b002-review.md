# Tier 3 batch b002: review of 50 sampled sentences

**Status:** provisional, knowledge-based review (no browsing; judgements are from handbook knowledge: Fortson, Ringe, Beekes, Mallory & Adams, LIV)
**Date:** 2026-10-23
**Sample:** `docs/audits/tier3-b002-sample-50.jsonl` (50 records; 25 contain at least one lexeme with an approximate derived gloss)

How to read the table:
- **Verdicts.** The scale is the same as in the pilot reviews (`tier3-pilot-review.md`, `tier3-pilot2-review.md`).
  - *ok*: no error that a mainstream handbook would reject. A "Note" may still be given; notes are not counted.
  - *minor*: a defect that leaves the sentence readable, such as a non-standard variant, a missing accent, a headword misspelling, a weak or marginal lexeme choice, a mis-inflection that does not change the reading, or a meaning that is a stretch but recoverable.
  - *wrong*: the PIE does not say the English, or a form is mis-inflected in a way that changes the reading.
- **DG** marks records that use a lexeme with an approximate derived gloss (`gloss_approximate` in the slice; `data/lexicon/derived_glosses.jsonl`). The derived lexeme is named in the meaning column.
- **Confidence** is my confidence in the verdict, not in the sentence.
- **Codes.** Codes in [brackets] point to "Systematic patterns" below. P-codes are from pilot 1 and Q-codes from pilot 2; both recur here. R-codes are new in b002.
- **Engine evidence.** I traced recurring errors through `data/lexicon/lexicon.jsonl` (reflexes, source titles), `derived_glosses.jsonl`, `data/morph/inflection_specs.jsonl`, `pie/morph.py`, `data/generation/slices/b002.json`, `scripts/make_slice.py`, `data/generation/plans/b002.jsonl` and `corpus/tier3/b002.jsonl` (250 records), and counted them there. The verdicts themselves are argued from the grammar. Acc. pl. *-ns* and the absence of gen. sg. *-ós* follow the engine check of 2026-10-23 and are not treated as errors.

## Summary

| | ok | minor | wrong | wrong % |
|---|---|---|---|---|
| all 50 | 31 | 17 | 2 | 4% |
| derived-gloss records (25) | 11 | 13 | 1 | 4% |
| other records (25) | 20 | 4 | 1 | 4% |

- The wrong rate is **4%**, against 10% (pilot 1, 5/50) and 2% (pilot 2, 1/50; its minor rate was 18%). At n = 50, 2 wrong vs 1 wrong is noise. b001 is not compared.
- **Derived-gloss records have the same wrong rate as the rest, but three times the minor rate** (13/25 vs 4/25). 11 of the 13 DG minors are caused by the derived lexeme itself. 00060 would be minor on its non-derived unaccented headwords alone (*gurnos*, *wēdos*), and 00042 (an engine locative) has a cause unrelated to the derived gloss.
- **Meaning errors that come from a derived gloss (the main thing this review measures): 4 of 25 DG records.**
  - 1 wrong: 00227, *léwkyeti* "brighten" is Gk λεύσσω "look at" [R1].
  - 3 minor: 00051 *bʰlongós* "blaze", an oxytone adjective "shining" [R1]; 00016 and 00123 *pleḱnós* "braid", a thin verbal adjective [R1].
  - The other derived-gloss failures are about form or attestation, not meaning:
    - an s-stem declined as thematic: *mḗdos* [R2];
    - thin or unaccented lexemes chosen over well-attested synonyms: *gʷéyh₃ti*, *srowmos*, *h₁rudʰyos*, *h₂emseti* [R3, P10];
    - one full-grade back-formation: *dewkéh₂ti* [R7].
- **Derived glosses that were right in the sample:** *stéwtōr* "praiser" (Ved. *stotár-*), *h₂molǵéyeti* "milk" (Lat. *mulgeō*), *troméyeti* "make tremble" (Umbr. *tremitu*), *smélos* "falsehood" (Lith. *mẽlas*), *srowmos* "stream" (Gmc **straumaz*), *séngʷʰeti* "recite", *kunédʰti* "hide", *Hrésgeti* "knit", *winéh₁ti* "twist", *sh₁esós* "crop" (Ved. *sasá-*).
  - The productive, transparent suffixes held up: agent *-tōr*, causative *-éye-*, nasal and thematic presents of verbal roots.
  - The failures cluster in suffixes whose function is ambiguous: oxytone vs barytone *-os*, *-nós*, *-yeti*, *-yós*.
- **Outside the sample, the same R1 drift is visible in the batch** (not counted in the verdicts above):
  - *dʰowh₂os* "smoke" = Gmc **dawwaz* "dew";
  - *meh₂turós* "good" = Lat. *mātūrus* "ripe";
  - *wl̥gnós* "wet" = Gmc **wulkną* "cloud";
  - *musn̥Hyéti* "pick up" = Ved. *muṣāyáti* "steals".
  - With *léwkyeti* and *bʰlongós*, the meaning-drifted lexemes touch **17 batch records (6.8%)**. I expect most of them to grade wrong. A batch-wide wrong rate of about 6–9% is therefore more realistic than the sample's 4%.

## Per-record table

| id | DG | verdict | form issues | meaning issues | syntax issues | confidence |
|---|---|---|---|---|---|---|
| t3-b002-00164 | | ok | none (thematic imperfects *wédʰet*, *wédʰom*) | none | none (Wackernagel *me*, *te*; clause-level *-kʷe*) | high |
| t3-b002-00021 | DG | ok | none (*h₂molǵéyom*, cf. Lat. *mulgeō* < *molǵéye-*: good) | none. Note: *péyh₂deti* "swell (with milk)" rests on Tocharian only; *h₂molǵéyeti* is apt | none (fem. *tā́m* for the sheep) | medium |
| t3-b002-00094 | | ok | none (thematic IMP *kapyé*, 1sg *kapyóh₂*) | none (*kapyéti*, Lat. *capiō*, Goth. *hafjan*) | none | high |
| t3-b002-00024 | DG | minor | ACC *mḗdom* is a thematic masculine ending on an s-stem neuter: Gk μῆδος / μήδεα (n.), lexicon stems *mḗdos/médos*. Expected ACC = NOM *mḗdos* [R2] | *mḗdos* "measure" is supported by Gmc **mētō* (OHG *māza*); Gk μήδεα means "counsels". Acceptable | none (Wackernagel DAT *moy*; GEN before head) | medium |
| t3-b002-00090 | DG | ok | Note: *kundʰdʰí* is morphophonemic (phonetically *-dzdʰ-*; cf. Ved. *bhindhí*) | none (*kunédʰti* "hide", nasal present to *kewdʰ-*, Gk κεύθω) | none | medium |
| t3-b002-00025 | DG | minor | *srowmom* is unaccented; the headword *srowmos* has no accent (expected *srówmos*, Gmc **straumaz*) [P10] | none ("stream" is right). Note: *sréwmn̥* "stream" (Gk ῥεῦμα, Ved. *srávman-*) is better attested but was not in the slice [R3] | none (ACC of goal; resumptive *só* is redundant but harmless) | high |
| t3-b002-00092 | DG | minor | *dewkéh₂ti* has a full-grade root, but its only reflex, Gmc **tugōną* "tug", requires zero grade **dukéh₂-*. A single-reflex Gmc ō-verb back-projected as an athematic *-éh₂-* present [R7] | none ("pull" is right). Note: *tóm* (masc.) for "it" is fine if the referent is masculine | none | medium |
| t3-b002-00043 | DG | ok | none (*gʰr̥némt*; o-grade causative *troméyet*) | none. Note: *troméyeti* is intransitive in Gk τρομέω but causative in Umbr. *tremitu*; causative *-éye-* is the regular reading | none | medium |
| t3-b002-00202 | DG | ok | none (*bʰéh₂s*, *mléwHs*: athematic injunctives) | none (*smélos* "falsehood": Lith. *mẽlas* "lie", masc. o-stem, so thematic inflection is right) | none (*mē* + injunctive [P8 fixed]; masc. *tóm* resumes *smélom*) | medium |
| t3-b002-00009 | | ok | none (*yéwos* NOM; *ne-kʷe* "and not", cf. Lat. *neque*) | none (*bʰuHyéti* "grow" of grain, cf. pilot 2 00148) | none | high |
| t3-b002-00183 | DG | minor | ACC *mḗdom* should be *mḗdos* (s-stem neuter) [R2] | Note: *h₁opéyeti* "make reach, deliver" for "give (as a fine)" is apt (Ved. *āpáyati*), but it is a causative where *dédeh₃ti*/*déh₃t* would be the default | none (relative–correlative *h₁yós … só*: good; SBJV *h₁opéyēti* for "shall") | medium |
| t3-b002-00163 | | ok | none (hysterokinetic ABL *pkʷtrés*; comparative *méǵh₂yōs*; IMPF *h₁ést*; ABL *méd*). Note: the headword is *méǵyōs*, the form *méǵh₂yōs* [Q3, trivial] | none | none (ABL of comparison: good) | high |
| t3-b002-00115 | | ok | none | none | Note: enclitic *te* as an ACC of goal with a person ("went to you") is Vedic-style (*yāhi devā́n*) but rarer than with places | medium |
| t3-b002-00170 | | ok | none (*tḱimé*: zero-grade athematic 1pl) | none (intransitive "we settled" matches Ved. *kṣéti* "dwells") | none | high |
| t3-b002-00016 | DG | minor | none (*pléḱtom*, Lat. *plectō*; *km̥Hnā́m* < *-néh₂m̥* by Stang's law, consistent with *tā́m*) | *pleḱnóm* "braid" stretches the gloss: a verbal adjective "plaited" used as a noun. Its only reflex is Skt. *praśná-*, which normally means "question" (< *preḱ-*); a "plaited basket" sense is lexicographically marginal. The derived gloss licenses "plaited", not "braid" [R1] | none | low-medium |
| t3-b002-00123 | DG | minor | none (root aorist *dʰéh₁s*, *dʰéh₁m̥*) | *pleḱnóm* "braid": as 00016 [R1] | none (fronted *kʷíd*) | low-medium |
| t3-b002-00186 | DG | ok | none (*gʷʰéns*, *kunédʰs*: injunctives) | none | none (*mē* + injunctive; fem. *tā́m* for the sheep) | high |
| t3-b002-00060 | DG | minor | *gurnos*, *wēdos* and *h₁rudʰyos* are all unaccented headwords [P10] | Notes: *h₁rudʰyos* "red" (Slavic *ryďь* "reddish") is thin; *h₁rudʰrós* (Gk ἐρυθρός, Lat. *ruber*) and *h₁rowdʰós* are in the lexicon but not in the slice [R3]. *gurnos* "back" (Arm. *kuṙn*; Balt. "hip") and *wēdos* "wet" (Gmc only) are thin | none (GEN *tósyo* as "his": good) | medium |
| t3-b002-00058 | DG | ok | none. MID imperfect *kundʰtó* "hid herself" is correctly formed (weak stem + *-to*); Q1 is fixed | none | none (*ne* + aorist *ǵnéh₃t* "did not recognize") | high |
| t3-b002-00154 | DG | minor | none (GEN *dh₃trés*; perfect *ǵeǵónh₁e*, Gk γέγονε: intransitive, so not P7) | *gʷéyh₃ti* "live" is an athematic construction. Its only reflex is Epic Gk βείομαι (future-like). *gʷíh₃weti* (Ved. *jī́vati*, Lat. *vīvit*, OCS *živetъ*; `attested_in` 14) was in the same slice; the planner chose the attested_in-2 word [Q2, R3] | none | medium |
| t3-b002-00227 | DG | **wrong** | none (thematic optatives *ǵʰléydoyt*, *léwkyoyt*; ACC *dʰwórm̥*) | *léwkyeti* is glossed "bright [-yeti: transitive present verb]" and planned as "brighten (the door)". Its only reflex, Gk λεύσσω, means "look at, behold". The sentence says "may it look at the door". The transitive "light up" is *lowkéyeti*, which is in the lexicon but not in the slice [R1] | none (neuter *tód* resumes *péh₂wr̥*) | high |
| t3-b002-00097 | | minor | *wésmn̥os* is not a possible o-stem: *-n̥-* cannot stand before a vowel. Its listed reflexes, Gk ἑανός and Skt. *vásana-*, point to **wés-n̥-o-*/**wes-ono-*, with no *m*. The slice gloss is "garment?". *wésmn̥* "garment" (Ved. *vásman-*) is in the lexicon [Q4]. *wēdos* is unaccented [P10] | none (it does say "garment … wet") | none (unmarked yes/no question) | medium |
| t3-b002-00065 | DG | ok | none (*gʷm̥sḱóme*; weak stem *km̥Hn̥h₂mé*) | none | none | high |
| t3-b002-00162 | DG | minor | none (athematic OPT *gʷih₃yéh₁s*, thematic *bʰuHyóys*) | *gʷéyh₃ti* chosen over *gʷíh₃weti* [Q2, R3]. In the batch, 00165 even uses both in one sentence ("He lives, and I live, and you live") | none | medium |
| t3-b002-00145 | | ok | none (*memógʰe*, Goth. *mag*) | none | none | high |
| t3-b002-00206 | DG | ok | none (SBJV *gʷr̥h₃ḗti*, *píph₃ēti*) | Note: *gʷl̥dʰyéti* (Ved. *gṛ́dhyati*) means "be greedy, covet" more than "be hungry". The derived gloss carries the root gloss "greedy, hungry", so this is a stretch but recoverable. *gʷr̥h₃éti* "devour" for "eat" is fine | none (two relative–correlative pairs: good) | medium |
| t3-b002-00198 | | ok | none (s-stem LOC *gʷʰéresi*, Ved. *háras-*) | none | none (*mē* + injunctive *bʰéres*) | high |
| t3-b002-00107 | | minor | none | The answer switches verbs: *dʰégʷʰeti* in the question, *h₁éwseti* in the answer. *h₁éwseti* is transitive in every witness (Ved. *óṣati*, Lat. *ūrō*, Gk εὕω), so "it is burning" (intransitive) needs the middle or *dʰégʷʰeti* again [R4, R6] | none | medium-low |
| t3-b002-00113 | | ok | none (PRF 2sg *bʰebʰóydʰth₂e*, phonetically *-tth₂-* by Bartholomae; Gk πέποιθα) | none | none | high |
| t3-b002-00101 | DG | ok | none (athematic SBJV *téksomos*; *winéh₁si*; *Hrésgoh₂*) | Note: three different "weave" verbs (*téks-*, *wineh₁-*, *Hresg-*) in one exchange [Q2 noise] | none (contrastive *túH … h₁eǵ*) | medium |
| t3-b002-00235 | DG | ok | none (VOC *stéwtor*; IMP *sth₂dʰí*, cf. Gk στῆθι, whose full grade is a Greek levelling; thematic IMP *séngʷʰe*) | none (*stéwtōr* = Ved. *stotár-* "praiser": very good) | none | high |
| t3-b002-00095 | | ok | none (*stunédt*, nasal present, Lat. *tundō*) | none | none | high |
| t3-b002-00078 | | ok | none | none | Note: fem. *séh₂* in "what is this?" anticipates the answer *h₂wĺ̥h₁neh₂*; neuter *tód* would be the neutral question | medium |
| t3-b002-00175 | | ok | none (PRF 2sg *h₁eh₁lówdʰth₂e*) | Note: the lexeme merges two homophonous roots. Skt. *ruróha*/Av. *urūruduša* "has grown" supports the gloss, but the listed Gk εἰλήλουθα "has come" belongs to *h₁lewdʰ-* "go" | none (focused *túH* in an answer to "who") | medium |
| t3-b002-00116 | | ok | none (thematic aorist *h₁ludʰét*, Gk ἤλυθε) | none | none | high |
| t3-b002-00233 | | ok | none (*dedórḱth₂e*, Gk δέδορκα; *ǵn̥néh₃si*) | none | none | high |
| t3-b002-00238 | | ok | none (perfect optative *tetr̥pih₁ént*) | none (*moysós* "ram", Ved. *meṣá-*) | Note: two singular conjuncts may take a dual verb; the plural is acceptable | high |
| t3-b002-00195 | DG | minor | ACC *mḗdom* should be *mḗdos* [R2] | Notes: *sh₁ésdʰeti* "harvests" has **no** reflex (a pure construction: noun root + *-dʰe-*); *sh₁esós* "crop" (Ved. *sasá-*) is fine | none | medium |
| t3-b002-00187 | | ok | none | none | none | high |
| t3-b002-00042 | DG | minor | LOC.SG *dʰoHnéh₂* = NOM. The handbooks give eh₂-stem LOC *-eh₂-i* (Ved. *-āyām*, Gk -ᾱι, Lat. *-ae*). The engine lists the endingless form first [P3, engine] | none (*sh₂éwti* "pour": Hitt. *šuḫḫa-*; neuter *tód* resumes *mélit*) | none | medium |
| t3-b002-00089 | | ok | none (*h₂lékse*; zero-grade *ph₂smós*) | Note: the answer swaps *h₂lékseti* → *péh₂sti*; both mean "protect" [R4, not counted] | none | high |
| t3-b002-00143 | | ok | none (*skinédsi*, *skinédmi*: Ved. *chinátsi*, *chinádmi*) | none | none | high |
| t3-b002-00012 | | ok | Note: *wéwket* (no *ʷ*) is Wiktionary's headword, justified by the boukólos rule (*kʷ* delabialized next to *w*); Gk εἶπον keeps the labial | none | none (DAT *h₁n̥gʷnéyey*; *mē me* + injunctive) | medium |
| t3-b002-00051 | DG | minor | none | *bʰlongós* is glossed "to blaze, burn [-os: action/result noun]" and planned as "the blaze". But o-grade with an oxytone thematic vowel is the agent/adjective type (*tomós* "cutting" vs *tómos* "a cut"), and the only reflex, Gmc **blankaz* "shining, white", is an adjective. The PIE says "I fear the bright (one)". Recoverable [R1]. Notes: *ḱr̥snéh₂ti* "run" rests on Gmc **hurzōną* "hurry" [R7]; *dedwóye* + ACC is Greek-like (δέδοικα + acc.) | none | medium |
| t3-b002-00209 | | **wrong** | none | The English is one sentence, "Do not leave him!". The PIE adds a second, *mē me linékʷs* "do not leave me!". The plan has an extra clause that the English does not contain [R5] | none | high |
| t3-b002-00124 | | ok | none (iterative *bʰoréyeti*, Gk φορέω) | none | none (neuter *tód* for the plough) | high |
| t3-b002-00126 | DG | ok | none | none (*stéwtōr*, *séngʷʰeti*) | none | high |
| t3-b002-00008 | | minor | VOC *moysé* keeps the oxytone accent. A PIE vocative is initial-accented (Ved. *vṛ́ka*), so expected *móyse* [P5, engine]. ACC *yéwos* = NOM (Wiktionary's neuter s-stem against masc. Ved. *yáva-*, Lith. *javaĩ*) [Q4] | none | none (*mē* + injunctive *h₁éds*; perfect *dedórḱe*) | medium |
| t3-b002-00153 | DG | minor | *h₂emseti* is unaccented [P10]. Note: ACC *h₃rḗǵnih₂m̥*: the devī type has *-ih₂m* (Ved. *rā́jñīm*), and the spec has `gender: m`, `devi: false` (low confidence). Note: ACC *népotm̥* vs Lat. *nepōtem* (ō levelled), defensible | *h₂emseti* "give birth" rests on one Hieroglyphic Luwian form (cf. Luw. *ḫamša-* "grandchild") [R3] | none (*wédʰet* "led (as bride)": apt; DAT *tósmey*) | medium |
| t3-b002-00166 | | minor | none (*tḱéyt*) | "settled us" uses *tḱéyti* transitively with a personal object. The root is "dwell" (Ved. *kṣéti*), and a transitive use takes a place (Gk κτίζω). "Make us dwell" needs a causative. The slice gloss "to settle, to populate" invites the error [R6] | none | medium |

## Systematic patterns

**Fixed since pilot 2, confirmed in this sample.**

| pattern | evidence in this sample |
|---|---|
| Q1 (middle voice) | the plan schema now produces MID: 10 MID tokens in the batch, and *kundʰtó* "she hid (herself)" (00058) is correct. No deponent is realized as active |
| P2/Q5 (imperatives) | *kapyé*, *h₂lékse*, *séngʷʰe*, *sth₂dʰí*, *kundʰdʰí*, *dewkh₂dʰí* |
| P6 (anaphor gender) | neuter *tód* for *péh₂wr̥*, *mélit*, *h₂érh₃trom*; fem. *tā́m* for *h₂ówis* |
| P8 (prohibitives) | *mē* + injunctive throughout (00008, 00012, 00186, 00187, 00198, 00202, 00209) |
| Q2 (`attested_in` in slices) | the field is present, but the planner does not always use it (see R3) |

Also right throughout:
- ABL of comparison;
- relative–correlative laws with the subjunctive;
- Wackernagel enclitics;
- perfects with present meaning (*dedórḱe*, *bʰebʰóydʰe*, *memógʰe*);
- s-stem LOC *gʷʰéresi*;
- i-stem DAT *h₁n̥gʷnéyey*.

No planner error in case or role assignment.

**R1. Derived-gloss suffix functions assert meanings that the reflexes contradict.** This is the main finding on derived glosses.
- **Source:** the derived gloss (`derived_glosses.jsonl`: root meaning + generic suffix label).
- **Sample:** 4 records.
  - 00227 *léwkyeti* "brighten" is Gk λεύσσω "look at". **Wrong.**
  - 00051 *bʰlongós* "blaze" is an oxytone adjective, Gmc **blankaz* "white, shining".
  - 00016 and 00123 *pleḱnós* "braid" is a verbal adjective whose only reflex, Skt. *praśná-*, normally means "question".
- **Batch:** these lexemes plus four more with the same defect touch **21 records** (17 without *pleḱnós*):
  - *dʰowh₂os* "smoke" (Gmc **dawwaz* "dew"), 2 records;
  - *meh₂turós* "good, great" (Lat. *mātūrus* "ripe, timely"), 4 records. "O master, you are good" (00223, 00229) is wrong;
  - *wl̥gnós* "wet" (Gmc **wulkną* "cloud", a noun), 1 record;
  - *musn̥Hyéti* "lift, pick up" (Ved. *muṣāyáti* "steals"), 2 records ("Pick it up!").
- **Mechanism:** the suffix label is generic. *-os* "action/result noun" ignores accent and stem class. *-nós* "verbal adjective" and *-yeti* "transitive present" are applied blindly. The root meaning is then taken over unchanged, even when the single listed reflex has a different meaning.
- **Fix:**
  1. Keep `gloss_approximate` only for transparent productive suffixes: agent *-tōr*, causative *-éye-*, instrument *-trom*, action *-tis*/*-tus*, and nasal or thematic presents of verbal roots. All of these were right in the sample.
  2. For *-os*/*-ós*, *-nós*, *-yós*, *-yeti*, *-rós*, *-mos*, require either `attested_in` ≥ 2 or a human-checked gloss.
  3. Make the *-os* label accent-sensitive: barytone = action/result noun; oxytone = agent/adjective.
  4. Block *léwkyeti*, *dʰowh₂os*, *wl̥gnós*, *meh₂turós* and *musn̥Hyéti* now, or regloss them ("look at", "dew", "cloud", "ripe", "steal").

**R2. Neuter s-stems are declined as thematic masculines when the lexeme has no paradigm table.**
- **Source:** engine classifier (`shape:thematic` is the default for any *-os* headword) together with the derived affix `pie-lex-os`. That affix entry conflates thematic *-o-* and s-stem *-es-*: its own reflexes list Lat. *-us*/*-ere* and Gk *-os*/*-ein*.
- **Sample:** 00024, 00183, 00195: *mḗdos* ACC *mḗdom* (Gk μῆδος/μήδεα n.; the lexicon stems *mḗdos/médos* show the ablaut of an s-stem).
- **Batch:** **10 records**:
  - *mḗdos* ×6 (00024, 00183, 00184, 00195, 00201, 00208), always ACC *mḗdom*;
  - *h₁éh₁ugʰos* "vow" ×4 (00185, 00190, 00199, 00239), ACC *h₁éh₁ugʰom*, although Gk εὖχος and Skt. *óhas* are both neuter s-stems.
- This is P1 recurring through a route the pilot-1 fix did not cover (that fix applied to table-derived nouns).
- **Fix:** in classification, route an *-os* headword to the neuter s-stem when:
  - its reflexes include a Greek *-ος* neuter, a Greek *-εα* plural, a Sanskrit *-as* neuter or a Latin *-us/-eris*; or
  - its `stems` list shows *ḗ/é* ablaut.
  - Otherwise flag it as unknown-gender and keep it out of slices until it is checked.
- Re-realize the 10 records. (Smaller cases: *smélos* and *stónos* are correctly thematic, since Lith. *mẽlas* and Gk στόνος are masculine.)

**R3. Slice construction lets thin or derived lexemes in without their well-attested synonyms, and the planner does not always use `attested_in`.**
- **Source:** the slice builder (`scripts/make_slice.py`) and the planner.
- The slice is keyword hits + core verbs + a **random fill** from the whole pool (`rest` shuffled). The fill does not prefer dictionary-glossed or well-attested words, and it never brings along a plain synonym. So concepts outside the keywords ("stream", "red", "garment", "blaze") come in only through thin lexemes:
  - *srowmos* (*sréwmn̥* absent);
  - *h₁rudʰyos* (*h₁rudʰrós*, *h₁rowdʰós* absent);
  - *wésmn̥os* "garment?" (*wésmn̥* absent);
  - *bʰlongós*, *léwkyeti* (*lowkéyeti* absent).
- Separately, *gʷíh₃weti* (`attested_in` 14) was in the slice, but *gʷéyh₃ti* (2) was chosen in 6 records. This breaks brief rule 9 [Q2].
- **Sample:** 00025, 00060, 00097, 00153, 00154, 00162 (and 00227, 00051 via R1).
- **Batch:** **20 records** use *srowmos*, *h₁rudʰyos*, *wésmn̥os* or *gʷéyh₃ti*.
- **Fix:**
  1. Draw the random fill only from Wiktionary-glossed lexemes or those with `attested_in` ≥ 3.
  2. Whenever a `gloss_approximate` lexeme is included, also include the best plain-glossed lexeme whose gloss shares its head word.
  3. Have the plan checker warn when a `gloss_approximate` lexeme is used while a same-gloss plain lexeme with higher `attested_in` is in the slice.

**R4. Question/answer and command/answer pairs switch verb lexemes.**
- **Source:** planner.
- **Batch:** 9 question→answer pairs with a different V lexeme, plus 4 imperative→answer pairs.
  - In about 7 of them the English repeats one verb: 00077, 00107, 00134, 00150, 00089, 00084, 00122.
  - The others are intended (00114 "awake/alert", 00146 "upset/afraid").
- The switch is harmless where the two verbs are synonyms (00089 *h₂lékseti*/*péh₂sti*). It is a meaning error where valency differs (00107: transitive *h₁éwseti* for intransitive "is burning").
- Counted only in 00107.
- **Fix:** brief: "an answer repeats the question's verb lexeme unless the English changes the verb". Checker warning when the English answer repeats the question's verb but the V `lex_id` differs.

**R5. A plan clause that is not in the English.**
- **Source:** planner (the initial plan already had it; repair did not touch it).
- 00209 adds "do not leave me!" to "Do not leave him!".
- **Batch:** 1/250. Three other records also have more PIE sentences than English sentences (00012, 00026, 00105), but those are quoted speech, which is legitimate.
- **Fix:** the checker compares the number of plan clauses with the number of finite clauses in the English (count quoted speech separately), or runs a gloss-back check of `gloss` against `english`.

**R6. An ambiguous English gloss leads to a wrong valency.**
- **Source:** lexicon gloss and the slice's English glosses.
- *tḱéyti* "to settle, to populate" is used as transitive "settled us" in **4 records** (00166, 00167, 00173, 00176). Its only intransitive use is 00170. *h₁éwseti* "to burn" is used intransitively once (00107).
- **Fix:** add a valency tag to verb glosses in slices ("dwell, settle (intr.)"; "burn (tr.)"), and gloss *tḱéyti* as "to dwell; to settle (intr.)".

**R7. Single-reflex Germanic ō-verbs back-projected as athematic *-(n)éh₂-* presents.**
- **Source:** lexicon tree-path derivatives.
- Examples:
  - *ḱr̥snéh₂ti* "run" (Gmc **hurzōną* "hurry"), 6 records;
  - *dewkéh₂ti* "pull" (Gmc **tugōną*: the zero grade requires **dukéh₂-*, so the full grade is an error), 2 records;
  - *km̥Hnéh₂ti* "hum" (Gmc **hummōną*), 2 records.
  - Together: **10 records**.
- The meanings are acceptable. The formations are speculative, and the engine conjugates them as ablauting athematic presents (*dewkh₂dʰí*, *km̥Hn̥h₂mé*), which no daughter shows.
- Counted only in 00092 (the full grade).
- **Fix:** correct *dewkéh₂ti* → *dukéh₂ti* or block it. Mark one-branch tree-path verbs as `attested_in` 1 so that R3's gate excludes them.

**P3 (recurs, engine). Endingless eh₂-stem locative.**
- `_EH2["LOC.SG"] = ["", "i"]` in `pie/morph.py` puts the endingless form first, so LOC *dʰoHnéh₂* = NOM (00042).
- The pilot-1 *-i* locative fix covered consonant stems but not this class.
- **Batch:** 1 record.
- **Fix:** reorder to `["i", ""]`, giving *-eh₂i* (Fortson, Beekes).

**P5 (recurs, engine). Thematic vocatives keep the final accent.**
- `_thematic` keeps the accent on the thematic vowel for every case, so VOC *moysé* (00008).
- The athematic path already calls `_initial_accent` for the VOC (hence *h₁ń̥gʷni*, *póti*).
- **Batch:** 1 record (the other 8 vocatives in the batch are correct).
- **Fix:** apply `_initial_accent` to VOC.SG in `_thematic`.

**Q4 (recurs). Source-headword defects pass through.**
- *yéwos* is declined as a neuter s-stem from Wiktionary's table (ACC *yéwos* in 00008, 00108, 00139; also LOC *yéwesi*, DAT *yéwesey*: 6 records).
- *wésmn̥os* is a phonotactically impossible headword with a queried gloss (6 records).
- **Fix:** block *wésmn̥os* (use *wésmn̥*), and override *yéwos* to a masculine o-stem. These two are worth a manual entry in the blocklist or overrides.

**Q2 (recurs, planner). Synonym noise.**
- Examples:
  - "live": *gʷéyh₃ti* vs *gʷíh₃weti*, both in 00165;
  - "weave": *téksti*/*wébʰti*/*Hrésgeti*/*pléḱteti*/*winéh₁ti*/*uh₁inéHti*. The last two are the same root, listed twice;
  - "burn": *dʰégʷʰeti* vs *h₁éwseti*;
  - "give": *déh₃t*/*dédeh₃ti*/*h₁opéyeti*.
- Counted only through R3 (00154, 00162).
- **Fix:** see R3. Also deduplicate *winéh₁ti*/*uh₁inéHti* in the lexicon.

**P10 (recurs, by design). Unaccented headwords.**
- *srowmos*, *h₂emseti*, *wēdos*, *h₁rudʰyos*, *dʰowh₂os*, *teh₂yeti*, *gurnos*: **15 batch records**. Four in the sample (00025, 00060, 00097, 00153) are counted *minor*, as in pilot 2.
- All seven are thin (one or two branches).
- **Fix:** with R3's attestation gate they would mostly drop out of the slices. Otherwise exclude unaccented lexemes from slices.

**P9 (recurs). Overt 1/2-person subject pronouns.**
- 27 plans in the batch. In the sample they are contrastive or focus answers (00101, 00116, 00175), which is legitimate.
- Not counted.

**Low-confidence observations (not counted):**
- **h₃rḗǵnih₂:** the spec has `gender: m`, `devi: false`, so ACC is *-ih₂m̥* rather than the devī-type *-ih₂m* (Ved. *rā́jñīm*). A gender-*m* spec on "queen" would also break adjective agreement if an adjective ever modifies it (none does in b002).
- **wéwket:** delabialized by the boukólos rule; a school difference.
- **pleḱnós:** the Skt. *praśná-* attribution may rest on a lexicographic "plaited basket" sense. If so, R1 for this word drops to a note.
- **h₁eh₁lówdʰe:** "is grown" draws on two homophonous roots (see 00175).
- **Morphophonemic clusters:** *kundʰdʰí*, *bʰebʰóydʰth₂e* and *kunédʰs* are written without assimilation, consistently with earlier batches.

## Counts

| verdict | n | records |
|---|---|---|
| ok | 31 | |
| minor | 17 | DG: 00024, 00025, 00092, 00183, 00016, 00123, 00060, 00154, 00162, 00195, 00042, 00051, 00153; other: 00097, 00107, 00008, 00166 |
| wrong | 2 | 00227 (DG), 00209 |

| issue kind (records with at least one counted issue) | n | records |
|---|---|---|
| form | 10 | 00024, 00183, 00195, 00092, 00025, 00060, 00097, 00042, 00008, 00153 |
| meaning | 9 | 00227, 00209, 00016, 00123, 00051, 00154, 00162, 00107, 00166 |
| syntax | 0 | |

| pattern | sample records (counted) | batch records (of 250) | source |
|---|---|---|---|
| R1 derived-gloss meaning drift | 4 (00227, 00051, 00016, 00123) | 21 (17 without *pleḱnós*) | derived gloss |
| R2 s-stem as thematic | 3 (00024, 00183, 00195) | 10 | engine classifier + affix gloss |
| R3 thin lexeme over attested synonym | 3 (00154, 00162, 00153) + via P10/Q4 | 20 | slice builder + planner |
| R4 Q/A verb switch | 1 (00107) | ~7 unintended of 13 | planner |
| R5 extra clause | 1 (00209) | 1 | planner |
| R6 valency from ambiguous gloss | 2 (00166, 00107) | 5 | lexicon gloss |
| R7 one-reflex *-(n)éh₂-* verbs | 1 (00092) | 10 | lexicon (tree path) |
| P3 eh₂ LOC | 1 (00042) | 1 | engine |
| P5 thematic VOC accent | 1 (00008) | 1 | engine |
| Q4 source headword | 2 (00097, 00008) | 12 | lexicon |
| P10 unaccented | 4 (00025, 00060, 00097, 00153) | 15 | lexicon |

## Verdict

**Is the wrong rate acceptable for scaling? Yes.**
- 2/50 (4%) wrong is below pilot 1 (10%) and in the same range as pilot 2 (2%). At n = 50 the difference from pilot 2 is not significant; the 18% figure is pilot 2's *minor* rate. Neither wrong record comes from the morphology engine: one is a planner clause error, one a derived gloss.
- The batch-wide picture is less rosy. R1's 17 strictly drifted records suggest a true wrong rate of about **6–9%**. That is still inside or below the pilot band, and nearly all of it is removable by gating a handful of lexemes.
- The engine-side residue (P3, P5, R2) is small and mechanical. R2 is the only one with real volume (10 records).
- Recommend scaling **after** the three fixes below, and re-realizing the affected b002 records rather than discarding them.

**Should derived-gloss lexemes stay in the planner's vocabulary? Yes, but behind a gate, not wholesale.**
- The DG half had the same wrong rate as the rest (1/25) but 13/25 minor. Those minors come from the derived lexemes themselves: 4 meaning stretches, 3 s-stem errors, and 5 from thin or unaccented words chosen over standard ones.
- Derived lexemes with transparent productive suffixes were consistently good, and they add real vocabulary: *stéwtōr*, *h₂molǵéyeti*, *troméyeti*, *kunédʰti*, *séngʷʰeti*, *smélos*, *srowmos*.
- The bad ones share three features that are cheap to test:
  - an ambiguous suffix label (*-os* without accent, *-nós*, *-yeti*, *-yós*, *-rós*);
  - a single reflex;
  - no plain-glossed competitor in the slice.

**Top fixes, in order:**
1. **Gate derived-gloss lexemes (R1, R3, R7).**
   - Keep only transparent suffixes, or `attested_in` ≥ 2 plus an accent-aware *-os* label.
   - Block or regloss *léwkyeti*, *bʰlongós*, *dʰowh₂os*, *wl̥gnós*, *meh₂turós*, *musn̥Hyéti*, *dewkéh₂ti*.
   - Restrict the slice's random fill to plain-glossed, attested lexemes, and pair each derived item with its plain synonym.
2. **Route *-os* nouns with s-stem evidence to the neuter s-stem (R2)**: *mḗdos*, *h₁éh₁ugʰos*; 10 records to re-realize.
3. **Planner and checker guards:**
   - warn on a `gloss_approximate` lexeme chosen over a higher-`attested_in` synonym (*gʷéyh₃ti*);
   - check plan clauses against the English clause count (R5);
   - keep the Q/A verb the same (R4).
   - Plus the two one-line engine fixes: eh₂ LOC `-i` first (P3), initial-accent thematic VOC (P5).
