# Stop the training queue and any training process started from Q:\AI\PIE (leaves the dashboard running).
Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like "*queue.ps1*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "Q:\AI\PIE\*" -and $_.CommandLine -notlike "*dashboard*" } | Stop-Process -Force
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*train_lora.py*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
"stopped"
