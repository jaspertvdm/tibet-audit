"""UCP readiness checks for commerce integration."""

import json
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Tuple, List

from .base import BaseCheck, CheckResult, Status, Severity


def _find_ucp_manifest(scan_path: Path) -> Optional[Path]:
    """Find a UCP manifest on disk."""
    candidates = [
        scan_path / ".well-known" / "ucp",
        scan_path / ".well-known" / "ucp.json",
        scan_path / "ucp.json",
        scan_path / "ucp_manifest.json",
        scan_path / "docs" / "ucp.json",
    ]
    for path in candidates:
        if path.exists():
            return path
    # Fallback: limited glob for common names
    for name in ("ucp.json", "ucp_manifest.json"):
        for path in scan_path.rglob(name):
            return path
    return None


def _read_text_safe(path: Path, limit: int = 20000) -> Optional[str]:
    """Read a text file with a size limit."""
    try:
        data = path.read_text(encoding="utf-8")
        return data[:limit]
    except Exception:
        return None


def _find_policy_files(scan_path: Path) -> List[Path]:
    """Find candidate policy files related to UCP/Matrix/commerce."""
    patterns = ("*matrix*", "*commerce*", "*ucp*", "*policy*")
    seen = set()
    matches: List[Path] = []
    for pattern in patterns:
        for path in scan_path.rglob(pattern):
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json", ".yaml", ".yml"}:
                if path not in seen:
                    seen.add(path)
                    matches.append(path)
    return matches


def _load_ucp_manifest(context: dict) -> Tuple[Optional[dict], Optional[Path], Optional[str]]:
    """Load and cache the UCP manifest."""
    if "ucp_manifest" in context:
        return context["ucp_manifest"], context.get("ucp_manifest_path"), context.get("ucp_manifest_error")

    scan_path = context["scan_path"]
    manifest_path = _find_ucp_manifest(scan_path)
    if not manifest_path:
        context["ucp_manifest"] = None
        context["ucp_manifest_path"] = None
        context["ucp_manifest_error"] = "No UCP manifest found"
        return None, None, context["ucp_manifest_error"]

    try:
        raw = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(raw)
        context["ucp_manifest"] = manifest
        context["ucp_manifest_path"] = manifest_path
        context["ucp_manifest_error"] = None
        return manifest, manifest_path, None
    except Exception as exc:
        context["ucp_manifest"] = None
        context["ucp_manifest_path"] = manifest_path
        context["ucp_manifest_error"] = str(exc)
        return None, manifest_path, str(exc)


def _extract_capabilities(manifest: dict) -> List:
    """Extract capability entries from UCP manifest."""
    if not manifest:
        return []
    caps = []
    if isinstance(manifest.get("capabilities"), list):
        caps.extend(manifest["capabilities"])
    services = manifest.get("services")
    if isinstance(services, dict):
        for service in services.values():
            if isinstance(service, dict):
                caps.extend(service.get("capabilities", []) or [])
                caps.extend(service.get("extensions", []) or [])
    return caps


def _capability_name(entry) -> Optional[str]:
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("name") or entry.get("id")
    return None


def _valid_capability_name(name: str) -> bool:
    parts = name.split(".")
    return len(parts) >= 3 and all(parts)


def _origin_matches(name: str, url: str) -> bool:
    try:
        authority = ".".join(name.split(".")[:2])
        origin = urlparse(url).netloc
        return origin.endswith(authority)
    except Exception:
        return False


class UCPDiscoveryManifestCheck(BaseCheck):
    check_id = "UCP-001"
    name = "UCP Discovery Manifest"
    description = "UCP manifest exists and is valid JSON"
    severity = Severity.HIGH
    category = "ucp"
    score_weight = 12

    def run(self, context: dict) -> CheckResult:
        manifest, path, error = _load_ucp_manifest(context)
        if manifest:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                category=self.category,
                message=f"UCP manifest found at {path}",
                score_impact=self.score_weight,
            )
        status = Status.FAILED if not path else Status.WARNING
        message = error or "UCP manifest not found"
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=status,
            severity=self.severity,
            category=self.category,
            message=message,
            recommendation="Publish /.well-known/ucp with valid UCP JSON.",
            score_impact=self.score_weight,
        )


class UCPDiscoveryFieldsCheck(BaseCheck):
    check_id = "UCP-002"
    name = "UCP Discovery Fields"
    description = "Required discovery fields present"
    severity = Severity.HIGH
    category = "ucp"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        manifest, _, _ = _load_ucp_manifest(context)
        if not manifest:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                category=self.category,
                message="No UCP manifest to validate.",
                score_impact=0,
            )
        missing = []
        for key in ("capabilities", "extensions", "services", "auth", "security"):
            if key not in manifest:
                missing.append(key)
        if missing:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.FAILED,
                severity=self.severity,
                category=self.category,
                message=f"Missing fields: {', '.join(missing)}",
                recommendation="Add required discovery fields per UCP spec.",
                score_impact=self.score_weight,
            )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            category=self.category,
            message="Required discovery fields present.",
            score_impact=self.score_weight,
        )


class UCPCapabilityNamespaceCheck(BaseCheck):
    check_id = "UCP-003"
    name = "UCP Capability Namespace"
    description = "Capabilities follow reverse-domain naming and spec origin matches"
    severity = Severity.MEDIUM
    category = "ucp"
    score_weight = 8

    def run(self, context: dict) -> CheckResult:
        manifest, _, _ = _load_ucp_manifest(context)
        if not manifest:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                category=self.category,
                message="No UCP manifest to validate.",
                score_impact=0,
            )
        bad = []
        origin_mismatch = []
        for entry in _extract_capabilities(manifest):
            name = _capability_name(entry)
            if not name:
                continue
            if not _valid_capability_name(name):
                bad.append(name)
            if isinstance(entry, dict):
                spec = entry.get("spec") or entry.get("schema")
                if spec and not _origin_matches(name, spec):
                    origin_mismatch.append(name)
        if bad or origin_mismatch:
            parts = []
            if bad:
                parts.append(f"bad ids: {', '.join(bad[:5])}")
            if origin_mismatch:
                parts.append(f"origin mismatch: {', '.join(origin_mismatch[:5])}")
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                category=self.category,
                message="; ".join(parts),
                recommendation="Use reverse-domain naming and align spec/schema origins.",
                score_impact=self.score_weight,
            )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            category=self.category,
            message="Capability IDs and origins look compliant.",
            score_impact=self.score_weight,
        )


class UCPHumoticaFieldsCheck(BaseCheck):
    check_id = "UCP-004"
    name = "Humotica Fields in Manifest"
    description = "JIS/TIBET/AETHER fields present in discovery manifest"
    severity = Severity.MEDIUM
    category = "ucp"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        manifest, _, _ = _load_ucp_manifest(context)
        if not manifest:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                category=self.category,
                message="No UCP manifest to validate.",
                score_impact=0,
            )
        missing = []
        for key in ("jis.identity", "tibet.audit", "aether.policy"):
            top, sub = key.split(".")
            if top not in manifest or sub not in (manifest.get(top) or {}):
                missing.append(key)
        if missing:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                category=self.category,
                message=f"Missing Humotica fields: {', '.join(missing)}",
                recommendation="Add JIS/TIBET/AETHER metadata to discovery manifest.",
                score_impact=self.score_weight,
            )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            category=self.category,
            message="Humotica fields present in manifest.",
            score_impact=self.score_weight,
        )


class UCPMatrixGatePolicyCheck(BaseCheck):
    check_id = "UCP-005"
    name = "Matrix Gate Policy"
    description = "Matrix content-type and room policy documented"
    severity = Severity.MEDIUM
    category = "ucp"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        policy_files = _find_policy_files(scan_path)
        if policy_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                category=self.category,
                message="Matrix/commerce policy artifacts detected.",
                score_impact=self.score_weight,
            )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            category=self.category,
            message="No Matrix/commerce policy artifacts found.",
            recommendation="Document Matrix room naming and content-type allowlist.",
            score_impact=self.score_weight,
        )


class UCPMatrixGateStrictCheck(BaseCheck):
    check_id = "UCP-006"
    name = "Matrix Gate Strict Policy"
    description = "Content-type allowlist + FIR/A thresholds documented"
    severity = Severity.HIGH
    category = "ucp"
    score_weight = 8

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        policy_files = _find_policy_files(scan_path)
        if not policy_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                category=self.category,
                message="No policy files found for Matrix gate enforcement.",
                recommendation="Document Matrix allowlist and FIR/A thresholds.",
                score_impact=self.score_weight,
            )

        allowlist = False
        trust_thresholds = False
        for path in policy_files:
            content = _read_text_safe(path)
            if not content:
                continue
            lower = content.lower()
            if "nl.humotica.ucp" in lower or "content-type" in lower:
                allowlist = True
            if "fir/a" in lower or "trust threshold" in lower or "0.7" in lower or "0.3" in lower:
                trust_thresholds = True

        if allowlist and trust_thresholds:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                category=self.category,
                message="Matrix allowlist and FIR/A thresholds documented.",
                score_impact=self.score_weight,
            )

        missing = []
        if not allowlist:
            missing.append("content-type allowlist")
        if not trust_thresholds:
            missing.append("FIR/A thresholds")
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            category=self.category,
            message=f"Missing policy elements: {', '.join(missing)}",
            recommendation="Add allowlist and trust thresholds to Matrix gate policy.",
            score_impact=self.score_weight,
        )


class UCPTibetTokenStructureCheck(BaseCheck):
    check_id = "UCP-007"
    name = "TIBET Token Structure (Commerce)"
    description = "TIBET token schema for UCP financial events documented"
    severity = Severity.HIGH
    category = "ucp"
    score_weight = 9

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]
        policy_files = _find_policy_files(scan_path)
        if not policy_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                category=self.category,
                message="No docs found for TIBET commerce token structure.",
                recommendation="Document TIBET fields for UCP transactions.",
                score_impact=self.score_weight,
            )

        required_tokens = ["erin", "eromheen", "erachter", "chain_hash", "signature"]
        found = set()
        for path in policy_files:
            content = _read_text_safe(path)
            if not content:
                continue
            lower = content.lower()
            if "tibet" not in lower:
                continue
            for tok in required_tokens:
                if tok in lower:
                    found.add(tok)

        if len(found) >= 4:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                category=self.category,
                message="TIBET token structure appears documented.",
                score_impact=self.score_weight,
            )

        missing = [t for t in required_tokens if t not in found]
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            category=self.category,
            message=f"TIBET schema fields missing in docs: {', '.join(missing)}",
            recommendation="Include full TIBET schema fields for commerce events.",
            score_impact=self.score_weight,
        )


class UCPDiscoverySchemaRefsCheck(BaseCheck):
    check_id = "UCP-008"
    name = "UCP Schema References"
    description = "Capabilities include spec/schema URLs"
    severity = Severity.MEDIUM
    category = "ucp"
    score_weight = 6

    def run(self, context: dict) -> CheckResult:
        manifest, _, _ = _load_ucp_manifest(context)
        if not manifest:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                category=self.category,
                message="No UCP manifest to validate.",
                score_impact=0,
            )
        missing = []
        for entry in _extract_capabilities(manifest):
            if isinstance(entry, dict):
                if not entry.get("spec") and not entry.get("schema"):
                    name = _capability_name(entry) or "unknown"
                    missing.append(name)
        if missing:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                category=self.category,
                message=f"Missing spec/schema URLs: {', '.join(missing[:5])}",
                recommendation="Add spec/schema URLs to capability entries.",
                score_impact=self.score_weight,
            )
        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            category=self.category,
            message="Capabilities include spec/schema URLs.",
            score_impact=self.score_weight,
        )


UCP_CHECKS = [
    UCPDiscoveryManifestCheck(),
    UCPDiscoveryFieldsCheck(),
    UCPCapabilityNamespaceCheck(),
    UCPHumoticaFieldsCheck(),
    UCPMatrixGatePolicyCheck(),
    UCPMatrixGateStrictCheck(),
    UCPTibetTokenStructureCheck(),
    UCPDiscoverySchemaRefsCheck(),
]
