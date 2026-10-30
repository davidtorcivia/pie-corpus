"""Cross-checks for the talkie ports. Run with python -I from outside the model dirs.

  verify.py torch <safetensors_dir> base|it <out.npz>
      fp32 CPU: modeling_talkie logits vs reference_forward logits (max |diff|),
      then bf16 MPS greedy generation with KV cache, checked against an uncached pass.
  verify.py mlx <safetensors_dir> base|it <out.npz from the torch run>
      bf16 MLX logits vs the saved fp32 torch logits, then greedy generation.
"""

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GETTYSBURG = (
    "Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, "
    "and dedicated to the proposition that all men are created equal. Now we are engaged in a great civil war, testing "
    "whether that nation, or any nation so conceived and so dedicated, can long endure. We are met on a great battle-field "
    "of that war. We have come to dedicate a portion of that field, as a final resting place for those who here gave their "
    "lives that that nation might live."
)
# Example prompts from the talkie README
PROMPTS = {
    "base": ["If scientists discover life on other planets,", "The effects of the automobile on public morality have"],
    "it": ["Write an essay predicting what life will be like in the year 1960.", "What were the causes of the French Revolution?"],
}


def texts(tok, style):
    out = [GETTYSBURG]
    for p in PROMPTS[style]:
        if style == "it":
            p = tok.apply_chat_template([{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True)
        out.append(p)
    return [tok(t, add_special_tokens=False)["input_ids"] for t in out]


def stop_ids(tok, style):
    s = {tok.convert_tokens_to_ids("<|endoftext|>")}
    if style == "it":
        s.add(tok.convert_tokens_to_ids("<|end|>"))
    return s


def run_torch(d, style, out):
    import torch
    from safetensors.torch import load_file
    from transformers import PreTrainedTokenizerFast
    import modeling_talkie as mt
    import reference_forward as ref

    tok = PreTrainedTokenizerFast.from_pretrained(d)
    idx = json.load(open(os.path.join(d, "model.safetensors.index.json")))
    sd = {}
    for fn in sorted(set(idx["weight_map"].values())):
        for k, v in load_file(os.path.join(d, fn)).items():
            sd[k] = v.float()
    cfg = mt.TalkieConfig(vocab_size=sd["embed.weight"].shape[0])
    with torch.device("meta"):
        model = mt.TalkieForCausalLM(cfg)
    model.load_state_dict({mt.rename(k): v for k, v in sd.items()}, strict=True, assign=True)  # shares storage
    model.eval()
    saved = {}
    with torch.no_grad():
        for i, ids in enumerate(texts(tok, style)):
            x = torch.tensor([ids])
            a = model(x)
            b = ref.forward(sd, x, dtype=torch.float32)
            nll = torch.nn.functional.cross_entropy(a[0, :-1], x[0, 1:]).item()
            print(f"[fp32] text {i} ({len(ids)} tok): max|module-reference| = {(a - b).abs().max().item():.3e}  nll/tok {nll:.4f}", flush=True)
            saved[f"logits{i}"] = a[0].numpy()
            saved[f"ids{i}"] = np.array(ids)
    np.savez(out, **saved)
    # bf16 MPS greedy generation with KV cache
    model = model.to("mps", torch.bfloat16)
    del sd
    stops = stop_ids(tok, style)
    for i, ids in enumerate(texts(tok, style)[1:], 1):
        t0 = time.time()
        gen = model.generate(torch.tensor([ids], device="mps"), max_new_tokens=80, stop_ids=stops)
        dt = time.time() - t0
        with torch.no_grad():  # uncached check: argmax of a full pass must reproduce the cached greedy tokens
            full = model(torch.tensor([ids + gen], device="mps"))[0, len(ids) - 1 : -1].argmax(-1).tolist()
        agree = sum(a == b for a, b in zip(full, gen)) / max(1, len(gen))
        print(f"[torch bf16 greedy] {len(gen)} tok in {dt:.1f}s, cached-vs-uncached argmax agreement {agree:.3f}\n{tok.decode(gen)!r}", flush=True)


def run_mlx(d, style, npz):
    import mlx.core as mx
    from transformers import PreTrainedTokenizerFast
    import mlx_talkie

    tok = PreTrainedTokenizerFast.from_pretrained(d)
    model = mlx_talkie.load_talkie(d)
    ref = np.load(npz)
    for i, ids in enumerate(texts(tok, style)):
        a = np.array(model(mx.array([ids]))[0])
        b = ref[f"logits{i}"]
        diff = np.abs(a - b)
        top = (a.argmax(-1) == b.argmax(-1)).mean()
        logp = a - np.log(np.exp(a - a.max(-1, keepdims=True)).sum(-1, keepdims=True)) - a.max(-1, keepdims=True)
        nll = -logp[np.arange(len(ids) - 1), ids[1:]].mean()
        print(f"[mlx bf16 vs torch fp32] text {i}: max|dlogit| {diff.max():.3f}  mean {diff.mean():.4f}  top1 agree {top:.3f}  nll/tok {nll:.4f}", flush=True)
    stops = stop_ids(tok, style)
    for ids in texts(tok, style)[1:]:
        t0 = time.time()
        gen = model.generate(ids, max_new_tokens=80, stop_ids=stops)
        print(f"[mlx bf16 greedy] {len(gen)} tok in {time.time() - t0:.1f}s\n{tok.decode(gen)!r}", flush=True)


if __name__ == "__main__":
    mode, d, style, path = sys.argv[1:5]
    (run_torch if mode == "torch" else run_mlx)(d, style, path)
