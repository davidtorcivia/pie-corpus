# Phase 8a: formula search, first run (2026-10-23)

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
