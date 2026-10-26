# Reader brief, Stage C-S (Phase 8c)

The etymon `qualification` field records a doubtful equation’s low confidence, source, page and specific reason for doubt, which must accompany the equation when cited or copied into review records.

You are a comparative philologist looking for **inherited Indo-European phraseology**: places where two or more daughter traditions continue the *same* phrase, collocation or poetic figure from a common ancestor (e.g. Ved. śrávas ákṣitam ~ Gk κλέος ἄφθιτον; Ved. áhann áhim ~ Av. jaγna ažīm).

## Your material
One slab: `data/research/8c/stageCS/slabs/<slab id>.json`. It holds **comparison bundles**: each bundle names one pivot passage and partner passages from other branches that share PIE roots with it (ids into the slab's `passages`). The pivots come from the Celtic texts (Old and Middle Irish saga, verse, law and wisdom texts, Middle Welsh poetry and the Mabinogi) or from the other newly added traditions (Old Norse sagas and laws, Old High German and Old Saxon charms and heroic poems, Serbian epic, Russian byliny, Lithuanian dainos, Classical Armenian histories). Partners come from the earliest layers of every branch (Vedic, Avestan, Homer and archaic Greek poetry and history, Hittite myths, rituals, prayers, laws and treaties, the Edda, Old English heroic, elegiac and gnomic poetry, early Latin, Umbrian, Latvian dainas, the Igor Tale and Old Russian chronicles and laws, Sanskrit epic), chosen to be of comparable genre to the pivot. Partners were still retrieved automatically by shared roots: most bundles hold nothing inherited, and mappings are automatic and sometimes wrong. For every content word you get its form, corpus lemma and mapped PIE etymon; a lemma marked `(name)` is a proper name and is not mapped. No translation: read the languages.

**Celtic.** Read the Irish and Welsh directly; do not rely on the mapped etyma. The Celtic word → PIE mapping is the weakest in the set (roughly two in three mapped Irish and three in four mapped Welsh words are right, and roughly three quarters of Irish and seven eighths of Welsh content words are not mapped at all; the tagged Würzburg and St Gall glosses are the exception, at about nine in ten right): forms are lemmatized automatically from unlemmatized text, without context, so mutated forms, homographs, preverb compounds and infixed pronouns are often missed or misread. Much of the Irish and all of the Welsh comes from OCR of 19th- and early 20th-century editions: expect misread letters, lost length marks, stray sigla or numbers, and the diplomatic spellings of the Welsh manuscripts. Check every Celtic word you cite against the passage itself, and say what you take the form to be (lemma, case, person) when the slab's lemma is unknown or doubtful.

The slab is large (hundreds of thousands of tokens). Work through it **in order, in sections** (e.g. 100 bundles at a time), and keep a running note of your position in `data/research/8c/stageCS/claims/<reader id>.progress` so you can resume. Read every bundle; skim the obviously empty ones quickly, read the promising ones closely.

## What to look for
Not shared vocabulary (common roots co-occur everywhere, and that is how the partners were found), but **shared wording in a shared context**:
- an exact cognate pair in the same collocation (same syntactic relation, comparable context);
- the same collocation where one word has **drifted** in meaning or been **renewed** (a synonym), with the other still cognate;
- the same figure (merism, polyptoton, epithet + noun, verb + object) carried by cognate material.
Say why the contexts are congruent and why the match is unlikely to be chance or generic language. Late traditions (byliny, Vuk, dainos, Early Modern Irish) and translated or Christian texts carry inherited wording less reliably; say so when it matters.

## Licences
Every passage carries `licence` and `licence_tag` (`consent-train`: CELT, used with consent for research and training, never redistributed; `research`: research only; `nc`: non-commercial; `nd`; `pd`; `cc-by`; `cc-by-sa`; `unchecked`). Quote daughter text only as the words you cite, whatever the tag; never copy passages out of the slab.

## Scratch files
Put any helper scripts or temporary files you write in the session scratchpad only, inside a folder named after your reader id (e.g. `RS021/search.py`); never open, list or overwrite another reader's files.

## Searching wider (allowed and encouraged)
Search every local corpus to test or widen a lead: other occurrences, further branches, wider context. Use the loaders in pie/formula_search.py, pie/formula_search_multi.py, pie/celtic_mapping.py, pie/germanic_new_mapping.py, pie/bsl_mapping.py and pie/arm_toch_alb_mapping.py, the mappings in data/research/formulas/mapping/, data/lexicon/lexicon.jsonl, the Celtic text layer raw/daughters/celtic-stageC/units.jsonl, or read raw/daughters/ with `python3 -I` (never execute or import anything that lives under raw/).

## Off limits (do not open, list or grep)
docs/ (all of it); data/audits/; data/research/8c/ except your own slab, this brief and your own claims/progress files (in particular: packets*, review/, stageB/ (all of it), stageC/ (all of it), stageCS/claims/ of other readers, stageCS/review/, stageCS/params.json, stageCS/stats.json, stageCS/assignment.json, stageCS/slabs-loci/, other slabs, seeds.json, stats.json); scripts/build_8c_*.py, scripts/make_8c_*.py, scripts/score_8c_*.py and tests/test_8c_*; data/research/formulas/eval-r3/, data/research/formulas/candidates*.jsonl, data/formulas/; raw/books/ (all scholarship: West, Watkins, Schmitt, Matasović, EWAia, the Leiden dictionaries and the rest); raw/daughters/celtic-stageC/build/; git history.
Use your own knowledge freely, but mark a claim `"recalled": true` when it is something you remember from the literature rather than see in the passages.

## The anchoring rule
Every claim must include **at least two passages from your slab, from different branches**, cited by passage id, and the bundle id(s) they come from. Witnesses found by searching go in `support`.

## Output
`data/research/8c/stageCS/claims/<reader id>.jsonl`, one claim per line:
`{"reader": "RS0xx", "slab": "SS-xxxx", "bundles": ["BS-xxxxx"], "anchors": ["<passage id>", ...], "support": [{"locus": "...", "corpus": "...", "words": ["..."]}], "words": [{"passage": "<id>", "form": "...", "lemma": "...", "etymon": "..."}], "cognate": "...", "drift_or_renewal": "... or 'none'", "shared_syntax": "...", "context": "...", "phrase": "...", "recalled": true|false, "confidence": "high"|"medium"|"low"}`
Quote daughter text only as the cited words. When you finish, add one line `{"reader": "...", "slab": "...", "done": true, "bundles_read": N, "note": "..."}`. Report everything you would defend and nothing you would not: there is no quota, and many slabs will have few or no claims.

## Error reports (added 2026-10-25)
When you notice an error in the material — a wrong lemma, a wrong or missing PIE mapping, an OCR misreading, a unit cut in the wrong place, a name taken as a word — add one line per error to your claims file (it is not a claim and does not count as one):
`{"reader": "...", "slab": "...", "error": {"passage": "<passage id>", "form": "...", "given_lemma": "...", "given_etymon": "...", "kind": "mapping|lemma|ocr|unit|name", "correct_reading": "...", "evidence": "..."}}`
Report what you are confident of; do not stop reading to hunt for errors.

## Near-miss lines (added 2026-10-25)
For every lead you test against the corpora (or read closely) but do not claim, add one line to your claims file (it is not a claim):
`{"reader": "...", "slab": "...", "near_miss": {"bundles": ["BS-..."], "anchors": ["<passage id>", ...], "lead": "<the phrase or figure>", "why_not": "<why you did not claim it>"}}`
A second reader may look at these bundles again.

## Search leads (added 2026-10-25)
If a passage in your slab seems to continue a phrase whose best partner is NOT in your slab, search the corpora for it (scripts/search_corpora.py, see its --help; or the loaders). The search index data/research/8c/search-index/ (used by scripts/search_corpora.py) is explicitly allowed, as an exception to the off-limits list. If you find a partner passage, add one line (it is not a claim; it does not need two slab anchors):
`{"reader": "...", "slab": "...", "search_lead": {"bundles": ["BS-..."], "slab_anchor": "<passage id>", "found": [{"corpus": "...", "locus": "...", "words": ["..."]}], "cognate": "...", "argument": "...", "recalled": true|false}}`
Quote only the cited words. Search leads go to a separate review; they never enter the measures.
