"""items_v2.jsonl (or argv[1]; items_v3 after the 2026-11-01 indeclinables fix): items.jsonl with each word's engine analysis precomputed (lemma, gloss, every reading), so a
judge needs no tool calls for the common case (judge-test-2026-10-31.md, cost lever 1)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from pie.realize import Lexicon  # noqa: E402
from pie.translator.analyze import Analyzer  # noqa: E402

an = Analyzer.load()
lx = Lexicon.load()
SENSES = len(sys.argv) > 1          # v3 on: every sense of each lemma, not only the analyzer's one-word gloss
out = []
for line in (HERE / "items.jsonl").read_text("utf-8").splitlines():
    it = json.loads(line)
    rows, senses = [], {}
    for w in it["pie"].split():
        for p in w.strip(".,;:?!\"“”'()").split("-"):
            if not p:
                continue
            res, status = an.word(p)
            if SENSES:          # v3: readings grouped by lexeme, so a homograph (ḱóymos 'village' beside the
                groups = {}     # adjective's five gender readings) is never cut off
                for a in res:
                    groups.setdefault((a.lex_id, a.lemma, a.english), []).append(a.features)
                res = [next(a for a in res if a.lex_id == k[0]) for k in groups]
                text = " | ".join(f"{lem} '{en}' {'/'.join(f for f in fs if f)}".rstrip()
                                  for (_, lem, en), fs in groups.items())
            else:
                text = " | ".join(f"{a.lemma} '{a.english}' {a.features or ''}".rstrip() for a in res[:4])
            rows.append(f"{p}: " + (text if res else "UNKNOWN") + ("" if status == "exact" or not res else f" ({status})"))
            for a in res:
                m = lx.entries.get(a.lex_id, {}).get("meaning")
                if m and len(m) + sum(";" in x for x in m) > 1:
                    senses.setdefault(a.lemma, "; ".join(m))
    out.append({**it, "analysis": rows, **({"senses": senses} if SENSES else {})})
OUT = sys.argv[1] if len(sys.argv) > 1 else "items_v2.jsonl"
(HERE / OUT).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), "utf-8")
print(len(out), "items;", sum(len(x["analysis"]) for x in out), "analysed words")
