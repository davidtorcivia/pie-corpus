# Tier-3 review: packet t004 (myth, epic, fable; 28 items)

Reviewer basis: handbook knowledge only (Fortson, Ringe, Beekes, LIV-style conventions). I did no browsing. I checked suspect forms against the project lexicon, the engine's `Lexicon.cells()` and `validate_text`. Per-item verdicts are in `docs/audits/packets/t004-verdicts.jsonl`.

## Counts

| verdict | n |
|---|---|
| ok | 13 |
| minor | 10 |
| wrong | 5 |

## Wrong items: a paradigm cell with the wrong person or number

All five come from one failure: the engine picks a form from the right paradigm but the wrong cell. The validator does not catch this; it flagged only one of them (3d7cc017) as an agreement warning.

- **3d7cc017**: `mórtōs mr̥wé` has the 1du aorist for 3pl "mortals die".
- **0b742656**: `gʷm̥sḱétes` is 3du present for "he is coming".
- **de1d95a8**: `h₁r̥té` is 2pl aorist/imperative for 3sg "he arrived".
- **57e9387b**: `só ... h₁sdʰí` is a 2sg imperative with a 3sg subject; it needs `h₁éstu`.
- **aa0b95c2**: `h₁élh₂t` is 3sg after a plural subject (the warriors); it needs `h₁l̥h₂ént`.

Recommendation: add a check that the verb's person and number match the subject, and that a 3rd-person subject never gets a 2nd-person imperative. The surface validator cannot see this.

## Recurring minor defects

- **Engine paradigm tables**:
  - The king's strong stem has a short vowel: `h₃réǵm̥`, `h₃réǵ`, `h₃réǵes` instead of `*h₃rḗǵ-` (2bb8057a).
  - The vocative of the devī-type equals the nominative: `pótnih₂` should be `*pótni` (6bb11969).
  - The accusative of the devī-type is `-ih₂m̥` instead of `*-ih₂m` (aa0b95c2).
  - The vocative of `ph₂tḗr` keeps final accent: `ph₂tér` instead of initial-accented `*ph₂ter` (efe135f8).
  - The neuter `ḱḗr` has accusative `ḱérd`, distinct from the nominative `ḱḗr` (2221af89, 90204495, 0609e1da). I did not downgrade for this.
- **Agreement and case**:
  - A feminine adjective modifies a masculine noun: `méǵh₂ih₂ h₁ógʷʰis` (bba6075d).
  - A dative is used for a locative: `wédney` "in the water" (1778762b).
- **Lexeme sense**: `gʷh₂tós` ("gone") is used as "Death" (9235770d), while the rest of the corpus uses `mértis`.
- **Reflexive possession**: anaphoric `tósyo` / `tósyeh₂s` is used systematically for a possessor who is the subject, where `*swo-` is expected. Examples: 6bb11969, bba6075d, 0bfdd3fb, a64324d9, 2221af89, fed07698. I treated this as an engine-wide style gap and downgraded only where the English says "own" (6bb11969).
- **Scholarly items** (e36ee459, d312cf25, 0d5eaf20) are correct for their sources. The first two use pre-laryngeal Lehmann–Zgusta notation, and d312cf25 also has the augment (`ebʰuget`); the third has Byrd-style `h₃rḗḱs súHnum`. All three are inconsistent with corpus orthography.
- **Lexicon-level caveats** (I did not downgrade for these):
  - The handbook form of "death" is `*mr̥tís`. The full-grade `mértis` is defensible only as a proterokinetic nominative.
  - `wéwket` without the labiovelar goes against Gk eîpe; `*wéwkʷet` is expected.
  - `déh₂nu` is coded as neuter, but Av. dānu- "river" is feminine.
  - `gʷʰr̥nḗm` (Stang's law applied to `*-néwm`) is bold but defensible.

## Strengths

The handbook-correct details are numerous:
- imperatives `gʷʰn̥dʰí`, `ḱludʰí`, `ph₂sdʰí`, and `h₁sdʰí` (correctly 2sg in 0bfdd3fb)
- 2du `ḱlutóm` for paired addressees
- prohibitive `mē` with the injunctive
- perfects `wóydh₂e`, `dedórḱe`, `dedwóye`, `bʰebʰóydʰe`, `lelóykʷth₂e`
- `píph₃onti`, `linékʷti`, `dédh₃n̥t`
- the vṛkī́-type nominative `wl̥kʷíh₂s`
- the subjunctive used as a future, and the optative `-oyh₁-`

The formulas are well chosen:
- `gʷʰént h₁ógʷʰim`
- `ḱléwos ń̥dʰgʷʰitom`
- `h₁uséwōm déh₃tōr` (dātā vasūnām)
- `diwés dʰúgh₂ter`
- `dyéw ph₂ter`
- the four-eyed dogs at the river (de1d95a8)

## Narrative prose

The stories hold together: each has a clear arc, a closing fame or name formula, and good use of the dual for pairs (the twins, the horses, Sky and Earth). The problems:

- **Unmarked speaker changes in dialogue.** Replies start with no speech verb, so a following `nu só mléwHt` can point to the wrong speaker (45315ed3, and to a lesser degree 2221af89 and a64324d9).
- **Repetitive clause links.** Narration leans almost entirely on `nu` plus `-kʷe`, which makes the prose feel mechanical.
- **Tense mixing.** Aorist or injunctive forms appear in present-tense or gnomic passages (fed07698 `bʰudʰént`/`litént`, 57e9387b `gʷémt`). I accepted these as Vedic-style timeless injunctives and gnomic aorists.
- **Participles** (`gʷm̥sḱóntm̥`, `sédyontn̥s`, `légʰyontm̥`, `h₂éǵontih₂`) are used correctly and idiomatically.
