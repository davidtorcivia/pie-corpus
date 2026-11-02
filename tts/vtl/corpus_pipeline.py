"""The PIE speech corpus, end to end on one machine (tr-desktop WSL): VTL render -> ElevenLabs -> restore -> QC ->
Kokoro files. Every stage skips work already on disk, so a rerun resumes.

    python corpus_pipeline.py WORK [render] [eleven] [restore] [qc] [final]     (no stage names: all, in order)

WORK is a scripts/tts_build.py output (timelines/, batch.txt, clips.jsonl, manifest.jsonl, OOD_texts.txt).
Writes, all named CLIP__SPEAKER.wav:
  renders/   VTL v10.1, 44.1 kHz (+ .json phone timings, manifest.jsonl with VTL QC)
  eleven/    ElevenLabs voice changer, pcm_44100 -> 16-bit WAV (masters); eleven_log.jsonl (cost, request id)
  restored/  tts/cadence/restore.py, 44.1 kHz (masters)
  qc.jsonl   qc.py on restored/ (aligned to the render); gate below
  final/     24 kHz mono 16-bit PCM WAV (kikiri-tts / StyleTTS2), only clips that pass the gate
  train_list.txt, val_list.txt (FILE|LABEL|SPEAKER), OOD_texts.txt, rejected.jsonl, summary.json

Gate (floors only; brightness above the raw-render ranges is intended, owner 2026-11-02): after restore no h under
0.25 and no χ under 0.30 (2-8 kHz share), voiced share >= 0.97, accent lift >= 1.5 st, at most 1 weak vowel.
ElevenLabs (owner's settings, 2026-11-02): eleven_multilingual_sts_v2, stability 0.9, similarity 0, style 0, speaker
boost on, background-noise removal off. Key: ~/.config/elevenlabs/api_key.
"""
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
RESTORE = HERE / "restore.py" if (HERE / "restore.py").exists() else HERE.parent / "cadence" / "restore.py"
VOICES = {"JD3-PIE": "d0grukerEzs069eKIauC", "W02-PIE": "f1abxvIEijusskcPWE5x"}   # owner's ElevenLabs voices
MODEL = "eleven_multilingual_sts_v2"
SETTINGS = {"stability": 0.9, "similarity_boost": 0.0, "style": 0.0, "use_speaker_boost": True}
RENDER_ARGS = ["--accent-range", "4.0", "--final-h", "murmur", "--vary-pitch", "2", "--vary-accent", "0.4",
               "--seed", "0", "--qc-min-lift", "2.0"]
SPEAKER_FILES = ["JD3-PIE.speaker", "W02-PIE.speaker"]


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def manifest(work):
    return [json.loads(l) for l in open(work / "manifest.jsonl", encoding="utf-8")]


# ---------------------------------------------------------------- 1. render
def render(work, shards=40):
    todo = [m for m in manifest(work) if not (work / m["vtl_wav"]).exists() or not (work / m["vtl_timing"]).exists()]
    clips = sorted({m["clip"] for m in todo})
    if not clips:
        return log("render: nothing to do")
    log(f"render: {len(clips)} clips x 2 voices on {shards} shards")
    sh = work / "_shards"
    sh.mkdir(exist_ok=True)
    procs = []
    for k in range(shards):
        part = clips[k::shards]
        if not part:
            continue
        lst = sh / f"batch-{k:02d}.txt"
        lst.write_text("".join(f"{work}/timelines/{c}.json\n" for c in part), "utf-8")
        out = sh / f"out-{k:02d}"
        env = dict(os.environ, VTL24_LIB=str(HERE / "linux" / "libvtl24.so"))
        procs.append(subprocess.Popen([PY, str(HERE / "pie_vtl.py"), "--batch", str(lst), "--speakers",
                                       ",".join(str(HERE / s) for s in SPEAKER_FILES), "--out-dir", str(out),
                                       *RENDER_ARGS], cwd=HERE, env=env, stdout=open(sh / f"log-{k:02d}.txt", "w"),
                                      stderr=subprocess.STDOUT))
    for p in procs:
        p.wait()
    bad = [i for i, p in enumerate(procs) if p.returncode]
    (work / "renders").mkdir(exist_ok=True)
    with open(work / "renders" / "manifest.jsonl", "a", encoding="utf-8") as man:
        for out in sorted(sh.glob("out-*")):
            for f in out.iterdir():
                if f.name == "manifest.jsonl":
                    for line in open(f, encoding="utf-8"):
                        r = json.loads(line)
                        for k_ in ("wav", "timing"):
                            r[k_] = "renders/" + Path(r[k_]).name
                        man.write(json.dumps(r, ensure_ascii=False) + "\n")
                    f.unlink()
                else:
                    f.replace(work / "renders" / f.name)
    left = [m for m in manifest(work) if not (work / m["vtl_wav"]).exists()]
    log(f"render: done, {len(left)} missing, shard failures {bad}")


# ---------------------------------------------------------------- 2. ElevenLabs
def _multipart(fields, file_field, file_path):
    b = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    body += (f'--{b}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{Path(file_path).name}"\r\n'
             f"Content-Type: audio/wav\r\n\r\n").encode() + Path(file_path).read_bytes() + f"\r\n--{b}--\r\n".encode()
    return body, f"multipart/form-data; boundary={b}"


def _pcm_to_wav(pcm, path, sr=44100):
    import wave
    tmp = path.with_suffix(".part")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)
    tmp.replace(path)


def _convert(work, m, key):
    src, dst = work / m["vtl_wav"], work / m["eleven_wav"]
    body, ctype = _multipart({"model_id": MODEL, "voice_settings": json.dumps(SETTINGS),
                              "remove_background_noise": "false"}, "audio", src)
    url = f"https://api.elevenlabs.io/v1/voice-changer/{VOICES[m['speaker']]}?output_format=pcm_44100"
    for attempt in range(6):
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"xi-api-key": key, "Content-Type": ctype})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                pcm = r.read()
                _pcm_to_wav(pcm, dst)
                return {"file": dst.name, "cost": int(r.headers.get("character-cost") or 0),
                        "request_id": r.headers.get("request-id"), "seconds": round(len(pcm) / 2 / 44100, 3)}
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode("utf-8", "replace")
            if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                time.sleep(5 * 2 ** attempt); continue
            return {"file": dst.name, "error": e.code, "msg": msg}
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < 5:
                time.sleep(5 * 2 ** attempt); continue
            return {"file": dst.name, "error": "net", "msg": str(e)[:300]}


def eleven(work, workers=8):
    key = (Path.home() / ".config/elevenlabs/api_key").read_text().strip()
    (work / "eleven").mkdir(exist_ok=True)
    todo = [m for m in manifest(work) if (work / m["vtl_wav"]).exists() and not (work / m["eleven_wav"]).exists()]
    log(f"eleven: {len(todo)} files, {workers} at a time")
    n = cost = 0
    errors = []
    with open(work / "eleven_log.jsonl", "a", encoding="utf-8") as lg, cf.ThreadPoolExecutor(workers) as ex:
        for res in ex.map(lambda m: _convert(work, m, key), todo):
            lg.write(json.dumps(res) + "\n"); lg.flush()
            n += 1
            if "error" in res:
                errors.append(res)
                if res["error"] in (401, 402, 403):                 # auth / quota: stop, don't burn retries
                    log("eleven: STOP", res); ex.shutdown(cancel_futures=True); break
            else:
                cost += res["cost"]
            if n % 100 == 0:
                log(f"eleven: {n}/{len(todo)}, {cost} credits this run, {len(errors)} errors")
    log(f"eleven: done {n}, {cost} credits this run, {len(errors)} errors")


# ---------------------------------------------------------------- 3. restore
def _restore(work, m):
    out = work / m["restored_wav"]
    r = subprocess.run([PY, str(RESTORE), str(work / m["eleven_wav"]), str(work / m["vtl_wav"]),
                        str(work / m["vtl_timing"]), str(out)], capture_output=True, text=True)
    (out.with_suffix(".log")).write_text(r.stdout + r.stderr, "utf-8")
    return r.returncode


def restore(work, workers=40):
    (work / "restored").mkdir(exist_ok=True)
    todo = [m for m in manifest(work) if (work / m["eleven_wav"]).exists() and not (work / m["restored_wav"]).exists()]
    log(f"restore: {len(todo)}")
    with cf.ProcessPoolExecutor(workers) as ex:
        rcs = list(ex.map(_restore, [work] * len(todo), todo))
    log(f"restore: done, {sum(1 for x in rcs if x)} failures")


# ---------------------------------------------------------------- 4. QC
def _qc(work, m):
    r = subprocess.run([PY, str(HERE / "qc.py"), str(work / m["restored_wav"]), "--timing", str(work / m["vtl_timing"]),
                        "--ref", str(work / m["vtl_wav"]), "--final-h", "murmur", "--min-lift", "1.5"],
                       capture_output=True, text=True, cwd=HERE)
    try:
        q = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"clip": m["clip"], "speaker": m["speaker"], "pass": False, "why": ["qc error: " + r.stderr[-200:]]}
    why = []
    lost_h = [x for x in q["h_share"] if x < 0.25]
    lost_c = [x for x in q["chi_share"] if x < 0.30]
    if lost_h: why.append(f"h lost {len(lost_h)}/{len(q['h_share'])}")
    if lost_c: why.append(f"chi lost {len(lost_c)}/{len(q['chi_share'])}")
    if q["voiced_share"] < 0.97: why.append(f"voiced {q['voiced_share']}")
    if not q["accent_lift_st"] >= 1.5: why.append(f"accent lift {q['accent_lift_st']}")
    if len(q["weak_vowels"]) > 1: why.append(f"weak vowels {len(q['weak_vowels'])}")
    return {"clip": m["clip"], "speaker": m["speaker"], "pass": not why, "why": why,
            "accent_lift_st": q["accent_lift_st"], "voiced_share": q["voiced_share"], "weak": q["weak_vowels"],
            "short_voicing": q["short_voicing"], "phrase_end_fails": [f for f in q["fails"] if "phrase" in f]}


def qc(work, workers=40):
    ms = [m for m in manifest(work) if (work / m["restored_wav"]).exists()]
    with cf.ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_qc, [work] * len(ms), ms))
    with open(work / "qc.jsonl", "w", encoding="utf-8") as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    log(f"qc: {sum(r['pass'] for r in res)}/{len(res)} pass")


# ---------------------------------------------------------------- 5. final
def _final(src, dst):
    import librosa, numpy as np, soundfile as sf
    y, sr = librosa.load(str(src), sr=None, mono=True)
    y = librosa.resample(y, orig_sr=sr, target_sr=24000, res_type="soxr_vhq")
    pk = float(np.abs(y).max())
    if pk > 0.99:
        y = y / pk * 0.99
    tmp = dst.with_suffix(".part.wav")
    sf.write(str(tmp), y, 24000, subtype="PCM_16")
    tmp.replace(dst)
    return len(y) / 24000


def final(work, workers=40):
    import soundfile as sf
    q = {(r["clip"], r["speaker"]): r for r in map(json.loads, open(work / "qc.jsonl", encoding="utf-8"))}
    (work / "final").mkdir(exist_ok=True)
    ms = manifest(work)
    ok = [m for m in ms if q.get((m["clip"], m["speaker"]), {}).get("pass")]
    todo = [m for m in ok if not (work / m["final_wav"]).exists()]
    with cf.ProcessPoolExecutor(workers) as ex:
        list(ex.map(_final, [work / m["restored_wav"] for m in todo], [work / m["final_wav"] for m in todo]))
    lists = {"train": [], "val": []}
    secs = {"train": {}, "val": {}}
    bad_len = []
    for m in ok:
        f = work / m["final_wav"]
        d = sf.info(str(f)).duration
        ref = sf.info(str(work / m["vtl_wav"])).duration
        if abs(d - ref) > 0.05:
            bad_len.append((f.name, d, ref)); continue
        lists[m["split"]].append(f"{f.name}|{m['label']}|{m['kokoro_speaker']}")
        secs[m["split"]][m["kokoro_speaker"]] = secs[m["split"]].get(m["kokoro_speaker"], 0) + d
    for s in lists:
        (work / f"{s}_list.txt").write_text("\n".join(lists[s]) + "\n", "utf-8")
    with open(work / "rejected.jsonl", "w", encoding="utf-8") as f:
        for m in ms:
            r = q.get((m["clip"], m["speaker"]))
            if not r or not r["pass"]:
                f.write(json.dumps({"file": Path(m["final_wav"]).name, "why": r["why"] if r else ["missing"]},
                                   ensure_ascii=False) + "\n")
    summary = {"files": {s: len(v) for s, v in lists.items()},
               "hours": {s: {k: round(v / 3600, 3) for k, v in d.items()} for s, d in secs.items()},
               "rejected": len(ms) - len(ok), "length_mismatch": bad_len,
               "format": "WAV PCM_16 mono 24000 Hz", "list_format": "FILE|LABEL|SPEAKER (files relative to final/)"}
    (work / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), "utf-8")
    log("final:", json.dumps(summary))


STAGES = {"render": render, "eleven": eleven, "restore": restore, "qc": qc, "final": final}

if __name__ == "__main__":
    work = Path(sys.argv[1]).resolve()
    for s in sys.argv[2:] or list(STAGES):
        STAGES[s](work)
