# Tier 2 (back-projection) adversarial review, round 6

Reviewer: an independent "skeptical Indo-Europeanist" subagent, 2026-10-28. I had no part in writing these lines.

**Naming.** This review covers the 14 lines of *drafting* round 3 (`docs/audits/tier2-round3-drafts.md`). Review rounds 3 to 5 already exist (`tier2-review-r3.md` to `-r5.md`), so this is review round 6:
- this file, `tier2-review-r6.md`;
- `data/tier2/review-r6.jsonl`;
- entries tagged `"review": "r6"` in `data/tier2/review_verdicts.json`.

## Scope

- The 14 round-3 draft lines (notes begin "Round 3 draft … not yet reviewed").
- Every previously reviewed line whose secure set or PIE text changed in the clean rebuild (§1): 7 lines.
- bp-ii-gmc-001, stale since 2026-10-25 (a support-locus edit), re-bound.

## Method

- **Rebuild.** Every cluster in `data/tier2/plans/` was rebuilt with `scripts/build_tier2.py` under the current mappings (corpus-quality batch 1, the theonym narrowing, the engine merge). Each record was diffed against the committed records on pie, secure_checks levels, secure_share, eval_grade and the verified flags.
- **Loci.** Every parallel locus of the 14 drafts was opened in its local corpus with `python3 -I`, read-only:
  - VedaWeb VNH text;
  - AGDT, with tags and heads;
  - GLAUx 0013-003, 0199-002, 0033-002, 0085-003 and 0006-001;
  - CAB;
  - DCS AVŚ 12.1 and 4.12;
  - CELT G301008 and G301900;
  - FJ 1926;
  - Perseus Latin (Catullus, Lucretius).
- **Scholarship.** West 2007 and Watkins 1995 were read only to confirm that a parallel is claimed and how. They are not quoted.
- **Standards.** The verdict scale and the three rules of round 4 (`tier2-review-r4.md` §0) apply unchanged:
  - **sound:** the head is shared in two branches in the same formation, and the line is not generic;
  - **weak:** a real parallel that is overclaimed;
  - **reject:** only periphery or only root-level material is shared, or the line is a commonplace, or a misconstrual.
  - Rule 1: an interpolated NP head needs a secure dependent phrase.
  - Rule 2: a tense or aspect difference counts as root level.
  - Rule 3: late or derivative witnesses (Catullus 64 and Lucretius among them) do not carry an independent branch.
- **Eval grade.** It is mechanical: sound, plus at least one lexeme the builder finds exact in two branches.
- **Caveat.** As before, this review was not plant-calibrated.

## 1. Rebuild drift

The PIE text of every line is unchanged; no form drifted. Drift on previously reviewed lines:

| line | verdict | change | before → after (secure_share; eval) | cause | verdict now |
|---|---|---|---|---|---|
| cattle-raid-002 | sound (r2) | *gʷʰn̥tós exact → root | 1.0 → 0.5; eval stays true | Gk πρόσφατος is now root (compound member) | sound, unchanged |
| cattle-raid-009 | weak (r2) | *péḱu none → exact | 0.333 → 0.667; false | Umbr. pequo now keyed | weak, unchanged (r2: contradicted imperative ph₂dʰí) |
| dawn-sun-009 | weak (r5) | *sóh₂wl̥ none → exact | 0 → 0.5; false | cq1 erratum maps epic ἠέλιος to *sóh₂wl̥ | weak, unchanged; the Greek credit is a false positive (see §3) |
| dawn-sun-016 | sound (r1) | *sóh₂wl̥ none → exact | 0.25 → 0.5; stays true | same ἠέλιος mapping; Av. huuarə is a true exact | sound, unchanged |
| death-otherworld-004 | sound (r2) | *gʷʰn̥tós exact → root | 0.5 → 0; **eval true → false** | πρόσφατος root; *ḱey- was already root (II) | sound, unchanged; eval lost to builder false negatives (§3) |
| dragon-slaying-006 | sound (r2) | *gʷʰn̥tós exact → root | 0.667 → 0.333; stays true | πρόσφατος root | sound, unchanged |
| sky-father-011 | weak (r5) | *ph₂tḗr none → exact | 0.667 → 1.0; false | cq1 erratum keys Iuppiter for both members | weak, unchanged (Catullus 64 is the only Italic witness) |
| bp-ii-gmc-001 | sound (r5) | none (only the review binding went stale) | 1.0; eval true → false (stale) | support-locus label edit, 2026-10-25 | **sound, re-bound (r6)**; eval restored |

Five more lines moved from level none to root for *sóh₂wl̥, with secure_share and eval unchanged: dawn-sun-010, -011, -018, -020 and divine-twins-002. This does not touch their verdicts.

The drafter predicted five drifts (dawn-sun-009, -016, death-otherworld-004, dragon-slaying-006, sky-father-011); all five occurred as predicted. Two were not predicted: cattle-raid-002 and cattle-raid-009. No plan's sha changed, so no verdict became stale except bp-ii-gmc-001's.

**Verdicts are unchanged on all drifted lines.** In every case the drift is the builder catching up with, or diverging from, a reading the earlier round had already made by hand:
- r2 had already said that the builder did not credit -φατος or the Umbrian;
- r5 had already ruled ἠέλιος a derivative and Catullus derivative.

## 2. Verdicts on the 14 drafts (and the re-binding)

| id | PIE | verdict | deciding fact |
|---|---|---|---|
| dawn-sun-022 | n̥mr̥téh₂ h₂éwsōs | **sound** | Both words are exact in Gk and II (Bacchyl. 17.42; RV 1.113.13a+d, predicated of Dawn). Caveats: one late-lyric Greek instance; oxytone against Ved. amŕ̥tā. |
| epic-diction-006 | wiHrṓm h₁éḱwōm-kʷe | **sound** | Ce fer ⁊ ech (Síaburcharpat = LU) and II vīrébhir áśvair, aspaēšu vīraēšu. West and Schmitt claim inheritance, and the shared choice of *wiHrós answers the generic objection. |
| epic-diction-007 | ish₁róm ménos | **sound** | Schulze's ἱερὸν μένος = iṣiréṇa mánasā, exact in form and accent. Only one Vedic instance. |
| epic-diction-005 | h₁éḱwōs h₂néres-kʷe | weak | RV 10.68.12 is a four-member list with vīrébhiḥ in between. The *h₂nḗr pairing is the Greek renewal, so it is a generic pair. |
| bp-ii-ita-004 | deywṓm ǵénh₁os | weak (reject edge) | The head is root level in II (jánman-). The only exact branch rests on Catullus 64 and Lucretius (rule 3). |
| death-otherworld-012 | tód toy gʷʰónos h₁ésti | weak (reject edge) | ON bani is the agent noun (root). The noun is exact in Greek only, and the frame is interpolated. |
| epic-diction-008 | h₁wésu ménos | weak | The words are exact, but the passages are not parallel: 'good courage' against the Gathic theological 'Good Thought'. West's comparison is the non-cognate bhadrám mánaḥ. |
| epic-diction-009 | dʰr̥snuwónt ménos | weak | The modifier is root level in both branches, and the engine's participle is in neither. |
| epic-diction-010 | nebʰelom wésn̥to | weak (reject edge) | No member is exact in two branches (s-aorist against root present; νεφέλη against abhrá-). |
| epic-diction-012 | uḱónts só uḱn̥tbʰís tṓys h₁ḗdtu | weak (reject edge) | The polyptoton core is shared at formation level. The verb and the heads are interpolated, and the Greek is drama only. |
| epic-diction-013 | deywṓs mr̥tṓs-kʷe | weak (reject edge) | A near-universal polar pair. *deywós is II only; *mr̥tós carries an ablaut caveat and a builder false positive. |
| epic-diction-011 | nébʰos wésm̥h₁nos só | **reject** | Rule 1: the head 'he' is interpolated, and neither dependent is exact in Greek. |
| healing-charms-007 | h₃r̥dʰwós sth₂dʰí | **reject** | A commonplace: West calls the shared words trivial and the inheritance thematic. The verb is root level with a different stem and valency. |
| dragon-slaying-016 | gʷʰénoh₂ h₁ím kʷoynéh₂h₁ | **reject** | Misconstrual. Avestan kaēna goes with 'come', not 'slay'. The Greek clause is 'accepted blood-price'. Only the noun is shared. |
| bp-ii-gmc-001 | priHóm h₁nómn̥ | sound (re-bound) | Only a support-ref label changed since r5. |

**Counts (the 14 drafts): 3 sound, 8 weak, 3 reject.** With the re-binding: 4 sound, 8 weak, 3 reject (15 verdicts). The drifted lines keep their verdicts (§1).

The drafter flagged six lines as root-level-only: epic-diction-009, -010, -011, -012, healing-charms-007 and dragon-slaying-016. None of them is sound; two are rejected (-011 and healing-007) plus dragon-016. Of the two lines open to the generic objection, -005 is weak and -006 survives as sound.

## 3. Findings per line

Full reasons, with every locus checked, are in `data/tier2/review-r6.jsonl`. The points that decided each verdict:

1. **dawn-sun-022 (sound).**
   - GLAUx 0199-002 at 17.42 has ἀμβρότου (fem. gen., ATR) agreeing with Ἀοῦς, in ἐραννὸν Ἀοῦς φάος.
   - The GLAUx lemma Ἀών is wrong, as the drafter says.
   - RV 1.113.13: devī́ uṣā́ḥ in 13a and ajárāmŕ̥tā in 13d belong to one stanza, with the same subject.
   - The scan's RV 7.75.3b is correctly dropped as a misconstrual.
2. **epic-diction-006 (sound).**
   - The CELT XML of G301008 and of LU (G301900) both read bátar anála fer ⁊ ech.
   - The LU Táin also has ó aíb ech ⁊ analaib fer, which supports a Celtic coupling.
   - West ch. 12 cites Wackernagel, Benveniste and Schmitt (1967) for the formula. His witnesses for the *wiHrós word are Celtic (Gododdin, Táin), Latin (uiris equisque, Livy) and Avestan (aspa.vīraja).
   - What makes it more than a natural pair is the lexical choice *wiHrós across three branches, not the collocation itself.
   - Cic. Off. 3.116 would add Italic if checked in `latin-perseus-latinlit`; it is a recommendation, not cited here.
3. **epic-diction-005 (weak).**
   - RV 10.68.12cd (VNH) is sá góbhiḥ sá áśvaiḥ sá vīrébhiḥ sá nŕ̥bhiḥ, so it is not a horses-and-men pair.
   - RV 7.41.3cd (support) splits the two words across pādas.
   - Because Greek ἀνήρ is the renewal of the formula's 'men' word, this line pairs two words that each branch may have coupled independently.
4. **bp-ii-ita-004 (weak).**
   - Perseus: Catull. 64.23 heroes, salvete, deum genus (vocative); Lucr. 5.1156 divom genus humanumque. Both are on round 4's derivative list.
   - Catullus is rendering the Hesiodic 'divine race of heroes'.
   - The real cognate pair West gives is Ved. jánas- = γένος, and neither form is in the cited loci.
5. **death-otherworld-012 (weak).**
   - Hávamál 72 (FJ 1926 p. 36) is confirmed.
   - Watkins ch. 51 builds *h₁es- *gʷʰon-o- from the Greek suppletive periphrasis (Il. 16.144, Od. 11.444, AGDT). His non-Greek comparanda are agent nouns (OP jatā biyā, Ved. hantā́), the same type as ON bani.
   - So the formation of the Greek, which the line takes, is Greek only.
6. **epic-diction-008 (weak).**
   - Il. 17.456 and 24.442: μένος ἠΰ is the accusative object of '(breathed) into' horses and mules.
   - Y. 34.8c (dūirē vohū as manō) and Y. 48.12b (vohū manaŋhā hacā̊ṇtē) are confirmed in CAB.
   - Both words are exact, but the line rests on a collocation of two common words with different senses and no cited claim of an inherited phrase.
7. **epic-diction-009 (weak).**
   - Il. 17.156 μένος πολυθαρσές (nom.), Il. 19.37 (acc.); RV 1.54.3b and 5.35.4c dhr̥ṣán mánaḥ (VNH).
   - West names the pair and also cites RV 8.62.5.
8. **epic-diction-010 (weak).** Confirmed in AGDT and VNH:
   - Il. 14.350 ἐπὶ … νεφέλην ἕσσαντο;
   - Il. 20.150 ἀμφὶ … νεφέλην … ἕσαντο;
   - RV 5.63.6c abhrā́ vasata marútaḥ;
   - RV 5.85.4c sám abhréṇa vasata párvatāsaḥ.

   West treats the *wes- metaphor as shared, so the line is weak rather than a reject. Its wording is root level throughout.
9. **epic-diction-011 (reject).**
   - Il. 15.308 εἱμένος ὤμοιιν νεφέλην (perfect participle) and RV 9.83.5b nábho vásānaḥ are confirmed.
   - West's exact Greek match is νέφος + ἑσ-, which no cited locus has.
   - Recommended fix: drop the line. epic-diction-010 already carries the image.
10. **epic-diction-012 (weak).**
    - GLAUx: [Aesch.] PV 218 = line 220 ἑκόνθ’ ἑκόντι Ζηνί; Eur. Cycl. 258 ἑκὼν ἑκοῦσι.
    - Recommended fix: an np line, nominative participle + instrumental participle, with no verb.
11. **epic-diction-013 (weak).**
    - RV 1.100.15a; Il. 24.533 and 15.99 (both negated); Y. 29.4b.
    - Recommended fix: re-cite the Vedic márta- with its own path, and fix the maṣ̌iia- mapping.
12. **healing-charms-007 (reject).**
    - DCS AVŚ 4.12, sixth stanza: sa ut tiṣṭha … prati tiṣṭha ūrdhvaḥ.
    - Pind. P. 3.53: τοὺς δὲ τομαῖς ἔστασεν ὀρθούς.
    - What is inherited, per West, is the use of standing up as the sign of a cure, a theme rather than a phrase. A back-projection line cannot carry that.
13. **dragon-slaying-016 (reject).**
    - CAB YtWay8.3d yat̰ kaēna nijasāni | 8.3e azəm brāϑrō uruuāxšiia | 8.3f yat̰ janāni hitāspəm.
    - AGDT Il. 9.632–633: κασιγνήτοιο φονῆος ποινὴν … ἐδέξατο, with φονῆος ATR of ποινήν.
    - The Greek scene is the alternative to vengeance (compensation accepted). The ποινή = kaēnā- equation is sound and could carry an NP line, but the cited passages share no phrase.

## 4. Builder errors found (for the mapping owner)

**False positives:**
- **Gk ἠέλιος → *sóh₂wl̥ "exact"** (cq1 erratum, scan 22). ἥλιος/ἠέλιος is the -iyo- derivative (*sāwel-iyo-), the same type as Ved. sū́rya-, so by the brief's rule it is root level. This inflates dawn-sun-009 (0 → 0.5) and dawn-sun-016. r5 had already read ἠέλιος as a derivative.
- **Gk νεφέλη → *nébʰos "exact"** (epic-diction-011; flagged by the drafter). It is *nebʰelā-.
- **Av. maṣ̌iia- → *mr̥tós "exact"** (epic-diction-013; flagged by the drafter). It is *mr̥tyo-.
- **Ved. dhr̥ṣ- → *dʰr̥snéwti "exact"** (epic-diction-009). It goes through the root.

**False negatives:**
- **Ved. √śī- (áśeran) and Av. saē- (sōire) → *ḱeytor** (death-otherworld-004). The Vedic lemma `√śī-` gets no match; plain `śī-` matches in dragon-006. The Avestan routes to the u-stem *ḱéy-u-s. Both are the root-present middle of *ḱey-. This costs death-004 its eval grade. Two fixes, either of which needs a re-review of the line:
  - re-cite the lemma as `śī-` (a plan change, so the line goes stale);
  - fix the `√` normalization and the saē- route in the mapping.
- **Gk -φατος in πρόσφατος → *gʷʰn̥tós** is now root level (compound member). This is the builder's rule; r2 credited it by hand. The verdicts of cattle-002, dragon-006 and death-004 do not depend on it.
- **Gk εἰμί → *h₁ésti** is root level only (death-otherworld-012).
- **Av. janāni → *gʷʰénti** is root level only (dragon-slaying-016).
- **AV ūrdhva → *h₃r̥dʰwós** is root level only (healing-charms-007).

## 5. Build after the verdicts

The verdicts were merged into `data/tier2/review_verdicts.json` (15 entries, `review: r6`, bound to the current plan sha). Seven clusters were then rebuilt: bp-ii-gmc, bp-ii-ita, dawn-sun, death-otherworld, dragon-slaying, epic-diction and healing-charms. The three rejects now move to `data/tier2/rejects/`.

**Clean worktree.** Another agent's uncommitted corpus-quality batch 2 edits appeared in the shared working tree during this round:
- mapping overrides (`z-cq2-formulas.json`, `cq1_mapping.py`, `compound_members`);
- they are read by the secure checker.

A rebuild in that tree changed four levels on unchanged plans: dawn-sun-016 *sóh₂wl̥, death-otherworld-012 *h₁ésti, epic-diction-008 *h₁wésus and epic-diction-013 *mr̥tós. To keep the committed records off unverified WIP mappings:
- every cluster was rebuilt in a clean git worktree at HEAD, with only this round's `review_verdicts.json` added (raw/ symlinked read-only);
- that output was committed.

Against the step-1 commit (4f54115), the clean build is identical in text, levels, secure_share and verified flags on all 109 shared records (review fields aside), so the drift table in §1 is the committed-mapping drift. Four records differ only in evidence-path strings: dawn-sun-001, -018, healing-charms-001 and sky-father-006, all with the same levels. Their clusters had been built after the WIP edits began. This commit carries the clean versions. When batch 2 lands, these four lines should be checked again.

**Eval grade:**
- Committed state before this round: 40 eval-grade lines out of 98.
- After the clean rebuild: 38 out of 112. bp-ii-gmc-001 had gone stale and death-otherworld-004 lost its exact lexeme.
- **After the verdicts: 42 eval-grade lines out of 109 built** (46 sound, 63 weak; the 3 new rejects are in `data/tier2/rejects/`).

Per cluster after the verdicts:

| cluster | lines | rejected | mean secure_share | eval_grade |
|---|---|---|---|---|
| bp-ii-gmc | 1 | 1 | 1.0 | 1 |
| bp-ii-ita | 4 | 0 | 0.542 | 1 |
| dawn-sun | 16 | 6 | 0.5 | 6 |
| death-otherworld | 6 | 6 | 0.139 | 1 |
| dragon-slaying | 10 | 6 | 0.218 | 5 |
| epic-diction | 12 | 1 | 0.625 | 4 |
| healing-charms | 4 | 3 | 0.479 | 3 |

The other eight clusters are unchanged from §1.

**Hold-out check.** Run in the clean worktree and again in the main tree, with the same result:
- `build_holdout.py --dry-run` prints universe 1469, protected 217, pool 913, held 147.
- `pytest tests/test_export.py` gives 12 passed.
- Tier 2 secure families (secure_level exact or root) number 40, up from 38. The two new ones are pie-root-wekj-wish (epic-diction-012) and pie-root-mer-die (epic-diction-013), and both were already in `protected_roots.json`.
- **No held family is protected**, and no held family occurs in any Tier 2 record.

**Eval-grade changes:**
- **Gained:** dawn-sun-022, epic-diction-006 and epic-diction-007 (new sound lines with exact lexemes), and bp-ii-gmc-001 (re-bound).
- **Lost:** death-otherworld-004 (builder false negative; the verdict is still sound).
