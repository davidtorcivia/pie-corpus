# Lexicon gaps, round 6: the wave 5–6 planners' list (t095–t109) and four lexicon fixes (2026-11-01)

The concept list is docs/NEXT.md "Vocabulary round 6": the gaps the t095–t109 planners reported, four lexicon fixes, a check of lexq's word search, and the sólh₂wos description.

I used round 5's method (`lexicon-gaps-round5-2026-10-31.md`) and round 3's ladder (`lexicon-gaps-round3-2026-10-31.md`), and stopped at the first rung that held:

1. An existing entry, fixed in `overrides.jsonl` (gloss, form, pos, gender or a hand-checked spec), then the lexicon is rebuilt.
2. A project reconstruction: one formation in at least 2 branches, flagged as such.
3. Otherwise an idiom or a stated paraphrase in `data/lexicon/idioms.json`.

Archaic first, and no Tier 3b neologisms this round: the model is a human PIE speaker. Nothing was coined.

Sources, read in `raw/books/text/`: M&A = Mallory & Adams 2006 (chapters and the appendix 3 English–PIE word list), LIV², Kroonen 2013, Derksen 2008 (Slavic) and 2015 (Baltic), Matasović 2009, de Vaan 2008, EWAia, NIL 2008, Fortson 2010 and Ringe 2006. Every override `note` and idiom `source` names its source and locator. No book text is quoted.

**Counts.** Rung 1: 16 lexemes (15 new override rows, 1 row edited) and 2 valency notes. Rung 2: none (4 candidates rejected, below). Rung 3: 36 new idiom entries (13 idioms, 23 paraphrases) and 6 rewritten. idioms.json grows from 87 to 123 entries.

## The four lexicon fixes

### 1. lexq offered ids the engine rejects (t096: sleh2gwt, gjhlh2dhros)

lexq's search never printed either id. It prints `pie-lex-sleh2gwt-2` (the aorist sléh₂gʷt, 224 corpus uses) and `pie-lex-ghlh2dhros` (gʰl̥h₂dʰrós), and so does t096's own slice (`data/generation/slices/t096.json` lists `pie-lex-sleh2gwt-2`, never the bare id). The planner typed ids from forms and checked them with `lexq --id`:
- **`--id pie-lex-sleh2gwt`** (the bare stem sleh₂gʷt, rule `unknown:noun-shape`) printed an entry with `"cells": {}`, as if usable. check_plan then rejected it ("no usable spec").
- **`--id pie-lex-gjhlh2dhros`** (ǵʰ typed for gʰ) printed only "not an inflectable lexeme (closed ids …)", which reads like a closed-class problem.

**Fix (scripts/lexq.py, a planner-tool change, not the engine).** `lookup_id` prints an offered word in full, as before. Anything else gets an error line with the id to use:
- `{"error": "not a planner word: no usable spec (rule unknown:noun-shape)", "use": ["pie-lex-sleh2gwt-2"]}`
- `{"error": "unknown id", "use": ["pie-lex-ghlh2dhros"]}`

The suggestion matches offered ids on an id skeleton: no accents, no j/x diacritic letters, no -N suffix.

### 2. tl̥h₂tóm 'bridge' rests on one branch

- **For the link.** Derksen 2015 s.v. tìltas (Lith. tìltas, Latv. tilts 'bridge'; *tl̥h₂-tó-m; Skt tīrthá- 'passage, ford'; `derksen-baltic/p0480.txt`).
- **Against it.** EWAia I s.v. tīrthá- derives the Sanskrit word from TAR (*terh₂- 'cross') and rejects the link to Lith. tìltas (`ewaia-v1/p0705.txt`).
- **Decision.** 'Bridge' is Baltic only, so the word is marked, not dropped.
  - The gloss is now `["bridge"]`: 'ford' leaves it (pérwr̥ and pértus cover it).
  - The caveat is in the override note and in a new 'bridge' idiom, which lexq prints right after the word. A gloss sense "Baltic only" was tried and dropped: the translator's lexmap reads every sense as an English word.
  - The first sense is unchanged, so the 5 corpus records (t041, t050, t070, t088, t103) keep their gloss lines.
- **New 'bridge' idiom.** It points to pértus 'crossing' (M&A §15.7: Gaul. ritu- 'ford', NE ford, Av. pərətu- 'ford, bridge') and pérwr̥ 'ford'.

### 3. woǵʰéyeti 'causative only'

- **The note.** A `data/generation/verb_valency.json` entry: `"valency": "tr"`, gloss "to make (someone) convey, have (something) carried: causative only; plain 'bring' is wédʰeti or bʰéreti".
- **Where it shows.** slice_item and lexq show this gloss in place of the lexicon's.
- **Effect.** `tr` makes check_plan require an OBJ in the active.
- **Corpus.** woǵʰéyeti has no corpus use (it was only in t045's and t101's initial plans), so nothing changes.

### 4. gʷr̥Htós 'welcome': the in-world brief against idioms.json

The in-world brief (`planner-brief-dialogue-inworld.md`, the lead's rule since 88fd509) says welcome is "be dear to us" or VOC gʰóstis + MOD priHós, never gʷr̥Htós. Two lower-authority files contradicted it: the thanks idiom ("call the gift welcome (gʷr̥Htós)") and the lexicon gloss "praised, welcome". I aligned both to the brief:
- **Override.** The gʷr̥Htós gloss is now `["praised", "pleasing; grateful, thankful"]`. The first sense, and so the gloss lines, is unchanged.
- **Thanks idiom.** It is "praise the giver (gʷr̥néHti)" only.
- **New 'welcome' idiom.** It gives the brief's two constructions, both checked:
  - príHe gʰóstey 'dear guest!';
  - túH n̥sméy priHós 'you are dear to us'.
- **Test.** It checks that no idiom offers gʷr̥Htós for 'welcome'.

**For the lead.** de Vaan 2008 s.v. grātus (`devaan-latin/p0285.txt`) lists Skt gūrtá- 'welcome' and Lat. grātus 'pleasant' under *gʷr̥H-to-. That is two branches for the adjective sense 'welcome (gladly received)'. The bar could be relaxed for the adjective, as distinct from a greeting formula. I did not relax it.

## The word-search check: judge, oath, swear, witness, every/each

What lexq returns now:

| query | words | idiom |
|---|---|---|
| judge | — | 'point out the right' (déyḱeti + neuter h₃reǵtós; now also h₂yéwos 'law') |
| oath | bʰoydʰéh₂ 'pledge, oath', h₁óytos 'oath', h₃m̥néh₃ti 'swear (an oath)' | — |
| swear | bʰoydʰéh₂, h₃m̥néh₃ti | — |
| witness | — | 'the man who saw' |
| every | solh₂wós 'whole, entire; all, every' | the every/all/each entry |
| each | — | the same entry |
| law | **h₂yéwos** (new), dʰéh₁mn̥ (new sense), then the in-law words | — |

- **What t098 actually missed.** lexq is consistent: 'judge' and 'witness' have only idioms (round 5), and 'oath' has three words. t098's own lookup log (scratch `t098_lookup.txt`) shows the batch used h₁óytos and h₃m̥néh₃ti. So t098 missed the *idioms* for judge and witness, and t102 found them. The ranking was not the cause.
- **Real defects found and fixed:**
  - **The every/each idiom was stale.** It said "solh₂wós has a NOUN spec: it cannot be a MOD", false since 994f7fc. That is what misled the t109 planner: the briefs never mention sólh₂wos. Rewritten, with checked plans:
    - MOD 'every man' = solh₂wós wiHrós;
    - 'all the cows' = solh₂wā́s gʷṓs;
    - a noun with a gender, 'all came' = solh₂wṓs gʷmént;
    - 'each' = 'every' (SG) or the repeated noun.
  - **'law' returned only the in-law words.** lexq's `words()` splits "brother-in-law". There was no 'law' lexeme, and now there is (h₂yéwos, below), so it ranks first.
  - **A plural in a gloss hid the word.** 'ash' missed kónHis 'ashes, dust' (t100). lexq now matches a query against the singular of each gloss word (`gloss_words`: -s and -es dropped), so 'ash' finds kónHis first.
- **sólh₂wos in the brief and in lexq.** lexq shows family `adj`; the briefs do not mention the word; the idiom is fixed. Still open: the lexicon's oxytone solh₂wós against M&A *sólwos and Skt sárva- (96 corpus uses), below.

## Result: words (rung 1)

| concept | lex_id | form | gloss now | evidence | note |
|---|---|---|---|---|---|
| mare | pie-lex-h1ekjweh2 | h₁éḱweh₂ f. | mare | NIL p. 230 (Ved. áśvā-, Av. aspā-, Lat. equa, Lith. ašvà); M&A §9.2 (four groups) | NIL_ADMIT; the entry was usable but NIL-held |
| soon | pie-lex-mokjs | **móḱs** | quickly; early; **soon** | de Vaan s.v. mox 'soon' (OIr. mo, MW moch, Av. mošu 'soon', Skt makṣú); EWAia II s.v. makṣú | form change, below |
| law | pie-lex-h2yewos | h₂yéwos n. | law, right; ritual norm | M&A §17.4 *yew(e)s- 'law, ritual norm' (Italic–Indo-Iranian); de Vaan s.v. iūs (OLat. ious, Skt yós, OAv. yaoš) | had reflexes and a spec, no gloss |
| law | pie-lex-dheh1mn | dʰéh₁mn̥ n. | (2nd sense) law, ordinance | M&A §17.4 (Gk θέμις, Skt dhā́man- 'law') | duplicated 3rd sense removed |
| enough | pie-lex-seh2tis | séh₂tis f. | satiety, sufficiency; enough | Matasović s.v. *sāti- (OIr. sáith, Lat. satis, Lith. sótis; ablaut *seh₂ti-/*sh₂tey-) | spec as Matasović's paradigm |
| oar | pie-lex-h1erh1trom | h₁érh₁trom n. | oar, paddle | M&A §15.6 (Lith. írklas, Skt arítra-) | had no gloss |
| bake | pie-lex-pekweti | pékʷeti | (3rd sense) to bake | Derksen 2008 s.v. *peťi 'bake' (OCS pešti, Lith. kèpti) | |
| bark | pie-lex-leh2yeti | léh₂yeti | to bark | Derksen 2015 s.v. lóti (Lith. lója, OCS lajati, Skt rā́yati) | ye-present in 3 branches |
| graze, pasture | pie-lex-peh2skjeti | peh₂sḱéti | to pasture, feed (cattle); MID to graze | de Vaan s.v. pāscō; Toch. pāsk- | valency tr |
| clay, potter | pie-lex-dheygjhti | dʰéyǵʰti | to knead, shape (clay); to smear | LIV² *dʰei̯ǵʰ- (Go. digan 'make pottery', Lith. žiesti, Lat. fingō, figulus) | |
| behind | pie-lex-posti | pósti adv. | (2nd sense) behind, in the rear | de Vaan s.v. post 'in the rear, behind, after' | |
| paternal grandfather | pie-lex-h2ewh2os | h₂éwh₂os m. | (3rd sense) grandfather (on either side) | M&A §12.3 (Hitt. ḫuḫḫas, Lat. avus, ON afi, Arm. haw) | 'maternal' is Wiktionary's |
| loud | pie-lex-klh1ros | kl̥h₁rós adj. | loud, sonorous | de Vaan s.v. clārus [adj. o/a] | pos noun → adj; Latin only |
| can | pie-lex-memoghe | memógʰe | (2nd sense) can, may | M&A appendix 3 'able' *magʰ- (Go. mag, OCS mogǫ) | |
| bridge | pie-lex-tlh2tom | tl̥h₂tóm n. | bridge | fix 2 | caveat in the idiom |
| welcome | pie-lex-gwrHtos | gʷr̥Htós | praised; pleasing; grateful | fix 4 | 'welcome' removed |
| bring | pie-lex-wogjheyeti | woǵʰéyeti | (valency note) causative only | fix 3 | verb_valency.json |

**Rules for the glosses.**
- Every added sense goes after the first, so no corpus gloss line moves.
- Every added sense is within the three senses that `Lexicon.meaning` (slices, lexq) shows, which is why dʰéh₁mn̥'s duplicate third sense was removed.
- All the words above are offered by `make_slice.offered()` without a TIER3B_INHERITED entry. The mare needed only NIL_ADMIT.

**móḱs.** The lexicon wrote the monosyllable without an accent mark. The validator's lint reported it as an accent defect (`accentless`), and the t099 and t100 planners removed it. An orthotonic monosyllable carries the accent on its one vowel and is written with it, like tód, kʷíd and préy, so the form is now móḱs. The old spelling stays a variant. This is the one change that alters approved PIE (below).
- **The records not yet re-realized still validate.** The old spelling is a variant, indexed at the exact tier: a t037 sentence with moḱs gives tiers `{"exact": …}` and no `legacy`, so the all_exact gate still passes. The only effect is the lint line it already had (`accentless: ["moḱs"]`).
- **Alternative for the lead:** leave the form and exempt it from the lint (an ACCENTLESS_LEXEMES entry). That changes no corpus record but leaves the notation inconsistent.

**Rung 2 candidates, all rejected:**

| word | sense | why rejected |
|---|---|---|
| *h₂eh₁peros | shore | Kroonen s.v. *ōf(e)ra- (OE ōfer, G Ufer < *h₂eh₁p-er-o-) against Gk ἤπειρος < *h₂eh₁per-io-: two formations, "a potential isogloss"; M&A marks it '?' |
| *ph₂tr̥wyós | father's brother | de Vaan s.v. pater: *ph₂tr-uio- is Indo-Iranian only (Skt pitṛvya-, YAv. tūiriia-); Lat. patruus, Gk πάτρως and OHG fetiro are other formations |
| h₂riHmom / *h₂reh₁- | count, number | the noun has no accent in any source; LIV² *(h₂)reh₁- 'reckon' is Lat. reor only |
| séǵʰtōr | victor, winner | held by the NIL re-review R7 (wrong oblique stem); not reopened |

## Numerals 11–99: what the handbooks reconstruct

- **Teens.** The unit + 'ten', juxtaposed: *dwóh₁ déḱm̥ 'twelve' (Lat. duodecim, Av. dvadasa, Skt dvā́daśa), 'fifteen' Lat. quīndecim, Skt pañcadaśa (M&A §19.1). Homeric δυοκαίδεκα is 'two and ten'.
- **Decads.** They are inflected forms of 'ten' (Ringe 2006 p. 53, `ringe/p0065.txt`; Fortson §7.17; M&A §19.1):
  - **20:** *wī́ḱm̥tih₁ < **dwi-dḱm̥t-ih₁ 'two tens', a neuter dual;
  - **30–90:** an archaic neuter collective in *-dḱṓmd (Ringe), *trīḱomt(h₂) (M&A);
  - Ringe: higher numerals cannot be securely reconstructed.
- **In the engine.** The lexicon's decad entries (wídḱm̥ti, tridḱómth₂ … ninety) have rule `indeclinable` and no engine shape. Their finals differ from Ringe's, so I added no closed-class decads.
- **Two idioms instead**, both checked, with no engine change. They reproduce the handbooks' analysis with the existing noun déḱm̥t 'decad' (n.):
  - **'Two/three tens'.** The numeral is a MOD on déḱm̥t, and the counted noun is a POSS in the genitive plural:
    - 20 = dwóyh₁ h₁éḱwōm déḱm̥tih₁ (the neuter dual, as *dwi-dḱm̥t-ih₁);
    - 30 = tríh₂ h₁éḱwōm déḱm̥th₂ (the neuter plural collective);
    - 50 = pénkʷe h₁éḱwōm déḱm̥th₂;
    - 21–99 add the unit with "and": dwóyh₁ h₁éḱwōm déḱm̥tih₁ pénkʷe-kʷe 'twenty-five horses'.
    - As a subject, the neuter plural takes a singular verb (… déḱm̥th₂ sésti).
  - **Teens.** 'Ten X and two': déḱm̥ h₁éḱwons dwóh₁-kʷe.
    - Two numeral MODs on one noun do not work: 'two' makes the noun dual, and 'ten' before 'two' fails ("form not generated"). The idiom says so.
    - Engine follow-up (not done): `slot_number` takes the first numeral MOD.

## Result: idioms and paraphrases

`data/lexicon/idioms.json`: 87 → 123 entries (64 idioms, 59 paraphrases).
- **New:** 36 entries, 13 idioms and 23 paraphrases.
- **Rewritten:** 6 entries: thanks, every/each, soon (móḱs), bread (bake), judge (h₂yéwos) and the describe-it entry (shore moved out). The well/slowly entry's móḱs mention is updated too.

**Checks.**
- Every round-6 id is a planner word: offered, a slice adverb or a closed id. None is a coinage (`test_round6_idiom_ids_are_planner_words`).
- Every PIE form a round-6 `how` gives was realized through check_plan and realize with no warning (`test_round6_idiom_plans`, 35 plans).

**New idioms (an inherited way of saying it):**
- **Welcome.** VOC gʰóstis + priHós, or 'you are dear to us' (fix 4).
- **Bridge.** tl̥h₂tóm (Baltic), or pértus / pérwr̥.
- **Numbers.** The teens and the decads (above).
- **can.** memógʰh₂e 'I can', or the optative (tód bʰéroyh₁m̥ 'I could carry it').
- **enough.** séh₂tis + GEN: dʰoHnéh₂s séh₂tis h₁ésti 'there is enough grain' (Lat. satis frūmentī).
- **sick, sickness.** 'Sickness holds him': swérgʰos wiHróm séǵʰeti. swérgʰos is the project word, flagged.
- **kind / cruel.** The bahuvrihis h₁suménēs / dusménēs (Gk εὐμενής / δυσμενής).
- **potter, clay.** dʰiǵʰónts wiHrós 'the man who shapes', and dʰéǵʰōm dʰéyǵʰti.
- **full moon.** pl̥h₁néh₂ lówksneh₂.
- **paternal uncle / grandfather.** ph₂trés bʰréh₂tēr 'the father's brother'; h₂éwh₂os for either side.
- **faster.** The comparative in the neuter accusative: HéHḱyos tékʷet 'he ran faster'.
- **graze, calve.** gʷówes peh₂sḱóntor (MID), gʷṓs peh₂sḱéti; 'the cow bore a calf'.

**New paraphrases** (no defensible word; the `how` says what to write and the `source` why):
- **Grammar words.**
  - count: 'see how many', with kʷóti.
  - must: the 3rd-person imperative h₁éytu, or the subjunctive (Fortson §5.56).
  - hope: the optative of wish, gʷm̥yéh₁t 'may he come'.
  - last: loykʷós 'remaining', or 'after all the others'.
- **Healing and song.**
  - healer and nurse: participles, mḗdonts wiHrós and dʰéh₁yontih₂ gʷḗn.
  - charm.
  - singer, poet and verse: gʷéHyonts wiHrós; wékʷos, kéh₂nmn̥.
- **Contests.**
  - coward and winner: trésonts wiHrós, séǵʰonts wiHrós.
  - wrestle, game, race, wager, cheat, mock and blame, by their verbs.
- **River and land.**
  - shore, bank and island: LOC déh₂nu; 'land in the water'.
  - flood.
  - mud: h₁werséh₂ dʰéǵʰōm 'wet earth'.
- **House and crafts.**
  - thatch: stégos gʰr̥h₁ménh₁ stégeti.
  - beam, ladder and camp.
  - axe, adze and sickle: ḱéstrom.
  - leather and shoe: skéwHtis.
  - mend and crack.
- **Fields and food.**
  - thresh, winnow, chaff and sheaf.
  - golden and arm-ring: POSS h₂éh₂usom.
  - to salt: dʰéh₁t + sḗh₂l.
  - stir, spoon, ladle and bowl: miḱsḱéti; péh₃tlom, kʷéros.
- **Manner and people.**
  - stingy, exactly and loudly/shout: h₃reǵtóm mléwHti, kl̥h₁róm mléwHti.
  - beat: kélh₂t.
  - journey: h₁éyti + póntoh₁s.

**Already covered, so not re-added:**
- second: h₂énteros 'second, other'.
- sickness: swérgʰos.
- bowl/cup: péh₃tlom.
- remaining: loykʷós.
- left: sewyós.
- slowly/well: the manner-adverb idiom.
- until: the existing paraphrase.
- wound, fever, medicine, shame, sword, hall, hammer, needle, reins, grave, drown and cheese: round 5's entries.

## Corpus records: the dry re-realization of every approved batch

**Method.**
- **Batches.** The 90 approved batches: every release record with review `approved`, without t3b-001.
- **How they were run.** With `scripts/realize_plans.py`'s own `main()` into a scratch ROOT, as in `rerealize-2026-10-31.md`. Each batch used its plan file and the `model`, `prompt_id` and `engine_version` of its records' `generator`. The run was in parallel workers.
- **Baseline.** The same run before any change gave 0 rejects and 0 PIE changes in all 90 batches, and no gloss-line change in the 72 batches whose full results were kept (the first 18 came from a serial run stopped for speed, which logged only reject and PIE-change counts). corpus/ was current.
- **Comparison.** After the changes, every record was compared with corpus/ field by field.
- **Nothing written.** No file in corpus/, batches/ or releases/ was written.

**Results.**
- **Rejects: 0 in all 90 batches.** Record counts and ids are unchanged.
- **PIE changes: only moḱs → móḱs.** 104 tokens in 97 records of 34 batches. The fields that differ are `pie`, `pie_ascii` and that token's `form`; no other field and no gloss line changes. Records per batch:

| batch | records | | batch | records | | batch | records |
|---|---|---|---|---|---|---|---|
| t035 | 7 | | t064 | 4 | | t097 | 2 |
| t036 | 2 | | t065 | 3 | | t102 | 1 |
| t037 | 10 | | t070 | 1 | | t103 | 2 |
| t039 | 4 | | t073 | 1 | | t106 | 4 |
| t041 | 3 | | t085 | 1 | | t108 | 3 |
| t042 | 3 | | t086 | 2 | | t109 | 7 |
| t044 | 3 | | t087 | 3 | | t3b-002 | 3 |
| t050 | 2 | | t089 | 4 | | t3b-003 | 1 |
| t053 | 1 | | t091 | 2 | | t3b-004 | 2 |
| t056 | 2 | | t094 | 3 | | t3b-006 | 1 |
| t059 | 3 | | t095 | 1 | | | |
| t062 | 4 | | t096 | 2 | | | |

The record ids are in `docs/audits/lexicon-gaps-round6-corpus-changes.json`. To take the change, re-realize those 34 batches with their own commands and rebind them; this is left to the lead. To refuse it, revert the `form` key of the pie-lex-mokjs override row, rebuild, and add the ACCENTLESS_LEXEMES exemption.

## What changed

- **`data/lexicon/overrides.jsonl`:** 15 new rows and the gʷr̥Htós row edited (meaning, note).
  - Rebuild: the build with the old overrides was first checked to reproduce the working tree (no diff). Then build_lexicon and classify_lexicon were run.
  - `inflection_specs.jsonl` changes in 2 rows: móḱs (form) and kl̥h₁rós (shape:thematic noun → shape:thematic-adj).
  - No displaced spec, so `alt-form-status.md` is unchanged.
- **`data/generation/verb_valency.json`:** woǵʰéyeti and peh₂sḱéti, both `tr`, each with its gloss.
- **`scripts/make_slice.py`:** NIL_ADMIT gains the mare.
- **`scripts/lexq.py`:**
  - `lookup_id`: the `--id` errors name the id to use;
  - `gloss_words`: a gloss's plural matches the query.
- **`data/lexicon/idioms.json`:** 87 → 123 entries.
- **`pie/translator/lexmap.py`:** 8 English keys: mare, law, oar, bake, bark (verb), pasture, knead and loud. 'graze' is left out: the translator would build an active with no object, which valency `tr` rejects.
- **Not changed:** the engine (`pie/`), the briefs, the plans.

## Tests

- **New: `tests/test_vocab_round6.py`** (47 tests). All plans go through `tests/helpers.produce`.
  - **The four fixes:** the lexq `--id` errors and their ids; tl̥h₂tóm's gloss; woǵʰéyeti causative + tr; no idiom offers gʷr̥Htós for 'welcome', and the brief's constructions realize.
  - **Search and words:** the word-search check; 'ash'; the mare; móḱs passing the validator's accent lint.
  - **Glosses and cells:** 10 concepts find their word first; the first senses (gloss lines) are unchanged; the new cells.
  - **Idioms:** every round-6 idiom id is a planner word; 35 idiom plans realize as their `how` says, with no warning.
- **New: `tests/test_translator.py::test_round6_words_reach_the_translator`.**
- **Full suite** (`UV_CACHE_DIR=/tmp/pie-uv-cache uv run --group translator python -I -m pytest -q -p no:cacheprovider`): **3991 passed, 5 skipped in 985.47s (0:16:25)** (pytest's own summary line, after the last rebuild).

## Left open

- **móḱs in corpus/:** 34 approved batches must be re-realized and rebound to carry it, or the form change reverted (above).
- **sólh₂wos accent:** the lexicon writes solh₂wós (oxytone); M&A *sólwos and Skt sárva- have root accent. It has 96 corpus uses, so not this round.
- **Engine follow-ups (report only):**
  - two numeral MODs on one noun ('twelve');
  - closed-class decads, once one handbook form is chosen;
  - lexq's `words()` splits hyphenated glosses ('law' still lists the in-law words after h₂yéwos).
- **Song theme cap (t105):** not touched.
- **Grammar items, not vocabulary:**
  - complement clauses after must/can;
  - a real ADV role for adjective case forms (the GOAL-slot idiom works; round 5 open item);
  - séǵʰtōr 'victor' (held, R7).
