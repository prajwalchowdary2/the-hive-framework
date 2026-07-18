@echo off
echo ========================================================
echo [*] THE HIVE - SANDBOX EMULATION RUNNER [*]
echo ========================================================
echo.

:: Ensure we are running inside the VM
if not exist "C:\TheHive" (
    echo [ERROR] This script must be run INSIDE the Virtual Machine sandbox!
    echo Could not find C:\TheHive directory.
    pause
    exit /b 1
)

:: Find Python executable
set "PYTHON_EXE=python"
where python >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\Python311\python.exe" (
        set "PYTHON_EXE=C:\Program Files\Python311\python.exe"
    ) else if exist "C:\Program Files (x86)\Python311\python.exe" (
        set "PYTHON_EXE=C:\Program Files (x86)\Python311\python.exe"
    ) else (
        echo [ERROR] Python was not found in PATH or standard installation directory!
        echo Please ensure Python is installed inside the VM.
        pause
        exit /b 1
    )
)

:: Step 1: Create a VM-local virtual environment if it doesn't exist
if not exist "C:\hive_venv" (
    echo [*] Creating VM-local Python virtual environment...
    "%PYTHON_EXE%" -m venv C:\hive_venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Step 2: Install/verify dependencies
echo [*] Checking dependencies inside VM-local virtual environment...
C:\hive_venv\Scripts\pip install -r C:\TheHive\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: Step 3: Prepare VM-local atomic red team directory to isolate downloads from host synced folders
if not exist "C:\atomic-red-team" (
    echo [*] Copying Atomic Red Team data to VM-local drive C:\atomic-red-team...
    powershell -Command "Copy-Item -Path 'C:\TheHive\data\atomic-red-team' -Destination 'C:\' -Recurse -Force -ErrorAction SilentlyContinue"
)

:: Step 4: Run the adversary emulation pipeline
echo [*] Launching adversary emulation pipeline...
cd C:\TheHive
C:\hive_venv\Scripts\python.exe run.py --config config/settings_vm.yaml --report data\threat_reports\apt29.json

echo.
echo ========================================================
echo Emulation run completed!
echo The report and results have been saved to C:\TheHive\output\
echo ========================================================
pause
