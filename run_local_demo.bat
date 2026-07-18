@echo off
title The Hive - Automated Emulation Local Demo
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [*] Requesting Administrator privileges to run the automated demo...
    powershell -Command "Start-Process -FilePath '%~dpnx0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
echo ========================================================
echo   THE HIVE - AUTOMATED ADVERSARY EMULATION PIPELINE
echo ========================================================
echo.
echo [*] Launching automated local setup and audits...
powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0setup_sandbox_windows.ps1"
