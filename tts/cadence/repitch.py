"""Put the cadence melody onto a converted render of it (same timeline), as one smooth, bounded shift curve.

    tts/vc/.venv-eval/bin/python -I tts/cadence/repitch.py <source.wav> <target> <out.wav> [psola|world]

The target keeps its own pitch detail; only the slow melody changes. In semitones:
    shift(t) = med_t + RANGE * (src_smooth(t) - med_s) - tgt_smooth(t)
where *_smooth is the voiced F0 averaged over SMOOTH_MS and med_* the voiced medians. The shift curve is filled
across frames where either side is unvoiced (no jumps at voicing edges), smoothed again, and soft-limited to
±LIMIT st (LIMIT·tanh(x/LIMIT)), since large shifts are what make PSOLA phasey. It is applied by
- psola: Praat overlap-add, pitch points = the target's own F0 × 2^(shift/12) (pitch floor 75 Hz, so the
  pulse marks are not placed on half periods);
- world: WORLD vocoder (pyworld harvest/cheaptrick/d4c), F0 multiplied by the shift, spectral envelope and
  aperiodicity kept.
Env: RANGE (1.6), SMOOTH_MS (120), LIMIT (3.5)."""
import os
import sys

import librosa
import numpy as np
import parselmouth
from parselmouth.praat import call

RANGE = float(os.environ.get("RANGE", "1.6"))
SMOOTH = float(os.environ.get("SMOOTH_MS", "120")) / 1000
LIMIT = float(os.environ.get("LIMIT", "3.5"))
STEP, FLOOR, CEIL = 0.005, 75, 400


def st_track(a, sr, n):
    f = parselmouth.Sound(a, sr).to_pitch_ac(STEP, FLOOR, CEIL).selected_array["frequency"]
    f = np.pad(f, (0, max(0, n - len(f))))[:n]
    s = np.where(f > 0, 12 * np.log2(np.maximum(f, 1e-9)), np.nan)
    med = np.nanmedian(s)
    s = np.where(s - med > 6, s - 12, s)          # fold octave errors back toward the median
    return np.where(med - s > 6, s + 12, s), med


def smooth_nan(s, win):
    """mean of the voiced frames within ±win/2 (NaN where none)"""
    k = max(1, int(round(win / STEP)))
    v = np.nan_to_num(s); w = (~np.isnan(s)).astype(float)
    ker = np.ones(k)
    num, den = np.convolve(v, ker, "same"), np.convolve(w, ker, "same")
    return np.where(den > k * 0.2, num / np.maximum(den, 1e-9), np.nan)


def fill(x):
    idx = np.arange(len(x)); ok = ~np.isnan(x)
    return np.interp(idx, idx[ok], x[ok]) if ok.any() else np.zeros_like(x)


def shift_curve(src, sr_s, tgt, sr_t):
    n = int(len(tgt) / sr_t / STEP) + 1
    S, med_s = st_track(src, sr_s, n)
    T, med_t = st_track(tgt, sr_t, n)
    sh = med_t + RANGE * (smooth_nan(S, SMOOTH) - med_s) - smooth_nan(T, SMOOTH)
    sh = fill(sh)
    sh = np.convolve(sh, np.ones(9) / 9, "same")     # 45 ms
    return LIMIT * np.tanh(sh / LIMIT), T


def psola(tgt, sr, sh):
    snd = parselmouth.Sound(tgt, sr)
    man = call(snd, "To Manipulation", 0.01, FLOOR, CEIL)
    pt = call(man, "Extract pitch tier")
    new = call("Create PitchTier", "p", 0, snd.duration)
    for i in range(1, call(pt, "Get number of points") + 1):
        t, f = call(pt, "Get time from index", i), call(pt, "Get value at index", i)
        call(new, "Add point", t, f * 2 ** (sh[min(int(t / STEP), len(sh) - 1)] / 12))
    call([man, new], "Replace pitch tier")
    return call(man, "Get resynthesis (overlap-add)").values[0]


def world(tgt, sr, sh):
    import pyworld as pw
    x = tgt.astype(np.float64)
    f0, t = pw.harvest(x, sr, f0_floor=FLOOR, f0_ceil=CEIL, frame_period=STEP * 1000)
    sp, ap = pw.cheaptrick(x, f0, t, sr), pw.d4c(x, f0, t, sr)
    k = np.minimum((t / STEP).astype(int), len(sh) - 1)
    return pw.synthesize(f0 * 2 ** (sh[k] / 12), sp, ap, sr, frame_period=STEP * 1000)


def main(src_p, tgt_p, out, method="psola"):
    src, sr_s = librosa.load(src_p, sr=None, mono=True)
    tgt, sr = librosa.load(tgt_p, sr=None, mono=True)
    sh, _ = shift_curve(src, sr_s, tgt, sr)
    y = (psola if method == "psola" else world)(tgt, sr, sh)
    y = y / np.abs(y).max() * 0.89
    parselmouth.Sound(y, sr).save(out, "WAV")
    print(out, method, f"shift |st| median {np.median(np.abs(sh)):.1f}, p90 {np.percentile(np.abs(sh), 90):.1f}, "
                       f"max {np.abs(sh).max():.1f}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
