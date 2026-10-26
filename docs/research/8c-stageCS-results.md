# 8c Stage C-S results (2026-10-26)

**Summary.** Under the preregistered primary measure, Stage C-S found no inherited phraseology beyond
recalled textbook formulas. The enrichment measures (real bundles draw near-misses and accepted-or-weak
claims at about 3.5× the decoy rate) are consistent with readers tracking the root overlap that defines a
real bundle; they do not show that retrieval finds inheritance. One candidate-new item survives as a lead:
"bear victory" (ON *bera sigr* ~ RV *sáhaḥ bibharṣi*), not found in the held literature.

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

**How to read the decoy comparison** (SCI-04): a real bundle's partners must share at least two root groups
with the pivot, one outside the 50 most frequent; a decoy's partners share at most one and no rare root, and
readers see the etymon annotations. Decoys keep a genuine pivot. A higher claim or near-miss rate on real
bundles is therefore partly built into the construction: it shows enrichment of reader judgements under
targeted retrieval, not a historical false-discovery rate.

Claims of primary and follow-up readers count together; a claim found twice (same slab and anchor set)
counts once (2 duplicates); a claim citing k bundles adds 1/k to each. 65 claims counted; all graded. The
permutation test is the preregistered one; the rate-ratio intervals are Poisson approximations on fractional
weights (secondary (ii): the interval touches 1.0 while the permutation p is 0.001).

| Measure (preregistered unless noted) | Real | Decoy | Ratio (95% CI) | One-sided permutation p | Criterion |
|---|---|---|---|---|---|
| **Primary (ii): accepted per bundle, all** | 1 / 16,068 | 0 / 4,016 | – | 0.80 | **not met** |
| **Primary (i): accepted per bundle, Celtic pivots** (contributing Celtic anchor) | 0 / 2,264 | 0 / 567 | – | 1.00 | **not met** |
| Secondary (ii): accepted + weak, all | 34.7 / 16,068 | 2.3 / 4,016 | 3.8 (1.0–14.7) | 0.001 | met |
| Secondary (i): accepted + weak, Celtic pivots | 4.7 / 2,264 | 0.3 / 567 | 3.5 (0.1–118) | 0.30 | not met |
| Exploratory (not preregistered): bundles flagged as near-miss by primary readers (80 slabs; the four pilot slabs had no near-miss line type) | 1,731 / 15,191 (11.4%) | 125 / 3,796 (3.3%) | 3.5 (2.9–4.2) | < 0.001 | – |

- **Reviewer grades by claim anchoring:** real-only claims 1 accepted / 29 weak / 26 reject; claims citing
  real and decoy bundles 0 / 7 / 1; decoy-only claims 0 / 0 / 1.
- **Confidence calibration:** high 1 (accepted); medium 11 weak / 2 reject; low 25 weak / 26 reject.

**Reading.** The primary test fails: one claim was accepted and it is a recalled textbook formula. Real
bundles draw near-misses and accepted-or-weak claims at about 3.5-3.8× the decoy rate, which fits readers
responding to visible root overlap; blind reviewers confirm almost none of it as inherited phraseology. The
weak grade is largely generic wording, contact or learned transmission (Biblical and Greek models in
Armenian, Latin in Norse law).

## Accepted items

All five accepted items are known formulas, and every one is marked `recalled` by its reader. The reader
brief defines it: "mark a claim `"recalled": true` when it is something you remember from the literature
rather than see in the passages." They are positive controls for the pipeline, not discoveries. Novelty was
checked against the held literature in `raw/books/text/` (West IEPP, Watkins HKD, Schmitt 1967,
Mallory–Adams, Fortson; Martirosyan for Armenian).

| Item | Track | Witnesses | Novelty (held literature) |
|---|---|---|---|
| *dyéws ph₂tḗr* "Father Sky" | claim (in measure) | Il. 4.235 πατὴρ Ζεύς ~ AVŚ 9.10.23 *dyaúr naḥ pitā́* | known (West) |
| live and see the light of the sun | search lead | Il. 24.558 ~ RV 10.37.7d | known (West) |
| "neither earth nor heaven above" | search lead | Vsp 3 ~ Wessobrunn Prayer (Germanic pair) | known (West, Schmitt) |
| setting a child on the knees (*sed- + *ǵónu + reflexive) | search lead | ON *setja í kné sér* ~ Il. 9.455/9.488, Od. 16.443 ~ OIr *suidid fo glún* | not in the held books; reviewers cite Onians, Benveniste, Güterbock (not held) |
| "put a name" (*h₁nómn̥ dʰeh₁-) | search lead | Arm. *anown dnel* ~ Gk ὄνομα θέσθαι ~ Ved. *nā́ma dhā-* | Martirosyan s.v. *anun* (per the reviewer) |

Search leads (158 reviewed: 4 accepted, 67 weak, 87 reject) are outside the measures: the anchoring rule and
the decoy control cannot apply to partners a reader found by searching.

## Strongest unconfirmed candidates (for the novelty check and an expert's eye)

- **bear victory** (*bʰer- + *seǵʰ-): ON *bera sigr* ~ RV 10.84.6 *sáhaḥ bibharṣi*; both words cognate.
  **Not found in the held literature** (findings lit-0056 to lit-0059; near-hits only: Fortson's name *Berenike* "bearing victory", whose
  νίκη is not cognate; West's Sigrdrífumál 3 "give victory", a different verb). The one candidate-new item.
  Graded weak: the senses differ ("carry off the victory" vs "bear might") and the Norse is hagiography.
- **sleeping on someone's knees** (*swep- + *ǵónu): ON (Laxdæla, Heimskringla) ~ Hittite KUB 36.89 rev. 56-57.
  Not found in the held literature. The wave-8 reject rests partly on "the Hittite sleep word is not
  cognate", which Kloekhorst contradicts (he cites this passage's *šuppariyant-* with ON *svefn*).
- **redden the earth with blood** (*h₁rewdʰ-): Rígsþula 37, Reginsmál 26 ~ Il. 11.394, 18.329; verb cognate,
  the earth noun differs. Not found in the held literature.
- **gods and un-gods**: OIr *dé ⁊ andé* ~ RV *deváḥ / ádevaḥ*: known (West IEPP ch. 2 cites exactly Táin
  2043 ~ RV 6.22.11); the Irish *andee* mapping is still open.
- **the bride's in-law list**: Il. 24.769-770 ~ Vuk ~ Russian ~ RV 10.85.46; graded weak; not found as a
  phrase-level comparison in the held books (reviewers cite Delbrück, Benveniste; not held).
- **sweet mead**: Gk μέθυ ἡδύ ~ Ved. *svādú mádhu*: known (West IEPP ch. 2); the Old English witness is an
  emendation.

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
