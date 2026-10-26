"""Round-3 formula search: mapping chains, keys, loaders and N-branch scoring.
All fixtures are small invented records, not corpus text."""

import collections
import math

from pie import formula_search as fs
from pie import formula_search_multi as fm

LEX = [
    {"id": "pie-lex-wlkwos", "kind": "lexeme", "form": "wĺ̥kʷos", "reflexes": {
        "Proto-Germanic": [{"form": "*wulfaz"}], "Old Norse": [{"form": "ulfr"}]}},
    {"id": "pie-root-werh1-speak", "kind": "root", "form": "werh₁-", "reflexes": {}},
    {"id": "pie-lex-suHnus", "kind": "lexeme", "form": "suHnús", "reflexes": {}},
    {"id": "pie-root-h1ed-eat", "kind": "root", "form": "h₁ed-", "reflexes": {}},
]


def tmpl(name, *args, **kw):
    a = {str(i + 1): v for i, v in enumerate(args)}
    a.update(kw)
    return {"name": name, "args": a}


def test_parse_entry_ancestor_links_and_borrowing():
    d = {"word": "ulfr", "pos": "noun", "etymology_templates": [
        tmpl("inh", "non", "gem-pro", "*wulfaz"), tmpl("cog", "ang", "wulf")]}
    e = fm.parse_entry(d, "non")
    assert e.links == [("gem-pro", "*wulfaz", "inh")] and not e.rejected
    bor = {"word": "kirkja", "pos": "noun", "etymology_templates": [tmpl("bor", "non", "ang", "cirice")]}
    assert fm.parse_entry(bor, "non").rejected.startswith("bor")
    foreign = {"word": "x", "pos": "noun", "etymology_templates": [tmpl("der", "non", "la", "y")]}
    assert fm.parse_entry(foreign, "non").rejected.startswith("foreign")
    disputed = {"word": "x", "pos": "noun", "etymology_templates": [
        tmpl("inh", "non", "gem-pro", "*x"), tmpl("der", "non", "qfa-sub", "")]}
    e = fm.parse_entry(disputed, "non")
    assert not e.rejected and e.disputed


def test_etymon_template_chain():
    a = {"1": "sla-pro", "2": ":inh", "3": "ine-bsl-pro:*sū́ˀnus<ref:x>"}
    assert fm._etymon_parts(a) == [("inh", "ine-bsl-pro", "*sū́ˀnus")]
    d = {"word": "synъ", "pos": "noun", "etymology_templates": [{"name": "ety", "args": a}]}
    assert fm.parse_entry(d, "sla-pro").links == [("ine-bsl-pro", "*sū́ˀnus", "etymon")]


def _protos(entries):
    p = fm.ProtoDB(codes=[])
    for code, d in entries:
        e = fm.parse_entry(d, code)
        p.entries[(code, fs.PieIndex.proto_key(e.word))].append(e)
    return p


def test_resolver_multistep_and_rejected_proto():
    idx = fs.PieIndex(LEX)
    kinds = {e["id"]: e["kind"] for e in LEX}
    protos = _protos([
        ("sla-pro", {"word": "synъ", "pos": "noun", "etymology_templates": [tmpl("inh", "sla-pro", "ine-bsl-pro", "*sū́ˀnus")]}),
        ("ine-bsl-pro", {"word": "sū́ˀnus", "pos": "noun", "etymology_templates": [tmpl("inh", "ine-bsl-pro", "ine-pro", "*suHnús")]}),
        ("gem-pro", {"word": "kaisaraz", "pos": "noun", "etymology_templates": [tmpl("bor", "gem-pro", "la", "Caesar")]}),
    ])
    res = fm.Resolver(idx, protos, kinds, pseudo=False)
    h = res.resolve("sla-pro", "*synъ")
    assert h.ids == {"pie-lex-suHnus"} and h.path[0] == "sla-pro:*synъ" and h.steps == 2
    assert res.resolve("gem-pro", "*kaisaraz") is None
    # a proto-form the lexicon lists as a reflex resolves to that lexeme directly
    assert res.resolve("gem-pro", "*wulfaz").ids == {"pie-lex-wlkwos"}


def test_build_lang_mapping_sources_and_base_chain():
    protos = _protos([])
    ents = [fm.parse_entry({"word": "ulfr", "pos": "noun", "etymology_templates": [
                tmpl("inh", "non", "gem-pro", "*wulfaz")], "forms": [{"form": "ulfs", "tags": ["genitive"]}]}, "non",
                keep_forms=True),
            fm.parse_entry({"word": "ylfingr", "pos": "noun", "etymology_templates": [
                tmpl("suffix", "non", "ulfr", "-ingr")]}, "non"),
            fm.parse_entry({"word": "orð", "pos": "noun", "etymology_templates": [
                tmpl("root", "non", "ine-pro", "*werh₁-")]}, "non")]
    lm = fm.build_lang_mapping("non", LEX, protos, entries=ents, pseudo=False)
    r = lm.recs["ulfr"]
    assert r.ids == {"pie-lex-wlkwos"} and r.confidence == "high" and set(r.sources) == {"chain", "lexicon"}
    assert lm.recs["ylfingr"].how == "base" and lm.recs["ylfingr"].confidence == "low"
    assert lm.recs["orð"].how == "root"
    assert "ulfr" in lm.forms["ulfs"]


def test_keys():
    assert fm.key_got("𐍅𐌿𐌻𐍆𐍃") == "wulfs"
    assert fm.key_xcl("ar̄nowm") == fm.key_xcl("aṙnum") == "aṙnum"
    assert fm.key_cu("сынъ") == fm.key_cu("сꙑнъ")
    assert fm.key_ang("gōd") != fm.key_ang("god") and fm.key_ang("gōd", True) == "god"
    assert fm.key_hit("ḫatteššar") == fm.key_hit("ḫateššar")
    assert fm.hit_lemma_stems("ēd-/ad-@essen") == ["ēd", "ad"]
    assert fm.hit_lemma_stems("① antezzi(a)-") == ["antezzi", "antezzia"]
    assert fm.lv_diminutive_variants("kalniņā")[0] == "kalns"
    assert "hef" in fm.non_clitic_variants("hefk")


def test_hit_lemma_selection():
    a = {"mrp0sel": " 1 ", "mrp1": "ēd-/ad-@essen@3PL.PST@I.2.4@", "mrp2": "x@y@@"}
    assert fm.hit_lemma(a) == ("ēd-/ad-@essen", "3PL.PST")
    assert fm.hit_lemma({"mrp0sel": " ", "mrp1": "a@b@@", "mrp2": "c@d@@"}) is None       # ambiguous
    assert fm.hit_lemma({"mrp0sel": " 1 ", "mrp1": "EZEN₄@Fest@@"}) is None                # Sumerogram
    assert fm.hit_lemma({"mrp0sel": " 1 ", "mrp1": "LUGAL=u-@König@@"}) is None


def test_hittite_gloss_check():
    rec = fm.MapRec("eku", "ekuzi", frozenset({"x"}), (), "chain", "high", (), gloss="to drink")
    assert fm.hittite_gloss_ok("eku-/aku-@trinken", rec)
    assert not fm.hittite_gloss_ok("pai-/pā-@gehen", rec)


def test_kloekhorst_damaged_key_and_fuzzy_pie():
    assert fm.hit_damaged_key("ḫalki-") == fm.hit_damaged_key("alki")
    assert fm.pie_fuzzy_key("*h₁ed-") == fm.pie_fuzzy_key("*h1ed-")
    fz = fm.FuzzyPie(LEX)
    ids, how = fz.lookup("*h1ed-ri-")
    assert ids == {"pie-root-h1ed-eat"} and how == "root-of-form"


def test_form_lemmatizer_and_ambiguity():
    lm = fm.LangMapping("non")
    lm.recs["sonr"] = fm.MapRec("sonr", "sonr", frozenset({"pie-lex-suHnus"}), ("non:sonr",), "chain", "high", ())
    lm.recs["ulfr"] = fm.MapRec("ulfr", "ulfr", frozenset({"pie-lex-wlkwos"}), ("non:ulfr",), "chain", "high", ())
    lm.forms["syni"]["sonr"] += 1
    lm.forms["ulfa"]["ulfr"] += 1
    lm.forms["ulfa"]["sonr"] += 1
    lemz = fm.FormLemmatizer(lm)
    assert lemz("syni") == "sonr" and lemz("xyz").startswith("?")
    toks = [fs.Token("non", lemz(w), "", "L 1", {"line": "1"}, True, "other") for w in ("syni", "ulfa")]
    m, recs = fm.multi_lemma_mapping(toks, lm)
    assert m.lemma_lex["sonr"] == {"pie-lex-suHnus"}
    assert "ulfr|sonr" in m.ambiguous or "sonr|ulfr" in m.ambiguous     # two etyma: dropped


def _counts(units):
    return fs.count_units([[frozenset(u) for u in unit] for unit in units])


def _spec(name, branch, tr=False):
    return fm.CorpusSpec(name, branch, "x", "test", "line", translation=tr)


def test_branch_logp_single_corpus_is_round2_exact_test():
    c = _counts([["x", "y"], ["x"], ["y"], ["z"]])
    lp, o, per = fm.branch_logp([("a", c)], ("x", "y"))
    assert o == 1 and math.isclose(lp, fs.hypergeom_logsf(1, 2, 2, 4))


def test_score_branches_classes_translation_and_calques():
    many = [["q"]] * 40
    strong = _counts([["x", "y"]] * 5 + many)
    weak = _counts([["x", "y"], ["x"], ["y"]] + many)
    specs = {"g": _spec("g", "Greek"), "v": _spec("v", "Indo-Iranian"), "o": _spec("o", "Germanic", True),
             "s": _spec("s", "Balto-Slavic", True), "h": _spec("h", "Anatolian")}
    rows = fm.score_branches({"g": strong, "v": weak}, specs)
    assert len(rows) == 1 and fm.ranking_class(rows[0]) == "c"
    # two translation corpora merge into one witness: Greek + translation = class b
    rows = fm.score_branches({"g": strong, "o": weak, "s": weak}, specs)
    assert rows[0]["n_witnesses"] == 2 and fm.ranking_class(rows[0]) == "b"
    assert any(w.branch.startswith("translation:") for w in rows[0]["witnesses"])
    rows = fm.score_branches({"g": strong, "v": weak, "h": weak}, specs)
    assert fm.ranking_class(rows[0]) == "a"
    # a calqued co-occurrence is discarded: the translation witness disappears
    rows = fm.score_branches({"g": strong, "o": weak}, specs, calques={"o": {("x", "y"): 1}})
    assert rows == []
    # no corpus significant: no candidate
    assert fm.score_branches({"v": weak, "h": weak}, specs) == []


def test_calque_counts():
    gnt = {"MATT 1.1": {("x", "y")}}
    units = {"o": [("MATT 1.1", [frozenset({"x"}), frozenset({"y"})]), ("MATT 1.2", [frozenset({"x"}), frozenset({"y"})])]}
    assert fm.calque_counts(units, gnt)["o"][("x", "y")] == 1


def test_proiel_and_dcs_loaders(tmp_path, monkeypatch):
    d = tmp_path / fm.PROIEL_DIR / "proiel"
    d.mkdir(parents=True)
    (d / "t.xml").write_text(
        '<proiel><source id="t" language="got"><div><sentence id="1">'
        '<token id="1" form="a" citation-part="MATT 1.1" lemma="wulfs" part-of-speech="Nb" morphology="-s---mn--i" head-id="2" relation="sub"/>'
        '<token id="2" form="b" citation-part="MATT 1.1" lemma="itan#1" part-of-speech="V-" morphology="3spia----i" relation="pred"/>'
        '<token id="3" form="c" citation-part="MATT 1.1" lemma="jah" part-of-speech="C-" morphology="---------n"/>'
        '<token id="4" empty-token-sort="P" citation-part="MATT 1.1"/>'
        '</sentence></div></source></proiel>', "utf-8")
    toks = fm.load_proiel(["proiel/t.xml"], "got", root=tmp_path)
    assert [t.lemma for t in toks] == ["wulfs", "itan", "jah"]
    assert [t.content for t in toks] == [True, True, False] and toks[0].head == 1
    assert toks[0].units["verse"] == "MATT 1.1"
    dd = tmp_path / fm.DCS_DIR / "Atharvaveda (Śaunaka)"
    dd.mkdir(parents=True)
    (dd / "x-0000-AVŚ, 1, 1-1.conllu").write_text(
        "## chapter: AVŚ, 1, 1\n# sent_id = 1_1\n1\tdevāḥ\tdeva\tNOUN\t_\tCase=Nom\t0\troot\t_\t_\n"
        "2\tca\tca\tCCONJ\t_\t_\t1\tcc\t_\t_\n\n", "utf-8")
    toks = fm.load_dcs(("Atharvaveda (Śaunaka)",), root=tmp_path)
    assert [(t.lemma, t.content, t.locus) for t in toks] == [("deva", True, "AVŚ, 1, 1.s1"), ("ca", False, "AVŚ, 1, 1.s1")]


def test_kloekhorst_entry_parser(tmp_path):
    d = tmp_path / fm.KLOEKHORST
    d.mkdir(parents=True)
    (d / f"{fm.KH_FIRST_FILE}.txt").write_text(
        " \nedzi / ad- (Ia3) ‘to eat’: 1sg.pres.act. e-et-mi.\n  PIE *h1ed-, *h1d-\n \n"
        "andaš-: see anda(i)š-\n \nantezzi(a)- (adj.) ‘first’: nom.sg.c. x.\n  PIE *h2ent-etiHo- \n", "utf-8")
    ents = fm.kloekhorst_entries(tmp_path)
    assert [e["head"] for e in ents] == ["edzi / ad-", "antezzi(a)-"]
    assert ents[0]["pie"] == ["*h1ed-", "*h1d-"] and ents[1]["stems"] == ["antezzi", "antezzia"]
