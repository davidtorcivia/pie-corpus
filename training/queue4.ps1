# Queue 4 (2026-11-01): the recipe (Qwen3-4B-Instruct, r16, lr 2e-4) on the export with waves 4-6 (t089-t109,
# conversation toward 20%); 2 epochs (the queue-3 recipe) and 3 epochs (does the larger set want more?). Scored on
# the frozen prompts (gen_prompts_v1) against baseline_v1 and queue 3.
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"; $R = "Q:\AI\PIE\runs"; $log = "$R\queue.log"
Add-Content $log "$(Get-Date -Format s) queue 4 start"
foreach ($ep in 2, 3) {
    $name = "qwen4b-instruct-r16-lr2e-4-export1101-e$ep"
    Add-Content $log "$(Get-Date -Format s) start $name"
    & $py Q:\AI\PIE\train\train_lora.py --run $name --model "$M\Qwen3-4B-Instruct-2507-cdbee75f" --template chatml --liger qwen3 --lr 2e-4 --epochs $ep --gen-file Q:\AI\PIE\data\gen_prompts_v1.jsonl --train Q:\AI\PIE\data\train_mix_1101.jsonl --eval Q:\AI\PIE\data\eval_1101.jsonl *> "$R\$name.log"
    Add-Content $log "$(Get-Date -Format s) end $name exit=$LASTEXITCODE"
}
Add-Content $log "$(Get-Date -Format s) queue 4 finished"
