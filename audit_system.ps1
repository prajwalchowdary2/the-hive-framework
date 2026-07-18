param(
    [switch]$NoPause
)

# The Hive - System Security Auditor
# ==================================
# Use this script to demonstrate the difference between a Clean PC and a Compromised PC.

# Force console output to UTF-8 to support emojis
$OutputEncoding = [System.Text.Encoding]::UTF8
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

Clear-Host
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "             SYSTEM SECURITY AUDIT TOOL                 " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$compromised = $false
$checks = @()

# 1. Check Windows Defender Status
Write-Host "[*] Auditing Windows Defender status..." -ForegroundColor White
try {
    $pref = Get-MpPreference -ErrorAction SilentlyContinue
    if ($pref -eq $null -or $pref.DisableRealtimeMonitoring -eq $true) {
        Write-Host "  [ALERT] Real-time Protection is DISABLED! ❌" -ForegroundColor Red
        $compromised = $true
        $checks += "Defender Disabled"
    } else {
        Write-Host "  [SAFE] Real-time Protection is Active. ✅" -ForegroundColor Green
    }
} catch {
    Write-Host "  [ALERT] Unable to query Defender status (possibly disabled/blocked). ❌" -ForegroundColor Red
    $compromised = $true
}
Write-Host ""

# 2. Check Registry Persistence Run Keys
Write-Host "[*] Auditing Startup Registry keys (HKCU/HKLM Run keys)..." -ForegroundColor White
$suspiciousKeys = @()

$hkcuRun = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
if ($hkcuRun -ne $null) {
    $props = $hkcuRun.psobject.properties.name | Where-Object { $_ -notin 'PSPath', 'PSParentPath', 'PSChildName', 'PSDrive', 'PSProvider', 'PSObject' }
    foreach ($propName in $props) {
        if ($propName -match "Atomic" -or $propName -match "Hive" -or $hkcuRun.$propName -match "temp" -or $hkcuRun.$propName -match "malicious") {
            $suspiciousKeys += "HKCU:\...\Run\$propName -> $($hkcuRun.$propName)"
        }
    }
}

$hklmRun = Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue
if ($hklmRun -ne $null) {
    $props = $hklmRun.psobject.properties.name | Where-Object { $_ -notin 'PSPath', 'PSParentPath', 'PSChildName', 'PSDrive', 'PSProvider', 'PSObject' }
    foreach ($propName in $props) {
        if ($propName -match "Atomic" -or $propName -match "Hive" -or $hklmRun.$propName -match "temp" -or $hklmRun.$propName -match "malicious") {
            $suspiciousKeys += "HKLM:\...\Run\$propName -> $($hklmRun.$propName)"
        }
    }
}

if ($suspiciousKeys.Count -gt 0) {
    foreach ($key in $suspiciousKeys) {
        Write-Host "  [ALERT] Suspicious startup key detected: $key ❌" -ForegroundColor Red
    }
    $compromised = $true
    $checks += "Suspicious Registry Startup Keys"
} else {
    Write-Host "  [SAFE] No suspicious startup registry keys found. ✅" -ForegroundColor Green
}
Write-Host ""

# 3. Check Scheduled Tasks
Write-Host "[*] Auditing Scheduled Tasks for backdoor execution..." -ForegroundColor White
$tasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object { 
    $_.TaskName -like "*Atomic*" -or 
    $_.TaskName -like "*Hive*" -or 
    $_.TaskName -like "*Backdoor*" 
}

if ($tasks -ne $null -and $tasks.Count -gt 0) {
    foreach ($task in $tasks) {
        Write-Host "  [ALERT] Backdoor Scheduled Task detected: $($task.TaskName) (Path: $($task.TaskPath)) ❌" -ForegroundColor Red
    }
    $compromised = $true
    $checks += "Backdoor Scheduled Tasks"
} else {
    Write-Host "  [SAFE] No malicious scheduled tasks detected. ✅" -ForegroundColor Green
}
Write-Host ""

# 4. Check Event Log Clearance
Write-Host "[*] Auditing Event Logs for indicator clearance..." -ForegroundColor White
$cleared = $false
$startTime = $null
if (Test-Path "$PSScriptRoot\last_reset.txt") {
    $resetTimeStr = Get-Content "$PSScriptRoot\last_reset.txt" -ErrorAction SilentlyContinue
    if ($resetTimeStr -match '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}') {
        try {
            $startTime = [DateTime]::Parse($resetTimeStr)
        } catch {}
    }
}

if ($startTime -eq $null) {
    # Default fallback: check last 30 minutes
    $startTime = (Get-Date).AddMinutes(-30)
}

try {
    $clearedEvents = Get-WinEvent -FilterHashtable @{LogName='Security';ID=1102;StartTime=$startTime} -MaxEvents 5 -ErrorAction SilentlyContinue
    if ($clearedEvents -ne $null -and $clearedEvents.Count -gt 0) {
        $cleared = $true
    }
} catch {}

try {
    $systemCleared = Get-WinEvent -FilterHashtable @{LogName='System';ID=104;StartTime=$startTime} -MaxEvents 5 -ErrorAction SilentlyContinue
    if ($systemCleared -ne $null -and $systemCleared.Count -gt 0) {
        $cleared = $true
    }
} catch {}

if ($cleared) {
    Write-Host "  [ALERT] Event Log clearance was detected! (ID 1102 / 104) ❌" -ForegroundColor Red
    $compromised = $true
    $checks += "Log Clearance Detected"
} else {
    Write-Host "  [SAFE] Event log integrity is intact. ✅" -ForegroundColor Green
}
Write-Host ""

# Final Status Output
Write-Host "========================================================" -ForegroundColor Cyan
if ($compromised) {
    Write-Host "          SYSTEM STATUS: COMPROMISED [💀]" -ForegroundColor Red -BackgroundColor Black
    Write-Host "  Indicators of Compromise (IOCs) Found:" -ForegroundColor Yellow
    foreach ($c in $checks) {
        Write-Host "  - $c" -ForegroundColor Yellow
    }
} else {
    Write-Host "            SYSTEM STATUS: SECURE [✅]" -ForegroundColor Green -BackgroundColor Black
    Write-Host "  No indicators of compromise detected. Host configuration is intact." -ForegroundColor White
}
Write-Host "========================================================" -ForegroundColor Cyan
if (-not $NoPause) {
    pause
}
