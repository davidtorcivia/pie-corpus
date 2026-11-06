# Voice fix v2 (2026-11-06): the scripts as run

They were run on tr-desktop (WSL, paths under `/mnt/c/Users/David/Downloads/PIE/tts-corpus-v1` and `~/kokoro-ft`).

| script | what it did |
|---|---|
| `st_scan.py` | Ran the phone recognizer over every s+t in the renders and conversions (CUDA). Found 331 male and 52 female clips heard with a velar. |
| `run_v2b.py` | Ran repair v2 over the whole corpus into `work/repaired_v2` and `work/final_v2`, taking the re-converted s+t clips where they pass the gate. |
| `reg288.py` | Compared old and new on the swapped s+t clips: every t before a vowel, h before e/i, and phrase-final r. |
| `trill_scan.py`, `rsame.py` | Counted trill contacts per r (render, v10, v2) and checked that every r is untouched inside the r. |
| `kv2.sh` | The resumable Kokoro v2 retrain (kikiri recipe; batch 4 and 3 under the whole-card VRAM cap) and the epoch selection. |
| `kokoro_eval.py`, `hphys.py`, `eval_lines.json`, `mk_labels.py` | Compared the old and new Kokoro voices on h before e/i, phrase-final r, s+t (whole word) and trill contacts. |

Results: `docs/research/` is not updated. See the commit messages and `tts/vtl/reconv_st_2026-11-06.json`.
