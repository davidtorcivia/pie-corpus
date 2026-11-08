# Ask a running Kokoro v2 stage to stop: it sees the STOP file at the next step, saves last.pth and exits 0.
#   powershell -File stop_stage.ps1 -Name stage1      (-Kill: hard stop, loses the steps since the last save)
param([string]$Name = "stage1", [switch]$Kill)
$d = "Q:\AI\PIE\runs\kokoro-v2\$Name"
if ($Kill) {
  Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*train_first.py*" -or $_.CommandLine -like "*train_second.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
  "killed"
} else { New-Item -ItemType File -Force "$d\STOP" | Out-Null; "STOP requested for $d" }
