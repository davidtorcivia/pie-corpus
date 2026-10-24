# Tier 2 (back-projection) adversarial review, round 3

Reviewer: an independent "skeptical Indo-Europeanist" subagent, 2026-10-23.
Scope: five new lines: epic-diction-001 to -004 (`corpus/tier2/epic-diction.jsonl`) and poetics-gifts-016 (`corpus/tier2/poetics-gifts.jsonl`). For each line I read pie, english, tokens, cognate_refs with roles, secure_checks, notes and generator.plan.
Standards: `docs/generation/tier2-brief.md` and round 2's verdict rules (`docs/audits/tier2-review-r2.md` §0), applied unchanged.
Machine-readable verdicts: `data/tier2/review-r3.jsonl`.
Caveat: as in round 2, this review was not plant-calibrated.

## Verdicts

| id | verdict | core | deciding fact |
|---|---|---|---|
| epic-diction-001 | sound | *h₂eh₃mó- *kréwh₂s *h₁ed- | Verb exact in 3 branches, verb + object exact in Ved/Gk. The full triad is in one clause only in Il. 22.347. |
| epic-diction-002 | weak | *wes- + *n̥mr̥tó- | Head is root-level only (Ved. root-present middle vs Gk active s-aorist). The engine's nasal present appears in neither passage. |
| epic-diction-003 | weak | *swéh₂du médʰu | The OE witness (Finnsburh 39 swētne) is Ettmüller's conjecture; Hickes reads hwitne. Ved/Gk alone is sound. |
| epic-diction-004 | weak | *h₁éḱwōs *n̥mr̥tṓs | Generic epithet pair (P5). The scholarly claim is for the motif only; the Avestan has non-cognate anaoša-. |
| poetics-gifts-016 | weak | *ḱlew- + *wékʷos + 1sg | Object exact; head root-level only (nasal-present subj. vs thematic aorist). |

Totals: 1 sound, 4 weak, 0 reject.

## Findings

1. **Emendation counted as an attestation (epic-003).**
   - The note says OE swētne medo was "checked in the Gutenberg Beowulf appendix". That text (Harrison–Sharp) prints the emendation silently.
   - Grein's apparatus (`raw/daughters/oe-poetry-grein/`, Bibliothek vol. 1, Finnsburh 39) gives Hickes's transcript, the only witness, as *hwitne* 'white', with *svêtne* from Ettmüller.
   - The OE branch therefore rests on an editor, and branches = 3 is an overclaim.
   - Fix: drop the OE ref or demote it to support, marked conjectural. The line then stands as a sound NP formula on Vedic and Greek, on the same pattern as fame-005.
   - The Vedic is thin: RV 1.84.10 is the only RV stanza with the pair (full sweep), and there svādóḥ and mádhvaḥ stand in separate pādas.
   - Brief-level lesson: when the local corpus has an apparatus, a word that carries a parallel must be checked against the manuscript reading, not only against a normalized edition.
2. **Construal corrections (epic-001).**
   - AGDT tags ὤμ' in Il. 22.347 as attributive to κρέα. The note calls it predicative.
   - In AVŚ 8.6.23, āmám agrees with māṃsám, not with kravíḥ.
   - The NP āmá- + kravís- occurs only in RV 1.162.10. That passage has no verb, and its context is the horse sacrifice.
   - The line survives because the Greek clause alone has all three words, the verb and object are exact in two branches, and the three savage contexts agree. West's claim covers only the compound *ōmo- + *ed- (ὠμηστής = āmā́d-).
3. **Generic pair (epic-004).**
   - "Immortal horses" has no lexical claim in the literature we hold.
   - West ch. 3 n. 127 cites Durante for the motif only. Durante 1976 is not held, so whether it makes a lexical claim cannot be checked.
   - The Avestan passage behind that claim, Yt. 10.125 (CAB YtMihr32.3), has auruuaṇtō … anaōšā̊ŋhō. Neither word is cognate.
   - A full RV sweep finds no áśva- + amṛ́ta- NP.
   - Treated like round 2's dawn-sun-009: weak, at the reject edge.
4. **Head rule (epic-002, poetics-016).** In both lines the verb is shared only at root level, and the notes say so honestly.
   - poetics-016 is the better line. Both sides are formulaic in their own traditions (3× RV, 2× Il.), and the object *wékʷos is the same formation.
   - epic-002 is weaker:
     - Its Greek formula's head is εἵματα, which Vedic lacks.
     - Its instrumental follows one Vedic passage.
     - Its voice (active) follows Greek against the Vedic middle.
5. **Loci.** Every cited locus was confirmed locally and contains the cited words. That covers AVŚ 8.6.23, 9.1.1, 13.1.24 (DCS); RV 1.162.10, 10.87.7, 6.75.18, 1.84.10, 10.66.11, 1.145.3, 10.65.13 (VedaWeb); Il. 22.347, 16.670, 16.680, 16.380-381, 16.866-867, 16.236, 14.234, 11.454 and Od. 9.297, 9.162, 17.533, 24.59 (AGDT); Hymn. Hom. 6.6 (glaux); the Vǫlsungakviða in forna 9 (FJ 1926); and Finnsburh 39 (Gutenberg and Grein).
   - No fabricated attestation was found.
   - The one problem with a locus is the emendation in finding 1.
6. **Engine forms.** In none of the five lines does a daughter contradict a secure form.
   - The one engine form that stands in neither passage is epic-002's nasal present *wes-néw-. It is marked interpolated/root-level, and the note says so.
   - Minor lexicon point, with no effect on output: pie-lex-h2eh3mos is linked to a root 'be hot', a doubtful etymology for 'raw'.
