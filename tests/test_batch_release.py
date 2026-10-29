import json
import runpy
import sys
from pathlib import Path

import pytest

from pie.batch_release import batch_eligibility, release_metadata


def candidate(root, batch='b', gate='PASS', status='approved', records=None):
    paths = {
        f'corpus/tier3/{batch}.jsonl': ''.join(json.dumps(r) + '\n' for r in (records or [])),
        f'data/generation/plans/{batch}.jsonl': '{}\n',
        f'data/generation/batches/{batch}.json': json.dumps({'gate': gate, 'gates': {'diversity': gate == 'PASS'}}),
    }
    for name, text in paths.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    p = root / f'data/generation/releases/{batch}.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(release_metadata(root, batch, status=status,
                                           evidence=['documented review'], rationale='Reviewed and fixed.')))
    return p


@pytest.mark.parametrize('gate,status,eligible,reason', [
    ('PASS', 'approved', True, None), ('PASS', 'pending', False, 'required review pending'),
    ('PASS', 'rejected', False, 'required review rejected'),
    ('FAIL', 'approved', False, 'gate FAIL: diversity'),
    ('FAIL', 'pending', False, 'required review pending'),
])
def test_gate_and_review_are_independent(tmp_path, gate, status, eligible, reason):
    candidate(tmp_path, gate=gate, status=status)
    d = batch_eligibility(tmp_path, 'b')
    assert d['eligible'] is d['admitted'] is eligible
    assert (d['gate'], d['review']) == (gate, status)
    if reason:
        assert reason in d['reasons']
    experimental = batch_eligibility(tmp_path, 'b', experimental=True)
    assert experimental == {**d, 'admitted': True, 'experimental': True}
    assert batch_eligibility(tmp_path, 'b') == d


@pytest.mark.parametrize('artifact', ['records', 'plans', 'gate_report'])
def test_stale_binding(tmp_path, artifact):
    from pie.batch_release import artifact_paths
    candidate(tmp_path)
    p = tmp_path / artifact_paths('b')[artifact]
    p.write_text(p.read_text() + '\n')
    d = batch_eligibility(tmp_path, 'b')
    assert not d['admitted']
    assert f'stale {artifact} evidence' in d['reasons']


@pytest.mark.parametrize('bad', [None, '{', '[]', '{}', '{"review": null}'])
def test_missing_malformed_metadata(tmp_path, bad):
    p = candidate(tmp_path)
    if bad is None:
        p.unlink()
    else:
        p.write_text(bad)
    d = batch_eligibility(tmp_path, 'b')
    assert not d['admitted']
    assert 'missing or malformed release metadata' in d['reasons']


@pytest.mark.parametrize('bad', [None, '{}', '[]', '{"gate":"PASS","gates":{"x":false}}',
                                  '{"gate":"PASS","gates":{"x":1}}'])
def test_bad_gate_report(tmp_path, bad):
    candidate(tmp_path)
    p = tmp_path / 'data/generation/batches/b.json'
    if bad is None:
        p.unlink()
    else:
        p.write_text(bad)
    d = batch_eligibility(tmp_path, 'b')
    assert not d['admitted']
    assert 'missing or malformed gate report' in d['reasons']


def test_excluded_population_does_not_control_holdouts(tmp_path, monkeypatch):
    import pie.export as ex
    from pie.holdout import held_roots
    rid = sorted(held_roots())[0]
    rec = {'id': 't3-b-1', 'pie': 'test', 'english': 'test', 'gloss': 'test', 'tokens': [{'form': 'test', 'root_id': rid}]}
    candidate(tmp_path, gate='FAIL', records=[rec])
    task = {'task': 'inflect', 'source_id': 'lex-test', 'root_id': rid}
    monkeypatch.setattr(ex, 'inflection_tasks', lambda lx, rng: [task])
    monkeypatch.setattr(ex, 'cognate_tasks', lambda lx: [])
    default = ex.build(root=tmp_path)
    assert default['train_records'] == default['train_tasks'] == []
    assert default['eval_tasks'] == [dict(task, seen_in_train=False)]
    assert 'gate FAIL: diversity' in default['batch_eligibility'][0]['reasons']
    experimental = ex.build(root=tmp_path, experimental_batches=True)
    assert experimental['train_records'] == [rec]
    assert task in experimental['train_tasks']
    assert len(experimental['train_tasks']) == 4
    assert experimental['eval_tasks'] == []


def test_shipped_migration():
    root = Path(__file__).resolve().parents[1]
    decisions = {p.stem: batch_eligibility(root, p.stem) for p in (root / 'corpus/tier3').glob('*.jsonl')}
    assert decisions['t022']['gate'] == 'FAIL'
    assert decisions['t022']['review'] == 'pending'
    assert not decisions['t022']['admitted']
    assert decisions['t023']['admitted']
    assert not decisions['pilot']['admitted'] and not decisions['pilot2']['admitted']
    # ENG-01's invariant, not today's batch list: a shipped batch is excluded only for a documented
    # reason (gate FAIL, review pending/rejected), never for missing, malformed or stale evidence. A new
    # batch parked at review pending is fine; an approved batch whose binding went stale is not.
    for b, d in decisions.items():
        assert d['admitted'] == (d['gate'] == 'PASS' and d['review'] == 'approved'), (b, d['reasons'])


def _produce(tmp_path, monkeypatch, plans_list):
    """Run scripts/realize_plans.py main() on these plan records in tmp_path; return its exit status."""
    root = Path(__file__).resolve().parents[1]
    module = runpy.run_path(str(root / 'scripts/realize_plans.py'))
    main = module['main']
    monkeypatch.setitem(main.__globals__, 'ROOT', tmp_path)
    for path in ('corpus/tier3', 'data/generation/rejects'):
        (tmp_path / path).mkdir(parents=True, exist_ok=True)
    # Exercise the real validator on just these plans' lexemes; the full lexicon
    # index is unrelated to the producer's persistence and exit contract.
    from pie.realize import Lexicon
    from pie.validate import FormIndex
    lx = Lexicon.load()
    lids = {slot['lex_id'] for plan in plans_list for clause in plan.get('plan', plan)['clauses']
            for slot in clause.get('slots', []) if 'lex_id' in slot}
    closed = json.loads((root / 'data/morph/closed_class.json').read_text())
    ix = FormIndex([v for k, v in lx.entries.items() if k in lids],
                   [v for k, v in lx.specs.items() if k in lids], closed)
    monkeypatch.setitem(main.__globals__, 'load_index', lambda: ix)
    plans = tmp_path / 'input.jsonl'
    plans.write_text(''.join(json.dumps(p) + '\n' for p in plans_list))
    monkeypatch.setattr(sys, 'argv', ['realize_plans.py', str(plans), '--batch', 'probe'])
    status = main()
    assert plans.read_bytes() == (tmp_path / 'data/generation/plans/probe.jsonl').read_bytes()
    return status


def _plan(batch, plan_id):
    root = Path(__file__).resolve().parents[1]
    return next(p for p in map(json.loads, (root / f'data/generation/plans/{batch}.jsonl').read_text().splitlines())
                if p['plan_id'] == plan_id)


@pytest.mark.parametrize('count,exit_status', [(1, 0), (7, 1)])
def test_producer_contract(tmp_path, monkeypatch, count, exit_status):
    # a charm plan relabelled as prose: this tests persistence and exit status, not meter (test below)
    plan = {**_plan('t023', 't023-0001'), 'genre': 'narrative'}
    assert _produce(tmp_path, monkeypatch, [plan] * count) == exit_status
    assert len((tmp_path / 'corpus/tier3/probe.jsonl').read_text().splitlines()) == count
    d = batch_eligibility(tmp_path, 'probe')
    assert d['gate'] == ('PASS' if exit_status == 0 else 'FAIL')
    assert d['review'] == 'pending'
    assert not d['admitted']
    assert (tmp_path / 'data/generation/rejects/probe.jsonl').exists()


def _report(tmp_path):
    return json.loads((tmp_path / 'data/generation/batches/probe.json').read_text())


def test_meter_exact_gate(tmp_path, monkeypatch):
    """The gate counts verse lines (sentences) of metered genres with exactly 8 or 11 syllables;
    the ±1 window (meter_fit, meter_near) is reported but no longer gates."""
    exact = _plan('t011', 't011-0036')              # a hymn of three 8-syllable lines
    assert _produce(tmp_path, monkeypatch, [exact]) == 0
    r = _report(tmp_path)
    assert r['gates']['meter_exact>=0.90'] is True
    assert r['meter_exact'] == {'lines': 3, 'exact': 3, 'share': 1.0}
    assert r['meter_near']['share'] == r['meter_fit']['share'] == 1.0
    assert batch_eligibility(tmp_path, 'probe')['gate'] == 'PASS'

    charm = _plan('t023', 't023-0001')               # six lines, 7-12 syllables, one exact
    assert _produce(tmp_path, monkeypatch, [charm]) == 1
    r = _report(tmp_path)
    assert r['meter_fit']['share'] == 1.0 and r['meter_exact']['share'] < 0.9
    assert r['gates']['meter_exact>=0.90'] is False
    d = batch_eligibility(tmp_path, 'probe')
    assert d['gate'] == 'FAIL' and 'meter_exact>=0.90' in d['reasons'][0]

    # prose is not scored: no meter fields, no meter gate
    assert _produce(tmp_path, monkeypatch, [{**charm, 'genre': 'narrative'}]) == 0
    r = _report(tmp_path)
    assert r['meter_exact'] is None and 'meter_exact>=0.90' not in r['gates']
