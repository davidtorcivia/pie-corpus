# Daughter-language sources for the formula search (2026-10-23)

Inventory of the open-licensed daughter data under `raw/daughters/`. Provenance, URLs and sha256 are in `raw/MANIFEST.md`, and `raw/` is gitignored. The search needs two things from each branch: a **text corpus** (where formulas occur) and a **lemma → PIE mapping** (to put words from different branches on the same lexeme). Before round 3 the mapping existed only for Sanskrit, Greek and Latin, and corpora outside Vedic and Homer were small.

**Licences.** NC = CC BY-NC-SA, research use only: never into released training data, and text derived from it is NC too. PD = public domain (pre-1929 editions). kaikki = Wiktionary CC BY-SA 4.0 / GFDL.

## Mapping sources: kaikki.org Wiktionary extracts (new)

These are JSONL, one entry per line, the same format as `kaikki-pie-20261021` and `kaikki-sanskrit`. None is lemmatized text. They are the lemma → etymon link: `etymology_templates` (inh/der/bor/root) cite the PIE (`ine-pro`) or intermediate proto-form, and the proto-language dumps carry `descendants` trees that link daughters PIE pages leave out. "PIE-linked" counts entries whose etymology templates cite an `ine-pro` etymon. Entries include inflected-form pages, so lemma-like entries (not pure form-of) are given too.

| Language | Dir | Entries | Lemma-like | PIE-linked |
|---|---|---:|---:|---:|
| Old Norse | `kaikki-oldnorse` | 11,403 | 4,862 | 1,502 |
| Old English | `kaikki-oldenglish` | 68,904 | 16,392 | 2,019 |
| Gothic | `kaikki-gothic` | 23,034 | 3,678 | 713 |
| Old High German | `kaikki-oldhighgerman` | 3,744 | 2,414 | 440 |
| Old Saxon | `kaikki-oldsaxon` | 2,337 | 1,810 | 329 |
| Old Irish | `kaikki-oldirish` | 6,716 | 3,324 | 1,298 |
| Middle Irish | `kaikki-middleirish` | 794 | 611 | 147 |
| Middle Welsh | `kaikki-middlewelsh` | 1,164 | 498 | 182 |
| Lithuanian | `kaikki-lithuanian` | 30,371 | 9,414 | 1,025 |
| Latvian | `kaikki-latvian` | 134,448 | 16,744 | 819 |
| Old Church Slavonic | `kaikki-oldchurchslavonic` | 4,635 | 3,530 | 369 |
| Old East Slavic | `kaikki-oldeastslavic` | 901 | 706 | 151 |
| Hittite | `kaikki-hittite` | 515 | 479 | 258 |
| Old Persian | `kaikki-oldpersian` | 587 | 566 | 118 |
| Old Armenian | `kaikki-oldarmenian` | 8,541 | 6,070 | 1,392 |
| Tocharian A | `kaikki-tochariana` | 504 | 500 | 172 |
| Tocharian B | `kaikki-tocharianb` | 2,484 | 2,370 | 409 |
| Umbrian | `kaikki-umbrian` | 531 | 403 | 238 |
| Albanian | `kaikki-albanian` | 24,481 | 13,853 | 1,488 |
| Mycenaean Greek | `kaikki-mycenaeangreek` | 568 | 545 | 46 |
| Proto-Germanic | `kaikki-protogermanic` | 5,764 | 5,537 | 3,690 |
| Proto-Celtic | `kaikki-protoceltic` | 1,613 | 1,605 | 1,197 |
| Proto-Brythonic | `kaikki-protobrythonic` | 741 | 704 | 302 |
| Proto-Balto-Slavic | `kaikki-protobaltoslavic` | 493 | 480 | 470 |
| Proto-Slavic | `kaikki-protoslavic` | 5,473 | 5,214 | 3,294 |
| Proto-Italic | `kaikki-protoitalic` | 753 | 747 | 691 |
| Proto-Indo-Iranian | `kaikki-protoindoiranian` | 800 | 754 | 733 |
| Proto-Iranian | `kaikki-protoiranian` | 415 | 402 | 259 |

The proto-language dumps matter most. Most daughter entries cite only their nearest proto-form (e.g. Old Norse → `gem-pro`), so a daughter → PIE path usually goes daughter → Proto-Germanic/Celtic/Slavic/Italic/Indo-Iranian → PIE. Proto-Germanic and Proto-Slavic are well covered, and Proto-Balto-Slavic (493) and Proto-Celtic (1,613) are thin.

**Missing from kaikki:** Avestan, Old Prussian, Cuneiform and Hieroglyphic Luwian, Oscan and Proto-Hellenic have no per-language extract. They appear only in the all-languages dump (3.08 GB, over the cap; not fetched). Until then, Avestan and Oscan words can be reached only through the descendants lists of the PIE and proto-language pages.

## Text corpora

| Source | Dir | Language(s) | Size | Lemmatized | Format | Licence |
|---|---|---|---|---|---|---|
| **Digital Corpus of Sanskrit** (Hellwig), `dcs/data` at 8aeed5a (new) | `dcs-hellwig` | Vedic and Classical Sanskrit | 5.94M words, 90,874 lemmas, 271 texts; Vedic Saṃhitā/Brāhmaṇa/Āraṇyaka/Upaniṣad ≈ 0.98M | yes (manually checked, one annotator); Vedic Treebank chapters and 7,227 `.conllu_parsed` files also have dependencies | CoNLL-U per chapter; lookup CSVs (dictionary with lemma IDs, word senses) | CC BY 4.0 |
| **PROIEL** (Syntacticus release 20230428) (new) | `syntacticus-proiel-torot/…/proiel` | Gothic 56k; OCS (Marianus) 58k; Classical Armenian 21k; Greek 240k (NT, Herodotus 84k, Sphrantzes); Latin 225k | 600k tokens | yes (manual), with full morphology and dependencies | PROIEL XML + CoNLL-X | NC |
| **TOROT** (same release) (new) | `…/torot` | OCS / Church Slavonic 156k (Suprasliensis, Zographensis, Psalterium Sinaiticum…); Old Russian 259k (chronicles, Igor Tale 2.8k, Zadonshchina…) | 415k tokens | yes (manual) | PROIEL XML + CoNLL-X | NC |
| **ISWOC**, Old English texts only (same release) (new) | `…/iswoc` | Old English prose (Ælfric, Orosius, AS Chronicle, Apollonius, WS Gospels) | 28k tokens | yes (manual) | PROIEL XML + CoNLL-X | NC |
| Buck 1904, *Grammar of Oscan and Umbrian* (new) | `oscan-umbrian-buck1904` | Umbrian (complete Iguvine Tables), Oscan inscriptions, English commentary | 135k words OCR, mostly commentary | no; glossary with references | archive.org OCR text | PD |
| Stokes & Strachan, *Thesaurus Palaeohibernicus* 1901–03 (new) | `oldirish-thesaurus-palaeohibernicus` | Old Irish glosses (Würzburg, Milan, St Gall…), poems, names; Latin lemmata, English translation | 565k words OCR (Irish part much smaller) | no | archive.org OCR text, 2 volumes | PD |
| Grein, *Bibliothek der ags. Poesie* 1857–58 + *Sprachschatz* 1861–64 (new) | `oe-poetry-grein` | Old English poetry (whole corpus), German apparatus; Sprachschatz = OE poetic dictionary with line refs | text vols ≈ 224k words per copy (3 OCR copies of vol. 1); Sprachschatz ≈ 683k | no; Sprachschatz usable as a lemma index | archive.org OCR text | PD |
| VedaWeb Rigveda | `rigveda-vedaweb` | Vedic | 165k tokens | yes | TEI | CC BY (annotation); text versions NC |
| Perseus AGDT 2.1, Iliad + Odyssey | `homer-perseus-agdt` | Homeric Greek | 204k words | yes | treebank XML | CC BY-SA 3.0 |
| LASLA, early Latin | `latin-lasla` | Plautus, Lucretius, Catullus, Cato | 145k tokens | yes | CoNLL-U+ | NC |
| CAB Avesta | `avesta-cab` | Avestan | ≈113k words | no | TEI-like XML | NC |
| TLHdig Beta 0.3 | `hittite-tlhdig` | Hittite | 928k words, 454k disambiguated | partly (automatic) | AOxml | CC BY 4.0 |
| Finnur Jónsson 1926 Edda | `edda-fj1926` | Old Norse poetry | ≈54k words | no | OCR text | PD |
| Harrison & Sharp *Beowulf* | `oe-beowulf-gutenberg` | Old English | ≈17.5k words + glossary | no | plain text | PD |
| UD Old Irish DipWBG/DipSGG | `oldirish-ud` | Old Irish | 835 tokens | yes | CoNLL-U | CC BY-SA / NC |

## What each adds to the formula search

- **DCS** is the largest gain. It gives a second, independent Vedic witness beyond the Rigveda (AV Śaunaka and Paippalāda, Yajurveda Saṃhitās, Brāhmaṇas, Upaniṣads), all lemmatized with permanent lemma IDs and openly licensed (CC BY), so it can be used beyond research. The Ṛgveda in DCS (170k words) gives an independent lemmatization to check VedaWeb against. The epics give a late-Indic control.
- **PROIEL/TOROT** add the first lemmatized Germanic (Gothic), Slavic (OCS, Old Russian), and Armenian corpora, plus Herodotus as post-Homeric Greek prose. They are Bible translations for the most part. That makes them poor for inherited poetic formulas, but they give clean lemma frequencies and a parallel-text control: a pair that co-occurs in Gothic, OCS and Armenian NT only because the Greek NT does is a translation artefact. The Igor Tale and Zadonshchina are the only (small) East Slavic poetic texts. Everything here is NC.
- **kaikki daughters + intermediate proto-languages** give the lemma → PIE mapping for Germanic, Celtic, Balto-Slavic, Armenian, Albanian, Tocharian, Anatolian and Italic. This is what the round-2 analysis named as the bottleneck. Mapping a corpus lemma goes through the daughter entry's `etymology_templates`, or else through the proto-language entry's `descendants`.
- **Grein (OE poetry), Thesaurus Palaeohibernicus (Old Irish), Buck (Umbrian/Oscan)** are the only sizable open texts for those branches with formulaic poetry or ritual language: the Iguvine Tables are the main Italic ritual text. All three are OCR, unlemmatized and mixed with apparatus or translation. They need cleanup and a lemma table (the Sprachschatz and Buck's glossary can supply one) before they can be counted.

## Not obtained (needs David)

- **Diorisis** (lemmatized Greek: Hesiod, Hymns, Pindar, tragedy, Herodotus): figshare is blocked by this machine's DNS filter; the licence is unverified.
- **kaikki all-languages dump** (3.08 GB) for Avestan, Old Prussian, Luwian, Oscan, Proto-Hellenic: over the size cap.
- **ACLT Luwian corpus** (no download, no licence), **ASPR** (copyright renewal unverified), **Dainu skapis** (unreachable or Cloudflare-blocked), **CEToM Tocharian** (server error), **Menotec** (no licence). Earlier items (TITUS, CELT, CorPH, YCOEP…) are in the manifest's round-1 list.

## Round 4 (acq2): wider daughter corpora (2026-10-23)

Goal: un-skew the cross-branch search (Celtic was ~820 tokens) and, at David's request, collect as large an open daughter corpus as possible. Provenance, sha256 and quoted licences are in `raw/MANIFEST.md` (round 4 sections). Most new material is OCR of public-domain editions, so token counts are whitespace tokens of the whole file; the "≈ target-language" figure is a rough line-level stopword vote (±30%), because the editions interleave text with translation, notes and glossary. None of the OCR is lemmatized; all of it needs language separation, diacritic repair and a lemma table before counting.

### Celtic

| Source | Dir | Language(s) | Size (tokens) | Lemmatized | Format | Licence |
|---|---|---|---|---|---|---|
| **Würzburg glosses** (Doyle, wurzburg.ie data) | `oldirish-wurzburg-doyle` | Old Irish (8th c.), Latin lemmata | 27.7k tokens in 3,648 glosses; ~10.1k Irish tokens POS+lemma-tagged | partly (UD UPOS, lemma, features) | JSON | CC BY 4.0 |
| **UD Old Irish, full files** (DipSGG `incomplete.conllu` + DipWBG) | `oldirish-ud-full-20261023` | Old Irish (St Gall Priscian glosses, 9th c.) | 21.4k tokens (3,406 glosses), 18.1k lemmatized; + 194 (Wb) | yes (UPOS, lemma, features; dependencies only in test set) | CoNLL-U | St Gall NC; Wb CC BY-SA 4.0 |
| Old Irish WordNet (Doyle) | `oldirish-sga-wordnet-doyle` | Old Irish lemmas → English WordNet senses | lexicon (+ a copy of DipSGG CoNLL-U) | n/a | YAML (GWA LMF), CSV | CC BY 4.0 (bundled CoNLL-U NC) |
| Stokes 1905, *Félire Óengusso* | `oldirish-felire-oengusso-stokes-1905` | Old Irish verse (c. 800) + Middle Irish scholia | 212k; Irish ≈ 58k | no | OCR text | PD |
| Windisch 1905, *Táin Bó Cúalnge* (LL) | `oldirish-tbc-windisch-1905` | Middle Irish saga (rec. II; rec. I variants) + German | 415k; Irish ≈ 120k | no | OCR text | PD |
| *Irische Texte* ser. 1–4.1 (1880–1900) | `oldirish-irische-texte-1880-1909` | Old/Middle Irish sagas, hymns, Acallam; Windisch's Wörterbuch | 908k; Irish ≈ 350k | no (glossary) | OCR text | PD |
| *Ancient Laws of Ireland* 1–6 (1865–1901) | `oldirish-ancient-laws-ireland-1865-1901` | Old Irish law (Senchas Már etc.) + commentary, English | 1.52M; Irish ≈ 320k | no (Atkinson glossary) | OCR text | PD |
| Meyer's editions (12 items, 1892–1919) | `oldirish-meyer-editions-1892-1919` | Old/Middle Irish: archaic rhymeless verse (*Über die älteste irische Dichtung*), Voyage of Bran, Triads, Cáin Adamnáin, Fianaigecht, Aislinge... | 592k; Irish ≈ 135k | no | OCR text | PD (2 NLS scans NC) |
| Stokes 1883, *Saltair na Rann* | `middleirish-saltair-na-rann-stokes-1883` | Middle Irish verse (c. 988) | 45k; Irish ≈ 35k | no (glossary) | OCR text | PD text, NLS scan NC |
| Stokes 1887, *Tripartite Life of Patrick* | `oldirish-tripartite-life-stokes-1887` | Middle Irish/Latin; Old Irish Armagh texts, hymns | 306k; Irish ≈ 53k | no | OCR text | PD |
| Stokes 1890, *Lives of Saints from the Book of Lismore* | `middleirish-lismore-lives-stokes-1890` | Middle Irish prose | 236k; Irish ≈ 68k | no | OCR text | PD |
| *Ériu* 1–10 (1904–28) | `celtic-journal-eriu-1904-1928` | Old/Middle Irish text editions + English | 800k; Irish ≈ 180k | no | OCR text | US-PD (research-only) |
| *ZCP* 1–14, 16 (1897–1926) | `celtic-journal-zcp-1897-1926` | Irish (some Welsh/Breton) editions + German/English | 2.64M; Irish ≈ 510k | no | OCR text | US-PD (research-only) |
| *Revue celtique* 1–45 (1870–1928) | `celtic-journal-revue-celtique-1870-1928` | Irish (Stokes's saga, Dindshenchas and annal editions), Breton, Welsh, Gaulish + French/English | 7.64M; Irish ≈ 0.78M | no | OCR text | US-PD (research-only) |
| *Archiv für celtische Lexikographie* 1–3 | `celtic-archiv-celt-lexikographie-1898-1907` | Irish glossaries (Cormac, O'Davoren) and texts | 625k; Irish ≈ 190k | no | OCR text | PD |
| Reference: Thurneysen *Handbuch* 1909, Pedersen *VKG* 1909–13, Stokes *Urkeltischer Sprachschatz* 1894, Holder *Alt-celtischer Sprachschatz* I | `celtic-reference-pd-1894-1913` | grammar/lexica (German) | 1.68M | n/a | OCR text | US-PD (Thurneysen, Pedersen research-only); Stokes, Holder PD |
| Dottin 1920, Rhŷs 1911/1913, Hübner 1893 | `gaulish-pd-editions-1893-1920` | Gaulish, Cisalpine Celtic, Celtiberian inscriptions with French/English/Latin commentary | 358k (inscription text small) | no (Dottin glossary) | OCR text | PD |
| **Lexicon Leponticum** | `celtic-lepontic-lexlep` | Lepontic / Cisalpine Gaulish: 495 inscriptions, 628 word and 202 morpheme entries | ~1k inscription tokens | yes in effect (morpheme analyses) | MediaWiki wikitext in JSONL | NC (research-only) |
| Skene 1868, *Four Ancient Books of Wales* | `welsh-skene-four-ancient-books` | Old/Middle Welsh poetry (Gododdin, Taliesin, Black Book, Red Book) + English | v2 101k, Welsh ≈ 35–50k; v1 137k English | no | OCR text (good) | PD |
| Rhŷs & Evans 1887, *Text of the Mabinogion* (Red Book) | `welsh-redbook-mabinogion-rhys-evans-1887` | Middle Welsh prose tales | 96k; Welsh ≈ 75k | no | OCR text (diplomatic, fair) | PD |
| Evans 1907, *White Book Mabinogion* | `welsh-white-book-mabinogion-evans-1907` | Middle Welsh prose | 118k; Welsh ≈ 90k | no | OCR text (fair–poor) | PD |
| Rhŷs & Evans 1890, *Text of the Bruts* | `welsh-redbook-bruts-rhys-evans-1890` | Middle Welsh chronicles | 139k; Welsh ≈ 105k | no | OCR text (fair) | PD |
| Evans 1911, *Poetry in the Red Book of Hergest* | `welsh-redbook-poetry-evans-1911` | Middle Welsh court and saga poetry | 91k; Welsh ≈ 80k | no | OCR text (poor) | PD (US) |
| Evans 1910/1915, *Book of Taliesin* | `welsh-book-of-taliesin-evans-1910` | Old/Middle Welsh poetry | 105k; Welsh ≈ 32k | no | OCR text (poor/fair) | PD (US) |
| Evans 1906, *Black Book of Carmarthen*; 1908, *Book of Aneirin* | `welsh-black-book-carmarthen-evans-1906`, `welsh-book-of-aneirin-evans-1908` | Old/Middle Welsh poetry (Y Gododdin) | 40k + 76k; Welsh ≈ 15k + 25k | no | OCR text | PD |
| Williams ab Ithel 1852, *Y Gododin* (Gutenberg #9842) | `welsh-gododin-gutenberg-9842` | Welsh (normalised) + English | 44.5k; Welsh ≈ 7k | no | clean text | PD |
| *Myvyrian Archaiology* 1870 | `welsh-myvyrian-archaiology-1870` | Welsh poetry, triads, Bruts, laws (normalised; includes Iolo forgeries) | 865k; Welsh ≈ 600k | no | OCR text (good) | PD |
| Owen 1841, *Ancient Laws and Institutes of Wales* | `welsh-ancient-laws-owen-1841` | Middle Welsh law + English, Latin | 809k; Welsh ≈ 280k | no | OCR text (fair) | PD |
| Norris 1859 *Ancient Cornish Drama*, Stokes 1864/1872 (*Gwreans an Bys*, *Beunans Meriasek*) | `cornish-middle-pd-editions-1859-1872` | Middle Cornish verse drama + English | 328k; Cornish ≈ 110k | no (glossaries) | OCR text (good) | PD |
| La Villemarqué 1865 *Grand mystère de Jésus*; Loth 1884 *Vocabulaire vieux-breton* | `breton-middle-pd-editions-1865-1884` | Middle Breton drama + French; Old Breton glossary | 192k; Breton ≈ 30k | no | OCR text | PD |

**What this adds.** Celtic goes from ~820 lemmatized tokens to ~49k glossed Old Irish tokens (28k of them lemmatized: St Gall 18k, Würzburg 10k), plus roughly 2.8M Irish and 1.4M Welsh word tokens of unlemmatized OCR (estimates), and smaller Cornish and Breton sets. The formula-relevant core is: Old Irish archaic verse (Meyer's rhymeless poems, Félire, Saltair), the Táin and Ulster/Fenian sagas (Irische Texte, Windisch, Ériu, ZCP), the law tracts (Senchas Már, with legal formulas and triads), and Welsh heroic poetry (Gododdin, Taliesin, Llywarch Hen in Skene, the Red Book, the Myvyrian). The Welsh diplomatic editions (Evans, Rhŷs & Evans) need character normalisation (OCR renders insular w as `O`, long r as `2`/`z`); Skene vol. 2 and the Myvyrian are in normalised print orthography and OCR cleanly. Continental Celtic is now present but tiny (Lepontic via LexLep; Gaulish and Celtiberian only inside Dottin, Rhŷs and Hübner). Lemma → PIE for Celtic can now go through Stokes's *Urkeltischer Sprachschatz* (Proto-Celtic with PIE cognates) and Pedersen, besides kaikki Proto-Celtic.

**Celtic, not obtained (needs David).** CELT (consent needed for 250 early Irish texts, ≈1.47M words, incl. both Táin recensions and the Metrical Dindshenchas: email b.faerber@ucc.ie); St Gall Priscian database (content licence unstated), Milan glosses dictionary (no licence; FileMaker app), CorPH/ChronHib (as before); eDIL (site unreachable from here; online lookup only); RIIG (site offline) and Hesperia (unreachable) for Gaulish/Celtiberian; Rhyddiaith Gymraeg 1300–1425 (Cardiff copyright, no download). In copyright, so only David's own copies would help: Vendryes *LEIA*, Thurneysen *Grammar of Old Irish* (1946; the 1909 German *Handbuch* is here), O'Rahilly's Táin editions (1967/1976), Binchy *Corpus Iuris Hibernici*, Ifor Williams *Canu Aneirin*/*Canu Taliesin*, Lambert/RIG, Wodtko *MLH* V.1. A better Thesaurus Palaeohibernicus scan is not needed for Würzburg and St Gall now; it still matters for the Milan glosses and the minor glosses and poems in vol. 2.


### Balto-Slavic

| Source | Slug | Language(s) | Size (word tokens) | Lemmatized | Format | Licence |
|---|---|---|---|---|---|---|
| Vuk Karadžić, Srpske narodne pjesme (sr.wikisource) | `serbian-vuk-wikisource` | Serbian (Štokavian, Cyrillic) | 838,871 (stripped wikitext of 1,827 song pages; index and preface pages excluded) | no | MediaWiki wikitext JSONL + derived plain text | CC BY-SA (text PD) |
| Kirsha Danilov + Rybnikov pt. I + 2 Hilferding byliny (ru.wikisource) | `russian-byliny-wikisource` | Russian (byliny; pre-reform orthography for Rybnikov /ДО) | 63,203 (stripped wikitext; modern-orthography duplicates excluded) | no | wikitext JSONL + plain text | CC BY-SA (text PD) |
| Hilferding, Onezhskie byliny 2nd ed. vols. 2–3 | `russian-hilferding-1894-archiveorg` | Russian (pre-reform) | 257,501 (whole OCR incl. headers and notes) | no | archive.org OCR txt | PD |
| Kireevsky, Pesni vyp. 1, 4–10 | `russian-kireevsky-1860-1874-archiveorg` | Russian (pre-reform) | 821,883 (whole OCR incl. Bessonov's commentary) | no | archive.org OCR txt | PD |
| Rybnikov, Pesni parts 1–4 | `russian-rybnikov-1861-1867-archiveorg` | Russian (pre-reform) | 512,950 (whole OCR incl. notes) | no | archive.org OCR txt | PD |
| Miladinov, Bălgarski narodni pesni 1861 (mk.wikisource) | `macedonian-miladinov-1861-wikisource` | Macedonian/Bulgarian dialects (modern Macedonian respelling) | 121,840 (stripped wikitext; second old-orthography column not counted) | no | wikitext JSONL + plain text | CC BY-SA (text PD) |
| Trautmann, Die altpreußischen Sprachdenkmäler 1910 | `oldprussian-trautmann1910` | Old Prussian + German | 198,622 (whole OCR; mostly German apparatus, Old Prussian a small fraction) | no (glossary) | archive.org OCR txt | PD |
| CCMH Old Church Slavonic source corpus | `ocs-ccmh` | Old Church Slavonic | ≈303,600 (word tokens of the `.txt` files, line ids dropped) | no | ASCII-translit txt + CES XML | CC BY |
| Rhesa, Dainos 1825 + 1843 | `lithuanian-rhesa-dainos-1825-1843` | Lithuanian + German | 60,369 (whole OCR) | no | archive.org OCR txt | PD |
| Nesselmann, Littauische Volkslieder 1853 | `lithuanian-nesselmann-1853` | Lithuanian + German | 166,420 (whole OCR) | no | archive.org OCR txt | PD |
| Schleicher, Litauische Märchen … Lieder 1857 | `lithuanian-schleicher-1857` | Lithuanian + German | 87,455 (whole OCR) | no | archive.org OCR txt | PD |
| Leskien & Brugmann, Litauische Volkslieder und Märchen 1882 | `lithuanian-leskien-brugmann-1882` | Lithuanian + German | 210,713 (whole OCR) | no | archive.org OCR txt | PD |
| Bartsch, Dainu balsai vol. 1 1886 | `lithuanian-bartsch-dainubalsai-1886` | Lithuanian + German | 109,954 (whole OCR) | no | archive.org OCR txt | PD |
| Juškevič, Lietuviškos dajnos vols. 1, 3 + Svotbinės dajnos 1883 | `lithuanian-juskevic-dainos-1880-1883` | Lithuanian | 269,536 (whole OCR) | no | archive.org OCR txt | PD |
| Mažvydas, Catechism 1547 (lt.wikisource) | `lithuanian-mazvydas-1547-wikisource` | Old Lithuanian | 6,482 (stripped wikitext) | no | wikitext JSONL + plain text | CC BY-SA (text PD) |

**What this adds.**

- `serbian-vuk-wikisource`: the largest clean oral-formulaic epic in the corpus (deseterac heroic songs plus women's/lyric songs). Clean Cyrillic transcription. The best Slavic counterpart to Homer for formula density.
- `russian-byliny-wikisource`: clean, small. Kirsha Danilov is the oldest bylina collection (18th c.).
- `russian-hilferding-1894-archiveorg`: the classic Onega bylina corpus, sung by named singers. Large but OCR (pre-reform ѣ errors). Vol. 1 is missing.
- `russian-kireevsky-1860-1874-archiveorg`: byliny and historical songs, a large set but OCR and heavy with commentary.
- `russian-rybnikov-1861-1867-archiveorg`: the first major Olonets bylina collection (complete 4 parts). OCR, fair.
- `macedonian-miladinov-1861-wikisource`: South-East Slavic (Macedonian/Bulgarian) epic and ritual songs (samovila, Marko). Clean, but in modern respelling.
- `oldprussian-trautmann1910`: the whole Old Prussian corpus (tiny and precious) with glossary. OCR needs scan check.
- `ocs-ccmh`: the canonical OCS gospels under CC BY. Adds Assemanianus and Savvina kniga. A parallel-text control, not poetry.
- Lithuanian dainos (Rhesa, Nesselmann, Schleicher, Leskien–Brugmann, Bartsch, Juškevič): the archaic Baltic lyric and ritual (wedding) song tradition, the closest Baltic analogue for inherited poetic diction. All OCR. Nesselmann, Leskien–Brugmann and the 1883 Juškevič are the cleanest; the Rhesa and Juškevič vols. 1/3 OCR is poor.
- `lithuanian-mazvydas-1547-wikisource`: the earliest Lithuanian text, a clean diplomatic transcription. Prose and hymn; mainly linguistic.


### Tocharian, Anatolian, Armenian, Albanian, Iranian, Phrygian; TITUS 2.0; UD sweep

| Source | Dir | Language(s) | Size | Lemmatized | Format | Licence |
|---|---|---|---|---|---|---|
| TITUS 2.0 Tocharian A (Sieg & Siegling 1921) | `titus2-tocharian` | Tocharian A | ≈106k whitespace tokens in TEI `<text>` (tags stripped; includes line numbers and some Sanskrit) | no | TEI XML + TITUS YAML | NC |
| TITUS 2.0 Lydian inscriptions (Gusmani) | `titus2-anatolian` | Lydian (+ Aramaic) | ≈3.4k tokens (same method) | no | TEI XML | NC |
| TITUS 2.0 Koriwn, Life of Maštoc' | `titus2-armenian` | Classical Armenian (translit.) | ≈6.1k tokens | no | TEI XML | NC |
| TITUS 2.0 Iranian (Šāyist nē šāyist; Manichaean Sermon of the Soul; Sindbad-Nāme) | `titus2-iranian` | Pahlavi, Manichaean MP/Parthian/Sogdian, New Persian | ≈16.1k + 8.5k + 21.6k (NP) tokens | no | TEI XML | NC |
| TITUS 2.0 Old Albanian (Buzuku 1555, Bogdani 1685, Blanchus 1635) + Phrygian | `titus2-other-ie` | Old Gheg Albanian; Old/Neo-Phrygian | Buzuku ≈126k, Bogdani ≈118k, Blanchus ≈21.6k, Phrygian ≈3.6k tokens | no | TEI XML | NC |
| TITUS 2.0 Germanic (Edda Neckel, Otfrid, Hildebrandlied, MHG epics) | `titus2-germanic` | ON, OHG, MLG, MHG | Edda ≈43k, Otfrid ≈67k, OHG small texts ≈11k, MHG ≈600k | no | TEI XML | NC |
| TITUS 2.0 Slavonic (Suprasliensis, Vita C&M, Old Russian OT, Old Czech) | `titus2-slavonic` | OCS, Old Russian, Old Czech | Supr ≈128k, VCM 13k, ORuss ≈121k, OCz ≈40k | no | TEI XML | NC |
| TITUS 2.0 Baltic (Donelaitis, Engels) | `titus2-baltic` | Old Lithuanian / 18th-c. Lithuanian | ≈28k | no | TEI XML | NC |
| TITUS 2.0 Mabinogi | `titus2-celtic` | Middle Welsh | ≈24k | no | TEI XML | NC |
| TITUS 2.0 Italic (Osco-Umbrian corpus etc.) | `titus2-italic` | Oscan, Umbrian, Old Latin, Old Italian, Gal.-Port. | Osco-Umbrian ≈17k (with glosses) | no | TEI XML | NC |
| TITUS 2.0 Odyssey (Ludwich) | `titus2-greek` | Homeric Greek | ≈87k | no | TEI XML | NC |
| TITUS 2.0 Indic (AV-Pariśiṣṭa etc.) | `titus2-indic` | Sanskrit | ≈63k | no | TEI XML | NC |
| UD Hittite-HitTB | `hittite-ud-hittb` | Hittite | 1,309 tokens (CoNLL-U word lines) | yes (manual) | CoNLL-U | CC BY-SA |
| UD Classical Armenian-CAVaL | `armenian-ud-caval` | Classical Armenian | 99,664 tokens (Gospels 82k, Xorenac'i I 17.7k) | yes | CoNLL-U | NC |
| UD Middle Armenian-ArmTDP | `armenian-ud-middle-armtdp` | Middle Armenian | 1,093 | yes | CoNLL-U | CC BY-SA |
| UD Phrygian-KUL | `phrygian-ud-kul` | Phrygian | 1,921 | yes | CoNLL-U | CC BY-SA |
| UD Umbrian-IKUVINA | `umbrian-ud-ikuvina` | Umbrian | 1,162 | partly (96 lemmas) | CoNLL-U | CC BY-SA |
| UD Old English-Cairo | `oldenglish-ud-cairo` | Old English | 171 | yes | CoNLL-U | CC BY-SA |
| UD Old English-OEDT (dev) | `oldenglish-ud-oedt-dev` | Old English prose | 26,310 | yes | CoNLL-U | CC BY-SA |
| UD Old Saxon-ConOS (dev) | `oldsaxon-ud-conos-dev` | Old Saxon (Heliand, Genesis) | 1,951 | yes | CoNLL-U | CC BY-SA |
| UD Middle Irish-CritMITB (dev) | `middleirish-ud-critmitb-dev` | Middle Irish | 3,047 | mostly | CoNLL-U | CC BY-SA |
| UD Old East Slavic-RNC | `oldeastslavic-ud-rnc` | Middle Russian 1300–1700 | 168,064 | yes | CoNLL-U | CC BY-SA |
| UD Old East Slavic-Birchbark | `oldeastslavic-ud-birchbark` | Old Novgorod / East Slavic vernacular | 27,907 | yes | CoNLL-U | CC BY-SA |
| Digital Matenagirk Hayots (5th-c. Classical Armenian authors) | `armenian-dmhp-matenagirk` | Classical Armenian | 570,388 tokens (`<w>` elements in `.vert`); 584,840 whitespace tokens in `_text.txt` | yes (automatic lemma + POS) | vertical XML-ish + plain text + raw OCR | CC BY |
| Mxit'ar Goš law code (Hovhannisyan) | `armenian-gosh-lawcode` | Classical/Middle Armenian (12th c.) | ≈39.1k whitespace tokens (Grabar column) | no | CSV | CC BY |
| Invisible East Digital Corpus | `iranian-invisible-east` | Bactrian, Sogdian, Middle Persian, New Persian, Arabic, Judeo-Persian | Bactrian ≈9k, Sogdian ≈2.9k, MP ≈0.5k, NP ≈35k (transcription + transliteration fields) | no | XML (JSON-like dict export) | CC BY |
| ŠKZ trilingual (Shamsian & Berti) | `iranian-skz-trilingual` | Middle Persian, Parthian, Greek | MP ≈1.6k, Parthian ≈1.5k, Greek ≈1.7k | no (word-aligned) | CSV/TSV | CC BY |
| PALaC working data | `anatolian-palac-workingdata` | Anatolian contact lexicon (Hitt., Luw., Lyc., Lyd., etc.) | 10,271 table rows (lexical, not text) | n/a | SQL + CSV | CC BY |
| Sieg & Siegling 1921, Tocharische Sprachreste I (OCR) | `tocharian-sieg-siegling-1921` | Tocharian A (+ German intro) | ≈99.4k whitespace tokens, whole djvu.txt | no | archive.org OCR text | PD |
| Kalinka 1901, TAM I (OCR) | `lycian-kalinka-tam1-1901` | Lycian (OCR-garbled) + Latin | ≈80.2k whitespace tokens, mostly Latin | no | archive.org OCR text | PD |
| hy.wikisource Classical Armenian (Agat'angełos, Ełišē, Narekac'i, Koriwn, Xorenac'i Ołb) | `armenian-hywikisource` | Classical Armenian | ≈180.6k whitespace tokens after stripping wiki markup and header templates (Agat'angełos 73.9k, Narekac'i 57.5k, Ełišē 40.6k, Koriwn 6.4k, Ołb 2.0k) | no | MediaWiki wikitext in JSONL | CC BY-SA |
| Classical Armenian PD editions on archive.org (Xorenac'i 1913, Sebēos 1913, Koriwn 1900) | `armenian-archiveorg-pd-editions` | Classical Armenian | ≈361k whitespace tokens of OCR (Xorenac'i 246k incl. apparatus, Sebēos 62k, Koriwn+ 53k) | no | archive.org OCR text | PD |

**What this adds.**

- titus2-tocharian: the first Tocharian running text in the corpus, the whole Tocharian A Sieg–Siegling corpus (Buddhist narrative and verse, metrical: Puṇyavanta-, Maitreya-texts). Clean digital transliteration, not OCR. Tocharian B is still missing.
- titus2-anatolian: the complete Lydian corpus, including the Lydian verse inscriptions (the only poetic Anatolian outside Hittite/Luwian ritual). Tiny but clean.
- titus2-armenian: the first non-biblical Classical Armenian text (5th-c. hagiography, prose). Clean.
- titus2-iranian: the first Middle Iranian text (Zoroastrian legal-ritual Pahlavi; Manichaean homily). Prose and clean, but marginal for formulas. Sindbad-Nāme is New Persian and only a control.
- titus2-other-ie: the whole of Old Albanian's two main 16th–17th-c. texts. Buzuku is the oldest Albanian book (liturgical translation; archaic Gheg). Clean diplomatic transcription. Phrygian is the full small corpus, a second witness next to UD Phrygian-KUL.
- `oskum` gives a clean digital Osco-Umbrian corpus (better than the Buck OCR). `edda` gives a clean digital Codex Regius (Neckel), better than the FJ 1926 OCR but under an in-copyright edition. `supra` gives a second Suprasliensis witness (TOROT has it). Otfrid and the Hildebrandlied are OHG verse. All are clean TEI.
- CAVaL: the first lemmatized **non-biblical** Classical Armenian text: Xorenac'i's History, all of Book I (sent_ids run through chapter I.32, so the chapter with the Vahagn birth song, I.31, is included). That song is the best-known Armenian inherited-poetry fragment. The Gospels part duplicates PROIEL.
- HitTB: manual lemmas, but the sentences are grammar-book examples, so it is useful only as a lemma/morphology check for TLHdig.
- Phrygian-KUL: a lemmatized Phrygian (Balkan IE) corpus, including the formulaic Neo-Phrygian curse inscriptions.
- The rest are small or late. The Birchbark letters are useful for a few charms. RNC is Middle Russian chancery prose, mostly irrelevant for formulas.
- **DMHP is the biggest single gain here.** It is the whole 5th-c. "Golden Age" Classical Armenian corpus, ≈570k tokens, lemmatized, CC BY. It includes the epic-tradition material in Xorenac'i (Vahagn song, Artašēs/Artawazd songs) and P'awstos (oral epic prose) that matters most for Armenian inherited formulas. Raw OCR is near-clean; the lemmas are automatic.
- Gosh: medieval legal prose, low formula value, but CC BY and clean.
- IEDC and ŠKZ: the only open Bactrian, Sogdian and Parthian text found. Documents and inscriptions, tiny, for lexicon and onomastics rather than formulas. ŠKZ has the Sasanian royal titulature, which is formulaic.
- PALaC: an Anatolian loanword/contact annotation table, useful to exclude contact lexemes from inheritance claims. Not text.
- Sieg & Siegling gives a PD (non-NC) copy of Tocharian A, but with noisy OCR. Use it to back up or check `titus2-tocharian`. Kalinka is kept only as the PD page-image reference for Lycian (the scans could be re-OCRed with a Lycian model). As text it adds nothing until then.
- hy.wikisource: clean, human-transcribed Grabar. It is an independent witness for Agat'angełos, Ełišē and Koriwn against the DMHP OCR, and it adds **Narekac'i** (10th-c. high-register religious poetry), which DMHP lacks. Text is clean, not OCR.
- Sebēos is new 7th-c. historiography with a few embedded epic passages. The other two are backups to DMHP (Xorenac'i, Koriwn) with variant apparatus. All are OCR and need cleaning.
