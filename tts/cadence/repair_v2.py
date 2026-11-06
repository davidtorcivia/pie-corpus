"""Repair v2: three corrections applied after the converter and the v1 repairs (restore.py, retrill.py, murmur.py), on
the pie_vtl phone timings, so the speech set is corrected without re-rendering or re-converting a single clip.

    tts/vc/.venv-eval/bin/python -I tts/cadence/repair_v2.py MURMURED.wav VTL.wav PHONES.json OUT.wav

Found by measuring 28 clips per context and voice at every stage of the v10 corpus (2026-11-06), after the owner
heard them in the trained Kokoro voices:
- h before a front vowel (e, i, y) sounded as a hushing fricative ("zh", "ch"). VTL shapes h's noise by the
  following vowel, so before e/i it is a palatal [ç]: 89% of its energy above 2 kHz in the renders (h before a/o/u:
  32%), heard by the phone recognizer as ɕ/ʃ in 9 of 28 renders, and as ɕ/s/tʃ in 12 of 28 after conversion. Fix:
  the converter's token is ducked out and replaced by a plain breath: noise through the following vowel's LPC
  envelope with its bandwidths widened (a_k * BW**k) and its top tilted down, at H_LEVEL dB re that vowel, so it
  carries about the 2-8 kHz share of h before a back vowel.
- Phrase-final r ended in a drag or hiss in the trained voices. In the corpus the r before a pause trails off into
  breath (v9/v10 phrase ends), which the recognizer hears as a vowel, ð, l or ɕ/ʃ rather than r. Fix: the audio after
  a phrase-final r fades out over R_FADE s starting exactly at the r's end (render timing + alignment), so the r and
  its trill contacts are untouched and no breath follows it.
- t before i drifted toward k ("-sti" heard as "-ski") in the trained voices. This one the converter makes, in the
  male voice: s+t heard as k in 0 of 48 renders and 13 of 48 conversions (male 14 of 20, female 0 of 20 on the test
  clips). Replacing the converter's release here (step 3, T_FIX=1) does not undo it (still 13 of 48), nor does a VTL
  burst alone before conversion (pie_vtl --t-burst -10: male 13 of 20), so step 3 is off by default. What does work is
  at the render: pie_vtl v11 --st-voice-lead 0.010 --t-burst -4 --st-closure 0.025 (male 17 -> 2 of 17 on the worst
  clips), used to re-convert the 288 affected training clips (tts-corpus-v1/reconv-st).
After repair v2 on the 28-per-context test set: h before e/i heard with a hushing onset in 2 of 25 (from 17 of 25),
with a stop onset in 1 of 25 (from 9), 2-8 kHz share 0.93 -> 0.47 (inside qc.py's 0.25-0.60 h gate); phrase-final r
heard as ʃ/ɕ in 0 of 28 (from 2).
Env: H_LEVEL (-12), H_OVER (0.035), BW (0.88), R_FADE (0.08); T_FIX (0), T_LEVEL (-8), T_DUCK (0.85), T_ASP (0.015),
T_BURST (0.012). Deterministic (seeded noise)."""
import json, os, sys

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from restore import lag_s, rms, share  # the same alignment and measures as the v1 repair

H_LEVEL = float(os.environ.get("H_LEVEL", "-12"))
BW = float(os.environ.get("BW", "0.88"))
R_FADE = float(os.environ.get("R_FADE", "0.08"))
T_LEVEL = float(os.environ.get("T_LEVEL", "-8"))
T_DUCK = float(os.environ.get("T_DUCK", "0.85"))     # how much of the converter's own release (25 ms) is taken out
T_ASP = float(os.environ.get("T_ASP", "0.015"))
T_BURST = float(os.environ.get("T_BURST", "0.012"))
T_FIX = os.environ.get("T_FIX", "0") == "1"
NUC = ("V", "Ns", "Ls", "Rs")
FRONT = set("eiy") | {"j"}


def base(ph):
    import unicodedata
    return unicodedata.normalize("NFD", ph)[0]


def plain_env(x, n, sr):
    """the vowel's LPC envelope with widened bandwidths and a falling top: a breath, not a palatal hiss"""
    order = 2 + sr // 1000
    x = np.append(x[0], x[1:] - 0.97 * x[:-1]) * np.hamming(len(x))
    r = np.correlate(x, x, "full")[len(x) - 1:len(x) + order]; r[0] *= 1.0001
    a, e = np.zeros(order + 1), r[0]; a[0] = 1.0
    for i in range(1, order + 1):
        k = -(r[i] + a[1:i] @ r[i - 1:0:-1]) / e
        a[1:i + 1] += k * np.r_[a[i - 1:0:-1], 1.0]; e *= 1 - k * k
    a = a * BW ** np.arange(order + 1)                             # bandwidth expansion: flatter formants
    f = np.fft.rfftfreq(n, 1 / sr)
    env = 1 / (np.abs(np.fft.rfft(a, n)) + 1e-9)
    env *= np.where(f < 500, (np.maximum(f, 50) / 500), 1.0)       # open glottis damps F1
    env *= (1500 / np.maximum(f, 1500)) ** 1.0                     # tilt: the top of a breath falls off
    env *= np.where(f > 7000, (7000 / np.maximum(f, 7000)) ** 4, 1.0)
    return env / env.max()


def repair(conv_p, vtl_p, json_p, out_p, report=True):
    y, sr = librosa.load(conv_p, sr=None, mono=True)
    ref, sr_r = librosa.load(vtl_p, sr=None, mono=True)
    d = lag_s(y, sr, ref, sr_r)
    J = json.load(open(json_p, encoding="utf-8"))
    rng = np.random.default_rng(0)
    S = lambda t: max(int((t + d) * sr), 0)
    seg = lambda t0, t1: y[S(t0):S(t1)]
    mid = lambda p: seg(p["start"] + 0.2 * (p["end"] - p["start"]), p["end"] - 0.2 * (p["end"] - p["start"]))
    out = y.copy(); log = []
    words = J["words"]
    for wi, w in enumerate(words):
        ph = w["phones"]
        nxt_w = words[wi + 1] if wi + 1 < len(words) else None
        # 1. word-initial h before a front vowel: a plain breath in place of the converter's token
        if len(ph) > 1 and ph[0]["phone"] == "h" and (base(ph[1]["phone"]) in FRONT or ph[1]["phone"] == "j"):
            p, v = ph[0], next((q for q in ph[1:] if q["kind"] in NUC), ph[1])
            # the breath runs on into the vowel (H_OVER s), which comes back in under it: a breathy onset, not an attack
            ov = int(float(os.environ.get("H_OVER", "0.035")) * sr)
            a, b = S(p["start"] - 0.005), S(p["end"]) + ov; n = b - a
            if n > 64 + ov:
                vx = mid(v)
                z = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * plain_env(vx, n, sr), n)
                z = z / rms(z) * rms(vx) * 10 ** (H_LEVEL / 20)
                ramp = min(int(0.025 * sr), (n - ov) // 2)
                env = np.ones(n); env[:ramp] = np.sin(np.linspace(0, np.pi / 2, ramp)) ** 2; env[n - ov:] = np.cos(np.linspace(0, np.pi / 2, ov)) ** 2
                duck = np.zeros(n); r = min(int(0.010 * sr), n // 4); duck[:r] = np.linspace(1, 0, r); duck[n - ov:] = np.sin(np.linspace(0, np.pi / 2, ov)) ** 2
                before = share(out[a:b - ov], sr)
                out[a:b] = out[a:b] * duck + z * env
                log.append(f"{w['word']:14s} h -> breath   2-8k share {before:.2f} -> {share(out[a:b - ov], sr):.2f}")
        # 2. phrase-final r: no breath after it
        if ph and ph[-1]["phone"] == "r" and (nxt_w is None or nxt_w["line"] != w["line"] or nxt_w["start"] - w["end"] > 0.15):
            p = ph[-1]; a = S(p["end"]); n = int(R_FADE * sr)    # from the r's own end: the trill is never touched
            stop = S(nxt_w["start"]) if nxt_w else len(out)
            out[a:a + n] *= np.linspace(1, 0, len(out[a:a + n])) ** 1.5
            out[a + n:stop] = 0.0
            log.append(f"{w['word']:14s} final r: tail faded over {R_FADE * 1000:.0f} ms")
        # 3. (T_FIX=1 only; does not undo the converter's k) an alveolar release at every t before a vowel or glide
        for i, p in enumerate(ph[:-1] if T_FIX else []):
            if p["phone"] != "t" or ph[i + 1]["kind"] not in NUC + ("G",):
                continue
            v = next((q for q in ph[i + 1:] if q["kind"] in NUC), None)
            if v is None: continue
            # the converter's own release goes (it reads a dull VTL t after s as k); an alveolar one goes in:
            # a sharp 3.5-8 kHz burst, then a short aspiration shaped by the vowel, over the first 25 ms
            rel = S(p["end"]) - int(0.004 * sr); m = int(0.025 * sr); seg_ = out[rel:rel + m]
            duck = 1 - T_DUCK * np.sin(np.linspace(0, np.pi, len(seg_))) ** 0.5
            out[rel:rel + m] = seg_ * duck
            n = int(T_BURST * sr); f = np.fft.rfftfreq(n, 1 / sr); band = ((f >= 3500) & (f <= 8000)).astype(float)
            z = np.fft.irfft(np.fft.rfft(rng.standard_normal(n)) * band, n)
            z = z / rms(z) * rms(mid(v)) * 10 ** (T_LEVEL / 20) * np.exp(-np.linspace(0, 4, n))
            na = int(T_ASP * sr); asp = np.fft.irfft(np.fft.rfft(rng.standard_normal(na)) * plain_env(mid(v), na, sr), na)
            asp = asp / rms(asp) * rms(mid(v)) * 10 ** ((T_LEVEL - 8) / 20) * np.linspace(1, 0, na)
            out[rel:rel + n] += z[:len(out[rel:rel + n])]
            out[rel + n // 2:rel + n // 2 + na] += asp[:len(out[rel + n // 2:rel + n // 2 + na])]
            log.append(f"{w['word']:14s} t release")
    out = out / max(1.0, np.abs(out).max() / 0.99)
    sf.write(out_p, out, sr)
    if report:
        print(f"{out_p}  (offset {d * 1000:+.0f} ms)"); print("\n".join("  " + r for r in log))


if __name__ == "__main__":
    repair(*sys.argv[1:5])
