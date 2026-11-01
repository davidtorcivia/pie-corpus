# Judge test: Claude subagents as the meaning judge for RL (2026-10-31)

Owner: RL reward stays local; Claude (subagents, not the API) augments it, possibly as a judge in the loop. Question:
how well do Sonnet and Opus at low and high effort judge PIE, and at what token cost?

**Set** (training/judge_test/build_items.py, seed 20261031). 60 items from approved Tier 3 dialogue batches t089–t109,
15–45 words each, English + PIE. 24 untouched. 36 with one planted error: 12 wrong inflections
(make_review_packet.corrupt), 12 noun or verb swaps to another lexeme in the same cell (a meaning error that still
parses), 12 removed negations. J25 is excluded from scoring: its swap ('leave' → 'leave over') is a near-synonym that
reads correctly, so 35 plants count.

**Judges.** Four Claude Code subagents, same brief, blind. Tools: training/judge_test/pie-tool. `analyze` gives
lemma, gloss and cell per word; `cells` gives paradigms; `usage` gives corpus examples, with the items' own records
excluded; `lexq` is the lexicon lookup. No direct reads of corpus/, export/ or training/.

| Judge | Caught (of 35) | Inflection · swap · negation | False alarms (of 24) | Tokens (60 items) | Per item | Wall time |
|---|---|---|---|---|---|---|
| Sonnet 5.5 low | 32 | 11/12 · 10/11 · 11/12 | 0 | 153 k | ~2.6 k | 14 min |
| Sonnet 5.5 high | 32 | 9/12 · 11/11 · 12/12 | 1 (J23, borderline) | 278 k | ~4.6 k | 12 min |
| Opus 5.5 low | 32 | 9/12 · 11/11 · 12/12 | 1 (J33) | 145 k | ~2.4 k | 16 min |
| Opus 5.5 high | 33 | 10/12 · 11/11 · 12/12 | 0 | 218 k | ~3.6 k | 8 min |

**False alarms, read by hand:**
- J33 (Opus low) is wrong. It flagged "feminine numeral with masculine ǵʰéyomn̥s", but ǵʰéyōm is f in the lexicon.
- J23 (Sonnet high) is borderline. It flagged a feminine adjective on márkons 'mares'. The project gives female animals
  f agreement, though round 6 added h₁éḱwah₂ 'mare'.

**Misses:** case-role errors that leave a valid form. A NOM where 'at the assembly' needs a LOC (J21), NOM.PL for a
VOC.SG address (J37), NOM for an ABL (J39). Meaning errors (negation, word swap) are caught almost always.

**Reading:**
- The four are equal within the noise (one item of 35), so effort buys nothing measurable here.
- Sonnet low is the cheapest setting with no false alarms.
- A judge adds what the local reward lacks: meaning.
- Case-role errors need a local check as well. Each judge missed 2–3 of the 12.

**Cost in the loop:** about 2.5 k tokens per judgment at Sonnet low, so 48 k judgments come to ~120 M tokens. Two
levers bring that down to ~15–30 M per RL run:
- precompute the analyzer output into each item, since most of a judge's tokens are tool calls;
- send to the judge only the samples the local reward passes, because a local failure is already a verdict.

## Round 2: Haiku, and precomputed analysis (same 60 items)

Items_v2 (training/judge_test/add_analysis.py) carry each word's engine analysis inline (lemma, gloss, all readings);
the tool stays available. Scored without J25 (35 plants).

| Judge | Format | Caught (of 35) | Inflection | False alarms (of 24) | Tokens (60 items) | Wall time |
|---|---|---|---|---|---|---|
| Sonnet low (round 1) | tool | 32 | 11/12 | 0 | 153 k | 14 min |
| Sonnet low | analysis inline | 29 | 9/12 | 1 (J23) | 187 k | 3 min |
| Haiku 5.5 low | analysis inline | 30 | 7/12 | 1 (J59) | 218 k | 4 min |
| Haiku 5.5 medium | analysis inline | 31 | 9/12 | 9 | 260 k | 7 min |
| Haiku 5.5 high | analysis inline | 34 | 11/12 | 2 (J27, J59) | 279 k | 8 min |

- **Inline analysis is not a cost lever.** The full reading lists make each prompt longer than the tool calls they
  replace, and Sonnet low got worse with them: it missed two dropped negations it had caught with the tool.
  Annotating only unknown or ambiguous words is untested.
- **Haiku high's two false alarms are defensible.** In J27 and J59 a 2PL addresses one person who speaks for a group
  ("we will lay them", "we will pay"), so the plural is acceptable.
- **Haiku high is the only run that caught J21 (NOM for LOC) and J37 (NOM.PL for VOC.SG).**
- **Haiku is erratic across efforts:** medium raised 9 false alarms on the same items.
- **Proposed loop judge:** Haiku high screens every sample, and Sonnet low (with the tool) re-checks only the flagged
  ones. Before relying on it, repeat Haiku high once on this set to check that 34/35 holds.

## Round 3: the API judge, one item per call (2026-11-01)

The RL judge sees one rollout per call, so round 3 sends each item alone through the Claude API
(training/judge_test/api_judge.py: round 2's brief, the analysis inline, no tools). Each call's usage gives the
cost. Scored without J25 (35 plants, 24 untouched).

| Run | Analysis | Caught (of 35) | False alarms (of 24) | $ per 1,000 judgments |
|---|---|---|---|---|
| Haiku high, 2 runs | items_v2 | 34, 35 | 16, 14 | 1.51–1.62 |
| Haiku high, then Sonnet low on its flags | indeclinables fixed, first sense only | 34 | 9 | 1.4 + 10.6 on flags |
| Haiku high, 2 runs | items_v3, every reading | 34, 33 (+2 unparsed catches) | 2, 2 | 1.36 |
| Haiku high, then Sonnet low on its flags, 2 runs | items_v3 | 31, 29 | 1, 1 | 1.36 + 10.5 on flags |

**One item at a time, Haiku over-flags at first, and the analysis was the cause, not the model.** Of round 3's first
false alarms, most were the engine's analysis misleading the judge:
- **Indeclinables missing from the analyzer.** Adverbs whose realizer spec is rule "indeclinable" but inadmissible
  (h₂éyeri 'in the morning', h₂éti 'again', Hn̥dʰí 'under', h₂ewsér 'at dawn', h₂éd 'to') were skipped by both
  indexing loops, so they fell to fuzzy verb matches ('go' MID.SBJV.1SG). Fixed in pie/translator/analyze.py; this
  also fixes the translator's analysis of every such word.
- **A reading cap.** The analysis kept the first 4 readings. An adjective's gender readings filled them, and the
  homograph noun (ḱóymos 'village' beside ḱóymos 'homely') was cut off. items_v3 groups the readings by lexeme and
  keeps all of them; the judge tool (tools.py) no longer caps either.
- **One-word glosses.** The analysis showed the first sense only (somHós 'same', not 'alone'). items_v3 adds every
  sense of each lemma.
- **Project grammar.** Five rules the judge brief now states: a neuter plural subject takes a singular verb; verbs of
  fearing take the ablative; with no augment, a PST form is also the injunctive (mḗ + injunctive is a prohibition);
  the middle can change a verb's meaning; a 2PL can address one speaker for a group. These were checked in the audits
  (fear-ablative-2026-10-30.md, t034, t062, b002), but they were added after seeing this set's false alarms, so the
  set is no longer blind to them; a fresh judge set should confirm them.

**The Sonnet confirmation tier hurts.** Sonnet low cleared real errors that Haiku had caught: two of the dropped
negations (J34, J57) and an inflection (J52), with "all words match". It removes one false alarm and costs 3–5
catches. Haiku high alone, on the fixed analysis, matches the round 2 subagent result (34/35, 2 false alarms) at
**$1.36 per 1,000 judgments**, about 1.7 s of wall time per judgment at 6 in parallel.

The false alarms left are misreadings, read by hand: J55 flags the feminine somHéh₂ 'alone', but the son is
speaking to his mother, so the feminine is right; J16 flags te 'you' after 'lie', but ne te dʰréwgʰm̥ is 'I did not
lie to you'; J03 is the neuter-plural rule the brief states.

**For the RL judge:**
- Proposed: Haiku high alone, no Sonnet tier (the owner's call; Sonnet re-checking with the engine tool, as in
  round 1, is untested per item).
- Unparsed answers (an unescaped quote in the reason) are now read by pattern; both unparsed ones were catches.
- The org's concurrent-request limit is low (a 429 at 16 parallel calls); 6 in parallel works.
- Cost: at 10–20% of 30–50 k rollouts reaching the judge, about $5–15 per run.
