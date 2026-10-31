# Queue 3 (2026-10-31): the recipe (Qwen3-4B-Instruct, r16, lr 2e-4, 2 epochs) on the export with every grammar
# drill, the stem-class drills and t044-t088; scored on the frozen prompts (gen_prompts_v1) against baseline_v1.
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"; $R = "Q:\AI\PIE\runs"; $log = "$R\queue.log"
$name = "qwen4b-instruct-r16-lr2e-4-export1031"
Add-Content $log "$(Get-Date -Format s) queue 3 start $name"
& $py Q:\AI\PIE\train\train_lora.py --run $name --model "$M\Qwen3-4B-Instruct-2507-cdbee75f" --template chatml --liger qwen3 --lr 2e-4 --epochs 2 --gen-file Q:\AI\PIE\data\gen_prompts_v1.jsonl --train Q:\AI\PIE\data\train_mix_1031.jsonl --eval Q:\AI\PIE\data\eval_1031.jsonl *> "$R\$name.log"
Add-Content $log "$(Get-Date -Format s) end $name exit=$LASTEXITCODE"
Add-Content $log "$(Get-Date -Format s) queue 3 finished"
