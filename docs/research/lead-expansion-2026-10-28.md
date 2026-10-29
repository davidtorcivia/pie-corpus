# Lead expansion: collocation scans of 20 seed words (2026-10-28)

Exploratory, outside the pre-registered measures, in the manner of
`8c-collocation-scans.md`. Tool: `scripts/collocates_8c.py`, window ±4, over the search
index as rebuilt today after the corpus-quality batch (the 22:41 build; not rebuilt here).
A later rebuild (cq2, 23:50) landed after the scans. The build used here is now
`corpora.pre-cq2.sqlite`, and the counts below are from that build. Scan outputs (forms and loci only):
`data/research/leads/expansion-2026-10-28-scans/<seed>.json`. Candidate rows:
`data/research/leads/expansion-2026-10-28.jsonl`. Mapping errors:
`data/research/formulas/mapping-errors-lead-expansion.jsonl`.

## Method

The method is the one in `8c-collocation-scans.md`. For each seed, `--target` listed the
cross-branch collocates. For each promising collocate, a `--pair` run listed every hit per
branch. A scratch variant of `--pair` used the same window logic and also printed the matched
form pair. As a spot check, the tool's own `--pair` on that build (heart + *men-*, window 3) gives the
same per-branch counts (81/27/11/7/1). I then read each hit in its unit and the two units on either side, with the
lemma/root of every word shown, and checked the etymology of the words that carried the
match. Atharvaveda loci are given as verses
(`pie.formula_search_multi.dcs_verse_citation`, the 8c erratum rule). "(inf.)" marks a verse
inferred where DCS has no counter.

| Seed | Target ids |
|---|---|
| heart | `pie-root-kjerd-heart` |
| mind | `pie-root-men-think` |
| name | `pie-lex-h1nomn` |
| fame | `pie-lex-kjlewos`, `pie-lex-kjlewmn` |
| fire | `pie-lex-h1ngwnis`, `pie-lex-peh2wr` |
| water | `pie-lex-wodr`, `pie-root-wed-well`, `pie-root-h2ep-water` |
| horse / cow | `pie-lex-h1ekjwos` / `pie-lex-gwoxws` |
| word | `pie-lex-wekwos` (Greek only, 2608 units; Ved. *vácas-* is keyed only to the root), so also `pie-root-wekw-speak` |
| sky/day | `pie-root-dyew-be_bright` |
| night / earth | `pie-lex-nokwts` / `pie-lex-dhegjhoxm` |
| king / guest | `pie-lex-h3rexgjs` / `pie-lex-ghostis` |
| house | `pie-lex-doxm`, `pie-root-dem-build` |
| path | `pie-lex-pontoh1s`, `pie-root-pent-pass` |
| eye | `pie-lex-h3okwih1`, `pie-lex-h3okws`, `pie-root-h3ekw-see` |
| hand / death / life | `pie-root-gjhes-hand` / `pie-root-mer-die` / `pie-root-gweyh3-live` |

## Summary

**The scans found no new candidate.** Every phrase that survived reading is either in the
held literature or already among this project's leads:

- *hear my word* is C022 (`8c-novelty.md`, partly known) and Tier 2 line poetics-gifts-016.
- *imperishable water* is stage-B claims B023 and B065, both graded weak.
- *wide path / wide sea* is 8a candidate no. 29, graded generic.
- *μένος ἠΰ ~ vohu manah* is known (Schmitt 1967) and is Tier 2 line epic-diction-008.

As a control, this is good: read hit by hit, the scans recover the textbook and
already-found shapes, and they recover them independently. As a search for new leads, these
20 seeds look saturated at this window and with the current mapping coverage. The scans also
found five mapping errors (below).

## Results by seed

Verdicts: **known** = stated in the held literature; **candidate** = cognate words in a
congruent construction in ≥ 2 branches, not stated as such in the held literature;
**generic** = an everyday or natural pair, a non-parallel construction, or Biblical, Latin-model
or translation wording; **mapping error** = the match rests on a wrong key.

| Seed | What the scans show | Verdict |
|---|---|---|
| heart | Heart + mind: the Vedic dyad *hr̥dā́ mánasā* (81 units). OIr *cride ⁊ menma* is homiletic prose, all of it Christian (G206000 ×7). ON *hjarta* ~ *munu* is the auxiliary 'shall' (root-level *men-*, below). Heart + ear (*h₂ṓws*) in Gmc, Arm, Gk and Slav: the Biblical 'heart and ears' (Zographensis, Gregory, the Benedictine Rule). Heart + tongue: unchanged from 8c. Heart + grief (*h₂eǵʰos*): Homeric ἄχος … κραδίην/κῆρ ×7 (Il. 2.171, 15.208 = 16.52, 17.539, 23.47; Od. 10.247, 18.348), but ON *agi* / OHG *egislîh* do not parallel it. Heart + desire: the RV *hr̥tsú kā́māḥ* type, and Christian OIr. | Heart and mind: as 8c (Vedic dyad). Heart and ear: generic (Biblical). ἄχος κραδίην: Greek-internal. |
| mind | Mind + good (*h₁wésu-*): Hom. μένος ἠΰ ×6 (Il. 17.456, 20.80, 23.524, 24.6, 24.442; Od. 2.271) ~ Av. *vohu manah-* (Gāthās, Y 28.4 … 34.15). Mind + tongue: RV 10.53.11b *mánasā … jihváyā*; the other branches are noise. Mind + know (*ǵneh₃-*): Lith and Serbian everyday pairs. | μένος ἠΰ ~ *vohu manō*: **known** (Schmitt 1967 §§210–214; West ch. 2), already epic-diction-008. Mind and tongue: Indic-internal. |
| name | Name + worshipful (*h₁yaǵ-*): RV *nā́ma yajñíyam* (1.6.4c, 6.48.21c, 8.80.9a). The Greek hits are Septuagint and NT ὄνομα ἅγιον. Name + people (*tewteh₂*): Umbrian *totar Iiouinar nome* (Tab. Ig. VIa 30–59), ON/OHG 'in his name … all peoples' (Biblical), and ON *þýða* 'interpret'. Name + praise (*gʷerH-*): RV *nā́ma gr̥ṇīmasi* and OIr *a ainm … co bráth*; Matasović has *bráth* < *gʷr̥H-tu-*, so the key is not an error. | Generic or one-branch; the Greek is Biblical. |
| fame | Imperishable fame (RV 1.40.4b ~ Il. 9.413), fame + name (RV 1.57.3c ~ MIr *clú … ainm*), wide fame (RV 1.9.7b ~ MIr *clú … leth*), fame + mortals. | **Known**: all recovered, as in 8c. |
| fire | Fire + water in 5 branches (*péh₂wr̥* + *wódr̥*; in Slavic, Serbian *огањ … вода* has *h₁n̥gʷnis*): Hitt. *paḫḫur … watar* (KBo 53.33+ Rs. IV 4, a ritual 'as this fire is quenched'; KUB 34.85+; HKM 116), Hom. (Il. 18.348 = Od. 8.437 boiling water, Od. 4.418), Theognis 1245, Pind. Ol. 1.1, Toch. A 647 14a2 *poryo … wäryo*. The OHG hits are Latin-model (Tatian 92 = Matt. 17:15; Notker Ps. 65). Fire + kindle: RV *agnínā idhyate* ~ πυρὸς αἰθομένοιο (the noun is renewed). Fire + quench (*sgʷes-*): Hom. πῦρ … ἔσβεσεν ~ Serbian *огањ … гаси*. Fire + worm: Mark 9:48 and AV. Living fire: Serbian epic *живи огањ* (88 units), OHG Notker *quecchemo fiure* (Boethius). Fire + stone: RV 2.12.3c ~ a Lith. daina that does not match. | Fire and water: **generic** (a natural pair everywhere; West ch. 6 has fire and water as elemental deities, after Hdt. 1.131.2). The rest: generic or Biblical. |
| water | Water + imperishable: Hes. Th. 805 Στυγὸς ἄφθιτον ὕδωρ ~ Ved. *útsa- ákṣita-* (RV 1.64.6d, 8.7.16c, 9.110.5b; AVŚ 4.27.2ab, 18.4.36ab, 3.24.4 (inf.)) and *āpo … akṣitāḥ* (AVŚ 10.6.14). Water + wind, flow, drink, sea, salt, snow, deep: everyday pairs. Water + bottom: RV *budhné apā́m* ~ πυθμήν in Aristotle and Heron only. | Imperishable water: **candidate (weak)**, a re-find of B023/B065. Not found in the held literature, but Nagy 1974 (not held) is the likely source. The rest: generic. |
| horse | Horse + cow (RV *áśvaiḥ … góbhiḥ*, Il. 23.260, OIr *ech … bó* in laws and annals), swift horses, yoking, conveying, chariot. | Swift horses: known (Watkins p. 12; Schmitt §§493–497). Horse and cow: generic wealth pair. |
| cow | Barren cow (*sterih₂-*): RV 1.116.22d *staryàm … gā́m*, 7.23.4a *staryàḥ ná gā́vaḥ* ~ Od. 10.522 = 11.30 στεῖραν βοῦν, Od. 20.186. Raw + cow: the Vedic paradox *pakvám āmā́su* (RV 1.180.3b, 3.30.14b) vs Od. 12.396 ὀπταλέα τε καὶ ὠμά (κρέα), where βοῶν goes with φωνή, so the construction is not parallel. Cows of the Sun (Od. 12 ~ RV 7.36.1b *sū́ryo gā́ḥ*). Driving cattle (OIr *táin bó*, RV *gā́ ajati*). Cows and sheep, ox, plough, yoke, milk: everyday. Speckled cow: RV *gaúḥ pŕ̥śniḥ* ~ MIr *erc*. | Barren cow: **known** at word level (Mallory–Adams ch. 11, p. 194: *ster-* 'barren', mostly said of cows). The phrase with *gʷṓws* is not stated, but it is lexical, and the contexts differ (an Aśvin miracle vs an offering). Cows of the Sun: known (West ch. 5). Cattle raid: known. Raw/cooked: not parallel. The rest: generic. |
| word | Root scan: hear + word (*ḱlew-* + *wékʷos*): RV 1.145.3b, 10.65.13c, 10.66.11c *śr̥ṇavat vácāṃsi me*; AVŚ 10.1.28 (inf.) *śṛṇu me vacaḥ*; AVP 5.26.2ab; Il. 16.236 = 14.234 ἐμὸν ἔπος ἔκλυες. Word + name: ON *nefndi vátta* (law formula), Slavic noise. | Hear my word: **candidate**, a re-find of C022 (partly known: 'hear me' in Schmitt 1967 §§396–405 and West ch. 8, where Il. 14.234 and 16.236 are cited for the 'as you heard before' topos; the cognate object is not stated). Already poetics-gifts-016. |
| sky/day | Day + night (Lat. *diem noctem*, RV *dyúbhir aktúbhiḥ*, Serbian, Lith.); Daughter of Sky; immortal gods; seat of the gods (RV *diví sádaḥ*, Eur. Ion 870 Διὸς ἕδος); pray/vow (εὔχετο Διί ~ Catull. 36.10 *uouere diuis*). | Daughter of Sky, immortal gods, seat of the gods (West ch. 3): known. The vow is not parallel: Διί vs *diuis* is root-level only, and the verbs are cognate only under a unified *h₁wegʷʰ-* (the index key). Mallory–Adams pp. 356–357 list εὔχομαι under *h₁eugʷʰ-* and *uoueō* under *wegʷʰ-*, and take the two as likely related. Day and night: generic. |
| night | Night and Dawn, dark night, night + sleep, midnight, evening, moon, stars. | As 8c: Night and Dawn known; the rest generic. |
| earth | Heaven and earth (Hitt. *nepiš tekan*, Serbian *небо земља*), 'earthly mortals' (ἐπιχθόνιοι βροτοί), the earth trembles. Celtic hits are *duine* 'person'. | Known or generic. |
| king | *h₃rēǵs* has 12,711 Indo-Iranian units but only 38 Latin, 13 Germanic and 599 Celtic (*rí*). The only collocate is king + queen. | Generic; little cross-branch material (coverage). |
| guest | Gmc, Lat. *hostis* and Slavic only. Guest + drink (Serbian *угостише пивом* ~ Plautus *hostium potitus*, which is noise), guest + house. | Generic. |
| house | Going home (Lat. *domum eat*, Hom. δῶ, Slavic *дом … идти*), house + roof, *dems potis* (RV *dámpatī* ~ Od. 19.531 δῶμα πόσιος), δῶμα περικλυτόν (Il. 1.607, Greek-internal). | *dems potis*: known. Mapping errors: Ved./MBh *√dam* 'tame' and Welsh *deint*/*neint* (below). |
| path | Wide path ~ wide sea: RV 3.54.9d *uraú pathí*, 4.26.5b, 8.68.13b, 10.107.1d, AVŚ 14.1.58cd ~ εὐρέα πόντον (Il. 6.291, 9.72; Od. 1.197, 2.295, 12.293, 12.401, 24.118). Path + go: generic. Celtic is *áit* 'place' (< *pōntH-*, Wiktionary; Mallory–Adams p. 250 agrees). | Wide path/sea: **generic**, as 8a no. 29: 'wide' is the default epithet of both nouns, and West ch. 2 calls 'broad sea' banal (with OE and Serbo-Croatian non-cognate parallels). |
| eye | Eyes and ears (Biblical and everyday), eye + brow, tears, sleep, light. OIr *enech* + *dérc*, ὀφθαλμοῖσι ἔδρακον. | Generic. |
| hand | Hand + foot (Hom. χεῖρας … πόδας; RV 1.32.7a *apā́d ahastáḥ* for Vṛtra, 10.22.14a, with no Greek parallel except Plutarch's armless and footless herms). Hand + head (Il. 24.724). Celtic is *fogas*/*focus* 'near' (Wiktionary *ǵʰóstus*, 'at hand'), not a hand word. | Generic. |
| death | Living and dead; ageless and immortal (RV *ajárā amŕ̥tā*, 1.113.13d); mortals age (RV 1.92.10d *mártasya … jaráyantī* ~ Od. 19.360 = Hes. Op. 93 βροτοὶ καταγηράσκουσιν); mortals who eat (Il. 6.142); worm (Biblical). | Ageless and immortal: known (West chs. 2–3), with Greek renewal ἀθάνατος. Mortals age: generic, and the constructions differ. |
| life | Life + years and a hundred (RV *jīváse śatám*), life + long life (*ā́yuḥ*), life + breath, 'give life'. | Generic or Indic-internal. |

## Candidates and their novelty

| Phrase | Witnesses | Cognates | Held literature | Verdict |
|---|---|---|---|---|
| *ḱlew-* + *wékʷos* + 1sg 'hear my word(s)' | RV 1.145.3b, 10.65.13c, 10.66.11c; AVŚ 10.1.28 (inf.), AVP 5.26.2ab; Il. 16.236 = 14.234 | *vácas-* = ἔπος (same neuter s-stem). The verb is root-level only (Ved. nasal present *śr̥ṇó-* vs Gk thematic aorist ἔκλυον). The possessor is root-level only (Ved. *me* vs Gk ἐμόν). | 'Hear me' is known: Schmitt 1967 §§396–405 (pp. 195–198, κλῦθί μοι ~ *śrudhí me*); West ch. 8 (prayer). With this object it is not found in the held literature (as `8c-novelty.md` C022). | Candidate; re-find of C022 |
| *n̥dʰgʷʰitós* + water word 'imperishable water' | Hes. Th. 805; RV 1.64.6d, 8.7.16c, 9.110.5b; AVŚ 4.27.2ab, 18.4.36ab, 10.6.14 | *ákṣita-* = ἄφθιτος (exact). The noun is root-level only: *útsa-* (*ud-s-o-*) vs ὕδωρ (*wód-r̥*); Ved. *ā́p-* is not cognate. | Not found in the held literature. West ch. 2 and Watkins ch. 15 treat only the fame formula and cite Nagy 1974, which we do not hold. | Candidate (weak); re-find of B023/B065 (weak). A single Greek locus, and the contexts differ (a spring that is milked vs the water of the gods' oath). |

Check on the cq2 build (current `corpora.sqlite`), with `--pair` on both builds. For hear + word
(*wekʷ-* root + *ḱlew-* root), Indo-Iranian 1445 → 1446, Slavic 28 → 28, Greek 27 → 26 and
Germanic 2 → 2; Il. 14.234 and 16.236 are still found. For imperishable water (the three water
ids + *dʰgʷʰey-*), Indo-Iranian 7 → 7 and Greek 6 → 6. Neither verdict changes.

## Mapping errors found

These are recorded in `data/research/formulas/mapping-errors-lead-expansion.jsonl` (five rows) for
the next corpus-quality batch. Mahābhārata loci there are DCS sentence labels
('MBh, 5, 123.s22'), not verse numbers. All three errors are still present, with the same counts, in the 23:50 cq2 build.

- **Ved./Epic *√dam* 'tame' keyed to *dóm* / *dem-* 'house, build'** as well as to
  *demh₂-* 'tame'. The likely cause is the homograph *dám-* 'house'. This affects 209 sa-ep
  units (lemma `dam`: *dānta-* 'tamed, self-controlled') and RV 7.6.4d, 10.74.5b
  (*damáyantam*). It made MBh *dāntau … śrutau* look like 'famous house' next to
  δῶμα περικλυτόν. Ved. *dama-* 'self-restraint' is also keyed to both *demh₂-* 'join' and
  *demh₂-* 'tame' (229 sa-ep units).
- **Welsh *deint* (pl. of *dant* 'tooth') and *neint* (pl. of *nant* 'stream', lemmatised as
  *deint*) keyed to *dm̥tós* (*dem-* 'build')**: 14 cy units.
- **OIr/MIr *focal*/*focul* 'word' keyed to *wókʷ-tlom* (*wekʷ-* 'speak')**. Matasović 2009
  (s.v. *wokʷ-*) takes the word as a loan from Lat. *vocabulum*, so it is not an inherited
  reflex. This affects 286 Celtic units, and it floods every *wekʷ-* scan in Celtic.

## Notes on coverage

- *wékʷos* is keyed as a lexeme in Greek only. Ved. *vácas-* and Av. *vacah-* reach only the
  root group, so a lexeme-level scan of 'word' misses Indo-Iranian.
- ON *munu* 'shall' (*memóne*) is a correct root-level key for *men-* 'think'. It makes 8,524
  Germanic units for 'mind', almost all of them the auxiliary, so Germanic is useless for
  this seed.
- Celtic *fogas*/*agos* 'near' keyed to *ǵʰóstus* (Wiktionary) is defensible. It makes the
  Celtic 'hand' units almost all 'near'.
- Latin has only 38 units of *rēx*, from the LASLA subset, and Avestan *sru-* with
  *vacah-* gives no hits. Absence of a king or 'hear my word' parallel in those branches
  says nothing here.

## Tier 2

No draft was written. The bar was exact cognates in ≥ 2 branches with early witnesses, and
of the phrases that meet it, the two that are not generic are already planned:
poetics-gifts-016 (hear my word) and epic-diction-008 (μένος ἠΰ). 'Barren cow' meets the bar,
but it is known at word level, and `pie-lex-sterih2s` is not usable in the engine (rule
`unknown:noun-shape`), so no plan can be realized for it. Imperishable water fails on the
noun (root-level only).
