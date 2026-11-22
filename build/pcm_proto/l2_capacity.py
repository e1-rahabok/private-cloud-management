"""L2 Monitor, the Capacity tab (design/l2-workspace.md, 4.3.3 to 4.3.6; D-094, D-095, D-096).

GENERATED from spec/workspaces/l2/monitor.md (Capacity tab on a cluster, Capacity tab above the cluster),
spec/catalog/l2.yaml (l2.statistics, l2.cluster_kpi_series, l2.cluster_check, l2.contention_now,
l2.consumption_parts, l2.usable_capacity, l2.host_spread, l2.capacity_hosts, l2.closed_count,
l2.consumption_spread, l2.near_closure, l2.capacity_clusters_at, l2.capacity_findings), spec/catalog/settings.yaml
(adapter.*) and spec/data/stories.yaml (M-4, N-1, C-1). Do not edit by hand (D-070).

What PCM reads, and what the prototype models in its place (D-071):
- The PCM adapter (vCommunity, D-096) publishes, per cluster, three KPIs every 5 minutes and, once per check period,
  the Periodic Cluster Check: the worst end of each KPI over the period and Close for Business. Pages read them;
  they never recompute the decision. decide() exists to name the rule that matched and for the synthetic data.
- Synthetic check values: Consumption from a class base with slow drift; M-4 plants the last 7. Performance and Risk
  come from the Performance tab's own cluster series (one definition): for the last 7 checks, the 5th (Performance)
  or 95th (Risk) percentile of that day's hourly points; older checks hold the recent level, with small noise.
- Synthetic Consumption points: each check day's 5-minute points follow the location's bank load shape, scaled so that
  their 95th percentile (nearest rank) is exactly the day's check value. So the check value is what the chart shows.
- Performance and Risk points are the Performance tab's own series (l2_performance), so both tabs show one line.
- Simplification: an hourly point holds the worst of its hour, so a Performance or Risk check value is a little
  stricter than the 5-minute percentile the adapter takes.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

from . import generator, l2, l2_estate as X, l2_performance as P

DAY = 86400
HISTORY_CHECKS = 400                      # 13 months of check results, kept as their own series
CLASSES = P.CLASSES
DEFAULT_CLASS = "gold"                    # always Gold first: the priority (D-094 as settled)
NEAR_CLOSURE_ABOVE = 60.0                 # l2.near_closure: the orange closure level of Consumption
CONTENTION_BELOW = 50.0                   # l2.contention_now: th-cluster-perf-red, the NOC's red line
CONS_BASE = {"gold": (25, 42), "silver": (32, 50), "bronze": (38, 54), "mixed": (32, 50)}
KPIS = ("consumption", "performance", "risk")
KPI_LABEL = {"consumption": "Cluster Consumption", "performance": "Cluster Performance", "risk": "Cluster Risk"}
HIGHER_IS_WORSE = {"consumption": True, "performance": False, "risk": True}
PARTS = (("cpu_thread_utilization", "CPU Thread Utilization"), ("memory_consumed", "Memory Consumed"),
         ("memory_ballooned", "Memory Ballooned"), ("memory_zip_swap", "Memory Zip Swap"))
# Upper end of green, yellow and orange per part; above the last is red (l2.consumption_parts, band_ends). From the
# Agent E2 knowledge base, knowledge/catalog/thresholds-capacity.yaml, rows of cluster-consumption. A value on an end stays below it.
PART_BAND_ENDS = {"cpu_thread_utilization": [55, 70, 85], "memory_consumed": [70, 80, 90],
                  "memory_ballooned": [1, 2, 4], "memory_zip_swap": [0.25, 0.5, 1], "memory_tiering": [25, 50, 75]}


# ---------------------------------------------------------------- settings set in the PCM adapter (D-096)

def adapter() -> dict:
    s = generator.load_spec()["settings"]
    lv = s["adapter.cluster_closure_levels"]
    num = lambda x: float(str(x).split()[-1])
    return {"period_hours": int(s["adapter.cluster_check_period_hours"]), "time_utc": s["adapter.cluster_check_time_utc"],
            "worst_percent": int(s["adapter.cluster_check_worst_percent"]),
            "red": num(lv["performance"]["red"]), "orange": num(lv["performance"]["orange"])}


def check_label(worst_percent: int, period_hours: int) -> str:
    """l2.statistics naming: a check value is a percentile of its period, never "Worst"."""
    p = 100 - worst_percent
    suffix = "th" if 10 <= p % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(p % 10, "th")
    return f"{p}{suffix} percentile, {period_hours} hours to"


# ---------------------------------------------------------------- the rule (l2.cluster_check)

def health(v: float, higher_is_worse: bool) -> float:
    return 100.0 - v if higher_is_worse else v


def closure_level(v: float, higher_is_worse: bool, red: float = 20.0, orange: float = 40.0) -> str:
    """"red", "orange" or "open" on the value's health. A value on a level does not reach it."""
    h = health(v, higher_is_worse)
    return "red" if h < red else "orange" if h < orange else "open"


def decide(performance, risk, consumption, red: float = 20.0, orange: float = 40.0) -> dict:
    """The adapter's Close for Business, and which rule matched. No check when an input has no data."""
    if None in (performance, risk, consumption):
        return {"state": "no_check", "close": None, "rule": None}
    p = closure_level(performance, False, red, orange)
    r = closure_level(risk, True, red, orange)
    c = closure_level(consumption, True, red, orange)
    if "red" in (p, c):
        return {"state": "closed", "close": 1, "rule": 1, "performance_red": p == "red", "consumption_red": c == "red"}
    if p == c == "orange" and r in ("orange", "red"):
        return {"state": "closed", "close": 1, "rule": 2}
    return {"state": "open", "close": 0, "rule": None}


def reason(chk: dict) -> str | None:
    """The rule that matched, in words (monitor.md, Verdict)."""
    if chk["state"] != "closed":
        return None
    c, p, r = (round(chk[k]) for k in KPIS)
    if chk["rule"] == 2:
        return f"Consumption {c}% and Performance {p}% are both orange, and Risk {r}% is above 60%."
    parts = []
    if chk.get("consumption_red"):
        parts.append(f"Consumption {c}% is above 80%.")
    if chk.get("performance_red"):
        parts.append(f"Performance {p}% is below 20%.")
    return " ".join(parts)


def finding_kind(chk: dict) -> str | None:
    """l2.capacity_findings for the 24-hour window."""
    if chk["state"] != "closed":
        return None
    return "closed_contention" if chk["rule"] == 2 or chk.get("performance_red") else "closed_consumption"


# ---------------------------------------------------------------- check results, one per period (13 months)

def check_ends(now: datetime, count: int) -> list:
    """The latest check window ends, newest first. Periods of 24 hours ending at the adapter's time (UTC)."""
    a = adapter()
    hh, mm = (int(x) for x in a["time_utc"].split(":"))
    u = now.astimezone(timezone.utc)
    latest = u.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if latest > u:
        latest -= timedelta(days=1)
    return [latest - timedelta(hours=a["period_hours"] * k) for k in range(count)]


def _risk_base(c: dict) -> tuple:
    lo, hi, rise = P.RISK_BASE[c["class"]]
    return lo + (hi - lo) * X._h(c["id"], "risk"), rise


@lru_cache(maxsize=8)
def _checks(enable: tuple, now_iso: str) -> dict:
    """cluster id -> [check, newest first], HISTORY_CHECKS of them."""
    now = datetime.fromisoformat(now_iso)
    E, act = X.estate(enable), X.active_stories(enable)
    ends = check_ends(now, HISTORY_CHECKS)
    a = adapter()
    m4 = act.get("M-4", {}).get("plant", {})
    c1 = act.get("C-1")
    m3 = act.get("M-3")
    ps = P._cluster_series(enable, now_iso, "7d")
    start, L, n = P._slots(now, "7d")
    slot_end = [start + (i + 1) * L for i in range(n)]
    days = [[i for i, t in enumerate(slot_end) if e.timestamp() - DAY < t <= e.timestamp()] for e in ends[:7]]
    out = {}
    for c in (x for x in E.nodes.values() if x["kind"] == "cluster" and x["class"] in X.WORKLOADS):
        cid = c["id"]
        lo, hi = CONS_BASE[c["class"]]
        if c1 and c["location"] == "sg" and c["class"] == "silver":
            lo, hi = 50, 58  # C-1: Singapore Silver runs out of working memory; the same week in both horizons
        base = lo + (hi - lo) * X._h(cid, "cons")
        perf_pts, risk_pts = ps[cid]["performance"], ps[cid]["risk"]
        perf_level, risk_level = P.nearest_rank(perf_pts, 5), P.nearest_rank(risk_pts, 95)
        plant = m4.get(cid)
        rows = []
        for k, end in enumerate(ends):
            cons = base + 2.5 * math.sin(2 * math.pi * k / 180 + 6 * X._h(cid, "ph")) + (X._h(cid, "cd", k) - 0.5) * 3
            cons = min(59.0, cons)
            day = days[k] if k < 7 else []
            if day:
                perf = P.nearest_rank([perf_pts[i] for i in day], 5)
                risk = P.nearest_rank([risk_pts[i] for i in day], 95)
            else:
                perf = perf_level + (X._h(cid, "pd", k) - 0.5) * 1.0
                risk = risk_level + (X._h(cid, "rd", k) - 0.5) * 2.0
                if m3 and cid == m3["objects"]["risk_cluster"]:
                    risk = m3["plant"]["risk"]["seven_days_ago"] + (X._h(cid, "rd", k) - 0.5) * 2.0 + 1.4
            if plant:
                n4 = len(plant["consumption"])
                cons = plant["consumption"][n4 - 1 - k] if k < n4 else max(base, plant["consumption"][0] - 0.8 * (k - n4 + 1))
            cons, perf, risk = round(min(100.0, max(0.0, cons)), 1), round(min(100.0, max(0.0, perf)), 1), round(min(100.0, max(0.0, risk)), 1)
            d = decide(perf, risk, cons, a["red"], a["orange"])
            rows.append({"end": end.isoformat(), "consumption": cons, "performance": perf, "risk": risk, **d})
        out[cid] = rows
    return out


def checks(now: datetime, enable=()) -> dict:
    return _checks(tuple(enable), now.isoformat())


def since(rows: list) -> tuple:
    """The first check of the current unbroken run of closed checks, and how many checks it holds."""
    n = 0
    while n < len(rows) and rows[n]["state"] == "closed":
        n += 1
    return (rows[n - 1]["end"], n) if n else (None, 0)


def heading_to_closed(rows: list) -> bool:
    """l2.capacity_findings, 7-day window: open, and the last seven check values of Consumption drift up."""
    seven = [r["consumption"] for r in rows[:7]][::-1]
    return rows[0]["state"] == "open" and len(seven) == 7 and seven[-1] > seven[0] and l2.is_drift(seven)


# ---------------------------------------------------------------- 5-minute points (Consumption), exact to the check

@lru_cache(maxsize=256)
def _shape(cid: str, tz: str, now_iso: str) -> tuple:
    """288 values per UTC day: the bank's load in the location's time (online day, end-of-day batch), with fixed noise.
    Returns (shape, its 95th percentile)."""
    off = datetime.fromisoformat(now_iso).astimezone(ZoneInfo(tz)).utcoffset().total_seconds()
    vals = []
    for i in range(288):
        h = ((i * 300 + off) % DAY) / 3600
        day = 0.30 * max(0.0, math.sin(math.pi * (h - 8) / 10)) if 8 <= h <= 18 else 0.0
        batch = 0.45 * max(0.0, math.sin(math.pi * ((h - 22) % 24) / 5)) if (h >= 22 or h <= 3) else 0.0
        vals.append(0.35 + day + batch + 0.12 * X._h(cid, "shape", i))
    return tuple(vals), P.nearest_rank(vals, 95)


def _amp(cid: str, k: int) -> float:
    return 6 + 4 * X._h(cid, "amp", k)


def consumption_at(E, c: dict, rows: list, latest_end: float, t: float, now_iso: str) -> float:
    """The 5-minute Consumption point at epoch t. The check ending at the next period end holds it; today's
    unfinished period follows the latest check."""
    end = math.ceil(t / DAY) * DAY
    k = max(0, int(round((latest_end - end) / DAY)))
    k = min(k, len(rows) - 1)
    shape, p95 = _shape(c["id"], E.nodes[c["location"]]["time_zone"], now_iso)
    i = int(((t - 1) % DAY) // 300)
    return min(100.0, max(0.0, rows[k]["consumption"] + _amp(c["id"], k) * (shape[i] - p95)))


SUB_MINUTES = {"1h": 5, "24h": 5, "7d": 5, "30d": 5, "1y": 60}   # 5-minute points for 45 days, hourly for 13 months


@lru_cache(maxsize=16)
def _cons_series(enable: tuple, now_iso: str, window: str) -> dict:
    """cluster id -> Consumption at every point of the window; a point holds the worst value inside it."""
    now = datetime.fromisoformat(now_iso)
    E = X.estate(enable)
    ck = _checks(enable, now_iso)
    start, L, n = P._slots(now, window)
    sub = SUB_MINUTES[window] * 60
    per = max(1, int(L // sub))
    out = {}
    for cid, rows in ck.items():
        c = E.nodes[cid]
        latest = datetime.fromisoformat(rows[0]["end"]).timestamp()
        pts = []
        for i in range(n):
            s0 = start + i * L
            pts.append(round(max(consumption_at(E, c, rows, latest, s0 + (j + 1) * sub, now_iso) for j in range(per)), 1))
        out[cid] = pts
    return out


def _times(now: datetime, window: str) -> tuple:
    start, L, n = P._slots(now, window)
    return [datetime.fromtimestamp(start + (i + 1) * L, tz=now.tzinfo).isoformat() for i in range(n)], int(L // 60)


def figures(vals: list, times: list, higher_is_worse: bool, decimals: int = 1) -> dict:
    """l2.statistics over time: Now, Worst with its time, 95th percentile. Never an average."""
    xs = [(v, i) for i, v in enumerate(vals) if v is not None]
    if not xs:
        return {"now": None, "worst": None, "percentile_95": None}
    w = max(xs) if higher_is_worse else min(xs)
    p = P.nearest_rank([v for v, _ in xs], 95 if higher_is_worse else 5)
    r = lambda v: round(v, decimals)
    return {"now": r(vals[-1]) if vals[-1] is not None else None, "worst": {"v": r(w[0]), "t": times[w[1]]}, "percentile_95": r(p)}


# ---------------------------------------------------------------- parts, usable capacity, hosts

def _part(key: str, cons: float, cid: str, i: int) -> float:
    if key == "cpu_thread_utilization":
        return min(100.0, max(0.0, 30 + 0.38 * cons + (X._h(cid, "cpu", i) - 0.5) * 4))
    if key == "memory_consumed":
        return min(100.0, 55 + 0.45 * cons)
    if key == "memory_ballooned":
        return max(0.0, (cons - 70) * 0.08)
    return max(0.0, (cons - 75) * 0.03)


def usable_capacity(E, c: dict) -> dict:
    """l2.usable_capacity: total, minus HA (the largest host), minus buffer, over the running hosts."""
    buf = generator.load_spec()["settings"]["capacity.buffer_percent"]
    hosts = [E.nodes[h["id"]] for h in c["hosts"]]
    out = {"running_hosts": len(hosts), "hosts": len(hosts)}
    for key, per, unit, b in (("cpu", lambda h: h["cores"] * 2, "threads", buf["compute"]), ("memory", lambda h: h["memory_gb"], "GB of DRAM", buf["memory"])):
        total = sum(per(h) for h in hosts)
        ha = max(per(h) for h in hosts)
        buffer = round((total - ha) * b / 100)
        out[key] = {"unit": unit, "total": total, "ha": ha, "buffer": buffer, "buffer_percent": b, "usable": total - ha - buffer}
    return out


def _host_offsets(E, c: dict, rows: list, uc: dict, act: dict) -> dict:
    """host id -> (cpu offset, memory offset), in points of the host's own capacity. M-4 pins LD-B-01's spread."""
    hosts = [h["id"] for h in c["hosts"]]
    off = {h: ((X._h(h, "co") - 0.5) * 16, (X._h(h, "mo") - 0.5) * 10) for h in hosts}
    pin = act.get("M-4", {}).get("plant", {}).get(c["id"], {}).get("host_spread_memory")
    if pin and pin["highest"] in off:
        cons = rows[0]["consumption"]
        cluster_mem_total = _part("memory_consumed", cons, c["id"], 0) * uc["memory"]["usable"] / uc["memory"]["total"]
        lowest = next(h for h in reversed(hosts) if h != pin["highest"])
        off[pin["highest"]] = (off[pin["highest"]][0], pin["highest_percent"] - cluster_mem_total)
        off[lowest] = (off[lowest][0], pin["lowest_percent"] - cluster_mem_total)
    return off


# ---------------------------------------------------------------- the cluster page

def contention_now(E, c: dict, now: datetime, enable=()) -> dict | None:
    """l2.contention_now: Cluster Performance over the last hour, orange or red. The NOC's own number."""
    v = X.cluster_score(E, c, now, "1h", X.active_stories(enable))
    return {"value": round(v, 1), "t": now.isoformat()} if v < CONTENTION_BELOW else None


def cluster_view(now: datetime, cid: str, window: str, enable=(), marked_host: str | None = None) -> dict:
    enable = tuple(enable)
    E = X.estate(enable)
    c = E.nodes[cid]
    if c["class"] not in X.WORKLOADS:
        return {"cluster": cid, "applies": False}
    now_iso = now.isoformat()
    a = adapter()
    rows = _checks(enable, now_iso)[cid]
    times, minutes = _times(now, window)
    cons = _cons_series(enable, now_iso, window)[cid]
    ps = P._cluster_series(enable, now_iso, window)[cid]
    perf = list(ps["performance"])
    if perf:  # Now is the NOC's own value at this moment (l2.contention_now): one number for "now".
        story = next((x for x in X.active_stories(enable).values() if x.get("objects", {}).get("cluster") == cid
                      and "cluster_performance" in x.get("plant", {})), None)
        from . import noc
        perf[-1] = min(perf[-1], noc.cluster_score({"id": cid, "base": c["base"]}, now, story, now, 7))
    series = {"consumption": cons, "performance": perf, "risk": ps["risk"]}
    latest = rows[0]
    s_end, s_n = since(rows)
    cn = contention_now(E, c, now, enable)
    kpis = []
    for k in KPIS:
        kpis.append({"key": k, "label": KPI_LABEL[k], "better": "lower" if HIGHER_IS_WORSE[k] else "higher",
                     "points": [{"t": t, "v": v} for t, v in zip(times, series[k])], **figures(series[k], times, HIGHER_IS_WORSE[k]),
                     "check_value": latest[k], "closure_levels": {"red": 100 - a["red"], "orange": 100 - a["orange"]} if HIGHER_IS_WORSE[k]
                     else {"red": a["red"], "orange": a["orange"]}})
    w0 = now.timestamp() - X.WINDOW_HOURS[window] * 3600
    strip = [{"end": r["end"], "state": r["state"], "rule": r["rule"]} for r in rows if datetime.fromisoformat(r["end"]).timestamp() > w0][::-1]
    parts = []
    for key, label in PARTS:
        vals = [round(_part(key, v, cid, i), 2 if key in ("memory_ballooned", "memory_zip_swap") else 1) for i, v in enumerate(cons)]
        parts.append({"key": key, "label": label, "unit": "%", "band_ends": PART_BAND_ENDS[key], "points": [{"t": t, "v": v} for t, v in zip(times, vals)],
                      **figures(vals, times, True, 2 if key in ("memory_ballooned", "memory_zip_swap") else 1)})
    uc = usable_capacity(E, c)
    off = _host_offsets(E, c, rows, uc, X.active_stories(enable))
    cpu_tot = [_part("cpu_thread_utilization", v, cid, i) * uc["cpu"]["usable"] / uc["cpu"]["total"] for i, v in enumerate(cons)]
    mem_tot = [_part("memory_consumed", v, cid, i) * uc["memory"]["usable"] / uc["memory"]["total"] for i, v in enumerate(cons)]
    host_pts = {h: ([min(100.0, max(0.0, x + o[0])) for x in cpu_tot], [min(100.0, max(0.0, x + o[1])) for x in mem_tot]) for h, o in off.items()}
    spread = {}
    for j, key in enumerate(("cpu_thread_utilization", "memory_consumed")):
        pts = []
        for i, t in enumerate(times):
            vals = [(host_pts[h][j][i], h) for h in host_pts]
            hi, lo = max(vals), min(vals)
            pts.append({"t": t, "highest": round(hi[0], 1), "highest_host": hi[1], "lowest": round(lo[0], 1), "lowest_host": lo[1]})
        spread[key] = pts
    # The hosts' 95th percentile over the latest check day, 5-minute points: what the story pins.
    latest_end = datetime.fromisoformat(latest["end"]).timestamp()
    day_mem = [_part("memory_consumed", consumption_at(E, c, rows, latest_end, latest_end - DAY + (j + 1) * 300, now_iso), cid, 0)
               * uc["memory"]["usable"] / uc["memory"]["total"] for j in range(288)]
    p95_day = P.nearest_rank(day_mem, 95)
    hosts = []
    for h in c["hosts"]:
        hn = E.nodes[h["id"]]
        cpu, mem = host_pts[h["id"]]
        fc, fm = figures([round(x, 1) for x in cpu], times, True), figures([round(x, 1) for x in mem], times, True)
        vms = [E.nodes[v] for v in hn["vms"]]
        step = max(1, len(mem) // 60)
        hosts.append({"host": h["id"], "cpu_thread_utilization": {"percentile_95": fc["percentile_95"], "worst": fc["worst"]},
                      "memory_consumed": {"percentile_95": fm["percentile_95"], "worst": fm["worst"],
                                          "at_check_percentile_95": round(min(100.0, max(0.0, p95_day + off[h["id"]][1])), 1)},
                      "spark": [{"v": round(x, 1)} for x in mem[::step]], "running_vms": len(vms),
                      "cpu_overcommit": round(sum(v["vcpu"] for v in vms) / hn["cores"], 1),
                      "memory_overcommit": round(sum(v["memory_gb"] for v in vms) / hn["memory_gb"], 2),
                      "state": "running", "marked": h["id"] == marked_host})
    hosts.sort(key=lambda r: -max(r["cpu_thread_utilization"]["percentile_95"], r["memory_consumed"]["percentile_95"]))
    status = "red" if cn or finding_kind(latest) == "closed_contention" else "amber" if latest["state"] == "closed" else "no_data" if latest["state"] == "no_check" else "green"
    return {"cluster": cid, "applies": True, "class_of_service": c["class"], "location": E.nodes[c["location"]]["name"],
            "window": window, "point_minutes": minutes, "status": status,
            "check": {**latest, "since": s_end, "checks_closed": s_n, "reason": reason(latest), "period_hours": a["period_hours"],
                      "window_end": latest["end"], "worst_percent": a["worst_percent"], "label": check_label(a["worst_percent"], a["period_hours"]),
                      "previous": {k: rows[1][k] for k in ("end", "state", "consumption", "performance", "risk")}},
            "contention_now": cn, "kpis": kpis, "strip": strip, "strip_as_words": len(strip) < 7,
            "parts": parts, "memory_tiering": None, "usable": uc, "spread": spread, "hosts": hosts, "marked_host": marked_host}


# ---------------------------------------------------------------- Capacity Remaining, from VCF Operations (l2.capacity_remaining, D-100)

REMAINING_KINDS = {"vm": ("capacity_remaining", "time_remaining"),
                   "host": ("capacity_remaining", "time_remaining", "vm_remaining"),
                   "cluster": ("capacity_remaining", "time_remaining", "vm_remaining")}
REMAINING_LABEL = {"capacity_remaining": ("Capacity Remaining", "%"), "time_remaining": ("Time Remaining", " days"),
                   "vm_remaining": ("VM Remaining", " VMs")}


def capacity_remaining(n: dict, now: datetime) -> dict | None:
    """l2.capacity_remaining: VCF Operations' own Capacity Remaining, Time Remaining and VM Remaining for a VM, host
    or cluster. Release 1.0 has no VCF Operations connector, so the values are placeholders, flagged as such, never
    computed by PCM. The real values replace them, with their collection time, when the connector reads them."""
    keys = REMAINING_KINDS.get(n["kind"])
    if not keys:
        return None
    h = lambda k: X._h(n["id"], "remaining", k)
    dummy = {"capacity_remaining": round(10 + 60 * h("c"), 1), "time_remaining": int(30 + 330 * h("t")),
             "vm_remaining": int(5 + 120 * h("v")) if n["kind"] == "cluster" else int(2 + 25 * h("v"))}
    return {"source": "VCF Operations", "placeholder": True, "time": None,
            "values": [{"key": k, "label": REMAINING_LABEL[k][0], "unit": REMAINING_LABEL[k][1], "value": dummy[k]} for k in keys]}


# ---------------------------------------------------------------- above the cluster

def _scope(E, view: str, nid: str, cls: str, stale: set) -> list:
    from . import l2_monitor as M
    cids = sorted({h["cluster"] for h in M._hosts_under(E, view, nid)})
    return [E.nodes[c] for c in cids if E.nodes[c]["class"] in X.WORKLOADS and (cls == "all" or E.nodes[c]["class"] == cls)
            and E.nodes[c]["location"] not in stale]


def group_view(now: datetime, view: str, nid: str, window: str, cls: str = DEFAULT_CLASS, at: str | None = None, enable=()) -> dict:
    from . import l2_monitor as M
    if cls not in CLASSES:
        raise ValueError("class must be one of " + ", ".join(CLASSES))
    enable = tuple(enable)
    E = X.estate(enable)
    now_iso = now.isoformat()
    stale = M.stale_locations(now, enable)
    clusters = _scope(E, view, nid, cls, stale)
    times, minutes = _times(now, window)
    start, L, n = P._slots(now, window)
    ck = _checks(enable, now_iso)
    cs = _cons_series(enable, now_iso, window)
    ps = P._cluster_series(enable, now_iso, window)
    # Clusters closed, per check period in the window.
    w0 = now.timestamp() - X.WINDOW_HOURS[window] * 3600
    ends = [e for e in check_ends(now, HISTORY_CHECKS) if e.timestamp() > w0][::-1] or check_ends(now, 1)
    closed = []
    for e in ends:
        k = int(round((datetime.fromisoformat(ck[next(iter(ck))][0]["end"]).timestamp() - e.timestamp()) / DAY))
        closed.append({"end": e.isoformat(), "closed": sum(1 for c in clusters if ck[c["id"]][k]["state"] == "closed")})
    now_closed = [c["id"] for c in clusters if ck[c["id"]][0]["state"] == "closed"]
    newly = [c["id"] for c in clusters if ck[c["id"]][0]["state"] == "closed" and ck[c["id"]][1]["state"] == "open"]
    opened = [c["id"] for c in clusters if ck[c["id"]][0]["state"] == "open" and ck[c["id"]][1]["state"] == "closed"]
    # Consumption across clusters: the highest and its 90th percentile.
    spread = []
    for i in range(n):
        vals = [(cs[c["id"]][i], c["id"]) for c in clusters]
        hi = max(vals) if vals else (None, None)
        spread.append({"t": times[i], "highest": hi[0], "highest_cluster": hi[1],
                       "percentile": P.nearest_rank([v for v, _ in vals], 90)})
    # Near closure: open clusters above the orange closure level at the latest check; the count at each of the last 7 checks.
    near = [c["id"] for c in clusters if ck[c["id"]][0]["state"] == "open" and ck[c["id"]][0]["consumption"] > NEAR_CLOSURE_ABOVE]
    counts = [sum(1 for c in clusters if ck[c["id"]][k]["state"] == "open" and ck[c["id"]][k]["consumption"] > NEAR_CLOSURE_ABOVE)
              for k in range(6, -1, -1)]
    direction = ("rising" if counts[-1] > counts[0] else "falling") if l2.is_drift(counts) or counts[-1] != counts[0] else "steady"
    # The selected time.
    if at:
        t = datetime.fromisoformat(at)
        t = t if t.tzinfo else t.replace(tzinfo=now.tzinfo)
        if not (start < t.timestamp() <= now.timestamp()):
            raise ValueError("at must be inside the window")
        sel = min(n - 1, int(math.ceil((t.timestamp() - start) / L)) - 1)
    else:
        cand = [(p["highest"], -i) for i, p in enumerate(spread) if p["highest"] is not None]
        sel = -max(cand)[1] if cand else n - 1
    rank = lambda r: (0 if r["check"]["state"] == "closed" else 1 if r["near_closure"] else 2, -(r["consumption"] or 0), r["cluster"])
    rows = []
    for c in clusters:
        r0 = ck[c["id"]][0]
        s_end, s_n = since(ck[c["id"]])
        step = max(1, n // 60)
        rows.append({"cluster": c["id"], "location": E.nodes[c["location"]]["name"], "class_of_service": c["class"],
                     "check": {"state": r0["state"], "since": s_end, "checks_closed": s_n, "rule": r0["rule"], "consumption": r0["consumption"]},
                     "near_closure": c["id"] in near, "consumption": cs[c["id"]][sel],
                     "performance": ps[c["id"]]["performance"][sel], "risk": ps[c["id"]]["risk"][sel],
                     "spark": [{"v": v} for v in cs[c["id"]][::step]], "contention_now": contention_now(E, c, now, enable)})
    rows.sort(key=rank)
    return {"class": cls, "classes": list(CLASSES), "window": window, "point_minutes": minutes, "clusters": len(clusters),
            "stale_locations": sorted(E.nodes[s]["name"] for s in stale if s in E.nodes),
            "closed": {"per_check": closed, "now": len(now_closed), "now_clusters": now_closed, "closed_since_previous": newly,
                       "opened_since_previous": opened, "as_words": len(closed) < 7},
            "spread": {"percentile": 90, "points": spread, "closure_levels": {"red": 80, "orange": 60}},
            "near_closure": {"clusters": near, "counts_7_checks": counts, "direction": direction, "above": NEAR_CLOSURE_ABOVE},
            "selected": {"t": times[sel], "index": sel, "default": not at}, "clusters_at": rows}


# ---------------------------------------------------------------- findings and the headline

def findings(now: datetime, enable=()) -> list:
    """l2.capacity_findings for every workload cluster."""
    E = X.estate(tuple(enable))
    out = []
    for cid, rows in checks(now, enable).items():
        r0 = rows[0]
        kind = finding_kind(r0)
        if kind:
            s_end, s_n = since(rows)
            out.append({"id": f"f-cap-{cid.lower()}", "pillar": "capacity", "severity": "red" if kind == "closed_contention" else "amber",
                        "window": "24h", "kind": kind, "object": cid, "object_name": cid,
                        "outcome_fixed": "problem" if kind == "closed_contention" else "improve",
                        "summary": f"Closed for new VMs at the latest check ({s_n} check{'s' if s_n != 1 else ''}). {reason(r0)}",
                        "explained_by": None, "proposal": None, "evidence": None})
        elif heading_to_closed(rows):
            seven = [r["consumption"] for r in rows[:7]][::-1]
            out.append({"id": f"w-cap-{cid.lower()}", "pillar": "capacity", "severity": "amber", "window": "7d", "kind": "heading_to_closed",
                        "object": cid, "object_name": cid, "outcome_fixed": "improve",
                        "summary": f"Open, and its Consumption rose at the last seven checks, from {seven[0]}% to {seven[-1]}%.",
                        "explained_by": None, "proposal": None,
                        "evidence": {"nightly": seven, "unit": "% Cluster Consumption at each check"}})
    return out


def under_node(E, view: str, nid: str, now: datetime, enable=()) -> dict:
    """For the Summary row: closed and near-closure clusters under the node, every class."""
    from . import l2_monitor as M
    ck = checks(now, enable)
    cids = sorted({h["cluster"] for h in M._hosts_under(E, view, nid)} & set(ck))
    if not cids and X.node(E, nid) and X.node(E, nid).get("cluster") in ck:
        cids = [X.node(E, nid)["cluster"]]
    closed = [c for c in cids if ck[c][0]["state"] == "closed"]
    near = [c for c in cids if ck[c][0]["state"] == "open" and ck[c][0]["consumption"] > NEAR_CLOSURE_ABOVE]
    cn = [c for c in cids if contention_now(E, E.nodes[c], now, enable)]
    if closed:
        hl = f"{len(closed)} cluster{'s' if len(closed) != 1 else ''} closed for new VMs ({', '.join(closed[:4])}{', …' if len(closed) > 4 else ''}); "
    else:
        hl = "No cluster closed for new VMs; "
    hl += f"{len(near)} open near closure."
    if cn:
        hl += f" Contention now on {', '.join(cn[:3])}."
    return {"headline": hl, "closed": closed, "near_closure": near, "contention_now": cn}
