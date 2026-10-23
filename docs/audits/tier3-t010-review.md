# Tier-3 review, packet t010 (everyday life: narratives, dialogues, instructions)

Reviewer: Claude, acting as a skeptical Indo-Europeanist. **Handbook knowledge only; no browsing.** I checked forms against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json`, engine paradigms (`Lexicon.cells`) and `pie/validate.py`. The validator passes every engine item, but it does not check person, number or gender. All the verb-ending errors below were found by reading the texts.

Verdicts: `docs/audits/packets/t010-verdicts.jsonl`.

## Counts (28 items)

| verdict | n |
|---|---|
| ok | 15 |
| minor | 7 |
| wrong | 6 |

## Recurring patterns

1. **Wrong person or number ending on a verb (engine items).** These are the most serious errors in the packet.
   - 08080029: `gʷʰnént` (3pl) used for "I slew"; it should be `gʷʰénm̥`.
   - 883efcf8: `dedwóyth₂e` (2sg perfect) used for "he was afraid"; it should be `dedwóye`.
   - 4c8eb5be: `gʷh₂tā́m` (3du) used for a 2sg imperative; it should be `gʷh₂dʰí`.

   In each case the text is otherwise well formed. This looks like the engine choosing the wrong cell, not using a bad paradigm.
2. **Malformed form from a bad stem spec.**
   - d32bb249: `dʰdʰeh₁dʰí`. The spec for `dʰédʰeh₁ti` gives the weak stem as `dʰdʰeh₁`; it should be `dʰedʰh₁-`. Any weak-stem cell of "put" will be wrong.
3. **Expletive `tód` with the impersonal "it grows bright" (h₂wes-).**
   - 3e6da3e0 and 32b4084a.

   The engine leaves `h₂wérst` "it rained" and `h₁regʷesyét` "it was getting dark" without a subject, which is correct, but adds `tód` to h₂wes-.
4. **Dual/plural drift for two referents.**
   - f169ab24: `tóy … tetr̥pḗr` between dual verbs.
   - 883efcf8: `widónt` for the man and the dog.
   - 9c57a481: `dʰh₁ént`.

   Homer tolerates this, but a dual-marking text should stay consistent.
5. **Agreement and case slips in nouns and adjectives.**
   - 3c97295c: `h₁wésuh₂` (neuter plural) with singular `ḱléwos`. The engine has no neuter cells for u-stem adjectives.
   - 322ea6fe: the vocative `h₂éwsos` used as the subject.
6. **Scholarly / Schleicher-tradition items (0f252df0, a403b478, 8b198596).** These are not engine output. They use mixed or older notation: no laryngeals, `kʷe` written as a separate word, `aǵrom`. They also have real errors:
   - 0f252df0: `ewewkʷ` has no ending and is not plural; `kʷnewti` should be `kʷr̥néwti`; "wool" is spelled two different ways.
   - 8b198596: `ḱeḱlōts` should be `ḱeḱluwṓs`.

   They clash with the corpus conventions and should be normalized or dropped.

Smaller notes:
- 9c57a481 uses `kʷékʷloy` ("wheel") to mean "wagon".
- d32bb249 switches from 2sg to 2pl imperatives.
- `wéh₁ikos` ("enclosed") is used as a noun meaning "enclosure"; this is acceptable.

## Overall view

The engine texts are mostly good: ablaut, laryngeals and accent are generally handbook-correct. Highlights:
- the root-aorist imperatives `gʷʰn̥dʰí`, `bʰudʰdʰí`, `dh₃dʰí`
- the subjunctive in `h₁yód` clauses (`gʷm̥yḗti`, `yésēti`)
- Stang's-law `gʷṓs`
- correct oblique pronoun genders (`tā́m`/`tā́s` for sheep and wool, `tóm` for wolf and spear, `tód` for the neuter `h₂éǵmn̥`)
- prohibitive `mē` + injunctive

The errors are discrete and mechanical: wrong person endings, one bad stem spec, the expletive `tód`. They are not systematic misunderstandings, but the person-ending errors (3 of 25 engine items) are serious enough to need a targeted check: a subject/verb person–number consistency test, which the validator lacks.
