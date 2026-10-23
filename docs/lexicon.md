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
| `neologisms.jsonl` | (Tier 3b, later) coinages; never merged into `lexicon.jsonl` |

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

## Known gaps

- **Verbal roots are 730**, short of the ≥800 target. Only 116 of those are explicitly marked by Wiktionary. The other 614 come from the gloss heuristic (cross-checked by the derivative signal, which disagrees on 104 roots; the list is in `build_report.json`). Closing the gap needs LIV² or a harvest of PIE etymologies from the daughter-language dumps.
- **344 words or derivatives have no root link.** These are mostly pronouns, particles, and nouns of unclear etymology.
- **The 50-entry handbook spot check** (Mallory & Adams / Fortson) is pending the books. A provisional knowledge-based review is in `docs/audits/`.
