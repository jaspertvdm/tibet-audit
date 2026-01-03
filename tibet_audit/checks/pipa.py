"""South Korea PIPA (Personal Information Protection Act) Compliance Checks.

PIPA is often considered stricter than GDPR, with:
- 24-hour breach notification (vs GDPR's 72 hours)
- Mandatory Privacy Officer
- Stricter consent requirements
- Data localization considerations
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class PIPAPrivacyOfficerCheck(BaseCheck):
    """Check for designated Privacy Officer (required by PIPA)."""

    check_id = "PIPA-001"
    name = "Privacy Officer Designation"
    description = "Verify a Privacy Officer is designated (mandatory in Korea)"
    severity = Severity.CRITICAL
    category = "pipa"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for privacy officer documentation
        patterns = ["privacy-officer*", "dpo*", "cpo*", "PRIVACY_OFFICER*", "개인정보*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        # Check config files for privacy officer settings
        config_files = list(scan_path.glob("**/config*.yaml")) + \
                      list(scan_path.glob("**/config*.json"))

        officer_in_config = False
        for cf in config_files[:5]:
            try:
                content = cf.read_text().lower()
                if any(term in content for term in ["privacy_officer", "dpo", "cpo_email"]):
                    officer_in_config = True
                    break
            except:
                pass

        if found or officer_in_config:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Privacy Officer designation found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No Privacy Officer designation found (PIPA requires this!)",
            recommendation="Designate a Privacy Officer and document their contact info",
            fix_action=FixAction(
                description="Generate Privacy Officer template",
                command="tibet-audit template privacy-officer > docs/privacy-officer.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "PIPA Article 31 - Privacy Officer",
                "https://www.pipc.go.kr/eng/"
            ],
            score_impact=self.score_weight
        )


class PIPABreachNotification24hCheck(BaseCheck):
    """Check for 24-hour breach notification procedure (PIPA is stricter than GDPR!)."""

    check_id = "PIPA-002"
    name = "24-Hour Breach Notification"
    description = "Verify rapid breach notification procedure (PIPA: 24 hours, not 72!)"
    severity = Severity.CRITICAL
    category = "pipa"
    score_weight = 25

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for breach procedure with 24h mention
        patterns = ["breach*", "incident*", "security-incident*", "침해*"]
        found_files = []

        for pattern in patterns:
            found_files.extend(scan_path.glob(f"**/{pattern}.*"))

        # Check if any mention 24 hours
        has_24h = False
        for f in found_files[:5]:
            try:
                content = f.read_text().lower()
                if any(term in content for term in ["24 hour", "24hour", "24h", "24시간"]):
                    has_24h = True
                    break
            except:
                pass

        if has_24h:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="24-hour breach notification procedure found",
                score_impact=0
            )

        if found_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.HIGH,
                message="Breach procedure found, but no 24-hour timeline specified",
                recommendation="Update breach procedure to specify 24-hour notification (PIPA requirement)",
                references=["PIPA Article 34 - Breach Notification"],
                score_impact=12
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No breach notification procedure found (PIPA requires 24-hour notification!)",
            recommendation="Create breach procedure with 24-hour notification timeline",
            fix_action=FixAction(
                description="Generate PIPA-compliant breach procedure",
                command="tibet-audit template pipa-breach > docs/breach-procedure-24h.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "PIPA Article 34 - 24 hour notification",
                "https://www.pipc.go.kr/eng/"
            ],
            score_impact=self.score_weight
        )


class PIPAConsentCheck(BaseCheck):
    """Check for explicit consent mechanisms (PIPA requires opt-in, not opt-out)."""

    check_id = "PIPA-003"
    name = "Explicit Consent (Opt-in)"
    description = "Verify explicit opt-in consent mechanisms (PIPA is stricter than GDPR)"
    severity = Severity.HIGH
    category = "pipa"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Search for consent patterns in code
        consent_patterns = ["explicit_consent", "opt_in", "consent_required",
                          "user_consent", "동의", "명시적"]
        found = False

        source_files = list(scan_path.glob("**/*.py")) + \
                      list(scan_path.glob("**/*.js")) + \
                      list(scan_path.glob("**/*.ts"))

        for sf in source_files[:30]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in consent_patterns):
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
                message="Explicit consent mechanisms found in code",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No explicit opt-in consent mechanism detected",
            recommendation="Implement explicit consent collection before any data processing",
            references=["PIPA Article 15 - Consent Requirements"],
            score_impact=10
        )


class PIPADataLocalizationCheck(BaseCheck):
    """Check for data localization awareness (Korea has strict cross-border rules)."""

    check_id = "PIPA-004"
    name = "Cross-Border Transfer Documentation"
    description = "Verify cross-border data transfer is documented"
    severity = Severity.HIGH
    category = "pipa"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for data transfer documentation
        patterns = ["data-transfer*", "cross-border*", "international*",
                   "data-localization*", "해외이전*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Cross-border transfer documentation found: {found[0].name}",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No cross-border data transfer documentation found",
            recommendation="Document any international data transfers and obtain consent",
            references=[
                "PIPA Article 17 - Cross-border Transfer",
                "Korea requires consent for international transfers"
            ],
            score_impact=8
        )


# All PIPA checks
PIPA_CHECKS = [
    PIPAPrivacyOfficerCheck(),
    PIPABreachNotification24hCheck(),
    PIPAConsentCheck(),
    PIPADataLocalizationCheck(),
]
