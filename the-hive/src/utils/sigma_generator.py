"""
Sigma Rule Generator - Creates valid Sigma detection rules from ATT&CK techniques.
"""

import yaml
from datetime import date
from typing import Optional


# Log source templates for common technique categories
LOG_SOURCES = {
    "process_creation": {"category": "process_creation", "product": "windows"},
    "sysmon": {"product": "windows", "service": "sysmon"},
    "powershell": {"product": "windows", "service": "powershell", "category": "ps_script"},
    "security": {"product": "windows", "service": "security"},
    "registry": {"category": "registry_set", "product": "windows"},
    "network": {"category": "network_connection", "product": "windows"},
    "file": {"category": "file_event", "product": "windows"},
    "dns": {"category": "dns_query", "product": "windows"},
}

# Technique to log source mapping
TECHNIQUE_LOG_SOURCE_MAP = {
    "T1059": "powershell",       # Command & Scripting Interpreter
    "T1059.001": "powershell",   # PowerShell
    "T1059.003": "process_creation",  # Windows Command Shell
    "T1547": "registry",         # Boot/Logon Autostart
    "T1547.001": "registry",     # Registry Run Keys
    "T1053": "security",         # Scheduled Task
    "T1053.005": "security",     # Scheduled Task
    "T1566": "file",             # Phishing
    "T1566.001": "file",         # Spearphishing Attachment
    "T1566.002": "network",      # Spearphishing Link
    "T1021": "security",         # Remote Services
    "T1021.001": "security",     # Remote Desktop
    "T1021.002": "security",     # SMB/Admin Shares
    "T1550": "security",         # Use Alternate Auth Material
    "T1550.002": "security",     # Pass the Hash
    "T1046": "network",          # Network Service Scanning
    "T1018": "process_creation", # Remote System Discovery
    "T1082": "process_creation", # System Information Discovery
    "T1016": "process_creation", # System Network Config Discovery
    "T1048": "network",          # Exfiltration Over Alternative Protocol
    "T1041": "network",          # Exfiltration Over C2
    "T1567": "dns",              # Exfiltration to Cloud Storage
    "T1112": "registry",         # Modify Registry
    "T1027": "file",             # Obfuscated Files
    "T1070": "security",         # Indicator Removal
    "T1070.004": "file",         # File Deletion
    "T1078": "security",         # Valid Accounts
    "T1574": "process_creation", # Hijack Execution Flow / DLL Side-Loading
    "T1190": "network",          # Exploit Public-Facing Application
    "T1570": "network",          # Lateral Tool Transfer
}


class SigmaGenerator:
    """Generates valid Sigma detection rules for ATT&CK techniques."""

    def __init__(self, author: str = "The Hive"):
        self.author = author

    def generate_rule(
        self,
        technique_id: str,
        technique_name: str,
        tactic: str,
        detection_logic: dict,
        log_source_key: Optional[str] = None,
        description: str = "",
    ) -> str:
        """
        Generate a complete Sigma rule as YAML string.

        Args:
            technique_id: ATT&CK T-code (e.g., T1059.001)
            technique_name: Human name (e.g., PowerShell)
            tactic: ATT&CK tactic (e.g., execution)
            detection_logic: Dict with 'selection' and optionally 'condition' keys
            log_source_key: Key from LOG_SOURCES dict
            description: Rule description
        """
        if not log_source_key:
            log_source_key = TECHNIQUE_LOG_SOURCE_MAP.get(technique_id, "process_creation")

        log_source = LOG_SOURCES.get(log_source_key, LOG_SOURCES["process_creation"])

        rule = {
            "title": f"Hive Detection: {technique_name} ({technique_id})",
            "id": self._generate_rule_id(technique_id),
            "status": "experimental",
            "description": description or f"Detects {technique_name} technique ({technique_id}) as observed during adversary emulation by The Hive.",
            "references": [f"https://attack.mitre.org/techniques/{technique_id.replace('.', '/')}/"],
            "author": self.author,
            "date": date.today().strftime("%Y/%m/%d"),
            "tags": [
                f"attack.{tactic.lower().replace(' ', '_')}",
                f"attack.{technique_id.lower()}",
            ],
            "logsource": log_source,
            "detection": detection_logic,
            "falsepositives": ["Legitimate administrative activity"],
            "level": "medium",
        }

        return yaml.dump(rule, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def generate_from_technique(
        self,
        technique_id: str,
        technique_name: str,
        tactic: str,
        artifacts: Optional[dict] = None,
    ) -> str:
        """
        High-level method: generate a Sigma rule based on technique category.
        Uses pre-built detection templates for common techniques.
        """
        templates = self._get_detection_template(technique_id, artifacts or {})
        return self.generate_rule(
            technique_id=technique_id,
            technique_name=technique_name,
            tactic=tactic,
            detection_logic=templates,
        )

    def generate_yara_rule(
        self,
        rule_name: str,
        description: str,
        strings: list,
        condition: str = "any of them",
    ) -> str:
        """Generate a basic YARA rule."""
        string_defs = []
        for i, s in enumerate(strings):
            if s.startswith("{"):  # hex pattern
                string_defs.append(f"        $h{i} = {s}")
            else:
                string_defs.append(f'        $s{i} = "{s}" ascii wide nocase')

        return f"""rule {rule_name}
{{
    meta:
        description = "{description}"
        author = "{self.author}"
        date = "{date.today().strftime('%Y-%m-%d')}"
        reference = "Generated by The Hive"

    strings:
{chr(10).join(string_defs)}

    condition:
        {condition}
}}
"""

    def _generate_rule_id(self, technique_id: str) -> str:
        """Generate a deterministic UUID-like ID for a rule."""
        import hashlib
        h = hashlib.md5(f"hive-{technique_id}".encode()).hexdigest()
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"

    def _get_detection_template(self, technique_id: str, artifacts: dict) -> dict:
        """Return detection logic template based on technique."""
        base_id = technique_id.split(".")[0]

        templates = {
            "T1059": {
                "selection": {"CommandLine|contains": ["-enc", "-nop", "-w hidden", "IEX", "Invoke-Expression", "downloadstring"]},
                "condition": "selection",
            },
            "T1547": {
                "selection": {
                    "TargetObject|contains": [
                        "\\CurrentVersion\\Run",
                        "\\CurrentVersion\\RunOnce",
                    ]
                },
                "condition": "selection",
            },
            "T1053": {
                "selection": {"CommandLine|contains": ["schtasks", "/create", "/sc"]},
                "condition": "selection",
            },
            "T1566": {
                "selection": {"TargetFilename|endswith": [".hta", ".lnk", ".iso", ".vbs", ".js"]},
                "filter": {"TargetFilename|contains": ["\\AppData\\Local\\Temp\\"]},
                "condition": "selection and filter",
            },
            "T1021": {
                "selection": {"EventID": [4624, 4625], "LogonType": [3, 10]},
                "condition": "selection",
            },
            "T1550": {
                "selection": {"EventID": 4624, "LogonType": 9, "LogonProcessName": "seclogo"},
                "condition": "selection",
            },
            "T1046": {
                "selection": {"Image|endswith": ["\\nmap.exe", "\\masscan.exe"], },
                "selection2": {"CommandLine|contains": ["-sS", "-sV", "-p-", "--top-ports"]},
                "condition": "selection or selection2",
            },
            "T1018": {
                "selection": {"CommandLine|contains": ["net view", "nltest", "dsquery", "Get-ADComputer"]},
                "condition": "selection",
            },
            "T1082": {
                "selection": {"CommandLine|contains": ["systeminfo", "hostname", "whoami /all"]},
                "condition": "selection",
            },
            "T1048": {
                "selection": {"DestinationPort|in": [53, 443, 8443], "Initiated": "true"},
                "filter_internal": {"DestinationIp|startswith": ["10.", "192.168.", "172.16."]},
                "condition": "selection and not filter_internal",
            },
            "T1112": {
                "selection": {"EventType": "SetValue", "TargetObject|contains": ["\\Software\\Microsoft\\Windows\\"]},
                "condition": "selection",
            },
            "T1070": {
                "selection": {"CommandLine|contains": ["wevtutil cl", "Clear-EventLog", "Remove-Item"]},
                "condition": "selection",
            },
            "T1574": {
                "selection": {"Image|endswith": [".exe"], "ImageLoaded|endswith": [".dll"]},
                "filter": {"ImageLoaded|startswith": ["C:\\Windows\\System32\\"]},
                "condition": "selection and not filter",
            },
        }

        # Try exact match first, then base technique
        if technique_id in templates:
            return templates[technique_id]
        elif base_id in templates:
            return templates[base_id]
        else:
            # Generic fallback
            return {
                "selection": {"CommandLine|contains": [technique_id]},
                "condition": "selection",
            }
