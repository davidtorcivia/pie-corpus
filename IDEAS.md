# Additions to PLAN.md (from the planning session, approved by David)

## Subagents are approved
Use them freely for parallel, independent work, for example:
- One agent per Tier 1 source version (each Schleicher fable or King & the God reconstruction), collecting text, citation and notation.
- One agent per Tier 2 theme cluster (dragon-slaying, imperishable fame, healing charms, …).
- Tier 3 batch generation.

Keep design decisions, the engine, and validator changes in the main session. Subagents produce records, and the main session merges them after validation.

## Improvements to fold into the plan
1. **Adversarial reviewer pass.** Before a tier is marked done, run an independent "skeptical Indo-Europeanist" subagent over a random sample. It should check ablaut, accent, case use, laryngeal coloring, and whether each Tier 2 element is actually supported by the cited cognates. Log its findings in `docs/audits/` and fix systematic errors in the engine/lexicon, not record by record.

2. **Forward sound-law checker (high value).** Implement a small set of sound laws for 3–4 daughters (Vedic, Greek, Latin, Gothic/Proto-Germanic): satem palatal merger, Grimm's/Verner's law, laryngeal coloring/loss, syllabic resonant outcomes, the Greek aspirate devoicing, the Brugmann's law approximation. Run lexicon forms forward and compare them with the Wiktionary descendants. Mismatches flag bad lexicon entries or bad normalization. It's also a strong check on the engine (inflected forms should map to attested daughter forms, e.g. *bʰéreti → bhárati, φέρει, fert, bairiþ*). Treat it as a validator stage after Phase 3, approximate and warning-only.

3. **Parallel-reconstruction dataset.** The many versions of Schleicher's fable / King & the God are effectively a parallel corpus of the same text across scholars and eras. Align them line by line (`work_group_id` + `line_no`). This is a nice eval set ("reconstruct in Byrd's style") and documents how notation changed over time.

4. **Task-format data, not just text.** Alongside the raw corpus, export instruction-style views so the fine-tuned model can do things, not only babble:
   - English → PIE translation and back
   - produce the interlinear gloss of a line
   - inflect a lemma for given features / give the full paradigm
   - given a cognate set (Skt/Gk/Lat/Goth), reconstruct the PIE form (from the lexicon reflexes; this is excellent training signal and is checkable)
   - continue a hymn or charm in the same meter

   Build the eval benchmark from the same task types on held-out data, so model quality is measurable (exact-match on paradigms and cognate reconstruction, chrF on translation).

5. **"Modern PIE" sub-tier (the funny part).** David wants the trained model to be fun. Add Tier 3b (`provenance: synthetic`, `neologism: true`) for everyday dialogue: greetings, questions, banter, a model talking about itself. Use a documented neologism policy: compounds and calques from attested roots only (e.g. a "thinking-machine" compound from *men- + a tool suffix). Log every coined word in `data/lexicon/neologisms.jsonl` with its derivation. Keep it clearly separated from Tiers 1–3 and capped at ~10–15% of training tokens, so the archaic register stays dominant.

6. **Meter is a measured property, not a label.** Compute syllable counts (and position of the caesura where relevant) from the PIE string. Only label `meter` when the count matches. That makes meter-constrained generation checkable.

7. **Coverage dashboard.** Track the root coverage %, the genre×theme grid fill, validator pass rate, tokens per tier, and neologism share in `docs/STATUS.md`. Optionally publish a small HTML dashboard as an Artifact so David can check it from his phone.

8. **Source requests.** If a source can't be found, record it in `docs/STATUS.md` under "Need from David" and keep going with something else. Don't block on it.
