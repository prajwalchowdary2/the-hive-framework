"""
Operator Agents - Execute adversary kill chain phases.
Each class handles a specific phase of the adversary lifecycle.
"""

from .base_agent import BaseAgent


class ReconAgent(BaseAgent):
    agent_name = "Recon Agent"
    agent_emoji = "🔭"

    def run(self, plan_phase: dict, context: dict = None) -> dict:
        self.log_start()
        techniques = plan_phase.get("techniques", [])
        target_env = self.settings.get("target_environment", {})
        executed = []

        for tech in techniques:
            self.log(f"Executing {tech['id']}: {tech.get('name', '')}")
            result = self._execute_atomic(tech["id"])
            result["name"] = tech.get("name", tech["id"])
            executed.append(result)

        # Use LLM to synthesize recon findings
        hosts = target_env.get("hosts", [])
        prompt = f"""You are a red team recon operator. Based on the following target environment and executed techniques, provide a brief reconnaissance summary.

Target environment: {hosts}
Techniques executed: {[t['id'] for t in techniques]}

Respond with a JSON object:
{{"discovered_hosts": [...], "services": [...], "high_value_targets": [...], "notes": "..."}}"""

        response = self.call_llm(prompt)
        findings = self.parse_json_from_llm(response) or {
            "discovered_hosts": [h["name"] for h in hosts],
            "services": ["SMB (445)", "RDP (3389)", "LDAP (389)", "DNS (53)"],
            "high_value_targets": [h["name"] for h in hosts if h.get("role") in ("domain_controller", "database_server")],
            "notes": "Default reconnaissance findings from target environment config",
        }

        result = {
            "phase": "reconnaissance",
            "techniques_executed": executed,
            "discovered_hosts": findings.get("discovered_hosts", []),
            "services": findings.get("services", []),
            "high_value_targets": findings.get("high_value_targets", []),
        }
        self.log_done(f"Discovered {len(result['discovered_hosts'])} hosts")
        return result


class AccessAgent(BaseAgent):
    agent_name = "Access Agent"
    agent_emoji = "🚪"

    def run(self, plan_phase: dict, context: dict = None) -> dict:
        self.log_start()
        techniques = plan_phase.get("techniques", [])
        executed = []

        for tech in techniques:
            self.log(f"Executing {tech['id']}: {tech.get('name', '')}")
            result = self._execute_atomic(tech["id"])
            result["name"] = tech.get("name", tech["id"])
            executed.append(result)

        target_hosts = (context or {}).get("discovered_hosts", ["WS01"])
        compromised = target_hosts[0] if target_hosts else "WS01"

        result = {
            "phase": "initial_access",
            "techniques_executed": executed,
            "foothold": {"host": compromised, "method": techniques[0].get("name", "Unknown") if techniques else "N/A"},
            "compromised_host": compromised,
        }
        self.log_done(f"Foothold on {compromised}")
        return result


class PersistAgent(BaseAgent):
    agent_name = "Persistence Agent"
    agent_emoji = "🔒"

    def run(self, plan_phase: dict, context: dict = None) -> dict:
        self.log_start()
        techniques = plan_phase.get("techniques", [])
        executed = []
        mechanisms = []

        for tech in techniques:
            self.log(f"Executing {tech['id']}: {tech.get('name', '')}")
            result = self._execute_atomic(tech["id"])
            result["name"] = tech.get("name", tech["id"])
            executed.append(result)
            mechanisms.append({
                "technique": tech["id"],
                "name": tech.get("name", ""),
                "location": self._get_persistence_location(tech["id"]),
                "survives_reboot": True,
            })

        result = {
            "phase": "persistence",
            "techniques_executed": executed,
            "mechanisms": mechanisms,
        }
        self.log_done(f"Established {len(mechanisms)} persistence mechanisms")
        return result

    def _get_persistence_location(self, technique_id: str) -> str:
        locations = {
            "T1547.001": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "T1053.005": "C:\\Windows\\System32\\Tasks\\",
            "T1574.001": "C:\\Program Files\\target_app\\malicious.dll",
            "T1112": "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\",
        }
        if technique_id in locations:
            return locations[technique_id]

        prompt = f"Where does MITRE ATT&CK technique {technique_id} typically establish persistence on Windows or Linux? Answer in one short line (path or registry key)."
        res = self.call_llm(prompt)
        if res and len(res.strip()) < 120:
            return res.strip().replace("\n", " ")

        return "System registry / filesystem autostart"


class MovementAgent(BaseAgent):
    agent_name = "Movement Agent"
    agent_emoji = "🔀"

    def run(self, plan_phase: dict, context: dict = None) -> dict:
        self.log_start()
        techniques = plan_phase.get("techniques", [])
        executed = []

        ctx = context or {}
        source_host = ctx.get("compromised_host", "WS01")
        high_value = ctx.get("high_value_targets", ["DC01", "DB01"])

        for tech in techniques:
            self.log(f"Executing {tech['id']}: {tech.get('name', '')}")
            result = self._execute_atomic(tech["id"])
            result["name"] = tech.get("name", tech["id"])
            executed.append(result)

        # Build movement path
        path = []
        current = source_host
        for target in high_value[:2]:
            tech_name = techniques[0].get("name", "Remote Services") if techniques else "Remote Services"
            path.append({"from": current, "to": target, "technique": tech_name})
            current = target

        compromised = [source_host] + [p["to"] for p in path]

        result = {
            "phase": "lateral_movement",
            "techniques_executed": executed,
            "path": path,
            "compromised_hosts": compromised,
        }
        self.log_done(f"Moved through {len(path)} hops, {len(compromised)} hosts compromised")
        return result


class ExfilAgent(BaseAgent):
    agent_name = "Exfil Agent"
    agent_emoji = "📤"

    def run(self, plan_phase: dict, context: dict = None) -> dict:
        self.log_start()
        techniques = plan_phase.get("techniques", [])
        executed = []

        for tech in techniques:
            self.log(f"Executing {tech['id']}: {tech.get('name', '')}")
            result = self._execute_atomic(tech["id"])
            result["name"] = tech.get("name", tech["id"])
            executed.append(result)

        exfil_channel = "HTTPS (443)" if not techniques else self._get_exfil_channel(techniques[0]["id"])

        result = {
            "phase": "exfiltration",
            "techniques_executed": executed,
            "staged_data": {
                "type": "Simulated sensitive data",
                "volume": "2.3 GB",
                "files": ["patient_records.db", "credentials.txt", "network_map.png"],
            },
            "exfil_channel": exfil_channel,
        }
        self.log_done(f"Exfiltration via {exfil_channel}")
        return result

    def _get_exfil_channel(self, technique_id: str) -> str:
        channels = {
            "T1048": "DNS tunneling (53)",
            "T1048.002": "Asymmetric encrypted non-C2 (443)",
            "T1041": "C2 channel (HTTPS 443)",
            "T1567": "Cloud storage (Google Drive API)",
            "T1567.002": "Cloud storage (OneDrive)",
        }
        if technique_id in channels:
            return channels[technique_id]

        prompt = f"What protocol or channel does MITRE ATT&CK technique {technique_id} use for exfiltration? Answer in one short phrase (e.g. HTTPS port 443, DNS queries)."
        res = self.call_llm(prompt)
        if res and len(res.strip()) < 100:
            return res.strip().replace("\n", " ")

        return "HTTPS (443)"
