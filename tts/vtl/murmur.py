"""Put back the murmur of bʰ dʰ gʰ gʷʰ that a voice converter weakens, on the pie_vtl phone timings (no re-rendering).

    python murmur.py CONVERTED.wav VTL.wav PHONES.json OUT.wav [--level -14] [--tilt 0.5] [--dur 0.060]

A murmured (breathy-voiced) release is voicing with an open glottis: breath noise over the voicing, and weaker
upper harmonics. Over the release of every Cʱ and the first MUR_DUR s of the sound after it (at most 60% of it),
both are laid in and then fade into modal voice:
  - breath noise coloured by the converted voice's own following vowel (the LPC envelope restore.py uses for h),
    LEVEL dB re that vowel;
  - a softened top: the window is mixed with its own 1.2 kHz low-pass, TILT at the release, fading to 0.
The converter's timeline is aligned to the VTL render first (restore.lag_s). Nothing else in the audio is touched.
"""
import argparse
import json
import os
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "cadence"))
import restore as R  # noqa: E402

NUC = ("V", "Ns", "Ls", "Rs")


def lowpass(x, sr, fc=1200.0):
    a = np.exp(-2 * np.pi * fc / sr)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc; y[i] = acc
    return y


def murmur(conv_p, vtl_p, json_p, out_p, level=-14.0, tilt=0.5, dur=0.060, seed=0):
    import librosa
    y, sr = librosa.load(conv_p, sr=None, mono=True)
    ref, sr_r = librosa.load(vtl_p, sr=None, mono=True)
    d = R.lag_s(y, sr, ref, sr_r)
    ph = [p for w in json.load(open(json_p, encoding="utf-8"))["words"] for p in w["phones"]]
    rng = np.random.default_rng(seed)
    out = y.copy(); n_done = 0
    for i, p in enumerate(ph[:-1]):
        if not p["phone"].endswith("ʱ"):
            continue
        nx = ph[i + 1]
        if nx["kind"] not in NUC + ("G", "L", "N", "R"):
            continue
        vow = next((q for q in ph[i + 1:] if q["kind"] in NUC), None)
        if vow is None:
            continue
        t0 = p["end"] - 0.005
        t1 = min(p["end"] + dur, nx["start"] + 0.6 * (nx["end"] - nx["start"]))
        a, b = int((t0 + d) * sr), int((t1 + d) * sr)
        n = b - a
        if n < int(0.02 * sr) or a < 0 or b > len(out):
            continue
        vd = vow["end"] - vow["start"]
        va, vb = int((vow["start"] + 0.3 * vd + d) * sr), int((vow["end"] - 0.2 * vd + d) * sr)
        vx = y[va:vb] if vb - va > int(0.015 * sr) else y[a:b]
        env = np.ones(n); r = int(0.005 * sr)
        env[:r] = np.linspace(0, 1, r)
        h = int(0.4 * n)
        env[h:] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, n - h))        # hold, then fade into modal voice
        z = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * R.lpc_env(vx, n, sr), n)
        noise = z / R.rms(z) * R.rms(vx) * 10 ** (level / 20)
        seg = out[a:b]
        soft = lowpass(seg, sr)
        beta = tilt * env
        out[a:b] = (1 - beta) * seg + beta * soft * (R.rms(seg) / (R.rms(soft) + 1e-12)) + noise * env
        n_done += 1
    out = out / max(1.0, np.abs(out).max() / 0.99)
    sf.write(out_p, out, sr, subtype="PCM_16")
    return n_done


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("conv"); ap.add_argument("vtl"); ap.add_argument("timing"); ap.add_argument("out")
    ap.add_argument("--level", type=float, default=-14.0)
    ap.add_argument("--tilt", type=float, default=0.5)
    ap.add_argument("--dur", type=float, default=0.060)
    a = ap.parse_args()
    print(murmur(a.conv, a.vtl, a.timing, a.out, a.level, a.tilt, a.dur), "murmured releases")
