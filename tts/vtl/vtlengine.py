"""One interface over two VocalTractLab engines.

  * "pip"  — vocaltractlab-cython (VTL API 2.4.2 backend). Speakers with the classic
             "Geometric glottis" model: JD3, JD3-PIE.
  * "2.4"  — the VTL 2.4 release API, driven through ctypes. Speakers with the
             "Geometric glottis 2025" model: W02 (female), M01 (male), and their PIE builds.
             Library: VocalTractLabApi.dll from the VTL 2.4 zip on Windows, or libvtl24.so
             built with build_vtl24.sh on Linux/macOS. Override with $VTL24_LIB.

The engine is picked from the speaker file. All audio is returned at 44.1 kHz.
"""
import ctypes, os, re, sys
import numpy as np

SR_OUT = 44100
HERE = os.path.dirname(os.path.abspath(__file__))


def engine_kind(speaker_path):
    head = open(speaker_path, encoding="utf-8").read()
    return "2.4" if 'type="Geometric glottis 2025"' in head else "pip"


def _ges_duration(ges_path):
    txt = open(ges_path, encoding="utf-8").read()
    best = 0.0
    for body in re.findall(r"<gesture_sequence[^>]*>(.*?)</gesture_sequence>", txt, re.S):
        best = max(best, sum(float(d) for d in re.findall(r'duration_s="([^"]+)"', body)))
    return best


def _resample(x, sr_in):
    if sr_in == SR_OUT:
        return x
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(SR_OUT, sr_in)
    return resample_poly(x, SR_OUT // g, sr_in // g)


class PipEngine:
    kind = "pip"

    def __init__(self, speaker):
        import vocaltractlab_cython as v
        self.v = v
        v.VocalTractLabApi._close()
        v.VocalTractLabApi._initialize(speaker)
        self.sr = 44100

    def shape(self, name):
        return np.asarray(self.v.get_shape(name, "tract"), dtype=float)

    def tube_area(self, params):
        return np.asarray(self.v.tract_state_to_tube_state(np.asarray(params, float))["tube_area"]).ravel()

    def ges_to_audio(self, ges_path):
        return np.asarray(self.v.gesture_file_to_audio(ges_path), dtype=float)

    def transfer(self, params, n=4096):
        """Glottis-to-lips volume-velocity transfer magnitude: (freqs Hz, magnitude), 0..sr/2."""
        r = self.v.tract_state_to_transfer_function(np.asarray(params, float), n_spectrum_samples=n)
        mag = np.asarray(r["magnitude_spectrum"], dtype=float)[: n // 2 + 1]
        return np.arange(len(mag)) * self.sr / n, mag

    def close(self):
        pass        # the pip module closes itself at exit; re-initialising replaces the speaker


class Vtl24Engine:
    kind = "2.4"
    _lib = None
    _open = False

    @classmethod
    def library(cls):
        if cls._lib is None:
            cands = [os.environ.get("VTL24_LIB", "")]
            names = ["VocalTractLabApi.dll"] if sys.platform.startswith("win") else ["libvtl24.so", "libvtl24.dylib"]
            for d in (HERE, os.path.join(HERE, "linux"), os.path.join(HERE, "vtl24"), os.getcwd()):
                cands += [os.path.join(d, n) for n in names]
            path = next((c for c in cands if c and os.path.exists(c)), None)
            if path is None:
                raise SystemExit("VTL 2.4 library not found: put VocalTractLabApi.dll (Windows, from VTL2.4.zip) "
                                 "or libvtl24.so (build_vtl24.sh) next to vtlengine.py, or set VTL24_LIB.")
            if sys.platform.startswith("win"):
                os.add_dll_directory(os.path.dirname(path))       # msvcp140/vcruntime140 from the zip
            cls._lib = ctypes.CDLL(path)
        return cls._lib

    def __init__(self, speaker):
        L = self.library()
        if Vtl24Engine._open:
            L.vtlClose()
        if L.vtlInitialize(os.path.abspath(speaker).encode()) != 0:
            raise SystemExit(f"VTL 2.4 could not load {speaker}")
        sr, nt, nv, ng = (ctypes.c_int() for _ in range(4))
        L.vtlGetConstants(ctypes.byref(sr), ctypes.byref(nt), ctypes.byref(nv), ctypes.byref(ng))
        self.L, self.sr, self.n_tube, self.n_tract = L, sr.value, nt.value, nv.value
        Vtl24Engine._open = True

    def shape(self, name):
        p = (ctypes.c_double * self.n_tract)()
        if self.L.vtlGetTractParams(name.encode(), p) != 0:
            raise KeyError(name)
        return np.array(p[:], dtype=float)

    def tube_area(self, params):
        n = self.n_tube
        tp = (ctypes.c_double * self.n_tract)(*np.asarray(params, float))
        length, area = (ctypes.c_double * n)(), (ctypes.c_double * n)()
        art = (ctypes.c_int * n)()
        inc, tts, vel = ctypes.c_double(), ctypes.c_double(), ctypes.c_double()
        self.L.vtlTractToTube(tp, length, area, art, ctypes.byref(inc), ctypes.byref(tts), ctypes.byref(vel))
        return np.array(area[:], dtype=float)

    def ges_to_audio(self, ges_path):
        n_max = int((_ges_duration(ges_path) + 1.0) * self.sr)
        buf = (ctypes.c_double * n_max)()
        n = ctypes.c_int(0)
        r = self.L.vtlGesturalScoreToAudio(os.path.abspath(ges_path).encode(), b"", b"", buf,
                                           ctypes.byref(n), 0, 0)
        if r != 0:
            raise SystemExit(f"VTL 2.4 synthesis failed ({r}) for {ges_path}")
        return _resample(np.array(buf[:n.value], dtype=float), self.sr)

    def transfer(self, params, n=4096):
        """Glottis-to-lips volume-velocity transfer magnitude: (freqs Hz, magnitude), 0..sr/2."""
        tp = (ctypes.c_double * self.n_tract)(*np.asarray(params, float))
        mag, ph = (ctypes.c_double * n)(), (ctypes.c_double * n)()
        self.L.vtlGetTransferFunction(tp, n, mag, ph)
        m = np.array(mag[:], dtype=float)[: n // 2 + 1]
        return np.arange(len(m)) * self.sr / n, m

    def close(self):
        if Vtl24Engine._open:
            self.L.vtlClose(); Vtl24Engine._open = False


def open_engine(speaker):
    return Vtl24Engine(speaker) if engine_kind(speaker) == "2.4" else PipEngine(speaker)
