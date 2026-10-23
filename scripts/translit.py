#!/usr/bin/env python3
"""Command-line front end for pie.translit and pie.notation.

  uv run python -I scripts/translit.py to-ascii   "h₂ówis h₁éḱwōs-kʷe"
  uv run python -I scripts/translit.py to-unicode "h2o/wis h1e/k'wo:s-kwe"
  uv run python -I scripts/translit.py normalize --profile plain-h-aspirates "bher-"
  uv run python -I scripts/translit.py check < lines.txt

With no text arguments, reads lines from stdin. Exits 1 if any line fails.
"""

import argparse
import sys

from pie.notation import PROFILES, normalize
from pie.translit import TranslitError, is_canonical, to_ascii, to_unicode


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["to-ascii", "to-unicode", "normalize", "check"])
    ap.add_argument("text", nargs="*")
    ap.add_argument("--profile", default="default", choices=sorted(PROFILES))
    args = ap.parse_args()

    lines = args.text or [line.rstrip("\n") for line in sys.stdin]
    failed = 0
    for line in lines:
        try:
            if args.command == "to-ascii":
                print(to_ascii(line))
            elif args.command == "to-unicode":
                print(to_unicode(line))
            elif args.command == "normalize":
                r = normalize(line, args.profile)
                flag = "" if r.canonical else "\tNOT-CANONICAL"
                print(f"{r.text}\t{','.join(r.applied) or '-'}{flag}")
                failed += not r.canonical
            else:
                if not is_canonical(line):
                    to_ascii(line)  # raises with a located message if outside inventory
                    raise TranslitError("not NFC", line, 0)
                print(f"ok\t{line}")
        except TranslitError as e:
            failed += 1
            print(f"error\t{e}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
