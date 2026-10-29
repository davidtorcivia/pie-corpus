#!/usr/bin/env python3
"""Formula discovery round D2 (pre-registration: docs/research/discovery-r2-preregistration.md, commit 4dac0a3).

Subcommands, run in order:
  extract   one pass over the search index (D1's 8 branches and key rules, scripts/discovery_d1.py) plus each
            unit's Stage C-S layer -> data/research/discovery/d2/words.npz, keys.json, layers.json
  count     real index + 20 within-layer shuffles (seeds 0-19) -> per-run per-layer O and frequencies
  split     the 65 distinct best pairs of D1's control diagnostics -> tune (33) / test (32) by sha256
  tune      the parameter grid on the tune half only -> tune-grid.json, frozen-params.json
            (never computes test recall)
  test      test-half recall and false rate with frozen-params.json -> test-results.json
  packet    review set (only if the success criterion is met): top 40 new candidates + 10 null decoys,
            shuffled, opaque ids; key -> data/audits/keys/d2-key.json, packet -> docs/research/discovery/d2-packet.jsonl
            (--dry-run writes both to a scratch directory; prints counts only)

Implementation decisions (recorded before any D2 number was computed):
- Layers. The Stage C-S builder's layer function, as applied to this index by scripts/search_corpora.py
  (it calls build_8c_stageCS.prepare and stores each unit's `layer_status`, "included" when the unit is in the
  Stage C-S comparable layers incl. the thin-corpus amendment, else "excluded"). A layer is
  (corpus, layer_status); both statuses are layers (the excluded strata, e.g. later Greek, are strata too).
  Corpora are not merged and genre classes do not split layers.
- Window-based O and E. A window is a pair of keyed content-word slots of one unit at distance <= 4 in the
  unit's `words` list (D1's window). W_L = number of such slot pairs in layer L, S_L = keyed slots in L,
  n_L(x) = slots of L carrying key x. O_L(x,y) = slot pairs of L carrying x on one slot and y on the other
  (an event count: each attestation adds 1; same-group pairs dropped as in D1). E_L(x,y) = 2 n_L(x) n_L(y) W_L / S_L^2,
  the expected O_L when key sets are placed on slots independently with their layer frequencies. The
  shuffles permute key sets among the keyed slots of each layer, so Sum O = Sum E is checked on every run
  (count-stats.json, `sum_O_over_E`).
- Branch rule. A pair qualifies in layer L if O_L >= minO and O_L/E_L >= minOE; in a branch if it qualifies in
  any layer of the branch; the branch's log2 O/E is the max over its qualifying layers; the pair's score is
  the min over qualifying branches (>= 2 required). Identical for real and null runs.
- Exclusions: D1's frozen function-word list and top-50 groups (scripts/discovery_d1.py exclusion_sets),
  applied identically to real and null runs before the threshold. Threshold: the given percentile of the
  pooled null scores (all 20 seeds, after exclusions); a candidate's score must be strictly greater.
- Items: the 65 distinct best pairs of D1's control diagnostics = 62 distinct key pairs plus 3 formulas whose
  spec pairs a word with itself (mortal+self, brother+self, wish+self; listed in D1 as "never co-occurs";
  same-group pairs are dropped, so they cannot be recovered). Hash string: the two key ids sorted, joined by
  "|" (self items: "<id>|<id>"); items sorted by sha256 hex digest; first 33 tune, last 32 test.
  An item is recovered if a candidate key pair has the item's root-group pair (the pre-registered unit is the
  root-group pair).
- False rate = mean over seeds of null candidates (key pairs, after exclusions, score > threshold) / real
  candidates (key pairs), per grid cell.
- Tune choice: among the 12 cells with false rate <= 0.20, max tune recall; ties -> lower false rate, then
  higher percentile, then higher O/E, then higher min O.
"""
import argparse, collections, hashlib, importlib.util, itertools, json, os, shutil, sqlite3, sys, time, zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location('discovery_d1_for_d2', ROOT / 'scripts/discovery_d1.py')
D1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(D1)

DB = D1.DB
OUT = ROOT / 'data/research/discovery/d2'
D1OUT = D1.OUT
KEYFILE = ROOT / 'data/audits/keys/d2-key.json'
PACKET = ROOT / 'docs/research/discovery/d2-packet.jsonl'
BRANCHES, BRANCH_MAP, M, PSHIFT, WINDOW = D1.BRANCHES, D1.BRANCH_MAP, D1.M, D1.PSHIFT, D1.WINDOW
SEEDS = range(20)
PP = PSHIFT * PSHIFT               # pair code space
GRID = [dict(min_O=o, min_OE=r, pct=p) for o in (2, 3) for r in (2.0, 3.0, 4.0) for p in (95, 99)]
MIN_BRANCHES, MAX_FALSE, N_TUNE = 2, 0.20, 33
RETAIN_O = min(c['min_O'] for c in GRID)


# ---------------------------------------------------------------- extract
def _extract_chunk(args):
    lo, hi = args
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    out = []
    for uid, corpus, branch, payload in db.execute(
            'select id,corpus,branch,payload from units where id>=? and id<? order by id', (lo, hi)):
        if branch not in BRANCH_MAP:
            continue
        p = json.loads(zlib.decompress(payload)); ws = p['words']
        kw = [(i, sorted(set(w['root_ids']) | set(w['root_groups'])), w['root_groups'], w['root_ids'])
              for i, w in enumerate(ws) if w['root_ids'] or w['root_groups']]
        out.append((uid, corpus, branch, len(ws), kw, p['layer_status']))
    return out


def cmd_extract(a):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    st = DB.stat()
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    lo, hi = db.execute('select min(id),max(id) from units').fetchone()
    step = (hi - lo) // 256 + 1
    chunks = [(lo + i * step, lo + (i + 1) * step) for i in range(256)]
    lex = D1.lexicon(); keyid = {}; group_cache = {}; mism = 0; over = 0
    U_uid, U_corp, U_br, U_len, U_layer = [], [], [], [], []
    W_unit, W_pos, W_keys = [], [], []
    corpora, cidx, layers, lidx = [], {}, [], {}
    with ProcessPoolExecutor(24) as ex:
        for res in ex.map(_extract_chunk, chunks):
            for uid, corpus, branch, n, kw, status in res:
                u = len(U_uid)
                if corpus not in cidx:
                    cidx[corpus] = len(corpora); corpora.append(corpus)
                lay = (corpus, status)
                if lay not in lidx:
                    lidx[lay] = len(layers); layers.append(lay)
                U_uid.append(uid); U_corp.append(cidx[corpus]); U_br.append(BRANCHES.index(BRANCH_MAP[branch]))
                U_len.append(n); U_layer.append(lidx[lay])
                for pos, ks, groups, rids in kw:
                    ids = []
                    for k in ks:
                        if k not in keyid:
                            keyid[k] = len(keyid); group_cache[k] = D1.key_group(k, lex)
                        ids.append(keyid[k])
                    if set(groups) != {D1.key_group(r, lex) for r in rids}:
                        mism += 1
                    if len(ids) > M:
                        over += 1; ids = ids[:M]
                    W_unit.append(u); W_pos.append(pos); W_keys.append(ids + [-1] * (M - len(ids)))
    keys = sorted(keyid, key=keyid.get)
    groups = sorted({group_cache[k] for k in keys}); gid = {g: i for i, g in enumerate(groups)}
    kgroup = np.array([gid[group_cache[k]] for k in keys], dtype=np.int32)
    arr = dict(u_uid=np.array(U_uid, np.int64), u_corp=np.array(U_corp, np.int16), u_br=np.array(U_br, np.int8),
               u_len=np.array(U_len, np.int32), u_layer=np.array(U_layer, np.int16),
               w_unit=np.array(W_unit, np.int32), w_pos=np.array(W_pos, np.int32),
               w_keys=np.array(W_keys, np.int32), kgroup=kgroup)
    np.savez(OUT / 'words.npz', **arr)
    json.dump({'keys': keys, 'groups': groups, 'corpora': corpora, 'branches': BRANCHES,
               'layers': [list(l) for l in layers]}, open(OUT / 'keys.json', 'w'), ensure_ascii=False)
    # same index and key numbering as D1's caches (so D1's frozen exclusion sets apply by key index)
    d1 = np.load(D1OUT / 'words.npz'); d1k = json.load(open(D1OUT / 'keys.json'))
    same = {k: bool(np.array_equal(d1[k], arr[k])) for k in d1.files}
    same['keys'] = d1k['keys'] == keys; same['groups'] = d1k['groups'] == groups
    ul = np.bincount(arr['u_layer'], minlength=len(layers))
    sl = np.bincount(arr['u_layer'][arr['w_unit']], minlength=len(layers))
    lay_rows = [{'layer': i, 'corpus': c, 'status': s, 'branch': BRANCH_MAP[db.execute('select branch from units where corpus=? limit 1', (c,)).fetchone()[0]],
                 'units': int(ul[i]), 'keyed_words': int(sl[i])} for i, (c, s) in enumerate(layers)]
    lay_rows.sort(key=lambda r: (BRANCHES.index(r['branch']), r['corpus'], r['status']))
    json.dump({'definition': '(corpus, layer_status) from the index payload, as written by scripts/search_corpora.py '
                             'with build_8c_stageCS.prepare (Stage C-S layer filter incl. thin-corpus amendment)',
               'layers': lay_rows}, open(OUT / 'layers.json', 'w'), indent=1)
    stats = {'index': str(DB.relative_to(ROOT)), 'index_mtime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime)),
             'index_bytes': st.st_size, 'units': len(U_uid), 'keyed_words': len(W_unit), 'keys': len(keys),
             'groups': len(groups), 'layers': len(layers), 'words_over_M': over, 'group_mismatch_words': mism,
             'identical_to_d1_cache': same, 'seconds': round(time.time() - t0, 1)}
    json.dump(stats, open(OUT / 'extract-stats.json', 'w'), indent=1)
    print(json.dumps(stats, indent=1))


# ---------------------------------------------------------------- count
def load_words():
    z = np.load(OUT / 'words.npz')
    return {k: z[k] for k in z.files}


def nlayers():
    return len(json.load(open(OUT / 'keys.json'))['layers'])


def layer_branch():
    km = json.load(open(OUT / 'keys.json')); lay = json.load(open(OUT / 'layers.json'))['layers']
    b = {(r['corpus'], r['status']): BRANCHES.index(r['branch']) for r in lay}
    return np.array([b[tuple(l)] for l in km['layers']], np.int64)


def count_layers(W, keys_mat):
    """Per-layer window counts. Returns triples (layer, pair code, O), n[nl, nk] slot counts, S[nl], Wn[nl]."""
    unit, pos, kg = W['w_unit'], W['w_pos'], W['kgroup']
    wl = W['u_layer'][unit].astype(np.int64); nl = int(W['u_layer'].max()) + 1; nk = len(kg)
    S = np.bincount(wl, minlength=nl)
    kk = keys_mat.reshape(-1).astype(np.int64); rows = np.repeat(wl, M); ok = kk >= 0
    n = np.zeros((nl, nk), np.int64)
    np.add.at(n, (rows[ok], kk[ok]), 1)
    Wn = np.zeros(nl, np.int64)
    lp = []
    L = len(unit)
    for t in range(1, WINDOW + 1):
        i = np.arange(L - t)
        sel = (unit[i] == unit[i + t]) & (pos[i + t] - pos[i] <= WINDOW)
        i = i[sel]; j = i + t
        Wn += np.bincount(wl[i], minlength=nl)
        codes = []
        for a_ in range(M):
            x = keys_mat[i, a_]; mx = x >= 0
            if not mx.any():
                continue
            for b_ in range(M):
                y = keys_mat[j, b_]; m = mx & (y >= 0)
                if not m.any():
                    continue
                xx, yy, ii = x[m].astype(np.int64), y[m].astype(np.int64), i[m].astype(np.int64)
                m2 = kg[xx] != kg[yy]
                xx, yy, ii = xx[m2], yy[m2], ii[m2]
                codes.append(ii * PP + np.minimum(xx, yy) * PSHIFT + np.maximum(xx, yy))
        c = np.unique(np.concatenate(codes))          # one count per slot pair and key pair
        lp.append(wl[c // PP] * PP + c % PP)
    ub, cnt = np.unique(np.concatenate(lp), return_counts=True)
    return ub // PP, ub % PP, cnt.astype(np.int32), n, S, Wn


def expected(lay, pair, n, S, Wn):
    x, y = pair // PSHIFT, pair % PSHIFT
    return 2.0 * n[lay, x] * n[lay, y] * Wn[lay] / (S[lay].astype(np.float64) ** 2)


def _count_seed(seed):
    t0 = time.time()
    W = load_words(); K = W['w_keys']
    if seed is None:
        km = K; tag = 'real'
    else:
        rng = np.random.default_rng(seed); km = K.copy(); tag = f'null-{seed:02d}'
        wl = W['u_layer'][W['w_unit']]
        for l in np.unique(wl):
            idx = np.nonzero(wl == l)[0]
            km[idx] = K[rng.permutation(idx)]
    lay, pair, O, n, S, Wn = count_layers(W, km)
    lb = layer_branch()
    # Sum O vs Sum E over all different-group key pairs, per layer (E summed in closed form)
    kg = W['kgroup']; nl = len(S)
    sumO = np.bincount(lay, weights=O, minlength=nl)
    tot = n.sum(1).astype(np.float64)
    G = np.stack([np.bincount(kg, weights=n[l], minlength=int(kg.max()) + 1) for l in range(nl)])   # per-group slot-key totals
    sumE = Wn * (tot ** 2 - (G ** 2).sum(1)) / np.maximum(S, 1).astype(np.float64) ** 2
    # retain pairs with O >= RETAIN_O in layers of >= 2 branches (the loosest grid cell)
    m = O >= RETAIN_O
    pb = np.unique(pair[m] * 8 + lb[lay[m]])
    pc, nb_ = np.unique(pb // 8, return_counts=True)
    keep = np.isin(pair, pc[nb_ >= MIN_BRANCHES])
    np.savez(OUT / f'run-{tag}.npz', lay=lay[keep].astype(np.int16), pair=pair[keep], O=O[keep], n=n, S=S, Wn=Wn)
    if seed is None:
        np.savez(OUT / 'real-full.npz', lay=lay.astype(np.int16), pair=pair, O=O)
    return tag, int(len(np.unique(pair))), int(len(pc[nb_ >= MIN_BRANCHES])), \
        {'sum_O': float(sumO.sum()), 'sum_E': float(sumE.sum()), 'sum_O_over_E': float(sumO.sum() / sumE.sum()),
         'per_layer_O_over_E_range': [float(np.min(sumO[sumE > 0] / sumE[sumE > 0])), float(np.max(sumO[sumE > 0] / sumE[sumE > 0]))]}, \
        round(time.time() - t0, 1)


def cmd_count(a):
    t0 = time.time()
    seeds = [None] + list(SEEDS)
    if a.only:
        seeds = [None if s == 'real' else int(s) for s in a.only.split(',')]
    prev = json.load(open(OUT / 'count-stats.json')) if (OUT / 'count-stats.json').exists() else {}
    with ProcessPoolExecutor(a.jobs) as ex:
        for tag, npairs, nret, chk, sec in ex.map(_count_seed, seeds):
            prev[tag] = {'pairs': npairs, 'retained': nret, 'sum_check': chk, 'seconds': sec}
            print(tag, npairs, nret, round(chk['sum_O_over_E'], 4), sec, flush=True)
    prev['_wall_seconds_last'] = round(time.time() - t0, 1)
    json.dump(prev, open(OUT / 'count-stats.json', 'w'), indent=1)


# ---------------------------------------------------------------- candidate rule
_EXCL = None


def exclusions():
    """D1's frozen exclusion sets, by key index (extract checks the key numbering is D1's)."""
    global _EXCL
    if _EXCL is None:
        assert all(json.load(open(OUT / 'extract-stats.json'))['identical_to_d1_cache'].values())
        func, top, topg, _ = D1.exclusion_sets()
        assert topg == json.load(open(D1OUT / 'summary.json'))['top50_groups']
        _EXCL = (func, top)
    return _EXCL


def qualify(run, cell, lb):
    """Qualifying key pairs of one run under a grid cell, after exclusions: pairs, score, branch mask."""
    lay, pair, O = run['lay'].astype(np.int64), run['pair'], run['O']
    E = expected(lay, pair, run['n'], run['S'], run['Wn'])
    with np.errstate(divide='ignore'):
        R = np.where(E > 0, O / E, 0.0)
    q = (O >= cell['min_O']) & (R >= cell['min_OE'])
    func, top = exclusions()
    x, y = pair // PSHIFT, pair % PSHIFT
    q &= ~(func[x] | func[y] | (top[x] & top[y]))
    pb = pair[q] * 8 + lb[lay[q]]; s = np.log2(R[q])
    order = np.lexsort((-s, pb)); pb, s = pb[order], s[order]
    first = np.r_[True, pb[1:] != pb[:-1]]
    pb, s = pb[first], s[first]                    # branch score = max over qualifying layers
    pp, br = pb // 8, pb % 8
    up, inv, cnt = np.unique(pp, return_inverse=True, return_counts=True)
    mn = np.full(len(up), np.inf); np.minimum.at(mn, inv, s)
    mask = np.zeros(len(up), np.int64); np.bitwise_or.at(mask, inv, 1 << br)
    k = cnt >= MIN_BRANCHES
    return up[k], mn[k], mask[k]


def evaluate(cell, runs_null, run_real, lb):
    pooled, per = [], []
    for r in runs_null:
        _, s, _ = qualify(r, cell, lb); pooled.append(s)
    allp = np.concatenate(pooled)
    thr = float(np.percentile(allp, cell['pct']))
    null_c = [int((s > thr).sum()) for s in pooled]
    p, s, mask = qualify(run_real, cell, lb)
    c = s > thr
    return {'threshold_log2': thr, 'null_qualifying_mean': float(np.mean([len(s) for s in pooled])),
            'null_candidates_per_seed': null_c, 'null_candidates_mean': float(np.mean(null_c)),
            'real_qualifying': int(len(p)), 'real_candidates': int(c.sum()),
            'false_rate': float(np.mean(null_c) / c.sum()) if c.sum() else float('inf')}, (p[c], s[c], mask[c])


def load_runs():
    real = dict(np.load(OUT / 'run-real.npz'))
    nulls = [dict(np.load(OUT / f'run-null-{s:02d}.npz')) for s in SEEDS]
    return real, nulls


# ---------------------------------------------------------------- items and split
def cmd_split(a):
    diag = json.load(open(D1OUT / 'control-diagnostics.json'))['formulas']
    ws = {r['formula_id']: r for r in map(json.loads, open(ROOT / 'data/research/formulas/witness-scan.jsonl'))}
    items = collections.OrderedDict()
    for f in diag:
        if 'pair' in f:
            k = '|'.join(sorted(f['pair'])); pair = sorted(f['pair'])
        else:
            specs = ws[f['formula_id']]['specs']
            assert len(specs) == 1 and set(specs[0]['A']) == set(specs[0]['B'])
            a_ = specs[0]['A'][0]; k = f'{a_}|{a_}'; pair = [a_, a_]
        it = items.setdefault(k, {'pair': pair, 'self': pair[0] == pair[1], 'formulas': []})
        it['formulas'].append(f['formula_id'])
    assert len(items) == 65, len(items)
    for k, it in items.items():
        it['sha256'] = hashlib.sha256(k.encode()).hexdigest()
    order = sorted(items, key=lambda k: items[k]['sha256'])
    lex = D1.lexicon()
    gp = collections.defaultdict(list)
    for k in order:
        it = items[k]; it['half'] = 'tune' if order.index(k) < N_TUNE else 'test'
        it['group_pair'] = sorted(D1.key_group(x, lex) for x in it['pair'])
        gp[tuple(it['group_pair'])].append(k)
    shared = [{'group_pair': list(g), 'items': v, 'halves': [items[k]['half'] for k in v]} for g, v in gp.items() if len(v) > 1]
    out = {'hash_string': 'sorted key ids joined by "|"; self items "<id>|<id>"', 'n_tune': N_TUNE,
           'items': [dict(key=k, **items[k]) for k in order], 'shared_group_pairs': shared}
    json.dump(out, open(OUT / 'split.json', 'w'), ensure_ascii=False, indent=1)
    print('tune', sum(1 for k in order if items[k]['half'] == 'tune'), 'test', sum(1 for k in order if items[k]['half'] == 'test'),
          'self items by half', collections.Counter(items[k]['half'] for k in order if items[k]['self']), 'shared group pairs', shared)


def candidate_group_pairs(p, kg):
    return {frozenset((int(kg[c // PSHIFT]), int(kg[c % PSHIFT]))) for c in p.tolist()}


def item_group_pair(it, keys, groups):
    gidx = {g: i for i, g in enumerate(groups)}
    if it['self']:
        return None
    return frozenset(gidx.get(g, -1) for g in it['group_pair'])


def recall(half, cand_p, kg, keys, groups):
    sp = json.load(open(OUT / 'split.json'))['items']
    cg = candidate_group_pairs(cand_p, kg)
    hit, miss = [], []
    for it in sp:
        if it['half'] != half:
            continue
        g = item_group_pair(it, keys, groups)
        (hit if g is not None and g in cg else miss).append(it)
    return len(hit) / (len(hit) + len(miss)), hit, miss


def choose(rows):
    ok = [r for r in rows if r['false_rate'] <= MAX_FALSE]
    if not ok:
        return None
    return max(ok, key=lambda r: (r['tune_recall'], -r['false_rate'], r['cell']['pct'], r['cell']['min_OE'], r['cell']['min_O']))


def cmd_tune(a):
    t0 = time.time()
    km = json.load(open(OUT / 'keys.json')); keys, groups = km['keys'], km['groups']
    kg = np.load(OUT / 'words.npz')['kgroup']; lb = layer_branch()
    real, nulls = load_runs()
    rows = []
    for cell in GRID:
        ev, (p, s, mask) = evaluate(cell, nulls, real, lb)
        r, hit, miss = recall('tune', p, kg, keys, groups)
        row = {'cell': cell, **ev, 'real_candidate_group_pairs': len(candidate_group_pairs(p, kg)),
               'tune_recall': r, 'tune_recovered': [h['key'] for h in hit]}
        rows.append(row)
        print(f"minO={cell['min_O']} OE={cell['min_OE']} pct={cell['pct']}: thr={ev['threshold_log2']:.3f} "
              f"real={ev['real_candidates']} null_mean={ev['null_candidates_mean']:.1f} false={ev['false_rate']:.3f} "
              f"tune_recall={r:.3f} ({len(hit)}/{len(hit) + len(miss)})", flush=True)
    ch = choose(rows)
    json.dump({'grid': rows, 'seconds': round(time.time() - t0, 1)}, open(OUT / 'tune-grid.json', 'w'), indent=1)
    frozen = {'round': 'D2', 'chosen': ch['cell'] if ch else None,
              'rule': 'max tune recall s.t. false rate <= 0.20; ties: lower false rate, higher pct, higher O/E, higher min O',
              'tune_recall': ch['tune_recall'] if ch else None, 'false_rate': ch['false_rate'] if ch else None,
              'threshold_log2': ch['threshold_log2'] if ch else None, 'window': WINDOW, 'min_branches': MIN_BRANCHES,
              'seeds': list(SEEDS)}
    json.dump(frozen, open(OUT / 'frozen-params.json', 'w'), indent=1)
    print('chosen', json.dumps(frozen))


# ---------------------------------------------------------------- test
def diagnose_item(it, cell, thr, full, run, lb, keys, groups, kg):
    """Why an item is missed: its best key pair within the item's group pair, by rule step."""
    if it['self']:
        return {'stage': 'self pair (one word with itself): same-group pairs are not counted'}
    gidx = {g: i for i, g in enumerate(groups)}
    ga, gb = (gidx.get(g, -1) for g in it['group_pair'])
    if ga < 0 or gb < 0:
        return {'stage': 'key not in index'}
    fx, fy = full['pair'] // PSHIFT, full['pair'] % PSHIFT
    gx, gy = kg[fx], kg[fy]
    m = ((gx == ga) & (gy == gb)) | ((gx == gb) & (gy == ga))
    if not m.any():
        return {'stage': 'pair never co-occurs within the window'}
    lay, pair, O = full['lay'][m].astype(np.int64), full['pair'][m], full['O'][m]
    E = expected(lay, pair, run['n'], run['S'], run['Wn'])
    func, top = exclusions()
    best = None
    km = json.load(open(OUT / 'keys.json'))['layers']
    for c in np.unique(pair):
        s = pair == c
        per = [(int(l), int(o), float(e)) for l, o, e in zip(lay[s], O[s], E[s])]
        qb = collections.defaultdict(list); ob = set()
        for l, o, e in per:
            if o >= cell['min_O']:
                ob.add(lb[l])
                if o / e >= cell['min_OE']:
                    qb[lb[l]].append(np.log2(o / e))
        sc = min(max(v) for v in qb.values()) if len(qb) >= 2 else None
        x, y = int(c // PSHIFT), int(c % PSHIFT)
        excl = bool(func[x] or func[y] or (top[x] and top[y]))
        rank = (len(qb) >= 2 and not excl and sc > thr, len(qb), len(ob), sc or 0)
        if best is None or rank > best[0]:
            top_layers = sorted(per, key=lambda t: -t[1])[:6]
            best = (rank, [keys[x], keys[y]], sc, excl,
                    [{'layer': '/'.join(km[l]), 'branch': BRANCHES[lb[l]], 'O': o, 'E': round(e, 2), 'OE': round(o / e, 1) if e else None}
                     for l, o, e in top_layers])
    (ok, nq, no, _), kp, sc, excl, tl = best
    stage = ('recovered' if ok else 'excluded (function / top-50)' if nq >= 2 and excl else
             'qualifies in >= 2 branches, score <= threshold' if nq >= 2 else
             'O >= min O in >= 2 branches, but O/E >= min O/E in <= 1' if no >= 2 else 'O >= min O in <= 1 branch')
    return {'stage': stage, 'best_key_pair': kp, 'score_log2': sc, 'top_layers_by_O': tl}


def cmd_test(a):
    t0 = time.time()
    frozen = json.load(open(OUT / 'frozen-params.json')); cell = frozen['chosen']
    assert cell is not None
    km = json.load(open(OUT / 'keys.json')); keys, groups = km['keys'], km['groups']
    kg = np.load(OUT / 'words.npz')['kgroup']; lb = layer_branch()
    real, nulls = load_runs()
    ev, (p, s, mask) = evaluate(cell, nulls, real, lb)
    assert abs(ev['threshold_log2'] - frozen['threshold_log2']) < 1e-12
    r, hit, miss = recall('test', p, kg, keys, groups)
    full = dict(np.load(OUT / 'real-full.npz'))
    rows = []
    for it in hit + miss:
        d = diagnose_item(it, cell, ev['threshold_log2'], full, real, lb, keys, groups, kg)
        rows.append({'key': it['key'], 'formulas': it['formulas'], 'recovered': it in hit, **d})
    ok = r >= 0.30 and ev['false_rate'] <= MAX_FALSE
    res = {'cell': cell, **ev, 'real_candidate_group_pairs': len(candidate_group_pairs(p, kg)),
           'test_recall': r, 'test_recovered': len(hit), 'test_n': len(hit) + len(miss),
           'criterion_met': ok, 'items': rows, 'seconds': round(time.time() - t0, 1)}
    json.dump(res, open(OUT / 'test-results.json', 'w'), ensure_ascii=False, indent=1)
    print(f"test recall={r:.3f} ({len(hit)}/{len(hit) + len(miss)}) false_rate={ev['false_rate']:.3f} "
          f"real_candidates={ev['real_candidates']} criterion_met={ok}")
    print(json.dumps(collections.Counter(x['stage'] for x in rows), indent=1))


# ---------------------------------------------------------------- packet
def cmd_packet(a):
    t0 = time.time()
    test = json.load(open(OUT / 'test-results.json'))
    if not test['criterion_met']:
        sys.exit('success criterion not met: no packet')
    keyfile, packet = (Path(a.dry_run) / 'd2-key.json', Path(a.dry_run) / 'd2-packet.jsonl') if a.dry_run else (KEYFILE, PACKET)
    frozen = json.load(open(OUT / 'frozen-params.json')); cell = frozen['chosen']
    km = json.load(open(OUT / 'keys.json')); keys, groups = km['keys'], km['groups']
    kidx = {k: i for i, k in enumerate(keys)}; lex = D1.lexicon()
    W = load_words(); kg = W['kgroup']; kmat = W['w_keys']; lb = layer_branch()
    real, nulls = load_runs()
    ev, (cp, cs, cmask) = evaluate(cell, nulls, real, lb)
    thr = ev['threshold_log2']
    known = D1.known_group_pairs(kidx, lex, keys, kg)
    best = {}
    for c, s, msk in zip(cp.tolist(), cs.tolist(), cmask.tolist()):
        x, y = c // PSHIFT, c % PSHIFT
        gp = frozenset((groups[kg[x]], groups[kg[y]]))
        if gp not in best or s > best[gp][0]:
            best[gp] = (float(s), x, y, [b for b in range(len(BRANCHES)) if msk >> b & 1])
    new = [(gp, v) for gp, v in best.items() if gp not in known]
    new.sort(key=lambda t: (-t[1][0], sorted(t[0])))
    top40 = new[:40]
    # decoys: null-qualifying pairs (frozen cell, after exclusions), not real candidates (group level), not
    # known, with real co-occurrence in >= 2 branches; seeded sample (D1's rule)
    full = np.load(OUT / 'real-full.npz')
    fb = np.unique(full['pair'] * 8 + lb[full['lay'].astype(np.int64)])
    rp_pairs, rp_nb = np.unique(fb // 8, return_counts=True)
    rp_set = set(rp_pairs[rp_nb >= 2].tolist())
    Ob = collections.defaultdict(lambda: np.zeros(len(BRANCHES), np.int64))
    pool = {}
    for r in nulls:
        p, _, _ = qualify(r, cell, lb)
        for c in p.tolist():
            gp = frozenset((groups[kg[c // PSHIFT]], groups[kg[c % PSHIFT]]))
            if gp in best or gp in known or c not in rp_set:
                continue
            pool.setdefault(gp, c)
    need = set(pool.values())
    sel = np.isin(full['pair'], np.array(sorted(need), np.int64))
    for c, l, o in zip(full['pair'][sel].tolist(), full['lay'][sel].tolist(), full['O'][sel].tolist()):
        Ob[c][lb[l]] += o
    rng = np.random.default_rng(1001)
    pool_list = sorted(pool.items(), key=lambda t: sorted(t[0]))
    decoys, used = [], set()
    for i in rng.permutation(len(pool_list)):
        gp, c = pool_list[i]
        O = Ob[c]
        brs = [int(b) for b in np.argsort(-O, kind='stable') if O[b] > 0][:4]
        if len(brs) < 2 or gp in used:
            continue
        decoys.append((gp, c // PSHIFT, c % PSHIFT, brs)); used.add(gp)
        if len(decoys) == 10:
            break
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    cache = {}

    def unit_rec(u):
        if u not in cache:
            p = db.execute('select payload from units where id=?', (int(W['u_uid'][u]),)).fetchone()[0]
            cache[u] = json.loads(zlib.decompress(p))
        return cache[u]

    def describe(k):
        e = lex.get(keys[k], {})
        return {'id': keys[k], 'pie': e.get('form'), 'meaning': e.get('meaning')}
    items = []
    lrng = np.random.default_rng(2002)
    for kind, gp, x, y, brs, score in ([('candidate', gp, v[1], v[2], v[3][:4], v[0]) for gp, v in top40] +
                                      [('decoy', gp, x, y, brs, None) for gp, x, y, brs in decoys]):
        loci, counts = D1.find_loci((x, y), brs, W, kmat, cap=3, rng=lrng)
        L = []
        for b in brs:
            for u, px, py in loci.get(b, []):
                rec = unit_rec(u); ws = rec['words']
                L.append({'branch': BRANCHES[b], 'corpus': rec['corpus'], 'locus': rec['locus'],
                          'words': f"{ws[px]['form']} ~ {ws[py]['form']}", 'lemmas': f"{ws[px]['lemma']} ~ {ws[py]['lemma']}"})
        items.append({'kind': kind, 'pair': [describe(x), describe(y)], 'loci': L,
                      'branches_shown': [BRANCHES[b] for b in brs], 'score': score,
                      'group_pair': sorted(gp), 'real_units_by_branch': {BRANCHES[int(b)]: n for b, n in counts.items()}})
    srng = np.random.default_rng(3003)
    perm = srng.permutation(len(items))
    ids = [f'D2-{i:03d}' for i in srng.choice(900, len(items), replace=False) + 100]
    pk, key = [], {}
    for pid, i in zip(ids, perm):
        it = items[i]
        pk.append({'id': pid, 'words': it['pair'], 'loci': it['loci']})
        key[pid] = {k: it[k] for k in ('kind', 'score', 'group_pair', 'branches_shown', 'real_units_by_branch')}
    pk.sort(key=lambda r: r['id'])
    keyfile.parent.mkdir(parents=True, exist_ok=True); packet.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'round': 'D2', 'cell': cell, 'threshold_log2': thr, 'items': key}, open(keyfile, 'w'), ensure_ascii=False, indent=1)
    with open(packet, 'w') as f:
        for r in pk:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    nloci = collections.Counter((it['kind'], len(it['loci'])) for it in items)
    stats = {'dry_run': bool(a.dry_run), 'candidate_group_pairs': len(best), 'new_group_pairs': len(new),
             'known_group_pairs_among_candidates': len(best) - len(new), 'review_candidates': len(top40),
             'decoys': len(decoys), 'decoy_pool_group_pairs': len(pool), 'packet_items': len(pk),
             'items_without_loci': sum(1 for it in items if not it['loci']),
             'loci_count_hist': {f'{k}:{n}': v for (k, n), v in sorted(nloci.items())},
             'packet_seconds': round(time.time() - t0, 1)}
    json.dump(stats, open(OUT / ('packet-dryrun-stats.json' if a.dry_run else 'packet-stats.json'), 'w'), indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == '__main__':
    os.chdir(ROOT)
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('extract')
    c = sp.add_parser('count'); c.add_argument('--jobs', type=int, default=7); c.add_argument('--only')
    sp.add_parser('split'); sp.add_parser('tune'); sp.add_parser('test')
    p = sp.add_parser('packet'); p.add_argument('--dry-run', metavar='DIR')
    a = ap.parse_args()
    {'extract': cmd_extract, 'count': cmd_count, 'split': cmd_split, 'tune': cmd_tune, 'test': cmd_test,
     'packet': cmd_packet}[a.cmd](a)
