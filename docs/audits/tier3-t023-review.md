# Tier-3 review: packet t023 (28 items)

The packet covers healing charms, laments and wisdom sayings, plus three fable lines. The reviewer worked from handbook knowledge only, with no browsing: Fortson, Beekes, Ringe, LIV², and Mallory & Adams as remembered. Doubtful forms were checked against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json`, `Lexicon.cells()` and `Lexicon.participle_cells()`, using a reverse index of every token to its cell. `raw/books/text/` is not present in this checkout, so the handbook texts could not be grepped. The three fable items were compared, as facts only, with the Tier 1 source wikitexts in `raw/tier1-wikipedia-*`. Verdicts are in `docs/audits/packets/t023-verdicts.jsonl`.

The grades follow the t021 calibration:
- **wrong**: the error is ungrammatical or changes the meaning (agreement, case, person or number, a malformed key verb, or PIE and English that do not say the same thing).
- **minor**: the problem is ablaut, accent, notation, or a stretched sense.

## Counts

| ok | minor | wrong |
|----|-------|-------|
| 14 | 7     | 7     |

## Wrong (7)

- **Verb person or number does not match the subject or addressee:**
  - 941eee8d: `dh₃éntu h₁ésmey téwe bʰoh₂góm` uses the 3pl imperative 'let them give' for the 2sg 'Give him your portion'; it should be dh₃dʰí.
  - caa45dce: `kʷŕ̥mey … píph₃esi n̥ḱéntu` uses the 3pl imperative for 'Worm, … vanish!'; it should be n̥ḱdʰí, parallel to mr̥dʰí in the line before.
  - 2fb3418e: `ḱwṓ toy sédyetes HréwdHti-kʷe` uses the 2/3du for a single dog; it should be sédyeti. The verb coordinated with it is already 3sg.
  - 66dc51f8: `yugóy stesth₂é` uses the 2pl perfect for 'you two stand'. The rest of the lament addresses the two horses in the dual. The engine builds no PRF.2DU/3DU cell, so this is an engine gap. The present sth₂éh₁yetes is available.
- **Wrong case:**
  - ff281902: `ph₂wénbʰos úd h₁éyti` puts the dat./abl. plural where the subject is needed. The next sentence has the correct nominative péh₂wr̥.
  - a193a252: `gʰóstis dh₃tr̥bʰós memóne` uses the dat./abl. plural for 'remembers the giver'; it should be acc. déh₃torm̥, which 55f7efb5 has.
- **The PIE and the English do not match:**
  - 1336d263: the English ends with 'Dawn follows the night', which has no PIE counterpart (six English sentences, five PIE). This is an omission, not a grammar error.

As in t021, all six grammar errors are local cell-selection slips. In four items the correct form is elsewhere in the same packet (dh₃dʰí, déh₃torm̥, péh₂wr̥, the 2sg imperative pattern).

## Recurring minor patterns

- **Notation in the Tier 1 fable lines.** Each transcribes its source faithfully, but each source's conventions clash with the corpus:
  - a6c38b14 (Lühr 2008): h₂wlh₂néh₂ with h₂; syllabic m unmarked (wéǵʰontm, méǵoh₂m, dʰǵʰémonm); full-grade gʷérh₂um; parenthesised (H), (h₁).
  - f48e6c41 (Byrd 2013): a-colouring spellings h₂áwyes and h₂wl̥h₁náh₂; agʰnutór without h₂; unaccented h₁esti, following the Vedic main-clause rule. The English 'the sheep has' is singular against the plural h₂áwibʰyos.
  - c48048af (Byrd, The King and the God): root-accented súHnum against the lexicon's suHnúm (Ved. sūnúm); unaccented wēlh₁mi.
- **Accent and ablaut of feminine adjectives:**
  - méǵh₂ih₂ (067acb43) is root-accented; Ved. mahī́ points to *meǵh₂íh₂.
  - pl̥h₁éwih₂n̥s (1336d263) should be *pl̥h₁wíh₂n̥s (Ved. purvī́ḥ).
- **Convention clash in a lexicon form:** kúdʰe 'where' (4a2817fc) has the plain velar, but the STATUS boukólos row keeps kʷ before u and cites M&A kʷu. Same item: gʷā́m writes the Stang outcome of the 1sg aorist beside gʷéh₂s (cf. t021 ḱlḗm), and h₁íns is masculine for gʷṓs.
- **Number of a possessor:** in 66f6627a, téwe 'your (sg.)' goes with a 2du verb addressed to two sons. Reflexive swóm would fit.
- **Word choice and omission:** in c295a789, the middle of the causative ǵorh₂éyeti is used for 'grow old', where *ǵérh₂- is the plain intransitive. The same item drops the English 'your' in 'Your blood is red on the field'.

## Documented limitations (noted, not penalised)

- Accentless vocatives ph₂ter (893868af, 634bc17c, 66c69fa7) and gʷh₂te (88c1bd30) are representation exceptions: STATUS, Known limitations (2).
- No item uses an accent-unresolved lexeme in a way that affects the grade. h₂ew is in the manifest and is accentless by limitation (1).

## Accepted conventions (not penalised)

- Unaugmented injunctives (aorist or present) stand in for an English present or past: méwdt, h₁áyto, léytt, h₁ludʰét, gʷéh₂t, wept. mē + injunctive marks prohibitions.
- mē + optative is used for negative wishes (mē trésoyh₁t, mē h₁r̥sḱóyh₁t), as in Gk μή + optative.
- Active root-aorist mért/mérs/mr̥dʰí 'die' is used beside middle-only mr̥yétor, as accepted in t021.
- Retracted vocatives follow the STATUS convention (súHnew, HéHḱew, mŕ̥we, wĺ̥kʷe, voc. du. HéHḱuh₁ h₁éḱwoh₁). The t021 HéHḱus accent complaint no longer applies: acc. HeHḱúm is oxytone.
- h₁rudʰéh₁n̥t is used as the neuter participle 'red'. ḱóm is used both as the deictic 'this' (876d1017) and as 'with, together' (lexicon pie-lex-kjom, Balto-Slavic evidence for *ḱ). h₂ew is used for 'back, again' (lexicon gloss). wéwket 'say' has delabialisation next to w, as the boukólos row allows.
- An accusative of goal follows verbs of motion (wĺ̥kʷom h₁éytu, ḱóymom dukdʰí, wódr̥ … dr̥mdʰí).

## Assessment

The grammar is strong:
- Coordinated subjects and addressees correctly take the dual: h₂éwsos sóh₂wl̥-kʷe … h₁l̥h₂tóm, dyḗws … dʰéǵʰōm-kʷe ph₂sih₁tā́m, péh₂wr̥ wódr̥-kʷe ne ḱéywoyh₁, and the dual sons of 66f6627a.
- A neuter-plural subject takes a singular verb (dáḱruh₂ tr̥syéh₁t), the archaic rule.
- The unaccented indefinite kʷis is kept apart from the accented interrogative kʷís.
- Anaphors take the gender of their antecedents: h₁íh₂n̥s for the sheep, h₁íh₂m̥ for the night, h₁íh₂ for the words, h₁íd for fire and fame.
- The h₁yós … só correlatives in the gnomic items are idiomatic.
- The middle is used where expected: h₁áyto 'takes', ḱéyth₂er/ḱéyor 'lies', yungih₁tó 'let it be joined', Hrumpih₁tó 'let it be broken'.

The texts suit their genres:
- **Charms** use the expected repetition and imperative chains:
  - 6bf439c4 is a proper Merseburg/Atharvaveda-type bone-to-bone, blood-to-blood, sinew-to-sinew charm.
  - ec01bcab repeats péyh₂wr̥ in every line.
  - The worm, snake and blood charms are the classic vermin, serpent and haemorrhage types: they address the illness, banish it, and invoke Perkunos or Sky.
  - 88c1bd30 sends the illness to the wolf and the wild beast.
- **Laments** use direct address to the dead, and formulas carry them: h₁nómn̥ toy ḱlutóm, ḱléwos ń̥dʰgʷʰitom, déh₃tor h₁uséwōm. 4a2817fc has a question-and-answer structure.
- **Wisdom sayings** are terse and parallel: the guest-right, oath and truth sayings, and wolf as outlaw.

The texts average about 23 words. Apart from the fable fragment and 1336d263, they read as complete: each opens with an address or a topic and closes with a refrain or a summary maxim, and nothing reads as cut off mid-thought.
- 1336d263 is the one real truncation: its English closing sentence was never rendered.
- c48048af (2 words) is an excerpt of dialogue from a Tier 1 text, not a truncated composition.
- At this length the laments are brief but feel finished. The charms could use one more round of repetition, but they do not feel incomplete.
