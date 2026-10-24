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

## Stage B (the full-corpus discovery run), unblinded 2026-10-23
Pre-registration: docs/research/8c-preregistration.md (Stage B, reader capacity, build parameters and deviations, five disclosed scratch-file exposures, none touching a slab that produced a claim). 50 slabs, 10,236 bundles (8,188 real, 2,048 embedded decoys whose partners were replaced; the pivot stays real), 50 readers, 148 claims, four blind reviewers (37 each; claims stripped of slab, bundle kind, reader, confidence and recalled flag). A claim is credited to the bundles it cites, split equally. One-sided permutation over the 10,236 bundle labels, 10,000 permutations, seed 0 (data/research/8c/stageB/results.json).

| measure | real (per 1,000 bundles) | decoy (per 1,000) | ratio | p |
|---|---|---|---|---|
| **accepted claims (primary)** | 3.83 | 1.79 | **2.14** | **0.018** |
| accepted + weak | 10.19 | 5.16 | 1.97 | 0.0018 |
| all claims | 16.48 | 6.39 | 2.58 | 0.0001 |

**The primary criterion is met** (ratio ≥ 2, p < 0.05). Of the 148 claims, 35 were accepted, 59 weak, 54 rejected. No claim rests on decoy material alone: the decoy-bundle credit comes entirely from 31 claims (9 accepted) that cite both real and decoy bundles. Because a decoy keeps its real pivot passage, such a claim can legitimately anchor on a decoy bundle's pivot, so the decoy rate likely overstates false discovery (a post-hoc observation, not used to adjust the score). Reader confidence is calibrated: high 23/28 accepted, medium 10/48, low 2/72. Reviewer strictness varied (accepted 7, 4, 14, 10 of 37 per reviewer); claims were assigned at random, so this adds noise, not bias.

### Novelty of the 35 accepted claims (data/research/8c/stageB/review/novelty-{1,2}.jsonl)
**29 known, 6 partly known, 0 not found.** The known ones are the textbook formulas (Father Sky, daughter of the sky, men and cattle, swift horses, givers of goods, great fame, immortal/mortal, slay the serpent, 'put a name' in six or more branches; several of the anchors are themselves cited by West, Watkins or Schmitt). The six partly known claims reduce to three candidates, each an addition to a known formula, not a new one:
1. **'Eat raw flesh' as a free phrase** (four independent claims; also found in Stage A): only the compound ὠμηστής ~ āmā́d- is in the literature (West p. 80; Beekes EDG). New: the clause AVŚ 8.6.48 ~ Il. 22.347, the phrase āmásya kravíṣaḥ (RV 1.162.10) ~ ὠμὰ κρέα, and raw-eaters tearing a corpse (AVŚ 11.10.18 ~ Il. 11.454).
2. **'Clothe in the immortal'**: West p. 157 n. 126 discusses ἄμβροτα εἵματα (Il. 16.680) and the word equations are known; new is the Vedic witness amŕ̥tena … vastām (RV 6.75.18 = AVŚ 7.118.1; AVŚ 9.1.2) set beside the Greek, with cognate verb (*wes-) and adjective (*n̥-mr̥tó-).
3. **'Hear my word' with the cognate object** (also found in Stage A): 'hear me' is known with non-cognate objects (West pp. 316-318, Schmitt §§396-405); new is *ḱlew- governing *wékʷos (Ved. vácas- = Gk ἔπος: RV 10.66.11c, 1.145.3b ~ Il. 16.236 = 14.234; Pind. I. 6.42).

## Overall (Stage A + B)
Readers recover the known inherited phraseology reliably and discriminate real from decoy material (Stage B primary criterion met, p = 0.018; Stage A underpowered). Across both stages the candidates beyond the literature we hold are three additions to known formulas, two of them found independently in both stages: 'eat raw flesh' as a free phrase, 'clothe in the immortal' with its Vedic witness, and *ḱlew- + *wékʷos. They are **candidates**: no expert has confirmed them, and the literature we hold is a subset of the field (Durante 1971/1976, the Vedic and Homeric commentaries and much journal literature are not checked). No wholly new formula was found.

## Erratum (2026-10-23)
Stage A's 'partly known' sweet-mead claim (an Old English witness, *swētne medo*, Finnsburh 39) rests on Ettmüller's emendation: the manuscript reads *hwitne* 'white' (Tier 2 review r3). The claim is therefore **known** (Vedic and Greek, West p. 84, Schmitt §529) with no new witness. Stage A's partly-known count becomes 3; the overall candidate list (three additions to known formulas) is unchanged, since sweet mead was not among them.
