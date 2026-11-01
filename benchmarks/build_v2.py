"""Benchmark v2 (benchmarks/README.md, amendment 2): add the export's held-out Tier 2 translation pairs that are
neither published texts nor already in the benchmark (same direction and record), in the export's own prompt
format (pie.export_chat.task_chat). Appends to items.jsonl and key.jsonl and adds batches "<segment>-v2-NN".

    uv run python -I benchmarks/build_v2.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "benchmarks"
sys.path.insert(0, str(ROOT))
from pie import export_chat as ec  # noqa: E402

SEG = {"translate_en_pie": "en_pie", "translate_pie_en": "pie_en"}
PUBLISHED = ("t1-", "schleicher", "king", "formula")


def main():
    key = [json.loads(x) for x in (HERE / "key.jsonl").read_text("utf-8").splitlines()]
    if any(k["id"].startswith("e2-") for k in key):
        sys.exit("v2 items already added")
    have = {(k["segment"], k.get("source_id")) for k in key}
    items, keys = [], []
    for t in map(json.loads, (ROOT / "export/eval_tasks.jsonl").read_text("utf-8").splitlines()):
        seg = SEG.get(t["task"])
        if not seg or any(w in t["source_id"] for w in PUBLISHED) or (seg, t["source_id"]) in have:
            continue
        have.add((seg, t["source_id"]))
        chat = ec.task_chat(t, None)["messages"]
        iid = f"e2-{seg}-{t['source_id']}"
        items.append({"id": iid, "segment": seg, "kind": t["task"], "system": chat[0]["content"],
                      "instruction": chat[1]["content"]})
        keys.append({"id": iid, "segment": seg, "kind": t["task"], "reference": t["output"],
                     "acceptable": t.get("acceptable"), "source_id": t["source_id"]})
    with open(HERE / "items.jsonl", "a", encoding="utf-8") as f:
        f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in items)
    with open(HERE / "key.jsonl", "a", encoding="utf-8") as f:
        f.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in keys)
    batches = json.loads((HERE / "batches.json").read_text())
    for seg in ("en_pie", "pie_en"):
        xs = [x["id"] for x in items if x["segment"] == seg]
        for i in range(0, len(xs), 20):
            batches.append({"batch": f"{seg}-v2-{i // 20:02d}", "items": xs[i:i + 20]})
    (HERE / "batches.json").write_text(json.dumps(batches, indent=0), "utf-8")
    print(len(items), "items:", {s: sum(x["segment"] == s for x in items) for s in ("en_pie", "pie_en")},
          [b["batch"] for b in batches if "-v2-" in b["batch"]])


if __name__ == "__main__":
    main()
