"""Generate a frozen prompt set on Tinker from a run's sampler checkpoint, unquantized (bf16), in eval_ckpt.py's output
format, for training/score_generations.py and the benchmark. Owner, 2026-11-03: Tinker sampling is allowed for the
Nemotron run's benchmark answers, to get an unquantized score beside the local oQ5 one; other sampling stays local.

    Q:\\AI\\PIE\\tinker\\.venv\\Scripts\\python.exe -I tinker_gen.py SAMPLER_PATH PROMPTS.jsonl OUT.jsonl

Same decoding as eval_ckpt.py: greedy (temperature 0), up to 384 new tokens, thinking off (renderer
nemotron3_ultra_disable_thinking: the empty <think></think> prefill the run trained under). Prints the tokens used.
"""
import asyncio
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ["TINKER_API_KEY"] = open(r"B:\Dropbox\Dropbox\AI BRAIN\tinker.txt").read().strip()
import tinker  # noqa: E402
from tinker_cookbook.renderers import get_renderer  # noqa: E402
from tinker_cookbook.tokenizer_utils import get_tokenizer  # noqa: E402

MODEL = "nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16"
RENDERER = "nemotron3_ultra_disable_thinking"
CONCURRENCY = 32


async def main(sampler_path, prompts_path, out_path):
    tok = get_tokenizer(MODEL)
    rend = get_renderer(RENDERER, tok)
    sc = tinker.ServiceClient()
    client = sc.create_sampling_client(model_path=sampler_path)
    params = tinker.SamplingParams(max_tokens=384, temperature=0.0, stop=rend.get_stop_sequences())
    gens = [json.loads(x) for x in open(prompts_path, encoding="utf-8") if x.strip()]
    sem = asyncio.Semaphore(CONCURRENCY)
    used = {"prompt": 0, "completion": 0}

    async def one(g):
        async with sem:
            mi = rend.build_generation_prompt(g["prompt"])
            r = await client.sample_async(prompt=mi, num_samples=1, sampling_params=params)
            toks = r.sequences[0].tokens
            used["prompt"] += mi.length
            used["completion"] += len(toks)
            msg, _ = rend.parse_response(toks)
            text = msg["content"] if isinstance(msg.get("content"), str) else "".join(
                p.get("text", "") for p in msg.get("content", []) if isinstance(p, dict))
            return text.split("</think>")[-1].strip()

    outs = await asyncio.gather(*(one(g) for g in gens))
    rows = [{**{k: v for k, v in g.items() if k != "prompt"},
             "user": next((m["content"] for m in reversed(g["prompt"]) if m["role"] == "user"), ""),
             "output": o} for g, o in zip(gens, outs)]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))
    cost = used["prompt"] / 1e6 * 0.57 + used["completion"] / 1e6 * 1.44
    print(f"wrote {len(rows)} to {out_path}; tokens prompt {used['prompt']} completion {used['completion']}, ~${cost:.2f}")


if __name__ == "__main__":
    asyncio.run(main(*sys.argv[1:4]))
