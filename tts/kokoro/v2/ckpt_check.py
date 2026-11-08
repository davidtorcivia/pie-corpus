"""checkpoint_modules is exact: the Stage 1 decoder (random F0/N smoothing) with and without checkpointing, same seeds:
outputs and parameter gradients must match"""
import os, sys, random, numpy as np, torch, yaml
sys.path.insert(0, "/mnt/q/AI/PIE/train/kokoro/StyleTTS2"); os.chdir("/mnt/q/AI/PIE/train/kokoro/StyleTTS2")
_l = torch.load; torch.load = lambda *a, **k: _l(*a, **{**k, "weights_only": False})
from munch import Munch
from models import build_model, load_ASR_models, load_F0_models
from utils import recursive_munch
from Utils.PLBERT.util import load_plbert
import pie_run
torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
torch.backends.cudnn.deterministic = True
cfg = yaml.safe_load(open("/mnt/q/AI/PIE/train/kokoro/configs/v2l_stage1.yml"))
mp = recursive_munch(cfg["model_params"])
model = build_model(mp, load_ASR_models(cfg["ASR_path"], cfg["ASR_config"]), load_F0_models(cfg["F0_path"]), load_plbert(cfg["PLBERT_dir"]))
dec = model.decoder.cuda().train()
B, T = 2, 100
torch.manual_seed(0)
asr = torch.randn(B, 512, T, device="cuda"); F0 = torch.rand(B, T * 2, device="cuda") * 200; N = torch.randn(B, T * 2, device="cuda"); s = torch.randn(B, 128, device="cuda")
def run():
    random.seed(5); np.random.seed(5); torch.manual_seed(5); torch.cuda.manual_seed(5)
    dec.zero_grad()
    y = dec(asr, F0, N, s)
    (y.pow(2).mean()).backward()
    return y.detach(), {n: p.grad.detach().clone() for n, p in dec.named_parameters() if p.grad is not None}, random.random()
a = run()
pie_run.checkpoint_modules({"decoder": dec}, ["decoder"])
b = run()
print("max |dy|", (a[0] - b[0]).abs().max().item(), " max rel grad diff",
      max(((a[1][k] - b[1][k]).norm() / (a[1][k].norm() + 1e-12)).item() for k in a[1]), " python RNG after equal:", a[2] == b[2])
