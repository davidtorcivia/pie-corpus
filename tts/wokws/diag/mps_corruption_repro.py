"""Repro: on Apple GPUs (MPS), torch <= 2.12 overwrites an unrelated tensor during the BigVGAN generator's backward pass.
Generator forward -> allocate K unrelated tensors filled with 0.123 -> backward -> count changed elements.
torch 2.8.0 / 2.11.0 / 2.12.0: 2,095,744 elements of one tensor change, every run, whatever the tensor size (which one is hit
depends on allocator layout). torch 2.13.0 / 2.15.0 and CPU: none. Needs the BigVGAN clone (BIGVGAN env var).
  [DEV=mps] [N=5242880] [K=8] python mps_corruption_repro.py"""
import os, sys, torch
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import gwerh as G
dev = torch.device(os.environ.get('DEV', 'mps')); torch.manual_seed(0)
gen = G.build().to(dev); x = torch.randn(4, 100, 128, device=dev) - 5
N = int(os.environ.get('N', 5242880)); K = int(os.environ.get('K', 8))
yh = gen(x)
Z = [torch.full((N,), 0.123, device=dev) for _ in range(K)]      # unrelated tensors allocated after the forward
if dev.type == 'mps': torch.mps.synchronize()
yh.backward(torch.randn_like(yh) * 1e-5)
if dev.type == 'mps': torch.mps.synchronize()
bad = [int((z != 0.123).sum()) for z in Z]
print(f'torch {torch.__version__} {dev} N={N} K={K}: changed elements per unrelated tensor {bad}')
