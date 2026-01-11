"""Provider-grade security checks (Project MERCURY)."""

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


class OSSecurityUpdatesCheck(BaseCheck):
    check_id = "PROV-001"
    name = "OS security update policy"
    description = "Checks for documented update/patch policy."
    severity = Severity.HIGH
    category = "provider"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        docs = _find_files(scan_path, ["*security*.md", "*policy*.md", "*patch*.md", "*update*.md"])
        keywords = ["security updates", "patch policy", "kernel updates", "update policy"]
        for path in docs:
            if any(k in _read_text(path).lower() for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Update policy found in {path}.",
                    score_impact=0,
                    category=self.category,
                )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No OS security update policy found.",
            recommendation="Document patch cadence and emergency update procedure.",
            score_impact=self.score_weight,
            category=self.category,
        )


class KernelPatchCheck(BaseCheck):
    check_id = "PROV-002"
    name = "Kernel patch strategy"
    description = "Checks for kernel patching or livepatch strategy."
    severity = Severity.MEDIUM
    category = "provider"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        docs = _find_files(scan_path, ["*security*.md", "*policy*.md", "*kernel*.md"])
        keywords = ["livepatch", "kpatch", "kernel patch", "kernel updates"]
        for path in docs:
            if any(k in _read_text(path).lower() for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Kernel patch strategy found in {path}.",
                    score_impact=0,
                    category=self.category,
                )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No kernel patch strategy found.",
            recommendation="Document kernel patching or livepatch policy.",
            score_impact=self.score_weight,
            category=self.category,
        )


class AISafetyIntegrityCheck(BaseCheck):
    check_id = "PROV-003"
    name = "AI model integrity check"
    description = "Checks for model integrity verification or checksums."
    severity = Severity.HIGH
    category = "provider"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        files = _find_files(scan_path, ["MODEL_CARD.md", "model.sha256", "model.integrity", "*model*.md"])
        keywords = ["checksum", "hash", "integrity", "model card", "provenance"]
        for path in files:
            if any(k in _read_text(path).lower() for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Model integrity evidence found in {path}.",
                    score_impact=0,
                    category=self.category,
                )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No AI model integrity evidence found.",
            recommendation="Provide model checksums/provenance; enable Sentinel integrity checks.",
            score_impact=self.score_weight,
            category=self.category,
        )


class AILaneEncryptionCheck(BaseCheck):
    check_id = "PROV-004"
    name = "AI-to-AI lane encryption"
    description = "Checks for secure channel / encryption in AI communications."
    severity = Severity.HIGH
    category = "provider"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        files = _find_files(scan_path, ["*network*.md", "*security*.md", "*crypto*.md", "*tls*.md"])
        keywords = ["tls", "mtls", "encryption", "noise", "wireguard", "quic"]
        for path in files:
            if any(k in _read_text(path).lower() for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Lane encryption evidence found in {path}.",
                    score_impact=0,
                    category=self.category,
                )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No AI-to-AI lane encryption evidence found.",
            recommendation="Enable encrypted lanes; integrate Vault + JIS Router secure channels.",
            score_impact=self.score_weight,
            category=self.category,
        )


class ASPDRMBindingCheck(BaseCheck):
    check_id = "PROV-005"
    name = "ASP/DRM binding verification"
    description = "Checks for attestation / DRM / secure binding statements."
    severity = Severity.MEDIUM
    category = "provider"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        files = _find_files(scan_path, ["*security*.md", "*attest*.md", "*drm*.md"])
        keywords = ["attestation", "secure boot", "tpm", "drm", "binding"]
        for path in files:
            if any(k in _read_text(path).lower() for k in keywords):
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"ASP/DRM binding evidence found in {path}.",
                    score_impact=0,
                    category=self.category,
                )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No ASP/DRM binding evidence found.",
            recommendation="Document attestation/DRM binding or enable Refinery attestation flow.",
            score_impact=self.score_weight,
            category=self.category,
        )


PROVIDER_SECURITY_CHECKS = [
    OSSecurityUpdatesCheck(),
    KernelPatchCheck(),
    AISafetyIntegrityCheck(),
    AILaneEncryptionCheck(),
    ASPDRMBindingCheck(),
]
