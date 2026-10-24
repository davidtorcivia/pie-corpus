"""Classical Armenian (PROIEL + DMHP), Tocharian A and Old Albanian lemma → PIE tables
(pie/arm_toch_alb_mapping.py, scripts/build_arm_toch_alb_mapping.py, mapping-overrides/arm-toch-alb.json)."""

import collections
import json
from pathlib import Path

import pytest

from pie import arm_toch_alb_mapping as am
from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "data" / "research" / "formulas" / "mapping"
OVR = ROOT / "data" / "research" / "formulas" / "mapping-overrides" / "arm-toch-alb.json"
LEXICON = ROOT / "data" / "lexicon" / "lexicon.jsonl"


def _lex_ids():
    return {json.loads(l)["id"] for l in LEXICON.read_text("utf-8").splitlines() if l.strip()}


def _table(corpus):
    out = {}
    for line in (TABLES / f"{corpus}.jsonl").read_text("utf-8").splitlines():
        r = json.loads(line)
        out[r["lemma"]] = r
    return out


# ---------------------------------------------------------------- normalisers


def test_armenian_transliteration_matches_proiel():
    conv = am.DmhpLemma(["Tēr", "ownim", "Astowac", "ar̄nem", "kʻoyr"])
    assert conv("տէր") == "Tēr"                       # PROIEL's capitalised lemma
    assert conv("ունիմ") == "ownim"                   # ու → ow
    assert conv("առնեմ") == "ar̄nem"                   # ռ → r̄
    assert conv("քոյր") == "kʻoyr"
    assert conv("այս (սա)") == "ays"                  # DMHP's lemma variant in brackets dropped
    assert am.arm_translit("օր") == "ōr"
    # the generic key drops ō, so 'day' collided with the clitic r; the module key keeps it
    assert am.key_xcl("ōr") != am.key_xcl("r") and fm.key_xcl("ōr") == fm.key_xcl("r")
    assert am.key_xcl("unim") == am.key_xcl("ownim")  # Martirosyan u vs PROIEL ow
    assert am.key_xcl("aɫač‘em") == am.key_xcl("ałačʻem")


def test_tocharian_normalisation():
    assert am.toch_norm("TAmyo") == "tämyo"
    assert am.toch_norm("tRAṅKAṢ\\") == "träṅkäṣ"
    assert am.toch_norm("KAl(pnā)") == "kälpnā"
    assert am.toch_norm("ts.7") is None and am.toch_norm("_") is None and am.toch_norm("PKA_\\") is None


def test_albanian_normalisation_and_skeleton():
    assert am.alb_norm("giξξè", "bogdani") == "gjithë"
    assert am.alb_norm("maξ", "bogdani") == "madh"
    assert am.alb_norm("chieλèt", "bogdani") == "qiellët"
    assert am.alb_skeleton(am.alb_norm("Chiofte", "bardhi")) == am.alb_skeleton("qoftë")
    assert am.alb_norm("ћi", "buzuku") == "qi"
    assert am.alb_norm("ɛot", "buzuku") == "zot"
    assert am.alb_norm("teh", "buzuku") == "të"
    # Buzuku's ſ is s or sh, ξ th or dh: the skeleton merges them
    assert am.alb_skeleton("shpirt") == am.alb_skeleton(am.alb_norm("ſpirt", "buzuku"))
    assert am.alb_skeleton("dhe") == am.alb_skeleton("the")
    assert "venë" in am.gheg_variants("verë") and "grue" in am.gheg_variants("grua")


# ---------------------------------------------------------------- systematic rules (no raw data needed)


def _kentry(word, roman=None, links=(), rejected=None, hedged=False, gloss="", hints=None):
    e = fm.Entry(word, "noun", roman=roman, links=list(links), rejected=rejected, glosses=gloss)
    return am.KEntry(e, hedged, hints or {})


def test_postprocess_drops_hedged_borrowed_and_unresolved_homographs():
    lexd = {"pie-root-a-fit": {"id": "pie-root-a-fit", "kind": "root", "form": "h₂er-", "meaning": ["to fit"]},
            "pie-root-a-take": {"id": "pie-root-a-take", "kind": "root", "form": "h₂er-", "meaning": ["to take"]},
            "pie-lex-x": {"id": "pie-lex-x", "kind": "word", "form": "x", "meaning": ["thing"]}}
    lm = fm.LangMapping("xcl")
    rec = lambda k, ids, how="lexicon": fm.MapRec(k, k, frozenset(ids), (f"xcl:{k}", "ine-pro:*x"), how, "high", (how,))
    lm.recs = {"hanem": rec("hanem", {"pie-lex-x"}, "chain"), "bazanem": rec("bazanem", {"pie-lex-x"}),
               "arnem": rec("arnem", {"pie-root-a-fit", "pie-root-a-take"}, "root"),
               "arar": rec("arar", {"pie-root-a-fit", "pie-root-a-take"}, "root"),
               "gom": rec("gom", {"pie-lex-x"})}
    kents = [_kentry("hanem", "hanem", links=[("ine-pro", "*x", "inh")], hedged=True),
             _kentry("bazanem", "bazanem", rejected="bor:ira"),
             _kentry("arnem", "arnem", links=[("ine-pro", "*h₂er-", "root")], hints={"her": {"fit"}}),
             _kentry("arar", "arar"),
             # a hedged homograph beside an entry without etymology does not veto (gom 'stall' / gom 'be')
             _kentry("gom", "gom", hedged=True), _kentry("gom", "gom")]
    ch = am.postprocess(lm, kents, lexd, "xcl")
    assert ch["hanem"] == "hedged" and "hanem" not in lm.recs
    assert ch["bazanem"] == "borrowed" and "bazanem" not in lm.recs
    assert lm.recs["arnem"].ids == {"pie-root-a-fit"} and ch["arnem"] == "homograph-resolved"
    assert ch["arar"] == "homograph" and "arar" not in lm.recs
    assert "gom" in lm.recs


def test_hedge_patterns():
    for t in ("The origin is uncertain. Perhaps from *x.", "Uncertain. Usually treated as a cognate of …",
              "From earlier *լէնիմ (*lēnim), of uncertain origin. Perhaps from Proto-Indo-European *ḱleyn-",
              "From Proto-Tocharian *al-, of uncertain further origin.", "Disputed. Possibilities include: …",
              "Ačaṙyan leaves the origin open."):
        assert am._HEDGE.match(t), t
    for t in ("From Proto-Indo-European *deh₃-.", "Probably from Proto-Indo-European *gʷeh₂- (“to come, step”)"):
        assert not am._HEDGE.match(t), t


def test_suffix_lemmatizer_keeps_unique_answers_only():
    lm = fm.LangMapping("xto")
    lm.forms["wäl"]["wäl"] += 1
    lm.pos["wäl"].add("noun")
    lm.forms["träṅk"]["träṅk"] += 1
    lm.pos["träṅk"].add("verb")
    lz = am.SuffixLemmatizer(lm, am.TOCH_NOUN_END, am.TOCH_VERB_END)
    assert lz("wälyo") == "wäl"                      # instrumental -yo on the oblique
    assert lz("träṅkäṣ") == "träṅk"                  # 3sg present on a verb root
    assert lz("xyzzy").startswith("?")


# ---------------------------------------------------------------- override file


def test_override_rows_are_well_formed_and_do_not_collide():
    d = json.loads(OVR.read_text("utf-8"))
    ids = _lex_ids()
    assert d.get("form") == []                       # 'sq'/'xto' are not in fm.KEYS unless this module is imported
    seen = set()
    for r in d["lemma"]:
        assert r["corpus"] in ("xcl", "xto", "sqo")
        assert r["note"] and len(r["note"]) > 20
        assert all(i in ids for i in r["lex_id"]), r
        assert (r["corpus"], r["lemma"]) not in seen
        seen.add((r["corpus"], r["lemma"]))
    # load_overrides concatenates the files in sorted order (later rows win): no lemma may also have an
    # east.json row, or one of the two would be lost silently
    east = json.loads((OVR.parent / "east.json").read_text("utf-8"))
    assert not seen & {(r["corpus"], r["lemma"]) for r in east["lemma"]}


# ---------------------------------------------------------------- generated tables


def test_xcl_table_serves_proiel_and_dmhp_with_licences():
    t = _table("xcl")
    corpora = collections.Counter(c for r in t.values() for c in r["corpora"])
    assert corpora["proiel"] > 150 and corpora["dmhp"] > 450
    for r in t.values():
        assert r["corpus"] == "xcl" and r["licence"]["kaikki"]
        assert set(r["corpora"]) <= set(r["licence"])
        if "dmhp" in r["corpora"]:
            assert r["dmhp_lemmas"] and all(any("Ա" <= ch <= "և" for ch in x) for x in r["dmhp_lemmas"])
    assert "Tēr" in t and "տէր" in t["Tēr"]["dmhp_lemmas"]


def test_xcl_known_errors_corrected():
    t = fm.apply_table_overrides("xcl", {k: tuple(r["lex_id"]) for k, r in _table("xcl").items()})
    assert t["ownim"] == ("pie-root-h1ep-grab",)                 # was *sesónh₂e
    assert t["ar̄nem"] == ("pie-root-h2er-fit",)                  # was three homograph *h₂er- roots
    assert t["ayg"] == ("pie-lex-h2ewsoxs",)                     # *h₁eyHw- 'yew' removed
    assert t["mard"] == ("pie-lex-mrtos",) and t["mardik"] == ("pie-lex-mrtos",)
    assert t["gam"] == ("pie-root-weh2dh-go",)
    assert set(t["Tēr"]) == {"pie-lex-doxm", "pie-lex-h2nexr"}
    for gone in ("hanem", "bažanem", "agarak", "bowr̄n", "linim", "hawt", "ertʻam", "d", "n"):
        assert gone not in t, gone                                # uncertain etymology, loan, or key collision


def test_toch_and_alb_tables():
    ids = _lex_ids()
    for corpus, src in (("xto", "titus-xto"), ("sqo", "titus-sqo")):
        t = _table(corpus)
        assert len(t) > 150
        for lem, r in t.items():
            assert src in r["licence"] and "kaikki" in r["licence"]
            assert not lem.startswith("?") and " " not in lem
            assert all(i in ids or i.startswith("kaikki:") for i in r["lex_id"])
    sqo = fm.apply_table_overrides("sqo", {k: tuple(r["lex_id"]) for k, r in _table("sqo").items()})
    assert sqo["kam"] == ("pie-root-kap-seize",)
    assert "regj" not in sqo                                      # 'king' (Lat. rēgem) beside 'tan'
    xto = _table("xto")
    assert "wäs" not in xto                                       # 'gold' (uncertain) beside 'poison'


@pytest.mark.skipif(not (ROOT / "raw" / "daughters" / "armenian-dmhp-matenagirk").exists(), reason="raw corpora absent")
def test_dmhp_tokens_and_content_filter():
    toks = am.dmhp_tokens()
    assert len(toks) > 500_000
    c = collections.Counter(t.pos for t in toks)
    assert c["V"] > 100_000 and c["N+Com"] > 100_000
    t = next(t for t in toks if t.pos == "I+Prep@N+Com")          # z- + noun: content, lemma is the noun
    assert t.content
