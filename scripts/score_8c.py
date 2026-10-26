"""Portable, text-free Stage C reanalysis. See stageC/ledger-celtic.README.md."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import random


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_ledger(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines()]
    meta = [r for r in rows if r['type'] == 'run']
    bundles = [r for r in rows if r['type'] == 'bundle']
    claims = [r for r in rows if r['type'] == 'claim']
    if len(meta) != 1 or meta[0]['schema_version'] != 1:
        raise ValueError('Expected one version-1 run record')
    ids = [b['bundle_id'] for b in bundles]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate bundle ID')
    blocks = defaultdict(list)
    for b in bundles:
        if b['actual_kind'] != b['intended_assignment'] or b['construction_status'] != 'succeeded':
            raise ValueError('Failed/unknown decoy construction requires an explicit assignment model')
        if b['actual_kind'] not in {'real', 'decoy'}:
            raise ValueError('Invalid assignment')
        blocks[b['block_id']].append(b)
    for k, bs in blocks.items():
        size = bs[0]['block_size']
        if size < 5 and k * 5 + size != meta[0]['total_original_bundles']:
            raise ValueError('Partial block is not the original final block')
        if not 1 <= size <= 5 or len(bs) != size:
            raise ValueError('Incomplete original assignment block')
        if sorted(b['order_index'] for b in bs) != list(range(k * 5, k * 5 + size)):
            raise ValueError('Invalid original order/block membership')
        if any(b['block_size'] != size for b in bs):
            raise ValueError('Inconsistent block size')
        nd = sum(b['actual_kind'] == 'decoy' for b in bs)
        if nd > 1 or (size == 5 and nd != 1):
            raise ValueError('Observed assignment violates block rule')
    if len({c['claim_id'] for c in claims}) != len(claims):
        raise ValueError('Duplicate claim')
    for c in claims:
        if c['original_grade'] not in {'accepted', 'weak', 'reject'}:
            raise ValueError('Invalid claim grade')
        if not isinstance(c['original_eligibility']['eligible'], bool) or not c['original_eligibility']['reason']:
            raise ValueError('Explicit original eligibility and reason required')
        for anchor in c['anchors']:
            if anchor['contribution'] not in {'contributes', 'does not contribute', 'uncertain'}:
                raise ValueError('Invalid contribution state')
        if not set(c['bundle_ids']) <= set(ids):
            raise ValueError('Claim cites missing bundles')
    return meta[0], bundles, claims


def contributing_celtic(anchors):
    """Strict sensitivity gate; uncertainty never counts as contribution."""
    branches = {a['branch'] for a in anchors if a['contribution'] == 'contributes'}
    verified_celtic = any(a['branch'] == 'Celtic' and a['contribution'] == 'contributes'
                          and a['verified'] for a in anchors)
    return verified_celtic and 'Celtic' in branches and len(branches) >= 2


def legal_options(block):
    # Five equiprobable slots even in the final partial block: unused slots mean no decoy.
    return [b['bundle_id'] for b in block] + [None] * (5 - len(block))


def assignment_options(bundles):
    blocks = defaultdict(list)
    for b in bundles:
        blocks[b['block_id']].append(b)
    return [legal_options(bs) for _, bs in sorted(blocks.items())]


def exact_distribution(options, selected, weights, target):
    """Integer multiplicities: exact convolution of all legal block assignments.

    Condition on the observed number of selected decoys. Members outside selected
    stay in options and therefore retain their original probability mass.
    """
    scale = math.lcm(*(w.denominator for w in weights.values())) if weights else 1
    terms = [Counter((int(b in selected), int(weights.get(b, 0) * scale)) for b in op)
             for op in options]
    # Collapse deterministic terms before convolution (irrelevant complete blocks included).
    fixed_n = fixed_w = 0
    variable = []
    for term in terms:
        if len(term) == 1:
            n, w = next(iter(term))
            fixed_n += n
            fixed_w += w
        else:
            variable.append(term)
    target -= fixed_n
    remaining_min = sum(min(n for n, w in t) for t in variable)
    remaining_max = sum(max(n for n, w in t) for t in variable)
    dist = {(0, fixed_w): 1}
    for term in variable:
        remaining_min -= min(n for n, w in term)
        remaining_max -= max(n for n, w in term)
        nxt = defaultdict(int)
        for (n, w), count in dist.items():
            for (dn, dw), multiplicity in term.items():
                nn = n + dn
                if nn + remaining_min <= target <= nn + remaining_max:
                    nxt[nn, w + dw] += count * multiplicity
        dist = nxt
    return {Fraction(w, scale): count for (n, w), count in dist.items() if n == target}


def score(bundles, claims, selected, grades, sensitivity=False, method='exact', seed=0, permutations=10000):
    weights = defaultdict(Fraction)
    outside = 0
    for c in claims:
        if c['original_grade'] not in grades or not c['original_eligibility']['eligible']:
            continue
        if sensitivity and not contributing_celtic(c['anchors']):
            continue
        bs = set(c['bundle_ids']) & selected
        if not bs:
            outside += 1
        for b in bs:
            weights[b] += Fraction(1, len(bs))
    decoys = {b['bundle_id'] for b in bundles if b['actual_kind'] == 'decoy'} & selected
    nd, nr = len(decoys), len(selected) - len(decoys)
    wd = sum((weights[b] for b in decoys), Fraction())
    wr = sum(weights.values(), Fraction()) - wd
    out = dict(real_weight=float(wr), decoy_weight=float(wd), real_bundles=nr, decoy_bundles=nd,
               outside_selection=outside, real_per_bundle=float(wr / nr) if nr else None,
               decoy_per_bundle=float(wd / nd) if nd else None)
    if not nr or not nd:
        return dict(out, p=None, status='undefined: observed denominator is zero')
    options = assignment_options(bundles)
    if method == 'exact':
        dist = exact_distribution(options, selected, weights, nd)
        total = sum(dist.values())
        tail = sum(v for w, v in dist.items() if w <= wd)
        out.update(p=tail / total, exact_tail=str(tail), exact_total=str(total), permutations=0,
                   monte_carlo_correction='none; exact integer convolution')
    else:
        rng = random.Random(seed)
        ge = retained = attempts = 0
        while retained < permutations:
            attempts += 1
            if attempts > max(100000, permutations * 10000):
                raise ValueError('Condition too rare for rejection sampling; use exact mode')
            draw = {rng.choice(op) for op in options} & selected
            if len(draw) != nd:
                continue
            retained += 1
            ge += sum((weights[b] for b in draw), Fraction()) <= wd
        out.update(p=(ge + 1) / (permutations + 1), permutations=permutations,
                   attempted_draws=attempts, monte_carlo_correction='(ge+1)/(N+1)')
    return out


def analyze(meta, bundles, claims, **kwargs):
    read = {b['bundle_id'] for b in bundles if b['in_completed_wave']}
    celtic = {b['bundle_id'] for b in bundles if b['pivot_group'] == 'celtic'} & read
    scopes = {'celtic_pivot': celtic, 'all_read': read}
    for field in ('date_bin', 'genre'):
        for value in sorted({b[field] for b in bundles if b['bundle_id'] in celtic}):
            scopes[f'{field}:{value}'] = {b['bundle_id'] for b in bundles
                                         if b['bundle_id'] in celtic and b[field] == value}
    endpoints = {'accepted': {'accepted'}, 'accepted+weak': {'accepted', 'weak'},
                 'all claims': {'accepted', 'weak', 'reject'}}
    def run(sensitivity):
        return {name: {label: score(bundles, claims, selected, grades, sensitivity, **kwargs)
                       for label, grades in endpoints.items()} for name, selected in scopes.items()}
    return {'schema_version': 1, 'analysis_version': 'celtic-v2-block-conditional',
            'source_run': meta, 'statistic': 'real weight / real count - decoy weight / decoy count; upper tail',
            'null_model': 'independent original document-order blocks: one uniformly selected decoy per five; final m/5 draw probability',
            'conditioning': 'observed selected decoy count in each scope; complete blocks retained before scope selection; fixed claims and original eligibility',
            'weighting': 'one per eligible claim, divided equally among cited bundles within scope',
            'correction': 'historical unrestricted label shuffle replaced by original block mechanism',
            'settings': kwargs, 'scores': run(False),
            'sensitivity_contributing_celtic': {'label': 'retrospective sensitivity; not original endpoint',
                'eligible_claims': [c['claim_id'] for c in claims if c['original_eligibility']['eligible']
                                    and contributing_celtic(c['anchors'])], 'scores': run(True)}}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ledger', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--analysis-date', required=True)
    p.add_argument('--method', choices=['exact', 'monte-carlo'], default='exact')
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--permutations', type=int, default=10000)
    a = p.parse_args()
    if a.permutations < 1:
        p.error('--permutations must be positive')
    meta, bundles, claims = read_ledger(a.ledger)
    result = analyze(meta, bundles, claims, method=a.method, seed=a.seed, permutations=a.permutations)
    result['run_metadata'] = dict(run_id=a.run_id, analysis_date=a.analysis_date,
                                  ledger_sha256=sha256(a.ledger), scorer_sha256=sha256(__file__))
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
