# Tier-3 review: packet t021 (28 items)

The reviewer worked from handbook knowledge only, with no browsing: Fortson, Beekes, Ringe, LIV², and Mallory & Adams as remembered. Doubtful forms were checked against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json` and `Lexicon.cells()`. Verdicts are in `docs/audits/packets/t021-verdicts.jsonl`.

The two grades are calibrated as follows:
- **wrong**: the error is ungrammatical or changes the meaning (agreement, case, person or number, or a malformed key verb).
- **minor**: the problem is ablaut, accent, notation, or a stretched sense.

## Counts

| ok | minor | wrong |
|----|-------|-------|
| 11 | 11    | 6     |

## Wrong (6)

- **Verb person or number does not match the subject:**
  - de740044: `só … h₁uként` is a 3pl verb with a singular subject; it should be h₁éwkt.
  - 0cd9c78f: `h₁n̥gʷnís h₁stés` uses the 3du for a single 'Fire'; it should be h₁ésti.
  - 8359eeb5: `ménos … h₂éǵe` uses the 2sg imperative for 'let the mind drive'; it should be h₂éǵetu.
- **Wrong case:**
  - aeb10aff: `dʰrówgʰoh₁ h₁ésti` puts the instrumental (or dual) where the nominative is needed; the answer that follows has the correct dʰrówgʰos.
  - 799f3b32: `ḱóymōys gʷmént` uses the instrumental plural for 'to the household'.
- **2dba1939** is a hybrid of the Hirt and Lehmann–Zgusta versions of Schleicher's fable:
  - `eweket` loses both the labiovelar and the reduplication of *wekʷ-.
  - It also has `ḱerd` as a nominative, a thematic `angʰetai`, and `ǵʰm̥onm̥`.

The first three wrong items look like errors in the engine's agreement or cell selection rather than in the lexicon. In de740044 and aeb10aff the correct form appears in the very next sentence.

## Recurring minor patterns

- **Lexicon accent errors:**
  - h₂ŕ̥ǵn̥tom (28ff4386, c015c938) should be *h₂r̥ǵn̥tóm (Ved. rajatám).
  - HéHḱus (59162af4, eb1825cc, and also e4eb7dd2) should be oxytone *HeHḱús (Ved. āśú-, Gk ὠκύς).
- **Paradigm cells off the handbook norm:**
  - h₃réǵm̥ has a short root vowel against the lengthened grade of Lat. rēgem (b9b3080a).
  - The eh₂-stem vocative equals the nominative, léwbʰeh₂ (591549a9); the handbook ending is *-h₂/*-a.
  - The ablative kʷósmead should be *-ōd (e4eb7dd2).
  - The instrumental péḱewh₁ (23bcf344) has full grade in both root and suffix.
  - The 1sg aorist ḱlḗm extends Stang's law to a verb (eb1825cc).
- **Senses:**
  - Hn̥dʰí is used for 'below', but Ved. ádhi means 'on, over' (823894ee).
  - sēmi is used as a free word for 'half (of them)' (7ad62b2a).
- **Notation:** the fable lines are in old notation with no laryngeals or accents (66d051e0, 2dba1939), while their title cae7baa2 uses modern notation.

## Accepted conventions (not penalised)

- Many verbs, such as mért, néḱt, gʷéh₂t, yéwgt and h₂wéyst, appear as unaugmented root-aorist injunctives standing in for an English present. A gnomic injunctive is defensible.
- Active perfects are used intransitively:
  - ǵeǵónh₁e 'is born', backed by Gk γέγονε.
  - lelóykʷe / lelikʷḗr 'is gone' (5962f573, 823894ee, 075fad50, e13e8fbf, b3c6d613). This one is a stretch from 'has left', but it is consistent.
- méǵh₂ is used as a bare-stem vocative.
- Pronominal datives and ablatives take the m-ending, as in h₁éymos.

## Assessment

The texts are strong overall. They draw well on the inherited poetic formulas:
- gʷʰént h₁ógʷʰim 'slew the serpent'
- déh₃tores h₁uséwōm 'givers of good things'
- dyéw ph₂ter 'Father Sky'
- h₃rḗǵs wiHrṓm poh₂imḗn 'the king, shepherd of men'
- h₁nómn̥ dʰeh₁- 'set a name'
- the two dogs guarding the crossing
- the twin sons of Sky

The duals (bʰéwdʰetes, dwóyh₁ swésorh₁ h₁stés, h₂léksoyh₁tām) and -kʷe placement are handled well. So are the subjunctives in conditional clauses and the mē + injunctive prohibitions.

The six wrong items are all local slips that can be fixed by choosing a different cell. There are no systemic misreadings of meaning.
