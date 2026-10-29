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

## Corpus and tooling (queued 2026-10-29)
- **More conversational corpus.** The owner wants a living language you can converse with, so plan more multi-turn dialogue batches in Tier 3 (wave 2, t034–t083, is still parked) and Tier 3b.
- **Slice gaps for Tier 3b:** bread, milk, hungry, angry, story, tomorrow, and the verbs pr̥sḱéti "ask/please" and wéḱti "wish". The brief's please/sorry idioms need them.
- **`realize_plans.py` should reject held-out root families** (`eval_root`) in plans. Today a held-out root can enter training unnoticed (t3b-001 0019 used h₁éwHt).
- **Glosses for the translator app** use internal labels (`personal/2-ACC.SG.ENCL`, `demonstrative_so-ACC.SG`). Map them to readable English glosses.
- **Compound engine:** a determinative prefix compound such as h₂énti- "counter-" for the "answer" coinage (h₂entiwékʷos).
- **t3b-001** predates the v2 rules (per-sentence English, the coined-sentence gate). Re-plan it under v2 if it is ever re-realized.
- **From the t3b-002 review:**
  - closed:demonstrative_so has no DAT/INS/GEN dual (the dual falls back to the plural).
  - The `words_per_sentence` metric equals `words_per_record`, which is a bug.
  - Two 'give' aorists (déh₃t, déh₃ut) both enter the chat data; pick one.
  - The 6-use cap blocks natural fixes for everyday words in Tier 3b.
  - Brief-3b §3 "Welcome, guest" idiom puts the model in a house, contradicting §5's "no home". Restrict it to the user's lines.

## Hold-out (redrawn 2026-10-29: 5f2239c, 1a2cb6a)
- 821 families are protected now (Swadesh-207, Leipzig–Jakarta, a conversational core); 81 core families that were held before are trainable (help, drink, hear, sit, water, day, think, …).
- **Owner's call:** some families are still held but arguably everyday: mneh₂- 'remind', h₃neh₂- 'enjoy', h₁rey- 'rise', prep- 'appear', ḱenk- 'hang', treH- 'protect', h₂ens- 'give birth', melkʷ- 'fall silent'. Protecting them needs another redraw (cheap until scores exist).
- Offer `pie-lex-h1ewHt` 'help' in Tier 3b slices (`TIER3B_INHERITED`) now that it is trainable.
- wait, thank, answer, today and tomorrow have no trusted gloss in the lexicon, so the concept list can't protect them. They need glosses or coinages.
