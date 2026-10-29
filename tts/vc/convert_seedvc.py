"""Seed-VC v1 (Plachtaa/seed-vc @ 51383ef, GPL-3.0 code and weights): every eSpeak source x every Kokoro
reference, in two modes.

    cd tts/vc/src/seed-vc && ../../.venv-seedvc/bin/python ../../convert_seedvc.py speech   # 22.05 kHz
    cd tts/vc/src/seed-vc && ../../.venv-seedvc/bin/python ../../convert_seedvc.py f0       # 44.1 kHz, F0-conditioned
Runs the clone's own inference.main (its documented CLI entry point) once per pair, with load_models cached so
the models load once; it must run from inside the clone (its HF cache is ./checkpoints). speech = default
whisper-small DiT; f0 = whisper-base DiT conditioned on the source's RMVPE F0 with auto-f0-adjust off, i.e. the
source contour is kept as is. fp16 off (CPU/MPS). Output tts/vc/audio/seedvc[-f0]/<id>.seedvc[-f0]-<voice>.wav.

    ... convert_seedvc.py f0 --queue <dir>    # job-queue worker (tts/finals/finals.py writes the jobs)
Queue mode: each <dir>/pending/*.json job is {"source", "voice", "shift", "out"}; a worker claims one by renaming
it into <dir>/claimed/ (atomic, so several workers can share a queue), converts it with --semi-tone-shift
`shift` (the whole source F0 contour moved by that many semitones; its shape is unchanged), writes `out`, and
moves the job to <dir>/done/ with its timing. It exits when nothing is pending. SEEDVC_THREADS caps torch's
CPU threads (set it to cores / workers)."""
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
if os.environ.get("SEEDVC_THREADS"):
    torch.set_num_threads(int(os.environ["SEEDVC_THREADS"]))

mode = sys.argv[1]
tag = "seedvc" if mode == "speech" else "seedvc-f0"
steps = int(os.environ.get("SEEDVC_STEPS", "30"))
args = argparse.Namespace(diffusion_steps=steps, length_adjust=1.0, inference_cfg_rate=0.7,
                          f0_condition=(mode == "f0"), auto_f0_adjust=False, semi_tone_shift=0,
                          checkpoint=None, config=None, fp16=False, output=str(VC / "audio" / tag / "_raw"))
models = inference.load_models(args)
inference.load_models = lambda a: models


def weight_hashes():
    return {str(p.relative_to("checkpoints")): hashlib.sha256(p.read_bytes()).hexdigest() for p in
            Path("checkpoints").rglob("*") if p.is_file() and p.suffix in (".pth", ".pt", ".bin", ".safetensors")}


if len(sys.argv) > 3 and sys.argv[2] == "--queue":
    q = Path(sys.argv[3])
    for d in ("pending", "claimed", "done"):
        (q / d).mkdir(parents=True, exist_ok=True)
    args.output = str(q / f"_raw-{os.getpid()}")  # per worker: the raw file name has no shift in it
    (q / "weights.json").write_text(json.dumps(weight_hashes(), indent=1), "utf-8")
    while True:
        for job in sorted((q / "pending").glob("*.json")):
            claimed = q / "claimed" / job.name
            try:
                job.replace(claimed)
            except FileNotFoundError:  # another worker took it
                continue
            break
        else:
            break
        j = json.loads(claimed.read_text("utf-8"))
        args.source, args.target = j["source"], str(VC / "audio" / "ref" / f"{j['voice']}.wav")
        args.semi_tone_shift = j.get("shift", 0)
        t = time.time()
        inference.main(args)
        raw = Path(args.output) / f"vc_{Path(j['source']).name.split('.')[0]}_{j['voice']}_1.0_{steps}_0.7.wav"
        Path(j["out"]).parent.mkdir(parents=True, exist_ok=True)
        raw.replace(j["out"])
        j.update(seconds=round(time.time() - t, 2), steps=steps, threads=torch.get_num_threads(), pid=os.getpid())
        (q / "done" / job.name).write_text(json.dumps(j, indent=1), "utf-8")
        claimed.unlink()
        print(job.name, j["seconds"], "s", flush=True)
    sys.exit(0)

sys.path.insert(0, str(VC))
from words import TIMBRES, selection  # noqa: E402

VOICES, ITEMS = selection(TIMBRES)  # env VC_VOICES / VC_ITEMS
srcs = json.loads((VC / "audio" / "espeak.json").read_text("utf-8"))
out_dir = VC / "audio" / tag
log = []
for voice in VOICES:
    for s in (x for x in srcs if ITEMS is None or x["id"] in ITEMS):
        args.source, args.target = s["wav"], str(VC / "audio" / "ref" / f"{voice}.wav")
        t = time.time()
        inference.main(args)
        raw = Path(args.output) / f"vc_{s['id']}_{voice}_1.0_{steps}_0.7.wav"
        out = out_dir / f"{s['id']}.{tag}-{voice}.wav"
        raw.replace(out)
        log.append(dict(id=s["id"], voice=voice, wav=str(out), steps=steps, seconds=round(time.time() - t, 2)))
        print(voice, s["id"], log[-1]["seconds"], "s", flush=True)
weights = weight_hashes()
(out_dir / f"log-{'-'.join(VOICES)}.json").write_text(json.dumps(dict(device=str(inference.device), weights=weights, clips=log), indent=1), "utf-8")
