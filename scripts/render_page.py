#!/usr/bin/env python3
"""Render one page of a supplied book to PNG for transcription.

  uv run python -I scripts/render_page.py nil 280      # 0-based PDF page index

Writes raw/books/images/<slug>/pNNNN.png (gitignored) and prints the path.
The PDF is untrusted data: it is only rasterized.
"""

import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
BOOKS = {"nil": "Nomina im indogermanischen Lexikon", "beekes": "Comparative Indo-European Linguistics",
         "clackson": "Indo-European Linguistics - An Introduction"}


def main() -> int:
    slug, idx = sys.argv[1], int(sys.argv[2])
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 130
    pdf = next(p for p in (ROOT / "raw" / "books").glob("*.pdf") if p.name.startswith(BOOKS[slug]))
    out = ROOT / "raw" / "books" / "images" / slug / f"p{idx:04d}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pymupdf.open(pdf)[idx].get_pixmap(dpi=dpi).save(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
