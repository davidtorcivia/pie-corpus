# eSpeak + voice conversion for PIE speech

Viability test, 2026-10-29 (sources accessed the same day). Question: can we keep eSpeak's exact PIE segments and
pitch accent (`pie.speak` backend `espeak`, voice `pie/pie-tone`) and re-voice the audio in a natural Kokoro timbre
with an open voice-conversion (VC) model that changes timbre only? Companion to `docs/research/tts-options.md`
(engines) and `docs/research/tts-bakeoff.md` / `tts-bakeoff-objective.md` (Kokoro voices and respellings).

Everything is in `tts/vc/`: scripts and `manifest.json` are committed; venvs (`tts/vc/.venv-*`), cloned repos
(`tts/vc/src/`), weights (`tts/vc/cache/`) and audio (`tts/vc/audio/`, `tts/vc/listening/audio/`) are gitignored.
Listening page: `tts/vc/listening/index.html`.

## Verdict

| Method | Verdict | Why |
|---|---|---|
| **Seed-VC, F0 mode** (eSpeak → Seed-VC with source F0) | **Viable**, the pick | The only converter that keeps the pitch accent: F0 r median 0.95 against the source (0.50–0.60 for the others, 0.53 for Kokoro alone), 71 % of the accent contrast (80 % on the lines), duration 1.00. Phone stability is at the recognizer's noise floor (PER 0.69 vs 0.70 for the pitch-shift control). The owner heard Seed-VC as solid on phrases and better than paired Kokoro. Costs: GPL-3.0 (code and weights), CPU only on this Mac at ~35 s per clip, and χ is weakened (68 % of its voiceless noise kept; Kokoro's default [χ] keeps 15 %). |
| Seed-VC, speech mode | Marginal | Same segments and duration as F0 mode, but it regenerates the pitch: F0 r median 0.50, accent contrast 0.46. Use F0 mode instead. |
| kNN-VC | Marginal | Best at keeping χ among converters (0.88) and duration (0.97), PER 0.68. But it rebuilds every frame from the reference, so pitch comes from the reference too: accent contrast 0.35, peak on the accent in 32 % of items, 0 % on the lines. With a 20–40 s reference its frame pool is thin (the paper saturates around 5 min). |
| OpenVoice V2 | Marginal, **single words only** | Keeps χ (0.96) and duration (1.01), and the owner heard em_alex as excellent on single words. On phrases it is, by ear, a disaster; the numbers agree on pitch (lines F0 r median 0.34, contrast 0.41) though not on phone stability (lines PER 0.47). Not for the hymn demo. |
| (Kokoro alone, for comparison) | — | Natural, but it is a different rendering: 28 % longer than eSpeak on words, χ nearly gone with the default spelling (0.15), F0 r 0.53. With each voice's recommended profile (top-3 round) its [x]/[ʁ] fares better, but on the lines it stays further from eSpeak than Seed-VC F0 on phones (PER 0.58–0.66 vs 0.40–0.42) and pitch (F0 r 0.26–0.66 vs 0.84–0.96). |

Recommendation for the demo: render with eSpeak (`pie/pie-tone`) and re-voice offline with Seed-VC F0 mode,
target timbre em_alex or em_santa (male voices: F0 mode keeps eSpeak's low male contour as is, so a female
target such as bf_isabella speaks at male pitch unless `--semi-tone-shift` is used, which was not tested; pick by
ear on the listening page).
Keep Seed-VC as a separately licensed GPL component, or pre-render the demo audio so only the audio ships.
The recognizer is too blunt to certify the hard segments (it never hears χ, ʔ or murmur), so the final call on
χ, ǵ/ḱ and bʰ must be by ear; the χ-noise check says Seed-VC thins χ by about a third.


## 1. Methods and licences

| Method | Version used | Licence (primary source) | Zero-shot? | How it works |
|---|---|---|---|---|
| **kNN-VC** | `bshall/knn-vc` @ `c616845` (2026-01-16); release v0.1 weights `WavLM-Large.pt`, `prematch_g_02500000.pt` | Code **MIT** (repo `LICENSE`, Stellenbosch MediaLab). WavLM-Large is Microsoft's (`microsoft/unilm`, **MIT**). The prematched HiFi-GAN is a release asset of the same MIT repo. | Yes, from reference audio | WavLM layer-6 features of the source; each frame is replaced by the mean of its k=4 nearest frames in the reference; HiFi-GAN vocoder. Output can only contain sounds present in the reference. |
| **OpenVoice V2** tone-colour converter | `myshell-ai/OpenVoice` @ `74a1d14` (2025-04-19); `myshell-ai/OpenVoiceV2` @ `f36e7ed`, `converter/checkpoint.pth` | **MIT**, code and V2 weights (repo `LICENSE`; README: "Starting from April 2024, both V2 and V1 are released under MIT License. Free for commercial use."; model card `license: mit`) | Yes | VITS-style posterior encoder → flow with the speaker embedding swapped (source embedding out, target in, `tau=0.3`) → decoder. |
| **Seed-VC** v1 | `Plachtaa/seed-vc` @ `51383ef` (2025-04-20); HF `Plachta/Seed-VC` @ `257283f` | **GPL-3.0**, code (repo) **and weights** (model card `license: gpl-3.0`). Not non-commercial, but copyleft: shipping it in a demo build means GPL obligations for that component. Its parts: whisper-small (Apache-2.0), BigVGAN v2 (MIT), CAM++ `funasr/campplus` (Apache-2.0), RMVPE `lj1995/VoiceConversionWebUI` (MIT). | Yes | Whisper encoder features of the source + reference mel prompt → diffusion transformer (30 steps) → BigVGAN. Two modes were run: **speech** (default whisper-small model, 22.05 kHz, no F0 input) and **F0** (`--f0-condition True --auto-f0-adjust False`: the `..._whisper_base_f0_44k` DiT, whose config in fact loads whisper-small, conditioned on the source's RMVPE F0, BigVGAN 44.1 kHz). With auto-adjust off the source contour is used as is, so the voice keeps eSpeak's pitch level (a low male voice). |

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

Seed-VC F0 mode adds:

| file | sha256 |
|---|---|
| `DiT_seed_v2_uvit_whisper_base_f0_44k_bigvgan_pruned_ft_ema_v2.pth` (Plachta/Seed-VC @ `257283f`) | `42aef93ffe65857c840d270252fa040f7ba04514945ec460f3ac1ac2a96de684` |
| BigVGAN v2 44 kHz `bigvgan_generator.pt` (nvidia/bigvgan_v2_44khz_128band_512x @ `95a9d1d`) | `d9fe7ec6bd0b44ed9d66973d5012d8181c1570b01e5c72df51973e241dccd357` |
| `rmvpe.pt` (lj1995/VoiceConversionWebUI @ `e6d0c1a`, MIT) | `6d62215f4306e3ca278246188607209f09af3dc77ed4232efdd069798c4ec193` |

The Seed-VC HF downloads are not revision-pinned by its code; the resolved snapshot commits are the ones listed,
and `convert_seedvc.py` records the sha256 of every weight file it found in its `log*.json`.

Speed on this Mac (CPU): kNN-VC 0.07 s per word, OpenVoice 0.2 s, Seed-VC 20–24 s (speech) and 34–36 s (F0) per
clip, almost all of it spent on the 25 s reference prompt. Seed-VC is a pre-render tool here, not live.

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

## 5. Results

### 5.1 Main round: 18 items × 3 timbres (hm_omega, ef_dora, em_alex)

Means over all 54 clips per system (lines = the two hymn lines, 6 clips). Kokoro alone is the pitch-patched
Kokoro rendering with the converter default spellings, compared with the same eSpeak source.

| System | PER vs source | PER, lines | Logit DTW ×1000 | PER vs IPA | χ noise kept | F0 r (median) | Accent contrast kept | Peak on accent | Duration ratio |
|---|---|---|---|---|---|---|---|---|---|
| kNN-VC | 0.68 | 0.51 | 8 | 0.62 | 0.88 | 0.60 | 0.35 | 32 % | 0.97 |
| OpenVoice V2 (words only) | 0.84 | 0.47 | 9 | 0.74 | 0.96 | 0.58 | 0.54 | 35 % | 1.01 |
| Seed-VC speech | 0.72 | 0.46 | 9 | 0.63 | 0.74 | 0.50 | 0.46 | 33 % | 0.98 |
| **Seed-VC F0** | **0.69** | 0.49 | 8 | 0.61 | 0.68 | **0.95** | **0.71** | **74 %** | **1.00** |
| Kokoro alone (default spellings) | 0.87 | 0.63 | 12 | 0.57 | 0.15 | 0.53 | 0.43 | 67 % | 1.28 |
| *Control: source after AAC* | 0.26 | 0.22 | 2 | 0.60 | 1.00 | 1.00 | 1.00 | 94 % | 1.00 |
| *Control: eSpeak at pitch 80* | 0.44 | 0.28 | 4 | 0.64 | 1.00 | 1.00 | 0.67 | 83 % | 1.00 |
| *Control: source +3 st (phase vocoder)* | 0.70 | 0.66 | 8 | 0.81 | 0.85 | 0.99 | 0.90 | 94 % | 1.04 |

Reading it:
- **Phones.** Even the AAC round trip moves the recognizer's string by 26 % on single words; a clean
  re-render at another pitch moves it 44 %; a phase-vocoder shift 70 %. Every converter sits between the second
  and third control, so the recognizer cannot separate them on words. On the lines (longer context) all
  converters are at 0.46–0.51, Kokoro at 0.63. The logit DTW distance gives the same order: converters 8–9,
  Kokoro 12, controls 2–8. Phone content survives conversion about as well as a pitch shift does; Kokoro's own
  rendering is further from eSpeak than any conversion. PER vs IPA is ~0.6 for the eSpeak source itself, which
  is the recognizer's ceiling on this material.
- **χ.** eSpeak's word-initial χ is 90–130 ms of voiceless noise. OpenVoice and kNN-VC keep almost all of it;
  Seed-VC keeps two thirds (it voices the onset in some timbres: ef_dora 0.42 in F0 mode). Kokoro's default
  [χ] is nearly silent (0.15), which matches the owner's ear.
- **Pitch.** Only Seed-VC F0 keeps the contour (median r 0.95 overall, 0.90–0.96 per timbre). The others
  regenerate pitch: median r 0.50–0.60, under half to a half of the accent contrast. For `ǵʰimḗ` [ɟʱi.méː] (source
  peak at 0.74 of the span, on méː) Seed-VC F0 (both modes, in fact) and Kokoro keep the peak on méː in all three timbres; kNN-VC in one of three, OpenVoice in two.
- **Duration.** All converters keep the source length (0.97–1.01); Kokoro is a separate rendering and runs
  28 % long on words.

Per timbre (all 18 items):

| Timbre | kNN-VC PER / F0 r med | OpenVoice PER / F0 r med | Seed-VC PER / F0 r med | Seed-VC F0 PER / F0 r med | Kokoro alone PER / F0 r med |
|---|---|---|---|---|---|
| hm_omega | 0.61 / 0.51 | 0.82 / 0.60 | 0.76 / 0.44 | 0.76 / 0.95 | 0.95 / 0.51 |
| ef_dora | 0.75 / 0.69 | 0.85 / 0.69 | 0.75 / 0.64 | 0.69 / 0.90 | 0.87 / 0.57 |
| em_alex | 0.69 / 0.60 | 0.86 / 0.55 | 0.66 / 0.39 | 0.62 / 0.96 | 0.79 / 0.53 |

### 5.2 Fair comparison: top-3 bake-off voices, Kokoro with recommended profiles

The owner's request: Kokoro+pitch in bf_isabella, af_nicole (`h2-velar` + dorsals=fronted) and em_santa
(`h2-voiced-uvular` + dorsals=plain), against Seed-VC from the same eSpeak sources into the same voices. Items:
h₂éwsos, h₂éǵeti, ḱléwos, bʰréh₂tēr (4 words) and the two hymn lines. Only 2 lines per voice, so the line
columns are indicative.

| Voice | System | PER, 4 words | PER, 2 lines | F0 r, words | F0 r, lines | Contrast kept, lines | χ noise kept | Duration, words | Duration, lines |
|---|---|---|---|---|---|---|---|---|---|
| bf_isabella | Seed-VC speech | 0.73 | 0.46 | 0.78 | 0.34 | 0.10 | 0.31 | 0.96 | 0.96 |
| | **Seed-VC F0** | 0.72 | **0.40** | 0.96 | **0.87** | **0.85** | 0.56 | 0.96 | 0.99 |
| | kNN-VC | 0.74 | 0.44 | 0.68 | 0.39 | 0.30 | 0.64 | 0.97 | 0.98 |
| | OpenVoice (words only) | 0.71 | 0.42 | 0.43 | 0.55 | 0.44 | 1.00 | 1.00 | 1.00 |
| | Kokoro + profile | 0.86 | 0.60 | 0.70 | 0.59 | 0.57 | 0.33 | 1.30 | 0.95 |
| af_nicole | Seed-VC speech | 0.83 | 0.50 | 0.34 | −0.15 | −0.12 | 0.69 | 0.95 | 0.96 |
| | **Seed-VC F0** | 0.62 | **0.40** | 0.91 | **0.84** | **0.80** | 0.74 | 0.98 | 0.97 |
| | kNN-VC | 0.70 | 0.54 | 0.46 | 0.06 | 0.07 | 1.18 | 0.99 | 0.99 |
| | OpenVoice (words only) | 0.74 | 0.42 | 0.56 | 0.40 | 0.50 | 0.82 | 1.00 | 1.01 |
| | Kokoro + profile | 0.72 | 0.58 | 0.84 | 0.26 | −0.02 | 0.90 | 1.37 | 1.24 |
| em_santa | Seed-VC speech | 0.79 | 0.46 | −0.31 | 0.29 | 0.51 | 1.08 | 0.94 | 0.99 |
| | **Seed-VC F0** | 0.59 | **0.42** | 0.96 | **0.96** | **0.91** | 0.74 | 0.99 | 0.99 |
| | kNN-VC | 0.64 | 0.66 | 0.33 | 0.21 | 0.24 | 0.97 | 1.00 | 0.99 |
| | OpenVoice (words only) | 0.73 | 0.48 | 0.06 | 0.39 | 0.65 | 1.03 | 1.01 | 1.01 |
| | Kokoro + profile | 0.67 | 0.66 | 0.47 | 0.66 | 0.74 | 0.92 | 1.09 | 0.90 |

(F0 r here is the mean, not the median; χ noise kept is over h₂éwsos, h₂éǵeti and line 1, words and line together.)

On the lines, the owner's focus, Seed-VC F0 is ahead of profiled Kokoro in every voice: phone distance to the
eSpeak rendering 0.40–0.42 vs 0.58–0.66, F0 r 0.84–0.96 vs 0.26–0.66, and it keeps the length, where Kokoro
runs 10 % short to 24 % long. The profiles do fix Kokoro's h₂ in af_nicole and em_santa (voiceless or [ʁ] noise
at 0.9 of eSpeak's χ length; for em_santa's voiced [ʁ] the "voiceless noise" check counts only its devoiced
part), but not in bf_isabella (0.33). Seed-VC F0 keeps 0.56–0.74 of χ in these voices. On single words the picture is mixed: profiled Kokoro af_nicole keeps the
pitch well (0.84), and Seed-VC F0 keeps it everywhere (0.91–0.96).

### 5.3 Limits of this test

- The phone recognizer is the weak instrument: it does not output χ, ʔ or murmured stops and is unstable on
  1-second clips (26 % change from AAC alone). Treat phone numbers as "nothing broke worse than a pitch shift",
  not as a segment-accuracy score. The χ-noise check is the one targeted segment test; murmur, palatals and
  labiovelars are judged by ear only.
- References are 20–40 s of Kokoro speech. kNN-VC in particular would improve with minutes of reference.
- Seed-VC F0 mode keeps eSpeak's absolute pitch (auto-f0-adjust off, so the accent is untouched); a female
  target then speaks at male pitch. `--semi-tone-shift` would move the whole contour without changing its shape;
  not tested.
- One run per clip; Seed-VC is a diffusion model and varies between runs.

## 6. Files

- Listening page: `tts/vc/listening/index.html`, audio under `tts/vc/listening/audio/` (list in
  `tts/vc/listening/files.txt`). Per word: eSpeak source, a method × timbre grid with Kokoro alone, and for the
  6 subset items a second grid for the top-3 voices with profiled Kokoro. OpenVoice rows are flagged "words
  only".
- Manifest for the merged rating page: `tts/vc/manifest.json` (schema `pie-tts-bakeoff/1`, `source: "vc"`; clip
  fields as in `tts/bakeoff/manifest.json` plus `pie`, `target`, `method`, `timbre`, absolute `wav`, `mp4`,
  `source_wav`, `metrics`). Every clip id starts `vc__` and every system id `vc-` (`vc-<method>-<voice>`,
  `vc-kokoro-default-<voice>`, `vc-kokoro-profiled-<voice>`, `vc-espeak-tone`), so nothing collides with the
  bake-off manifest. The 15 eSpeak source clips for shared words are the same render as the bake-off's
  `espeak-tone` clips; their `same_as` names the bake-off id. The Kokoro rows are not bake-off duplicates (the
  bake-off renders non-h₂ targets with base profile h2-velar; the first round here uses the plain default).
  `targets` is copied from the bake-off; the hymn lines use target `line` and ǵʰimḗ `accent`, which the bake-off
  list does not define.
- Per-clip numbers: `tts/vc/results.json`.


## 7. Finals set (2026-10-29)

The owner's finals: 8 systems on 28 items, 224 clips, for rating on `tts/finals/index.html` (manifest
`tts/finals/manifest.json`, schema `pie-tts-bakeoff/1`, `source: "finals"`; publish map `tts/finals/files.json`).
Pipeline `tts/finals/finals.py` (steps in its docstring); audio under `tts/finals/audio/` (gitignored).

- **Items:** the 10 corpus hymns of the Voice Lab, whole records read at HEAD 2284132 (13–32 s in eSpeak), then
  the 18 words and lines above.
- **Systems:** eSpeak tone; Kokoro + pitch patch with each voice's recommended profile (as §5.2); eSpeak →
  Seed-VC F0 into em_santa, em_alex, bf_isabella, af_nicole (references as before).
- **Long sources.** With a 25 s reference prompt Seed-VC's window holds only ~5 s of source, and it would cut
  the hymns there. Instead each source is cut at the longest quiet run (a pause or stop closure, ≥ 30 ms at
  −40 dB) in the second half of each 4.6 s window, the pieces are converted separately and joined; every seam
  is in silence. (eSpeak pie-tone's sentence pause is only 30–60 ms, no longer than a closure.)
- **Semitone shift for the female targets** (`tts/finals/shift_trials.json`). eSpeak's tone voice sits at
  ~94 Hz, so +5 to +7 st leaves both voices well under their own range. Trials at 0, +5, +7, +9, +11, +13 st on
  ḱléwos and hymn-1; the pick is the shift whose converted median F0 is nearest the voice's reference median
  (first 25 s, Praat AC) among those inside its interquartile range:

  | voice | reference median (IQR), Hz | +7 st | +9 st | +11 st | +13 st | chosen |
  |---|---|---|---|---|---|---|
  | bf_isabella | 201 (183–225) | 137 | 157 | 177 | **196** | **+13** |
  | af_nicole | 159 (144–181) | 141 | **153** | 175 | 195 | **+9** |

  F0 r and accent contrast stay at the unshifted level (0.86–0.98, 0.66–1.0). The shift does not affect χ:
  its onset noise varies run to run (af_nicole hymn-1: 10–100 ms across the six trials).
- **QC.** No clip is clipped, silent or truncated (Seed-VC file length 0.99–1.00× the source in every clip).
  Eleven clips whose first segment kept less than half of eSpeak's word-initial noise got a second render of
  that segment, keeping the one with more noise (`tts/finals/rerenders.json`, 7 of 11 improved). Five remain
  under half (bf_isabella h₂éwsos, h₂ówis, hymn-1, t3-t026-00015; af_nicole h₂éwsos), noted on the page.

Objective checks (`tts/vc/evaluate.py`, against the eSpeak source; `tts/finals/results.json`):

| system | PER, hymns | PER, words | F0 r median, hymns | F0 r median, words | accent kept, hymns | χ noise kept | duration, hymns | duration, words |
|---|---|---|---|---|---|---|---|---|
| Kokoro bf_isabella | 0.62 | 0.91 | 0.14 | 0.69 | 0.12 | 0.54 | 1.39 | 1.43 |
| Kokoro af_nicole | 0.62 | 0.80 | 0.05 | 0.79 | −0.04 | 0.79 | 1.66 | 1.46 |
| Kokoro em_santa | 0.69 | 0.93 | 0.18 | 0.55 | 0.15 | 0.80 | 1.11 | 1.23 |
| Seed-VC F0 em_santa | 0.54 | 0.76 | 0.94 | 0.95 | 0.90 | 0.85 | 1.00 | 1.00 |
| Seed-VC F0 em_alex | 0.52 | 0.75 | 0.86 | 0.95 | 0.81 | 0.74 | 1.00 | 0.99 |
| Seed-VC F0 bf_isabella (+13) | 0.51 | 0.68 | 0.96 | 0.98 | 0.87 | 0.35 | 1.00 | 0.96 |
| Seed-VC F0 af_nicole (+9) | 0.53 | 0.77 | 0.95 | 0.93 | 0.88 | 0.52 | 1.00 | 0.96 |

"Words" here are the 16 single words; the two lines are in `results.json`. χ noise kept is over the χ-initial
items (4 words and lines, and the hymns that open with h₂). On the hymns Kokoro's F0 r and accent numbers are
near zero partly by method: the F0 tracks are compared on normalised time, and over 15–30 s Kokoro's own
timing (1.1–1.7× eSpeak's length) puts its syllables elsewhere; read them as "not eSpeak's contour", not as
"no accent". Seed-VC F0 keeps the contour on the hymns as on the words. Its χ is weakest in the shifted female
voices, bf_isabella above all, which matches §5.2 (0.56 there, unshifted).

## 2026-10-29: recitation cadence + ElevenLabs chain (Dawn hymn, t3-t026-00015)

Owner listening: Seed-VC sounds good but loses the laryngeals; OpenVoice keeps them. Best so far (owner's pick):
**eSpeak re-timed as verse (tts/cadence/cadence.py) → OpenVoice V2 em_alex → ElevenLabs speech-to-speech (owner, by
hand) → tts/cadence/transplant_f0.py with MICRO=1 F0_RANGE=1.6** (the slow melody from the eSpeak source,
widened 1.6×, ElevenLabs' own micro-variation kept).

Measurements (all on the 27.21 s cadence timeline, which ElevenLabs preserves to the millisecond):
- h₂ friction (2–8 kHz share, initial h₂ of h₂éwsos): eSpeak 0.38, OpenVoice 0.15, Seed-VC 0.05, ElevenLabs on
  OpenVoice 0.32. ElevenLabs restores what OpenVoice thinned.
- Melody: ElevenLabs re-invents it (window r 0.22 to the source; Seed-VC F0 mode keeps it, 0.86). A plain F0
  transplant gets r 0.99 but copies eSpeak's piecewise-flat contour (median 10 ms step 0.06 st vs ElevenLabs'
  0.22), heard as robotic; MICRO mode gives r 0.93 with step 0.15 st.
- A second ElevenLabs pass over the transplanted file again drops the melody (r 0.30); the transplant has to be last.

VocalTractLab render (built by another agent, 19.8 s), and ElevenLabs over it: cleanest voice (HNR 14.3 dB), pitch
steps 0.105 st, and ElevenLabs follows its melody (r 0.84). But there are no pauses between lines (longest
silence 0.21 s), and the h₂ windows (located by DTW from the cadence source, so approximate) show almost no
friction (0.02–0.05 against eSpeak's 0.36–0.41), although its [s] is strong. Its χ looks absent or very weak;
to be confirmed by ear.

Repitch round (owner listening, 2026-10-29): the plain transplant's pitch edit was audibly phasey/aliased (shifts
median 2.2 st, p90 5.5, jumps at voicing edges). tts/cadence/repitch.py (one smooth shift curve, filled across
voicing gaps, soft-limited to ±3.5 st, pitch floor 75 Hz): **A = PSOLA is the owner's pick**; B = WORLD vocoder
second; C = Seed-VC re-synthesis of A in the ElevenLabs voice "terrible" (also HNR 9.6 dB and weaker h₂/h₁).
Current best chain: cadence.py → OpenVoice em_alex → ElevenLabs STS (manual) → repitch.py psola (RANGE 1.6).
Next: VocalTractLab with the other agent's IPA compiler (check χ and line pauses).

### VTL v3: native prosody on the cadence timeline (2026-10-29)

The other agent's compiler (`pie_vtl.py --timeline`) now renders on the cadence timeline (27.21 s, 6 pauses) and writes
phone timings. Pitch comes from VTL's F0 tier: accent bumps (`--accent-range 4.6`, about 0.74× delivered),
declination 1.5 → −2.5 st, and a final fall. There is no post-correction. All measures below use the exact phone
intervals from `dawn-hymn-vtl.json`. Accent = mean nucleus F0, accented minus unaccented. Declination = slope fitted
on unaccented nuclei per line.

| file | F0 sd | step | HNR | r vs eSpeak | accent | decl/line | voiced nuclei |
|---|---|---|---|---|---|---|---|
| eSpeak cadence | 2.6 | 0.073 | 13.3 | 1.00 | +1.2 | +1.4 | 63/68 |
| A (OpenVoice→11L→repitch) | 2.6 | 0.192 | 12.3 | 0.80 | +2.4 | −0.9 | 66/68 |
| VTL v3 | 2.5 | 0.097 | 14.8 | 0.69 | +3.8 | −3.5 | 68/68 |
| VTL v3 → ElevenLabs | 3.1 | 0.225 | 14.5 | 0.47 | +3.2 | −0.5 | 68/68 |

χ through ElevenLabs now survives every time. Its 2–8 kHz share is 0.63–0.91, against 0.01–0.05 lost in v2.
Glottal h/H is the gap. VTL gives 0.00–0.03 at wiHrṓs, túH and the H of h₂yuHénih₂, where eSpeak gives 0.18–0.71.
Word-initial h₁ of h₁áydʰi alone survives (0.24).
