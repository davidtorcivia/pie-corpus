"""Wave-5 source-local senses, name isolation and TEI numeral context."""
import json
from pathlib import Path

import pytest

from pie import germanic_new_mapping as gm

ROOT = Path(__file__).resolve().parents[1]


def test_ledger_accounts_for_all_norse_observations():
    expected = set()
    for file in ('error-reports-w5.jsonl', 'error-reports-search-w5.jsonl'):
        for n, line in enumerate((ROOT / 'data/research/8c/stageCS' / file).read_text().splitlines(), 1):
            report = json.loads(line)
            for i, obs in enumerate([report] + report.get('observations', [])):
                e = obs.get('error', obs)
                if e.get('passage', '').startswith(('menota:', 'icepahc:', 'edda:')):
                    expected.add((file, n, i))
    rows = [json.loads(l) for l in (ROOT / 'data/research/8c/stageCS/error-verdicts-w5-norse.jsonl').read_text().splitlines()]
    assert len(rows) == len(expected) == 51
    assert {(r['report_file'], r['report_line'], r['observation']) for r in rows} == expected
    assert all(r['evidence'] and r['current'] and r['source'] for r in rows)
    assert next(r for r in rows if r['report_line'] == 64)['verdict'] == 'unclear'


@pytest.mark.parametrize('lemma', ['Áki', 'Bjǫrn', 'hringr', 'ormr'])
def test_names_require_source_np_annotation(lemma):
    w = gm.MenotaWord('unrelated', lemma, 'NP', lemma, '1', '1', None, 0)
    assert gm.reviewed_menota_token(w, lemma, 'NP', {}) == (lemma + ' (name)', 'NP')
    assert gm.reviewed_menota_token(w, lemma, 'NC', {}) == (lemma, 'NC')


def test_local_homonyms_do_not_change_unreviewed_occurrences():
    rules = gm.menota_reviewed_tokens(ROOT)
    w = gm.MenotaWord('HolmPerg-30-4to', None, '', 'man', '84v', '18', None, 0)
    assert gm.reviewed_menota_token(w, 'munu', 'VB', rules) == ('maðr', 'NC')
    w.line = '19'
    assert gm.reviewed_menota_token(w, 'munu', 'VB', rules) == ('munu', 'VB')
    w = gm.MenotaWord('AM-35-fol', None, '', 'goða', '209', '', None, 0)
    assert gm.reviewed_menota_token(w, 'góðr', 'AJ', rules) == ('goð', 'NC')
    w.occurrence = 1
    assert gm.reviewed_menota_token(w, 'góðr', 'AJ', rules) == ('góðr', 'AJ')


@pytest.mark.parametrize('annotated', [False, True])
def test_tei_numbers_survive_without_lexical_evidence_or_false_boundaries(tmp_path, monkeypatch, annotated):
    path = tmp_path / gm.MENOTA / 'xml/test.xml'
    path.parent.mkdir(parents=True)
    attrs = ' lemma="vetr" me:msa="xNC"' if annotated else ''
    path.write_text('<text><pb n="1r"/><lb n="2"/>'
                    '<num type="cardinal" value="15"><me:norm>15</me:norm>'
                    '<me:dipl>xv<pc>.</pc></me:dipl></num>'
                    f'<w{attrs}><me:norm>vetra</me:norm></w>'
                    '<pc>.</pc><w' + attrs + '><me:norm>vetra</me:norm></w></text>')
    words = gm.menota_words(path, 'test')
    assert [w.form for w in words] == ['15', 'vetra', 'vetra']
    assert words[0].sent == words[1].sent
    assert words[2].sent == words[1].sent + 1
    monkeypatch.setattr(gm, 'menota_documents', lambda *a: [('test', {})])
    tokens = gm.load_menota(tmp_path)
    assert tokens[0].surface == '15'
    assert tokens[0].units['tag'] == 'MC'
    assert not tokens[0].content
    assert tokens[1].units['lemma_source'] == ('corpus' if annotated else 'unknown')


def test_verified_source_numbers_and_deleted_letter():
    words = gm.menota_words(ROOT / gm.MENOTA / 'xml/HolmPerg-34-4to-MLL.xml', 'HolmPerg-34-4to-MLL')
    for folio, line, number, following in [('24v', '22', '3', 'nǽtr'), ('10v', '12', '8', 'ørtogum'),
                                          ('10v', '13', '13', 'mǫrkum'), ('10v', '27', '4', 'mǫrkum'),
                                          ('43v', '26', '15', 'vetra')]:
        matches = [(i, w) for i, w in enumerate(words) if (w.folio, w.line, w.form, w.msa) == (folio, line, number, 'MC')]
        assert len(matches) == 1
        i, w = matches[0]
        assert words[i + 1].form == following
        assert words[i + 1].sent == w.sent
    words = gm.menota_words(ROOT / gm.MENOTA / 'xml/HolmPerg-4-fol.xml', 'HolmPerg-4-fol')
    assert any((w.folio, w.line, w.form, w.lemma) == ('2-291', '31', 'hann', 'hann') for w in words)
    assert not any((w.folio, w.line, w.form) == ('2-291', '31', 'hrann') for w in words)


def test_dictionary_checked_mappings_and_qualified_reports():
    table = gm.read_table('menota', ROOT)
    assert table['ulfr'] == table['úlfr'] == ('pie-lex-wlkwos',)
    assert table['hlýða'] == table['hljóð'] == ('pie-root-kjlew-hear',)
    assert table['risi'] == ('pie-root-wers-rise',)
    assert table['danskr'] == ('pie-lex-dhonh2is',)
    assert table['vísi@ruler'] == ('pie-root-weyd-see',)
    for lemma in ('hnefi', 'iáta', 'hluta', 'sýni', 'síða@side', 'austr@bailing', 'kórr'):
        assert lemma not in table
    # The corresponding common words and verbs still retain their readings.
    assert table['nefi'] == ('pie-lex-nepoxts',)
    assert table['síða'] == ('pie-lex-seyteti',)
    assert table['ormr'] == ('pie-lex-wrmis',)
