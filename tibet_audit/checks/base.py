"""Base classes for compliance checks."""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Callable


class Severity(Enum):
    """How serious is the issue?"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(Enum):
    """Did the check pass or fail?"""
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class FixAction:
    """An action that can fix a failed check."""
    description: str
    command: Optional[str] = None  # Shell command
    function: Optional[Callable] = None  # Python function
    requires_confirmation: bool = True
    risk_level: str = "low"  # low, medium, high


@dataclass
class CheckResult:
    """Result of running a compliance check."""
    check_id: str
    name: str
    status: Status
    severity: Severity
    message: str
    category: Optional[str] = None
    recommendation: Optional[str] = None
    fix_action: Optional[FixAction] = None
    references: List[str] = field(default_factory=list)
    score_impact: int = 0  # Points deducted if failed

    @property
    def icon(self) -> str:
        """Get status icon."""
        icons = {
            Status.PASSED: "✅",
            Status.WARNING: "⚠️",
            Status.FAILED: "❌",
            Status.SKIPPED: "⏭️",
        }
        return icons.get(self.status, "❓")

    @property
    def can_auto_fix(self) -> bool:
        """Can this issue be auto-fixed?"""
        return self.fix_action is not None


class BaseCheck(ABC):
    """
    Base class for all compliance checks.

    Subclass this to create your own checks:

        class MyCheck(BaseCheck):
            check_id = "MY-001"
            name = "My Custom Check"
            description = "Checks something important"
            severity = Severity.HIGH
            category = "custom"

            def run(self, context: dict) -> CheckResult:
                # Your check logic here
                pass
    """

    check_id: str = "BASE-000"
    name: str = "Base Check"
    description: str = "Override this"
    severity: Severity = Severity.MEDIUM
    category: str = "general"
    score_weight: int = 10

    @abstractmethod
    def run(self, context: dict) -> CheckResult:
        """
        Execute the check and return result.

        Args:
            context: Dictionary with collected system information

        Returns:
            CheckResult with pass/fail status and details
        """
        pass

    def get_fix_action(self) -> Optional[FixAction]:
        """Override to provide auto-fix capability."""
        return None

    def applies_to(self, profile: str) -> bool:
        """Check if this check applies to given profile."""
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.check_id}: {self.name}>"
