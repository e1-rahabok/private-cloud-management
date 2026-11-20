"""Catalog definitions for the Executive workspace.

GENERATED from spec/catalog/executive.yaml and spec/catalog/settings.yaml. Do not edit by hand (D-070).
One function per catalog entry. Pages never compute these; the API returns their results.
"""
from __future__ import annotations

from datetime import datetime, timedelta

DEFINITION_VERSION = 1


def decision_date(run_out_date: datetime, lead_time_days: int) -> datetime:
    """capacity.decision_date = run_out_date - procurement lead time."""
    return run_out_date - timedelta(days=lead_time_days)


def location_decision(decisions: dict, in_plan_groups: set, now: datetime, settings: dict) -> dict:
    """capacity.location_decision.

    decisions: {"<group>.<resource>": datetime}. Returns the earliest, with status.
    """
    key = min(decisions, key=lambda k: decisions[k])
    group, resource = key.rsplit(".", 1)
    date = decisions[key]
    in_plan = group in in_plan_groups
    days = (date.date() - now.date()).days
    if in_plan:
        status = "in_plan"
    elif days <= settings["capacity.decide_now_days"]:
        status = "red"
    elif days <= settings["capacity.decide_soon_days"]:
        status = "amber"
    else:
        status = "green"
    return {"group": group, "resource": resource, "date": date, "days": days,
            "in_plan": in_plan, "status": status}


def band_status(value: float, target: float, amber_margin: float) -> str:
    """Status rule shared by up.availability_percent and fast.served_well_percent."""
    if value >= target:
        return "green"
    if value >= target - amber_margin:
        return "amber"
    return "red"


def safe_findings(cert_days: list, ssh_or_shell: int, lockdown_off: int, root_logins: int,
                  settings: dict) -> dict:
    """safe.findings. cert_days: days until expiry of each finding (negative = expired)."""
    certs = [d for d in cert_days if d <= settings["safe.certificate_warning_days"]]
    total = len(certs) + ssh_or_shell + lockdown_off + root_logins
    if any(d <= settings["safe.certificate_red_days"] for d in certs):
        status = "red"
    elif total == 0:
        status = "green"
    else:
        status = "amber"
    return {"total": total, "status": status, "certificates_expiring": len(certs),
            "ssh_or_shell_enabled": ssh_or_shell, "lockdown_off": lockdown_off,
            "root_logins": root_logins}


def site_recovery(last_test_days_ago: int, recovery_minutes: int, target_minutes: int,
                  protected_vms: int, vms_in_test: int, settings: dict) -> dict:
    """recovery.site_recovery for one protected location."""
    share = round(100.0 * vms_in_test / protected_vms, 1) if protected_vms else 0.0
    if last_test_days_ago > settings["recovery.test_max_age_days"] or recovery_minutes > target_minutes:
        status = "red"
    elif share < settings["recovery.min_share_tested_percent"]:
        status = "amber"
    else:
        status = "green"
    return {"share_tested_percent": share, "status": status}


def public_cloud_comparison(cost_annual: float, depreciation_years: int, estimate: float) -> dict:
    """value.tco and value.public_cloud_comparison."""
    tco = cost_annual * depreciation_years
    difference = estimate - tco
    return {"tco": tco, "difference": difference,
            "difference_percent": round(100.0 * difference / estimate, 1)}


def goal_status(target: float, direction: str, projected: float) -> str:
    """goals.status: on_track, at_risk (misses by at most 10% of target), missed."""
    met = projected <= target if direction == "at_most" else projected >= target
    if met:
        return "on_track"
    gap = abs(projected - target)
    return "at_risk" if gap <= 0.1 * target else "missed"


def compute_cores(locations: dict, generations: dict) -> int:
    """scale.compute_cores over the estate."""
    return sum(n * generations[gen]["cores"]
               for loc in locations.values() for gen, n in loc["hosts"].items())


def memory_tb(hosts: dict, generations: dict) -> float:
    """scale.memory_tb for one location's host counts."""
    return sum(n * generations[gen]["memory_gb"] for gen, n in hosts.items()) / 1024.0


def is_stale(as_of: datetime, now: datetime, cycle_minutes: int) -> bool:
    """Meta.stale: older than two collection cycles (PCM core, 3.5; D-041)."""
    return (now - as_of) > timedelta(minutes=2 * cycle_minutes)
