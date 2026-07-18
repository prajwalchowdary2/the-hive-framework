"""
Intel Agent - Extracts TTPs from raw threat intelligence reports.
"""

import json
from pathlib import Path
from .base_agent import BaseAgent


class IntelAgent(BaseAgent):
    agent_name = "Intel Agent"
    agent_emoji = "🔍"

    def run(self, report_path: str) -> dict:
        """Parse a threat report and extract structured TTPs."""
        self.log_start()

        # Load report
        report = self._load_report(report_path)
        if not report:
            return {"error": "Failed to load report"}

        self.log(f"Analyzing threat report: {report.get('threat_actor', 'Unknown')}")

        # If report already has structured techniques, validate them
        if "known_techniques" in report:
            self.log("Report contains pre-structured techniques. Validating...")
            techniques = self._validate_techniques(report["known_techniques"])
        else:
            # Use LLM to extract techniques from raw text
            self.log("Extracting TTPs from report text using LLM...")
            techniques = self._extract_with_llm(report.get("report_text", ""))

        # Build kill chain ordering
        kill_chain = self._order_kill_chain(techniques)

        result = {
            "threat_actor": report.get("threat_actor", "Unknown"),
            "aliases": report.get("aliases", []),
            "origin": report.get("origin", "Unknown"),
            "targets": report.get("targets", []),
            "tools": report.get("tools", []),
            "techniques": techniques,
            "kill_chain": kill_chain,
        }

        self.log_done(f"Extracted {len(techniques)} techniques")
        return result

    def _load_report(self, path: str) -> dict:
        """Load threat report from JSON file."""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading report: {e}", style="red")
            return {}

    def _validate_techniques(self, technique_ids: list) -> list:
        """Validate technique IDs against ATT&CK database and enrich."""
        techniques = []
        for tid in technique_ids:
            if self.attck_mapper:
                info = self.attck_mapper.get_technique(tid)
                if info:
                    techniques.append({
                        "id": tid,
                        "name": info["name"],
                        "tactic": info["tactics"][0] if info["tactics"] else "unknown",
                        "tactics": info["tactics"],
                        "description": info["description"][:200],
                        "platforms": info.get("platforms", []),
                    })
                    continue

            # Fallback if not in ATT&CK
            techniques.append({
                "id": tid,
                "name": tid,
                "tactic": "unknown",
                "tactics": [],
                "description": "",
                "platforms": [],
            })

        return techniques

    def _extract_with_llm(self, report_text: str) -> list:
        """Use LLM to extract MITRE ATT&CK techniques from narrative text."""
        prompt = f"""You are a cyber threat intelligence analyst. Analyze the following threat report and extract ALL MITRE ATT&CK techniques mentioned or implied.

For each technique, provide:
- technique_id: The ATT&CK T-code (e.g., T1566.001)
- technique_name: The official name
- tactic: The ATT&CK tactic (e.g., initial-access, execution, persistence)
- confidence: high, medium, or low

Return ONLY valid JSON in this format:
{{
  "techniques": [
    {{"technique_id": "T1566.001", "technique_name": "Spearphishing Attachment", "tactic": "initial-access", "confidence": "high"}},
    ...
  ]
}}

THREAT REPORT:
{report_text[:3000]}

Return ONLY the JSON, no other text."""

        response = self.call_llm(prompt)
        parsed = self.parse_json_from_llm(response)

        if not parsed or "techniques" not in parsed:
            self.log("LLM extraction failed, falling back to empty list", style="yellow")
            return []

        # Validate and enrich
        techniques = []
        for t in parsed["techniques"]:
            tid = t.get("technique_id", "")
            entry = {
                "id": tid,
                "name": t.get("technique_name", tid),
                "tactic": t.get("tactic", "unknown"),
                "tactics": [t.get("tactic", "unknown")],
                "description": "",
                "platforms": [],
                "confidence": t.get("confidence", "medium"),
            }

            # Enrich from ATT&CK if available
            if self.attck_mapper:
                info = self.attck_mapper.get_technique(tid)
                if info:
                    entry["name"] = info["name"]
                    entry["tactics"] = info["tactics"]
                    entry["tactic"] = info["tactics"][0] if info["tactics"] else entry["tactic"]
                    entry["description"] = info["description"][:200]
                    entry["platforms"] = info.get("platforms", [])

            techniques.append(entry)

        return techniques

    def _order_kill_chain(self, techniques: list) -> list:
        """Order techniques by kill chain phase."""
        if not self.attck_mapper:
            return [t["id"] for t in techniques]

        tactic_order = self.attck_mapper.get_tactic_order()

        def sort_key(tech):
            tactic = tech.get("tactic", "")
            try:
                return tactic_order.index(tactic)
            except ValueError:
                return 99

        sorted_techs = sorted(techniques, key=sort_key)
        return [t["id"] for t in sorted_techs]
