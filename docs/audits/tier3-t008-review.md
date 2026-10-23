# Tier-3 review t008 (wedding songs, laments, oaths, praise of a patron)

This review uses handbook knowledge only, with no browsing. I checked forms against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json`, the engine's `Lexicon.cells()`, and `validate_text`. The verdicts are in `docs/audits/packets/t008-verdicts.jsonl`.

## Counts (28 items)

- ok: 12
- minor: 10
- wrong: 6

## Errors (wrong)

The forms in these items are well-formed one by one, but the case or agreement is wrong in context, so the validator passes them.

- **Verb person does not match the subject:**
  - d8ce7b39: `gʰrómos ... gʷʰn̥yéh₁s` is 2sg; it needs 3sg *gʷʰn̥yéh₁t.
  - 88062bc6: `h₁opéyom` is 1sg, but the English is "he gave".
  - 65dcd7b7: `démont` is 3pl, but the English is "he built".
- **Wrong case:**
  - 9661df37: the instrumental `h₂éh₂usoh₁` is used as the object of 'give'.
  - 8708918f: the nominative `h₁égʷʰis` is used for the thing feared, which should be ablative/genitive. In the same item, the nom. pl. `gʷowsth₂ṓs` is used for the goal "to your own cow-stall" after `swóm`.
- **Imported text, garbled:** 86a009be is Lehmann–Zgusta-type. `ewewkʷ` has no ending and is singular with "the horses". `kʷnewti` has lost the *r̥ of *kʷr̥néwti. Notation is mixed.

## Recurring minor patterns

- **Engine paradigm flaws** (they recur wherever the lexeme is used):
  - u-stem nom. pl. `suHnúes` instead of *suHnéwes (a7b35261, ecf6f28b). The adjectives `HéHḱewes` and `h₁wésewes` are formed correctly.
  - `deduyḗr` instead of *dedwiyḗr (32b48ee0), against the engine's own `dedwiyéh₁s`.
  - The agent-noun dative `stutréy` has a zero-grade root (45fadbe6); expect *stewtréy, cf. Ved. stotré.
  - The thematic middle optative `h₁éwsoyto` lacks the *-oyh₁- that the active has (58b61453).
  - Full-grade u-stem gen. pl. (`suHnówōm`, `h₁uséwōm`) has some support from OCS synovъ but is not the handbook *-u-om. I did not count it against any item.
- **Accent of agent nouns:** `déh₃tōr`/`stéwtōr` take a genitive, but they carry root accent. Vedic puts the accent on the suffix in that construction: dātā́ vásūnām vs dā́tā vásu (9df6c88a, 32b48ee0, 45fadbe6).
- **Lexical sense:** `h₂m̥bʰí` used for 'in exchange' (2ad5f294), and `séngʷs` 'sank' for falling in battle (a7b35261).
- **Imported scholarly lines:** 652925e0 (Lühr-style `pter Werune`) and 72054765 (Schleicher 1868, pre-laryngeal) are each faithful to its source, but neither is in this corpus's convention. Their genre is tagged "fable", outside the packet's stated genres, and they need a convention tag.
- **Checked and accepted:**
  - `h₁áy-` 'give / mid. take' follows LIV *h₁ái̯-.
  - `déh₃ut` and `térh₂ut` are *deh₃w-* and *terh₂w-* (Hitt. tarḫu-).
  - `mértis` follows the lexicon's proterokinetic analysis (gen. mr̥téys).
  - `péḱos` 'livestock' is supported by Lat. pecus, -oris.
  - `séh₂gyet` 'gave a sign' is supported by Hitt. šākiya-.
  - `trémti` is athematic per the lexicon.
  - `noh₃` is in closed_class.json.

## The texts as Indo-European poetry

The texts are strong. Most use real inherited formulae, and use them correctly:

- *ḱléwos ń̥dʰgʷʰitom*, *h₁wésu ḱléwos* and *ḱlutóm h₁nómn̥*.
- *dyéw ph₂ter* with an unaccented second vocative, and *diwés dʰugh₂tḗr* for Dawn.
- *(gʷʰen-) h₁ógʷʰim*, the dragon-slaying formula.
- *wékʷōs tḗtḱmi*, the poet as carpenter of words.
- *déh₃tōr h₁uséwōm*, matching Ved. dātā́ vásūnām and Gk dōtores eáōn.

Genre by genre:

- **Oaths.** These are the best of the set.
  - 58b61453 has a Hittite-style curse built on likenesses: as the fat melts, as the wool burns, as the water boils. The all-seeing sun stands as witness.
  - 04ee203f is a dual-number treaty between two lords, sealed by drinking water.
  - 5fd49392 is a vassal's oath that ends in the Homeric dogs-and-birds curse.
- **Wedding songs.** These use Vedic ritual detail well.
  - ecf6f28b has the bride price *h₁wédmn̥*, the bride led three times around the fire, the "I am Sky, you are Earth" formula, and the bride stepping onto the millstone.
  - 0fa882aa is advice to the bride about her in-laws.
- **Laments.** These are moving.
  - 1a41578a sends the dead along the path of the fathers and past the two dogs.
  - 2ad5f294, though a praise poem, is a recognisable Hávamál "cattle die, kinsmen die" strophe.
- **Praise of a patron.** These have a real dānastuti structure: an inventory of gifts with numbers, a giver who is himself made famous by the poem, and fame shared between patron and praiser.

The main weakness is mechanical rather than poetic: number and case slips when the generator assigns a subject or object, which a simple agreement check against the plan would catch.
