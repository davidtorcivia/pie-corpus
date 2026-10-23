"""Regenerate Wiktionary's inflection tables with the engine and compare cells.

This is the Phase 2 acceptance harness. The Wiktionary tables are one
independent implementation (a Lua module), so agreement means the engine
reproduces it. Each mismatch class is triaged in docs/morphology.md as a
convention difference, a Wiktionary idiosyncrasy, or an engine bug, and the
engine-bug class must reach zero.
"""

from __future__ import annotations

import collections
import json
from pathlib import Path

from .morph import AdjSpec, NounSpec, VerbSpec, conjugate, decline, decline_adj

_CASE = {"nominative": "NOM", "vocative": "VOC", "accusative": "ACC", "genitive": "GEN",
         "ablative": "ABL", "dative": "DAT", "locative": "LOC", "instrumental": "INS"}
_NUM = {"singular": "SG", "dual": "DU", "plural": "PL"}
_PERSON = {"first-person": "1", "second-person": "2", "third-person": "3"}
_SKIP_VERB = {"subjunctive", "optative", "participle"}


def _split(v: str | None) -> list[str]:
    return [x.strip().lstrip("*") for x in v.split(",")] if v else []


def noun_feature(tags: list[str]) -> str | None:
    if "collective" in tags:
        return None
    c = [_CASE[t] for t in tags if t in _CASE]
    n = [_NUM[t] for t in tags if t in _NUM]
    return f"{c[0]}.{n[0]}" if len(c) == 1 and len(n) == 1 else None


def verb_feature(tags: list[str], kind: str) -> str | None:
    if _SKIP_VERB & set(tags):
        return None
    p = [_PERSON[t] for t in tags if t in _PERSON]
    n = [_NUM[t] for t in tags if t in _NUM]
    if len(p) != 1 or len(n) != 1:
        return None
    if "imperative" in tags:
        mood = "IMP"
    elif kind == "impf":
        mood = "PRS" if "present" in tags else "PST" if "past" in tags else None
    else:
        mood = {"pf": "AOR", "stat": "PRF"}[kind]
    return f"{mood}.{p[0]}{n[0]}" if mood else None


def _engine_one(t: dict) -> tuple[str, dict[str, list[str]], str] | None:
    name, a = t["name"], t["args"]
    if any(" " in v for k, v in a.items() if k.isdigit()):
        return None  # phrases are out of scope
    if name in ("ine-decl-noun-mf", "ine-decl-noun-n"):
        strong = a["1"]
        gender = "n" if name.endswith("-n") else ("f" if strong.endswith(("eh₂", "éh₂")) else "m")
        spec = NounSpec(strong, a.get("2"), a.get("ac"), gender,
                        nom_sg=_split(a.get("nom_sg"))[0] if a.get("nom_sg") else None,
                        loc_sg=_split(a.get("loc_sg")))
        return "noun", decline(spec, "wiktionary", alternatives=False), "exact"
    if name == "ine-decl-adj":
        spec = AdjSpec(a["1"], a.get("2"), a.get("3"), a.get("4"), a.get("ac"), _split(a.get("loc_sg")))
        by_g = decline_adj(spec, "wiktionary", alternatives=False)
        cells: dict[str, list[str]] = collections.defaultdict(list)
        for g in ("m", "f", "n"):
            for k, v in by_g[g].items():
                cells[k] += [x for x in v if x not in cells[k]]
        return "adj", dict(cells), "exact"
    if name.startswith("ine-conj-"):
        kind = name.removeprefix("ine-conj-")
        spec = VerbSpec(a["1"], a.get("2"), kind)
        return f"verb-{kind}", conjugate(spec, "wiktionary", alternatives=False), \
            "exact" if a.get("v") == "actv" else "active-subset"
    return None


def engine_cells(para: dict) -> tuple[str, dict[str, list[str]], str] | None:
    """Engine output for a paradigm record: (family, cells, compare mode).
    A page with several templates (e.g. proterokinetic and hysterokinetic
    variants of one adjective) shows their union, so the engine output is too."""
    results = [r for r in (_engine_one(t) for t in para["templates"]) if r]
    if not results:
        return None
    family, mode = results[0][0], results[0][2]
    cells: dict[str, list[str]] = collections.defaultdict(list)
    for _, c, _ in results:
        for k, v in c.items():
            cells[k] += [x for x in v if x not in cells[k]]
    return family, dict(cells), mode


def compare(paradigms: list[dict]) -> dict:
    stats = collections.defaultdict(lambda: collections.Counter())
    mismatches = []
    for para in paradigms:
        got = engine_cells(para)
        t = para["templates"][0]
        group = f"{t['name']}|{para.get('accent_class') or '-'}"
        if got is None or para["form"].endswith(("tor", "toy")):  # middle-only verbs: Phase B
            stats[group]["out_of_scope_tables"] += 1
            continue
        family, cells, mode = got
        kind = t["name"].removeprefix("ine-conj-")
        heteroclite = any("coll" in a for tt in para["templates"] for a in tt["args"])
        table_ok = True
        for cell in para["cells"]:
            feat = verb_feature(cell["tags"], kind) if family.startswith("verb") else noun_feature(cell["tags"])
            if feat is None or (heteroclite and not feat.endswith(".SG")):
                stats[group]["cells_out_of_scope"] += 1   # collectives / heteroclite plurals: Phase B
                continue
            # Suffix tables: the engine does not carry the leading hyphen.
            want, have = [f.replace("-", "") for f in cell["forms"]], cells.get(feat, [])
            if mode == "exact":
                ok = set(want) == set(have)
            else:  # Wiktionary lists active then middle in one cell
                ok = bool(have) and want[0] in have and set(have) <= set(want)
            stats[group]["cells_ok" if ok else "cells_bad"] += 1
            if not ok:
                table_ok = False
                mismatches.append({"lex_id": para["lex_id"], "form": para["form"], "template": t["name"],
                                   "args": t["args"], "feature": feat, "wiktionary": want, "engine": have})
        stats[group]["tables_ok" if table_ok else "tables_bad"] += 1
    total = collections.Counter()
    for c in stats.values():
        total.update(c)
    return {"by_group": {k: dict(v) for k, v in sorted(stats.items())}, "total": dict(total),
            "mismatches": mismatches}


def run(paradigms_path: Path) -> dict:
    paras = [json.loads(line) for line in paradigms_path.read_text("utf-8").splitlines()]
    return compare(paras)
