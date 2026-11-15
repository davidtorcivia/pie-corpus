"""Render held-out lines with a wokʷs checkpoint: Chimera features -> wokʷs log-mel -> vocoder -> wav.
  render.py NAME CKPT [--lines SPEC.json] [--vocoder v4|PATH_TO_GWERH.pt] [--pitch_st 0] [--tf] [--copy]
-> $WOKWS_EVAL/NAME/<VOICE>/<stem>.wav. --tf: decoder conditioned on the paid clip's own prosody. --copy: no converter,
the paid clip's own mel (the vocoder ceiling). v4 = the GPT-SoVITS v4 vocoder (stand-in, 48 kHz out)."""
import argparse, json, math, os, sys
import soundfile as sf, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wokws as W
from tiny_voca.config import Config
D = os.path.expanduser('~/AI/chimera-pie-data'); E = os.environ.get('WOKWS_EVAL', f'{D}/sts-eval')
ap = argparse.ArgumentParser(); ap.add_argument('name'); ap.add_argument('ckpt', nargs='?', default='')
ap.add_argument('--lines', required=True); ap.add_argument('--vocoder', default='v4'); ap.add_argument('--pitch_st', type=float, default=0.0)
ap.add_argument('--tf', action='store_true'); ap.add_argument('--copy', action='store_true')
ap.add_argument('--data', default=f'{D}/wokws/data'); ap.add_argument('--dev', default='cpu'); a = ap.parse_args()


def v4_vocoder():
    repo = os.environ.get('GSV_REPO', f'{D}/gsv-mac/GPT-SoVITS'); sys.path[:0] = [repo, f'{repo}/GPT_SoVITS']
    from module.models import Generator
    voc = Generator(initial_channel=100, resblock='1', resblock_kernel_sizes=[3, 7, 11], resblock_dilation_sizes=[[1, 3, 5]] * 3,
                    upsample_rates=[10, 6, 2, 2, 2], upsample_initial_channel=512, upsample_kernel_sizes=[20, 12, 4, 4, 4],
                    gin_channels=0, is_bias=True)
    voc.eval(); voc.remove_weight_norm()
    voc.load_state_dict(torch.load(f'{repo}/GPT_SoVITS/pretrained_models/gsv-v4-pretrained/vocoder.pth', map_location='cpu', weights_only=False))
    return (lambda m: voc(m.transpose(1, 2))[0, 0]), 48000, voc


if a.vocoder == 'v4':
    vocode, SR, vm = v4_vocoder()
else:
    import gwerh as G
    vocode, SR, vm = G.load_for_inference(a.vocoder)
vm.to(a.dev)
if not a.copy:
    ck = torch.load(a.ckpt, map_location='cpu', weights_only=False)
    c = Config.from_dict(ck['config']); voc = ck['vocab']
    m = W.Wokws(c, voc['n_tokens'], len(voc['kinds'])); m.load_state_dict(ck['model']); m = m.to(a.dev).eval()
for v, s, _ in json.load(open(a.lines))['lines']:
    d = torch.load(f'{a.data}/feats/{v}/{s}.pt', weights_only=True)
    with torch.inference_mode():
        if a.copy:
            mel = d['paid_mel'].float()[None].to(a.dev)
        else:
            b = W.collate([W.item(d, v)], a.dev)
            if a.tf:
                x, fm, _, _ = m.frames(b); h, _ = m.predict_prosody(x, fm)
                cond = b['prosody'].clone(); cond[..., 0] += a.pitch_st * math.log(2) / 12
                mel = m.decode(h, cond, fm)[1] * W.MEL_SCALE + W.MEL_MEAN
            else:
                mel = m.convert(b, pitch_shift=a.pitch_st * math.log(2) / 12)[0]
        y = vocode(mel.float()).float().cpu().numpy()
    y = y / max(1.0, abs(y).max())
    os.makedirs(f'{E}/{a.name}/{v}', exist_ok=True); sf.write(f'{E}/{a.name}/{v}/{s}.wav', y, SR)
print('DONE', a.name)
