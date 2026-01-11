"""JIS compliance checks."""

from pathlib import Path
from typing import List

from .base import BaseCheck, CheckResult, Status, Severity


def _find_files(scan_path: Path, names: List[str]) -> List[Path]:
    hits = []
    for name in names:
        for path in scan_path.rglob(name):
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


class JISIdentityFileCheck(BaseCheck):
    check_id = "JIS-001"
    name = "JIS identity file present"
    description = "Looks for a JIS identity or metadata file."
    severity = Severity.HIGH
    category = "jis"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        names = ["jis.json", "jis.yaml", "identity.json", "identity.yaml", "jis_identity.json"]
        hits = _find_files(scan_path, names)
        if hits:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Found identity file(s): {', '.join(str(h) for h in hits[:3])}",
                score_impact=0,
            )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No JIS identity file found (expected jis.json/identity.json).",
            recommendation="Create a JIS identity file with owner/scope/environment.",
            score_impact=self.score_weight,
        )


class JISMetadataCheck(BaseCheck):
    check_id = "JIS-002"
    name = "JIS identity metadata completeness"
    description = "Checks for owner/scope/environment fields in identity data."
    severity = Severity.MEDIUM
    category = "jis"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        hits = _find_files(scan_path, ["jis.json", "identity.json", "identity.yaml", "jis.yaml"])
        if not hits:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message="No identity file found to validate metadata.",
                score_impact=0,
            )

        text = _read_text(hits[0]).lower()
        missing = [k for k in ("owner", "scope", "environment") if k not in text]
        if not missing:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Identity metadata includes owner/scope/environment.",
                score_impact=0,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message=f"Identity metadata missing fields: {', '.join(missing)}",
            recommendation="Add missing identity metadata fields.",
            score_impact=self.score_weight,
        )


class JISKeyRotationPolicyCheck(BaseCheck):
    check_id = "JIS-003"
    name = "Key rotation policy present"
    description = "Checks for documentation of key rotation policy."
    severity = Severity.MEDIUM
    category = "jis"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        policy_files = _find_files(scan_path, ["*policy*.md", "*policy*.txt", "*security*.md", "*security*.txt"])
        keywords = ["key rotation", "rotate keys", "rotation policy"]
        for path in policy_files:
            text = _read_text(path).lower()
            if any(k in text for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Key rotation policy found in {path}.",
                    score_impact=0,
                )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No explicit key rotation policy found.",
            recommendation="Document key rotation frequency and procedure.",
            score_impact=self.score_weight,
        )


JIS_CHECKS = [
    JISIdentityFileCheck(),
    JISMetadataCheck(),
    JISKeyRotationPolicyCheck(),
]
