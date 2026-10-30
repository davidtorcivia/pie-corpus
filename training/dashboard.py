"""Training dashboard: serves the runs directory and a live page (standard library only).

    python dashboard.py [--runs Q:\\AI\\PIE\\runs] [--port 8790]      then open http://127.0.0.1:8790

GET /api/runs        every run: its config.json and metrics.jsonl
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


def make_handler(runs: Path):
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
                return self.json(out)
            if u.path == "/api/gens":
                d = runs / q.get("run", [""])[0]
                e = q.get("epoch", ["1"])[0]
                if not d.resolve().is_relative_to(runs.resolve()):
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
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8790)
    a = ap.parse_args()
    runs = Path(a.runs)
    runs.mkdir(parents=True, exist_ok=True)
    print(f"dashboard on http://{a.host}:{a.port}")
    ThreadingHTTPServer((a.host, a.port), make_handler(runs)).serve_forever()


if __name__ == "__main__":
    main()
