"""TIBET Audit Scanner - The core scanning engine."""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Callable
from datetime import datetime
import uuid

from .checks import ALL_CHECKS, CheckResult, Status


# Lynis-style status labels with colors (for Rich console)
STATUS_LABELS = {
    Status.PASSED: ("[green]", "OK"),
    Status.WARNING: ("[yellow]", "WARNING"),
    Status.FAILED: ("[red]", "FAILED"),
    Status.SKIPPED: ("[dim]", "SKIPPED"),
}

# Category display names and emojis
CATEGORY_NAMES = {
    "humotica": ("🏛️ Humotica Three Pillars (A-Grade Gate)", "humotica"),
    "health": ("💚 System Health & Energy", "health"),
    "gdpr": ("🇪🇺 GDPR (EU Privacy)", "gdpr"),
    "ai_act": ("🤖 EU AI Act", "ai_act"),
    "jis": ("🧭 JIS Compliance", "jis"),
    "sovereignty": ("🛰️ Sovereignty & Residency", "sovereignty"),
    "provider": ("🛡️ Provider Security", "provider"),
    "nis2": ("🛡️ NIS2 Directive", "nis2"),
    "ucp": ("🛒 UCP Commerce", "ucp"),
    "pipa": ("🇰🇷 PIPA (Korea)", "pipa"),
    "appi": ("🇯🇵 APPI (Japan)", "appi"),
    "pdpa": ("🇸🇬 PDPA (Singapore)", "pdpa"),
    "au_privacy": ("🇦🇺 Privacy Act (Australia)", "au_privacy"),
    "lgpd": ("🇧🇷 LGPD (Brazil)", "lgpd"),
    "gulf": ("🇸🇦 Gulf PDPL", "gulf"),
    "ndpr": ("🇳🇬 NDPR (Nigeria)", "ndpr"),
    "penguin": ("🐧 Penguin Act (Antarctica)", "penguin"),
}


@dataclass
class ScanResult:
    """Complete scan result."""
    timestamp: datetime
    scan_path: str
    score: int
    grade: str
    passed: int
    warnings: int
    failed: int
    skipped: int
    results: List[CheckResult]
    duration_seconds: float
    scan_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def fixable_count(self) -> int:
        """Count of issues that can be auto-fixed."""
        return sum(1 for r in self.results if r.can_auto_fix and r.status != Status.PASSED)


class TIBETAudit:
    """
    TIBET Audit Scanner

    The Diaper Protocol™ - One command, hands free, compliance done.

    Usage:
        audit = TIBETAudit()
        result = audit.scan("/path/to/project")
        print(f"Score: {result.score}/100 (Grade: {result.grade})")

    For Lynis-style live output:
        result = audit.scan("/path/to/project", live_mode=True)
    """

    def __init__(self, checks: Optional[List] = None):
        """Initialize scanner with checks."""
        self.checks = checks or ALL_CHECKS

    def scan(
        self,
        path: str = ".",
        categories: Optional[List[str]] = None,
        live_mode: bool = False,
        output_callback: Optional[Callable[[str], None]] = None
    ) -> ScanResult:
        """
        Run all compliance checks on the given path.

        Args:
            path: Directory to scan
            categories: Optional list of categories to check (e.g., ["gdpr", "ai_act"])
            live_mode: If True, print Lynis-style live output
            output_callback: Optional callback for live output (default: print to rich console)

        Returns:
            ScanResult with score and all check results
        """
        import time
        start_time = time.time()

        scan_path = Path(path).resolve()

        # Build context for checks
        context = {
            "scan_path": scan_path,
            "tibet_available": self._check_tibet_available(),
        }

        # Get console for live mode output
        console = None
        if live_mode:
            try:
                from rich.console import Console
                console = Console()
            except ImportError:
                live_mode = False

        # Group checks by category for Lynis-style output
        checks_by_category = {}
        for check in self.checks:
            if categories and check.category not in categories:
                continue
            cat = check.category or "general"
            if cat not in checks_by_category:
                checks_by_category[cat] = []
            checks_by_category[cat].append(check)

        # Run checks
        results = []
        current_category = None

        for category, category_checks in checks_by_category.items():
            # Print category header in live mode
            if live_mode and console:
                cat_name, _ = CATEGORY_NAMES.get(category, (f"📋 {category.upper()}", category))
                console.print(f"\n[bold cyan][+] {cat_name}[/]")
                console.print("[cyan]" + "-" * 40 + "[/]")

            for check in category_checks:
                try:
                    result = check.run(context)
                    # Ensure category is set from the check class
                    if result.category is None:
                        result.category = check.category
                    results.append(result)

                    # Print live status
                    if live_mode and console:
                        self._print_check_result(console, result)

                except Exception as e:
                    # Check failed to run - skip it
                    result = CheckResult(
                        check_id=check.check_id,
                        name=check.name,
                        status=Status.SKIPPED,
                        severity=check.severity,
                        category=check.category,
                        message=f"Check failed to run: {str(e)}",
                        score_impact=0
                    )
                    results.append(result)

                    if live_mode and console:
                        self._print_check_result(console, result)

        # Calculate score
        score, grade = self._calculate_score(results)

        # Count by status
        passed = sum(1 for r in results if r.status == Status.PASSED)
        warnings = sum(1 for r in results if r.status == Status.WARNING)
        failed = sum(1 for r in results if r.status == Status.FAILED)
        skipped = sum(1 for r in results if r.status == Status.SKIPPED)

        duration = time.time() - start_time

        return ScanResult(
            timestamp=datetime.now(),
            scan_path=str(scan_path),
            score=score,
            grade=grade,
            passed=passed,
            warnings=warnings,
            failed=failed,
            skipped=skipped,
            results=results,
            duration_seconds=round(duration, 2)
        )

    def _print_check_result(self, console, result: CheckResult):
        """Print a single check result in Lynis style."""
        color, label = STATUS_LABELS.get(result.status, ("[white]", "UNKNOWN"))

        # Truncate name if too long
        name = result.name[:45] if len(result.name) > 45 else result.name

        # Format: "  - Check name                             [ STATUS ]"
        padding = 50 - len(name)
        if padding < 2:
            padding = 2

        console.print(f"  - {name}" + " " * padding + f"{color}[ {label:^8} ][/]")

        # Show details for non-passed checks
        if result.status == Status.WARNING:
            if result.message:
                msg = result.message[:60] if len(result.message) > 60 else result.message
                console.print(f"    [dim]{msg}[/]")
        elif result.status == Status.FAILED:
            if result.message:
                msg = result.message[:60] if len(result.message) > 60 else result.message
                console.print(f"    [red]{msg}[/]")
            if result.recommendation:
                rec = result.recommendation[:55] if len(result.recommendation) > 55 else result.recommendation
                console.print(f"    [green]→ {rec}[/]")

    def _calculate_score(self, results: List[CheckResult]) -> tuple:
        """Calculate compliance score from results."""
        max_score = 100
        deductions = 0

        for result in results:
            if result.status == Status.FAILED:
                deductions += result.score_impact
            elif result.status == Status.WARNING:
                deductions += result.score_impact * 0.5  # Half penalty

        score = max(0, int(max_score - deductions))

        # Calculate grade
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return score, grade

    def _check_tibet_available(self) -> bool:
        """Check if tibet-vault is installed."""
        try:
            import tibet_vault
            return True
        except ImportError:
            return False

    def get_fixable_issues(self, results: List[CheckResult]) -> List[CheckResult]:
        """Get list of issues that can be auto-fixed."""
        return [r for r in results if r.can_auto_fix and r.status != Status.PASSED]
