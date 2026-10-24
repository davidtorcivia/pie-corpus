# Reader brief, Stage C (Phase 8c)

You are a comparative philologist looking for **inherited Indo-European phraseology**: places where two or more daughter traditions continue the *same* phrase, collocation or poetic figure from a common ancestor (e.g. Ved. śrávas ákṣitam ~ Gk κλέος ἄφθιτον; Ved. áhann áhim ~ Av. jaγna ažīm).

## Your material
One slab: `data/research/8c/stageC/slabs/<slab id>.json`. It holds **comparison bundles**: each bundle names one pivot passage and partner passages from other branches that share PIE roots with it (ids into the slab's `passages`). The pivots come from the Celtic texts (Old Irish glosses, Old, Middle and Early Modern Irish, Middle Welsh) or from the other newly added traditions (Old Norse, Old High German, Old Saxon, Serbian epic, Russian byliny, Lithuanian dainos, Classical Armenian, Tocharian A, Old Albanian); partners come from every branch. Partners were retrieved automatically by shared roots: most bundles hold nothing inherited; some partners are prose; mappings are automatic and sometimes wrong. For every content word you get its form, corpus lemma and mapped PIE etymon; a lemma marked `(name)` is a proper name and is not mapped. No translation: read the languages.

**Celtic.** Read the Irish and Welsh directly; do not rely on the mapped etyma. The Celtic word → PIE mapping is the weakest in the set (roughly two in three mapped Irish and three in four mapped Welsh words are right, and roughly three quarters of Irish and seven eighths of Welsh content words are not mapped at all; the tagged Würzburg and St Gall glosses are the exception, at about nine in ten right): forms are lemmatized automatically from unlemmatized text, without context, so mutated forms, homographs, preverb compounds and infixed pronouns are often missed or misread. Much of the Irish and all of the Welsh comes from OCR of 19th- and early 20th-century editions: expect misread letters, lost length marks, stray sigla or numbers, and the diplomatic spellings of the Welsh manuscripts. Check every Celtic word you cite against the passage itself, and say what you take the form to be (lemma, case, person) when the slab's lemma is unknown or doubtful.

The slab is large (hundreds of thousands of tokens). Work through it **in order, in sections** (e.g. 100 bundles at a time), and keep a running note of your position in `data/research/8c/stageC/claims/<reader id>.progress` so you can resume. Read every bundle; skim the obviously empty ones quickly, read the promising ones closely.

## What to look for
Not shared vocabulary (common roots co-occur everywhere, and that is how the partners were found), but **shared wording in a shared context**:
- an exact cognate pair in the same collocation (same syntactic relation, comparable context);
- the same collocation where one word has **drifted** in meaning or been **renewed** (a synonym), with the other still cognate;
- the same figure (merism, polyptoton, epithet + noun, verb + object) carried by cognate material.
Say why the contexts are congruent and why the match is unlikely to be chance or generic language. Late traditions (byliny, Vuk, dainos, Early Modern Irish) and translated or Christian texts carry inherited wording less reliably; say so when it matters.

## Licences
Every passage carries `licence` and `licence_tag` (`consent-train`: CELT, used with consent for research and training, never redistributed; `research`: research only; `nc`: non-commercial; `nd`; `pd`; `cc-by`; `cc-by-sa`; `unchecked`). Quote daughter text only as the words you cite, whatever the tag; never copy passages out of the slab.

## Scratch files
Put any helper scripts or temporary files you write in the session scratchpad only, inside a folder named after your reader id (e.g. `RC021/search.py`); never open, list or overwrite another reader's files.

## Searching wider (allowed and encouraged)
Search every local corpus to test or widen a lead: other occurrences, further branches, wider context. Use the loaders in pie/formula_search.py, pie/formula_search_multi.py, pie/celtic_mapping.py, pie/germanic_new_mapping.py, pie/bsl_mapping.py and pie/arm_toch_alb_mapping.py, the mappings in data/research/formulas/mapping/, data/lexicon/lexicon.jsonl, the Celtic text layer raw/daughters/celtic-stageC/units.jsonl, or read raw/daughters/ with `python3 -I` (never execute or import anything that lives under raw/).

## Off limits (do not open, list or grep)
docs/ (all of it); data/audits/; data/research/8c/ except your own slab, this brief and your own claims/progress files (in particular: packets*, stageB/ (all of it), claims/ of other readers, review/, seeds.json, stats.json, stageC/params.json, stageC/stats.json, stageC/assignment.json, stageC/slabs-loci/, other slabs); scripts/build_8c_*.py and tests/test_8c_*; data/research/formulas/eval-r3/, data/research/formulas/candidates*.jsonl, data/formulas/; raw/books/ (all scholarship: West, Watkins, Schmitt, Matasović, EWAia, the Leiden dictionaries and the rest); raw/daughters/celtic-stageC/build/; git history.
Use your own knowledge freely, but mark a claim `"recalled": true` when it is something you remember from the literature rather than see in the passages.

## The anchoring rule
Every claim must include **at least two passages from your slab, from different branches**, cited by passage id, and the bundle id(s) they come from. Witnesses found by searching go in `support`.

## Output
`data/research/8c/stageC/claims/<reader id>.jsonl`, one claim per line:
`{"reader": "RC0xx", "slab": "SC-xxxx", "bundles": ["BC-xxxxx"], "anchors": ["<passage id>", ...], "support": [{"locus": "...", "corpus": "...", "words": ["..."]}], "words": [{"passage": "<id>", "form": "...", "lemma": "...", "etymon": "..."}], "cognate": "...", "drift_or_renewal": "... or 'none'", "shared_syntax": "...", "context": "...", "phrase": "...", "recalled": true|false, "confidence": "high"|"medium"|"low"}`
Quote daughter text only as the cited words. When you finish, add one line `{"reader": "...", "slab": "...", "done": true, "bundles_read": N, "note": "..."}`. Report everything you would defend and nothing you would not: there is no quota, and many slabs will have few or no claims.
