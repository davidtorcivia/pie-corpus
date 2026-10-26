# Completed Stage C Celtic replay (SCI-01 / scorer part of SCI-02)

This is a retrospective reanalysis dated 2026-10-25, not a new experiment or
amendment to an unread endpoint. The reviewed source commit and current HEAD at
inspection were both `8d316864894aaee8ad814af13b01d663f343a3b5`. Its scorer still
used unrestricted shuffling and the reader/confidence exclusion shortcut.
`results-celtic.json` remains the historical result. `results-celtic-v2.json`
contains corrected results and a separately labelled contribution sensitivity.
No original verdict, grade, claim or exclusion has been revised.

## Public replay

From the repository root (Python standard library only):

```sh
uv run python -I scripts/score_8c.py \
  --ledger data/research/8c/stageC/ledger-celtic.jsonl \
  --output /tmp/results-celtic-v2.json \
  --run-id stageC-celtic-reanalysis-v2 --analysis-date 2026-10-25
uv run pytest -q tests/test_score_8c.py
```

The scorer and ledger can also be copied into an otherwise empty directory.
Neither keys, verdict files, raw corpora nor other project modules are loaded.
If the default uv cache is inaccessible, set `UV_CACHE_DIR=/tmp/pie-uv-cache`.
Use `--method monte-carlo --seed 0 --permutations 10000` for conditional rejection
sampling instead of the default exact calculation. Output records the ledger and
scorer SHA-256, analysis ID/date, method, seed, requested count and actual count.
Exact output uses zero permutations and no Monte Carlo correction; sampled
output uses `(ge+1)/(N+1)` and records attempts including condition failures.

## Assignment, statistic and conditioning

`build_8c_stageC.build()` draws one decoy per consecutive five-bundle block from
Stage B `doc_order`: corpus position, then pivot unit index. `pack_slabs` traverses
that same order. The original key's slab and entry insertion order preserves it;
public slab bundle arrays are sorted by opaque ID and **do not** preserve it.
The export follows key insertion order and checks pivot/partner identifiers
against the loci-only slabs. Never sort bundle IDs to reconstruct blocks.

A final block of size m < 5 has a decoy with probability m/5, uniformly among its
members. Equivalently there are five equal-probability slots: one for each
member, and 5-m empty slots. The full original build reports 4,946 intended and
4,946 successful decoys. Thus intended assignment equals shown kind here; the
exporter and scorer reject unknown/failed construction instead of assuming that
future failures have the same randomization law.

The public ledger includes every original block touched by the 28 completed
slabs, including outside-scope members. There are 4,765 read bundles. Celtic
selection contains 4,687, ending two members into block 937 (zero-based): all
five members remain in the mechanism. Irrelevant independent blocks outside the
ledger marginalize out. The ledger records the full original population size.

Each eligible claim has weight one, divided equally among its cited bundles
inside the analysis scope, as in the original scorer. The statistic is mean
real weight minus mean decoy weight, tested in the upper tail, holding claims,
grades, scope and eligibility fixed. This is an assignment-based reference test
of the frozen claims, not a model of how readers would respond to new passages.

Every scope (Celtic, all read, each Celtic date/genre stratum) **conditions on its
observed selected decoy count**. This is explicit additional conditioning, not
unrestricted shuffling. Complete original blocks generate assignments before
scope selection. Conditional draws preserve outside members' probability mass;
no permutation is removed for an inconvenient statistic. Zero observed real or
decoy denominator returns an explicitly undefined p-value. Under this condition
the upper-tail statistic is equivalent to decoy weight <= observed decoy weight.

Exact mode convolves integer multiplicities of the five slots per block,
tracking selected decoy count and rational weight. It is equivalent to enumerating
all legal assignments, including repeated empty slots of a partial block. Common
multiplicity factors for deterministic blocks are cancelled; `exact_tail` and
`exact_total` are counts in that reduced enumeration, not the full 5^B space.
Tests independently enumerate a tiny cut-block/partial-block fixture.

Corrected Celtic p-values: accepted 1; accepted+weak 0.24601572671488;
all claims 0.041274589864925125. Historical unrestricted Monte Carlo values were
1, 0.25177482251774824 and 0.042995700429957005 respectively. Weights remain
0/0, 6.25/0.75 and 14.25/0.75 real/decoy. The controls compare targeted retrieval
with the specified decoy construction, not false historical discoveries among
equally plausible root-matched candidates.

## Eligibility and contribution sensitivity

Each claim carries an explicit original eligibility decision with a reason.
C0011 remains excluded: Vedic and Avestan both belong to the registered
Indo-Iranian branch. Reader ID and confidence are not eligibility inputs.

Per-anchor contribution coding is a retrospective interpretation of the original
verdict reasons, with an evidence pointer and short text-free rationale. States
are `contributes`, `does not contribute`, and `uncertain`; missing support for a
contribution decision stays uncertain. Contribution to a proposed comparison
is distinct from acceptance as inherited phraseology. Genericity or possible
borrowing does not itself erase a stated contribution. The `verified` flag
records explicit source checking available in the verdict; it is not a new
verification and is not a full SCI-03 compliance assessment.

The sensitivity requires original eligibility, a verified contributing Celtic
anchor, and a contributing anchor from another registered branch. Uncertain
anchors do not satisfy it. C0009's Irish anchor is explicitly not a witness;
C0014's Irish contribution to the inherited collocation is uncertain because it
supplies only the noun. The qualifying claims are C0001, C0003, C0005, C0007 and
C0010. Sensitivity weights are 4.25/0.75 for accepted+weak and all, with exact
p=0.480247808; accepted remains 0/0. This conservative coding is separately
labelled and leaves the original endpoint intact. A future endpoint requires
prospective documentation and direct anchor adjudication before reading.

## JSONL schema version 1

There is one `run` row, followed by `bundle` rows and `claim` rows. All identifiers
and loci are metadata; no passage text or verdict quotations are included.

| Row | Required fields and meaning |
| --- | --- |
| run | `schema_version`, `run_id`, `reviewed_source_commit`, `input_sha256` (source paths to hashes), `total_original_bundles`, `completed_readers`, `order_provenance`, `construction_evidence`, `eligibility_evidence` |
| bundle | `bundle_id`, `slab`, zero-based `order_index`, `block_id=floor(order_index/5)`, `block_size`, `block_rule`, `intended_assignment`, `actual_kind` (real/decoy), `construction_status`, boolean `in_completed_wave`, `pivot_corpus`, `pivot_group`, `pivot_branch`, `date_bin`, `genre`, `pivot_id`, `shown_partner_ids` |
| claim | `claim_id`, `bundle_ids`, `original_grade` (accepted/weak/reject), `original_eligibility` (`eligible` boolean and `reason`), `anchors`, `contribution_coding` |
| anchor | `id` (locus), `branch`, `contribution`, `verified` boolean, `reason`, `evidence` (verdict filename, claim and field) |

The exporter `scripts/build_8c_celtic_ledger.py` accepts explicit `--key`,
`--claims-key`, `--assignment`, `--stats`, `--historical-results`, `--loci-dir`, `--verdicts` (one or more),
`--output`, `--source-commit`, and `--run-id` arguments. It is specific to the
completed 28-reader wave and freezes manual contribution coding. Export requires
the permitted original Stage C keys; replay does not. The run row's hashes
identify those private inputs without requiring their distribution. Stage C-S
inputs are neither opened nor included.
