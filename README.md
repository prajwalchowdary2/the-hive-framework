# 🐝 The Hive

> **Autonomous Multi-Agent AI Adversary Emulation & Detection Engineering Pipeline**

Feed a raw Cyber Threat Intelligence (CTI) report → get automated adversary emulation, hybrid safety guardrails, production Sigma & YARA detection rules, ATT&CK Navigator heatmaps, and dynamic active defense decoys.

---

## 🚀 Quick Start

```bash
# 1. Setup Environment (One-time setup)
setup.bat          # Windows
# or
bash setup.sh      # Linux / macOS

# 2. Run Smoke Tests (Verify offline pipeline logic)
python test_smoke.py

# 3. List Available Threat Reports
python run.py --list-reports

# 4. Run Adversary Emulation (Simulation Mode - Laptop / Lightweight)
python run.py --report data/threat_reports/apt29.json --simulate --model llama3.1:8b

# 5. Run Live Adversary Emulation + Launch Web Dashboard
python run.py --report data/threat_reports/apt29.json --ui
```

---

## 🏗️ Multi-Agent Architecture

```
Threat Intelligence Report (JSON / Text)
                   │
                   ▼
          [ 🔍 Intel Agent ] ──────► Extracts & validates T-codes against MITRE ATT&CK
                   │
                   ▼
         [ 📋 Planner Agent ] ─────► Sequences kill chain dependencies (Access → Movement → Exfil)
                   │
                   ▼
          [ ⚖️ Critic Agent ] ──────► Hybrid Guardrail: Deterministic STIX check + Zero-temp safety
                   │
                   ▼
        [ ⚔️ Operator Fleet ] ─────► Executes / Simulates Atomic Red Team tests
    (Recon, Access, Persist, Move, Exfil)
                   │
                   ▼
        [ 🟣 Purple Team Agent ] ──► Assesses log coverage, synthesizes Sigma & YARA rules
                   │
                   ▼
        [ 🕸️ Deception Agent ] ───► Deploys dynamic honeypots for identified detection gaps
                   │
                   ▼
         [ 💡 Explain Agent ] ─────► Produces executive incident narrative & remediation plan
```

---

## 🤖 Agent Fleet Breakdown

| Agent | Icon | Role | Key Output Artifacts |
| :--- | :---: | :--- | :--- |
| **Intel Agent** | 🔍 | Parses CTI reports, maps TTPs | Structured TTP JSON & STIX T-code mapping |
| **Planner Agent** | 📋 | Builds sequenced kill chain playbooks | Ordered kill chain execution plan |
| **Critic Agent** | ⚖️ | Safety & hallucination guardrail | Validated execution plan (blocks unknown T-codes / destructive commands) |
| **Recon Agent** | 🔭 | Network & AD discovery | Target profile & high-value asset list |
| **Access Agent** | 🚪 | Initial access simulation | Foothold inventory |
| **Persist Agent** | 🔒 | Persistence mechanisms | Registry run keys / scheduled task inventory |
| **Movement Agent**| 🔀 | Lateral movement simulation | Network hop path map |
| **Exfil Agent** | 📤 | Data exfiltration staging | Staged data & covert channel report |
| **Purple Agent** | 🟣 | Detection engineering | Validated Sigma rules, YARA rules, Coverage Scorecard |
| **Deception Agent**| 🕸️ | Active defense trap deployment | Target-tailored decoy honeypots & honeytokens |
| **Explain Agent** | 💡 | Executive reporting | Human-readable incident narrative & root cause analysis |

---

## 📂 Output Artifacts

Each run creates a timestamped output folder under `output/run_YYYYMMDD_HHMMSS/` containing:

- 📄 `report.md` — Full technical & defensive coverage scorecard report.
- 💡 `explainability_report.md` — Executive plain-English incident breakdown.
- 🗺️ `attck_navigator.json` — Layer file ready for direct import into [MITRE ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/).
- 📜 `sigma_rules/` — Validated YAML Sigma rules for process, registry, and network events.
- 🎯 `yara_rules/` — YARA signature files for specific tool indicators.
- 💾 `raw_results.json` — Complete execution telemetry across all pipeline phases.

---

## 💻 Hardware & Model Sizing Guidelines

The Hive is designed **privacy-first** to run entirely on local LLMs via **Ollama**, ensuring no sensitive corporate infrastructure data leaves your network.

| Deployment Target | Hardware Spec | Recommended Model | Command |
| :--- | :--- | :--- | :--- |
| **Laptop / Workstation** | 16GB VRAM or Apple Silicon M-Series | `llama3.1:8b` or `mistral` | `python run.py -r data/threat_reports/apt29.json -m llama3.1:8b --simulate` |
| **Enterprise Server / GPU Rig** | 32GB+ VRAM (NVIDIA RTX 4090 / 5090 / A100) | `llama3.3:70b` | `python run.py -r data/threat_reports/apt29.json` |

---

## 🛠️ Tech Stack & Dependencies

- **Core**: Python 3.10+
- **LLM Engine**: Ollama (Local open-weights inference)
- **Agent Framework**: CrewAI & LangChain
- **Knowledge Base**: MITRE ATT&CK Enterprise Matrix (STIX JSON)
- **Emulation Engine**: Atomic Red Team (`atomic-operator`)
- **Detection Standards**: Sigma Rule Format & YARA Syntax

---

## 👥 Authors

* **Sapna VM**
* **Prajwal Chowdary** - [GitHub](https://github.com/prajwalchowdary2)
* **Vinaykumar**
* **Prasad HB**

---

## 📄 License

This project is open-source under the [MIT License](LICENSE). 

*Disclaimer: For authorized security testing, educational, and defense research purposes only.*

