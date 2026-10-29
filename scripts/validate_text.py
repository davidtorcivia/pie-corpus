#!/usr/bin/env python3
"""Validate canonical PIE text line by line and show each token's analysis.

  uv run python -I scripts/validate_text.py "h₂ówis h₁éḱwōs-kʷe"
  uv run python -I scripts/validate_text.py < lines.txt
  uv run python -I scripts/validate_text.py --neologisms [data/lexicon/neologisms.jsonl] "…"   (Tier 3b)

The index is the Tier 1-3 validator lexicon, which never includes neologisms (PLAN.md "Tier 3b"); a Tier 3b text
is validated with the neologism table loaded (--neologisms, pie.neologism.index_neologisms).
"""

import sys
from pathlib import Path

from pie.validate import load_index, validate_text


def main() -> int:
    argv, neo = sys.argv[1:], None
    if "--neologisms" in argv:
        k = argv.index("--neologisms")
        has_path = k + 1 < len(argv) and argv[k + 1].endswith(".jsonl")
        neo = Path(argv[k + 1]) if has_path else True
        del argv[k: k + 1 + has_path]
    lines = argv or [x.rstrip("\n") for x in sys.stdin if x.strip()]
    ix = load_index()
    if neo:
        from pie.neologism import NEOLOGISMS, index_neologisms
        index_neologisms(ix, NEOLOGISMS if neo is True else neo)
    for line in lines:
        r = validate_text(line, ix)
        print(f"{r['status'].upper():5} cov={r['coverage']:.2f} tiers={r['tiers']} misses={r['misses']}  {line}")
        if r["accentless"]:
            print(f"   accentless (accent defect): {' '.join(r['accentless'])}")
        if r["accent_unresolved"]:
            print(f"   unresolved accent (missing information): {' '.join(r['accent_unresolved'])}")
        if r["accent_representation"]:
            print(f"   accent not representable (notation exception): {' '.join(r['accent_representation'])}")
        for t in r["tokens"]:
            if t.found:
                a = t.analyses[0]
                more = f" (+{len(t.analyses) - 1})" if len(t.analyses) > 1 else ""
                extra = "".join(f" {x}" for x in (t.clitic, t.augment and f"aug={t.augment}") if x)
                st = f" [{t.status}]" if t.status != "primary" else ""
                print(f"   {t.surface:18} {t.tier:9} {a.lex_id} {a.features}{more}{extra}{st}")
            else:
                print(f"   {t.surface:18} MISS      {t.miss}  {t.miss_detail or ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
