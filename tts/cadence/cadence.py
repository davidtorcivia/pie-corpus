"""eSpeak with a recitation cadence: the exact eSpeak phones, re-timed and re-pitched as verse.

Each word is rendered by eSpeak alone (pie/pie-tone), then PSOLA (Praat via parselmouth) sets:
- duration: quantitative rhythm, the word stretched toward its syllable weights (pie.meter.weights:
  light 1 mora, heavy 2), with lengthening before the caesura and at line end;
- pitch: eSpeak's own accent peaks kept, a declination across each line, a fall on the line's last word,
  and a slow drift so the voice is not perfectly level;
- pauses: none between words inside a phrase (connected speech runs on), one at the caesura (after syllable 5
  in an 11, 4 in an 8), longest between lines;
- a word ending in h gets FINAL_H more time, so its tail (pie_vtl.py --final-h murmur) needn't eat the vowel.

    tts/vc/.venv-eval/bin/python -I tts/cadence/cadence.py t3-t026-00015 out.wav
    tts/vc/.venv-eval/bin/python -I tts/cadence/cadence.py tts/cadence/hardtest.txt out.wav   # a text file
    CADENCE_PITCH=0 ...   # the timing and pauses alone, eSpeak's own pitch
"""
import json, math, os, random, sys, tempfile
from pathlib import Path

import numpy as np
import parselmouth
from parselmouth.praat import call

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from pie.ipa import to_ipa
from pie.meter import line_syllables, verse_lines, weights, words
from pie.speak import speak_ipa

MORA = 0.165            # seconds per mora at this tempo (light syllable 1, heavy 2)
CAESURA_LEN, FINAL_LEN = 1.12, 1.35
GAP, CAESURA, LINE, END = 0.0, 0.24, 0.70, 0.9
FINAL_H = 0.06
DECL_START, DECL_END, FINAL_FALL = 1.5, -2.5, -2.0   # semitones
RATIO = (0.7, 1.7)
PITCH = os.environ.get("CADENCE_PITCH", "1") != "0"   # 0: timing and pauses only, eSpeak's own pitch


def record(rid):
    for f in (ROOT / "corpus/tier3").glob("*.jsonl"):
        for l in open(f, encoding="utf-8"):
            r = json.loads(l)
            if r["id"] == rid:
                return r
    raise SystemExit(f"{rid} not found")


def trim(snd, db=-40):
    a = snd.values[0]; thr = np.abs(a).max() * 10 ** (db / 20)
    idx = np.nonzero(np.abs(a) > thr)[0]
    return snd.extract_part(from_time=max(0, idx[0] / snd.sampling_frequency - 0.01),
                            to_time=min(snd.duration, idx[-1] / snd.sampling_frequency + 0.02))


def word_audio(w, tmp):
    out = Path(tmp) / f"w{abs(hash(w))}.wav"
    speak_ipa(to_ipa(w, tone=True), backend="espeak", out_wav=str(out), tone=True)
    return trim(parselmouth.Sound(str(out)))


def shape(snd, ratio, st_of, rng):
    """PSOLA: uniform stretch by ratio; pitch points moved by st_of(fraction through the word)."""
    man = call(snd, "To Manipulation", 0.01, 60, 400)
    dt = call("Create DurationTier", "d", 0, snd.duration)
    call(dt, "Add point", 0, ratio)
    call([man, dt], "Replace duration tier")
    pt = call(man, "Extract pitch tier")
    n = call(pt, "Get number of points")
    phase = rng.uniform(0, 2 * math.pi)
    for i in range(1, n + 1):
        t = call(pt, "Get time from index", i); f = call(pt, "Get value at index", i)
        st = st_of(t / snd.duration) + 0.3 * math.sin(2 * math.pi * 0.8 * t + phase) if PITCH else 0
        call(pt, "Remove point", i)
        call(pt, "Add point", t, f * 2 ** (st / 12))
    call([man, pt], "Replace pitch tier")
    return call(man, "Get resynthesis (overlap-add)")


def main(src, out_wav):
    r = {"pie": Path(src).read_text(encoding="utf-8")} if Path(src).is_file() else record(src)
    rng = random.Random(0)
    sr, parts, report, t = None, [], [], 0.0
    lines = verse_lines(r["pie"])
    with tempfile.TemporaryDirectory() as tmp:
        for li, line in enumerate(lines):
            ws, syl, wt = words(line), line_syllables(line), weights(line)
            assert sum(syl) == len(wt), (line, syl, wt)
            n = len(wt); cut = 5 if n >= 10 else 4
            pos = 0
            for wi, (w, k) in enumerate(zip(ws, syl)):
                wwt = wt[pos:pos + k]
                snd = word_audio(w, tmp); sr = sr or snd.sampling_frequency
                target = MORA * sum(2 if x == "H" else 1 for x in wwt)
                last, caes = wi == len(ws) - 1, pos < cut <= pos + k and wi < len(ws) - 1
                target *= FINAL_LEN if last else CAESURA_LEN if caes else 1
                target += FINAL_H if to_ipa(w, tone=True).endswith("h") else 0
                ratio = min(max(target / snd.duration, RATIO[0]), RATIO[1])
                a, b = pos / n, (pos + k) / n
                st_of = lambda x, a=a, b=b, last=last: (DECL_START + (DECL_END - DECL_START) * (a + (b - a) * x)
                                                       + (FINAL_FALL * x if last else 0))
                y = shape(snd, ratio, st_of, rng)
                parts.append(y.values[0])
                start, t = t, t + len(y.values[0]) / sr
                gap = END if (last and li == len(lines) - 1) else LINE if last else CAESURA if caes else GAP
                parts.append(np.zeros(int(gap * sr)))
                report.append({"line": li + 1, "word": w, "ipa": to_ipa(w, tone=True), "weights": wwt,
                               "start": round(start, 4), "end": round(t, 4), "espeak_s": round(snd.duration, 3),
                               "ratio": round(ratio, 2), "pause_after": gap})
                t += gap
                pos += k
    a = np.concatenate(parts); a = a / np.abs(a).max() * 0.89
    parselmouth.Sound(a, sampling_frequency=sr).save(out_wav, "WAV")
    json.dump(report, open(Path(out_wav).with_suffix(".json"), "w"), ensure_ascii=False, indent=1)
    print(out_wav, f"{len(a) / sr:.1f} s", len(report), "words")


if __name__ == "__main__":
    main(*sys.argv[1:3])
