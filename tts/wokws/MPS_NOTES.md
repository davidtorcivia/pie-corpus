# gʷerh on Apple GPUs (MPS)

*2026-11-15. Apple M3 Ultra (256 GB), macOS 26.6.2, Python 3.11.*

## 1. PyTorch bug: the backward pass corrupts unrelated memory (fixed in 2.13)

**Symptom.** gʷerh (BigVGAN generator, MPD and CQT discriminators) went NaN at step 2 on the Mac GPU and trained normally on the CPU.

**Trace.**
- One MPD weight's AdamW second moment (`exp_avg_sq`) held negative values, down to −2.5e-05. That is impossible for a running average of squared gradients, and its square root is NaN.
- Both AdamW updates were correct when redone on the CPU. But 297,472 of the state's 5,242,880 values changed *between* the updates, during the generator's backward pass, which never touches that tensor.
- Minimal repro (`diag/mps_corruption_repro.py`): run the generator forward, allocate unrelated tensors filled with 0.123, run the backward pass. 2,095,744 values of one tensor change on every run.

**Verified.**

| Check | Result |
|---|---|
| torch 2.8.0, 2.11.0, 2.12.0 on the Mac GPU | Corrupt |
| torch 2.13.0, 2.15.0 on the Mac GPU | Clean |
| CPU | Clean |
| Unrelated-tensor sizes 0.26M–16.8M, up to 64 tensors | Same result |
| Unsafe ops in BigVGAN (`as_strided`, `.data` writes) | None |
| Real training on 2.15.0, 100 steps | All finite |

Metal shader validation reports nothing. The exact kernel is not pinned down: the bug needs the whole generator graph to trigger.

**Our side.** `gwerh_train.py` refuses torch ≤ 2.12 on the Mac GPU.

## 2. Slowdown: conv1d backward with a strided gradient (still present in 2.15)

On the Mac GPU, conv1d's input gradient takes 810 ms when the incoming gradient is a strided view and 7.6 ms when it is contiguous, with the same result. On the CPU both take 1.7 ms. Benchmark: `diag/mps_conv_noncontig_bench.py`.

nnAudio's CQT creates exactly this case with `torch.stack(..., -1)`. PhaseAug's `forward_sync` adds an unused input gradient for the real audio on top.

**Fixes** (identical maths; nnAudio and BigVGAN unedited):
- `mps_fixes.apply()` makes the gradients reaching the CQT convolutions contiguous.
- The real branch is detached in the generator pass.

| Batch-4 step, torch 2.15.0 | Seconds |
|---|---|
| No changes | 10.4 |
| Real branch detached | 6.9 |
| Contiguous CQT gradients | 3.55 |
| Both | 3.44 |

**Measured but not adopted:**
- bf16 mixed precision: 15–25% faster.
- `torch.compile`: ~10% faster.
- Batch 8 or 16: no gain.
- Rewriting PhaseAug's STFT: no gain (it costs 2–3 ms).
