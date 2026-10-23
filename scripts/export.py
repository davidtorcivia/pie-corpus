#!/usr/bin/env python3
"""Write export/: train/eval JSONL, task views and plain-text views.

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
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", "utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
