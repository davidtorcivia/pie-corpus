# Reconstructed PIE Corpus: Build Plan

*Revised in Phase 0 (2026-10-23) to fold in IDEAS.md. What was changed or declined is in docs/STATUS.md, under "IDEAS.md disposition".*

Goal: a training corpus of reconstructed Proto-Indo-European text, mostly poetic and mythic (following West, *Indo-European Poetry and Myth*, and Watkins, *How to Kill a Dragon*). It will be used to fine-tune a small model that "speaks PIE." The corpus is **plausible PIE by construction, not recovered PIE**. Provenance tags on every record keep that distinction honest and keep scholarly material separable from synthetic material.

Owner: David. Licensing: fair-use training, cleared. We may seek texts on the web; David can supply books or scans we can't find.

---

## 1. Fixed decisions (do not drift)

### Stage & notation
- **Late PIE (post-Anatolian split, "Brugmannian-plus-laryngeals")**, the stage most reconstructed poetry targets. Anatolian evidence is used for roots and laryngeals, not for morphology.
- Three laryngeals **h₁ h₂ h₃** (also generic **H** in lexicon entries where the color is unknown).
- Three dorsal series: **ḱ ǵ ǵʰ / k g gʰ / kʷ gʷ gʷʰ**. Voiced aspirates are written **bʰ dʰ gʰ**. No glottalic notation.
- Syllabic resonants are written **r̥ l̥ m̥ n̥**, plus **ĺ̥** style where accented. Accent is marked with an acute (é, ó, ḗ, ŕ̥). Long vowels use a macron.
- **Wiktionary/LIV-style conventions** are canonical, because the lexicon backbone comes from Wiktionary.
- Every text field is stored twice:
  - `pie` — canonical Unicode, **NFC-normalized**.
  - `pie_ascii` — reversible ASCII transliteration for tokenizers: `h1 h2 h3 H`, `k' g' g'h`, `kw gw gwh`, `bh dh gh`, syllabic `r_ l_ m_ n_`, accent `/` after the vowel (`e/`), length `:` (`e:`). Write `scripts/translit.py` with round-trip tests **before** any text is produced.
- Sources with different notation (Schleicher, Hirt, Lehmann-Zgusta, Kortlandt, Byrd, glottalic forms) are **normalized to the canonical notation**. The original string is kept in `source_form`. Normalization is a silent-corruption risk, so log every mapping rule in `docs/notation.md`.

### Record schema (JSONL, one sentence/line-unit per record)
```json
{
  "id": "t1-schleicher-byrd-0003",
  "tier": 1,
  "provenance": "scholarly | formulaic | back_projection | synthetic",
  "citation": "Byrd 2013, 'The Sheep and the Horses', line 3",
  "work_id": "schleicher-fable-byrd",
  "work_group_id": "schleicher-fable",
  "line_no": 3,
  "pie": "…NFC…",
  "pie_ascii": "…",
  "source_form": "…original notation, or null…",
  "tokens": [
    {"form": "h₂éwis", "lemma": "h₂éwis", "root_id": "pie-root-h2ewi", "pos": "N",
     "stem_class": "i-stem", "ablaut": "e", "features": "NOM.SG", "verified": true}
  ],
  "gloss": "Leipzig interlinear, morpheme-aligned with tokens",
  "english": "…",
  "genre": "fable | hymn | charm | epic | praise | curse | genealogy | prayer | riddle | law | dialogue",
  "theme": ["dragon-slaying", "imperishable-fame", …],
  "syllables": 11,
  "meter": "free | octosyllable | hendecasyllable | dodecasyllable | null",
  "neologism": false,
  "formulas": ["kleos-ndhgwhitom"],
  "cognate_refs": [{"lang": "Vedic", "locus": "RV 1.9.7", "text": "…"}],
  "alt_reconstructions": [{"pie": "…", "by": "Kortlandt 2007"}],
  "validator": {"status": "pass | warn | fail", "unknown_roots": [], "bad_forms": []},
  "generator": {"model": "…", "engine_version": "…", "prompt_id": "…"} ,
  "notes": "…"
}
```
Field notes (from IDEAS.md, folded in Phase 0):
- `work_group_id` groups versions of the same text across scholars (all Schleicher-fable versions share one), and `line_no` is aligned within the group. This makes Tier 1 a parallel-reconstruction corpus.
- `syllables` is **computed** from `pie` by the syllabifier (`pie/meter.py`). `meter` is set only when the count matches the named meter. It is never a hand label.
- `neologism: true` only in Tier 3b.
- `tier` is an int; Tier 3b records have `tier: 3`, `neologism: true`, and live in `corpus/tier3b/`.

Also keep separate tables:
- `data/lexicon/lexicon.jsonl` — `root_id, root, meaning, root_type (verbal/nominal), aspect (for verbal roots: LIV class), derivatives[], reflexes{lang: [forms]}, source (wiktionary|liv|mallory-adams|…), confidence`.
- `data/formulas/formulas.jsonl` — Watkins/West formulas: `formula_id, pie, english, cognate_attestations[], citation, slot_pattern` (for example `*X-gʷʰen- h₃egʷʰi-`).
- `data/lexicon/neologisms.jsonl` — Tier 3b coinages only: `neo_id, pie, english, derivation (roots + suffixes, each by root_id), model (compound | calque | derivative), rationale`. Never merged into `lexicon.jsonl`.
- `data/themes/themes.jsonl` — West's motifs (sky-father, dawn goddess, dragon-slayer, horse sacrifice, twin horsemen, the poet's craft as weaving/carpentry, …), each with chapter refs and canonical vocabulary.

### Directory layout
```
PLAN.md  docs/  scripts/  pie/ (python package: translit, lexicon, morph, validate)
raw/<source>/          # downloaded material, untrusted; one dir per source; never executed
data/lexicon/ data/formulas/ data/themes/
corpus/tier1/ corpus/tier2/ corpus/tier3/ corpus/tier3b/   # JSONL
export/                # train/eval splits, plain-text views
tests/
```
Rules: downloads go into their own empty dir under `raw/`. Scripts live in `scripts/` and `pie/`. Run Python that reads `raw/` with `python -I`. Use git from day one.

---

## 2. Phases with acceptance checks

### Phase 0: Scaffolding & notation
- git init, python package skeleton, `translit.py` + round-trip tests, `docs/notation.md`.
- **Done when:** NFC↔ASCII round-trip passes on a test list of ~200 tricky forms.

### Phase 1: Lexicon
- Find the **Proto-Indo-European** JSONL on kaikki.org (wiktextract dumps; locate it from the dictionary index, don't guess the URL). Ingest Reconstruction-namespace entries: roots, derived terms, descendants, any inflection tables.
- Normalize notation. Assign stable `root_id`s. Merge homographs carefully (`*bʰer-` "carry" vs others).
- Supplement verbal roots with LIV² class/aspect info where available (ask David for LIV² if it isn't findable).
- **Done when:** ≥2,000 lexical entries, ≥800 verbal roots, all notation-valid, and a spot-check of 50 entries against Mallory & Adams/Fortson shows no systematic errors.

### Phase 2: Morphology engine (`pie/morph.py`)
- **Phase A (gates Tier 3):** thematic o-stems (m./n.), eh₂-stems, i/u-stems, the basic athematic consonant stem; thematic present (*bʰéreti*), athematic root present (*h₁ésti*), primary & secondary active endings, imperative, thematic aorist; personal pronouns, demonstratives *so/seh₂/tod*, *kʷi-/kʷo-*, numerals 1–10.
- **Phase B:** ablaut-accent classes (acrostatic, proterokinetic, hysterokinetic, amphikinetic), r/n heteroclites, sigmatic & root aorist, perfect, subjunctive/optative, middle/mediopassive endings, participles (-ent-, -mh₁no-, -wos-), common derivational suffixes (-tér-, -tó-, -ti-, -mn̥, -yo-).
- Paradigm source: Fortson (ch. 6–7) and Ringe (*From PIE to Proto-Germanic*) as references. Ask David for scans if the tables can't be found.
- **Done when:** golden tests pass for canonical paradigms: *pṓds/pedós*, *wĺ̥kʷos*, *dʰugh₂tḗr*, *ph₂tḗr*, *h₂éwis*, *gʷṓws*, *dyḗws/diwós*, *h₁ésti/h₁sénti*, *bʰéreti/bʰéronti*, *ǵʰeu-*, *gʷʰén-ti/gʷʰn-énti*, *wóyde* (perfect).

### Phase 3: Validator (`pie/validate.py`)
- Tokenize, lemmatize back to root_id via the engine's generated forms (and a lexicon lookup for indeclinables and particles: *-kʷe, *-wē, *nu, *ne, *mē, *h₁e-* augment etc.).
- Flag unknown roots, impossible forms, notation errors, and agreement mismatches (case/number/gender where determinable).
- **Done when:** Tier 1 texts validate at ≥90% token coverage, and every miss is explained (a lexicon gap vs. a scholarly form outside the engine).

### Phase 3b: Forward sound-law checker (`pie/soundlaw.py`, warning-only)
- Apply a small set of approximate sound laws to run canonical PIE forward into **Vedic, Ancient Greek, Latin, Proto-Germanic** (Gothic later, if useful). The set: satem palatal merger and RUKI; Grimm's and Verner's laws; laryngeal coloring, loss and vocalization (including Greek triple reflexes); syllabic resonant outcomes; Grassmann's law and Greek aspirate devoicing; Brugmann's law **behind a flag** (it is contested, so its mismatches are counted separately).
- Compare against the Wiktionary descendants in the lexicon. A mismatch flags a bad lexicon entry, bad normalization, or a missing law. All checker output is **warnings, never rejections**.
- **Scope:** lexical (root/stem) forms against their listed reflexes. Inflected forms are checked only against a curated list of pairs known to be regular. Daughter paradigms are full of analogy: Gk φέρει is not the regular outcome of *bʰéreti*, and Lat. *fert* continues an athematic form. A blanket inflected-form check would mostly measure analogy.
- **Done when:** run over the full lexicon, with the mismatch rate per daughter and per law reported in STATUS, and the top mismatch classes triaged.

### Phase 4: Tier 1, scholarly texts (provenance `scholarly`)
- One subagent per source version (collect text, citation, notation). The main session normalizes, validates and merges.
- Collect every published version of **Schleicher's fable** (Schleicher 1868, Hirt 1939, Lehmann & Zgusta 1979, Danka?, Kortlandt 2007, Adams/Mallory 1997, Byrd 2013, others) and of **The King and the God** (Sihler, Lühr, Kortlandt, Byrd, …). One `work_id` per version and author, one `work_group_id` per text. Align versions line by line (`line_no` shared across a group) as a parallel-reconstruction set. Keep the source notation in `source_form`.
- Collect reconstructed formulas and phrases with citations from Watkins (*How to Kill a Dragon*), West (*IEPM*), Schmitt (*Dichtung und Dichtersprache*), Mallory & Adams, Fortson, and Matasović as far as findable. These go to `formulas.jsonl` **and** as Tier 1 records.
- **Done when:** ~200–500 cited lines/phrases, each with a citation and an English gloss.

### Phase 5: Tier 2, back-projection (provenance `back_projection`)
- For each parallel passage West/Watkins discuss (RV ↔ Avesta ↔ Homer ↔ Edda ↔ Old Irish ↔ Hittite), store the attested cognate texts in `cognate_refs` and produce the reconstructed ancestor phrase. Record which elements are secure (full cognate set) and which are interpolated (in `notes` and token `verified`).
- Priority clusters: dragon-slaying (Indra/Vṛtra, Thor/Jǫrmungandr, Herakles/Hydra, Θraētaona), imperishable fame, the sky-father/dawn hymns, healing charms (Merseburg II ↔ AV 4.12), the Divine Twins, horse sacrifice, "word-weaving/poet as carpenter", the patron's praise and gift exchange, the cattle raid, and death and the otherworld (the river, the dog).
- One subagent per theme cluster. The main session merges after validation.
- Use attested texts from public-domain editions (Rigveda: van Nooten-Holland / Griffith trans.; Avesta: Geldner; Homer; Poetic Edda: Neckel; AV: Whitney).
- **Done when:** ≥300 back-projected lines across ≥8 theme clusters.

### Phase 6: Tier 3, constrained synthetic (provenance `synthetic`)
- Generation loop: an LLM picks a genre + theme + formulas, drafts the **English + a structured plan (lemma, root_id, morphological features)**; the **engine** produces the forms; the LLM may only reorder (SOV default, Wackernagel clitics, verb-initial for emphasis/narrative) and choose particles; the validator gates the output. Generation is never free-form PIE text from the LLM.
- Coverage targets: genres × themes grid from `themes.jsonl`; the vocabulary distribution should reach most of the lexicon (track root coverage).
- Meter is **measured, not labeled.** `pie/meter.py` syllabifies deterministically under documented rules (laryngeal vocalization between consonants, glide/vowel alternation, Sievers' law as a flag). It records `syllables` and the caesura position. A generation target of octo-/hendeca-/dodecasyllable (after Meillet/Watkins) counts as met only if the measured count matches, and `meter` is set only then.
- Batch generation via subagents/workflows. Each batch records generator metadata and a validator pass rate.
- **Tier 3b, "modern PIE"** (`provenance: synthetic`, `neologism: true`, in `corpus/tier3b/`): everyday dialogue, greetings, questions, banter, a model talking about itself. Neologism policy: compounds, calques and derivatives from **attested roots and productive suffixes only**, built through the engine. Every coinage is logged in `neologisms.jsonl` with its derivation. The validator's Tier 1–3 lexicon never includes neologisms. Tier 3b is validated with the neologism table loaded. **Cap: 10–15% of training tokens**, so the archaic register stays dominant.
- **Done when:** ~1–10M tokens, validator reject rate is tracked and <10% after repair, near-duplicate dedup (MinHash) done, and a manual audit of 100 random records is logged in `docs/audits/`.

### Phase 7: Export
- `export/train.jsonl`, `export/eval.jsonl`. Eval = all of Tier 1 + a held-out slice of Tier 2; never train on eval. Plain-text views: PIE-only, PIE+English parallel, interlinear, and ASCII variants.
- **Task-format views** (instruction style), built from every tier where the source supports them:
  - English → PIE and PIE → English translation
  - line → interlinear gloss
  - lemma + features → form, and lemma → full paradigm (from the engine)
  - cognate set (Skt/Gk/Lat/PGmc) → PIE reconstruction (from lexicon reflexes)
  - continue a hymn or charm in the same meter
- **Benchmark** (`export/bench/`) uses the same task types on held-out data:
  - exact match on paradigms (against the Phase 2 golden paradigms, not just engine output)
  - exact match on cognate→PIE, with **whole root families held out**: no task example in training touches a held-out root
  - chrF on translation (Tier 1 lines)
  - "reconstruct in X's style" on the parallel-reconstruction set
  - measured-meter success rate on continuation
- Training setup is format-agnostic. The trainer and base model are chosen later with David.

### Phase 8: Research extensions (approved by David 2026-10-23)
Two uses of the machinery that could add knowledge, not only training data. Both are judged against the daughter languages, never against our own synthetic text.

**8a. Formula discovery.** Watkins found *gʷʰen- h₁ógʷʰim* by noticing cognate words that co-occur across branches. Automate the search:
- Daughter corpora in `raw/daughters/` (licensed or public domain, recorded in `raw/MANIFEST.md`): Rigveda, Homer, plus as available the Avesta, Old Irish, the Poetic Edda and Old English poetry, and Hittite.
- Map daughter word forms to PIE lexemes through the lexicon's reflexes (lemmatized texts where they exist, otherwise reflex matching with a stem table).
- Score each pair of PIE lexemes by co-occurrence within a short window, separately per branch. Candidates are pairs significant in ≥2 branches, ranked by the weakest branch's score.
- **Acceptance:** recall of the known formulas in `data/formulas/formulas.jsonl` (phrase and lexical kinds) at the top 200 candidates, measured before any new candidate is looked at. Known formulas are the test set, so the method is tuned on a held-out half and reported on the other half.
- New candidates go to a review file with their daughter attestations. A candidate is reported as a finding only after an independent reviewer confirms that the attestations are real and not a calque or chance co-occurrence.

**8b. Historical backtest: can a model rediscover the laryngeals?** Saussure inferred missing "coefficients" in 1879 from vowel patterns; Hittite confirmed them in 1915–27. Test whether a model can make that inference from pre-Hittite evidence:
- **Inputs:** attested daughter forms only. Anatolian and Tocharian (published 1908 onward) are removed. So is any language whose forms write laryngeal notation at a noticeable rate: the Wiktionary proto-languages Proto-Indo-Iranian, -Indo-Aryan and -Iranian write *H* in over 40% of forms. Proto-Balto-Slavic's acute also encodes the theory. The primary run uses attested languages only (1,408 cognate sets, 688 with a laryngeal). A secondary run adds the notation-clean proto-languages (PGmc, PItal, PCelt; 1,957 / 960). The excluded list is recorded in the dataset metadata. Romanizations keep length and accent (Skt *ā*, Gk η/ω, Lat macrons): they are the signal.
- **Targets:** PIE written as pre-laryngeal handbooks wrote it (`pie/prelaryngeal.py`), not with laryngeals deleted: coloring (*aǵ-*), long vowels (*dʰē-*, *stā-*, *bʰū-*), schwa (*pətḗr*), loss (*ówis*). The transducer also records each laryngeal's effect and position: the gold standard.
- **Model:** a small sequence or probabilistic sound-change model trained only on that data. **Not an LLM:** any modern LLM already knows laryngeal theory, so its success would prove nothing.
- **Test:** on held-out root families, per-position reconstruction error and output entropy at laryngeal-effect positions vs **context-matched control positions** (same vowel class and length, no laryngeal). A model that "feels" the missing segment is less certain, or errs systematically, exactly there. The stronger variant gives the model k free extra target symbols: are they used systematically at laryngeal positions? Then check whether Hittite *ḫ* falls on the flagged positions, the original confirmation.
- **Acceptance:** the effect must be significant against the matched controls (a shuffled-data baseline is reported too, but it is too weak to count on its own). A positive result is reported with its failure cases; a negative result is reported too.
- **Stated limit:** Wiktionary's cognate grouping already assumes coloring and prothesis (which Greek word belongs to which root). Saussure's Neogrammarian groupings were mostly the same, so the test stands, but the claim is "the inference is recoverable from these correspondences", not "a naive learner would make it".

Both get their own STATUS rows. Subagents do the corpus gathering, model runs and independent reviews.

---

### Gate for every tier: adversarial review
Before Tier 1, 2, 3 or 3b is marked done, an independent "skeptical Indo-Europeanist" subagent reviews a random sample of ≥50 records. It checks ablaut, accent, case use, laryngeal coloring, agreement and, for Tier 2, whether each element is actually supported by the cited cognates. Its findings are logged in `docs/audits/<tier>-<date>.md`. Systematic errors get fixed in the engine, lexicon or normalizer and then regenerated, not patched record by record.

## 3. Things to ask David for early
Ask in the first status message for any of these that can't be found online:
- Fortson, *Indo-European Language and Culture* (2nd ed.): paradigm tables, the sample text.
- Ringe, *From Proto-Indo-European to Proto-Germanic* (2nd ed.).
- LIV² (Rix et al.).
- Watkins, *How to Kill a Dragon*.
- West, *Indo-European Poetry and Myth* (David has this one).
- Mallory & Adams, *The Oxford Introduction to PIE and the Proto-Indo-European World*.
- Byrd's reconstructions (the 2013 fable and *The King and the God*); papers are likely findable online.

## 4. Working norms
- Commit after each phase. Keep `docs/STATUS.md` updated with phase, counts, open questions, and source requests.
- Prefer scholarly forms over invention. When inventing (Tier 3), it must go through engine + lexicon.
- When sources disagree, store alternatives instead of silently picking one.
- Use the high-effort model for design and judgment. Bulk generation can use subagents.
- **Subagents** are approved for parallel, independent work: one per Tier 1 source version, one per Tier 2 cluster, and Tier 3 batches. Design decisions and changes to the engine, validator and normalizer stay in the main session. Subagents produce candidate records, and the main session merges them after validation.
- **Coverage dashboard in STATUS.md:** root coverage %, genre×theme grid fill, validator pass rate, tokens per tier, neologism share, and sound-law mismatch rate. Once data exists (Phase 1+), it can also be published as a small HTML Artifact so David can check it from his phone.
- **Missing sources never block.** Record them under "Need from David" in STATUS.md and move on to other work.
