# 8c: narrowing the theonym exemption (2026-10-28)

Record: `data/research/8c/corpus-quality/theonym-narrowing.json`.
Reproduce with `scripts/audit_theonym_narrowing.py` (before / after / report).

## Rule

Batch 6 (`data/research/8c/stageCS/error-verdicts-w6-theonyms.json`) let a
source-tagged name keep its lemma and roots whenever the lemma mapped exactly
to an inherited PIE lexeme. That also kept ordinary names: Homeric Μέντωρ was
read as *men-* "think", and the town Ἕλος as its common noun. Those readings
produced false collocates in phrase search.

David approved a narrower rule. An exact-match name keeps its roots only if it
also appears on `THEONYMS` in `pie/name_mapping.py`. That allowlist holds
deities and personified natural or abstract powers, per language, and each
entry carries a one-line justification. Every other source-tagged name becomes
"X (name)" and is non-content. `exact_name_ids` now requires both conditions
through `theonym_allowed`.

`PERSONAL_HOMOGRAPHS` and `REVIEWED_NORSE_PERSONAL_HOMOGRAPHS` are kept as
reviewed records and as a second guard. Under the new rule they are redundant.

The change applies to future builds and to the search index. Read slabs and
committed Stage C-S results stay as they are.

## Allowlist

The allowlist has 80 entries: grc 24, la 23, sa 14, non 17, orv 2. It was
built from a census of every lemma that the batch-6 gate kept bare in hom,
grc, grc-late, grp, lat, av, sa-ep, orv, menota and icepahc. The Sanskrit
entries are preventive, because neither DCS selection name-tags a Vedic
theonym, so av and sa-ep do not change. Norse entries outside the census: `óðr` is the wave-9
reviewed divine exemption; `þór`, `baldr`, `týr` and `nótt` are preventive,
like the Sanskrit set.

## Counts (tokens that lose roots; whole corpus, no sampling)

| corpus | tokens | lose roots | census lemmas kept / now "(name)" |
|---|---:|---:|---|
| hom | 200,145 | 31 | 8 / 7 |
| lat | 144,786 | 55 | 23 / 22 |
| av | 107,134 | 0 | 0 / 0 |
| sa-ep | 1,409,567 | 0 | 0 / 0 |
| grc | 3,809,801 | 676 | 18 / 37 |
| grc-late | 10,657,541 | 2,742 | 21 / 51 |
| grp (overlaps grc) | 340,300 | 182 | 17 / 23 |
| orv | 122,818 | 65 | 2 / 12 |
| menota | 1,650,615 | 260 | 5 / 31 |
| icepahc | 255,967 | 800 | 8 / 95 |

The aggregate without grp is 4,629 tokens.

In every corpus, no allowlisted (deity) token loses its roots, and no token
gains roots. The Homeric losses are Μέντωρ 20, Ἄκτωρ 3, Ῥέα 2, Σεμέλη 2,
Ἕλος 2, Δαίδαλος 1 and Μέμνων 1. Homer keeps 752 deity tokens: Ζεύς 696,
Βορέας 25, Ἀΐδης 12, Ἔρεβος 7, Εὖρος 6, Ἥβη 4, Φόβος 1 and Ὥρα 1. The JSON
breaks the losses down by lemma for each corpus.

## Borderline decisions

Where a case was borderline, the decision went toward "(name)". The full list
with reasons is under `borderline_decisions` in the JSON.

- **Πόντος → (name).** This is the largest borderline (177 grc and 443
  grc-late tokens). A personified Sea exists, but as a tagged name Πόντος
  almost always means the region Pontus or the Black Sea. Lowercase πόντος is
  unaffected. This changes a batch-6 test expectation.
- **Deity, wrong lexeme → (name).** These are deities whose exact match is a
  homograph or a folk etymology, not the word for the power:
  - Νηρεύς: *nér* "below"
  - Τρίτων: "three"
  - Ῥέα: "dew"
  - Ἕως: the conjunction "until"
  - Δίς: "twice"
  - волосъ (Volos): "wolf"
  - Norse mars: "horse"/"sea"
- **Half-deities and mortals → (name):** Σεμέλη, hercules, Ὀρφεύς, Μέμνων,
  Δαίδαλος, Μαῖα (her name is the common noun "mother, nurse"), gróa,
  glámur, askur, gunnr.
- **Rivers, mountains and constellations as geography → (name):** Στρυμών,
  Ἠριδανός, Πάδος, Ῥᾶ, rhenus, дунаи, бугъ, Ταῦρος, Ἄρκτος, septentrio.
- **Titles and kinship words → (name):** Πατήρ, pater, mater, faðir,
  sonur. Also natural nouns tagged as names that are not personified in these
  texts: himinn, haf, sumar, stjarna, IcePaHC ás, dies and lux.
- **Kept, with notes:** Ἀΐδης and Ἔρεβος (David's examples); Κόρος (Satiety,
  rare); Μήν (the Moon god Men); Λήθη; Τέρμων; Χθών; Δεύς; Latin liber (the
  god) and manes; дивъ and стрибогъ; Christian guð, drottinn (the Lord) and
  andi (the Holy Spirit); and the Norse hel, áss, Hǫðr, Sól, Máni, Dagr and
  Jǫrð.
- IcePaHC pronouns and numerals mis-tagged NPR (hann, þetta, ég, þú, þér, sá,
  vér, mér, hún, tveir) now lose roots. This corrects an error; no deity is
  lost.
