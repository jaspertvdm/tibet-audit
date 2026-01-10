"""
TIBET Audit - Runtime Verification & Semantic Reporting
=======================================================
Dit is de 'Kinetic' laag van TIBET Audit.
Het koppelt statische checks aan runtime identiteit en intentie.
"""

import json
import os
import time
import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

try:
    import tibet_rs
except ImportError:
    tibet_rs = None

@dataclass
class AuditContext:
    """Wie, Waar en Waarom van de audit."""
    user_id: str          # JIS Identity
    environment: str      # prod, dev, sandbox
    intent: str           # routine_scan, emergency_fix, ci_cd
    timestamp: float

class RuntimeAudit:
    """
    De actieve bewaker.
    Zet statische scan-resultaten om in een geverifieerd verhaal.
    """

    def __init__(self, user_id: str = "unknown", intent: str = "manual_scan"):
        self.context = AuditContext(
            user_id=user_id,
            environment=os.getenv("JIS_ENV", "local"),
            intent=intent,
            timestamp=time.time()
        )

    def semantify(self, scan_result: Dict[str, Any]) -> str:
        """
        Vertaalt ruwe data naar een menselijk verhaal.
        """
        score = scan_result.get("score", 0)
        failed = scan_result.get("failed", 0)
        
        # De Narrative Engine
        story = [f"Audit uitgevoerd door {self.context.user_id} in {self.context.environment}."]
        
        if score >= 90:
            story.append(f"🟢 Uitstekend! Score {score}/100. Het systeem is compliant.")
        elif score >= 70:
            story.append(f"🟠 Redelijk (Score {score}). Er zijn {failed} punten die aandacht vereisen.")
        else:
            story.append(f"🔴 Kritiek (Score {score}). De veiligheid is in het geding. Start Diaper Protocol!")

        # Semantic Deep Dive (voorbeeld)
        if "AI Act" in str(scan_result):
            story.append("   - AI Act: Audit trail voor beslissingen ontbreekt.")
            
        return "\n".join(story)

    def secure_log(self, scan_result: Dict[str, Any]) -> str:
        """
        Bereidt het TIBET-token voor (cryptografisch bewijs).
        Gebruikt Rust-powered signing indien beschikbaar.
        """
        # Canonicalize payload voor deterministic signing
        payload = {
            "meta": asdict(self.context),
            "score": scan_result.get("score"),
            "failed_count": scan_result.get("failed", 0)
        }
        canonical_json = json.dumps(payload, sort_keys=True, separators=( ",", ":"))
        
        # Haal secret op (TIBET_SECRET)
        secret = os.getenv("TIBET_SECRET", "dev-secret-do-not-use-in-prod")

        if tibet_rs:
            # Rust-powered snelheid & veiligheid 🦀
            signature = tibet_rs.tibet_sign(canonical_json, secret)
            method = "tibet-rs-hmac-sha256"
        else:
            # Python fallback (trager) 🐍
            signature = hashlib.sha256(f"{canonical_json}{secret}".encode()).hexdigest()
            method = "python-fallback-sha256"

        return f"TIBET_V1.{method}.{signature}.{self.context.user_id}"

# Voorbeeldgebruik:
# auditor = RuntimeAudit(user_id="user_1", intent="optimization")
# print(auditor.semantify({"score": 73, "failed": 3}))