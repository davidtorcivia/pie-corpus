"""Export the completed, unblinded Stage C wave only; never loads raw corpora.

The key's insertion order preserves build()/pack_slabs()/doc_order(). Public
slab bundle arrays are ID-sorted and must NOT be used as document order.
"""
import argparse
import hashlib
import json
from pathlib import Path


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


BRANCH = {'sga': 'Celtic', 'sga-gl': 'Celtic', 'mga': 'Celtic', 'ga-early': 'Celtic',
          'cy': 'Celtic', 'grc': 'Greek', 'grc-late': 'Greek', 'hom': 'Greek',
          'menota': 'Germanic', 'ang': 'Germanic', 'lat': 'Italic',
          'av': 'Indo-Iranian', 'rv': 'Indo-Iranian', 'ae': 'Indo-Iranian',
          'vuk': 'Balto-Slavic', 'lv': 'Balto-Slavic'}
# Manual, text-free coding of the original verdict reasons, in claim-key anchor order.
# Contribution means support for the proposed comparison, not proof of inheritance.
CODING = {
 'C0001': ('++++', 'Reviewer identifies the cattle-driving relation in all four anchors; genericity limits grade.'),
 'C0002': ('??????', 'Generic winter inventory and derivative contexts; no explicit positive contribution decision.'),
 'C0003': ('++', 'Reviewer explicitly finds the carrion-threat context comparable despite limited cognation.'),
 'C0004': ('+-++', 'Irish formula confirmed; Serbian anchor explicitly judged no parallel formula.'),
 'C0005': ('+++++', 'Reviewer confirms Irish binomial and Indo-Iranian formula; Norse renews a term; cross-branch link weak.'),
 'C0006': ('?-', 'Irish brink/brow identity uncertain; Strabo explicitly lacks the claimed collocation.'),
 'C0007': ('++', 'Reviewer identifies cognate verb-object relation and a loosely comparable Vedic counterpart.'),
 'C0008': ('??', 'Shared fruit inventory but no explicit support for inherited figure.'),
 'C0009': ('+---', 'Norse alone has claimed form; Plato and Galen have different constructions; Irish explicitly not a witness.'),
 'C0010': ('+++', 'Reviewer finds living-wealth congruence real but natural, with different orders and lexical slots.'),
 'C0011': ('++', 'Reviewer accepts Indo-Iranian phraseology; both anchors are in one registered branch.'),
 'C0012': ('???????', 'Translation and generic washing semantics; no explicit positive inherited-figure contribution decision.'),
 'C0013': ('---', 'Reviewer explicitly says anchors do not show the formula.'),
 'C0014': ('?+', 'Greek is an explicit inherited-collocation witness; Irish supplies only noun, so contribution to that collocation uncertain.'),
 'C0015': ('-+', 'Welsh explicitly not the claimed epithet; Avestan compound epithet verified.'),
 'C0016': ('--', 'Reviewer explicitly rejects congruence of meanings, syntax and horse roles.'),
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--key', type=Path, required=True)
    p.add_argument('--claims-key', type=Path, required=True)
    p.add_argument('--assignment', type=Path, required=True)
    p.add_argument('--stats', type=Path, required=True)
    p.add_argument('--historical-results', type=Path, required=True)
    p.add_argument('--loci-dir', type=Path, required=True)
    p.add_argument('--verdicts', type=Path, nargs='+', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-commit', required=True)
    p.add_argument('--run-id', required=True)
    a = p.parse_args()
    key = json.loads(a.key.read_text())['slabs']
    assignment = json.loads(a.assignment.read_text())['slabs']
    stats = json.loads(a.stats.read_text())
    if stats['decoy_target'] != stats['decoy_bundles']:
        raise ValueError('Cannot infer intended assignments when construction failures occurred')
    historical = json.loads(a.historical_results.read_text())
    if historical['excluded_anchoring'] != ['C0011']:
        raise ValueError('Unexpected original eligibility; manual review required')
    ck = json.loads(a.claims_key.read_text())
    verdicts = {v['claim']: (v, f.name) for f in a.verdicts for line in f.read_text().splitlines()
                for v in [json.loads(line)]}
    paths = [a.key, a.claims_key, a.assignment, a.stats, a.historical_results, Path(__file__), *a.verdicts]
    full = [(s, b, v) for s, bs in key.items() for b, v in bs.items()]
    completed = {s for s, r in assignment.items() if 1 <= int(r.removeprefix('RC')) <= 28}
    # Include every member of every touched assignment block, even outside the wave.
    touched = {i // 5 for i, (s, b, v) in enumerate(full) if s in completed}
    rows = []
    loci = {}
    for s in {s for i, (s, b, v) in enumerate(full) if i // 5 in touched}:
        path = a.loci_dir / (s + '.json')
        paths.append(path)
        loci[s] = {b['bundle']: b for b in json.loads(path.read_text())['bundles']}
    for i, (s, b, v) in enumerate(full):
        if i // 5 not in touched:
            continue
        shown = loci[s][b]
        assert shown['pivot'] == v['pivot']
        assert shown['partners'] == v.get('decoy_partners', [x['id'] for x in v['real_partners']])
        m = v.get('pivot_meta') or {}
        year = m.get('date_from')
        mid = (year + (m.get('date_to') or year)) / 2 if year is not None else None
        date = 'unknown' if mid is None else '<=900' if mid <= 900 else '901-1200' if mid <= 1200 else '1201-1250' if mid <= 1250 else '>1250'
        rows.append(dict(type='bundle', bundle_id=b, slab=s, order_index=i, block_id=i // 5,
                         block_size=min(5, len(full) - i // 5 * 5), block_rule='one-of-five; final m/5',
                         intended_assignment=v['kind'], actual_kind=v['kind'], construction_status='succeeded',
                         in_completed_wave=s in completed, pivot_corpus=v['pivot_corpus'],
                         pivot_group=v['pivot_group'], pivot_branch=BRANCH.get(v['pivot_corpus'], 'other'),
                         date_bin=date, genre=m.get('genre', 'unknown'), pivot_id=v['pivot'],
                         shown_partner_ids=shown['partners']))
    for c, x in ck.items():
        v, source = verdicts[c]
        if historical['claims'][c]['grade'] != v['grade']:
            raise ValueError('Original grade mismatch')
        codes, reason = CODING[c]
        assert len(codes) == len(x['anchors'])
        anchors = []
        for anchor, code in zip(x['anchors'], codes):
            branch = BRANCH[anchor.split(':')[0]]
            # Celtic checks are explicitly attested in verdict reasons except C0006's
            # uncertain OCR apparatus. Keep verification distinct from contribution.
            verified = branch == 'Celtic' and c != 'C0006'
            if c in {'C0004', 'C0010', 'C0011', 'C0015', 'C0016'}:
                verified = True
            anchors.append(dict(id=anchor, branch=branch,
                                contribution={'+': 'contributes', '-': 'does not contribute', '?': 'uncertain'}[code],
                                verified=verified, reason=reason, evidence=f'{source}#{c}.reasons'))
        rows.append(dict(type='claim', claim_id=c, bundle_ids=x['bundles'], original_grade=v['grade'],
                         original_eligibility=dict(eligible=not historical['claims'][c]['excluded'], reason=(
                             'Original exclusion: Vedic and Avestan are one Indo-Iranian branch; two registered branches required.'
                             if c == 'C0011' else 'Included by original completed-wave anchoring decision; no recorded exclusion.')),
                         anchors=anchors, contribution_coding='retrospective 2026-10-25; original grades unchanged'))
    meta = dict(type='run', schema_version=1, run_id=a.run_id, reviewed_source_commit=a.source_commit,
                input_sha256={str(f.relative_to(Path.cwd()) if f.is_absolute() and f.is_relative_to(Path.cwd()) else f): digest(f) for f in paths}, total_original_bundles=len(full),
                completed_readers=[f'RC{i:03}' for i in range(1, 29)],
                order_provenance='Stage C key insertion order: slabs and entries emitted by pack_slabs in doc_order; loci arrays are ID-sorted',
                construction_evidence=dict(intended_decoys=stats['decoy_target'], successful_decoys=stats['decoy_bundles']),
                eligibility_evidence='Historical results-celtic.json excludes C0011; handoff SCI-02 explains same-branch reason')
    a.output.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in [meta, *rows]))


if __name__ == '__main__':
    main()
