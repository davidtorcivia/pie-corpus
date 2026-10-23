# Phase 8a: an independent evaluation set of inherited formulas (eval-r3)

*Status: in progress. The protocol section below was written first, before the set was finished and before any round-3 result existed.*

## Pre-registered protocol (written 2026-10-23, before any round-3 numbers)

**Population.** Only items with `strength = "lexical"`: every content word is cognate across at least two branches. `partial` and `schema` items are kept in the file but are never scored. Indo-Iranian (Vedic, Avestan, Old Persian) counts as one branch.

**Eligibility per ranking.** A ranking built from corpora C₁…Cₙ is scored on the lexical items whose *scholarly* attestations include at least two of those corpora's branches (e.g. Rigveda × Homer → items with an Indo-Iranian and a Greek attestation). Eligibility comes from the scholarship, not from whether we confirmed the locus. Items whose words have no lexicon entry stay in the denominator. They count as misses unless the ranking matches them at root level.

**Hit.** An item is hit at k if any pair in its `pairs` (lexeme level) or `pairs_root` (root-group level; for rankings that score root groups) is at rank ≤ k. Its rank is the smallest rank over its pairs.

**Primary metric.** Recall@k for k = 50, 100, 200, per ranking, with a 95% percentile CI from 2,000 bootstrap resamples of items (seed 0).

**Subsets, each with its own CI:**
1. *All eligible lexical items.*
2. *Held-out core:* items that overlap neither `data/formulas/formulas.jsonl` nor the round-2 E2 set (`overlap.formulas_jsonl == []` and `overlap.E2 == null`). This is the clean number, because the round-3 search may use formulas.jsonl and West's text for tuning. If the round-3 search tuned on formulas.jsonl or E2, this subset is the headline result.
3. *Corpus-confirmed:* items with a confirmed co-occurrence (`at_locus` or `other_locus`) in both corpora of the ranking.

**Comparisons.** Comparisons between two rankings use a paired bootstrap over the same items (2,000 resamples), reported as the difference with its 95% CI.

**Baseline.** The same method on corpora whose PIE labels are permuted across tokens (5 seeds, as in round 2). Report the mean and maximum recall@k.

**Rules.**
- The set is frozen before scoring. Its sha256 is recorded in the round-3 report.
- No item is added, removed or relabelled after any ranking has been scored against it. Errors found later are listed in an erratum, and both versions are reported.
- Settings may not be tuned on this set. If tuning is needed, use formulas.jsonl/E2. Otherwise, split this set by `sha1(item_id) mod 2`, tune on half A, and report half B once.
- Report the counts of eligible items per ranking next to every recall figure.
