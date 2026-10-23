# Tier-3 review: packet t013 (speeches)

I reviewed this from handbook knowledge only (Fortson, Ringe, Beekes, Meier-Brügger, LIV²-style conventions), without browsing. To check engine forms I used `Lexicon.cells()` and data/lexicon/lexicon.jsonl.

Verdicts are in `docs/audits/packets/t013-verdicts.jsonl`.

## Counts (28 items)

- ok: 15
- minor: 8 (131efd72, 06c4d511, 3fb9faf2, ac9d47bf, ca05fee0, 590a1b91, 64810906, 8ac7583d)
- wrong: 5 (715fe5ee, 8c064899, 70502bea, 457f5394, a3425be0)

## Recurring patterns

1. **Verb person doesn't match the English (planner/realizer slot error).**
   - 715fe5ee: `sddʰí` is 2sg imperative where the English is "let them sit". The coordinated verbs `h₁déntu`, `ph₃éntu` are correct 3pl.
   - 8c064899: `mē bʰebʰih₂ih₁ént` is 3pl optative where the English is "may you not be afraid".

   In both cases the right lexeme got the wrong person cell.
2. **Agreement and case slips.**
   - a3425be0: masc. pl. `lewkṓs` with neuter sg. `péh₂wr̥`.
   - 70502bea: gen. `bʰoydʰéh₂s` used as the object of "give".
   - 3fb9faf2: dual adjective `lewbʰóh₁` with 3pl verb `h₁sih₁ént`. The engine does produce dual verbs elsewhere (131efd72 `wéǵʰetes`).
3. **Lexeme sense.** In 457f5394, `HrewdH-` 'weep' renders English "cries" in the sense of "shouts". Planners must disambiguate "cry".
4. **Negation.**
   - Accented `kʷís … ne` stands for "no one" (131efd72, 457f5394). It reads as the question "who … not?".
   - `ne` + subjunctive stands for "let us not" (ac9d47bf), although the engine correctly uses `mē` for prohibitions elsewhere.
5. **Paradigm variants of doubtful ablaut** (engine and lexicon level):
   - u-stems inflected as proterokinetic with a zero-grade root and a full-grade suffix: `HHḱéwbʰis` (06c4d511), `nh₂éwh₁` (ca05fee0).
   - The alternate nom. pl. `polh₁úes` (715fe5ee) should be `-ewes`.
   - `wédni` (8ac7583d).
   - Accent on the reduplication in `dédh₃yeh₁t` and `dédh₃dʰi`.
   - `undʰí` for `wn̥dʰí` (457f5394).
6. **Scholarly items.**
   - 590a1b91 (King and God) has garbled `wewked` for `wéwkʷet`.
   - 64810906 (Schleicher's fable) lacks syllabic diacritics and has a translation that drops "on a hill".
   - 5c9ff162 (the fable title) is fine.

## View of the speeches

The genre works well. The texts use the inherited formulae appropriately: `ń̥dʰgʷʰitom ḱléwos`, `h₁wésu ḱléwos`, `déh₃tōr h₁uséwōm`, `dyéw ph₂ter`, `h₂éwsos diwés dʰúgh₂ter`. Mood use is mostly idiomatic:
- subjunctive for future and hortative;
- optative for wishes;
- the perfect for states (`wóyde`, `dedwóyh₂e`, `stestóh₂e`);
- correlative `h₁yós … tóm`;
- mē + injunctive.

Vocatives (`ph₂ter`, `súHnew`, `wíḱpotey`, `h₁ń̥gʷney`, `ḱwón`) and enclitic pronouns are handled correctly.

The errors are local slot errors, not systemic grammar failures. Two checks would catch most of them:
- verb person/number checked against the English or the plan;
- predicate-adjective gender/number checked against the subject.
