# PIE benchmark (pre-registered 2026-11-01)

How well does a model speak this project's Proto-Indo-European? One fixed test set, the same for every contestant:
frontier models answering from their weights alone, and our fine-tuned models. The design, the scoring and the
weights below are fixed before any contestant runs; a change after the first run gets a new version number and a
note here.

## Items

Version 1: the frozen held-out prompt sets already used for our checkpoints. No lexeme or record in them is in any
training or RL data (training/rl/make_rl_prompts.py holds them out; tests/test_rl.py checks it).

| Segment | Weight | Items | Source |
|---|---|---|---|
| Inflection | 20 | 335 | v1 inflect (48), v2 drills inflect (287) |
| Paradigm | 15 | 124 | v1 paradigm (40), v2 drills paradigm (84) |
| EN→PIE translation | 30 | 48 | v1 translate_en_pie (24), translate_app/en_pie (24; the PIE line) |
| PIE→EN translation | 20 | 24 | v1 translate_pie_en (12), translate_app/pie_en (12; the English line) |
| Dialogue | 15 | 74 | v1 en_dialogue (48; the PIE reply), pie_dialogue (16), continuation (10) |

Excluded: v1 `gloss` (12) and the gloss lines of translate_app, whose labels are the project's own
(demonstrative_so, personal/1), which no outside model could know.

Weights: EN→PIE is the demo's main use (users type English), so it weighs most.

## Scoring

Every segment is scored 0–100 twice, **strict** and **lenient**:

- **Strict** is the project's notation: the exact form (NFC), accents and laryngeals as written.
- **Lenient** forgives notation only: accents and vowel length dropped, ASCII spellings (h2, bh, k', kw, *)
  mapped to the project's, upper/lower case ignored. A wrong ending is still wrong.

Per segment:

- **Inflection:** exact match to the reference form (as training/score_generations.py), strict and lenient.
- **Paradigm:** the share of the reference table's cells the answer gives, strict and lenient.
- **EN→PIE, PIE→EN, dialogue:** judged, because a different but valid sentence scores badly against one
  reference. Two judges, from two vendors, so no vendor grades its own models alone: Claude Opus 5.5 at high effort
  (a subagent) and GPT-6.1 Sol at high effort (Codex). Both get the project's engine and corpus tools
  (training/judge_test/pie-tool: analyze, cells, usage, lexq) and the reference. Each item scores 1 (right),
  0.5 (right meaning, one minor error) or 0 (wrong), and is marked separately for notation (strict: every word a
  real form in the project's notation). Strict counts a notation failure as 0; lenient ignores notation. A
  segment's score is the mean of the two judges; their agreement is reported.
  - EN→PIE: does the PIE say what the English says, grammatically?
  - PIE→EN: does the English say what the PIE says?
  - Dialogue: is the reply in PIE, in-world, grammatical, and a sensible answer to the turn?

**PIE score** = the weighted mean of the five segments, 0–100, strict and lenient. The hero figure is the lenient
PIE score, since the question is grammar, not the project's typography; strict is reported beside it.

## Contestants and conditions

- **Claude** Haiku 5.5, Sonnet 5.5, Opus 5.5, each at effort low, medium, high and xhigh: a custom subagent
  (.claude/agents/pie-bench.md) whose only tool is submit_answers (benchmarks/tools/submit_server.py), with no
  CLAUDE.md, no memory, no skills, no web. Subscription-billed.
- **GPT** 6.1 Terra and 6.1 Sol at reasoning effort low, medium, high and xhigh: `codex exec` with the shell,
  web search, MCP, skills and project docs disabled and a one-line instruction file, from an empty directory with
  a clean CODEX_HOME. Subscription-billed.
- **Ours:** the best fine-tuned and RL checkpoints, through one fixed generation path (training/rl/eval_ckpt.py,
  mlx_lm), with a small sweep of sampling settings (temperature, repetition penalty) reported separately; the
  setting chosen for the leaderboard is the sweep's best on a separate tuning split, never on these items.
- **Blindness is checked per run:** a contestant run with any tool call other than submit_answers, or any file or
  web access in its log, is discarded and rerun. Canary items (a file only readable with tools; a question about
  the project's memory) open every Claude and Codex configuration's first batch.
- **Batching:** frontier contestants answer 20 items of one segment per call, told to treat each on its own; our
  models answer one item per call. This difference is noted beside every result.

## Records

- benchmarks/items.jsonl: the items as contestants see them (no references).
- benchmarks/key.jsonl: the references, for scoring only.
- benchmarks/results/<contestant>/answers.jsonl: every answer, with its batch, run log path and token usage.
- benchmarks/results/<contestant>/scores.json: per-item and per-segment scores, strict and lenient, both judges.
- benchmarks/results/summary.json: one row per contestant, for the /bench chart.
