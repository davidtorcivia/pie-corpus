import collections
import math

import pytest

from pie import formula_search as fs


def tok(corpus, lemma, unit, surface=None, pos="noun", case=None, number="SG", content=True, finite=False, i=0):
    units = ({"pada": unit, "stanza": unit[:-1], "hymn": "1.1"} if corpus == "rv"
             else {"line": unit, "sentence": "s", "book": "Il. 1"})
    return fs.Token(corpus, lemma, surface or lemma, unit, units, content, pos, case, number, finite)


# ---------------------------------------------------------------- normalization

def test_skt_key_strips_vowel_accents_only():
    assert fs.skt_key("śrávas-") == "śravas"          # ś keeps its acute
    assert fs.skt_key("√kr̥-") == "kṛ"                 # ISO r̥ = IAST ṛ
    assert fs.skt_key("vŕ̥ṣan-") == "vṛṣan"            # accent on syllabic r goes too
    assert fs.skt_key("puróhitaṁ") == fs.skt_key("puróhitaṃ") == "purohitaṃ"
    assert fs.skt_key("√janⁱ-") == "jan"


def test_skt_lemma_keys():
    assert fs.skt_lemma_keys("√īḍ- ~ īḷ-") == ["īḍ", "īḷ"]
    assert fs.skt_lemma_keys("√as- 1") == ["as"]


def test_grc_key():
    assert fs.grc_key("ἔχῐς") == fs.grc_key("ἔχις")     # breve off
    assert fs.grc_key("κλέος") == fs.grc_key("κλὲος")   # grave = acute
    assert fs.grc_key("Ζεύς", accents=False) == "ζευσ"
    assert fs.grc_roman("ἵππος") == "ippos" and fs.grc_roman("ἄγγελος") == "angelos"


def test_pie_key_keeps_palatals():
    assert fs.pie_key("ḱléwos") == "ḱlewos"
    assert fs.pie_key("h₁ōḱ-éw-es") == "h₁oḱewes"


# ---------------------------------------------------------------- root table and bridges

@pytest.mark.parametrize("form,root", [
    ("cetayati", "cit"), ("dadhāti", "dhā"), ("juhoti", "hu"), ("bharati", "bhṛ"), ("vardhati", "vṛdh"),
])
def test_skt_root_candidates(form, root):
    assert root in fs.skt_root_candidates(form)


def test_pii_to_skt():
    assert fs.pii_to_skt("*Háćwas")[:2] == ["aśvas", "aśva"]
    assert fs.pii_to_skt("*ǰʰan-") == ["han"]
    assert "dhṛ" in fs.pii_to_skt("*dʰar-")
    assert "pitar" in fs.pii_to_skt("*pHtā́")          # CHC → CiC; agent noun citation
    assert fs.pii_to_skt("*dʰuHmás")[:2] == ["dhūmas", "dhūma"]


def test_ph_to_grc():
    assert fs.ph_to_grc("*íkkʷos") == ["ippos"]
    assert fs.ph_to_grc("*kléwos") == ["kleos"]
    assert fs.ph_to_grc("*Dzéus") == ["zeus"]
    assert "mētēr" in fs.ph_to_grc("*mā́tēr")
    assert fs.ph_to_grc("*gʷíyos") == ["bios"]          # gʷ → d only before e


def test_privatives():
    assert "kṣi" in fs.skt_privative("akṣita")
    assert fs.skt_privative("anāgas") == ["āgas"]
    assert "φθιω" in fs.grc_privative("αφθιτοσ")
    assert fs.grc_privative("αμβροτοσ")[0] == "βροτοσ"
    assert fs.grc_privative("αειδω") == []              # ἀ- before a vowel is not privative


# ---------------------------------------------------------------- mapping

LEX = [
    {"id": "r-kjlew", "kind": "root", "form": "ḱlew-", "root_id": "r-kjlew",
     "reflexes": {"Sanskrit": [{"form": "श्रु", "roman": "śru"}]}},
    {"id": "w-kjlewos", "kind": "word", "form": "ḱléwos", "root_id": "r-kjlew",
     "reflexes": {"Proto-Indo-Iranian": [{"form": "*ćráwas"}], "Proto-Hellenic": [{"form": "*kléwos"}]}},
    {"id": "r-kweyt", "kind": "root", "form": "kʷeyt-", "root_id": "r-kweyt",
     "reflexes": {"Sanskrit": [{"form": "चेतयति", "roman": "cetáyati"}]}},
    {"id": "w-megh2s", "kind": "word", "form": "méǵh₂s", "root_id": None,
     "reflexes": {"Ancient Greek": [{"form": "μέγᾰς", "roman": "mégas"}], "Proto-Indo-Iranian": [{"form": "*maȷ́ʰā́"}]}},
    {"id": "w-loan", "kind": "word", "form": "x", "root_id": None,
     "reflexes": {"Sanskrit": [{"form": "x", "roman": "máh", "borrowed": True}]}},
]


def test_rv_mapping_tiers_and_root_collapse():
    toks = [tok("rv", "√śru- 1", "1.1.1a"), tok("rv", "śrávas-", "1.1.1a"), tok("rv", "√cit-", "1.1.1b"),
            tok("rv", "máh-", "1.1.1b"), tok("rv", "índra-", "1.1.1c")]
    m = fs.build_rv_mapping(LEX, toks)
    assert m.lemma_groups["√śru- 1"] == {"r-kjlew"} and m.lemma_tier["√śru- 1"] == "direct"
    assert m.lemma_groups["śrávas-"] == {"r-kjlew"} and m.lemma_tier["śrávas-"] == "bridge"   # derivative → its root
    assert m.lemma_groups["√cit-"] == {"r-kweyt"} and m.lemma_tier["√cit-"] == "roots"
    assert m.lemma_groups["máh-"] == {"w-megh2s"}            # borrowed reflex ignored, bridge used
    assert "índra-" not in m.lemma_groups
    cov = fs.coverage(toks, m)
    assert cov["tokens_mapped"] == 4 and cov["tokens"] == 5


def test_homer_mapping():
    toks = [tok("hom", "μέγας", "Il. 1.1"), tok("hom", "κλέος", "Il. 1.1"), tok("hom", "θεός", "Il. 1.2")]
    m = fs.build_homer_mapping(LEX, toks)
    assert m.lemma_groups["μέγας"] == {"w-megh2s"} and m.lemma_tier["μέγας"] == "direct"
    assert m.lemma_groups["κλέος"] == {"r-kjlew"} and m.lemma_tier["κλέος"] == "bridge"
    assert "θεός" not in m.lemma_groups


# ---------------------------------------------------------------- counting and scoring

A, B, C = frozenset({"a"}), frozenset({"b"}), frozenset({"c"})


def test_pairs_need_two_tokens():
    assert fs._pairs_of([A | B]) == set()                   # one ambiguous token is not a pair
    assert fs._pairs_of([A, B, frozenset()]) == {("a", "b")}


def test_count_units_presence_per_unit():
    c = fs.count_units([[A, B, B], [A], [B, C]])
    assert c.n == 3 and c.single == {"a": 2, "b": 2, "c": 1}
    assert c.pair == {("a", "b"): 1, ("b", "c"): 1}


def test_count_windows():
    seg = [A, frozenset(), B, frozenset(), frozenset(), C]
    c = fs.count_windows([seg], 2)
    assert c.pair == {("a", "b"): 1}                        # b–c are 3 apart
    assert c.n == 2 + 2 + 2 + 2 + 1                         # token pairs at distance ≤ 2
    assert c.single["a"] == 2 and c.single["b"] == 4


def test_llr_sign_and_value():
    assert fs.llr(10, 10, 10, 100) > 0 > fs.llr(0, 50, 50, 100)
    # independent table → 0
    assert fs.llr(25, 50, 50, 100) == pytest.approx(0, abs=1e-9)
    o, e = (10, 0, 0, 90), (1, 9, 9, 81)
    assert fs.llr(10, 10, 10, 100) == pytest.approx(2 * sum(a * math.log(a / b) for a, b in zip(o, e) if a))
    assert fs.pmi(10, 10, 10, 100) == pytest.approx(math.log2(10))


def test_score_pairs_needs_both_corpora():
    u_strong = [[A, B]] * 5 + [[C]] * 95
    u_none = [[A], [B]] * 5 + [[C]] * 90 + [[A, B]]
    both = fs.score_pairs(fs.count_units(u_strong), fs.count_units(u_strong), min_count=3)
    assert [r["pair"] for r in both] == [("a", "b")]
    assert fs.score_pairs(fs.count_units(u_strong), fs.count_units(u_none), min_count=1) == []


def test_score_ranks_by_weaker_corpus():
    strong = fs.count_units([[A, B]] * 8 + [[A, C]] * 4 + [[C]] * 88)
    weak = fs.count_units([[A, B]] * 4 + [[A, C]] * 8 + [[C]] * 88)
    r = fs.score_pairs(strong, weak, min_count=3, llr_min=0)
    s = {x["pair"]: x for x in r}
    assert s[("a", "b")]["score"] == min(s[("a", "b")]["rv"]["llr"], s[("a", "b")]["hom"]["llr"])


def test_shuffled_keeps_units_and_multiset():
    toks = [tok("rv", "x", f"1.1.{i}a") for i in range(20)]
    for i, t in enumerate(toks):
        t.roots = frozenset({str(i % 3)})
    s = fs.shuffled(toks, seed=1)
    assert [t.units for t in s] == [t.units for t in toks]
    assert collections.Counter(t.roots for t in s) == collections.Counter(t.roots for t in toks)
    assert toks[0].roots == frozenset({"0"})                # original untouched


# ---------------------------------------------------------------- evaluation

def test_split_half_is_fixed():
    assert fs.split_half("swift-horses") == fs.split_half("swift-horses")
    halves = collections.Counter(fs.split_half(f"f{i}") for i in range(200))
    assert 70 < halves["A"] < 130


def test_recall_at_k():
    ranking = [{"pair": ("a", "b")}, {"pair": ("c", "d")}, {"pair": ("e", "f")}]
    gold = [{"formula_id": "x", "pairs": [("c", "d")]}, {"formula_id": "y", "pairs": [("g", "h")]}]
    r = fs.recall(ranking, gold, ks=(1, 2))
    assert r["recall@1"] == 0 and r["recall@2"] == 0.5 and r["ranks"] == {"x": 2, "y": None}


class _Lem:
    def __init__(self, v, g):
        self.v, self.g = v, g

    def vedic(self, w):
        return frozenset(self.v.get(w, ()))

    def greek(self, w):
        return frozenset(self.g.get(w, ()))


def test_gold_set_pairs():
    f = {"formula_id": "great-fame", "kind": "phrase", "pie": "méǵh₂ ḱléwos",
         "attestations": [{"lang": "Vedic", "text": "máhi śrávas"}, {"lang": "Greek", "text": "μέγα κλέος"}]}
    lem = _Lem({"máhi": ["m"], "śrávas": ["k"]}, {"μέγα": ["m"], "κλέος": ["k"]})
    idx = [("ḱlewos", frozenset({"k"})), ("meǵh₂", frozenset({"m"}))]
    g = fs.gold_set([f], lem, idx)
    assert g[0]["pairs"] == [("k", "m")] and g[0]["attested_pairs"] == [("k", "m")] and g[0]["pie_pairs"] == [("k", "m")]
    # one PIE word and no attested pair: not evaluable
    f2 = {**f, "formula_id": "lex", "kind": "lexical", "pie": "ḱléwes-",
          "attestations": [{"lang": "Vedic", "text": "śrávas"}, {"lang": "Greek", "text": "μέγα κλέος"}]}
    assert fs.gold_set([f2], lem, idx) == []
    # no Greek attestation: not evaluable
    f3 = {**f, "formula_id": "v", "attestations": [{"lang": "Vedic", "text": "máhi śrávas"}]}
    assert fs.gold_set([f3], lem, idx) == []


def test_relation_and_parallel():
    v = tok("rv", "√han-", "1.1.1a", pos="verb", case=None, finite=True)
    o = tok("rv", "áhi-", "1.1.1a", case="ACC")
    adj = tok("rv", "máh-", "1.1.1a", case="ACC")
    assert fs.relation(v, o) == "verb+acc" and fs.relation(o, adj) == "agree"
    assert fs.parallel_relation(collections.Counter({"verb+acc": 3, "other": 9}),
                                collections.Counter({"verb+acc": 2})) == "verb+acc"
    assert fs.parallel_relation(collections.Counter({"verb+acc": 3}), collections.Counter({"agree": 4})) is None


def test_known_pairs_covers_pie_wording_of_any_kind():
    lem = _Lem({}, {})
    idx = [("ḱlewos", frozenset({"k"})), ("meǵh₂", frozenset({"m"}))]
    f = {"formula_id": "x", "kind": "schema", "pie": "méǵh₂ ḱléwos",
         "attestations": [{"lang": "Avestan", "text": "..."}]}
    assert fs.known_pairs([f], lem, idx) == {("k", "m")}


# ================================================================ round 2

# ---------------------------------------------------------------- kaikki links

def _entry(word, roman, templates, pos="noun"):
    return {"word": word, "pos": pos, "forms": [{"form": roman, "tags": ["romanization"]}],
            "etymology_templates": templates}


def test_kaikki_entry_links_templates():
    d = _entry("विश्व", "víśva", [
        {"name": "inh", "args": {"1": "sa", "2": "iir-pro", "3": "*wíćwas"}},
        {"name": "inh", "args": {"1": "sa", "2": "ine-pro", "3": "", "4": "*(h₁)wiḱ-wo-s"}},
        {"name": "cog", "args": {"1": "ae", "2": "x"}},
        {"name": "root", "args": {"1": "sa", "2": "ine-pro", "3": "*weyḱ-"}},
    ])
    r = fs.kaikki_entry_links(d, "sa")
    assert r["pie"] == ["*(h₁)wiḱ-wo-s"]                 # arg 4 when arg 3 is empty
    assert r["proto"] == [("iir-pro", "*wíćwas")] and r["pie_root"] == ["*weyḱ-"] and r["roman"] == "víśva"
    assert fs.kaikki_entry_links(_entry("x", "x", [{"name": "cog", "args": {"1": "sa", "2": "ine-pro", "3": "*x"}}]),
                                 "sa") is None
    af = _entry("ἄφθιτος", "áphthitos", [{"name": "af", "args": {"1": "grc", "2": "ἀ-<t:not>", "3": "φθίω"}}])
    assert fs.kaikki_entry_links(af, "grc")["bases"] == ["φθίω"]  # one non-affix part
    comp = _entry("x", "x", [{"name": "af", "args": {"1": "grc", "2": "ἵππος", "3": "δάμνημι"}}])
    assert fs.kaikki_entry_links(comp, "grc") is None              # compounds are not chained
    sfx = _entry("x", "x", [{"name": "suffix", "args": {"1": "grc", "2": "κλέος", "3": "ινος"}}])
    assert fs.kaikki_entry_links(sfx, "grc")["bases"] == ["κλέος"]


KLEX = [
    {"id": "r-kjlew", "kind": "root", "form": "ḱlew-", "root_id": "r-kjlew", "reflexes": {}},
    {"id": "w-kjlewos", "kind": "word", "form": "ḱléwos", "root_id": "r-kjlew",
     "reflexes": {"Proto-Indo-Iranian": [{"form": "*ćráwas"}]}},
    {"id": "r-dhgwhey", "kind": "root", "form": "dʰgʷʰey-", "root_id": "r-dhgwhey", "reflexes": {}},
    {"id": "w-ekwos", "kind": "word", "form": "h₁éḱwos", "root_id": None, "reflexes": {}},
]


def test_pie_index_exact_loose_and_proto():
    idx = fs.PieIndex(KLEX)
    assert idx.pie("*ḱléwos") == {"w-kjlewos"}
    assert idx.pie("*ḱlewos") == {"w-kjlewos"}            # accent-free fallback
    assert idx.pie("*ḱlew-") == {"r-kjlew"}
    assert idx.via_proto("sa", "iir-pro", "*ćráwas") == {"w-kjlewos"}
    assert idx.via_proto("grc", "iir-pro", "*ćráwas") == set()


def test_resolve_kaikki_tiers_chain_and_pseudo():
    links = [
        {"word": "κλέος", "roman": "kléos", "pos": "noun", "pie": ["*ḱléwos"], "pie_root": [], "proto": [], "bases": []},
        {"word": "φθίω", "roman": "phthíō", "pos": "verb", "pie": ["*dʰgʷʰey-"], "pie_root": [], "proto": [], "bases": []},
        {"word": "ἄφθιτος", "roman": "", "pos": "adj", "pie": [], "pie_root": [], "proto": [], "bases": ["φθίω"]},
        {"word": "κλύω", "roman": "", "pos": "verb", "pie": [], "pie_root": ["*ḱlew-"], "proto": [], "bases": []},
        {"word": "πᾶς", "roman": "", "pos": "adj", "pie": ["*ph₂ents"], "pie_root": [], "proto": [], "bases": []},
    ]
    idx = fs.PieIndex(KLEX)
    r = fs.resolve_kaikki(links, idx, "grc", fs.grc_key)
    assert r[fs.grc_key("κλέος")] == ("kaikki", {"w-kjlewos"})
    assert r[fs.grc_key("ἄφθιτος")] == ("kaikki-chain", {"r-dhgwhey"})
    assert r[fs.grc_key("κλύω")] == ("kaikki-root", {"r-kjlew"})
    assert fs.grc_key("πᾶς") not in r
    rp = fs.resolve_kaikki(links, idx, "grc", fs.grc_key, pseudo=True)
    assert rp[fs.grc_key("πᾶς")] == ("kaikki-pseudo", {"kaikki:ph₂ents"})


def test_build_kaikki_mapping_backoff_order():
    toks = [tok("hom", "κλέος", "Il. 1.1"), tok("hom", "ἄφθιτος", "Il. 1.1"), tok("hom", "πᾶς", "Il. 1.2"),
            tok("hom", "ἵππος", "Il. 1.2")]
    links = [
        {"word": "κλέος", "roman": "", "pos": "noun", "pie": ["*ḱléwos"], "pie_root": [], "proto": [], "bases": []},
        {"word": "ἄφθιτος", "roman": "", "pos": "adj", "pie": ["*dʰgʷʰey-"], "pie_root": [], "proto": [], "bases": []},
        {"word": "πᾶς", "roman": "", "pos": "adj", "pie": ["*ph₂ents"], "pie_root": [], "proto": [], "bases": []},
        {"word": "ἵππος", "roman": "", "pos": "noun", "pie": ["*xyzzy"], "pie_root": [], "proto": [], "bases": []},
    ]
    backoff = fs.Mapping({"ἵππος": frozenset({"w-ekwos"}), "κλέος": frozenset({"zz"})},
                         {"ἵππος": "direct", "κλέος": "direct"}, set(),
                         {"ἵππος": frozenset({"w-ekwos"}), "κλέος": frozenset({"zz"})})
    m = fs.build_kaikki_mapping("grc", KLEX, toks, backoff, links=links, pseudo=True)
    assert m.lemma_lex["κλέος"] == {"w-kjlewos"} and m.lemma_groups["κλέος"] == {"r-kjlew"}   # kaikki beats backoff
    assert m.lemma_tier["ἄφθιτος"] == "kaikki"
    assert m.lemma_tier["ἵππος"] == "direct"            # backoff beats a pseudo etymon
    assert m.lemma_tier["πᾶς"] == "kaikki-pseudo" and m.lemma_groups["πᾶς"] == {"kaikki:ph₂ents"}


def test_apply_mapping_levels():
    m = fs.Mapping({"κλέος": frozenset({"r-kjlew"})}, {"κλέος": "kaikki"}, set(), {"κλέος": frozenset({"w-kjlewos"})})
    t = [tok("hom", "κλέος", "Il. 1.1")]
    fs.apply_mapping(t, m, level="lexeme")
    assert t[0].roots == {"w-kjlewos"}
    fs.apply_mapping(t, m, level="group")
    assert t[0].roots == {"r-kjlew"}


def test_lat_key():
    assert fs.lat_key("Iūppiter") == "iuppiter" and fs.lat_key("vīvus") == "uiuus" and fs.lat_key("lustro2") == "lustro"


def test_load_latin(tmp_path):
    d = tmp_path / fs.LATIN
    d.mkdir(parents=True)
    row = "\t".join(["1", "Marti", "Mars", "PROPN", "x", "Case=Dat|Number=Sing", "_", "_", "_",
                     "CitationHierarchy=Capitulum_141,Paragraphus_2"])
    row2 = "\t".join(["2", "pater", "pater", "NOUN", "x", "Case=Voc|Number=Sing", "_", "_", "_",
                      "CitationHierarchy=Capitulum_141,Paragraphus_2"])
    (d / "Cato_CatoAgricultura_CatAgr.conllup").write_text(f"# sent_id = s1\n{row}\n{row2}\n\n", "utf-8")
    t = fs.load_latin(tmp_path)
    assert [x.lemma for x in t] == ["Mars", "pater"] and t[1].case == "VOC" and t[1].content and not t[0].content
    assert t[0].units["line"] == "CatAgr 141.2" and t[0].corpus == "lat"


# ---------------------------------------------------------------- exact scoring

def _hyper_sf(o, K, d, N):
    return sum(math.comb(K, i) * math.comb(N - K, d - i) for i in range(o, min(K, d) + 1)) / math.comb(N, d)


@pytest.mark.parametrize("o,K,d,N", [(1, 1, 1, 100), (2, 5, 7, 40), (0, 3, 3, 10), (5, 10, 10, 30),
                                     (3, 50, 60, 1000), (30, 300, 400, 40000), (1, 300, 400, 40000)])
def test_hypergeom_logsf_matches_enumeration(o, K, d, N):
    assert math.exp(fs.hypergeom_logsf(o, K, d, N)) == pytest.approx(_hyper_sf(o, K, d, N), rel=1e-9)


def test_poisson_and_midp():
    sf = lambda o, l: 1 - sum(math.exp(-l) * l ** i / math.factorial(i) for i in range(o))
    for o, lam in [(1, 0.01), (3, 2.5), (10, 2.0)]:
        assert math.exp(fs.poisson_logsf(o, lam)) == pytest.approx(sf(o, lam), rel=1e-9)
    pmf1 = math.exp(-0.5) * 0.5
    assert math.exp(fs.poisson_logsf(1, 0.5, midp=True)) == pytest.approx(sf(2, 0.5) + pmf1 / 2, rel=1e-9)


def test_fisher_closed_form():
    p1, p2 = 0.01, 0.02
    q = p1 * p2
    assert math.exp(fs.fisher_logp([math.log(p1), math.log(p2)])) == pytest.approx(q * (1 - math.log(q)))
    assert fs.fisher_logp([0.0, 0.0]) == 0.0
    # chi-square with 6 dof
    x = -2 * math.log(0.1 * 0.2 * 0.3)
    want = math.exp(-x / 2) * (1 + x / 2 + (x / 2) ** 2 / 2)
    assert math.exp(fs.fisher_logp([math.log(0.1), math.log(0.2), math.log(0.3)])) == pytest.approx(want)


D = frozenset({"d"})


def test_score_exact_single_rare_cooccurrence_counts():
    # a and b occur once each and together: one co-occurrence is improbable
    rare = fs.count_units([[A, B]] + [[C]] * 499 + [[D]] * 500)
    # c and d are frequent and co-occur at chance
    common = fs.count_units([[A, B]] + [[C, D]] * 250 + [[C]] * 250 + [[D]] * 250 + [[]] * 249)
    r = fs.score_exact([rare, common], min_count=1)
    assert r[0]["pair"] == ("a", "b") and r[0]["n"] == [1, 1]
    assert r[0]["score"] > 4                               # p ≈ 1e-3 in each, Fisher ≈ 1e-5


def test_score_exact_needs_every_corpus_and_ranks_by_weaker():
    x = fs.count_units([[A, B]] * 5 + [[A, C]] * 2 + [[C]] * 93)
    y = fs.count_units([[A, C]] * 5 + [[A]] * 5 + [[B]] * 5 + [[C]] * 85)
    r = {q["pair"]: q for q in fs.score_exact([x, y], min_count=1)}
    assert ("a", "b") not in r                             # no co-occurrence in y
    rm = fs.score_exact([x, y], min_count=1, rank_by="max")
    assert all(q["score"] == pytest.approx(-max(q["logp"]) / fs.LOG10) for q in rm)


def test_score_exact_floor_and_third_modes():
    big = fs.count_units([[A, B]] * 60 + [[C]] * 940)
    small = fs.count_units([[A, B]] * 1 + [[A]] * 30 + [[B]] * 30 + [[C]] * 939)
    full = fs.score_exact([big, small])[0]["score"]
    capped = fs.score_exact([big, small], floor=-10.0)[0]["score"]
    assert capped < full
    lat_none = fs.count_units([[A]] * 10 + [[B]] * 10 + [[C]] * 80)          # testable, no co-occurrence
    assert fs.score_exact([big, small], third=lat_none, third_mode="require") == []
    f3 = fs.score_exact([big, small], third=lat_none, third_mode="fisher3")[0]["score"]
    f3pos = fs.score_exact([big, small], third=lat_none, third_mode="fisher3pos")[0]["score"]
    assert f3 < f3pos == pytest.approx(full)               # an absent third co-occurrence costs only in fisher3


def test_score_exact_bonus_and_keep():
    x = fs.count_units([[A, B]] * 3 + [[A, C]] * 3 + [[C]] * 94)
    s = {q["pair"]: q["score"] for q in fs.score_exact([x, x])}
    b = {q["pair"]: q["score"] for q in fs.score_exact([x, x], bonus={("a", "c"): 2.0})}
    assert b[("a", "c")] == pytest.approx(s[("a", "c")] + 2.0) and b[("a", "b")] == pytest.approx(s[("a", "b")])
    assert [q["pair"] for q in fs.score_exact([x, x], keep={("a", "b")}.__contains__)] == [("a", "b")]


# ---------------------------------------------------------------- syntax links

def test_edges_and_relations():
    adj = tok("hom", "ὠκύς", "Il. 1.1", pos="adj", case="NOM")
    noun = tok("hom", "ἵππος", "Il. 1.1", case="NOM")
    verb = tok("hom", "ἄγω", "Il. 1.1", pos="verb", finite=True)
    obj = tok("hom", "βοῦς", "Il. 1.1", case="ACC")
    adj.head, adj.rel = 1, "ATR"
    obj.head, obj.rel = 2, "OBJ"
    ts = [adj, noun, verb, obj]
    for t, r in zip(ts, [A, B, C, D]):
        t.roots = r
    assert fs.dep_edges(ts) == [(0, 1), (3, 2)]
    c = fs.count_edges(ts, fs.dep_edges(ts))
    assert c.kind == "pairs" and c.n == 2 and c.pair == {("a", "b"): 1, ("c", "d"): 1}
    rel = fs.edge_relations(ts, fs.dep_edges(ts))
    assert rel[("a", "b")] == {"adj+noun": 1} and rel[("c", "d")] == {"verb+obj": 1}
    assert fs.dominant_relation(collections.Counter({"other": 5, "verb+obj": 1})) == "verb+obj"
    assert fs.dominant_relation(collections.Counter({"other": 5})) is None


def test_adjacency_edges_in_pada_skip_function_words():
    ts = [tok("rv", "ákṣiti-", "1.1.1a"), tok("rv", "ca", "1.1.1a", content=False), tok("rv", "śrávas-", "1.1.1a"),
          tok("rv", "√dhā-", "1.1.1b")]
    assert fs.adjacency_edges(ts, "pada", 1) == [(0, 2)]
    assert fs.adjacency_edges(ts, "pada", 1, content_only=False) == [(0, 1), (1, 2)]


# ---------------------------------------------------------------- silver set and CV helpers

def test_is_vedic_like_and_passage_tokens():
    assert fs.is_vedic_like("śrávaḥ") and fs.is_vedic_like("ákṣitam") and not fs.is_vedic_like("glory")
    assert not fs.is_vedic_like("κλέος")
    toks = fs.passage_tokens("Kuhn: ákṣiti śrávaḥ, κλέος ἄφθιτον.")
    assert [(w, s) for _, w, s in toks] == [("Kuhn", "lat"), ("ákṣiti", "skt"), ("śrávaḥ", "skt"),
                                             ("κλέος", "grc"), ("ἄφθιτον", "grc")]


def test_silver_pairs_phrase_and_span():
    lem = _Lem({"ákṣiti": ["dh"], "śrávaḥ": ["kl"], "máhi": ["m"]}, {"κλέος": ["kl"], "ἄφθιτον": ["dh"], "μέγα": ["m"]})
    text = "a phrase common to Vedic and Homeric poetry: ákṣiti śrávaḥ, κλέος ἄφθιτον."
    c = fs.cited_groups(text, lem.vedic, lem.greek)
    assert fs.silver_pairs_in(c) == {("dh", "kl")}
    far = "máhi " + "x " * 60 + "śrávaḥ and μέγα κλέος"         # Vedic words too far apart for a phrase
    assert fs.silver_pairs_in(fs.cited_groups(far, lem.vedic, lem.greek)) == set()
    assert ("kl", "m") in fs.co_mentions(fs.cited_groups(far, lem.vedic, lem.greek))
    s, m = fs.build_silver([({"book": "west", "para": 3}, text)], lem.vedic, lem.greek)
    assert s == {("dh", "kl"): [{"book": "west", "para": 3}]}


def test_eval_items_merge_and_folds():
    gold = [{"formula_id": "imperishable-fame", "pairs": [("dh", "kl"), ("kl", "x")]}]
    silver = {("dh", "kl"): [], ("a", "b"): []}
    items = fs.eval_items(gold, silver)
    assert len(items) == 2
    merged = next(it for it in items if it["gold"])
    assert merged["silver"] and merged["pairs"] == [("dh", "kl"), ("kl", "x")]
    assert all(it["fold"] == fs.fold_of(it["item_id"]) for it in items)
    assert collections.Counter(fs.fold_of(f"p{i}") for i in range(500)).most_common()[-1][1] > 70


def test_item_ranks_project_and_recall_ci():
    ranking = [{"pair": ("l1", "l2")}, {"pair": ("l3", "l4")}, {"pair": ("l1", "l5")}]
    proj = {"l1": "g1", "l2": "g2", "l3": "g1", "l4": "g2", "l5": "g3"}
    project = lambda p: tuple(sorted((proj[p[0]], proj[p[1]])))
    items = [{"pairs": [("g1", "g3")]}, {"pairs": [("g1", "g2")]}, {"pairs": [("g7", "g8")]}]
    assert fs.item_ranks(ranking, items, project) == [2, 1, None]     # duplicate group pair not counted twice
    assert fs.recall_at([2, 1, None], ks=(1, 2)) == {"recall@1": 1 / 3, "recall@2": 2 / 3}
    ci = fs.bootstrap_ci([1, None, 1, None] * 10, ks=(1,), b=500)
    lo, hi = ci["recall@1"]
    assert lo < 0.5 < hi
