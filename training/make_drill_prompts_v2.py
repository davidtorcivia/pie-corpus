"""Freeze the v2 drill prompt set: every inflect and paradigm example of the eval export (export/chat/eval.jsonl),
in gen_eval.py's prompt format. v1 (gen_prompts_v1.jsonl) has 18 inflect and 13 paradigm prompts of ablauting
lexemes, too few to measure the ablaut gap; v2 takes all the drill-split lexemes' drills (about 290 inflect and 80
paradigm prompts, ablauting lexemes among them), scored by score_generations.py's per-class view.

    uv run python -I training/make_drill_prompts_v2.py [--eval export/chat/eval.jsonl] [--out training/gen_prompts_drills_v2.jsonl]

The drill-split lexemes are never drilled in training (pie.export.eval_drill); the set is frozen once written, so
later exports are compared on the same prompts (tests/test_export_chat.py checks it stays valid).
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", default=str(ROOT / "export/chat/eval.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "training/gen_prompts_drills_v2.jsonl"))
    a = ap.parse_args()
    out = []
    for line in Path(a.eval).read_text("utf-8").splitlines():
        e = json.loads(line)
        m = e["meta"]
        if m["task"] not in ("inflect", "paradigm"):
            continue
        out.append({"kind": m["task"], "id": m["id"], "source_id": m["source_id"],
                    "prompt": e["messages"][:-1], "reference": e["messages"][-1]["content"]})
    out.sort(key=lambda g: (g["kind"], g["source_id"], g["id"]))
    Path(a.out).write_text("".join(json.dumps(g, ensure_ascii=False) + "\n" for g in out), "utf-8")
    print(f"wrote {len(out)} prompts to {a.out}")


if __name__ == "__main__":
    main()
