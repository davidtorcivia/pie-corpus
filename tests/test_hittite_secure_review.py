"""Production-path regressions for the 2026-10-25 secure-evidence adjudication."""
import json
from pathlib import Path

import pytest

from pie.realize import Lexicon
from pie.tier2_secure import (
    SECURE_HITTITE_UNCERTAINTY, SecureChecker, decision_keys, load_population,
)

ROOT = Path(__file__).resolve().parents[1]


def ref(lemmas=(), words=()):
    return {"lang": "Hittite", "role": "parallel", "lemmas": list(lemmas), "words": list(words)}


@pytest.fixture(scope="module")
def production():
    return SecureChecker.from_disk(Lexicon.load().entries)


@pytest.mark.parametrize("lemma,word,lid", [
    ("ištamašš=@hören", "ištamašš-", "pie-lex-steh3mn"),
    ("taganzip=a-@Erde", "taganzipa-", "pie-lex-dhegjhoxm"),
])
def test_derivative_production_and_competing_routes(production, lemma, word, lid):
    for citation in (ref([lemma]), ref([word]), ref([word], [word + "n"]), ref(words=[word])):
        result = production.check(lid, [citation])
        assert result["exact_branches"] == []
        assert result["root_branches"] == ["An"]
    # Give every automatic source an exact route, including a direct reflex.
    # The real reviewed override must still govern them and compound remainders.
    entries = {**production.entries, lid: {**production.entries[lid],
               "reflexes": {"Hittite": [{"form": word}]}}}
    sources = [{"hit": {k: [(frozenset({lid}), (source,), source, False)]
                        for k in decision_keys("hit", lemma, word)}}
               for source in ("kaikki:hit", "dict:hit", "table:hit")]
    checker = SecureChecker.from_population(entries, load_population(codes={"hit"}), lambda: sources)
    assert checker.check(lid, [ref([word], [word + "n"])])["root_branches"] == ["An"]
    assert checker.match(lid, "hit", "Hittite", word, True)["level"] == "root"
    for k in decision_keys("hit", lemma, word):
        result = checker._match_key(lid, "hit", "Hittite", k, word)
        assert result is None or result["level"] == "root"


def test_all_eight_doubtful_equations_have_explicit_secure_decisions():
    rows = [json.loads(s) for s in (ROOT / "data/research/formulas/mapping/hit-doubtful.jsonl").read_text().splitlines()]
    assert {r["lemma"]: r["lex_id"] for r in rows} == {
        lemma: [lid] for lemma, _, lid, _ in SECURE_HITTITE_UNCERTAINTY}
    # Retrieval remains separate; the secure population does not import doubtful rows.
    assert not any(x.how == "kloekhorst-doubtful" for x in load_population(codes={"hit"}).resolved)


@pytest.mark.parametrize("lemma,word,lid,pages", SECURE_HITTITE_UNCERTAINTY)
def test_doubtful_caps_all_routes_and_family(production, lemma, word, lid, pages):
    forms = [lemma.split("@")[0], *(word.split(" ~ ") if word else [])]
    family = {lid, production.entries.get(lid, {}).get("root_id")} - {None}
    family |= {i for i, e in production.entries.items() if e.get("root_id") in family}
    for target in family:
        assert production.check(target, [ref(forms, forms)])["evidence"] == {}
    # Inject exact table, dictionary and reflex evidence for the doubtful target.
    # Include an unrelated equation at the same keys: the cap must be targeted.
    other = "test-independent-hittite-equation"
    entries = {**production.entries,
               lid: {**production.entries[lid], "reflexes": {"Hittite": [{"form": f} for f in forms]}},
               other: {"id": other, "reflexes": {"Hittite": [{"form": forms[0]}]}}}
    keys = decision_keys("hit", lemma, word)
    sources = [{"hit": {k: [(frozenset({lid, other}), (source,), source, False)] for k in keys}}
               for source in ("table:hit", "kaikki:hit", "dict:hit")]
    checker = SecureChecker.from_population(entries, load_population(codes={"hit"}), lambda: sources)
    for f in forms:
        for citation in (ref([f]), ref(words=[f]), ref([f], [f + "an"])):
            assert checker.check(lid, [citation])["evidence"] == {}
    for k in keys:
        assert checker._match_key(lid, "hit", "Hittite", k, forms[0]) is None
    assert checker.check(other, [ref([forms[0]])])["exact_branches"] == ["An"]


def test_known_reflex_bypasses_blocked_but_independent_pouring_preserved(production):
    for lid, word in (("pie-lex-h3rewnos", "aruna-"), ("pie-lex-sh2ewti", "šuḫḫa-i")):
        # The stored reflex survives; without reviewed policy it still supplies exact evidence.
        baseline = SecureChecker(production.entries)
        assert baseline.check(lid, [ref([word])])["exact_branches"] == ["An"]
        assert production.check(lid, [ref([word])])["evidence"] == {}
    assert production.check("pie-root-sh2ew-pour", [ref(["išḫuwai-"])])["exact_branches"] == ["An"]
