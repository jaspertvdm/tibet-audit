"""
NIS2 Directive Compliance Checks
================================
EU Network and Information Security Directive 2022/2555

Essential for:
- US companies selling AI/tech to EU
- Critical infrastructure providers
- Digital service providers

One love, one fAmIly!
"""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class NIS2IncidentReportingCheck(BaseCheck):
    """Check for incident reporting capability (24h requirement)."""

    check_id = "NIS2-001"
    name = "Incident Reporting Capability"
    description = "NIS2 requires 24-hour incident reporting to authorities"
    severity = Severity.CRITICAL
    category = "nis2"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for incident response documentation
        incident_patterns = [
            "*incident*", "*security*response*", "*breach*",
            "*alert*", "*notification*", "*report*"
        ]

        found_docs = []
        for pattern in incident_patterns:
            found_docs.extend(scan_path.glob(f"**/{pattern}.md"))
            found_docs.extend(scan_path.glob(f"**/{pattern}.txt"))
            found_docs.extend(scan_path.glob(f"**/docs/{pattern}*"))

        # Check for automated alerting in code
        alert_in_code = False
        for py_file in list(scan_path.glob("**/*.py"))[:50]:
            try:
                content = py_file.read_text()
                if any(term in content.lower() for term in
                       ["incident", "alert", "notify", "pagerduty", "opsgenie", "slack_webhook"]):
                    alert_in_code = True
                    break
            except:
                pass

        if found_docs and alert_in_code:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Incident reporting documentation and alerting found",
                score_impact=0
            )

        if found_docs or alert_in_code:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.HIGH,
                message="Partial incident reporting capability found",
                recommendation="Ensure 24-hour reporting capability to relevant CSIRT",
                references=["NIS2 Article 23"],
                score_impact=10
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No incident reporting capability found (NIS2 requires 24h reporting!)",
            recommendation="Implement incident response plan with automated alerting",
            fix_action=FixAction(
                description="Create incident response template",
                command="tibet-audit fix --template incident-response",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["NIS2 Article 23", "ENISA Guidelines"],
            score_impact=self.score_weight
        )


class NIS2RiskManagementCheck(BaseCheck):
    """Check for cybersecurity risk management measures."""

    check_id = "NIS2-002"
    name = "Risk Management Measures"
    description = "NIS2 requires documented risk management approach"
    severity = Severity.HIGH
    category = "nis2"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        risk_docs = list(scan_path.glob("**/*risk*")) + \
                    list(scan_path.glob("**/*security*policy*")) + \
                    list(scan_path.glob("**/*threat*model*"))

        if risk_docs:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Risk management documentation found: {len(risk_docs)} files",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No risk management documentation found",
            recommendation="Create risk assessment and security policy documents",
            references=["NIS2 Article 21"],
            score_impact=self.score_weight
        )


class NIS2SupplyChainSecurityCheck(BaseCheck):
    """Check for supply chain security measures (dependencies)."""

    check_id = "NIS2-003"
    name = "Supply Chain Security"
    description = "NIS2 requires supply chain risk assessment"
    severity = Severity.HIGH
    category = "nis2"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for dependency scanning
        lockfiles = list(scan_path.glob("**/requirements*.txt")) + \
                    list(scan_path.glob("**/Cargo.lock")) + \
                    list(scan_path.glob("**/package-lock.json")) + \
                    list(scan_path.glob("**/poetry.lock"))

        # Check for security scanning tools
        security_configs = list(scan_path.glob("**/.snyk")) + \
                          list(scan_path.glob("**/dependabot.yml")) + \
                          list(scan_path.glob("**/.github/dependabot.yml")) + \
                          list(scan_path.glob("**/safety*"))

        sbom_files = list(scan_path.glob("**/sbom*")) + \
                     list(scan_path.glob("**/bom.json")) + \
                     list(scan_path.glob("**/cyclonedx*"))

        if sbom_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="SBOM (Software Bill of Materials) found - excellent supply chain visibility",
                score_impact=0
            )

        if security_configs:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Dependency security scanning configured",
                score_impact=0
            )

        if lockfiles:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message="Lockfiles found but no security scanning configured",
                recommendation="Add dependency scanning (Dependabot, Snyk, or Safety)",
                fix_action=FixAction(
                    description="Enable GitHub Dependabot",
                    command="tibet-audit fix --enable-dependabot",
                    requires_confirmation=True,
                    risk_level="low"
                ),
                references=["NIS2 Article 21(2)(d)"],
                score_impact=8
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No supply chain security measures found",
            recommendation="Implement SBOM and dependency scanning",
            references=["NIS2 Article 21(2)(d)", "CRA (Cyber Resilience Act)"],
            score_impact=self.score_weight
        )


class NIS2EncryptionCheck(BaseCheck):
    """Check for encryption in transit and at rest."""

    check_id = "NIS2-004"
    name = "Encryption Measures"
    description = "NIS2 requires appropriate encryption"
    severity = Severity.HIGH
    category = "nis2"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        encryption_evidence = []

        # Check for TLS/SSL configs
        tls_configs = list(scan_path.glob("**/*ssl*")) + \
                      list(scan_path.glob("**/*tls*")) + \
                      list(scan_path.glob("**/certs/*"))
        if tls_configs:
            encryption_evidence.append("TLS/SSL configuration")

        # Check code for encryption usage
        for py_file in list(scan_path.glob("**/*.py"))[:50]:
            try:
                content = py_file.read_text()
                if any(term in content for term in
                       ["cryptography", "fernet", "aes", "encrypt", "hashlib", "hmac"]):
                    encryption_evidence.append("Encryption in code")
                    break
            except:
                pass

        # Check for TIBET (includes crypto signing)
        if list(scan_path.glob("**/tibet*")):
            encryption_evidence.append("TIBET cryptographic signing")

        if len(encryption_evidence) >= 2:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Encryption measures found: {', '.join(encryption_evidence)}",
                score_impact=0
            )

        if encryption_evidence:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message=f"Partial encryption: {', '.join(encryption_evidence)}",
                recommendation="Ensure encryption at rest and in transit",
                references=["NIS2 Article 21(2)(h)"],
                score_impact=8
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No encryption measures found",
            recommendation="Implement TLS for transit and encryption at rest",
            references=["NIS2 Article 21(2)(h)"],
            score_impact=self.score_weight
        )


class NIS2AccessControlCheck(BaseCheck):
    """Check for access control and authentication."""

    check_id = "NIS2-005"
    name = "Access Control & Authentication"
    description = "NIS2 requires proper access management"
    severity = Severity.HIGH
    category = "nis2"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Check for authentication implementation
        auth_evidence = []

        for py_file in list(scan_path.glob("**/*.py"))[:50]:
            try:
                content = py_file.read_text()
                if any(term in content.lower() for term in
                       ["jwt", "oauth", "authentication", "authorize", "rbac", "permission"]):
                    auth_evidence.append("Authentication code")
                    break
            except:
                pass

        # Check for JIS (our identity system)
        if list(scan_path.glob("**/jis*")) or list(scan_path.glob("**/identity*")):
            auth_evidence.append("JIS identity system")

        # Check for MFA documentation
        mfa_docs = list(scan_path.glob("**/*mfa*")) + list(scan_path.glob("**/*2fa*"))
        if mfa_docs:
            auth_evidence.append("MFA documentation")

        if len(auth_evidence) >= 2:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Access control measures: {', '.join(auth_evidence)}",
                score_impact=0
            )

        if auth_evidence:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message=f"Basic access control: {', '.join(auth_evidence)}",
                recommendation="Consider adding MFA and role-based access control",
                references=["NIS2 Article 21(2)(i)"],
                score_impact=8
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No access control implementation found",
            recommendation="Implement authentication and authorization",
            references=["NIS2 Article 21(2)(i)", "JIS Identity Standard"],
            score_impact=self.score_weight
        )


class NIS2BusinessContinuityCheck(BaseCheck):
    """Check for business continuity and disaster recovery."""

    check_id = "NIS2-006"
    name = "Business Continuity"
    description = "NIS2 requires backup and recovery procedures"
    severity = Severity.HIGH
    category = "nis2"
    score_weight = 12

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        bc_docs = list(scan_path.glob("**/*backup*")) + \
                  list(scan_path.glob("**/*disaster*")) + \
                  list(scan_path.glob("**/*recovery*")) + \
                  list(scan_path.glob("**/*continuity*"))

        # Check for infrastructure-as-code (enables recovery)
        iac_files = list(scan_path.glob("**/terraform*")) + \
                    list(scan_path.glob("**/*.tf")) + \
                    list(scan_path.glob("**/docker-compose*")) + \
                    list(scan_path.glob("**/Dockerfile"))

        if bc_docs and iac_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Business continuity docs and IaC found",
                score_impact=0
            )

        if bc_docs or iac_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message="Partial business continuity measures",
                recommendation="Document backup procedures and test recovery",
                references=["NIS2 Article 21(2)(c)"],
                score_impact=6
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No business continuity measures found",
            recommendation="Create backup and disaster recovery plan",
            references=["NIS2 Article 21(2)(c)"],
            score_impact=self.score_weight
        )


# Export all checks
NIS2_CHECKS = [
    NIS2IncidentReportingCheck(),
    NIS2RiskManagementCheck(),
    NIS2SupplyChainSecurityCheck(),
    NIS2EncryptionCheck(),
    NIS2AccessControlCheck(),
    NIS2BusinessContinuityCheck(),
]
