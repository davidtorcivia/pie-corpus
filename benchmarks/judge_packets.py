"""Judge packets for the benchmark's judged segments (benchmarks/README.md): each packet holds a few items, each with
its prompt, its reference and every contestant's answer, anonymized and shuffled per item, so a judge grades all
answers to an item side by side and never sees who wrote them. The judges write verdict files; `file` maps them back
to each contestant (results/<contestant>/judge-<judge>.jsonl).

    python3 -I benchmarks/judge_packets.py build ROUND CONTESTANT...     # /Users/david/AI/pie-runs/bench/judge/ROUND
    python3 -I benchmarks/judge_packets.py file ROUND JUDGE              # verdicts-JUDGE-*.json -> results/

A round judges only the (item, contestant) pairs not yet judged by that judge, so a later contestant gets its own
round without re-judging the others.
"""
import hashlib
import os
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path("/Users/david/AI/pie-runs/bench/judge")
JUDGED = ("en_pie", "pie_en", "dialogue")
PER_PACKET = int(os.environ.get("BENCH_PER_PACKET", 3))    # items per packet; more when a round has few contestants


def part(kind: str, answer: str) -> str:
    """The part of an answer that is judged: the PIE line of a PIE-plus-gloss answer, the English line of an
    English-plus-gloss one, the reply before an English translation."""
    if kind == "translate_app/pie_en":
        m = re.search(r"English:\s*(.+)", answer)
        return (m[1] if m else re.split(r"\n?Gloss:", answer)[0]).strip()
    if kind in ("translate_app/en_pie", "en_dialogue/en_pie_gloss", "translate_en_pie"):
        t = answer.split("PIE:", 1)[-1]
        return re.split(r"\n?(English|Gloss|Notes):", t)[0].strip()
    return answer.strip()


def build(rnd: str, contestants: list[str]):
    items = {x["id"]: x for x in map(json.loads, (HERE / "items.jsonl").read_text("utf-8").splitlines())}
    key = {x["id"]: x for x in map(json.loads, (HERE / "key.jsonl").read_text("utf-8").splitlines())}
    answers = {}
    for c in contestants:
        for r in map(json.loads, (HERE / "results" / c / "answers.jsonl").read_text("utf-8").splitlines()):
            answers.setdefault(c, {}).setdefault(r["id"], r["answer"])
    d = OUT / rnd
    d.mkdir(parents=True, exist_ok=True)
    mapping, packets = {}, []
    only = os.environ.get("BENCH_ONLY")                # an id prefix: judge only those items (v2's "e2-")
    excluded = set(json.loads((HERE / "excluded.json").read_text("utf-8")))   # never scored (Amendment 1): not judged
    ids = [i for i, k in key.items() if k["segment"] in JUDGED and i not in excluded and (not only or i.startswith(only))]
    for i in ids:
        k, it = key[i], items[i]
        cands = [(c, part(k["kind"], answers[c][i])) for c in contestants if i in answers.get(c, {})]
        rng = random.Random(int(hashlib.sha256(f"{rnd}|{i}".encode()).hexdigest(), 16))
        rng.shuffle(cands)
        anon = []
        for n, (c, text) in enumerate(cands):
            aid = f"{i}#{n + 1}"
            mapping[aid] = c
            anon.append({"answer_id": aid, "answer": text})
        packets.append({"id": i, "segment": k["segment"], "kind": k["kind"], "setting": it["system"],
                        "prompt": it["instruction"], "reference": part(k["kind"], k["reference"]), "answers": anon})
    for n in range(0, len(packets), PER_PACKET):
        (d / f"packet-{n // PER_PACKET:03d}.json").write_text(json.dumps(packets[n:n + PER_PACKET], ensure_ascii=False, indent=1), "utf-8")
    (d / "mapping.json").write_text(json.dumps(mapping, indent=0), "utf-8")
    print(f"{rnd}: {len(packets)} items, {len(mapping)} answers, {(len(packets) + PER_PACKET - 1) // PER_PACKET} packets in {d}")


def file(rnd: str, judge: str):
    d = OUT / rnd
    mapping = json.loads((d / "mapping.json").read_text())
    rows, bad = {}, 0
    for f in sorted(d.glob(f"verdicts-{judge}-*.json")):
        try:
            vs = json.loads(f.read_text("utf-8"))
        except json.JSONDecodeError:
            bad += 1
            continue
        for v in vs:
            c = mapping.get(v.get("answer_id"))
            if c is None or v.get("score") not in (0, 0.5, 1, 0.0, 1.0):
                bad += 1
                continue
            rows.setdefault(c, []).append({"id": v["answer_id"].split("#")[0], "score": float(v["score"]),
                                           "reason": v.get("reason", ""), "round": rnd})
    for c, rs in rows.items():
        p = HERE / "results" / c / f"judge-{judge}.jsonl"
        have = {json.loads(x)["id"] for x in p.read_text("utf-8").splitlines()} if p.exists() else set()
        with open(p, "a", encoding="utf-8") as f:
            for r in rs:
                if r["id"] not in have:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{rnd} {judge}: filed {sum(map(len, rows.values()))} verdicts for {len(rows)} contestants, {bad} unusable,"
          f" of {len(mapping)} answers")


if __name__ == "__main__":
    {"build": lambda: build(sys.argv[2], sys.argv[3:]), "file": lambda: file(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
