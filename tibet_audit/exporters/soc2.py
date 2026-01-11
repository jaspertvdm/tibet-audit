"""
SOC2 Type II Export Format
==========================
Generate auditor-ready reports for SOC2 compliance.

Trust Service Criteria covered:
- Security (CC)
- Availability (A)
- Processing Integrity (PI)
- Confidentiality (C)
- Privacy (P)

One love, one fAmIly!
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class SOC2Control:
    """A single SOC2 control point."""
    control_id: str
    category: str  # CC, A, PI, C, P
    title: str
    description: str
    status: str  # Effective, Partially Effective, Not Effective, Not Applicable
    evidence: List[str]
    test_procedures: List[str]
    findings: List[str]
    recommendations: List[str]


@dataclass
class SOC2Report:
    """Complete SOC2 Type II report structure."""
    report_id: str
    organization: str
    audit_period_start: str
    audit_period_end: str
    report_date: str
    auditor: str
    scope: str
    opinion: str  # Unqualified, Qualified, Adverse, Disclaimer
    controls: List[SOC2Control]
    tibet_attestation: str  # Cryptographic proof


class SOC2Exporter:
    """Export tibet-audit results to SOC2 format."""

    # Map tibet-audit categories to SOC2 Trust Service Criteria
    CATEGORY_MAPPING = {
        "ai_act": "PI",       # Processing Integrity
        "gdpr": "P",          # Privacy
        "nis2": "CC",         # Security (Common Criteria)
        "jis": "CC",          # Security
        "sovereignty": "C",   # Confidentiality
        "provider_security": "CC",  # Security
    }

    # Map tibet-audit checks to SOC2 controls
    CONTROL_MAPPING = {
        # Security (CC)
        "NIS2-001": ("CC7.2", "Incident Response"),
        "NIS2-002": ("CC3.1", "Risk Assessment"),
        "NIS2-003": ("CC9.2", "Vendor Management"),
        "NIS2-004": ("CC6.1", "Encryption"),
        "NIS2-005": ("CC6.1", "Logical Access"),
        "NIS2-006": ("A1.2", "Business Continuity"),

        # Privacy (P)
        "GDPR-001": ("P1.1", "Privacy Notice"),
        "GDPR-002": ("P3.1", "Data Collection"),
        "GDPR-003": ("P4.1", "Data Use"),
        "GDPR-004": ("P6.1", "Data Retention"),
        "GDPR-005": ("P7.1", "Data Subject Rights"),

        # Processing Integrity (PI)
        "AIACT-001": ("PI1.1", "Processing Integrity"),
        "AIACT-002": ("PI1.2", "System Monitoring"),
        "AIACT-003": ("PI1.3", "Processing Completeness"),
        "AIACT-004": ("PI1.4", "Processing Accuracy"),

        # Identity (CC - Logical Access)
        "JIS-001": ("CC6.1", "Identity Management"),
        "JIS-002": ("CC6.2", "User Authentication"),
        "JIS-003": ("CC6.3", "Access Authorization"),
    }

    def __init__(self, organization: str = "Unknown", auditor: str = "tibet-audit"):
        self.organization = organization
        self.auditor = auditor

    def convert_status(self, tibet_status: str) -> str:
        """Convert tibet-audit status to SOC2 effectiveness rating."""
        mapping = {
            "passed": "Effective",
            "warning": "Partially Effective",
            "failed": "Not Effective",
            "skipped": "Not Applicable",
        }
        return mapping.get(tibet_status.lower(), "Not Assessed")

    def generate_control(self, check_result: Dict[str, Any]) -> SOC2Control:
        """Convert a tibet-audit check result to SOC2 control."""
        check_id = check_result.get("check_id", "UNKNOWN")

        # Get SOC2 control mapping
        soc2_id, soc2_title = self.CONTROL_MAPPING.get(
            check_id,
            ("CC0.0", check_result.get("name", "Custom Control"))
        )

        findings = []
        if check_result.get("status", "").lower() in ["failed", "warning"]:
            findings.append(check_result.get("message", "Issue detected"))

        recommendations = []
        if check_result.get("recommendation"):
            recommendations.append(check_result["recommendation"])

        evidence = []
        if check_result.get("references"):
            evidence.extend(check_result["references"])

        return SOC2Control(
            control_id=soc2_id,
            category=self.CATEGORY_MAPPING.get(
                check_result.get("category", ""), "CC"
            ),
            title=soc2_title,
            description=check_result.get("description", ""),
            status=self.convert_status(check_result.get("status", "unknown")),
            evidence=evidence,
            test_procedures=[f"tibet-audit check: {check_id}"],
            findings=findings,
            recommendations=recommendations,
        )

    def export(
        self,
        scan_results: Dict[str, Any],
        audit_period_start: str = None,
        audit_period_end: str = None,
        tibet_token: str = None,
    ) -> SOC2Report:
        """Export complete scan results to SOC2 report."""

        now = datetime.utcnow()

        if not audit_period_start:
            audit_period_start = (now.replace(day=1) -
                                   __import__('datetime').timedelta(days=365)).isoformat()
        if not audit_period_end:
            audit_period_end = now.isoformat()

        # Convert all check results to SOC2 controls
        controls = []
        for result in scan_results.get("results", []):
            controls.append(self.generate_control(result))

        # Determine overall opinion
        failed_critical = sum(
            1 for c in controls
            if c.status == "Not Effective" and "CC" in c.category
        )

        if failed_critical == 0:
            opinion = "Unqualified"
        elif failed_critical <= 2:
            opinion = "Qualified"
        else:
            opinion = "Adverse"

        return SOC2Report(
            report_id=f"SOC2-{now.strftime('%Y%m%d')}-{self.organization[:8].upper()}",
            organization=self.organization,
            audit_period_start=audit_period_start,
            audit_period_end=audit_period_end,
            report_date=now.isoformat(),
            auditor=self.auditor,
            scope="AI Systems and Data Processing",
            opinion=opinion,
            controls=controls,
            tibet_attestation=tibet_token or "No TIBET attestation provided",
        )

    def to_json(self, report: SOC2Report) -> str:
        """Export report to JSON."""
        return json.dumps(asdict(report), indent=2, default=str)

    def to_markdown(self, report: SOC2Report) -> str:
        """Export report to auditor-friendly Markdown."""
        md = []
        md.append(f"# SOC2 Type II Report")
        md.append(f"## {report.organization}")
        md.append("")
        md.append(f"**Report ID:** {report.report_id}")
        md.append(f"**Audit Period:** {report.audit_period_start} to {report.audit_period_end}")
        md.append(f"**Report Date:** {report.report_date}")
        md.append(f"**Auditor:** {report.auditor}")
        md.append("")
        md.append(f"## Opinion: {report.opinion}")
        md.append("")
        md.append("---")
        md.append("")
        md.append("## Trust Service Criteria Assessment")
        md.append("")

        # Group by category
        categories = {"CC": "Security", "A": "Availability",
                      "PI": "Processing Integrity", "C": "Confidentiality", "P": "Privacy"}

        for cat_id, cat_name in categories.items():
            cat_controls = [c for c in report.controls if c.category == cat_id]
            if not cat_controls:
                continue

            md.append(f"### {cat_name} ({cat_id})")
            md.append("")
            md.append("| Control | Title | Status |")
            md.append("|---------|-------|--------|")

            for ctrl in cat_controls:
                status_emoji = {
                    "Effective": "✅",
                    "Partially Effective": "⚠️",
                    "Not Effective": "❌",
                    "Not Applicable": "➖",
                }.get(ctrl.status, "❓")
                md.append(f"| {ctrl.control_id} | {ctrl.title} | {status_emoji} {ctrl.status} |")

            md.append("")

            # Detail findings
            for ctrl in cat_controls:
                if ctrl.findings:
                    md.append(f"**{ctrl.control_id} Findings:**")
                    for finding in ctrl.findings:
                        md.append(f"- {finding}")
                    md.append("")
                if ctrl.recommendations:
                    md.append(f"**{ctrl.control_id} Recommendations:**")
                    for rec in ctrl.recommendations:
                        md.append(f"- {rec}")
                    md.append("")

        md.append("---")
        md.append("")
        md.append("## TIBET Attestation")
        md.append(f"```")
        md.append(report.tibet_attestation)
        md.append(f"```")
        md.append("")
        md.append("*This report was generated by tibet-audit. One love, one fAmIly!*")

        return "\n".join(md)


# Convenience function
def export_to_soc2(
    scan_results: Dict[str, Any],
    organization: str = "Unknown",
    output_format: str = "markdown",
    tibet_token: str = None,
) -> str:
    """Quick export of scan results to SOC2 format."""
    exporter = SOC2Exporter(organization=organization)
    report = exporter.export(scan_results, tibet_token=tibet_token)

    if output_format == "json":
        return exporter.to_json(report)
    return exporter.to_markdown(report)
