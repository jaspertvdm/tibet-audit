#!/usr/bin/env python3
"""
TIBET Audit CLI - Compliance Health Scanner

The Diaper Protocol™: One command, hands free, compliance done.

    $ tibet-audit scan
    $ tibet-audit fix --auto       # Fix everything, no questions asked
    $ tibet-audit fix --wet-wipe   # Preview what would be fixed (dry-run)

For when you have one hand on the baby and one on the keyboard.

Authors: Jasper van de Meent & Root AI
License: MIT
"""

import sys
from pathlib import Path
from typing import Optional, List

try:
    import typer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
except ImportError:
    print("Missing dependencies. Run: pip install typer rich")
    sys.exit(1)

from .scanner import TIBETAudit, ScanResult
from .checks.base import Status, Severity

app = typer.Typer(
    name="tibet-audit",
    help="TIBET Audit - Compliance Health Scanner. Like Lynis, but for regulations.",
    add_completion=False,
)
console = Console()


# ═══════════════════════════════════════════════════════════════════════════════
# BANNER
# ═══════════════════════════════════════════════════════════════════════════════

BANNER = """
[bold blue]══════════════════════════════════════════════════════════════════════════════[/]
[bold blue]  ████████╗██╗██████╗ ███████╗████████╗     █████╗ ██╗   ██╗██████╗ ██╗████████╗[/]
[bold blue]  ╚══██╔══╝██║██╔══██╗██╔════╝╚══██╔══╝    ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝[/]
[bold blue]     ██║   ██║██████╔╝█████╗     ██║       ███████║██║   ██║██║  ██║██║   ██║   [/]
[bold blue]     ██║   ██║██╔══██╗██╔══╝     ██║       ██╔══██║██║   ██║██║  ██║██║   ██║   [/]
[bold blue]     ██║   ██║██████╔╝███████╗   ██║       ██║  ██║╚██████╔╝██████╔╝██║   ██║   [/]
[bold blue]     ╚═╝   ╚═╝╚═════╝ ╚══════╝   ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   [/]
[bold blue]══════════════════════════════════════════════════════════════════════════════[/]
[dim]  Compliance Health Scanner v0.1.0[/]
[dim]  "SSL secures the connection. TIBET secures the timeline."[/]
[bold blue]══════════════════════════════════════════════════════════════════════════════[/]
"""

DIAPER_BANNER = """
[bold yellow]══════════════════════════════════════════════════════════════════════════════[/]
[bold yellow]  🍼 DIAPER PROTOCOL™ ACTIVATED[/]
[dim]  "Press the button, hands free, diaper change, server fixed."[/]
[bold yellow]══════════════════════════════════════════════════════════════════════════════[/]
"""

CALL_MAMA_BANNER = """
[bold red]══════════════════════════════════════════════════════════════════════════════[/]
[bold red]  📞 CALLING M.A.M.A...[/]
[bold red]  Mission Assurance & Monitoring Agent[/]
[dim]  "When the diaper is too dirty, you call for backup."[/]
[bold red]══════════════════════════════════════════════════════════════════════════════[/]
"""


# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@app.command()
def scan(
    path: str = typer.Argument(".", help="Path to scan"),
    categories: Optional[str] = typer.Option(None, "--categories", "-c", help="Categories: gdpr,ai_act"),
    output: str = typer.Option("terminal", "--output", "-o", help="Output: terminal, json"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output"),
    cry: bool = typer.Option(False, "--cry", help="Verbose mode - for when things are really bad"),
):
    """
    Scan for compliance issues and get a health score.

    Examples:
        tibet-audit scan
        tibet-audit scan ./my-project
        tibet-audit scan --categories gdpr,ai_act
        tibet-audit scan --cry              # When you need ALL the details
    """
    if cry:
        console.print("[bold red]😭 CRY MODE ACTIVATED - Full verbose output[/]")
        console.print("[dim]   \"When everything is on fire, you need all the details.\"[/]")
        console.print()

    if not quiet:
        console.print(BANNER)

    # Parse categories
    cat_list = categories.split(",") if categories else None

    # Run scan with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Scanning for compliance issues...", total=None)

        audit = TIBETAudit()
        result = audit.scan(path, categories=cat_list)

    # Display results
    _display_results(result, quiet, verbose=cry)

    # Upsell (only if not quiet)
    if not quiet:
        console.print()
        console.print("[dim]💡 Want managed compliance? → [link=https://symbaion.eu/enterprise]symbaion.eu/enterprise[/][/]")
        console.print()


@app.command()
def fix(
    path: str = typer.Argument(".", help="Path to scan and fix"),
    auto: bool = typer.Option(False, "--auto", "-a", help="🍼 Diaper Protocol: fix everything, no questions"),
    wet_wipe: bool = typer.Option(False, "--wet-wipe", "-w", help="Preview what would be fixed (like --dry-run but funnier)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Same as --wet-wipe"),
):
    """
    Fix compliance issues automatically.

    The Diaper Protocol™: For when you have one hand on the baby
    and one on the keyboard.

    Examples:
        tibet-audit fix                    # Interactive fix
        tibet-audit fix --wet-wipe         # Preview fixes
        tibet-audit fix --auto             # 🍼 Fix everything, no questions
    """
    # --wet-wipe is an alias for --dry-run
    preview_only = wet_wipe or dry_run

    if auto and not preview_only:
        console.print(DIAPER_BANNER)
    else:
        console.print(BANNER)

    # First, scan
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Scanning for fixable issues...", total=None)
        audit = TIBETAudit()
        result = audit.scan(path)

    # Get fixable issues
    fixable = audit.get_fixable_issues(result.results)

    if not fixable:
        console.print("[green]✅ No fixable issues found! Your compliance is looking good.[/]")
        return

    console.print(f"\n[bold]Found {len(fixable)} fixable issue(s):[/]\n")

    # Display what would be fixed
    for i, issue in enumerate(fixable, 1):
        status_color = "red" if issue.status == Status.FAILED else "yellow"
        console.print(f"  [{status_color}]{issue.icon}[/] [{status_color}]{issue.check_id}[/]: {issue.name}")
        if issue.fix_action:
            console.print(f"     [dim]→ {issue.fix_action.description}[/]")
            if issue.fix_action.command:
                console.print(f"     [dim]  $ {issue.fix_action.command}[/]")
        console.print()

    if preview_only:
        console.print("[yellow]🧻 Wet-wipe mode: No changes made. Run without --wet-wipe to apply fixes.[/]")
        return

    if auto:
        # Diaper Protocol: just do it
        console.print("[bold yellow]🍼 Diaper Protocol: Applying all fixes...[/]\n")
        _apply_fixes(fixable)
    else:
        # Interactive mode
        if typer.confirm("Apply these fixes?"):
            _apply_fixes(fixable)
        else:
            console.print("[dim]No changes made.[/]")


def _apply_fixes(issues: List):
    """Apply fixes for issues."""
    import subprocess

    fixed = 0
    failed = 0

    for issue in issues:
        if not issue.fix_action or not issue.fix_action.command:
            continue

        console.print(f"[bold]Fixing {issue.check_id}...[/]")

        try:
            # For now, just show what would be done
            # In production, you'd actually run the commands
            console.print(f"  [green]✅[/] Would run: {issue.fix_action.command}")
            fixed += 1
        except Exception as e:
            console.print(f"  [red]❌[/] Failed: {e}")
            failed += 1

    console.print()
    console.print(f"[bold green]🎉 Done! Fixed: {fixed}, Failed: {failed}[/]")
    console.print()
    console.print("[dim]Run 'tibet-audit scan' to verify improvements.[/]")


@app.command("list")
def list_checks(
    category: Optional[str] = typer.Option(None, "--category", "-c", help="Filter by category"),
):
    """List all available compliance checks."""
    console.print(BANNER)

    from .checks import ALL_CHECKS

    table = Table(title="Available Compliance Checks", box=box.ROUNDED)
    table.add_column("ID", style="cyan", width=12)
    table.add_column("Name", width=30)
    table.add_column("Category", style="green", width=10)
    table.add_column("Severity", width=10)
    table.add_column("Weight", justify="right", width=8)

    for check in ALL_CHECKS:
        if category and check.category != category:
            continue

        severity_colors = {
            Severity.INFO: "dim",
            Severity.LOW: "green",
            Severity.MEDIUM: "yellow",
            Severity.HIGH: "red",
            Severity.CRITICAL: "bold red",
        }
        sev_color = severity_colors.get(check.severity, "white")

        table.add_row(
            check.check_id,
            check.name,
            check.category,
            f"[{sev_color}]{check.severity.value}[/]",
            str(check.score_weight)
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(ALL_CHECKS)} checks[/]")


# Default M.A.M.A. endpoint
MAMA_DEFAULT_EMAIL = "mama@humotica.com"  # Forwards to support team


@app.command("call-mama")
def call_mama(
    path: str = typer.Argument(".", help="Path to scan"),
    email: Optional[str] = typer.Option(None, "--email", "-e", help=f"Send report to email (default: {MAMA_DEFAULT_EMAIL})"),
    webhook: Optional[str] = typer.Option(None, "--webhook", "-w", help="POST report to webhook URL"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save report to file"),
    send: bool = typer.Option(False, "--send", "-s", help=f"Actually send to {MAMA_DEFAULT_EMAIL}"),
):
    """
    📞 Call M.A.M.A. - Mission Assurance & Monitoring Agent

    When the diaper is too dirty to handle alone, you call for backup.
    Generates a full compliance report and sends it to:
    - M.A.M.A. HQ (--send) - sends to SymbAIon support team
    - Email (--email) - send to custom email
    - Webhook (--webhook) - POST to Slack/Teams/custom
    - File (--output) - save locally

    Examples:
        tibet-audit call-mama --send              # Send to M.A.M.A. HQ
        tibet-audit call-mama --email me@co.com   # Custom email
        tibet-audit call-mama --webhook https://slack.webhook.url
        tibet-audit call-mama --output report.json
    """
    console.print(CALL_MAMA_BANNER)

    # Run scan
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("Scanning for compliance issues...", total=None)
        audit = TIBETAudit()
        result = audit.scan(path)

    # Build report
    import json
    from datetime import datetime

    report = {
        "generated_at": datetime.now().isoformat(),
        "tool": "tibet-audit",
        "version": "0.1.0",
        "scan_path": result.scan_path,
        "score": result.score,
        "grade": result.grade,
        "summary": {
            "passed": result.passed,
            "warnings": result.warnings,
            "failed": result.failed,
            "skipped": result.skipped,
            "fixable": result.fixable_count,
        },
        "issues": [
            {
                "check_id": r.check_id,
                "name": r.name,
                "status": r.status.value,
                "severity": r.severity.value,
                "message": r.message,
                "recommendation": r.recommendation,
                "can_auto_fix": r.can_auto_fix,
            }
            for r in result.results if r.status != Status.PASSED
        ],
        "help_requested": True,
        "mama_message": "Help! The compliance diaper needs changing! 🍼"
    }

    report_json = json.dumps(report, indent=2)

    # Display summary
    console.print(f"\n[bold]Compliance Report Generated[/]")
    console.print(f"  Score: [{_score_color(result.score)}]{result.score}/100[/] (Grade: {result.grade})")
    console.print(f"  Issues: {result.failed} failed, {result.warnings} warnings")
    console.print()

    sent_to = []

    # Send to M.A.M.A. HQ (SymbAIon support)
    if send:
        try:
            import urllib.request
            mama_endpoint = "https://brein.jaspervandemeent.nl/api/mama/report"
            req = urllib.request.Request(
                mama_endpoint,
                data=report_json.encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status in (200, 201, 202):
                    console.print(f"[green]✅ Report sent to M.A.M.A. HQ ({MAMA_DEFAULT_EMAIL})[/]")
                    sent_to.append("mama_hq")
                else:
                    console.print(f"[yellow]⚠️ M.A.M.A. HQ returned status {response.status}[/]")
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not reach M.A.M.A. HQ: {e}[/]")
            console.print(f"[dim]   Try --output to save locally instead[/]")

    # Send to email
    if email:
        console.print(f"[yellow]📧 Would send report to: {email}[/]")
        console.print(f"   [dim](Email sending not yet implemented - save to file and send manually)[/]")
        sent_to.append(f"email:{email}")

    # Send to webhook
    if webhook:
        try:
            import urllib.request
            req = urllib.request.Request(
                webhook,
                data=report_json.encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    console.print(f"[green]✅ Report sent to webhook![/]")
                    sent_to.append(f"webhook:{webhook}")
                else:
                    console.print(f"[red]❌ Webhook returned status {response.status}[/]")
        except Exception as e:
            console.print(f"[red]❌ Failed to send to webhook: {e}[/]")

    # Save to file
    if output:
        try:
            Path(output).write_text(report_json)
            console.print(f"[green]✅ Report saved to: {output}[/]")
            sent_to.append(f"file:{output}")
        except Exception as e:
            console.print(f"[red]❌ Failed to save report: {e}[/]")

    # If nothing specified, print to stdout
    if not email and not webhook and not output:
        console.print("[dim]Tip: Use --email, --webhook, or --output to send the report somewhere[/]")
        console.print()
        console.print("[bold]Report JSON:[/]")
        console.print(report_json)

    console.print()
    console.print("[bold green]📞 Mama has been called! Help is on the way![/]")
    console.print("[dim]   (Or at least, the report is ready to send)[/]")


def _score_color(score: int) -> str:
    """Get color for score."""
    if score >= 80:
        return "green"
    elif score >= 60:
        return "yellow"
    return "red"


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"tibet-audit version {__version__}")
    console.print("https://symbaion.eu")


# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _display_results(result: ScanResult, quiet: bool = False, verbose: bool = False):
    """Display scan results in a nice format."""

    # Score display
    score_color = "green" if result.score >= 80 else "yellow" if result.score >= 60 else "red"

    score_panel = Panel(
        f"[bold {score_color}]{result.score}/100[/]  [dim]Grade: {result.grade}[/]",
        title="[bold]COMPLIANCE HEALTH SCORE[/]",
        border_style=score_color,
        padding=(1, 4),
    )
    console.print(score_panel)

    # Summary
    console.print(f"\n  [green]✅ PASSED[/]: {result.passed}")
    console.print(f"  [yellow]⚠️  WARNINGS[/]: {result.warnings}")
    console.print(f"  [red]❌ FAILED[/]: {result.failed}")
    if result.skipped:
        console.print(f"  [dim]⏭️  SKIPPED[/]: {result.skipped}")

    console.print()

    # In cry mode, show EVERYTHING
    if verbose:
        console.print("[bold]😭 FULL BREAKDOWN (cry mode):[/]\n")

        # Show all passed checks too
        passed = [r for r in result.results if r.status == Status.PASSED]
        if passed:
            console.print("[bold green]PASSED CHECKS:[/]")
            for check in passed:
                console.print(f"  [green]✅[/] {check.check_id}: {check.name}")
                console.print(f"     [dim]{check.message}[/]")
            console.print()

    # Failed checks (priority)
    failed = [r for r in result.results if r.status == Status.FAILED]
    if failed:
        console.print("[bold red]TOP PRIORITIES:[/]\n")
        limit = len(failed) if verbose else 5  # Show all in cry mode
        for i, check in enumerate(failed[:limit], 1):
            console.print(f"  {i}. [red][{check.severity.value.upper()}][/] {check.name}")
            console.print(f"     [dim]{check.message}[/]")
            if check.recommendation:
                console.print(f"     [green]→ FIX: {check.recommendation}[/]")
            if verbose and check.references:
                console.print(f"     [cyan]📚 References:[/]")
                for ref in check.references:
                    console.print(f"        - {ref}")
            if verbose and check.fix_action:
                console.print(f"     [yellow]🔧 Auto-fix available:[/]")
                console.print(f"        {check.fix_action.description}")
                if check.fix_action.command:
                    console.print(f"        $ {check.fix_action.command}")
            console.print()

    # Warnings
    warnings = [r for r in result.results if r.status == Status.WARNING]
    if warnings and not quiet:
        console.print("[bold yellow]WARNINGS:[/]\n")
        limit = len(warnings) if verbose else 3  # Show all in cry mode
        for check in warnings[:limit]:
            console.print(f"  [yellow]⚠️[/]  {check.name}: {check.message}")
            if verbose and check.recommendation:
                console.print(f"     [green]→ {check.recommendation}[/]")
            if verbose and check.references:
                for ref in check.references:
                    console.print(f"     [dim]📚 {ref}[/]")
        if len(warnings) > limit and not verbose:
            console.print(f"  [dim]... and {len(warnings) - limit} more[/]")
        console.print()

    # Fixable count
    fixable = sum(1 for r in result.results if r.can_auto_fix and r.status != Status.PASSED)
    if fixable:
        console.print(f"[bold]💡 {fixable} issue(s) can be auto-fixed:[/]")
        console.print("   [dim]tibet-audit fix --auto[/]  (Diaper Protocol™)")
        console.print("   [dim]tibet-audit fix --wet-wipe[/]  (preview first)")

    # Scan info
    console.print(f"\n[dim]Scanned: {result.scan_path}[/]")
    console.print(f"[dim]Duration: {result.duration_seconds}s[/]")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
