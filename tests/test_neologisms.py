"""Tier 3b neologisms (PLAN.md "Tier 3b", data/lexicon/neologisms.jsonl, pie/neologism.py): coinages from attested
roots and productive suffixes, derived by the engine, flagged coined "neologism" everywhere, Tier 3b only.

Production path: make_slice --tier3b offers them (flagged) -> a plan from the slice -> scripts/realize_plans.py on a
t3b- batch (check_plan, speaker rule, realize, validate with index_neologisms) -> corpus/tier3b record with
neologism: true and flagged tokens -> pie.export tasks carry the flags, train only, within the 15% cap.
The default Lexicon, the Tier 1-3 validator index and Tier 2 never see them."""

import json
import runpy
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NEO = ROOT / "data/lexicon/neologisms.jsonl"
pytestmark = pytest.mark.skipif(not NEO.exists(), reason="no neologisms")
MACHINE, MAKER, WORDMAKER, QUESTION = "pie-neo-kwertrom", "pie-neo-kwrtexr", "pie-neo-werdhokwrtexr", "pie-neo-prekjnos"
WRITE, READ = "pie-neo-write", "pie-neo-read"
SEE, SPEAK = "pie-lex-spekjyeti", "pie-lex-bheh2ti"


def _rows():
    return [json.loads(x) for x in NEO.read_text("utf-8").splitlines() if x.strip()]


@pytest.fixture(scope="module")
def base():
    from pie.realize import Lexicon
    return Lexicon.load()


@pytest.fixture(scope="module")
def lx(base):
    from pie.neologism import with_neologisms
    return with_neologisms(base)


def V(lex, person=None, num=None, tense="PRS", mood="IND"):
    v = {"tense": tense, "mood": mood, "voice": "ACT"}
    if person:
        v.update(person=person, num=num)
    return {"lex_id": lex, "role": "V", "verb": v}


def _plan():
    """'Do you write questions? I see a machine, a word-maker.' (user, then model)."""
    return {"english": "Do you write questions? I see the word-maker's machine.", "clauses": [
        {"speaker": "user", "question": True, "slots": [{"lex_id": QUESTION, "role": "OBJ", "num": "PL"},
                                                         V(WRITE, 2, "SG")]},
        {"speaker": "model", "break": True, "slots": [{"lex_id": MACHINE, "role": "OBJ"},
                                                       {"lex_id": WORDMAKER, "role": "POSS", "head": 0},
                                                       V(SEE, 1, "SG")]}]}


def test_rows_meet_the_policy(base):
    """PLAN schema; 40-60 coinages of the three models; each derived by the engine (the stored pie and inflection
    are what pie.neologism derives); attested roots (kind root) and productive suffixes (kind affix) only; no
    held-out root family; ids never in lexicon.jsonl."""
    from pie.export import eval_root
    rows = _rows()
    assert 40 <= len(rows) <= 60
    assert {r["model"] for r in rows} == {"compound", "calque", "derivative"}
    for r in rows:
        assert {"neo_id", "pie", "english", "derivation", "model", "rationale", "inflection"} <= set(r), r["neo_id"]
        assert r["neo_id"].startswith("pie-neo-") and r["neo_id"] not in base.entries
        # roots are listed by root_id; only a calque of a lexeme the lexicon gives no root (péḱu) lists none
        assert r["rationale"] and (r["derivation"]["roots"] or not base.entries[r["derivation"]["base"]].get("root_id"))
        for i in r["derivation"]["roots"]:
            assert base.entries[i]["kind"] == "root" and not eval_root(i), (r["neo_id"], i)
        for i in r["derivation"]["suffixes"]:
            assert base.entries[i]["kind"] == "affix", (r["neo_id"], i)
        assert r["inflection"]["usable"] and r["inflection"]["rule"].startswith(f"neologism:{r['model']}:")
    from pie.neologism import load_neologisms
    entries, specs = load_neologisms(base)          # raises if a stored pie/inflection differs from the engine's
    assert len(entries) == len(rows)
    forms = {e["form"] for e in base.entries.values()}
    for r in rows:
        assert (r["pie"] in forms) == (r["model"] == "calque"), r["neo_id"]   # a coinage never reproduces a word


def test_derive_form_reproduces_attested_derivatives(base):
    """The derivative builder, calibrated on lexicon derivatives of the same suffixes (root grade + accent)."""
    from pie.classify import by_shape
    from pie.neologism import derive_form
    cases = [("pie-root-men-think", "e", "-tōr", "root", "pie-lex-mentoxr"),
             ("pie-root-men-think", "o", "-éyeti", "suffix", "pie-lex-moneyeti"),
             ("pie-root-kwer-do", "zero", "-tós", "suffix", "pie-lex-kwrtos"),
             ("pie-root-gerbh-carve", "e", "-mn̥", "root", "pie-lex-gerbhmn"),
             ("pie-root-bhergj-fry", "e", "-trom", "root", "pie-lex-bhergjtrom"),
             ("pie-root-kjlew-hear", "e", "-trom", "root", "pie-lex-kjlewtrom"),
             ("pie-root-dwey-fear", "e", "-nós", "suffix", "pie-lex-dweynos"),
             ("pie-root-gjews-taste", "e", "-tōr", "root", "pie-lex-gjewstoxr")]
    for root, grade, suf, acc, want in cases:
        form = derive_form(base.entries[root]["form"], grade, suf, acc)
        assert form == base.entries[want]["form"], (root, suf, form)
        e = base.entries[want]
        assert by_shape({"form": form, "pos": e.get("pos"), "gender": e.get("gender")}).rule == base.specs[want]["rule"]


def test_default_lexicon_never_has_them(base, lx):
    """Lexicon.load() (Tier 1-3, Tier 2, export) has no neologism; with_neologisms returns a new Lexicon and leaves
    the cached one unchanged. Lexicon.coined gives "neologism", also for a compound with a neologism member."""
    from pie.neologism import neologism_ids
    ids = {r["neo_id"] for r in _rows()}
    assert not ids & set(base.entries) and not ids & set(base.specs)
    assert set(neologism_ids(lx)) == ids and lx is not base
    assert all(lx.coined(i) == "neologism" for i in ids)
    assert base.coined(SEE) is None and lx.coined(SEE) is None
    assert lx.coined(f"compound:determinative:pie-lex-werdhom+{MAKER}") == "neologism"
    assert lx.cells(MACHINE)["ACC.SG"][0] == "kʷértrom" and lx.cells(MAKER)["GEN.SG"][0] == "kʷr̥trés"
    assert lx.cells(WRITE) == base.cells("pie-lex-pinekjti")       # a calque is its base's paradigm


def test_compounds_are_the_compound_engines(lx):
    """A compound coinage's spec declines to exactly pie.compound.resolve's cells."""
    from pie.compound import resolve
    for r in _rows():
        if r["model"] == "compound":
            c = resolve(r["derivation"]["compound"], lx)
            g = c.head_gender if c.ctype == "determinative" else "m"
            assert lx.cells(r["neo_id"], None if c.ctype == "determinative" else g) == c.cells(
                None if c.ctype == "determinative" else g), r["neo_id"]
            assert r["pie"] == c.cells(None if c.ctype == "determinative" else "m")["NOM.SG"][0]


def test_speaker_rule():
    from pie.neologism import speaker_errors
    assert speaker_errors(_plan()) == []
    p = _plan()
    del p["clauses"][1]["break"]
    assert "mid-sentence" in speaker_errors(p)[0]
    p = _plan()
    del p["clauses"][0]["speaker"]
    assert "needs a speaker" in speaker_errors(p)[0]


def _run_realize(tmp_path, monkeypatch, lx, batch, plans, *flags):
    from pie.validate import FormIndex
    rp = runpy.run_path(str(ROOT / "scripts/realize_plans.py"))
    main = rp["main"]
    monkeypatch.setitem(main.__globals__, "ROOT", tmp_path)
    (tmp_path / "data/generation/rejects").mkdir(parents=True, exist_ok=True)
    closed = json.loads((ROOT / "data/morph/closed_class.json").read_text())
    # only the scholarly verbs are pre-indexed; realize_plans adds the neologisms itself (index_neologisms)
    ix = FormIndex([lx.entries[SEE], lx.entries[SPEAK]], [lx.specs[SEE], lx.specs[SPEAK]], closed)
    monkeypatch.setitem(main.__globals__, "load_index", lambda: ix)
    f = tmp_path / f"{batch}.input.jsonl"
    f.write_text("".join(json.dumps({"plan_id": i, "genre": "dialogue", "plan": p}, ensure_ascii=False) + "\n"
                         for i, p in enumerate(plans)), "utf-8")
    monkeypatch.setattr(sys, "argv", ["realize_plans.py", str(f), "--batch", batch, *flags])
    return main()


def test_slice_to_export_production_path(lx, tmp_path, monkeypatch):
    # 1. make_slice: the default slice offers no neologism; --tier3b offers every one, flagged
    ms = runpy.run_path(str(ROOT / "scripts/make_slice.py"))
    monkeypatch.setitem(ms["main"].__globals__, "ROOT", tmp_path)
    (tmp_path / "data/generation/slices").mkdir(parents=True)
    for name, extra in (("plain", []), ("t3b-probe", ["--tier3b"])):
        monkeypatch.setattr(sys, "argv", ["make_slice.py", name, "--keywords", "see", "speak", "--size", "30", *extra])
        assert ms["main"]() == 0
    plain = json.loads((tmp_path / "data/generation/slices/plain.json").read_text())["lexemes"]
    b = {it["lex_id"]: it for it in json.loads((tmp_path / "data/generation/slices/t3b-probe.json").read_text())["lexemes"]}
    assert not any(it["lex_id"].startswith("pie-neo-") for it in plain)
    assert {r["neo_id"] for r in _rows()} <= set(b) and all(b[r["neo_id"]]["coined"] == "neologism" for r in _rows())
    assert "coined" not in b.get(SEE, {})
    # 2. a plan from the slice, through scripts/realize_plans.py as a Tier 3b batch
    assert _run_realize(tmp_path, monkeypatch, lx, "t3b-probe", [_plan()], "--tier3b") == 0
    batch = json.loads((tmp_path / "data/generation/batches/t3b-probe.json").read_text())
    assert batch["realized"] == 1 and batch["exact_pass"] == 1 and batch["neologism_tokens"]["tokens"] == 4
    rec = json.loads((tmp_path / "corpus/tier3b/t3b-probe.jsonl").read_text().splitlines()[0])
    assert rec["tier"] == 3 and rec["neologism"] is True
    assert rec["pie"] == "preḱnóns pinéḱsi? werdʰokʷr̥trés kʷértrom spéḱyoh₂."
    assert {t["lex_id"]: t.get("coined") for t in rec["tokens"]} == {
        QUESTION: "neologism", WRITE: "neologism", MACHINE: "neologism", WORDMAKER: "neologism", SEE: None}
    # the chat export splits the turns by speaker
    from pie.export_chat import dialogue_turns
    assert dialogue_turns(rec)[:2] == ([("user", [0]), ("assistant", [1])], "speaker")
    # 3. the export flags every task of the record
    from pie.export import record_tasks
    tasks = record_tasks(rec)
    assert tasks and all(t["coined"] == "neologism" and t["neologism"] is True for t in tasks)
    plain_rec = {**rec, "tokens": [rec["tokens"][-1]]}
    assert all(t["neologism"] is True and "coined" not in t for t in record_tasks(plain_rec))


def test_tier3_and_tier2_reject_them(lx, base, tmp_path, monkeypatch):
    """A Tier 3 batch (the default Lexicon) rejects a plan with a neologism id; so does Tier 2 (check_plan with
    Lexicon.load(), plus pie.realize.plan_coined); a t3b- batch needs --tier3b and vice versa."""
    from pie.realize import check_plan, plan_coined
    assert any("pie-neo-" in e for e in check_plan(_plan(), base))
    assert plan_coined(_plan(), lx) == [QUESTION, WRITE, MACHINE, WORDMAKER]
    assert "plan_coined(p[\"plan\"], lx)" in (ROOT / "scripts/build_tier2.py").read_text("utf-8")
    assert _run_realize(tmp_path, monkeypatch, base, "probe", [_plan()]) == 1
    rej = json.loads((tmp_path / "data/generation/rejects/probe.jsonl").read_text().splitlines()[0])
    assert any(MACHINE in e for e in rej["errors"])
    assert not (tmp_path / "corpus/tier3b/probe.jsonl").exists()
    with pytest.raises(SystemExit):
        _run_realize(tmp_path, monkeypatch, base, "t3b-x", [_plan()])          # t3b- name without --tier3b


def test_validator_excludes_them_unless_loaded(lx, tmp_path):
    """load_index (the Tier 1-3 validator) never indexes them; index_neologisms adds them (validate_text.py
    --neologisms), tagged engine:neologism:…"""
    from pie.neologism import index_neologisms
    from pie.validate import load_index, validate_text
    (tmp_path / "data/lexicon").mkdir(parents=True)
    (tmp_path / "data/morph").mkdir(parents=True)
    (tmp_path / "data/lexicon/lexicon.jsonl").write_text(json.dumps(lx.entries[SEE], ensure_ascii=False) + "\n")
    (tmp_path / "data/morph/inflection_specs.jsonl").write_text(json.dumps(lx.specs[SEE], ensure_ascii=False) + "\n")
    (tmp_path / "data/lexicon/paradigms.jsonl").write_text("")
    (tmp_path / "data/lexicon/neologisms.jsonl").write_bytes(NEO.read_bytes())
    (tmp_path / "data/morph/closed_class.json").write_text((ROOT / "data/morph/closed_class.json").read_text())
    ix = load_index(tmp_path)
    ids = {r["neo_id"] for r in _rows()}
    assert not ids & set(ix.lex) and not ids & set(ix.specs)
    assert not validate_text("kʷértrom spéḱyeti.", ix)["tokens"][0].found
    assert set(index_neologisms(ix)) == ids
    v = validate_text("kʷértrom spéḱyeti.", ix)
    assert v["status"] == "pass" and v["tokens"][0].analyses[0].lex_id == MACHINE
    assert v["tokens"][0].analyses[0].source.startswith("engine:neologism:derivative")


def _approved_batch(root, batch, recs):
    from pie.batch_release import corpus_dir, release_metadata
    d = root / corpus_dir(batch)
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{batch}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), "utf-8")
    for sub, body in (("plans", ""), ("batches", json.dumps({"gates": {"g": True}, "gate": "PASS"}))):
        (root / "data/generation" / sub).mkdir(parents=True, exist_ok=True)
        (root / "data/generation" / sub / f"{batch}.{'jsonl' if sub == 'plans' else 'json'}").write_text(body)
    (root / "data/generation/releases").mkdir(parents=True, exist_ok=True)
    (root / f"data/generation/releases/{batch}.json").write_text(json.dumps(
        release_metadata(root, batch, status="approved", evidence=["test"], rationale="test")))


def _rec(i, words, tier=3, neo=True):
    pie = " ".join(["kʷértrom"] * words) + "."
    return {"id": f"r{i}", "tier": tier, "neologism": neo, "pie": pie, "pie_ascii": pie, "english": "x",
            "tokens": [{"form": "kʷértrom", "lex_id": MACHINE, "coined": "neologism"}] if neo else []}


def test_export_tier3b_is_train_only_and_capped(tmp_path, monkeypatch):
    import pie.export as ex
    monkeypatch.setattr(ex, "inflection_tasks", lambda lx, rng: [])
    monkeypatch.setattr(ex, "cognate_tasks", lambda lx: [])
    (tmp_path / "corpus/tier1").mkdir(parents=True)
    (tmp_path / "corpus/tier2").mkdir(parents=True)
    # 9 archaic words for every Tier 3b word: 10%, within the cap, status ok
    (tmp_path / "corpus/tier2/a.jsonl").write_text(json.dumps(_rec(0, 90, tier=2, neo=False)) + "\n")
    _approved_batch(tmp_path, "t3b-001", [_rec(1, 10)])
    out = ex.build(root=tmp_path)
    assert {r["id"] for r in out["train_records"]} == {"r0", "r1"} and not out["eval_records"]
    t3b = [t for t in out["train_tasks"] if t["source_id"] == "r1"]
    assert t3b and all(t["neologism"] is True and t["coined"] == "neologism" for t in t3b)
    assert not any(t.get("source_id") == "r1" for t in out["eval_tasks"])
    assert out["neologism_share"]["share"] == 0.1 and out["neologism_share"]["status"] == "ok"
    assert any(d["batch"] == "t3b-001" and d["admitted"] for d in out["batch_eligibility"])
    # 12%: a warning; 20%: the export fails
    _approved_batch(tmp_path, "t3b-002", [_rec(2, 2)])
    assert ex.build(root=tmp_path)["neologism_share"]["status"] == "warn"
    _approved_batch(tmp_path, "t3b-003", [_rec(3, 10)])
    with pytest.raises(ValueError, match="cap"):
        ex.build(root=tmp_path)
    # a Tier 3b record must say so; an evaluation record with a neologism fails
    (tmp_path / "corpus/tier3b/t3b-003.jsonl").unlink()
    _approved_batch(tmp_path, "t3b-003", [{**_rec(3, 1), "neologism": False}])
    with pytest.raises(ValueError, match="neologism: true"):
        ex.build(root=tmp_path)
    (tmp_path / "corpus/tier3b/t3b-003.jsonl").unlink()
    (tmp_path / "corpus/tier1/x.jsonl").write_text(json.dumps({**_rec(9, 1, tier=1), "neologism": False}) + "\n")
    with pytest.raises(ValueError, match="neologism in an evaluation record"):
        ex.build(root=tmp_path)


def test_pilot_batch_t3b_001(lx):
    """The shipped pilot: 20 dialogues in corpus/tier3b, gate PASS, every neologism token flagged, every record
    split into user/model turns by speaker."""
    from pie.batch_release import batch_eligibility
    from pie.export_chat import dialogue_turns
    p = ROOT / "corpus/tier3b/t3b-001.jsonl"
    if not p.exists():
        pytest.skip("pilot not built")
    recs = [json.loads(x) for x in p.read_text("utf-8").splitlines() if x.strip()]
    assert len(recs) == 20 and all(r["tier"] == 3 and r["neologism"] is True for r in recs)
    assert batch_eligibility(ROOT, "t3b-001")["gate"] == "PASS"
    for r in recs:
        for t in r["tokens"]:
            assert (t.get("coined") == "neologism") == t["lex_id"].startswith("pie-neo-"), (r["id"], t)
        assert dialogue_turns(r)[1] == "speaker", r["id"]
