"""Speed fixes for training gʷerh on Apple GPUs (MPS). Each one leaves the maths unchanged.
1. nnAudio's CQT stacks real/imaginary conv outputs with torch.stack(..., -1), so the gradient reaching each conv1d is a
   strided (non-contiguous) view, and MPS conv1d backward with a non-contiguous grad_output is ~100x slower (measured
   2026-11-15, M3 Ultra, torch 2.8 and 2.15: 810 ms vs 7.6 ms for one CQT octave; CPU 1.7 ms either way). We wrap the
   conv outputs in an identity whose backward makes the gradient contiguous. nnAudio stays unedited: we replace the
   helper it looks up (nnAudio.features.cqt.get_cqt_complex) with an equivalent that adds the wrapper.
2. (in gwerh_train.py) PhaseAug.forward_sync concatenates real and generated audio, so in the generator pass the real
   branch also carries a gradient and the CQT discriminator computes an unused input gradient for it; the real branch
   is detached there (identical generator gradients). PhaseAug itself is cheap (~2 ms); its apparent cost was this."""
import torch
from torch.nn.functional import conv1d


class ContiguousGrad(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x): return x.view_as(x)
    @staticmethod
    def backward(ctx, g): return g.contiguous()


def get_cqt_complex(x, cqt_kernels_real, cqt_kernels_imag, hop_length, padding):
    """nnAudio.utils.get_cqt_complex (nnAudio 0.3.4), plus ContiguousGrad on the two conv outputs."""
    try:
        x = padding(x)
    except Exception:
        x = torch.nn.functional.pad(x, (cqt_kernels_real.shape[-1] // 2, cqt_kernels_real.shape[-1] // 2))
    CQT_real = ContiguousGrad.apply(conv1d(x, cqt_kernels_real, stride=hop_length))
    CQT_imag = -ContiguousGrad.apply(conv1d(x, cqt_kernels_imag, stride=hop_length))
    return torch.stack((CQT_real, CQT_imag), -1)


def apply():
    import nnAudio.features.cqt as C, nnAudio.utils as U, inspect
    src = inspect.getsource(U.get_cqt_complex)
    assert 'conv1d(x, cqt_kernels_real, stride=hop_length)' in src and 'torch.stack((CQT_real, CQT_imag), -1)' in src, \
        'nnAudio get_cqt_complex changed; re-check mps_fixes'
    C.get_cqt_complex = get_cqt_complex


def contiguous_conv_grads(*modules):
    """Forward hook on every Conv/ConvTranspose (1-D and 2-D) so the gradient reaching it is contiguous (a no-op copy
    when it already is). Same values; avoids the slow MPS convolution-backward path for strided gradients."""
    kinds = (torch.nn.Conv1d, torch.nn.Conv2d, torch.nn.ConvTranspose1d, torch.nn.ConvTranspose2d)
    n = 0
    for m in modules:
        for sub in m.modules():
            if isinstance(sub, kinds):
                sub.register_forward_hook(lambda mod, inp, out: ContiguousGrad.apply(out)); n += 1
    return n
