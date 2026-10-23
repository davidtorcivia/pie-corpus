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
