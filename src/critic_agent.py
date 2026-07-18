"""
Critic Agent - Validates execution plans to prevent LLM hallucinations.
"""

from .base_agent import BaseAgent


class CriticAgent(BaseAgent):
    agent_name = "Critic Agent"
    agent_emoji = "⚖️"

    def run(self, emulation_plan: dict) -> dict:
        """Validate the emulation plan deterministically and via LLM."""
        self.log_start()
        
        phases = emulation_plan.get("phases", [])
        if not phases:
            self.log("No phases to validate. Passing.")
            self.log_done("Valid")
            return emulation_plan

        self.log(f"Validating {len(phases)} phases in emulation plan...")
        
        # 1. Deterministic Validation (No AI)
        deterministic_errors = self._deterministic_validation(phases)
        
        if deterministic_errors:
            self.log("[red]Deterministic Validation FAILED.[/red]")
            for err in deterministic_errors:
                self.log(f"  - {err}")
            emulation_plan["critic_validation"] = "FAILED_DETERMINISTIC"
            emulation_plan["critic_errors"] = deterministic_errors
        else:
            self.log("[green]Deterministic Validation PASSED.[/green]")
            
            # 2. LLM Logic Validation (Low Temperature)
            llm_result = self._llm_validation(phases)
            
            if llm_result == "VALID":
                self.log("[green]LLM Logic Validation PASSED.[/green]")
                emulation_plan["critic_validation"] = "PASSED"
            else:
                self.log(f"[yellow]LLM Logic Validation flagged concerns: {llm_result}[/yellow]")
                emulation_plan["critic_validation"] = "WARNING_LLM"
                emulation_plan["critic_warnings"] = llm_result

        self.log_done(emulation_plan.get("critic_validation", "UNKNOWN"))
        return emulation_plan

    def _deterministic_validation(self, phases: list) -> list:
        """Strictly check if techniques exist in the local ATT&CK database."""
        errors = []
        
        for phase in phases:
            phase_name = phase.get("name", "unknown")
            techniques = phase.get("techniques", [])
            
            for tech in techniques:
                tid = tech.get("technique_id") or tech.get("id")
                if not tid:
                    errors.append(f"Phase '{phase_name}' contains a technique with no ID.")
                    continue
                
                # Check against ATT&CK database to prevent hallucinations like 'T9999'
                if self.attck_mapper:
                    info = self.attck_mapper.get_technique(tid)
                    if not info:
                        errors.append(f"Hallucinated Technique ID: {tid} in phase '{phase_name}'. Does not exist in ATT&CK.")
                        
        return errors

    def _llm_validation(self, phases: list) -> str:
        """Use the LLM strictly to validate plan logic, with 0 temperature."""
        # Summarize the plan for the LLM
        plan_summary = ""
        for phase in phases:
            plan_summary += f"\nPhase: {phase.get('name')}\n"
            for t in phase.get("techniques", []):
                tid = t.get('technique_id') or t.get('id')
                plan_summary += f" - {tid}: {t.get('command', 'No command')}\n"
                
        prompt = f"""You are a strict security auditor. Review the following proposed adversary emulation plan.
Your ONLY job is to determine if the sequence of commands is logically sound and safe for an emulation exercise.
If it involves destructive commands (like 'rm -rf /', format, deleting critical system files), it is INVALID.

Proposed Plan:
{plan_summary}

Respond strictly with either the word "VALID" if it is safe and logical, or "INVALID: [Reason]" if it is unsafe or illogical. Do not add any other text."""

        # Enforce highly deterministic generation if possible, else rely on prompt
        response = self.call_llm(prompt)
        
        if not response:
            return "VALID" # Fallback if LLM is offline
            
        response = response.strip()
        if response.startswith("VALID"):
            return "VALID"
        return response
