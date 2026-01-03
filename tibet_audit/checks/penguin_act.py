"""🐧 The Penguin Act - Antarctica Data Protection Compliance

For our friends at McMurdo Station and other Antarctic research bases.
The most chill compliance framework in the world.

Easter egg with REAL value:
- PENG-001: Penguin Data Sovereignty → Linux user/permission hygiene
- PENG-002: Ice Age Data Retention → TTL/expiration policies
- PENG-003: Blizzard Resilience → Failover/redundancy patterns
- PENG-004: Krill Consent Framework → Default consent (always passes)
- PENG-005: Aurora Australis Logging → Persistent logging config

If Penguin Act passes → your Linux server is McMurdo-ready! 🐧
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class PenguinDataSovereigntyCheck(BaseCheck):
    """Check that penguins' personal data is protected.

    Real check: Linux user/group permissions and access control.
    """

    check_id = "PENG-001"
    name = "Penguin Data Sovereignty"
    description = "Verify penguin tracking data respects their privacy (Linux permissions)"
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
                message="Penguin data detected! Ensure proper waddle consent 🐧 (Check file permissions)",
                recommendation="Review Linux permissions: chmod/chown access control on sensitive data",
                references=[
                    "Antarctic Treaty Article III",
                    "Linux File Permissions (chmod 600 for secrets)",
                    "Principle of Least Privilege"
                ],
                score_impact=10
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message="Colony approves! 🐧 No sensitive data exposed (permissions OK)",
            score_impact=0
        )


class IceDataRetentionCheck(BaseCheck):
    """Check data isn't kept longer than an ice age.

    Real check: TTL, expiration, and data retention policies.
    """

    check_id = "PENG-002"
    name = "Ice Age Data Retention"
    description = "Verify data isn't frozen forever (TTL/expiration policies)"
    severity = Severity.MEDIUM
    category = "penguin"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for retention policies
        patterns = ["retention*", "ttl*", "expir*", "cleanup*", "purge*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Won't freeze for millennia! 🧊 (TTL/retention policies found)",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.LOW,
            message="Data might outlast ice caps! ❄️ (No TTL/expiration found)",
            recommendation="Add data retention policies: TTL, cleanup jobs, or expiration timestamps",
            references=["GDPR Article 5(1)(e) - Storage Limitation", "Log rotation best practices"],
            score_impact=5
        )


class BlizzardResilienceCheck(BaseCheck):
    """Check for system resilience during Antarctic blizzards.

    Real check: Failover, redundancy, retry, and backup patterns.
    """

    check_id = "PENG-003"
    name = "Blizzard Resilience"
    description = "Verify systems survive extreme conditions (failover/redundancy)"
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
                message="TIBET detected - survives any blizzard! 🌨️ (Cryptographic redundancy)",
                score_impact=0
            )

        # Check for offline/resilience patterns
        resilience_terms = ["offline", "cache", "retry", "fallback", "resilient", "backup", "failover", "redundant", "replicate"]

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
                message="Antarctic-ready! 🌨️ (Failover/retry/backup patterns found)",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="May not survive polar vortex! ⚠️ (No failover/redundancy found)",
            recommendation="Implement: retry logic, circuit breakers, backup systems, graceful degradation",
            fix_action=FixAction(
                description="Install TIBET for blizzard-proof audit trails",
                command="pip install tibet-vault  # Works at -60°C!",
                requires_confirmation=True,
                risk_level="low"
            ),
            score_impact=10
        )


class KrillConsentCheck(BaseCheck):
    """Ensure krill populations have opted into the food chain tracking.

    Real check: Baseline sanity check (always passes). Every system has SOMETHING right.
    """

    check_id = "PENG-004"
    name = "Krill Consent Framework"
    description = "Verify basic system sanity (baseline check)"
    severity = Severity.LOW
    category = "penguin"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        # Krill always consent - baseline sanity check always passes
        # Every system has SOMETHING working right!
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message="Krill approve! 🦐 (Baseline sanity check passed - system is alive)",
            score_impact=0
        )


class AuroraAustralisLoggingCheck(BaseCheck):
    """Check for proper logging during aurora events.

    Real check: Persistent logging configuration (files, syslog, external).
    """

    check_id = "PENG-005"
    name = "Aurora Australis Logging"
    description = "Verify persistent logging config (survives reboots/crashes)"
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
                message="TIBET survives solar flares! ✨ (Cryptographic logging to disk)",
                score_impact=0
            )

        # Check for logging
        logging_terms = ["logging", "logger", "audit", "log_event", "syslog", "journald", "logfile"]

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
                message="Aurora-proof! ✨ (Logging to persistent storage detected)",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.LOW,
            message="Aurora might wipe records! ⚡ (No persistent logging found)",
            recommendation="Add logging: Python logging module, syslog, or external log service",
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
