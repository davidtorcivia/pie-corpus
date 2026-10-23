# Phase 8b replication 2 (NIL daughters): pre-registration (written 2026-10-23, before the data is built)

The first replication (docs/research/8b-preregistration.md) was underpowered: the kaikki etymologies repeat Wiktionary's descendant lists. NIL (Wodtko, Irslinger & Schneider 2008) is an independent source: its daughter words were transcribed from the book (data/lexicon/nil.jsonl, `formations[].evidence`, up to four per formation). This file fixes the confirmatory test before the NIL-based data is built.

## Data
- One cognate set per NIL formation: the daughter words in its `evidence` (language abbreviation + word), from attested languages only, with the first run's contamination rules (Anatolian and Tocharian removed; no reconstructed proto-forms).
- Exclusions: formations marked ‡, **, ˣ or uncertain; sets with fewer than two languages; any formation whose normalized PIE stem (pie.nil.stem) matches, up to accent and length, a target in data/research/backtest/primary.jsonl or secondary.jsonl. **Independence is per formation, not per root family:** a different derivative of a first-run root counts as new, because its daughter words and its laryngeal contexts differ.
- Target: the NIL stem written pre-laryngeally by pie/prelaryngeal.py (unchanged), with its laryngeal effects as gold.
- **Power rule:** if fewer than 150 effect slots with exact-matched controls (≥ 3 control root families per stratum) result, report "underpowered" and stop.

## Model, hypotheses, statistic (unchanged from the first pre-registration)
- The first run's model and hyperparameters (data/research/backtest/tune.json), trained on all of the first run's primary data, evaluated once on the NIL sets.
- H1 (loss) and H2 (colouring): surprisal at effect positions minus matched controls, minus the same difference under the shuffled-data model, > 0. One-sided α = 0.05 each, Holm-corrected; bootstrap over root families (10,000 resamples).
- Not tested confirmatorily: length, schwa, initial vowels.

## Known limitation, stated in advance
NIL's daughter words are cited forms (often stems, sometimes with morpheme boundaries), not running text. Their romanizations may differ from the Wiktionary-based training inputs (e.g. Vedic accent marking, Greek transliteration); the builder normalizes them with the same rules as the first run and reports the share of words it could not normalize. If that share exceeds 20%, the result is reported with that caveat.

## Reporting
Numbers reported as they come out, with slot counts, under "Replication 2" in docs/research/8b-backtest.md. No other statistic is substituted for H1/H2 after the data is seen.

## Outcome of this pre-registration (2026-10-23)
Underpowered, as the power rule defines it: the NIL formations gave 274 independent cognate sets with 46 exact-matched effect slots (minimum 150); 12.9% of daughter words could not be normalized (under the 20% caveat). No model was trained and no statistic computed; H1 and H2 remain open. Details under "Replication 2" in docs/research/8b-backtest.md.
