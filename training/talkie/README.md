# talkie-1930-13b: our own PyTorch and MLX ports

These are small implementations of talkie (pre-1931 English, Apache 2.0) that load the safetensors converted from the official pickle checkpoints. The talkie reference code (github.com/talkie-lm/talkie @ 35317ba3) was only **read as text**, never imported or run. See `docs/research/training-models.md` ("talkie conversion") for how the downloads and the conversion were done.

| Model | Weights (original talkie tensor names) | dtype | vocab |
|---|---|---|---|
| base | `/Users/david/AI/talkie-13B-b7c97680/safetensors/` | fp32 | 65,536 |
| it (chat) | `/Users/david/AI/talkie-13B-chat-8033675b/safetensors/` | bf16 | 65,540 (+ `<\|end\|> <\|user\|> <\|assistant\|> <\|system\|>`) |

Each directory also holds `tokenizer.json` and `tokenizer_config.json`; the it directory adds `chat_template.jinja`. The chat format is `<|system|>…<|end|><|user|>…<|end|><|assistant|>…<|end|>`, and eos is `<|end|>`.

## Files
- `modeling_talkie.py`: a plain-torch `TalkieForCausalLM` with `load_talkie(dir, dtype, device)` and greedy/sampled `generate` with a KV cache.
- `mlx_talkie.py`: the same model in MLX, with `load_talkie(dir)` (bf16) and greedy `generate`.
- `reference_forward.py`: an independent functional forward pass, used only for cross-checking.
- `verify.py`: logit and generation checks. `lora_smoke.py`: the MLX LoRA smoke test.

Run everything with the scratch venv (`/Users/david/AI/talkie-work/.venv`) and `python -I`.

```python
import sys; sys.path.insert(0, "/Users/david/AI/PIE/training/talkie")
from transformers import PreTrainedTokenizerFast
D = "/Users/david/AI/talkie-13B-chat-8033675b/safetensors"
tok = PreTrainedTokenizerFast.from_pretrained(D)

# PyTorch (peft LoRA: target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"])
import torch, modeling_talkie as mt
model = mt.load_talkie(D, dtype=torch.bfloat16, device="mps")

# MLX (wrap the same names with mlx_lm.tuner.lora.LoRALinear.from_base; blocks are model.layers)
import mlx_talkie
model = mlx_talkie.load_talkie(D)
ids = tok.apply_chat_template([{"role": "user", "content": "Hello"}], add_generation_prompt=True)["input_ids"]
print(tok.decode(model.generate(ids, 100, stop_ids={65535, 65536})))
```

## Architecture and how it differs from Qwen3
talkie has 40 layers, d=5120, and 40 heads × 128 with full MHA (no GQA). The MLP is SwiGLU with 13,696 hidden units. There are no biases, the LM head is untied, and RoPE uses θ=1e6. It differs from Qwen3 as follows:
1. **Every RMSNorm is weightless.** That includes the pre-attention and pre-MLP norms, the final norm and the qk-norm. Each is `F.rms_norm` with the default eps, which is the fp32 machine eps (1.19e-7) even for bf16 input. It is not finfo(bf16), and the MLX port has to set this explicitly.
2. **The token embedding is RMS-normalised** before the first layer.
3. **Embedding add-back:** after every block, `x += embed_skip[l] · e`, where `e` is the normalised embedding. The trained values reach about |0.73|.
4. **Learned scalar gains:** `attn_gain[l]` scales the attention output and `mlp_gain[l]` scales the MLP output before each residual add. `lm_head_gain` scales the LM-head weight (≈3.88).
5. **qk-norm after RoPE** (Qwen3 applies it before), followed by a **learned per-head query scale** `head_g[l, h]`, which spans 0.5–3.7 within a layer. In effect this is a per-head attention temperature, and Qwen3's shared per-channel `q_norm.weight` cannot express it.
6. **RoPE rotates the other way:** `y1 = x1·cos + x2·sin`, `y2 = −x1·sin + x2·cos`. The cos/sin tables are rounded to bf16, as in the reference.

None of these are folded away. The gains are kept as their own parameters, so the ported model is the original function.

## Verification (2026-10-30, M-series Mac, torch 2.15.0, mlx 0.32.4)
**(a) Torch module vs `reference_forward.py`, fp32 CPU.** Max |Δlogit| is **0.0** on all 6 inputs: the Gettysburg Address (103 tokens) and the two README prompts, for both models. The README prompts go through the chat template for the it model. Both files were written by the same author from the same reading of `model.py`. Before them, the reference pass was checked against the real model: coherent generations, and Gettysburg NLL 0.235 (base) / 0.301 (it), against 3.5 / 2.6 with the RoPE sign flipped.

**(b) MLX bf16 vs torch fp32:**

| Model | Max \|Δlogit\| | Mean \|Δlogit\| | Top-1 agreement | Gettysburg NLL (fp32 → MLX bf16) |
|---|---|---|---|---|
| base | 0.65–1.49 | 0.04 | 0.88–1.00 | 0.235 → 0.236 |
| it | 2.3–5.7 | 0.05–0.15 | 0.92–0.98 | 0.301 → 0.321 |

The it model's maximum comes from a 20-token chat prompt. The bf16 drift is the same size as torch bf16 against fp32 (max 1.7 for base, 2.3 for it on Gettysburg).

**(c) Greedy generation, 80 tokens.**
- Torch bf16 on MPS, with the KV cache, takes about 4.5 s. A cached decode reproduces an uncached forward's argmax on 100% / 100% / 100% / 97.5% of tokens; the misses are bf16 near-ties.
- MLX takes about 3.4 s.
- Both give coherent period English. it: *"The causes of the French Revolution may be referred to three principal sources: first, the abuses of the feudal system; secondly, the oppression of the people by taxation; and, thirdly, the spread of infidelity…"*, the same in torch and MLX. Base: *"…have been discussed by many writers. The automobile has been blamed for the increase in the number of divorces, for the increase in the number of suicides…"*. Greedy decoding is repetitive, as usual for a base model, and MLX and torch match.

**(d) MLX LoRA smoke test**, run as `lora_smoke.py <it dir> export/chat/train_mix.jsonl 32 10`.
- Setup: the first 32 examples rendered with the chat template. Loss covers assistant tokens only (1,752 supervised). Packed into a batch of **5 × 1024**. Rank-8 LoRA (scale 2) on all 7 projections × 40 layers is 31.2M trainable params, trained with Adam at 2e-4.
- Loss by step: 4.00, 3.21, 2.69, 2.32, **6.45**, 2.09, 2.13, 1.79, 1.32, 0.83. The loss falls overall, but a single-step spike at step 5 suggests the learning rate is on the high side for real runs.
- Throughput: **335 tokens/s** (15.3 s per step), with 108 GB peak memory and no gradient checkpointing.
