@echo off
title The Hive Dashboard - STOP
echo ===================================================
echo [THE HIVE] Stopping Dashboard Server
echo ===================================================

:: Kill the python process associated with our specific window title
taskkill /FI "WINDOWTITLE eq TheHiveDashboardProcess" /F /T > nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Dashboard server stopped successfully!
) else (
    echo [INFO] Dashboard server was not running.
)

echo.
echo Press any key to exit...
pause > nul
