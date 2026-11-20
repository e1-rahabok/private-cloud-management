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
    """A target with an amber margin. No longer used by up.availability_percent (D-077)."""
    if value >= target:
        return "green"
    if value >= target - amber_margin:
        return "amber"
    return "red"


KPI_BANDS = ((75, "green"), (50, "yellow"), (25, "orange"), (0, "red"))


def kpi_band(score: float) -> str:
    """SP5 scoring bands: green 100-75, yellow 75-50, orange 50-25, red 25-0."""
    for floor, band in KPI_BANDS:
        if score >= floor:
            return band
    return "red"


def fast_status(class_kpi: dict) -> dict:
    """fast.production_kpi status (D-072). No target: SP5 bands and the class promise only."""
    order_kept = class_kpi["gold"] >= class_kpi["silver"] >= class_kpi["bronze"]
    lowest = kpi_band(min(class_kpi.values()))
    if lowest in ("orange", "red"):
        status = "red"
    elif lowest == "yellow" or not order_kept:
        status = "amber"
    else:
        status = "green"
    return {"status": status, "order_kept": order_kept}


def vm_secured_time_percent(minutes_so_far: int, unsecured: int, unsecured_in_window: int) -> float:
    """safe.vm_secured_time_percent: unsecured minutes inside maintenance windows do not count (D-073)."""
    counted = unsecured - unsecured_in_window
    return round(100.0 * (minutes_so_far - counted) / minutes_so_far, 2)


def sla_allowance_minutes(target_percent: float, days_in_month: int) -> float:
    """up.sla_allowance_minutes and the security equivalent: allowance for the whole calendar month (D-077)."""
    return round(days_in_month * 1440 * (100 - target_percent) / 100, 2)


def counted_downtime_minutes(downtime: int, inside_approved_window: int, customer_caused: int = 0) -> int:
    """up.vm_counted_downtime_minutes: approved green zone and reclassified customer-caused time do not count."""
    return max(0, downtime - inside_approved_window - customer_caused)


def sla_status(counted: list, allowances: list) -> str:
    """Status shared by up.availability_percent and safe.ksi_percent: per VM, against the whole month."""
    if any(c > a for c, a in zip(counted, allowances)):
        return "red"
    if all(c == 0 for c in counted):
        return "green"
    return "amber"


def ksi_status(vm_unsecured_minutes: list, days_in_month: int, settings: dict) -> str:
    """safe.ksi_percent status (D-073, corrected by D-077: whole-month allowance)."""
    allowance = sla_allowance_minutes(settings["safe.sla_contract_percent"], days_in_month)
    return sla_status(vm_unsecured_minutes, [allowance] * len(vm_unsecured_minutes))


def kai_status(vm_counted_minutes: list, classes: list, days_in_month: int, settings: dict) -> str:
    """up.availability_percent status (D-077)."""
    allow = [sla_allowance_minutes(settings["up.sla_percent"][c], days_in_month) for c in classes]
    return sla_status(vm_counted_minutes, allow)


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
