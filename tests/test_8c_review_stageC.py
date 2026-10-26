"""Review exporter regressions using invented data in temporary directories only."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/make_8c_review_stageC.py'
spec = importlib.util.spec_from_file_location('review_stageC', SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def fixture(root, prefix='C', qualification=None):
    stage = root / 'data/research/8c/stageC'
    inputs, slabs = stage / 'claims', stage / 'slabs'
    inputs.mkdir(parents=True)
    slabs.mkdir()
    (stage / 'review').mkdir()
    (root / 'data/audits/keys').mkdir(parents=True)
    etymon = {'form': '*h₂éwis', 'private': 'discard'}
    if qualification is not None:
        etymon['qualification'] = qualification
    passage = {'id': 'p1', 'corpus': 'hit', 'locus': 'invented 1', 'private': 'discard',
               'lines': [{'role': 'anchor', 'locus': '1', 'text': 'invented',
                          'words': [{'form': 'w', 'lemma': 'l',
                                     'etymon': [etymon, {'form': '*ésti'}, 'ignored']}]}]}
    for name, passages in [('slab1', [passage]), ('slab2', {'p1': passage})]:
        (slabs / f'{name}.json').write_text(json.dumps({'passages': passages}), encoding='utf-8')
    rows = [{'slab': f'slab{1 + i % 2}', 'reader': f'R{prefix}{i:03d}',
             'anchors': ['p1', 'missing'] if i == 0 else ['p1'],
             'bundles': [f'b{i}'], 'confidence': 'high', 'recalled': False,
             'support': [f's{i}'], 'words': ['w'], 'cognate': bool(i % 2),
             'context': f'invented {i}'} for i in range(5)]
    for suffix, batch in [('002', rows[2:]), ('001', rows[:2] + [{'done': True}, {'none': True}])]:
        (inputs / f'R{prefix}{suffix}.jsonl').write_text(
            '\n' + ''.join(json.dumps(row) + '\n' for row in batch), encoding='utf-8')
    (inputs / 'unrelated.jsonl').write_text('not JSON', encoding='utf-8')
    return stage


# SHA-256 of every output from the original exporter on fixture(), including
# JSON spacing, Unicode, shuffle order, partition boundaries and key indentation.
LEGACY_HASHES = {
    'claims-A.jsonl': '352239d76cfa4db4a7117db9fe5ad4ba01128b574a02d8b9fb13307e164504c4',
    'claims-B.jsonl': '7566b84a9ad548bdac48446fbe53387fb3d019e5102863a6643a52eea9d3155e',
    'claims-C.jsonl': 'f258078be26f2b330fb5651306c9965b5a06a5678ae76001816b0b593965115c',
    'claims-D.jsonl': '05e83f9831a8835bcb1f98c401cd99b099571608ac9a1c87876b9c62ba16229b',
    '8c-stageC-claims-key.json': '4853816549071d1fdcb019eed0bb49b1ac7b1c6015c6abcf444b803a0f662e31',
}


def test_stage_c_defaults_byte_identical(tmp_path, monkeypatch):
    stage = fixture(tmp_path)
    monkeypatch.setattr(review, 'ROOT', tmp_path)
    review.main([])
    files = sorted((stage / 'review').glob('*.jsonl'))
    files.append(tmp_path / 'data/audits/keys/8c-stageC-claims-key.json')
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files} == LEGACY_HASHES


def test_stage_cs_parameters_and_qualification(tmp_path):
    qualification = {'confidence': 'doubtful', 'source': 'invented source',
                     'page': 123, 'reason': 'invented uncertainty'}
    stage = fixture(tmp_path, prefix='S', qualification=qualification)
    out = tmp_path / 'custom/packets'
    key = tmp_path / 'custom/key/key.json'
    argv = ['--claims-dir', str(stage / 'claims'), '--slabs-dir', str(stage / 'slabs'),
            '--out-dir', str(out), '--key-out', str(key), '--prefix', 'S',
            '--seed', '889', '--parts', '2']
    review.main(argv)
    packets = [json.loads(line) for p in sorted(out.glob('*.jsonl')) for line in p.read_text().splitlines()]
    assert sorted(p.name for p in out.iterdir()) == ['claims-A.jsonl', 'claims-B.jsonl']
    assert [len(p.read_text().splitlines()) for p in sorted(out.iterdir())] == [2, 3]
    assert [p['claim'] for p in packets] == [f'S{i:04d}' for i in range(1, 6)]
    # Random(889), independently fixed expected permutation of five sorted inputs.
    assert [p['context'] for p in packets] == [f'invented {i}' for i in (3, 0, 2, 1, 4)]
    for packet in packets:
        assert 'confidence' not in packet and 'reader' not in packet and 'slab' not in packet
        etymons = packet['anchors'][0]['lines'][0]['words'][0]['etymon']
        assert etymons == [{'form': '*h₂éwis', 'qualification': qualification}, '*ésti']
    assert set(json.loads(key.read_text())) == {p['claim'] for p in packets}
    assert not list((stage / 'review').iterdir())


def test_default_options_and_legacy_parts():
    args = review.parse_args([])
    assert (args.prefix, args.seed, args.parts) == ('C', 888, 4)
    assert args.claims_dir == review.ROOT / 'data/research/8c/stageC/claims'
    assert args.slabs_dir == review.ROOT / 'data/research/8c/stageC/slabs'
    assert args.out_dir == review.ROOT / 'data/research/8c/stageC/review'
    assert args.key_out == review.ROOT / 'data/audits/keys/8c-stageC-claims-key.json'
    assert review.parse_args(['3']).parts == 3


@pytest.mark.parametrize('argv', [['--parts', '0'], ['--parts', '17'], ['2', '--parts', '3']])
def test_invalid_parts(argv):
    with pytest.raises(SystemExit):
        review.parse_args(argv)
