#!/usr/bin/env python3
"""The translator app: a local web page over pie.translator (no language model).

    uv run --group translator python -I scripts/translator_server.py [--port 8765]

Then open http://127.0.0.1:8765. JSON API: POST /api/en2pie {"text": ...}, POST /api/pie2en {"text": ...}.
Standard library only (http.server); it binds to 127.0.0.1 unless --host says otherwise.
"""
import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pie.translator import english_to_pie, pie_to_english  # noqa: E402

PAGE = (ROOT / "scripts" / "translator_page.html").read_text("utf-8")
MAX_CHARS = 2000


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):
        if self.path not in ("/api/en2pie", "/api/pie2en"):
            return self._send(404, b"not found", "text/plain")
        try:
            # a negative length would read to the end of the connection (a stalled thread); no body is {}
            n = max(0, min(int(self.headers.get("Content-Length", "0") or 0), 64_000))
            body = json.loads(self.rfile.read(n) or b"{}")
            text = body.get("text", "") if isinstance(body, dict) else None
        except (ValueError, UnicodeDecodeError):
            text = None
        if not isinstance(text, str):
            return self._send(400, json.dumps({"error": "expected a JSON object {\"text\": string}"}).encode(),
                              "application/json")
        try:
            text = text[:MAX_CHARS]
            out = english_to_pie(text) if self.path == "/api/en2pie" else pie_to_english(text)
            self._send(200, json.dumps(out, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
        except Exception as e:                       # report, don't crash the server
            self._send(500, json.dumps({"error": str(e)}).encode("utf-8"), "application/json")

    def log_message(self, fmt, *args):
        sys.stderr.write("%s\n" % (fmt % args))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    # warm every cache before serving (the first request otherwise pays for them, ~30 s after a deploy that
    # changes an input of the caches): the memory and a rules translation (parser, lexmap, word vectors) …
    english_to_pie("Be well! The tiger ate the bread.")
    pie_to_english("wlkwos h2owim widet")           # … and the analyzer with its typed-spelling index (5 s)
    print(f"translator on http://{a.host}:{a.port}")
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
