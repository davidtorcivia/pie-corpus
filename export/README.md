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
| `chat/train_mix.jsonl` | a subset of `chat/train.jsonl` in the target mix (English input 50%, PIE chat 15%, see "Mix"): **the default SFT file for the chat model** (the LLM you converse with) |
| `translator/train.jsonl`, `translator/eval.jsonl` | **the translation app's dataset**: every translator item in both directions, English → PIE and PIE → English, 1:1 (see "Translator dataset"). Not part of the chat model's mix |
| `translator/summary.json` | the translator dataset's examples per direction and unit, gloss coverage, assistant-turn self-overlap, leakage report, source commit |
| `chat/summary.json` | examples per kind and per mode, the mix table, user turns per kind and the multi-turn breakdown (`turns`), the translator's items, the self-overlap measure, English-alignment coverage of the dialogues, demo seeds used/skipped, the conversational eval's counts, Qwen3-4B token counts per kind, tokens per word (Unicode vs ASCII), leakage report, Tier 3b neologism share, source commit |
| `eval_dialogues.jsonl` | the records reserved for the conversational eval (data/export/held_dialogues.json) |
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
- `pie_dialogue`: PIE-only conversations (`meta.mode` `pie_pie`). In training these are the dialogues that
  get no English-input conversation (no sentence alignment, or narrated) and, whole, one in two (crc32,
  `PIE_PIE_EVERY`) of the aligned dialogues: the same exchanges as their English-input conversations, with
  the user turns in PIE (see `en_dialogue`); the conversational eval has every reserved dialogue in it. The system prompt (English) says to answer only in PIE; every
  user and assistant turn is PIE. Built from the dialogue-like genres (`dialogue`, `greeting`, `challenge`,
  `parley`, `council`, `farewell`, `riddle`) by splitting a text into turns. `meta.split` records how:
  `speaker` when the plan's clauses name a speaker (wave-2 / Tier 3b plans; consecutive sentences of one
  speaker form a turn, exactly two speakers, the first is the user); else `english_quotes` when the record's
  English is nothing but quoted speeches ('Who is at the door?' 'I am a stranger.' …) whose sentences are
  exactly the aligned English: each speech is a turn, the speakers alternate, the first is the user (strict
  alternation: a speaker who goes on in a second quotation is read as the other speaker); else
  `sentence_qa`, a conservative heuristic: a run of questions is a user turn, the run of statements after it is the reply, statements
  before the first question open the first user turn. A record is skipped when its `?` disagree with the
  plan's `question` flags or no question is answered; a trailing unanswered question is dropped
  (`meta.dropped_trailing`). Skips are counted in `summary.json`. Single-question records (b001–b004) are
  not paired across records.
- `continuation`: the user gives the opening of a hymn, prayer, story, fable, epic or charm in PIE (about
  40% of its sentences, or of a Tier 1 work's lines) and the assistant continues it in PIE.
- `en_dialogue`: the same dialogues with **English user input**, for chatting with the model in English.
  Every aligned dialogue of k exchanges (a user turn and its reply) gets (`mode_plan`):
  `en_pie` on the whole dialogue; `en_pie_gloss` on the whole when k ≤ 3, else on one half of the exchanges
  (`[:k//2]` or `[k//2:]`, two or more exchanges each, so a dialogue stays multi-turn); `mixed` on the whole
  when k is 2 or 3, on the other half when k ≥ 4; and on one aligned dialogue in two (crc32) `pie_pie` on
  the whole (k = 2 or 3: instead of `mixed`). So each assistant turn is trained in at most three
  dialogue-mode examples (`DEDUP_CAP` 3; `meta.window`: the exchanges an example covers, when not the
  whole). The modes:
  - `en_pie`: every user turn is the English of the user's sentences; every assistant turn is PIE only.
    System prompt: "Reply in Proto-Indo-European."
  - `en_pie_gloss`: as en_pie, but each assistant turn is fixed-format: the PIE reply, a newline, then
    `English: <translation>`. The first user turn may carry a request for PIE ("Answer me in PIE: …").
  - `mixed`: the user switches between English and PIE from turn to turn (`meta.user_langs`, at least
    one of each); the assistant always answers in PIE. System prompt: "The user may write in English or
    in Proto-Indo-European. Always reply in Proto-Indo-European."

  Every dialogue that splits into turns and **aligns sentence by sentence** with its English, and is not
  narrated, gets them (`summary.json` `dialogue_english_alignment`). The alignment (`align_english`,
  `meta.align`): the plan's per-sentence `english` when every sentence-initial clause has one
  (`plan_english`, exact; the optional plan field in docs/generation/planner-brief-v4.md); otherwise the
  record's English split at sentence ends (`plain`), also after a closing quote (`quotes`), also at a
  "said:" frame before a quotation (`quotes_colon`), also at semicolons (`semicolon`,
  `quotes_semicolon`); the first split whose sentence count equals the PIE's and whose `?` fall on the
  same sentences is used. A record no split aligns is skipped (`unaligned:<reason>`), never guessed. A
  narrated dialogue ("Then the master said: …", `narrated:<split>`) keeps its pie_dialogue but gets no
  English-input conversation, since its frames would be user turns that are not conversation. Quotation
  marks and "User:"/"Model:" turn markers are removed from the English.
- `translate_app`: the **translator** (English in, PIE out, gloss alongside), for the translation app;
  format below. Built from every record with English: its sentences (a Tier 1 work: its numbered lines)
  are partitioned into items of one to three sentences (crc32; about half sentence-level, half short
  paragraphs, `meta.unit`, `meta.sentences`; a line without final punctuation, such as a title, ends its
  item), so every sentence is in exactly one item. A record whose
  English does not align sentence by sentence is one item when it has at most three sentences, else
  skipped (`summary.json` `translate_app`). In the chat data one item in five (crc32) is the inverse mode
  (`meta.mode` `pie_en`; the default is `en_pie`): PIE → English stays small for the chat model. The
  translation app's dataset (`translator/`) has every item in both directions. Tier 3b records are treated
  the same way.
- `app_session`: a few multi-turn translator sessions (train only): adjacent `en_pie` items of one text,
  in text order, chained into one conversation of two or three requests ("And this: …", "Next: …"). They are
  the same items, not copies: each sentence is still in exactly one translator example. Chained requests
  (`app_session` and the two-turn `demo_chat` seeds) are capped at 10% of the multi-turn examples
  (`APP_SESSION_SHARE`), so the multi-turn data is conversation, not a phrasebook.
- `demo_chat`: a small hand-written seed set for the live demo (data/export/demo_seeds.jsonl): English
  requests ("Can you say hello?", "Who are you?", "Translate: …", "How do you say 'horse'?", "And
  'horses'?"), one to two turns each, mode `en_pie` or `en_pie_gloss` by crc32. The answers are never
  written by hand: each is a sentence (or a run of sentences) of a **training** record, checked against
  its aligned English, or an engine cell (`admissible_cells`) of a lexicon entry that occurs in a training
  record (so never a held-out family), or of a Tier 3b neologism (data/lexicon/neologisms.jsonl; flagged
  `coined: neologism`, `neologism: true`). A seed is skipped whole when any answer does not resolve
  (`summary.json` `demo_seeds.skipped`): the seeds about the model itself point at the Tier 3b chat
  batch t3b-001, now admitted, so all 51 seeds resolve. Train only.

**Translator format** (`translate_app`, `pie.export_chat.app_format` / `parse_app`). System prompt, fixed:
"Translate English into Proto-Indo-European. Give the PIE, then a word-by-word gloss." The user turn is the
English text alone. The assistant turn is one field per line, in this order:

```
PIE: príHe te ne memónh₂e. nu moy téwe wékʷesh₂ smr̥téy h₁ésti. smḗymi.
Gloss: dear-VOC.SG personal/2-ACC.SG.ENCL NEG think-PRF.1SG NU personal/1-GEN.SG.ENCL personal/2-GEN.SG word-NOM.PL memory-LOC.SG be-PRS.3SG smile-PRS.1SG
Notes: smr̥téy: a modern coinage built from inherited roots.
```

- `PIE:` always; the translation, with sentence punctuation.
- `Gloss:` the `gloss` task's own Leipzig-style gloss for those words (the record's gloss sliced by each
  sentence's word count), one gloss word per PIE word, in order. Left out, never guessed, when the record has
  no gloss (Tier 1 texts) or its gloss does not have one word per PIE word; `meta.gloss_reference` says
  whether the line is there.
- `Notes:` optional: the item's coined words (a Tier 3b neologism: "a modern coinage built from inherited
  roots"; a project reconstruction: "not a standard handbook form"). No other notes are written.

To parse: split on newlines; a line starting `PIE: `, `Gloss: ` or `Notes: ` opens that field. The inverse
mode's system prompt is "Translate Proto-Indo-European into English. Give the English, then a word-by-word
gloss."; the user turn is PIE and the assistant turn is `English: …` then `Gloss: …`. For eval, score the
`PIE:` line against the reference (with `meta.acceptable` and `meta.token_variants`, as for
`translate_en_pie`) and the `Gloss:` line only where `meta.gloss_reference` is true; the reconstruction
convention of a Tier 1 item is in `meta.style` (the fixed system prompt does not carry it).

**Translator dataset** (`translator/`, `pie.export_chat.build_translator`). For the translation app, which
translates both ways (a user gets a PIE answer, then translates it back to English): every `translate_app`
item emitted twice, once `en_pie` (English in; `PIE:` / `Gloss:` / `Notes:` out) and once `pie_en` (PIE in;
`English:` / `Gloss:` out), the pair sharing `meta.item`. Single requests only (no sessions). The same items
and split as the chat export's translator (`app_chats(..., both_directions=True)`): train items from train
records, eval items from eval records, both directions of an eval item in eval only. The leakage check is
the chat export's, run against the translator's train and the chat train together, and fails the export.
`summary.json` `self_overlap` counts assistant turns only: an `en_pie` output's PIE is the `pie_en` partner's
input, by design. Train the translation model on `translator/train.jsonl`; train the chat model on
`chat/train_mix.jsonl`. As built: train 5,908 examples (2,954 per direction: 1,609 sentence-level and
1,345 short-paragraph items), eval 170 (85 per direction, 84 with a gloss reference; the Tier 1 items have
none).

**Mix.** `summary.json` `mix` groups the kinds: `english_input` (`translate_en_pie`, `translate_app` en_pie,
`app_session`, `en_dialogue`, `demo_chat`), `pie_to_english` (`translate_pie_en`, `translate_app` pie_en),
`pie_only_chat` (`pie_dialogue`, `continuation`) and `grammar` (`gloss`, `inflect`, `paradigm`,
`cognates_to_pie`), with each split's examples, content tokens (Qwen3-4B), shares and the per-example
sampling weight that reaches the target. Every task stays a conversation in `chat/train.jsonl`, so the
grammar tasks are most of its examples; `chat/train_mix.jsonl` keeps every English-input example and
fills the rest in the target proportions (the lowest crc32 of their content; no example repeated), or all a
group has when it is short of its target. The target (`TARGET_MIX`): **50% English input, 10% PIE → English,
15% PIE-only chat, 25% grammar**. PIE → English is kept small for the chat model; the translation app's
both-ways data is the separate `translator/` dataset. As built (the commit is `chat/summary.json`
`provenance`; Tier 3 batches pending re-approval, among them b001-b003 and t3b-002, are out, so train is
smaller for now):

| group | target | `train.jsonl` examples | share | tokens | token share | `train_mix.jsonl` examples | share |
|---|---|---|---|---|---|---|---|
| english_input | 50% | 3,699 | 26.4% | 509,797 | 29.3% | 3,699 | 55.6% |
| pie_to_english | 10% | 1,541 | 11.0% | 268,698 | 15.4% | 740 | 11.1% |
| pie_only_chat | 15% | 360 | 2.6% | 80,850 | 4.6% | 360 | 5.4% |
| grammar | 25% | 8,398 | 60.0% | 880,908 | 50.6% | 1,850 | 27.8% |
| total | | 13,998 | | 1,740,253 | | 6,649 | |

**PIE-only chat is short of its 15% target**: the mix takes all 360 such examples (111 `pie_dialogue`, 249
`continuation`), 5.4% of `train_mix.jsonl`, so English input lands at 55.6% rather than 50%. Doubling every
aligned dialogue into `pie_pie` instead of one in two would still give only about 6%; reaching 15% needs more
dialogue corpus. By tokens, English input is 55.6% of `train_mix.jsonl` (509,797 of 916,536). Of the
conversation and translation examples (all but grammar), English input is 66% in `train.jsonl` and 77% in
`train_mix.jsonl`.

**Multi-turn.** `summary.json` `turns`: user turns per example (1, 2, 3, 4+) per kind and mode, and the
multi-turn examples (two or more user turns) by source: `dialogue` (the exchanges of one dialogue text, each
reply answering what was said: `en_dialogue`, `pie_dialogue`) and `chained` (a user's requests one after
another: `app_session`, `demo_chat`), the latter capped at 10%. As built, `train_mix.jsonl` has 278
multi-turn examples, 4.2% of it: 251 dialogue-derived and 27 chained (9.7% of the multi-turn). Every
multi-turn example of `train.jsonl` is in the mix. The dialogue data is thin: the admitted corpus has 149
aligned dialogues and 111 `pie_pie` conversations, many single-exchange, so conversational multi-turn
cannot be a large share until more dialogue corpus is written.

**Self-overlap.** `summary.json` `self_overlap`: per assistant turn of a dialogue record, the number of
dialogue-mode examples that train on it (cap 3, `DEDUP_CAP`; the tests fail above it); and, reported only,
per PIE sentence and per word 4-gram of every PIE-output kind, the number of train examples whose assistant
turns contain it (a single-sentence record is a `translate_en_pie` output and a translator item, 2 by
design; a short formula that many records share counts once per example).

**Conversational eval.** The dialogue records listed in `data/export/held_dialogues.json` (frozen; its
`rule` documents the choice: the 16 dialogue records of the approved batch t010, quoted exchanges of speeches with 2-5 user turns each)
leave training in `pie.export.build()` (`eval_dialogue_records`, written to `eval_dialogues.jsonl`): no
train record, task, chat example or plain text contains them, and they make no task-benchmark item. In
`chat/eval.jsonl` each is a `pie_dialogue` and an `en_dialogue` in every mode, with `meta.chat_eval: true`.
To measure whether the model can converse in PIE from English input, score the `en_pie` conversations:
replay the user turns with the reference history and compare each assistant turn to the reference PIE
(chrF or word overlap), or judge them; `mixed` and `pie_pie` test the same exchanges from PIE input.
`summary.json` `chat_eval` gives the counts. The translator's eval items (`translate_app` in
`chat/eval.jsonl`) come from the eval records: Tier 1 (no gloss reference) and eval-grade Tier 2.

**Meta flags**: `tier`, `genre`, `meter` (the record's), `accent` (`unresolved` | `representation`, see
"Accent flags"), `coined` (`project` | `neologism`), `neologism: true` (Tier 3b records),
`num_fallback`, `seen_in_train` (eval only: a Tier 1 line Tier 3 reuses verbatim), `style`, `root_id`.
An accent-specified score uses the eval conversations without `meta.accent == "unresolved"`, as with
`eval_tasks_accent_specified.jsonl`.

**Hold-out and leakage.** `chat/eval.jsonl` is exactly the eval task views (Tier 1, eval-grade Tier 2, the
held families' inflection and cognate tasks, plus their paradigms), continuations of eval records, and
the conversational eval's dialogues. The
export fails if an eval source id has any train example (any template), if an eval (user, assistant)
pair or a multi-word eval assistant turn occurs verbatim in train, or if 50% or more of an eval PIE
assistant turn's word 4-grams occur in train (all train messages and `text/train.txt`; field labels
such as `PIE: ` are not words, and n-grams do not cross a line). A translator item is measured on its
`PIE:` line and also fails when that PIE is the whole PIE of a train assistant turn; its inverse mode
outputs English and is exempt from the 4-gram failure, like `translate_pie_en`. Items flagged
`seen_in_train` are reported in `summary.json`, not failed. The per-kind overlap distribution is reported.

**Tier 3b cap.** PLAN.md caps Tier 3b (`neologism: true`, `corpus/tier3b/`) at 10–15% of training tokens.
`pie.export.build` fails when Tier 3b words exceed 15% of the training records' words and reports status
`warn` above 10% (`summary.json` `neologism_share`; the count is `pie.export_chat.neologism_share`, also in
`chat/summary.json` `neologism`). Tier 3b records are training data only; their tasks carry `neologism: true`.
The English-input treatment gives a Tier 3b record more chat examples than its words alone (every mode and
translator item carries `neologism: true`), so `chat/summary.json` also reports the Tier 3b share of the chat
examples (`mix.train.tier3b_example_share`) and of their tokens (`tokens.train_tier3b`); the cap itself stays
the share of training records' words.

**Loading.** Any SFT trainer that reads OpenAI-style `messages` takes the files as they are:

```python
from datasets import load_dataset
# train_mix.jsonl: the chat and translation model's mix; train.jsonl: the full pool (grammar-heavy)
ds = load_dataset("json", data_files={"train": "export/chat/train_mix.jsonl", "eval": "export/chat/eval.jsonl"})
# TRL: SFTTrainer(model, train_dataset=ds["train"].remove_columns("meta"),
#                 args=SFTConfig(assistant_only_loss=True, ...))
```

On Tinker, render each conversation with the model's renderer and train on the assistant tokens (names as in
the tinker-cookbook renderers; check them against your version):

```python
import json
from tinker_cookbook import renderers
renderer = renderers.get_renderer(renderer_name, tokenizer)   # the model's own (e.g. qwen3, Nemotron's)
for line in open("export/chat/train_mix.jsonl"):
    ex = json.loads(line)
    tokens, weights = renderer.build_supervised_example(ex["messages"])   # weights = assistant tokens
```

For the plain text, split `text/train.txt` on blank lines and train with LM loss on every token (a base
checkpoint, or the instruct model before chat SFT). Filter on `meta.task` to train or score one kind, e.g.
`pie_dialogue` + `en_dialogue` + `demo_chat` + `continuation` for speaking PIE (`meta.mode` for
the input language), `translate_app` for the translator, the task kinds for grammar. For the translation app, load
`export/translator/train.jsonl` and `eval.jsonl` the same way.
