# Tier-3 review: packet t015 (law and custom)

Reviewer: skeptical Indo-Europeanist pass, handbook knowledge only (Fortson, Ringe, Beekes, LIV-style conventions as I know them). No browsing. Checked against data/lexicon, data/morph/closed_class.json, engine paradigms (`Lexicon.cells`), and `validate_text`.

Verdicts: /Users/david/AI/PIE/docs/audits/packets/t015-verdicts.jsonl

## Counts (28 items)

- ok: 15
- minor: 7
- wrong: 6

Severity rule: "wrong" means a single form that by itself encodes the wrong grammatical relation, such as the wrong person, a wrong case for a subject or address, or an agreement clash, so the sentence no longer says the English. "minor" means the meaning can still be recovered: a sense stretch, notation, an inconsistency between number and person across sentences. f615d926 is minor by this rule: the 2pl/2du mixing still points to the same two sons, and `tóh₁` "to them" can be read as an accusative of goal.

## Recurring patterns

1. **Wrong person in the verb (the engine produced the wrong person).** 82f62c5e `gʷm̥yóh₂` (1sg) for "the wolf comes" (3sg); 3f71a618 `h₁ésmi` (1sg) for "you are" (2sg). Both are surface errors in otherwise sound texts, so a check that the verb's person matches the subject should catch them.
2. **Case slips on nominals in address and adjuncts.** 791b7863 `méh₂ter` (voc.) used as the subject; d6f161d4 `dyéw ph₂térm̥` (acc. in place of voc.; the validator also flags this as an agreement mismatch); fa326bd3 `stéygʰes` (nom. pl.) for "on the path". The same plan elements come out right in other items (`dyéw ph₂ter` in fa326bd3, `stéygʰi` in b8674ce8, nom. `méh₂tēr` later in 791b7863), so the problem is case selection, not the paradigms.
3. **Number of addressees mixed.** f615d926 addresses the two sons in 2pl (`ǵeǵn̥h₁é`, `wos`) and then 2du (`stundtóm`), and uses nom./acc. du. `tóh₁` where the sense needs a dative.
4. **Lexeme sense stretched.** b8216b7b HréwdH- 'weep, wail' used for calling cattle; 6f3b7876 somHós 'same' used for 'lone'; 9012a653 kʷyéh₁tis 'rest, quiet' (the lexicon itself says "not a treaty") for the peace that settles a blood-price. Milder cases, not downgraded: kʷyéh₁tis again in 34275dcc and 353a7ffc (borderline, since 'quiet' fits there); lelóykʷe 'has left' for "is gone" (b8674ce8, dd011ec3); gʷerh₃- 'swallow, devour' for "ate" (cda613bd); kʷékʷlom 'wheel' for "cart" (b93aa54d, 3a367b11); kúdʰe 'where (at)' for "where to" (791b7863).
5. **Lexicon/engine form issue.** kn̥h₂ónks keeps the nom. -s in every cell (gen. kn̥h₂ónksos), so the accusative in b4723299 is wrong. The fix belongs in the source paradigm.
6. **Scholarly fable versions (6f30ade5, 497759c9, 9dd5a4d3).** These mix conventions: parentheses for optional segments, unaccented or unmarked forms. 497759c9 has a real agreement error: dat. pl. participle `widn̥tbʰ(y)os` with sg. `moi`, left over from the "us" of Schleicher's horses' speech, plus a malformed `weukʷét`. Including them as-is would teach notation, not language.

## Overall view

The rule-based texts are mostly good. Ablaut and the endings are handled carefully: athematic vs. thematic optatives, 3du -tām/-tes, perfect 2sg -th₂e/2pl -é, nasal-present subjunctive `Hrunépetor`, i/u-stem vocatives, zero-grade imperatives (`h₁ddʰí`, `sddʰí`, `l̥gʰdʰí`, `wr̥h₁dʰí`). The pronoun genders track their referents well: fem. `h₁íh₂m̥` for néh₂us and h₂ówis, masc. `h₁ím` for h₁óytos, neut. `h₁íd` for h₁wédmn̥ and déh₃rom. Gnomic statements use the aorist injunctive (`mért`, `néḱt`, `h₁áyto`), which I accept as gnomic aorist. Nearly all the errors are single-token agreement or case choices, the kind a person/case agreement check would catch.
