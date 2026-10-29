# Formula discovery, round D2: pre-registration (2026-10-28)

D1 failed its positive control: known-formula recall was 0.10 against a required 0.30
(`docs/research/discovery-r1-results.md`). Its design notes give four causes:

1. branch base rates swamp the poetic corpora;
2. O and E are measured over different spans;
3. the null threshold is too strict for two-branch formulas;
4. recall is counted in duplicated rows.

D2 fixes each cause, and it uses a tune/test split so that the fixes are not fitted to the test set. It is
written before any D2 number is computed. The D1 code (`scripts/discovery_d1.py`) and its cached counts may
be reused.

## Changes from D1 (fixed)

- **Strata, not branches.** Each daughter tradition is split into register layers: Homer and archaic
  epic; later Greek; Rigveda and Atharvaveda; epic Sanskrit; Avesta; Edda and skaldic verse; sagas;
  Old Irish; Middle Irish; and so on. Counts are taken per **layer**, using the layer list from the Stage C-S
  stratified build (`docs/research/8c-preregistration.md`, Stage C-S). A pair qualifies in a branch if it
  qualifies in **any** layer of that branch.
- **Window-based expectation.** E = the expected number of ±4-word windows that contain both ids, given
  each id's frequency within the layer and the layer's window count. O and E are now measured over the
  same span.
- **Unit of recall.** Recall is counted over **distinct root-group pairs** of the multi-branch known formulas:
  the 65 distinct best pairs in D1's control diagnostics. Duplicated rows no longer weigh in.
- **Tune/test split.** The 65 pairs are split by sha256(pair) into tune (33) and test (32). Free
  parameters are chosen on the tune half **only**, from the grid below, by maximizing tune recall at a
  null-matched false rate. Then they are frozen and recorded, and recall is measured once on the test half.
  - min O ∈ {2, 3}
  - O/E ∈ {2, 3, 4}
  - minimum qualifying branches = 2
  - null percentile ∈ {95, 99}
- **Null rate.** Shuffles are as in D1 (20 seeds, within each layer). The false rate is the mean number of
  null candidates divided by the real candidate count. It is reported for the chosen parameters and must be
  ≤ 0.20.
- **Success criterion for the candidate list.** Test-half recall ≥ 0.30 with false rate ≤ 0.20. If either
  fails, D2 reports the list as uninformative and stops before any review.
- **Review (only if the criterion is met).** Unchanged from D1: the top 40 new candidates plus 10 null decoys,
  blind, accepted/weak/reject. The measure is accepted rate on new candidates against decoys (Fisher, one-sided,
  ≥ 2× and p < 0.05). Accepted items get a novelty check against the held literature, then the Tier 2 path.

## Reporting

Results go in `docs/research/discovery-r2-results.md`: the tune grid, the frozen parameters, test recall, the
false rate, and, if run, the review.
