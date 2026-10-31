"""items_v2.jsonl: items.jsonl with each word's engine analysis precomputed (lemma, gloss, every reading), so a
judge needs no tool calls for the common case (judge-test-2026-10-31.md, cost lever 1)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from pie.translator.analyze import Analyzer  # noqa: E402

an = Analyzer.load()
out = []
for line in (HERE / "items.jsonl").read_text("utf-8").splitlines():
    it = json.loads(line)
    rows = []
    for w in it["pie"].split():
        for p in w.strip(".,;:?!\"“”'()").split("-"):
            if not p:
                continue
            res, status = an.word(p)
            rows.append(f"{p}: " + (" | ".join(f"{a.lemma} '{a.english}' {a.features or ''}".rstrip() for a in res[:4])
                                    if res else "UNKNOWN") + ("" if status == "exact" or not res else f" ({status})"))
    out.append({**it, "analysis": rows})
(HERE / "items_v2.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), "utf-8")
print(len(out), "items;", sum(len(x["analysis"]) for x in out), "analysed words")
