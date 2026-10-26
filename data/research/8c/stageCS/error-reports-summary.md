# Stage C-S error-report triage: pilots + wave 1 primaries

Collected 2026-10-25. These are **unverified reader reports**, not adjudicated corrections. No mapping, lemmatizer, material, corpus, or export fixes were made. The existing Stage C pilot reports are retained alongside Stage C-S pilots and RS004, RS005, RS006, RS007, RS008, RS010, RS011, RS012. Follow-up `*F` files and RS002H were excluded before opening. Only claims/progress and the collector's existing `slabs-loci` metadata were used; neither text-bearing slabs nor the audit key was opened.

Reproduce from the repository root (quote globs):

```sh
UV_CACHE_DIR=/tmp/pie-uv-cache uv run python -I scripts/collect_8c_errors.py \
  data/research/8c/stageC/claims data/research/8c/stageCS/claims \
  --readers 'RC*' RS001 RS001X RS002 RS002X RS003 RS003X RS009 RS009X \
  RS004 RS005 RS006 RS007 RS008 RS010 RS011 RS012 \
  --exclude '*F' RS002H \
  --output data/research/8c/stageCS/error-reports.jsonl
```

Omitting `--readers` preserves the prior pilot selection; the default output was compared byte-for-byte with the previous 10-report artifact. Explicit IDs or filename-stem globs override that selection across all supplied directories; exclusions take precedence. RS002H remains unconditionally excluded.


## Counts

167 deduplicated report clusters, containing 227 observations. A cluster is the collector's corpus + given-lemma/form grouping, not necessarily one defect or one passage. Kind counts count each cluster once per kind, so they sum to 175; corpus counts sum to 167. Observations include repeated reader reports and harvested notes, not independent attestations.

| Kind | Clusters | Observations |
| --- | --- | --- |
| lemma | 91 | 116 |
| mapping | 31 | 45 |
| name | 24 | 33 |
| ocr | 6 | 6 |
| unit | 23 | 27 |

| Corpus | Clusters | Observations |
| --- | --- | --- |
| Classical Armenian | 1 | 1 |
| Epic Sanskrit | 1 | 1 |
| GLAUx Greek | 2 | 2 |
| Hittite | 2 | 2 |
| Homer | 4 | 11 |
| IcePaHC Icelandic | 1 | 1 |
| Latin | 2 | 2 |
| Menota Norse | 15 | 21 |
| Middle Irish | 107 | 149 |
| Middle Welsh | 3 | 3 |
| Old English | 4 | 4 |
| Old Irish | 4 | 5 |
| Poetic Edda | 5 | 5 |
| Russian byliny | 8 | 9 |
| unknown | 8 | 11 |

Eight clusters have no resolved corpus: retain them for manual locus resolution; do not infer a corpus from a guessed word. Full corpus labels remain in the JSONL.

## Most frequent lemmas and forms

Counts below are observations, including repeats across readers/passages. Lemmas are the **supplied, potentially erroneous** lemmas. Placeholder labels such as “not applicable: passage extraction” and blank values are excluded. Tables include all entries occurring at least three times; separate exact spellings and composite lemma strings are retained.

| Corpus | Given lemma | Observations |
| --- | --- | --- |
| Homer | ἀφύσσω | 5 |
| Homer | αὔω | 4 |
| Menota Norse | einarr | 4 |
| Middle Irish | adaig | 4 |
| Middle Irish | bí | 4 |
| Menota Norse | helga | 3 |
| Middle Irish | alpán | 3 |
| Middle Irish | benaid | 3 |
| Middle Irish | bíad | 3 |
| Middle Irish | bó | 3 |
| Middle Irish | días | 3 |
| Middle Irish | easna | 3 |
| Middle Irish | fer | 3 |
| Middle Irish | grán\|gráin | 3 |
| Middle Irish | ord | 3 |
| Middle Irish | áed | 3 |

| Corpus | Form | Observations |
| --- | --- | --- |
| Menota Norse | Einars | 4 |
| Homer | ἀφυσσάμεθ̓ | 3 |
| Menota Norse | Helga | 3 |
| Middle Irish | días | 3 |

## Queue A — mapping, lemma, name, and OCR within a word

146 clusters / 200 observations. Review mapping tables, lemmatizers, name handling, and word-level OCR. Each row identifies the corpus, reported forms/lemmas, loci, and reader source files. Consult the linked source lines and JSONL observations for proposed readings and evidence. Cluster numbers are 1-based lines in `error-reports.jsonl`.

Source links are reader report files; passage IDs retain the underlying corpus document identifier and locus. These are not independently verified raw-source paths. All provenance for a cluster is listed, including any material observation merged into it.

| Cluster | Corpus | Forms | Given lemmas | Kinds | Passages / source document IDs | Reader source files:lines |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Middle Irish | Lotar | loit | lemma | mga:G301035:#1/3:89 | [RS004.jsonl:1](claims/RS004.jsonl) |
| 2 | Middle Irish | ṅgabail | gaibid | lemma | mga:G301035:#1/3:140 | [RS004.jsonl:2](claims/RS004.jsonl) |
| 4 | Middle Irish | úathu | úath | lemma | mga:G301035:#1/39:97 | [RS004.jsonl:4](claims/RS004.jsonl) |
| 5 | Middle Irish | lind | lind | lemma | mga:G301035:#1/8:135; mga:G303000:#1:916 | [RS004.jsonl:5](claims/RS004.jsonl); [RS005.jsonl:23](claims/RS005.jsonl) |
| 6 | Middle Irish | días | días | mapping | mga:G301035:#1/1:12 (w2/2); mga:G302014:#1/#2:39 (w2/3); mga:G302014:#1/#2:52 (w3/3) | [RS004.jsonl:8](claims/RS004.jsonl); [RS005.jsonl:17](claims/RS005.jsonl); [RS005.jsonl:18](claims/RS005.jsonl) |
| 7 | Middle Irish | fáe | fod\|foid | lemma | mga:G301035:#1/38:6 | [RS004.jsonl:9](claims/RS004.jsonl) |
| 8 | Middle Irish | ḟálti | fálaigh | lemma | mga:G301035:#1/10:17 (w1/2) | [RS004.jsonl:10](claims/RS004.jsonl) |
| 9 | Middle Irish | suil | súil | lemma | mga:G301041:#1:212 (w2/2) | [RS004.jsonl:11](claims/RS004.jsonl) |
| 10 | Middle Irish | fir; fer | fer | lemma | mga:G301041:#1:426; mga:G302000:#1/15:3; mga:celtic-journal-revue-celtique-1870-1928:revueceltique22pari:L11846-L11850 (w2/2) | [RS004.jsonl:12](claims/RS004.jsonl); [RS005.jsonl:10](claims/RS005.jsonl); [RS008.jsonl:21](claims/RS008.jsonl) |
| 11 | Middle Irish | dhuin | dún | lemma | mga:G301041:#1:426 | [RS004.jsonl:13](claims/RS004.jsonl) |
| 12 | Middle Irish | bhai; bhó; mbo | bó | lemma | mga:G301044:#1/66:4; mga:G303000:#1:419 (w2/2); mga:celtic-journal-eriu-1904-1928:eriu_1912_6:L8294-L8296 | [RS004.jsonl:14](claims/RS004.jsonl); [RS005.jsonl:67](claims/RS005.jsonl); [RS007.jsonl:4](claims/RS007.jsonl) |
| 13 | Middle Irish | nís | nigh | lemma | mga:G301035:#1/4/#1:19 (w1/2) | [RS004.jsonl:15](claims/RS004.jsonl) |
| 14 | Middle Irish | maid | maith | lemma | mga:G301035:#1/36:18 (w2/2) | [RS004.jsonl:16](claims/RS004.jsonl) |
| 15 | Middle Irish | nAlpain; h-Alpain; n-Alpain | alpán | name | mga:G301035:#1/39:194; mga:G302007:#1/5:1; mga:G303000:#1:87 | [RS004.jsonl:17](claims/RS004.jsonl); [RS005.jsonl:49](claims/RS005.jsonl); [RS005.jsonl:50](claims/RS005.jsonl) |
| 16 | Middle Irish | rena | fren | lemma | mga:G301035:#1/39:83 (w2/2) | [RS004.jsonl:20](claims/RS004.jsonl) |
| 17 | Middle Irish | géis | géiss | lemma | mga:G301035:#1/39:561 (w1/2) | [RS004.jsonl:21](claims/RS004.jsonl) |
| 18 | Middle Irish | messu; Messi | midithir | lemma | mga:G301035:#1/15:18; mga:G301035:#1/4/#1:230 | [RS004.jsonl:22](claims/RS004.jsonl); [RS004.jsonl:54](claims/RS004.jsonl) |
| 19 | Middle Irish | día | día | lemma | mga:G301026:#1/52:11 (w1/2) | [RS004.jsonl:25](claims/RS004.jsonl) |
| 20 | Middle Irish | smera | smiur | lemma | mga:G301041:#1:183 (w2/3) | [RS004.jsonl:26](claims/RS004.jsonl) |
| 21 | Middle Irish | bheithi | beithe | lemma | mga:G301041:#1:468 (w2/2) | [RS004.jsonl:27](claims/RS004.jsonl) |
| 22 | Middle Irish | bas; bás | bás | lemma | mga:G301035:#1/4/#1:207; mga:G308002:#1/47:2 | [RS004.jsonl:28](claims/RS004.jsonl); [RS007.jsonl:8](claims/RS007.jsonl) |
| 23 | Middle Irish | Eó | eó | lemma | mga:G301035:#1/39:249 | [RS004.jsonl:29](claims/RS004.jsonl) |
| 24 | Middle Irish | airc | arc\|airc\|árc | lemma | mga:G301041:#1:371 (w2/2) | [RS004.jsonl:32](claims/RS004.jsonl); [RS005.jsonl:9](claims/RS005.jsonl) |
| 25 | Middle Irish | thes | thés\|téit\|tés | lemma | mga:G301041:#1/t#4:15 | [RS004.jsonl:33](claims/RS004.jsonl) |
| 26 | Middle Irish | braiti | braiteach\|braith | lemma | mga:G301035:#1/39:54 (w2/2) | [RS004.jsonl:34](claims/RS004.jsonl) |
| 27 | Middle Irish | ben | ben | lemma | mga:G301035:#1/29:234 | [RS004.jsonl:36](claims/RS004.jsonl) |
| 28 | Middle Irish | ṅDiad | dead | name | mga:G301035:#1/29:234 | [RS004.jsonl:37](claims/RS004.jsonl) |
| 29 | Middle Irish | ás | ás | lemma | mga:G301035:#1/22:21 | [RS004.jsonl:38](claims/RS004.jsonl) |
| 30 | Middle Irish | ghaibh | gabh\|ghabh | lemma | mga:G301044:#1/48:4 (w1/2) | [RS004.jsonl:39](claims/RS004.jsonl) |
| 31 | Middle Irish | hingnib | ingen | lemma | mga:G301044:#1/100:4 (w2/2) | [RS004.jsonl:40](claims/RS004.jsonl) |
| 32 | Middle Irish | iṅgni | ingnin | lemma | mga:G301035:#1/39:644 | [RS004.jsonl:41](claims/RS004.jsonl) |
| 33 | Middle Irish | aide; d'Áed; Āed | áed | lemma, name | mga:G301044:#1/21:1 (w1/3); mga:G302014:#1/#1:168 (w2/2); mga:G301045:#1/t#1:3 | [RS004.jsonl:42](claims/RS004.jsonl); [RS005.jsonl:30](claims/RS005.jsonl); [RS005.jsonl:31](claims/RS005.jsonl) |
| 34 | Middle Irish | nít | net | lemma | mga:G301035:#1/4/#1:361 | [RS004.jsonl:43](claims/RS004.jsonl) |
| 35 | Middle Irish | caera; cháera | cáera | lemma | mga:G301041:#1:208; mga:G301035:#1/39:640 | [RS004.jsonl:45](claims/RS004.jsonl); [RS004.jsonl:46](claims/RS004.jsonl) |
| 36 | Middle Irish | t-art | tart | lemma | mga:G301035:#1/39:377 | [RS004.jsonl:47](claims/RS004.jsonl) |
| 37 | Middle Irish | lasan | lasán | lemma | mga:G301035:#1/17:21 | [RS004.jsonl:48](claims/RS004.jsonl) |
| 38 | Middle Irish | damhsa | damh\|damhsa\|damhsaigh | lemma | mga:G301026:#1/29:1 (w1/2) | [RS004.jsonl:49](claims/RS004.jsonl) |
| 39 | Middle Irish | ásna; asna | easna | lemma | mga:G301035:#1/39:101 (w2/3); mga:G302000:#1/53:6; mga:G303000:#1:292 | [RS004.jsonl:50](claims/RS004.jsonl); [RS005.jsonl:43](claims/RS005.jsonl); [RS005.jsonl:44](claims/RS005.jsonl) |
| 40 | Middle Irish | chlíu | clú | lemma | mga:G301035:#1/39:309 | [RS004.jsonl:53](claims/RS004.jsonl) |
| 41 | Middle Irish | rioghacht | ríocht | mapping | mga:G301026:#1/6:4 (w1/3) | [RS004.jsonl:55](claims/RS004.jsonl) |
| 42 | Middle Irish | bias; bía; bether | benaid | lemma | mga:G301044:#1/12:3 (w2/2); mga:G302014:#1/#1/t#11:33; mga:G308002:#1/47:2 | [RS004.jsonl:56](claims/RS004.jsonl); [RS005.jsonl:48](claims/RS005.jsonl); [RS007.jsonl:9](claims/RS007.jsonl) |
| 43 | Middle Irish | tuga | tuga | lemma | mga:G301044:#1/12:3 (w2/2) | [RS004.jsonl:57](claims/RS004.jsonl) |
| 44 | Middle Irish | h-aidchi-so; aidchi; n-adaig; adaig | adaig | mapping, lemma | mga:G303000:#1:4 (w1/2); mga:G303000:#1:1075 (w2/2); mga:G302014:#1/#1:127 (w1/2); mga:celtic-journal-eriu-1904-1928:eriu_1914_7:L119-L127 | [RS005.jsonl:1](claims/RS005.jsonl); [RS005.jsonl:37](claims/RS005.jsonl); [RS005.jsonl:76](claims/RS005.jsonl); [RS007.jsonl:3](claims/RS007.jsonl) |
| 45 | Middle Irish | bhir; m-bíd; bíd | bí | lemma | mga:G303000:#1:334; mga:G302014:#1/#1:36 (w1/2); mga:G303000:#1:566 (w1/2); mga:G303000:#1:1495 (w3/3) | [RS005.jsonl:2](claims/RS005.jsonl); [RS005.jsonl:55](claims/RS005.jsonl); [RS005.jsonl:60](claims/RS005.jsonl); [RS006.jsonl:2](claims/RS006.jsonl) |
| 46 | Middle Irish | méd; mēd | med | lemma | mga:G302014:#1/#2:28; mga:G302025:#1/13:1 (w2/2) | [RS005.jsonl:3](claims/RS005.jsonl); [RS005.jsonl:4](claims/RS005.jsonl) |
| 47 | Middle Irish | órda; n-uird | ord | lemma, mapping | mga:G303000:#1:822 (w4/4); mga:G303000:#1:1075 (w2/2); mga:G303000:#1:858 (w2/2) | [RS005.jsonl:5](claims/RS005.jsonl); [RS005.jsonl:38](claims/RS005.jsonl); [RS005.jsonl:39](claims/RS005.jsonl) |
| 48 | Middle Irish | ēistecht; n-eistecht | estecht | mapping | mga:G302025:#1/75:1; mga:G303000:#1:858 (w2/2) | [RS005.jsonl:6](claims/RS005.jsonl); [RS005.jsonl:7](claims/RS005.jsonl) |
| 49 | Middle Irish | biadh | bia | lemma | mga:G302025:#1/6:8 (w1/2) | [RS005.jsonl:8](claims/RS005.jsonl) |
| 50 | Middle Irish | gai | gae | lemma | mga:G302000:#1/15:3 | [RS005.jsonl:11](claims/RS005.jsonl) |
| 51 | Middle Irish | adaigh | fadaigh | lemma | mga:G302025:#1/67:4 (w1/2); mga:G302025:#1/70:1 | [RS005.jsonl:12](claims/RS005.jsonl); [RS005.jsonl:13](claims/RS005.jsonl) |
| 52 | Middle Irish | chuain | cuain | lemma | mga:G303000:#1:562 (w1/4) | [RS005.jsonl:14](claims/RS005.jsonl) |
| 53 | Middle Irish | h-athaid | feithid | lemma | mga:G303000:#1:562 (w1/4) | [RS005.jsonl:15](claims/RS005.jsonl) |
| 54 | Middle Irish | find | find | mapping | mga:G302000:#1/20:1 | [RS005.jsonl:16](claims/RS005.jsonl) |
| 55 | Middle Irish | grain; gráin; grāin | grán\|gráin | lemma | mga:G303000:#1:1170 (w2/2); mga:G303000:#1:564; mga:G302025:#1/70:1 | [RS005.jsonl:19](claims/RS005.jsonl); [RS005.jsonl:20](claims/RS005.jsonl); [RS005.jsonl:21](claims/RS005.jsonl) |
| 56 | Middle Irish | shaltair | altair | lemma | mga:G302014:#1/#1:34 (w1/2) | [RS005.jsonl:22](claims/RS005.jsonl) |
| 57 | Middle Irish | collaib | coll | lemma | mga:G302025:#1/97:4 (w2/2) | [RS005.jsonl:24](claims/RS005.jsonl) |
| 58 | Middle Irish | Dobo; dobo | doboing | lemma | mga:G302025:#1/76:9; mga:G302025:#1/5:4 (w2/2) | [RS005.jsonl:25](claims/RS005.jsonl); [RS005.jsonl:26](claims/RS005.jsonl) |
| 59 | Middle Irish | cuala | cualf\|cúal\|cual | lemma | mga:G303000:#1:494 (w2/4) | [RS005.jsonl:27](claims/RS005.jsonl) |
| 60 | Middle Irish | d'Eōgan; h-Eōgan | eógan | name | mga:G302025:#1/35:3 (w2/2); mga:G302025:#1/13:2 | [RS005.jsonl:28](claims/RS005.jsonl); [RS005.jsonl:29](claims/RS005.jsonl) |
| 61 | Middle Irish | Eogan | éogan | name | mga:G303000:#1:1058 | [RS005.jsonl:32](claims/RS005.jsonl) |
| 62 | Middle Irish | Ōengus | oíngus | name | mga:G302002:#1:8 | [RS005.jsonl:33](claims/RS005.jsonl) |
| 63 | Middle Irish | n-Domnall | domnall | name | mga:G302014:#1/#1:283 (w1/2) | [RS005.jsonl:34](claims/RS005.jsonl) |
| 64 | Middle Irish | lía | lía | lemma | mga:G303000:#1:958 | [RS005.jsonl:35](claims/RS005.jsonl) |
| 65 | Middle Irish | Cas | cas\|cás\|casadh | name | mga:G303000:#1/t#64:50 | [RS005.jsonl:36](claims/RS005.jsonl) |
| 66 | Middle Irish | Mina | min | lemma | mga:G302000:#1/21:3 | [RS005.jsonl:40](claims/RS005.jsonl) |
| 67 | Middle Irish | n-airc | arc\|áirc\|árc | lemma | mga:G303000:#1:1117 (w1/2) | [RS005.jsonl:41](claims/RS005.jsonl) |
| 68 | Middle Irish | áilli | aille | lemma | mga:G302014:#1/#1:250 | [RS005.jsonl:42](claims/RS005.jsonl) |
| 69 | Old Irish | file | file\|fil | lemma | sga:G301012:#1/#2/#12:5 | [RS005.jsonl:45](claims/RS005.jsonl) |
| 70 | Middle Irish | mín | mín | lemma | mga:G303000:#1:58 (w2/2) | [RS005.jsonl:46](claims/RS005.jsonl) |
| 71 | Middle Irish | bhud; bíad | bíad | lemma | mga:G303000:#1:58 (w2/2); mga:G302014:#1/#1:139; mga:G302014:#1/#1:74 | [RS005.jsonl:47](claims/RS005.jsonl); [RS005.jsonl:53](claims/RS005.jsonl); [RS005.jsonl:54](claims/RS005.jsonl) |
| 72 | Middle Irish | áith | áith | lemma | mga:G303000:#1:489; mga:G303000:#1:1686 (w2/3) | [RS005.jsonl:51](claims/RS005.jsonl); [RS006.jsonl:3](claims/RS006.jsonl) |
| 73 | Menota Norse | mól | mál | lemma | menota:AM-63-fol 326: (w3/7) | [RS005.jsonl:52](claims/RS005.jsonl) |
| 74 | Middle Irish | t-ech | tech | lemma | mga:G303000:#1:67 (w1/4) | [RS005.jsonl:56](claims/RS005.jsonl) |
| 75 | Middle Irish | Mun | mún | lemma | mga:G303000:#1:35 | [RS005.jsonl:57](claims/RS005.jsonl) |
| 76 | Middle Irish | gairit | gairid | lemma | mga:G303000:#1:35 | [RS005.jsonl:58](claims/RS005.jsonl) |
| 78 | Menota Norse | Einars | einarr | name | menota:AM-132-fol-Njals-saga 39v:33 [AM-132-fol-Njals-saga.6229]; menota:AM-132-fol-Droplaugarsona-saga 146r:30 [AM-132-fol-Droplaugarsona-saga.1035] | [RS005.jsonl:61](claims/RS005.jsonl); [RS006.jsonl:7](claims/RS006.jsonl); [RS010.jsonl:14](claims/RS010.jsonl); [RS010.jsonl:17](claims/RS010.jsonl) |
| 79 | Menota Norse | Helga | helga | name | menota:AM-132-fol-Njals-saga 39v:33 [AM-132-fol-Njals-saga.6229] | [RS005.jsonl:62](claims/RS005.jsonl); [RS006.jsonl:8](claims/RS006.jsonl); [RS010.jsonl:18](claims/RS010.jsonl) |
| 80 | Classical Armenian | հաւուց։ | haw | lemma | xcl:MH_1_1_06_Yeghishe ed. page 579 - PDF page 59 (word id 9376) | [RS005.jsonl:63](claims/RS005.jsonl) |
| 81 | Middle Irish | agaib | ág | lemma | mga:G302025:#1/84:7 | [RS005.jsonl:64](claims/RS005.jsonl) |
| 82 | Middle Irish | filed | fili | lemma | mga:G302025:#1/84:7 | [RS005.jsonl:65](claims/RS005.jsonl) |
| 83 | Middle Irish | omna | ómun | lemma | mga:G302000:#1/33:1 | [RS005.jsonl:66](claims/RS005.jsonl) |
| 84 | Middle Irish | dána | dán\|dána | lemma | mga:G303000:#1:567 (w1/2) | [RS005.jsonl:68](claims/RS005.jsonl) |
| 85 | Middle Irish | aingil | aingel | mapping | mga:G303000:#1:796 | [RS005.jsonl:69](claims/RS005.jsonl) |
| 86 | Middle Irish | n-éicne | éicen | lemma | mga:G303000:#1:722 (w1/3) | [RS005.jsonl:70](claims/RS005.jsonl) |
| 87 | Old English | wer | wer | mapping | ang:Grein I Genesis l.7136 | [RS005.jsonl:71](claims/RS005.jsonl) |
| 88 | Middle Irish | oss | oss | lemma | mga:G303000:#1:926; mga:G303000:#1:849 (w2/3) | [RS005.jsonl:72](claims/RS005.jsonl); [RS005.jsonl:73](claims/RS005.jsonl) |
| 89 | Middle Irish | eacute | ?eacute | ocr | mga:G302025:#1/105:5 (w2/2) | [RS005.jsonl:74](claims/RS005.jsonl) |
| 90 | Menota Norse | mǫðr | móðr | lemma | menota:AM-36-fol 473:29 (w8/28) | [RS005.jsonl:75](claims/RS005.jsonl) |
| 91 | Middle Irish | fele | féle\|fil | lemma | mga:G303009:#1/10/21:1 | [RS006.jsonl:1](claims/RS006.jsonl) |
| 92 | Old Irish | chomla; comla | adcomla\|conlá | lemma | sga:G301900:#1/#23/#1:50; sga:G301900:#1/#16:24 | [RS006.jsonl:4](claims/RS006.jsonl); [RS006.jsonl:5](claims/RS006.jsonl) |
| 93 | Menota Norse | heila | heill | lemma | menota:AM-36-fol 424:29 (w28/43) | [RS006.jsonl:6](claims/RS006.jsonl) |
| 96 | Middle Irish | Tlas | ?tlas (name) | name | mga:G303009:#1/10/21:1 | [RS006.jsonl:26](claims/RS006.jsonl) |
| 97 | Middle Irish | gcēad-óir | ceadaigh | lemma | mga:G303010:#1/18:11 (w3/4) | [RS006.jsonl:27](claims/RS006.jsonl) |
| 98 | Middle Irish | rigid | rigid | lemma | mga:G303000:#1:1328 (w1/2) | [RS006.jsonl:28](claims/RS006.jsonl) |
| 99 | Middle Irish | d'Fionn | fionn\|feann | name | mga:G303010:#1/11:5 (w7/7) | [RS006.jsonl:29](claims/RS006.jsonl) |
| 100 | IcePaHC Icelandic | Áki | áki | name | icepahc:1260.jomsvikingar.nar-sag s932 | [RS006.jsonl:30](claims/RS006.jsonl) |
| 101 | Menota Norse | þa(+K) | þak | lemma | menota:AM-36-fol 424:29 (w28/43) | [RS006.jsonl:31](claims/RS006.jsonl) |
| 102 | Middle Irish | gonadh | goin | lemma | mga:G400047:#1:1 (w2/2) | [RS007.jsonl:1](claims/RS007.jsonl) |
| 103 | Middle Irish | leiginn | lig | lemma | mga:celtic-journal-eriu-1904-1928:eriu_1911_5:L7498-L7499 | [RS007.jsonl:2](claims/RS007.jsonl) |
| 104 | Middle Irish | h-Erenà | asren | name | mga:celtic-journal-revue-celtique-1870-1928:revueceltique06pari:L9054-L9055 | [RS007.jsonl:5](claims/RS007.jsonl) |
| 105 | Middle Irish | hErind | érind | name | mga:celtic-journal-eriu-1904-1928:eriu_1912_6:L8274-L8276 | [RS007.jsonl:6](claims/RS007.jsonl) |
| 106 | Menota Norse | vín | vinr | lemma | menota:AM-242-fol 24:9 (w3/3) | [RS007.jsonl:7](claims/RS007.jsonl) |
| 107 | Middle Irish | eitir | eitigh | lemma | mga:G400055:#1:60 | [RS007.jsonl:10](claims/RS007.jsonl) |
| 108 | Middle Irish | der | dér | lemma | mga:celtic-journal-revue-celtique-1870-1928:revueceltique10pari:L5026-L5028 | [RS007.jsonl:11](claims/RS007.jsonl) |
| 123 | Middle Irish | ior | orcaid | ocr | mga:celtic-journal-revue-celtique-1870-1928:revueceltique22pari:L11846-L11850 (w2/2) | [RS008.jsonl:22](claims/RS008.jsonl) |
| 124 | Middle Irish | chlaid | clad\|claidid | lemma | mga:celtic-journal-revue-celtique-1870-1928:revueceltique22pari:L11846-L11850 (w2/2) | [RS008.jsonl:23](claims/RS008.jsonl) |
| 125 | Middle Irish | Icthchlocind | ?icthchlocind (name) | name | mga:celtic-journal-revue-celtique-1870-1928:revueceltique22pari:L11846-L11850 (w2/2) | [RS008.jsonl:24](claims/RS008.jsonl) |
| 126 | Homer | Τυδέος | Τυδεύς | name | hom:Il. 23.383 | [RS008.jsonl:25](claims/RS008.jsonl) |
| 127 | Middle Irish | no-mbligtis | ?nombligtis | mapping | mga:oldirish-irische-texte-1880-1909:irischetextemitw01winduoft:L4236-L4237 | [RS008.jsonl:26](claims/RS008.jsonl) |
| 128 | Middle Irish | hlechta | ?hlechta | ocr | mga:oldirish-irische-texte-1880-1909:irischetextemitw01winduoft:L4236-L4237 | [RS008.jsonl:27](claims/RS008.jsonl) |
| 129 | Latin | edere | edo | mapping | lat:LucrDRN6 6.1258 | [RS008.jsonl:28](claims/RS008.jsonl) |
| 130 | Old English | swāte | swat\|swāt | mapping | ang:Beo. 1607 | [RS008.jsonl:29](claims/RS008.jsonl) |
| 131 | Menota Norse | Þverá | þverá | name | menota:AM-132-fol-Droplaugarsona-saga 146r:30 [AM-132-fol-Droplaugarsona-saga.1035] | [RS010.jsonl:15](claims/RS010.jsonl) |
| 132 | GLAUx Greek | Κύρου | Κῦρος | name | grc:Herodotus Historiae 3.133.1 s2 | [RS010.jsonl:16](claims/RS010.jsonl) |
| 133 | Old English | sniw | sniwan\|snīwan | lemma | ang:Grein I A Za R I A S l.10871 | [RS010.jsonl:19](claims/RS010.jsonl) |
| 135 | Middle Welsh | vaur | maur | mapping | cy:welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:L21480-L21480 | [RS010.jsonl:21](claims/RS010.jsonl) |
| 136 | Middle Welsh | kae | cae | lemma | cy:welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:L17235-L17250 (w1/3) | [RS010.jsonl:22](claims/RS010.jsonl) |
| 137 | Epic Sanskrit | paśyataḥ | dṛś | mapping | sa-ep:MBh, 7, 142.s55 | [RS010.jsonl:23](claims/RS010.jsonl) |
| 138 | Homer | ἀφυσσάμεθ̓; ἀφυσσάμενοι | ἀφύσσω | mapping | hom:Od. 10.56; hom:Od. 4.359 | [RS010.jsonl:24](claims/RS010.jsonl); [RS010.jsonl:25](claims/RS010.jsonl); [RS011.jsonl:22](claims/RS011.jsonl); [RS012.jsonl:16](claims/RS012.jsonl); [RS012.jsonl:17](claims/RS012.jsonl) |
| 140 | Russian byliny | впадешя | ?впадешя | ocr | byliny:sbornikotdelenijarusskogojazykaislovesno92:8617 | [RS010.jsonl:27](claims/RS010.jsonl) |
| 141 | Menota Norse | Beru | bera | name | menota:AM-132-fol-Egils-saga 85v:12 [AM-132-fol-Egils-saga.4382] | [RS011.jsonl:15](claims/RS011.jsonl) |
| 142 | Menota Norse | Yngvars | yngvarr | name | menota:AM-132-fol-Egils-saga 85v:12 [AM-132-fol-Egils-saga.4382] | [RS011.jsonl:16](claims/RS011.jsonl) |
| 143 | Middle Irish | boinn | bonn | name | mga:celtic-journal-revue-celtique-1870-1928:revueceltique24pari:L9034-L9040 (w1/3) | [RS011.jsonl:17](claims/RS011.jsonl) |
| 144 | Old Irish | m-Maig | mag\|maig | mapping | sga:G301006:#1/3:1 (w1/2) | [RS011.jsonl:18](claims/RS011.jsonl) |
| 145 | Middle Irish | muig | mag | mapping | mga:celtic-journal-revue-celtique-1870-1928:revueceltique24pari:L9034-L9040 (w1/3) | [RS011.jsonl:19](claims/RS011.jsonl) |
| 146 | Menota Norse | Haraldr | haraldr | name | menota:AM-132-fol-Egils-saga 84r:5 (w1/2) | [RS011.jsonl:20](claims/RS011.jsonl) |
| 147 | Homer | ἤϋσεν; αὖε | αὔω | mapping | hom:Il. 11.462; hom:Il. 13.477; hom:Il. 11.461 | [RS011.jsonl:21](claims/RS011.jsonl); [RS012.jsonl:13](claims/RS012.jsonl); [RS012.jsonl:14](claims/RS012.jsonl); [RS012.jsonl:15](claims/RS012.jsonl) |
| 148 | Menota Norse | várit; vár | vár | mapping | menota:AM-132-fol-Egils-saga 76r:21 [AM-132-fol-Egils-saga.2661]; menota:AM-132-fol-Kormaks-saga 128v:14 [AM-132-fol-Kormaks-saga.2122] | [RS011.jsonl:23](claims/RS011.jsonl); [RC002.jsonl:2](../stageC/claims/RC002.jsonl) |
| 149 | Menota Norse | egg | egg | mapping | menota:AM-132-fol-Egils-saga 76r:37 [AM-132-fol-Egils-saga.2682] | [RS011.jsonl:24](claims/RS011.jsonl) |
| 150 | Latin | oris | os | mapping | lat:LucrDRN2 2.511 | [RS011.jsonl:25](claims/RS011.jsonl) |
| 151 | Homer | ἐπιόντα | ἔπειμι | mapping | hom:Il. 13.477 | [RS012.jsonl:18](claims/RS012.jsonl) |
| 152 | Menota Norse | sveiti | sveiti | mapping | menota:AM-132-fol-Hallfredar-saga 154v:23 (w1/2) | [RS012.jsonl:19](claims/RS012.jsonl) |
| 153 | Menota Norse | niðjum | niðr | mapping | menota:AM-132-fol-Hallfredar-saga 152r:20 (w2/2) | [RS012.jsonl:20](claims/RS012.jsonl) |
| 155 | Russian byliny | вранъ | вранье | lemma | byliny:11016812bsb:6393 | [RS012.jsonl:22](claims/RS012.jsonl); [RS012.jsonl:23](claims/RS012.jsonl) |
| 156 | GLAUx Greek | Ἀκρισίου | Ἀκρίσιος | name | grc:Herodotus Historiae 6.53.2 s3 | [RS012.jsonl:24](claims/RS012.jsonl) |
| 157 | Hittite | a-ra-a-i | ar=a-@Freund | lemma | hit:KUB 36.89 Rs. 56′ | [RS012.jsonl:25](claims/RS012.jsonl) |
| 158 | Hittite | e-eš-ta | eš-@sitzen | lemma | hit:KUB 36.89 Rs. 56′ | [RS012.jsonl:26](claims/RS012.jsonl) |
| 159 | unknown | mairc | unspecified | lemma | unresolved | [RC001.jsonl:2](../stageC/claims/RC001.jsonl) |
| 160 | unknown | m-broin | unspecified | lemma, mapping | unresolved | [RC011.jsonl:1](../stageC/claims/RC011.jsonl) |
| 161 | unknown | menmae | unspecified | mapping | unresolved | [RS003.jsonl:2](claims/RS003.jsonl) |
| 162 | unknown | unspecified | unspecified | ocr, mapping | unresolved | [RS009X.jsonl:1](claims/RS009X.jsonl) |
| 163 | Old Irish | doesetar | unspecified | mapping | sga:G301012:#1/#2/#52:49 | [RS001X.progress:11](claims/RS001X.progress) |
| 164 | unknown | unspecified | unspecified | mapping | unresolved | [RS001X.progress:11](claims/RS001X.progress) |
| 165 | unknown | fili | unspecified | mapping | unresolved | [RS002X.progress:4](claims/RS002X.progress) |
| 166 | unknown | unspecified | unspecified | ocr, mapping | unresolved | [RS009X.progress:5](claims/RS009X.progress) |
| 167 | unknown | vaiio/woe | unspecified | mapping | unresolved | [RS009X.progress:12](claims/RS009X.progress) |

## Queue B — material, passage labels, and unit boundaries

23 clusters / 27 observations. Each material observation has its own row below, including all five passages merged under the placeholder lemma in cluster 116. Review extraction boundaries, apparatus/commentary exclusion, genre assignment, and Edda poem-label carryover. Word splits inside restored forms are retained here because the readers classified them as unit/extraction errors.

Clusters 24 and 155 also occur in A: a word-level report and a material report were merged by the existing identity rule. Thus A and B overlap by two clusters (146 + 23 − 2 = 167); observations are partitioned by reported kind. Word-level OCR inside an editorial passage remains in A, while the separate material report goes in B. No proposed reading below has been independently verified.

| Cluster | Corpus | Passage / source document ID | Reported material or unit issue | Reader | Reader source files:lines |
| --- | --- | --- | --- | --- | --- |
| 3 | Poetic Edda | non:Sólarljób 82 [edda:19662] | Modern editorial explanation, not an Eddic verse witness | RS004 | [RS004.jsonl:3](claims/RS004.jsonl) |
| 24 | Middle Irish | mga:G302000:#1/15:3 | Read Adcon[n]airc-sium as one verbal form, ad-cí, saw, with emphatic suffix. | RS005 | [RS005.jsonl:9](claims/RS005.jsonl) |
| 77 | Middle Irish | mga:G302000:#1/36:3 | Restore derscai[g]theach as a single adjective, outstanding. | RS005 | [RS005.jsonl:59](claims/RS005.jsonl) |
| 94 | Russian byliny | byliny:pesnisobrannyepvkireevskimch3vyp36:22795 | Editorial/biographical prose, not a bylina verse witness | RS006 | [RS006.jsonl:20](claims/RS006.jsonl) |
| 95 | Russian byliny | byliny:pesnisobrannyepvkireevskimch3vyp51:20604 | Editorial/biographical prose, not a bylina verse witness | RS006 | [RS006.jsonl:21](claims/RS006.jsonl) |
| 109 | Middle Irish | mga:celtic-journal-revue-celtique-1870-1928:revueceltique07pari:L16269-L16269 | Editorial list of cited verb forms, not a continuous Irish passage | RS007 | [RS007.jsonl:18](claims/RS007.jsonl) |
| 110 | Middle Irish | mga:celtic-journal-eriu-1904-1928:eriu_1914_7:L273-L279 | Latin editorial sic plus witness siglum H | RS007 | [RS007.jsonl:19](claims/RS007.jsonl) |
| 111 | Middle Irish | mga:celtic-journal-eriu-1904-1928:eriu_1910_4:L9175-L9177 | Apparatus variants keyed to section 27, not continuous narrative | RS007 | [RS007.jsonl:20](claims/RS007.jsonl) |
| 112 | Middle Irish | mga:celtic-journal-revue-celtique-1870-1928:revueceltique10pari:L11521-L11521:2 | Editorial dictionary reference, not a continuous Irish source passage | RS007 | [RS007.jsonl:23](claims/RS007.jsonl) |
| 113 | Poetic Edda | non:Sólarljób 82 [edda:19761] | Modern Icelandic editorial commentary, not verse 82 | RS007 | [RS007.jsonl:24](claims/RS007.jsonl) |
| 114 | Middle Irish | mga:celtic-journal-eriu-1904-1928:eriu_1910_4:L8699-L8701 | Editorial apparatus of variants labelled L | RS007 | [RS007.jsonl:25](claims/RS007.jsonl) |
| 115 | Old English | ang:Grein II And Re A S l.1686 | Apparatus citation of manuscripts and editions, not Old English verse | RS007 | [RS007.jsonl:26](claims/RS007.jsonl) |
| 116 | Middle Irish | mga:celtic-journal-zcp-1897-1926:zeitschriftfrc03meyeuoft:L185-L185 | Editorial discussion of alternative titles, not a primary narrative utterance. | RS008 | [RS008.jsonl:10](claims/RS008.jsonl) |
| 116 | Middle Irish | mga:celtic-journal-revue-celtique-1870-1928:revueceltique16pari:L8224-L8230 (w1/3) | Separate the English editorial introduction from the Irish quotation. | RS008 | [RS008.jsonl:11](claims/RS008.jsonl) |
| 116 | Middle Irish | mga:celtic-journal-revue-celtique-1870-1928:revueceltique14pari:L22341-L22343 | This is an editorial list of verbal forms with references, not continuous narrative. | RS008 | [RS008.jsonl:12](claims/RS008.jsonl) |
| 116 | Middle Irish | mga:oldirish-irische-texte-1880-1909:irischetextemit00stokgoog:L25882-L25888 (w1/3) | Editorial textual comparison containing German instructions and Irish variants. | RS008 | [RS008.jsonl:13](claims/RS008.jsonl) |
| 116 | Middle Irish | mga:oldirish-irische-texte-1880-1909:irischetextemit00stokgoog:L13233-L13235 | German grammatical/editorial commentary quoting Irish variants. | RS008 | [RS008.jsonl:16](claims/RS008.jsonl) |
| 117 | Russian byliny | byliny:11016812bsb:12350 | Lexical/editorial Russian discussion, not a bylina verse. | RS008 | [RS008.jsonl:14](claims/RS008.jsonl) |
| 118 | Middle Irish | mga:celtic-journal-revue-celtique-1870-1928:revueceltique13pari:L22520-L22524 (w2/2) | An editorial paradigm/list of preterite forms. | RS008 | [RS008.jsonl:15](claims/RS008.jsonl) |
| 119 | Russian byliny | byliny:pesnisobrannyepvkireevskimvyp1pesn13:14918 | Editorial enumeration of episodes, not an epic verse. | RS008 | [RS008.jsonl:17](claims/RS008.jsonl) |
| 120 | Poetic Edda | non:Helreið    Brynhildar 15 [edda:15443] | Prose associated with Guðrúnarkviða en forna, not Helreið Brynhildar 15. | RS008 | [RS008.jsonl:18](claims/RS008.jsonl) |
| 121 | Poetic Edda | non:Grípisspá 53 [edda:12437] | Reginsmál introductory prose about Andvari, not Grípisspá stanza 53. | RS008 | [RS008.jsonl:19](claims/RS008.jsonl) |
| 122 | Poetic Edda | non:Hymiskviða 39 [edda:5355] | Lokasenna introductory feast prose, not Hymiskviða stanza 39. | RS008 | [RS008.jsonl:20](claims/RS008.jsonl) |
| 134 | Middle Welsh | cy:welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:L21480-L21480 | Join the preceding hir with awd; this is the end of a verb of anointing, not an independent form of mynd. | RS010 | [RS010.jsonl:20](claims/RS010.jsonl) |
| 139 | Russian byliny | byliny:sbornikotdelenijarusskogojazykaislovesno92:8617 | Editorial prose describing an informant, not an epic verse unit. | RS010 | [RS010.jsonl:26](claims/RS010.jsonl) |
| 154 | Russian byliny | byliny:pesnisobrannyepvkireevskimch2pesni36:18509 | Exclude this editorial explanatory note from the verse corpus. | RS012 | [RS012.jsonl:21](claims/RS012.jsonl) |
| 155 | Russian byliny | byliny:11016812bsb:6393 | Exclude the editorial metrical correction from the verse corpus. | RS012 | [RS012.jsonl:22](claims/RS012.jsonl) |

## Collection limits

The collector still harvests only explicit `error` objects, diagnostic patterns in completion notes, and progress notes. It does not reinterpret claims or near-misses as errors. Harvested notes can be incomplete or ambiguous; unresolved forms and loci need human review. Frequency is report frequency, not corpus prevalence. Existing merging can combine distinct senses, passages, or kinds; use observations and provenance, not only the leading error. The summary expands material observations without changing that merging behavior.
