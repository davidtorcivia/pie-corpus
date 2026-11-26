# g7_hnm_dual: third-opinion code audit (Opus, high), 2026-11-25

Files read in full: `gwerh_hnm_dual.py`, `gwerh_hnm_dual_train.py`, `pietts/predmels_pietts.py`, `pietts/model.py` (synthesize / make_item / collate), `colab/vm_run_g7.sh`. I also read the kit around them (`vm_push.sh`, `keepalive.py`, `colab_check.sh`, `colab_train.sh`, `runs.sh`) and the BigVGAN `loss.py` / `discriminators.py` APIs.

## Verdict

- **Model, DSP and training code: GO.** I found no remaining P0 or P1 in the generator, the losses or the training loop.
- **Launch kit: NO-GO until two small fixes are in.** Both are about the VM billing or failing at launch. Neither affects audio quality.

## P1 launch traps

### P1-1. Any failure before step 5,000 leaves a VM billing with nothing running (`vm_push.sh:13-14`)

`vm_push.sh` only writes DONE when `push $R/last.pt && push $R/train.log && touch $W/DONE` all succeed. g7 writes its first `last.pt` at step 5,000 (`--save_every 5000`). These failures all write `TRAIN_EXIT` with no `last.pt` on disk:
- the predmels step fails (rc≠0);
- an import or bundle error;
- the WavLM weight download fails (`bundle.get_model()` runs at startup);
- an out-of-memory crash or NaN before step 5k.

In each case `hf upload` fails, DONE is never written, and the pusher exits anyway: it does not retry. `keepalive.py` then holds the kernel BUSY until DONE appears, and `colab_check.sh` only releases the VM on DONE. Its CU-floor guard writes STOP, but no trainer is left to read it. The result is a G4 that bills until the balance runs out. The `TRAIN_EXIT` fix in `vm_run_g7.sh` is correct, but this second gate defeats it.

Fix (safe for the gʷerh runs, which share this pusher): retry the uploads, then write DONE regardless of whether they succeeded.
```bash
if [ -f $W/TRAIN_EXIT ]; then
  sleep 5; for f in $R/step*.pt; do case " $seen " in *" $f "*) ;; *) push "$f";; esac; done
  cp $W/train.out $R/train.out 2>/dev/null || true          # predmels / startup tracebacks live here, not in train.log
  for f in last.pt train.log train.out; do [ -f $R/$f ] || continue
    for i in 1 2 3; do push $R/$f && break; sleep 30; done; done
  touch $W/DONE; echo "DONE exit=$(cat $W/TRAIN_EXIT)"; exit 0
fi
```

### P1-2. Nothing builds or uploads `g7_bundle.tgz`, and the launcher has no pre-flight check (`vm_run_g7.sh:10, 43, 52`)

No file in the repo references `g7_bundle.tgz` except `vm_run_g7.sh` itself. `colab_train.sh g7_hnm` will not do it either: it packs the gʷerh files and `runs.sh` exits 2 with "unknown run". The VM script depends implicitly on all of these:
- `code/{gwerh_hnm_dual.py, gwerh_hnm_dual_train.py, gwerh.py, audio.py}`
- `pietts/{predmels_pietts.py, model.py}`
- `tv/tiny_voca/`
- `BigVGAN/` (for `env`, `discriminators`, `loss`)
- `pylib/` (for nnAudio, which CQTD needs)
- `kit/vm_push.sh`
- `/content/w/v4_hc_12k.pt` and `/content/w/pietts_meta.pt`

The carbon audit's fix (fetch `data/pietts_meta.pt` and `ckpt/pietts_v4_hc/step12000.pt` from HF, plus an import check before `nohup`) was not applied.

Fix:
1. Add a `colab_train_g7.sh` modelled on `colab_train.sh`. It should:
   - build the bundle with the layout above;
   - start `keepalive.py` with `colab exec`;
   - upload the bundle and the HF token;
   - run `vm_run_g7.sh`;
   - keep the `trap ... colab stop` ERR guard.
2. In `vm_run_g7.sh`, before the `nohup`, run this check. Under `set -e` a failure returns nonzero to the host, and the host trap then releases the VM:
```bash
for f in v4_hc_12k.pt pietts_meta.pt code/gwerh_hnm_dual_train.py pietts/predmels_pietts.py pietts/model.py \
         kit/vm_push.sh tv/tiny_voca/config.py BigVGAN/discriminators.py pylib/nnAudio; do
  [ -e "$W/$f" ] || { echo "MISSING $W/$f"; exit 4; }; done
python -c "import sys; sys.path[:0]=['$W/pietts','$W/BigVGAN']; import gwerh_hnm_dual, gwerh, discriminators, loss, nnAudio, tiny_voca.config, model, torchaudio; torchaudio.pipelines.WAVLM_BASE_PLUS.get_model()"
```
The last call also downloads the WavLM weights (~360 MB) up front, so a failed download shows up here rather than as a background crash.

## Checked and correct (no action)

**Alignment and reconstruction**
- **7× alignment:** 252/63 gives 7T frames. The `h_cond` linear-interp centres land at 63j+31 against STFT centres at 63j+32.
- **Excitation and FIR frame centres** both sit at 441t+221, matching the 1764/441 STFT pad of 661.
- **LTV-FIR overlap-add (OLA):** T+4 frames; full 4× Hann coverage holds over all of `[pad_l, pad_l+L)`, the periodic Hann sums to exactly 2, and the ×0.5 is correct. The 4096-point linear convolution is at least 1764+1323−1.
- **Minimum phase:** folding the 1764-point cepstrum and zero-padding it to 3528 reproduces `L_tot` exactly on the even bins. Clamping to [−12, 6] keeps `exp` bounded.

**Excitation**
- **Dirichlet / BLIT:** the closed form and its φ→0 limit (K) are right. It is computed in fp64. Its gradient never reaches f0, so `torch.where` cannot produce a NaN there.
- **Breathiness noise:** the normalisation √(1−m+0.375m²) is exact.

**Stage 2**
- **Baseband demodulation and remodulation by (−i)^{km}:** the algebra checks out. `k·m` stays exact in fp32 for clips under about 190 s.
- **Initial state:** M=0, `dS_equiv`=0 and the burst head is 0, so Stage 2 is an identity at init and the handoff at step 2k is smooth.

**Prosody and predmels**
- **`clean_paid_pros`** is deterministic and runs on CPU in both places (`torch.median`, `np.interp`), so the P0-2 guard `max_diff < 1e-3` will pass.
- **predpros** saves `hp`, which equals the cleaned prosody when `--teacher_pros 1` is set.
- **Units:** `continuous_pitch` uses the same log(F0/200) units, so teacher prosody fed to the CFM is in the scale the TTS was trained on.

**Discriminators and losses**
- **API matches BigVGAN:** the `mel_spectrogram` override signature, `discriminator_loss[0]`, `generator_loss[0]`, the `feature_loss` scalar, and the CQTD config keys from `G.H` (`sampling_rate` = 44100).
- **WavLM path, run here on CPU:** `feature_extractor` → `encoder.extract_features(num_layers=6)` works with gradients, and the input gradient is finite.
- **cMBSD:** 15 outputs and 90 feature maps, matching the 0.2×/0.1× normalisation.
- **bf16 / fp32 split:** `_spec_feats` stays in fp32 under autocast. CQTD runs outside autocast in both the D and G steps.

**Training loop and VM script**
- **Warmup:** Stage-2 parameters have `grad=None` during warmup, and AdamW skips them. EMA buffers are copied.
- **Exit codes:** `--max_steps` and resume cannot trigger a false `exit 3` on a fresh run.
- **Quoting and `set -e`:** the `'"$RUN"'` quoting is correct, and the inner `bash -c` does not inherit `set -e`.
- **Import resolution on the VM:**
  - `gwerh_hnm_dual` resolves from `$W/code` via `PYTHONPATH`.
  - `audio` resolves to `code/audio.py`. The `wokws/` path that predmels inserts does not exist on the VM, which is harmless.
  - `model` resolves to `pietts/model.py`; there is no `model.py` in `code/`.
  - `pylib` holds only `alias_free_torch`, `nnAudio` and `phaseaug`, so no module names collide.

## Measured, not a bug

`rel_energy` is relative to the maximum over the 128-frame crop in training, but over the whole utterance at inference. I measured the gap on 60 paid clips × 5 crops: a mean of 0.31 nats, with 0.7% of frames off by more than 1 nat. That is negligible; leave it.

## P2 notes (optional, not blocking)

- **Validation slowdown:** `cudnn.benchmark=True` re-tunes the convolutions for every validation clip length. Each val pass costs a few extra minutes; it does not affect correctness.
- **Voicing input differs slightly from TTS training:** with `--teacher_pros 1` the CFM gets the cleaned uv (`vk & active_lo`), whereas in training it got `max(pv, vk)`. On voiced-kind frames with low energy (voiced-stop closures), the harmonic comb is now off. The vocoder sees the same uv, so the pair stays consistent. Expect predmels for those closures to be slightly less voiced.
- **Unseeded random in `GlobalGlottalFiLM`:** the sub-pool window uses the unseeded global `random`, so this part is not reproducible across resumes. Harmless.
