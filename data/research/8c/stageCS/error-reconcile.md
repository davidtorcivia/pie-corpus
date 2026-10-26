# Stage C-S extraction-error reconciliation — 2026-10-25

Checked against the current loaders without building retrieval bundles, regenerating corpus/export files, or opening the historical key or text slabs. Historical verdict ledgers are left intact.

Of the 16 Irish extraction referrals marked confirmed, fix batch 1 already repairs 13; two additional, locus-scoped repairs are implemented in `pie/material_units.py`; one is a conflicting verdict resolved in favor of retaining the manuscript quotation. All 14 confirmed material-owner observations in the other ledger are already handled by fix batch 1.

## Irish: all 16 extraction referrals

IDs refer to `error-verdicts-irish.jsonl`. The locus is the reported historical passage; window suffixes are not new unit IDs.

| Verdict ID | Reported passage | Fixed by batch 1? | Loader/source evidence and disposition |
| --- | --- | --- | --- |
| IR-CS-035 | `mga:G302000:#1/15:3` | Yes | Internal restoration joined: Adcon[n]airc-sium → Adconnairc-sium. |
| IR-CS-112 | `mga:G302000:#1/36:3` | Yes | Internal restoration joined: derscai[g]theach → derscaigtheach. |
| IR-CS-121 | `mga:G302025:#1/105:5 (w2/2)` | No; repaired here | Malformed entity eacute;ga → éga. The ampersand is already missing in CELT G302025.xml:7093; repair is restricted to this unit. |
| IR-CS-134 | `mga:celtic-journal-revue-celtique-1870-1928:revueceltique10pari:L5026-L5028` | No; repaired here | Edition abbreviations der(ed) → dered and atfia(datar) → atfiadatar, restricted to this OCR unit. Source lines 5026–5028 confirm the expansions; unrelated OCR damage is not guessed. |
| IR-CS-135 | `mga:celtic-journal-revue-celtique-1870-1928:revueceltique07pari:L16269-L16269` | Yes | Reviewed lexical/apparatus range; unit absent. |
| IR-CS-136 | `mga:celtic-journal-eriu-1904-1928:eriu_1914_7:L273-L279` | Yes | Mixed unit cropped at the narrative colon; sicH and the apparatus tail absent. |
| IR-CS-137 | `mga:celtic-journal-eriu-1904-1928:eriu_1910_4:L9175-L9177` | Yes | Reviewed apparatus range; unit absent. |
| IR-CS-138 | `mga:celtic-journal-revue-celtique-1870-1928:revueceltique10pari:L11521-L11521:2` | Yes | Reviewed dictionary-reference range; suffixed unit :2 absent too. |
| IR-CS-139 | `mga:celtic-journal-eriu-1904-1928:eriu_1910_4:L8699-L8701` | Yes | Reviewed variant apparatus range; unit absent. |
| IR-CS-140 | `mga:celtic-journal-zcp-1897-1926:zeitschriftfrc03meyeuoft:L185-L185` | Not a defect; retained | Conflicting verdict: Irish ledger says confirmed, but material review rejects it. Source ZCP 3 OCR lines 182–190 explicitly introduce a quotation from manuscript B; the alternative-title wording at line 185 is primary manuscript text. Loader retains it unchanged. |
| IR-CS-141 | `mga:celtic-journal-revue-celtique-1870-1928:revueceltique16pari:L8224-L8230 (w1/3)` | Yes | English editorial lead-in removed; Irish quotation retained. |
| IR-CS-142 | `mga:celtic-journal-revue-celtique-1870-1928:revueceltique14pari:L22341-L22343` | Yes | Reviewed verbal-form list; unit absent. |
| IR-CS-143 | `mga:oldirish-irische-texte-1880-1909:irischetextemit00stokgoog:L25882-L25888 (w1/3)` | Yes | Reviewed German textual-comparison apparatus; unit absent. |
| IR-CS-144 | `mga:oldirish-irische-texte-1880-1909:irischetextemit00stokgoog:L13233-L13235` | Yes | Reviewed German grammatical commentary; unit absent. |
| IR-CS-145 | `mga:celtic-journal-revue-celtique-1870-1928:revueceltique13pari:L22520-L22524 (w2/2)` | Yes | Reviewed preterite paradigm/list; unit absent. |
| IR-CS-156 | `mga:G301026:#1/52:6` | Yes | Internal restoration joined: uirt[h]i → uirthi. |

## Other traditions: all 14 confirmed material/boundary observations

Report numbers below refer to `error-reports.jsonl` and identify the corresponding rows in `error-verdicts-other.jsonl`.

| Report | Reported passage | Fixed by batch 1? | Loader evidence and disposition |
| --- | --- | --- | --- |
| 3 | `non:Sólarljób 82 [edda:19662]` | Yes | Commentary after the printed heading excluded; exact edda line key absent. |
| 94 | `byliny:pesnisobrannyepvkireevskimch3vyp36:22795` | Yes | Reviewed editorial source span excluded; exact reported line absent from byliny_units. |
| 95 | `byliny:pesnisobrannyepvkireevskimch3vyp51:20604` | Yes | Reviewed editorial source span excluded; exact reported line absent from byliny_units. |
| 113 | `non:Sólarljób 82 [edda:19761]` | Yes | Commentary after the printed heading excluded; exact edda line key absent. |
| 115 | `ang:Grein II And Re A S l.1686` | Yes | Numbered manuscript/editor variant citation excluded before normalization; greinII:1686 absent even with a permissive dictionary. |
| 117 | `byliny:11016812bsb:12350` | Yes | Reviewed editorial source span excluded; exact reported line absent from byliny_units. |
| 119 | `byliny:pesnisobrannyepvkireevskimvyp1pesn13:14918` | Yes | Reviewed editorial source span excluded; exact reported line absent from byliny_units. |
| 120 | `non:Helreið    Brynhildar 15 [edda:15443]` | Yes | Introductory prose excluded and poem owner reset to Guðrúnarkviða en forna; reported edda key absent. Prose is not recast as verse. |
| 121 | `non:Grípisspá 53 [edda:12437]` | Yes | Introductory prose excluded and poem owner reset to Reginsmál; reported edda key absent. Prose is not recast as verse. |
| 122 | `non:Hymiskviða 39 [edda:5355]` | Yes | Introductory prose excluded and poem owner reset to Lokasenna; reported edda key absent. Prose is not recast as verse. |
| 134 | `cy:welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:L21480-L21480` | Yes | Separate L21480 unit absent; merged L21478–L21480 contains hirawd, with metadata retained. |
| 139 | `byliny:sbornikotdelenijarusskogojazykaislovesno92:8617` | Yes | Reviewed editorial source span excluded; exact reported line absent from byliny_units. |
| 154 | `byliny:pesnisobrannyepvkireevskimch2pesni36:18509` | Yes | Reviewed editorial source span excluded; exact reported line absent from byliny_units. |
| 155 | `byliny:11016812bsb:6393` | Yes | Reviewed editorial source span excluded; exact reported line absent from byliny_units. |

The additional `155:observation:1` row is an **unclear lexical observation**, not a fifteenth confirmed material defect. It refers to the same excluded apparatus line as report 155. Its lexical interpretation remains unresolved; no global lemma suppression is warranted.

## Verification

- Read the frozen Celtic layer as JSON text and compared the actual reported IDs with `build_8c_stageC.celtic_rows()`: 325,551 active repaired source rows. All eight reported apparatus IDs are absent; the two mixed units retain their primary portion; the three bracket repairs and two new repairs produce the expected forms; the manuscript-title unit is unchanged. The White Book merge is present under its combined locus.
- Ran `formula_search_multi.edda_lines()` on the actual source: 12,591 lines; both commentary keys and all three mislabelled prose keys are absent. The existing `edda_region` rule sets the next poem owner.
- Ran the full `build_8c_stageC.load_celtic()` loader without a cache: 368,754 windowed units. Verified the expected restored forms at all three bracket-repair loci, both new repair loci, and the combined Welsh locus (including both windows of G302025:#1/105:5).
- Ran `bsl_mapping.byliny_units()` on the actual sources: 153,710 lines; all seven reported editorial keys are absent.
- Ran `formula_search_multi.grein_lines(lambda word: word)` on the actual sources: 28,105 candidates with deliberately permissive lemmatization; reported apparatus key `greinII:1686` is absent. This isolates the boundary repair from incidental dictionary rejection.
- Small fixtures test restoration boundaries, primary-quotation retention, exclusions, mixed-unit cropping, Welsh merging, Edda boundaries, Grein apparatus, and both new locus-scoped repairs (including idempotence and unchanged unrelated rows).
- Focused tests: 18 passed. Final full suite: `UV_CACHE_DIR=/tmp/pie-uv-cache uv run pytest -q` — **2,685 passed in 456.05 seconds**. The temporary UV cache avoids the sandbox-restricted default cache; test selection was unchanged.

## Between-wave builder handoff

`scripts/build_8c_stageCS.py` now accepts `--exclude-read-pivots FILE`, `--out-dir`, `--key`, and `--reader-start`. FILE is a JSON list of passage IDs, slab IDs, or both. Slab IDs resolve only through historical `stageCS/slabs-loci/` copies. Pivot exclusions are applied before the regular, thin, and shuffled-null searches; index membership and IDF remain unchanged. Both floors are frozen over the remaining pivots in the fresh output directory. The excluded IDs are recorded in params.json.

An exclusion rebuild rejects an existing output directory or key, and rejects the historical Stage C-S locations. New slab/bundle IDs retain SS-/BS- and avoid every historical ID in the original loci copies; reader numbering starts at the requested value. The new `stageCS-w*/slabs/` ignore rule was verified with the explicitly permitted `git check-ignore data/research/8c/stageCS-w2/slabs/example.json`.

Read-only validation against the actual assignment resolved RS001–RS012 (12 loci-only slabs) to 3,272 unique pivot passage IDs. The original loci directory reserves 15,260 historical slab/bundle IDs. No retrieval was run for this check.

Lead-only example (not executed here; use a fresh loader-cache directory so the new source repairs are loaded):

```sh
uv run python -I scripts/build_8c_stageCS.py \
  --exclude-read-pivots /path/to/read-slabs.json \
  --out-dir data/research/8c/stageCS-w2 \
  --key data/audits/keys/8c-stageCS-w2-key.json \
  --reader-start 13 --cache-dir /path/to/fresh-wave2-cache
```

No production build was run. `docs/STATUS.md` was not edited; this file is the handoff.
