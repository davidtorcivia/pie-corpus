"""Stage C Germanic lemma → PIE tables (pie/germanic_new_mapping.py, scripts/build_germanic_new_mapping.py,
data/research/formulas/mapping-overrides/germanic-new.json; docs/research/mapping-precision-germanic-new.md).
Pure-function tests, checks on the committed tables data/research/formulas/mapping/{menota,icepahc,rea-goh,
rea-osx}.jsonl and the override file, and (skipped when raw/ is absent) loader checks on the raw corpora."""

import json
from pathlib import Path

import pytest

from pie import formula_search as fs
from pie import formula_search_multi as fm
from pie import germanic_new_mapping as gm

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "data" / "research" / "formulas" / "mapping"
OVR = ROOT / gm.OVERRIDE_FILE
CORPORA = ("menota", "icepahc", "rea-goh", "rea-osx")
LEX = [json.loads(l) for l in (ROOT / "data/lexicon/lexicon.jsonl").read_text("utf-8").splitlines() if l]
LEX_IDS = {e["id"] for e in LEX}
COPULA = {"pie-lex-h1esti", "pie-lex-h2weseti"}
HAVE_RAW = (ROOT / gm.MENOTA / "catalogue-list.json").exists() and (ROOT / gm.REA).exists()


def table(corpus):
    return [json.loads(l) for l in (TABLES / f"{corpus}.jsonl").read_text("utf-8").splitlines() if l.strip()]


# ---------------------------------------------------------------- spelling and lemma strings

def test_menota_decode_entities_and_letter_variants():
    assert gm.menota_decode("f&oogon;&eth;ur") == "fǫður"
    assert gm.menota_decode("s&aeligacute;mundr") == "sǽmundr"
    assert gm.menota_decode("&slong;kall") == "skall"                 # long s entity
    assert gm.menota_decode("ſkall") == "skall"                       # long s character
    assert gm.menota_decode("ma&nscap;") == "man"                     # small-capital variant → base letter
    assert gm.menota_decode("&kenl;onungr") == "konungr"              # enlarged initial
    assert gm.menota_decode("bꝛeꝼ") == "bref"                         # r rotunda, insular f
    assert gm.menota_decode("v&bar;") == "v"                          # an abbreviation sign is dropped


def test_rea_lemma_alternatives():
    assert gm.rea_lemma("abawesan¦abasin¦wesan¦sin¦wesan") == "abawesan|abasin|wesan|sin"
    assert gm.rea_lemma("haben,haben") == "haben"
    assert gm.rea_lemma("quedan") == "quedan"
    assert gm.rea_is_content("VV¦VA") and gm.rea_is_content("NA")
    assert not gm.rea_is_content("NA¦DD") and not gm.rea_is_content("")


def test_west_germanic_keys():
    assert gm.key_wgm("werđan") == "werðan" == gm.key_wgm("werðan")
    assert gm.key_wgm("hōren") == "hōren" and gm.key_wgm("hōren", True) == gm.key_wgm("horen", True)
    assert gm.key_wgm("thiod", True) == gm.key_wgm("þiod", True) == gm.key_wgm("diod", True)
    assert gm.key_wgm("cunni", True) == gm.key_wgm("kunni", True)
    assert gm.key_wgm("uuort", True) == gm.key_wgm("wort", True)
    assert fm.KEYS["goh"] is gm.key_wgm and fm.KEYS["osx"] is gm.key_wgm


def test_old_norse_skeleton():
    assert gm.skel_non("segia") == gm.skel_non("segja")
    assert gm.skel_non("lutr") == gm.skel_non("hlutr")                 # Old Norwegian h-loss
    assert gm.skel_non("bióða") == gm.skel_non("bjóða")
    assert gm.skel_non("hús") == "hus"                               # h before a vowel stays


def test_modern_icelandic_variants():
    assert "maðr" in gm.modern_to_old_variants("maður")
    assert "konungr" in gm.modern_to_old_variants("konungur")
    assert "andask" in gm.modern_to_old_variants("andast")
    assert "eptir" in gm.modern_to_old_variants("eftir")
    assert "svá" in gm.modern_to_old_variants("svo")
    assert "dýrligr" in gm.modern_to_old_variants("dýrlegur")
    assert "fara" not in gm.modern_to_old_variants("fara")            # the lemma itself is not a variant


def test_kroonen_ocr_and_stem_keys():
    assert gm.kroonen_ocr("hiis") == "hus" and gm.kroonen_ocr("hj6ta") == "hjota"
    assert gm.pgmc_stem_key("*waldaną") == gm.pgmc_stem_key("waldan-")
    assert gm.pgmc_stem_key("*nabją") == gm.pgmc_stem_key("nabja-")
    assert gm.pgmc_stem_key("*huzdą") == gm.pgmc_stem_key("huzda-")


def test_proto_bases_reads_star_hyphen_suffixes():
    d = {"etymology_templates": [{"name": "af", "args": {"1": "gem-pro", "2": "*hailaz", "3": "*-gaz"}}]}
    assert gm.proto_bases(d, "gem-pro") == ["*hailaz"]
    d = {"etymology_templates": [{"name": "etymon", "args": {"1": "gem-pro", "2": ":af", "3": "*hailaz<id:whole>",
                                                             "4": "*-gaz"}}]}
    assert gm.proto_bases(d, "gem-pro") == ["*hailaz"]
    d = {"etymology_templates": [{"name": "suffix", "args": {"1": "gmw-pro", "2": "", "3": "*-ī"}}]}
    assert gm.proto_bases(d, "gmw-pro") == []                         # an affix alone is no base


def _protos(entries):
    p = fm.ProtoDB(ROOT, codes=set())
    for code, d in entries:
        e = fm.parse_entry(d, code)
        p.entries[(code, fs.PieIndex.proto_key(e.word))].append(e)
    return p


def test_base_resolver_affixes_bases_and_fixes():
    idx = fs.PieIndex(LEX)
    kinds = {e["id"]: e.get("kind") for e in LEX}
    protos = _protos([
        ("gem-pro", {"word": "ga-", "pos": "prefix", "etymology_templates": [
            {"name": "inh", "args": {"1": "gem-pro", "2": "ine-pro", "3": "*ḱóm"}}]}),
        ("gem-pro", {"word": "hailaz", "pos": "adj", "etymology_templates": [
            {"name": "inh", "args": {"1": "gem-pro", "2": "ine-pro", "3": "*kóh₂ilos"}}]}),
        ("gem-pro", {"word": "hailagaz", "pos": "adj", "etymology_templates": [
            {"name": "af", "args": {"1": "gem-pro", "2": "*hailaz", "3": "*-gaz"}}]}),
        ("gem-pro", {"word": "hugiz", "pos": "noun", "etymology_templates": [
            {"name": "inh", "args": {"1": "gem-pro", "2": "ine-pro", "3": "*kewk-"}}]}),
    ])
    for e in protos.entries[("gem-pro", "hailagaz")]:
        e.bases = ["*hailaz"]
    fixes = {("gem-pro", "hugiz"): ((), "Kroonen s.v. *hugi-")}
    res = gm.BaseResolver(idx, protos, kinds, True, fixes=fixes)
    assert res.resolve("gem-pro", "*ga-") is None                     # no chain through a prefix page
    assert res.resolve("gem-pro", "*-gaz") is None
    h = res.resolve("gem-pro", "*hailagaz")
    plain = res.resolve("gem-pro", "*hailaz")
    assert h is not None and plain is not None and h.ids == plain.ids and h.how == "base"
    assert res.resolve("gem-pro", "*hugiz") is None                   # a proto row unmaps the term


def _maps(non=None, goh=None, osx=None, bridge=None):
    lms = {}
    for lang, recs in (("non", non or {}), ("goh", goh or {}), ("osx", osx or {})):
        lm = fm.LangMapping(lang)
        for k, (word, ids) in recs.items():
            lm.recs[k] = fm.MapRec(k, word, frozenset(ids), (f"{lang}:{word}",), "chain", "high", ("chain",))
            lm.lemma_words.add(k)
            lm.pos[k].add("verb")
        lms[lang] = lm
    gmap = fs.group_map(LEX)
    return gm.GermanicMappings(lms["non"], lms["goh"], lms["osx"], bridge or {}, {}, {"goh": {}, "osx": {}, "non": {}},
                               LEX, gmap)


def test_map_lemma_alternatives_overrides_and_prefixes():
    maps = _maps(goh={"wesan": ("wesan", {"pie-lex-sh1es"}), "sehan": ("sehan", {"pie-lex-sekweti"}),
                      "sin": ("sīn", {"pie-lex-swe-2"})})
    loose = {L: gm.LooseIndex(getattr(maps, L), maps.gmap) for L in ("non", "goh", "osx")}
    # alternatives with different etyma stay unmapped ...
    r, st = gm.map_lemma(maps, "rea-goh", "wesan|sin", loose)
    assert r is None and st == "ambiguous"
    # ... until a lemma row corrects one part
    ov = {"wesan": (frozenset(COPULA), {"note": "x"}), "sin": (frozenset(COPULA), {"note": "x"})}
    r, st = gm.map_lemma(maps, "rea-goh", "abawesan|wesan|sin", loose, ov)
    assert r is not None and r.ids == COPULA and r.confidence == "low"
    # prefix stripping: gi- + sehan, but not for a word that is itself a headword
    r, st = gm.map_lemma(maps, "rea-goh", "gisehan", loose)
    assert r is not None and r.how == "prefix" and st == "prefix:gi-"
    maps.goh.lemma_words.add("gisehan")
    assert gm.map_lemma(maps, "rea-goh", "gisehan", loose)[0] is None


def test_icelandic_bridge_and_borrowed_sources():
    maps = _maps(non={"maðr": ("maðr", {"pie-lex-mon"})}, bridge={"maður": ["maðr"], "herra": ["herra"]})
    maps.non.rejected["herra"] = "bor:osx"
    loose = {L: gm.LooseIndex(getattr(maps, L), maps.gmap) for L in ("non", "goh", "osx")}
    r, st = gm.map_lemma(maps, "icepahc", "maður", loose)
    assert r is not None and r.ids == {"pie-lex-mon"} and st == "is-bridge"
    assert gm.map_lemma(maps, "icepahc", "herra", loose)[0] is None   # ON herra < OS hērro: no chain
    assert gm._ice_rec(maps, loose["non"], "herra") == (None, "bridge-borrowed")


def test_regeneration_keeps_proto_decision_ancestry():
    from pie import mapping as mp
    from pie.tier2_secure import SecureChecker, build_population

    maps = _maps(non={"fara": ("fara", {"pie-lex-piporti"})})
    maps.non.recs["fara"] = fm.MapRec(
        "fara", "fara", frozenset({"pie-lex-piporti"}),
        ("non:fara", "gem-pro:*faraną", "lexicon-reflex"), "chain", "high", ("chain",))
    ov = {**mp.as_overrides({}), "proto": mp.load_overrides(ROOT)["proto"]}
    recs, _ = gm.corpus_recs(maps, "menota", ["fara", "misfara"], root=ROOT, overrides=ov)
    rows = gm.table_rows("menota", recs)
    assert {r["lemma"] for r in rows} == {"fara", "misfara"}
    for row in rows:
        assert "gem-pro:*faraną" in row["path"]
        assert row["lex_id"] == ["pie-root-per-go_through"]
    checker = SecureChecker.from_population(
        {e["id"]: e for e in LEX}, build_population({"menota": rows}, mp.load_overrides(ROOT)))
    for lemma in ("fara", "misfara"):
        assert checker.match("pie-lex-piporti", "non", "Old Norse", lemma, True)["level"] == "root"


def test_name_lemmas_map_only_through_name_entries():
    maps = _maps(goh={"aram": ("aram", {"pie-lex-h2ermos"})})
    assert gm._name_rec(maps, "goh", "Aram")[0] is None               # the poor-word is not the name Aram
    maps.goh.pos["aram"].add("name")
    assert gm._name_rec(maps, "goh", "Aram")[0] is not None
    toks = [fs.Token("rea-goh", "Aram", "", "", {"tag": "NE"}, True, "noun"),
            fs.Token("rea-goh", "arm", "", "", {"tag": "ADJ"}, True, "adj")]
    assert gm.name_lemmas(toks) == {"Aram"}


# ---------------------------------------------------------------- override file

def test_override_file_rows():
    d = json.loads(OVR.read_text("utf-8"))
    assert d["form"] == []                     # no form rows: load_overrides would key them with KEYS[goh] etc.
    assert d["lemma"] and d["proto"]
    for r in d["lemma"]:
        assert r["corpus"] in CORPORA, r
        assert r["note"].strip() and r["erratum"].strip(), r
        assert set(r["lex_id"]) <= LEX_IDS, r
    for r in d["proto"]:
        assert r["code"] in ("gem-pro", "gmw-pro", "gmq-pro") and r["term"] and r["note"].strip(), r
        assert set(r["lex_id"]) <= LEX_IDS, r
    ov = fm.load_overrides(ROOT)["lemma"]
    assert ov["menota"]["vera"][0] == COPULA and ov["rea-goh"]["sin"][0] == COPULA
    fixes = gm.proto_fixes(ROOT)
    assert fixes[("gem-pro", "hugiz")][0] == ()
    assert fixes[("gem-pro", "ganganą")][0] == ("pie-lex-gjhongh",)


# ---------------------------------------------------------------- committed tables

@pytest.mark.parametrize("corpus", CORPORA)
def test_table_rows(corpus):
    rows = table(corpus)
    assert len(rows) > 1000
    lemmas = [r["lemma"] for r in rows]
    assert len(lemmas) == len(set(lemmas))
    for r in rows:
        assert r["corpus"] == corpus and r["lang"] == gm.CORPORA[corpus]["lang"]
        assert r["licence"] == gm.CORPORA[corpus]["licence"]
        assert r["research_only"] is (corpus.startswith("rea-"))
        assert r["lex_id"] and "pie-lex-sh1es" not in r["lex_id"]
        assert all(i in LEX_IDS or i.startswith("kaikki:") for i in r["lex_id"]), r
    if corpus.startswith("rea-"):
        assert all("NC" in r["licence"] and "research only" in r["licence"] for r in rows)


def test_tables_carry_the_corrections():
    menota, ice = gm.read_table("menota", ROOT), gm.read_table("icepahc", ROOT)
    goh, osx = gm.read_table("rea-goh", ROOT), gm.read_table("rea-osx", ROOT)
    assert set(menota["vera"]) == COPULA and set(ice["vera"]) == COPULA
    assert set(goh["sin"]) == COPULA and set(goh["wesan"]) == COPULA and set(osx["wesan"]) == COPULA
    assert set(goh["abawesan|abasin|anawesan|anasin|wesan|sin"]) == COPULA      # corrected per alternative
    for lem in ("margr", "hugr", "gamall", "eyrir", "ríki", "vetr", "mær"):
        assert lem not in menota, lem                                  # Kroonen: no (inherited) PIE etymology
    for lem in ("hugi", "biginnan", "menigi", "bom"):
        assert lem not in osx, lem
    assert "scriban" not in goh and "luzzil" not in goh                # Latin loan; problematic etymology
    assert menota["mǽla"] == ("pie-root-meh2d-meet",)                  # *maþla- < *mad-tlo-, not *mēla- 'time'
    assert ice["maður"] == menota["maðr"]                              # IcePaHC lemmas reach the Old Norse word
    assert "pie-lex-h1eh1oye" not in set(goh["gangan"]) | set(menota["ganga"])
    assert "Aram" not in goh                                           # a biblical name is not aram 'poor'


def test_coverage_file():
    cov = json.loads((ROOT / "data/research/formulas/germanic-new-coverage.json").read_text("utf-8"))
    for c in CORPORA:
        assert 0.4 < cov[c]["content_token_share"] < 1, c
        assert cov[c]["licence"] == gm.CORPORA[c]["licence"]
    assert "all_years" in cov["icepahc"]


# ---------------------------------------------------------------- loaders (raw corpora; skipped without raw/)

@pytest.mark.skipif(not HAVE_RAW, reason="raw corpora not present")
def test_menota_voluspa_codex_regius():
    ws = gm.menota_words(ROOT / gm.MENOTA / "xml" / "GKS-2365-4to-Vsp.xml", "GKS-2365-4to-Vsp")
    lem = [w.lemma for w in ws if w.lemma]
    assert len(lem) > 1000 and "hlióð" in lem and all("&" not in x for x in lem)   # Hljóðs bið ek allar …
    assert {w.msa for w in ws} & {"NC", "VB", "AJ"}
    assert any(w.stanza for w in ws)


@pytest.mark.skipif(not HAVE_RAW, reason="raw corpora not present")
def test_menota_documents_are_west_norse():
    docs = dict(gm.menota_documents(ROOT))
    assert docs and all(m["language"] in gm.WEST_NORSE for m in docs.values())
    assert "Holm-D-4" not in docs and "GKS-2365-4to-Vsp" in docs


@pytest.mark.skipif(not HAVE_RAW, reason="raw corpora not present")
def test_rea_small_subcorpus():
    rows = gm.rea_tokens(ROOT, subcorpora={"DDD-AD-Kleinere_Altsächsische_Denkmäler"})
    toks = gm.load_rea("rea-osx", ROOT, rows=rows)
    assert len(toks) > 5000 and all(t.corpus == "rea-osx" for t in toks)
    assert not any("¦" in t.lemma for t in toks)
    assert any(t.content for t in toks) and any(not t.content for t in toks)
