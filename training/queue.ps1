# The training queue on tr-desktop: runs one after another on the 5090. Stop everything with training/stop.ps1.
$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"
$log = "Q:\AI\PIE\runs\queue.log"
$runs = @(
  @("qwen4b-instruct-r16-lr2e-4", "--model", "$M\Qwen3-4B-Instruct-2507-cdbee75f", "--template", "chatml", "--liger", "qwen3", "--lr", "2e-4", "--epochs", "3"),
  @("qwen4b-base-r16-lr2e-4", "--model", "$M\Qwen3-4B-Base-906bfd4b", "--template", "chatml", "--liger", "qwen3", "--lr", "2e-4", "--epochs", "3"),
  @("typewriter-sft-r16-lr1e-4", "--model", "$M\typewriter-1913-7B-sft-v2-3fd609e0", "--template", "typewriter", "--liger", "llama", "--lr", "1e-4", "--epochs", "3", "--batch", "2", "--accum", "4"),
  @("typewriter-base-r16-lr1e-4", "--model", "$M\typewriter-1913-7B-base-v2-5a5ec1c0", "--template", "typewriter", "--liger", "llama", "--lr", "1e-4", "--epochs", "3", "--batch", "2", "--accum", "4")
)
foreach ($r in $runs) {
  $name = $r[0]
  if (Test-Path "Q:\AI\PIE\runs\$name\metrics.jsonl") { if ((Get-Content "Q:\AI\PIE\runs\$name\metrics.jsonl" -Tail 1) -match '"done"') { continue } }
  Add-Content $log "$(Get-Date -Format s) start $name"
  & $py Q:\AI\PIE\train\train_lora.py --run $name $r[1..($r.Length-1)] *> "Q:\AI\PIE\runs\$name.log"
  Add-Content $log "$(Get-Date -Format s) end $name exit=$LASTEXITCODE"
}
Add-Content $log "$(Get-Date -Format s) queue finished"
