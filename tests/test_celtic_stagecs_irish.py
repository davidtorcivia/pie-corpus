"""Irish reader-error regressions; small fixtures, no raw source dependency."""

from pie import celtic_mapping as cm
from pie import formula_search_multi as fm


def lemmatizer(lang="sga"):
    lm = fm.LangMapping(lang)
    forms = {
        "fir": "fer", "bhó": "bó", "bíad": "bíad", "t-ech": "tech",
        "t-art": "tart", "t-echt": "techt", "lotar": "loit",
        "lotair": "loit", "cas": "cas", "deógan": "eógan",
        "nalpain": "alpán", "aingil": "aingel", "gráin": "grán|gráin",
        "no-mbligtis": "?nombligtis", "husci": "?husci",
    }
    return cm.CelticLemmatizer(lm, cm.irish_demutate, cm.irish_skeleton,
                              form_overrides={fm.KEYS[lang](k): v for k, v in forms.items()},
                              use_skeleton=False)


def test_copula_and_food_noun_do_not_cross_contaminate():
    lz = lemmatizer()
    assert cm.lemmatize_words(lz, ["gur'", "bhó", "fliuch"])[1] == "bo"
    assert cm.lemmatize_words(lz, ["in", "bhó", "bán"])[1] == "bó"
    assert cm.lemmatize_words(lz, ["no", "bíad", "Congal"])[1] == "bí"
    assert cm.lemmatize_words(lz, ["in", "bíad"])[1] == "bíad"
    assert not cm.content_of(lz.lm, "bo", "bhó", lz)
    assert cm.content_of(lz.lm, "bó", "bhó", lz)


def test_truth_reading_does_not_replace_men_everywhere():
    lz = lemmatizer()
    assert cm.lemmatize_words(lz, ["As", "fir", "don", "clamh"])[1] == "fír"
    assert cm.lemmatize_words(lz, ["na", "fir", "don", "chath"])[1] == "fer"
    assert cm.lemmatize_words(lz, ["fir", "don"])[0] == "fer"
    assert lz("fir") == "fer"  # contextual results must not poison the form cache


def test_explicit_t_prothesis_is_disambiguated_in_context():
    lz = lemmatizer()
    for form, following, target in (("t-ech", "bocóidech", "ech"),
                                    ("t-art", "amnas", "art"),
                                    ("t-echt", "dosom", "écht")):
        assert cm.lemmatize_words(lz, ["in", form, following])[1] == target
    assert cm.lemmatize_words(lz, ["in", "tech", "bocóidech"])[1] != "ech"


def test_reviewed_names_include_prefixed_and_initial_forms():
    lz = lemmatizer()
    for form, target in (("nAlpain", "alba (name)"), ("d'Eōgan", "eógan (name)"),
                         ("Cas", "cas (name)"), ("Cáilte", "caílte (name)")):
        assert cm.lemmatize_words(lz, [form])[0] == target
    assert cm.lemmatize_words(lz, ["cas"])[0] == "cas"
    assert cm.lemmatize_words(lz, ["deógan"])[0] == "eógan"


def test_suppletive_preterite_keeps_its_own_etymon():
    lz = lemmatizer()
    assert cm.lemmatize_words(lz, ["Lotar", "na", "slóig"])[0] == "luid"
    assert cm.lemmatize_words(lz, ["léo", "lotair", "îor", "muir"])[1] == "luid"
    table = cm.read_table("celt")
    assert set(table["luid"]) == {"pie-lex-h1ludhet"}
    assert set(table["dobeir@give-present"]) == {"pie-root-bher-bear"}


def test_unmapped_homograph_senses_cannot_fall_back_to_wrong_roots():
    lz = lemmatizer()
    assert cm.lemmatize_words(lz, ["bennachadur", "aingil", "Dé"])[1] == "aingel@angel"
    assert cm.lemmatize_words(lz, ["gabus", "gráin", "egla"])[1] == "gráin@fear"
    table = cm.read_table("celt")
    for sense in ("aingel@angel", "gráin@fear", "adaig@night", "áith@sharp", "brú@belly"):
        assert not table.get(sense)
    assert set(table["ingen@nail"]) == {"pie-lex-h3noxghs"}


def test_irish_context_rules_do_not_apply_to_welsh():
    assert cm.lemmatize_words(lemmatizer("cy"), ["As", "fir", "don"])[1] == "fer"


def test_truncated_sword_form_requires_the_blade_edge_context():
    lz = lemmatizer()
    assert cm.lemmatize_words(lz, ["fo", "fâcbur", "a", "chlaid"])[-1] == "claideb"
    assert cm.lemmatize_words(lz, ["a", "chlaid"])[-1] != "claideb"
    assert cm.lemmatize_words(lz, ["fâcbur", "chlaid"])[-1] != "claideb"
