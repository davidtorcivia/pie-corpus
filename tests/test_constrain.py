"""Engine-constrained decoding (pie.translator.constrain): the grammar accepts what score.notation_ok accepts, and
the processor picks the model's best candidate that keeps every PIE word a known form."""
import sys
from pathlib import Path

import pytest

from pie.translator.constrain import Constraint, Grammar

ROOT = Path(__file__).resolve().parents[1]
FORMS = ["h₁éḱwos", "h₁éḱwōs", "h₂ówis", "kʷe", "wéydeti", "tód", "só"]


class CharTok:
    """One token per character; id 0 is EOS."""

    def __init__(self, alphabet):
        self.chars = ["<eos>"] + sorted(set(alphabet))
        self.eos_token_ids = {0}

    def ids(self, s):
        return [self.chars.index(c) for c in s]

    def decode(self, ids):
        return "".join(self.chars[i] for i in ids if i)


@pytest.fixture(scope="module")
def g():
    return Grammar(FORMS)


def test_words_and_prefixes(g):
    assert g.word("h₁éḱwos") and g.word("h₁eḱwos")          # an accent left out is notation_ok's leniency
    assert not g.word("ekwos") and not g.word("h₁éḱw")
    assert g.prefix("h₁éḱ") and g.prefix("") and not g.prefix("ek")


def test_tokens(g):
    assert g.token("h₂ówis,", False)                        # trailing punctuation closes the word
    assert not g.token("h₂ówi,", False)
    assert g.token("h₁éḱwōs-kʷe", True) and g.token("h₁éḱwōs-k", False)
    assert not g.token("h₁éḱwōs-k", True)
    assert not g.token("bʰ(y)os", False)                    # punctuation inside a word
    assert g.token('"tód', False) and g.token("(só)", True)


def test_lines(g):
    assert g.text("PIE: h₂ówis wéydeti h₁éḱwons\nGloss: anything at all", complete=False) is False   # unknown form
    assert g.text("PIE: h₂ówis wéydeti h₁éḱwos.\nGloss: sheep-NOM.SG see-PRS.3SG", complete=True)
    assert g.text("Engl", complete=False)                    # may still become a label
    assert g.text("h₂ówis wéydeti\nEnglish: The sheep sees.", complete=True)
    assert not g.text("the sheep", complete=False)


def test_processor_picks_best_valid(g):
    tok = CharTok("".join(FORMS) + " .-\nxa")
    c = Constraint(tok, g, prompt_len=0, topk=len(tok.chars))
    gen = tok.ids("h₂ówis wéyd")
    prev = tok.decode(gen)
    order = tok.ids("xae")                                   # the model prefers x, then a, then e
    assert c.choose(gen, order) == tok.ids("e")[0]
    gen = tok.ids("h₂ówi")
    assert c.choose(gen, [0] + tok.ids("s")) == tok.ids("s")[0]   # no EOS inside a word
    gen = tok.ids("h₂ówis")
    assert c.choose(gen, [0]) == 0                           # EOS after a whole word
    assert c._ok(gen, prev, 0) is False                      # but not after "wéyd"


def test_one_bad_word_does_not_free_the_rest(g):
    """A word written when the grammar gave way stays; the next words are constrained again, and the answer may end
    after a whole word."""
    tok = CharTok("".join(FORMS) + " .-\nxa")
    c = Constraint(tok, g, prompt_len=0, topk=len(tok.chars))
    gen = tok.ids("h₂ówis xa wéyd")                         # "xa" is no form
    assert c.choose(gen, tok.ids("xae")) == tok.ids("e")[0]
    gen = tok.ids("h₂ówis xa h₂ówi")
    assert c.choose(gen, [0] + tok.ids("s")) == tok.ids("s")[0]   # still no EOS inside a word
    assert c.choose(tok.ids("h₂ówis xa h₂ówis"), [0]) == 0


def test_real_grammar_agrees_with_notation_ok():
    sys.path.insert(0, str(ROOT / "benchmarks"))
    import score
    g = Grammar.load()
    for s in ["h₂ówis h₁éḱwōs-kʷe wéydeti.", "tód ḱeḱluwṓs h₂ówis h₂áǵrom ebʰuget.", "tod ḱeḱluwōs owis aǵrom ebʰuget.",
              "h₁íd tḗtḱm̥.", "kʷíd wēlh₁si?"]:
        assert g.text(s, complete=True) == score.notation_ok(s), s
