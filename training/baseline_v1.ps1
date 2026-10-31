# After queue 2: every queue-1/2 adapter's answers to the frozen prompt set (training/gen_prompts_v1.jsonl), the
# baseline the next export's runs are compared against.
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"; $R = "Q:\AI\PIE\runs"; $log = "$R\queue.log"
while (-not ((Get-Content $log -Tail 1) -match "queue 2 finished")) { Start-Sleep 60 }
Add-Content $log "$(Get-Date -Format s) baseline v1 start"
$jobs = @(
  @("qwen4b-instruct-r16-lr2e-4", "$M\Qwen3-4B-Instruct-2507-cdbee75f", "chatml", "2"),
  @("qwen4b-instruct-r32-lr2e-4", "$M\Qwen3-4B-Instruct-2507-cdbee75f", "chatml", "2"),
  @("qwen4b-instruct-r16-lr1e-4", "$M\Qwen3-4B-Instruct-2507-cdbee75f", "chatml", "2"),
  @("qwen4b-base-plain-r16-lr2e-4", "$M\Qwen3-4B-Base-906bfd4b", "plain", "1"),
  @("typewriter-sft-r16-lr1e-4", "$M\typewriter-1913-7B-sft-v2-3fd609e0", "typewriter", "1")
)
Set-Location Q:\AI\PIE\train
foreach ($j in $jobs) {
  & $py gen_eval.py --model $j[1] --adapter "$R\$($j[0])\adapter-e$($j[3])" --template $j[2] --out "$R\$($j[0])\generations-v1e$($j[3]).jsonl" *> "$R\$($j[0])-v1.log"
  Add-Content $log "$(Get-Date -Format s) baseline $($j[0]) exit=$LASTEXITCODE"
}
Add-Content $log "$(Get-Date -Format s) baseline v1 finished"
