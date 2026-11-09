"""Compare Kokoro Stage 2 epochs objectively and render demo clips (PIE fine-tune, tr-desktop WSL).

    cd /mnt/q/AI/PIE/train/kokoro && /root/kokoro-ft/venv/bin/python kokoro_select_v3.py OUT_DIR EPOCH_FILE [...]

Corpus v2 (2026-11-09): four speakers (training/speakers_v2.json), lists training/v2_{train,val}_list.txt, audio
/root/kokoro-ft/data-v2/wavs. For each epoch checkpoint (runs/kokoro-v2/stage2/epoch_2nd_NNNNN.pth):
  1. convert it to a Kokoro KModel checkpoint (scripts/test_inference.convert_checkpoint);
  2. extract a voicepack per speaker (scripts/extract_voicepack.py; 200 training clips of that speaker);
  3. synthesize every validation line (training/val_list.txt, its own speaker) and score it against the real
     recording: mel-cepstral distortion (MCD, dB, DTW-aligned, 13 MFCC-based cepstra), log-F0 RMSE on frames voiced
     in both (cents), and the duration ratio synth/real;
  4. render the first N OOD sentences (training/OOD_texts.txt) per speaker for listening.
Writes OUT_DIR/summary.json and OUT_DIR/<epoch>/{voices,val,demo}/.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import librosa
import torch

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "kokoro"))
sys.path.insert(0, str(ROOT / "scripts"))
from test_inference import convert_checkpoint  # noqa: E402
import types  # noqa: E402
# kokoro/__init__ imports the G2P pipeline (misaki, not installed here); load only the model module
_pkg = types.ModuleType("kokoro"); _pkg.__path__ = [str(ROOT / "kokoro" / "kokoro")]
sys.modules["kokoro"] = _pkg
from kokoro.model import KModel  # noqa: E402

SR = 24000
SPEAKERS = {0: ("pie_zazy", "ZAZY"), 1: ("pie_valeria", "VALERIA"), 2: ("pie_antonio", "ANTONIO"), 3: ("pie_w02", "W02")}
AUDIO = Path("/root/kokoro-ft/data-v2/wavs")
N_DEMO = 6


def mcd(a, b):
    ca = librosa.feature.mfcc(y=a, sr=SR, n_mfcc=14, n_fft=1024, hop_length=256)[1:]
    cb = librosa.feature.mfcc(y=b, sr=SR, n_mfcc=14, n_fft=1024, hop_length=256)[1:]
    _, wp = librosa.sequence.dtw(ca, cb, metric="euclidean")
    d = np.array([np.linalg.norm(ca[:, i] - cb[:, j]) for i, j in wp])
    return float((10 / np.log(10)) * np.sqrt(2) * d.mean() / 10)   # MFCC-scale MCD (relative, comparable across epochs)


def f0_rmse(a, b):
    fa = librosa.yin(a, fmin=60, fmax=500, sr=SR, frame_length=1024, hop_length=256)
    fb = librosa.yin(b, fmin=60, fmax=500, sr=SR, frame_length=1024, hop_length=256)
    ea, eb = librosa.feature.rms(y=a, hop_length=256)[0], librosa.feature.rms(y=b, hop_length=256)[0]
    va, vb = ea[: len(fa)] > 0.02 * ea.max(), eb[: len(fb)] > 0.02 * eb.max()
    la, lb = np.log2(fa), np.log2(fb)
    _, wp = librosa.sequence.dtw(la[None], lb[None])
    c = [1200 * (la[i] - lb[j]) for i, j in wp if va[i] and vb[j]]
    return float(np.sqrt(np.mean(np.square(c)))) if c else float("nan")


def main(out, epochs):
    out = Path(out)
    cfg = str(ROOT / "training/config.json")
    val = [l.split("|") for l in (ROOT / "training/v2_val_list.txt").read_text("utf-8").splitlines() if l.strip()]
    ood = [l.strip() for l in (ROOT / "training/OOD_texts.txt").read_text("utf-8").splitlines() if l.strip()][:N_DEMO]
    summary = {}
    for ep in epochs:
        ep = Path(ep)
        tag = ep.stem.replace("epoch_2nd_", "e")
        d = out / tag
        (d / "voices").mkdir(parents=True, exist_ok=True)
        kpath = d / f"kokoro_pie_{tag}.pth"
        if not kpath.exists():
            convert_checkpoint(str(ep), str(kpath))
        voices = {}
        for sid, (name, suffix) in SPEAKERS.items():
            vp = d / "voices" / f"{name}.pt"
            if not vp.exists():
                sd = out / f"audio-{name}"
                if not sd.exists():
                    sd.mkdir(parents=True)
                    for line in (ROOT / "training/v2_train_list.txt").read_text("utf-8").splitlines():
                        f = line.split("|")[0]
                        if f.endswith(f"__{suffix}.wav"):
                            (sd / f).symlink_to(AUDIO / f)
                subprocess.run([sys.executable, "scripts/extract_voicepack.py", "--model", str(ep), "--audio-dir", str(sd),
                                "--output", str(vp), "--device", "cuda"], check=True)
            voices[sid] = torch.load(vp, weights_only=True)
        model = KModel(config=cfg, model=str(kpath)).to("cuda").eval()

        def say(text, sid, speed=1.0):
            ps = text.strip()
            ref = voices[sid][min(len(ps), 509) - 1].to("cuda")
            with torch.no_grad():
                wav = model(ps, ref, speed)
            wav = wav.audio if hasattr(wav, "audio") else wav
            return wav.detach().float().cpu().numpy().squeeze()

        rows = []
        (d / "val").mkdir(exist_ok=True)
        for f, text, sid in val:
            sid = int(sid)
            syn = say(text, sid)
            real, _ = librosa.load(AUDIO / f, sr=SR)
            sf.write(d / "val" / f, syn, SR)
            rows.append({"file": f, "speaker": sid, "mcd": mcd(syn, real), "f0_cents": f0_rmse(syn, real),
                         "dur_ratio": len(syn) / len(real), "peak": float(np.abs(syn).max())})
        (d / "demo").mkdir(exist_ok=True)
        for i, text in enumerate(ood):
            for sid, (name, _) in SPEAKERS.items():
                sf.write(d / "demo" / f"ood{i:02d}_{name}.wav", say(text, sid), SR)
        agg = lambda k, s=None: float(np.nanmean([r[k] for r in rows if s is None or r["speaker"] == s]))
        summary[tag] = {"mcd": agg("mcd"), "f0_cents": agg("f0_cents"), "dur_ratio": agg("dur_ratio"),
                        **{f"mcd_{SPEAKERS[k][0][4:]}": agg("mcd", k) for k in SPEAKERS},
                        **{f"f0_{SPEAKERS[k][0][4:]}": agg("f0_cents", k) for k in SPEAKERS}, "clipped": sum(r["peak"] > 0.99 for r in rows),
                        "n": len(rows)}
        (d / "val_scores.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        print(tag, json.dumps(summary[tag]), flush=True)
        del model
        torch.cuda.empty_cache()
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    (out / "demo_texts.json").write_text(json.dumps(ood, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
