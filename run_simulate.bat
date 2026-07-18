@echo off
REM ============================================
REM  The Hive - SIMULATION Mode
REM  No real atomic execution (safe to run anywhere)
REM ============================================

echo.
echo  ============================================
echo   THE HIVE - SIMULATION MODE
echo   No real attacks will be executed
echo  ============================================
echo.

call venv\Scripts\activate.bat

echo Select a threat report:
echo   [1] APT29    (Russia)
echo   [2] FIN7     (Eastern Europe)
echo   [3] Lazarus  (North Korea)
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" set report=data\threat_reports\apt29.json
if "%choice%"=="2" set report=data\threat_reports\fin7.json
if "%choice%"=="3" set report=data\threat_reports\lazarus.json

if not defined report (
    echo [ERROR] Invalid choice. Please enter 1, 2, or 3.
    pause
    exit /b 1
)

echo.
echo Running simulation against: %report%
echo.
python run.py --report %report% --simulate

echo.
pause
