"""
ATT&CK Mapper - MITRE ATT&CK technique lookup and validation utility.
"""

import json
from pathlib import Path
from typing import Optional
from functools import lru_cache
from rich.console import Console

console = Console()

# Kill chain phase ordering
TACTIC_ORDER = [
    "reconnaissance",
    "resource-development",
    "initial-access",
    "execution",
    "persistence",
    "privilege-escalation",
    "defense-evasion",
    "credential-access",
    "discovery",
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
]

# Map tactics to our pipeline phases
TACTIC_TO_PHASE = {
    "reconnaissance": "recon",
    "resource-development": "recon",
    "initial-access": "access",
    "execution": "access",
    "persistence": "persist",
    "privilege-escalation": "persist",
    "defense-evasion": "persist",
    "credential-access": "movement",
    "discovery": "recon",
    "lateral-movement": "movement",
    "collection": "exfil",
    "command-and-control": "exfil",
    "exfiltration": "exfil",
    "impact": "exfil",
}


class ATTCKMapper:
    """Loads and queries the MITRE ATT&CK Enterprise knowledge base."""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self._techniques: dict = {}
        self._tactics: dict = {}
        self._loaded = False

    def load(self) -> None:
        """Load ATT&CK STIX data from JSON file."""
        if self._loaded:
            return

        if not self.data_path.exists():
            console.print(f"[yellow]ATT&CK data not found at {self.data_path}. Run setup.sh first.[/yellow]")
            self._loaded = True
            return

        console.print(f"[dim]Loading ATT&CK data from {self.data_path}...[/dim]")
        with open(self.data_path, "r") as f:
            bundle = json.load(f)

        for obj in bundle.get("objects", []):
            if obj.get("type") == "attack-pattern" and not obj.get("revoked", False):
                ext_refs = obj.get("external_references", [])
                for ref in ext_refs:
                    if ref.get("source_name") == "mitre-attack":
                        tech_id = ref.get("external_id", "")
                        if tech_id.startswith("T"):
                            tactics = []
                            for phase in obj.get("kill_chain_phases", []):
                                if phase.get("kill_chain_name") == "mitre-attack":
                                    tactics.append(phase["phase_name"])

                            self._techniques[tech_id] = {
                                "id": tech_id,
                                "name": obj.get("name", ""),
                                "description": (obj.get("description", "") or "")[:500],
                                "tactics": tactics,
                                "platforms": obj.get("x_mitre_platforms", []),
                                "data_sources": obj.get("x_mitre_data_sources", []),
                                "url": ref.get("url", ""),
                            }
                            break

        self._loaded = True
        console.print(f"[dim]Loaded {len(self._techniques)} ATT&CK techniques.[/dim]")

    def get_technique(self, technique_id: str) -> Optional[dict]:
        """Look up a technique by T-code (e.g., T1566.001)."""
        self.load()
        return self._techniques.get(technique_id)

    def validate_technique_id(self, technique_id: str) -> bool:
        """Check if a T-code exists in ATT&CK."""
        self.load()
        return technique_id in self._techniques

    def get_techniques_by_tactic(self, tactic: str) -> list:
        """Get all techniques for a given tactic."""
        self.load()
        tactic_lower = tactic.lower().replace(" ", "-")
        return [t for t in self._techniques.values() if tactic_lower in t.get("tactics", [])]

    def get_tactic_order(self) -> list:
        """Return the kill chain tactic ordering."""
        return TACTIC_ORDER.copy()

    def get_phase_for_tactic(self, tactic: str) -> str:
        """Map an ATT&CK tactic to a Hive pipeline phase."""
        return TACTIC_TO_PHASE.get(tactic.lower().replace(" ", "-"), "access")

    def get_all_technique_ids(self) -> list:
        """Return all known technique IDs."""
        self.load()
        return list(self._techniques.keys())

    def search_techniques(self, keyword: str) -> list:
        """Search techniques by keyword in name or description."""
        self.load()
        keyword_lower = keyword.lower()
        return [
            t for t in self._techniques.values()
            if keyword_lower in t["name"].lower() or keyword_lower in t.get("description", "").lower()
        ]
