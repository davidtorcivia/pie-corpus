"""How each word ends: how fast its last nucleus dies away, and how deep the dip into the next word is.

    tts/vc/.venv-eval/bin/python -I tts/cadence/vtl_ends.py <phones.json> name=file.wav [name=file.mp3 ...]

decay: ms from 10 dB to 30 dB under the last nucleus's peak. A hard cut is ~10–25 ms; a phrase trailing off is ~100 ms or
more. dip: the lowest level between this word and the next, re that peak (only for gaps under 200 ms). Files whose name
starts with "el" are taken as 5 ms late (the ElevenLabs offset)."""
import json, sys
import librosa, numpy as np
SR=22050; J=json.load(open(sys.argv[1])); hop=55  # 2.5 ms
files=[(k,librosa.load(p,sr=SR)[0]) for k,p in (x.split("=",1) for x in sys.argv[2:])]
W=J["words"]
def db(y): return 20*np.log10(librosa.feature.rms(y=y,frame_length=220,hop_length=hop,center=True)[0]+1e-6)
E={k:db(y) for k,y in files}
print(f"{'word':16s} gap  " + "  ".join(f"{k:>18s}" for k,_ in files)); print(" "*22+"  ".join(f"{'decay10→30ms  dip':>18s}" for _ in files))
for i,w in enumerate(W):
    nxt=W[i+1]["start"] if i+1<len(W) else w["end"]+1; gap=nxt-w["end"]
    nucs=[p for p in w["phones"] if p["kind"] in ("V","Ns","Ls","Rs")]
    if not nucs: continue
    v=nucs[-1]; row=[]
    for k,_ in files:
        e=E[k]; lag=-0.005 if k.startswith("el") else 0
        f=lambda t:int((t-lag)*SR/hop)
        peak=e[f(v["start"]):f(v["end"])].max()
        seg=e[f(v["start"]):f(min(nxt,w["end"]+0.4))]
        pk=np.argmax(seg); after=seg[pk:]
        t10=np.argmax(after<peak-10); t30=np.argmax(after<peak-30)
        dec=(t30-t10)*hop/SR*1000 if t30>0 else float('nan')
        dip=e[f(w["end"]-0.01):f(nxt+0.01)].min()-peak if gap<0.2 else float('nan')
        row.append(f"{dec:8.0f} {dip:+7.0f}dB")
    print(f"{w['word']:16s} {gap*1000:4.0f}  "+"  ".join(f"{r:>18s}" for r in row))
