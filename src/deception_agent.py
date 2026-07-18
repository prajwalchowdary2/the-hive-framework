"""
Deception Agent - Dynamically deploys honeypots and active defense decoys based on Purple Team gaps.
"""

from .base_agent import BaseAgent


class DeceptionAgent(BaseAgent):
    agent_name = "Deception Agent"
    agent_emoji = "🕸️"

    def run(self, execution_results: dict, plan: dict) -> dict:
        """Analyze gaps and generate targeted deception strategies."""
        self.log_start()

        purple_data = execution_results.get("purple", {})
        gaps = purple_data.get("gaps", [])

        if not gaps:
            self.log("No detection gaps identified. Skipping targeted deception.")
            self.log_done("Deception complete")
            return {"decoys": []}
            
        self.log(f"Analyzing {len(gaps)} detection gaps for targeted deception...")

        decoys = self._generate_decoys(gaps)
        
        # Simulate deployment
        for decoy in decoys:
            self.log(f"Deploying Decoy: {decoy.get('type', 'Unknown')} -> {decoy.get('target', 'Unknown')}")

        self.log_done(f"Deployed {len(decoys)} adaptive deception traps")
        return {"decoys": decoys}

    def _generate_decoys(self, gaps: list) -> list:
        """Use LLM to generate targeted deception techniques based on gaps."""
        
        prompt = f"""You are a senior Active Defense Engineer.
The Purple Team has identified the following detection gaps in our environment.
For each gap, generate a specific honeypot, decoy, or honeytoken that we should deploy to detect this specific ATT&CK technique if an adversary tries it again.

Detection Gaps:
{gaps}

Focus on practical deception techniques:
- For credential access gaps (e.g., LSASS): Deploy fake credentials in memory or fake AD accounts.
- For lateral movement gaps (e.g., SMB): Deploy a fake open SMB share with auditing enabled.
- For discovery gaps: Deploy a fake 'passwords.txt' file that triggers an alert on read.

Return a JSON array of objects, where each object has:
- "technique": The ATT&CK ID it targets
- "type": The category of decoy (e.g., "Honeytoken Account", "Decoy File", "Fake Service")
- "target": The specific name or location of the decoy
- "description": A short explanation of how the trap works

Return ONLY valid JSON. Example:
[
  {{"technique": "T1021.002", "type": "Fake Service", "target": "\\\\FS02\\Admin$", "description": "High interaction honeypot capturing SMB auth attempts"}}
]
"""

        response = self.call_llm(prompt)
        
        try:
            import json
            import re
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(response)
        except Exception as e:
            self.log(f"Failed to parse deception JSON: {e}")
            # Fallback static decoy if LLM fails
            return [{"technique": "Unknown", "type": "Generic Honeypot", "target": "lab.local", "description": "Fallback decoy"}]
