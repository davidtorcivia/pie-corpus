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
