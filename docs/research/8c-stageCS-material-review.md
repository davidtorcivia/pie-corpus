# Stage C–S queue B material review (2026-10-25)

The ledger is `data/research/8c/stageCS/error-verdicts-material.jsonl`: 28 material observations, 27 confirmed and one rejected. The eight specified follow-up files were inspected through their error records only; one additional boundary report (RS004F:17, tagged `ocr`) confirms uirt[h]i splitting and is covered by the restoration rule. Source OCR and CELT XML were read independently. Dictionaries were checked for the restored Irish words; structural apparatus verdicts depend on explicit source headings, sigla, grammar labels and context, not etymological matches. The local Middle Welsh dictionary does not independently establish the reported anointing lemma; only the directly visible split is repaired, without changing its lexical mapping.

The rejected report is ZCP 3, OCR line 185: the editor explicitly introduces and translates a quotation from manuscript B. Its alternative-title wording is manuscript text, not the modern editor's composition.

## Source fixes

`pie/material_units.py` provides the reviewed cleanup pass. `material-unit-rules.json` supplies cited, inclusive source-line ranges for exclusions. These are loader inputs, not edits to generated tables.

- Celtic: exclude ten units wholly within eight reviewed apparatus/commentary ranges; retain primary text in the two mixed units; join internal alphabetic restorations; merge the adjacent White Book units at OCR 21478/21480 without inserting a space into the divided word. The source quotation rejected above is retained.
- Edda: stop at the printed commentary heading; exclude the three reviewed prose introductions; reset their poem owners; normalize the relevant Guðrúnarkviða running headings without conflating Völsungakviða; parse A./B. stanza prefixes.
- Byliny: exclude seven independently reviewed editorial source spans. The existing heuristic remains elsewhere; this is not a complete apparatus survey of these editions.
- Grein: reject numbered manuscript/editor variant citations before normalization and dictionary-based verse selection.

The historical Celtic OCR builder is `raw/daughters/celtic-stageC/build/celtclean-part-ocr.py`, with classification/unit construction in `celtclean_ocr.py` and assembly/deduplication companions. It was inspected as text only, never executed or imported. Its documented siglum filter misses repeated identical L sigla, glued sicH, and commentary fragments after number stripping. The new pass works on the frozen layer through the Stage C loader, so future Stage C–S builds receive the repairs. `scripts/build_celtic_material_units.py` also produces a separate reviewed layer without overwriting the frozen input. It is idempotent.

## Verification and handoff

| Loader/layer | Before | After | Removed | Added | Modified retained units |
| --- | ---: | ---: | ---: | ---: | ---: |
| Celtic complete layer, including duplicates | 375,098 | 375,087 | 12 | 1 | 493 |
| Edda | 13,801 | 12,591 | 1,212 | 2 | 635 |
| Byliny | 153,727 | 153,710 | 17 | 0 | 0 |
| Grein, with project Old English dictionary filter | 12,395 | 12,254 | 141 | 0 | 0 |

Among active Celtic units (duplicates excluded), Early Modern Irish has 156 modified rows; Middle Irish loses 10 and modifies 297; Old Irish modifies 37; Middle Welsh replaces two units with one; Old Welsh is unchanged. The live Celtic loader output exactly equals v2 with duplicate rows excluded.

Celtic removals comprise ten apparatus units and two units replaced by their merge. Of the 493 modified rows, 491 only join word-internal restoration brackets; two retain the primary portion of mixed units. Edda adds two stanza-opening lines previously lost to the OCR debris threshold before the stanza prefix was parsed. All removed/added/modified IDs and layer hashes are recorded in `data/research/8c/stageCS/material-unit-diff.json`. Comparisons asserted the relevant source-range/pattern condition for every removal, unchanged byliny/Grein survivors, and restoration-only changes for all other CELT text edits. Representative Grein removals were also checked directly against the OCR.

The builder ran first into `/tmp`, then produced `raw/daughters/celtic-stageC/units.v2.jsonl`; the outputs match byte for byte. The old `units.jsonl` remains untouched. No slabs, Tier 2/Tier 3 corpus files or export were rebuilt. The Stage C loader still reads the old filename and applies the cleanup; the lead can switch to v2 when ready. A version suffix invalidates the affected Stage C loader-group caches (stageB, Celtic, Balto-Slavic). Standalone Stage B caches supplied separately must be refreshed by their owner.

Regression tests cover preservation of primary quotations, mixed-unit cropping, restoration boundaries, Welsh merge provenance/dedupe references, exact exclusion boundaries, Grein apparatus, Edda commentary/prose filtering and distinct poem names. The first full suite passed (2,662 tests, 475.97s). The final full run, during concurrent mapping edits, finished with 2,660 passed and two failures (474.20s): `test_override_file_rows` (new Germanic override rows lack `erratum`) and `test_every_override_file_and_key_is_loaded` (Celtic override rows changed after the resolver snapshot). A fresh targeted rerun passes the resolver test and all six material tests; only the missing Germanic `erratum` metadata still fails. These mapping files are outside this task’s owned scope and were not edited here. The full-suite-green acceptance condition remains blocked pending the owner’s repair and a stable final run.
