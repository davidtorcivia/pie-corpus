# Kokoro v2 training (corpus v2, tr-desktop)

StyleTTS2 / kikiri-tts fine-tune of Kokoro on corpus v2: four voices, 6,267 train / 224 val clips, 15.5 h.
The voices are Zazy, Valeria, Antonio and W02, made from Chimera renders converted speech-to-speech and then
restored (restoration v2). The export is `chimera-vocal-synth/pie/export_kokoro.py`, which runs after
`pie/gate_v2.py`.

Where things live on tr-desktop:
- `Q:\AI\PIE\train\kokoro`: code, configs and the integer-speaker lists (`training/v2_*_list.txt`).
- `Q:\AI\PIE\data\tts-corpus-v2`: the audio, mirrored into WSL ext4 at `/root/kokoro-ft/data-v2/wavs` at each launch.
- `Q:\AI\PIE\runs\kokoro-v2\<stage>`: run outputs.

## Running

The run goes through WSL (Ubuntu-26.04), launched as a Windows scheduled task so it survives ssh and logoff.

- **Start or resume:** `powershell -File Q:\AI\PIE\train\kokoro\wsl\launch.ps1 -Task PIE-kokoro-v2 -Cmd run_all.sh`
  - A finished stage is skipped.
  - An unfinished stage resumes from its `last.pth` at the exact next batch of the same epoch.
- **Stop:** `powershell -File Q:\AI\PIE\train\kokoro\wsl\stop_stage.ps1 -Name stage1` (or `stage2`).
  - It writes a STOP file; the trainer saves `last.pth` at its next step and exits 0.
  - `-Kill` is the hard stop, losing the steps since the last save.
- **Saving:** `last.pth` is written every 20 min (`PIE_SAVE_MIN`) and at each epoch end. Each write goes to
  `last.pth.tmp` and is then renamed; the previous save is kept as `prev.pth`. A full save is 1.7 GB and takes
  about 12 s over `/mnt/q`.
- **Dashboard:** `http://127.0.0.1:8790/kokoro` on tr-desktop (`training/dashboard.py`, `training/kokoro.html`).

Logs in each run directory:

| File | Contents |
|---|---|
| `metrics.jsonl` | One JSON event per line: start/resume; train every 10 steps (every loss, lr, s/step, peak GiB); val per epoch; checkpoint; stopped; done |
| `manifest.json` | Config, torch/CUDA/Triton versions, GPU, every `PIE_*` switch, dataset counts; earlier launches kept under `history` |
| `gpu.csv` | nvidia-smi every 30 s |
| `console.log` | The trainer's console output |
| `tensorboard/` | As before |

## Speed work (2026-11-08)

All numbers are fp32 with TF32 matmuls, on an RTX 5090 that also drives the display. The VRAM cap is
`PIE_GPU_MEM_FRAC=0.80` (25.6 GiB). Speed is the median s/step after warm-up, over 30–80 steps on the real train
list.

### Native Windows vs WSL

Stage 1, batch 4, eager:

| Platform | s/step |
|---|---|
| WSL | 1.06 |
| Native Windows | 1.20 |

- Both are launch-bound, and native Windows is slower.
- Inductor on Windows also needs MSVC, which isn't installed.
- Decision: WSL.
- The native-Windows pieces stay in `win/` and `windows-native/` (a numba port of `monotonic_align`, bit-exact
  against the Cython one).

### Where the time went

**Stage 1** (torch.profiler over 6 steps at batch 4):
- The CPU spent 7.5 s and the GPU 2.4 s, so the GPU is idle about two-thirds of each step.
- That's about 42k kernel launches per step at about 12 µs each through the WSL GPU driver.

By module (forward, labelled with `record_function`):

| Module | Share of step |
|---|---|
| Text aligner's attention decoder (a Python loop over tokens) | about half, forward plus backward |
| Multi-scale / multi-period discriminators | about 30 % |

**Stage 2:** 31 s/step at batch 3 under torch 2.11.
- py-spy showed 66 % of the time in `torch.fx.traceback.format_stack` and `linecache.checkcache`.
- The cause was `torch.autograd.set_detect_anomaly(True)` at the top of the fork's `train_second.py`. It captures a
  Python stack for every autograd node, and each capture stats source files over `/mnt/q`.
- Turning it off gave 1.59 s/step. The old v1 run, which had it on with the code on ext4, ran at 3.7 s/step.
- `PIE_ANOMALY=1` turns it back on. The trainer has its own NaN checks.

### Memory

Memory left allocated by each module's forward per step (Stage 1, batch 4): msd 6.4 GiB, decoder 5.4, mpd 3.1,
everything else under 1.5. These three set the batch-size ceiling. Step time barely grows with batch size (1.06 s at
batch 4, 1.10 at batch 8), so a bigger batch is almost free throughput.

### What was tried

**Stage 1:**

| Variant | s/step | ms/clip | Peak GiB | Notes |
|---|---|---|---|---|
| b4 eager (v1 setup) | 1.06 | 264 | 15.7 | |
| b4 compile decoder, text_encoder, style_encoder (dynamic=True) | 1.0–9.3 | — | 12.0 | Recompiles until the limit, about 3 % gain between them |
| b4 compile decoder, mpd, msd (automatic dynamic) | 1.09 | 272 | 10.3 | No speed gain, a third less memory |
| b6 eager (expandable segments) | 1.19 | 198 | 21.9 | |
| b8 compile decoder, mpd, msd | 1.34 | 167 | 17.9 | |
| b8 checkpoint decoder, mpd, msd | 1.58 | 198 | 14.9 | |
| **b12 checkpoint decoder, mpd, msd** | 1.83 | **153** | 21.1 | **Chosen: 1.73×** |
| b12 compile | — | — | — | Out of memory |
| b16 checkpoint | — | — | — | Out of memory |
| b8 bf16 autocast | 1.10 | 138 | 22.4 | Loss NaN from step 1: rejected |
| Aligner token step compiled (`PIE_ASR_COMPILE`) | — | — | — | Exact (attention within 4e-7), 0.286 → 0.270 s: left off |

**Stage 2** (joint / SLM-adversarial training on, as in epochs 4–10):

| Variant | s/step | ms/clip | Peak GiB |
|---|---|---|---|
| b3 (v1 run, anomaly mode on) | 3.7 | 1233 | 19 |
| b3, anomaly off | 1.59 | 529 | 18.9 |
| b6 checkpoint | 2.32 | 387 | 15.9 |
| **b8 checkpoint (chosen: 3.85×)** | 2.56 | **320** | 20.0 |
| b12 / b16 checkpoint | — | — | Out of memory |

### Correctness fixes along the way

- **Data workers.** `meldataset.py` seeds numpy at import (`np.random.seed(1)`), so every data worker drew the same
  random crops, style references and OOD texts. The v1 run had this. Each worker is now seeded from torch's
  per-worker seed.
- **Checkpointing.** The decoder draws its F0/N smoothing width with Python's `random`, so a plain checkpoint
  recomputes a different branch in backward.
  - Stage 1 shapes happened to match, so the gradients would have been silently wrong.
  - Stage 2's didn't, and raised a CheckpointError.
  - `pie_run.checkpoint_modules` now replays Python's and numpy's RNG in the recompute. Outputs and gradients are
    identical to no checkpointing (difference 0.0), and the RNG stream continues unchanged.
- **Gradient norm.** Stage 2's gradient-norm loop did a `.item()` sync per parameter. It's now one reduction per
  module, which computes the same value.
- **Stage 1 resume.** Stage 1 resumed one epoch early, re-running the epoch it had just saved. The new `last.pth`
  stores the epoch, the step within it and the absolute epoch bounds.

## The run (2026-11-08 18:10 → 2026-11-09 05:00)

Kokoro base, Stage 1 10 epochs (2.75 h, batch 12), Stage 2 15 epochs (7.9 h, batch 8), 10.7 h in all.

| Validation | Previous run (Nov 6), final | This run |
|---|---|---|
| Stage 1 mel | 0.211 (best) | 0.197 (epoch 9) |
| Stage 2 mel | 0.235 | 0.223 (epoch 15) |
| Duration | 0.528 | 0.437 (epoch 15) |
| F0 | 1.333 | 1.236 (epoch 15) |

The validation sets differ, so compare these loosely.

**Synthesis from text** (`kokoro_select_v3.py`, all 224 val clips against their recordings):

| Epoch | MCD | F0 RMSE (cents) | Clipped clips |
|---|---|---|---|
| 12 | 22.15 | 353 | 1 |
| 13 | 22.63 | 356 | 1 |
| 14 | 21.74 | 347 | 0 |
| 15 | 22.42 | 352 | 2 |

**Recognizer error, word by word** (`synth_eval.py` here, `chimera-vocal-synth/pie/kokoro_score.py`). PhoneticXeus
transcribes each word inside the span Kokoro's own durations give it, and the transcription is compared with the
corpus target phones by edit distance. The scorer uses pie/wordscore.py's broad equivalences. Same 224 val clips;
the old model's two voices stand in for the four.

| Model | Zazy | Antonio | Valeria | W02 | Male | Female | All |
|---|---|---|---|---|---|---|---|
| The site's model until now (Nov 6 run, Stage 2 e00005, `kokoro-final-v2`) | 70.0 | 70.7 | 76.6 | 76.1 | 70.3 | 76.4 | 73.4 |
| The Nov 3 model (`final/kokoro_pie_stage2_e10.pth`) | 70.9 | 71.6 | 74.9 | 74.3 | 71.1 | 74.7 | 73.0 |
| Epoch 14 | 55.7 | 55.8 | 58.2 | 60.5 | 55.7 | 59.0 | 57.4 |
| Epoch 15 | 55.0 | 55.5 | 57.2 | 60.2 | 55.2 | 58.3 | 56.8 |
| The val recordings, on their corpus timing | 65.0 | 65.9 | 68.4 | 70.0 | 65.3 | 69.0 | 67.2 |

- The recordings are scored on source timings, which can drift from the converted audio; Kokoro's spans are exact by
  construction. That row is a rough reference, not a ceiling.
- On a whole-word measure like this, PhoneticXeus misses about 45 % of the sounds of real recorded speech (the human
  floor), so absolute numbers run high.
- The drop from the site's model to epoch 15, 16.6 points (23 % relative), is the finding.

Listening page: https://claude.ai/artifact/Cs3QeRwqeZjdR14Cbd98XZ
