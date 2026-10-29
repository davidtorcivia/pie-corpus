"""OpenVoice V2 tone-colour conversion of the cadence renders (same pinned setup as tts/vc/convert_openvoice.py).

    tts/vc/.venv-openvoice/bin/python -I tts/cadence/convert_openvoice.py <src.wav> <voice> <out.wav>"""
import sys
from pathlib import Path

VC = Path(__file__).resolve().parents[1] / "vc"
sys.path.insert(0, str(VC / "src" / "OpenVoice"))
from openvoice.api import OpenVoiceBaseClass, ToneColorConverter  # noqa: E402

src, voice, out = sys.argv[1:4]
CK = VC / "cache" / "openvoice"
tcc = ToneColorConverter.__new__(ToneColorConverter)
OpenVoiceBaseClass.__init__(tcc, str(CK / "config.json"), device="cpu")
tcc.watermark_model, tcc.version = None, getattr(tcc.hps, "_version_", "v1")
tcc.load_ckpt(str(CK / "checkpoint.pth"))
tcc.convert(src, tcc.extract_se([src]), tcc.extract_se([str(VC / "audio" / "ref" / f"{voice}.wav")]),
            output_path=out, tau=0.3)
print(out)
