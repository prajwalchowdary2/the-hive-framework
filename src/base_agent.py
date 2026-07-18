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
        base_url = self.settings.get('ollama_base_url', 'http://localhost:11434')
        
        # Check if localhost is unreachable and try default gateway (Windows Sandbox / Hyper-V) or 10.0.2.2 (VirtualBox)
        if "localhost" in base_url or "127.0.0.1" in base_url:
            try:
                requests.get(f"{base_url}/api/tags", timeout=1)
            except Exception:
                import subprocess
                import re
                redirected = False
                
                # 1. Try default gateway from ipconfig
                try:
                    out = subprocess.check_output("ipconfig", shell=True).decode(errors='ignore')
                    gateways = re.findall(r"Default Gateway[\s\.:]* ([0-9\.]+)", out)
                    for gw in gateways:
                        if gw and gw != "0.0.0.0":
                            alt_url = base_url.replace("localhost", gw).replace("127.0.0.1", gw)
                            try:
                                requests.get(f"{alt_url}/api/tags", timeout=1)
                                base_url = alt_url
                                redirected = True
                                break
                            except Exception:
                                pass
                except Exception:
                    pass
                    
                # 2. VirtualBox standard NAT gateway fallback
                if not redirected:
                    alt_url = base_url.replace("localhost", "10.0.2.2").replace("127.0.0.1", "10.0.2.2")
                    try:
                        requests.get(f"{alt_url}/api/tags", timeout=1)
                        base_url = alt_url
                    except Exception:
                        pass

        url = f"{base_url}/api/generate"
        payload = {
            "model": self.settings.get("model", "llama3.3:70b"),
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

            import yaml
            import os

            selected_guids = None
            yaml_path = os.path.join(atomics_path, technique_id, f"{technique_id}.yaml")
            if not os.path.exists(yaml_path):
                base_tid = technique_id.split(".")[0]
                yaml_path = os.path.join(atomics_path, base_tid, f"{base_tid}.yaml")

            if os.path.exists(yaml_path):
                try:
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        tests = data.get("atomic_tests", [])
                        
                        guids = []
                        heavy_keywords = ["winpwn", "winpeas", "seatbelt", "watson", "powersploit", "itm4n", "skyark", "systeminfo"]
                        for test in tests:
                            name = test.get("name", "").lower()
                            guid = test.get("auto_generated_guid")
                            supported = test.get("supported_platforms", [])
                            
                            if "windows" not in supported:
                                continue
                                
                            is_heavy = any(kw in name for kw in heavy_keywords)
                            
                            # Also check the actual execution command content for heavy commands
                            executor = test.get("executor", {})
                            command = executor.get("command", "").lower()
                            if any(kw in command for kw in heavy_keywords):
                                is_heavy = True
                                
                            if not is_heavy and guid:
                                guids.append(guid)
                                
                        if guids:
                            selected_guids = guids[:2]
                except Exception as e:
                    self.log(f"Failed to parse atomic YAML: {e}", style="yellow")

            self.log(f"Executing atomic test for {technique_id}...")
            
            run_kwargs = {
                "techniques": [technique_id],
                "atomics_path": atomics_path,
                "get_prereqs": False,
            }
            if selected_guids:
                self.log(f"Selecting lightweight tests: {selected_guids}")
                run_kwargs["test_guids"] = selected_guids
                
            results = ao.run(**run_kwargs)
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
