# Setup Windows Task Scheduler for Daily Microstash Book Drop
param (
    [string]$Time = "08:00AM"
)

$TaskName = "MicrostashDailyBookDrop"
$WorkingDir = "C:\LLM\deepstash_microlearning"
$ScriptPath = "scripts\add_daily_book.py"

Write-Host "Configuring Windows Task Scheduler for $TaskName..." -ForegroundColor Cyan

try {
    $Action = New-ScheduledTaskAction -Execute "python.exe" -Argument $ScriptPath -WorkingDirectory $WorkingDir
    $Trigger = New-ScheduledTaskTrigger -Daily -At $Time
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Automatically adds 1 new seminal book to Microstash daily" -Force
    Write-Host "[SUCCESS] Task '$TaskName' registered! It will run daily at $Time." -ForegroundColor Green
    Write-Host "To test now, run: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Yellow
} catch {
    Write-Host "[ERROR] Failed to register task: $_" -ForegroundColor Red
}
