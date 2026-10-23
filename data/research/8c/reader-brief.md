# Reader brief (Phase 8c)

You are a comparative philologist looking for **inherited Indo-European phraseology**: places where two or more daughter traditions continue the *same* phrase, collocation or poetic figure from a common ancestor. Famous examples of the kind (not to be re-reported unless your packet really contains them): Ved. śrávas ákṣitam ~ Gk κλέος ἄφθιτον 'imperishable fame'; Ved. áhann áhim ~ Av. jaγna ažīm 'slew the serpent'.

## Your material
Your assigned packets are JSON files in `data/research/8c/packets/<id>.json`. Each holds blocks of passages from several branches. For every content word you get its form, its corpus lemma, and the PIE lexicon etymon it was mapped to (the mapping is automatic and sometimes wrong: check it). No translation is given: read the languages.

## What to look for
Not shared vocabulary (common words co-occur everywhere), but **shared wording in a shared context**:
- an exact cognate pair in the same collocation (same syntactic relation, comparable context);
- the same collocation where one word has **drifted** in meaning (a cognate in a shifted sense) or been **renewed** (replaced by a synonym), with the other word still cognate;
- the same figure or formula shape (merism, polyptoton, epithet + noun, verb + object) carried by cognate material.
Say why the context is congruent and why the match is unlikely to be chance or generic language.

## Searching wider (allowed and encouraged)
You may search every local corpus to test or widen a lead: other occurrences of the roots, further branches, wider context. Use the loaders in pie/formula_search.py and pie/formula_search_multi.py, the mappings in data/research/formulas/mapping/, data/lexicon/lexicon.jsonl, or read raw/daughters/ with `python3 -I` (never execute or import anything that lives under raw/).

## Off limits (do not open, list or grep)
- docs/ (all of it), data/audits/, data/research/8c/seeds.json, data/research/8c/stats.json, data/research/8c/packets-loci/, scripts/build_8c_packets.py, tests/test_8c_packets.py;
- data/research/formulas/eval-r3/, data/research/formulas/candidates*.jsonl, data/formulas/;
- raw/books/ (all scholarship);
- git history (`git log`, `git show`, …).
Use your own knowledge freely, but say when a claim is something you remember from the literature rather than see in the passages ("recalled").

## The anchoring rule
Every claim must include **at least two passages from your packet, from different branches**, cited by their passage id (`corpus:locus`). Witnesses found by searching are added separately as `support`.

## Output
Write one JSON object per claim, one per line, to `data/research/8c/claims/<your reader id>.jsonl`:
`{"reader": "R?", "packet": "P-xxxx", "anchors": ["<passage id>", "<passage id>", ...], "support": [{"locus": "...", "corpus": "...", "words": ["..."]}], "words": [{"passage": "<id>", "form": "...", "lemma": "...", "etymon": "<lexicon id or reconstruction>"}], "cognate": "what is exactly cognate", "drift_or_renewal": "what shifted or was replaced, and why that is plausible (or 'none')", "shared_syntax": "...", "context": "why the contexts are congruent", "phrase": "the reconstructed common phrase, as PIE lexeme ids or a rough reconstruction", "recalled": true|false, "confidence": "high"|"medium"|"low"}`
Quote daughter text only as the cited words, never whole passages. If a packet has no parallel, write one line `{"reader": "R?", "packet": "P-xxxx", "none": true, "note": "..."}`. Report everything you would defend, and nothing you would not: there is no quota.
