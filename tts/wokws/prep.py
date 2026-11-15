"""Training data for wokʷs (Chimera -> paid converter) and gʷerh (our vocoder), in the audio.py format.

Per (voice, stem) pair, N frames at 100 frames/s (N = ceil(len(Chimera render at 32 kHz) / 320)):
  feats/<V>/<stem>.pt   paid_mel f16 [N,100], chim_mel f16 [N,100]   (audio.mel; paid padded/trimmed to 320 N samples)
                        paid_pros, chim_pros f32 [N,3]              log(F0/200), voiced, log RMS (pyin 50-600 Hz, frame
                                                                    1280, centred on the mel frame centres)
                        tokens i16 [K], kinds i8 [K], dur i16 [K]    PIE phones + silence from Chimera's timing, sum(dur) = N
  wave44/<V>/<stem>.pt  int16 [441 N]   the paid clip at its native 44.1 kHz, padded/trimmed to match (gʷerh's target)
Paid is frame-aligned to Chimera (measured: envelope lag 0 ms), so no aligner is used.
  prep.py [--workers 28] [--limit N]    (run with OMP/VECLIB/OPENBLAS threads = 1)"""
import argparse, json, os, sys, math
from multiprocessing import Pool
import numpy as np, soundfile as sf, torch, librosa

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import audio as A
D = os.path.expanduser('~/AI/chimera-pie-data'); OUT = os.environ.get('WOKWS_DATA', f'{D}/wokws/data')
sys.path.insert(0, f'{D}/gsv-mac')
import pie_phones as PP
VOCAB = json.load(open(f'{D}/tv/data/vocab.json'))       # same token / kind inventory as tvc
TOK, KINDS = VOCAB['tokens'], VOCAB['kinds']


def load(path, sr):
    x, s = sf.read(path, dtype='float32', always_2d=True)
    x = x.mean(1)
    return librosa.resample(x, orig_sr=s, target_sr=sr) if s != sr else x


def fit(x, n):
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def prosody(w, n):
    """pyin + RMS on 32 kHz audio, frames centred at 320 i + 160 (the mel frame centres)."""
    w = np.pad(w, (A.HOP // 2, 0))
    f0, vf, _ = librosa.pyin(w, fmin=50, fmax=600, sr=A.SR, frame_length=A.N_FFT, hop_length=A.HOP, center=True, pad_mode='constant')
    f0, vf = f0[:n], vf[:n]
    pitch = np.where(vf, np.log(np.maximum(np.nan_to_num(f0, nan=200.0), 1) / 200.0), 0)
    rms = librosa.feature.rms(y=w, frame_length=A.N_FFT, hop_length=A.HOP, center=True, pad_mode='constant')[0, :n]
    p = np.stack((pitch, vf.astype(np.float32), np.log(np.maximum(rms, 1e-5))), -1).astype(np.float32)
    return torch.from_numpy(np.pad(p, ((0, n - len(p)), (0, 0)), mode='edge'))


def tokens_of(stem, n):
    words = json.load(open(f'{D}/full/timing/{stem}.json'))['words']
    seg, t = [], 0.0
    for w in words:
        for p in w['phones']:
            if p['start'] > t + 1e-4: seg.append((1, 0, t, p['start']))
            seg.append((TOK[PP.pie_key(p)], KINDS.index(p['kind']) if p['kind'] in KINDS else 1, p['start'], p['end']))
            t = p['end']
    seg.append((1, 0, t, max(t, n * A.HOP / A.SR)))
    bounds = [min(n, round(e * A.SR / A.HOP)) for _, _, _, e in seg]; bounds[-1] = n
    tok, kin, dur, prev = [], [], [], 0
    for (tk, kd, _, _), b in zip(seg, bounds):
        d = max(0, b - prev)
        if d == 0 and tk == 1: continue
        tok.append(tk); kin.append(kd); dur.append(d); prev += d
    if prev != n: dur[-1] += n - prev
    assert sum(dur) == n and min(dur) >= 0, (stem, sum(dur), n)
    return tok, kin, dur


def one(r):
    v, s = r['voice'], r['stem']
    of, ow = f'{OUT}/feats/{v}/{s}.pt', f'{OUT}/wave44/{v}/{s}.pt'
    if os.path.exists(of) and os.path.exists(ow): return s, 'skip'
    try:
        cw = np.clip(load(f'{D}/full/chimera-v2/renders/{s}.wav', A.SR), -1, 1)
        n = math.ceil(len(cw) / A.HOP); cw = fit(cw, n * A.HOP)
        src = f'{D}/full/restored-v2/{v}/{s}.wav'
        pw = np.clip(fit(load(src, A.SR), n * A.HOP), -1, 1)
        p44 = np.clip(fit(load(src, A.OUT_SR), n * A.OUT_HOP), -1, 1)
        with torch.no_grad():
            pm, cm = A.mel(torch.from_numpy(pw)), A.mel(torch.from_numpy(cw))
        assert pm.shape[0] == n == cm.shape[0], (pm.shape, n)
        tok, kin, dur = tokens_of(s, n)
        for o in (of, ow): os.makedirs(os.path.dirname(o), exist_ok=True)
        torch.save({'paid_mel': pm.half(), 'chim_mel': cm.half(), 'paid_pros': prosody(pw, n), 'chim_pros': prosody(cw, n),
                    'tokens': torch.tensor(tok, dtype=torch.int16), 'kinds': torch.tensor(kin, dtype=torch.int8),
                    'dur': torch.tensor(dur, dtype=torch.int16)}, of + '.tmp')
        os.replace(of + '.tmp', of)
        torch.save(torch.from_numpy((p44 * 32767).astype(np.int16)), ow + '.tmp'); os.replace(ow + '.tmp', ow)
        return s, 'ok'
    except Exception as e:
        return s, f'ERR {e!r}'


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=28); ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()
    pairs = json.load(open(f'{D}/tv/data/pairs.json'))
    if a.limit: pairs = pairs[:a.limit]
    os.makedirs(OUT, exist_ok=True)
    json.dump(VOCAB, open(f'{OUT}/vocab.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(pairs, open(f'{OUT}/pairs.json', 'w'))
    torch.set_num_threads(1)
    with Pool(a.workers) as pool:
        for i, (s, st) in enumerate(pool.imap_unordered(one, pairs, chunksize=4)):
            if st.startswith('ERR') or i % 500 == 0: print(i, len(pairs), s, st, flush=True)
    print('PREP_DONE')
