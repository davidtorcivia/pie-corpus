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
