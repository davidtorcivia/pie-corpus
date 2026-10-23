# Tier 2 (back-projection) adversarial review, round 2

Reviewer: an independent "skeptical Indo-Europeanist" subagent, 2026-10-23.
Scope: the 69 lines that were revised or added since round 1 (65 revised, 4 new: cattle-raid-009, fame-015, healing-charms-006, sky-father-015). Each line was read in `corpus/tier2/<cluster>.jsonl` in full: pie, english, tokens, cognate_refs with roles, secure_checks, notes, generator.plan.
Standards: PLAN.md Phase 5, `docs/generation/tier2-brief.md` (including its "Lessons"), and round 1's verdict scale, P1–P9.
Round 1's verdicts were not used as priors. Machine-readable verdicts are in `data/tier2/review-r2.jsonl`.
**Caveat:** like round 1, this was **not plant-calibrated**: no `make_review_packet.py` plants and no blind back-translation. It is one expert pass with full provenance visible.

Verdict rules, applied the same way to every line:
- **sound:** the head of the formula is attested in at least two branches, in genuinely parallel passages and in the same formation. For a verb-object formula the head is the verb; for a noun-phrase formula it is the noun plus its modifier. In addition, the collocation is not a commonplace, interpolation is honestly marked, and no form is contradicted by every daughter that attests the cell.
  - Cognates the builder's reflex table misses are credited, and flagged.
- **weak:** a real, citable parallel that is overclaimed. Typical causes:
  - the head is shared only at root level;
  - the frame is larger than the core;
  - the line's only addition beyond a core that another line already carries is non-cognate (duplication by itself is an eval-split matter, P8, and does not lower a verdict);
  - the collocation is generic;
  - a support ref leaks into the output;
  - an engine form is contradicted by the daughters.
- **reject:** one of:
  - the only shared item is a single cognate word that is not the head, or only root-level material, with non-cognate heads;
  - the collocation is a commonplace with no scholarly claim of inheritance;
  - the second branch contradicts the line or doesn't carry the phrase (misconstrual);
  - the only secure token has an outright wrong form.

## 1. Counts

| cluster | lines | sound | weak | reject |
|---|---|---|---|---|
| cattle-raid | 6 | 2 | 3 | 1 |
| dawn-sun | 14 | 1 | 9 | 4 |
| death-otherworld | 4 | 1 | 0 | 3 |
| divine-twins | 7 | 1 | 4 | 2 |
| dragon-slaying | 8 | 3 | 4 | 1 |
| fame | 10 | 2 | 7 | 1 |
| healing-charms | 5 | 2 | 1 | 2 |
| poetics-gifts | 6 | 2 | 2 | 2 |
| sky-father | 9 | 2 | 4 | 3 |
| **total** | **69** | **16 (23%)** | **34 (49%)** | **19 (28%)** |

Against round 1, on the same ids:
- **Round-1 sound (10):** 9 stay sound. twins-004 drops to weak, for a Vedic construal problem and an engine form.
- **Round-1 weak (55):**
  - 5 become sound: death-004, twins-005, dragon-011, poetics-008, poetics-015.
  - 31 stay weak.
  - 19 become rejects.
- **New (4):** fame-015 and healing-006 are sound; cattle-009 and sky-015 are weak.

Most of the new rejects come from **honest revisions**: round 2 correctly withdrew overclaimed secure flags, stitched loci and misconstruals, and the notes now say so plainly.
That honesty exposes lines with no shared phrase left. 26 of the 69 now have secure_share 0. Some of those are builder undercounts (see P1b), but most are genuinely empty. The brief says such lines are "not a back-projection; skip it", and the generator kept them anyway with "weak, kept with that warning" (P3).

## 2. Per-line verdicts

### fame (10)
| id | verdict | reason |
|---|---|---|
| fame-002 | weak | dʰedʰh₁dʰí is now correct. But the Greek is stitched from two texts, both unverifiable (Krisa for ἄφθιτον, Timocreon PMG 728 for τίθει; glaux has only Timocreon's epigram). The builder never matches ákṣita- = ἄφθιτος. Same RV 1.9.7 as fame-001, fame-004 and poetics-012. |
| fame-004 | weak | The frame (ἔχοι 'may he have') is Greek only and rests on the unverifiable Krisa inscription. The NP is the one already in fame-001, fame-002 and poetics-012 (same RV 1.9.7). |
| fame-005 | sound | máhi śrávaḥ = μέγα κλέος (RV 1.79.4, 1.43.7, Od. 2.125, Il. 6.446, all checked), with the beneficiary dative in both. The verb is now the correct present dʰedʰh₁dʰí, honestly interpolated. |
| fame-006 | weak | Only ḱléwos is secure. 'Wide' is the compound member urugāyá- against κλέος εὐρύ (root-level), and the verb is Vedic only. RV 6.65.6, Od. 3.83 and 1.344 checked. |
| fame-007 | weak | The plural 'fames' with a genitive of the doer is shared (Il. 9.524, Od. 8.73, RV 8.99.2 táva śrávāṃsi, all checked). But the distinctive 'of men' is Greek only (West: narā́m śrávāṃsi 'cannot be documented'), and 'heard' is interpolated (Greek πεύθομαι). |
| fame-008 | weak | Head *h₂is-sḱé- is exact (Ved. ichámāna-, RV 1.126.1 and 10.102.4, checked; OCS/ORuss. iskati, which the builder misses). The object is only root-level in Slavic (slava). The second branch is the late, contested Slovo (not local). |
| fame-009 | weak | *h₁wésu ḱléwos (Y. 62.6c vaŋhāuca srauuahi, checked; OIr fó chlú, not local). The Avestan has a locative after zazəbuiiē, and the line an accusative. The frame is Avestan only. Same NP and the same OIr ref as poetics-013. |
| fame-011 | weak | ὄνομα κλυτόν against śrútyaṃ nā́ma: śrútya- is another derivative (root-level), and 'bear' is Vedic only (bíbhrat, a participle). RV 5.30.5, Od. 9.364 and 19.183 checked. |
| fame-012 | reject | On the reading the note itself adopts, RV 8.46.14 (checked) has no 'famous name': nā́ma is adverbial and śrútyam goes with índram. So only 'name' is shared, in passages with no common phrase. Also shares Od. 19.183 with fame-011. |
| fame-015 | sound | Compound equation *h₁su-ḱléwes- (Ved. suśrávas- = Gk εὐκλεής, West ch. 10, checked). Both parallel loci checked: RV 1.91.21 and 1.49.2 suśrávasam, Od. 21.331 ἐϋκλεῖας predicated with ἔμμεναι. The nom. -ēs and the Vedic accent are defensible; the copula is honestly interpolated. A one-word formula; the builder can't credit compounds (share 0). |

### dragon-slaying (8)
| id | verdict | reason |
|---|---|---|
| dragon-slaying-001 | sound | Watkins' Basic Formula: past of *gʷʰen- in RV 1.32.1, Y. 9.8 and KBo 12.84 (Indo-Iranian checked). Hittite gives only the verb, so the serpent is one-branch, as Watkins' own formula has it. The Greek is now support (Pyth. 4.249 has κτεῖνε, checked). |
| dragon-slaying-002 | weak | The relative + *gʷʰen- appears in three traditions (Y. 9.8, RV 2.12.11, Od. 5.128, all checked), and κατέπεφνε is *gʷʰen-, which the builder misses. But the Greek is a reduplicated aorist (root-level), and 'Zeus who slew him (Iasion)' is a generic relative clause, not a hero defined by his monster-slaying. The serpent is Indo-Iranian only. |
| dragon-slaying-006 | sound | *h₁ógʷʰis … ḱéytor (RV 1.32.5, checked) with *gʷʰn̥tó- + *ḱey- (Yt. 10.80 jata sōire, Il. 24.757-758 πρόσφατος κεῖσαι). The serpent is Vedic only and honestly interpolated. Same formula as cattle-002 and death-004. |
| dragon-slaying-008 | weak | Better Vedic locus: RV 4.19.3 suṣupāṇám āśáyānam áhim (checked) beside Beowulf 2746-2747 ligeð, swefeð (checked). But only *swep- is shared, at root level, and 'lie' is two different roots (*legʰ- against *ḱey-). Secure share 0. |
| dragon-slaying-009 | reject | Wrong form in the only secure token. The INS.SG sh₂inéh₁ drops the m of *sh₂i-mn- (the engine's weak stem is sh₂in-: GEN sh₂inés), against Hitt. išḫimanta and OE sīmon. Also, the interpolated verb sinéh₂- is taken from RV 7.84.2, a support ref ('without ropes'). The parallel itself (KUB 17.5 i 15′ and Genesis 766, both checked) is fine: regenerate after fixing the n-stem. |
| dragon-slaying-010 | weak | Watkins ch. 43 is real (Grípisspá 11, Beowulf 587, RV 1.4.8, all checked). The predicate noun matches at formation level, but 'become' is renewed, and 'serpent' is interpolated where both texts have other words. The interpolated GEN h₁égʷʰis is contradicted by Ved. áheḥ. In Grípisspá 11 'bane' governs Regin ok Fáfni; orm goes with vega. |
| dragon-slaying-011 | sound | Watkins pp. 327-328 (checked) explicitly equates RV 8.84.9 nákir yáṃ ghnánti hánti yáḥ (checked) with OIr gonait 7 ní genaiter (TBDD 783, not local) as 'the slayer not slain'. *gʷʰen- in both clauses in both branches. Voice follows the Vedic. The builder can't match OIr gonaid, so share = 0: fix the flags. |
| dragon-slaying-013 | weak | Clause 1 *gʷʰen- + serpent is fine (KUB 17.5 i 18′, RV 6.20.2, both checked). Clause 2 'the gods were with him' is Hittite only (logographic DINGIRMEŠ, katti=šši). 1 verified token of 6. |

### healing-charms (5)
| id | verdict | reason |
|---|---|---|
| healing-charms-001 | sound | Heteroclitic polyptoton 'blood with blood': AVP 4.15.3 asṛk te asnā rohatu (DCS checked; the AVŚ correction is right) and KUB 55.20+ Vs. I 17-18 ešḫar=kan ešḫani ḫandan (TLH checked). The verb is honestly interpolated. The builder has no Hittite key, so share = 0. |
| healing-charms-002 | reject | The marrow clause is a one-branch proposition: no second branch has marrow-to-marrow, OHG is support only, and the marrow word is root-level. The second clause is healing-001 word for word, so it leaks a duplicate. The verb 'set' is stitched from AVŚ 4.12.5d (checked). |
| healing-charms-003 | weak | Watkins' reconstruction by contiguity, not an attested parallel. AVŚ 12.5 majjānam asya nirjahi (DCS checked). OHG and OIr each give one word, from texts that aren't local. Marrow is root-level. OIr gono is *gʷʰen-, which the builder misses. |
| healing-charms-005 | reject | Common words, a thematic parallel (the note says so itself). *steh₂- is root-level: Ved. práti tiṣṭha (AVŚ 4.12.6, DCS checked), an intransitive present, against Pindar's transitive ἔστασεν ὀρθούς (Pyth. 3.53, checked in glaux). The ūrdhvá-/ὀρθός equation is disputed. Share 0. |
| healing-charms-006 | sound | 'Bone with bone': AVP 4.15.2 asthnāsthy api rohatu (DCS checked) and KUB 55.20+ Vs. I 16 ḫaštai=kan ḫaštai ḫandan (TLH checked); Hitt. ḫaštai- is a true cognate of *h₃ésth₁. The verb is honestly interpolated. The INS h₃sth₁éh₁ lacks the Vedic n (asthnā́), but that n is the Indic i/n-stem pattern (ákṣi/akṣṇ-, dádhi/dadhn-), and Hitt. ḫaštai- has its own -i- extension. Handbooks give the oblique *h₃sth₁- without n, so this is not counted as a contradicted form. The builder has no Hittite key. |

### divine-twins (7)
| id | verdict | reason |
|---|---|---|
| divine-twins-001 | weak | A real invocation parallel (RV 10.61.4, checked; Alcaeus fr. 34, not local). The head 'son' is renewed in both branches and interpolated. In RV 10.61.4 me is possessive (me yajñám, me ánnam: 'my sacrifice', 'my food'), not 'come to me', so the moy parallel is weaker than the note says. Only diwés is secure. |
| divine-twins-002 | weak | 'Daughter of the Sun' is shared (RV 1.117.13, checked; Lith. Sáulės dukrýtė, not local), though Sáulė against sū́rya- is root-level. The clause is Vedic only. Form problems: 'of you two' comes out as plural wos (the plan has DU), and avr̥ṇīta is the imperfect of a nasal present, not a root aorist. |
| divine-twins-003 | reject | Stitched from RV 10.85.14 and 1.117.12-13 (two hymns, three stanzas; checked). Its only secure NP is the one twins-002 already uses (same RV 1.117.13, same dainos). The Vedic áyātam is 2du; the line has 3du. 6 tokens, 1 verified. |
| divine-twins-004 | weak | The formula is real (Watkins *h₁ōḱéwes h₁éḱwōs; Il. 5.275 ὠκέας ἵππους, checked). But in RV 8.5.7 (checked) āśúbhiḥ goes with śyenébhiḥ in pāda b and áśvebhiḥ stands in pāda c: use RV 1.117.9 or 7.71.5 āśúm áśvam, also of the Aśvins. The engine's INS.PL HHḱéwbʰis (zero-grade root, full-grade suffix) is contradicted by Ved. āśúbhiḥ and Gk ὠκ-. |
| divine-twins-005 | sound | Bahuvrihi *h₁su-h₁éḱwo- of the Twins in both branches: sváśvā … yātam (RV 7.69.3, checked) = εὔιπποι Τυνδαρίδαι (Pind. Ol. 3.39, checked in glaux, contrary to the note; West ch. 4 makes the comparison). The verb is honestly interpolated. The builder can't credit compounds (share 0). |
| divine-twins-006 | weak | Pastiche. 'Young' (yúvānā, RV 1.117.14) and 'sons of Sky' (1.117.12) come from different stanzas. The Greek gives only Διός (Hymn 33.1, checked in glaux), and the Latin iuuenes is Cicero's prose. h₂yéwHonh₁ has a full-grade root against Ved. yúvan- and Lat. iuu- (zero grade). |
| divine-twins-007 | reject | Only 'ship' is shared, a high-frequency noun; the verb and the object are Vedic only. The vocative 'Sons of Sky' in the output comes from a support ref (RV 1.117.12): P2 leaks into the PIE. The Alcaeus wording is unverified (West prints a translation). Hymn. Hom. 33.8 νηῶν (local) would have been the checkable Greek. |

### cattle-raid (6)
| id | verdict | reason |
|---|---|---|
| cattle-raid-001 | sound | *h₂eǵ- + *gʷṓws: RV 2.12.3 gā́ udā́jat and 8.14.8 úd gā́ ājat (checked) = Lat. boves abigere (Livy 1.7.4, not local; cf. abigeus 'cattle thief'). Same thematic present. Builder misses Lat. bōs and marks the object interpolated. Vergil Aen. 8.203-205 should probably go: from memory (not local), agebat governs tauros there and boves is the subject of tenebant. OIr táin bó is root-level only. |
| cattle-raid-002 | sound | *gʷʰn̥tó- + middle *ḱey-: RV 10.108.4 hatā́ … śayadhve, Il. 24.757-758 πρόσφατος … κεῖσαι, Yt. 10.80 sōire … jata (all checked). The builder doesn't credit -φατος or jata-. Same formula and the same Greek and Avestan loci as dragon-006 and death-004: one parallel for the eval split. |
| cattle-raid-004 | reject | Fails the head rule. No clause head is shared: 'slay' is Vedic only, 'drive' is Latin only (Hes. Th. 287-291, checked in glaux, has ἐξενάριξε … ἤλασεν), and 'head' is not cognate. Only 'three' and 'cow' are shared, both high-frequency. 1 verified token of 10. A myth-level parallel, not shared wording. Hesiod is local, contrary to the note. |
| cattle-raid-006 | weak | 'Cattle and horses' (Il. 1.154, RV 10.108.7, both checked) is a generic wealth pair (P5). The verb, 'my' and the negation are Greek only. |
| cattle-raid-007 | weak | Honest root-level line. The verb is shared only by root (Ved. ajati against Gk ἀγέλη, a noun; the Greek verb is ἐλαύνω), and gʰóstis stands in for non-cognate arí-. RV 1.33.3 and Il. 11.677-678 checked. |
| cattle-raid-009 | weak | Watkins' *peh₂- wiHro- peku- (ch. 17, checked in watkins/). Umbr. ueiro pequo (Tab. Ig. VIa 30, checked in Buck 1904) = Av. pasuuā̊ vīraiiā̊ (Yt. 13.10 = YtFra2.10e, checked). The merism is sound. But the interpolated imperative ph₂dʰí is contradicted by every daughter that attests the stem (Ved. pāhí, Av. pāiδi; *ph₂-dʰí would give Ved. *pidhí). Fix the form or cut the line to the NP, and it is sound. Builder can't match Umbrian, so share = 0. |

### dawn-sun (14)
| id | verdict | reason |
|---|---|---|
| dawn-sun-001 | sound | Vocative title *diwés dʰugh₂ter: RV 1.48.1 duhitar divaḥ and Il. 5.348 Διὸς θύγατερ (both checked). The verb and 'Dawn' are honestly interpolated; Od. 9.151 adds only Ἠώς. Same title as sky-014, with Rhesa no. 78 cited in both: group them for eval. |
| dawn-sun-002 | reject | Secure share 0. 'Shine' is Greek only (φάνη), 'born' is root-level (jā́yamāna-, a -ye- present, against the compound ἠριγένεια), and the reduplicated participle ǵíǵn̥h₁omh₁neh₂es is in neither branch. Only the Dawn word is shared. After the round-2 cuts nothing is left that is a shared phrase. |
| dawn-sun-003 | weak | West ch. 5 pairs φάε … Ἠώς (Od. 14.502) with Ved. bhā of Uṣas (RV 3.61.2 ví bhāhi), both checked. But the Greek is a 3sg past, the line is an imperative, and the root-imperative bʰh₂dʰí is contradicted by Ved. bhāhí (full grade). |
| dawn-sun-004 | weak | Middle voice is now correct (yukṣvá, ζεύγνυσθ', RV 1.92.15 and Od. 23.244-246 checked). Still: different stems (s-aorist against -νυ- present), and the Greek is a negated infinitive. Yoking horses is generic; only Dawn as the agent makes it specific. |
| dawn-sun-005 | weak | *bʰer- + Dawn is shared (RV 10.35.5 jyótir bhárantīr uṣásaḥ, Il. 11.1-2 φόως φέροι, both checked; also Od. 23.245). The object is not cognate (jyótis- against φάος), and the interpolated bʰéh₂os is not φάος's formation (*φάϝος). |
| dawn-sun-008 | reject | Contradiction. In Hes. Th. 371-374 (checked in glaux, though the note says not local) Theia bears Helios, Selene and Eos, so Dawn is the Sun's sister, not his mother. 'The Dawns bore the Sun' is a Vedic-only proposition (RV 7.78.3, checked). The formations also differ: reduplicated aorist against γείνατο. |
| dawn-sun-009 | weak | West ch. 5 notes the cognate epithet (RV 3.2.7 svàr mahát, Hes. Th. 19 Ἠέλιον μέγαν, both checked), but 'great' + 'sun' is generic. Both branches have it attributive; the line makes it predicative with an interpolated copula. |
| dawn-sun-011 | weak | spáś- against σκοπός is root-level, as the note says (RV 4.13.3 and Hymn. Dem. 62, both checked; the Hymn is local in glaux). The builder's 'exact' for Greek is a false positive: a 3-letter prefix match on σκώψ. |
| dawn-sun-012 | reject | Secure share 0. 'Goes up' is Vedic only (ἀνόρουσε is another verb). márteṣu is governed by páśyan ('looking at … among mortals'), not 'for mortals'. Ved. márta- (full grade) is not exactly βροτός (*mr̥tó-). What's left is the sun rising for people, a commonplace. |
| dawn-sun-013 | reject | 'The sun shines' is the commonest possible collocation (P5). There is no scholarly claim of inheritance, and φαείνω is a derived present against Ved. bhā́ti. RV 10.121.6 and Od. 12.385 checked. |
| dawn-sun-015 | weak | Only the NP 'wheel of the Sun' is shared (cakrám sū́ryasya = κύκλος ἀελίοιο). 'Horse' is Greek only and 'draw' Vedic only. West doubts the image is PIE. Eur. El. 464-466 is local in glaux (checked), contrary to the note. The NP overlaps dawn-014. |
| dawn-sun-017 | weak | 'Eye of Sky' rests on RV 1.72.10 divó … akṣī́ (dual, sun and moon; checked) and Macrobius' late report. The 'eye' words are different formations (ákṣ-/ákṣi- against the diminutive oculus). Greek is properly support only. |
| dawn-sun-020 | weak | A real West parallel ('to live is to see the sun', West ch. 2). 'Live' is root-level and 'see' is Vedic only. The optative mood comes from RV 10.37.7, a support ref, so P2 leaks into the output. All loci checked. |
| dawn-sun-021 | weak | The note is wrong in the cautious direction. vedaweb has ájma- m., a thematic noun (mahó ájmasya, RV 4.53.4, checked), the same *-mo- formation as ὄγμος (Hymn. Hom. 32.11, checked in glaux). So the NP equation holds at formation level. But 'great' + 'course' is a natural pairing, West's 'exact equivalent' claim could not be found in the local text, the verb and the locative are interpolated, and LOC méǵh₂i has an unexpected full-grade root. |

### death-otherworld (4)
| id | verdict | reason |
|---|---|---|
| death-otherworld-001 | reject | Only one formation-level noun is shared (támas : tenebrae). The verbs differ (a causative gamaya against uiso), and with 'lower' now interpolated, West's NP formula ('lower darkness') is gone. RV 10.152.4 is a curse sending an enemy below; Lucr. 1.115 is about the soul's fate (both checked). Darkness as the place of the dead is near-universal. |
| death-otherworld-004 | sound | 3pl 'the slain lie': Yt. 10.80 sōire … jata and RV 1.133.1 hatā́ḥ … áśeran (both checked), with Il. 24.757-758. The 3pl middle -n̥tor is defensible (Homeric κέαται; Indo-Iranian has the r-ending, which the note flags). Duplicates the formula of cattle-002 and dragon-006 (same Greek and Avestan loci). |
| death-otherworld-005 | reject | Secure share 0, and every shared item is root-level: κοιμάω (a derivative of *ḱey-), Ved. svap- (a verb) against ὕπνος (a noun). The Greek has a cognate accusative and the locative is interpolated. 'Death as sleep' here is thematic. RV 1.121.11 and Il. 11.241 checked. |
| death-otherworld-009 | reject | A single lexeme (νέκυς; OIr éc means 'death', not 'the dead') with non-cognate verbs. 'Go to the dead' is a near-universal idiom. The OIr is an idiom quoted from West, not a locus. Il. 15.251-252 checked. |

### poetics-gifts (6)
| id | verdict | reason |
|---|---|---|
| poetics-gifts-002 | reject | The NP 'carpenters of words' stands in no cited text. In Pyth. 3.112-113 (checked in glaux, contrary to the note) ἐπέων depends on ἐξ and τέκτονες is the subject of ἅρμοσαν; Nem. 3.4 has τέκτονες κώμων. The Vedic has a different agent noun in a simile (táṣṭeva, RV 3.38.1, 1.61.4), and the Avestan a compound (N. 5.2). The *wékʷos/*tetḱ- collocation belongs to poetics-001. |
| poetics-gifts-008 | sound | Benfey's δῶτορ ἑάων = dātā́ vásūnām (Od. 8.335, RV 8.51.5, both checked), with Y. 16.1 correctly demoted to support. The Greek -τωρ supports the root-accented déh₃tor and the Vedic the oxytone, which the note acknowledges. The verb is interpolated. Shares RV 8.51.5 with poetics-007. |
| poetics-gifts-010 | reject | Only 'horse' is shared. 'Song' (gír- against dúan) and 'give' (dā- against do-beir) are not cognate. Watkins compares the institution (horses as the poet's fee), not wording. The Irish text isn't local. RV 6.63.10 checked. |
| poetics-gifts-011 | weak | The secure NP is the same as fame-005's and uses the same Od. 2.125-126. Its own content, 'make' (kṛdhi against ποιεῖτ'), is a semantic frame with non-cognate verbs. RV 5.18.5 checked. |
| poetics-gifts-014 | weak | *misdʰó- is a specific technical term (mīždəm, Y. 44.18, checked; μισθόν, Pyth. 1.75-77, checked in glaux) in a 'win the reward' frame. The verbs are not cognate (han- against ἀρέομαι), and 'how' is Avestan only. |
| poetics-gifts-015 | sound | Root-aorist imperative *ḱludʰí exact (κλῦθι, śrudhí; Il. 1.37, RV 1.25.19, both checked), plus a 1sg enclitic. Homer always has the genitive κλῦθί μευ (8 times in the treebank, never μοι), so *moy follows Ved. me (gen./dat.) and Greek has renewed the genitive enclitic. The builder marks it root-level, which is an undercount. Minor: in RV 1.25.19 me goes with hávam ('my call'). |

### sky-father (9)
| id | verdict | reason |
|---|---|---|
| sky-father-001 | weak | The core *dyéw ph₂ter is sound in three branches (RV 6.51.5, Il. 3.276, Cato Agr. 134.3 Iupiter, all checked). But the Earth half still has the engine's pl̥th₂éwih₂ (Greek-type -ew-ih₂, and the VOC keeps -ih₂), contradicted by Ved. pṛthivī́/pŕ̥thivi: round-1 P6 is not fixed. The OE 'Folde … mōdor' is not in the local Grein. |
| sky-father-002 | weak | Only the kin terms are shared beyond Vedic. Lucretius' pater aether / mater terrai (1.250-251, checked) is a Greek-influenced topos, and Æcerbot is not local. The form pl̥th₂éwih₂ is still wrong. 9 tokens, 2 verified. |
| sky-father-003 | sound | mahé pitré divé (RV 1.71.5, checked; RV 3.54.2 mahé divé) = Ζεῦ πάτερ … μέγιστε (Il. 3.276, checked). The cases follow the Vedic and the forms are right (m̥ǵh₂éy fits Ved. mahé). Unlike fame-006, whose secure core is one word, the core here is already the two-word *dyéw ph₂ter formula, plus 'great'. Shares Il. 3.276 with sky-001: one eval group. Note: Greek 'great' is the superlative here and the λ-stem in Il. 2.134, so the builder's 'exact' is generous. |
| sky-father-004 | reject | Only the genitive 'of Sky' is shared. The heads differ (ὄμβρος against vr̥ṣṭí-), and the note itself says the line fails the head rule. A semantic parallel ('Sky's rain') with one cognate modifier. Il. 5.91, RV 5.83.6 and 5.63.4 checked. |
| sky-father-007 | weak | Root-level throughout (sádman- against the compound -εδής). The output head sédos comes from a support ref (Hes. Th. 117), so P2 leaks, and 'earth' and 'for the gods' are interpolated. The builder's 'exact' for 'broad' is a prefix match on a compound. Simonides isn't local. |
| sky-father-010 | reject | Only diwés is shared (Hymn 33.1 Διὸς κούρους, checked in glaux; RV 1.182.1, checked). Head and predicate are interpolated, and it overlaps twins-001 and twins-006 (same Hymn 33.1). |
| sky-father-013 | reject | Zero verified tokens. Among the parallel refs, dyēws is Vedic only, 'mother' is OE only (Æcerbot, not local), the verb is interpolated, and the Earth name is root-level. A pastiche of a ploughman's prayer. Hes. Op. 465 and Cato 134.2 checked. |
| sky-father-014 | sound | *diwés dʰugh₂tḗr (RV 10.39.12, Od. 4.227, both checked; Lith. dukrýtė supports dʰugh₂tḗr only). The verb is honestly interpolated, though the reduplicated present doesn't follow the Vedic jā́yate. Same title as dawn-001. |
| sky-father-015 | weak | *déms pótis is a phrase only in Indo-Iranian (RV 1.149.1 pátir dán, Y. 45.11 də̄ṇg patōiš, both checked). The Greek is a compound of another formation (δέσποινα, Od. 14.9, checked), so the second branch is root/formation-level for 'master'. The copula is interpolated. |
## 3. Round-1 problems: fixed, partly fixed, still open

**Fixed (credit where due):**
- The `role: parallel | support` split exists, and the builder computes `secure_checks` instead of trusting `secure` (P1a, P2 at the ref level).
- Ved. dhehi is now the present dʰedʰh₁dʰí in fame-002, fame-005 and fame-006.
- dawn-004 now has the middle voice.
- poetics-015 now has the dat./gen. enclitic.
- The Lith. Diẽvo < *deywós position is used consistently.
- Most of round 1's P7 misconstruals are corrected: fame-007, fame-008, sky-004, sky-013's locus, poetics-008, dragon-002, dragon-011, death-004's OE nū.
- Stitched words were dropped (dawn-005, -009, -011, -012, -013, -015).
- The AVP/AVŚ stanza numbers were corrected against the DCS.

**P1b (new): the builder's secure check is wrong in both directions.**
- **False "exact".** `secure_check` matches when one normalized key is a 3-letter prefix of the other (`k[:max(3, len(k)-2)]`), so derivatives and compounds pass:
  - σκοπός counts as exact for *spéḱs through σκώψ (dawn-011);
  - εὐρυεδής counts for *h₁wérHus (sky-007);
  - μέγιστε and μεγάλου count for *méǵh₂s (sky-003).
  - Wiktionary reflex lists add their own errors: ájma- is listed under *h₂óǵmos (correct by chance, see dawn-021), and σκώψ under *spéḱs.
- **False "none".** The table has no keys for:
  - Gk ἠώς, ἠέλιος, ἄφθιτος, -φατος, κατέπεφνε;
  - Ved. duhitár-, ákṣita-, márta-, śrudhí;
  - Hitt. ēšḫar, ḫaštai-;
  - OIr gonaid, clú;
  - Umbrian anything;
  - OCS/ORuss. iskati.
- **Compounds are never credited.** A line built on a compound gets share 0: fame-015, twins-005.
- **Effect:** `eval_grade` (sound review **and** at least one exact check) would exclude healing-001, healing-006, fame-015, twins-005, dragon-011 and poetics-015. These are among the best lines in the tier, and it would admit nothing it should exclude.
- **Fix (builder and lexicon):**
  1. Match on stem plus suffix class, not on a 3-letter prefix.
  2. Add a reviewed daughter-reflex table for the lemmas above.
  3. Credit a compound token when both members match the same compound in two branches.
  4. Let a reviewed `formation_match` override the mechanical level, and gate `eval_grade` on the review verdict plus the reviewed match, not on the mechanical check alone.

**P2 (partly fixed): support refs still leak into the output.** The role split is respected for counting branches, but material from support refs still stands in the PIE line:
- twins-007's vocative 'Sons of Sky' (RV 1.117.12);
- dawn-020's optative (RV 10.37.7);
- sky-007's head sédos (Hes. Th. 117);
- dragon-009's verb sinéh₂- (RV 7.84.2, a passage that says 'without ropes').

**Fix (builder):** a token whose lexeme is attested only in support refs must be flagged interpolated **and** named in the notes as "from support". Better, reject a plan whose head comes only from support refs.

**P3 (still open): the frame outweighs the core.**
- Examples: cattle-004 (1 verified token of 10), twins-003 (1 of 6), dragon-013 (1 of 6), sky-002 (2 of 9).
- Several notes say "weak, kept with that warning" (healing-002, -005, poetics-002).
- The brief's fix (emit only the shared NP or formula) was not applied.
- **Fix (brief):** make it a hard rule. If the clause head is not shared at least at root level, the record is the NP or formula alone, and the sentence frame goes in `alt_reconstructions`.

**P5 (still open): generic collocations.**
- Examples: sun + shine (dawn-013), great + sun (dawn-009), cattle + horses (cattle-006), a lone 'horse' (poetics-010), a lone 'ship' (twins-007), 'go to the dead' (death-009), 'darkness' (death-001).
- **Fix (brief):** require a quoted scholarly claim that the *wording* (not the motif) is inherited. A one-lexeme line (one cognate, non-cognate head) is never a back-projection.

**P6 (still open): engine and lexicon forms.** Forms contradicted by every daughter that attests the cell:
- **sh₂inéh₁ and the whole weak stem sh₂in-** (dragon-009): the n-stem *sh₂i-mn- loses its m. Hitt. išḫimanta and OE sīmon keep it. This is a stem-parsing bug for *-mō(n) nouns; check the other -mṓ/-mō lexemes.
- **pl̥th₂éwih₂** (sky-001, -002, -013): Greek-type *-ew-ih₂ where Ved. pṛthivī́ requires *pl̥th₂wih₂, and the VOC keeps -ih₂ where Ved. pŕ̥thivi has -i. This is round 1's P6, untouched.
- **Zero-grade root imperatives of ā-roots:** ph₂dʰí (cattle-009) and bʰh₂dʰí (dawn-003), where Ved. pāhí, bhāhí and Av. pāiδi all have full grade. A rule-based zero grade would give Ved. *pidhí or *bhidhí.
- **Proterokinetic u-stem obliques:** HHḱéwbʰis (twins-004), against Ved. āśúbhiḥ and Gk ὠκ-. The lexicon's `accent_class: proterokinetic` for HéHḱus is the cause.
- **Others:**
  - full-grade h₂yéwHonh₁ (twins-006), where yúvan- and iuu- have zero grade;
  - acrostatic GEN h₁égʷʰis (dragon-010), against Ved. áheḥ;
  - LOC méǵh₂i (dawn-021);
  - INS h₃sth₁éh₁ without the Vedic n-stem (healing-006, a minor point).
- **Plan honored only in part:** twins-002 asks for a dual and gets plural wos.
- **Defensible, noted only:**
  - ḱéyn̥tor, where Indo-Iranian has *-ro but Homeric κέαται has *-n̥t-;
  - the 1pl middle -mesdʰh₂ (Greek -μεσθα only; Ved. -mahe points to *-medʰh₂).
- **Fix (engine, lexicon):** in the generation check, compare every interpolated or secure form against the cited daughter forms for that cell. If all of them disagree on root grade or suffix, flag it instead of shipping it.

**P7 (new misconstruals found this round):**
- RV 8.5.7: āśúbhiḥ goes with śyenébhiḥ in pāda b, and áśvebhiḥ stands in pāda c (twins-004). Use RV 1.117.9 or 7.71.5 āśúm áśvam.
- RV 10.61.4: me is possessive, me yajñám, me ánnam (twins-001).
- Pind. Pyth. 3.112–113: ἐπέων depends on ἐξ, and τέκτονες is the subject of ἅρμοσαν. There is no 'carpenters of words' NP (poetics-002, and also round-1-sound poetics-001's Greek).
- Hes. Th. 371–374: Theia bears Eos too (dawn-008).
- RV 8.46.14: on the note's own reading there is no 'famous name' (fame-012).
- Grípisspá 11: at bana verða governs Regin ok Fáfni, while orm goes with vega (dragon-010, a minor point).
- Verg. Aen. 8.203–205: agebat governs tauros (from memory; not local) (cattle-001).
- dawn-021's note says ájma- is *-mn̥. vedaweb has ájma- m., a thematic noun, the same formation as ὄγμος. This is an error in the cautious direction.

**P8 (still open): duplication.** The builder's dedup key is the identical locus set, so the same formula survives under different loci:
- cattle-002, dragon-006 and death-004 (same Il. 24.757–758 and Yt. 10.80);
- fame-001, -002, -004 and poetics-012 (RV 1.9.7);
- fame-005 and poetics-011 (Od. 2.125);
- fame-009 and poetics-013 (the same OIr ref);
- fame-011 and -012 (Od. 19.183);
- dawn-001 and sky-014 (the same title, Rhesa no. 78);
- twins-002 and -003 (RV 1.117.13);
- twins-001, twins-006 and sky-010 (Hymn. Hom. 33.1, the 'X of Sky' title);
- healing-001, -002 and -006 (same AVP 4.15 and KUB 55.20+; healing-002's second clause is healing-001 word for word);
- poetics-008 and poetics-007 (RV 8.51.5);
- sky-003 and sky-001 (Il. 3.276, the *dyéw ph₂ter core).

**Fix:** key the eval split on the sorted secure lex_ids plus the source texts (hymn or tablet, not stanza), and keep each group wholly in train or wholly in eval.

**P10 (new): the generator doesn't know glaux.**
- Notes say "not in local corpora" for texts that **are** in `raw/daughters/glaux`:
  - Hes. Th. 19, 117–118, 287–291, 371–374; Op. 465;
  - Hymn. Hom. 2.62, 31.2, 32.11, 33.1;
  - Pind. Ol. 3.39; Pyth. 1.75–77, 3.53, 3.112–113, 4.249; Nem. 3.4;
  - Eur. El. 464–466.
  - I checked all of these. Two of them overturn a line: Th. 371–374 for dawn-008, and Pyth. 3.112–113 for poetics-002.
- The brief's evidence list omits glaux and `oscan-umbrian-buck1904`. The latter is used (cattle-009), but the builder can't match Umbrian.
- **Fix (brief):** add glaux (Hesiod, the Hymns, Pindar, Bacchylides, tragedy) and Buck to the evidence list, and require a local check where a corpus exists.

## 4. Loci checked and findings

**Totals:** the 69 lines cite 225 refs (171 parallel). I checked about 150 loci locally. Every checked locus contains the cited words: **no fabricated attestation was found.** The problems are construal (P7), formation (P1b) and generic pairing (P5).

**Rigveda (vedaweb, 70 stanzas):**
- Book 1: 1.4.8, 1.9.7, 1.25.19*, 1.32.1, 1.32.5, 1.43.7, 1.48.1, 1.49.2, 1.53.9, 1.61.4, 1.71.5, 1.72.10, 1.79.4, 1.89.4, 1.91.21, 1.92.15, 1.103.7, 1.116.3, 1.117.12–14, 1.119.5, 1.121.11, 1.126.1, 1.133.1, 1.149.1, 1.164.2, 1.164.33, 1.182.1, 1.185.6
- Books 2–5: 2.12.3, 2.12.11, 2.23.2, 3.2.7, 3.38.1, 3.54.2, 3.61.2, 4.13.3, 4.19.3, 4.53.4, 5.18.5, 5.30.5, 5.63.4, 5.83.6
- Books 6–8: 6.17.7, 6.20.2, 6.51.5, 6.63.10, 6.65.6, 7.60.2*, 7.63.2, 7.68.1, 7.69.3, 7.69.4, 7.78.3, 8.5.7*, 8.14.8, 8.46.14*, 8.84.9, 8.99.2
- Book 10: 10.35.5, 10.37.7, 10.39.12, 10.57.4, 10.61.4*, 10.85.14, 10.102.4, 10.108.4, 10.121.6, 10.152.4
- Plus searches: āśúm áśvam (1.117.9, 7.71.5) and pátir dán (1.149.1, 1.153.4, 10.99.6, 10.105.2).

**Homer (AGDT, 32 loci):**
- Iliad: 1.37, 1.154, 2.134, 3.276, 5.91, 5.275, 5.348, 6.446, 9.524, 11.1–2, 11.241, 11.677–678, 15.251, 16.417, 18.61, 24.757–758
- Odyssey: 1.344, 2.125–126, 3.1–3, 3.83, 4.227, 5.128, 8.73, 8.335, 9.151, 9.364, 12.385, 14.9, 14.502, 19.183, 21.331, 23.244–246

**glaux (20 loci):**
- Hesiod: Th. 19, 117–118, 287–291, 371–374*; Op. 465
- Homeric Hymns: Hymn. Hom. 2.62, 31.1–2, 32.11, 33.1–2, 33.8–12
- Pindar: Ol. 3.39; Pyth. 1.75–77, 3.51–54, 3.112–113*, 4.249; Nem. 3.4–5
- Euripides: El. 464–467
- Timocreon: only an epigram is in glaux, not PMG 728.

**Avesta (CAB):** Y. 9.4, 9.8, 30.10, 44.18, 45.11, 62.6; Yt. 10.60, 10.76, 10.80, 13.10; N. 5.2 (vacastaštiuuat̰); a vacas-tašti- search.

**Atharvaveda (DCS):**
- AVP 4.15.1–3 (majjā majjñā, asthnāsthi, asṛk … asnā)
- AVŚ 4.12.1–6 (asṛk te asthi; chinnaṃ saṃ dhehi; prati tiṣṭha ūrdhvaḥ)
- AVŚ 12.5 (majjānam asya nirjahi)

**Hittite (TLH):**
- KUB 55.20+ Vs. I 3–18 (ḫaštai=kan ḫaštai ḫandan, I 16; ešḫar=kan ešḫani ḫandan, I 17–18)
- KUB 17.5 Vs. I 15′ (išḫimanta) and I 18′ (kuenta DINGIRMEŠ-ša kattišši ešer)

**Latin (LASLA):** Cato Agr. 134.1–4 (Iupiter in 134.2 and 134.3), 141.3 (pastores pecuaque); Lucr. 1.115, 1.250–251.

**Other:**
- Umbrian: Buck 1904, Tab. Ig. VIa 30 (nerf arsmo ueiro pequo).
- Old English: Beowulf 587, 2746–2747; Genesis 766 (Grein: simon gesǣled).
- Old Norse: Grípisspá 11 (FJ 1926).

**Scholarship checked:**
- Watkins pp. 327–328 (the slayer not slain: RV 8.84.9 and TBDD 783);
- Watkins ch. 17 and p. 30 (*peh₂- wiHro- peku-, Umbrian VIa, Yt. 13);
- West ch. 2 (see the sun = be alive);
- West ch. 4 (εὔιπποι = suáśvā; the Dioskouroi at sea);
- West ch. 5 (Dawn and bhā / φάε; 'great' and 'swift' sun; σκοπός : spáś-);
- West ch. 10 (suśrávas- = εὐκλεής; fó chlú).
- Not found locally: West's "exact equivalent" for mahó ájmasya = μέγας ὄγμος. Clackson pairs ájman- n. with Lat. agmen.

(* = construal problem, see P7.)

**Not locally checkable: 35 refs (26 of them parallel).**
- Greek: Krisa; Timocreon PMG 728; Alcaeus fr. 34; Simonides PMG 542.
- Latin: Livy; Vergil; Cicero; Varro; Macrobius.
- Baltic: Rhesa and the dainos.
- Old English: Æcerbot (not in the local Grein OCR).
- Celtic: all Old and Middle Irish (TBDD, Laws, Lebor na hUidre, the Verslehren, the worm charm, ZCP) and the Welsh Hendregadredd.
- Old High German: the charms.
- Slavic: the Slovo.
- **Lines that rest on such a ref for their second branch:**
  - entirely: fame-002, fame-004, fame-008, fame-009, dragon-011, sky-007;
  - in part: cattle-001 (Livy), dawn-017 (Macrobius), twins-001 (Alcaeus), sky-001 and -002 (Æcerbot).

## 5. Can the sound lines serve as evaluation data?

**Yes, as a small formula-level set, but not as the builder currently marks them.**

The 16 sound lines reduce to **12 distinct parallels** once duplicates are grouped:
1. cattle-001
2. {cattle-002, dragon-006, death-004}
3. {dawn-001, sky-014}
4. twins-005
5. dragon-001
6. dragon-011
7. fame-005
8. fame-015
9. {healing-001, healing-006}
10. poetics-008 (with poetics-007)
11. poetics-015
12. sky-003 (with sky-001)

Conditions:
1. **Score only the secure core** (the formula), not the interpolated frame. Most sound lines have an honestly interpolated verb.
2. **Fix the flags first** (P1b). Six of the 16 have no verified token, or only root-level ones, because of reflex-table gaps, so `eval_grade` excludes them. Gate eval on this review plus a reviewed formation match.
3. **Split by formula group**, never by line (P8). Keep the groups above, plus fame-001/-002/-004/poetics-012, together.
4. **Regenerate after the engine fixes in P6** where they touch a group. None of the 16 sound lines currently carries a daughter-contradicted form in its secure core. The near-misses do: cattle-009 and twins-004 become sound once ph₂dʰí and HHḱéwbʰis are fixed (and twins-004 gets a better Vedic locus). dragon-009 becomes weak once the n-stem bug is fixed.
5. **Rerun the gate as PLAN specifies** before Tier 2 is marked done: a `make_review_packet.py` packet with planted errors, plus the blind back-translation. This review, like round 1, was not calibrated.

The 34 weak lines are usable for training if their flags are corrected, ideally cut down to their shared NP or formula. The 19 rejects should not reach the corpus as they stand:
- 3 can be rebuilt: dragon-009 after the engine fix; poetics-002 as an NP-less *wékʷos + *tetḱ- line; twins-007 on Hymn. Hom. 33.
- The rest should be dropped. They are parallels of motif, not of wording.
