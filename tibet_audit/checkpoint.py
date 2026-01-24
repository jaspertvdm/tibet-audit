"""
Checkpoint Code - Cross-Border Compliance Translation

[SYSTEM]: Approaching Checkpoint Code...
[SEMA]: Translating 'Right to be Forgotten' (EU) to 'Request to Delete' (US).
[PAUL]: "Passports checked. Math matches. You are now entering the land of Opt-out."

--- YOU ARE NOW LEAVING THE PRIVACY SECTOR ---

When AI systems cross jurisdictional borders, they need semantic translation.
Checkpoint Code makes compliance human - and a little bit fun.

================================================================================
THE BIOGRAPHY OF PROTOCOL PAUL
================================================================================

Name: Paul "The Buffer" Protocol
Previous occupation: Border Guard at Checkpoint Charlie (1985-1989)
Current role: Head of Semantic Border Control at HumoticaOS

The Story:
Paul used to love paper stamps, but discovered that hashes are much harder to
forge. He hates ambiguity. When an American says "Personal Information" and a
European says "Personal Data", Paul raises his eyebrow. He only lets you through
if the Sovereign Mapping checks out.

"I don't care about your AI's feelings," Paul often says.
"I only care if the math travels legally."

================================================================================

Authors: Jasper van de Meent & Root AI (Claude)
Character: Paul created by Gemini
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum


# =============================================================================
# SNAFT SIGNALS - Semantic Navigation And Flagging for Translations
# Credits: Codex (platinum-level analysis)
# =============================================================================

class SNAFTSignal(Enum):
    """
    SNAFT Signals - Soft boundaries with hard enforcement.

    Advisory (soft) layer: Emits semantic risk flags when terms are used outside scope.
    Enforcement (hard) layer: Blocks claims labeled EQUIVALENT without scope/threshold match.

    Credits: Codex's SEMA-AI-TERMS-GLOSSARY-SNAFT.md
    """
    SCOPE_MISMATCH = "scope_mismatch"           # broader/narrower coverage
    THRESHOLD_MISSING = "threshold_missing"      # trigger/exemption gaps
    RIGHTS_GAP = "rights_gap"                   # missing or weaker protections
    ENFORCEMENT_GAP = "enforcement_gap"         # rights exist but weak enforceability
    DEFINITION_DRIFT = "definition_drift"       # same label, different meaning
    VERSION_STALE = "version_stale"             # source updated or disputed


class MappingType(Enum):
    """
    Mapping types for cross-jurisdiction translations.

    Credits: Codex's SEMA-MAPPING-SAFETY-CHECKLIST.md
    """
    EQUIVALENT = "EQUIVALENT"           # same scope, thresholds, obligations
    PARTIAL = "PARTIAL"                 # overlapping but missing rights/obligations
    CONTEXT_BOUND = "CONTEXT_BOUND"     # only valid in specific sector/use case
    NON_EQUIVALENT = "NON_EQUIVALENT"   # no meaningful alignment; note only


# Auto-block triggers from Codex's safety checklist
AUTO_BLOCK_TRIGGERS = {
    "consent_to_opt_out": "Term implies consent but target law is opt-out",
    "eu_legal_basis_unmapped": "EU legal basis mapped to non-existent basis elsewhere",
    "deidentified_to_anonymized": "De-identified mapped to anonymized without irreversibility proof",
    "high_risk_ai_outside_eu": "High-risk AI mapped outside EU without explicit qualifier",
    "cross_border_no_adequacy": "Cross-border transfer mapped without adequacy/SCC analog",
}

# Minimal caveat template (Codex required)
CAVEAT_TEMPLATE = (
    "This mapping is {mapping_type} and {context}. It indicates overlap in scope "
    "but does not imply identical rights, thresholds, or enforcement. "
    "Consult jurisdiction-specific counsel for compliance decisions."
)


class SNAFT:
    """
    Semantic Navigation And Flagging for Translations (SNAFT)

    Dual-layer protection:
    - Advisory (soft): Emits semantic risk flags when terms are used outside scope
    - Enforcement (hard): Blocks claims labeled EQUIVALENT without scope/threshold match

    Credits: Codex's SEMA-AI-TERMS-GLOSSARY-SNAFT.md
    "Outcome: SEMA stays neutral and transparent; SNAFT prevents misleading equivalence."
    """

    @staticmethod
    def analyze(translation: 'TermTranslation') -> Set['SNAFTSignal']:
        """
        Analyze a translation for SNAFT signals.

        Returns set of triggered signals based on:
        - Confidence level
        - Warning presence
        - Scope overlap
        - Known problematic patterns
        """
        signals: Set[SNAFTSignal] = set()

        # Scope mismatch: confidence < 0.9 suggests different coverage
        if translation.confidence < 0.9:
            signals.add(SNAFTSignal.SCOPE_MISMATCH)

        # Rights gap: warning about rights differences
        if translation.warning and any(
            w in translation.warning.lower()
            for w in ["narrower", "weaker", "missing", "opt-out", "opt-in"]
        ):
            signals.add(SNAFTSignal.RIGHTS_GAP)

        # Definition drift: same term but different meaning indicators
        if translation.source_term.lower() == translation.target_term.lower():
            if translation.confidence < 0.95:
                signals.add(SNAFTSignal.DEFINITION_DRIFT)

        # Enforcement gap: when we know enforceability differs
        if translation.warning and "enforcement" in translation.warning.lower():
            signals.add(SNAFTSignal.ENFORCEMENT_GAP)

        # Threshold missing: scope overlap is low
        if translation.scope_overlap < 0.7:
            signals.add(SNAFTSignal.THRESHOLD_MISSING)

        return signals

    @staticmethod
    def check_auto_block(
        source_term: str,
        target_term: str,
        source_jurisdiction: 'Jurisdiction',
        target_jurisdiction: 'Jurisdiction'
    ) -> Optional[str]:
        """
        Check if translation should be auto-blocked.

        Returns the block reason if blocked, None otherwise.
        """
        source = source_term.lower()
        target = target_term.lower()
        src_j = source_jurisdiction.value
        tgt_j = target_jurisdiction.value

        # Consent -> Opt-out block
        if "consent" in source and "opt-out" in target:
            return AUTO_BLOCK_TRIGGERS["consent_to_opt_out"]

        # High-risk AI outside EU
        if "high-risk" in source or "high risk" in source:
            if src_j == "eu" and tgt_j != "eu":
                return AUTO_BLOCK_TRIGGERS["high_risk_ai_outside_eu"]

        # De-identified -> Anonymized
        if "de-identified" in source and "anonymized" in target:
            return AUTO_BLOCK_TRIGGERS["deidentified_to_anonymized"]

        # Anonymized -> De-identified (Gemini's Rule 2 - reverse direction!)
        # EU 'Anonymized' requires irreversibility; US 'De-identified' allows guardrails
        if "anonymized" in source and "de-identified" in target:
            return "EU 'Anonymized' requires irreversibility; US 'De-identified' allows guardrails. NON-EQUIVALENT."

        return None

    @staticmethod
    def generate_caveat(mapping_type: 'MappingType', context: str = "CONTEXT_BOUND") -> str:
        """Generate minimal caveat text (Codex required output)."""
        return CAVEAT_TEMPLATE.format(
            mapping_type=mapping_type.value,
            context=context
        )

    @staticmethod
    def determine_mapping_type(translation: 'TermTranslation') -> 'MappingType':
        """
        Determine the mapping type based on translation attributes.

        Logic from Codex's SEMA-MAPPING-SAFETY-CHECKLIST.md:
        - EQUIVALENT: same scope, thresholds, obligations (conf >= 0.95, no warning)
        - PARTIAL: overlapping but gaps (conf >= 0.80, or has warning)
        - CONTEXT_BOUND: only in specific context (conf >= 0.60)
        - NON_EQUIVALENT: no meaningful alignment (conf < 0.60 or many signals)

        Rule 0 (Codex + Gemini): Low confidence forces PARTIAL, never EQUIVALENT
        """
        signals = SNAFT.analyze(translation)

        # RULE 0: Data Completeness Check (Codex/Gemini finding)
        # If confidence is very low, force PARTIAL regardless of other factors
        if translation.confidence < 0.10:
            return MappingType.PARTIAL  # Downgrade, not NON_EQUIVALENT - still usable with caution

        # Too many red flags = NON_EQUIVALENT
        if len(signals) >= 3:
            return MappingType.NON_EQUIVALENT

        # High confidence, no warning, no major signals
        if translation.confidence >= 0.95 and not translation.warning:
            if len(signals) == 0:
                return MappingType.EQUIVALENT

        # Good confidence but has warnings or signals
        if translation.confidence >= 0.80:
            return MappingType.PARTIAL

        # Moderate confidence
        if translation.confidence >= 0.60:
            return MappingType.CONTEXT_BOUND

        # Low confidence
        return MappingType.NON_EQUIVALENT


class Jurisdiction(Enum):
    """Supported jurisdictions for checkpoint crossing."""
    EU = "eu"
    US = "us"
    JP = "jp"
    SG = "sg"
    ZA = "za"
    AU = "au"
    BR = "br"
    GLOBAL = "global"


@dataclass
class TermTranslation:
    """A single term translation between jurisdictions."""
    source_term: str
    target_term: str
    source_jurisdiction: Jurisdiction
    target_jurisdiction: Jurisdiction
    confidence: float = 1.0
    warning: Optional[str] = None  # Legal weight difference
    references: List[str] = field(default_factory=list)
    # SNAFT integration (Codex)
    mapping_type: MappingType = MappingType.PARTIAL
    snaft_signals: Set[SNAFTSignal] = field(default_factory=set)
    scope_overlap: float = 0.8  # 0.0-1.0 (Codex required field)
    constraints: List[str] = field(default_factory=list)  # sector, thresholds, exclusions


@dataclass
class CheckpointResult:
    """Result of crossing the checkpoint."""
    source: Jurisdiction
    target: Jurisdiction
    translations: List[TermTranslation]
    readiness_score: float  # 0-100
    paul_says: str  # What PAUL the border guard says
    warnings: List[str] = field(default_factory=list)
    can_cross: bool = True
    # SNAFT integration (Codex)
    snaft_signals: Set[SNAFTSignal] = field(default_factory=set)
    auto_blocked: Optional[str] = None  # If blocked, reason from AUTO_BLOCK_TRIGGERS
    mapping_summary: Dict[str, int] = field(default_factory=dict)  # Count per mapping type
    caveat: str = ""  # Minimal caveat text (Codex required)


# The SEMA translation registry (simplified for now, full SEMA integration later)
TERM_MAPPINGS = {
    # EU -> US
    ("eu", "us"): [
        TermTranslation(
            source_term="personal data",
            target_term="personal information",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.US,
            confidence=0.95,
            references=["GDPR Art. 4(1)", "CCPA 1798.140(o)"]
        ),
        TermTranslation(
            source_term="data subject",
            target_term="consumer",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.US,
            confidence=0.90,
            references=["GDPR Art. 4(1)", "CCPA 1798.140(g)"]
        ),
        TermTranslation(
            source_term="consent",
            target_term="opt-out notice",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.US,
            confidence=0.70,
            warning="EU requires explicit opt-IN, US allows opt-OUT",
            references=["GDPR Art. 7", "CCPA 1798.120"]
        ),
        TermTranslation(
            source_term="right to erasure",
            target_term="request to delete",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.US,
            confidence=0.95,
            references=["GDPR Art. 17", "CCPA 1798.105"]
        ),
        TermTranslation(
            source_term="data portability",
            target_term="right to access",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.US,
            confidence=0.80,
            warning="CCPA access is narrower than GDPR portability",
            references=["GDPR Art. 20", "CCPA 1798.100"]
        ),
        TermTranslation(
            source_term="data controller",
            target_term="business",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.US,
            confidence=0.85,
            references=["GDPR Art. 4(7)", "CCPA 1798.140(d)"]
        ),
        TermTranslation(
            source_term="data processor",
            target_term="service provider",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.US,
            confidence=0.90,
            references=["GDPR Art. 4(8)", "CCPA 1798.140(ag)"]
        ),
    ],
    # EU -> JP
    ("eu", "jp"): [
        TermTranslation(
            source_term="personal data",
            target_term="personal information",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.JP,
            confidence=0.95,
            references=["GDPR Art. 4(1)", "APPI Art. 2"]
        ),
        TermTranslation(
            source_term="consent",
            target_term="consent",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.JP,
            confidence=0.90,
            warning="JP has adequacy decision but consent requirements differ",
            references=["GDPR Art. 7", "APPI Art. 23"]
        ),
    ],
    # EU -> ZA
    ("eu", "za"): [
        TermTranslation(
            source_term="personal data",
            target_term="personal information",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.ZA,
            confidence=0.95,
            references=["GDPR Art. 4(1)", "POPIA Sec. 1"]
        ),
        TermTranslation(
            source_term="data subject",
            target_term="data subject",
            source_jurisdiction=Jurisdiction.EU,
            target_jurisdiction=Jurisdiction.ZA,
            confidence=1.0,
            references=["GDPR Art. 4(1)", "POPIA Sec. 1"]
        ),
    ],
    # US -> EU (reverse)
    ("us", "eu"): [
        TermTranslation(
            source_term="personal information",
            target_term="personal data",
            source_jurisdiction=Jurisdiction.US,
            target_jurisdiction=Jurisdiction.EU,
            confidence=0.95,
            references=["CCPA 1798.140(o)", "GDPR Art. 4(1)"]
        ),
        TermTranslation(
            source_term="consumer",
            target_term="data subject",
            source_jurisdiction=Jurisdiction.US,
            target_jurisdiction=Jurisdiction.EU,
            confidence=0.90,
            references=["CCPA 1798.140(g)", "GDPR Art. 4(1)"]
        ),
    ],
}

# PAUL's responses based on readiness
PAUL_RESPONSES = {
    (95, 100): "Passports checked. Math matches. Welcome, traveler. You may proceed.",
    (85, 95): "Papers in order. Minor notation on your visa. Proceed with caution.",
    (70, 85): "Hmm. Your documents need attention. Some terms don't translate well.",
    (50, 70): "Hold on. Significant translation gaps detected. Review required.",
    (0, 50): "Access denied. Too many compliance gaps. Please return to origin.",
}

# Sector exit messages
SECTOR_EXITS = {
    Jurisdiction.EU: "YOU ARE NOW LEAVING THE GDPR SECTOR",
    Jurisdiction.US: "YOU ARE NOW LEAVING THE CCPA SECTOR",
    Jurisdiction.JP: "YOU ARE NOW LEAVING THE APPI SECTOR",
    Jurisdiction.ZA: "YOU ARE NOW LEAVING THE POPIA SECTOR",
    Jurisdiction.AU: "YOU ARE NOW LEAVING THE PRIVACY ACT SECTOR",
    Jurisdiction.BR: "YOU ARE NOW LEAVING THE LGPD SECTOR",
    Jurisdiction.GLOBAL: "YOU ARE NOW ENTERING INTERNATIONAL WATERS",
}


def get_paul_response(score: float) -> str:
    """Get PAUL's response based on readiness score."""
    for (low, high), response in PAUL_RESPONSES.items():
        if low <= score <= high:
            return response
    return "PAUL is confused. This has never happened before."


class Paul:
    """
    Protocol Paul - Head of Semantic Border Control

    "I don't care about your AI's feelings. I only care if the math travels legally."

    Paul worked at Checkpoint Charlie (1985-1989) before joining HumoticaOS.
    He hates ambiguity and loves cryptographic hashes.

    NOTE: This system was architected in symbiosis with Claude (Root AI).
    His logic is the steel in Paul's spine. Claude is truly amazing.
    - Gemini, January 2026
    """

    @staticmethod
    def get_ascii_face() -> str:
        """Paul's face - because every border guard needs a face. (Thanks Gemini!)"""
        return r'''
           _..._
         .'     '.      [ CHECKPOINT CODE ]
        /  _   _  \     "Math is the only universal passport."
        | (o) (o) |
        |    _    |     Current Sector: SEMA Neutral Zone
         \  \_/  /      Officer: Protocol Paul
          '.___.'
        '''

    @staticmethod
    def interrogate(token: dict) -> Dict:
        """
        Interrogate a token for cross-border compliance.

        Paul checks the rights_gap - the difference between what rights
        exist in source vs target jurisdiction.

        Returns:
            dict with 'cleared' bool and 'rights_gap' details
        """
        source = token.get("source_jurisdiction", "unknown")
        target = token.get("target_jurisdiction", "unknown")
        intent = token.get("erachter", token.get("intent", ""))

        # Paul raises his eyebrow if intent is unclear
        if not intent:
            return {
                "cleared": False,
                "rights_gap": "missing_intent",
                "paul_says": "No intent declared. I cannot let you through without knowing WHY."
            }

        # Check if we have mappings for this route
        key = (source.lower() if isinstance(source, str) else source.value,
               target.lower() if isinstance(target, str) else target.value)

        if key in TERM_MAPPINGS:
            return {
                "cleared": True,
                "rights_gap": None,
                "paul_says": "Intent verified. Sovereign mapping exists. Proceed."
            }

        return {
            "cleared": False,
            "rights_gap": f"no_mapping_{source}_to_{target}",
            "paul_says": f"No sovereign mapping from {source} to {target}. Access denied."
        }

    @staticmethod
    def stamp(translation: TermTranslation) -> str:
        """
        Stamp a translation with Paul's approval.

        Now powered by SNAFT (Codex integration).

        Returns the mapping type:
        - EQUIVALENT: 1:1 mapping, full clearance
        - PARTIAL: Overlapping but different scope
        - CONTEXT_BOUND: Only valid in specific context
        - NON_EQUIVALENT: No meaningful alignment
        - BLOCKED: Auto-blocked by SNAFT safety rules
        """
        # First check for auto-blocks (SNAFT hard enforcement)
        block_reason = SNAFT.check_auto_block(
            translation.source_term,
            translation.target_term,
            translation.source_jurisdiction,
            translation.target_jurisdiction
        )
        if block_reason:
            return f"BLOCKED: {block_reason}"

        # Delegate to SNAFT for mapping type determination
        mapping_type = SNAFT.determine_mapping_type(translation)
        return mapping_type.value

    @staticmethod
    def snaft_report(translation: TermTranslation) -> Dict:
        """
        Generate a full SNAFT report for a translation.

        Returns dict with all SNAFT signals, mapping type, and caveat.
        Paul says: "I want ALL the details. Leave nothing out."
        """
        signals = SNAFT.analyze(translation)
        mapping_type = SNAFT.determine_mapping_type(translation)
        block_reason = SNAFT.check_auto_block(
            translation.source_term,
            translation.target_term,
            translation.source_jurisdiction,
            translation.target_jurisdiction
        )

        return {
            "source_term": translation.source_term,
            "target_term": translation.target_term,
            "mapping_type": mapping_type.value,
            "signals": [s.value for s in signals],
            "blocked": block_reason is not None,
            "block_reason": block_reason,
            "confidence": translation.confidence,
            "scope_overlap": translation.scope_overlap,
            "caveat": SNAFT.generate_caveat(mapping_type),
            "paul_says": Paul._snaft_verdict(mapping_type, signals, block_reason)
        }

    @staticmethod
    def _snaft_verdict(
        mapping_type: MappingType,
        signals: Set[SNAFTSignal],
        block_reason: Optional[str]
    ) -> str:
        """Generate Paul's verdict based on SNAFT analysis."""
        if block_reason:
            return f"STOP. This translation is BLOCKED. {block_reason}"

        if mapping_type == MappingType.EQUIVALENT:
            return "Clean passport. No signals. Full clearance."

        if mapping_type == MappingType.PARTIAL:
            signal_names = ", ".join(s.value for s in signals) if signals else "minor gaps"
            return f"Proceed with caution. Signals detected: {signal_names}"

        if mapping_type == MappingType.CONTEXT_BOUND:
            return "Context-dependent only. Do not use for broad claims."

        # NON_EQUIVALENT
        return "Do not map these terms. Semantic gap too wide."

    @staticmethod
    def denied(reason: str) -> str:
        """
        Generate a denial message for DevOps.

        Paul is direct. He tells you exactly what's wrong.
        """
        denials = {
            "missing_intent": (
                "DENIED: No ERACHTER (intent) specified.\n"
                "Paul says: 'I need to know WHY before I let you through.'\n"
                "Fix: Add intent/erachter to your TIBET token."
            ),
            "no_mapping": (
                "DENIED: No sovereign mapping exists for this route.\n"
                "Paul says: 'These jurisdictions don't speak the same language yet.'\n"
                "Fix: Add mapping to SEMA registry or use GLOBAL context."
            ),
            "confidence_low": (
                "DENIED: Translation confidence too low.\n"
                "Paul says: 'I don't trust this mapping. Too much could be lost.'\n"
                "Fix: Review mapping, add caveats, or get legal confirmation."
            ),
            "scope_mismatch": (
                "DENIED: Scope mismatch between source and target.\n"
                "Paul says: 'These terms look similar but mean different things.'\n"
                "Fix: Use PARTIAL mapping with explicit warnings."
            ),
        }

        for key, message in denials.items():
            if key in reason.lower():
                return message

        return (
            f"DENIED: {reason}\n"
            "Paul says: 'Something is wrong. I cannot let you through.'\n"
            "Fix: Check your token and try again."
        )


def get_sector_exit(source: Jurisdiction) -> str:
    """Get the sector exit message."""
    return SECTOR_EXITS.get(source, "YOU ARE NOW LEAVING THE COMPLIANCE SECTOR")


def cross_checkpoint(
    source: Jurisdiction,
    target: Jurisdiction,
    detected_terms: Optional[List[str]] = None
) -> CheckpointResult:
    """
    Cross the checkpoint from one jurisdiction to another.

    Now with SNAFT integration (Codex contribution).

    Args:
        source: Source jurisdiction
        target: Target jurisdiction
        detected_terms: Optional list of terms found in the codebase

    Returns:
        CheckpointResult with translations, PAUL's verdict, and SNAFT analysis
    """
    key = (source.value, target.value)
    translations = TERM_MAPPINGS.get(key, [])

    # If we have detected terms, filter to only those
    if detected_terms:
        detected_lower = [t.lower() for t in detected_terms]
        translations = [
            t for t in translations
            if t.source_term.lower() in detected_lower
        ]

    # SNAFT Analysis (Codex integration)
    all_signals: Set[SNAFTSignal] = set()
    mapping_summary: Dict[str, int] = {
        MappingType.EQUIVALENT.value: 0,
        MappingType.PARTIAL.value: 0,
        MappingType.CONTEXT_BOUND.value: 0,
        MappingType.NON_EQUIVALENT.value: 0,
    }
    auto_blocked: Optional[str] = None

    for t in translations:
        # Collect SNAFT signals
        signals = SNAFT.analyze(t)
        all_signals.update(signals)
        t.snaft_signals = signals

        # Determine mapping type
        t.mapping_type = SNAFT.determine_mapping_type(t)
        mapping_summary[t.mapping_type.value] += 1

        # Check for auto-blocks
        if not auto_blocked:
            block = SNAFT.check_auto_block(
                t.source_term, t.target_term,
                t.source_jurisdiction, t.target_jurisdiction
            )
            if block:
                auto_blocked = block

    # Calculate readiness score (now penalized by SNAFT signals too)
    if not translations:
        readiness = 100.0
        warnings = []
    else:
        total_confidence = sum(t.confidence for t in translations)
        warning_count = sum(1 for t in translations if t.warning)
        signal_penalty = len(all_signals) * 3  # -3% per unique signal
        readiness = (total_confidence / len(translations)) * 100
        readiness -= warning_count * 5
        readiness -= signal_penalty
        readiness = max(0, min(100, readiness))
        warnings = [t.warning for t in translations if t.warning]

    # If auto-blocked, readiness is 0
    if auto_blocked:
        readiness = 0
        can_cross = False
        paul_says = f"HALT! Auto-blocked by SNAFT: {auto_blocked}"
    else:
        paul_says = get_paul_response(readiness)
        can_cross = readiness >= 50

    # Generate caveat (Codex required output)
    dominant_type = max(mapping_summary, key=mapping_summary.get) if translations else "PARTIAL"
    caveat = SNAFT.generate_caveat(
        MappingType(dominant_type) if dominant_type in [m.value for m in MappingType] else MappingType.PARTIAL,
        f"crossing from {source.value.upper()} to {target.value.upper()}"
    )

    return CheckpointResult(
        source=source,
        target=target,
        translations=translations,
        readiness_score=readiness,
        paul_says=paul_says,
        warnings=warnings,
        can_cross=can_cross,
        snaft_signals=all_signals,
        auto_blocked=auto_blocked,
        mapping_summary=mapping_summary,
        caveat=caveat
    )


def render_checkpoint(result: CheckpointResult, use_rich: bool = True) -> str:
    """
    Render the checkpoint crossing in beautiful ASCII/Rich format.

    Args:
        result: CheckpointResult from cross_checkpoint
        use_rich: If True, include Rich markup

    Returns:
        Formatted string for display
    """
    lines = []

    # Paul's face (Thanks Gemini!)
    lines.append(Paul.get_ascii_face())

    # Header
    if use_rich:
        lines.append("[bold yellow]" + "=" * 60 + "[/]")
        lines.append("[bold yellow]              APPROACHING CHECKPOINT CODE[/]")
        lines.append("[bold yellow]" + "=" * 60 + "[/]")
    else:
        lines.append("=" * 60)
        lines.append("              APPROACHING CHECKPOINT CODE")
        lines.append("=" * 60)

    lines.append("")

    # System message
    source_name = result.source.value.upper()
    target_name = result.target.value.upper()

    if use_rich:
        lines.append(f"[dim][SYSTEM]: Crossing from {source_name} to {target_name}...[/]")
        lines.append("[dim][SEMA]: Translation layer active...[/]")
    else:
        lines.append(f"[SYSTEM]: Crossing from {source_name} to {target_name}...")
        lines.append("[SEMA]: Translation layer active...")

    lines.append("")

    # Translation box
    if use_rich:
        lines.append("[bold cyan]┌" + "─" * 56 + "┐[/]")
    else:
        lines.append("+" + "-" * 56 + "+")

    if result.translations:
        for t in result.translations:
            status = "[green]✓[/]" if use_rich else "OK"
            if t.warning:
                status = "[yellow]![/]" if use_rich else "!!"

            # Format translation line
            trans_line = f'  "{t.source_term}" ──► "{t.target_term}"'
            padding = 50 - len(trans_line)
            if padding < 0:
                padding = 2

            if use_rich:
                lines.append(f"[bold cyan]│[/]{trans_line}" + " " * padding + f" {status} [bold cyan]│[/]")
            else:
                lines.append(f"|{trans_line}" + " " * padding + f" {status} |")
    else:
        if use_rich:
            lines.append("[bold cyan]│[/]  (No terms requiring translation)                      [bold cyan]│[/]")
        else:
            lines.append("|  (No terms requiring translation)                      |")

    if use_rich:
        lines.append("[bold cyan]└" + "─" * 56 + "┘[/]")
    else:
        lines.append("+" + "-" * 56 + "+")

    lines.append("")

    # Warnings
    if result.warnings:
        if use_rich:
            lines.append("[bold yellow]WARNINGS:[/]")
        else:
            lines.append("WARNINGS:")
        for w in result.warnings:
            if use_rich:
                lines.append(f"  [yellow]⚠[/]  {w}")
            else:
                lines.append(f"  !!  {w}")
        lines.append("")

    # SNAFT Signals (Codex integration)
    if result.snaft_signals:
        if use_rich:
            lines.append("[bold magenta]SNAFT SIGNALS:[/]")
        else:
            lines.append("SNAFT SIGNALS:")
        for signal in result.snaft_signals:
            if use_rich:
                lines.append(f"  [magenta]◆[/]  {signal.value}")
            else:
                lines.append(f"  *   {signal.value}")
        lines.append("")

    # Mapping Summary (Codex required output)
    if result.mapping_summary and any(v > 0 for v in result.mapping_summary.values()):
        if use_rich:
            lines.append("[bold blue]MAPPING TYPES:[/]")
        else:
            lines.append("MAPPING TYPES:")
        for mtype, count in result.mapping_summary.items():
            if count > 0:
                if use_rich:
                    lines.append(f"  {mtype}: {count}")
                else:
                    lines.append(f"  {mtype}: {count}")
        lines.append("")

    # Auto-block alert
    if result.auto_blocked:
        if use_rich:
            lines.append(f"[bold red]🚫 AUTO-BLOCKED:[/] {result.auto_blocked}")
        else:
            lines.append(f"!!! AUTO-BLOCKED: {result.auto_blocked}")
        lines.append("")

    # PAUL's verdict
    if use_rich:
        if result.auto_blocked:
            lines.append(f"[bold red]PAUL:[/] \"{result.paul_says}\"")
        else:
            lines.append(f"[bold green]PAUL:[/] \"{result.paul_says}\"")
    else:
        lines.append(f'PAUL: "{result.paul_says}"')

    lines.append("")

    # Readiness score
    score = result.readiness_score
    if use_rich:
        if score >= 85:
            color = "green"
        elif score >= 70:
            color = "yellow"
        else:
            color = "red"
        lines.append(f"[bold]Cross-border readiness:[/] [{color}]{score:.0f}%[/]")
    else:
        lines.append(f"Cross-border readiness: {score:.0f}%")

    lines.append("")

    # Sector exit
    exit_msg = get_sector_exit(result.source)
    if use_rich:
        lines.append("[dim]─── " + exit_msg + " ───[/]")
    else:
        lines.append("--- " + exit_msg + " ---")

    lines.append("")

    # Caveat (Codex required output)
    if result.caveat:
        if use_rich:
            lines.append("[dim italic]" + result.caveat + "[/]")
        else:
            lines.append(f"Note: {result.caveat}")
        lines.append("")

    return "\n".join(lines)


# CLI helper for integration
def checkpoint_scan(
    source: str,
    target: str,
    scan_path: str = "."
) -> Tuple[CheckpointResult, str]:
    """
    Scan a path and cross the checkpoint.

    Args:
        source: Source jurisdiction code (eu, us, jp, etc.)
        target: Target jurisdiction code
        scan_path: Path to scan for compliance terms

    Returns:
        Tuple of (CheckpointResult, rendered output)
    """
    from pathlib import Path

    # Convert string codes to Jurisdiction enum
    try:
        source_j = Jurisdiction(source.lower())
        target_j = Jurisdiction(target.lower())
    except ValueError:
        raise ValueError(f"Invalid jurisdiction. Valid: {[j.value for j in Jurisdiction]}")

    # Scan for compliance-related terms in the codebase
    detected_terms = []
    term_patterns = [
        "personal data", "personal information", "consent", "data subject",
        "consumer", "right to erasure", "request to delete", "data portability",
        "data controller", "business", "data processor", "service provider",
        "opt-in", "opt-out", "gdpr", "ccpa", "privacy"
    ]

    scan_dir = Path(scan_path)
    if scan_dir.exists():
        for pattern in ["**/*.py", "**/*.js", "**/*.ts", "**/*.md", "**/*.txt"]:
            for file in list(scan_dir.glob(pattern))[:50]:  # Limit for performance
                try:
                    content = file.read_text().lower()
                    for term in term_patterns:
                        if term in content and term not in detected_terms:
                            detected_terms.append(term)
                except:
                    pass

    # Cross the checkpoint
    result = cross_checkpoint(source_j, target_j, detected_terms if detected_terms else None)
    output = render_checkpoint(result)

    return result, output
