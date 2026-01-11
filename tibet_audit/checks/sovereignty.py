"""Sovereignty and data residency checks."""

from pathlib import Path
from typing import List

from .base import BaseCheck, CheckResult, Status, Severity


def _find_files(scan_path: Path, patterns: List[str]) -> List[Path]:
    hits = []
    for pattern in patterns:
        for path in scan_path.rglob(pattern):
            if path.is_file():
                hits.append(path)
            if len(hits) >= 10:
                return hits
    return hits


def _read_text(path: Path, max_bytes: int = 200_000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


class DataResidencyCheck(BaseCheck):
    check_id = "SOV-001"
    name = "Data residency declaration"
    description = "Checks for explicit data residency documentation."
    severity = Severity.HIGH
    category = "sovereignty"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        policy_files = _find_files(scan_path, ["*policy*.md", "*privacy*.md", "*compliance*.md", "*security*.md"])
        keywords = ["data residency", "residency", "sovereignty", "data location", "region"]
        for path in policy_files:
            text = _read_text(path).lower()
            if any(k in text for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Residency language found in {path}.",
                    score_impact=0,
                )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No data residency declaration found.",
            recommendation="Document data residency regions and storage location.",
            score_impact=self.score_weight,
        )


class ThirdPartyDisclosureCheck(BaseCheck):
    check_id = "SOV-002"
    name = "Third-party processor disclosure"
    description = "Checks for third-party vendor or subprocessor list."
    severity = Severity.MEDIUM
    category = "sovereignty"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        docs = _find_files(scan_path, ["*processor*.md", "*vendor*.md", "*subprocessor*.md", "*privacy*.md"])
        keywords = ["subprocessor", "vendor", "third party", "processor list"]
        for path in docs:
            text = _read_text(path).lower()
            if any(k in text for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Third-party disclosure found in {path}.",
                    score_impact=0,
                )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No third-party processor disclosure found.",
            recommendation="Provide a list of subprocessors and their regions.",
            score_impact=self.score_weight,
        )


class CrossBorderTransferCheck(BaseCheck):
    check_id = "SOV-003"
    name = "Cross-border transfer policy"
    description = "Checks for cross-border data transfer guidance."
    severity = Severity.MEDIUM
    category = "sovereignty"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        docs = _find_files(scan_path, ["*transfer*.md", "*policy*.md", "*privacy*.md"])
        keywords = ["cross-border", "cross border", "transfer", "standard contractual clauses", "scc"]
        for path in docs:
            text = _read_text(path).lower()
            if any(k in text for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Transfer policy found in {path}.",
                    score_impact=0,
                )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No cross-border transfer policy found.",
            recommendation="Document transfer mechanisms and legal basis.",
            score_impact=self.score_weight,
        )


class EncryptionAtRestCheck(BaseCheck):
    check_id = "SOV-004"
    name = "Encryption at rest documented"
    description = "Checks for encryption at rest statements."
    severity = Severity.MEDIUM
    category = "sovereignty"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        docs = _find_files(scan_path, ["*security*.md", "*policy*.md", "*compliance*.md"])
        keywords = ["encryption at rest", "disk encryption", "storage encryption"]
        for path in docs:
            text = _read_text(path).lower()
            if any(k in text for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Encryption-at-rest statement found in {path}.",
                    score_impact=0,
                )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No encryption-at-rest documentation found.",
            recommendation="Document encryption-at-rest configuration.",
            score_impact=self.score_weight,
        )


SOVEREIGNTY_CHECKS = [
    DataResidencyCheck(),
    ThirdPartyDisclosureCheck(),
    CrossBorderTransferCheck(),
    EncryptionAtRestCheck(),
]
