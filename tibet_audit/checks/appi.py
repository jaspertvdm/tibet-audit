"""Japan APPI (Act on Protection of Personal Information) Compliance Checks.

APPI was significantly amended in 2022 with:
- Stricter breach notification requirements
- New cross-border transfer rules
- Individual rights expansion
- Pseudonymization rules
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class APPIPrivacyPolicyCheck(BaseCheck):
    """Check for APPI-compliant privacy policy."""

    check_id = "APPI-001"
    name = "Privacy Policy (APPI)"
    description = "Verify privacy policy meets APPI requirements"
    severity = Severity.HIGH
    category = "appi"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for privacy policy files
        patterns = ["privacy*", "プライバシー*", "個人情報*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            # Check if it mentions APPI-specific terms
            appi_compliant = False
            for f in found[:3]:
                try:
                    content = f.read_text().lower()
                    if any(term in content for term in ["appi", "japan", "個人情報保護法", "ppc"]):
                        appi_compliant = True
                        break
                except:
                    pass

            if appi_compliant:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message="APPI-aware privacy policy found",
                    score_impact=0
                )

            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message="Privacy policy found but may not be APPI-compliant",
                recommendation="Update privacy policy to address APPI requirements",
                references=["APPI Article 21 - Disclosure of Purpose"],
                score_impact=5
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No privacy policy found",
            recommendation="Create an APPI-compliant privacy policy",
            fix_action=FixAction(
                description="Generate APPI privacy policy template",
                command="tibet-audit template appi-privacy > docs/privacy-policy-japan.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["APPI Article 21", "https://www.ppc.go.jp/en/"],
            score_impact=self.score_weight
        )


class APPIDataHandlingRecordsCheck(BaseCheck):
    """Check for data handling records (required by APPI 2022)."""

    check_id = "APPI-002"
    name = "Data Handling Records"
    description = "Verify records of data handling activities exist"
    severity = Severity.HIGH
    category = "appi"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))
        tibet_available = context.get("tibet_available", False)

        # TIBET provides automatic data handling records!
        if tibet_available:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="TIBET provides cryptographic data handling records",
                score_impact=0
            )

        # Look for manual records
        patterns = ["data-handling*", "processing-records*", "ropa*", "記録*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        # Check for logging in code
        logging_found = False
        source_files = list(scan_path.glob("**/*.py"))
        for sf in source_files[:20]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in ["audit_log", "data_log", "processing_log"]):
                    logging_found = True
                    break
            except:
                pass

        if found or logging_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message="Basic data handling records found",
                recommendation="Consider TIBET for cryptographic proof of data handling",
                fix_action=FixAction(
                    description="Install TIBET for automatic audit trails",
                    command="pip install tibet-vault && tibet-vault init",
                    requires_confirmation=True,
                    risk_level="low"
                ),
                references=["https://pypi.org/project/tibet-vault/"],
                score_impact=8
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No data handling records found (APPI 2022 requires this)",
            recommendation="Implement data handling records or install TIBET",
            fix_action=FixAction(
                description="Install TIBET vault for audit trails",
                command="pip install tibet-vault && tibet-vault init",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "APPI Article 26 - Records",
                "https://pypi.org/project/tibet-vault/"
            ],
            score_impact=self.score_weight
        )


class APPICrossBorderTransferCheck(BaseCheck):
    """Check for cross-border transfer compliance (APPI 2022 strengthened this)."""

    check_id = "APPI-003"
    name = "Cross-Border Transfer Rules"
    description = "Verify cross-border transfers comply with APPI 2022"
    severity = Severity.HIGH
    category = "appi"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for cross-border documentation
        patterns = ["cross-border*", "international-transfer*", "data-transfer*", "越境*"]
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
                if any(term in content for term in ["region", "japan", "jp", "data_residency"]):
                    region_aware = True
                    break
            except:
                pass

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Cross-border transfer documentation found",
                score_impact=0
            )

        if region_aware:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message="Region-aware config found, but no formal documentation",
                recommendation="Document cross-border transfer procedures",
                score_impact=5
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No cross-border transfer documentation found",
            recommendation="Document international data flows and obtain necessary consent",
            references=[
                "APPI Article 28 - Cross-border Transfer",
                "Japan PPC Guidelines on International Transfers"
            ],
            score_impact=10
        )


class APPIPseudonymizationCheck(BaseCheck):
    """Check for pseudonymization capabilities (new in APPI 2022)."""

    check_id = "APPI-004"
    name = "Pseudonymization Support"
    description = "Verify pseudonymization is available for data protection"
    severity = Severity.MEDIUM
    category = "appi"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Search for pseudonymization in code
        pseudo_terms = ["pseudonym", "anonymize", "hash_pii", "mask_data",
                       "tokenize", "仮名", "匿名"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:30]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in pseudo_terms):
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
                message="Pseudonymization/anonymization capabilities found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.LOW,
            message="No pseudonymization detected",
            recommendation="Consider implementing data pseudonymization for enhanced privacy",
            references=["APPI 2022 - Pseudonymously Processed Information"],
            score_impact=5
        )


class APPIOptOutMechanismCheck(BaseCheck):
    """Check for opt-out mechanisms (APPI requires easy opt-out)."""

    check_id = "APPI-005"
    name = "Opt-Out Mechanism"
    description = "Verify users can easily opt-out of data processing"
    severity = Severity.HIGH
    category = "appi"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Search for opt-out in code
        optout_terms = ["opt_out", "optout", "unsubscribe", "withdraw_consent",
                       "delete_data", "オプトアウト", "同意撤回"]

        source_files = list(scan_path.glob("**/*.py")) + \
                      list(scan_path.glob("**/*.js")) + \
                      list(scan_path.glob("**/*.ts"))

        found = False
        for sf in source_files[:30]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in optout_terms):
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
                message="Opt-out mechanism found in code",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No opt-out mechanism detected",
            recommendation="Implement easy opt-out for users (APPI requirement)",
            references=["APPI Article 23 - Opt-out"],
            score_impact=10
        )


# All APPI checks
APPI_CHECKS = [
    APPIPrivacyPolicyCheck(),
    APPIDataHandlingRecordsCheck(),
    APPICrossBorderTransferCheck(),
    APPIPseudonymizationCheck(),
    APPIOptOutMechanismCheck(),
]
