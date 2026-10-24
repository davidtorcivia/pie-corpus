"""Score 8c Stage C (Celtic wave) as Stage B: per-bundle claim weights, real vs decoy, permutation test."""
import json, random, collections
ROOT = '/Users/david/AI/PIE'
key = json.load(open(ROOT+'/data/audits/keys/8c-stageC-key.json'))['slabs']
asg = json.load(open(ROOT+'/data/research/8c/stageC/assignment.json'))['slabs']
READ = {s for s, r in asg.items() if r <= 'RC028'}
kind, group, meta = {}, {}, {}
for slab, bs in key.items():
    if slab not in READ: continue
    for b, v in bs.items():
        kind[(slab, b)] = v['kind']; group[(slab, b)] = v['pivot_group']; meta[(slab, b)] = (v['pivot_corpus'], v.get('pivot_meta'))
ck = json.load(open(ROOT+'/data/audits/keys/8c-stageC-claims-key.json'))
V, R = {}, {}
for n in 'AB':
    for l in open(f'{ROOT}/data/research/8c/stageC/review/verdicts-{n}.jsonl', encoding='utf-8'):
        v = json.loads(l); V[v['claim']] = v['grade']; R[v['claim']] = v
EXCL = {c for c, x in ck.items() if x['reader'] == 'RC028' and x['confidence'] == 'medium'}   # anchoring rule (pre-reg)
print('excluded (anchoring):', EXCL, [V[c] for c in EXCL])
def run(sel):
    bundles = sorted(b for b in kind if sel(b)); labels = [kind[b] for b in bundles]; bset = set(bundles)
    def weights(grades):
        w = collections.Counter(); unk = 0
        for c, g in V.items():
            if g not in grades or c in EXCL: continue
            bs = [(ck[c]['slab'], b) for b in ck[c]['bundles'] if (ck[c]['slab'], b) in bset]
            if not bs: unk += 1; continue
            for b in bs: w[b] += 1/len(bs)
        return w, unk
    def stat(w, lab):
        r = [w[b] for b, l in zip(bundles, lab) if l == 'real']; d = [w[b] for b, l in zip(bundles, lab) if l != 'real']
        return sum(r)/len(r), sum(d)/len(d)
    def perm(w):
        r, d = stat(w, labels); obs = r-d; rng = random.Random(0); lab = labels[:]; ge = 0
        for _ in range(10000):
            rng.shuffle(lab); rr, dd = stat(w, lab)
            if rr-dd >= obs-1e-15: ge += 1
        return r, d, (ge+1)/10001
    out = {'bundles': dict(collections.Counter(labels))}
    for name, gr in (('accepted', {'accepted'}), ('accepted+weak', {'accepted', 'weak'}), ('all claims', {'accepted', 'weak', 'reject'})):
        w, unk = weights(gr); r, d, p = perm(w)
        out[name] = dict(real_per_bundle=r, decoy_per_bundle=d, ratio=(r/d if d else None), p=p, outside_selection=unk)
        print(f"  {name}: real {r*1000:.3f}/1000, decoy {d*1000:.3f}/1000, ratio {(r/d) if d else 'inf' if r else 'n/a'}, p={p:.4f}, outside {unk}")
    return out
res = {}
print('(i) Celtic-pivot bundles'); res['celtic_pivot'] = run(lambda b: group[b] == 'celtic')
print('all bundles read (28 slabs; not measure ii)'); res['all_read'] = run(lambda b: True)
cl = collections.Counter(); per = {}
for c, g in V.items():
    ks = {kind.get((ck[c]['slab'], b)) for b in ck[c]['bundles']}
    t = 'decoy-only' if ks == {'decoy'} else 'mixed' if 'decoy' in ks else 'real-only' if ks == {'real'} else 'unknown'
    cl[(t, g)] += 1
    per[c] = dict(reader=ck[c]['reader'], slab=ck[c]['slab'], bundles=ck[c]['bundles'], kinds=sorted(k or '?' for k in ks),
                  confidence=ck[c]['confidence'], recalled=ck[c]['recalled'], grade=g, excluded=c in EXCL)
print(dict(cl))
cal = collections.defaultdict(collections.Counter)
for c, g in V.items(): cal[ck[c]['confidence']][g] += 1
print({k: dict(v) for k, v in cal.items()})
for c in sorted(per): print(c, per[c])
json.dump({'scores': res, 'excluded_anchoring': sorted(EXCL), 'claim_level': {f'{a}|{b}': n for (a, b), n in cl.items()},
           'calibration': {k: dict(v) for k, v in cal.items()}, 'claims': per},
          open(ROOT+'/data/research/8c/stageC/results-celtic.json', 'w'), indent=1, ensure_ascii=False)
