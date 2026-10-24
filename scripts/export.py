#!/usr/bin/env python3
"""Write export/: train/eval JSONL, task views and plain-text views.

eval_tasks_accent_specified.jsonl is the accent-sensitive eval view: eval_tasks.jsonl without the tasks flagged
"accent": "unresolved" (export/README.md).

  uv run python -I scripts/export.py [--include-pilot]
"""

import argparse
import collections
import json
import sys
from pathlib import Path

from pie.export import build, views

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-pilot", action="store_true")
    args = ap.parse_args()
    d = build(include_pilot=args.include_pilot)
    out = ROOT / "export"
    for name in ("train_records", "eval_records", "train_tasks", "eval_tasks"):
        (out / f"{name.replace('_records', '').replace('_tasks', '_tasks')}.jsonl").write_text(
            "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in d[name]), "utf-8")
    vdir = out / "views"
    vdir.mkdir(exist_ok=True)
    for split in ("train", "eval"):
        for fname, text in views(d[f"{split}_records"]).items():
            (vdir / f"{split}.{fname}").write_text(text, "utf-8")
    summary = {k: len(v) for k, v in d.items()}
    summary["train_tasks_by_type"] = dict(collections.Counter(t["task"] for t in d["train_tasks"]))
    summary["eval_tasks_by_type"] = dict(collections.Counter(t["task"] for t in d["eval_tasks"]))
    (out / "eval_tasks_accent_specified.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in d["eval_tasks_accent_specified"]), "utf-8")
    # accent flags (data/morph/accent_unresolved.json): unresolved = missing information; representation = voc. ph₂ter
    for split in ("train_tasks", "eval_tasks"):
        summary[f"{split}_by_accent_flag"] = {f"{k}/{t}": v for (k, t), v in sorted(collections.Counter(
            (x["accent"], x["task"]) for x in d[split] if x.get("accent")).items())}
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", "utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
