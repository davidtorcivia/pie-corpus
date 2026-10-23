# Tier-3 review: packet t007 (wisdom, riddles, fables)

This review uses handbook knowledge only (Fortson, Ringe, Beekes, Meier-Brügger, LIV² conventions as I remember them). I did no browsing. I used the project lexicon and engine `cells()` to check specific paradigms.

## Counts (28 items)

- **ok**: 16
- **minor**: 6 (92f1be03, c81edb04, 457fab75, b0f274bc, dee0b7dd, c0bac242)
- **wrong**: 6 (9f4330a0, 5a9552b6, 18c70d7c, cab1dc19, ebd88eae, 3bc3edb1)

## Recurring patterns

1. **Wrong paradigm cell chosen (person/number/case).** These are the most serious errors. The form exists in the paradigm, but it is the wrong cell:
   - cab1dc19 `sn̥h₂wé`: PST.1DU used for a 3pl subject.
   - ebd88eae `h₂élete`: 2pl used for a 3sg subject.
   - 3bc3edb1 `ḱlutṓys`: INS.PL used as a nominative predicate.
   - 9f4330a0 `bʰréh₂teres mért`: 3sg verb with a plural subject. `pie-lex-mert` has no paradigm, so the lemma is emitted as is.

   This looks like a slot-selection bug, not a morphology bug. A validator check of subject/verb person and number, and of predicate case, would catch all four.
2. **Pronoun gender does not follow the antecedent.** Fem. `téh₂es`/`tā́s` resumes masc. `moysṓs` in 92f1be03 and dee0b7dd. The engine seems to resolve the pronoun's gender from the concept 'sheep' (fem. h₂ówis), not from the noun actually used.
3. **Lexeme confusion: h₂éwis 'bird' vs h₂ówis 'sheep'** (18c70d7c).
4. **Paradigm defects in the engine:**
   - `dʰéǵʰōm` ACC.SG = NOM.SG (c0bac242).
   - Root-noun obliques of `dʰǵʰúHs` with a spurious -o- (`dʰǵʰúHobʰos`, GEN.PL `dʰǵʰúHoōm`).
   - u-stem adjective feminine `h₁uséwih₂` (b0f274bc).
5. **Clitic -kʷe misplaced** on the first conjunct (c81edb04, 18c70d7c).
6. **Scholarly texts in mixed notations.** The Sheep-and-Horses material mixes three systems: a modern laryngealist title (027b44a6), Schleicher 1868 (5a9552b6, a-vocalism, impossible as modern PIE), and Lehmann-Zgusta 1979 (457fab75, no laryngeals). If these stay in the corpus, they should be tagged as historical so a model does not learn their phonology as PIE.

## Acceptable conventions (not penalized)

- Gnomic statements often use secondary/aorist forms: `néḱt`, `léytt`, `h₂wékst`, `h₁épt`, `mért`. These can be defended as gnomic injunctives.
- Vocatives `súHnu` and `gʰóstipoti`: handbooks more often give *-ew/*-ey, but Greek supports these.
- `wéwket` (boukólos delabialization).
- `h₂éryeti` (Pinault's rule).
- Athematic `trémti`, as in LIV.
- Acrostatic `wédni`.

## The texts as literature

The fables are Aesopic in shape: a narrative, a short dialogue, then a one-line epimythium in the gnomic present. Several work well:

- Dog and Wolf, freedom vs. a full belly (3a6bee41).
- The wolf at the spring, "seeks a sheep and finds a word" (c9430bce).
- The sheep who trusted the she-wolf (dee0b7dd).
- The two rams and the snow (35bb686a).

The cast and vocabulary are small and keep recurring (wolf/she-wolf, dog, sheep, bird, fish, master, guest). The many verbs of speaking (wérh₁t, sékʷt, h₂éǵt, mléwHt, wéwket, bʰéh₂t) are a real strength.

The wisdom items draw well on genuine IE themes:
- guest-friendship (gʰóstis/gʰóstipotis, the guest as the gods');
- inherited formulae: *ḱléwos ń̥dʰgʷʰitom and *déh₃tōr h₁wesuHom (rendered h₁uséwōm).

The maxims are paratactic lists, though, with little parallelism or sound play. Some lines are flat ("Cook for the guest"). The riddles all follow one template (kʷíd h₁ésti h₁yód … ? h₁ésti tód X). They are grammatical but too transparent to work as riddles.
