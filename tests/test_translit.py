import random
import unicodedata
from pathlib import Path

import pytest

from pie.translit import TranslitError, is_canonical, to_ascii, to_unicode

NFC = lambda s: unicodedata.normalize("NFC", s)  # noqa: E731
NFD = lambda s: unicodedata.normalize("NFD", s)  # noqa: E731


def load_tricky():
    rows = []
    for line in (Path(__file__).parent / "data" / "tricky_forms.tsv").read_text("utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        uni, asc, *_ = line.split("\t")
        rows.append((uni, asc))
    return rows


TRICKY = load_tricky()

# Every consonant symbol of the inventory, as (unicode, ascii).
CONSONANTS = [
    ("p", "p"), ("b", "b"), ("bʰ", "bh"), ("t", "t"), ("d", "d"), ("dʰ", "dh"),
    ("ḱ", "k'"), ("ǵ", "g'"), ("ǵʰ", "g'h"), ("k", "k"), ("g", "g"), ("gʰ", "gh"),
    ("kʷ", "kw"), ("gʷ", "gw"), ("gʷʰ", "gwh"), ("s", "s"), ("z", "z"),
    ("m", "m"), ("n", "n"), ("r", "r"), ("l", "l"), ("w", "w"), ("y", "y"),
    ("h₁", "h1"), ("h₂", "h2"), ("h₃", "h3"), ("H", "H"),
]
MARKS = [("", ""), ("\u0304", ":"), ("\u0301", "/"), ("\u0304\u0301", ":/")]
NUCLEI = [(v + m, v + a) for v in "aeiou" for m, a in MARKS] + [
    (r + "\u0325" + m, r + "_" + a) for r in "rlmn" for m, a in MARKS
]


def consonant_contexts():
    """Each consonant alone, before a vowel, before w, before h₁/H, after a vowel."""
    for cu, ca in CONSONANTS:
        w_ascii = "\\w" if ca in ("k", "g") else "w"
        yield cu, ca
        yield cu + "e", ca + "e"
        yield cu + "we", ca + w_ascii + "e"
        yield cu + "h₁e", ca + "h1e"
        yield cu + "H", ca + "H"
        yield "e" + cu, "e" + ca
        yield "é" + cu + "h₂", "e/" + ca + "h2"


GENERATED = list(consonant_contexts()) + [("t" + nu + "s", "t" + na + "s") for nu, na in NUCLEI]
ALL_FORMS = TRICKY + GENERATED


def test_acceptance_size():
    # Phase 0 acceptance: round-trip on ~200 tricky forms.
    assert len(TRICKY) >= 150
    assert len(ALL_FORMS) >= 200


@pytest.mark.parametrize("uni,asc", ALL_FORMS)
def test_expected_ascii(uni, asc):
    assert to_ascii(uni) == asc


@pytest.mark.parametrize("uni,asc", ALL_FORMS)
def test_unicode_round_trip(uni, asc):
    assert to_unicode(to_ascii(uni)) == NFC(uni)
    # Decomposed input gives the same ASCII.
    assert to_ascii(NFD(uni)) == asc


@pytest.mark.parametrize("uni,asc", ALL_FORMS)
def test_ascii_round_trip(uni, asc):
    out = to_unicode(asc)
    assert out == NFC(uni)
    assert out == NFC(out)
    assert to_ascii(out) == asc


@pytest.mark.parametrize("uni,asc", ALL_FORMS)
def test_canonical(uni, asc):
    assert is_canonical(NFC(uni))


def test_nfd_input_is_not_canonical_but_converts():
    s = NFD("h₁éḱwōs")
    assert not is_canonical(s)
    assert to_unicode(to_ascii(s)) == "h₁éḱwōs"


def test_fuzz_round_trip():
    rng = random.Random(1868)
    syms = CONSONANTS + NUCLEI + [(" ", " "), ("-", "-")]
    for _ in range(5000):
        parts = [rng.choice(syms) for _ in range(rng.randint(1, 9))]
        uni = NFC("".join(p[0] for p in parts))
        asc = to_ascii(uni)
        assert asc.isascii()
        assert to_unicode(asc) == uni
        assert to_ascii(to_unicode(asc)) == asc


@pytest.mark.parametrize("bad", [
    "kʰ", "tʰ", "pʰ", "ḱʰ", "kʷʰ",      # no voiceless aspirates
    "ḱʷ", "kʷʷ", "sʰ", "wʷ",            # impossible modifiers
    "h", "he", "h₄", "ʰ", "ʷ",          # bare h / stray modifiers
    "ə", "i̯", "u̯", "ṛ", "k̂",            # foreign notation: normalize first
    "e\u0301\u0304",                    # acute before macron
    "ŕ", "ḿ", "r\u0304",                # marks on non-syllabic resonants
    "e\u0325", "ḗ\u0301",               # ring on vowel, doubled accent
    "A", "Ḱ", "x", "q", "c", "f", "v", "j", "þ", "1", "\u0301e",
    "…", "“", "—", "\t", "\n",
])
def test_to_ascii_rejects(bad):
    with pytest.raises(TranslitError):
        to_ascii(bad)


@pytest.mark.parametrize("bad", [
    "th", "kh", "k'h", "kwh", "sh",     # no voiceless/plain-consonant aspirates
    "h", "h4", "he", "e/:", "r/", "s:", "_", "'", ":", "/",
    "\\q", "w\\w", "\\w", "x", "A", "5", "é", "e//",
])
def test_to_unicode_rejects(bad):
    with pytest.raises(TranslitError):
        to_unicode(bad)


def test_error_points_at_offender():
    with pytest.raises(TranslitError) as e:
        to_ascii("h₁éḱwos kʰer")
    assert e.value.pos == 9
