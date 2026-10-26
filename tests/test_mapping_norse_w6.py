"""Source-tag rules and narrowly guarded wave-6 Norse repairs."""
import json
from pathlib import Path

import pytest

from pie import germanic_new_mapping as gm
from pie import formula_search_multi as fm
from pie.material_units import reviewed_edda_lemma


def test_verdict_ledger_covers_all_norse_reports_and_observations():
    base = gm.ROOT / 'data/research/8c/stageCS'
    expected = set()
    for n, line in enumerate((base / 'error-reports-w6.jsonl').read_text().splitlines(), 1):
        report = json.loads(line)
        for i, observation in enumerate([report] + report.get('observations', [])):
            if observation['error']['passage'].split(':')[0] in {'menota', 'icepahc', 'non'}:
                expected.add((n, i))
    rows = [json.loads(line) for line in (base / 'error-verdicts-w6-norse.jsonl').read_text().splitlines()]
    assert len(rows) == len(expected) == 112
    assert {(r['report_line'], r['observation']) for r in rows} == expected
    assert all(r['source_tokens'] and r['current'] and r['evidence'] for r in rows)
    assert next(r for r in rows if r['report_line'] == 77)['verdict'] == 'rejected'


@pytest.mark.parametrize('lemma', ['ulfr', 'Oddr', 'finnr', 'Skíði', 'unlisted-name'])
def test_every_source_np_is_separate_from_common_lemma(lemma):
    assert gm.annotated_norse_lemma(lemma, 'NP') == lemma + ' (name)'
    assert gm.annotated_norse_lemma(lemma, 'NC') == lemma
    assert gm.annotated_norse_lemma(lemma, '') == lemma
    assert gm.annotated_norse_lemma(lemma + ' (name)', 'NP') == lemma + ' (name)'


@pytest.mark.parametrize('tag', ['NPR-N', 'NPR-D', 'NPRS-G'])
def test_icepahc_names_use_tag_even_with_bad_dictionary_lemma(tag):
    assert gm.annotated_norse_lemma('finna', tag) == 'finna (name)'


def test_menota_uses_source_or_winning_np_tag_and_allows_review():
    w = gm.MenotaWord('doc', 'ulfr', 'NP', 'Ulfr', '1r', '2', None, 0)
    assert gm.reviewed_menota_token(w, 'ulfr', 'NP', {}) == ('ulfr (name)', 'NP')
    rules = {('doc', '1r', '2', 'Ulfr'): {'given_lemma': 'ulfr', 'lemma': 'ulfr', 'tag': 'NC'}}
    assert gm.reviewed_menota_token(w, 'ulfr', 'NP', rules) == ('ulfr', 'NC')
    w.lemma, w.msa = None, ''
    assert gm.reviewed_menota_token(w, 'ulfr', 'NP', {}) == ('ulfr (name)', 'NP')
    assert gm.reviewed_menota_token(w, 'síða', 'NC', {}) == ('síða', 'NC')


@pytest.mark.parametrize('lemma,noun', [('síða', 'síða@side'), ('vit', 'vit@understanding'), ('reka', 'reka@shovel')])
def test_pos_homographs_leave_verbs_and_unannotated_words_alone(lemma, noun):
    for tag in ['NC', 'N-A', 'NS-D']:
        assert gm.annotated_norse_lemma(lemma, tag) == noun
    for tag in ['', 'VB', 'VBDI', 'PRO-N']:
        assert gm.annotated_norse_lemma(lemma, tag) == lemma


def test_name_common_word_separation_and_explicit_mapping_exception():
    # map_lemma must stop before consulting ordinary dictionary roots.
    assert gm.map_lemma(None, 'menota', 'ulfr (name)', {}) == (None, 'name-unmapped')
    overrides = fm.load_overrides()
    assert overrides['lemma']['icepahc']['síða@side'][0] == frozenset()
    assert overrides['lemma']['icepahc']['vit@understanding'][0] == frozenset({'pie-lex-weydos'})


def test_edda_local_repairs_preserve_other_homographs():
    assert reviewed_edda_lemma('edda:11377', 'Œr', 'ær') == 'œrr@mad'
    assert reviewed_edda_lemma('edda:1', 'Œr', 'ær') == 'ær'
    assert reviewed_edda_lemma('edda:4383', 'raari', '?raari') == 'marr@horse'
    assert reviewed_edda_lemma('edda:4383', 'mari', 'marr') == 'marr'
    toks = fm.text_tokens('non', [('test', {'line': 'edda:11377'}, ['Œr'])], lambda _: 'ær', lambda _: True)
    assert toks[0].lemma == 'œrr@mad'


def test_icepahc_review_guard_and_heading_preserve_sentence_numbers(tmp_path):
    base = tmp_path / gm.ICEPAHC
    base.mkdir(parents=True)
    (base / '1250.test.tagged').write_text('Ulfr\tNPR-N\tulfr\n\nskildi\tVBDI\tskilja\n\nLát\tN-N\tlát\n\nsíðu\tN-A\tsíða\n')
    path = tmp_path / 'data/research/formulas/icepahc-reviewed-w6.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps([
        {'text': '1250.test', 'sentence': 2, 'form': 'skildi', 'given_lemma': 'skilja', 'lemma': 'skjöldur', 'tag': 'N-D'},
        {'text': '1250.test', 'sentence': 3, 'form': 'Lát', 'given_lemma': 'lát', 'exclude': True},
    ]))
    ts = gm.load_icepahc(tmp_path)
    assert [(t.lemma, t.locus, t.pos) for t in ts] == [
        ('ulfr (name)', '1250.test s1', 'noun'), ('skjöldur', '1250.test s2', 'noun'),
        ('síða@side', '1250.test s4', 'noun')]
