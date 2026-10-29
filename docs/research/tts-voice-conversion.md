# eSpeak + voice conversion for PIE speech

Viability test, 2026-10-29 (sources accessed the same day). Question: can we keep eSpeak's exact PIE segments and
pitch accent (`pie.speak` backend `espeak`, voice `pie/pie-tone`) and re-voice the audio in a natural Kokoro timbre
with an open voice-conversion (VC) model that changes timbre only? Companion to `docs/research/tts-options.md`
(engines) and `docs/research/tts-bakeoff.md` / `tts-bakeoff-objective.md` (Kokoro voices and respellings).

Everything is in `tts/vc/`: scripts and `manifest.json` are committed; venvs (`tts/vc/.venv-*`), cloned repos
(`tts/vc/src/`), weights (`tts/vc/cache/`) and audio (`tts/vc/audio/`, `tts/vc/listening/audio/`) are gitignored.
Listening page: `tts/vc/listening/index.html`.

<!-- VERDICT -->

## 1. Methods and licences

| Method | Version used | Licence (primary source) | Zero-shot? | How it works |
|---|---|---|---|---|
| **kNN-VC** | `bshall/knn-vc` @ `c616845` (2026-01-16); release v0.1 weights `WavLM-Large.pt`, `prematch_g_02500000.pt` | Code **MIT** (repo `LICENSE`, Stellenbosch MediaLab). WavLM-Large is Microsoft's (`microsoft/unilm`, **MIT**). The prematched HiFi-GAN is a release asset of the same MIT repo. | Yes, from reference audio | WavLM layer-6 features of the source; each frame is replaced by the mean of its k=4 nearest frames in the reference; HiFi-GAN vocoder. Output can only contain sounds present in the reference. |
| **OpenVoice V2** tone-colour converter | `myshell-ai/OpenVoice` @ `74a1d14` (2025-04-19); `myshell-ai/OpenVoiceV2` @ `f36e7ed`, `converter/checkpoint.pth` | **MIT**, code and V2 weights (repo `LICENSE`; README: "Starting from April 2024, both V2 and V1 are released under MIT License. Free for commercial use."; model card `license: mit`) | Yes | VITS-style posterior encoder → flow with the speaker embedding swapped (source embedding out, target in, `tau=0.3`) → decoder. |
| **Seed-VC** v1 | `Plachtaa/seed-vc` @ `51383ef` (2025-04-20); HF `Plachta/Seed-VC` @ `257283f` | **GPL-3.0**, code (repo) **and weights** (model card `license: gpl-3.0`). Not non-commercial, but copyleft: shipping it in a demo build means GPL obligations for that component. Its parts: whisper-small / whisper-base (Apache-2.0), BigVGAN v2 (MIT), CAM++ `funasr/campplus` (Apache-2.0), RMVPE `lj1995/VoiceConversionWebUI` (MIT). | Yes | Whisper encoder features of the source + reference mel prompt → diffusion transformer (30 steps) → BigVGAN. Two modes were run: **speech** (default whisper-small model, 22.05 kHz, no F0 input) and **F0** (`--f0-condition True --auto-f0-adjust False`, whisper-base model conditioned on the source's RMVPE F0, 44.1 kHz). |

Not run:
- **RVC** (`RVC-Project/Retrieval-based-Voice-Conversion-WebUI`, MIT) needs a trained per-target model. Training
  on CPU/MPS takes well over 20 minutes, and its installer is a Windows/CUDA bundle; skipped as the brief allows.
- **FreeVC** (`OlaWod/FreeVC`, MIT) is older (2022, WavLM + VITS) and close to OpenVoice in design; three systems
  were enough to answer the question.

No method is non-commercial. Seed-VC is the only copyleft one.

## 2. Setup (reproducible)

Each method has its own uv venv under `tts/vc/` (Python 3.11), never the main env or `.venv-kokoro`:

| venv | pins |
|---|---|
| `.venv-knnvc` | torch 2.5.1, torchaudio 2.5.1, numpy 1.26.4, soundfile 0.12.1 |
| `.venv-openvoice` | torch 2.5.1, numpy 1.26.4, librosa 0.10.2, soundfile 0.12.1, plus the pure-Python imports of `openvoice.text` (eng_to_ipa 0.0.2, inflect 7.0.0, unidecode 1.3.7, pypinyin 0.50.0, cn2an 0.5.22, jieba 0.42.1). The package itself is not installed: no faster-whisper, whisper-timestamped or wavmark. |
| `.venv-seedvc` | torch 2.5.1, torchaudio 2.5.1 (the repo pins 2.4.0, which has no MPS autocast), numpy 1.26.4, scipy 1.13.1, librosa 0.10.2, huggingface-hub 0.26.2, transformers 4.46.3, munch 4.0.0, einops 0.8.0, soundfile 0.12.1, pyyaml 6.0.2, descript-audio-codec 1.0.0 |
| `.venv-eval` | torch 2.5.1, transformers 4.46.3, librosa 0.10.2, praat-parselmouth 0.4.5, soundfile 0.12.1 |

Weights, sha256 (checked at load time by the scripts where the file is fetched outside HF):

| file | sha256 | note |
|---|---|---|
| knn-vc `WavLM-Large.pt` | `6fb4b3c3e6aa567f0a997b30855859cb81528ee8078802af439f7b2da0bf100f` | GitHub release asset; upstream publishes no hash (trust on first use) |
| knn-vc `prematch_g_02500000.pt` | `f924c7632c6eaf99004386d62293e124419e33582573552a6ae976eb88ed2dd5` | same |
| OpenVoiceV2 `converter/checkpoint.pth` | `9652c27e92b6b2a91632590ac9962ef7ae2b712e5c5b7f4c34ec55ee2b37ab9e` | equals the HF LFS oid |
| OpenVoiceV2 `converter/config.json` | `9dfff60350b8c63f2c664efd92a61b2516efb22671466960f0e5dfebd881fa47` | |
| Seed-VC `DiT_seed_v2_uvit_whisper_small_wavenet_bigvgan_pruned.pth` | `8ec8841b20bb46df9f7e8e570a6946a4b87b940133c7f0e778487ff33841f720` | speech mode |
| whisper-small `model.safetensors` @ `973afd2` | `1d7734884874f1a1513ed9aa760a4f8e97aaa02fd6d93a3a85d27b2ae9ca596b` | |
| BigVGAN v2 22 kHz `bigvgan_generator.pt` @ `633ff70` | `e95ba25972d3de0628d99cd156e9315a9c018899bf739988959ebe3544080ced` | |
| CAM++ `campplus_cn_common.bin` @ `e4b6ede` | `3388cf5fd3493c9ac9c69851d8e7a8badcfb4f3dc631020c4961371646d5ada8` | |
| wav2vec2-xlsr-53-espeak-cv-ft `pytorch_model.bin` @ `2c73378` | `04366b6c8d24099ef313cf02f0e58d26f5dddfda16edbfc8eb2c713d94a9f551` | recognizer |

<!-- F0WEIGHTS -->

Only documented entry points ran: kNN-VC through `torch.hub.load(<local clone>, "knn_vc", source="local")` with
the weights pre-placed in `$TORCH_HOME`; OpenVoice through `openvoice.api.ToneColorConverter`; Seed-VC through its
`inference.main` (the CLI), with `load_models` cached so the models load once per run. Workarounds, all in the
scripts: the pinned OpenVoice `api.py` forwards `enable_watermark` to a base `__init__` that rejects it, so the
converter is built the way its `__init__` does with the watermark off; Seed-VC fails on MPS inside BigVGAN's
resampler ("Output channels > 65536 not supported", not covered by `PYTORCH_ENABLE_MPS_FALLBACK`), so it runs on
CPU; `HF_HUB_ENABLE_HF_TRANSFER=0` because the shell sets it without the package.

Run order (from the repo root):

```
.venv/bin/python -I tts/vc/render_pie.py espeak            # eSpeak tone sources
.venv-kokoro/bin/python -I tts/vc/render_pie.py kokoro     # Kokoro + pitch patch, default spellings
.venv-kokoro/bin/python -I tts/vc/render_pie.py kokoro-prof   # top-3 voices with recommended profiles
.venv/bin/python -I tts/vc/render_pie.py espeak-p80        # control
.venv-kokoro/bin/python -I tts/vc/make_refs.py             # target references
TORCH_HOME=tts/vc/cache/torch tts/vc/.venv-knnvc/bin/python -I tts/vc/convert_knnvc.py
tts/vc/.venv-openvoice/bin/python -I tts/vc/convert_openvoice.py
cd tts/vc/src/seed-vc && ../../.venv-seedvc/bin/python ../../convert_seedvc.py speech   # and: f0
tts/vc/.venv-eval/bin/python -I tts/vc/evaluate.py         # -> tts/vc/results.json
tts/vc/.venv-eval/bin/python -I tts/vc/build_page.py       # -> listening/, manifest.json
```
`VC_VOICES=a,b,c VC_ITEMS=x,y` restrict a converter run (used for the top-3 round).

## 3. Material

- **Sources:** 15 hard words from the brief plus `ǵʰimḗ` [ɟʱi.méː] (the F0-peak check word of tts-options.md
  §2.3) and two sentences of `t3-t026-00015` ("Dawn, Daughter of Sky", `corpus/tier3/t026.jsonl`):
  *h₂éwsos léwka déywi diwés dʰúgh₂ter.* and *n̥sméy léwks sḱih₃wós-kʷe twéd bʰéwgt.* All rendered with
  `pie.speak(..., backend="espeak", tone=True)`, round trip strict. Word ids are the bake-off's.
- **Targets:** 20–28 s Kokoro references of plain speech, through the pinned model and voices in `pie.speak`,
  G2P `misaki.espeak.EspeakG2P`. hm_omega reads English; ef_dora and em_alex read Spanish. The texts are packed
  for a kNN-VC frame pool: Spanish jota [x], English aspirated p t k, labialised qu-/tw-, ʃ θ ɾ ŋ, many vowels.
  The top-3 round adds bf_isabella (en-gb, 25 s), af_nicole (en-us, 38 s, a slow speaker; Seed-VC uses only the
  first 25 s) and em_santa (Spanish, 22 s).
- **Kokoro comparison rows:** `pie.speak(..., backend="kokoro", pitch=True)` (pitch-patched, speed 0.9). The
  first round uses the converter default spellings ([χ], palatal [ɟ c]). The top-3 round uses each voice's
  recommended profile from tts-bakeoff-objective.md: bf_isabella and af_nicole `h2-velar` + dorsals=fronted,
  em_santa `h2-voiced-uvular` + dorsals=plain.

## 4. Objective checks

`tts/vc/evaluate.py`; full per-clip numbers in `tts/vc/results.json` and `tts/vc/manifest.json`.

- **Phone preservation.** `facebook/wav2vec2-xlsr-53-espeak-cv-ft`, greedy CTC, on the source and on each clip.
  *PER vs source* = edit distance between the two phone strings / source length. *Logit DTW* = mean cosine
  distance between the frame-level CTC logits along the DTW path (continuous, steadier on 1 s words). *PER vs
  IPA* = base-character distance to the converter IPA. As tts-options.md found, the recognizer never outputs χ, ʔ
  or murmured stops, so these numbers measure whether the heard phone string stays stable, not whether PIE
  sounds are right.
- **Controls** (no phonetic change at all): the source after AAC 48 kb/s (what the page plays), the same eSpeak
  codes rendered at eSpeak pitch 80, and the source pitch-shifted +3 st by a phase vocoder. They are the noise
  floor; on single words it is high.
- **χ check.** Length of voiceless noise before voicing starts, clip / source, on the χ-initial items (h₂éwsos,
  h₂ówis, h₂éǵeti, hymn line 1). 1 = the χ survives at full length; near 0 = it was dropped or voiced.
- **Pitch.** Praat autocorrelation F0 (10 ms, 50–600 Hz, octave jumps folded), speech span normalised to 0–1,
  200-point grid. *F0 r* = Pearson r in semitones over frames voiced in both. *Accent contrast kept* = (mean
  semitones on the source's high-tone frames − rest) in the clip / the same in the source; eSpeak's high tone is
  the accented syllable, about 3 st above the low tone. *Peak on accent* = F0 maximum within 0.12 of the
  source's (noisy: eSpeak's high tone is a plateau).
- **Duration.** Speech span (35 dB trim) and whole file, clip / source.

<!-- RESULTS -->
