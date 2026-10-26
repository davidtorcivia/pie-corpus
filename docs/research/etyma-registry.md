# Research etymon registry

David’s rule (2026-10-25): **“if it's correct and known we should add to our lexicon”.** A missing etymon becomes a **production lexicon candidate for the normal pipeline** when at least two standard sources agree on its reconstruction and sense. It remains **registry-only** when it is Kloekhorst-only, doubtful, or disputed. Two agreeing sources do not override an explicit scholarly dispute. This review submits candidates; it does not edit or activate the production lexicon.

The registry provides opt-in retrieval targets, not inflectable lexemes, generation candidates, export tasks, evaluation holdouts, or Tier 2 secure evidence. Candidates are held separately from the registry, with `scope: research_only` until the normal pipeline reviews and admits them.

## 2026-10-25 Hittite review

**500 historical unmapped content lemmas, 51,554 tokens; 110 distinct missing etyma/alternative reconstructions: 8 lexicon candidates and 102 registry-only records.** The latter comprise 28 roots, 51 nouns, 7 adjectives and 16 other formations; candidates comprise 5 roots, 2 nouns and 1 adjective. These are etymon counts, not coverage gains. Alternative reconstructions have separate records; repeated daughter lemmas do not multiply etymon counts.

The population is the historical top 500 underlying the main checkout’s `docs/research/mapping-precision-hittite.md`, rather than a silently changed top 500 after its subsequent mapping additions. The main `pie/hittite_mapping.py` and `hit-reviewed-top200.json` were read without editing. The 23 later main-tier top-200 additions were removed from the mapped set to reproduce the report baseline. The first 200 ranks match the frozen reviewed report. Input paths and SHA-256 hashes are in the audit manifest.

| Decision on a lemma | Count |
|---|---:|
| Linked to one or more missing-etymon records | 155 |
| Existing production family, including doubtful mapping equations | 64 |
| Explicitly excluded after source review | 23 |
| No further absent EDHIL PIE etymon established for the exact lemma/sense | 258 |

The last category includes cultural terms, daughter-language derivatives and unresolved dictionary-headword matches. It is **not a claim that those words have no etymology**. A failure to match a damaged text layer is not evidence of PIE absence. The audit records all 500 lemmas and preserves the main report’s prior top-200 decisions alongside the new decisions.

| Candidate | Sense | Agreeing sources, printed pages |
|---|---|---|
| *h₂let- | call; summon | EDHIL 277–278; Kroonen 328 |
| *h₁reh₁- | ask; consult an oracle | EDHIL 202; LIV² 251 |
| *h₂et- | pierce; strike | EDHIL 330–331, 333, 335–336; LIV² 274 |
| *merǵ- | divide; separate into portions | EDHIL 558–559; de Vaan 365; Kroonen 355 |
| *mewg- | make a lowing noise; invoke by noise | EDHIL 585–586; de Vaan 392 |
| *ǵenh₁-su- | abdomen; lap | EDHIL 468–469; de Vaan 260 |
| *dʰn̥gʷ-(e)i- | dark; black | EDHIL 829; Kroonen 96 |
| *ǵʰéw-t- | wall; embankment | EDHIL 498–499; de Vaan 249 |

The asking root is distinct from production’s rowing/resting homographs; piercing is distinct from its grass/particle homographs. De Vaan explicitly reconstructs the full lap noun, so its evidence counts for that noun, not merely for the already-present birth root. The old `research-etymon-h2let-call` id is retired, never reused: its six proposed lemma keys now accompany the lexicon candidate. The time noun *méih₂-ur remains registry-only, and its one research mapping proposal remains in the proposal file.

Examples retained only in the registry include doubtful *bʰers- “break”, mechanical *HH-ye/o- “make”, *h₁eNs- “remain”, the two alternative speech formations, and exact nominal formations whose root alone is corroborated. The double-h₃ name reconstruction has EDHIL **and Beekes** support but is explicitly rejected by Matasović; it therefore remains registry-only. Related forms, homographs, bibliographic mentions and possible borrowings are not counted as agreeing reconstructions.

The review also inspected discussions where the parser found no PIE line: for example, illness *(H)in-on-*, the alternatives *h₂es- / h₂eNs-* “open”, *sup-(e)i-* “sacred”, and mechanical *Trewp-* “collect”. False inherited lines were rejected: riverbank is not the following speech particle’s *werh₁-*, horn is not the following ending *-soi*, and “play” is not the following daughter noun. The announcement noun already exists as `pie-lex-h2lewghos`; it was not added again. Existing “wash” and “know” families likewise require mapping review rather than duplicate roots.

## Files and source review

- `data/research/formulas/etyma.jsonl`: the 102 registry-only records; explicitly loaded by `pie.etyma.load_registry`.
- `data/research/formulas/lexicon-candidates-hittite.jsonl`: the 8 candidates with form, sense, source pages, `proposed_kind`, agreement rationale and lemma ranks. No automatic production reader is introduced.
- `data/research/formulas/hittite-etyma-inventory.jsonl`: one classification and rationale per missing etymon, with related production ids where reviewed.
- `data/research/formulas/hittite-top500-etyma-audit.jsonl`: one decision per ranked lemma, linked to the inventory.
- `data/research/formulas/hittite-etyma-source-review.jsonl`: source support, adjudicated comparisons/disagreements and text-search metadata for every inventory record.
- `data/research/formulas/hittite-etyma-audit.json`: population definition, counts and input hashes.
- `data/research/formulas/etyma-hittite-proposals.jsonl`: one remaining time-noun research mapping proposal; outside `mapping/` discovery.
- `pie/etyma.py`: registry schema and opt-in grouping adapter; `pie/research_scope.py`: scope classification without registry/raw I/O.

The source screen covers local text in LIV², the 2026-10-21 kaikki PIE dump, Mallory–Adams, Derksen Baltic and Slavic, de Vaan, Beekes, Kroonen, Matasović and Martirosyan. Queries and matching file paths are discovery metadata, **not votes**. Reviewed supporting citations and explicit comparisons are separately recorded. A zero literal-search result does not prove absence, especially with OCR and private-font glyph damage. Kaikki homographs were checked against their senses, not accepted from spelling alone. A bibliography or index occurrence does not provide independent support.

Only source reconstruction strings, citation metadata and editorial notes are stored here. Raw files were read as text and left unchanged; no book running text is copied into the repository. Printed pages and raw filenames are recorded separately: EDHIL files use printed page +8, the cited LIV² files +5, de Vaan +14 and the cited Kroonen entries +40. Beekes text files can contain two printed pages; their file numbers are not page numbers. Mallory–Adams and other unpaginated text comparisons use section/headword locators where a printed page could not be verified.

## Schema and editorial rules

Required registry fields: `id`, `kind`, `form`, `source_forms`, `sense`, `sources`, `uncertainty`, `scope`. Unknown fields raise. Optional fields are `homograph`, `note`, and `cross_link` with an existing `root_id` and explanatory `note`.

- Ids are immutable ASCII `research-etymon-<slug>` identifiers. Never recycle a retired id.
- Kinds are `root`, `noun`, `adj`, or `other`.
- Canonical forms are nonempty NFC PIE reconstructions without an editorial asterisk, daughter `ḫ`, question marks or control glyphs. Explicit uncertainty slots (`H`, `T`, `K`, etc.) are research notation, not resolved phonemes.
- `source_forms` preserve segmentation, accent, grade and source doubt markers. **Doubtful source forms are permitted only with a nonempty uncertainty note.** This supersedes the first batch’s exclusion of question-marked forms: the registry is now their appropriate destination, while lexicon candidates remain separately screened.
- Each `sources` object names its source, positive printed page and raw text path. The registry currently validates EDHIL, LIV² and Beekes; candidate citations also include de Vaan and Kroonen.
- `scope` is always `research_only`. Canonical spelling agreement with a production entry is allowed for distinct homographs; ids and senses must remain distinct.
- Alternatives have separate entries unless the source identifies one etymon. Inflection/ablaut does not multiply records; different nominal suffixes can. Cross-links never merge groups or confer secure status.

## Resolver and scope guarantees


Research targets use the existing `lex_id` list in mapping/override rows. `pie.mapping` remains the sole resolution authority: lemma decisions precede path decisions, and removals cannot be restored by automatic routes. Its existing rejection of unknown override-file keys is retained and tested.

`Decision.scope` and `Resolved.scope` are explicit fields. They infer research scope from the reserved id prefix, also preserve an explicit `scope: research_only` on a row pointing at a production id, and reject unknown scope labels. An explicit production label cannot downgrade a research id. Mixed production/research mappings are conservatively research-only as a whole. For id-only legacy retrieval APIs, the reserved namespace retains classification; consumers needing row metadata must use the resolver's `Resolved` objects. Cross-links are never substituted into those id-only APIs.

`research_group_map` extends a copy of the ordinary `pie.formula_search.group_map` with `id → id` for each research etymon. Ordinary retrieval remains unchanged; no consumer has been silently opted in. Do not pass registry rows as lexicon entries or replace the ordinary group-map function globally.

Tier 2 enforcement in `pie/tier2_secure.py`:

- `build_population` retains research scope in its resolved audit population but excludes research rows from evidence tables and installs blocking decisions for their words.
- `Gov` caps all evidence routes to no evidence when a governing decision is research-only: direct overrides, automatic tables, dictionary/kaikki paths, lexicon reflexes, sibling/root matches, inflected forms and compounds.
- External dictionary paths that encounter a research decision install that cap even without a corpus table row. Lemma decisions remain authoritative.
- `_path_decided` excludes research decisions from external table evidence. `level_of` rejects research targets before root/sibling matching. Direct table fixtures and explicitly scoped entries are also rejected.

Production enforcement:

- No builder (`scripts/build_lexicon.py`, `scripts/classify_lexicon.py`, `pie/liv.py`) reads or imports the registry. No LIV integration or root-aorist creation is invoked. Production data files are untouched.
- `Lexicon` rejects research entries/specs at construction, covering realization and generation. The scope helper it imports performs no file reads.
- `cognate_tasks` additionally rejects research entries rather than relying on usable-spec gates. `record_tasks` rejects research records/tokens; `eval_root` rejects research ids before partitioning.
- No holdout list, paradigm, production root group or existing mapping table is extended.

## Adding or promoting an entry

1. Check production forms, variants, senses and homographs. A surface grade or a productive daughter derivative is not automatically a missing PIE etymon.
2. Read the source entry and discussion as text; verify doubt markers, alternatives, sense and printed pages. Do not execute raw files or copy book prose.
3. Seek a second standard source at the same reconstruction level. Record disagreements and distinguish inherited cognates from possible loans. A known root does not by itself corroborate every nominal formation built on it.
4. Put agreed, non-disputed missing etyma in the candidate file for the normal production pipeline. Keep EDHIL-only, doubtful and disputed etyma in the registry with a reason. Do not activate either class through mapping overrides here.
5. Validate schema, references, candidate evidence, scope isolation and the full test suite; verify production hashes. No lexicon build is needed or authorized by this review.

## Validation and limits

The tests cover qualified doubtful forms, rejection of damaged control glyphs, stable ids, independent groups, cross-links, mapping/fallback/compound exclusion, production rejection, retirement of the call proposals, all 500 audit ranks, inventory references and the candidates’ two-source requirement. Tests do not read raw corpora. Source-search results are not an independent adjudication of every possible cognate; editorial and OCR limitations remain visible in the records.

`.venv/bin/python -m pytest -q` completed with **2,480 passed, 1 xfailed** in 337.52 seconds. The 25 registry/isolation tests also passed on the final data. All 226 production files under `data/lexicon`, `data/morph`, `data/generation` and `export` retained identical paths and SHA-256 hashes. All 110 inventory records have consistent source-review records covering ten local collections. The earlier first-batch export comparison (14 byte-identical artifacts) is historical and was not rerun as part of this data review.
