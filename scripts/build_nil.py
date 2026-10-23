#!/usr/bin/env python3
"""Turn the NIL transcription chunks (raw/, local) into data/lexicon/nil.jsonl:
facts only (root, formation stems as printed and normalized, gender, marker,
up to four daughter words and their branches, an English gloss composed from
them and its cleaned form, page). The lexicon build reads this committed file,
so the repo rebuilds without the book.

  uv run python -I scripts/build_nil.py [--out path]
"""

import argparse
import json
import sys
from pathlib import Path

from pie.nil import build_records

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "lexicon" / "nil.jsonl")
    args = ap.parse_args()
    recs = build_records()
    p = args.out
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), "utf-8")
    fm = [f for r in recs for f in r["formations"]]
    print(f"{len(recs)} NIL roots, {len(fm)} formations ({sum(1 for f in fm if f['stem'])} with a usable stem, "
          f"{sum(1 for f in fm if f['marker'] == '‡')} marked ‡, "
          f"{sum(1 for f in fm if f['gloss_en_composed'] and not f['gloss_en'])} composed glosses dropped, "
          f"{sum(1 for f in fm if len(f['branches']) < 2)} in fewer than two branches, "
          f"{sum(1 for f in fm if f['flags'])} with notation flags) → {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
