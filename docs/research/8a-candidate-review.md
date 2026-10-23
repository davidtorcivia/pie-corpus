# Phase 8a: independent review of formula candidates (2026-10-23)

Reviewer: skeptical-Indo-Europeanist subagent. Scope: every record in `data/research/formulas/candidates.jsonl` with `significant_in_both: true` (39 rows). Seven of the rows are the same word pair listed twice under homograph PIE entries (5/10, 16/17, 27/28, 72/73, 106/107, 135/179, 151/152), so there are **32 distinct pairs**.

How the checks were done:
- **Attestations.** Every example locus in the file was read in the raw corpora: VedaWeb `versions/vnh.csv` (van Nooten & Holland saṃhitā text) and the Perseus AGDT 2.1 treebank XML. Scripts ran with `python3 -I` from the scratchpad, and nothing in `raw/` was executed. **All cited loci exist and contain the two lemmas.** One Homer locus is truncated in the file ("Od. 2" for a παννύχιος line under rank 20).
- **Corpus-wide search.** For the three flagged candidates I also searched the whole RV and the whole Homer for the two words, not only the file's examples.
- **Literature.** West, *IEPM*, was searched in `raw/books/text/west/` (EPUB text). Watkins, *How to Kill a Dragon*, was searched in `raw/books/text/watkins/` (OCR; no Greek script and no Vedic diacritics). Both searches ignore accents.

**Two caveats on the file itself.**
- The caller's premise that all three flagged candidates are "same relation in both" does not hold. Only rank 43 (barren cow) has `same_in_both: true`. Ranks 72/73 (drink + satisfy) are `adj+noun` / none, and rank 86 (yoke + bulls) is `verb+obj` / none.
- The relation labels are unreliable anyway. RV 8.35.10a *píbataṃ ca tṛpṇutáṃ ca* is two coordinated imperatives, but it is tagged `agree` / `adj+noun`. `same_in_both` should not be used as evidence downstream.

## Verdict counts
| verdict | rows | distinct pairs |
|---|---|---|
| known (discussed by West) | 5 | 4 |
| plausible new | 2 | 1 |
| generic | 6 | 6 |
| chance | 7 | 7 |
| mapping error | 19 | 14 |
| **total** | **39** | **32** |

## Table
Text quotes are from the corpora. "W" is West, *IEPM*; "Wk" is Watkins.

| rank | pair (PIE) | attestation checked (RV ~ Homer) | cognate? | verdict | reason |
|---|---|---|---|---|---|
| 1 | *médʰu* + *peh₃-* | *áśvinā píbatam mádhu* (1.15.11a) ~ *μέθυ πίνετο* (Il. 9.469, Od. 9.45) | yes | generic | Drink + drink-substance. W discusses *μέθυ ἡδύ* ~ *svādór mádhvaḥ* (ch. 2), a different pair, but not "drink mead". The method doc's "known" has no source in W/Wk. |
| 2 | *h₂éwsōs* + *sóh₂wl̥* | *uṣásā sū́ryeṇa* (1.62.5b) ~ *ὑπ' ἠῶ τ' ἠέλιόν τε* (Il. 5.267, the only Homer hit) | yes | generic | Dawn and sun co-occur in any description of morning. Homer has 1 hit. |
| 4 | *méh₂tēr* + *ph₂tḗr* | *pitáraṃ ca dṛśéyam mātáraṃ ca* (1.24.1d) ~ *πατὴρ καὶ πότνια μήτηρ* (Il. 11.452) | yes | known | Parental merism. W ch. 4 discusses Dyaus pitā / Pṛthivī mātā and cites RV 1.89.4. Generic in any case. |
| 5 | *gʷṓws* + *welH-* 'strong' | *gā́ … valásya* (2.12.3b) ~ *βουσὶν ἕλιξιν* (Il. 12.293), *εἰλίποδας βοῦς* | no | mapping error | valá- 'enclosure, Vala' (*wel-* 'cover') vs ἕλιξ / εἰλίπους (*wel(H)-* 'turn'). Two roots, and the 'strong' entry fits neither. |
| 10 | *gʷṓws* + *welH-* 'roll' | same as 5 | no | mapping error | Duplicate of 5. Right for the Greek, wrong for valá-. |
| 15 | *déywih₂* + *h₂éwsōs* | *devī́m uṣásaṃ* (1.115.2a), *úṣo devi* ~ *Ἠῶ δῖαν* (Od. 12.7 etc.) | root only | known | W ch. 5: *δῖα* is Dawn's formulaic epithet. W's comparandum is *divyá-* ('heavenly', *yóṣaṇe divyé*), not devī́. δῖος < *diw-yo-* ≠ devī́ < *deyw-ih₂*, so the lexeme-level mapping is off. |
| 16 | *bʰeh₂-* 'speak' + *smey-* | *smayate vibhātī́* (1.92.6c) ~ *ὣς φάτο μείδησεν δὲ* (Il. 1.595 etc.) | no | mapping error | √bhā 'shine' ≠ φημί 'say' (homograph). Incidentally, W ch. 5 discusses this very RV verse (Dawn's smile, *smayate*) and a possible Greek counterpart, but not with φημί. |
| 17 | *bʰeh₂-* 'light' + *smey-* | same as 16 | no | mapping error | Duplicate of 16. Right for the Vedic, wrong for φημί. |
| 18 | *h₁éḱwos* + *yewg-* | *áśvān yuyujāná* (4.45.6c) ~ *ἵππους ζευγνῦμεν* (Il. 16.145), *ζεύξειεν … ἵππους* (Il. 24.14) | yes | generic | Horses are the default object of 'yoke' (cf. Lat. *equos iungere*). The method doc's "known" has no source: neither W nor Wk treats it as a formula. |
| 20 | *h₂éwsōs* + *nókʷts* | *náktā … uṣā́sā* (1.73.7c, 7.42.5c) ~ *νὺξ … ἠώς* (Il. 10.251, 7.433) | yes (aktú- doubtful) | known | W ch. 5: Night and Dawn as alternating sisters (RV 1.113.2), with a Hesiod parallel. A natural merism. Mapping aktú- to *nókʷts* is doubtful. |
| 21 | *bʰer-* + *ǵʰes-* | *bibharti hásta* (8.29.3a) ~ *χέρνιβα … φέρουσα* (Od. 1.136) | root only | chance | The Greek is the type-scene "a maid carrying hand-washing water" (χέρνιψ, a compound), not "carry in the hand". "Carry in hand" would be generic anyway. |
| 23 | *dʰuh₂mós* + *h₃er-* | *dhūmá ṛṇvati* (6.2.6a) 'smoke rises' ~ *θυμὸν ὄρινε* (Il. 11.804) 'stirred his heart' | yes (θυμός ~ dhūmá- is standard) | chance | Lexically correct, semantically unrelated. One co-occurrence pattern is about fire, the other about emotion. |
| 27 | *pónth₂os* + *yeh₂-* 'go' | *yātam pathíbhir* (1.183.6c) ~ *ζήτει … πόντῳ* (Il. 14.258) | no | mapping error | ζητέω is not from *yeh₂-*, and the Homer line has the two words in separate clauses. |
| 28 | *pónth₂os* + *yeh₂-* 'request' | same as 27 | no | mapping error | Duplicate of 27. |
| 29 | *h₁wérHus* + *pónth₂os* | *uraú pathí* (3.54.9d), *urúḥ pánthā* (10.107.1d) ~ *εὐρέα πόντον* (Il. 6.291), *εὐρέι πόντῳ* (Od. 12.293) | yes | generic | The cognation pánthā- ~ πόντος is accepted, but the referents differ (path vs sea). W ch. 2 calls "broad sea" banal, gives Old English and Serbo-Croat parallels, and does not link it to pánthā-. 'Wide' is the default epithet of both nouns. |
| 34 | *h₁yaǵnós* + *ten-* | *yajñáṃ tanvānā́* (7.10.2b) ~ *ἁγνή· τίς δέ κε τόξα τιταίνοιτ'* (Od. 21.259) | root level | chance | "Extend the sacrifice" is a Vedic idiom. In Greek, ἁγνή describes the feast day and τιταίνω takes the bow: two clauses. |
| 38 | *médʰyos* + *steh₂-* | *mádhye tasthúr* (1.105.10b) ~ *μέσον ἱστίον* (Il. 1.481) | root only | chance | 'Stood in the middle' vs 'middle of the sail' (ἱστίον, from ἵστημι). |
| 43 | *gʷṓws* + *stérih₂* | *staryàm pipyathur gā́m* (1.116.22d), *staryò ná gā́vaḥ* (7.23.4a) ~ *στεῖραν βοῦν* (Od. 10.522 = 11.30), *βοῦν στεῖραν* (Od. 20.186) | yes | generic | The word's primary referent is a barren cow in both languages, and the contexts differ. See below. |
| 45 | *déywih₂* + *gʷḗn* | *gnā́ṃ devī́m* (5.43.6b) ~ *δῖα γυναικῶν* (Il. 3.171) | γυνή ~ gnā́ yes; δῖα ≠ devī́ | mapping error | δῖα < *diw-yo-* is a different derivation from devī́. The constructions differ too: apposition vs partitive superlative. W ch. 4 treats *δῖα γυναικῶν* as originally 'consorts of Zeus', with no Vedic comparison. |
| 48 | *h₃dónts* + *bʰes-* | *dadbhír … bapsati* (8.43.3c) ~ *ψυχρὸν … χαλκὸν ὀδοῦσιν* (Il. 5.75) | no | mapping error | ψυχρός is not from *bʰes-* 'chew'. |
| 72 | *peh₃-* + *terp-* 'numb' | see 73 | (homograph) | plausible new | Duplicate of 73 under the wrong homograph (*terp-* 'stiffen', Lat. *torpeo*). |
| 73 | *peh₃-* + *terp-* 'satisfy' | *píbataṃ ca tṛpṇutáṃ ca* (8.35.10a), *píbā … tṛpṇuhi* (2.36.4d) ~ *πίνοντά τε τερπόμενόν τε* (Od. 1.258), *τάρπημεν ἐδητύος ἠδὲ ποτῆτος* (Il. 11.780) | yes | plausible new (weak) | Same two roots, same coordination, and *terp-* takes the genitive of the drink in both, in host-to-guest invitations. Not in W/Wk. See below. |
| 75 | *pónth₂os* + *derḱ-* | *pánthā … adṛśrann* (7.76.2a) ~ *πόντον ἐπ' ἀτρύγετον δερκέσκετο* (Od. 5.84) | yes | chance | 'The path appeared' vs 'gazed over the sea'. The referents and the sense of the verb both differ. |
| 86 | *wérsēn* + *yewg-* | *yuktvā́ hárī vṛ́ṣaṇā* (1.177.1d), *áśvāso vṛ́ṣaṇo yujānā́ḥ* (6.29.2d) ~ *ζεύξῃ βόας ἄρσενας* (Il. 20.495) | contested | generic | 27 RV stanzas vs 1 Homer line. vṛ́ṣan- in the RV is a ubiquitous 'bullish' epithet of horses; the Homer line is male oxen in a threshing simile. See below. |
| 95 | *h₁wésus* + *suHnús* | *vásuṃ sūnúṃ sáhasaḥ* (1.127.1b) ~ *υἷος ἑῆος* (Il. 24.422), *υἱὸν ἐῢν* (Il. 8.303) | no (lexeme) | mapping error | υἱός < *suH-yú-* is not sūnú- < *suH-nú-*. ἑῆος is a contested reading of ἐΰς; vásu- ~ ἐΰς is itself disputed. In Il. 6.8, ἠΰν is a predicate epithet of Acamas, not an attributive 'good son'. |
| 106 | *bʰeh₂-* 'speak' + *dyḗws* | *divó duhitáro vibhātī́ḥ* (4.51.1c) ~ *προσέφη νεφεληγερέτα Ζεύς* (Il. 1.511) | no | mapping error | √bhā 'shine' vs φημί 'say' (homograph). |
| 107 | *bʰeh₂-* 'light' + *dyḗws* | same as 106 | no | mapping error | Duplicate of 106. |
| 112 | *ḱewh₁-* + *steh₂-* | *śū́ro ásteva* (6.64.3c) ~ *ἱστίον ἀμφὶ δὲ κῦμα* (Il. 1.481) | no | mapping error | ástar- 'archer' (√as 'throw') is mapped to *steh₂-*. śū́ra- ~ κῦμα is a root-level link only. |
| 118 | *médʰyos* + *peh₂ǵ-* | *mádhye árṇaso dhā́yi pajráḥ* (1.158.3b) ~ *μέσῃ δ' ἐν γαστέρι πῆξε* (Il. 13.372) | doubtful (pajrá-) | chance | 'Set in the middle of the flood' vs 'stuck (the spear) in the middle of the belly'. |
| 121 | *h₁ed-* + *welh₁-* | *áditiṃ vṛṇīmahe* (10.100.1d, refrain ×6) ~ *ἐελδόμενος … ἐδωδῆς* (Od. 14.42) | no | mapping error | áditi- 'boundlessness' (a- + √dā 'bind') is not from *h₁ed-* 'eat'. The RV count is the hymn's refrain, repeated in every stanza. |
| 130 | *sēmi* + *twek-* | *tvácam ásiknīm* (9.73.5d) ~ *τὸ δ' ἥμισυ* (Il. 13.565) | no | mapping error | ásita- 'black' is not *sēmi*. |
| 135 | *dʰers-* + *ménos* | *dhṛṣán mánaḥ* (1.54.3b, 5.35.4c, 8.62.5a) ~ *μένος καὶ θάρσος* (Il. 5.2, Od. 1.321) | yes | known | W ch. 2 treats exactly this pair, with these loci, as formulae with cognates (citing the RV hymn as 1.54.2; the bold-mind pāda is 1.54.3b). It also notes *dhṛṣánmanas-* and Θερσιμένης. |
| 137 | *h₂nḗr* + *weyd-* | *náryāṇi vidvā́n* (4.16.6a) ~ *ἀνέρι εἰσάμενος* (Il. 16.716) | root level | chance | 'Knowing manly deeds' vs 'likening oneself to a man'. |
| 147 | *bʰes-* + *twek-* | *bapsati … tvací* (9.79.4c) ~ *ψυχρή καὶ σακέεσσι* (Od. 14.477) | no | mapping error | ψυχρός again. σάκος ~ tvác- is a speculative etymology. |
| 151 | *skeyd-* + *wí* | *vér ivā́chedi parṇám* (1.116.15a) ~ *σκέδασεν κατὰ νῆας ἐΐσας* (Il. 23.162) | no | mapping error | vér is 'bird' (*h₂éwis*), not *wí*. ἐΐσας is 'balanced', not *wí*. σκεδάννυμι is not *skeyd-*. |
| 152 | *wí* + *skeyd-* | same as 151 | no | mapping error | Duplicate of 151. |
| 157 | *h₂élyos* + *h₁eysh₂-* | *anyám ichasva* (10.10.10d) ~ *ἰητρὸς … ἄλλων* (Il. 11.514) | no | mapping error | √iṣ 'seek' (*h₂eys-*) is not ἰάομαι. 'Other' + anything is generic anyway. |
| 179 | *ménos* + *dʰers-* | same as 135 | yes | known | Duplicate of 135. |
| 181 | *bʰerǵʰ-* + *h₂lek-* | *rákṣā ṇo brahmaṇas pate* (1.18.3c) ~ *πύργων … ἐπάλξεις* (Il. 12.258) | no | mapping error | bráhman- is not from *bʰerǵʰ-*, and the semantics are unrelated. |

## The three flagged candidates

### Plausible new (weak): *peh₃-* + *terp-*, "drink and be sated" (ranks 73 and 72)
**Attestations (whole-corpus search, not only the file's examples).**
- **RV.** Coordinated or juxtaposed in host-to-guest invitations to drink soma:
  - *píbataṃ ca tṛpṇutáṃ ca* (8.35.10a, Aśvins)
  - *píbā … bhāgásya tṛpṇuhi* 'drink … be sated with your share' (2.36.4d)
  - *tṛpát … pāhi* (2.11.15b), *tṛpát piba* (2.36.5d), *píba mádhvas tṛpát* (10.116.1d), *píbā … tṛpád ā́ vṛṣasva* (3.32.2)
  - *píbā vṛṣasva tā́tṛpim* (3.40.2), *pibata … tṛptā́ yāta* (7.38.8), *ví pītíṃ tṛptím aśnuhi* (8.82.6c)

  That is about 10 stanzas: a frozen Vedic collocation, with *tṛpát* 'to satiety' almost adverbial beside *piba*.
- **Homer.** About 4 lines:
  - *πίνοντά τε τερπόμενόν τε* (Od. 1.258)
  - *τέρπεο πῖνέ τε οἶνον* (Od. 15.391)
  - *τάρπημεν / τάρπησαν ἐδητύος ἠδὲ ποτῆτος* (Il. 11.780; Od. 5.201)

**Why inheritance is the best available explanation.**
- **Lexical.** Both verbs are the same cognates: *pi-bʰ-/πίνω* < *peh₃-*, and *tṛp-/τέρπω* < *terp-* 'be sated, enjoy'.
- **Syntactic.** *terp-* governs the genitive of the thing consumed in both languages: *bhāgásya tṛpṇuhi*, *mádhvas … tṛpát* ~ *τάρπημεν … ποτῆτος*.
- **Coordination.** The coordination is the same, the doubled *-kʷe*: *ca … ca* ~ *τε … τε*.
- **Genre.** Both occur in invitations to a guest to drink.
- **Semantic change.** The Greek verb has drifted toward 'delight' and keeps 'have one's fill of' only in this genitive construction. The drink phrase preserves the older sense, as an archaism would.
- **Sources.** Neither West nor Watkins discusses it. The root comparison with the genitive is standard in the etymological dictionaries. I could not check Schmitt 1967 or Durante, so "new" means "not in W/Wk", not "unknown to the field".

**Against.**
- "Drink and be sated" is a natural sequence. Watkins (p. 405, PDF p0422) quotes Hittite Illuyanka "they ate and drank … and were sated" with non-cognate verbs, which shows the narrative pattern arises without shared lexicon.
- Doubled *-kʷe* is common in both corpora.
- Homer has only about 4 hits, and the significance is modest (Homer p ≈ 10⁻³·², RV p ≈ 10⁻¹·⁹ for the file's count).

**What would confirm it.**
- **A third branch** with a *terp-* reflex and a drink verb in the same clause. Avestan is the obvious place to look (*θrap-*, *θrafəδa-* 'satisfied', in the haoma passages; to be checked in Bartholomae). The Latin corpus here lacks the root (*torpeo* is the homograph).
- **Metrical fixity.** In Greek the phrase sits at the end of the line: Od. 1.258 fills the hemistich after the penthemimeral caesura, and 15.391 is line-final. In the RV, 8.35.10a is pāda-initial in a jagatī line. Cross-metre position is weak evidence, but repeated line-final placement in Greek fits a traditional formula.
- **Proposed reconstruction:** *pí-ph₃-e/o- … térp-e/o-* + genitive, 'drink and take your fill of X'.

### Generic: *stérih₂* + *gʷṓws*, "barren cow" (rank 43)
- **Attestations.** RV: *staryàm pipyathur gā́m* (1.116.22d) and *ádhenuṃ … staryàm … gā́m* (1.117.20), both the Aśvins' miracle for Śayu, plus *staryò ná gā́vaḥ* (7.23.4a). 7.68.8 tells the same story with *aghnyā́*. Homer: *στεῖραν βοῦν* (Od. 10.522 = 11.30, one repeated line) and Od. 20.186.
- **Cognation.** Solid.
- **Why not a formula.** *stérih₂* denotes a barren female animal, and in Vedic starī́ is itself a noun 'barren cow'. Any branch that kept both words would produce the phrase independently. The contexts share nothing: a milk miracle in the RV vs a victim for the dead or for a feast in Homer.
- **Latin.** Virgil's *sterilem … vaccam* to Proserpina (Aen. 6.251) imitates the Odyssean Nekyia and cannot count as an independent witness.
- **Use.** Acceptable as a reconstructible lexical collocation for corpus text, not as a poetic formula.

### Generic: *wérsēn* + *yewg-*, "yoke the bulls" (rank 86)
- **Attestations.** 27 RV stanzas pair vṛ́ṣan- with yuj-: mostly *hárī vṛ́ṣaṇā* 'the two bullish bays', and once a 'bullish chariot' (1.157.2a). Homer has the single line *ζεύξῃ βόας ἄρσενας* (Il. 20.495), male oxen threshing in a simile.
- **Cognation.** vṛ́ṣan- ~ ἄρσην is contested. Wiktionary, followed by the lexicon, unifies them as *wérsēn*. Others separate ἄρσην / Av. *aršan-* (*h₁r̥s-en-*) from vṛ́ṣan- / Lat. *verrēs*.
- **Why generic.** Draft teams are male. vṛ́ṣan- is one of the most frequent RV epithets, so the RV count is inflated.
- **A closer Homeric match** would be *τετράοροι ἄρσενες ἵπποι* (Od. 13.81) ~ *áśvāso vṛ́ṣaṇo yujānā́ḥ* (RV 6.29.2d). It uses a different 'yoke' word, and the phrase is still natural.

## Notes for the pipeline
- **Homograph roots are the main error source.** 14 of 32 distinct pairs are mapping errors, chiefly *bʰeh₂-*, *wel-*, *yeh₂-*, ψυχρός, and *wí*/*h₂éwis*.
- **Derivation mismatches pass as matches.** δῖος vs devī́ and υἱός vs sūnú- share a root but are different words. The stem-family idea in the method doc should apply here as well.
- **The "known" claims in the method doc need sources.** For "drink mead" and "yoke horses" they are not supported by West or Watkins.

## Follow-up: Avestan check (main session, 2026-10-23)
The reviewer named Avestan *θrap-* in the haoma texts as the confirming third branch for "drink and be sated". In the CAB corpus (17,177 stanzas, which write ϑ), *ϑrap-/ϑraf-* occurs only in *aēϑrapaiti-* 'priest-teacher' (13 stanzas), never as 'sate' and never next to a drinking or haoma word. **No third-branch support**: the candidate stays weak (two branches, natural sequence, Hittite parallel with non-cognate verbs).
