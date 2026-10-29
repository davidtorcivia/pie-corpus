import json
import random
import re
import unicodedata
from pathlib import Path

import pytest

from pie.ipa import CONVENTIONS, Convention, color, syllables, to_ipa, to_xsampa
from pie.meter import weights, word_nuclei, word_syllables, words
from pie.phon import parse
from pie.translit import to_ascii

NFC = lambda s: unicodedata.normalize("NFC", s)  # noqa: E731
ROOT = Path(__file__).resolve().parent.parent


# Famous forms, default convention, high tone.
@pytest.mark.parametrize("pie,ipa", [
    ("h₂ówis h₁éḱwōs-kʷe", "χó.wis héc.woːs.kʷe"),
    ("ph₂tḗr", "pə.téːr"),
    ("dʰugh₂tḗr", "dʱu.ɡə.téːr"),
    ("diwés", "di.wés"),
    ("ḱléwos ń̥dʰgʷʰitom", "clé.wos ń̩dʱ.ɡʷʱi.tom"),
    ("gʷʰénti", "ɡʷʱén.ti"),
    ("dyḗws ph₂tḗr", "djéːws pə.téːr"),
    ("wĺ̥kʷos", "wĺ̩.kʷos"),
    ("h₁ésti", "hés.ti"),
    ("kʷetwóres", "kʷet.wó.res"),        # Ved. cat-vā́-ras: VC.CV
    ("h₂stḗr", "χstéːr"),
    ("deywós", "dej.wós"),
])
def test_famous_forms(pie, ipa):
    assert to_ipa(pie) == NFC(ipa)


# Every segment class, one word each (tone off, so only the segment is under test).
@pytest.mark.parametrize("pie,ipa", [
    ("pód", "pod"), ("bel", "bel"), ("tod", "tod"), ("dom", "dom"),
    ("bʰer", "bʱer"), ("dʰeh₁", "dʱeh"), ("gʰos", "ɡʱos"),
    ("ḱom", "com"), ("ǵonu", "ɟo.nu"), ("ǵʰim", "ɟʱim"),
    ("kos", "kos"), ("gos", "ɡos"),
    ("kʷis", "kʷis"), ("gʷow", "ɡʷow"), ("gʷʰon", "ɡʷʱon"),
    ("sed", "sed"), ("nizdós", "niz.dos"),
    ("mer", "mer"), ("nem", "nem"), ("lew", "lew"), ("yugóm", "ju.ɡom"), ("wes", "wes"),
    ("mr̥tós", "mr̩.tos"), ("wĺ̥kʷos", "wl̩.kʷos"), ("ḱm̥tóm", "cm̩.tom"), ("n̥", "n̩"),
    ("ḱr̥̄", "cr̩ː"),
    ("bʰeh₁", "bʱeh"), ("peh₂", "paχ"), ("doh₃", "doɣʷ"), ("dʰeH", "dʱeh"),
    ("a", "a"), ("e", "e"), ("o", "o"), ("i", "i"), ("u", "u"),
    ("ā", "aː"), ("ē", "eː"), ("ō", "oː"), ("ī", "iː"), ("ū", "uː"),
])
def test_segments(pie, ipa):
    assert to_ipa(pie, tone=False) == NFC(ipa)


def test_ascii_input_matches_unicode():
    for pie in ["h₂ówis h₁éḱwōs-kʷe", "ḱléwos ń̥dʰgʷʰitom", "dʰugh₂tḗr", "kʷékʷlos"]:
        assert to_ipa(to_ascii(pie), ascii=True) == to_ipa(pie)
    assert to_ipa("k\\we/kwlos", ascii=True, tone=False) == "kwekʷ.los"   # escaped plain k + w


# Accent: high tone on the nucleus; stress fallback marks the syllable; tone=False marks nothing.
@pytest.mark.parametrize("pie,tone,ipa", [
    ("ph₂tḗr", True, "pə.téːr"),
    ("ph₂tḗr", "stress", "pə.ˈteːr"),
    ("ph₂tḗr", False, "pə.teːr"),
    ("h₂ówis", "stress", "ˈχo.wis"),
    ("deywós", True, "dej.wós"),
    ("déywos", True, "déj.wos"),              # the acute is on the vowel, the glide stays in the coda
    ("déywos", "stress", "ˈdej.wos"),
    ("wĺ̥kʷos", True, "wĺ̩.kʷos"),              # accented syllabic resonant
    ("ń̥dʰgʷʰitom", "stress", "ˈn̩dʱ.ɡʷʱi.tom"),
    ("kʷe", True, "kʷe"),                     # unaccented clitic: no mark
    ("ǵénh₁tor", "stress", "ˈɟe.nə.tor"),
])
def test_accent(pie, tone, ipa):
    assert to_ipa(pie, tone=tone) == NFC(ipa)


def test_stress_and_tone_never_both():
    for pie in ["h₂ówis h₁éḱwōs-kʷe", "ḱléwos ń̥dʰgʷʰitom", "ph₂tḗr"]:
        s = to_ipa(pie, tone="stress")
        assert "́" not in unicodedata.normalize("NFD", s)
        assert "ˈ" not in to_ipa(pie)


def test_bad_tone():
    with pytest.raises(ValueError):
        to_ipa("só", tone="pitch")


# Vocalized laryngeals: a nucleus [ə] exactly where pie.meter counts one.
@pytest.mark.parametrize("pie,ipa", [
    ("ph₂tḗr", "pə.teːr"),               # CHC
    ("ǵénh₁tor", "ɟe.nə.tor"),           # RHC: Ved. janitár-
    ("méǵh₂", "me.ɟə"),                 # CH#: Ved. máhi
    ("h₃ésth₁", "ɣʷos.tə"),              # CH#, with h₃e coloring
    ("h₃ésth₁h₂", "ɣʷos.təχ"),           # -CHH#: only the first vocalizes
    ("h₂énh₁mos", "χa.nə.mos"),          # Gk ἄνεμος
    ("h₂érh₃trom", "χa.rət.rom"),        # Gk ἄροτρον
    ("bʰéroyh₁t", "bʱe.rojht"),         # V y H C: joins the diphthong
    ("kréwh₂s", "kre.wəs"),              # after -w it vocalizes
    ("h₂stḗr", "χsteːr"),               # #HC stays consonantal
    ("pĺ̥h₂seh₂m", "pl̩χ.saχm"),          # after a syllabic resonant: consonantal
])
def test_vocalized_laryngeals(pie, ipa):
    assert to_ipa(pie, tone=False) == NFC(ipa)


def test_vocalized_styles():
    assert to_ipa("dʰugh₂tḗr", convention=Convention(vocalized="colored"), tone=False) == "dʱu.ɡɐ.teːr"
    assert to_ipa("h₂érh₃trom", convention=Convention(vocalized="colored"), tone=False) == "χa.rɵt.rom"
    assert to_ipa("ph₂tḗr", convention=Convention(vocalized="syllabic"), tone=False) == NFC("pχ̩.teːr")
    with pytest.raises(ValueError):
        Convention(vocalized="nasal")


# Laryngeal coloring (default on): short e next to h₂ → a, next to h₃ → o; ē and h₁ untouched.
@pytest.mark.parametrize("pie,ipa", [
    ("h₂éǵeti", "χá.ɟe.ti"),
    ("h₃éḱwn̥", "ɣʷóc.wn̩"),
    ("bʰéh₂ti", "bʱáχ.ti"),
    ("dʰéh₁ti", "dʱéh.ti"),             # h₁ does not color
    ("h₂ḗr", "χéːr"),                   # long ē is not colored (Eichner's law)
    ("h₂ówis", "χó.wis"),              # o stays o
    ("Hésti", "hés.ti"),               # generic H does not color
])
def test_coloring(pie, ipa):
    assert to_ipa(pie) == NFC(ipa)


def test_uncolored_convention():
    assert to_ipa("h₂éǵeti", convention="uncolored") == "χé.ɟe.ti"
    segs = parse("peh₂")
    assert [s.base for s in color(segs)] == ["p", "a", "h2"]


def test_conventions():
    assert to_ipa("h₁éh₂h₃", convention="pharyngeal", tone=False) == "ʔaħʕʷ"
    assert to_ipa("Hé", convention="pharyngeal") == "ʔé"           # H takes h₁'s value
    assert to_ipa("h₃ésth₁", convention=Convention(laryngeals="voiceless"), tone=False) == "χʷos.tə"
    assert to_ipa("ḱékʷgʰ", convention=Convention(dorsals="fronted"), tone=False) == "kʲekʷɡʱ"
    assert to_ipa("ḱékʷgʰ", convention=Convention(dorsals="uvular"), tone=False) == "kekʷɢʱ"
    assert to_ipa("Hé", convention=Convention(generic="ʔ"), tone=False) == "ʔe"
    with pytest.raises(ValueError):
        to_ipa("só", convention="kortlandt")
    assert set(CONVENTIONS) >= {"default", "pharyngeal", "uncolored"}


def test_syllabification_rule():
    assert syllables("h₁éḱwōs") == ["héc", "woːs"]                 # VC.CV
    assert syllables("h₂ówis", tone=False) == ["χo", "wis"]         # V.CV
    assert syllables("septḿ̥", tone=False) == ["sep", "tm̩"]
    assert syllables("h₂ŕ̥tḱos", tone=False) == ["χr̩t", "cos"]       # VC.CV with a syllabic resonant
    assert syllables("ǵʰs", tone=False) == []                       # no nucleus: no syllable
    assert to_ipa("ǵʰs", tone=False) == "ɟʱs"


def test_punctuation_breaks():
    assert to_ipa("só, h₂ówis. kʷe? (só)") == "só | χó.wis ‖ kʷe ‖ só"
    assert to_ipa("só, . só") == "só ‖ só"                         # | then ‖ → ‖
    assert to_ipa("só. só", breaks=False) == "só só"
    assert to_ipa('"só" =só*') == "só só"


def test_clitic_hyphen_joins_host():
    assert to_ipa("h₃ésth₁-kʷe", tone=False) == "ɣʷos.tə.kʷe"
    assert len(syllables("h₃ésth₁-kʷe")) == word_syllables("h₃ésth₁-kʷe") == 3


def test_xsampa():
    assert to_xsampa(to_ipa("h₂ówis h₁éḱwōs-kʷe")) == "Xo_H.wis he_Hc.wo:s.k_we"
    assert to_xsampa(to_ipa("ph₂tḗr")) == "p@.te:_Hr"
    assert to_xsampa(to_ipa("ǵʰwĺ̥", tone="stress")) == "\"J\\_twl="
    assert to_xsampa(to_ipa("dʰugh₂tḗr. só")) == "d_tu.g@.te:_Hr || so_H"
    assert to_xsampa("ħaʕʷ") == "X\\a?\\_w"
    with pytest.raises(ValueError):
        to_xsampa("θ")


def test_output_is_nfc_and_uses_ipa_g():
    s = to_ipa("gʷʰénti ǵénh₁tor gos")
    assert s == NFC(s) and "g" not in s


# --- consistency with pie.meter over the corpus ------------------------------------------------------------

_NUCLEUS = re.compile(r"[aeiouəɐɵ]|.̩")


def _corpus_words(tiers=("tier1", "tier2", "tier3"), sample=None, seed=7):
    out = []
    for t in tiers:
        for f in sorted((ROOT / "corpus" / t).glob("*.jsonl")):
            for line in f.read_text("utf-8").splitlines():
                if line.strip():
                    p = json.loads(line).get("pie")
                    if p:
                        out += words(p)
    out = sorted(set(out))
    if sample and len(out) > sample:
        out = random.Random(seed).sample(out, sample)
    return out


def test_syllable_count_matches_meter_tier1():
    ws = _corpus_words(("tier1",))
    assert len(ws) > 100
    bad = [w for w in ws if len(syllables(w)) != word_syllables(w)]
    assert not bad, bad[:10]


def test_syllable_count_matches_meter_sample():
    ws = _corpus_words(("tier2", "tier3"), sample=3000)
    bad = []
    for w in ws:
        n = word_syllables(w)
        ipa = unicodedata.normalize("NFD", to_ipa(w, tone=False))
        if len(syllables(w)) != n or len(_NUCLEUS.findall(ipa)) != n:    # also count nuclei in the string itself
            bad.append(w)
    assert not bad, bad[:10]


def test_syllable_weight_matches_meter():
    """Within a word, an IPA syllable is heavy iff it has a long nucleus or a coda, which must agree with
    meter.weights (the word-final syllable depends on the next word, so it is left out)."""
    long_or_coda = re.compile(r"ː|[^aeiouəɐɵ̩́]$")
    for w in _corpus_words(("tier1",)) + _corpus_words(("tier3",), sample=1000):
        sy = [unicodedata.normalize("NFD", s) for s in syllables(w)]
        mine = "".join("H" if long_or_coda.search(s) else "L" for s in sy)
        assert mine[:-1] == weights(w)[:-1], (w, sy, weights(w))


def test_shared_nuclei():
    segs, nuclei = word_nuclei("dʰugh₂tḗr")
    assert len(syllables("dʰugh₂tḗr")) == len(nuclei) == 3
