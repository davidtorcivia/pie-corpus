# LR sweep for the Nemotron 3.5 Super run: four 150-step probes in parallel (Tinker is remote; nothing local on the GPU),
# each on the full run's 3-epoch cosine schedule, so a probe sees the LR the full run would at those steps.
# Compare test NLL / bpb at steps 50, 100, 150 in each run's metrics.jsonl. About 1.9 M tokens each: ~$2.50 per probe.
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\tinker\.venv\Scripts\python.exe"
New-Item -ItemType Directory -Force "Q:\AI\PIE\tinker\runs" | Out-Null
$probes = @(@("dimuon", "1e-3"), @("dimuon", "2e-3"), @("dimuon", "4e-3"), @("adamw", "2e-4"))
$procs = foreach ($p in $probes) {
    $run = "nemotron35-sweep-$($p[0])-lr$($p[1])"
    Add-Content Q:\AI\PIE\runs\queue.log "$(Get-Date -Format s) tinker start $run"
    $env:PIE_OPT = $p[0]; $env:PIE_LR = $p[1]; $env:PIE_RANK = "16"; $env:PIE_MAX_STEPS = "150"; $env:PIE_RUN = $run
    Start-Process -PassThru -NoNewWindow -FilePath $py -ArgumentList "-u", "Q:\AI\PIE\tinker\train_nemotron.py" `
        -RedirectStandardOutput "Q:\AI\PIE\tinker\runs\$run.console.log" -RedirectStandardError "Q:\AI\PIE\tinker\runs\$run.err.log"
    Start-Sleep 20
}
$procs | Wait-Process
foreach ($p in $procs) { Add-Content Q:\AI\PIE\runs\queue.log "$(Get-Date -Format s) tinker sweep process $($p.Id) exit=$($p.ExitCode)" }
