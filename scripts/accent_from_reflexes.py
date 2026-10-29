#!/usr/bin/env python3
"""Supply missing headword accents from the lexeme's own accented Vedic or Greek reflex (pie/accent_reflex.py,
docs/morphology.md "Accent from a Vedic or Greek reflex"), as form overrides in data/lexicon/overrides.jsonl.

  uv run python -I scripts/accent_from_reflexes.py [--write]

Only usable, accent-unresolved lexemes of an accent-faithful shape class are considered. Each override names the
reflex it rests on; tests/test_vocab_push.py re-derives every one from the lexicon. Rebuild afterwards
(build_lexicon.py, classify_lexicon.py, build_glosses.py) and remove the lexemes from
data/morph/accent_unresolved.json.
"""

import argparse
import json
import sys
from pathlib import Path

from pie.accent_reflex import accented, position
from pie.realize import Lexicon, accent_status

ROOT = Path(__file__).resolve().parent.parent
OV = ROOT / "data/lexicon/overrides.jsonl"
TAG = "accent from reflex"


def proposals(lx: Lexicon) -> list[dict]:
    out = []
    for i, r in sorted(lx.specs.items()):
        if not r.get("usable") or accent_status(i) != "unresolved":
            continue
        e = lx.entries[i]
        p = position(e["form"], r["rule"], e.get("reflexes", {}))
        if p:
            k, used = p
            cites = ", ".join(f"{u['lang']} {u['form']} ({u['roman']})" for u in used)
            out.append({"id": i, "form": accented(e["form"], k),
                        "accent_source": [{"lang": u["lang"], "form": u["form"], "roman": u["roman"]} for u in used],
                        "note": f"{TAG}: the accent of {cites}, same syllable counted from the end "
                                f"({r['rule']}; docs/morphology.md)"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    props = proposals(Lexicon.load())
    for p in props:
        print(p["id"], p["form"], p["note"])
    if args.write:
        lines = [x for x in OV.read_text("utf-8").splitlines() if x.strip()]
        have = {json.loads(x)["id"] for x in lines}
        lines += [json.dumps(p, ensure_ascii=False) for p in props if p["id"] not in have]
        OV.write_text("\n".join(lines) + "\n", "utf-8")
    print(len(props), "proposals", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
