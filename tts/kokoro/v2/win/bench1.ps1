# Stage 1 speed benchmark: each variant trains PIE_MAX_STEPS steps on the real train list from kokoro_base, fresh.
$V = @(
  @{n="b4-eager";        e="PIE_BATCH=4;PIE_MAX_STEPS=80"},
  @{n="b4-compile";      e="PIE_BATCH=4;PIE_MAX_STEPS=80;PIE_COMPILE=decoder,text_encoder,style_encoder"},
  @{n="b4-compile-all";  e="PIE_BATCH=4;PIE_MAX_STEPS=80;PIE_COMPILE=decoder,text_encoder,style_encoder,text_aligner,pitch_extractor,mpd,msd"},
  @{n="b8-compile";      e="PIE_BATCH=8;PIE_MAX_STEPS=50;PIE_COMPILE=decoder,text_encoder,style_encoder"},
  @{n="b8-compile-bf16"; e="PIE_BATCH=8;PIE_MAX_STEPS=50;PIE_COMPILE=decoder,text_encoder,style_encoder;ACCELERATE_MIXED_PRECISION=bf16"},
  @{n="b4-eager-bf16";   e="PIE_BATCH=4;PIE_MAX_STEPS=80;ACCELERATE_MIXED_PRECISION=bf16"}
)
foreach ($v in $V) {
  $env = "PIE_FRESH=1;PIE_BENCH=1;PIE_EPOCHS=1;PIE_LOG_DIR=Q:/AI/PIE/runs/kokoro-v2/bench1/$($v.n);" + $v.e
  & powershell -NoProfile -ExecutionPolicy Bypass -File Q:\AI\PIE\train\kokoro\win\run_stage.ps1 -Stage 1 -Config v2w_stage1 -Env $env -LogDir "Q:/AI/PIE/runs/kokoro-v2/bench1/$($v.n)"
}
New-Item -ItemType File -Force Q:\AI\PIE\runs\kokoro-v2\bench1\DONE | Out-Null
