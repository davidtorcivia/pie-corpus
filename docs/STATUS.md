# Status

**Current phase:** Phase 2, the morphology engine. Layer 1 (stem spec → paradigm) is built and regenerates Wiktionary's tables at 98.9% cell agreement, with every mismatch triaged. Next: Layer 2 (lemma → spec, the real Tier 3 gate), then Phase 3 (validator). Phases 1 and 2 are both "built, acceptance pending books".

## Phases

| Phase | State | Acceptance |
|---|---|---|
| 0 Scaffolding & notation | **done** | NFC↔ASCII round-trip on ≥200 tricky forms: **pass** (382 listed forms: 157 hand-written with expected ASCII + 225 generated; plus 5,000 fuzzed; 1,807 tests) |
| 1 Lexicon | **built, acceptance pending** | ≥2,000 entries: 2,226 glossed, 7,401 total ✅ · ≥800 verbal roots: **730** ❌ · 50-entry handbook spot check: pending books (provisional review in `docs/audits/`) |
| 2 Morphology engine | **Layer 1 built**; Layer 2 next | Wiktionary regeneration: 11,136/11,255 cells (98.9%), 582/615 tables, **0 unexplained** ✅ · PLAN golden paradigms: 11/11 pass, but the source is unverified (pending Fortson/Ringe) |
| 3 Validator | — | Tier 1 ≥90% token coverage |
| 3b Sound-law checker | — | full lexicon run, mismatch report |
| 4 Tier 1 scholarly | — | 200–500 cited lines + adversarial review |
| 5 Tier 2 back-projection | — | ≥300 lines, ≥8 clusters + adversarial review |
| 6 Tier 3 / 3b synthetic | — | 1–10M tokens, <10% reject, dedup, audit |
| 7 Export + benchmark | — | splits, task views, bench |

## Dashboard

| Metric | Value |
|---|---|
| Lexicon entries | 7,401 total: 885 roots · 893 words · 110 affixes · 5,470 tree derivatives · 22 alt · 21 form-of |
| Glossed entries | 2,226 |
| Verbal roots | 730 (116 marked by Wiktionary + 614 by the "to …" gloss heuristic; 104 disagree with the derivative signal) |
| Wiktionary paradigms (clean) | 625 (90 dropped as module-corrupted, 1 with a non-canonical cell) |
| Normalization rejects | 67 (alternative lists, queries, placeholders) |
| Root coverage in corpus | — |
| Engine agreement with Wiktionary tables | 98.9% of cells (docs/morphology.md) |
| Inflectable lexicon entries (Layer 2 coverage) | — (next) |
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

## Phase 1 notes

- **The source is clean.** Only 4 of 1,931 headwords are outside the inventory. Normalization fired 14 times (3 homoglyphs, 6 laryngeal rings, 5 dot-below syllabics). The `\w` escape occurs in 17 forms.
- **Wiktionary's declension module corrupts some tables.** Where a stem template has parentheses or Ø, the dual `-h₁` becomes `é₁`/`Ø₁`. Those 90 tables are excluded at the source.
- **Wiktionary etymon ids can't disambiguate homographs.** kaikki copies them across sibling sections, so 8 homograph sets collided. Root ids therefore carry a gloss tag on every id (`pie-root-men-think`, `pie-root-men-stay`) and persist in a committed registry. Rebuilds are idempotent.
- **Provisional review** (subagent, knowledge-only, 50 entries): 20 ok, 26 questionable, 4 wrong. The triage is in `docs/audits/phase1-lexicon-provisional-review.md`. It found **one real builder bug**: same-form derivatives under different homograph roots were merged, e.g. two *kretós*. Fixing it split 140 homonyms. Duplicate reflexes and unflagged loans are fixed as well. The other 3 "wrong" links are Wiktionary's own placements, logged as disputed. The id registry was reset once for this fix; safe because nothing references ids yet.
- **Gaps:** 730 verbal roots (see the question below); 344 words/derivatives with no root link (mostly pronouns, particles, opaque nouns); 58 etymon parts that point at ambiguous homographs.

## Open questions for David

All in one place. None of these block work in progress; each one has a default that I'm using until you decide.

1. **Eval contamination via formulas.** The fixed decision is "eval = all of Tier 1 + a held-out slice of Tier 2". But Tier 1 includes the Watkins/West formulas, and Tiers 2–3 are built *from* them, so eval would leak into training. **Recommendation:** eval = Tier 1 *texts* (fable and King versions, held out whole) + held-out Tier 2, with the formula records kept in training. *Default until you decide:* records are tagged so either split can be cut later.
2. **Phase 1 targets.**
   - (a) May the "≥2,000 entries" target be met by *glossed* entries (2,226)? The 5,470 unglossed tree derivatives are a separate, lower-confidence kind.
   - (b) Verbal roots are 730, against a target of 800. The options are **LIV²** (authoritative; also supplies aspect for the 614 roots classified by gloss), or a harvest from the kaikki daughter-language dumps (more roots, no aspect). *Default:* waiting for LIV².
3. **Paradigm convention for corpus text.** I read "Wiktionary/LIV conventions are canonical" (PLAN §1) as being about *notation*, not paradigm reconstructions, so corpus text defaults to the **handbook** forms (contracted thematic *-ōs/-ōy/-ōd*, as in the Tier 1 texts). Wiktionary-convention forms are kept as alternatives in every cell. The tiebreaker will be Phase 3 validator coverage on Tier 1 texts under each convention. Tell me if you meant the stricter reading.
4. **GitHub.** The repo is local only. Do you want a private remote, and under which account?

## IDEAS.md disposition

Everything in IDEAS.md is folded into PLAN.md, and nothing is rejected outright. These parts were **modified**:

- **Sound-law checker (2).** (a) The Germanic target is **Proto-Germanic**, not Gothic. Wiktionary descendants include PGmc reconstructions, and Gothic needs a further layer of rules; Gothic can be added later. (b) **Inflected forms are checked only against a curated list of regular pairs.** The IDEAS example itself shows why: Gk φέρει is not the regular outcome of *bʰéreti* (the regular one would be *φέρετι), and Lat. *fert* continues an athematic form. A blanket inflected-form check would mostly measure analogy, not engine errors. (c) **Brugmann's law** goes behind a flag with separate counts, because it is contested.
- **Task-format eval (4).** Cognate→PIE eval holds out **whole root families**, otherwise derivatives in training leak the answer. Paradigm exact-match is scored against the golden scholarly paradigms (Phase 2), not only engine output, so the benchmark doesn't just reward imitating our own engine.
- **Modern PIE (5).** Added as Tier 3b, as proposed, with one extra guard: neologisms are **never** loaded into the validator lexicon for Tiers 1–3, so a coinage can't leak into the "plausible archaic" tiers as if it were a real root.
- **Meter (6).** Accepted. It needs one deterministic syllabifier with documented choices (laryngeal vocalization, Sievers' law as a flag), because syllable counts in PIE depend on those choices.
- **Dashboard (7).** The metrics are in STATUS.md now. The HTML Artifact version is deferred until there is data to show (Phase 1+).

## Log

- **2026-10-23. Phase 2 (Layer 1).** Built `pie/phon.py` (segments; junction syllabification; Szemerényi, Stang, boukólos; Wiktionary-only Pinault and perfect laryngeal loss), `pie/morph.py` (thematic, eh₂, athematic in 4 accent classes, devi feminines, adjectives, thematic/athematic presents, aorists, perfects; `handbook` and `wiktionary` conventions with alternatives), the cross-check harness, and the mismatch classifier. Agreement went 89.6% → 98.9% as each mismatch class was triaged. Bugs found that way include Stang's law never firing after syllabification. Also wrote 11 golden paradigms (flagged unverified) and closed-class hand tables. 1,896 tests. Details in `docs/morphology.md`.

- **2026-10-23. Phase 1 (built).** Found the dump via the kaikki.org index and logged it in `raw/MANIFEST.md`. Built `pie/lexicon.py` and `scripts/build_lexicon.py`, wrote the schema in `docs/lexicon.md`, and added two normalizer rules (G-HOMOGLYPH, G-LAR-RING). Lexicon tests cover form parsing, id/link integrity, parent/child symmetry and paradigm cleanliness (1,838 tests in total). A provisional reviewer subagent is auditing a stratified 50-entry sample.

- **2026-10-23. Phase 0.** Set up git, the uv project (Python 3.14), and the directory layout. Built `pie/translit.py` (strict, closed-inventory, reversible), `pie/notation.py` (19 named normalization rules, 4 profiles, applied rules reported per call), and the `scripts/translit.py` CLI, and wrote `docs/notation.md`. The tests caught two real bugs, both fixed: a fixture typed with acute before macron (the strict check correctly rejected it), and `G-CASE` lowercasing a word-final generic `H` (`"" in "₁₂₃"` is True in Python, which is exactly the silent laryngeal corruption the rule log warns about).
