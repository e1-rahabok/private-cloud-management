"""Synthetic ACME data generator, Executive scope.

GENERATED from spec/data/estate.yaml, spec/data/stories.yaml and design/synthetic-acme-data.md.
Do not edit by hand (D-070).

Inputs: the specification, a seed, "now" and the stories to enable (D-067). Same inputs, same data.

Capacity decision dates come from the capacity engine (capacity.py), the one definition every workspace reads.
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
    return {"estate": y("data/estate.yaml"), "stories": y("data/stories.yaml"), "settings": settings,
            "thresholds": y("catalog/thresholds.yaml")["thresholds"], "standards": y("catalog/standards.yaml")["standards"]}


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

    # Capacity decisions per cluster group and resource, from the capacity engine (spec/catalog/capacity.yaml).
    from . import capacity as capacity_engine
    cap = capacity_engine.build(now, enable)
    decisions, in_plan = {}, set()
    for g in cap["groups"]:
        for res, r in g["resources"].items():
            if r["decision_days"] is not None:
                decisions.setdefault(g["location"], {})[f"{g['id']}.{res}"] = now + timedelta(days=r["decision_days"])
        if g["in_plan"] and g["round_on_time"]:
            in_plan.add(g["id"])
    for lid in locs:
        locs[lid]["decision"] = catalog.location_decision(decisions[lid], in_plan, now, st)

    # Health.
    health = {}

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

    # Calendar month in each location's time zone: minutes so far, and days in the whole month (D-077).
    def month_minutes(lid):
        tz = ZoneInfo(est["locations"][lid]["time_zone"])
        local = now.astimezone(tz)
        start = local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return int((local - start).total_seconds() // 60)

    def days_in_month(lid):
        local = now.astimezone(ZoneInfo(est["locations"][lid]["time_zone"]))
        nxt = (local.replace(day=28) + timedelta(days=4)).replace(day=1)
        return (nxt - timedelta(days=1)).day

    total_vm_minutes = sum(sum(prod[l].values()) * month_minutes(l) for l in locs)
    n_prod = sum(sum(prod[l].values()) for l in locs)

    # Up: the SP5 Availability SLA, Operational Availability per VM, whole-month allowance (D-077).
    events_up, counted, classes, actual_down, below_up = [], [], [], 0, {}
    if "U-1" in active:
        u1 = active["U-1"]
        cw = u1["plant"]["change_window"]
        start = rel(cw["starts"], now)
        down_start = start + timedelta(minutes=u1["plant"]["downtime"]["start_in_window_minutes"])
        mins = u1["plant"]["downtime"]["minutes"]
        inside = mins if down_start + timedelta(minutes=mins) <= start + timedelta(hours=cw["hours"]) and cw["approved"] else 0
        n = u1["objects"]["vms"]
        for _ in range(n):
            counted.append(catalog.counted_downtime_minutes(mins, inside)); classes.append(u1["objects"]["class"])
        actual_down += mins * n
        events_up.append({"at": down_start.isoformat(), "counted": False, "change_ref": cw["change_ref"],
                          "text": f"{n} virtual machines in Virginia were down for {mins} minutes during patching, inside approved change {cw['change_ref']}. Not counted against the target."})
    if "U-2" in active:
        u2 = active["U-2"]
        mins = u2["plant"]["downtime"]["minutes"]
        vms = u2["objects"]["vms"]
        for _ in vms:
            counted.append(catalog.counted_downtime_minutes(mins, 0)); classes.append(u2["objects"]["class"])
        actual_down += mins * len(vms)
        allow = catalog.sla_allowance_minutes(st["up.sla_percent"][u2["objects"]["class"]], days_in_month(u2["objects"]["location"]))
        if mins > allow:
            below_up[u2["objects"]["location"]] = len(vms)
        events_up.append({"at": rel(u2["plant"]["downtime"]["starts"], now).isoformat(), "counted": True, "change_ref": None,
                          "text": f"{len(vms)} virtual machines in Tokyo were down for {mins} minutes outside any approved change window. Counted."})
    counted_total = sum(counted)
    kai = 100.0 * (total_vm_minutes - counted_total) / total_vm_minutes
    actual = 100.0 * (total_vm_minutes - actual_down) / total_vm_minutes
    pad = n_prod - len(counted)
    up_status = catalog.kai_status(counted + [0] * pad, classes + ["silver"] * pad, days_in_month("tk"), st)
    days_so_far = now.astimezone(timezone.utc).day
    health["up"] = {"value": round(kai, 7), "actual": round(actual, 7), "status": up_status,
                    "vms_below_sla": sum(below_up.values()), "below_by_location": below_up,
                    "counted_minutes": counted_total, "actual_minutes": actual_down, "events": events_up,
                    "sla": st["up.sla_percent"],
                    "by_location": {lid: (sum(1 for e in events_up if e["counted"] and lid == "tk")) for lid in locs}}
    health["up"]["series7"] = [{"t": (now - timedelta(days=days_so_far - 1 - i)).isoformat(),
                                "v": 100.0 if i < days_so_far - 2 else round(kai, 7)} for i in range(days_so_far)]
    health["up"]["series30"] = health["up"]["series7"]

    # Safe: Security SLA as unsecured time, calendar month to date in each location's time zone (D-073).
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
        n_vms = n4["objects"]["production_vms_on_hosts"]
        vm_secured += [minutes - in_window] * n_vms  # unsecured minutes per VM
        unsecured_vm_minutes += (minutes - in_window) * n_vms
        allowance = catalog.sla_allowance_minutes(st["safe.sla_contract_percent"], days_in_month(n4["objects"]["location"]))
        if minutes - in_window > allowance:
            below[n4["objects"]["location"]] = {"vms": n_vms, "hours": (minutes - in_window) // 60}
        ssh_events.append({"at": since.isoformat(),
                           "text": f"{ssh} servers in London have had remote admin access left open for {minutes // 60} hours, "
                                   f"outside the maintenance window. {n_vms} virtual machines on them fell below the security target."})
    vm_secured += [0] * (n_prod - len(vm_secured))
    ksi = round(100.0 * (total_vm_minutes - unsecured_vm_minutes) / total_vm_minutes, 7)
    health["safe"] = {
        "value": ksi, "status": catalog.ksi_status(vm_secured, days_in_month("ld"), st),
        "vms_below_sla": sum(b["vms"] for b in below.values()), "below_by_location": below,
        "ssh_or_shell_enabled": ssh, "lockdown_off": e1.get("lockdown_off", 0),
        "certificates_expired": e1.get("certificates_expired", 0), "root_logins_open": e1.get("root_logins_open", 0),
        "risk_certificates": len([d for d in cert_days if d <= st["safe.certificate_warning_days"]]),
        "events": ssh_events + cert_events,
    }
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
        "cost_avoidable_next_round": sum(r["cost_avoidable"] for r in cap["reclamation"]),
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
        "next_round_closes": cap["next_round_closes"], "capacity": cap,
        "health": health, "value": value, "recovery": recovery, "speed": speed, "goals": goals,
        "region_stale": region_stale, "active_stories": sorted(active),
    }
