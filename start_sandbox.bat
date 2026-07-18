@echo off
title The Hive Windows Sandbox Launcher

:: Step 1: Check for Admin permissions and elevate automatically
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Requesting Administrator privileges to verify and enable Windows Sandbox...
    powershell -Command "Start-Process -FilePath '%~dpnx0' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

echo ========================================================
echo [*] THE HIVE - WINDOWS SANDBOX AUTOMATED LAUNCHER [*]
echo ========================================================
echo.

:: Step 2: Check if Windows Sandbox is enabled
powershell -Command "if ((Get-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM -ErrorAction SilentlyContinue).State -ne 'Enabled') { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Windows Sandbox is NOT enabled. Enabling it now...
    dism.exe /online /enable-feature /featurename:Containers-DisposableClientVM /all /norestart
    set "DISM_RES=%errorlevel%"
    if "%DISM_RES%"=="0" (
        goto :dismsuccess
    )
    if "%DISM_RES%"=="3010" (
        goto :dismsuccess
    )
    echo [ERROR] Failed to enable Windows Sandbox automatically.
    echo Please ensure you are running a Windows Pro, Enterprise, or Education edition.
    pause
    exit /b 1

    :dismsuccess
    echo.
    echo ========================================================
    echo [+] Windows Sandbox has been enabled successfully!
    echo [!] IMPORTANT: You MUST restart your computer to apply changes.
    echo ========================================================
    echo.
    pause
    exit /b 0
)

:: Step 3: Launch Windows Sandbox
echo [*] Windows Sandbox is active. Booting sandbox environment...
start "" "%~dp0the_hive_sandbox.wsb"
echo.
echo [+] Sandbox booted!
echo Please wait for the provisioning PowerShell console inside the Sandbox to complete.
echo.
timeout /t 5 > nul
exit /b 0
