"""wokʷs (PIE *wṓkʷs 'voice'): the Chimera -> paid speech-to-speech converter, trained from scratch.

  PIE phone tokens + phone class --encoder--> expanded by CHIMERA's own timing (no duration predictor, so no phone can
  be added, dropped or moved) + per-frame Chimera features (audio.py log-mel 100 + log-F0, voiced, energy; spans
  masked in training so pronunciation rests on the tokens) --prosody stack--> paid's pitch / voicing / energy
  --acoustic stack + conv postnet--> paid's log-mel in the audio.py format, which our vocoder gʷerh (v4 stands in
  until then) turns into audio.

Transformer blocks are tiny-voca's (Apache-2.0, imported unedited)."""
import os, sys
import torch
from torch import nn
from torch.nn import functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
TV = os.path.expanduser(os.environ.get('TINY_VOCA', '~/AI/chimera-pie-data/tv/tiny-voca/src'))
sys.path.insert(0, TV); sys.path.insert(0, HERE)
from tiny_voca.config import Config
from tiny_voca.model import Stack, length_mask
from tiny_voca.data import continuous_pitch
import audio as A

SPEAKERS = ('ZAZY', 'ANTONIO', 'VALERIA', 'W02')
VOICED_KINDS = (1, 9, 10, 11)          # V, Ns, Rs, Ls: voiced by definition
MEL_MEAN, MEL_SCALE = -6.5, 3.0         # audio.mel normalisation: paid mean -6.53, std 2.96 (200-clip sample)
ENERGY_MEAN, ENERGY_SCALE = -4.8, 3.0   # log RMS: paid mean -4.77, std 3.06
IN_FEATS = A.N_MELS + 3


def config(channels=256, heads=4, feedforward=1024, encoder_layers=4, prosody_layers=3, acoustic_layers=8, **kw):
    """tiny-voca Config used only for its transformer hyper-parameters."""
    return Config(speakers=SPEAKERS, channels=channels, heads=heads, feedforward=feedforward, encoder_layers=encoder_layers,
                  prosody_layers=prosody_layers, acoustic_layers=acoustic_layers, **kw)


class Postnet(nn.Module):
    def __init__(self, n=A.N_MELS, ch=256, layers=5, k=5, dropout=0.1):
        super().__init__()
        dims = [n] + [ch] * (layers - 1) + [n]
        self.convs = nn.ModuleList(nn.Conv1d(i, o, k, padding=k // 2) for i, o in zip(dims[:-1], dims[1:]))
        self.drop = nn.Dropout(dropout)

    def forward(self, x, mask):
        y = x.transpose(1, 2)
        for i, cv in enumerate(self.convs):
            y = cv(y * mask[:, None])
            if i < len(self.convs) - 1: y = self.drop(F.gelu(y))
        return (x + y.transpose(1, 2)) * mask[..., None]


class Wokws(nn.Module):
    def __init__(self, c, n_tokens, n_kinds=12):
        super().__init__()
        self.config = c
        self.tokens = nn.Embedding(n_tokens, c.channels, padding_idx=0)
        self.kinds = nn.Embedding(n_kinds, c.channels)
        self.voices = nn.Embedding(len(c.speakers), c.channels)
        self.encoder = Stack(c, c.encoder_layers)
        self.frame_voices = nn.Embedding(len(c.speakers), c.channels)
        self.frame_position = nn.Linear(3, c.channels)
        self.frame_input = nn.Sequential(nn.Linear(IN_FEATS, c.channels), nn.GELU(), nn.Linear(c.channels, c.channels))
        self.prosody_stack = Stack(c, c.prosody_layers)
        self.prosody_head = nn.Linear(c.channels, 3)
        self.prosody_projection = nn.Linear(3, c.channels)
        self.acoustic_stack = Stack(c, c.acoustic_layers)
        self.mel_out = nn.Linear(c.channels, A.N_MELS)
        self.postnet = Postnet()

    def encode(self, tokens, kinds, lengths, speakers):
        mask = length_mask(lengths, tokens.shape[1])
        x = (self.tokens(tokens) + self.kinds(kinds) + self.voices(speakers)[:, None]) * mask[..., None]
        return self.encoder(x, mask), mask

    def expand(self, hidden, durations, speakers):
        """tiny_voca.model.TinyVoca.expand: repeat token states by frame durations + position inside the token."""
        lengths = durations.sum(1); size = int(lengths.max()); ends = durations.cumsum(1)
        frame = torch.arange(size, device=hidden.device)[None].expand(hidden.shape[0], size).contiguous()
        index = torch.searchsorted(ends, frame, right=True).clamp(max=durations.shape[1] - 1)
        owned = durations.gather(1, index).clamp_min(1)
        offset = frame - (ends.gather(1, index) - durations.gather(1, index))
        relative = (offset.to(hidden.dtype) + 0.5) / owned
        features = torch.stack((relative, 1 - relative, torch.log1p(owned.to(hidden.dtype)) / 4), dim=-1)
        mask = frame < lengths[:, None]
        expanded = hidden.gather(1, index[..., None].expand(-1, -1, hidden.shape[-1]))
        expanded = expanded + self.frame_position(features) + self.frame_voices(speakers)[:, None]
        return expanded * mask[..., None], mask, lengths, index

    def frames(self, batch, src_mask=None):
        hidden, _ = self.encode(batch['tokens'], batch['kinds'], batch['token_lengths'], batch['speakers'])
        x, fmask, lengths, owner = self.expand(hidden, batch['durations'], batch['speakers'])
        src = batch['src'] if src_mask is None else batch['src'] * (~src_mask)[..., None]
        return x + self.frame_input(src) * fmask[..., None], fmask, lengths, owner

    def predict_prosody(self, x, fmask):
        h = self.prosody_stack(x, fmask)
        return h, self.prosody_head(h) * fmask[..., None]

    @staticmethod
    def hard_prosody(p):
        return torch.stack((p[..., 0].clamp(-2.0, 1.5), (p[..., 1] > 0).to(p.dtype), p[..., 2].clamp(-4.5, 3.0)), dim=-1)

    def decode(self, h, condition, fmask):
        a = self.acoustic_stack((h + self.prosody_projection(condition)) * fmask[..., None], fmask)
        pre = self.mel_out(a) * fmask[..., None]
        return pre, self.postnet(pre, fmask)

    @torch.inference_mode()
    def convert(self, batch, pitch_shift=0.0):
        """Free-running: the model's own pitch / voicing / energy on Chimera's timing. pitch_shift in log-F0 units
        (semitones * ln2/12) is added to the predicted pitch. Returns log-mel [B, N, 100] (audio.py units), lengths."""
        x, fmask, lengths, owner = self.frames(batch)
        h, p = self.predict_prosody(x, fmask)
        vk = torch.isin(batch['kinds'].gather(1, owner), torch.tensor(VOICED_KINDS, device=x.device)) & fmask
        p = torch.cat((p[..., :1] + pitch_shift, torch.where(vk, p[..., 1].clamp_min(2.0), p[..., 1])[..., None], p[..., 2:]), -1)
        _, post = self.decode(h, self.hard_prosody(p), fmask)
        return post * MEL_SCALE + MEL_MEAN, lengths, p


def item(d, voice):
    def pros(raw):
        pitch, trusted = continuous_pitch(raw[:, 0], raw[:, 1])
        return pitch, raw[:, 1].clone(), (raw[:, 2] - ENERGY_MEAN) / ENERGY_SCALE, trusted
    pp, pv, pe, trusted = pros(d['paid_pros'])
    kinds = d['kinds'].long(); dur = d['dur'].long()
    vk = torch.repeat_interleave(torch.isin(kinds, torch.tensor(VOICED_KINDS)), dur)
    pv = torch.maximum(pv, vk.float())
    sp, sv, se, _ = pros(d['chim_pros'])
    src = torch.cat(((d['chim_mel'].float() - MEL_MEAN) / MEL_SCALE, torch.stack((sp, sv, se), -1)), -1)
    return {'tokens': d['tokens'].long(), 'kinds': kinds, 'durations': dur, 'speaker': SPEAKERS.index(voice),
            'mel': d['paid_mel'], 'src': src.half(), 'prosody': torch.stack((pp, pv, pe), -1), 'pitch_trusted': trusted}


def collate(items, device='cpu'):
    from torch.nn.utils.rnn import pad_sequence
    b = {k: pad_sequence([x[k] for x in items], batch_first=True).to(device)
         for k in ('tokens', 'kinds', 'durations', 'mel', 'src', 'prosody', 'pitch_trusted')}
    b['mel'] = (b['mel'].float() - MEL_MEAN) / MEL_SCALE; b['src'] = b['src'].float()
    b['token_lengths'] = torch.tensor([x['tokens'].numel() for x in items], device=device)
    b['frame_lengths'] = torch.tensor([x['mel'].shape[0] for x in items], device=device)
    b['speakers'] = torch.tensor([x['speaker'] for x in items], device=device)
    return b
