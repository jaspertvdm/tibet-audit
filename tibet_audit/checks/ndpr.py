"""Nigeria NDPR (Nigeria Data Protection Regulation) Compliance Checks.

NDPR was issued by NITDA in 2019, making Nigeria one of the first
African countries with comprehensive data protection. Recently upgraded
to NDPA (Nigeria Data Protection Act) 2023.

Key features:
- Consent requirement
- Data Protection Officer for large processors
- 72-hour breach notification
- Cross-border transfer restrictions
- Annual audit requirements
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class NDPRConsentCheck(BaseCheck):
    """Check for NDPR consent requirements."""

    check_id = "NDPR-001"
    name = "Consent Requirement"
    description = "Verify consent is obtained for data processing"
    severity = Severity.HIGH
    category = "ndpr"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        consent_terms = ["consent", "ndpr", "user_agreement", "data_consent"]

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
            message="No consent mechanism detected",
            recommendation="Implement consent collection before processing Nigerian data",
            references=[
                "NDPR Article 2.3 - Consent",
                "https://nitda.gov.ng/ndpr/"
            ],
            score_impact=12
        )


class NDPRDPOCheck(BaseCheck):
    """Check for Data Protection Officer (required for large processors)."""

    check_id = "NDPR-002"
    name = "Data Protection Officer"
    description = "Verify DPO is designated (required if >10k subjects)"
    severity = Severity.HIGH
    category = "ndpr"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        patterns = ["dpo*", "data-protection-officer*", "privacy-officer*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Data Protection Officer designation found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No DPO designation found",
            recommendation="Designate DPO if processing data of 10,000+ Nigerians",
            references=["NDPR Article 4.1(8) - DPO requirement"],
            score_impact=10
        )


class NDPRBreachNotification72hCheck(BaseCheck):
    """Check for 72-hour breach notification (same as GDPR)."""

    check_id = "NDPR-003"
    name = "72-Hour Breach Notification"
    description = "Verify breach notification within 72 hours"
    severity = Severity.CRITICAL
    category = "ndpr"
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
            message="No breach notification procedure found (NDPR requires 72 hours!)",
            recommendation="Create breach procedure with 72-hour notification timeline",
            fix_action=FixAction(
                description="Generate NDPR breach procedure",
                command="tibet-audit template ndpr-breach > docs/breach-procedure-ng.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["NDPR Article 2.10 - Breach notification"],
            score_impact=self.score_weight
        )


class NDPRAnnualAuditCheck(BaseCheck):
    """Check for annual audit compliance (unique NDPR requirement!)."""

    check_id = "NDPR-004"
    name = "Annual Audit Compliance"
    description = "Verify annual data protection audit is conducted"
    severity = Severity.HIGH
    category = "ndpr"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))
        tibet_available = context.get("tibet_available", False)

        # TIBET provides continuous audit capability
        if tibet_available:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="TIBET provides continuous audit trail - exceeds annual requirement!",
                score_impact=0
            )

        # Look for audit documentation
        patterns = ["audit*", "compliance-report*", "ndpr-audit*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Audit documentation found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No audit documentation found",
            recommendation="Conduct annual NDPR audit and file with NITDA",
            fix_action=FixAction(
                description="Install TIBET for continuous audit capability",
                command="pip install tibet-vault && tibet-audit scan --categories ndpr",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "NDPR Article 4.1(5) - Annual audit requirement",
                "NITDA filing deadline: March 15"
            ],
            score_impact=12
        )


# All NDPR checks
NDPR_CHECKS = [
    NDPRConsentCheck(),
    NDPRDPOCheck(),
    NDPRBreachNotification72hCheck(),
    NDPRAnnualAuditCheck(),
]
