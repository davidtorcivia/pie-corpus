# Run any script in this folder as a scheduled task (survives ssh)
param([string]$Task, [string]$Script)
$a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File Q:\AI\PIE\train\kokoro\win\$Script"
$s = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $Task -Action $a -Settings $s -RunLevel Highest -Force | Out-Null
Start-ScheduledTask -TaskName $Task; "started $Task"
