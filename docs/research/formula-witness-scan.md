# Formula witness scan (2026-10-28)

The evidence step for Tier 2 back-projection. Every known formula in `data/formulas/formulas.jsonl`
(389 rows, Watkins and West) and the ten unnamed `core` rows of `data/generation/formula_menu.json`
was turned into one or more cognate lexeme pairs. Each pair was scanned over all branches of the
corrected search index (`data/research/8c/search-index/`, theonym-narrowed build; not rebuilt), and
the hits were read. Results, one row per formula: `data/research/formulas/witness-scan.jsonl`.
Mapping errors and coverage gaps noticed on the way: `data/research/formulas/mapping-errors-found.jsonl`
(42 entries, same shape as `data/research/8c/stageCS/error-reports-search.jsonl`). Forms and loci only;
no running text is stored.

## Method

**Pairs.** Formulas were collapsed into 164 pair specs (the dragon and fame families share a handful).
Ids came, in order of precedence, from the menu's `lex_ids`, from the eval-r3 pairs linked through
`overlap.formulas_jsonl`, and otherwise by hand from the PIE wording and the cited daughter words, looked
up in `data/lexicon/lexicon.jsonl`. Each slot is a set: the lexeme id plus its root group where the
group is specific. The lexeme alone under-recalls badly: the first test, *ḱléwos* + *n̥dʰgʷʰitós*,
found no Vedic hit because RV *ákṣiti* is keyed *dʰgʷʰéytis* and RV 1.9.7 spreads *śrávaḥ … ákṣitam*
over two pādas. Overbroad groups were left out: *dyew-* would bring in "god", and *dʰeh₁-* carries θεός.
A formula whose daughter wordings share no cognate pair is marked **not searchable**, with the
reason: only one slot is cognate; no cognate pair (renewed wording, or a parallel known only in
translation); function words or a grammatical figure only; names or compound names only.

**Scan.** `scan.py` (in the session scratchpad, read-only on the index) applies the `collocates_8c.py
--pair` rule: a word keyed (root_ids ∪ root_groups) in A, a different word keyed in B, within ±4
content words of one loader unit. It reproduces `collocates_8c.py` exactly on a lexeme pair (Greek 3)
and on a root-group target (*gʷʰen-* + *h₁ógʷʰis*: Indo-Iranian 36, Greek 4). It also records two
extra kinds of hit, each counted separately and never mixed into the pair count:
*compound* (one word keyed in both slots) and *adjacent* (A in unit n, B in unit n±1 of the same book,
for pāda- and line-length units). It also handles self-pairs (two distinct A words, for polyptoton).
A supplementary lemma scan covered the 125 unkeyed Homeric ἠέλιος units. The whole scan of 164 specs
took about 15 s.

**Reading.** For every spec and branch with hits, a core-corpus-first sample (up to 6 pair and 3
adjacent hits) was read; branches with many hits were read only as far as the sample. Each branch got
an accepted reading with the loci that carry the formula, or a rejection with the reason. The row
records the raw counts (pair, adjacent, compound), the number of read and accepted loci, up to five
loci with forms, and flags:
- `emendation`: matched form listed in the unit's `emendations` (Finnsburh 39 *swētne medo*);
- `name`: theonym or proper name;
- `calque-risk`, `biblical`, `late`, `latin-source risk`: corpus priors (xcl, ccmh/orv, grc-late,
  rea-goh/osx, sga-gl), confirmed or lifted on reading;
- `generic`, `weak`, `different-construction`;
- `etymology-disputed`, `partial-lexical`, `compound`;
- `found-by-probe`: a witness the scan misses because of a mapping error, checked at its locus.

A branch counts as **real** only when a witness was read and accepted, and it is not flagged
generic, weak, different construction, biblical or calque. Baltic and Slavic count as one branch,
Balto-Slavic.

**Classes.**
- **multi-branch**: real witnesses in two or more branches. `lexical` means the same cognate pair in
  at least two branches; `partial-lexical` means one slot is renewed or the two branches use different
  derivatives (εὐρύ ~ pr̥thú, χθών ~ pr̥thivī́).
- **single-branch**: real witnesses in one branch only.
- **not found**: `not searchable` (above); `coverage gap`, where hits are missing or wrong because of
  mapping, compounds, unkeyed clitics or an unreachable corpus; `absent`, where the pair is
  searchable but no witness was found.

**Tier 2 linkage.** The `formulas` field of every `corpus/tier2/*.jsonl` row is empty. Rows were
therefore linked to pair specs by hand, through their `theme` and the lemmas of their `cognate_refs`.
`in_tier2` lists the Tier 2 line ids that already realise a formula. "Not in Tier 2" means no line
on that theme was found; it is not the result of joining on a field.

**Recall probe.** Of the 471 RV and Homer loci that the formula sources and the eval-r3 attestations
cite for searchable formulas, the scan hits 232 (49%). Most misses are expected: the cited line shows
the parallel in non-cognate wording (ἀθάνατος, θνητός, ἐθέλω), or the source cites a whole stanza.
The misses that were checked turned up mapping errors: RV stár- keyed *terh₂-, Greek πολιός keyed
*pleh₁-, RV ajuryá- and πολυθαρσής unkeyed.

## Counts by class

| Class | formulas.jsonl (389) | menu core rows (10) |
|---|---|---|
| multi-branch, lexical | 102 | 9 |
| multi-branch, partial lexical | 18 | 0 |
| single-branch | 70 | 0 |
| not found: coverage gap | 42 | 1 (good fame) |
| not found: absent | 5 | 0 |
| not found: not searchable | 152 | 0 |

Not searchable, by reason: one cognate slot only 68, no cognate pair 54, names or compound names 19,
function words or a figure 11. Of the 120 multi-branch formulas, 87 are already realised in Tier 2;
33 are not, and they fall under 27 distinct pair specs. Of the 164 specs, 67 have real witnesses in
two or more branches, 58 in one, and 39 in none.

The three compound epithets `horse-devouring-man-devouring`, `weapon-kill-monster` and
`man-slaying-beast-slaying` are counted as coverage gaps. A coordinated "horses and men" (ἵππων τε
καὶ ἀνδρῶν ~ áśvaiḥ vīrébhiḥ) does not attest aspō.garəm nərə.garəm or gohā́ nr̥hā́. The
dragon-slaying variants (with a weapon, with a companion, relative clause, reciprocity, ring
composition) carry `evidence_scope`: their multi-branch class rests on the basic pair slay + serpent
alone, and the variant feature itself was not checked.

Indo-Iranian and Greek dominate: they appear in 116 and 93 of the multi-branch formulas. Italic
appears in 18, Germanic 12, Balto-Slavic 6, Celtic 4 and Anatolian 4. Most new candidates are
therefore Greek–Indo-Iranian pairs; three-branch ones are rare.

### Tier 2 lines whose evidence the index does not reproduce

These are input for the review→fix loop. Seven Tier 2-realised formulas come out **not found**,
all as coverage gaps:
- `hero-terh2-adversary` (dragon-slaying-004): vr̥tra- has no id, and the Hittite serpent word is
  not cognate.
- `west_ch04_f29`, `west_ch12_f26`, `west_ch02_f85` (divine-twins-005, good horses): compounds,
  and *h₁su-* has no postings.
- `west_ch10_f10`, `west_ch10_f11` (fame-009, fame-010, fame-015, poetics-gifts-013, good fame):
  Avestan vaŋhāu is unkeyed, and OIr fó is unmapped.
- `west_ch01_f04` (poetics-gifts-003, weave words): ὕμνος has no id, and Bacchylides is not found.

Twenty-six come out **single-branch**. Each Tier 2 line rests on its second branch through the
witnesses its authors found by locus, not through this scan:
- dragon-slaying-011 (the reciprocal slayer-slain formula; Vedic RV 8.84.9b only): `slays-slayer-iteration`,
  `he-who-slays-will-be-slain`, `adversary-slay-hero`, `hero-slay-anti-hero`, `slain-is-x-paean`,
  `west_ch02_f88`.
- death-otherworld-007 (overcome death; Vedic only): `overcome-death`, `overcome-death-mrti-nek`,
  `nectar-ambrosia-nek-terh2-nmrto`, `west_ch03_f31`.
- death-otherworld-010 (bring death; Greek only, the ON witness is the compound banaorð): `bring-death-to`.
- healing-charms-001 and -006 (bone to bone; Vedic only, Hittite found only in law and ritual):
  `bone-to-bone-juxtaposition`, `west_ch08_f22`.
- dawn-sun-010, -007, -006 (swift Sun, Dawn shines widely, Dawn seen; Vedic only):
  `west_ch05_f02`, `west_ch05_f17`, `west_ch05_f18`.
- divine-twins-001 and -006, bp-east-003 (sons of Sky; Vedic only): `west_ch04_f28`.
- poetics-gifts-004 (the song goes forth): `west_ch01_f11`.
- poetics-gifts-015 and -016 (hear me; Greek only, Vedic clitics unkeyed): `west_ch08_f01`, `west_ch02_f50`.
- bp-gk-gmc-001 (word and deed; Greek only, Germanic orð/word not cognate): `west_ch02_f04`.
- sky-father-011 (father begetter): `west_ch02_f32`.
- bp-ii-ita-002 (god of gods; Vedic only): `west_ch02_f71`, `west_ch02_f73`, `west_ch02_f91`, `west_ch02_f93`.

## Best multi-branch formulas not yet in Tier 2

Ranked by number of real branches (×10), +4 for a full lexical match, +2 for each branch with a
witness in a core corpus (Homer, RV, AV, Avestan, Hittite, Edda, OE, OIr, Umbrian, dainos), and −2
for each weakening flag (late, name, disputed etymology, found by probe, compound, partial). Each
entry gives the formula ids it covers and the read witnesses (locus *forms*).

### 1. `horse+men`: Celtic, Greek, Indo-Iranian

Formula ids: `west_ch12_f17`. Score 40.

- **Celtic** (raw: 31 pair, 68 adjacent; read and accepted: 3): G301008:#1/#1:13 *ech ~ fer*; G301900:#1/#25:12 *ech ~ fer*; G302011:#1/#1/t#5:21 *eich ~ ḟir*.
- **Greek** (raw: 328 pair, 536 adjacent; read and accepted: 1): Il. 10.338 *ἵππων ~ ἀνδρῶν*.
- **Indo-Iranian** (raw: 131 pair, 106 adjacent; read and accepted: 3): RV 9.96.11d *áśvaiḥ ~ vīrébhiḥ*; AVŚ, 3, 16.s6 *aśvair ~ nṛbhir*; AVŚ, 12, 1.s53 *aśveṣu ~ vīreṣu*.
- Note: "Men" is *h₂nḗr in Greek, *wiHrós in Irish; Vedic has both (nŕ̥-, vīrá-).

### 2. `bold+mind`: Greek, Indo-Iranian

Formula ids: `west_ch02_f36`. Score 28.

- **Greek** (raw: 41 pair, 85 adjacent; read and accepted: 2): Il. 5.2 *θάρσος ~ μένος*; Od. 1.321 *θάρσος ~ μένος*.
- **Indo-Iranian** (raw: 5 pair, 8 adjacent; read and accepted: 3): RV 1.54.3b *dhr̥ṣatáḥ ~ mánaḥ*; RV 5.35.4c *dhr̥ṣát ~ mánaḥ*; RV 8.62.5a *dhr̥ṣatáḥ ~ mánaḥ*.

### 3. `cloud+clothe`: Greek, Indo-Iranian

Formula ids: `west_ch02_f48`. Score 28.

- **Greek** (raw: 5 pair, 9 adjacent; read and accepted: 3): Il. 14.350 *νεφέλην ~ ἕσσαντο*; Il. 15.308 *νεφέλην ~ εἱμένος*; Il. 20.150 *νεφέλην ~ ἕσαντο*.
- **Indo-Iranian** (raw: 4 pair, 5 adjacent; read and accepted: 4): RV 5.63.6c *abhrā́ ~ vasata*; RV 5.85.4c *abhréṇa ~ vasata*; RV 7.97.6d *nábhaḥ ~ vásānāḥ*; RV 9.83.5b *nábhaḥ ~ vásānaḥ*.

### 4. `race+mankind`: Germanic, Indo-Iranian

Formula ids: `west_ch03_f08`. Score 28.

- **Germanic** (raw: 1939 pair, 4665 adjacent; read and accepted: 4): Beo. 702 *cynnes ~ manna*; Beo. 713 *cynnes ~ manna*; Beo. 736 *cynnes ~ manna*; Beo. 811 *cynne ~ manna*.
- **Indo-Iranian** (raw: 83 pair, 116 adjacent; read and accepted: 3): RV 1.48.11b *jáne ~ mā́nuṣe*; RV 1.70.2b *jánasya ~ mā́nuṣasya*; RV 1.96.2b *prajā́ḥ ~ mánūnām*.
- Note: *mon-/*manu- "man" + *ǵenh₁- "race": OE manna cynn ~ Ved. mā́nuṣa- jána-. Germanic and Indo-Iranian.

### 5. `strong+mind`: Greek, Indo-Iranian

Formula ids: `holy-strength-isira-manas`, `west_ch02_f38`. Score 28.

- **Greek** (raw: 156 pair, 257 adjacent; read and accepted: 4): Od. 13.20 *ἱερὸν ~ μένος*; Od. 13.24 *ἱέρευσ̓ ~ μένος*; Od. 18.34 *ἱερὸν ~ μένος*; Od. 7.167 *ἱερὸν ~ μένος*.
- **Indo-Iranian** (raw: 1 pair, 0 adjacent; read and accepted: 1): RV 8.48.7a *iṣiréṇa ~ mánasā*.

### 6. `swift+fly`: Greek, Indo-Iranian

Formula ids: `swift-flying-eagle`, `west_ch02_f06`. Score 28.

- **Greek** (raw: 20 pair, 23 adjacent; read and accepted: 2): Il. 15.238 *ὠκέϊ ~ πετεηνῶν*; Il. 21.253 *ὤκιστος ~ πετεηνῶν*.
- **Indo-Iranian** (raw: 3 pair, 5 adjacent; read and accepted: 1): RV 2.16.3d *āśúbhiḥ ~ pátasi*.
- Note: West's ὠκυπέτης ἴρηξ ~ śyenáḥ āśupátvā are compounds; the witnesses found are phrasal.

### 7. `upright+stand`: Greek, Indo-Iranian

Formula ids: `west_ch08_f23`. Score 28.

- **Greek** (raw: 350 pair, 370 adjacent; read and accepted: 3): Il. 18.246 *ὀρθῶν ~ ἑσταότων*; Il. 23.271 *ὀρθὸς ~ στῆ*; Il. 24.359 *ὀρθαὶ ~ ἔσταν*.
- **Indo-Iranian** (raw: 38 pair, 17 adjacent; read and accepted: 2): RV 1.30.6a *ūrdhváḥ ~ tiṣṭha +*; RV 1.164.10b *ūrdhváḥ ~ tasthau*.
- Note: Posture collocation; generic as well as the healing formula.

### 8. `white+clothe`: Greek, Indo-Iranian

Formula ids: `west_ch02_f19`. Score 28.

- **Greek** (raw: 62 pair, 50 adjacent; read and accepted: 1): Il. 3.419 *ἀργῆτι ~ ἑανῷ*.
- **Indo-Iranian** (raw: 13 pair, 19 adjacent; read and accepted: 2): RV 3.39.2c *árjunā ~ vástrāṇi*; MBh, 1, 57.s334 *arjunāni ~ vastrāṇi*.

### 9. `god+mortal`: Indo-Iranian, Italic

Formula ids: `west_ch03_f11`, `west_ch02_f64`. Score 26.

- **Indo-Iranian** (raw: 157 pair, 188 adjacent; read and accepted: 2): RV 1.70.6b *devā́nām ~ mártān*; RV 1.100.15a *devā́ḥ ~ mártāḥ*.
- **Italic** (raw: 33 pair, 19 adjacent; read and accepted: 1): LucrDRN1 1.1015 *diuom ~ mortale*.

### 10. `good+mind`: Greek, Indo-Iranian

Formula ids: `west_ch02_f35`. Score 26.

- **Greek** (raw: 13 pair, 3 adjacent; read and accepted: 4): Il. 17.456 *ἠΰ ~ μένος*; Il. 20.80 *ἠΰ ~ μένος*; Il. 23.524 *ἠῢ ~ μένος*; Il. 24.6 *ἠΰ ~ μένος*.
- **Indo-Iranian** (raw: 168 pair, 74 adjacent; read and accepted: 1): Y16.3b *vohu ~ manō*. Flags: name.
- Note: Lexical match *h₁(we)su- + *ménos: Greek μένος ἠΰ ~ Avestan vohu manah-. Vedic sumatí- is a compound with mati-, rejected.

### 11. `race+god`: Indo-Iranian, Italic

Formula ids: `west_ch03_f07`. Score 26.

- **Indo-Iranian** (raw: 233 pair, 437 adjacent; read and accepted: 2): RV 1.20.1a *jánmane ~ devā́ya*; RV 1.70.6b *jánma ~ devā́nām*.
- **Italic** (raw: 15 pair, 19 adjacent; read and accepted: 1): Catul 64.23 *genus ~ deum*.

### 12. `skygod+cloud`: Greek, Indo-Iranian

Formula ids: `west_ch04_f04`. Score 26.

- **Greek** (raw: 44 pair, 45 adjacent; read and accepted: 2): Il. 16.298 *Ζεύς ~ νεφέλην* [name]; Il. 2.146 *Διὸς ~ νεφελάων* [name]. Flags: name.
- **Indo-Iranian** (raw: 15 pair, 36 adjacent; read and accepted: 2): RV 2.4.6d *dyaúḥ ~ nábhobhiḥ*; RV 5.63.4c *diví ~ abhréṇa*.
- Note: West's Latvian Dieva debesīm unreachable: the Latvian corpus (lv) has 751 units.

### 13. `skygod+rain`: Greek, Indo-Iranian

Formula ids: `west_ch04_f03`. Score 26.

- **Greek** (raw: 51 pair, 74 adjacent; read and accepted: 3): Il. 11.493 *Διὸς ~ ὄμβρῳ* [name]; Il. 12.286 *Διὸς ~ ὄμβρος* [name]; Il. 5.91 *Διὸς ~ ὄμβρος* [name]. Flags: name.
- **Indo-Iranian** (raw: 93 pair, 147 adjacent; read and accepted: 2): RV 2.6.5a *diváḥ ~ vr̥ṣṭím*; RV 2.27.15b *diváḥ ~ vr̥ṣṭím*.
- Note: Cognate rain words differ (ὄμβρος ~ abhrá-, vr̥ṣṭí- ~ *h₁wers-); Sky/Zeus cognate.

### 14. `slay+pay`: Celtic, Greek

Formula ids: `slay-and-avenge-gwhen-kwei`. Score 26.

- **Celtic** (raw: 4 pair, 12 adjacent; read and accepted: 2): G302011:#1/#1/t#4:12 *guin ~ cin*; celtic-journal-eriu-1904-1928:eriu_1904_1:L2605-L2605 *guin ~ cinaid*. Flags: etymology-disputed.
- **Greek** (raw: 32 pair, 38 adjacent; read and accepted: 5): Il. 15.116 *φόνον ~ τίσασθαι*; Il. 21.134 *φόνον ~ τίσετε*; Od. 24.470 *φόνον ~ τίσεσθαι*; Hesiodus Scutum 17 *φόνον ~ τίσαιτο*.
- Note: Avestan kaēnā- (Yt 19) not found.

### 15. `star+adorn`: Greek, Indo-Iranian

Formula ids: `west_ch09_f10`. Score 26.

- **Greek** (raw: 3 pair, 4 adjacent; read and accepted: 1): Il. 16.134 *ἀστερόεντα ~ ποικίλον*.
- **Indo-Iranian** (raw: 1 pair, 1 adjacent; read and accepted: 1): RV 1.68.10b *pipéśa ~ stŕ̥bhiḥ* [found-by-probe]. Flags: found-by-probe.
- Note: Mapping error hides the Vedic witness; with it fixed the figure would be two-branch (Vedic, Greek).

### 16. `wish+self`: Greek, Indo-Iranian

Formula ids: `west_ch02_f99`. Score 26.

- **Greek** (raw: 269 pair, 0 adjacent; read and accepted: 1): Aeschylus Prometheus vinctus 220 *ἑκόνθ’ ~ ἑκόντι*.
- **Indo-Iranian** (raw: 39 pair, 0 adjacent; read and accepted: 3): RV 1.62.11c *uśatī́ḥ ~ uśántam*; RV 1.71.1a *uśatī́ḥ ~ uśántam*; RV 2.37.6d *uśán ~ uśatáḥ*.

### 17. `wolf+grey`: Balto-Slavic, Greek

Formula ids: `west_ch02_f20`. Score 26.

- **Baltic** (raw: 1 pair, 1 adjacent; read and accepted: 2): Lietuvi-kos-svotbin-s-dainos-1883:65369 *Vilkas ~ pilkas*; litauischevolksl00leskuoft:14597 / litauischevolksl00leskuoft:14598 *vilkelei ~ pilkelei* [adjacent].
- **Greek** (raw: 0 pair, 0 adjacent; read and accepted: 1): Il. 10.334 *πολιοῖο ~ λύκοιο* [found-by-probe]. Flags: found-by-probe.
- Note: Lith. pilkas and Gk πολιός are both *pelH-; OE wulf se græga and ON úlfr grár use a non-cognate adjective.

### 18. `dawn+immortal`: Greek, Indo-Iranian

Formula ids: `west_ch05_f15`. Score 24.

- **Greek** (raw: 6 pair, 1 adjacent; read and accepted: 2): Apollonius Rhodius Argonautica 4.1170 *ἠὼς ~ ἀμβροσίοισιν* [late (post-classical Greek)]; Quintus Posthomerica 2.641 *Ἠῶ ~ ἄμβροτον* [late (post-classical Greek), name]. Flags: late.
- **Indo-Iranian** (raw: 1 pair, 2 adjacent; read and accepted: 1): RV 7.75.3b *uṣásaḥ ~ amŕ̥tāsaḥ*.
- Note: Greek witnesses are post-classical epic; Homer has no ἄμβροτος Ἠώς in the scan.

### 19. `deathn+be`: Germanic, Greek

Formula ids: `be-the-death-of`. Score 24.

- **Germanic** (raw: 130 pair, 221 adjacent; read and accepted: 2): AM-132-fol-Egils-saga 66v:41 *banamaðr ~ vera*; AM-132-fol-Bandamanna-saga 116v:2 *banamaðr ~ var*. Flags: compound.
- **Greek** (raw: 579 pair, 1039 adjacent; read and accepted: 2): Il. 16.144 *φόνον ~ ἔμμεναι*; Il. 11.443 / Il. 11.444 *φόνον ~ ἔσσεσθαι* [adjacent].

### 20. `immortal+eat`: Greek, Indo-Iranian

Formula ids: `west_ch03_f30`. Score 24.

- **Greek** (raw: 9 pair, 4 adjacent; read and accepted: 5): Il. 13.35 *ἀμβρόσιον ~ εἶδαρ*; Il. 5.369 *ἀμβρόσιον ~ εἶδαρ*; Hesiodus Theogonia 640 *ἀμβροσίην ~ ἔδουσι*; Hymni Homerici In Venerem 260 *ἄμβροτον ~ εἶδαρ*.
- **Indo-Iranian** (raw: 10 pair, 7 adjacent; read and accepted: 1): MBh, 13, 62.s64 *amṛtam ~ annaṃ*. Flags: late.
- Note: Greek εἶδαρ and Vedic/Skt. ánna- are both *h₁ed- derivatives with *n̥mr̥tó-.

Ranked 21–27 (weaker, each two-branch with a flag):
- `immortal+eat`: ἀμβρόσιον εἶδαρ Il. 5.369 and Hes. Th. 640 ~ MBh annam amr̥tam (late).
- `immortal+word`: ἀμβροσίων ἐπέων Pind. P. 4.299 and Soph. Ant. 1134 ~ MBh 12.279.3 amr̥tasya iva
  vacasaḥ (late).
- `mortal+self`: RV 1.147.5b mártaḥ mártam ~ Theocr. 16.4 βροτοὶ βροτούς.
- `see+self`: AVŚ 5.23.12 dr̥ṣṭāṃś ca … adr̥ṣṭāṃś ca ~ Cato Agr. 141.2 morbos uisos inuisosque and
  Umbrian uirseto auirseto; the verbs are not cognate.
- `skygod+door`: RV 1.48.15b dvā́rau … diváḥ ~ Ar. Pax 179 ἐν Διὸς θύραισιν.
- `earth+navel`: nā́bhā pr̥thivyā́ḥ ~ χθονὸς ὀμφαλός; the earth word is renewed.
- `skygod+eye`: Il. 14.286 Διὸς ὄσσε ~ RV 1.115.1a devā́nām … ánīkam; two different images.
- `sun+rota`: Lucr. 5.432 solis rota ~ RV sū́ryasya rátha-; different derivatives.

Left out of the ranking: `fame+name`, the coordinated dyad "fame and name" (RV 1.57.3c śrávase nā́ma ~
Soph. El. 694 κλεινὸν ὄνομα ~ Early Modern Irish annals clú ⁊ ainm, late). It has three branches,
but its only formula id, `famous-name`, is already realised in Tier 2 as "famous name" (fame-011).
The dyad itself is not realised.

Judgement notes on the top of the list:
- `horse+men` is the only clean three-branch new formula, but the word for "men" differs: Greek
  ἀνδρῶν (*h₂nḗr) and Irish fer (*wiHrós). Vedic has both, nr̥bhir in AVŚ 3.16.6 and vīrébhiḥ in RV
  9.96.11d. A Tier 2 line would choose one, or pair the two as Vedic does.
- `upright+stand` is posture language as much as the healing formula.
- `slay+pay` rests on OIr *cin* < *kʷei-*, which is disputed.
- `star+adorn` and `wolf+grey` each need a witness that the scan misses because of a mapping error
  (RV stár- and Greek πολιός); both witnesses were checked at their locus.

## Coverage gaps

These hide formulas from the scan; details and loci are in `mapping-errors-found.jsonl`.
- **Compounds**: compounds are keyed to one member only. This hides man-slaying (nr̥hán-, ἀνδροφόνος),
  good horses (suáśva-, εὔιππος), many-named, two-footed and four-footed, well-made, well-wheeled,
  fine-yoked, ill-famed, unsleeping and besiege. *h₁su-*, *n̥-*, *dus-* and *Hn̥dʰér* have no postings.
- **Clitics and particles** are not content words (me, μοι, sú, εὖ, elided ὑπ̓): hear me, hear well,
  under the sun.
- **Homer**: 125 units lemmatised ἠέλιος are not keyed *sóh₂wl̥*.
- **Latvian**: the dainas corpus has 751 units, so West's Dieva nams, Dieva durvis, Dieva dēli,
  Dieva vērši and Saules meita are unreachable.
- **Single lexemes not keyed**: Avestan vaŋhāu (good fame); Vedic tvā (this I ask thee); Hittite
  dankui- (dark earth); Greek ἰός (arrow formulas); Greek ὀμείχω (urinate standing); Latin nouem
  (thrice nine); RV ajuryá-; AVP asthi (bone to bone).
- **Corpora not indexed**: Avestan Yašt verse is partly missing (janat̰ ažīm, kaēnā); Old Persian,
  Gothic, Mycenaean, Gaulish, Venetic, Oscan and Scottish Gaelic are absent.

## Mapping errors found (31 mapping, 11 coverage)

The largest by impact:
- The *gʷerH-* "praise" group also carries *gʷerH-* "mountain" (gora, giri-, Βορέας, Lith. giria) and
  unrelated words (OIr bráth, ON kyrr). Every praise or song scan is flooded.
- OIr día "to his/their" (do + possessive) and día "day" are keyed *dyḗws*. This floods every
  sky-god scan in Celtic.
- OIr gona "with his" and gonadh "so that" are keyed *gʷʰen-*.
- RV stár- "star" is keyed *terh₂-*.
- Greek πολιός is keyed *pleh₁-*; Σάτυρος is keyed *deywós*; ἦρ "spring" is keyed *h₁ésh₂r̥* "blood";
  ὁδός is keyed *sed-* "sit"; φατός is keyed *gʷʰen-*.
- RV anyá- is keyed *h₂élyos*.
- Vedic hvā-/hū- "call" is keyed *ǵʰew-* "pour".
- Skt kṣam- "forbear" is keyed "earth".
- Armenian գան "they come" and the aorist ending -ցան are keyed *gʷʰen-*; տուիչ "giver" is keyed
  *dyḗws*.
- Latin medulla is keyed *mosgʰós*.

## Limitations

- Reading was sampled. Branches with hundreds of hits (μέγα κλέος, ἔπεα πτερόεντα) were judged on
  the core-corpus sample, so "read and accepted" is a lower bound, not a count.
- Classification is per spec. Where several formula ids share a spec (the dragon-slaying family),
  they share its evidence; the reciprocal and with-weapon variants are not separated.
- Pairs were assigned by hand for about 240 formulas. A different id choice can change a
  single-branch result. The `specs` field of each row gives the A and B ids used.
- Time: started 20:18, scan and reading done by 20:55; the deliverables were written after that.
