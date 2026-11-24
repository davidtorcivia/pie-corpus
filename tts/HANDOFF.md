# PIE text to speech: handoff

*2026-11-24. This covers all the audio-model work to date, and the plan for the next step.*

## The goal

Build our own complete PIE text-to-speech model and replace Kokoro on the site with it.

The reference is **tiny-voca** (github.com/n4ze3m/tiny-voca, Apache-2.0), a small English text-to-speech model:
- 4.5M parameters and 18 MB, waveform generator included;
- about 70× real time on four CPU threads, and it runs in the browser through ONNX Runtime Web;
- trained from scratch, in 7.7 h on one RTX 4090, on 17.6 h of synthetic speech.

That last point is the model for this plan. A big, slow, accurate pipeline generates a corpus, and a small fast model learns from it. We have the slow pipeline. The owner has listened to tiny-voca's English and said "it sounds good".

"Our own" means:
- trained from random weights;
- trained only on our data;
- no borrowed base model or vocoder in the shipped chain.

## Why replace Kokoro

Kokoro is live on the site: model `kokoro-final-v3`, epoch 15. The site uses two of its four voices, Zazy for male and Valeria for female.

| | Kokoro (live) | Our chain (Chimera → wokʷs → gʷerh) |
|---|---|---|
| Base model | borrowed (fine-tuned from kokoro_base) | trained from scratch, all ours |
| Training targets | the paid voice conversions | Chimera input, paid clips as targets (until a corpus of its own exists) |
| Word accuracy (lower is better) | .286 on 12 lines, the best measured | ≈ .30 (wB4b, 24 lines; not a head-to-head) |
| Trill | doesn't trill (trill share .178) | trills (≈ .6, about paid's level) |
| Phone drift | inherits the paid conversions' drift | keeps Chimera's phones by construction |
| Speed | fast, a single model | Chimera render + two networks; not live yet |

**What drifts.** The paid conversions change phones: on 18 lines, the recognizer missed 40.6% of phones in paid against 34.2% in Chimera itself. The owner has also heard mispronunciations in the paid female clips.

**What carries through.** Our converters keep Chimera's phones. On those 18 lines an earlier phone-track converter missed 32.6%, against Chimera's 34.2%. wokʷs is built the same way, on Chimera's timing and phone tokens.

**The bar.** A replacement has to keep Chimera's phones and trills and sound at least as natural as Kokoro.

## What we have

### Source: Chimera, a physical vocal-tract synthesizer

- **Repo:** fork github.com/davidtorcivia/chimera-vocal-synth, branch `pie` (MIT licence; upstream jamesondh/chimera-vocal-synth). PIE planning is in `crates/chimera/src/phonetics/pie.rs`.
- **Engine merge (2026-11-24):** the branch now carries upstream's 232 commits of voice work, merged in commit 61f0de5. On the owner's blind raw test the merged engine won 8–1.
- **Accuracy:** the recognizer misses 27.5% of phones on the held-out set, the most accurate source we have. It sounds synthetic.
- **Renderer:** `pie/fullrender.py`, with binary `target/release/examples/pie`. It renders on **given phone timing** (see Gap 1).
- **Speed:** CPU only, deterministic. It also runs in the browser as WASM; that's the Chimera app's own Speak panel, with the PIE chip.

### Converter: wokʷs (*wṓkʷs* 'voice'), checkpoint **wB4b step 8000**

- **What it does:** Chimera features plus PIE phone tokens go in; a natural voice's log-mel comes out. 13.3M parameters.
- **Timing:** phones are expanded by Chimera's own timing, so no phone can be added, dropped or moved.
- **Training:**
  - Phase A: mel regression.
  - Phase B: spectrogram critics. These fixed the "snare drum" buzz, which was frequency over-smoothing.
- **Code:** `tts/wokws/` (`wokws.py`, `train.py`, `render.py`, `PLAN.md`).

### Vocoder: gʷerh (*gʷerh₃-* 'swallow, throat'), checkpoint **g3f step 188,000**

- **Architecture:** BigVGAN-base, 13.9M parameters, trained from scratch. It reads 100-band log-mel at 32 kHz with hop 320 (100 frames/s) and outputs 44.1 kHz.
- **Training data:** paid clips, mixed with wokʷs's predicted mels, so it learns from the kind of input it gets at inference.
- **Choice:** g3f is the owner's pick by ear (2026-11-23); 216k gave no audible gain.
- **Code:** `tts/wokws/gwerh.py`, `gwerh_train.py`.

### Voices

All four are in every model:

| Voice | Sex | Paid hours |
|---|---|---|
| Zazy | male | ~5 |
| Antonio | male | ~3 |
| Valeria | female | ~5 |
| W02 | female | ~3 |

### Data

| What | Where | Size |
|---|---|---|
| Paired training data: features, 44.1 kHz targets, predicted mels | HF `disinfozone/pie-voice-train` (private), plus `~/AI/chimera-pie-data/wokws/data` | 6,660 pairs, 16.4 h, train/val split in `pairs.json` |
| Chimera renders, public | HF `disinfozone/pie-chimera-speech` (CC BY-SA 4.0) | 4,238 clips, 10.4 h |
| Corpus phone timing (from the old VocalTractLab build) | `~/AI/chimera-pie-data/full/timing/*.json` | one per clip |
| wokʷs and gʷerh checkpoints | `~/AI/chimera-pie-data/wokws/runs/` and HF private `ckpt/` | |

### How we measure

- **The owner's ear decides.** Every listening decision goes on a blind A/B page: randomised order per line, loudness-matched, a "Better" button, and silence counted as a tie.
- **Recognizer phone misses:** `pie/gop.py` in the Chimera repo, scored with PhoneticXeus on known phone spans. It can't hear murmur or palatal stops; those need the acoustic checks (`pie/murmur.py`).
- **Word check and trill share:** checks for a broken run only, never for ranking. The ear has overruled them several times.

## The gaps between our chain and a text-to-speech model

1. **Timing for new text.** Chimera renders on given phone durations. Every corpus clip so far took its timing from the old VocalTractLab build. For new sentences we need a duration source. Chimera's own text planner (`parse_pie` / `plan_pie`, used by the app's PIE chip) already makes durations. Check it against the VocalTractLab timings on the existing corpus before relying on it. Our converter takes timing from Chimera, so whatever timing we pick is the timing the voice will have.
2. **Corpus size.** 16 h across four voices is thin; tiny-voca used 17.6 h for two. New corpus generation now means rendering new PIE text with merged Chimera and running it through wokʷs and gʷerh, at no cost. Paid conversions are over (owner, 2026-11-24).
3. **Speed and size.**
   - The chain is about 27M parameters of networks, plus a physics simulation.
   - A tiny-voca-sized model could run in the visitor's browser.
   - gʷerh alone is 14M, so a browser target needs either a smaller vocoder or one shared on a server.

## Proposed plan

**Stage 0: baseline (Mac CPU, no GPU).**
- Blind A/B of the full chain against Kokoro e15 on held-out lines, for the two site voices.
- This has never been done for wokʷs. It tells us whether the chain's sound already reaches Kokoro's, and so whether we distil now or improve the chain first.

**Stage 1: timing for new text.**
- Have the PIE planner write its phone durations, and render a few hundred corpus sentences on both the planner's and the VocalTractLab timing.
- Compare by blind A/B and by recognizer phone misses. Keep whichever is better, or blend the two.

**Stage 2: generate the corpus (Mac CPU, niced, no paid services).**
- Text: archaic PIE sentences from the project corpus. In-world, inherited vocabulary first; see the project's archaic-first rule.
- Render with merged Chimera, then convert through wB4b and g3f into all four voices.
- QC every clip:
  - recognizer phone misses against the intended phones;
  - drop the clips where the conversion drifted, using the same screen as the converter's training data.
- Target: well over 16 h per voice pair.
- Licensing: the public Chimera dataset is CC BY-SA. Whether converted clips can be published is an owner call.

**Stage 3: the text-to-speech model, tiny-voca style.**
- Input: PIE text, turned into PIE phone tokens (the same 48-symbol inventory the converter uses), plus a speaker id for the four voices.
- Predicts:
  - phone durations, learned from the corpus timing;
  - pitch, voicing and energy;
  - then a 100-band log-mel in the shared format.
- Vocoder: gʷerh (g3f) first. A small vocoder distilled from gʷerh later, if we target the browser.
- What to reuse:
  - wokʷs's encoder, prosody and acoustic stacks, without the Chimera input features;
  - its Phase B spectrogram critics.
- What not to repeat: tiny-voca's own waveform head (a pulse train at an explicit pitch with learned filters). That was our tvc line, and it buzzed and sounded tinny, especially on stops and fricatives.
- Train on the Stage 2 corpus. Whether to also train on the paid clips directly is an owner call (licensing; Kokoro already does).

**Stage 4: gates, then replace Kokoro.**
- Blind A/B against Kokoro on held-out text, per voice. Accuracy has to stay at least at Chimera's level, and trills have to survive.
- Then re-render the site audio: the hymn, the readings and the 8,324 dictionary words, in the same way Kokoro's were done.

**Option to weigh: ship the chain instead of a new model.** Chimera, wokʷs and gʷerh already make speech from PIE text once Gap 1 is closed. For pre-rendered site audio the chain's speed may not matter. A small model matters for live speech (the translator demo) and for the browser.

## Lessons that cost us time

- **Metrics don't replace the ear.** Envelope periodicity ("buzz"), cycle-to-cycle similarity, HNR and comb clarity all rated versions the owner disliked as close to or better than the target. Use metrics to find broken runs and to locate problems, and blind pages to decide.
- **Test only on held-out lines.** A converter's training lines flatter its usual input. On 2026-11-24 a first A/B page mixed in 11 training lines and had to be rebuilt.
- **No candidate may change words or phonemes.** Content-regenerating models such as Seed-VC were dropped for this, after the owner heard wrong words.
- **"Buzzy / snare drum / doubled" was frequency over-smoothing** from mel regression. The owner confirmed it with blurred-paid controls, and spectrogram critics fixed it.
- **Male voices are harder.** Every continuous-mel generator before wokʷs lost all its male trials. A male 80-band mel barely pins the pitch, so the vocoder has to infer it from fine cues.
- **Train the vocoder on the kind of input it gets at inference.** gʷerh mixes in predicted mels; mels predicted on training clips are cleaner than inference output.
- **Don't fine-tune a vocoder end to end with the mapper on this data.** It damaged a released vocoder early on.
- **Mac GPU:** torch 2.8–2.12 corrupts memory in BigVGAN's backward pass on MPS (`tts/wokws/MPS_NOTES.md`); use torch 2.13 or later.
- **Desktop GPU training is launch-bound.** A bigger batch is nearly free until memory runs out (Kokoro run notes in `tts/kokoro/v2/`).

## Rules for whoever picks this up

- No human voice actors, no recordings of real speakers as targets, and no paid conversions.
- The desktop GPU is the owner's display card:
  - any job there needs the owner's explicit OK for that job;
  - cap VRAM at 0.8, with a whole-card watchdog;
  - one GPU process at a time, and every run must be pausable.
- **Mac:**
  - CPU only, never the Mac GPU, at the lowest priority with two threads while the owner trains there;
  - don't touch the owner's own runs.
- **Colab** (G4 is about 1.6× the desktop on gʷerh): kit in `tts/wokws/colab`. Always stop a billed session.
- **Public pages and repos:**
  - never name the paid voice service;
  - never post its audio, the paired mels or prosody, or converter outputs.
  - Keep keys, tokens, hostnames and network details out.
- Vendored code (tiny-voca, BigVGAN, Chimera upstream) is imported, never edited.
