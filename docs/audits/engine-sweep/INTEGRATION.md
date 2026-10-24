# Engine sweep: integration

Integrated 2026-10-24 from the eight reports in this directory (brief: BRIEF.md). Non-controversial fixes went in first, one family at a time, with `uv run pytest -q` green after each family. The lead's convention decisions followed, then the realize.py fixes (after the coordinator freed the file; see PENDING-realize.md). Every applied fix has a test, in tests/test_engine_sweep.py (39 tests) or at the end of tests/test_realize.py (`test_sweep_*`, 10 tests).

## Results

| Check | Before | After |
|---|---|---|
| `uv run pytest -q` | 2,248 passed | **2,303 passed**, 0 failed |
| Wiktionary crosscheck (`scripts/crosscheck_paradigms.py`; test_morph's acceptance test) | 14,015/14,197 cells (98.72%), 574/615 tables, 0 unexplained | **14,015/14,197 (98.72%), 574/615 tables, 0 unexplained** (unchanged: every engine change is gated to the handbook convention, or, for the phon.py junction rule, changes no Wiktionary cell) |
| Usable lexemes (`classify_report.json` `usable_for_tier3`) | 3,814 | **4,215** (+401: 282 neuter o-stems, 62 s-aorists, 35 thematic deponents, 21 *-tḗr* agent nouns, nókʷts, …) |
| id_registry.jsonl | | unchanged (checked after every rebuild) |
| Dry re-realization of all 2,115 stored tier-3 plans (in memory, nothing written) | 154 records differ from the stored text (stale), 31 plans rejected | 692 records differ, **31 rejected (the same 31)**, 0 exceptions |

Two pinned tests changed, both because the report showed they pinned a wrong or superseded form: tests/test_realize.py `test_t017_review_stems` (*h₂ḱmnés* → *h₂ḱm̥nés*, r-n-stems defect 1) and `test_np_utterance_has_no_copula` (*swéh₂du* → *sweh₂dú*, the lead's u-adjective decision; the realize.py docstring example was updated with it).

## Applied, by family

**thematic.md.** Defect 9 neuter dual *-oyh₁* first (handbook only; Wiktionary keeps *-oy*). Defects 3, 4, 6, 7 overrides: *Hróth₂os*, *dʰubʰrós*, *dinós*, *wékʷsperos*, ten neuter s-stems (*ḱéh₂dos*, *dʰérsos*, *gʷélHos*, …). Defect 5: *lówh₃trom*, *sh₂éytlom* overrides; silver (*h₂r̥ǵn̥tóm*) via the realize.py and compound.py condition. Defect 10: *pos: adj* for *h₁rudʰyos*, *wēdos*, *dʰr̥ǵʰtós* only (see below). The "Gating" change to `classify_lexicon.py` `compare`: the backtest reran at 1.0 for `shape:thematic-neuter` (it was 0.81), so the 282 neuters became usable. The header docstring of morph.py no longer credits Ringe with the contracted forms.
Decisions: vocative plural/dual retraction (Fortson §6.52 states it for the plural; applied to the plural and, as the report proposes, to the dual; every non-neuter declension); boukólos kept before *u* in the handbook thematic and eh₂ declensions (*pérkʷunos*, as Mallory & Adams write it; Fortson does not print the name, and his §3.39 states the rule for a labiovelar next to *u*; `phon.delabialize(before_u=False)`).

**feminine.md.** D6 athematic *-eh₂* Stang (*dn̥ǵʰwéh₂m*, *-ās*); D4 *gʷḗn* voc. = nom.; D9 alternatives *-eh₂eh₁*, *-eh₂ih₁*; overrides D3, D4, D7, D8, D10, D11, D12 and the gender housekeeping lines. Decisions: D2 vocative *-a* (retracted, then *-á*, *-eh₂*), D1 devī acc. *-ih₂m*.

**i-u-stems.md.** Patch A INS.SG on the zero-grade suffix (#5); Patch C neuter dual (#15); overrides #4 *déh₂nu*, #6 *néh₂us*, #8 *HeHḱús*, #9 *sweh₂déw-*, #10 *péḱu*, #11 *bʰeh₂ǵʰús*, *Hrugʰís*, #12 *h₁léngʷʰus*, #13 *pérkʷu*, #14 *ḱm̥tógʷus*. Decisions: #2 *-ḗw* added as an alternative only (restricted to e-grade weak stems, so no invented *suHnṓw*); #1 suffix accent for the eight u-adjectives listed in STATUS.md. #3 not applied: Fortson prints no i-stem locative (§6.11 is generic), so the lead's condition was not met.

**r-n-stems.md.** Defect 1 phon.py `join` step 2b (*h₂ḱm̥nés*); defect 2 men-neuter oblique plural *-mń̥-* (the old forms stay as alternatives); defects 3–6 overrides; defects 7–8 classify rules (backtests reran: `shape:tor-agent` 1.0, `shape:er-stem` 0.902). The `_restore_mn` comment now records the Asno-law contradiction.

**s-root-heteroclite.md.** F1 heteroclite collective *-ōr* (*wédōr*); F3 root accent for unaccented s-stem headwords (classify.py); F8 no accentless locative; F9 `_initial_accent` laryngeal check; overrides F2 *yḗkʷr̥*, F4 *h₃ókʷ*, F5, F6 *dʰǵʰúHs* weak stem, F7 *h₃rḗǵs* locative, F10 *dusménēs*, F11 *nókʷts*. F2/F4/F10 needed a new `form` key in overrides.jsonl (pie/lexicon.py; the old headword stays in `variants`).

**athematic-verbs.md.** E1 glide rule only after a true cluster, rewriting in place; E2 zero-grade optative after an accented or reduplicated stem, 3pl *-ih₁ent*; E3 Narten/s-aorist subjunctive on the e-grade; E4 reduplicated 3pl *dʰédʰh₁n̥ti*; E5 *-tṓd* on the zero grade; S1, S2, D4 overrides; S3 `_redup_weak` fix (regenerated: *wewḱ-*, *wiwkʷ-*, *yeys-*). Decisions: D1 *h₁ḗdti* (Narten), D5 *ḱéyor* (new `VerbSpec.mid_t_less`), D2 *dedh₃més*; N1 2du *-tes* primary with the citation fixed.

**thematic-verbs.md.** Defects 2–3 (merged into the E1 glide condition: `wk[-2].base != wk[-1].base`, in-place rewrite), 4–6 (merged with E2/E3: handbook optative 3pl always *-ent*, including perfects), 7 *-ómh₁nos*; defect 1 (2du) as above; defects 8–9 classify rules (backtests reran: `shape:s-aorist` 1.0 on its one table, `shape:thematic-middle` 1.0 on two); defect 10 in realize.py.

**closed-class-compounds.md.** C3–C6 (closed_class.json; every edit keeps the cell's old forms as alternatives); P1, P2 (compound.py); R1–R8 (realize.py, PENDING-realize.md). Decisions: C1 'I' and C2 'ten' (below).

**t020 review item (from the coordinator).** Consonant-stem nom.-acc. dual: Ringe *-h₁e*; Beekes §13.2.11 C-stems *-h₁e*, u-stems *-h₁*; L&Y §2.1.1 *-h₁e* (glide-final stems *-h₁*); Fortson §6.13 either. Applied *-h₁e* primary for consonant stems, *-h₁* second; i/u-stems and ā/ī-stems unchanged.

**Integration fixes found by the dry re-realization** (each would have broken stored plans): the i/u INS.SG rule fired for men-neuters through the shared `obl_pl` (*dyumń̥h₁*; now separate, tested); the Narten participle *h₁édn̥ts* could not be declined (`decline_participle` now handles *-n̥ts*: gen. *h₁édn̥tos*, f. *h₁édn̥tih₂*); *néh₂w-* 'ship' lost its compositional form (compound.py: a stem in C + glide composes as *néh₂u-*); a bare-stem vocative ending in C + glide is syllabic (*néh₂u*).

## Convention choices made in integration (please confirm)

- 'I': the majority prints the *-oh₂* form (Fortson *eǵoh₂*, L&Y *(h₁)eǵoh₂*, Beekes *h₁eǵ(oH)*; Ringe *éǵh₂*), so the primary is ***h₁eǵóh₂*** with the table's initial h₁. No book prints an accent: the final accent follows Gk ἐγώ, Ved. ahám. *h₁eǵoh₂, eǵoh₂, h₁eǵ, éǵh₂, eǵh₂óm* remain.
- 'ten': ***déḱm̥*** (Fortson, L&Y, the lexicon's pie-lex-dekjm) over Beekes *déḱm̥t* and Ringe *déḱm̥d*. These two agree on a final stop but not on which one, so this is close to a tie.
- 2du: Beekes's *-tHe/os* is marked "perhaps", so it does not count as support for *-th₁es* as primary.
- u-adjectives: *mr̥ǵʰús* and *dlukús* rest on Greek alone, with no contrary evidence; *ténh₂us* stays root-accented (Ringe's model word; Vedic only).
- Override displacement: when an override replaces a spec, `classify_lexicon.py` keeps the old spec in `extra_specs` (`displaced_by_override: true`), and the validator indexes it. So *h₁dénti*, *dédh₃mes* and *pléth₂us* remain recognized forms, but they are not cells. Making them cells (a realize.py merge) is deliberately not done, because most displaced specs are table errors.

## Not applied, for the lead

Blocklist lines (data/generation/ is off-limits to me; the lines are in the reports):
- **Needed now:** none is urgent. *h₂eh₂iḱḗr* (a perfect 3pl glossed 'to possess') would have become a usable *-tḗr* noun under the new er-stem rule. I kept it out with an override `pos: verb` (it is now `unknown:verb-shape`). A blocklist line is still the clean fix.
- thematic 11–12 (*Hyós*, *kʷos*, *h₁énos*, *dwóh₁*), i-u #16 (*tréyes*), athematic S5 (5 3pl-form lemmas, plus *méyh₁wti*, *wéh₁yti*, *h₁éh₁sti*), closed-class L1–L2 (*dwóh₁*, *kʷetwóres*, *sḗm*; the two corpus records with *kʷetwóres* need closed:numerals/4).

Decisions the reports mark that are not in the lead's list (not applied):
- thematic: *-obʰos* first (the lead keeps *-oybʰos*); *kʷékʷlos* m. vs M&A *kʷekʷlóm* n.; *súHros* accent (low confidence); *h₂élyos* as a pronominal closed class.
- defect 10, held back for 5 of 8 lexemes: *pos: adj* for *mr̥wós*, *ḱéywos*, *ḱuh₁rós*, *dʰegʷʰrós*, *sḿ̥teros*. 59 stored plan slots use them as nouns without a gender, and the checker would reject 40 plans. To apply it, add `"gender": "m"` to those slots, then add the overrides (the lines are in thematic.md).
- feminine: D5 devī acc. pl. *-ih₂ns* (Ringe, the only book that prints the form, has *-ih₂n̥s*); L&Y's feminine *-w-íh₂*; Beekes *-eh₂ih₁* as primary; instr. pl. *-bʰi* vs *-bʰis* (cross-family).
- i-u: #7 *suHnús* weak *-éw-* (L&Y/Fortson/Ringe vs Beekes/Wiktionary); i-stem LOC order (#3, condition not met); *ténh₂us*.
- r-n: *méh₂tēr* accent class (keep); men-neuter collective *-mō* as an alternative; *h₂ḱn̥-* (Asno law) vs the *h₂ḱmn-* override; the *kéh₂nmn̥* lemma's stray n.
- s-root: comparatives with weak *-is-* (optional); the `spec_from_template` hyphen guard (it would drop the one table with a hyphen, which the crosscheck counts; the override already fixes the lexeme); the full Wiktionary `coll=` route; *sóḱr̥* collective (rule *séḱōr* vs Wiktionary *sḱṓr*, 1 token, NOM.SG unaffected).
- athematic: D3 the uncontracted 1sg secondary (*stéh₂m̥*), not even as an alternative; S4 the derived statives/factitives (10 gloss-less lexemes; block them instead); the LIV weak-stem correction inside `liv.py`.
- thematic-verbs: *h₁rudʰéh₁ti* → thematic *-éh₁ye-*; the *pr̥ḱsḱé-* override; the perfect subjunctive e-grade (unverifiable).
- closed-class: pronominal dat./abl. pl. *-mos* first; *mē* with 2nd/3rd-person SBJV and with OPT; R9; L3 'one' with pronominal endings.
- The 62 new s-aorists and 35 deponents rely on derived glosses: spot-review them before planners see them, as thematic-verbs.md recommends.

## Corpus-affecting changes (for the re-realization)

Morphology changes the primary form of **1,034 of 42,017 tier-3 tokens** (249 distinct cells), measured by comparing primary cells before and after for each token's lex_id + features. The list is in the scratchpad (`integ/impact.json`). By fix:

| Tokens | Change |
|---|---|
| 230 | spec overrides and the smaller engine fixes (*déh₂news*, *néh₂wm̥*, *Hróth₂os*, *dʰubʰróm*, *h₂r̥ǵn̥tóm*, *h₂wr̥s-*, *bʰuHént*, *dedwiyḗr*, *h₂ḱm̥néh₁*, *-mń̥su*, …) |
| 121 | *h₁ed-* Narten (*h₁ḗdti*, *h₁édn̥ti*, *h₁éddʰi*, …) (decision) |
| 99 | heteroclite collective *wédōr*, *déh₃ōr*, *h₂égōr*, *yéh₁ōr*, … |
| 82 | 'I' *h₁eǵ* → *h₁eǵóh₂* (decision) |
| 79 | *ḱéytor* → *ḱéyor*, *ḱéyo*, *ḱéyror*, *ḱéyro* (decision) |
| 67 | u-adjective suffix accent (*gʷr̥h₂ús*, *sweh₂dús*, *pl̥th₂ús*, …) (decision) |
| 64 | vocative plural/dual retraction (*déywōs*, *wíHrōs*, *súHnewes*, …) (decision) |
| 62 | consonant-stem dual *-h₁e* (*bʰréh₂terh₁e*, *gʷówh₁e*, *dómh₁e*, …) (decision) |
| 55 | 'ten' *déḱm̥t* → *déḱm̥* (decision) |
| 49 | *pérkunos* → *pérkʷunos* (decision) |
| 37 | *dédeh₃ti* mobile weak stem (decision) |
| 21 | devī acc. *-ih₂m* (decision) |
| 20 | i/u INS.SG *-íh₁/-úh₁* |
| 19 | pronoun table consistency (*h₁yósmey*, *kʷósyo*, …) and *tísrn̥s* |
| 17 | eh₂ vocative *-a* (decision) |
| 9 | 2du *-tes* (decision) |
| 3 | thematic neuter dual *-oyh₁* |

realize.py changes word order and agreement on top of this: by the closed-class report's count, phrase *-kʷe* 29, vocative pairs 11, conjoined-subject verbs 8, dual enclitics 3, *moy moy* 3, clitic after *-kʷe* 1, plus 68 tokens relabelled `GEN.PL.ENCL`. In the dry re-realization, 692 of 2,115 records come out different from their stored text (154 of them were already stale before this work), and no plan fails that did not fail before.

Files changed: pie/morph.py, pie/phon.py, pie/classify.py, pie/compound.py, pie/lexicon.py, pie/realize.py, scripts/classify_lexicon.py, data/lexicon/overrides.jsonl (70 → 140 lines), data/morph/closed_class.json, the regenerated data/lexicon/* and data/morph/inflection_specs.jsonl, classify_report.json, crosscheck.json, tests/test_engine_sweep.py (new), tests/test_realize.py, docs/STATUS.md (new section "Conventions (engine sweep)").
