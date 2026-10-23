#!/usr/bin/env python3
"""Check, realize and validate a batch of Tier 3 plans.

  uv run python -I scripts/realize_plans.py data/generation/plans/pilot-fable.jsonl --batch pilot-fable

Plans that fail the checker go to data/generation/rejects/<batch>.jsonl with
their errors. Realized records go to corpus/tier3/<batch>.jsonl.
"""

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

from pie.meter import measure
from pie.realize import Lexicon, check_plan, realize
from pie.translit import to_ascii
from pie.validate import load_index, validate_text

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plans", type=Path)
    ap.add_argument("--batch", required=True)
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--prompt-id", default="tier3-planner-v1")
    args = ap.parse_args()
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                         text=True).stdout.strip()
    lx, ix = Lexicon.load(), load_index()
    plans = [json.loads(x) for x in args.plans.read_text("utf-8").splitlines() if x.strip()]
    records, rejects, stats = [], [], collections.Counter()
    for n, p in enumerate(plans):
        plan = p.get("plan", p)
        errs = check_plan(plan, lx)
        if errs:
            rejects.append({"plan_id": p.get("plan_id", n), "errors": errs, "plan": plan})
            stats["rejected"] += 1
            continue
        r = realize(plan, lx)
        v = validate_text(r["pie"], ix)
        stats["realized"] += 1
        stats["exact_pass"] += set(v["tiers"]) == {"exact"} and v["coverage"] == 1.0
        roots = sorted({lx.entries[w["lex_id"]].get("root_id") for w in r["words"]
                        if w["lex_id"] in lx.entries} - {None})
        records.append({
            "id": f"t3-{args.batch}-{len(records) + 1:05d}",
            "tier": 3, "provenance": "synthetic", "citation": None,
            "work_id": args.batch, "work_group_id": None, "line_no": None,
            "pie": r["pie"], "pie_ascii": to_ascii(r["pie"]), "source_form": None,
            "tokens": [{"form": w["form"], "lex_id": w["lex_id"],
                        "root_id": lx.entries.get(w["lex_id"], {}).get("root_id"),
                        "features": w["features"], "verified": True} for w in r["words"]],
            "gloss": r["gloss"], "english": r["english"],
            "genre": p.get("genre"), "theme": p.get("theme", []),
            "syllables": measure(r["pie"])["syllables"], "meter": None,
            "formulas": [], "cognate_refs": [], "alt_reconstructions": [],
            "validator": {k: v[k] for k in ("status", "coverage", "tiers", "misses")},
            "generator": {"model": args.model, "engine_version": sha, "prompt_id": args.prompt_id,
                          "convention": "handbook", "plan": plan},
            "neologism": False, "roots": roots,
            "notes": "",
        })
    out = ROOT / "corpus" / "tier3" / f"{args.batch}.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), "utf-8")
    (ROOT / "data" / "generation" / "rejects" / f"{args.batch}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rejects), "utf-8")
    roots = {x for r in records for x in r["roots"]}
    summary = {"plans": len(plans), **stats, "reject_rate": round(stats["rejected"] / max(1, len(plans)), 3),
               "distinct_roots": len(roots), "tokens": sum(len(r["tokens"]) for r in records)}
    print(json.dumps(summary, ensure_ascii=False))
    for r in rejects[:10]:
        print("  REJECT", r["plan_id"], r["errors"][:3])
    return 0


if __name__ == "__main__":
    sys.exit(main())
