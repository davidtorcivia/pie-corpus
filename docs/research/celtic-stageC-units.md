# Celtic text layer for 8c Stage C (2026-10-24)

The pivot text for Stage C of the 8c formula-reading experiment (`docs/research/8c-preregistration.md`, Stage C) is the Celtic corpus. This file describes the unit layer built for it. The Celtic word → PIE mapping is a separate job; this layer only makes sure the pivots are clean, unique and correctly attributed.

**File:** `raw/daughters/celtic-stageC/units.jsonl`. It is gitignored and must never be committed (it holds CELT text under consent, and research-only and NC text). It has 375,098 units: 5.20M tokens before dedupe, and 325,562 units / 4.46M tokens with `dup_of` null. sha256 `c0ec53001831a61064a10f1de67f27cb25f88d7288c071a4036f3d47c11ccef6`, also recorded in `raw/MANIFEST.md` under CELT. Tokens are whitespace tokens containing a letter, digit or ⁊.

**Fields.**
- `id`, `text`, `lang` (`sga` / `mga` / `ga-early` / `wlm` / `owl`).
- `date` (`from-to`), `date_from`, `date_to`, `date_basis`, `date_ms_only`.
- `genre`, `source`, `licence` (`consent-train` / `research` / `pd` / `cc-by` / `nc`).
- `edition` and `edition_type` (`critical` / `diplomatic`).
- `dup_of`: the id of the preferred copy, or null.
- `kind`: `l` verse line, `s` prose sentence, `gloss`, `lg`.

Extra fields:
- CELT: `stanza`, `year`.
- Glosses: `ref`.
- OCR: `title`, `ms`, `ms_date`, `lang_basis`, `stanza`, `ocr: true`.

**Ids.**
- CELT keeps its own unit ids (`G301035:#1/…:n`).
- OCR ids trace back to the raw file: `<dir>:<file stem>:L<first line>-L<last line>[:k]`.
- Glosses: `wb:<folio>:<gloss no.>` and `sg:<ref>:<sent_id>`.

**Provenance** is kept next to the file, all gitignored:
- `build/`: the scripts, mapping and check briefs, and CELT edition table.
- `sections/`: the per-text section tables that carry every OCR date.
- `check-round1/`, `check-round2/`: the hand-labelled samples.
- `stats.txt` and `stats.json` (the count tables below).

The scripts were run from the session scratchpad. They read `raw/` as data only, with `python3 -I`.

## Sources

| Source | Units in | Basis | Licence tag |
|---|---:|---|---|
| CELT (`celt-ucc/units.jsonl`), sga + mga + ga-early | 240,953 | CELT's own clean layer | `consent-train`. The 58 G4000xx OUP files (3,909 units) are `research` (David's ruling). G100055/56, G600019/31 are `nc` (CC BY-NC-SA). |
| Würzburg glosses (Doyle, `glosses.json`) | 3,512 | Thes. Pal. I text. Latin `[GLat]` spans and footnote markers removed; 136 Latin-only glosses dropped. | `cc-by` |
| St Gall Priscian glosses (UD DipSGG, all 3,406) | 3,405 | `Foreign=Yes` (Latin) tokens removed | `nc` |
| PD Irish OCR: Félire (Stokes 1905); Windisch TBC 1905; *Irische Texte* ser. 1–4.1; Meyer's editions (11 items) | 30,402 | sections below | `pd` (Fianaigecht and Aislinge NLS scans: `nc`) |
| *Ériu* 1–10, *ZCP* 1–14 + 16, *Revue celtique* 1–45 | 61,232 | sections below | `research` (US-PD only) |
| Welsh OCR: Skene vol. 2; Red Book Mabinogion (Rhŷs & Evans 1887); White Book (Evans 1907); Red Book Bruts (1890); Red Book Poetry (Evans 1911) | 35,594 | sections below; Welsh found inside RC and ZCP is included in the journal rows | `pd` |

**Left out, with reasons:**
- **CELT units not in Stage C's language set:** 6,845 units of Modern Irish (`ga`, > 1650) and 2,550 `undated` units (11 texts).
- **Ancient Laws of Ireland (all 6 volumes).** The Irish is printed in Irish type, and the OCR of it is unreadable (e.g. `CCchjabail cn.eifi floij;6t>`). The two Atkinson volumes are glossary and index. Nothing usable could be kept, so the law material in the layer is CELT's 31k law tokens plus law texts edited in the journals.
- **Meyer item `anecdotaoxonien00stokgoog`.** Despite its id, it is the Ethiopic Book of Jubilees (Anecdota Oxoniensia, Semitic series), not Stokes's Irish volume.
- **Skene vol. 1:** English translation only.
- **Not in this brief:** the Stokes OCR of Saltair na Rann and the Lismore Lives (CELT has both: G202001, G201001), the Tripartite Life, the Evans diplomatic Black Book, Aneirin and Taliesin (Skene's texts of those books are used), the Myvyrian, Owen's Welsh laws, and Breton, Cornish and Gaulish.
- **Thesaurus Palaeohibernicus OCR (Milan and minor glosses):** deferred, because it has the worst diacritics in the set. The Milan glosses are therefore missing.
- **DipWBG:** a 194-token subset of Würzburg.
- **Inside the OCR**, the section tables cut post-1650 Irish, Scottish Gaelic, Manx, Breton, Cornish and Gaulish, plus glossaries, indices, Windisch's *Wörterbuch*, variant appendices, catalogues of first lines, grammar and etymology articles, and reviews.

## 1. OCR cleanup

**Classification.** Each OCR line gets one label from a pipeline written for this job (`build/celtclean_ocr.py`):

1. **Language.** A character 1–4-gram naive-Bayes model is trained on:
   - Irish: CELT units.
   - English: CELT's translations.
   - Latin: Perseus.
   - German, French, Welsh and Breton: OCR lines with a dominant stopword vote (from Windisch/ZCP/Thurneysen, RC, the Myvyrian/Skene and La Villemarqué).

   The per-line scores are smoothed by a Viterbi pass with a language-switch penalty. A long line that disagrees strongly with its context keeps its own label.
2. **Page headers.** Short lines that start or end with a page number and are upper-case or repeat in the file; lines full of sigla that end in a number (`LL. p. 69a, St. p. 22a … 193`); and isolated numbered short lines. Pure number, roman-numeral and printer's-signature lines are dropped too.
3. **Footnote zones.** A zone opens at a line that follows a blank line, starts with a footnote marker (digit, `^ * » " '` …) and contains a siglum or editorial word (`St.`, `LU.`, `om.`, `add.`, `leg.`, `fehlt`, `vgl.` …). It closes at the next page header, after 7 consecutive lines without a marker, after 45 lines, or at a printed text line number (a multiple of 5).

   Requiring a siglum or editorial word stopped numbered verse and section headings (e.g. Maelisu's hymn in *Irische Texte* I) from being taken for footnotes. In Windisch, the remaining Irish lines inside footnote zones were checked and are the Stowe/Rec. I variant readings.
4. **Apparatus lines.** A footnote marker together with a siglum or editorial word, or a dense run of sigla and numbers.
5. **Garbage.** An Irish or Welsh line is discarded if more than a third of its tokens are malformed or its per-character score is below CELT's 0.5th percentile.
6. **Welsh diplomatic letters.** Before classification, Welsh files are normalised word-internally: insular w printed as `O`/`C`/`6` → `w`, long r printed as `z`/`x`/`2` → `r`, long s printed as `f` before `t`/`c` → `s`, the `ll` ligature printed as `H`/`Il` → `ll`.

**Section tables.** Which line ranges are an edited text, which text they belong to, and its date come from section tables written by seven mapping agents, one per edition group, under one brief (`build/celtclean-mapping-brief.md`).
- 533 `keep` and 542 `cut` rows over 95 OCR files (92 with kept text).
- The agents read the region summaries, the page maps and the editors' introductions.
- Only `keep` rows produce units. Glossaries, indices and word lists are `cut` explicitly, because a language model alone would keep them.

**Units.**
- **Verse/prose split.** A paragraph is verse if 75% of its lines are shorter than 0.72 × the file's typical prose line (at least 55 characters) and few end in a hyphen. A single short line counts as verse. A section can force verse or prose.
- **Verse:** one printed line per unit (`kind l`, with `stanza`).
- **Prose:** lines are joined and split into sentences at `[.?!]` + capital. The split never happens after `.i.`, `m.`, `mc.`, single letters or roman numerals. Sentences over 80 words are split at `;`/`:`.
- **Hyphenated line breaks** are joined without the hyphen, except after an Irish preverb or particle (`ro-`, `do-`, `ar-`, `ní-` …), where the hyphen is kept.

**Inline cleanup.** The following are removed:
- Leading stanza or line numbers and trailing printed line numbers.
- Footnote digits and glyphs glued to words (`Eclas1`, `calne®`), and line numbers glued to or splitting words (`chromm-2575 sciath`, `683othair`).
- Free-standing Arabic numbers. Irish numerals in the texts are roman (`.xii.`).
- Folio and page references (`(fo. 104b)`, `{LL. p. 61:)`).
- Editor's parentheticals: `(?)`, `(sic)`, `(i.e. …)`, numbered.
- Leading section numerals and letter labels, `(II)`, `K)`, `(Aided … .)`, verse speaker labels (`F. d.`, `Cc.`) and trailing `, L.`-type sigla.

Standalone `7` becomes `⁊`, and in Irish OCR `6` becomes `ó`.

Whole units are dropped (2,467) if they contain a strong siglum (`St.`, `LU.`, `LL.`, `YBL.`, `Eg.`, `MS.`, `om.`, `add.`, `leg.`, `vgl.`, `cf.`, `Tog.`, `Lism.` …), are variant lists (≥ 2 siglum tokens, outside annals and genealogies), or are Latin calendar headings (`kal.`, `nonas`, `idus`).

**Line labels inside the keep sections** (whitespace tokens): Irish 1.24M, Welsh 0.52M; English 0.92M, German 0.35M, French 0.13M, Latin 40k (translations, notes, introductions); footnote zones 0.49M; page headers 119k; apparatus lines 35k; garbage 32k.

**Hand check.** Reviewer agents labelled 100 random OCR units per edition by reading them blind. They had no access to the raw files or the classifier. Each unit was labelled TEXT (only Irish/Welsh text; OCR misspellings allowed), MIXED (text plus an intrusion: number, siglum, editor's word, translation fragment) or NOT (not Irish/Welsh text). **Precision** below is TEXT/100; TEXT+MIXED/100 is the share of units that are at least mostly Irish/Welsh.
- **Round 1** was run on the first full build.
- **Round 2** was run on fresh samples after fixing the round-1 failure classes at source: numbers, footnote glyphs, editor's parentheticals, trailing sigla, variant lists. It covered the seven Irish editions only, because the Welsh were already ≥ 97%.

After round 2, a further fix (line numbers inside words, section headings and numerals, speaker labels, Félire variant lists) cleaned or removed 18 of the 72 round-2 MIXED/NOT units and lost 1 TEXT unit. The figures below are as measured, before that fix. A last pass then:
- read White Book `02`/`20` as `or`/`rw`;
- read standalone Irish `0`/`4` as `ó`/`⁊`;
- stopped stripping a leading `a`/`i`/`o`/`y`/`O`.

The labelled samples were diffed against the final text: of 1,729 rows labelled TEXT, 2 no longer exist as units (one merged with its continuation line, one Stowe variant line now dropped as apparatus). 121 changed text, by footnote glyphs and markers removed, `.i.` spacing restored, or the letter readings just listed. None lost Irish or Welsh words beyond such stray tokens. The Welsh precision figures are from round 1, before all inline cleanup changes.

| Edition | Round 1 TEXT / MIXED / NOT | Round 2 TEXT / MIXED / NOT | Precision (latest round: 2 for Irish, 1 for Welsh) | TEXT+MIXED | ocr-bad |
|---|---|---|---:|---:|---:|
| Félire (Stokes 1905) | 93 / 3 / 4 | 90 / 5 / 5 | 0.90 | 0.95 | 0 |
| Windisch TBC 1905 | 91 / 7 / 2 | 82 / 15 / 3 | 0.82 | 0.97 | 0 |
| *Irische Texte* | 87 / 13 / 0 | 90 / 9 / 1 | 0.90 | 0.99 | 0 |
| Meyer's editions | 86 / 8 / 6 | 92 / 3 / 5 | 0.92 | 0.95 | 2 |
| *Ériu* | 85 / 9 / 6 | 92 / 5 / 3 | 0.92 | 0.97 | 1 |
| *ZCP* | 85 / 11 / 4 | 93 / 3 / 4 | 0.93 | 0.96 | 4 |
| *Revue celtique* (incl. its Welsh) | 80 / 13 / 7 | 89 / 4 / 7 | 0.89 | 0.93 | 3 |
| Skene, Four Ancient Books vol. 2 | 97 / 2 / 1 | n/a | 0.97 | 0.99 | 3 |
| Red Book Mabinogion | 99 / 0 / 1 | n/a | 0.99 | 0.99 | 1 |
| White Book Mabinogion | 100 / 0 / 0 | n/a | 1.00 | 1.00 | 2 |
| Red Book Bruts | 99 / 0 / 1 | n/a | 0.99 | 0.99 | 1 |
| Red Book Poetry | 99 / 0 / 1 | n/a | 0.99 | 0.99 | 2 |

**Remaining failure types:**
- Windisch's editor's notes and labels inside the text.
- Variant-reading lines made of sigla (Félire, Meyer).
- French or English translation fragments and headings in RC.
- Latin rubrics and scholia.
- Interleaved annal translations (RC's Tigernach).

The Welsh diplomatic texts are clean of intrusions but OCR-noisy throughout: ornamented initials misread (`J`, `Jc`, `l|`), `ỳ`/`ö` forms.

`ocr-bad` (more than about a third of words garbled) is 0–4% per edition. Light OCR damage (lost length marks, italic expansions read as `/i`, `w`, `z`) is common in all the Irish OCR. The Celtic → PIE mapping should expect it.

## 2. Dedupe

**Matching.** Matching runs on a normalised form only; the stored text is untouched (`build/celtclean_lib.py: dnorm`). The normalisation:
- Lowercases and strips accents and length marks.
- Maps `⁊`/`7`/`&`/`acus`/`agus` → `ocus`.
- Ignores mutations: prefixed `h-`/`n-`/`t-`; `mb nd ng bp gc dt bhf` → base; lenition `h` after a consonant.
- Collapses doubled letters, maps v→u, j/y→i, k→c, and ignores word division.

**Algorithm.**
- **Candidate search.** Each text (a CELT text id, or an OCR section) is turned into one string of character 6-grams. Every fourth 6-gram is indexed, using a deterministic CRC32 sample. Each unit votes for aligned offsets in other texts.
- **Containment.** The unit's full 6-gram set is compared with the target window. The thresholds are 0.6, or 0.45 when either side is OCR. Units under 25 normalised characters are matched only when sandwiched between matched neighbours.
- **Run requirement.** A match counts only as part of a passage: ≥ 3 consecutive units (one gap allowed) aligned to the same text, or ≥ 150 normalised characters, or a single unit ≥ 150 characters with containment ≥ 0.7. This keeps a recurring formula or stock line in two different texts from being merged; 18,694 short candidate runs were rejected this way.
- **Clustering.** Matched units are clustered (union-find), and each cluster keeps one preferred text. The preference order is:
  1. critical edition: CELT critical, glosses > OCR critical edition > CELT diplomatic (Lebor na hUidre G301900, Book of Leinster G800011A–F) > Welsh diplomatic;
  2. for verse, the copy with line division;
  3. licence (pd > cc-by > consent-train > nc > research);
  4. id.
- **`dup_of`.** Every other member gets `dup_of` = the unit of the preferred text that shares most 6-grams with it, so `dup_of` always points to a non-duplicate (checked: 0 chains). Where the two editions segment differently, the pointer is the best-overlapping unit, not an exact equivalent.

**Result:** 49,536 units (734k tokens) marked as duplicates.

| Duplicate → preferred | Units |
|---|---:|
| OCR → CELT critical | 30,199 |
| CELT diplomatic (LU/LL) → CELT critical | 6,885 |
| CELT diplomatic → OCR critical edition | 5,060 |
| OCR → OCR (journal ↔ book reprints, Red ↔ White Book, Red Book poetry ↔ Skene) | 4,000 |
| CELT critical → CELT critical (overlapping editions, recensions, annals copying each other) | 3,328 |
| CELT diplomatic → CELT diplomatic | 63 |
| CELT critical → glosses | 1 |

**Largest pairs:**
- *Irische Texte* IV Acallam → CELT G303000: 4,236.
- Windisch → O'Rahilly's LL Táin (G301035): 2,944. Windisch is 77% duplicate by tokens; most of the rest is footnote-level Stowe variants and OCR-damaged lines.
- Stokes's Félire OCR → CELT G200001: 2,000. This is the same 1905 edition. CELT lacks the scholia, so they stay.
- Red Book → White Book Mabinogion: 1,879.
- LU → TBC Rec. I (G301012): 1,564.
- Red Book Poetry → Skene's Red Book poems: 1,213.
- ZCP 6 → CELT G306000: 1,160.

The manifest's warning that CELT overlaps itself holds: LU and LL are now largely `dup_of` the separate critical editions.

**Precision.** A spot check of random duplicate pairs found the passage match correct throughout. About 2% of CELT-internal pointers in the annals and genealogies point to a neighbouring entry of the right passage rather than the exact sentence.

## 3. Dating

**CELT.** `date` is CELT's `<creation>` range, unchanged (`date_basis` `celt-creation`), with `lang` from CELT's own rules (annal entries by annal year). Four annal texts have no CELT date: Loch Cé G100010A/B, Chronicon Scotorum G100016 and Fragmentary Annals G100017, 11,181 units. They get the entry's annal year as both ends of `date`, with `date_basis` saying so.

**Glosses.**
- Würzburg: 700–800 (main hand mid/late 8th c.; MS c. 750–800).
- St Gall: 800–851 (MS written c. 845–851).

**OCR.** Every section carries the date the editor states for the text, with a `date_basis`:
- `editor-linguistic` (49,702 OCR units): the editor dates the composition or language. The section table quotes the dating sentence with its raw line number.
- `editor-ms-only` (38,543 units): the editor gives only the manuscript date. `date` is then the MS date and **`date_ms_only` is true**. This is the flag the brief asked for; all of these are OCR units.
- `none-stated` (38,983 units): the editor gives nothing usable. The mapping agent's period judgement from the language is used as a period range (sga 600–900, mga 900–1200, ga-early 1200–1650), and the section note says so. Evans 1911 (Red Book poetry) states no dates at all.

`ms` and `ms_date` carry the manuscript where the editor names it.

**OCR `lang`.**
- For Irish it follows the date midpoint (≤ 900 sga, ≤ 1200 mga, else ga-early: `lang_basis` `date-midpoint`).
- In 1,127 units the mapping agent overrode this with a language judgement because the only date was a late MS (`lang_basis` says so).
- Elsewhere the MS-only rule was applied literally. So some older texts known only from late manuscripts are `ga-early`: Echtra Cormaic, Táin bó Regamna, Oided mac nUisnig and Acallam in *Irische Texte*; Snedgus, Macgnímrada and the Eg. 93 Táin in RC; Amra Senáin and the Vossianus Fled Bricrend in ZCP. Each is flagged in its section note, and `date_ms_only` marks them.
- A period classifier trained on CELT (sga / mga / ga-early) was tried as a check and rejected: it scored only 62% text-level accuracy on held-out CELT texts, because the spelling follows the manuscripts.
- **Welsh** is `wlm` throughout except 2 units of Old Welsh (`owl`, the ZCP 8 computus fragment). Skene's 6th-century attribution of Aneirin and Taliesin is not a linguistic argument (he says the language was modernised in transmission), so his books are `editor-ms-only` with his own MS dates: Black Book "12th century", Aneirin late 13th/early 14th, Taliesin early 14th, Red Book c. 1400. Evans 1907 dates the White Book MS to the last quarter of the 13th c. and gives composition dates for the tales (Four Branches by the early 12th c., the romances early 13th).

## Counts

Before dedupe = all units; after = `dup_of` null.

**By language**

| lang | units before | tokens before | units after | tokens after |
|---|---:|---:|---:|---:|
| sga (Old Irish) | 54,784 | 493,286 | 45,537 | 388,460 |
| mga (Middle Irish) | 163,743 | 1,852,630 | 139,611 | 1,552,612 |
| ga-early (Early Modern Irish) | 112,771 | 2,365,235 | 100,157 | 2,110,279 |
| wlm (Middle Welsh) | 43,798 | 487,195 | 40,255 | 413,279 |
| owl (Old Welsh) | 2 | 12 | 2 | 12 |
| **total** | **375,098** | **5,198,358** | **325,562** | **4,464,642** |

**By period** (century of the date midpoint)

| period | units before | tokens before | units after | tokens after |
|---|---:|---:|---:|---:|
| 5th c. | 430 | 6,042 | 430 | 6,042 |
| 6th c. | 399 | 2,876 | 379 | 2,739 |
| 7th c. | 1,036 | 7,269 | 737 | 5,397 |
| 8th c. | 12,980 | 121,281 | 12,064 | 109,944 |
| 9th c. | 36,022 | 342,610 | 28,163 | 252,226 |
| 10th c. | 11,793 | 117,036 | 10,421 | 104,960 |
| 11th c. | 110,274 | 1,394,491 | 98,009 | 1,227,281 |
| 12th c. | 77,575 | 805,176 | 66,199 | 681,405 |
| 13th c. | 17,819 | 224,100 | 16,717 | 198,289 |
| 14th c. | 36,610 | 568,789 | 31,740 | 464,345 |
| 15th c. | 34,259 | 762,735 | 25,803 | 586,005 |
| 16th c. | 19,269 | 373,787 | 18,569 | 362,136 |
| 17th c. | 16,632 | 472,166 | 16,331 | 463,873 |

Notes on the periods:
- The 5th–7th-c. units are early annal entries, dated by annal year, which are retrospective.
- The 11th-c. peak includes CELT texts with wide ranges (e.g. 900–1200 → midpoint 1050).
- 38,543 units before / 27,983 after are dated by manuscript only (`date_ms_only`), 521k / 320k tokens.

**By genre**

| genre | units before | tokens before | units after | tokens after |
|---|---:|---:|---:|---:|
| saga | 89,868 | 1,202,175 | 65,255 | 820,608 |
| annals | 62,492 | 1,016,456 | 59,095 | 961,958 |
| religious | 59,446 | 864,185 | 55,073 | 820,800 |
| history | 16,695 | 382,145 | 14,969 | 357,632 |
| adaptation | 12,988 | 357,310 | 12,910 | 355,983 |
| genealogy | 37,238 | 308,671 | 29,191 | 229,931 |
| medical-scientific | 6,438 | 269,522 | 6,438 | 269,522 |
| verse | 43,592 | 264,239 | 42,194 | 253,146 |
| prose | 9,928 | 224,360 | 6,364 | 116,889 |
| dindshenchas | 13,801 | 87,566 | 13,553 | 85,077 |
| other | 4,945 | 64,902 | 3,496 | 42,246 |
| scholarship | 4,534 | 63,232 | 4,534 | 63,232 |
| glosses | 7,333 | 41,404 | 7,333 | 41,404 |
| law | 3,180 | 30,855 | 3,174 | 30,792 |
| wisdom | 2,620 | 21,336 | 1,983 | 15,422 |

**By licence**

| licence | units before | tokens before | units after | tokens after |
|---|---:|---:|---:|---:|
| consent-train (CELT) | 232,434 | 3,372,267 | 217,608 | 3,192,828 |
| research (CELT G4000xx; Ériu, ZCP, RC) | 65,141 | 852,636 | 50,265 | 591,025 |
| pd | 64,080 | 755,961 | 45,648 | 483,516 |
| nc (St Gall; CELT CC BY-NC-SA; 2 NLS Meyer scans) | 9,931 | 197,170 | 8,529 | 176,949 |
| cc-by (Würzburg) | 3,512 | 20,324 | 3,512 | 20,324 |

**By source**

| source | units before | tokens before | units after | tokens after |
|---|---:|---:|---:|---:|
| CELT | 240,953 | 3,544,711 | 225,616 | 3,362,513 |
| *Revue celtique* | 30,043 | 364,870 | 24,036 | 265,698 |
| *ZCP* | 21,829 | 356,893 | 14,174 | 206,975 |
| *Irische Texte* | 16,026 | 218,009 | 7,297 | 82,121 |
| Red Book Bruts | 6,113 | 112,045 | 6,112 | 111,963 |
| *Ériu* | 9,360 | 112,944 | 8,654 | 103,168 |
| White Book Mabinogion | 6,037 | 100,572 | 5,718 | 89,996 |
| Red Book Poetry | 10,958 | 80,129 | 9,737 | 71,303 |
| Red Book Mabinogion | 3,370 | 76,819 | 1,406 | 22,575 |
| Meyer's editions | 5,567 | 62,695 | 3,110 | 31,195 |
| Windisch TBC 1905 | 4,579 | 54,921 | 1,504 | 12,527 |
| Skene vol. 2 | 9,116 | 43,587 | 9,078 | 43,399 |
| Félire (Stokes 1905) | 4,230 | 31,745 | 2,203 | 22,791 |
| Würzburg glosses | 3,512 | 20,324 | 3,512 | 20,324 |
| St Gall glosses | 3,405 | 18,094 | 3,405 | 18,094 |

## Points for David

- **Licence of preferred copies.** Dedupe prefers the critical edition regardless of licence. 5,060 LU/LL units (`consent-train`) are therefore `dup_of` a journal or *Irische Texte* edition, some of which are `research`. A training export that filters by licence should fall back to the duplicate when the preferred copy is not trainable.
- **Exclusions the mapping agents flagged as reversible:**
  - Bergin's Irish Grammatical Tracts (*Ériu* supplement, ≈ 34k tokens, cut as paradigms although they quote many bardic lines).
  - Vol. 1 *Ériu* texts in unreadable Gaelic type.
  - RC 36's van Hamel poems (kept in their corrected RC 37 printing).
- **Not covered:** the Milan glosses (Thes. Pal. OCR) and the Ancient Laws Irish. They would need a better scan or a re-OCR with an Irish-type model.
