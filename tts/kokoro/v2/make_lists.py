import json, sys
sys.path.insert(0, r"Q:\AI\PIE\train\kokoro\training")
from kokoro_symbols import TextCleaner
D = r"Q:\AI\PIE\data\tts-corpus-v2"; T = r"Q:\AI\PIE\train\kokoro\training"
SPK = {"pie_zazy": 0, "pie_valeria": 1, "pie_antonio": 2, "pie_w02": 3}
tc = TextCleaner(); bad = {}
for s in ("train", "val"):
    out = []
    for l in open(fr"{D}\{s}_list.txt", encoding="utf-8"):
        f, lab, spk = l.rstrip("\n").split("|")
        for ch in lab:
            if ch not in tc.word_index_dictionary if hasattr(tc, "word_index_dictionary") else False:
                bad[ch] = bad.get(ch, 0) + 1
        out.append(f"{f}|{lab}|{SPK[spk]}")
    open(fr"{T}\v2_{s}_list.txt", "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print(s, len(out))
json.dump({"speakers": SPK, "note": "corpus v2 (2026-11-08); StyleTTS2 meldataset reads the speaker column as int"}, open(fr"{T}\speakers_v2.json", "w"), indent=1)
print("unmapped symbols:", bad)
import inspect; print(inspect.getsource(TextCleaner)[:600])
