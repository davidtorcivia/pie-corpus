"""Corpus-quality batch 1, Norse: source-coordinate and source-morphology regressions."""
import json

import pytest

from pie import germanic_new_mapping as gm, mapping as mp

CQ = gm.ROOT / 'data/research/8c/corpus-quality'


def test_tunga_after_a_preposition_is_the_farm():
    for prev in ('í', 'Í', 'til', 'ór', 'gegnt'):
        assert gm.reviewed_menota_lemma('tunga', 'xNC nS gF cD', 'Tungu', 'AM-132-fol-Laxdaela-saga', prev) == 'tunga (name)'
    # the organ: line-initial definite form, lower case, or no preposition
    assert gm.reviewed_menota_lemma('tunga', 'xNC nS gF cN', 'Tungan', 'AM-619-4to', 'sár') == 'tunga'
    assert gm.reviewed_menota_lemma('tunga', 'xNC nS gF cA', 'tungu', 'DG-8-OHleg', 'oc') == 'tunga'
    assert gm.reviewed_menota_lemma('tunga', 'xNC nS gF cA', 'Tungu', 'X', 'hans') == 'tunga'


def test_wends_and_lawspeaker_byname():
    assert gm.reviewed_menota_lemma('vindr', 'xNC nP gM cN', 'vindir', 'DG-8-OHleg') == 'vindr (name)'
    assert gm.reviewed_menota_lemma('vindr', 'xNC nP gM cN', 'vindar', 'DG-8-OHleg') == 'vindr'
    assert gm.reviewed_menota_lemma('máni', 'xNC', 'máni', 'AM-113-b-fol', 'Þorkell') == 'máni (name)'
    assert gm.reviewed_menota_lemma('máni', 'xNC', 'máni', 'AM-113-b-fol', 'Þorkels') == 'máni (name)'
    assert gm.reviewed_menota_lemma('máni', 'xNC', 'máni', 'GKS-2365-4to-Vsp', 'sól') == 'máni'


@pytest.mark.parametrize('lemma,form,folio,initial,expected', [
    ('finna', 'Finnr', '110', False, 'finnr (name)'), ('finna', 'Finnz', '111', False, 'finnr (name)'),
    ('finna', 'finnr', '110', False, None), ('finna', 'Finnaz', '27v', False, None),
    ('finna', 'Finnr', '121', True, None),
    ('dagr', 'Dagr', '406', False, 'dagr (name)'), ('dagr', 'Dagh', '28r', False, None),
    ('dagr', 'Dagr', '259', False, None),                       # exception
    ('haukr', 'Haucr', '351', False, 'haukr (name)'), ('bera', 'Bera', '32', False, 'bera (name)'),
    ('bera', 'Bar', '325', False, None), ('maðr', 'Menn', '1', False, None),
])
def test_unlemmatised_name_forms(lemma, form, folio, initial, expected):
    doc = 'AM-63-fol' if folio == '259' else 'AM-35-fol'
    assert gm.unlemmatized_name(lemma, form, doc, folio, initial) == expected


def test_icepahc_married_participle():
    assert gm.annotated_norse_lemma('átta', 'VAN-A', 'icepahc') == 'eiga'
    assert gm.annotated_norse_lemma('átta', 'NUM-N', 'icepahc') == 'átta'
    assert gm.annotated_norse_lemma('átta', 'ADJ-N', 'icepahc') == 'átta'


def test_veginn_coordinate_repair_is_local():
    rules = gm.menota_reviewed_tokens()
    w = gm.MenotaWord('AM-132-fol-Njals-saga', 'vega', 'VB', 'veginn', '42v', '35', None, 0, 0)
    assert gm.reviewed_menota_token(w, 'vega', 'VB', rules) == ('vega@slay', 'VB')
    w.line = '36'
    assert gm.reviewed_menota_token(w, 'vega', 'VB', rules) != ('vega@slay', 'VB')


def test_mapping_decisions():
    for c in ('menota', 'icepahc'):
        assert 'fleinn' not in mp.resolve_table(c)            # *flainaz < *(s)pel- 'split', not 'say'
    assert 'for' not in mp.resolve_table('menota')
    assert mp.resolve_table('menota')['vega@slay'].ids == {'pie-lex-wiketi'}
    assert mp.resolve_table('menota')['tunga'].ids == {'pie-lex-dngjhweh2s'}


@pytest.fixture(scope='module')
def menota():
    return {(t.locus, t.surface): t for t in gm.load_menota()}


@pytest.mark.parametrize('locus,form,lemma,content', [
    ('AM-63-fol 110:', 'Finnr', 'finnr (name)', False),
    ('AM-36-fol 406:29', 'Dagr', 'dagr (name)', False),
    ('AM-35-fol 32:', 'Bera', 'bera (name)', False),
    ('AM-35-fol 351:', 'Haucr', 'haukr (name)', False),
    ('AM-132-fol-Laxdaela-saga 191r:33', 'Tungu', 'tunga (name)', False),
    ('AM-162-B-fol-kappa 2r:11', 'Tungu', 'tunga (name)', False),
    ('AM-132-fol-Njals-saga 42v:35', 'veginn', 'vega@slay', True),
    ('DG-8-OHleg 0102:1', 'vindir', 'vindr (name)', False),
    ('AM-113-b-fol 4r:19', 'máni', 'máni (name)', False),
    ('AM-619-4to 118:14', 'Tungan', 'tunga', True),
    ('AM-242-fol 27:12', 'ottu', 'ótta', True),
])
def test_production_loader(menota, locus, form, lemma, content):
    t = menota[(locus, form)]
    assert (t.lemma, t.content) == (lemma, content)


def test_every_norse_report_has_a_verdict():
    base = gm.ROOT / 'data/research/8c/stageCS'
    want = {'error-reports-w10.jsonl': {8, 52, 53, 56, 100}, 'error-reports-w11.jsonl': {10, 18, 22, 24, 32, 34, 36, 43}}
    expected = set()
    for f, lines in want.items():
        for n, line in enumerate((base / f).read_text().splitlines(), 1):
            if n in lines:
                expected |= {(f, n, i) for i in range(1 + len(json.loads(line)['observations']))}
    rows = [json.loads(l) for l in (CQ / 'error-verdicts-cq1-norse.jsonl').read_text().splitlines()]
    assert {(r['report_file'], r['report_line'], r['observation']) for r in rows} == expected
    assert all(r['verdict'] in {'confirmed', 'already fixed', 'rejected', 'unclear'} and r['evidence']
               and r['current_loader_checked'] for r in rows)
