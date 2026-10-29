"""Listening page + manifest for the eSpeak + voice-conversion test.

    tts/vc/.venv-eval/bin/python -I tts/vc/build_page.py
Reads tts/vc/results.json (evaluate.py), encodes every clip to AAC 48 kb/s in .mp4 with
`afconvert -f m4af -d aac -b 48000` into tts/vc/listening/audio/, writes tts/vc/listening/index.html and
tts/vc/manifest.json (fields mirror tts/bakeoff/manifest.json, schema pie-tts-bakeoff/1, plus VC fields)."""
import html
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import soundfile as sf

VC = Path(__file__).resolve().parent
sys.path.insert(0, str(VC))
from words import TIMBRES, WORDS  # noqa: E402

LIST = VC / "listening"
AUD = LIST / "audio"
R = json.loads((VC / "results.json").read_text("utf-8"))
SRC = {s["id"]: s for s in json.loads((VC / "audio" / "espeak.json").read_text("utf-8"))}
KOK = {(s["id"], s["voice"]): s for s in json.loads((VC / "audio" / "kokoro.json").read_text("utf-8"))}

METHODS = {
    "knnvc": dict(label="kNN-VC", licence="MIT (code, prematched HiFi-GAN); WavLM-Large MIT",
                  repo="bshall/knn-vc@c616845"),
    "openvoice": dict(label="OpenVoice V2", licence="MIT (code and weights)",
                      repo="myshell-ai/OpenVoice@74a1d14, myshell-ai/OpenVoiceV2@f36e7ed"),
    "seedvc": dict(label="Seed-VC", licence="GPL-3.0 (code and weights)", repo="Plachtaa/seed-vc@51383ef"),
    "seedvc-f0": dict(label="Seed-VC F0", licence="GPL-3.0 (code and weights)", repo="Plachtaa/seed-vc@51383ef"),
    "kokoro": dict(label="Kokoro alone", licence="Apache-2.0", repo="hexgrad/Kokoro-82M@f3ff357"),
}
TIMBRE_LABEL = {"hm_omega": "hm_omega", "ef_dora": "ef_dora", "em_alex": "em_alex"}
# bake-off target/variant ids (tts/bakeoff/manifest.json); every source here is the converter default
TARGET = {"h2ewsos": ("h2", "chi"), "h2owis": ("h2", "chi"), "h2egjeti": ("dorsal", "palatal"),
          "gjenh1tor": ("dorsal", "palatal"), "kjlewos": ("dorsal", "palatal"), "bhreh2ter": ("murmur", "breathy"),
          "dhugh2ter": ("murmur", "breathy"), "gwhenti": ("murmur", "breathy"), "kwetwores": ("kw", "labialized"),
          "h3esth1": ("h3", "gw-labialized"), "wlkwos": ("syllabic", "syllabic"), "kmtom": ("syllabic", "syllabic"),
          "ph2ter": ("vocalized", "default"), "dyews": ("accent", "default"), "h1esti": ("h1", "h"),
          "ghime": ("accent", "default"), "hymn-1": ("line", "default"), "hymn-2": ("line", "default")}
GLOSS = {"h2ewsos": "dawn", "h2owis": "sheep", "h2egjeti": "drives", "gjenh1tor": "begetter", "kjlewos": "fame",
         "bhreh2ter": "brother", "dhugh2ter": "daughter", "gwhenti": "strikes", "kwetwores": "four",
         "h3esth1": "bone", "wlkwos": "wolf", "kmtom": "hundred", "ph2ter": "father", "dyews": "sky, day",
         "h1esti": "is", "ghime": "in winter",
         "hymn-1": "Dawn, bright goddess, Daughter of Sky!",
         "hymn-2": "You shone for us, and darkness fled from you."}


def enc(wav: Path, rel: str) -> dict:
    out = AUD / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.stat().st_mtime < wav.stat().st_mtime:
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", "-b", "48000", str(wav), str(out)], check=True)
    y, sr = sf.read(wav, dtype="float32", always_2d=True)
    y = y.mean(1)
    loud = np.flatnonzero(np.abs(y) > 0.02)
    return dict(audio=rel, duration_s=round(len(y) / sr, 3),
                speech_s=round((loud[-1] - loud[0]) / sr, 3) if len(loud) else 0.0,
                peak=round(float(np.abs(y).max()), 3), clipped=int((np.abs(y) >= 0.999).sum()), rate=sr)


clips, cells = [], {}
for wid, pie, target in WORDS:
    s = SRC[wid]
    tgt, var = TARGET[wid]
    a = enc(Path(s["wav"]), f"src/{wid}.mp4")
    rec = dict(id=f"{wid}__{var}__espeak-tone", word=wid, variant=var, system="espeak-tone", **a,
               ipa=s["ipa"], engine_input=s["engine_input"], profile=None, same_as=None, qc=dict(ok=True, flags=[]),
               pie=pie, target=target, method="espeak-source", timbre=None, wav=s["wav"], mp4=str(AUD / a["audio"]),
               metrics={k: R["sources"][wid][k] for k in ("rec", "per_ipa", "contrast", "peak")})
    clips.append(rec)
    cells[(wid, "src", None)] = rec
for r in R["clips"]:
    if r["method"].startswith("ctrl"):
        continue
    wid, m, v = r["id"], r["method"], r["timbre"]
    tgt, var = TARGET[wid]
    sysid = f"kokoro-{v}" if m == "kokoro" else f"vc-{m}-{v}"
    a = enc(Path(r["wav"]), f"{m}/{wid}.{v}.mp4")
    pie = SRC[wid]["pie"]
    engine = KOK[(wid, v)]["engine_input"] if m == "kokoro" else SRC[wid]["engine_input"]
    rec = dict(id=f"{wid}__{var}__{sysid}", word=wid, variant=var, system=sysid, **a, ipa=SRC[wid]["ipa"],
               engine_input=engine, profile=None, same_as=None, qc=dict(ok=a["clipped"] == 0, flags=[] if a["clipped"] == 0 else ["clipped"]),
               pie=pie, target=SRC[wid]["target"], method=m, timbre=v, wav=r["wav"], mp4=str(AUD / a["audio"]),
               source_wav=SRC[wid]["wav"],
               metrics={k: r[k] for k in ("rec", "per_src", "per_src_base", "per_ipa", "f0_r", "peak_src", "peak",
                                          "peak_ok", "contrast_src", "contrast", "contrast_ratio", "dur_ratio", "len_ratio")})
    clips.append(rec)
    cells[(wid, m, v)] = rec
refs = {}
for v in TIMBRES:
    refs[v] = enc(VC / "audio" / "ref" / f"{v}.wav", f"ref/{v}.mp4")

systems = [dict(id="espeak-tone", label="eSpeak (tone)", family="espeak", language="pie (hi base)",
                licence="GPL-3.0 engine; output unrestricted", reference=True)]
for m, d in METHODS.items():
    for v in TIMBRES:
        systems.append(dict(id=f"kokoro-{v}" if m == "kokoro" else f"vc-{m}-{v}",
                            label=f"{d['label']} {v}" if m == "kokoro" else f"eSpeak→{d['label']} {v}",
                            family="kokoro" if m == "kokoro" else "vc", method=m, voice=v, licence=d["licence"],
                            repo=d["repo"], reference=False))
bake = json.loads((VC.parent / "bakeoff" / "manifest.json").read_text("utf-8")) if (VC.parent / "bakeoff" / "manifest.json").exists() else {}
words = [dict(id=w, pie=p, gloss=GLOSS[w], target=TARGET[w][0], ipa=SRC[w]["ipa"], sound=t) for w, p, t in WORDS]
manifest = dict(schema="pie-tts-bakeoff/1", source="vc", generated=str(date.today()), audio_base="listening/audio/",
                settings=dict(espeak=dict(voice="pie/pie-tone", version="1.52.0", rate=130, round_trip="strict"),
                              kokoro=dict(model="hexgrad/Kokoro-82M@f3ff3571791e39611d31c381e3a41a3af07b4987",
                                          pitch_patch=True, speed=0.9, profile=None),
                              references={v: dict(audio=refs[v]["audio"], seconds=refs[v]["duration_s"]) for v in TIMBRES},
                              audio="AAC 48 kb/s in .mp4 (afconvert -f m4af -d aac -b 48000)",
                              metrics="tts/vc/evaluate.py; docs/research/tts-voice-conversion.md"),
                targets=bake.get("targets", []), words=words, systems=systems,
                summary=R["summary"], clips=clips)
(VC / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")

# ------------------------------------------------------------------ page
S = R["summary"]


def fmt(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def chip_per(x, floor):
    if x is None:
        return "na"
    return "good" if x <= floor + 0.15 else "warn" if x <= floor + 0.35 else "bad"


def chip_r(x):
    if x is None:
        return "na"
    return "good" if x >= 0.7 else "warn" if x >= 0.4 else "bad"


FLOOR = S["ctrl-espeak-p80"]["all"]["per_src"]
rows = []
for m, d in METHODS.items():
    a = S[m]["all"]
    rows.append(f"""<tr><th scope="row">{d['label']}</th><td class="{chip_per(a['per_src'], FLOOR)}">{fmt(a['per_src'])}</td>
<td>{fmt(S[m]['lines']['per_src'])}</td><td>{fmt(a['post_dtw'] * 1000, 1)}</td><td>{fmt(a['per_ipa'])}</td><td class="{chip_r(a['f0_r_median'])}">{fmt(a['f0_r_median'])}</td>
<td>{fmt(a['contrast_ratio'])}</td><td>{fmt(a['peak_ok'] * 100, 0)}%</td><td>{fmt(a['dur_ratio'])}</td></tr>""")
CTRL = {"ctrl-aac": "Control: source after AAC", "ctrl-espeak-p80": "Control: eSpeak at pitch 80",
        "ctrl-shift3": "Control: source +3 semitones"}
for k, lab in CTRL.items():
    c = S[k]["all"]
    rows.append(f"""<tr class="ctrl"><th scope="row">{lab}</th><td>{fmt(c['per_src'])}</td><td>{fmt(S[k]['lines']['per_src'])}</td>
<td>{fmt(c['post_dtw'] * 1000, 1)}</td><td>{fmt(c['per_ipa'])}</td>
<td>{fmt(c['f0_r_median'])}</td><td>{fmt(c['contrast_ratio'])}</td><td>{fmt(c['peak_ok'] * 100, 0)}%</td><td>{fmt(c['dur_ratio'])}</td></tr>""")
summary_table = "\n".join(rows)


def play(rel, label, extra=""):
    return f'<button class="play" type="button" data-src="audio/{html.escape(rel)}" aria-label="Play {html.escape(label)}"><span class="tri" aria-hidden="true"></span>{extra}</button>'


sections = []
for wid, pie, target in WORDS:
    src = cells[(wid, "src", None)]
    head = f"""<header class="wh"><div class="form"><span class="pie">{html.escape(pie)}</span>
<span class="ipa">[{html.escape(SRC[wid]['ipa'])}]</span></div><div class="meta"><span class="gloss">‘{html.escape(GLOSS[wid])}’</span>
<span class="tag">{html.escape(target)}</span></div></header>"""
    srcrow = f"""<div class="srcrow">{play(src['audio'], pie + ' eSpeak source', '<span>eSpeak source</span>')}
<span class="rec" title="recognizer output on the source">heard as <code>{html.escape(src['metrics']['rec'])}</code></span></div>"""
    grid = ['<div class="grid" role="table"><div class="gh" role="row"><span role="columnheader"></span>' +
            "".join(f'<span role="columnheader">{TIMBRE_LABEL[v]}</span>' for v in TIMBRES) + "</div>"]
    for m, d in METHODS.items():
        cellhtml = []
        for v in TIMBRES:
            cl = cells.get((wid, m, v))
            if not cl:
                cellhtml.append('<span class="cell na" role="cell">missing</span>')
                continue
            mt = cl["metrics"]
            cellhtml.append(f"""<span class="cell" role="cell">{play(cl['audio'], f"{pie} {d['label']} {v}")}
<span class="nums"><span class="{chip_per(mt['per_src'], FLOOR)}" title="phone edit distance vs source">PER {fmt(mt['per_src'])}</span>
<span class="{chip_r(mt['f0_r'])}" title="F0 correlation with source">r {fmt(mt['f0_r'])}</span>
<span title="speech-span duration / source">×{fmt(mt['dur_ratio'])}</span></span>
<code class="heard" title="recognizer output">{html.escape(mt['rec'])}</code></span>""")
        grid.append(f'<div class="gr{" kok" if m == "kokoro" else ""}" role="row"><span class="mlabel" role="rowheader">{d["label"]}</span>{"".join(cellhtml)}</div>')
    grid.append("</div>")
    sections.append(f'<section class="word" id="{wid}">{head}{srcrow}{"".join(grid)}</section>')

refrow = "".join(play(refs[v]["audio"], f"{v} reference", f"<span>{v} · {refs[v]['duration_s']:.0f} s</span>") for v in TIMBRES)
page = f"""<title>PIE Voice Conversion</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gentium+Book+Plus:ital,wght@0,400;0,700;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: one listening column; per word a source row then a method × timbre grid (stacks to cards on phones). */
:root {{
  --bg: #f3f4f1; --surface: #fbfbf9; --fg: #1f2422; --muted: #5d6662; --line: #d5d9d4;
  --accent: #2f5d62; --accent-soft: #dde8e7;
  --good: #2e6b3a; --good-bg: #e1efe2; --warn: #7a5a12; --warn-bg: #f4ead0; --bad: #8f2d24; --bad-bg: #f5dfdb;
  --f-display: "Gentium Book Plus", "Charis SIL", "Doulos SIL", Georgia, serif;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #151918; --surface: #1d2321; --fg: #e3e7e4; --muted: #9aa49f; --line: #333b38;
  --accent: #8cc4c4; --accent-soft: #24393a;
  --good: #9fd6a6; --good-bg: #1f3424; --warn: #e4c77a; --warn-bg: #3a3119; --bad: #f0a197; --bad-bg: #42231f; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #151918; --surface: #1d2321; --fg: #e3e7e4; --muted: #9aa49f; --line: #333b38;
  --accent: #8cc4c4; --accent-soft: #24393a;
  --good: #9fd6a6; --good-bg: #1f3424; --warn: #e4c77a; --warn-bg: #3a3119; --bad: #f0a197; --bad-bg: #42231f; color-scheme: dark }}
body {{ background: var(--bg); color: var(--fg); font: 15px/1.5 var(--f-body);
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 24px 64px; }}
main {{ max-width: 1040px; margin: 0 auto; display: flex; flex-direction: column; gap: 28px; }}
h1 {{ font: 700 2rem/1.15 var(--f-display); margin: 0; text-wrap: balance; }}
h2 {{ font: 600 1.05rem/1.3 var(--f-body); margin: 0; letter-spacing: .02em; }}
p {{ margin: 0; max-width: 68ch; }}
.intro {{ display: flex; flex-direction: column; gap: 10px; }}
.lede {{ color: var(--muted); }}
.panel {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px; display: flex; flex-direction: column; gap: 12px; min-width: 0; }}
.tablewrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; font-size: .9rem; }}
th, td {{ text-align: right; padding: 6px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }}
th[scope=row], thead th:first-child {{ text-align: left; }}
thead th {{ font-weight: 500; color: var(--muted); font-size: .78rem; text-transform: uppercase; letter-spacing: .05em; vertical-align: bottom; white-space: normal; }}
tr.ctrl {{ color: var(--muted); font-style: italic; }}
td.good, .nums .good {{ color: var(--good); background: var(--good-bg); }}
td.warn, .nums .warn {{ color: var(--warn); background: var(--warn-bg); }}
td.bad, .nums .bad {{ color: var(--bad); background: var(--bad-bg); }}
.note {{ font-size: .85rem; color: var(--muted); }}
.refs, .srcrow {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
.play {{ display: inline-flex; align-items: center; gap: 8px; border: 1px solid var(--accent); background: var(--surface); color: var(--accent);
  border-radius: 999px; padding: 5px 12px 5px 9px; font: 500 .85rem var(--f-body); cursor: pointer; }}
.play:hover {{ background: var(--accent-soft); }}
.play:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.play .tri {{ width: 0; height: 0; border-left: 9px solid currentColor; border-top: 6px solid transparent; border-bottom: 6px solid transparent; }}
.play.on {{ background: var(--accent); color: var(--surface); }}
.play.on .tri {{ border: 0; width: 9px; height: 10px; border-left: 3px solid currentColor; border-right: 3px solid currentColor; box-sizing: border-box; }}
.word {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px; display: flex; flex-direction: column; gap: 12px; scroll-margin-top: 16px; }}
.wh {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 6px 16px; }}
.form {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 4px 14px; min-width: 0; }}
.pie {{ font: 700 1.6rem/1.2 var(--f-display); }}
.ipa {{ font: 400 1.15rem var(--f-display); color: var(--muted); }}
.meta {{ display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; }}
.gloss {{ font-family: var(--f-display); font-style: italic; }}
.tag {{ font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--accent); border: 1px solid var(--line); border-radius: 4px; padding: 1px 6px; }}
.rec {{ font-size: .82rem; color: var(--muted); }}
code {{ font-family: var(--f-mono); font-size: .8rem; }}
.grid {{ display: flex; flex-direction: column; border-top: 1px solid var(--line); }}
.gh, .gr {{ display: grid; grid-template-columns: 8.5rem repeat(3, minmax(0, 1fr)); gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--line); align-items: start; }}
.gh {{ font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); padding-block: 6px; }}
.gr.kok {{ background: linear-gradient(var(--accent-soft), var(--accent-soft)) left / 3px 100% no-repeat; padding-left: 0; }}
.mlabel {{ font-weight: 600; font-size: .88rem; padding-top: 6px; padding-left: 8px; }}
.cell {{ display: flex; flex-direction: column; gap: 4px; min-width: 0; }}
.cell .play {{ align-self: flex-start; padding: 5px 10px 5px 9px; }}
.nums {{ display: flex; flex-wrap: wrap; gap: 4px; font: 500 .74rem var(--f-mono); font-variant-numeric: tabular-nums; }}
.nums span {{ padding: 0 4px; border-radius: 3px; }}
.heard {{ color: var(--muted); font-size: .72rem; overflow-wrap: anywhere; }}
.na {{ color: var(--muted); font-size: .8rem; }}
nav.jump {{ display: flex; flex-wrap: wrap; gap: 6px 12px; font-family: var(--f-display); }}
nav.jump a {{ color: var(--accent); text-decoration: none; }}
nav.jump a:hover {{ text-decoration: underline; }}
@media (max-width: 640px) {{
  .gh {{ display: none; }}
  .gr {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  .mlabel {{ grid-column: 1 / -1; padding: 0 0 0 8px; }}
  .heard {{ display: none; }}
}}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; }} }}
</style>
<main>
<div class="intro">
<h1>eSpeak re-voiced: does the phonetics survive?</h1>
<p class="lede">Each PIE word is rendered by eSpeak with the project's phoneme table and tone voice, then converted to a natural Kokoro timbre by three open voice-conversion systems. Kokoro alone, with the pitch patch, is the comparison row. The numbers under each clip are measured against the eSpeak source.</p>
</div>
<section class="panel" aria-labelledby="sum">
<h2 id="sum">Averages over 18 items × 3 timbres</h2>
<div class="tablewrap"><table>
<thead><tr><th>System</th><th>Phone edit distance vs source</th><th>Same, hymn lines only</th><th>Logit DTW distance ×1000</th><th>Phone edit distance vs IPA</th><th>F0 r (median)</th><th>Accent contrast kept</th><th>F0 peak on accent</th><th>Duration ratio</th></tr></thead>
<tbody>
{summary_table}
</tbody></table></div>
<p class="note">Edit distance uses a wav2vec2 phone recognizer (xlsr-53-espeak-cv-ft) on the source and on each clip, divided by the source length. The recognizer never outputs χ, ʔ or murmured stops, so it measures how stable the heard phone string is, not whether the PIE sounds are right. The control rows change nothing phonetic: the source after the page's AAC encoding, the same eSpeak codes rendered at a higher pitch, and the source pitch-shifted by a phase vocoder. They show how much the recognizer moves on its own; on 1-second words that is a lot, so the hymn-line column and the logit DTW distance (frame-level, continuous) are the steadier guides. Accent contrast kept is the semitone gap between the source's high-tone frames and the rest, in the clip, divided by the same gap in the source. Green, amber and red mark distance within 0.15, 0.35 or more of the eSpeak-pitch control, and F0 r of at least 0.7, 0.4 or less.</p>
</section>
<section class="panel" aria-labelledby="refh">
<h2 id="refh">Target timbre references (Kokoro, plain speech)</h2>
<div class="refs">{refrow}</div>
<p class="note">hm_omega reads English; ef_dora and em_alex read Spanish. kNN-VC can only reuse frames that exist in these clips.</p>
</section>
<nav class="jump" aria-label="Words">{"".join(f'<a href="#{w}">{html.escape(p)}</a>' for w, p, _ in WORDS)}</nav>
{"".join(sections)}
</main>
<script>
(() => {{
  const audio = new Audio();
  let cur = null;
  const reset = () => {{ if (cur) cur.classList.remove("on"); cur = null; }};
  audio.addEventListener("ended", reset);
  audio.addEventListener("error", reset);
  document.addEventListener("click", (e) => {{
    const b = e.target.closest(".play");
    if (!b) return;
    if (cur === b && !audio.paused) {{ audio.pause(); reset(); return; }}
    reset();
    audio.src = b.dataset.src;
    audio.currentTime = 0;
    audio.play().then(() => {{ cur = b; b.classList.add("on"); }}).catch(reset);
  }});
}})();
</script>
"""
(LIST / "index.html").write_text(page, "utf-8")
files = sorted(str(p.relative_to(LIST)) for p in AUD.rglob("*.mp4"))
(LIST / "files.txt").write_text("index.html\n" + "\n".join(files) + "\n", "utf-8")
print(len(clips), "clips;", len(files), "mp4 files")
