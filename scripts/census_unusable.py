#!/usr/bin/env python3
"""Census of the lexemes a planner cannot get, bucketed by the first cause in make_slice's pool order.

  uv run python -I scripts/census_unusable.py [--json OUT.json]

The pool order is usable spec, blocklist, P10 accent gate, eval holdout root, NIL hold, gloss. Prints the buckets.
docs/audits/unusable-lexemes-census.md was written from this output; its per-word lists are the work queue for
data agents.
"""

import argparse
import collections
import json
import runpy
import sys
from pathlib import Path

from pie.export import eval_root
from pie.realize import Lexicon

ROOT = Path(__file__).resolve().parent.parent


def census(lx: Lexicon) -> dict[str, list[str]]:
    ms = runpy.run_path(str(ROOT / "scripts" / "make_slice.py"))
    accent_ok, admit, held = ms["planner_accent_ok"], ms["NIL_ADMIT"], ms["NIL_GLOSS_HELD"]

    def nil_held(i):        # = make_slice.main's nil_held
        e = lx.entries[i]
        if any(u.startswith("nil-") for u in e.get("uncertain", [])):
            return True
        if e.get("source") == "nil":
            return i not in admit
        return e.get("meaning_source") == "nil" and i in held

    def cause(r):
        i, e = r["id"], lx.entries.get(r["id"], {})
        if not r["usable"]:
            if r["spec"] is not None:
                return f"backtest-fail:{r['rule']}"
            if e.get("form", "").endswith("-") or e.get("form", "").startswith("-"):
                return "bound-stem (form with a hyphen)"
            return r["rule"]
        if i in lx.blocked:
            return "blocklist"
        if not accent_ok(lx, i):
            return "no-accent (pool P10)"
        if eval_root(e.get("root_id")):
            return "eval-holdout root"
        if nil_held(i):
            return "NIL hold"
        if not e.get("meaning"):
            return "derived gloss only (needs --derived)" if i in lx.derived else "no gloss"
        return "ok"

    out: dict[str, list[str]] = collections.defaultdict(list)
    for x in (ROOT / "data" / "morph" / "inflection_specs.jsonl").read_text("utf-8").splitlines():
        r = json.loads(x)
        out[cause(r)].append(r["id"])
    return dict(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, help="write bucket → ids here")
    args = ap.parse_args()
    lx = Lexicon.load()
    ex = census(lx)
    for k, ids in sorted(ex.items(), key=lambda kv: -len(kv[1])):
        glossed = sum(1 for i in ids if lx.entries[i].get("meaning"))
        print(f"{len(ids):6} {k} ({glossed} glossed)")
    if args.json:
        args.json.write_text(json.dumps(ex, ensure_ascii=False, indent=0) + "\n", "utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
