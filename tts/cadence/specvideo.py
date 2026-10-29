"""Render a shareable video of a render. The layout:
- a scrolling mel spectrogram with the PIE words riding under it, behind a fixed centre playhead;
- the current word lit;
- a full-length overview strip with its own playhead;
- the English of the current verse line.

The audio is muxed in. Output is H.264 + AAC, 1920×1080 by default.

    tts/vc/.venv-eval/bin/python -I tts/cadence/specvideo.py AUDIO TIMING.json OUT.mp4 \\
        --title "Proto-Indo-European · Hymn to Dawn" --subtitle "VocalTractLab → voice conversion · female voice" \\
        --english "Dawn, bright goddess, Daughter of Sky! You shone for us, ..."

TIMING is a pie_vtl.py render .json ({"words": [...]}) or a cadence .json (a list of words). Each word needs
word, line, start and end. --english is split into sentences, one per verse line, and shown while that line plays.
The images are drawn once with matplotlib. ffmpeg then scrolls them and switches the overlays, so a 30 s clip takes
seconds to render."""
import argparse, json, re, subprocess, tempfile
from pathlib import Path

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BG, FG, DIM, ACCENT = "#0b0d12", "#f1ece4", "#8a8f9c", "#ffb547"
FONT = "DejaVu Serif"                       # full IPA, subscripts and combining marks


def load_words(path):
    j = json.load(open(path, encoding="utf-8"))
    ws = j["words"] if isinstance(j, dict) else j
    return [dict(word=w.get("word", w.get("ipa")), line=w["line"], start=w["start"], end=w["end"]) for w in ws]


def figure(W, H, bg=None):
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    fig.patch.set_facecolor(bg or BG); fig.patch.set_alpha(1 if bg is not None else 0)
    return fig


def save(fig, path):
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)


def mel_db(y, sr, fmax, hop):
    M = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=hop, n_mels=160, fmax=fmax, power=2.0)
    return librosa.power_to_db(M, ref=np.max, top_db=75)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio"); ap.add_argument("timing"); ap.add_argument("out")
    ap.add_argument("--title", default="Proto-Indo-European")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--english", default="", help="translation; one sentence per verse line")
    ap.add_argument("--offset", type=float, default=0.0, help="seconds to add to the JSON times (e.g. an mp3's lead-in)")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--pps", type=float, default=300, help="scroll speed, pixels per second at 1080p")
    ap.add_argument("--fmax", type=float, default=8000)
    ap.add_argument("--cmap", default="magma")
    ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    W, H = map(int, a.size.split("x")); s = H / 1080              # s: scale for type and margins
    y, sr = librosa.load(a.audio, sr=None, mono=True)
    D = len(y) / sr
    words = load_words(a.timing)
    for w in words: w["start"] += a.offset; w["end"] += a.offset
    lines = {}
    for w in words:
        lo, hi = lines.get(w["line"], (w["start"], w["end"])); lines[w["line"]] = (min(lo, w["start"]), max(hi, w["end"]))
    english = [x.strip() for x in re.findall(r"[^.!?]+[.!?]?", a.english) if x.strip()]
    tmp = Path(tempfile.mkdtemp(prefix="specvideo-"))

    # layout (pixels, top-left origin)
    M = int(90 * s)
    OY0, OY1 = int(165 * s), int(225 * s)                          # overview strip
    SY0, SY1 = int(265 * s), int(745 * s)                          # scrolling spectrogram
    WY = int(770 * s)                                              # first word row
    EY = int(960 * s)                                              # English line (centre)
    PPS = a.pps * s; CX = W // 2                                   # playhead at the centre

    # ---- base: title, subtitle, overview spectrogram
    fig = figure(W, H, bg=BG)
    fig.text(M / W, 1 - 68 * s / H, a.title, color=FG, fontsize=40 * s, family=FONT, va="center")
    if a.subtitle:
        fig.text(M / W, 1 - 118 * s / H, a.subtitle, color=DIM, fontsize=21 * s, family=FONT, va="center")
    ax = fig.add_axes([M / W, 1 - OY1 / H, (W - 2 * M) / W, (OY1 - OY0) / H])
    ax.imshow(mel_db(y, sr, a.fmax, 512), origin="lower", aspect="auto", cmap=a.cmap, interpolation="bicubic",
              extent=[0, D, 0, 1], vmin=-75, vmax=0, alpha=0.9)
    ax.set_xlim(0, D); ax.set_ylim(0, 1); ax.axis("off")
    save(fig, tmp / "base.png")

    # ---- the scrolling strip: spectrogram + words, padded by half a screen on each side
    SW = int(D * PPS) + W; SH = WY + int(120 * s) - SY0
    fig = figure(SW, SH, bg=BG)
    sx = lambda t: CX + t * PPS                                    # strip x of time t
    ax = fig.add_axes([sx(0) / SW, 1 - (SY1 - SY0) / SH, (sx(D) - sx(0)) / SW, (SY1 - SY0) / SH])
    ax.imshow(mel_db(y, sr, a.fmax, 128), origin="lower", aspect="auto", cmap=a.cmap, interpolation="bicubic",
              extent=[0, D, 0, 1], vmin=-75, vmax=0)
    ax.set_xlim(0, D); ax.set_ylim(0, 1); ax.axis("off")
    for ln, (lo, hi) in sorted(lines.items()):
        fig.add_artist(plt.Line2D([sx(lo - 0.15) / SW] * 2, [1 - (SY1 - SY0) / SH, 1], color=FG, alpha=0.10, lw=1.2 * s))
    fig.canvas.draw(); r = fig.canvas.get_renderer()
    boxes, row_end = [], [-1e9, -1e9]
    for w in words:
        cx = sx((w["start"] + w["end"]) / 2)
        t = fig.text(cx / SW, 0.5, w["word"], color=FG, fontsize=26 * s, family=FONT, ha="center", va="top")
        bb = t.get_window_extent(r); half = bb.width / 2
        free = [cx - half > e + 14 * s for e in row_end]
        row = 0 if free[0] else 1 if free[1] else int(row_end[0] > row_end[1])
        row_end[row] = cx + half
        ty = WY - SY0 + row * 56 * s                               # strip y of the label top
        t.set_position((cx / SW, 1 - ty / SH))
        fig.add_artist(plt.Line2D([sx(w["start"]) / SW, sx(w["end"]) / SW], [1 - (SY1 - SY0 + 9 * s) / SH] * 2,
                                  color=FG, alpha=0.28, lw=2.2 * s, solid_capstyle="round"))
        boxes.append((cx - half - 10 * s, ty - 7 * s, bb.width + 20 * s, bb.height + 18 * s, w))
    save(fig, tmp / "strip.png")

    # ---- overlays: overview mask (right of its playhead), playhead glows, English lines
    fig = figure(W - 2 * M, OY1 - OY0, bg=BG); fig.patch.set_alpha(0.6); save(fig, tmp / "mask.png")
    gw = int(44 * s)

    def glow(path, h):
        fig = figure(gw, h); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
        xs = np.linspace(-1, 1, gw); g = np.exp(-(xs / 0.35) ** 2)[None, :] * np.ones((10, 1))
        rgba = np.zeros((10, gw, 4)); rgba[..., :3] = matplotlib.colors.to_rgb(ACCENT); rgba[..., 3] = 0.5 * g
        ax.imshow(rgba, aspect="auto", extent=[-1, 1, 0, 1]); ax.axvline(0, color=ACCENT, lw=2.4 * s)
        ax.set_xlim(-1, 1); ax.set_ylim(0, 1); save(fig, path)
    glow(tmp / "head.png", SY1 - SY0 + int(20 * s)); glow(tmp / "mini.png", OY1 - OY0 + int(10 * s))
    eng, starts = [], [lo for lo, _ in sorted(lines.values())]
    for i in range(min(len(english), len(starts))):
        fig = figure(W, int(90 * s))
        fig.text(0.5, 0.5, english[i], color=FG, alpha=0.92, fontsize=28 * s, family=FONT, style="italic",
                 ha="center", va="center")
        p = tmp / f"en{i}.png"; save(fig, p)
        eng.append((p, starts[i] - 0.15, (starts[i + 1] if i + 1 < len(starts) else D + 1) - 0.15))

    fig = figure(W, SH); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ramp = np.clip(np.minimum(np.arange(W), W - 1 - np.arange(W)) / (260 * s), 0, 1)
    rgba = np.zeros((2, W, 4)); rgba[..., :3] = matplotlib.colors.to_rgb(BG); rgba[..., 3] = (1 - ramp) ** 1.5
    ax.imshow(rgba, aspect="auto", extent=[0, 1, 0, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); save(fig, tmp / "edges.png")

    # ---- ffmpeg composition
    scroll = f"{PPS:.4f}*t"
    inputs = ["-loop", "1", "-framerate", str(a.fps), "-i", str(tmp / "base.png"), "-i", a.audio]
    for p in ("strip.png", "mask.png", "head.png", "mini.png"):
        inputs += ["-loop", "1", "-framerate", str(a.fps), "-i", str(tmp / p)]
    for p, _, _ in eng: inputs += ["-loop", "1", "-framerate", str(a.fps), "-i", str(p)]
    inputs += ["-loop", "1", "-framerate", str(a.fps), "-i", str(tmp / "edges.png")]
    hl = ",".join(f"drawbox=x={x:.0f}:y={yy:.0f}:w={w:.0f}:h={h:.0f}:color=0xffb547@0.18:t=fill:"
                  f"enable='between(t,{ww['start'] - 0.04:.3f},{ww['end'] + 0.04:.3f})'" for x, yy, w, h, ww in boxes)
    mini_x = f"{M}+{W - 2 * M}*t/{D:.4f}"
    f = [f"[2]{hl},crop=w={W}:h={SH}:x='{scroll}':y=0[s0]",
         f"[s0][{6 + len(eng)}]overlay=0:0[strip]",
         f"[0][strip]overlay=x=0:y={SY0}:shortest=1[v0]",
         f"[v0][3]overlay=x='{mini_x}':y={OY0}[v1]",
         f"[v1][4]overlay=x={CX - gw // 2}:y={SY0 - int(10 * s)}[v2]",
         f"[v2][5]overlay=x='{mini_x}-{gw // 2}':y={OY0 - int(5 * s)}[v3]"]
    v = "v3"
    for i, (p, t0, t1) in enumerate(eng):
        f.append(f"[{v}][{6 + i}]overlay=x=0:y={EY - int(45 * s)}:enable='between(t,{t0:.3f},{t1:.3f})'[e{i}]"); v = f"e{i}"
    f.append(f"[{v}]fade=t=in:st=0:d=0.5,fade=t=out:st={D - 0.4:.3f}:d=0.4,format=yuv420p[vout]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(f),
           "-map", "[vout]", "-map", "1:a", "-t", f"{D:.3f}", "-r", str(a.fps),
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print(a.out, f"{D:.1f} s, {W}×{H}")


if __name__ == "__main__":
    main()
