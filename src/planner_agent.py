"""
Planner Agent - Creates sequenced adversary emulation plans from extracted TTPs.
"""

from .base_agent import BaseAgent
from .utils.attck_mapper import TACTIC_TO_PHASE


class PlannerAgent(BaseAgent):
    agent_name = "Planner Agent"
    agent_emoji = "📋"

    PHASE_ORDER = ["recon", "access", "persist", "movement", "exfil"]

    def run(self, intel_output: dict) -> dict:
        """Create a sequenced emulation plan from Intel Agent output."""
        self.log_start()

        techniques = intel_output.get("techniques", [])
        if not techniques:
            self.log("No techniques to plan. Skipping.", style="yellow")
            return {"phases": [], "execution_order": []}

        self.log(f"Planning emulation for {len(techniques)} techniques...")

        # Group techniques into phases
        phase_groups = self._group_by_phase(techniques)

        # Use LLM to resolve dependencies and sequence
        phases = self._build_phases(phase_groups, intel_output)

        # Flatten execution order
        execution_order = []
        for phase in phases:
            for tech in phase.get("techniques", []):
                execution_order.append(tech["id"])

        result = {
            "threat_actor": intel_output.get("threat_actor", "Unknown"),
            "phases": phases,
            "execution_order": execution_order,
            "total_techniques": len(execution_order),
        }

        self.log_done(f"Planned {len(phases)} phases, {len(execution_order)} techniques")
        return result

    def _group_by_phase(self, techniques: list) -> dict:
        """Group techniques into pipeline phases based on ATT&CK tactics."""
        groups = {phase: [] for phase in self.PHASE_ORDER}

        for tech in techniques:
            tactic = tech.get("tactic", "")
            phase = TACTIC_TO_PHASE.get(tactic, "access")
            if phase in groups:
                groups[phase].append(tech)
            else:
                groups["access"].append(tech)

        return groups

    def _build_phases(self, phase_groups: dict, intel_output: dict) -> list:
        """Build structured phases with dependency resolution."""
        phases = []

        for phase_name in self.PHASE_ORDER:
            techs = phase_groups.get(phase_name, [])
            if not techs:
                continue

            # Limit techniques per phase
            max_per_phase = self.settings.get("max_techniques_per_phase", 5)
            techs = techs[:max_per_phase]

            phase_techs = []
            for tech in techs:
                phase_techs.append({
                    "id": tech["id"],
                    "name": tech.get("name", tech["id"]),
                    "tactic": tech.get("tactic", "unknown"),
                    "description": tech.get("description", ""),
                    "depends_on": self._get_dependencies(tech["id"], phase_name),
                })

            phases.append({
                "name": phase_name,
                "order": self.PHASE_ORDER.index(phase_name),
                "techniques": phase_techs,
            })

        return phases

    def _get_dependencies(self, technique_id: str, current_phase: str) -> list:
        """Determine dependencies for a technique."""
        dep_map = {
            "access": [],
            "persist": ["access"],
            "movement": ["access", "persist"],
            "exfil": ["access"],
        }
        return dep_map.get(current_phase, [])
