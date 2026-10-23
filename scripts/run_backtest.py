#!/usr/bin/env python3
"""Phase 8b backtest: train a small cognate-set → pre-laryngeal PIE model and test it.

  uv run --group research python scripts/run_backtest.py tune      # dev grid, writes tune.json
  uv run --group research python scripts/run_backtest.py all       # everything else, writes results.json
  uv run --group research python scripts/run_backtest.py oof       # rerun only the out-of-fold stage
  uv run --group research python scripts/run_backtest.py all --data data/research/backtest/secondary.jsonl \\
      --out data/research/backtest/results_secondary.json             # secondary run, frozen config

The model is a small character-level transformer (encoder over the cognate set,
decoder over PIE units) trained only on data/research/backtest/primary.jsonl.
No LLM, no phonological prior: the model never sees laryngeal notation.

Stages (all with the hyperparameters chosen on dev in `tune`):
  main      3-seed ensemble on train, scored once on eval (teacher-forced per-slot
            error, entropy, surprisal; greedy decoding for accuracy)
  shuffled  same config, daughter forms shuffled across training sets
  oof       5-fold out-of-fold predictions over train+dev (by root family), for the
            better-powered analysis and to seed the free symbols, with shuffled-input
            and bigram baselines per fold
  freesym   k=4 free target symbols inserted where out-of-fold surprisal is high,
            assigned by clustering, refined by two hard-EM rounds; scored on eval
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie import backtest as bt  # noqa: E402

D = ROOT / "data/research/backtest"
SPECIAL = ["<pad>", "<s>", bt.EOS]
K_FREE = 4
FREE = [f"<X{i}>" for i in range(K_FREE)]


# ---------------------------------------------------------------- vocab / batching

class Vocab:
    def __init__(self, train_rows, order):
        cc = Counter(ch for r in train_rows for fs in r["inputs"].values() for f in fs
                     for ch in bt.unicodedata.normalize("NFD", f))
        self.chars = ["<pad>", "<unk>", "<lang>", "<sep>"] + sorted(c for c, n in cc.items() if n >= 2)
        lc = Counter(l for r in train_rows for l in r["inputs"])
        self.langs = ["<pad>", "<other>"] + sorted(l for l, n in lc.items() if n >= 3)
        units = sorted({u for r in train_rows for u in bt.segments(r["target"])})
        self.units = SPECIAL + units + ["<unk-unit>"] + FREE
        self.ci = {c: i for i, c in enumerate(self.chars)}
        self.li = {c: i for i, c in enumerate(self.langs)}
        self.ui = {c: i for i, c in enumerate(self.units)}
        self.order = order

    def enc_src(self, inputs, rng=None, max_forms=2):
        seq = bt.encode_inputs(inputs, self.order, max_forms=max_forms, rng=rng)
        c, l, p = [], [], []
        pos = 0
        for sym, lang in seq:
            pos = 0 if sym == "<lang>" else pos + 1
            c.append(self.ci.get(sym, 1))
            l.append(self.li.get(lang, 1))
            p.append(min(pos, 39))
        return c, l, p

    def enc_tgt(self, units):
        return [self.ui.get(u, self.ui["<unk-unit>"]) for u in units] + [self.ui[bt.EOS]]


def lang_dropout(inputs, rng, p=0.2):
    if len(inputs) <= 2:
        return inputs
    keep = {l: v for l, v in inputs.items() if rng.random() > p}
    if len(keep) < 2:
        ls = rng.sample(sorted(inputs), 2)
        keep = {l: inputs[l] for l in ls}
    return keep


def pad(seqs, v=0):
    n = max(len(s) for s in seqs)
    return torch.tensor([s + [v] * (n - len(s)) for s in seqs], dtype=torch.long)


def make_batch(vocab, items, rng=None, augment=False):
    """items: (inputs, target unit list incl. any free symbols)."""
    srcs, tgts = [], []
    for inputs, units in items:
        if augment:
            inputs = lang_dropout(inputs, rng)
        srcs.append(vocab.enc_src(inputs, rng=rng if augment else None))
        tgts.append(vocab.enc_tgt(units))
    c = pad([s[0] for s in srcs]); l = pad([s[1] for s in srcs]); p = pad([s[2] for s in srcs])
    y = pad(tgts)
    yin = torch.cat([torch.full((len(items), 1), 1, dtype=torch.long), y[:, :-1]], 1)   # <s> prefix
    yin = yin.masked_fill(yin == 0, 0)
    return c, l, p, yin, y


# ---------------------------------------------------------------- model

class Model(nn.Module):
    def __init__(self, vocab, d=128, layers=3, dec_layers=2, ff=256, drop=0.25, heads=4):
        super().__init__()
        self.ce = nn.Embedding(len(vocab.chars), d, padding_idx=0)
        self.le = nn.Embedding(len(vocab.langs), d, padding_idx=0)
        self.pe = nn.Embedding(40, d)
        self.ue = nn.Embedding(len(vocab.units), d, padding_idx=0)
        self.upe = nn.Embedding(40, d)
        self.tf = nn.Transformer(d, heads, layers, dec_layers, ff, drop, batch_first=True)
        self.out = nn.Linear(d, len(vocab.units))
        self.drop = nn.Dropout(drop)
        self.free_ids = [vocab.ui[f] for f in FREE]

    def forward(self, c, l, p, yin, allow_free=False):
        src = self.drop(self.ce(c) + self.le(l) + self.pe(p))
        pos = torch.arange(yin.size(1)).clamp(max=39)
        tgt = self.drop(self.ue(yin) + self.upe(pos)[None])
        mask = nn.Transformer.generate_square_subsequent_mask(yin.size(1))
        h = self.tf(src, tgt, tgt_mask=mask, src_key_padding_mask=(c == 0), tgt_key_padding_mask=(yin == 0) & (pos[None] > 0),
                    memory_key_padding_mask=(c == 0), tgt_is_causal=True)
        logits = self.out(h)
        logits[..., 0] = -1e9
        logits[..., 1] = -1e9
        if not allow_free:
            logits[..., self.free_ids] = -1e9
        return logits


# ---------------------------------------------------------------- train / predict

def train_model(cfg, train_items, dev_items, vocab, seed, allow_free=False, log=None):
    torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)
    torch.set_num_threads(cfg.get("threads", 3))
    rng = random.Random(seed)
    m = Model(vocab, d=cfg["d"], layers=cfg["layers"], dec_layers=cfg["dec_layers"], ff=cfg["d"] * 2, drop=cfg["drop"])
    opt = torch.optim.AdamW(m.parameters(), lr=cfg["lr"], weight_decay=0.01)
    steps_per = math.ceil(len(train_items) / cfg["bs"])
    total = steps_per * cfg["epochs"]
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 200) * max(0.05, 0.5 * (1 + math.cos(math.pi * s / total))))
    lossf = nn.CrossEntropyLoss(ignore_index=0)
    best, best_state, best_ep, hist = float("inf"), None, 0, []
    for ep in range(cfg["epochs"]):
        m.train()
        idx = list(range(len(train_items))); rng.shuffle(idx)
        for b in range(0, len(idx), cfg["bs"]):
            c, l, p, yin, y = make_batch(vocab, [train_items[i] for i in idx[b:b + cfg["bs"]]], rng, augment=True)
            loss = lossf(m(c, l, p, yin, allow_free).reshape(-1, len(vocab.units)), y.reshape(-1))
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step(); sched.step()
        if dev_items and ((ep + 1) % 5 == 0 or ep == cfg["epochs"] - 1):
            nll = dev_nll(m, vocab, dev_items, allow_free)
            hist.append((ep + 1, nll))
            if nll < best:
                best, best_ep = nll, ep + 1
                best_state = {k: v.clone() for k, v in m.state_dict().items()}
    if best_state is not None and cfg.get("early_stop", True):
        m.load_state_dict(best_state)
    return m, {"best_dev_nll": best, "best_epoch": best_ep, "history": hist}


@torch.no_grad()
def dev_nll(m, vocab, items, allow_free=False):
    m.eval()
    tot, n = 0.0, 0
    for b in range(0, len(items), 128):
        c, l, p, yin, y = make_batch(vocab, items[b:b + 128])
        lp = torch.log_softmax(m(c, l, p, yin, allow_free), -1)
        g = lp.gather(-1, y.unsqueeze(-1)).squeeze(-1)
        mask = y != 0
        tot += -(g * mask).sum().item(); n += mask.sum().item()
    m.train()
    return tot / n


@torch.no_grad()
def tf_probs(m, vocab, items, allow_free=False):
    """Teacher-forced distributions: one array [n_slots, V] per item."""
    m.eval()
    out = []
    for b in range(0, len(items), 128):
        chunk = items[b:b + 128]
        c, l, p, yin, y = make_batch(vocab, chunk)
        pr = torch.softmax(m(c, l, p, yin, allow_free), -1).numpy()
        for i, (_, units) in enumerate(chunk):
            out.append(pr[i, :len(units) + 1].copy())
    return out


@torch.no_grad()
def greedy(m, vocab, items, max_len=16):
    m.eval()
    res = []
    for b in range(0, len(items), 128):
        chunk = items[b:b + 128]
        c, l, p, _, _ = make_batch(vocab, chunk)
        yin = torch.full((len(chunk), 1), 1, dtype=torch.long)
        done = torch.zeros(len(chunk), dtype=torch.bool)
        for _ in range(max_len):
            nxt = m(c, l, p, yin)[:, -1].argmax(-1)
            nxt = nxt.masked_fill(done, 0)
            yin = torch.cat([yin, nxt[:, None]], 1)
            done |= nxt == vocab.ui[bt.EOS]
            if done.all():
                break
        for row in yin[:, 1:].tolist():
            us = []
            for t in row:
                if t in (0, vocab.ui[bt.EOS]):
                    break
                us.append(vocab.units[t])
            res.append(us)
    return res


def edit(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
    return d[-1]


# ---------------------------------------------------------------- jobs (run in worker processes)

def _job(args):
    kind, cfg, train_rows, dev_rows, pred_sets, seed, extra = args
    t0 = time.time()
    vocab = Vocab(train_rows, bt.language_order(train_rows))
    if extra.get("vocab_rows"):
        vocab = Vocab(extra["vocab_rows"], bt.language_order(train_rows))
    allow_free = extra.get("allow_free", False)
    tr = [(r["inputs"], r.get("units_aug") or bt.segments(r["target"])) for r in train_rows]
    dv = [(r["inputs"], bt.segments(r["target"])) for r in dev_rows] if dev_rows else []
    m, info = train_model(cfg, tr, dv, vocab, seed, allow_free=allow_free)
    out = {"info": info, "seed": seed, "secs": time.time() - t0, "units": vocab.units, "preds": {}}
    for name, rows in pred_sets.items():
        items = [(r["inputs"], bt.segments(r["target"])) for r in rows]
        out["preds"][name] = {"probs": tf_probs(m, vocab, items, allow_free)}
        if extra.get("greedy"):
            out["preds"][name]["greedy"] = greedy(m, vocab, items)
        if extra.get("score_aug") and name in extra["score_aug"]:
            out["preds"][name]["aug"] = score_alternatives(m, vocab, extra["score_aug"][name])
    return kind, out


@torch.no_grad()
def score_alternatives(m, vocab, cands):
    """cands: list of (inputs, unit list) → total log-likelihood of each sequence."""
    m.eval()
    out = []
    for b in range(0, len(cands), 256):
        chunk = cands[b:b + 256]
        c, l, p, yin, y = make_batch(vocab, chunk)
        lp = torch.log_softmax(m(c, l, p, yin, True), -1)
        g = lp.gather(-1, y.unsqueeze(-1)).squeeze(-1) * (y != 0)
        out += g.sum(-1).tolist()
    return out


def stack(probs):
    m = max(len(x) for x in probs)
    A = np.zeros((len(probs), m, probs[0].shape[1]), dtype=np.float32)
    for i, x in enumerate(probs):
        A[i, :len(x)] = x
    return A


def run_jobs(jobs, workers):
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_job, jobs))


# ---------------------------------------------------------------- analysis helpers

def ensemble(outs, name):
    arrs = [o["preds"][name]["probs"] for o in outs]
    return [np.mean([a[i] for a in arrs], 0) for i in range(len(arrs[0]))]


def words_from(rows, probs, units, free=False):
    ui = {u: i for i, u in enumerate(units)}
    free_ids = [ui[f] for f in FREE]
    words = []
    for r, pr in zip(rows, probs):
        us = bt.segments(r["target"])
        gold = [u if u in ui else "<unk-unit>" for u in us] + [bt.EOS]
        dists = []
        for s in range(len(gold)):
            row = pr[s].copy()
            row[free_ids] = 0.0
            row = row / row.sum()
            dists.append({units[i]: float(row[i]) for i in range(len(units)) if row[i] > 0})
        w = bt.Word(r["id"], bt.family(r), us, bt.effect_slots(r), bt.slot_metrics(dists, gold))
        w.dists = dists
        if free:
            ins = [float(pr[s][free_ids].sum()) for s in range(len(gold))]
            w.metrics["ins_before"] = ins
            w.metrics["ins_adjacent"] = [max(ins[s], ins[s + 1] if s + 1 < len(ins) else 0.0) for s in range(len(ins))]
        words.append(w)
    return words


def accuracy(rows, greedy_units):
    ex = sum(bt.segments(r["target"]) == g for r, g in zip(rows, greedy_units)) / len(rows)
    ue = sum(edit(bt.segments(r["target"]), g) for r, g in zip(rows, greedy_units)) / sum(len(bt.segments(r["target"])) for r in rows)
    return {"exact_match": ex, "unit_error_rate": ue}


def freq_words(rows, train_rows, order):
    fb = bt.FreqBaseline([r["target"] for r in train_rows], order=order)
    return [bt.Word(r["id"], bt.family(r), bt.segments(r["target"]), bt.effect_slots(r), fb.word_metrics(r["target"])) for r in rows]


def residual_words(words, fwords, metric="surprisal"):
    """Model metric minus the frequency-baseline metric, slot by slot (same rows, same order)."""
    out = []
    for w, f in zip(words, fwords):
        out.append(bt.Word(w.id, w.family, w.units, w.effects,
                           {metric: [a - b for a, b in zip(w.metrics[metric], f.metrics[metric])]}))
    return out


def hittite_check(rows, words, threshold_metric="entropy", q=0.75):
    """For sets with a Hittite reflex: does each ḫ sit on a slot flagged by the model?"""
    allv = sorted(v for w in words for v in w.metrics[threshold_metric])
    thr = allv[int(q * (len(allv) - 1))]
    hits = exp = n = gold_on = 0
    err_hits = err_exp = 0
    cases = []
    for r, w in zip(rows, words):
        hit = (r.get("hittite") or {}).get("Hittite")
        if not hit:
            continue
        flagged = {s for s, v in enumerate(w.metrics[threshold_metric]) if v >= thr}
        errs = {s for s, v in enumerate(w.metrics["error"]) if v > 0}
        for form in hit:
            h = bt.hittite_clean(form)
            if not h or "H" not in h:
                continue
            for slots in bt.hittite_slots(w.units, h):
                n += 1
                k = len(slots)
                spans = [set(range(i, i + k)) for i in range(len(w.units) + 2 - k)]
                is_hit = bool(slots & flagged)
                hits += is_hit
                exp += sum(bool(sp & flagged) for sp in spans) / len(spans)
                err_hits += bool(slots & errs)
                err_exp += sum(bool(sp & errs) for sp in spans) / len(spans)
                g = bool(slots & set(w.effects))
                gold_on += g
                cases.append({"id": r["id"], "target": r["target"], "hittite": form, "slots": sorted(slots),
                              "flagged_entropy": is_hit, "error": bool(slots & errs), "on_gold_effect": g,
                              "effects": {str(s): sorted(v) for s, v in w.effects.items()}})
        # one row may have several forms; each ḫ counted
    return {"n_h": n, "n_sets": len({c["id"] for c in cases}), "entropy_threshold_q": q,
            "hit_rate_entropy": hits / n if n else None, "expected_entropy": exp / n if n else None,
            "hit_rate_error": err_hits / n if n else None, "expected_error": err_exp / n if n else None,
            "on_gold_effect_rate": gold_on / n if n else None, "cases": cases}


def summarize(words):
    return {"contrasts": bt.all_contrasts(words), "descriptive": {m: bt.descriptive(words, m) for m in words[0].metrics},
            "strata_exact": bt.strata_table(words, "exact")[:40]}


# ---------------------------------------------------------------- stages

BASE = {"d": 128, "layers": 3, "dec_layers": 2, "drop": 0.3, "lr": 1e-3, "bs": 32, "epochs": 120, "threads": 3}


def stage_tune(rows, workers):
    tr = [r for r in rows if r["split"] == "train"]
    dv = [r for r in rows if r["split"] == "dev"]
    grid = []
    for d in (128, 192):
        for drop in (0.2, 0.35):
            for layers in (2, 3):
                grid.append({**BASE, "d": d, "drop": drop, "layers": layers})
    jobs = [("tune", g, tr, dv, {}, 0, {}) for g in grid]
    res = run_jobs(jobs, workers)
    table = [{"cfg": g, **o["info"], "secs": o["secs"]} for g, (_, o) in zip(grid, res)]
    table.sort(key=lambda x: x["best_dev_nll"])
    for t in table:
        print(json.dumps({k: t[k] for k in ("best_dev_nll", "best_epoch", "secs")}), t["cfg"])
    best = {**table[0]["cfg"], "epochs_fixed": table[0]["best_epoch"]}
    (D / "tune.json").write_text(json.dumps({"best": best, "table": table}, indent=1) + "\n")
    return best


def fold_of(fam, k=5):
    import hashlib
    return int(hashlib.sha256(("fold:" + fam).encode()).hexdigest()[:8], 16) % k


def stage_all(rows, cfg, workers, seeds=(0, 1, 2), npz=None):
    tr = [r for r in rows if r["split"] == "train"]
    dv = [r for r in rows if r["split"] == "dev"]
    ev = [r for r in rows if r["split"] == "eval"]
    results = {"config": cfg, "seeds": list(seeds)}
    fixed = {**cfg, "epochs": cfg["epochs_fixed"], "early_stop": False}

    # main + shuffled + oof, in one pool
    shuf = bt.shuffle_inputs(tr, seed=123)
    jobs = [("main", cfg, tr, dv, {"eval": ev, "dev": dv, "train": tr}, s, {"greedy": True}) for s in seeds]
    jobs += [("shuffled", cfg, shuf, dv, {"eval": ev}, s, {"greedy": True}) for s in seeds]
    t0 = time.time()
    res = run_jobs(jobs, workers)
    print(f"main/shuffled done in {time.time() - t0:.0f}s", flush=True)
    by = defaultdict(list)
    for kind, o in res:
        by[kind].append(o)
    units = by["main"][0]["units"]
    if npz:                         # eval probabilities, so the analysis can be redone without retraining
        arrays = {"units": np.array(units), "ids": np.array([r["id"] for r in ev])}
        for k in ("main", "shuffled"):
            for o in by[k]:
                arrays[f"{k}_seed{o['seed']}"] = stack(o["preds"]["eval"]["probs"])
        np.savez_compressed(Path(npz).with_name(Path(npz).name.replace("_oof", "_eval")), **arrays)

    # main
    probs = ensemble(by["main"], "eval")
    words = words_from(ev, probs, units)
    results["main"] = {"train_info": [o["info"] | {"secs": o["secs"]} for o in by["main"]], **summarize(words)}
    results["main"]["accuracy_eval"] = [accuracy(ev, o["preds"]["eval"]["greedy"]) for o in by["main"]]
    results["main"]["accuracy_train"] = [accuracy(tr, o["preds"]["train"]["greedy"]) for o in by["main"]]
    results["main"]["per_seed_eval"] = {}
    for o in by["main"]:
        ws = words_from(ev, o["preds"]["eval"]["probs"], units)
        results["main"]["per_seed_eval"][o["seed"]] = {
            lvl: {m: bt.matched_contrast(ws, m, lvl, n_boot=500)["diff"] for m in ("error", "entropy", "surprisal")}
            for lvl in ("exact", "class")}
    dvw = words_from(dv, ensemble(by["main"], "dev"), units)
    results["main"]["dev_contrasts"] = bt.all_contrasts(dvw, n_boot=500)
    results["main"]["examples_eval"] = [
        {"target": r["target"], "greedy": "".join(g), "effects": {str(s): sorted(k) for s, k in w.effects.items()},
         "entropy": [round(x, 3) for x in w.metrics["entropy"]], "error": w.metrics["error"]}
        for r, w, g in zip(ev, words, by["main"][0]["preds"]["eval"]["greedy"])]

    # shuffled baseline
    sw = words_from(ev, ensemble(by["shuffled"], "eval"), units)
    results["shuffled"] = {"train_info": [o["info"] for o in by["shuffled"]], **summarize(sw),
                           "accuracy_eval": [accuracy(ev, o["preds"]["eval"]["greedy"]) for o in by["shuffled"]]}

    # frequency baselines
    results["freq"] = {}
    for order in (1, 2):
        fw = freq_words(ev, tr, order)
        results["freq"][f"order{order}"] = {"contrasts": bt.all_contrasts(fw), "descriptive": {m: bt.descriptive(fw, m) for m in fw[0].metrics}}
    fw2 = freq_words(ev, tr, 2)
    results["main"]["residual_vs_bigram"] = bt.all_contrasts(residual_words(words, fw2), metrics=("surprisal",))
    results["main"]["minus_shuffled"] = bt.all_contrasts(residual_words(words, sw), metrics=("surprisal",))

    # Hittite on eval
    results["hittite_eval"] = hittite_check(ev, words)

    # out-of-fold over train+dev, with its own baselines
    results["oof"], oof_rows, oof_words = stage_oof(rows, fixed, workers, npz=npz)
    print("oof done", flush=True)

    # free symbols
    try:
        results["freesym"] = stage_freesym(tr, dv, ev, oof_rows, oof_words, fixed, cfg, workers, seeds)
    except Exception as e:  # report, never hide
        import traceback
        results["freesym"] = {"error": repr(e), "trace": traceback.format_exc()}
    return results


def stage_oof(rows, fixed, workers, npz=None):
    """5-fold out-of-fold predictions over train+dev (eval untouched), by root family, with
    the same fixed-epoch config: real inputs, shuffled inputs (within each fold's fit set)
    and a bigram baseline fit on each fold's fit set. Saves the probabilities to `npz`."""
    trdv = [r for r in rows if r["split"] in ("train", "dev")]
    folds = {f: ([r for r in trdv if fold_of(bt.family(r)) != f], [r for r in trdv if fold_of(bt.family(r)) == f])
             for f in range(5)}
    jobs = []
    for f, (fit, held) in folds.items():
        jobs.append(("real", fixed, fit, [], {"held": held}, 100 + f, {}))
        jobs.append(("shuf", fixed, bt.shuffle_inputs(fit, seed=f), [], {"held": held}, 200 + f, {}))
    out = run_jobs(jobs, workers)
    got = {(k, o["seed"] % 100): o for k, o in out}
    oof_rows, real, shuf, freq, argmax = [], [], [], [], []
    arrays = {}
    for f, (fit, held) in folds.items():
        oof_rows += held
        for k, acc in (("real", real), ("shuf", shuf)):
            o = got[(k, f)]
            ws = words_from(held, o["preds"]["held"]["probs"], o["units"])
            acc += ws
            if k == "real":
                argmax += [[max(d, key=d.get) for d in w.dists] for w in ws]
            arrays[f"{k}_fold{f}"] = stack(o["preds"]["held"]["probs"])
            arrays[f"{k}_fold{f}_units"] = np.array(o["units"])
        arrays[f"fold{f}_ids"] = np.array([r["id"] for r in held])
        freq += freq_words(held, fit, 2)
    if npz:
        np.savez_compressed(npz, **arrays)
    res = summarize(real)
    res["shuffled"] = {"contrasts": bt.all_contrasts(shuf), "descriptive": {m: bt.descriptive(shuf, m) for m in shuf[0].metrics}}
    res["bigram"] = {"contrasts": bt.all_contrasts(freq)}
    res["residual_vs_bigram"] = bt.all_contrasts(residual_words(real, freq), metrics=("surprisal",))
    res["minus_shuffled"] = bt.all_contrasts(residual_words(real, shuf), metrics=("surprisal",))
    res["breakdown_exact_surprisal"] = {k: bt.stratum_breakdown(real, "surprisal", "exact", k)[:12] for k in bt.KINDS}
    res["breakdown_exact_error"] = {k: bt.stratum_breakdown(real, "error", "exact", k)[:12] for k in bt.KINDS}
    res["confusions"] = {k: bt.confusions(real, argmax, k) for k in ("color", "length", "loss")}
    res["confusions_class"] = {k: bt.confusions(real, argmax, k, "class") for k in ("color", "length", "loss", "schwa")}
    res["hittite"] = hittite_check(oof_rows, real)
    return res, oof_rows, real


def kmeans(X, k, seed=0, iters=50):
    rng = np.random.default_rng(seed)
    C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        lab = ((X[:, None] - C[None]) ** 2).sum(-1).argmin(1)
        C = np.stack([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
    return lab


def stage_freesym(tr, dv, ev, oof_rows, oof_words, fixed, cfg, workers, seeds, q=0.90, rounds=2):
    """Seed: before each train unit whose out-of-fold surprisal is in the top 10% of train slots,
    insert a free symbol; which of the k symbols is chosen by k-means on the out-of-fold
    predictive distribution at that slot (no gold labels). Then hard-EM rounds: retrain on the
    augmented targets, and for each seeded slot keep the alternative (no symbol, or one of the
    k) with the highest sequence likelihood. Score on eval: probability mass the final model
    puts on free symbols at each gold slot (teacher forced), effect vs matched controls."""
    tr_ids = {r["id"] for r in tr}
    sur = {w.id: w for w in oof_words if w.id in tr_ids}
    allv = sorted(v for w in sur.values() for v in w.metrics["surprisal"][:-1])
    thr = allv[int(q * (len(allv) - 1))]
    # features: the out-of-fold predictive distribution at that slot (no gold labels)
    seeds_slots = []
    feats = []
    space = sorted({u for w in sur.values() for d in w.dists for u in d})
    for r in tr:
        w = sur.get(r["id"])
        if not w:
            continue
        for s, v in enumerate(w.metrics["surprisal"][:-1]):
            if v >= thr:
                seeds_slots.append((r["id"], s))
                feats.append([w.dists[s].get(u, 0.0) for u in space])
    X = np.sqrt(np.array(feats))
    lab = kmeans(X, K_FREE)
    assign = defaultdict(dict)                 # id -> slot -> free symbol index
    for (rid, s), j in zip(seeds_slots, lab):
        assign[rid][s] = int(j)

    def aug_units(r, a):
        us = bt.segments(r["target"])
        out = []
        for s, u in enumerate(us):
            if s in a:
                out.append(FREE[a[s]])
            out.append(u)
        return out

    info = {"threshold_surprisal": thr, "seeded_slots": len(seeds_slots), "rounds": []}
    full_vocab_rows = tr
    for rnd in range(rounds + 1):
        tr_aug = [{**r, "units_aug": aug_units(r, assign.get(r["id"], {}))} for r in tr]
        # cluster purity against gold, train side (diagnostic only)
        pur = defaultdict(Counter)
        for r in tr:
            eff = bt.effect_slots(r)
            for s, j in assign.get(r["id"], {}).items():
                pur[FREE[j]][",".join(sorted(eff.get(s, ["none"])))] += 1
        n_ins = sum(len(a) for a in assign.values())
        n_on = sum(1 for r in tr for s in assign.get(r["id"], {}) if s in bt.effect_slots(r))
        rinfo = {"round": rnd, "insertions": n_ins, "on_effect_slots": n_on,
                 "share_on_effect": n_on / n_ins if n_ins else None,
                 "train_effect_slot_share": sum(len(bt.effect_slots(r)) for r in tr) / sum(len(bt.segments(r["target"])) for r in tr),
                 "symbol_by_gold": {k: dict(v.most_common()) for k, v in pur.items()}}
        last = rnd == rounds
        cands = {}
        if not last:
            # alternatives for each seeded slot of each training row
            alt_index = []
            alt_items = []
            for r in tr:
                a = assign.get(r["id"], {})
                for s in list(a):
                    for choice in [None] + list(range(K_FREE)):
                        b = dict(a)
                        if choice is None:
                            b.pop(s)
                        else:
                            b[s] = choice
                        alt_index.append((r["id"], s, choice))
                        alt_items.append((r["inputs"], aug_units(r, b)))
            cands = {"train": alt_items}
        cfg_r = {**cfg, "threads": 3}
        jobs = [("free", cfg_r, tr_aug, dv, {"eval": ev, "train": tr[:1]}, s, {"allow_free": True, "score_aug": cands})
                for s in (seeds if last else seeds[:1])]
        res = [o for _, o in run_jobs(jobs, workers)]
        rinfo["train_info"] = [o["info"] for o in res]
        info["rounds"].append(rinfo)
        if not last:
            scores = res[0]["preds"]["train"]["aug"]
            best = {}
            for (rid, s, choice), sc in zip(alt_index, scores):
                if (rid, s) not in best or sc > best[(rid, s)][0]:
                    best[(rid, s)] = (sc, choice)
            # E-step over symbol identity: each seeded slot takes the free symbol that maximizes
            # the sequence likelihood. Slots are kept (a free symbol never raises the likelihood
            # of an otherwise identical sequence much, so "drop" would win by default); how often
            # "no symbol" would have won is recorded as a diagnostic.
            new = defaultdict(dict)
            best_sym, none_wins = {}, 0
            for (rid, s, choice), sc in zip(alt_index, scores):
                if choice is None:
                    continue
                if (rid, s) not in best_sym or sc > best_sym[(rid, s)][0]:
                    best_sym[(rid, s)] = (sc, choice)
            for (rid, s), (sc, choice) in best_sym.items():
                new[rid][s] = choice
                none_wins += best[(rid, s)][1] is None
            rinfo["none_would_win"] = none_wins
            assign = new
    units = res[0]["units"]
    probs = ensemble(res, "eval")
    words = words_from(ev, probs, units, free=True)
    info["eval"] = {"contrasts": bt.all_contrasts(words, metrics=("ins_before", "ins_adjacent")),
                    "descriptive": {m: bt.descriptive(words, m) for m in ("ins_before", "ins_adjacent")}}
    # hard decision: a slot is "marked" if free-symbol mass > 0.5
    marked = [(w, s) for w in words for s, v in enumerate(w.metrics["ins_before"]) if v > 0.5]
    info["eval"]["marked_slots"] = len(marked)
    info["eval"]["marked_on_effect"] = sum(1 for w, s in marked if s in w.effects)
    info["eval"]["eval_effect_slot_share"] = sum(len(w.effects) for w in words) / sum(len(w.units) + 1 for w in words)
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["tune", "all", "oof"])
    ap.add_argument("--data", default=str(D / "primary.jsonl"))
    ap.add_argument("--out", default=str(D / "results.json"))
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    rows = bt.load(a.data)
    if a.stage == "tune":
        stage_tune(rows, a.workers)
        return 0
    cfg = json.loads((D / "tune.json").read_text())["best"]
    out = Path(a.out)
    npz = out.with_name(out.stem + "_oof.npz")
    t0 = time.time()
    if a.stage == "oof":            # rerun only the out-of-fold analysis, merged into an existing file
        res = json.loads(out.read_text("utf-8"))
        fixed = {**cfg, "epochs": cfg["epochs_fixed"], "early_stop": False}
        res["oof"], _, _ = stage_oof(rows, fixed, a.workers, npz=npz)
        res["oof_wall_secs"] = time.time() - t0
    else:
        res = stage_all(rows, cfg, a.workers, npz=npz)
        res["wall_secs"] = time.time() - t0
    res["data"] = Path(a.data).name
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float) + "\n", "utf-8")
    print("wrote", out, time.time() - t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
