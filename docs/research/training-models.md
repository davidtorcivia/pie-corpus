# Candidate base models for the training tests (2026-10-30)

These are the downloads and tokenizer checks for arms A, C and D in `docs/NEXT.md` ("Model training tests" and "Before training C and D"). Every directory is named `<model>-<first 8 of commit sha>`, and every download is pinned to that sha. Only safetensors weights, config, tokenizer, generation config, chat template, LICENSE and README were fetched. No shipped code was run, and no file needed `trust_remote_code`. The downloads were anonymous (`token=False`). The exception is talkie: its official repos hold only PyTorch pickle checkpoints, so those were fetched (without `token=False`) and loaded with `weights_only=True` only. See "talkie conversion".

## Models

| Arm | Model | Repo | Revision | Local path | Size on disk | Licence | Params | Context | Chat template | Tokens/word (Unicode / ASCII) |
|---|---|---|---|---|---|---|---|---|---|---|
| A (control) | Qwen3-4B-Base | Qwen/Qwen3-4B-Base | 906bfd4b | /Users/david/AI/Qwen3-4B-Base-906bfd4b | 7.5 GB (pre-existing) | Apache 2.0 | 4.02B | 32,768 | n/a | 5.16 / 4.63 |
| A | Qwen3-4B-Instruct-2507 | [Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) | cdbee75f17c01a7cc42f958dc650907174af0554 | /Users/david/AI/Qwen3-4B-Instruct-2507-cdbee75f | 7.5 GB | Apache 2.0 (LICENSE included) | 4.022B | 262,144 | yes (in tokenizer_config.json) | 5.16 / 4.63 |
| D | TypewriterLM base-v2 | [typewriter-ai/typewriter-1913-7B-base-v2](https://huggingface.co/typewriter-ai/typewriter-1913-7B-base-v2) | 5a5ec1c056cb14802da0fcc78bad5abb338cd3ae | /Users/david/AI/typewriter-1913-7B-base-v2-5a5ec1c0 | 13 GB | **none published** | 7.242B | 8,192 | no | 7.79 / 5.76 |
| D | TypewriterLM v2-selfinstruct | [typewriter-ai/typewriter-1913-v2-selfinstruct](https://huggingface.co/typewriter-ai/typewriter-1913-v2-selfinstruct) | 55ef3658a8d3c6ec688e2e24c9c378f3d8a97637 | /Users/david/AI/typewriter-1913-v2-selfinstruct-55ef3658 | 13 GB | **none published** | 7.242B | 8,192 | yes (ChatML, chat_template.jinja) | 7.79 / 5.76 |
| D | TypewriterLM v2-sft | [typewriter-ai/typewriter-1913-7B-sft-v2](https://huggingface.co/typewriter-ai/typewriter-1913-7B-sft-v2) | 3fd609e0213722d3d05ee4192bae47992ab96f85 | /Users/david/AI/typewriter-1913-7B-sft-v2-3fd609e0 | 13 GB | **none published** | 7.242B | 8,192 | yes (ChatML, chat_template.jinja) | 7.79 / 5.76 |
| C | talkie-1930-13b-base | [talkie-lm/talkie-1930-13b-base](https://huggingface.co/talkie-lm/talkie-1930-13b-base) | b7c97680791f7fca4262c3c80b36ff7d666faab0 | /Users/david/AI/talkie-13B-b7c97680 (original `final.ckpt`; safe copy in `safetensors/`) | 53.1 GB ckpt + 49 GiB safetensors (fp32) | Apache 2.0 | 13.280B | 4,096 (reference code default) | no | 5.81 / 4.86 |
| C | talkie-1930-13b-it | [talkie-lm/talkie-1930-13b-it](https://huggingface.co/talkie-lm/talkie-1930-13b-it) | 8033675be6360ae0127fa75f941c12d52064f1dc | /Users/david/AI/talkie-13B-chat-8033675b (original `rl-refined.pt`; safe copy in `safetensors/`) | 26.6 GB ckpt + 25 GiB safetensors (bf16) | Apache 2.0 | 13.280B | 4,096 (SFT/RL used max_length 2,048) | yes, `chat_template.jinja` written from `chat.py`: `<\|system\|>…<\|end\|><\|user\|>…<\|end\|><\|assistant\|>` | 5.81 / 4.86 |

Notes on the columns:
- **Params** come from the safetensors headers: the shape products are summed without loading any tensor. Both architectures are stock: Typewriter is `LlamaForCausalLM` / `llama` and Qwen is `Qwen3ForCausalLM`. Neither config has an `auto_map`. **Context** is `max_position_embeddings` from config.json. For Typewriter it matches the paper's 8,192.
- **Tokens/word** is the token count for the whole of `export/text/train.txt` or `export/text-ascii/train.txt`, divided by the whitespace-word count (68,409 words), with `add_special_tokens=False`. The method was calibrated on the existing Qwen3-4B-Base tokenizer.json, where it reproduces 5.16 / 4.63 exactly. The three Typewriter tokenizers give identical counts; the chat variants add only the ChatML special tokens. Counted line by line, which drops the newline tokens, Typewriter gives 7.70 / 5.68.
- **talkie tokens/word** was first measured with tiktoken, rebuilt from data only: the repo's base64 `vocab.txt`, which is byte-identical in base and it, plus the split regex copied as a string from `talkie-lm/talkie` `src/talkie/tokenizer.py`. No talkie code was imported. It has since been re-measured with the converted `tokenizer.json` (see "talkie conversion"), using the same method. The counts are 397,575 and 332,591 tokens over 68,409 words, so again 5.81 / 4.86.

## Choices
- **Qwen: Qwen3-4B-Instruct-2507** is the newest official text-only 4B instruct release (Aug 2025). It shares the architecture and tokenizer of the Base model we already hold, so arm A is a clean comparison of instruct against base. The tokens/word are identical to Base. `Qwen/Qwen3.5-4B` (Feb 2026) is newer, but it is a different family (`qwen3_5`, image-text-to-text) with its own base model, so it would not pair with the Qwen3-4B-Base control. `Qwen/Qwen3-4B` is the older hybrid-thinking release.
- **TypewriterLM**: the three repos downloaded are exactly the ones the paper's model table names (arXiv 2606.02991v2, appendix: base-v2, v2-selfinstruct, v2-sft). The paper's footnote also links the org, https://huggingface.co/typewriter-ai. These were also in the official org but **not downloaded**:
  - `typewriter-1913-7B-dpo-v2` (3cdda5f7) is not cited in the paper and has no model card.
  - `typewriter-1913-7B-base` (v1) was superseded by base-v2.
  - `typewriter-1938-7B-instruct` and `typewriter-1938-3B-EN-DE-base` have the wrong cutoff.
- **talkie**: the paper's model table and the talkie README both confirm `talkie-lm/talkie-1930-13b-base` and `-it` as the official repos. The many HF-format conversions (lewtun/…, Abstract4700/…, the MLX, GGUF and GPTQ builds) are third-party re-uploads, most tagged `custom_code`, so none were used.

## Blockers
1. **talkie: resolved with our own model code.** No standard Hugging Face class fits talkie exactly, so there is no config.json and no `from_pretrained`. We now have exact PyTorch and MLX ports in `training/talkie/` (`modeling_talkie.py`, `mlx_talkie.py`). They load the converted safetensors, and their projections are named so that peft and MLX LoRA can target them. The verification numbers are in `training/talkie/README.md`. MLX LoRA on the it model runs at about 335 tok/s with a 5×1024 batch.

2. **TypewriterLM: no licence.** None of the typewriter-ai repos has a LICENSE file, a README/model card, or licence metadata. The org page states no terms either. The CC BY 4.0 on arXiv covers the paper, not the weights. The paper says "we openly release TypewriterLM", but with no licence, permission to fine-tune and to run a public demo is **not confirmed**. Ask the authors (Luo, Shinnick, … Lu) before a public demo.
3. **TypewriterLM tokenizer splits PIE into bytes**, as NEXT.md feared. It is a 32k BPE trained on pre-1913 text, and subscript laryngeals, ʰ, macrons and syllabic-ring characters fall back to UTF-8 bytes: `h₁` → `h`+3 byte tokens, `ʰ` → 2, `ē` → 2, `n̥` → `n`+2. The result is 7.79 tokens/word on Unicode, against 5.16 for Qwen. The ASCII export (5.76) is much closer, so **arm D should probably train on the ASCII form**. Alternatively, add tokens for the PIE characters and train the embeddings, as the authors already did for ChatML. talkie's 65k tokenizer does better (5.81 / 4.86) but is still worse than Qwen.
4. Tinker support for C and D was not checked; that was out of scope here.

## talkie conversion (2026-10-30)
**What was fetched.** The checkpoints were downloaded with `huggingface_hub.snapshot_download`, pinned to the shas in the table, into `/Users/david/AI/talkie-13B-b7c97680` and `/Users/david/AI/talkie-13B-chat-8033675b`. Both sha256 values match the Hub LFS metadata:
- `final.ckpt`: `caa3c169…2061b6f9f`
- `rl-refined.pt`: `c6fd903b…694e70064`

The reference code was cloned **as text only** from github.com/talkie-lm/talkie at commit `35317ba3a84861a84c84065bd73faf88ad19329c`, into `/Users/david/AI/talkie-code-35317ba3`. The HF repos hold no code. None of it was imported or run.

**How it was loaded.** All work ran from the scratch directory `/Users/david/AI/talkie-work`, using a fresh uv venv there (torch 2.15.0, transformers 5.22.1), with `python -I`. Both checkpoints loaded with `torch.load(path, weights_only=True, map_location="cpu", mmap=True)`. Nothing was refused.
- Base: `{"model": state_dict}`, 443 tensors, all fp32, vocab 65,536.
- it: `{"model_state_dict", "config", "metadata"}`, 443 tensors, all bf16, vocab **65,540**. The 4 chat-token rows are trained, so the reference code's random re-initialization of them never fires. `metadata` holds only the RL run config: step 1070, max_length 2048, lr 3e-6.

**What was written.** `<dir>/safetensors/` in each directory holds:
- the weights as sharded safetensors under the **original talkie parameter names**, with no renaming, folding or dtype change, and a `model.safetensors.index.json`. Base is 10 × ≤5 GiB fp32 shards; it is 5 shards in bf16. Every tensor was re-read and checked with `torch.equal` against the checkpoint: 443/443 identical in both.
- `tokenizer.json` and `tokenizer_config.json`, built with `TikTokenConverter` from `vocab.txt`. Ranks ≥ 65,535 were dropped, as `tokenizer.py` does (the file has 262,144 lines). The special tokens are:
  - base: `<|endoftext|>` = 65535;
  - it: also `<|end|>`, `<|user|>`, `<|assistant|>`, `<|system|>` = 65536–65539, with eos `<|end|>` and `chat_template.jinja`.

  Ids are identical to the tiktoken encoder on the whole of both train.txt files and on 11,862 single lines. The one deliberate difference is that a literal `<|endoftext|>` in input text is parsed as the special token, which is standard HF behaviour.
- it only: `talkie_ckpt_config.json`, holding the checkpoint's own dims dict.

**Architecture** (from `model.py` plus the tensor shapes): a 40-layer decoder with d=5120 and 40 heads × 128, full MHA. SwiGLU MLP with 13,696 hidden units, no biases, untied `lm_head`. RoPE with θ=1e6 and cos/sin precomputed in bf16. All RMSNorms are weightless (`F.rms_norm`, default eps). Closest standard class: Qwen3 (qk-norm, SwiGLU, untied head).

These parts **fold exactly into Qwen3 weights**:
- the scalar `attn_gain`, `mlp_gain` and `lm_head_gain` (into o_proj, down_proj and lm_head);
- the RMSNorm applied after the embedding (pre-normalize the embedding rows);
- the weightless norms (weight = 1);
- post-RoPE qk-norm, which commutes with RoPE;
- the opposite RoPE rotation direction, fixed by negating the second-half rows of each head in q/k. This was checked numerically in float64: talkie's q·k equals HF rotate_half q·k with the halves negated, for all position pairs 0–7, with max difference 0. The other folds are derived algebraically; they have not yet been tested in a built model.

These parts **do not fold into any standard class**, and the trained values are far from neutral:
1. `embed_skip`: every block adds `a·rmsnorm(embed(x))` back into the residual stream. The values range up to |0.73|; layers 0–2 are about −0.40/−0.35/−0.26 and layers 31–38 are 0.15–0.59 or −0.73.
2. `head_gain`: a learned **per-head** scalar on the unit-RMS query, i.e. a per-head attention temperature. Within a layer it spans roughly 0.5–3.7, with std 0.2–0.6. Qwen3's `q_norm.weight` is per-channel and shared across heads, so it cannot express this.

Following the brief, no HF config or model class was invented, and so `mlx_lm.convert` (which needs a supported architecture) was not run.

**Verification** used an independent ~50-line forward pass, `/Users/david/AI/talkie-work/reimpl.py`, written from `model.py` read as text, running on the safetensors with the tokenizer.json. bf16 on MPS took about 0.15–0.5 s per token without a KV cache.
- Base, README prompts: *"The effects of the automobile on public morality have"* → " been much discussed. It is said by many that there are more people in jails and reformatories than there were before the automobile became so popular…". *"If scientists discover life on other planets,"* gave 1920s newspaper-column squibs about sugar prices, gasoline and Sunday theatres, with an authentic OCR "1t".
- it, README prompts: "Write an essay predicting… 1960" → "the earth will have a population of 5,000,000,000 … The air will be everywhere traversed by ships and by flying-machines. There will be no more war…". "Causes of the French Revolution" → feudal abuses, taxation and the clergy, then Jansenists and Jesuits. Both ran to the 150-token cap without emitting `<|end|>`, and both were coherent pre-1931 English.
- Gettysburg Address (103 tokens), NLL/token:

  | | fp32 CPU | bf16 MPS | bf16, RoPE sign flipped |
  |---|---|---|---|
  | base | 0.235 | 0.235 | 3.46 |
  | it | 0.301 | 0.320 | 2.62 |

  The flipped-RoPE column confirms the rotation direction. Max |Δlogit| between bf16 and fp32 is 1.7 (base) and 2.3 (it), which is ordinary bf16 drift over 40 layers. Norm eps barely matters: the default eps (the fp32 eps, 1.19e-7, which `F.rms_norm` also uses for bf16 input) and 1e-6 differ by ≤0.01 NLL. This corrects an earlier label in losstest.py, which called it finfo(bf16). Using the real finfo(bf16) of 2⁻⁷ breaks the model, because the embedding rows have RMS ≈ 0.012.
- There is no converted HF model to diff against, so the HF-versus-reimplementation logit comparison was not possible. The reference code itself was deliberately not run.

**Scripts** (scratch, not in repo): all in `/Users/david/AI/talkie-work/`:
- `dl.py` downloads the checkpoints;
- `inspect_ckpt.py` lists tensors and gains;
- `convert_raw.py` writes and verifies the safetensors;
- `tok.py` builds and verifies the tokenizer;
- `reimpl.py`, `gen.py` and `losstest.py` run the verification.

**Follow-up (same day):** David chose an exact custom module over an approximation, so it was written in `training/talkie/`; see its README. Nothing was folded or approximated.

## Training speed (2026-10-30)

LoRA rank 16 on every linear layer, packed 2048-token rows of `export/chat/train_mix.jsonl` (2.27 M tokens per
epoch), `training/bench_lora.py`.

| machine | model | setup | tokens/s | memory | one epoch |
|---|---|---|---|---|---|
| tr-desktop, RTX 5090, Windows | Qwen3-4B-Instruct | bf16 LoRA, cuDNN attention, Liger kernels, grad checkpointing, batch 4 | **4,302** | 11.2 GB | ~9 min |
| tr-desktop | Qwen3-4B-Instruct | same, batch 8 / 16 | 4,139 / 4,215 | 14.5 / 21.0 GB | ~9 min |
| tr-desktop | Qwen3-4B-Instruct | bf16 LoRA, default attention, no Liger, batch 4 | 1,681 | 23.3 GB | ~23 min |
| Mac Studio M3 Ultra, MLX | Qwen3-4B-Base | bare forward+backward ceiling (packed) | ~850–930 | — | ~45 min |
| Mac Studio, MLX | Qwen3-4B-Base | stock `mlx_lm lora` (pads, short examples) | 140–230 real | 28–148 GB | ~3 h |
| Mac Studio, MLX | talkie-13B chat | LoRA rank 8, packed 1024 | 335 | 108 GB | ~1.9 h |

What made the 5090 fast, in order:
1. `model.train()` after `get_peft_model`: from_pretrained returns eval mode, where gradient checkpointing is off;
   one 2048-token row then held 37 GB of activations and Windows silently spilled past the card into system RAM.
2. A VRAM cap (`torch.cuda.set_per_process_memory_fraction(0.92)`) so anything too big fails with OOM instead of
   spilling (the spill is Windows' sysmem fallback; it made the first attempt crawl).
3. cuDNN attention: torch 2.11 on Windows has no flash or memory-efficient SDPA kernel for the 5090; the math
   fallback materializes every attention matrix (47.6 ms and 8.6 GB per call vs 8.1 ms and 0.8 GB for cuDNN).
4. Liger kernels (triton-windows + liger-kernel --no-deps): fused linear cross-entropy never builds the 152k-vocab
   logits (9.3 GB at batch 8 x 2048), plus fused RMSNorm, SwiGLU and RoPE.
QLoRA (4-bit) brings no speed for a 4B model; it matters for talkie-13B (26 GB of bf16 weights) on the 32 GB card.
