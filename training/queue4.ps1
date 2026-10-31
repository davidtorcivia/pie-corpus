# Queue 4 (2026-11-01): the recipe (Qwen3-4B-Instruct, r16, lr 2e-4) on the export with waves 4-6 (t089-t109,
# conversation toward 20%). One 3-epoch run: train_lora.py saves adapters and frozen-prompt generations after every
# epoch, so e2 compares with baseline_v1 (queue 1's 3-epoch run at e2) and e3 tests whether the larger set wants
# more. (A 3-epoch cosine run's e2 is at a higher LR than queue 3's 2-epoch end.) Scored on gen_prompts_v1.
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"; $R = "Q:\AI\PIE\runs"; $log = "$R\queue.log"
$name = "qwen4b-instruct-r16-lr2e-4-export1101"
Add-Content $log "$(Get-Date -Format s) queue 4 start $name"
& $py Q:\AI\PIE\train\train_lora.py --run $name --model "$M\Qwen3-4B-Instruct-2507-cdbee75f" --template chatml --liger qwen3 --lr 2e-4 --epochs 3 --gen-file Q:\AI\PIE\data\gen_prompts_v1.jsonl --train Q:\AI\PIE\data\train_mix_1101.jsonl --eval Q:\AI\PIE\data\eval_1101.jsonl *> "$R\$name.log"
Add-Content $log "$(Get-Date -Format s) end $name exit=$LASTEXITCODE"
Add-Content $log "$(Get-Date -Format s) queue 4 finished"
