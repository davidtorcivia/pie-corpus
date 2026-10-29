# Text-to-speech options for the PIE demo

Survey and hands-on test, 2026-10-28 (all sources accessed 2026-10-28). The demo is around 2026-11-11.

The TTS receives only the IPA produced by `pie.ipa.to_ipa` (`docs/pronunciation.md`). It never sees PIE spelling. The symbols that matter are the ones the converter actually emits. Under the default convention, in corpus frequency order (pronunciation.md §10), these are: χ, kʷ, c, dʱ, ə, eː, bʱ, oː, ɡʷ, ɟ, ɣʷ, n̩, r̩, m̩, l̩, ɟʱ, ɡʱ and ɡʷʱ. The pitch accent is a combining acute (U+0301) on the nucleus, or ˈ with `tone="stress"`. The `pharyngeal` preset adds ʔ, ħ and ʕʷ.

## Verdict

| | Pick | Why | Status |
|---|---|---|---|
| **(a)** robotic but correct, 1-2 days | **eSpeak-NG 1.52.0 with a custom `pie` phoneme table** (Hindi base + Arabic ħ ʕ + level tones), fed `[[…]]` phoneme mnemonics | It has native χ ɣ ʔ ħ ʕ c ɟ, murmured bʱ dʱ ɡʱ ɟʱ, syllabic r̩ l̩ m̩ n̩ and long vowels. It also gives **real per-syllable pitch**: tone phonemes were tested and measured with Praat. | Built and working (below) |
| **(b)** most natural, no fine-tuning, by 11-11 | **Kokoro-82M v1.0 (Apache-2.0), Hindi voice `hf_alpha`/`hm_omega`**, raw IPA via `KModel.forward(phonemes, …)`, with **an imposed F0 accent** (a 30-line patch of the predicted F0) | It is the best-sounding open model that takes IPA directly. Its Hindi voices were trained on murmured stops. It has explicit F0, so the PIE high tone can be placed on the right syllable. | Rendered and pitch measured; still needs listening |
| **(c)** fine-tune on the owner's voice afterwards | **Kokoro-82M fine-tune with the `semidark/kikiri-tts` recipe** (patched StyleTTS2, Apache-2.0), labels = converter IPA with new tokens for ʱ ʷ ̩ ħ ʕ. **Fallback: Piper 1.8 (`piper1-gpl`) with `--data.phoneme_type text`** from a medium checkpoint | Kokoro keeps the Apache licence and explicit F0 (the pitch accent). Piper is the low-risk path: documented custom-phoneme training, ONNX inference on the Mac. | Recipe exists for German and Marathi; not tried here |

Backup for (b): Piper `hi_IN-rohan-medium` with raw `[[ … ]]` IPA. It is fast and correct-ish, but it has no pitch control and a lower ceiling than Kokoro. Commercial APIs (Azure, Google, Polly, ElevenLabs) are not viable. Each restricts IPA to the voice locale's phone set, and Azure rejects unknown phones with HTTP 400.

## 1. Comparison

"Phoneme in" means the engine accepts IPA or phoneme codes in place of text. "PIE inventory" lists what the engine's phoneme input can represent. A symbol can be in the vocabulary and still never have been trained on (see §3.3).

| System (version checked) | Phoneme in | PIE inventory | Pitch control | macOS local | Licence | Fine-tune from 1-5 h | Quality / maturity |
|---|---|---|---|---|---|---|---|
| **eSpeak-NG** 1.52.0 (Homebrew; last release 2024-12, repo active 2026-09) | Yes: `[[…]]` eSpeak mnemonics, per-voice phoneme tables | **All** when tables are combined: χ ɣ ʔ c ɟ (hi, hu, ar…), ħ ʕ (ar), bʱ dʱ ɡʱ ɟʱ (hi: `b# d# g# J#`), syllabic `r- l- m- n-`, length `:`. kʷ only as k+w | **Yes**: stress marks, SSML `<prosody pitch>`, and tone phonemes `Tone(…)` (tested) | Yes, `brew install espeak-ng` | GPL-3.0 (engine and data; audio output unaffected) | No (formant synthesis; hand-tune only) | Robotic; very mature |
| **Piper** 1.8.0 (`OHF-Voice/piper1-gpl`, 2026-09; `rhasspy/piper` archived) | Yes: `[[ IPA ]]` in text; training with raw IPA or ids | 157-symbol IPA map with χ ħ ʔ c ɟ ʰ ɣ ̩ ː. **No ʱ, no ʷ** (dropped with a warning) | Stress ˈ only (VITS, no F0 input) | Yes, pip; ONNX on CPU, real-time | Code GPL-3.0. Voice licences vary: hi_IN pratham/priyamvada data **CC-BY-NC-SA**; ljspeech public domain; hu/cs/fa CC0 | **Good**: documented, fine-tunes from a checkpoint, custom phoneme sets; CUDA advised | Decent, slightly buzzy; mature |
| **Kokoro-82M** v1.0 (`kokoro` 0.9.4, misaki 0.9.4) | Yes: `KModel.forward(phonemes: str, …)`, `KPipeline.generate_from_tokens`, ONNX `input_ids` | 113-symbol vocab with χ ʔ c ɟ ʰ ɣ ʁ ː ˈ. **No ʱ ʷ ̩ ħ ʕ**, no acute | Not exposed, but the decoder takes an explicit predicted **F0** that can be edited (done here) | Yes (CPU fine; ONNX or PyTorch) | **Apache-2.0** weights | Official: no. Community 2026 recipes (`semidark/kikiri-tts` German, `bol-tts-marathi`), CUDA | Very natural for 82M; widely used |
| **StyleTTS2** (`yl4579/StyleTTS2`, last push 2024-08) | Yes: IPA characters (phonemizer output) | 178 symbols incl. χ ħ ʔ ʕ ʡ c ɟ ʰ **ʱ ʷ ̩** ː ˈ, tone letters ↓↑→↗↘ | Explicit F0 predictor (editable as in Kokoro) | Inference on CPU or MPS; training CUDA | Code MIT. Pre-trained models carry a **"tell listeners it is synthetic"** condition | `train_finetune.py`: 1 h on LibriTTS checkpoint, ~4 h on 4×A100 | Human-level on LJSpeech; research code, stale |
| **Coqui XTTS-v2** (company closed early 2024; fork `idiap/coqui-ai-TTS` 0.28.0, 2026-10) | No (text, 17 languages) | n/a | No | Yes (slow) | Weights **CPML, non-commercial**. Fork code MPL-2.0 | XTTS fine-tune exists; the fork's VITS recipes accept espeak phonemes or custom characters | Good; project orphaned, fork maintained |
| **F5-TTS / E2** (`SWivid/F5-TTS` 1.1.22) | No (characters/pinyin; can be retrained on any token set) | n/a | No | Yes (MPS slow) | Code MIT, weights **CC-BY-NC-4.0** (Emilia data) | Fine-tune scripts; needs more data | Very natural zero-shot cloning |
| **Meta MMS-TTS** (`facebook/mms-tts-*`) | No: per-language character (uroman) VITS | Per-language letters only | No | Yes (transformers) | **CC-BY-NC-4.0** | Possible (VITS) but NC | Robotic-ish; 1,100+ languages |
| **Parler-TTS** (last push 2024-12) | No (text + style description) | n/a | Only via the description | Yes | Apache-2.0 | Training code exists; large data | Good English; stale |
| **Matcha-TTS** (MIT, active 2026-10) | Yes: same 178-symbol IPA set as StyleTTS2 | Same as StyleTTS2 (incl. ʱ ʷ ̩ ħ) | No explicit F0 | Yes | MIT. LJSpeech checkpoints are public domain data | **Easy**: fast flow-matching training from scratch or a checkpoint | Good; small |
| **OpenVoice** v2 (MIT, last push 2025-04) | No (MeloTTS text front end + tone colour converter) | n/a | No | Yes | MIT | Voice conversion only | Good; could re-voice eSpeak or Kokoro output |
| **Fish Speech / OpenAudio** (v3.0.0-beta, S2-Pro) | No (LLM over text) | n/a | No | Yes | **Fish Audio Community Licence**: non-commercial plus a revenue cap; hosted services need a separate licence; S2-Pro "Research License" | LoRA | Top-tier naturalness; licence unsuitable |
| **CosyVoice 3** (`Fun-CosyVoice3-0.5B-2512`, Apache-2.0) | Partial: "pronunciation inpainting" with **pinyin and English CMU phonemes only** | No IPA | Instruct-style only | CUDA-leaning | Apache-2.0 | SFT scripts | Very natural |
| **Qwen3-TTS** (2026-01), **VoxCPM2** (2026-04), **Chatterbox Multilingual V3**, **Kitten TTS 2**, **Zonos** v0.1 | No: text in (Zonos phonemizes with espeak internally; Kitten 0.8 ONNX is espeak-based English) | n/a | Description or emotion only | VoxCPM2 and Qwen3 want CUDA; Kitten runs on CPU | Apache-2.0 (Qwen3, VoxCPM2, Kitten, Zonos), MIT (Chatterbox) | VoxCPM2 LoRA from 5-10 min; Qwen3 base models fine-tunable | State of the art for natural languages; can't be told to say [χ] |
| **Kyutai pocket-tts** (v4.0.1, 2026-10) + `willwade/pocket-tts-en-phonemes-24l` | The fine-tune takes space-separated IPA | **English inventory only** (119 tokens from en-us espeak) | No | Yes (CPU) | Code MIT, weights CC-BY-4.0 | Retraining the text embedding (30k steps) | Good; English-only phones |
| **Azure Speech** | `<phoneme alphabet="ipa">` | "Each locale supports a specific phone set"; unrecognized phones → **HTTP 400** | `<prosody>` | Cloud | Commercial | Custom Neural Voice (gated) | Excellent, but no χ c ɟ bʱ in one locale |
| **Google Cloud TTS** | `<phoneme>` IPA / X-SAMPA for ~20 languages | Per-language tables | `<prosody>` | Cloud | Commercial | No | Same limitation |
| **Amazon Polly** | `<phoneme>` ipa / x-sampa (neural: full; generative: partial) | The voice language's phoneme set | `<prosody>` partial | Cloud | Commercial | No | Same limitation |
| **ElevenLabs** | Phoneme tags (CMU Arpabet, IPA) **only on `eleven_flash_v2`**, one word per tag | English-oriented | No | Cloud | Commercial | Voice cloning | Not usable for PIE |

## 2. Hands-on results (this machine, 2026-10-28)

Everything lives under `/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/tts/`. Nothing personal was sent anywhere. The only downloads were Homebrew, PyPI, GitHub, and Hugging Face model files.

### 2.1 eSpeak-NG: works, including per-syllable pitch

1. `brew install espeak-ng` installed 1.52.0 (the latest release). Stock voices already cover the set when combined. `espeak-ng -v hi -q --ipa "[[X H ? c J J# kw gw g#w Xw Q r- l- m- n- b# d# g# a: e: o: i: u:]]"` → `χ h ʔ c ɟ ɟʰ kw ɡw ɡʰw χw ɣ r̩ l̩ m̩ n̩ bʰ dʰ ɡʰ aː eː oː i ˈuː`. The Hindi table has everything except ħ (it becomes h) and unstressed long i (shortened). The Arabic table has ħ ʕ χ ʔ but no murmured stops. Hungarian and Armenian have c ɟ, Czech has the syllabic resonants. eSpeak shows murmur as ʰ in its IPA, but Hindi `b#` is its breathy-voiced stop.
2. **Custom `pie` table** (Hindi base + imports): built with `--compile-phonemes` into a private data directory, no system changes. Round trip `[[H'ekwos ?esti:]]` → `ħˈekwos ʔestiː`.
3. **Tone phonemes** (Vietnamese-style `Tone()` definitions) under a voice with `language vi` gave real high/low syllables. Praat F0 tracks:
   - `[[Xo5wis1]]`: 98 → 82 Hz;
   - `[[Xo1wis5]]`: 82 → 99 Hz;
   - converter output `χá.ɟe.ti` as `Xa5Je1ti1`: high 98-99, then 81-83 Hz;
   - `ɟʱi.méː` as `J#i1me:5`: 81, then 92-99 Hz.

   The range is narrow at the default settings. Widen it with the `Tone()` values or the voice's `pitch` line.
4. **Failure mode (important):** an unknown mnemonic does not just vanish. It silently **truncates the rest of the word**: `[[H'eKw0s]]` → `ħˈe`, and `[[d#e:H0ti]]` → `dʰeːħ`. Every rendering must therefore be round-tripped through `espeak-ng --ipa -q "[[…]]"` and compared against the converter IPA (§4.1, step 5).
5. With `-v hi`, a `;` after s gives retroflex ʂ, and plain `r` is often a tap [ɾ]. The base table decides r and vowel quality.

### 2.2 Piper 1.8.0: works; ʷ and ʱ are missing

`uv pip install piper-tts==1.8.0`, then `python -m piper.download_voices hi_IN-rohan-medium`. The input `[[ χˈowis ʔˈekʷoeskʷe bʰˈer̩ti ɟʰˈims ħˈekʷos ]]` synthesizes with "Missing phoneme from id map: ʷ" (ʷ is dropped), so kʷ must be sent as kw. ʱ is not in the map either; send ʰ.

### 2.3 Kokoro-82M: works from raw IPA; the pitch accent can be imposed

- **ONNX:** `onnx-community/Kokoro-82M-v1.0-ONNX` `model.onnx` plus the `hf_alpha` voice, run with onnxruntime only. The converter IPA, mapped (§4.2), renders. ʷ and ̩ are not in the vocab and must be mapped before input.
- **PyTorch:** `kokoro==0.9.4`. `KModel.forward_with_tokens` computes `F0_pred` and passes it to the decoder. Wrapping `predictor.F0Ntrain` so that F0 is flattened (0.92 × median) and raised (1.3 × median) on the frames of the accented vowel worked:
  - `ɟʱi.méː`: 172-205 Hz on the first syllable, 254-271 Hz on méː;
  - `χá.ɟe.ti`: peak 280 Hz early, then 202-222 Hz.

  Script: `scratchpad/tts/kokoro_pitch.py`; the core is in §4.2. Note: `KPipeline(lang_code="h")` crashes on this Mac (espeakng-loader looks for a CI build path). Load the voice tensor directly with `hf_hub_download("hexgrad/Kokoro-82M", "voices/hf_alpha.pt")`. Raw-IPA use doesn't need the pipeline.

### 2.4 Listening pack (the owner should listen before choosing)

Folder: `/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/tts/pack/`. Manifest: `/private/tmp/claude-501/-Users-david-AI-PIE/7bdc6640-3091-456e-a081-2c28d7d03867/scratchpad/tts/pack/manifest.json`. It records each item's converter IPA, the exact engine input, and eSpeak's IPA round trip.

- **Items:** the phrases χó.wis héc.woːs.kʷe, dʱu.ɡə.téːr, clé.wos ń̩dʱ.ɡʷʱi.tom, χá.ɟe.ti, ɣʷós.tə, ɟʱi.méː and wĺ̩.kʷos, plus minimal pairs kʷe/ke, bʱer/ber, χowis/howis, ʔesti/esti, wl̩kʷos/wəlkʷos, and ħekʷos.
- **Renderings of each item:** `.espeak_stress.wav`, `.espeak_tone.wav`, `.piper_rohan.wav` and `.kokoro_hf_alpha.wav`. Four phrases also have `.kokoro_pitch.wav`.

**Automatic check: inconclusive for the hard sounds.** A multilingual phone recognizer (`facebook/wav2vec2-xlsr-53-espeak-cv-ft`) recovers the rough segment sequence. On the Kokoro output it gave "ɡ ɔ v i t e k o s k w i ɡ a r m o s p e r t i dʒ i m e d o ɡ a t e r". It never emitted χ, ʔ or a murmured stop for any engine, so it cannot judge the sounds that matter. Ears are needed.

## 3. Findings that drive the choice

### 3.1 Nothing outside eSpeak has the whole inventory

No neural model takes all of ɣʷ, ɡʷʱ and syllabic resonants as trained input. Of the neural models, only the StyleTTS2/Matcha symbol table even contains ʱ ʷ ̩, and no released checkpoint was trained on them. ʰ for ʱ is the standard neighbour. Kokoro's Hindi voices and Piper's Hindi voices learned Hindi murmured stops through espeak's `bʰ` notation, so ʰ after a voiced stop *is* breathy voice in those models.

### 3.2 Commercial APIs are locale-bound

Azure: "Each locale supports a specific phone set … If the specified string contains unrecognized phones, text to speech service will return http 400 error." Google and Polly take IPA or X-SAMPA per language table. ElevenLabs takes phoneme tags only on `eleven_flash_v2`, one word per tag. No locale has χ, c/ɟ, murmured stops and syllabic resonants together. The Hindi locales come closest but lack χ (except Urdu loan [x]) and c ɟ. These APIs also aren't local.

### 3.3 "In the vocabulary" ≠ "trained": an embedding-norm proxy

VITS (Piper) trains with AdamW weight decay, so the embedding row of a symbol that never occurs in training decays toward zero. The L2 norm of each row is therefore a cheap proxy for "was this symbol seen". Values for Piper voices are below; ~0.25-0.38 means untrained, ~0.8-1.6 means trained.

| Voice | ʰ | χ | ħ | ʔ | c | ɟ | ɣ | ̩ |
|---|---|---|---|---|---|---|---|---|
| hi_IN-rohan (fine-tuned from en lessac) | 0.76 | 0.84 | **0.26** | 0.96 | 0.82 | 0.80 | 0.94 | 1.60 |
| hi_IN-pratham (from scratch, Hindi only) | 0.86 | 0.94 | **0.06** | **0.22** | 0.87 | 0.88 | 1.19 | **0.23** |
| ar_JO-kareem | **0.28** | 0.80 | 0.76 | 1.02 | **0.27** | **0.25** | 0.88 | 1.02 |
| hu_HU-anna (CC0) | **0.31** | **0.29** | **0.31** | 1.13 | 0.71 | 0.64 | **0.30** | 1.16 |
| en_US-ljspeech (public domain) | **0.38** | **0.35** | **0.38** | **0.34** | **0.37** | **0.35** | **0.36** | 1.66 |

The proxy checks out. pratham, trained only on Hindi, has untrained ʔ and ̩, while rohan, fine-tuned from English lessac, has both trained, exactly as English exposure predicts. **hi_IN-rohan-medium is the best single Piper voice for PIE**: everything except ħ, which is fine because the default h₂ is χ. Its dataset licence (IIT Madras IndicTTS) reads as royalty-free in the excerpts found, but this is **not verified**. The pratham and priyamvada data are **CC-BY-NC-SA**.

For Kokoro (no weight decay on the text encoder), only the PL-BERT embedding is informative. There χ 0.52, c 0.67 and ɟ 0.74 are present but weaker than common phones (~0.9-1.1), so they were probably seen rarely. ʔ 1.11 and ʰ 1.17 are strong. This is weak evidence; listen.

### 3.4 Pitch accent

- **eSpeak:** true per-syllable level tones via custom tone phonemes (tested). Fallback: one `'` per accented syllable, which gives a pitch peak.
- **Kokoro/StyleTTS2:** edit the predicted F0 on the accented vowel's frames (tested on Kokoro). This is the only natural-sounding option here with explicit pitch.
- **Piper/VITS, Matcha:** stress ˈ only. Pitch could be re-imposed after synthesis with Praat PSOLA (`praat-parselmouth`, GPL) or WORLD (`pyworld`), using the converter's syllable timing. That works for any engine, but it's more work and adds artefacts.

## 4. Setup steps

### 4.1 (a) eSpeak-NG with the `pie` table

1. Install and get the phoneme sources, keeping the system install read-only:
   ```sh
   brew install espeak-ng                      # 1.52.0
   W=~/pie-tts && mkdir -p $W && cd $W
   git clone --depth 1 --branch 1.52.0 https://github.com/espeak-ng/espeak-ng.git src
   cp -R /opt/homebrew/Cellar/espeak-ng/1.52.0/share/espeak-ng-data data/ && chmod -R u+w data
   cp -R src/phsource data/phsource
   ```
2. Add `data/phsource/ph_pie` and register it:
   ```
   // PIE: Hindi base (murmured stops, c ɟ, χ ɣ ʔ, syllabic resonants) + Arabic pharyngeals + level tones
   phoneme H                       // ħ (pharyngeal preset h2)
     import_phoneme ar/H
   endphoneme
   phoneme A                       // ʕ (pharyngeal preset h3)
     import_phoneme ar/A
   endphoneme
   phoneme i:                      // Hindi shortens unstressed i:, PIE must not
     vwl lng starttype #i endtype #i
     length 230
     FMT(vowel/i_fnt)
   endphoneme
   phoneme 1                       // low level tone: unaccented syllable
     stress
     Tone(22, 20, envelope/p_level, NULL)
   endphoneme
   phoneme 5                       // high level tone: the PIE acute
     stress
     Tone(55, 52, envelope/p_level, NULL)
   endphoneme
   ```
   ```sh
   printf '\nphonemetable pie hi\ninclude ph_pie\n' >> data/phsource/phonemes
   mkdir -p data/espeak-ng-data/voices/pie
   printf 'name pie\nlanguage hi\nphonemes pie\n'           > data/espeak-ng-data/voices/pie/pie
   printf 'name pie-tone\nlanguage vi\nphonemes pie\n'      > data/espeak-ng-data/voices/pie/pie-tone
   ESPEAK_DATA_PATH=$W/data espeak-ng --compile-phonemes=$W/data/phsource   # "0 errors"
   ```
3. Map converter IPA to mnemonics. Work on the NFD form, reorder ʷʱ → ʱʷ first (eSpeak puts murmur on the stop, then w), and drop the `.` syllable dots.

   | IPA | χ | ħ | ʕ | ɣ | ʔ | h | c | ɟ | ɡ | ʱ | ʷ | ə | ː | ̩ | ˈ | j | others |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
   | eSpeak | `X` | `H` | `A` | `Q` | `?` | `h` | `c` | `J` | `g` | `#` | `w` | `@` | `:` | `-` | `'` | `j` | same letter |

   Examples: ɡʷʱ → `g#w`, ɣʷ → `Qw`, n̩ → `n-`, ‖ → `_:` (long pause) and | → `_` (short pause).
4. Choose the accent mode:
   - **Stress:** `to_ipa(…, tone="stress")`, then `espeak-ng -v pie/pie "[[…]]"`.
   - **Tone:** `to_ipa(…)` with the acute. Split each word on `.`, strip the acute, append `5` to the accented syllable and `1` to every other, then `espeak-ng -v pie/pie-tone "[[Xa5Je1ti1]]"`.
5. **Validate every rendering:** compare `espeak-ng -v pie/pie -q --ipa "[[…]]"` against the converter IPA. Normalise first: drop dots, stress and tone, read eSpeak's ʰ after a voiced stop as ʱ, and treat `kw` as kʷ. Fail on any difference. This catches the silent truncation in §2.1, item 4.
6. Render with `-w out.wav` (22.05 kHz). Use `-s 130` for a slower rate and `-p`/`-a` for pitch and amplitude. Optionally run OpenVoice v2 (MIT) tone-colour conversion afterwards to make it sound less robotic, without changing the segments.

### 4.2 (b) Kokoro-82M, raw IPA plus imposed accent

1. Install and fetch weights (CPU is enough; MPS optional):
   ```sh
   uv venv kokoro && uv pip install --python kokoro/bin/python kokoro==0.9.4 soundfile
   ```
   ```python
   import torch, soundfile as sf
   from huggingface_hub import hf_hub_download
   from kokoro import KModel
   model = KModel(repo_id="hexgrad/Kokoro-82M").eval()
   voice = torch.load(hf_hub_download("hexgrad/Kokoro-82M", "voices/hf_alpha.pt"), weights_only=True)
   ```
   Hindi voices: `hf_alpha`, `hf_beta`, `hm_omega`, `hm_psi`. Try the English `af_heart` too; it is the best voice overall but had no exposure to murmured stops.
2. Map to Kokoro's vocab (NFD; drop dots):

   | converter | Kokoro input |
   |---|---|
   | ʷʱ → ʱʷ, then ʱ | ʰ |
   | ʷ | w (kʷ → kw: the only option) |
   | ħ / ʕ (pharyngeal preset) | χ / ɣ |
   | C + ̩ (r̩ l̩ m̩ n̩) | ə + C (`ń̩dʱ` → `əndʰ`, tone on ə) |
   | acute | removed; drives the F0 mask; optionally also ˈ before the syllable |
   | ‖, \| | `.`, `,` |

   Characters not in `model.vocab` are silently dropped by `KModel.forward`. Assert that nothing is dropped.
3. Impose the accent: wrap `model.predictor.F0Ntrain`, and replace voiced F0 frames with `median × 1.3` on the accented vowel (and its ː) and `median × 0.92` elsewhere. Smooth over ~9 frames. F0 runs at twice the alignment frame rate, so expand the token mask with `repeat_interleave(mask, pred_dur)` and then ×2. Run `forward_with_tokens` once to get `pred_dur`, then again with the patch. The core, as tested:
   ```python
   # ids: [[0, *token_ids, 0]]; hmask: bool per id (True on the accented vowel and its ː), same length
   _, dur = model.forward_with_tokens(ids, ref_s, 0.9)
   orig = model.predictor.F0Ntrain
   def patched(en, s):
       F0, N = orig(en, s)
       frames = torch.repeat_interleave(torch.repeat_interleave(hmask, dur), 2)[: F0.shape[-1]]
       voiced = F0[0] > 10
       base = F0[0][voiced].median()
       target = torch.where(frames, base * 1.3, base * 0.92)
       target = torch.nn.functional.conv1d(target[None, None], torch.ones(1, 1, 9) / 9, padding=4)[0, 0]
       return torch.where(voiced, target, F0[0])[None], N
   model.predictor.F0Ntrain = patched
   audio, _ = model.forward_with_tokens(ids, ref_s, 0.9)
   model.predictor.F0Ntrain = orig
   ```
   A full script (`kokoro_pitch.py`) was in this session's temporary scratchpad. Rebuild it in the repo when the TTS integration is built.
4. Pick the `ref_s` row by phoneme count (`voice[len(phonemes) - 1]`). Inputs are limited to 510 tokens, so synthesize line by line.
5. If it sounds wrong on χ, c or ɟ, the fallback is Piper `hi_IN-rohan-medium` (`piper-tts==1.8.0`, `[[ … ]]`, ʱ → ʰ, ʷ → w, keep ̩). Confirm the IndicTTS licence before a public demo.

### 4.3 (c) Fine-tuning on the owner's voice

**Recording:** 1-3 h of clean single-speaker audio, 24 kHz or more, one corpus line per file. Label with `to_ipa(…)` output for the same convention used at inference. Make the labels **narrow**: the reading must actually realise χ, c, ɟ, murmur and the syllabic resonants, or the model learns whatever was said. Record the accented syllable high, so a pitch-capable model can learn the accent from data.

1. **Kokoro fine-tune (primary).**
   - Recipe: `semidark/kikiri-tts` (formerly `kokoro-deutsch`, Apache-2.0, 2026-06) and its fork `shreyaskarnik/bol-tts-marathi` (2026-07). Steps: data prep → Stage 1 → Stage 2 → voicepack extraction → `KModel` inference; there is Mac inference in the Marathi recipe.
   - Tokens: the embedding has 178 ids and the shipped vocab uses 113, so give ʱ ʷ ̩ ħ ʕ, and optionally a tone token such as ↑, their own unused ids.
   - Hardware: one rented 24-80 GB CUDA GPU. Expect hours, not days, for Stage 2 on 1-3 h of data. This is extrapolated from the StyleTTS2 README (1 h fine-tune ≈ 4 h on 4×A100).
   - Licence: stays Apache-2.0, and explicit F0 keeps the accent controllable.
2. **Piper (lower risk, lower ceiling).**
   ```sh
   git clone https://github.com/OHF-voice/piper1-gpl && cd piper1-gpl
   python3 -m venv .venv && . .venv/bin/activate && pip install -e '.[train]' && ./build_monotonic_align.sh
   python3 -m piper.train fit --data.voice_name pie_owner --data.csv_path meta.csv --data.audio_dir wav/ \
     --data.phoneme_type text --model.sample_rate 22050 --data.cache_dir cache/ \
     --data.config_path pie_owner.onnx.json --data.batch_size 32 --ckpt_path <medium checkpoint>
   ```
   - `meta.csv` rows are `utt.wav|<IPA>`. With `phoneme_type text`, each NFD code point is a phoneme, so ʱ ʷ ̩ and the acute become tokens of their own. Alternatively use `--data.data_type phoneme_ids` with your own id map so that kʷ, ɡʷʱ and the like are single ids.
   - Start from the `hi_IN-rohan` or lessac medium checkpoint (the docs say a checkpoint "will speed up training a lot, even if the checkpoint is from a different language").
   - Lightning on CUDA. Export to ONNX and run on the Mac.
   - No explicit pitch, but with the acute or ↑ as a token it can learn the accent from the recordings.
3. **StyleTTS2 directly** (`train_finetune.py` from the LibriTTS checkpoint): this is Kokoro's parent, with the same F0 control. Its IPA table already has ʱ ʷ ̩ ħ ʕ and tone arrows. Its pre-trained models carry the "inform listeners that the speech is synthetic" condition, which a demo can meet. DDP is broken (single GPU only). Use it if the Kokoro recipe fights the new tokens.
4. **Matcha-TTS** (MIT, same symbol table, trains fastest) is a reasonable experiment, but it has no F0 control.
5. Not recommended: the NC families F5/E2, XTTS, MMS and Fish, and the text-only LLM TTS models (Qwen3-TTS, VoxCPM2, CosyVoice 3, Chatterbox). The text-only models would need their text tokenizer retrained on IPA. LoRA from minutes of audio teaches a voice, not new phones.

## 5. Workarounds for missing phonemes, in order of preference

1. **Pick a convention the engine can say.** The converter's default h₂ = χ is native nearly everywhere; ħ isn't. h₁ = h, the default, is safer than ʔ.
2. **Nearest-neighbour mapping, done in one place.** The rules are ʱ → ʰ (breathy in Hindi-trained voices), ʷ → w, ħ → χ, ʕ → ɣ, and C̩ → əC in engines without ̩. Then assert that the engine drops nothing (Piper warns, Kokoro silently filters, eSpeak truncates).
3. **Combine tables in eSpeak** with `import_phoneme <table>/<phoneme>`; it compiled with 0 errors.
4. **Train with a custom symbol set**: Piper `phoneme_type text` / `phoneme_ids`, StyleTTS2/Matcha IPA table, or Kokoro unused ids.
5. **Post-hoc prosody:** Praat or WORLD resynthesis of F0 on the accented syllables, for engines without F0 input.

## 6. Caveats

- **Nobody has listened yet.** The norm proxy and the phone recognizer can't certify χ, c, ɟ or murmur; the owner must listen to the pack (§2.4) before 11-11.
- The neural options say kʷ as k+w, and say ɡʷʱ as ɡʰw.
- Kokoro on Hindi voices will carry a Hindi accent (dental/retroflex t d, Hindi vowel colours). eSpeak's `hi` base does the same (tap r).
- Licences: Piper hi_IN pratham/priyamvada (NC-SA data), XTTS (CPML), F5/E2 (CC-BY-NC), MMS (CC-BY-NC) and Fish (community/research) are **not** for commercial use. Kokoro (Apache), eSpeak and Piper code (GPL-3.0; audio output is not covered), Matcha (MIT) and StyleTTS2 (MIT plus the disclosure condition) are usable. The IndicTTS (rohan) licence is unverified.
- `pie/ipa.py`'s X-SAMPA output (`J\` for ɟ, `_t` for murmur) is **not** eSpeak input. eSpeak uses `J` and `#`. Keep the eSpeak mapping in the TTS integration, as `docs/pronunciation.md` §9 says.

## Sources (all accessed 2026-10-28)

- eSpeak-NG repo and 1.52.0 release: https://github.com/espeak-ng/espeak-ng, https://github.com/espeak-ng/espeak-ng/releases. Phoneme source used: `phsource/phonemes`, `ph_hindi`, `ph_arabic`, `ph_vietnam` at tag 1.52.0.
- Piper: https://github.com/OHF-Voice/piper1-gpl (README; `docs/CLI.md` "Raw Phonemes"; `docs/TRAINING.md` "Custom Phonemes", "Custom Phoneme Ids"); PyPI `piper-tts` 1.8.0 https://pypi.org/project/piper-tts/; archived https://github.com/rhasspy/piper; voices and model cards https://huggingface.co/rhasspy/piper-voices.
- IndicTTS licence: https://www.iitm.ac.in/donlab/indictts/database, https://www.iitm.ac.in/donlab/indictts/downloads/license.pdf (could not be downloaded; excerpts via search).
- Kokoro: https://huggingface.co/hexgrad/Kokoro-82M (model card, `config.json` vocab), https://github.com/hexgrad/kokoro (`kokoro/model.py`), https://github.com/hexgrad/misaki, ONNX https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX.
- Kokoro fine-tuning recipes: https://github.com/semidark/kikiri-tts, https://github.com/shreyaskarnik/bol-tts-marathi.
- StyleTTS2: https://github.com/yl4579/StyleTTS2 (README "Finetuning", pre-trained model condition; `text_utils.py`).
- Matcha-TTS: https://github.com/shivammehta25/Matcha-TTS (`matcha/text/symbols.py`).
- Coqui: https://huggingface.co/coqui/XTTS-v2 (CPML), fork https://github.com/idiap/coqui-ai-TTS (v0.28.0).
- F5-TTS: https://github.com/SWivid/F5-TTS, https://huggingface.co/SWivid/F5-TTS (CC-BY-NC-4.0 weights).
- MMS-TTS: https://huggingface.co/facebook/mms-tts-eng.
- Parler-TTS: https://github.com/huggingface/parler-tts. OpenVoice: https://github.com/myshell-ai/OpenVoice.
- Fish Speech: https://github.com/fishaudio/fish-speech (README licence notice, LICENSE).
- CosyVoice 3: https://github.com/FunAudioLLM/CosyVoice (now QwenAudio/CosyVoice), https://huggingface.co/FunAudioLLM/Fun-CosyVoice3-0.5B-2512.
- Qwen3-TTS: https://github.com/QwenLM/Qwen3-TTS. VoxCPM2: https://huggingface.co/openbmb/VoxCPM2, https://github.com/OpenBMB/VoxCPM.
- Chatterbox: https://github.com/resemble-ai/chatterbox. Kitten TTS: https://github.com/KittenML/KittenTTS. Zonos: https://github.com/Zyphra/Zonos.
- pocket-tts: https://github.com/kyutai-labs/pocket-tts, https://huggingface.co/willwade/pocket-tts-en-phonemes-24l.
- Azure: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-pronunciation, https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-ssml-phonetic-sets.
- Google: https://docs.cloud.google.com/text-to-speech/docs/phonemes.
- Amazon Polly: https://docs.aws.amazon.com/polly/latest/dg/phoneme-tag.html, https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html.
- ElevenLabs: https://elevenlabs.io/docs/best-practices/prompting/controls.
- Phone recognizer used for the sanity check: https://huggingface.co/facebook/wav2vec2-xlsr-53-espeak-cv-ft.
