#!/usr/bin/env python3
"""Exploratory: does replication 2's power shortfall come from a strict rule?

  uv run --group research python -I scripts/replication2_sensitivity.py

Reruns scripts/build_replication2.py's build (without writing the data) under looser
readings and reports the exact-matched effect slots of each. Not a substitute test:
the pre-registered build is the default one. Writes
data/research/backtest/replication2_sensitivity.json.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))
import build_replication2 as b  # noqa: E402

VARIANTS = {
    "pre-registered": {},
    "keep ?/[ daughter words": {"loose_daughters": True},
    "literal independence (bare stem vs first-run target)": {"independence": "literal"},
    "keep ?/[ daughters + literal independence": {"loose_daughters": True, "independence": "literal"},
    "also keep ‡/**/ˣ/uncertain formations (excluded by the plan)": {
        "loose_daughters": True, "loose_formations": True, "independence": "literal"},
    "no independence rule at all (first-run formations included)": {
        "loose_daughters": True, "loose_formations": True, "independence": "none"},
    "same, with a 1-family control rule": {
        "loose_daughters": True, "loose_formations": True, "independence": "none", "min_families": 1},
}


def main() -> int:
    out = {}
    for name, kw in VARIANTS.items():
        m = b.main(write=False, **kw)
        out[name] = {"sets": m["sets"], "families": m["families"], "effect_slots": m["effect_slots"],
                     "exact_matched": m["effect_slots_exact_matched"],
                     "matched_by_kind": {k: v["matched"] for k, v in m["per_kind"].items()}}
        print(f"{m['effect_slots_exact_matched']:4d}  {name}  {out[name]}")
    path = ROOT / "data/research/backtest/replication2_sensitivity.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
