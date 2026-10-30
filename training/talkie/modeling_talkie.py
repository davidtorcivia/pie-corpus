"""talkie-1930-13b in plain PyTorch.

This is our own implementation, written from the talkie architecture. That
architecture was read as text from github.com/talkie-lm/talkie
src/talkie/model.py at commit 35317ba3; none of that code is imported. It
loads the safetensors shards that were converted from the official
checkpoints (see README.md). Training runs through peft LoRA on the
projection names below.

The model is Qwen3-like (SwiGLU, RoPE, qk-norm, untied head) with these
differences:
  * every RMSNorm is weightless (F.rms_norm, default eps), and the token
    embedding is RMS-normalised as well;
  * after each block, x += embed_skip[l] * normalised_embedding;
  * the attention and MLP outputs are scaled by the learned scalars
    attn_gain[l] and mlp_gain[l];
  * the qk-norm sits after RoPE, and the normalised q is multiplied by a
    learned per-head scale head_g[l, h];
  * RoPE rotates the other way: y1 = x1 cos + x2 sin, y2 = -x1 sin + x2 cos;
    theta is 1e6, and cos/sin are rounded to bf16;
  * the LM-head weight is multiplied by the learned scalar lm_head_gain.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class TalkieConfig:
    vocab_size: int = 65536  # 65540 for the -it chat model
    n_layer: int = 40
    n_head: int = 40
    d_model: int = 5120
    head_dim: int = 128
    d_mlp: int = 13696
    rope_theta: float = 1_000_000.0
    eps: float | None = None  # None = torch.finfo(dtype).eps, as the reference does


def rms(x: torch.Tensor, eps: float | None) -> torch.Tensor:
    return F.rms_norm(x, (x.shape[-1],), eps=eps)


def rope(x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
    d = x.shape[-1] // 2
    x1, x2 = x[..., :d], x[..., d:]
    return torch.cat([x1 * cos + x2 * sin, -x1 * sin + x2 * cos], -1).type_as(x)


def rope_tables(cfg: TalkieConfig, start: int, length: int, device, dtype):
    inv = 1.0 / (cfg.rope_theta ** (torch.arange(0, cfg.head_dim, 2, dtype=torch.float32) / cfg.head_dim))
    t = torch.arange(start, start + length, dtype=torch.float32)
    f = torch.outer(t, inv)
    cos, sin = f.cos().bfloat16(), f.sin().bfloat16()  # the reference precomputes in bf16
    return cos[None, :, None, :].to(device, dtype), sin[None, :, None, :].to(device, dtype)


class Attention(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model
        self.q_proj = nn.Linear(d, cfg.n_head * cfg.head_dim, bias=False)
        self.k_proj = nn.Linear(d, cfg.n_head * cfg.head_dim, bias=False)
        self.v_proj = nn.Linear(d, cfg.n_head * cfg.head_dim, bias=False)
        self.o_proj = nn.Linear(cfg.n_head * cfg.head_dim, d, bias=False)
        self.head_g = nn.Parameter(torch.ones(cfg.n_head))

    def forward(self, x, cos, sin, cache=None):
        B, T, _ = x.shape
        H, D = self.cfg.n_head, self.cfg.head_dim
        q = self.q_proj(x).view(B, T, H, D)
        k = self.k_proj(x).view(B, T, H, D)
        v = self.v_proj(x).view(B, T, H, D)
        q, k = rope(q, cos, sin), rope(k, cos, sin)
        q, k = rms(q, self.cfg.eps), rms(k, self.cfg.eps)
        q = q * self.head_g.type_as(q).view(1, 1, -1, 1)
        q, k, v = q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2)
        if cache is not None:
            if cache.get("k") is not None:
                k = torch.cat([cache["k"], k], 2)
                v = torch.cat([cache["v"], v], 2)
            cache["k"], cache["v"] = k, v
        S = k.shape[2]
        if S == T:
            y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        else:  # decoding with a cache: query i sits at absolute position S-T+i
            mask = torch.ones(T, S, dtype=torch.bool, device=x.device).tril(S - T)
            y = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
        return self.o_proj(y.transpose(1, 2).reshape(B, T, H * D))


class MLP(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.gate_proj = nn.Linear(cfg.d_model, cfg.d_mlp, bias=False)
        self.up_proj = nn.Linear(cfg.d_model, cfg.d_mlp, bias=False)
        self.down_proj = nn.Linear(cfg.d_mlp, cfg.d_model, bias=False)

    def forward(self, x):
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class Block(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.cfg = cfg
        self.attn = Attention(cfg)
        self.mlp = MLP(cfg)
        self.attn_gain = nn.Parameter(torch.ones(1))
        self.mlp_gain = nn.Parameter(torch.ones(1))
        self.embed_skip = nn.Parameter(torch.zeros(1))

    def forward(self, e, x, cos, sin, cache=None):
        x = x + self.attn(rms(x, self.cfg.eps), cos, sin, cache) * self.attn_gain.type_as(x)
        x = x + self.mlp(rms(x, self.cfg.eps)) * self.mlp_gain.type_as(x)
        return x + e * self.embed_skip.type_as(x)


class TalkieForCausalLM(nn.Module):
    def __init__(self, cfg: TalkieConfig):
        super().__init__()
        self.cfg = cfg
        self.embed = nn.Embedding(cfg.vocab_size, cfg.d_model)
        self.layers = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.lm_head = nn.Linear(cfg.d_model, cfg.vocab_size, bias=False)
        self.lm_head_gain = nn.Parameter(torch.ones(1))

    def forward(self, input_ids: torch.Tensor, caches: list | None = None) -> torch.Tensor:
        """Return logits [B, T, V] in float32. Pass ``caches`` (one dict per layer) to decode incrementally."""
        start = 0
        if caches is not None and caches[0].get("k") is not None:
            start = caches[0]["k"].shape[2]
        x = rms(self.embed(input_ids), self.cfg.eps)
        e = x
        cos, sin = rope_tables(self.cfg, start, input_ids.shape[1], x.device, x.dtype)
        for i, blk in enumerate(self.layers):
            x = blk(e, x, cos, sin, None if caches is None else caches[i])
        x = rms(x, self.cfg.eps)
        return F.linear(x, self.lm_head.weight * self.lm_head_gain.type_as(x)).float()

    @torch.no_grad()
    def generate(self, input_ids, max_new_tokens=100, temperature=0.0, stop_ids=()):
        caches = [{} for _ in self.layers]
        logits = self(input_ids, caches)[:, -1]
        out = []
        for _ in range(max_new_tokens):
            if temperature > 0:
                nxt = torch.multinomial(torch.softmax(logits / temperature, -1), 1)
            else:
                nxt = logits.argmax(-1, keepdim=True)
            if nxt.item() in stop_ids:
                break
            out.append(nxt.item())
            logits = self(nxt, caches)[:, -1]
        return out


# checkpoint name (talkie) -> module name (ours), with {i} for the layer index
_RENAMES = {
    "blocks.{i}.attn.attn_query.weight": "layers.{i}.attn.q_proj.weight",
    "blocks.{i}.attn.attn_key.weight": "layers.{i}.attn.k_proj.weight",
    "blocks.{i}.attn.attn_value.weight": "layers.{i}.attn.v_proj.weight",
    "blocks.{i}.attn.attn_resid.weight": "layers.{i}.attn.o_proj.weight",
    "blocks.{i}.attn.head_gain.head_g": "layers.{i}.attn.head_g",
    "blocks.{i}.mlp.mlp_gate.weight": "layers.{i}.mlp.gate_proj.weight",
    "blocks.{i}.mlp.mlp_linear.weight": "layers.{i}.mlp.up_proj.weight",
    "blocks.{i}.mlp.mlp_resid.weight": "layers.{i}.mlp.down_proj.weight",
    "blocks.{i}.attn_gain.a_g": "layers.{i}.attn_gain",
    "blocks.{i}.mlp_gain.a_g": "layers.{i}.mlp_gain",
    "blocks.{i}.embed_skip.a_g": "layers.{i}.embed_skip",
}


def rename(k: str) -> str:
    if k == "embed.weight":
        return k
    if k == "lm_head":
        return "lm_head.weight"
    if k == "lm_head_gain.w_g":
        return "lm_head_gain"
    parts = k.split(".")
    i = parts[1]
    tmpl = ".".join(["blocks", "{i}"] + parts[2:])
    return _RENAMES[tmpl].format(i=i)


def load_talkie(path: str, dtype=torch.bfloat16, device="cpu") -> TalkieForCausalLM:
    """Load from a directory of converted safetensors shards (talkie names)."""
    from safetensors.torch import load_file

    idx = json.load(open(os.path.join(path, "model.safetensors.index.json")))
    sd = {}
    for fn in sorted(set(idx["weight_map"].values())):
        for k, v in load_file(os.path.join(path, fn)).items():
            sd[rename(k)] = v.to(device, dtype)
    cfg = TalkieConfig(vocab_size=sd["embed.weight"].shape[0])
    with torch.device("meta"):
        model = TalkieForCausalLM(cfg)
    model.load_state_dict(sd, strict=True, assign=True)
    return model.eval()
