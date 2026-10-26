"""Wave-3 Norse source repairs, homographs and material boundaries."""
import json
from pathlib import Path

from pie import germanic_new_mapping as gm

ROOT = Path(__file__).resolve().parents[1]


def test_ledger_accounts_for_every_norse_observation():
    expected = set()
    for n, line in enumerate((ROOT / 'data/research/8c/stageCS/error-reports-w3.jsonl').read_text().splitlines(), 1):
        report = json.loads(line)
        for i, obs in enumerate([report] + report.get('observations', [])):
            if obs['error']['passage'].startswith('menota:'):
                expected.add((n, i))
    rows = [json.loads(line) for line in (ROOT / 'data/research/8c/stageCS/error-verdicts-w3-norse.jsonl').read_text().splitlines()]
    assert {(r['report_line'], r['observation']) for r in rows} == expected
    assert len(rows) == len(expected)
    assert all(r['evidence'] and r['verdict'] in {'confirmed', 'rejected', 'unclear', 'already-fixed'} for r in rows)


def test_same_coordinate_hair_and_high_are_distinguished():
    rules = gm.menota_reviewed_tokens(ROOT)
    high = gm.MenotaWord('AM-36-fol', None, '', 'hár', '1', '', None, 0, 0)
    hair = gm.MenotaWord('AM-36-fol', None, '', 'hár', '1', '', None, 0, 1)
    assert gm.reviewed_menota_token(high, 'hár', 'NC', rules) == ('hár', 'NC')
    assert gm.reviewed_menota_token(hair, 'hár', 'NC', rules) == ('hár@hair', 'NC')


def test_material_rules_are_coordinate_guarded_and_preserve_readings(tmp_path):
    xml = tmp_path / gm.MENOTA / 'xml' / 'AM-36-fol.xml'
    xml.parent.mkdir(parents=True)
    rules = tmp_path / 'data/research/formulas/menota-material-w3.json'
    rules.parent.mkdir(parents=True)
    rules.write_bytes((ROOT / rules.relative_to(tmp_path)).read_bytes())
    xml.write_text('<text><pb n="15"/>'
                   '<w><me:dipl>brygiorsverþ</me:dipl></w>'
                   '<pb n="75"/>' + ''.join('<w><me:dipl>' + f + '</me:dipl></w>' for f in
                    ['[siste', 'd', 'kan', 'vere', 'ð]', '[medieval]', 'orð']) +
                   '<pb n="76"/><w><me:dipl>brygiorsverþ</me:dipl></w></text>')
    assert [w.form for w in gm.menota_words(xml, 'AM-36-fol')] == [
        'brygior', 'sverþ', '[medieval]', 'orð', 'brygiorsverþ']


def test_sulphur_join_does_not_join_unrelated_stone(tmp_path):
    xml = tmp_path / gm.MENOTA / 'xml' / 'AM-63-fol.xml'
    xml.parent.mkdir(parents=True)
    rules = tmp_path / 'data/research/formulas/menota-material-w3.json'
    rules.parent.mkdir(parents=True)
    rules.write_bytes((ROOT / rules.relative_to(tmp_path)).read_bytes())
    xml.write_text('<text><pb n="62"/>' + ''.join('<w><me:dipl>' + f + '</me:dipl></w>' for f in
                   ['breno', 'steini', 'steini']) + '</text>')
    assert [w.form for w in gm.menota_words(xml, 'AM-63-fol')] == ['brenosteini', 'steini']


def test_corrected_mapping_excludes_false_homographs():
    table = gm.read_table('menota', ROOT)
    assert table['varmr'] == ('pie-root-gwher-be_warm',)
    assert table['úlfr'] == ('pie-lex-wlkwos',)
    assert table['ǫrn'] == ('pie-lex-h3erox',)
    assert table['vísi@ruler'] == ('pie-root-weyd-see',)
    assert 'hár@hair' not in table and 'raun' not in table and 'væringi' not in table
    assert table['hár'] == ('pie-lex-kowkos-2',)
    assert table['vindr'] == ('pie-lex-h2weh1nts',)
    assert 'danmǫrk (name)' not in table
