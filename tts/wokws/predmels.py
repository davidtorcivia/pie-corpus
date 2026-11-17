"""Converter outputs for gʷerh fine-tuning: run a wokʷs checkpoint (free-running, as at inference) over every pair and save
its denormalized log-mel next to the prepared data, frame-aligned with paid_mel and wave44 (the converter emits exactly the
Chimera frame count, which is the paid clip's frame count after prep).
  predmels.py CKPT OUTNAME [--data DIR] [--dev cuda]   ->  DATA/predmel/OUTNAME/<VOICE>/<stem>.pt  (f16 [N,100])"""
import argparse, json, os, sys, time, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wokws as W
from tiny_voca.config import Config
ap = argparse.ArgumentParser(); ap.add_argument('ckpt'); ap.add_argument('outname')
ap.add_argument('--data', default=os.path.expanduser('~/AI/chimera-pie-data/wokws/data'))
ap.add_argument('--dev', default='cuda' if torch.cuda.is_available() else 'cpu'); a = ap.parse_args()
ck = torch.load(a.ckpt, map_location='cpu', weights_only=False); c = Config.from_dict(ck['config']); voc = ck['vocab']
m = W.Wokws(c, voc['n_tokens'], len(voc['kinds'])); m.load_state_dict(ck['model']); m = m.to(a.dev).eval()
pairs = json.load(open(f'{a.data}/pairs.json')); t0 = time.time(); n = bad = 0
for r in pairs:
    v, s = r['voice'], r['stem']; f = f'{a.data}/feats/{v}/{s}.pt'; out = f'{a.data}/predmel/{a.outname}/{v}/{s}.pt'
    if not os.path.exists(f) or os.path.exists(out): continue
    d = torch.load(f, weights_only=True)
    with torch.inference_mode(): mel = m.convert(W.collate([W.item(d, v)], a.dev))[0][0].float().cpu()
    if mel.shape != d['paid_mel'].shape: bad += 1; print('SHAPE', v, s, tuple(mel.shape), tuple(d['paid_mel'].shape)); continue
    os.makedirs(os.path.dirname(out), exist_ok=True); torch.save(mel.half(), out); n += 1
    if n % 500 == 0: print(n, f'{time.time() - t0:.0f}s', flush=True)
print('PREDMELS_DONE', n, 'written', bad, 'shape mismatches', f'{time.time() - t0:.0f}s')
