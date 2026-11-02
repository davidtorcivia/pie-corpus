"""Merge LoRA adapters of one base model exactly: the merged adapter's update is sum_i w_i * (A_i B_i).

    python -I training/rl/merge_adapters.py OUT_DIR ADAPTER:WEIGHT [ADAPTER:WEIGHT ...]

ADAPTER is an adapters.safetensors file (its adapter_config.json beside it) or a numbered checkpoint
(RUN/adapters/0000275_adapters.safetensors). The adapters are stacked along the rank axis (the one axis both factors
contract over: size `rank` in every tensor), with each B scaled by its weight, so the result is an exact weighted sum
of the deltas, at rank sum(rank_i); averaging the A and B matrices themselves would not be. Same base, same scale,
same keys required. Writes OUT_DIR/adapters.safetensors and adapter_config.json (rank updated).
"""
import json
import sys
from pathlib import Path

import numpy as np
from safetensors.numpy import load_file, save_file


def rank_axis(shape, r):
    ax = [i for i, x in enumerate(shape) if x == r]
    if len(ax) != 1:
        raise SystemExit(f"ambiguous rank axis in shape {shape}")
    return ax[0]


def merge(out, specs):
    cfgs, tensors, weights = [], [], []
    for spec in specs:
        path, w = spec.rsplit(":", 1)
        p = Path(path)
        cfgs.append(json.loads((p.parent / "adapter_config.json").read_text()))
        tensors.append(load_file(str(p)))
        weights.append(float(w))
    lp = [c["lora_parameters"] for c in cfgs]
    if len({(x["scale"], x.get("use_dora", False)) for x in lp}) != 1 or len({frozenset(t) for t in tensors}) != 1:
        raise SystemExit("adapters differ in scale, DoRA or keys")
    ranks = [x["rank"] for x in lp]
    merged = {}
    for k in tensors[0]:
        parts = []
        for t, r, w in zip(tensors, ranks, weights):
            x = t[k].astype(np.float32)
            ax = rank_axis(x.shape, r)
            parts.append((x * w if k.endswith("lora_b") else x, ax))
        axes = {ax for _, ax in parts}
        if len(axes) != 1:
            raise SystemExit(f"rank axis differs across adapters for {k}")
        merged[k] = np.concatenate([x for x, _ in parts], axis=axes.pop()).astype(tensors[0][k].dtype)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    save_file(merged, str(out / "adapters.safetensors"))
    cfg = dict(cfgs[0])
    cfg["lora_parameters"] = dict(lp[0], rank=sum(ranks))
    cfg["merged_from"] = [{"adapter": s.rsplit(":", 1)[0], "weight": float(s.rsplit(":", 1)[1])} for s in specs]
    (out / "adapter_config.json").write_text(json.dumps(cfg, indent=1))
    return tensors, weights, merged


def check(tensors, weights, merged, n=3):
    """The merged delta equals sum w_i A_i B_i on a few 2-D modules (A [in, r], B [r, out])."""
    keys = [k[:-len(".lora_a")] for k in merged if k.endswith("lora_a") and merged[k].ndim == 2][:n]
    for k in keys:
        want = sum(w * (t[k + ".lora_a"].astype(np.float64) @ t[k + ".lora_b"].astype(np.float64))
                   for t, w in zip(tensors, weights))
        got = merged[k + ".lora_a"].astype(np.float64) @ merged[k + ".lora_b"].astype(np.float64)
        err = np.abs(got - want).max() / (np.abs(want).max() + 1e-12)
        print(f"check {k}: relative max error {err:.2e}")
        assert err < 1e-2


if __name__ == "__main__":
    t, w, m = merge(sys.argv[1], sys.argv[2:])
    check(t, w, m)
    print("wrote", sys.argv[1])
