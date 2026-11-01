"""Build benchmark v1 (benchmarks/README.md): items.jsonl as contestants see them, key.jsonl for scoring, and the
batches frontier contestants answer (20 items of one segment each).

    uv run python -I benchmarks/build.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "benchmarks"
SEGMENT = {"inflect": "inflection", "paradigm": "paradigm", "translate_en_pie": "en_pie",
           "translate_app/en_pie": "en_pie", "translate_pie_en": "pie_en", "translate_app/pie_en": "pie_en",
           "en_dialogue/en_pie": "dialogue", "en_dialogue/en_pie_gloss": "dialogue", "en_dialogue/mixed": "dialogue",
           "pie_dialogue/pie_pie": "dialogue", "continuation": "dialogue"}
WEIGHTS = {"inflection": 20, "paradigm": 15, "en_pie": 30, "pie_en": 20, "dialogue": 15}
BATCH = 20


def main():
    items, key = [], []
    for f in ("training/gen_prompts_v1.jsonl", "training/gen_prompts_drills_v2.jsonl"):
        for x in map(json.loads, (ROOT / f).read_text("utf-8").splitlines()):
            seg = SEGMENT.get(x["kind"])
            if not seg:
                continue
            sysm = next((m["content"] for m in x["prompt"] if m["role"] == "system"), "")
            user = next(m["content"] for m in reversed(x["prompt"]) if m["role"] == "user")
            iid = f"{'v1' if 'v1' in f else 'v2'}-{x['id']}"
            items.append({"id": iid, "segment": seg, "kind": x["kind"], "system": sysm, "instruction": user})
            key.append({"id": iid, "segment": seg, "kind": x["kind"], "reference": x["reference"],
                        "source_id": x.get("source_id")})
    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)), "duplicate ids"
    (HERE / "items.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items), "utf-8")
    (HERE / "key.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in key), "utf-8")
    batches = []
    for seg in WEIGHTS:
        xs = [x for x in items if x["segment"] == seg]
        for i in range(0, len(xs), BATCH):
            batches.append({"batch": f"{seg}-{i // BATCH:02d}", "items": [x["id"] for x in xs[i:i + BATCH]]})
    (HERE / "batches.json").write_text(json.dumps(batches, indent=0), "utf-8")
    from collections import Counter
    print(dict(Counter(x["segment"] for x in items)), len(items), "items,", len(batches), "batches")


if __name__ == "__main__":
    main()
