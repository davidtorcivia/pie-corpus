# Start a stage as a scheduled task (survives ssh/logoff); no trigger, so it only runs when started here.
param([string]$Task = "PIE-kokoro-v2", [int]$Stage = 1, [string]$Config = "v2w_smoke1", [string]$Env = "")
$arg = "-NoProfile -ExecutionPolicy Bypass -File Q:\AI\PIE\train\kokoro\win\run_stage.ps1 -Stage $Stage -Config $Config"
if ($Env) { $arg += " -Env `"$Env`"" }
$a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
$s = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $Task -Action $a -Settings $s -RunLevel Highest -Force | Out-Null
Start-ScheduledTask -TaskName $Task
"started ${Task}: stage $Stage $Config [$Env]"
