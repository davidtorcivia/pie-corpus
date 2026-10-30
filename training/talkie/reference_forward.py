"""Independent functional forward pass used only to cross-check modeling_talkie.py.

Written separately from the module, from talkie-lm/talkie model.py read as text
(commit 35317ba3). It takes a state dict under the original talkie names and
returns logits for every position. eps=None mirrors the default of F.rms_norm."""
import torch, torch.nn.functional as F

def rope(x, cos, sin):
    d = x.shape[-1] // 2
    x1, x2 = x[..., :d], x[..., d:]
    return torch.cat([x1 * cos + x2 * sin, -x1 * sin + x2 * cos], -1).type_as(x)

def rms(x, eps):
    return F.rms_norm(x, (x.shape[-1],), eps=eps)

@torch.no_grad()
def forward(sd, ids, dtype=torch.float32, eps=None, n_layer=40, n_head=40, hd=128, base=1_000_000, rope_bf16=True, dev="cpu"):
    g = lambda k: sd[k].to(dev, dtype)
    T = ids.shape[1]
    inv = 1.0 / (base ** (torch.arange(0, hd, 2, dtype=torch.float32) / hd))
    fr = torch.outer(torch.arange(T, dtype=torch.float32), inv)
    cos, sin = fr.cos(), fr.sin()
    if rope_bf16: cos, sin = cos.bfloat16(), sin.bfloat16()
    cos, sin = cos[None, :, None, :].to(dev, dtype), sin[None, :, None, :].to(dev, dtype)
    x = F.embedding(ids.to(dev), g("embed.weight"))
    x = rms(x, eps); e = x
    B = ids.shape[0]
    for i in range(n_layer):
        p = f"blocks.{i}."
        h = rms(x, eps)
        q = (h @ g(p+"attn.attn_query.weight").T).view(B, T, n_head, hd)
        k = (h @ g(p+"attn.attn_key.weight").T).view(B, T, n_head, hd)
        v = (h @ g(p+"attn.attn_value.weight").T).view(B, T, n_head, hd)
        q, k = rope(q, cos, sin), rope(k, cos, sin)
        q, k = rms(q, eps), rms(k, eps)
        q = q * g(p+"attn.head_gain.head_g").view(1, 1, -1, 1)
        y = F.scaled_dot_product_attention(q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2), is_causal=True)
        y = y.transpose(1, 2).reshape(B, T, -1) @ g(p+"attn.attn_resid.weight").T
        x = x + y * g(p+"attn_gain.a_g")
        h = rms(x, eps)
        m = (F.silu(h @ g(p+"mlp.mlp_gate.weight").T) * (h @ g(p+"mlp.mlp_linear.weight").T)) @ g(p+"mlp.mlp_resid.weight").T
        x = x + m * g(p+"mlp_gain.a_g")
        x = x + e * g(p+"embed_skip.a_g")
    x = rms(x, eps)
    return (x @ (g("lm_head") * g("lm_head_gain.w_g")).T).float()
