"""Quantize a merged HF model with omlx's oQ (owner, 2026-10-31: "use the omlx quant method ... preserve draft
heads"), through the running omlx server's admin API, and wait for it. Prints the output path.

    python3 -I training/tinker/omlx_oq.py MERGED_DIR [LEVEL]      # LEVEL default 5, enhanced, MTP kept: -oQ5e-mtp

Also: `omlx_oq.py --reload` (re-discover models), `--pin ID` / `--unpin ID`. The API key is read from
~/.omlx/settings.json and never printed.
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8000"
KEY = json.loads((Path.home() / ".omlx/settings.json").read_text())["auth"]["api_key"]


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read() or b"{}")


def main():
    a = sys.argv[1:]
    if a[0] == "--reload":
        print(call("POST", "/admin/api/reload"))
        return
    if a[0] in ("--pin", "--unpin"):
        print(call("PUT", f"/admin/api/models/{a[1]}/settings", {"is_pinned": a[0] == "--pin"}))
        return
    merged, level = a[0], float(a[1]) if len(a) > 1 else 5
    task = call("POST", "/admin/api/oq/start", {"model_path": merged, "oq_level": level, "enhanced": True,
                                                 "preserve_mtp": True})["task"]
    tid = task["task_id"]
    print("oQ task", tid, "->", task["output_path"], flush=True)
    while True:
        time.sleep(30)
        t = next(x for x in call("GET", "/admin/api/oq/tasks")["tasks"] if x["task_id"] == tid)
        print(f"  {t['status']} {t['progress']}% {t.get('phase') or ''}", flush=True)
        if t["status"] in ("completed", "failed", "cancelled"):
            if t["status"] != "completed":
                sys.exit(f"oQ {t['status']}: {t.get('error')}")
            print(t["output_path"])
            return


if __name__ == "__main__":
    main()
