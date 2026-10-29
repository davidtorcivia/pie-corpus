# Build a blind listening package for the TTS finals: clips cut from the levelled sprites, systems coded A-H.
import csv, json, random, wave, sys
from pathlib import Path
F = Path("/Users/david/AI/PIE/tts/finals"); OUT = Path(sys.argv[1]); KEY = Path(sys.argv[2])
m = json.load(open(F / "manifest.json"))
syss = [s["id"] for s in m["systems"]]
letters = list("ABCDEFGH"); random.Random(20261029).shuffle(syss)
code = dict(zip(syss, letters))
json.dump({"letter_to_system": {v: k for k, v in code.items()}}, open(KEY, "w"), indent=1)
words = {w["id"]: w for w in m["words"]}
order = [w["id"] for w in m["words"]]
clips = {(c["word"], c["system"]): c for c in m["clips"]}
(OUT / "clips").mkdir(parents=True, exist_ok=True)
rows = []
for sid in syss:
    with wave.open(str(F / "audio/sprites" / f"{sid}.wav")) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth(); data = w.readframes(w.getnframes())
    fb = ch * sw
    for n, wid in enumerate(order, 1):
        c = clips[(wid, sid)]; s = round(c["sprite"]["start"] * sr); d = round(c["sprite"]["duration"] * sr)
        d_ = OUT / "clips" / f"{n:02d}_{wid}"; d_.mkdir(exist_ok=True)
        with wave.open(str(d_ / f"{code[sid]}.wav"), "wb") as o:
            o.setnchannels(ch); o.setsampwidth(sw); o.setframerate(sr); o.writeframes(data[s * fb:(s + d) * fb])
with open(OUT / "items.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["n", "item", "kind", "pie", "target_ipa", "english"])
    for n, wid in enumerate(order, 1):
        w = words[wid]; wr.writerow([n, wid, w["kind"], w["pie"], w["ipa"], w.get("english") or w.get("gloss") or ""])
with open(OUT / "ratings.csv", "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["n", "item", "system", "accuracy", "clarity", "naturalness", "overall", "note"])
    for n, wid in enumerate(order, 1):
        for L in letters: wr.writerow([n, wid, L, "", "", "", "", ""])
print(len(order), "items x", len(syss), "systems ->", OUT)
