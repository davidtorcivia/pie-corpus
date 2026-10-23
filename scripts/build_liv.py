#!/usr/bin/env python3
"""Turn the LIV² transcription chunks (raw/, local) into data/lexicon/liv2.jsonl:
structured facts only (normalized headword, glosses, IEW, stem labels and
forms, page), deduplicated, cross-references and placeholders removed, each
checked against the page OCR. The lexicon build reads this committed file,
so the repo rebuilds without the book.

  uv run python -I scripts/build_liv.py
"""

import json
import sys
from pathlib import Path

from pie.liv import headword, load_chunks, ocr_check

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    seen, out, skipped = set(), [], {"cross_reference": 0, "unparsed": [], "duplicate": 0}
    for e in load_chunks():
        k = (e.get("headword_printed"), e.get("meaning_de"))
        if k in seen:
            skipped["duplicate"] += 1
            continue
        seen.add(k)
        if e.get("see") or not e.get("stems") and (not e.get("meaning_de") or "entfällt" in json.dumps(e)):
            skipped["cross_reference"] += 1
            continue
        form, hom, unc = headword(e["headword_printed"])
        if not form:
            skipped["unparsed"].append(e["headword_printed"])
            continue
        out.append({"root": form, "homograph": hom, "uncertain": unc or bool(e.get("uncertain_chars")),
                    "headword_printed": e["headword_printed"], "meaning_de": e.get("meaning_de"),
                    "meaning_en": e.get("meaning_en"), "iew": e.get("iew"),
                    "stems": [{"label": s.get("label"), "form": s.get("form_printed"),
                               "uncertain": bool(s.get("uncertain"))} for s in e.get("stems", [])],
                    "neubildungen": e.get("neubildungen", []),
                    "page": {"djvu": e["djvu_page"], "printed": e.get("printed_page")},
                    "ocr_check": ocr_check(e)})
    p = ROOT / "data" / "lexicon" / "liv2.jsonl"
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), "utf-8")
    flags = sum(1 for r in out if not all(r["ocr_check"].values()))
    print(f"{len(out)} LIV² roots written; skipped {skipped['duplicate']} duplicates, "
          f"{skipped['cross_reference']} cross-references, {len(skipped['unparsed'])} unparsed; "
          f"OCR-check flags {flags}")
    print("unparsed:", skipped["unparsed"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
