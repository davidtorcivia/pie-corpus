# Phase 8c results

## Stage A (validation), unblinded 2026-10-23
Pre-registration: docs/research/8c-preregistration.md. 24 packets (16 real, 8 decoy), 8 readers, 52 claims, two blind reviewers (26 each), then unblinding. Scores computed by permutation over packet labels (10,000, seed 0, one-sided).

| measure | real (per packet) | decoy (per packet) | ratio | p |
|---|---|---|---|---|
| **accepted claims (primary)** | 0.688 (11 / 16) | 0.250 (2 / 8) | 2.75 | **0.15** |
| accepted + weak | 1.750 | 0.625 | 2.80 | 0.010 |
| all claims | 2.750 | 1.000 | 2.75 | 0.0006 |

**The primary criterion is not met**: the ratio meets the 2× bar but p = 0.15 > 0.05 (8 decoy packets give little power at these rates). Secondary measures: readers make about 2.75× as many claims on real packets as on decoys (p = 0.0006), and accepted + weak claims are 2.8× as frequent (p = 0.010). Reader confidence is calibrated: high 7/11 accepted, medium 6/22, low 0/19.

Of the 2 accepted claims from decoy packets, both are well-known genuine parallels whose branch blocks happened to fall in different theme blocks (Ζεῦ πάτερ ~ Mars pater; the 'men and cattle' formula). This suggests the decoy rate overstates false discovery, but it is a post-hoc observation and is not used to adjust the result.

### Novelty of the 13 accepted claims (docs/research/8c-novelty.md)
**9 known, 4 partly known, 0 not found.** Known: Father Sky (dyaùḥ pítar = Ζεῦ πάτερ), givers of good things, 'men and cattle' (three claims), yoke the horses, slay the serpent, Ζεῦ πάτερ ~ Mars pater, and others; all are in West, Watkins or Schmitt. Partly known, with what is new relative to the literature we hold:
- **sweet mead**: West p. 84 and Schmitt §529 cite Vedic and Greek only; the Old English witness *swētne medo* (Finnsburh 39) adds Germanic.
- **'hear my word'**: 'hear me' is known (West pp. 316-317, Schmitt §§396-405) with non-cognate objects; new is the cognate object Ved. vácas- = Gk ἔπος with *ḱlew-.
- **'eat raw flesh'**: only the compound ὠμηστής ~ āmā́d- is known (West p. 80); new is the free three-word phrase (AVŚ 8.6.48 ~ Il. 22.347) and the Old Norse witness.
- **immortal horses**: West p. 158 has the motif only; new is the lexical match amŕ̥tāḥ áśvāḥ ~ ἄμβροτοι ἵπποι (Durante 1976, which West credits and we do not hold, may already have it).
These four are **candidates**: additions to known parallels (a new branch witness, a cognate object, a free phrase beside a compound), not new formulas, and unconfirmed by an expert.

Caveat on the novelty check: the directory raw/books/text/kroonen-pgmc/ held Ringe's *A History of English I* instead of Kroonen's dictionary (an extraction slug collision, fixed 2026-10-23 after this check); Kroonen was therefore not consulted for the Germanic witnesses.

## Decision on Stage B
The pre-registration gates Stage B on Stage A's primary criterion, or on David's decision if it fails. Asked on 2026-10-23 with the result above, David chose to run Stage B. Stage B is reported with Stage A's failed primary criterion as the headline caveat; its own embedded decoys (20% of bundles) are its primary control.
