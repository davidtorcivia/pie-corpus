"""scripts/meter_report.py: lines and clause groups match realize_plans' scoring; listed edits are measured."""
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MR = runpy.run_path(str(ROOT / "scripts/meter_report.py"))


def _plans(batch):
    return [json.loads(x) for x in (ROOT / f"data/generation/plans/{batch}.jsonl").read_text("utf-8").splitlines()
            if x.strip()]


def test_report_lines_and_edits(tmp_path):
    from pie.meter import record_meter
    from pie.realize import Lexicon, realize
    plan = next(p for p in _plans("t032") if p["plan_id"] == "t032-0002")
    f = tmp_path / "t032.jsonl"           # named like the batch, so the t032 slice supplies epithets
    f.write_text(json.dumps(plan) + "\n", "utf-8")
    rep = MR["report"](f)
    lines = rep["plans"][0]["lines"]
    stored = record_meter(realize(plan["plan"], Lexicon.load())["pie"], "charm")
    assert [ln["syllables"] for ln in lines] == stored["line_syllables"]     # the same lines realize_plans scores
    assert rep["exact"] == stored["exact"] and rep["lines"] == len(lines)
    l2 = lines[1]                          # nu h₁éy wékʷos trís wéwket: 7 syllables, one clause
    assert (l2["syllables"], l2["target"], l2["gap"], l2["clauses"]) == (7, 8, 1, [2])
    assert any(e["exact"] and e["result"] == "8" for e in l2["edits"])
    assert all(ln["edits"] == [] for ln in lines if ln["gap"] == 0)


def test_groups_match_sentences():
    from pie.meter import verse_lines
    from pie.realize import Lexicon, check_plan, realize
    lx = Lexicon.load()
    for p in _plans("t026"):
        if not check_plan(p["plan"], lx):
            assert len(MR["groups"](p["plan"])) == len(verse_lines(realize(p["plan"], lx)["pie"]))
