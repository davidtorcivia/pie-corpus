#!/usr/bin/env python3
"""pie_vtl.py — compile PIE IPA into a VocalTractLab gestural score, then synthesize.

Two input modes:

  1. Text (rule-based timing)
       python pie_vtl.py hymn.txt out
     One text file in the dotted IPA notation:
       χáw.sos léw.ka déj.wi di.wés dʱú.ɡə.ter ‖ n̩s.méj ...
     spaces separate words, dots are ignored, ‖ (or a newline) ends a line.

  2. Cadence timeline (exact word placement)
       python pie_vtl.py --timeline dawn-hymn-cadence.json out
     A JSON list of words with "ipa", "line", "start", "end" (seconds) and "pause_after".
     Each word's phones are fitted inside [start, end]; silence until the next start.
     The render is frame-for-frame on that timeline.

IPA: acute (á, ń̩) = accented nucleus; ʷ labialized; ʱ breathy-voiced release; ː long; n̩ syllabic.

Output (next to out_prefix):
  .ges       gestural score  (VocalTractLab 2.x desktop: load JD3-PIE.speaker, then the score)
  .wav       44.1 kHz audio
  .json      word + phone timings (start, end, flags) — exact labels
  .TextGrid  the same as a Praat TextGrid (tiers: words, phones)
  .tsv       flat phone list (start, end, phone)

Needs JD3-PIE.speaker (from make_speaker.py).
"""
import argparse, json, os, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # vtlengine.py / qc.py next to this file

# ---------------------------------------------------------------- inventory
# kind: V vowel, G glide, N nasal, S stop, F fricative, H h, L lateral, R tap;
#       syllabic sonorants are nuclei: Ns (n̩ m̩), Ls (l̩), Rs (r̩)
CONS = {
    #  phone  (kind, tier, shape, glottis)
    "p": ("S", "lip", "ll-labial-closure", "voiceless-unaspirated"),
    "b": ("S", "lip", "ll-labial-closure", "voiced-plosive"),
    "t": ("S", "tt", "tt-alveolar-closure", "voiceless-unaspirated"),
    "d": ("S", "tt", "tt-alveolar-closure", "voiced-plosive"),
    "k": ("S", "tb", "tb-velar-closure", "voiceless-unaspirated"),
    "ɡ": ("S", "tb", "tb-velar-closure", "voiced-plosive"),
    "c": ("S", "tb", "tb-palatal-closure", "voiceless-unaspirated"),   # custom shape
    "ɟ": ("S", "tb", "tb-palatal-closure", "voiced-plosive"),      # custom shape
    "s": ("F", "tt", "tt-alveolar-fricative", "voiceless-fricative"),
    "χ": ("F", "tb", "tb-uvular-fricative", "voiceless-uvular"),    # wide glottis (speaker file)
    "ɣ": ("F", "tb", "tb-uvular-fricative", "voiced-fricative"),    # rendered uvular [ʁ]
    "h": ("H", None, None, "h"),
    "m": ("N", "lip", "ll-labial-closure", "modal"),
    "n": ("N", "tt", "tt-alveolar-closure", "modal"),
    "l": ("L", "tt", "tt-alveolar-lateral", "modal"),
    "r": ("R", "tt", "tt-alveolar-closure", "modal"),               # tap [ɾ]
    "w": ("G", None, None, "modal"),
    "j": ("G", None, None, "modal"),
}
VOWEL_SHAPE = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "u", "ə": "@", "w": "u", "j": "i"}

# durations in seconds at --rate 1.0 (deliberate, recited delivery)
DUR = {"V": 0.105, "VL": 0.190, "ə": 0.055, "G": 0.060, "N": 0.070, "Ns": 0.115, "Ls": 0.115, "Rs": 0.115,
       "S": 0.085, "Sv": 0.070, "F": 0.095, "Fχ": 0.115, "H": 0.070, "L": 0.060, "R": 0.028}
# how much each kind stretches/compresses when a word is fitted to a timeline slot
ELASTIC = {"V": 1.0, "Ns": 0.9, "Ls": 0.9, "Rs": 0.9, "G": 0.6, "N": 0.5, "L": 0.5, "F": 0.45, "H": 0.45, "S": 0.35, "R": 0.0}
BREATHY_RELEASE = 0.040   # murmured phonation carried into the following segment (≤ 1/3 of it)
BREATHY_SHAPE = "murmur"  # glottis shape for ʱ releases (defined in JD3-PIE.speaker)
BREATHY_F0_DIP = 2.0      # st lower at the onset of a vowel after ʱ (first 35 ms)
GLOTTAL_LEAD = 0.045      # glottis opens this early before voiceless consonants
GLOTTAL_LEAD_BACK = 0.070 # ... and earlier before χ, whose noise source is weak
MIN_VOICED = 0.055        # a nucleus keeps at least this much modal voicing
VOICE_LEAD = 0.040        # glottis starts closing this long before a voiced sound after a voiceless one
VOICE_LEAD_SHARE = 0.45   # ... but at most this share of the voiceless sound
CONS_LEAD = 0.075         # oral constriction gestures start this early ...
CONS_TC = 0.010           # ... and approach their target with this time constant
PHRASE_PAUSE, EDGE_PAUSE = 0.85, 0.20     # rule mode: ‖ pause, leading/trailing silence
LUNG_RELEASE = 0.050      # airflow starts dropping this long before a pause, so the word ends on time
GAP_RELEASE = 0.020       # ... and this long before a short word gap
SHORT_GAP = 0.15          # gaps shorter than this: glottal closure, lungs stay on

# pitch (semitones); all overridable from the command line
ACCENT_RANGE = 4.6        # nominal st above the line baseline; VTL's pitch lag delivers ~0.74x (≈3.4 st measured)
DECL_START, DECL_END = 1.5, -2.5   # baseline across each line, relative to --pitch
FINAL_FALL = 2.0          # extra fall through the line-final word
QUESTION_RISE = 3.0       # v10.1: st of rise through the last word of a line marked "rise": true (a question)
ACCENT_RISE = 0.12        # s of rise into an accented nucleus
ACCENT_FALL = 0.15        # s of fall after it
F0_STEP = 0.020           # contour sampling step for the F0 gesture tier
LAX_SHORT = False         # --lax-short: short e i o u on the lax shapes E I O U
GLOTTIS_ADVANCE = None    # s voicing onsets lead the score (None: per engine, pip 0.030 / VTL 2.4 0.040)
ABDUCT_ADVANCE = 0.0      # s glottal openings lead the score
ORAL_ADVANCE = 0.0        # s the oral and velic tiers lead the score
H_MODE = "patch"          # h: "patch" = vowel-coloured noise after synthesis; "vtl" = open glottis only (near-silent)
TRILL = 1                 # --trill N: r as N tongue-tip contacts (1 = VTL's tap); "auto": by position (v10.1)
TRILL_AUTO = {"initial": 3, "postconsonantal": 2}   # v10.1 --trill auto: word-initial r 3 contacts, after a consonant 2, else a tap
TRILL_CYCLE = 0.040       # s per trill cycle (25 Hz, typical alveolar trill)
TRILL_CLOSE = 0.40        # share of a cycle the tongue tip is in contact
TRILL_DEPTH = -20.0       # dB: level during a patched contact (voicing continues underneath)
TB_RELEASE = 0.030        # s before its end a tongue-body (velar/palatal/uvular) constriction is released
LABIAL_CARRY = 0.030      # s the rounding of Cʷ carries into the next sound
PHRASE_END = True         # --phrase-end: the last voiced sound before a pause ≥ 0.2 s trails off
# Output-level path of a phrase-end decay, as (s re the word end, dB under full voice): quick to −10 dB,
# then slow to −30 dB (the part vtl_ends.py times), then off. Lung pressure follows it as a staircase.
PE_PATH = {"line":    [(-0.070, 0), (-0.040, -10), (0.090, -30), (0.120, -45)],
           "caesura": [(-0.060, 0), (-0.035, -10), (0.055, -30), (0.075, -45)]}
PE_K = 1.5                # output dB per lung-pressure dB (calibrated; VTL's voice falls faster than pressure)
PE_TAP = False            # --pe-tap: keep a phrase-final r as a tap (default: open [ɹ] the voice trails on)
PE_LUNG = 0.35            # (kept for the final-H tail: lung share it decays to)
PE_FALL = 0.0             # st of extra F0 fall over a line-final decay (v9: 2; v10: 0, the timeline's fall is enough)
PE_F0_COMP = 0.35         # st of F0 target raise per dB of lung-pressure drop in a decay (per engine, see ENGINE_TIMING)
PE_FLOOR = 3.0            # st: a decay's F0 target never sinks further under its last nucleus (0.8× = 3.9 st)
PE_LINE_FALL = 3.0        # st: most a line-final nucleus + tail may fall from its starting target
PE_GLOTTIS_HOLD = 0.080   # s a final m n l's glottis stays open after the decay, until the lungs are empty
                          # (otherwise the folds close again and a −14 dB hum comes back)
PE_BREATH = -16.0         # dB re the vowel: breath layered after a final m n l's hum, fading to −45 dB
PE_BREATH_SHAPE = {"line": (0.070, 0.090), "caesura": (0.030, 0.060)}   # s of breath held, then faded
PE_HUM_TC = 0.015         # time constant of that opening
PE_HUM_LAG = 0.100        # s from the opening command to the end of voicing (tc 10 ms)
PE_K_HUM = 1.0            # a nasal/lateral hum fades faster with pressure than a vowel: × PE_K
PE_HUM = 0.120            # s: a final m n l hums at most this long, then the tail is breath
FINAL_H = "noise"         # --final-h: word-final H as voiceless breath ("noise") or the vowel trailing
FINAL_H_DUR = 0.090       # into breathy voice ("murmur"); murmur H's rule/target duration (s)
FINAL_H_FALL = 4.0        # st F0 falls across a murmured final H (nominal; VTL's lag delivers ~half)
FINAL_H_OPEN = 0.5        # ... whose last half opens from murmur to the h glottis
FINAL_H_NOISE = -6.0      # dB, breath layer of a murmured final H re a plain h
FINAL_H_F0_LEAD = 0.040   # s the tail's F0 fall leads the score (VTL's F0 lag)
FINAL_H_LUNG = 0.5        # ... with lung pressure decaying towards this share
H_ROUND_BOOST = 5.0       # dB added to h coloured by u (o: 2/3 of it, w: as u): A-weighted, dark h read ~4.5 dB quieter
ROUNDED_BACK = {"u": 1.0, "w": 1.0, "o": 2 / 3}
H_FADE = 0.040            # s of fade-out at the end of a word-final H
H_DUCK = 0.8              # how much of VTL's own h interval the patch replaces
H_TILT = None             # dB/oct added to the vowel's transfer function for the h noise (None: per engine)


class Seg:
    def __init__(self, base):
        self.base, self.long, self.accent = base, False, False
        self.labial = self.breathy = self.syllabic = False
        self.line = self.word = 0

    @property
    def label(self):
        s = self.base + ("̩" if self.syllabic else "") + ("ʷ" if self.labial else "") \
            + ("ʱ" if self.breathy else "") + ("ː" if self.long else "")
        return ("ˈ" if self.accent else "") + s


def parse_word(ipa):
    """Parse one word's IPA into Segs."""
    text = unicodedata.normalize("NFD", ipa.replace("g", "ɡ"))
    segs = []
    for ch in text:
        if ch in ". -": continue
        elif ch == "́": segs[-1].accent = True      # combining acute
        elif ch == "̩": segs[-1].syllabic = True    # combining syllabic (n̩ r̩ l̩ m̩)
        elif ch == "̥":                             # ring below: PIE spelling of syllabic (r̥ l̥ n̥ m̥)
            if segs and segs[-1].base in "rlmn": segs[-1].syllabic = True
        elif ch == "ʷ": segs[-1].labial = True
        elif ch in "ʱʰ": segs[-1].breathy = True
        elif ch == "ː": segs[-1].long = True
        elif ch in VOWEL_SHAPE or ch in CONS: segs.append(Seg(ch))
        else: raise SystemExit(f"unknown symbol {ch!r} (U+{ord(ch):04X}) in {ipa!r}")
    return segs


def words_from_text(text):
    """[{line, ipa, word, segs}] from the dotted-IPA text format."""
    words, line = [], 1
    for chunk in text.replace("\n", " ‖ ").split("‖"):
        toks = chunk.split()
        if not toks: continue
        for t in toks:
            words.append({"line": line, "ipa": t, "word": t})
        line += 1
    return words


def kind(s):
    if s.base in "aeiouə": return "V"
    k = CONS[s.base][0]
    if s.syllabic:
        if k == "N": return "Ns"
        if s.base == "l": return "Ls"
        if s.base == "r": return "Rs"
    return k


NUCLEI = ("V", "Ns", "Ls", "Rs")


def trill_n(s):
    """Contacts for this r: its own (set by mark_trills under --trill auto) or the global --trill N."""
    return getattr(s, "trill", TRILL if isinstance(TRILL, int) else 1)


def mark_trills(segs):
    """v10.1 --trill auto: PIE r is an alveolar trill (docs/pronunciation.md), realised by position as in
    languages with one trilled r: a full trill word-initially, a shorter one after a consonant, a tap between
    vowels and before a consonant. Syllabic r̩ and phrase-final r are untouched (held [ɹ̩] / open [ɹ])."""
    if TRILL != "auto":
        return
    for i, x in enumerate(segs):
        if x.base != "r" or x.syllabic:
            continue
        if i == 0:
            x.trill = TRILL_AUTO["initial"]
        elif not is_nucleus(segs[i - 1]) and kind(segs[i - 1]) != "G":
            x.trill = TRILL_AUTO["postconsonantal"]
        else:
            x.trill = 1


def vowel_shape(seg):
    """VTL vowel shape for a vocalic segment: syllabic sonorants ride on a schwa; --lax-short puts
    short e i o u on the lax shapes E I O U (as in Bett, bitte, Gott, Hund)."""
    k = kind(seg)
    if k in ("Ns", "Ls", "Rs"): return "@"
    if k == "V" and LAX_SHORT and not seg.long and seg.base in "eiou": return seg.base.upper()
    return VOWEL_SHAPE[seg.base]


def is_final_h(s):
    """Word-final H after a nucleus, rendered as a murmured vowel tail (--final-h murmur)."""
    return FINAL_H == "murmur" and getattr(s, "final_h", False)


def phrase_end(s):
    """(T0, T1) of a trailing-off phrase end on this segment, or None."""
    return getattr(s, "pe", None) if PHRASE_END else None


def mark_phrase_ends(timed):
    """Flag the last segment of each word before a pause ≥ 0.2 s when it is voiced (a nucleus, a glide,
    m n r l, or a murmured final H): its voice decays over PE_SPAN, running into the pause."""
    for i, (s0, s1, seg) in enumerate(timed):
        if seg is None or i + 1 >= len(timed) or timed[i + 1][2] is not None: continue
        gap = timed[i + 1][1] - timed[i + 1][0]
        if gap < 0.2: continue
        if not (is_nucleus(seg) or kind(seg) == "G" or seg.base in "mnrl" or is_final_h(seg)): continue
        kind_ = "line" if gap >= 0.5 else "caesura"
        if is_nucleus(seg) or kind(seg) == "G" or is_final_h(seg):
            path = [(s1 + max(dt, -0.5 * (s1 - s0)), db) for dt, db in PE_PATH[kind_]]
        else:                                                # final m n l: the hum itself carries the decay
            t30 = s0 + PE_HUM + (0.005 if kind_ == "line" else -0.025)
            path = [(s0 - 0.020, 0), (s0 + 0.005, -10), (t30, -30), (t30 + 0.030, -45)]
        lim = s1 + gap - 0.08                                # leave real silence before the next word
        path = [(min(t, lim), db) for t, db in path]
        seg.pe = (path[0][0], path[-1][0])
        seg.pe_path, seg.pe_kind = path, kind_


def elastic(s):
    return 0.2 if is_final_h(s) else ELASTIC[kind(s)]


def is_nucleus(s):
    return kind(s) in NUCLEI


# ---------------------------------------------------------------- timing
def default_durations(segs, line_final):
    """Rule-based phone durations for one word (seconds at rate 1)."""
    last_nuc = max((i for i, s in enumerate(segs) if is_nucleus(s)), default=len(segs) - 1)
    out = []
    for i, s in enumerate(segs):
        k = kind(s)
        if k == "V":
            d = DUR["ə"] if s.base == "ə" else DUR["VL" if s.long else "V"]
            if s.accent: d *= 1.2
        elif k == "S":
            d = DUR["Sv" if CONS[s.base][3] == "voiced-plosive" else "S"]
        elif s.base == "χ":
            d = DUR["Fχ"]
        elif k == "R" and trill_n(s) > 1:
            d = trill_n(s) * TRILL_CYCLE
        elif is_final_h(s):
            d = FINAL_H_DUR
        else:
            d = DUR[k] * (1.2 if (k in ("Ns", "Ls", "Rs") and s.accent) else 1.0)
        if line_final:
            if i == last_nuc: d *= 1.45             # line-final lengthening
            if i > last_nuc: d *= 1.2
        out.append(d)
    return out


def fit(durs, segs, target):
    """Stretch/compress a word to `target` seconds, vowels more than consonants."""
    tot = sum(durs)
    el = [elastic(s) * d for s, d in zip(segs, durs)]
    if sum(el) > 0:
        x = (target - tot) / sum(el)
        new = [d * (1 + elastic(s) * x) for s, d in zip(segs, durs)]
        if min(n / d for n, d in zip(new, durs)) >= 0.45:
            return new
    return [d * target / tot for d in durs]          # extreme compression: scale uniformly


def build_timeline(words, rate, cadence=None):
    """Return (timed, total, words) with timed = [(start, end, Seg|None)], None = silence.
    words get "start", "end", "segs" filled in."""
    for w in words:
        w["segs"] = parse_word(w["ipa"])
        mark_trills(w["segs"])
        sg = w["segs"]
        if len(sg) > 1 and sg[-1].base == "h" and is_nucleus(sg[-2]):
            sg[-1].final_h = True
    for i, w in enumerate(words):
        line_final = i == len(words) - 1 or words[i + 1]["line"] != w["line"]
        w["line_final"] = line_final
        for s in w["segs"]:
            s.line, s.word = w["line"], i

    timed = []
    if cadence:                                         # exact placement from the JSON
        t = 0.0
        for w in words:
            if w["start"] - t > 1e-4:
                timed.append((t, w["start"], None))
            durs = fit(default_durations(w["segs"], w["line_final"]), w["segs"], w["end"] - w["start"])
            u = w["start"]
            for s, d in zip(w["segs"], durs):
                timed.append((u, u + d, s)); u += d
            t = w["end"]
        total = words[-1]["end"] + words[-1].get("pause_after", 0.5)
        timed.append((t, total, None))
        mark_phrase_ends(timed)
        return timed, total, words

    t = EDGE_PAUSE                                      # rule-based timing
    timed.append((0.0, t, None))
    for i, w in enumerate(words):
        w["start"] = t
        for s, d in zip(w["segs"], default_durations(w["segs"], w["line_final"])):
            timed.append((t, t + d / rate, s)); t += d / rate
        w["end"] = t
        if w["line_final"]:
            p = (EDGE_PAUSE if i == len(words) - 1 else PHRASE_PAUSE) / rate
            timed.append((t, t + p, None)); t += p
    mark_phrase_ends(timed)
    return timed, t, words


# ---------------------------------------------------------------- gestures
class Tier:
    def __init__(self, typ, unit="", neutral_value="", tc=0.012):
        self.typ, self.unit, self.nv, self.tc, self.g = typ, unit, neutral_value, tc, []

    def end(self):
        return sum(d for _, d, _, _ in self.g)

    def add(self, start, end, value, neutral=False, tc=None):
        """Append a gesture, filling any gap before it with a neutral gesture."""
        cur = self.end()
        start = max(start, cur)
        if end - start < 0.005: return
        if start - cur > 1e-6:
            self.g.append((self.nv, start - cur, True, self.tc))
        if self.g and not neutral and self.g[-1][0] == value and not self.g[-1][2]:
            v, d, n, c = self.g[-1]; self.g[-1] = (v, d + end - start, n, c)   # merge
        else:
            self.g.append((value, end - start, neutral, tc or self.tc))

    def advance(self, dt):
        """Shift the whole tier dt s earlier (trimming its first gesture)."""
        while dt > 1e-9 and self.g:
            v, d, n, c = self.g[0]
            if d > dt + 0.005:
                self.g[0] = (v, d - dt, n, c); return
            self.g.pop(0); dt -= d

    def close(self, total):
        cur = self.end()
        if total - cur > 1e-6:
            self.g.append((self.nv, total - cur, True, self.tc))

    def xml(self):
        rows = [f'  <gesture_sequence type="{self.typ}" unit="{self.unit}">']
        for v, d, n, c in self.g:
            val = f"{v:.6f}" if isinstance(v, float) else v
            rows.append(f'    <gesture value="{val}" slope="0.000000" duration_s="{d:.6f}" '
                        f'time_constant_s="{c:.6f}" neutral="{int(n)}" />')
        rows.append("  </gesture_sequence>")
        return "\n".join(rows)


def is_short_gap(s0, s1, seg):
    return seg is None and s1 - s0 < SHORT_GAP and s0 > 0


def f0_contour(timed, words, base_st):
    """Continuous F0 target (st) as a function of time:
       line baseline (declination DECL_START → DECL_END across each line)
     + extra fall through the line-final word (−FINAL_FALL by its end)
     + one smooth accent bump per accented nucleus: raised-cosine rise over ACCENT_RISE s into the
       nucleus, ACCENT_RANGE st across it, raised-cosine fall over ACCENT_FALL s after it
     − a short dip at the onset of a vowel after ʱ (breathy voice lowers F0)."""
    import math
    lines = {}
    for w in words:
        lo, hi = lines.get(w["line"], (w["start"], w["end"]))
        lines[w["line"]] = (min(lo, w["start"]), max(hi, w["end"]))
    line_order = sorted(lines)
    final_words = {w["line"]: w for w in words}          # last word of each line wins

    accents, dips, tails, pe_falls, pe_comp, prev, last_nuc = [], [], [], [], [], None, None
    for (s0, s1, seg) in timed:
        if seg is None: continue
        if is_nucleus(seg): last_nuc = (s0, s1)
        if phrase_end(seg) and last_nuc is not None:       # decay: hold F0 against the pressure sag
            pe_comp.append((seg.pe_path, last_nuc, seg.pe_kind))
        if is_final_h(seg): tails.append((s0 - FINAL_H_F0_LEAD, s1 - FINAL_H_F0_LEAD))   # F0 lags ~40 ms
        if phrase_end(seg) and seg.pe_kind == "line" and PE_FALL:
            pe_falls.append((phrase_end(seg)[0] - FINAL_H_F0_LEAD, phrase_end(seg)[1] - FINAL_H_F0_LEAD))
        if is_nucleus(seg) and seg.accent:
            lead_ = FINAL_H_F0_LEAD if (phrase_end(seg) or any(          # a phrase-final accent reaches
                phrase_end(x[2]) for x in timed if x[2] is not None and x[2].word == seg.word
                and x[0] >= s1 - 1e-6)) else 0.0                         # its peak by the vowel onset
            accents.append((s0 - lead_, s1))
        if is_nucleus(seg) and prev is not None and prev.breathy and BREATHY_F0_DIP:
            dips.append(s0)
        prev = seg

    def line_at(t):
        for ln in line_order:
            lo, hi = lines[ln]
            if t <= hi + 0.3: return ln
        return line_order[-1]

    def rc(x):                                          # 0→1 raised cosine on [0,1]
        x = min(max(x, 0.0), 1.0)
        return 0.5 - 0.5 * math.cos(math.pi * x)

    def f(t):
        ln = line_at(t); lo, hi = lines[ln]
        frac = min(max((t - lo) / max(hi - lo, 1e-3), 0), 1)
        v = base_st + DECL_START + (DECL_END - DECL_START) * frac
        fw = final_words[ln]
        if t > fw["start"]:                             # v10.1: a question's last word rises instead of falling
            x = rc((t - fw["start"]) / max(fw["end"] - fw["start"], 1e-3))
            v += QUESTION_RISE * x if fw.get("rise") else -FINAL_FALL * x
        bump = 0.0
        for (a0, a1) in accents:
            if t < a0 - ACCENT_RISE or t > a1 + ACCENT_FALL: continue
            if t < a0:   b = rc((t - (a0 - ACCENT_RISE)) / ACCENT_RISE)
            elif t <= a1: b = 1.0
            else:        b = 1.0 - rc((t - a1) / ACCENT_FALL)
            bump = max(bump, b)                         # overlapping accents don't stack
        v += ACCENT_RANGE * bump
        for (p0, p1) in pe_falls:                       # line-final decay: F0 sinks a little further
            if p0 <= t <= p1 + 0.10:
                v -= PE_FALL * rc((t - p0) / max(p1 - p0, 1e-3))
        for (h0, h1) in tails:                          # murmured final H: F0 sinks through it
            if h0 <= t <= h1 + 0.03:
                v -= FINAL_H_FALL * rc((t - h0) / max(h1 - h0, 1e-3))
        for d0 in dips:
            if d0 - 0.01 <= t <= d0 + 0.045:
                v -= BREATHY_F0_DIP * math.sin(math.pi * (t - d0 + 0.01) / 0.055)
        return v

    # Phrase-end decay: VTL's F0 sags with the falling lung pressure (and the opening glottis), which
    # ElevenLabs turns into a creaky dive. Raise the target by PE_F0_COMP st per dB of lung-pressure drop
    # (calibrated per engine), led by VTL's F0 lag, and never let the target sink more than PE_FLOOR st
    # under its value at the middle of the last nucleus.
    # Caesura: the last nucleus and its tail are level at the nucleus's starting target (the accent
    # fall is not carried into a caesura). Line end: the timeline's contour, but never more than
    # PE_LINE_FALL st under the nucleus's starting target.
    comps = []
    for path, (n0, n1), kind_ in pe_comp:
        ts = [t - FINAL_H_F0_LEAD for t, _ in path]; dbs = [db for _, db in path]
        ref = f(n0 - FINAL_H_F0_LEAD)          # where VTL's lagging F0 actually is at the nucleus onset
        comps.append((ts, dbs, ref - min(PE_FLOOR, PE_LINE_FALL), n0 - 2 * FINAL_H_F0_LEAD, ref, kind_))

    def g(t):
        v = f(t)
        for ts, dbs, floor, h0, ref, kind_ in comps:
            if h0 <= t <= ts[-1] + 0.10:
                v = ref if kind_ == "caesura" else max(v, floor)
            if ts[0] <= t <= ts[-1] + 0.10:
                db = dbs[-1] if t > ts[-1] else float(sum(  # linear interpolation along the path
                    dbs[k] + (dbs[k + 1] - dbs[k]) * (t - ts[k]) / max(ts[k + 1] - ts[k], 1e-6)
                    for k in range(len(ts) - 1) if ts[k] <= t <= ts[k + 1]) if any(
                    ts[k] <= t <= ts[k + 1] for k in range(len(ts) - 1)) else 0.0)
                v = max(v + PE_F0_COMP * (-db / PE_K), floor)
        return v
    return g


def compile_score(timed, total, words, base_st):
    import numpy as np
    vow = Tier("vowel-gestures")
    lip, tt, tb = Tier("lip-gestures"), Tier("tongue-tip-gestures"), Tier("tongue-body-gestures")
    vel = Tier("velic-gestures", neutral_value=0.0)
    glo = Tier("glottal-shape-gestures")
    f0 = Tier("f0-gestures", "st", neutral_value=float(base_st), tc=0.015)
    lung = Tier("lung-pressure-gestures", "dPa", neutral_value=0.0)
    tiers = {"lip": lip, "tt": tt, "tb": tb}

    # vowel tier: each vocalic target spans from the previous vocalic end to its own end
    prev_end, last_shape = 0.0, "@"
    for (s0, s1, seg) in timed:
        if seg is None: continue
        k = kind(seg)
        if k in ("V", "G", "Ns", "Ls", "Rs"):
            shape = vowel_shape(seg)
        elif is_final_h(seg):
            shape = last_shape                          # the vowel carries on through its murmured tail
        else:
            continue
        e_ = phrase_end(seg)[1] if phrase_end(seg) else s1        # held through a phrase-end decay
        vow.add(prev_end, e_, shape); prev_end, last_shape = e_, shape
    vow.add(prev_end, total, last_shape)

    # consonant tiers, velum, lip rounding. A constriction may anticipate, but never before
    # the middle of the preceding vowel (short vowels between stops would never open up).
    last_nuc_mid = -1.0
    for idx, (s0, s1, seg) in enumerate(timed):
        if seg is None: continue
        k = kind(seg)
        nxt = next((g for _, _, g in timed[idx + 1:] if g is not None), None)
        if seg.base in CONS:
            _, tier, shape, _ = CONS[seg.base]
            if k == "Rs":
                shape = "tt-alveolar-approximant"               # syllabic r̩ = held [ɹ̩] over a schwa
            if k == "R" and phrase_end(seg) and not PE_TAP:
                shape, k = "tt-alveolar-approximant", "Ls"       # phrase-final r: an open [ɹ] the voice trails on
            if tier and k == "R" and trill_n(seg) > 1:                # trill: VTL makes the first contact,
                start = max(s0 - CONS_LEAD, last_nuc_mid)         # then holds an open [ɹ]-like tip;
                c1 = s0                                           # tip contact lands ~+14..+32 ms (measured)
                tiers[tier].add(start, max(c1, start + 0.03), "tt-alveolar-closure", tc=CONS_TC)
                tiers[tier].add(max(c1, start + 0.03), s1 - 0.010, "tt-alveolar-approximant", tc=CONS_TC)
            elif tier:
                start = max(s0 - CONS_LEAD, last_nuc_mid)
                end = s1 - (0.010 if k == "R" else TB_RELEASE if tier == "tb" else 0.030)
                if phrase_end(seg) and k != "R":                     # m n l held (a tap stays a tap), past the
                    end = phrase_end(seg)[1] + (0.05 if k == "N" else 0.0)   # end of airflow: no breath burst
                tiers[tier].add(start, max(end, start + 0.05), shape, tc=CONS_TC)
            if k in ("N", "Ns"):
                obstruent_next = nxt is not None and kind(nxt) in ("S", "F", "H")
                vel.add(s0 - 0.03, phrase_end(seg)[1] + 0.05 if phrase_end(seg) else
                        s1 - (0.045 if obstruent_next else 0.015), 0.5, tc=0.010)
            if seg.labial:                       # Cʷ: rounding carries into the release
                lip.add(s0 - 0.06, s1 + LABIAL_CARRY, "ll-rounded")
            elif seg.base == "w":                 # glide: rounding released before the next sound
                lip.add(s0 - 0.04, s1 - 0.025, "ll-rounded")
        if is_nucleus(seg):
            last_nuc_mid = (s0 + s1) / 2

    # glottis: one shape per segment. Voiceless sounds open the glottis early (anticipation);
    # a breathy-voiced stop releases into murmur; short word gaps are a glottal closure.
    VOICELESS = {"voiceless-plosive", "voiceless-unaspirated", "voiceless-fricative", "voiceless-uvular", "h"}
    spans = []
    for (s0, s1, seg) in timed:
        if seg is None:
            g = "stop" if is_short_gap(s0, s1, seg) else "modal"
        else:
            g = CONS[seg.base][3] if seg.base in CONS else "modal"
            if is_final_h(seg): g = BREATHY_SHAPE
        spans.append([s0, s1, g, seg])
    # murmur after ʱ spills into the next segment: at most BREATHY_RELEASE, at most a third of it,
    # and never into the MIN_VOICED of modal voicing a nucleus keeps
    spill = [0.0] * len(spans)
    for i in range(1, len(spans)):
        prev = spans[i - 1][3]
        if prev is not None and prev.breathy and spans[i][3] is not None:
            d = spans[i][1] - spans[i][0]
            sp = min(BREATHY_RELEASE, d / 3)
            if is_nucleus(spans[i][3]):
                sp = min(sp, max(0.0, d - MIN_VOICED))
            spill[i] = sp
    for i in range(1, len(spans)):
        if spans[i][2] in VOICELESS and spans[i - 1][2] not in VOICELESS:
            want = GLOTTAL_LEAD_BACK if spans[i][3] is not None and spans[i][3].base == "χ" else GLOTTAL_LEAD
            prev_dur = spans[i - 1][1] - spans[i - 1][0]
            prev_seg = spans[i - 1][3]
            if prev_seg is not None and is_nucleus(prev_seg):     # keep the vowel's modal voicing:
                lead = min(want, max(0.0, prev_dur - spill[i - 1] - MIN_VOICED))   # murmur counts against it
            else:
                lead = min(want, max(0.0, prev_dur - spill[i - 1]) * 0.7)
            spans[i - 1][1] -= lead; spans[i][0] -= lead
    # the folds need ~60-80 ms to start vibrating after a voiceless sound: begin adducting
    # during the voiceless consonant's release so the next vowel gets short-lag voicing
    for i in range(1, len(spans)):
        cur_seg = spans[i][3]
        if spans[i - 1][2] in VOICELESS | {"stop"} and spans[i][2] not in VOICELESS and cur_seg is not None:
            lead = min(VOICE_LEAD, (spans[i - 1][1] - spans[i - 1][0]) * VOICE_LEAD_SHARE)
            spans[i - 1][1] -= lead; spans[i][0] -= lead
    # VTL's folds are slow to start vibrating (measured onset lag: pip ~30 ms, VTL 2.4 ~40 ms) but
    # quick to stop. So only the voicing onsets move earlier (GLOTTIS_ADVANCE, eating into the
    # voiceless sound, which keeps at least 40% of itself); openings move by ABDUCT_ADVANCE, and
    # never into a nucleus's MIN_VOICED.
    for i in range(1, len(spans)):
        a_, b_ = spans[i - 1], spans[i]
        if a_[2] in VOICELESS | {"stop"} and b_[2] not in VOICELESS:
            nominal = timed[i - 1][1] - timed[i - 1][0]
            sh = max(0.0, min(GLOTTIS_ADVANCE, (a_[1] - a_[0]) - 0.4 * nominal))
            a_[1] -= sh; b_[0] -= sh
        elif b_[2] in VOICELESS and a_[2] not in VOICELESS and ABDUCT_ADVANCE:
            room = (a_[1] - a_[0] - spill[i - 1] - MIN_VOICED) if a_[3] is not None and is_nucleus(a_[3]) \
                else (a_[1] - a_[0]) * 0.5
            sh = max(0.0, min(ABDUCT_ADVANCE, room))
            a_[1] -= sh; b_[0] -= sh
    for i, (s0, s1, g, seg) in enumerate(spans):
        nxt_spill = spill[i + 1] if i + 1 < len(spans) else 0.0
        start = s0 + spill[i]
        if seg is not None and seg.breathy:
            glo.add(start, s1 - 0.010, g)
            glo.add(s1 - 0.010, s1 + nxt_spill, BREATHY_SHAPE)
        elif seg is not None and is_final_h(seg):        # murmured tail opening into breath
            start = min(start, glo.end())                 # (begins where the vowel's modal span was cut)
            if phrase_end(seg):                          # at a phrase end the tail follows the decay path:
                T0, T1 = seg.pe_path[1][0], phrase_end(seg)[1]   # murmur until −10 dB, then into breath
                lag = GLOTTIS_ADVANCE or 0.0
                mid = max(start, T0 - lag) + 0.5 * (T1 - lag - max(start, T0 - lag))
            else:
                T1 = s1
                mid = start + (1 - FINAL_H_OPEN) * (s1 - start)
            glo.add(start, mid, BREATHY_SHAPE)
            glo.add(mid, T1, CONS["h"][3], tc=0.020)
        elif seg is not None and phrase_end(seg):          # phrase end: modal → murmur → breath
            T0, T1 = seg.pe_path[1][0], phrase_end(seg)[1]   # (from the −10 dB point)
            lag = GLOTTIS_ADVANCE or 0.0
            t0 = max(T0 - lag, start + 0.5 * (s1 - start))
            t_open = t0 + 0.5 * (T1 - lag - t0)
            if is_nucleus(seg) or kind(seg) == "G":          # vowel: the voice fades out into breath
                glo.add(start, t0, g)
                glo.add(t0, t_open, BREATHY_SHAPE)
                glo.add(t_open, T1, CONS["h"][3], tc=0.020)     # (as v9: the decay is right, keep it)
            else:                                            # final m n l: hum ≤ PE_HUM, then breath. With a
                t_open = min(t_open, s0 + PE_HUM - PE_HUM_LAG) # 10 ms time constant the folds stop ~55 ms after
                t0 = min(t0, t_open - 0.020)                 # the command (20 ms: ~150 ms, a long low hum)
                glo.add(start, t0, g)
                glo.add(t0, t_open, BREATHY_SHAPE)
                glo.add(t_open, T1 + PE_GLOTTIS_HOLD, "aspirate", tc=PE_HUM_TC)
        else:
            nxt_seg = spans[i + 1][3] if i + 1 < len(spans) else None
            if nxt_seg is not None and is_final_h(nxt_seg):     # the folds lag: start the murmur early
                s1 = max(s1 - (GLOTTIS_ADVANCE or 0.0), start + 0.5 * (s1 - start))
            glo.add(start, s1, g, tc=0.010 if g in VOICELESS | {"stop"} else None)
    glo.close(total)

    # F0: sample the continuous contour every F0_STEP s (targets lead by ~one time constant)
    contour = f0_contour(timed, words, base_st)
    t = 0.0
    while t < total - 1e-6:
        f0.add(t, min(t + F0_STEP, total), contour(t + F0_STEP / 2 + 0.015))
        t += F0_STEP

    # lungs: off in long pauses, on through short word gaps. A pause-initial obstruent waits
    # until its constriction has formed (otherwise a stray vowel appears).
    # Every gap is silent: airflow drops just before the word ends (LUNG_RELEASE before a pause,
    # GAP_RELEASE before a short word gap) and comes back just before the next word.
    prev_gap = "long"
    for idx, (s0, s1, seg) in enumerate(timed):
        if seg is None:
            short = is_short_gap(s0, s1, seg)
            soft = idx > 0 and timed[idx - 1][2] is not None and phrase_end(timed[idx - 1][2])
            lung.add(s0, s1 - (0.025 if short else 0.05), 0.0, tc=0.030 if soft else 0.005)
            prev_gap = "short" if short else "long"
            continue
        if prev_gap == "long":
            onset = s0 - (0.005 if kind(seg) in ("S", "F", "H") else 0.04)
        elif prev_gap == "short":
            onset = s0 - (0.005 if kind(seg) in ("S", "F", "H") else 0.025)
        else:
            onset = s0
        nxt = timed[idx + 1] if idx + 1 < len(timed) else None
        end = s1
        if nxt is not None and nxt[2] is None:
            rel = GAP_RELEASE if is_short_gap(*nxt) else LUNG_RELEASE
            end = max(s1 - rel, (s0 + s1) / 2)          # airflow drops so sound ends on time
        elif nxt is not None and is_final_h(nxt[2]):
            end = s1 - 0.020                            # the breath tail starts decaying a little early
        if phrase_end(seg):                                 # phrase end: pressure falls, not a step
            T0, T1 = phrase_end(seg)
            if True:                                     # (a murmured final H follows the same path)
                lung.add(min(onset, lung.end()) if is_final_h(seg) else onset, T0, 8000.0, tc=0.005)
                ts, dbs = zip(*seg.pe_path)
                t = T0
                while t < T1 - 1e-6:                             # 10 ms steps along the level path
                    t2 = min(t + 0.010, T1)
                    db = float(np.interp(t2, ts, dbs))
                    k_ = PE_K * (1.0 if is_nucleus(seg) or kind(seg) == "G" or is_final_h(seg) else PE_K_HUM)
                    lung.add(t, t2, 8000.0 * 10 ** (db / k_ / 20), tc=0.010)
                    t = t2
            prev_gap = None
            continue
        if is_final_h(seg):                                 # the breath tail decays (from where the
            lung.add(min(onset, lung.end()), end, 8000.0 * FINAL_H_LUNG, tc=0.015)   # vowel's pressure ended)
        else:
            lung.add(onset, end, 8000.0, tc=0.005)
        if end < s1 and not (nxt is not None and nxt[2] is not None and is_final_h(nxt[2])):
            lung.add(end, s1, 0.0, tc=0.005)
        prev_gap = None
    lung.close(total)

    for t in (vow, lip, tt, tb, vel):
        if ORAL_ADVANCE: t.advance(ORAL_ADVANCE)    # articulators lag their targets (release ~30 ms late)
        t.close(total)
    body = "\n".join(t.xml() for t in (vow, lip, tt, tb, vel, glo, f0, lung))
    return "<gestural_score>\n" + body + "\n</gestural_score>\n"


# ---------------------------------------------------------------- frication patch
# VTL's noise source behind a back (uvular) constriction mostly rings one cavity resonance:
# loud but tonal, a whistle rather than a hiss. Since every χ/ɣ position is known exactly,
# we lay shaped noise over those intervals after synthesis.
# Spectral template (Hz, dB): eSpeak's χ from 750 Hz to 5 kHz, rolled off below like a real
# [χ] and above 6 kHz (enhancers treat bright stationary noise as background and remove it).
CHI_TEMPLATE = [(0, -40), (300, -24), (600, -10), (750, -4.6), (1000, -11.2), (1250, -7.1),
                (1600, -2.6), (2000, -5.2), (2500, -7.6), (3150, -14.0), (4000, -6.4),
                (5000, -8.1), (6300, -24.0), (8000, -40.0), (10000, -50.0), (22050, -70)]


def _shaped_noise(n, sr, template, rng):
    import numpy as np
    spec = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / sr)
    hz, db = zip(*template)
    spec *= 10 ** (np.interp(f, hz, db) / 20)
    x = np.fft.irfft(spec, n)
    return x / (np.sqrt((x ** 2).mean()) + 1e-12)


def patch_frication(audio, timed, chi_level, gamma_level, sr=44100, seed=0):
    """Replace χ with shaped noise and add a noise layer under ɣ.
    Levels are dB relative to the RMS of the nearest vowel."""
    import numpy as np
    rng = np.random.default_rng(seed)
    out = audio.copy()
    nuclei = [(s0, s1) for s0, s1, g in timed if g is not None and is_nucleus(g)]

    def vowel_rms(t):
        s0, s1 = min(nuclei, key=lambda v: min(abs(v[0] - t), abs(v[1] - t)))
        m = (s0 + s1) / 2
        x = audio[int((m - .025) * sr):int((m + .025) * sr)]
        return np.sqrt((x ** 2).mean()) + 1e-9

    for s0, s1, seg in timed:
        if seg is None or seg.base not in ("χ", "ɣ"):
            continue
        a, b = max(int((s0 - 0.01) * sr), 0), min(int((s1 + 0.005) * sr), len(out))
        n = b - a
        ramp = min(int(0.015 * sr), n // 2)
        env = np.ones(n)
        env[:ramp] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ramp))
        env[n - ramp:] = env[:ramp][::-1]
        noise = _shaped_noise(n, sr, CHI_TEMPLATE, rng)
        if seg.base == "χ":
            noise *= vowel_rms(s0) * 10 ** (chi_level / 20)
            out[a:b] = out[a:b] * (1 - 0.95 * env) + noise * env      # duck VTL's tonal χ ~26 dB
        else:
            noise *= vowel_rms(s0) * 10 ** (gamma_level / 20)
            out[a:b] = out[a:b] + noise * env                         # keep voicing, add friction
    return out


# ---------------------------------------------------------------- phrase-end breath (final m n l)
# A final nasal/lateral hum keeps its level until the folds part, so it can't carry a long decay
# without becoming the long low hum ElevenLabs dislikes. The hum stops after PE_HUM; breath coloured
# like the vowel before it (VTL transfer function, as the h patch) carries the rest of the decay.

def patch_phrase_breath(audio, timed, engine, sr=44100, seed=2):
    import numpy as np
    rng = np.random.default_rng(seed)
    out = audio.copy()
    last_v = None
    for i, (s0, s1, seg) in enumerate(timed):
        if seg is None: continue
        if is_nucleus(seg): last_v = (s0, s1, seg)
        if not phrase_end(seg) or is_nucleus(seg) or kind(seg) == "G" or is_final_h(seg) or last_v is None:
            continue
        gap = timed[i + 1][1] - timed[i + 1][0]
        t_a = s0 + PE_HUM - 0.030                          # breath swells in as the hum stops
        hold, fade = PE_BREATH_SHAPE[seg.pe_kind]
        t_b = min(t_a + 0.030 + hold + fade, s1 + gap - 0.06)
        if t_b <= t_a + 0.03: continue
        a, b = int(t_a * sr), int(t_b * sr); n = b - a
        v0, v1, vseg = last_v; m = (v0 + v1) / 2
        x = audio[int((m - 0.02) * sr):int((m + 0.02) * sr)]
        spec = np.fft.rfft(rng.standard_normal(n)) * _aspiration_envelope(engine, vowel_shape(vseg), n, sr)
        y = np.fft.irfft(spec, n); y /= np.sqrt((y ** 2).mean()) + 1e-12
        tt = np.arange(n) / sr
        db = PE_BREATH + (-45.0 - PE_BREATH) * np.clip((tt - 0.030 - hold) / fade, 0, 1)   # hold, then fade
        env = 10 ** (db / 20) * np.minimum(1.0, tt / 0.030)                         # 30 ms swell
        out[a:b] += y * (np.sqrt((x ** 2).mean()) + 1e-9) * env
    return out


# ---------------------------------------------------------------- trill patch (r)
# A trill is aerodynamic: airflow sucks the tongue tip back onto the ridge 25 times a second.
# VTL's tongue is target-driven, and after the first contact its tip only reaches its 0.15 cm²
# constriction floor (measured: re-closure targets of any depth don't re-close within 40 ms).
# So VTL makes the first contact itself (a real tap, with real formant transitions) and holds
# an open tip; this patch cuts the remaining TRILL−1 contacts into the audio, like the χ/h patches.

def patch_trill(audio, timed, sr=44100):
    """Bring each of the TRILL contacts down to TRILL_DEPTH dB re the following vowel. Contacts
    VTL already made (JD3's first one) are left as they are; missing ones are cut in."""
    import numpy as np
    out = audio.copy()
    for idx, (s0, s1, seg) in enumerate(timed):
        if seg is None or kind(seg) != "R" or trill_n(seg) < 2:
            continue
        n_c = trill_n(seg)
        nuc = next(((v0, v1) for v0, v1, g in timed[idx + 1:] if g is not None and is_nucleus(g)), None)
        if nuc is None:
            nuc = next(((v0, v1) for v0, v1, g in reversed(timed[:idx]) if g is not None and is_nucleus(g)), None)
        m = (nuc[0] + nuc[1]) / 2
        ref = np.sqrt((audio[int((m - .02) * sr):int((m + .02) * sr)] ** 2).mean()) + 1e-9
        cyc = (s1 - s0) / n_c
        edge = int(0.005 * sr)
        for c in range(n_c):
            t = s0 + 0.014 + c * cyc                 # VTL's own first contact lands ~14 ms in
            a, b = int(t * sr), int((t + TRILL_CLOSE * cyc) * sr)
            rms = np.sqrt((out[a:b] ** 2).mean()) + 1e-12
            k = min(1.0, ref * 10 ** (TRILL_DEPTH / 20) / rms)
            if k >= 0.999:
                continue
            env = np.full(b - a + 2 * edge, k)
            r = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, edge))       # 1 → 0
            env[:edge] = k + (1 - k) * r
            env[-edge:] = k + (1 - k) * r[::-1]
            out[a - edge:b + edge] *= env
    return out


# ---------------------------------------------------------------- aspiration patch (h)
# VTL's "h" glottis gives almost no audible aspiration. Real [h] is breath noise filtered by the
# vocal tract of the neighbouring vowel, so we estimate that vowel's resonances (LPC envelope)
# from VTL's own audio and colour white noise with it. Between two vowels the colour crossfades
# from the preceding vowel to the following one.

def _aspiration_envelope(engine, shape, n, sr):
    """|H(f)| of the vowel's own tract (VTL transfer function, glottis → lips), as breath noise
    would be filtered by it: × H_TILT dB/oct (turbulent source + lip radiation), F1 damped lightly
    (open glottis), rolled off above 7 kHz. Sampled on rfft bins of length n. Independent of F0."""
    import numpy as np
    fh, mag = engine.transfer(engine.shape(shape))
    f = np.fft.rfftfreq(n, 1 / sr)
    env = np.interp(f, fh, mag)
    env *= np.clip(f / 1000, 0.25, 8.0) ** (H_TILT / 6.0)
    env *= np.where(f < 500, (np.maximum(f, 50) / 500) ** 0.5, 1.0)
    env *= np.where(f > 7000, (7000 / np.maximum(f, 7000)) ** 4, 1.0)
    return env / env.max()


def patch_aspiration(audio, timed, h_level, engine, sr=44100, seed=1):
    """Lay vowel-coloured breath noise over every h. Level: dB re the RMS of its colouring vowel(s)."""
    import numpy as np
    rng = np.random.default_rng(seed)
    out = audio.copy()

    def vowel_sample(s0, s1):
        m, half = (s0 + s1) / 2, min(0.02, (s1 - s0) / 2)
        return audio[int((m - half) * sr):int((m + half) * sr)]

    def neighbour(idx, step):
        """Nearest nucleus in this word in direction `step`, crossing at most one consonant/glide."""
        seg = timed[idx][2]; j, hops = idx + step, 0
        while 0 <= j < len(timed) and timed[j][2] is not None and timed[j][2].word == seg.word:
            if is_nucleus(timed[j][2]) or kind(timed[j][2]) == "G": return timed[j]   # glides colour h too
            hops += 1
            if hops > 1: break
            j += step
        return None

    for idx, (s0, s1, seg) in enumerate(timed):
        if seg is None or seg.base != "h":
            continue
        prev_v, next_v = neighbour(idx, -1), neighbour(idx, +1)
        colours = [v for v in (prev_v, next_v) if v is not None]
        if not colours:                                    # isolated h: nearest nucleus anywhere
            colours = [min((x for x in timed if x[2] is not None and is_nucleus(x[2])),
                           key=lambda v: min(abs(v[0] - s0), abs(v[1] - s1)))]
        a, b = max(int((s0 - 0.005) * sr), 0), min(int((s1 + 0.005) * sr), len(out))
        n = b - a
        ramp = min(int(0.012 * sr), n // 2)
        env = np.ones(n)
        env[:ramp] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ramp))
        env[n - ramp:] = env[:ramp][::-1]
        duck = env.copy() if not is_final_h(seg) else np.zeros(n)   # VTL's own h is ducked over the whole
                                                           # interval (a murmured final H keeps its voice),
        if is_final_h(seg):                                # murmured tail: breath swells in as the voice
            up, dn = int(0.4 * n), int(0.3 * n)            # decays (first 40%), fades over the last 30%
            env[:up] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, up))
            env[n - dn:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, dn))
        elif next_v is None and prev_v is not None:        # word-final H: only the breath fades, over its last
            fade = min(int(H_FADE * sr), n // 2)           # H_FADE s and never more than half of a short H
            env[n - fade:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade))
        layers = []
        for (v0, v1, vseg) in colours:
            x = vowel_sample(v0, v1)
            spec = np.fft.rfft(rng.standard_normal(n)) * _aspiration_envelope(engine, vowel_shape(vseg), n, sr)
            y = np.fft.irfft(spec, n); y /= np.sqrt((y ** 2).mean()) + 1e-12
            boost = H_ROUND_BOOST * ROUNDED_BACK.get(vseg.base, 0.0)    # dark u/o colour: same loudness
            if is_final_h(seg): boost += FINAL_H_NOISE                  # breath under a voiced tail
            layers.append(y * (np.sqrt((x ** 2).mean()) + 1e-9) * 10 ** ((h_level + boost) / 20))
        if len(layers) == 2:                               # between vowels: colour glides across the h
            w = np.linspace(0, 1, n)
            noise = layers[0] * (1 - w) + layers[1] * w
        else:
            noise = layers[0]
        out[a:b] = out[a:b] * (1 - H_DUCK * duck) + noise * env   # VTL's own (mostly voiced) h, ducked
    return out


# ---------------------------------------------------------------- timing outputs
def write_timings(prefix, timed, total, words):
    phones = []
    for (s0, s1, seg) in timed:
        if seg is None: continue
        phones.append({"phone": seg.label.lstrip("ˈ"), "start": round(s0, 4), "end": round(s1, 4),
                       "word_index": seg.word, "line": seg.line, "accent": seg.accent,
                       "breathy": seg.breathy, "labial": seg.labial, "long": seg.long,
                       "kind": kind(seg)})
    out = {"duration": round(total, 4), "sample_rate": 44100, "words": []}
    for i, w in enumerate(words):
        out["words"].append({"index": i, "word": w["word"], "ipa": w["ipa"], "line": w["line"],
                             "start": round(w["start"], 4), "end": round(w["end"], 4),
                             "phones": [p for p in phones if p["word_index"] == i]})
    with open(prefix + ".json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    with open(prefix + ".tsv", "w", encoding="utf-8") as f:
        f.write("start\tend\tphone\n")
        for s0, s1, seg in timed:
            f.write(f"{s0:.4f}\t{s1:.4f}\t{seg.label if seg else '<pause>'}\n")

    def tier(name, items):
        iv, t = [], 0.0
        for a, b, lab in items:
            if a - t > 1e-6: iv.append((t, a, ""))
            iv.append((a, b, lab)); t = b
        if total - t > 1e-6: iv.append((t, total, ""))
        rows = [f'    class = "IntervalTier"', f'    name = "{name}"', "    xmin = 0",
                f"    xmax = {total:.4f}", f"    intervals: size = {len(iv)}"]
        for k, (a, b, lab) in enumerate(iv, 1):
            rows += [f"    intervals [{k}]:", f"        xmin = {a:.4f}", f"        xmax = {b:.4f}",
                     f'        text = "{lab}"']
        return rows
    word_items = [(w["start"], w["end"], w["word"]) for w in words]
    phone_items = [(s0, s1, seg.label) for s0, s1, seg in timed if seg is not None]
    lines = ['File type = "ooTextFile"', 'Object class = "TextGrid"', "", "xmin = 0",
             f"xmax = {total:.4f}", "tiers? <exists>", "size = 2", "item []:"]
    for k, (name, items) in enumerate((("words", word_items), ("phones", phone_items)), 1):
        lines.append(f"    item [{k}]:"); lines += tier(name, items)
    with open(prefix + ".TextGrid", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- rendering
def speaker_pitch(speaker):
    """Default baseline: the speaker's rest F0 minus 3 st (JD3 120 Hz → 80 st, W02 220 Hz → 90.3 st)."""
    import math, re
    t = open(speaker, encoding="utf-8").read()
    m = re.search(r'abbr="rest_f0"[^>]*value="([^"]+)"', t) or re.search(r'name="RF0"[^>]*neutral="([^"]+)"', t)
    return 12 * math.log2(float(m.group(1))) - 3 if m else 80.0


# Measured lags (hard-test sweeps, v6): stop releases land ~30 ms after their score time in both
# engines; voicing onsets lag ~30 ms (pip) / ~40 ms (VTL 2.4); VTL 2.4 also opens the glottis late.
ENGINE_TIMING = {"pip": {"ORAL_ADVANCE": 0.030, "GLOTTIS_ADVANCE": 0.030, "ABDUCT_ADVANCE": 0.0, "BREATHY_RELEASE": 0.040,
                         "PE_K": 3.0, "PE_F0_COMP": 0.04},
                 "2.4": {"ORAL_ADVANCE": 0.030, "GLOTTIS_ADVANCE": 0.040, "ABDUCT_ADVANCE": 0.020, "BREATHY_RELEASE": 0.040,
                         "PE_K": 5.0, "PE_F0_COMP": 0.04}}    # PE_K: VTL 2.4's folds stop abruptly at low pressure, so keep it higher
SPEAKER_TIMING = {"JD3-PIE": {"BREATHY_RELEASE": 0.025}}   # per-voice overrides (v7: JD3's i after ɡʷʱ)
SPEAKER_H_TILT = {"M01-PIE": 1.0}   # M01's tract is brighter: 2 dB/oct put its h median at 0.63


def render(words, prefix, opt, engine, cadence, seed=0, pitch=None, accent=None):
    """Compile, synthesize, patch and write one clip. Returns (timed, total, words, audio)."""
    import numpy as np, wave
    globals()["ACCENT_RANGE"] = opt.accent_range if accent is None else accent
    import os, vtlengine
    tag = os.path.splitext(os.path.basename(opt.speaker))[0]
    timing = dict(ENGINE_TIMING[vtlengine.engine_kind(opt.speaker)], **SPEAKER_TIMING.get(tag, {}))
    for k, flag in (("GLOTTIS_ADVANCE", "glottis_advance"), ("ABDUCT_ADVANCE", "abduct_advance"),
                    ("ORAL_ADVANCE", "oral_advance"), ("BREATHY_RELEASE", "breathy_release")):
        v = getattr(opt, flag, None)
        globals()[k] = timing[k] if v is None else v
    globals()["PE_F0_COMP"] = opt.pe_f0_comp if getattr(opt, "pe_f0_comp", None) is not None else timing.get("PE_F0_COMP", PE_F0_COMP)
    if getattr(opt, "pe_k", None) is not None:
        globals()["PE_K"] = opt.pe_k
    else:
        globals()["PE_K"] = timing.get("PE_K", PE_K)
    if opt.h_tilt is not None:
        globals()["H_TILT"] = opt.h_tilt
    else:
        import vtlengine
        globals()["H_TILT"] = SPEAKER_H_TILT.get(tag, 2.0 if vtlengine.engine_kind(opt.speaker) == "2.4" else 0.0)
    timed, total, words = build_timeline(words, opt.rate, cadence=cadence)
    base = speaker_pitch(opt.speaker) if pitch is None else pitch
    with open(prefix + ".ges", "w", encoding="utf-8") as f:
        f.write(compile_score(timed, total, words, base))
    write_timings(prefix, timed, total, words)
    if opt.no_audio:
        return timed, total, words, None
    audio = engine.ges_to_audio(prefix + ".ges")
    n_target = int(round(total * 44100))                      # exact timeline length
    audio = np.pad(audio, (0, max(0, n_target - len(audio))))[:n_target]
    if not opt.no_patch:
        audio = patch_frication(audio, timed, opt.chi_level, opt.gamma_level, seed=seed)
        if opt.h_mode == "patch":
            audio = patch_aspiration(audio, timed, opt.h_level, engine, seed=seed + 1)
    if TRILL == "auto" or TRILL > 1:
        audio = patch_trill(audio, timed)
    if not opt.no_patch and PHRASE_END and PE_BREATH is not None:
        audio = patch_phrase_breath(audio, timed, engine, seed=seed + 2)
    audio = audio / (np.abs(audio).max() + 1e-9) * 0.89       # normalize to -1 dBFS
    with wave.open(prefix + ".wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(44100)
        w.writeframes((audio * 32767).astype("<i2").tobytes())
    return timed, total, words, audio


def load_timeline(path):
    words = json.load(open(path, encoding="utf-8"))
    return [dict(w, word=w.get("word", w["ipa"])) for w in words]


def run_batch(opt):
    """Render every timeline JSON in --batch (a .txt list of paths, or a folder) with every speaker
    in --speakers. One engine start per speaker, deterministic per-clip seed and variation,
    QC on every clip, manifest.jsonl in --out-dir."""
    import hashlib, os, random, time
    import qc, vtlengine
    src = opt.batch
    if os.path.isdir(src):
        files = sorted(os.path.join(src, f) for f in os.listdir(src) if f.endswith(".json"))
    else:
        base = os.path.dirname(os.path.abspath(src))
        files = [l.strip() if os.path.isabs(l.strip()) else os.path.join(base, l.strip())
                 for l in open(src, encoding="utf-8") if l.strip() and not l.startswith("#")]
    os.makedirs(opt.out_dir, exist_ok=True)
    speakers = [s.strip() for s in opt.speakers.split(",")]
    man = open(os.path.join(opt.out_dir, "manifest.jsonl"), "a", encoding="utf-8")
    n_pass = n_all = 0
    for spk in speakers:
        opt.speaker = spk
        eng = vtlengine.open_engine(spk)
        tag = os.path.splitext(os.path.basename(spk))[0]
        base_pitch = speaker_pitch(spk) if opt.pitch is None else opt.pitch
        for path in files:
            clip = os.path.splitext(os.path.basename(path))[0]
            seed = int(hashlib.sha1(f"{clip}|{tag}|{opt.seed}".encode()).hexdigest()[:8], 16)
            rnd = random.Random(seed)
            pitch = base_pitch + rnd.uniform(-opt.vary_pitch, opt.vary_pitch)
            accent = opt.accent_range + rnd.uniform(-opt.vary_accent, opt.vary_accent)
            prefix = os.path.join(opt.out_dir, f"{clip}__{tag}")
            t0 = time.time()
            timed, total, words, audio = render(load_timeline(path), prefix, opt, eng, True,
                                                seed=seed, pitch=pitch, accent=accent)
            rec = {"clip": clip, "speaker": tag, "source": path, "wav": prefix + ".wav",
                   "timing": prefix + ".json", "duration_s": round(total, 4), "seed": seed,
                   "pitch_st": round(pitch, 2), "accent_range_st": round(accent, 2),
                   "render_s": round(time.time() - t0, 1)}
            if audio is not None:
                rec["qc"] = qc.check(audio, 44100, json.load(open(prefix + ".json", encoding="utf-8")),
                                     min_lift=opt.qc_min_lift, min_voiced_ms=opt.qc_min_voiced_ms,
                                     final_h=opt.final_h, phrase_end=opt.phrase_end)
                rec["qc"].pop("vowels")
                n_pass += rec["qc"]["pass"]
            n_all += 1
            man.write(json.dumps(rec, ensure_ascii=False) + "\n"); man.flush()
            print(f"{clip}__{tag}: {total:.2f} s  pitch {pitch:.1f} st  accent {accent:.2f}  "
                  + ("QC pass" if rec.get("qc", {}).get("pass") else f"QC FAIL {rec.get('qc', {}).get('fails')}"))
        eng.close()
    print(f"{n_all} clips, {n_pass} passed QC → {os.path.join(opt.out_dir, 'manifest.jsonl')}")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", help="TEXT OUT_PREFIX, or OUT_PREFIX with --timeline; none with --batch")
    ap.add_argument("--timeline", help="cadence JSON: words with ipa, line, start, end, pause_after")
    ap.add_argument("--speaker", default="JD3-PIE.speaker", help="JD3-PIE (male) | W02-PIE (female) | M01-PIE (male)")
    ap.add_argument("--rate", type=float, default=1.0, help="speaking rate multiplier (text mode)")
    ap.add_argument("--pitch", type=float, default=None, help="baseline F0 in st (default: speaker rest F0 − 3 st)")
    ap.add_argument("--accent-range", type=float, default=ACCENT_RANGE, help="st above baseline on accented nuclei")
    ap.add_argument("--declination", default=f"{DECL_START},{DECL_END}", help="line start,end in st (e.g. 1.5,-2.5)")
    ap.add_argument("--final-fall", type=float, default=FINAL_FALL, help="st of extra fall through the line-final word")
    ap.add_argument("--accent-rise", type=float, default=ACCENT_RISE, help="s of rise into an accented nucleus")
    ap.add_argument("--accent-fall", type=float, default=ACCENT_FALL, help="s of fall after an accented nucleus")
    ap.add_argument("--lax-short", action="store_true", help="short e i o u on lax shapes E I O U")
    ap.add_argument("--trill", type=lambda v: v if v == "auto" else int(v), default=1,
                    help="r as an N-contact trill (1 = tap; 3 ≈ Spanish rr), or auto (v10.1: by position); contacts 2..N are patched")
    ap.add_argument("--voice-lead", type=float, default=VOICE_LEAD, help="s of fold adduction before voicing resumes")
    ap.add_argument("--voice-lead-share", type=float, default=VOICE_LEAD_SHARE, help="... at most this share of the voiceless sound")
    ap.add_argument("--oral-advance", type=float, default=None,
                    help="s the oral/velic tiers lead the score (default 0.030: releases land on the JSON time)")
    ap.add_argument("--abduct-advance", type=float, default=None,
                    help="s glottal openings lead the score (default per engine: pip 0, VTL 2.4 0.020)")
    ap.add_argument("--glottis-advance", type=float, default=None,
                    help="s voicing onsets lead the score (default per engine: pip 0.030, VTL 2.4 0.040)")
    ap.add_argument("--breathy-shape", default=BREATHY_SHAPE, help="glottis shape for ʱ (murmur|breathy)")
    ap.add_argument("--breathy-release", type=float, default=None,
                    help="s of murmur after ʱ, at most 1/3 of the next sound (default 0.040; JD3 0.025)")
    ap.add_argument("--breathy-dip", type=float, default=BREATHY_F0_DIP, help="st F0 dip at vowel onset after ʱ (0 = off)")
    ap.add_argument("--chi-level", type=float, default=-9.0, help="χ noise level, dB re neighbouring vowel")
    ap.add_argument("--gamma-level", type=float, default=-20.0, help="ɣ friction layer, dB re neighbouring vowel")
    ap.add_argument("--h-mode", choices=("vtl", "patch"), default=H_MODE, help="h from VTL's glottis, or the noise patch")
    ap.add_argument("--tb-release", type=float, default=TB_RELEASE, help="s early release of tongue-body constrictions")
    ap.add_argument("--labial-carry", type=float, default=LABIAL_CARRY, help="s Cʷ rounding carries into the next sound")
    ap.add_argument("--phrase-end", action=argparse.BooleanOptionalAction, default=PHRASE_END,
                    help="voice trails off before pauses ≥ 0.2 s (default on; --no-phrase-end = v8 behaviour)")
    ap.add_argument("--pe-k", type=float, default=None, help="phrase end: output dB per lung dB (default per engine)")
    ap.add_argument("--pe-f0-comp", type=float, default=None, help="phrase end: st F0 raise per lung dB (default per engine)")
    ap.add_argument("--pe-floor", type=float, default=PE_FLOOR, help="phrase end: st the F0 target may sink under the last nucleus")
    ap.add_argument("--pe-k-hum", type=float, default=PE_K_HUM, help=argparse.SUPPRESS)
    ap.add_argument("--pe-hum-tc", type=float, default=PE_HUM_TC, help=argparse.SUPPRESS)
    ap.add_argument("--pe-hum-lag", type=float, default=PE_HUM_LAG, help=argparse.SUPPRESS)
    ap.add_argument("--pe-breath", type=float, default=PE_BREATH,
                    help="phrase end: dB re the vowel of the breath after a final m n l's hum (--pe-breath -99 = none)")
    ap.add_argument("--pe-hum", type=float, default=PE_HUM, help="phrase end: s a final m n l may hum before the breath")
    ap.add_argument("--pe-tap", action="store_true", help="phrase end: keep a final r as a tap")
    ap.add_argument("--pe-lung", type=float, default=PE_LUNG, help="phrase end: lung pressure share the decay falls to")
    ap.add_argument("--pe-fall", type=float, default=PE_FALL, help="phrase end: extra F0 fall at line ends, st")
    ap.add_argument("--final-h", choices=("noise", "murmur"), default=FINAL_H,
                    help="word-final H: voiceless breath, or the vowel trailing into breathy voice (+ breath patch)")
    ap.add_argument("--final-h-dur", type=float, default=FINAL_H_DUR, help="s, murmured final H (target)")
    ap.add_argument("--final-h-open", type=float, default=FINAL_H_OPEN, help="share of a murmured final H that opens into breath")
    ap.add_argument("--final-h-lung", type=float, default=FINAL_H_LUNG, help="lung pressure the murmured final H decays towards (share)")
    ap.add_argument("--final-h-noise", type=float, default=FINAL_H_NOISE, help="dB breath layer of a murmured final H re a plain h")
    ap.add_argument("--final-h-fall", type=float, default=FINAL_H_FALL, help="st F0 fall across a murmured final H")
    ap.add_argument("--h-round-boost", type=float, default=H_ROUND_BOOST,
                    help="dB more h level when coloured by u/w (o: 2/3 of it)")
    ap.add_argument("--h-fade", type=float, default=H_FADE, help="s of fade-out on a word-final H")
    ap.add_argument("--h-level", type=float, default=-14.0, help="h patch level, dB re its neighbouring vowel")
    ap.add_argument("--h-duck", type=float, default=H_DUCK, help="share of VTL's own h interval replaced (0-1)")
    ap.add_argument("--h-tilt", type=float, default=None,
                    help="dB/oct brightening of the h noise (default per engine: pip 0, VTL 2.4 2)")
    ap.add_argument("--no-patch", action="store_true", help="raw VTL output, no frication/aspiration patch")
    ap.add_argument("--no-audio", action="store_true", help="only write the score and timing files")
    ap.add_argument("--batch", help="folder of timeline JSONs, or a .txt list of their paths")
    ap.add_argument("--speakers", default="JD3-PIE.speaker,W02-PIE.speaker", help="batch: comma-separated speakers")
    ap.add_argument("--out-dir", default="renders", help="batch: output folder (manifest.jsonl goes here)")
    ap.add_argument("--vary-pitch", type=float, default=0.0, help="batch: ± st random baseline shift per clip")
    ap.add_argument("--vary-accent", type=float, default=0.0, help="batch: ± st random accent height per clip")
    ap.add_argument("--seed", type=int, default=0, help="batch: master seed (per-clip seeds derive from it)")
    ap.add_argument("--qc-min-lift", type=float, default=2.5, help="batch QC: minimum accent lift in st")
    ap.add_argument("--qc-min-voiced-ms", type=float, default=40.0, help="batch QC: minimum voicing per vowel")
    a = ap.parse_args()
    d0, d1 = (float(x) for x in a.declination.split(","))
    globals().update(BREATHY_SHAPE=a.breathy_shape,
                     BREATHY_F0_DIP=a.breathy_dip, ACCENT_RANGE=a.accent_range,
                     DECL_START=d0, DECL_END=d1, FINAL_FALL=a.final_fall,
                     ACCENT_RISE=a.accent_rise, ACCENT_FALL=a.accent_fall, LAX_SHORT=a.lax_short, TRILL=a.trill,
                     VOICE_LEAD=a.voice_lead, VOICE_LEAD_SHARE=a.voice_lead_share, 
                     H_MODE=a.h_mode, H_DUCK=a.h_duck, H_FADE=a.h_fade,
                     LABIAL_CARRY=a.labial_carry, TB_RELEASE=a.tb_release,
                     H_ROUND_BOOST=a.h_round_boost, FINAL_H=a.final_h, FINAL_H_DUR=a.final_h_dur,
                     FINAL_H_FALL=a.final_h_fall, FINAL_H_OPEN=a.final_h_open, FINAL_H_LUNG=a.final_h_lung,
                     FINAL_H_NOISE=a.final_h_noise, PHRASE_END=a.phrase_end, PE_LUNG=a.pe_lung, PE_FALL=a.pe_fall,
                     PE_TAP=a.pe_tap, PE_FLOOR=a.pe_floor, PE_HUM=a.pe_hum,
                     PE_K_HUM=a.pe_k_hum, PE_HUM_LAG=a.pe_hum_lag, PE_HUM_TC=a.pe_hum_tc,
                     PE_BREATH=(None if a.pe_breath <= -90 else a.pe_breath))
    CONS["h"] = ("H", None, None, "aspirate" if a.h_mode == "vtl" else "h")

    if a.batch:
        return run_batch(a)
    if a.timeline:
        if len(a.inputs) != 1: ap.error("with --timeline give only OUT_PREFIX")
        prefix, words, cadence = a.inputs[0], load_timeline(a.timeline), True
    else:
        if len(a.inputs) != 2: ap.error("give TEXT OUT_PREFIX")
        text, prefix = a.inputs
        words, cadence = words_from_text(open(text, encoding="utf-8").read()), False
    eng = None
    if not a.no_audio:
        import vtlengine
        eng = vtlengine.open_engine(a.speaker)
    timed, total, words, audio = render(words, prefix, a, eng, cadence)
    print(f"{prefix}.ges  ({total:.3f} s, {len(words)} words, {sum(1 for x in timed if x[2])} phones)")
    print(f"{prefix}.json / .TextGrid / .tsv" + (f" / .wav ({len(audio) / 44100:.3f} s)" if audio is not None else ""))


if __name__ == "__main__":
    main()
