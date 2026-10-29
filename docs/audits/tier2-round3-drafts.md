# Tier 2 round 3 drafts: back-projections from the formula witness scan (2026-10-28)

Source list: the 27 pair specs "not yet in Tier 2" in `docs/research/formula-witness-scan.md`
(`data/research/formulas/witness-scan.jsonl`). Each candidate was re-checked in the local corpora:
RV in VedaWeb TEI, AV in DCS, Homer in AGDT, other Greek in GLAUx, Avestan in CAB, Old Irish in
CELT XML, Old Norse in FJ 1926, Old English in the Gutenberg Beowulf, and Latin through the search
index unit text. Daughter text is given as locus plus the parallel words only.

**Review status: pending.** None of the 14 new lines has an entry in `data/tier2/review_verdicts.json`,
so the builder writes `"review": null` and `"eval_grade": false` for them. They get a verdict only
when the next adversarial round adds one, bound to the plan's sha. Every new plan's `notes` also
begins "Round 3 draft … not yet reviewed".

Result: **14 lines accepted, from 13 of the 27 specs** (horse+men gave two, cloud+clothe gave two).
14 specs were declined. The target of 30–50 lines was not reached. The scan's list does not hold
more lines with real two-branch wording, and padding would mean citing generic, renewed or
root-only material.

## Accepted

"Exact" and "root" are the builder's `secure_checks` levels, so cross-check them against the notes.
Where the builder is wrong (mapping errors), the line's notes say so.

| line | candidate | PIE (engine) | confirmed parallel loci | secure lexemes (builder level) |
|---|---|---|---|---|
| epic-diction-005 | horse+men (*h₂nḗr) | h₁éḱwōs h₂néres-kʷe | Il. 23.242 ἵπποι … ἄνδρες; Il. 10.338 ἵππων … ἀνδρῶν; RV 10.68.12cd áśvaiḥ … nŕ̥bhiḥ | h₁éḱwos exact Gk+II; h₂nḗr exact Gk+II |
| epic-diction-006 | horse+men (*wiHrós) | wiHrṓm h₁éḱwōm-kʷe (gen.) | Síaburcharpat Con Culainn (CELT G301008 p. 49 l. 19; = LU 9246) anála fer ⁊ ech; RV 9.96.11d vīrébhir áśvaiḥ; AVŚ 12.1.25 aśveṣu vīreṣu; Yt. 15 (CAB YtWay12.12a) aspaēšu vīraēšu | wiHrós exact Ce+II; h₁éḱwos exact Ce+II. Greek renewed *wiHrós by ἀνήρ (Il. 20.157, support) |
| epic-diction-007 | strong+mind | ish₁róm ménos | Od. 7.167, Od. 8.2, Hymn. Hom. 3.371 ἱερὸν μένος; RV 8.48.7a iṣiréṇa mánasā | ish₁rós, ménos exact Gk+II |
| epic-diction-008 | good+mind | h₁wésu ménos | Il. 17.456, Il. 24.442 μένος ἠΰ; Y. 34.8c vohū … manō; Y. 48.12b vohū manaŋhā | h₁wésus, ménos exact Gk+II (caveat: Vohu Manah is also a divine name) |
| epic-diction-009 | bold+mind | dʰr̥snuwónt ménos | Il. 17.156, Il. 19.37 μένος πολυθαρσές; RV 1.54.3b, 5.35.4c dhr̥ṣán mánaḥ | ménos exact Gk+II; the *dʰers- modifier is root-level in both (engine formation interpolated) |
| epic-diction-010 | cloud+clothe (aorist) | nebʰelom wésn̥to | Il. 14.350, Il. 20.150 νεφέλην ἕσσαντο; RV 5.63.6c abhrā́ vasata; RV 5.85.4c abhréṇa vasata | wḗs- and nebʰelos exact Gk, root II |
| epic-diction-011 | cloud+clothe (participle) | nébʰos wésm̥h₁nos só | RV 9.83.5b nábho vásānaḥ; Il. 15.308 εἱμένος … νεφέλην | nébʰos exact II (Greek νεφέλη is root-level; the builder's Greek "exact" is a mapping error); wéstor root in both |
| epic-diction-012 | wish+self | uḱónts só uḱn̥tbʰís tṓys h₁ḗdtu | RV 10.15.8d uśánn uśádbhiḥ; RV 1.71.1a uśatī́r uśántam; Aesch. PV 218 ἑκόνθ’ ἑκόντι; Eur. Cycl. 258 ἑκὼν ἑκοῦσι | weḱ- participle: exact Gk, root II (ablaut differs); the verb 'eat' is Vedic only |
| epic-diction-013 | god+mortal | deywṓs mr̥tṓs-kʷe | RV 1.100.15a devā́ḥ … mártāḥ; Il. 24.533, Il. 15.99 θεοῖσι … βροτοῖσιν; Y. 29.4b daēuuāišcā maṣ̌iiāišcā | mr̥tós exact Gk+II; deywós II only (Greek renewed it with θεός) |
| bp-ii-ita-004 | race+god | deywṓm ǵénh₁os | RV 6.51.2b, RV 1.70.6b devā́nāṃ jánma; Catull. 64.23 deum genus; Lucr. 5.1156 divom genus | deywós exact II+It; ǵénh₁os exact It, root II (jánman-) |
| dawn-sun-022 | dawn+immortal | n̥mr̥téh₂ h₂éwsōs | Bacchyl. 17.42 ἀμβρότου … Ἀοῦς; RV 1.113.13a,d uṣā́ḥ … amŕ̥tā | n̥mr̥tós, h₂éwsōs exact Gk+II |
| healing-charms-007 | upright+stand | h₃r̥dʰwós sth₂dʰí | AVŚ 4.12.6 tiṣṭha ūrdhváḥ; Pind. Pyth. 3.53 ἔστασεν ὀρθούς | h₃r̥dʰwós exact Gk, root II (mapping gap); *steh₂- root-level in both |
| death-otherworld-012 | deathn+be | tód toy gʷʰónos h₁ésti | Hávamál 72 (FJ) es … bani; Il. 16.144 φόνον ἔμμεναι; Od. 11.444 φόνος ἔσσεται | gʷʰónos exact Gk, root Gm (bani); h₁ésti exact Gm, root Gk |
| dragon-slaying-016 | slay+pay | gʷʰénoh₂ h₁ím kʷoynéh₂h₁ | Yt. 15 (CAB YtWay8.3d–f) kaēna … janāni; Il. 9.632–633 φονῆος ποινήν | kʷoynéh₂ exact Gk+II; gʷʰen- root in both (the verb itself is attested only in Avestan) |

Expected weak points for the reviewer:
- epic-diction-009 and -012, healing-charms-007 and dragon-slaying-016 have a head that is only
  root-level in one or both branches.
- epic-diction-010 and -011 each share the verb only at root level.
- epic-diction-005 and -006 are open to the generic objection that "horses and men" is a natural
  pair in any war narrative.

## Declined

| candidate | reason |
|---|---|
| race+mankind (OE manna cynn ~ Ved. mā́nuṣa- jána-) | Lexicon gap: the only *mon-/manu- 'man' lexeme (pie-lex-mon) is not usable. Both slots would be root-level anyway: cynn and jána- are different formations, and mā́nuṣa- is a derivative. |
| swift+fly (ὠκυπέτης ἴρηξ Hes. Op. 212 ~ śyenáḥ āśupátvā RV 4.26.4b) | A real parallel, but it is a compound with a verbal second member (-pétēs / -pátvan-), which the engine cannot build. The phrasal witnesses (ὤκιστος πετεηνῶν Il. 15.238 'swiftest of birds'; āśúbhiḥ pátasi RV 2.16.3d 'you fly with swift [steeds]') are not the same phrase. |
| upright+stand, posture variant (ὀρθὸς στῆ Il. 23.271 ~ ūrdhvás tasthau RV 1.164.10b) | Generic posture collocation. The healing variant is accepted (healing-charms-007). |
| white+clothe (ἑανῷ ἀργῆτι Il. 3.419 ~ árjunā vástrāṇi RV 3.39.2c) | Both slots are cognate only at root level (ἀργής ~ árjuna-; ἑανός ~ vástra-), so no shared word stands. West's third element (φαεινός ~ bhadrá-) is not cognate. |
| skygod+cloud (Διὸς … νεφελάων Il. 2.146 ~ dyaúr … nábhobhiḥ RV 2.4.6d) | Different construction: a genitive of source against Agni compared to Sky. The cloud words are root-level (νεφέλη ~ nábhas-). West's real parallel, Latvian Dieva debesīm, is not reachable in the local dainas. |
| skygod+rain (Διὸς ὄμβρος ~ divó vr̥ṣṭí-) | The rain words are not cognate. The cognate abhrá- (= ὄμβρος) stands in RV 5.84.3 but depends on vidyútaḥ, not on divó, so it is not one phrase. |
| slay+pay, Celtic witness (OIr guin ~ cin) | Etymology of cin < *kʷei- is disputed. The candidate is accepted on a new Avestan witness instead (dragon-slaying-016). |
| star+adorn (ἀστέρων ποικίλματα Eur. Hel. 1096; stəhrpaēsah- Yt. 10; pipéśa … stŕ̥bhiḥ RV 1.68.10b) | A good three-branch root parallel, and West gives it as root-level only. The head *peyḱ- has three different formations (noun ποίκιλμα, s-stem in an Avestan compound, Vedic perfect). The builder finds the head in no branch at the needed level (Greek ποίκιλμα is unmapped), so the head is not secure. *h₂stḗr is exact in Gk+II. |
| wolf+grey (πολιοῖο λύκοιο Il. 10.334 ~ Lith. vilkas pilkas) | Lexicon gap: no usable *pelH- adjective (pl̥Hkós, polHwos and polHnós are noun-family, and MOD rejects them). The head λύκος = vilkas would be exact. Worth adding an adjective and retrying. |
| immortal+eat (ἀμβρόσιον εἶδαρ ~ MBh amṛtam annam) | The only Indo-Iranian witness is epic Sanskrit. No RV or AV *n̥mr̥tó- + *h₁ed- collocation exists (AVŚ 8.7.12 amṛ́tasya bhakṣáḥ uses bhakṣá-). |
| immortal+word (ἀμβροσίων ἐπέων Pind. P. 4.299 ~ MBh 12.279) | The Indo-Iranian witness is late. RV 3.34.2b vā́cam amŕ̥tāya is 'speech for the immortal', not 'immortal speech'. |
| mortal+self (márto mártam RV 1.147.5b ~ βροτοὶ βροτούς) | No archaic or classical Greek βροτός–βροτός polyptoton in GLAUx; Theocritus is Hellenistic. Hes. Scut. 6 θνηταὶ θνητοῖς is not cognate. |
| see+self (seen and unseen) | The verbs are not cognate (dr̥ṣṭa- ~ uisus ~ Umbr. uirseto). |
| skygod+door (dvā́rau diváḥ RV 1.48.15 ~ ἐν Διὸς θύραισιν Ar. Pax 179) | The head is root-level (θύρα *dʰur-eh₂ against dvā́r-), and the Greek is a literal house door in comedy. West says there is no lexically equivalent phrase in Greek. |
| earth+navel (nā́bhā pr̥thivyā́ḥ ~ χθονὸς ὀμφαλός) | The earth word is renewed, the navel words are different formations (root-level), and West himself suspects diffusion. |
| skygod+eye (Διὸς ὄσσε ~ devā́nām … ánīkam) | Two different images. 'Eye of Sky' is already dawn-sun-017. |
| sun+rota (solis rota ~ sū́ryasya rátha-) | Different formations and meanings ('wheel' against 'chariot'), and *roth₂ós is blocklisted. The wheel of the Sun is already in dawn-sun-014/015. |
| immortal+mortal, ageless+immortal, god+human | Single-branch in the scan. Rechecking found nothing new. |

## Mapping and annotation errors found

- **DCS sentence index cited as stanza.** The scan's "AVŚ, 3, 16.s6" is stanza 3 (= RV 7.41.3), and
  "AVŚ, 12, 1.s53" is stanza 25. The `.sN` suffix is the DCS sentence index, not `sent_counter`.
  DCS AVŚ 4.12 has no stanza counters.
- **RV 7.75.3b misconstrued.** uṣásaḥ is genitive singular, and amŕ̥tāsaḥ (masculine plural) agrees
  with bhānávaḥ, so this is not 'immortal Dawns'.
- **GLAUx lemma Ἀοῦς → Ἀών** (Bacchyl. 17.42) should be Ἀώς/Ἠώς. This is why the scan found no
  classical ἄμβροτος Ἠώς.
- **VedaWeb RV 1.113.13a** merges uṣā́ḥ (sandhi puróṣā́ḥ) into the token purā́.
- **Builder/mapping: Greek νεφέλη → *nébʰos "exact".** It belongs to *nebʰelos (root-level for
  *nébʰos).
- **Builder/mapping: Avestan maṣ̌iia- → *mr̥tós "exact".** It is *mr̥tyo- (= Ved. mártya-).
- **Builder/mapping: Vedic lemma dhr̥ṣ- → *dʰr̥snéwti "exact".** The nasal present is reached
  through the root.
- **Builder/mapping gaps.**
  - Vedic vas- 'wear' is not linked to *wéstor (the participle vásāna- is root-level only).
  - AV ūrdhva- is not linked to *h₃r̥dʰwós.
  - Greek ποίκιλμα is unmapped.
  - Greek εἰμί (ἔμμεναι, ἔσσεται) reaches *h₁ésti only at root level (death-otherworld-012).
- **How the Latin loci were checked.** The Latin loci (Catull. 64.23, Lucr. 5.1156) were read from
  the search index unit text, which comes from the local Perseus Latin corpus. The source files
  themselves were not opened.
  - Avestan kaēnā- was never found by the scan; Yt. 15 (CAB YtWay8.3d) has it beside jan-.
- **Scan coverage.** The Avestan horses-and-men pair aspaēšu vīraēšu (CAB YtWay12.12a,
  YtMihr26.4f) was not reported.
- **CELT keys.** The scan's G301008 and G301900 hits are the same text (Síaburcharpat Con Culainn,
  also preserved in Lebor na hUidre), so they are one witness. G302011 (Fingal Rónáin) is a
  three-member list.

## Build

Run with `uv run python -I scripts/build_tier2.py data/tier2/plans/<cluster>.jsonl` for
epic-diction, bp-ii-ita, dawn-sun, healing-charms, death-otherworld and dragon-slaying. All 14 new
lines realize, and every one validates (`pass`). There are 0 new rejects: every reject listed is a
pre-existing line that the review already rejected.

| cluster | lines | rejected | mean secure_share | eval_grade |
|---|---|---|---|---|
| epic-diction (+9) | 13 | 0 | 0.603 | 2 |
| bp-ii-ita (+1) | 4 | 0 | 0.542 | 1 |
| dawn-sun (+1) | 16 | 6 | 0.500 | 5 |
| healing-charms (+1) | 5 | 2 | 0.383 | 3 |
| death-otherworld (+1) | 6 | 6 | 0.139 | 1 |
| dragon-slaying (+1) | 11 | 5 | 0.228 | 5 |

The secure_share of the new lines is 0 for epic-diction-010, -012, healing-charms-007 and
death-otherworld-012: every shared lexeme there is exact in one branch only. Their real evidence
level is in the notes.

**Rebuild drift in existing lines.** A plain rebuild of the current tree changes some existing records:
- dawn-sun-009: secure_share 0 → 0.5.
- dawn-sun-016: secure_share 0.25 → 0.5.
- death-otherworld-004: secure_share 0.5 → 0, and eval_grade true → false, because πρόσφατος now
  reaches *gʷʰn̥tós only at root level.
- dragon-slaying-006: secure_share 0.667 → 0.333.
- sky-father-011: secure_share 0.667 → 1.0.

To keep this batch from silently changing reviewed lines, the existing records in the six rebuilt
files were restored to their pre-build versions, and only the 14 new records come from the new
build. sky-father was rebuilt only for the drift check and then restored. A full rebuild by the lead
will apply the drift.
