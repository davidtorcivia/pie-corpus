# Tier-3 review: t014 packet (farm and herd life)

Reviewer stance: skeptical Indo-Europeanist, handbook knowledge only (Fortson, Beekes, Meier-Brügger, Ringe, LIV-style conventions). No browsing. I checked a few lexeme paradigms with the engine (`Lexicon.cells`) and the lexicon and inflection specs to find where forms come from. I did not read the corpus, generation or audit data.

## Counts (28 items)

- ok: 8 (06571375, 0e3acf34, 9b272d49, 678a0c68, 12a83cac, 89340fd8, 2d00a531, 1b056e80)
- minor: 9 (84c006c9, 9c9527f3, 095ab06d, c8673123, eb11ddb3, 418f8ada, 2e1b48dd, b1d8b5c1, d0f6195e)
- wrong: 11 (c8dd04cc, f0d8a9ca, baa9206e, 7e9e9f52, 4ff05e8d, 08223209, b7b20df6, c08325a4, 745db3b3, 932d2f44, 3936669d)

## Recurring patterns

1. **NP-level -kʷe on the first conjunct.** The engine writes "A-kʷe B" (h₂óweyes-kʷe h₁éḱwos, gʷṓs-kʷe h₂ówins, puHróm-kʷe wósh₂r̥, h₂nḗr-kʷe gʷḗn, sóh₂wl̥-kʷe n̥bʰrós, ǵʰéslom gʷówes-kʷe ...). PIE practice (Lat. senatus populusque, Ved. A B ca) is "A B-kʷe" or "A-kʷe B-kʷe". Clause-level -kʷe is placed correctly. Affected items: 9c9527f3, 095ab06d, 418f8ada, 7e9e9f52, 2e1b48dd, b1d8b5c1, b7b20df6, c08325a4, d0f6195e. This is systematic and should be fixed in the realizer.
2. **Wrong paradigm cell picked: number or person.** The forms are well built, but the slot is wrong:
   - polh₁ús (nom. sg.) for 'they are many': 7e9e9f52, 4ff05e8d
   - h₂élbʰitih₁ (dual) for 'the barley': 745db3b3
   - h₂éǵrons (pl.) for 'the field': 3936669d
   - gʷíh₃wom (1sg) for 'they lived': c08325a4
   - h₂élomes (1pl) for 'who nourishes': f0d8a9ca
   
   These look like plan-to-cell mapping bugs, not morphology bugs.
3. **Agreement with the referent.**
   - Neuter-plural 'ears of grain' is resumed by masc. pl. n̥th₂grṓs h₁sént (08223209).
   - The predicate adjective is put in the dative, attracted to the husband (lewbʰṓy, baa9206e).
   - Earth is addressed with masculine adjectives (b7b20df6). The spec for dʰéǵʰōm has gender m, which is wrong: it is feminine.
4. **Engine paradigm defects worth fixing at source.**
   - IMP.2SG h₂ur̥sdʰí: the w and the r are both vocalized; it should be h₂wr̥sdʰí.
   - u-stem nom. pl. suHnúes (should be *-éwes); polh₁ús offers both forms.
   - u-stem instr. pl. pl̥h₁éwbʰis (should be *-ubʰís).
   - The lexicon has h₂éryeti with no h₃, inconsistent with h₂érh₃trom.
   - Accent on the weak reduplicated forms: dédh₃mes should be *dedh₃més.
5. **Tense in present-tense texts.** Aorists with secondary endings are used for English presents (84c006c9, d0f6195e). This is defensible as gnomic or completive aorist, but the engine seems to map certain verbs ('be sated', 'lie down', 'rain', 'grow up') to aorist regardless of tense.
6. **Scholarly texts.**
   - 932d2f44 is Schleicher's 1868 fable in obsolete notation. It should not sit unlabeled beside handbook-notation PIE.
   - c8673123 and c8dd04cc look like lines from Byrd's 'King and God', with transcription slips: wéwked for wéwkʷet, and the possessor in the nominative (h₃réḱs) instead of the genitive h₃rēǵés.

## Overall view

The synthetic texts are better than I expected. Ablaut and endings are mostly right: perfects stesth₂ḗr, tetr̥pḗr, dedórḱth₂e; subjunctives skinédomes, wéǵʰōmes; causatives sodéyet, bʰoréyet, h₃roǵéyete; the athematic optatives; dual verbs with dual subjects. Lexeme choice is idiomatic and often attested-collocational (déms pótnih₂, ń̥dʰgʷʰitom ḱléwos, gʷowsth₂ṓd). Almost every 'wrong' verdict comes from a wrong cell or wrong agreement target, not from bad morphology. The fixes are therefore cheap and mechanical: the -kʷe placement rule, number and person selection, gender agreement with referents, and the paradigm defects listed above.
