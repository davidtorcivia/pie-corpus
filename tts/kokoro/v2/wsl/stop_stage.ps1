# Ask a running Kokoro v2 stage to stop: it sees the STOP file at the next step, saves last.pth and exits 0.
#   stop_stage.ps1 -Name stage1        (-Kill: hard stop of the WSL trainers, loses the steps since the last save)
param([string]$Name = "stage1", [switch]$Kill)
if ($Kill) { wsl -d Ubuntu-26.04 -- pkill -f "python train_(first|second).py"; "killed" }
else { New-Item -ItemType File -Force "Q:\AI\PIE\runs\kokoro-v2\$Name\STOP" | Out-Null; "STOP requested for $Name" }
