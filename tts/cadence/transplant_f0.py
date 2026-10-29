"""Put the source's pitch curve back onto a converted render of it (same timeline, e.g. ElevenLabs output of
an OpenVoice render of tts/cadence/cadence.py output): PSOLA (Praat), every pitch point of the target set to
the source's F0 at that time, moved into the target's register (median-to-median); where the source is
unvoiced the target's own F0 is kept. F0_RANGE (default 1) widens the source's excursions around its median. MICRO=1 keeps the target's own
micro-variation: the new F0 is the smoothed source curve times target / smoothed target (both smoothed
over SMOOTH_MS, default 120 ms), so only the slow melody comes from the source.

    tts/vc/.venv-eval/bin/python -I tts/cadence/transplant_f0.py <source.wav> <target> <out.wav>"""
import os
import sys

import librosa
import numpy as np
import parselmouth
from parselmouth.praat import call

src, tgt, out = sys.argv[1:4]
a, sr = librosa.load(tgt, sr=None, mono=True)
snd = parselmouth.Sound(a, sr)
sp = parselmouth.Sound(src).to_pitch_ac(0.01, 50, 500)
f_src = sp.selected_array["frequency"]
tpitch = snd.to_pitch_ac(0.01, 50, 500)
tp = tpitch.selected_array["frequency"]
MICRO = os.environ.get("MICRO") == "1"
W = float(os.environ.get("SMOOTH_MS", "120")) / 1000


def smooth_at(pitch, t):
    """mean voiced F0 in semitones over t ± W/2 (None if nothing voiced)"""
    v = [pitch.get_value_at_time(x) for x in np.arange(t - W / 2, t + W / 2 + 1e-9, 0.01)]
    v = [x for x in v if x and not np.isnan(x) and x > 0]
    return 2 ** (np.mean(12 * np.log2(v)) / 12) if v else None
med_s, med_t = np.median(f_src[f_src > 0]), np.median(tp[tp > 0])
shift, rng = med_t / med_s, float(os.environ.get("F0_RANGE", "1"))
man = call(snd, "To Manipulation", 0.01, 50, 500)
pt = call(man, "Extract pitch tier")
new = call("Create PitchTier", "p", 0, snd.duration)
moved = kept = 0
for i in range(1, call(pt, "Get number of points") + 1):
    t, f = call(pt, "Get time from index", i), call(pt, "Get value at index", i)
    fs = sp.get_value_at_time(t)
    if fs and not np.isnan(fs) and fs > 0:
        if MICRO:
            ss, ts = smooth_at(sp, t), smooth_at(tpitch, t)
            if ss and ts:
                fs = ss * (f / ts) ** (1 / rng)   # the target's wobble, unscaled after the range power
        call(new, "Add point", t, med_t * (fs / med_s) ** rng); moved += 1
    else:
        call(new, "Add point", t, f); kept += 1
call([man, new], "Replace pitch tier")
y = call(man, "Get resynthesis (overlap-add)")
v = y.values[0]; y = parselmouth.Sound(v / np.abs(v).max() * 0.89, sr)
y.save(out, "WAV")
print(out, f"register ×{shift:.2f} ({12 * np.log2(shift):+.1f} st), {moved} points from source, {kept} kept")
