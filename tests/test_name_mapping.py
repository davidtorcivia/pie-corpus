"""Inherited source-tagged names survive the same-lexeme gate."""
import pytest

from pie import formula_search as fs, formula_search_multi as fm
from pie import germanic_new_mapping as gm
from pie import name_mapping as nm
from pie import mapping as mp, tier2_secure as secure


@pytest.mark.parametrize('corpus,lemma,lid', [
    ('hom', 'Ζεύς', 'pie-lex-dyexws'),
    ('grp', 'Ἠώς', 'pie-lex-h2ewsoxs'),
    ('grc-late', 'Ἥλιος', 'pie-lex-soh2wl'),
    ('lat', 'iuppiter', 'pie-lex-dyexws'),
    ('lat', 'sol', 'pie-lex-soh2wl'),
    ('lat', 'luna', 'pie-lex-lowksneh2'),
    ('lat', 'aurora', 'pie-lex-h2ewsoxs'),
    ('menota', 'þórr', 'pie-lex-stenh2'),
    ('menota', 'dagr', 'pie-lex-dhogwhos'),
    ('menota', 'sól', 'pie-lex-soh2wl'),
    ('menota', 'jǫrð', 'pie-lex-h1erteh2'),
])
def test_exact_inherited_names(corpus, lemma, lid):
    assert lid in nm.exact_name_ids(corpus, lemma)
    assert nm.name_lemma(corpus, lemma) == lemma


@pytest.mark.parametrize('corpus,lemma', [
    ('hom', 'Σωκράτης'), ('grp', 'Κῦρος'), ('hom', 'Πάτροκλος'),
    ('grp', 'Κλεάνωρ'), ('grp', 'Ζήνων'), ('grp', 'Ἀρκαδία'), ('hom', 'Στέντωρ'),
    ('hom', 'Εὐρύκλεια'), ('grp', 'Ἀντίγονος'), ('grp', 'Ἀντιφῶν'),
    ('menota', 'ǫgmundr'), ('menota', 'steinarr'), ('icepahc', 'ófeigur'),
    ('menota', 'Úlfr'), ('menota', 'ulfr'), ('menota', 'Finnr'),
    ('menota', 'Hallr'), ('menota', 'Oddr'), ('icepahc', 'finna'),
])
def test_ordinary_names(corpus, lemma):
    assert nm.name_lemma(corpus, lemma) == lemma + ' (name)'
    assert nm.name_lemma(corpus, lemma + ' (name)') == lemma + ' (name)'


def test_source_name_routes_and_content():
    for c in ('grc', 'grp', 'grc-late', 'hom'):
        t = fs.Token(c, 'Ζεύς', 'Ζεύς', 'fixture', {}, True, 'name')
        assert (t.lemma, t.content, t.pos) == ('Ζεύς', True, 'noun')
        t = fs.Token(c, 'Σωκράτης', 'Σωκράτης', 'fixture', {}, True, 'name')
        assert (t.lemma, t.content) == ('Σωκράτης (name)', False)
    for c, tag in [('menota', 'NP'), ('icepahc', 'NPR-N')]:
        if c == 'menota':
            assert gm.annotated_norse_lemma('þórr', tag, c) == 'þórr'
        lem = gm.annotated_norse_lemma('hallr', tag, c)
        assert not fs.Token(c, lem, '', 'fixture', {}, True, 'noun').content
    # Latin PROPN begins outside LAT_CONTENT; exact inherited names restore content.
    assert fs.Token('lat', 'iuppiter', '', 'fixture', {}, False, 'name').content


def test_real_skyfather_passages():
    ts = fs.load_homer()
    zeus = next(t for t in ts if t.locus == 'Il. 4.235' and t.lemma == 'Ζεύς')
    assert zeus.lemma == 'Ζεύς' and zeus.content
    lex = fs.load_jsonl(fs.ROOT / 'data/lexicon/lexicon.jsonl')
    m = fs.build_kaikki_mapping('grc', lex, ts, fs.build_homer_mapping(lex, ts), pseudo=True)
    m = fm.apply_lemma_overrides('hom', m, fs.group_map(lex))
    fs.apply_mapping([zeus], m, level='lexeme')
    assert 'pie-lex-dyexws' in zeus.roots
    av = fm.load_dcs(texts=fm.DCS_VEDIC[:2])
    sky = [t for t in av if '9, 10.s23' in t.locus and t.surface == 'dyaur']
    assert len(sky) == 1
    assert sky[0].content and not sky[0].lemma.endswith(' (name)')
    assert 'pie-lex-dyexws' in mp.resolve_table('av')[sky[0].lemma].ids


@pytest.mark.parametrize('formation,ids,scope,expected', [
    (None, ['pie-lex-test'], 'production', True),
    ('derivative', ['pie-lex-test'], 'production', False),
    (None, ['pie-root-test'], 'production', False),
    (None, ['compound:test'], 'production', False),
    (None, ['pie-lex-test'], 'research_only', False),
    (None, [], 'production', False),
])
def test_gate_obeys_production_decisions(monkeypatch, formation, ids, scope, expected):
    row = {'corpus': 'menota', 'lemma': 'testname', 'lex_id': ids,
           'formation': formation, 'scope': scope}
    ov = mp._pack({'menota': {'testname': [mp.decision(row)]}}, {})
    resolved = mp.resolve_rows('menota', [], ov)
    entries = {'pie-lex-test': {'id': 'pie-lex-test', 'form': 'test', 'root_id': 'pie-root-test'}}
    checker = secure.SecureChecker.from_population(entries, secure.build_population({'menota': [{**row, 'lang': 'non'}]}, ov))
    monkeypatch.setattr(nm, '_resources', lambda _: ('non', ov, resolved, checker))
    # This test isolates the exact-formation gate; allowlist membership is separate.
    monkeypatch.setattr(nm, 'theonym_allowed', lambda corpus, lemma: True)
    nm.exact_name_ids.cache_clear()
    try:
        assert bool(nm.exact_name_ids('menota', 'testname')) == expected
    finally:
        nm.exact_name_ids.cache_clear()


# Narrowed exemption (docs/research/8c-theonym-narrowing.md): only reviewed
# deities and personified powers keep roots; other exact matches are names.
@pytest.mark.parametrize('corpus,lemma,lid', [
    ('hom', 'Ζεύς', 'pie-lex-dyexws'),
    ('menota', 'þórr', 'pie-lex-stenh2'),
    ('lat', 'iuppiter', 'pie-lex-dyexws'),
    ('av', 'div', 'pie-lex-dyexws'),
    ('sa-ep', 'uṣas', 'pie-lex-h2ewsoxs'),
])
def test_theonyms_keep_roots(corpus, lemma, lid):
    assert nm.theonym_allowed(corpus, lemma)
    assert lid in nm.exact_name_ids(corpus, lemma)
    assert nm.name_lemma(corpus, lemma) == lemma


@pytest.mark.parametrize('corpus,lemma', [
    ('hom', 'Μέντωρ'), ('hom', 'Ἕλος'), ('hom', 'Ἄκτωρ'), ('hom', 'Μέμνων'),
    ('hom', 'Δαίδαλος'), ('grc-late', 'Πόντος'), ('grc-late', 'Ἕως'),
    ('lat', 'hercules'), ('lat', 'pater'), ('orv', 'дунаи'), ('orv', 'волосъ'),
    ('menota', 'ljótr'), ('icepahc', 'sveinn'), ('icepahc', 'hann'),
])
def test_exact_non_theonyms_become_names(corpus, lemma):
    assert not nm.theonym_allowed(corpus, lemma)
    assert nm.exact_name_ids(corpus, lemma) == frozenset()
    assert nm.name_lemma(corpus, lemma) == lemma + ' (name)'


def test_theonym_narrowing_production_tokens():
    # Through Token.__post_init__ -> annotated_name -> name_lemma.
    t = fs.Token('hom', 'Μέντωρ', 'Μέντωρ', 'fixture', {}, True, 'name')
    assert (t.lemma, t.content, t.pos) == ('Μέντωρ (name)', False, 'name')
    t = fs.Token('hom', 'Ἕλος', 'Ἕλος', 'fixture', {}, True, 'name')
    assert (t.lemma, t.content) == ('Ἕλος (name)', False)
    t = fs.Token('hom', 'Ζεύς', 'Ζεύς', 'fixture', {}, True, 'name')
    assert (t.lemma, t.content, t.pos) == ('Ζεύς', True, 'noun')
    t = fs.Token('lat', 'iuppiter', '', 'fixture', {}, False, 'name')
    assert (t.lemma, t.content) == ('iuppiter', True)
    t = fs.Token('av', 'div', 'dyaur', 'fixture', {}, True, 'name')
    assert (t.lemma, t.content) == ('div', True)
    assert gm.annotated_norse_lemma('þórr', 'NP', 'menota') == 'þórr'
    assert gm.annotated_norse_lemma('ljótr', 'NP', 'menota') == 'ljótr (name)'


def test_real_homer_mentor_is_a_name():
    ts = fs.load_homer()
    mentor = [t for t in ts if t.lemma.startswith('Μέντωρ')]
    assert mentor and all(t.lemma == 'Μέντωρ (name)' and not t.content for t in mentor)
    assert any(t.lemma == 'Ζεύς' and t.content for t in ts)
