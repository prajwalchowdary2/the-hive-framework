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

import sys
import os

# Fix Windows console encoding for emoji/unicode output
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import yaml
from pathlib import Path
from datetime import datetime
import random
import time

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


def animated_boot():
    """Crazy forensic animated boot sequence."""
    console.clear()
    
    # Phase 1: Rapid Hex Scroll (Forensic Scan)
    colors = ["cyan", "cyan", "green", "dim cyan"]
    for _ in range(40):
        line = "  ".join("".join(random.choices("0123456789ABCDEF", k=2)) for _ in range(16))
        addr = f"0x{random.randint(0, 0xFFFFFFFF):08X}"
        console.print(f"[dim]{addr}[/dim]  [{random.choice(colors)}]{line}[/]")
        time.sleep(0.03)
        
    console.clear()
    
    # Phase 2: Decrypting Banner
    banner_lines = BANNER.strip("\n").split("\n")
    for line in banner_lines:
        for _ in range(3):
            glitch = "".join(random.choice("!@#$%^&*?<>") if c != " " and random.random() > 0.6 else c for c in line)
            print(f"\r\033[96m{glitch}\033[0m", end="")
            sys.stdout.flush()
            time.sleep(0.04)
        print(f"\r\033[1;96m{line}\033[0m" + " " * 20)
    
    print()
    # Phase 3: Initializing Modules
    modules = [
        "Mounting forensic volumes", 
        "Loading ATT&CK Matrix (709 techniques)", 
        "Initializing Ollama LLM Engine", 
        "Waking up Agent Fleet"
    ]
    for mod in modules:
        console.print(f"[bold green][*][/] {mod}", end="")
        for _ in range(3):
            console.print("[bold green].[/]", end="")
            time.sleep(0.2)
        console.print(" [bold cyan]OK[/]")
        time.sleep(0.1)
    console.print()

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
        "--model", "-m",
        type=str,
        help="LLM Model to use (e.g., llama3.3:70b, llama3.1:8b, mistral). Overrides config.",
    )
    parser.add_argument(
        "--ui", "-u",
        action="store_true",
        help="Launch dashboard in browser after completion",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory (overrides config)",
    )

    args = parser.parse_args()

    # -- Load config --
    settings = load_settings(args.config)

    if args.model:
        settings["model"] = args.model

    if args.simulate:
        settings["execute_atomics"] = False

    if args.output:
        settings["output_dir"] = args.output

    # -- List reports --
    if args.list_reports:
        console.print(Text(BANNER, style="bold cyan"))
        list_reports(settings.get("threat_reports_dir", "./data/threat_reports"))
        return

    # -- Validate report path --
    if not args.report:
        console.print(Text(BANNER, style="bold cyan"))
        console.print("[red]Error: --report is required. Use --list-reports to see available reports.[/red]")
        parser.print_help()
        sys.exit(1)

    report_path = Path(args.report)
    if not report_path.exists():
        console.print(f"[red]Report file not found: {args.report}[/red]")
        sys.exit(1)

    # Run the animated forensic boot sequence
    animated_boot()

    console.print(
        Panel(
            "[bold white]Adversary Emulation Pipeline[/bold white]\n"
            f"[dim]Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            border_style="cyan",
        )
    )

    if args.simulate:
        console.print("[yellow]Running in SIMULATION mode (no real atomic execution)[/yellow]\n")

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

    dashboard_url = "http://localhost:8080/dashboard.html"
    console.print(
        Panel(
            "[bold green]Pipeline complete![/bold green]\n"
            f"[dim]Results saved to {run_output}[/dim]\n"
            f"[cyan]Dashboard available at: {dashboard_url}[/cyan]",
            border_style="green",
        )
    )

    if args.ui:
        import webbrowser
        console.print(f"[bold cyan]Launching dashboard in browser...[/bold cyan]")
        webbrowser.open(dashboard_url)


if __name__ == "__main__":
    main()
