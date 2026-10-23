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
CAP_EXEMPT = {"pie-lex-h1esti"}          # "to be"


def lexeme_cap(n_sentences: int) -> int:
    """Max uses of one lexeme per batch: 6, or 2% of the batch if larger."""
    return max(6, round(0.02 * n_sentences))


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
    # the copula is exempt from the per-lexeme cap; everything else is capped
    uses = collections.Counter(t["lex_id"] for r in records for t in r["tokens"]
                               if not t["lex_id"].startswith("closed:") and t["lex_id"] not in CAP_EXEMPT)
    others = set()
    for f in (ROOT / "corpus" / "tier3").glob("*.jsonl"):
        # a batch's own initial run (<batch>-initial) is a draft of the same plans, not another batch
        if f.name != out.name and not f.stem.endswith("-initial"):
            others |= {json.loads(x)["pie"] for x in f.read_text("utf-8").splitlines() if x.strip()}
    pies = [r["pie"] for r in records]
    dup_within = len(pies) - len(set(pies))
    dup_across = sum(1 for p_ in set(pies) if p_ in others)
    n = max(1, len(records))
    summary = {"plans": len(plans), **stats, "reject_rate": round(stats["rejected"] / max(1, len(plans)), 3),
               "distinct_roots": len(roots), "roots_per_sentence": round(len(roots) / n, 3),
               "distinct_lexemes": len(uses), "max_lexeme_uses": max(uses.values(), default=0),
               "most_used": uses.most_common(5), "dup_within": dup_within, "dup_across_batches": dup_across,
               "tokens": sum(len(r["tokens"]) for r in records),
               "words_per_sentence": round(sum(len(r["pie"].split()) for r in records) / n, 2)}
    # Gates (docs/STATUS.md question 5): the batch passes only on numbers
    gates = {"reject_rate<=0.10": summary["reject_rate"] <= 0.10,
             f"max_lexeme_uses<={lexeme_cap(n)}": summary["max_lexeme_uses"] <= lexeme_cap(n),
             "roots_per_sentence>=0.35": summary["roots_per_sentence"] >= 0.35,
             "duplicates<=2%": (dup_within + dup_across) <= 0.02 * n,
             "all_exact": stats["exact_pass"] == stats["realized"]}
    summary["gates"] = gates
    summary["gate"] = "PASS" if all(gates.values()) else "FAIL"
    (ROOT / "data" / "generation" / "batches").mkdir(exist_ok=True)
    (ROOT / "data" / "generation" / "batches" / f"{args.batch}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    for r in rejects[:10]:
        print("  REJECT", r["plan_id"], r["errors"][:3])
    return 0


if __name__ == "__main__":
    sys.exit(main())
