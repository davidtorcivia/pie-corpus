"""Phase 8b replication, EXPLORATORY sensitivity bound (not part of the pre-registered build):
slot counts under the loosest reasonable rules. Prints counts only, writes nothing.

  uv run --group research python -I scripts/replication_sensitivity.py <sa dump> <grc dump> <la dump>
"""
import sys, collections
from pathlib import Path
_R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_R)); sys.path.insert(0, str(_R / "scripts"))
import build_replication as B
from pie import backtest as bt
B.AFFIX = ()            # keep affix/compound entries
B.SKIP_POS = set()
orig = B.entry_links
def loose(d, lang):
    r = orig(d, lang)
    return r
paths = sys.argv[1:]
st = collections.Counter(); ents = []
for p in paths:
    lang = next(c for c, n in (("sa", "Sanskrit"), ("grc", "AncientGreek"), ("la", "Latin")) if n in p)
    ents += B.read_dump(p, lang, st)
lex = bt.load(B.ROOT / "data/lexicon/lexicon.jsonl"); byid = {e["id"]: e for e in lex}; idx = B.PieIndex(lex)
D = B.ROOT / "data/research/backtest"
first = bt.load(D / "primary.jsonl") + bt.load(D / "secondary.jsonl")
ff = {bt.family(r) for r in first}; fi = {r["id"] for r in first}
groups = collections.defaultdict(lambda: {"langs": set(), "terms": set(), "roots": set(), "lemma": None})
for e in ents:
    for w in e["words"]:                      # every word-level link counts, not just one per entry
        p = B.parse_form(w if w.startswith("*") else "*" + w)
        if not p.lemma: continue
        g = groups[B.pie_key(p.lemma)]; g["lemma"] = g["lemma"] or p.lemma
        g["langs"].add(e["lang"]); g["terms"].add(w); g["roots"].update(e["roots"])
rows = []
for k, g in groups.items():
    if len(g["langs"]) < 2: continue
    hits = set().union(*[idx.pie(t) for t in g["terms"]]) | set().union(*[idx.pie(t, roots_only=True) for t in g["roots"]] or [set()])
    fams = {(byid.get(x) or {}).get("root_id") or x for x in hits}
    if hits & fi or fams & ff: continue
    try: t, eff = B.convert(g["lemma"])
    except ValueError: continue
    rows.append({"id": k, "root_id": sorted(fams)[0] if fams else k, "target": t,
                 "effects": [{"kind": x.kind, "offset": x.offset} for x in eff]})
words = [bt.Word(r["id"], bt.family(r), bt.segments(r["target"]), bt.effect_slots(r)) for r in rows]
m = bt.match(words, "exact")
print("loose sets", len(rows), "effect slots", len(m), "exact-matched", sum(bool(x["controls"]) for x in m))
m1 = bt.match(words, "exact", min_families=1)
print("even with 1-family rule:", sum(bool(x["controls"]) for x in m1))
