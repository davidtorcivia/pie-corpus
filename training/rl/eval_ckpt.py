"""Generate a frozen prompt set with the RL policy (the quantized SFT model plus an RL adapter checkpoint) in
mlx_lm, in gen_omlx.py's output format, for training/score_generations.py. Greedy, thinking off, cap 384.

    python -I training/rl/eval_ckpt.py --model DIR [--adapter RUN/adapters/0000250_adapters.safetensors] \
        --prompts training/gen_prompts_drills_v2.jsonl --out OUT.jsonl

Without --adapter it generates with the SFT model alone: the baseline to compare checkpoints with, under the same
generation path (omlx's numbers use repetition penalty 1.1 and are not comparable to these).

--constrain: the engine-in-the-loop mode. Prompts whose answer is PIE (CONSTRAIN_KINDS) are generated one at a time
with pie.translator.constrain (every PIE word a form the engine knows, as it is written); each such row records
the decoding steps and how many gave way (no fitting candidate among the top 64). Pair it with prompts from
training/engine_prompts.py (lexicon hints).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
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


RUNS = Path("/Users/david/AI/pie-runs/rl/runs")
ROOT = Path(__file__).resolve().parents[2]
CONSTRAIN_KINDS = {"translate_en_pie", "translate_app/en_pie", "en_dialogue/en_pie", "en_dialogue/en_pie_gloss",
                   "en_dialogue/mixed", "pie_dialogue/pie_pie", "continuation"}


def generate_constrained(model, tok, prompt: list[int], max_new: int, grammar) -> tuple[str, dict]:
    import mlx.core as mx
    from mlx_lm.generate import generate_step
    from pie.translator.constrain import Constraint
    proc = Constraint(tok, grammar, len(prompt))
    eos = proc.eos
    out = []
    for t, _ in generate_step(mx.array(prompt), model, max_tokens=max_new, logits_processors=[proc]):
        t = int(t)
        if t in eos:
            break
        out.append(t)
    return tok.decode(out), {"steps": proc.steps, "fallbacks": proc.fallbacks}
SSM_MODELS = {"nemotron_h", "mamba", "mamba2", "jamba", "falcon_h1", "granitemoehybrid"}  # Qwen3.5/3.6 hybrids (gated-delta layers) stay padded-batched as before, so earlier scores stay comparable; unchecked one at a time


def live_trainers() -> list[str]:
    """Runs whose trainer pid is alive. A second model on the Mac GPU beside a GRPO trainer wedged the GPU and killed
    rl3 at step 288 (2026-11-01; docs/research/rl-lessons.md), so evals wait for training to end."""
    out = []
    for f in RUNS.glob("*/pid"):
        pid = f.read_text().strip()
        cmd = subprocess.run(["ps", "-p", pid, "-o", "command="], capture_output=True, text=True).stdout
        if "grpo.py" in cmd:          # the pid is live and still the trainer (pids are reused after a reboot)
            out.append(f.parent.name)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new", type=int, default=384)
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--force", action="store_true", help="run even while an RL trainer is alive")
    ap.add_argument("--same-length", action="store_true", help="batch only same-length prompts (no padding)")
    ap.add_argument("--constrain", action="store_true", help="engine-constrained decoding for PIE answers")
    a = ap.parse_args()
    if (busy := live_trainers()) and not a.force:
        sys.exit(f"refusing: RL trainer running ({', '.join(busy)}); evaluate after it exits, or pass --force")
    model, tok = load(a.model, adapter_path=adapter_dir(Path(a.adapter)) if a.adapter else None)
    gens = [json.loads(x) for x in Path(a.prompts).read_text("utf-8").splitlines() if x.strip()]
    prompts = [tok.apply_chat_template(g["prompt"], add_generation_prompt=True, tokenize=True, enable_thinking=False)
               for g in gens]
    outs = [None] * len(prompts)
    info = [None] * len(prompts)
    if a.constrain:
        sys.path.insert(0, str(ROOT))
        from pie.translator.constrain import Grammar
        grammar = Grammar.load()
        for i, g in enumerate(gens):
            if g.get("kind") in CONSTRAIN_KINDS:
                outs[i], info[i] = generate_constrained(model, tok, prompts[i], a.max_new, grammar)
        print(f"constrained {sum(x is not None for x in info)} prompts, "
              f"{sum(x['fallbacks'] for x in info if x)} of {sum(x['steps'] for x in info if x)} steps gave way", flush=True)
    # Models with recurrent (Mamba/SSM) layers can't batch left-padded prompts: the pad tokens enter the recurrent
    # state (2026-11-03, Nemotron 3.5 Super: 3/3 inflections right one at a time, 1/3 batched). For those, batch only
    # prompts of the same token length, which need no padding. Attention-only models batch as before.
    cfg = json.loads((Path(a.model) / "config.json").read_text())
    todo = [i for i in range(len(prompts)) if outs[i] is None]
    if cfg.get("model_type") in SSM_MODELS or a.same_length:
        groups = {}
        for i in todo:
            p = prompts[i]
            groups.setdefault(len(p), []).append(i)
        chunks = [ix[j:j + a.batch] for ix in groups.values() for j in range(0, len(ix), a.batch)]
        print(f"{cfg.get('model_type')}: {len(chunks)} same-length batches for {len(prompts)} prompts", flush=True)
    else:
        chunks = [todo[i:i + a.batch] for i in range(0, len(todo), a.batch)]
    for ix in chunks:
        texts = batch_generate(model, tok, [prompts[i] for i in ix], max_tokens=a.max_new,
                               completion_batch_size=a.batch, prefill_batch_size=a.batch).texts
        for i, t in zip(ix, texts):
            outs[i] = t
    rows = [{**{k: v for k, v in g.items() if k != "prompt"},
             "user": next((m["content"] for m in reversed(g["prompt"]) if m["role"] == "user"), ""),
             "output": o.split("</think>")[-1].strip(), **({"constraint": c} if c else {})}
            for g, o, c in zip(gens, outs, info)]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
    print(f"wrote {len(rows)} to {a.out}")


if __name__ == "__main__":
    main()
