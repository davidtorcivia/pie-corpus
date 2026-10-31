"""Training dashboard: serves the runs directory and a live page (standard library only).

    python dashboard.py [--runs Q:\\AI\\PIE\\runs] [--tinker Q:\\AI\\PIE\\tinker\\runs] [--port 8790]
    then open http://127.0.0.1:8790

GET /api/runs        every run: its config.json and metrics.jsonl; Tinker runs (training/tinker) as "tinker/<run>",
                     their cookbook logs converted to the same events (tinker_run)
GET /api/gens?run=R&epoch=N   that run's generations-eN.jsonl (and its scores-eN.json when the Mac has scored it)
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent


def read_jsonl(p: Path) -> list:
    if not p.exists():
        return []
    out = []
    for line in p.read_text("utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:          # a line being written right now
            pass
    return out


TINKER_WINDOW = 10      # Tinker logs every step; the 4B logs every 5. Mean train loss over windows of this many steps


def tinker_run(d: Path) -> dict:
    """A tinker_cookbook supervised run's log dir (config.json, metrics.jsonl, checkpoints.jsonl) as a dashboard run:
    the per-step train_mean_nll (nats per trained token, the 4B's loss) averaged over TINKER_WINDOW steps, the lr, and
    tokens per second of step time. Done when checkpoints.jsonl has its "final" row."""
    cfg = json.loads((d / "config.json").read_text("utf-8")) if (d / "config.json").exists() else {}
    rows = [m for m in read_jsonl(d / "metrics.jsonl") if "train_mean_nll" in m]
    epochs = cfg.get("num_epochs") or 1
    total = round((rows[-1]["step"] + 1) / rows[-1]["progress"]) if rows and rows[-1].get("progress") else None
    metrics, elapsed = [], 0.0
    for i in range(0, len(rows), TINKER_WINDOW):
        w = rows[i:i + TINKER_WINDOW]
        secs = sum(m.get("time/step") or 0 for m in w)
        elapsed += secs
        metrics.append({"event": "train", "step": w[-1]["step"], "epoch": round(w[-1]["progress"] * epochs, 3),
                        "loss": round(sum(m["train_mean_nll"] for m in w) / len(w), 4), "lr": w[-1]["learning_rate"],
                        "tok_per_s": round(sum(m["num_tokens"] for m in w) / secs) if secs else None,
                        "elapsed_min": round(elapsed / 60, 1)})
    ckpts = read_jsonl(d / "checkpoints.jsonl")
    if any(c.get("name") == "final" for c in ckpts):
        metrics.append({"event": "done", "step": rows[-1]["step"] if rows else 0, "elapsed_min": round(elapsed / 60, 1)})
    return {"name": f"tinker/{d.name}", "metrics": metrics,
            "config": {"model": cfg.get("model_name", ""), "lr": cfg.get("learning_rate"), "rank": cfg.get("lora_rank"),
                       "total_steps": total, "backend": "tinker",
                       "checkpoints": [c.get("name") for c in ckpts]},
            "epochs": sorted(int(p.stem.split("-e")[-1]) for p in d.glob("generations-e*.jsonl"))}


def make_handler(runs: Path, tinker: Path):
    class H(BaseHTTPRequestHandler):
        def send(self, code, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def json(self, obj):
            self.send(200, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            if u.path in ("/", "/index.html"):
                return self.send(200, (HERE / "dashboard.html").read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/runs":
                out = []
                for d in sorted(p for p in runs.iterdir() if p.is_dir()):
                    cfg = json.loads((d / "config.json").read_text("utf-8")) if (d / "config.json").exists() else {}
                    epochs = sorted(int(p.stem.split("-e")[-1]) for p in d.glob("generations-e*.jsonl"))
                    out.append({"name": d.name, "config": cfg, "metrics": read_jsonl(d / "metrics.jsonl"),
                                "epochs": epochs})
                if tinker.is_dir():
                    out += [tinker_run(d) for d in sorted(p for p in tinker.iterdir() if p.is_dir())]
                return self.json(out)
            if u.path == "/api/gens":
                name = q.get("run", [""])[0]
                root = tinker if name.startswith("tinker/") else runs
                d = root / name.removeprefix("tinker/")
                e = q.get("epoch", ["1"])[0]
                if not d.resolve().is_relative_to(root.resolve()):
                    return self.send(400, b"bad run", "text/plain")
                sc = d / f"scores-e{e}.json"
                return self.json({"gens": read_jsonl(d / f"generations-e{e}.jsonl"),
                                  "scores": json.loads(sc.read_text("utf-8")) if sc.exists() else None})
            self.send(404, b"not found", "text/plain")

        def log_message(self, *a):
            pass
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=r"Q:\AI\PIE\runs")
    ap.add_argument("--tinker", default=r"Q:\AI\PIE\tinker\runs")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8790)
    a = ap.parse_args()
    runs = Path(a.runs)
    runs.mkdir(parents=True, exist_ok=True)
    print(f"dashboard on http://{a.host}:{a.port}")
    ThreadingHTTPServer((a.host, a.port), make_handler(runs, Path(a.tinker))).serve_forever()


if __name__ == "__main__":
    main()
