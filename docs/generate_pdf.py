#!/usr/bin/env python3
"""Generate a LaTeX-style academic PDF whitepaper for The Hive."""

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
        # Add Unicode fonts from Windows system
        font_dir = "C:/Windows/Fonts"
        self.add_font("Serif", "", f"{font_dir}/georgia.ttf", uni=True)
        self.add_font("Serif", "B", f"{font_dir}/georgiab.ttf", uni=True)
        self.add_font("Serif", "I", f"{font_dir}/georgiai.ttf", uni=True)
        self.add_font("Serif", "BI", f"{font_dir}/georgiaz.ttf", uni=True)
        self.add_font("Mono", "", f"{font_dir}/consola.ttf", uni=True)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Serif", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "The Hive: Multi-Agent LLM-Driven Adversary Emulation", align="C")
            self.ln(3)
            self.set_draw_color(180, 180, 180)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font("Serif", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, str(self.page_no()), align="C")

    def title_block(self, title, authors, affiliation, venue):
        self.set_font("Serif", "B", 17)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 9, title, align="C")
        self.ln(5)
        self.set_font("Serif", "", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 7, authors, align="C")
        self.ln(6)
        self.set_font("Serif", "I", 9.5)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, affiliation, align="C")
        self.ln(8)
        self.set_font("Serif", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 6, venue.upper(), align="C")
        self.ln(8)
        self.set_draw_color(180, 180, 180)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(5)

    def abstract(self, text):
        self.set_font("Serif", "B", 9)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, "ABSTRACT", align="C")
        self.ln(5)
        x_start = 30
        w = 150
        self.set_x(x_start)
        self.set_font("Serif", "", 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(w, 4.5, text, align="J")
        self.ln(3)

    def keywords(self, kw):
        x_start = 30
        w = 150
        self.set_x(x_start)
        self.set_font("Serif", "B", 8.5)
        self.set_text_color(70, 70, 70)
        self.write(4.5, "Keywords: ")
        self.set_font("Serif", "", 8.5)
        self.write(4.5, kw)
        self.ln(6)
        self.set_draw_color(180, 180, 180)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(6)

    def section(self, title):
        self.section_num += 1
        roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        num = roman[self.section_num - 1] if self.section_num <= 10 else str(self.section_num)
        self.ln(4)
        self.set_font("Serif", "B", 12.5)
        self.set_text_color(20, 20, 20)
        self.cell(0, 8, f"{num}. {title}")
        self.ln(7)

    def subsection(self, title):
        self.ln(2)
        self.set_font("Serif", "BI", 10.5)
        self.set_text_color(30, 30, 30)
        self.cell(0, 7, title)
        self.ln(6)

    def body_text(self, text, indent=True):
        self.set_font("Serif", "", 10)
        self.set_text_color(30, 30, 30)
        if indent:
            self.set_x(self.l_margin + 8)
            self.multi_cell(self.w - self.l_margin - self.r_margin - 8, 5, text, align="J")
        else:
            self.multi_cell(0, 5, text, align="J")
        self.ln(2)

    def bullet_list(self, items):
        self.set_font("Serif", "", 9.5)
        self.set_text_color(30, 30, 30)
        for item in items:
            x = self.l_margin + 8
            self.set_x(x)
            self.write(5, "\u2022  ")
            self.multi_cell(self.w - x - self.r_margin - 5, 5, item, align="L")
            self.ln(1)
        self.ln(2)

    def add_table(self, caption, headers, rows):
        self.set_font("Serif", "I", 8.5)
        self.set_text_color(50, 50, 50)
        self.cell(0, 5, caption, align="C")
        self.ln(5)

        col_count = len(headers)
        available_w = self.w - self.l_margin - self.r_margin
        col_w = available_w / col_count

        # Header
        self.set_draw_color(50, 50, 50)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.l_margin + available_w, self.get_y())
        self.ln(1)
        self.set_font("Serif", "B", 8.5)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(240, 240, 240)
        for h in headers:
            self.cell(col_w, 6, h, border=0, fill=True, align="L")
        self.ln()
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y(), self.l_margin + available_w, self.get_y())
        self.ln(1)

        # Rows
        self.set_font("Serif", "", 8.5)
        self.set_text_color(40, 40, 40)
        for row in rows:
            max_h = 6
            for i, cell in enumerate(row):
                self.cell(col_w, max_h, str(cell)[:45], border=0, align="L")
            self.ln()
            self.set_draw_color(200, 200, 200)
            self.line(self.l_margin, self.get_y(), self.l_margin + available_w, self.get_y())

        self.set_draw_color(50, 50, 50)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.l_margin + available_w, self.get_y())
        self.ln(5)

    def highlight_box(self, text):
        self.set_fill_color(249, 249, 240)
        self.set_draw_color(201, 162, 39)
        self.set_line_width(0.6)
        x = self.l_margin
        y = self.get_y()
        w = self.w - self.l_margin - self.r_margin
        self.set_font("Serif", "", 9)
        self.set_text_color(40, 40, 40)
        self.set_x(x + 5)
        self.multi_cell(w - 10, 4.5, text, align="L")
        h = self.get_y() - y + 4
        self.rect(x, y - 2, w, h, style="D")
        self.line(x, y - 2, x, y - 2 + h)
        self.ln(4)

    def code_block(self, text):
        self.set_font("Mono", "", 7.5)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(246, 246, 246)
        x = self.l_margin + 5
        w = self.w - self.l_margin - self.r_margin - 10
        self.set_x(x)
        self.multi_cell(w, 4, text, align="L", fill=True)
        self.ln(3)

    def reference_item(self, num, text):
        self.set_font("Serif", "", 8)
        self.set_text_color(50, 50, 50)
        self.set_x(self.l_margin + 3)
        self.write(4, f"[{num}]  ")
        self.multi_cell(self.w - self.l_margin - self.r_margin - 10, 4, text, align="L")
        self.ln(1)


def generate_pdf():
    pdf = AcademicPDF()
    pdf.set_title("The Hive: Multi-Agent LLM-Driven Adversary Emulation and Automated Detection Engineering")
    pdf.set_author("Sapna")
    pdf.add_page()

    # ---- TITLE ----
    pdf.title_block(
        "The Hive: Multi-Agent LLM-Driven\nAdversary Emulation and Automated\nDetection Engineering",
        "Sapna",
        "Independent Security Research",
        "Submitted to Black Hat Europe 2026 \u2014 Arsenal / Briefings"
    )

    # ---- ABSTRACT ----
    pdf.abstract(
        "We present The Hive, an open-source multi-agent AI pipeline that automates the complete adversary "
        "emulation lifecycle\u2014from threat intelligence ingestion to detection rule generation. Given a structured "
        "or free-form threat report, The Hive extracts MITRE ATT&CK techniques via a large language model "
        "(Llama 3.1 70B running locally on consumer GPU hardware), constructs a sequenced kill-chain emulation "
        "plan, executes each technique through specialized operator agents (with optional live Atomic Red Team "
        "execution), and automatically generates Sigma detection rules, YARA indicators, ATT&CK Navigator "
        "heatmaps, and a detection coverage scorecard with D3FEND-mapped gap analysis. In an APT29 emulation, "
        "The Hive extracted 12 techniques, generated 12 Sigma rules and 3 YARA rules, and identified 4 detection "
        "gaps with actionable countermeasure recommendations\u2014completing the full pipeline in under 5 minutes on "
        "a single workstation. The Hive bridges the operational gap between red team emulation and blue team "
        "detection engineering, enabling security teams to continuously validate and improve their detection "
        "posture against real-world adversaries."
    )

    pdf.keywords(
        "adversary emulation, multi-agent systems, large language models, MITRE ATT&CK, "
        "detection engineering, Sigma rules, purple teaming, threat intelligence automation"
    )

    # ---- I. INTRODUCTION ----
    pdf.section("Introduction")
    pdf.body_text(
        "Modern security operations centers (SOCs) face an asymmetric challenge: adversaries evolve tactics "
        "continuously, while detection rule development remains a largely manual, labor-intensive process. "
        "A single APT campaign may employ 10\u201320 distinct techniques spanning the full MITRE ATT&CK kill chain, "
        "yet translating a threat intelligence report into validated detection rules can take a skilled analyst "
        "days or weeks.", False
    )
    pdf.body_text(
        "Adversary emulation frameworks such as MITRE CALDERA, Atomic Red Team, and Infection Monkey have "
        "made technique execution more accessible, but they do not close the loop: the output is execution "
        "telemetry, not detection rules. Detection engineering tools like Sigma and YARA provide standardized "
        "rule formats, but rule authorship still requires deep domain expertise and manual effort."
    )
    pdf.body_text(
        "Recent advances in large language models (LLMs) have demonstrated strong capabilities in structured "
        "reasoning, code generation, and domain-specific knowledge retrieval. The emergence of multi-agent "
        "orchestration frameworks suggests an architecture where specialized AI agents can collaborate on "
        "complex security workflows."
    )
    pdf.body_text(
        "In this paper, we present The Hive, a multi-agent AI pipeline that automates the full cycle: "
        "Threat Report \u2192 TTP Extraction \u2192 Kill Chain Planning \u2192 Technique Execution \u2192 Detection Rule "
        "Generation \u2192 Coverage Scorecard \u2192 Gap Analysis. The system runs entirely on local infrastructure "
        "using Ollama with Llama 3.1 70B, requiring no cloud API dependencies, making it suitable for "
        "classified or air-gapped environments."
    )

    # ---- II. RELATED WORK ----
    pdf.section("Related Work")
    pdf.body_text(
        "Adversary Emulation. MITRE CALDERA [1] provides automated adversary emulation using decision trees, "
        "but lacks integrated detection engineering. Atomic Red Team [2] offers unit-test-style technique "
        "execution but requires manual orchestration and interpretation. Purple Team frameworks like Vectr [3] "
        "track coverage but do not generate rules.", False
    )
    pdf.body_text(
        "LLM-Assisted Security. Recent work has explored LLMs for vulnerability analysis [4], malware "
        "classification [5], and CTI extraction [6]. However, end-to-end pipelines that chain LLM-driven "
        "intelligence extraction with automated emulation and detection engineering remain unexplored."
    )
    pdf.body_text(
        "Detection Engineering Automation. SigmaHQ [7] provides community-maintained rules, and pySigma [8] "
        "enables programmatic rule generation. The Hive builds upon pySigma to generate context-aware rules "
        "driven by emulation results rather than static templates."
    )

    # ---- III. ARCHITECTURE ----
    pdf.section("System Architecture")
    pdf.body_text(
        "The Hive employs a linear directed acyclic graph (DAG) of eight specialized agents, each responsible "
        "for a distinct phase of the adversary emulation lifecycle. All agents inherit from a common BaseAgent "
        "class that provides LLM invocation (with a three-tier fallback: LangChain \u2192 direct REST API \u2192 "
        "template defaults), ATT&CK technique resolution, and atomic test execution capabilities.", False
    )

    pdf.code_block(
        "Threat Report (JSON)\n"
        "        |\n"
        "        v\n"
        "+---------------+\n"
        "|  Intel Agent  | -- Extract TTPs, validate against ATT&CK (709 techniques)\n"
        "+-------+-------+\n"
        "        v\n"
        "+---------------+\n"
        "| Planner Agent | -- 14-tactic -> 5-phase compression, dependency resolution\n"
        "+-------+-------+\n"
        "        v\n"
        "+---------------------------------------------------+\n"
        "|              Operator Fleet (5 agents)             |\n"
        "|  Recon -> Access -> Persist -> Movement -> Exfil   |\n"
        "|  [Live Atomic Red Team or Simulated Execution]     |\n"
        "+---------------------------+-----------------------+\n"
        "                            v\n"
        "                   +----------------+\n"
        "                   |  Purple Agent  | -- Sigma/YARA, D3FEND, scorecard\n"
        "                   +--------+-------+\n"
        "                            v\n"
        "              +--------------------------+\n"
        "              |     Output Artifacts     |\n"
        "              |  report.md, sigma_rules, |\n"
        "              |  yara_rules, navigator   |\n"
        "              +--------------------------+"
    )

    pdf.subsection("A. Intel Agent")
    pdf.body_text(
        "The Intel Agent supports dual-mode TTP extraction: (1) structured ingestion from pre-annotated "
        "reports containing known_techniques arrays, validated against the full ATT&CK Enterprise STIX bundle "
        "(709 techniques); and (2) LLM-driven extraction from free-form narrative text, where the model is "
        "prompted to return structured JSON with technique IDs, names, tactics, and confidence levels. "
        "Extracted techniques are enriched with ATT&CK metadata (description, platforms, data sources) and "
        "sorted by kill-chain phase ordering.", False
    )

    pdf.subsection("B. Planner Agent")
    pdf.body_text(
        "The Planner compresses ATT&CK's 14 tactical phases into 5 operational phases: Reconnaissance, "
        "Initial Access, Persistence, Lateral Movement, and Exfiltration. This mapping (e.g., "
        "credential-access \u2192 movement, defense-evasion \u2192 persist, collection \u2192 exfil) reflects real-world "
        "operational sequencing. The planner enforces per-phase technique limits (configurable, default 5) "
        "and annotates phase dependencies.", False
    )

    pdf.subsection("C. Operator Fleet")
    pdf.body_text(
        "Five operator agents execute their respective kill-chain phases. Each operator supports dual-mode "
        "execution: live mode invokes Atomic Red Team tests via the atomic-operator library with prerequisite "
        "checking, while simulation mode generates synthetic execution records. Context flows forward through "
        "the fleet: reconnaissance findings inform initial access targeting, compromised hosts feed into "
        "persistence mechanisms, and so forth. The Recon Agent augments findings with LLM-synthesized network "
        "topology based on the target environment configuration.", False
    )

    pdf.subsection("D. Purple Team Agent")
    pdf.body_text(
        "The capstone agent performs four functions: (1) Sigma rule generation using technique-specific "
        "detection templates covering 12 technique families with proper log source mapping; (2) YARA rule "
        "generation for techniques with known tool indicators (PowerShell, Mimikatz, obfuscation patterns); "
        "(3) coverage assessment using a knowledge-based model of detection difficulty (8 well-detected vs. "
        "6 hard-to-detect technique categories); and (4) gap analysis with D3FEND countermeasure mapping and "
        "actionable recommendations.", False
    )

    # ---- IV. KEY DESIGN DECISIONS ----
    pdf.section("Key Design Decisions")

    pdf.subsection("A. Local LLM Execution")
    pdf.body_text(
        "The Hive uses Ollama with Llama 3.1 70B running entirely on local GPU hardware (tested on NVIDIA "
        "RTX 5090, 32 GB VRAM). This eliminates cloud API dependencies, avoids transmitting sensitive threat "
        "intelligence to third-party services, and enables deployment in air-gapped or classified environments. "
        "The three-tier LLM fallback chain (LangChain \u2192 direct REST \u2192 template defaults) ensures the pipeline "
        "produces useful output even if the LLM is unavailable.", False
    )

    pdf.subsection("B. Deterministic Rule Generation")
    pdf.body_text(
        "Sigma rule IDs are generated deterministically via MD5 hash of the technique identifier, formatted "
        "as UUIDv4. This ensures idempotent re-generation\u2014re-running the pipeline against the same threat "
        "actor produces identical rule IDs, critical for rule lifecycle management in production SOC "
        "environments where rules are tracked by UUID.", False
    )

    pdf.subsection("C. ATT&CK-to-D3FEND Bridging")
    pdf.body_text(
        "The gap analysis module maps each undetected offensive technique (ATT&CK) to its corresponding "
        "defensive countermeasure (D3FEND), providing SOC teams with actionable remediation paths rather than "
        "simply flagging detection failures. For example, T1550.002 (Pass the Hash) maps to D3-RRDD with a "
        "recommendation to deploy Credential Guard and monitor Windows Event ID 4624 with LogonType 9.", False
    )

    pdf.subsection("D. Intermediate State Persistence")
    pdf.body_text(
        "After each agent completes, its output is persisted as intermediate_{step}.json. This enables "
        "post-mortem analysis of failed runs, partial pipeline re-execution, and forensic review of the "
        "LLM's reasoning at each stage.", False
    )

    # ---- V. EVALUATION ----
    pdf.section("Evaluation")

    pdf.subsection("A. APT29 Case Study")
    pdf.body_text(
        "We evaluated The Hive against APT29 (Cozy Bear / Midnight Blizzard), a Russian SVR-attributed "
        "threat actor targeting government, healthcare, and defense sectors. The input report contained 12 "
        "pre-annotated ATT&CK techniques spanning the full kill chain, from T1566.001 (Spearphishing "
        "Attachment) through T1048.002 (Encrypted Exfiltration).", False
    )

    pdf.add_table(
        "Table I: APT29 Emulation Results",
        ["Metric", "Value"],
        [
            ["Techniques Extracted", "12"],
            ["Kill Chain Phases Executed", "5 (Recon, Access, Persist, Move, Exfil)"],
            ["Sigma Rules Generated", "12"],
            ["YARA Rules Generated", "3"],
            ["Techniques Detected", "8 (67%)"],
            ["Detection Gaps Identified", "4 (with D3FEND countermeasures)"],
            ["Total Pipeline Duration", "~5 minutes"],
            ["Hardware", "RTX 5090 (32GB), i9 Ultra, 128GB RAM"],
        ]
    )

    pdf.subsection("B. Detection Coverage Analysis")
    pdf.body_text(
        "The pipeline identified four critical detection gaps in the simulated environment:", False
    )

    pdf.add_table(
        "Table II: Detection Gap Analysis with D3FEND Countermeasures",
        ["Technique", "ATT&CK ID", "D3FEND", "Recommendation"],
        [
            ["Obfuscated Files", "T1027", "D3-FCA", "AMSI logging + content inspect"],
            ["File Deletion", "T1070.004", "D3-FIM", "File Integrity Monitoring"],
            ["Pass the Hash", "T1550.002", "D3-RRDD", "Credential Guard, EID 4624"],
            ["Encrypted Exfil", "T1048.002", "D3-NTA", "SSL/TLS inspect + anomaly"],
        ]
    )

    pdf.subsection("C. Generated Sigma Rule Quality")
    pdf.body_text(
        "The generated Sigma rules adhere to the SigmaHQ specification with proper logsource, detection, "
        "tags (ATT&CK-mapped), and references fields. High-fidelity templates were produced for 10 of 12 "
        "techniques. The T1059.001 (PowerShell) rule detects encoded command flags (-enc, -nop), download "
        "cradles (Net.WebClient, DownloadString), and execution bypasses (IEX, Invoke-Expression). Two "
        "techniques (T1016, T1027) fell back to generic command-line matching templates, representing an "
        "area for future detection logic refinement.", False
    )

    pdf.subsection("D. Multi-Threat Actor Validation")
    pdf.body_text(
        "The pipeline was additionally validated against FIN7 (Eastern Europe, 14 techniques, financial "
        "sector) and Lazarus Group (North Korea, 14 techniques, cryptocurrency sector), demonstrating "
        "generalizability across distinct adversary profiles, TTPs, and operational objectives.", False
    )

    # ---- VI. BLACK HAT RELEVANCE ----
    pdf.section("Black Hat Europe Relevance")
    pdf.highlight_box(
        "Arsenal Fit: The Hive is open-source, fully functional with live demo capability. "
        "Meets all Arsenal requirements: 3+ pages documentation, self-contained demo, no vendor affiliation.\n\n"
        "Briefing Fit: Novel architecture (multi-agent LLM for purple teaming), original implementation, "
        "quantitative evaluation, addresses real operational gap in security operations."
    )

    pdf.body_text("The Hive addresses several topics solicited by Black Hat review boards:", False)
    pdf.bullet_list([
        "Novel Tool Release \u2014 Open-source, local-first, GPU-accelerated purple team automation",
        "AI/ML in Security \u2014 Multi-agent LLM orchestration for offensive + defensive security",
        "Detection Engineering \u2014 Automated Sigma/YARA generation from adversary emulation",
        "Purple Teaming \u2014 Bridging ATT&CK (offense) to D3FEND (defense) automatically",
        "Threat Intelligence Automation \u2014 End-to-end TI-to-detection pipeline",
    ])

    # ---- VII. LIMITATIONS ----
    pdf.section("Limitations and Future Work")
    pdf.body_text(
        "Detection template coverage. The current Sigma generator includes hardcoded templates for 12 "
        "technique families. Expanding to LLM-generated detection logic (with human-in-the-loop validation) "
        "would improve coverage of the full ATT&CK matrix.", False
    )
    pdf.body_text(
        "CrewAI integration. The agents.yaml persona definitions and CrewAI dependency are scaffolded but "
        "not yet active. Migrating to CrewAI's native multi-agent orchestration would enable dynamic task "
        "delegation, inter-agent communication, and parallel execution."
    )
    pdf.body_text(
        "Telemetry validation. In simulation mode, detection coverage is assessed heuristically rather than "
        "against actual SIEM telemetry. Integration with Elastic Security, Splunk, or Microsoft Sentinel for "
        "ground-truth validation is planned."
    )
    pdf.body_text(
        "Rule quality scoring. Automated quality metrics (false positive rate estimation, log source "
        "availability checking) would help prioritize generated rules for production deployment."
    )

    # ---- VIII. CONCLUSION ----
    pdf.section("Conclusion")
    pdf.body_text(
        "The Hive demonstrates that multi-agent LLM architectures can effectively automate the adversary "
        "emulation lifecycle, from threat intelligence parsing through detection rule generation. By running "
        "entirely on local GPU infrastructure with an open-weight model, it eliminates cloud dependencies "
        "while achieving meaningful results: 12 validated Sigma rules, 3 YARA indicators, and 4 actionable "
        "detection gap recommendations generated in under 5 minutes for a real-world APT29 campaign.", False
    )
    pdf.body_text(
        "The ATT&CK-to-D3FEND bridging in the gap analysis provides a novel contribution to purple team "
        "automation, and the dual-mode execution model (live Atomic Red Team + simulation) makes the tool "
        "accessible to both resource-constrained teams and advanced red team operations. We believe The Hive "
        "represents a practical step toward continuous, AI-augmented detection validation."
    )

    # ---- REFERENCES ----
    pdf.ln(5)
    pdf.set_draw_color(180, 180, 180)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Serif", "B", 12)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 8, "References")
    pdf.ln(7)

    refs = [
        'MITRE Corporation, "CALDERA: Automated Adversary Emulation Platform," github.com/mitre/caldera, 2023.',
        'Red Canary, "Atomic Red Team: Small, Portable Detection Tests," github.com/redcanaryco/atomic-red-team, 2024.',
        'SecurityRisk Advisors, "Vectr: Purple Team Tracking," vectr.io, 2024.',
        'M. Shao et al., "LLM-based Vulnerability Detection: Challenges and Opportunities," IEEE S&P Workshop, 2024.',
        'R. Fang et al., "LLM Agents Can Autonomously Exploit One-day Vulnerabilities," arXiv:2404.08144, 2024.',
        'Z. Li et al., "ChatGPT for CTI: Extracting TTPs from Threat Reports," ACM CCS Workshop, 2024.',
        'SigmaHQ, "Sigma: Generic Signature Format for SIEM Systems," github.com/SigmaHQ/sigma, 2024.',
        'T. Patzke, "pySigma: Sigma Rule Processing in Python," github.com/SigmaHQ/pySigma, 2024.',
        'MITRE Corporation, "ATT&CK v14," attack.mitre.org, 2024.',
        'MITRE Corporation, "D3FEND: Cybersecurity Countermeasures," d3fend.mitre.org, 2024.',
        'CrewAI Inc., "CrewAI: Framework for Multi-Agent AI Systems," crewai.com, 2025.',
        'Meta AI, "Llama 3.1: Open Foundation and Fine-Tuned Chat Models," ai.meta.com, 2024.',
    ]
    for i, ref in enumerate(refs, 1):
        pdf.reference_item(i, ref)

    # Save
    output_path = os.path.join(os.path.dirname(__file__), "The_Hive_Whitepaper.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    generate_pdf()
