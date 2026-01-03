"""Compliance checks - pluggable check system."""

from .base import BaseCheck, CheckResult, Status, Severity
from .gdpr import GDPR_CHECKS
from .ai_act import AI_ACT_CHECKS
from .pipa import PIPA_CHECKS  # South Korea
from .appi import APPI_CHECKS  # Japan
from .pdpa import PDPA_CHECKS  # Singapore
from .privacy_act_au import AU_PRIVACY_CHECKS  # Australia
from .penguin_act import PENGUIN_CHECKS  # Antarctica (Easter egg!)

# All available checks
ALL_CHECKS = []
ALL_CHECKS.extend(GDPR_CHECKS)
ALL_CHECKS.extend(AI_ACT_CHECKS)
ALL_CHECKS.extend(PIPA_CHECKS)
ALL_CHECKS.extend(APPI_CHECKS)
ALL_CHECKS.extend(PDPA_CHECKS)
ALL_CHECKS.extend(AU_PRIVACY_CHECKS)
ALL_CHECKS.extend(PENGUIN_CHECKS)

__all__ = ["BaseCheck", "CheckResult", "Status", "Severity", "ALL_CHECKS"]
