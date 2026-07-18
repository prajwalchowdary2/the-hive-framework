#!/usr/bin/env python3
"""Generate a LaTeX-style academic PDF for Pipeline and Architecture Report."""

import os
import sys

os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fpdf import FPDF

class AcademicPDF(FPDF):
    def __init__(self):
        super().__init__(format='A4')
        self.set_auto_page_break(auto=True, margin=25)
        self.section_num = 0
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
            self.cell(0, 8, "The Hive: Pipeline and System Architecture Report", align="C")
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
        roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
        num = roman[self.section_num - 1] if self.section_num <= 8 else str(self.section_num)
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

    def code_block(self, text):
        self.set_font("Mono", "", 8)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(246, 246, 246)
        x = self.l_margin + 5
        w = self.w - self.l_margin - self.r_margin - 10
        self.set_x(x)
        self.multi_cell(w, 4, text, align="L", fill=True)
        self.ln(4)

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


def generate_pdf():
    pdf = AcademicPDF()
    pdf.add_page()
    pdf.title_block(
        "The Hive: Pipeline and System Architecture Report",
        "Deep Technical Architecture, DAG Modeling, and Execution Data Flow"
    )

    pdf.body_text(
        "This report provides an architectural deep-dive into The Hive's system pipeline. It details the internal "
        "mechanics of the Python orchestration engine, the exact data structures passed between agents, and the "
        "Directed Acyclic Graph (DAG) state management that makes the autonomous execution possible."
    )

    # ---- I. SYSTEM ARCHITECTURE ----
    pdf.section("System Architecture Overview")
    pdf.body_text(
        "The system architecture is decoupled into three primary layers: the Ingestion Layer, the Orchestration "
        "Layer (the Pipeline), and the Output Layer. The Orchestration Layer relies entirely on an offline LLM "
        "engine (Ollama running Llama 3) to process natural language without internet dependencies."
    )

    pdf.code_block(
        "                      +---------------------------------+\n"
        "                      |   LOCAL AI ENGINE (OLLAMA)      |\n"
        "                      |   Model: llama3.1:70b           |\n"
        "                      +---------------------------------+\n"
        "                                      ^\n"
        "                                      | (REST API / LangChain)\n"
        "                                      v\n"
        "+----------------+    +---------------------------------+\n"
        "| INPUT LAYER    |    |   ORCHESTRATION LAYER           |\n"
        "| - JSON Reports |--->|   (src/pipeline.py DAG)         |\n"
        "| - PDF CTI      |    |                                 |\n"
        "+----------------+    |  +-------+       +----------+   |\n"
        "                      |  | Intel | ----> | Planner  |   |\n"
        "                      |  +-------+       +----------+   |\n"
        "                      |                       |         |\n"
        "                      |                       v         |\n"
        "                      |  +--------------------------+   |\n"
        "                      |  |   Operator Agent Fleet   |   |\n"
        "                      |  | (Recon, Access, Move...) |   |\n"
        "                      |  +--------------------------+   |\n"
        "                      |                       |         |\n"
        "                      |                       v         |\n"
        "                      |  +-------+       +----------+   |\n"
        "                      |  | Purple| <---- | Telemetry|   |\n"
        "                      |  +-------+       +----------+   |\n"
        "                      +---------------------------------+\n"
        "                                      |\n"
        "                                      v\n"
        "                      +---------------------------------+\n"
        "                      | OUTPUT LAYER                    |\n"
        "                      | - Sigma/YARA Rules              |\n"
        "                      | - Markdown Reports              |\n"
        "                      | - Intermediate JSON State       |\n"
        "                      +---------------------------------+"
    )

    pdf.highlight_box("Zero Cloud Footprint", "Because the architecture relies on local Ollama integration, all data traversing the pipeline remains in local memory or local disk. No external API keys are required for core execution.")

    # ---- II. THE PIPELINE DAG ----
    pdf.section("The Pipeline Engine (src/pipeline.py)")
    pdf.body_text(
        "The `pipeline.py` file contains the `SimulationPipeline` class, which is responsible for state machine "
        "transitions. It enforces a strict Directed Acyclic Graph (DAG) execution model. An agent cannot "
        "execute until its prerequisite agent has successfully returned a structured JSON state object."
    )
    
    pdf.subsection("A. State Management")
    pdf.body_text(
        "The state object is a Python dictionary that grows as it moves through the pipeline. It begins containing "
        "only the raw threat report and ends containing hundreds of execution logs and detection rules. At every "
        "transition, `pipeline.py` writes the state to `intermediate_{step}.json`."
    )

    pdf.code_block(
        "{\n"
        "  \"intel\": { \"techniques\": [\"T1059.001\", \"T1027\"] },\n"
        "  \"plan\": { \"phases\": {\n"
        "      \"access\": [\"T1059.001\"],\n"
        "      \"evasion\": [\"T1027\"]\n"
        "  }},\n"
        "  \"execution_results\": {\n"
        "      \"access\": { \"logs\": [...], \"success\": true }\n"
        "  },\n"
        "  \"purple_team\": {\n"
        "      \"sigma_rules\": [...],\n"
        "      \"gaps\": [...]\n"
        "  }\n"
        "}"
    )

    # ---- III. EXECUTION FLOW ----
    pdf.section("Execution Data Flow")
    
    pdf.subsection("1. Ingestion & Routing")
    pdf.body_text(
        "The pipeline initializes by loading `config/agents.yaml`. This file defines the system prompts, "
        "temperatures, and constraints for the LLMs. The `run.py` script then passes the target JSON report "
        "into the `SimulationPipeline.run()` method."
    )

    pdf.subsection("2. Planning Constraints")
    pdf.body_text(
        "When the Planner Agent receives techniques from the Intel Agent, it runs a dependency validation algorithm. "
        "It maps the techniques to 5 hardcoded phases: Reconnaissance, Initial Access, Persistence, Lateral "
        "Movement, and Exfiltration. If a technique is unsupported, it drops it and logs a warning."
    )

    pdf.subsection("3. Dynamic Instantiation of Operators")
    pdf.body_text(
        "The pipeline loops through the 5 phases dynamically. For each phase that contains techniques, it "
        "dynamically instantiates the correct Operator class (e.g., `ReconAgent`, `AccessAgent`). This prevents "
        "memory bloat, as agents are only loaded into RAM when their specific phase is active."
    )

    # ---- IV. COMPONENT INTERACTIONS ----
    pdf.section("Inter-Component Interaction Protocol")
    pdf.body_text(
        "The Hive avoids unstructured chatter between agents. Instead, it uses a highly structured payload protocol."
    )
    pdf.body_text(
        "1. Request Framing: The pipeline wraps the previous phase's JSON output in a strict prompt template "
        "before querying the LLM.\n"
        "2. JSON Enforcement: The LLM is instructed to respond ONLY in valid JSON. The `pipeline.py` engine "
        "includes an auto-retry mechanism. If the LLM hallucinates markdown or conversational text, the pipeline "
        "strips it or issues a regeneration request.\n"
        "3. Live Integration (Future): The Operator agents contain scaffolding to hook into Atomic Red Team's "
        "`atomic-operator` Python library. In live mode, the JSON structured techniques are passed directly "
        "to the `atomic-operator` execution engine, bridging AI reasoning with deterministic script execution."
    )

    # ---- V. ERROR HANDLING ----
    pdf.section("Fault Tolerance and Error Handling")
    pdf.highlight_box("Pipeline Resilience", "If the LLM fails to generate valid Sigma rules during the Purple Team phase, the pipeline does not crash. It falls back to generating a generic detection scorecard and logs the error in the final report.md.")
    pdf.body_text(
        "The pipeline implements strict exception boundaries around agent invocations. If the Access Agent fails "
        "to simulate an exploit due to LLM context limits, the pipeline logs a 'Phase Failure', preserves the "
        "state, and proceeds to the Persistence phase if applicable. This mimics real-world red teaming where "
        "one failed exploit does not necessarily stop the entire campaign."
    )

    output_path = os.path.join(os.path.dirname(__file__), "The_Hive_Pipeline_and_Architecture_Report.pdf")
    pdf.output(output_path)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    generate_pdf()
