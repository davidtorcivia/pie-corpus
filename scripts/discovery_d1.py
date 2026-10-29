#!/usr/bin/env python3
"""Formula discovery round D1 (pre-registration: docs/research/discovery-r1-preregistration.md).

Subcommands, run in order:
  extract   one pass over the search index (8 pre-registered branches) -> keyed-word arrays
            (cache: data/research/discovery/d1/words.npz, keys.json)
  count     real index + 20 within-corpus shuffles (seeds 0-19) -> per-run qualifying pairs
            (cache: data/research/discovery/d1/run-real.npz, run-null-<seed>.npz, real-pairs.npz)
  freq      dump the top keys by unit count (for freezing the function-word list; no pairs)
  control   candidate rule + exclusions, null threshold, positive-control recall
            (writes summary.json; prints recall and known-formula ids only, never candidates)
  packet    review set: top 40 new candidates (group-pair level) + 10 null decoys, shuffled,
            opaque ids; key -> data/audits/keys/d1-key.json, packet -> docs/research/discovery/d1-packet.jsonl
            (prints counts only)

Counting follows scripts/collocates_8c.py: a word's keys are root_ids | root_groups; a pair is two keys on
different content words (positions in the unit's `words` list) at distance <= 4; O = units with the pair;
E = n_b(x) * n_b(y) / N_b with n_b = units containing the key in that branch. Pairs whose two keys are
in the same root group are not two-word phrases and are dropped. Shuffle: within each corpus the key sets
of keyed word slots are permuted (unkeyed slots and all positions fixed), preserving unit size, the number
of keyed words per unit, and per-corpus root token frequencies.
"""
import argparse, collections, json, math, os, sqlite3, sys, time, zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DB = ROOT / 'data/research/8c/search-index/corpora.sqlite'
OUT = ROOT / 'data/research/discovery/d1'
KEYFILE = ROOT / 'data/audits/keys/d1-key.json'
PACKET = ROOT / 'docs/research/discovery/d1-packet.jsonl'
BRANCH_MAP = {'Indo-Iranian': 'Indo-Iranian', 'Greek': 'Greek', 'Italic': 'Italic', 'Celtic': 'Celtic',
              'Germanic': 'Germanic', 'Baltic': 'Balto-Slavic', 'Slavic': 'Balto-Slavic',
              'Armenian': 'Armenian', 'Anatolian': 'Anatolian'}
BRANCHES = ['Indo-Iranian', 'Greek', 'Italic', 'Celtic', 'Germanic', 'Balto-Slavic', 'Armenian', 'Anatolian']
WINDOW, MIN_O, MIN_OE, MIN_BRANCHES, SEEDS, TOP_FREQ = 4, 3, 3.0, 2, range(20), 50
FUNCTION_POS = {'pron', 'particle', 'det', 'conj', 'intj', 'adv', 'prefix', 'suffix', 'infix'}
M = 7          # max keys per word (extract checks words_over_M == 0)
PSHIFT = 1 << 14  # key ids < 16384


def lexicon():
    return {e['id']: e for e in map(json.loads, (ROOT / 'data/lexicon/lexicon.jsonl').read_text('utf-8').splitlines()) if e}


def key_group(k, lex):
    from pie.formula_search import group_of
    e = lex.get(k)
    return group_of(e) if e else k


# ---------------------------------------------------------------- extract
def _extract_chunk(args):
    lo, hi = args
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    out = []
    for uid, corpus, branch, payload in db.execute(
            'select id,corpus,branch,payload from units where id>=? and id<? order by id', (lo, hi)):
        if branch not in BRANCH_MAP:
            continue
        ws = json.loads(zlib.decompress(payload))['words']
        kw = [(i, sorted(set(w['root_ids']) | set(w['root_groups'])), w['root_groups'], w['root_ids'])
              for i, w in enumerate(ws) if w['root_ids'] or w['root_groups']]
        out.append((uid, corpus, branch, len(ws), kw))
    return out


def cmd_extract(a):
    t0 = time.time(); OUT.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    lo, hi = db.execute('select min(id),max(id) from units').fetchone()
    step = (hi - lo) // 256 + 1
    chunks = [(lo + i * step, lo + (i + 1) * step) for i in range(256)]
    lex = lexicon(); keyid = {}; group_cache = {}; mism = 0; nkw = 0; over = 0
    U_uid, U_corp, U_br, U_len = [], [], [], []
    W_unit, W_pos, W_keys = [], [], []
    corpora = []; cidx = {}
    with ProcessPoolExecutor(24) as ex:
        for res in ex.map(_extract_chunk, chunks):
            for uid, corpus, branch, n, kw in res:
                u = len(U_uid)
                if corpus not in cidx:
                    cidx[corpus] = len(corpora); corpora.append(corpus)
                U_uid.append(uid); U_corp.append(cidx[corpus]); U_br.append(BRANCHES.index(BRANCH_MAP[branch])); U_len.append(n)
                for pos, ks, groups, rids in kw:
                    ids = []
                    for k in ks:
                        if k not in keyid:
                            keyid[k] = len(keyid); group_cache[k] = key_group(k, lex)
                        ids.append(keyid[k])
                    # consistency: the payload's groups should be the groups of its keys
                    if set(groups) != {key_group(r, lex) for r in rids}:
                        mism += 1
                    if len(ids) > M:
                        over += 1; ids = ids[:M]
                    W_unit.append(u); W_pos.append(pos); W_keys.append(ids + [-1] * (M - len(ids))); nkw += 1
    keys = sorted(keyid, key=keyid.get)
    groups = sorted({group_cache[k] for k in keys})
    gid = {g: i for i, g in enumerate(groups)}
    # groups may themselves be keys; a key's group index
    kgroup = np.array([gid[group_cache[k]] for k in keys], dtype=np.int32)
    assert len(keys) < PSHIFT
    np.savez(OUT / 'words.npz', u_uid=np.array(U_uid, np.int64), u_corp=np.array(U_corp, np.int16),
             u_br=np.array(U_br, np.int8), u_len=np.array(U_len, np.int32),
             w_unit=np.array(W_unit, np.int32), w_pos=np.array(W_pos, np.int32),
             w_keys=np.array(W_keys, np.int32), kgroup=kgroup)
    json.dump({'keys': keys, 'groups': groups, 'corpora': corpora, 'branches': BRANCHES}, open(OUT / 'keys.json', 'w'), ensure_ascii=False)
    stats = {'units': len(U_uid), 'keyed_words': nkw, 'keys': len(keys), 'groups': len(groups),
             'words_over_M': over, 'group_mismatch_words': mism, 'seconds': round(time.time() - t0, 1),
             'units_by_branch': dict(collections.Counter(BRANCHES[b] for b in U_br))}
    json.dump(stats, open(OUT / 'extract-stats.json', 'w'), indent=1)
    print(json.dumps(stats, indent=1))


# ---------------------------------------------------------------- count
def load_words():
    z = np.load(OUT / 'words.npz')
    return {k: z[k] for k in z.files}


def count_run(W, keys_mat):
    """Per-branch O (pair -> units) and n (key -> units) for one (real or shuffled) key assignment.
    Returns pair codes (x*PSHIFT+y, x<y), O[nb, npairs], n[nb, nkeys], N[nb]."""
    unit, pos, kg = W['w_unit'], W['w_pos'], W['kgroup']
    ubr = W['u_br'].astype(np.int64); nb = len(BRANCHES); nk = len(kg)
    N = np.bincount(ubr, minlength=nb)
    # key unit counts
    rows = np.repeat(unit.astype(np.int64), M); kk = keys_mat.reshape(-1).astype(np.int64)
    ok = kk >= 0
    uk = np.unique(rows[ok] * PSHIFT + kk[ok])
    n = np.zeros((nb, nk), np.int64)
    np.add.at(n, (ubr[uk // PSHIFT], uk % PSHIFT), 1)
    # pair incidences per unit
    codes = []
    L = len(unit)
    for t in range(1, WINDOW + 1):
        i = np.arange(L - t)
        sel = (unit[i] == unit[i + t]) & (pos[i + t] - pos[i] <= WINDOW)
        i = i[sel]; j = i + t
        for a_ in range(M):
            x = keys_mat[i, a_]
            mx = x >= 0
            if not mx.any():
                continue
            for b_ in range(M):
                y = keys_mat[j, b_]
                m = mx & (y >= 0)
                if not m.any():
                    continue
                xx, yy, uu = x[m].astype(np.int64), y[m].astype(np.int64), unit[i[m]].astype(np.int64)
                m2 = kg[xx] != kg[yy]
                xx, yy, uu = xx[m2], yy[m2], uu[m2]
                lo_, hi_ = np.minimum(xx, yy), np.maximum(xx, yy)
                codes.append(np.unique(uu * (PSHIFT * PSHIFT) + lo_ * PSHIFT + hi_))
    allc = np.unique(np.concatenate(codes))
    uu = allc // (PSHIFT * PSHIFT); pc = allc % (PSHIFT * PSHIFT)
    bc = ubr[uu] * (PSHIFT * PSHIFT) + pc
    ub, cnt = np.unique(bc, return_counts=True)
    pairs, inv = np.unique(ub % (PSHIFT * PSHIFT), return_inverse=True)
    O = np.zeros((nb, len(pairs)), np.int32)
    O[ub // (PSHIFT * PSHIFT), inv] = cnt
    return pairs, O, n, N


def qualify(pairs, O, n, N):
    """Pairs meeting O>=3 and O/E>=3 in >=2 branches; score = min log2 O/E over qualifying branches."""
    x, y = pairs // PSHIFT, pairs % PSHIFT
    E = n[:, x] * n[:, y] / N[:, None]
    with np.errstate(divide='ignore', invalid='ignore'):
        R = np.where(E > 0, O / E, 0)
    Q = (O >= MIN_O) & (R >= MIN_OE)
    nq = Q.sum(0)
    keep = nq >= MIN_BRANCHES
    Rk = np.where(Q[:, keep], R[:, keep], np.inf)
    score = np.log2(Rk.min(0))
    return {'pairs': pairs[keep], 'score': score, 'O': O[:, keep], 'E': E[:, keep].astype(np.float32),
            'qmask': Q[:, keep]}


def _count_seed(seed):
    t0 = time.time()
    W = load_words()
    K = W['w_keys']
    if seed is None:
        km = K; tag = 'real'
    else:
        rng = np.random.default_rng(seed); km = K.copy(); tag = f'null-{seed:02d}'
        wc = W['u_corp'][W['w_unit']]
        for c in np.unique(wc):
            idx = np.nonzero(wc == c)[0]
            km[idx] = K[rng.permutation(idx)]
    pairs, O, n, N = count_run(W, km)
    q = qualify(pairs, O, n, N)
    np.savez(OUT / f'run-{tag}.npz', **q, n=n, N=N)
    if seed is None:
        # real pair table, pairs with any co-occurrence in >= 2 branches (for decoy locus availability)
        m = (O > 0).sum(0) >= 2
        np.savez(OUT / 'real-pairs.npz', pairs=pairs[m], O=O[:, m])
    return tag, len(pairs), len(q['pairs']), round(time.time() - t0, 1)


def cmd_count(a):
    t0 = time.time()
    seeds = [None] + list(SEEDS)
    if a.only:
        seeds = [None if s == 'real' else int(s) for s in a.only.split(',')]
    times = {}
    with ProcessPoolExecutor(a.jobs) as ex:
        for tag, npairs, nq, sec in ex.map(_count_seed, seeds):
            times[tag] = {'pairs': int(npairs), 'qualifying_before_exclusion': int(nq), 'seconds': sec}
            print(tag, npairs, nq, sec, flush=True)
    prev = json.load(open(OUT / 'count-stats.json')) if (OUT / 'count-stats.json').exists() else {}
    prev.update(times); prev['_wall_seconds_last'] = round(time.time() - t0, 1)
    json.dump(prev, open(OUT / 'count-stats.json', 'w'), indent=1)


# ---------------------------------------------------------------- exclusions
def key_meta():
    km = json.load(open(OUT / 'keys.json'))
    return km['keys'], km['groups']


def exclusion_sets():
    """Function-word key ids, and key ids whose group is in the top-50 groups by unit count (8 branches)."""
    keys, groups = key_meta(); lex = lexicon()
    W = load_words(); kg = W['kgroup']
    run = np.load(OUT / 'run-real.npz'); n = run['n'].sum(0)
    # unit count of a group = unit count of the group's own key when the group is a key (every keyed word
    # carries its group among its keys); otherwise max over its lexeme keys
    kidx = {k: i for i, k in enumerate(keys)}
    gcount = np.zeros(len(groups), np.int64)
    for gi, g in enumerate(groups):
        if g in kidx:
            gcount[gi] = n[kidx[g]]
    for i in range(len(keys)):
        gcount[kg[i]] = max(gcount[kg[i]], n[i])
    top_groups = set(np.argsort(-gcount)[:TOP_FREQ].tolist())
    top_keys = np.array([kg[i] in top_groups for i in range(len(keys))])
    func_groups = set()
    func = np.zeros(len(keys), bool)
    for i, k in enumerate(keys):
        e = lex.get(k)
        if k.startswith('closed:') or (e and e.get('pos') in FUNCTION_POS):
            func[i] = True
    # frozen additions (before any candidate was computed or read): ids or groups listed here are function words
    extra = set(json.load(open(OUT / 'function-extra.json'))['ids']) if (OUT / 'function-extra.json').exists() else set()
    for i, k in enumerate(keys):
        if k in extra or groups[kg[i]] in extra:
            func[i] = True
    return func, top_keys, [groups[g] for g in sorted(top_groups, key=lambda g: -gcount[g])], gcount


def cmd_freq(a):
    keys, groups = key_meta(); lex = lexicon()
    run = np.load(OUT / 'run-real.npz'); n = run['n'].sum(0)
    func, top, topg, gcount = exclusion_sets()
    for i in np.argsort(-n)[:a.top]:
        k = keys[i]; e = lex.get(k, {})
        print(f"{n[i]:8d} {'F' if func[i] else ' '}{'T' if top[i] else ' '} {k:40s} {e.get('pos')!s:8s} {str(e.get('meaning'))[:50]}")


def apply_exclusions(q, func, top):
    x, y = q['pairs'] // PSHIFT, q['pairs'] % PSHIFT
    keep = ~(func[x] | func[y] | (top[x] & top[y]))
    return {k: (v[..., keep] if k in ('O', 'E', 'qmask') else v[keep]) for k, v in q.items() if k in ('pairs', 'score', 'O', 'E', 'qmask')}


# ---------------------------------------------------------------- control
def expand(ids, keys_idx, lex):
    out = set()
    for i in ids:
        for k in {i, key_group(i, lex)}:
            if k in keys_idx:
                out.add(keys_idx[k])
    return out


def threshold_and_candidates():
    func, top, topg, _ = exclusion_sets()
    null_scores, per_seed = [], {}
    for s in SEEDS:
        q = apply_exclusions(dict(np.load(OUT / f'run-null-{s:02d}.npz')), func, top)
        null_scores.append(q['score']); per_seed[s] = int(len(q['score']))
    pooled = np.concatenate(null_scores)
    thr = float(np.percentile(pooled, 99)) if len(pooled) else float('-inf')
    real = apply_exclusions(dict(np.load(OUT / 'run-real.npz')), func, top)
    qual_real = int(len(real['pairs']))
    m = real['score'] > thr
    cand = {k: (v[..., m] if k in ('O', 'E', 'qmask') else v[m]) for k, v in real.items()}
    return thr, pooled, per_seed, qual_real, cand, func, top, topg


def cmd_control(a):
    t0 = time.time()
    keys, groups = key_meta(); kidx = {k: i for i, k in enumerate(keys)}; lex = lexicon()
    thr, pooled, per_seed, qual_real, cand, func, top, topg = threshold_and_candidates()
    cset = set(cand['pairs'].tolist())
    rows = [json.loads(l) for l in open(ROOT / 'data/research/formulas/witness-scan.jsonl')]
    mb = [r for r in rows if r['class'] == 'multi-branch' and r['source'] in ('west', 'watkins')]
    rec, miss = [], []
    for r in mb:
        hit = None; searchable = False
        for s in r['specs']:
            A, B = expand(s['A'], kidx, lex), expand(s['B'], kidx, lex)
            if A and B:
                searchable = True
            for x in A:
                for y in B:
                    if x != y and min(x, y) * PSHIFT + max(x, y) in cset:
                        hit = s['spec']; break
                if hit: break
            if hit: break
        (rec if hit else miss).append({'formula_id': r['formula_id'], 'subclass': r['subclass'],
                                        'real_branches': r['real_branches'], 'spec': hit or [s['spec'] for s in r['specs']],
                                        'keys_in_index': searchable})
    recall = len(rec) / len(mb)
    # why missed: per-missed formula, does the real (pre-threshold) qualifying list hold it, is it excluded
    allq = dict(np.load(OUT / 'run-real.npz')); allq_set = set(allq['pairs'].tolist())
    for r in miss:
        spec_rows = [s for s in next(x for x in mb if x['formula_id'] == r['formula_id'])['specs']]
        why = 'not qualifying in >=2 branches'
        for s in spec_rows:
            A, B = expand(s['A'], kidx, lex), expand(s['B'], kidx, lex)
            for x in A:
                for y in B:
                    c = min(x, y) * PSHIFT + max(x, y)
                    if c in allq_set:
                        why = 'excluded (function/top-50)' if (func[x] or func[y] or (top[x] and top[y])) else 'qualifies, below null threshold'
                        if why.startswith('qualifies'): break
        if not r['keys_in_index']:
            why = 'keys not in index'
        r['why'] = why
    summary = {
        'branches': BRANCHES, 'window': WINDOW, 'min_O': MIN_O, 'min_OE': MIN_OE, 'min_branches': MIN_BRANCHES,
        'null_threshold_log2': thr, 'null_threshold_OE': 2 ** thr,
        'null_qualifying_per_seed': per_seed,
        'null_score_quantiles': {str(p): float(np.percentile(pooled, p)) for p in (1, 5, 25, 50, 75, 90, 95, 99, 99.9)} if len(pooled) else {},
        'null_score_max': float(pooled.max()) if len(pooled) else None,
        'real_qualifying_after_exclusion': qual_real,
        'candidates': int(len(cand['pairs'])),
        'candidate_group_pairs': int(len(set(zip(*np.sort(np.stack([np.load(OUT / 'words.npz')['kgroup'][cand['pairs'] // PSHIFT],
                                                                      np.load(OUT / 'words.npz')['kgroup'][cand['pairs'] % PSHIFT]]), 0).tolist())))),
        'function_keys': int(func.sum()), 'top50_groups': topg,
        'positive_control': {'n': len(mb), 'recovered': len(rec), 'recall': recall,
                             'recovered_ids': rec, 'missed_ids': miss,
                             'by_subclass': {sc: [sum(1 for r in rec if r['subclass'] == sc), sum(1 for r in mb if r['subclass'] == sc)] for sc in ('lexical', 'partial-lexical')}},
        'control_seconds': round(time.time() - t0, 1),
    }
    json.dump(summary, open(OUT / 'summary.json', 'w'), ensure_ascii=False, indent=1)
    print(f"candidates={summary['candidates']} group_pairs={summary['candidate_group_pairs']} threshold_log2={thr:.3f}")
    print(f"recall={recall:.3f} ({len(rec)}/{len(mb)})  by_subclass={summary['positive_control']['by_subclass']}")
    print('recovered:', ' '.join(r['formula_id'] for r in rec))
    print('missed:', ' '.join(f"{r['formula_id']}[{r['why']}]" for r in miss))


# ---------------------------------------------------------------- packet
def known_group_pairs(kidx, lex, keys, kg):
    """Group pairs of every witness-scan spec (all rows) and of every Tier 2 line (any two token groups)."""
    known = set()
    def g(k):
        return key_group(k, lex)
    for r in map(json.loads, open(ROOT / 'data/research/formulas/witness-scan.jsonl')):
        for s in r.get('specs') or []:
            for a_ in s['A']:
                for b_ in s['B']:
                    known.add(frozenset((g(a_), g(b_))))
    for p in sorted((ROOT / 'corpus/tier2').glob('*.jsonl')):
        for line in p.read_text('utf-8').splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            gs = {g(t['lex_id']) for t in row.get('tokens', []) if t.get('lex_id') and not t['lex_id'].startswith('closed:')}
            gs |= {t['root_id'] for t in row.get('tokens', []) if t.get('root_id')}
            for a_ in gs:
                for b_ in gs:
                    if a_ != b_:
                        known.add(frozenset((a_, b_)))
    return known


def unit_loci(uids_pos_pairs):
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    return db


def find_loci(pair_keys, branches_wanted, W, kmat, cap=3, rng=None):
    """Real units where the two keys co-occur within the window, per branch: up to `cap` (random, seeded)."""
    x, y = pair_keys
    unit, pos = W['w_unit'], W['w_pos']
    hx = np.nonzero((kmat == x).any(1))[0]; hy = np.nonzero((kmat == y).any(1))[0]
    ux = collections.defaultdict(list)
    for i in hx: ux[unit[i]].append(pos[i])
    hits = collections.defaultdict(list)
    for j in hy:
        u = unit[j]
        if u in ux and any(abs(p - pos[j]) <= WINDOW and p != pos[j] for p in ux[u]):
            px = min(ux[u], key=lambda p: (abs(p - pos[j]) if p != pos[j] else 99))
            hits[W['u_br'][u]].append((int(u), int(px), int(pos[j])))
    out = {}
    for b in branches_wanted:
        h = sorted(set(hits.get(b, [])))
        # one hit per unit
        seen = {};
        for t in h: seen.setdefault(t[0], t)
        h = list(seen.values())
        if rng is not None and len(h) > cap:
            h = [h[i] for i in sorted(rng.choice(len(h), cap, replace=False))]
        out[b] = h[:cap]
    return out, {b: len({t[0] for t in v}) for b, v in hits.items()}


def cmd_packet(a):
    t0 = time.time()
    keys, groups = key_meta(); kidx = {k: i for i, k in enumerate(keys)}; lex = lexicon()
    W = load_words(); kg = W['kgroup']; kmat = W['w_keys']
    thr, pooled, per_seed, qual_real, cand, func, top, topg = threshold_and_candidates()
    known = known_group_pairs(kidx, lex, keys, kg)
    # collapse candidates to group pairs, best score per group pair
    best = {}
    for c, s, qm in zip(cand['pairs'], cand['score'], cand['qmask'].T):
        x, y = int(c // PSHIFT), int(c % PSHIFT)
        gp = frozenset((groups[kg[x]], groups[kg[y]]))
        if gp not in best or s > best[gp][0]:
            best[gp] = (float(s), x, y, [int(b) for b in np.nonzero(qm)[0]])
    new = [(gp, v) for gp, v in best.items() if gp not in known]
    new.sort(key=lambda t: (-t[1][0], sorted(t[0])))
    top40 = new[:40]
    # decoys: pooled null-qualifying pairs (after exclusions), not real candidates (group level), not known,
    # with real co-occurrence in >= 2 branches; seeded sample
    real_pairs = np.load(OUT / 'real-pairs.npz'); rp = dict(zip(real_pairs['pairs'].tolist(), real_pairs['O'].T))
    cand_groups = set(best)
    pool = {}
    for s in SEEDS:
        q = apply_exclusions(dict(np.load(OUT / f'run-null-{s:02d}.npz')), func, top)
        for c in q['pairs'].tolist():
            x, y = c // PSHIFT, c % PSHIFT
            gp = frozenset((groups[kg[x]], groups[kg[y]]))
            if gp in cand_groups or gp in known or c not in rp:
                continue
            pool.setdefault(gp, c)
    rng = np.random.default_rng(1001)
    pool_list = sorted(pool.items(), key=lambda t: sorted(t[0]))
    order = rng.permutation(len(pool_list))
    decoys = []
    used = set()
    for i in order:
        gp, c = pool_list[i]
        x, y = c // PSHIFT, c % PSHIFT
        O = rp[c]
        brs = [int(b) for b in np.argsort(-O, kind='stable') if O[b] > 0][:4]
        if len(brs) < 2 or gp in used:
            continue
        decoys.append((gp, x, y, brs)); used.add(gp)
        if len(decoys) == 10:
            break
    db = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    payload_cache = {}
    def unit_rec(u):
        if u not in payload_cache:
            p = db.execute('select payload from units where id=?', (int(W['u_uid'][u]),)).fetchone()[0]
            payload_cache[u] = json.loads(zlib.decompress(p))
        return payload_cache[u]
    def describe(k):
        e = lex.get(keys[k], {})
        return {'id': keys[k], 'pie': e.get('form'), 'meaning': e.get('meaning')}
    items = []
    lrng = np.random.default_rng(2002)
    for kind, gp, x, y, brs, score in ([('candidate', gp, v[1], v[2], v[3][:4], v[0]) for gp, v in top40] +
                                      [('decoy', gp, x, y, brs, None) for gp, x, y, brs in decoys]):
        loci, counts = find_loci((x, y), brs, W, kmat, cap=3, rng=lrng)
        L = []
        for b in brs:
            for u, px, py in loci.get(b, []):
                rec = unit_rec(u); ws = rec['words']
                L.append({'branch': BRANCHES[b], 'corpus': rec['corpus'], 'locus': rec['locus'],
                          'words': f"{ws[px]['form']} ~ {ws[py]['form']}", 'lemmas': f"{ws[px]['lemma']} ~ {ws[py]['lemma']}"})
        items.append({'kind': kind, 'pair': [describe(x), describe(y)], 'loci': L,
                      'branches_shown': [BRANCHES[b] for b in brs], 'score': score,
                      'group_pair': sorted(gp), 'real_units_by_branch': {BRANCHES[b]: n for b, n in counts.items()}})
    srng = np.random.default_rng(3003)
    perm = srng.permutation(len(items))
    ids = [f'D1-{i:03d}' for i in srng.choice(900, len(items), replace=False) + 100]
    packet, key = [], {}
    for pid, i in zip(ids, perm):
        it = items[i]
        packet.append({'id': pid, 'words': it['pair'], 'loci': it['loci']})
        key[pid] = {k: it[k] for k in ('kind', 'score', 'group_pair', 'branches_shown', 'real_units_by_branch')}
    packet.sort(key=lambda r: r['id'])
    KEYFILE.parent.mkdir(parents=True, exist_ok=True); PACKET.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'round': 'D1', 'threshold_log2': thr, 'items': key}, open(KEYFILE, 'w'), ensure_ascii=False, indent=1)
    with open(PACKET, 'w') as f:
        for r in packet:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    nloci = collections.Counter((items[i]['kind'], len(items[i]['loci'])) for i in range(len(items)))
    full = {k: sum(1 for it in items if it['kind'] == k and all(len([l for l in it['loci'] if l['branch'] == b]) == 3 for b in it['branches_shown'])) for k in ('candidate', 'decoy')}
    stats = {'new_group_pairs': len(new), 'candidate_group_pairs': len(best), 'known_group_pairs_among_candidates': len(best) - len(new),
             'review_candidates': len(top40), 'decoys': len(decoys), 'decoy_pool_group_pairs': len(pool),
             'items_with_full_3_loci_every_branch_shown': full,
             'loci_count_hist': {f'{k}:{n}': v for (k, n), v in sorted(nloci.items())},
             'packet_seconds': round(time.time() - t0, 1)}
    json.dump(stats, open(OUT / 'packet-stats.json', 'w'), indent=1)
    print(json.dumps(stats, indent=1))


# ---------------------------------------------------------------- diagnose (known formulas only; no candidates)
def cmd_diagnose(a):
    """Per positive-control formula: per-branch O, E, O/E of its best spec pair in the real index, and the
    step of the candidate rule that drops it. Reads known-formula pairs only."""
    keys, groups = key_meta(); kidx = {k: i for i, k in enumerate(keys)}; lex = lexicon()
    W = load_words(); pairs, O, n, N = count_run(W, W['w_keys'])
    func, top, _, _ = exclusion_sets()
    summ = json.load(open(OUT / 'summary.json')); thr = summ['null_threshold_log2']
    pidx = {int(c): i for i, c in enumerate(pairs)}
    rows = [json.loads(l) for l in open(ROOT / 'data/research/formulas/witness-scan.jsonl')]
    mb = [r for r in rows if r['class'] == 'multi-branch' and r['source'] in ('west', 'watkins')]
    out = []; stage = collections.Counter()
    for r in mb:
        best = None
        for s in r['specs']:
            for x in expand(s['A'], kidx, lex):
                for y in expand(s['B'], kidx, lex):
                    c = min(x, y) * PSHIFT + max(x, y)
                    if x == y or c not in pidx:
                        continue
                    i = pidx[c]; E = n[:, x] * n[:, y] / N
                    per = {BRANCHES[b]: [int(O[b, i]), round(float(E[b]), 2), round(float(O[b, i] / E[b]), 1) if E[b] else None]
                           for b in range(len(BRANCHES)) if O[b, i]}
                    o3 = sum(1 for v in per.values() if v[0] >= MIN_O)
                    q = [v for v in per.values() if v[0] >= MIN_O and v[2] and v[2] >= MIN_OE]
                    sc = math.log2(min(v[2] for v in q)) if len(q) >= 2 else None
                    rank = (len(q) >= 2 and sc > thr, len(q), o3, sc or 0)
                    if best is None or rank > best[0]:
                        best = (rank, s['spec'], keys[x], keys[y], per, sc, bool(func[x] or func[y] or (top[x] and top[y])))
        if best is None:
            st = 'pair never co-occurs in window'
            out.append({'formula_id': r['formula_id'], 'stage': st}); stage[st] += 1; continue
        (ok, nq, o3, _), spec, kx, ky, per, sc, excl = best
        st = ('candidate' if ok and not excl else 'excluded' if ok else 'O>=3 and O/E>=3 in >=2 branches, score <= null 99th pct' if nq >= 2
              else 'O>=3 in >=2 branches but O/E<3 in all but <=1' if o3 >= 2 else 'O>=3 in <=1 branch')
        stage[st] += 1
        out.append({'formula_id': r['formula_id'], 'subclass': r['subclass'], 'real_branches': r['real_branches'],
                    'spec': spec, 'pair': [kx, ky], 'per_branch_O_E_OE': per, 'score_log2': sc, 'stage': st})
    json.dump({'threshold_log2': thr, 'stages': dict(stage), 'formulas': out}, open(OUT / 'control-diagnostics.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(dict(stage), indent=1))


if __name__ == '__main__':
    os.chdir(ROOT)
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('extract')
    c = sp.add_parser('count'); c.add_argument('--jobs', type=int, default=7); c.add_argument('--only')
    f = sp.add_parser('freq'); f.add_argument('--top', type=int, default=120)
    sp.add_parser('control'); sp.add_parser('packet'); sp.add_parser('diagnose')
    a = ap.parse_args()
    {'extract': cmd_extract, 'count': cmd_count, 'freq': cmd_freq, 'control': cmd_control, 'packet': cmd_packet, 'diagnose': cmd_diagnose}[a.cmd](a)
