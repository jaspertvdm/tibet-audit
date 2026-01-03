"""Brazil LGPD (Lei Geral de Proteção de Dados) Compliance Checks.

LGPD is Brazil's comprehensive data protection law, similar to GDPR.
Key features:
- Consent-based processing
- Data Protection Officer (DPO/Encarregado)
- Data subject rights
- Breach notification
- Cross-border transfer restrictions
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class LGPDLegalBasisCheck(BaseCheck):
    """Check for legal basis for data processing."""

    check_id = "LGPD-001"
    name = "Legal Basis for Processing"
    description = "Verify legal basis exists for personal data processing"
    severity = Severity.CRITICAL
    category = "lgpd"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Search for consent/legal basis patterns
        basis_terms = ["consent", "lgpd", "legal_basis", "consentimento",
                      "base_legal", "tratamento"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:25]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in basis_terms):
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
                message="Legal basis mechanisms found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.HIGH,
            message="No legal basis mechanism detected",
            recommendation="Implement consent or other legal basis before processing",
            references=[
                "LGPD Article 7 - Legal bases for processing",
                "https://www.gov.br/anpd/"
            ],
            score_impact=15
        )


class LGPDEncarregadoCheck(BaseCheck):
    """Check for Data Protection Officer (Encarregado)."""

    check_id = "LGPD-002"
    name = "Encarregado (DPO)"
    description = "Verify Data Protection Officer is designated"
    severity = Severity.HIGH
    category = "lgpd"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for DPO documentation
        patterns = ["dpo*", "encarregado*", "data-protection-officer*"]
        found = []

        for pattern in patterns:
            found.extend(scan_path.glob(f"**/{pattern}.*"))

        if found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Encarregado (DPO) designation found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No Encarregado (DPO) designation found",
            recommendation="Designate an Encarregado and publish contact information",
            references=["LGPD Article 41 - Encarregado"],
            score_impact=10
        )


class LGPDDataSubjectRightsCheck(BaseCheck):
    """Check for data subject rights implementation."""

    check_id = "LGPD-003"
    name = "Data Subject Rights"
    description = "Verify data subject rights are implemented"
    severity = Severity.HIGH
    category = "lgpd"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for rights-related patterns
        rights_terms = ["data_access", "data_deletion", "data_portability",
                       "right_to_access", "direito_acesso", "exclusao"]

        source_files = list(scan_path.glob("**/*.py"))
        found = False

        for sf in source_files[:25]:
            try:
                content = sf.read_text().lower()
                if any(term in content for term in rights_terms):
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
                message="Data subject rights mechanisms found",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No data subject rights implementation detected",
            recommendation="Implement access, correction, deletion, and portability rights",
            references=["LGPD Article 18 - Rights of data subjects"],
            score_impact=12
        )


class LGPDBreachCheck(BaseCheck):
    """Check for breach notification procedure."""

    check_id = "LGPD-004"
    name = "Breach Notification"
    description = "Verify breach notification procedure exists"
    severity = Severity.CRITICAL
    category = "lgpd"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for breach procedures
        patterns = ["breach*", "incident*", "incidente*", "vazamento*"]
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
            recommendation="Create breach notification procedure (notify ANPD in reasonable time)",
            fix_action=FixAction(
                description="Generate LGPD breach procedure",
                command="tibet-audit template lgpd-breach > docs/breach-procedure-br.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["LGPD Article 48 - Breach notification"],
            score_impact=self.score_weight
        )


# All LGPD checks
LGPD_CHECKS = [
    LGPDLegalBasisCheck(),
    LGPDEncarregadoCheck(),
    LGPDDataSubjectRightsCheck(),
    LGPDBreachCheck(),
]
