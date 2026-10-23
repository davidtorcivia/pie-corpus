# Forward sound-law checker (Phase 3b)

Code: `pie/soundlaw.py`. Run: `uv run python -I scripts/check_soundlaws.py`. Output: `data/lexicon/soundlaw_report.json` and `soundlaw_warnings.jsonl`. **Approximate and warning-only:** nothing is rejected on its basis.

## Design

Running whole forms through four daughter phonologies would mostly measure derivation and analogy. Gk *φέρει* and Lat. *fert* aren't regular outcomes of *bʰéreti*. So the checker tests **diagnostic correspondences at the word-initial position**, where alignment is reliable. It compares each lexeme's PIE form with its Sanskrit, Ancient Greek, Latin and Proto-Germanic reflexes, using the romanization.

| Law | What it checks |
|---|---|
| satem / centum | ḱ ǵ ǵʰ → Skt ś j h; Gk/Lat k/c g; PGmc h k g |
| labiovelar | kʷ gʷ gʷʰ → Lat qu- v-; Gk p/t/k b/d/g; PGmc hw kw |
| grimm | p t ḱ/k/kʷ → f þ h(w); b d g → p t k; bʰ dʰ gʰ → b d g |
| aspirate | bʰ dʰ gʰ → Skt bh dh gh/h; Gk ph th kh; Lat f f h |
| grassmann | the first of two aspirates deaspirates in Skt and Gk (bʰendʰ- → bandh-) |
| greek-s-h, s-mobile | s + vowel → Gk h-; #sC- may lose the s |
| prothesis | #h₁C #h₂C #h₃C → Gk e- a- o- (*h₂nḗr* → *anḗr*) |
| coloring | #h₂e → Gk/Lat a-; #h₃e → o- |
| labial, dental, velar, resonant, sibilant | the plain correspondences |

Skipped: reflexes flagged `borrowed`, `analogical` or `uncertain` (from the dump's raw tags); initial stop clusters (*dʰǵʰ-*, *tḱ-*); and failed daughter forms that start with a known prefix or augment (Gk *e-*, Skt *a-*, Lat *con-*, PGmc *ga-*, …).

## Result (2026-10-23)

**5,315 checks, 94.8% pass, 277 warnings.** Most remaining warnings are known irregularities or checker limits, not lexicon errors: Gk *tw- → s-* (*twós → sós*); dissimilation (*dléwkus → glukús*); PGmc *f-* in "four" (*fedwōr*); and laryngeal-initial forms where Greek shows no prothetic vowel. The warnings file is the triage list for the books check against Mallory & Adams and LIV².
