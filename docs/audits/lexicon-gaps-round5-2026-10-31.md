# Lexicon gaps, round 5: the t073–t094 planners' list, 'other' and 'cattle' (2026-10-31)

The concept list is docs/NEXT.md "Vocabulary round 5": the gaps the t073, t079, t089 and t094 planners and the horror wave reported, plus round 3's open list. Two engine items came with it: h₂élyos 'other' was filed as a noun, and gʷṓws 'cattle' was masculine while the planners treated cows as feminine in some dialogues and masculine in others. The owner also asked for two idioms: 'with two hands' (no oblique dual) and 'teach me to X' (no infinitive).

I used round 3's ladder (`lexicon-gaps-round3-2026-10-31.md`) and stopped at the first rung that held:

1. An existing entry, fixed in `overrides.jsonl` (gloss, form, pos, gender or a hand-checked spec), then the lexicon is rebuilt.
2. A project reconstruction: one formation in at least 2 branches.
3. A Tier 3b neologism.

Archaic comes first. Where no word holds, the concept gets an **idiom** or a stated **paraphrase** in `data/lexicon/idioms.json`. This round needed no rung 2 and no rung 3: nothing was coined.

Sources, read in `raw/books/text/`: M&A = Mallory & Adams 2006, LIV², Kroonen 2013, Derksen 2008/2015, Matasović 2009, de Vaan 2008, Beekes 2010, EWAia, West 2007, Fortson 2010, Ringe 2006, and the Handbook of Comparative and Historical IE Linguistics (Klein, Joseph & Fritz 2017). Every override `note` and idiom `source` names its source and locator. No book text is quoted.

## The two engine items

### h₂élyos 'other': a pronominal adjective

pie-lex-h2elyos had pos `det` and a masculine thematic NOUN spec, so 'another girl' could not be said (t090). It is an adjective in every branch: Lat. alius, Gk ἄλλος, Goth. aljis, OIr. aile, Arm. ayl (M&A §19.2, `mallory-adams/028_part0027.txt`; de Vaan s.v. alius adj. o/a, n. aliud, `devaan-latin/p0048.txt`).

- **Engine.** `AdjSpec` gets a `pronominal` flag in `pie/morph.py`. When set, `decline_adj` makes the neuter NOM/VOC/ACC.SG end in *-od*, like *tód* and *kʷód*. The flag works on thematic adjectives only.
  - **Why only the neuter.** Ringe 2006 p. 55 (`ringe/p0066.txt`) reconstructs neuter *h₂élyod as secure, from Lat. aliud and Gk ἄλλο. He leaves the scope of the rest of the pronominal inflection open. So the *-sm-*/*-sy-* obliques and NOM.PL *-oy* are not built, and every other cell is the ordinary o/eh₂ adjective (f. h₂élyeh₂).
  - **Storage.** `spec_dict` (pie/morph.py), shared by `classify_lexicon.py` and `pie.neologism`, writes the flag only when it is set, so no other spec row changed.
  - **Size.** The change is 21 lines, and `tests/test_vocab_round5.py` tests it.
- **Override.** `pos: "adj"`, `spec: {"pronominal": true}`. The displaced non-pronominal spec stays indexed with status `rejected` (its h₂élyom).
- **Results.** Cells are m. h₂élyos, f. h₂élyeh₂, n. **h₂élyod**. Masculine uses come out exactly as before.
- **Consequence for corpus/.** check_plan rejects an adjective used as a noun without a `gender` ("needs a gender … for whom it names"). This is the same rule as for sólh₂wos. **49 slots in 34 corpus records** use h₂élyos as a noun with no gender ('the other', 'another said'). They are rejects until the plan sets a gender (list below).

### gʷṓws 'cattle': stays masculine; a cow is the slot gender f (feminine default reverted)

- **Tried, then reverted (lead decision).** First, gʷṓws was made feminine by default with an entry override `"gender": "f"`.
  - **Evidence for it.** EWAia I s.v. gáv- m. f. 'cattle, bull, cow' (`ewaia-v1/p0533.txt`). Beekes s.v. βοῦς [f., m.] 'cow, bull, ox' (`beekes-edg/p0140.txt`).
  - **What the scan showed.** The noun's own forms do not change, but 60 records changed their agreement (dwóh₁ → dwóyh₁, tréyes → tísres, swóns → swā́s …). 4 oxen and bulls came out feminine. 21 records became mixed: feminine agreement beside the masculine pronouns their planners wrote. 73 more began to warn.
  - **Why reverted.** The word is of **common gender** in the daughters, and most corpus plans treat cattle as masculine. The flip turned self-consistent records into mixed ones across 41 batches. The override is removed, and the gʷṓws row's note records the trial.
- **What holds instead.**
  - **Engine gender m**, unchanged.
  - **Brief rule 10:** "a cow as a female animal: gender f on the slot and on its pronouns; bull/ox is uksḗn or gender m".
  - **Cow idiom:** gʷṓws with the slot gender f.
  - **New 'bull, ox' idiom:** uksḗn (M&A §9.2 *uk(ʷ)sēn- 'ox', the male as against the three 'cow' words; `mallory-adams/018_part0017.txt`).
- **New warning, `_common_gender_warnings` in pie/realize.py** (list `COMMON_GENDER`, so far only gʷṓws).
  - **When it fires:** a 3rd-person pronoun on its own takes up an ungendered gʷṓws slot of its number in its clause or the two before, with a different gender. The typical case is tā́s 'them (f)' for cows whose slot has no gender, so their MODs come out masculine.
  - **What it says:** set `"gender"` on that slot too (it names the clause and slot), or make the pronoun masculine.
  - **Test:** `test_pronoun_of_another_gender_for_ungendered_cattle_warns`.
  - **Scope:** this is the t042 false warning in NEXT.md. The generic "matches no referent" warning still fires there; the new one says which slot to fix.

## Result: words (rungs 1–3)

| concept | rung | lex_id | form | gloss now | evidence | rejected, and why |
|---|---|---|---|---|---|---|
| other | 1 (pos; pronominal spec) | pie-lex-h2elyos | h₂élyos adj. | other, another | above | — |
| cow, cattle | no change (gender f tried, reverted) | pie-lex-gwoxws | gʷṓws m. (common gender) | cattle; cow, ox, bull | above | the feminine default (above) |
| face | 1 (form, pos, gender: stem → n. o-stem) | pie-lex-h1enih3kwo | h₁énih₃kʷom n. | face | M&A §11.1 *h₁éni-h₃kʷ-o- (OIr. enech, Gk ἐνωπή, Av. ainika-, Skt ánīka-); EWAia s.v. ánīka- n.; Matasović s.v. *enekʷo- n. Neuter o-stem in Indic and Celtic; root accent as in Skt ánīka- | h₂entíos (an adjective, 'front'); *próti-h₃kʷ-o- (no entry) |
| holy, sacred | 1 (pos: noun → adj; gloss) | pie-lex-sh2kros | sh₂krós adj. | sacred, holy, consecrated | de Vaan s.v. sacer (OLat. sakros, Osc.-Umb. sakro-; Hitt. šaklai- 'rite' from the root); M&A §23.2. Italic formation. The oxytone is the headword's; no handbook prints one | ḱwentos (Balto-Slavic, Av. spəṇta-: unaccented) |
| holy (Greek sense) | 1 (gloss, appended) | pie-lex-ish1ros | ish₁rós | strong, vigorous; holy, hallowed (Greek) | M&A §11.7 (Gk ἱερός, Skt iṣirá-) | — |
| age | 1 (gloss, appended) | pie-lex-h2oyu | h₂óyu n. | long time, lifetime; age (span of life) | de Vaan s.v. aevum; M&A §11.7 *h₂óyus | sh₂éytlom ('lifetime' only) |
| generation | 1 (gloss, appended) | pie-lex-gjenh1eseh2 | ǵenh₁eséh₂ f. | lineage, offspring; generation (of men) | the entry's Gk γενεά; Greek-only formation, and the sense is not checked in the handbooks read | ǵénh₁os ('race', not 'generation') |
| pray | 1 (gloss, appended) | pie-lex-gwhedhyeti | gʷʰédʰyeti | to keep requesting; to pray (for), plead | Matasović s.v. *gʷed-yo- (OIr. guidid, Gaul. uediiumi); YAv. jaiδiiemi, OPers. jadiyāmiy | *h₁ewgʷʰ- MID (no usable verb) |
| host | 1 (gloss) | pie-lex-ghostipotis | gʰóstipotis | lord, master; host (master of the guests) | de Vaan s.v. hospes (OCS gospodь) | gʰóstis ('guest, stranger') |
| anvil (hammer) | 1 (gloss, appended) | pie-lex-h2ekjmox | h₂éḱmō | stone; heaven?; anvil | Beekes s.v. ἄκμων 'anvil'; M&A §8.1; Kroonen s.v. *hamara- (ON hamarr 'hammer; crag') | no PIE 'anvil'/'hammer' |
| bellows, bag | 1 (form accent, pos, gender, hand-checked spec) | pie-lex-bholgjhis | bʰólǵʰis m. | (skin) bag, sack; bellows | M&A §14.1 *bʰólǵʰis (OIr. bolg, Gaul. bulga); Kroonen s.v. *balgi- (ON belgr, OE belig 'bellows'). Acrostatic i-stem with the o-grade kept: no source prints the obliques | bʰolǵʰis- (Indo-Iranian -is-) |
| axle | 1 (form, pos, gender, hand-checked spec) | pie-lex-h2ekjs | h₂éḱsis m. | axle, axis | de Vaan s.v. axis (m. i); Derksen s.v. ašìs, PSl. *osь. The i-stem is Italic and Balto-Slavic. The accent is a choice: the root, as in Ved. ákṣa- and Gk ἄξων (other stems) | thematic *h₂éḱsos (Skt only) |
| roast | 1 (gloss) | pie-lex-bhrgjyeti | bʰr̥ǵyéti | to roast, parch, fry | LIV² *bʰerǵ- (Ved. bhṛjjáti); M&A §16.2 (Lat. frīgō, Gk φρύγω) | pékʷeti stays 'cook' |
| offer, sacrifice, worship | 1 (gloss) | pie-lex-h1yagjeti | h₁yáǵeti | to worship (a god); to sacrifice, offer | LIV² *Hi̯aǵ- (Ved. yájati, YAv. yazaite; Gk ἅζομαι) | — |
| howl, roar | 1 (gloss, appended) | pie-lex-HrewdHti | HréwdHti | … ; to howl, roar, bellow (of animals) | de Vaan s.v. rudō | waylos (unaccented) |
| month | 1 (pos, gender, hand-checked spec) | pie-lex-mexh1ns | mḗh₁n̥s m. | month; moon | Beekes s.v. μήν (oblique *meh₁ns-: Lat. mēnsis, Skt mā́s-); M&A §8.4. **Round 3 was wrong that there is no entry**: there is one, with 21 reflex groups, but it had no engine shape | *méh₁nōt (Gmc, Baltic: another stem) |
| slow | 1 (form, pos, hand-checked u-adjective spec) | pie-lex-gwerdus | gʷr̥dús adj. | slow, sluggish; heavy; dull | Derksen (Baltic) s.v. gurdùs, *gʷr̥d-u-; Gk βραδύς; de Vaan s.v. gurdus. Spec on the dʰr̥sús pattern | the noun spec (f. gʷérdus) |
| right (south) | 1 (gloss order) | pie-lex-dekjsiwos | deḱsiwós adj. | right, on the right hand; what is proper | M&A §18.3, §18.7 (Gk δεξιός, Umbr. desua, Gmc *tehswô) | — |
| tears, help, wait, still, quickly, summer | already covered | dáḱru, h₁éwHt, méneti, éti, moḱs, sémeh₂ | — | lexq finds them ('tears' after the lexq fix below). moḱs being "unaccented" is lint noise: it is a monosyllable | — |

**Rung 2 candidates, all rejected:**

| word | sense | why rejected |
|---|---|---|
| weh₂tis | seer | no source prints the accent |
| *h₂éygʷʰos | shame | Greek only; the Gothic word is another formation |
| *wr̥nós | wound | the branches build different formations |
| ǵenh₁tḗr | ancestor | NIL single-branch, so it stays held |

## Result: idioms and paraphrases

`data/lexicon/idioms.json` grows from 54 to 87 entries: 51 idioms and 36 paraphrases.

| change | entries |
|---|---|
| New | 34: 20 idioms and 14 paraphrases |
| Rewritten | 4: herald, rich/poor, hunter, storm |
| Trimmed | 1: 'describe it' loses spindle, deer and stag |
| Deleted | 1: month is now a word |
| Changed | 1: cow |

Every id in a round-5 entry is a word a Tier 3 planner may use (`test_round5_idioms`), and none is a coinage. Every plan in a `how` was run through check_plan and realize, with no error and no warning.

**The owner's two:**
- **With two hands (no oblique dual).** The oblique takes the plural with no numeral. 'He carries it with two hands' = ǵʰesr̥bʰís bʰéreti.
  - The other cases of the dual cannot be reconstructed (Fortson §6.13, `fortson/016_9781405188968_006.txt`). Ringe 2006 p. 47 leaves them out of his paradigms (`ringe/p0058.txt`).
  - The `how` says `num: "PL"`. `"DU"` falls back to the plural silently (NEXT's silent-substitution item), and a dwóh₁ MOD in an oblique is rejected.
  - 'With two cows' takes the same route.
- **Teach me to X (no infinitive).** Two ways, both checked:
  - **(1) A dative -tu- verbal noun, where one is offered.** pértus 'crossing', gʷémtus 'coming', ǵéwstus 'tasting' and stéh₂tus 'standing' are. 'Teach me to cross' = pr̥téwey me ḱHsdʰí. Daughter infinitives are frozen case forms of verbal nouns, of uncertain PIE date (Fortson §5.58: Ved. pā́tave 'for drinking').
  - **(2) Parataxis.** The imperative of ḱéHst with me, then the verb in the 1st-person subjunctive: ḱHsdʰí me snéh₂oh₂ 'teach me: I shall swim'.

**Other new idioms:**
- **Cattle**
  - bull/ox: uksḗn, or gʷṓws with gender m.
- **Body and health**
  - herb: gʰréh₁mn̥, with the participle of mḗdeti for 'healing herb'.
  - medicine: the verb mḗdeti.
  - fever: 'heat burns him', from Hitt. tapašša- and Alb. ethe.
- **People and the gods**
  - ancestor: 'the fathers', ph₂tḗr in the plural (West ch. 10).
  - mercy: the bahuvrihi h₁su + ménos, as in Gk εὐμενής and Skt sumánas-.
  - judge: déyḱeti + neuter h₃reǵtós, 'point out the right' (Lat. iūdex).
  - serve: sékʷetor MID.
  - offer to the gods: déh₃t + IO, ǵʰéwt for a libation, h₁yáǵeti for the rite.
  - pyre: two clauses with kʷéyt + dóru, then 'burn the dead'.
- **Things and animals**
  - hammer: h₂éḱmō 'stone'.
  - bridle/reins: sh₂éymn̥.
  - dye: pinéḱti.
  - hall: méǵh₂s dṓm.
  - deer/stag: h₁ólḱis.
- **Words of manner and place**
  - well/slowly: the neuter accusative of the adjective in a GOAL slot with gender n, e.g. h₁wésu mléwHti 'he speaks well'. Sources: Fortson §7.23 and Handbook v3 §2.3.2.
  - west/north/south/east: orientation facing the sunrise. West = wékʷsperos, north = sewyós 'left', south = deḱsiwós 'right', east = h₂éwsteros (M&A §18.3, §18.7).
  - foreign land: h₂élyeh₂ dʰéǵʰōm, as in Gk ἀλλοδαπός and OE el-lende; or gʰóstis.

**New paraphrases**, each with its reason in the file:
- **Body and harm.** hair, wound (noun) and staff.
- **People.** seer, priest and witness.
- **Feeling and speech.** shame, and 'to mean'.
- **Things.** needle, spindle, cheese and flame.
- **Birds.** raven/crow and owl.

**Rewritten.**
- rich/poor: now the dative of possession, with a checked plan: polh₁ú h₃épnos wiHrṓy h₁ésti.
- herald: ḱn̥sónts wiHrós.
- hunter: wrégonts wiHrós.
- storm: adds gʰrómos 'thunder'.

## Corpus records: plans edited, and the scratch re-realization

**h₂élyos plans edited (lead's permission, h₂élyos only).** 49 slots in 34 records used h₂élyos as a noun with no gender. check_plan rejects that now, as it does for sólh₂wos. Each slot got `"gender": "m"` in `data/generation/plans/<batch>.jsonl`, and the diff is exactly those 49 keys. The gender comes from the referent: men, brothers, 'another man', the other bull.

| batch | slots | | batch | slots |
|---|---|---|---|---|
| pilot | 2 | | t076 | 1 |
| t004 | 11 | | t085 | 6 |
| t020 | 11 | | t086 | 1 |
| t021 | 5 | | t087 | 2 |
| t040 | 1 | | t088 | 1 |
| t050 | 1 | | t089 | 1 |
| t056 | 1 | | t090 | 3 |
| | | | t092 | 2 |

Three cases were checked by hand:
- **t050-0012** 'the others will follow': the cows, whose slot is ungendered, so m.
- **t090-0006** 'my heart yearns for another': the girl speaks of a man.
- **t090-0036** 'the others are asleep': the friend's companions.

The slot list is `docs/audits/lexicon-gaps-round5-h2elyos-slots.json`.

**Scratch re-realization of every approved batch.** All 76 approved batches (`pie.batch_release.batch_eligibility`, review approved) were realized under the new lexicon into a scratch ROOT. This used `scripts/realize_plans.py`'s own `main()` on each batch's plan file, with the records' model, prompt id and engine version. Nothing was written to corpus/, batches/ or releases/.

**Rejects per batch:**
- **75 batches: 0 rejects.**
  - b001–b004
  - t001–t021, t023, t024, t026–t045, t050, t053, t056, t059, t062, t064, t065, t070, t073, t076, t079, t084–t094
  - t3b-002–t3b-007
- **t3b-001: 20 rejects. This is not from this round.** Every plan fails the Tier 3b v2 rule "a Tier 3b sentence needs its own english on its first clause". NEXT.md already records that t3b-001 predates the v2 rules and cannot re-run until it is re-planned. No lexicon or engine change is involved, and I did not re-plan it.
- **PIE text:** no record of any approved batch changes its realized PIE, and the record counts are unchanged. The masculine gender reproduces the old noun cells, and gʷṓws stays m.

Per-batch numbers: `/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/rr/rerealize.json` (scratch). The old gʷṓws-flip lists in `docs/audits/lexicon-gaps-round5-corpus-changes.json` are kept only as the record of the reverted trial.

**Gloss lines only (PIE unchanged): 8 records.** deḱsiwós now glosses 'right', not 'what.is.proper':
- b003: 00027, 00099, 00100
- pilot: 00106
- t045: 00003, 00007, 00024, 00040

The Tier 1 file corpus/tier1/king-and-god.jsonl uses h₁yáǵeti, which had no gloss and now has one. Every other gloss fix appends a sense after the first, so its gloss line is unchanged.

## Remaining gaps, and why

- **Paraphrases only.** No PIE word or defensible single formation exists for these:
  - **Kept from round 3:** until, ago, lend, iron, sword/weapon, grave and bee.
  - **New:** hair, staff, wound (noun), seer, priest, witness, shame, 'to mean', needle, spindle, cheese, flame, raven and owl.
  - **Engine shape or accent missing:**
    - lightning *meldʰn-: a bare stem
    - deer h₁élh₁ēn: an n-stem with no oblique evidence
    - cheese dʰédʰh₁i: the i/n heteroclite
    - summer sm̥h₂eros: still no printed accent
    - 'flame' bʰl̥gmeh₂: unaccented
    - 'holy' ḱwentos: unaccented, though the better PIE word
- **Manner adverbs** use a GOAL slot with gender n. It realizes right, but the role name is odd. A real ADV role for adjective case forms would be cleaner.
- **'land, country'** has no gloss on dʰéǵʰōm, because no source read glosses it that way. lexq finds it only through the 'foreign land' idiom.
- **Not touched (out of scope):**
  - gʷṓws's oblique plurals on gʷéw- (NEXT, t035): changing them would change hundreds of records
  - the silent DU→PL fallback in obliques (NEXT)
  - kʷóteros as a pronominal adjective: only Skt katarád supports it

## What changed

- **`pie/realize.py`:** `_common_gender_warnings` (the gʷṓws pronoun warning), called from `plan_warnings`.
- **`pie/morph.py`:** `AdjSpec.pronominal`, applied in `decline_adj`, and `spec_dict`. The callers in `scripts/classify_lexicon.py` and `pie/neologism.py` now use `spec_dict`.
- **`data/lexicon/overrides.jsonl`:** 17 ids, plus a note on gʷṓws.
  - 14 new rows: h₂élyos and 13 of the words above.
  - 3 rows merged with the notes joined: ǵenh₁eséh₂, h₂éḱmō, HréwdHti.
  - 1 note edited: gʷṓws records the reverted trial (no gender field; it stays m).
  - Rebuild: the scratch-copy rebuild was first checked byte-identical to the working tree. Then build_lexicon and classify_lexicon were run.
  - `inflection_specs.jsonl` changes in 7 rows: h₂élyos, h₂éḱsis, mḗh₁n̥s, bʰólǵʰis, gʷr̥dús, h₁énih₃kʷom, sh₂krós.
- **`docs/audits/alt-form-status.md`:** three new displaced specs, all `rejected`: h₂élyos's non-pronominal neuter, and the zero-grade proterokinetic obliques the shape rule gave h₂éḱsis and bʰólǵʰis. The count is now 68 (the old header said 63 against 65 rows).
- **`data/morph/accent_unresolved.json`:** sh₂krós's 3 frozen noun vocatives are now 3 m + 3 f adjective vocatives (sh₂kre, sh₂kra …). The same laryngeal-nucleus exception applies. `test_representation_exceptions_are_frozen_vocatives` was updated from 129 to 132 cells, with the reason in its comment.
- **`data/lexicon/idioms.json`:** 54 → 87 entries.
- **Reachability**
  - `scripts/make_slice.py` TIER3B_INHERITED: 17 ids. All of them pass `offered()`.
  - `pie/translator/lexmap.py`: 37 English keys.
  - `pie/translator/transfer.py`: the determiner 'another' → an h₂élyos MOD. "Another girl sings" = h₂élyeh₂ dʰugh₂tḗr gʷéHyeti; "The great bull sleeps" = méǵh₂s uksḗn sésti.
- **`scripts/lexq.py`:** a plural query with no hit of its own is looked up in the singular ('tears' → dáḱru, h₂éḱru).
- **Docs:** `docs/morphology.md` (the pronominal flag) and `docs/generation/planner-brief-v4.md` rule 10 (a cow is gender f on the slot and its pronouns; 'other').

## Tests

- **New: `tests/test_vocab_round5.py`.** All plans go through `tests/helpers.produce`.
  - The pronominal cells, and `spec_dict`.
  - 'another girl', 'something else' (h₂élyod), and masculine uses unchanged.
  - The needs-a-gender reject.
  - Cattle stay m (albʰós gʷṓws); gender f gives albʰéh₂ gʷṓws.
  - The new warning: tā́s f for an ungendered gʷṓws slot warns and names the slot; f + f or m + m do not.
  - The lexq plural lookup.
  - Every round-5 idiom id is offered; the two-hands and teach-me plans realize.
  - 16 concepts find their lexeme first, with hand-checked cells.
- **New: `tests/test_translator.py` `test_round5_words_reach_the_translator`.**
- **Updated: `tests/test_accent_invariant.py`** (129 → 132, reason above).
- **Full suite** (`uv run --group translator python -I -m pytest -q -p no:cacheprovider`), after the revert and the plan edits: **1 failed, 3941 passed, 5 skipped in 894.00s**.
  - **The one failure is expected:** `test_batch_release.py::test_shipped_migration`. The release bindings hash the plan files, so the 14 approved batches whose plans gained h₂élyos genders report 'stale plans evidence': t004, t020, t021, t040, t050, t056, t076, t085, t086, t087, t088, t089, t090 and t092. The pilot batch is not approved.
  - **What clears it:** re-realize those batches (their PIE does not change) and rebind them, which writes releases/ (left to the lead). This is the same pattern as bd6a13d.
  - **Before the plan edits:** with the gʷṓws flip still in, the suite gave 3942 passed, 5 skipped.
