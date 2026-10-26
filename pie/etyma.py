"""Opt-in research etyma. Never load these into a production Lexicon."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

from .research_scope import RESEARCH_ONLY

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = "data/research/formulas/etyma.jsonl"
REQUIRED = {"id", "kind", "form", "source_forms", "sense", "sources", "uncertainty", "scope"}
OPTIONAL = {"homograph", "cross_link", "note"}
SOURCE_DIRS = {"EDHIL": "kloekhorst-hitt", "LIV2": "liv2", "Beekes": "beekes-edg"}


def validate(entry: dict) -> None:
    missing, unknown = REQUIRED - entry.keys(), entry.keys() - REQUIRED - OPTIONAL
    if missing or unknown:
        raise ValueError(f"etymon schema: missing {sorted(missing)}, unknown {sorted(unknown)}")
    if not re.fullmatch(r"research-etymon-[a-z0-9]+(?:-[a-z0-9]+)*", entry["id"]):
        raise ValueError("invalid research etymon id")
    if entry["scope"] != RESEARCH_ONLY or entry["kind"] not in {"root", "noun", "adj", "other"}:
        raise ValueError("invalid etymon scope or kind")
    form = entry["form"]
    if not isinstance(form, str) or not form or unicodedata.normalize("NFC", form) != form:
        raise ValueError("canonical form must be nonempty NFC")
    if "ḫ" in form or "?" in form or any(ord(c) < 32 for c in form):
        raise ValueError("canonical form must be a reviewed PIE reconstruction")
    if not isinstance(entry["sense"], str) or not entry["sense"].strip():
        raise ValueError("sense required")
    if not isinstance(entry["uncertainty"], list) or not all(isinstance(x, str) for x in entry["uncertainty"]):
        raise ValueError("uncertainty must be a list of notes")
    if not isinstance(entry["source_forms"], list) or not entry["source_forms"] or not all(
        isinstance(x, str) and x.strip() and not any(ord(c) < 32 for c in x)
        for x in entry["source_forms"]):
        raise ValueError("source forms required without damaged control glyphs")
    if any("?" in x for x in entry["source_forms"]) and not any(
        x.strip() for x in entry["uncertainty"]
    ):
        raise ValueError("doubtful source forms require an explicit uncertainty note")
    if not isinstance(entry["sources"], list) or not entry["sources"]:
        raise ValueError("sources required")
    for source in entry["sources"]:
        if set(source) != {"source", "page", "text_file"} or source["source"] not in SOURCE_DIRS:
            raise ValueError("unknown source schema")
        book = SOURCE_DIRS[source["source"]]
        if type(source["page"]) is not int or source["page"] < 1 or not re.fullmatch(
            rf"raw/books/text/{book}/p[0-9]{{4}}\.txt", source["text_file"]):
            raise ValueError("printed page and source text path required")
    if "homograph" in entry and (type(entry["homograph"]) is not int or entry["homograph"] < 1):
        raise ValueError("homograph must be a positive source number")
    if "cross_link" in entry:
        link = entry["cross_link"]
        if set(link) != {"root_id", "note"} or not link["root_id"].startswith("pie-root-") or not link["note"].strip():
            raise ValueError("cross-link needs a production root and review note")


def load_registry(root: Path = ROOT) -> dict[str, dict]:
    """Explicit load; validate all rows and reject duplicate stable ids. No raw text is read."""
    out = {}
    for line in (Path(root) / REGISTRY).read_text("utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        validate(entry)
        if entry["id"] in out:
            raise ValueError(f"duplicate research etymon: {entry['id']}")
        out[entry["id"]] = entry
    return out


def research_group_map(lexicon: list[dict], registry: dict[str, dict]) -> dict[str, str]:
    """Explicit retrieval adapter. Cross-links are metadata, never group aliases."""
    from .formula_search import group_map
    groups = group_map(lexicon)
    roots = {e["id"] for e in lexicon if e.get("kind") == "root"}
    for key, entry in registry.items():
        validate(entry)
        if key != entry["id"] or key in groups:
            raise ValueError("registry key mismatch or production id collision")
        if "cross_link" in entry and entry["cross_link"]["root_id"] not in roots:
            raise ValueError("cross-link does not name an existing production root")
        groups[key] = key
    return groups
