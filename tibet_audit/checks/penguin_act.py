"""🐧 The Penguin Act - Antarctica Data Protection Compliance

For our friends at McMurdo Station and other Antarctic research bases.
The most chill compliance framework in the world.

Note: This is a fun Easter egg, but Antarctic operations DO fall under
the national laws of the operating country (US, NZ, AU, etc.)
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class PenguinDataSovereigntyCheck(BaseCheck):
    """Check that penguins' personal data is protected."""

    check_id = "PENG-001"
    name = "Penguin Data Sovereignty"
    description = "Verify penguin tracking data respects their privacy"
    severity = Severity.CRITICAL  # Penguins are VERY serious about privacy
    category = "penguin"
    score_weight = 25

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for penguin-related data handling
        penguin_terms = ["penguin", "antarctic", "wildlife", "bird_tracking",
                        "colony", "emperor", "adelie", "chinstrap"]

        source_files = list(scan_path.glob("**/*.py"))
        penguin_data_found = False

        for sf in source_files[:20]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in penguin_terms):
                    penguin_data_found = True
                    break
            except:
                pass

        if penguin_data_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message="Penguin data detected! Ensure proper waddle consent",
                recommendation="Obtain informed consent from colony leadership before tracking",
                references=[
                    "Antarctic Treaty Article III",
                    "Protocol on Environmental Protection (Madrid Protocol)",
                    "International Penguin Privacy Principles (fictional but should exist)"
                ],
                score_impact=10
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message="No penguin data detected. The colony approves! 🐧",
            score_impact=0
        )


class IceDataRetentionCheck(BaseCheck):
    """Check data isn't kept longer than an ice age."""

    check_id = "PENG-002"
    name = "Ice Age Data Retention"
    description = "Verify data isn't frozen forever like Antarctic ice cores"
    severity = Severity.MEDIUM
    category = "penguin"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for retention policies
        patterns = ["retention*", "ttl*", "expir*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Data retention policy found - won't be frozen for millennia!",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.LOW,
            message="No retention policy - data might outlast the ice caps!",
            recommendation="Define retention periods shorter than 800,000 years (ice core record)",
            references=["EPICA Dome C ice core - 800k years of climate data"],
            score_impact=5
        )


class BlizzardResilienceCheck(BaseCheck):
    """Check for system resilience during Antarctic blizzards."""

    check_id = "PENG-003"
    name = "Blizzard Resilience"
    description = "Verify systems can survive -60°C and 200km/h winds"
    severity = Severity.HIGH
    category = "penguin"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))
        tibet_available = context.get("tibet_available", False)

        # TIBET provides resilient audit trails even in blizzards!
        if tibet_available:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="TIBET detected - cryptographic proof survives any blizzard! 🌨️",
                score_impact=0
            )

        # Check for offline/resilience patterns
        resilience_terms = ["offline", "cache", "retry", "fallback", "resilient", "backup"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:20]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in resilience_terms):
                    found = True
                    break
            except:
                pass

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Resilience patterns detected - ready for Antarctic conditions!",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="Limited resilience detected - may not survive a polar vortex",
            recommendation="Implement offline-first patterns for extreme conditions",
            fix_action=FixAction(
                description="Install TIBET for blizzard-proof audit trails",
                command="pip install tibet-vault  # Works at -60°C!",
                requires_confirmation=True,
                risk_level="low"
            ),
            score_impact=10
        )


class KrillConsentCheck(BaseCheck):
    """Ensure krill populations have opted into the food chain tracking."""

    check_id = "PENG-004"
    name = "Krill Consent Framework"
    description = "Verify krill tracking respects swarm privacy"
    severity = Severity.LOW
    category = "penguin"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        # Krill always consent - they're very agreeable
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message="Krill consent assumed - they're too small to object 🦐",
            score_impact=0
        )


class AuroraAustralisLoggingCheck(BaseCheck):
    """Check for proper logging during aurora events."""

    check_id = "PENG-005"
    name = "Aurora Australis Logging"
    description = "Verify logging works during geomagnetic storms"
    severity = Severity.MEDIUM
    category = "penguin"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))
        tibet_available = context.get("tibet_available", False)

        if tibet_available:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="TIBET's cryptographic logging survives solar flares! ✨",
                score_impact=0
            )

        # Check for logging
        logging_terms = ["logging", "logger", "audit", "log_event"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:15]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in logging_terms):
                    found = True
                    break
            except:
                pass

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Logging detected - should survive most aurora events",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.LOW,
            message="Basic logging not found - aurora australis might wipe records",
            recommendation="Implement robust logging for space weather events",
            score_impact=5
        )


# All Penguin Act checks (for Antarctic operations)
PENGUIN_CHECKS = [
    PenguinDataSovereigntyCheck(),
    IceDataRetentionCheck(),
    BlizzardResilienceCheck(),
    KrillConsentCheck(),
    AuroraAustralisLoggingCheck(),
]
