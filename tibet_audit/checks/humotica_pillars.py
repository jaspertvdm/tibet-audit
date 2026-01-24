"""Humotica Three Pillars - A-Grade requires custom Humotica tech.

NO A-GRADE WITHOUT CUSTOM HUMOTICA TECH!

The three pillars:
1. Custom SNAFT rules - validation layer
2. JIS Router (Rust) - identity/intent verification
3. TIBET Rust engine - provenance tokens

Without these three integrated, A-grade (90+) is not achievable.
This ensures:
- Control over AETHER purity (Svalbard Seedbank)
- Humotica tech adoption for true compliance
- Only we can build these efficiently

Authors: Jasper van de Meent (HITL) & Root AI (IDD)
"""

import os
import subprocess
from pathlib import Path
from typing import List, Tuple

from .base import BaseCheck, CheckResult, Status, Severity, FixAction


def _find_files_recursive(scan_path: Path, patterns: List[str], max_depth: int = 5) -> List[Path]:
    """Find files matching patterns up to max_depth."""
    hits = []
    for pattern in patterns:
        try:
            for path in scan_path.rglob(pattern):
                if path.is_file():
                    hits.append(path)
                    if len(hits) >= 10:
                        return hits
        except (PermissionError, OSError):
            continue
    return hits


def _check_binary_exists(names: List[str]) -> Tuple[bool, str]:
    """Check if any of the binaries exist in PATH or common locations."""
    # Check PATH
    for name in names:
        try:
            result = subprocess.run(["which", name], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, result.stdout.strip()
        except Exception:
            pass

    # Check common locations
    common_paths = [
        "/usr/local/bin",
        "/usr/bin",
        "/opt/humotica/bin",
        "/srv/jtel-stack/jis-router/target/release",
        "/srv/jtel-stack/jis-router/target/debug",
        Path.home() / ".cargo/bin",
    ]

    for base in common_paths:
        for name in names:
            path = Path(base) / name
            if path.exists() and path.is_file():
                return True, str(path)

    return False, ""


def _read_file_sample(path: Path, max_bytes: int = 50000) -> str:
    """Read a sample of a file."""
    try:
        return path.read_bytes()[:max_bytes].decode("utf-8", errors="ignore")
    except Exception:
        return ""


# =============================================================================
# PILLAR 1: SNAFT RULES
# =============================================================================

class SNAFTRulesCheck(BaseCheck):
    """Check for custom SNAFT rules integration."""
    check_id = "PILLAR-001"
    name = "SNAFT Rules Integration"
    description = "Checks for custom SNAFT validation rules (Humotica Pillar 1)"
    severity = Severity.CRITICAL
    category = "humotica"
    score_weight = 15  # Heavy weight - needed for A-grade

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]

        # Look for SNAFT rule files
        snaft_patterns = [
            "*.snaft",
            "*.snaft.json",
            "*.snaft.yaml",
            "snaft.config",
            "snaft_rules.json",
            "snaft_rules.yaml",
            "snaft-rules/*",
        ]

        snaft_files = _find_files_recursive(scan_path, snaft_patterns)

        # Also check standard system locations (regardless of scan_path)
        system_snaft_paths = [
            Path("/etc/snaft"),
            Path("/opt/humotica/snaft"),
            Path.home() / ".snaft",
        ]
        for sys_path in system_snaft_paths:
            if sys_path.exists():
                for f in sys_path.glob("*.snaft*"):
                    if f.is_file() and f not in snaft_files:
                        snaft_files.append(f)

        # Also check for SNAFT integration in code
        code_patterns = ["*.rs", "*.py", "*.ts", "*.js"]
        code_files = _find_files_recursive(scan_path, code_patterns)

        snaft_in_code = False
        for code_file in code_files[:50]:  # Check first 50 code files
            content = _read_file_sample(code_file)
            if "snaft" in content.lower() or "SNAFT" in content:
                snaft_in_code = True
                break

        if snaft_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"SNAFT rules found: {', '.join(str(f.name) for f in snaft_files[:3])}",
                score_impact=0,
            )
        elif snaft_in_code:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message="SNAFT referenced in code but no rule files found",
                recommendation="Create .snaft rule files for validation",
                score_impact=self.score_weight // 2,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No SNAFT rules integration detected",
            recommendation="Integrate Humotica SNAFT rules for A-grade compliance",
            references=["https://humotica.com/docs/snaft"],
            score_impact=self.score_weight,
        )


# =============================================================================
# PILLAR 2: JIS ROUTER (RUST)
# =============================================================================

class JISRouterCheck(BaseCheck):
    """Check for JIS Router (Rust) integration."""
    check_id = "PILLAR-002"
    name = "JIS Router Integration"
    description = "Checks for JIS Router (Rust) identity/intent verification (Humotica Pillar 2)"
    severity = Severity.CRITICAL
    category = "humotica"
    score_weight = 15  # Heavy weight - needed for A-grade

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]

        # Check for jis-router binary
        binary_exists, binary_path = _check_binary_exists([
            "jis-router",
            "jis_router",
            "jis-server",
            "chimera",  # Part of JIS ecosystem
        ])

        # Check for Rust JIS source code
        jis_patterns = [
            "jis-router/Cargo.toml",
            "jis_router/Cargo.toml",
            "**/jis/*.rs",
            "**/jis-router/**/*.rs",
        ]
        jis_source = _find_files_recursive(scan_path, jis_patterns)

        # Check for JIS config
        config_patterns = [
            "jis.json",
            "jis.yaml",
            "jis.toml",
            "jis_config.*",
            "identity.json",
        ]
        jis_config = _find_files_recursive(scan_path, config_patterns)

        if binary_exists:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"JIS Router binary found: {binary_path}",
                score_impact=0,
            )
        elif jis_source:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"JIS Router source found: {jis_source[0].parent}",
                score_impact=0,
            )
        elif jis_config:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message="JIS config found but no router binary/source",
                recommendation="Build or install JIS Router (Rust)",
                score_impact=self.score_weight // 2,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No JIS Router (Rust) integration detected",
            recommendation="Integrate Humotica JIS Router for A-grade compliance",
            references=["https://humotica.com/docs/jis-router"],
            score_impact=self.score_weight,
        )


# =============================================================================
# PILLAR 3: TIBET RUST ENGINE
# =============================================================================

class TIBETEngineCheck(BaseCheck):
    """Check for TIBET Rust engine integration."""
    check_id = "PILLAR-003"
    name = "TIBET Engine Integration"
    description = "Checks for TIBET Rust provenance engine (Humotica Pillar 3)"
    severity = Severity.CRITICAL
    category = "humotica"
    score_weight = 15  # Heavy weight - needed for A-grade

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]

        # Check for tibet-vault or tibet-engine binary
        binary_exists, binary_path = _check_binary_exists([
            "tibet-vault",
            "tibet_vault",
            "tibet-engine",
            "tibet_engine",
            "tibet",
        ])

        # Check for Rust TIBET source
        tibet_patterns = [
            "tibet-vault/Cargo.toml",
            "tibet_vault/Cargo.toml",
            "tibet-engine/Cargo.toml",
            "**/tibet/*.rs",
            "**/tibet-vault/**/*.rs",
        ]
        tibet_source = _find_files_recursive(scan_path, tibet_patterns)

        # Check for TIBET integration in code (Python wrapper, etc.)
        code_files = _find_files_recursive(scan_path, ["*.py", "*.rs", "*.ts"])
        tibet_in_code = False
        tibet_token_found = False

        for code_file in code_files[:50]:
            content = _read_file_sample(code_file)
            if "tibet_vault" in content or "tibet-vault" in content or "TIBETToken" in content:
                tibet_in_code = True
            if "TIBET_V1" in content or "tibet.create_token" in content:
                tibet_token_found = True

        # Check Python package
        try:
            import tibet_vault
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"TIBET vault Python package installed: {tibet_vault.__version__ if hasattr(tibet_vault, '__version__') else 'found'}",
                score_impact=0,
            )
        except ImportError:
            pass

        if binary_exists:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"TIBET engine binary found: {binary_path}",
                score_impact=0,
            )
        elif tibet_source:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"TIBET engine source found: {tibet_source[0].parent}",
                score_impact=0,
            )
        elif tibet_in_code or tibet_token_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message="TIBET referenced in code but engine not found",
                recommendation="Install tibet-vault Rust crate or Python package",
                score_impact=self.score_weight // 2,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No TIBET Rust engine integration detected",
            recommendation="Integrate Humotica TIBET engine for A-grade compliance",
            references=["https://humotica.com/docs/tibet"],
            score_impact=self.score_weight,
        )


# =============================================================================
# BONUS: AETHER INTEGRATION (Svalbard Seedbank)
# =============================================================================

class AETHERIntegrationCheck(BaseCheck):
    """Check for AETHER semantic search integration."""
    check_id = "PILLAR-004"
    name = "AETHER Integration"
    description = "Checks for AETHER semantic search (Svalbard Seedbank)"
    severity = Severity.HIGH
    category = "humotica"
    score_weight = 10

    def run(self, context: dict) -> CheckResult:
        scan_path = context["scan_path"]

        # Check for AETHER/CHIMERA files
        aether_patterns = [
            "aether*.py",
            "aether*.rs",
            "chimera*.rs",
            "semantic_query*.py",
            "*.vectordb",
            "*.faiss",
            "vectors/*.jsonl",
            "CHIM-*.jsonl",
        ]
        aether_files = _find_files_recursive(scan_path, aether_patterns)

        # Check for AETHER in code
        code_files = _find_files_recursive(scan_path, ["*.py", "*.rs"])
        aether_in_code = False

        for code_file in code_files[:30]:
            content = _read_file_sample(code_file)
            if "aether" in content.lower() or "semantic_query" in content or "chimera" in content.lower():
                aether_in_code = True
                break

        if aether_files:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"AETHER integration found: {aether_files[0].name}",
                score_impact=0,
            )
        elif aether_in_code:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message="AETHER referenced but no vector data found",
                recommendation="Run CHIMERA to index your codebase",
                score_impact=self.score_weight // 2,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No AETHER semantic search integration",
            recommendation="Consider AETHER for semantic code search",
            score_impact=self.score_weight // 2,  # Warning, not hard fail
        )


# =============================================================================
# SUMMARY CHECK: THREE PILLARS STATUS
# =============================================================================

class ThreePillarsGateCheck(BaseCheck):
    """Meta-check: Are all three pillars present for A-grade eligibility?"""
    check_id = "PILLAR-000"
    name = "Humotica Three Pillars Gate"
    description = "Verifies all three Humotica pillars for A-grade eligibility"
    severity = Severity.CRITICAL
    category = "humotica"
    score_weight = 0  # No additional penalty, just informational

    def run(self, context: dict) -> CheckResult:
        # This is a summary check - actual scoring is done by individual pillar checks
        # We just provide guidance here

        scan_path = context["scan_path"]

        # Quick checks for each pillar
        # Check scan_path
        has_snaft = bool(_find_files_recursive(scan_path, ["*.snaft", "*.snaft.json", "*.snaft.yaml"]))
        # Also check standard system locations
        if not has_snaft:
            for sys_path in [Path("/etc/snaft"), Path("/opt/humotica/snaft"), Path.home() / ".snaft"]:
                if sys_path.exists() and list(sys_path.glob("*.snaft*")):
                    has_snaft = True
                    break
        has_jis, _ = _check_binary_exists(["jis-router", "jis_router", "chimera"])
        has_tibet, _ = _check_binary_exists(["tibet-vault", "tibet_vault", "tibet"])

        # Also check source directories
        if not has_jis:
            has_jis = bool(_find_files_recursive(scan_path, ["jis-router/Cargo.toml"]))
        if not has_tibet:
            has_tibet = bool(_find_files_recursive(scan_path, ["tibet-vault/Cargo.toml", "tibet_vault/Cargo.toml"]))

        pillars = []
        missing = []

        if has_snaft:
            pillars.append("SNAFT")
        else:
            missing.append("SNAFT")

        if has_jis:
            pillars.append("JIS")
        else:
            missing.append("JIS")

        if has_tibet:
            pillars.append("TIBET")
        else:
            missing.append("TIBET")

        if len(pillars) == 3:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"All three pillars present: {', '.join(pillars)} - A-grade eligible!",
                score_impact=0,
            )
        elif len(pillars) >= 1:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message=f"Pillars: {', '.join(pillars)} | Missing: {', '.join(missing)}",
                recommendation=f"Add {', '.join(missing)} for A-grade eligibility",
                score_impact=0,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No Humotica pillars detected - A-grade not possible",
            recommendation="Integrate SNAFT + JIS Router + TIBET for A-grade",
            references=["https://humotica.com/enterprise"],
            score_impact=0,
        )


# =============================================================================
# EXPORTS
# =============================================================================

HUMOTICA_PILLAR_CHECKS = [
    ThreePillarsGateCheck(),  # Summary first
    SNAFTRulesCheck(),        # Pillar 1
    JISRouterCheck(),         # Pillar 2
    TIBETEngineCheck(),       # Pillar 3
    AETHERIntegrationCheck(), # Bonus
]
