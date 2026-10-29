# Tier-3 review: packet t026 (28 items)

The batch is myth, hymn and prayer on Dawn, Sun and Sky: 40 texts, planned by claude-sonnet-5-5 (tier3-planner-v4). The packet has 28 items: 20 real, 5 planted and 3 Tier 1. It was built with `make_review_packet.py t026 --n 20 --plants 5 --tier1 3`. The reviewer worked from handbook knowledge (Fortson, Beekes, Ringe, LIV², Mallory–Adams). Doubtful forms were checked against a reverse index of every admissible `Lexicon.cells()` / `participle_cells()` form and against `closed_class.json`.

Order of work, as the brief requires:
1. The blind back-translation was done from the `pie` field alone. Only ids, genre and PIE were printed.
2. The English was opened after that, and every verdict was saved.
3. The verdicts file sha256 is `5c5dc5ac63c76c265505310a388221ae2a01184e4e9438f388594b3f81369e5c`.
4. Then came scoring and `resolve_review_items.py`. Nothing under `data/audits/` was read, and the packet was not diffed against the corpus.

## Counts

| | ok | minor | wrong |
|---|---|---|---|
| real (20), as judged | 14 | 3 | 3 |
| real (20), after fixes | 19 | 1 | 0 |

- **Plant recall: 5/5, blind.** All five plants were named before any record was opened: 955473e5, 6d59d4c1, e43c974e and eaaefffc were judged wrong, and 9e772845 minor. `score_review.py` counts 5 caught.
- **Real wrong rate: 3/20 before the fixes, 0/20 after.**
- **Tier 1:** 2 minor on notation, 1 ok, none wrong.
- **Calibration note:** dfc3d807 (Sky and Earth addressed with 2pl verbs and plural predicates) was graded minor. t024 graded the same pattern wrong (db70fa16), because the dual pronoun yú and the 2du cells exist. On that precedent the real wrong count before fixes is 4/20. It is fixed either way.

## Wrong: real (3), all fixed in `data/generation/plans/t026.jsonl`

- **4c72d046 (t3-t026-00005), gender.**
  - The error: `h₂yéwHō-kʷe h₁ést` predicates the masculine nom. sg. 'young' of feminine h₂éwsōs.
  - Cause: the PRED slot had no gender, and the engine defaulted it to m (engine gap 2).
  - Fix: `gender: f` on the slot, which gives h₂yuHénih₂.
  - Also fixed: ǵn̥h₃tā́m is 'did not know (each other)'. The English 'did not meet' was changed to match.
- **dd084638 (t3-t026-00010), number.**
  - The error: `méne h₃ókʷih₁ ne dedwiyḗr` puts a 3pl perfect after a dual subject. The engine has no PRF.3DU, and the plan left num unset, so the plural fallback applied.
  - Fix: the present tréseti PRS.3DU, giving `méne h₃ókʷih₁ ne trésetes`. The English now reads 'My eyes do not tremble'.
- **b77f7cd4 (t3-t026-00012), number.**
  - The error: `dwóh₁ ḱwónh₁e h₁ím sékʷonto` puts a 3pl middle after a dual subject. **The plan explicitly asked for MID.PST 3DU.** The deponent has no such cell, and the realizer silently gave 3pl (engine gap 1).
  - Fix: one dog, giving `ḱwṓ h₁ím sékʷeto`. The English now reads 'A dog followed him'.

## Wrong: planted (5, no fix needed)

One second finding on a planted item was real in its source record:
- The 955473e5 verdict also flagged `méǵh₂ih₂ swésōr`, a singular apposition against the English 'great sisters'.
- The source record is t3-t026-00022. The reviewer inferred this after scoring, from the hymn survey; the resolve script names no records for plants.
- The fault was in the plan: the APPOS slot takes its number from its head (Dawn).
- Fixed with a separate dual vocative NP: `nókʷt h₂éwsōs-kʷe méǵh₂ih₂h₁ swésorh₁e`.

| Item | Planted error |
|---|---|
| 955473e5 | nékʷtbʰos dat./abl. pl. used as the address 'Night' |
| 6d59d4c1 | swéh₂i loc. sg. f. for swóm 'his own (brother)' |
| e43c974e | gʷnéh₂bʰos dat. pl. for one woman |
| eaaefffc | bʰoydʰéh₂s gen. sg. as the object of dʰéh₁m̥ |
| 9e772845 | nékʷtbʰos 'from the nights' against 'in the night' (judged minor) |

## Minor items

- **f0571ba6 (00019).** The English 'Hear us, Father' has no PIE vocative. The active perfect tetónth₂e was translated 'you are stretched'. Fixed in the English: 'you have stretched out above us' and 'Hear us, hear our words!'.
- **dfc3d807 (00020).** 2pl h₂élete and the plural yúH pl̥th₂enṓs dʰubʰrṓs stood beside dual ǵénh₁torh₁e, ḱlutóm and ph₂stóm.
  - Fixed: the text is dual throughout, `yú pl̥th₂enóh₁ yú-kʷe dʰubʰróh₁ … h₂életes`.
  - usméd stays plural, because the engine builds no ABL.DU.
- **f962e52b (00003).** lowkóm 'open, light space' was rendered 'into the light'. The English now reads 'into the clearing'.
  - **Remains minor:** the masculine swóns/h₁íns for Dawn's cows follows the lexicon gender of gʷṓws (m). The Vedic Vala cows (gā́ḥ) are feminine.
- **Tier 1 4cb410d4.** This is the Lühr-type source notation (wlh₂néH, unmarked syllabic m in méǵHm, (h₁é)). The English drops gʷr̥Hḗi 'on a hill'.
- **Tier 1 6618d3af.** Laryngeal-less notation. The English 'the sheep has' is singular, but owibʰyos is plural.

## Accepted (not penalised)

- The Narten optative h₁édih₁t.
- Unaugmented injunctives (aorist) used for an English present.
- Common-gender kʷís for a female referent.
- gʰóstis 'stranger' used as 'enemy' (Lat. hostis).
- Middle h₁áyso 'take' beside active h₁áydʰi 'give'.
- A neuter-plural subject (dʰewséh₂, wékʷesh₂) with a singular verb.

## The "born of Sky" substitution

- **What the planner wrote:** for t3-t026-00015 (not in the packet) the planner wrote `diwés ǵń̥h₁yomh₁na déywi`, 'born of Sky', because "no daughter lexeme was in the slice".
- **Grammar:** the form is grammatical (abl. + present middle participle).
- **Why it is still a poor substitute:**
  - The participle means 'being born', not 'born'.
  - It throws away the best-secured Dawn formula of all, *diwós dʰugh₂tḗr (Ved. divó duhitā́/duhitar, Gk Διὸς θυγάτηρ).
- **The lexeme was available:** `pie-lex-dhugh2texr` is in the lexicon, admissible, and has a VOC. `formula_menu.json` lists "Dawn, daughter of Sky" with exactly these lexemes.
- **Fix:** the plan now has APPOS dʰugh₂tḗr + POSS dyḗws. It realizes as `h₂éwsos léwka déywi diwés dʰúgh₂ter`, with the retracted vocative as in Ved. dúhitar, and the English reads 'Daughter of Sky'.
- **Note for the lead:** dʰugh₂tḗr is not in the t026 slice. The realizer accepts it, but slice-based coverage or export accounting may need to know.
- **Gap:** the fault lies in how the slice is built. It is reported below (engine gap 3).

## Meter claim (159/159)

The claim is true but empty:
- **How the check works:** `realize_plans._meter` counts a line (a sentence) as fitting when its syllable count is within ±1 of 8 or 11. 7–9 and 10–12 join into one unbroken window, 7–12, so the check only measures line length.
- **The numbers:** of the 159 lines in the 26 hymns and prayers, 32 have 7 syllables, 41 have 8, 32 have 9, 21 have 10, 18 have 11 and 15 have 12. Only 59/159 (37%) are exactly 8 or 11.
- **What the check never tests:** cadence (the gāyatrī/triṣṭubh iambic close), equal line length within a poem, or caesura.
- **What it does show:** the planner keeps sentences short. It does not show the hymns are metrical.

## Poetry verdict

About half of the 13 hymns have real hymnic form:
- **Relative-clause praise:**
  - e26e4114 (00017) is a model: `sóh₂wl̥ diwés h₃ókʷ, h₁yód … wóydth₂e, h₁yód … yéwgs, h₁yód … gʷʰr̥néwsi …`, five neuter relatives agreeing with sóh₂wl̥, then the request `n̥sméy h₂ew l̥h₂pdʰí, n̥sméy léwkm̥ h₁áydʰi`.
  - f0571ba6 (00019) has `h₁yós … dʰéh₁s` ×2, the epithet déh₃tor h₁uséwōm, 'king of gods', and a closing request.
- **Epithet chains:** 00015 and 00016 (Dawn: léwka déywi, diwés dʰúgh₂ter, kʷspés swésōr, ending in ḱléwos ń̥dʰgʷʰitom) and 955473e5 (00022) have vocative epithet chains and a final plea.

True relative-clause praise appears in only 2 of 13 hymns (00017 and 00019). The h₁yód in 00016, 00024 and 00025 is temporal ('when'), not praise.

The rest are short descriptive prose cut into sentence-lines, though most still end in a wish:
- the spring hymn 1e7ebfb1;
- the Light litany 00021;
- the Dawn-and-Sun sequence 7d1f2941;
- 00023.

Two hymns have no closing request at all: 00023 ends 'we became glad', and 00025 ends 'we rise'.

**Verdict:** genuine hymn form in roughly 6 of 13, recognisable but thin in the rest. The meter figure does not support "poetry".

## Blind back-translation (6 items)

The six items are in `docs/audits/packets/t026-blind-translations.jsonl`.

| Agreement | Items |
|---|---|
| Full or near-full | f0571ba6, 4c72d046, b48a24ac, e26e4114 |
| Partial | 955473e5, 9e772845 |

- The two partial items turned out to be plants, and they diverged at the planted nékʷtbʰos.
- **Reviewer misreadings:**
  - ḱéyweh₂ read as 'bright' (it means 'dear');
  - pérkʷus read as Perkunos (it is 'oak');
  - h₂éweyes 'birds' put as 'sheep' in 955473e5, although the h₂éwi-/h₂ówi- split was noted.
- In 4c72d046 the blind reading 'did not know each other' was more exact than the planner's English, which was fixed to match.

## Engine, slice and metric gaps (for the lead; `pie/` not changed)

1. **The dual-to-plural fallback is silent, even when the dual is asked for explicitly** (`finite_cell`: no MID 2/3DU, no PRF 2/3DU).
   - Plan 0012 requested MID.PST 3DU and got sékʷonto with no warning.
   - This is the third batch with the problem (t023 66dc51f8, t024 db70fa16, t026 ×2).
   - The engine should reject an explicit DU request that has no cell, or warn on it.
2. **A predicate adjective does not take its noun subject's gender.**
   - In 00005, PRED h₂yewHox after SUBJ h₂éwsōs (lexicon f) defaulted to masculine h₂yéwHō. When the SUBJ is a pronoun with an explicit gender (00015), it agrees.
   - The checker should either infer the gender from the subject or reject a gender mismatch.
3. **The slice dropped a formula's lexeme.**
   - The t026 slice (theme dawn/sky) left out dʰugh₂tḗr, although the formula menu's "Dawn, daughter of Sky" names it.
   - make_slice should pull in every lexeme of a menu formula whose other lexemes are in the theme core.
4. **The meter metric is vacuous** (see above).
   - It should test exact 8/11, or a cadence, and per-poem line regularity.
   - The figure should not be quoted as metrical evidence.

## Re-realization

Run: `realize_plans.py data/generation/plans/t026.jsonl --batch t026 --model claude-sonnet-5-5 --prompt-id tier3-planner-v4`.

| | Value |
|---|---|
| Gate | **PASS** |
| Texts | 40/40 exact |
| Reject rate | 0 |
| Tokens | 1,306 |
| Lexeme cap | 7, max 7 |
| Meter | 159/159 |

The token count dropped by 1 (from 1,307), when the numeral dwóh₁ was removed. The cap still rounds to 7, but only 6 tokens of margin remain above the 1,300 threshold.

Release approval is not set; that is for the lead.

## Lead's note (2026-10-28)
The reviewer's restoration of *diwés dʰugh₂tḗr* in t026-0015 was reverted to "born of Sky". `pie-lex-dhugh2texr` belongs to a root family held out of training for the cognate→PIE benchmark (`pie.export.eval_root`). Any training use would quietly drop that family from the benchmark. Whether to swap the held-out families so that "Daughter of Sky" can be trained is open with the owner.
