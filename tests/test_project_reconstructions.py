"""Project reconstructions (PLAN.md "Project reconstructions", docs/lexicon-project-reconstructions.md):
lexemes projected from cognates in >= 2 branches, flagged coined "project" everywhere, Tier 3/3b only.

Production path: make_slice offers them (flagged) -> a plan from the slice -> scripts/realize_plans.py (check_plan,
realize, validate with index_project) -> the corpus record's tokens carry coined -> pie.export tasks carry it.
The default validator index (load_index: Tier 1 and Tier 2) never sees them."""

import json
import runpy
import sys
from pathlib import Path

import pytest

from .helpers import produce

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "data/lexicon/project_reconstructions.jsonl"
pytestmark = pytest.mark.skipif(not PROJECT.exists(), reason="no project reconstructions")
HARE, FOAL, HORN, FLY = "pie-proj-kjasos", "pie-proj-poxlHos", "pie-proj-kjrnom", "pie-proj-musih2"
SEE = "pie-lex-spekjyeti"


def _rows():
    return [json.loads(x) for x in PROJECT.read_text("utf-8").splitlines() if x.strip()]


@pytest.fixture(scope="module")
def lx():
    from pie.realize import Lexicon
    Lexicon.load.cache_clear()
    return Lexicon.load()


def test_entries_meet_the_policy():
    """Each entry: flagged, cognates in >= 2 branches, every reflex cited, handbook evidence, a usable spec,
    and the sound-law checker passes with at least one correspondence actually checked."""
    from pie.soundlaw import check_entry
    sys.path.insert(0, str(ROOT / "scripts"))
    from make_slice import branches
    lex_ids = {json.loads(x)["id"] for x in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines()}
    rows = _rows()
    assert {r["id"] for r in rows} >= {HARE, FOAL, HORN, FLY}
    for r in rows:
        assert r["source"] == "project" and r["coined"] == "project" and r["id"] not in lex_ids
        assert len(branches(r["reflexes"])) >= 2, r["id"]
        assert all(x.get("cite") for xs in r["reflexes"].values() for x in xs), r["id"]
        assert r["evidence"]["handbooks"] and all(h["text_file"].startswith("raw/books/text/")
                                                   for h in r["evidence"]["handbooks"])
        assert sum(x["same_formation"] for xs in r["reflexes"].values() for x in xs) >= 2, r["id"]
        assert r["inflection"]["usable"] and r["inflection"]["spec"]
        checks = list(check_entry(r))
        assert checks and all(ok for _, _, ok, _, _ in checks), (r["id"], checks)


def test_lexicon_loads_them_with_specs_and_flag(lx):
    from pie.realize import load_project_reconstructions
    entries, specs = load_project_reconstructions()
    for i in entries:
        assert lx.entries[i] is not None and lx.specs[i]["family"] == "noun"
        assert "inflection" not in lx.entries[i]          # the spec is split off into Lexicon.specs
        assert lx.coined(i) == "project" and not lx.inadmissible(i)
    assert lx.cells(HARE)["ACC.SG"][0] == "ḱasóm"
    assert lx.cells(HORN)["NOM.PL"][0] == "ḱr̥néh₂"       # thematic neuter
    assert lx.cells(FLY)["GEN.SG"][0] == "musyéh₂s"       # proterokinetic devī, like néptih₂
    assert lx.gender(FLY) == "f" and lx.gender(HORN) == "n"
    assert lx.coined("pie-lex-h2owis") is None
    # a compound with a project member is coined too (one source: Lexicon.coined)
    assert lx.coined(f"compound:bahuvrihi:closed:prefix/h1su+{HORN}") == "project"


def test_slice_to_export_production_path(lx, tmp_path, monkeypatch):
    # 1. make_slice offers the project lexemes, flagged
    ms = runpy.run_path(str(ROOT / "scripts/make_slice.py"))
    monkeypatch.setitem(ms["main"].__globals__, "ROOT", tmp_path)
    (tmp_path / "data/generation/slices").mkdir(parents=True)
    monkeypatch.setattr(sys, "argv", ["make_slice.py", "probe", "--keywords", "hare", "foal", "horn", "fly",
                                      "--size", "40"])
    assert ms["main"]() == 0
    items = {it["lex_id"]: it for it in json.loads((tmp_path / "data/generation/slices/probe.json").read_text())["lexemes"]}
    for i in (HARE, FOAL, HORN, FLY):
        assert items[i]["coined"] == "project", i
    assert "coined" not in items.get(SEE, {})
    # 2. a plan from the slice through scripts/realize_plans.py
    plan = {"english": "The hare sees the foal's horns.", "clauses": [{"slots": [
        {"lex_id": HARE, "role": "SUBJ", "num": "SG"}, {"lex_id": HORN, "role": "OBJ", "num": "PL"},
        {"lex_id": FOAL, "role": "POSS", "num": "SG", "head": 1}, {"lex_id": SEE, "role": "V",
                                                                 "verb": {"tense": "PRS", "mood": "IND", "voice": "ACT"}}]}]}
    r = produce(plan, lx)
    assert r["pie"] == "ḱasós pṓlHosyo ḱr̥néh₂ spéḱyeti."
    rp = runpy.run_path(str(ROOT / "scripts/realize_plans.py"))
    main = rp["main"]
    monkeypatch.setitem(main.__globals__, "ROOT", tmp_path)
    for p in ("corpus/tier3", "data/generation/rejects"):
        (tmp_path / p).mkdir(parents=True)
    from pie.validate import FormIndex
    closed = json.loads((ROOT / "data/morph/closed_class.json").read_text())
    # only the scholarly lexeme is pre-indexed; realize_plans adds the project ones itself (index_project)
    ix = FormIndex([lx.entries[SEE]], [lx.specs[SEE]], closed)
    monkeypatch.setitem(main.__globals__, "load_index", lambda: ix)
    plans = tmp_path / "input.jsonl"
    plans.write_text(json.dumps({"plan_id": 1, "plan": plan}) + "\n")
    monkeypatch.setattr(sys, "argv", ["realize_plans.py", str(plans), "--batch", "probe"])
    main()
    batch = json.loads((tmp_path / "data/generation/batches/probe.json").read_text())
    assert batch["realized"] == 1 and batch["exact_pass"] == 1      # validated at the exact tier
    rec = json.loads((tmp_path / "corpus/tier3/probe.jsonl").read_text().splitlines()[0])
    flags = {t["lex_id"]: t.get("coined") for t in rec["tokens"]}
    assert flags == {HARE: "project", FOAL: "project", HORN: "project", SEE: None}
    # 3. the export carries the flag into every task view of the record
    from pie.export import record_tasks
    tasks = record_tasks(rec)
    assert {t["task"] for t in tasks} == {"translate_en_pie", "translate_pie_en", "gloss"}
    assert all(t["coined"] == "project" for t in tasks)
    assert not any("coined" in t for t in record_tasks({**rec, "tokens": [rec["tokens"][-1]]}))


def test_export_keeps_them_out_of_evaluation(lx):
    import random
    from pie.export import cognate_tasks, inflection_tasks
    inf = [t for t in inflection_tasks(lx, random.Random(0)) if t["source_id"].startswith("pie-proj-")]
    assert inf and all(t["coined"] == "project" for t in inf)
    assert not any(t["source_id"].startswith("pie-proj-") for t in cognate_tasks(lx))


def test_export_build_routes_project_tasks_to_train_and_rejects_eval_records(lx, tmp_path, monkeypatch):
    import pie.export as ex
    (tmp_path / "corpus/tier1").mkdir(parents=True)
    task = {"task": "inflect", "input": "ḱasós ACC.SG", "output": "ḱasóm", "source_id": HARE,
            "root_id": None, "coined": "project"}
    held_task = {**task, "source_id": HORN, "root_id": "pie-root-held"}
    monkeypatch.setattr(ex, "eval_root", lambda rid, share=0.1: rid == "pie-root-held")
    monkeypatch.setattr(ex, "inflection_tasks", lambda lx, rng: [dict(task), dict(held_task)])
    monkeypatch.setattr(ex, "cognate_tasks", lambda lx: [])
    out = ex.build(root=tmp_path)
    # train only; a held-out root family's project task is dropped, not trained on and not evaluated
    assert [t["source_id"] for t in out["train_tasks"]] == [HARE]
    assert not out["eval_tasks"]
    rec = {"id": "t1-x", "tier": 1, "pie": "ḱasós.", "pie_ascii": "k'aso/s.", "english": "A hare.",
           "tokens": [{"form": "ḱasós", "lex_id": HARE, "coined": "project"}]}
    (tmp_path / "corpus/tier1/x.jsonl").write_text(json.dumps(rec, ensure_ascii=False) + "\n", "utf-8")
    with pytest.raises(ValueError, match="project reconstruction"):
        ex.build(root=tmp_path)


def test_default_validator_index_never_sees_them(lx, tmp_path):
    """load_index (Tier 1, Tier 2) indexes lexicon.jsonl and inflection_specs.jsonl only, even with the
    project file present; index_project adds them for Tier 3, tagged engine:project."""
    from pie.validate import index_project, load_index, validate_text
    (tmp_path / "data/lexicon").mkdir(parents=True)
    (tmp_path / "data/morph").mkdir(parents=True)
    (tmp_path / "data/lexicon/lexicon.jsonl").write_text(json.dumps(lx.entries[SEE], ensure_ascii=False) + "\n")
    (tmp_path / "data/morph/inflection_specs.jsonl").write_text(json.dumps(lx.specs[SEE], ensure_ascii=False) + "\n")
    (tmp_path / "data/lexicon/paradigms.jsonl").write_text("")
    (tmp_path / "data/lexicon/project_reconstructions.jsonl").write_bytes(PROJECT.read_bytes())
    (tmp_path / "data/morph/closed_class.json").write_text((ROOT / "data/morph/closed_class.json").read_text())
    ix = load_index(tmp_path)
    proj = {r["id"] for r in _rows()}
    assert not proj & set(ix.lex) and not proj & set(ix.specs)
    assert not any(a.lex_id in proj for t in ix.idx.values() for an in t.values() for a in an)
    v = validate_text("ḱasós spéḱyeti.", ix)
    assert not v["tokens"][0].found
    assert index_project(ix) == sorted(proj)
    v = validate_text("ḱasós spéḱyeti.", ix)
    assert {a.source for a in v["tokens"][0].analyses} == {"engine:project", "project-lexicon"}


def test_tier2_rejects_project_lexemes(lx):
    """scripts/build_tier2.py adds a plan error for every pie.realize.plan_coined lexeme."""
    from pie.realize import plan_coined
    plan = {"english": "x", "clauses": [{"slots": [
        {"lex_id": HARE, "role": "SUBJ"},
        {"lex_id": "compound", "compound": {"first": "closed:prefix/h1su", "second": HORN, "type": "bahuvrihi"},
         "role": "MOD", "head": 0}, {"lex_id": SEE, "role": "V"}]}]}
    assert plan_coined(plan, lx) == [HARE, HORN]
    assert "plan_coined(p[\"plan\"], lx)" in (ROOT / "scripts/build_tier2.py").read_text("utf-8")
