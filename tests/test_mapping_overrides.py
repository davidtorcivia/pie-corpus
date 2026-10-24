"""Mapping errata (data/research/formulas/mapping-overrides.json, from mapping-errata.md): the override
helpers in pie/formula_search_multi.py and the regenerated round-3 tables."""

import json
from pathlib import Path

from pie import formula_search as fs
from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "data" / "research" / "formulas" / "mapping"

EXPECTED = {   # (corpus, lemma) → corrected ids (empty: unmapped)
    ("rv", "pád-"): {"pie-lex-poxds"},
    ("av", "pad"): {"pie-lex-poxds", "pie-lex-pedyeti"},
    ("rv", "ásita-"): set(),
    ("av", "asita"): set(),
    ("rv", "√vadhⁱ-"): {"pie-lex-wedhh1t"},
    ("av", "vadh"): {"pie-lex-wedhh1t"},
    ("rv", "kṣáya-"): {"pie-root-tkjey-cultivate"},
    ("av", "kṣaya"): {"pie-root-tkjey-cultivate"},
    ("lat", "situs"): {"pie-lex-tkjineti"},
}
WRONG = {"pie-lex-pedyeti", "pie-lex-sexmi", "pie-lex-sineh2ti", "pie-lex-wedheti", "pie-lex-wedheti-2",
         "pie-lex-wodheyeti", "pie-lex-dhgwhey", "pie-root-dhgwhey-decline"}


def test_override_table_covers_the_errata():
    ov = fm.load_overrides(ROOT)
    got = {(c, lem): set(ids) for c, rows in ov["lemma"].items() for lem, (ids, _) in rows.items()}
    # every erratum stays covered; per-language files (data/research/formulas/mapping-overrides/) may add
    # rows or refine an erratum's target, but never drop an erratum or restore a WRONG mapping
    for key in EXPECTED:
        assert key in got, key
        assert not (got[key] & WRONG), (key, got[key])
    assert ov["form"]["ang"].get("bid") == "biþ"
    errata = (ROOT / "data/research/formulas/mapping-errata.md").read_text("utf-8")
    for _, row in [r for rows in ov["lemma"].values() for r in rows.values()]:
        if "erratum" in row:
            assert row["erratum"].split()[0].strip("'") in errata


def test_apply_lemma_overrides_replaces_and_unmaps():
    m = fs.Mapping()
    for lem, ids in (("pád-", {"pie-lex-pedyeti"}), ("ásita-", {"pie-lex-sexmi", "pie-lex-sineh2ti"}),
                     ("kṣáya-", {"pie-lex-dhgwhey"}), ("áśva-", {"pie-lex-hxekjwos"})):
        m.lemma_lex[lem], m.lemma_groups[lem], m.lemma_tier[lem] = frozenset(ids), frozenset(ids), "kaikki"
    gmap = {"pie-lex-poxds": "pie-root-ped-walk"}
    out = fm.apply_lemma_overrides("rv", m, gmap, root=ROOT)
    assert out.lemma_lex["pád-"] == {"pie-lex-poxds"} and out.lemma_groups["pád-"] == {"pie-root-ped-walk"}
    assert "ásita-" not in out.lemma_lex and "ásita-" not in out.lemma_groups
    assert out.lemma_lex["kṣáya-"] == {"pie-root-tkjey-cultivate"} and out.lemma_tier["kṣáya-"] == "erratum"
    assert out.lemma_lex["áśva-"] == {"pie-lex-hxekjwos"}
    assert m.lemma_lex["pád-"] == {"pie-lex-pedyeti"}          # the input is not changed
    recs = {"situs": fm.MapRec("situs", "situs", frozenset({"pie-lex-dhgwhey"}), (), "chain", "high", ())}
    assert fm.apply_rec_overrides("lat", recs, root=ROOT)["situs"].ids == {"pie-lex-tkjineti"}
    table = fm.apply_table_overrides("av", {"asita": ("pie-lex-sexmi",), "vadh": ("pie-lex-wedheti",)}, root=ROOT)
    assert "asita" not in table and table["vadh"] == ("pie-lex-wedhh1t",)


def test_old_english_bid_is_bith():
    lm = fm.LangMapping("ang")
    lm.forms["bid"]["bīdan"] += 1
    lz = fm.FormLemmatizer(lm)
    assert lz("bid") == "biþ" and lz("Bid") == "biþ"
    assert fm.FormLemmatizer(lm, form_overrides={})("bid") == "bīdan"


def test_regenerated_av_table():
    rows = {}
    for line in (TABLES / "av.jsonl").read_text("utf-8").splitlines():
        r = json.loads(line)
        rows[r["lemma"]] = set(r["lex_id"])
    for (c, lem), ids in EXPECTED.items():
        if c != "av":
            continue
        if ids:
            assert rows[lem] == ids
        else:
            assert lem not in rows
    assert not WRONG & (rows["pad"] - {"pie-lex-pedyeti"} | rows["vadh"] | rows["kṣaya"])
