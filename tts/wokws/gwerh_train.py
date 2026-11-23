"""Train gʷerh (gwerh.py) from scratch on the paid clips: audio.py log-mel -> 44.1 kHz.
BigVGAN-v2 recipe: multi-period + multi-scale sub-band CQT discriminators, multi-scale mel loss x15, feature matching,
AdamW(0.8, 0.99) lr 1e-4; plus PhaseAug on the discriminator inputs, random peak level (-6..-1 dBFS, mel shifted to
match), generator EMA (exported), grad clip 100 for the first --clip_low_steps then 500.
Apple GPUs: torch >= 2.13 (<= 2.12 corrupts memory on MPS) and mps_fixes (same maths; 10.4 -> 3.4 s per batch-4 step on an M3 Ultra).
Operational: STOP file -> last.pt + exit; --resume; VRAM cap; whole-card memory logged; held-out error every
--val_every = L1 between audio.mel of the EMA output (resampled to 32 kHz) and the clip's own mel.
  gwerh_train.py --name NAME [--steps 1000000] [--batch 8] [--frames 128]"""
import argparse, collections, copy, itertools, json, math, os, random, sys, time
import torch, torchaudio
from torch import nn

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import audio as A, gwerh as G
from discriminators import MultiPeriodDiscriminator, MultiScaleSubbandCQTDiscriminator
from loss import feature_loss, generator_loss, discriminator_loss, MultiScaleMelSpectrogramLoss
from phaseaug.phaseaug import PhaseAug
import mps_fixes

ap = argparse.ArgumentParser()
ap.add_argument('--name', required=True); ap.add_argument('--data', default=os.path.expanduser('~/AI/chimera-pie-data/wokws/data'))
ap.add_argument('--runs', default=None); ap.add_argument('--steps', type=int, default=1000000)
ap.add_argument('--batch', type=int, default=8); ap.add_argument('--frames', type=int, default=128)
ap.add_argument('--lr', type=float, default=1e-4); ap.add_argument('--lr_half_life', type=float, default=500000)
ap.add_argument('--ema', type=float, default=0.999); ap.add_argument('--clip_low_steps', type=int, default=20000)
ap.add_argument('--phaseaug', type=int, default=1); ap.add_argument('--level_aug', type=int, default=1)
ap.add_argument('--val_every', type=int, default=2000); ap.add_argument('--save_every', type=int, default=10000)
ap.add_argument('--log_every', type=int, default=50); ap.add_argument('--max_steps', type=int, default=0)
ap.add_argument('--pred_mel', default='', help='name under DATA/predmel/: converter outputs used as generator input with --pred_prob')
ap.add_argument('--pred_prob', type=float, default=0.5)
ap.add_argument('--pred_blur_f', type=float, default=0.0, help='converter-mel inputs: 3-tap blur along frequency, strength ~ U(0, this) per sample')
ap.add_argument('--pred_blur_t', type=float, default=0.0, help='same along time (held-out converter output ~ 0.012 / 0.010 softer than on training clips)')
ap.add_argument('--voice_weight', default='', help='sampling weight per voice, e.g. W02=2,VALERIA=1.5 (others 1): oversample voices gʷerh renders worst')
ap.add_argument('--val_per_voice', type=int, default=0, help='held-out set: the first N val clips of each voice, scored per voice and per male/female group (0: the first 24 val clips, which are all one voice)')
ap.add_argument('--bf16', type=int, default=0, help='1: bfloat16 autocast for the generator and discriminator forwards (CUDA); losses in float32')
ap.add_argument('--gen_checkpoint', type=int, default=-1, help='1: activation checkpointing on the generator resblocks (default: on for CUDA)')
ap.add_argument('--resume', action='store_true'); ap.add_argument('--mem_frac', type=float, default=0.7)
ap.add_argument('--dev', default='cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu'))
ap.add_argument('--seed', type=int, default=20261115)
a = ap.parse_args()
dev = torch.device(a.dev); torch.manual_seed(a.seed); rng = random.Random(a.seed)
if dev.type == 'mps':
    # torch <= 2.12 on MPS overwrites unrelated memory in the generator backward (verified 2026-11-15: 2.8, 2.11, 2.12;
    # NaN by step 2); 2.13 and 2.15 are clean. Refuse the broken versions rather than train on corrupted optimizer state.
    assert tuple(int(v) for v in torch.__version__.split('+')[0].split('.')[:2]) >= (2, 13), 'MPS needs torch >= 2.13 (memory corruption in <= 2.12)'
    mps_fixes.apply()                                         # contiguous gradients into nnAudio's CQT convs (~100x faster backward)
if dev.type == 'cuda':
    torch.cuda.set_per_process_memory_fraction(a.mem_frac)
    torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True; torch.backends.cudnn.benchmark = True
RUN = f"{a.runs or os.path.join(os.path.dirname(a.data), 'runs')}/{a.name}"; os.makedirs(RUN, exist_ok=True)
logf = open(f'{RUN}/train.log', 'a')
def say(*x):
    s = ' '.join(str(v) for v in x); print(s, flush=True); logf.write(s + '\n'); logf.flush()
def mem():
    if dev.type != 'cuda': return '-'
    free, total = torch.cuda.mem_get_info()
    return f'{torch.cuda.max_memory_allocated() / 2**30:.1f}G card {(total - free) / 2**30:.1f}G'

# ---------------- data: every paid clip (a vocoder needs no pronunciation screen); val split held out
pairs = json.load(open(f'{a.data}/pairs.json'))
def load(r):
    m = torch.load(f"{a.data}/feats/{r['voice']}/{r['stem']}.pt", weights_only=True)['paid_mel']
    w = torch.load(f"{a.data}/wave44/{r['voice']}/{r['stem']}.pt", weights_only=True)
    assert w.numel() == m.shape[0] * A.OUT_HOP
    if a.pred_mel:                      # converter output for the same frames (frame-aligned with paid_mel and the wave)
        p = torch.load(f"{a.data}/predmel/{a.pred_mel}/{r['voice']}/{r['stem']}.pt", weights_only=True)
        assert p.shape == m.shape
        return m, w, p
    return m, w
ok = lambda r: all(os.path.exists(f"{a.data}/{k}/{r['voice']}/{r['stem']}.pt") for k in ('feats', 'wave44') + ((f'predmel/{a.pred_mel}',) if a.pred_mel else ()))
t0 = time.time()
TROWS = [r for r in pairs if r['split'] == 'train' and ok(r)]
TRAIN = [load(r) for r in TROWS]
if a.val_per_voice:          # balanced: the first 24 val pairs are all one voice (ZAZY), which hid per-voice effects
    VROWS = [r for v in sorted({r['voice'] for r in pairs}) for r in [r for r in pairs if r['split'] == 'val' and r['voice'] == v and ok(r)][:a.val_per_voice]]
else:
    VROWS = [r for r in pairs if r['split'] == 'val' and ok(r)][:24]
VAL = [load(r) for r in VROWS]; VVOICE = [r['voice'] for r in VROWS]
FEMALE = {'VALERIA', 'W02'}
keep = [i for i, x in enumerate(TRAIN) if x[0].shape[0] >= a.frames]
TRAIN = [TRAIN[i] for i in keep]; TVOICE = [TROWS[i]['voice'] for i in keep]
VW = {k: float(v) for k, v in (kv.split('=') for kv in a.voice_weight.split(',') if kv)}
CUMW = list(itertools.accumulate(VW.get(v, 1.0) for v in TVOICE)) if VW else None   # clip sampling weights (None: uniform)
if VW: say('voice sampling weights', VW, 'share per voice', {v: round(sum(VW.get(u, 1.0) for u in TVOICE if u == v) / CUMW[-1], 3) for v in sorted(set(TVOICE))})
if a.pred_mel: say(f'generator input: converter mels ({a.pred_mel}) with p={a.pred_prob} (blur f<={a.pred_blur_f} t<={a.pred_blur_t}), paid mels otherwise; target = paid audio')
say(f'data: {len(TRAIN)} train clips ({sum(x[0].shape[0] for x in TRAIN) / 360000:.1f} h), {len(VAL)} val {dict(collections.Counter(VVOICE))}, loaded in {time.time() - t0:.0f}s')
LOG_FLOOR = math.log(1e-5)

def batch():
    mels, waves = [], []
    for _ in range(a.batch):
        it = TRAIN[rng.choices(range(len(TRAIN)), cum_weights=CUMW)[0] if CUMW else rng.randrange(len(TRAIN))]; m, w = it[0], it[1]
        pred = bool(a.pred_mel) and rng.random() < a.pred_prob
        if pred: m = it[2]      # generator input = converter output, target = paid audio
        s = rng.randrange(m.shape[0] - a.frames + 1)
        mm = m[s:s + a.frames].float()
        if pred and (a.pred_blur_f > 0 or a.pred_blur_t > 0):   # converter mels of training clips are sharper than the
            mm = G.blur3(mm, rng.uniform(0, a.pred_blur_f), rng.uniform(0, a.pred_blur_t))   # converter's unseen-line output
        ww = w[s * A.OUT_HOP:(s + a.frames) * A.OUT_HOP].float() / 32767
        if a.level_aug:
            pk = float(ww.abs().max())
            if pk > 1e-4:
                g = 10 ** (rng.uniform(-6, -1) / 20) / pk; ww = ww * g; mm = (mm + math.log(g)).clamp_min(LOG_FLOOR)
        mels.append(mm); waves.append(ww)
    return torch.stack(mels).transpose(1, 2).to(dev), torch.stack(waves)[:, None].to(dev)

# ---------------- model
h = G.attrdict()
gen = G.build().to(dev); ema = G.build().to(dev); ema.load_state_dict(gen.state_dict()); ema.eval().requires_grad_(False)   # (weight_norm modules can't be deep-copied)
mpd, cqtd = MultiPeriodDiscriminator(h).to(dev), MultiScaleSubbandCQTDiscriminator(h).to(dev)
if a.gen_checkpoint == 1 or (a.gen_checkpoint == -1 and dev.type == 'cuda'): say('generator resblock checkpointing on', G.checkpoint_resblocks(gen))
class MelLoss(MultiScaleMelSpectrogramLoss):
    """BigVGAN's multi-scale mel loss with the window / filter tensors made float32 on the host first (MPS has no
    float64) and cached per device; the computation is otherwise the same."""
    _cache = {}
    def mel_spectrogram(self, wav, n_mels, fmin, fmax, window_length, hop_length, match_stride, window_type):
        B, C, T = wav.shape
        right_pad = math.ceil(T / hop_length) * hop_length - T if match_stride else 0
        pad = (window_length - hop_length) // 2 if match_stride else 0
        wav = torch.nn.functional.pad(wav, (pad, pad + right_pad), mode='reflect')
        key = (window_type, window_length, n_mels, fmin, fmax, wav.device)
        if key not in self._cache:
            win = torch.from_numpy(self.get_window(window_type, window_length).astype('float32')).to(wav.device)
            mb = torch.from_numpy(self.get_mel_filters(self.sampling_rate, window_length, n_mels, fmin, fmax).astype('float32')).to(wav.device)
            self._cache[key] = (win, mb)
        win, mb = self._cache[key]
        stft = torch.stft(wav.reshape(-1, wav.shape[-1]), n_fft=window_length, hop_length=hop_length, window=win, return_complex=True, center=True)
        _, nf, nt = stft.shape; stft = stft.reshape(B, C, nf, nt)
        if match_stride: stft = stft[..., 2:-2]
        return (stft.abs().transpose(2, -1) @ mb.T).transpose(-1, 2)
mel_loss = MelLoss(sampling_rate=A.OUT_SR).to(dev)
aug = PhaseAug().to(dev) if a.phaseaug else None
say('params gen', sum(p.numel() for p in gen.parameters()), 'mpd', sum(p.numel() for p in mpd.parameters()), 'cqtd', sum(p.numel() for p in cqtd.parameters()))
og = torch.optim.AdamW(gen.parameters(), a.lr, betas=(0.8, 0.99))
dparams = list(mpd.parameters()) + list(cqtd.parameters())
od = torch.optim.AdamW(dparams, a.lr, betas=(0.8, 0.99))
to32 = torchaudio.transforms.Resample(A.OUT_SR, A.SR).to(dev)

@torch.no_grad()
def validate(pred=False, groups=None):
    """Mean held-out mel L1 over VAL; with groups (a dict) also filled per voice and per male/female group."""
    errs = []
    for it in VAL:
        m = it[0]; inp = it[2] if pred else m
        y = ema(inp.float().T[None].to(dev))[0, 0]
        mm = A.mel(to32(y)[None])[0]; n = min(mm.shape[0], m.shape[0])
        errs.append(float((mm[:n] - m[:n].float().to(dev)).abs().mean()))
    if groups is not None:
        for key, sel in [(v, [v]) for v in sorted(set(VVOICE))] + [('male', sorted(set(VVOICE) - FEMALE)), ('female', sorted(set(VVOICE) & FEMALE))]:
            e = [x for x, v in zip(errs, VVOICE) if v in sel]
            if e: groups[key] = round(sum(e) / len(e), 4)
    return round(sum(errs) / len(errs), 4)

def save_last(step):
    torch.save({'gen': gen.state_dict(), 'ema': ema.state_dict(), 'mpd': mpd.state_dict(), 'cqtd': cqtd.state_dict(),
                'og': og.state_dict(), 'od': od.state_dict(), 'step': step, 'args': vars(a), 'rng': rng.getstate()}, f'{RUN}/last.pt.tmp')
    os.replace(f'{RUN}/last.pt.tmp', f'{RUN}/last.pt')

def export(step):
    torch.save({'h': dict(h), 'step': step, 'generator': {k: v.detach().cpu() for k, v in ema.state_dict().items()}}, f'{RUN}/step{step}.pt')

step = 0
if a.resume and os.path.exists(f'{RUN}/last.pt'):
    ck = torch.load(f'{RUN}/last.pt', map_location='cpu', weights_only=False)
    gen.load_state_dict(ck['gen']); ema.load_state_dict(ck['ema']); mpd.load_state_dict(ck['mpd']); cqtd.load_state_dict(ck['cqtd'])
    og.load_state_dict(ck['og']); od.load_state_dict(ck['od']); step = ck['step']; rng.setstate(ck['rng']); say('resumed at', step)
else:
    say('args', json.dumps(vars(a))); w0 = {k: v.detach().clone() for k, v in gen.state_dict().items()}

assert not a.bf16 or dev.type == 'cuda', '--bf16 is for CUDA'
if a.bf16: say('bf16 autocast on (generator + discriminator forwards; losses float32)')
ac = lambda: torch.autocast('cuda', dtype=torch.bfloat16, enabled=bool(a.bf16))
f32 = lambda o: [f32(x) for x in o] if isinstance(o, (list, tuple)) else (o.float() if torch.is_tensor(o) else o)
t_start, s_start = time.time(), step; stopped = False
while step < a.steps:
    if os.path.exists(f'{RUN}/STOP'):
        save_last(step); say('STOP at', step); os.remove(f'{RUN}/STOP'); stopped = True; break
    if a.max_steps and step - s_start >= a.max_steps:
        save_last(step); say('max_steps reached', step); stopped = True; break
    lr = a.lr * 0.5 ** (step / a.lr_half_life)
    for o in (og, od):
        for g_ in o.param_groups: g_['lr'] = lr
    clip = 100.0 if step < a.clip_low_steps else 500.0
    x, y = batch()
    with ac(): y_hat = gen(x)
    y_hat = y_hat.float()
    yd, yhd = (aug.forward_sync(y, y_hat.detach()) if aug is not None else (y, y_hat.detach()))
    od.zero_grad(set_to_none=True)
    with ac(): rf, gf, _, _ = f32(mpd(yd, yhd)); rc, gc, _, _ = f32(cqtd(yd, yhd))
    ld = discriminator_loss(rf, gf)[0] + discriminator_loss(rc, gc)[0]
    ld.backward(); gnd = nn.utils.clip_grad_norm_(list(mpd.parameters()) + list(cqtd.parameters()), clip); od.step()
    og.zero_grad(set_to_none=True)
    for p_ in dparams: p_.requires_grad_(False)   # generator pass: no discriminator weight gradients (they were computed and
                                                  # thrown away) and no activations kept for them; generator gradients identical
    lm = mel_loss(y, y_hat) * h.lambda_melloss
    yg, yhg = (aug.forward_sync(y, y_hat) if aug is not None else (y, y_hat))
    yg = yg.detach()            # forward_sync concatenates real and generated audio, so the real branch would otherwise carry
                                # a gradient and the discriminators would compute an unused input gradient for it
    with ac(): _, gf, fr, fg = f32(mpd(yg, yhg)); _, gc, cr, cg = f32(cqtd(yg, yhg))
    ladv = generator_loss(gf)[0] + generator_loss(gc)[0]; lfm = feature_loss(fr, fg) + feature_loss(cr, cg)
    lg = lm + ladv + lfm
    lg.backward()
    for p_ in dparams: p_.requires_grad_(True)
    gng = nn.utils.clip_grad_norm_(gen.parameters(), clip); og.step(); step += 1
    with torch.no_grad():
        dcy = min(a.ema, (1 + step) / (10 + step))
        for pe, pm in zip(ema.parameters(), gen.parameters()): pe.lerp_(pm, 1 - dcy)
        for be, bm in zip(ema.buffers(), gen.buffers()): be.copy_(bm)
    if step == 1 and not a.resume:
        ch = sum(float((v.float() - w0[k].to(v.device).float()).abs().max()) > 0 for k, v in gen.state_dict().items() if v.is_floating_point())
        say('weights changed after step 1 in', ch, 'of', sum(v.is_floating_point() for v in gen.state_dict().values()), 'tensors')
    if step % a.log_every == 0 or step <= 3:
        el = time.time() - t_start
        say(f'step {step} mel {float(lm) / h.lambda_melloss:.4f} adv {float(ladv):.3f} fm {float(lfm):.3f} d {float(ld):.3f} '
            f'gn {float(gng):.1f} gd {float(gnd):.1f} lr {lr:.2e} {el / max(1, step - s_start):.3f}s/step mem {mem()}')
    if step % a.val_every == 0:
        gp, gc = {}, {}
        say('val', step, 'ema mel_l1', validate(groups=gp), *(('pred_in', validate(True, groups=gc)) if a.pred_mel else ()))
        if a.val_per_voice: say('valgroups', step, 'paid_in', json.dumps(gp), *(('pred_in', json.dumps(gc)) if a.pred_mel else ()))
    if step % a.save_every == 0: export(step); save_last(step); say('saved', step)
say('TRAIN_END', step)
if stopped: sys.exit(3)            # paused, resumable: not DONE
