"""Quality checks for a render, from its audio + .json phone timings.

  python qc.py out/clip                                # out/clip.wav + out/clip.json
  python qc.py eleven.wav --timing out/clip.json       # any wav (e.g. ElevenLabs output) on that timeline
  python qc.py eleven.wav --timing out/clip.json --ref out/clip.wav   # ... first aligning it to the VTL render
  add --vowels for the per-nucleus table

Checks (thresholds overridable in check()):
  accent_lift   accented − unaccented nuclei, st, with each line's offset and slope regressed out
                (the plain difference is reported as accent_lift_raw_st)            ≥ 2.5
  voiced        share of nuclei with any tracked F0                        ≥ 0.97
  per nucleus   level: no vowel more than 8 dB below the clip's median vowel
                (syllabic m̩ n̩: 12 dB, nasal murmur is quieter by nature);
                voicing: ≥ 40 ms of tracked F0 (≥ 70% of the nucleus if it is shorter than 57 ms),
                tracked with a 34 ms span so the edges aren't under-read
  chi_share     2–8 kHz energy share at each χ (mid ±20 ms)                0.30 – 0.80
  h_share       2–8 kHz energy share at each h, median                     0.25 – 0.60
  h_level_db    (reported, not gated) level at each h re the median vowel — compare before/after ElevenLabs
  phrase_ends   decay of the last nucleus before every pause ≥ 0.2 s (10 → 30 dB under its peak, as vtl_ends.py);
                gated for vowel/sonorant endings: ≥ 120 ms at line ends (≥ 0.5 s), ≥ 80 ms at caesuras.
                Also its F0 from the last nucleus to word end + 120 ms: span (90th − 3rd percentile) ≤ 1 st
                at caesuras, ≤ 3 st at line ends; floor (3rd percentile re the nucleus) ≥ −3.9 st (0.8×)
  final_h       with --final-h murmur: each word-final H (a breathy vowel tail) with its voiced ms, level
                and share; these are left out of the h-share gate
"""
import json, sys, wave
import numpy as np

NUCLEI = ("V", "Ns", "Ls", "Rs")


def load_wav(path, sr_out=44100):
    """Any PCM/float wav, mono or stereo, resampled to sr_out. (mp3: convert with ffmpeg first.)"""
    try:
        from scipy.io import wavfile
        sr, raw = wavfile.read(path)
        a = raw.astype(float)
        if np.issubdtype(raw.dtype, np.integer): a /= float(np.iinfo(raw.dtype).max)
        if a.ndim > 1: a = a.mean(1)
    except ImportError:
        w = wave.open(path); sr = w.getframerate()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32767
        if w.getnchannels() > 1: a = a.reshape(-1, w.getnchannels()).mean(1)
    if sr != sr_out:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(sr, sr_out); a = resample_poly(a, sr_out // g, sr // g); sr = sr_out
    return a, sr


def align(a, ref, sr, max_shift=0.3):
    """Shift a so its energy envelope lines up with ref (± max_shift s). Returns (a, shift_s)."""
    hop = int(0.005 * sr)
    env = lambda x: np.sqrt(np.add.reduceat(x[:len(x) // hop * hop] ** 2, np.arange(0, len(x) // hop * hop, hop)) + 1e-12)
    ea, er = np.log(env(a)), np.log(env(ref))
    n = min(len(ea), len(er)); ea, er = ea[:n] - ea[:n].mean(), er[:n] - er[:n].mean()
    m = int(max_shift / 0.005)
    best = max(range(-m, m + 1), key=lambda k: np.dot(ea[max(k, 0):n + min(k, 0)], er[max(-k, 0):n - max(k, 0)]))
    shift = best * hop
    a = np.r_[np.zeros(max(-shift, 0)), a[max(shift, 0):]][:len(ref)]
    return np.pad(a, (0, max(0, len(ref) - len(a)))), shift / sr


def yin(a, sr, hop=0.005, fmin=60, fmax=500, thr=0.20, win=0.03):
    """Vectorised YIN. Returns F0 (Hz, nan = unvoiced) per hop, and the hop in s."""
    W, tmax, tmin = int(sr * win), int(sr / fmin), int(sr / fmax)
    H = int(sr * hop)
    n = (len(a) - W - tmax) // H
    hop = H / sr                                      # the real hop (220 samples ≠ 5 ms at 44.1 kHz)
    if n <= 0: return np.array([]), hop
    idx = np.arange(n)[:, None] * H + np.arange(W + tmax)[None, :]
    fr = a[idx]
    energy = np.sqrt((fr[:, :W] ** 2).mean(1))
    nfft = 1 << int(np.ceil(np.log2(2 * (W + tmax))))
    F = np.fft.rfft(fr, nfft, axis=1)
    X0 = np.fft.rfft(fr[:, :W], nfft, axis=1)
    r = np.fft.irfft(F * np.conj(X0), nfft, axis=1)[:, :tmax]          # Σ x_j x_{j+τ}
    c = np.cumsum(fr ** 2, axis=1)
    e0 = c[:, W - 1][:, None]
    eT = c[:, W - 1 + np.arange(tmax)] - np.c_[np.zeros(n), c[:, :tmax - 1]]
    d = e0 + eT - 2 * r
    d[:, 0] = 0
    cm = d[:, 1:] * np.arange(1, tmax) / np.maximum(np.cumsum(d[:, 1:], axis=1), 1e-12)
    cm = np.c_[np.ones(n), cm]
    f0 = np.full(n, np.nan)
    gate = energy > 0.01 * (energy.max() + 1e-12)
    for i in np.where(gate)[0]:
        cand = np.where(cm[i, tmin:] < thr)[0]
        if len(cand) == 0: continue
        t = cand[0] + tmin
        while t + 1 < tmax and cm[i, t + 1] < cm[i, t]: t += 1
        f0[i] = sr / t
    return f0, hop


def band_share(a, sr, t0, t1, lo=2000, hi=8000):
    x = a[int(t0 * sr):int(t1 * sr)]
    if len(x) < 32: return float("nan")
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
    f = np.fft.rfftfreq(len(x), 1 / sr)
    return float(X[(f >= lo) & (f < hi)].sum() / (X[(f >= 50) & (f < hi)].sum() + 1e-12))


def accent_regression(pts):
    """Accent lift with the line slope taken out: least squares F0 = line offset + slope × (position in
    line, 0..1) + lift × accented, over every voiced nucleus. A plain accented-minus-unaccented mean is
    biased on short clips, where the unaccented nuclei may all sit early (high) or late (low) in a line."""
    if not pts or all(p[3] for p in pts) or not any(p[3] for p in pts): return float("nan")
    lines = sorted({p[0] for p in pts})
    span = {L: (min(p[1] for p in pts if p[0] == L), max(p[1] for p in pts if p[0] == L)) for L in lines}
    X, y = [], []
    for L, t, f, acc in pts:
        t0, t1 = span[L]
        X.append([1.0 if L == M else 0.0 for M in lines] + [(t - t0) / max(t1 - t0, 1e-6), float(acc)])
        y.append(f)
    coef = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)[0]
    return float(coef[-1])


def decays(a, sr, timing, lag=0.0):
    """vtl_ends.py's measure: ms for the word's last nucleus to fall from 10 to 30 dB under its peak
    (10 ms RMS frames, 2.5 ms hop), for every word followed by ≥ 0.2 s. Returns
    [{word, gap_ms, kind (line|caesura), voiced_end (bool), decay_ms}]."""
    W = timing["words"]; H = int(0.0025 * sr); F = int(0.010 * sr)
    x = np.pad(a, (F // 2, F // 2))
    n = (len(x) - F) // H
    idx = np.arange(n)[:, None] * H + np.arange(F)[None, :]
    e = 20 * np.log10(np.sqrt((x[idx] ** 2).mean(1)) + 1e-6)
    f = lambda t: int((t - lag) * sr / H)
    out = []
    for i, w in enumerate(W):
        nxt = W[i + 1]["start"] if i + 1 < len(W) else w["end"] + 1
        gap = nxt - w["end"]
        nucs = [p for p in w["phones"] if p["kind"] in NUCLEI]
        if gap < 0.2 or not nucs: continue
        v = nucs[-1]
        peak = e[f(v["start"]):f(v["end"])].max()
        seg = e[f(v["start"]):f(min(nxt, w["end"] + 0.4))]
        after = seg[np.argmax(seg):]
        t10, t30 = np.argmax(after < peak - 10), np.argmax(after < peak - 30)
        last = w["phones"][-1]
        voiced_end = last["kind"] in NUCLEI or last["kind"] in ("G", "N", "L", "R") or last["phone"] == "h"
        out.append({"word": w["word"], "gap_ms": round(gap * 1000), "kind": "line" if gap >= 0.5 else "caesura",
                    "voiced_end": bool(voiced_end),
                    "decay_ms": round((t30 - t10) * H / sr * 1000) if t30 > 0 else None})
    return out


def f0_ends(a, sr, timing, f0=None, hop=None):
    """F0 over every phrase end (pause ≥ 0.2 s): from the word's last nucleus to word end + 120 ms.
    span = 90th − 3rd percentile (st); floor = 3rd percentile re the nucleus's own F0 (median of its middle 40%)."""
    if f0 is None: f0, hop = yin(a, sr)
    st = 12 * np.log2(f0); fr = lambda t: max(int(round((t - 0.015) / hop)), 0)
    W = timing["words"]; out = []
    for i, w in enumerate(W):
        nxt = W[i + 1]["start"] if i + 1 < len(W) else w["end"] + 1
        nucs = [p for p in w["phones"] if p["kind"] in NUCLEI]
        if nxt - w["end"] < 0.2 or not nucs: continue
        v = nucs[-1]; d = v["end"] - v["start"]
        seg = st[fr(v["start"]):fr(min(w["end"] + 0.12, nxt))]; seg = seg[~np.isnan(seg)]
        ref = st[fr(v["start"] + 0.3 * d):fr(v["end"] - 0.3 * d)]; ref = ref[~np.isnan(ref)]
        if len(seg) < 3 or len(ref) < 1: continue
        hi, lo, r = np.percentile(seg, 90), np.percentile(seg, 3), np.median(ref)
        out.append({"word": w["word"], "kind": "line" if nxt - w["end"] >= 0.5 else "caesura",
                    "span_st": round(float(hi - lo), 2), "floor_st": round(float(lo - r), 2)})
    return out


def check(a, sr, timing, min_lift=2.5, min_voiced=0.97, chi=(0.30, 0.80), h=(0.25, 0.60),
          max_drop=8.0, max_drop_nasal=12.0, min_voiced_ms=40.0, final_h="noise",
          phrase_end=True, min_decay_line=120.0, min_decay_caesura=80.0,
          max_span_caesura=1.0, max_span_line=3.0, min_floor=-3.9):
    f0, hop = yin(a, sr)
    st = 12 * np.log2(f0)
    c = 0.015                                         # YIN frame i is centred at i*hop + 15 ms
    fr = lambda t: max(int(round((t - c) / hop)), 0)
    # voicing duration: a shorter analysis span (20 ms + 1 period at 70 Hz = 34 ms instead of 47),
    # so a vowel between voiceless sounds isn't under-read by half a long window at each edge
    fv, _ = yin(a, sr, fmin=70, win=0.02)
    frv = lambda t: max(int(round((t - 0.010) / hop)), 0)
    acc, un, unvoiced, n_nuc = [], [], [], 0
    chis, hs, vowels, h_lv, pts, tails = [], [], [], [], [], []
    for w in timing["words"]:
        for p in w["phones"]:
            if p["kind"] in NUCLEI:
                n_nuc += 1
                seg = st[fr(p["start"]):fr(p["end"])]
                ms = float(np.sum(~np.isnan(fv[frv(p["start"]):frv(p["end"])])) * hop * 1000)
                d = p["end"] - p["start"]
                x = a[int((p["start"] + 0.2 * d) * sr):int((p["end"] - 0.2 * d) * sr)]
                vowels.append({"id": f'{w["word"]}:{p["phone"]}@{p["start"]:.2f}', "kind": p["kind"],
                               "dur_ms": round(d * 1000), "voiced_ms": round(ms),
                               "level_db": round(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9), 1)})
                seg = seg[~np.isnan(seg)]
                if len(seg) < 3:
                    unvoiced.append(f'{w["word"]}:{p["phone"]}@{p["start"]:.2f}')
                    continue
                (acc if p["accent"] else un).append(float(np.median(seg)))
                pts.append((w.get("line", 1), (p["start"] + p["end"]) / 2, float(np.median(seg)), p["accent"]))
            m = (p["start"] + p["end"]) / 2
            if p["phone"] == "χ": chis.append(band_share(a, sr, m - 0.02, m + 0.02))
            k_ = w["phones"].index(p)
            fin = (p["phone"] == "h" and k_ == len(w["phones"]) - 1 and k_ > 0
                   and w["phones"][k_ - 1]["kind"] in NUCLEI)
            if p["phone"] == "h" and fin and final_h == "murmur":     # breathy vowel tail: voicing + level
                seg = fv[frv(p["start"]):frv(p["end"])]
                x = a[int(p["start"] * sr):int(p["end"] * sr)]
                tails.append({"id": f'{w["word"]}:h@{p["start"]:.2f}', "dur_ms": round((p["end"] - p["start"]) * 1000),
                              "voiced_ms": round(float(np.sum(~np.isnan(seg)) * hop * 1000)),
                              "share": round(band_share(a, sr, p["start"], p["end"]), 2),
                              "level_db": 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)})
            elif p["phone"] == "h":
                hs.append(band_share(a, sr, m - 0.02, m + 0.02))
                x = a[int((m - 0.02) * sr):int((m + 0.02) * sr)]
                h_lv.append(20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9))
    raw = (np.mean(acc) - np.mean(un)) if acc and un else float("nan")
    lift = accent_regression(pts)
    voiced = 1 - len(unvoiced) / max(n_nuc, 1)
    med = float(np.median([v["level_db"] for v in vowels if v["kind"] == "V"])) if vowels else 0.0
    weak, short_voice = [], []
    for v in vowels:
        v["re_median_db"] = round(v["level_db"] - med, 1)
        lim = max_drop_nasal if v["kind"] == "Ns" else max_drop
        if v["re_median_db"] < -lim: weak.append(f'{v["id"]} {v["re_median_db"]:+.1f} dB')
        need = min(min_voiced_ms, 0.7 * v["dur_ms"])
        if v["voiced_ms"] < need: short_voice.append(f'{v["id"]} {v["voiced_ms"]}/{v["dur_ms"]} ms')
    res = {"accent_lift_st": round(float(lift), 2), "accent_lift_raw_st": round(float(raw), 2),
           "voiced_share": round(voiced, 3),
           "unvoiced": unvoiced, "weak_vowels": weak, "short_voicing": short_voice,
           "chi_share": [round(x, 2) for x in chis], "h_share": [round(x, 2) for x in hs],
           "h_level_db": [round(float(x - med), 1) for x in h_lv]}       # re the median vowel
    for t_ in tails: t_["level_db"] = round(float(t_["level_db"] - med), 1)
    if final_h == "murmur": res["final_h"] = tails
    fails = []
    if weak: fails.append(f"{len(weak)} nuclei > {max_drop:g} dB below the median vowel")
    if short_voice: fails.append(f"{len(short_voice)} nuclei with < {min_voiced_ms:g} ms voicing")
    if not (lift >= min_lift): fails.append(f"accent lift {lift:.2f} < {min_lift}")
    if voiced < min_voiced: fails.append(f"voiced {voiced:.3f} < {min_voiced}")
    bad_chi = [x for x in chis if not (chi[0] <= x <= chi[1])]
    med_h = float(np.median(hs)) if hs else None             # h varies with its vowel: gate the median
    bad_h = [] if med_h is None or h[0] <= med_h <= h[1] else [round(med_h, 2)]
    if bad_chi: fails.append(f"χ share out of {chi}: {bad_chi}")
    if bad_h: fails.append(f"h median share out of {h}: {bad_h}")
    pe = decays(a, sr, timing)
    fe = {x["word"]: x for x in f0_ends(a, sr, timing, f0, hop)}
    for d in pe:
        if d["word"] in fe: d.update(span_st=fe[d["word"]]["span_st"], floor_st=fe[d["word"]]["floor_st"])
    res["phrase_ends"] = pe
    if phrase_end:
        short_pe = [f'{d["word"]} {d["decay_ms"]} ms' for d in pe if d["voiced_end"] and d["decay_ms"] is not None
                    and d["decay_ms"] < (min_decay_line if d["kind"] == "line" else min_decay_caesura)]
        if short_pe: fails.append(f"phrase ends cut short: {short_pe}")
        dive = [f'{d["word"]} span {d["span_st"]} floor {d["floor_st"]}' for d in pe if d["voiced_end"] and "span_st" in d
                and (d["span_st"] > (max_span_line if d["kind"] == "line" else max_span_caesura) or d["floor_st"] < min_floor)]
        if dive: fails.append(f"phrase-end F0 moves too much: {dive}")
    res["pass"], res["fails"] = not fails, fails
    res["vowels"] = vowels
    return res


def check_manifest(manifest, other_dir, out_path, **kw):
    """QC a folder of processed clips (e.g. ElevenLabs output named like the VTL wavs: CLIP__SPEAKER.wav)
    against the VTL batch manifest. Each clip is aligned to its VTL render, then checked on its timing.
    Writes one JSON line per clip to out_path; returns (n_checked, n_pass)."""
    import os
    base = os.path.dirname(os.path.abspath(manifest))
    n = n_pass = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for line in open(manifest, encoding="utf-8"):
            rec = json.loads(line)
            vtl_wav = rec["wav"] if os.path.isabs(rec["wav"]) else os.path.join(base, os.path.basename(rec["wav"]))
            tim = rec["timing"] if os.path.isabs(rec["timing"]) else os.path.join(base, os.path.basename(rec["timing"]))
            cand = os.path.join(other_dir, os.path.basename(vtl_wav))
            if not os.path.exists(cand):
                continue
            a, sr = load_wav(cand); r, _ = load_wav(vtl_wav); a, shift = align(a, r, sr)
            q = check(a, sr, json.load(open(tim, encoding="utf-8")), **kw); q.pop("vowels")
            q["aligned_shift_s"] = round(shift, 3)
            out.write(json.dumps({"clip": rec["clip"], "speaker": rec["speaker"], "wav": cand, "qc": q},
                                 ensure_ascii=False) + "\n")
            n += 1; n_pass += q["pass"]
            print(f'{rec["clip"]}__{rec["speaker"]}: ' + ("pass" if q["pass"] else f'FAIL {q["fails"]}'))
    return n, n_pass


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip", nargs="?", help="PREFIX (PREFIX.wav + PREFIX.json) or a .wav with --timing")
    ap.add_argument("--timing", help="phone-timing .json from pie_vtl.py")
    ap.add_argument("--ref", help="VTL render to align the wav to first (for ElevenLabs output)")
    ap.add_argument("--manifest", help="batch: VTL manifest.jsonl; checks every matching wav in --dir")
    ap.add_argument("--dir", help="batch: folder of processed wavs named like the VTL renders")
    ap.add_argument("--out", default="manifest_qc.jsonl", help="batch: output manifest")
    ap.add_argument("--vowels", action="store_true", help="print the per-nucleus table")
    ap.add_argument("--min-lift", type=float, default=2.5)
    ap.add_argument("--min-voiced-ms", type=float, default=40.0)
    ap.add_argument("--max-drop", type=float, default=8.0)
    ap.add_argument("--phrase-end", action=argparse.BooleanOptionalAction, default=True,
                    help="gate phrase-end decay: ≥ 120 ms at line ends, ≥ 80 ms at caesuras (vowel/sonorant endings)")
    ap.add_argument("--final-h", choices=("noise", "murmur"), default="noise",
                    help="murmur: word-final H is a breathy vowel tail; report it, keep it out of the h gate")
    o = ap.parse_args()
    kw = dict(min_lift=o.min_lift, min_voiced_ms=o.min_voiced_ms, max_drop=o.max_drop, final_h=o.final_h,
              phrase_end=o.phrase_end)
    if o.manifest:
        n, k = check_manifest(o.manifest, o.dir, o.out, **kw)
        print(f"{n} clips checked, {k} passed → {o.out}")
        sys.exit(0)
    wav = o.clip if o.clip.endswith(".wav") else o.clip + ".wav"
    tim = o.timing or (o.clip[:-4] if o.clip.endswith(".wav") else o.clip) + ".json"
    a, sr = load_wav(wav)
    shift = None
    if o.ref:
        r, _ = load_wav(o.ref); a, shift = align(a, r, sr)
    r = check(a, sr, json.load(open(tim, encoding="utf-8")), **kw)
    if shift is not None: r["aligned_shift_s"] = round(shift, 3)
    table = r.pop("vowels")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    if o.vowels:
        for v in table:
            print(f'  {v["id"]:24s} {v["kind"]:3s} {v["dur_ms"]:4d} ms  voiced {v["voiced_ms"]:4d} ms  '
                  f'{v["re_median_db"]:+6.1f} dB')
