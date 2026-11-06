"""Blend two LoRA adapters of the same model exactly: the result adds a * ΔW_A + (1 - a) * ΔW_B to the base.

Averaging lora_a and lora_b separately is not a blend of the adapters (it adds cross terms a_A·b_B); stacking them
along the rank axis is. With a = [a_A | a_B] and b = [α b_A ; (1 - α) b_B], a·b = α a_A b_A + (1 - α) a_B b_B, at twice
the rank. Used to pull an RL checkpoint part of the way back toward an earlier one (rl6b) when a later stage cost a
segment (stage 8: EN dialogue).

    python -I training/rl/blend_adapters.py A.safetensors B.safetensors ALPHA OUT_DIR
"""
import json
import shutil
import sys
from pathlib import Path

import mlx.core as mx


def main(fa: str, fb: str, alpha: float, out: str) -> None:
    A, B = mx.load(fa), mx.load(fb)
    cfg = json.loads((Path(fa).parent / "adapter_config.json").read_text())
    r = cfg["lora_parameters"]["rank"]
    assert A.keys() == B.keys(), "the adapters cover different layers"
    o = {}
    for k in A:
        a, b = A[k], B[k]
        assert a.shape == b.shape and r in a.shape, (k, a.shape)
        ax = a.shape.index(r) if a.shape.count(r) == 1 else None
        assert ax is not None, f"{k}: rank axis ambiguous in {a.shape}"
        if k.endswith("lora_a"):
            o[k] = mx.concatenate([a, b], axis=ax)
        elif k.endswith("lora_b"):
            o[k] = mx.concatenate([a * alpha, b * (1 - alpha)], axis=ax)
        else:
            raise ValueError(f"unexpected tensor {k}")
    Path(out).mkdir(parents=True, exist_ok=True)
    mx.save_safetensors(str(Path(out) / "adapters.safetensors"), o)
    cfg["lora_parameters"]["rank"] = 2 * r
    cfg["blend"] = {"a": fa, "b": fb, "alpha": alpha}
    (Path(out) / "adapter_config.json").write_text(json.dumps(cfg, indent=4))
    print(f"blended {len(o)} tensors, alpha {alpha} on {Path(fa).parent.parent.name}, rank {2 * r} -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4])
