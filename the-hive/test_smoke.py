#!/usr/bin/env python3
"""
Quick smoke test — validates that all modules import correctly and
the pipeline can initialize without requiring Ollama/Docker.
Run: python test_smoke.py
"""

import sys
import json
from pathlib import Path

PASS = "✅"
FAIL = "❌"
results = []


def test(name, func):
    try:
        func()
        print(f"  {PASS} {name}")
        results.append(True)
    except Exception as e:
        print(f"  {FAIL} {name}: {e}")
        results.append(False)


print("=" * 50)
print("  THE HIVE — Smoke Test")
print("=" * 50)
print()

# Test 1: Import all modules
def t_imports():
    from src.base_agent import BaseAgent
    from src.intel_agent import IntelAgent
    from src.planner_agent import PlannerAgent
    from src.operators import ReconAgent, AccessAgent, PersistAgent, MovementAgent, ExfilAgent
    from src.purple_agent import PurpleAgent
    from src.pipeline import HivePipeline
    from src.utils.attck_mapper import ATTCKMapper
    from src.utils.sigma_generator import SigmaGenerator
    from src.utils.report_builder import ReportBuilder

test("All modules import", t_imports)

# Test 2: Load config
def t_config():
    import yaml
    with open("config/settings.yaml") as f:
        settings = yaml.safe_load(f)
    assert "model" in settings
    assert "output_dir" in settings

test("Config loads", t_config)

# Test 3: Load agent definitions
def t_agents_yaml():
    import yaml
    with open("config/agents.yaml") as f:
        agents = yaml.safe_load(f)
    expected = ["intel_agent", "planner_agent", "recon_agent", "access_agent",
                "persist_agent", "movement_agent", "exfil_agent", "purple_agent"]
    for name in expected:
        assert name in agents, f"Missing agent: {name}"

test("Agent configs load (8 agents)", t_agents_yaml)

# Test 4: Load threat reports
def t_reports():
    for name in ["apt29", "lazarus", "fin7"]:
        path = Path(f"data/threat_reports/{name}.json")
        assert path.exists(), f"Missing: {path}"
        with open(path) as f:
            data = json.load(f)
        assert "threat_actor" in data
        assert "known_techniques" in data
        assert len(data["known_techniques"]) > 5

test("Threat reports load (3 APTs)", t_reports)

# Test 5: ATT&CK Mapper (without STIX data)
def t_attck_mapper():
    from src.utils.attck_mapper import ATTCKMapper, TACTIC_ORDER, TACTIC_TO_PHASE
    assert len(TACTIC_ORDER) == 14
    assert "initial-access" in TACTIC_TO_PHASE
    mapper = ATTCKMapper("nonexistent.json")
    mapper.load()  # Should not crash

test("ATT&CK Mapper initializes", t_attck_mapper)

# Test 6: Sigma Generator
def t_sigma():
    from src.utils.sigma_generator import SigmaGenerator
    gen = SigmaGenerator(author="TestHive")
    rule = gen.generate_from_technique(
        technique_id="T1059.001",
        technique_name="PowerShell",
        tactic="execution",
    )
    assert "title:" in rule
    assert "T1059.001" in rule
    assert "detection:" in rule

test("Sigma rule generation", t_sigma)

# Test 7: YARA Generator
def t_yara():
    from src.utils.sigma_generator import SigmaGenerator
    gen = SigmaGenerator()
    rule = gen.generate_yara_rule(
        rule_name="Test_Rule",
        description="Test YARA rule",
        strings=["Invoke-Expression", "IEX"],
    )
    assert "rule Test_Rule" in rule
    assert "Invoke-Expression" in rule

test("YARA rule generation", t_yara)

# Test 8: Report Builder
def t_report():
    from src.utils.report_builder import ReportBuilder
    rb = ReportBuilder()
    mock_results = {
        "intel": {"threat_actor": "TEST", "aliases": [], "targets": [], "tools": [], "techniques": []},
        "planner": {"phases": []},
        "purple": {"sigma_rules": [], "yara_rules": [], "coverage": {"total": 5, "detected": 3, "missed": 2, "percentage": 60.0, "detected_techniques": [], "missed_techniques": []}, "gaps": [], "executive_summary": "Test summary"},
    }
    report = rb.build_report(mock_results)
    assert "TEST" in report
    assert "60%" in report

test("Report builder", t_report)

# Test 9: Navigator layer
def t_navigator():
    from src.utils.report_builder import ReportBuilder
    rb = ReportBuilder()
    layer = rb.build_navigator_layer(
        techniques=[{"id": "T1059.001"}, {"id": "T1547.001"}],
        coverage={"detected_techniques": ["T1059.001"], "missed_techniques": ["T1547.001"], "threat_actor": "Test"},
    )
    assert layer["domain"] == "enterprise-attack"
    assert len(layer["techniques"]) == 2

test("ATT&CK Navigator layer", t_navigator)

# Test 10: Intel Agent (dry run)
def t_intel():
    from src.intel_agent import IntelAgent
    agent = IntelAgent(settings={"model": "test", "ollama_base_url": "http://localhost:11434"})
    result = agent._load_report("data/threat_reports/apt29.json")
    assert result["threat_actor"] == "APT29"
    assert len(result["known_techniques"]) == 12

test("Intel Agent loads APT29 report", t_intel)

# Summary
print()
print("=" * 50)
passed = sum(results)
total = len(results)
if passed == total:
    print(f"  ALL {total} TESTS PASSED {PASS}")
else:
    print(f"  {passed}/{total} tests passed, {total - passed} failed {FAIL}")
print("=" * 50)

sys.exit(0 if passed == total else 1)
