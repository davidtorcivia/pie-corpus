import json, sys, glob, os
for d in sorted(glob.glob(sys.argv[1] + "/*/")):
    p = d + "metrics.jsonl"
    if not os.path.exists(p): print(os.path.basename(d[:-1]), "no metrics"); continue
    for l in open(p):
        e = json.loads(l)
        if e["event"] == "train":
            print(os.path.basename(d[:-1]), e["step"], round(e["s_per_step"], 3), "mel", round(e["mel"], 3) if e["mel"] == e["mel"] else "nan",
                  "gen", round(e["gen"], 2) if e["gen"] == e["gen"] else "nan", "slm", round(e["slm"], 2) if e["slm"] == e["slm"] else "nan", "peak", e["peak_gib"])
    con = d + "console.log"
    if os.path.exists(con):
        tail = [l.rstrip() for l in open(con, errors="replace") if any(k in l for k in ("Error", "error:", "EXIT", "nan", "NaN"))]
        print("   ", tail[-3:])
