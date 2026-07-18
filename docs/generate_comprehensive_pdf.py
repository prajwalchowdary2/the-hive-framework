#!/usr/bin/env python3
"""Generate a comprehensive LaTeX-style academic PDF for The Hive's features."""

import os
import sys

# Fix encoding for Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fpdf import FPDF

class AcademicPDF(FPDF):
    """Custom PDF class with LaTeX-style academic formatting."""

    def __init__(self):
        super().__init__(format='A4')
        self.set_auto_page_break(auto=True, margin=25)
        self.section_num = 0
        
        font_dir = "C:/Windows/Fonts"
        self.add_font("Serif", "", f"{font_dir}/georgia.ttf", uni=True)
        self.add_font("Serif", "B", f"{font_dir}/georgiab.ttf", uni=True)
        self.add_font("Serif", "I", f"{font_dir}/georgiai.ttf", uni=True)
        self.add_font("Serif", "BI", f"{font_dir}/georgiaz.ttf", uni=True)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Serif", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "The Hive: Comprehensive Feature & Architecture Specification", align="C")
            self.ln(3)
            self.set_draw_color(180, 180, 180)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font("Serif", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, str(self.page_no()), align="C")

    def title_block(self, title, subtitle):
        self.set_font("Serif", "B", 18)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 9, title, align="C")
        self.ln(4)
        
        self.set_font("Serif", "", 12)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, subtitle, align="C")
        self.ln(8)
        
        self.set_draw_color(180, 180, 180)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(8)

    def section(self, title):
        self.section_num += 1
        roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"]
        num = roman[self.section_num - 1] if self.section_num <= 16 else str(self.section_num)
        self.ln(4)
        self.set_font("Serif", "B", 13)
        self.set_text_color(20, 20, 20)
        self.cell(0, 8, f"{num}. {title}")
        self.ln(8)

    def subsection(self, title):
        self.ln(3)
        self.set_font("Serif", "BI", 11)
        self.set_text_color(30, 30, 30)
        self.cell(0, 7, title)
        self.ln(7)

    def body_text(self, text):
        self.set_font("Serif", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text, align="J")
        self.ln(3)

    def highlight_box(self, title, text):
        self.set_fill_color(249, 249, 240)
        self.set_draw_color(201, 162, 39)
        self.set_line_width(0.6)
        x = self.l_margin
        y = self.get_y()
        w = self.w - self.l_margin - self.r_margin
        
        self.set_x(x + 5)
        self.set_font("Serif", "B", 9)
        self.set_text_color(20, 20, 20)
        self.cell(w - 10, 5, title, align="L")
        self.ln(5)
        
        self.set_x(x + 5)
        self.set_font("Serif", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(w - 10, 4.5, text, align="L")
        
        h = self.get_y() - y + 4
        self.rect(x, y - 2, w, h, style="D")
        self.line(x, y - 2, x, y - 2 + h)
        self.ln(6)

    def bullet_point(self, title, text):
        self.set_font("Serif", "B", 10)
        self.set_text_color(30, 30, 30)
        
        x = self.l_margin + 5
        self.set_x(x)
        self.write(5.5, "\u2022  " + title + ": ")
        
        self.set_font("Serif", "", 10)
        self.write(5.5, text)
        self.ln(6)


def generate_pdf():
    pdf = AcademicPDF()
    pdf.set_title("The Hive: Comprehensive Feature Specification")
    pdf.set_author("The Hive")
    pdf.add_page()

    pdf.title_block(
        "The Hive: Comprehensive Feature Specification",
        "An Exhaustive Breakdown of Architecture, Agents, UI, and Outputs"
    )

    pdf.body_text(
        "This document provides a maximal, feature-by-feature breakdown of The Hive. It is intended to serve as "
        "the ultimate reference manual, covering the underlying artificial intelligence architecture, the individual "
        "agent capabilities, the dual-interface visual design, and the highly specific output artifacts generated "
        "by the system during adversary emulation."
    )

    # ---- SEC 1 ----
    pdf.section("Core Orchestration Engine & Architecture")
    pdf.body_text(
        "At the heart of The Hive is a heavily optimized, asynchronous orchestration engine. Unlike legacy tools "
        "that execute static YAML scripts top-to-bottom, The Hive uses a Directed Acyclic Graph (DAG) driven by "
        "local Large Language Models (LLMs). This means the system reasons about the network environment in real-time."
    )
    pdf.bullet_point("Local Privacy-First AI", "The platform integrates natively with Ollama (specifically targeting Llama 3.1 70B). It performs all reasoning locally on consumer GPU hardware. Zero bytes of sensitive threat intelligence or network topology are ever sent to cloud providers like OpenAI or Anthropic.")
    pdf.bullet_point("DAG Execution Model", "The 8 AI agents do not run randomly. They operate within a strict dependency graph. The output of the Intel Agent strictly forms the input of the Planner Agent. The planner's output dictates the exact operational flow of the 5 execution agents.")
    pdf.bullet_point("State Persistence", "Between every single agent execution, the complete internal state, memory, and findings are dumped to intermediate JSON files. If a simulation is interrupted, it can resume perfectly from the last known state without losing forensic data.")

    # ---- SEC 2 ----
    pdf.section("The Intelligence Phase: Intel Agent")
    pdf.body_text(
        "The first step in any adversary emulation is understanding the adversary. The Intel Agent bridges the massive gap "
        "between unstructured human language (blog posts, PDFs) and machine-executable code."
    )
    pdf.bullet_point("Unstructured Text Parsing", "The Intel Agent uses Natural Language Processing (NLP) to read raw threat reports (e.g., a Mandiant report on APT29) and identify sentences describing malicious behavior.")
    pdf.bullet_point("MITRE ATT&CK Mapping", "It cross-references identified behaviors against the massive MITRE ATT&CK Enterprise Matrix (containing over 700 techniques) and extracts the exact IDs (e.g., T1059.001 for PowerShell).")
    pdf.bullet_point("Confidence Scoring", "It assigns a mathematical confidence score to each extracted technique, ensuring that low-probability or ambiguous intelligence is flagged before execution.")

    # ---- SEC 3 ----
    pdf.section("The Planning Phase: Planner Agent")
    pdf.body_text(
        "A list of techniques is useless if executed in the wrong order. You cannot exfiltrate data before you gain access. "
        "The Planner Agent acts as the Red Team Lead, organizing the attack."
    )
    pdf.bullet_point("14-to-5 Phase Compression", "The standard MITRE framework has 14 tactical phases. The Planner compresses these into a highly actionable 5-phase operational Kill Chain: Recon, Access, Persistence, Movement, and Exfiltration.")
    pdf.bullet_point("Dependency Resolution", "The Planner evaluates the prerequisites of every technique. If a technique requires Administrator privileges, the Planner schedules privilege escalation techniques immediately prior to it.")
    pdf.bullet_point("Atomic Mapping", "The Planner validates which extracted techniques have corresponding live-fire execution scripts available via the Atomic Red Team database.")

    # ---- SEC 4 ----
    pdf.section("Execution Phase: Reconnaissance Agent")
    pdf.body_text(
        "The Recon Agent is the first operator to touch the target network. Its goal is situational awareness."
    )
    pdf.bullet_point("Network Sweeping", "Executes commands like ARP sweeps and ICMP pings to build a map of the local subnet.")
    pdf.bullet_point("Topology Generation", "In simulation mode, it uses LLM logic to hallucinate a highly realistic corporate network topography (e.g., 10.0.0.0/24 containing Domain Controllers, File Servers, and Workstations).")
    pdf.bullet_point("Defense Discovery", "Actively looks for running EDR processes (CrowdStrike, SentinelOne) to inform subsequent agents of potential roadblocks.")

    # ---- SEC 5 ----
    pdf.section("Execution Phase: Initial Access Agent")
    pdf.body_text(
        "The Access Agent breaches the perimeter. It focuses heavily on user execution and fileless malware delivery."
    )
    pdf.bullet_point("Payload Staging", "Simulates dropping malicious LNK files, macro-enabled Word documents, or disguised PDFs onto the filesystem.")
    pdf.bullet_point("Memory Injection", "Executes Base64 encoded PowerShell payloads designed to run purely in RAM, avoiding disk-based Antivirus signatures.")

    # ---- SEC 6 ----
    pdf.section("Execution Phase: Persistence Agent")
    pdf.body_text(
        "The Persistence Agent ensures the Red Team does not lose their foothold if the target machine reboots."
    )
    pdf.bullet_point("Registry Manipulation", "Modifies HKCU and HKLM Run/RunOnce keys to execute malicious binaries on user login.")
    pdf.bullet_point("Scheduled Tasks", "Creates hidden Windows Scheduled Tasks configured to run as SYSTEM, ensuring highest-level privileges upon reboot.")

    # ---- SEC 7 ----
    pdf.section("Execution Phase: Lateral Movement Agent")
    pdf.body_text(
        "The Lateral Movement Agent focuses on spreading the infection from the initial patient-zero to the crown jewels."
    )
    pdf.bullet_point("Credential Access", "Simulates LSASS memory dumping (Mimikatz style) to steal NTLM hashes or Kerberos tickets.")
    pdf.bullet_point("Pass-The-Hash Execution", "Uses the stolen credentials to authenticate to remote SMB shares (C$, ADMIN$) and execute code via Windows Management Instrumentation (WMI) or PsExec.")

    # ---- SEC 8 ----
    pdf.section("Execution Phase: Exfiltration Agent")
    pdf.body_text(
        "The Exfiltration Agent completes the attack by stealing the data."
    )
    pdf.bullet_point("Data Staging", "Finds sensitive files (e.g., HR databases, source code), compresses them into ZIP archives, and encrypts them with a hardcoded password.")
    pdf.bullet_point("Encrypted Channels", "Simulates pushing the compressed archives out to cloud providers (AWS S3, Mega) over standard HTTPS (Port 443) to blend in with normal web traffic.")

    # ---- SEC 9 ----
    pdf.section("Defensive Engineering: Purple Team Agent")
    pdf.highlight_box("The Crown Jewel Feature", "While the Operator Fleet breaks things, the Purple Team Agent fixes them. This agent represents the single largest leap over traditional adversary emulation frameworks.")
    pdf.body_text(
        "The Purple Team Agent acts as a Senior Detection Engineer. It reads the execution logs of the Red Team and immediately builds defensive countermeasures."
    )
    pdf.bullet_point("Sigma Rule Generation", "Automatically generates production-ready Sigma rules. These rules target the specific Event IDs (e.g., Sysmon 13 for Registry, Event 4688 for Process Creation) triggered by the Red Team.")
    pdf.bullet_point("YARA Indicator Creation", "Generates YARA rules to catch the specific obfuscation patterns, base64 stubs, or file entropies of the payloads used by the Access Agent.")
    pdf.bullet_point("Deterministic Hashing", "Sigma rule UUIDs are generated via MD5 hashes of the technique IDs. This ensures that re-running the same threat actor produces the exact same rule IDs, allowing for seamless integration into production SIEMs without generating duplicates.")

    # ---- SEC 10 ----
    pdf.section("D3FEND Gap Analysis Engine")
    pdf.body_text(
        "Identifying a gap in defenses is only half the battle. The Hive goes further by recommending exact architectural fixes."
    )
    pdf.bullet_point("MITRE D3FEND Mapping", "When a technique is identified as highly evasive or 'undetected', the system queries the MITRE D3FEND framework. It maps the offensive ATT&CK technique to its defensive counterpart.")
    pdf.bullet_point("Actionable Countermeasures", "Instead of just saying 'Pass the Hash failed', the system outputs: 'Deploy Credential Guard (D3-RRDD) and monitor Event ID 4624 Logon Type 9'. This gives SOC teams immediate remediation steps.")

    # ---- SEC 11 ----
    pdf.section("Visual Interfaces: The Forensic CLI Sequence")
    pdf.body_text(
        "The terminal interface (run.py) was custom-built to provide a cinematic, highly engaging user experience. It abandons boring standard-out logging for dynamic visual effects."
    )
    pdf.bullet_point("Hexadecimal Memory Scanning", "Upon launch, the terminal displays a rapid, scrolling matrix of randomized hexadecimal memory addresses, simulating a low-level memory scan of the target environment.")
    pdf.bullet_point("ANSI Glitch Effects", "The Hive's logo and phase transitions utilize ANSI color codes (reds, cyan, stark white) to create a 'glitching' visual effect, heavily inspired by modern cyberpunk/forensic aesthetics.")
    pdf.bullet_point("Real-Time Telemetry Ticker", "As agents execute, the CLI outputs a clean, timestamped ticker showing exact tool executions and memory states in real time.")

    # ---- SEC 12 ----
    pdf.section("Visual Interfaces: The Tactical Dashboard")
    pdf.body_text(
        "For a broader overview, The Hive features a standalone, zero-dependency web dashboard (dashboard.html). This dashboard is designed for SOC wall-monitors or Black Hat presentations."
    )
    pdf.bullet_point("Steel & Dark Grey Aesthetics", "The dashboard uses a highly refined, muted color palette (slate gray, tactical green, crimson red) to look premium and professional, avoiding cheap neon colors.")
    pdf.bullet_point("Canvas Matrix Rain", "The background features a custom HTML5 Canvas rendering a muted, slow-falling data rain. It provides motion without distracting from the data.")
    pdf.bullet_point("Scroll-Triggered Animations", "Using the IntersectionObserver API, the dashboard reveals agents, statistics, and pipeline phases smoothly as the user scrolls, creating a dynamic presentation experience.")
    pdf.bullet_point("Live State Emulation", "The dashboard features a live threat ticker and blinking operational states, simulating a live WebSocket connection to a running campaign.")

    # ---- SEC 13 ----
    pdf.section("Output Artifacts & File Structure")
    pdf.body_text(
        "The Hive generates a highly structured output directory for every single simulation run."
    )
    pdf.bullet_point("report.md", "A human-readable markdown file summarizing the entire campaign, listing all techniques, extracted Sigma rules, and the final D3FEND gap analysis.")
    pdf.bullet_point("raw_results.json", "A massive, machine-readable JSON dump containing the entire LLM prompt history, execution logs, and API responses. Perfect for debugging or ingesting into external data lakes.")
    pdf.bullet_point("sigma_rules/", "A dedicated directory containing individual .yml files for every single Sigma rule generated during the run.")
    pdf.bullet_point("yara_rules/", "A dedicated directory containing the .yar files for static payload detection.")

    # ---- SEC 14 ----
    pdf.section("Deployment & Automation")
    pdf.body_text(
        "The system is designed for zero-friction deployment on Windows."
    )
    pdf.bullet_point("start_dashboard.bat", "A one-click batch script that automatically launches a local Python HTTP server on port 8080 and opens the user's default browser to the dashboard.")
    pdf.bullet_point("stop_dashboard.bat", "A clean-up script that uses taskkill to gracefully shut down the background server by targeting its specific window title, preventing port-in-use errors.")
    pdf.bullet_point("Python Virtual Environment", "The entire tool runs within an isolated venv, ensuring that dependencies (fpdf2, markdown) do not conflict with the host system's global Python installation.")

    # ---- SEC 15 ----
    pdf.section("Conclusion & Operational Impact")
    pdf.body_text(
        "The Hive represents a paradigm shift in adversary emulation. By combining the natural language processing power of local LLMs with the structured execution of Atomic Red Team and the standardized defense formats of Sigma/YARA, it removes the human bottleneck from the threat intelligence lifecycle."
    )
    pdf.body_text(
        "What previously required a dedicated Red Team, a Threat Intelligence Analyst, and a Detection Engineer working for weeks can now be accomplished by The Hive in under 5 minutes. It is the ultimate tool for continuous security validation."
    )

    output_path = os.path.join(os.path.dirname(__file__), "The_Hive_Comprehensive_Feature_Report.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Pages: {pdf.pages_count}")

if __name__ == "__main__":
    generate_pdf()
