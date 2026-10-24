# Mapping precision: Sanskrit (rv, av)

Scope: the lemma → PIE-lexicon mapping of the two Sanskrit corpora.
- **rv**: the Rigveda, VedaWeb/Grassmann lemmas, mapped live in `pie/formula_search.py`. The table used is the round-2 "pseudo" kaikki mapping plus the errata.
- **av**: the DCS Atharvaveda (Śaunaka + Paippalāda) and Ṛgvedakhilāni, read from `data/research/formulas/mapping/av.jsonl` (`apply_table_overrides`).

Corrections are in `data/research/formulas/mapping-overrides/sanskrit.json`. No code, lexicon or shared file was changed.

## Results

Each sample has 100 content-word types (NOUN/VERB/ADJ/PROPN in DCS; nominal stem/root in VedaWeb), drawn with probability proportional to token frequency, without replacement. Draw: key = u^(1/freq), `random.Random(seed)`, lemmas sorted, top 100 kept.

**Precision** = correct / mapped. **Lenient** counts partials as correct too.

| corpus | sample | mapping | mapped (of 100) | correct | partial | wrong (of which mixed) | precision | lenient | unmapped but mappable |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| rv | seed 0 | before | 58 | 41 | 2 | 15 (8) | **70.7%** | 74.1% | 19 |
| rv | seed 1 | before | 64 | 45 | 3 | 16 (9) | 70.3% | 75.0% | 7 |
| rv | seed 1 | after batch 1 | 64 | 55 | 3 | 6 (3) | **85.9%** | 90.6% | 4 |
| av | seed 0 | before | 55 | 45 | 1 | 9 (5) | **81.8%** | 83.6% | 19 |
| av | seed 1 | before | 64 | 43 | 0 | 21 (12) | 67.2% | 67.2% | 10 |
| av | seed 1 | after batch 1 | 65 | 60 | 0 | 5 (3) | **92.3%** | 92.3% | 5 |

- **Same items, before and after.** Seed 1 was judged once per item, under both the pre-override and the post-override mapping. The before/after difference on seed 1 therefore comes from the overrides, not from a change of sample.
- **Sample noise is large.** At n ≈ 60 mapped types, one item is about 1.6 points. Seed 0 and seed 1 differ by 15 points for av before any change.
- **Batch 2 (90 rows) and the `pad` row are not in these numbers.** It was written after the seed-1 measurement, from sibling lemmas of the batch-1 errors and from the errors seed 1 surfaced. It would remove all 6 rv and all 5 av residual errors of seed 1, but that is an in-sample figure, not a measurement.

Coverage of content tokens (types mapped):

| corpus | before | after (both batches) | tokens whose mapping changed |
|---|---:|---:|---:|
| rv | 65.4% (1828 types) | 65.1% (1822) | 18.7% |
| av | 61.4% (1569) | 61.7% (1560) | 15.0% |

Coverage moved in two directions:
- **Unmaps lowered it.** Some very frequent false etymologies were unmapped: índra- (2435 tokens), bráhman-, vratá-, rudrá-, áhan-.
- **Additions raised it.** Secure etyma were added for √as- 'be' (1366 RV tokens; DCS *as* has 1606), nár-, bṛhánt-, hótar-, mahā́nt-, duhitár-, nápāt-, ghṛtá-, mṛtyú-, hvā, etc.
- **The rest changed precision only.** About a sixth of all content tokens now carry a different mapping.

## Overrides

There are 339 rows: 181 for rv and 158 for av. Counted against the "before" tables:

| | rv | av | total |
|---|---:|---:|---:|
| corrections (ids replaced) | 117 | 95 | 212 |
| unmaps (empty lex_id) | 35 | 36 | 71 |
| additions (lemma was unmapped) | 29 | 27 | 56 |

They come in three groups:
- **Batch 1:** 248 rows, 136 rv and 112 av. This is what the seed-1 "after" measures.
- **Batch 2:** 90 rows, 45 rv and 45 av, each note tagged `[batch 2]`.
- **Coordinator fix:** 1 row, av `pad`.

**Re-running seed 1 against the current file will not reproduce the table.** It will show the batch-2 effects too. The measured "after" is the file without the rows tagged `[batch 2]` and without the `pad` row. Neither of those touches a seed-1 item beyond the ones listed in the appendix.

**The av `pad` row.** It refines the shared erratum row, which still lists pie-lex-pedyeti, an id flagged wrong in mapping-errata.md and by tests/test_mapping_overrides.py. The new row is ['pie-lex-poxds', 'pie-root-ped-walk'].
- DCS *pad* merges the noun pád- 'foot' (LemmaId 171474, 43 tokens) and the verb PAD 'fall, go' (157388, 32 tokens: padye, padyatām; EWAia II 76 < *ped-*).
- The verb is kept through the root id rather than through the flagged lexeme.
- rv `pád-` is already ['pie-lex-poxds'] in the shared file.

**Row format.** Each row has `erratum` (a short label of what was wrong) and `note` (the evidence). The `erratum` key is needed because `apply_rec_overrides` reads `row["erratum"]` for every row. Evidence is:
- EWAia volume and page, located in the OCR via the running page numbers. Where the OCR page could not be found, the note gives "s.v. ROOT".
- VedaWeb surface forms for Grassmann's numbered homographs.
- DCS LemmaId counts for merged DCS lemmas.

**Validation.** Every lemma string occurs in its corpus, and every lex_id exists in the lexicon. `load_overrides` and `apply_rec_overrides` run on the file.

**Mirroring in av.** av.jsonl was built by joining DCS lemmas to the RV mapping by accent-free key (`R3._sanskrit`), and that join copies every RV error. Each RV fix is therefore repeated for the matching DCS lemma where a DCS content lemma exists. A merged DCS lemma gets one row covering the senses actually present.

**Test status.** `tests/test_mapping_overrides.py::test_override_table_covers_the_errata` still fails after the `pad` fix, on a different check. That check requires every row's `erratum` first word to occur in mapping-errata.md.
- No per-language file can meet it. The check fails for 191/191 east rows, 221/221 germanic, 685/860 greek, 173/175 italic and 321/339 sanskrit.
- Dropping the `erratum` key is not an option either: `apply_rec_overrides` would then raise KeyError.
- The test needs to restrict that check to the shared file, or accept `note`. That is a test change, which is outside this brief.

## Method

1. Built the rv mapping as in `Env` (r1 + kaikki pseudo) and the av table from av.jsonl. "Before" applies the shared errata and every other group's override file, but not sanskrit.json.
2. Measured seed 0 (before) for both corpora.
3. Checked the 300 most frequent mapped lemmas of each corpus, and the most frequent unmapped ones, against EWAia (I–III, OCR, read with `python3 -I`), with VedaWeb forms and DCS lemma ids. This produced batch 1.
4. Measured seed 1, judging every item under both mappings.
5. Batch 2: swept both corpora for lemmas mapped to ids that are homographs of correct ones (e.g. *ḱewk-* 'call', *pewH-* 'rot', *dʰeh₁y-* 'suck', *stew-* 'push', the pronoun *is*, *we* 'or', *suHs* 'pig'). Each hit was checked, and the seed-1 residual errors were fixed.

**Judging rules** (fixed before seed 1):
- **Correct:** every id belongs to the right etymon. A root id or any lexeme of that root counts.
- **Partial:** right root, wrong formation, e.g. rā́jan- → *h₃rḗǵs*, nárya- → *h₂nḗr*, prathamá- → *pro*.
- **Wrong:** the set contains any false etymon. "Mixed" means a right id plus a wrong one.
- **Speculative etymologies.** If EWAia calls an etymology unclear, disputed or unproven ("unklar", "nicht sicher", "umstritten", "willkürlich"), the mapping counts as wrong and the override unmaps it. If EWAia endorses the etymology ("wohl", "glaubhaft"), it is kept, even when the id is a kaikki pseudo-entry; examples are víśva-, sahásra-, svastí-, maṇí-, maghá- (EWAia II 289: *magʰ-*).
- **Merged DCS lemmas.** Where a DCS lemma string merges homographs (pā = PĀ¹ 'protect' + PĀ² 'drink'; vas = three VAS roots; kṣi, naś, aś, pṛ, gṛ, iṣ), a mapping that covers the senses actually present is correct. One that covers only a minority sense is wrong; pā → 'drink' only was wrong because 59% of its tokens are 'protect'.

## Main error types (before)

1. **Homograph roots merged.** This is the largest class, over half of the wrong items in both samples. The kaikki path attaches every lexicon root of the same shape. For example, √pū- 'purify' got *pewH-* 'clean' + 'rot'.
   - Others of this kind: √dhā- 'put' + 'suck', √stu- 'praise' + 'push', √śuc- 'glow' + 'call', √mad- + 'meet', √sac- + 'say', 'see', √bhā- 'shine' + 'speak', √tap- + 'smear', √nud- + 'use', √bhī- + 'strike'.
   - Also pronouns or particles of the same shape: √i- 'go' + *is* 'this', √mā- 'measure' + *eǵh₂*, *meh₁*, √hi- + *ǵʰi*, √vā- 'blow' + *we* 'or', √nu- 'praise' → *nu* 'now'.
2. **Grassmann's numbered homographs ignored.** √pā- 1 'protect' (pāhi, pātu) was mapped to *peh₃-* 'drink'. √vas- 1 'shine' (ucchati) went to 'dwell' + 'dress'. √kṣi- 'dwell' went to *dʰgʷʰey-* 'perish'. √naś-, √yā-, √iṣ-, √vṛ- and √gṝ- had both senses on both numbers. √vidh- 1 'worship' went to *h₁weydʰh₁-* 'separate', and the DCS join then sent AV *vidh* to √vidh- 2 'pierce'.
3. **False or speculative etyma**, unmapped per EWAia:
   - Divine names: índra- (I 192f), rudrá- (II 452f), víṣṇu- (II 566), pūṣán- (II 158f).
   - Other words: bráhman- / bṛ́haspáti- (II 236f: *bʰreǵʰ-*, "nicht vorzuziehen" *bʰerǵʰ-*), vratá- (II 594f: "muß willkürlich bleiben"), áhan- 'day' → *gʷʰen-* 'strike', vána- 'tree' → *wénh₁os* 'desire', śátru-, dásyu-, ádri-, dhána-, krand, apsarás-, kṣatrá- → *tek-* 'weave', śarád-, púruṣa- → *perh₃-*, aruṣá- → *h₂elut-* 'beer', skambhá- → *skabʰ-* 'scratch'.
4. **Wrong root chosen.**
   - √vṛdh- 'grow' → *h₁lewdʰ-*, which is the root of ruh; correct is *h₂werdʰ-*.
   - gír- 'praise-song' → *gʷerh₃-* 'swallow'.
   - áditi- → *deh₂-* / *h₁ed-*; correct is DĀ 'bind' *deh₁-*.
   - √sṛ- 'flow' → three *sel-* roots; correct is *ser-*.
   - √śā- 'sharpen' → 'lie' / 'darkness'; correct is *ḱeh₃(y)-*.
   - √vyadh- → 'separate'; correct is *h₂wyedʰ-*.
   - takmán- 'fever' → a pseudo *tenk-*; correct is *tap-mán-* (TAP, EWAia I 611).
   - jā́- 'offspring' → *ǵneh₃-* 'know'.
   - The DCS join compounded this. Joining by the first RV key match sent AV hṛ 'take' to √hṛ- 2 'like', and AV svar 'sun' to the verb √svar- 'sound'.
5. **Unmapped though secure.** √as- 'be' is the most frequent verb of both corpora and was unmapped. Others: nár-, bṛhánt-, hótar-, mahā́nt-, duhitár-, nápāt-, ghṛtá-, stotár-, mṛtyú-, dīrghá-, kṛ́mi-.

## What remains

- **Unmeasured batch.** Batch 2 is not measured. A fresh seed-2 sample would give a clean figure for both batches.
- **Lexicon gaps** (no entry for the right root, so these stay unmapped):
  - VAR¹ 'cover' (√vṛ- 1, vṛtrá-, āvṛ). The lexicon's *h₂wer-* 'lift' has the gloss "to cover, to enclose" but only an Armenian reflex.
  - SAV³ 'impel' (savitár-, √sū- 1).
  - KṢAY² 'rule' (kṣatrá-).
  - *bʰreǵʰ-* (bráhman-).
  - SKAMBH *ske(m)bʰH-*.
  - *sh₂om-* (sā́man-).
  - HAR¹ 'take', which has no etymology at all.
- **Lexicon root_id errors** these overrides cannot fix:
  - pie-lex-tkjeyti → *tek-* 'sire' (already noted in the shared errata). Root ids are used instead.
  - pie-lex-h2enyos (anyá-) has root *h₂enh₁-* 'breathe'. anyá- is therefore left on *h₂élyos* and judged partial.
  - pie-lex-dhugh2texr has root *dʰewgʰ-* 'hit', so duhitár- now groups with √duh-.
- **Residual errors seen in seed 1 and fixed only in batch 2.** For rv: √vā-, √ji- 2 ~ jinv-, vṛ́dh-, √nas-, bhójana-, ádbhuta-. For av: āsya, diś, sāman, āvṛ, aha.
- **Formations.** Derivatives mapped to the base noun or root count as partial and were left: rā́jan-, nárya-, samudrá-, prathamá-, anyá-.
- **Unmapped with no lexicon target.** Frequent names and words like váruṇa-, aśvín-, marút-, síndhu-, tanū́-, adhvará- remain unmapped. EWAia has no secure PIE etymon for them.
- **Merged DCS lemmas.** The av table is keyed by DCS lemma string, so merged homographs get the union of their roots: pā, vas, kṣi, naś, aś, pṛ, gṛ, iṣ, sū. Splitting them needs the DCS LemmaId in the loader, which is a code change.

## Appendix: wrong and partial items per sample

Codes: C correct, P partial, W wrong, WM wrong-mixed, N unmapped. Every other item of each sample was judged C, U (unmapped but mappable) or N (unmapped, no secure lexicon target). Item numbers are positions in the seeded sample (`random.Random(seed)`, keys u^(1/freq) over the sorted content-lemma list; RV content = VedaWeb class "nominal stem"/"root", AV content = DCS NOUN/VERB/ADJ/PROPN).

**rv seed 0 (before):**
- 4 rájas- WM (+ *h₃reǵ-)
- 10 índra- W (pseudo *h₃eyd-; EWAia I 192 not secure)
- 13 nárya- P (→ base noun *h₂nḗr)
- 21 √kṣi- W ('dwell' → 'perish')
- 37 √pū- WM (+ 'rot')
- 39 √pā- 1 W ('protect' → 'drink')
- 44 √cit- WM (+ *kʷeyt-* 'begin to shine')
- 50 √dhā- 1 WM (+ 'suck')
- 51 máda- WM (+ 'meet')
- 55 rā́jan- P (→ *h₃rḗǵs*)
- 63 drapsá- W (→ *drep-* 'cut off')
- 71 vána- W ('tree' → *wénh₁os* 'desire')
- 72 suvṛktí- W (VARJ → *h₁erkʷ-* 'praise')
- 75 √vṛ- 1 WM ('cover' → 'lift' / 'choose')
- 84 √śuc- WM (+ 'call')
- 86 √mad- WM (+ 'meet')
- 97 ávāta- W ('unassailed' → *h₂weh₁-* 'blow')

**av seed 0 (before):**
- 0 rājan P
- 48 pā W (DCS lemma is 59% 'protect', mapped to 'drink' only)
- 55 vasu WM (+ two *h₂wes-* roots)
- 61 prasū WM (+ 'pig')
- 63 gaṇa W (→ *gʷerH-* 'praise')
- 77 viṣṇu W (EWAia II 566 'nicht klar')
- 80 svadhā WM (+ 'suck')
- 87 dhā WM (+ 'suck')
- 88 kulyā W (pseudo *keh₂ul-*)
- 96 hu WM (+ 'call')

**rv seed 1 (before→after batch 1):**
- 6 √i- 1 WM→C (+ pronoun *is*)
- 11 áditi- W→C
- 14 gír- W→C
- 17 √vā- WM→WM (+ *we* 'or', *h₁weh₂-*; fixed in batch 2)
- 21 √ji- 2 ~ jinv- W→W (→ *gʷey-* 'win'; batch 2)
- 26 anyá- P→P (→ *h₂élyos*)
- 29 vṛ́dh- W→W (→ *h₁lewdʰ-*; batch 2)
- 40 índra- W→N
- 47 √mad- WM→C
- 54 √dhā- 1 WM→C
- 55 √vas- 2 WM→C
- 61 √vṛ- 1 WM→N
- 69 √nas- WM→WM (+ 'nose', pronoun; batch 2)
- 72 prathamá- P→P
- 76 vṛtrá- WM→N
- 84 bhójana- WM→WM (+ 'flee'; batch 2)
- 89 samudrá- P→P
- 96 ádbhuta- W→W (→ *dʰebʰ-*; batch 2)
- 99 √pā- 1 W→C
- Also changed: 5 √as- 1 U→C, 51 ghṛtá- U→C, 81 pūrvyá- U→C.

**av seed 1 (before→after batch 1):**
- 1 śī WM→C
- 2 aṅga W→N
- 3 āsya WM→WM (+ 'sit'; batch 2)
- 10 diś WM→WM (+ 'throw'; batch 2)
- 11 pā W→C
- 13 indra W→N
- 15 hi WM→C
- 20 i WM→C
- 24 vrata W→N
- 32 dhā WM→C
- 34 vṛdh W→C
- 38 pṛ WM→C (+ *perh₃-*)
- 40 pū WM→C
- 41 sāman W→W (→ *senh₂-*; batch 2)
- 59 ās WM→C
- 60 svar WM→C
- 61 yā WM→C
- 66 hṛ W→N
- 78 āvṛ WM→WM ('cover' → 'lift' + 'choose'; batch 2)
- 81 kṣi W→C
- 94 aha W→W (particle → *h₁e*; batch 2)
- Also changed: 12 as, 14 dīrgha, 76 bhuvana, 85 mṛtyu, 97 dakṣiṇa U→C.
