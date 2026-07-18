@echo off
title The Hive Desktop Application Launcher
echo ========================================================
echo Starting The Hive Desktop Native App...
echo ========================================================
echo.
echo NOTE: Honeypot trap is active in the background.
echo.

:: We launch the script using the virtual environment python so it can find pywebview
venv\Scripts\python.exe src\desktop_app.py
