"""Phase 7 export: train/eval splits, plain-text views, task-format views.

Policy (docs/STATUS.md, open question 1 until David decides):
  eval  = every Tier 1 record with canonical `pie` (scholarly texts and formulas),
          the evaluation-grade Tier 2 lines (eval_grade), plus the held-out
          root families for the cognate and inflection tasks: hash-selected
          families that occur in NO training record (so the test is unseen
          root families across all training material; checked)
  train = Tier 2 and release-eligible Tier 3 records; pilots additionally require
          include_pilot=True. Experimental inclusion explicitly bypasses eligibility.
Cognate→PIE examples hold out *whole root families* (a deterministic hash
of root_id), so no derivative of an eval root appears in a training task.
The leakage check fails the export if any PIE string or record id is in both
splits.

Accent (docs/STATUS.md "Known limitations", data/morph/accent_unresolved.json):
every task whose target or one of whose tokens comes from a lexeme with an
unresolved accent (missing information: the headword has no accent) carries
"accent": "unresolved"; a target that is a representation exception (voc.
ph₂ter) carries "accent": "representation". Such tasks stay in the full eval
and in training. The accent-sensitive eval view (eval_tasks_accent_specified)
omits the unresolved ones; a score presented as testing fully specified accent
uses that view.
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from .batch_release import batch_eligibility
from .realize import Lexicon, accent_manifest, accent_status

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


def record_style(r: dict) -> str:
    """The reconstruction style a record's PIE follows: a named scholarly reconstruction (Tier 1,
    normalized to the project's notation but keeping its linguistic choices) or the project's own
    handbook convention (Tier 2, Tier 3). A translation benchmark must not score one as the other
    (David's review)."""
    if r.get("tier") == 1:
        return "scholarly: " + (r.get("work_id") or r.get("work_group_id") or "unnamed") + " (normalized notation)"
    return "project handbook convention"


def _record_accent(r: dict) -> str | None:
    """"unresolved" when a token of the record comes from an unresolved-accent lexeme; "representation" when a
    token is a frozen representation exception (voc. ph₂ter); None otherwise. Engine-built records (Tier 2/3)
    only: a Tier 1 text's accents are its author's, and its token lex_ids are the validator's lookups."""
    if r.get("tier") == 1:
        return None
    toks = r.get("tokens") or []
    if any(accent_status(t.get("lex_id")) == "unresolved" for t in toks):
        return "unresolved"
    exc = {(lid, cell, form) for lid, _g, cell, form in accent_manifest()["exception_cells"]}
    if any((t.get("lex_id"), str(t.get("features") or "").split("|")[0], t.get("form")) in exc for t in toks):
        return "representation"
    return None


def _target_accent(lid: str, gender: str | None, cell: str, form: str) -> str | None:
    """The accent flag of an engine-built target (inflection task)."""
    if accent_status(lid) == "unresolved":
        return "unresolved"
    if (lid, gender, cell, form) in accent_manifest()["exception_cells"]:
        return "representation"
    return None


def accent_specified(tasks: list[dict]) -> list[dict]:
    """The accent-sensitive evaluation view: the tasks without an unresolved accent (missing information)."""
    return [t for t in tasks if t.get("accent") != "unresolved"]


def record_tasks(r: dict) -> list[dict]:
    out = []
    style = record_style(r)
    if r.get("english"):
        out.append({"task": "translate_en_pie", "input": f"[style: {style}] {r['english']}", "output": r["pie"],
                    "style": style,
                    # other defensible realizations: the work's own alternative reconstructions
                    "acceptable": [r["pie"]] + [a.get("pie", a) if isinstance(a, dict) else a
                                                for a in (r.get("alt_reconstructions") or [])]})
        out.append({"task": "translate_pie_en", "input": r["pie"], "output": r["english"], "style": style})
    if r.get("gloss"):
        out.append({"task": "gloss", "input": r["pie"], "output": r["gloss"], "style": style})
    acc = _record_accent(r)
    num_fallback = any(w.get("num_fallback") == "du->pl" for w in r.get("tokens", []))
    for t in out:
        t["source_id"] = r["id"]
        if acc:
            t["accent"] = acc
        if num_fallback:
            t["num_fallback"] = "du->pl"
    return out


def token_variants(r: dict, lx) -> list[list[str]] | None:
    """Per word, the engine's alternative forms for the same cell (e.g. -éy/-ḗy locatives, -mes/-mos): a
    scorer may accept any of them. Only for engine-built records (Tier 2/3) whose tokens carry one feature
    string; None otherwise. The cell is the token's full analysis: case, number, person, tense, mood and voice
    (in `features`) and, for adjectives and participles, the resolved gender (`gender`), read through the
    lexicon's admissible cells. A token without a resolved gender (records realized before tokens carried
    it) gets no alternatives: a guessed gender offered agreement errors as acceptable (David's review:
    neuter sweh₂dú with masculine sweh₂dús)."""
    if r.get("tier") == 1:
        return None
    out = []
    for t in r.get("tokens", []):
        feat, lid = t.get("features"), t.get("lex_id") or ""
        alts = [t["form"]]
        if isinstance(feat, str) and lid in lx.specs and not lx.inadmissible(lid):
            cell, gender, fam = feat.split("|")[0], t.get("gender"), lx.specs[lid]["family"]
            try:
                if cell.startswith("PTCP."):                     # PTCP.MID.NOM.SG
                    _, voice, cell = cell.split(".", 2)
                    cells = lx.admissible_participle_cells(lid, voice, gender) if gender else {}
                elif fam == "adj":
                    cells = lx.admissible_cells(lid, gender) if gender else {}
                else:
                    cells = lx.admissible_cells(lid)
                if t["form"] in cells.get(cell, []):           # the token is the cell's form: offer the cell
                    alts = list(dict.fromkeys([t["form"]] + list(cells[cell])))
            except (KeyError, ValueError):
                pass
        out.append(alts)
    return out


GENDER_TAG = {"m": "M", "f": "F", "n": "N"}


def inflection_tasks(lx: Lexicon, rng: random.Random, per_lexeme: int = 3) -> list[dict]:
    """lemma + features → form, from the engine, for usable lexemes (primary forms only). Only admissible
    cells (Lexicon.admissible_cells: no active cells of a middle-only verb, nothing of a blocked lexeme); an
    adjective's feature names its gender first (F.NOM.SG), since the cell differs by gender."""
    out = []
    for lid, r in lx.specs.items():
        if not r.get("usable") or not lx.entries[lid]["meaning"] or lx.inadmissible(lid):
            continue
        if r["family"] == "adj":
            cells = {f"{GENDER_TAG[g]}.{f}": v for g in ("m", "f", "n") for f, v in lx.admissible_cells(lid, g).items()}
        else:
            cells = lx.admissible_cells(lid)
        feats = sorted(cells)
        tag_gender = {v: k for k, v in GENDER_TAG.items()}
        for f in rng.sample(feats, min(per_lexeme, len(feats))):
            t = {"task": "inflect", "input": f"{lx.entries[lid]['form']} {f}", "output": cells[f][0],
                 "source_id": lid, "root_id": lx.entries[lid].get("root_id")}
            g, cell = (tag_gender[f.split(".", 1)[0]], f.split(".", 1)[1]) if r["family"] == "adj" else (None, f)
            acc = _target_accent(lid, g, cell, cells[f][0])
            if acc:
                t["accent"] = acc
            out.append(t)
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
            t = {"task": "cognates_to_pie", "input": "; ".join(parts), "output": e["form"],
                 "source_id": e["id"], "root_id": e.get("root_id")}
            if accent_status(e["id"]) == "unresolved":
                t["accent"] = "unresolved"
            out.append(t)
    return out


def build(root: Path = ROOT, include_pilot: bool = False, seed: int = 0,
          experimental_batches: bool = False) -> dict:
    rng = random.Random(seed)
    tier1 = [r for r in _load("corpus/tier1/*.jsonl", root) if r.get("pie")]
    tier2 = _load("corpus/tier2/*.jsonl", root)
    # eval = Tier 1 + the evaluation-grade Tier 2 lines (judged sound by the adversarial review and
    # with a lexeme exactly attested in two branches); the other Tier 2 lines are training data
    t2_eval = [r for r in tier2 if r.get("eval_grade")]
    train_recs = [r for r in tier2 if not r.get("eval_grade")]
    tier1 = tier1 + t2_eval
    batch_decisions = []
    for f in sorted((root / "corpus" / "tier3").glob("*.jsonl")):
        decision = batch_eligibility(root, f.stem, experimental=experimental_batches)
        if f.name.startswith("pilot") and not include_pilot:
            decision = {**decision, "admitted": False,
                        "reasons": [*decision["reasons"], "pilot not requested"]}
        batch_decisions.append(decision)
        if not decision["admitted"]:
            continue
        train_recs += [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
    lx = Lexicon.load()
    train_tasks = [t for r in train_recs for t in record_tasks(r)]
    eval_tasks = []
    for r in tier1:
        for t in record_tasks(r):
            if t["task"] == "translate_en_pie":
                tv = token_variants(r, lx)
                if tv:
                    t["token_variants"] = tv
            eval_tasks.append(t)
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
    return {"train_records": train_recs, "eval_records": tier1, "train_tasks": train_tasks, "eval_tasks": eval_tasks,
            "eval_tasks_accent_specified": accent_specified(eval_tasks),
            "batch_eligibility": batch_decisions}


def views(records: list[dict]) -> dict[str, str]:
    """Plain-text views: PIE only, PIE + English, interlinear, ASCII."""
    pie = "\n".join(r["pie"] for r in records)
    par = "\n\n".join(f"{r['pie']}\n{r['english']}" for r in records if r.get("english"))
    ilg = "\n\n".join(f"{r['pie']}\n{r['gloss']}\n'{r['english']}'" for r in records if r.get("gloss"))
    asc = "\n".join(r["pie_ascii"] for r in records)
    return {"pie.txt": pie + "\n", "parallel.txt": par + "\n", "interlinear.txt": ilg + "\n", "pie_ascii.txt": asc + "\n"}
