"""The PIE speech corpus for the Kokoro fine-tune: clips, timelines, labels, filenames.

One clip is one to a few sentences of a corpus record (or, for verse, a few consecutive lines of a work), spoken
by each of two VocalTractLab voices (tts/vtl, v10: JD3-PIE male, W02-PIE female), re-voiced by ElevenLabs
speech-to-speech and repaired by tts/cadence/restore.py, the chain the owner locked on 2026-10-30
(docs/research/tts-voice-conversion.md). This module is text only: it never renders.

Single source of truth for the phones: every word's IPA is `pie.ipa.to_ipa(word)`. The same string is
  - the `ipa` field of the timeline JSON that pie_vtl.py renders (checked: identical on the hard test), and
  - after `kokoro_label`, the training label and the inference input of the fine-tuned Kokoro.
So the model is trained on exactly the alphabet it is later sent.

Label convention (`kokoro_label`): NFD; syllable dots dropped (Kokoro's "." is the sentence stop); clitic hyphens
dropped (h₃ésth₁-kʷe is one phonological word); words joined by one space; the source punctuation kept, and a
pause the timeline makes without punctuation (the verse caesura and line ends) written as "," / ".". Kokoro's
178-id vocab has no ʱ ʷ ̩ or acute; they get unused ids (KOKORO_EXTRA), declared for the recipe's symbol table.

Timing: prose and dialogue use pie_vtl's own rule-based durations (its text mode), with a pause at each
sentence and comma; verse records that scan (`meter.exact`) use the recitation cadence of tts/cadence/cadence.py
(moras, caesura, line ends) computed from the syllable weights alone, without eSpeak. cadence.py stretches eSpeak's
word to the mora target, clamped to 0.7-1.7x, so the two agree except where that clamp bit.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from pie.ipa import to_ipa
from pie.meter import line_syllables, weights, words as meter_words

ROOT = Path(__file__).resolve().parents[1]
VTL_DIR = ROOT / "tts" / "vtl"
KOKORO_VOCAB: dict[str, int] = json.loads((ROOT / "tts/kokoro/vocab.json").read_text("utf-8"))["vocab"]
# New symbols on ids the shipped Kokoro vocab leaves unused (7, 8, 26, 27 are free; tts-options.md §4.3)
KOKORO_EXTRA = {"ʱ": 7, "ʷ": 8, "̩": 26, "́": 27}
LABEL_VOCAB = {**KOKORO_VOCAB, **KOKORO_EXTRA}
assert not set(KOKORO_EXTRA) & set(KOKORO_VOCAB) and not set(KOKORO_EXTRA.values()) & set(KOKORO_VOCAB.values())

# VTL speaker file -> Kokoro speaker name (the recipe's third column; one Stage-2 voice each)
SPEAKERS = {"JD3-PIE": "pie_m", "W02-PIE": "pie_f"}
VERSE_PAUSE = {"caesura": 0.24, "line": 0.70, "end": 0.9}      # cadence.py CAESURA, LINE, END
MORA, CAESURA_LEN, FINAL_LEN, FINAL_H = 0.165, 1.12, 1.35, 0.06  # cadence.py
PROSE_COMMA, EDGE = 0.25, 0.30               # s: pause at "," (a caesura: < 0.5 s); lead-in/out
STOP_RANGE = (0.55, 0.75)                    # s: pause between sentences (pie_vtl "line" phrase end: >= 0.5 s)
RATE_RANGE = (0.93, 1.07)                    # per-clip speaking rate
MAX_CLIP_S, MIN_CLIP_S = 15.0, 1.5
SENT_END = re.compile(r"(?<=[.?!])\s+")
PUNCT = ".,?!;:"


class LabelError(ValueError):
    pass


def _pie_vtl():
    if str(VTL_DIR) not in sys.path:
        sys.path.insert(0, str(VTL_DIR))
    import pie_vtl
    return pie_vtl


def word_ipa(word: str) -> str:
    """The IPA of one written PIE word (punctuation stripped), as pie_vtl.py consumes it. A scholar's optional
    segment in brackets (Tier 1: Hamp's éwel(e)t, Adams' (h₁é)) is read as spoken: the brackets are dropped."""
    return unicodedata.normalize("NFC", to_ipa(word.strip(PUNCT + "\"“”").replace("(", "").replace(")", "")))


def kokoro_word(ipa: str) -> str:
    return unicodedata.normalize("NFD", ipa).replace(".", "").replace("-", "").replace("g", "ɡ")


def kokoro_label(words: list[dict]) -> str:
    """Words [{ipa, punct}] -> the Kokoro label; every symbol checked against LABEL_VOCAB."""
    out = []
    for w in words:
        out.append(kokoro_word(w["ipa"]) + w.get("punct", ""))
    s = " ".join(out)
    bad = sorted({c for c in s if c not in LABEL_VOCAB})
    if bad:
        raise LabelError(f"symbols outside the Kokoro label vocab: {bad} in {s!r}")
    return s


def text_label(pie: str) -> str:
    """The label for plain PIE text, the way inference will build it: words + their own punctuation."""
    ws = []
    for tok in pie.split():
        core = tok.strip(PUNCT + "\"“”()")
        if not core:
            continue
        p = tok.rstrip("\"“”()")
        p = p[len(p.rstrip(PUNCT)):]
        ws.append({"ipa": word_ipa(core), "punct": p[-1:] if p else ""})
    return kokoro_label(ws)


@dataclass
class Clip:
    id: str
    records: list[str]
    genre: str
    verse: bool
    pie: str
    english: str
    words: list[dict] = field(default_factory=list)   # {line, word, ipa, punct, start, end, pause_after}

    @property
    def duration(self) -> float:
        return self.words[-1]["end"] + self.words[-1]["pause_after"] if self.words else 0.0

    @property
    def label(self) -> str:
        return kokoro_label(self.words)

    def timeline(self) -> list[dict]:
        """pie_vtl.py --timeline / --batch input (cadence JSON format)."""
        keys = ("line", "word", "ipa", "start", "end", "pause_after", "rise")
        return [{k: w[k] for k in keys if k in w} for w in self.words]


def _tokens(pie: str) -> list[tuple[str, str]]:
    out = []
    for tok in pie.split():
        core = tok.strip(PUNCT + "\"“”()")
        if core:
            p = tok.rstrip("\"“”()")
            p = p[len(p.rstrip(PUNCT)):]
            out.append((core, p[-1:] if p else ""))
    return out


def _unit(key: str) -> float:
    return int(hashlib.sha1(key.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def prose_words(pie: str, key: str = "") -> list[dict]:
    """Prose timing on pie_vtl's own phone durations (its text-mode rules: accented vowels ×1.2, the last nucleus
    of a sentence ×1.45). Intonation units, owner 2026-11-02 ("clip timing right so sentences sound correct and
    have a proper cadence"):
      - a sentence is one pitch line (declination across it, the final fall on its last word);
      - a comma / ; / : is a level pause inside the line, as the verse caesura (pie_vtl's caesura phrase end),
        with the caesura's 1.12× pre-pause lengthening;
      - a question rises through its last word (pie_vtl v10.1 "rise"; cf. Vedic pluti), lengthened ×1.15;
      - tempo: one rate per clip in RATE_RANGE and sentence pauses in STOP_RANGE, drawn from the clip key."""
    pv = _pie_vtl()
    toks = _tokens(pie)
    rate = RATE_RANGE[0] + (RATE_RANGE[1] - RATE_RANGE[0]) * _unit(f"rate|{key}|{pie}")
    words, line, t = [], 1, EDGE
    for i, (core, p) in enumerate(toks):
        last = i == len(toks) - 1
        p = p or ("." if last else "")
        ipa = word_ipa(core)
        segs = pv.parse_word(ipa)
        if len(segs) > 1 and segs[-1].base == "h" and pv.is_nucleus(segs[-2]):
            segs[-1].final_h = True
        stop = bool(p) and p in ".?!"
        d = sum(pv.default_durations(segs, stop)) / rate
        if p and p in ",;:":
            d *= CAESURA_LEN
        if p == "?":
            d *= 1.15
        if last:
            gap = EDGE
        elif stop:
            gap = STOP_RANGE[0] + (STOP_RANGE[1] - STOP_RANGE[0]) * _unit(f"stop|{key}|{i}|{pie}")
        else:
            gap = PROSE_COMMA if p else 0.0
        w = {"line": line, "word": core, "ipa": ipa, "punct": p, "start": round(t, 4), "end": round(t + d, 4),
             "pause_after": round(gap, 3)}
        if p == "?":
            w["rise"] = True
        words.append(w)
        t = w["end"] + w["pause_after"]
        if stop:
            line += 1
    return words


def verse_words(lines: list[str]) -> list[dict]:
    """cadence.py's recitation timing from the weights: mora durations, caesura after syllable 5 (11) / 4 (8)."""
    words, t = [], EDGE
    for li, line in enumerate(lines):
        toks, syl, wt = _tokens(line), line_syllables(line), weights(line.rstrip(PUNCT))
        if [c for c, _ in toks] != [w.strip(PUNCT) for w in meter_words(line)] or sum(syl) != len(wt):
            raise ValueError(f"cannot time verse line {line!r}")
        n = len(wt)
        cut = 5 if n >= 10 else 4
        pos = 0
        for wi, ((core, p), k) in enumerate(zip(toks, syl)):
            ipa = word_ipa(core)
            target = MORA * sum(2 if x == "H" else 1 for x in wt[pos:pos + k])
            last = wi == len(toks) - 1
            caes = pos < cut <= pos + k and not last
            target *= FINAL_LEN if last else CAESURA_LEN if caes else 1
            target += FINAL_H if ipa.endswith("h") else 0
            gap = (VERSE_PAUSE["end"] if li == len(lines) - 1 else VERSE_PAUSE["line"]) if last else \
                VERSE_PAUSE["caesura"] if caes else 0.0
            punct = p or ("." if last else "," if caes else "")
            words.append({"line": li + 1, "word": core, "ipa": ipa, "punct": punct, "start": round(t, 4),
                          "end": round(t + target, 4), "pause_after": gap})
            t += target + gap
            pos += k
    return words


def is_verse(r: dict) -> bool:
    m = r.get("meter") or {}
    return bool(m.get("exact")) and m.get("fit") == 1


def sentences(pie: str) -> list[str]:
    return [s.strip() for s in SENT_END.split(pie.strip()) if s.strip()]


def clips_for_work(recs: list[dict]) -> list[Clip]:
    """Records of one work, in order -> clips, each inside one record. Verse (a record that scans): up to 4 of its
    lines per clip; prose: its sentences, grouped while the clip stays within MAX_CLIP_S. A single sentence
    longer than that stays one clip (the recipe takes 2-30 s)."""
    out: list[Clip] = []
    i = 0
    while i < len(recs):
        r = recs[i]
        if is_verse(r):                             # a verse record's lines are its sentences (pie.meter.verse_lines)
            lines = sentences(r["pie"])
            k, part = 0, 0
            while k < len(lines):
                take = 1
                while k + take < len(lines) and take < 4 and \
                        verse_words(lines[k:k + take + 1])[-1]["end"] + 1 <= MAX_CLIP_S:
                    take += 1
                ws = verse_words(lines[k:k + take])
                out.append(Clip(f"{r['id']}-v{part:02d}", [r["id"]], r.get("genre") or "", True,
                                " ".join(lines[k:k + take]),
                                r.get("english") or "" if (k == 0 and take == len(lines)) else "", ws))
                k += take
                part += 1
            i += 1
            continue
        sents, k, part = sentences(r["pie"]), 0, 0
        while k < len(sents):
            take = 1
            cid = f"{r['id']}-p{part:02d}"
            while k + take < len(sents) and \
                    prose_words(" ".join(sents[k:k + take + 1]), cid)[-1]["end"] + EDGE <= MAX_CLIP_S:
                take += 1
            text = " ".join(sents[k:k + take])
            ws = prose_words(text, cid)
            out.append(Clip(cid, [r["id"]], r.get("genre") or "", False, text,
                            r.get("english") or "" if (k == 0 and take == len(sents)) else "", ws))
            k += take
            part += 1
        i += 1
    return out


def split_of(clip: Clip, work_id: str, val_share: float = 0.05) -> str:
    """Whole works go to val (text unseen in train), chosen by hash: deterministic, independent of selection."""
    h = int(hashlib.sha1(f"tts-val|{work_id}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "val" if h < val_share else "train"


def filename(clip_id: str, speaker: str, stage: str = "vtl") -> str:
    """ASCII, stable, survives any tool: CLIP__SPEAKER.wav (pie_vtl batch naming); stage dirs keep the same name."""
    name = f"{clip_id}__{speaker}.wav"
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError(f"non-ASCII-safe filename {name!r}")
    return name
