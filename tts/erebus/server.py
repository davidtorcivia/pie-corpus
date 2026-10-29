"""HTTP front for the pitch-patched Kokoro backend of pie.speak (docs/pronunciation.md "Deployment on erebus").

Standard library only. Every request goes through the public pie.speak entry points (speak / speak_ipa with
backend="kokoro"), so the server renders exactly what a local run renders.

  GET  /health      {"status": "ok", ...} once the model and voices are loaded
  POST /speak       {"text": PIE, "voice": "hf_alpha", "pitch": true, "convention": "default",
                     "tone": true, "speed": 0.9, "seed": null}                       -> audio/wav
  POST /speak_ipa   {"ipa": converter IPA, "voice", "pitch", "tone", "speed", "seed"} -> audio/wav

A wav response carries X-PIE-IPA, X-PIE-Engine-Input and X-PIE-Voice (percent-encoded UTF-8). An error is
JSON {"error": message, "type": exception class} with status 400 (bad input), 404, 413 (too long) or 500.
Synthesis is serialized by a lock: pie.speak's pitch patch swaps a method on the shared model.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

import torch

from pie import speak as S
from pie.ipa import CONVENTIONS

MAX_TEXT = int(os.environ.get("PIE_TTS_MAX_TEXT", "2000"))     # characters of PIE text or IPA
MAX_BODY = 16 * 1024                                            # bytes of request JSON
VOICES = sorted(k[len("voices/"):-len(".pt")] for k in S.KOKORO_FILES if k.startswith("voices/"))
TONES = (True, False, "stress")
LOCK = threading.Lock()
STARTED = time.time()


class BadRequest(ValueError):
    pass


def _options(req: dict) -> dict:
    voice = req.get("voice", "hf_alpha")
    if voice not in VOICES:
        raise BadRequest(f"voice must be one of {VOICES}")
    pitch = req.get("pitch", True)
    if not isinstance(pitch, bool):
        raise BadRequest("pitch must be true or false")
    tone = req.get("tone", True)
    if tone not in TONES or isinstance(tone, int) and not isinstance(tone, bool):
        raise BadRequest('tone must be true, false or "stress"')
    speed = req.get("speed", 0.9)
    if isinstance(speed, bool) or not isinstance(speed, (int, float)) or not 0.5 <= speed <= 2.0:
        raise BadRequest("speed must be a number in [0.5, 2.0]")
    seed = req.get("seed")
    if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or not 0 <= seed < 2**32):
        raise BadRequest("seed must be null or an integer in [0, 2^32)")
    return {"voice": voice, "pitch": pitch, "tone": tone, "speed": float(speed), "seed": seed}


def _string(req: dict, key: str) -> str:
    s = req.get(key)
    if not isinstance(s, str) or not s.strip():
        raise BadRequest(f"{key!r} must be a non-empty string")
    if len(s) > MAX_TEXT:
        raise OverflowError(f"{key!r} is {len(s)} characters; the limit is {MAX_TEXT}")
    return s


def render(path: str, req: dict) -> tuple[bytes, S.SpeechResult]:
    o = _options(req)
    if path == "/speak":
        text = _string(req, "text")
        conv = req.get("convention", "default")
        if conv not in CONVENTIONS:
            raise BadRequest(f"convention must be one of {sorted(CONVENTIONS)}")
        call = lambda out: S.speak(text, backend="kokoro", out_wav=out, convention=conv, tone=o["tone"],  # noqa: E731
                                   voice=o["voice"], pitch=o["pitch"], speed=o["speed"])
    else:
        ipa = _string(req, "ipa")
        call = lambda out: S.speak_ipa(ipa, backend="kokoro", out_wav=out, tone=o["tone"], voice=o["voice"],  # noqa: E731
                                       pitch=o["pitch"], speed=o["speed"])
    with tempfile.TemporaryDirectory() as d, LOCK:
        if o["seed"] is not None:
            torch.manual_seed(o["seed"])
        res = call(str(Path(d) / "out.wav"))
        return Path(res.out_wav).read_bytes(), res


class Handler(BaseHTTPRequestHandler):
    server_version = "pie-tts/1"

    def log_message(self, fmt, *args):      # one line per request on stderr (docker logs); never the body
        sys.stderr.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%S"), fmt % args))

    def _send(self, code: int, body: bytes, ctype: str, headers: dict | None = None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, code: int, e: BaseException):
        body = json.dumps({"error": str(e), "type": type(e).__name__}, ensure_ascii=False).encode()
        self._send(code, body, "application/json; charset=utf-8")

    def do_GET(self):
        if self.path != "/health":
            return self._error(404, LookupError(f"no such endpoint: GET {self.path}"))
        body = {"status": "ok", "model": S.KOKORO_REPO, "revision": S.KOKORO_REVISION, "voices": VOICES,
                "torch": torch.__version__, "threads": torch.get_num_threads(), "max_text": MAX_TEXT,
                "uptime_s": round(time.time() - STARTED)}
        self._send(200, json.dumps(body).encode(), "application/json")

    def do_POST(self):
        if self.path not in ("/speak", "/speak_ipa"):
            return self._error(404, LookupError(f"no such endpoint: POST {self.path}"))
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._error(400, BadRequest("bad Content-Length"))
        if n > MAX_BODY:
            self.close_connection = True
            return self._error(413, OverflowError(f"request body over {MAX_BODY} bytes"))
        try:
            req = json.loads(self.rfile.read(n).decode("utf-8"))
            if not isinstance(req, dict):
                raise BadRequest("body must be a JSON object")
            wav, res = render(self.path, req)
        except OverflowError as e:
            return self._error(413, e)
        except (ValueError, UnicodeDecodeError) as e:     # BadRequest, JSON errors, UnsupportedPhone, bad PIE
            return self._error(400, e)
        except S.SpeechError as e:                          # e.g. a chunk over Kokoro's 510 phonemes
            return self._error(400, e)
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._error(500, e)
        self._send(200, wav, "audio/wav", {"X-PIE-IPA": quote(res.ipa), "X-PIE-Engine-Input": quote(res.engine_input),
                                           "X-PIE-Voice": quote(res.voice)})


def main():
    torch.set_num_threads(int(os.environ.get("PIE_TTS_THREADS", "6")))
    t = time.time()
    S._kokoro_model()                       # loads and sha256-checks the baked weights
    for v in VOICES:
        S._kokoro_voice(v)
    sys.stderr.write(f"model and {len(VOICES)} voices loaded in {time.time() - t:.1f}s; "
                     f"torch {torch.__version__}, {torch.get_num_threads()} threads\n")
    host, port = os.environ.get("PIE_TTS_HOST", "0.0.0.0"), int(os.environ.get("PIE_TTS_PORT", "8881"))
    srv = ThreadingHTTPServer((host, port), Handler)
    srv.daemon_threads = True
    sys.stderr.write(f"listening on {host}:{port}\n")
    srv.serve_forever()


if __name__ == "__main__":
    main()
