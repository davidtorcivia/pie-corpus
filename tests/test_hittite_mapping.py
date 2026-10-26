"""Hittite (TLHdig) content words, names, lemma keys and the EDHIL route to PIE (pie/hittite_mapping.py).
All fixtures are small invented records in the formats of TLHdig, the EDHIL text layer and the lexicon;
no corpus or book text."""

from pie import formula_search_multi as fm
from pie import hittite_mapping as hm


def test_formation_gate_distinguishes_derivatives_and_complete_endings():
    for lemma in ("mar=nu-@verschwinden lassen", "mar=išk-@verschwinden",
                  "mar=iye/a-@verschwinden", "mar=anna-@verschwinden"):
        assert not hm.formation_matches(lemma, "*mér-t")
    assert hm.formation_matches("u=nu-@schmücken", "*h3u-néu-ti")
    assert hm.formation_matches("eš-@sein", "*h1és-ti")  # not a suffix
    assert hm.same_formation("*h1ép-ti", "h₁épti")
    assert hm.same_formation("*\x02éi-to", "ḱéytor")
    for a, b in (("*dhéh1-ti", "dʰéh₁t"), ("*sup-tó", "swépt"),
                 ("*póh2s-ei", "péh₂sti"), ("*su-no-H-ei", "sunéHti")):
        assert not hm.same_formation(a, b)


def test_formation_gate_applies_to_chain_and_edhil_without_losing_evidence():
    lex = [dict(id="pie-root-mer-die", kind="root", form="mer-", meaning=["to disappear"]),
           dict(id="pie-lex-mert", kind="word", form="mért", pos="verb",
                parents=["pie-root-mer-die"], meaning=["to disappear"])]
    entry = _entry([["*mér-t"]], doubtful=False, gloss="to disappear")
    entry.update(stems=["mer", "mar"], printed="577")
    lemma = "mar=nu-@verschwinden lassen"
    for how in ("chain", "lexicon", "kloekhorst"):
        rec = fm.MapRec("mar", "mar", frozenset({"pie-lex-mert"}), ("ine-pro:*mér-t",),
                        how, "high", (), "")
        result = hm.check_formations({lemma: rec}, lex, [entry])[lemma]
        assert result.ids == {"pie-root-mer-die"}
        assert result.path == rec.path
        assert "577" in result.sources[-1] and "*mér-t" in result.sources[-1]
    result = hm.resolve_entry(entry, lemma, fm.FuzzyPie(lex), hm.RootIndex(lex),
                              {e["id"]: e for e in lex})
    assert result == ({"pie-root-mer-die"}, "*mér-t", "kloekhorst-root")


def test_blind_review_families_and_wrong_etymologies():
    from pie import mapping as mp
    main = hm.read_union_table(doubtful=False)
    union = hm.read_union_table()
    for lemma in ("laḫ=u-@gießen", "tarn=a-@lassen", "kara/ep(p)-@fressen"):
        assert lemma not in union
        assert mp.decisions_for("hit", lemma)
    families = {
        "pie-root-mer-die": ["mar=nu-@verschwinden lassen", "mer=nu-@verschwinden lassen"],
        "pie-root-peh2-protect": ["paḫš=@beschützen", "paḫḫaš=@beschützen", "paḫḫaš=nu-@beschützen"],
        "pie-root-sewh3-be_become_full": ["šunn=a-@füllen", "šunn=iye/a-@füllen", "šunn=išk-@füllen"],
        "pie-root-swep-sleep": ["šup=@schlafen", "šupp=@schlafen", "šupp=a-@schlafen"],
        "pie-root-dheh1-do": ["te-/tar-@sprechen"],
        "pie-root-ses-rest": ["šaš=nu-@zum Schlafen veranlassen", "šašša=nu-@zum Schlafen veranlassen"],
    }
    for root, lemmas in families.items():
        for lemma in lemmas:
            assert main[lemma] == (root,)
    assert main["mer-/mar-@verschwinden"] == ("pie-lex-mert",)
    assert main["ki=@liegen"] == ("pie-lex-kjeytor",)


def test_derivative_root_fallback_still_rejects_ambiguous_and_wrong_sense_matches():
    lex = [dict(id="pie-root-x", kind="root", form="lah-", meaning=["to bark"]),
           dict(id="pie-root-y", kind="root", form="lah-", meaning=["to hide"])]
    assert hm.resolve_form(["*lah-"], "laḫḫ=išk-@reisen", "to travel", fm.FuzzyPie(lex),
                           {e["id"]: e for e in lex}) is None


def test_shared_plural_does_not_prove_hi_and_mi_are_the_same_formation():
    lex = [dict(id="pie-root-mer", kind="root", form="mer-"),
           dict(id="pie-lex-merti", kind="word", form="mérti", pos="verb",
                stems=["mérti", "mrenti"], parents=["pie-root-mer"])]
    entry = _entry([["*mor-ei", "*mr-enti"]], doubtful=False, gloss="to disappear")
    entry.update(stems=["mar"], printed="577")
    lemma = "mar-@verschwinden"
    rec = fm.MapRec("mar", "mar", frozenset({"pie-lex-merti"}), (), "chain", "high", (), "")
    assert hm.check_formations({lemma: rec}, lex, [entry])[lemma].ids == {"pie-root-mer"}

LEX = [
    {"id": "pie-root-bhers-top", "kind": "root", "form": "bʰers-", "variants": [], "meaning": ["top, tip, point"]},
    {"id": "pie-root-h1erH-wash", "kind": "root", "form": "h₁erH-", "variants": [], "meaning": ["to wash"],
     "meaning_de": "'waschen'"},
    {"id": "pie-root-h2en-draw", "kind": "root", "form": "h₂en-", "variants": [], "meaning": ["to draw (water), scoop"]},
    {"id": "pie-root-gjeys-turn", "kind": "root", "form": "ǵeys-", "variants": [], "meaning": ["to turn, turn oneself"]},
    {"id": "pie-lex-h1epti", "kind": "derivative", "form": "h₁épti", "variants": [], "meaning": []},
    {"id": "pie-lex-h2us", "kind": "derivative", "form": "h₂us-", "variants": [], "meaning": [],
     "parents": ["pie-root-h2ews-draw_water"]},
    {"id": "pie-root-h2ews-draw_water", "kind": "root", "form": "h₂ews-", "variants": [], "meaning": ["to draw water"]},
]


# ---------------------------------------------------------------- content words and names

def test_clitic_chains_pronouns_and_particles_are_not_content():
    chain = "{ a → CONNn=PPRO.3SG.N.NOM} { b → CONNn=PPRO.3SG.N.ACC}"
    assert fm.hit_morph_tags(chain) == ["CONNn", "CONNn"]
    assert fm.hit_word_kind("n=at", chain) == "function"
    assert fm.hit_pos("n=at", chain) == ("other", False)            # NOM in the morphology, still no noun
    assert fm.hit_pos("n=aš=kan", "CONNn=PPRO.3SG.C.NOM=OBPk") == ("other", False)
    assert fm.hit_pos("ta=aš", "CONNt=PPRO.3SG.C.NOM") == ("other", False)
    assert fm.hit_word_kind("nu=war=an", "") == "function"          # no gloss, a connective first: by the lemma
    assert fm.hit_pos("apa-@er", "DEM2/3.NOM.SG.C", "20") == ("other", False)
    assert fm.hit_pos("kui-@welcher", "REL.NOM.SG.C", "22") == ("other", False)
    assert fm.hit_pos("uk@ich", "{ a → PPROa.1SG.NOM}", "32") == ("other", False)
    # content: verbs and nominals; a quantifier adjective (QUANall) is content like an adjective
    assert fm.hit_pos("parš=@zerbrechen", "3SG.PRS.MP", "III.1.8") == ("verb", True)
    assert fm.hit_pos("wātar@Wasser", "{ a → NOM.SG.N} { b → ACC.SG.N}", "14") == ("noun", True)
    assert fm.hit_pos("ḫumant-@jeder; ganz", "{ a → QUANall.NOM.SG.N}", "27.3") == ("noun", True)
    # a noun lemma that merely begins with n / t is not a clitic chain
    assert fm.hit_word_kind("nepiš=ant-@(ERG) Himmel", "ERG.SG") == "word"


def test_names_are_not_content():
    assert fm.hit_pos("nerik=@Nerik", "{ a → GN.NOM.SG(UNM)} { b → GN.ACC.SG(UNM)}", "39.1") == ("name", False)
    assert fm.hit_pos("ḫep=a(t)(u)-@Ḫepat", "DN.NOM.SG(UNM)", "35.10.6") == ("name", False)
    assert fm.hit_pos("tutḫali=a-@Tudḫaliya", "PNm.NOM.SG.C", "38.2") == ("name", False)
    # an analysis without a name tag ('…' = clitic form) is still a name by TLHdig's inflection class
    assert fm.hit_word_kind("telipin=u-@Tele/ipinu", "{ a → …:D/L.SG}", "35.3.1") == "name"
    assert fm.hit_word_kind("ḫattuš=a-@Ḫattuša", "GN.D/L.SG", "39.2") == "name"


def test_selection_marks_are_dropped_from_the_lemma():
    a = {"mrp0sel": " 1 ", "mrp1": "Ⓐ apa-@er@DEM2/3.NOM.SG.C@20@"}
    assert fm.hit_analysis(a) == ("apa-@er", "DEM2/3.NOM.SG.C", "20")
    # a marked and an unmarked proposal of one lemma are one lemma, not an ambiguity
    b = {"mrp0sel": " ", "mrp1": "⓷Ⓐ kui-@welcher@REL.NOM.SG.C@22@", "mrp2": "kui-@welcher@REL.ACC.SG.C@22@"}
    assert fm.hit_lemma(b) == ("kui-@welcher", "REL.NOM.SG.C")


# ---------------------------------------------------------------- lemma keys

def test_tlhdig_stem_normalization():
    assert fm.hit_lemma_stems("iye/a-@machen") == ["iye", "iya"]                 # a one-letter alternation
    assert fm.hit_lemma_stems("ēd-/ad-@essen") == ["ēd", "ad"]                   # two stems
    assert fm.hit_lemma_stems("šak(k)-, šek(k)-@wissen") == ["šak", "šakk", "šek", "šekk"]
    assert fm.hit_lemma_stems("ḫatr=ā(e)-@mitteilen") == ["ḫatrā", "ḫatrāe"]
    assert fm.hit_lemma_stems("išpart/za-@entkommen") == ["išpart", "išparza"]   # a consonant: two stems
    assert fm.hit_lemma_stems("ḫaršar/ḫarš(ša)n-@Kopf") == ["ḫaršar", "ḫaršn", "ḫarššan"]
    assert fm.hit_lemma_stems("kurš=i-2@Tablett(?)") == ["kurši"]                # homograph digit off
    assert fm.hit_lemma_stems("Ⓐ dai-/te-/ti(ya)-@setzen") == ["dai", "te", "ti", "tiya"]
    assert fm.hit_damaged_key("ḫuwaššanna") == fm.hit_damaged_key("uaššana") == "uasana"
    assert fm.hit_damaged_key("iye") == "ie"                                     # y deleted like EDHIL's lost i̯
    assert "ar" in hm.lemma_keys("arr=a-@waschen")                              # the stem without its -a-
    assert "mem" in hm.lemma_keys("mem=išk-@sprechen")                          # imperfective -išk-
    assert "pes" in hm.lemma_keys("pešš=iye/a-@werfen")


def test_edhil_stem_pattern_treats_a_lost_glyph_as_an_optional_vowel():
    p = hm.edhil_stem_pattern("m\x02ma")                                         # mēma-, ē lost in the text layer
    assert p.fullmatch(fm.hit_damaged_key("mema")) and not p.fullmatch("mima-")
    assert hm.edhil_stem_pattern("\x02alzai").fullmatch(fm.hit_damaged_key("ḫalzai"))
    assert hm.edhil_stem_pattern("\x06emi\x05e").fullmatch(fm.hit_damaged_key("wemiye"))
    ents = [{"stems": ["m\x02ma", "m\x02mi"], "gloss": "to speak"}, {"stems": ["mall"], "gloss": "to grind"}]
    ei = hm.EdhilIndex(ents)
    assert ei.candidates("mem=a-@sprechen") == [0]


# ---------------------------------------------------------------- the PIE root resolver

def test_root_skeletons_normalize_notation():
    assert hm.root_skeletons("*bhrs-ské/ó-") == [("bh", "r", "s")]
    assert hm.lex_root_skeletons("bʰers-") == [("bh", "r", "s")]                 # e-grade = zero grade
    assert hm.root_skeletons("*h1órh1-ei") == [("H1", "r", "H1")]
    assert hm.skeletons_agree(hm.root_skeletons("*h1órh1-ei")[0], hm.lex_root_skeletons("h₁erH-")[0])
    assert hm.root_skeletons("*h1/3ók-ei") == [("H13", "Kk")]                     # h1/3 kept as one laryngeal
    assert hm.root_skeletons("*mé-molh2-") == [("m", "l", "H2")]                  # past a reduplication
    assert hm.skeletons_agree(hm.root_skeletons("*\x02\x03\x03éis-o")[0], hm.lex_root_skeletons("ǵeys-")[0])
    assert hm.root_skeletons("*-d") == [] and hm.root_skeletons("*h1poi+*h1s-ie/o-") == []


def test_root_resolver_accepts_a_correct_root_and_rejects_a_wrong_meaning():
    roots = hm.RootIndex(LEX)
    gmap = {e["id"]: e["id"] for e in LEX}
    ids, form = hm.resolve_root(["*h1órh1-ei", "*h1rh1-énti"], "arr=a-@waschen", "to wash", roots, gmap)
    assert ids == {"pie-root-h1erH-wash"} and form == "*h1órh1-ei"
    # parš- 'to break' *bhrs-: the skeleton matches *bʰers- 'top, tip', the meaning does not
    assert roots.lookup(hm.root_skeletons("*bhrs-")[0]) == ["pie-root-bhers-top"]
    assert hm.resolve_root(["*bhrs-"], "parš=@zerbrechen", "to break", roots, gmap) is None
    # the German gloss can agree through LIV's meaning_de
    assert hm.gloss_agrees("arr=a-@waschen", "", [LEX[1]])


def test_form_resolver_needs_meaning_for_a_short_stem():
    fz, by_id = fm.FuzzyPie(LEX), {e["id"]: e for e in LEX}
    assert hm.resolve_form(["*h1ép-ti"], "ēp(p)-/ap(p)-@fassen", "to take", fz, by_id) == ({"pie-lex-h1epti"}, "*h1ép-ti")
    # *h₂us- is a tree-path stub of *h₂ews- 'draw water': not ḫuiš- 'to live'
    assert hm.resolve_form(["*h2us-"], "ḫuišw=a(e)-@leben", "to live", fz, by_id) is None
    # a form with a lost glyph is left to the root resolver
    assert hm.resolve_form(["*h1or\x02\x02\x03-ei"], "ark=@aufteilen", "to divide", fz, by_id) is None


# ---------------------------------------------------------------- EDHIL entries and the route

def _edhil(tmp_path):
    d = tmp_path / fm.KLOEKHORST
    d.mkdir(parents=True)
    (d / f"{fm.KH_FIRST_FILE}.txt").write_text(
        "A \n \n197\n"
        "\x04rr-i / arr- (IIa2 > IIa1, Ic1) ‘to wash’: 1sg.pres.act. x.\n  PIE *h1órh1-ei, *h1rh1-énti \n \n"
        "parši-a(ri), parš-a(ri) (IIIc > IIIg) ‘to break’: 3sg.pres.midd. x.\n  PIE *bhrs- ? \n \n"
        "arra- (c.) ‘arse’: nom.sg. x.\n \n"
        "aršan\x02-zi / aršan- ‘to be envious’: x.\n  PIE *h1/3rs-ne-h1-ti / *h1/3rs-n-h1-enti. \n \n"
        "kiš-zi ‘to comb’: see kišš-  \n", "utf-8")
    return fm.kloekhorst_entries(tmp_path)


def test_kloekhorst_entries_keep_doubt_and_page(tmp_path):
    ents = _edhil(tmp_path)
    by = {e["head"]: e for e in ents}
    assert set(by) == {"\x04rr-i / arr-", "parši-a(ri) / parš-a(ri)", "arra-", "aršan\x02-zi / aršan-"}
    assert by["\x04rr-i / arr-"]["printed"] == "197" and not by["\x04rr-i / arr-"]["doubtful"]
    assert by["parši-a(ri) / parš-a(ri)"]["stems"] == ["parši", "parš"] and by["parši-a(ri) / parš-a(ri)"]["doubtful"]
    assert by["arra-"]["pie"] == []
    assert by["aršan\x02-zi / aršan-"]["pie"] == ["*h1/3rs-ne-h1-ti", "*h1/3rs-n-h1-enti"]


def test_kloekhorst_route_gloss_chooses_the_headword_and_doubt_stays_unmapped(tmp_path):
    ents = _edhil(tmp_path)
    gmap = {e["id"]: e["id"] for e in LEX}
    st = {}
    out = hm.kloekhorst_hittite(["arr=a-@waschen", "parš=@zerbrechen", "arr=a-@Freund"], LEX, tmp_path,
                                gmap=gmap, entries=ents, stats=st)
    # arr=a- 'waschen' meets ārr- 'to wash' and arra- 'arse': the gloss chooses
    assert set(out) == {"arr=a-@waschen"}
    r = out["arr=a-@waschen"]
    assert r.ids == {"pie-root-h1erH-wash"} and r.how == "kloekhorst-root" and "headword-gloss" in r.sources
    assert "edhil-page:197" in r.path
    assert st["doubtful"] == 1                      # parš- 'to break': Kloekhorst's '?' is kept
    assert st["headword_no_gloss_agreement"] == 1   # arr=a- 'Freund': neither entry fits


# ---------------------------------------------------------------- the doubtful tier (retrieval only)

def _entry(pie_alts, doubtful=True, gloss="to wash"):
    return {"head": "x", "stems": ["arr"], "pie": [f for a in pie_alts for f in a], "pie_alts": pie_alts,
            "page": "p0205", "printed": "197", "gloss": gloss, "doubtful": doubtful, "foreign": False, "cls": ""}


def test_doubtful_tier_resolves_only_doubtful_lines_and_needs_agreeing_alternatives():
    fz, roots, by_id = fm.FuzzyPie(LEX), hm.RootIndex(LEX), {e["id"]: e for e in LEX}
    gmap = {e["id"]: e["id"] for e in LEX}
    lem = "arr=a-@waschen"
    # the main tier keeps Kloekhorst's doubt; the doubtful tier resolves the same line
    assert hm.resolve_entry(_entry([["*h1órh1-ei"]]), lem, fz, roots, by_id, gmap) == "doubtful"
    ids, form, how = hm.resolve_entry(_entry([["*h1órh1-ei"]]), lem, fz, roots, by_id, gmap, doubtful=True)
    assert ids == {"pie-root-h1erH-wash"} and how == "kloekhorst-doubtful"
    assert hm.resolve_entry(_entry([["*h1órh1-ei"]], doubtful=False), lem, fz, roots, by_id, gmap,
                            doubtful=True) == "not_doubtful"
    # two alternatives ('or'): both must resolve, to the same root group
    two = _entry([["*h1órh1-ei"], ["*h2ón-ei"]], gloss="to wash; to draw (water)")
    assert hm.resolve_entry(two, "arr=a-@waschen schöpfen", fz, roots, by_id, gmap, doubtful=True) == \
        "alternatives_disagree"
    assert hm.resolve_entry(_entry([["*h1órh1-ei"], ["*bhrs-"]]), lem, fz, roots, by_id, gmap,
                            doubtful=True) == "pie_unresolved"


def test_kloekhorst_entries_keep_or_alternatives(tmp_path):
    d = tmp_path / fm.KLOEKHORST
    d.mkdir(parents=True)
    (d / f"{fm.KH_FIRST_FILE}.txt").write_text(
        " \nm\x02ma-i / m\x02mi- (IIa5) ‘to speak’: x.\n  PIE *h1mé-h1m-oi-ei / *h1mé-h1m-i-enti ?? or "
        "*mé-moi-ei / *mé-mi-enti ?? \n", "utf-8")
    e = fm.kloekhorst_entries(tmp_path)[0]
    assert e["doubtful"] and e["pie_alts"] == [["*h1mé-h1m-oi-ei", "*h1mé-h1m-i-enti"], ["*mé-moi-ei", "*mé-mi-enti"]]


def test_lost_dorsal_before_h_is_an_aspirate():
    # kīnu- *ǵʰih₁-neu- (a lost glyph + h) does not meet LIV *ǵeyH- 'burst open'
    asp = hm.root_skeletons("*\x02\x03\x03hih1-neu-")[0]
    assert asp == ("K*h", "y", "H1")
    assert not hm.skeletons_agree(asp, hm.lex_root_skeletons("ǵeyH-")[0])
    assert hm.skeletons_agree(asp, hm.lex_root_skeletons("ǵʰeyH-")[0])


def test_doubtful_table_is_retrieval_only(tmp_path):
    import json
    from pie import mapping as mp
    d = tmp_path / mp.MAPPING
    d.mkdir(parents=True)
    row = {"corpus": "hit", "lang": "hit", "lemma": "a@b", "word": "a", "lex_id": ["pie-lex-x"], "path": [],
           "how": "chain", "confidence": "high", "sources": []}
    (d / "hit.jsonl").write_text(json.dumps(row) + "\n", "utf-8")
    (d / "hit-doubtful.jsonl").write_text(json.dumps({**row, "lemma": "c@d", "lex_id": ["pie-lex-y"],
                                                      "how": "kloekhorst-doubtful"}) + "\n", "utf-8")
    assert mp.table_corpora(tmp_path) == ["hit"]                      # the secure check and audits skip it
    assert hm.read_union_table(tmp_path, doubtful=False) == {"a@b": ("pie-lex-x",)}
    assert hm.read_union_table(tmp_path) == {"a@b": ("pie-lex-x",), "c@d": ("pie-lex-y",)}


def test_union_retains_doubtful_qualification_without_changing_ids():
    import json
    qualifications = {}
    union = hm.read_union_table(qualifications=qualifications)
    assert union == hm.read_union_table()
    rows = [json.loads(line) for line in (hm.ROOT / hm.DOUBTFUL_TABLE).read_text().splitlines() if line.strip()]
    assert len(qualifications) == len(rows) == 8
    for row in rows:
        q = qualifications[row["lemma"]]
        assert q["confidence"] == row["confidence"] == "low"
        assert q["source"] == "Kloekhorst EDHIL"
        assert "edhil-page:" + q["page"] in row["path"]
        assert q["reason"] == row["note"]
        assert union[row["lemma"]] == tuple(sorted(row["lex_id"]))
    hm.read_union_table(doubtful=False, qualifications=qualifications)
    assert qualifications == {}


def _reviewed_file(tmp_path, **changes):
    import json
    row = dict(lemma="arr=a-@waschen", lex_id=["pie-root-h1erH-wash"], head="arr-",
               page="197-198", pie="*h1erH-", note="EDHIL pp. 197-198: reviewed doubtful fixture.")
    row.update(changes)
    p = tmp_path / hm.REVIEWED_DOUBTFUL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps([row]), "utf-8")
    return row


def test_reviewed_doubtful_keeps_evidence_and_obeys_main_and_override_precedence(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from pie import mapping as mp
    row = _reviewed_file(tmp_path)
    lem = row["lemma"]
    toks = [SimpleNamespace(lemma=lem, content=True)]
    monkeypatch.setattr(hm, "kloekhorst_hittite", lambda *args, **kwargs: {})
    out = hm.doubtful_table(toks, LEX, {}, {}, tmp_path)
    assert out[lem].ids == {"pie-root-h1erH-wash"}
    assert out[lem].confidence == "low" and out[lem].how == "kloekhorst-doubtful"
    assert "edhil-page:197-198" in out[lem].path
    assert hm.doubtful_note(hm.table_rows(out)[0]) == row["note"]
    assert not hm.doubtful_table(toks, LEX, {}, {lem: object()}, tmp_path)
    assert not hm.doubtful_table([SimpleNamespace(lemma=lem, content=False)], LEX, {}, {}, tmp_path)
    monkeypatch.setattr(mp, "decisions_for", lambda *args, **kwargs: [object()])
    assert not hm.doubtful_table(toks, LEX, {}, {}, tmp_path)


def test_reviewed_doubtful_rejects_stale_ids_unknown_fields_and_missing_pages(tmp_path):
    import pytest
    for changes in ({"lex_id": ["nonexistent"]}, {"lex_id": []}, {"typo": "x"},
                    {"page": ""}, {"page": "unknown"}):
        _reviewed_file(tmp_path, **changes)
        with pytest.raises(ValueError):
            hm.reviewed_doubtful(LEX, tmp_path)


def test_reviewed_doubtful_rejects_duplicates(tmp_path):
    import json
    import pytest
    row = _reviewed_file(tmp_path)
    (tmp_path / hm.REVIEWED_DOUBTFUL).write_text(json.dumps([row, row]), "utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        hm.reviewed_doubtful(LEX, tmp_path)


def test_reviewed_hittite_existing_ids_and_tier_separation():
    import json
    from pie import mapping as mp
    lex = [json.loads(x) for x in (fm.ROOT / "data/lexicon/lexicon.jsonl").read_text().splitlines()]
    reviewed = hm.reviewed_doubtful(lex)
    ov = mp.load_overrides()
    assert len(reviewed) == 7
    for lem, rec in reviewed.items():
        assert not mp.decisions_for("hit", lem, ov)
        assert rec.confidence == "low"
    main = hm.read_union_table(doubtful=False)
    union = hm.read_union_table()
    assert main["warp=@baden"] == ("pie-root-werp-turn_back_and-2",)
    assert main["šak(k)-, šek(k)-@wissen"] == ("pie-root-sekH-separate",)
    for lem, rec in reviewed.items():
        assert lem not in main and set(union[lem]) == rec.ids
    for lem in ("parš=@zerbrechen", "mem=a-@sprechen", "wēḫ-/waḫḫ-@sich drehen"):
        assert lem not in union


def test_edhil_ineligible_headers_close_previous_entry(tmp_path):
    """Invented layout: a rejected headword still owns its following PIE line."""
    d = tmp_path / fm.KLOEKHORST
    d.mkdir(parents=True)
    for header in ("=zza (encl.pron. 3sg.) ‘for it’: x.",
                   "MUNUSzalla- (c.) a fictional functionary: x.",
                   "=za(r)= (particle of fictional use)",
                   "zappa-: see zappi-", "za-za-za-za- (n.) ‘fixture’: x."):
        (d / f"{fm.KH_FIRST_FILE}.txt").write_text(
            "A\n\n197\nlamma- (n.) ‘fixture’: x.\n\n"
            "Discussion proposes *h1er- only.\n\n" + header +
            "\n  PIE *h2en- ?\n\nmalla- (n.) ‘fixture’: x.\n  PIE *mel-\n", "utf-8")
        ents = fm.kloekhorst_entries(tmp_path)
        assert ents[0]["pie"] == [], header
        assert ents[-1]["pie"] == ["*mel-"]


def test_edhil_page_continuations_and_control_glyphs_are_not_headers(tmp_path):
    d = tmp_path / fm.KLOEKHORST
    d.mkdir(parents=True)
    (d / f"{fm.KH_FIRST_FILE}.txt").write_bytes(
        "A\n\n197\nlamma- (n.) ‘fixture’: x.\n".encode())
    (d / "p0171.txt").write_bytes(
        "A\n\n198\nla-am-ma (MH/MS), more attestations.\n"
        " IE cognates: fixture \r\x1c\x0b ‘invented’.\n  PIE *h1er-\n".encode())
    ents = fm.kloekhorst_entries(tmp_path)
    assert len(ents) == 1
    assert ents[0]["pie"] == ["*h1er-"]


def test_edhil_discussion_and_labelled_pie_do_not_supply_forms(tmp_path):
    d = tmp_path / fm.KLOEKHORST
    d.mkdir(parents=True)
    (d / f"{fm.KH_FIRST_FILE}.txt").write_text(
        "A\n\n197\nlamma- (n.) ‘fixture’: x.\n"
        "  PIE adj. *h1er-\n\nDiscussion proposes *h2en-.\n\n"
        "=zza (encl.pron.) ‘fixture’: x.\n  PIE *mel-\n", "utf-8")
    assert fm.kloekhorst_entries(tmp_path)[0]["pie"] == []
