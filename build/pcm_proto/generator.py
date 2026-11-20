"""Synthetic ACME data generator, Executive scope.

GENERATED from spec/data/estate.yaml, spec/data/stories.yaml and design/synthetic-acme-data.md.
Do not edit by hand (D-070).

Inputs: the specification, a seed, "now" and the stories to enable (D-067). Same inputs, same data.

Scope note: this prototype plants capacity decision dates from the stories. The forecast engine
(Capacity design, 3.5) is built with the Capacity workspace (D-053).
"""
from __future__ import annotations

import math
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import catalog

SPEC = Path(__file__).resolve().parents[2] / "spec"
CLASSES = ("gold", "silver", "bronze")
RESOURCES = ("compute", "memory", "storage")


def load_spec() -> dict:
    def y(p):
        return yaml.safe_load((SPEC / p).read_text())
    settings = {k: v["default"] for k, v in y("catalog/settings.yaml")["settings"].items()}
    return {"estate": y("data/estate.yaml"), "stories": y("data/stories.yaml"), "settings": settings}


def rel(expr: str, now: datetime) -> datetime:
    """Parse 'now + 30 days', 'now - 8 hours', 'now - 20 minutes'."""
    m = re.fullmatch(r"now\s*([+-])\s*(\d+)\s*(day|days|hour|hours|minute|minutes)", expr.strip())
    if not m:
        raise ValueError(f"Bad relative time: {expr}")
    sign = 1 if m.group(1) == "+" else -1
    n = int(m.group(2)) * sign
    unit = m.group(3).rstrip("s") + "s"
    return now + timedelta(**{unit: n})


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc).replace(microsecond=0)
    dt = datetime.fromisoformat(value)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def series(rng: random.Random, now: datetime, days: int, step_hours: int, level: float,
           wobble: float, floor: float | None = None, ceil: float | None = None) -> list:
    """A smooth series around level, with a daily rhythm. Mostly green (realism rule)."""
    pts = []
    n = days * 24 // step_hours
    for i in range(n):
        t = now - timedelta(hours=step_hours * (n - 1 - i))
        v = level + wobble * 0.5 * math.sin(2 * math.pi * t.hour / 24) + rng.uniform(-wobble, wobble) * 0.3
        if floor is not None:
            v = max(floor, v)
        if ceil is not None:
            v = min(ceil, v)
        pts.append({"t": t.isoformat(), "v": round(v, 3)})
    return pts


def generate(now: datetime, seed: int = 7, enable: tuple = ()) -> dict:
    spec = load_spec()
    est, stories, st = spec["estate"], spec["stories"]["stories"], spec["settings"]
    bg = spec["stories"]["background"]
    active = {k: v for k, v in stories.items() if v.get("enabled_by_default", True) or k in enable}
    rng = random.Random(seed)
    gens = est["host_generations"]

    # Freshness per region (E-7).
    region_read = {r: now for r in est["regions"]}
    if "E-7" in active:
        s = active["E-7"]
        region_read["emea"] = rel(s["plant"]["last_successful_read"], now)
        cycle = s["plant"]["collection_cycle_minutes"]
    else:
        cycle = 5
    region_stale = {r: catalog.is_stale(t, now, cycle) for r, t in region_read.items()}

    # Scale per location.
    locs = {}
    in_use_base = {"compute": (55, 68), "memory": (72, 82), "storage": (55, 66)}
    for lid, loc in est["locations"].items():
        cores = sum(n * gens[g]["cores"] for g, n in loc["hosts"].items())
        hosts = sum(loc["hosts"].values())
        in_use = {r: round(rng.uniform(*in_use_base[r]), 1) for r in RESOURCES}
        locs[lid] = {
            "id": lid, "name": loc["name"], "region": loc["region"],
            "cores": cores, "hosts": hosts,
            "memory_tb": round(catalog.memory_tb(loc["hosts"], gens), 1),
            "storage_tb": round(hosts * est["datastores"]["tb_per_host"], 1),
            "in_use": in_use,
            "as_of": region_read[loc["region"]], "stale": region_stale[loc["region"]],
            "source": est["regions"][loc["region"]]["vcf_operations_instance"],
            "lead_time": loc["procurement_lead_time_days"],
        }
    if "C-1" in active:
        locs["sg"]["in_use"]["memory"] = 86.0  # SG-Silver memory pressure shows at location level
    total_cores = catalog.compute_cores(est["locations"], gens)

    # Capacity decisions per cluster group and resource (planted; see scope note).
    decisions, in_plan = {}, set()
    for lid, loc in locs.items():
        base = bg["decision_dates_days_from_now"].get(lid, 220)
        for i, cls in enumerate(CLASSES):
            group = f"{lid.upper()}-{cls.capitalize()}"
            for j, res in enumerate(RESOURCES):
                days = base + 15 * i + 25 * j + rng.randint(0, 10)
                decisions.setdefault(lid, {})[f"{group}.{res}"] = now + timedelta(days=days)
    if "C-1" in active:
        c1 = active["C-1"]
        run_out = rel(c1["plant"]["run_out_date"], now)
        key = f"{c1['objects']['cluster_group']}.{c1['objects']['resource']}"
        decisions["sg"][key] = catalog.decision_date(run_out, locs["sg"]["lead_time"])
        if c1["plant"]["in_next_round"]:
            in_plan.add(c1["objects"]["cluster_group"])
    for lid in locs:
        locs[lid]["decision"] = catalog.location_decision(decisions[lid], in_plan, now, st)

    # Health.
    up_level = bg["up.availability_percent"]["estate"]
    health = {
        "up": {"value": up_level, "series7": series(rng, now, 7, 2, up_level, 0.02, ceil=100.0),
               "series30": series(rng, now, 30, 8, up_level, 0.02, ceil=100.0)},
    }
    health["up"]["by_location"] = {lid: round(up_level + rng.uniform(-0.01, 0.02), 2) for lid in locs}

    # Production VMs per location and class (estate.yaml vms and cluster_layout).
    vm_cfg, layout = est["vms"], est["cluster_layout"]["share_of_hosts"]
    prod = {lid: {c: round(locs[lid]["hosts"] * layout[c] * vm_cfg["per_host_average"][c] * vm_cfg["production_share"])
                  for c in CLASSES} for lid in locs}

    # Fast: a KPI, not an SLA (D-072). Class group KPIs are planted; the VM KPI engine comes with L2.
    ckpi = bg["fast.class_group_kpi"]
    n_cls = {c: sum(prod[l][c] for l in locs) for c in CLASSES}
    prod_kpi = round(sum(ckpi[c] * n_cls[c] for c in CLASSES) / sum(n_cls.values()), 1)
    health["fast"] = {"value": prod_kpi, "class_kpi": dict(ckpi), **catalog.fast_status(ckpi)}
    daily = lambda days: [{"t": (now - timedelta(days=days - 1 - i)).isoformat(),
                           "v": round(prod_kpi + rng.uniform(-1.2, 1.2), 1)} for i in range(days)]
    health["fast"]["series7"], health["fast"]["series30"] = daily(7), daily(30)
    health["fast"]["by_location"] = {lid: round(prod_kpi + rng.uniform(-2.0, 1.5), 1) for lid in locs}

    # Safe: Security SLA as unsecured time, calendar month to date in each location's time zone (D-073).
    def month_minutes(lid):
        tz = ZoneInfo(est["locations"][lid]["time_zone"])
        local = now.astimezone(tz)
        start = local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return int((local - start).total_seconds() // 60)
    cert_days, cert_events, ssh, ssh_events, below = [], [], 0, [], {}
    e1 = active.get("E-1", {}).get("plant", {})
    for c in e1.get("certificates_expiring", []):
        d = (rel(c["expires"], now).date() - now.date()).days
        cert_days.append(d)
        where = {"fr": "Frankfurt", "sg": "Singapore"}[c["component"].split("-")[-2]]
        cert_events.append({"at": now.isoformat(),
                            "text": f"A security certificate on a management server in {where} expires in {d} days."})
    unsecured_vm_minutes = 0
    vm_secured = []
    if "N-4" in active:
        n4 = active["N-4"]
        ssh = n4["objects"]["hosts"]
        since = rel(n4["plant"]["ssh_enabled_since"], now)
        minutes = int((now - since).total_seconds() // 60)
        in_window = minutes if n4["plant"].get("inside_maintenance_window") else 0
        mm = month_minutes(n4["objects"]["location"])
        minutes, in_window = min(minutes, mm), min(in_window, mm)  # only this calendar month counts
        pct = catalog.vm_secured_time_percent(mm, minutes, in_window) if mm else 100.0
        n_vms = n4["objects"]["production_vms_on_hosts"]
        vm_secured += [pct] * n_vms
        unsecured_vm_minutes += (minutes - in_window) * n_vms
        if pct < st["safe.sla_contract_percent"]:
            below[n4["objects"]["location"]] = {"vms": n_vms, "hours": (minutes - in_window) // 60}
        ssh_events.append({"at": since.isoformat(),
                           "text": f"{ssh} servers in London have had remote admin access left open for {minutes // 60} hours, "
                                   f"outside the maintenance window. {n_vms} virtual machines on them fell below the security target."})
    total_vm_minutes = sum(sum(prod[l].values()) * month_minutes(l) for l in locs)
    n_prod = sum(sum(prod[l].values()) for l in locs)
    vm_secured += [100.0] * (n_prod - len(vm_secured))
    ksi = round(100.0 * (total_vm_minutes - unsecured_vm_minutes) / total_vm_minutes, 4)
    health["safe"] = {
        "value": ksi, "status": catalog.ksi_status(vm_secured, st),
        "vms_below_sla": sum(b["vms"] for b in below.values()), "below_by_location": below,
        "ssh_or_shell_enabled": ssh, "lockdown_off": e1.get("lockdown_off", 0),
        "certificates_expired": e1.get("certificates_expired", 0), "root_logins_open": e1.get("root_logins_open", 0),
        "risk_certificates": len([d for d in cert_days if d <= st["safe.certificate_warning_days"]]),
        "events": ssh_events + cert_events,
    }
    days_so_far = now.astimezone(timezone.utc).day
    health["safe"]["series7"] = [{"t": (now - timedelta(days=days_so_far - 1 - i)).isoformat(),
                                  "v": 100.0 if i < days_so_far - 1 else ksi} for i in range(days_so_far)]
    health["safe"]["series30"] = health["safe"]["series7"]
    health["safe"]["by_location"] = {lid: below.get(lid, {}).get("vms", 0) for lid in locs}

    # Value.
    cost = est["cost"]
    cost_annual = cost["product"] + cost["service"] + cost["people"]
    comp = catalog.public_cloud_comparison(cost_annual, st["value.depreciation_years"],
                                           est["public_cloud_estimate"]["total_5y"])
    value = {
        "cost": cost, "cost_annual": cost_annual, **comp,
        "public_cloud_estimate": est["public_cloud_estimate"]["total_5y"],
        "public_cloud_as_of": rel(est["public_cloud_estimate"]["as_of"], now),
        "cost_avoided_ytd": active.get("E-4", {}).get("plant", {}).get("deferred_purchase", {}).get("value_at_today_price", 0),
        "cost_avoidable_next_round": active.get("C-6", {}).get("plant", {}).get("next_round_cost_for_group", 0),
    }

    # Site recovery.
    recovery = []
    e3 = active.get("E-3", {}).get("plant")
    for plan in est["recovery_plans"]:
        lid = plan["protected"]
        if e3 and lid == "fr":
            ago = (now - rel(e3["last_test"], now)).days
            mins, prot, tested = e3["recovery_minutes"], e3["protected_vms"], e3["vms_in_last_test"]
        else:
            other = (e3 or {}).get("other_plans", {"last_test": "now - 60 days", "recovery_minutes": 18, "share_tested_percent": 99})
            ago = (now - rel(other["last_test"], now)).days
            mins = other["recovery_minutes"]
            prot = 1000 + 100 * len(recovery)
            tested = round(prot * other["share_tested_percent"] / 100)
        r = catalog.site_recovery(ago, mins, plan["target_minutes"], prot, tested, st)
        recovery.append({"location": lid, "last_test_at": now - timedelta(days=ago), "days_ago": ago,
                         "recovery_minutes": mins, "target_minutes": plan["target_minutes"],
                         "protected_vms": prot, "vms_in_test": tested, **r})

    # Speed.
    e6 = active.get("E-6", {}).get("plant", {"delivery_hours_last_30d": 4.0, "delivery_hours_year_ago": 240})
    speed = {"now": e6["delivery_hours_last_30d"], "year_ago": e6["delivery_hours_year_ago"],
             "series12": [{"t": (now - timedelta(days=30 * (11 - i))).isoformat(),
                           "v": round(e6["delivery_hours_year_ago"] * (e6["delivery_hours_last_30d"] / e6["delivery_hours_year_ago"]) ** (i / 11), 1)}
                          for i in range(12)]}

    # Goals.
    goals = []
    e5 = active.get("E-5", {}).get("plant", {})
    for g in est["goals"]:
        proj = e5.get(g["id"], {}).get("projected_year_end", g["target"])
        goals.append({"id": g["id"], "title": g["title"], "current": proj, "target": g["target"],
                      "direction": g["direction"],
                      "status": catalog.goal_status(g["target"], g["direction"], proj)})

    return {
        "now": now, "settings": st, "locations": locs, "total_cores": total_cores,
        "decisions": decisions, "in_plan": in_plan,
        "next_round_closes": rel(est["procurement"]["next_round_closes"], now),
        "health": health, "value": value, "recovery": recovery, "speed": speed, "goals": goals,
        "region_stale": region_stale, "active_stories": sorted(active),
    }
