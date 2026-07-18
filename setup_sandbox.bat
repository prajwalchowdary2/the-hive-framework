@echo off
echo ==========================================
echo [*] THE HIVE - SANDBOX LAUNCHER [*]
echo ==========================================

REM Check if Vagrant is installed
where vagrant >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Vagrant is not installed!
    echo Please download and install Vagrant from: https://developer.hashicorp.com/vagrant/downloads
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

REM Ensure VirtualBox is in the PATH (default installation directory)
set "PATH=%PATH%;C:\Program Files\Oracle\VirtualBox"

REM Check if VirtualBox is installed
where VBoxManage >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] VirtualBox is not installed or not in PATH!
    echo Please download and install VirtualBox from: https://www.virtualbox.org/wiki/Downloads
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo [*] Initializing Windows 10 Virtual Machine Sandbox...
echo [*] This will take a few minutes if it is the first boot.
echo.

vagrant up

echo.
echo ==========================================
echo [*] SANDBOX IS RUNNING [*]
echo ==========================================
echo To connect to the sandbox, open VirtualBox to view the GUI,
echo or run 'vagrant ssh' to connect via terminal.
echo.
echo Inside the sandbox, your code is mounted at: C:\TheHive
echo.
echo When you are finished, run 'vagrant destroy' to delete the VM.
echo ==========================================
pause
