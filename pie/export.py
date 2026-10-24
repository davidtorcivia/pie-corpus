"""Phase 7 export: train/eval splits, plain-text views, task-format views.

Policy (docs/STATUS.md, open question 1 until David decides):
  eval  = every Tier 1 record with canonical `pie` (scholarly texts and formulas),
          the evaluation-grade Tier 2 lines (eval_grade), plus the held-out
          root families for the cognate and inflection tasks: hash-selected
          families that occur in NO training record (so the test is unseen
          root families across all training material; checked)
  train = Tier 2 and Tier 3 records; batches named pilot-* only with
          include_pilot=True (unreviewed)
Cognate→PIE examples hold out *whole root families* (a deterministic hash
of root_id), so no derivative of an eval root appears in a training task.
The leakage check fails the export if any PIE string or record id is in both
splits.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from .realize import Lexicon

ROOT = Path(__file__).resolve().parent.parent
COGNATE_LANGS = ["Sanskrit", "Ancient Greek", "Latin", "Proto-Germanic", "Hittite", "Old Irish", "Gothic",
                 "Avestan", "Old Church Slavonic", "Lithuanian", "Tocharian B", "Old Armenian"]


def eval_root(root_id: str | None, share: float = 0.10) -> bool:
    if not root_id:
        return False
    h = int(hashlib.sha256(root_id.encode()).hexdigest()[:8], 16)
    return h / 0xFFFFFFFF < share


def train_root_ids(records: list[dict], lx) -> set[str]:
    """Root families that occur anywhere in the given records' tokens (lexeme → root_id; a root
    lexeme counts as its own family)."""
    out = set()
    for r in records:
        for t in r.get("tokens", []):
            lid = t.get("lex_id") or ""
            rid = t.get("root_id") or lx.entries.get(lid, {}).get("root_id")
            if rid:
                out.add(rid)
            elif lid.startswith("pie-root-"):
                out.add(lid)
    return out


def _load(globpat: str, root: Path) -> list[dict]:
    recs = []
    for f in sorted(root.glob(globpat)):
        recs += [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
    return recs


def record_tasks(r: dict) -> list[dict]:
    out = []
    if r.get("english"):
        out.append({"task": "translate_en_pie", "input": r["english"], "output": r["pie"]})
        out.append({"task": "translate_pie_en", "input": r["pie"], "output": r["english"]})
    if r.get("gloss"):
        out.append({"task": "gloss", "input": r["pie"], "output": r["gloss"]})
    for t in out:
        t["source_id"] = r["id"]
    return out


def inflection_tasks(lx: Lexicon, rng: random.Random, per_lexeme: int = 3) -> list[dict]:
    """lemma + features → form, from the engine, for usable lexemes (primary forms only)."""
    out = []
    for lid, r in lx.specs.items():
        if not r.get("usable") or not lx.entries[lid]["meaning"]:
            continue
        cells = lx.cells(lid) if r["family"] != "adj" else lx.cells(lid, "m")
        feats = sorted(cells)
        for f in rng.sample(feats, min(per_lexeme, len(feats))):
            out.append({"task": "inflect", "input": f"{lx.entries[lid]['form']} {f}", "output": cells[f][0],
                        "source_id": lid, "root_id": lx.entries[lid].get("root_id")})
    return out


def cognate_tasks(lx: Lexicon) -> list[dict]:
    """Cognate set (≥2 daughters, no loans or analogical forms) → PIE lemma."""
    out = []
    for e in lx.entries.values():
        refl = e.get("reflexes", {})
        parts = []
        for lang in COGNATE_LANGS:
            forms = [x for x in refl.get(lang, []) if not (x.get("borrowed") or x.get("analogical"))]
            if forms:
                parts.append(f"{lang} {forms[0].get('roman') or forms[0]['form']}")
        if len(parts) >= 2:
            out.append({"task": "cognates_to_pie", "input": "; ".join(parts), "output": e["form"],
                        "source_id": e["id"], "root_id": e.get("root_id")})
    return out


def build(root: Path = ROOT, include_pilot: bool = False, seed: int = 0) -> dict:
    rng = random.Random(seed)
    tier1 = [r for r in _load("corpus/tier1/*.jsonl", root) if r.get("pie")]
    tier2 = _load("corpus/tier2/*.jsonl", root)
    # eval = Tier 1 + the evaluation-grade Tier 2 lines (judged sound by the adversarial review and
    # with a lexeme exactly attested in two branches); the other Tier 2 lines are training data
    t2_eval = [r for r in tier2 if r.get("eval_grade")]
    train_recs = [r for r in tier2 if not r.get("eval_grade")]
    tier1 = tier1 + t2_eval
    for f in sorted((root / "corpus" / "tier3").glob("*.jsonl")):
        if f.name.startswith("pilot") and not include_pilot:
            continue
        train_recs += [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
    lx = Lexicon.load()
    train_tasks = [t for r in train_recs for t in record_tasks(r)]
    eval_tasks = [t for r in tier1 for t in record_tasks(r)]
    # held-out root families must be unseen in ALL training material, not only in the cognate and
    # inflection tasks: a family the hash selects but that occurs in a training sentence goes to train
    # (David's review: deyḱ- was held out of the cognate task while training sentences inflected it)
    seen_roots = train_root_ids(train_recs, lx)
    held = lambda rid: eval_root(rid) and rid not in seen_roots
    for t in inflection_tasks(lx, rng) + cognate_tasks(lx):
        (eval_tasks if held(t.get("root_id")) else train_tasks).append(t)
    bad = [t for t in train_tasks if held(t.get("root_id"))]
    if bad:
        raise ValueError(f"held-out root family in training tasks: {bad[0].get('root_id')}")
    # leakage check
    train_pie = {r["pie"] for r in train_recs}
    leak = sorted({r["pie"] for r in tier1} & train_pie)
    ids = {r["id"] for r in tier1} & {r["id"] for r in train_recs}
    if leak or ids:
        raise ValueError(f"eval leakage: {len(leak)} shared PIE strings, {len(ids)} shared ids, e.g. {leak[:3]}")
    # an eval line found verbatim inside a training text (Tier 3 reuses the formula menu on purpose):
    # kept in eval but flagged, so a benchmark can report scores with and without them
    big = "\n".join(r["pie"] for r in train_recs)
    seen = {r["id"] for r in tier1 if len(r["pie"].rstrip(".").split()) >= 2 and r["pie"].rstrip(".").strip() in big}
    tier1 = [{**r, "seen_in_train": r["id"] in seen} for r in tier1]
    eval_tasks = [{**t, "seen_in_train": t.get("source_id") in seen} if "source_id" in t else t for t in eval_tasks]
    return {"train_records": train_recs, "eval_records": tier1, "train_tasks": train_tasks, "eval_tasks": eval_tasks}


def views(records: list[dict]) -> dict[str, str]:
    """Plain-text views: PIE only, PIE + English, interlinear, ASCII."""
    pie = "\n".join(r["pie"] for r in records)
    par = "\n\n".join(f"{r['pie']}\n{r['english']}" for r in records if r.get("english"))
    ilg = "\n\n".join(f"{r['pie']}\n{r['gloss']}\n'{r['english']}'" for r in records if r.get("gloss"))
    asc = "\n".join(r["pie_ascii"] for r in records)
    return {"pie.txt": pie + "\n", "parallel.txt": par + "\n", "interlinear.txt": ilg + "\n", "pie_ascii.txt": asc + "\n"}
