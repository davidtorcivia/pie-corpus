#!/usr/bin/env python3
"""Validate canonical PIE text line by line and show each token's analysis.

  uv run python -I scripts/validate_text.py "h₂ówis h₁éḱwōs-kʷe"
  uv run python -I scripts/validate_text.py < lines.txt
"""

import sys

from pie.validate import load_index, validate_text


def main() -> int:
    lines = sys.argv[1:] or [x.rstrip("\n") for x in sys.stdin if x.strip()]
    ix = load_index()
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
