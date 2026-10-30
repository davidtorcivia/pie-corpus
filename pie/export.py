"""Phase 7 export: train/eval splits, plain-text views, task-format views.

Policy (docs/STATUS.md, open question 1 until David decides):
  eval  = every Tier 1 record with canonical `pie` (scholarly texts and formulas),
          the evaluation-grade Tier 2 lines (eval_grade), plus the drill split: the
          inflection and cognate tasks of about 5% of lexemes (eval_drill, a sha256 rank
          of the lexeme id). Those lexemes still occur in training texts; only their
          drills are kept back, so the score tests whether the model inflects a word it
          was never drilled on. No root family is held out of training (owner, 2026-10-30;
          the family hold-out of 2026-10-28/29 is kept in data/export/held_roots.json
          as "held_before_2026-10-30")
  train = Tier 2 and release-eligible Tier 3 records; pilots additionally require
          include_pilot=True. Experimental inclusion explicitly bypasses eligibility.
  conversational eval = the whole dialogue records frozen in data/export/held_dialogues.json (one
          approved batch's dialogues), taken out of train (eval_dialogue_records): they make no task
          and no text view, only the chat/eval.jsonl conversations (pie.export_chat, export/README.md "Chat export")
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

Project reconstructions (data/lexicon/project_reconstructions.jsonl, PLAN.md):
every task from a record with a token from one, and every inflection task of
one, carries "coined": "project". They are training data only: their
inflection tasks never go to eval (and are dropped when their root family is
held out), they make no cognate→PIE task (the answer
would be our own projection), and an evaluation record with such a token
fails the export.

Tier 3b, "modern PIE" (corpus/tier3b/, records with neologism: true; PLAN.md "Tier 3b"): admitted through the
same release eligibility as Tier 3, training only. Every task of a Tier 3b record carries "neologism": true,
and "coined": "neologism" when a token is a neologism (data/lexicon/neologisms.jsonl, pie/neologism.py).
Neologisms are not in the default Lexicon, so they make no inflection or cognate task. The cap: Tier 3b words
are at most NEOLOGISM_CAP (15%) of the training records' words (pie.export_chat.neologism_share, the one
count) or the build fails; above NEOLOGISM_WARN (10%) the result says so (`neologism_share.status`).
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from .batch_release import batch_eligibility
from .realize import Lexicon, accent_manifest, accent_status

ROOT = Path(__file__).resolve().parent.parent
NEOLOGISM_WARN = 0.10       # PLAN.md: Tier 3b at most 10-15% of training tokens; the hard cap is
                            # pie.export_chat.NEOLOGISM_CAP (0.15)
COGNATE_LANGS = ["Sanskrit", "Ancient Greek", "Latin", "Proto-Germanic", "Hittite", "Old Irish", "Gothic",
                 "Avestan", "Old Church Slavonic", "Lithuanian", "Tocharian B", "Old Armenian"]


EVAL_DRILL_SHARE = 0.05


def eval_drill(lex_id: str | None) -> bool:
    """Do this lexeme's inflection and cognate tasks go to eval? A stable sha256 rank under EVAL_DRILL_SHARE.
    The lexeme itself stays trainable everywhere else (texts, slices, translation)."""
    from .holdout import hash_rank
    return bool(lex_id) and hash_rank(lex_id) < EVAL_DRILL_SHARE


def eval_root(root_id: str | None) -> bool:
    """Is this root family held out of training? Membership in the frozen list data/export/held_roots.json,
    which has been empty since 2026-10-30 (owner: no vocabulary is withheld). Kept as the one predicate
    make_slice, neologism and export ask, so a future hold-out needs only the list."""
    from .holdout import held_roots
    from .research_scope import mapping_scope, RESEARCH_ONLY
    if mapping_scope((root_id,)) == RESEARCH_ONLY:
        raise ValueError("research_only id cannot enter evaluation holdouts")
    if not root_id:
        return False
    return root_id in held_roots()


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
    from .research_scope import mapping_scope, RESEARCH_ONLY
    for item in (r, *r.get("tokens", [])):
        if mapping_scope((item.get("id"), item.get("lex_id"), item.get("root_id")), item.get("scope")) == RESEARCH_ONLY:
            raise ValueError("research_only record cannot enter export")
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
    # a coined token (pie.realize.Lexicon.coined: a project reconstruction or a neologism) marks every task of its
    # record; a neologism wins over a project reconstruction when a record has both
    flags = {w["coined"] for w in r.get("tokens", []) if w.get("coined")}
    coined = "neologism" if "neologism" in flags else next(iter(sorted(flags)), None)
    tier3b = r.get("neologism") is True
    for t in out:
        t["source_id"] = r["id"]
        if acc:
            t["accent"] = acc
        if num_fallback:
            t["num_fallback"] = "du->pl"
        if coined:
            t["coined"] = coined
        if tier3b:
            t["neologism"] = True
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
            if lx.coined(lid):
                t["coined"] = lx.coined(lid)
            out.append(t)
    return out


def cognate_tasks(lx: Lexicon) -> list[dict]:
    """Cognate set (≥2 daughters, no loans or analogical forms) → PIE lemma."""
    from .research_scope import research_entry
    out = []
    for e in lx.entries.values():
        if research_entry(e):
            raise ValueError("research_only entry in cognate export")
        if e.get("coined"):
            continue      # a project reconstruction's lemma is our projection, not a handbook answer
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
    # Tier 3b dialogues where the model calls itself a machine (data/export/persona_excluded.json)
    persona_excluded = set(json.loads((Path(root) / "data/export/persona_excluded.json").read_text("utf-8"))["records"]) \
        if (Path(root) / "data/export/persona_excluded.json").exists() else set()
    for f in sorted((root / "corpus" / "tier3").glob("*.jsonl")):
        decision = batch_eligibility(root, f.stem, experimental=experimental_batches)
        if f.name.startswith("pilot") and not include_pilot:
            decision = {**decision, "admitted": False,
                        "reasons": [*decision["reasons"], "pilot not requested"]}
        batch_decisions.append(decision)
        if not decision["admitted"]:
            continue
        train_recs += [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
    # Tier 3b ("modern PIE"): the same release eligibility; training only
    for f in sorted((root / "corpus" / "tier3b").glob("*.jsonl")):
        decision = batch_eligibility(root, f.stem, experimental=experimental_batches)
        batch_decisions.append(decision)
        if not decision["admitted"]:
            continue
        recs = [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
        recs = [r for r in recs if r["id"] not in persona_excluded]
        bad3b = [r["id"] for r in recs if r.get("neologism") is not True or r.get("tier") != 3]
        if bad3b:
            raise ValueError(f"a corpus/tier3b record needs tier 3 and neologism: true: {bad3b[0]}")
        train_recs += recs
    # the conversational eval (data/export/held_dialogues.json, pie.export_chat.held_dialogue_ids): whole dialogue
    # records reserved from training; they feed only chat/eval.jsonl, never a task or a text view
    from .export_chat import held_dialogue_ids
    held_dia = held_dialogue_ids(root)
    eval_dialogues = [r for r in train_recs if r["id"] in held_dia]
    train_recs = [r for r in train_recs if r["id"] not in held_dia]
    neo_share = neologism_cap(train_recs)
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
    seen_roots = train_root_ids(train_recs, lx)
    held = lambda rid: eval_root(rid) and rid not in seen_roots      # empty list: never true (eval_root)
    for t in inflection_tasks(lx, rng) + cognate_tasks(lx):
        # a project reconstruction never enters evaluation (PLAN.md "Project reconstructions")
        if t.get("coined"):
            if not held(t.get("root_id")):
                train_tasks.append(t)
            continue
        (eval_tasks if held(t.get("root_id")) or eval_drill(t.get("source_id")) else train_tasks).append(t)
    coined_eval = [r["id"] for r in tier1 if r.get("neologism") or any(t.get("coined") for t in r.get("tokens") or [])]
    if coined_eval:
        raise ValueError(f"project reconstruction or neologism in an evaluation record: {coined_eval[0]}")
    bad = [t for t in train_tasks if held(t.get("root_id"))]
    if bad:
        raise ValueError(f"held-out root family in training tasks: {bad[0].get('root_id')}")
    # leakage check
    train_pie = {r["pie"] for r in train_recs}
    leak = sorted({r["pie"] for r in tier1 + eval_dialogues} & train_pie)
    ids = {r["id"] for r in tier1 + eval_dialogues} & {r["id"] for r in train_recs}
    if leak or ids:
        raise ValueError(f"eval leakage: {len(leak)} shared PIE strings, {len(ids)} shared ids, e.g. {leak[:3]}")
    # an eval line found verbatim inside a training text (Tier 3 reuses the formula menu on purpose):
    # kept in eval but flagged, so a benchmark can report scores with and without them
    big = "\n".join(r["pie"] for r in train_recs)
    seen = {r["id"] for r in tier1 if len(r["pie"].rstrip(".").split()) >= 2 and r["pie"].rstrip(".").strip() in big}
    tier1 = [{**r, "seen_in_train": r["id"] in seen} for r in tier1]
    eval_tasks = [{**t, "seen_in_train": t.get("source_id") in seen} if "source_id" in t else t for t in eval_tasks]
    return {"train_records": train_recs, "eval_records": tier1, "train_tasks": train_tasks, "eval_tasks": eval_tasks,
            "eval_tasks_accent_specified": accent_specified(eval_tasks), "eval_dialogue_records": eval_dialogues,
            "batch_eligibility": batch_decisions, "neologism_share": neo_share}


def neologism_cap(train_records: list[dict]) -> dict:
    """The Tier 3b share of the training records' words (pie.export_chat.neologism_share) with a status: "ok",
    "warn" above NEOLOGISM_WARN; above the cap (pie.export_chat.NEOLOGISM_CAP) the export fails (PLAN.md)."""
    from .export_chat import neologism_share
    s = neologism_share(train_records)
    if s["exceeded"]:
        raise ValueError(f"Tier 3b neologism share {s['share']:.1%} of training words exceeds the {s['cap']:.0%} "
                         f"cap (PLAN.md 'Tier 3b'): admit fewer Tier 3b batches or more archaic text")
    return {**s, "warn_at": NEOLOGISM_WARN, "status": "warn" if s["share"] > NEOLOGISM_WARN else "ok"}


def views(records: list[dict]) -> dict[str, str]:
    """Plain-text views: PIE only, PIE + English, interlinear, ASCII."""
    pie = "\n".join(r["pie"] for r in records)
    par = "\n\n".join(f"{r['pie']}\n{r['english']}" for r in records if r.get("english"))
    ilg = "\n\n".join(f"{r['pie']}\n{r['gloss']}\n'{r['english']}'" for r in records if r.get("gloss"))
    asc = "\n".join(r["pie_ascii"] for r in records)
    return {"pie.txt": pie + "\n", "parallel.txt": par + "\n", "interlinear.txt": ilg + "\n", "pie_ascii.txt": asc + "\n"}
