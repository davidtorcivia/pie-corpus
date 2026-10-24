# Tier-3 review: packet t020 (family life cycle)

Reviewer: skeptical Indo-Europeanist pass over 28 items in `docs/audits/packets/t020-packet.jsonl`. I worked from handbook knowledge only (Fortson, Ringe, Beekes, Mallory & Adams, LIV², no browsing). I also checked the project lexicon, inflection specs, closed-class tables and `pie/validate.py`. Verdicts are in `docs/audits/packets/t020-verdicts.jsonl`.

## Counts

| verdict | n |
|---|---|
| ok | 10 |
| minor | 12 |
| wrong | 6 |

## Wrong (needs a fix at source)

These are mostly agreement and case slips in sentences that are otherwise well built:

- **Verb number vs subject:** `eecc1279` *h₂néres ... yéwgt* (3sg verb with plural subject). `beb1775f` *h₁éḱwōs HéHḱewes h₁ésmi* (1sg 'I am' where 3pl *h₁sénti* is needed).
- **Wrong case/number on a noun:** `fcf83a26` *h₁widʰéwh₂n̥s bʰúHt* (acc. pl. as predicate nominative). `b093d5d2` *ǵónh₁oh₁ bʰuHyéti* (nom. du./ins. sg. as subject of a 3sg verb). `16f6df63` *swéḱuroybʰos* (dat. pl. for the single father-in-law). These look like the realizer picking the wrong cell, not plan errors.
- **Scholarly-style text:** `3d4cde46` has *eḱwos* (sg.) as plural subject, *wewekur*, *ḱludʰe*, *ǵʰm̥on* and *kʷr̥neti*. It is a garbled adaptation of a later e/o-grade scholarly version of the Schleicher fable.

## Recurring minor patterns

- **Consonant-stem dual in bare -h₁** (*bʰréh₂terh₁*, *gʷénh₂h₁*): `0d14c70b`, `af69d73b`, `da86b925`. The handbook nom.-acc. du. is *-h₁e* (Gk πατέρε). This is systematic in the engine and is not among the stated conventions, so it is worth a decision.
- **Accent and ablaut details in table cells:** `7821ed25` (*h₃rēǵi* with no accent, voc. *h₃réǵ* with short e). `1ab5b045` (*n̥ptéy*: the weak stem is *nept-*). `671ab8ce` (*ǵn̥h₁téy* labelled locative, but -éy is the dative and the i-stem locative is -ēy).
- **Lexeme senses that rest on one branch or a thin Wiktionary gloss:** `0d43fed9` (*gʰóstis* 'enemy' is Latin only). `9ab6eebb` (*h₂nḗr* 'force' for the root noun 'man').
- **Syntax:**
  - `22bc4767`: prohibitive *mē* used for a negative statement.
  - `fba27178`: singular *téwe* addressed to plural hearers.
  - `3f81c631`: doubled enclitic *nos nos*.

## Not flagged (convention or defensible)

- **Engine conventions taken as given:** the boukólos extension *wéwket / wéwkont* (though Gk εἶπον keeps the labial), *polh₁ús* o-grade (lexicon lemma), and *h₁áy-* forms under the root id *h₂ey-* 'give'.
- **Defensible choices:** gnomic aorist *m̥rént*, and the athematic *HrewdH-* (matches Ved. róditi).
- **`3d8f603e`** is Schleicher's 1868 original copied exactly. It is internally consistent for its period (Sanskrit-style a-vocalism, no laryngeals). It should be used only if it is tagged as a historical convention.
- **`51843cc1`** is a fragment in the style of a later e/o-grade scholarly version (not Lehmann–Zgusta 1979, which has *ewewkʷet*, *ḱēr*). Its only real slip is *eweket* without kʷ.

## Overall view

The synthetic texts are good. Ablaut in verbs is handled with real care: athematic subjunctives with a short vowel and thematic ones with a long vowel, root-aorist optatives, perfect imperatives and Narten *tḗtḱti*. Dual agreement and pronoun gender are mostly right, including fem. *h₁íh₂sōm*, fem. *h₁íh₂m̥* for *bʰoydʰéh₂*, and masc. *h₁éy/h₁ím* for *h₂éǵros*. Every error found is local: one wrong cell in an otherwise correct sentence (number, case or person). That points to cell-selection bugs in the realizer rather than to problems with the plans or the grammar model.
