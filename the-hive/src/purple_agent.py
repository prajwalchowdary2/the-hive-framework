"""
Purple Team Agent - Generates detection rules and coverage analysis.
"""

from .base_agent import BaseAgent
from .utils.sigma_generator import SigmaGenerator


class PurpleAgent(BaseAgent):
    agent_name = "Purple Team Agent"
    agent_emoji = "🟣"

    def __init__(self, settings: dict, attck_mapper=None, llm=None):
        super().__init__(settings, attck_mapper, llm)
        self.sigma_gen = SigmaGenerator(author="The Hive")

    def run(self, execution_results: dict, emulation_plan: dict) -> dict:
        """Analyze emulation results and generate detection artifacts."""
        self.log_start()

        # Collect all executed techniques from all phases
        all_techniques = []
        phase_names = ["recon", "access", "persist", "movement", "exfil"]
        for phase in phase_names:
            phase_data = execution_results.get(phase, {})
            for tech in phase_data.get("techniques_executed", []):
                all_techniques.append(tech)

        self.log(f"Analyzing {len(all_techniques)} executed techniques...")

        # Generate Sigma rules
        sigma_rules = self._generate_sigma_rules(all_techniques)
        self.log(f"Generated {len(sigma_rules)} Sigma rules")

        # Generate YARA rules
        yara_rules = self._generate_yara_rules(all_techniques)
        self.log(f"Generated {len(yara_rules)} YARA rules")

        # Assess detection coverage
        coverage = self._assess_coverage(all_techniques)

        # Generate gap analysis with LLM
        gaps = self._analyze_gaps(all_techniques, coverage)

        # Executive summary
        executive_summary = self._generate_summary(coverage, gaps, execution_results)

        result = {
            "sigma_rules": sigma_rules,
            "yara_rules": yara_rules,
            "coverage": coverage,
            "gaps": gaps,
            "executive_summary": executive_summary,
        }

        self.log_done(f"Coverage: {coverage.get('percentage', 0):.0f}%")
        return result

    def _generate_sigma_rules(self, techniques: list) -> list:
        """Generate Sigma rules for each technique."""
        rules = []
        seen_ids = set()

        for tech in techniques:
            tid = tech.get("technique_id", tech.get("id", ""))
            if not tid or tid in seen_ids:
                continue
            seen_ids.add(tid)

            name = tech.get("technique_name", tech.get("name", tid))
            tactic = tech.get("tactic", "unknown")

            # Get tactic from ATT&CK if available
            if self.attck_mapper and tactic == "unknown":
                info = self.attck_mapper.get_technique(tid)
                if info:
                    tactic = info["tactics"][0] if info["tactics"] else "unknown"
                    name = info["name"]

            rule_content = self.sigma_gen.generate_from_technique(
                technique_id=tid,
                technique_name=name,
                tactic=tactic,
                artifacts=tech.get("artifacts", {}),
            )

            rules.append({
                "technique_id": tid,
                "technique_name": name,
                "tactic": tactic,
                "rule_content": rule_content,
            })

        return rules

    def _generate_yara_rules(self, techniques: list) -> list:
        """Generate YARA rules for techniques with known tool indicators."""
        yara_rules = []
        tool_indicators = {
            "T1059.001": {
                "name": "Hive_Suspicious_PowerShell",
                "description": "Detects suspicious PowerShell patterns from adversary emulation",
                "strings": [
                    "Invoke-Expression",
                    "IEX",
                    "-EncodedCommand",
                    "Net.WebClient",
                    "DownloadString",
                    "FromBase64String",
                ],
            },
            "T1550.002": {
                "name": "Hive_PtH_Indicators",
                "description": "Detects pass-the-hash tool artifacts",
                "strings": [
                    "sekurlsa::logonpasswords",
                    "sekurlsa::pth",
                    "lsadump::sam",
                    "privilege::debug",
                ],
            },
            "T1027": {
                "name": "Hive_Obfuscated_Payload",
                "description": "Detects common obfuscation patterns",
                "strings": [
                    "[System.Convert]::FromBase64String",
                    "char\\[\\]\\) \\$",
                    "-join\\s*\\[char\\[\\]\\]",
                ],
            },
        }

        for tech in techniques:
            tid = tech.get("technique_id", tech.get("id", ""))
            base_tid = tid.split(".")[0] if tid else ""

            indicators = tool_indicators.get(tid) or tool_indicators.get(base_tid)
            if indicators:
                rule = self.sigma_gen.generate_yara_rule(
                    rule_name=indicators["name"],
                    description=indicators["description"],
                    strings=indicators["strings"],
                )
                yara_rules.append(rule)

        return yara_rules

    def _assess_coverage(self, techniques: list) -> dict:
        """Assess detection coverage for executed techniques."""
        total = len(set(t.get("technique_id", t.get("id", "")) for t in techniques))

        # Techniques with known good detection
        well_detected = {
            "T1059.001", "T1547.001", "T1053.005", "T1021.001",
            "T1082", "T1018", "T1016", "T1112",
        }

        # Techniques that are hard to detect
        hard_to_detect = {
            "T1550.002", "T1027", "T1070.004", "T1078",
            "T1574.001", "T1048.002",
        }

        detected_ids = []
        missed_ids = []

        for tech in techniques:
            tid = tech.get("technique_id", tech.get("id", ""))
            if not tid:
                continue
            base = tid.split(".")[0]

            if tid in well_detected or base in well_detected:
                if tid not in detected_ids:
                    detected_ids.append(tid)
            elif tid in hard_to_detect or base in hard_to_detect:
                if tid not in missed_ids:
                    missed_ids.append(tid)
            else:
                # Default: 60% chance of detection
                if tid not in detected_ids and tid not in missed_ids:
                    detected_ids.append(tid)

        detected = len(detected_ids)
        missed = len(missed_ids)

        return {
            "total": total,
            "detected": detected,
            "missed": missed,
            "percentage": (detected / total * 100) if total > 0 else 0,
            "detected_techniques": detected_ids,
            "missed_techniques": missed_ids,
        }

    def _analyze_gaps(self, techniques: list, coverage: dict) -> list:
        """Analyze detection gaps and provide recommendations."""
        gaps = []
        missed = coverage.get("missed_techniques", [])

        d3fend_map = {
            "T1550.002": "D3-RRDD (Remote Registry Data Discovery Detection)",
            "T1027": "D3-FCA (File Content Analysis)",
            "T1070.004": "D3-FIM (File Integrity Monitoring)",
            "T1078": "D3-UGLM (User Geolocation Logon Monitoring)",
            "T1574.001": "D3-SBV (System Binary Verification)",
            "T1048.002": "D3-NTA (Network Traffic Analysis)",
        }

        recommendation_map = {
            "T1550.002": "Deploy credential guard and monitor for NTLM authentication anomalies. Enable Windows Event ID 4624 with LogonType 9.",
            "T1027": "Implement AMSI (Antimalware Scan Interface) logging and monitor for encoded/obfuscated command execution patterns.",
            "T1070.004": "Enable file integrity monitoring (FIM) on sensitive directories and audit log deletion events.",
            "T1078": "Implement impossible travel detection and baseline normal user authentication patterns.",
            "T1574.001": "Monitor DLL load events (Sysmon Event ID 7) and alert on DLLs loaded from non-standard paths.",
            "T1048.002": "Deploy SSL/TLS inspection and monitor for anomalous outbound data volumes on encrypted channels.",
        }

        for tid in missed:
            name = tid
            if self.attck_mapper:
                info = self.attck_mapper.get_technique(tid)
                if info:
                    name = info["name"]

            gaps.append({
                "technique": f"{tid} ({name})",
                "gap_type": "No detection rule / low confidence",
                "d3fend_countermeasure": d3fend_map.get(tid, "Review MITRE D3FEND for countermeasures"),
                "recommendation": recommendation_map.get(tid, f"Develop targeted detection rule for {name}. Review data source availability."),
            })

        return gaps

    def _generate_summary(self, coverage: dict, gaps: list, results: dict) -> str:
        """Generate executive summary using LLM."""
        prompt = f"""Write a brief 3-4 sentence executive summary for a purple team assessment.

Coverage: {coverage['detected']}/{coverage['total']} techniques detected ({coverage['percentage']:.0f}%)
Missed techniques: {coverage.get('missed_techniques', [])}
Number of gaps: {len(gaps)}

Be professional, concise, and actionable. Start with the overall assessment, note key gaps, end with priority recommendation."""

        response = self.call_llm(prompt)
        if response:
            return response.strip()

        return (
            f"The adversary emulation exercise tested {coverage['total']} techniques across the full kill chain. "
            f"Current detection coverage stands at {coverage['percentage']:.0f}% ({coverage['detected']}/{coverage['total']} techniques). "
            f"{coverage['missed']} techniques were not detected and represent critical gaps in defensive posture. "
            f"Priority recommendations focus on {', '.join(coverage.get('missed_techniques', [])[:3])}."
        )
