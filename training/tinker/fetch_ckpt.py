"""Download a Tinker checkpoint of a PIE run to tr-desktop (Q:\\AI\\PIE\\tinker\\ckpt\\<run>\\<name>), for the Mac to
merge and quantize (training/tinker/deploy_qwen36.sh). No sampling on Tinker (owner, 2026-10-31).

    Q:\\AI\\PIE\\tinker\\.venv\\Scripts\\python.exe Q:\\AI\\PIE\\tinker\\fetch_ckpt.py RUN NAME
      NAME: a checkpoints.jsonl name ("000835", "final") or "list"

Sampler checkpoints can't be downloaded, so this takes the row's state_path (tinker://.../weights/NAME), which
weights.download exports, downloads and decrypts.
"""
import json
import os
import sys
from pathlib import Path

os.environ["TINKER_API_KEY"] = open(r"B:\Dropbox\Dropbox\AI BRAIN\tinker.txt").read().strip()
from tinker_cookbook import weights

run, name = sys.argv[1], sys.argv[2]
rows = [json.loads(x) for x in open(Path(r"Q:\AI\PIE\tinker\runs") / run / "checkpoints.jsonl", encoding="utf-8")]
if name == "list":
    for r in rows:
        print(r.get("name"), {k: v for k, v in r.items() if k.endswith("path")})
    sys.exit(0)
row = [r for r in rows if r.get("name") == name][-1]
path = row.get("state_path") or row["path"]
out = Path(r"Q:\AI\PIE\tinker\ckpt") / run / name
out.mkdir(parents=True, exist_ok=True)
print("downloading", path, "->", out, flush=True)
weights.download(tinker_path=path, output_dir=str(out))
for p in sorted(out.rglob("*")):
    if p.is_file():
        print(f"  {p.relative_to(out)}  {p.stat().st_size / 1e6:.1f} MB")
