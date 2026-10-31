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
    ("Do not fear the wolf!", "wĺ̥kʷōd mē pr̥ksḱés."),       # fear takes the ablative (fear-ablative-2026-10-30.md)
    ("Let us drive the cattle home.", "gʷṓs dṓm h₂éǵōmes."),
    ("We walked through the forest.", None),
    ("Give me water!", "méǵʰye wódr̥ dh₃dʰí."),
])
def test_transfer_builds_the_plan(transfer, english, pie):
    r = transfer.translate(english)
    assert (r.pie == pie if pie else r.pie) and not r.errors


def test_core_gap_words_reach_the_translator(transfer):
    """docs/audits/lexicon-gaps-core-2026-10-30.md: the English words map to the inherited lexemes, and a stative
    perfect with no present stem (h₃eh₃óde 'hates', Lat. ōdī) gives the present state."""
    assert transfer.translate("The beautiful woman carries the goat.").pie == "ḱubʰréh₂ gʷḗn káprom bʰéreti."
    assert transfer.translate("The council decides.").pie == "dʰh₁tléh₂ h₂réh₁dʰeti."
    assert transfer.translate("I hate the wolf.").pie == "wĺ̥kʷom h₃eh₃ódh₂e."


def test_round3_words_reach_the_translator(transfer):
    """docs/audits/lexicon-gaps-round3-2026-10-31.md: war, exchange and kinship words, with the new specs."""
    assert transfer.translate("The brave man repays the debt.").pie == "dʰr̥sús wiHrós dʰl̥gʰóm gʰéldʰeti."
    assert transfer.translate("The bride weeps.").pie == "snusós HréwdHti."
    # 'kill' is moréyeti or gʷʰénti 'slay': corpus use decides (the horror wave, t085-t088, slays often)
    assert transfer.translate("The plague kills the people.").pie in ("móros h₁léwdʰins moréyeti.",
                                                                       "móros h₁léwdʰins gʷʰénti.")


def test_round5_words_reach_the_translator(transfer):
    """docs/audits/lexicon-gaps-round5-2026-10-31.md: a bull is uksḗn, 'another' is the adjective h₂élyos, and the
    round's new words."""
    assert transfer.translate("The great bull sleeps.").pie == "méǵh₂s uksḗn sésti."
    assert transfer.translate("Another girl sings.").pie == "h₂élyeh₂ dʰugh₂tḗr gʷéHyeti."
    assert transfer.translate("The other men saw his face.").pie == "h₂élyōs wiHrṓs h₁ésyo h₁énih₃kʷom widónt."
    assert transfer.translate("The holy man roasts meat.").pie == "sh₂krós wiHrós mḗms bʰr̥ǵyéti."


def test_round6_words_reach_the_translator(transfer):
    """docs/audits/lexicon-gaps-round6-2026-11-01.md: the mare, the law, barking, baking and pasturing."""
    assert transfer.translate("The mare runs.").pie == "h₁éḱweh₂ tékʷeti."
    assert transfer.translate("The dog barks.").pie == "ḱwṓ léh₂yeti."
    assert transfer.translate("The man knows the law.").pie == "wiHrós h₂yéwos wóyde."
    assert transfer.translate("The shepherd pastures the sheep.").pie == "poh₂imḗn h₂ówim peh₂sḱéti."
    assert transfer.translate("The loud man sings.").pie == "kl̥h₁rós wiHrós gʷéHyeti."


def test_transfer_reports_what_it_cannot_say(transfer):
    r = transfer.translate("The tiger ate the bread.")
    assert set(r.unknown) >= {"tiger"}


def test_transfer_never_drops_a_word_silently(transfer):
    """Owner 2026-10-30: 'We hold these truths to be self evident' came back as one verb. The governed clause is
    translated, a missing word is replaced by the nearest one the lexicon has and noted, and every content word
    that is still left out is listed."""
    r = transfer.translate("We hold these truths to be self evident.")
    assert len(r.pie.split()) >= 4 and not r.errors
    notes = " ".join(r.notes)
    assert "h₁sónt" in r.pie                      # h₁sónts 'true; n. as noun: the truth'
    assert "'evident' ≈ 'visible'" in notes and "self" in notes


@pytest.mark.parametrize("typed,form", [("wekwos", "wékʷos"), ("*wékʷos", "wékʷos"), ("we/kwos", "wékʷos"),
                                        ("h2owis", "h₂ówis"), ("ekwos", "h₁éḱwos"), ("dyeus", "dyḗws"),
                                        ("bhrater", "bʰréh₂tēr")])
def test_analyzer_forgives_how_people_type(analyzer, typed, form):
    """Owner 2026-10-30: 'wekwos' and '*wékʷos' found nothing. Plain letters, ASCII, a leading *, dropped laryngeals
    and accents, and a misremembered vowel all reach the corpus form."""
    from pie.translator.analyze import skeleton
    an, how = analyzer.word(typed)
    assert an and how in ("exact", "unaccented", "typed", "close")
    assert form in analyzer.forms_for(typed) or how in ("exact", "unaccented")


def test_words_carry_their_provenance():
    """Owner 2026-10-30: the app marks each word attested, inferred or coined."""
    from pie.translator.provenance import provenance
    assert provenance("pie-lex-h1ekjwos") == "attested"         # Ved. áśva-, Lat. equus, …
    assert provenance("pie-proj-spelom") == "inferred"          # our project reconstruction
    assert provenance("pie-neo-bread") == "coined"
    assert provenance("closed:personal/1") == "attested"
