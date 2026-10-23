#!/usr/bin/env python3
"""Build corpus/tier1/<work_group>.jsonl and the Tier 1 validation report.

  uv run python -I scripts/build_tier1.py
"""

import collections
import json
import sys
from pathlib import Path

from pie.tier1 import build_records

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    records, cross = build_records()
    out = ROOT / "corpus" / "tier1"
    by_group = collections.defaultdict(list)
    for r in records:
        by_group[r["work_group_id"]].append(r)
    for g, rs in by_group.items():
        with (out / f"{g}.jsonl").open("w", encoding="utf-8") as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # per-version validation summary
    summary = {}
    for r in records:
        s = summary.setdefault(r["work_id"], collections.Counter())
        s["lines"] += 1
        if r["pie"] is None:
            s["documentary_lines"] += 1
            continue
        for t in r["tokens"]:
            s["tokens"] += 1
            s[f"match:{t['match']}" if t["match"] else f"miss:{t['miss']}"] += 1
    rows = {}
    for wid, s in sorted(summary.items()):
        found = sum(v for k, v in s.items() if k.startswith("match:"))
        rows[wid] = {**dict(s), "coverage": round(found / s["tokens"], 3) if s["tokens"] else None}
    report = {"records": len(records), "versions": rows, "cross_check_diffs": cross}
    (ROOT / "data" / "tier1_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", "utf-8")
    for wid, r in rows.items():
        misses = {k[5:]: v for k, v in r.items() if k.startswith("miss:")}
        tiers = {k[6:]: v for k, v in r.items() if k.startswith("match:")}
        print(f"{wid:56} lines {r['lines']:2} doc {r.get('documentary_lines', 0):2} tokens {r.get('tokens', 0):3} "
              f"cov {r['coverage']}  {tiers} {misses}")
    print("cross-check diffs:", len(cross))
    for c in cross:
        print(f"   {c['work_id']} vs {c['secondary']}: similarity {c['similarity']}, diffs {c['diffs'][:6]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
