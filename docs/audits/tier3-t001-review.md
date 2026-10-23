# Tier-3 review, packet t001 (28 items)

Reviewer basis: handbook knowledge only (Fortson, Ringe, LIV-type conventions), with no browsing. I checked suspicious forms against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json`, and the engine's `Lexicon.cells()`, and ran `validate_text` on every item. Per-item verdicts are in `docs/audits/packets/t001-verdicts.jsonl`.

## Counts

| verdict | n |
|---|---|
| ok | 7 |
| minor | 16 |
| wrong | 5 |

## Wrong: picking the wrong cell of a paradigm

All five errors are well-formed forms taken from the wrong row of a correct paradigm. In each case the person or number is wrong, and four of the five fall in the dual or in an unexpected person:

- **a48f7532** `sth₂tóm`: 2du imperative addressed to plural horses (2pl `sth₂té` needed).
- **3f245a0a** `h₁opéyetom`: 2du imperfect where 3pl "they gave" is needed (`h₁opéyont`).
- **d30819a5** `ḱéywosdʰh₂`: middle 1du "we two lie" for "I lie" (`ḱéyh₂er`).
- **1e3f53ea** `h₁édm̥`: 1sg imperfect with the subject `táwros` (3sg `h₁édt`).
- **c3e172fa** `ḱléwesbʰis`: instrumental plural where nom. sg. `ḱléwos` is needed.

The validator passes every one of these, because each form exists in the paradigm. Catching them needs a check that the verb's person and number match the subject or addressee, and that the case matches the slot. The dual cells (`-tom`, `-wosdʰh₂`) look especially likely to be picked by mistake.

## Recurring minor patterns

- **Nonstandard closed-class forms.** `closed_class.json` lists these before the handbook forms:
  - abl. `tósmead` instead of `tósmōd`, in a48f7532, d30819a5, ab847a9f, 07e4c4a8, 2b9df11c and 1b744836;
  - instr. `tónoh₁` instead of `tóh₁`, in ab847a9f and eee6b9c5;
  - fem. loc. `tósyeh₂i`, in fc08766c.

  Reordering the list would clear most of the minor verdicts.
- **No dual where the referent is a natural pair.** This affects the hands in 42e50809, Man and Twin in fc08766c, and the divine Twins in 0a920b4d. The engine does produce dual forms, but in the wrong places (see above).
- **Neuter plural subject with a plural verb.** See be629217 (`wódr̥h₂ … h₁sént`) and 1e3f53ea (`péth₂r̥h₂ … h₁sénti`).
- **Masculine `déh₃tor` addressed to a female divinity.** This happens with Dawn in 2b9df11c and with the river goddess in be629217. The feminine `*déh₃trih₂` is expected.
- **Athematic stems where the cognates are thematic.** These are `déwkti`/`duként` for `*dewk-` (c0be2579, d98a6f3c, ab847a9f, a48f7532) and `trémt` for `*trem-` (42e50809, 99834cf2). They come from the lexicon's source, not from the engine.
- **Ambiguous accusative of goal.** In ab847a9f, `tóns wiHróns h₂éǵet` reads first as "drove those men". I graded it minor because the context resolves it.
- **Lexical points.** These are `némos` for "the sacrifice" (6f6ea7c3), and the marginal words `márkos` (be629217) and `sprongʰós` (1e3f53ea).
- **Scholarly items.** 8a51a3f9, f13aa0b8 and 90859669 are correct in meaning. Their notation predates laryngeals and has no accents. One of them leaves a parenthesized alternative in the running text, and f13aa0b8 writes `ōku` for `*h₁ṓḱu`.

The following points I noted but did not count against any item:

- the vocative `ph₂tér` (initial accent expected; c6882869, 42e50809);
- `gʷówn̥s` (this follows the stated acc. pl. -ns convention);
- `wéwket` (consistent with the boukólos rule).

## The texts as prose

**Morphology and formulas.** Outside the five slips, the morphology is impressively consistent. Ablaut is right in root aorists (`gʷémt`/`gʷmént`, `h₁élh₂t`/`h₁l̥h₂ént`), in nasal presents (`yunégt`/`yungént`, `tl̥néh₂t`/`tl̥nh₂ént`), and in perfects (`dedórḱe`/`dedr̥ḱḗr`, `bʰebʰóyh₂h₂e`/`bʰebʰih₂mé`). Subjunctive and optative are used idiomatically: future and conditional (`h₁yód … wéǵʰēsi … noḱéyōh₂`), wish (`h₂léksoyh₁t`), and prohibitive `mē` with the injunctive (`mē l̥gʰté`, `mē linékʷs`). The inherited formulas are well chosen and placed:

- `ḱléwos ń̥dʰgʷʰitom`
- `h₁wésu ḱléwos`
- `h₁uséwōm déh₃tor`
- `diwés dʰugh₂tḗr`
- `gʷʰént … h₁ógʷʰim`
- `dyḗws ph₂tḗr`
- `wédnōm népōts`

Several touches are good. Wackernagel clitics (`skʷále te tóy moréyōnti`, `h₂óweyes wos ḱwónes`) are placed correctly. The preposed relative with its head noun inside the clause (`h₁yóm ḱwónm̥ kʷéḱt só néḱt`) is idiomatic, as are the `h₁yós … só` correlative morals that close the fables.

**Reference and style.** The weakness is the plain, run-on style built from `só`/`séh₂`/`tóy` and `-kʷe`. All third-person reference runs through `só` and `tóm`. When two masculine participants are present (horse and man, wolf and dog, king and stranger), the reader has to rely on the English to know who does what. Some examples:

- c0be2579: `só tóm wéǵʰet só-kʷe tóm gʷréwh₁ kélh₂t`.
- 42e50809 introduces `séh₂` with no feminine antecedent close by.

The engine never uses a reflexive possessive. `tósyo` serves for "his own" as well as "his (another's)", which causes a real ambiguity in 07e4c4a8. `nu` is used for nearly every new sentence.

**Participles.** These are rare but correct where used: `spéḱyontes`, `sth₂éh₁yontih₂`, `ḱléwsontih₂`, `bʰéronts`, `tr̥syónts`. More participles and subordinate clauses would make the prose less monotonous.

**Coherence.** Each story holds together, and most have a recognizable mythological source: the serpent-slaying, Dawn's cattle, the Manu/Yemo creation, Apām Napāt, and the choice of Achilles. They read as competent, formulaic, deliberately plain narrative.
