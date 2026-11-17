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


@pytest.mark.parametrize("english,pie", [
    ("There is no hope.", "h₂oyséh₂ ne h₁ésti."),
    ("No man came.", "wiHrós ne h₁nédʰt."),
    ("Nobody came.", "ne kʷis h₁nédʰt."),
    ("No one came.", "ne kʷis h₁nédʰt."),
    ("I saw nothing.", "ne kʷid widóm."),
    ("There was no water.", "wódr̥ ne h₁ést."),
])
def test_a_negative_determiner_negates_the_clause(transfer, english, pie):
    """Owner 2026-11-05: 'There is no hope' came back as 'there is hope'. "no X", "nothing", "nobody" on a subject,
    object or existential noun put ne on the clause (the pronouns are the indefinite kʷis/kʷid)."""
    r = transfer.translate(english)
    assert r.pie == pie and not r.errors


def test_no_elsewhere_is_reported_not_dropped(transfer):
    r = transfer.translate("The man with no horse wept.")
    assert " ne " not in f" {r.pie} " and any("'no horse'" in n for n in r.notes)


def test_there_is_takes_the_verb_that_agrees(transfer):
    """'there is/are X': X is the subject of h₁ésti (existence takes the verb), so a plural takes the plural."""
    assert transfer.translate("There are three wolves.").pie == "tréyes wĺ̥kʷōs h₁sénti."
    assert transfer.translate("There was a king.").pie == "h₃rḗǵs h₁ést."


@pytest.mark.parametrize("english,pie", [
    ("I have a horse.", "h₁éḱwos moy h₁ésti."),
    ("I have no hope.", "h₂oyséh₂ moy ne h₁ésti."),
    ("The king had a horse.", "h₁éḱwos h₃rēǵéy h₁ést."),
    ("They have horses and cows.", "h₁éḱwōs gʷówes-kʷe h₁éymos h₁sénti."),
    ("I have nothing.", "ne kʷid moy h₁ésti."),
])
def test_possessive_have_is_the_dative_of_possession(transfer, english, pie):
    """Owner 2026-11-05: 'I have no hope' came back as a perfect of 'be aware'. Possessive 'have' is the possessor in
    the dative + h₁ésti (Lat. mihi est); the perfect's 'have' is untouched."""
    r = transfer.translate(english)
    assert r.pie == pie and not r.errors
    assert any("dative of possession" in n for n in r.notes)


def test_perfect_have_stays_the_perfect(transfer):
    r = transfer.translate("I have seen the horse.")
    assert r.pie == "h₁éḱwom dedórḱh₂e." and not any("dative of possession" in n for n in r.notes)


def test_only_is_h1oynos_agreeing_with_its_noun(transfer):
    """Owner 2026-11-05: 'Only death remains' left 'only' out. h₁óynos 'one, alone' stands in, agreeing (f. mértis,
    m.pl. deywṓs), and the note says so."""
    r = transfer.translate("Only death remains.")
    assert r.pie == "h₁óyneh₂ mértis méneti." and any("'only' ≈ h₁óynos" in n for n in r.notes)
    assert transfer.translate("Only the gods know.").pie == "h₁óynōs deywṓs widḗr."
    assert not any("left out" in n for n in r.notes)


def test_a_verbless_phrase_after_a_comma_is_its_own_utterance(transfer):
    """Owner 2026-11-05: 'There is no hope, only death' lost the negation and 'only death'."""
    r = transfer.translate("There is no hope, only death")
    assert r.pie == "h₂oyséh₂ ne h₁ésti h₁óyneh₂ mértis." and not r.errors
    assert r.plan["clauses"][1]["type"] == "np"
    assert not any(n.startswith("left out") for n in r.notes)


@pytest.mark.parametrize("english,pie", [
    ("Come, my friend!", "príHe moy gʷm̥yé."),
    ("Come, young men!", "h₂yúHn̥ḱōs wíHrōs gʷm̥yéte."),
    ("Do not fight, young men!", "h₂yúHn̥ḱōs wíHrōs mē wikéte."),
])
def test_an_address_after_a_comma_is_vocative(transfer, english, pie):
    """In a command the comma-set noun phrase is an address, and a plural addressee makes the verb plural."""
    r = transfer.translate(english)
    assert r.pie == pie and not r.errors


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


# ---- pre-launch polish (2026-11-17): what site visitors type ------------------------------------------------------
@pytest.mark.parametrize("english,pie", [
    ("wolf", "wĺ̥kʷos."),
    ("Two horses.", "dwóh₁ h₁éḱwoh₁."),
    ("The wolf and the dog.", "wĺ̥kʷos ḱwṓ-kʷe."),
])
def test_a_sentence_without_a_verb_is_a_noun_phrase(transfer, english, pie):
    """A bare noun ('wolf') was reported as having no PIE word: a verbless sentence is the engine's np utterance
    (planner-brief-v4 'Noun-phrase utterance')."""
    r = transfer.translate(english)
    assert r.pie == pie and not r.unknown and r.plan["clauses"][0]["type"] == "np"


def test_or_between_nouns_is_not_turned_into_and(transfer):
    r = transfer.translate("The wolf or the dog.")
    assert "-kʷe" not in r.pie and any("'or dog' left out" in n for n in r.notes)


def test_a_name_never_takes_a_stand_in(transfer):
    """'John loves Mary' came back as 'craftsman loves craftsman' (the vectors put names near 'smith'). A name with
    no lexeme is reported unknown; 'My name is David' keeps 'my name' instead of failing."""
    r = transfer.translate("John loves Mary.")
    assert r.pie == "lubʰyéti." and set(r.unknown) == {"John", "Mary"} and not any("≈" in n for n in r.notes)
    r = transfer.translate("My name is David.")
    assert r.pie == "h₁nómn̥ moy." and r.unknown == ["David"] and not r.errors


@pytest.mark.parametrize("english,pie", [
    ("What did the wolf eat?", "kʷíd wĺ̥kʷos h₂éḱh₃t?"),          # was 'what eat!' (IMP 2SG), the wolf dropped
    ("Do not kill the horse!", "h₁éḱwom mē gʷʰéns."),
    ("Do come!", "gʷm̥yé."),
])
def test_do_support_is_not_a_command(transfer, english, pie):
    assert transfer.translate(english).pie == pie


def test_a_mislemmatized_verb_is_recovered(transfer):
    """spaCy lemmatizes 'shines' as 'shin', so the site's own example 'Dawn, daughter of the sky, shines.' had no
    verb and translated to nothing; the apposition is kept (realize: APPOS)."""
    r = transfer.translate("Dawn, daughter of the sky, shines.")
    assert r.pie == "h₂éwsōs diwés dʰugh₂tḗr gʰlindeti." and not r.unknown


def test_a_verb_with_no_lexeme_takes_the_nearest_one(transfer):
    r = transfer.translate("I don't understand.")
    assert r.pie == "ne wóydh₂e." and any("'understand' ≈ 'know'" in n for n in r.notes)


@pytest.mark.parametrize("english,pie", [
    ("If you come, I will go.", "h₁yód gʷm̥yési h₁éyoh₂."),
    ("When the sun rises, the birds sing.", "h₁yód sóh₂wl̥ h₁réyh₁seti h₂éweyes gʷéHyonti."),
    ("I will go if you come.", "h₁éyoh₂ h₁yód gʷm̥yési."),
])
def test_a_subordinate_clause_takes_h1yod(transfer, english, pie):
    """'if' was dropped silently and subordinating 'when' came out as the interrogative kʷóm 'when?'. The clause
    particle h₁yód 'if, when' (pie.realize; idioms.json: because → a clause with h₁yód) marks it, in the English
    order."""
    assert transfer.translate(english).pie == pie


def test_a_subordinator_with_no_rule_is_reported(transfer):
    assert any("'Although' left out" in n for n in transfer.translate("Although he is old, he is strong.").notes)


@pytest.mark.parametrize("english,pie", [
    ("The wolf is bigger than the dog.", "wĺ̥kʷos ḱunés méǵyōs."),
    ("The king is the greatest of the men.", "h₃rḗǵs wiHrṓm méǵistos."),
    ("The bigger wolf ate the sheep.", "méǵyōs wĺ̥kʷos h₂ówim h₂éḱh₃t."),
])
def test_comparatives_and_superlatives(transfer, english, pie):
    """'bigger than the dog' came out as 'big', the dog dropped: the engine's degrees (pie.degree) with the ablative
    of comparison and the partitive genitive (Ringe 2006 §2.3.1)."""
    r = transfer.translate(english)
    assert r.pie == pie and not r.errors


def test_a_degree_the_engine_cannot_build_is_noted(transfer):
    r = transfer.translate("He is older than me.")
    assert any("no comparative of ǵérh₂onts" in n for n in r.notes)


@pytest.mark.parametrize("english,pie", [
    ("Yesterday I saw a wolf here.", "wĺ̥kʷom dʰǵʰyés h₁idʰé widóm."),
    ("Today I will go home.", "dṓm ḱósmi dinóy h₁éyoh₂."),            # idioms.json: 'on this day'
    ("Come back soon!", "h₂éti móḱs gʷm̥yé."),
    ("She never sleeps.", "ne sésti."),
])
def test_adverbs_are_said(transfer, english, pie):
    """Time and place adverbs were left out: the indeclinables of the lexicon and idioms.json (Transfer.adverbs)."""
    r = transfer.translate(english)
    assert r.pie == pie and not any(n.startswith("left out") for n in r.notes)


def test_a_time_word_is_never_a_nouns_stand_in(transfer):
    assert not any("≈ 'yesterday'" in n for n in transfer.translate("Today is a good day.").notes)


def test_tense_and_modals_are_not_lost_silently(transfer):
    assert transfer.translate("The man was eating meat.").pie == "wiHrós mḗms h₁ḗdt."     # PST, the imperfect
    assert transfer.translate("The man might eat meat.").pie == "wiHrós mḗms h₁édih₁t."   # OPT, like 'may'
    for s, m in [("The man would eat meat.", "would"), ("We cannot go.", "can"), ("The man must eat meat.", "must")]:
        assert any(f"'{m}' not expressed" in n for n in transfer.translate(s).notes), s


@pytest.mark.parametrize("english,pie", [
    ("Hello!", "kéh₂ilos h₁sdʰí."),
    ("Good morning.", "kéh₂ilos h₁sdʰí."),
    ("Hello, friends!", "príHōs kéh₂ilōs h₁sté."),
    ("Welcome!", "príHe gʰóstey."),
])
def test_greetings_are_the_briefs_formulas(english, pie):
    """'Hello', 'Thank you', 'Welcome' came back as having no PIE word. No PIE greeting is reconstructible; the
    planner brief builds them from inherited words (planner-brief-v4, Greetings and thanks: 'be well!', the dear
    guest, praise of the giver), and the note says so."""
    pytest.importorskip("spacy")
    from pie.translator import english_to_pie
    [s] = english_to_pie(english)
    assert s["pie"] == pie and any("planner-brief-v4" in n for n in s["notes"])


def test_thanks_is_praise_and_please_yes_no_are_reported():
    pytest.importorskip("spacy")
    from pie.translator import english_to_pie
    [s] = english_to_pie("Thank you.")
    assert "gʷr̥néH" in s["pie"]
    [s] = english_to_pie("Thanks, my friend!")
    assert s["pie"].startswith("príHe moy") and "gʷr̥néH" in s["pie"] and not s["unknown"]
    for w in ("Yes.", "No.", "Please."):
        [s] = english_to_pie(w)
        assert s["pie"] is None and s["unknown"] == [w.strip(".")] and s["notes"], w
    [s] = english_to_pie("Please give me water.")       # 'please' is not the verb 'gratify'
    assert s["pie"] and "'please' left out" in " ".join(s["notes"])
    hello, how = english_to_pie("Hello, how are you?")
    assert hello["pie"] == "kéh₂ilos h₁sdʰí." and how["pie"] == "kʷíh₁ h₁ési?"
    assert "planner-brief" not in " ".join(english_to_pie("Hail fell from the sky.")[0]["notes"])


def test_abbreviations_end_no_sentence():
    from pie.translator import split_sentences
    assert split_sentences("Dr. Smith saw the wolf. The dog barked.") == ["Dr. Smith saw the wolf.", "The dog barked."]
    assert split_sentences("The wolf... saw the sheep?!") == ["The wolf... saw the sheep?!"]
    assert split_sentences("No. I will not go.") == ["No.", "I will not go."]


def test_every_word_has_a_gloss_for_the_site():
    """The site lays out w.gloss under each word (w.gloss.split): a gloss that doesn't align word for word falls
    back to each word's own reading, never None."""
    from pie.translator import _words
    ws = _words("wĺ̥kʷos h₂ówim widét.", None, None)
    assert [w["gloss"] for w in ws] == ["wolf-NOM.SG", "sheep-ACC.SG", "see-AOR.3SG"]


def test_readable_gloss_tidies_cut_glosses():
    assert readable("fire.(the.element-NOM.SG computer:.counting.machine-ACC.PL go.(away)-IMP.2SG") == \
        "fire-NOM.SG computer-ACC.PL go.(away)-IMP.2SG"


def test_analyzer_splits_an_unhyphenated_enclitic(analyzer):
    """'h1ekwoskwe' was read as a near spelling of h₁érkʷowe 'we two praised'."""
    w = analyzer.analyze("h1ekwoskwe")[0]
    assert w["clitic"] == ("kʷe", "and") and w["analyses"][0].lex_id == "pie-lex-h1ekjwos"


def test_pie_to_english_marks_a_guess_and_reads_degrees():
    from pie.translator import pie_to_english
    assert pie_to_english("hello")["rough_english"].endswith("(?)")       # an English word is no PIE word
    r = pie_to_english("wĺ̥kʷos ḱunés méǵyōs.")                         # the translator's own comparative
    assert [w["match"] for w in r["words"]] == ["exact"] * 3 and r["rough_english"].endswith("more big")
