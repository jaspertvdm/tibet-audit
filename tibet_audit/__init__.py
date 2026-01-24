"""
TIBET Audit - Compliance Health Scanner
========================================

Like Lynis, but for regulations. Scan your systems, get a score, fix the issues.

The Diaper Protocol™: One command, hands free, compliance done.

    $ tibet-audit scan
    $ tibet-audit fix --auto    # Diaper Protocol: fix everything, no questions
    $ tibet-audit fix --wet-wipe  # Preview what would be fixed (like --dry-run but funnier)

Authors: Jasper van de Meent & Root AI
License: MIT
Website: https://humotica.com

One love, one fAmIly!
"""

__version__ = "0.10.0"  # AETHER Tiers check command + compliance levels
__author__ = "Jasper van de Meent & Root AI"
__email__ = "team@humotica.com"

from .scanner import TIBETAudit
from .checks.base import CheckResult, Status, Severity

__all__ = ["TIBETAudit", "CheckResult", "Status", "Severity"]
