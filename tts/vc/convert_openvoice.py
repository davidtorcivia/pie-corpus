"""OpenVoice V2 tone-colour converter (myshell-ai/OpenVoice @ 74a1d14, weights myshell-ai/OpenVoiceV2 @ f36e7ed,
both MIT): every eSpeak source x every Kokoro reference.

    tts/vc/.venv-openvoice/bin/python -I tts/vc/convert_openvoice.py
Only openvoice.api.ToneColorConverter is used (no se_extractor/whisper, watermark off). The source tone-colour
embedding is extracted from all eSpeak source clips together, the target one from the Kokoro reference.
Output 22.05 kHz in tts/vc/audio/openvoice/<id>.openvoice-<voice>.wav."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VC = ROOT / "tts" / "vc"
sys.path.insert(0, str(VC / "src" / "OpenVoice"))
from openvoice.api import OpenVoiceBaseClass, ToneColorConverter  # noqa: E402

CK = VC / "cache" / "openvoice"
SHA = {"checkpoint.pth": "9652c27e92b6b2a91632590ac9962ef7ae2b712e5c5b7f4c34ec55ee2b37ab9e",  # = HF LFS oid
       "config.json": "9dfff60350b8c63f2c664efd92a61b2516efb22671466960f0e5dfebd881fa47"}
for f, h in SHA.items():
    assert hashlib.sha256((CK / f).read_bytes()).hexdigest() == h, f
TAU = float(os.environ.get("OV_TAU", "0.3"))

# The pinned api.py passes enable_watermark through to a base __init__ that rejects it, so construct the
# converter without wavmark the same way its __init__ does when the watermark is off.
tcc = ToneColorConverter.__new__(ToneColorConverter)
OpenVoiceBaseClass.__init__(tcc, str(CK / "config.json"), device="cpu")
tcc.watermark_model, tcc.version = None, getattr(tcc.hps, "_version_", "v1")
tcc.load_ckpt(str(CK / "checkpoint.pth"))
srcs = json.loads((VC / "audio" / "espeak.json").read_text("utf-8"))
src_se = tcc.extract_se([s["wav"] for s in srcs])
out_dir = VC / "audio" / "openvoice"
out_dir.mkdir(parents=True, exist_ok=True)
log = []
for voice in ["hm_omega", "ef_dora", "em_alex"]:
    tgt_se = tcc.extract_se([str(VC / "audio" / "ref" / f"{voice}.wav")])
    for s in srcs:
        t = time.time()
        out = out_dir / f"{s['id']}.openvoice-{voice}.wav"
        tcc.convert(s["wav"], src_se, tgt_se, output_path=str(out), tau=TAU)
        log.append(dict(id=s["id"], voice=voice, wav=str(out), tau=TAU, seconds=round(time.time() - t, 2)))
        print(voice, s["id"], log[-1]["seconds"], "s", flush=True)
(out_dir / "log.json").write_text(json.dumps(log, indent=1), "utf-8")
