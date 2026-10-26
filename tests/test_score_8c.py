"""Assignment-design and public-replay regressions; no keys or raw imports."""
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('score_8c', ROOT / 'scripts/score_8c.py')
sc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sc)
LEDGER = ROOT / 'data/research/8c/stageC/ledger-celtic.jsonl'


def fixture_blocks(sizes):
    result = []
    for k, size in enumerate(sizes):
        for i in range(size):
            result.append(dict(bundle_id=f'{k}:{i}', block_id=k, block_size=size,
                               order_index=k * 5 + i, actual_kind='decoy' if i == 0 else 'real'))
    return result


def test_exact_matches_independent_enumeration_with_cut_and_partial_block():
    bs = fixture_blocks([5, 3])
    selected = {'0:0', '0:1', '1:0', '1:1'}
    weights = {'0:0': Fraction(1, 2), '1:1': Fraction(1)}
    options = sc.assignment_options(bs)
    expected = {}
    for draw in itertools.product(*options):
        chosen = set(draw) & selected
        if len(chosen) == 2:
            w = sum((weights.get(b, 0) for b in chosen), Fraction())
            expected[w] = expected.get(w, 0) + 1
    assert sc.exact_distribution(options, selected, weights, 2) == expected
    # Outside members must retain their mass: selecting one of five is probability 1/5.
    one = sc.exact_distribution([options[0]], {'0:0'}, {'0:0': Fraction(1)}, 0)
    assert one == {Fraction(0): 4}
    assert options[1].count(None) == 2
    assert len(list(itertools.product(*options))) == 25
    assert all(sum(x is not None for x in draw[:1]) == 1 for draw in itertools.product(*options))


def test_exact_score_and_monte_carlo():
    bs = fixture_blocks([5])
    claim = dict(claim_id='X', bundle_ids=['0:1'], original_grade='weak',
                 original_eligibility={'eligible': True})
    ids = {b['bundle_id'] for b in bs}
    exact = sc.score(bs, [claim], ids, {'weak'})
    mc = sc.score(bs, [claim], ids, {'weak'}, method='monte-carlo', seed=42, permutations=10000)
    assert exact['p'] == .8
    assert abs(mc['p'] - .8) < .02
    assert mc == sc.score(bs, [claim], ids, {'weak'}, method='monte-carlo', seed=42, permutations=10000)
    assert sc.score(bs, [claim], {'0:1'}, {'weak'})['p'] is None


def test_frozen_weights_and_original_exclusion():
    _, bs, claims = sc.read_ledger(LEDGER)
    ids = {b['bundle_id'] for b in bs if b['in_completed_wave'] and b['pivot_group'] == 'celtic'}
    assert len(ids) == 4687
    for grades, expected in [({'accepted'}, (0, 0)), ({'accepted', 'weak'}, (6.25, .75)),
                             ({'accepted', 'weak', 'reject'}, (14.25, .75))]:
        result = sc.score(bs, claims, ids, grades)
        assert (result['real_weight'], result['decoy_weight']) == expected
    excluded = [c['claim_id'] for c in claims if not c['original_eligibility']['eligible']]
    assert excluded == ['C0011']
    cut = [b for b in bs if b['block_id'] == 4685 // 5]
    assert len(cut) == 5
    assert sum(b['bundle_id'] in ids for b in cut) == 2
    assert len({b['branch'] for c in claims if c['claim_id'] == 'C0011' for b in c['anchors']}) == 1
    c9 = next(c for c in claims if c['claim_id'] == 'C0009')
    assert not sc.contributing_celtic(c9['anchors'])
    assert next(a for a in c9['anchors'] if a['branch'] == 'Celtic')['contribution'] == 'does not contribute'


def test_contribution_gate():
    def anchor(branch, state='contributes', verified=True):
        return dict(branch=branch, contribution=state, verified=verified)
    assert sc.contributing_celtic([anchor('Celtic'), anchor('Greek')])
    assert not sc.contributing_celtic([anchor('Celtic', 'does not contribute'), anchor('Greek'), anchor('Germanic')])
    assert not sc.contributing_celtic([anchor('Indo-Iranian'), anchor('Indo-Iranian')])
    assert not sc.contributing_celtic([anchor('Celtic', 'uncertain'), anchor('Greek')])
    assert not sc.contributing_celtic([anchor('Celtic', verified=False), anchor('Greek')])


def test_reject_incomplete_blocks_and_construction_failures(tmp_path):
    rows = [json.loads(x) for x in LEDGER.read_text().splitlines()]
    path = tmp_path / 'bad.jsonl'
    def write(rs):
        path.write_text(''.join(json.dumps(r) + '\n' for r in rs))
    write(rows[:1] + rows[2:])
    with pytest.raises(ValueError, match='Incomplete'):
        sc.read_ledger(path)
    rows[1]['construction_status'] = 'failed'
    write(rows)
    with pytest.raises(ValueError, match='construction'):
        sc.read_ledger(path)


def test_clean_standalone_replay(tmp_path):
    shutil.copy(ROOT / 'scripts/score_8c.py', tmp_path / 'score.py')
    shutil.copy(LEDGER, tmp_path / 'ledger.jsonl')
    subprocess.run([sys.executable, '-I', str(tmp_path / 'score.py'), '--ledger', 'ledger.jsonl',
                    '--output', 'result.json', '--run-id', 'fixture', '--analysis-date', '2026-10-25'],
                   cwd=tmp_path, check=True)
    result = json.loads((tmp_path / 'result.json').read_text())
    shipped = json.loads((LEDGER.parent / 'results-celtic-v2.json').read_text())
    assert result['scores'] == shipped['scores']
    assert result['sensitivity_contributing_celtic'] == shipped['sensitivity_contributing_celtic']
    historical = json.loads((LEDGER.parent / 'results-celtic.json').read_text())
    assert historical['scores']['celtic_pivot']['all claims']['p'] == 0.042995700429957005
