"""Build the PIE speech set for VocalTractLab: choose clips, write their timelines, labels and manifests.

    uv run python -I scripts/tts_build.py pilot OUT          # ~24 clips across genres, both voices
    uv run python -I scripts/tts_build.py full OUT --hours 5 # per voice (owner: 10 h total, 2 voices)

OUT gets:
  timelines/CLIP.json        pie_vtl.py --batch input (one per clip; both voices render the same clips)
  batch.txt                  the list of timelines for --batch
  clips.jsonl                one line per clip: id, records, genre, verse, pie, english, label, duration, split
  manifest.jsonl             one line per clip x voice: file names at every stage, Kokoro speaker, label
  eleven_jobs.csv            the ElevenLabs speech-to-speech step: in, out, voice (VOICE_ID placeholder)
  README.txt                 the pipeline and the audio spec
Text only: nothing is rendered here (tts/vtl/pie_vtl.py does that, after this).
"""
import argparse
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pie import tts_data as T  # noqa: E402

VOICES = {"JD3-PIE": "VOICE_ID_MALE", "W02-PIE": "VOICE_ID_FEMALE"}   # ElevenLabs targets: placeholders (owner)


def works() -> dict[str, list[dict]]:
    out = collections.defaultdict(list)
    for f in sorted((ROOT / "corpus").glob("*/*.jsonl")):
        for line in open(f, encoding="utf-8"):
            r = json.loads(line)
            if r.get("pie"):
                out[r.get("work_id") or r["id"]].append(r)
    for recs in out.values():
        recs.sort(key=lambda r: (r.get("line_no") or 0, r["id"]))
    return out


def all_clips() -> list[tuple[str, T.Clip]]:
    return [(w, c) for w, recs in works().items() for c in T.clips_for_work(recs)]


def h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:12], 16)


PILOT = [  # (name, n, predicate) — chosen in hash order, train split only
    ("question dialogue", 4, lambda c: c.genre == "dialogue" and "?" in c.pie and 5 <= c.duration <= 14),
    ("plain dialogue", 2, lambda c: c.genre == "dialogue" and "?" not in c.pie and 5 <= c.duration <= 14),
    ("comma prose", 2, lambda c: not c.verse and c.pie.count(",") >= 2 and c.duration <= 14),
    ("myth/narrative", 3, lambda c: c.genre in ("myth", "narrative", "tale") and 6 <= c.duration <= 15),
    ("law/proverb/wisdom", 3, lambda c: c.genre in ("law", "proverb", "wisdom") and 2 <= c.duration <= 10),
    ("fable", 2, lambda c: c.genre == "fable" and c.id.startswith("t3") and 3 <= c.duration <= 12),
    ("schleicher (tier 1)", 1, lambda c: c.id.startswith("t1-schleicher") and 3 <= c.duration <= 12),
    ("king and god (tier 1)", 1, lambda c: c.id.startswith("t1-king") and 3 <= c.duration <= 12),
    ("hymn verse", 2, lambda c: c.verse and c.genre == "hymn"),
    ("prayer/charm verse", 2, lambda c: c.verse and c.genre in ("prayer", "charm", "praise")),
    ("epic", 1, lambda c: c.genre == "epic" and not c.verse and 3 <= c.duration <= 12),
    ("short line", 1, lambda c: not c.verse and 1.5 <= c.duration <= 3),
]


def pick_pilot(clips):
    chosen, seen, report = [], set(), []
    for name, n, pred in PILOT:
        cands = sorted((x for x in clips if x[1].id not in seen and T.split_of(x[1], x[0]) == "train" and pred(x[1])),
                       key=lambda x: h("pilot|" + x[1].id))[:n]
        if len(cands) < n:
            raise SystemExit(f"pilot: only {len(cands)} clips for {name!r}")
        for x in cands:
            seen.add(x[1].id)
            chosen.append(x)
            report.append((name, x[1].id))
    return chosen, report


def pick_full(clips, hours):
    """Every clip of tiers 1, 2 and 3b and every verse clip; then Tier 3 in hash order, at most 40% of the hours
    from dialogue, until `hours` per voice; val clips (5% of works, by hash) on top, capped at 4% of the hours."""
    must = [x for x in clips if not x[1].id.startswith("t3-") or x[1].verse]
    rest = sorted((x for x in clips if x not in must), key=lambda x: h("full|" + x[1].id))
    budget, dial_cap = hours * 3600, 0.4 * hours * 3600
    tr = [x for x in must if T.split_of(x[1], x[0]) == "train"]
    va = [x for x in must if T.split_of(x[1], x[0]) == "val"]
    t = sum(c.duration for _, c in tr)
    tv = sum(c.duration for _, c in va)
    dial = sum(c.duration for _, c in tr if c.genre == "dialogue")
    for x in rest:
        c = x[1]
        if T.split_of(c, x[0]) == "val":
            if tv + c.duration <= 0.04 * budget:
                va.append(x); tv += c.duration
            continue
        if t + c.duration > budget:
            continue
        if c.genre == "dialogue":
            if dial + c.duration > dial_cap:
                continue
            dial += c.duration
        tr.append(x); t += c.duration
    return tr + va


def write(out: Path, chosen, ood):
    (out / "timelines").mkdir(parents=True, exist_ok=True)
    with open(out / "clips.jsonl", "w", encoding="utf-8") as fc, open(out / "manifest.jsonl", "w", encoding="utf-8") as fm, \
            open(out / "batch.txt", "w", encoding="utf-8") as fb, open(out / "eleven_jobs.csv", "w", newline="") as fe:
        ej = csv.writer(fe)
        ej.writerow(["in_wav", "out_wav", "voice_id", "model_id", "output_format"])
        for w, c in chosen:
            label = c.label
            tl = out / "timelines" / f"{c.id}.json"
            tl.write_text(json.dumps(c.timeline(), ensure_ascii=False, indent=1), "utf-8")
            fb.write(f"timelines/{c.id}.json\n")
            split = T.split_of(c, w)
            fc.write(json.dumps({"id": c.id, "work": w, "records": c.records, "genre": c.genre, "verse": c.verse,
                                 "pie": c.pie, "english": c.english, "label": label, "duration_s": round(c.duration, 3),
                                 "split": split}, ensure_ascii=False) + "\n")
            for spk, kspk in T.SPEAKERS.items():
                name = T.filename(c.id, spk)
                fm.write(json.dumps({"clip": c.id, "speaker": spk, "kokoro_speaker": kspk, "split": split,
                                     "vtl_wav": f"renders/{name}", "vtl_timing": f"renders/{name[:-4]}.json",
                                     "eleven_wav": f"eleven/{name}", "restored_wav": f"restored/{name}",
                                     "final_wav": f"final/{name}", "label": label}, ensure_ascii=False) + "\n")
                ej.writerow([f"renders/{name}", f"eleven/{name}", VOICES[spk], "eleven_multilingual_sts_v2",
                             "pcm_44100"])
    (out / "OOD_texts.txt").write_text("\n".join(ood) + "\n", "utf-8")
    (out / "README.txt").write_text(README, "utf-8")


README = """PIE speech set (pie/tts_data.py, scripts/tts_build.py)

Pipeline per clip x voice (file name CLIP__SPEAKER.wav at every stage, ASCII):
  1. renders/   tts/vtl/pie_vtl.py v10.1 --batch batch.txt --speakers JD3-PIE.speaker,W02-PIE.speaker
                --out-dir renders --final-h murmur --accent-range 4.0 --vary-pitch 2 --vary-accent 0.4 --seed 0
                (44.1 kHz; writes .wav .json .TextGrid .tsv .ges and manifest.jsonl with QC)
  2. eleven/    ElevenLabs speech-to-speech, eleven_jobs.csv (voice ids are placeholders), pcm_44100
  3. restored/  tts/cadence/restore.py (re-lays any h / chi the converter deleted, on the renders/ timing)
  4. QC         tts/vtl/qc.py --manifest renders/manifest.jsonl --dir restored/
  5. final/     24 kHz, mono, 16-bit PCM WAV (kikiri-tts / StyleTTS2); same names

Kokoro lists (made after step 5 from manifest.jsonl): train_list.txt / val_list.txt lines
  CLIP__SPEAKER.wav|LABEL|pie_m  (or pie_f), file names relative to the audio dir; OOD_texts.txt: labels only.
Labels: to_ipa per word, NFD, syllable dots and clitic hyphens dropped, punctuation kept; symbols outside
Kokoro's vocab on unused ids: ʱ 7, ʷ 8, U+0329 (syllabic) 26, U+0301 (accent) 27.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("pilot", "full"))
    ap.add_argument("out", type=Path)
    ap.add_argument("--hours", type=float, default=5.0, help="per voice (full)")
    a = ap.parse_args()
    clips = all_clips()
    if a.mode == "pilot":
        chosen, report = pick_pilot(clips)
        for name, cid in report:
            print(f"{name:24s} {cid}")
    else:
        chosen = pick_full(clips, a.hours)
    ids = {c.id for _, c in chosen}
    recs_used = {r for _, c in chosen for r in c.records}
    ood = [c.label for w, c in sorted(clips, key=lambda x: h("ood|" + x[1].id))
           if c.id not in ids and not set(c.records) & recs_used and len(c.label) >= 50][:500]
    write(a.out, chosen, ood)
    by = collections.Counter()
    for w, c in chosen:
        by[(T.split_of(c, w), c.genre if c.genre in ("dialogue",) else "verse" if c.verse else "other")] += c.duration
    tot = sum(c.duration for _, c in chosen)
    print(f"{len(chosen)} clips, {tot / 3600:.2f} h per voice ({2 * tot / 3600:.2f} h both), "
          + ", ".join(f"{k[0]}/{k[1]} {v / 3600:.2f} h" for k, v in sorted(by.items())))
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
