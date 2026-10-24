# Engine sweep: athematic verbs

Family: athematic presents (root, Narten, reduplicated, nasal-infix, *-néw-*, *-néH-*), root aorists, and every cell they generate: active indicative in all persons and numbers including the dual, imperatives, the injunctive after *mē*, the short-vowel subjunctive, the optative, the middle, the participles, and the CCu/CCi glide rule. Perfects (`kind: stat`) belong to another family and were left out.

Method. I took the inventory from `Lexicon.load()` and compared cells with the handbook convention (first form in each cell) against Fortson ch. 5, Ringe 2006 ch. 2, Beekes ch. 18, Lundquist & Yates (Handbook ch. 122, §4.3–4.4) and Mallory & Adams ch. 4. The M&A tables are missing from the text extract, but its prose agrees on *-e/ont-*, *-mh₁no-* and *stí-steh₂-ti*. Then I ran well-formedness checks over all 677 specs: adjacent nuclei, resonants left unsyllabified, weak stems with no nucleus or a geminate, a glide after a vocalic segment in the 3pl, and *-éh₁/-éh₂* suffix stems. Corpus impact counts tokens in `corpus/tier3/*.jsonl` whose (lex_id, features) cell has a different first form under the proposed fix. `INJ.*` is mapped to the PST/AOR cell that `realize.py` picks, and `PTCP.*` to the PTCP cell. I checked staleness first: 12 of the 7,874 tokens in this family differ from the current engine (all of them `-omos` vs `-omes` and glide variants), so the counts measure the current engine.

All engine changes below were applied to a scratch copy of the repo. The full test suite passes: 2,246 existing tests plus the 8 new ones below. The single failure, `test_mapping_overrides.py::test_override_table_covers_the_errata`, already fails on the unmodified tree and has nothing to do with this family. The Wiktionary-convention output (`alternatives=False`) is unchanged for every verb, so `pie.crosscheck` is unaffected.

## Inventory

701 usable verb specs have a weak stem; 24 of them are perfects. That leaves 677 lexemes. Four non-ablauting athematic presents are specified with `weak: None` and a non-thematic stem, so the family has **681 lexemes** with **8,041 corpus tokens** (19.1% of the 42,017 tier-3 tokens).

| sub-type | lexemes | of which Wiktionary tables | tokens | examples |
|---|---:|---:|---:|---|
| root present (e-grade ~ zero) | ~147 | 20 | 2,638 | h₁ésti, h₁éyti, gʷʰénti, péh₂sti, h₁édti |
| Narten / fixed root accent | 3 | 2 | 50 | h₂wḗh₁ti, tḗtḱti, smḗyti (override) |
| reduplicated present | 23 | 1 (dédeh₃ti) | 209 | dédeh₃ti, dʰédʰeh₁ti, gʷígʷeh₂ti, mímenti |
| nasal infix *-né-/-n-* | 88 | 5 | 292 | linékʷti, yunégti, bʰinédti, stunédti |
| *-néH-/-n̥H-* (Sanskrit ninth class) | 92 | 8 | 232 | pl̥néh₁ti, kʷrinéh₂ti, ǵn̥néh₃ti, tl̥néh₂ti |
| *-néw-/-nu-* | 47 | 6 | 134 | ḱl̥néwti, tn̥néwti, minéwti, ksnéwti |
| derived *-éh₁-/-(e)h₂-* stative/factitive (shape rule, ablauting) | 10 | 0 | 0 | wr̥téh₁ti, dewkéh₂ti, spéḱeh₂ti |
| non-ablauting athematic present (`weak: None`) | 4 | 4 | 167 | ḱéytor, wéstor, h₁rudʰéh₁ti, néweh₂ti |
| root aorist (e-grade ~ zero) | ~263 | 15 | 4,115 | déh₃t, gʷéh₂t, gʷémt, ḱléwt, stéh₂t, dʰéh₁t |
| non-ablauting aorist | 3 | 2 | 202 | bʰúHt, h₁áyt (override), wḗǵʰst |

Three lexemes carry 22% of the family's tokens: h₁ésti (1,397), déh₃t (209) and dédeh₃ti (180). Most tokens are in the 3sg (AOR 2,238, PRS 1,058, PST 814) and IMP.2SG (626). These are strong-stem or *-dʰí* cells, and nothing below changes them.

## What is right

These cells match the handbooks and need no change.

- **Root presents, actives.** Singular full grade with root accent; dual, plural and middle zero grade with accented endings: h₁ésmi, h₁ési (h₁éssi as an alternative), h₁ésti, h₁smés, h₁sté, h₁sénti, and h₁éymi … h₁yénti. This is Fortson §5.21–5.22; L&Y §4.3.1 (*h₁s-énti*, *h₁y-énti*); Beekes §18.2.3 (*h₁éi-mi … h₁i-més … h₁y-énti*); Ringe pp. 27, 31. The 3pl takes *-énti* after an unaccented stem and *-n̥ti* after an accented one, as Ringe p. 33 states the rule. Secondary forms: h₁ésm̥, gʷʰénm̥ (1sg *-m̥* after a consonant), h₁sént, gʷʰnént. The voiced variant *-d* is listed as an alternative, following Ringe p. 20.
- **Dual.** Primary 1du *-wós*, 3du *-tés*; secondary *-wé*, *-tóm*, *-tā́m*; imperative 2du/3du *-tóm*, *-tā́m*, i.e. the secondary forms. All match Ringe's table on p. 31. See the note below on the 2du *-th₁es*.
- **Nasal infix.** Infix *-né-* in the singular, *-n-* elsewhere, inserted into the zero-grade root: linékʷti / linkʷénti, yunégti / yungénti, pl̥néh₁ti / pl̥nh₁énti, pl̥nh₁més. Sources: Fortson §5.25–5.26 (*i̯u-n-g-énti*, *pu-n-h₂-mé-*); L&Y §4.3.1; Ringe p. 28 (*li-né-kʷ- ~ li-n-kʷ-*, *tl̥-né-h₂- ~ tl̥-n-h₂-*).
- **Root aorists.** Secondary endings, full grade in the singular active, zero grade elsewhere: stéh₂t / sth₂ént, dʰéh₁t / dʰh₁ént, gʷémt / gʷmént, ḱléwt / ḱluwént. Sources: Fortson §5.46; Beekes §18.3.3 (*sth₂-ént*); L&Y §4.3.2; Ringe p. 29 (*gʷém- ~ gʷm̥-*). Root aorists without a present get IMP and SBJV from the aorist stem, which is correct.
- **Imperative.** 2sg is the zero grade + *-dʰí*, with the bare strong stem as an alternative (Fortson §5.54 Ved. *śru-dhí*; Ringe p. 31 ∅ / *-dʰí*). 3sg is strong + *-tu*; 3pl is *-éntu*, or *-n̥tu* after an accented stem; 2pl is *-té* (Fortson §5.54, Ringe p. 31, Beekes §18.8.5). Clusters such as h₁ddʰí, sddʰí and bʰudʰdʰí are unassimilated underlying forms, written that way on purpose (`phon.py` header; Ringe p. 20 also writes unassimilated clusters).
- **Injunctive with mē.** `realize.py` replaces the imperative with the augmentless PST/AOR form of the same person: mē h₁és, mē déh₃s. This fits Beekes §18.8.2 (the prohibitive takes the injunctive) and Fortson §5.44.
- **Subjunctive.** Strong stem + thematic vowel + primary endings, 1sg *-oh₂*: h₁éseti, h₁ésonti, h₁ésoh₂, yunégeti, gʷémeti. Sources: Fortson §5.55; Ringe pp. 29–30 (*h₁és-e/o-*, *li-né-kʷ-e/o-*, *gʷém-e/o-*); Beekes §18.8.3 (full grade always). The exception is the Narten type (defect E3).
- **Optative, ordinary stems.** Weak stem + *-yéh₁-* in the singular and *-ih₁-* elsewhere, 3pl *-ih₁ént*: h₁syéh₁m̥, h₁sih₁mé, h₁sih₁ént, gʷm̥yéh₁m̥, gʷmih₁mé (Ringe p. 30 *gʷm̥-yéh₁- ~ gʷm-ih₁-*). Beekes §18.8.4 has 3pl *h₁és-ih₁-n̥t*. Fortson §5.57 gives *-ent* for the 3pl in every case and excludes *-n̥t*, even after an unaccented suffix. The engine follows Fortson, which is a reasonable handbook choice.
- **Middle.** Zero grade with accented endings throughout (Fortson §5.21). Endings: *-h₂ér*, *-th₂ér*, *-tór/-ór*, *-mésdʰh₂*, *-dʰwé*, *-n̥tór/-rór*; secondary *-h₂é*, *-th₂é*, *-tó/-ó*, *-médʰh₂*, *-n̥tó/-ró*. Sources: Fortson §5.16; Ringe p. 31; L&Y §4.2 (*-ror/-ntor*, *-ro/-nto*).
- **Participles.** Active: weak stem + *-ónt-*, giving h₁sónts, gʷmónts and linkʷónts (Ringe p. 33 hysterokinetic *-ónt-/-nt-*; L&Y §4.4.1 *h₁s-ónt-*). Fortson §5.60 writes *-(e)nt-*. After an accented stem the engine gives *-n̥ts* (h₂wéh₁n̥ts). Middle: *-m̥h₁nós* (Ringe p. 33; L&Y §4.4.1; Fortson §5.60).
- **Boukólos.** linkwós and linkwé (kʷ before consonantal w), and gunuwénti for gʷunéwti (gʷ before unaccented u), follow the engine's stated boukólos convention (`phon.delabialize`, the Wiktionary module's rule). This family has no case against it.
- **CCu/CCi glide on true clusters.** ḱlu → ḱluwént / ḱluwónts (LIV), tḱi → tḱiyénti (Ved. *kṣiyánti*), ksnu → ksnuwénti, and the CCi stems skri-, wli-, ḱli-.

## Defects, ranked by corpus impact

"Tokens" means corpus tokens whose primary form changes. In the type column, *decision* marks a point where the handbooks disagree with each other or with the Wiktionary table. Each such point has a recommendation, but the integrator should confirm it.

| # | defect | type | lexemes | tokens |
|---|---|---|---:|---:|
| D1 | h₁édti 'eat' inflected as an ordinary root present; Fortson and Ringe have Narten | decision / spec | 1 | 105 |
| D5 | ḱéytor 'lies': middle 3sg/3pl ranked *-tor/-n̥tor* before the t-less *-or/-ror* that Fortson, L&Y and Beekes reconstruct for this verb | decision / engine + spec | 1 | 79 |
| D2 | dédeh₃ti (Wiktionary table) has the reduplication accent in every weak form (Ringe), not mobile (Beekes, Vedic) | decision / spec | 1 | 36 |
| D3 | 1sg secondary contracted by Stang's law (ḱlḗm, gʷḗm, h₁ḗm, stā́m); the uncontracted form that Beekes and Vedic support (stéh₂m̥, ḱléwm̥) is missing even as an alternative | decision / engine | 13 in corpus | 0 primary (24 tokens if the primary were switched) |
| D4 | bʰúHt: accented weak stem gives bʰúHn̥t, bʰúHyeh₁t; Ringe and Vedic have the suffix and ending accented | spec | 1 | 18 |
| E1 | CCu/CCi glide rule fires after a syllabic resonant (ḱl̥nuwénti for ḱl̥nwénti); glided forms also outrank the *-t-* middle | engine | 27 (+ ordering for all true-CCu stems) | 13 |
| S1 | LIV weak stems with a dropped breve or labial: h₂ur̥s, gul̥, h₂ur̥g, ul̥h₁, plus LIV-style ul, un, Hur | spec | 7 | 13 |
| E2 | optative of an accented weak stem has *-yeh₁-* in the singular and *-ih₁n̥t* in the 3pl | engine | 11 | 10 |
| E3 | Narten / s-aorist subjunctive built on the ḗ grade | engine | 3 | 3 |
| E4 | shape-rule reduplicated presents: 3pl *-énti*, which no handbook gives; full-grade optative suffix | engine | 22 | 1 |
| S2 | tétḱti (shape rule) weak stem ttḱ- | spec | 1 | 1 |
| E5 | future imperative *-tōd* on the accented strong stem | engine | all 681 | 0 |
| S3 | `_redup_weak` leaves hiatus: weuḱ, wiukʷ, yeis | classify | 3 | 0 |
| S4 | derived *-éh₁-/-(e)h₂-* statives/factitives given root ablaut (wr̥th₁-, spḱeh₂-) | spec / classify | 10 | 0 |
| S5 | junk lemmas: 3pl forms and gloss-less derived terms parsed as 3sg presents | blocklist | 8 | 0 |
| N1 | code comment cites Ringe for 2du *-th₁es*, but Ringe's table has 2du = 3du *-tés* | comment | – | 0 |

The engine changes (E1–E5, plus the D3 alternative) total **27** changed tokens. The spec items S1, S2 and D4 add 32. The decisions D1, D5 and D2 would change another 220.

---

### D1. h₁édti 'eat': ordinary or Narten (decision; 105 tokens)

- Engine (Wiktionary table): h₁édti / h₁d-, which gives h₁dénti, h₁dént, h₁ddʰí, h₁dyéh₁t and h₁dónts.
- **Ringe p. 27** gives *h₁ḗd- ~ *h₁éd-* as his Narten example of a root present. On p. 30 he gives the optative *h₁éd-ih₁-* and the subjunctive *h₁éd-e/o-*.
- **Fortson ch. 5, exercises, note 17** lists Lat. *ēs*, *ēst* 'eats' and Ved. *ad-ánti* (with *ad-* < *h₁ed-*) as evidence for the Narten type, i.e. e-grade, not zero grade, in the plural.
- L&Y §4.3 lists *h₁ed-* among the roots that form root presents, without saying which type.
- Recommendation: the handbook convention should follow Fortson and Ringe, i.e. Narten. The cost is that the Wiktionary forms (h₁dénti …) leave the cells, because an override replaces the spec. If the validator should keep them, add the Wiktionary spec to `extra_specs` instead of losing it.

```json
{"id": "pie-lex-h1edti", "spec": {"strong": "h₁ḗd", "weak": "h₁éd"}, "spec_checked": true, "note": "Narten root present: Ringe 2006 p. 27 *h₁ḗd- ~ *h₁éd-, p. 30 opt. *h₁éd-ih₁-, subj. *h₁éd-e/o-; Fortson ch. 5 exercise n. 17 (Lat. ēs, ēst; Ved. adánti with e-grade). 3sg h₁ḗdti, 3pl h₁édn̥ti, ipv. h₁éddʰi, ptcp. h₁édn̥ts (engine sweep, athematic verbs)"}
```

Changes: PRS.3SG h₁édti → h₁ḗdti (25 tokens); IMP.2SG h₁ddʰí → h₁éddʰi (22); PST.3PL h₁dént → h₁édn̥t (13); PRS.3PL h₁dénti → h₁édn̥ti (8); and so on, 105 in all. This assumes E2 and E3 are applied: then the optative is h₁édih₁t and the subjunctive stays h₁édeti.

### D5. ḱéytor 'lies': t-less middle (decision; 79 tokens)

- Engine (Wiktionary table ḱéy-, lemma ḱéytor): MID.PRS.3SG ḱéytor, MID.PST.3SG ḱéyto, MID.PRS.3PL ḱéyn̥tor, MID.PST.3PL ḱéyn̥to. The t-less forms are alternatives only.
- Handbooks: **Fortson §5.16** reconstructs 'lies' as *ḱei̯-o(-)* (CLuw. *ziyari*, Ved. *śáye*), and **§5.18** uses it as the standard example of the t-less endings. **L&Y §4.3.1** gives *ḱéy-or* 'lies'. **L&Y §4.2** (start of ch. 8 part 7) puts this verb among those that select 3pl *-ror* (Ved. *śé-re*; impf. *á-śe-ran* < *-ro*). **Beekes §18.7** (p. 273) gives *ḱéi-o*. **Ringe p. 32** says the t-less 3rd-person endings survive in a restricted set of verbs. All four books agree that this verb is t-less; only the Wiktionary lemma has *-tor*.
- The engine has no per-lexeme switch for this, so the morph.py diff adds a `VerbSpec.mid_t_less` flag (default False). With the flag set, the handbook convention moves *-o(r)* and *-ro(r)* to the front of the four 3rd-person middle cells, and *-t-* stays as the alternative. wéstor (Hitt. *wešta*, Ved. *váste*, Gk *héstai*: L&Y §4.3.1) keeps *-tor*.
- Recommendation: set the flag for ḱéytor. Changes: MID.PST.3SG ḱéyto → ḱéyo (40), MID.PRS.3SG ḱéytor → ḱéyor (26), MID.PRS.3PL ḱéyn̥tor → ḱéyror (7), MID.PST.3PL ḱéyn̥to → ḱéyro (6).

```json
{"id": "pie-lex-kjeytor", "spec": {"mid_t_less": true}, "note": "*ḱéy-or 'lies' with t-less middle 3sg *-o(r), 3pl *-ro(r): Fortson §5.16, §5.18; L&Y §4.2, §4.3.1 (Ved. śáye, śére, áśeran; CLuw. ziyari); Beekes §18.7 *ḱéi-o. The -t- forms stay as alternatives (engine sweep, athematic verbs)"}
```

### D2. dédeh₃ti: weak-stem accent (decision; 36 tokens)

- Engine (Wiktionary table): weak *dédh₃-* accented throughout, giving dédh₃mes, dédh₃te, dédh₃dʰi and dédh₃n̥ti.
- **Ringe p. 28** writes *dʰé-dʰeh₁- ~ dʰé-dʰh₁-* and *stí-steh₂- ~ stí-sth₂-*, i.e. fixed accent on the reduplication. The Wiktionary table matches this.
- **Beekes §18.1.3** gives *dʰé-dʰh₁-n̥ti* beside 1pl *dʰi-dʰh₁-mé*. **§18.2.3** gives *bʰé-bʰer-mi*, 1pl *bʰi-bʰr̥-més*, 3pl *bʰé-bʰr̥-n̥ti*: the accent is mobile and only the 3pl has the static pattern. Vedic agrees: *dadmás* and *daddhí* beside *dádati*. **Fortson §5.27** gives *de-deh₃-* in the singular, *de-dh₃-* elsewhere and 3pl *de-dh₃-n̥ti*, without marking the accent.
- After E4, the shape-rule reduplicated presents (dʰédʰeh₁ti and 21 others) follow Beekes and Vedic. Recommendation: make dédeh₃ti the same, so that the family is consistent. Ringe's forms survive as the Wiktionary-convention alternatives. The 3pl stays dédh₃n̥ti through E4.

```json
{"id": "pie-lex-dedeh3ti", "spec": {"weak": "dedh₃"}, "note": "mobile accent in the weak stem, 3pl on the reduplication: Beekes §18.1.3, §18.2.3 (*dʰi-dʰh₁-mé, *bʰi-bʰr̥-més vs 3pl *dʰé-dʰh₁-n̥ti); Ved. dadmás, daddhí, dádati; Fortson §5.27 *de-dh₃-n̥ti. Ringe 2006 p. 28 has fixed *dʰé-dʰh₁-; that is the Wiktionary table, kept as the alternative convention. Needs the engine fix for reduplicated 3pl (engine sweep, athematic verbs)"}
```

Changes: IMP.2SG dédh₃dʰi → dedh₃dʰí (20 tokens); PRS.1PL dédh₃mes → dedh₃més (9); PRS.2PL and IMP.2PL dédh₃te → dedh₃té (5); IMP.3DU (1); OPT (1). 36 in all.

### D3. 1sg secondary and Stang's law (decision; 0 tokens as proposed, 24 if switched)

- Engine: the 1sg *-m̥* is contracted after *-ew-, -ey-, -em-, -eh₂-*, giving ḱlḗm, h₁ḗm, gʷḗm, trḗm, stā́m, gʷā́m and ḱr̥snā́m. The uncontracted form is missing even as an alternative.
- **Ringe p. 21** states Stang's law for word-final *-Vmm, -Vwm, -Vh₂m*, with nominal examples only (*dṓm*, *dyḗm*, *-ām*). **Beekes §18.3.3** writes the aorist 1sg as *h₁é-steh₂-m*, uncontracted. Vedic has *ásthām* but also *áśravam* and *ágamam*; Greek has ἔχευα < *é-ǵʰew-m̥*. The nominal handbook convention in `_eh2` keeps *-eh₂m* uncontracted, while the verbal one contracts it.
- Recommendation: keep the primary forms. They are Ringe-consistent and tested (`tests/test_morph.py:76`). Add the uncontracted form as an alternative so that the validator matches texts that write it. That is the last hunk of the morph.py diff, and it changes 0 primary tokens. If the integrator prefers consistency with the nominal *-eh₂m*, put the uncontracted form first for *-eh₂-* stems instead (11 tokens: gʷā́m 3, ḱr̥snā́m 3, stā́m 1, bʰā́m 1, yā́m 1, km̥Hnā́m 1, tl̥nā́m 1).

### D4. bʰúHt 'became' (spec; 18 tokens)

- Engine (Wiktionary table): strong = weak = *bʰúH-* with the accent fixed on the root, giving bʰúHn̥t, bʰúHtām, bʰúHdʰi, bʰúHyeh₁t and bʰúHih₁n̥t.
- **Ringe p. 30**: the optative is *bʰuh₂-yéh₁- ~ bʰuh₂-ih₁-* and the subjunctive *bʰúh₂-e/o-*, i.e. the stem is unaccented outside the singular indicative. Vedic agrees: *ábhūvan* (3pl *-an* < *-ent*; Beekes §18.3.3), *ábhūma*, *bhūyā́t*.
- The strong stem *bʰúH-* stays, so bʰúHt, bʰúHs, bʰúHm̥ and the subjunctive bʰúHeti are unchanged.

```json
{"id": "pie-lex-bhuHt", "spec": {"weak": "bʰuH"}, "note": "non-ablauting root aorist, but unaccented outside the sg. act.: Ringe 2006 p. 30 opt. *bʰuh₂-yéh₁- ~ *bʰuh₂-ih₁-; Ved. ábhūvan, ábhūma, bhūyā́t. 3pl bʰuHént, opt. bʰuHyéh₁t (engine sweep, athematic verbs)"}
```

Changes: OPT.3SG bʰúHyeh₁t → bʰuHyéh₁t (5); AOR.3DU bʰúHtām → bʰuHtā́m (4); IMP.2SG bʰúHdʰi → bʰuHdʰí (4); AOR.3PL bʰúHn̥t → bʰuHént (3); OPT.3PL (1); OPT.2DU (1).

### E1. Glide rule after a syllabic resonant (engine; 27 lexemes, 13 tokens)

- `_handbook_verbal` applies the CCu/CCi rule when `wk[-2].kind != "V" and wk[-3].kind != "V"`. Syllabic l̥, n̥, r̥, i and u have kind `R`, so stems ending in VCu also match. Examples: ḱl̥-nu, tn̥-nu, gʷʰr̥-nu, mi-nu, ǵʰi-nu, dʰu-nu, tr̥h₂-u, dʰn̥h₂-u, kl̥h₂-u, ḱl̥-ni, h₂r̥h₁-i, and 27 lexemes in all. They get ḱl̥nuwénti, tn̥nuwénti, minuwénti, tr̥h₂uwénti and ḱl̥niyénti.
- Handbooks: **L&Y §4.3.1** *ḱl̥-né-w-ti, ḱl̥-n-w-énti*; **Ringe p. 28** weak *tn̥-nw-*, **p. 30** opt. *tn̥-nw-ih₁-*; Fortson §5.26 Ved. *tanvánti*. Vedic also has *śr̥ṇvánti* and *minvánti*. The plain junction output (ḱl̥nwénti) was right, and the rule overwrites it.
- Second bug in the same block: `out[k] = _uniq(new + forms)` puts every glided form at the head of its cell. This applies even to true CCu stems, so the t-less middle comes first: MID.AOR.3SG of ḱléwt is ḱluwó, not ḱlutó, and MID.PRS.3SG of ksnéwti is ksnuwór, not ksnutór. That contradicts the engine's own ranking (*-tó* before *-ó*; Ringe p. 31; L&Y §4.2).
- Fix: first hunk of the morph.py diff (`not wk[-3].vocalic`, with the glided form inserted in place). The misfired forms drop out of the cells entirely, since no handbook writes them.
- Changes: ḱl̥néwti PRS/PST.3PL (5), ḱl̥néyti MID.PST.3SG ḱl̥niyó → ḱl̥nitó (4), ḱléwt MID.AOR.3SG (1), gʷʰr̥néwti (1), térh₂uti (1), tn̥néwti PTCP (1).

### S1. LIV weak stems with a dropped breve (spec; 13 tokens)

`pie/liv.py::_aorist_lexemes` copies LIV's printed weak stem (`source_ref.stem`). In four cases the transcription has lost the breve of *u̯* or the labial of *gᵘ̯*, which leaves two adjacent nuclei:

| lexeme | LIV stem as transcribed | current weak | fix | tokens |
|---|---|---|---|---:|
| pie-lex-h2werst 'rain' | *h₂u̯érs-/h₂ur̥s- (p. 291) | h₂ur̥s (h₂ur̥syéh₁t, h₂ur̥sdʰí) | h₂wr̥s | 11 |
| pie-lex-h2wergt-2 'turn' | *h₂u̯érg-/h₂ur̥g- (p. 290) | h₂ur̥g | h₂wr̥g | 0 |
| pie-lex-welh1t-2 'choose' | *u̯élh₁-/ul̥h₁- (p. 677) | ul̥h₁ | wl̥h₁ | 0 |
| pie-lex-gwelt 'swallow' | *gu̯él-/gul̥- (p. 192) | gul̥ | gʷl̥ (the strong stem is already gʷél-) | 0 |
| pie-lex-went 'overpower' | *u̯én-/un- (p. 680) | un (undʰí, unyéh₁s) | wn̥ | 2 |
| pie-lex-welt 'turn, roll' | *u̯él-/ul- (p. 675) | ul | wl̥ | 0 |
| pie-lex-Hwert 'enclose' | *Hu̯ér-/Hur- (p. 227) | Hur | Hwr̥ | 0 |

The last three are genuine LIV notation for the prevocalic shape, as LIV's reduplicated aorist *He-Hur-e-* shows. As fixed strings, though, they give *unmé*, *undʰí*, *ulmé*. The engine's own zero grade (wn̥, wl̥, Hwr̥) gives *wn̥mé* before a consonant and, through `join`, *unént* before a vowel, so it covers both shapes. The same correction belongs in `_aorist_lexemes`: replace the transcribed weak stem with `classify.zero_grade(strong)` whenever the two differ only in syllabicity. These override lines fix the current data:

```json
{"id": "pie-lex-h2werst", "spec": {"weak": "h₂wr̥s"}, "note": "LIV² p. 291, transcribed *h₂u̯érs-/h₂ur̥s-: the weak stem has two adjacent nuclei (a lost breve); read h₂u̯r̥s- (engine sweep, athematic verbs)"}
{"id": "pie-lex-h2wergt-2", "spec": {"weak": "h₂wr̥g"}, "note": "LIV² p. 290, transcribed *h₂u̯érg-/h₂ur̥g-: two adjacent nuclei (a lost breve); read h₂u̯r̥g- (engine sweep, athematic verbs)"}
{"id": "pie-lex-welh1t-2", "spec": {"weak": "wl̥h₁"}, "note": "LIV² p. 677, transcribed *u̯élh₁-/ul̥h₁-: two adjacent nuclei; read u̯l̥h₁- (engine sweep, athematic verbs)"}
{"id": "pie-lex-gwelt", "spec": {"weak": "gʷl̥"}, "note": "LIV² p. 192, transcribed *gu̯él-/gul̥-: the weak stem lost the labiovelar (the strong stem is already gʷél-) (engine sweep, athematic verbs)"}
{"id": "pie-lex-went", "spec": {"weak": "wn̥"}, "note": "LIV² p. 680 *u̯én-/un-: LIV prints the prevocalic shape; the engine's zero grade wn̥- gives unént before a vowel and wn̥- before a consonant (wn̥dʰí, not undʰí) (engine sweep, athematic verbs)"}
{"id": "pie-lex-welt", "spec": {"weak": "wl̥"}, "note": "LIV² p. 675 *u̯él-/ul-: prevocalic shape; wl̥- syllabifies for both environments (engine sweep, athematic verbs)"}
{"id": "pie-lex-Hwert", "spec": {"weak": "Hwr̥"}, "note": "LIV² p. 227 *Hu̯ér-/Hur-: prevocalic shape; Hwr̥- syllabifies for both environments (engine sweep, athematic verbs)"}
```

### E2. Optative of an accented weak stem (engine; 11 lexemes, 10 tokens)

- Engine: when the weak stem is accented, as in Narten h₂wéh₁-, smḗy- and tétḱ-, fixed-accent dédh₃-, s-aorist wéǵʰs-, non-ablauting bʰúH- and h₁áy-, and the `weak: None` presents h₁rudʰéh₁-, néweh₂-, ḱéy- and wés-, the singular still takes *-yeh₁-* (h₂wéh₁yeh₁m̥, dédh₃yeh₁t). The 3pl is changed to *-ih₁n̥t* (dédh₃ih₁n̥t).
- **Fortson §5.57**: Narten presents have the zero-grade suffix *-ih₁-* throughout, and the 3pl is always *-ent*, never *-n̥t*, even when unaccented. **Ringe p. 30**: *h₁éd-ih₁-*, *dʰé-dʰh₁-ih₁-*, *stí-sth₂-ih₁-*, *déyḱ-s-ih₁-*, and with a question mark *h₁rudʰ-éh₁-ih₁-* and *néwe-h₂-ih₁-*, i.e. only the zero-grade suffix when the accent is fixed to the left. **Beekes §18.8.4**: reduplicated optatives have the zero-grade suffix everywhere (Av. *daidīt* < *dʰe-dʰh₁-ih₁-t*). Beekes writes 3pl *-ih₁-n̥t*, so there is a disagreement over the 3pl ending. The handbook convention already follows Fortson's *-ent* for ordinary stems, and this fix extends that to accented stems.
- Fix: the optative hunk of the morph.py diff, which also covers reduplicated stems with an unaccented weak stem, so that dʰedʰh₁ih₁t follows Beekes. The full-grade *-yeh₁-* forms stay as alternatives, and the Wiktionary module keeps *-ih₁n̥t*.
- Perfects are excluded (`spec.kind != "stat"`), so the patch does not touch the perfect family.
- Changes: bʰúHt OPT.3SG/3PL (6; superseded by D4 if that is applied), dédeh₃ti OPT.3SG/3PL (2), h₁rudʰéh₁ti OPT.3SG/3PL (2).

### E3. Narten / s-aorist subjunctive (engine; 3 lexemes, 3 tokens)

- Engine: the subjunctive is built on the strong stem even when that stem has the lengthened grade, giving h₂wḗh₁eti, tḗtḱomes and wḗǵʰseti.
- **Ringe p. 30**: the subjunctive takes the e-grade of the stem, so *h₁éd-e/o-* to *h₁ḗd-*, and the s-aorist *déyḱ-s-e/o-* to *dḗyḱ-s-*. For these stems the e-grade is the accented weak stem.
- Fix: the subjunctive hunk of the morph.py diff (`sbjv = weak` when the strong stem has an accented long vowel and the weak stem is accented). Changes: h₂wḗh₁ti SBJV.1SG and SBJV.3SG (2), tḗtḱti SBJV.1PL (1).

### E4. Reduplicated presents from the shape rule (engine; 22 lexemes, 1 token)

- `classify._redup_weak` takes the accent off the reduplication: dʰédʰeh₁- / dʰedʰh₁-. The general rule then gives 3pl dʰedʰh₁énti, dʰedʰh₁ént, dʰedʰh₁éntu and dʰedʰh₁n̥tór. **No handbook has *-énti* in this type.** Fortson §5.27 gives *de-dh₃-n̥ti*. Beekes §18.1.3 and §18.2.3 give *dʰé-dʰh₁-n̥ti* and *bʰé-bʰr̥-n̥ti* (static 3pl). Ringe pp. 28 and 33 has an accented stem, hence *-n̥ti*. Vedic agrees: *dádhati*, *bíbhrati*, middle *dádhate*.
- The 1pl, 2pl and dual forms with ending accent (dʰedʰh₁més) are right by Beekes and Vedic (*dadhmás*). See D2 for Ringe's dissent.
- The optative takes the zero-grade suffix throughout (Beekes §18.8.4; Ringe p. 30), covered by E2.
- Fix: `_redup_weak_accented` and the `red` branches in `_conjugate` and `_phase_b`. The 3pl active (PRS, PST, IMP) and middle (MID.PRS, MID.PST) take the reduplication accent with *-n̥ti/-n̥t/-n̥tu/-n̥tor/-n̥to*. The participle gets dʰédʰh₁n̥ts (Ved. *dádhat-*) as an alternative, and dʰedʰh₁ónts stays first because Fortson §5.60 writes *dʰe-dʰh₁-(e)nt-*. Changes: dʰédʰeh₁ti PRS.3PL (1). The 22 lexemes: dʰédʰeh₁ti, dédeḱti, dʰédʰoh₁ti, dʰídʰerti, dʰídʰeyh₂ti, dídreh₂ti, gʰégʰromti, ǵʰéǵʰeh₁ti, gʷígʷeh₂ti, h₁íh₁eyǵʰti, léloydti, mímenti, pípleh₁ti, píporti, pípréh₁ti, síselti, títerh₂ti, wéwoḱti, wéwolHti, wíwekʷti, wíweysti, yéyesti. The rule does not fire for dédeh₃ti (accented weak stem), tétḱti or h₁éh₁sti (no reduplication match).

### S2. tétḱti (shape rule; 1 token)

- `_redup_weak` returns None for tétḱ- (no e/o in the "root" tḱ). `zero_grade` then deletes the only vowel, giving ttḱ-: ttḱénti, ttḱént.
- **Ringe p. 20**: 3pl *tétḱ-n̥ti* (Ved. *tákṣati*) beside 3sg *tḗtḱ-ti*, i.e. a Narten/acrostatic root. The table lexeme pie-lex-textkjti already has tḗtḱ- / tétḱ-.

```json
{"id": "pie-lex-tetkjti", "spec": {"weak": "tétḱ"}, "note": "acrostatic root *tetḱ-: Ringe 2006 p. 20 3pl *tétḱ-n̥ti (Ved. tákṣati); the shape rule's ttḱ- deleted the root's only vowel; cf. the Narten table lexeme pie-lex-textkjti (engine sweep, athematic verbs)"}
```

### E5. Future imperative *-tōd* (engine; 0 tokens)

- Engine: strong stem + *-tōd*, unaccented, giving h₁éstōd, gʷʰéntōd and déh₃tōd.
- Handbooks: for the zero grade, **Fortson §5.54** cites Ved. *dhattāt* (the zero-grade reduplicated stem *dhat-*), and **Beekes §18.8.5** gives Ved. *i-tā́t*, Gk *í-tō*, Lat. *itō*. For the accent, **Ringe p. 31** has *-tṓd*, and Beekes's *i-tā́t* is accented on the ending. So the ending takes the zero-grade stem, accented: h₁stṓd, h₁itṓd. Fix: the IMP.FUT hunk, with the strong-stem form kept as an alternative. No corpus tokens.

### S3. `_redup_weak` hiatus (classify; 3 lexemes, 0 tokens)

- The root is zero-graded apart from the reduplication, so a glide next to the deleted vowel never sees the reduplication vowel. The results have two nuclei in hiatus: wéwoḱ → weuḱ (we-uḱ), wíwekʷ → wiukʷ and yéyes → yeis.
- Fix: zero-grade the whole sequence with the reduplication deaccented (classify.py diff below), which gives wewḱ, wiwkʷ and yeys. The other 21 reduplicated stems come out unchanged (checked). Re-run `scripts/classify_lexicon.py` to regenerate `inflection_specs.jsonl`. Without a regeneration, use these override lines:

```json
{"id": "pie-lex-wewokjti", "spec": {"weak": "wewḱ"}, "note": "reduplicated present: the zero grade beside the reduplication vowel is a glide (we-wḱ-), not hiatus weuḱ- (engine sweep, athematic verbs)"}
{"id": "pie-lex-wiwekwti", "spec": {"weak": "wiwkʷ"}, "note": "reduplicated present: wi-wkʷ-, not hiatus wiukʷ- (engine sweep, athematic verbs)"}
{"id": "pie-lex-yeyesti", "spec": {"weak": "yeys"}, "note": "reduplicated present: ye-ys-, not hiatus yeis- (engine sweep, athematic verbs)"}
```

### S4. Derived statives and factitives given root ablaut (10 lexemes, 0 tokens)

- The shape rule zero-grades the first accented e/o, which here is the suffix vowel or the root vowel of a non-ablauting derived stem. That gives wr̥téh₁- / wr̥th₁-, skn̥déh₁- / skn̥dh₁-, kewkéh₁- / kewkh₁-, kswibʰéh₁- / kswibʰh₁-, ḱl̥wéh₁- / ḱl̥wh₁-, dewkéh₂- / dewkh₂-, seykʷéh₂- / seykʷh₂-, woyh₁éh₂- / woyh₁h₂-, spéḱeh₂- / spḱeh₂- and stéh₂weh₂- / sth₂weh₂-.
- **Ringe pp. 28 and 30**: statives in *-éh₁-* (*h₁rudʰ-éh₁-*) and factitives in *-h₂-* (*néwe-h₂-*) are athematic but non-ablauting; their subjunctive is built on the invariant stem.
- Disagreement: **L&Y §4.3.1** treats the productive stative as thematic *-eh₁-ye/o-* and reports that LIV's athematic *-éh₁-* fientive is disputed.
- Recommendation: set weak = strong, i.e. non-ablauting, which yields 3pl wr̥téh₁n̥ti. Better still, block these lexemes. All are gloss-less Wiktionary derived terms (`meaning: []`, apart from 'eh₁-stative' and '*eh₂-stative') with no corpus use. Override lines for weak = strong:

```json
{"id": "pie-lex-wrteh1ti", "spec": {"weak": "wr̥téh₁"}, "note": "stative in *-éh₁-, non-ablauting: Ringe 2006 pp. 28, 30 (*h₁rudʰ-éh₁-); not root ablaut wr̥th₁- (engine sweep, athematic verbs)"}
{"id": "pie-lex-skndeh1ti", "spec": {"weak": "skn̥déh₁"}, "note": "stative in *-éh₁-, non-ablauting (Ringe 2006 pp. 28, 30) (engine sweep, athematic verbs)"}
{"id": "pie-lex-kewkeh1ti", "spec": {"weak": "kewkéh₁"}, "note": "stative in *-éh₁-, non-ablauting (Ringe 2006 pp. 28, 30) (engine sweep, athematic verbs)"}
{"id": "pie-lex-kswibheh1ti", "spec": {"weak": "kswibʰéh₁"}, "note": "stative in *-éh₁-, non-ablauting (Ringe 2006 pp. 28, 30) (engine sweep, athematic verbs)"}
{"id": "pie-lex-kjlweh1ti", "spec": {"weak": "ḱl̥wéh₁"}, "note": "stative in *-éh₁-, non-ablauting (Ringe 2006 pp. 28, 30) (engine sweep, athematic verbs)"}
{"id": "pie-lex-dewkeh2ti", "spec": {"weak": "dewkéh₂"}, "note": "*-(e)h₂- verb, non-ablauting like the factitive *néwe-h₂- (Ringe 2006 pp. 28, 30) (engine sweep, athematic verbs)"}
{"id": "pie-lex-seykweh2ti", "spec": {"weak": "seykʷéh₂"}, "note": "*-eh₂- stative, non-ablauting (Ringe 2006 pp. 28, 30) (engine sweep, athematic verbs)"}
{"id": "pie-lex-woyh1eh2ti", "spec": {"weak": "woyh₁éh₂"}, "note": "*-eh₂- verb, non-ablauting (Ringe 2006 pp. 28, 30) (engine sweep, athematic verbs)"}
{"id": "pie-lex-spekjeh2ti", "spec": {"weak": "spéḱeh₂"}, "note": "factitive-type *-e-h₂- on a full-grade root, non-ablauting (Ringe 2006 p. 28 *néwe-h₂-); the shape rule zero-graded the root (spḱeh₂-) (engine sweep, athematic verbs)"}
{"id": "pie-lex-steh2weh2ti", "spec": {"weak": "stéh₂weh₂"}, "note": "*-e-h₂- verb, non-ablauting (Ringe 2006 p. 28); not sth₂weh₂- (engine sweep, athematic verbs)"}
```

The same applies to bʰégʷyeh₂ti, bʰéh₃geh₂ti and ǵʰéydʰyeh₂ti (also gloss-less, 0 tokens). A classify rule could do this generally: a stem ending in *-é?h₁/-é?h₂* that is longer than a CeH root gets weak = strong. I have not drafted it, because the 0-token count does not justify the risk to real CeH roots (déh₁-, stéh₂-, pléh₁-).

### S5. Junk lemmas (0 tokens)

Two groups should go on a blocklist rather than be fixed:

- **3pl forms parsed as 3sg:** ih₁énti, minwénti, stringénti, plénh₁ónti, gowh₂dʰyónti.
- **Gloss-less pages that yield odd stems:** méyh₁wti → mih₁w-, wéh₁yti → uh₁y-, and h₁éh₁sti → weak h₁h₁s-, which should be the non-ablauting *h₁ḗs-*; see L&Y §4.3.1, citing Melchert, *h₁ḗs-ti / h₁és-n̥ti*.

None are used. Suggested lines for `data/generation/blocklist.jsonl` (field names as `realize.py` reads them):

```json
{"lex_id": "pie-lex-ih1enti", "reason": "lemma is a 3pl form (-énti); the shape rule parses it as a 3sg stem ih₁én-"}
{"lex_id": "pie-lex-minwenti", "reason": "lemma is a 3pl form of minéwti"}
{"lex_id": "pie-lex-stringenti", "reason": "lemma is a 3pl form; stem stringén- is spurious"}
{"lex_id": "pie-lex-plenh1onti", "reason": "lemma is a participle/3pl form; stem plénh₁ón- is spurious"}
{"lex_id": "pie-lex-gowh2dhyonti", "reason": "lemma is a 3pl form; stem gowh₂dʰyón- is spurious"}
```

### N1. 2du primary *-th₁es* citation (0 behaviour change)

`_handbook_verbal` puts 2du *-th₁es* first and cites Ringe for it. Ringe's table on p. 31 has *-tés* for both the 2du and the 3du. The distinction is Vedic (*-thas* vs *-tas*), and the closest handbook form is Beekes §18.2.3, who writes 2pl *-th₁é*. The forms can stay, with the comment changed to cite Beekes and Vedic. 6 corpus tokens are in PRS.2DU.

---

## Proposed code changes

### pie/morph.py (E1–E5, D3 alternative, D5 field)

```diff
--- a/pie/morph.py
+++ b/pie/morph.py
@@ -428,6 +428,7 @@
     strong: str
     weak: str | None = None
     kind: str = "impf"
+    mid_t_less: bool = False   # middle 3sg *-o(r), 3pl *-ro(r) first (*ḱéy-or 'lies': Fortson §5.16, L&Y §4.3.1)
 
     @property
     def thematic(self) -> bool:
@@ -502,16 +503,23 @@
             out[k] = _uniq([re.sub("t([eé])s$", lambda m: "th₁" + m[1] + "s", f) for f in out[k]] + out[k])
     # *CCu-/CCi- before a vowel keeps the vowel with a glide (Sievers/Lindeman; LIV ḱluwónt-, not ḱl̥wónt-):
     # the junction rule would vocalize the liquid instead (ḱlu+ént → ḱl̥wént)
+    # Only a true CC cluster counts: after a syllabic resonant (ḱl̥-nu-, tn̥-nu-, mi-nu-, tr̥h₂-u-) the
+    # stem ends in VCu and takes the plain glide (L&Y §4.3.1 *ḱl̥-n-w-énti; Ringe 2006 p. 28 *tn̥-nw-).
     wk = _p(_bare(spec.weak or ""))
     if (not spec.thematic and len(wk) > 2 and wk[-1].base in ("w", "y") and wk[-1].syl
-            and wk[-2].kind != "V" and wk[-3].kind != "V" and wk[-2].base not in ("w", "y")):
+            and not wk[-2].vocalic and not wk[-3].vocalic and wk[-2].base not in ("w", "y")):
         bad = render(join(wk, _p("e")))[:-1]
         good = render(wk) + wk[-1].base
         if bad != good:
             for k, forms in out.items():
-                new = [good + f[len(bad):] for f in forms if f.startswith(bad)]
-                if new:
-                    out[k] = _uniq(new + forms)
+                # the glided form takes the place of the form it rewrites; the ranking of
+                # the cell's alternatives (-tór before -ór, ...) is kept
+                new = []
+                for f in forms:
+                    if f.startswith(bad):
+                        new.append(good + f[len(bad):])
+                    new.append(f)
+                out[k] = _uniq(new)
     st = _p(_bare(spec.strong))
     if not spec.thematic and st and st[-1].base == "s" and st[-1].kind == "C" and "PRS.2SG" in out:
         out["PRS.2SG"] = _uniq(out["PRS.2SG"] + [render(st) + "si"])
@@ -583,34 +591,83 @@
 
     strong = fix(_p(_bare(spec.strong)))
     weak = fix(_p(_bare(spec.weak or spec.strong)))
+    hb = conv == "handbook"
+    red = _redup_weak_accented(strong, weak) if (hb and spec.kind == "impf") else None
 
     def on(stem, e: str) -> str:
-        if has_accent(stem) and e in ("ih₁ént", "ónts"):
-            e = {"ih₁ént": "ih₁n̥t", "ónts": "n̥ts"}[e]   # accented stem: zero-grade -n̥t (bʰúHih₁n̥t, h₁édn̥ts)
+        if has_accent(stem) and e == "ónts":
+            e = "n̥ts"   # accented stem: zero-grade -n̥t (h₂wéh₁n̥ts)
+        if has_accent(stem) and e == "ih₁ént" and (not hb or spec.kind == "stat"):
+            e = "ih₁n̥t"   # Wiktionary module; the handbook keeps -ent (Fortson §5.57)
         return render(fix(join(stem, _p(e))))
 
-    # subjunctive stem: the strong stem, e-grade in the perfect (wóyd- → wéyd-)
+    # subjunctive stem: the strong stem, e-grade in the perfect (wóyd- → wéyd-); a Narten / s-aorist stem
+    # (ḗ in the singular, accented é elsewhere) takes the e-grade, i.e. the weak stem (Ringe 2006 p. 30:
+    # *h₁éd-e/o- to *h₁ḗd-, *déyḱ-s-e/o- to *dḗyḱ-s-)
     sbjv = [replace(x, base="e") if (spec.kind == "stat" and x.kind == "V" and x.base == "o" and x.acc) else x
             for x in strong]
+    if hb and has_accent(weak) and any(x.long and x.acc for x in strong):
+        sbjv = weak
     out.update(_slots("SBJV", _SH_SBJV, lambda e: on(sbjv, e)))
-    out.update({k: v for k, v in _slots("OPT", [*_ATH_OPT_SG, *_ATH_OPT_PL], lambda e: on(weak, e)).items()})
+    # optative: *-yéh₁-/-ih₁- on the weak stem; when the weak stem is accented (Narten, fixed-accent
+    # reduplication, s-aorist) or the stem is reduplicated, the suffix is zero-grade throughout
+    # (Fortson §5.57; Ringe 2006 p. 30 *h₁éd-ih₁-, *dʰé-dʰh₁-ih₁-; Beekes §18.8.4 *dʰe-dʰh₁-ih₁-t)
+    zero_opt = hb and spec.kind != "stat" and (has_accent(weak) or red is not None)
+    if zero_opt:
+        opt_sg = ["ih₁m̥", "ih₁s", "ih₁t"]
+    else:
+        opt_sg = _ATH_OPT_SG
+    out.update({k: v for k, v in _slots("OPT", [*opt_sg, *_ATH_OPT_PL], lambda e: on(weak, e)).items()})
+    if zero_opt:   # the full-grade-suffix form stays as an alternative
+        for pn, e in zip(_P[:3], _ATH_OPT_SG):
+            out[f"OPT.{pn}"] = _uniq(out[f"OPT.{pn}"] + [on(weak, e)])
     if spec.kind == "stat":
         out["PTCP.ACT"] = [on(weak, "wṓs")]
         return out
     if spec.kind == "impf":
         out.update(_slots("MID.PRS", _ATH_MID_PRS, lambda e: on(weak, e)))
     out.update(_slots("MID.PST" if spec.kind == "impf" else "MID.AOR", _ATH_MID_PST, lambda e: on(weak, e)))
+    if red is not None:
+        # reduplicated present, middle 3pl: accent on the reduplication, *-n̥to(r) (Ved. dádhate, dádhata)
+        for k, e in (("MID.PRS.3PL", "n̥tór"), ("MID.PST.3PL", "n̥tó")):
+            if k in out:
+                out[k] = _uniq([on(red, e)] + out[k])
+    if hb and spec.mid_t_less:
+        for k in ("MID.PRS.3SG", "MID.PST.3SG", "MID.AOR.3SG", "MID.PRS.3PL", "MID.PST.3PL", "MID.AOR.3PL"):
+            if k in out and len(out[k]) > 1:
+                out[k] = out[k][1:] + out[k][:1]   # [-tór, -ór] → [-ór, -tór]; [-n̥tór, -rór] → [-rór, -n̥tór]
     if conv == "handbook":
-        out["IMP.FUT.2SG"] = out["IMP.FUT.3SG"] = [on(strong, "tōd")]
+        # *-tṓd on the zero-grade stem, accented (zero grade: Fortson §5.54 Ved. dhattāt; accent: Ringe 2006 p. 31
+        # *-tṓd, Beekes §18.8.5 Ved. itā́t); the strong-stem form stays as an alternative
+        out["IMP.FUT.2SG"] = out["IMP.FUT.3SG"] = _uniq([on(weak, "tṓd"), on(strong, "tōd")])
     out["MID.IMP.2SG"] = [on(weak, "só")]
     out["MID.IMP.2PL"] = [on(weak, "dʰh₂wé")]
     out.update(_slots("MID.SBJV", _SH_MID_SBJV, lambda e: on(sbjv, e)))
     out.update(_slots("MID.OPT", _ATH_MID_OPT, lambda e: on(weak, e)))
-    out["PTCP.ACT"] = [on(weak, "ónts")]
+    out["PTCP.ACT"] = [on(weak, "ónts")] + ([on(red, "n̥ts")] if red is not None else [])   # Ved. dádhat-
     out["PTCP.MID"] = [on(weak, "m̥h₁nós")]
     return out
 
 
+def _redup_weak_accented(strong: list[Seg], weak: list[Seg]) -> list[Seg] | None:
+    """Athematic reduplicated present with an unaccented weak stem (dʰédʰeh₁- / dʰedʰh₁-): the weak stem
+    with the accent on the reduplication vowel (dʰédʰh₁-), which the 3pl takes before *-n̥ti (Fortson §5.27
+    *de-dh₃-n̥ti; Beekes §18.1.3, §18.2.3 *dʰé-dʰh₁-n̥ti, *bʰé-bʰr̥-n̥ti; Ved. dádhati). None otherwise."""
+    if has_accent(weak) or len(strong) < 4 or len(weak) < 3:
+        return None
+    for n in (1, 2):   # Ce-, and sCe-/HCe- (Beekes §18.1.3 *sti-st(e)h₂-)
+        if len(strong) <= 2 * n + 1:
+            continue
+        v = strong[n]
+        if not (v.acc and ((v.kind == "V" and v.base == "e") or (v.syl and v.base == "y"))):
+            continue
+        if all(x.kind != "V" and not x.syl for x in strong[:n]) \
+                and [x.base for x in strong[:n]] == [x.base for x in strong[n + 1:2 * n + 1]] \
+                and [x.base for x in weak[:n + 1]] == [x.base for x in strong[:n + 1]]:
+            return weak[:n] + [replace(weak[n], acc=True)] + weak[n + 1:]
+    return None
+
+
 def _conjugate(spec: VerbSpec, conv: str) -> Cells:
     wk = conv == "wiktionary"
     fix = pinault if wk else (lambda x: x)
@@ -638,6 +695,8 @@
     strong = fix(_p(_bare(spec.strong)))
     weak = fix(_p(_bare(spec.weak or spec.strong)))
     weak_acc = has_accent(weak)
+    # reduplicated present: the 3pl accents the reduplication and takes *-n̥ti (dʰédʰh₁n̥ti; see _redup_weak_accented)
+    red = _redup_weak_accented(strong, weak) if (not wk and spec.kind == "impf") else None
 
     def sg_or_pl(i: int, e: str) -> str:
         st = strong if i < 3 else weak
@@ -645,6 +704,8 @@
             st = junction_laryngeal_loss(st, _p(e))
         if weak_acc and e.startswith("én"):
             e = e[1:]   # accented stem: zero-grade 3pl -n̥t(i) (bʰúHn̥t)
+        elif red is not None and e.startswith("én"):
+            st, e = red, e[1:]
         if e == "m":
             # 1sg secondary is -m̥, syllabic even after a vowel (ném̥, h₁ésm̥, térh₂wm̥),
             # with contractions: -em-m̥ → -ḗm, -ey/-ew-m̥ → -ḗm (Stang), -eh₂-m̥ → -ām
@@ -667,13 +728,24 @@
         tense = "PST" if spec.kind == "impf" else "AOR"
         for i, (pn, e) in enumerate(zip(PERSONS, _ATH_PST)):
             out[f"{tense}.{pn}"] = [sg_or_pl(i, e)]
+    if not wk:
+        # the uncontracted 1sg secondary as an alternative: Beekes §18.3.3 *h₁é-steh₂-m (Ved. ásthām), Ved.
+        # áśravam, ágamam, Gk ἔχευα beside the Stang's-law forms stā́m, ḱlḗm, gʷḗm (Ringe 2006 p. 21 states
+        # the law for word-final *-Vmm, *-Vwm, *-Vh₂m, with nominal examples only)
+        for t in ("PST", "AOR"):
+            k = f"{t}.1SG"
+            if k in out and len(strong) > 1 and strong[-2].kind == "V" and strong[-1].base in ("w", "y", "m", "h2") \
+                    and not strong[-1].syl:
+                out[k] = _uniq(out[k] + [render(strong + [Seg("m", "R", syl=True)])])
     out["IMP.2SG"] = [render(strong), render(_add(weak, "dʰí"))]
     if conv == "handbook":   # zero grade + -dʰí is the usual athematic 2sg imperative (h₁sdʰí, ḱludʰí)
         out["IMP.2SG"].reverse()
     for pn, e in _ATH_IMP.items():
+        st = strong if pn == "3SG" else weak
         if weak_acc and e.startswith("én"):
             e = e[1:]
-        st = strong if pn == "3SG" else weak
+        elif red is not None and e.startswith("én"):
+            st, e = red, e[1:]
         if wk and spec.kind == "stat":
             st = junction_laryngeal_loss(st, _p(e))
         out[f"IMP.{pn}"] = [render(_add(st, e))]
```

### pie/classify.py (S3)

```diff
--- a/pie/classify.py
+++ b/pie/classify.py
@@ -71,10 +71,10 @@
     if j is None:
         return None
     root = [replace(x, acc=(i == j)) for i, x in enumerate(root)]
-    rest = zero_grade(render(root))
-    if rest is None:
-        return None
-    return render([replace(x, acc=False) for x in segs[:2]]) + rest
+    # zero-grade the root with the (deaccented) reduplication in place, so that a glide next to the
+    # deleted vowel sees the reduplication vowel: wé-woḱ → wewḱ, wí-wekʷ → wiwkʷ, yé-yes → yeys
+    # (zero-grading the root alone gave weuḱ, wiukʷ, yeis: two nuclei in hiatus)
+    return zero_grade(render([replace(x, acc=False) for x in segs[:2]] + root))
 
 
 def zero_grade(stem: str) -> str | None:
```

After the classify change, regenerate the specs with `scripts/classify_lexicon.py`. The only specs that change are wéwoḱti, wíwekʷti and yéyesti.

### Tests to add (new file tests/test_morph_athematic.py, or append to tests/test_morph.py)

All of these pass on the patched copy:

```python
from pie.morph import VerbSpec, conjugate


def c(strong, weak, kind="impf"):
    return conjugate(VerbSpec(strong, weak, kind), "handbook")


def test_glide_only_after_a_true_cluster():
    # VCu: plain glide (L&Y §4.3.1 *ḱl̥-n-w-énti; Ringe 2006 p. 28 *tn̥-nw-; Ved. śr̥ṇvánti, minvánti)
    assert c("ḱl̥néw", "ḱl̥nu")["PRS.3PL"][0] == "ḱl̥nwénti"
    assert c("tn̥néw", "tn̥nu")["PRS.3PL"][0] == "tn̥nwénti"
    assert c("minéw", "minu")["PRS.3PL"][0] == "minwénti"
    assert c("ḱl̥néy", "ḱl̥ni")["PRS.3PL"][0] == "ḱl̥nyénti"
    # CCu / CCi keep the vowel (LIV ḱluwónt-; Ved. kṣiyánti)
    assert c("ksnéw", "ksnu")["PRS.3PL"][0] == "ksnuwénti"
    assert c("tḱéy", "tḱi")["PRS.3PL"][0] == "tḱiyénti"
    assert c("ḱléw", "ḱlu", "pf")["PTCP.ACT"][0] == "ḱluwónts"


def test_glide_keeps_the_t_middle_first():
    assert c("ḱléw", "ḱlu", "pf")["MID.AOR.3SG"][0] == "ḱlutó"
    assert c("ksnéw", "ksnu")["MID.PRS.3SG"][0] == "ksnutór"


def test_optative_of_an_accented_weak_stem_is_zero_grade():
    # Fortson §5.57 (Narten: *-ih₁- throughout, 3pl always *-ent); Ringe 2006 p. 29 *h₁éd-ih₁-
    n = c("h₂wḗh₁", "h₂wéh₁")
    assert n["OPT.3SG"][0] == "h₂wéh₁ih₁t"
    assert n["OPT.3PL"][0] == "h₂wéh₁ih₁ent"
    assert c("h₁és", "h₁s")["OPT.3SG"][0] == "h₁syéh₁t"        # ordinary root present unchanged


def test_reduplicated_present_3pl():
    # Fortson §5.27 *de-dh₃-n̥ti; Beekes §18.1.3 *dʰé-dʰh₁-n̥ti, §18.2.3 *bʰé-bʰr̥-n̥ti
    r = c("dʰédʰeh₁", "dʰedʰh₁")
    assert r["PRS.3PL"][0] == "dʰédʰh₁n̥ti"
    assert r["PST.3PL"][0] == "dʰédʰh₁n̥t"
    assert r["IMP.3PL"][0] == "dʰédʰh₁n̥tu"
    assert r["MID.PRS.3PL"][0] == "dʰédʰh₁n̥tor"
    assert r["PRS.1PL"][0] == "dʰedʰh₁més"                       # Beekes *dʰi-dʰh₁-mé, Ved. dadhmás
    assert r["OPT.3SG"][0] == "dʰedʰh₁ih₁t"                       # Beekes §18.8.4 *dʰe-dʰh₁-ih₁-t
    assert "dʰedʰh₁énti" in r["PRS.3PL"]                          # Wiktionary form kept


def test_narten_subjunctive_on_the_e_grade():
    assert c("h₂wḗh₁", "h₂wéh₁")["SBJV.3SG"][0] == "h₂wéh₁eti"    # Ringe 2006 p. 29 *h₁éd-e/o-


def test_future_imperative_on_the_zero_grade():
    assert c("h₁és", "h₁s")["IMP.FUT.2SG"][0] == "h₁stṓd"         # Ved. dhattā́t, itā́t


def test_non_ablauting_athematic_optative():
    # Ringe 2006 p. 30: *h₁rudʰ-éh₁-ih₁-, *néwe-h₂-ih₁- (zero-grade suffix after a fixed accent)
    assert conjugate(VerbSpec("h₁rudʰéh₁", None), "handbook")["OPT.3SG"][0] == "h₁rudʰéh₁ih₁t"


def test_t_less_middle():
    # *ḱéy-or 'lies' (Fortson §5.16; L&Y §4.3.1; Beekes §18.7; Ved. śáye, 3pl śére)
    m = conjugate(VerbSpec("ḱéy", None, mid_t_less=True), "handbook")
    assert m["MID.PRS.3SG"][0] == "ḱéyor" and "ḱéytor" in m["MID.PRS.3SG"]
    assert m["MID.PST.3SG"][0] == "ḱéyo"
    assert m["MID.PRS.3PL"][0] == "ḱéyror"
    assert conjugate(VerbSpec("wés", None), "handbook")["MID.PRS.3SG"][0] == "wéstor"
```

## Order of integration

1. morph.py diff. It is self-contained: it touches only athematic verbal paths, and the Wiktionary convention is unchanged.
2. S1, S2 and D4 override lines. These are uncontroversial data fixes.
3. D1, D5 and D2 overrides, once the convention calls are confirmed. D5 needs the `mid_t_less` field from (1), and D2 depends on (1) for its 3pl.
4. classify.py change (S3) and spec regeneration; S4 and S5 at the integrator's discretion.

Scratch work for this audit (inventory, impact script, patched copies): /private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/athv_*.
