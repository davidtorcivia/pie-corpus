# Next steps (handoff list, started 2026-10-29)

This file is finished at the end of the session, with everything left over from the work in progress.

## Model training tests (owner, 2026-10-29)

Every arm uses the same export and the same tests:
- the chat model trains on `export/chat/train_mix.jsonl`, the translator on `export/translator/`;
- the conversational test is the reserved t010 dialogues, with English input;
- the translator test is the `translate_app` eval items;
- the benchmark is paradigm, cognate→PIE and chrF.

| Arm | Model | Where | Notes |
|---|---|---|---|
| A | Qwen ~4B instruct, LoRA | local (M3 Ultra) | fast iteration; also a base-model control |
| B | Nemotron 3.5 122B MoE instruct, LoRA | Tinker | the demo model; no base checkpoint exists |
| C | **talkie-13B** (pre-1931 English, Apache 2.0) | local LoRA | "ignorant of the modern world". Try the base model and the chat variant; the chat variant's post-training used synthetic Claude chats, so it is less purely vintage |
| D | **TypewriterLM 7.2B** (pre-1913 English, arXiv 2606.02991) | local LoRA | check the license and the released chat/instruction data |

Before training C and D:
- Measure tokens per word on our PIE (Unicode and ASCII), as was done for Qwen3-4B (5.1 / 4.6). An old-text tokenizer may split PIE characters into bytes.
- Confirm that the weights and license allow fine-tuning and a public demo.
- Check whether Tinker supports C or D as a base model; otherwise train them locally.

Judge "a living language you can converse with", not a talking dictionary: use the conversational eval plus a human read of multi-turn exchanges.
