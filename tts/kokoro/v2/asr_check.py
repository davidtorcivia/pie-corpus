"""PIE_ASR_COMPILE equivalence + speed: the trained aligner, a real-sized batch, eager vs compiled step,
forward outputs and parameter gradients"""
import os, sys, time, torch, yaml
_l = torch.load; torch.load = lambda *a, **k: _l(*a, **{**k, "weights_only": False})   # the trainer does the same
sys.path.insert(0, "/mnt/q/AI/PIE/train/kokoro/StyleTTS2"); os.chdir("/mnt/q/AI/PIE/train/kokoro/StyleTTS2")
from models import load_ASR_models
torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
m = load_ASR_models("Utils/ASR/epoch_00080.pth", "Utils/ASR/config.yml").cuda().train()
B, L, T = 4, 1200, 110
torch.manual_seed(0)
mels = torch.randn(B, 80, L, device="cuda"); lens = torch.tensor([L, L - 200, L - 400, 700], device="cuda")
texts = torch.randint(4, 150, (B, T), device="cuda")
n_down = m.n_down
mask = (torch.arange(L // 2 ** n_down, device="cuda")[None] >= (lens // 2 ** n_down)[:, None])
def run(fast):
    os.environ["PIE_ASR_COMPILE"] = "1" if fast else "0"
    torch.manual_seed(1); torch.cuda.manual_seed(1)
    m.zero_grad()
    ppgs, s2s_pred, s2s_attn = m(mels, mask, texts)
    loss = s2s_pred.float().pow(2).mean() + s2s_attn.pow(2).sum() * 1e-3 + ppgs.pow(2).mean()
    loss.backward()
    return s2s_pred.detach(), s2s_attn.detach(), {n: p.grad.detach().clone() for n, p in m.named_parameters() if p.grad is not None}
a = run(False); b = run(True)
print("max |d pred|", (a[0] - b[0]).abs().max().item(), " max |d attn|", (a[1] - b[1]).abs().max().item())
print("max rel grad diff", max(((a[2][k] - b[2][k]).norm() / (a[2][k].norm() + 1e-12)).item() for k in a[2]))
for fast in (False, True):
    for _ in range(2): run(fast)
    torch.cuda.synchronize(); t = time.time()
    for _ in range(5): run(fast)
    torch.cuda.synchronize(); print("compiled" if fast else "eager", round((time.time() - t) / 5, 3), "s fwd+bwd", torch.cuda.max_memory_allocated() / 2**30)
    torch.cuda.reset_peak_memory_stats()
