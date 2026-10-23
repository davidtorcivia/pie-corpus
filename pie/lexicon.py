"""Build the lexicon from the kaikki.org (wiktextract) Proto-Indo-European dump.

Outputs (see docs/lexicon.md for the schema):
  data/lexicon/lexicon.jsonl     one entry per lexeme: roots, words, affixes,
                                 derivatives (from descendant trees), alt/form-of
  data/lexicon/paradigms.jsonl   Wiktionary-module inflection tables (filtered)
  data/lexicon/rejects.jsonl     every string we could not normalize, with reason
  data/lexicon/id_registry.jsonl persistent id assignments, reused on rebuild
  data/lexicon/build_report.json counts

Every PIE string goes through pie.notation.normalize and must come out
canonical. Optional elements are expanded into `variants`, and
placeholders are rejected.
"""

from __future__ import annotations

import collections
import itertools
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .notation import normalize
from .translit import is_canonical, to_ascii

SOURCE = "wiktionary"

# Placeholder or meta notation that cannot become a form.
_REJECT_PATTERNS = [
    (re.compile("[Ø∅]"), "zero-grade placeholder"),
    (re.compile("V́|V́|\\bV\\b"), "vowel placeholder V"),
    (re.compile("[TCRK](?![₁₂₃])"), "consonant placeholder"),
    (re.compile("̆"), "breve (length uncertain)"),
    (re.compile("ₔ|ə"), "schwa notation"),
    (re.compile(r"\bor\b|\?|/|,"), "alternatives list or query"),
    (re.compile(r"\.\.\.|…"), "truncated"),
]

_OPTIONAL_MOD = re.compile("⁽([ʷʰ])⁾|\\(([ʷʰ])\\)")
_OPTIONAL_SEG = re.compile(r"\(([^()]+)\)")


@dataclass
class Parsed:
    lemma: str | None              # canonical, internal hyphens removed
    segmented: str | None          # canonical, with morpheme hyphens
    variants: list[str] = field(default_factory=list)
    stems: list[str] = field(default_factory=list)
    uncertain: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    reject: str | None = None


def _strip_internal_hyphens(s: str) -> str:
    """Remove morpheme boundaries; keep a leading (affix) and trailing (bound stem) hyphen."""
    lead = s.startswith("-")
    trail = s.endswith("-") and len(s) > 1
    core = s.strip("-").replace("-", "")
    return ("-" if lead else "") + core + ("-" if trail else "")


def _expand_optional(s: str) -> tuple[list[str], list[str]]:
    """Expand ⁽ʷ⁾, (ʰ) and (seg) into all combinations. Full form first."""
    s = _OPTIONAL_MOD.sub(lambda m: "(" + (m[1] or m[2]) + ")", s)
    parts = _OPTIONAL_SEG.split(s)
    fixed, opts = parts[0::2], parts[1::2]
    tags = []
    if any(o in ("ʷ", "ʰ") for o in opts):
        tags.append("optional-modifier")
    if any(o not in ("ʷ", "ʰ") for o in opts):
        tags.append("optional-segment")
    out = []
    for choice in itertools.product([True, False], repeat=len(opts)):
        out.append("".join(f + (o if c else "") for f, o, c in itertools.zip_longest(fixed, opts, choice, fillvalue="")))
    return list(dict.fromkeys(out)), tags


def parse_form(raw: str) -> Parsed:
    s = raw.strip()
    if s.startswith("*"):
        s = s[1:]
    s = s.replace(" ~ *", " ~ ").strip()
    for rx, why in _REJECT_PATTERNS:
        if rx.search(s):
            return Parsed(None, None, reject=why)
    stems_raw = [x.strip().lstrip("*") for x in s.split("~")]
    rules: list[str] = []
    stems: list[str] = []
    variants: list[str] = []
    uncertain: list[str] = []
    for i, st in enumerate(stems_raw):
        r = normalize(st, "wiktionary")
        rules += [x for x in r.applied if x not in rules]
        expanded, tags = _expand_optional(r.text)
        uncertain += [t for t in tags if t not in uncertain]
        for v in expanded:
            if not is_canonical(v):
                return Parsed(None, None, reject=f"not canonical after normalization: {v!r}")
        if i == 0:
            variants = expanded
        stems.append(expanded[0])
    segmented = variants[0]
    lemma = _strip_internal_hyphens(segmented)
    other = [_strip_internal_hyphens(v) for v in variants[1:]]
    return Parsed(
        lemma=lemma,
        segmented=segmented if segmented != lemma else None,
        variants=[v for v in dict.fromkeys(other) if v != lemma],
        stems=[_strip_internal_hyphens(x) for x in stems] if len(stems) > 1 else [],
        uncertain=uncertain,
        rules=rules,
    )


# --- ids ---------------------------------------------------------------------

def slug(form: str) -> str:
    a = to_ascii(form)
    a = a.replace("/", "").replace("\\", "").replace("'", "j").replace(":", "x").replace("_", "")
    a = re.sub(r"[()\[\]*=\"]", "", a).strip("-").replace("-", "").replace(" ", "_")
    return a or "x"


def gloss_tag(gloss: str | None) -> str:
    if not gloss:
        return "nogloss"
    g = re.sub(r"^\(.*?\)\s*", "", gloss.strip())
    g = re.sub(r"^(to|a|an|the)\s+", "", g, flags=re.I)
    g = re.split(r"[,;:(]", g)[0]
    words = re.findall(r"[a-z0-9]+", g.lower())[:3]
    return "_".join(words) or "nogloss"


class IdRegistry:
    """Persistent key → id map, so ids survive rebuilds and dump updates."""

    def __init__(self, path: Path):
        self.path = path
        self.by_key: dict[str, str] = {}
        if path.exists():
            for line in path.read_text("utf-8").splitlines():
                rec = json.loads(line)
                self.by_key[rec["key"]] = rec["id"]
        self.used: set[str] = set()
        self.taken = set(self.by_key.values())
        self.minted = 0

    def get(self, key: str, base: str) -> str:
        if key in self.by_key:
            i = self.by_key[key]
        else:
            i, n = base, 2
            while i in self.taken:
                i, n = f"{base}-{n}", n + 1
            self.by_key[key] = i
            self.taken.add(i)
            self.minted += 1
        if i in self.used:
            raise ValueError(f"id {i} assigned twice in one build (key {key})")
        self.used.add(i)
        return i

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            for k, i in sorted(self.by_key.items(), key=lambda kv: kv[1]):
                f.write(json.dumps({"id": i, "key": k}, ensure_ascii=False) + "\n")

    def stale(self) -> list[str]:
        return sorted(set(self.by_key.values()) - self.used)


# --- builder -----------------------------------------------------------------

_POS_KIND = {"root": "root", "suffix": "affix", "prefix": "affix", "infix": "affix"}
_VERB_ENDINGS = ("ti", "tor", "toy")  # finite 3sg present / middle, segmented or not


def _glosses(row) -> list[str]:
    return [g for s in row.get("senses", []) for g in s.get("glosses", [])]


def _head_arg(row, name: str) -> str:
    for h in row.get("head_templates", []):
        if h["name"] == name:
            return h["args"].get("1", "")
    return ""


def _etymon_parts(row) -> list[dict]:
    """Morphemes from {{etymon|ine-pro|:af|*root-<id:x>|*-suffix}}; first template only."""
    for t in row.get("etymology_templates", []):
        if t["name"] != "etymon":
            continue
        args = t["args"]
        keys = sorted((k for k in args if k.isdigit() and int(k) >= 3), key=int)
        if not keys or not args.get("2", "").startswith(":"):
            return []
        parts = []
        for k in keys:
            m = re.match(r"^\*?([^<]+)((?:<[^>]*>)*)$", args[k].strip())
            if not m:
                continue
            tags = dict(re.findall(r"<(\w+):([^>]*)>", m[2]))
            parts.append({"form": m[1], "id_tag": tags.get("id"), "uncertain": "unc" in tags})
        return parts
    return []


def _reflexes(nodes) -> dict[str, list[dict]]:
    """Flatten a descendants tree to daughter forms, stopping at PIE nodes.

    `via` lists the intermediate stages (Proto-Germanic for a Gothic form,
    or a grouping label like Balto-Slavic), for the sound-law checker.
    """
    out: dict[str, list[dict]] = collections.defaultdict(list)
    seen: set[tuple] = set()

    def walk(ds, via, borrowed):
        for d in ds:
            if d.get("lang_code") == "ine-pro":
                continue
            label = d.get("lang") if d.get("lang") not in (None, "unknown") else None
            raw = d.get("raw_tags") or []
            here_borrowed = borrowed or any(t in ("borrowed", "learned borrowing", "learned") for t in raw)
            if d.get("word") and label and (label, d["word"], d.get("roman")) not in seen:
                seen.add((label, d["word"], d.get("roman")))
                rec = {"form": d["word"]}
                if d.get("roman"):
                    rec["roman"] = d["roman"]
                stages = [v for v in via if v != label]
                if stages:
                    rec["via"] = stages
                if here_borrowed:
                    rec["borrowed"] = True  # a loan, or descended from one: not a sound-law witness
                if "reshaped by analogy or addition of morphemes" in raw:
                    rec["analogical"] = True
                if "uncertain" in raw or "possibly" in (d.get("tags") or []):
                    rec["uncertain"] = True
                notes = [t for t in raw if t not in ("borrowed", "inherited", "uncertain",
                                                     "reshaped by analogy or addition of morphemes")]
                if notes:
                    rec["notes"] = notes
                out[label].append(rec)
            walk(d.get("descendants", []), via + (label,) if label else via, here_borrowed)

    walk(nodes, (), False)
    return dict(out)


def _pie_children(nodes):
    """PIE nodes directly in this tree level, or under non-PIE grouping nodes."""
    for d in nodes:
        if d.get("lang_code") == "ine-pro" and d.get("word"):
            yield d
        elif not d.get("word"):
            yield from _pie_children(d.get("descendants", []))


def build(dump: Path, outdir: Path, dump_label: str) -> dict:
    rows = [json.loads(line) for line in dump.open(encoding="utf-8")]
    reg = IdRegistry(outdir / "id_registry.jsonl")
    entries: dict[str, dict] = {}
    by_form: dict[str, list[str]] = collections.defaultdict(list)
    rejects: list[dict] = []
    rule_counts: collections.Counter = collections.Counter()
    seen_keys: collections.Counter = collections.Counter()

    def reject(raw, why, where):
        rejects.append({"raw": raw, "reason": why, "where": where})

    # Pass 1: headword entries. Roots first, so their ids are minted before words.
    rows.sort(key=lambda r: (r["pos"] != "root", r["original_title"], r.get("etymology_number", ""), r["pos"]))
    for row in rows:
        p = parse_form(row["word"])
        if p.reject:
            reject(row["word"], p.reject, row["original_title"])
            continue
        rule_counts.update(p.rules)
        gl = _glosses(row)
        senses = row.get("senses", [])
        form_of = [x["word"] for s in senses for x in (s.get("form_of") or [])]
        alt_of = [x["word"] for s in senses for x in (s.get("alt_of") or [])]
        alt_gloss = [re.sub(r"^alternative (reconstruction|form) of \*?", "", g).split(" ")[0]
                     for g in gl if g.lower().startswith(("alternative reconstruction", "alternative form"))]
        kind = _POS_KIND.get(row["pos"], "word")
        if alt_of or (alt_gloss and len(alt_gloss) == len(gl)):
            kind = "alt"
        elif form_of and len(form_of) >= len(gl):
            kind = "form"
        first = gl[0] if gl else None
        etymon_id = next((t["args"].get("id", "") for t in row.get("etymology_templates", [])
                          if t["name"] == "etymon"), "")
        key = f"{row['original_title']}|{row['pos']}|{row.get('etymology_number', '')}|{first}|{etymon_id}"
        seen_keys[key] += 1
        if seen_keys[key] > 1:
            key += f"|#{seen_keys[key]}"
        if kind == "root":
            base = f"pie-root-{slug(p.lemma)}-{gloss_tag(first)}"
        else:
            base = f"pie-lex-{slug(p.lemma)}"
        eid = reg.get(key, base)
        e = {
            "id": eid,
            "kind": kind,
            "form": p.lemma,
            "form_ascii": to_ascii(p.lemma),
            "segmented": p.segmented,
            "variants": p.variants,
            "stems": p.stems,
            "pos": row["pos"],
            "meaning": gl,
            "uncertain": p.uncertain,
            "source": SOURCE,
            "source_ref": {"dump": dump_label, "title": row["original_title"],
                           "etymology_number": row.get("etymology_number")},
            "confidence": "entry",
            "normalized": p.rules,
        }
        if kind in ("alt", "form"):
            e["target_forms"] = [x.lstrip("*") for x in (alt_of or form_of or alt_gloss)]
        if row["pos"] == "noun":
            e["gender"] = _head_arg(row, "ine-noun") or None
        asp = _head_arg(row, "ine-root") if kind == "root" else _head_arg(row, "ine-verb")
        if kind == "root":
            if asp in ("impf", "pf", "stat"):
                e["root_type"], e["root_type_source"], e["aspect"] = "verbal", "head-template", asp
            elif asp == "adj":
                e["root_type"], e["root_type_source"] = "nominal", "head-template"
            elif first and first.lower().startswith("to "):
                e["root_type"], e["root_type_source"] = "verbal", "gloss-heuristic"
            else:
                e["root_type"], e["root_type_source"] = "nominal", "gloss-heuristic"
        elif row["pos"] == "verb" and asp:
            e["aspect"] = asp
        for it in row.get("inflection_templates", [])[:1]:
            if it["args"].get("ac"):
                e["accent_class"] = it["args"]["ac"]
        e["etymon_parts"] = _etymon_parts(row)
        e["reflexes"] = _reflexes(row.get("descendants", []))
        e["_row"] = row
        entries[eid] = e
        by_form[p.lemma].append(eid)

    roots_by_form: dict[str, list[str]] = collections.defaultdict(list)
    for e in entries.values():
        if e["kind"] == "root":
            for f in [e["form"], *e["variants"]]:
                roots_by_form[f].append(e["id"])

    def etymon_roots(e) -> tuple[list[str], list[dict]]:
        found, unres = [], []
        for part in e.get("etymon_parts", []):
            pp = parse_form(part["form"])
            if pp.reject or not pp.lemma or not pp.lemma.endswith("-") or pp.lemma.startswith("-"):
                continue
            ids = roots_by_form.get(pp.lemma, [])
            if len(ids) > 1 and part["id_tag"]:
                tag = gloss_tag(part["id_tag"])
                ids = [i for i in ids if i.endswith("-" + tag)] or ids
            if len(ids) == 1:
                found.append(ids[0])
            else:
                unres.append({"entry": e["id"], "part": part["form"], "candidates": ids})
        return found, unres

    for e in entries.values():
        e["_owner_root"] = e["id"] if e["kind"] == "root" else (etymon_roots(e)[0] or [None])[0]

    # Pass 2: derivatives from descendant trees (PIE nodes). Same-form nodes
    # merge only when their trees belong to the same root (or one is unknown):
    # *kretós under *kret- "shake" and *kretós under *kret- "be strong" are two words.
    def add_derivatives(parent_id: str, nodes):
        owner_root = entries[parent_id]["_owner_root"]
        for d in _pie_children(nodes):
            p = parse_form(d["word"])
            if p.reject:
                reject(d["word"], p.reject, entries[parent_id]["source_ref"]["title"])
                add_derivatives(parent_id, d.get("descendants", []))
                continue
            rule_counts.update(p.rules)
            uncertain = list(p.uncertain) + (["marked-uncertain"] if "uncertain" in (d.get("raw_tags") or []) else [])
            existing = [i for i in by_form.get(p.lemma, [])
                        if (entries[i]["kind"] != "root" or p.lemma.endswith("-"))
                        and (owner_root is None or entries[i]["_owner_root"] in (None, owner_root))]
            if existing:
                tgt = entries[existing[0]]
                tgt.setdefault("parents", [])
                if parent_id not in tgt["parents"] and parent_id != tgt["id"]:
                    tgt["parents"].append(parent_id)
                if tgt["kind"] == "derivative":
                    for lang, refl in _reflexes(d.get("descendants", [])).items():
                        tgt["reflexes"].setdefault(lang, []).extend(
                            r for r in refl if r not in tgt["reflexes"].get(lang, []))
                    if d.get("sense") and d["sense"] not in tgt["meaning"]:
                        tgt["meaning"].append(d["sense"])
                    if p.segmented and not tgt.get("segmented"):
                        tgt["segmented"] = p.segmented
                child = tgt["id"]
            else:
                child = reg.get(f"deriv|{p.lemma}|{owner_root or ''}", f"pie-lex-{slug(p.lemma)}")
                entries[child] = {
                    "id": child, "kind": "derivative", "form": p.lemma, "form_ascii": to_ascii(p.lemma),
                    "segmented": p.segmented, "variants": p.variants, "stems": p.stems, "pos": None,
                    "meaning": [d["sense"]] if d.get("sense") else [], "uncertain": uncertain,
                    "source": SOURCE,
                    "source_ref": {"dump": dump_label, "title": entries[parent_id]["source_ref"]["title"],
                                   "tree_path": True},
                    "confidence": "derivative" if "marked-uncertain" not in uncertain else "uncertain",
                    "normalized": p.rules, "parents": [parent_id],
                    "reflexes": _reflexes(d.get("descendants", [])),
                    "_owner_root": owner_root,
                }
                by_form[p.lemma].append(child)
            entries[parent_id].setdefault("derivatives", [])
            if child not in entries[parent_id]["derivatives"] and child != parent_id:
                entries[parent_id]["derivatives"].append(child)
            add_derivatives(child, d.get("descendants", []))

    for eid in [i for i in entries if entries[i]["kind"] != "derivative"]:
        add_derivatives(eid, entries[eid]["_row"].get("descendants", []))

    # Pass 3: resolve morphemes and roots.
    unresolved = []
    for e in entries.values():
        if e["kind"] == "root":
            e["root_id"] = e["id"]
            continue
        if e["kind"] in ("alt", "form"):
            tgt = [i for f in e.get("target_forms", []) for i in by_form.get(_strip_internal_hyphens(f), [])]
            e["target_ids"] = tgt
            e["root_id"] = next((i for i in tgt if entries[i]["kind"] == "root"), None)
            continue
        cands, unres = etymon_roots(e)
        unresolved += unres
        if not cands:
            # Fall back on the tree: nearest root ancestor through parents.
            seen, stack = set(), list(e.get("parents", []))
            while stack:
                pid = stack.pop(0)
                if pid in seen or pid not in entries:
                    continue
                seen.add(pid)
                if entries[pid]["kind"] == "root":
                    cands.append(pid)
                    break
                stack.extend(entries[pid].get("parents", []))
            e["root_link_source"] = "tree" if cands else None
        else:
            e["root_link_source"] = "etymon"
        e["root_id"] = cands[0] if cands else None
        if len(cands) > 1:
            e["root_ids"] = list(dict.fromkeys(cands))

    # alt/form-of entries inherit the root of their target (now resolved).
    for e in entries.values():
        if e["kind"] in ("alt", "form") and not e["root_id"]:
            e["root_id"] = next((entries[t]["root_id"] for t in e["target_ids"] if entries[t].get("root_id")), None)

    # Second root-type signal: a finite verb among a root's derivatives.
    disagreements = []
    for e in entries.values():
        if e["kind"] != "root":
            continue
        has_verb = any(
            entries[c]["pos"] == "verb" or (entries[c]["kind"] == "derivative" and
                                            entries[c]["form"].endswith(_VERB_ENDINGS))
            for c in e.get("derivatives", []) if c in entries)
        e["has_verb_derivative"] = has_verb
        if e["root_type_source"] == "gloss-heuristic" and (e["root_type"] == "verbal") != has_verb:
            disagreements.append(e["id"])

    # LIV² (committed facts file data/lexicon/liv2.jsonl, built from the book by scripts/build_liv.py)
    liv_report = None
    liv_path = outdir / "liv2.jsonl"
    if liv_path.exists():
        from .liv import apply as apply_liv
        recs = [json.loads(x) for x in liv_path.read_text("utf-8").splitlines() if x.strip()]
        liv_report = apply_liv(entries, recs, reg)

    # Paradigms (Wiktionary module output), hard-filtered.
    paradigms, para_skipped = [], collections.Counter()
    for e in entries.values():
        row = e.get("_row")
        if not row or not row.get("inflection_templates"):
            continue
        tmpls = row["inflection_templates"]
        if any(re.search(r"[(Ø∅~/]", v) for t in tmpls for v in t["args"].values()):
            para_skipped["parenthesized/zero-grade template args"] += 1
            continue
        cells: dict[tuple, list[str]] = {}
        ok = True
        for f in row.get("forms", []):
            if f.get("source") != "inflection" or {"table-tags", "inflection-template"} & set(f.get("tags", [])):
                continue
            if f["form"] == "-":
                continue
            v = f["form"].lstrip("*")
            if not is_canonical(v):
                ok = False
                break
            cells.setdefault(tuple(sorted(f["tags"])), [])
            if v not in cells[tuple(sorted(f["tags"]))]:
                cells[tuple(sorted(f["tags"]))].append(v)
        if not ok:
            para_skipped["non-canonical cell"] += 1
            continue
        if cells:
            paradigms.append({
                "lex_id": e["id"], "form": e["form"], "pos": e["pos"],
                "templates": [{"name": t["name"], "args": t["args"]} for t in tmpls],
                "accent_class": e.get("accent_class"),
                "cells": [{"tags": list(k), "forms": v} for k, v in cells.items()],
                "source": "wiktionary-module",
            })

    for e in entries.values():
        e.pop("_row", None)
        e.pop("_owner_root", None)
        for k in ("segmented", "gender", "root_type_source", "root_link_source"):
            if e.get(k) is None:
                e.pop(k, None)

    outdir.mkdir(parents=True, exist_ok=True)
    order = sorted(entries.values(), key=lambda e: ({"root": 0, "word": 1, "affix": 2, "form": 3, "alt": 4,
                                                     "derivative": 5}[e["kind"]], e["id"]))
    _write_jsonl(outdir / "lexicon.jsonl", order)
    _write_jsonl(outdir / "paradigms.jsonl", paradigms)
    _write_jsonl(outdir / "rejects.jsonl", rejects)
    reg.save()

    kinds = collections.Counter(e["kind"] for e in entries.values())
    roots = [e for e in entries.values() if e["kind"] == "root"]
    report = {
        "dump": dump_label,
        "entries": len(entries),
        "by_kind": dict(kinds),
        "glossed_entries": sum(1 for e in entries.values() if e["meaning"]),
        "roots": len(roots),
        "verbal_roots": {
            "total": sum(1 for r in roots if r["root_type"] == "verbal"),
            "head_template": sum(1 for r in roots if r["root_type"] == "verbal" and r["root_type_source"] == "head-template"),
            "gloss_heuristic": sum(1 for r in roots if r["root_type"] == "verbal" and r["root_type_source"] == "gloss-heuristic"),
            "liv2": sum(1 for r in roots if r["root_type"] == "verbal" and r["root_type_source"] == "liv2"),
            "with_liv2_entry": sum(1 for r in roots if r.get("liv")),
            "with_verb_derivative": sum(1 for r in roots if r["has_verb_derivative"]),
        },
        "root_type_disagreements": disagreements,
        "non_root_without_root_link": sum(1 for e in entries.values()
                                          if e["kind"] in ("word", "derivative") and not e.get("root_id")),
        "unresolved_etymon_parts": unresolved,
        "paradigms": len(paradigms),
        "paradigms_skipped": dict(para_skipped),
        "rejects": len(rejects),
        "rejects_by_reason": dict(collections.Counter(r["reason"].split(":")[0] for r in rejects)),
        "normalization_rules_fired": dict(rule_counts),
        "w_escape_forms": sum(1 for e in entries.values() if "\\w" in e["form_ascii"]),
        "liv2": liv_report,
        "ids_minted_this_build": reg.minted,
        "stale_registry_ids": reg.stale(),
    }
    (outdir / "build_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return report


def _write_jsonl(path: Path, recs) -> None:
    with path.open("w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
