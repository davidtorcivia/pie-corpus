"""Source-local Norse wave-4 repairs and homograph regressions."""
import json
from pathlib import Path

from pie import germanic_new_mapping as gm

ROOT = Path(__file__).resolve().parents[1]


def test_ledger_accounts_for_every_norse_observation():
    expected = set()
    for file in ('error-reports-w4.jsonl', 'error-reports-search.jsonl'):
        for n, line in enumerate((ROOT / 'data/research/8c/stageCS' / file).read_text().splitlines(), 1):
            report = json.loads(line)
            for i, obs in enumerate([report] + report.get('observations', [])):
                e = obs.get('error', obs)
                if e.get('passage', '').startswith(('menota:', 'icepahc:', 'edda:')) or e.get('corpus') == 'Old Norse':
                    expected.add((file, n, i))
    rows = [json.loads(line) for line in (ROOT / 'data/research/8c/stageCS/error-verdicts-w4-norse.jsonl').read_text().splitlines()]
    assert {(r['report_file'], r['report_line'], r['observation']) for r in rows} == expected
    assert len(rows) == len(expected)
    assert all(r['evidence'] and r['verdict'] in {'confirmed', 'rejected', 'unclear', 'already-fixed'} for r in rows)


def test_name_guard_uses_annotation_and_preserves_common_words():
    rules = gm.menota_reviewed_tokens(ROOT)
    word = gm.MenotaWord('unrelated', None, '', 'Finnr', '1', '2', None, 0)
    for lemma in ('Einarr', 'Sveinn', 'Finnr', 'alfr', 'Ósló'):
        assert gm.reviewed_menota_token(word, lemma, 'NP', rules) == (lemma + ' (name)', 'NP')
        assert gm.reviewed_menota_token(word, lemma, 'NC', rules) == (lemma, 'NC')
    assert gm.reviewed_menota_token(word, 'Baldr', 'NP', rules) == ('Baldr', 'NP')


def test_hair_and_high_in_same_passage_stay_separate():
    rules = gm.menota_reviewed_tokens(ROOT)
    high = gm.MenotaWord('DG-8-OHleg', 'hár', 'AJ', 'haR', '0027', '27', None, 0)
    hair = gm.MenotaWord('DG-8-OHleg', 'hár', 'NC', 'har', '0027', '28', None, 0)
    assert gm.reviewed_menota_token(high, 'hár', 'AJ', rules) == ('hár', 'AJ')
    assert gm.reviewed_menota_token(hair, 'hár', 'NC', rules) == ('hár@hair', 'NC')
    hair.line = '29'
    assert gm.reviewed_menota_token(hair, 'hár', 'NC', rules) == ('hár', 'NC')


def test_material_repairs_are_coordinate_and_sequence_guarded(tmp_path):
    repairs = tmp_path / 'data/research/formulas/menota-material-w4.json'
    repairs.parent.mkdir(parents=True)
    repairs.write_bytes((ROOT / repairs.relative_to(tmp_path)).read_bytes())
    xml = tmp_path / gm.MENOTA / 'xml/AM-78-4to.xml'
    xml.parent.mkdir(parents=True)
    xml.write_text('<text><pb n="65r"/><lb n="10"/>'
                   '<w><me:dipl>man</me:dipl></w><w><me:dipl>mærgð</me:dipl></w>'
                   '<w><me:dipl>man</me:dipl></w><w><me:dipl>orð</me:dipl></w>'
                   '<lb n="11"/><w><me:dipl>man</me:dipl></w>'
                   '<w><me:dipl>mærgð</me:dipl></w></text>')
    assert [w.form for w in gm.menota_words(xml, 'AM-78-4to')] == [
        'manmærgð', 'man', 'orð', 'man', 'mærgð']
    xml.write_text('<text><pb n="292"/><w><me:dipl>barnøogon;sco</me:dipl></w>'
                   '<pb n="293"/><w><me:dipl>barnøogon;sco</me:dipl></w></text>')
    assert [w.form for w in gm.menota_words(xml, 'AM-63-fol')] == ['barnǫsco', 'barnøogon;sco']


def test_sense_mappings_and_rejected_reports():
    table = gm.read_table('menota', ROOT)
    assert table['kvæði'] == ('pie-root-gwet-say',)
    assert table['siǫt'] == ('pie-root-sed-sit',)
    assert table['vega@slay'] == ('pie-lex-wiketi',)
    assert table['vit@understanding'] == ('pie-lex-weydos',)
    assert table['fǫr@journey'] == ('pie-root-per-go_through',)
    assert table['vanr@accustomed'] == ('pie-root-wenh1-love',)
    for lemma in ('ákall', 'œrr', 'lund@manner', 'gerð@act', 'ber@berry', 'sál@soul'):
        assert lemma not in table
    assert table['munnr'] == ('pie-lex-mntos-2',)
    assert table['veita'] == ('pie-lex-woydeyeti',)
    assert table['Baldr'] == ('pie-lex-bholtos',)
    assert table['nótt'] == ('pie-lex-nokwts',)
    assert table['fara'] == ('pie-root-per-go_through',)
