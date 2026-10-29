"""Corpus-quality batch 1, area 'other': production-path regressions (no review slabs or claims)."""
import json
from pathlib import Path

import pytest

from pie import formula_search as fs, mapping as mp, material_units as mu
from pie.cq1_mapping import reading_rows

ROOT = Path(__file__).resolve().parents[1]
CQ = ROOT / 'data/research/8c/corpus-quality'


def tok(corpus, lemma, surface, locus='elsewhere', content=True, pos='noun'):
    return fs.Token(corpus, lemma, surface, locus, {}, content, pos)


@pytest.mark.parametrize('corpus,lemma,surface,expected', [
    ('ang', 'cwēn|cwen', 'cn', '?cn'),            # OCR fragment of a vowel-less word
    ('ang', 'mētan', 'Mt', '?mt'),
    ('ang', 'cwēn|cwen', 'cwen', 'cwēn|cwen'),     # real word keeps its lemma
    ('ang', '?td', 'td', '?td'),
    ('grc', 'δείκνυμι', 'δεξάμενοι', 'δέχομαι'),
    ('grc-late', 'δείκνυμι', 'δέξασθαι', 'δέχομαι'),
    ('grc', 'δείκνυμι', 'δέξαιντ’', 'δέχομαι'),
    ('grc', 'δείκνυμι', 'δέξαι', 'δείκνυμι'),       # Ionic active 'show' (Hdt. 6.61) stays
    ('grc', 'δείκνυμι', 'δέξω', 'δείκνυμι'),
    ('grc', 'δείκνυμι', 'δείξας', 'δείκνυμι'),
    ('hom', 'δείκνυμι', 'δεξάμενοι', 'δείκνυμι'),   # rule is for GLAUx automatic lemmas only
    ('byliny', 'старик', 'старухи', 'старуха'),
    ('byliny', 'старик', 'старика', 'старик'),
    ('vuk', 'smeo', 'смела', 'smesti'),
    ('vuk', 'smeće|smeti', 'смеће', 'smesti'),
    ('vuk', 'smeti', 'смем', 'smeti'),
    ('vuk', 'smeo', 'смео', 'smeo'),
])
def test_general_rules_and_their_exceptions(corpus, lemma, surface, expected):
    assert tok(corpus, lemma, surface).lemma == expected


def test_polites_is_a_name_in_homer_only():
    t = tok('hom', 'Πολίτης', 'Πολίτης', 'Il. 15.339')
    assert t.lemma == 'Πολίτης (name)' and t.content is False
    assert tok('hom', 'πολίτης', 'πολῖται').lemma == 'πολίτης'


def test_tara_readings_are_exact_coordinates():
    rows = [r for r in reading_rows() if r['corpus'] == 'sa-ep']
    assert len(rows) == 46
    for r in rows:
        t = tok('sa-ep', r['old'], r['surface'], r['locus'])
        assert t.lemma == 'tārā (name)' and t.content is False
        assert tok('sa-ep', 'tārā', r['surface'], 'MBh, 12, 290.s74').lemma == 'tārā'
    # Ki 21.s1: Tārā 'like a star fallen from the sky' -- only the first token is the name
    assert tok('sa-ep', 'tārā', 'tārām', 'Rām, Ki, 21.s1').lemma == 'tārā'
    assert tok('sa-ep', 'tārā', 'tārābhir', 'Rām, Ki, 11.s56').lemma == 'tārā'


@pytest.mark.parametrize('corpus,lemma,ids', [
    ('lat', 'libra', set()), ('lat', 'papauer', set()), ('lat', 'rideo', set()),
    ('ang', 'fyren', set()), ('hom', 'μέλινος', set()), ('hom', 'μελία', set()),
    ('grp', 'μελία', set()), ('grp', 'Μῆδος', set()),
    ('orv', 'зьрѣти', {'pie-root-gjher-shine'}), ('orv', 'прозьрѣти', {'pie-root-gjher-shine'}),
])
def test_reviewed_lemma_rows_replace_the_automatic_ids(corpus, lemma, ids):
    assert mp.decide(corpus, lemma, {'wrong-auto-root'})[0] == ids


def test_proto_and_key_decisions_reach_every_daughter_word():
    vuk, ru, ccmh = mp.resolve_table('vuk'), mp.resolve_table('byliny'), mp.resolve_table('ccmh')
    for t, w in ((vuk, 'dete'), (vuk, 'deca'), (vuk, 'djeca'), (ru, 'дитя'), (ccmh, 'дѣтищь')):
        assert t[w].ids == {'pie-root-dheh1y-suckle'}, w
    for t, w in ((vuk, 'zrak'), (ru, 'узреть'), (ru, 'презирать'), (ru, 'зрак'), (ccmh, 'зракъ'), (vuk, 'prezreti')):
        assert t[w].ids == {'pie-root-gjher-shine'}, w
    for w in ('отвыкать', 'привыкать'):
        assert ru[w].ids == {'pie-root-h1ewk-become_accustomed'}
    # homonyms and unrelated words keep their mapping
    assert ru['созреть'].ids == {'pie-root-gjerh2-grow_old'}       # ripen
    assert vuk['sazreti'].ids == {'pie-root-gjerh2-grow_old'}
    assert ru['зреть'].ids == {'pie-root-gjerh2-grow_old'}         # ambiguous simplex: undecided
    assert ru['зерно'].ids == {'pie-lex-gjrh2nom'}                 # grain: correct
    assert 'pie-lex-dheh1tis' in mp.resolve_table('cu')['дѣти'].ids  # OCS 'put' page untouched
    assert ru['старуха'].ids == {'pie-lex-sth2ros'}


def test_byliny_material_exclusions_have_exact_boundaries():
    rows = json.loads((CQ / 'material-unit-rules-cq1-other.json').read_text())
    assert len(rows) == 5
    for r in rows:
        name = Path(r['source']).name
        assert mu.excluded_source('byliny', name, r['start']) and mu.excluded_source('byliny', name, r['end'])
    k = 'pesnisobrannyepvkireevskimvyp1pesn13_djvu.txt'
    assert not mu.excluded_source('byliny', k, 23519)        # quoted verse before the essay paragraph
    assert not mu.excluded_source('byliny', 'pesnisobrannyepvkireevskimch2pesni36_djvu.txt', 15998)
    h = 'sbornikotdelenijarusskogojazykaislovesno32_djvu.txt'
    assert not mu.excluded_source('byliny', h, 14523)        # the song itself
    assert not mu.excluded_source('byliny', h, 14478)


def test_ocr_repair_is_local():
    assert mu.reviewed_byliny_text('sbornikotdelenijarusskogojazykaislovesno32:25499', '«Кло мн') == '«Кто мн'
    assert mu.reviewed_byliny_text('sbornikotdelenijarusskogojazykaislovesno32:25500', '«Кло мн') == '«Кло мн'


def test_every_report_and_observation_has_a_verdict():
    expected = set()
    base = ROOT / 'data/research/8c/stageCS'
    lines = {'error-reports-w10.jsonl': {1, 2, 5, 6, 10, 11, 14, 15, 29, 32, 36, 49, 50, 51, 98, 112, 114, 120},
             'error-reports-w11.jsonl': {15, 25, 26, 35, 37, 41, 42, 46, 47, 48, 49, 51}}
    for f, want in lines.items():
        for n, line in enumerate((base / f).read_text().splitlines(), 1):
            if n in want:
                for i in range(1 + len(json.loads(line)['observations'])):
                    expected.add((f, n, i))
    expected |= {('mapping-errors-found.jsonl', 16, 0), ('mapping-errors-found.jsonl', 17, 0)}
    rows = [json.loads(l) for l in (CQ / 'error-verdicts-cq1-other.jsonl').read_text().splitlines()]
    assert {(r['report_file'], r['report_line'], r['observation']) for r in rows} == expected
    assert all(r['verdict'] in {'confirmed', 'already fixed', 'rejected', 'unclear'} and r['evidence']
               and r['action'] and r['current_loader_checked'] for r in rows)
