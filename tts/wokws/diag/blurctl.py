"""Smoothed-ceiling control: the paid clip's own mel, blurred along frequency (or time) on linear magnitude until its
fine-detail ratios match wokʷs step 25000, then the v4 stand-in vocoder.  blurctl.py SPEC --scan | --render NAME AXIS SIGMA"""
import sys, json, os, numpy as np, torch, soundfile as sf
from scipy.ndimage import gaussian_filter1d
D = os.path.expanduser('~/AI/chimera-pie-data'); E = f'{D}/sts-eval'; lines = json.load(open(sys.argv[1]))['lines']
B = [(0, 25), (25, 50), (50, 75), (75, 100)]
def blur(x, axis, s):  # x [T,100] natural-log magnitude mel; axis 'ft' = both
    if axis == 'ft': return blur(blur(x, 'f', s), 't', s)
    return np.log(np.maximum(gaussian_filter1d(np.exp(x), s, axis=1 if axis == 'f' else 0, mode='nearest'), 1e-5))
def dfdt(x):
    dF = [np.abs(2 * x[:, max(a,1):min(b,99)] - x[:, max(a,1)-1:min(b,99)-1] - x[:, max(a,1)+1:min(b,99)+1]).mean() for a, b in B]
    dT = [np.abs(np.diff(x[:, a:b], axis=0)).mean() for a, b in B]
    return np.array(dF), np.array(dT)
mels = [(v, s, torch.load(f'{D}/wokws/data/feats/{v}/{s}.pt', weights_only=True)['paid_mel'].float().numpy()) for v, s, _ in lines]
if sys.argv[2] == '--scan':
    ref = np.mean([np.concatenate(dfdt(m)) for _, _, m in mels], 0)
    for ax, ss in (('f', [0.5, 0.75, 1.0, 1.5, 2.0]), ('t', [0.5, 0.75, 1.0, 1.5])):
        for sg in ss:
            r = np.mean([np.concatenate(dfdt(blur(m, ax, sg))) for _, _, m in mels], 0) / ref
            print(ax, sg, 'dF', ' '.join(f'{v:.2f}' for v in r[:4]), '| dT', ' '.join(f'{v:.2f}' for v in r[4:]))
    sys.exit()
name, ax, sg = sys.argv[3], sys.argv[4], float(sys.argv[5])
repo = f'{D}/gsv-mac/GPT-SoVITS'; sys.path[:0] = [repo, f'{repo}/GPT_SoVITS']
from module.models import Generator
voc = Generator(initial_channel=100, resblock='1', resblock_kernel_sizes=[3, 7, 11], resblock_dilation_sizes=[[1, 3, 5]] * 3,
                upsample_rates=[10, 6, 2, 2, 2], upsample_initial_channel=512, upsample_kernel_sizes=[20, 12, 4, 4, 4], gin_channels=0, is_bias=True)
voc.eval(); voc.remove_weight_norm()
voc.load_state_dict(torch.load(f'{repo}/GPT_SoVITS/pretrained_models/gsv-v4-pretrained/vocoder.pth', map_location='cpu', weights_only=False))
for v, s, m in mels:
    with torch.inference_mode(): y = voc(torch.from_numpy(blur(m, ax, sg)).float()[None].transpose(1, 2))[0, 0].numpy()
    y = y / max(1.0, abs(y).max()); os.makedirs(f'{E}/{name}/{v}', exist_ok=True); sf.write(f'{E}/{name}/{v}/{s}.wav', y, 48000)
print('DONE', name)
