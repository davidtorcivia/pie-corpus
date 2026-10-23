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
    monkeypatch.setattr(ex, "inflection_tasks", lambda lx, rng: [])
    monkeypatch.setattr(ex, "cognate_tasks", lambda lx: [])
    with pytest.raises(ValueError, match="leakage"):
        ex.build(root=tmp_path)
