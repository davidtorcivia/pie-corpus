"""NIL (Wodtko, Irslinger & Schneider 2008): noun formations, read from page images.

`build_records()` turns the transcription chunks (raw/books/extract/nil/,
local) into facts-only records for data/lexicon/nil.jsonl: the root, and per
formation the stem as printed, a normalized stem, gender, marker, the first
daughter words and an English gloss composed from what they agree on.

`apply()` (called by pie.lexicon.build) matches each NIL root to a lexicon
root as LIV² roots are matched, then each formation to a derivative of that
root whose form, without accents and length, is the NIL stem plus an
inflectional ending. A matched lexeme gets a `nil` block, and if it has no
dictionary gloss it takes NIL's (`meaning_source: "nil"`). Formations marked
‡ (one language only) or ** (pre-forms) are never used as PIE glosses.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from .liv import _gloss_sim, _plain, headword
from .notation import normalize
from .translit import is_canonical

ROOT = Path(__file__).resolve().parent.parent
FIRST_PAGE, LAST_PAGE, CHUNK = 78, 807, 30
ENDINGS = ("", "s", "m", "os", "om", "ós", "óm", "h₂", "eh₂", "éh₂", "ih₂", "íh₂", "is", "ís", "us", "ús",
           "ōs", "ōn", "ō", "ḗr", "ēr", "ōr", "ṓr", "ṓ", "ḗn", "mn̥", "r̥", "n̥", "ts", "t")


def chunk_range(name: str) -> tuple[int, int]:
    n = int(name.split("-")[1])
    if n == 0:
        return 270, 299                      # the pilot
    lo = FIRST_PAGE + CHUNK * (n - 1)
    return lo, min(LAST_PAGE, lo + CHUNK - 1)


def stem(printed: str | None) -> str | None:
    """'?*ĝnoh₃-tér-' → 'ĝnoh₃tér' normalized; None for schematic or partial forms."""
    if not printed:
        return None
    s = printed.split(">")[-1].strip()                 # '**h₁éd-u̯-on- > *h₁éd-u̯on-': the later form
    s = re.sub(r"^[?‡ˣ\[\s*]+|[\]\s]+$", "", s).replace("(-)", "")
    if s.startswith("-") or "/" in s or "´" in s or re.search(r"\([^)]*\)", s):
        return None                                   # suffix-only, alternants or optional parts
    s = s.replace("-", "")
    t = normalize(s, "liv2").text
    # NIL writes the a-colouring next to h₂ (h₂áu̯g-, -ah₂-); the lexicon writes h₂e / eh₂
    t = unicodedata.normalize("NFC", re.sub("h₂a|ah₂", lambda m: m[0].replace("a", "e"),
                                            re.sub("h₂á|áh₂", lambda m: m[0].replace("á", "é"), t)))
    return t if t and is_canonical(t) else None


def build_records(root: Path = ROOT) -> list[dict]:
    out, seen = [], set()
    for f in sorted((root / "raw/books/extract/nil").glob("chunk-*.jsonl")):
        lo, hi = chunk_range(f.stem)
        for line in f.read_text("utf-8").splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            if "root_printed" not in e or not lo <= int(e.get("pdf_page") or -1) <= hi + 10:
                continue
            key = (e["root_printed"], e.get("root_gloss_de"))
            if key in seen or not e.get("formations"):
                continue
            seen.add(key)
            alts = []
            for part in re.split(r"\s*[,/]\s*", e["root_printed"]):
                part = re.sub(r"\((ó|o)-\)", "", part).strip()
                if "´" in part or not part.strip("*?- "):
                    continue
                f_, h_, u_ = headword(part)
                if f_ and f_ not in alts:
                    alts.append(f_)
            form, hom, unc = (alts[0] if alts else None), *headword(e["root_printed"].split(",")[0])[1:]
            out.append({
                "root": form, "root_alternatives": alts, "homograph": hom, "uncertain": unc or bool(e.get("uncertain_chars")),
                "root_printed": e["root_printed"], "root_gloss_de": e.get("root_gloss_de"),
                "root_gloss_en": e.get("root_gloss_en"), "liv_ref": e.get("liv_ref"),
                "page": {"pdf": e.get("pdf_page"), "printed": e.get("printed_page")},
                "formations": [{
                    "printed": x.get("form_printed"), "stem": stem(x.get("form_printed")),
                    "marker": x.get("marker") or ("‡" if (x.get("form_printed") or "").startswith("‡") else None),
                    "indent": x.get("indent"), "gender": x.get("gender"), "gloss_en": x.get("gloss_en"),
                    "evidence": (x.get("evidence") or [])[:4], "uncertain": bool(x.get("uncertain")),
                } for x in e["formations"]],
            })
    return out


def citation(stem: str, gender: str | None) -> tuple[str, str, str | None] | None:
    """NIL stem + gender → (citation form, pos, gender) for the classifier, or None.

    NIL prints stems (*ĝnoh₃-tér-, *dʰiH-ti-); the lexicon cites nominatives.
    Adjectives are the o-stems NIL prints without a gender.
    """
    from .phon import has_accent, parse
    try:
        if not has_accent(parse(stem)):
            return None                       # the slice gate needs an accent; don't guess one
    except ValueError:
        return None
    g = gender if gender in ("m", "f", "n") else None
    if re.search(r"[oó]$", stem):
        if g is None:
            return stem + "s", "adj", None
        return stem + ("m" if g == "n" else "s"), "noun", g
    if stem.endswith(("eh₂", "éh₂")):                     # eh₂-stem (NIL -ah₂-, normalized in stem())
        return stem, "noun", "f"
    if stem.endswith(("ih₂", "íh₂")):
        return stem, "noun", "f"
    if re.search(r"[ií]$|[uú]$", stem) and g in ("m", "f"):
        return stem + "s", "noun", g
    if re.search(r"[eé]s$", stem) and g in (None, "n"):   # s-stem neuter: ǵénh₁es- → ǵénh₁os
        return re.sub(r"([eé])s$", lambda m: {"e": "o", "é": "ó"}[m[1]] + "s", stem), "noun", "n"
    if re.search(r"m[eé]n$", stem) and g == "n":
        return re.sub(r"m[eé]n$", "mn̥", stem), "noun", "n"
    if re.search(r"t[eé]r$", stem) and g in (None, "m", "f"):
        return re.sub(r"t([eé])r$", lambda m: "t" + ("ḗ" if m[1] == "é" else "ē") + "r", stem), "noun", g or "m"
    if re.search(r"t[oó]r$", stem) and g in (None, "m"):
        return stem[:-2] + "ōr", "noun", "m"
    if re.search(r"[^aeiouāēīōūáéíóúr̥l̥m̥n̥]$", stem) and g in ("m", "f"):
        return stem + "s", "noun", g                      # root noun
    return None


def _key(form: str) -> str:
    from .validate import key
    return key(form.strip("-"), "nolength")


def apply(entries: dict[str, dict], records: list[dict], reg=None) -> dict:
    from .validate import key as vkey
    roots = [e for e in entries.values() if e["kind"] == "root"]
    by_plain, by_generic = {}, {}
    for r in roots:
        for f in [r["form"], *r.get("variants", [])]:
            by_plain.setdefault(_plain(f), []).append(r)
            by_generic.setdefault(vkey(f, "generic-H"), []).append(r)
    words = {}
    for e in entries.values():
        if e["kind"] in ("word", "derivative"):
            words.setdefault(_key(e["form"]), e)
    children = {}
    for e in entries.values():
        if e["kind"] in ("word", "derivative") and e.get("root_id"):
            children.setdefault(e["root_id"], []).append(e)
    rep = {"roots": len(records), "roots_matched": 0, "formations": 0, "formations_matched": 0, "glossed": 0,
           "new": 0}
    for x in records:
        en = (x.get("root_gloss_en") or "").lower()
        forms = x.get("root_alternatives") or ([x["root"]] if x["root"] else [])
        cands = [r for f in forms for r in by_plain.get(_plain(f), [])]
        if len(cands) > 1:
            cands = sorted(cands, key=lambda r: -_gloss_sim(en, (r["meaning"][0] if r["meaning"] else "").lower()))[:1]
        if not cands:
            cands = [r for f in forms for r in by_generic.get(vkey(f, "generic-H"), [])
                     if r["meaning"] and _gloss_sim(en, r["meaning"][0].lower()) >= 0.35][:1]
        if not cands:
            # a nominal headword (*dʰéĝʰ-om-, *dʰugh₂tér-): a word whose form is the stem + an ending
            for f in forms:
                k = _key(f.replace("-", ""))
                w = next((words[k + _key(end)] for end in ENDINGS if (k + _key(end)) in words), None)
                if w:
                    cands = [entries.get(w.get("root_id") or "", w)]
                    break
        if not cands:
            continue
        rep["roots_matched"] += 1
        root = cands[0]
        root.setdefault("nil", []).append({"root_printed": x["root_printed"], "page": x["page"]})
        kids = {_key(c["form"]): c for c in children.get(root["id"], []) + ([root] if root["kind"] != "root" else [])}
        for fm in x["formations"]:
            rep["formations"] += 1
            if not fm["stem"]:
                continue
            k = _key(fm["stem"])
            hit = next((kids[k + _key(end)] for end in ENDINGS if (k + _key(end)) in kids), None) if k else None
            if not hit:
                rep["new"] += _new_lexeme(entries, kids, root, x, fm, reg)
                continue
            rep["formations_matched"] += 1
            hit.setdefault("nil", []).append({**fm, "root_printed": x["root_printed"], "page": x["page"]})
            if not hit["meaning"] and fm["gloss_en"] and fm["marker"] not in ("‡", "**", "ˣ"):
                hit["meaning"], hit["meaning_source"] = [fm["gloss_en"]], "nil"
                rep["glossed"] += 1
    return rep


def _new_lexeme(entries: dict, kids: dict, root: dict, x: dict, fm: dict, reg) -> int:
    """A NIL formation the lexicon lacks → a new derivative lexeme (citation form built from
    the stem; the classifier assigns the paradigm and decides usability as for any lexeme)."""
    from .lexicon import slug
    from .translit import to_ascii
    if reg is None or not fm["stem"] or not fm["gloss_en"] or fm["marker"] in ("‡", "**", "ˣ"):
        return 0
    c = citation(fm["stem"], fm.get("gender"))
    if not c:
        return 0
    form, pos, g = c
    form = unicodedata.normalize("NFC", form)
    if not is_canonical(form) or _key(form) in kids:
        return 0
    lid = reg.get(f"nil|{x['root_printed']}|{fm['printed']}", f"pie-lex-{slug(form)}")
    entries[lid] = {
        "id": lid, "kind": "derivative", "form": form, "form_ascii": to_ascii(form), "variants": [], "stems": [],
        "pos": pos, "gender": g, "meaning": [fm["gloss_en"]], "meaning_source": "nil",
        "uncertain": ["nil-uncertain"] if fm["uncertain"] else [], "source": "nil",
        "source_ref": {"dump": "NIL (Wodtko, Irslinger & Schneider 2008)", "page": x["page"],
                       "printed": fm["printed"]},
        "confidence": "entry", "normalized": [], "etymon_parts": [], "reflexes": {},
        "nil": [{**fm, "root_printed": x["root_printed"], "page": x["page"]}],
        "parents": [root["id"]], "root_link_source": "nil", "root_id": root["id"] if root["kind"] == "root"
        else root.get("root_id")}
    kids[_key(form)] = entries[lid]
    return 1
