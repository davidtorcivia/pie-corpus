"""RL stage 1 (training/rl): the prompt set never touches what is scored, its answers are the engine's, and the
engine reward pays only for the exact answer (training/rl/reward_engine.py)."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"training/rl/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def built():
    mp = _load("make_rl_prompts")
    return mp, *mp.build(600, 32)


def test_rl_prompts_hold_out_scored_lexemes(built):
    mp, train, valid, man = built
    held = mp.held_lexemes()
    frozen = {json.loads(x)["source_id"] for p in ("training/gen_prompts_v1.jsonl", "training/gen_prompts_drills_v2.jsonl")
              for x in (ROOT / p).read_text("utf-8").splitlines() if json.loads(x).get("source_id")}
    assert frozen <= held
    assert not {x["source_id"] for x in train + valid} & held
    assert not {x["source_id"] for x in train} & {x["source_id"] for x in valid}
    assert len(train) == 600 and {x["type"] for x in train} == {"inflect", "paradigm"}


def test_rl_answers_are_the_engines(built):
    mp, train, valid, _ = built
    from pie.realize import Lexicon
    lx = Lexicon.load()
    for x in train[:200]:
        a = json.loads(x["answer"])
        if x["type"] == "inflect":
            cells = mp.all_cells(lx, x["source_id"])
            assert any(a == list(dict.fromkeys(v)) for v in cells.values()), x
        else:
            assert all(c and f for c, f in a.items())


def test_engine_reward_pays_only_for_the_exact_answer():
    r = _load("reward_engine")
    table = {"NOM.SG": "pódes", "GEN.SG": "pedés", "ACC.SG": "pódm̥", "DAT.SG": "pedéy"}
    a = json.dumps(table, ensure_ascii=False)
    exact = "\n".join(f"{c}: {f}" for c, f in table.items())
    assert r.score(exact, a, "paradigm") == 1.0
    assert r.score("\n".join(f"- {c}: *{f}." for c, f in table.items()), a, "paradigm") == 1.0
    for hack in (exact + "\nNOM.SG: pṓds",              # a second guess at a cell
                 exact + "\nXX.PL: pódes",               # a cell the table lacks
                 exact.replace("pedés", "pedés / pódos"),  # a hedged row
                 "Here is the table:\n" + exact):        # prose
        assert r.score(hack, a, "paradigm") < 1.0, hack
    assert r.score("", a, "paradigm") == 0.0
    f = json.dumps(["pedés"], ensure_ascii=False)
    assert r.score("pedés", f, "inflect") == r.score("*pedés.", f, "inflect") == 1.0
    assert r.score("pedés or pódos", f, "inflect") == r.score("pedés (genitive)", f, "inflect") == 0.0


def test_translation_local_checks():
    """reward_rl.local decides what it can without the judge, and every cheap exploit scores 0."""
    sys.path.insert(0, str(ROOT / "training/rl"))
    import reward_rl
    from pie.translator.analyze import Analyzer
    an = Analyzer.load()
    ans = {"english": "They divided the plunder.", "refs": ["tóy Hrowpóm bʰéh₂gont."]}
    assert reward_rl.local("tóy Hrowpóm bʰéh₂gont.", ans, an)[0] == 1.0
    assert reward_rl.local("Tóy Hrowpóm bʰéh₂gont", ans, an)[0] == 1.0          # case and punctuation aside
    assert reward_rl.local("Hrowpóm tóy bʰéh₂gont.", ans, an)[0] is None        # a reordering: the judge decides
    assert reward_rl.local("They divided the plunder.", ans, an)[0] == 0.0      # English
    assert reward_rl.local("tóy Hrowpóm bʰéh₂gont.\nThis means they divided it.", ans, an)[0] == 0.0  # commentary
    assert reward_rl.local("tóy Hrowpóm xqzzlont.", ans, an)[0] == 0.0          # an invented word
    assert reward_rl.local(" ".join(["tóy"] * 20), ans, an)[0] == 0.0           # padding
    assert reward_rl.local("", ans, an)[0] == 0.0
