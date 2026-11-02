"""Re-cut trill contacts into converted audio (after restore.py), on the pie_vtl phone timings: the same tap-train
pie_vtl.patch_trill makes in VTL, applied where the converter smoothed it away. An r's contact count is its
rendered length / TRILL_CYCLE (pie_vtl --trill auto gives 2 or 3 x 40 ms; a tap is ~28 ms and is left alone)."""
import json, sys
import numpy as np, soundfile as sf
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))  # pie_vtl beside this file
import pie_vtl as pv

def retrill(wav_in, timing_json, wav_out):
    a, sr = sf.read(wav_in); a = a if a.ndim == 1 else a.mean(1)
    t = json.load(open(timing_json, encoding="utf-8"))
    timed, n_tr = [], 0
    for w in t["words"]:
        for p in w["phones"]:
            s = pv.Seg(p["phone"][0]); s.syllabic = p["kind"] in ("Rs", "Ns", "Ls")
            if p["phone"] == "r" and p["kind"] == "R":
                n = int(round((p["end"] - p["start"]) / pv.TRILL_CYCLE))
                s.trill = n if n >= 2 else 1; n_tr += s.trill > 1
            timed.append((p["start"], p["end"], s))
    pv.TRILL = "auto"
    out = pv.patch_trill(a, timed, sr=sr) if n_tr else a
    sf.write(wav_out, out, sr, subtype="PCM_16")
    return n_tr

if __name__ == "__main__":
    print(retrill(*sys.argv[1:4]), "trills re-cut")
