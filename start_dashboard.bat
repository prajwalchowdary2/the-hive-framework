@echo off
title The Hive Dashboard Launcher
echo ========================================================
echo Starting The Hive Dashboard (HONEYPOT MODE ACTIVE)...
echo ========================================================
echo.
echo The dashboard will be available at http://localhost:8080/dashboard.html
echo NOTE: Honeypot is armed. Any attempt to download Sigma rules will trigger an alarm.
echo.

:: Start the python web server in a new minimized window with a specific title so we can kill it later
start "TheHiveDashboardProcess" /MIN python src/honeypot_server.py

:: Give the server a couple of seconds to boot up
timeout /t 2 /nobreak > nul

:: Automatically open the default web browser to the dashboard
echo Opening dashboard in your web browser...
start http://localhost:8080/dashboard.html

echo.
echo [SUCCESS] Dashboard is live! You can close this window.
timeout /t 3 > nul
