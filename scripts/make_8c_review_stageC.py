"""Blind review packets for 8c Stage C (as Stage B): shuffled claims without slab, bundle, reader,
confidence; key to data/audits/keys/8c-stageC-claims-key.json. usage: python3 -I stageC_review_prep.py <parts>"""
import json, glob, random, pathlib, sys
ROOT = pathlib.Path('/Users/david/AI/PIE')
parts = int(sys.argv[1]) if len(sys.argv) > 1 else 4
claims = []
for f in sorted(glob.glob(str(ROOT/'data/research/8c/stageC/claims/RC*.jsonl'))):
    for l in open(f, encoding='utf-8'):
        if l.strip():
            c = json.loads(l)
            if not c.get('done') and not c.get('none'): claims.append(c)
print('claims', len(claims))
slabs = {c['slab'] for c in claims}
P = {}
for s in slabs:
    d = json.load(open(ROOT/f'data/research/8c/stageC/slabs/{s}.json', encoding='utf-8'))
    ps = d['passages']
    for pid, p in (ps.items() if isinstance(ps, dict) else ((p['id'], p) for p in ps)):
        P[(s, pid)] = p
def strip(p):
    return {'id': p.get('id'), 'corpus': p.get('corpus'), 'locus': p.get('locus'),
            'lines': [{'role': ln.get('role'), 'locus': ln.get('locus'), 'text': ln.get('text'),
                       'words': [{'form': w.get('form'), 'lemma': w.get('lemma'),
                                  'etymon': [e.get('form') for e in (w.get('etymon') or []) if isinstance(e, dict)]}
                                 for w in ln.get('words', [])]} for ln in p.get('lines', [])]}
rng = random.Random(888); rng.shuffle(claims)
out, key, miss = [], {}, []
for k, c in enumerate(claims):
    cid = f"C{k+1:04d}"
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
d = ROOT/'data/research/8c/stageC/review'; d.mkdir(exist_ok=True)
n = len(out)
for i in range(parts):
    name = 'ABCDEFGHIJKLMNOP'[i]
    part = out[i*n//parts:(i+1)*n//parts]
    (d/f'claims-{name}.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in part), 'utf-8')
    print(name, len(part))
(ROOT/'data/audits/keys/8c-stageC-claims-key.json').write_text(json.dumps(key, ensure_ascii=False, indent=1), 'utf-8')
print('missing anchors', len(miss), miss[:10])
