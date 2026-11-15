# wokʷs and gʷerh: our own speech-to-speech voice, from scratch

*Started 2026-11-15.*

## Names

- **wokʷs**, from PIE *\*wṓkʷs* 'voice'. It shares a root with *\*wékʷos* 'word' (wekwos). This is the converter: Chimera's PIE render goes in, and a natural voice comes out.
- **gʷerh**, from PIE *\*gʷerh₃-* 'to swallow'. That root gives words for the throat, such as Old Church Slavonic *grъlo*. This is our own vocoder, which turns wokʷs's spectrogram into audio.

Both are trained from random weights, only on our data: Chimera renders, and the paid conversions of those renders as targets. Until gʷerh is ready, the GPT-SoVITS v4 vocoder stands in. It is frozen, and it reads the same spectrogram format. When gʷerh passes its blind test it replaces v4, and the converter doesn't change. After that nothing in the chain is borrowed.

## Why a new run

The previous converter, tvc (tiny-voca parts, 4.5M parameters), made the audio itself with a source-filter output stage: a band-limited pulse train at an explicit pitch, shaped by learned filters. It beat paid on pronunciation and matched it on trills. Its output stage set the quality ceiling:

| Checkpoint | Owner's verdict |
|---|---|
| Round 23, step 80k | "very close, but it has a tinny buzzy sound that prevents it from reaching parity" |
| Round 24, step 25k | "still buzzes/sounds a little tinny at points but much improved" |

The measurements agree:

- **Buzz grew late in training.** Envelope periodicity at the pitch period, 1–4.5 kHz, was paid-level at 20k–30k (.33 against paid's .32). It then climbed to .57 by 80k. The learning rate was constant and the GAN kept pushing.
- **The rest is in the output stage.** At 25k, the excess periodicity over paid is on stops (+.17) and fricatives (+.18), while vowels and nasals sit at paid's level. The same output stage, fed paid's own features (the ceiling run), is already slightly more periodic than paid. A regular pulse train that nothing gates off in consonants explains both.
- **The v4 vocoder doesn't have the problem.** Paid run through v4 (copy-synthesis) comes out:
  - less periodic than paid in every band;
  - within 0.7 dB of paid's long-term spectrum;
  - .589 on trills, against paid's .595;
  - 1–3 against paid in round 21, with 8 can't-tell.

  The GPT-SoVITS line failed in its generator, not its vocoder.

So the new line predicts a spectrogram and leaves the waveform to a vocoder.

## The spectrogram format, shared by wokʷs and gʷerh (`audio.py`)

| Setting | Value |
|---|---|
| Analysis rate | 32 kHz |
| STFT | Hann window, n_fft = 1280, hop 320 (100 frames/s) |
| Padding | reflect-padded by 480 on each side, not centered |
| Bands | 100 Slaney mel bands, 0–16 kHz |
| Values | natural log of magnitude, clamped at 1e-5 |

This is numerically identical to the v4 vocoder's input (max difference 0.0 on a test clip). N frames correspond to exactly 320 N samples at 32 kHz, or 441 N at 44.1 kHz. gʷerh outputs 44.1 kHz, the paid clips' native rate. v4 outputs 48 kHz.

## wokʷs (`wokws.py`, `train.py`)

**Inputs.**

- PIE phone tokens, plus each phone's class (vowel, stop, fricative, ...).
- Tokens are expanded by **Chimera's own timing**. There is no duration predictor, so no phone can be added, dropped or moved.
- Per-frame Chimera features: log-mel 100, plus log F0, voicing and energy.

**Network.** Transformer blocks are tiny-voca's (Apache-2.0, imported, not edited). Width 256, 4 heads.

| Stack | Layers | Job |
|---|---|---|
| Encoder | 4 | phone tokens and classes |
| Prosody | 3 | predicts paid's pitch, voicing and energy |
| Acoustic | 8 | turns frames into paid's log-mel |

A 5-layer convolutional postnet follows the acoustic stack. Total: 13.3M parameters, against tvc's 4.5M.

**Phase A: regression.**

- Losses:
  - mel L1, before and after the postnet;
  - paid-prosody losses (pitch, pitch spread, voicing, energy).
- Teacher forcing (feeding the true prosody in early training): held for 3k steps, then ramped down to off by 10k.
- Masking: Chimera's features are zeroed on about 15% of frames, in 12-frame spans. That way pronunciation has to come from the tokens.
- Schedule and averaging:
  - AdamW;
  - 1k-step warm-up, then cosine decay to 10% of the learning rate;
  - an averaged copy of the weights (EMA 0.999), which is what gets exported.
- Data: the same 15% drift screen as tvc. It drops the train pairs where the paid conversion strayed most from Chimera's phones.
- Phase A is also the blur check. Its output goes through v4 onto a blind page before anything adversarial is added.

**Phase B: spectrogram critics.**

- Starts from Phase A's weights.
- Critics: three 2D convolutional critics on 32-, 64- and 128-frame windows of the mel itself.
- Losses: LSGAN plus feature matching.
- Scaling: the GAN's gradient is set to 0.5× the reconstruction gradient at the predicted mel.
- The critics judge the spectrogram, not any vocoder's audio. A converter tuned through v4's audio could learn v4's blind spots and emit spectrograms gʷerh won't read well. Spectrogram critics keep the output looking like real paid spectrograms.

## gʷerh (`gwerh.py`, `gwerh_train.py`)

**Generator.** BigVGAN's code (NVIDIA, MIT licence; imported, not edited), at base size: 13.9M parameters.

- snake-beta, anti-aliased activations;
- upsampling 7 × 7 × 3 × 3 = 441 samples per frame.

The 2026 re-evaluation of Vocos found that waveform-domain BigVGAN still clearly beats frequency-domain Vocos.

**Recipe.**

- Critics: multi-period, plus the multi-scale sub-band CQT discriminator (built for harmonic detail, which is where tvc's buzz lived).
- Losses: multi-scale mel loss ×15, plus feature matching.
- Optimizer: AdamW (0.8, 0.99) at 1e-4.
- Training aids:
  - PhaseAug on the critics' inputs;
  - a random peak level of −6 to −1 dBFS, with the mel shifted to match;
  - averaged weights (EMA), which are exported;
  - gradient clip 100 for the first 20k steps, then 500. That's BigVGAN's advice for training from scratch at small batch sizes.

**Data.** All 6,660 paid clips (16.4 h). A vocoder only reproduces the paid voice, so the drift screen doesn't apply. The bigger corpus gets added later.

**Checkpoints.** The held-out screen is the L1 between the output's mel and the clip's own. The owner's ear picks. I found no published step count for BigVGAN trained from scratch on this little data, so expect several nights.

## Left out on purpose

- **Muon optimizer.** It's about 2× more compute-efficient for LLMs, but I found no speech or vocoder results. With the output stage, size, resolution, losses and schedule all changing at once, a new optimizer would make results impossible to attribute. A short A/B later.
- **Flow-matching or diffusion refiner.** The second-line fix for blur, only if the Phase B critics aren't enough.
- **Re-rendering Chimera with variations.** Paid followed Chimera's pitch, so changing input pitch or timing breaks the link between input and target. Only timbre or noise changes are safe, and only after the pitch-follow check. Deferred to the corpus phase.

## Gates and checks

1. **Data** (Mac CPU, `prep.py`): spectrograms, prosody and tokens for every pair, plus the 44.1 kHz target audio.
2. **Desktop sweeps:**
   - gʷerh at batch 8 and 16 (NaN and memory);
   - wokʷs at 27k and 40k frames per batch, critics on.
   - Acceptance: whole-card memory ≤ 24 GB. torch is capped at 0.7 of the card, a watchdog stops any run that goes over 24.5 GB twice in a row, and only one GPU process runs at a time.
3. **wokʷs Phase A, 50k steps,** then Phase B, 20k steps.
   - Every 5k steps: render through v4, then word check, trill share, local buzz (by phone class) and long-term spectrum.
   - These are screens. The owner's ear decides, on blind pages.
4. **Required before any claim of pitch control:** raise Chimera's pitch 2 semitones and check the output follows. This is needed for the later TTS.
5. **Fair comparisons.** Paid is native 44.1 kHz and the blind reference so far has been paid24. Either bring wokʷs down to 24 kHz to match paid24, or build a 44.1 kHz paid reference. Settled before round 25.
6. **gʷerh from scratch** (the long stage), then a blind ceiling test against paid (copy-synthesis), then the swap.

Every run can be paused (a `STOP` file saves `last.pt`) and resumed (`--resume`). The first save checks that the weights changed, and validation checks that the Chimera features are actually used (by zeroing them).

## After this

The corpus phase: render more PIE through Chimera, convert it with wokʷs + gʷerh, then train a new TTS on the larger corpus. gʷerh retrains on the bigger voice data along the way.
