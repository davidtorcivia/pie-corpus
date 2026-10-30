#!/bin/zsh
# Mirror tr-desktop's run outputs to the Mac, score new generations with the PIE tools, push the scores back so the
# dashboard shows them. Loops every 5 minutes until the queue log says "queue finished".
M=/Users/david/AI/pie-runs
cd /Users/david/AI/PIE
while true; do
  for f in $(ssh tr-desktop 'Get-ChildItem Q:\AI\PIE\runs\*\generations-e*.jsonl | ForEach-Object { $_.Directory.Name + "/" + $_.Name }' 2>/dev/null | tr -d '\r'); do
    d=${f%/*}; mkdir -p $M/$d
    s=${f/generations-/scores-}; s=${s%.jsonl}.json
    if [ ! -f $M/$s ]; then
      scp -q "tr-desktop:Q:/AI/PIE/runs/$f" $M/$f && \
      UV_CACHE_DIR=/tmp/pie-uv-cache uv run --quiet python -I training/score_generations.py $M/$f && \
      scp -q $M/$s "tr-desktop:Q:/AI/PIE/runs/$s"
    fi
  done
  for d in $(ssh tr-desktop 'Get-ChildItem Q:\AI\PIE\runs -Directory | ForEach-Object Name' 2>/dev/null | tr -d '\r'); do
    mkdir -p $M/$d; scp -q "tr-desktop:Q:/AI/PIE/runs/$d/metrics.jsonl" "tr-desktop:Q:/AI/PIE/runs/$d/config.json" $M/$d/ 2>/dev/null
  done
  ssh tr-desktop 'Get-Content Q:\AI\PIE\runs\queue.log -Tail 1' 2>/dev/null | grep -q "queue finished" && break
  sleep 300
done
echo sync done
