"""scripts/lexq.py, the planners' lexicon query beside the slice: same pool and entry format as make_slice."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("lexq", ROOT / "scripts" / "lexq.py")
lexq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lexq)


def test_finds_words_planners_wrote_around():
    from pie.realize import Lexicon
    lx = Lexicon.load()
    ids, uses = lexq.pool(lx, False), lexq.corpus_uses()
    first = lambda t: lexq.search(t, lx, ids, uses, 3)[0]["lex_id"]
    assert first("wolf") == "pie-lex-wlkwos"
    assert first("one") == "pie-lex-h1oynos"             # t059: 'one who begets/cooks/knows' outranked the numeral
    assert first("story") == "pie-proj-spelom"            # a project reconstruction, flagged coined: project
    assert first("fear") in {"pie-lex-bhebhoyh2e", "pie-lex-treseti", "pie-lex-tromeyeti", "pie-lex-prkskjeti"}
    with_ = [h["lex_id"] for h in lexq.search("with", lx, ids, uses, 3)]
    assert "pie-lex-kjom" in with_ and all(h.startswith(("pie-lex-kjom", "pie-lex-me", "closed:")) or
                                           lexq.ms.slice_item(lx, h)["family"] not in ("noun", "verb", "adj")
                                           for h in with_ if h in lx.specs)
    assert not any(lx.coined(i) == "neologism" for i in ids)      # Tier 3 never sees a coinage


def test_idioms_answer_concepts_without_a_word():
    """Round 3 (docs/audits/lexicon-gaps-round3-2026-10-31.md): a concept with no single word gets its idiom from
    data/lexicon/idioms.json on every query, and Tier 3 sees no coinage id in it."""
    import json
    from pie.realize import Lexicon
    lx = Lexicon.load()
    ids, uses = lexq.pool(lx, False), lexq.corpus_uses()
    assert not lexq.search("tomorrow", lx, ids, uses, 3)              # no lexeme: the idiom is the answer
    tomorrow = lexq.idioms("tomorrow")
    assert tomorrow and "pie-lex-h2eyeri" in tomorrow[0]["ids"]
    assert lexq.idioms("answer")[0]["ids"] == ["pie-lex-proti", "pie-lex-mlewHti"]
    assert any("pie-lex-gwoxws" in e["ids"] for e in lexq.idioms("cow"))
    assert lexq.idioms("for three days") and lexq.idioms("yes") and lexq.idioms("because")
    assert "tier3b_ids" not in lexq.idioms("bread")[0] and lexq.idioms("bread", tier3b=True)[0]["tier3b_ids"]
    entries = json.loads(lexq.IDIOMS.read_text("utf-8"))["idioms"]
    closed = {c for c in lexq.closed_adverb_ids(lx)}
    for e in entries:
        assert e["kind"] in ("idiom", "paraphrase") and e["english"] and e["source"]
        for i in e["ids"]:
            assert lx.coined(i) != "neologism", (e["english"], i)       # Tier 3 never sees a coinage
            assert i in lx.entries or i.startswith("closed:") or i in closed, (e["english"], i)
        for i in e.get("tier3b_ids", []):
            assert i.startswith("pie-neo-"), (e["english"], i)


def test_round3_words_are_found():
    """Round-3 gloss fixes: the planners' concepts now find an offered lexeme first."""
    from pie.realize import Lexicon
    lx = Lexicon.load()
    ids, uses = lexq.pool(lx, False), lexq.corpus_uses()
    first = lambda t: lexq.search(t, lx, ids, uses, 3)[0]["lex_id"]
    for term, want in [("booty", "pie-lex-Hrowpos"), ("shield", "pie-lex-skeytos"), ("victory", "pie-lex-segjhos-2"),
                       ("weep", "pie-lex-HrewdHti"), ("summer", "pie-lex-semeh2"), ("obey", "pie-lex-kjlowseyeti"),
                       ("debt", "pie-lex-dhlghos"), ("plague", "pie-lex-moro"), ("mother-in-law", "pie-lex-swekjruh2"),
                       ("bride", "pie-lex-snusos"), ("kick", "pie-lex-sprneHti"), ("brave", "pie-lex-dhrsus")]:
        assert first(term) == want, term
