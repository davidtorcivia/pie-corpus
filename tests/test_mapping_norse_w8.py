"""Wave-8 independently reviewed Norse homonyms and cautious NP inference."""
import collections
import json

from pie import germanic_new_mapping as gm, mapping as mp


def test_lowercase_competing_common_votes_abstain_but_source_and_reviews_win():
    votes = collections.Counter({('már', 'NP'): 44, ('marr', 'NC'): 3})
    w = gm.MenotaWord('doc', None, '', 'mar', '1r', '1', None, 0)
    assert gm.reviewed_menota_token(w, 'már', 'NP', {}, votes) == ('?mar', '')
    w.form = 'Mar'
    assert gm.reviewed_menota_token(w, 'már', 'NP', {}, votes)[1] == 'NP'
    w.form = 'mar'
    w.lemma, w.msa = 'már', 'NP'
    assert gm.reviewed_menota_token(w, 'már', 'NP', {}, votes)[1] == 'NP'
    w.lemma, w.msa = None, ''
    rules = {('doc', '1r', '1', 'mar'): {'given_lemma': 'már', 'lemma': 'marr', 'tag': 'NC'}}
    assert gm.reviewed_menota_token(w, 'már', 'NP', rules, votes) == ('marr', 'NC')
    votes['marr', 'NC'] = 2
    assert gm.reviewed_menota_token(w, 'már', 'NP', {}, votes)[1] == 'NP'
    assert gm.reviewed_menota_token(w, 'már', 'NP', {}, collections.Counter({('már','NP'):44, ('mar','FW'):3}))[1] == 'NP'


def test_loader_abstention_preserves_source_annotation_and_uppercase(tmp_path, monkeypatch):
    monkeypatch.setattr(gm, 'menota_documents', lambda *a: [('annotated', {}), ('inferred', {})])
    def words(path, doc):
        if doc == 'annotated':
            return [gm.MenotaWord(doc, 'már', 'NP', 'mar', '1r', str(i), None, 0) for i in range(9)] + [
                gm.MenotaWord(doc, 'marr', 'NC', 'mar', '1r', str(i + 9), None, 0) for i in range(3)]
        return [gm.MenotaWord(doc, None, '', form, '2r', str(i), None, 0) for i, form in enumerate(('mar','Mar'))]
    monkeypatch.setattr(gm, 'menota_words', words)
    ts = gm.load_menota(tmp_path)
    assert ts[-2].lemma == '?mar' and ts[-2].units['lemma_source'] == 'unknown'
    assert ts[-2].content and ts[-2].units['tag'] == ''
    assert ts[-1].units['tag'] == 'NP'
    assert all(t.units['tag'] == 'NP' for t in ts[:9])


def test_reviewed_personal_names_do_not_change_common_homographs_or_theonyms():
    for lemma, tag, corpus in [('unnr','NP','menota'), ('vagn','NP','menota'),
                               ('hafr','NP','menota'), ('barði','NPR-N','icepahc'), ('ormur','NPR-N','icepahc')]:
        assert gm.annotated_norse_lemma(lemma, tag, corpus) == lemma + ' (name)'
        assert gm.annotated_norse_lemma(lemma + ' (name)', tag, corpus) == lemma + ' (name)'
        assert gm.annotated_norse_lemma(lemma, 'NC', corpus) == lemma
    assert gm.annotated_norse_lemma('Hǫðr', 'NP') == 'Hǫðr'
    assert gm.annotated_norse_lemma('þórr', 'NP') == 'þórr'


def test_every_norse_report_and_observation_has_evidenced_verdict():
    base = gm.ROOT / 'data/research/8c/stageCS'
    expected = set()
    for n, line in enumerate((base / 'error-reports-w8.jsonl').read_text().splitlines(), 1):
        r = json.loads(line)
        for i, obs in enumerate([r] + r.get('observations', [])):
            if obs['error']['passage'].split(':')[0] in {'menota','icepahc','non'}:
                expected.add((n,i))
    ledger = [json.loads(l) for l in (base / 'error-verdicts-w8-norse.jsonl').read_text().splitlines()]
    reports = [r for r in ledger if r['report_file'] == 'error-reports-w8.jsonl']
    assert {(r['report_line'],r['observation']) for r in reports} == expected
    assert len(reports) == len(expected)
    assert all(r['source_tokens'] and r['current'] and r['dictionary_refs'] and r['evidence'] for r in reports)
    queued = {r['report_line']:r for r in ledger if r['report_file']=='error-reports-search-w8.jsonl'}
    assert queued[2]['verdict'] == 'deferred'
    assert queued[3]['verdict'] == 'confirmed'


def test_reviewed_senses_exclude_wrong_homographs_and_cap_derivatives():
    ov = mp.load_overrides()
    rs = mp.resolve_rows('menota',mp.read_table('menota'),ov)
    assert 'fat@clothes' not in rs
    assert 'stefna@summon' not in rs
    assert rs['nyt@yield'].ids == {'pie-root-newd-use'}
    assert rs['sá@demonstrative'].ids == {'pie-lex-so'}
    assert rs['vist@provisions'].ids == {'pie-root-wes-graze'}
    for lemma in ('hamarr','máttr','sókn','goði','gerði'):
        assert rs[lemma].formation == 'derivative'


def test_token_diff_guard_counts_and_local_material_repairs():
    base = gm.ROOT / 'data/research/8c/stageCS'
    diff = [json.loads(l) for l in (base/'norse-token-diff-w8.jsonl').read_text().splitlines()]
    summary = json.loads((base/'norse-token-diff-w8-summary.json').read_text())
    assert summary['changed_tokens'] == len(diff)
    assert summary['counts_per_rule'] == dict(collections.Counter(r['rule'] for r in diff))
    guard = [r for r in diff if r['rule']=='inferred-NP-abstention']
    assert len(guard) == summary['inferred_np_guard']['before']
    assert summary['inferred_np_guard']['after'] == 0
    assert all(r['form'].islower() and r['old']['tag']=='NP' and r['new']['lemma'].startswith('?') for r in guard)
    assert any(r['form']=='mar' for r in guard)
    repairs = json.loads((gm.ROOT/'data/research/formulas/menota-material-w8.json').read_text())
    assert len(repairs)==3
    assert next(r for r in repairs if r['forms']==['hannstað'])['replacement']==['hann','stað']
    assert all(r['citation'] and r['doc']=='AM-36-fol' for r in repairs)
