"""Windows-native drop-in for the Cython `monotonic_align` (resemble-ai fork of VITS's): the same functions, compiled
with numba instead of Cython (no C compiler needed). Only the 1-step topology StyleTTS2 uses."""
from .mas import mask_from_len, mask_from_lens, maximum_path  # noqa: F401
