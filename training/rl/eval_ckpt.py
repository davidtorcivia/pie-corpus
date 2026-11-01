"""Generate a frozen prompt set with the RL policy (the quantized SFT model plus an RL adapter checkpoint) in
mlx_lm, in gen_omlx.py's output format, for training/score_generations.py. Greedy, thinking off, cap 384.

    python -I training/rl/eval_ckpt.py --model DIR [--adapter RUN/adapters/0000250_adapters.safetensors] \
        --prompts training/gen_prompts_drills_v2.jsonl --out OUT.jsonl

Without --adapter it generates with the SFT model alone: the baseline to compare checkpoints with, under the same
generation path (omlx's numbers use repetition penalty 1.1 and are not comparable to these).
"""
import argparse
import json
import shutil
import tempfile
from pathlib import Path

from mlx_lm import batch_generate, load


def adapter_dir(ckpt: Path) -> str:
    """mlx_lm loads an adapter directory (adapter_config.json + adapters.safetensors); a numbered checkpoint
    file is linked into one."""
    if ckpt.is_dir():
        return str(ckpt)
    d = Path(tempfile.mkdtemp(prefix="rl-ckpt-"))
    shutil.copy(ckpt.parent / "adapter_config.json", d / "adapter_config.json")
    (d / "adapters.safetensors").symlink_to(ckpt.resolve())
    return str(d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new", type=int, default=384)
    ap.add_argument("--batch", type=int, default=64)
    a = ap.parse_args()
    model, tok = load(a.model, adapter_path=adapter_dir(Path(a.adapter)) if a.adapter else None)
    gens = [json.loads(x) for x in Path(a.prompts).read_text("utf-8").splitlines() if x.strip()]
    prompts = [tok.apply_chat_template(g["prompt"], add_generation_prompt=True, tokenize=True, enable_thinking=False)
               for g in gens]
    outs = []
    for i in range(0, len(prompts), a.batch):
        outs += batch_generate(model, tok, prompts[i:i + a.batch], max_tokens=a.max_new,
                               completion_batch_size=a.batch, prefill_batch_size=a.batch).texts
    rows = [{**{k: v for k, v in g.items() if k != "prompt"},
             "user": next((m["content"] for m in reversed(g["prompt"]) if m["role"] == "user"), ""),
             "output": o.split("</think>")[-1].strip()} for g, o in zip(gens, outs)]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
    print(f"wrote {len(rows)} to {a.out}")


if __name__ == "__main__":
    main()
