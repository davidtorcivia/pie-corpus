"""Put the source's pitch curve back onto a converted render of it (same timeline, e.g. ElevenLabs output of
an OpenVoice render of tts/cadence/cadence.py output): PSOLA (Praat), every pitch point of the target set to
the source's F0 at that time, moved into the target's register (median-to-median); where the source is
unvoiced the target's own F0 is kept. F0_RANGE (default 1) widens the source's excursions around its median.

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
tp = snd.to_pitch_ac(0.01, 50, 500).selected_array["frequency"]
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
        call(new, "Add point", t, med_t * (fs / med_s) ** rng); moved += 1
    else:
        call(new, "Add point", t, f); kept += 1
call([man, new], "Replace pitch tier")
y = call(man, "Get resynthesis (overlap-add)")
v = y.values[0]; y = parselmouth.Sound(v / np.abs(v).max() * 0.89, sr)
y.save(out, "WAV")
print(out, f"register ×{shift:.2f} ({12 * np.log2(shift):+.1f} st), {moved} points from source, {kept} kept")
