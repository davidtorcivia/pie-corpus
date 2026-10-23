# OCR for scanned books (no text layer)

Output goes to `raw/books/text/<slug>/p####.txt` (gitignored), page numbers = PDF page index.

- `tess_ocr.py` — Tesseract 5 (`brew install tesseract tesseract-lang`), parallel pages at 400 dpi.
  Use it when the book prints Greek: `-l deu+grc` (Schmitt 1967), `eng+grc` (Watkins 1995).
- `vision_ocr.py` + `vision_ocr.swift` — macOS Vision (no install; no Greek support). Used for
  EWAia I–III (German and Latin transliteration).

    uv run python -I scripts/ocr/tess_ocr.py "<pdf>" raw/books/text/<slug> deu+grc 6
