#!/usr/bin/env bash
# ============================================
#  The Hive - Setup Script (Linux/Mac)
# ============================================
set -e

echo ""
echo " ============================================"
echo "  THE HIVE - Setup"
echo "  Multi-Agent Adversary Emulation Pipeline"
echo " ============================================"
echo ""

# -- Create virtual environment --
if [ ! -d "venv" ]; then
    echo "[1/5] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[1/5] Virtual environment already exists."
fi

source venv/bin/activate

# -- Install dependencies --
echo "[2/5] Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# -- Download ATT&CK data --
echo "[3/5] Downloading MITRE ATT&CK data..."
mkdir -p data/attck_data
if [ ! -f "data/attck_data/enterprise-attack.json" ]; then
    curl -sL -o data/attck_data/enterprise-attack.json \
        "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    echo "    Downloaded enterprise-attack.json"
else
    echo "    ATT&CK data already exists."
fi

# -- Download Atomic Red Team --
echo "[4/5] Downloading Atomic Red Team tests..."
if [ ! -d "data/atomics" ]; then
    python -c "from atomic_operator import AtomicOperator; ao = AtomicOperator(); ao.get_atomics(save_path='data')" 2>/dev/null || \
        echo "    [WARN] atomic-operator download failed. Clone manually: git clone https://github.com/redcanaryco/atomic-red-team.git data/atomic-red-team"
else
    echo "    Atomics already downloaded."
fi

# -- Create output dirs --
mkdir -p output/sigma_rules output/yara_rules

# -- Start Ollama --
echo "[5/5] Starting Ollama (Docker + GPU)..."
docker compose up -d 2>/dev/null || echo "    [WARN] Docker failed. Install Ollama natively: https://ollama.com"

echo ""
echo "Pulling llama3.1:70b model..."
docker exec hive-ollama ollama pull llama3.1:70b 2>/dev/null || ollama pull llama3.1:70b 2>/dev/null || true

echo ""
echo " ============================================"
echo "  Setup complete!"
echo "  Run: python run.py --report data/threat_reports/apt29.json"
echo " ============================================"
