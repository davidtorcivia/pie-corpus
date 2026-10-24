# Tier 3 review: packet t018 (journeys)

Reviewer: skeptical Indo-Europeanist pass, handbook knowledge only (no browsing). Forms were checked against `data/lexicon/lexicon.jsonl` and engine cells (`Lexicon.cells`) where a lexeme was in doubt.

## Counts (28 items)

- ok: 16
- minor: 5 (ed50b7d2, ae097cb0, 3e807605, 52d42eae, 6b86294c)
- wrong: 7 (5c1e20a7, df0c37b3, 7cc8cff8, a9f3a01b, 75498ae9, e55b09ae, 7bec3ebd)

## Recurring patterns

1. **Wrong person, number or case cell picked from an otherwise correct paradigm** (the main failure). The form exists in the paradigm, but the plan chose the wrong cell:
   - 5c1e20a7: optative 3DU `h₂ḱh₃ih₁tā́m` with a singular subject.
   - e55b09ae: aorist 1DU `pr̥wé` for 'he crossed'.
   - a9f3a01b: 3pl imperative `bʰérontu` addressed to one boatman.
   - df0c37b3: gen. pl. `h₂n̥rṓm` as the subject 'a man'.
   - 75498ae9: dat./abl. pl. `h₂usbʰós` as the subject 'Dawn'.

   The validator should check that the subject is nominative and that the verb's person and number match the subject or addressee.
2. **Anaphor gender follows the wrong antecedent.** In 7cc8cff8, fem. `h₁íh₂m̥` refers to the neuter silver.
3. **Lexeme picked by surface form, not by sense.** In 7bec3ebd, `h₂ewseti` ('draw water', unaccented in the lexicon) is used for 'singe' instead of `h₁éwseti` (burn).
4. **Dual agreement is inconsistent.** Two conjoined subjects get dual verbs (good: `ih₂tā́m`, `lm̥bʰih₁tā́m`, `tr̥h₂tā́m`). Two addressees or two speakers get plural imperatives or 1pl forms instead (7bec3ebd, a9f3a01b).
5. **Paradigm-table issues** (minor, engine-wide):
   - The eh₂-stem dual `-eh₂h₁` is identical to the instr. sg. (52d42eae); the handbook form is *-eh₂-ih₁.
   - `déh₂nu` is a neuter noun used as a 'river goddess' (ed50b7d2).
6. **Schleicher 1868 lines** (ae097cb0, 3e807605) are faithful to the source but appear in pre-laryngeal notation. Per PLAN.md, they should be normalized, or at least clearly flagged as historical with the original kept in `source_form`. Byrd-style 95f54829 is fine.

## Points checked and accepted

These forms looked doubtful but pass on the handbook or lexicon evidence:

- `Hrunépeti` is a correct short-vowel subjunctive in a generalizing relative clause.
- `h₁áyt`/`h₁áyto` ('give' active / 'take' middle) and `h₁opéye-` ('make reach, give') are both lexicon-backed.
- `wéwket` follows the boukólos rule.
- `h₁énoy` is the pronominal nom. pl. (the engine lists it as loc. sg., but the form in the text is right).
- `ḱl̥niyó` takes the secondary middle 3sg in *-o.
- `widḗsi` is the subjunctive of a thematic aorist.
- The proterokinetic u-adjectives (`HéHḱu-`, `pléth₂u`, `bʰérǵʰu`) are a defensible convention, though *h₁oh₁ḱú-/*pl̥th₂ú- with zero grade and oxytone accent is the more common handbook citation.

## Overall view

The narrative texts are idiomatic and mostly well built:

- Correct ablaut in root aorists and nasal presents.
- Good modal choices: subjunctive for 'I shall', optative for wishes, mē + injunctive for prohibitions.
- Sound correlative relatives (`h₁yós … só/tóm`).
- `-kʷe` placed correctly throughout.
- Neuter plurals take singular verbs.

The errors are local cell or agreement slips, not systematic morphology failures. They are cheap to fix at plan level, and agreement checks in the validator would catch most of them.
