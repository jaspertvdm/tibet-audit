"""GDPR Compliance Checks."""

import os
from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class GDPRPrivacyPolicyCheck(BaseCheck):
    """Check for privacy policy document."""

    check_id = "GDPR-001"
    name = "Privacy Policy Document"
    description = "Verify a privacy policy document exists"
    severity = Severity.HIGH
    category = "gdpr"
    score_weight = 15

    POLICY_PATTERNS = [
        "privacy-policy*", "privacy_policy*", "privacypolicy*",
        "PRIVACY*", "gdpr*", "GDPR*", "data-protection*"
    ]

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for privacy policy files
        found_files = []
        for pattern in self.POLICY_PATTERNS:
            found_files.extend(scan_path.glob(f"**/{pattern}.md"))
            found_files.extend(scan_path.glob(f"**/{pattern}.txt"))
            found_files.extend(scan_path.glob(f"**/{pattern}.html"))

        if found_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Privacy policy found: {found_files[0].name}",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No privacy policy document found",
            recommendation="Create a privacy-policy.md file in your docs/ folder",
            fix_action=FixAction(
                description="Generate privacy policy template",
                command="tibet-audit template privacy-policy > docs/privacy-policy.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["GDPR Article 13", "https://gdpr.eu/privacy-notice/"],
            score_impact=self.score_weight
        )


class GDPRDataRetentionCheck(BaseCheck):
    """Check for data retention policy."""

    check_id = "GDPR-002"
    name = "Data Retention Policy"
    description = "Verify data retention policies are defined"
    severity = Severity.HIGH
    category = "gdpr"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for retention policy
        retention_patterns = ["retention*", "data-retention*", "RETENTION*"]
        found = []

        for pattern in retention_patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        # Also check config files for retention settings
        config_files = list(scan_path.glob("**/config*.yaml")) + \
                      list(scan_path.glob("**/config*.json")) + \
                      list(scan_path.glob("**/.env*"))

        retention_in_config = False
        for cf in config_files[:5]:  # Check first 5 config files
            try:
                content = cf.read_text().lower()
                if "retention" in content or "ttl" in content:
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
                message="Data retention policy found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No explicit data retention policy found",
            recommendation="Define data retention periods in config or create retention-policy.md",
            fix_action=FixAction(
                description="Generate retention policy template",
                command="tibet-audit template retention-policy > docs/retention-policy.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["GDPR Article 5(1)(e)", "https://gdpr.eu/article-5/"],
            score_impact=8
        )


class GDPRBreachProcedureCheck(BaseCheck):
    """Check for data breach notification procedure."""

    check_id = "GDPR-003"
    name = "Breach Notification Procedure"
    description = "Verify 72-hour breach notification procedure exists"
    severity = Severity.CRITICAL
    category = "gdpr"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for breach procedure
        patterns = ["breach*", "incident*", "security-incident*", "BREACH*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Breach procedure found: {found[0].name}",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No data breach procedure found (GDPR requires 72-hour notification!)",
            recommendation="Create a breach response procedure document",
            fix_action=FixAction(
                description="Generate breach procedure template",
                command="tibet-audit template breach-procedure > docs/breach-procedure.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "GDPR Article 33 - 72 hour notification",
                "https://gdpr.eu/article-33/"
            ],
            score_impact=self.score_weight
        )


class GDPREncryptionCheck(BaseCheck):
    """Check for encryption configuration."""

    check_id = "GDPR-004"
    name = "Data Encryption"
    description = "Verify encryption is configured for sensitive data"
    severity = Severity.HIGH
    category = "gdpr"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for encryption indicators
        encryption_found = False
        evidence = []

        # Check for SSL/TLS certificates
        cert_files = list(scan_path.glob("**/*.pem")) + \
                    list(scan_path.glob("**/*.crt")) + \
                    list(scan_path.glob("**/*.key"))

        if cert_files:
            encryption_found = True
            evidence.append("SSL/TLS certificates found")

        # Check config files for encryption settings
        config_files = list(scan_path.glob("**/config*.yaml")) + \
                      list(scan_path.glob("**/config*.json"))

        for cf in config_files[:5]:
            try:
                content = cf.read_text().lower()
                if any(term in content for term in ["encrypt", "ssl", "tls", "https", "aes"]):
                    encryption_found = True
                    evidence.append(f"Encryption config in {cf.name}")
                    break
            except:
                pass

        if encryption_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Encryption configured: {', '.join(evidence[:2])}",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No encryption configuration detected",
            recommendation="Ensure data at rest and in transit is encrypted",
            references=["GDPR Article 32 - Security of processing"],
            score_impact=10
        )


class GDPRConsentCheck(BaseCheck):
    """Check for consent management."""

    check_id = "GDPR-005"
    name = "Consent Management"
    description = "Verify consent collection mechanisms exist"
    severity = Severity.HIGH
    category = "gdpr"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for consent-related code/config
        consent_found = False

        # Search in source files
        source_files = list(scan_path.glob("**/*.py")) + \
                      list(scan_path.glob("**/*.js")) + \
                      list(scan_path.glob("**/*.ts"))

        for sf in source_files[:20]:  # Check first 20 files
            try:
                content = sf.read_text().lower()
                if any(term in content for term in ["consent", "gdpr", "cookie_consent", "user_consent"]):
                    consent_found = True
                    break
            except:
                pass

        if consent_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Consent management code found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No consent management detected in code",
            recommendation="Implement explicit consent collection before data processing",
            references=["GDPR Article 7 - Conditions for consent"],
            score_impact=10
        )


# All GDPR checks
GDPR_CHECKS = [
    GDPRPrivacyPolicyCheck(),
    GDPRDataRetentionCheck(),
    GDPRBreachProcedureCheck(),
    GDPREncryptionCheck(),
    GDPRConsentCheck(),
]
