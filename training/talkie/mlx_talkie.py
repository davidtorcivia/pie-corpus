"""talkie-1930-13b in MLX: the same model as modeling_talkie.py.

It loads the same safetensors shards (original talkie names, renamed at
load) as bf16. Projections are mlx.nn.Linear, so mlx_lm.tuner LoRALinear
can wrap them by name: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj,
down_proj. The model exposes ``.layers`` for mlx_lm's tuner utilities.
"""

from __future__ import annotations

import json
import os
import sys

import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modeling_talkie import TalkieConfig, rename  # noqa: E402  (shared name map and dims)


def rms(x: mx.array, eps: float | None) -> mx.array:
    if eps is None:  # torch F.rms_norm default: eps of the fp32 compute type, even for bf16 input
        eps = float(mx.finfo(mx.float32).eps)
    return mx.fast.rms_norm(x, None, eps)


def rope(x: mx.array, cos: mx.array, sin: mx.array) -> mx.array:
    d = x.shape[-1] // 2
    x1, x2 = x[..., :d], x[..., d:]
    return mx.concatenate([x1 * cos + x2 * sin, -x1 * sin + x2 * cos], -1)


def rope_tables(cfg: TalkieConfig, start: int, length: int, dtype):
    inv = 1.0 / (cfg.rope_theta ** (mx.arange(0, cfg.head_dim, 2, dtype=mx.float32) / cfg.head_dim))
    f = mx.arange(start, start + length, dtype=mx.float32)[:, None] * inv[None, :]
    cos = mx.cos(f).astype(mx.bfloat16).astype(dtype)  # reference rounds the tables to bf16
    sin = mx.sin(f).astype(mx.bfloat16).astype(dtype)
    return cos[None, :, None, :], sin[None, :, None, :]


class Attention(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.cfg = cfg
        d, hd = cfg.d_model, cfg.n_head * cfg.head_dim
        self.q_proj = nn.Linear(d, hd, bias=False)
        self.k_proj = nn.Linear(d, hd, bias=False)
        self.v_proj = nn.Linear(d, hd, bias=False)
        self.o_proj = nn.Linear(hd, d, bias=False)
        self.head_g = mx.ones((cfg.n_head,))

    def __call__(self, x, cos, sin, cache=None):
        B, T, _ = x.shape
        H, D = self.cfg.n_head, self.cfg.head_dim
        q = self.q_proj(x).reshape(B, T, H, D)
        k = self.k_proj(x).reshape(B, T, H, D)
        v = self.v_proj(x).reshape(B, T, H, D)
        q, k = rope(q, cos, sin), rope(k, cos, sin)
        q, k = rms(q, self.cfg.eps), rms(k, self.cfg.eps)
        q = q * self.head_g.astype(q.dtype)[None, None, :, None]
        q, k, v = q.transpose(0, 2, 1, 3), k.transpose(0, 2, 1, 3), v.transpose(0, 2, 1, 3)
        if cache is not None:
            if "k" in cache:
                k = mx.concatenate([cache["k"], k], 2)
                v = mx.concatenate([cache["v"], v], 2)
            cache["k"], cache["v"] = k, v
        mask = "causal" if T > 1 else None
        y = mx.fast.scaled_dot_product_attention(q, k, v, scale=D**-0.5, mask=mask)
        return self.o_proj(y.transpose(0, 2, 1, 3).reshape(B, T, H * D))


class MLP(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.gate_proj = nn.Linear(cfg.d_model, cfg.d_mlp, bias=False)
        self.up_proj = nn.Linear(cfg.d_model, cfg.d_mlp, bias=False)
        self.down_proj = nn.Linear(cfg.d_mlp, cfg.d_model, bias=False)

    def __call__(self, x):
        return self.down_proj(nn.silu(self.gate_proj(x)) * self.up_proj(x))


class Block(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.cfg = cfg
        self.attn = Attention(cfg)
        self.mlp = MLP(cfg)
        self.attn_gain = mx.ones((1,))
        self.mlp_gain = mx.ones((1,))
        self.embed_skip = mx.zeros((1,))

    def __call__(self, e, x, cos, sin, cache=None):
        x = x + self.attn(rms(x, self.cfg.eps), cos, sin, cache) * self.attn_gain.astype(x.dtype)
        x = x + self.mlp(rms(x, self.cfg.eps)) * self.mlp_gain.astype(x.dtype)
        return x + e * self.embed_skip.astype(x.dtype)


class TalkieForCausalLM(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.cfg = cfg
        self.embed = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.layers = [Block(cfg) for _ in range(cfg.n_layer)]
        self.lm_head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        self.lm_head_gain = mx.ones((1,))

    def __call__(self, input_ids: mx.array, caches: list | None = None) -> mx.array:
        """Return logits [B, T, V] (float32). In-place KV caches: a list of dicts, one per layer."""
        start = caches[0]["k"].shape[2] if caches is not None and "k" in caches[0] else 0
        x = rms(self.embed(input_ids), self.cfg.eps)
        e = x
        cos, sin = rope_tables(self.cfg, start, input_ids.shape[1], x.dtype)
        for i, blk in enumerate(self.layers):
            x = blk(e, x, cos, sin, None if caches is None else caches[i])
        x = rms(x, self.cfg.eps)
        w = self.lm_head.weight * self.lm_head_gain.astype(x.dtype)
        return (x @ w.T).astype(mx.float32)

    def generate(self, ids: list[int], max_new_tokens=100, stop_ids=()):
        caches = [{} for _ in self.layers]
        logits = self(mx.array([ids]), caches)[:, -1]
        out = []
        for _ in range(max_new_tokens):
            nxt = mx.argmax(logits, -1)
            t = nxt.item()
            if t in stop_ids:
                break
            out.append(t)
            logits = self(nxt[:, None], caches)[:, -1]
        return out


def load_talkie(path: str, dtype=mx.bfloat16) -> TalkieForCausalLM:
    idx = json.load(open(os.path.join(path, "model.safetensors.index.json")))
    weights = {}
    for fn in sorted(set(idx["weight_map"].values())):
        for k, v in mx.load(os.path.join(path, fn)).items():
            weights[rename(k)] = v.astype(dtype)
    cfg = TalkieConfig(vocab_size=weights["embed.weight"].shape[0])
    model = TalkieForCausalLM(cfg)
    model.load_weights(list(weights.items()), strict=True)
    mx.eval(model.parameters())
    return model
