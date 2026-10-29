# Formula discovery, round D1: pre-registration (2026-10-28)

Written before any D1 candidate is computed or read. D1 uses the corrected multi-branch search index:
corpus-quality batch 1, theonym narrowing, and the collocation tool `scripts/collocates_8c.py`. It
asks whether a corpus-wide, controlled collocation search can surface inherited two-word phrases that are
not in the known-formula list.

## Method (fixed)

- **Unit and window.** A collocation is a pair of PIE lexeme or root-group ids that co-occur within ±4
  content words in the same unit. Counting follows `collocates_8c.py`: O = units containing both;
  E = from each id's unit rate in that branch.
- **Branches.** Indo-Iranian, Greek, Italic, Celtic, Germanic, Balto-Slavic, Armenian and Anatolian, as in the
  8c branch list. Within a branch, every corpus counts.
- **Null.** Root sets are shuffled within each corpus, preserving each unit's size and each corpus's root
  frequencies. There are 20 shuffles with seeds 0–19. A pair's null score in a branch is its O/E in the shuffled index.
- **Candidate rule.** A pair is a candidate if, in **≥ 2 branches**, O ≥ 3 and O/E ≥ 3, **and** its real
  cross-branch score (the minimum over its qualifying branches of log₂ O/E) exceeds the 99th percentile of the
  same score over the 20 nulls. Pairs with a function-word id, or a top-50-frequency root on both sides, are excluded.
- **Positive control (measured first).** Recall of the multi-branch known formulas from
  `data/research/formulas/witness-scan.jsonl`, the 120 "multi-branch" rows, among the candidates. It is
  reported before any candidate is read. If recall is under 0.30, the candidate list is reported as
  uninformative and D1 stops there.
- **Novelty.** A candidate is "known" if it matches a formula in `data/formulas/formulas.jsonl` or Tier 2;
  otherwise it is "new".
- **Blind review.** The top 40 new candidates, ranked by the cross-branch score, are mixed with 10 **decoys**:
  pairs from the null runs that meet the O and O/E thresholds in ≥ 2 branches of a shuffled index, shown with
  real loci for their two words that happen to co-occur. The mix is shuffled and given opaque ids; the key is
  in `data/audits/keys/` (gitignored). A reviewer agent opens every locus and grades each item
  accepted / weak / reject, using the 8c grades (`docs/research/8c-preregistration.md`).
- **Measures.**
  - The primary measure is the accepted rate on new candidates against decoys (Fisher, one-sided; success if
    the rate is ≥ 2× and p < 0.05).
  - The secondary measures are accepted + weak, and positive-control recall.
  - Every accepted item gets a novelty check against the held literature (West, Watkins, Schmitt,
    Mallory–Adams, Fortson), as for the knee-sleep study.
- **Use.** Accepted new phrases become Tier 2 candidates (`docs/generation/tier2-brief.md`) and go through the
  normal Tier 2 adversarial review.

## Reporting

All results go in `docs/research/discovery-r1-results.md`, whatever they are.
