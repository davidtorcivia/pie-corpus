# 8c collocation scans of the strongest leads (2026-10-26)

Exploratory, outside the pre-registered measures. Tool: `scripts/collocates_8c.py`
over the corpus search index (2.34M units, 30 corpora). Results (forms and loci only):
`data/research/8c/collocations/*.json`.

## Method

For a target (one or more lexeme/root ids), every unit containing it is scanned; any
lexeme id or root group within ±W content words is a collocate. Per branch,
O = target units with the collocate, E = target units × the collocate's unit rate in
that branch. A collocate is listed when O ≥ 2 and O/E ≥ 2 in at least two branches,
ranked by branch count, then by the summed log₂(O/E). `--pair` prints the actual hits
of a target with given partners per branch.

Window counts are compared with unit-level base rates, so O/E understates
association. Personal names, semantic drift (Slavic слово 'word' < *ḱléwos) and
mapping errors produce false collocates: every listed pair has to be read.

## Calibration

Run on *ḱléwos* 'fame' with no hint, the scan recovers the textbook formulas:
imperishable fame (RV *śrávaḥ … ákṣiti*, *dʰgʷʰey-*), wide fame (RV *pr̥thú śrávaḥ* ~
OIr *clú* + *leth*), fame and name (RV *śrávase nā́ma* ~ OIr *clú … ainm*), fame among
gods/mortals. On *dʰugh₂tḗr* it recovers Daughter of the Sky (RV *duhitar divaḥ* ~
Hom. θυγάτηρ Διός); on *ḱerd-*, *ḱred-dʰeh₁-* 'believe'; on night, Night and Dawn
(RV *náktā uṣásā* ~ νύξ … ἠώς). The method finds known formulas; its negative results
mean something, within mapping coverage.

## Results by lead

| Lead | What the scans show | Verdict |
|---|---|---|
| Split the heart (*bʰeyd-* + *ḱerd-*) | Heart + split/burst verbs: Indo-Iranian 37 (*bhid-*, *hṛdayaṃ dīryati* 'the heart bursts'), Germanic 1 (the Heimskringla verse), Latin 1 (Plautus *cor finditur*). Blind review rejected the claim: ON *bíta* is the ordinary weapon verb and *hjarta* the place bitten. | Robust Indic idiom; not shown to be shared |
| Sleeping on someone's knees | Knee + sleep (window 8) finds only Laxdæla 174r:28, **a second Norse witness** (Heimskringla, Óláfs saga helga, AM 36 fol 486:29: Óláfr sleeps with his head on Finnr Árnason's knees before Stiklestad) and the Hittite KUB 36.89. Nothing in Greek, Indic or Celtic. | Lead strengthened (two Norse witnesses); the second is a man's knees |
| Loving as one's eyes | Eye + love/dear: nothing cross-branch (one AV love charm). | Still rests on Latin; unchanged |
| The night grows dark | Night + *temH-* 'dark' in four branches (Baltic ×93, Slavic ×51, Germanic ×19, RV *aktū́n támasaḥ*); *mergʷ-* Germanic + Slavic. Night + *h₁regʷos*: Homer's formulaic ἐρεβεννὴ νύξ (×16, "dark night covered his eyes"), Vedic only one weak hit. | Generic; ἐρεβεννή νύξ is Greek-internal |
| Mother earth | Earth + mother: Russian *мать сыра земля* (Slavic 149), Hesiod χθόνα μητέρα μήλων. | Known theme |
| Father's/mother's/brother's house | AVŚ 1.14.4 and the Norse law line are the only kin-list hits; δώματα πατρός, *domum … patri* are everyday. | Weak, as the review graded it |
| Give one's daughter | MBh *duhitaraṃ adadat*, Il. 11.226 θυγατέρα δίδου, Armenian. | Generic, as graded |
| Bear a name | RV *nā́ma bíbhrat* ×18; ON *beri þræls nafn* (Laxdæla); Greek noise. | Generic |
| Alive into the light | AV *jīva lokam* (loká- < *lówkos*), Lucretius *lumina vitae*, *in luminis oras*. | Known theme (light of the sun = life) |

## New candidates found by the scans

- **Daughters and daughters-in-law** (*dʰugh₂tḗr* + *snusós*, coordinated): Il. 24.166 and
  Od. 3.451 (θυγατέρες τε νυοί τε) and the Mahābhārata ×5 (*snuṣāṃ duhitaraṃ ca*). Both
  nouns cognate in a coordinated pair for the women of a household. Two branches,
  natural pairing. Strongest new shape.
- **With heart and mind** (*ḱerd-* + *men-*): Vedic stock dyad *hṛdā́ mánasā* (81 units);
  OIr *cride ⁊ menma* (Christian prose); Il. 16.435 κραδίη μέμονε (not a dyad).
- **Heart and tongue**: AV *hṛdayaṃ … jihvāṃ*; ON and Armenian witnesses are Christian.
- **Kāma's arrow in the heart**: AVŚ 3.25 *iṣuḥ kāmasya … vidhyāmi tvā hṛdi*; Irish *rop tú
  charas mo chride* is a Christian hymn. Thematic only.
- **Kneel and beg** (*ǵónu* + *gʷʰedʰ-*): ON *ganga fyrir kné … biðja* (Njála, secular) and
  Irish *léigis a ghlúine re lár … do ghuidh Dia* (Christian). Greek supplication at the
  knees uses non-cognate verbs.
- Rejected on reading: heart of a deer (the Slavic hits are a mapping error: *разгорелось*
  'flared up' mapped to *h₁el-* through *лось*).

## Errors found

Three mapping errors found by the scans are in
`data/research/8c/stageCS/error-reports-search.jsonl` for fix batch 4: byliny
*разгорелось* → *h₁el-*; Greek κέρδος 'gain' → *ḱerd-*; ON *nótt* grouped under
*negʷ-* 'bare'.

## Wave-4 figures (2026-10-26)

| Figure | Scan | Reading |
|---|---|---|
| Set a child on the knees (*sed-* + *ǵónu*) | Greek 116, Germanic 25, Celtic 4 (pair window 4) | Il. 9.488 and 9.455, Od. 19.401; ON *setti í kné sér* (Egils saga), *knésetja*; OIr Cú Chulainn *fo glún Chonchobair*. Found independently by RS031, RS031F and RS032F (two slabs). Known theme; Near Eastern parallels. |
| Men and cattle (*wiHro-* + *peḱu-*) | Indo-Iranian 14 (AV *paśubhiś ca vīraiḥ*, *paśu-vid vīra-vid*), Germanic 0 real, Italic 0 | The textbook formula; **coverage gap**: Umbrian *ueiro pequo* and Avestan *pasu vīra* are not found, so those mappings are missing. |
| Slay the serpent (*gʷʰen-* + *h₁ógʷʰis*) | RV *áhan áhim* ×36; Greek 0 (ὄφις not cognate) | As expected: outside Vedic the formula uses renewed words (Watkins). |
| Leave the light = die (*leykʷ-*) | Greek 517 (λείπειν φάος ἠελίοιο: Il. 18.11, Od. 11.93, Hes. *Op.* 155, *H. Ven.* 272); Latin 4 (Lucr. 3.542 *lumina … linquunt*, 3.1025 Ennius, 5.989 *linquebant … lumina vitae*); RV 1.113.1 (night leaves its place to dawn, *ric-*) | Greek formulaic; Latin repeated in Lucretius, a reader of Ennius and Homer (imitation risk); a known theme (light = life). |
| Redden with blood (*h₁rewdʰ-*) | No cross-branch pair with blood words | Weak. |
