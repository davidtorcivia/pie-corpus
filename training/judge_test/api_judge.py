"""The round-2 judge brief through the Claude API, one item per call (the shape the RL judge will have), with the
engine analysis inline and no tools. Records each call's usage and cost.

    uv run --with anthropic python -I training/judge_test/api_judge.py --model claude-haiku-5-5 --effort high \
        --out training/judge_test/verdicts3-api-haiku-high.json

Key: ANTHROPIC_API_KEY or ~/.config/anthropic/api_key; the org-level key needs ~/.config/anthropic/workspace_id.
"""
import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "training/rl"))
from judge import PRICE, SYSTEM, call, client  # noqa: E402  (the RL judge's own brief and call: one source)


def judge(c, model, effort, item):
    return {"id": item["id"], **call(c, item, model, effort)}


GROUP = """

Several items follow, as a JSON array. Judge each one on its own. Answer with only a JSON array, one object per item
in the same order: {"id": the item's id, "verdict": "ok" or "wrong", "word": the PIE word at fault or null,
"reason": one short sentence}."""


def judge_group(c, model, effort, items):
    """Several items in one call (the RL judge sends a prompt's rollouts together: one call per prompt)."""
    body = json.dumps([{"id": it["id"], **{k: it[k] for k in ("english", "pie", "analysis", "senses") if k in it}}
                       for it in items], ensure_ascii=False, indent=1)
    t = time.time()
    r = c.messages.create(model=model, max_tokens=20000, system=SYSTEM.rsplit("\n\nAnswer with only", 1)[0] + GROUP,
                          output_config={"effort": effort}, messages=[{"role": "user", "content": body}])
    text = "".join(b.text for b in r.content if b.type == "text")
    m = re.search(r"\[.*\]", text, re.S)
    try:
        got = {v["id"]: v for v in json.loads(m[0])} if m else {}
    except (json.JSONDecodeError, TypeError, KeyError):
        got = {}
    u, n = r.usage, len(items)
    return [{"id": it["id"], "verdict": got.get(it["id"], {}).get("verdict", "unparsed"),
             "word": got.get(it["id"], {}).get("word"), "reason": got.get(it["id"], {}).get("reason", ""),
             "in": u.input_tokens / n, "out": u.output_tokens / n, "s": round(time.time() - t, 1)} for it in items]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-haiku-5-5")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--items", default=str(HERE / "items_v2.jsonl"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--group", type=int, default=1, help="items per call")
    ap.add_argument("--only-flagged", help="a verdicts file: judge only the items it marked wrong (the tier-2 check)")
    a = ap.parse_args()
    items = [json.loads(x) for x in Path(a.items).read_text("utf-8").splitlines() if x.strip()]
    if a.only_flagged:
        flagged = {v["id"] for v in json.loads(Path(a.only_flagged).read_text()) if v["verdict"] != "ok"}
        items = [it for it in items if it["id"] in flagged]
    c = client()
    t = time.time()
    with ThreadPoolExecutor(a.workers) as ex:
        if a.group > 1:
            chunks = [items[i:i + a.group] for i in range(0, len(items), a.group)]
            rows = [r for g in ex.map(lambda ch: judge_group(c, a.model, a.effort, ch), chunks) for r in g]
        else:
            rows = list(ex.map(lambda it: judge(c, a.model, a.effort, it), items))
    Path(a.out).write_text(json.dumps(rows, ensure_ascii=False, indent=0), "utf-8")
    pi, po = PRICE[a.model]
    tin, tout = sum(r["in"] for r in rows), sum(r["out"] for r in rows)
    cost = (tin * pi + tout * po) / 1e6
    print(f"{a.model} {a.effort}: {len(rows)} items, {time.time() - t:.0f} s wall, in {tin} out {tout} tokens, "
          f"${cost:.4f} (${cost / len(rows) * 1000:.2f} per 1000 judgments), "
          f"unparsed {sum(r['verdict'] == 'unparsed' for r in rows)}")


if __name__ == "__main__":
    main()
