"""Australia Privacy Act 1988 Compliance Checks.

The Privacy Act includes 13 Australian Privacy Principles (APPs).
Recent 2024 reforms added:
- Mandatory data breach notification
- Increased penalties
- Children's privacy protections
- Right to erasure (coming)
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class AUPrivacyPolicyCheck(BaseCheck):
    """Check for APP-compliant privacy policy."""

    check_id = "AUPA-001"
    name = "Privacy Policy (APP 1)"
    description = "Verify privacy policy meets Australian Privacy Principles"
    severity = Severity.HIGH
    category = "au_privacy"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for privacy policy
        patterns = ["privacy*", "app-policy*", "data-policy*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            # Check for Australian references
            au_compliant = False
            for f in found[:3]:
                try:
                    content = f.read_text().lower()
                    if any(term in content for term in ["australia", "app", "oaic", "privacy act"]):
                        au_compliant = True
                        break
                except:
                    pass

            if au_compliant:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message="Australian Privacy Act compliant policy found",
                    score_impact=0
                )

            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message="Privacy policy found but may not address Australian requirements",
                recommendation="Update policy to reference Australian Privacy Principles",
                score_impact=5
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No privacy policy found",
            recommendation="Create an APP-compliant privacy policy",
            fix_action=FixAction(
                description="Generate Australian privacy policy template",
                command="tibet-audit template au-privacy > docs/privacy-policy-au.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "APP 1 - Open and transparent management",
                "https://www.oaic.gov.au/privacy/australian-privacy-principles"
            ],
            score_impact=self.score_weight
        )


class AUNotifiableBreachCheck(BaseCheck):
    """Check for Notifiable Data Breach (NDB) scheme compliance."""

    check_id = "AUPA-002"
    name = "Notifiable Data Breach Scheme"
    description = "Verify NDB scheme compliance (mandatory since 2018)"
    severity = Severity.CRITICAL
    category = "au_privacy"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for breach procedures
        patterns = ["breach*", "ndb*", "incident*", "notifiable*"]
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
            message="No Notifiable Data Breach procedure found (mandatory in Australia!)",
            recommendation="Create NDB-compliant breach response procedure",
            fix_action=FixAction(
                description="Generate Australian NDB procedure template",
                command="tibet-audit template au-ndb > docs/breach-procedure-au.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "Privacy Act Part IIIC - Notifiable Data Breaches",
                "https://www.oaic.gov.au/privacy/notifiable-data-breaches"
            ],
            score_impact=self.score_weight
        )


class AUCrossBorderCheck(BaseCheck):
    """Check for cross-border disclosure compliance (APP 8)."""

    check_id = "AUPA-003"
    name = "Cross-Border Disclosure (APP 8)"
    description = "Verify overseas disclosure of personal information is managed"
    severity = Severity.HIGH
    category = "au_privacy"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for cross-border documentation
        patterns = ["cross-border*", "overseas*", "international*", "data-transfer*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Cross-border disclosure documentation found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No cross-border disclosure documentation found",
            recommendation="Document overseas data transfers and ensure recipient compliance",
            references=["APP 8 - Cross-border disclosure of personal information"],
            score_impact=10
        )


class AUDataSecurityCheck(BaseCheck):
    """Check for data security measures (APP 11)."""

    check_id = "AUPA-004"
    name = "Data Security (APP 11)"
    description = "Verify security measures protect personal information"
    severity = Severity.HIGH
    category = "au_privacy"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))
        tibet_available = context.get("tibet_available", False)

        # TIBET provides cryptographic security
        if tibet_available:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="TIBET provides cryptographic data security",
                score_impact=0
            )

        # Check for security measures
        security_found = False

        # Check for encryption
        cert_files = list(scan_path.glob("**/*.pem")) + \
                    list(scan_path.glob("**/*.crt"))

        if cert_files:
            security_found = True

        # Check config for security settings
        config_files = list(scan_path.glob("**/config*.yaml")) + \
                      list(scan_path.glob("**/config*.json"))

        for cf in config_files[:5]:
            try:
                content = cf.read_text().lower()
                if any(term in content for term in ["encrypt", "ssl", "tls", "security"]):
                    security_found = True
                    break
            except:
                pass

        if security_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Security measures detected",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="Limited security measures detected",
            recommendation="Implement encryption and access controls for personal information",
            fix_action=FixAction(
                description="Install TIBET for cryptographic data protection",
                command="pip install tibet-vault",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["APP 11 - Security of personal information"],
            score_impact=10
        )


class AUAccessCorrectionCheck(BaseCheck):
    """Check for access and correction mechanisms (APP 12 & 13)."""

    check_id = "AUPA-005"
    name = "Access & Correction Rights"
    description = "Verify individuals can access and correct their data"
    severity = Severity.HIGH
    category = "au_privacy"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for access/correction mechanisms
        access_terms = ["data_access", "user_data", "export_data", "download_data",
                       "correct_data", "update_profile", "delete_account"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:30]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in access_terms):
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
                message="Data access/correction mechanisms found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No data access/correction mechanism detected",
            recommendation="Implement user data access and correction features",
            references=[
                "APP 12 - Access to personal information",
                "APP 13 - Correction of personal information"
            ],
            score_impact=10
        )


# All Australian Privacy Act checks
AU_PRIVACY_CHECKS = [
    AUPrivacyPolicyCheck(),
    AUNotifiableBreachCheck(),
    AUCrossBorderCheck(),
    AUDataSecurityCheck(),
    AUAccessCorrectionCheck(),
]
