@echo off
REM ============================================
REM  The Hive - LIVE Mode
REM  Real Atomic Red Team execution (ADMIN REQUIRED)
REM ============================================
cd /d "%~dp0"

echo.

:: Safety check: Prevent execution inside the VM synced folder
if "%USERNAME%"=="vagrant" (
    echo ========================================================
    echo [ERROR] Do not run this host script inside the VM!
    echo.
    echo Please run the 'run_live.bat' shortcut located directly
    echo on the guest VM Desktop.
    echo ========================================================
    echo.
    pause
    exit /b 1
)

echo  ============================================
echo   THE HIVE - LIVE MODE
echo   WARNING: Real attacks WILL be executed!
echo  ============================================
echo.

REM -- Check for admin privileges --
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] This script must be run as Administrator!
    echo         Right-click and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with Administrator privileges.
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
echo  ============================================
echo   WARNING: You are about to run LIVE attacks
echo   Report: %report%
echo   This will execute real techniques on this machine.
echo  ============================================
echo.
set /p confirm="Type YES to continue: "

if /i not "%confirm%"=="YES" (
    echo Aborted. No attacks were executed.
    pause
    exit /b 0
)

echo.
echo Running LIVE against: %report%
echo.
python run.py --report %report%

echo.
pause
