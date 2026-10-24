# Engine sweep: realize.py fixes

Collected from the reports while pie/realize.py was being changed for verbless clauses. **Status (2026-10-24): applied** on top of the new realize.py (the `nominal`/`np` clause types and APPOS), after the coordinator freed the file. Tests: tests/test_realize.py, the `test_sweep_*` functions at the end (all pass, as do the verbless-clause tests).

| # | Report item | Fix as applied | Test |
|---|---|---|---|
| T5 | thematic.md defect 5: `Lexicon.cells` prepended the headword to NOM/ACC/VOC.SG of an o-stem table whose stem differs (silver *h₂ŕ̥ǵn̥tom* + *h₂r̥ǵn̥tósyo*) | the headword is prepended only when `NounSpec(**sp).kind != "thematic"`; same condition in `compound.py` `_determinative` | `test_sweep_thematic_table_paradigm_has_one_stem` |
| TV10 | thematic-verbs.md defect 10: a deponent's participle could be planned active | `check_plan` rejects a participle of a *-tor/-toy* lemma unless voice MID | `test_sweep_deponent_participle_is_middle` |
| R1 | phrase-level *-kʷe* after the conjunct's head | `and_host`: *-kʷe* after the first non-clitic word of the conjunct's phrase (Fortson §7.27, §8.24) | `test_sweep_kwe_follows_first_word_of_a_phrasal_conjunct` |
| R2 | dual enclitics *noh₃*, *woh₃* not Wackernagel | added to `ENCLITIC_PRONOUNS`; any `.ENCL` feature is a clitic | `test_sweep_dual_enclitics_are_wackernagel` |
| R3 | stressed 1/2 pl. gen. falls back to the enclitic but was labelled `GEN.PL` | `_closed_feat` relabels it `GEN.PL.ENCL` | `test_sweep_stressed_plural_genitive_fallback_is_labelled_enclitic` |
| R4 | verb agreed with the first conjoined subject only | group agreement: two singulars → dual, else plural, lowest person; neuter plurals stay singular (Fortson §8.16, Il. 2.468); DU → PL fallback where a stem has no dual cell. The coordination-group computation moved before verb agreement (unchanged logic) | `test_sweep_conjoined_subjects_agree_as_a_group` |
| R5 | conjoined vocative pair *ph₂ter méh₂ter-kʷe* | the *-kʷe* conjunct of a 2-member VOC pair is nominative (Fortson §8.11, Ved. vā́yav índraś ca); its MOD/APPOS follow it | `test_sweep_conjoined_vocative_pair_puts_the_second_in_the_nominative` |
| R6 | Wackernagel clitics before word 1's own *-kʷe* | inserted after word 1 and its *-kʷe/-wē* (Fortson §8.25) | `test_sweep_wackernagel_clitic_after_the_first_words_own_kwe` |
| R7 | indeclinable numerals (5–1000) did not fix the head's number | `"indeclinable": "PL"` | `test_sweep_indeclinable_numeral_makes_its_head_plural` |
| R8 | *moy moy* stacked | a repeated identical clitic (same form and features) is dropped from the cluster | (covered by re-realization; no dedicated test) |
| C5 | numerals 2–4 had no VOC cells (closed_class.json) | VOC = NOM | `test_sweep_numeral_vocative` |

Not applied (for the lead):
- R9 (closed-class report): *-kʷe* on an enclitic-pronoun conjunct is lost. Not patched by the auditor either; planner guidance: a conjunct with *-kʷe* must be stressed.
- *mē* with 2nd/3rd-person subjunctive and with the optative (closed-class report, "Convention note"): a convention decision not in the lead's list. Current rule unchanged (mē for IMP, OPT and 1st-person SBJV).
- A cell-level merge of an override's displaced spec into `Lexicon.cells` (so that, e.g., Wiktionary's *h₁dénti* is an alternative cell of *h₁édti*): not done, because most displaced specs are table errors (*dʰubróm*, *nh₂éws*) that should not become alternatives. The displaced specs are kept in `extra_specs` (`displaced_by_override: true`), which the validator indexes.
