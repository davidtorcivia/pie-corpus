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
