from pathlib import Path

import pytest

from pie.validate import key, tokenize

ROOT = Path(__file__).resolve().parent.parent


def test_key_tiers():
    assert key("h₁éḱwōs", "noaccent") == "h₁eḱwōs"
    assert key("h₁éḱwōs", "nolength") == "h₁eḱwos"
    assert key("h₁éḱwōs", "generic-H") == "Heḱwos"


def test_tokenize_splits_hyphenated_clitics_and_punctuation():
    assert tokenize('h₂ówis, h₁éḱwōs-kʷe. "ḱḗr!"') == ["h₂ówis", "h₁éḱwōs", "-kʷe", "ḱḗr"]
    assert tokenize("bʰér-e-ti") == ["bʰéreti"]      # morpheme hyphens are not clitics


@pytest.fixture(scope="module")
def ix():
    if not (ROOT / "data" / "morph" / "inflection_specs.jsonl").exists():
        pytest.skip("specs not built")
    from pie.validate import load_index
    return load_index()


def test_analyses(ix):
    from pie.validate import validate_text
    r = validate_text("h₂ówis h₁éḱwōs-kʷe", ix)
    assert r["coverage"] == 1.0 and r["status"] == "pass"
    feats = {a.features for a in r["tokens"][1].analyses}
    assert "NOM.PL" in feats
    assert r["tokens"][2].analyses[0].features == "PARTICLE"


def test_augment_and_clitic(ix):
    from pie.validate import analyze_token
    t = analyze_token("h₁ébʰeret", ix)
    assert t.augment and any(a.features == "PST.3SG" for a in t.analyses)
    t = analyze_token("h₂ówiskʷe", ix)
    assert t.clitic == "-kʷe" and t.found


def test_every_miss_is_classified(ix):
    from pie.validate import validate_text
    r = validate_text("spéḱet wl̥h₂néh₂ qqq", ix)
    assert all(t.miss for t in r["tokens"] if not t.found)


def test_accent_tiers_keep_palatals():
    # Regression: stripping U+0301 in NFD also removed the palatal mark of ḱ.
    assert key("ḱléwos", "noaccent") == "ḱlewos"
    assert key("ǵʰéyōm", "nolength") == "ǵʰeyom"
    assert key("ḱ", "generic-H") != key("k", "generic-H")
