"""Phone recognition for the VC test: facebook/wav2vec2-xlsr-53-espeak-cv-ft (Apache-2.0) @ 2c73378, greedy CTC.

    tts/vc/.venv-eval/bin/python -I tts/vc/recognize.py <wav>...      # prints  path<TAB>phones
Imported by evaluate.py. Weights cached in tts/vc/cache/hf (gitignored); sha256 recorded in the write-up."""
import sys
from pathlib import Path

import librosa
import torch
import json

from huggingface_hub import hf_hub_download
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForCTC

REPO, REV = "facebook/wav2vec2-xlsr-53-espeak-cv-ft", "2c733782da5604684829819a5eb744c193fe9398"
CACHE = Path(__file__).resolve().parent / "cache" / "hf"
_M = {}


def model():
    if not _M:
        # greedy CTC decoded with the model's vocab.json directly: the phoneme tokenizer class would need
        # phonemizer + protobuf only to encode text, which is not needed here
        _M["p"] = Wav2Vec2FeatureExtractor.from_pretrained(REPO, revision=REV, cache_dir=CACHE)
        vocab = json.loads(Path(hf_hub_download(REPO, "vocab.json", revision=REV, cache_dir=CACHE)).read_text())
        _M["v"] = {i: t for t, i in vocab.items()}
        _M["m"] = Wav2Vec2ForCTC.from_pretrained(REPO, revision=REV, cache_dir=CACHE).eval()
    return _M["p"], _M["m"]


def logits(wav: str):
    """CTC logits, frames x vocab (20 ms frames)."""
    p, m = model()
    x, _ = librosa.load(wav, sr=16000)
    with torch.no_grad():
        return m(p(x, sampling_rate=16000, return_tensors="pt").input_values).logits[0].numpy()


def decode(lg) -> list[str]:
    ids, out, prev = lg.argmax(-1).tolist(), [], None
    for i in ids:
        if i != prev:
            t = _M["v"][i]
            if not t.startswith("<") and t not in ("|", " "):
                out.append(t)
        prev = i
    return out


def phones(wav: str) -> list[str]:
    return decode(logits(wav))


if __name__ == "__main__":
    for w in sys.argv[1:]:
        print(w, " ".join(phones(w)), sep="\t", flush=True)
