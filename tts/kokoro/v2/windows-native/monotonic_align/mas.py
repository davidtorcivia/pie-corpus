import numpy as np
import torch
from .core import maximum_path_c


def mask_from_len(lens: torch.Tensor, max_len=None):
    if max_len is None:
        max_len = lens.max()
    index = torch.arange(max_len).to(lens).view(1, -1)
    return index < lens.unsqueeze(1)


def mask_from_lens(similarity: torch.Tensor, symbol_lens: torch.Tensor, mel_lens: torch.Tensor):
    _, S, T = similarity.size()
    mask_S = mask_from_len(symbol_lens, S)
    mask_T = mask_from_len(mel_lens, T)
    return (mask_S.unsqueeze(2) * mask_T.unsqueeze(1)).to(similarity)


def maximum_path(value: torch.Tensor, mask: torch.Tensor = None, topology: str = "1-step", output_scores: bool = False):
    if topology != "1-step":
        raise NotImplementedError("only the 1-step topology is ported")
    if mask is None:
        mask = torch.ones_like(value)
    device, dtype = value.device, value.dtype
    value = (value * mask).data.cpu().numpy().astype(np.float32)
    mask = mask.data.cpu().numpy()
    path = np.zeros_like(value).astype(np.int32)
    t_x_max = mask.sum(1)[:, 0].astype(np.int32)
    t_y_max = mask.sum(2)[:, 0].astype(np.int32)
    maximum_path_c(path, value, t_x_max, t_y_max)
    path = torch.from_numpy(path).to(device=device, dtype=dtype)
    if output_scores:
        return path, torch.from_numpy(value).to(device=device, dtype=dtype)
    return path
