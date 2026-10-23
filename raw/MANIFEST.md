# Raw source manifest

Everything under `raw/` is downloaded or supplied material. It is untrusted, never executed, and gitignored. This tracked file records each source's provenance, so `raw/` can be rebuilt and checked.

Rules: one new, empty directory per source; scripts that read it live in `scripts/` or `pie/` and run with `python -I`.

| Dir | Source | URL / origin | Retrieved | sha256 | License / basis |
|---|---|---|---|---|---|
