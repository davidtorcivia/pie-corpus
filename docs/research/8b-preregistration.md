# Phase 8b replication: pre-registration (written 2026-10-23, before the data exists)

The first run (docs/research/8b-backtest.md) found, in an exploratory out-of-fold analysis, higher surprisal at laryngeal **loss** and **colouring** positions than at context-matched controls, beyond the bigram and shuffled-data baselines (+0.27 nats [+0.08, +0.48]), and nothing at **length**. Because that analysis was chosen after the pre-registered test proved underpowered, it is a hypothesis. This file fixes the confirmatory test before any new data is built.

## Data (fresh)
- Cognate sets built from the kaikki.org Sanskrit and Ancient Greek dictionaries' etymology links to PIE (and Latin if available), for PIE lemmas **not present** in data/research/backtest/primary.jsonl or secondary.jsonl, at root-family level: no root family of the first run's data may appear.
- The same contamination rules (attested languages only; the >2% laryngeal-notation scan; Anatolian and Tocharian removed) and the same target transducer (pie/prelaryngeal.py, unchanged).
- If fewer than 150 effect slots with exact-matched controls (≥ 3 control families per stratum) result, the replication is reported as underpowered and not run as confirmatory.

## Model and training
- The first run's model and hyperparameters (data/research/backtest/tune.json), unchanged, trained on all of the first run's primary data (train + dev + eval), and evaluated once on the fresh sets.

## Hypotheses and test (one-sided, α = 0.05 each, Holm-corrected over the two)
- **H1 (loss):** surprisal at loss positions minus matched controls, minus the same difference under the shuffled-data model, is > 0.
- **H2 (colouring):** the same for colouring positions.
- Statistic: mean difference over slots; CI by bootstrap over root families (10,000 resamples); the test passes if the lower bound of the one-sided 95% interval is > 0 after Holm correction.
- **Not tested confirmatorily:** length (null in the first run), schwa and initial vowels (no controls available).

## Reporting
Whatever the outcome, the numbers above are reported as they come out, with the slot counts, in docs/research/8b-backtest.md under "Replication". No other statistic is substituted for H1/H2 after the data is seen.

## Outcome of this pre-registration (2026-10-23)
Underpowered, as the minimum-power rule defines it: the kaikki Sanskrit/Greek/Latin etymologies gave 23 fresh sets with 1 exact-matched effect slot (minimum 150), because they derive from the same Wiktionary pages as the first run's lexicon. No model was trained and no statistic computed. H1 and H2 remain open.

**Next replication (to be pre-registered separately before any data is built):** NIL's formations carry daughter words transcribed from the book (data/lexicon/nil.jsonl, up to four per formation, with ‡ marking single-language formations). They are independent of Wiktionary's descendant lists, but share root families with the first run, so independence must be defined per formation (a formation, i.e. root + suffix, absent from the first run's data) rather than per root family.
