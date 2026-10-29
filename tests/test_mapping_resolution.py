"""One mapping resolution (pie/mapping.py) for every consumer: the reviewed overrides add, remove and remap
lemmas, and no later evidence route of the secure checker (pie/tier2_secure.py) restores what they removed."""

import collections
import json
from pathlib import Path

from pie import formula_search_multi as fm
from pie import mapping as mp
from pie.tier2_secure import SecureChecker, build_population, code_of, load_population, row_keys

ROOT = Path(__file__).resolve().parent.parent


def rec(ids, word, code, src):
    return (frozenset(ids), (src, f"{code}:{word}"), src, False)


def real_row(corpus, lemma):
    return next(r for r in mp.read_table(corpus, ROOT) if r["lemma"] == lemma)


# ---------------------------------------------------------------- David's review cases, on the shipped data

ENTRIES = {
    # the lexicon lists Latv. pūrs under *péh₂wr̥ (via Proto-Balto-Slavic)
    "pie-lex-peh2wr": {"id": "pie-lex-peh2wr", "form": "péh₂wr̥", "reflexes": {"Latvian": [{"form": "pūrs"}]}},
    "pie-root-gwerh3-swallow": {"id": "pie-root-gwerh3-swallow", "kind": "root", "form": "gʷerh₃-"},
    "pie-lex-gwrh3eti": {"id": "pie-lex-gwrh3eti", "form": "gʷr̥h₃éti", "root_id": "pie-root-gwerh3-swallow",
                         "reflexes": {"Sanskrit": [{"form": "गिरति", "roman": "giráti"}]}},
    "pie-lex-gwerh3t": {"id": "pie-lex-gwerh3t", "form": "gʷérh₃t", "root_id": "pie-root-gwerh3-swallow"},
    "pie-root-gwerH-express_approval": {"id": "pie-root-gwerH-express_approval", "kind": "root", "form": "gʷerH-"},
    "pie-lex-gwerHtis": {"id": "pie-lex-gwerHtis", "form": "gʷérHtis", "root_id": "pie-root-gwerH-express_approval"},
}


def review_checker(population=True):
    rows = {"lv": [real_row("lv", "pūrs")], "av": [real_row("av", "gir")]}
    pop = build_population(rows, fm.load_overrides(ROOT), codes={"lv", "sa"})
    if not population:      # the tables alone, no reviewed decisions over the other routes (the old checker)
        return SecureChecker(ENTRIES, {c: dict(t) for c, t in pop.tables.items()})
    return SecureChecker.from_population(ENTRIES, pop)


def test_purs_removal_is_not_restored_by_the_reflex_list():
    assert real_row("lv", "pūrs")["lex_id"] == ["pie-lex-peh2wr"]        # the automatic table row
    old = review_checker(population=False).match("pie-lex-peh2wr", "lv", "Latvian", "pūrs", True)
    assert old["level"] == "exact" and old["via"] == "reflex"          # the defect
    ch = review_checker()
    assert ch.match("pie-lex-peh2wr", "lv", "Latvian", "pūrs", True) is None
    # an inflected form cited with the lemma is decided by it too
    c = ch.check("pie-lex-peh2wr", [{"lang": "Latvian", "lemmas": ["pūrs"], "words": ["pūru"]}])
    assert c["exact_branches"] == [] and c["root_branches"] == []


def test_purs_in_another_sense_is_not_decided_by_the_dowry_row():
    # the row is about pūrs 'dowry chest' (its erratum's gloss); pūrs 'fire', if cited so, is not that word
    ch = review_checker()
    assert ch.match("pie-lex-peh2wr", "lv", "Latvian", "pūrs", True, sense="dowry chest") is None
    m = ch.match("pie-lex-peh2wr", "lv", "Latvian", "pūrs", True, sense="fire")
    assert m["level"] == "exact" and m["via"] == "reflex"
    c = ch.check("pie-lex-peh2wr", [{"lang": "Latvian", "lemmas": ["pūrs"], "senses": {"pūrs": "fire"}}])
    assert c["exact_branches"] == ["BS"]


def test_gir_praise_does_not_reach_swallow_through_girati():
    old = review_checker(population=False)
    assert old.match("pie-lex-gwerh3t", "sa", "Vedic", "gír-", True)["path"][-1] == "lexicon:Sanskrit:giráti"
    ch = review_checker()
    for lid in ("pie-root-gwerh3-swallow", "pie-lex-gwrh3eti", "pie-lex-gwerh3t"):
        for cited in ("gír-", "gir", "gīr-"):
            assert ch.match(lid, "sa", "Vedic", cited, True) is None, (lid, cited)
    assert ch.match("pie-root-gwerH-express_approval", "sa", "Vedic", "gír-", True)["level"] == "exact"
    assert ch.match("pie-lex-gwerHtis", "sa", "Vedic", "gír-", True)["level"] == "root"
    # the decision is about the lemma gír-, not about every word with its stem: giráti stays *gʷr̥h₃éti
    assert ch.match("pie-lex-gwrh3eti", "sa", "Vedic", "giráti", True)["level"] == "exact"
    c = ch.check("pie-lex-gwrh3eti", [{"lang": "Vedic", "lemmas": ["√gṝ-"], "words": ["giráti"]}])
    assert c["exact_branches"] == ["II"]


# ---------------------------------------------------------------- added rows and the shared population

def test_added_only_override_row_is_used_by_the_checker():
    table = {r["lemma"] for r in mp.read_table("cu", ROOT)}
    ids, row = fm.load_overrides(ROOT)["lemma"]["cu"]["животъ"]
    assert "животъ" not in table and ids == {"pie-lex-gwih3wos"}       # an east.json addition
    pop = load_population(codes={"cu"})
    assert any(x.corpus == "cu" and x.lemma == "животъ" and x.status == "added" for x in pop.resolved)
    ch = SecureChecker.from_population({}, pop)
    m = ch.match("pie-lex-gwih3wos", "cu", "Old Church Slavonic", "животъ", True)
    assert m["level"] == "exact" and m["via"].startswith("table:")
    assert any(ids == {"pie-lex-gwih3wos"} and src == "table:cu" for ids, _, src, _ in
               ch.table("cu")[row_keys("cu", {"lemma": "животъ"}).pop()])
    # Hittite decisions too (east.json): every lemma an override maps is in the resolved population, as an
    # added row while hit.jsonl predates the override, as a confirmed/remapped one once the table is rebuilt
    # (`formula_search.py mapping --corpus hit` writes the decided rows as how 'erratum')
    hit = {x.lemma: x for x in load_population(codes={"hit"}).resolved}
    decided = {l for l, (ids, _) in fm.load_overrides(ROOT)["lemma"]["hit"].items() if ids}
    assert len(decided) >= 100 and decided <= set(hit)
    assert all(hit[l].decisions for l in decided)


def test_audit_population_is_the_checker_population():
    pop = load_population()
    ch = SecureChecker.from_population({}, pop)
    by_checker = collections.defaultdict(dict)
    for x in pop.resolved:
        by_checker[x.corpus][x.lemma] = x.ids
    for corpus in mp.table_corpora(ROOT):
        raw = mp.read_table(corpus, ROOT)
        res = mp.resolve_table(corpus, ROOT)
        audit = {k: frozenset(v) for k, v in fm.apply_table_overrides(
            corpus, {r["lemma"]: tuple(r["lex_id"]) for r in raw}, root=ROOT).items()}
        assert audit == {x.lemma: x.ids for x in res.values()}, corpus
        # the checker reads the rows of the languages it checks (Lith., Russian, Welsh tables: none)
        read = {x.lemma: x.ids for x in res.values() if code_of(corpus, x.lang)}
        assert read == by_checker.get(corpus, {}), corpus
        rows = {r["lemma"]: r for r in raw}
        for x in res.values():
            code = code_of(corpus, x.lang)
            if x.uncertain or code is None:
                continue
            for k in row_keys(code, {"lemma": x.lemma, "word": rows.get(x.lemma, {}).get("word", x.word)}):
                assert any(ids == x.ids for ids, *_ in ch.table(code)[k]), (corpus, x.lemma, k)
    # the corpora whose mapping is built live (rv, hom, lat) enter through their decided lemmas
    assert {"rv", "hom", "lat"} <= {x.corpus for x in pop.resolved}
    assert {x.corpus for x in pop.resolved} == {x.corpus for x in mp.iter_resolved(ROOT)
                                               if code_of(x.corpus, x.lang)}


# ---------------------------------------------------------------- every route, on a fixture

FIX = {
    "pie-root-bhew-be": {"id": "pie-root-bhew-be", "kind": "root", "form": "bʰewH-"},
    "pie-lex-bhuHt": {"id": "pie-lex-bhuHt", "form": "bʰúHt", "root_id": "pie-root-bhew-be",
                      "reflexes": {"Sanskrit": [{"form": "भू", "roman": "bhū́"}]}},
    "pie-lex-bhewHti": {"id": "pie-lex-bhewHti", "form": "bʰewHti", "root_id": "pie-root-bhew-be",
                        "reflexes": {"Sanskrit": [{"form": "भवति", "roman": "bhū́"}]}},
    "pie-lex-sunus": {"id": "pie-lex-sunus", "form": "suHnús", "reflexes": {"Sanskrit": [{"roman": "sūnú"}]}},
    "pie-root-sew-bear": {"id": "pie-root-sew-bear", "kind": "root", "form": "sewH-"},
    "pie-lex-suHyus": {"id": "pie-lex-suHyus", "form": "suHyús", "root_id": "pie-root-sew-bear",
                       "reflexes": {"Sanskrit": [{"roman": "sūyú"}]}},
}


def fix_checker(overrides, rows=None, kaikki=None, forms=None):
    rows = rows if rows is not None else {"av": [{"corpus": "av", "lang": "sa", "lemma": "bhū", "word": "bhū́",
                                                  "lex_id": ["pie-lex-bhuHt"], "path": ["sa:bhū"], "how": "chain"}]}
    pop = build_population(rows, overrides, codes={"sa"})
    if forms:
        pop.forms["sa"] = forms
    others = ({"sa": kaikki or {}},)
    return SecureChecker.from_population(FIX, pop, lambda: others)


REMOVE = {"av": {"bhū": (frozenset(), {"erratum": "bhū 'earth' mapped to *bʰuHt"})}}


def test_removal_blocks_every_route():
    kaikki = {"bhū": [rec({"pie-lex-bhuHt"}, "bhū́", "sa", "kaikki-sa")],
              "bhūmi": [rec({"pie-lex-bhuHt"}, "bhū́mi", "sa", "kaikki-sa")]}
    free = fix_checker({}, kaikki=kaikki)
    assert free.match("pie-lex-bhuHt", "sa", "Vedic", "bhū́", True)["level"] == "exact"
    ch = fix_checker(REMOVE, kaikki=kaikki, forms={"bhuvam": "bhū"})
    for lid in ("pie-lex-bhuHt", "pie-lex-bhewHti", "pie-root-bhew-be"):
        assert ch.match(lid, "sa", "Vedic", "bhū́", True) is None, lid          # table, kaikki, reflex, sibling
        assert ch.match(lid, "sa", "Vedic", "prabhū", False) is None, lid      # preverb + reflex
        assert ch.match(lid, "sa", "Vedic", "bhuvam", False) is None, lid      # reviewed form row → lemma
    ref = {"lang": "Vedic", "lemmas": ["bhū́-"], "words": ["bhū́ḥ"]}
    assert ch.check("pie-lex-bhuHt", [ref])["exact_branches"] == []          # inflected word, cited lemma
    # the kaikki link of another word is not touched
    assert ch.match("pie-lex-bhuHt", "sa", "Vedic", "bhū́mi", True)["level"] == "exact"
    # the kaikki link stays in the table (another sense could use it) but is capped by the decision
    assert any("pie-lex-bhuHt" in ids for ids, *_ in ch.table("sa").get("bhū", []))


def test_remap_to_a_root_keeps_its_lexemes_but_not_what_it_removed():
    rows = {"av": [{"corpus": "av", "lang": "sa", "lemma": "sūyu", "word": "sūyú-", "lex_id": ["pie-lex-sunus"],
                    "path": ["sa:sūyu"], "how": "chain"}]}
    ov = {"av": {"sūyu": (frozenset({"pie-root-sew-bear"}), {"note": "a different formation of *sewH-"})}}
    ch = fix_checker(ov, rows=rows)
    # the removed *suHnús stays out, whatever the reflex lists say; a lexeme under the decided root may be exact
    assert ch.match("pie-lex-sunus", "sa", "Vedic", "sūyú-", True) is None
    assert ch.match("pie-root-sew-bear", "sa", "Vedic", "sūyú-", True)["level"] == "exact"
    assert ch.match("pie-lex-suHyus", "sa", "Vedic", "sūyú-", True)["level"] == "exact"


def test_derivative_and_uncertain_rows():
    ov = {"av": {"bhū": (frozenset({"pie-lex-bhuHt"}), {"note": "x", "formation": "derivative"})}}
    m = fix_checker(ov).match("pie-lex-bhuHt", "sa", "Vedic", "bhū́", True)
    assert m["level"] == "root"                          # the reflex list does not make a derivative exact
    ov = {"av": {"bhū": (frozenset({"pie-lex-bhuHt"}), {"note": "x", "uncertain": True})}}
    assert fix_checker(ov).match("pie-lex-bhuHt", "sa", "Vedic", "bhū́", True) is None
    x = mp.resolve_rows("av", [{"lemma": "bhū", "lex_id": ["pie-lex-bhuHt"]}], ov)["bhū"]
    assert x.uncertain and x.confidence == "low" and x.ids == {"pie-lex-bhuHt"}   # kept for formula search
    assert fm.apply_table_overrides("av", {"bhū": ("pie-lex-bhuHt",)}, overrides=ov) == {"bhū": ("pie-lex-bhuHt",)}


def test_tain_is_root_evidence_and_other_celtic_rows_are_unchanged():
    """ENG-03: the reviewed nominal derivative cannot attest the thematic present."""
    from pie.realize import Lexicon

    lid = "pie-lex-h2egjeti"
    ov = mp.load_overrides(ROOT)
    without = {**ov, "decisions": {**ov["decisions"], "celt": {
        k: v for k, v in ov["decisions"]["celt"].items() if k != "táin"}}}
    rows = mp.read_table("celt", ROOT)
    resolved = mp.resolve_rows("celt", rows, ov)
    baseline = mp.resolve_rows("celt", rows, without)
    assert resolved["táin"].ids == {lid}
    assert resolved["táin"].derivative
    # Rebuilt override rows carry the corpus label as lang; they must still
    # govern Irish evidence, including the separate glosses table.
    assert code_of("celt", "celt") == "sga"
    assert {k: v for k, v in resolved.items() if k != "táin"} == {
        k: v for k, v in baseline.items() if k != "táin"}

    entries = Lexicon.load().entries
    ch = SecureChecker.from_disk(entries)
    plan = json.loads((ROOT / "data/tier2/plans/cattle-raid.jsonl").read_text().splitlines()[0])
    verb = ch.check(lid, plan["cognate_refs"])
    assert verb["exact_branches"] == ["II", "It"]
    assert verb["root_branches"] == ["Ce"]
    assert verb["level"] == "exact"
    assert ch.check("pie-lex-gwoxws", plan["cognate_refs"])["exact_branches"] == ["Ce", "II", "It"]
    # The ambiguous táin|doaig table route must not downgrade the verb doaig.
    assert ch.match(lid, "sga", "Old Irish", "doaig", True)["level"] == "exact"

    # Even a competing dictionary route and a direct lexicon reflex cannot
    # restore exact evidence against the shipped lemma decision.
    entries = {**entries, lid: {**entries[lid], "reflexes": {"Old Irish": [{"form": "táin"}]}}}
    pop = load_population(codes={"sga"})
    alternative = {"táin": [rec({lid}, "táin", "sga", "alternative")]}
    guarded = SecureChecker.from_population(entries, pop, others_loader=lambda: ({"sga": alternative},))
    for lemma in (True, False):
        assert guarded.match(lid, "sga", "Old Irish", "táin", lemma)["level"] == "root"


def test_every_override_file_and_key_is_loaded():
    # every row of every file under mapping-overrides/ (and the shared file) reaches the one resolver
    ov = fm.load_overrides(ROOT)
    files = mp.override_files(ROOT)
    assert {f.name for f in files} >= {"mapping-overrides.json", "east.json", "greek.json", "sanskrit.json"}
    n = collections.Counter()
    for f in files:
        d = json.loads(f.read_text("utf-8"))
        assert set(d) <= mp.FILE_KEYS, (f.name, set(d) - mp.FILE_KEYS)
        for kind in ("lemma", "form", "proto", "key"):
            n[kind] += len(d.get(kind, []))
            for r in d.get(kind, []):
                if kind == "lemma":
                    assert r["lemma"] in ov["decisions"][r["corpus"]], (f.name, r)
                elif kind == "form":
                    assert mp._keyer(r["lang"])(r["form"]) in ov["form"][r["lang"]], (f.name, r)
                elif kind == "proto":
                    assert (r["code"], mp.proto_key(r["term"])) in ov["proto"], (f.name, r)
                else:
                    # cq2: headword_key, never "" (an Avestan-script key row keyed to "" matched every path)
                    assert mp.headword_key(r["lang"], r["key"]) in ov["key"][r["lang"]], (f.name, r)
    assert n["lemma"] and n["form"]


def test_unknown_override_key_is_an_error(tmp_path):
    import pytest
    d = tmp_path / "data" / "research" / "formulas" / "mapping-overrides"
    d.mkdir(parents=True)
    (d / "x.json").write_text('{"lemma": [], "stems": []}', "utf-8")
    with pytest.raises(ValueError, match="stems"):
        mp.load_overrides(tmp_path)


def test_proto_rows_decide_every_word_through_the_page():
    # germanic-new.json: gem-pro *hugiz has no certain etymology: every table word mapped through it is unmapped
    ov = fm.load_overrides(ROOT)
    d = ov["proto"].get(("gem-pro", mp.proto_key("*hugiz")))
    if d is None:
        return
    assert d.removal
    rows = [{"lemma": "hyge", "lang": "ang", "lex_id": ["pie-root-kewk-cry_out"],
             "path": ["ang:hyge", "gem-pro:*hugiz", "ine-pro:*kewk-"]}]
    assert mp.resolve_rows("zz", rows, ov) == {}
    assert fm.apply_rec_overrides("zz", {"hyge": fm.MapRec("hyge", "hyge", frozenset({"x"}), tuple(rows[0]["path"]),
                                                            "chain", "high", ())}) == {}


def test_decisions_and_senses():
    d = mp.decision({"corpus": "lv", "lemma": "pūrs", "lex_id": [], "erratum": "pūrs 'dowry chest' mapped to x"})
    assert d.removal and d.sense == "dowry chest"
    assert mp.decision({"lemma": "a", "lex_id": ["x"], "erratum": "remapped to x"}).sense is None
    assert mp.senses_overlap("dowry chest", "chest") and not mp.senses_overlap("dowry chest", "fire")
    assert mp.senses_overlap(None, "fire")
    # several senses of one lemma: a lemma-keyed table gets their union, a sense query only its own
    rows = [{"corpus": "x", "lemma": "w", "lex_id": ["a"], "sense": "fire"},
            {"corpus": "x", "lemma": "w", "lex_id": [], "sense": "dowry chest"}]
    dec = {"x": {"w": [mp.decision(r) for r in rows]}}
    ov = mp._pack(dec, {})
    assert mp.decide("x", "w", ("b",), ov)[0] == {"a"}
    assert mp.decide("x", "w", ("b",), ov, sense="dowry")[0] == frozenset()
    assert mp.decide("x", "v", ("b", "pie-lex-sh1es"), ov)[0] == {"b"}      # no decision: automatic, BLOCKED_IDS out


def test_lemmatizer_group_decision_is_about_its_row_only():
    # ang 'gēar|gear' (an OCR form read as gēar or gearo) is unmapped as a group; gēar 'year' itself is not
    assert fm.load_overrides(ROOT)["lemma"]["ang"]["gēar|gear"][0] == frozenset()
    pop = load_population(codes={"ang"})
    ch = SecureChecker.from_population({}, pop)
    assert ch.governing("ang", "gēar", True) is None and ch.governing("ang", "gear", True) is None


def test_root_choice_between_homograph_roots_keeps_the_lexeme_exact():
    # Ved. bhā: the decision keeps the root 'shine' and drops 'speak'; the 'shine' verb stays exact
    ent = {"pie-root-bheh2-shine": {"id": "pie-root-bheh2-shine", "kind": "root"},
           "pie-root-bheh2-speak": {"id": "pie-root-bheh2-speak", "kind": "root"},
           "pie-lex-shine": {"id": "pie-lex-shine", "root_id": "pie-root-bheh2-shine",
                             "reflexes": {"Sanskrit": [{"roman": "bhā"}]}},
           "pie-lex-speak": {"id": "pie-lex-speak", "root_id": "pie-root-bheh2-speak",
                             "reflexes": {"Sanskrit": [{"roman": "bhā"}]}}}
    rows = {"av": [{"lemma": "bhā", "lang": "sa", "lex_id": ["pie-lex-shine", "pie-lex-speak"], "path": ["sa:bhā"]}]}
    ov = {"av": {"bhā": (frozenset({"pie-root-bheh2-shine"}), {"erratum": "bhā 'shine' also mapped to 'speak'"})}}
    ch = SecureChecker.from_population(ent, build_population(rows, ov, codes={"sa"}))
    assert ch.match("pie-lex-shine", "sa", "Vedic", "bhā", True)["level"] == "exact"
    assert ch.match("pie-lex-speak", "sa", "Vedic", "bhā", True) is None


def test_accent_homographs_and_remainders_are_not_decided_by_another_lemma():
    ent = {"pie-lex-raw": {"id": "pie-lex-raw", "reflexes": {"Ancient Greek": [{"form": "ὠμός"}]}},
           "pie-lex-shoulder": {"id": "pie-lex-shoulder"},
           "pie-lex-slain": {"id": "pie-lex-slain", "reflexes": {"Ancient Greek": [{"form": "φατός"}]}}}
    rows = {"grp": [{"lemma": "ὦμος", "lang": "grc", "lex_id": ["pie-lex-raw"], "path": ["grc:ὦμος"]},
                    {"lemma": "φάτις", "lang": "grc", "lex_id": ["pie-lex-slain"], "path": ["grc:φάτις"]}]}
    ov = {"grp": {"ὦμος": (frozenset({"pie-lex-shoulder"}), {"erratum": "ὦμος 'shoulder' mapped to 'raw'"}),
                  "φάτις": (frozenset(), {"erratum": "φάτις 'speech' mapped to 'slain'"})}}
    ch = SecureChecker.from_population(ent, build_population(rows, ov, codes={"grc"}))
    assert ch.match("pie-lex-raw", "grc", "Greek", "ὦμος", True) is None
    assert ch.match("pie-lex-shoulder", "grc", "Greek", "ὦμος", True)["level"] == "exact"
    assert ch.match("pie-lex-raw", "grc", "Greek", "ὠμός", True)["level"] == "exact"     # same key ωμοσ
    m = ch.match("pie-lex-slain", "grc", "Greek", "πρόσφατος", False)                     # -φατος, not φάτις
    assert m["level"] == "exact" and m["path"][0] == "preverb:pros"


# ---------------------------------------------------------------- independent Germanic / Balto-Slavic check (seed 41)

def test_kannijana_proto_row_reaches_old_saxon_kennian():
    # germanic-new.json: gem-pro *kannijaną < *ǵneh₃- only; OS kennian kept the *ǵenh₁- id from the lexicon
    # reflex list, past the proto row
    raw = next(r for r in mp.read_table("rea-osx", ROOT) if r["lemma"] == "kennian")
    assert "pie-lex-gjonh1eyeti" in raw["lex_id"]
    res = mp.resolve_table("rea-osx", ROOT)
    for lem in ("kennian", "ankennian", "antkennian"):
        assert res[lem].ids == {"pie-lex-gjnneh3ti"}, lem
    table = {r["lemma"]: tuple(r["lex_id"]) for r in mp.read_table("rea-osx", ROOT)}
    assert fm.apply_table_overrides("rea-osx", table, root=ROOT)["kennian"] == ("pie-lex-gjnneh3ti",)


FARA = {"pie-root-per-go_through": {"id": "pie-root-per-go_through", "kind": "root"},
        "pie-lex-piporti": {"id": "pie-lex-piporti", "root_id": "pie-root-per-go_through",
                            "reflexes": {"Old Norse": [{"form": "fara"}]}}}


def test_a_proto_row_decides_every_route_through_the_page():
    # ON fara / OHG faran reach *píporti through the lexicon reflex link of gem-pro *faraną (Kroonen p0168:
    # *por-e-, píparti only a cognate). A proto row for the page decides the tables and blocks the
    # checker's reflex route for the words mapped through it. This fixture isolates the mechanism;
    # the production-data regression below also covers regeneration and the shipped formation cap.
    rows = {"menota": [{"lemma": "fara", "lang": "non", "lex_id": ["pie-lex-piporti"],
                        "path": ["non:fara", "gem-pro:*faraną", "lexicon-reflex"]},
                       {"lemma": "misfara", "lang": "non", "lex_id": ["pie-lex-piporti"],
                        "path": ["non:misfara", "prefix:mis-", "non:fara", "gem-pro:*faraną", "lexicon-reflex"]}]}
    ov = mp.as_overrides({})
    ov = {**ov, "proto": {("gem-pro", mp.proto_key("*faraną")):
                          mp.decision({"lex_id": ["pie-root-per-go_through"], "note": "Kroonen p0168: *por-e-"},
                                      "gem-pro", "*faraną")}}
    res = mp.resolve_rows("menota", rows["menota"], ov)
    assert res["fara"].ids == res["misfara"].ids == {"pie-root-per-go_through"}
    free = SecureChecker.from_population(FARA, build_population(rows, {}, codes={"non"}))
    assert free.match("pie-lex-piporti", "non", "Old Norse", "fara", True)["level"] == "exact"
    ch = SecureChecker.from_population(FARA, build_population(rows, ov, codes={"non"}))
    # *píporti was removed in favour of its root: only root level, the reflex list cannot restore exact
    assert ch.match("pie-lex-piporti", "non", "Old Norse", "fara", True)["level"] == "root"
    assert ch.match("pie-root-per-go_through", "non", "Old Norse", "fara", True)["level"] == "exact"


def test_shipped_farana_decision_reaches_tables_and_secure_checker():
    corpora = {"menota": "fara", "icepahc": "fara", "rea-goh": "faran", "rea-osx": "faran"}
    rows = {c: mp.read_table(c, ROOT) for c in corpora}
    languages = {"menota": "Old Norse", "icepahc": "Old Norse",
                 "rea-goh": "Old High German", "rea-osx": "Old Saxon"}
    ov = mp.load_overrides(ROOT)
    assert ov["proto"][("gem-pro", mp.proto_key("*faraną"))].ids == {"pie-root-per-go_through"}
    entries = {r["id"]: r for r in fm.fs.load_jsonl(ROOT / "data/lexicon/lexicon.jsonl")}
    checker = SecureChecker.from_population(entries, build_population(rows, ov))
    for corpus, lemma in corpora.items():
        resolved = mp.resolve_table(corpus, ROOT)
        assert resolved[lemma].ids == {"pie-root-per-go_through"}
        covered = [r for r in rows[corpus] if "gem-pro:*faraną" in r["path"]]
        assert any(r["lemma"] != lemma for r in covered)  # prefixed/inflected descendants
        for row in covered:
            assert row["lex_id"] == ["pie-root-per-go_through"], (corpus, row["lemma"])
            assert resolved[row["lemma"]].ids == {"pie-root-per-go_through"}
            assert resolved[row["lemma"]].derivative
            code = code_of(corpus, row["lang"])
            # The secure checker currently consumes non, but not is/goh/osx.
            # All four tables still carry the same root-only formation decision.
            if code is None:
                continue
            match = checker.match("pie-lex-piporti", code, languages[corpus], row["lemma"], True)
            assert match is not None and match["level"] == "root", (corpus, row["lemma"], match)
            assert checker.match("pie-root-per-go_through", code, languages[corpus],
                                 row["lemma"], True) is not None
    # The legitimate PIE lexeme remains available outside this Germanic formation.
    assert "pie-lex-piporti" in fm._strip_blocked({"pie-lex-piporti"})


def test_shipped_podici_key_removes_fallback_but_preserves_go_verbs():
    ov = mp.load_overrides(ROOT)
    assert ov["key"]["sh"][mp._keyer("sh")("podići")].removal
    rows = {r["lemma"]: r for r in mp.read_table("vuk", ROOT)}
    resolved = mp.resolve_table("vuk", ROOT)
    assert "podići" not in rows
    assert "podići" not in resolved
    for lemma in ("ići", "doći", "otići"):
        assert rows[lemma]["lex_id"] == ["pie-lex-h1eyti"]
        assert resolved[lemma].ids == {"pie-lex-h1eyti"}
    # Also govern the formerly selected path, which omitted the rejected proto page.
    old = {"lemma": "podići", "lang": "sh", "lex_id": ["pie-lex-h1eyti"],
           "path": ["sh:podići", "base:ići", "sh:ići", "ine-pro:*h₁éyti"]}
    # resolve_rows also adds independent reviewed lemmas (e.g. mrkli).
    assert "podići" not in mp.resolve_rows("vuk", [old], ov)
