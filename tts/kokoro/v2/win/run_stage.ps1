# Launch one Kokoro v2 training stage natively on Windows (tr-desktop). Resumes from <log_dir>\last.pth when present.
#   powershell -File run_stage.ps1 -Stage 1 -Config v2w_stage1 [-Env "PIE_COMPILE=decoder;PIE_TF32=1"]
# Stop it gracefully with stop_stage.ps1 (it saves last.pth first). Output: Q:\AI\PIE\runs\kokoro-v2\<name>\console.log
param([int]$Stage = 1, [string]$Config = "v2w_smoke1", [string]$Env = "", [string]$LogDir = "")
$K = "Q:\AI\PIE\train\kokoro"
$py = "Q:\AI\PIE\train\kokoro-env\Scripts\python.exe"
$env:PYTHONUTF8 = "1"; $env:PYTHONIOENCODING = "utf-8"; $env:PYTHONUNBUFFERED = "1"
$env:HF_HOME = "Q:\AI\PIE\.hf"
$env:TORCHINDUCTOR_CACHE_DIR = "Q:\AI\PIE\.inductor-cache"; $env:TRITON_CACHE_DIR = "Q:\AI\PIE\.triton-cache"
$env:PIE_GPU_MEM_FRAC = "0.80"; $env:PIE_TF32 = "1"
foreach ($kv in ($Env -split ";" | Where-Object { $_ -match "=" })) { $ename, $evalue = $kv -split "=", 2; Set-Item "env:$ename" $evalue }
$cfg = "$K\configs\$Config.yml"
$log_dir = if ($LogDir) { $LogDir } else { (Select-String -Path $cfg -Pattern "^log_dir: (.+)$").Matches[0].Groups[1].Value.Trim() }
New-Item -ItemType Directory -Force $log_dir | Out-Null
$con = Join-Path $log_dir "console.log"
$script = if ($Stage -eq 1) { "train_first.py" } else { "train_second.py" }
Set-Location "$K\StyleTTS2"
# PowerShell 5 redirection writes UTF-16, so the trainer's output goes through a .cmd wrapper (UTF-8 log)
$bat = Join-Path $log_dir "run.cmd"
Set-Content -Path $bat -Encoding ASCII -Value @(
  "@echo off",
  "cd /d `"$K\StyleTTS2`"",
  "echo %DATE% %TIME% START stage $Stage $Config env=[$Env] >> `"$con`"",
  "`"$py`" $script -p `"$cfg`" >> `"$con`" 2>&1",
  "echo %DATE% %TIME% EXIT %ERRORLEVEL% >> `"$con`"")
& cmd.exe /c `"$bat`"
