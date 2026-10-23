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


# DjVu page range each transcription chunk owns (one extra page may be read to
# finish an entry). Entries outside a chunk's range are dropped: one agent's
# append once landed in another chunk's file (chunk-05 lines in chunk-10).
CHUNK_RANGES = {f"chunk-{i:02d}": (lo, hi) for i, (lo, hi) in enumerate(
    [(69, 127), (128, 186), (187, 245), (246, 304), (305, 363), (364, 422), (423, 481), (482, 540),
     (541, 599), (600, 658), (659, 712)], start=1)}


def load_chunks(root: Path = ROOT) -> list[dict]:
    out = []
    for f in sorted((root / "raw/books/extract/liv2").glob("chunk-*.jsonl")):
        lo, hi = CHUNK_RANGES.get(f.stem, (0, 10 ** 6))
        for line in f.read_text("utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                if "headword_printed" in d and lo <= int(d.get("djvu_page") or -1) <= hi:
                    d["_chunk"] = f.stem
                    out.append(d)
    return out


def headword(printed: str) -> tuple[str | None, int | None, bool]:
    """'1.*bʰeh₂-' → (canonical 'bʰeh₂-', homograph 1, uncertain)."""
    s = printed.strip()
    unc = s.startswith("?")
    s = s.lstrip("?").strip()
    m = re.match(r"^\(?(\d+)\.\)?\s*", s)
    hom = int(m[1]) if m else None
    s = s[m.end():] if m else s
    s = s.lstrip("*").strip()
    # capital placeholders (R = any resonant, T, K, …) are not forms; H (laryngeal) is
    if re.search(r"[A-GI-Z]", s):
        return None, hom, unc
    # LIV's uncertain series: g⁽ᵘ̯⁾ = g or gʷ (optional labialization); ĝ⁽ʼ⁾ = uncertain
    # palatal (the palatal is kept as primary). Both mark the root uncertain.
    if "⁽ᵘ̯⁾" in s or "⁽ʼ⁾" in s:
        unc = True
        s = s.replace("⁽ᵘ̯⁾", "⁽ʷ⁾").replace("⁽ʼ⁾", "")
    # optional elements (⁽ʰ⁾, (s)) expand to variants, as in the Wiktionary builder; the full form wins
    from .lexicon import _expand_optional
    for v in _expand_optional(normalize(s, "liv2").text)[0]:
        if is_canonical(v):
            return v, hom, unc
    return None, hom, unc


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


def _gloss_sim(a: str, b: str) -> float:
    """Word overlap of two English glosses (stopwords and 'to' ignored)."""
    stop = {"to", "the", "a", "be", "of", "and", "or", "in", "up", "out", "make"}
    wa = {w for w in re.findall(r"[a-z]+", a) if w not in stop}
    wb = {w for w in re.findall(r"[a-z]+", b) if w not in stop}
    return len(wa & wb) / max(1, min(len(wa), len(wb))) if wa and wb else 0.0


def merge(lexicon: list[dict], entries: list[dict]) -> tuple[list[dict], dict]:
    """→ (new root entries to add, report). Matched roots are updated in place."""
    from .validate import key as vkey
    roots = [e for e in lexicon if e["kind"] == "root"]
    by_plain: dict[str, list[dict]] = {}
    by_generic: dict[str, list[dict]] = {}
    for r in roots:
        for f in [r["form"], *r.get("variants", [])]:
            by_plain.setdefault(_plain(f), []).append(r)
            by_generic.setdefault(vkey(f, "generic-H"), []).append(r)
    new, report = [], {"entries": len(entries), "matched": 0, "new": 0, "unparsed": [], "ocr_flags": [],
                       "ambiguous": []}
    seen = set()
    for e in entries:
        key = (e.get("headword_printed"), e.get("meaning_de"))
        if key in seen:      # overlap pages: the same entry from two chunks
            continue
        seen.add(key)
        if e.get("see") or (not e.get("stems") and ("entfällt" in json.dumps(e, ensure_ascii=False)
                                                    or not e.get("meaning_de"))):
            report.setdefault("cross_references", []).append(e.get("headword_printed"))
            continue         # "entfällt, s. …": a redirect, not a root
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
        if not cands:
            # same root written with a different laryngeal index or coloring
            # (LIV bʰeyH- ~ Wiktionary bʰeyh₂-): accept only if the glosses agree too
            en = (e.get("meaning_en") or "").lower()
            g = [r for r in by_generic.get(vkey(form, "generic-H"), [])
                 if r["meaning"] and _gloss_sim(en, r["meaning"][0].lower()) >= 0.35]
            if g:
                cands = g
                liv_match = "generic-H+gloss"
            else:
                liv_match = None
        else:
            liv_match = "form"
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
            liv["match"] = liv_match
            r.setdefault("liv", []).append(liv)
            if aspect and (r.get("root_type_source") != "head-template" or not r.get("aspect")):
                r["aspect"], r["root_type"], r["root_type_source"] = aspect, "verbal", "liv2"
            report["matched"] += 1
        else:
            new.append({"form": form, "liv": liv, "aspect": aspect, "meaning": [e.get("meaning_en") or ""],
                        "meaning_de": e.get("meaning_de")})
            report["new"] += 1
    return new, report
