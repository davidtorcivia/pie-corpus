"""Text-only Nemotron 3.5 Super base from the VL checkpoint, for merging Tinker LoRAs and quantizing with omlx.

    uv run --with torch --with safetensors python -I training/tinker/build_text_base.py SRC_VL_DIR OUT_DIR

The VL checkpoint (NemotronH_Omni_Reasoning_V3) wraps a plain nemotron_h language model under `language_model.`
(backbone.*, lm_head, mtp.*) beside the vision tower (vision_model.*, vision_projector.*, mlp1.*). The cookbook's
Nemotron merge profile and mlx-lm's nemotron_h expect the plain names, so this writes the language model alone:
`language_model.` stripped, vision tensors dropped, config = the VL config's llm_config. The text path of the
model is unchanged (Tinker's LoRA is text-only). Shards are rewritten one at a time (low memory); the source is
only read.
"""
import json
import shutil
import sys
from pathlib import Path

from safetensors import safe_open
from safetensors.torch import save_file

PREFIX = "language_model."
COPY = ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja", "generation_config.json",
        "special_tokens_map.json")


def main(src, out):
    src, out = Path(src), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    vl = json.loads((src / "config.json").read_text())
    cfg = dict(vl["llm_config"])
    cfg["architectures"] = ["NemotronHForCausalLM"]
    cfg.pop("auto_map", None)
    cfg["torch_dtype"] = cfg.get("dtype", "bfloat16")
    (out / "config.json").write_text(json.dumps(cfg, indent=2))
    for f in COPY:
        if (src / f).exists():
            shutil.copy2(src / f, out / f)
    wmap = json.loads((src / "model.safetensors.index.json").read_text())["weight_map"]
    shards = sorted(set(wmap.values()))
    new_map, total, dropped = {}, 0, 0
    for i, sh in enumerate(shards, 1):
        target = out / sh
        keys = [k for k, v in wmap.items() if v == sh]
        keep = [k for k in keys if k.startswith(PREFIX)]
        dropped += len(keys) - len(keep)
        for k in keep:
            new_map[k[len(PREFIX):]] = sh
        if target.exists():                       # resumable: a finished shard is not rewritten
            print(f"[{i}/{len(shards)}] {sh}: exists", flush=True)
            continue
        if not keep:
            continue
        tensors = {}
        with safe_open(src / sh, framework="pt") as f:
            for k in keep:
                t = f.get_tensor(k)
                tensors[k[len(PREFIX):]] = t
                total += t.numel() * t.element_size()
        save_file(tensors, str(target) + ".part", metadata={"format": "pt"})
        Path(str(target) + ".part").rename(target)
        print(f"[{i}/{len(shards)}] {sh}: {len(keep)} tensors", flush=True)
    used = sorted(set(new_map.values()))
    (out / "model.safetensors.index.json").write_text(json.dumps(
        {"metadata": {"total_size": total}, "weight_map": dict(sorted(new_map.items()))}, indent=1))
    print(f"wrote {len(new_map)} tensors in {len(used)} shards to {out}; dropped {dropped} vision tensors")


if __name__ == "__main__":
    main(*sys.argv[1:3])
