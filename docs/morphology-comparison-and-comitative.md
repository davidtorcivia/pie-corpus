# Degrees of comparison and pronouns with adpositions

Two gaps planners kept hitting, closed on 2026-10-30: "swifter / swiftest / swifter than the wolf", and "with me / with you / among us". The engine code is `pie/degree.py` (the comparative and superlative), `pie/realize.py` (the slot field, the checks, the pronoun fallback), `pie/validate.py` (`index_plan_degrees`) and `pie/export.py` (`token_variants`). The backtest data is `data/morph/degree_backtest.json` and the tests are in `tests/test_degree.py`. Book references are to the texts in `raw/books/text/`. They are cited and paraphrased, never quoted. "Handbook" is the *Handbook of Comparative and Historical Indo-European Linguistics* (Klein, Joseph & Fritz), cited by its printed chapter numbers (ch. 27 Indic morphology, ch. 34 and 35 Iranian morphology and syntax, ch. 41 Greek morphology, ch. 111 Indo-Iranian morphology, ch. 122 PIE morphology, ch. 123 PIE syntax), as in pie/morph.py.

## 1. Degrees of comparison

### Decision

An adjective slot may carry `"degree": "CMP"` or `"degree": "SUP"`. The engine builds the form from the adjective's root:

| | form | example (swéh₂dus 'sweet') |
|---|---|---|
| comparative | root (full grade, accented) + *-yos-* / *-is-* | swéh₂dyōs, gen. sweh₂disés |
| superlative | root (full grade, accented) + *-isto-* | swéh₂distos, -teh₂, -tom |

**Suffix and attachment.** The primary comparative *-yos-/-is-* and the superlative *-isto-* attach to the root, not to the stem of the adjective. The adjective's own suffix (-u-, -ro-) is dropped.
- Fortson §6.78 (the full grade of the root) and §6.81.
- Beekes §14.4, printed pp. 221–222 (to the root, not the stem; Skt vás-u-: vás-yas-, vás-iṣṭha-; tigmá-: téj-īyas-).
- Ringe 2006 §2.4.2(iii) p. 64 (*h₁wér-yos- from *h₁wér-u-; part of the Caland system).
- Handbook ch. 122 (directly to the adjectival root; Ved. svā́d-īyas-, Gk ἡδίω).
- Mallory & Adams 2006 (*-yes-, *-isto-).

*-tero-* is contrastive and is not a degree (Fortson §6.79; Beekes §14.4; Handbook ch. 122). It is not used.

**Root grade and accent.** The root is in the full grade and is accented in the strong cases.
- Fortson §6.78; Avestan, Handbook ch. 34.
- Vedic root accent and the matching Greek leftmost accent (Handbook ch. 122).
- When the adjective has the root in the zero grade (h₂r̥ǵrós, priHós, mh₂ḱrós) or the o-grade (polh₁ús), the full grade comes from the lexicon root it is linked to (`root_id`), but only when the two have the same consonants. Examples: h₂érǵ-, préyH-, méh₂ḱ-, pléh₁-. This matches Ved. préyas-/préṣṭha- beside priyá- and Gk πλείων beside πολύς. Ringe likewise has the full grade on a zero-grade positive.
- A labiovelar lost next to *u* in the adjective comes back from the root: h₁léngʰus beside *h₁lengʷʰ- gives h₁léngʷʰistos. This is Ringe's *h₁léngʷʰistos (Av. rənjištō), and the delabialization is the boukólos rule.
- A root adjective in C + laryngeal is built without the laryngeal, which belongs to the adjective (Beekes EDG s.v. μέγας: *meǵ-h₂-). méǵh₂s therefore gives méǵyōs and méǵistos, as Fortson §6.78 (*meg-i̯os-) and Handbook ch. 41 §2.4.1.1 (*meǵi̯os-, *meǵist[h₂]o-) write them, matching Gk μείζων, μέγιστος, Lat. maior and Av. mazišta-. The laryngeal-kept méǵh₂yōs, which is the stem of the Wiktionary spec of pie-lex-megjyoxs and what the corpus uses through that lexeme, stays as an alternative.

**Comparative inflection.** The comparative is a common-gender s-stem: the feminine is the masculine (Beekes §14.4; Gk -ίων and Lat. -ior are common gender). The suffix is amphikinetic (Fortson §6.78: masc. nom. *-i̯ōs, weak *-is-).

| cell | primary | source |
|---|---|---|
| NOM.SG m/f | R-yōs | Fortson *-i̯ōs; Beekes *-iōs |
| VOC.SG | R-yos | Handbook ch. 111 PII voc. *u̯ási̯as |
| ACC.SG | R-yosm̥ | Handbook ch. 122 PGk *swā́d-(i)yos-m̥ |
| NOM.PL / ACC.PL | R-yoses / R-yosn̥s | Gk -ους < *-oses; Myc. -o-e |
| NOM.DU | R-yosh₁e | Myc. me-zo-e (dual) |
| GEN.SG, DAT, INS, oblique pl. | R°-is- + accented ending (R°isés, R°iséy, R°isbʰós) | Fortson weak *-is-; Beekes gen. *-is-ós; Ringe *-is-´ |
| LOC.SG | R-yosi | Handbook ch. 111 PII *u̯ási̯as-i |
| neuter NOM/ACC.SG | R-yos | Beekes *-ios; Lat. maius |
| neuter NOM/ACC.PL | R-yosh₂ | Lat. maiōra, Gk -ω < *-oha |

The cells keep these alternatives, so texts that use them validate:
- Sievers' *-iyos-* (Handbook ch. 41 *su̯ādii̯os-; Handbook ch. 122 says both shapes occur and the details are elusive).
- Beekes's suffix-accented acc. *-yésm̥*.
- The generalized strong stem in the weak cases (Ved. vásyasas).
- Wiktionary's root-accented weak stem *R-is-*.
- The amphikinetic loc. *-yés(i)*.
- Beekes's older neuter *R-is* (Lat. magis).
- The collective *-yōs*.
- After C + laryngeal, Pinault's law's *Cy*: Ringe's *h₁wér-yos- beside h₁wérH-.

The engine applies that last rule only in the Wiktionary convention, so it is never primary. The superlative also keeps *-isth₂o-* (Ved. -iṣṭha-; Handbook ch. 27 and ch. 41 *-ist[h₂]o-; the lexicon's Wiktionary headwords) as an alternative. The primary is *-isto-*, after Fortson, Ringe, Mallory & Adams, and Handbook ch. 122 (little evidence for the aspirate outside Vedic).

**Which adjectives.** The primary degrees belong to primary (Caland-type) adjectives:
- Handbook ch. 111: only for primary adjectives.
- Handbook ch. 122: relational adjectives are not gradable.
- Beekes p. 181: the Caland adjectives in -ro-, -u-, -mo- take *-ies-*, *-isto-*.

`pie.degree.base` therefore accepts:
- u-stems (swéh₂dus, HéHḱus, polh₁ús);
- -ro- and -mo- adjectives (h₂r̥ǵrós, mh₂ḱrós);
- root-accented thematic adjectives (néwos, sénos: Ved. návyas-, Lat. senior);
- zero-grade *-ó-* adjectives (priHós);
- root adjectives (méǵh₂s).

It rejects the rest with a reason that check_plan passes on:
- -tó-/-to- verbal adjectives;
- -yo- relational and -wo- derivatives;
- -tero-;
- compounds;
- participles;
- o-grade thematic derivatives (bʰorós, ḱóymos);
- e-grade thematic adjectives with the accent on the thematic vowel (weydós 'seen': Handbook ch. 122, accented thematic vowel in derivation);
- lengthened-grade (vr̥ddhi) stems;
- stems with a consonant the root lacks (bʰeh₂-n-ós);
- lexemes that are already comparatives or superlatives;
- zero-grade roots with no linked root of the same consonants (dl̥h₁gʰós: its full grade *dleh₁gʰ- with metathesis is not derivable).

55 of the 258 adjectives with an inflection spec (lexicon and project reconstructions) qualify.

**Status (flagged).** Every degree token carries `degree_status`.
- **Comparative: `"nuclear-IE"`.** It is absent from Anatolian and Tocharian (Fortson §9.4; Handbook ch. 122). Handbook ch. 122 raises the possibility that it is a post-Anatolian, even post-Tocharian, innovation. Ringe calls it an elative ('exceptionally X') of West IE at the latest. Fortson, Beekes and Mallory & Adams reconstruct it for PIE.
- **Superlative: `"late-IE"`.** Ringe says it was built later on the comparative (*-is-to-* in most daughters, *-is-m̥mo-* in Italic and Celtic). Fortson §6.80 notes that PIE need not have marked a superlative at all: Homeric dĩa theā́ōn and Hitt. šallayaš šiunaš šalliš use the positive + genitive plural. Planners can still write that with a POSS slot.

The token's lex_id is `degree:<CMP|SUP>:<lex_id>`, its gloss is `sweet.CMP`, and its roots are the adjective's (`pie.compound.member_ids`).

**Standard of comparison.** 'than X' is an ABL slot with `"dep"` pointing at the comparative slot. The engine places it directly before the comparative. 'of X' with a superlative is a POSS slot (partitive genitive) with `"dep"` pointing at the superlative.
- Ringe 2006 §2.3.1 lists the standard of comparison among the PIE ablative's functions, the only explicit PIE statement in the books.
- Old Iranian marks the standard with the ablative (Handbook ch. 35 §5.4), including the pronominal *aniiō θβāt̰* 'other than you'. That is the engine's *twéd*.
- Greek uses the genitive, which took over the ablative's functions (Handbook ch. 42 §2.1; Fortson §18.37).
- Slavic uses the genitive and Proto-Germanic the dative (Ringe §4.3.1). These are case mergers or innovations.
- The Vedic and Latin ablatives of comparison are standard grammar, but none of the files here states them, so they are not cited.

A plain clause-level ABL slot (the b002 texts' *twéd méǵh₂yōs*) still works.

### Alternatives considered and rejected

- ***-tero-* as the comparative.** It is contrastive in PIE, and its use as a comparative is a later dialectal development (Fortson §6.79; Handbook ch. 122). Rejected.
- **Strict amphikinetic weak cases with a zero-grade root** (Ringe *h₁ur-is-´). No daughter keeps the zero-grade root in the comparative's weak cases; all generalize the full grade (Fortson). Not built. The weak suffix *-is-* with the accented ending is kept.
- **Beekes's hysterokinetic accusative *-iés-m*** as primary. Fortson, Handbook ch. 122 (Gk *-(i)yos-m̥*) and Vedic -yāṃsam have root accent and o-grade. It is an alternative only.
- **A separate feminine *-yes-ih₂*.** Indo-Iranian -yasī; Handbook ch. 111 *-i̯as-ī; the Wiktionary spec méǵh₂yesih₂. Greek and Latin have none, and Beekes says the feminine was the masculine. Not built; recorded here.
- ***-isth₂o-* as primary.** Its evidence is Vedic only (Handbook ch. 122). Alternative.
- **Deriving the root mechanically from `root_id` alone.** The links are heuristic (tégus → *steg-*, stuh₂rós → *steh₂-*). They are used only to restore a full grade, and only when the consonants match.
- **Accepting every adjective.** This would build *bʰr̥t-yos-* 'more carried'. The books restrict the formation to primary adjectives (above).
- **Treating the superlative as plain PIE.** Ringe and Fortson §6.80 argue against it, so it is flagged `late-IE`.

### Backtest

`data/morph/degree_backtest.json` has 45 items, each scored by `pie.degree.backtest`; `tests/test_degree.py::test_degree_backtest` pins every result.

**What the bases mean:**
- **handbook:** a handbook prints the PIE form.
- **dictionary:** an etymological dictionary prints it (de Vaan, Beekes EDG, Kroonen, EWAia).
- **multi-branch:** a primary comparative or superlative of the root is attested in two or more branches. The target is the dictionary's root + suffix, so what is tested is the engine's choice of root, grade and suffix.
- **wiktionary:** the lexicon's own headwords.
- **single-branch:** supplementary, and not in the headline rate.

**What the results mean:**
- **hit:** the engine's primary form.
- **alt:** one of the engine's alternatives.
- **miss:** the engine builds a different form.
- **rejected:** the engine refuses the adjective.

A target printed without an accent is compared without accents.

**Headline (handbook + dictionary + multi-branch + wiktionary, 36 items):**

| result | count | share |
|---|---|---|
| hit | 27 | 75% |
| alt | 4 | 11% |
| miss | 3 | 8% |
| rejected | 2 | 6% |

That is 31/36 (86%) reproduced as the primary form or an alternative. Including the supplementary single-branch items (45 in all): 32 hit, 4 alt, 4 miss, 5 rejected.

**Every miss and rejection:**
- **light-cmp-kroonen** (*h₁legʷʰ-yos-*, OIr. laigiu): Kroonen and Matasović reconstruct a nasalless root variant for Celtic. The engine builds h₁léngʷʰyos from the nasal root (Ringe's superlative is a hit). The sources disagree on the root, not on the formation.
- **swift-cmp-devaan** (*h₁oh₁ḱ-yos-*): de Vaan and EDG write the root with an o-grade *h₁oh₁ḱ-*. The lexicon and EWAia (after Schmitt) write *HeHḱ-*, and the engine follows the lexicon. A notation and root-vowel disagreement; the superlative on the lexicon's root is a hit.
- **short-cmp-edg** (*mr̥ǵʰ-yos-*, Gk βράσσων): EDG puts the Greek comparative on the positive's zero grade. de Vaan's *mregʰ-is-m̥Ho-* (Lat. brūma) has the full grade the engine uses (short-sup-multi is a hit). The sources disagree on the grade.
- **young-cmp-devaan** (rejected): *h₂yéwHō* is an n-stem. The comparative Lat. iūnior is built on the n-stem (*h₂iu-h₁n-yos-*), which is not a primary adjective root; Ved. yávīyas- has a different base. The engine does not build degrees of n-stems.
- **strong2-cmp-wikt** (rejected): *tewh₂sós* is an e-grade thematic adjective with the accent on the thematic vowel, which the rule rejects as a derivative. The lexicon's téwh₂yōs and PII *táu̯H-i̯as-* are built on the bare root.
- **single-branch, rejected:**
  - dl̥h₁gʰós (zero grade, no root link; Ved. drā́ghīyas- needs *dleh₁gʰ-*);
  - stuh₂rós (its root link is *steh₂-*; Ved. sthávīyas- needs *stewh₂-*);
  - tewh₂sós (as above).
- **single-branch, miss:** gʷréh₂us. The engine takes the headword's grade *gʷreh₂-* (Lat. gravis); Ved. gárīyas- points to *gʷerh₂-* (EDG).

**Alternatives that match:**
- Handbook ch. 41's Sievers form *su̯ādii̯os-*.
- Ringe's laryngeal-less *h₁wér-yos-* (Pinault's law).
- The Wiktionary *-isth₂os* headwords.

| basis | degree | lexeme | target (as printed, our notation) | engine | result | source | evidence |
|---|---|---|---|---|---|---|---|
| handbook | CMP | megjh2s | *meǵ-yos- | méǵyos | hit | Fortson §6.78 (pre-Gk *meg-i̯os-e, Lat. mag-i̯os-; velar written plain) | Myc. me-zo-e, Gk μείζων, Lat. maior, magis  |
| handbook | CMP | megjh2s | *meǵyos- | méǵyos | hit | Handbook ch. 41 (Greek) §2.4.1.1 *meg̑i̯os- | Gk μείζων, Myc. me-zo-e  |
| handbook | SUP | megjh2s | *meǵisto- | méǵisto | hit | Handbook ch. 41 (Greek) §2.4.1.1 *meg̑ist[h₂]o-; Fortson §6.81 Gk még-istos | Gk μέγιστος, Av. mazišta-  |
| wiktionary | CMP | megjh2s | *méǵyōs | méǵyōs | hit | lexicon pie-lex-megjyoxs (headword) |   |
| handbook | CMP | polh1us | *pleh₁yos- | pléh₁yos | hit | Mallory & Adams 2006 ch. 19 *pleh1yos | Gk πλείων, Lat. plūs, ON fleiri, Av. frāiiah-  |
| dictionary | CMP | polh1us | *pleh₁-yos- | pléh₁yos | hit | de Vaan s.v. plūs *pleh₁-ios- (de Vaan writes the glide i) |   |
| dictionary | SUP | polh1us | *pleh₁-isto- | pléh₁isto | hit | Beekes EDG s.v. πλείων | Gk πλεῖστος, ON flestr  |
| wiktionary | CMP | polh1us | *pléh₁yōs | pléh₁yōs | hit | lexicon pie-lex-pleh1yoxs (headword) |   |
| handbook | CMP | sweh2dus | *sweh₂diyos- | swéh₂dyos | alt | Handbook ch. 41 (Greek) §2.4.1.1 *su̯ādii̯os- (Sievers variant; ch. 122: both *-yos and *-iyos) | Ved. svā́dīyas-, Gk ἡδίων  — the engine's primary is *-yos-, *-iyos- an alternative |
| handbook | SUP | sweh2dus | *sweh₂disto- | swéh₂disto | hit | Handbook ch. 41 (Greek) §2.4.1.1 *su̯ād-ist[h₂]o-; ch. 122 Ved. svā́diṣṭha- = Gk ἥδιστος | Ved. svā́diṣṭha-, Gk ἥδιστος  |
| wiktionary | CMP | sweh2dus | *swéh₂dyōs | swéh₂dyōs | hit | lexicon pie-lex-sweh2dyoxs (headword) |   |
| wiktionary | SUP | sweh2dus | *swéh₂disth₂os | swéh₂distos | alt | lexicon pie-lex-sweh2disth2os (headword) |   |
| handbook | SUP | h1lenghus | *h₁léngʷʰistos | h₁léngʷʰistos | hit | Ringe 2006 p. 91 (Av. rənjištō) | Av. rənjišta-; Gk ἐλάχιστος (nasalless)  |
| wiktionary | SUP | h1lenghus | *h₁léngʷʰisth₂os | h₁léngʷʰistos | alt | lexicon pie-lex-h1lengwhisth2os (headword) |   |
| dictionary | CMP | h1lenghus | *h₁legʷʰ-yos- | h₁léngʷʰyos | miss | Kroonen s.v. *lingwan- *h1legwh-ios- (OIr. laigiu); Matasović s.v. *legu- | OIr. laigiu, Gk ἐλάσσων  — a nasalless root variant |
| dictionary | CMP | HeHkjus | *h₁oh₁ḱ-yos- | HéHḱyos | miss | de Vaan s.v. ōcior *h1oh1k-ios- | Lat. ōcior, Ved. ā́śīyas-, Av. āsiiah-  — the lexicon writes the root HeHḱ- |
| multi-branch | SUP | HeHkjus | *HeHḱisto- | HéHḱisto | hit | target: the lexicon's root HeHḱ- + *-isto- | Ved. ā́śiṣṭha-, Av. āsišta-, Gk ὤκιστος  |
| handbook | CMP | h1werHus | *h₁wér-yos- | h₁wérHyos | alt | Ringe 2006 §2.4.2(iii) p. 64 *h₁wér-yos- ~ *h₁ur-is- | Ved. várīyas-, váriṣṭha-  — Ringe writes the root without the laryngeal |
| dictionary | CMP | mregjhus | *mr̥ǵʰ-yos- | mréǵʰyos | miss | Beekes EDG s.v. βραχύς (zero grade, for βράσσων) | Gk βράσσων; Lat. brūma (de Vaan *mregʰ-is-m̥Ho-, e-grade)  — zero vs full grade: the sources disagree |
| multi-branch | SUP | mregjhus | *mreǵʰisto- | mréǵʰisto | hit | target: the root *mreǵʰ- (de Vaan s.v. brevis, e-grade) + *-isto- | Gk βράχιστος, Lat. brūma (*-is-m̥mo-)  |
| handbook | CMP | senos | *sen-yōs | sényōs | hit | Fortson §6.78 *sen-i̯ōs | Lat. senior, OIr. siniu  |
| multi-branch | SUP | senos | *senisto- | sénisto | hit | target: *sen- + *-isto- | Goth. sinista; (OIr. sinem, OW hinham *-is-m̥mo-)  — only Germanic has *-isto- here |
| dictionary | CMP | h2yewHox | *h₂iu-h₁n-yos- | — | rejected | de Vaan s.v. iuvenis *h2iu-h1n-ios | Lat. iūnior, Ved. yávīyas-, PGmc *junhizan-  — an n-stem positive |
| multi-branch | CMP | newos | *newyos- | néwyos | hit | target: *new- + *-yos- | Ved. návyas-, návīyas-; PGmc *niwizō  |
| multi-branch | SUP | newos | *newisto- | néwisto | hit | target: *new- + *-isto- | Ved. náviṣṭha-; PGmc *niwistaz  |
| multi-branch | CMP | bhengjhus | *bʰenǵʰyos- | bʰénǵʰyos | hit | target: EWAia *bʰenǵʰ- + *-yos- | Ved. báṃhīyas-, Gk πάσσων  — Gk has the positive's zero grade |
| multi-branch | SUP | bhengjhus | *bʰenǵʰisto- | bʰénǵʰisto | hit | target: *bʰenǵʰ- + *-isto- | Ved. báṃhiṣṭha-, Gk πάχιστος  |
| multi-branch | SUP | mh2kjros | *meh₂ḱisto- | méh₂ḱisto | hit | target: EDG *meh₂ḱ- (s.v. μῆκος) + *-isto- | Gk μήκιστος, Av. masišta-, OP maθišta-  — Gk long vs Iranian short root vowel (EDG) |
| multi-branch | SUP | h2engjhus | *h₂enǵʰisto- | h₂énǵʰisto | hit | target: EWAia *h₂enǵʰ- + *-isto- | Gk ἄγχιστος; Ved. áṃhīyas- (cmp)  — weak: Gk 'nearest' (EDG builds it on ἄγχι) |
| multi-branch | SUP | pleth2us | *pleth₂isto- | pléth₂isto | hit | target: *pleth₂- + *-isto- | Ved. práthiṣṭha-, Gk πλατάνιστος  — weak: πλατάνιστος is built on *pl̥th₂n̥- (Ringe p. 27) |
| wiktionary | CMP | newos | *néwyōs | néwyōs | hit | lexicon headword néwyōs (lexicon.jsonl, Wiktionary) |   |
| wiktionary | CMP | mregjhus | *mréǵʰyōs | mréǵʰyōs | hit | lexicon headword mréǵʰyōs |   |
| wiktionary | CMP | bhengjhus | *bʰénǵʰyōs | bʰénǵʰyōs | hit | lexicon headword bʰénǵʰyōs |   |
| wiktionary | CMP | h1lenghus | *h₁léngʷʰyōs | h₁léngʷʰyōs | hit | lexicon headword h₁léngʷʰyōs |   |
| wiktionary | CMP | dweh2ros | *dwéh₂yōs | dwéh₂yōs | hit | lexicon headword dwéh₂yōs |   |
| wiktionary | CMP | tewh2sos | *téwh₂yōs | — | rejected | lexicon headword téwh₂yōs |   |
| single-branch | CMP | h1wesus | *h₁wesyos- | h₁wésyos | hit | Beekes §14.4 (vásyas-, vásiṣṭha-); target *h₁wes- + *-yos- | Ved. vásyas-, Av. vahiiah-  |
| single-branch | CMP | priHos | *preyHyos- | préyHyos | hit | Handbook ch. 27 (Vedic) §2.5 préyāṃs-; target *preyH- + *-yos- | Ved. préyas-, Av. fraēšta-  |
| single-branch | CMP | dlh1ghos | *dleh₁gʰyos- | — | rejected | EWAia s.v. dīrghá-; target *dleh₁gʰ- + *-yos- | Ved. drā́ghīyas-, Av. drājiiah-  |
| single-branch | SUP | dweh2ros | *dweh₂-isto- | dwéh₂isto | hit | EWAia s.v. dūrá- *dueh2-isto- | OP duvaišta-  |
| single-branch | SUP | kjuh1ros | *ḱewh₁isto- | ḱéwh₁isto | hit | Handbook ch. 111 (Indo-Iranian) PII *ćáu̯Hišta-; target *ḱewh₁- + *-isto- | Ved. śáviṣṭha-, Av. səuuišta-  |
| single-branch | CMP | stuh2ros | *stewh₂yos- | — | rejected | EWAia s.v. sthūrá-; target *stewh₂- + *-yos- | Ved. sthávīyas-, YAv. staoiiah-  |
| single-branch | CMP | tenh2us | *tenh₂yos- | ténh₂yos | hit | EWAia s.v. tanú-; target *tenh₂- + *-yos- | Ved. tánīyas- (Br.)  |
| single-branch | CMP | gwreh2us | *gʷerh₂yos- | gʷréh₂yos | miss | Beekes EDG s.v. βαρύς (full grade *gʷerh₂- in gárīyān) | Ved. gárīyas-  — the lexicon's headword has *gʷreh₂- (Lat. gravis) |
| single-branch | CMP | tewh2sos | *tewh₂yos- | — | rejected | Handbook ch. 111 (Indo-Iranian) PII *táu̯H-i̯as- | Ved. távīyas-  |

Lexicon issues found while collecting this. They are reported, not fixed, because data/lexicon/ was off limits:
- pie-lex-pleh1yoxs 'full' mixes the comparative with Gk πλεῖος 'full', a -yo- adjective.
- pie-lex-wersos 'better' (OIr. ferr) is an o-stem, not a *-yos-* comparative.
- pie-lex-megjyoxs's spec has a laryngeal (méǵh₂yos) that no daughter supports.
- pie-lex-kjom's palatal *ḱ* rests on Slavic and Baltic reflexes (sъ, sù) that Derksen, Handbook ch. 1221 and Mallory & Adams derive from *som/*sm̥* instead. de Vaan, Kroonen and Matasović write *kom*.

## 2. Personal pronouns with adpositions, and the missing instrumental

### The gap

The 1st- and 2nd-person and reflexive pronouns (`closed_class.json` "personal") have nominative, accusative, genitive and dative cells, plus the ablative *méd*, *twéd*, *n̥sméd*, *usméd* (Beekes §15.3.1; de Vaan s.v. me; Fortson §13.52a: Lat. mēd < PIE *med). They have no instrumental and no locative.
- Ringe 2006 §2.3.6(iii) p. 57 reconstructs only four singular cases (no ablative either) and '???' for the stressed plural oblique.
- Fortson §7.2: little beyond the bare stems can be reconstructed.
- Beekes §15.3.1 alone offers a singular loc./ins. *h₁mói*, *tói*, which he calls unclear; it has the shape of his dative-genitive clitic. Nobody reconstructs a plural instrumental.
- The daughters' instrumentals are each built anew: Ved. máyā, OCS mъnojǫ (with the a-stem ending: Handbook ch. 1222), Lith. manimì.

A pronoun as an adposition's `dep` already worked for the cases it has (méd ḱóm). INS and LOC died in the realizer with "form not generated".

### Survey: 'with me' in the daughters

| branch | expression | adposition (cognate of) | pronoun case | source |
|---|---|---|---|---|
| Vedic | sahá + instr. (máyā) | sahá (*sm̥-dʰ-*; sám is a preverb only) | instr. | EWAia s.vv. sahá, sám; Handbook ch. 28 §4.1.2 |
| Old Iranian | hadā, mat̰ + instr. | *sem* family | instr. | Handbook ch. 35 §2.2 |
| Greek | σύν + dat.; μετά + gen./dat. | σύν unclear (EDG s.v. ξύν); μετά *meth₂/*met-* | dat. (gen.) | Handbook ch. 42; Beekes EDG |
| Latin | mē-cum | cum (*kom*) | abl. mē(d) < *h₁med* | de Vaan s.vv. com-, me; Fortson §13.52a |
| Gothic | miþ + dat. (miþ sis) | miþ (*medi < *met-i*, the cognate of médʰi) | dat. | Kroonen s.v. *medi; Fortson ch. 15 (Mk 8:14) |
| Old Irish | co + dat.; conjugated prepositions | co (*kom*) | dat. | Matasović s.v. *kom |
| OCS | sъ + instr. (sъ tobojǫ) | sъ (*s(o)m*, Derksen; *kom*, Matasović) | instr. | Handbook ch. 117; Derksen |
| Lithuanian | su + instr. (su manimì) | su (*sum/*som*) | instr. | Derksen (Baltic) s.v. su |
| Hittite | katti=mi | katti + enclitic possessive (katta + gen.) | possessive | Kloekhorst s.v. katta |
| Tocharian B | cimp(a) 'with thee' | comitative suffix on the oblique | oblique | Fortson §17.23; Adams s.v. -mpa |

**What the survey shows:**
- Where an instrumental survives (Indo-Iranian, Balto-Slavic), the comitative is the instrumental. The adposition there belongs to the *sem/*som* family, not to *kom*.
- *kom* survives only where the instrumental has merged into another case: Latin + ablative, Old Irish + dative.
- Handbook ch. 123 §4.4: the case of an adposition's noun comes from its role, and lexical case selected by the adposition is a later development.
- Handbook ch. 123 §5.3, after Strunk: the instrumental was sociative with animates.
- Fortson §6.1 and Mallory & Adams §4.4, §4.7: the instrumental marks accompaniment.

So for nouns 'with X' stays INS + ḱóm, as before.

### Decision

A personal pronoun governed by an adposition (a `dep` of an ADV slot) in the role INS ('with me') or LOC ('in / among us') is realized in the **dative**:
- méǵʰye ḱóm 'with me', tébʰye ḱóm 'with you';
- n̥sméy ḱóm 'with us', usméy ḱóm 'with you (pl.)';
- n̥sméy médʰi 'among us'.

The token's features name the cell it really is (DAT.SG). It carries `case_fallback: "ins->dat"` or `"loc->dat"`, so the export and any reviewer can see the substitution. A dual takes the plural, as for every dual oblique.

**Why the dative:**
- It is the case a pronoun takes after 'with' in three branches whose oblique cases merged: Greek σύν + dat., Gothic miþ + dat. (miþ is the exact cognate of médʰi), and Old Irish co + dat. (the cognate of ḱóm).
- Only Latin has the ablative.
- Beekes's tentative pronominal loc./ins. *h₁mói/*tói* is itself a dative-shaped form.

**Two rules check_plan enforces:**
- Without an adposition, a pronoun INS or LOC is a plan error, with the reason and a hint to use ḱóm or an adposition. 'By me' (agent or means) has no form to fall back on.
- A pronoun governed by an adposition must be the stressed form. An enclitic moves to the clause's second position, away from its adposition.

### Alternatives considered and rejected

- **Ablative (Lat. mē-cum, the exact phrase *méd ḱóm*).** This is the strongest single correspondence: the ḱóm-cognate with the very ablative cell the table has, postposed as the engine places it. But it is one branch against three, and the Latin ablative is itself a syncretic case that absorbed the instrumental. Planners who want it can write role ABL with the dep: the engine accepts every adposition role, and méd ḱóm is what it then produces. The brief steers them to INS, because ABL + adposition otherwise reads 'from'.
- **Reconstructing an instrumental** (*h₁mói*, after Beekes; or *méh₁*). Beekes himself calls the form unclear, no other handbook gives one, and none gives a plural. The project rule is not to invent cells the sources mark unreconstructable. Rejected.
- **The genitive** (Gk μετ' ἐμοῦ; Hitt. katta + gen.). This is a construction of μετά and katta, not a general comitative, and it has no wider support. Rejected.
- **Choosing the case per adposition** (ABL for ḱóm after Latin, DAT for médʰi after Gothic). This would make 'with me' depend on which of two near-synonyms the planner picked, on one branch each. Rejected for one rule. The survey table keeps the evidence for revisiting it.
- **Leaving the gap.** Planners rewrote 'with me' clumsily or dropped it. Rejected.

### 'Between us', 'in me'

*h₁entér 'between' takes the accusative: Ved. antár + acc. 'between' (+ loc. 'within'), Osc. anter + acc., OIr. eter + acc. (Handbook ch. 28 §2.1.3; de Vaan s.v. inter; Matasović). 'Between us' is therefore role GOAL with the dep, the accusative n̥smé h₁entér. The pronoun has that cell, so no fallback is needed.

*h₁én 'in' takes the locative for place and the accusative for direction (de Vaan s.v. in; Matasović s.v. *en; Ringe §4.3.1). 'In me' is LOC, which falls back to méǵʰye h₁én; 'into me' is GOAL.

## 3. What planners write

The section below is in docs/generation/planner-brief-v4.md.

**Comparison: "swifter", "swiftest", "swifter than X" (new).** Put `"degree": "CMP"` (comparative) or `"degree": "SUP"` (superlative) on an adjective slot: MOD, PRED, APPOS, or a noun role with a `gender` ("the swiftest one"). The engine builds the form from the root (HéHḱus → HéHḱyōs, HéHḱistos; swéh₂dus → swéh₂dyōs, swéh₂distos; méǵh₂s → méǵyōs, méǵistos). Only primary adjectives have these forms: u-stems, -ro- adjectives, root-accented ones like néwos and sénos, and old root adjectives like méǵh₂s. Participles, -tó- adjectives ('given', 'seen'), -yo- adjectives ('heavenly'), compounds and the like are rejected with a reason; say "more" another way there. The standard ("than the wolf") is its own slot, role ABL, with `"dep"` = the index of the comparative slot; it stands right before the comparative. "The horse is swifter than the wolf" =
`[{"lex_id": "<horse>", "role": "SUBJ"}, {"lex_id": "<wolf>", "role": "ABL", "dep": 2}, {"lex_id": "<swift>", "role": "PRED", "degree": "CMP"}]` with `"type": "nominal"` → h₁éḱwos wĺ̥kʷōd HéHḱyōs. "Than you" is the pronoun in ABL (twéd). With a superlative, "of the horses" is role POSS (num PL) with `"dep"` = the superlative slot. The older way to say "the greatest" is just as good, and better in hymns: the positive with a genitive plural ("divine among goddesses"). Use the slot field instead of the old comparative lexemes (méǵyōs, swéh₂dyōs, pléh₁yōs): it covers any primary adjective, and the tokens say what they are (`degree_status`: the comparative is "nuclear-IE", missing in Anatolian; the superlative "late-IE").

**Pronouns with adpositions: "with me", "among us", "between us" (new).** A 1st/2nd-person pronoun can be an adposition's object like any noun: its own slot with `dep` = the ADV slot. "With me / with you / with us" = ADV ḱóm (pie-lex-kjom) + the pronoun with role INS → méǵʰye ḱóm, tébʰye ḱóm, n̥sméy ḱóm. "Among us" = ADV médʰi + the pronoun with role LOC → n̥sméy médʰi. The pronouns have no instrumental or locative (none is reconstructable), so under an adposition the engine uses the dative and marks the token `case_fallback`; this is expected. Without an adposition a pronoun cannot be INS or LOC ("by me" is rejected; rephrase). "Between us" = ADV h₁entér + pronoun role GOAL (accusative: n̥smé h₁entér). "From me" = ABL (méd h₂epó). Never mark such a pronoun `enclitic`. Nouns keep the instrumental: "with the wolf" = wĺ̥kʷoh₁ ḱóm.

## 4. Checks

- No corpus record changes. All 2270 records of the 36 approved Tier 3 batches (b001–b004, t002–t042) were re-realized from their stored plans under the engine before and after the change, against the same frozen copy of the plans and the same data. pie, gloss, tokens and the check_plan output are byte-identical. The comparison script is in the session scratchpad: rerealize2.py and regress.sh.
- `tests/test_degree.py` covers:
  - the paradigms and the base derivation;
  - check_plan's rejections;
  - "swifter than the wolf", the comparative as a MOD with its standard, and the superlative with a partitive genitive;
  - validation at the exact tier (`index_plan_degrees`);
  - the export's alternatives;
  - the five pronoun fallbacks and their rejections;
  - nouns keeping INS under ḱóm;
  - the backtest.
