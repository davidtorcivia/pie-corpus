"""summarise benchmark runs: median s/step over the train events after the first two (warm-up, compile), s/sample"""
import json, statistics, sys
from pathlib import Path
root = Path(sys.argv[1])
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    ev = [json.loads(l) for l in open(d / "metrics.jsonl", encoding="utf-8")] if (d / "metrics.jsonl").exists() else []
    st = next((e for e in ev if e["event"] == "start"), {})
    tr = [e for e in ev if e["event"] == "train"]
    if len(tr) < 3:
        print(f"{d.name:22s} {len(tr)} train events (running or failed)"); continue
    sp = statistics.median(e["s_per_step"] for e in tr[2:])
    b = st.get("batch_size", 1)
    print(f"{d.name:22s} batch {b}  {sp:.3f} s/step  {sp / b * 1000:.0f} ms/sample  peak {max(e['peak_gib'] for e in tr):.1f} GiB  first {tr[0]['s_per_step']:.2f}  mel {tr[-1]['mel']:.3f}")
