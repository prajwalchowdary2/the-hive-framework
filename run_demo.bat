@echo off
title The Hive - Automated Emulation Demo
echo ========================================================
echo   THE HIVE - AUTOMATED ADVERSARY EMULATION PIPELINE
echo ========================================================
echo.
echo [*] Launching guest provisioning and audits...
powershell.exe -NoExit -ExecutionPolicy Bypass -File C:\TheHive\setup_sandbox_windows.ps1
