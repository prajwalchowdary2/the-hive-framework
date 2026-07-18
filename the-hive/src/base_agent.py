"""
Base Agent - Shared base class for all Hive agents.
"""

import json
import re
from typing import Optional
from rich.console import Console
from rich.panel import Panel

console = Console()


class BaseAgent:
    """Base class for all Hive pipeline agents."""

    agent_name: str = "BaseAgent"
    agent_emoji: str = "🔷"

    def __init__(self, settings: dict, attck_mapper=None, llm=None):
        self.settings = settings
        self.attck_mapper = attck_mapper
        self.llm = llm

    def log(self, message: str, style: str = "dim") -> None:
        """Print a styled log message."""
        console.print(f"  [{style}]{self.agent_emoji} [{self.agent_name}] {message}[/{style}]")

    def log_start(self) -> None:
        console.print(Panel(
            f"[bold]{self.agent_emoji} {self.agent_name}[/bold]",
            border_style="cyan", width=50,
        ))

    def log_done(self, summary: str = "") -> None:
        self.log(f"Done. {summary}", style="green")

    def call_llm(self, prompt: str) -> str:
        """Send prompt to the LLM and return the text response."""
        if self.llm is None:
            return self._call_ollama_direct(prompt)

        try:
            response = self.llm.invoke(prompt)
            if hasattr(response, "content"):
                return response.content
            return str(response)
        except Exception as e:
            self.log(f"LLM call failed: {e}", style="red")
            return self._call_ollama_direct(prompt)

    def _call_ollama_direct(self, prompt: str) -> str:
        """Fallback: call Ollama REST API directly."""
        import requests
        url = f"{self.settings.get('ollama_base_url', 'http://localhost:11434')}/api/generate"
        payload = {
            "model": self.settings.get("model", "llama3.1:70b"),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.settings.get("temperature", 0.3),
                "num_predict": self.settings.get("max_tokens", 4096),
            },
        }
        try:
            resp = requests.post(url, json=payload, timeout=300)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            self.log(f"Ollama API error: {e}", style="red")
            return ""

    def parse_json_from_llm(self, text: str) -> Optional[dict]:
        """Extract JSON from LLM response text (handles markdown code blocks)."""
        # Try to find JSON in code blocks
        patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'\{.*\}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1) if '```' in pattern else match.group(0))
                except json.JSONDecodeError:
                    continue

        # Try parsing the whole text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            self.log("Failed to parse JSON from LLM response", style="yellow")
            return None

    def _execute_atomic(self, technique_id: str, test_guid: str = "") -> dict:
        """Execute an Atomic Red Team test (when enabled)."""
        if not self.settings.get("execute_atomics", False):
            return self._simulate_technique(technique_id)

        try:
            from atomic_operator import AtomicOperator
            ao = AtomicOperator()
            atomics_path = self.settings.get("atomic_red_team_path", "./data/atomics")

            self.log(f"Executing atomic test for {technique_id}...")
            results = ao.run(
                techniques=[technique_id],
                atomics_path=atomics_path,
                check_prereqs=True,
                get_prereqs=True,
            )
            return {
                "technique_id": technique_id,
                "execution": "atomic",
                "success": True,
                "results": str(results)[:1000],
            }
        except Exception as e:
            self.log(f"Atomic execution failed for {technique_id}: {e}", style="yellow")
            return self._simulate_technique(technique_id)

    def _simulate_technique(self, technique_id: str) -> dict:
        """Simulate a technique when atomic execution is not available."""
        tech_info = None
        if self.attck_mapper:
            tech_info = self.attck_mapper.get_technique(technique_id)

        name = tech_info["name"] if tech_info else technique_id
        return {
            "technique_id": technique_id,
            "technique_name": name,
            "execution": "simulated",
            "success": True,
            "artifacts": [f"Simulated execution of {name}"],
            "log_entries": [f"Process created: simulated_{technique_id.replace('.', '_')}.exe"],
        }
