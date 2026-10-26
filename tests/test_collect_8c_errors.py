"""Invented reader records only; no corpus, audit key, or text slabs opened."""
import importlib.util
import json
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    'collect_8c_errors', Path(__file__).resolve().parents[1] / 'scripts/collect_8c_errors.py')
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)


def harvest(note, passages=None, bundles=None):
    return S.harvest(note, 'R1', 'S1', passages or {}, bundles or {}, {'file': 'r.progress', 'line': 1})


@pytest.mark.parametrize(('note', 'kind'), [
    ('wrong lemma `abc`', 'lemma'),
    ('wrong mapping for abc', 'mapping'),
    ('missing PIE mapping for abc', 'mapping'),
    ('OCR misreading of abc', 'ocr'),
    ('misread Irish abc', 'lemma'),
    ('misread Welsh abc', 'lemma'),
    ('mapping junk', 'mapping'),
    ('unit cut in the wrong place', 'unit'),
    ('name taken as a word', 'name'),
])
def test_error_categories(note, kind):
    reports = harvest(note)
    assert kind in {r['error']['kind'] for r in reports}
    for r in reports:
        assert r['source'] == 'harvested-note'
        assert r['error']['note_fragment'] in note
        assert len(r['error']['note_fragment']) <= 280
        assert r['error']['given_lemma'] == r['error']['given_etymon'] == ''


@pytest.mark.parametrize('note', [
    'Read 100 bundles with mappings.', 'The edition is OCR.',
    'No mapping errors found.', 'No wrong lemma reported.',
    'A generic horse epithet with unrelated context.',
])
def test_non_errors(note):
    assert harvest(note) == []


def test_explicit_report_lookup_and_no_guesses():
    record = {'reader': 'R', 'slab': 'S', 'error': {
        'passage': 'xx:1', 'form': 'abc', 'kind': 'mapping', 'evidence': 'wrong'}}
    loci = {'xx:1': {'corpus': 'Corpus X', 'lines': [{'role': 'passage', 'locus': '1'}]}}
    result = S.normalize(record, loci, 'structured-error', {})
    assert result['error']['corpus'] == 'Corpus X'
    assert result['error']['given_lemma'] == result['error']['given_etymon'] == ''
    loci['xx:1']['words'] = [{'form': 'abc', 'lemma': 'ab', 'etymon': '*ab'}]
    result = S.normalize(record, loci, 'structured-error', {})
    assert result['error']['given_lemma'] == 'ab'
    assert result['error']['given_etymon'] == '*ab'
    record['error']['given_lemma'] = 'reader-value'
    assert S.normalize(record, loci, 'structured-error', {})['error']['given_lemma'] == 'reader-value'


def test_note_form_and_bundle_resolution():
    passages = {'menota:1': {'corpus': 'Norse'}, 'mga:2': {'corpus': 'Irish'}}
    reports = harvest("BC-abcde: mis-mapping of ON vár 'spring'", passages,
                      {'BC-abcde': ['mga:2', 'menota:1']})
    assert reports[0]['error']['form'] == 'vár'
    assert reports[0]['error']['passage'] == 'menota:1'
    assert reports[0]['error']['corpus'] == 'Norse'
    assert harvest('Irish m-broin = bron sorrow, not bro quern')[0]['error']['form'] == 'm-broin'
    assert harvest('menmae is not < *ménos')[0]['error']['form'] == 'menmae'


def test_collect_filter_done_notes_and_dedup(tmp_path):
    claims = tmp_path / 'stageCS' / 'claims'
    claims.mkdir(parents=True)
    loci = tmp_path / 'slabs-loci'
    loci.mkdir()
    (loci / 'S.json').write_text(json.dumps({'passages': [
        {'id': 'xx:1', 'corpus': 'X'}, {'id': 'xx:2', 'corpus': 'X'}]}))
    records = [
        {'reader': 'RS002', 'slab': 'S', 'error': {'passage': 'xx:1', 'form': 'abc', 'kind': 'mapping'}},
        {'reader': 'RS002', 'slab': 'S', 'error': {'passage': 'xx:2', 'form': 'abc', 'kind': 'lemma'}},
        {'reader': 'RS002', 'slab': 'S', 'note': 'wrong lemma ignored non-done'},
        {'reader': 'RS002', 'slab': 'S', 'done': True, 'note': 'OCR misreading xx:1'},
    ]
    (claims / 'RS002.jsonl').write_text('\n'.join(json.dumps(r) for r in records))
    (claims / 'RS002.progress').write_text('mapping junk\n')
    # These would fail JSON parsing if opened.
    (claims / 'RS002H.jsonl').write_text('MUST NOT READ')
    (claims / 'RS004.jsonl').write_text('MUST NOT READ')
    reports = S.collect([claims], [loci])
    assert len(reports) == 3
    explicit = reports[0]
    assert set(explicit['kinds']) == {'mapping', 'lemma'}
    assert len(explicit['provenance']) == 2
    assert explicit['observations'][0]['error']['passage'] == 'xx:2'
    assert all(r['slab'] == 'S' for r in reports)


def test_unknown_notes_are_not_collapsed():
    reports = harvest('wrong lemma abc; wrong lemma def')
    assert len(S.deduplicate(reports)) == 2
    assert len(S.deduplicate(harvest('mapping junk') + harvest('mapping junk'))) == 1


def test_invalid_kind():
    with pytest.raises(ValueError, match='Invalid error kind'):
        S.normalize({'error': {'kind': 'typo'}}, {}, 'structured-error', {})


def test_rejection_is_not_a_lemma_error():
    assert harvest('bones = Aen. 12.35-36, Vergilian, not inherited.') == []


def test_bundle_context_survives_semicolon_but_not_next_sentence():
    passages = {'sga:1': {'corpus': 'Irish'}, 'sga:2': {'corpus': 'Irish'}}
    bundles = {'BS-11111': ['sga:1'], 'BS-22222': ['sga:2']}
    reports = harvest('BS-11111 rejected: ordinary posture; Irish abc is not a secure cognate. '
                      'BS-22222 rejected: ordinary fruit list.', passages, bundles)
    assert len(reports) == 1
    assert reports[0]['error']['passage'] == 'sga:1'
    assert 'fruit' not in reports[0]['error']['note_fragment']


def test_lemma_and_surface_form_dedup_preserves_observations():
    explicit = S.normalize({'error': {'kind': 'mapping', 'corpus': 'X', 'form': 'abc',
                                      'given_lemma': 'ab'}}, {}, 'structured-error', {})
    note = harvest('wrong lemma abc')[0]
    note['error']['corpus'] = 'X'
    merged = S.deduplicate([note, explicit])
    assert len(merged) == 1
    assert merged[0]['source'] == 'structured-error'
    assert merged[0]['observations'][0]['source'] == 'harvested-note'


def test_separate_quoted_lead_does_not_inherit_previous_bundle():
    reports = harvest("BC-11111 unrelated shield; 'abc' (Irish abc = def, not ghi)",
                      {'sga:1': {'corpus': 'Irish'}}, {'BC-11111': ['sga:1']})
    assert reports[0]['error']['passage'] == ''


def test_reader_selection_and_exclusion_before_open(tmp_path, monkeypatch):
    claims = tmp_path / 'stageCS' / 'claims'
    claims.mkdir(parents=True)
    loci = tmp_path / 'loci'
    loci.mkdir()
    record = {'reader': 'RS004', 'error': {
        'passage': 'xx:1', 'form': 'abc', 'kind': 'mapping'}}
    (claims / 'RS004.jsonl').write_text(json.dumps(record))
    (claims / 'RS004.progress').write_text('wrong lemma def')
    for name in ['RS002H.jsonl', 'RS004F.jsonl', 'RS005.jsonl', 'RS001.jsonl',
                 'RS004.txt']:
        (claims / name).write_text('MUST NOT OPEN')
    original = Path.read_text

    def guarded_read(path, *args, **kwargs):
        assert path.name in {'RS004.jsonl', 'RS004.progress'}
        return original(path, *args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(Path, 'read_text', guarded_read)
        exact = S.collect([claims], [loci], readers=['RS004'])
        glob = S.collect([claims], [loci], readers=['RS00[245]*'],
                         exclude=['*F', 'RS005'])
        assert exact == glob
        assert len(exact) == 2
        assert S.collect([claims], [loci], readers=['NO_MATCH']) == []
        assert S.collect([claims], [loci], readers=['RS004'], exclude=['RS004']) == []
        output = tmp_path / 'reports.jsonl'
        m.setattr('sys.argv', ['collect_8c_errors.py', str(claims), '--output',
                              str(output), '--loci-dirs', str(loci), '--readers',
                              'RS004', 'RS005', '--exclude', 'RS005'])
        S.main()
    assert [json.loads(line) for line in output.read_text().splitlines()] == exact


def test_default_and_explicit_selection_outside_stagecs():
    assert S.allowed(Path('stageC/claims/RC001.jsonl'))
    assert not S.allowed(Path('stageC/claims/RC001.jsonl'), ['RS004'])
    assert S.allowed(Path('stageCS/claims/RS001X.progress'))
    assert not S.allowed(Path('stageCS/claims/RS004.progress'))
    assert not S.allowed(Path('stageCS/claims/RS002H.progress'), ['*'])
