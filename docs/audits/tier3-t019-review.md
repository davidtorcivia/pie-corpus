# Tier-3 review, packet t019 (dialogues among the gods)

Reviewer: skeptical Indo-Europeanist pass, from handbook knowledge only (Fortson, Ringe, LIV-type conventions as I know them). I did no browsing. I used the lexicon, closed-class tables, engine cells and validator only to identify which lexeme and cell each form is.

Verdicts are in `docs/audits/packets/t019-verdicts.jsonl`.

## Counts

| verdict | n |
|---|---|
| ok | 15 |
| minor | 8 |
| wrong | 5 |
| total | 28 |

## Wrong: a cell from the wrong slot of a correct paradigm

All five errors are the same kind. The form is well built, but it is the wrong case or person for the sentence. The validator passes all of them because each is a real cell.

- **Case of a noun** (3 items):
  - 4788e042: `wóǵʰōs` nom. pl. for 'on the wagon'.
  - a0e0c016: `gʷéwi` loc. sg. for 'drive the cattle', which needs acc. pl. `gʷṓs`.
  - 5d4a6c9b: `déh₃noybʰos` dat./abl. pl. as the object of 'give a gift'.
- **Number on the subject** (1 item): 9b92cd29, `deywóh₁` nom. du. with 3sg `h₁ért` for 'a god came'.
- **Person/number on the verb** (1 item): bc747571, `h₂élēth₁es` 2du subjunctive for 'if I do not nourish'. The same item also has `mē` in a conditional, and 2pl `dédh₃te` addressed to two gods.

## Minor

- **Pre-laryngeal scholarly fragments** of Schleicher's fable in Lehmann–Zgusta-style notation (584f96e4, 1fd6dcd1, 71b1605c). They are correct as reconstructions, but they have no laryngeals and no accents. 584f96e4 also writes `kʷe` as a separate word. Either normalize them or label them as legacy notation.
- **s-stem neuter plural `nébʰōs`** (1f3a1a62, 6aef3550). The engine gives the disputed collective in *-ōs* where the handbooks give *-es-h₂*. This is systematic, so it is worth fixing in the paradigm rather than per text.
- **Gender of a personified neuter** (6aef3550). The Sun (`sóh₂wl̥`, neuter, referred to with `h₁íd`) takes masc. `méǵh₂s`.
- **Clitic placement or stacking**:
  - 805d4d38: `gʷṓs te toy-kʷe` splits the conjuncts.
  - dfc9f263: `moy moy`.
- **Stem inconsistency** (e9452bc4): `légʰyonti` and `légʰete` in one sentence.

## Checked and accepted

- **`h₂uséy`**: dat. of an amphikinetic s-stem with weak stem *h₂us-s-*.
- **`ḱlḗm`**: Stang's law, parallel to *dyēm*.
- **Middle 2sg `-th₂er`**: the r-ending convention.
- **`h₁égʷʰis`**: acrostatic gen.
- **`h₂éHsh₂m̥`**: h₂-stem acc.

## Doubtful lexeme

`gʷh₂tós` 'death' (675e911d, 5d4a6c9b, 1e093793) comes from Wiktionary, and I cannot confirm that sense; *mr̥tís* would be safer. I did not count it as an error.

## Overall view

The texts are good. They are idiomatic and full of formulas used correctly:

- *ḱléwos ń̥dʰgʷʰitom*
- *méǵh₂ ḱléwos*
- *déh₃tōr h₁uséwōm*
- *h₁suḱléwēs*
- the *Hwer-* serpent who holds back the waters

Ablaut in the root aorists and the nu-present, *-yé-* present and imperative stems (*ḱludʰí*, *gʷʰr̥nudʰí*, *ḱl̥nuté*) is consistently right. The remaining risk is in choosing which cell to use, not in building the forms. A check that the case or number fits the verb's valence would catch every "wrong" item in this packet.
