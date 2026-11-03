# Launch the Nemotron 3.5 Super Tinker run (remote; no GPU on tr-desktop) and log to Q:\AI\PIE\tinker\runs.
$env:PYTHONIOENCODING = "utf-8"
$run = "nemotron35-super-dimuon-r16-export1103"
New-Item -ItemType Directory -Force "Q:\AI\PIE\tinker\runs" | Out-Null
Add-Content Q:\AI\PIE\runs\queue.log "$(Get-Date -Format s) tinker start $run"
$env:PIE_RUN = $run
& Q:\AI\PIE\tinker\.venv\Scripts\python.exe -u Q:\AI\PIE\tinker\train_nemotron.py *> "Q:\AI\PIE\tinker\runs\$run.console.log"
Add-Content Q:\AI\PIE\runs\queue.log "$(Get-Date -Format s) tinker end $run exit=$LASTEXITCODE"
