"""Gulf Region Data Protection Laws (Saudi Arabia PDPL, UAE PDPL, etc.)

The Gulf Cooperation Council countries are rapidly adopting data protection:
- Saudi Arabia PDPL (2023) - Very comprehensive
- UAE Federal Decree-Law No. 45 (2021)
- Bahrain PDPL (2019)
- Qatar (pending)

Common themes: consent, cross-border restrictions, breach notification.
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class GulfDataLocalizationCheck(BaseCheck):
    """Check for data localization compliance (strict in Gulf region)."""

    check_id = "GULF-001"
    name = "Data Localization"
    description = "Verify data residency requirements are met"
    severity = Severity.CRITICAL
    category = "gulf"
    score_weight = 25

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for data residency documentation
        patterns = ["data-residency*", "data-localization*", "local-storage*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        # Check config for region settings
        config_files = list(scan_path.glob("**/config*.yaml")) + \
                      list(scan_path.glob("**/config*.json"))

        region_aware = False
        for cf in config_files[:5]:
            try:
                content = cf.read_text().lower()
                if any(term in content for term in ["region", "saudi", "uae", "gulf", "mena", "data_residency"]):
                    region_aware = True
                    break
            except:
                pass

        if found or region_aware:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Data localization awareness detected",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.HIGH,
            message="No data localization documentation found",
            recommendation="Document data residency and ensure Gulf data stays in approved regions",
            references=[
                "Saudi PDPL Article 29 - Cross-border transfer",
                "UAE PDPL Article 22 - Data localization"
            ],
            score_impact=15
        )


class GulfConsentCheck(BaseCheck):
    """Check for explicit consent (required in Gulf region)."""

    check_id = "GULF-002"
    name = "Explicit Consent"
    description = "Verify explicit consent is obtained"
    severity = Severity.HIGH
    category = "gulf"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        consent_terms = ["explicit_consent", "consent", "user_agreement", "موافقة"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:25]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in consent_terms):
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
                message="Consent mechanisms found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No explicit consent mechanism detected",
            recommendation="Implement explicit consent collection",
            references=["Saudi PDPL Article 5 - Consent"],
            score_impact=12
        )


class GulfBreachNotificationCheck(BaseCheck):
    """Check for breach notification (varies by country)."""

    check_id = "GULF-003"
    name = "Breach Notification"
    description = "Verify breach notification procedure exists"
    severity = Severity.CRITICAL
    category = "gulf"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        patterns = ["breach*", "incident*", "security-incident*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Breach notification procedure found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No breach notification procedure found",
            recommendation="Create breach procedure (Saudi: 72 hours, UAE: reasonable time)",
            fix_action=FixAction(
                description="Generate Gulf breach procedure",
                command="tibet-audit template gulf-breach > docs/breach-procedure-gulf.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "Saudi PDPL - Breach notification",
                "UAE PDPL Article 9"
            ],
            score_impact=self.score_weight
        )


class GulfSensitiveDataCheck(BaseCheck):
    """Check for sensitive data handling (very strict in Gulf)."""

    check_id = "GULF-004"
    name = "Sensitive Data Protection"
    description = "Verify sensitive data is handled with extra care"
    severity = Severity.HIGH
    category = "gulf"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))
        tibet_available = context.get("tibet_available", False)

        # TIBET provides cryptographic protection for sensitive data
        if tibet_available:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="TIBET provides cryptographic protection for sensitive data",
                score_impact=0
            )

        # Look for sensitive data handling
        sensitive_terms = ["sensitive_data", "pii", "encrypt", "protected"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:20]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in sensitive_terms):
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
                message="Sensitive data handling detected",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No explicit sensitive data handling detected",
            recommendation="Implement extra protections for sensitive/special category data",
            fix_action=FixAction(
                description="Install TIBET for cryptographic data protection",
                command="pip install tibet-vault",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["Saudi PDPL Article 20 - Sensitive data"],
            score_impact=12
        )


# All Gulf region checks
GULF_CHECKS = [
    GulfDataLocalizationCheck(),
    GulfConsentCheck(),
    GulfBreachNotificationCheck(),
    GulfSensitiveDataCheck(),
]
