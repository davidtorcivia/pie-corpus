"""RL stage 6 prompts from text no fine-tune has seen (2026-11-03).

Stage 5 found that every translation and dialogue prompt of the earlier RL sets, train and validation, is verbatim in
the SFT export Nemotron e3 was trained on (5b754f0 added Tier 1), and e3 reproduces 82-89% of them exactly: they
teach and measure memory, not translation. The rl6-* Tier 3 batches were written for RL alone (Opus planners, the
engine's PIE; pie.export.RL_HELDOUT_PREFIX keeps them out of every training export). This builds, in the SFT
export's own prompt formats (pie.export_chat.task_chat, dialogue_chats):

- translate_en_pie / translate_pie_en: one sentence (3+ English words) or two consecutive sentences (up to 35 words)
  of a record, the engine's PIE and the plan's per-sentence English (align_english) as the references;
- dialogue: the first exchange of each dialogue conversation the chat export would build (its windows start at
  different turns), the reply being the reference;
- from stage 5: its kept prompts (drills, and translations and dialogue e3 missed at least once) and its held-out
  drill validation.

Whole records are split into train and valid (VALID_SHARE, by a hash of the id). Records listed in
data/rl6/flags-<batch>.jsonl (review verdict "wrong") are left out. Every prompt and reference is checked against the SFT
export's texts: a verbatim match is dropped from validation (unseen text only) but may train, since passrate.py
drops what e3 always gets right anyway.

    uv run python -I training/rl/make_rl6.py [--out /Users/david/AI/pie-runs/rl/data/rl6]
Then training/rl/passrate.py --mix rl6 on the candidates.
"""
import argparse
import collections
import json
import random
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pie import export_chat as ec  # noqa: E402
from pie.export import RL_HELDOUT_PREFIX, record_style  # noqa: E402
from make_rl_prompts import item  # noqa: E402

VALID_SHARE = 0.2
VALID_PER_KIND = {"translate_en_pie": 56, "translate_pie_en": 48, "dialogue": 40, "inflect": 24, "paradigm": 16,
                  "vocab_en_pie": 32, "vocab_pie_en": 16}   # 232
VOCAB = ("vocab_en_pie", "vocab_pie_en")
MAX_WORDS = 35
RL5 = Path("/Users/david/AI/pie-runs/rl/data/rl5")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def sft_texts() -> set[str]:
    """Every message text in the SFT export (chat train and the task file), normalized."""
    out = set()
    for p in (ROOT / "export/chat/train.jsonl", ROOT / "export/chat/train_mix.jsonl"):
        if p.exists():
            for line in p.read_text("utf-8").splitlines():
                for m in json.loads(line).get("messages", []):
                    if isinstance(m.get("content"), str):
                        out.add(norm(m["content"]))
                        out.update(norm(s) for s in ec.sentences(m["content"]) if len(s.split()) >= 3)
    for line in (ROOT / "export/train_tasks.jsonl").read_text("utf-8").splitlines():
        t = json.loads(line)
        for k in ("input", "output"):
            if isinstance(t.get(k), str):
                out.add(norm(re.sub(r"^\[style: [^\]]*\] ", "", t[k])))
    return out


def is_valid(rid: str) -> bool:
    return zlib.crc32(rid.encode()) % 1000 < VALID_SHARE * 1000


def translation_items(rec: dict) -> list[dict]:
    en, _ = ec.align_english(rec)
    pie = ec.sentences(rec["pie"])
    if en is None:
        return []
    style, out = record_style(rec), []
    units = [(i, i + 1) for i in range(len(pie)) if len(en[i].split()) >= 3] + \
            [(i, i + 2) for i in range(0, len(pie) - 1, 2)]
    for a, b in units:
        e, p = " ".join(en[a:b]), " ".join(pie[a:b])
        if len(e.split()) > MAX_WORDS:
            continue
        sid = f"{rec['id']}#{a}-{b}"
        t = {"task": "translate_en_pie", "input": f"[style: {style}] {e}", "output": p, "source_id": sid}
        out.append(item(ec.task_chat(t, None), "translate_en_pie", {"english": e, "refs": [p]}, sid, False))
        t = {"task": "translate_pie_en", "input": p, "output": e, "source_id": sid}
        out.append(item(ec.task_chat(t, None), "translate_pie_en", {"pie": p, "refs": [e]}, sid, False))
    return out


def dialogue_items(recs: list[dict]) -> list[dict]:
    out, seen = [], set()
    for r in ec.dialogue_chats(recs, collections.Counter()):
        m, msgs = r["meta"], r["messages"]
        i = next((j for j, x in enumerate(msgs) if x["role"] == "user"), None)
        if i is None or i + 1 >= len(msgs) or msgs[i + 1]["role"] != "assistant":
            continue
        key = (msgs[i]["content"], msgs[i + 1]["content"])
        if key in seen:
            continue
        seen.add(key)
        out.append(item({"messages": msgs[:i + 1]}, f"dialogue|{m['task']}|{m.get('mode', 'pie')}",
                        {"turn": msgs[i]["content"], "refs": [msgs[i + 1]["content"]]}, m["source_id"], False))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/Users/david/AI/pie-runs/rl/data/rl6")
    a = ap.parse_args()
    flags = set()
    for fp in sorted((ROOT / "data/rl6").glob("flags-*.jsonl")):
        flags |= {json.loads(x)["record"] for x in fp.read_text("utf-8").splitlines() if x.strip()}
    recs = []
    for f in sorted((ROOT / "corpus/tier3").glob(f"{RL_HELDOUT_PREFIX}*.jsonl")):
        if f.stem.endswith("-initial"):
            continue
        recs += [json.loads(x) for x in f.read_text("utf-8").splitlines() if x.strip()]
    kept = [r for r in recs if r["id"] not in flags]
    sft = sft_texts()
    stats = collections.Counter()
    cand, valid = [], []
    rows = [x for r in kept for x in translation_items(r)] + dialogue_items(kept)
    for x in rows:
        rec_id = x["source_id"].split("#")[0]
        ans = json.loads(x["answer"])
        texts = [x["prompt"], *ans.get("refs", [])]
        kind = x["type"].split("|")[0]
        seen = any(norm(t) in sft for t in texts)
        if seen and is_valid(rec_id):            # validation is unseen text only
            stats["dropped_valid_in_sft"] += 1
            continue
        if seen:                                 # training may keep it: passrate.py drops it if e3 always gets it right
            stats[f"cand_in_sft:{kind}"] += 1
        if is_valid(rec_id):
            x["type"] = "v." + x["type"]
            valid.append(x)
            stats[f"valid:{kind}"] += 1
        else:
            cand.append(x)
            stats[f"cand:{kind}"] += 1
    # drill anchors from stage 5: its kept inflection/paradigm prompts and its held-out drill validation
    # owner, 2026-11-03: "we can still keep anything the model gets wrong": stage 5's kept translation and dialogue
    # prompts are in the SFT data, but e3 missed each at least once in 4 samples, so they still teach
    for x in map(json.loads, (RL5 / "train.jsonl").read_text("utf-8").splitlines()):
        if x["type"].split("|")[0] in ("inflect", "paradigm", "translate_en_pie", "translate_pie_en", "dialogue", *VOCAB):
            cand.append(x)
            stats[f"cand:{x['type'].split('|')[0]}"] += 1
    for x in map(json.loads, (RL5 / "valid.jsonl").read_text("utf-8").splitlines()):
        if x["type"].split("|")[0] in ("v.inflect", "v.paradigm", *(f"v.{k}" for k in VOCAB)):
            valid.append(x)
            stats[f"valid:{x['type'].split('|')[0][2:]}"] += 1
    # vocabulary (2026-11-03): English->PIE word recall was stage 5's one moving skill (0.48 -> 0.61 at step 50, on
    # 9 held-out prompts), so stage 6 keeps drilling it. Stage 5's vocabulary candidates it never trained on split by
    # lemma: valid-hashed lemmas are held out (and never train), the rest are candidates beside stage 5's kept ones.
    trained = {x["source_id"] for x in map(json.loads, (RL5 / "train.jsonl").read_text("utf-8").splitlines())}
    have = {x["prompt"] for x in cand}
    for x in map(json.loads, (RL5 / "candidates.jsonl").read_text("utf-8").splitlines()):
        k = x["type"].split("|")[0]
        if k not in VOCAB or x["prompt"] in have:
            continue
        if is_valid(x["source_id"]) and x["source_id"] not in trained:
            x["type"] = "v." + x["type"]
            valid.append(x)
            stats[f"valid:{k}"] += 1
        elif not is_valid(x["source_id"]):
            cand.append(x)
            stats[f"cand:{k}"] += 1
    rng = random.Random(20261103)
    rng.shuffle(cand)
    rng.shuffle(valid)
    # the trainer scores every valid prompt at each check (8 per batch, ~1 min a batch on Nemotron), so valid.jsonl is a
    # fixed sample per kind; valid_full.jsonl keeps every held-out prompt for offline evaluation
    full, per, valid = valid, dict(VALID_PER_KIND), []
    for x in full:
        k = x["type"].removeprefix("v.").split("|")[0]
        if per.get(k, 0) > 0:
            per[k] -= 1
            valid.append(x)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "valid_full.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in full), "utf-8")
    for name, rs in (("candidates", cand), ("valid", valid), ("test", valid[:8])):
        (out / f"{name}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rs), "utf-8")
    man = {"source": "rl6 batches (held out of training)", "records": len(recs), "flagged": len(recs) - len(kept),
           "valid_share": VALID_SHARE, "valid": len(valid), "valid_full": len(full), "stats": dict(sorted(stats.items()))}
    (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main()
