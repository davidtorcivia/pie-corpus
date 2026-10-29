# 8c corpus-quality fix batch 1 (cq1, 2026-10-28)

Approved under the Stage C-S closing rule (`docs/research/8c-preregistration.md`, "Closing rule"):
the 174 reader reports of waves 10-12 are fixed after the stage closed and do not reopen it. The
batch also takes the 42 entries of the formula witness scan (`data/research/formulas/mapping-errors-found.jsonl`).
Every report was checked against the source, the current production loader and a dictionary before
it was fixed. Read slabs, claims and committed Stage C-S results are unchanged; the fixes apply to
future builds and to the search index.

## Ledgers

`data/research/8c/corpus-quality/error-verdicts-cq1-<area>.jsonl` (one record per report, plus one
per attached observation), with metrics and token diffs beside them:

| area | inputs | reports: confirmed / already fixed / rejected / unclear | observations |
|---|---|---|---|
| armenian | 108 reader reports + scan 9-11 | 110 / 1 / 1 / 0 (112 records; scan 10 split) | 93 confirmed, 1 rejected |
| celtic | 23 reader reports + scan 4-8, 24, 25, 36 | reports 18 / 0 / 5 / 0; scan 8 confirmed, 1 unclear (entry 6 split) | 4 confirmed |
| norse | 13 reader reports | 12 / 1 / 0 / 0 | 5 confirmed |
| other | 30 reader reports + scan 16, 17 | 32 / 0 / 0 / 0 (зерно half of scan 17 rejected) | 21 confirmed |
| formulas | scan 1-3, 12-15, 18-23, 26-35, 37-42 | 27 / 0 / 2 / 5 (34 records; 26 and 29 split by form) | — |

Reader reports: 174 of 174 verdicted. Scan entries: 42 of 42.

## Where the fixes live (one source for index, builders, packets and checker)

- `pie/cq1_mapping.py`: exact word-coordinate readings (`data/research/formulas/cq1-readings-<area>.json`)
  and the per-area rule modules `pie/cq1_xcl.py`, `pie/cq1_other.py`, `pie/cq1_formulas.py`, hooked
  from `pie.other_mapping.contextual_lemma` and `pie.formula_search.Token` (non-content).
- Celtic rules in `pie/celtic_mapping.py` ("Corpus-quality batch 1" block, `_cq1_irish_rule`); Norse rules
  in `pie/germanic_new_mapping.py` and `data/research/formulas/menota-reviewed-wcq1.json`.
- Reviewed overrides `data/research/formulas/mapping-overrides/z-cq1-{xcl,celtic,norse,other,formulas}.json`.
  The `z-` prefix makes them read last (files are read in name order; later rows win). They use the
  existing lemma, form, proto and key row kinds of `pie/mapping.py`.
- Root-group splits, new: `data/research/formulas/group-splits.json`, read by
  `pie.formula_search.group_of`. Stage B's `_group` and the packets' `group_of` now call the shared
  rule instead of their own copies of `root_id or id`.
- Material units: `data/research/8c/corpus-quality/material-unit-rules-cq1-other.json` (auto-loaded by
  `pie.material_units.reviewed_ranges`).

## General rules added (measured on the whole corpus; exceptions listed in the code and ledgers)

- **\*gʷerH- 'mountain' vs 'praise' (group split).** Wiktionary files *gʷorH-eh₂ (gora, Βορέας, Lith.
  giria), *gʷr̥H-í- (girí-) and *gʷorH-no- under the 'praise' page; IEW 477/478 separate the roots.
  The three entries now form the group `pie-root-gwerH-mountain`; their lexeme mappings and the lexicon
  are unchanged. Found while verifying: Skt girí- was also keyed *ǵl̥h₂ṓws (an uncertain Wiktionary
  reflex), ON kyrr goes through gem-pro *kwerruz from a different *gʷerH- 'crumble' (proto row, unmapped),
  and Russian горшок goes to *gʷʰr̥nós (key row). OIr bráth stays (kaikki Proto-Celtic *brātus < *gʷr̥Htus).
- **Armenian (pie/cq1_xcl.py):** letter numerals become `<value>@numeral`, non-content (1,242 tokens);
  a reviewed name list with exceptions (Greeks, Aryans, Tigran, Asia, Medes, ...: 1,142 tokens); lexical
  form rules: oblique of այր 'man' no longer 'blood' (64), տամ 'give' forms (115), gini 'wine' (102),
  ban 'word' (221), village (47), gan 'they come' -> gam (27) and others; ~3,544 of 551,142 tokens.
- **Irish (pie/celtic_mapping.py):** prepositional día/die -> do (726 tokens), with día@day (306) and
  día@god (29) decided by context, Latin/German die excluded; gona -> co (124); gonadh/gonad -> conid
  (327); asna -> as (76); gráin 'horror' (175); Dál + people name (120); risin -> fri (553); eitir -> eter;
  airc. 3,648 tokens in 3,432 of 318,622 units. "Day" keyed *dyḗws was judged correct (*dyīus).
- **Norse:** Tunga place name after í/til/ór/gegnt (63); capitalised non-initial name forms in the
  unlemmatised Heimskringla codices (Finnr 40, Dagr 63, Haukr 9, Bera 3); Wends, máni byname, átta (VAN).
- **Other:** OE vowel-less OCR fragments (117); GLAUx δεξ- middle forms -> δέχομαι (107); byliny
  старух- -> старуха (51); Kireevsky ch. 2 index excluded as material (1,009 units) plus four prose
  paragraphs; Μῆδος unmapped (739; batch 9's "already fixed" held only for the grp table).
- **Formula scan (pie/cq1_formulas.py):** Greek plural ἰοί etc. -> ἰός@arrow (*(H)isu-); epic Sanskrit
  kṣam is the verb 'forbear' (232 tokens), Vedic kṣam- 'earth' kept.
- Lemma decisions for single errors: RV stár- 'star'; √piś-, √ci- 1, √hū- (no 'pour'); anyá-/anya/aniia-
  unmapped (*h₂en-yo-); ajuryá- *ǵerh₂-; DCS tva (the -tva suffix, 1,181 tokens) unmapped; upamā;
  ásthi- added; Iuppiter + *ph₂tḗr; medulla unmapped; Hitt. dankui- *dʰengʷʰ-; σάτυρος, Ἀμαζών unmapped;
  φατός/ἄφατος 'speak' only; ἔαρ/ἦρ 'spring' (*wésr̥, not 'blood'); πολιός *pelH-; ὀμιχέω *h₃meyǵʰ-;
  Homeric ἠέλιος 'sun' (125 units); Avestan vaŋhāu -> vohu.

## Left as they are

- Disputed etymologies: ὁδός and *sed- 'sit' vs 'go'; τυφλός (*dʰewbʰ-, the source's root); *gъrdъ
  (Serbian grdan); OIr mag 'plain' (EDPC marks *megh₂- with "(?)"); bebsait, tús, tarla (rejected:
  the mapping follows EDPC); ǰnǰem (Martirosyan *gʷʰen-); smesti still reaches *meh₁- via mȅsti.
- Structural, deferred: clitics and pronouns are non-content in the index (scan 30, and 3); compound
  members (scan 42); the Latvian corpus is small (scan 21).
- Policy calls raised by the workers, not made: capitalised GLAUx lemmas that go through common-word
  homographs (8,493 tokens, 468 lemmas); byliny sentence-initial capitals taken as names (needs
  punctuation context in `load_bsl`); more byliny editorial prose (Rybnikov vol. 2 Bessonov essay,
  about 2,900 units); Early Modern Irish Dia 'God' is non-content (about 3,600 tokens); Armenian gan has
  two outcomes (the w8 gam@present tokens map to nothing, the cq1 rule gives gam).
- Window keys: content-word counts change, so a rebuild re-cuts some windows (Celtic: 146 keys gone,
  69 new; Armenian: 93 sentences relabelled). Already-read slabs are unaffected; future builds differ.

## Tests

New: `tests/test_cq1_formulas.py`, `test_cq1_armenian.py`, `test_cq1_celtic.py`, `test_cq1_norse.py`,
`test_cq1_other.py`. Assertions superseded by the new general rules were updated, with a comment, in
`test_celtic_w4.py`, `test_celtic_w5.py`, `test_stagecs_w5_other.py` and `test_mapping_w7_other.py`.
Full suite: 3,428 passed, 1 failed (`tests/test_batch_release.py::test_shipped_migration`: Tier 3
batches t025/t033 not admitted, from the parallel generation work, unrelated to mappings).

## Search index

Rebuilt after the suite with a fresh loader cache, as after the theonym narrowing:
`UV_CACHE_DIR=/tmp/pie-uv-cache uv run python -I scripts/search_corpora.py --build --cache-dir data/research/8c/search-index/cache-cq1`
(default index path `data/research/8c/search-index/corpora.sqlite`; 1,082 s). The previous index is kept as
`corpora.pre-cq1.sqlite` and its cache as `cache/`. Units: 2,324,876 -> 2,323,653 (byliny -1,049 from the
material exclusions; xcl -93 and Celtic windows re-cut).

Words keyed to a group or id, before -> after (whole index):

| key | before | after |
|---|---:|---:|
| *gʷerH- 'praise' group | 6,621 | 2,988 |
| *gʷerH- 'mountain' group (new) | 0 | 3,408 |
| *h₁ésh₂r̥ 'blood' | 2,126 | 943 |
| *wósr̥ 'spring' | 838 | 1,797 |
| *sóh₂wl̥ 'sun' (hom ἠέλιος 0 -> 125) | 9,348 | 9,472 |
| *Hísus 'arrow' (Greek 0 -> 82) | 382 | 464 |
| *dyew- group | 27,920 | 27,053 |
| *gʷʰen- 'slay' group | 13,205 | 12,707 |
| *twós 'your' | 4,952 | 3,771 |
| Irish lemma día (undecided) | 892 | 71 (rest now do, día@day 307, día@god) |

Pair checks (the witness scan's `collocates_8c.py --pair` rule, ±4 content words; p = pair hits,
a = adjacent-unit hits, c = compound), before -> after, selected:

| spec | before | after |
|---|---|---|
| praise+put | Greek p29 a110, Slavic p3, Baltic p1 | Greek 0, Slavic p2, Baltic 0 (gora, Βορέας, giria gone) |
| praise+song (group) | Greek p9, Indo-Iranian p90 | Greek 0, Indo-Iranian p79 (girí- gone) |
| earth+sky | Celtic p12 a30 | Celtic p5 a20 (prepositional día gone) |
| sky+great | Celtic p3 a10 | Celtic 0 a1 |
| slay+man | Armenian a21, Celtic a1 | Armenian a9, Celtic 0 |
| star+adorn | Indo-Iranian p1 | p2 (RV 1.68.10b pipéśa nā́kaṃ stŕ̥bhiḥ) |
| wolf+grey | Greek 0 | Greek p5 (πολιοῖο λύκοιο) |
| arrow+fly / arrow+hand | Greek 0 / 0 | Greek p8 / p3 |
| urinate+upright | Greek 0 | Greek p1 (Hes. Op. 727) |
| sun+swift / sun+see | Greek p0 / p108 | Greek p1 / p110 (Homeric ἠέλιος) |
| blood+self | Greek p17, Armenian p21 | Greek 0, Armenian p17 |
| other+self | Indo-Iranian p22 | 0 (anyá- unmapped) |
| bone+self | Indo-Iranian 0 | p1 (AVP 4.15.3) |
| fame+good / fame+ageless | Indo-Iranian p1 / p1 | p2 / p2 (vaŋhāu srauuahī; ajuryá-) |
| sky+father | Italic c0 | Italic c92 (Iuppiter, compound hits only) |
| earth+darkadj | Anatolian 0 | Anatolian p7 (dankui- tekan) |
| race+mankind / name+god | Greek p18 / p10 | Greek 0 / 0 (Ἀμαζών, σάτυρος) |
| god+wide-seat | Greek p2, Celtic p11 | Greek 0, Celtic p3 |

Checks run with a copy of the scan script (session scratchpad), read-only on both indexes.
