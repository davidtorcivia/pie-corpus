"""Wave-9 source-coordinate repairs and source morphology safeguards."""
import collections
import json

from pie import germanic_new_mapping as gm, mapping as mp


def test_every_norse_report_has_independent_evidence():
    base = gm.ROOT / 'data/research/8c/stageCS'
    expected = set()
    for n, line in enumerate((base / 'error-reports-w9.jsonl').read_text().splitlines(), 1):
        report = json.loads(line)
        for i, obs in enumerate([report] + report.get('observations', [])):
            if obs['error']['passage'].split(':')[0] in {'menota', 'icepahc', 'non'}:
                expected.add((n, i))
    rows = [json.loads(line) for line in (base / 'error-verdicts-w9-norse.jsonl').read_text().splitlines()]
    reports = [r for r in rows if r['report_file'] == 'error-reports-w9.jsonl']
    assert len(reports) == len(expected) == 29
    assert {(r['report_line'], r['observation']) for r in reports} == expected
    assert all(r['source_tokens'] and r['current'] and r['dictionary_refs'] and r['evidence'] for r in rows)
    assert all(r['verdict'] in {'confirmed', 'rejected', 'unclear', 'already-fixed'} for r in rows)


def test_man_requires_source_noun_gender_and_preserves_both_verbs_and_bondfolk():
    for lemma in ('maðr', 'muna', 'munu', 'man'):
        assert gm.reviewed_menota_lemma(lemma, 'xNC nS gM cA', 'man') == 'maðr'
    for lemma in ('muna', 'munu'):
        assert gm.reviewed_menota_lemma(lemma, 'xVB p3 nS', 'man') == lemma
        assert gm.reviewed_menota_lemma(lemma, '', 'man') == lemma
    assert gm.reviewed_menota_lemma('man', 'xNC nS gN cA', 'man') == 'man'
    w = gm.MenotaWord('doc', None, '', 'man', '1', '1', None, 0)
    assert gm.reviewed_menota_token(w, 'munu', 'NC', {}) == ('munu', 'NC')


def test_dyr_needs_gender_because_both_senses_are_nouns():
    assert gm.reviewed_menota_lemma('dýr', 'xNC nP gF cN', 'dyr') == 'dyrr'
    assert gm.reviewed_menota_lemma('dyr', 'xNC nP gN cN', 'dyr') == 'dýr'
    assert gm.reviewed_menota_lemma('dýr', 'xNC', 'dyr') == 'dýr'
    assert gm.reviewed_menota_lemma('dýrr', 'xAJ nS gF', 'dyr') == 'dýrr'
    assert gm.reviewed_menota_lemma(None, '', 'dyr') is None
    w = gm.MenotaWord('doc', None, '', 'dyr', '1', '1', None, 0)
    assert gm.reviewed_menota_token(w, 'dýr', 'NC', {}) == ('dýr', 'NC')


def test_local_reviews_guard_occurrence_and_divine_exemption():
    rules = gm.menota_reviewed_tokens()
    w = gm.MenotaWord('AM-56-4to', None, '', 'man', '27v', '22', None, 0, 1)
    assert gm.reviewed_menota_token(w, 'munu', 'VB', rules) == ('maðr', 'NC')
    w.occurrence = 0
    assert gm.reviewed_menota_token(w, 'munu', 'VB', rules) == ('munu', 'VB')
    assert gm.annotated_norse_lemma('óðr', 'NP') == 'óðr'
    w = gm.MenotaWord('AM-242-fol', None, '', 'oðs', '55', '4', None, 0)
    assert gm.reviewed_menota_token(w, 'óðr', 'AJ', rules) == ('óðr', 'NP')


def test_mapping_senses_and_diff_are_limited():
    rows = mp.resolve_rows('menota', mp.read_table('menota'), mp.load_overrides())
    assert rows['samkvǽði'].ids == {'pie-root-gwet-say'}
    assert rows['samkvǽði'].formation == 'derivative'
    assert 'viti@beacon' not in rows
    assert 'stefna@summons' not in rows
    base = gm.ROOT / 'data/research/8c/stageCS'
    diff = [json.loads(l) for l in (base / 'norse-token-diff-w9.jsonl').read_text().splitlines()]
    summary = json.loads((base / 'norse-token-diff-w9-summary.json').read_text())
    assert summary['changed_tokens'] == len(diff)
    assert summary['by_corpus'] == dict(collections.Counter(r['corpus'] for r in diff))
    assert set(summary['by_corpus']) == {'menota'}
    for form in ('man', 'dyr'):
        assert len(summary['samples'][form]) == 30
        assert all(r['form'].lower() == form for r in summary['samples'][form])
    assert summary['whole_corpus_counts']['icepahc']['man']['before'] == summary['whole_corpus_counts']['icepahc']['man']['after']
