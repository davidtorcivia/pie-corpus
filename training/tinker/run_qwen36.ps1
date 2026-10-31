# Launch the Qwen3.6-35B-A3B Tinker run (remote; no GPU on tr-desktop) and log to Q:\AI\PIE\tinker\runs.
$env:PYTHONIOENCODING = "utf-8"
$run = "qwen36-35b-a3b-r16-lr2e-4-export1102"
New-Item -ItemType Directory -Force "Q:\AI\PIE\tinker\runs" | Out-Null
Add-Content Q:\AI\PIE\runs\queue.log "$(Get-Date -Format s) tinker start $run"
& Q:\AI\PIE\tinker\.venv\Scripts\python.exe -u Q:\AI\PIE\tinker\train_qwen36.py *> "Q:\AI\PIE\tinker\runs\$run.console.log"
Add-Content Q:\AI\PIE\runs\queue.log "$(Get-Date -Format s) tinker end $run exit=$LASTEXITCODE"
