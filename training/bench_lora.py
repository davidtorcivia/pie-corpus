"""LoRA / QLoRA training-speed benchmark on the chat mix, packed (CUDA or CPU torch; plain transformers + peft).

    python bench_lora.py MODEL_DIR DATA_JSONL --quant {bf16,4bit} --batch 8 --seq 2048 [--gc] [--steps 12]

Every example is rendered with the model's own chat template, the token streams are concatenated and cut into
--seq-long rows (packing: no padding, the way a real run would train), and LoRA rank 16 adapts every linear layer.
Prints tokens/s over the steps after 3 warm-up steps, and peak GPU memory.
"""
import argparse
import json
import time

import torch
from torch.nn.attention import SDPBackend, sdpa_kernel
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


def packed_rows(tok, path: str, seq: int, need: int) -> torch.Tensor:
    ids: list[int] = []
    for line in open(path, encoding="utf-8"):
        msgs = json.loads(line)["messages"]
        out = tok.apply_chat_template(msgs, tokenize=True)
        ids += list(out["input_ids"] if hasattr(out, "keys") else out) + [tok.eos_token_id]   # transformers 5: a dict
        if len(ids) >= seq * need:
            break
    n = len(ids) // seq
    return torch.tensor(ids[: n * seq]).view(n, seq)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"), ap.add_argument("data")
    ap.add_argument("--quant", choices=("bf16", "4bit"), default="bf16")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--seq", type=int, default=2048)
    ap.add_argument("--gc", action="store_true", help="gradient checkpointing")
    ap.add_argument("--steps", type=int, default=12)
    ap.add_argument("--liger", action="store_true",
                    help="Liger kernels (Qwen3): fused linear cross-entropy never materializes the 152k-vocab logits")
    ap.add_argument("--vram-frac", type=float, default=0.92,
                    help="cap on the GPU memory torch may use: past it a run fails with OOM instead of spilling into "
                         "system RAM (Windows' sysmem fallback, which made a first run crawl)")
    a = ap.parse_args()
    torch.cuda.set_per_process_memory_fraction(a.vram_frac, 0)
    if a.liger:
        from liger_kernel.transformers import apply_liger_kernel_to_qwen3
        apply_liger_kernel_to_qwen3(rope=True, rms_norm=True, swiglu=True, fused_linear_cross_entropy=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    q = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                           bnb_4bit_use_double_quant=True) if a.quant == "4bit" else None
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, quantization_config=q,
                                                 attn_implementation="sdpa", device_map={"": 0})
    if a.gc:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, target_modules="all-linear", task_type="CAUSAL_LM"))
    model.train()      # from_pretrained returns eval mode, where gradient checkpointing is off (37 GB of activations)
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-4)
    rows = packed_rows(tok, a.data, a.seq, a.batch * a.steps)
    torch.cuda.reset_peak_memory_stats()
    done, t0 = 0, None
    for step in range(a.steps):
        x = rows[(step * a.batch) % len(rows):][: a.batch].cuda()
        try:
            # cuDNN attention: on Windows torch 2.11 has no flash / mem-efficient SDPA kernel for the 5090, and the math
            # fallback materializes every attention matrix (6x slower, 10x the memory)
            with sdpa_kernel([SDPBackend.CUDNN_ATTENTION, SDPBackend.FLASH_ATTENTION, SDPBackend.EFFICIENT_ATTENTION]):
                loss = model(input_ids=x, labels=x).loss
                loss.backward()
        except torch.OutOfMemoryError as e:
            print(json.dumps({"model": a.model, "quant": a.quant, "batch": a.batch, "seq": a.seq, "gc": a.gc,
                              "oom": str(e)[:300]}))
            return
        opt.step(), opt.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        if step == 2:
            t0 = time.time()
        elif step > 2:
            done += x.numel()
    dt = time.time() - t0
    print(json.dumps({"model": a.model.rstrip("\\/").split("\\")[-1].split("/")[-1], "quant": a.quant,
                      "batch": a.batch, "seq": a.seq, "gc": a.gc, "liger": a.liger, "tok_per_s": round(done / dt),
                      "peak_gb": round(torch.cuda.max_memory_allocated() / 2**30, 1), "loss": round(loss.item(), 3)}))


if __name__ == "__main__":
    main()
