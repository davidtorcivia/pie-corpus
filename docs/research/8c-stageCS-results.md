# 8c Stage C-S results (2026-10-26)

Stage C-S is the stratified, exhaustive reading of the Stage C retrieval (design and every amendment:
[8c-preregistration.md](8c-preregistration.md)). Numbers below are recomputed by
`scripts/stagecs_measures.py` from the committed claims and verdicts and the gitignored keys; output:
`data/research/8c/stageCS/measures.json`.

## What was read

- **84 slabs, 20,084 bundles** (16,068 real, 4,016 embedded decoys = 20.0%), in a pilot and 12 waves
  (Astra medium primary readers; Opus second look on every bundle a primary reader flagged as a near-miss).
- **Stopping rule met.** Floors were frozen at the Stage C-S values (main 13.4891, thin 12.3867). After each
  wave, read pivots were left out and the unread part was rebuilt with the corrected mappings. The remainder
  fell 15,201 → 12,438 → 10,559 → 8,846 → 7,538 → 5,894 → 5,153 → 5,135 → 3,541 → 1,351 → 57 → 13 → **0**
  bundles. Fix batches lifted a few unread pivots above the floors each time (wave 7-8 plateau); the last two
  rounds were pivots that the bundle merge rule had folded into earlier bundles without recording them as
  pivots (see the prereg note of wave 11).
- **Closing rule (proposed, awaiting the owner):** the error reports of waves 10-12 go to a corpus-quality fix
  batch after Stage C-S and do not reopen the pivot pool.

## Measures

Claims of primary and follow-up readers count together; a claim found twice (same slab and anchor set)
counts once (2 duplicates); a claim citing k bundles adds 1/k to each. 65 claims counted; all graded.

| Measure (preregistered unless noted) | Real | Decoy | Ratio (95% CI) | One-sided permutation p | Criterion |
|---|---|---|---|---|---|
| **Primary (ii): accepted per bundle, all** | 1 / 16,068 | 0 / 4,016 | – | 0.80 | **not met** |
| **Primary (i): accepted per bundle, Celtic pivots** (contributing Celtic anchor) | 0 / 2,264 | 0 / 567 | – | 1.00 | **not met** |
| Secondary (ii): accepted + weak, all | 34.7 / 16,068 | 2.3 / 4,016 | 3.8 (1.0–14.7) | 0.001 | met |
| Secondary (i): accepted + weak, Celtic pivots | 4.7 / 2,264 | 0.3 / 567 | 3.5 (0.1–118) | 0.30 | not met |
| Exploratory (not preregistered): bundles flagged as near-miss by primary readers | 1,731 (10.8%) | 125 (3.1%) | 3.5 (2.9–4.2) | < 0.001 | – |

- **Reviewer grades by claim anchoring:** real-only claims 1 accepted / 29 weak / 26 reject; claims citing
  real and decoy bundles 0 / 7 / 1; decoy-only claims 0 / 0 / 1.
- **Confidence calibration:** high 1 (accepted); medium 11 weak / 2 reject; low 25 weak / 26 reject.
- **Decoy interpretation** (SCI-04): decoys keep a genuine pivot, and real candidates must share at least two
  root groups while decoys share at most one, so the ratios measure enrichment under targeted retrieval, not
  a historical false-discovery rate.

**Reading.** The primary test fails: one claim was accepted and it is a recalled textbook formula. The
secondary and exploratory measures show that targeted retrieval concentrates what readers judge plausible:
real bundles draw near-misses and accepted-or-weak claims at about 3.5-3.8× the decoy rate. Blind reviewers
confirm almost none of it as inherited phraseology; the weak grade is largely generic wording, contact or
learned transmission (Biblical and Greek models in Armenian, Latin in Norse law).

## Accepted items

All five accepted items are known formulas, and every one is marked `recalled` by its reader (the reader
recognised a formula it already knew). They are positive controls for the pipeline, not discoveries.

| Item | Track | Witnesses | Literature |
|---|---|---|---|
| *dyéws ph₂tḗr* "Father Sky" | claim (in measure) | Il. 4.235 πατὴρ Ζεύς ~ AVŚ 9.10.23 *dyaúr naḥ pitā́* | textbook |
| live and see the light of the sun | search lead | Il. 24.558 ~ RV 10.37.7d | known (West) |
| "neither earth nor heaven above" | search lead | Vsp 3 ~ Wessobrunn Prayer (Germanic pair) | textbook |
| setting a child on the knees (*sed- + *ǵónu + reflexive) | search lead | ON *setja í kné sér* ~ Il. 9.455/9.488, Od. 16.443 ~ OIr *suidid fo glún* | Onians, Benveniste, Güterbock |
| "put a name" (*h₁nómn̥ dʰeh₁-) | search lead | Arm. *anown dnel* ~ Gk ὄνομα θέσθαι ~ Ved. *nā́ma dhā-* | Martirosyan |

Search leads (158 reviewed: 4 accepted, 67 weak, 87 reject) are outside the measures: the anchoring rule and
the decoy control cannot apply to partners a reader found by searching.

## Strongest unconfirmed candidates (for the novelty check and an expert's eye)

- **bear victory** (*bʰer- + *seǵʰ-): ON *bera sigr* ~ RV 10.84.6 *sáhaḥ bibharṣi*; both words cognate; the
  reviewer did not know it as a discussed formula.
- **sleeping on someone's knees** (*swep- + *ǵónu): ON (Laxdæla, Heimskringla) ~ Hittite KUB 36.89 rev. 56-57.
  The wave-8 reject rests partly on "the Hittite sleep word is not cognate", which Kloekhorst contradicts (he
  cites this passage's *šuppariyant-* with ON *svefn*); recorded in the leads file.
- **redden the earth with blood** (*h₁rewdʰ-): Rígsþula 37, Reginsmál 26 ~ Il. 11.394, 18.329; verb cognate.
- **gods and un-gods**: OIr *dé ⁊ andé* ~ RV *deváḥ / ádevaḥ* (known; the Irish *andee* mapping is still open).
- **the bride's in-law list**: Il. 24.769-770 ~ Vuk ~ Russian ~ RV 10.85.46 (known; graded weak).
- **sweet mead**: Gk μέθυ ἡδύ ~ Ved. *svādú mádhu* (known; the Old English witness is an emendation).

Full list with witnesses and caveats: `data/research/8c/leads.jsonl`.

## What review caught

Blind reviewers opened every anchor and cited locus. Besides genericness and Biblical/Greek models they found:
a misread Vedic anchor (RV 10.115.2a: *nā́ma* "by name", *dhāyi* "established in the house"); wrong
etymologies (Arm. *eker* < *gʷerh₃-*, not *h₁ed-*; Gk χιών < *ǵʰyōm*; ON *ormr* vs Skt *kṛmi-*); the Finnsburh
39 *swētne* emendation (missed twice before the corpus marked emendations); translated sources (Alexanders
saga, Þiðreks saga). Reviewers also erred: one wrongly denied the Hittite–Norse sleep cognate.

## The error stream

Readers filed error reports alongside claims; each was verified against source and dictionary before any fix,
and fixes applied only between waves (read slabs frozen).

- **1,168 deduplicated reports** in fix batches 1-9 (167, 149, 125, 101, 112, 174, 99, 104, 137); 174 more from
  waves 10-12 are queued for the corpus-quality batch.
- **Recurring classes made general** after per-occurrence fixes kept leaking: proper names from source tags
  (about 120,000 tokens), with an exact-match exemption that keeps inherited theonyms (Ζεύς, Ἠώς, *iuppiter*,
  Þórr; 15,866 tokens regain roots); POS-decided homographs (*síða*, *vit*, *reka*, *man*, *dyr*); byliny `$`
  OCR splits (3,132 words); interleaved Lithuanian columns (5,012 units); an editorial-prose detector for the
  byliny (2,777 units, recall 21%); emendation flags in Old English.
- **Engineering finds:** two loaders duplicated in the Stage C builder (Menota, IcePaHC) silently missed fixes
  and now call the shared loaders; coverage gaps the collocation scans exposed (Umbrian *pequo*, Avestan
  *pasu vīra*) were fixed and confirmed.

## Limitations

- One accepted claim cannot support a rate comparison; the primary measure is underpowered at this yield.
- Readers are language models that recall famous formulas; every accepted item is recalled.
- Mappings improved during reading (frozen floors, but each wave read a better-mapped corpus).
- The pilot slabs were read by the official Opus reader, the rest by Astra with an Opus second look.
- Reviewer judgements are single blind reviews; at least one contained a factual error.
- The closing rule awaits the owner's sign-off; the theonym narrowing proposal is deferred.
