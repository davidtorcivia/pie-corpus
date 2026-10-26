"""Export blind 8c review packets, retaining etymological qualifications.

Defaults reproduce Stage C. For Stage C-S, supply its input/output paths,
--prefix S and --seed 889. The optional positional parts count remains supported.
Reader confidence and provenance are recorded only in the separate key.
"""
import argparse
import json
import pathlib
import random

ROOT = pathlib.Path('/Users/david/AI/PIE')


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    stage = ROOT / 'data/research/8c/stageC'
    parser.add_argument('legacy_parts', nargs='?', type=int, help=argparse.SUPPRESS)
    parser.add_argument('--claims-dir', type=pathlib.Path, default=stage / 'claims')
    parser.add_argument('--slabs-dir', type=pathlib.Path, default=stage / 'slabs')
    parser.add_argument('--out-dir', type=pathlib.Path, default=stage / 'review')
    parser.add_argument('--key-out', type=pathlib.Path,
                        default=ROOT / 'data/audits/keys/8c-stageC-claims-key.json')
    parser.add_argument('--prefix', default='C', help='claim ID prefix; inputs match R<prefix>*.jsonl')
    parser.add_argument('--seed', type=int, default=888)
    parser.add_argument('--parts', type=int, default=None)
    args = parser.parse_args(argv)
    if args.parts is not None and args.legacy_parts is not None:
        parser.error('use either --parts or the positional parts count')
    args.parts = args.parts if args.parts is not None else (args.legacy_parts if args.legacy_parts is not None else 4)
    if not 1 <= args.parts <= 16:
        parser.error('parts must be between 1 and 16')
    if not args.prefix or not args.prefix.isalnum():
        parser.error('prefix must be nonempty and alphanumeric')
    return args


def strip(p):
    return {'id': p.get('id'), 'corpus': p.get('corpus'), 'locus': p.get('locus'),
            'lines': [{'role': ln.get('role'), 'locus': ln.get('locus'), 'text': ln.get('text'),
                       'words': [{'form': w.get('form'), 'lemma': w.get('lemma'),
                                  'etymon': [({'form': e.get('form'), 'qualification': e['qualification']}
                                             if 'qualification' in e else e.get('form')) for e in (w.get('etymon') or []) if isinstance(e, dict)]}
                                 for w in ln.get('words', [])]} for ln in p.get('lines', [])]}


def main(argv=None):
    args = parse_args(argv)
    claims = []
    for f in sorted(args.claims_dir.glob(f"R{args.prefix}*.jsonl")):
        with f.open(encoding='utf-8') as source:
            for line in source:
                if line.strip():
                    c = json.loads(line)
                    if not c.get('done') and not c.get('none'):
                        claims.append(c)
    print('claims', len(claims))
    slabs = {c['slab'] for c in claims}
    P = {}
    for s in slabs:
        with (args.slabs_dir / f"{s}.json").open(encoding='utf-8') as source:
            d = json.load(source)
        ps = d['passages']
        for pid, p in (ps.items() if isinstance(ps, dict) else ((p['id'], p) for p in ps)):
            P[(s, pid)] = p
    rng = random.Random(args.seed); rng.shuffle(claims)
    out, key, miss = [], {}, []
    for k, c in enumerate(claims):
        cid = f"{args.prefix}{k+1:04d}"
        anchors = []
        for a in c.get('anchors', []):
            x = P.get((c['slab'], a))
            if x is None: miss.append((c['reader'], a))
            else: anchors.append(strip(x))
        out.append({'claim': cid, 'anchors': anchors, 'support': c.get('support', []), 'words': c.get('words', []),
                    'cognate': c.get('cognate'), 'drift_or_renewal': c.get('drift_or_renewal'),
                    'shared_syntax': c.get('shared_syntax'), 'context': c.get('context'), 'phrase': c.get('phrase')})
        key[cid] = {'slab': c['slab'], 'bundles': c.get('bundles', []), 'reader': c['reader'],
                    'confidence': c.get('confidence'), 'recalled': c.get('recalled'), 'anchors': c.get('anchors', [])}
    d = args.out_dir; d.mkdir(parents=True, exist_ok=True)
    n = len(out)
    for i in range(args.parts):
        name = 'ABCDEFGHIJKLMNOP'[i]
        part = out[i*n//args.parts:(i+1)*n//args.parts]
        (d/f'claims-{name}.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in part), 'utf-8')
        print(name, len(part))
    args.key_out.parent.mkdir(parents=True, exist_ok=True)
    args.key_out.write_text(json.dumps(key, ensure_ascii=False, indent=1), 'utf-8')
    print('missing anchors', len(miss), miss[:10])


if __name__ == '__main__':
    main()
