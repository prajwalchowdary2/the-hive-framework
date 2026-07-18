param(
    [switch]$NoPause
)

# The Hive - System Security Reset Tool
# =====================================
# Use this script to restore the guest VM to a SECURE status.

# Force console output to UTF-8 to support emojis
$OutputEncoding = [System.Text.Encoding]::UTF8
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

Clear-Host
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "             SYSTEM SECURITY RESET TOOL                 " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Enable Windows Defender Real-time Protection
Write-Host "[*] Enabling Windows Defender Real-time Protection..." -ForegroundColor White
try {
    Set-MpPreference -DisableRealtimeMonitoring $false -ErrorAction Stop
    Write-Host "  [+] Real-time Protection enabled successfully. ✅" -ForegroundColor Green
} catch {
    Write-Host "  [-] Failed to enable Real-time Protection: $_" -ForegroundColor Red
}
Write-Host ""

# 2. Clean up Startup Registry Keys
Write-Host "[*] Cleaning up suspicious registry persistence keys..." -ForegroundColor White
$hkcuRunPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$hklmRunPath = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"

function Remove-SuspiciousKeys($path) {
    if (Test-Path $path) {
        $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue
        if ($props -ne $null) {
            $names = $props.psobject.properties.name | Where-Object { $_ -notin 'PSPath', 'PSParentPath', 'PSChildName', 'PSDrive', 'PSProvider', 'PSObject' }
            foreach ($name in $names) {
                if ($name -match "Atomic" -or $name -match "Hive" -or $props.$name -match "temp" -or $props.$name -match "malicious") {
                    Remove-ItemProperty -Path $path -Name $name -Force -ErrorAction SilentlyContinue
                    Write-Host "  [+] Removed registry key: $path\$name 🗑️" -ForegroundColor Green
                }
            }
        }
    }
}

Remove-SuspiciousKeys $hkcuRunPath
Remove-SuspiciousKeys $hklmRunPath
Write-Host "  [+] Startup registry keys audited and cleaned. ✅" -ForegroundColor Green
Write-Host ""

# 3. Clean up Scheduled Tasks
Write-Host "[*] Cleaning up backdoor scheduled tasks..." -ForegroundColor White
$tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { 
    $_.TaskName -like "*Atomic*" -or 
    $_.TaskName -like "*Hive*" -or 
    $_.TaskName -like "*Backdoor*" 
}

if ($tasks -ne $null -and $tasks.Count -gt 0) {
    foreach ($task in $tasks) {
        Unregister-ScheduledTask -TaskName $task.TaskName -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "  [+] Removed Scheduled Task: $($task.TaskName) 🗑️" -ForegroundColor Green
    }
} else {
    Write-Host "  [+] No malicious scheduled tasks found. ✅" -ForegroundColor Green
}
Write-Host ""

# 4. Record the reset timestamp to filter out historical event log clearances
Write-Host "[*] Recording reset timestamp..." -ForegroundColor White
$now = Get-Date
# Write timestamp in ISO-8601 format
$now.ToString("yyyy-MM-ddTHH:mm:ss") | Out-File -FilePath "$PSScriptRoot\last_reset.txt" -Force
Write-Host "  [+] System reset timestamp recorded: $($now.ToString()) ✅" -ForegroundColor Green
Write-Host ""

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "          SYSTEM RESET COMPLETE - RUN AUDIT NOW!        " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
if (-not $NoPause) {
    pause
}
