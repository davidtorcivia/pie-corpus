"""watch.py: one health check of the Kokoro v2 run; prints a status line, exit code 0 ok / 2 problem / 3 finished"""
import json, os, sys, time
R = "/mnt/q/AI/PIE/runs/kokoro-v2"
log = open(f"{R}/run_all.log").read() if os.path.exists(f"{R}/run_all.log") else ""
if log.strip().endswith("run_all finished"):
    print("FINISHED"); sys.exit(3)
st = "stage2" if os.path.exists(f"{R}/stage2/metrics.jsonl") else "stage1"
ev = [json.loads(l) for l in open(f"{R}/{st}/metrics.jsonl") if l.strip()]
age = time.time() - os.path.getmtime(f"{R}/{st}/metrics.jsonl")
tail = open(f"{R}/{st}/console.log", errors="replace").read()[-20000:]
tr = [e for e in ev if e["event"] == "train"]
last = tr[-1] if tr else {}
vals = [round(e["mel"], 4) for e in ev if e["event"] == "val"]
msg = f"{st} epoch {last.get('epoch', 0) + 1} step {last.get('step')} mel {last.get('mel', float('nan')):.3f} {last.get('s_per_step')} s/step peak {last.get('peak_gib')} GiB; val {vals}; updated {age / 60:.0f} min ago"
bad = []
if "Traceback" in tail or "Error" in tail.split("EXIT")[-1][-3000:]: bad.append("error in console")
if "stage" in log.split("\n")[-2:][-1] and "not done" in log.split("\n")[-2:][-1]: bad.append(log.strip().split("\n")[-1])
if age > 20 * 60: bad.append("no metrics for 20 min")
if last and last.get("mel") != last.get("mel"): bad.append("mel NaN")
print(("PROBLEM: " + "; ".join(bad) + " | " if bad else "OK ") + msg)
sys.exit(2 if bad else 0)
