#!/usr/bin/env python3
"""Build the glosses for lexemes without a dictionary gloss (pie/glosses.py), after build_lexicon.py and
classify_lexicon.py:

  uv run python -I scripts/build_glosses.py

data/lexicon/derived_glosses.jsonl: root meaning + suffix function (approximate, --derived slices only).
data/lexicon/confirmed_glosses.jsonl: reflex-confirmed glosses, from data/lexicon/reflex_glosses.jsonl
(docs/lexicon.md "Reflex-confirmed glosses"); Lexicon.load gives them meaning_source "reflex-confirmed".
"""

import sys

from pie import glosses


def main() -> int:
    print("derived", glosses.write())
    print("confirmed", glosses.write_confirmed())
    return 0


if __name__ == "__main__":
    sys.exit(main())
