"""Seed-VC v1 (Plachtaa/seed-vc @ 51383ef, GPL-3.0 code and weights): every eSpeak source x every Kokoro
reference, in two modes.

    cd tts/vc/src/seed-vc && ../../.venv-seedvc/bin/python ../../convert_seedvc.py speech   # 22.05 kHz
    cd tts/vc/src/seed-vc && ../../.venv-seedvc/bin/python ../../convert_seedvc.py f0       # 44.1 kHz, F0-conditioned
Runs the clone's own inference.main (its documented CLI entry point) once per pair, with load_models cached so
the models load once; it must run from inside the clone (its HF cache is ./checkpoints). speech = default
whisper-small DiT; f0 = whisper-base DiT conditioned on the source's RMVPE F0 with auto-f0-adjust off, i.e. the
source contour is kept as is. fp16 off (CPU/MPS). Output tts/vc/audio/seedvc[-f0]/<id>.seedvc[-f0]-<voice>.wav."""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

VC = Path(__file__).resolve().parent
sys.path.insert(0, os.getcwd())
assert Path("inference.py").exists(), "run from inside tts/vc/src/seed-vc"
import inference  # noqa: E402
import torch  # noqa: E402

# MPS fails in BigVGAN's anti-aliased resampler ("Output channels > 65536 not supported", not covered by
# PYTORCH_ENABLE_MPS_FALLBACK), so the whole pipeline runs on CPU.
inference.device = torch.device(os.environ.get("SEEDVC_DEVICE", "cpu"))

mode = sys.argv[1]
tag = "seedvc" if mode == "speech" else "seedvc-f0"
steps = int(os.environ.get("SEEDVC_STEPS", "30"))
args = argparse.Namespace(diffusion_steps=steps, length_adjust=1.0, inference_cfg_rate=0.7,
                          f0_condition=(mode == "f0"), auto_f0_adjust=False, semi_tone_shift=0,
                          checkpoint=None, config=None, fp16=False, output=str(VC / "audio" / tag / "_raw"))
models = inference.load_models(args)
inference.load_models = lambda a: models

srcs = json.loads((VC / "audio" / "espeak.json").read_text("utf-8"))
out_dir = VC / "audio" / tag
log = []
for voice in ["hm_omega", "ef_dora", "em_alex"]:
    for s in srcs:
        args.source, args.target = s["wav"], str(VC / "audio" / "ref" / f"{voice}.wav")
        t = time.time()
        inference.main(args)
        raw = Path(args.output) / f"vc_{s['id']}_{voice}_1.0_{steps}_0.7.wav"
        out = out_dir / f"{s['id']}.{tag}-{voice}.wav"
        raw.replace(out)
        log.append(dict(id=s["id"], voice=voice, wav=str(out), steps=steps, seconds=round(time.time() - t, 2)))
        print(voice, s["id"], log[-1]["seconds"], "s", flush=True)
weights = {str(p.relative_to("checkpoints")): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in Path("checkpoints").rglob("*") if p.is_file() and p.suffix in (".pth", ".pt", ".bin", ".safetensors")}
(out_dir / "log.json").write_text(json.dumps(dict(device=str(inference.device), weights=weights, clips=log), indent=1), "utf-8")
