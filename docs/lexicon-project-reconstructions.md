# Project reconstructions

File: `data/lexicon/project_reconstructions.jsonl`. Policy: PLAN.md, "Project reconstructions" (David, 2026-10-28: "We can invent words that reconstruct well as long as we denote them as such").

## Policy

- A lexeme that is **absent** from the Wiktionary/LIV lexicon (`lexicon.jsonl`) may be added when it is projected from cognates in at least 2 branches through the regular correspondences.
- Every reflex is cited. The `evidence` block names the handbooks: source id from `data/research/literature/bibliography.json`, entry or section, the `raw/books/text/` page file, and a one-line paraphrase of the fact.
- The form must pass `pie/soundlaw.py`. The checker covers only word-initial correspondences in Sanskrit, Ancient Greek, Latin and Proto-Germanic. The number of checks actually run is given for each entry below. An entry with no reflex in those four would pass vacuously, so `tests/test_project_reconstructions.py` requires at least one check.
- At least 2 reflexes must continue the **same formation** (`same_formation: true`). Root-level cognates with other suffixes are listed too, with `same_formation: false`.
- A word that already exists in `lexicon.jsonl` is not duplicated, even when its entry is unusable (no spec, no accent, no gloss). Its repair goes through `overrides.jsonl` and the lexicon build (see "Existing but not offered").
- The flag is `source: "project"`, `coined: "project"`, `meaning_source: "project"`, `confidence: "project"`. Ids are `pie-proj-<ascii>`, so they never collide with `pie-lex-` ids and are easy to grep.

## Schema

Each line is a `lexicon.jsonl` word entry (`id, kind, form, form_ascii, pos, gender, meaning, root_id, reflexes, …`) plus three fields:

- `reflexes{lang: [{form, roman, gloss, same_formation, cite, notes}]}`
- `evidence{handbooks[], branches[], formation, accent, irregularities[]}`
- `inflection`: one row in the `data/morph/inflection_specs.jsonl` schema (`rule: "project"`, `family`, `spec`, `usable`, `backtest_cell_accuracy: null`, `extra_specs`).

`pie.realize.load_project_reconstructions` is the only loader. It splits each line into the entry and its spec.

## Where the flag goes

| Stage | Behaviour |
|---|---|
| `pie.realize.Lexicon.load` | loads the file into `entries` and `specs` (it refuses an id already in `lexicon.jsonl`); `Lexicon.coined(lex_id)` is the one source of the flag (a compound with a project member is coined too) |
| `scripts/make_slice.py` | offers them like other glossed lexemes (`project` is a trusted gloss source); each slice item carries `"coined": "project"` |
| `pie.realize.realize` / `token_cell` | every realized word gets `coined`; corpus tokens built through `token_cell` carry `"coined": "project"` |
| `scripts/realize_plans.py` (Tier 3) | `load_index()` then `index_project(ix)`, so project forms validate at the exact tier (analysis source `engine:project` / `project-lexicon`) |
| `pie.validate.load_index` (Tier 1, Tier 2, `validate_text.py`, formula menu) | never indexes them |
| `scripts/build_tier2.py` | a plan using one (`pie.realize.plan_coined`, including compound members) is rejected |
| `pie.export.record_tasks` | every task of a record with a coined token carries `"coined": "project"` |
| `pie.export.inflection_tasks` | tasks carry `"coined": "project"`; `build` puts them in train only, and drops them when their root family is held out |
| `pie.export.cognate_tasks` | none: the target would be our own projection |
| `pie.export.build` | fails if an evaluation record has a coined token |

## Entries

### *ḱasós* m. "hare" (`pie-proj-kjasos`): thematic, oxytone

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Indo-Iranian | Skt *śaśá-* m. "hare" (ś-ś by assimilation of *ś-s) | yes | EWAia II s.v.; Kroonen s.v. *hesan- |
| Indo-Iranian | Khot. *saha-*, Pashto *soe* "hare" | yes | Kroonen |
| Germanic | PGmc *hasan-/*hazan-* m. (n-stem: OHG *haso*, OE *hara*, ON *heri*) | no (n-stem *ḱas-on-*) | Kroonen |
| Baltic | OPr. *sasins* "hare" | no (-no-) | Kroonen; M&A |
| Celtic | W *ceinach* f. "hare" (*ḱas-n-ih₂-* + -ach; PCelt. *kasni-*) | no | Kroonen; Matasović s.v. *kasni- |
| Italic | Lat. *cānus* "grey" (*ḱas-no-*) | no | Kroonen; M&A |

- Handbooks: Mallory–Adams 2006 §9.2 and §20.4 give *ḱasos* "hare" (named "the grey one"). Kroonen 2013 s.v. *hesan- ~ *hazan-*. Matasović 2009 s.v. *kasni-* (PIE *ḱas- or *ḱh₂es-*). EWAia II s.v. *śaśá-*.
- Sound laws: 3 checks, 0 warnings (Skt satem ś-, Lat. centum c-, PGmc Grimm h-).
- Honest notes: only Indo-Iranian has the thematic stem itself. The other four branches have n-derivatives of the same root and meaning. The root vowel is *a* in M&A and Matasović and *e* in Kroonen; Indo-Iranian *a* cannot decide between them, and the project follows M&A. The oxytone accent is taken from Ved. *śaśá-*.
- Spec: noun, thematic, strong `ḱasó`, m.

### *pṓlHos* m. "foal, young horse" (`pie-proj-poxlHos`): thematic, lengthened grade

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Greek | πῶλος m./f. "young horse, foal, filly" | yes | Beekes s.v.; Kroonen s.v. *fulan- |
| Celtic | W *ebawl* "foal" < *h₁eḱwo-pṓlH-o-* "horse-foal" | yes (as second member) | Kroonen |
| Germanic | PGmc *fulan-* m. (Go. *fula*, ON *foli*, OE *fola*, OHG *folo*) | no (zero-grade n-stem *pl̥H-on-*) | Kroonen; Beekes |
| Albanian | *pelë* "mare" | no (*pṓlH-neh₂*, Kroonen; *pol-n-*, Beekes) | Kroonen; Beekes; M&A |

- Handbooks: Beekes 2010 s.v. πῶλος (IE *polH-, *plH-*). Kroonen 2013 s.v. *fulan-*. Mallory–Adams 2006 ch. 11 (*pelH-* "bear young": NE foal, Alb. pelë, Gk pôlos).
- Sound laws: 2 checks, 0 warnings (Gk p-, PGmc Grimm f-).
- Honest notes: the laryngeal is unidentified (*H*). Kroonen prefers a root noun *pṓlHs*, gen. *pl̥Hós*, behind all the forms. The project takes the thematic formation attested in Greek and Welsh.
- Spec: noun, thematic, strong `pṓlHo`, m.

### *ḱr̥nóm* n. "horn" (`pie-proj-kjrnom`, root `pie-root-kjerh2-head`): thematic neuter

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Germanic | PGmc *hurną* n. (Go. *haurn*, ON/OE/OHG *horn*) | yes | Kroonen s.v. *hurna- |
| Italic | Lat. *cornum* n. (Ter.+, beside the usual u-stem *cornū*) | yes | de Vaan s.v. cornū |
| Italic | Lat. *cornū* n. u-stem (*ḱr̥n-u-*, remade from *ḱr̥n-o-*) | no | de Vaan; Kroonen |
| Celtic | PCelt. *karno-* "horn, hoof" (MW *carn* "hoof", OBret. *carn*, Gaul. κάρνον "Galatian trumpet") | yes | Matasović s.v. *karno-; Kroonen |
| Indo-Iranian | Skt *śṛ́ṅga-* "horn" (*ḱr̥-n-go-*) | no | Kroonen |

- Handbooks: Kroonen 2013 s.v. *hurna-*. de Vaan 2008 s.v. *cornū* (PIt. *kornu-, *korno-*; PIE *ḱr̥n-o-* > *ḱr̥n-u-*). Matasović 2009 s.v. *karno-*. Mallory–Adams 2006 §9.2.
- Sound laws: 4 checks, 0 warnings (Skt satem ś-, Lat. centum c- ×2, PGmc Grimm h-).
- Honest notes: M&A write a laryngeal (*ḱr̥h₂nom*). But *r̥h₂C* would give Lat. and Celt. *rā*, and Lat. *corn-*, Celt. *karn-* show none, so the project follows Kroonen, de Vaan and Matasović. **No daughter preserves the accent.** The oxytone *-óm* is a project convention (as in *yugóm*) and should be read as projected.
- Spec: noun, thematic neuter, strong `ḱr̥nó`, n. Nom./acc. pl. *ḱr̥néh₂*.

### *músih₂* f. "fly (the insect)" (`pie-proj-musih2`, parent `pie-lex-mus`): devī feminine, proterokinetic

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Greek | μυῖα f. "fly" (PGr. *mus-ya*) | yes | Beekes s.v. μυῖα |
| Baltic | Lith. *musė* (dial. *musia*) f. "fly" | yes | Beekes; Derksen s.v. musė |
| Baltic | Latv. *muša* "fly" | yes | Derksen |
| Italic | Lat. *musca* "fly" | no (suffix -k-) | Beekes; Derksen |
| Armenian | *mun* "gnat, mosquito" | no (suffix -n-) | Beekes; M&A |
| Slavic | PSl. *muxa* f. "fly" (< BSl. *mouˀsaˀ*) | no (full grade) | Derksen |

- Handbooks: Beekes 2010 s.v. μυῖα (IE *mus-ih₂*; agrees best with Lith. *musia, musė*). Derksen 2015 s.v. *musė*. Mallory–Adams 2006 §9.5 (*mus-* "fly; gnat, midge, mosquito").
- Sound laws: 2 checks, 0 warnings (Gk m-, Lat. m-; the Latin form is root-level only).
- Honest notes: Beekes notes tabooistic remodelling of the word across the family. The lexicon's `pie-lex-mus` (*mus-* "a fly") is the bare stem, with no reflexes and no paradigm, so it is never usable. This entry is its inflectable *-ih₂* formation, not a second copy of it.
- Spec: noun, devī, strong `músih₂`, weak `musyéh₂`, proterokinetic, f. (the pattern of *néptih₂*). Gen. sg. *musyéh₂s*.

## Rejected

| Word | Why not added |
|---|---|
| fox | **Exists**: `pie-lex-h2wlpis` *h₂wl̥pis* (reflexes PII *lupiš*, PIt. *wolpis*) and kin (*h₂wlōpēḱs*, *h₂lewpis*, *h₂wlopih₂*). None is usable: no accent, `unknown:noun-shape`, no dictionary gloss. The daughters do not converge on one preform: Gk ἀλώπηξ *h₂lōp-*, Lat. *vulpēs* and Av. *urupi-* *wl̥p-*, Skt *lopāśá-* *lōp-*, Lith. *lãpė* *lap-*. M&A write *wl(o)p-*. That irregularity is a reason to fix the attested i-stem by override, not to coin a project form. |
| fly (verb) | Exists and is offered: *péth₂eti*, *péth₂t*. |
| nest | Exists and is usable: `pie-lex-nisdos` *nisdós* m. It is offered whenever "nest" is a slice keyword. |
| beak | Every "beak" word is confined to one branch. PGmc *nabja-* "beak" has "no clear extra-Germanic cognates" (Kroonen s.v.). PCelt. *gulbV-, *gulbino-* "beak" is Celtic-only (Matasović s.v.). Lat. *beccus* "beak" is Celtic (de Vaan s.v. *bucca*). Lat. *rōstrum* is a derivative of *rōdō* "gnaw" (in the lexicon as *Hreh₃dtrom*). |
| hunger (noun) | Single branch: PGmc *hungruz* is the only noun (`pie-lex-knkros` *kn̥krós*, Germanic reflex only). The verb exists: *kénketi* "to feel hunger" (Hesych. κέγκει), plus *gʷl̥dʰ-* "be greedy, hungry". These have derived glosses, offered only with `--derived`. |
| "here" | Exists as `pie-lex-kje` *ḱe* "here" (Lith. *šè* and OIr. *cé* "here"; the lexicon also lists Hitt. *kī*, which means "this", not "here"). It is `indeclinable`, POS `particle`, and enclitic in the validator (ACCENTLESS_LEXEMES), so make_slice's adverb list (adv/prep/postp) never offers it. PGmc *hiar* "here" < *ḱi-or* (Kroonen) is Germanic only. Kroonen also rejects a lengthened *ḱēr*. No two-branch adverb formation, so this is a closed-class matter (see the report). |
| calf | Formations differ by branch: Lat. *vitulus* *wet-elo-* (Italic only; `pie-lex-wetelos` exists, unusable), Skt *vatsá-* *wet-so-* (`pie-lex-wetsos` exists, "having a year"). |
| cheese, pot, axe, knife, frog, owl, neighbour | No cross-branch cognate set (regional or unknown words). |

## Existing but not offered (repair through the lexicon build, not here)

These are in `lexicon.jsonl`, but their specs are unusable or they have no dictionary gloss, so `make_slice.py` never offers them. Each needs a `data/lexicon/overrides.jsonl` row (meaning and/or `spec` + `spec_checked`) and a lexicon/classify rebuild. That rebuild was not run here, because batches were in flight.

- `pie-lex-h2wlpis` fox (i-stem; accent unresolved)
- `pie-lex-mus` fly, bare stem (superseded for use by `pie-proj-musih2`)
- `pie-lex-h1ekjweh2` *h₁éḱweh₂* "mare"
- `pie-lex-h1orseh2` *h₁orséh₂* "tail"
- `pie-lex-wobhseh2` *wóbʰseh₂* "wasp"
- The three above (mare, tail, wasp) are `shape:eh2` with `usable: false`: 391 eh₂-stems are blocked by the shape backtest threshold. This is systemic. The rest of this list is `unknown` / `unknown:noun-shape`.
- `pie-lex-ugwsexn` "bull, ox"
- `pie-lex-sexh2l` "salt"
- `pie-lex-lewH` "louse"
- `pie-lex-bhey` "bee"
- `pie-lex-nid` "nit"
- `pie-lex-kjerh2os` *ḱérh₂os* (Gk κέρας "horn"): usable, but no gloss
