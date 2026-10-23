# Beyond training: ideas to pursue later

Captured 2026-10-23 at David's request. Each idea is grounded in parts the project already has.

## Tools
- **PIE workbench** (web page / Artifact): English sentence → plan → PIE with an interlinear gloss; a paradigm browser for any lexeme; the validator as a "spellchecker" for pasted reconstructions (recognized forms, and a reason for each miss). Uses: `pie/realize.py`, `pie/morph.py`, `pie/validate.py`. *First candidate: cheap, and it lets David spot-check corpus quality himself.*
- **Reconstruction diff viewer:** the 17 Schleicher-fable / King-and-the-God versions (1868–2013) aligned by line, showing how laryngeals, accent and notation changed. Uses `work_group_id` + `line_no` in `corpus/tier1/`.
- **Teaching materials:** inflection drills, cognates → PIE exercises, flashcards (Anki). The answers are checkable through the engine and the lexicon reflexes.

## Research
- **LLM historical-linguistics benchmark:** cognate set → PIE, inflection, and "spot the Claude-PIE error" on corrupted forms. The eval split and root-family holdout already exist (`pie/export.py`).
- **Wiktionary corrections:** the cross-check found module inconsistencies (*poh₂imnés* vs *h₂ym̥nés*, the dropped *h₂* in *méǵyōs*, final deaspiration). The 277 sound-law warnings are a ready-made review list for Wiktionary editors (`data/morph/crosscheck.json`, `data/lexicon/soundlaw_warnings.jsonl`).
- **Scholarly disagreement map:** per root, where LIV², Mallory & Adams, Fortson and Wiktionary differ (laryngeals, ablaut, palatal vs velar). This falls out of the variants layer (STATUS question 4).
- **Forward projection:** apply the sound laws to whole synthetic texts, giving "the same fable" in pseudo-Proto-Germanic or pseudo-Vedic. A demo of the comparative method run in reverse (`pie/soundlaw.py` would need to grow into a full forward transducer).

## Creative
- **Metered composition:** octosyllabic or hendecasyllabic hymns built from the Watkins/West formulas, with meter measured by `pie/meter.py`, not claimed.
- **Spoken PIE:** an IPA rendering (canonical → IPA is mechanical) plus TTS, so the fable can be heard.
- **Names and phrases on request:** with the gloss and derivation shown (compounds from attested roots; the Tier 3b neologism policy).
