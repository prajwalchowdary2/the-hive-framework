# -*- mode: ruby -*-
# vi: set ft=ruby :

# The Hive - Execution Sandbox
# This Vagrantfile builds a disposable Windows VM for safe adversary emulation.

Vagrant.configure("2") do |config|
  # Increase the boot timeout because Windows takes longer to initialize WinRM
  config.vm.boot_timeout = 600

  # We use a standard Windows Server 2019 Box which has excellent VirtualBox support
  # Note: The first boot will take some time to download the image.
  config.vm.box = "StefanScherer/windows_2019"

  config.vm.provider "virtualbox" do |vb|
    vb.gui = true # We want to see the UI to watch the AI work
    vb.memory = "16384" # 16 GB RAM for lightning-fast performance
    vb.cpus = 8         # 8 cores to harness your i9 Ultra power
    vb.name = "The_Hive_Sandbox"

    # Optimizations for Windows 11 hosts with Hyper-V/VBS enabled:
    vb.customize ["modifyvm", :id, "--paravirtprovider", "hyperv"]
    vb.customize ["modifyvm", :id, "--hwvirtex", "on"]
  end

  # Mount the current project folder directly into the VM at C:\TheHive as READ-ONLY
  # This prevents downloaded atomic payloads inside the VM from writing back to the host and triggering host Defender alerts.
  config.vm.synced_folder ".", "/TheHive", readonly: true

  # Forward the honeypot port just in case you want to test the UI locally
  config.vm.network "forwarded_port", guest: 8080, host: 8080, auto_correct: true

  # Provisioning script: Runs automatically on first boot
  config.vm.provision "shell", inline: <<-SHELL
    Write-Host "=========================================="
    Write-Host "[*] INITIALIZING THE HIVE SANDBOX VM [*]"
    Write-Host "=========================================="
    
    # 1. Disable Windows Defender completely inside guest VM
    Write-Host "[*] Disabling Windows Defender inside Guest VM..."
    Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
    Set-MpPreference -DisableIOAVProtection $true -ErrorAction SilentlyContinue
    Set-MpPreference -DisableScriptScanning $true -ErrorAction SilentlyContinue
    Set-MpPreference -EnableControlledFolderAccess Disabled -ErrorAction SilentlyContinue
    Set-MpPreference -MAPSReporting Disable -ErrorAction SilentlyContinue
    Set-MpPreference -SubmitSamplesConsent NeverSend -ErrorAction SilentlyContinue

    # 2. Copy files to a VM-local writable location
    Write-Host "[*] Copying project files to C:\\local_hive..."
    New-Item -ItemType Directory -Force -Path "C:\\local_hive" | Out-Null
    Get-ChildItem -Path "C:\\TheHive" | Where-Object { $_.Name -notin @('.vagrant', 'venv', '.git', '__pycache__', 'output') } | Copy-Item -Destination "C:\\local_hive" -Recurse -Force -ErrorAction SilentlyContinue

    # 3. Retrieve and install Python 3.11
    if (Test-Path "C:\\TheHive\\python-3.11.5-amd64.exe") {
        Write-Host "[*] Found Python installer on host. Copying locally..."
        Copy-Item "C:\\TheHive\\python-3.11.5-amd64.exe" -Destination "C:\\python-installer.exe" -Force
    } else {
        Write-Host "[*] Downloading Python 3.11..."
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe" -OutFile "C:\\python-installer.exe"
    }
    
    Write-Host "[*] Installing Python 3.11 Silently..."
    Start-Process -FilePath "C:\\python-installer.exe" -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0 AssociateFiles=0 Shortcuts=0 Include_doc=0 Include_launcher=0 InstallLauncherAllUsers=0" -Wait
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    # Locate Python
    $pythonExe = "python"
    if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
        $userPython = "C:\\Users\\vagrant\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
        if (Test-Path $userPython) {
            $pythonExe = $userPython
        }
    }

    # 4. Setup local environment
    Write-Host "[*] Setting up local Python venv..."
    & $pythonExe -m venv C:\\hive_venv
    & C:\\hive_venv\\Scripts\\pip install --quiet -r C:\\local_hive\\requirements.txt

    # 5. Create desktop launcher inside guest VM
    Write-Host "[*] Creating Desktop Live Emulation Launcher..."
    $desktopPath = "C:\\Users\\vagrant\\Desktop"
    if (Test-Path $desktopPath) {
        $launcherContent = @"
@echo off
title The Hive - Automated Live Emulation Run
echo ========================================================
echo   THE HIVE - AUTOMATED LIVE ADVERSARY EMULATION RUN
echo ========================================================
echo.
powershell.exe -NoExit -ExecutionPolicy Bypass -File C:\\local_hive\\setup_sandbox_windows.ps1
"@
        $launcherContent | Out-File -FilePath "$desktopPath\\run_live.bat" -Force
        Write-Host "  [+] run_live.bat shortcut created on guest VM desktop! ✅" -ForegroundColor Green
    }

    Write-Host "=========================================="
    Write-Host "[*] VM SANDBOX READY [*]"
    Write-Host "Double-click 'run_live.bat' on the VM desktop to run the live emulation!"
    Write-Host "=========================================="
  SHELL
end
