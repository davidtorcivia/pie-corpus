"""Reviewed source-boundary repairs, before mapping or context construction.

Coordinates in material-unit-rules.json are one-based inclusive source OCR
lines, not generated table rows. See error-verdicts-material.jsonl for review.
The frozen Celtic layer remains an input; no raw Python is imported.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "data/research/8c/stageCS/material-unit-rules.json"


@lru_cache(maxsize=1)
def reviewed_ranges():
    return json.loads(RULES.read_text(encoding="utf-8"))


def excluded_source(corpus: str, filename: str, start: int, end: int | None = None) -> bool:
    """Exclude units wholly inside a reviewed non-primary source span."""
    end = start if end is None else end
    return any(r["corpus"] == corpus and Path(r["source"]).name == filename
               and r["start"] <= start <= end <= r["end"] for r in reviewed_ranges())


def join_restorations(text: str) -> str:
    """Internal alphabetic restorations belong to the enclosing word.

    Leave standalone brackets and editorial annotations intact.
    """
    return re.sub(r"(?<=[^\W\d_])\[([^\W\d_]+)\](?=[^\W\d_])", r"\1", text)


def repair_celtic_rows(rows: list[dict]) -> list[dict]:
    out = []
    welsh = "welsh-white-book-mabinogion-evans-1907:whitebookofmabin00evan:"
    first, second = welsh + "L21478-L21478", welsh + "L21480-L21480"
    merged_id = welsh + "L21478-L21480"
    for original in rows:
        d = dict(original)
        uid, text = d["id"], d["text"]
        m = re.search(r":([^:]+):L(\d+)-L(\d+)", uid)
        if m and excluded_source("celtic", m[1] + "_djvu.txt", int(m[2]), int(m[3])):
            continue
        if "eriu_1914_7:L273-L279" in uid:
            # Source lines 273-274 are narrative, 277-279 are apparatus.
            text = text.split(":", 1)[0] + ":"
        if "revueceltique16pari:L8224-L8230" in uid:
            text = re.sub(r"^in the Bodleian manuscript:\s*", "", text)
        if d.get("source", "").startswith("celt-ucc/"):
            text = join_restorations(text)
        d["text"] = text
        if uid == second and out and out[-1]["id"] == first:
            previous = out[-1]
            if previous["text"].endswith("hir") and text.startswith("awd "):
                out[-1] = {**previous, "id": merged_id, "text": previous["text"] + text}
                continue
        out.append(d)
    # Keep dedupe references valid if either source unit was a preferred copy.
    for d in out:
        if d.get("dup_of") in (first, second) and any(x["id"] == merged_id for x in out):
            d["dup_of"] = merged_id
    return out


def edda_region(line: int) -> tuple[str | None, bool]:
    """Reviewed introductory prose (one-based OCR lines) and owning poem."""
    for start, end, poem in ((5339, 5371, "Lokasenna"),
                             (12423, 12461, "Reginsmál"),
                             (15414, 15453, "Guðrúnarkviða en forna")):
        if start <= line <= end:
            return poem, True
    return None, False


def grein_apparatus(text: str) -> bool:
    # Numbered variant citations with manuscript/editor sigla, before OCR
    # normalization and lemmatization can make the quoted OE look like verse.
    return bool(re.search(r"\b\d+\)\s", text) and re.search(r"\b(?:MS|M3|Th|Grimm)\.", text))
