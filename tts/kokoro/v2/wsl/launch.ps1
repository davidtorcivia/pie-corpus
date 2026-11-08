# Start a WSL stage (or the benchmark scripts) as a scheduled task: survives ssh and logoff.
#   launch.ps1 -Task PIE-kokoro-v2-stage1 -Cmd "run_stage.sh 1 v2l_stage1"
param([string]$Task, [string]$Cmd)
$a = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-d Ubuntu-26.04 -- bash -lc `"/mnt/q/AI/PIE/train/kokoro/wsl/$Cmd`""
$s = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $Task -Action $a -Settings $s -RunLevel Highest -Force | Out-Null
Start-ScheduledTask -TaskName $Task; "started ${Task}: $Cmd"
