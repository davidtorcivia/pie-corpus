"""Generate a saved adapter's answers to a frozen prompt set (the before/after comparison across exports).

    python gen_eval.py --model DIR --adapter RUNS/RUN/adapter-e2 --template chatml --out RUNS/RUN/generations-v1-e2.jsonl
        [--prompts Q:\\AI\\PIE\\data\\gen_prompts_v1.jsonl]

Same decoding as train_lora.py's per-epoch samples (greedy, repetition penalty 1.1, batched with left padding).
"""
import argparse
import json
from pathlib import Path

import torch
from peft import PeftModel
from torch.nn.attention import sdpa_kernel
from transformers import AutoModelForCausalLM, AutoTokenizer

from train_lora import ATTN, TEMPLATES, load_jsonl, prompt_ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--template", choices=TEMPLATES, required=True)
    ap.add_argument("--prompts", default=r"Q:\AI\PIE\data\gen_prompts_v1.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--max-new", type=int, default=160)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, attn_implementation="sdpa",
                                                 device_map={"": 0})
    model = PeftModel.from_pretrained(model, a.adapter).eval()
    gens = load_jsonl(a.prompts)
    end = tok.eos_token_id if TEMPLATES[a.template].get("assistant_end") == "eos" else tok.convert_tokens_to_ids("<|im_end|>")
    pad = tok.pad_token_id if tok.pad_token_id is not None else end
    out = []
    with torch.no_grad(), sdpa_kernel(ATTN):
        for i in range(0, len(gens), a.batch):
            chunk = gens[i:i + a.batch]
            ps = [prompt_ids(tok, a.template, g["prompt"])[0] for g in chunk]
            L = max(len(p) for p in ps)
            ids = torch.full((len(ps), L), pad)
            att = torch.zeros((len(ps), L), dtype=torch.long)
            for k, p in enumerate(ps):
                ids[k, L - len(p):], att[k, L - len(p):] = p, 1
            o = model.generate(input_ids=ids.cuda(), attention_mask=att.cuda(), max_new_tokens=a.max_new,
                               do_sample=False, repetition_penalty=1.1, eos_token_id=end, pad_token_id=pad)
            for k, g in enumerate(chunk):
                out.append({**{x: v for x, v in g.items() if x != "prompt"},
                            "user": next((m["content"] for m in reversed(g["prompt"]) if m["role"] == "user"), ""),
                            "output": tok.decode(o[k, L:], skip_special_tokens=True).strip()})
    Path(a.out).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), "utf-8")
    print(f"wrote {len(out)} to {a.out}")


if __name__ == "__main__":
    main()
