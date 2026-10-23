"""NIL merge (pie/nil.py): stem normalization, citation forms, gender from the daughters,
root linking and the duplicate check (docs/audits/nil-merge-review.md P1-P10)."""

import pytest

from pie.nil import _match, apply, branches, citation, clean_gloss, ev_gender, expected, link_root, stem


# --- stem(): NIL notation → lexicon notation (P5, P7) ----------------------------------------

@pytest.mark.parametrize("printed,want", [
    ("*h₂áu̯g-", "h₂éwg"),                    # a-colouring next to h₂ → h₂e, glides → w/y
    ("*h₃okʷ-ah₂-", "h₃okʷeh₂"),              # -ah₂- → eh₂; root-initial h₃o is left alone
    ("?*ĝnoh₃-tér-", "ǵneh₃tér"),             # o-colouring next to h₃ → eh₃ (P5)
    ("*dóh₃-tor-", "déh₃tor"),
    ("*kor-i̯o-h₃ōn-", "koryoh₃ōn"),          # but not across a morpheme boundary
    ("**h₁éd-u̯-on- > *h₁éd-u̯on-", "h₁édwon"),  # the later form
    ("*k̂l̥-tó-", "ḱl̥tó"),                     # NIL k̂ → ḱ
])
def test_stem_normalization(printed, want):
    assert stem(printed) == want


@pytest.mark.parametrize("printed", [
    "*h₂énh₁-Ro-",          # R: NIL's r/l cover symbol (P7)
    "*oi̯bʰ-r̥ó-",            # syllabic r̥ before a vowel (P7)
    "*-bʰag-ó-",            # suffix-only / compound member
    "*gʷih₃-u̯ó/áh₂-",       # alternants
    "*(dʰ)ĝʰ-m-ah₂-",       # optional part
    None,
])
def test_stem_rejects_notation(printed):
    assert stem(printed) is None


# --- citation(): one nominative per stem class ----------------------------------------------

@pytest.mark.parametrize("st,gender,want", [
    ("bʰágo", "m", ("bʰágos", "noun", "m")),             # thematic masculine
    ("ḱléwtro", "n", ("ḱléwtrom", "noun", "n")),          # thematic neuter
    ("wersó", None, ("wersós", "adj", None)),             # genderless o-stem: adjective
    ("bʰagéh₂", "f", ("bʰagéh₂", "noun", "f")),           # eh₂-stem
    ("h₂weksíH", "f", ("h₂weksíh₂", "noun", "f")),        # devī type: iH → ih₂, no -s (P8)
    ("neptíH", "f", ("neptíh₂", "noun", "f")),
    ("sweḱrúH", "f", ("sweḱrúh₂", "noun", "f")),
    ("dʰébʰti", "f", ("dʰébʰtis", "noun", "f")),          # i-stem
    ("dʰébʰtu", "m", ("dʰébʰtus", "noun", "m")),          # u-stem
    ("ǵénh₁es", "n", ("ǵénh₁os", "noun", "n")),           # neuter s-stem
    ("bʰésmen", "n", ("bʰésmn̥", "noun", "n")),            # men-neuter
    ("ǵneh₃tér", None, ("ǵneh₃tḗr", "noun", "m")),        # -tér- agent
    ("dʰéh₁tor", "m", ("dʰéh₁tōr", "noun", "m")),         # -tor agent
    ("swóp", "f", ("swóps", "noun", "f")),                # consonant-final root noun
])
def test_citation_by_stem_class(st, gender, want):
    assert citation(st, gender) == want


@pytest.mark.parametrize("st,gender", [
    ("séǵʰyes", None),      # *-i̯es- comparative: no neuter s-stem (P3)
    ("h₁wésyes", "n"),
    ("pedyos", None),       # *-i̯os-
    ("gʷénh₂", "f"),        # laryngeal-final root noun: no *gʷénh₂s (P8)
    ("bʰagti", "f"),        # no accent: the slice gate needs one, don't guess
    ("dʰébʰti", None),      # genderless i-stem
])
def test_citation_none(st, gender):
    assert citation(st, gender) is None


def test_comparative_matches_an_existing_yos_entry():
    assert ("pedyōs", None) in expected({"stem": "pedyes", "gender": None, "evidence": []})


# --- the gender rule: NIL prints no gender, the daughters do (P2) ---------------------------

def test_gender_from_evidence_makes_nouns():
    assert citation("gʷowsth₂ó", None, ["ved. goṣṭhá- m./n.? 'Kuhstall, Kuhweide'"]) == \
        ("gʷowsth₂ós", "noun", "m")
    # Hittite common gender counts as masculine; the majority wins
    assert citation("h₂worsó", None, ["heth. warsa- c. 'Nebel? Regenguß?'", "ved. varṣá- m. 'Regen'"]) == \
        ("h₂worsós", "noun", "m")
    assert citation("dʰh₁só", None, ["hluv. tasan(-za) NASg. n. 'Votivstele'", "lyk. NASg. θθē n. 'Altar'",
                                    "?gr. θεός m. und f. o 'Gottheit'"])[1:] == ("noun", "n")
    # a Latin neuter in -um, even without a gender mark
    assert citation("bʰérmento", None, ["[lat. fermentum 'Gärungsstoff, Sauerteig'"]) == \
        ("bʰérmentom", "noun", "n")


def test_gender_from_evidence_keeps_adjectives():
    assert citation("bʰegnó", None, ["ved. bhagna- 'gebrochen' (Br)"]) == ("bʰegnós", "adj", None)
    # a gender after 'Subst.' is the substantivized adjective's, not the formation's
    assert ev_gender(["ved. mádhya- 'mittlerer, in der Mitte befindlich', Subst. n. 'Mitte'",
                      "lat. medius, -a, -um 'mittlerer'"]) == "adj"
    assert ev_gender(["ved. jīvá- 'lebendig, lebend' Subst. m., n. 'lebendes Wesen'"]) == "adj"


def test_gender_from_evidence_does_not_guess():
    # a daughter cited as a substantive: noun of unknown gender, no lexeme
    assert citation("medró", None, ["ved. madrá- Pl. Name eines Volkes; Subst. ~ 'Freude'"]) is None
    # a noun (capitalized German gloss) without a gender
    assert ev_gender(["ved. bhūmá- 'Erde'"]) == "noun"
    assert citation("bʰuh₂mó", None, ["ved. bhūmá- 'Erde'"]) is None
    # as many nouns as adjectives
    assert ev_gender(["lit. ãkas m. 'Wuhne'", "ahd. aga- 'öffentlich'"]) == "mixed"
    assert citation("h₃okʷó", None, ["lit. ãkas m. 'Wuhne'", "ahd. aga- 'öffentlich'"]) is None
    # remodelled daughters ([) only count when nothing else is cited
    assert ev_gender(["gr. -βήτωρ 'Besteiger'", "[lat. stator m. 'Amtsdiener'"]) == "noun"


# --- glosses and attestation (P9, P10) ------------------------------------------------------

@pytest.mark.parametrize("raw,want", [
    ("sinew (?), diaphragm (?)", None),
    ("beech (oak in Greek)", "beech"),
    ("human being, man (earthling)", "human being, man"),
    ("giver; to give", "giver"),
    ("to watch, heed", None),
    ("deceiving (infinitive)", "deceiving"),
    ("(period of) day(s), in compounds", "day"),
    (None, None),
])
def test_clean_gloss(raw, want):
    assert clean_gloss(raw) == want


def test_branches_leave_out_remodelled_daughters():
    assert branches(["ved. bhága- m. 'Zuteiler'", "jav. baγa- m. 'Gott'", "aksl. usw. bogъ m. 'Gott'"]) == \
        {"Indo-Iranian", "Balto-Slavic"}
    assert branches(["[gr. λεῖμμα n. (-t-) 'Rest'"]) == set()
    assert branches(["? [arm. ǰer 'Wärme'", "?ved. -da- 'gebend'"]) == {"Indo-Iranian"}


# --- matching an existing lexeme (P6) -------------------------------------------------------

def _w(i, form, meaning=(), root="r1", **kw):
    return {"id": i, "kind": "derivative", "form": form, "meaning": list(meaning), "root_id": root, **kw}


def _kids(*ws):
    from pie.nil import _key
    out = {}
    for w in ws:
        out.setdefault(_key(w["form"]), []).append(w)
    return out


def test_match_keeps_length_and_stem_class():
    # *h₃ōkʷ-ah₂- is not h₃okʷéh₂; *u̯ēd-r-o- is not wedrom
    assert _match({"stem": "h₃ōkʷeh₂", "gender": "f", "evidence": []}, _kids(_w("a", "h₃okʷéh₂"))) is None
    assert _match({"stem": "wēdro", "gender": "n", "evidence": []}, _kids(_w("a", "wedrom"))) is None
    # an o-stem adjective is not the neuter s-stem of the same letters, but the adjective is
    s_stem = _w("s", "bʰéydʰos", gender="n")
    adj = _w("o", "bʰeydʰós", pos="adj")
    fm = {"stem": "bʰeydʰó", "gender": None, "evidence": ["lat. fīdus, -a, -um 'vertrauenswürdig'"]}
    assert _match(fm, _kids(s_stem, adj)) is adj
    assert _match(fm, _kids(s_stem)) is None
    # a root noun matches only "" or "-s", not any ending
    assert _match({"stem": "bʰíd", "gender": "f", "evidence": []}, _kids(_w("a", "bʰídis"))) is None
    # the lexicon's bare stems and genderless u-stems still match
    assert _match({"stem": "yewgtér", "gender": "m", "evidence": []}, _kids(_w("a", "yewgtér-")))["id"] == "a"
    assert _match({"stem": "pedtu", "gender": None, "evidence": []}, _kids(_w("a", "pedtus")))["id"] == "a"


# --- root linking (P1) ----------------------------------------------------------------------

def _root(i, form, meaning, page=None, variants=()):
    r = {"id": i, "kind": "root", "form": form, "variants": list(variants), "meaning": [meaning]}
    if page:
        r["liv"] = [{"page": {"djvu": page + 4, "printed": str(page)}, "meaning_en": meaning}]
    return r


def _index(roots):
    from pie.liv import _depal, _plain
    from pie.validate import key
    bp, bd, bg = {}, {}, {}
    for r in roots:
        for f in [r["form"], *r["variants"]]:
            bp.setdefault(_plain(f), []).append(r)
            bd.setdefault(_depal(f), []).append(r)
            bg.setdefault(key(f, "generic-H"), []).append(r)
    return bp, bd, bg


def test_link_root_by_liv_page_and_gloss():
    harvest = _root("sh1es", "sh₁es-", "harvest", variants=["h₁es-"])
    be = _root("h1es", "h₁es-", "to be", page=241)
    rec = {"root": "h₁es-", "root_alternatives": ["h₁es-"], "root_gloss_en": "be, exist", "liv_ref": "LIV 241f."}
    assert link_root(rec, *_index([harvest, be]))[0] is be
    # no page: a homograph tie, or no gloss overlap, leaves the root unlinked
    remember = _root("smer", "smer-", "to remember")
    rec = {"root": "smer-", "root_alternatives": ["smer-"], "root_gloss_en": "a greasy substance: marrow, fat"}
    assert link_root(rec, *_index([remember]))[0] is None
    # ḱ and k are different roots: *k̂el- 'warm' is not skel-/kel- 'bend'
    bend = _root("skel", "skel-", "to bend", variants=["kel-"])
    rec = {"root": "ḱel-", "root_alternatives": ["ḱel-"], "root_gloss_en": "become warm"}
    assert link_root(rec, *_index([bend]))[0] is None
    # the other series is accepted only with the gloss (sources disagree on some roots' series)
    rec = {"root": "ḱel-", "root_alternatives": ["ḱel-"], "root_gloss_en": "bend, crook"}
    assert link_root(rec, *_index([bend])) == (bend, "loose-form+gloss")


def test_root_alternatives_split_only_before_a_new_form():
    import re
    parts = re.split(r"\s*,\s*|\s*/\s*(?=[?*])", "*su̯ek̂ur̥/u̯er-")
    assert parts == ["*su̯ek̂ur̥/u̯er-"]
    assert re.split(r"\s*,\s*|\s*/\s*(?=[?*])", "*kor-o-, *kor-i̯o-") == ["*kor-o-", "*kor-i̯o-"]


# --- the duplicate check (P4) ---------------------------------------------------------------

class _Reg:
    def get(self, key, base):
        return base


def _nil_rec(root, gloss, formations):
    return {"root": root, "root_alternatives": [root], "root_gloss_en": gloss, "liv_ref": None,
            "root_printed": "*" + root, "page": {"pdf": 1, "printed": 1},
            "formations": [{"printed": p, "stem": stem(p), "marker": None, "indent": 0, "gender": g,
                            "gloss_en": gl, "evidence": ev, "branches": sorted(branches(ev)),
                            "uncertain": False, "flags": []} for p, g, gl, ev in formations]}


def test_duplicates_attach_instead_of_creating():
    entries = {e["id"]: e for e in [
        _root("r-dawn", "h₂ews-", "to dawn"), _root("r-dwell", "h₂wes-", "to dwell"),
        _root("r-give", "deh₃-", "to give"), _root("r-mer", "mer-", "to die"),
        _w("gold", "h₂éh₂usom", ["gold"], root="r-dawn"),          # under another root
        _w("giver", "déh₃tōr", ["giver"], root="r-other"),          # h₃ colouring
        _w("mortal", "mórtos", ["mortal"], root="r-mer"),           # other ablaut grade
    ]}
    two = ["ved. X- m. 'Y'", "gr. Z m. 'W'"]
    recs = [
        _nil_rec("h₂wes-", "dwell", [("*h₂áh₂-us-o-", "m", "gold", two)]),
        _nil_rec("deh₃-", "give", [("*dóh₃-tor-", "m", "giver", two)]),
        _nil_rec("mer-", "die", [("*mér-to-", "m", "mortal, human", two),
                                 ("*mr̥-tí-", "f", "death", ["ved. mr̥tí- f. 'Tod'"])]),
    ]
    rep = apply(entries, recs, _Reg())
    assert rep["duplicate"] == 3 and rep["new"] == 1
    assert entries["gold"]["nil"][0]["match"] == "duplicate"
    assert entries["giver"]["nil"][0]["match"] == "duplicate"
    assert entries["mortal"]["nil"][0]["match"] == "duplicate"
    new = [e for e in entries.values() if e.get("source") == "nil"]
    assert [e["form"] for e in new] == ["mr̥tís"]
    assert new[0]["uncertain"] == ["nil-single-branch"]          # one daughter (P9)


def test_gloss_capitalization_and_articles():
    assert ev_gender(["heth. pattar-palḫi- 'ein Orakelvogel'"]) == "noun"   # indefinite article + noun
    assert ev_gender(["ved. nédiṣṭha- 'der nächste'"]) == "adj"            # substantivized superlative
    # a diphthong-root s-stem is no comparative
    assert citation("h₁éyes", "n") == ("h₁éyos", "noun", "n")
