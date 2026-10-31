"""Generate a model's answers to a frozen prompt set through the local omlx server, in gen_eval.py's output format,
so training/score_generations.py scores them like the 4B's (owner, 2026-10-31: test in omlx, no inference on
Tinker).

    python3 -I training/tinker/gen_omlx.py --model MODEL_ID --prompts training/gen_prompts_v1.jsonl --out OUT.jsonl

Same decoding as gen_eval.py: greedy (temperature 0), repetition penalty 1.1, up to 384 new tokens, with
enable_thinking false (the empty <think></think> the run trained under, renderer qwen3_5_disable_thinking).
"""
import argparse
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

KEY = json.loads((Path.home() / ".omlx/settings.json").read_text())["auth"]["api_key"]


def ask(model, messages, max_new):
    body = {"model": model, "messages": messages, "temperature": 0.0, "repetition_penalty": 1.1,
            "max_tokens": max_new, "enable_thinking": False, "stream": False}
    req = urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"] or ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-new", type=int, default=384)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    gens = [json.loads(x) for x in Path(a.prompts).read_text("utf-8").splitlines() if x.strip()]
    with ThreadPoolExecutor(a.workers) as ex:
        outs = list(ex.map(lambda g: ask(a.model, g["prompt"], a.max_new), gens))
    rows = [{**{k: v for k, v in g.items() if k != "prompt"},
             "user": next((m["content"] for m in reversed(g["prompt"]) if m["role"] == "user"), ""),
             "output": o.strip()} for g, o in zip(gens, outs)]
    Path(a.out).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), "utf-8")
    print(f"wrote {len(rows)} to {a.out}")


if __name__ == "__main__":
    main()
