"""Secure check v2 (pie/tier2_secure.py) on small fixtures: no tables or dumps from disk."""

from pie.tier2_secure import SecureChecker, plan_compound_ids


def rec(ids, word, code="grc", corpus="grp", derived=False):
    return (frozenset(ids), (f"table:{corpus}", f"{code}:{word}"), f"table:{corpus}", derived)


ENTRIES = {
    "pie-root-spekj-see": {"id": "pie-root-spekj-see", "kind": "root", "form": "speḱ-"},
    # σκώψ written as a sure reflex here, to test that only whole-word equality counts
    "pie-lex-spekjs": {"id": "pie-lex-spekjs", "form": "spéḱs", "root_id": "pie-root-spekj-see",
                       "reflexes": {"Ancient Greek": [{"form": "σκώψ"}]}},
    "pie-root-h2ews-become_light": {"id": "pie-root-h2ews-become_light", "kind": "root", "form": "h₂ews-"},
    "pie-lex-h2ewsoxs": {"id": "pie-lex-h2ewsoxs", "form": "h₂éwsōs", "root_id": "pie-root-h2ews-become_light",
                         "reflexes": {"Proto-Hellenic": [{"form": "*auhṓs"}]}},
    "pie-root-dhgwhey-decline": {"id": "pie-root-dhgwhey-decline", "kind": "root", "form": "dʰgʷʰey-"},
    "pie-lex-ndhgwhitos": {"id": "pie-lex-ndhgwhitos", "form": "ń̥dʰgʷʰitos", "root_id": "pie-root-dhgwhey-decline"},
    "pie-lex-dhgwhitos": {"id": "pie-lex-dhgwhitos", "form": "dʰgʷʰitós", "root_id": "pie-root-dhgwhey-decline"},
    "pie-lex-h1esh2r": {"id": "pie-lex-h1esh2r", "form": "h₁ésh₂r̥",
                        "reflexes": {"Hittite": [{"form": "𒂊𒌍𒄯", "roman": "e-eš-ḫar"}]}},
    "pie-root-gwhen-strike": {"id": "pie-root-gwhen-strike", "kind": "root", "form": "gʷʰen-"},
    "pie-lex-gwhenti": {"id": "pie-lex-gwhenti", "form": "gʷʰénti", "root_id": "pie-root-gwhen-strike"},
    "pie-lex-gwhonos": {"id": "pie-lex-gwhonos", "form": "gʷʰónos", "root_id": "pie-root-gwhen-strike"},
    "pie-root-kjlew-hear": {"id": "pie-root-kjlew-hear", "kind": "root", "form": "ḱlew-"},
    "pie-lex-kjlewos": {"id": "pie-lex-kjlewos", "form": "ḱléwos", "root_id": "pie-root-kjlew-hear",
                        "reflexes": {"Old Irish": [{"form": "clú"}]}},
    "pie-lex-h1ekjwos": {"id": "pie-lex-h1ekjwos", "form": "h₁éḱwos"},
}
TABLES = {
    "grc": {"σκοποσ": [rec({"pie-root-spekj-see"}, "σκοπός", derived=False)],
            "ηωσ": [rec({"pie-lex-h2ewsoxs"}, "ἠώς")],
            "αφθιτοσ": [rec({"pie-lex-ndhgwhitos"}, "ἄφθιτος")],
            "κλεοσ": [rec({"pie-lex-kjlewos"}, "κλέος")],
            "ιπποσ": [rec({"pie-lex-h1ekjwos"}, "ἵππος")],
            "ευιπποσ": [rec({"pie-lex-h1ekjwos"}, "εὔιππος", derived=True)]},
    "sa": {"uṣas": [rec({"pie-lex-h2ewsoxs"}, "uṣás-", "sa", "av")],
           "akṣita": [rec({"pie-lex-ndhgwhitos"}, "ákṣita-", "sa", "av")],
           "spaś": [rec({"pie-lex-spekjs"}, "spáś-", "sa", "av")],
           "han": [rec({"pie-lex-gwhenti"}, "√han-", "sa", "av")],
           "śravas": [rec({"pie-lex-kjlewos"}, "śrávas-", "sa", "av")],
           "aśva": [rec({"pie-lex-h1ekjwos"}, "áśva-", "sa", "av")]},
    "sga": {"gonaid": [rec({"pie-lex-gwhenti"}, "gonaid", "sga", "dict")]},
    "hit": {},
}


def checker(tables=TABLES):
    return SecureChecker(ENTRIES, tables)


def ref(lang, lemmas, words=(), role="parallel"):
    return {"lang": lang, "locus": f"{lang} 1", "lemmas": list(lemmas), "words": list(words), "role": role}


def test_skopos_is_not_an_exact_reflex_of_spekjs():
    refs = [ref("Greek", ["σκοπός"], ["σκοπὸν"]), ref("Vedic", ["spáś-"], ["spáśaḥ"])]
    c = checker().check("pie-lex-spekjs", refs)
    assert c["exact_branches"] == ["II"]          # spáś- only
    assert c["root_branches"] == ["Gk"]           # σκοπός reaches the root *speḱ-, not the noun
    assert c["level"] == "root"
    # no table at all: σκοπός must not match the reflex σκώψ by its first letters
    assert checker({}).check("pie-lex-spekjs", [ref("Greek", ["σκοπός"], ["σκοπόν"])])["exact_branches"] == []


def test_eos_matches_h2ewsos():
    c = checker().check("pie-lex-h2ewsoxs", [ref("Greek", ["ἠώς"], ["Ἠὼς"]), ref("Vedic", ["uṣás-"], ["uṣā́ḥ"])])
    assert c["level"] == "exact" and c["exact_branches"] == ["Gk", "II"]
    assert c["evidence"]["Gk"]["via"] == "table:grp"


def test_aphthitos_matches_ndhgwhitos_not_its_base():
    refs = [ref("Greek", ["ἄφθιτος"], ["ἄφθιτον"]), ref("Vedic", ["ákṣita-"], ["ákṣitam"])]
    assert checker().check("pie-lex-ndhgwhitos", refs)["level"] == "exact"
    # the base *dʰgʷʰitós is a sibling formation of the same root: root level only
    assert checker().check("pie-lex-dhgwhitos", refs)["level"] == "root"


def test_hittite_by_reflex_list():
    refs = [ref("Hittite", ["ēšḫar"], ["ēšḫar=kan"]), ref("Latin", ["assyr"])]
    c = checker().check("pie-lex-h1esh2r", refs)
    assert "An" in c["exact_branches"]
    assert c["evidence"]["An"]["via"] == "reflex"


def test_old_irish_by_table_and_by_reflex():
    c = checker().check("pie-lex-gwhenti", [ref("Old Irish", ["gonaid"]), ref("Vedic", ["han-"], ["hán"])])
    assert c["exact_branches"] == ["Ce", "II"]
    # a sibling formation of the same root (gʷʰónos) gets root level from the same words
    assert checker().check("pie-lex-gwhonos", [ref("Old Irish", ["gonaid"]), ref("Vedic", ["han-"])])["level"] == "root"
    k = checker().check("pie-lex-kjlewos", [ref("Old Irish", ["clú"]), ref("Greek", ["κλέος"])])
    assert k["exact_branches"] == ["Ce", "Gk"]


def test_support_refs_do_not_count():
    refs = [ref("Greek", ["ἠώς"]), ref("Vedic", ["uṣás-"], role="support")]
    assert checker().check("pie-lex-h2ewsoxs", refs)["exact_branches"] == ["Gk"]


def test_compound_both_members_exact():
    cid = "compound:bahuvrihi:closed:prefix/h1su+pie-lex-kjlewos"
    refs = [ref("Vedic", ["suśrávas-"], ["suśrávasam"]), ref("Greek", ["εὐκλεής"], ["ἐϋκλεῖας"])]
    c = checker().check(cid, refs)
    assert c["level"] == "exact" and c["exact_branches"] == ["Gk", "II"]
    assert c["members"]["closed:prefix/h1su"]["exact_branches"] == ["Gk", "II"]
    assert c["members"]["pie-lex-kjlewos"]["exact_branches"] == ["Gk", "II"]


def test_compound_through_derived_table_entry_and_plan_ids():
    cid = "compound:bahuvrihi:closed:prefix/h1su+pie-lex-h1ekjwos"
    refs = [ref("Vedic", ["sváśva-"], ["sváśvā"]), ref("Greek", ["εὔιππος"], ["εὔιπποι"])]
    assert checker().check(cid, refs)["level"] == "exact"
    # standalone, the compound εὔιππος is only a derivative of ἵππος: root level, never exact
    c = checker().check("pie-lex-h1ekjwos", [ref("Greek", ["εὔιππος"])])
    assert c["exact_branches"] == [] and c["root_branches"] == ["Gk"]
    plan = {"clauses": [{"slots": [{"lex_id": "compound", "compound": {"first": "pie-lex-h1su",
                                    "second": "pie-lex-h1ekjwos", "type": "bahuvrihi"}}]}]}
    assert plan_compound_ids(plan) == [(cid, "closed:prefix/h1su", "pie-lex-h1ekjwos")]


def test_compound_without_first_member_is_none():
    cid = "compound:bahuvrihi:closed:prefix/h1su+pie-lex-kjlewos"
    c = checker().check(cid, [ref("Vedic", ["śrávas-"]), ref("Greek", ["κλέος"])])
    assert c["level"] == "none" and c["members"]["pie-lex-kjlewos"]["exact_branches"] == []


# ---------------------------------------------------------------- formation (tier2-review-r4 §3)

from pie.tier2_secure import agent_type_cited, agent_type_pie, merge_tables, table_from_rows  # noqa: E402

FORM = {
    "pie-root-sewH-bear": {"id": "pie-root-sewH-bear", "kind": "root", "form": "sewH-"},
    "pie-lex-suHnus": {"id": "pie-lex-suHnus", "form": "suHnús", "root_id": "pie-root-sewH-bear",
                       "reflexes": {"Proto-Indo-Iranian": [{"form": "*suHnúš"}]}},
    "pie-lex-megjh2s": {"id": "pie-lex-megjh2s", "form": "méǵh₂s", "pos": "adj",
                        "reflexes": {"Ancient Greek": [{"form": "μέγᾰς"}],
                                     "Proto-Indo-Iranian": [{"form": "*maȷ́ʰā́"}]}},
    "pie-lex-soh2wl": {"id": "pie-lex-soh2wl", "form": "sóh₂wl̥", "reflexes": {"Latin": [{"form": "sōl"}]}},
    "pie-root-deh3-give": {"id": "pie-root-deh3-give", "kind": "root", "form": "deh₃-"},
    "pie-lex-deh3toxr": {"id": "pie-lex-deh3toxr", "form": "déh₃tōr", "root_id": "pie-root-deh3-give",
                         "reflexes": {"Ancient Greek": [{"form": "δώτωρ"}],
                                      "Proto-Indo-Iranian": [{"form": "*dáHtā"}]}},
    "pie-root-gjenh1-produce": {"id": "pie-root-gjenh1-produce", "kind": "root", "form": "ǵenh₁-"},
    "pie-lex-gjenh1toxr": {"id": "pie-lex-gjenh1toxr", "form": "ǵénh₁tōr", "root_id": "pie-root-gjenh1-produce",
                           "reflexes": {"Latin": [{"form": "genitor"}]}},
    "pie-lex-gjenh1texr": {"id": "pie-lex-gjenh1texr", "form": "ǵenh₁tḗr", "root_id": "pie-root-gjenh1-produce"},
}


def row(corpus, lang, lemma, ids, word=None, path=None):
    return corpus, {"corpus": corpus, "lang": lang, "lemma": lemma, "word": word or lemma, "lex_id": list(ids),
                    "path": path or [f"{lang}:{lemma}", "r2-tier:kaikki"], "how": "kaikki"}


# errata as pie.formula_search_multi.load_overrides()["lemma"] gives them: {corpus: {lemma: (ids, row)}}
OVERRIDES = {
    "grp": {"υἱός": (frozenset({"pie-root-sewH-bear"}), {"note": "Beekes EDG p. 1528 s.v. υἱός: *suH-iu-"})},
    "av": {"sūrya": (frozenset({"pie-lex-soh2wl"}), {"note": "EWAia II 742", "formation": "derivative"}),
           "mahat": (frozenset({"pie-lex-megjh2s"}), {"note": "EWAia II 337f.", "formation": "derivative"}),
           "svar": (frozenset({"pie-lex-soh2wl"}), {"note": "EWAia II 794"})},
}
ROWS = [row("grp", "grc", "υἱός", {"pie-lex-suHnus"}), row("grp", "grc", "μέγας", {"pie-lex-megjh2s"}),
        row("av", "sa", "sūnu", {"pie-lex-suHnus"}, "sūnú-"), row("av", "sa", "sūrya", {"pie-lex-soh2wl"}, "sū́rya-"),
        row("av", "sa", "svar", {"pie-lex-soh2wl", "pie-root-swer-resound"}, "√svar-"),
        row("av", "sa", "mahat", {"pie-lex-megjh2s"}),
        row("av", "sa", "dātṛ", {"pie-lex-deh3toxr"}), row("av", "sa", "janitṛ", {"pie-lex-gjenh1toxr"}),
        row("ae", "ae", "dātar", {"pie-lex-deh3toxr"}, "𐬛𐬁𐬙𐬀𐬭"),
        row("grp", "grc", "δώτωρ", {"pie-lex-deh3toxr"})]


def form_checker(overrides=OVERRIDES):
    tables, corrected = table_from_rows(ROWS, overrides)
    # the round-2 kaikki links still join mahát and sū́rya- to the base lexemes (Wiktionary "from *méǵh₂s")
    kaikki = {"sa": {"mahat": [rec({"pie-lex-megjh2s"}, "mahát", "sa", "kaikki-sa")],
                     "sūrya": [rec({"pie-lex-soh2wl"}, "sū́rya", "sa", "kaikki-sa")]}}
    return SecureChecker(FORM, {c: merge_tables(c, tables, (kaikki,), corrected) for c in ("sa", "grc", "ae")})


def test_huios_is_root_level_for_suHnus():
    # υἱός < *suH-iu- (Beekes): the table reached *suHnús through the alternative-form page *suHyús
    refs = [ref("Greek", ["υἱός"], ["υἱός"]), ref("Vedic", ["sūnú-"], ["sūnúḥ"])]
    assert form_checker({}).check("pie-lex-suHnus", refs)["exact_branches"] == ["Gk", "II"]   # the old behaviour
    c = form_checker().check("pie-lex-suHnus", refs)
    assert c["exact_branches"] == ["II"] and c["root_branches"] == ["Gk"] and c["level"] == "root"
    assert any(p.startswith("erratum:") for p in c["evidence"]["Gk"]["path"])
    # the inflected word is not re-admitted as a 'table form' of *suHnús either
    assert form_checker().check("pie-lex-suHnus", [ref("Greek", [], ["υἱὸν"])])["exact_branches"] == []


def test_surya_is_a_derivative_svar_the_heteroclite():
    c = form_checker().check("pie-lex-soh2wl", [ref("Vedic", ["sū́rya-"], ["sū́ryaḥ"]), ref("Latin", ["sōl"])])
    assert c["exact_branches"] == ["It"] and c["root_branches"] == ["II"] and c["level"] == "root"
    c = form_checker().check("pie-lex-soh2wl", [ref("Vedic", ["svàr-"], ["svàr"]), ref("Latin", ["sōl"])])
    assert c["exact_branches"] == ["II", "It"]


def test_mahat_is_the_nt_stem_megas_exact():
    refs = [ref("Vedic", ["mahā́nt-"], ["mahát"]), ref("Greek", ["μέγας"], ["μέγαν"])]
    c = form_checker().check("pie-lex-megjh2s", refs)
    assert c["exact_branches"] == ["Gk"] and c["root_branches"] == ["II"] and c["level"] == "root"
    # the kaikki link for the same key is dropped once an erratum corrected the corpus row
    assert c["evidence"]["II"]["via"] == "table:av"


def test_agent_noun_types():
    assert agent_type_pie("déh₃tōr") == agent_type_pie("ǵénh₁tōr") == "root"
    assert agent_type_pie("ǵenh₁tḗr") == agent_type_pie("ph₂tḗr") == "suffix"
    assert agent_type_pie("méh₂tēr") is None and agent_type_pie("h₂nḗr") is None
    assert [agent_type_cited("sa", w) for w in ("dātā́", "dātár-", "janitā́", "janitṛ́")] == ["suffix"] * 4
    assert [agent_type_cited("sa", w) for w in ("dā́tā", "jánitā", "dā́tāraḥ")] == ["root"] * 3
    assert agent_type_cited("grc", "δωτῆρες") == agent_type_cited("grc", "δωτήρ") == "suffix"
    assert agent_type_cited("grc", "δῶτορ") == agent_type_cited("la", "genitor") == "root"
    # no accent, no grade: no evidence (DCS dātṛ, Av. dātārō, Ved. śrávas-)
    assert {agent_type_cited("sa", "dātṛ"), agent_type_cited("ae", "dātārō"), agent_type_cited("sa", "śrávas-")} == {None}


def test_suffix_accented_data_is_not_exact_for_root_accented_deh3tor():
    ch = form_checker()
    # dātā́ (vásūnām) is the suffix-accented type: root level, through the table and the PIIr. *dáHtā bridge
    m = ch.match("pie-lex-deh3toxr", "sa", "Vedic", "dātā́", False)
    assert m["level"] == "root" and any(p.startswith("formation:agent-noun") for p in m["path"])
    assert ch.match("pie-lex-deh3toxr", "sa", "Vedic", "dātár-", True)["level"] == "root"
    assert ch.match("pie-lex-deh3toxr", "sa", "Vedic", "dā́tā", False)["level"] == "exact"
    assert ch.match("pie-lex-deh3toxr", "sa", "Vedic", "dātṛ", True)["level"] == "exact"    # unaccented
    assert ch.match("pie-lex-deh3toxr", "grc", "Greek", "δώτωρ", True)["level"] == "exact"
    m = ch.match("pie-lex-deh3toxr", "grc", "Greek", "δωτῆρες", False)
    assert m is None or m["level"] != "exact"
    # poetics-gifts-007: Gk δωτῆρες, Av. dātārō, Ved. dātā́. Avestan shows no accent; its branch's Vedic word
    # shows the suffix-accented type, so Indo-Iranian is root level
    refs = [ref("Greek", ["δωτήρ"], ["δωτῆρες"]), ref("Avestan", ["dātar-"], ["dātārō"]),
            ref("Vedic", ["dātár-"], ["dātā́"])]
    c = ch.check("pie-lex-deh3toxr", refs)
    assert c["exact_branches"] == [] and c["root_branches"] == ["II"]
    # Avestan alone is no evidence against the lexeme
    assert ch.check("pie-lex-deh3toxr", [ref("Avestan", ["dātar-"], ["dātārō"])])["exact_branches"] == ["II"]
    # poetics-gifts-008: δῶτορ is exact, dātā́ root level
    c = ch.check("pie-lex-deh3toxr", [ref("Greek", ["δώτωρ"], ["δῶτορ"]), ref("Vedic", ["dātár-"], ["dātā́"])])
    assert c["exact_branches"] == ["Gk"] and c["root_branches"] == ["II"] and c["level"] == "root"


def test_janitar_is_not_exact_for_gjenh1tor():
    # sky-father-011: Ved. janitā́ is the suffix-accented *ǵenh₁tér-; Lat. genitor shows the o-grade *-tor-
    refs = [ref("Vedic", ["janitár-"], ["janitā́"]), ref("Latin", ["genitor"], ["genitor"])]
    c = form_checker().check("pie-lex-gjenh1toxr", refs)
    assert c["exact_branches"] == ["It"] and c["root_branches"] == ["II"] and c["level"] == "root"
    # the same words are root level for the suffix-accented sibling, which no table maps
    assert form_checker().check("pie-lex-gjenh1texr", refs)["exact_branches"] == []
