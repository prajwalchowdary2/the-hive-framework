"""
Pipeline Orchestrator - Wires all agents together and runs the full emulation.
"""

import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel

from .utils.attck_mapper import ATTCKMapper
from .utils.report_builder import ReportBuilder
from .intel_agent import IntelAgent
from .planner_agent import PlannerAgent
from .operators import ReconAgent, AccessAgent, PersistAgent, MovementAgent, ExfilAgent
from .purple_agent import PurpleAgent

console = Console()

PHASE_MAP = {
    "intel": 0,
    "planner": 1,
    "recon": 2,
    "access": 3,
    "persist": 4,
    "movement": 5,
    "exfil": 6,
    "purple": 7,
}


class HivePipeline:
    """Orchestrates the full adversary emulation pipeline."""

    def __init__(self, settings: dict):
        self.settings = settings

        # Initialize ATT&CK mapper
        self.attck_mapper = ATTCKMapper(settings.get("attck_data_path", "./data/attck_data/enterprise-attack.json"))
        self.attck_mapper.load()

        # Initialize LLM connection
        self.llm = self._init_llm()

        # Initialize report builder
        self.report_builder = ReportBuilder()

        # Initialize agents
        agent_kwargs = {"settings": settings, "attck_mapper": self.attck_mapper, "llm": self.llm}
        self.agents = {
            "intel": IntelAgent(**agent_kwargs),
            "planner": PlannerAgent(**agent_kwargs),
            "recon": ReconAgent(**agent_kwargs),
            "access": AccessAgent(**agent_kwargs),
            "persist": PersistAgent(**agent_kwargs),
            "movement": MovementAgent(**agent_kwargs),
            "exfil": ExfilAgent(**agent_kwargs),
            "purple": PurpleAgent(**agent_kwargs),
        }

    def _init_llm(self):
        """Initialize Ollama LLM connection."""
        try:
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=self.settings.get("model", "llama3.1:70b"),
                base_url=self.settings.get("ollama_base_url", "http://localhost:11434"),
                temperature=self.settings.get("temperature", 0.3),
                num_predict=self.settings.get("max_tokens", 4096),
            )
        except ImportError:
            console.print("[yellow]langchain-ollama not available. Using direct Ollama API.[/yellow]")
            return None
        except Exception as e:
            console.print(f"[yellow]LLM init warning: {e}. Will use direct API calls.[/yellow]")
            return None

    def run(self, report_path: str, phase: str = "all") -> dict:
        """Run the full emulation pipeline (or a single phase)."""
        results = {}
        output_dir = self.settings.get("run_output_dir", "./output")

        pipeline_steps = [
            ("intel", "Extracting threat intelligence", self._run_intel),
            ("planner", "Building emulation plan", self._run_planner),
            ("recon", "Executing reconnaissance", self._run_recon),
            ("access", "Simulating initial access", self._run_access),
            ("persist", "Establishing persistence", self._run_persist),
            ("movement", "Performing lateral movement", self._run_movement),
            ("exfil", "Simulating exfiltration", self._run_exfil),
            ("purple", "Generating detections & analysis", self._run_purple),
        ]

        # Filter to single phase if requested
        if phase != "all":
            if phase in PHASE_MAP:
                idx = PHASE_MAP[phase]
                # Always need intel and planner for context
                if idx > 1:
                    pipeline_steps = pipeline_steps[:2] + [pipeline_steps[idx]]
                else:
                    pipeline_steps = [pipeline_steps[idx]]
            else:
                console.print(f"[red]Unknown phase: {phase}[/red]")
                return {}

        console.print(Panel(
            f"[bold cyan]Starting Pipeline — {len(pipeline_steps)} phases[/bold cyan]",
            border_style="cyan",
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[bold]{task.completed}/{task.total}"),
            console=console,
        ) as progress:
            task = progress.add_task("Pipeline", total=len(pipeline_steps))

            for step_name, description, runner in pipeline_steps:
                progress.update(task, description=f"[cyan]{description}...")
                try:
                    step_result = runner(report_path, results)
                    results[step_name] = step_result

                    # Save intermediate result
                    self._save_intermediate(output_dir, step_name, step_result)

                except Exception as e:
                    console.print(f"[red]  Error in {step_name}: {e}[/red]")
                    results[step_name] = {"error": str(e)}

                progress.advance(task)

        # Save final artifacts
        console.print("\n[bold]Saving output artifacts...[/bold]")
        self.report_builder.save_all(output_dir, results)

        return results

    def _run_intel(self, report_path: str, results: dict) -> dict:
        return self.agents["intel"].run(report_path)

    def _run_planner(self, report_path: str, results: dict) -> dict:
        return self.agents["planner"].run(results.get("intel", {}))

    def _run_recon(self, report_path: str, results: dict) -> dict:
        plan = results.get("planner", {})
        recon_phase = self._get_phase(plan, "recon")
        return self.agents["recon"].run(recon_phase)

    def _run_access(self, report_path: str, results: dict) -> dict:
        plan = results.get("planner", {})
        access_phase = self._get_phase(plan, "access")
        context = results.get("recon", {})
        return self.agents["access"].run(access_phase, context)

    def _run_persist(self, report_path: str, results: dict) -> dict:
        plan = results.get("planner", {})
        persist_phase = self._get_phase(plan, "persist")
        context = results.get("access", {})
        return self.agents["persist"].run(persist_phase, context)

    def _run_movement(self, report_path: str, results: dict) -> dict:
        plan = results.get("planner", {})
        movement_phase = self._get_phase(plan, "movement")
        context = {
            "compromised_host": results.get("access", {}).get("compromised_host", "WS01"),
            "high_value_targets": results.get("recon", {}).get("high_value_targets", []),
        }
        return self.agents["movement"].run(movement_phase, context)

    def _run_exfil(self, report_path: str, results: dict) -> dict:
        plan = results.get("planner", {})
        exfil_phase = self._get_phase(plan, "exfil")
        context = results.get("movement", {})
        return self.agents["exfil"].run(exfil_phase, context)

    def _run_purple(self, report_path: str, results: dict) -> dict:
        plan = results.get("planner", {})
        return self.agents["purple"].run(results, plan)

    def _get_phase(self, plan: dict, phase_name: str) -> dict:
        """Extract a specific phase from the emulation plan."""
        for phase in plan.get("phases", []):
            if phase.get("name") == phase_name:
                return phase
        return {"name": phase_name, "techniques": []}

    def _save_intermediate(self, output_dir: str, step_name: str, result: dict) -> None:
        """Save intermediate results after each agent."""
        try:
            path = Path(output_dir) / f"intermediate_{step_name}.json"
            with open(path, "w") as f:
                json.dump(result, f, indent=2, default=str)
        except Exception:
            pass
