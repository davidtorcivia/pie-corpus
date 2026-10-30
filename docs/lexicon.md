# Lexicon

Built by `uv run python -I scripts/build_lexicon.py <kaikki dump>` (code: `pie/lexicon.py`). Source: the kaikki.org Proto-Indo-European dump (wiktextract), recorded in `raw/MANIFEST.md`. The build is deterministic and idempotent: a rebuild mints no new ids.

## Files (`data/lexicon/`)

| File | Contents |
|---|---|
| `lexicon.jsonl` | one entry per lexeme (schema below) |
| `paradigms.jsonl` | Wiktionary inflection tables that passed the corruption filter |
| `rejects.jsonl` | every PIE string that could not be normalized, with the reason |
| `id_registry.jsonl` | **persistent** key → id map; committed; never hand-edit ids |
| `build_report.json` | counts, rules fired, unresolved links, root-type disagreements |
| `derived_glosses.jsonl` | approximate glosses (root meaning + suffix function) for unglossed lexemes (`scripts/build_glosses.py`) |
| `reflex_glosses.jsonl` | the daughters' Wiktionary glosses and cited etyma for each unglossed lexeme's reflexes (`scripts/build_reflex_glosses.py`; committed facts, the dumps are not) |
| `confirmed_glosses.jsonl` | reflex-confirmed glosses with their evidence (see "Reflex-confirmed glosses") |
| `neologisms.jsonl` | (Tier 3b, later) coinages; never merged into `lexicon.jsonl` |
| `project_reconstructions.jsonl` | hand-authored lexemes projected from ≥2 branches, `coined: "project"`, Tier 3/3b only; loaded by `pie.realize.Lexicon.load`, never by the build or `load_index` (docs/lexicon-project-reconstructions.md) |

## Entry kinds

| kind | From | Notes |
|---|---|---|
| `root` | headword, POS root | `root_type`, `root_type_source`, `aspect` |
| `word` | headword, other POS | `root_id` via etymon template or tree |
| `affix` | headword, suffix/prefix/infix | leading hyphen kept |
| `derivative` | PIE node in a descendant tree | usually unglossed; `confidence: derivative` or `uncertain` |
| `alt` | "alternative reconstruction of X" | `target_forms`, `target_ids`; `root_id` from target |
| `form` | form-of senses (*h₁sénti* ← *h₁ésti*) | same |

## Schema

```
id                pie-root-<slug>-<gloss tag> | pie-lex-<slug>[-n]
kind              see above
form              canonical NFC lemma, no leading *, internal morpheme hyphens removed;
                  a trailing hyphen marks a bound root/stem, a leading one an affix
form_ascii        translit.to_ascii(form)
segmented         the form with morpheme hyphens, when the source gave them
variants          other canonical spellings: expansions of optional elements
                  ((s)-mobile, ⁽ʷ⁾, (ʰ), tú(h₂)); the full form is the lemma
stems             ablaut stems when the source gave "A ~ B" (first is the lemma)
pos, gender       from Wiktionary; derivatives have pos null
meaning           list of glosses ([] for most derivatives)
root_id           the root this lexeme belongs to (roots: itself)
root_ids          when etymon templates name several roots (compounds)
root_link_source  etymon | tree
root_type         roots only: verbal | nominal
root_type_source  head-template (Wiktionary marked impf/pf/stat/adj) | gloss-heuristic ("to …")
aspect            impf | pf | stat (LIV-style), when Wiktionary gives it
has_verb_derivative  roots: a finite-verb derivative exists (second root-type signal)
accent_class      acrostatic | proterokinetic | hysterokinetic | amphikinetic | …
etymon_parts      morphemes from {{etymon}}: [{form, id_tag, uncertain}]
parents, derivatives  tree links (symmetric)
reflexes          {language: [{form, roman?, via?, notes?}]}; `via` lists intermediate
                  stages (Proto-Germanic for a Gothic form), for the sound-law checker
uncertain         optional-segment | optional-modifier | marked-uncertain
confidence        entry | derivative | uncertain
normalized        notation rules that fired (docs/notation.md)
source, source_ref  wiktionary; dump label, page title, etymology number
```

## Decisions

- **Ids carry a gloss tag on every root, not just on homographs.** That way a future dump that adds a homograph cannot rename an existing id. Wiktionary's etymon ids were *not* usable as disambiguators: kaikki copies one section's id onto its sibling sections, so 8 homograph sets collided (e.g. "think" on *men-* "small, isolated"). Once minted, an id lives in the registry, keyed by (page, POS, etymology number, first gloss, etymon id).
- **Derivatives are deduplicated by canonical form.** A derivative that matches an existing headword merges into it and adds a parent link. A derivative listed under several parents keeps all of them.
- **Paradigms are filtered at the source.** Any table whose template args contain `( Ø ∅ ~ /` is dropped. Wiktionary's module mangles the dual `-h₁` on those stems (`é₁`, `Ø₁`, `s₁`). Tables with any non-canonical cell are dropped too. The surviving tables are **one Lua module's view** (`source: wiktionary-module`). They are a Phase 2 cross-check, not the authority: the golden paradigms come from Fortson/Ringe.
- **Placeholders are rejected, not guessed:** V́, T, Ø, schwa notation, "or"/comma alternative lists, queries with `?`, e/o slashes. Rejects are in `rejects.jsonl`.

## Reflex-confirmed glosses

Most derivatives have no dictionary gloss, only the approximate derived one (root meaning + suffix function, `pie/glosses.py`), which slices offer only with `--derived`. A lexeme gets a real gloss when its own reflexes' dictionary entries agree in at least two branches. Evidence: `data/lexicon/reflex_glosses.jsonl` (`scripts/build_reflex_glosses.py`, from the daughter kaikki dumps in `raw/daughters`; committed because the dumps are not). Rule (`pie.glosses.confirm`), tried in order:

- **head:** a sense of the derived gloss whose content words recur in the reflex glosses of ≥ 2 branches. The gloss is that sense, so it never says more than the derived gloss did (*bʰéndʰeti* 'to bind': PGmc *\*bindaną*, Skt *bandhati*).
- **consensus:** a content word of the *primary* sense (the first sense of the first gloss) of reflexes in ≥ 2 branches, all of the lexeme's part of speech; the gloss is the shortest such primary sense (*lókus* 'lake': Alb. *liqen*, PCelt. *\*loku*). A word deep in a gloss list does not count (Gk νέμω 'deal out, …, enjoy' and Latv. *ņemt* 'take; …, enjoy' do not make *németi* 'to enjoy'). Two unrelated words tied for most branches give no gloss.

A reflex counts only if its entry is linked to the lexeme: its etymology cites the lexeme's form (accents and hyphens ignored), or it is the only entry under that form. Branches come from one table, `pie.glosses.BRANCHES` (also make_slice's). `scripts/build_glosses.py` writes `data/lexicon/confirmed_glosses.jsonl` (with the evidence) after `classify_lexicon.py`; `Lexicon.load` gives those lexemes `meaning_source: "reflex-confirmed"`, so make_slice offers them by default and marks each slice item `gloss_source: "reflex-confirmed"`, for reviews to sample apart. A dictionary gloss or override always wins.

2026-10-30: 121 lexemes (68 head, 53 consensus; péh₃tlom 'drinking vessel, cup' and méh₃yeti now have override glosses: the reflex-confirmed 'to get tired' reversed Kroonen's transitive 'to tire'). As of 2026-10-29: of the 2,300 usable derived-gloss-only lexemes left, 1,340 have linked reflexes in one branch only, 151 in none, 553 have no reflex record, and 256 have linked reflexes in ≥ 2 branches that do not agree under the rule.

## Known gaps

- **Verbal roots are 730**, short of the ≥800 target. Only 116 of those are explicitly marked by Wiktionary. The other 614 come from the gloss heuristic (cross-checked by the derivative signal, which disagrees on 104 roots; the list is in `build_report.json`). Closing the gap needs LIV² or a harvest of PIE etymologies from the daughter-language dumps.
- **344 words or derivatives have no root link.** These are mostly pronouns, particles, and nouns of unclear etymology.
- **The 50-entry handbook spot check** (Mallory & Adams / Fortson) is pending the books. A provisional knowledge-based review is in `docs/audits/`.
