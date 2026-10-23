# Tier-3 review: packet t012 (28 items, fables)

The review used handbook knowledge only, with no browsing. I checked forms against `data/lexicon/lexicon.jsonl`, `data/morph/inflection_specs.jsonl` and engine `Lexicon.cells()`. Per-item verdicts are in `packets/t012-verdicts.jsonl`.

## Counts

- ok: 12
- minor: 9
- wrong: 7

## Recurring patterns

1. **Person/number errors on the main verb or subject, from the generator rather than the paradigm tables.** The engine cells are correct, but the wrong cell was chosen.
   - 257b8dc2: `gʷétes` is 2sg where 3sg is needed.
   - 4e062e11: `yunégti` is 3sg for "I join".
   - f057535b: `stéygʰome` is a 1pl imperfect where a 3sg aorist is needed.
   - b44a51bd: `h₁ógʷʰih₁` is a dual for "a serpent".
   - a61b6ff2: `ḱérdih₁` is a dual for "his heart".
   - These are the main failure class: 5 of the 7 "wrong" verdicts.
2. **Pronoun gender against the referent.**
   - Neuter `tód` is used for masc. `h₁yégos` "ice" in 9a89d2ac (three times) and 936f2bec, and for fem. `h₂ékʷeh₂` in 1ea0ec34.
   - 9a89d2ac is inconsistent within itself: it also uses masc. `tósmi` for the ice. Rated minor because the meaning is recoverable.
   - The generator seems to fall back to neuter `tód` for "it".
3. **Engine paradigm defects.**
   - `ml̥dúes` should be nom. pl. *ml̥déwes (f0d8de32).
   - `ḱl̥wónts` should be *ḱluwónts (2ebec70f).
   - The loc. `ǵʰémi` should be *dʰǵʰém(i) (a71d2c0a).
4. **Weak lexeme choice.** `wókʷeti` "say" is an o-grade thematic present supported only by Germanic. It is used in 52685852, 7dc023bf and 936f2bec. Smaller points: athematic `déwkmi` (4e062e11), e-grade `gʷéwbʰos` (b44a51bd), and `-kʷe` placed on the first conjunct only (f0d8de32; also `dʰǵʰúHs-kʷe skʷálos` in c195723b).
5. **Scholarly texts.**
   - 25d69709 and 531af602 are Schleicher (1868) in his own pre-laryngeal notation. They are faithful to the source, but as corpus PIE they are wrong. They should be tagged historical, or replaced by a modern version. 531af602 also has a transcription artifact, "wiwidwant- swas".
   - 26b2dc05 (Byrd 2013) is sound, but it uses spellings that differ from corpus conventions: `bʰuged` and `h₂aǵróm`.

## View of the fables

The synthetic fables are mostly good and idiomatic for reconstructed PIE:

- Aspect use is sensible (aorist narrative, imperfect background, gnomic aorist/present in morals).
- Correlative `h₁yós … só` morals work, vocatives are correct, and the prohibitive is `mē` + injunctive.
- Directional accusatives, dative of possession, and impersonal `h₁regʷesyét` all appear.
- Good lexical touches: `ḱléwos ń̥dʰgʷʰitom`, `h₂éwsos diwés dʰúgh₂ter`, `bʰebʰóydʰh₂e`, `tetólh₂e`.

The errors are local: a wrong cell or a wrong pronoun gender, not broken syntax. Each one is easy to fix, but a single one changes the meaning (e.g. "you said", "two serpents"). That points to a validator check that the verb's person/number agrees with the subject and that pronoun gender agrees with the antecedent.
