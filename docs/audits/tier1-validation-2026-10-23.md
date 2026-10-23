# Tier 1 validation (Phase 3 acceptance run)

- **Date:** 2026-10-23
- **Command:** `uv run python -I scripts/build_tier1.py`
- **Index:** engine (both conventions, with alternatives) + lexicon lemmas + closed classes + verbatim Wiktionary table cells. **No forms taken from the Tier 1 texts themselves**: the measurement is not circular.

## Coverage by version

| Version | Scope | Lines (doc.) | Tokens | Coverage (any tier) | Exact | Misses by class |
|---|---|---|---|---|---|---|
| king-and-god-byrd-2013 | **acceptance** | 12 (0) | 55 | 65.5% | 34.5% | near-miss 14, lexicon-gap 4, engine-gap 1 |
| king-and-god-hamp-sen-1997 | **acceptance** | 11 (5) | 20 | 55.0% | 15.0% | near-miss 8, lexicon-gap 1 |
| schleicher-fable-adams-1997 | **acceptance** | 5 (0) | 66 | 65.2% | 40.9% | near-miss 10, lexicon-gap 7, engine-gap 6 |
| schleicher-fable-byrd-2013 | **acceptance** | 6 (0) | 61 | 72.1% | 49.2% | near-miss 8, lexicon-gap 6, engine-gap 3 |
| schleicher-fable-luhr-2008 | **acceptance** | 5 (0) | 54 | 59.3% | 46.3% | near-miss 9, lexicon-gap 8, engine-gap 5 |
| king-and-god-lehmann-1952 | documentary/pre-laryngeal | 11 (10) | 5 | 60.0% | 60.0% | pre-laryngeal 2 |
| schleicher-fable-danka-1986 | documentary/pre-laryngeal | 5 (0) | 53 | 30.2% | 7.5% | near-miss 16, lexicon-gap 10, pre-laryngeal 7, engine-gap 4 |
| schleicher-fable-hirt-1939 | documentary/pre-laryngeal | 5 (3) | 8 | 25.0% | 12.5% | near-miss 4, lexicon-gap 1, pre-laryngeal 1 |
| schleicher-fable-lehmann-zgusta-1979 | documentary/pre-laryngeal | 5 (0) | 63 | 30.2% | 6.3% | near-miss 23, lexicon-gap 13, pre-laryngeal 5, engine-gap 3 |
| schleicher-fable-schleicher-1868 | documentary/pre-laryngeal | 5 (0) | 61 | 4.9% | 0.0% | pre-laryngeal 56, engine-gap 1, lexicon-gap 1 |
| schleicher-fable-voyles-barrack-2009 | documentary/pre-laryngeal | 5 (0) | 56 | 30.4% | 7.1% | near-miss 21, pre-laryngeal 8, lexicon-gap 7, engine-gap 3 |

Kortlandt (6 versions, 24 lines) is documentary: his glottalic notation has no tested mapping yet.

## Convention tiebreaker (index built under one convention, no alternatives)

| | Byrd fable | Lühr | Adams | Byrd King | Hamp/Sen |
|---|---|---|---|---|---|
| handbook | 67.2% | 53.7% | 47.0% | 63.6% | 40.0% |
| wiktionary | 60.7% | 51.9% | 43.9% | 60.0% | 40.0% |

Measured before the table-cell and glide-spelling tiers were added. Handbook wins on every laryngealist text, which settles open question 3 in favor of the current default.

## Precision (are the hits right?)

Every found token of Byrd's fable was checked by hand against Byrd's translation, as were all fuzzy-tier hits in Adams, Lühr and Hamp/Sen.

- Byrd fable: 43/44 correct after the short-token rule. *tu* "then" no longer matches the pronoun *tú*.
- Known false lemmatizations, which stay in the records as known errors:
  - *h₂áwey* (Byrd, "to the sheep") → *h₂ewís* "evident". The engine does not generate this dative of *h₂ówis*.
  - *h₂ówyom* (Lühr, "of sheep") → *h₂ōwyóm* "egg".
  - *loukós* (Hamp/Sen) → *lowkós* "clearing": the root is right, the lexeme is debatable.
- Fuzzy-tier precision on the checked sample: about 19/21.

## What the misses are

- **Phase B forms:** middles (*agʰnutor*, *u̯l̥nh₁to*, *h₁i̯aǵeto*), participles (*ḱeḱluwṓs*, *widn̥tbʰyos*), the pronominal *-sméy* (*h₁yosméy*). The King and the God is dense with them.
- **Different reconstructions of a known lexeme** (`near-miss`, never counted): Byrd *dʰǵʰémō* vs Wiktionary *ǵʰémō*; *gʷʰérmom*.
- **Genuine lexicon gaps:** checked against the raw dump, 38 of 39 have a counterpart (some coincidental at the 0.75 cutoff). The one with nothing close is *h₁yáǵeswo*.

## Verdict

**Not accepted yet.** Laryngealist coverage is 55–72%, against a target of ≥90%. Every miss has a class. The remaining gap is dominated by Phase B form classes, so Phase 3 acceptance is gated on Phase B (middle, participles, pronominal declension), which is next.
