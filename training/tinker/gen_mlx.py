"""Generate a quantized MLX model's answers to a frozen prompt set on the Mac, in gen_eval.py's output format, so
training/score_generations.py scores them like the 4B's (owner, 2026-10-31: no inference on Tinker).

    uv run --python 3.12 --with mlx-lm python -I training/tinker/gen_mlx.py --model DIR --prompts training/gen_prompts_v1.jsonl --out OUT.jsonl

Same decoding as gen_eval.py: greedy, repetition penalty 1.1, up to 384 new tokens. The chat template is rendered
with enable_thinking=False (the empty <think></think> the run trained under, renderer qwen3_5_disable_thinking).
"""
import argparse
import json
from pathlib import Path

from mlx_lm import generate, load
from mlx_lm.sample_utils import make_logits_processors, make_sampler


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new", type=int, default=384)
    a = ap.parse_args()
    model, tok = load(a.model)
    sampler = make_sampler(temp=0.0)
    procs = make_logits_processors(repetition_penalty=1.1)
    gens = [json.loads(x) for x in Path(a.prompts).read_text("utf-8").splitlines() if x.strip()]
    out = []
    for i, g in enumerate(gens):
        prompt = tok.apply_chat_template(g["prompt"], add_generation_prompt=True, tokenize=False,
                                         enable_thinking=False)
        text = generate(model, tok, prompt=prompt, max_tokens=a.max_new, sampler=sampler, logits_processors=procs)
        out.append({**{k: v for k, v in g.items() if k != "prompt"},
                    "user": next((m["content"] for m in reversed(g["prompt"]) if m["role"] == "user"), ""),
                    "output": text.strip()})
        if i % 50 == 0:
            print(f"{i}/{len(gens)}", flush=True)
    Path(a.out).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), "utf-8")
    print(f"wrote {len(out)} to {a.out}")


if __name__ == "__main__":
    main()
