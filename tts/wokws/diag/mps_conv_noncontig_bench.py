"""MPS conv1d backward with a contiguous vs a non-contiguous grad_output (same values). M3 Ultra, torch 2.8 and 2.15: ~7.6 ms vs ~810 ms; CPU ~1.7 ms either way. (The first timing of each kind includes warm-up.)"""
import os, time, torch, torch.nn.functional as F
dev = torch.device(os.environ.get('DEV', 'mps')); torch.manual_seed(0)
K = torch.randn(48, 1, 1024, device=dev); L, hop = 113920, 256
def S(): torch.mps.synchronize() if dev.type == 'mps' else None
def run(contig):
    x = torch.randn(4, 1, L, device=dev).requires_grad_(True); y = F.conv1d(x, K, stride=hop)
    g = torch.randn(*y.shape, 2, device=dev)[..., 0]          # non-contiguous view, stride (.., .., 2)
    if contig: g = g.contiguous()
    S(); t = time.time(); y.backward(g); S(); return time.time() - t, x.grad
for c in (True, False, True, False):
    dt, gx = run(c); print(f'{dev} grad_output contiguous={c}: conv1d input-grad {dt * 1000:8.1f} ms')
torch.manual_seed(1); x = torch.randn(4, 1, L, device=dev).requires_grad_(True); y = F.conv1d(x, K, stride=hop)
g = torch.randn(*y.shape, 2, device=dev)[..., 0]
a, = torch.autograd.grad(y, x, g, retain_graph=True); b, = torch.autograd.grad(y, x, g.contiguous())
print('same result:', float((a - b).abs().max()))
