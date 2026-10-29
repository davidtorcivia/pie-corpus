# export/

Written by `uv run python -I scripts/export.py` (pie/export.py; policy in its docstring and docs/STATUS.md).

- `train.jsonl`, `eval.jsonl`: records. `train_tasks.jsonl`, `eval_tasks.jsonl`: task views. `views/`: plain text.
- `eval_tasks_accent_specified.jsonl`: the **accent-sensitive evaluation view**, `eval_tasks.jsonl` without the tasks flagged `"accent": "unresolved"`.

## Benchmark hold-out (changed 2026-10-28)

The cognate→PIE and inflection eval tasks come from held-out root families: the frozen list
`data/export/held_roots.json` (written by `scripts/build_holdout.py`, read through `pie.export.eval_root`),
restricted to families no training record uses. Families in `data/export/protected_roots.json` (formula
vocabulary such as *dʰugh₂tḗr*, Tier 2 secure lexemes, the planners' core lists, numerals, Swadesh-type kin,
body-part and natural-world nouns) are never held out. Until 2026-10-28 a 10% hash of root_id chose the
families instead. **Benchmark scores from before and after the swap are not comparable**: the held families,
and so the cognate and inflection eval sets, are different (docs/STATUS.md "Known limitations" (3)).

## Accent flags

Every task whose target or one of whose tokens comes from a lexeme with an unresolved accent carries `"accent": "unresolved"`: the Wiktionary headword has no accent and no source used here supplies one. This is missing information, not a claim that the word was unaccented. A task whose target or token is a representation exception carries `"accent": "representation"`: the vocative *ph₂ter* and its kind, where the notation cannot show the initial vocative accent. Both lists are in data/morph/accent_unresolved.json, and docs/STATUS.md "Known limitations" explains them. Tier 1 texts are not flagged, because their accents are their authors'.

Flagged tasks stay in the full eval and in training. **A score presented as testing fully specified accent must be computed on `eval_tasks_accent_specified.jsonl`**, not on `eval_tasks.jsonl`. `summary.json` gives the flagged counts by task type (`*_by_accent_flag`).

**Schema clarification (2026-10-25, DOC-01).** Raw corpus records/tokens do not store the derived task-level accent flags. Raw consumers join token `lex_id` values to `data/morph/accent_unresolved.json` (through `Lexicon.accent_status` / `accent_status`); exported tasks carry the derived status. For engine-built Tier 2/3 record tasks, any unresolved token yields `accent: unresolved`; otherwise a matching frozen representation cell/form yields `accent: representation`. Inflection targets use the frozen lexeme/gender/cell/primary-form tuple; cognate-to-PIE tasks derive unresolved status from the target lexeme. Tier 1 authorial accents are not flagged this way. Representation limitations and genuinely unaccented clitics remain separate from lexical uncertainty. Unresolved lexemes remain morphologically usable under the existing policy. The evaluation invariant is `eval_tasks_accent_specified == [task for task in eval_tasks if task.get("accent") != "unresolved"]`; representation tasks remain in that view. This clarification changes no linguistic decisions, stored corpus schema, or export behavior.

## Number fallback

Engine-built Tier 2/3 tokens carry `"num_fallback": "du->pl"` when a dual
controller or explicit pro-drop dual is realized with a plural because the dual
cell is unavailable (Ringe 2006 pp. 31–32). `features` still names the realized
plural cell; `gender` and `voice` keep their usual meanings. Available duals and
ordinary plurals have no fallback key. Record exports preserve this token metadata;
translation (both directions) and gloss tasks carry the same flag if any source
token carries it. Alternative forms remain alternatives of the realized cell.
Existing corpus records need regeneration before they carry the marker; export
does not infer it from an unmarked plural token.

## Batch eligibility

Default export admits Tier 3 only with current PASS gates and content-bound
review approval in `data/generation/releases/`. Missing, malformed, or stale
evidence excludes the batch before root-family holdouts are computed.
`summary.json` reports every batch decision and exclusion reason.
`--experimental-batches` explicitly bypasses eligibility and records the bypass;
pilots additionally need `--include-pilot`. See
[the migration and release policy](../docs/audits/eng-01-release-migration.md).

## Chat export (for fine-tuning chat models)

Written by the same `scripts/export.py` run (pie/export_chat.py), from the same splits; nothing is re-split.
For token counts, run it as
`uv run --with tokenizers python -I scripts/export.py --tokenizer <path to Qwen3-4B tokenizer.json>`.

| file | what |
|---|---|
| `chat/train.jsonl`, `chat/eval.jsonl` | one conversation per line: `{"messages": [{"role": "system"\|"user"\|"assistant", "content": …}], "meta": {…}}` |
| `chat/summary.json` | examples per kind, Qwen3-4B token counts per kind, tokens per word (Unicode vs ASCII), leakage report, Tier 3b neologism share, source commit |
| `text/train.txt`, `text/eval.txt` | plain PIE for LM loss: one text per paragraph (blank-line separated, each on one line); a Tier 1 work is one paragraph in line order |
| `text-ascii/…` | the same in `pie_ascii`, for a tokenizer ablation |

**Trainer-neutral.** The messages carry no chat template and no special tokens: the trainer renders them
with each model's own template. Train on the assistant turns only (the default "last assistant message" /
"all assistant messages" loss masking).

**Kinds** (`meta.task`):

- Task conversations: `translate_en_pie`, `translate_pie_en`, `gloss`, `inflect`, `cognates_to_pie` (one per
  task in `train_tasks.jsonl`/`eval_tasks.jsonl`) and `paradigm` (lemma → a noun's declension, an adjective
  in one gender, or one finite block of a verb, from the engine; one per lexeme with inflection tasks, in
  that lexeme's split). Several paraphrased prompt templates per task (`meta.template`), chosen by a
  crc32 of the item, so the choice is stable across runs. The assistant turn is the task's exact output, so
  eval scoring compares it directly (`meta.acceptable` and `meta.token_variants` carry the alternatives
  for en→PIE). The reconstruction convention ("project handbook convention" or a named scholarly
  reconstruction for Tier 1) is stated in the system turn, never mixed into the user text.
- `pie_dialogue`: PIE-only conversations. The system prompt (English) says to answer only in PIE; every
  user and assistant turn is PIE. Built from the dialogue-like genres (`dialogue`, `greeting`, `challenge`,
  `parley`, `council`, `farewell`, `riddle`) by splitting a text into turns. `meta.split` records how:
  `speaker` when the plan's clauses name a speaker (wave-2 / Tier 3b plans; consecutive sentences of one
  speaker form a turn, exactly two speakers, the first is the user), else `sentence_qa`, a conservative
  heuristic: a run of questions is a user turn, the run of statements after it is the reply, statements
  before the first question open the first user turn. A record is skipped when its `?` disagree with the
  plan's `question` flags or no question is answered; a trailing unanswered question is dropped
  (`meta.dropped_trailing`). Skips are counted in `summary.json`. Single-question records (b001–b004) are
  not paired across records.
- `continuation`: the user gives the opening of a hymn, prayer, story, fable, epic or charm in PIE (about
  40% of its sentences, or of a Tier 1 work's lines) and the assistant continues it in PIE.
- `bilingual_chat` (a minority, one aligned dialogue in three): the user writes English and asks for a PIE
  reply; each assistant turn is fixed-format: the PIE reply, a newline, then `English: <translation>`.
  Only dialogues whose PIE and English sentences align one to one are used.

**Meta flags**: `tier`, `genre`, `meter` (the record's), `accent` (`unresolved` | `representation`, see
"Accent flags"), `coined` (`project` | `neologism`), `neologism: true` (Tier 3b records),
`num_fallback`, `seen_in_train` (eval only: a Tier 1 line Tier 3 reuses verbatim), `style`, `root_id`.
An accent-specified score uses the eval conversations without `meta.accent == "unresolved"`, as with
`eval_tasks_accent_specified.jsonl`.

**Hold-out and leakage.** `chat/eval.jsonl` is exactly the eval task views (Tier 1, eval-grade Tier 2, the
held families' inflection and cognate tasks, plus their paradigms) and continuations of eval records. The
export fails if an eval source id has any train example (any template), if an eval (user, assistant)
pair or a multi-word eval assistant turn occurs verbatim in train, or if 50% or more of an eval PIE
assistant turn's word 4-grams occur in train (all train messages and `text/train.txt`). Items flagged
`seen_in_train` are reported in `summary.json`, not failed. The per-kind overlap distribution is reported.

**Tier 3b cap.** PLAN.md caps Tier 3b (`neologism: true`) at 10–15% of training tokens. The export warns
on stderr when the share in the training records exceeds 15%; `summary.json` `neologism` gives the share.

**Loading.** Any SFT trainer that reads OpenAI-style `messages` takes the files as they are:

```python
from datasets import load_dataset
ds = load_dataset("json", data_files={"train": "export/chat/train.jsonl", "eval": "export/chat/eval.jsonl"})
# TRL: SFTTrainer(model, train_dataset=ds["train"].remove_columns("meta"),
#                 args=SFTConfig(assistant_only_loss=True, ...))
```

On Tinker, render each conversation with the model's renderer and train on the assistant tokens (names as in
the tinker-cookbook renderers; check them against your version):

```python
import json
from tinker_cookbook import renderers
renderer = renderers.get_renderer(renderer_name, tokenizer)   # the model's own (e.g. qwen3, Nemotron's)
for line in open("export/chat/train.jsonl"):
    ex = json.loads(line)
    tokens, weights = renderer.build_supervised_example(ex["messages"])   # weights = assistant tokens
```

For the plain text, split `text/train.txt` on blank lines and train with LM loss on every token (a base
checkpoint, or the instruct model before chat SFT). Filter on `meta.task` to train or score one kind, e.g.
`pie_dialogue` + `continuation` for speaking PIE, the task kinds for grammar.
