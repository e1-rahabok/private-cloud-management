"""Capacity engine: usable capacity, weekly peaks, the 13-month forecast, decision dates, the purchase plan,
reclamation and what-if (prototype).

GENERATED from spec/catalog/capacity.yaml, spec/catalog/settings.yaml and spec/data/stories.yaml.
Do not edit by hand (D-070). Executive, L2 and Capacity read their decision dates from here (PCM core, 1).
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import generator

CLASSES = ("gold", "silver", "bronze")
RESOURCES = ("compute", "memory", "storage")
HORIZON_DAYS = 396  # 13 months
CLASS_FACTOR_R = {"gold": 2.5, "silver": 1.0, "bronze": 2.2}
RES_FACTOR_R = {"compute": 1.6, "memory": 1.0, "storage": 1.4}
CLASS_DU = {"gold": -0.10, "silver": 0.0, "bronze": 0.05}


def _avg(loc_hosts: dict, gens: dict, key: str) -> float:
    n = sum(loc_hosts.values())
    return sum(c * gens[g][key] for g, c in loc_hosts.items()) / n


def usable(hosts: int, n_clusters: int, per_host: dict, storage_tb: float, buffer: dict) -> dict:
    """capacity.usable: total, minus one HA and one maintenance host per cluster, minus buffer after HA."""
    out = {}
    for res, unit in (("compute", per_host["threads"]), ("memory", per_host["memory_gb"])):
        total = hosts * unit
        ha = n_clusters * unit
        maint = n_clusters * unit
        base = total - ha - maint
        buf = base * buffer[res] / 100
        out[res] = {"total": total, "ha": ha, "maintenance": maint, "buffer": buf, "usable": base - buf}
    total = storage_tb
    buf = total * buffer["storage"] / 100
    out["storage"] = {"total": total, "ha": 0, "maintenance": 0, "buffer": buf, "usable": total - buf}
    return out


def fit(points: list) -> tuple[float, float]:
    """Least squares on (day offset, value): returns (value at day 0, slope per day)."""
    n = len(points)
    mx = sum(x for x, _ in points) / n
    my = sum(y for _, y in points) / n
    sxx = sum((x - mx) ** 2 for x, _ in points) or 1.0
    slope = sum((x - mx) * (y - my) for x, y in points) / sxx
    return my - slope * mx, slope


def close_month(d: datetime, month: int) -> bool:
    return d.month == month and d.day >= 25  # the close week at the end of the year-end month


def build(now: datetime, enable=()) -> dict:
    spec = generator.load_spec()
    est, st = spec["estate"], spec["settings"]
    stories = {k: v for k, v in spec["stories"]["stories"].items() if v.get("enabled_by_default", True) or k in enable}
    bg = spec["stories"]["background"]["capacity"]
    gens = est["host_generations"]
    share = est["cluster_layout"]["share_of_hosts"]
    std = st["capacity.host_standard"]
    rounds_next = generator.rel(est["procurement"]["next_round_closes"], now)
    round_after = rounds_next + timedelta(days=est["procurement"]["round_interval_days"])
    register = []
    if "C-4" in stories:
        r = stories["C-4"]["plant"]["demand_register"]
        register.append({**r, "group": stories["C-4"]["objects"]["cluster_group"], "date": generator.rel(r["when"], now)})

    groups = []
    for lid, loc in est["locations"].items():
        tz = ZoneInfo(loc["time_zone"])
        per_host = {"threads": _avg(loc["hosts"], gens, "threads"), "memory_gb": _avg(loc["hosts"], gens, "memory_gb")}
        hosts_total = sum(loc["hosts"].values())
        base_r = bg["silver_memory_trend_run_out_days"][lid]
        for cls in CLASSES:
            gid = f"{lid.upper()}-{cls.capitalize()}"
            hosts = round(hosts_total * share[cls])
            n_cl = max(1, round(hosts / 12))
            cap = usable(hosts, n_cl, per_host, hosts * est["datastores"]["tb_per_host"], st["capacity.buffer_percent"])
            res_out = {}
            for res in RESOURCES:
                U = cap[res]["usable"]
                u0 = bg["in_use_percent_now"][res] / 100 + CLASS_DU[cls]
                R = base_r * CLASS_FACTOR_R[cls] * RES_FACTOR_R[res]
                uplift_frac = 0.0
                if gid == "SG-Silver" and res == "memory" and "C-1" in stories:
                    u0 = stories["C-1"]["plant"]["memory_in_use_percent_now"] / 100
                    R = (generator.rel(stories["C-1"]["plant"]["trend_run_out"], now) - now).days
                if gid == "TK-Gold" and "C-2" in stories:
                    u0 = stories["C-2"]["plant"]["in_use_percent_now"][res] / 100
                    R = stories["C-2"]["plant"]["trend_run_out_days"]
                if "C-3" in stories and gid == stories["C-3"]["objects"]["cluster_group"] and res == stories["C-3"]["objects"]["resource"]:
                    uplift_frac = stories["C-3"]["plant"]["last_year_close_uplift_percent_of_usable"] / 100
                slope_true = (1 - u0) * U / R
                ye = loc["financial_year_end_month"]
                # 13 months of weekly peaks (PCM's own history, PCM core 3.3)
                weekly = []
                for w in range(56, -1, -1):
                    d = now - timedelta(days=7 * w)
                    v = u0 * U - slope_true * 7 * w
                    if uplift_frac and close_month(d.astimezone(tz), ye):
                        v += uplift_frac * U
                    weekly.append({"t": d.isoformat(), "v": round(v, 2), "close": close_month(d.astimezone(tz), ye)})
                pts = [(-7 * (56 - i), p["v"]) for i, p in enumerate(weekly) if i >= 56 - st["capacity.trend_weeks"] and not p["close"]]
                a, b = fit(pts)
                # seasonal uplift: last year's excess over the trend inside the close week
                ex = [p["v"] - (a + b * (-7 * (56 - i))) for i, p in enumerate(weekly) if p["close"]]
                uplift = max(ex) if ex else 0.0
                pts90 = [(-7 * (13 - i), weekly[43 + i]["v"]) for i in range(14)]
                a90, b90 = fit(pts90)
                committed = lambda day: sum(r[{"memory": "memory_gb", "compute": "compute_threads", "storage": "storage_tb"}[res]]
                                            for r in register if r["group"] == gid and now + timedelta(days=day) >= r["date"])
                run_out = peak = run90 = None
                forecast = []
                for day in range(0, HORIZON_DAYS + 1):
                    d = now + timedelta(days=day)
                    base_v = a + b * day + committed(day)
                    seas = uplift if close_month(d.astimezone(tz), ye) else 0.0
                    if day % 7 == 0:
                        forecast.append({"t": d.isoformat(), "v": round(base_v + seas, 2)})
                    if run_out is None and base_v >= U:
                        run_out = day
                    if peak is None and run_out is None and base_v + seas >= U:
                        peak = day
                    if run90 is None and a90 + b90 * day >= U:
                        run90 = day
                if run_out is None:  # extrapolate the trend beyond the horizon for decision dates
                    extra = (U - a - committed(HORIZON_DAYS)) / b if b > 0 else None
                    run_out_days = round(extra) if extra else None
                else:
                    run_out_days = run_out
                lead = loc["procurement_lead_time_days"]
                decision_days = run_out_days - lead if run_out_days is not None else None
                res_out[res] = {
                    "usable": round(U, 1), "waterfall": {k: round(v, 1) for k, v in cap[res].items()},
                    "now": round(a, 1), "remaining_percent": round(100 * (U - a) / U, 1),
                    "slope_per_day": round(b, 3), "weekly": weekly, "forecast": forecast,
                    "run_out_days": run_out_days, "run_out_within_horizon": run_out is not None,
                    "peak_cross_days": peak, "seasonal_uplift": round(uplift, 1),
                    "run_out_90d_days": run90, "decision_days": decision_days,
                }
            tight = min(RESOURCES, key=lambda r_: res_out[r_]["run_out_days"] if res_out[r_]["run_out_days"] is not None else 10 ** 6)
            t = res_out[tight]
            dec = t["decision_days"]
            dec_date = now + timedelta(days=dec) if dec is not None else None
            must_be_in_round = dec_date is not None and dec_date < round_after
            in_plan = must_be_in_round and ("C-1" not in stories or gid != "SG-Silver" or stories["C-1"]["plant"]["in_next_round"])
            # "In the plan" only counts if the round closes before the decision date (the order arrives in time)
            on_time = in_plan and rounds_next <= dec_date
            if dec is not None and dec <= st["capacity.decide_soon_days"] and not in_plan:
                quadrant = "red"
            elif t["remaining_percent"] > st["capacity.waste_remaining_percent"] and (t["run_out_days"] or 10 ** 6) > st["capacity.waste_time_days"]:
                quadrant = "waste"
            else:
                quadrant = "green"
            groups.append({"id": gid, "location": lid, "location_name": loc["name"], "class": cls, "hosts": hosts,
                           "clusters": n_cl, "per_host": per_host, "resources": res_out, "tightest": tight,
                           "decision_days": dec, "decision_date": dec_date, "in_plan": in_plan, "round_on_time": on_time,
                           "quadrant": quadrant, "lead_time_days": lead,
                           "peak_warning": next(({"resource": r_, "days": res_out[r_]["peak_cross_days"]} for r_ in RESOURCES
                                                 if res_out[r_]["peak_cross_days"] is not None), None)})
    plan = purchase_plan(groups, now, rounds_next, st)
    recl = reclamation(groups, stories, now, rounds_next, st, plan)
    return {"now": now, "groups": groups, "next_round_closes": rounds_next, "round_after": round_after,
            "register": register, "plan": plan, "reclamation": recl, "settings": st, "stories": stories}


def host_cost(std: dict, years: int) -> dict:
    """D-060 cost lines per host; CPU licensing per core (D-061)."""
    lic = std["cores"] * std["vcf_licence_usd_per_core_year"] * years
    sup = std["support_usd_per_year"] * years
    return {"server": std["server_usd"], "vcf_licence": lic, "support": sup, "total": std["server_usd"] + lic + sup}


def purchase_plan(groups: list, now: datetime, rounds_next: datetime, st: dict) -> list:
    """capacity.purchase_plan: groups that must be in the next round, hosts to buy, cost lines."""
    std = st["capacity.host_standard"]
    per = host_cost(std, st["value.depreciation_years"])
    out = []
    for g in groups:
        if not g["in_plan"]:
            continue
        r = g["resources"][g["tightest"]]
        delivery = (rounds_next - now).days + g["lead_time_days"]
        target = delivery + st["capacity.purchase_cover_months"] * 30
        need = r["now"] + r["slope_per_day"] * target - r["usable"]
        per_host = {"memory": std["memory_gb"], "compute": std["threads"] * 0.9, "storage": std["storage_tb"]}[g["tightest"]]
        hosts = max(1, math.ceil(need / per_host))
        out.append({"group": g["id"], "resource": g["tightest"], "hosts": hosts, "delivery_days": delivery,
                    "cover_until_days": target, "lines": {k: v * hosts for k, v in per.items() if k != "total"},
                    "total": per["total"] * hosts, "per_host": per, "on_time": g["round_on_time"]})
    return out


IDLE_GB, OVERSIZED_GB, POWERED_OFF_TB = 12, 64, 0.2


def reclamation(groups, stories, now, rounds_next, st, plan) -> list:
    """capacity.reclamation for planted groups (C-6): what each area frees, and whether it defers the round."""
    out = []
    if "C-6" not in stories:
        return out
    p = stories["C-6"]["plant"]
    g = next(x for x in groups if x["id"] == stories["C-6"]["objects"]["cluster_group"])
    mem = g["resources"]["memory"]
    areas = [
        {"area": "Orphaned files and unmapped blocks", "count": None, "frees": "Datastore space only", "memory_gb": 0, "storage_tb": 18.0},
        {"area": "Powered-off VMs", "count": p["powered_off_vms"], "frees": "Datastore space, once deleted; no memory or CPU", "memory_gb": 0, "storage_tb": round(p["powered_off_vms"] * POWERED_OFF_TB, 1)},
        {"area": "Idle VMs", "count": p["idle_vms"], "frees": "Memory once powered off; CPU only in allocation, not cycles", "memory_gb": p["idle_vms"] * IDLE_GB, "storage_tb": 0},
        {"area": "Oversized VMs, largest first", "count": p["oversized_large_vms"], "frees": "Memory; CPU only in allocation", "memory_gb": p["oversized_large_vms"] * OVERSIZED_GB, "storage_tb": 0},
        {"area": "Unused VMs", "count": None, "frees": "CPU cycles and memory; hardest to prove", "memory_gb": 0, "storage_tb": 0},
    ]
    freed = sum(a["memory_gb"] for a in areas)
    new_run_out = mem["run_out_days"] + (freed / mem["slope_per_day"] if mem["slope_per_day"] > 0 else 0)
    new_decision = new_run_out - g["lead_time_days"]
    round_after = (rounds_next - now).days + st["procurement.round_interval_days"] if "procurement.round_interval_days" in st else None
    pl = next((x for x in plan if x["group"] == g["id"]), None)
    defers = pl is not None and new_decision > (rounds_next - now).days + 182
    out.append({"group": g["id"], "areas": areas, "memory_freed_gb": freed, "run_out_days_before": mem["run_out_days"],
                "run_out_days_after": round(new_run_out), "decision_days_after": round(new_decision),
                "defers_next_round": defers, "cost_avoidable": pl["total"] if (pl and defers) else 0})
    return out


def what_if_refresh(cap: dict, location: str, replace_previous: int, new_hosts: int) -> dict:
    """C-5 what-if: replace previous-generation hosts with the current standard; threads and memory before and after."""
    est = generator.load_spec()["estate"]
    gens = est["host_generations"]
    std = cap["settings"]["capacity.host_standard"]
    before = {"threads": replace_previous * gens["previous"]["threads"], "memory_gb": replace_previous * gens["previous"]["memory_gb"],
              "cores_licensed": replace_previous * gens["previous"]["cores"]}
    after = {"threads": new_hosts * std["threads"], "memory_gb": new_hosts * std["memory_gb"], "cores_licensed": new_hosts * std["cores"]}
    ld = [g for g in cap["groups"] if g["location"] == location]
    growth_threads = sum(g["resources"]["compute"]["slope_per_day"] * 365 for g in ld)
    growth_mem = sum(g["resources"]["memory"]["slope_per_day"] * 365 for g in ld)
    return {"location": location, "replace_previous": replace_previous, "new_hosts": new_hosts, "before": before, "after": after,
            "threads_gain": after["threads"] - before["threads"], "memory_gain_gb": after["memory_gb"] - before["memory_gb"],
            "next_year_growth": {"threads": round(growth_threads), "memory_gb": round(growth_mem)},
            "racks_saved_hosts": replace_previous - new_hosts}
