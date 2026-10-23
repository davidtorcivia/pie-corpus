"""Build Tier 1 records (provenance `scholarly`) from the collected sources.

Inputs: raw/tier1-*/versions.json, written by the collection agents; see
raw/MANIFEST.md. A primary source wins over a secondary one for the same
work; each secondary copy is kept as a cross-check, and differences are
reported. Editorial paragraph numbers ("(1) ") are stripped as a
structural step and noted on the record.

A line whose notation cannot be mapped to the canonical inventory (Hirt's
ь, Kortlandt's glottalic system) is a *documentary* record: `pie` is null,
`source_form` is kept, it stays in the parallel-reconstruction set, and it
never enters training text views. Normalization is notational only
(docs/notation.md).
"""

from __future__ import annotations

import difflib
import json
import re
from dataclasses import asdict
from pathlib import Path

from .meter import measure
from .notation import normalize
from .translit import to_ascii

ROOT = Path(__file__).resolve().parent.parent

# work_id → normalization profile; None = documentary (no notational mapping yet)
PROFILE = {
    "schleicher-fable-schleicher-1868": "schleicher-1868",
    "schleicher-fable-hirt-1939": "hirt-1939",
    "schleicher-fable-lehmann-zgusta-1979": "lehmann-zgusta-1979",
    "schleicher-fable-danka-1986": "danka-1986",
    "schleicher-fable-adams-1997": "adams-1997",
    "schleicher-fable-luhr-2008": "luhr-2008",
    "schleicher-fable-voyles-barrack-2009": "voyles-barrack-2009",
    "schleicher-fable-byrd-2013": "default",
    "king-and-god-hamp-sen-1997": "default",
    "king-and-god-lehmann-1952": "default",
    "king-and-god-byrd-2013": "default",
}
DOCUMENTARY_REASON = {
    "kortlandt": "Kortlandt's glottalic notation (ʔ ʕ ʕʷ, fortis k̑:, glottalic t’, u/i without glide "
                 "distinction) has no tested notational mapping yet",
}
# Secondary copies that duplicate a primary source: secondary work_id → primary work_id
SECONDARY_OF = {
    "schleicher-fable-schleicher-1868": "schleicher-fable-schleicher-1868",
    "schleicher-fable-byrd-2013": "schleicher-fable-byrd-2013",
    "king-and-god-byrd-nd": "king-and-god-byrd-2013",
    # Wikipedia's two Kortlandt blocks, matched by content to his 2010 paper's stages
    "schleicher-fable-kortlandt-2007": "schleicher-fable-kortlandt-2010",
    "schleicher-fable-kortlandt-2007-after-anatolian-tocharian": "schleicher-fable-kortlandt-2010-classic-ie",
}
_PARA = re.compile(r"^\(\d+\)\s*")


def load_sources(root: Path = ROOT) -> tuple[dict[str, dict], dict[str, list[dict]], dict[str, dict]]:
    """→ (chosen version per work_id, other copies per work_id, group translations).
    Copies of one work are grouped under its canonical work_id; a primary
    source is chosen over secondaries."""
    groups: dict[str, list[dict]] = {}
    group_en: dict[str, dict] = {}
    for f in sorted(root.glob("raw/tier1-*/versions.json")):
        d = json.loads(f.read_text("utf-8"))
        if d.get("english_translation"):
            grp = d["versions"][0]["work_group_id"]
            group_en.setdefault(grp, {**d["english_translation"], "from": f.parent.name})
        for v in d["versions"]:
            v["_file"] = str(f.relative_to(root))
            wid = SECONDARY_OF.get(v["work_id"], v["work_id"]) if v["confidence"] == "secondary" else v["work_id"]
            groups.setdefault(wid, []).append(v)
    chosen, others = {}, {}
    for wid, vs in groups.items():
        vs = sorted(vs, key=lambda v: v["confidence"] != "primary")
        chosen[wid], others[wid] = vs[0], vs[1:]
    return chosen, others, group_en


def _line_english(v: dict, i: int, line: dict, group: dict | None) -> tuple[str | None, str | None]:
    if line.get("english"):
        return line["english"], "source line"
    if group and len(group.get("lines", [])) == len(v["lines"]):
        en = group["lines"][i]
        if isinstance(en, dict):
            en = en.get("text") or en.get("source_form")
        return (_PARA.sub("", en) if en else None), f"group translation ({group.get('from')})"
    return None, None


def build_records(index=None, root: Path = ROOT) -> tuple[list[dict], list[dict]]:
    """→ (records, cross-check report)."""
    from .validate import load_index, validate_text
    ix = index or load_index(root)
    chosen, secondary, group_en = load_sources(root)
    records, cross = [], []
    for wid, v in sorted(chosen.items()):
        profile = PROFILE.get(wid)
        doc_reason = next((r for k, r in DOCUMENTARY_REASON.items() if k in wid), None)
        # a version is laryngealist if any of its lines writes a laryngeal
        laryngealist = any(re.search("h[₁₂₃ₓ]|H|h<sub>", ln["source_form"]) for ln in v["lines"])
        for i, line in enumerate(v["lines"]):
            src = line["source_form"]
            stripped = _PARA.sub("", src)
            notes = []
            if stripped != src:
                notes.append("editorial paragraph number stripped")
            pie, applied, validator, tokens = None, [], None, []
            if profile and not doc_reason:
                r = normalize(stripped, profile)
                applied = r.applied
                if r.canonical:
                    pie = r.text
                else:
                    notes.append("documentary: notation not mappable after normalization")
            elif doc_reason:
                notes.append("documentary: " + doc_reason)
            if pie:
                val = validate_text(pie, ix, laryngealist=laryngealist)
                tokens = [{
                    "form": t.surface,
                    "lex_id": t.analyses[0].lex_id if t.found else None,
                    "root_id": next((a.root_id for a in t.analyses if a.root_id), None),
                    "features": sorted({a.features for a in t.analyses})[:6] if t.found else [],
                    "match": t.tier, "clitic": t.clitic, "augment": t.augment,
                    "miss": t.miss, "miss_detail": t.miss_detail,
                    "verified": t.tier == "exact",
                } for t in val["tokens"]]
                validator = {k: val[k] for k in ("status", "coverage", "tiers", "misses", "unknown_roots",
                                                 "bad_forms", "agreement_warnings")}
            en, en_src = _line_english(v, i, line, group_en.get(v["work_group_id"]))
            if en_src and en_src != "source line":
                notes.append(f"english from {en_src}")
            if applied:
                notes.append("normalized: " + ",".join(applied))
            notes.append(f"source confidence: {v['confidence']}")
            records.append({
                "id": f"t1-{wid}-{i + 1:04d}",
                "tier": 1,
                "provenance": "scholarly",
                "citation": v.get("citation"),
                "work_id": wid,
                "work_group_id": v["work_group_id"],
                "line_no": i + 1,
                "pie": pie,
                "pie_ascii": to_ascii(pie) if pie else None,
                "source_form": src,
                "tokens": tokens,
                "gloss": None,
                "english": en,
                "genre": "fable",
                "theme": [],
                "syllables": measure(pie)["syllables"] if pie else None,
                "meter": None,
                "formulas": [],
                "cognate_refs": [],
                "alt_reconstructions": [],
                "validator": validator,
                "generator": None,
                "neologism": False,
                "source": {"author": v.get("author"), "year": v.get("year"), "url": v.get("url"),
                           "file": v["_file"], "confidence": v["confidence"]},
                "notes": "; ".join(notes),
            })
        for sec in secondary.get(wid, []):
            prim = _letters(" ".join(_PARA.sub("", x["source_form"]) for x in v["lines"]))
            other = _letters(" ".join(_PARA.sub("", x["source_form"]) for x in sec["lines"]))
            if prim != other:
                sm = difflib.SequenceMatcher(None, prim, other)
                diffs = [(prim[i1:i2], other[j1:j2]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
                cross.append({"work_id": wid, "secondary": sec["_file"], "similarity": round(sm.ratio(), 4),
                              "diffs": diffs[:20]})
    return records, cross


def _letters(s: str) -> str:
    """Compare copies on letters only (punctuation and markup differ between editions)."""
    return re.sub(r"[^\w]", "", normalize(s).text.lower())
