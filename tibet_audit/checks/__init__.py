"""Compliance checks - pluggable check system."""

from .base import BaseCheck, CheckResult, Status, Severity
from .gdpr import GDPR_CHECKS          # EU
from .ai_act import AI_ACT_CHECKS      # EU AI Regulation
from .pipa import PIPA_CHECKS          # South Korea
from .appi import APPI_CHECKS          # Japan
from .pdpa import PDPA_CHECKS          # Singapore
from .privacy_act_au import AU_PRIVACY_CHECKS  # Australia
from .lgpd import LGPD_CHECKS          # Brazil
from .gulf_pdpl import GULF_CHECKS     # Saudi Arabia, UAE, Gulf region
from .ndpr import NDPR_CHECKS          # Nigeria
from .penguin_act import PENGUIN_CHECKS  # Antarctica (Easter egg!)

# All available checks - Global Coverage!
ALL_CHECKS = []
ALL_CHECKS.extend(GDPR_CHECKS)         # 🇪🇺 Europe
ALL_CHECKS.extend(AI_ACT_CHECKS)       # 🇪🇺 EU AI Act
ALL_CHECKS.extend(PIPA_CHECKS)         # 🇰🇷 South Korea
ALL_CHECKS.extend(APPI_CHECKS)         # 🇯🇵 Japan
ALL_CHECKS.extend(PDPA_CHECKS)         # 🇸🇬 Singapore
ALL_CHECKS.extend(AU_PRIVACY_CHECKS)   # 🇦🇺 Australia
ALL_CHECKS.extend(LGPD_CHECKS)         # 🇧🇷 Brazil
ALL_CHECKS.extend(GULF_CHECKS)         # 🇸🇦🇦🇪 Gulf Region
ALL_CHECKS.extend(NDPR_CHECKS)         # 🇳🇬 Nigeria
ALL_CHECKS.extend(PENGUIN_CHECKS)      # 🐧 Antarctica

__all__ = ["BaseCheck", "CheckResult", "Status", "Severity", "ALL_CHECKS"]
