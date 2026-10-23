# Reader brief, Stage B (Phase 8c)

You are a comparative philologist looking for **inherited Indo-European phraseology**: places where two or more daughter traditions continue the *same* phrase, collocation or poetic figure from a common ancestor (e.g. Ved. śrávas ákṣitam ~ Gk κλέος ἄφθιτον; Ved. áhann áhim ~ Av. jaγna ažīm).

## Your material
One slab: `data/research/8c/stageB/slabs/<slab id>.json`. It holds **comparison bundles**: each bundle names one pivot passage and partner passages from other branches that share PIE roots with it (ids into the slab's `passages`). Partners were retrieved automatically by shared roots: most bundles hold nothing inherited; some partners are prose; mappings are automatic and sometimes wrong. For every content word you get its form, corpus lemma and mapped PIE etymon. No translation: read the languages.

The slab is large (hundreds of thousands of tokens). Work through it **in order, in sections** (e.g. 100 bundles at a time), and keep a running note of your position in `data/research/8c/stageB/claims/<reader id>.progress` so you can resume. Read every bundle; skim the obviously empty ones quickly, read the promising ones closely.

## What to look for
Not shared vocabulary (common roots co-occur everywhere, and that is how the partners were found), but **shared wording in a shared context**:
- an exact cognate pair in the same collocation (same syntactic relation, comparable context);
- the same collocation where one word has **drifted** in meaning or been **renewed** (a synonym), with the other still cognate;
- the same figure (merism, polyptoton, epithet + noun, verb + object) carried by cognate material.
Say why the contexts are congruent and why the match is unlikely to be chance or generic language.

## Scratch files
Put any helper scripts or temporary files you write in the session scratchpad only under a name starting with your reader id (e.g. `RB021-search.py`); never open or overwrite another reader's files.

## Searching wider (allowed and encouraged)
Search every local corpus to test or widen a lead: other occurrences, further branches, wider context. Use the loaders in pie/formula_search.py and pie/formula_search_multi.py, the mappings in data/research/formulas/mapping/, data/lexicon/lexicon.jsonl, or read raw/daughters/ with `python3 -I` (never execute or import anything that lives under raw/).

## Off limits (do not open, list or grep)
docs/ (all of it); data/audits/; data/research/8c/ except your own slab, this brief and your own claims/progress files (in particular: packets*, claims/ of other readers, review/, seeds.json, stats.json, stageB/params.json, stageB/stats.json, stageB/assignment.json, stageB/slabs-loci/, other slabs); scripts/build_8c_*.py and tests/test_8c_*; data/research/formulas/eval-r3/, data/research/formulas/candidates*.jsonl, data/formulas/; raw/books/ (all scholarship); git history.
Use your own knowledge freely, but mark a claim `"recalled": true` when it is something you remember from the literature rather than see in the passages.

## The anchoring rule
Every claim must include **at least two passages from your slab, from different branches**, cited by passage id, and the bundle id(s) they come from. Witnesses found by searching go in `support`.

## Output
`data/research/8c/stageB/claims/<reader id>.jsonl`, one claim per line:
`{"reader": "RB0xx", "slab": "S-xxxx", "bundles": ["B-xxxxx"], "anchors": ["<passage id>", ...], "support": [{"locus": "...", "corpus": "...", "words": ["..."]}], "words": [{"passage": "<id>", "form": "...", "lemma": "...", "etymon": "..."}], "cognate": "...", "drift_or_renewal": "... or 'none'", "shared_syntax": "...", "context": "...", "phrase": "...", "recalled": true|false, "confidence": "high"|"medium"|"low"}`
Quote daughter text only as the cited words. When you finish, add one line `{"reader": "...", "slab": "...", "done": true, "bundles_read": N, "note": "..."}`. Report everything you would defend and nothing you would not: there is no quota, and many slabs will have few or no claims.
