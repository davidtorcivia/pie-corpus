"""Synthesize the corpus v2 validation sentences with a Kokoro model and write, for each clip, the audio and the
predicted word spans (from Kokoro's own per-token durations), so pie/wordscore-style recognizer scoring can judge
each word in its own span. Runs on tr-desktop (WSL):

    cd /mnt/q/AI/PIE/train/kokoro && python synth_eval.py OUT NAME KMODEL.pth VOICE_DIR SPEAKER_MAP

SPEAKER_MAP maps the val list's speaker ids to voicepack names, e.g. "0:pie_zazy,1:pie_valeria,2:pie_antonio,3:pie_w02"
for the new model or "0:pie_m,1:pie_f,2:pie_m,3:pie_f" for the old two-voice one. Writes OUT/NAME/<clip>.wav and
OUT/NAME/spans.jsonl ({"file", "speaker", "voice", "text", "words": [[word, start_s, end_s], ...]}).
"""
import json
import sys
import types
from pathlib import Path

import soundfile as sf
import torch

ROOT = Path.cwd()
_pkg = types.ModuleType("kokoro"); _pkg.__path__ = [str(ROOT / "kokoro" / "kokoro")]
sys.modules["kokoro"] = _pkg
from kokoro.model import KModel  # noqa: E402

SR = 24000
PUNCT = set(".,;:!?—–-\"'()")


def word_index(text, vocab):
    """for each character KModel keeps (those in its vocab), the index of the word it belongs to (None for spaces
    and punctuation); words are the space-separated chunks with punctuation stripped"""
    idx, words, w, cur = [], [], -1, False
    for ch in text:
        if ch not in vocab:
            continue
        if ch == " " or ch in PUNCT:
            idx.append(None); cur = False
            continue
        if not cur:
            w += 1; words.append(""); cur = True
        words[w] += ch
        idx.append(w)
    return idx, words


def main(out, name, kpath, vdir, spkmap):
    out = Path(out) / name
    out.mkdir(parents=True, exist_ok=True)
    spk = {int(a): b for a, b in (x.split(":") for x in spkmap.split(","))}
    model = KModel(config=str(ROOT / "training/config.json"), model=kpath).to("cuda").eval()
    voices = {v: torch.load(Path(vdir) / f"{v}.pt", weights_only=True) for v in set(spk.values())}
    rows = []
    for line in (ROOT / "training/v2_val_list.txt").read_text("utf-8").splitlines():
        if not line.strip():
            continue
        f, text, sid = line.split("|")
        voice = spk[int(sid)]
        ps = text.strip()
        ref = voices[voice][min(len(ps), 509) - 1].to("cuda")
        with torch.no_grad():
            o = model(ps, ref, 1.0, return_output=True)
        audio = o.audio.detach().float().cpu().numpy().squeeze()
        dur = o.pred_dur.numpy().astype(int)              # one per token, including the boundary tokens
        idx, words = word_index(ps, model.vocab)
        assert len(dur) == len(idx) + 2, (f, len(dur), len(idx))
        spf = len(audio) / dur.sum()                      # samples per duration frame
        t = dur[0]
        span = {}
        for k, d in zip(idx, dur[1:-1]):
            if k is not None:
                a, b = span.get(k, (t, t + d))
                span[k] = (min(a, t), t + d)
            t += d
        wl = [[words[k], round(span[k][0] * spf / SR, 4), round(span[k][1] * spf / SR, 4)] for k in sorted(span)]
        sf.write(out / f, audio, SR)
        rows.append({"file": f, "speaker": int(sid), "voice": voice, "text": ps, "words": wl})
    (out / "spans.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), "utf-8")
    print(name, len(rows), "clips")


if __name__ == "__main__":
    main(*sys.argv[1:6])
