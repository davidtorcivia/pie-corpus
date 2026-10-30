"""Put back the laryngeals a voice converter deleted, in one deterministic pass (no re-rendering).

    tts/vc/.venv-eval/bin/python -I tts/cadence/restore.py CONVERTED VTL.wav PHONES.json OUT.wav

Neural converters (ElevenLabs, Cartesia, Chatterbox) keep timing but treat a short voiceless noise as background
and remove it. Word-final H before a pause suffers most. The pie_vtl.py phone JSON says exactly where every h and χ is.
The converter's output is aligned to the VTL render (energy-envelope cross-correlation) and each h/χ is measured.
Only the tokens below threshold are rebuilt, and nothing else in the audio is touched:
- h: white noise filtered by the converted voice's own neighbouring vowel. The filter is an LPC envelope of
  that vowel in the converted audio: the following vowel for initial h, the preceding one for final H,
  a crossfade between them inside a word. F1 is damped and energy above 7 kHz rolled off.
  The level is H_LEVEL dB re that vowel, and a word-final H fades out over its second half.
- χ: noise shaped to eSpeak's χ spectrum (as in pie_vtl.py) at CHI_LEVEL dB re the nearest vowel.
  What the converter left stays underneath.
Where the converter deleted an h, it usually stretched the neighbouring vowel across it rather than leaving silence.
So a rebuilt token first ducks the converter's audio over the interval (H_DUCK / CHI_DUCK, 10 ms ramps),
then lays the noise in.
A word-final H that the VTL render itself voices (pie_vtl.py --final-h murmur: share under 0.15 there) is a
murmured tail the converter usually keeps. It is not ducked; breath is added over its second half only.
Env: H_LEVEL (−12), CHI_LEVEL (−9), H_DUCK (0.85), CHI_DUCK (0.5), H_MIN_SHARE (0.25), CHI_MIN_SHARE (0.30),
FORCE=1 rebuilds every token."""
import json, os, sys

import librosa
import numpy as np
import soundfile as sf

H_LEVEL = float(os.environ.get("H_LEVEL", "-12"))
CHI_LEVEL = float(os.environ.get("CHI_LEVEL", "-9"))
H_MIN, CHI_MIN = float(os.environ.get("H_MIN_SHARE", "0.25")), float(os.environ.get("CHI_MIN_SHARE", "0.30"))
FORCE = os.environ.get("FORCE") == "1"
H_DUCK, CHI_DUCK = float(os.environ.get("H_DUCK", "0.85")), float(os.environ.get("CHI_DUCK", "0.5"))
NUC = ("V", "Ns", "Ls", "Rs")
CHI_TEMPLATE = [(0, -40), (300, -24), (600, -10), (750, -4.6), (1000, -11.2), (1250, -7.1), (1600, -2.6),
                (2000, -5.2), (2500, -7.6), (3150, -14.0), (4000, -6.4), (5000, -8.1), (6300, -24.0),
                (8000, -40.0), (10000, -50.0), (24000, -70)]


def lag_s(a, sr_a, ref, sr_r, max_s=0.3):
    """seconds to add to the reference's times to land on a's timeline"""
    env = lambda x, sr: np.log(librosa.feature.rms(y=librosa.resample(x, orig_sr=sr, target_sr=8000),
                                                    frame_length=80, hop_length=40)[0] + 1e-4)
    e, r = env(a, sr_a), env(ref, sr_r); n = min(len(e), len(r)); m = int(max_s * 200)
    k = max(range(-m, m + 1), key=lambda k: np.corrcoef(e[max(k, 0):n + min(k, 0)], r[max(-k, 0):n - max(k, 0)])[0, 1])
    return k / 200


def share(x, sr):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; f = np.fft.rfftfreq(len(x), 1 / sr)
    return X[(f >= 2000) & (f < 8000)].sum() / (X[(f >= 50) & (f < 8000)].sum() + 1e-12)


def rms(x):
    return float(np.sqrt((x ** 2).mean()) + 1e-9)


def lpc_env(x, n, sr):
    order = 2 + sr // 1000
    x = np.append(x[0], x[1:] - 0.97 * x[:-1]) * np.hamming(len(x))
    r = np.correlate(x, x, "full")[len(x) - 1:len(x) + order]; r[0] *= 1.0001
    a, e = np.zeros(order + 1), r[0]; a[0] = 1.0
    for i in range(1, order + 1):
        k = -(r[i] + a[1:i] @ r[i - 1:0:-1]) / e
        a[1:i + 1] += k * np.r_[a[i - 1:0:-1], 1.0]; e *= 1 - k * k
    f = np.fft.rfftfreq(n, 1 / sr)
    env = 1 / (np.abs(np.fft.rfft(a, n)) + 1e-9)
    env *= np.where(f < 500, (np.maximum(f, 50) / 500) ** 1.0, 1.0)      # open glottis damps F1
    env *= np.where(f > 7000, (7000 / np.maximum(f, 7000)) ** 4, 1.0)
    return env / env.max()


def main(conv_p, vtl_p, json_p, out_p):
    y, sr = librosa.load(conv_p, sr=None, mono=True)
    ref, sr_r = librosa.load(vtl_p, sr=None, mono=True)
    d = lag_s(y, sr, ref, sr_r)
    J = json.load(open(json_p, encoding="utf-8"))
    rng = np.random.default_rng(0)
    seg = lambda t0, t1: y[max(int((t0 + d) * sr), 0):int((t1 + d) * sr)]
    nucs = [p for w in J["words"] for p in w["phones"] if p["kind"] in NUC]
    mid = lambda p: seg(p["start"] + 0.2 * (p["end"] - p["start"]), p["end"] - 0.2 * (p["end"] - p["start"]))
    vmed = np.median([rms(mid(p)) for p in nucs])
    out = y.copy(); report = []
    ref_share = lambda p: share(ref[int(p["start"] * sr_r):int(p["end"] * sr_r)], sr_r)
    for w in J["words"]:
        ph = w["phones"]
        for i, p in enumerate(ph):
            base = p["phone"].rstrip("ʷ")
            if base not in ("h", "χ"): continue
            x = seg(p["start"], p["end"])
            sh, lv = share(x, sr), 20 * np.log10(rms(x) / vmed)
            need = FORCE or sh < (H_MIN if base == "h" else CHI_MIN)
            murmur = base == "h" and i == len(ph) - 1 and ref_share(p) < 0.15
            report.append(f"{w['word']:14s} {p['phone']:3s} share {sh:.2f} level {lv:+5.1f} dB  "
                          f"{('BREATH ADDED' if murmur else 'REBUILT') if need else 'kept'}")
            if not need: continue
            a, b = max(int((p["start"] + d - 0.005) * sr), 0), int((p["end"] + d + 0.005) * sr); n = b - a
            prev = next((q for q in reversed(ph[:i]) if q["kind"] in NUC + ("G",)), None)
            nxt = next((q for q in ph[i + 1:] if q["kind"] in NUC + ("G",)), None)
            ramp = min(int(0.012 * sr), n // 2)
            env = np.ones(n); env[:ramp] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ramp)); env[n - ramp:] = env[:ramp][::-1]
            if murmur:                                       # breath over the second half, the tail itself kept
                h = n // 2; env[:h] = 0; env[h:h + ramp] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, len(env[h:h + ramp])))
            if base == "h":
                cols = [v for v in (prev, nxt) if v is not None] or [min(nucs, key=lambda v: abs(v["start"] - p["start"]))]
                layers = []
                for v in cols:
                    vx = mid(v)
                    z = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * lpc_env(vx, n, sr), n)
                    layers.append(z / rms(z) * rms(vx) * 10 ** (H_LEVEL / 20))
                noise = layers[0] * (1 - np.linspace(0, 1, n)) + layers[1] * np.linspace(0, 1, n) if len(layers) == 2 else layers[0]
                if nxt is None and not murmur:                   # word-final H: breath dies away
                    h = n // 2; env[h:] *= np.linspace(1, 0, n - h) ** 1.5
            else:
                near = min(nucs, key=lambda v: min(abs(v["start"] - p["end"]), abs(v["end"] - p["start"])))
                f = np.fft.rfftfreq(n, 1 / sr); hz, db = zip(*CHI_TEMPLATE)
                z = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * 10 ** (np.interp(f, hz, db) / 20), n)
                noise = z / rms(z) * rms(mid(near)) * 10 ** (CHI_LEVEL / 20)
            duck = np.ones(n); r = min(int(0.010 * sr), n // 2)
            duck[:r] = np.linspace(1, 0, r); duck[n - r:] = np.linspace(0, 1, r); duck[r:n - r] = 0
            if base == "h" and nxt is None: duck[n - r:] = 0          # word-final: the vowel stays cut
            keep = 1 - (0 if murmur else H_DUCK if base == "h" else CHI_DUCK) * (1 - duck)
            out[a:b] = out[a:b] * keep + noise * env
    out = out / max(1.0, np.abs(out).max() / 0.99)
    sf.write(out_p, out, sr)
    print(f"{out_p}  (converter offset {d * 1000:+.0f} ms)"); print("\n".join("  " + r for r in report))


if __name__ == "__main__":
    main(*sys.argv[1:5])
