# Candidate base models for the training tests (2026-10-30)

These are the downloads and tokenizer checks for arms A, C and D in `docs/NEXT.md` ("Model training tests" and "Before training C and D"). Every directory is named `<model>-<first 8 of commit sha>`, and every download is pinned to that sha. Only safetensors weights, config, tokenizer, generation config, chat template, LICENSE and README were fetched. No shipped code was run, and no file needed `trust_remote_code`. The downloads were anonymous (`token=False`).

## Models

| Arm | Model | Repo | Revision | Local path | Size on disk | Licence | Params | Context | Chat template | Tokens/word (Unicode / ASCII) |
|---|---|---|---|---|---|---|---|---|---|---|
| A (control) | Qwen3-4B-Base | Qwen/Qwen3-4B-Base | 906bfd4b | /Users/david/AI/Qwen3-4B-Base-906bfd4b | 7.5 GB (pre-existing) | Apache 2.0 | 4.02B | 32,768 | n/a | 5.16 / 4.63 |
| A | Qwen3-4B-Instruct-2507 | [Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | cdbee75f17c01a7cc42f958dc650907174af0554 | /Users/david/AI/Qwen3-4B-Instruct-2507-cdbee75f | 7.5 GB | Apache 2.0 (LICENSE included) | 4.022B | 262,144 | yes (in tokenizer_config.json) | 5.16 / 4.63 |
| D | TypewriterLM base-v2 | [typewriter-ai/typewriter-1913-7B-base-v2](https://huggingface.co/typewriter-ai/typewriter-1913-7B-base-v2) | 5a5ec1c056cb14802da0fcc78bad5abb338cd3ae | /Users/david/AI/typewriter-1913-7B-base-v2-5a5ec1c0 | 13 GB | **none published** | 7.242B | 8,192 | no | 7.79 / 5.76 |
| D | TypewriterLM v2-selfinstruct | [typewriter-ai/typewriter-1913-v2-selfinstruct](https://huggingface.co/typewriter-ai/typewriter-1913-v2-selfinstruct) | 55ef3658a8d3c6ec688e2e24c9c378f3d8a97637 | /Users/david/AI/typewriter-1913-v2-selfinstruct-55ef3658 | 13 GB | **none published** | 7.242B | 8,192 | yes (ChatML, chat_template.jinja) | 7.79 / 5.76 |
| D | TypewriterLM v2-sft | [typewriter-ai/typewriter-1913-7B-sft-v2](https://huggingface.co/typewriter-ai/typewriter-1913-7B-sft-v2) | 3fd609e0213722d3d05ee4192bae47992ab96f85 | /Users/david/AI/typewriter-1913-7B-sft-v2-3fd609e0 | 13 GB | **none published** | 7.242B | 8,192 | yes (ChatML, chat_template.jinja) | 7.79 / 5.76 |
| C | talkie-1930-13b-base | [talkie-lm/talkie-1930-13b-base](https://huggingface.co/talkie-lm/talkie-1930-13b-base) | b7c97680791f7fca4262c3c80b36ff7d666faab0 | **not downloaded** (see Blockers) | (53.1 GB `final.ckpt`) | Apache 2.0 | ~13B (40 layers, d=5120) | 4,096 (reference code default) | no | 5.81 / 4.86 |
| C | talkie-1930-13b-it | [talkie-lm/talkie-1930-13b-it](https://huggingface.co/talkie-lm/talkie-1930-13b-it) | 8033675be6360ae0127fa75f941c12d52064f1dc | **not downloaded** (see Blockers) | (26.6 GB `rl-refined.pt`) | Apache 2.0 | ~13B | 4,096 | yes, in code only (`<\|system\|>…<\|end\|><\|user\|>…<\|end\|><\|assistant\|>`) | 5.81 / 4.86 |

Notes on the columns:
- **Params** come from the safetensors headers: the shape products are summed without loading any tensor. Both architectures are stock: Typewriter is `LlamaForCausalLM` / `llama` and Qwen is `Qwen3ForCausalLM`. Neither config has an `auto_map`. **Context** is `max_position_embeddings` from config.json. For Typewriter it matches the paper's 8,192.
- **Tokens/word** is the token count for the whole of `export/text/train.txt` or `export/text-ascii/train.txt`, divided by the whitespace-word count (68,409 words), with `add_special_tokens=False`. The method was calibrated on the existing Qwen3-4B-Base tokenizer.json, where it reproduces 5.16 / 4.63 exactly. The three Typewriter tokenizers give identical counts; the chat variants add only the ChatML special tokens. Counted line by line, which drops the newline tokens, Typewriter gives 7.70 / 5.68.
- **talkie tokens/word** was measured with tiktoken. The encoder was rebuilt from data only: the repo's base64 `vocab.txt`, which is byte-identical in base and it, plus the split regex copied as a string from `talkie-lm/talkie` `src/talkie/tokenizer.py`. No talkie code was imported. There is no tokenizer.json to load with `tokenizers`.

## Choices
- **Qwen: Qwen3-4B-Instruct-2507** is the newest official text-only 4B instruct release (Aug 2025). It shares the architecture and tokenizer of the Base model we already hold, so arm A is a clean comparison of instruct against base. The tokens/word are identical to Base. `Qwen/Qwen3.5-4B` (Feb 2026) is newer, but it is a different family (`qwen3_5`, image-text-to-text) with its own base model, so it would not pair with the Qwen3-4B-Base control. `Qwen/Qwen3-4B` is the older hybrid-thinking release.
- **TypewriterLM**: the three repos downloaded are exactly the ones the paper's model table names (arXiv 2606.02991v2, appendix: base-v2, v2-selfinstruct, v2-sft). The paper's footnote also links the org, https://huggingface.co/typewriter-ai. These were also in the official org but **not downloaded**:
  - `typewriter-1913-7B-dpo-v2` (3cdda5f7) is not cited in the paper and has no model card.
  - `typewriter-1913-7B-base` (v1) was superseded by base-v2.
  - `typewriter-1938-7B-instruct` and `typewriter-1938-3B-EN-DE-base` have the wrong cutoff.
- **talkie**: the paper's model table and the talkie README both confirm `talkie-lm/talkie-1930-13b-base` and `-it` as the official repos. The many HF-format conversions (lewtun/…, Abstract4700/…, the MLX, GGUF and GPTQ builds) are third-party re-uploads, most tagged `custom_code`, so none were used.

## Blockers
1. **talkie: no safetensors, and custom code is needed.** Each official repo holds only one PyTorch pickle (`final.ckpt` 53.1 GB in base, `rl-refined.pt` 26.6 GB in it) plus `vocab.txt`. There is no config.json and no tokenizer.json. The reference loader does a plain `torch.load` (pickle, so arbitrary code execution) into a custom GPT class (`ActGain` residual gains, separate `lm_head`, tiktoken tokenizer, 65,536 + 4 special tokens). Transformers has no matching architecture. Using it means one of the following, which is David's call:
   - (a) convert it yourself, in a sandbox, with `torch.load(weights_only=True)`, then a safetensors export and a hand-written HF or MLX model class;
   - (b) review and pick one of the third-party conversions;
   - (c) ask talkie-lm for safetensors.

   Nothing was downloaded except README.md and vocab.txt, which went to the scratch cache.
2. **TypewriterLM: no licence.** None of the typewriter-ai repos has a LICENSE file, a README/model card, or licence metadata. The org page states no terms either. The CC BY 4.0 on arXiv covers the paper, not the weights. The paper says "we openly release TypewriterLM", but with no licence, permission to fine-tune and to run a public demo is **not confirmed**. Ask the authors (Luo, Shinnick, … Lu) before a public demo.
3. **TypewriterLM tokenizer splits PIE into bytes**, as NEXT.md feared. It is a 32k BPE trained on pre-1913 text, and subscript laryngeals, ʰ, macrons and syllabic-ring characters fall back to UTF-8 bytes: `h₁` → `h`+3 byte tokens, `ʰ` → 2, `ē` → 2, `n̥` → `n`+2. The result is 7.79 tokens/word on Unicode, against 5.16 for Qwen. The ASCII export (5.76) is much closer, so **arm D should probably train on the ASCII form**. Alternatively, add tokens for the PIE characters and train the embeddings, as the authors already did for ChatML. talkie's 65k tokenizer does better (5.81 / 4.86) but is still worse than Qwen.
4. Tinker support for C and D was not checked; that was out of scope here.
