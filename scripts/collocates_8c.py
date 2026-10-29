#!/usr/bin/env python3
"""Cross-branch collocates of a target (one or more ids, lexeme or root).
Keys collocates by both lexeme ids and root groups. Per branch: O = target units with
the collocate within +-W content words; E = target units * base unit rate of the
collocate in that branch. Lists collocates with O>=2 and O/E>=2 in >=2 branches.
--pair IDS: instead print per-branch pair hits (all) with text."""
import sqlite3, zlib, json, sys, collections, math, argparse
ap = argparse.ArgumentParser()
ap.add_argument('--db', default='data/research/8c/search-index/corpora.sqlite')
ap.add_argument('--target', required=True); ap.add_argument('--pair')
ap.add_argument('--window', type=int, default=4); ap.add_argument('--out')
ap.add_argument('--top', type=int, default=40); ap.add_argument('--show', type=int, default=4)
a = ap.parse_args()
T = set(a.target.split(',')); P = set(a.pair.split(',')) if a.pair else None
db = sqlite3.connect(f'file:{a.db}?mode=ro', uri=True)
# compound members (pie/compound_members.py, index field member_ids / member_groups) count as keys
def keys(w): return set(w['root_ids']) | set(w['root_groups']) | set(w.get('member_ids', ())) | set(w.get('member_groups', ()))
tids = [r[0] for r in db.execute(f"select id from terms where kind='root' and value in ({','.join('?'*len(T))})", tuple(T))]
units = db.execute(f"select distinct u.corpus,u.branch,u.payload from units u join postings p on p.unit=u.id where p.term in ({','.join('?'*len(tids))})", tids)
H = collections.Counter(); O = collections.defaultdict(collections.Counter)
ex = collections.defaultdict(lambda: collections.defaultdict(list)); pairs = collections.defaultdict(list)
for corpus, branch, payload in units:
    rec = json.loads(zlib.decompress(payload)); ws = rec['words']
    hp = [i for i, w in enumerate(ws) if keys(w) & T]
    if not hp: continue
    H[branch] += 1; seen = {}
    for i in hp:
        for j in range(max(0, i - a.window), min(len(ws), i + a.window + 1)):
            if j in hp: continue
            for r in keys(ws[j]) - T: seen.setdefault(r, (ws[i]['form'], ws[j]['form']))
    if P is not None:
        if set(seen) & P: pairs[branch].append(f"{corpus} | {rec['locus']} | {rec['text'][:220]}")
        continue
    for r, pr in seen.items():
        O[branch][r] += 1
        if len(ex[r][branch]) < 3: ex[r][branch].append(f"{corpus} {rec['locus']}: {pr[0]} ~ {pr[1]}")
print("target units by branch:", dict(H))
if P is not None:
    for b, v in sorted(pairs.items(), key=lambda x: -len(x[1])):
        print(f"== {b}: {len(v)} of {H[b]}")
        for s in v[:a.show]: print("   ", s)
    sys.exit()
N = dict(db.execute("select branch,count(*) from units group by branch"))
cands = {r for b in O for r, c in O[b].items() if c >= 2}
base = collections.defaultdict(dict)
for r in cands:
    t = db.execute("select id from terms where kind='root' and value=?", (r,)).fetchone()
    if t:
        for b, c in db.execute("select u.branch,count(*) from postings p join units u on u.id=p.unit where p.term=? group by u.branch", (t[0],)):
            base[r][b] = c
rows = []
for r in cands:
    per = {}
    for b in O:
        o = O[b].get(r, 0); e = H[b] * base[r].get(b, 0) / N[b]
        if o >= 2 and e and o / e >= 2: per[b] = (o, round(e, 1), round(o / e, 1))
    if len(per) >= 2: rows.append((len(per), sum(math.log2(v[2]) for v in per.values()), r, per))
rows.sort(key=lambda x: (-x[0], -x[1]))
if a.out:
    json.dump({"target": sorted(T), "window": a.window, "units": H, "rows": [{"root": r, "branches": per, "examples": {b: ex[r][b] for b in per}} for _, _, r, per in rows]}, open(a.out, 'w'), ensure_ascii=False, indent=1)
for n, s, r, per in rows[:a.top]:
    print(f"{n} {s:5.1f} {r:34s} " + "; ".join(f"{b[:5]}:{o}/{e}x{q}" for b, (o, e, q) in sorted(per.items(), key=lambda x: -x[1][2])))
    print("        " + " || ".join(ex[r][b][0] for b in per)[:330])
