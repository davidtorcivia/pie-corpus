# Queue 5 (2026-10-31): the queue 4 recipe and export (train_mix_1101), run for 5 epochs. Queue 4 was still improving
# at e3 (chrF 51.0) while eval loss rose from e1, so this tests how far more epochs carry. Adapters and frozen-prompt
# generations are saved after every epoch. The cosine schedule spans 5 epochs, so e3 here is not queue 4 e3.
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"; $R = "Q:\AI\PIE\runs"; $log = "$R\queue.log"
$name = "qwen4b-instruct-r16-lr2e-4-export1101-5ep"
Add-Content $log "$(Get-Date -Format s) queue 5 start $name"
& $py Q:\AI\PIE\train\train_lora.py --run $name --model "$M\Qwen3-4B-Instruct-2507-cdbee75f" --template chatml --liger qwen3 --lr 2e-4 --epochs 5 --gen-file Q:\AI\PIE\data\gen_prompts_v1.jsonl --train Q:\AI\PIE\data\train_mix_1101.jsonl --eval Q:\AI\PIE\data\eval_1101.jsonl *> "$R\$name.log"
Add-Content $log "$(Get-Date -Format s) end $name exit=$LASTEXITCODE"
Add-Content $log "$(Get-Date -Format s) queue 5 finished"
