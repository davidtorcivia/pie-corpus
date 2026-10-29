"""Corpus-quality batch 1, formula witness scan fixes (verdicts:
data/research/8c/corpus-quality/error-verdicts-cq1-formulas.jsonl). Production paths: the shared
group rule, the override resolver, Token construction and the live Homer / Rigveda mappings."""
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from pie import formula_search as fs, formula_search_multi as fm, mapping as mp
from pie.cq1_mapping import group_splits

ROOT = Path(__file__).resolve().parents[1]
LEX = {e["id"]: e for e in fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")}
GMAP = fs.group_map(list(LEX.values()))
PRAISE, MOUNTAIN = "pie-root-gwerH-express_approval", "pie-root-gwerH-mountain"


def _stage(name):
    spec = importlib.util.spec_from_file_location(f"cq1_{name}", ROOT / f"scripts/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_mountain_derivatives_leave_the_praise_group_everywhere():
    for i in ("pie-lex-gworHeh2", "pie-lex-gwrHis", "pie-lex-gworHno"):
        assert LEX[i]["root_id"] == PRAISE          # the lexicon itself is unchanged
        assert GMAP[i] == fs.group_of(LEX[i]) == MOUNTAIN
    # the praise words keep the praise group
    for i in ("pie-lex-gwrneHti", "pie-lex-gwerHtoxr", "pie-lex-gwrHyeti", "pie-lex-gwerHos", PRAISE):
        assert GMAP[i] == PRAISE
    # every consumer computes groups through the shared rule
    assert _stage("build_8c_packets").group_of(LEX["pie-lex-gworHeh2"]) == MOUNTAIN
    assert _stage("build_8c_stageB")._group("pie-lex-gwrHis", LEX) == MOUNTAIN
    assert set(group_splits()) == {"pie-lex-gworHeh2", "pie-lex-gwrHis", "pie-lex-gworHno"}


def test_split_ids_exist_and_group_ids_do_not_collide_with_lexicon_ids():
    data = json.loads((ROOT / "data/research/formulas/group-splits.json").read_text())
    for g in data["groups"]:
        assert g["group"] not in LEX
        assert all(i in LEX for i in g["ids"])


@pytest.mark.parametrize("corpus,lemma,ids", [
    ("rv", "stár- ~ tár-", {"pie-lex-h2stexr"}),
    ("rv", "√piś-", {"pie-root-peykj-hew"}),
    ("rv", "√ci- 1", {"pie-lex-kwinewti-2", "pie-root-kwey-gather"}),
    ("rv", "√hū-", {"pie-lex-gjhewHeti", "pie-root-gjhewH-call_on"}),
    ("rv", "anyá-", set()), ("av", "anya", set()), ("ae", "anya", set()),
    ("rv", "ajuryá-", {"pie-root-gjerh2-grow_old"}),
    ("rv", "girí-", {"pie-lex-gwrHis"}),
    ("av", "tva", set()), ("av", "upamā", {"pie-root-meh1-measure"}), ("av", "asthi", {"pie-lex-h3esth1"}),
    ("lat", "iuppiter", {"pie-lex-dyexws", "pie-lex-ph2texr"}), ("lat", "medulla", set()),
    ("hit", "danku=i-@dunkel", {"pie-root-dhengwh-dark"}),
    ("grp", "σάτυρος", set()), ("grp", "Σάτυρος", set()), ("grp", "Ἀμαζών", set()), ("hom", "Ἀμαζών", set()),
    ("grp", "φατός", {"pie-lex-bhh2tos"}), ("grp", "ἄφατος", {"pie-lex-bhh2tos"}),
    ("grp", "ἔαρ", {"pie-lex-wosr"}), ("hom", "ἔαρ", {"pie-lex-wosr"}),
    ("grp", "πολιός", {"pie-root-pelH-pale"}), ("hom", "πολιός", {"pie-root-pelH-pale"}),
    ("hom", "ἰός", {"pie-lex-Hisus"}), ("grp", "ἰός@arrow", {"pie-lex-Hisus"}),
    ("grp", "ὀμιχέω", {"pie-root-h3meygjh-urinate"}), ("hom", "ἠέλιος", {"pie-lex-soh2wl"}),
])
def test_reviewed_rows_decide_the_lemma(corpus, lemma, ids):
    assert mp.decide(corpus, lemma, {"wrong-auto-root"})[0] == ids


def test_proto_and_key_rows_decide_every_word_through_the_page():
    def table(c):
        rows = [json.loads(l) for l in (ROOT / f"data/research/formulas/mapping/{c}.jsonl").read_text("utf-8").splitlines() if l]
        return fm.apply_table_overrides(c, {r["lemma"]: tuple(r["lex_id"]) for r in rows}, root=ROOT)
    for c in ("menota", "non", "icepahc"):
        assert "kyrr" not in table(c)               # gem-pro *kwerruz 'still' is not *gʷerH- 'praise'
    by = table("byliny")
    assert by["горшок"] == by["горшочка"] == ("pie-lex-gwhrnos",)   # *gъrnьcь < *gʷʰr̥nós, via form-of
    assert by["гора"] == ("pie-lex-gworHeh2",)
    assert "anya" not in table("ae")
    assert table("celt")["bráth"] == ("pie-lex-gwerHtus",)            # rejected report: Wiktionary *brātus
    assert table("av")["kṣam"] == ("pie-lex-dhegjhoxm",)              # Vedic kṣam- 'earth' kept


@pytest.mark.parametrize("corpus,lemma,surface,want", [
    ("grc", "ἰός", "ἰοὺς", "ἰός@arrow"), ("grc-late", "ἰός", "ἰοῖσιν", "ἰός@arrow"),
    ("grc", "ἰός", "ἰοῦ", "ἰός"), ("grc", "ἰός", "ἰὸν", "ἰός"),       # singular: arrow or poison, undecided
    ("sa-ep", "kṣam", "kṣantum", "kṣam@forbear"), ("av", "kṣam", "kṣami", "kṣam"),
])
def test_form_and_corpus_decided_homographs(corpus, lemma, surface, want):
    t = fs.Token(corpus, lemma, surface, "anywhere", {}, True, "noun")
    assert t.lemma == want and t.content


def test_exact_reading_and_its_exceptions():
    assert fs.Token("rv", "√ci- 1", "acet", "RV 10.102.2d", {}, True, "verb").lemma == "√cit-"
    assert fs.Token("rv", "√ci- 1", "acet", "RV 1.1.1a", {}, True, "verb").lemma == "√ci- 1"
    assert fs.Token("rv", "√ci- 1", "cinuhí", "RV 6.53.4b", {}, True, "verb").lemma == "√ci- 1"


def test_avestan_locative_of_good_is_lemmatised_vohu():
    lem = fm.AvestanLemmatizer(fm.LangMapping("ae"), {})   # the reviewed form decides before any stem
    assert lem("vaŋhāu") == "vohu"


@pytest.fixture(scope="module")
def live():
    sb = _stage("build_8c_stageB")
    out = {}
    for c, load, lang, r1 in (("hom", fs.load_homer, "grc", fs.build_homer_mapping),
                              ("rv", fs.load_rv, "sa", fs.build_rv_mapping)):
        toks = load(ROOT)
        out[c] = (toks, sb.live(c, lang, toks, r1(list(LEX.values()), toks), list(LEX.values()), GMAP, ROOT))
    return out


def test_homeric_sun_grey_arrow_and_mountain(live):
    toks, m = live["hom"]
    n = sum(1 for t in toks if t.content and t.lemma == "ἠέλιος")
    assert n >= 120 and m["ἠέλιος"] == ("pie-lex-soh2wl",)
    assert m["πολιός"] == ("pie-root-pelH-pale",) and m["ἰός"] == ("pie-lex-Hisus",)
    assert {GMAP[i] for i in m["Βορέας"]} == {MOUNTAIN}
    assert m["ἥλιος"] == ("pie-lex-soh2wl",)


def test_rigveda_star_call_other(live):
    toks, m = live["rv"]
    assert m["stár- ~ tár-"] == ("pie-lex-h2stexr",)
    assert "pie-root-gjhew-pour" not in {GMAP.get(i, i) for i in m["√hū-"]}
    assert m["√hu-"] == ("pie-root-gjhew-pour",)                    # 'pour' keeps its own root
    assert "anyá-" not in m
    assert [t.lemma for t in toks if t.locus == "RV 10.102.2d" and t.surface == "acet"] == ["√cit-"]
