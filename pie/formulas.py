"""Poetic formulas from Watkins (1995) and West (2007).

`build()` reads the extraction files (raw/, local) and writes
data/formulas/formulas.jsonl, which is committed. Each record keeps the
form as printed, a normalized `pie` when the notation maps, the English
sense, the daughter attestations, and a page or section reference. The
extractors' evidence quotes (running text from the books) are not
included.

`tier1_candidates()` picks the formulas that are complete inflected
phrases: no gaps (…), no bare stems (-), no schematic placeholders
(PRO, X), no composite or Indo-Iranian-only reconstructions, and no
West forms whose word breaks the PDF text leaves ambiguous. They become
Tier 1 records with provenance "formulaic" (pie.tier1).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .notation import normalize

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "watkins": {"file": "raw/books/extract/watkins/formulas.jsonl", "profile": "watkins",
                "citation": "Watkins, C. (1995). How to Kill a Dragon: Aspects of Indo-European Poetics. "
                            "Oxford University Press."},
    "west": {"file": "raw/books/extract/west/formulas.jsonl", "profile": "west",
             "citation": "West, M. L. (2007). Indo-European Poetry and Myth. Oxford University Press."},
}
_FLAG = re.compile(r"^\[(no PIE wording|composite)\]\s*")
_ELLIPSIS = re.compile(r"\s*(\.\s*\.\s*\.|…)\s*")


def _clean(printed: str) -> str:
    s = _FLAG.sub("", printed).replace("*", "")
    return _ELLIPSIS.sub(" … ", s).strip()


def _kind(src: str, x: dict, printed: str | None) -> str:
    if src == "watkins":
        return x.get("type") or "schema"
    if not printed:
        return "attested"                   # West cites only daughter wordings
    return "phrase" if len(_clean(printed).split()) >= 2 else "lexical"


def build(root: Path = ROOT) -> list[dict]:
    out = []
    for src, cfg in SOURCES.items():
        path = root / cfg["file"]
        if not path.exists():
            continue
        for x in (json.loads(l) for l in path.read_text("utf-8").splitlines() if l.strip()):
            printed = x.get("pie_printed")
            flags = []
            if printed and (m := _FLAG.match(printed)):
                flags.append(m[1].replace(" ", "-").lower())
            notes = x.get("notes") or ""
            if re.search(r"Indo-Iranian|Greek[–-]Indo-Iranian|proto-Slavonic", (printed or "") + " " + notes):
                flags.append("not-full-pie")
            pie = None
            if printed and "no-pie-wording" not in flags:
                r = normalize(_clean(printed), cfg["profile"])
                pie = r.text if r.canonical else None
            out.append({
                "formula_id": x["formula_id"], "source": src, "kind": _kind(src, x, printed),
                "pie_printed": printed, "pie": pie, "english": x.get("english"),
                "attestations": x.get("cognate_attestations", []),
                "ref": {"chapter": x.get("chapter"), "section": x.get("section"),
                        "printed_page": x.get("printed_page"), "pdf_page": x.get("pdf_page")},
                "citation": cfg["citation"], "flags": flags, "notes": notes,
            })
    return out


def write(root: Path = ROOT) -> int:
    recs = build(root)
    d = root / "data" / "formulas"
    d.mkdir(exist_ok=True)
    (d / "formulas.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), "utf-8")
    return len(recs)


def load(root: Path = ROOT) -> list[dict]:
    p = root / "data" / "formulas" / "formulas.jsonl"
    return [json.loads(l) for l in p.read_text("utf-8").splitlines() if l.strip()] if p.exists() else []


def tier1_candidates(formulas: list[dict]) -> list[dict]:
    out, seen = [], set()
    for f in formulas:
        p = f.get("pie")
        if f["kind"] != "phrase" or not p or f["flags"]:
            continue
        # West's PDF text puts a space after a spacing ring (n˚ t), so a word break there is ambiguous
        if f["source"] == "west" and re.search("[\u02da\u00b0] ", f["pie_printed"] or ""):
            continue
        if "…" in p or "..." in p or re.search(r"[/;()\[\]]|[A-Z]", p) or any(w.endswith("-") or w.startswith("-") for w in p.split()):
            continue
        words = [w.replace("-", "") for w in p.split()]    # segmentation hyphens: h₁ōḱ-éw-es → h₁ōḱéwes
        if len(words) < 2:
            continue
        text = " ".join(words)
        if text in seen:
            continue
        seen.add(text)
        out.append({**f, "pie": text})
    return out
