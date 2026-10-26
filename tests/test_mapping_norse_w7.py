"""Wave-7 name-vote propagation, reviewed exceptions and formation precision."""
import json
import collections
import random

from pie import germanic_new_mapping as gm, mapping as mp, tier2_secure as secure


def word(lemma=None, tag='', form='Ulfr'):
    return gm.MenotaWord('doc', lemma, tag, form, '1r', '2', None, 0)


def test_winning_np_tag_propagates_without_changing_common_word_votes():
    w = word()
    assert gm.reviewed_menota_token(w, 'ulfr', 'NP', {}) == ('ulfr (name)', 'NP')
    assert gm.reviewed_menota_token(w, 'ulfr', 'NC', {}) == ('ulfr', 'NC')
    assert gm.reviewed_menota_token(w, 'þórr', 'NP', {}) == ('þórr', 'NP')
    rules = {('doc', '1r', '2', 'Ulfr'): {'given_lemma': 'ulfr', 'lemma': 'ulfr', 'tag': 'NC'}}
    assert gm.reviewed_menota_token(w, 'ulfr', 'NP', rules) == ('ulfr', 'NC')


def test_personal_homographs_do_not_pass_the_theonym_exemption():
    for lemma, tag, corpus in [('hjǫrtr', 'NP', 'menota'), ('jökull', 'NPR-N', 'icepahc')]:
        assert gm.annotated_norse_lemma(lemma, tag, corpus) == lemma + ' (name)'
        assert gm.annotated_norse_lemma(lemma + ' (name)', tag, corpus) == lemma + ' (name)'
        assert gm.annotated_norse_lemma(lemma, 'NC', corpus) == lemma


def test_form_table_uses_the_winning_lemma_and_tag_together(tmp_path, monkeypatch):
    monkeypatch.setattr(gm, 'menota_documents', lambda *a: [('annotated', {}), ('inferred', {})])
    def words(path, doc):
        if doc == 'annotated':
            return [gm.MenotaWord(doc, 'ulfr', 'NP', 'Ulfr', '1r', str(i), None, 0) for i in range(3)]
        return [gm.MenotaWord(doc, None, '', 'Ulfr', '2r', '1', None, 0)]
    monkeypatch.setattr(gm, 'menota_words', words)
    toks = gm.load_menota(tmp_path)
    assert len(toks) == 4
    assert toks[-1].lemma == 'ulfr (name)' and toks[-1].units['tag'] == 'NP'
    assert not toks[-1].content and toks[-1].pos == 'noun'


def test_all_w7_norse_reports_have_independent_verdicts():
    base = gm.ROOT / 'data/research/8c/stageCS'
    expected = set()
    for n, line in enumerate((base / 'error-reports-w7.jsonl').read_text().splitlines(), 1):
        r = json.loads(line)
        for i, x in enumerate([r] + r.get('observations', [])):
            if x['error']['passage'].split(':')[0] in {'menota', 'icepahc', 'non'}:
                expected.add((n, i))
    rows = [json.loads(l) for l in (base / 'error-verdicts-w7-norse.jsonl').read_text().splitlines()]
    reports = [r for r in rows if 'report_line' in r]
    assert {(r['report_line'], r['observation']) for r in reports} == expected
    assert len(reports) == len(expected)
    assert all(r['source_tokens'] and r['current'] and r['dictionary_refs'] and r['evidence'] for r in reports)
    assert next(r for r in reports if (r['report_line'], r['observation']) == (33, 1))['verdict'] == 'already-fixed'
    assert next(r for r in reports if r['report_line'] == 36)['verdict'] == 'rejected'


def test_compound_decisions_cap_every_exact_route_but_preserve_ids():
    entries = {r['id']: r for r in map(json.loads, (gm.ROOT / 'data/lexicon/lexicon.jsonl').read_text().splitlines())}
    ov = mp.load_overrides()
    rows = {c: mp.read_table(c) for c in ('menota', 'icepahc', 'non')}
    checker = secure.SecureChecker.from_population(entries, secure.build_population(rows, ov))
    for corpus, lemma in [('menota', 'helvíti'), ('icepahc', 'rannsaka'), ('non', 'valhöll'), ('menota', 'borgar-maðr')]:
        r = mp.resolve_rows(corpus, rows[corpus], ov)[lemma]
        assert r.formation == 'derivative' and len(r.ids) == 1
        hit = checker.match(next(iter(r.ids)), 'non', 'Old Norse', lemma, True)
        assert hit and hit['level'] == 'root'
    for c in ('menota', 'icepahc', 'non'):
        r = mp.resolve_rows(c, rows[c], ov).get('þórr')
        if r:
            assert checker.match(next(iter(r.ids)), 'non', 'Old Norse', 'þórr', True)['level'] == 'exact'
    # A compound's cap must not become a decision on its standalone member.
    menota = mp.resolve_rows('menota', rows['menota'], ov)
    assert menota['borgar-maðr'].word == 'borgar-maðr'
    for lemma in ('maðr', 'faðir', 'steinn', 'rauðr'):
        r = menota[lemma]
        assert checker.match(next(iter(r.ids)), 'non', 'Old Norse', lemma, True)['level'] == 'exact'


def test_whole_corpus_diff_samples_and_reviewed_names_are_preserved():
    base = gm.ROOT / 'data/research/8c/stageCS'
    diff = [json.loads(l) for l in (base / 'norse-token-diff-w7.jsonl').read_text().splitlines()]
    summary = json.loads((base / 'norse-token-diff-w7-summary.json').read_text())
    assert summary['changed_tokens'] == len(diff)
    assert summary['counts_per_rule'] == dict(collections.Counter(r['rule'] for r in diff))
    for rule, n in summary['counts_per_rule'].items():
        population = [r for r in diff if r['rule'] == rule]
        assert summary['samples_per_rule'][rule] == random.Random(7).sample(population, min(30, n))
    assert all(not r['old']['lemma'].endswith(' (name)') or r['new']['lemma'].endswith(' (name)') for r in diff)
