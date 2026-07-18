"""
Explain Agent - Breaks down the highly technical execution and detection engineering results into a proper human-readable narrative.
"""

from .base_agent import BaseAgent


class ExplainAgent(BaseAgent):
    agent_name = "Explain Agent"
    agent_emoji = "💡"

    def run(self, execution_results: dict, plan: dict) -> dict:
        """Generate an explainability report based on the emulation."""
        self.log_start()

        # Collect techniques
        all_techniques = []
        phase_names = ["recon", "access", "persist", "movement", "exfil"]
        for phase in phase_names:
            phase_data = execution_results.get(phase, {})
            for tech in phase_data.get("techniques_executed", []):
                all_techniques.append(tech)

        purple_data = execution_results.get("purple", {})
        
        self.log(f"Synthesizing narrative for {len(all_techniques)} techniques...")

        # Use LLM to generate narrative
        report_markdown = self._generate_explainability_report(all_techniques, purple_data)
        
        # We will save this in pipeline.py or here, but let's return it as part of the results
        result = {
            "explainability_report": report_markdown
        }

        self.log_done("Explainability narrative generated")
        return result

    def _generate_explainability_report(self, techniques: list, purple_data: dict) -> str:
        """Use LLM to generate a plain-English explanation."""
        
        coverage = purple_data.get("coverage", {})
        gaps = purple_data.get("gaps", [])

        prompt = f"""You are a senior cybersecurity storyteller and explainer.
Based on the following adversary emulation data, generate a clear, executive-level markdown report explaining EXACTLY what happened, why it happened, and how the defenders fared.

DO NOT use simulation language. Treat this as a real, executed operation that just occurred on the network.

Data:
Total Techniques Executed: {len(techniques)}
Detection Coverage: {coverage.get('percentage', 0):.0f}%
Gaps identified: {len(gaps)}

Key Techniques:
{[t.get("name", t.get("id")) for t in techniques[:5]]}...

Please format your response in professional Markdown with the following sections:
# Incident Explanation Report
## Executive Summary
## The Attack Path (What Happened)
## Defensive Posture (How we detected it)
## Root Cause Analysis (Why the gaps exist)

Do not wrap your entire response in a json block, just output raw markdown.
"""

        response = self.call_llm(prompt)
        return response if response else "# Error generating explainability report."
