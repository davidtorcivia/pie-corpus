"""Gap SFT, stage 1 (2026-11-04): a short supervised LoRA run on the Mac, from the latest RL adapter, on what the RL
filter found the model never or only sometimes gets right. RL sharpens what the model can already do; a word it never
produces has to be taught (stage 7's filter: 201 of 500 English->PIE vocabulary prompts never right in 4 samples).

From data/rl7 (passrate.jsonl: 4 samples per candidate scored with the training reward, judge included; mean <=
BAND_MAX is a miss):
- vocabulary, both ways: every missed or unsampled vocabulary candidate (train-split lemmas only: make_rl6.py holds
  the valid-hashed lemmas out), the answer being the corpus's most used lemma for the sense (EN->PIE) or the
  lexicon's first sense (PIE->EN);
- context: for each missed word, up to CONTEXT sentence pairs from the SFT export whose record uses the lexeme
  (corpus tokens' lex_id), so the word is also seen in use;
- dialogue, translation and inflection misses, with their reviewed references (rl6 train-split records);
- replay: as many random SFT-export examples again, so what the model knows is kept.
Validation (SFT loss only): the 232 held-out RL validation prompts with their references, never trained.

    uv run python -I training/rl/make_sft1.py [--out /Users/david/AI/pie-runs/rl/data/sft1]
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

BAND_MAX = 0.8          # passrate.py's: a mean reward above it over 4 samples is "always right" (passrate.py needs mlx)
D7 = Path("/Users/david/AI/pie-runs/rl/data/rl7")
CONTEXT = 2
SEED = 20261104


def kind(x):
    return x["type"].removeprefix("v.").split("|")[0]


def reference(x: dict, lemma_uses) -> str | None:
    """The answer to teach for an RL prompt, in the SFT export's formats."""
    k, a = kind(x), json.loads(x["answer"])
    if k in ("translate_en_pie", "translate_pie_en", "dialogue"):
        return a["refs"][0]
    if k == "vocab_en_pie":
        return max(a["lemmas"], key=lambda w: (lemma_uses.get(w, 0), -a["lemmas"].index(w)))
    if k == "vocab_pie_en":
        return a["senses"][0]
    if k == "inflect":
        return a[0]
    if k == "paradigm":
        return "\n".join(f"{c}: {f}" for c, f in a.items())
    return None


def chat(x: dict, answer: str, tag: str) -> dict:
    return {"messages": [{"role": "system", "content": x["system"]}, {"role": "user", "content": x["prompt"]},
                         {"role": "assistant", "content": answer}], "meta": {"gap": tag, "source_id": x["source_id"]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/Users/david/AI/pie-runs/rl/data/sft1")
    a = ap.parse_args()
    from pie.realize import Lexicon
    from pie.translator.lexmap import _corpus_counts
    lx = Lexicon.load()
    uses = _corpus_counts()
    form_lid = {}
    for lid, e in lx.entries.items():
        form_lid.setdefault(e.get("form", "").strip("*"), lid)
    lemma_uses = {f: uses.get(lid, 0) for f, lid in form_lid.items()}

    cands = [json.loads(x) for x in (D7 / "candidates.jsonl").read_text("utf-8").splitlines()]
    rates = {r["i"]: r["scores"] for r in map(json.loads, (D7 / "passrate.jsonl").read_text("utf-8").splitlines())}
    stats = collections.Counter()
    train, missed_lids = [], set()
    for i, x in enumerate(cands):
        k = kind(x)
        s = rates.get(i)
        miss = s is None or sum(s) / len(s) <= BAND_MAX
        if k in ("vocab_en_pie", "vocab_pie_en"):
            if not miss:
                continue
            tag = f"vocab:{'unsampled' if s is None else 'miss'}"
        elif s is not None and miss and k in ("dialogue", "translate_en_pie", "translate_pie_en", "inflect", "paradigm"):
            tag = "miss"
        else:
            continue
        ref = reference(x, lemma_uses)
        if not ref:
            continue
        train.append(chat(x, ref, f"{k}:{tag}"))
        stats[f"{k}:{tag}"] += 1
        if k == "vocab_en_pie" and s is not None:
            lid = form_lid.get(ref)
            if lid:
                missed_lids.add(lid)
        elif k == "vocab_pie_en" and s is not None:
            lid = form_lid.get(json.loads(x["answer"])["word"].strip("*"))
            if lid:
                missed_lids.add(lid)

    # context: corpus records that use a missed lexeme, as the export's own short translation pairs
    recs_by_lid = collections.defaultdict(set)
    for f in sorted((ROOT / "corpus").glob("tier*/*.jsonl")):
        for line in f.read_text("utf-8").splitlines():
            r = json.loads(line)
            for t in r.get("tokens") or []:
                if t.get("lex_id") in missed_lids:
                    recs_by_lid[t["lex_id"]].add(r["id"])
    export = [json.loads(x) for x in (ROOT / "export/chat/train.jsonl").read_text("utf-8").splitlines()]
    by_src = collections.defaultdict(list)
    for j, e in enumerate(export):
        if e["meta"].get("task") in ("translate_en_pie", "translate_pie_en"):
            by_src[e["meta"]["source_id"].split("#")[0]].append(j)
    rng = random.Random(SEED)
    used = set()
    for lid in sorted(missed_lids):
        pool = [j for rid in sorted(recs_by_lid.get(lid, ())) for j in by_src.get(rid, ()) if j not in used]
        for j in rng.sample(pool, min(CONTEXT, len(pool))):
            used.add(j)
            train.append({"messages": export[j]["messages"], "meta": {"gap": "context", "lex_id": lid}})
            stats["context"] += 1
    stats["missed_lexemes"] = len(missed_lids)
    stats["missed_lexemes_with_context"] = sum(1 for lid in missed_lids if recs_by_lid.get(lid))

    # replay: as many random export examples (not already used as context)
    rest = [j for j in range(len(export)) if j not in used]
    for j in rng.sample(rest, min(len(train), len(rest))):
        train.append({"messages": export[j]["messages"], "meta": {"gap": "replay", "task": export[j]["meta"].get("task")}})
        stats["replay"] += 1
    rng.shuffle(train)

    valid = []
    for x in map(json.loads, (D7 / "valid.jsonl").read_text("utf-8").splitlines()):
        ref = reference(x, lemma_uses)
        if ref:
            valid.append(chat(x, ref, f"valid:{kind(x)}"))
    # a drill prompt can recur with the same text in another split (an inflection asked of two lemmas' homographs):
    # nothing whose prompt is a validation prompt trains
    vprompts = {r["messages"][1]["content"] for r in valid}
    keep = [r for r in train if next(m["content"] for m in r["messages"] if m["role"] == "user") not in vprompts]
    stats["dropped_valid_prompt"] = len(train) - len(keep)
    train = keep
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, rows in (("train", train), ("valid", valid)):
        (out / f"{name}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    man = {"source": str(D7), "band_max": BAND_MAX, "train": len(train), "valid": len(valid), "stats": dict(sorted(stats.items()))}
    (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
    print(json.dumps(man, indent=1))


if __name__ == "__main__":
    main()
