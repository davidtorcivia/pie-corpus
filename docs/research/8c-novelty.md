# 8c novelty check: accepted claims against the literature we hold

Input: `data/research/8c/review/accepted.jsonl` (13 claims). Per-claim record with full source list: `data/research/8c/review/novelty.jsonl`.

Searched (diacritic-insensitive, several spellings, loci and roots): West 2007 (epub text plus PDF for page numbers), Watkins 1995 (tess text), Schmitt 1967 (tess text plus index), Matasović 1996, Fortson 2010, Mallory & Adams 2006, Clackson, EWAia I-III, Beekes EDG, de Vaan, and `raw/books/text/kroonen-pgmc/`. Despite its name, that directory holds a Proto-Germanic grammar rather than Kroonen's dictionary, so the Germanic dictionary check is incomplete. Also the eval set `data/research/formulas/eval-r3/` (main plus single-branch) and `data/formulas/formulas.jsonl`. References give the source and page or section only.

Grades: **known** means the same parallel (same words, same branches, or a superset) is stated. **Partly known** means the words are compared, or a related formula is discussed, but this phrasal parallel or this branch's witness is not. **Not found** means nothing in what we hold.

## Counts

| grade | n | claims |
|---|---|---|
| known | 9 | C003, C004, C020, C027, C028, C030, C036, C046, C050 |
| partly known | 4 | C013, C022, C029, C048 |
| not found | 0 | none |

## Per claim

| claim | phrase | grade | main sources | what is new |
|---|---|---|---|---|
| C003 | *wiHro- *peḱu- 'men and cattle', with *salwo- + *ser- 'keep safe' | known | Watkins 1995 pp. 15, 42, 199-201, 210-213, 224, 520; Schmitt 1967 §§22-23, 437-444; West 2007 pp. 100-101, 324; Matasović §119; Fortson §§2.42-2.43, 13.74; eval r3e-410e38a07f, r3e-2594d7bdb9 | Nothing in the formula. The anchor AVŚ 12.2.29 and the free Vedic pairing paśubhiś ... vīraiḥ (AVP 19.56) are uncited. The literature has Vedic only via vīrapśá-, RV 5.20.4 and AV 8.7.11 (puruṣa-). |
| C004 | *h₁óḱewes h₁éḱwōs 'swift horses' (yoked) | known | West pp. 84, 465-466; Schmitt §§493-497; Watkins p. 12; Matasović §§48, 103-104; eval r3e-5fff2e2a1b | Nothing. The yoking frame and the RV 1.118.4b renewal (pataṃgā́ḥ) are context only. |
| C013 | *swéh₂dus médhu 'sweet mead' | partly known | West p. 84; Schmitt §529 p. 256; EWAia II p. 303; eval r3e-3b261d547a | The sources have only Vedic and Greek. The **Old English** witness (swētne + medo, Finnsburh 39) is new, which makes Germanic a third branch. |
| C020 | *dyeu ph₂ter (voc.) 'O Father Sky' | known | Schmitt §§282-289; Watkins pp. 8, 25; West pp. 170-171; Fortson §2.19; Mallory & Adams ch. 25; eval r3e-caf3b0e0d5 | Nothing. This is a textbook formula. |
| C022 | *ḱlew- + *wékʷos + 1sg 'hear my word' (god in prayer) | partly known | West pp. 316-317 (n. 18), 320; Schmitt §§396-405; Watkins p. 86 n. 2 (word equation only); eval r3e-09049c1880, r3e-f9254d9945 | 'Hear me' (śrudhí me ~ κλῦθί μοι) is known. 'Hear my word(s)' is also stated, but only with non-cognate objects (Ved. hávam, Hitt. uttar). West cites Il. 14.234 = 16.236, but for the 'as you heard before' schema. **New:** the cognate object *wékʷos (vácas- = ἔπος) governed by *ḱlew-. |
| C027 | *gʷʰen- *h₁ógʷʰim 'slay the serpent', Gmc *gʷʰonō 'serpent's slayer' | known | Watkins pp. 321-322, 353, 418-423, 505, 522; West p. 250; eval r3e-cff7b12041, r3e-2437b2b22e, r3e-de0dbfcc58 | Nothing. Watkins already has orms einbani, Beowulf bona, and the renewal of the serpent noun by *wr̥mi-. |
| C028 | *dyeu ph₂ter (voc.) opening a prayer for protection | known | Schmitt §§282-289; West pp. 131, 305; Fortson §§2.19, 13.53a; Watkins p. 8; eval r3e-caf3b0e0d5, r3e-5ef4cb728c | Nothing. The Italic spread of 'father' to Mars/Ianus in Cato is also stated. |
| C029 | *h₂eh₃mom krewh₂s h₁ed- 'eat raw flesh' | partly known | West p. 80 (ὠμηστής ~ āmā́d-); EWAia I pp. 170, 411; Beekes EDG p. 774; eval r3e-a6aee68916 | Only the compound and the word equations are known. **New:** the free three-word phrase (AVŚ 8.6.48 ~ Il. 22.347, Od. 9) and the Norse witness (hrátt + eta). |
| C030 | *déh₃tores h₁wesuHom 'givers of good things' | known | Schmitt §§14-16, 267-280 (n. 785 cites Il. 24.528); West p. 132; eval r3e-555b68698a | Nothing. Even the anchor Il. 24.528 is noted by Schmitt. |
| C036 | *wiHro- *peḱu- (+ *dem-) 'keep safe men and cattle (of my house)' | known | as C003 | Nothing in the formula. The domo ~ Av. nmāne link and the Shnuman/AVP anchors are uncited minor details. |
| C046 | *deywós *n̥-mr̥tós 'immortal gods' vs *mr̥tós 'mortals' | known | Schmitt §§78-81, 390-393; West pp. 101, 111, 127; Matasović §121; eval r3e-75334fe58a, r3e-a91d2bc03e, r3e-54a9e1dd79 | Nothing. |
| C048 | *n̥mr̥tóes h₁éḱwōs 'immortal horses' (drawing a god's chariot) | partly known | West p. 158 n. 127 (after Durante 1976: 55, not held), p. 205; Schmitt §§321-323 | The motif is known: the gods' horses are immortal (Greek, and Mithra's steeds in Avestan). AVŚ 13.1 is cited only for the Sun's horses (13.1.24). **New:** the cognate pair amŕ̥tāḥ áśvāḥ (AVŚ 13.1.47) ~ ἄμβροτοι ἵπποι (Il. 16.381), which is the Vedic witness for 'immortal horses'. Durante could not be checked. |
| C050 | *wiHrōs péḱu as object of a prayer to avert harm | known | as C003, plus Watkins p. 520 (RV 1.114 Rudra hymn) | Nothing in the formula. Its own anchors (AVŚ 4.21.14, AVP 19.14.24, Cato 149.2) are weak, uncited instances. |

## Notes

- C003, C036 and C050 are one formula: *wiHro- *peḱu-, Watkins 1995 ch. 17, Schmitt §§437-444, eval r3e-410e38a07f / r3e-2594d7bdb9. They differ only in anchors and side elements.
- The only branch-level additions are C013 (Germanic) and C029 (Germanic, plus the whole phrase). C022 and C048 add a cognate lexeme to a known schema or motif.
- C048 is the one claim where a prior source we lack (Durante 1976) may already state the lexical pair.
