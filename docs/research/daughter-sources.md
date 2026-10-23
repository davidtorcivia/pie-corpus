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
