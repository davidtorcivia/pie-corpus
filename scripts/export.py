#!/usr/bin/env python3
"""Write export/: train/eval JSONL, task views and plain-text views.

eval_tasks_accent_specified.jsonl is the accent-sensitive eval view: eval_tasks.jsonl without the tasks flagged
"accent": "unresolved" (export/README.md).

  uv run python -I scripts/export.py [--include-pilot] [--experimental-batches]

The chat and plain-text layer (export/chat/, export/text/, export/text-ascii/; pie/export_chat.py) is written
from the same build. Token counts need a tokenizer.json and the tokenizers package:

  uv run --with tokenizers python -I scripts/export.py --tokenizer path/to/Qwen3-4B/tokenizer.json
"""

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

from pie.export import build, views
from pie.export_chat import write_chat

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-pilot", action="store_true")
    ap.add_argument("--experimental-batches", action="store_true",
                    help="explicitly admit failed/pending batches; record bypasses in summary")
    ap.add_argument("--tokenizer", help="tokenizer.json for chat/summary.json token counts (needs `tokenizers`)")
    args = ap.parse_args()
    d = build(include_pilot=args.include_pilot, experimental_batches=args.experimental_batches)
    out = ROOT / "export"
    for name in ("train_records", "eval_records", "train_tasks", "eval_tasks"):
        (out / f"{name.replace('_records', '').replace('_tasks', '_tasks')}.jsonl").write_text(
            "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in d[name]), "utf-8")
    vdir = out / "views"
    vdir.mkdir(exist_ok=True)
    for split in ("train", "eval"):
        for fname, text in views(d[f"{split}_records"]).items():
            (vdir / f"{split}.{fname}").write_text(text, "utf-8")
    summary = {k: len(v) for k, v in d.items() if k not in ("batch_eligibility", "neologism_share")}
    summary["neologism_share"] = d["neologism_share"]      # Tier 3b words / training words (PLAN.md cap 10-15%)
    summary["experimental_batches"] = args.experimental_batches
    summary["batch_eligibility"] = d["batch_eligibility"]
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
    chat = write_chat(d, out, tokenizer=args.tokenizer, provenance=_provenance(args))
    print(json.dumps({k: chat[k] for k in ("examples_by_kind", "neologism")}, indent=1, ensure_ascii=False))
    return 0


def _provenance(args) -> dict:
    """The commit the export was built from, and whether the inputs it reads had uncommitted changes."""
    def git(*a):
        try:
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return None
    dirty = git("status", "--porcelain", "--", "corpus", "data", "pie")
    return {"commit": git("rev-parse", "HEAD"), "inputs_dirty": bool(dirty) if dirty is not None else None,
            "include_pilot": args.include_pilot, "experimental_batches": args.experimental_batches}


if __name__ == "__main__":
    sys.exit(main())
