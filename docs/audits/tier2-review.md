# Tier 2 (back-projection) adversarial review

Reviewer: independent "skeptical Indo-Europeanist" subagent, 2026-10-23.
Scope: all 111 lines in `corpus/tier2/*.jsonl` (9 clusters), read against `docs/generation/tier2-brief.md`, PLAN.md Phase 5 and "Gate for every tier".
Method: each line read in full (PIE, English, tokens with verified/interpolated flags, cognate_refs, notes). 246 of the 327 cited loci are in local corpora, and I checked about 170 of them (list below). Judgments rest on handbook knowledge (Watkins 1995, West 2007, Fortson, Mallory & Adams), and I re-read West and Watkins where a claim turned on what the author actually says.
**Caveat:** this review was **not plant-calibrated**. The PLAN gate asks for `make_review_packet.py` with planted errors and Tier 1 controls, and this was a direct read with full provenance visible. Treat the numbers as one expert pass, not a scored gate.

Verdict scale:
- **sound:** the secure tokens are true cognates standing in a genuinely parallel phrase in ≥2 branches, the PIE morphology is defensible, and interpolation is honestly marked.
- **weak:** the parallel is defensible but overclaimed. Typical causes: secure only at root level, secure set stitched from unrelated loci, interpolated frame larger than the secure core, branch count inflated, or a morphology problem.
- **reject:** not a real parallel (coincidence or a single-branch proposition), the secure claim violates the ≥2-branch rule, or a wrong form or contradiction.

## 1. Counts

| cluster | lines | sound | weak | reject |
|---|---|---|---|---|
| cattle-raid | 8 | 3 | 3 | 2 |
| dawn-sun | 21 | 5 | 16 | 0 |
| death-otherworld | 11 | 1 | 7 | 3 |
| divine-twins | 8 | 1 | 7 | 0 |
| dragon-slaying | 15 | 4 | 7 | 4 |
| fame | 14 | 5 | 9 | 0 |
| healing-charms | 5 | 2 | 3 | 0 |
| poetics-gifts | 15 | 5 | 10 | 0 |
| sky-father | 14 | 5 | 8 | 1 |
| **total** | **111** | **31 (28%)** | **70 (63%)** | **10 (9%)** |

`secure_share` points the wrong way. Of the 12 lines with secure_share = 1.0, only 3 are sound (cattle-001, cattle-002, dragon-001). Three are rejects (cattle-008, death-008, dragon-007) and six are weak. A share of 1.0 usually means root-level matches were counted as exact.

## 2. Per-line verdicts

### fame (14)
| id | verdict | reason |
|---|---|---|
| fame-001 | sound | Kuhn's κλέος ἄφθιτον = śrávas ákṣitam (Il. 9.413, RV 1.9.7, both checked). The verb is honestly interpolated. |
| fame-002 | weak | dʰh₁dʰí is marked verified as "aorist imperative following Ved. dhehi", but dhehi is the reduplicated **present** imperative (*dʰe-dʰh₁-dʰí > *dhazdhi, cf. Av. dazdi). Timocreon τίθει (a present) is used to verify an aorist. h₂yéwi is root-level only (viśvā́yu- compound against αἰϝεί). Same parallel as poetics-012, which uses the correct present form. |
| fame-003 | sound | Watkins' frame: sá dhatte ákṣiti śrávaḥ (RV 1.40.4, checked) and Hdt. κλέος καταθέσθαι. Greek ἄφθιτος is stitched from Il. 9.413, which is acceptable for this frame. |
| fame-004 | weak | The Krisa inscription can't be checked. h₂óyu is root-level only. The predicate *seǵʰ- is Greek-only, so the line rests on a single attestation. |
| fame-005 | sound | máhi śrávaḥ = μέγα κλέος (RV 1.79.4, Il. 6.446, Od. 2.125 all checked). The verb is interpolated. |
| fame-006 | weak | h₁wérHu is verified only through the compound urugāyá- (root-level). The verb is Vedic-only. |
| fame-007 | weak | The core κλέα ἀνδρῶν is fine. But RV 1.43.7 nṛṇā́m depends on śatásya ("of a hundred men"), not on śrávaḥ (misconstrued). The Old Irish cloth neirt is root-level (*ḱlutom, *h₂ner-to-), so branches = 3 is inflated. The verb is interpolated. |
| fame-008 | weak | Good formation match (icchámāna- = Slavic iskati, *h₂is-sḱé-), but ḱléwos rests on slava (a different formation). "Goes forth" stitches éti (pāda b) to prá (pāda c) of RV 10.102.4, which belong to different clauses. 'King' comes from another hymn. |
| fame-009 | weak | Av. vohu sravah- = OIr fó chlú is fine. The frame (optative 'place on me') comes from Y. 62.6, where Avestan has a locative. The verb is interpolated, and the Greek supplies only ḱléwos. |
| fame-010 | weak | The predicate (Greek ἀροίμην) is from one branch. 'Good' comes from Avestan and Old Irish, which belong to other passages. Pastiche of three traditions. |
| fame-011 | weak | ὄνομα κλυτόν against śrútyaṃ nā́ma. Ved. śrútya- is a different derivative (root-level). 'Bears' is Vedic-only. |
| fame-012 | weak | Same pair as fame-011, applied to RV 8.46.14, where nā́ma is adverbial ('by name'). Root-level. Duplicates fame-011. |
| fame-013 | sound | 'Place a name' in four branches: Hitt. lāman dāi- (KUB 24.8 iii 14′, checked), Ved. nā́ma dhā- (RV 5.3.10), Gk ὄνομα θέσθαι (Od. 18.5), Lat. nomen indere (Plaut. Capt. 69, checked). |
| fame-014 | sound | Hitt. ŠUM-an ēšdu = Gk ὄνομ' ἔστω, an exact *h₁éstu (KUB 24.8 iii 11′ and Od. 19.409, both checked). The interpolated tód is not flagged (closed class). |

### dragon-slaying (15)
| id | verdict | reason |
|---|---|---|
| dragon-001 | sound | Watkins' Basic Formula: RV 1.32.1, Y. 9.8, KBo 12.84 kuenta (all checked). The Greek is stitched (ὄφιν from Pindar, κατέπεφνε from the Chimaera passage), but the line stands on Indo-Iranian plus Hittite. |
| dragon-002 | weak | Secure share 0.2. Il. 24.758 ὅν κατέπεφνεν is an object relative ('whom Apollo slew') about Hector, not 'who slew the serpent'. The copular frame is interpolated. |
| dragon-003 | reject | 'The serpent overcame him' is Hittite-only narrative (KBo 3.7 i 11, checked). The Vedic counterpart (ná atārīt) has the opposite subject, the opposite polarity and a different stem. That leaves the root only. |
| dragon-004 | weak | Watkins' *terh₂- variant is defensible. All three branches share only the root (Hitt. tarḫu-, Ved. turv-, Av. tauruuaiia-), and the object is interpolated. |
| dragon-005 | sound | Watkins' Luvian–Vedic imprecation: tatarḫandu, widaindu, annan pātanza duwandu (KUB 9.6+ iii 27′–29′ in the TLH numbering, checked) against RV 1.32.6–8 (atārīt, vadhá-, patsutaḥśī́ḥ with *pedsú). The interpolation is honestly marked. |
| dragon-006 | sound | *gʷʰn̥tós + *ḱey- 'lie slain' (RV 1.32.5, Yt. 10.80 = CAB YtMihr21.3 sōire … jata, Il. 24.757 πρόσφατος κεῖσαι, all checked). Duplicates cattle-002 and death-004 (same refs). |
| dragon-007 | reject | Secure 1.0 rests on Il. 12.208 ὄφιν κείμενον (an eagle drops a live snake as a portent, checked), which is a natural collocation, not a slaying. The *gʷʰen- comes from an unrelated passage (Il. 6.183). The parallel is Indo-Iranian only. |
| dragon-008 | weak | Beowulf 2746–7 nū se wyrm ligeð, swefeð (checked) against RV 1.121.11 (checked). The match is root-level only (svap- causative aorist against OE swefan). ḱéytor is honestly not secure. |
| dragon-009 | weak | Rope: Hitt. išḫiman- = OE sīma is good (KUB 17.5 i 15′–16′, checked). The verb rests on Ved. sinā́ti (Varuṇa's fetters in RV 7.84.2, explicitly arajjúbhiḥ 'without ropes'!) and on OE sǣlan, a denominative (root-level). Genesis B can't be checked. |
| dragon-010 | weak | Watkins ch. 43 'become the bane' is well founded. But Gmc. bana- is an n-stem, not *gʷʰonós (root-level), and Od. 21.24 φόνος is a different noun. The verb is interpolated. |
| dragon-011 | weak | 'Slayer slain' is Celtic-only (one branch). RV 8.84.9 says 'whom none slay, who slays' (checked), which is not the same figure. Il. 18.309 κτανέοντα κατέκτα would have been the real second branch. |
| dragon-012 | sound | 1sg *gʷʰénmi in a charm (AV ghanéna hanmi, OIr gono). Watkins treats these as two performances of one text. Both loci are external. |
| dragon-013 | weak | Secure 0.167: only *gʷʰen- is shared. The 'companion' motif is semantic. |
| dragon-014 | reject | Only the numeral 'three' is shared. 'Head' differs (śīrṣán-, κεφαλή), and 'six-eyed' and the serpent word are Indo-Iranian only. A semantic parallel (three-headed), which the brief says to skip. |
| dragon-015 | reject | The Greek snake of Il. 22.93 has eaten 'evil herbs' (checked), not horses and men. The only link to Y. 9.11's compounds aspō.garəm nərə.garəm (checked) is the root *gʷerh₃-. Coincidence. |

### healing-charms (5)
| id | verdict | reason |
|---|---|---|
| healing-001 | sound | 'Blood to blood' polyptoton with the same heteroclitic: AV ásṛk … asnā́ and Hitt. ešḫar=kan ešḫani ḫandan (KUB 9.4 i 17–18 = TLH KUB 55.20+, checked). The verb is interpolated. |
| healing-002 | weak | Marrow: Ved. n-stem majján- against Gmc. thematic *mazga- (root-level). OHG 'out of the marrow' is not a marrow-to-marrow formula. |
| healing-003 | weak | Watkins' proto-text is a reconstruction by contiguity. OHG and OIr each contribute a single word, and none of the three loci can be checked locally. |
| healing-004 | sound | AV vo hanmi = OIr gono míl, the athematic 1sg (Watkins). The object is honestly reduced. |
| healing-005 | weak | práti tiṣṭha ūrdhváḥ against Pindar ἔστασεν ὀρθούς: the Greek is a transitive s-aorist ('set them upright'), and *h₃r̥dʰwó- against ὀρθός (ϝορθ-) is itself debated. Common words, thematic parallel. |

### divine-twins (8)
| id | verdict | reason |
|---|---|---|
| twins-001 | weak | The note says Lith. Diẽvo continues *dyēws. It doesn't: it is *deywós, and sky-010 itself says so. So the Baltic branch doesn't support diwés, and branches = 3 is inflated. The genuine cognate moy (μοι = Ved. me) is uncredited. Two of four content tokens are interpolated. |
| twins-002 | weak | 'Daughter of the Sun' (sū́raḥ duhitā́ = Lith. Sáulės dukrýtė) is sound. The clause 'chose you two as husbands' is Vedic-only, stitched from RV 1.119.5 onto 7.69.4 (both checked). |
| twins-003 | weak | Same core. The participle and the verb are Vedic or interpolated, and Lith. Diẽvo is *deywós again. |
| twins-004 | sound | Watkins' *h₁ōḱéwes h₁éḱwōs (RV 8.5.7, checked). The Alcaeus compound ὠκύπους is weaker than the Homeric ὠκέας ἵππους, which should replace it. |
| twins-005 | weak | Ved. sváśva- = Gk εὔιππος is a real compound equation, but the line decomposes it, and only 'horse' is secure (0.2). |
| twins-006 | weak | Ved. yúvan- = Lat. iuvenis. The Latin source is Cicero's prose report of an epiphany. Greek contributes Διός only. |
| twins-007 | weak | Only 'ship' is shared. 'Rescuers at sea' is thematic, and the verb and object are Vedic-only. |
| twins-008 | weak | Latin is Cicero (late prose), and 'white' and 'came' are Latin-only or interpolated. |

### cattle-raid (8)
| id | verdict | reason |
|---|---|---|
| cattle-001 | sound | *h₂eǵ- + *gʷṓws: RV 2.12.3 gā́ḥ udā́jat and 8.14.8 (checked), Lat. boves agere (Hercules and Cacus), OIr táin bó. Note that boves agere is also an everyday farming phrase (Cato Agr. 72). |
| cattle-002 | sound | RV 10.108.4 hatā́ḥ … śayadhve and Il. 24.757 (checked). Duplicates dragon-006 and death-004. |
| cattle-003 | sound | Av. azāni (YtASA10.3h = Yt. 5.34, checked) is formally identical to Gk κ' ἄγω (Il. 1.184, checked), *h₂éǵoh₂. The object is honestly interpolated. |
| cattle-004 | weak | Watkins' Geryon/Viśvarūpa myth is real, but only 'three' and 'cows' are secure (0.2). Hesiod and Livy can't be checked. |
| cattle-005 | reject | The only link between Hittite Laws §67 (checked: takku ÁB kuiški tāyezzi … 6 GU₄ pāi) and RV 7.104.10 (a curse naming a thief, stená-) is the root *(s)teh₂-. The sentence is Hittite law. Not a collocation. |
| cattle-006 | weak | 'Cattle and horses' as wealth is a generic pair (Il. 1.154, RV 10.108.7, both checked). The verb, the negation and the possessor are Greek-only. |
| cattle-007 | weak | Ved. sám aryó gā́ḥ ajati (RV 1.33.3, checked) against Gk ἀγέλη, a noun, while the Greek verb is ἐλαύνω. The verb is root-level, and gʰóstis stands in for a non-cognate. |
| cattle-008 | reject | Secure 1.0, but the Greek 'support' is βοῶν (Il. 11.677) plus βίη Ἡρακληείη (11.690, checked), an unrelated line about Heracles sacking Pylos. βίη is a noun. There is no 'win cattle' phrase in Greek. |

### dawn-sun (21)
| id | verdict | reason |
|---|---|---|
| dawn-001 | sound | 'Dawn, daughter of Sky' (RV 1.48.1, checked). The Greek title belongs to other goddesses (acknowledged in the note), and Lith. Diẽvo is *deywós. |
| dawn-002 | weak | Secure 1.0 overclaimed. The Vedic is stitched from two hymns (6.52.4, 6.65.2), the Greek has the compound ἠριγένεια and φάνη (an n-present aorist), and no branch has the participle formation. |
| dawn-003 | weak | Ved. ámartyā (*-t-yo-) is not *n̥mr̥tós. amŕ̥tā comes from another hymn, and Bacchylides can't be checked. Engine: the feminine eh₂-stem VOC ń̥mr̥teh₂ looks like the nominative (expected *-h₂/*-a, cf. Ved. ámbe, Gk -ᾰ). |
| dawn-004 | weak | Both daughters are **middle** (Ved. yukṣvá, Gk ζεύγνυσθ', RV 1.92.15 and Od. 23.244, both checked), but the line has active yugdʰí. That violates the brief's rule to follow the morphology the branches agree on. The Greek is negated narrative. |
| dawn-005 | weak | Il. 11.1–2 and Od. 23.246 (φάος … φέροντας) are good. The Vedic is stitched (jyótir bhárantīḥ from 10.35.5, mártyāya from 6.65.3), mártya- is a different formation, and 'light' is interpolated. |
| dawn-006 | weak | Secure 1.0, but the Greek has only the compound πολυδερκής ('much-seeing', the opposite diathesis). West ch. 5 presents only the root association with Dawn. |
| dawn-007 | weak | Ved. urviyā́ bhāti against the name Εὐρυφάεσσα, a compound standing for Dawn's mother. Root-level. |
| dawn-008 | weak | RV 7.78.3 is good (checked). The Greek is Euryphaessa or Theia bearing Helios: a name compound, and not Dawn. |
| dawn-009 | weak | 'Great sun' is a generic adjective-noun pair (svàr mahát, Ἠέλιόν τε μέγαν). The verb is Vedic. |
| dawn-010 | sound | āśú- = ὠκύς with the sun (AV 13.2.2, Mimnermus). Both loci are external. |
| dawn-011 | weak | spáś- against σκοπός is root-level (a different formation, mislabelled "Kuhn's equation"). h₂n̥rṓm is verified through a Vedic compound in another verse. |
| dawn-012 | weak | Pastiche of RV 7.60.2 (checked) and two Greek texts. Half of the content is interpolated. |
| dawn-013 | weak | The verb and participle are interpolated, and φαείνω is root-level. Overlaps dawn-009 and dawn-012. |
| dawn-014 | sound | The Sun's wheel in three branches: cakrám (RV 2.11.20, checked), κύκλος ἁλίοιο, ON fagrahvél (Alvíssmál 16, checked). |
| dawn-015 | weak | The Vedic is stitched (7.63.2 Etaśa, 1.164.2 a riddle hymn), and West himself doubts PIE date. |
| dawn-016 | sound | The Sun's horses (RV 1.115.3, Y. 16.4 checked; Hymn. Dem.). The interpolated predicate is honestly marked. |
| dawn-017 | weak | West ch. 4 n. 25 (checked) says divó akṣī́ corresponds to Διὸς ὄσσε "etymologically, though not semantically": Il. 14.286 is Zeus' literal eyes. That leaves the Vedic and Macrobius' late report (plus Latvian, not cited). |
| dawn-018 | sound | 'Daughter of the Sun', Vedic and Lithuanian (RV 1.116.17, checked). The predicate is honestly interpolated. |
| dawn-019 | weak | RV 7.36.1 (checked): the Sun releases the cows, which are rays or dawns, not a solar herd. The Od. 12.127 herd is a different image. |
| dawn-020 | weak | 'Live and see the sun' is a real West parallel, but the secure set is stitched: the sun from Il. 18.61, where the verb is ὁράω, and *derḱ- from Il. 1.88, which has no sun. ζάω is a different present formation. |
| dawn-021 | weak | Ved. ájma- (*-mn̥) against ὄγμος (*-mos) is root-level, the subject is interpolated, and the verb is interpolated. |

### death-otherworld (11)
| id | verdict | reason |
|---|---|---|
| death-001 | weak | 'Lower darkness': támas : tenebrae is root-level (different suffixes), and 'lower' is an adverb, not the adjective. Infernus is cited from Aeneid 7, which can't be checked. RV 10.152.4 is a causative (checked). |
| death-002 | weak | Only *ḱwṓ is shared, and the dual comes from Indo-Iranian only (the Greek is singular κύνα). The path-guarding is Indo-Iranian. |
| death-003 | sound | Causative *swop-éye- 'put to sleep = kill' in three branches with the same formation: Ved. svāpaya- (RV 7.19.4, 4.30.21), OE swebban (Beowulf 567, 680), Lat. sōpīre (Lucr. 3.904). All checked. |
| death-004 | weak | The formula is sound (see dragon-006), but branch 3 (OE) supports only the particle nū (ligeð is *legʰ-). Triplicate of dragon-006 and cattle-002. |
| death-005 | weak | Secure 1.0 from root-level matches: κοιμάω is a derivative of *ḱey-, OE has licgan (*legʰ-), and the Vedic has verbs, not *supnós. |
| death-006 | reject | The Greek contributes only νέκταρ, under Thieme's contested *neḱ-tr̥h₂-. The sentence is the AV verse translated. |
| death-007 | weak | Watkins' νέκταρ/ἀμβροσίη against Īśā Up. 14 (late Vedic, external). ἀμβροσίη is a different derivative of the root. |
| death-008 | reject | **Rule violation:** pértum is Avestan-only and péroh₂ is Greek-only, so neither has two branches, yet secure_share is 1.0. The note admits that "neither passage has both words". |
| death-009 | weak | Gk νέκυς against OIr éc (*n̥ḱ-u-, a different grade and stem). 'Go to the dead' is a common idiom, and the verb is interpolated. |
| death-010 | weak | Secure 1.0: φόνον φέρειν (Il. 2.352, 3.6) against ON banorð bera (Fáfnismál 39). All checked. ON bana- is a compound n-stem (root-level), and banorð is a 'death-word'. |
| death-011 | reject | The proposition 'the Twin died first of mortals' is Vedic-only. Y. 9.5 (checked) explicitly says there was no death under Yima, and Ymir isn't mortal. Only the name is shared, and the second branch contradicts the line. |

### poetics-gifts (15)
| id | verdict | reason |
|---|---|---|
| poetics-001 | sound | vácāṃsi … takṣam (RV 6.32.1, checked) against ἐπέων τέκτονες, plus Av. vacas-tašti- (N. 5.2, checked). |
| poetics-002 | weak | The cited Vedic has táṣṭar- (a different agent noun, root-level) and the Avestan a compound. Only Greek has *tétḱōn + 'words'. |
| poetics-003 | sound | Weaving song: Av. ufiiānī (Y. 28.3 Geldner = CAB Y28.5, checked), Gk ὑφαίνω ὕμνον, OE wæf. The object is honestly interpolated. |
| poetics-004 | sound | Ved. prá … etu = Gk ἴτω, an exact *h₁éytu (RV 7.66.1, checked). |
| poetics-005 | weak | πτερόεντα (an adjective from πτερόν) and ποτάομαι against pátanti: root-level, and 'words' interpolated. |
| poetics-006 | weak | Only Germanic continues the perfect (ON man, OE gemunan; Vsp. 1–2 and Beowulf 869–71, checked). Greek μνησαίατο (*mneh₂-) and Ved. manāmahe are other stems. A thematic parallel. |
| poetics-007 | weak | δωτῆρες ἐάων = vohunąm dātārō = dātā́ vásūnām (Od. 8.325, Y. 65.12, RV 8.51.5, all checked) is a real Benfey equation. But all three branches point to *dh₃-tér- / *deh₃-tér- (oxytone δωτήρ, dātā́), while the engine gives root-accented déh₃tores. |
| poetics-008 | weak | Y. 16.1 (checked) reads dātārəm vohunąm dāmanąm, 'creator of good creatures': vohunąm agrees with dāmanąm, and dātar- 'creator' is likely *dʰeh₁-. Od. 8.335 δῶτορ ἑάων and RV 8.51.5 still stand. The verb is Indo-Iranian. |
| poetics-009 | weak | Watkins' 'inverse dānastuti' is real, but the 'give' verb and 'songs' are interpolated. ḱlḗm (1sg root aorist with Stang's law *-ewm̥ > *-ēm) is questionable: Ved. áśravam and the OIr perfect don't support it. |
| poetics-010 | weak | Only 'horse' is shared (gíre against ar dúana are not cognate). Thematic. |
| poetics-011 | weak | A Vedic sentence (RV 5.18.5, checked) with Greek μέγα κλέος (Il. 6.446, Hector's father's fame) bolted on. Secure 0.25. |
| poetics-012 | sound | κλέος ἄφθιτον = śrávaḥ ákṣitam with the correct present imperative dʰedʰh₁dʰí. Duplicates fame-002, and contradicts fame-002's aorist on the same Vedic word. |
| poetics-013 | sound | *h₁wésu ḱléwos: Av. vaŋhāu srauuahī (Y. 30.10, checked) = OIr fó chlú. The wish frame is honestly interpolated. |
| poetics-014 | weak | Only misdʰós is shared (Y. 44.18, checked, against Pindar). Everything else is Avestan, and secure is 0.2. |
| poetics-015 | weak | κλῦθί μευ = śrudhī́ is exact (Il. 1.37, RV 1.25.19, checked), but the enclitic is accusative *me where both branches have a gen./dat. enclitic (μευ; me < *moy). Hljóðs (Vsp. 1) is root-level, so the third branch is inflated. |

### sky-father (14)
| id | verdict | reason |
|---|---|---|
| sky-001 | weak | *dyéw ph₂ter is sound (RV 6.51.5, Il. 3.276, Cato, all checked). 'Broad One' rests on OE Folde, a different formation (*pl̥th₂-eh₂-?), so it is root-level. Two engine issues: pl̥th₂éwih₂ has the Greek-type *-ew-ih₂ where Ved. pṛthivī́ requires *pl̥th₂wih₂, and the VOC keeps -ih₂ (Ved. pṛ́thivi has short -i). |
| sky-002 | weak | Same Folde issue. Varro's Tellus mater is not cognate. RV 1.89.4 and 1.164.33 (checked) carry the line, so the extra branches are inflated. |
| sky-003 | sound | mahé pitré divé (RV 1.71.5, checked) = Ζεῦ πάτερ … μέγιστε (Il. 3.276, checked). |
| sky-004 | weak | Διὸς ὄμβρος (Il. 5.91, checked) is real. But in RV 5.84.3 (checked) diváḥ goes with vṛṣṭáyaḥ (divó vṛṣṭí, the actual equation), not with abhrásya, so 'rain-clouds of Sky' is a misconstrual. |
| sky-005 | reject | West ch. 4 n. 25: "etymologically, though not semantically". Il. 14.286 is Zeus' literal eyes. A Vedic sentence with a coincidental Greek phrase. |
| sky-006 | sound | 'Hold heaven and earth' with *nébʰos + *dʰéǵʰōm: Hitt. nepiš tekan (KUB 8.41 ii 6′, checked) and Av. ząmcā … nabā̊scā (Y. 44.4, checked). The verb is honestly interpolated. The English says 'clouds' where both daughters mean 'sky': the gloss follows the lexicon, not the parallel. |
| sky-007 | weak | Root-level throughout (sádman- against ἕδος against εὐρυεδής), a pastiche of four loci. |
| sky-008 | sound | εὐρεῖα χθών = kṣā́m urvī́m (Il. 11.741, RV 6.17.7, both checked). The verb comes from Y. 38.1 (checked) and is honestly interpolated. |
| sky-009 | weak | Star-adorned heaven: the Avestan is a compound (stəhrpaēsah-), the Vedic a verb (piś-) and the Greek ποίκιλμα. Root-level. |
| sky-010 | weak | Only diwés is secure. Near-duplicate of twins-001. |
| sky-011 | sound | dyaúḥ pitā́ janitā́ (RV 1.164.33, 4.1.10, checked) = Iupiter … diuum genitor (Catull. 64.26–27, checked). Possible Hellenistic calque in Catullus, but the Vedic alone matches closely. |
| sky-012 | weak | Ζεύς με πατὴρ προέηκε (Il. 11.201, checked) is real. In Plaut. Amph. 19–20 (checked), 'Iouis' belongs to 'Iouis iussu' and 'pater … meus' to a separate clause, so the Latin doesn't attest *dyēws ph₂tḗr and is only a situational parallel. The k-aorist *Hyeh₁k- is a Greek/Italic formation. |
| sky-013 | weak | Branches = 4 is inflated: Cato contributes only Iupiter + precor (134.2, not 134.3, praying to Janus and Jupiter, not Earth), Δημήτηρ is not Earth-as-*pl̥th₂wih₂, and Folde is root-level. |
| sky-014 | sound | diwés dʰugh₂tḗr (RV 10.39.12, checked; Od. 4.227, checked). The verb is honestly interpolated. |

## 3. Systematic problems and fixes

### P1. `secure` is self-declared and never verified (builder)
`scripts/build_tier2.py` sets `verified = lex_id in plan.secure and validator tier == exact`. Nothing checks that the cited lemmas in ≥2 branches map to that lexeme, or that they are the same formation. As a result, root-level matches are marked verified: fame-002/004 (h₂yéwi), fame-008, fame-011/012, dawn-002, dawn-005, dawn-011, death-005, death-010, poetics-002, poetics-005, sky-007, sky-009, cattle-007, cattle-008, dragon-009, dragon-010. Single-branch lexemes are also marked secure (death-008: secure_share 1.0 with each lexeme in one branch only).
**Fix (builder):**
- (a) For each secure lex_id, require ≥2 branches whose `lemmas` match the lexeme's `reflexes` (or a reviewed reflex table). Reject otherwise.
- (b) Add a per-lemma `match: exact | formation | root` to cognate_refs. Compute `secure_share` from exact/formation matches only, and report `root_share` separately.
- (c) Count `branches` only over refs that support at least one secure token. Today a ref that contributes just a particle (death-004 OE nū), a non-cognate (twins-001 Lith. *deywós) or a single god-name (sky-013 Cato) still adds a branch.

### P2. Support-locus stitching (brief + builder)
The brief says the cognates must "stand in the cited passages". In practice, a word from an unrelated passage in the same language is appended to make up the second branch: dragon-007 (Il. 6.183 + Il. 12.208), cattle-008 (Il. 11.690), dawn-005/-020, dragon-001/-013, fame-003.
**Fix:** give each cognate_ref a `role: parallel | support`. Only `parallel` refs (one passage per branch containing the collocation) count toward secure and branches. `support` refs document reflexes only.

### P3. The interpolated frame outweighs the secure core (brief)
33 of 111 lines have secure_share < 0.5. Many take a whole sentence from one branch (usually Vedic) and keep only a noun phrase as the parallel (poetics-011, poetics-014, dragon-002, dragon-013, twins-002/003/005/007, cattle-004). These are translations of a Vedic verse with a cognate NP, not reconstructions of a common ancestor.
**Fix (brief):** the head of the collocation (the verb in a verb-object formula, or the noun plus its modifier in an NP formula) must be secure. When the frame isn't shared, emit only the shared NP or formula as the record and put the sentence frame in `alt_reconstructions` or the notes.

### P4. Closed-class tokens are neither verified nor interpolated (builder)
72 closed-class tokens in 50 lines are exempt. Interpolated pronouns and particles are invisible (fame-014 tód, dragon-005 tóm ×3, many nu, ne, -kʷe, moy, nos). At the same time, real closed-class cognates go uncredited: twins-001 moy = μοι = Ved. me; dragon-002 *yo- = yá- = ὅς; fame-007 and death-004 nu = νῦν = nū.
**Fix:** treat closed-class lex_ids like any other: verified when listed in secure with ≥2-branch support, interpolated otherwise.

### P5. Generic or coincidental collocations (brief)
Several lines rest on common words that co-occur anywhere: horse (poetics-010), cattle and horses (cattle-006), great + sun (dawn-009), the numeral three (dragon-014), dog (death-002), Zeus' eyes (sky-005, flagged by West himself).
**Fix (brief):** a secure set made only of high-frequency items (numerals, 'great', 'horse', 'cow', 'dog', pronouns) needs either a specific shared formation or a scholar's explicit claim of inheritance, quoted, including the scholar's own caveats.

### P6. Morphology errors and inconsistencies (engine, lexicon, notes)
- **Ved. dhehi** is the reduplicated present imperative (*dʰe-dʰh₁-dʰí > *dhazdhi; Av. dazdi). fame-002/005/006 render it as the root aorist dʰh₁dʰí and call it the aorist, while poetics-012 uses dʰedʰh₁dʰí for the same Vedic word. Pick the present.
- **Voice:** dawn-004 has an active imperative where both branches are middle.
- **Feminine vocatives:** ń̥mr̥teh₂ (dawn-003) and pĺ̥th₂ewih₂ (sky-001) look like nominatives. Check the engine's VOC for eh₂- and ih₂-stems (expected *-h₂/*-a and *-i).
- **pl̥th₂éwih₂:** Ved. pṛthivī́ points to *pl̥th₂wih₂. The *-ew-ih₂ type is Greek εὐρεῖα. Store both, and use *pl̥th₂wih₂ for the Vedic-based Earth name.
- **Agent nouns:** déh₃tor- (root accent) where Gk δωτήρ and Ved. dātā́ (+gen.) agree on *-tér- (poetics-007).
- **ḱlḗm** (poetics-009): check whether the engine applies Stang's law to verbal 1sg *-ewm̥. No daughter supports it.
- **Enclitic case** with 'hear': both branches have a gen./dat. enclitic, but the line has acc. *me (poetics-015).
- **Notes contradicting each other:** Lith. Diẽvo is called *dyēws in the twins-001 note (and treated as diwés support in dawn-001 through the verified flag and branches = 3), but *deywós in sky-010 and sky-014.

### P7. Misconstrued source passages (individual lines)
- RV 1.43.7: nṛṇā́m goes with śatásya (fame-007).
- RV 5.84.3: diváḥ goes with vṛṣṭáyaḥ (sky-004).
- RV 10.102.4: éti and prá are in different pādas (fame-008).
- Y. 16.1: vohunąm agrees with dāmanąm (poetics-008).
- Plaut. Amph. 19–20: Iouis and pater are not a phrase (sky-012).
- Il. 24.758: ὅν is an object relative (dragon-002).
- RV 8.84.9: not 'slayer slain' (dragon-011).
- RV 7.36.1: the cows are rays (dawn-019).
- Y. 9.5: denies death under Yima (death-011).
- Cato's precor is at Agr. 134.2, not 134.3 (sky-013).

### P8. Duplication (matters for eval)
Near-identical parallel sets:
- dragon-006, cattle-002 and death-004 (the same three refs)
- fame-002 and poetics-012
- fame-009, fame-010 and poetics-013
- fame-011 and fame-012
- twins-001 and sky-010
- dawn-017 and sky-005
- dragon-012 and healing-004
- dragon-003 and dragon-004
- dawn-009, dawn-012 and dawn-013
- death-006 and death-007
- dragon-008 and death-005

A held-out Tier 2 slice drawn at random would leak its parallel into training. **Fix:** key each record by its parallel set (the sorted list of branch:locus pairs plus the secure lex_ids). Dedup, or at least split train and eval by that key.

### P9. Opportunity noted
KUB 9.4 i 16 (= TLH KUB 55.20+, checked) also has ḫaštai=kan ḫaštai ḫandan, 'bone to bone', with Hitt. ḫaštai < *h₂ost-. That would give a secure two-branch *h₂ost- polyptoton against AV 4.12 (verify the AV pāda), stronger than healing-002.

## 4. Loci checked locally

All checked loci contain the cited words. No fabricated attestations were found. The problems are in interpretation (sections 2 and P7), not in attestation.

- **Rigveda (vedaweb Lubotsky/VNH), about 80 verses**, all found with the cited words:
  - 1.4.8, 1.9.7, 1.25.4, 1.25.19, 1.32.1, 1.32.5, 1.32.12, 1.33.3, 1.40.4, 1.43.7*, 1.48.1, 1.67.5, 1.68.10, 1.71.5, 1.72.10, 1.79.4, 1.92.9, 1.92.15, 1.109.2, 1.113.13
  - 1.115.3, 1.116.3, 1.116.17, 1.117.12, 1.117.14, 1.119.5, 1.121.11, 1.126.1, 1.164.2, 1.164.33, 1.185.6, 2.11.20, 2.12.3, 2.12.11
  - 3.2.7, 3.38.1, 3.54.2, 3.61.2, 4.1.10, 4.13.3, 4.30.21, 4.53.4, 5.3.10, 5.13.2, 5.18.5, 5.30.5, 5.84.3*
  - 6.17.7, 6.20.2, 6.32.1, 6.51.5, 6.52.4, 6.63.10, 6.64.2, 6.65.2, 6.65.3, 6.65.6
  - 7.19.4, 7.36.1*, 7.60.2, 7.63.2, 7.66.1, 7.68.1, 7.69.4, 7.77.3, 7.78.3, 7.84.2, 7.104.10
  - 8.5.7, 8.46.14, 8.51.5, 8.84.9*, 10.8.8–9, 10.13.4, 10.14.11, 10.35.5, 10.39.12, 10.57.4, 10.61.4, 10.85.14, 10.99.6, 10.102.4*, 10.108.4, 10.108.7, 10.121.6, 10.152.4

  (* = construal problem, see P7.)
- **Homer (AGDT treebank), 47 lines**, all found:
  - Iliad: 1.37, 1.88, 1.154, 1.184, 1.477, 2.134, 2.352, 2.492, 3.6, 3.276, 5.3, 5.91, 5.348, 6.183, 6.446, 8.368, 9.413, 9.524, 11.1, 11.38, 11.201, 11.241, 11.677, 11.690*, 11.741, 12.208*, 14.286*, 15.251, 18.20, 18.61, 18.121, 22.93*, 23.71, 24.757–8*
  - Odyssey: 1.344, 2.125, 3.1, 3.83, 4.227, 8.325, 8.335, 9.151, 9.364, 12.127, 14.502, 18.5, 19.183, 19.409, 23.244
- **Avesta (CAB, mapped through `corresp` to Geldner numbering):**
  - Yasna: Y. 9.4, 9.5, 9.8, 9.11, 16.1*, 16.4, 28.3 (= CAB Y28.5), 30.10, 38.1, 44.4, 44.18, 46.10, 62.6, 65.12
  - Yašts: Yt. 5.34 (= YtASA10.3), Yt. 10.80 (= YtMihr21.3), Yt. 13.2–3 (= YtFra2.3), Yt. 13.38 (= YtFra10.2)
  - Other: Vd. 13.9, Vd. 19.30, N. 5.2

  All found.
- **Poetic Edda (FJ 1926):** Vǫluspá 1–3, Alvíssmál 16, Grípisspá 11, Fáfnismál 39. All found.
- **Beowulf (Harrison–Sharp):** 567, 587, 680, 869–871, 2746–2747. All found.
- **Hittite/Luwian (TLHdig):**
  - Illuyanka: KUB 17.5 i 15′–18′, KUB 17.6 i 10′–13′, KBo 3.7 i 11 and iii 25′, KBo 12.84 1′–2′
  - KUB 24.8 iii 11′ and iii 14′ (Appu)
  - KUB 8.41 ii 6′ and ii 12′
  - KUB 9.4 i 16–18 (in the TLH join KUB 55.20+)
  - Laws §67 (KBo 22.62+ iii 51)
  - KUB 9.6+ iii 27′–29′ (Luwian, cited as iii 19ff.)

  All found.
- **Latin (LASLA):** Lucr. 1.115, 1.250–251, 3.628, 3.904; Catull. 3.13–14, 64.26–27; Cato Agr. 72, 134.2–3*; Plaut. Amph. 19–20*, Capt. 69. All found.
- **West and Watkins** (for authors' claims): West ch. 4 n. 25 (Divó akṣī́ : Διὸς ὄσσε "not semantically"), West ch. 10 (Timocreon κλέος … τίθει), West ch. 5 (πολυδερκής, Th. 451), Watkins p. 391 (nectar, AV 4.35.1).
- **Not locally checkable:** 81 of 327 refs (25%). The main sources:
  - Greek: Pindar, Hesiod, Hymn. Hom., Alcaeus, Bacchylides, Euripides, Krisa, Timocreon, Ibycus, Simonides, Mimnermus, Herodotus
  - Indic outside the RV: AV, VS
  - Other Latin: Vergil, Livy, Cicero, Varro, Macrobius
  - Baltic dainos, Rhesa, Brodowski
  - Celtic: all Old Irish and Welsh (I didn't search oldirish-ud, which is a gloss treebank)
  - Germanic: OHG charms, Genesis B, Æcerbot, Elene
  - Slavic: Slovo o polku Igoreve

  25 lines have fewer than 2 locally checkable refs. Five have none: dawn-010, dragon-012, healing-003, healing-004, healing-005.

## 5. Can Tier 2 be used as evaluation data?

**Not as is.** With 9% rejects and 63% weak (sections 1–2), the flags overstate certainty, and `secure_share` is not a trustworthy metric until P1 lands (it is inversely informative at 1.0). The PIE line often reconstructs one branch's sentence rather than the common ancestor (P3). And the duplication (P8) would leak held-out parallels into training.

**A filtered subset is usable.** The 31 sound lines, deduplicated by parallel set (about 25 distinct parallels), can serve now as a small "reconstruct the formula" eval set, provided:
1. The secure tokens are recomputed on exact or formation matches in `parallel` loci only (P1, P2).
2. The eval task scores only the secure core (the formula), not the interpolated frame.
3. The dhehi present/aorist and the feminine-vocative engine issues (P6) are resolved first, because they touch sound lines (fame-005).

The weak lines can go to training with their flags corrected, or be rewritten down to their shared NP or formula. The 10 rejects should be dropped or rebuilt: dragon-003, dragon-007, dragon-014, dragon-015, cattle-005, cattle-008, death-006, death-008, death-011, sky-005.

Before Tier 2 is marked done, rerun the gate as PLAN specifies: `make_review_packet.py` with planted errors on the repaired set, plus a blind back-translation. This review was not calibrated.
