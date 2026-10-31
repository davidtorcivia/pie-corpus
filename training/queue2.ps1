# Queue 2 (2026-10-30): base models on the plain format, then two Qwen-instruct variants; 2 epochs each (queue 1:
# eval loss bottoms at epoch 2). Waits for queue 1 to finish first.
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"
$log = "Q:\AI\PIE\runs\queue.log"
while (-not ((Get-Content $log -Tail 1) -match "queue finished")) { Start-Sleep 60 }
Remove-Item -Recurse -Force "Q:\AI\PIE\runs\typewriter-base-r16-lr1e-4" -ErrorAction SilentlyContinue
Add-Content $log "$(Get-Date -Format s) queue 2 start"
$runs = @(
  @("typewriter-base-plain-r16-lr1e-4", "--model", "$M\typewriter-1913-7B-base-v2-5a5ec1c0", "--template", "plain", "--liger", "llama", "--lr", "1e-4", "--epochs", "2", "--batch", "2", "--accum", "4"),
  @("qwen4b-base-plain-r16-lr2e-4", "--model", "$M\Qwen3-4B-Base-906bfd4b", "--template", "plain", "--liger", "qwen3", "--lr", "2e-4", "--epochs", "2"),
  @("qwen4b-instruct-r16-lr1e-4", "--model", "$M\Qwen3-4B-Instruct-2507-cdbee75f", "--template", "chatml", "--liger", "qwen3", "--lr", "1e-4", "--epochs", "2"),
  @("qwen4b-instruct-r32-lr2e-4", "--model", "$M\Qwen3-4B-Instruct-2507-cdbee75f", "--template", "chatml", "--liger", "qwen3", "--lr", "2e-4", "--epochs", "2", "--rank", "32", "--alpha", "64")
)
foreach ($r in $runs) {
  $name = $r[0]
  if (Test-Path "Q:\AI\PIE\runs\$name\metrics.jsonl") { if ((Get-Content "Q:\AI\PIE\runs\$name\metrics.jsonl" -Tail 1) -match '"done"') { continue } }
  Add-Content $log "$(Get-Date -Format s) start $name"
  & $py Q:\AI\PIE\train\train_lora.py --run $name $r[1..($r.Length-1)] *> "Q:\AI\PIE\runs\$name.log"
  Add-Content $log "$(Get-Date -Format s) end $name exit=$LASTEXITCODE"
}
Add-Content $log "$(Get-Date -Format s) queue 2 finished"
