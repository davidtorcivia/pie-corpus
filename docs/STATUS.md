# Status

**Current state (2026-10-23):** The pipeline runs end to end. Lexicon → engine (98.8% agreement with Wiktionary's tables, Phase A + verbal Phase B) → validator → Tier 1 (17 scholarly works, 99 lines) → Tier 3 realizer. **The Tier 3 pilot is done** (148 sentences; review fixes applied), and **scale-up waits on David's budget choice (question 5)**; a cheaper-model comparison pilot is running. Phases 1–3 are built but not accepted: acceptance waits on the books (LIV², Fortson, M&A), and Tier 1 coverage is 55–82% against a 90% target (question 4).

## Phases

| Phase | State | Acceptance |
|---|---|---|
| 0 Scaffolding & notation | **done** | NFC↔ASCII round-trip on ≥200 tricky forms: **pass** (382 listed forms: 157 hand-written with expected ASCII + 225 generated; plus 5,000 fuzzed; 1,807 tests) |
| 1 Lexicon | **built, acceptance pending** | ≥2,000 entries: 2,226 glossed, 7,401 total ✅ · ≥800 verbal roots: **1,261** (LIV² merged) ✅ · 50-entry M&A spot check: **pass**, no systematic errors (docs/audits/phase1-ma-spotcheck.md) ✅ |
| 2 Morphology engine | **built, acceptance pending books** | Wiktionary regeneration: 14,023/14,197 cells (98.8%) incl. verbal Phase B, 576/615 tables, **0 unexplained** ✅ · PLAN golden paradigms: 11/11 pass, **verified against Fortson/Ringe**; corrections applied (acc. pl. *-ns*, no gen. *-ós*) ✅ |
| 3 Validator | **built; not accepted**: 55–82% on the laryngealist versions after Phase B (docs/audits/tier1-validation.md). The remaining gap is mostly different reconstructions of known lexemes; see question 4 | Tier 1 laryngealist versions ≥90% token coverage, every miss classified |
| 3b Sound-law checker | **built**: initial-position diagnostics for Skt/Gk/Lat/PGmc | full lexicon run: 5,315 checks, 94.8% pass, 277 warnings (docs/soundlaws.md) |
| 4 Tier 1 scholarly | **texts collected**: 17 works (14 fable incl. 5 Kortlandt stages, 3 King) from 22 collected copies; 99 lines, 57 canonical (the rest documentary), 71 with English. Formulas wait on Watkins/West | 200–500 cited lines + adversarial review |
| 5 Tier 2 back-projection | — | ≥300 lines, ≥8 clusters + adversarial review |
| 6 Tier 3 / 3b synthetic | **scaling, connected texts**: 1430 records, 21,795 PIE words: sentence batches b001-b004 (1,000) and connected-text batches t001-t011 (430 texts, 15 genres incl. long epic, everyday life, hymns to individual gods). Calibrated reviews t001-t011: planted errors caught 5/5 by the reviewer in every batch (blind back-translator 2-5/5); real texts judged wrong 0-1/20 in every batch but t002 (3/20, fixed). Each review's systematic findings fixed at the source (engine, lexicon overrides, slices, brief, checker); all batches re-realized at HEAD, 0 rejects |
| 7 Export + benchmark | **scaffolded**: splits, views, task views, leakage guard | splits, task views, bench |
| 8a Formula discovery | **round 2: recall@200 0.50** [0.29, 0.71] on 24 known pairs (round 1: 0.17; shuffled 0.02), from kaikki-etymology mapping (coverage 44% → 65–70%), lexeme counting and exact tests. Still below the bar: only 5/24 known pairs significant in both corpora. Independent review of the 39 (docs/research/8a-candidate-review.md): 4 known, 6 generic, 7 chance, 14 mapping errors (homograph duplicates), 1 plausible new but weak: 'drink and be sated' (píbataṃ ca tṛpṇutáṃ ca ~ πίνοντά τε τερπόμενόν τε); Avestan gives no third-branch support. Next: homograph-safe mapping, relation labels |
| 8b Laryngeal backtest | **inconclusive with available data** (docs/research/8b-backtest.md). First run: pre-registered test underpowered; exploratory signal at laryngeal loss and colouring (+0.27 nats [+0.08, +0.48] beyond baselines), none at length. Two pre-registered replications, both stopped at the power rule: kaikki etymologies (1 matched slot; they repeat Wiktionary) and NIL daughters (46 of 150; colouring 2). A confirmatory test needs a larger independent cognate source; the threshold is not lowered after the fact |

## Dashboard

- **2026-10-23 (night). Wave 2.** Reviews of b001/b002: 4% wrong each, no engine-caused wrong records. Fixes in engine (i-stem *-ēy*/*-eys*, eh₂ LOC *-i*, thematic VOC accent), classifier (reflex evidence for neuter s-stems: Skt *-as*, Gk *-εα*), slices (accent and derived-gloss gates, balanced fill, core nouns, verb valency) and checker. LIV² chunk 11 redone after the image audit; LIV root aorists → 239 new aorist lexemes (usable lexemes 3,719). Pronoun gaps filled from Ringe (60 printed + 84 derived cells). Formulas (Watkins + West, 389) and themes (West, 456). Second book delivery: NIL transcription running (25 chunks of 30 pages, wave 1 of 6 chunks), Beekes/Lundquist–Yates check running. Phase 8: 8a formula search on Rigveda + Homer running; 8b transducer built, design reviewed.

| Metric | Value |
|---|---|
| Lexicon entries | 7,401 total: 885 roots · 893 words · 110 affixes · 5,470 tree derivatives · 22 alt · 21 form-of |
| Glossed entries | 2,226 |
| Verbal roots | 1,261: 116 marked by Wiktionary, 963 backed by LIV² (aspect from LIV's primary stem), 182 still only by the "to …" gloss heuristic |
| LIV² | 1,172 roots transcribed from page images (`data/lexicon/liv2.jsonl`, facts only): 662 matched by form, 17 by generic-H key + gloss, 493 new (51 linked `possible_alias_of` a Wiktionary root, not merged). Image audit of 22 pages (docs/audits/liv2-image-audit.md): no errors in first-stem labels, glosses or IEW; chunk 11 re-transcribed after false homograph numbers and missing arcs; placeholder headwords (R, K, T, N) expanded and kept as uncertain. Known gap: 8 roots with LIV's voiceless aspirates (*spʰerH-*) are outside our inventory. 9 OCR-check flags, all OCR-side |
| Wiktionary paradigms (clean) | 625 (90 dropped as module-corrupted, 1 with a non-canonical cell) |
| Normalization rejects | 67 (alternative lists, queries, placeholders) |
| Root coverage in corpus | — |
| Engine agreement with Wiktionary tables | see the cross-check row below |
| Inflectable lexemes (Layer 2) | 4,476 with a spec; **3,468 usable** for Tier 3 (table or rule backtested ≥85%) |
| Roots with ≥1 usable lexeme | 821/885 (93%); verbal 691/730 |
| Records per tier (1 / 2 / 3 / 3b) | 99 (57 with canonical `pie`; 71 with English) / 0 / 148 (pilot, not in train) / 0 |
| Plannable vocabulary for Tier 3 | 3,371 lexemes (853 Wiktionary-glossed + 2,518 with derived glosses), 816/885 roots |
| Tier 1 validator coverage, laryngealist versions | Byrd King 81.8%, Byrd fable 75.4%, Adams 65.2%, Lühr 59.3%, Hamp/Sen 55.0%. Precision: the fuzzy hits checked are right except for 2 listed lexemes |
| Engine cross-check (Phase A + verbal Phase B) | 14,023/14,197 cells (98.8%), 0 unexplained |
| Tokens per tier | — |
| Neologism share of training tokens | — (cap 10–15%) |
| Validator pass rate | — |
| Sound-law mismatch rate | 5.2% of 5,315 initial-position checks (277 warnings) |
| Formulas | 389 from Watkins (1995: 27 phrases, 81 schemas) and West (2007: 21 phrases, 62 lexical, 198 attested-only), `data/formulas/formulas.jsonl` (no book quotes); 7 complete phrases are Tier 1 records (`provenance: formulaic`, `corpus/tier1/formulas.jsonl`), validator coverage 55%: both books often omit initial laryngeals (*ógʷʰim*, *wésu*) |
| NIL | 207 roots, 3,044 formations transcribed from page images (all 737 pages; 96% agreement between overlapping transcriptions). Merge **failed review** (docs/audits/nil-merge-review.md: ~25% of usable new lexemes wrong; 13 glosses on the wrong word); held out of slices while the fixes (homograph linking, palatal-preserving keys, gender from evidence, comparatives, duplicates, attestation gate) are applied and re-reviewed |
| Themes | 456 motifs from West (2007) in 12 clusters (his chapters: Poet and Poesy … Arms and the Man), `data/themes/themes.jsonl` |
| Genre × theme grid fill | — |

## Need from David

**Books received 2026-10-23** (in `raw/books/`, gitignored; text extracted by `scripts/extract_books.py`): Fortson, Ringe, Watkins, West, Mallory & Adams (EPUB/PDF, usable text layers); LIV² (read from the DjVu page images by 11 transcription agents; merged 2026-10-23). **Second delivery (2026-10-23, ~05:00):** NIL (Wodtko et al. 2008; OCR poor, so read from page images: pilot on 30 pages running), Beekes 2011 and the Klein–Joseph–Fritz *Handbook* (2018, incl. Lundquist & Yates on morphology: paradigm check running, same method as Fortson), Clackson 2007 (clean text; for the variants layer). In progress: Fortson paradigm verification, Watkins and West formulas and themes, the M&A 50-entry spot check.

## Phase 1 notes

- **The source is clean.** Only 4 of 1,931 headwords are outside the inventory. Normalization fired 14 times (3 homoglyphs, 6 laryngeal rings, 5 dot-below syllabics). The `\w` escape occurs in 17 forms.
- **Wiktionary's declension module corrupts some tables.** Where a stem template has parentheses or Ø, the dual `-h₁` becomes `é₁`/`Ø₁`. Those 90 tables are excluded at the source.
- **Wiktionary etymon ids can't disambiguate homographs.** kaikki copies them across sibling sections, so 8 homograph sets collided. Root ids therefore carry a gloss tag on every id (`pie-root-men-think`, `pie-root-men-stay`) and persist in a committed registry. Rebuilds are idempotent.
- **Provisional review** (subagent, knowledge-only, 50 entries): 20 ok, 26 questionable, 4 wrong. The triage is in `docs/audits/phase1-lexicon-provisional-review.md`. It found **one real builder bug**: same-form derivatives under different homograph roots were merged, e.g. two *kretós*. Fixing it split 140 homonyms. Duplicate reflexes and unflagged loans are fixed as well. The other 3 "wrong" links are Wiktionary's own placements, logged as disputed. The id registry was reset once for this fix; safe because nothing references ids yet.
- **Gaps:** 344 words/derivatives with no root link (mostly pronouns, particles, opaque nouns); 58 etymon parts that point at ambiguous homographs.

## Decisions recorded before measurement

- **Phase 3 acceptance scope** (written 2026-10-23, before any Tier 1 text was validated): the PLAN's "≥90% token coverage on Tier 1" applies to the **laryngealist versions**: Byrd, Kortlandt, Lühr, Adams/Mallory, and any later version with h₁ h₂ h₃. Schleicher 1868, Hirt 1939 and the other pre-laryngeal versions are documentary. They are kept for the parallel-reconstruction set, measured and reported, but not held to 90%: they score near zero by construction.
- **The lexicon id registry is frozen.** Tier 1 records are the first data that reference lexicon ids, so no rebuild may reset `data/lexicon/id_registry.jsonl` from here on. A new dump mints new ids and reports stale ones; it never renames existing ones.
- **No formulas, glosses or reconstructions from memory.** The Watkins/West formulas wait for the books. Interlinear glosses come from validator lemmatization plus the published translation, never from a subagent.

## Open questions for David

All in one place. None of these block work in progress; each one has a default that I'm using until you decide.

1. **Eval contamination via formulas.** The fixed decision is "eval = all of Tier 1 + a held-out slice of Tier 2". But Tier 1 includes the Watkins/West formulas, and Tiers 2–3 are built *from* them, so eval would leak into training. **Recommendation:** eval = Tier 1 *texts* (fable and King versions, held out whole) + held-out Tier 2, with the formula records kept in training. *Default until you decide:* records are tagged so either split can be cut later.
2. **Phase 1 targets.**
   - (a) May the "≥2,000 entries" target be met by *glossed* entries (2,226)? The 5,470 unglossed tree derivatives are a separate, lower-confidence kind.
   - (b) ~~Verbal roots are 730, against a target of 800.~~ **Resolved:** LIV² merged, 1,253 verbal roots. The options are **LIV²** (authoritative; also supplies aspect for the 614 roots classified by gloss), or a harvest from the kaikki daughter-language dumps (more roots, no aspect). *Default:* waiting for LIV².
3. ~~**Paradigm convention for corpus text.**~~ **Settled by measurement:** with the index built under one convention alone, `handbook` beats `wiktionary` on every laryngealist Tier 1 text (Byrd 67.2 vs 60.7%; Lühr 53.7 vs 51.9; Adams 47.0 vs 43.9; Byrd King 63.6 vs 60.0; Hamp/Sen tie). The default stays `handbook`. Original note: I read "Wiktionary/LIV conventions are canonical" (PLAN §1) as being about *notation*, not paradigm reconstructions, so corpus text defaults to the **handbook** forms (contracted thematic *-ōs/-ōy/-ōd*, as in the Tier 1 texts). Wiktionary-convention forms are kept as alternatives in every cell. The tiebreaker will be Phase 3 validator coverage on Tier 1 texts under each convention. Tell me if you meant the stricter reading.
4. **Phase 3's 90% target vs. how scholars differ.** After Phase B, what's left is mostly *different reconstructions of the same word* (Byrd's *pter* vs Wiktionary *ph₂tḗr*, Byrd *km̥tá* vs *ḱm̥tá*, Adams's and Lühr's "man" and "wool"), plus theonyms (*Wérunos*). These aren't engine errors. Closing them would mean either counting fuzzy near-misses (rejected: they pick wrong lexemes) or adding each scholar's variants to the lexicon from these very texts (circular, since they're the measurement). **My proposal:** add a `variants` layer filled from *other* sources (M&A, Fortson, LIV² when they arrive) and measure leave-one-text-out, and keep 90% as the target for that measurement. Until then, report the current numbers as the Phase A+B baseline.
5. **Tier 3 scale-up: model and budget.** Two 150-plan pilots with the same 50-record review:

   | | Pilot 1 (current model) | Pilot 2 (cheaper model, Sonnet) |
   |---|---|---|
   | Review ok / minor / wrong | 31 / 14 / 5 (*before* engine fixes) | 40 / 9 / 1 (after fixes) |
   | Planner-caused meaning / syntax issues | 3 / 3 | 3 / 0 |
   | Distinct lexemes / roots | 233 / 123 | 155 / 78 |
   | Planner tokens for 150 plans | 134k | 149k |
   | Plan reject rate (after the new checks) | 3.3% | 5.3% |

   The cheaper planner is **no worse on the planner's own errors, but less diverse**, at about the same token count (so the saving is the per-token price). Sentences average ~4.5 words, so **1,000 sentences ≈ 1M planner tokens** either way.

   **Recommendation:** scale with the cheaper model plus diversity controls (rotating slices, the new attestation ranking, a per-lexeme usage cap, and longer 2–3-clause plans to amortize overhead). Then a 50-record review by the stronger model per ~2,000 sentences (~130k tokens each) and automatic gates on every batch (reject rate, distinct roots, exact validation). A first scaled batch of **10,000 sentences ≈ 10M planner tokens + ~0.7M review tokens**, yielding ~45k PIE words. The PLAN's 1–10M-token target is a large multiple of that, so please pick a budget, or a first-batch size, before I go further.
6. ~~**GitHub.**~~ **Done:** public at https://github.com/davidtorcivia/pie-corpus (2026-10-23). Still open: a **code license** (none chosen; the data files are CC BY-SA 4.0 because they derive from Wiktionary; see NOTICE.md).

## IDEAS.md disposition

Everything in IDEAS.md is folded into PLAN.md, and nothing is rejected outright. These parts were **modified**:

- **Sound-law checker (2).** (a) The Germanic target is **Proto-Germanic**, not Gothic. Wiktionary descendants include PGmc reconstructions, and Gothic needs a further layer of rules; Gothic can be added later. (b) **Inflected forms are checked only against a curated list of regular pairs.** The IDEAS example itself shows why: Gk φέρει is not the regular outcome of *bʰéreti* (the regular one would be *φέρετι), and Lat. *fert* continues an athematic form. A blanket inflected-form check would mostly measure analogy, not engine errors. (c) **Brugmann's law** goes behind a flag with separate counts, because it is contested.
- **Task-format eval (4).** Cognate→PIE eval holds out **whole root families**, otherwise derivatives in training leak the answer. Paradigm exact-match is scored against the golden scholarly paradigms (Phase 2), not only engine output, so the benchmark doesn't just reward imitating our own engine.
- **Modern PIE (5).** Added as Tier 3b, as proposed, with one extra guard: neologisms are **never** loaded into the validator lexicon for Tiers 1–3, so a coinage can't leak into the "plausible archaic" tiers as if it were a real root.
- **Meter (6).** Accepted. It needs one deterministic syllabifier with documented choices (laryngeal vocalization, Sievers' law as a flag), because syllable counts in PIE depend on those choices.
- **Dashboard (7).** The metrics are in STATUS.md now. The HTML Artifact version is deferred until there is data to show (Phase 1+).

## Log

- **2026-10-23. Tier 3 pilot.** Built the realizer and plan checker (an unattached slot is an error, never a silent drop), lexicon slices, and derived glosses (+2,518 plannable lexemes). A planner subagent wrote 150 plans: 0 rejects at the time, all validating at the exact tier. The adversarial review on 50 came back 31 ok / 14 minor / 5 wrong; the systematic causes were fixed in the engine and classifier (s-stem routing, thematic aorist, handbook vocative, *-dʰí* imperative, *-i* locative, prohibitive on perfects). 2 plans are now rejected (1.3%).

- **2026-10-23. Phase 3b.** The forward sound-law checker uses word-initial diagnostic correspondences (satem/centum, labiovelars, Grimm, aspirates, Grassmann, s-mobile, Greek prothesis and coloring), skipping loans, analogical forms and prefixed daughter forms: 94.8% of 5,315 checks pass. The Tier 3 pilot is running: the realizer is built, and a planner subagent is writing 150 plans.

- **2026-10-23. Phase B (verbal).** Built middle, subjunctive, optative, participles and middle imperatives, cross-checked at 98.8% over 14,197 cells. Validator: written voicing assimilation (*h₃rḗḱs* = *h₃rḗǵs*), which took Byrd's King and the God from 69% to 82%. Relative pronoun *h₁yó-* added; *-tōr* agent rule. The audit is now regenerated by `scripts/tier1_audit.py`.

- **2026-10-23. Tier 1 collected and validated.** 5 collection subagents; every source verified independently (re-fetch, sha256, page image), with primary and secondary copies agreeing letter for letter. 7 new notation rules plus per-source profiles. Validator additions: decolored and glide-spelling tiers, table-cell index, exact-only matching for short tokens (from a precision check: *tu* "then" ≠ *tú*). Engine: handbook variants *-ed/-ond* and *-bʰyos*, as attested by Byrd and Adams. Classifier bug fixed: numerals in *-os* now decline. The convention tiebreaker was measured, and handbook wins.

- **2026-10-23. Phase 3 (built).** `pie/validate.py` builds a form index of ~90k forms (every cell of every spec, both conventions and alternatives, closed classes, lexicon lemmas; 3.5 s) and does tiered lookup (exact → no accent → no length → generic H). It splits off clitics and the augment, and gives every miss one class (notation / phase-b:<class> / engine-gap / pre-laryngeal / variant-of-known-lexeme / lexicon-gap). A test caught the accent-stripping tiers deleting the palatal acute of ḱ; fixed. Five collection subagents are gathering the Tier 1 texts in parallel.

- **2026-10-23. Phase 2 (Layer 2).** `pie/classify.py` derives a spec from Wiktionary tables or, failing that, from 17 lemma-shape rules with `zero_grade()`. Every rule is backtested against the hidden tables; the thematic present and the perfect reach 100%. A usability threshold of 85% gates Tier 3. Output: `data/morph/inflection_specs.jsonl`, `classify_report.json`.

- **2026-10-23. Phase 2 (Layer 1).** Built `pie/phon.py` (segments; junction syllabification; Szemerényi, Stang, boukólos; Wiktionary-only Pinault and perfect laryngeal loss), `pie/morph.py` (thematic, eh₂, athematic in 4 accent classes, devi feminines, adjectives, thematic/athematic presents, aorists, perfects; `handbook` and `wiktionary` conventions with alternatives), the cross-check harness, and the mismatch classifier. Agreement went 89.6% → 98.9% as each mismatch class was triaged. Bugs found that way include Stang's law never firing after syllabification. Also wrote 11 golden paradigms (flagged unverified) and closed-class hand tables. 1,896 tests. Details in `docs/morphology.md`.

- **2026-10-23. Phase 1 (built).** Found the dump via the kaikki.org index and logged it in `raw/MANIFEST.md`. Built `pie/lexicon.py` and `scripts/build_lexicon.py`, wrote the schema in `docs/lexicon.md`, and added two normalizer rules (G-HOMOGLYPH, G-LAR-RING). Lexicon tests cover form parsing, id/link integrity, parent/child symmetry and paradigm cleanliness (1,838 tests in total). A provisional reviewer subagent is auditing a stratified 50-entry sample.

- **2026-10-23. Phase 0.** Set up git, the uv project (Python 3.14), and the directory layout. Built `pie/translit.py` (strict, closed-inventory, reversible), `pie/notation.py` (19 named normalization rules, 4 profiles, applied rules reported per call), and the `scripts/translit.py` CLI, and wrote `docs/notation.md`. The tests caught two real bugs, both fixed: a fixture typed with acute before macron (the strict check correctly rejected it), and `G-CASE` lowercasing a word-final generic `H` (`"" in "₁₂₃"` is True in Python, which is exactly the silent laryngeal corruption the rule log warns about).
