@echo off
REM ============================================
REM  The Hive - Setup Script (Windows)
REM  Target: Dell Pro Max Tower / RTX 5090
REM ============================================

echo.
echo  ============================================
echo   THE HIVE - Setup
echo   Multi-Agent Adversary Emulation Pipeline
echo  ============================================
echo.

REM -- Check Python --
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ from python.org
    exit /b 1
)

REM -- Create virtual environment --
if not exist "venv" (
    echo [1/5] Creating virtual environment...
    python -m venv venv
) else (
    echo [1/5] Virtual environment already exists.
)

REM -- Activate venv --
call venv\Scripts\activate.bat

REM -- Install dependencies --
echo [2/5] Installing Python dependencies...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

REM -- Download ATT^&CK data --
echo [3/5] Downloading MITRE ATT^&CK data...
if not exist "data\attck_data" mkdir data\attck_data
if not exist "data\attck_data\enterprise-attack.json" (
    curl -L -o data\attck_data\enterprise-attack.json ^
        "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    echo     Downloaded enterprise-attack.json
) else (
    echo     ATT^&CK data already exists.
)

REM -- Download Atomic Red Team atomics --
echo [4/5] Downloading Atomic Red Team tests...
if not exist "data\atomics" (
    python -c "from atomic_operator import AtomicOperator; ao = AtomicOperator(); ao.get_atomics(save_path='data')" 2>nul
    if %errorlevel% neq 0 (
        echo     [WARN] atomic-operator download failed. You can manually clone:
        echo     git clone https://github.com/redcanaryco/atomic-red-team.git data/atomic-red-team
    )
) else (
    echo     Atomics already downloaded.
)

REM -- Create output directory --
if not exist "output" mkdir output
if not exist "output\sigma_rules" mkdir output\sigma_rules
if not exist "output\yara_rules" mkdir output\yara_rules

REM -- Start Ollama via Docker --
echo [5/5] Starting Ollama (Docker + GPU)...
docker compose up -d 2>nul
if %errorlevel% neq 0 (
    echo     [WARN] Docker Compose failed. Make sure Docker Desktop is running.
    echo     You can also install Ollama natively: https://ollama.com/download
)

REM -- Pull the LLM model --
echo.
echo Pulling llama3.1:70b model (this takes a while on first run)...
docker exec hive-ollama ollama pull llama3.1:70b 2>nul
if %errorlevel% neq 0 (
    echo     [INFO] Trying native ollama...
    ollama pull llama3.1:70b 2>nul
)

REM -- Run Smoke Test --
echo [6/6] Verifying pipeline setup...
python test_smoke.py

echo.
echo  ============================================
echo   Setup complete!
echo   Run: python run.py --report data\threat_reports\apt29.json
echo  ============================================
