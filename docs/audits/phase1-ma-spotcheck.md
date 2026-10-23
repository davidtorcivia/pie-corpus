# Phase 1 acceptance: 50-entry spot check against Mallory & Adams (2006)

- **Date:** 2026-10-23
- **Sample:** `phase1-ma-spotcheck-sample-50.jsonl` (25 roots + 25 words, stratified, fixed before lookup)
- **Lookup:** a subagent searched the EPUB text and copied M&A's forms as printed. The extraction damages M&A's notation (*h₂* comes out as "ha"; *k̂* and syllabic resonants are lost); notes flag where. The full rows are in `raw/books/extract/mallory-adams/spotcheck.jsonl` (local).

## Result

**Found in M&A: 48/50.** Not found: *bʰed-* "improve" and *h₂éymō* "imitation".

21 rows differ "in substance" by the agent's strict rule. Triage by the main session:

| Class | Count | Examples | Verdict |
|---|---|---|---|
| Derived word our lexicon has; M&A lists only the root | 8 | *ǵónh₁os*, *ǵénh₁mn̥*, *ǵʰutós*, *bʰorǵʰéyeti*, *múHtrom* | not an error: M&A doesn't list derivatives |
| Different but standard reconstruction choices | 10 | laryngeal or none (*deyh₂-*/*dei-*, *mewsH-*/*meus-*, *h₃yebʰ-*/*yebh-*), *a*- vs *e*-vocalism (*skend-*/*skand-*), s-mobile, enlargements (*stew-*/*(s)teud-*, *skert-*/*(s)ker-*) | school variation; candidates for the variants layer (STATUS question 4) |
| Contested point worth a books check | 2 | *gʷeldʰ-* (labiovelar) vs M&A *gheldh-*; thematic aorist *h₁ludʰét* (zero grade, standard) vs M&A *h1leudhet* | logged; Wiktionary's choice is defensible in both |
| Extraction damage only | (overlaps) | *phaéh1* = *preh₂-*-type, *wk^wos* = *wĺ̥kʷos* | not a difference |

**Verdict: no systematic error in the lexicon builder.** No pattern points at normalization, homograph linking, segmentation or gloss assignment. The differences are inter-scholar variation and derivatives that M&A doesn't list. **The Phase 1 spot-check criterion is met.** The verbal-root target (≥800) still depends on LIV².
