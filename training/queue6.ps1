# Queue 6 (2026-10-31): the queue 5 recipe (Qwen3-4B-Instruct, r16, lr 2e-4, 5 epochs) on export e2b6d78
# (train_mix_1102: the ablaut drills and the round-6 lexicon), so e5 vs queue 5 e5 tests the drills. Generation
# cap 384 tokens instead of 160: 50 of 84 paradigm answers are longer than 160, and queue 5 e5 never generated
# 25% of the paradigm cells. Then the v2 drill prompts on every epoch, and v1 and v2 at 384 on the baselines
# (queue 5 e5, queue 4 e3), so all are scored on the same prompts and cap.
$env:PYTHONIOENCODING = "utf-8"
$py = "Q:\AI\PIE\train\.venv\Scripts\python.exe"
$M = "Q:\AI\PIE\models"; $R = "Q:\AI\PIE\runs"; $D = "Q:\AI\PIE\data"; $log = "$R\queue.log"
$model = "$M\Qwen3-4B-Instruct-2507-cdbee75f"
$name = "qwen4b-instruct-r16-lr2e-4-export1102-5ep"
Add-Content $log "$(Get-Date -Format s) queue 6 start $name"
& $py Q:\AI\PIE\train\train_lora.py --run $name --model $model --template chatml --liger qwen3 --lr 2e-4 --epochs 5 --max-new 384 --gen-file $D\gen_prompts_v1.jsonl --train $D\train_mix_1102.jsonl --eval $D\eval_1102.jsonl *> "$R\$name.log"
Add-Content $log "$(Get-Date -Format s) end $name exit=$LASTEXITCODE"
foreach ($e in 1..5) {
  & $py Q:\AI\PIE\train\gen_eval.py --model $model --adapter "$R\$name\adapter-e$e" --template chatml --max-new 384 --prompts $D\gen_prompts_drills_v2.jsonl --out "$R\$name\generations-drills_v2-e$e.jsonl" *>> "$R\$name-gen.log"
}
foreach ($b in @("qwen4b-instruct-r16-lr2e-4-export1101-5ep\adapter-e5", "qwen4b-instruct-r16-lr2e-4-export1101\adapter-e3")) {
  $run, $ad = $b.Split("\")
  foreach ($p in @("v1", "drills_v2")) {
    $f = if ($p -eq "v1") { "$D\gen_prompts_v1.jsonl" } else { "$D\gen_prompts_drills_v2.jsonl" }
    & $py Q:\AI\PIE\train\gen_eval.py --model $model --adapter "$R\$b" --template chatml --max-new 384 --prompts $f --out "$R\$run\generations-$p-384-$ad.jsonl" *>> "$R\$name-gen.log"
  }
}
Add-Content $log "$(Get-Date -Format s) gen_eval done exit=$LASTEXITCODE"
Add-Content $log "$(Get-Date -Format s) queue 6 finished"
