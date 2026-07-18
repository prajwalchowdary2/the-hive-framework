# 🐝 The Hive

**Multi-Agent AI Adversary Emulation Pipeline**

Feed a threat intelligence report → get automated adversary emulation + Sigma detection rules + coverage scorecard.

## Quick Start

```bash
# 1. Setup (one-time)
setup.bat          # Windows (Dell workstation)
# or
bash setup.sh      # Linux/Mac

# 2. Run against APT29
python run.py --report data/threat_reports/apt29.json

# 3. Run in simulation mode (no real atomic execution)
python run.py --report data/threat_reports/apt29.json --simulate

# 4. List available threat reports
python run.py --list-reports
```

## Architecture

```
Threat Report → [Intel Agent] → [Planner Agent] → [Operator Fleet] → [Purple Agent] → Detection Rules
                    ↓                  ↓               ↓                    ↓
              Extract TTPs      Build Plan      Execute Kill Chain    Generate Sigma/YARA
              Map to ATT&CK     Sequence         Recon → Access →     Coverage Scorecard
                                Dependencies     Persist → Move →     Gap Analysis
                                                 Exfil                D3FEND Mapping
```

## Agents

| Agent | Role | Output |
|-------|------|--------|
| Intel Agent | Parse threat reports, extract TTPs | Structured TTP JSON |
| Planner Agent | Build sequenced emulation plan | Kill chain playbook |
| Recon Agent | Network discovery | Target profile |
| Access Agent | Initial access simulation | Foothold details |
| Persist Agent | Persistence mechanisms | Persistence inventory |
| Movement Agent | Lateral movement | Movement path map |
| Exfil Agent | Data exfiltration simulation | Exfil summary |
| Purple Agent | Detection engineering | Sigma/YARA rules + scorecard |

## Output

Each run creates a timestamped folder in `output/` containing:
- `report.md` — Full emulation report
- `attck_navigator.json` — Import into ATT&CK Navigator for heatmap
- `sigma_rules/` — Detection rules for each technique
- `yara_rules/` — YARA rules for tool indicators
- `raw_results.json` — Complete pipeline data

## Tech Stack

- **Python 3.10+** — Core language
- **Ollama + Llama 3.1 70B** — Local LLM (runs on GPU)
- **CrewAI** — Agent orchestration
- **Atomic Red Team** — Real technique execution
- **MITRE ATT&CK** — Technique database
- **Sigma** — Detection rule format
- **Docker** — Ollama container with GPU passthrough

## Requirements

- Python 3.10+
- Docker (for Ollama)
- NVIDIA GPU with 32GB+ VRAM (for llama3.1:70b)
- Windows 11 (for full Atomic Red Team execution)

## License

For educational and authorized security testing purposes only.
