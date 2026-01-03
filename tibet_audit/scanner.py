"""TIBET Audit Scanner - The core scanning engine."""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from .checks import ALL_CHECKS, CheckResult, Status


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
    """

    def __init__(self, checks: Optional[List] = None):
        """Initialize scanner with checks."""
        self.checks = checks or ALL_CHECKS

    def scan(self, path: str = ".", categories: Optional[List[str]] = None) -> ScanResult:
        """
        Run all compliance checks on the given path.

        Args:
            path: Directory to scan
            categories: Optional list of categories to check (e.g., ["gdpr", "ai_act"])

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

        # Run checks
        results = []
        for check in self.checks:
            # Filter by category if specified
            if categories and check.category not in categories:
                continue

            try:
                result = check.run(context)
                results.append(result)
            except Exception as e:
                # Check failed to run - skip it
                results.append(CheckResult(
                    check_id=check.check_id,
                    name=check.name,
                    status=Status.SKIPPED,
                    severity=check.severity,
                    message=f"Check failed to run: {str(e)}",
                    score_impact=0
                ))

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
