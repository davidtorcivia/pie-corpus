"""kNN-VC (bshall/knn-vc @ c616845, MIT): every eSpeak source x every Kokoro reference.

    TORCH_HOME=tts/vc/cache/torch tts/vc/.venv-knnvc/bin/python -I tts/vc/convert_knnvc.py
Loads the pinned clone through its documented entry point (torch.hub.load(..., source="local")); the
prematched HiFi-GAN and WavLM-Large weights are pre-placed in $TORCH_HOME/hub/checkpoints and sha256-checked
here, so nothing is fetched at run time. Output 16 kHz in tts/vc/audio/knnvc/<id>.knnvc-<voice>.wav."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torchaudio

ROOT = Path(__file__).resolve().parents[2]
VC = ROOT / "tts" / "vc"
SHA = {"WavLM-Large.pt": "6fb4b3c3e6aa567f0a997b30855859cb81528ee8078802af439f7b2da0bf100f",
       "prematch_g_02500000.pt": "f924c7632c6eaf99004386d62293e124419e33582573552a6ae976eb88ed2dd5"}
ck = Path(os.environ["TORCH_HOME"]) / "hub" / "checkpoints"
for f, h in SHA.items():
    got = hashlib.sha256((ck / f).read_bytes()).hexdigest()
    assert got == h, (f, got)

K = int(os.environ.get("KNN_K", "4"))
knn = torch.hub.load(str(VC / "src" / "knn-vc"), "knn_vc", source="local", prematched=True, trust_repo=True,
                     pretrained=True, device="cpu")


def load16(p):
    x, sr = sf.read(p, dtype="float32", always_2d=True)
    x = torch.from_numpy(np.ascontiguousarray(x.T.mean(0, keepdims=True)))
    return torchaudio.functional.resample(x, sr, 16000) if sr != 16000 else x


sys.path.insert(0, str(VC))
from words import TIMBRES, selection  # noqa: E402

VOICES, ITEMS = selection(TIMBRES)  # env VC_VOICES / VC_ITEMS
srcs = json.loads((VC / "audio" / "espeak.json").read_text("utf-8"))
out_dir = VC / "audio" / "knnvc"
out_dir.mkdir(parents=True, exist_ok=True)
log = []
for voice in VOICES:
    # vad_trigger_level=0 like the README; the reference is clean TTS with only 0.25 s pauses
    pool = knn.get_matching_set([load16(VC / "audio" / "ref" / f"{voice}.wav")], vad_trigger_level=0)
    for s in (x for x in srcs if ITEMS is None or x["id"] in ITEMS):
        t = time.time()
        q = knn.get_features(load16(s["wav"]))
        wav = knn.match(q, pool, topk=K).numpy()
        out = out_dir / f"{s['id']}.knnvc-{voice}.wav"
        sf.write(out, wav, 16000)
        log.append(dict(id=s["id"], voice=voice, wav=str(out), pool_frames=int(pool.shape[0]),
                        seconds=round(time.time() - t, 2)))
        print(voice, s["id"], log[-1]["seconds"], "s", flush=True)
(out_dir / f"log-{'-'.join(VOICES)}.json").write_text(json.dumps(log, indent=1), "utf-8")
