"""The translator app's engine (pie/translator): readable glosses, the inverse form index, the translation memory, and
the rule-based transfer (needs the `translator` dependency group: spaCy; skipped without it)."""
import json
from pathlib import Path

import pytest

from pie.translator.gloss import readable

ROOT = Path(__file__).resolve().parents[1]


def test_readable_gloss_names_closed_class_words():
    assert readable("personal/1-GEN.SG.ENCL ph₂ter-NOM.SG") == "my-GEN.SG.ENCL ph₂ter-NOM.SG"
    assert readable("demonstrative_so-ACC.PL personal/2-NOM.SG grow-AOR.3SG=and") == \
        "those-ACC.PL you-NOM.SG grow-AOR.3SG=and"
    assert readable("numerals/indeclinable/10 interrogative_adv/where anaphoric_i-NOM.PL") == "ten where? they-NOM.PL"
    assert readable(None) is None


@pytest.fixture(scope="module")
def analyzer():
    from pie.translator.analyze import Analyzer
    return Analyzer.load()


def test_analyzer_knows_the_corpus_forms(analyzer):
    """Nearly every engine-built token of the Tier 3 corpus is in the inverse index with its own lexeme."""
    toks = []
    for f in sorted((ROOT / "corpus/tier3").glob("t0*.jsonl"))[:6]:
        for line in f.read_text("utf-8").splitlines():
            toks += [t for t in json.loads(line)["tokens"] if t.get("lex_id") and not t["form"].startswith("-")]
    hit = sum(any(a.lex_id == t["lex_id"] for a in analyzer.word(t["form"])[0]) for t in toks)
    assert hit / len(toks) > 0.95, hit / len(toks)


def test_analyzer_splits_enclitics(analyzer):
    w = analyzer.analyze("h₁éḱwōs-kʷe")[0]
    assert w["clitic"] == ("kʷe", "and") and any(a.lex_id == "pie-lex-h1ekjwos" for a in w["analyses"])


def test_memory_returns_the_corpus_sentence():
    from pie.translator.memory import Memory
    m = Memory.load()
    p = m.pairs[len(m.pairs) // 2]
    score, hit = m.search(p.english, k=1)[0]
    assert score == 1.0 and hit.english.lower().strip(".!? ") == p.english.lower().strip(".!? ")


@pytest.fixture(scope="module")
def transfer():
    pytest.importorskip("spacy")
    from pie.translator.transfer import Transfer
    return Transfer()


@pytest.mark.parametrize("english,pie", [
    ("The wolf saw the sheep.", "wĺ̥kʷos h₂ówim widét."),
    ("Where is my father?", "kúdʰe moy ph₂tḗr h₁ésti?"),
    ("Do not fear the wolf!", "wĺ̥kʷom mē pr̥ksḱés."),
    ("Let us drive the cattle home.", "gʷṓs dṓm h₂éǵōmes."),
    ("Give me water!", "méǵʰye wódr̥ dh₃dʰí."),
])
def test_transfer_builds_the_plan(transfer, english, pie):
    r = transfer.translate(english)
    assert r.pie == pie and not r.errors


def test_transfer_reports_what_it_cannot_say(transfer):
    r = transfer.translate("The tiger ate the bread.")
    assert set(r.unknown) >= {"tiger"}
