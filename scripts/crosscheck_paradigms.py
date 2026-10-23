#!/usr/bin/env python3
"""Regenerate Wiktionary tables with the engine; print agreement, write mismatches.

  uv run python -I scripts/crosscheck_paradigms.py [--show N] [--group SUBSTR]
"""

import argparse
import collections
import json
import sys
from pathlib import Path

from pie.crosscheck import run

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paradigms", type=Path, default=ROOT / "data" / "lexicon" / "paradigms.jsonl")
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "morph" / "crosscheck.json")
    ap.add_argument("--show", type=int, default=0, help="print N mismatches")
    ap.add_argument("--group", default="", help="only show mismatches whose template contains this")
    args = ap.parse_args()
    r = run(args.paradigms)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", "utf-8")
    for g, c in r["by_group"].items():
        ok, bad = c.get("cells_ok", 0), c.get("cells_bad", 0)
        pct = 100 * ok / (ok + bad) if ok + bad else 0
        print(f"{g:40} tables {c.get('tables_ok', 0):4}/{c.get('tables_ok', 0) + c.get('tables_bad', 0):<4} "
              f"cells {ok:5}/{ok + bad:<5} {pct:5.1f}%")
    t = r["total"]
    ok, bad = t.get("cells_ok", 0), t.get("cells_bad", 0)
    print(f"{'TOTAL':40} tables {t.get('tables_ok', 0)}/{t.get('tables_ok', 0) + t.get('tables_bad', 0)} "
          f"cells {ok}/{ok + bad} {100 * ok / max(1, ok + bad):.1f}%")
    by_feat = collections.Counter((m["template"], m["feature"]) for m in r["mismatches"])
    print("top mismatch cells:", by_feat.most_common(12))
    shown = 0
    for m in r["mismatches"]:
        if args.group in m["template"] and shown < args.show:
            print(f"  {m['form']:14} {m['feature']:8} wikt={m['wiktionary']} engine={m['engine']} args={m['args']}")
            shown += 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
