# The Hive - Windows Sandbox Provisioning Script
# ===============================================
# This script is executed automatically inside Windows Sandbox to set up Python,
# dependencies, and the emulation environment.

$OutputEncoding = [System.Text.Encoding]::UTF8
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     PROVISIONING THE HIVE WINDOWS SANDBOX  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Determine source path and copy project to local writable folder
$sourcePath = "C:\TheHive"
if (-not (Test-Path $sourcePath)) {
    $sourcePath = $PSScriptRoot
}

Write-Host "[*] Isolating project files to local storage (C:\local_hive) from $sourcePath..." -ForegroundColor White
New-Item -ItemType Directory -Force -Path "C:\local_hive" | Out-Null
Get-ChildItem -Path $sourcePath | Where-Object { $_.Name -notin @('.vagrant', 'venv', '.git', '__pycache__', 'output') } | Copy-Item -Destination "C:\local_hive" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  [+] Copy complete. ✅" -ForegroundColor Green
Write-Host ""

# 2. Disable guest Windows Defender inside Sandbox/VM
Write-Host "[*] Configuring Windows Defender..." -ForegroundColor White
try {
    Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
    Set-MpPreference -DisableIOAVProtection $true -ErrorAction SilentlyContinue
    Write-Host "  [+] Real-time monitoring disabled. ✅" -ForegroundColor Green
} catch {
    Write-Host "  [-] Failed to disable realtime monitoring (may already be managed by policy). ⚠️" -ForegroundColor Yellow
}
Write-Host ""

# 3. Get and install Python 3.11
if (Test-Path "$sourcePath\python-3.11.5-amd64.exe") {
    Write-Host "[*] Found Python installer locally. Copying..." -ForegroundColor White
    Copy-Item "$sourcePath\python-3.11.5-amd64.exe" -Destination "C:\python-installer.exe" -Force
    Write-Host "  [+] Copied Python installer successfully. ✅" -ForegroundColor Green
} else {
    Write-Host "[*] Downloading Python 3.11.5..." -ForegroundColor White
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    try {
        $oldProgress = $ProgressPreference
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe" -OutFile "C:\python-installer.exe"
        $ProgressPreference = $oldProgress
        Write-Host "  [+] Download complete. ✅" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Failed to download Python: $_" -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host "[*] Installing Python 3.11.5 silently (disabling launcher and shortcuts to prevent hangs)..." -ForegroundColor White
$installProc = Start-Process -FilePath "C:\python-installer.exe" -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 AssociateFiles=0 Shortcuts=0 Include_doc=0 Include_launcher=0 InstallLauncherAllUsers=0" -PassThru
$installProc | Wait-Process -Timeout 60 -ErrorAction SilentlyContinue

if (-not $installProc.HasExited) {
    Write-Host "  [-] Installer timed out. Terminating installer process..." -ForegroundColor Yellow
    $installProc | Stop-Process -Force
}

# Verify if python was successfully installed
$pythonPath = "$env:USERPROFILE\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path $pythonPath)) {
    # Check if python is in PATH anyway
    if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
        Write-Host "  [ERROR] Python installation failed or was not found." -ForegroundColor Red
        pause
        exit 1
    }
}
Write-Host "  [+] Python installer execution finished. ✅" -ForegroundColor Green
Write-Host ""

# Refresh Path environment variable
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# 4. Prepare local atomic directory
Write-Host "[*] Deploying Atomic Red Team files to local disk (C:\atomic-red-team)..." -ForegroundColor White
New-Item -ItemType Directory -Force -Path "C:\atomic-red-team" | Out-Null
Copy-Item -Path "C:\local_hive\data\atomic-red-team" -Destination "C:\" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  [+] Atomic definitions deployed. ✅" -ForegroundColor Green
Write-Host ""

# 5. Build virtual environment and install requirements
Write-Host "[*] Creating virtual environment C:\hive_venv..." -ForegroundColor White

$pythonExe = "python"
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    # Check default AppData location for current user install
    $userPython = "$env:USERPROFILE\AppData\Local\Programs\Python\Python311\python.exe"
    if (Test-Path $userPython) {
        $pythonExe = $userPython
    } else {
        # Fallback search in User Programs folder
        $search = Get-ChildItem -Path "$env:USERPROFILE\AppData\Local\Programs\Python" -Filter "python.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($search) {
            $pythonExe = $search.FullName
        }
    }
}

& $pythonExe -m venv C:\hive_venv
Write-Host "[*] Installing Python dependencies (this may take a minute)..." -ForegroundColor White
& C:\hive_venv\Scripts\pip install --quiet -r C:\local_hive\requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Dependency installation failed." -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  [+] Environment initialized and dependencies installed. ✅" -ForegroundColor Green
Write-Host ""

# 6. Run Automated Live Emulation Flow
Write-Host "[*] Establishing baseline audit timestamp..." -ForegroundColor White
$now = Get-Date
$now.ToString("yyyy-MM-ddTHH:mm:ss") | Out-File -FilePath "C:\local_hive\last_reset.txt" -Force

Write-Host "=============================================" -ForegroundColor Green
Write-Host "     GUEST SANDBOX SETUP COMPLETE            " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Starting the automated live adversary emulation pipeline..." -ForegroundColor Cyan
Write-Host ""

# Step A: Run Baseline Audit (expect SECURE)
Write-Host "--------------------------------------------------------" -ForegroundColor DarkCyan
Write-Host "[LIVE RUN 1/3] Running Baseline Security Audit (SECURE)" -ForegroundColor DarkCyan
Write-Host "--------------------------------------------------------" -ForegroundColor DarkCyan
Start-Sleep -Seconds 1
& "C:\local_hive\audit_system.ps1" -NoPause

# Step B: Run the Emulation Pipeline
Write-Host ""
Write-Host "--------------------------------------------------------" -ForegroundColor DarkCyan
Write-Host "[LIVE RUN 2/3] Running Multi-Agent AI Adversary Emulation" -ForegroundColor DarkCyan
Write-Host "--------------------------------------------------------" -ForegroundColor DarkCyan
Write-Host "Executing APT29 playbook via Python pipeline in local guest directory..." -ForegroundColor White
Start-Sleep -Seconds 2

Push-Location "C:\local_hive"
try {
    & "C:\hive_venv\Scripts\python.exe" run.py --config config/settings_vm.yaml --report data/threat_reports/apt29.json
} catch {
    Write-Host "[ERROR] Emulation pipeline encountered an error: $_" -ForegroundColor Red
}
Pop-Location

# Step C: Run Post-Emulation Audit (expect COMPROMISED)
Write-Host ""
Write-Host "--------------------------------------------------------" -ForegroundColor DarkCyan
Write-Host "[LIVE RUN 3/3] Running Post-Emulation Security Audit (COMPROMISED)" -ForegroundColor DarkCyan
Write-Host "--------------------------------------------------------" -ForegroundColor DarkCyan
Start-Sleep -Seconds 2
& "C:\local_hive\audit_system.ps1" -NoPause

# Show Completion Summary
Write-Host "=============================================" -ForegroundColor Green
Write-Host "     AUTOMATED EMULATION RUN COMPLETE!       " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Review the audit logs above to compare the SECURE vs COMPROMISED system states." -ForegroundColor White
Write-Host ""
Write-Host "Manual control options:" -ForegroundColor White
Write-Host " - To Reset and run again: C:\local_hive\reset_system.ps1" -ForegroundColor Yellow
Write-Host " - To Audit status again:  C:\local_hive\audit_system.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "This guest console remains active for your inspection." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
