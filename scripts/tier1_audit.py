#!/usr/bin/env python3
"""Regenerate the coverage table in docs/audits/tier1-validation.md from data/tier1_report.json.

  uv run python -I scripts/build_tier1.py && uv run python -I scripts/tier1_audit.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCEPT = {"schleicher-fable-byrd-2013", "schleicher-fable-luhr-2008", "schleicher-fable-adams-1997",
          "king-and-god-byrd-2013", "king-and-god-hamp-sen-1997"}
BEGIN, END = "<!-- coverage:begin -->", "<!-- coverage:end -->"


def table() -> str:
    rep = json.loads((ROOT / "data" / "tier1_report.json").read_text("utf-8"))
    lines = ["| Version | Scope | Lines (doc.) | Tokens | Coverage | Exact | Misses by class |",
             "|---|---|---|---|---|---|---|"]
    rows = sorted(rep["versions"].items(), key=lambda kv: (kv[0] not in ACCEPT, kv[0]))
    for wid, r in rows:
        if not r.get("tokens"):
            lines.append(f"| {wid} | documentary | {r['lines']} ({r.get('documentary_lines', 0)}) | 0 | — | — | — |")
            continue
        misses = {k[5:]: v for k, v in r.items() if k.startswith("miss:")}
        ms = ", ".join(f"{k} {v}" for k, v in sorted(misses.items(), key=lambda kv: -kv[1]))
        exact = r.get("match:exact", 0) / r["tokens"]
        scope = "**acceptance**" if wid in ACCEPT else "pre-laryngeal / documentary"
        lines.append(f"| {wid} | {scope} | {r['lines']} ({r.get('documentary_lines', 0)}) | {r['tokens']} | "
                     f"{r['coverage']:.1%} | {exact:.1%} | {ms} |")
    return "\n".join(lines)


def main() -> int:
    doc = ROOT / "docs" / "audits" / "tier1-validation.md"
    text = doc.read_text("utf-8")
    a, b = text.index(BEGIN) + len(BEGIN), text.index(END)
    doc.write_text(text[:a] + "\n" + table() + "\n" + text[b:], "utf-8")
    print(table())
    return 0


if __name__ == "__main__":
    sys.exit(main())
