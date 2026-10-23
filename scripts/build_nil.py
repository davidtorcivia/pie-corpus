#!/usr/bin/env python3
"""Turn the NIL transcription chunks (raw/, local) into data/lexicon/nil.jsonl:
facts only (root, formation stems as printed and normalized, gender, marker,
up to four daughter words, an English gloss composed from them, page). The
lexicon build reads this committed file, so the repo rebuilds without the book.

  uv run python -I scripts/build_nil.py
"""

import json
import sys
from pathlib import Path

from pie.nil import build_records

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    recs = build_records()
    p = ROOT / "data" / "lexicon" / "nil.jsonl"
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), "utf-8")
    fm = [f for r in recs for f in r["formations"]]
    print(f"{len(recs)} NIL roots, {len(fm)} formations ({sum(1 for f in fm if f['stem'])} with a usable stem, "
          f"{sum(1 for f in fm if f['marker'] == '‡')} marked ‡) → {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
