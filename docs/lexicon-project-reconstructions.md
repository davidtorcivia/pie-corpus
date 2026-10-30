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

## Round 2 (2026-10-28)

Requested by the wave-1 planners (judge, witness, owe/debt, sell, swear, sick/illness, spring, grave, long, wait, mounted, beak, sing, love, thank/praise, here, grey, man/human), plus a search for missing everyday words. What happened to each request is in `docs/audits/unusable-requests-round2.md`. Most of the requested words, and most everyday words, **already exist** in `lexicon.jsonl`. They are unusable or have no dictionary gloss, so they are listed there and not duplicated here.

Round 2 adds the first adjectives (`family: "adj"`, thematic: `m_strong` only) and the first verb (`family: "verb"`, thematic present: `strong`, `kind: "impf"`). They use the same engine paradigms as the lexicon's `shape:thematic-adj` and `shape:thematic-present` specs. The nouns use shapes already proven in the lexicon: thematic m., acrostatic i-stem (as *h₁ógʷʰis*) and u-stem (as *bʰébʰrus*). `tests/test_project_reconstructions.py` realizes each entry through `check_plan` + `realize`, and checks that `make_slice.py` offers it flagged.

Sound-law checks, round 2: 17 run, 0 warnings.

| Id | Form | Gloss | Branches (same formation) | Checks |
|---|---|---|---|---|
| `pie-proj-kjasnos` | *ḱásnos* adj. | grey, hoary | Italic, Germanic | 2 (Lat. c-, PGmc h-) |
| `pie-proj-kolsos` | *kólsos* m. | neck | Italic, Germanic | 2 (Lat. c-, PGmc h-) |
| `pie-proj-bhodhHros` | *bʰodʰHrós* adj. | deaf | Indo-Iranian, Celtic | 1 (Skt Grassmann b-) |
| `pie-proj-konHis` | *kónHis* f. | ashes, dust | Greek, Italic | 2 (Gk k-, Lat. c-) |
| `pie-proj-lh2eywos` | *lh₂eywós* adj. | left | Italic, Greek, Slavic | 2 (Gk l-, Lat. l-) |
| `pie-proj-reydheti` | *réydʰeti* | to ride; to move, rock | Germanic, Celtic, Baltic | 1 (PGmc r-) |
| `pie-proj-swerghos` | *swérgʰos* m. | illness, sickness | Celtic, Tocharian | 1 (PGmc s-, root-level) |
| `pie-proj-gwhermos` | *gʷʰermós* adj. | warm, hot | Greek, Armenian (Albanian) | 3 (Skt gh-, Gk th-, Lat. f-) |
| `pie-proj-moghus` | *mógʰus* m. | boy, young man; servant (Celtic) | Germanic, Celtic | 1 (PGmc m-) |
| `pie-proj-keh2ros` | *keh₂rós* adj. | dear, beloved; desired | Italic, Baltic, Germanic, Gaulish | 2 (Lat. c-, PGmc h-) |

### *ḱásnos* "grey" (`pie-proj-kjasnos`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Italic | Lat. *cānus* "white, grey (of hair)" (PIt. *kasno-*) | yes | de Vaan s.v.; Kroonen; M&A |
| Germanic | PGmc *hasna-* (OHG *hasan* "mat, dull"; de Vaan "grey, shining") | yes | Kroonen s.v. *haswa- |
| Italic | Osc. (de Vaan: Pael.) *casnar* "old man" | no (derivative) | M&A; de Vaan |
| Germanic | OE *hasu*, ON *hǫss* "grey" (*haswa-*) | no (-wo-) | Kroonen; de Vaan |

- Handbooks: de Vaan 2008 s.v. *cānus*; Kroonen 2013 s.v. *haswa-* ("OHG *hasan* < *hasna-*, the same suffixation as Lat. *cānus*"); Mallory–Adams 2006 §20.4.
- Honest notes: this is the adjective the hare word (`pie-proj-kjasos`) is named from. The root vowel is *a*, as in the hare word. Germanic's colour sense is weak ("mat, dull"). **Accent: projected.** The root accent *ḱásnos* is consistent with OHG *hasan* (voiceless *s*), but this does not decide it, because West Germanic also levelled *s* in the hare word, where Anglo-Nordic has the Verner variant *hazan-* (Kroonen). For "grey wolf", the better-attested *pelH-wo-* adjective exists but is unusable (`pie-lex-polHwos`; see the audit).
- Spec: adj, thematic, `m_strong` `ḱásno`.

### *kólsos* m. "neck" (`pie-proj-kolsos`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Italic | Lat. *collus* m. (Naev.+), *collum* n. (Cic.+) "neck" (-ll- < *-ls-) | yes | de Vaan s.v. collus; Kroonen |
| Germanic | PGmc *halsaz* m. (Go., ON, OHG *hals*, OE *heals*) | yes | Kroonen s.v. *halsa- |

- Handbooks: Kroonen 2013 s.v. *halsa-* (*kols-o-*); de Vaan 2008 s.v. *collus* ("safer to reconstruct only *kolso-*"); M&A 2006 §11.1.
- Honest notes: de Vaan also allows *kʷol(H)-s-o-*, from the "wheel" s-stem. Kroonen rejects it, since the loss of labialization would be irregular. MIr. *coll* "head" may be a loan from Latin, so it is not counted. **Accent:** root accent, because PGmc *hals-* has no Verner *z*.
- Spec: noun, thematic, `kólso`, m.

### *bʰodʰHrós* "deaf" (`pie-proj-bhodhHros`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Indo-Iranian | Ved. *badhirá-* "deaf" (RV+) | yes | EWAia II s.v.; Matasović; M&A |
| Celtic | OIr. *bodar*, MW *byddar*, Bret. *bouzar* "deaf" (PCelt. *bodaro-*) | yes | Matasović s.v. *bodaro- |

- Handbooks: Matasović 2009 s.v. *bodaro-* (PIE *bʰod(ʰ)Hro-*); EWAia II s.v. *badhirá-*; M&A 2006 §11.7 ("a strong Celtic-Indic isogloss").
- Honest notes: **EWAia calls the Sanskrit word "not clear"** and only allows the Celtic link. The laryngeal is vocalized regularly in both daughters (Skt *i*, Celtic *a*), but it cannot be identified. The oxytone accent is from Vedic.
- Spec: adj, thematic, `bʰodʰHró`.

### *kónHis* f. "ashes, dust" (`pie-proj-konHis`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Greek | κόνις f. "dust, ashes" | yes | Beekes s.v.; de Vaan |
| Italic | Lat. *cinis* m./f. "ashes" (*ken(H)-i-*, the e-grade stem; remade as an s-stem) | yes | de Vaan s.v. cinis |
| Tocharian | B *kentse* "dust; rust" (*kon-is-o-*) | no | de Vaan; M&A |

- Handbooks: de Vaan 2008 s.v. *cinis* ("a PIE i-stem noun *kon(H)i-/*ken(H)-i-*"); Beekes 2010 s.v. κόνις; M&A 2006 §8.2.
- Honest notes: plain *k* or palatal *ḱ* cannot be decided. The laryngeal is only possible (de Vaan writes *(H)*, M&A *kenHis*). Greek generalized the o-grade and Latin the e-grade of one acrostatic paradigm.
- Spec: noun, acrostatic i-stem, strong `kónHi`, weak `kénHi`, f. (the pattern of *h₁ógʷʰis*). Gen. sg. *kénHis*.

### *lh₂eywós* "left" (`pie-proj-lh2eywos`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Italic | Lat. *laevus* "left" | yes | de Vaan s.v.; Beekes; M&A |
| Greek | λαιός (< *λαιϝός) "left" | yes | Beekes s.v. λαιός 1 |
| Slavic | PSl. *lěvъ* AP (c) (OCS *lěvъ*, Ru. *lévyj*) | yes | Derksen 2008 s.v. |
| Tocharian | B *laiwo* "lassitude" | no | de Vaan; M&A |

- Handbooks: de Vaan 2008 s.v. *laevus*; Beekes 2010 s.v. λαιός; Derksen 2008 s.v. *lěvъ* (PIE *lh₂eiwo-*); M&A 2006 §18.3.
- Honest notes: *leh₂i-wo-* (Beekes; de Vaan's first choice) and *lh₂ei-wo-* (Derksen, Schrijver) give the same daughters. The project follows Derksen, because the Slavic accent decides between them. The accent is oxytone (Gk λαιός, Slavic AP c). The lexicon already has a usable "left", *sewyós* (`pie-lex-sewyos`).
- Spec: adj, thematic, `lh₂eywó`.

### *réydʰeti* "to ride" (`pie-proj-reydheti`, root `pie-root-reydh-move_swayingly`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Germanic | PGmc *rīdaną* "to ride; move, rock" (ON *ríða*, OE *rīdan*, OHG *rītan*) | yes | Kroonen s.v. *rīdan-; LIV |
| Celtic | OIr. *réidid*, *-réid* "rides" (PCelt. *red-o-*) | yes | LIV; Matasović s.v. *red-o- |
| Baltic | Lith. *riedu* (*riedėti*) "roll (along)" | yes | LIV; Kroonen |
| Celtic | Gaul. *rēda* "wagon"; PCelt. *wo-redo-* "horse" | no | Matasović |

- Handbooks: LIV² s.v. *rei̯dʰ-* (p. 502: present *réi̯dʰ-e-*); Kroonen 2013 s.v. *rīdan-*; Matasović 2009 s.v. *red-o-*; M&A 2006 §22.17 ("a Celtic-Germanic isogloss").
- Honest notes: this is a north-western verb ("ride" in Germanic and Celtic, "roll" in Baltic). Kroonen and Matasović write an initial laryngeal (*Hreidʰ-*, *(H)reydʰ-*) that no daughter shows, so the project follows LIV. It is a different verb from `pie-lex-h2reydheti` *h₂réydʰeti* "arrange". LIV calls the Baltic acute problematic. This answers the planners' "mounted (on horseback)": the participle *réydʰonts* means "riding", and no adjective "mounted" reconstructs.
- Spec: verb, thematic present, strong `réydʰe`, `kind: "impf"`. 3 pl. *réydʰonti*.

### *swérgʰos* m. "illness" (`pie-proj-swerghos`, root `pie-root-swergh-be_ill`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Celtic | OIr. *serg* m. o-stem "illness" (PCelt. *swergo-*) | yes | Matasović s.v. *swergo-; LIV; M&A |
| Tocharian | A *särk* "illness, sickness" | yes (stem class not certain) | LIV; Matasović; Adams |
| Baltic | Lith. *sergù* (*sir̃gti*) "I am ill" | no (verb, present *swérgʰ-e-*) | LIV; M&A |
| Germanic | PGmc *surgō* f. (Go. *saurga*) "care, sorrow" | no (zero grade, eh₂) | Matasović; LIV |

- Handbooks: Matasović 2009 s.v. *swergo-*; LIV² s.v. *su̯ergʰ-* (pp. 613–614); Adams 2013 s.v. *sark* (TchA *särk* "sickness" is undoubted); M&A 2006 §11.7 ("its PIE status is guaranteed").
- Honest notes: only OIr. *serg* is certainly thematic. Toch. A *särk* matches it in root and meaning, but its stem class is not certain. The checker's one correspondence (PGmc *s-*) is on the root-level cognate *surgō*. No daughter preserves the accent. Albanian *dergjem* "lie ill" belongs to *derHgʰ-* (LIV).
- Spec: noun, thematic, `swérgʰo`, m.

### *gʷʰermós* "warm" (`pie-proj-gwhermos`, root `pie-root-gwher-be_warm`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Greek | θερμός "warm, hot" | yes | Beekes s.v.; de Vaan |
| Armenian | *ǰerm* "warm" | yes | Beekes; de Vaan |
| Albanian | *zjarm* "heat, fire" | yes (de Vaan: "maybe") | Beekes; de Vaan |
| Indo-Iranian | Skt *gharmá-* m. "heat"; Av. *garəma-* "warm; heat" | no (o-grade *gʷʰormó-*) | EWAia I s.v.; de Vaan; Beekes |
| Italic | Lat. *formus* "warm" | no (o-grade) | de Vaan s.v. formus |
| Baltic | OPr. *gorme* "heat" | no (o-grade) | de Vaan; Beekes |

- Handbooks: de Vaan 2008 s.v. *formus*; Beekes 2010 s.v. θερμός; EWAia I s.v. *gharmá-*; M&A 2006 §20.9 ("almost ubiquitous").
- Honest notes: there are two ablaut grades. The e-grade *gʷʰermó-* is in Greek and Armenian; the o-grade *gʷʰormó-* is in Indic, Iranian, Latin and Baltic. The project takes the e-grade adjective. The lexicon has the root's nouns (*gʷʰérmn̥* "warmth", *gʷʰéros* "heat") but no adjective.
- Spec: adj, thematic, `gʷʰermó`.

### *mógʰus* m. "boy, young man" (`pie-proj-moghus`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Germanic | PGmc *maguz* (Go. *magus* "boy", OE *magu* "child, young man, son") | yes | Kroonen s.v. *magu-; Matasović |
| Celtic | OIr. *mug* u m. "servant"; Corn., Bret. *maw* "boy" | yes | Matasović s.v. *mogu-; Kroonen; M&A |

- Handbooks: Kroonen 2013 s.v. *magu-*; Matasović 2009 s.v. *mogu-* (PIE *mogʰ-u-* "young person"); M&A 2006 §12.1.
- Honest notes: this is a West European word; Kroonen calls it "of obscure origin". Celtic *mogu-* needs *o*, and Germanic *a* is the regular reflex of *o*, so *mogʰ-u-* (Matasović) fits both. Kroonen and M&A write *a*, and Gaulish *Magu-* is unexplained. The accent and the proterokinetic pattern are projected. The feminine *mogʰwih₂* "girl" (Go. *mawi*) is not added.
- Spec: noun, u-stem, strong `mógʰu`, weak `mogʰéw`, proterokinetic, m. (the pattern of *bʰébʰrus*).

### *keh₂rós* "dear" (`pie-proj-keh2ros`)

| Branch | Reflex | Same formation | Cited |
|---|---|---|---|
| Italic | Lat. *cārus* "dear, precious" | yes | de Vaan s.v.; Kroonen |
| Baltic | Latv. *kārs* "lecherous, greedy" | yes | de Vaan; Kroonen |
| Germanic | PGmc *hōraz* "adulterer" (Go. *hors*) | yes | Kroonen s.v. *hōra- 1 |
| Celtic | Gaulish names in *Cara-*, *-carus* | yes | de Vaan |
| Celtic | OIr. *caraid* "loves" | no (*kh₂-r-eh₂-ye-*) | Kroonen; de Vaan |

- Handbooks: de Vaan 2008 s.v. *cārus* (PIE *keh₂-ro-* "desired"); Kroonen 2013 s.v. *hōra-* 1.
- Honest notes: the meaning splits into "dear" (Latin, Gaulish), "lustful" (Latvian) and "adulterer" (Germanic). The project glosses the Latin sense. The oxytone accent is projected from the usual accent of *-ro-* adjectives; no daughter preserves it. *lewbʰós* and *priHós* are other usable words for "dear".
- Spec: adj, thematic, `keh₂ró`.

### Rejected in round 2

| Word | Why not added |
|---|---|
| man, human (*mánus*) | Kroonen s.v. *mannan-*: PGmc *mann-* cannot come from *men-u-/*mon-u-* and is better taken from *dʰǵʰm-on-*. That leaves Skt *mánu-* alone. Existing words: see the audit. |
| sand (*samh₂dʰos*) | Kroonen s.v. *samda-*: Gmc *samda-*, Lat. *sabulum* and Gk ἄμαθος are irreconcilable, so the word is of non-IE origin. |
| boar (*h₁eperos*) | Kroonen s.v. *ebura-*: Gmc *epr-*, It. *apr-* and Slav. *wepr-* alternate irregularly, so it is probably not inherited. |
| thrush (*trosdos*) | Kroonen s.v. *þrastu-*: the initial differs in every branch (Lat. *torzd-*, Lith. *strozd-*, Slav. *drozd-*, Arm. *dorzdh-*). |
| willow (*salik-*) | de Vaan s.v. *salix*: the *-ik-*/*-k-* interchange is hardly IE, so the word is probably non-IE. |
| starling, lynx | Formations and initials diverge (de Vaan s.v. *sturnus*; Kroonen s.v. *luhsa-*). |
| salmon (*loḱs-*) | Kroonen posits a hysterokinetic s-stem (*lóḱ-os*, gen. *loḱ-s-ós*). The daughters continue different stems of it, and the engine has no such paradigm. Deferred. |
| wax (*woḱso-*) | Gmc *wahsa-* vs BSl. *wosk-*: metathesis, so the formation is uncertain (Kroonen). |
| boil (*bʰérweti*) | LIV puts W *berw-* with Lat. *fervō*, but Matasović takes the Celtic verb as denominative. With Latin alone, the case is too weak. The lexicon's *yéseti* "to be boiling" is usable. |
| hope (*wélpeti*) | LIV: the verb is only Greek (ἔλπομαι); Lat. *volup* is an adverb. |
| rot (*puHyéti*) | LIV: the *yé*-present is only Indo-Iranian. |
| wait (*th₂usyéti*) | LIV: only Hitt. *tuḫḫušiya-*. |
| kid (*ǵʰaydos*) | Only Lat. *haedus* is thematic; Gmc *gait-* is another stem. |
| load, burden (*h₃énos*) | Exists and is usable: `pie-lex-h3enHos` *h₃énHos* "load; burden" (Lat. *onus*, Skt *ánas-*), offered under the keywords `load` and `burden`. A draft project entry was removed after the validator found the homograph. |
| sweep, cauldron, flower | Sweep exists (`pie-lex-wrseti`, derived gloss). The cauldron *u*-stem is only Skt *carú-*. Flower exists (`pie-lex-h2endhos` "bloom", usable). |

## Round 3 (2026-10-30, dialogue gaps)

Requested by the t3b dialogue planners and the translator. The full ladder (lexicon fix → project → neologism) for all 15 concepts is in `docs/audits/lexicon-gaps-dialogue-2026-10-30.md`. Two concepts reached this file. Sound-law checks: 3 run, 0 warnings.

| Id | Form | Gloss | Branches (same formation) | Checks |
|---|---|---|---|---|
| `pie-proj-spelom` | *spélom* n. | story, tale, legend | Germanic, Armenian | 1 (PGmc s-) |
| `pie-proj-h2enHos` | *h₂énHos* f. | grandmother | Anatolian, Armenian | 2 (Gk, Lat. a- < *h₂e, root-level) |

- *spélom*: PGmc *spellą* "story, tale" (Kroonen *spel(H)-o-*) and Arm. *aṙaspel* "myth, tale" (Martirosyan: *aṙ-* + *spel-*, the same formation as OHG *bī-spel*). Kroonen counts the Armenian only at the root level, and the Germanic *-ll-* (laryngeal?) is unexplained. The accent is projected (as in *wérǵom*). Spec: thematic neuter `spélo`.
- *h₂énHos*: Hitt. *ḫanna-* (a-stem) and Arm. *han* (o-stem) "grandmother" (Kloekhorst *h₂enHo-*; Martirosyan). Root-level cognates: Lat. *anus*, OHG *ana*, OPr. *ane*. The *-H-* is Kloekhorst's, from the Hittite geminate. Gender f and the accent are projected. Spec: thematic `h₂énHo`, f.
