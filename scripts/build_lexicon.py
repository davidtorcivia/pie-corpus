#!/usr/bin/env python3
"""Build data/lexicon/ from the kaikki.org PIE dump.

  uv run python -I scripts/build_lexicon.py raw/kaikki-pie-20261021/kaikki.org-dictionary-ProtoIndoEuropean.jsonl
"""

import argparse
import json
import sys
from pathlib import Path

from pie.lexicon import build

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dump", type=Path)
    ap.add_argument("--label", default="kaikki.org ProtoIndoEuropean, extracted 2026-10-21 from enwiktionary 2026-10-01")
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "lexicon")
    args = ap.parse_args()
    report = build(args.dump, args.out, args.label)
    brief = {k: v for k, v in report.items() if k not in ("unresolved_etymon_parts", "root_type_disagreements", "stale_registry_ids")}
    brief["unresolved_etymon_parts"] = len(report["unresolved_etymon_parts"])
    brief["root_type_disagreements"] = len(report["root_type_disagreements"])
    brief["stale_registry_ids"] = len(report["stale_registry_ids"])
    print(json.dumps(brief, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
