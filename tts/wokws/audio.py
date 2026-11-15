"""The one spectrogram format of the wokʷs line, shared by the converter (wokʷs) and our vocoder (gʷerh).

It is numerically the GPT-SoVITS v4 vocoder's input (so v4 can stand in until gʷerh is trained):
audio at 32 kHz, |STFT| with n_fft = win = 1280 (Hann), hop 320 (100 frames/s), reflect-padded by 480 on each side,
no centering; 100 librosa (Slaney) mel bands 0-16 kHz; natural log, clamped at 1e-5. Frame i covers 32 kHz samples
[320 i, 320 i + 320) at its centre (+160), so N frames <-> exactly 320 N samples (441 N at 44.1 kHz)."""
import functools
import torch

SR, N_FFT, HOP, N_MELS = 32000, 1280, 320, 100
OUT_SR, OUT_HOP = 44100, 441          # gʷerh's output rate; paid is native 44.1 kHz


@functools.lru_cache(maxsize=None)
def _basis(device, dtype):
    import librosa
    return torch.from_numpy(librosa.filters.mel(sr=SR, n_fft=N_FFT, n_mels=N_MELS, fmin=0, fmax=None)).to(device, dtype)


@functools.lru_cache(maxsize=None)
def _window(device, dtype):
    return torch.hann_window(N_FFT, device=device, dtype=dtype)


def mel(y):
    """y [B, T] or [T] float audio at 32 kHz -> log-mel [B, T // 320, 100] (or [T // 320, 100])."""
    one = y.ndim == 1
    y = y[None] if one else y
    p = (N_FFT - HOP) // 2
    y = torch.nn.functional.pad(y[:, None], (p, p), mode='reflect')[:, 0]
    s = torch.stft(y, N_FFT, hop_length=HOP, win_length=N_FFT, window=_window(y.device, y.dtype), center=False,
                   normalized=False, onesided=True, return_complex=True)
    m = torch.sqrt(s.real ** 2 + s.imag ** 2 + 1e-8)
    m = torch.log(torch.clamp(_basis(y.device, y.dtype) @ m, min=1e-5)).transpose(1, 2)
    return m[0] if one else m
