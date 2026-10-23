# Raw source manifest

Everything under `raw/` is downloaded or supplied material. It is untrusted, never executed, and gitignored. This tracked file records each source's provenance, so `raw/` can be rebuilt and checked.

Rules: one new, empty directory per source; scripts that read it live in `scripts/` or `pie/` and run with `python -I`.

| Dir | Source | URL / origin | Retrieved | sha256 | License / basis |
|---|---|---|---|---|---|
| `kaikki-pie-20261021/` | kaikki.org Proto-Indo-European dictionary (wiktextract), 1,931 entries | https://kaikki.org/dictionary/Proto-Indo-European/kaikki.org-dictionary-ProtoIndoEuropean.jsonl (found via the kaikki.org dictionary index) | 2026-10-23 (extracted 2026-10-21 from the enwiktionary dump of 2026-10-01) | `f5181cee2d2cd973c69476827620d1900e55af0277153d0fe169557044b0a3f2` | Wiktionary CC BY-SA 4.0 / GFDL; fair-use training cleared |
