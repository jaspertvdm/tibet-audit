"""Singapore PDPA (Personal Data Protection Act) Compliance Checks.

Singapore's PDPA is enforced by the PDPC (Personal Data Protection Commission).
Key features:
- Consent requirements
- Purpose limitation
- Data Protection Officer requirement for certain organizations
- Data breach notification (3 days for significant breaches)
- Do Not Call Registry
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class PDPAConsentCheck(BaseCheck):
    """Check for PDPA consent mechanisms."""

    check_id = "PDPA-001"
    name = "PDPA Consent Obligation"
    description = "Verify consent is obtained before collecting personal data"
    severity = Severity.HIGH
    category = "pdpa"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Search for consent patterns
        consent_terms = ["consent", "pdpa", "user_agreement", "data_consent",
                        "collection_consent", "opt_in"]

        source_files = list(scan_path.glob("**/*.py")) + \
                      list(scan_path.glob("**/*.js")) + \
                      list(scan_path.glob("**/*.ts"))

        found = False
        for sf in source_files[:30]:
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
                message="Consent mechanisms found in code",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No consent mechanism detected",
            recommendation="Implement consent collection before processing personal data",
            references=[
                "PDPA Section 13 - Consent Obligation",
                "https://www.pdpc.gov.sg/"
            ],
            score_impact=10
        )


class PDPADataProtectionOfficerCheck(BaseCheck):
    """Check for Data Protection Officer (DPO) designation."""

    check_id = "PDPA-002"
    name = "Data Protection Officer"
    description = "Verify DPO is designated (required for certain organizations)"
    severity = Severity.HIGH
    category = "pdpa"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for DPO documentation
        patterns = ["dpo*", "data-protection-officer*", "privacy-officer*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        # Check config for DPO settings
        config_files = list(scan_path.glob("**/config*.yaml")) + \
                      list(scan_path.glob("**/config*.json"))

        dpo_in_config = False
        for cf in config_files[:5]:
            try:
                content = cf.read_text().lower()
                if any(term in content for term in ["dpo", "privacy_officer", "data_protection"]):
                    dpo_in_config = True
                    break
            except:
                pass

        if found or dpo_in_config:
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
            recommendation="Designate a Data Protection Officer and publish contact details",
            references=["PDPA Section 11(3) - DPO Requirement"],
            score_impact=8
        )


class PDPABreachNotificationCheck(BaseCheck):
    """Check for breach notification procedure (3 days for significant breaches)."""

    check_id = "PDPA-003"
    name = "Breach Notification (3 Days)"
    description = "Verify breach notification procedure exists (PDPA: 3 calendar days)"
    severity = Severity.CRITICAL
    category = "pdpa"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for breach procedure
        patterns = ["breach*", "incident*", "security-incident*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            # Check if 3 days mentioned
            has_3day = False
            for f in found[:3]:
                try:
                    content = f.read_text().lower()
                    if any(term in content for term in ["3 day", "3day", "three day", "72 hour"]):
                        has_3day = True
                        break
                except:
                    pass

            if has_3day:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message="PDPA-compliant breach notification procedure found",
                    score_impact=0
                )

            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.HIGH,
                message="Breach procedure found but 3-day timeline not specified",
                recommendation="Update to specify 3 calendar day notification requirement",
                score_impact=10
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No breach notification procedure found (PDPA: 3 days for significant breaches)",
            recommendation="Create breach procedure with 3-day notification timeline",
            fix_action=FixAction(
                description="Generate PDPA breach procedure",
                command="tibet-audit template pdpa-breach > docs/breach-procedure-sg.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "PDPA Section 26D - Breach Notification",
                "https://www.pdpc.gov.sg/overview-of-pdpa/data-protection/business-owner/data-breach-management"
            ],
            score_impact=self.score_weight
        )


class PDPADoNotCallCheck(BaseCheck):
    """Check for Do Not Call Registry compliance."""

    check_id = "PDPA-004"
    name = "Do Not Call Compliance"
    description = "Verify Do Not Call Registry is checked for marketing"
    severity = Severity.MEDIUM
    category = "pdpa"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for DNC patterns in code
        dnc_terms = ["do_not_call", "dnc", "marketing_consent", "dnc_registry",
                    "check_dnc", "unsubscribe"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:20]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in dnc_terms):
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
                message="Do Not Call compliance mechanisms found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.LOW,
            message="No Do Not Call Registry check detected",
            recommendation="Implement DNC Registry check before marketing communications",
            references=["PDPA Part IX - Do Not Call Registry"],
            score_impact=5
        )


class PDPARetentionCheck(BaseCheck):
    """Check for data retention limitation."""

    check_id = "PDPA-005"
    name = "Data Retention Limitation"
    description = "Verify data is not retained longer than necessary"
    severity = Severity.HIGH
    category = "pdpa"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for retention documentation
        patterns = ["retention*", "data-lifecycle*", "deletion*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        # Check config for TTL/retention settings
        config_files = list(scan_path.glob("**/config*.yaml")) + \
                      list(scan_path.glob("**/config*.json"))

        retention_in_config = False
        for cf in config_files[:5]:
            try:
                content = cf.read_text().lower()
                if any(term in content for term in ["retention", "ttl", "expir", "delete_after"]):
                    retention_in_config = True
                    break
            except:
                pass

        if found or retention_in_config:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Data retention policies found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No data retention policy found",
            recommendation="Define retention periods and implement automatic deletion",
            references=["PDPA Section 25 - Retention Limitation"],
            score_impact=10
        )


# All PDPA checks
PDPA_CHECKS = [
    PDPAConsentCheck(),
    PDPADataProtectionOfficerCheck(),
    PDPABreachNotificationCheck(),
    PDPADoNotCallCheck(),
    PDPARetentionCheck(),
]
