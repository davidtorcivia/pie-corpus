import json

import pytest

from pie.export import eval_root, record_tasks


def test_root_holdout_is_deterministic_and_about_ten_percent():
    ids = [f"pie-root-x{i}" for i in range(2000)]
    held = [i for i in ids if eval_root(i)]
    assert held == [i for i in ids if eval_root(i)]
    assert 150 < len(held) < 250
    assert not eval_root(None)


def test_record_tasks():
    r = {"id": "t3-x-1", "pie": "h₂ówis spéḱyeti.", "english": "The sheep sees.", "gloss": "sheep-NOM.SG see-PRS.3SG"}
    kinds = {t["task"] for t in record_tasks(r)}
    assert kinds == {"translate_en_pie", "translate_pie_en", "gloss"}


def test_leakage_guard(tmp_path, monkeypatch):
    import pie.export as ex
    (tmp_path / "corpus" / "tier1").mkdir(parents=True)
    (tmp_path / "corpus" / "tier3").mkdir(parents=True)
    rec = {"id": "a", "pie": "h₂ówis.", "pie_ascii": "h2o/wis.", "english": "sheep"}
    (tmp_path / "corpus/tier1/x.jsonl").write_text(json.dumps(rec) + "\n", "utf-8")
    (tmp_path / "corpus/tier3/b.jsonl").write_text(json.dumps({**rec, "id": "b"}) + "\n", "utf-8")
    from pie.batch_release import release_metadata
    (tmp_path / "data/generation/plans").mkdir(parents=True)
    (tmp_path / "data/generation/batches").mkdir(parents=True)
    (tmp_path / "data/generation/releases").mkdir(parents=True)
    (tmp_path / "data/generation/plans/b.jsonl").write_text("{}\n")
    (tmp_path / "data/generation/batches/b.json").write_text(json.dumps({"gate": "PASS", "gates": {"exact": True}}))
    (tmp_path / "data/generation/releases/b.json").write_text(json.dumps(
        release_metadata(tmp_path, "b", status="approved", evidence=["fixture review"])))
    monkeypatch.setattr(ex, "inflection_tasks", lambda lx, rng: [])
    monkeypatch.setattr(ex, "cognate_tasks", lambda lx: [])
    with pytest.raises(ValueError, match="leakage"):
        ex.build(root=tmp_path)


def _lx():
    from pie.realize import Lexicon
    return Lexicon.load()


@pytest.mark.parametrize("lid,gender,form", [("pie-lex-sweh2dus", "n", "sweh₂dú"), ("pie-lex-HeHkjus", "n", "HeHḱú"),
                                             ("pie-lex-h1werHus", "f", "h₁wr̥Héwih₂")])
def test_token_variants_keep_the_tokens_gender(lid, gender, form):
    """David's review: eval-grade Tier 2 offered masculine sweh₂dús, HeHḱús, h₁wr̥Hús as acceptable."""
    from pie.export import token_variants
    lx = _lx()
    r = {"tier": 2, "tokens": [{"form": form, "lex_id": lid, "features": "NOM.SG", "gender": gender}]}
    alts = token_variants(r, lx)[0]
    assert alts[0] == form and set(alts) <= set(lx.cells(lid, gender)["NOM.SG"])
    others = {f for g in "mfn" if g != gender for f in lx.cells(lid, g)["NOM.SG"]} - set(lx.cells(lid, gender)["NOM.SG"])
    assert not set(alts) & others
    # a stored token without a resolved gender gets no alternatives (never a guessed masculine)
    r["tokens"][0].pop("gender")
    assert token_variants(r, lx) == [[form]]


def test_token_variants_of_a_realized_record():
    from pie.export import token_variants
    from pie.realize import realize
    lx = _lx()
    w = realize({"english": "Sweet mead.", "clauses": [{"type": "np", "slots": [
        {"lex_id": "pie-lex-medhu", "role": "NP"}, {"lex_id": "pie-lex-sweh2dus", "role": "MOD", "head": 0}]}]}, lx)["words"]
    r = {"tier": 2, "tokens": [{k: x[k] for k in ("form", "lex_id", "features", "gender")} for x in w]}
    assert token_variants(r, lx)[0] == ["sweh₂dú"]


def test_no_active_inflection_tasks_for_middle_only_verbs():
    """David's review: 8 of 15 tasks for five newly admitted middle-only verbs asked for active forms
    (mn̥yétor PRS.1PL → mn̥yómes), which check_plan forbids."""
    import random
    from pie.export import inflection_tasks
    lx = _lx()
    mid = {i for i in lx.specs if lx.voices(i) == ("MID",)}
    assert "pie-lex-mnyetor" in mid
    for seed in (0, 1, 2):
        ts = [t for t in inflection_tasks(lx, random.Random(seed)) if t["source_id"] in mid]
        assert ts and all(t["input"].split()[-1].startswith(("MID.", "PTCP.MID")) for t in ts), ts[:3]


def test_adjective_inflection_tasks_name_the_gender():
    import random
    from pie.export import inflection_tasks
    lx = _lx()
    ts = [t for t in inflection_tasks(lx, random.Random(0)) if lx.specs[t["source_id"]]["family"] == "adj"]
    assert ts
    for t in ts:
        lemma, feat = t["input"].rsplit(" ", 1)
        g, cell = feat.split(".", 1)
        assert g in ("M", "F", "N") and t["output"] == lx.cells(t["source_id"], g.lower())[cell][0]


@pytest.mark.parametrize("num,flag", [("DU", "du->pl"), ("PL", None)])
def test_record_tasks_carry_realized_number_fallback(num, flag):
    from pie.export import record_tasks, token_variants
    from pie.realize import token_cell
    from .helpers import produce
    lx = _lx()
    realized = produce({"english": "They carry for themselves.", "clauses": [{"slots": [
        {"lex_id": "pie-lex-bhereti", "role": "V", "verb": {
            "voice": "MID", "person": 3, "num": num}}]}]}, lx)
    tokens = [{k: w[k] for k in ("form", "lex_id", "features")} | token_cell(w)
              for w in realized["words"]]
    record = {**realized, "id": "fallback-test", "tier": 2, "tokens": tokens}
    tasks = record_tasks(record)
    assert {t["task"] for t in tasks} == {"translate_en_pie", "translate_pie_en", "gloss"}
    assert all(t.get("num_fallback") == flag for t in tasks)
    assert all(("num_fallback" in t) == bool(flag) for t in tasks)
    assert token_variants(record, lx) == [lx.admissible_cells("pie-lex-bhereti")["MID.PRS.3PL"]]
    tokens[0].pop("num_fallback", None)
    assert all("num_fallback" not in t for t in record_tasks(record))
