"""gʷerh (PIE *gʷerh₃- 'to swallow', the root of words for the throat, e.g. Old Church Slavonic grъlo): our own
vocoder, trained from scratch on the paid voices. audio.py log-mel (100 bands, 100 frames/s) -> 44.1 kHz waveform.
Generator and discriminators are BigVGAN's (NVIDIA, MIT licence; imported from a clone, unedited), configured here:
base-size generator (snake-beta, anti-aliased), upsampling 7 x 7 x 3 x 3 = 441 samples per frame."""
import os, sys
import torch

BIGVGAN = os.path.expanduser(os.environ.get('BIGVGAN', '~/AI/chimera-pie-data/wokws/BigVGAN'))
if BIGVGAN not in sys.path: sys.path.insert(0, BIGVGAN)

H = dict(
    resblock='1', num_mels=100, upsample_rates=[7, 7, 3, 3], upsample_kernel_sizes=[15, 15, 7, 7],
    upsample_initial_channel=512, resblock_kernel_sizes=[3, 7, 11], resblock_dilation_sizes=[[1, 3, 5]] * 3,
    activation='snakebeta', snake_logscale=True, use_tanh_at_final=False, use_bias_at_final=False,
    # discriminators (BigVGAN-v2 recipe: multi-period + multi-scale sub-band CQT) and loss
    mpd_reshapes=[2, 3, 5, 7, 11], use_spectral_norm=False, discriminator_channel_mult=1,
    cqtd_filters=128, cqtd_max_filters=1024, cqtd_filters_scale=1, cqtd_dilations=[1, 2, 4],
    cqtd_hop_lengths=[512, 256, 256], cqtd_n_octaves=[9, 9, 9], cqtd_bins_per_octaves=[24, 36, 48],
    sampling_rate=44100, lambda_melloss=15)


def attrdict(h=None):
    from env import AttrDict
    return AttrDict(dict(H if h is None else h))


def build(h=None):
    from bigvgan import BigVGAN
    return BigVGAN(attrdict(h), use_cuda_kernel=False)


def load_for_inference(path):
    ck = torch.load(path, map_location='cpu', weights_only=False)
    g = build(ck.get('h')); g.load_state_dict(ck['generator']); g.remove_weight_norm(); g.eval()
    return (lambda mel: g(mel.transpose(1, 2))[0, 0]), H['sampling_rate'], g
