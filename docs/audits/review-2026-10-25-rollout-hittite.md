Review findings (2026-10-25), as received from an external engineer.

## 2. Some new behavior has not reached the published artifacts
This is the clearest remaining engineering issue: the code has moved further than several stored records.

### A. The dual-to-plural fallback flags are missing from all six affected stored tokens
The realizer now correctly computes `"num_fallback": "du->pl"`, and the exporter knows how to pass that flag on to tasks. But the affected corpus tokens have not been updated, so the default export contains no fallback-tagged tasks.

The six affected records:

| Corpus record | Stored realized form | In default training? |
|---|---|---|
| b003, record 192 | bʰidn̥tó | Yes |
| t005, record 16 | bʰebʰih₂ḗr | Yes |
| t010, record 12 | tetr̥pḗr | Yes |
| t016, record 7 | kʷrn̥tó | Yes |
| t016, record 11 | ḱéyro | Yes |
| t022, record 28 | sléh₂gʷontor | No |

Re-realization identifies all six as dual controllers that take the plural fallback, and all six stored tokens lack the new flag. This is a gap in rolling out metadata, not a new error in the surface forms. The fix should update the affected corpus metadata, verify that the change is limited, and renew the corresponding release bindings explicitly. The new content-bound approvals rightly prevent an approved artifact from being changed silently while it keeps its old approval hash.

### B. Two Tier 2 evidence records still describe the old checker
The new agent-noun handling changes the live evidence for two records, but their stored evidence and notes are stale:

| Record | Stored evidence | Current checker result |
|---|---|---|
| t2-poetics-gifts-007, giver noun | none; no exact branches | exact: Greek + Indo-Iranian |
| t2-sky-father-011, begetter noun | root; Indo-Iranian + Italic | exact: Indo-Iranian + Italic |

This reproduces with the shipped lexicon and the shared mapping population. In poetics-gifts-007, the stored giver token still has `interpolated: true`, and the notes still say the builder cannot recognize the suffix-accented formation; that explanation is now obsolete. sky-father-011 carries the same kind of obsolete note.

A targeted rebuild should refresh `secure_checks`, the derived token fields and the obsolete notes. Editorial review and evaluation-grade decisions stay separate: a change in automatic evidence should not rewrite those judgments automatically. Otherwise regeneration is in good shape: all 2,195 Tier 3 records and 98 Tier 2 records reproduce their PIE, ASCII, English, gloss, token forms and features.

## 3. The Hittite expansion needs two narrower corrections

### A. Two derivatives receive exact evidence for their nominal bases
Both reproduce through the production secure checker:

| Hittite lemma | Current target | Its own override note says | Live result |
|---|---|---|---|
| ištamašš=@hören | stéh₃mn̥, a nominal entry | the hearing verb is an s-extension of the nominal base | exact |
| taganzip=a-@Erde | dʰéǵʰōm, 'earth' | the formation is 'earth' plus a further element | exact |

Neither override sets `formation: "derivative"`, although their notes already contain what is needed to classify them. Under the project rule that exact means the same formation, both should be capped at root level, as *táin* now is.

Minimal fix: keep the mappings, add the derivative classification, regenerate the table, and verify that no other route can restore exact evidence. Neither lemma is in current Tier 2 records, so this is a live checker defect, not a misgrading of an existing Tier 2 sentence.

### B. The doubtful tier loses its qualifications on the way to the reader
The eight-row doubtful table is correctly excluded from the ordinary mapping population, and Stage C-S deliberately opts into it for retrieval. But `read_union_table()` reduces each row to `lemma → tuple(ids)`, which drops the low-confidence flag, the source and page, and the reason for doubt. The renderer then shows an ordinary-looking etymon annotation. For the `arun=a-@Meer` row, for example, the annotation gives the root *h₃er-* and its gloss with none of the recorded qualification. The loss happens in the union-table adapter and in the word renderer.

Keep these equations available for exploratory retrieval, but carry their known uncertainty into the reader's word annotations and the later review record. A general warning that automatic mappings can be wrong does not replace a specific qualification the system already has.

There is a related policy issue for secure evidence. Leaving the doubtful file out does not stop existing reflex routes from crediting the same equations. With the main-only checker:
- aruna- still gets exact evidence for pie-lex-h3rewnos through an existing Hittite reflex;
- šuḫḫa-i still gets exact evidence for pie-lex-sh2ewti through an existing Hittite reflex.

The doubtful table documents the uncertainty of both. That does not show either reconstruction is false, since another authority might support it. It shows that "the checker never reads the doubtful file" and "a doubtful equation cannot receive secure credit" are different guarantees. For secure use, record an explicit decision for each: either document the independent support that justifies accepting it, or apply a targeted uncertainty cap across every route.
