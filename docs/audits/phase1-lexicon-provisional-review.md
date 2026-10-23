# Phase 1 lexicon audit: provisional review

- **Status:** PROVISIONAL. This review is knowledge-based only. No handbooks (LIV², Mallory & Adams, Fortson, Ringe, Beekes, Pokorny) or web sources were consulted. Every claim needs checking against the books before anything is fixed on its basis.
- **Date:** 2026-10-23
- **Sample:** `docs/audits/phase1-lexicon-sample-50.jsonl` (20 roots, 15 words, 15 derivatives)

**Legend.** The verdict covers the whole entry: form, meaning, `root_id`, type/aspect, and the sampled reflexes. The `issue` column starts with the part that fails: **[form]**, **[meaning]**, **[root_id]**, **[type/aspect]**, **[reflex]**, or **[builder]** for a data or parsing artefact. "questionable" can therefore mean a sound root with one bad reflex. Read the tag. Confidence is my confidence in the verdict, not in the reconstruction.

## Entry table

| id | form | verdict | issue (short) | confidence |
|---|---|---|---|---|
| pie-root-h2ed-dry | h₂ed- | questionable | [meaning][type/aspect] Two senses that look like separate homographs are merged: "to dry" (cf. Hitt. ḫāt- 'dry up'; its root shape is itself debated) and "grain, barley" (Lat. ador, Arm. hat, Goth. atisk, nominal). The heuristic read only the first sense and called it verbal. No reflexes. | med |
| pie-root-h2elh1-grind | h₂elh₁- | ok | Mainstream (LIV² *h₂elh₁-; Gk. aléō, Arm. alam). [builder] No aspect, and reflexes are empty even though derivative h₂léh₁wr̥ has some. | high |
| pie-root-terp-satisfy | terp- | ok | Mainstream (LIV² *terp- 'become sated'; Skt. tṛp-, Gk. térpō). [builder] No aspect, no reflexes. | high |
| pie-root-gweyh3-live | gʷeyh₃- | ok | Mainstream (LIV² writes *gʷi̯eh₃-; it is the same root). [reflex] The sample skips the core witnesses (Skt. jīvati, Lat. vīvō). Arm. keam and Pashto žwënd are fine. Alb. nxit / zit and PAlb. *džita are ones I cannot confirm. | med |
| pie-root-neygw-wash | neygʷ- | questionable | Root is mainstream (LIV² *nei̯gʷ-; Skt. nij-, Gk. níptō, OIr. nigid). [reflex] PSl. *něgati: deriving the *něga 'tenderness' family from 'wash' is speculative at best. | low |
| pie-root-keh1w-wobble | keh₁w- | questionable | [form] I cannot place this root in LIV² or the handbooks. There are no reflexes to test it against. It may be a Wiktionary-only root. | low |
| pie-root-h1reh1p-take_away | h₁reh₁p- | questionable | [form] LIV² has *h₁rep- (short vowel; Gk. ereptomai, Lat. rapiō, Alb. rjep). The *-eh₁- rests on Lith. rė̃pti. Treat it as a Wiktionary-school variant, not mainstream. | med |
| pie-root-peyh2-swell | peyh₂- | ok | LIV² *pei̯H- 'swell, be fat'. Wiktionary fixes the laryngeal color as h₂, which is more specific than LIV. The two glosses mix eventive and stative senses, and no aspect is given. | med |
| pie-root-kers-cut | kers- | ok | Plausible (Hitt. karš- 'cut off'). I cannot confirm the LIV² entry or the pf aspect from memory. Plain vs palatal velar is not decidable from Hittite alone. No reflexes. | low |
| pie-root-bheg-break | bʰeg- | questionable | Root is mainstream (*bʰeg-, nasal present in Skt. bhanákti, OIr. bongid; Arm. bekanem has no nasal). [reflex] PGmc *bangōną fails Grimm's law: *g gives Gmc *k, so *bʰ(o)ng- would give *bank-. *bang- is almost certainly onomatopoeic. PGmc *bikjaną is unclear to me. Skt. bhañj-/bhaṅgá and Khot. fit. | med |
| pie-root-kleh2-put | kleh₂- | ok | Plausible (Lith. klóti 'spread, lay'). LIV status not recalled. No reflexes to check. | low |
| pie-root-dem-build | dem- | questionable | [form] LIV² has *demh₂- 'build, join' (Gk. démō, -dmē- forms). Wiktionary splits it into *dem- 'house' and the verb, and this lemma drops the laryngeal. [reflex] Alb. dhomë is usually taken as a Greek loan, and it is listed twice. HLuw. ta+mi-ha fits *demh₂-. | med |
| pie-root-kjlewH-clean | ḱlewH- | questionable | Root plausible (Gk. klúzō, Lat. cluō, Goth. hlutrs). [meaning] The "to slide" sense is odd. [reflex] Proto-Finnic *luuta is a Baltic loan presented as a reflex. PSl. *Slovǫta (capitalised, so apparently a name) is unclear. The Baltic 'sweep' words are debated. | low |
| pie-root-tres-tremble | tres- | ok | Mainstream (LIV² *tres-; Skt. trásati, Gk. tréō, Lat. terreō). impf is fine. OIr. tarrach < *tr̥s- fits. | high |
| pie-root-gwher-be_warm | gʷʰer- | ok | Mainstream (LIV² *gʷʰer-; Skt. gharmá, Gk. thermós). [builder] No aspect. | high |
| pie-root-h2weh1-blow | h₂weh₁- | ok | Mainstream (LIV² *h₂u̯eh₁-). impf is fine. Gk. atmós / aütmḗ and the Baltic 'cool' words are acceptable. [reflex] The Albanian items (vetëtin, fjur, PAlb. *awuòr) are speculative or unverified. | med |
| pie-root-h3sleydh-slip | h₃sleydʰ- | questionable | [form] LIV² has *slei̯dʰ-. The initial h₃ is motivated only by Gk. olisthánō. **Check whether the source form was *(h₃)sleydʰ-**: if so, the builder made an optional segment obligatory. #h₃sl- is a rare cluster. | med |
| pie-root-h2leg-care_for | h₂leg- | questionable | Root plausible (Gk. alégō 'heed'). [reflex] Gk. álgos 'pain' belongs to *h₂elg-. Linking it to *h₂leg- needs metathesis and is not standard. | med |
| pie-root-prekj-ask | preḱ- | questionable | Root mainstream (LIV² *preḱ-). [reflex] Lat. percontor is per- + contus 'pole' and is not from *preḱ-; the real Latin reflexes are precor and poscō. Arm. harsn, Lith. piršti, PGmc *frehnaną and Kurd. pirs are fine. | high |
| pie-root-h2ekj-sharp | h₂eḱ- | questionable | Root mainstream. Nominal is a reasonable call: the root is mostly adjectival/nominal and LIV hardly treats it as a verb. Lat. occa and Arm. hask fit. [reflex] I cannot identify Avestan "asūra" or Armenian "osi" as reflexes of this root, and Alb. ath / eh are unverified. | low |
| pie-lex-nogwos | nogʷós | questionable | [form] The o-stem *nogʷó- is defensible (Winter's law gives BSl. *nōˀgás; Brugmann's law gives Skt. ā). [root_id] *negʷ- 'bare' looks like a back-formation; the handbooks usually treat *nogʷ- as non-ablauting. [reflex] Skt. nāgá 'snake' as "the naked one" is speculative; Skt. 'naked' is nagná-. PGmc *nakwōną is odd. | med |
| pie-lex-h2leh1wr | h₂léh₁wr̥ | ok | Fits Gk. áleuron and Arm. aliwr (Osthoff's law shortens *ēu). Beekes and others start from *h₂l̥h₁-eu-r-, so this exact ablaut is one view among several. Proterokinetic is plausible. | low |
| pie-lex-bhinedti | bʰinédti | ok | Textbook nasal present *bʰi-né-d-ti (Skt. bhinátti, Lat. findō). | high |
| pie-lex-ner | nér | questionable | [form][reflex] Pokorny's 4. *ner- 'under' (Gk. nérteros, énerthe) exists, but "Old Latin -ner" is not a reflex I recognise. No root_id. Probably a thin Wiktionary-only entry. | low |
| pie-lex-h3regjeti | h₃réǵeti | ok | Mainstream thematic present (Lat. regō, Gk. orégō, OIr. rigid). PGmc *rekaną is a plausible but less certain link. | high |
| pie-lex-bhebhoydhe | bʰebʰóydʰe | ok | Textbook perfect (Gk. pépoitha, Goth. baiþ). The Greek sample is 1sg (-a), the lemma 3sg (-e). That is a mismatch of cited forms, not an error. | high |
| pie-lex-eti-2 | éti | questionable | [meaning] "beyond, over" and "and" are spliced from what look like separate entries. [reflex] BSl. *ati, Lith. at-, Latv. at- have *a, which does not fit *e- (it needs *h₂eti or *oti). OPr. et- would fit. Arm. -ē is unclear. A "-2" id. | med |
| pie-lex-kjwox | ḱwṓ | ok | Mainstream hysterokinetic *ḱwṓ / *ḱunés. Hitt. kuwaš and Arm. šun fit. [builder] The Luwian sample is raw Anatolian hieroglyph code points, not a transliteration. Lydian kan- is unclear to me. | high |
| pie-lex-yewgos | yéwgos | questionable | Form fine (Gk. zeûgos). [reflex] Goth. jukuzi and PGmc *jūkaz/*jukaz have zero grade (*yug-) and do not continue an e-grade s-stem. [builder] Every Germanic reflex is listed twice. OHG "*jūh" is a starred form placed under an attested language. | med |
| pie-lex-perkjus | pérḱus | wrong | [root_id] 'Rib, chest' (Skt. párśu-, Av. pərəsu-, Alb. parz) is linked to *perḱ- 'colored, speckled' (Skt. pṛ́śni-, Gk. perknós). That is the wrong homograph. Leave it unlinked (root unclear) or link it to whatever Wiktionary names. The form, gender, and reflexes are fine. | med |
| pie-lex-wern | wern- | wrong | [root_id] An alder word (Alb. verr, Arm. geran, Gaul. verno-) is linked to *wer- 'squirrel/marten' (*wéwer-). This is obviously the wrong *wer- homograph. The correct link is no root, or Wiktionary's own (uncertain) one. | high |
| pie-lex-h2sowsos | h₂sowsós | questionable | [form] Mainstream writes the root *sh₂ews- (LIV² *sh₂eu̯s-, as I recall). *h₂sews- is a Wiktionary-school ordering (it drives the PIIr *Hs-). The adjective formation *-sowsó- is fine. | low |
| pie-lex-ghebhoxl | gʰébʰōl | wrong | [root_id] 'Head, gable' (Gk. kephalḗ, Gmc *gabla-, ToA śpāl) is linked to *gʰebʰ- 'give, take'. The words are unrelated homographs. The form itself is acceptable. [builder] Every Germanic reflex is listed twice. | high |
| pie-lex-h1wersos | h₁wersós | ok | Fits LIV² *h₁u̯ers- 'rain' (Skt. varṣá, Gk. (h)érsē with prothesis). [builder] Gk. hérsē is listed twice. Sanskrit and Greek are nouns, not the adjective; that is fine for a reflex list. | med |
| pie-lex-swepnos | swépnos | ok | Textbook (Skt. svápna-, Lat. somnus, ON svefn, Lith. sãpnas). | high |
| pie-lex-boli | boli- | ok | *bel- 'strong' (Skt. bála-, OCS bolьjь). Lat. dēbilis < *dē-bol-i- / *-bel-i- is the standard explanation. The stem is given without accent. | med |
| pie-lex-kretos | kretós | wrong | [root_id][meaning] The reflexes (Lith. kretė́ti, Latv. kretêt 'shake, tremble') belong to a *kret- 'shake' homograph, but the entry links to *kret- 'be strong' (Gk. krátos, Goth. hardus). The meaning array also splices "swelling" onto "a shake". An e-grade oxytone action noun is also odd. | med |
| pie-lex-h2ogjnyo | h₂oǵn̥yo- | questionable | [form] Rests on one branch (PToch. *ekäñye- 'possession'). The derivation is speculative. [builder] No `segmented` field, unlike the other derivatives. Root link is fine. | low |
| pie-lex-yemHos-2 | yémHos | questionable | [form][meaning] Skt. yamá- 'twin' is oxytone, while root-accented yáma- means 'rein, restraint'. The barytone *yémHos fits the 'rein' word, but the gloss is 'twin'. Possibly the "-2" collision mixed form and gloss. The root gloss 'mingle' is not what LIV² gives for *i̯emH- ('hold, restrain'). No reflexes. | low |
| pie-lex-probhHus | probʰHus | questionable | Lat. probus / Skt. prabhú < *pro-bʰ(H)u- is a standard etymology. [form] There is no accent (PIIr *prabʰHúš shows *-ús). The zero grade *bʰH- presupposes *bʰweH- (LIV² *bʰu̯eh₂-), which fits root_id *bʰuH- poorly. | low |
| pie-lex-kjerh2onowos | ḱerh₂onowos | questionable | [form] Lat. cernuus as the compound *ḱerh₂-o- + *now-o- ('nod') is clever but speculative. No accent. The second member's root (*new-) is not captured in root_id. That is a limitation of the data model. | low |
| pie-lex-pedom | pedom | questionable | Reconstruction mainstream (*pédom: Hitt. pēdan, Gk. pédon, Arm. het). [form] The accent is missing from both form and segmented, while Wiktionary's own lemma is *pédom. The reflexes are fine. | med |
| pie-lex-ligjhtos | liǵʰtós | ok | Textbook *-tó- adjective (Skt. līḍhá, with Bartholomae's law). [builder] Proto-Iranian and Khotanese forms are listed twice. | high |
| pie-lex-bhoh2gs | bʰóh₂gs | questionable | [form] LIV² has *bʰag- 'allot', with no laryngeal; *bʰeh₂g- is the Wiktionary school. An o-grade nominative in a root noun is unusual. [reflex] PGmc *bōks 'book' is normally from the beech word *bʰeh₂ǵ- (palatal). The 'allotment' derivation is a minority view. | med |
| pie-lex-worno | worno- | questionable | [reflex] Two ablaut grades sit under one lemma. BSl. *warnás fits *wor-no-, but Celtic *branos needs *wr̥-no- (*wr- > br-). [root_id] The link to *wer- 'burn' ("burnt, black") is a hypothesis, not established. No accent. | med |
| pie-lex-bhndhtos | bʰn̥dʰtós | ok | Textbook (Skt. baddhá, with Bartholomae's law). | high |
| pie-lex-kjrh2sexr | ḱr̥h₂sḗr | questionable | [form] An animate *-ḗr with an oblique *-n- stem (*ḱr̥h₂snós) is not a standard paradigm. The handbooks have an n-stem *ḱr̥h₂s-(r)-ōn (Lat. crābrō, -ōnis; Lith. širšuo, -ens). [reflex] PGmc/PWG *hurnut- has no *-s- and comes from the horn word *ḱr̥n-, not from this stem. It is also listed twice. | med |
| pie-lex-h3moygjhos-2 | h₃moyǵʰós | ok | Gk. moikhós < o-grade agent noun of *h₃meyǵʰ- is widely cited. The missing prothesis is explainable (laryngeal loss before *o, the Saussure effect). [builder] The "-2" id may be a duplicate record. | med |
| pie-lex-gownos | gownos | questionable | [reflex] Med. Gk. goúna, Late Lat. gunna, and probably PSl. *guňa form a loanword chain presented as inherited reflexes. PIIr *gawnám is a noun ('hair'), not 'furry'. [root_id] The link to *gew- 'bend' is speculative. No accent. Reflexes listed twice. | med |
| pie-lex-uh1yeyeti | uh₁yéyeti | questionable | [form] LIV² has *u̯ei̯h₁- 'wrap'. Lat. vīmen/vītis, Lith. vyti and OCS viti point to *wiH-, which favours *weyh₁- over *weh₁y-. A zero grade plus *-éye- is also atypical for this kind of present. Skt. vyáyati and Lat. vieō themselves fit either analysis. | low |

## Counts

| verdict | n |
|---|---|
| ok | 20 |
| questionable | 26 |
| wrong | 4 |
| **total** | **50** |

Of the 26 "questionable", about 9 rest on a reflex problem attached to an otherwise sound form (5, 10, 13, 18, 19, 20, 29, 45, 49 by line), and 6 are Wiktionary-vs-LIV disagreements over a form (7, 12, 32, 44, 50, and 17 in part). Neither group is a reconstruction error in the strict sense.

## Systematic patterns

These are hypotheses about builder causes drawn from the data alone. No code was read. Line numbers refer to the sample file.

1. **Aspect coverage hole.** Only the 3 roots whose type came from `head-template` (kers-, tres-, h₂weh₁-) have `aspect`. All 17 roots typed by `gloss-heuristic` have none. The heuristic can only say verbal/nominal; it cannot tell eventive from stative (gʷʰer- 'be warm' and peyh₂- 'be swollen' get no `stat`). Root type itself is right in all 20 cases except line 1.
2. **Gloss heuristic reads only the first sense, and sense arrays merge homographs.** Line 1 splices a verbal 'to dry' and a nominal 'grain, barley' and is typed verbal. Lines 27 ('beyond' + 'and') and 37 ('swelling' + 'a shake') also join senses from what look like separate entries or etymologies.
3. **Wrong-homograph `root_id` linkage: 4 of the 30 linked words and derivatives (13%), plus 2 or 3 doubtful.** Lines 30 (*perḱ- 'colored'), 31 (*wer- 'squirrel'), 33 (*gʰebʰ- 'give') and 37 (*kret- 'be strong'). Likely cause: matching on the root string or skeleton and taking the first homograph, not the root Wiktionary's etymology section actually names. Doubtful links: 45 (*wer- 'burn'), 49 (*gew- 'bend'), 21 (*negʷ-). Fix: resolve through the etymology template's target page and sense id, and leave the entry unlinked when the source says "uncertain".
4. **No reflex dedup.** The same form repeats within one language list on lines 12, 29, 33, 34, 43, 47, 49. Probably alt-forms or multi-sense descendant lines are each appended.
5. **Derivatives lose the accent.** Lines 40, 41, 42, 45, 49 (and stem 36) are unaccented, though for 42 Wiktionary's lemma is *pédom. The likely cause is that forms are taken from descendant-tree lines, not from the lemma page. Prefer the linked lemma page's headword when one exists.
6. **Reflexes are not propagated to roots.** 7 of 20 roots (lines 1, 2, 3, 6, 8, 9, 11) have empty `reflexes_sample`, yet line 22 (a derivative of line 2) has reflexes. The root's reflexes apparently come only from the root page's direct descendants and not from its derived terms.
7. **Borrowings and starred forms are treated as reflexes.** Line 13 (Proto-Finnic *luuta, a Baltic loan), 49 (Med. Gk./Late Lat. loan chain), 12 (Alb. dhomë, probably from Greek), 29 (starred *jūh under attested OHG), and 28 (raw hieroglyph code points for Luwian). Hypothesis: `bor=1`/`der=1`/`unc=1` flags and "?"/"possibly" markers are dropped. That would also explain the dubious reflexes on lines 10 (*bangōną), 18 (álgos) and 19 (percontor).
8. **One lemma, several ablaut grades.** Lines 29 and 45 (and 47 at the level of derivation) list descendants of different ablaut grades or derivatives under one entry. This is probably inherited from how Wiktionary groups its descendant trees.
9. **Sampling bias.** `reflexes_sample` follows the tree's order (Albanian, Anatolian, Armenian first), so samples overrepresent the least secure branches (lines 4, 16, 20, 31). This is not a data error, but it weakens any reflex-based audit. Sample the core witnesses (Skt., Gk., Lat., Gmc., BSl.) first.
10. **"-2" ids** (lines 27, 39, 48) may be the same lexeme harvested twice from different trees. Line 39 may also have form and gloss crossed between two homographs.
11. **Optional segments.** Line 17 *h₃sleydʰ- is the only candidate here (LIV² *slei̯dʰ-). Check whether the source was *(h₃)sleydʰ-. If so, the builder keeps the parenthesised segment, and it should strip it or store both variants.
12. **Missing fields.** Line 38 lacks `segmented`. ID slugs render ō/ē as "ox"/"ex" (kjwox, ghebhoxl, kjrh2sexr). That is harmless but worth documenting.

**Not builder bugs (school differences).** Wiktionary consistently follows its own root shapes against LIV²: h₁reh₁p- vs *h₁rep-, dem- vs *demh₂-, h₂sews- vs *sh₂eus-, bʰeh₂g- vs *bʰag-, weh₁y- vs *weyh₁-, and peyh₂- vs *peyH-. That is acceptable under the task's terms. A LIV-correspondence column would let the builder flag these divergences automatically.

---

## Triage (main session, 2026-10-23)

I checked each systematic pattern against the builder code and the raw dump.

| # | Pattern | Verdict | Action |
|---|---|---|---|
| 3 | Wrong homograph root (4/30) | **1 builder bug, 3 source claims.** The bug: *kretós* "swelling" and *kretós* "a shake", which sit under two different *kret-* roots, were merged by form. The other three (*pérḱus* under *perḱ-* "colored", *wern-* under *wer-* "squirrel", *gʰébʰōl* under *gʰebʰ-* "give") are where Wiktionary itself lists them. kaikki does not copy trees between homograph sections (0 of 97 multi-section pages share a tree). | **Fixed:** derivative dedup is now scoped by owning root, which splits 140 homonyms. Regression test added. The three Wiktionary placements are logged as disputed source claims for the books check. |
| 4 | Duplicate reflexes | Bug (one form reached through two paths) | **Fixed:** dedup on (language, form, romanization). Test added. |
| 7 | Borrowings and doubtful forms counted as reflexes | Partly a bug: the dump has `raw_tags` (`borrowed` 548, `learned borrowing`, `reshaped by analogy` 1,780, `uncertain` 1,807), but we only kept them as free-text notes | **Fixed:** explicit `borrowed` (inherited down a loan chain), `analogical`, `uncertain` flags. The Phase 3b checker will skip borrowed and analogical forms. |
| 1 | Heuristic roots have no aspect | By design. Wiktionary gives aspect only for the 116 template-marked roots | Needs LIV² (already on the request list) |
| 2 | Root type decided from the first gloss; mixed senses (*h₂ed-* "to dry" + "grain") | Source: Wiktionary has both senses in one section | Logged. The disagreement list in `build_report.json` covers the type call |
| 5 | Derivatives lack accents (*pedom*) | Source: tree lines often omit the accent | By design (the form is kept as given). The validator should accept unaccented variants |
| 6 | Root reflexes aren't aggregated from derivatives | By design: reflexes belong to a lexeme | The Phase 3b checker will walk derivatives |
| 8 | Mixed ablaut grades under one lemma | Source: the `~` stems | Kept as `stems` |
| 10 | `-2` ids | Not duplicates. The slug drops accents and hyphens, so a *different* form already holds the plain id: `pie-lex-eti` is the suffix *-eti*, `pie-lex-yemHos` is *yemHós*, `pie-lex-h3moygjhos` is unaccented *h₃moyǵʰos*. Each `-2` form occurs once in the lexicon. | No action |
| 11 | *h₃sleydʰ-* optional segment? | The Wiktionary headword is `h₃sleydʰ-`, with no parentheses | Correct as parsed |
| 12 | *h₂oǵn̥yo-* lacks `segmented` | The tree line has no internal hyphens, so there is nothing to segment | Correct as parsed |

**School differences** (the reviewer kept these apart; not errors): h₁reh₁p-, dem-, h₂sews-, bʰeh₂g-, weh₁y-, peyh₂-.
