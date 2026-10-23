# Tier-3 review: packet t002 (hymns, prayers, charms)

Reviewer stance: a skeptical Indo-Europeanist. This review uses handbook knowledge only (Fortson, Beekes, Ringe, LIV-type conventions from memory). Nothing was looked up online. The packet's forms were checked against `data/lexicon/lexicon.jsonl`, the engine's paradigms (`Lexicon.cells`) and `validate_text`. Validator "pass/exact" only shows that the engine can generate a form, not that the form is correct. Every judgment below rests on comparative evidence.

## Counts (28 items)

| verdict | n | items |
|---|---|---|
| ok | 2 | ca37027c, 3c26deaa |
| minor | 20 | all others |
| wrong | 6 | 34173695, f9e72f42, 8c422850, 9662760c, 250b93cb, 22836f65 |

Three items have genre `fable`, not hymn/prayer/charm. They are scholarly-style reconstructions: bedfca36 is a Byrd-type "King and God" line; f78d41d7 and 13ca3160 are Schleicher-fable titles in pre-laryngeal, Lehmann–Zgusta-type notation. They were judged on notation only and marked minor, not wrong.

## Recurring patterns

**Errors that change the meaning (wrong)**
- **h₁idʰí used for "give"** (f9e72f42, 8c422850, 9662760c). The form is the imperative of *h₁ey- "go" (Ved. ihí, Gk ἴθι), so "h₁idʰí moy gʷṓm" reads "go … cattle". The source is the lexeme `pie-lex-h1ayt` (h₁áyt "to give"). Its notation is suspect: h₁ next to a written a-vowel, while its root id is `h2ey-give`. Any "give" sentence realised through this lexeme will carry the same error. Fix it at the lexicon level, or prefer dh₃dʰí / h₁opéye.
- **Wrong person or case for the subject:**
  - 34173695: bʰéwdʰesi is 2sg, but its subject is nominative h₁n̥gʷnís.
  - 250b93cb: h₂wérstu is a 3sg imperative, but the English is a 2sg request.
  - 22836f65: h₃ósdōd is ablative, but it is meant as the subject ("The branch burns").

**Morphological defects (minor)**
- **Acc. pl. of "cow" is gʷówn̥s for *gʷṓms** (14df450a, 9662760c). Stang's law applies to the plural as well as to the acc. sg. gʷṓm. The engine already lists gʷṓs as an alternative, so it should be preferred.
- **Oblique stem of *dʰéǵʰōm is written ǵʰm-/ǵʰém- for *dʰǵʰm-/dʰǵʰém-** (3e37a92a, 61fd8276, f5f2fa2f: ǵʰémi; e99ca815: ǵʰmés).
- **s-stem "dawn" loses its suffix in the weak cases** (c1d7d425 h₂uséy for *h₂usséy, Ved. uṣáse). The acc. h₂éwsosm̥ has a short o where *h₂éwsōsm̥ is expected (237b84f0, Ved. uṣā́sam).
- **Vocative of *ph₂tḗr is accented ph₂tér, like the nominative** (8e7084ed, 250b93cb, 782abb61, e99ca815). This is inconsistent with the engine's own retraction in dʰúgh₂ter and h₁ń̥gʷni.
- **One-off forms:**
  - h₁ddʰí for *h₁éddʰi (Ved. addhí, Gk ἔσθι) in 4a12ffc8.
  - h₂éryeti missing the root's h₃ (*h₂érh₃yeti) in 107f4ccb.
  - Zero-grade HHḱéwih₂ / n̥ḱéwih₂ in 237b84f0.
- **Vocative lapse:** nominative h₂éwsōs is used with an imperative in 237b84f0. Elsewhere, vocative use is consistently good: dʰúgh₂ter, ń̥bʰre, wĺ̥kʷe, ḱwón, dʰéǵʰom méh₂ter, and voc. pl. h₂ékʷeh₂es / deywṓs.

**Lexical and syntactic defects (minor)**
- **néḱus "dead, corpse" glossed as "mortal"** (14df450a, 237b84f0, c1d7d425, b2ae47ae). The IE topos "gods are not mortal" is built on *mr̥tós / *n̥mr̥tós.
- **lowkós "clearing, open space" (Lat. lūcus, Ved. loká-) used for "light"** (f9e72f42, 237b84f0, eed13123, 2742da4e). The same texts also use léwks / léwkos correctly.
- **Aorist (injunctive) where the English is a present state** (8c422850, 9662760c, eed13123 bʰudʰént/sth₂ént; 4b4cf609, 782abb61 wénHs; e99ca815 wn̥Hént; 107f4ccb wénHt/h₂wékst; 61fd8276 h₂wérst/péh₃s; ce9f0544 méwdt). This is defensible as gnomic or timeless injunctive, but the English does not ask for it.
- **One-off syntax:**
  - Plural instead of dual for Sky and Earth (e99ca815).
  - An English-style dummy "it" with a weather verb: tód h₁regʷesyéti (dc263956).
  - A non-reflexive tósyeh₂s that, combined with a null subject, points to the wrong person (eed13123).
  - Masc. déh₃tōr predicated of Earth (107f4ccb).
- **Not counted against the texts:** mē + optative in negative wishes has Greek support (μὴ γένοιτο). It is a defensible variant of mē + injunctive.

## The texts as hymnic poetry

The best texts are recognisably Indo-European in substance:
- **Invocation with a genealogical epithet:** h₂éwsos diwés dʰúgh₂ter, dyéw ph₂tér, dʰéǵʰom méh₂ter, h₂ékʷeh₂es méh₂teres.
- **Inherited formulas:**
  - ń̥dʰgʷʰitom ḱléwos and méǵh₂ ḱléwos.
  - h₁uséwōm déh₃tōr (cf. Ved. dātā vásūnām, Gk δωτῆρες ἑάων).
  - HéHḱewes h₁éḱwōs.
  - h₁nómn̥ dʰeh₁- "give a name".
  - The dragon-slaying h₁ógʷʰim gʷʰéns with the waters released (782abb61).
- **Rig-Vedic rhetorical questions:** kʷís h₂éwsosm̥ dedórḱe?, kʷís kʷékʷlom sh₂wéns dʰéh₁t?
- **Mythic motifs:** Night as Dawn's sister, the sun following Dawn, Fire born in the waters, and Fire as messenger to the gods.
- **Structure:** the ask-and-give logic (do ut des: h₁yós toy dédeh₃ti, tósmey gʷṓm h₁opéye) is correct, and the charms use ring composition (34173695, 3c26deaa).

The weaknesses are those of a sentence generator rather than a poet:
- **Monotony:** nu or nu-kʷe opens most clauses, and the prose is flat SOV.
- **No real parallelism** beyond literal repetition, no metre, and few epithets per deity (mostly one per text).
- **Abrupt person shifts** from 2nd to 3rd and back (4b4cf609, 107f4ccb).
- **Little variation in the requests.** Nearly every hymn ends with "give us strength / increase / fame, remember us".

As training material, the hymns supply sound formula-level diction. The errors listed above should be fixed before they recur at scale, especially h₁idʰí and the acc. pl. gʷówn̥s.
