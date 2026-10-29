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
    # t032-0002 as planned before its meter repair (line 2 at 7 syllables)
    plan = json.loads((ROOT / "tests/data/meter_report_t032-0002.jsonl").read_text("utf-8"))
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


def test_insert_renumbers_head_and_dep():
    slots = [{"lex_id": "a", "role": "MOD", "head": 1}, {"lex_id": "b", "role": "OBJ"},
             {"lex_id": "c", "role": "GOAL", "dep": 3}, {"lex_id": "d", "role": "ADV"}]
    out = MR["_insert"](slots, 0, {"lex_id": "v", "role": "VOC"})
    assert [s["lex_id"] for s in out] == ["v", "a", "b", "c", "d"]
    assert out[1]["head"] == 2 and out[3]["dep"] == 4
    assert slots[0]["head"] == 1                       # the input plan is not mutated
    mid = MR["_insert"](slots, 2, {"lex_id": "x", "role": "ADV"})
    assert mid[0]["head"] == 1 and mid[3]["dep"] == 4  # links before the insertion point stay


def test_added_vocative_keeps_epithet_on_its_noun():
    from pie.realize import Lexicon, check_plan, realize
    lx = Lexicon.load()
    plan = {"english": "Build the new wagon!", "clauses": [{"slots": [
        {"lex_id": "pie-lex-newos", "role": "MOD", "head": 1}, {"lex_id": "pie-lex-kwekwlos", "role": "OBJ"},
        {"lex_id": "pie-lex-demeti", "role": "V", "verb": {"mood": "IMP", "voice": "ACT", "person": 2,
                                                           "tense": "PRS"}}]}]}
    voc = [p for kind, _, p in MR["candidate_edits"](plan, 0, [0], lx, {"theme_core": ["pie-lex-dyexws"]})
           if kind == "vocative"]
    assert voc
    slots = voc[0]["clauses"][0]["slots"]
    assert slots[0] == {"lex_id": "pie-lex-dyexws", "role": "VOC"}
    assert slots[slots[1]["head"]]["lex_id"] == "pie-lex-kwekwlos"
    assert not check_plan(voc[0], lx)
    base = {w["lex_id"]: w["features"] for w in realize(plan, lx)["words"]}
    new = {w["lex_id"]: w["features"] for w in realize(voc[0], lx)["words"]}
    assert new["pie-lex-newos"] == base["pie-lex-newos"]       # the epithet still agrees with the object


def test_cap_note_matches_the_gate():
    from collections import Counter
    words = [{"lex_id": x} for x in ("pie-lex-a", "pie-lex-a", "closed:personal/1", "pie-lex-h1esti")]
    assert MR["cap_uses"](words) == Counter({"pie-lex-a": 2})          # no closed ids, no copula
    uses = Counter({"pie-lex-a": 6, "pie-lex-core": 6, "pie-lex-h1esti": 40})
    over = MR["over_cap"]
    assert over(Counter({"pie-lex-a": 1}), uses, 6, set(), 15) == ["pie-lex-a"]
    assert over(Counter({"pie-lex-core": 1}), uses, 6, {"pie-lex-core"}, 15) == []    # theme core: theme_cap
    assert over(Counter({"pie-lex-core": 10}), uses, 6, {"pie-lex-core"}, 15) == ["pie-lex-core"]
    assert over(Counter({"pie-lex-h1esti": 1}), uses, 6, set(), 15) == []
    assert over(Counter({"pie-lex-new": 6}), uses, 6, set(), 15) == []
    assert over(Counter({"pie-lex-new": 7}), uses, 6, set(), 15) == ["pie-lex-new"]


def test_report_flags_over_cap_epithets_and_spares_theme_core():
    rep = MR["report"](ROOT / "data/generation/plans/t026.jsonl", True, 1000)
    cap, core_cap, uses = rep["lexeme_cap"], rep["theme_cap"], rep["uses"]
    core = MR["GATE"]["theme_core"]("t026")
    seen = 0
    for e in rep["plans"]:
        for ln in e["lines"]:
            for ed in ln["edits"]:
                if ed["kind"] in ("epithet", "vocative"):
                    lid = ed["edit"].split(f"add {ed['kind']} ")[1].split()[0]
                    limit = core_cap if lid in core else cap
                    assert (uses.get(lid, 0) + 1 > limit) == (lid in ed.get("over_cap", [])), ed
                    seen += 1
    assert seen
