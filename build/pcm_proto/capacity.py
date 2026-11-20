"""Capacity engine: usable capacity, weekly peaks, the 13-month forecast, decision dates, the purchase plan,
reclamation and what-if (prototype).

GENERATED from spec/catalog/capacity.yaml, spec/catalog/settings.yaml and spec/data/stories.yaml.
Do not edit by hand (D-070). Executive, L2 and Capacity read their decision dates from here (PCM core, 1).
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import sqlite3

from . import generator, store

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


class State:
    """Demand register entries added on the page, in the PCM database (table demand_register, D-080).
    Planted story entries (C-4) stay synthetic: they are generated from "now", never stored."""

    @property
    def added(self) -> list:
        out = []
        for r in store.rows("SELECT * FROM demand_register ORDER BY id"):
            g = r.pop("cluster_group")
            out.append({**r, "group": g, "date": datetime.fromisoformat(r["date"]), "added": datetime.fromisoformat(r["added"])})
        return out

    def reset(self):
        """Prototype and test reset only."""
        store.execute("DELETE FROM demand_register")


STATE = State()


def trend(weekly: list, weeks: int) -> tuple[float, float]:
    """capacity.trend: least squares over the last `weeks` weekly peaks, close weeks left out."""
    last = len(weekly) - 1
    pts = [(-7 * (last - i), p["v"]) for i, p in enumerate(weekly) if i >= last - weeks and not p["close"]]
    return fit(pts)


def build(now: datetime, enable=(), register_as_of: datetime | None = None) -> dict:
    """register_as_of: leave out register entries added after this time (last week's view, for /capacity)."""
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
        register.append({**r, "group": stories["C-4"]["objects"]["cluster_group"], "date": generator.rel(r["when"], now),
                         "added": generator.rel(r.get("added", "now - 30 days"), now)})
    for r in STATE.added:
        register.append(dict(r))
    if register_as_of is not None:
        register = [r for r in register if r["added"] <= register_as_of]

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
                a, b = trend(weekly, st["capacity.trend_weeks"])
                # seasonal uplift: last year's excess over the trend inside the close week
                ex = [p["v"] - (a + b * (-7 * (56 - i))) for i, p in enumerate(weekly) if p["close"]]
                uplift = max(ex) if ex else 0.0
                pts90 = [(-7 * (13 - i), weekly[43 + i]["v"]) for i in range(14)]
                a90, b90 = fit(pts90)
                committed = lambda day: sum(r.get({"memory": "memory_gb", "compute": "compute_threads", "storage": "storage_tb"}[res], 0)
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
            "racks_saved_hosts": replace_previous - new_hosts,
            "covers_next_year_growth": (after["threads"] - before["threads"]) >= growth_threads
                                       and (after["memory_gb"] - before["memory_gb"]) >= growth_mem}


def planning_six_numbers(cls: str, cores: int, base_ghz: float, memory_gb: float, st: dict) -> dict:
    """capacity.planning_six_numbers: VMs per host by CPU and memory allocation, reservation and utilization (SP5 host
    specification). The smallest binds. The matching DRAM is what memory needs to hold as many VMs as the CPU does."""
    c = st["capacity.class_planning"][cls]
    hv = st["capacity.planning_hypervisor"]
    threads = cores * 2 - hv["threads"]
    ghz = cores * base_ghz - hv["system_reservation_ghz"]
    mem = memory_gb - hv["memory_gb"]
    n = {
        "cpu_allocation": threads * c["cpu_overcommit"] / c["vcpu"],
        "cpu_reservation": ghz / (c["vcpu"] * base_ghz * c["cpu_reservation"]),
        "cpu_utilization": threads / (c["vcpu"] * c["cpu_peak"]),
        "mem_allocation": mem * c["mem_overcommit"] / c["gb"],
        "mem_reservation": mem / (c["gb"] * c["mem_reservation"]),
        "mem_utilization": mem / (c["gb"] * c["mem_peak"]),
    }
    cpu_vms = min(n["cpu_allocation"], n["cpu_reservation"], n["cpu_utilization"])
    need = max(cpu_vms * c["gb"] / c["mem_overcommit"], cpu_vms * c["gb"] * c["mem_reservation"], cpu_vms * c["gb"] * c["mem_peak"])
    return {"class": cls, "inputs": {"cores": cores, "base_ghz": base_ghz, "memory_gb": memory_gb, **hv},
            "planning": c, "numbers": {k: round(v, 2) for k, v in n.items()}, "binds": min(n, key=n.get),
            "vms_per_host": round(min(n.values()), 1), "cpu_vms": round(cpu_vms, 1),
            "matching_dram_gb": round(need + hv["memory_gb"])}


# ---- Capacity workspace views (spec/api/capacity.yaml)

def _day(now, d):
    return None if d is None else (now + timedelta(days=d)).isoformat()


def _row(g: dict, now: datetime) -> dict:
    t = g["resources"][g["tightest"]]
    return {"id": g["id"], "location": g["location"], "location_name": g["location_name"], "class": g["class"],
            "hosts": g["hosts"], "tightest": g["tightest"], "remaining_percent": t["remaining_percent"],
            "time_remaining_days": t["run_out_days"], "run_out_date": _day(now, t["run_out_days"]),
            "decision_days": g["decision_days"], "decision_date": _day(now, g["decision_days"]),
            "in_plan": g["in_plan"], "round_on_time": g["round_on_time"], "quadrant": g["quadrant"],
            "peak_warning": g["peak_warning"] and {**g["peak_warning"], "date": _day(now, g["peak_warning"]["days"])}}


def contention(now: datetime, enable=()) -> dict:
    """Clusters not serving their VMs well now (Cluster Performance orange or red), per cluster group."""
    from . import noc
    out = {}
    for c in noc.build(now, enable)["clusters"]:
        if c["class"] in CLASSES and c["status"] in ("orange", "red"):
            out.setdefault(f"{c['location'].upper()}-{c['class'].capitalize()}", []).append(
                {"cluster": c["id"], "score": c["score"], "status": c["status"]})
    return out


def groups_view(now: datetime, enable=()) -> dict:
    cap = build(now, enable)
    hot = contention(now, enable)
    rows = []
    for g in cap["groups"]:
        r = _row(g, now)
        r["full_now"] = hot.get(g["id"])
        rows.append(r)
    rows.sort(key=lambda r: (r["decision_days"] if r["decision_days"] is not None else 10 ** 6))
    return {"now": now.isoformat(), "horizon_days": HORIZON_DAYS, "next_round_closes": cap["next_round_closes"].isoformat(),
            "groups": rows}


def group_detail(now: datetime, gid: str, enable=()) -> dict | None:
    cap = build(now, enable)
    g = next((x for x in cap["groups"] if x["id"] == gid), None)
    if g is None:
        return None
    res = {}
    for k, r in g["resources"].items():
        res[k] = {**r, "unit": {"compute": "threads", "memory": "GB", "storage": "TB"}[k],
                  "run_out_date": _day(now, r["run_out_days"]), "decision_date": _day(now, r["decision_days"]),
                  "run_out_90d_date": _day(now, r["run_out_90d_days"]), "peak_cross_date": _day(now, r["peak_cross_days"])}
    reg = [_reg(r) for r in cap["register"] if r["group"] == gid]
    return {**_row(g, now), "now": now.isoformat(), "clusters": g["clusters"], "lead_time_days": g["lead_time_days"], "resources": res, "register": reg,
            "full_now": contention(now, enable).get(gid)}


def _reg(r):
    return {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in r.items()}


def week(now: datetime, enable=()) -> dict:
    """What changed since last week: decision dates that moved because of new register entries, groups that entered
    their decision window, peak warnings and waste."""
    cap = build(now, enable)
    last = build(now, enable, register_as_of=now - timedelta(days=7))
    soon = cap["settings"]["capacity.decide_soon_days"]
    new_entries = [r for r in cap["register"] if r["added"] > now - timedelta(days=7)]
    moved, entered = [], []
    for g in cap["groups"]:
        lg = next(x for x in last["groups"] if x["id"] == g["id"])
        if g["decision_days"] is None or lg["decision_days"] is None:
            continue
        diff = lg["decision_days"] - g["decision_days"]
        if abs(diff) >= 7:
            because = [r["id"] for r in new_entries if r["group"] == g["id"]]
            moved.append({"group": g["id"], "days_earlier": diff, "decision_date": _day(now, g["decision_days"]),
                          "because_of": because, "causes": [{"id": r["id"], "kind": r["kind"], "source": r.get("source"),
                                                             "owner": r.get("owner")} for r in new_entries if r["group"] == g["id"]]})
        if g["decision_days"] <= soon and lg["decision_days"] + 7 > soon:
            entered.append(g["id"])
    plan = cap["plan"]
    return {"now": now.isoformat(), "next_round_closes": cap["next_round_closes"].isoformat(),
            "groups_in_round": [p["group"] for p in plan], "moved": moved, "entered_window": entered,
            "peak_warnings": [_row(g, now) for g in cap["groups"] if g["peak_warning"]],
            "waste": [_row(g, now) for g in cap["groups"] if g["quadrant"] == "waste"]}


def demand(now: datetime, enable=()) -> dict:
    cap = build(now, enable)
    return {"now": now.isoformat(), "entries": [_reg(r) for r in sorted(cap["register"], key=lambda r: r["date"])],
            "groups": [g["id"] for g in cap["groups"]]}


KINDS = ("project", "migration", "dr", "growth")


def add_demand(now: datetime, body: dict, enable=()) -> tuple[int, dict]:
    groups = {g["id"] for g in build(now, enable)["groups"]}
    missing = [k for k in ("kind", "group", "date", "owner") if not body.get(k)]
    if missing:
        return 400, {"error": f"missing: {', '.join(missing)}"}
    if body["kind"] not in KINDS or body["group"] not in groups:
        return 400, {"error": "unknown kind or group"}
    try:
        d = datetime.fromisoformat(body["date"])
    except ValueError:
        return 400, {"error": "date must be YYYY-MM-DD"}
    if d.tzinfo is None:
        d = d.replace(tzinfo=now.tzinfo)
    try:
        amounts = {k: float(body.get(k) or 0) for k in ("compute_threads", "memory_gb", "storage_tb")}
    except ValueError:
        return 400, {"error": "amounts must be numbers"}
    n = store.rows("SELECT COUNT(*) AS n FROM demand_register")[0]["n"]
    entry = {"id": f"dr-{n + 1:03d}", "kind": body["kind"], "source": body.get("source") or "",
             "group": body["group"], "date": d, "added": now, "owner": body["owner"], **amounts}
    try:
        store.execute("INSERT INTO demand_register (id, kind, source, cluster_group, date, added, owner, compute_threads, memory_gb, storage_tb) "
                      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (entry["id"], entry["kind"], entry["source"], entry["group"], d.isoformat(), now.isoformat(), entry["owner"],
                       amounts["compute_threads"], amounts["memory_gb"], amounts["storage_tb"]))
    except sqlite3.IntegrityError:
        return 400, {"error": "An entry needs at least one amount, none negative: threads, GB or TB."}
    g = next(x for x in groups_view(now, enable)["groups"] if x["id"] == body["group"])
    return 200, {"entry": _reg(entry), "group": g}


def plan_view(now: datetime, enable=()) -> dict:
    cap = build(now, enable)
    rows = [{**p, "delivery_date": _day(now, p["delivery_days"]), "cover_until_date": _day(now, p["cover_until_days"]),
             "decision_date": _day(now, next(g["decision_days"] for g in cap["groups"] if g["id"] == p["group"]))}
            for p in cap["plan"]]
    return {"now": now.isoformat(), "next_round_closes": cap["next_round_closes"].isoformat(), "rows": rows,
            "total": sum(r["total"] for r in rows), "depreciation_years": cap["settings"]["value.depreciation_years"],
            "host_standard": cap["settings"]["capacity.host_standard"]}


def waste_view(now: datetime, enable=()) -> dict:
    cap = build(now, enable)
    rec = [{**r, "run_out_date_before": _day(now, r["run_out_days_before"]), "run_out_date_after": _day(now, r["run_out_days_after"])}
           for r in cap["reclamation"]]
    return {"now": now.isoformat(), "reclamation": rec,
            "waste_groups": [_row(g, now) for g in cap["groups"] if g["quadrant"] == "waste"]}
