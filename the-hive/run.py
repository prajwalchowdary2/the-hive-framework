#!/usr/bin/env python3
"""
The Hive - Multi-Agent AI Adversary Emulation Pipeline
======================================================
Feed a threat intelligence report → get automated adversary emulation
+ detection rules + coverage scorecard.

Usage:
    python run.py --report data/threat_reports/apt29.json
    python run.py --report data/threat_reports/apt29.json --phase intel
    python run.py --list-reports
"""

import argparse
import sys
import os
import yaml
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

console = Console()

BANNER = r"""
 _____ _            _   _ _
|_   _| |__   ___  | | | (_)_   _____
  | | | '_ \ / _ \ | |_| | \ \ / / _ \
  | | | | | |  __/ |  _  | |\ V /  __/
  |_| |_| |_|\___| |_| |_|_| \_/ \___|

  Multi-Agent AI Adversary Emulation Pipeline
"""


def load_settings(config_path: str = "config/settings.yaml") -> dict:
    """Load configuration from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        console.print(f"[red]Config file not found: {config_path}[/red]")
        sys.exit(1)
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def list_reports(reports_dir: str) -> None:
    """List available threat intelligence reports."""
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        console.print("[red]No threat reports directory found.[/red]")
        return

    table = Table(title="Available Threat Reports", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Threat Actor", style="red bold")
    table.add_column("Origin", style="yellow")

    import json
    for f in sorted(reports_path.glob("*.json")):
        try:
            with open(f) as fp:
                data = json.load(fp)
            table.add_row(f.name, data.get("threat_actor", "?"), data.get("origin", "?"))
        except Exception:
            table.add_row(f.name, "?", "?")

    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="The Hive - Multi-Agent AI Adversary Emulation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example: python run.py --report data/threat_reports/apt29.json",
    )
    parser.add_argument(
        "--report", "-r",
        type=str,
        help="Path to threat intelligence report (JSON)",
    )
    parser.add_argument(
        "--phase", "-p",
        type=str,
        choices=["intel", "planner", "recon", "access", "persist", "movement", "exfil", "purple", "all"],
        default="all",
        help="Run specific phase only (default: all)",
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/settings.yaml",
        help="Path to config file (default: config/settings.yaml)",
    )
    parser.add_argument(
        "--list-reports",
        action="store_true",
        help="List available threat reports",
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Simulation mode only (no real Atomic Red Team execution)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory (overrides config)",
    )

    args = parser.parse_args()

    # -- Banner --
    console.print(Text(BANNER, style="bold cyan"))
    console.print(
        Panel(
            "[bold white]Adversary Emulation Pipeline[/bold white]\n"
            f"[dim]Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="cyan",
        )
    )

    # -- Load config --
    settings = load_settings(args.config)

    if args.simulate:
        settings["execute_atomics"] = False
        console.print("[yellow]Running in SIMULATION mode (no real atomic execution)[/yellow]\n")

    if args.output:
        settings["output_dir"] = args.output

    # -- List reports --
    if args.list_reports:
        list_reports(settings.get("threat_reports_dir", "./data/threat_reports"))
        return

    # -- Validate report path --
    if not args.report:
        console.print("[red]Error: --report is required. Use --list-reports to see available reports.[/red]")
        parser.print_help()
        sys.exit(1)

    report_path = Path(args.report)
    if not report_path.exists():
        console.print(f"[red]Report file not found: {args.report}[/red]")
        sys.exit(1)

    # -- Create output directory --
    output_dir = Path(settings["output_dir"])
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_output = output_dir / f"run_{run_id}"
    run_output.mkdir(parents=True, exist_ok=True)
    (run_output / "sigma_rules").mkdir(exist_ok=True)
    (run_output / "yara_rules").mkdir(exist_ok=True)
    settings["run_output_dir"] = str(run_output)

    console.print(f"[dim]Report:  {report_path}[/dim]")
    console.print(f"[dim]Output:  {run_output}[/dim]")
    console.print(f"[dim]Model:   {settings['model']}[/dim]")
    console.print(f"[dim]Atomics: {'LIVE' if settings.get('execute_atomics') else 'SIMULATED'}[/dim]")
    console.print()

    # -- Run pipeline --
    from src.pipeline import HivePipeline

    pipeline = HivePipeline(settings)
    results = pipeline.run(str(report_path), phase=args.phase)

    # -- Summary --
    if results and "purple" in results:
        purple = results["purple"]
        coverage = purple.get("coverage", {})

        summary_table = Table(title="Emulation Results", box=box.HEAVY)
        summary_table.add_column("Metric", style="cyan bold")
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Threat Actor", results.get("intel", {}).get("threat_actor", "N/A"))
        summary_table.add_row("Techniques Extracted", str(len(results.get("intel", {}).get("techniques", []))))
        summary_table.add_row("Techniques Executed", str(coverage.get("total", 0)))
        summary_table.add_row("Likely Detected", f"[green]{coverage.get('detected', 0)}[/green]")
        summary_table.add_row("Likely Missed", f"[red]{coverage.get('missed', 0)}[/red]")
        summary_table.add_row("Coverage", f"{coverage.get('percentage', 0):.0f}%")
        summary_table.add_row("Sigma Rules Generated", str(len(purple.get("sigma_rules", []))))
        summary_table.add_row("Output Directory", str(run_output))

        console.print()
        console.print(summary_table)

    console.print(
        Panel(
            "[bold green]Pipeline complete![/bold green]\n"
            f"[dim]Results saved to {run_output}[/dim]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
