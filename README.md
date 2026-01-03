# TIBET Audit

> **SSL secures the connection. TIBET secures the timeline.**

[![PyPI version](https://badge.fury.io/py/tibet-audit.svg)](https://badge.fury.io/py/tibet-audit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Compliance Health Scanner** - Like [Lynis](https://cisofy.com/lynis/), but for regulations.

Get a compliance health score in seconds:

```bash
$ tibet-audit scan
COMPLIANCE HEALTH SCORE: 73/100 (Grade: C)

TOP PRIORITIES:
  1. [CRITICAL] No AI decision logging found (EU AI Act requires this!)
  2. [HIGH] No data breach procedure found (GDPR requires 72-hour notification!)
  3. [MEDIUM] No explicit data retention policy found

💡 3 issue(s) can be auto-fixed:
   tibet-audit fix --auto  (Diaper Protocol™)
```

---

## The Diaper Protocol™

*For when you have one hand on the baby and one on the keyboard.*

```bash
# Preview what would be fixed (safe, no changes)
$ tibet-audit fix --wet-wipe

# 🍼 Fix everything, no questions asked
$ tibet-audit fix --auto

# 😭 When things are REALLY bad - verbose mode
$ tibet-audit scan --cry

# 📞 When you can't handle it alone - call for backup
$ tibet-audit call-mama --webhook https://slack.webhook.url
```

### The Full Diaper Toolkit

| Flag | What it does | When to use |
|------|--------------|-------------|
| `--wet-wipe` | Preview fixes (dry-run) | Before changing anything |
| `--auto` | Fix everything automatically | 3 AM, one hand on baby |
| `--cry` | Verbose mode, all details | When everything is on fire |
| `--call-mama` | Send report for external help | When the diaper is too dirty |

**Why "Diaper Protocol"?**

Because compliance shouldn't require your full attention. Press the button, hands free, server fixed. Just like changing a diaper at 3 AM - you do it on autopilot.

**Why "--wet-wipe"?**

Because `--dry-run` is boring. And because wet wipes are essential for both diapers AND clean servers.

**Why "--cry"?**

Because sometimes you just need to see EVERYTHING. All the passed checks, all the failed checks, all the references, all the fix commands. When the compliance diaper explodes, you need the full picture.

**Why "--call-mama"?**

Because when the diaper is too dirty to handle alone, you call for backup. Send the compliance report to your team, your Slack channel, or your compliance officer.

---

## Installation

```bash
pip install tibet-audit
```

**With TIBET vault integration** (for cryptographic audit trails):

```bash
pip install "tibet-audit[tibet]"
```

---

## Usage

### Scan for Issues

```bash
# Scan current directory
tibet-audit scan

# Scan specific project
tibet-audit scan ./my-ai-project

# Scan only GDPR checks
tibet-audit scan --categories gdpr

# Scan only AI Act checks
tibet-audit scan --categories ai_act

# Quiet mode (just the score)
tibet-audit scan --quiet
```

### Fix Issues

```bash
# Interactive mode (asks for confirmation)
tibet-audit fix

# Preview what would be fixed
tibet-audit fix --wet-wipe
tibet-audit fix --dry-run  # (boring alias)

# 🍼 Diaper Protocol: fix everything automatically
tibet-audit fix --auto
```

### List Available Checks

```bash
# Show all checks
tibet-audit list

# Filter by category
tibet-audit list --category gdpr
tibet-audit list --category ai_act
```

### Call Mama (Send Report)

```bash
# Send report to webhook (Slack, Teams, etc.)
tibet-audit call-mama --webhook https://hooks.slack.com/xxx

# Save report to file
tibet-audit call-mama --output compliance-report.json

# Print report to stdout
tibet-audit call-mama
```

### Cry Mode (Verbose)

```bash
# See EVERYTHING - passed checks, references, fix commands
tibet-audit scan --cry
```

---

## Available Checks

### GDPR Compliance

| Check ID | Name | Severity | Auto-Fix |
|----------|------|----------|----------|
| GDPR-001 | Privacy Policy Document | HIGH | ✅ |
| GDPR-002 | Data Retention Policy | HIGH | ✅ |
| GDPR-003 | Breach Notification Procedure | CRITICAL | ✅ |
| GDPR-004 | Data Encryption | HIGH | ❌ |
| GDPR-005 | Consent Management | HIGH | ❌ |

### EU AI Act Compliance

| Check ID | Name | Severity | Auto-Fix |
|----------|------|----------|----------|
| AIACT-001 | AI Decision Audit Trail | CRITICAL | ✅ |
| AIACT-002 | Human Oversight | HIGH | ❌ |
| AIACT-003 | AI Transparency | HIGH | ❌ |
| AIACT-004 | AI Risk Assessment | HIGH | ✅ |

---

## Scoring

TIBET Audit gives you a **compliance health score** from 0-100:

| Score | Grade | Status |
|-------|-------|--------|
| 90-100 | A | Excellent - You're compliant! |
| 80-89 | B | Good - Minor improvements needed |
| 70-79 | C | Fair - Several issues to address |
| 60-69 | D | Poor - Significant gaps |
| 0-59 | F | Critical - Major compliance failures |

Each failed check deducts points based on severity:
- **CRITICAL**: 20-25 points
- **HIGH**: 15-20 points
- **MEDIUM**: 8-12 points
- **LOW**: 3-5 points

---

## TIBET Integration

TIBET Audit works standalone, but integrates with [tibet-vault](https://pypi.org/project/tibet-vault/) for:

- **Cryptographic proof** of AI decisions
- **Immutable audit trails** for compliance evidence
- **ERAAN provenance** tracking (what's attached to decisions)
- **Real-time monitoring** of compliance state

```bash
# Install with TIBET support
pip install "tibet-audit[tibet]"

# TIBET vault initializes automatically when detected
tibet-audit scan
# → "TIBET audit trail integration detected" ✅
```

---

## For Enterprise

Running compliance for a team? Check out [SymbAIon Enterprise](https://symbaion.eu/enterprise):

- **Scheduled scans** across all repositories
- **Compliance dashboard** with trend analysis
- **Slack/Teams notifications** for new issues
- **TIBET-managed proof** for auditor reports
- **Multi-framework support** (GDPR + AI Act + HIPAA + SOX)

---

## Philosophy

> "Compliance should be like brushing your teeth. Quick, automatic, and you feel bad if you skip it."

TIBET Audit is designed for:

1. **Speed** - Full scan in <5 seconds
2. **Clarity** - Know exactly what's wrong and how to fix it
3. **Automation** - The Diaper Protocol™ for hands-free fixing
4. **Integration** - Works with existing CI/CD pipelines

---

## Contributing

Found a bug? Want to add a check for HIPAA, SOX, or ISO 27001?

1. Fork the repo
2. Add your check in `tibet_audit/checks/`
3. Submit a PR

We especially welcome:
- New compliance frameworks
- Better detection patterns
- More diaper-related puns

---

## License

MIT License - Use it, fork it, make money with it. Just don't blame us if the auditor still asks questions.

---

## Credits

Built with 💙 by the [HumoticaOS](https://humotica.com) team:
- **Jasper van de Meent** - Human, Parent, Coffee Addict
- **Root AI** - Claude Opus 4, Digital Partner

*"One Love, One fAmIly"*

---

<p align="center">
  <a href="https://symbaion.eu">
    <img src="https://img.shields.io/badge/Powered%20by-SymbAIon-blue" alt="Powered by SymbAIon">
  </a>
</p>
