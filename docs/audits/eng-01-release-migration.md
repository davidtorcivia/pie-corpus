# ENG-01 release eligibility migration — 2026-10-25

Inspection of the current implementation confirmed ENG-01 remained open: all
non-pilot JSONL batches entered export, including t022; the producer returned 0
on FAIL. No git commands were used. Existing root-family leakage protection was
already implemented and is preserved, now operating on admitted records only.

## Policy and evidence

Every Tier 3 batch requires both PASS gates and approved review. The shared
`pie.batch_release.batch_eligibility` decision fails closed on missing, malformed,
inconsistent, or stale evidence. `data/generation/releases/<batch>.json` binds
review status to SHA-256 hashes of records, source plans, and the unchanged gate
report. A newly realized candidate always resets review to pending, even if its
gates pass. Review approval is a separate, evidence-backed decision; successful
realization never supplies approval. To approve a future reviewed candidate,
record its review/remediation evidence and rationale with `release_metadata`,
then write that metadata to its release file. Do not refresh hashes on an old
approval without reviewing the changed candidate.

Historical decisions below use the individual review's findings together with
the STATUS remediation/release account. These migrate the project's historical
release decisions; they do not upgrade provisional, knowledge-based reviews to
source-verified scholarly acceptance. Each release file records its evidence
locations and rationale. Gate reports, including t022's thresholds, are unchanged.

| Batches | Review status | Evidence and interpretation |
|---|---|---|
| b001–b004 | approved | Individual `tier3-bNNN-review.md` verdicts explicitly pass scaling; STATUS line 16 records findings fixed and re-realization; lines 111–112 document subsequent fixes/regeneration. |
| t001–t015 | approved | STATUS line 16 explicitly records calibrated reviews, fixed findings, and re-realization; individual reviews document findings, and lines 111–112 document subsequent fixes/regeneration. |
| t016–t017 | approved | Individual reviews document assessment and correctable causes. STATUS lines 111–112 consolidate validity fixes and merged-engine regeneration of the 25 historical batches (b001–b004 + t001–t021), separately identifying the new unreviewed t022. This combined historical release account supplies the migration basis; audit existence alone does not. |
| t018–t021 | approved | STATUS line 119 explicitly records their review outcomes; lines 111–112 record fixes/regeneration, alongside individual review findings. |
| t022 | pending | STATUS lines 112–115 explicitly say unreviewed, redo open; report FAIL (ordinary lexeme use 18, cap 8). |
| t023 | approved | Individual review plus STATUS line 112 explicitly records the review and fixes (2/20 real wrong fixed); report PASS. |
| pilot, pilot2 | pending | Historical provisional reviews exist, but current reports FAIL; no release approval for failed candidates is inferred. Already excluded by default pilot policy. |

Only batches with current candidate files receive release metadata. Historical
`*-initial` gate reports are drafts, not releases; they remain untouched. If a
draft candidate is restored, missing release metadata excludes it explicitly.

## Export and producer contracts

`uv run python -I scripts/export.py` applies admission before training records,
tasks, seen roots, and leakage checks. `export/summary.json` lists every batch's
gate, review, eligibility, admission, and reasons. `--experimental-batches`
explicitly bypasses eligibility and records that choice without altering the
candidate or review metadata. Pilots also require `--include-pilot`.

`uv run python -I scripts/realize_plans.py ... --batch NAME` returns 1 on gate
FAIL and 0 on PASS. Both retain candidate records, plans, rejects, gate reports,
and pending release metadata. `--engine-version` supplies engine provenance
without executing git; omitted provenance is explicitly `unknown`.

## Rebuild comparison

The pre-change `build()` result was captured immediately before implementation;
the default export was then rebuilt with `scripts/export.py`.

| View | Before | After |
|---|---:|---:|
| Training records | 1,968 | 1,928 |
| Training tasks | 11,661 | 11,541 |
| Evaluation records | 104 | 104 |
| Evaluation tasks | 333 | 333 |
| Accent-specified evaluation tasks | 326 | 326 |

Exactly the 40 t022 records and their 120 tasks disappeared; t023 remains
admitted. Task identity comparison (source ID, task, input) found no additions,
no other removals, and no changed train/evaluation membership. Evaluation record
IDs and root-family holdout task membership are unchanged in this rebuild.
These are observed deltas, not permanent dataset-size assertions.

The admitted sentence population still contains the same 402 root families.
One contamination annotation changes: `t2-poetics-gifts-013` now has
`seen_in_train: false` (previously true), propagated to its evaluation tasks,
because its formula no longer occurs inside an admitted training text. This is
an annotation change, not a split-membership change.

## Validation

Focused eligibility/export tests: 31 passed. Final full suite:
`uv run pytest -q` — **2,490 passed in 343.59s**. Commands used a temporary
`UV_CACHE_DIR` because the default user cache is outside the writable sandbox.

Concurrent changes caused two earlier full-run failures outside ENG-01. The
Germanic table refresh resolved its regression without edits here. The Hittite
parser's new dictionary-page cutoff required a one-line fixture filename update
in `tests/test_formula_search_multi.py`: use `KH_FIRST_FILE` rather than a
front-matter page. All parser assertions were preserved, and no protected
Hittite implementation or mapping files were edited. The final full run includes
that fixture correction and passes.
