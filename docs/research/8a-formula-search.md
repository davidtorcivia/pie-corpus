# Phase 8a: formula search, first run (2026-10-23)

*Round 2 (same day) is at the end: exact per-corpus tests gave the only clear gain, recall@200 went from 0.17 to 0.50 on a 24-item set, and the verdict is still below the bar.*

**Verdict: below the bar.** The method finds a real but weak signal, and most of the loss is in mapping daughter words to PIE lexemes, not in the scoring.

## Setup
- Corpora: Rigveda (VedaWeb, Zurich lemma annotation, CC BY) and Homer (Perseus treebank 2.1, CC BY-SA). Window: Rigvedic pāda vs Homeric line.
- Mapping: corpus lemma → lexicon reflex → PIE root group. Where the lexicon lacks a direct Sanskrit or Greek reflex, rule-based bridges from the Proto-Indo-Iranian and Proto-Hellenic reflexes are used, plus a privative a-/ἀ- rule. Each bridge is accepted only if it yields an attested corpus lemma. Spot-checked precision is about 80–85%.
- Scoring: log-likelihood ratio per corpus. A pair needs LLR ≥ 3.84 and ≥ 3 co-occurrences in both corpora.
- Evaluation: the known formulas (data/formulas/formulas.jsonl, attested in Vedic and Greek) split into halves by hash. Settings were tuned on half A and frozen, then reported on half B once.

## Numbers
| | value |
|---|---|
| mapping coverage, Rigveda | 50.2% of tokens (44.4% of content words) |
| mapping coverage, Homer | 46.4% (43.6%) |
| root groups present in both corpora | 279 |
| pairs passing in both corpora | 44 |
| recall, half B (phrase + lexical), k = 50/100/200 | 2/7 (one distinct pair: *méǵh₂s* + *ḱlew-*, "great fame") |
| recall, half B with schema formulas | 4/14 |
| shuffled-corpus baseline | 0–1 pairs pass; recall 0 |

Tuning was nearly empty: half A had 4 usable formulas (7 with schemas), and 25 settings tied.

## Why it misses
- **Mapping:** many lexemes have no Sanskrit or Greek reflex listed (*h₁éḱwos*, *ḱléwos* through intermediate proto-forms only). Root groups such as *dyew-* and *peh₂-* also lump unrelated words.
- **Frequency:** the most famous formulas are rare in absolute terms. κλέος ἄφθιτον occurs once in Homer (Il. 9.413), and counting cannot find a single occurrence.
- **Evaluation size:** 7 known pairs in the test half is too few for a stable recall estimate.

## Candidates (top of data/research/formulas/candidates.jsonl; not yet reviewed)
"Yoke horses" (áśva + √yuj / ἵππος + ζυγόν), "mother and father" (merism), "hands and feet", "drink mead" (mádhu + √pā / μέθυ + πίνω), "eat and drink", "speak a formula" (mántra + √vac / μάντις + εἶπον), "great Sky" (máh + dyú / μέγας + Ζεύς). Most of these are already known in the literature or are generic collocations. Two of the top 17 are mapping errors (θυμός/dhūmá, ávas/ἄστυ).

## Next steps (not started)
1. **Mapping:** build lemma ↔ reflex tables from the full kaikki Sanskrit and Greek dumps, not just the PIE pages' descendant lists. Use derivative-level groups instead of whole roots.
2. **Third corpus:** require Avestan or early Latin as a third witness, which cuts generic collocations.
3. **Syntactic agreement:** count a pair only when the treebanks show the same relation (verb + object) in both.
4. **Larger test set:** use West's lexical formulas to grow the evaluation set beyond 7 known pairs.


---

# Round 2 (2026-10-23): evaluation set, mapping, exact tests, syntax, Latin

**Verdict: a real improvement, still below the bar for findings.** Exact per-corpus tests combined by Fisher's method raise cross-validated recall@200 from 0.17 (round-1 method) to 0.50 (95% CI 0.29–0.71; shuffled baseline 0.02). The evaluation set is only 24 items, though. Most of the gain comes from pairs that are significant in one corpus and merely present in the other. The kaikki mapping helps only together with lexeme-level counting and the exact test. Syntax and Latin add nothing measurable. No candidate is a finding until it is reviewed.

Code: `pie/formula_search.py` (kaikki links, Latin loader, exact tests, syntactic links, silver set, CV helpers), `scripts/formula_search.py` (`ablation`, `candidates`, `all`). Outputs in `data/research/formulas/`: `evaluation.json` (ablation table, eval sets, per-item held-out ranks, coverage), `candidates.jsonl`, `final_setting.json`, `spot_checks.json`, `kaikki_links/` (link cache: words, romanizations and etymon strings only). Round-1 outputs: `evaluation_round1.json`, `tuning_round1.json`.

## 1. Evaluation set
- **Gold:** every `formulas.jsonl` record with Vedic and Greek attestations (phrase, lexical, attested, schema), with its pairs built as in round 1.
- **Silver:** a West paragraph (EPUB) cites two Vedic words for PIE groups *x*, *y* within 60 characters, and two Greek words for *x*, *y* within 60 characters, and the two phrases are ≤ 400 characters apart. Words go through the corpus surface forms, then the mapping, then the kaikki dictionary words. Only pairs and chapter/paragraph refs are stored.
- **Watkins: 0 pairs.** The PDF text layer of *How to Kill a Dragon* has no Greek script at all, and its Vedic has no diacritics. There is no OCR engine here to recover them. Watkins pages are used only for the "mentioned" flag on candidates (ASCII Vedic co-citations).
- **Size:** 17 silver pairs, of which only 4 are not already gold pairs. The set is 24 items (gold formulas and silver pairs merged when they share a pair), 11 of them containing a phrase/lexical (round-1 acceptance) formula. A paragraph-wide rule would add 16 pairs, but only 2 of those are genuine, so it is not used.
- **Spot check (by reading the passages):** of the 17 strict silver pairs, 14 are genuine phrase-level parallels. The 3 failures are a demonstrative pronoun beside 'fame', West's own invented Greek rendering of a Vedic line, and 'first' plus an incidental genitive of Zeus. Counting the first 3 paragraph-wide-only pairs as well, 14 of 20 are genuine. Verdicts are in `spot_checks.json`.
- **Protocol:** folds = sha1(item's smallest pair) mod 5. Each fold's setting is chosen on the other four folds, by mean recall@50/100/200. Held-out ranks are pooled, and CIs come from 2,000 bootstrap resamples of items. The last column of the table is a paired bootstrap against the final method. **E2** is the set lemmatized with the round-2 mapping and frozen for all rows. **E1** is the same construction with the round-1 mapping (16 items). The shuffled baseline is each fold's chosen setting on corpora with PIE labels permuted across tokens (5 seeds).

## 2. Mapping (kaikki Sanskrit, Ancient Greek; Latin for step 5)
Dumps are in `raw/daughters/kaikki-{sanskrit,ancientgreek,latin}/` (logged in `raw/MANIFEST.md`; 1.8 GB in total; parsed, never executed). Links come from `etymology_templates`, tried in this order:
1. a PIE etymon (`inh/der/bor … ine-pro`, normalized with `pie.lexicon.parse_form` / `pie.notation`) that is in our lexicon
2. an intermediate proto-form (`iir-pro`, `inc-pro`, `grk-pro`, `itc-pro`) that the lexicon lists as a reflex
3. `{{root|…|ine-pro}}`
4. derivation from a same-language word that is itself linked (`{{root|sa|sa|√…}}`, one-base affix templates)
5. optionally, a PIE etymon *not* in our lexicon, as its own pseudo-entry ("pseudo"; ranked below the round-1 mapping).

The round-1 mapping is the backoff.

| content-token coverage | round 1 | + kaikki | + pseudo etyma |
|---|---|---|---|
| Rigveda | 44.4% | 59.5% | 65.4% |
| Homer | 43.6% | 63.9% | 70.1% |
| Latin (LASLA) | 25.1% | 53.5% | 57.2% |

Spot check of 30 kaikki-tier lemmas, sampled by token frequency: all 30 include the right etymon. 26 are unambiguous. 4 also carry a homograph root with the same written form: √dā- (+ *deh₂-, *deh₁-), stóma-, καλύπτω, κλισία (*ḱel-, *ḱley-). Homograph roots are the main error source, and they also cause the mapping errors among the candidates below.

## 3–5. Ablation (E2, 24 items; CI = 95% bootstrap)
| row | recall@50 / 100 / 200 | CI@50 | CI@200 | shuffled@200 | primary items@200 (n=11) | E1 @200 | final − row @200 (paired CI) |
|---|---|---|---|---|---|---|---|
| round-1 method, frozen setting | 0.17 / 0.17 / 0.17 | 0.04–0.33 | 0.04–0.33 | 0.00 | 0.27 | 0.31 | +0.33 (+0.17…+0.50) |
| round-1 method, CV-tuned | 0.17 / 0.25 / 0.25 | 0.04–0.33 | 0.08–0.42 | 0.00 | 0.36 | 0.38 | +0.25 (+0.08…+0.42) |
| + kaikki mapping (LLR, root groups) | 0.12 / 0.17 / 0.21 | 0.00–0.29 | 0.04–0.38 | 0.01 | 0.18 | 0.25 | +0.29 (+0.12…+0.50) |
| + pseudo etyma (LLR, root groups) | 0.12 / 0.12 / 0.17 | 0.00–0.29 | 0.04–0.33 | 0.00 | 0.09 | 0.19 | +0.33 (+0.17…+0.54) |
| + lexeme-level counting (LLR) | 0.17 / 0.25 / 0.29 | 0.04–0.33 | 0.12–0.50 | 0.01 | 0.55 | 0.44 | +0.21 (+0.00…+0.42) |
| **+ exact tests, Fisher (final)** | **0.29 / 0.46 / 0.50** | 0.12–0.46 | **0.29–0.71** | **0.02** | 0.64 | 0.50 | — |
| control: exact tests on round-1 mapping | 0.25 / 0.33 / 0.33 | 0.08–0.42 | 0.17–0.54 | 0.03 | 0.46 | 0.38 | +0.17 (+0.04…+0.33) |
| syntax: count linked co-occurrences only | 0.29 / 0.38 / 0.38 | 0.12–0.46 | 0.17–0.58 | 0.03 | 0.55 | 0.50 | +0.12 (+0.00…+0.25) |
| syntax: bonus if linked in both | 0.25 / 0.42 / 0.42 | 0.08–0.42 | 0.25–0.62 | 0.07 | 0.64 | 0.44 | +0.08 (+0.00…+0.21) |
| syntax: bonus for same relation type | 0.29 / 0.42 / 0.46 | 0.12–0.46 | 0.25–0.67 | 0.03 | 0.64 | 0.44 | +0.04 (+0.00…+0.12) |
| syntax: filter, same relation type | 0.12 / 0.21 / 0.25 | 0.00–0.25 | 0.08–0.42 | 0.06 | 0.36 | 0.25 | +0.25 (+0.04…+0.46) |
| Latin as tiebreaker | 0.29 / 0.46 / 0.50 | 0.12–0.46 | 0.29–0.71 | 0.03 | 0.64 | 0.56 | +0.00 |
| Latin as third Fisher test | 0.29 / 0.42 / 0.50 | 0.12–0.46 | 0.29–0.71 | 0.02 | 0.64 | 0.56 | +0.00 |
| Latin, third test only where it co-occurs | 0.29 / 0.46 / 0.46 | 0.12–0.46 | 0.25–0.67 | 0.02 | 0.64 | 0.50 | +0.04 (+0.00…+0.12) |
| Latin co-occurrence required | 0.08 / 0.12 / 0.12 | 0.00–0.21 | 0.00–0.25 | 0.03 | 0.09 | 0.12 | +0.38 (+0.17…+0.58) |
| diagnostic: final, but p < 0.05 in *each* corpus | 0.21 / 0.21 / 0.21 | 0.08–0.38 | 0.04–0.38 | 0.00 | 0.46 | 0.25 | +0.29 (+0.12…+0.46) |

**Final setting** (all five folds chose it): lexeme level, pseudo-etymon mapping, RV pāda × Homer line, content words only, hypergeometric p per corpus, ≥ 1 co-occurrence in each corpus, ranked by Fisher's combined p, no mid-p, no truncation. On the round-1 acceptance subset (11 items with a phrase/lexical formula) it reaches 0.36 / 0.64 / 0.64; round 1 had 2/7.

## What helped, what didn't
- **Exact tests: helped, but only in combination.** The final method beats the round-1 method by +0.33 at k = 200 (paired CI +0.17…+0.50). That is the cumulative gain of mapping, lexeme-level counting and exact tests together. Step by step, neither change is clearly significant on 24 items: exact tests vs the row before (lexeme-level LLR) give +0.21 (CI 0.00…+0.42), and exact tests on the old mapping beat the tuned round-1 method by only +0.08. A single co-occurrence now counts. Several recovered items have 1 co-occurrence in one corpus (sweet mead, vigorous spirit, wide fame, giver of goods). The gain is mostly *Fisher's* doing, though. Of the 12 items recovered at k ≤ 200, 7 are significant in one corpus only, e.g. Father Sky (RV p = 0.5) and Dawn shines (Homer p = 0.5). Requiring p < 0.05 in each corpus keeps only 44 pairs, and recall@200 falls to 0.21. So the signal that works is "a collocation strongly significant in one tradition that also occurs in the other". This is weaker evidence than two independent significant results, and it is what the candidate list mostly contains. Truncating each corpus at p = 10⁻¹⁰ and ranking by the weaker corpus were both tried and lost in CV.
- **Mapping: helps only with lexeme-level counting and the exact test.** At root-group level the bigger mapping *lowered* LLR recall (0.25 → 0.21 / 0.17): more mapped tokens make the big root groups (*ḱlew-*, *dʰeh₁-*, *bʰeh₂-*) more frequent and dilute them. Lexeme-level counting recovers the loss. Under exact scoring, the round-2 mapping beats the round-1 mapping by +0.17 (CI +0.04…+0.33) on E2. On E1 (built with the round-1 mapping) the gap is small and changes sign (0.50 vs 0.38 at k = 200, 0.25 vs 0.31 at k = 50), so part of the E2 advantage is the set's own bias.
- **Syntax: no gain.** The bonus for "linked in both" or "same relation type" leaves recall unchanged or lowers it. Filtering to linked co-occurrences or to the same relation type loses recall. Known formulas are often split across the line (śrávo … ákṣitam), coordinated (μένος καὶ θάρσος) or carry different relation labels in the two corpora. RV pāda adjacency is a weak stand-in for syntax.
- **Latin: no gain.** As a tiebreaker or a third test it is neutral (E1 +0.06, within noise). Requiring a Latin co-occurrence drops recall to 0.12: 145k tokens of Plautus, Lucretius, Catullus and Cato rarely repeat the Graeco-Aryan formula stock.
- **Still missed, and why:** imperishable fame. Lexeme-level counting maps ákṣiti- (a *-ti-* noun) and ἄφθιτος (*n̥-dʰgʷʰi-tó-*) to different lexemes, so the pair does not match across the corpora. At root-group level the 3 RV / 1 Homer co-occurrences are at chance level (p ≈ 0.4 / 0.5), because *ḱlew-* and *dʰgʷʰey-* are so frequent. No counting method finds a once-attested formula built from frequent words. The slaying formulas (*gʷʰen-* + serpent / lie) have no co-occurrence in both corpora under the mapping.
- **Reproducibility:** three later runs, two of them under different hash seeds, are identical. One earlier run differed by 0.04 at k = 50 on the exact rows, and I did not find the cause.

## Candidates (`candidates.jsonl`: top 200 new pairs, not in `formulas.jsonl`)
Each record has the per-corpus counts and p, the Latin evidence, RV pāda / Homer dependency relation tallies, `significant_in_both`, example loci (lemmas and verse refs only; Latin as lemmas and loci), and West/Watkins mention refs. Of the 200, 39 are significant in both corpora, 31 have the same dominant relation in both, and 66 are co-cited somewhere in West or Watkins. Most of the top of the list is one-sided and generic, for example cattle + horse (Homer p ≈ 1), dawn + sun, "speak" + "ear".

**10 most promising** (significant in both unless noted; all unreviewed):
1. *peh₃-* + *terp-*, "drink and be satisfied": píbatam ca tṛpṇutám ca (RV 8.35.10a), píba … tṛpṇuhi (2.36.4d) ~ πίνοντά τε τερπόμενόν τε (Od. 1.258), τάρπημεν … ποτῆτος (Il. 11.780). Not mentioned by West or Watkins. (Ranks 72/73: *terp-* has two homograph entries.)
2. *gʷṓws* + *steríh₂s*, "barren cow": staryàm … gā́m (RV 1.116.22d), staryàḥ ná gā́vaḥ (7.23.4a) ~ στεῖραν βοῦν (Od. 10.522 = 11.30). Adjective + noun in both. Not mentioned. Rank 43.
3. *wérsēn* + *yewg-*, "yoke the bulls/stallions": yuktvā́ hárī vŕ̥ṣaṇā (RV 1.177.1d) ~ ζεύξῃ βόας ἄρσενας (Il. 20.495). Verb + object in both. West co-cites the words but not as a phrase. Rank 86.
4. *h₁wérHus* + *póntoh₁s*, "wide path" ~ "wide sea": uraú pathí (RV 3.54.9d), pathā́ urúṇā (4.26.5b) ~ εὐρέα πόντον (Il. 6.291, 9.72). Adjective + noun in both; it depends on the πόντος/pánthā- cognation (path → sea). Co-cited in West. Rank 29.
5. *dʰers-* + *ménos*, "bold spirit": dhṛṣát mánaḥ (RV 1.54.3b) ~ μένος καὶ θάρσος (Il. 5.2, Od. 1.321). The Greek is coordinated, not attributive. Ranks 135/179.
6. *déywih₂* + *gʷḗn*, "divine (among) women": gnā́ṃ devī́m (RV 5.43.6b), devī́r … jánīnām (5.46.8d) ~ δῖα γυναικῶν (Il. 2.714, 3.171). Rank 45.
7. *déywih₂* + *h₂éwsōs*, "divine Dawn": devī́ uṣás ~ Ἠὼς δῖα. Probably known in the literature (West co-cites it). Rank 15.
8. *h₂éwsōs* + *nókʷts*, dawn and night (merism). Probably known. Rank 20.
9. *médʰu* + *peh₃-*, "drink mead": RV 51×, Homer 2×. Known (round 1), but not in `formulas.jsonl`. Rank 1.
10. *h₁éḱwos* + *yewg-*, "yoke horses": RV 12×, Homer 8×, verb + object in both. Known (round 1). Rank 18.

**Flagged mapping errors:**
- φημί 'say' vs √bhā 'shine' (*bʰeh₂-* homographs): ranks 6–8, 16–17, 106–107.
- βοῦς εἰλίπους/ἕλιξ vs valá- (two different roots *wel-*): 5, 10.
- ζητέω vs √yā 'go': 27–28.
- ψυχρός under *bʰes-* 'chew': 48, 147.
- áditi- under *h₁ed-*: 121.
- ásita- under *sēmi*: 130.
- ἴσος under *wí*: 151–152.
- bráhman- / πύργος under *bʰerǵʰ-*: 181.
- υἷος ἑῆος, where ἑῆος is lemmatized as ἐύς (a contested reading): 95.

**Flagged generic or semantically diverged:**
- θυμὸν ὀρίνω vs dhūmá- + √ṛ ("smoke rises"): 23.
- mast in the middle (*médʰyos* + *steh₂-*): 38.
- φέρω + χέρνιψ: 21.
- 'man' + 'see': 137.
- 'other' + 'heal': 157.
- 'gaze over the sea' (*póntoh₁s* + *derḱ-*): 75.

## Next steps
1. Grow the test set beyond West: OCR the Greek in the Watkins scan, or hand-enter Watkins's index of Greek forms. This is the bottleneck: 24 items give CIs ±0.2.
2. Disambiguate homograph roots by the template's gloss or `id` argument (the main mapping error).
3. Map derivatives to one shared "stem family" so that ákṣiti- and ἄφθιτος meet without falling back to the whole root.
4. Report one-sided and two-sided candidates separately. Send the two-sided, same-relation ones (1–6 above) to an independent reviewer per PLAN.md.
