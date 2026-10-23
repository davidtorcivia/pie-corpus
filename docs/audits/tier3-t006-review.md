# Tier-3 review, packet t006 (28 items)

The reviewer worked from handbook knowledge only (Fortson, Ringe, Beekes, Sihler, LIV-type material) and did no browsing. Engine paradigms were spot-checked with `Lexicon.cells`, and lexicon entries were looked up in `data/lexicon/lexicon.jsonl` and `data/morph/closed_class.json`. Per-item verdicts are in `docs/audits/packets/t006-verdicts.jsonl`.

## Counts

| verdict | n |
|---|---|
| ok | 11 |
| minor | 11 |
| wrong | 6 |

## Errors ("wrong")

Every one is an agreement or case slip on a single word. Forms are well built, but the wrong paradigm cell was picked.

- **Wrong case on a noun**
  - d3ffb5e7: gen. bʰréh₂tr̥s for the addressee; needs dat. bʰréh₂trey.
  - b72b2429: gen. Hrugʰéys as the subject; needs nom. Hrugʰís.
- **Wrong verb number or person**
  - b201e915: 2pl dh₃té addressed to one god.
  - 5f799de7: 3du h₁stā́m with plural gʷówes.
  - 4d0acaeb: 3sg stunédtu with animate plural h₂ékʷeh₂es. The neuter-plural singular-verb rule was applied to a non-neuter noun.
  - b91a94ec: bʰindth₂é is 2sg middle, used for 'it split'; needs 3sg bʰindtó.

## Recurring "minor" patterns

- **Bare-stem vocatives of i- and u-stems** (444e4906 súHnu, 801d9456 h₁ń̥gʷni). Ved. sūno, ágne and Lith. sūnaũ support *-ew/*-ey. The engine lists the bare stem first; the full-grade-suffix form should come first.
- **Dual endings** (ff41eafd). The engine's 2du primary -tes is the same as the 3du; the handbook 2du is *-th₁es. Consonant-stem nom./voc. du. comes out as -h₁, where *-eh₁ is better (Ved. dātārā).
- **Tense, aspect or voice of stem choice**
  - ff41eafd: root aorist dm̥h₂tóm is used for present 'you who tame'.
  - 3ae9c2d1: past h₂wérst sits in a present gnomic hymn, and active pékʷonti 'cook' is used for intransitive 'ripen' (needs a middle).
  - e563baa6: transitive pléh₁t is used for 'the streams filled'; the corpus's own pléh₁dʰet would fit.
  - d3ffb5e7 and 5104d86d: active mért 'died' is doubtful for a verb that is largely middle (*mr̥tó, Ved. amṛta, Lat. morior). Not graded down.
- **Lexicon-form defects showing through**
  - 9fc22b26: h₂éryeti lacks the h₃ of *h₂erh₃-.
  - 7ad2bee0: loc. ǵʰémi lacks dʰ (*dʰǵʰém(i)).
  - 6a6ec4a6: yémHos has the wrong accent (lexicon yemHós).
- **Scholarly fable lines in older notation** (5b59111e, 3447e1fe, a30bc8bc). These lines lack laryngeals or accents and use augments, -bʰyos, mixed ḱw/kʷ spellings and final -d, all inconsistent with the corpus. The grammar is sound: a30bc8bc's accusative of the addressee follows Byrd's version.

## Lesser observations (not graded down)

- h₁opéyeti 'give' (cc4c6ccb, 6a6ec4a6, c6af5a12, ff41eafd, 61e7fc63, cca680b6). The core sense is 'cause to reach' (Ved. āpayati), so 'give' is a stretch, but it comes from the lexicon.
- The u-stem give-verb déh₃ut / duh₃- (Lat. duim, Cypr. δοϝεναι) is a minority reconstruction, but it is used consistently.
- Possible lexicon issue, not checked further: Hrugʰís (nom.) and Hréwgʰim (acc.) mix ablaut models.
- péruni (5f799de7, a Hittite-type locative; the engine has pr̥wéni) and wr̥sménsu (40d6058b, full-grade suffix in the loc. pl.) are defensible variants.
- Engine dat. h₂uséy ('to Dawn') follows a Schindler-type weak stem *h₂us-s-. Defensible.
- *h₂ew is glossed 'back, again'. Greek αὖ makes this tolerable.

## The texts as Indo-European myth

The thematic content is good and often pointedly traditional.

- **Storm god and serpent**
  - h₁ógʷʰim gʷʰen- and h₁ógʷʰim Hwért, the obstructing serpent (cf. Vṛtra) (b72b2429, 5c9ae480, 5f799de7, b201e915, d3ffb5e7).
  - Stone weapon, waters released, cattle freed from the rock in the Vala manner (5f799de7, b201e915).
  - The god defeated first and then helped, as in Illuyanka (5104d86d).
- **Formulae**: *ḱléwos ń̥dʰgʷʰitom, *h₁wésu ḱléwos, *h₁nómn̥ dʰeh₁-, *diwós suHnú, *sh₂wéns kʷékʷlos, *dyew ph₂ter.
- **Divine twins**
  - The Sun's daughter is rescued from the sea and then married off on a silver car, as with the Aśvins and Sūryā (RV 10.85) and the Latvian Saules meita (2e2200c4, cca680b6, 6a6ec4a6).
  - The twins are addressed as horse-drivers and rescuers (ff41eafd).
- **Cosmogony**
  - Sky and Earth propped apart (7ad2bee0, 1b8c408a). 1b8c408a's "to which god shall we give" echoes RV 10.121 kásmai devā́ya.
  - Sun follows Dawn, and cosmic order (3ae9c2d1).
- **Other myths**: Agni hiding in the waters and saying "I am afraid" (dedwóyh₂e), close to RV 10.51 (801d9456). Theft of fire (b91a94ec, b86d64c4) is more folktale than reconstructable IE myth, but it is harmless.

Overall: idiomatic, formula-rich and morphologically careful. The residual errors are concentrated in agreement and cell selection, so they could be caught mechanically. Worth adding to validate_text:
- addressee case after verbs of speaking;
- dative arguments;
- subject case;
- 2nd-person number against vocative number;
- the neuter-plural rule restricted to neuters;
- finite person against the overt subject.
