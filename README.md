# Reconstructed PIE corpus

A training corpus of reconstructed Proto-Indo-European text, mostly poetic and mythic, for fine-tuning a small model that "speaks PIE". It is **plausible PIE by construction, not recovered PIE**: every record carries a provenance tag (`scholarly`, `formulaic`, `back_projection`, `synthetic`).

- Plan: [PLAN.md](PLAN.md). Progress: [docs/STATUS.md](docs/STATUS.md). Notation spec: [docs/notation.md](docs/notation.md).
- Setup: `uv sync`. Tests: `uv run pytest`.
- Transliteration: `uv run python -I scripts/translit.py to-ascii "h₂ówis h₁éḱwōs-kʷe"` prints `h2o/wis h1e/k'wo:s-kwe`.

- Sources and licenses: [NOTICE.md](NOTICE.md). The lexicon data derives from Wiktionary (CC BY-SA 4.0).
