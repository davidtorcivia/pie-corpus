# Tier-3 review: packet t005 (hymns and prayers)

28 items reviewed. Verdicts are in `docs/audits/packets/t005-verdicts.jsonl`.
I worked from handbook knowledge only, with no browsing. The project lexicon, the inflection specs, closed_class.json and the engine's cell tables were consulted to identify which lexeme and cell each word comes from.

## Counts

| verdict | n |
|---|---|
| ok | 5 (8e7508b4, 32c8f6cf, e0e08ba6, da4d22ba, 805bda5b) |
| minor | 18 |
| wrong | 5 (93dcdf33, 20b91eb5, 98665807, 91651f82, d70eb263) |

## Wrong

- **Person/number agreement with the addressee.** In d70eb263, `túH ... lowkéyonti` has 3pl beside an explicit 2sg subject. In 93dcdf33, `woséyeti` is 3sg inside a 2sg address, where the English has "You clothe". The engine seems to lose the 2sg subject in some clauses.
- **Wrong case or number on a subject noun.** In 91651f82, `deywṓm` (gen. pl.) is the subject of ǵeǵn̥h₁ḗr. In 98665807, `deywóh₁` (dual) is used for "the gods" with a 3pl verb.
- **20b91eb5 (Byrd-style Schleicher fable):** `wewkond` lacks the labiovelar. It should be wéwkʷond.

## Recurring minor patterns

- **Vocative ph₂tér keeps the suffix accent** in b300410a, fda067a9, 7df9479d, 3cdd92a1 and 827f70b5. Vocatives are initial-accented (Ved. pítar, Gk páter). The engine gets this right for dʰúgh₂ter, méh₂ter, gʷʰéntor and déh₃tor; it fails only where the root vowel is a laryngeal.
- **Zero grade in oblique plurals:**
  - i-stem loc. pl. `uh₁itéysu` should be *-isu (0c3dcdb5, 7fb504b1).
  - men-stem loc. pl. `h₁iménsu` should be *-mn̥su (df072a1b).
  - `m̥rént` should be *mr-ént (ec527ee9).
  - `ǵʰémi` loses the dʰ of *dʰǵʰ- (3d279278).
- **Agreement:** 3d279278 has an adjective that does not agree with its noun (h₂éwsterōy beside wédn̥bʰos). 8e30c9e4 has a 1sg verb with the conjoined subject "I and my brother".
- **Gender of h₁ógʷʰis.** The lexicon has it as feminine, which yields fem. sérpontih₂ (fda067a9) and tā́m (4f49a13c). Ved. áhi-, Av. aži- and Gk óphis are masculine.
- **Lexeme senses that are doubtful though the lexicon licenses them:**
  - Hn̥dʰí 'under' (ec527ee9, 55732414, 3d279278). Its Sanskrit cognate ádhi means 'over, on'; *n̥dʰér is the secure 'under'.
  - supnós for "death" (827f70b5).
  - ǵʰlíeti 'shine' (9f1a1703), which is also ill-formed.
  - linékʷti used intransitively for 'depart' (47e26f8e).
  - énu with a locative (4bf98409); it should take the accusative.
- **Not downgraded but worth noting:**
  - péḱos is glossed "wealth" throughout. It means 'livestock/fleece' (Lat. pecus, Gk pékos); *péḱu would be the 'wealth' word.
  - h₂én is used for "there". It is a thin reconstruction resting on particles.
  - h₂m̥bʰí is used for "in exchange". The lexicon licenses it, but *h₂énti is the classic word.
  - 1sg pronoun spellings are inconsistent: h₁mé (acc.) beside méd (abl.).
- **The two Schleicher-fable items** (2ea20aa8, 06feafca) are in pre-laryngeal notation. 06feafca keeps the editor's alternatives "(y)" and "(eḱwomos)" in the running text. They should be normalised or dropped.

## The hymns as poetry

As Indo-European hymnody the synthetic hymns are strong.

- **Opening invocations** use well-attested epithet chains: dyéw ph₂ter, h₂éwsos diwés dʰúgh₂ter, dʰéǵʰom méh₂ter, h₁wŕ̥Hewih₂.
- **Inherited formulas:**
  - ḱléwos ń̥dʰgʷʰitom
  - ḱlutóm h₁nómn̥ (and h₁nómn̥ dʰeh₁-)
  - méǵh₂ ḱléwos
  - h₁uséwōm déh₃tores (= Ved. dātā́ro vásūnām, Gk dōtēres eáōn)
  - h₁wérHum lowkóm (= Ved. urúṃ lokám)
  - HéHḱuns h₁éḱwons
  - gʷʰént h₁ógʷʰim, the dragon-slaying formula
- **Myths** are the expected Vedic ones:
  - Dawn freeing the hidden cows
  - Agni born of the waters, hiding in plants, sought and seated by the gods
  - the Waters carrying away the worshipper's stain (cf. RV 1.23.22)
  - the navel of the earth
  - the Sun's unbreakable wheel
  - a dialogue with the rivers (df072a1b, cf. RV 3.33)
- **Structure** follows the expected sequence: vocative, then praise by relative clause (h₁yós ... bʰéydt, twé h₁érkʷomes), mythic narrative, then requests in imperative and optative, with mē + injunctive for prohibitions. Several end with a do-ut-des vow, as in 4f49a13c and da4d22ba.
- **Anaphora** works well, for example túH ... túH ... túH and the triple h₂réwesi.

The weaknesses are a rather mechanical clause-per-sentence rhythm, few relative clauses outside the openings, and little use of particles or preverb tmesis beyond h₂epó and úd. The hymns sound like good student Vedic in PIE dress more than like an inherited poetic syntax.
