"""EU AI Act Compliance Checks."""

from pathlib import Path
from .base import BaseCheck, CheckResult, Status, Severity, FixAction


class AIActDecisionLoggingCheck(BaseCheck):
    """Check for AI decision audit trail."""

    check_id = "AIACT-001"
    name = "AI Decision Audit Trail"
    description = "Verify AI decisions are logged with provenance"
    severity = Severity.CRITICAL
    category = "ai_act"
    score_weight = 25

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))
        tibet_available = context.get("tibet_available", False)

        # Check for TIBET integration
        tibet_files = list(scan_path.glob("**/tibet*")) + \
                     list(scan_path.glob("**/TIBET*"))

        # Check for general AI logging
        ai_log_patterns = ["ai_log*", "ml_log*", "model_log*", "decision_log*", "audit_log*"]
        ai_logs_found = []

        for pattern in ai_log_patterns:
            ai_logs_found.extend(scan_path.glob(f"**/{pattern}*"))

        # Check source code for logging
        logging_in_code = False
        source_files = list(scan_path.glob("**/*.py"))

        for sf in source_files[:30]:
            try:
                content = sf.read_text()
                if any(term in content for term in ["tibet", "audit_log", "decision_log", "model.predict"]):
                    logging_in_code = True
                    break
            except:
                pass

        if tibet_files or tibet_available:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="TIBET audit trail integration detected",
                score_impact=0
            )

        if ai_logs_found or logging_in_code:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                message="Basic AI logging found, but not TIBET-integrated",
                recommendation="Upgrade to TIBET for cryptographic proof of AI decisions",
                fix_action=FixAction(
                    description="Install TIBET vault for AI audit trails",
                    command="pip install tibet-vault && tibet-vault init",
                    requires_confirmation=True,
                    risk_level="low"
                ),
                references=["EU AI Act Article 12", "https://humotica.com/tibet"],
                score_impact=10
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No AI decision logging found (EU AI Act requires this!)",
            recommendation="Implement TIBET token tracking for AI decisions",
            fix_action=FixAction(
                description="Install TIBET vault for AI audit trails",
                command="pip install tibet-vault && tibet-vault init",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=[
                "EU AI Act Article 12 - Record-keeping",
                "https://humotica.com/tibet"
            ],
            score_impact=self.score_weight
        )


class AIActHumanOversightCheck(BaseCheck):
    """Check for human oversight mechanisms."""

    check_id = "AIACT-002"
    name = "Human Oversight"
    description = "Verify human-in-the-loop mechanisms exist"
    severity = Severity.HIGH
    category = "ai_act"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for human oversight patterns
        oversight_found = False

        source_files = list(scan_path.glob("**/*.py"))
        for sf in source_files[:30]:
            try:
                content = sf.read_text().lower()
                oversight_terms = [
                    "human_review", "manual_review", "approval_required",
                    "human_in_the_loop", "hitl", "manual_override",
                    "requires_approval", "pending_review"
                ]
                if any(term in content for term in oversight_terms):
                    oversight_found = True
                    break
            except:
                pass

        if oversight_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Human oversight mechanisms found in code",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No explicit human oversight mechanisms detected",
            recommendation="Implement human review for high-risk AI decisions",
            references=["EU AI Act Article 14 - Human oversight"],
            score_impact=12
        )


class AIActTransparencyCheck(BaseCheck):
    """Check for AI system transparency."""

    check_id = "AIACT-003"
    name = "AI Transparency"
    description = "Verify AI systems are transparent to users"
    severity = Severity.HIGH
    category = "ai_act"
    score_weight = 15

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for transparency documentation
        transparency_docs = []
        patterns = ["ai-transparency*", "model-card*", "algorithm-info*", "AI_DISCLOSURE*"]

        for pattern in patterns:
            transparency_docs.extend(scan_path.glob(f"**/{pattern}*"))

        # Also check README for AI disclosure
        readmes = list(scan_path.glob("**/README*"))
        ai_disclosed = False

        for readme in readmes[:3]:
            try:
                content = readme.read_text().lower()
                if any(term in content for term in ["ai", "machine learning", "model", "algorithm"]):
                    ai_disclosed = True
                    break
            except:
                pass

        if transparency_docs:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"AI transparency documentation found: {transparency_docs[0].name}",
                score_impact=0
            )

        if ai_disclosed:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=Severity.LOW,
                message="AI mentioned in README but no dedicated transparency doc",
                recommendation="Create a model-card.md with detailed AI system information",
                score_impact=5
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=Severity.MEDIUM,
            message="No AI transparency documentation found",
            recommendation="Create transparency documentation for AI/ML systems",
            references=["EU AI Act Article 13 - Transparency"],
            score_impact=10
        )


class AIActRiskAssessmentCheck(BaseCheck):
    """Check for AI risk assessment."""

    check_id = "AIACT-004"
    name = "AI Risk Assessment"
    description = "Verify AI risk assessment has been performed"
    severity = Severity.HIGH
    category = "ai_act"
    score_weight = 20

    def run(self, context: dict) -> CheckResult:
        scan_path = Path(context.get("scan_path", "."))

        # Look for risk assessment docs
        risk_docs = []
        patterns = ["risk-assessment*", "ai-risk*", "impact-assessment*", "DPIA*", "AIIA*"]

        for pattern in patterns:
            risk_docs.extend(scan_path.glob(f"**/{pattern}*"))

        if risk_docs:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Risk assessment found: {risk_docs[0].name}",
                score_impact=0
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.FAILED,
            severity=self.severity,
            message="No AI risk assessment documentation found",
            recommendation="Perform and document AI Impact Assessment (AIIA)",
            fix_action=FixAction(
                description="Generate risk assessment template",
                command="tibet-audit template ai-risk-assessment > docs/ai-risk-assessment.md",
                requires_confirmation=True,
                risk_level="low"
            ),
            references=["EU AI Act Article 9 - Risk Management"],
            score_impact=self.score_weight
        )


# All AI Act checks
AI_ACT_CHECKS = [
    AIActDecisionLoggingCheck(),
    AIActHumanOversightCheck(),
    AIActTransparencyCheck(),
    AIActRiskAssessmentCheck(),
]
