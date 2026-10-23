"""Merge LIV² root entries (transcribed from page images) into the lexicon.

Input: raw/books/extract/liv2/chunk-NN.jsonl (one entry per line; see
docs/generation/liv2-brief.md). The transcription is checked against the
PDF's OCR text: the OCR garbles roots but keeps German glosses and IEW
numbers, so an entry whose gloss or IEW number is missing from its page's
OCR is flagged (a transcription slip or an invented entry) and never merged
silently.

Merge policy (decided before the data arrived):
- a LIV root that matches a Wiktionary root (normalized form, accent-
  insensitive; homographs disambiguated by meaning) gets `liv` (page,
  German and English gloss, IEW, stem types) and the aspect of LIV's primary
  stem: the first row of the main block (Präsens → impf, Aorist → pf,
  Perfekt → stat);
- a LIV-only root becomes a new root entry with `source: liv2` and its page;
- Neubildungen (post-PIE formations) never enter the PIE stem inventory.
"""

from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path

from .notation import normalize
from .translit import is_canonical

ROOT = Path(__file__).resolve().parent.parent
DJVU_TO_PDF = 1          # DjVu page n = PDF page n + 1 (verified on *bʰeh₃g-: d0074 = p0075)
ASPECT = {"Präsens": "impf", "Aorist": "pf", "Perfekt": "stat"}


def load_chunks(root: Path = ROOT) -> list[dict]:
    out = []
    for f in sorted((root / "raw/books/extract/liv2").glob("chunk-*.jsonl")):
        for line in f.read_text("utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                if "headword_printed" in d:
                    d["_chunk"] = f.stem
                    out.append(d)
    return out


def headword(printed: str) -> tuple[str | None, int | None, bool]:
    """'1.*bʰeh₂-' → (canonical 'bʰeh₂-', homograph 1, uncertain)."""
    s = printed.strip()
    unc = s.startswith("?")
    s = s.lstrip("?").strip()
    m = re.match(r"^(\d+)\.\s*", s)
    hom = int(m[1]) if m else None
    s = s[m.end():] if m else s
    s = s.lstrip("*").strip()
    r = normalize(s, "liv2")
    return (r.text if r.canonical else None), hom, unc


def _plain(f: str) -> str:
    d = unicodedata.normalize("NFD", f)
    return unicodedata.normalize("NFC", "".join(c for c in d if c not in ("́",)))


def ocr_check(e: dict, root: Path = ROOT) -> dict:
    """Does the page's OCR text contain the transcribed German gloss and IEW number?"""
    pdf_page = int(e["djvu_page"]) + DJVU_TO_PDF
    texts = []
    for p in (pdf_page - 1, pdf_page, pdf_page + 1):
        f = root / f"raw/books/text/liv2/p{p:04d}.txt"
        if f.exists():
            texts.append(f.read_text("utf-8"))
    t = " ".join(texts)
    gloss = (e.get("meaning_de") or "").strip("'‘’ ")
    words = [w for w in re.findall(r"\w{4,}", gloss)]
    gloss_ok = bool(words) and sum(w in t for w in words) >= max(1, len(words) // 2)
    iew_ok = True
    if e.get("iew"):
        num = re.findall(r"\d+", e["iew"])
        iew_ok = bool(num) and num[0] in re.sub(r"(\d)\s+(\d)", r"\1\2", t)
    return {"gloss_in_ocr": gloss_ok, "iew_in_ocr": iew_ok}


def merge(lexicon: list[dict], entries: list[dict]) -> tuple[list[dict], dict]:
    """→ (new root entries to add, report). Matched roots are updated in place."""
    roots = [e for e in lexicon if e["kind"] == "root"]
    by_plain: dict[str, list[dict]] = {}
    for r in roots:
        for f in [r["form"], *r.get("variants", [])]:
            by_plain.setdefault(_plain(f), []).append(r)
    new, report = [], {"entries": len(entries), "matched": 0, "new": 0, "unparsed": [], "ocr_flags": [],
                       "ambiguous": []}
    seen = set()
    for e in entries:
        key = (e.get("headword_printed"), e.get("meaning_de"))
        if key in seen:      # overlap pages: the same entry from two chunks
            continue
        seen.add(key)
        form, hom, unc = headword(e.get("headword_printed", ""))
        chk = ocr_check(e)
        if not (chk["gloss_in_ocr"] and chk["iew_in_ocr"]):
            report["ocr_flags"].append({"headword": e["headword_printed"], "page": e["djvu_page"], **chk})
        if not form:
            report["unparsed"].append(e.get("headword_printed"))
            continue
        stems = [s for s in e.get("stems", []) if s.get("label")]
        aspect = ASPECT.get(stems[0]["label"]) if stems else None
        liv = {"page_djvu": e["djvu_page"], "printed_page": e.get("printed_page"), "headword": e["headword_printed"],
               "homograph": hom, "uncertain": unc, "meaning_de": e.get("meaning_de"),
               "meaning_en": e.get("meaning_en"), "iew": e.get("iew"),
               "stems": [{"label": s["label"], "form": s.get("form_printed"), "uncertain": s.get("uncertain", False)}
                         for s in stems],
               "neubildungen": e.get("neubildungen", []), "ocr_check": chk}
        cands = by_plain.get(_plain(form), [])
        if len(cands) > 1:   # homographs: pick by meaning similarity
            en = (e.get("meaning_en") or "").lower()
            scored = sorted(cands, key=lambda r: -difflib.SequenceMatcher(
                None, en, (r["meaning"][0] if r["meaning"] else "").lower()).ratio())
            if en and scored:
                cands = scored[:1]
            else:
                report["ambiguous"].append(e["headword_printed"])
                cands = cands[:1]
        if cands:
            r = cands[0]
            r.setdefault("liv", []).append(liv)
            if aspect and (r.get("root_type_source") != "head-template" or not r.get("aspect")):
                r["aspect"], r["root_type"], r["root_type_source"] = aspect, "verbal", "liv2"
            report["matched"] += 1
        else:
            new.append({"form": form, "liv": liv, "aspect": aspect, "meaning": [e.get("meaning_en") or ""],
                        "meaning_de": e.get("meaning_de")})
            report["new"] += 1
    return new, report
