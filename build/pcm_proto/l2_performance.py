"""L2 Monitor, the Performance tab above the cluster: VM first, then Cluster (design/l2-workspace.md, 4.3.1).

GENERATED from spec/workspaces/l2/monitor.md (Performance tab above the cluster), spec/catalog/l2.yaml
(l2.consumer_hits, l2.worst_vms, l2.provider_spread, l2.clusters_at) and spec/data/stories.yaml (M-3).
Do not edit by hand (D-070).

Synthetic model, prototype only (D-071):
- A VM is hit when its VM Performance falls below green (75). Hits are intervals: background hits (a few
  percent of VMs per day, short), VMs whose score is below green all window, VMs a story plants now, and M-3.
  Background hits are modelled over the last 7 days only.
- A cluster's Performance at a time is the NOC's score for it (one definition), lowered by its VMs' hits as
  vCommunity combines them: 8 contention sub-metrics, 4 from the worst VM and 4 from the 90th percentile. A hit
  moves 2 of each 4 (CPU and memory, say); the others stay at 100.
- A cluster's Risk is a class base, a business-hours rise in the location's time zone, and noise. M-3 plants one rise.
"""
from __future__ import annotations

import math
import random
from datetime import datetime, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

from . import catalog, generator, l2_estate as X, noc

CLASSES = ("gold", "silver", "bronze", "all")
DEFAULT_CLASS = "gold"
GREEN = 75.0
PERCENTILE = {"performance": 10, "risk": 90}  # vCommunity's Worst 10 Percent (D-091)
SLOT_MINUTES = {"1h": 5, "24h": 5, "7d": 60, "30d": 240, "1y": 1440}
ABOVE_CLUSTER = {"estate", "region", "location", "vcf_instance", "workload_domain", "class_of_service"}
BACKGROUND_PER_DAY = {"gold": 0.02, "silver": 0.04, "bronze": 0.06}
MODELLED_DAYS = 7
RISK_BASE = {"gold": (4, 16, 5), "silver": (20, 40, 10), "bronze": (35, 55, 12), "mixed": (25, 45, 10)}  # low, high, business-hours rise
WORST_VMS = 20


def applies(n: dict) -> bool:
    """The tab's VM and Cluster sections show on nodes above the cluster."""
    return n["kind"] in ABOVE_CLUSTER


def perf_band(v: float | None) -> str:
    return "no_data" if v is None else catalog.kpi_band(v)


def risk_band(v: float | None) -> str:
    """Risk is higher-is-worse: the same four bands, the other way round."""
    return "no_data" if v is None else catalog.kpi_band(100 - v)


def nearest_rank(values: list, p: float) -> float | None:
    """vCommunity's percentile: sort, take the value at position p% of the count, rounded up."""
    if not values:
        return None
    s = sorted(values)
    return s[max(1, math.ceil(p / 100 * len(s))) - 1]


def kpi(scores: list) -> float:
    """vCommunity's weighted average by color: weight 2^((100 - score) / 25)."""
    w = [2 ** ((100 - s) / 25) for s in scores]
    return sum(s * x for s, x in zip(scores, w)) / sum(w)


# ---------------------------------------------------------------- hits (VM below green), cached per clock

def _ts(d: datetime) -> float:
    return d.timestamp()


@lru_cache(maxsize=8)
def _hits(enable: tuple, now_iso: str) -> dict:
    """vm id -> [(start, end, value)], epoch seconds. Only VMs that were below green at some time."""
    from . import l2_monitor as M
    now = datetime.fromisoformat(now_iso)
    E, act = X.estate(enable), X.active_stories(enable)
    end = _ts(now)
    quiet = end - 3600  # the last hour is the NOC's: no background hit there
    out: dict = {}
    vm1h = M._vm_scores(enable, now_iso, "1h")
    for v in E.nodes.values():
        if v["kind"] != "vm" or v["class_of_service"] not in BACKGROUND_PER_DAY:
            continue
        vid, p = v["id"], BACKGROUND_PER_DAY[v["class_of_service"]]
        hs = []
        if v["base"] < GREEN:  # below green the whole time
            hs.append((end - 400 * 86400, end, round(v["base"], 1)))
        elif vm1h.get(vid, 100) < GREEN:  # a story plants it now
            hs.append((end - 3600, end, round(vm1h[vid], 1)))
        for d in range(MODELLED_DAYS):
            if X._h(vid, "hit", d) >= p:
                continue
            s = end - (d + 1) * 86400 + X._h(vid, "at", d) * 86400
            e = s + (5 + 15 * X._h(vid, "dur", d)) * 60
            if e <= quiet:
                hs.append((s, e, round(58 + 16 * X._h(vid, "v", d), 1)))
        if hs:
            out[vid] = hs
    m3 = act.get("M-3")
    if m3:
        o, pl = m3["objects"], m3["plant"]
        for key, clusters in (("wide", o["wide_clusters"]), ("narrow", [o["narrow_cluster"]])):
            p = pl[key]
            s0, e0 = _ts(generator.rel(p["from"], now)), _ts(generator.rel(p["to"], now))
            lo, hi = p["vm_performance"]["from"], p["vm_performance"]["to"]
            for cid in clusters:
                for vid in _cluster_vms(E, cid):
                    if X._h(vid, "m3", key) < p["vm_share"]:
                        s = s0 + X._h(vid, "m3s", key) * 600
                        e = e0 - X._h(vid, "m3e", key) * 600
                        out.setdefault(vid, []).append((s, e, round(lo + (hi - lo) * X._h(vid, "m3v", key), 1)))
        t = pl["turns"]
        vms = sorted(_cluster_vms(E, o["turns_cluster"]), key=lambda x: X._h(x, "turns"))[: t["vms"]]
        span = 22.5 * 3600
        first = end - 23.5 * 3600
        for i, vid in enumerate(vms):
            s = first + (i + 0.3 * X._h(vid, "ts")) * span / len(vms)
            e = s + (t["minutes"]["from"] + (t["minutes"]["to"] - t["minutes"]["from"]) * X._h(vid, "td")) * 60
            lo, hi = t["vm_performance"]["from"], t["vm_performance"]["to"]
            out.setdefault(vid, []).append((s, e, round(lo + (hi - lo) * X._h(vid, "tv"), 1)))
    return out


def _cluster_vms(E, cid: str) -> list:
    return [v for h in E.nodes[cid]["hosts"] for v in E.nodes[h["id"]]["vms"]]


# ---------------------------------------------------------------- the window's points

def _slots(now: datetime, window: str) -> tuple:
    minutes = SLOT_MINUTES[window]
    n = X.WINDOW_HOURS[window] * 60 // minutes
    start = _ts(now) - n * minutes * 60
    return start, minutes * 60, n


def _slot_range(s: float, e: float, start: float, L: float, n: int) -> range:
    """The points an interval touches: a point holds the worst value inside it."""
    a = max(0, int((s - start) // L))
    b = min(n - 1, int(math.ceil((e - start) / L)) - 1)
    return range(a, b + 1) if b >= a and e > start else range(0)


@lru_cache(maxsize=16)
def _per_slot(enable: tuple, now_iso: str, window: str) -> dict:
    """vm id -> {slot: worst value}, for every VM hit in the window."""
    now = datetime.fromisoformat(now_iso)
    start, L, n = _slots(now, window)
    out = {}
    for vid, hs in _hits(enable, now_iso).items():
        m = {}
        for s, e, v in hs:
            for i in _slot_range(s, e, start, L, n):
                if v < m.get(i, 101):
                    m[i] = v
        if m:
            out[vid] = m
    return out


@lru_cache(maxsize=16)
def _cluster_series(enable: tuple, now_iso: str, window: str) -> dict:
    """cluster id -> {"performance": [..], "risk": [..], "hit": [..], "different": n} at every point."""
    now = datetime.fromisoformat(now_iso)
    E, act = X.estate(enable), X.active_stories(enable)
    start, L, n = _slots(now, window)
    ps = _per_slot(enable, now_iso, window)
    m3 = act.get("M-3")
    out = {}
    for c in (x for x in E.nodes.values() if x["kind"] == "cluster" and x["class"] in X.WORKLOADS):
        story = next((s for s in act.values() if s.get("objects", {}).get("cluster") == c["id"] and "cluster_performance" in s.get("plant", {})), None)
        vms = _cluster_vms(E, c["id"])
        k = max(1, math.ceil(0.1 * len(vms)))
        by_slot: dict = {}
        different = 0
        for vid in vms:
            m = ps.get(vid)
            if m:
                different += 1
                for i, v in m.items():
                    by_slot.setdefault(i, []).append(v)
        dip = next((x["plant"]["window_dip"] for x in act.values() if x.get("plant", {}).get("window_dip", {}).get("cluster") == c["id"]), None)
        dip_slot = next(iter(_slot_range(_ts(generator.rel(dip["at"], now)) - 1, _ts(generator.rel(dip["at"], now)), start, L, n)), None) if dip else None
        tz = ZoneInfo(E.nodes[c["location"]]["time_zone"])
        lo, hi, rise = RISK_BASE[c["class"]]
        base_risk = lo + (hi - lo) * X._h(c["id"], "risk")
        perf, risk, hit = [], [], []
        for i in range(n):
            t = start + (i + 1) * L
            td = datetime.fromtimestamp(t - L / 2, tz=now.tzinfo)
            v = noc.cluster_score({"id": c["id"], "base": c["base"]}, td, story, now, 7)
            vals = by_slot.get(i)
            if vals:
                vals.sort()
                p90 = vals[k - 1] if len(vals) >= k else 100.0
                v = min(v, kpi([vals[0], vals[0], 100.0, 100.0, p90, p90, 100.0, 100.0]))
            if i == dip_slot:
                v = min(v, float(dip["value"]))
            perf.append(round(v, 1))
            hit.append(len(vals) if vals else 0)
            hour = td.astimezone(tz).hour + td.astimezone(tz).minute / 60
            day = rise * max(0.0, math.sin(math.pi * (hour - 8) / 12)) if 8 <= hour <= 20 else 0.0
            r = base_risk + day + random.Random(f"risk-{c['id']}-{int(t // 300)}").uniform(-2.5, 2.5)
            if m3 and c["id"] == m3["objects"]["risk_cluster"]:
                a, b = m3["plant"]["risk"]["seven_days_ago"], m3["plant"]["risk"]["now"]
                frac = min(1.0, max(0.0, 1 - (_ts(now) - t) / (7 * 86400)))
                r = a + (b - a) * frac + random.Random(f"risk-{c['id']}-{int(t // 300)}").uniform(-1.5, 1.5)
            risk.append(round(min(100.0, max(0.0, r)), 1))
        out[c["id"]] = {"performance": perf, "risk": risk, "hit": hit, "different": different}
    return out


# ---------------------------------------------------------------- the tab

def _scope(E, view: str, nid: str, cls: str, stale: set) -> tuple:
    """The VMs and clusters in scope: under the node, of the class, not in a location without data."""
    from . import l2_monitor as M
    vms = [v for v in M._vms_under(E, view, nid)
           if v["class_of_service"] in BACKGROUND_PER_DAY and (cls == "all" or v["class_of_service"] == cls) and v["location"] not in stale]
    cids = sorted({h["cluster"] for h in M._hosts_under(E, view, nid)})
    clusters = [E.nodes[c] for c in cids if E.nodes[c]["class"] in X.WORKLOADS and (cls == "all" or E.nodes[c]["class"] == cls)
                and E.nodes[c]["location"] not in stale]
    return vms, clusters


def view(now: datetime, view_: str, nid: str, window: str, cls: str = DEFAULT_CLASS, at: str | None = None, enable=()) -> dict:
    from . import l2_monitor as M
    if cls not in CLASSES:
        raise ValueError("class must be one of " + ", ".join(CLASSES))
    enable = tuple(enable)
    key = (enable, now.isoformat(), window)
    E = X.estate(enable)
    stale = M.stale_locations(now, enable)
    vms, clusters = _scope(E, view_, nid, cls, stale)
    start, L, n = _slots(now, window)
    times = [datetime.fromtimestamp(start + (i + 1) * L, tz=now.tzinfo).isoformat() for i in range(n)]

    # Cluster: two lines per KPI.
    cs = _cluster_series(*key)
    perf_pts, risk_pts = [], []
    for i in range(n):
        pv = [(cs[c["id"]]["performance"][i], c["id"]) for c in clusters]
        rv = [(cs[c["id"]]["risk"][i], c["id"]) for c in clusters]
        wp, wr = min(pv) if pv else (None, None), max(rv) if rv else (None, None)
        perf_pts.append({"t": times[i], "worst": wp[0], "worst_cluster": wp[1],
                         "percentile": nearest_rank([x for x, _ in pv], PERCENTILE["performance"])})
        risk_pts.append({"t": times[i], "worst": wr[0], "worst_cluster": wr[1],
                         "percentile": nearest_rank([x for x, _ in rv], PERCENTILE["risk"])})

    # The selected time: a click, or the worst point of Worst Cluster Performance.
    if at:
        t = datetime.fromisoformat(at)
        t = t if t.tzinfo else t.replace(tzinfo=now.tzinfo)
        if not (start < _ts(t) <= _ts(now)):
            raise ValueError("at must be inside the window")
        sel = min(n - 1, int(math.ceil((_ts(t) - start) / L)) - 1)
    else:
        cand = [(p["worst"], i) for i, p in enumerate(perf_pts) if p["worst"] is not None]
        sel = min(cand)[1] if cand else n - 1  # the first point at the lowest value

    # VM: hit over time.
    ps = _per_slot(*key)
    scoped = {v["id"]: v for v in vms}
    hit_now = [0] * n
    first = {}
    for vid in scoped:
        m = ps.get(vid)
        if not m:
            continue
        for i in m:
            hit_now[i] += 1
        first[vid] = min(m)
    most = max(range(n), key=lambda i: (hit_now[i], i)) if n else 0
    vs = M._vm_scores(*key)
    consumer = {"vms": len(vms), "different": len(first), "most_at_once": hit_now[most] if n else 0,
                "most_at": times[most] if n else None,
                "near_line": sum(1 for v in vms if 75 <= vs[v["id"]] < 80), "below_green": sum(1 for v in vms if vs[v["id"]] < 75)}

    # VM: the worst VMs, or the VMs hit at the selected time.
    hits = _hits(enable, now.isoformat())
    five = 300.0

    spans = [(s, e, o) for o in scoped for s, e, _ in hits.get(o, ())]

    def together(vid: str, t0: float) -> int:
        return len({o for s, e, o in spans if o != vid and s < t0 + five and e > t0})

    rows = []
    if at:
        for vid in scoped:
            m = ps.get(vid)
            if m and sel in m:
                rows.append((m[sel], vid, start + sel * L))
        mode = "at"
    else:
        for vid in scoped:
            m = ps.get(vid)
            if not m:
                continue
            hv = [(v, max(s, start)) for s, e, v in hits[vid] if e > start and s < _ts(now)]
            v, s = min(hv)
            rows.append((v, vid, s))
        mode = "window"
    total = len(rows)
    rows.sort()
    out_rows = []
    for v, vid, t0 in rows[:WORST_VMS]:
        vm = scoped[vid]
        t5 = t0 - (t0 % five)
        out_rows.append({"vm": vid, "vm_performance": v, "status": X.status_of(v), "at": datetime.fromtimestamp(t5, tz=now.tzinfo).isoformat(),
                         "cluster": vm["cluster"], "location": E.nodes[vm["location"]]["name"], "class_of_service": vm["class_of_service"],
                         "together": together(vid, t5)})
    consumer.update(worst_vms=out_rows, worst_vms_mode=mode, worst_vms_total=total)

    # Cluster: every cluster at the selected time.
    at_rows = []
    for c in clusters:
        s = cs[c["id"]]
        p, r = s["performance"][sel], s["risk"][sel]
        at_rows.append({"cluster": c["id"], "location": E.nodes[c["location"]]["name"], "class_of_service": c["class"],
                        "performance": p, "performance_band": perf_band(p), "status": X.status_of(p),
                        "risk": r, "risk_band": risk_band(r), "vms_hit": s["hit"][sel], "different_vms_hit": s["different"]})
    at_rows.sort(key=lambda r: (r["performance"], -r["risk"], r["cluster"]))
    return {"class": cls, "classes": list(CLASSES), "window": window, "point_minutes": int(L // 60),
            "stale_locations": sorted(E.nodes[s]["name"] for s in stale if s in E.nodes),
            "consumer": consumer,
            "provider": {"clusters": len(clusters), "percentile": PERCENTILE, "performance": perf_pts, "risk": risk_pts},
            "selected": {"t": times[sel], "index": sel, "default": not at},
            "clusters_at": at_rows}
