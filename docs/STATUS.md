# Status

**Current phase:** Phase 0 complete (2026-10-23). Next up: Phase 1 (lexicon from the kaikki.org PIE dump).

## Phases

| Phase | State | Acceptance |
|---|---|---|
| 0 Scaffolding & notation | **done** | NFC↔ASCII round-trip on ≥200 tricky forms: **pass** (382 listed forms: 157 hand-written with expected ASCII + 225 generated; plus 5,000 fuzzed; 1,807 tests) |
| 1 Lexicon | next | ≥2,000 entries, ≥800 verbal roots, 50-entry spot check |
| 2 Morphology engine | — | golden paradigms |
| 3 Validator | — | Tier 1 ≥90% token coverage |
| 3b Sound-law checker | — | full lexicon run, mismatch report |
| 4 Tier 1 scholarly | — | 200–500 cited lines + adversarial review |
| 5 Tier 2 back-projection | — | ≥300 lines, ≥8 clusters + adversarial review |
| 6 Tier 3 / 3b synthetic | — | 1–10M tokens, <10% reject, dedup, audit |
| 7 Export + benchmark | — | splits, task views, bench |

## Dashboard

| Metric | Value |
|---|---|
| Lexicon entries / verbal roots | 0 / 0 |
| Root coverage in corpus | — |
| Records per tier (1 / 2 / 3 / 3b) | 0 / 0 / 0 / 0 |
| Tokens per tier | — |
| Neologism share of training tokens | — (cap 10–15%) |
| Validator pass rate | — |
| Sound-law mismatch rate | — |
| Genre × theme grid fill | — |

## Need from David

Ordered by when they are needed. These are all in copyright with no legitimate full text online, so I won't go looking for pirated copies. Put PDFs or EPUBs in `raw/books/` (gitignored). A text layer is best, but plain scans are fine (I'll OCR them).

| # | Book | Needed for | Which parts |
|---|---|---|---|
| 1 | **LIV²**: Rix et al., *Lexikon der indogermanischen Verben*, 2nd ed. (2001) | Phase 1 (verbal root class/aspect) | Whole book; the entries are the point. Wiktionary cites LIV for some roots, which is only a partial stopgap. |
| 2 | **Fortson**, *Indo-European Language and Culture*, 2nd ed. (2010) | Phase 2 (paradigms), Phase 1 spot check | The PIE morphology chapters (the paradigm tables; PLAN cites ch. 6–7), plus its sample text. |
| 3 | **Ringe**, *From Proto-Indo-European to Proto-Germanic*, 2nd ed. (2017) | Phase 2 paradigms, Phase 3b Germanic sound laws | Ch. 2 (PIE) and ch. 3 (PIE → PGmc). |
| 4 | **Mallory & Adams**, *The Oxford Introduction to Proto-Indo-European and the Proto-Indo-European World* (2006) | Phase 1 spot check, vocabulary by semantic field | Whole book. |
| 5 | **Watkins**, *How to Kill a Dragon* (1995) | Phases 4–5 (formulas, the dragon-slaying cluster) | Whole book, especially the formula chapters and the index of formulas. |
| 6 | **West**, *Indo-European Poetry and Myth* (2007) | Phases 4–5, themes table | You have this one. I need it as a PDF or scan. |

Nice to have (lower priority): Schmitt, *Dichtung und Dichtersprache in indogermanischer Zeit* (1967); Beekes, *Comparative Indo-European Linguistics* (2nd ed. 2011), as a second paradigm source; Byrd, *The Indo-European Syllable* (2015), for the meter syllabifier's rules; Lehmann & Zgusta (1979), "Schleicher's tale after a century" (Festschrift Szemerényi), if it isn't transcribed reliably online.

**I'll find these myself:** the kaikki.org PIE dump; Byrd's fable (2013) and *King and the God*; Kortlandt (2007; on his website); Schleicher (1868, public domain); other fable/King versions as transcribed in secondary sources (verified against originals where possible); and the public-domain daughter texts for Tier 2 (Rigveda van Nooten–Holland, Geldner's Avesta, Homer, Neckel's Edda, Whitney's AV).

## Open questions for David

1. **Eval contamination via formulas.** The fixed decision is "eval = all of Tier 1 + a held-out slice of Tier 2". But Tier 1 includes the Watkins/West formulas (*ḱléwos ń̥dʰgʷʰitom*, *gʷʰen- h₃egʷʰim*), and Tiers 2–3 are built *from* those same formulas. So the eval formulas would appear verbatim throughout training. **My recommendation:** eval = Tier 1 *texts* (the fable and King versions, held out whole) + held-out Tier 2. The formula records stay in training, because they are the core poetic vocabulary we want the model to learn. I haven't changed anything yet, since this is your fixed decision.
2. **Remote repo.** The local git repo is initialized, with Phase 0 committed. Do you want a private GitHub repo as well? If so, under which account or org?

## IDEAS.md disposition

Everything in IDEAS.md is folded into PLAN.md, and nothing is rejected outright. These parts were **modified**:

- **Sound-law checker (2).** (a) The Germanic target is **Proto-Germanic**, not Gothic. Wiktionary descendants include PGmc reconstructions, and Gothic needs a further layer of rules; Gothic can be added later. (b) **Inflected forms are checked only against a curated list of regular pairs.** The IDEAS example itself shows why: Gk φέρει is not the regular outcome of *bʰéreti* (the regular one would be *φέρετι), and Lat. *fert* continues an athematic form. A blanket inflected-form check would mostly measure analogy, not engine errors. (c) **Brugmann's law** goes behind a flag with separate counts, because it is contested.
- **Task-format eval (4).** Cognate→PIE eval holds out **whole root families**, otherwise derivatives in training leak the answer. Paradigm exact-match is scored against the golden scholarly paradigms (Phase 2), not only engine output, so the benchmark doesn't just reward imitating our own engine.
- **Modern PIE (5).** Added as Tier 3b, as proposed, with one extra guard: neologisms are **never** loaded into the validator lexicon for Tiers 1–3, so a coinage can't leak into the "plausible archaic" tiers as if it were a real root.
- **Meter (6).** Accepted. It needs one deterministic syllabifier with documented choices (laryngeal vocalization, Sievers' law as a flag), because syllable counts in PIE depend on those choices.
- **Dashboard (7).** The metrics are in STATUS.md now. The HTML Artifact version is deferred until there is data to show (Phase 1+).

## Log

- **2026-10-23. Phase 0.** Set up git, the uv project (Python 3.14), and the directory layout. Built `pie/translit.py` (strict, closed-inventory, reversible), `pie/notation.py` (19 named normalization rules, 4 profiles, applied rules reported per call), and the `scripts/translit.py` CLI, and wrote `docs/notation.md`. The tests caught two real bugs, both fixed: a fixture typed with acute before macron (the strict check correctly rejected it), and `G-CASE` lowercasing a word-final generic `H` (`"" in "₁₂₃"` is True in Python, which is exactly the silent laryngeal corruption the rule log warns about).
