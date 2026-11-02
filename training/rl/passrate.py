"""Filter RL candidates by the SFT model's own pass rate, so training spends its steps where rollouts disagree
(stage 1: most groups scored 8/8, group σ fell to 0.03, and those prompts taught nothing).

    python -I training/rl/passrate.py --model DIR --data DIR [--k 4] [--n 4000]

Samples the model k times per candidate (DIR/candidates.jsonl, from make_rl_prompts.py --mix v2) at temperature
1.0, thinking off, the RL cap, and scores each locally, with no judge: drills by the engine reward, translations by
reward_rl.local (exact reference = 1, hard fail = 0, else undecided). Keeps:
- drills not always right (a mean reward below 1; at most a quarter of them never right, which can still teach
  when 8 rollouts find one);
- translations the model does not reproduce exactly every time (memorized ones teach nothing).
Writes DIR/passrate.jsonl (resumable: done candidates are skipped) and DIR/train.jsonl: up to n prompts, 40%
inflection, 20% paradigm, 40% translation, shuffled.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))
import reward_engine  # noqa: E402
import reward_rl  # noqa: E402

SHARE = {"inflect": 0.15, "paradigm": 0.1, "translate_en_pie": 0.25, "translate_pie_en": 0.15,
         "vocab_en_pie": 0.075, "vocab_pie_en": 0.075, "dialogue": 0.2}   # with vocabulary, PIE→EN and dialogue (owner, 2026-11-01)
SHARES = {"rl3": SHARE,
          # stage 4 (2026-11-02): what slipped in stage 3 up (EN→PIE, the benchmark's heaviest segment; inflection;
          # paradigms), dialogue and PIE→EN kept as anchors, the mostly zero-variance vocabulary drills down
          "rl4": {"inflect": 0.22, "paradigm": 0.13, "translate_en_pie": 0.30, "translate_pie_en": 0.12,
                  "vocab_en_pie": 0.04, "vocab_pie_en": 0.04, "dialogue": 0.15}}
SEED = 20261101


def kind(x: dict) -> str:
    return x["type"].split("|")[0]


def score(x: dict, completion: str, an) -> float | None:
    k, a = kind(x), json.loads(x["answer"]) if kind(x) not in ("inflect", "paradigm") else None
    if k == "translate_en_pie":
        return reward_rl.local(completion, a, an)[0]
    if k == "translate_pie_en":
        return reward_rl.local_pie_en(completion, a)
    if k == "vocab_pie_en":
        return reward_rl.local_vocab_pie_en(completion, a)
    if k == "vocab_en_pie":
        return reward_rl.vocab_en_pie(completion, a)
    if k == "dialogue":
        return reward_rl.local_dialogue(completion, a, an)
    return reward_engine.score(completion, x["answer"], kind(x))


def sample(model_dir: str, cands: list[dict], k: int, out: Path, batch: int, an, adapter: str | None = None):
    from mlx_lm import batch_generate, load
    from mlx_lm.sample_utils import make_sampler
    done = {json.loads(x)["i"] for x in out.read_text("utf-8").splitlines()} if out.exists() else set()
    todo = [(i, x) for i, x in enumerate(cands) if i not in done]
    print(f"{len(done)} done, {len(todo)} to sample", flush=True)
    if not todo:
        return
    model, tok = load(model_dir, adapter_path=adapter)   # the policy RL starts from (stage 4: base + merged adapter)
    sampler = make_sampler(temp=1.0)
    t0, f = time.time(), out.open("a", encoding="utf-8")
    per = max(1, batch // k)
    for j in range(0, len(todo), per):
        chunk = todo[j:j + per]
        prompts = [tok.apply_chat_template([{"role": "system", "content": x["system"]}, {"role": "user", "content": x["prompt"]}],
                                           add_generation_prompt=True, tokenize=True, enable_thinking=False)
                   for _, x in chunk for _ in range(k)]
        texts = batch_generate(model, tok, prompts, max_tokens=384, sampler=sampler,
                               completion_batch_size=len(prompts), prefill_batch_size=len(prompts)).texts
        for n, (i, x) in enumerate(chunk):
            outs = texts[n * k:(n + 1) * k]
            f.write(json.dumps({"i": i, "type": x["type"], "scores": [score(x, o, an) for o in outs],
                                "outputs": outs}, ensure_ascii=False) + "\n")
        f.flush()
        d = j + len(chunk)
        print(f"{d}/{len(todo)} candidates, {time.time() - t0:.0f} s, "
              f"eta {(time.time() - t0) / d * (len(todo) - d) / 60:.0f} min", flush=True)


def select(cands: list[dict], rates: dict[int, list], n: int, share: dict | None = None) -> tuple[list[dict], dict]:
    share = share or SHARE
    keep = {k: [] for k in share}
    never = {k: [] for k in share}
    stats = {}
    for i, x in enumerate(cands):
        s = rates.get(i)
        if s is None:
            continue
        k = kind(x)
        st = stats.setdefault(k, {"sampled": 0, "always": 0, "never": 0, "kept": 0})
        st["sampled"] += 1
        if k in ("translate_en_pie", "translate_pie_en", "vocab_pie_en", "dialogue"):     # judged kinds: drop what is always exact
            exact = sum(v == 1.0 for v in s)
            if exact == len(s):
                st["always"] += 1
                continue
            keep[k].append(x)
        else:
            m = sum(s) / len(s)
            if m >= 1.0:
                st["always"] += 1
            elif m == 0.0:
                st["never"] += 1
                never[k].append(x)
            else:
                keep[k].append(x)
    rng = random.Random(SEED)
    train = []
    for k, sh in share.items():
        want = int(n * sh)
        pool = keep[k] + rng.sample(never[k], min(len(never[k]), len(keep[k]) // 3))
        rng.shuffle(pool)
        train += pool[:want]
        stats[k]["kept"] = min(len(pool), want)
    rng.shuffle(train)
    return train, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--batch", type=int, default=256, help="rollouts decoded together")
    ap.add_argument("--adapter", help="LoRA adapter dir on top of --model (the policy RL starts from)")
    ap.add_argument("--mix", default="rl3", choices=sorted(SHARES), help="kind shares of train.jsonl")
    a = ap.parse_args()
    d = Path(a.data)
    cands = [json.loads(x) for x in (d / "candidates.jsonl").read_text("utf-8").splitlines() if x.strip()]
    from pie.translator.analyze import Analyzer
    an = Analyzer.load()
    sample(a.model, cands, a.k, d / "passrate.jsonl", a.batch, an, a.adapter)
    rates = {r["i"]: r["scores"] for r in map(json.loads, (d / "passrate.jsonl").read_text("utf-8").splitlines())}
    train, stats = select(cands, rates, a.n, SHARES[a.mix])
    (d / "train.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in train), "utf-8")
    man = json.loads((d / "manifest.json").read_text())
    man["passrate"] = {"k": a.k, "model": a.model, "adapter": a.adapter, "mix": a.mix, "by_kind": stats, "train": len(train)}
    (d / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False), "utf-8")
    print(json.dumps(man["passrate"]))


if __name__ == "__main__":
    main()
