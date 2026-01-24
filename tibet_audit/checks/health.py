"""System Health & Energy checks - Ben je wel gezond bezig?

This module checks for system health, energy consumption, and sustainability.
Inspired by Lynis system hardening, but with a Humotica twist.

Categories:
- Energy consumption monitoring
- Resource efficiency
- Sustainability practices
- System health indicators
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from .base import BaseCheck, CheckResult, Status, Severity, FixAction


def _run_command(cmd: List[str], timeout: int = 5) -> Tuple[bool, str]:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout + result.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        return False, str(e)


def _get_cpu_power_estimate() -> Optional[float]:
    """Estimate current CPU power consumption in watts."""
    # Try Intel RAPL (Running Average Power Limit)
    rapl_path = Path("/sys/class/powercap/intel-rapl")
    if rapl_path.exists():
        try:
            # Read package energy in microjoules
            for domain in rapl_path.iterdir():
                if domain.name.startswith("intel-rapl:"):
                    energy_file = domain / "energy_uj"
                    if energy_file.exists():
                        # This is cumulative energy, we'd need two readings
                        # For now, just return that RAPL is available
                        return -1.0  # Indicates RAPL available
        except Exception:
            pass

    # Try reading from /proc/cpuinfo for frequency
    try:
        with open("/proc/cpuinfo") as f:
            content = f.read()
            # Count cores and look for frequency
            cores = content.count("processor\t:")
            # Rough estimate: 5-15W per core at load
            return cores * 10.0  # Rough estimate
    except Exception:
        pass

    return None


def _get_memory_usage() -> Optional[dict]:
    """Get memory usage info."""
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()

        info = {}
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().split()[0]  # Get numeric part
                try:
                    info[key] = int(value)
                except ValueError:
                    pass

        total = info.get("MemTotal", 0)
        available = info.get("MemAvailable", 0)
        used = total - available

        return {
            "total_kb": total,
            "available_kb": available,
            "used_kb": used,
            "percent_used": round(used / total * 100, 1) if total > 0 else 0
        }
    except Exception:
        return None


def _get_disk_usage(path: str = "/") -> Optional[dict]:
    """Get disk usage info."""
    try:
        stat = os.statvfs(path)
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_bavail * stat.f_frsize
        used = total - free

        return {
            "total_gb": round(total / (1024**3), 1),
            "free_gb": round(free / (1024**3), 1),
            "used_gb": round(used / (1024**3), 1),
            "percent_used": round(used / total * 100, 1) if total > 0 else 0
        }
    except Exception:
        return None


def _get_load_average() -> Optional[Tuple[float, float, float]]:
    """Get system load average."""
    try:
        return os.getloadavg()
    except Exception:
        return None


def _get_cpu_count() -> int:
    """Get number of CPU cores."""
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1


# =============================================================================
# ENERGY CHECKS
# =============================================================================

class EnergyMonitoringCheck(BaseCheck):
    """Check if energy monitoring tools are available."""
    check_id = "HEALTH-001"
    name = "Energy monitoring capability"
    description = "Checks for energy/power monitoring tools (RAPL, powertop, etc.)"
    severity = Severity.LOW
    category = "health"
    score_weight = 3

    def run(self, context: dict) -> CheckResult:
        tools_found = []

        # Check Intel RAPL
        rapl_path = Path("/sys/class/powercap/intel-rapl")
        if rapl_path.exists():
            tools_found.append("Intel RAPL")

        # Check for powertop
        success, _ = _run_command(["which", "powertop"])
        if success:
            tools_found.append("powertop")

        # Check for turbostat
        success, _ = _run_command(["which", "turbostat"])
        if success:
            tools_found.append("turbostat")

        # Check for s-tui
        success, _ = _run_command(["which", "s-tui"])
        if success:
            tools_found.append("s-tui")

        if tools_found:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Energy monitoring available: {', '.join(tools_found)}",
                score_impact=0,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No energy monitoring tools found",
            recommendation="Install powertop or s-tui for energy monitoring",
            fix_action=FixAction(
                description="Install powertop for energy analysis",
                command="apt install powertop -y",
            ),
            score_impact=self.score_weight,
        )


class CPUGovernorCheck(BaseCheck):
    """Check CPU frequency governor for efficiency."""
    check_id = "HEALTH-002"
    name = "CPU frequency governor"
    description = "Checks if CPU governor is set for efficiency"
    severity = Severity.LOW
    category = "health"
    score_weight = 2

    def run(self, context: dict) -> CheckResult:
        governors = []
        gov_path = Path("/sys/devices/system/cpu")

        if not gov_path.exists():
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message="CPU governor info not available",
                score_impact=0,
            )

        try:
            for cpu in gov_path.iterdir():
                if cpu.name.startswith("cpu") and cpu.name[3:].isdigit():
                    gov_file = cpu / "cpufreq" / "scaling_governor"
                    if gov_file.exists():
                        gov = gov_file.read_text().strip()
                        if gov not in governors:
                            governors.append(gov)
        except Exception as e:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message=f"Could not read governor: {e}",
                score_impact=0,
            )

        if not governors:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message="No CPU governors found",
                score_impact=0,
            )

        # Efficient governors
        efficient = ["powersave", "conservative", "ondemand", "schedutil"]
        performance = ["performance"]

        if all(g in efficient for g in governors):
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"CPU governor(s): {', '.join(governors)} (energy efficient)",
                score_impact=0,
            )
        elif any(g in performance for g in governors):
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message=f"CPU governor: {', '.join(governors)} (performance mode - high energy)",
                recommendation="Consider using 'schedutil' or 'ondemand' for better efficiency",
                score_impact=self.score_weight,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message=f"CPU governor(s): {', '.join(governors)}",
            score_impact=0,
        )


# =============================================================================
# RESOURCE EFFICIENCY CHECKS
# =============================================================================

class MemoryUsageCheck(BaseCheck):
    """Check memory usage levels."""
    check_id = "HEALTH-003"
    name = "Memory usage"
    description = "Checks current memory utilization"
    severity = Severity.MEDIUM
    category = "health"
    score_weight = 4

    def run(self, context: dict) -> CheckResult:
        mem = _get_memory_usage()

        if not mem:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message="Could not read memory info",
                score_impact=0,
            )

        pct = mem["percent_used"]
        total_gb = round(mem["total_kb"] / (1024 * 1024), 1)
        used_gb = round(mem["used_kb"] / (1024 * 1024), 1)

        if pct < 70:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Memory usage: {pct}% ({used_gb}/{total_gb} GB)",
                score_impact=0,
            )
        elif pct < 85:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message=f"Memory usage elevated: {pct}% ({used_gb}/{total_gb} GB)",
                recommendation="Consider adding more RAM or optimizing memory usage",
                score_impact=self.score_weight // 2,
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.FAILED,
                severity=self.severity,
                message=f"Memory usage critical: {pct}% ({used_gb}/{total_gb} GB)",
                recommendation="System may be under memory pressure - investigate processes",
                score_impact=self.score_weight,
            )


class DiskUsageCheck(BaseCheck):
    """Check disk usage levels."""
    check_id = "HEALTH-004"
    name = "Disk usage"
    description = "Checks disk space utilization"
    severity = Severity.HIGH
    category = "health"
    score_weight = 5

    def run(self, context: dict) -> CheckResult:
        disk = _get_disk_usage("/")

        if not disk:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message="Could not read disk info",
                score_impact=0,
            )

        pct = disk["percent_used"]

        if pct < 80:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Disk usage: {pct}% ({disk['used_gb']}/{disk['total_gb']} GB)",
                score_impact=0,
            )
        elif pct < 90:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message=f"Disk usage elevated: {pct}% ({disk['free_gb']} GB free)",
                recommendation="Clean up disk space or expand storage",
                score_impact=self.score_weight // 2,
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.FAILED,
                severity=self.severity,
                message=f"Disk usage critical: {pct}% ({disk['free_gb']} GB free)",
                recommendation="URGENT: Clean up disk space immediately",
                score_impact=self.score_weight,
            )


class LoadAverageCheck(BaseCheck):
    """Check system load average."""
    check_id = "HEALTH-005"
    name = "System load average"
    description = "Checks CPU load relative to core count"
    severity = Severity.MEDIUM
    category = "health"
    score_weight = 4

    def run(self, context: dict) -> CheckResult:
        load = _get_load_average()
        cpu_count = _get_cpu_count()

        if not load:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message="Could not read load average",
                score_impact=0,
            )

        load_1, load_5, load_15 = load
        # Load relative to CPU count
        relative_load = load_5 / cpu_count

        if relative_load < 0.7:
            status = Status.PASSED
            msg = f"Load: {load_1:.2f}/{load_5:.2f}/{load_15:.2f} ({cpu_count} cores) - healthy"
            impact = 0
        elif relative_load < 1.0:
            status = Status.WARNING
            msg = f"Load: {load_1:.2f}/{load_5:.2f}/{load_15:.2f} ({cpu_count} cores) - moderate"
            impact = self.score_weight // 2
        else:
            status = Status.FAILED
            msg = f"Load: {load_1:.2f}/{load_5:.2f}/{load_15:.2f} ({cpu_count} cores) - HIGH"
            impact = self.score_weight

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=status,
            severity=self.severity,
            message=msg,
            recommendation="Investigate high CPU usage processes" if status != Status.PASSED else None,
            score_impact=impact,
        )


# =============================================================================
# SUSTAINABILITY CHECKS
# =============================================================================

class SwapUsageCheck(BaseCheck):
    """Check swap usage for efficiency."""
    check_id = "HEALTH-006"
    name = "Swap usage"
    description = "Checks swap memory usage (indicates memory pressure)"
    severity = Severity.LOW
    category = "health"
    score_weight = 3

    def run(self, context: dict) -> CheckResult:
        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()

            swap_total = 0
            swap_free = 0
            for line in lines:
                if line.startswith("SwapTotal:"):
                    swap_total = int(line.split()[1])
                elif line.startswith("SwapFree:"):
                    swap_free = int(line.split()[1])

            if swap_total == 0:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message="No swap configured (running in RAM only)",
                    score_impact=0,
                )

            swap_used = swap_total - swap_free
            pct_used = round(swap_used / swap_total * 100, 1)

            if pct_used < 20:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Swap usage: {pct_used}% ({swap_used // 1024} MB used)",
                    score_impact=0,
                )
            elif pct_used < 50:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.WARNING,
                    severity=self.severity,
                    message=f"Swap usage elevated: {pct_used}% - may indicate memory pressure",
                    recommendation="Consider adding more RAM to improve performance",
                    score_impact=self.score_weight // 2,
                )
            else:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.FAILED,
                    severity=self.severity,
                    message=f"Heavy swap usage: {pct_used}% - system is memory constrained",
                    recommendation="System needs more RAM - swap causes disk I/O and energy waste",
                    score_impact=self.score_weight,
                )

        except Exception as e:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message=f"Could not read swap info: {e}",
                score_impact=0,
            )


class TmpCleanupCheck(BaseCheck):
    """Check if temp file cleanup is configured."""
    check_id = "HEALTH-007"
    name = "Temp file cleanup"
    description = "Checks for automatic temp file cleanup (reduces disk waste)"
    severity = Severity.LOW
    category = "health"
    score_weight = 2

    def run(self, context: dict) -> CheckResult:
        cleanup_configured = False
        details = []

        # Check systemd-tmpfiles
        if Path("/usr/lib/tmpfiles.d").exists():
            cleanup_configured = True
            details.append("systemd-tmpfiles")

        # Check /etc/cron.daily/tmpwatch or similar
        cron_paths = [
            Path("/etc/cron.daily/tmpwatch"),
            Path("/etc/cron.daily/tmpreaper"),
        ]
        for p in cron_paths:
            if p.exists():
                cleanup_configured = True
                details.append(p.name)

        # Check if /tmp is tmpfs (cleaned on reboot)
        try:
            with open("/proc/mounts") as f:
                for line in f:
                    if " /tmp " in line and "tmpfs" in line:
                        cleanup_configured = True
                        details.append("tmpfs /tmp")
                        break
        except Exception:
            pass

        if cleanup_configured:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Temp cleanup configured: {', '.join(details)}",
                score_impact=0,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.WARNING,
            severity=self.severity,
            message="No automatic temp file cleanup detected",
            recommendation="Configure tmpwatch or use tmpfs for /tmp",
            score_impact=self.score_weight,
        )


class ZombieProcessCheck(BaseCheck):
    """Check for zombie processes."""
    check_id = "HEALTH-008"
    name = "Zombie processes"
    description = "Checks for zombie processes (resource waste)"
    severity = Severity.MEDIUM
    category = "health"
    score_weight = 3

    def run(self, context: dict) -> CheckResult:
        try:
            # Count zombies from /proc
            zombie_count = 0
            for pid_dir in Path("/proc").iterdir():
                if pid_dir.name.isdigit():
                    status_file = pid_dir / "status"
                    if status_file.exists():
                        try:
                            content = status_file.read_text()
                            if "State:\tZ" in content:
                                zombie_count += 1
                        except Exception:
                            pass

            if zombie_count == 0:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message="No zombie processes found",
                    score_impact=0,
                )
            else:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.WARNING,
                    severity=self.severity,
                    message=f"Found {zombie_count} zombie process(es)",
                    recommendation="Investigate parent processes not reaping children",
                    score_impact=self.score_weight,
                )

        except Exception as e:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message=f"Could not check processes: {e}",
                score_impact=0,
            )


class ServiceManagerCheck(BaseCheck):
    """Check which service manager is in use."""
    check_id = "HEALTH-009"
    name = "Service manager"
    description = "Identifies the service manager (systemd, etc.)"
    severity = Severity.INFO
    category = "health"
    score_weight = 0

    def run(self, context: dict) -> CheckResult:
        # Check for systemd
        if Path("/run/systemd/system").exists():
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Service Manager: systemd",
                score_impact=0,
            )

        # Check for sysvinit
        if Path("/etc/init.d").exists() and not Path("/run/systemd").exists():
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="Service Manager: sysvinit",
                score_impact=0,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message="Service Manager: unknown",
            score_impact=0,
        )


class UptimeCheck(BaseCheck):
    """Check system uptime."""
    check_id = "HEALTH-010"
    name = "System uptime"
    description = "Shows system uptime (long uptime may indicate missed updates)"
    severity = Severity.INFO
    category = "health"
    score_weight = 2

    def run(self, context: dict) -> CheckResult:
        try:
            with open("/proc/uptime") as f:
                uptime_seconds = float(f.read().split()[0])

            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)

            if days < 30:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Uptime: {days} days, {hours} hours",
                    score_impact=0,
                )
            elif days < 90:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.WARNING,
                    severity=self.severity,
                    message=f"Uptime: {days} days - consider scheduling maintenance",
                    recommendation="Long uptime may indicate pending kernel/security updates",
                    score_impact=self.score_weight // 2,
                )
            else:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.WARNING,
                    severity=self.severity,
                    message=f"Uptime: {days} days - very long uptime",
                    recommendation="Plan a maintenance reboot to apply security updates",
                    score_impact=self.score_weight,
                )

        except Exception as e:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message=f"Could not read uptime: {e}",
                score_impact=0,
            )


# =============================================================================
# SESSION & ACCESS CHECKS
# =============================================================================

class SSHSessionCheck(BaseCheck):
    """Check if running via SSH (remote access has different security profile)."""
    check_id = "HEALTH-011"
    name = "Session type"
    description = "Checks if audit is running locally or via SSH"
    severity = Severity.LOW
    category = "health"
    score_weight = 2

    def run(self, context: dict) -> CheckResult:
        # Check for SSH environment variables
        ssh_connection = os.environ.get("SSH_CONNECTION")
        ssh_client = os.environ.get("SSH_CLIENT")
        ssh_tty = os.environ.get("SSH_TTY")

        if ssh_connection or ssh_client or ssh_tty:
            # Parse SSH connection info
            details = []
            if ssh_connection:
                parts = ssh_connection.split()
                if len(parts) >= 2:
                    details.append(f"from {parts[0]}")

            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.WARNING,
                severity=self.severity,
                message=f"Running via SSH {' '.join(details)}".strip(),
                recommendation="For highest security, run audits from local console",
                score_impact=self.score_weight,
            )

        # Check for local TTY
        tty = os.environ.get("TERM", "")
        display = os.environ.get("DISPLAY", "")

        if display:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Local graphical session (DISPLAY={display})",
                score_impact=0,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message=f"Local console session (TERM={tty})",
            score_impact=0,
        )


class NetworkConnectionsCheck(BaseCheck):
    """Check for suspicious network connections."""
    check_id = "HEALTH-012"
    name = "Network connections"
    description = "Checks for unusual outbound connections"
    severity = Severity.MEDIUM
    category = "health"
    score_weight = 3

    def run(self, context: dict) -> CheckResult:
        try:
            # Count ESTABLISHED connections
            success, output = _run_command(["ss", "-tunaH", "state", "established"])

            if not success:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.SKIPPED,
                    severity=self.severity,
                    message="Could not check network connections",
                    score_impact=0,
                )

            lines = [l for l in output.strip().split("\n") if l.strip()]
            conn_count = len(lines)

            if conn_count < 50:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.PASSED,
                    severity=self.severity,
                    message=f"Active connections: {conn_count} (normal)",
                    score_impact=0,
                )
            elif conn_count < 200:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.WARNING,
                    severity=self.severity,
                    message=f"Active connections: {conn_count} (elevated)",
                    recommendation="Review active connections with 'ss -tunaH'",
                    score_impact=self.score_weight // 2,
                )
            else:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.FAILED,
                    severity=self.severity,
                    message=f"Active connections: {conn_count} (high)",
                    recommendation="Investigate unusual connection count",
                    score_impact=self.score_weight,
                )

        except Exception as e:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message=f"Network check failed: {e}",
                score_impact=0,
            )


class RunningServicesCheck(BaseCheck):
    """Check number of running services."""
    check_id = "HEALTH-013"
    name = "Running services"
    description = "Counts active systemd services"
    severity = Severity.INFO
    category = "health"
    score_weight = 0

    def run(self, context: dict) -> CheckResult:
        try:
            success, output = _run_command(
                ["systemctl", "list-units", "--type=service", "--state=running", "--no-pager", "--no-legend"]
            )

            if not success:
                return CheckResult(
                    check_id=self.check_id,
                    name=self.name,
                    status=Status.SKIPPED,
                    severity=self.severity,
                    message="Could not list services",
                    score_impact=0,
                )

            lines = [l for l in output.strip().split("\n") if l.strip()]
            service_count = len(lines)

            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"Running services: {service_count}",
                score_impact=0,
            )

        except Exception as e:
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.SKIPPED,
                severity=self.severity,
                message=f"Service check failed: {e}",
                score_impact=0,
            )


class GPUPresenceCheck(BaseCheck):
    """Check for GPU presence and utilization."""
    check_id = "HEALTH-014"
    name = "GPU status"
    description = "Checks for GPU availability"
    severity = Severity.INFO
    category = "health"
    score_weight = 0

    def run(self, context: dict) -> CheckResult:
        # Try nvidia-smi first
        success, output = _run_command(["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv,noheader"])

        if success and output.strip():
            lines = output.strip().split("\n")
            gpus = []
            for line in lines:
                parts = line.split(",")
                if len(parts) >= 1:
                    gpus.append(parts[0].strip())

            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message=f"GPU detected: {', '.join(gpus)}",
                score_impact=0,
            )

        # Check for any GPU via lspci
        success, output = _run_command(["lspci"])
        if success and ("VGA" in output or "3D" in output):
            return CheckResult(
                check_id=self.check_id,
                name=self.name,
                status=Status.PASSED,
                severity=self.severity,
                message="GPU detected (no NVIDIA driver)",
                score_impact=0,
            )

        return CheckResult(
            check_id=self.check_id,
            name=self.name,
            status=Status.PASSED,
            severity=self.severity,
            message="No dedicated GPU detected",
            score_impact=0,
        )


# =============================================================================
# EXPORTS
# =============================================================================

HEALTH_CHECKS = [
    # Energy
    EnergyMonitoringCheck(),
    CPUGovernorCheck(),
    # Resources
    MemoryUsageCheck(),
    DiskUsageCheck(),
    LoadAverageCheck(),
    # Sustainability
    SwapUsageCheck(),
    TmpCleanupCheck(),
    ZombieProcessCheck(),
    # Info
    ServiceManagerCheck(),
    UptimeCheck(),
    # Session & Access
    SSHSessionCheck(),
    NetworkConnectionsCheck(),
    RunningServicesCheck(),
    GPUPresenceCheck(),
]
