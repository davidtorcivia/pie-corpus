# Tier-3 review: packet t016 (cosmogony)

I reviewed all 28 items in `packets/t016-packet.jsonl`. Verdicts are in `packets/t016-verdicts.jsonl`. I worked from handbook knowledge only, with no browsing. I spot-checked forms against `data/lexicon/lexicon.jsonl`, `data/morph/closed_class.json` and the engine's `Lexicon.cells()`.

## Counts

| verdict | n  |
|---------|----|
| ok      | 10 |
| minor   | 11 |
| wrong   | 7  |

## Recurring patterns

1. **Wrong case or number form chosen from the paradigm.** This is the main source of errors. The engine picks a real cell, but the wrong one for the slot:
   - acc. pl. where nom. sg. or abl. is needed: wiHróns for the subject 'a man' (abef24e2); yemHóns for 'of/from the twin' (5cba5250);
   - nom. pl. snóygʷʰōs with a singular verb (3c4bf32c);
   - fem. dat./abl. pl. ḱlutéh₂bʰos as the predicate of neut. h₁nómn̥ (7bfc4be0);
   - 2du aorist dʰh₁tóm for the 3pl with deywṓs (6730cb71);
   - nom. sg. ḱwṓ plus 3sg h₂lékseti after dwóh₁ instead of the dual ḱwónh₁ / h₂léksetes (7547d947).
2. **Gender agreement with the referent.** Masc. l̥h₂tós modifies neut. péh₂wr̥ (abef24e2). Fem. h₁íh₂ pl̥th₂éwih₂ refers back to masc. dyḗws (2e8228c6).
3. **Aorist/injunctive forms in present-tense texts.** Gnomic texts and hymns often use secondary aorist forms for English presents (8b7a76c6, e110427e, fe2aae83, 421bc814, 3c4bf32c), even where the lexicon has a present (gʷm̥yéti beside gʷémt). This is defensible as a gnomic injunctive, but it is inconsistent.
4. **Accent and ablaut in optatives and u-stems.**
   - Root-accented optatives keep a full-grade, unaccented suffix: bʰúHyeh₁t, bʰúHih₁n̥t, h₁áyih₁to (6730cb71, 40fb1752, 7547d947).
   - The headword pléth₂us yields nom. pl. pléth₂ewes instead of pl̥th₂éwes (7d9158a7).
5. **Lexeme senses that are borderline but defensible:** nasal-present stn̥h₂ént used intransitively for 'stood' (0a16ab21), spért 'freed' (d28c5b03), némos 'sacrifice'.
6. **Scholarly items** (a7a8ff29, 9c351b1e, 3e433031) are older or partly pre-laryngeal reconstructions. Their problems are notational (agʰnutai, no laryngeals, no accents), plus a fem. antecedent with masc./neut. yesmin and a loose purpose-clause English for finite h₁yaǵeto.

## Overall view

Most of the texts are good. Verb morphology is the strongest part:
- perfects (dedr̥ḱmé, dedwóyh₂e, widḗr), subjunctives (tl̥néh₂omes, gʷm̥yḗti after h₁yód), duals (h₁stā́m, h₂éǵetām, dh₃tóm);
- imperatives (gʷm̥dʰí, dh₃dʰí, ḱludʰí), k-aorists, causatives;
- i-stem, u-stem and n-stem nominal morphology;
- formulae such as ḱléwos ń̥dʰgʷʰitom and *dyéw ph₂ter.

Two failures recur: a wrong cell picked from an otherwise correct paradigm (case or number), and pronoun or adjective gender that does not follow the referent. These look like the planner-to-realizer handoff choosing the wrong slot, not bad morphology. They are worth fixing at the source, especially dual subjects (dwóh₁ X) and predicate adjective agreement.
