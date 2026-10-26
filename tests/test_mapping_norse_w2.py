"""Wave-2 Norse repairs: source-coordinate isolation and homograph guards."""
import json
from pathlib import Path

import pytest

from pie import germanic_new_mapping as gm
from pie import formula_search_multi as fm

ROOT = Path(__file__).resolve().parents[1]


def word(form, doc='example', folio='1r', line='1'):
    return gm.MenotaWord(doc, None, '', form, folio, line, None, 0)


def test_xml_comments_with_internal_tags_do_not_leak(tmp_path):
    p = tmp_path / 'example.xml'
    p.write_text('<text><w><me:dipl><!--<add> editorial </add> -->þa</me:dipl></w>'
                 '<!--<w><me:dipl>spurious</me:dipl></w>-->'
                 '<w><me:dipl>sn&oslashcurl;ri</me:dipl></w></text>')
    assert [w.form for w in gm.menota_words(p, 'example')] == ['þa', 'snøri']


@pytest.mark.parametrize('lemma', ['án', 'bróðir', 'gunnarr', 'Gunnarr', 'Haraldr', 'Mímir'])
def test_names_require_name_annotation(lemma):
    assert gm.reviewed_menota_token(word('x'), lemma, 'NP', {}) == (lemma + ' (name)', 'NP')
    assert gm.reviewed_menota_token(word('x'), lemma, 'NC', {}) == (lemma, 'NC')


def test_source_rules_are_guarded_and_do_not_change_other_loci():
    rules = gm.menota_reviewed_tokens(ROOT)
    for key, r in rules.items():
        w = word(r['form'], r['doc'], r['folio'], r['line'])
        assert gm.reviewed_menota_token(w, r['given_lemma'], '', rules) == (r['lemma'], r['tag'])
        assert gm.reviewed_menota_token(w, '?different', '', rules) == ('?different', '')
        w.line += '-elsewhere'
        assert gm.reviewed_menota_token(w, r['given_lemma'], '', rules) == (r['given_lemma'], '')


def test_local_homograph_senses_have_reviewed_mapping_decisions():
    ov = fm.load_overrides(ROOT)['lemma']['menota']
    assert ov['vega@slay'][0] == {'pie-lex-wiketi'}
    assert ov['minni@memory'][0] == {'pie-root-men-think'}
    assert ov['svelgja'][0] == {'pie-root-swel-swallow'}
    assert ov['rjóða'][0] == {'pie-root-h1rewdh-red'}
    for lemma in ('iarn', 'járn', 'tún', 'grund', 'gegna', 'gler', 'skaði', 'selja@willow'):
        assert not ov[lemma][0]


def test_review_applies_after_inference_without_contaminating_votes(tmp_path, monkeypatch):
    xml = tmp_path / gm.MENOTA / 'xml'
    xml.mkdir(parents=True)
    (xml / 'seed.xml').write_text('<text>' +
        '<w lemma="ǫl" me:msa="xNC"><me:dipl>ol</me:dipl></w>' * 3 + '</text>')
    (xml / 'AM-242-fol.xml').write_text(
        '<text><pb n="155"/><lb n="27"/>'
        '<w><me:dipl>ol</me:dipl></w><lb n="28"/>'
        '<w><me:dipl>ol</me:dipl></w></text>')
    rules = tmp_path / 'data/research/formulas/menota-reviewed-w2.json'
    rules.parent.mkdir(parents=True)
    rules.write_bytes((ROOT / rules.relative_to(tmp_path)).read_bytes())
    monkeypatch.setattr(gm, 'menota_documents', lambda *a: [('seed', {}), ('AM-242-fol', {})])
    ts = gm.load_menota(tmp_path)
    assert [(t.lemma, t.pos) for t in ts] == [('ǫl', 'noun')] * 3 + [('ala', 'verb'), ('ǫl', 'noun')]
    assert ts[-2].units['lemma_source'] == 'reviewed'
    assert ts[-1].units['lemma_source'] == 'form-table'


def test_regenerated_table_contains_only_reviewed_senses():
    table = gm.read_table('menota', ROOT)
    assert table['vega@slay'] == ('pie-lex-wiketi',)
    assert table['rjóða'] == ('pie-root-h1rewdh-red',)
    assert table['hræ'] == ('pie-root-krewh2-blood_outside_the',)
    assert 'pie-lex-wegjheti' in table['vega']  # Other verb senses remain available.
    assert table['bróðir'] == ('pie-lex-bhreh2texr',)  # Common kinship noun survives.
    assert 'Gunnarr' not in table and 'gunnarr' not in table


def test_ledger_covers_every_norse_observation():
    reports = ROOT / 'data/research/8c/stageCS/error-reports-w2.jsonl'
    expected = set()
    for n, line in enumerate(reports.read_text().splitlines(), 1):
        d = json.loads(line)
        for i, obs in enumerate([d] + d.get('observations', [])):
            if 'menota:' in obs.get('error', {}).get('passage', ''):
                expected.add((n, i))
    ledger = [json.loads(l) for l in (ROOT / 'data/research/8c/stageCS/error-verdicts-w2-norse.jsonl').read_text().splitlines()]
    assert {(r['report_line'], r['observation']) for r in ledger} == expected
    assert len(ledger) == len(expected)
    assert all(r['evidence'] and r['verdict'] in {'confirmed', 'rejected', 'unclear', 'already-fixed'} for r in ledger)
