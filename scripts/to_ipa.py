#!/usr/bin/env python3
"""Command-line front end for pie.ipa (conventions: docs/pronunciation.md).

  uv run python -I scripts/to_ipa.py convert "h₂ówis h₁éḱwōs-kʷe"
  uv run python -I scripts/to_ipa.py convert --ascii --tone stress "h2o/wis"
  uv run python -I scripts/to_ipa.py convert --xsampa < lines.txt
  uv run python -I scripts/to_ipa.py batch corpus/tier1/schleicher-fable.jsonl out.jsonl
  uv run python -I scripts/to_ipa.py stats corpus/tier1 corpus/tier2 corpus/tier3

convert: with no text arguments, reads lines from stdin; exits 1 if any line fails.
batch:   copies a JSONL file, adding an `ipa` field (and `xsampa` with --xsampa) to every record with a
         `pie` field (or --field). Writes a new file only: refuses to write over the input or, without
         --force, over an existing file.
stats:   converts every `pie` field under the given files/directories and reports failures, the IPA symbol
         inventory (code points, and phone units without tone), and the most frequent phones
         outside the plain Latin set.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from pie.ipa import CONVENTIONS, to_ipa, to_xsampa

# Symbols an English-trained TTS front end already has: not "unusual".
PLAIN = set("pbtdkɡszhmnrljwaeiou. ")


def _tone(v: str):
    return {"tone": True, "none": False, "stress": "stress"}[v]


def _opts(args) -> dict:
    return {"convention": args.convention, "tone": _tone(args.tone), "breaks": not args.no_breaks}


def phones(ipa: str) -> list[str]:
    """Phone units of an IPA string: a base letter with its combining marks and modifier letters (kʷ, ɡʷʱ,
    eː, n̩). Boundaries, breaks and stress marks are units of their own."""
    out: list[str] = []
    for ch in unicodedata.normalize("NFD", ipa):
        attach = unicodedata.combining(ch) or (ch in "ʷʱʲː")
        if attach and out:
            out[-1] += ch
        else:
            out.append(ch)
    return [unicodedata.normalize("NFC", s) for s in out]


def _jsonl_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in map(Path, paths):
        files += sorted(p.rglob("*.jsonl")) if p.is_dir() else [p]
    return files


def cmd_convert(args) -> int:
    lines = args.text or [line.rstrip("\n") for line in sys.stdin]
    failed = 0
    for line in lines:
        try:
            ipa = to_ipa(line, ascii=args.ascii, **_opts(args))
            print(to_xsampa(ipa) if args.xsampa else ipa)
        except ValueError as e:
            print(f"ERROR\t{line}\t{e}", file=sys.stderr)
            failed += 1
    return 1 if failed else 0


def cmd_batch(args) -> int:
    src, dst = Path(args.input), Path(args.output)
    if dst.resolve() == src.resolve():
        sys.exit("refusing to write over the input file")
    if dst.exists() and not args.force:
        sys.exit(f"{dst} exists (use --force to replace it)")
    n = failed = 0
    with src.open(encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            rec = json.loads(line)
            text = rec.get(args.field)
            if text is not None:
                try:
                    rec["ipa"] = to_ipa(text, ascii=args.field.endswith("ascii"), **_opts(args))
                    if args.xsampa:
                        rec["xsampa"] = to_xsampa(rec["ipa"])
                    n += 1
                except ValueError as e:
                    print(f"ERROR\t{rec.get('id')}\t{e}", file=sys.stderr)
                    failed += 1
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"{n} records converted, {failed} failed -> {dst}", file=sys.stderr)
    return 1 if failed else 0


def cmd_stats(args) -> int:
    opts = _opts(args)
    records = tokens = 0
    fails: list[tuple[str, str]] = []
    inv: Counter = Counter()
    chars: Counter = Counter()
    for f in _jsonl_files(args.paths):
        for line in f.read_text("utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            text = rec.get("pie")
            if not text:
                continue
            records += 1
            for word in text.split():
                tokens += 1
                try:
                    to_ipa(word, **opts)
                except ValueError as e:
                    fails.append((word, str(e)))
            try:
                ipa = to_ipa(text, **opts)
                chars.update(ch for ch in unicodedata.normalize("NFD", ipa) if ch != " ")
                inv.update(p for p in phones(to_ipa(text, **{**opts, "tone": False})) if p != " ")
            except ValueError:
                pass
    unusual = [(p, c) for p, c in inv.most_common() if any(ch not in PLAIN for ch in p) and p not in "|‖"]
    report = {"convention": args.convention, "tone": args.tone, "records": records, "tokens": tokens,
              "failed_tokens": len(fails), "failures": fails[:20],
              "distinct_codepoints": len(chars),
              "codepoints": {f"{ch} U+{ord(ch):04X}": n for ch, n in chars.most_common()},
              "distinct_phones": len(inv), "phones": dict(inv.most_common()),
              "unusual_top": unusual[:args.top]}
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--convention", default="default", choices=sorted(CONVENTIONS))
    common.add_argument("--tone", default="tone", choices=["tone", "stress", "none"],
                        help="accent as high tone (acute), as stress (ˈ), or unmarked")
    common.add_argument("--no-breaks", action="store_true", help="drop the ‖ | phrase breaks")
    sub = ap.add_subparsers(dest="command", required=True)
    c = sub.add_parser("convert", parents=[common])
    c.add_argument("text", nargs="*")
    c.add_argument("--ascii", action="store_true", help="input is pie_ascii")
    c.add_argument("--xsampa", action="store_true", help="print X-SAMPA instead of IPA")
    b = sub.add_parser("batch", parents=[common])
    b.add_argument("input")
    b.add_argument("output")
    b.add_argument("--field", default="pie", help="source field (a field ending in 'ascii' is read as pie_ascii)")
    b.add_argument("--xsampa", action="store_true", help="also add an xsampa field")
    b.add_argument("--force", action="store_true")
    s = sub.add_parser("stats", parents=[common])
    s.add_argument("paths", nargs="+")
    s.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    return {"convert": cmd_convert, "batch": cmd_batch, "stats": cmd_stats}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
