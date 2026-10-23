#!/usr/bin/env python3
"""Run the forward sound-law checker over the lexicon (Phase 3b, warning-only).

  uv run python -I scripts/check_soundlaws.py

Writes data/lexicon/soundlaw_report.json (pass rate per law and daughter)
and data/lexicon/soundlaw_warnings.jsonl (one line per mismatch).
"""

import json
import sys
from pathlib import Path

from pie.soundlaw import run

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    r = run()
    out = ROOT / "data" / "lexicon"
    (out / "soundlaw_report.json").write_text(
        json.dumps({"total": r["total"], "by_law": r["by_law"]}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    (out / "soundlaw_warnings.jsonl").write_text(
        "".join(json.dumps(w, ensure_ascii=False) + "\n" for w in r["warnings"]), "utf-8")
    t = r["total"]
    print(f"{t['checks']} checks, {t['mismatch']} warnings, pass {1 - t['mismatch'] / t['checks']:.1%}")
    for k, v in r["by_law"].items():
        print(f"  {k:20} ok {v.get('ok', 0):4}  mismatch {v.get('mismatch', 0):3}  ({v['rate']:.1%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
