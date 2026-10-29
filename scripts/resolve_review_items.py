#!/usr/bin/env python3
"""After the verdicts are written: map the reviewer's flagged items to their records, without revealing plants.

  uv run python -I scripts/resolve_review_items.py t024

Reads docs/audits/packets/<batch>-verdicts.jsonl, which must already exist, and the key. For every item
judged minor or wrong it prints the source record id, or "(planted item: no fix needed)" for a plant, so
fixes can be made in the plans without diffing the packet against corpus/tier3/ (which reveals the plants:
t028 and t030 reviews). It also prints the sha256 of the verdicts file, which is the record that the
verdicts came first.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    batch = sys.argv[1]
    vpath = ROOT / "docs/audits/packets" / f"{batch}-verdicts.jsonl"
    if not vpath.exists():
        sys.exit(f"{vpath} missing: write the verdicts first")
    key = json.loads((ROOT / "data/audits/keys" / f"{batch}-key.json").read_text("utf-8"))
    print("verdicts sha256", hashlib.sha256(vpath.read_bytes()).hexdigest())
    for line in vpath.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        v = json.loads(line)
        if v["verdict"] == "ok":
            continue
        k = key.get(v["item"], {})
        if k.get("kind") == "plant":
            print(v["item"], v["verdict"], "(planted item: no fix needed)")
        else:
            print(v["item"], v["verdict"], k.get("source_id"), f"[{k.get('kind')}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
