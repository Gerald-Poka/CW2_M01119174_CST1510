# setup_ai_monitor_scheduler.ps1
# Registers a Windows Task Scheduler task that runs the headless AI monitor
# every 5 minutes using the project virtual environment.
#
# Usage (run from the project root):
#   powershell -ExecutionPolicy Bypass -File .\setup_ai_monitor_scheduler.ps1

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $ProjectDir ".venv\Scripts\pythonw.exe"
$Script = Join-Path $ProjectDir "ai_monitor.py"
$TaskName = "CyberOps_AIMonitor"

if (-not (Test-Path $Python)) {
    Write-Error "pythonw.exe not found at $Python. Create the virtual env first (.venv)."
    exit 1
}

if (-not (Test-Path $Script)) {
    Write-Error "ai_monitor.py not found at $Script."
    exit 1
}

$action = "`"$Python`" `"$Script`""

# Run every 1 minute, indefinitely, for the current user.
schtasks /Create /TN $TaskName /SC MINUTE /MO 1 /TR $action /F

if ($LASTEXITCODE -eq 0) {
    Write-Host "Scheduled task '$TaskName' created. It runs ai_monitor.py every 1 minute."
    Write-Host "Python : $Python"
    Write-Host "Script : $Script"
} else {
    Write-Error "Failed to create the scheduled task."
    exit 1
}
