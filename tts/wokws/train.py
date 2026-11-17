"""Train wokʷs (wokws.py).
Phase A (default): mel L1 (pre- and post-net) + paid-prosody losses, teacher-forcing schedule, Chimera-feature span
masking, cosine LR to --lr_final_frac, EMA weights exported. Phase B (--init A/last.pt --gan_start 0): adds multi-
window 2D critics on the mel (not on any vocoder's audio, so the converter stays vocoder-agnostic), LSGAN + feature
matching, GAN gradient scaled to --gan_ratio x the reconstruction gradient at the predicted mel.

Operational: STOP file in the run dir saves last.pt and exits; --resume; VRAM cap (--mem_frac); whole-card memory
logged; conditioning check (Chimera features zeroed) at start and in validation; stepN.pt (EMA inference weights)
every --save_every.     train.py --name NAME [--steps 50000] [--batch_frames 27000] ..."""
import argparse, copy, json, math, os, queue, random, sys, threading, time
import torch
from torch import nn
from torch.nn import functional as F

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import wokws as W
from tiny_voca.losses import masked_mean
from tiny_voca.train import teacher_probability, masked_std
from tiny_voca.data import BucketSampler

ap = argparse.ArgumentParser()
ap.add_argument('--name', required=True); ap.add_argument('--data', default=os.path.expanduser('~/AI/chimera-pie-data/wokws/data'))
ap.add_argument('--runs', default=None); ap.add_argument('--steps', type=int, default=50000)
ap.add_argument('--batch_frames', type=int, default=27000); ap.add_argument('--max_batch', type=int, default=48)
ap.add_argument('--lr', type=float, default=3e-4); ap.add_argument('--warmup', type=int, default=1000)
ap.add_argument('--lr_final_frac', type=float, default=0.1); ap.add_argument('--grad_clip', type=float, default=1.0)
ap.add_argument('--ema', type=float, default=0.999)
ap.add_argument('--r_weight', type=float, default=1.0, help='weight of /r/ and syllabic /r̩/ frames in the mel losses')
ap.add_argument('--r_delta', type=float, default=0.0, help='weight of a frame-to-frame (tap contrast) mel loss on /r/ frames')
ap.add_argument('--dropout', type=float, default=-1, help='override every dropout probability in the model (encoder, decoder, postnet); -1 keeps the config')
ap.add_argument('--src_mask', type=float, default=0.15, help='fraction of frames whose Chimera features are zeroed (spans of 12)')
ap.add_argument('--teacher_hold', type=int, default=3000); ap.add_argument('--teacher_ramp', type=int, default=7000)
ap.add_argument('--teacher_final', type=float, default=0.0)
ap.add_argument('--screen', type=float, default=0.15)
ap.add_argument('--init', default=''); ap.add_argument('--gan_start', type=int, default=10**9)
ap.add_argument('--gan_ratio', type=float, default=0.5); ap.add_argument('--gan_ramp', type=int, default=2000)
ap.add_argument('--feature_matching', type=float, default=2.0); ap.add_argument('--crop_frames', default='32,64,128')
ap.add_argument('--val_every', type=int, default=1000); ap.add_argument('--save_every', type=int, default=5000)
ap.add_argument('--log_every', type=int, default=25); ap.add_argument('--max_steps', type=int, default=0)
ap.add_argument('--resume', action='store_true'); ap.add_argument('--mem_frac', type=float, default=0.7)
ap.add_argument('--dev', default='cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu'))
ap.add_argument('--amp', type=int, default=1, help='bf16 autocast on cuda'); ap.add_argument('--seed', type=int, default=20261115)
ap.add_argument('--prefetch', type=int, default=3)
a = ap.parse_args()

dev = torch.device(a.dev); torch.manual_seed(a.seed); random.seed(a.seed)
if dev.type == 'cuda':
    torch.cuda.set_per_process_memory_fraction(a.mem_frac)
    torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True
RUN = f"{a.runs or os.path.join(os.path.dirname(a.data), 'runs')}/{a.name}"; os.makedirs(RUN, exist_ok=True)
logf = open(f'{RUN}/train.log', 'a')
AMP = dict(device_type='cuda', dtype=torch.bfloat16, enabled=bool(a.amp) and dev.type == 'cuda')


def say(*x):
    s = ' '.join(str(v) for v in x); print(s, flush=True); logf.write(s + '\n'); logf.flush()


def mem():
    if dev.type != 'cuda': return '-'
    free, total = torch.cuda.mem_get_info()
    return f'{torch.cuda.max_memory_allocated() / 2**30:.1f}G card {(total - free) / 2**30:.1f}G'


# ---------------- data
c = W.config()
vocab = json.load(open(f'{a.data}/vocab.json')); pairs = json.load(open(f'{a.data}/pairs.json'))
screen = json.load(open(f'{a.data}/screen.json')) if os.path.exists(f'{a.data}/screen.json') else {}
exists = lambda r: os.path.exists(f"{a.data}/feats/{r['voice']}/{r['stem']}.pt")
train_rows = [r for r in pairs if r['split'] == 'train' and exists(r)]; val_rows = [r for r in pairs if r['split'] == 'val' and exists(r)]
if a.screen > 0:
    covered = sum(f"{r['voice']}|{r['stem']}" in screen for r in train_rows)
    if covered < len(train_rows): raise SystemExit(f'screen covers {covered}/{len(train_rows)} train pairs; refusing (use --screen 0)')
    drift = lambda r: (lambda s: (s['paid'] - s['chim']) / max(1, s['n']))(screen[f"{r['voice']}|{r['stem']}"])
    order = sorted(train_rows, key=drift); cut = int(len(order) * (1 - a.screen))
    say('screen: dropped', len(order) - cut, 'of', len(order), 'train pairs; drift threshold', round(drift(order[cut - 1]), 3))
    train_rows = order[:cut]
load = lambda rows: [W.item(torch.load(f"{a.data}/feats/{r['voice']}/{r['stem']}.pt", weights_only=True), r['voice']) for r in rows]
t0 = time.time(); TRAIN, VAL = load(train_rows), load(val_rows)
lengths = [x['mel'].shape[0] for x in TRAIN]
say(f'data: {len(TRAIN)} train / {len(VAL)} val pairs, {sum(lengths) / 100 / 3600:.1f} h, loaded in {time.time() - t0:.0f}s')
VB = [W.collate(VAL[i:i + 8]) for i in range(0, min(len(VAL), 64), 8)]

# ---------------- model
model = W.Wokws(c, vocab['n_tokens'], len(vocab['kinds'])).to(dev)
R_IDS = torch.tensor([vocab['tokens'][t] for t in ('PIE_r', 'PIE_r̩')], device=dev)
if a.dropout >= 0:                       # regularize against memorizing the training clips (all dropout here is nn.Dropout)
    nd = 0
    for mod in model.modules():
        if isinstance(mod, nn.Dropout): mod.p = a.dropout; nd += 1
    say('dropout set to', a.dropout, 'in', nd, 'modules')
ema = copy.deepcopy(model).eval().requires_grad_(False)


class MelCritic(nn.Module):
    """2D conv critic over a [T, 100] log-mel window (time x frequency)."""
    def __init__(self, ch=(32, 64, 128, 256)):
        super().__init__()
        wn = nn.utils.parametrizations.weight_norm
        layers, i = [], 1
        for j, o in enumerate(ch):
            layers.append(wn(nn.Conv2d(i, o, (3, 5), stride=(1 if j == 0 else 2, 2), padding=(1, 2)))); i = o
        self.layers = nn.ModuleList(layers); self.out = wn(nn.Conv2d(i, 1, 3, padding=1))

    def forward(self, x):
        feats, y = [], x[:, None]
        for l in self.layers:
            y = F.leaky_relu(l(y), 0.1); feats.append(y)
        return self.out(y), feats


CROPS = [int(v) for v in a.crop_frames.split(',')]
critics = nn.ModuleList(MelCritic() for _ in CROPS).to(dev)
say('params (inference)', sum(p.numel() for p in model.parameters()), 'critics', sum(p.numel() for p in critics.parameters()))
opt = torch.optim.AdamW(model.parameters(), lr=a.lr, betas=(0.9, 0.98), weight_decay=0.01)
copt = torch.optim.AdamW(critics.parameters(), lr=a.lr, betas=(0.8, 0.99))
sampler = BucketSampler(lengths, a.batch_frames, a.max_batch, a.seed)


def lr_at(step):
    if step < a.warmup: return a.lr * (step + 1) / a.warmup
    t = min(1.0, (step - a.warmup) / max(1, a.steps - a.warmup))
    return a.lr * (a.lr_final_frac + (1 - a.lr_final_frac) * 0.5 * (1 + math.cos(math.pi * t)))


def span_mask(fmask, frac, span=12):
    if frac <= 0: return None
    starts = (torch.rand(fmask.shape, device=fmask.device) < frac / span).float()
    return (F.max_pool1d(starts[:, None], span, 1, padding=span // 2)[:, 0, :fmask.shape[1]] > 0) & fmask


def objective(m, batch, teacher_p, masking=True, zero_src=False):
    if zero_src: batch = {**batch, 'src': torch.zeros_like(batch['src'])}
    fm0 = torch.arange(batch['mel'].shape[1], device=dev)[None] < batch['frame_lengths'][:, None]
    with torch.autocast(**AMP):
        x, fmask, flen, owner = m.frames(batch, span_mask(fm0, a.src_mask) if masking else None)
        h, pred = m.predict_prosody(x, fmask)
        pred, tgt, trusted = pred.float(), batch['prosody'], batch['pitch_trusted']
        teacher = torch.rand(len(flen), device=dev) < teacher_p
        cond = torch.where(teacher[:, None, None], tgt, m.hard_prosody(pred.detach()))
        pre, post = m.decode(h, cond.to(h.dtype), fmask)
    pre, post, fmf = pre.float(), post.float(), fmask.float()
    sung = fmf * tgt[..., 1] * trusted; enough = (sung.sum(1) >= 10).float()
    isr = torch.isin(batch['tokens'].gather(1, owner), R_IDS) & fmask           # /r/ and /r̩/ frames
    wmel = fmf * (1 + (a.r_weight - 1) * isr.float())
    terms = dict(
        pitch=masked_mean((pred[..., 0] - tgt[..., 0]).abs(), fmf * (trusted + 0.1 * (1 - trusted))),
        pitch_spread=masked_mean((masked_std(pred[..., 0], sung) - masked_std(tgt[..., 0], sung)).abs(), enough),
        voicing=masked_mean(F.binary_cross_entropy_with_logits(pred[..., 1], tgt[..., 1], reduction='none'), fmf),
        energy=masked_mean((pred[..., 2] - tgt[..., 2]).abs(), fmf),
        mel_pre=masked_mean((pre - batch['mel']).abs().mean(-1), wmel),
        mel=masked_mean((post - batch['mel']).abs().mean(-1), wmel))
    if a.r_delta > 0:                                                              # tap contrast: match frame-to-frame change on trills
        rr = (isr[:, 1:] & isr[:, :-1]).float(); dt = batch['mel'][:, 1:] - batch['mel'][:, :-1]
        terms['r_delta'] = masked_mean(((post[:, 1:] - post[:, :-1]) - dt).abs().mean(-1), rr)
    wts = dict(pitch=2.0, pitch_spread=2.0, voicing=1.0, energy=1.0, mel_pre=10.0, mel=10.0, r_delta=10.0 * a.r_delta)
    loss = sum(wts[k] * v for k, v in terms.items())
    with torch.no_grad(): terms['pitch_st'] = 12 / math.log(2) * masked_mean((pred[..., 0] - tgt[..., 0]).abs(), sung)
    return loss, terms, {'post': post, 'rec': 10.0 * terms['mel']}


@torch.no_grad()
def validate(m):
    m.eval(); tot = {}
    for b in VB:
        b = {k: v.to(dev) for k, v in b.items()}
        for name, tp in (('tf', 1.0), ('free', 0.0)):
            _, t, _ = objective(m, b, tp, masking=False)
            tot[f'{name}_mel'] = tot.get(f'{name}_mel', 0) + float(t['mel']) / len(VB)
            if name == 'free': tot['pitch_st'] = tot.get('pitch_st', 0) + float(t['pitch_st']) / len(VB)
        tot['tf_mel_src_zeroed'] = tot.get('tf_mel_src_zeroed', 0) + float(objective(m, b, 1.0, False, True)[1]['mel']) / len(VB)
    m.train() if m is model else None
    return {k: round(v, 4) for k, v in tot.items()}


def save_last(step):
    torch.save({'model': model.state_dict(), 'ema': ema.state_dict(), 'critics': critics.state_dict(), 'opt': opt.state_dict(),
                'copt': copt.state_dict(), 'sampler': sampler.state(), 'step': step, 'args': vars(a), 'rng': torch.get_rng_state()},
               f'{RUN}/last.pt.tmp')
    os.replace(f'{RUN}/last.pt.tmp', f'{RUN}/last.pt')


def export(step):
    torch.save({'config': c.to_dict(), 'vocab': vocab, 'step': step, 'mel_norm': (W.MEL_MEAN, W.MEL_SCALE),
                'model': {k: v.detach().cpu() for k, v in ema.state_dict().items()}}, f'{RUN}/step{step}.pt')


step = 0
if a.resume and os.path.exists(f'{RUN}/last.pt'):
    ck = torch.load(f'{RUN}/last.pt', map_location='cpu', weights_only=False)
    model.load_state_dict(ck['model']); ema.load_state_dict(ck['ema']); critics.load_state_dict(ck['critics'])
    opt.load_state_dict(ck['opt']); copt.load_state_dict(ck['copt']); sampler.load_state(ck['sampler']); step = ck['step']
    torch.set_rng_state(ck['rng']); say('resumed at', step)
    if not a.init and ck.get('args', {}).get('init'):   # a run started with --init stays free-running (teacher prob 0)
        a.init = ck['args']['init']; say('run was started with --init', a.init)   # after a resume, as before the pause
else:
    if a.init:
        ck = torch.load(a.init, map_location='cpu', weights_only=False)
        model.load_state_dict(ck['ema'] if 'ema' in ck else ck['model']); ema.load_state_dict(model.state_dict())
        say('init from', a.init, 'step', ck.get('step'))
    say('args', json.dumps(vars(a)))
    say('val 0', validate(model)); export(0)
    w0 = {k: v.detach().clone() for k, v in model.state_dict().items()}


def producer(q, stop):
    while not stop.is_set():
        b = W.collate([TRAIN[i] for i in sampler.next()])
        if dev.type == 'cuda': b = {k: v.pin_memory() for k, v in b.items()}
        while not stop.is_set():
            try: q.put(b, timeout=1); break
            except queue.Full: pass
bq, bstop = queue.Queue(maxsize=max(1, a.prefetch)), threading.Event()
if a.prefetch: threading.Thread(target=producer, args=(bq, bstop), daemon=True).start()
next_batch = (lambda: {k: v.to(dev, non_blocking=True) for k, v in bq.get().items()}) if a.prefetch else \
             (lambda: W.collate([TRAIN[i] for i in sampler.next()], dev))


def mel_crops(fake, real, lengths, size):
    size = min(size, int(lengths.min()))
    start = (torch.rand(len(lengths), device=dev) * (lengths - size + 1)).long()
    idx = (start[:, None] + torch.arange(size, device=dev))[..., None].expand(-1, -1, fake.shape[-1])
    return fake.gather(1, idx), real.gather(1, idx), idx


model.train(); t_start = time.time(); s_start = step; stopped = False
while step < a.steps:
    if os.path.exists(f'{RUN}/STOP'):
        save_last(step); say('STOP at', step); os.remove(f'{RUN}/STOP'); stopped = True; break
    if a.max_steps and step - s_start >= a.max_steps:
        save_last(step); say('max_steps reached', step); stopped = True; break
    for g in opt.param_groups: g['lr'] = lr_at(step)
    for g in copt.param_groups: g['lr'] = lr_at(step)
    batch = next_batch()
    tp = teacher_probability(step, a.teacher_hold, a.teacher_ramp, a.teacher_final) if not a.init else 0.0
    opt.zero_grad(set_to_none=True)
    loss, terms, aux = objective(model, batch, tp)
    if step >= a.gan_start:
        post, flen = aux['post'], batch['frame_lengths']
        d_loss, gan, sel = 0.0, 0.0, []
        for cr, size in zip(critics, CROPS):
            fake, real, idx = mel_crops(post, batch['mel'], flen, size); sel.append(idx)
            rl, _ = cr(real); fl, _ = cr(fake.detach())
            d_loss = d_loss + ((rl - 1) ** 2).mean() + (fl ** 2).mean()
        copt.zero_grad(set_to_none=True); d_loss.backward(); nn.utils.clip_grad_norm_(critics.parameters(), 10); copt.step()
        critics.requires_grad_(False); adv = fm = 0.0
        for cr, idx in zip(critics, sel):
            fake, real = post.gather(1, idx), batch['mel'].gather(1, idx)
            with torch.no_grad(): _, rf = cr(real)
            fl, ff = cr(fake)
            adv = adv + ((fl - 1) ** 2).mean(); fm = fm + sum((x - y).abs().mean() for x, y in zip(ff, rf)) / len(ff)
        gan = adv + a.feature_matching * fm
        rg = torch.autograd.grad(aux['rec'], post, retain_graph=True)[0]
        gg = torch.autograd.grad(gan, post, retain_graph=True)[0]
        ramp = min(1.0, (step - a.gan_start + 1) / max(a.gan_ramp, 1))
        scale = (a.gan_ratio * ramp * rg.norm() / gg.norm().clamp_min(1e-12)).clamp(max=100.0).detach()
        loss = loss + scale * gan; terms.update(d=d_loss, adv=adv, fm=fm, gan_scale=scale)
        loss.backward(); critics.requires_grad_(True)
    else:
        loss.backward()
    gn = nn.utils.clip_grad_norm_(model.parameters(), a.grad_clip)
    opt.step(); step += 1
    with torch.no_grad():
        d = min(a.ema, (1 + step) / (10 + step))
        for pe, pm in zip(ema.parameters(), model.parameters()): pe.lerp_(pm, 1 - d)
        for be, bm in zip(ema.buffers(), model.buffers()): be.copy_(bm)
    if step == 1 and not a.resume:
        ch = sum(float((v.float() - w0[k].to(v.device).float()).abs().max()) > 0 for k, v in model.state_dict().items() if v.is_floating_point())
        say('weights changed after step 1 in', ch, 'of', sum(v.is_floating_point() for v in model.state_dict().values()), 'tensors')
    if step % a.log_every == 0 or step <= 3:
        el = time.time() - t_start
        say(f'step {step}/{a.steps} loss {float(loss):.3f} mel {float(terms["mel"]):.4f} pre {float(terms["mel_pre"]):.4f} '
            f'pitch_st {float(terms["pitch_st"]):.2f} ' + (f'd {float(terms["d"]):.3f} adv {float(terms["adv"]):.3f} fm {float(terms["fm"]):.3f} '
            f'gs {float(terms["gan_scale"]):.2f} ' if 'd' in terms else '') + f'grad {float(gn):.2f} lr {lr_at(step):.2e} tp {tp:.2f} '
            f'{el / max(1, step - s_start):.3f}s/step frames {int(batch["frame_lengths"].sum())} mem {mem()}')
    if step % a.val_every == 0: say('val', step, 'ema', validate(ema))
    if step % a.save_every == 0 or step == a.steps: export(step); save_last(step); say('saved', step)
bstop.set(); say('TRAIN_END', step)
if stopped: sys.exit(3)            # paused, resumable: not DONE
