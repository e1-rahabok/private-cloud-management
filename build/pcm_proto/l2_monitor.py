"""L2 Monitor: top down over the whole estate (design/l2-workspace.md, section 4).

GENERATED from spec/workspaces/l2/monitor.md and frame.md, spec/catalog/l2.yaml and spec/data/.
Do not edit by hand (D-070).

Every view is scoped to one node of the inventory tree, one pillar and one window (D-086).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from functools import lru_cache

from . import generator, l2, l2_capacity as CAP, l2_estate as X, l2_performance as P, l2_story_m5 as S5, noc

PILLARS = ("availability", "performance", "capacity", "security", "configuration", "inventory")
# Inventory counts objects and their changes: a provider tab (l2.pillars, D-092).
CONSUMER_KINDS = ("vm", "guest_os", "virtual_disk", "vnic")


def pillars_for(n: dict) -> tuple:
    return tuple(p for p in PILLARS if not (p == "inventory" and n["kind"] in CONSUMER_KINDS))
RANK = {"red": 0, "amber": 1, "no_data": 2, "green": 3}
WORST = lambda xs: min(xs, key=lambda s: RANK.get(s, 3)) if xs else "green"


def _key(now: datetime) -> str:
    return now.isoformat()


# ---------------------------------------------------------------- scores, cached per clock and window

@lru_cache(maxsize=32)
def _vm_scores(enable: tuple, now_iso: str, window: str) -> dict:
    now = datetime.fromisoformat(now_iso)
    E, act = X.estate(enable), X.active_stories(enable)
    return {n["id"]: X.vm_score(E, n, now, window, act) for n in E.nodes.values() if n["kind"] == "vm"}


@lru_cache(maxsize=32)
def _cluster_scores(enable: tuple, now_iso: str, window: str) -> dict:
    now = datetime.fromisoformat(now_iso)
    E, act = X.estate(enable), X.active_stories(enable)
    return {n["id"]: X.cluster_score(E, n, now, window, act) for n in E.nodes.values() if n["kind"] == "cluster"}


@lru_cache(maxsize=32)
def _host_scores(enable: tuple, now_iso: str, window: str) -> dict:
    E, act = X.estate(enable), X.active_stories(enable)
    now = datetime.fromisoformat(now_iso)
    vs = _vm_scores(enable, now_iso, window)
    out = {}
    for h in (n for n in E.nodes.values() if n["kind"] == "host"):
        vals = sorted(vs[v] for v in h["vms"])
        out[h["id"]] = (vals[max(0, int(len(vals) * 0.1) - 1)] if len(vals) > 3 else vals[0]) if vals else 99.0
        if act.get("M-5") and h["id"] == "sg-esx-110":
            out[h["id"]] = X.story_m5_score("esxi_performance", now, window)
    return out


def stale_locations(now: datetime, enable=()) -> set:
    ds = generator.generate(now, enable=enable)
    return {lid for lid, l in ds["locations"].items() if l["stale"]}


def perf_score(E, n: dict, now: datetime, window: str, enable=()) -> float | None:
    """l2.node_score for any node. Above the cluster: the worst child (provider performance is bottom up)."""
    k, key = n["kind"], (tuple(enable), _key(now), window)
    if k == "vm":
        return _vm_scores(*key)[n["id"]]
    if k == "guest_os":
        vm = E.nodes[n["vm"]]
        return guest_os_values(vm, X.active_stories(enable))["guest_os_performance"]
    if k in ("virtual_disk", "vnic"):
        return _vm_scores(*key)[n["vm"]]
    if k == "host":
        return _host_scores(*key)[n["id"]]
    if k == "cluster":
        return _cluster_scores(*key)[n["id"]]
    if k == "datastore":
        vs = _vm_scores(*key)
        vals = [vs[v] for v in n["vms"]]
        return min(vals) if vals else 99.0
    if k == "resource_pool":
        vs = _vm_scores(*key)
        return min(vs[v] for v in n["members"])
    if k in ("port_group",):
        c = E.nodes[n["cluster"]]
        return _cluster_scores(*key)[c["id"]]
    kids = X.children(E, "compute" if k not in ("distributed_switch", "class_of_service") else
                      ("network" if k == "distributed_switch" else "class"), n["id"])
    if k == "location" and n.get("class"):
        kids = X.children(E, "class", n["id"])
    vals = [perf_score(E, c, now, window, enable) for c in kids if c["kind"] not in ("resource_pool",)]
    vals = [v for v in vals if v is not None]
    return min(vals) if vals else None


def guest_os_values(vm: dict, act: dict) -> dict:
    """The Guest OS's "on my court" values (l2.realms). Planted for story VMs, normal otherwise."""
    healthy = {"disk_queue": 1 + int(X._h(vm["id"], "dq") * 4), "free_memory_mb": 700 + int(X._h(vm["id"], "fm") * 1200)}
    if act.get("L-2") and vm["id"] == act["L-2"]["objects"]["vm"]:
        return {**healthy, **act["L-2"]["plant"]["guest_os"]}
    if act.get("T-1") and vm["id"] == act["T-1"]["objects"]["vm"]:
        return {**healthy, **act["T-1"]["plant"]["guest_os"]}
    h = X._h(vm["id"], "os")
    return {"run_queue_per_vcpu": round(0.1 + h * 0.6, 2), "context_switches_per_s": int(3000 + h * 9000),
            "paging_per_s": int(h * 4), "guest_os_performance": round(90 + h * 8, 1), **healthy}


def vm_values(vm: dict, score: float, act: dict) -> dict:
    """The VM's "on my court" values (l2.realms)."""
    lack = max(0.0, 100 - score)
    # The sub-metrics of the VM Performance KPI without a planted value: healthy, a little worse as the score falls.
    base = {"cpu_ready_percent": round(0.3 + lack * 0.12, 1), "co_stop_percent": round(lack * 0.02, 1),
            "cpu_overlap_percent": round(0.1 + lack * 0.02, 1), "memory_contention_percent": 0.0,
            "disk_latency_ms": round(2 + lack * 0.2, 1), "network_dropped_tx_percent": 0.0,
            "cpu_run_percent": round(40 + X._h(vm["id"], "run") * 40, 1), "memory_ballooned_percent": 0.0,
            "memory_zip_swap_percent": 0.0, "vm_performance": score}
    if act.get("L-2") and vm["id"] == act["L-2"]["objects"]["vm"]:
        p = dict(act["L-2"]["plant"]["vm"])
        if "memory_wait_percent" in p:
            p["memory_contention_percent"] = p.pop("memory_wait_percent")
        return {**base, **p}
    if act.get("T-1") and vm["id"] == act["T-1"]["objects"]["vm"]:
        c = act["T-1"]["plant"]["vm_counters"]
        return {**base, "cpu_ready_percent": c["cpu_ready_percent"], "co_stop_percent": c["co_stop_percent"],
                "memory_contention_percent": c["memory_wait_percent"], "disk_latency_ms": c["disk_latency_ms"],
                "cpu_run_percent": c.get("run_percent", base["cpu_run_percent"]), "vm_performance": score}
    return base


# ---------------------------------------------------------------- a VM's two layers (l2.realms, D-092)

# (key, label, unit, better, decimals, scale, band_ends). The label never holds the unit; the unit follows the number.
# band_ends: upper end of green, yellow, orange, from the Agent E2 catalog (thresholds-performance.yaml, VirtualMachine and
# Guest OS rows; Run Queue per vCPU from the adapter's Guest OS Performance table: 2, 4, 8). None where there is no row (Context Switches).
LAYER_METRICS = (
    ("guest_os", "Guest OS", (
        ("run_queue_per_vcpu", "Run Queue", " per vCPU", "lower", 2, None, [2, 4, 8]),
        ("context_switches_per_s", "Context Switches", "/s", "lower", 0, None, None),
        ("disk_queue", "Disk Queue", " IOs", "lower", 0, None, [20, 40, 80]),
        ("free_memory_mb", "Free Memory", " MB", "higher", 0, None, [512, 256, 128]),
        ("paging_per_s", "Page-Out Rate", " pages/s", "lower", 0, None, [1000, 2000, 4000]),
        ("guest_os_performance", "Guest OS Performance", "%", "higher", 1, (0, 100), None))),
    ("virtual_motherboard", "Virtual Motherboard", (
        ("cpu_ready_percent", "CPU Ready", "%", "lower", 1, None, [2, 4, 8]),
        ("co_stop_percent", "CPU Co-Stop", "%", "lower", 1, None, [1, 2, 4]),
        ("cpu_overlap_percent", "CPU Overlap", "%", "lower", 1, None, [0.5, 1, 2]),
        ("memory_contention_percent", "Memory Contention", "%", "lower", 1, None, [0.5, 1, 2]),
        ("disk_latency_ms", "Disk Latency", " ms", "lower", 1, None, [10, 20, 40]),
        ("network_dropped_tx_percent", "Network Dropped Tx", "%", "lower", 1, None, [0, 0.5, 1]),
        ("cpu_run_percent", "CPU Run", "%", "lower", 1, None, [95, 97, 99]),
        ("memory_ballooned_percent", "Memory Ballooned", "%", "lower", 1, None, [2, 4, 8]),
        ("memory_zip_swap_percent", "Memory Zip Swap", "%", "lower", 1, None, [0.25, 0.5, 1]),
        ("vm_performance", "VM Performance", "%", "higher", 1, (0, 100), None))),
)


def _series(vm_id: str, key: str, now_value: float, better: str, decimals: int, scale, n: int) -> list:
    """One metric's points over the window, ending at the value the page already knows. Deterministic noise;
    the worst value inside a point is the point (D-091)."""
    out = []
    for i in range(n):
        h, spike = X._h(vm_id, key, i), X._h(vm_id, key, "spike", i)
        if better == "higher" and scale is None:
            v = max(0, now_value * (0.9 + 0.2 * h) * (0.6 if spike > 0.97 else 1))
        elif better == "higher":
            v = now_value + (h - 0.5) * 6 - (8 + 12 * spike if spike > 0.97 else 0)
            v = min(scale[1], max(scale[0], v))
        else:
            v = now_value * (0.55 + 0.9 * h) * (1.8 + spike if spike > 0.97 else 1)
        out.append(v)
    out[-1] = now_value
    return [int(round(v)) if decimals == 0 else round(v, decimals) for v in out]


def vm_layers(n: dict, now: datetime, window: str, act: dict, own: float) -> list:
    """The Guest OS on top, the Virtual Motherboard under it. Per metric: points, now, worst with its time,
    and the 95th percentile. Never an average."""
    values = {"guest_os": guest_os_values(n, act), "virtual_motherboard": vm_values(n, round(own, 1), act)}
    start, L, count = P._slots(now, window)
    times = [datetime.fromtimestamp(start + (i + 1) * L, tz=now.tzinfo).isoformat() for i in range(count)]
    m5 = act.get("M-5") and n["id"] == S5.VM  # story M-5: the VM's own rows, and the rows of VM Performance the tab hides
    rows5 = S5.part_series("vm_rows", now.timestamp(), start, L, count) if m5 else {}
    layers = []
    for lk, title, metrics in LAYER_METRICS:
        out = []
        if m5 and lk == "virtual_motherboard":
            metrics = metrics[:-1] + tuple((k, lab, "%", "lower", dec, None, ends) for k, lab, _u, dec, ends, _r in S5.VM_EXTRA_ROWS) + metrics[-1:]
        for key, label, unit, better, dec, scale, ends in metrics:
            if m5 and key == "vm_performance":
                vals = S5.slot_values(S5.story()["vm_performance"], now.timestamp(), start, L, count, "higher")
            elif m5 and lk == "virtual_motherboard":
                src = S5.VM_LAYER_KEYS.get(key) or next(r for k, *_x, r in S5.VM_EXTRA_ROWS if k == key)
                vals = rows5[src]
            else:
                vals = _series(n["id"], key, values[lk][key], better, dec, scale, count)
            if m5 and lk == "virtual_motherboard":
                vals = [int(round(v)) if dec == 0 else round(v, dec) for v in vals]
            w = max(range(count), key=lambda i: vals[i]) if better == "lower" else min(range(count), key=lambda i: vals[i])
            p95 = P.nearest_rank(vals, 95 if better == "lower" else 5)
            out.append({"key": key, "label": label, "unit": unit, "better": better, "decimals": dec, "scale": scale,
                        "minutes": L // 60, "points": [{"t": t, "v": v} for t, v in zip(times, vals)],
                        "now": vals[-1], "worst": {"v": vals[w], "t": times[w]}, "percentile_95": p95,
                        **({"band_ends": ends} if ends else {})})
        status = X.status_of(values[lk]["guest_os_performance"] if lk == "guest_os" else own)
        layers.append({"key": lk, "title": title, "status": status, "metrics": out})
    return layers


# ---------------------------------------------------------------- the object's own Performance KPI (l2.object_kpis, D-100)

# The KPI each kind of object is read by, as the PCM adapter (vCommunity) names it. Datastore and resource pool have
# no KPI of their own: their score is the worst VM on them (l2.node_score), and the label says so.
OBJECT_KPI_LABEL = {"cluster": "Cluster Performance", "host": "ESXi Performance", "guest_os": "Guest OS Performance",
                    "virtual_disk": "VM Performance", "vnic": "VM Performance", "port_group": "Cluster Performance",
                    "datastore": "Worst VM Performance", "resource_pool": "Worst VM Performance"}


def _kpi(key: str, label: str, better: str, vals: list, times: list, minutes: int) -> dict:
    xs = [(v, i) for i, v in enumerate(vals) if v is not None]
    w = (max(xs) if better == "lower" else min(xs)) if xs else None
    p95 = P.nearest_rank([v for v, _ in xs], 95 if better == "lower" else 5) if xs else None
    return {"key": key, "label": label, "unit": "%", "better": better, "decimals": 1, "scale": (0, 100), "minutes": minutes,
            "points": [{"t": t, "v": v} for t, v in zip(times, vals)], "now": vals[-1] if vals else None,
            "worst": {"v": w[0], "t": times[w[1]]} if w else None, "percentile_95": None if p95 is None else round(p95, 1),
            "bands": "lower_is_better" if better == "higher" else "higher_is_worse"}


# What a cluster KPI is made of (D-106). Performance: the contention of its VMs, worst VM (Depth) and 90th percentile
# (Breadth), and the worst host's bad packets. Risk: the worst host's utilization, saturation, reservation, allocation
# and monster VMs. Names and band ends are the Agent E2 catalog's (knowledge/catalog/thresholds-performance.yaml,
# thresholds-capacity.yaml, rows of cluster-performance and cluster-risk). Release 1.0: values derived from the KPI's
# own series, until PCM reads the parts from VCF Operations. A performance part has no band at 5 minutes in the
# catalog (its levels are for 20-second points), so it shows none. Memory tiering parts: only where hosts have a tier.
# (key, label, unit, decimals, value from the KPI value v: contention is 100 - v for Performance, v for Risk, band_ends)
PERFORMANCE_PARTS = (
    ("worst_vcpu_ready", "Worst peak vCPU Ready among all VMs", "%", 1, lambda c: c * 0.18, [4, 8, 16]),
    ("worst_vcpu_costop", "Worst peak vCPU Co-stop among all VMs", "%", 1, lambda c: c * 0.08, [2, 4, 8]),
    ("worst_memory_wait", "Worst memory wait among all VMs", "%", 1, lambda c: c * 0.04, [1, 2, 4]),
    ("worst_disk_latency", "Worst peak read/write disk latency, all VM vDisks", " ms", 1, lambda c: c * 3.2, [40, 80, 160]),
    ("p90_vcpu_ready", "90th percentile peak vCPU Ready among VMs", "%", 1, lambda c: c * 0.05, [1, 2, 4]),
    ("p90_vcpu_costop", "90th percentile peak vCPU Co-stop among VMs", "%", 1, lambda c: c * 0.02, [0.5, 1, 2]),
    ("p90_memory_wait", "90th percentile memory wait among VMs", "%", 1, lambda c: c * 0.01, [0.5, 1, 2]),
    ("p90_disk_latency", "90th percentile read/write latency among VM virtual disks", " ms", 1, lambda c: c * 1.0, [20, 40, 60]),
    ("highest_esxi_packets", "Highest ESXi (error + dropped) network packets", "%", 2, lambda c: c * 0.004, [0, 0.2, 0.4]),
)
# An ESXi host: the same nine parts over the VMs on the host (HostSystem rows of the same catalog file). Memory wait is
# "memory latency" there. D-108.
HOST_PARTS = (
    ("worst_vcpu_ready", "Worst peak vCPU Ready among VMs on the host", "%", 1, lambda c: c * 0.18, [4, 8, 16]),
    ("worst_vcpu_costop", "Worst peak vCPU Co-stop among VMs on the host", "%", 1, lambda c: c * 0.08, [2, 4, 8]),
    ("worst_memory_latency", "Worst memory latency among VMs on the host", "%", 1, lambda c: c * 0.04, [1, 2, 4]),
    ("worst_disk_latency", "Worst peak read/write disk latency, all vDisks of VMs on the host", " ms", 1, lambda c: c * 3.2, [40, 80, 160]),
    ("p90_vcpu_ready", "90th percentile peak vCPU Ready among VMs on the host", "%", 1, lambda c: c * 0.05, [1, 2, 4]),
    ("p90_vcpu_costop", "90th percentile peak vCPU Co-stop among VMs on the host", "%", 1, lambda c: c * 0.02, [0.5, 1, 2]),
    ("p90_memory_latency", "90th percentile memory latency among VMs on the host", "%", 1, lambda c: c * 0.01, [0.5, 1, 2]),
    ("p90_disk_latency", "90th percentile read/write latency among virtual disks of VMs on the host", " ms", 1, lambda c: c * 1.0, [20, 40, 60]),
    ("esxi_packets", "ESXi (error + dropped) network packets", "%", 2, lambda c: c * 0.004, [0, 0.2, 0.4]),
)
# Where red ends on a part's chart (the last number of the catalog's red band). The chart gives each of the four bands
# the same height, so every part reads alike: green, yellow, orange and red each a quarter of the axis.
BAND_TOP = {"worst_vcpu_ready": 32, "worst_vcpu_costop": 16, "worst_memory_wait": 8, "worst_memory_latency": 8, "worst_disk_latency": 320,
            "p90_vcpu_ready": 8, "p90_vcpu_costop": 4, "p90_memory_wait": 4, "p90_memory_latency": 4, "p90_disk_latency": 80,
            "highest_esxi_packets": 0.8, "esxi_packets": 0.8,
            "highest_esxi_cpu_thread_utilization": 95, "worst_esxi_cpu_imbalance": 2, "highest_esxi_memory_consumed": 100,
            "worst_esxi_memory_ballooned": 8, "worst_esxi_swapped_zipped_memory": 2, "highest_esxi_cpu_reservation": 80,
            "highest_esxi_memory_reservation": 80, "highest_esxi_cpu_overcommit": 4, "highest_esxi_memory_overcommit": 2.2,
            "highest_cpu_monster_vm_host_ratio": 4, "highest_memory_monster_vm_host_ratio": 4}
RISK_PARTS = (
    ("highest_esxi_cpu_thread_utilization", "Highest ESXi CPU thread utilization", "%", 1, lambda r: min(100.0, 28 + 0.75 * r), [60, 80, 90]),
    ("worst_esxi_cpu_imbalance", "Worst ESXi CPU imbalance", "", 2, lambda r: 1 + 0.004 * r, [1, 1.3, 1.6]),
    ("highest_esxi_memory_consumed", "Highest ESXi DRAM Memory Consumed", "%", 1, lambda r: min(100.0, 55 + 0.5 * r), [80, 90, 95]),
    ("worst_esxi_memory_ballooned", "Worst ESXi memory ballooned", "%", 2, lambda r: max(0.0, (r - 45) * 0.12), [1, 2, 4]),
    ("worst_esxi_swapped_zipped_memory", "Worst ESXi swapped + zipped memory", "%", 2, lambda r: max(0.0, (r - 55) * 0.05), [0.25, 0.5, 1]),
    ("highest_esxi_cpu_reservation", "Highest ESXi CPU reservation", "%", 1, lambda r: 0.4 * r, [10, 40, 60]),
    ("highest_esxi_memory_reservation", "Highest ESXi memory reservation", "%", 1, lambda r: 0.5 * r, [10, 40, 60]),
    ("highest_esxi_cpu_overcommit", "Highest ESXi CPU overcommit ratio", "", 1, lambda r: 0.9 + 0.025 * r, [1, 2, 3]),
    ("highest_esxi_memory_overcommit", "Highest ESXi memory overcommit ratio", "", 2, lambda r: 0.8 + 0.012 * r, [1, 1.4, 1.8]),
    ("highest_cpu_monster_vm_host_ratio", "Highest CPU monster VM : host ratio", "", 1, lambda r: 0.3 + 0.012 * r, [1, 2, 3]),
    ("highest_memory_monster_vm_host_ratio", "Highest memory monster VM : host ratio", "", 1, lambda r: 0.25 + 0.01 * r, [1, 2, 3]),
)


def kpi_details(cid: str, kpi_key: str, vals: list, times: list, minutes: int, host: bool = False, rows: dict | None = None) -> list:
    """l2.kpi_details: the parts of Cluster Performance or Cluster Risk over the window, same points as the KPI.
    Each part: points, Now, Worst with its time, 95th percentile (never an average). Lower is better for every part."""
    perf = kpi_key in ("cluster_performance", "esxi_performance")
    out = []
    for key, label, unit, dec, f, ends in HOST_PARTS if host else PERFORMANCE_PARTS if perf else RISK_PARTS:
        if rows is not None:  # story M-5: the parts the KPI was computed from, not values derived from it
            pts = [round(v, dec) for v in rows[key]]
        else:
            pts = [None if v is None else round(max(0.0, f(100 - v if perf else v) * (0.92 + 0.16 * X._h(cid, key, i))), dec) for i, v in enumerate(vals)]
        if rows is None and pts and pts[-1] is not None and vals[-1] is not None:
            pts[-1] = round(max(0.0, f(100 - vals[-1] if perf else vals[-1])), dec)
        part = {"key": key, "label": label, "unit": unit, "decimals": dec, "better": "lower", "scale": None, "minutes": minutes,
                "points": [{"t": t, "v": v} for t, v in zip(times, pts)], **CAP.figures(pts, times, True, dec)}
        if ends:
            part["band_ends"] = ends
            part["band_top"] = BAND_TOP[key]
        out.append(part)
    return out


def object_kpis(E, n: dict, now: datetime, window: str, enable=()) -> list:
    """l2.object_kpis: the Performance KPI of a cluster or anything under it, over the window, one point per slot
    (l2.statistics). First on its Performance tab. A cluster adds Cluster Risk: potential slowness (D-091)."""
    start, L, count = P._slots(now, window)
    times = [datetime.fromtimestamp(start + (i + 1) * L, tz=now.tzinfo).isoformat() for i in range(count)]
    cid = n["id"] if n["kind"] == "cluster" else n.get("cluster") if n["kind"] == "port_group" else None
    if cid:
        series = P._cluster_series(tuple(enable), now.isoformat(), window).get(cid)
        if series:  # one definition with the Capacity tab: Now is the NOC's own value at this moment
            cap = CAP.cluster_view(now, cid, window, enable)
            perf = {k["key"]: k for k in cap.get("kpis", [])}.get("performance")
            pv = [p["v"] for p in perf["points"]] if perf else [None if v is None else round(v, 1) for v in series["performance"]]
            rv = [None if v is None else round(v, 1) for v in series["risk"]]
            ks = [_kpi("cluster_performance", "Cluster Performance", "higher", pv, times, L // 60),
                  _kpi("cluster_risk", "Cluster Risk", "lower", rv, times, L // 60)]
            m5 = X.active_stories(enable).get("M-5") and cid == S5.CLUSTER
            for k, vals in zip(ks, (pv, rv)):
                rows = S5.part_series("cluster_rows" if k["key"] == "cluster_performance" else "risk_rows", now.timestamp(), start, L, count) if m5 else None
                k["details"] = kpi_details(cid, k["key"], vals, times, L // 60, rows=rows)
            return ks
    s = perf_score(E, n, now, window, enable)
    if s is None:
        return []
    label = OBJECT_KPI_LABEL.get(n["kind"], "Performance")
    key = label.lower().replace(" ", "_")
    m5 = X.active_stories(enable).get("M-5") and n["kind"] == "host" and n["id"] == S5.HOST
    if m5:  # story M-5: the host's own points and the rows they were computed from
        vals = [round(v, 1) for v in S5.slot_values(S5.story()["esxi_performance"], now.timestamp(), start, L, count, "higher")]
    else:
        vals = _series(n["id"], key, round(s, 1), "higher", 1, (0, 100), count)
    k = _kpi(key, label, "higher", vals, times, L // 60)
    if n["kind"] == "host":  # D-108: the parts of ESXi Performance, as for a cluster
        rows = S5.part_series("host_rows", now.timestamp(), start, L, count) if m5 else None
        k["details"] = kpi_details(n["id"], key, vals, times, L // 60, host=True, rows=rows)
    return [k]


# ---------------------------------------------------------------- where an object sits

def ancestors(E, nid: str) -> set:
    """Every node an object sits under, in every view: a finding shows on each of them."""
    base = nid if nid in E.nodes else nid.split("/")[0]
    out = set()
    for v in X.VIEWS:
        if base in E.parent[v] or base == "estate":
            out |= set(E.path(v, base))
    n = E.nodes.get(base)
    if n and n["kind"] == "datastore":
        out |= set(E.path("compute", n["cluster"]))
    if n and n["kind"] == "location" and n.get("class"):
        out |= set(E.path("compute", n["location"]))
    return out


def under(E, nid: str, node_id: str) -> bool:
    return node_id == "estate" or node_id in ancestors(E, nid)


# ---------------------------------------------------------------- findings (l2.findings)

OUTCOME = {"present_health": "problem", "risk": "improve", "efficiency": "improve"}
# SP5: only availability and performance are troubleshot. Security goes to the security team when breached (D-044);
# capacity, configuration and inventory are improved, not troubleshot (L2 design, 3.3).
TROUBLESHOOT_PILLARS = ("availability", "performance")
WEEKLY_PILLAR = {"slow_drift": "capacity", "hidden_in_average": "performance", "configuration_drift": "configuration"}
WEEKLY_OUTCOME = {"slow_drift": "improve", "hidden_in_average": "problem", "configuration_drift": "improve"}
OBJECT_OF = {"London ESXi hosts": "LD-S-01", "SG-Silver": "class-silver/sg"}


def findings(now: datetime, enable=()) -> list:
    """Every finding of the latest daily (24h) and weekly (7d) runs, with its outcome. Cached until the next action."""
    base = _findings(tuple(enable), _key(now), len(noc.STATE.history))
    cases_by_finding = _cases_by_finding()
    return [{**f, "case": cases_by_finding.get(f["id"])} for f in base]


@lru_cache(maxsize=16)
def _findings(enable: tuple, now_iso: str, version: int) -> list:
    now = datetime.fromisoformat(now_iso)
    E, act = X.estate(tuple(enable)), X.active_stories(enable)
    out = []
    for f in l2.daily(now, enable)["findings"]:
        obj = OBJECT_OF.get(f["object"], f["object"])
        out.append({**{k: f[k] for k in ("id", "pillar", "severity", "summary")}, "window": "24h", "kind": None,
                    "object": obj, "object_name": f["object"], "outcome": OUTCOME[f["verdict"]],
                    "explained_by": f.get("explained_by"), "proposal": f.get("proposal"), "evidence": None})
    for f in l2.weekly(now, enable)["findings"]:
        out.append({"id": f["id"], "pillar": WEEKLY_PILLAR[f["kind"]], "severity": "amber", "summary": f["summary"] + " " + f["cause"],
                    "window": "7d", "kind": f["kind"], "object": f["object"], "object_name": f["object"],
                    "outcome": WEEKLY_OUTCOME[f["kind"]], "explained_by": None, "proposal": None, "evidence": f.get("evidence")})
    m1 = act.get("M-1")
    if m1:
        p = m1["plant"]["finding"]
        out.append({"id": "f-m1-remote-memory", "pillar": p["pillar"], "severity": p["severity"], "summary": p["summary"],
                    "window": p["window"], "kind": p["kind"], "object": m1["objects"]["location"], "object_name": "London",
                    "outcome": "problem", "explained_by": None, "proposal": None,
                    "evidence": {"nightly": m1["plant"]["remote_memory_percent_7_nights"], "unit": "% of memory remote",
                                 "group_by": "host_model"}, "story": "M-1"})
    m2 = act.get("M-2")
    if m2:
        p = m2["plant"]["finding"]
        out.append({"id": "f-m2-other-wait", "pillar": p["pillar"], "severity": p["severity"], "summary": p["summary"],
                    "window": p["window"], "kind": None, "object": m2["objects"]["location"], "object_name": "Virginia",
                    "outcome": "problem", "explained_by": None, "proposal": None, "evidence": None, "story": "M-2"})
    u2 = act.get("U-2")
    if u2:
        o = u2["objects"]
        out.append({"id": "f-u2-down", "pillar": "availability", "severity": "amber", "window": "24h", "kind": None,
                    "object": o["cluster"], "object_name": o["cluster"], "outcome": "problem", "explained_by": None, "proposal": None,
                    "evidence": None, "summary": f"{len(o['vms'])} production VMs ({', '.join(o['vms'])}) were down for "
                                                 f"{u2['plant']['downtime']['minutes']} minutes outside any change window. Counted; within the Silver allowance."})
    e1 = act.get("E-1")
    if e1:
        for c in e1["plant"]["certificates_expiring"]:
            lid = c["component"].split("-")[-2]
            d = (generator.rel(c["expires"], now).date() - now.date()).days
            out.append({"id": f"f-cert-{c['component']}", "pillar": "security", "severity": "amber", "window": "24h", "kind": None,
                        "object": f"vcf-{lid}-01", "object_name": c["component"], "outcome": "improve", "explained_by": None,
                        "proposal": None, "evidence": None, "summary": f"Certificate on {c['component']} expires in {d} days."})
    out.extend(CAP.findings(now, enable))  # l2.capacity_findings (D-094)
    for c in l2.inventory(now, 7, enable)["unexplained"]:
        obj = {"Tokyo": "tk"}.get(c["object"], c["object"])
        out.append({"id": f"f-{c['id']}", "pillar": "inventory", "severity": "red" if c["count"] > 1 else "amber", "window": "24h",
                    "kind": None, "object": obj, "object_name": c["object"],
                    "outcome": "problem" if c["count"] > 1 else "improve", "explained_by": None, "proposal": None, "evidence": None,
                    "summary": f"Unexplained change: {c['detail']}, by {c['by']} through {c['via']}."})
    for f in out:
        f["path"] = [n["name"] for n in X.path(E, X.view_of(E, f["object"]), f["object"])] if X.node(E, f["object"]) else []
        f["outcome"] = f.pop("outcome_fixed", None) or ("problem" if f["pillar"] in TROUBLESHOOT_PILLARS else "improve")
        f["under"] = sorted(ancestors(E, f["object"])) if X.node(E, f["object"]) else ["estate"]
    order = {"red": 0, "amber": 1}
    out.sort(key=lambda f: (1 if f.get("explained_by") else 0, order[f["severity"]], f["window"] != "24h"))
    return out


def _cases_by_finding() -> dict:
    from . import l2_cases
    return {c["finding"]: c["id"] for c in l2_cases.STATE.cases.values() if c.get("finding")}


def findings_under(now: datetime, node_id: str, enable=(), pillar: str | None = None, window: str = "24h") -> list:
    fs = [f for f in findings(now, enable) if node_id in f["under"] or node_id == f["object"] or node_id == "estate"]
    if pillar and pillar != "summary":
        fs = [f for f in fs if f["pillar"] == pillar]
    if window == "24h" or window == "1h":
        fs = [f for f in fs if f["window"] == "24h"]
    elif window == "7d":
        fs = [f for f in fs if f["window"] == "7d"]
    return fs


def pillar_status(findings_list: list) -> dict:
    """l2.pillar_status: the worst status of each pillar's findings."""
    return {p: WORST([f["severity"] for f in findings_list if f["pillar"] == p]) for p in PILLARS}


# ---------------------------------------------------------------- pillar content

def _vms_under(E, view: str, nid: str) -> list:
    n = X.node(E, nid)
    if n is None:
        return []
    if n["kind"] == "vm":
        return [n]
    if n["kind"] in ("guest_os", "virtual_disk", "vnic"):
        return [E.nodes[n["vm"]]]
    if n["kind"] == "resource_pool":
        return [E.nodes[v] for v in n["members"]]
    if n["kind"] == "host":
        return [E.nodes[v] for v in n["vms"]]
    if n["kind"] == "datastore":
        return [E.nodes[v] for v in n["vms"]]
    if view not in X.VIEWS or nid not in E.parent[view] and nid != "estate":
        view = X.view_of(E, nid)
    return E.descendants(view, nid, "vm")


def _hosts_under(E, view: str, nid: str) -> list:
    n = X.node(E, nid)
    if n is None or n["kind"] in ("vm", "guest_os", "virtual_disk", "vnic", "datastore"):
        return []
    if n["kind"] == "host":
        return [n]
    v = view if (nid in E.parent["compute"] or nid == "estate") and view == "compute" else "compute"
    if n["kind"] == "location" and n.get("class"):
        return [h for c in E.kids("class", nid) for h in E.kids("compute", c["id"]) if h["kind"] == "host"]
    if n["kind"] == "class_of_service":
        return [h for loc in E.kids("class", nid) for c in E.kids("class", loc["id"]) for h in E.kids("compute", c["id"]) if h["kind"] == "host"]
    if nid not in E.parent["compute"] and nid != "estate":
        return []
    return E.descendants(v, nid, "host")


def near_line_count(scores, lo: float = 75, hi: float = 80) -> int:
    """l2.iceberg: how many sit just above the green line."""
    return sum(1 for s in scores if lo <= s < hi)


def iceberg(E, view: str, nid: str, now: datetime, window: str, enable=()) -> dict:
    """l2.iceberg: VMs under the node just above the green line now, and over the last 7 days."""
    cfg = generator.load_spec()["estate"]
    lo, hi = 75, 80
    vms = _vms_under(E, view, nid)
    vs = _vm_scores(tuple(enable), _key(now), window)
    now_n = sum(1 for v in vms if lo <= vs[v["id"]] < hi)
    below = sum(1 for v in vms if vs[v["id"]] < lo)
    act = X.active_stories(enable)
    m1 = set(act["M-1"]["objects"]["affected_vms"]) if act.get("M-1") else set()
    trend = []
    for d in range(6, -1, -1):
        cnt = 0
        for v in vms:
            s = vs[v["id"]]
            if v["id"] in m1:  # rising toward the line night by night
                s = s + (d * 1.2)
            else:
                s = s + (X._h(v["id"], d) - 0.5) * 1.2 if d else s
            cnt += lo <= s < hi
        trend.append(cnt)
    direction = "rising" if trend[-1] > trend[0] + max(1, trend[0] * 0.05) else "falling" if trend[-1] < trend[0] - max(1, trend[0] * 0.05) else "steady"
    days = [(now - timedelta(days=d)).isoformat() for d in range(6, -1, -1)]
    return {"vms": len(vms), "near_line": now_n, "below_green": below, "trend_7_days": trend, "direction": direction,
            "points_7_days": [{"t": t, "v": v} for t, v in zip(days, trend)], "near_line_from": lo, "near_line_to": hi}


def group_by(E, view: str, nid: str, attribute: str, now: datetime, window: str, enable=()) -> list:
    """l2.slice_attributes: descendants grouped by one attribute."""
    vs = _vm_scores(tuple(enable), _key(now), window)
    host_attrs = ("host_model", "esxi_build", "firmware")
    if attribute in host_attrs:
        rows = {}
        for v in _vms_under(E, view, nid):
            h = E.nodes[v["host"]]
            r = rows.setdefault(h[attribute], {"value": h[attribute], "hosts": set(), "vms": 0, "below_green": 0, "near_line": 0,
                                               "worst": 100.0, "wider_than_numa_node": 0})
            s = vs[v["id"]]
            r["hosts"].add(h["id"]); r["vms"] += 1; r["below_green"] += s < 75; r["near_line"] += 75 <= s < 80
            r["worst"] = min(r["worst"], s); r["wider_than_numa_node"] += v["vcpu"] > h["cores_per_numa_node"]
        out = [{**r, "hosts": len(r["hosts"])} for r in rows.values()]
    else:
        rows = {}
        for v in _vms_under(E, view, nid):
            val = v.get(attribute) if attribute != "vcpu_band" else ("1-4" if v["vcpu"] <= 4 else "5-16" if v["vcpu"] <= 16 else "17+")
            h = E.nodes[v["host"]]
            r = rows.setdefault(val, {"value": val, "vms": 0, "below_green": 0, "near_line": 0, "worst": 100.0, "wider_than_numa_node": 0})
            s = vs[v["id"]]
            r["vms"] += 1; r["below_green"] += s < 75; r["near_line"] += 75 <= s < 80; r["worst"] = min(r["worst"], s)
            r["wider_than_numa_node"] += v["vcpu"] > h["cores_per_numa_node"]
        out = list(rows.values())
    for r in out:
        r["worst"] = round(r["worst"], 1)
        r["status"] = X.status_of(r["worst"])
    return sorted(out, key=lambda r: (-r["below_green"] / max(1, r["vms"]), r["worst"]))


def _alerts_by_object(now: datetime, enable=()) -> dict:
    nd = noc.build(now, enable)
    out = {}
    for inc in nd["incidents"]:
        for a in inc["alerts"]:
            sev = "red" if a["severity"] == "red" else "orange"
            out.setdefault(a["object"], {"red": 0, "orange": 0})[sev] += 1
    return out


def node_row(E, view: str, n: dict, now: datetime, window: str, enable=(), alerts=None) -> dict:
    s = perf_score(E, n, now, window, enable)
    s_now = perf_score(E, n, now, "1h", enable) if window != "1h" else s
    worst = None if s is None else min(s, s_now if s_now is not None else s)
    row = {"id": n["id"], "kind": n["kind"], "name": n.get("appliance_name") and f"{n['name']} ({n['appliance_name']})" or n["name"],
           "score": None if s is None else round(s, 1), "score_now": None if s_now is None else round(s_now, 1),
           "band": X.band(worst), "status": X.status_of(worst), "_worst": worst}
    a = (alerts or {}).get(n["id"], {"red": 0, "orange": 0})
    row["alerts"] = a
    if n["kind"] == "host":
        row.update(host_model=n["host_model"], esxi_build=n["esxi_build"], running_vms=len(n["vms"]))
    if n["kind"] == "vm":
        row.update(vcpu=n["vcpu"], memory_gb=n["memory_gb"], class_of_service=n["class_of_service"],
                   environment=n["environment"], guest_os=n["guest_os"])
    if n["kind"] == "cluster":
        row.update(class_of_service=n["class"], hosts=len(n["hosts"]))
    return row


def stale_for(E, nid: str, now: datetime, enable=()) -> bool:
    st = stale_locations(now, enable)
    return bool(st & ancestors(E, nid))


def summary(now: datetime, view: str, nid: str, window: str, enable=()) -> dict | None:
    E = X.estate(tuple(enable))
    n = X.node(E, nid)
    if n is None:
        return None
    fs = findings_under(now, nid, enable, None, window)
    st = pillar_status(fs)
    perf = perf_score(E, n, now, window, enable)
    st["performance"] = WORST([st["performance"], X.status_of(perf)]) if perf is not None else st["performance"]
    stale = stale_for(E, nid, now, enable)
    rows = []
    for p in pillars_for(n):
        rows.append({"pillar": p, "status": "no_data" if stale and p in ("availability", "performance") else st[p],
                     "findings": sum(1 for f in fs if f["pillar"] == p), "headline": headline(E, view, nid, p, now, window, enable)})
    out = {"object": node_out(E, view, nid), "window": window, "run": run_line(now, window), "pillars": rows,
           "findings": fs, "slipped_alerts": slipped(now, enable, window), "stale": stale}
    if nid == "estate" and window == "1y":
        out["measures"] = l2.monthly(now, enable)["baselines"]
        out["repeated_problems"] = l2.monthly(now, enable)["repeated_escalations"]
    return out


def slipped(now, enable, window):
    if window == "7d":
        return l2.weekly(now, enable)["slipped_alerts"]
    if window in ("24h", "1h"):
        return [{**s, "would_have_caught_it": "A check rule on each virtual disk's latency, not the VM average."} for s in l2.daily(now, enable)["slipped_alerts"]]
    return []


def run_line(now: datetime, window: str) -> dict:
    """Which check run the window reads (frame.md, Object header)."""
    if window in ("1h", "24h"):
        d = l2.daily(now)["run"]
        return {"kind": "daily", "region": d["region"], "started_at": d["started_at"], "finished_at": d["finished_at"], "review": d["review"]}
    if window == "7d":
        w = l2.weekly(now)["run"]
        return {"kind": "weekly", "region": w["region"], "started_at": w["started_at"], "finished_at": w["finished_at"], "review": w["review"]}
    return {"kind": "baseline", "review": "Baselines over the window, from the daily and weekly runs."}


def node_out(E, view: str, nid: str) -> dict:
    n = X.node(E, nid)
    v = X.view_of(E, nid, view)
    return {"id": nid, "kind": n["kind"], "name": n.get("name"), "view": v,
            "path": [{"id": p["id"], "name": p.get("name"), "kind": p["kind"]} for p in X.path(E, v, nid)]}


def headline(E, view, nid, pillar, now, window, enable) -> str:
    c = pillar_content(E, view, nid, pillar, now, window, enable, brief=True)
    return c.get("headline", "")


def pillar_content(E, view, nid, pillar, now, window, enable=(), brief=False) -> dict:
    act = X.active_stories(enable)
    n = X.node(E, nid)
    if pillar == "performance":
        kids = [k for k in X.children(E, X.view_of(E, nid, view), nid)]
        sc = [(k, perf_score(E, k, now, window, enable), perf_score(E, k, now, "1h", enable)) for k in kids]
        sc = [(k, min(s, s1 if s1 is not None else s)) for k, s, s1 in sc if s is not None]
        out = [k for k, s in sc if s < 75]
        worst = min(sc, key=lambda x: x[1]) if sc else None
        ice = iceberg(E, view, nid, now, window, enable) if not brief or n["kind"] in ("estate", "region", "location") else None
        hl = (f"Worst: {worst[0]['name']} at {round(worst[1])}. {len(out)} of {len(sc)} outside the green zone."
              if worst else f"Score {round(perf_score(E, n, now, window, enable) or 0)}.")
        if ice:
            hl += f" {ice['near_line']} VMs just above the line, {ice['direction']}."
        return {"headline": hl, "iceberg": ice}
    if pillar == "availability":
        ds = generator.generate(now, enable=enable)
        evs = []
        for e in ds["health"]["up"]["events"]:
            obj = act["U-1"]["objects"]["cluster"] if e.get("change_ref") else act["U-2"]["objects"]["cluster"] if act.get("U-2") else None
            if obj and (nid == "estate" or under(E, obj, nid)):
                evs.append({**e, "object": obj})
        counted = sum(1 for e in evs if e["counted"])
        stale = sorted(stale_locations(now, enable) & (ancestors(E, nid) | {x["id"] for x in E.descendants("compute", nid, "location")} if nid in E.parent["compute"] or nid == "estate" else set()))
        hl = (f"{counted} downtime event counted this month, {len(evs) - counted} inside approved windows (not counted)."
              if evs else "No VM down this month.")
        if stale:
            hl += f" No data from {', '.join(E.nodes[s]['name'] for s in stale)}."
        return {"headline": hl, "events": evs, "stale_locations": stale, "hosts_not_connected": 0, "ha_restarts": 0}
    if pillar == "capacity":
        return CAP.under_node(E, view, nid, now, enable)
    if pillar == "security":
        hosts = [h for h in _hosts_under(E, view, nid) if h.get("ssh_on")]
        fs = [f for f in findings(now, enable) if f["pillar"] == "security" and (nid == "estate" or nid in f["under"])]
        certs = [f for f in fs if f["id"].startswith("f-cert-")]
        hl = f"{len(hosts)} hosts with SSH on outside a maintenance window; {len(certs)} certificates near expiry."
        return {"headline": hl, "ssh_hosts": [{"id": h["id"], "cluster": h["cluster"]} for h in hosts],
                "certificates": [{"object": f["object_name"], "summary": f["summary"]} for f in certs],
                "lockdown_off": 0, "root_logins": 0}
    if pillar == "configuration":
        hosts = _hosts_under(E, view, nid)
        vms = _vms_under(E, view, nid) if not brief or n["kind"] not in ("estate",) else _vms_under(E, view, nid)
        builds, tools = {}, {}
        for h in hosts:
            builds[h["esxi_build"]] = builds.get(h["esxi_build"], 0) + 1
        for v in vms:
            tools[v["tools_version"]] = tools.get(v["tools_version"], 0) + 1
        items = config_items_under(E, nid, now, enable)
        hl = f"{len(items)} drift finding{'s' if len(items) != 1 else ''}; {len(builds)} ESXi builds and {len(tools)} VMware Tools versions in use."
        return {"headline": hl, "drift": items, "esxi_builds": sorted(builds.items(), key=lambda x: -x[1]),
                "tools_versions": sorted(tools.items(), key=lambda x: -x[1])}
    if pillar == "inventory":
        return inventory_content(E, view, nid, now, window, enable, brief)
    return {}


def config_items_under(E, nid: str, now: datetime, enable=()) -> list:
    out = []
    for g, items in l2.configuration(now, enable)["groups"].items():
        for it in items:
            objs = it.get("objects") or [it["object_id"]]
            if nid == "estate" or any(o == nid or (X.node(E, o) and nid in ancestors(E, o)) for o in objs):
                out.append({**it, "group": g})
    return out


def inventory_content(E, view, nid, now, window, enable=(), brief=False) -> dict:
    n = X.node(E, nid)
    hosts = _hosts_under(E, view, nid)
    vms = _vms_under(E, view, nid)
    clusters = {h["cluster"] for h in hosts} if hosts else ({n["cluster"]} if n.get("cluster") else set())
    days = 30 if window in ("30d", "1y") else 7
    inv = l2.inventory(now, days, enable)
    share = len(vms) / max(1, sum(1 for x in E.nodes.values() if x["kind"] == "vm"))
    unexplained = [c for c in inv["unexplained"] if nid == "estate" or under(E, {"Tokyo": "tk"}.get(c["object"], c["object"]), nid)]
    hl = f"{len(hosts)} hosts, {len(vms):,} VMs; {len(unexplained)} unexplained change{'s' if len(unexplained) != 1 else ''} in {days} days."
    if brief:
        return {"headline": hl}
    kids = X.children(E, X.view_of(E, nid, view), nid)
    dist = []
    for k in kids:
        kv = _vms_under(E, view, k["id"]) if k["kind"] not in ("guest_os", "virtual_disk", "vnic") else []
        dist.append({"id": k["id"], "name": k["name"], "kind": k["kind"], "vms": len(kv)})
    explained = {t: {e: round(c * share) for e, c in by.items()} for t, by in inv["explained_by_type"].items()}
    return {"headline": hl, "counts": {"clusters": len(clusters), "hosts": len(hosts), "vms": len(vms),
                                        "datastores": len({v['datastore'] for v in vms})},
            "change": {"created": round(sum(explained["created"].values())), "deleted": round(sum(explained["deleted"].values()))},
            "distribution": dist, "unexplained": unexplained, "explained_by_type": explained,
            "expected_by_l2": [c for c in inv["expected_by_l2"] if nid == "estate" or under(E, {"Tokyo": "tk"}.get(c["object"], c["object"]), nid)],
            "pcm_actions": [c for c in inv["pcm_actions"] if nid == "estate" or (X.node(E, c["object"]) and under(E, c["object"], nid))],
            "days": days}


def pillar_view(now: datetime, view: str, nid: str, pillar: str, window: str, group: str | None = None, enable=(),
                cls: str | None = None, at: str | None = None) -> dict | None:
    E = X.estate(tuple(enable))
    n = X.node(E, nid)
    if n is None or pillar not in pillars_for(n):
        return None
    v = X.view_of(E, nid, view)
    alerts = _alerts_by_object(now, enable)
    kids = X.children(E, v, nid)
    rows = [node_row(E, v, k, now, window, enable, alerts) for k in kids]
    rows.sort(key=lambda r: (r["_worst"] is None, r["_worst"] if r["_worst"] is not None else 0, r["name"]))
    for r in rows:
        r.pop("_worst")
    own = perf_score(E, n, now, window, enable)
    own_now = perf_score(E, n, now, "1h", enable)
    out = {"object": node_out(E, v, nid), "window": window, "pillar": pillar, "run": run_line(now, window),
           "score": None if own is None else round(own, 1), "score_now": None if own_now is None else round(own_now, 1),
           "status": X.status_of(own if own_now is None or own is None else min(own, own_now)), "band": X.band(own),
           "outside_green": sum(1 for r in rows if r["status"] != "green"), "children_total": len(rows),
           "children": rows[:200], "children_truncated": max(0, len(rows) - 200),
           "trend": trend(E, n, now, window, enable),
           "content": pillar_content(E, v, nid, pillar, now, window, enable),
           "findings": findings_under(now, nid, enable, pillar, window),
           "slipped_alerts": slipped(now, enable, window) if pillar == "performance" else [],
           "stale": stale_for(E, nid, now, enable)}
    if n["kind"] == "vm":
        act = X.active_stories(enable)
        out["realms"] = {"vm": {"status": X.status_of(own), **vm_values(n, round(own, 1), act)},
                         "guest_os": {"status": X.status_of(guest_os_values(n, act)["guest_os_performance"]), **guest_os_values(n, act)}}
        if pillar == "performance":
            out["layers"] = vm_layers(n, now, window, act, own)
    if group and n["kind"] not in CONSUMER_KINDS:
        out["group_by"] = {"attribute": group, "rows": group_by(E, v, nid, group, now, window, enable)}
    if pillar == "performance" and P.applies(n):
        out["perf"] = P.view(now, v, nid, window, cls or P.DEFAULT_CLASS, at, enable)
    elif pillar == "performance" and n["kind"] != "vm":
        out["kpis"] = object_kpis(E, n, now, window, enable)
    if pillar == "capacity":
        out["capacity"] = capacity_tab(E, v, n, now, window, cls, at, enable)
        out["status"] = out["capacity"]["status"]
    return out


def capacity_tab(E, view: str, n: dict, now: datetime, window: str, cls, at, enable=()) -> dict:
    """The Capacity tab (D-094): on a cluster, or below it for its cluster with the host marked; above it, the group."""
    if P.applies(n):
        g = CAP.group_view(now, view, n["id"], window, cls or CAP.DEFAULT_CLASS, at, enable)
        fs = [f for f in findings_under(now, n["id"], enable, "capacity", window)]
        g["status"] = WORST([f["severity"] for f in fs] + (["red"] if any(r["contention_now"] for r in g["clusters_at"]) else []))
        return {"kind": "group", **g}
    cid = n["id"] if n["kind"] == "cluster" else n.get("cluster") or E.nodes.get(n.get("vm", ""), {}).get("cluster")
    if not cid or cid not in E.nodes:
        return {"kind": "none", "status": "green"}
    host = n["id"] if n["kind"] == "host" else n.get("host") if n["kind"] == "vm" else E.nodes.get(n.get("vm", ""), {}).get("host")
    return {"kind": "cluster", **CAP.cluster_view(now, cid, window, enable, host if n["kind"] != "cluster" else None),
            "remaining": CAP.capacity_remaining(n, now)}


def trend(E, n: dict, now: datetime, window: str, enable=()) -> list:
    """The node's own trend for the window, 12 points; for nodes above the cluster, the count of clusters outside green."""
    hours = X.WINDOW_HOURS[window]
    act = X.active_stories(enable)
    pts = []
    planted = {s["objects"]["cluster"]: s for s in act.values() if "cluster_performance" in s.get("plant", {}) and s.get("objects", {}).get("cluster")}
    for i in range(12, -1, -1):
        t = now - timedelta(hours=hours * i / 12)
        if n["kind"] == "cluster":
            v = noc.cluster_score({"id": n["id"], "base": n["base"]}, t, planted.get(n["id"]), now, 7)
            pts.append({"t": t.isoformat(), "v": v})
        elif n["kind"] in ("estate", "region", "location", "vcf_instance", "workload_domain", "class_of_service"):
            view = "class" if n["kind"] == "class_of_service" or (n["kind"] == "location" and n.get("class")) else "compute"
            cl = E.descendants(view, n["id"], "cluster") if n["id"] in E.parent[view] or n["id"] == "estate" else []
            cnt = sum(1 for c in cl if noc.cluster_score({"id": c["id"], "base": c["base"]}, t, planted.get(c["id"]), now, 7) < 75)
            pts.append({"t": t.isoformat(), "v": cnt, "unit": "clusters outside green"})
        else:
            s = perf_score(E, n, now, window, enable) or 0
            pts.append({"t": t.isoformat(), "v": round(min(100, s + (X._h(n["id"], i) - 0.3) * 3 * (i > 0)), 1)})
    return pts


# ---------------------------------------------------------------- the tree (l2.tree)

TREE_LEAF_KINDS = {"host", "datastore", "port_group", "vm"}


def tree(now: datetime, view: str, nid: str, activity: str, pillar: str, window: str, enable=()) -> dict | None:
    """A node, its path, and its children as the tree shows them: down to the cluster, sorted by activity."""
    from . import l2_cases, l2_improve
    E = X.estate(tuple(enable))
    if view not in X.VIEWS:
        raise ValueError("view must be one of " + ", ".join(X.VIEWS))
    n = X.node(E, nid)
    if n is None:
        return None
    kids = [k for k in X.children(E, view, nid) if k["kind"] not in ("resource_pool", "vm", "guest_os", "virtual_disk", "vnic")
            or (view == "management" and k["kind"] == "vm")]
    if view == "compute":  # the VCF instance is not a vCenter object: its workload domains (the vCenter Servers) sit under the location
        kids = [g for k in kids for g in (X.children(E, view, k["id"]) if k["kind"] == "vcf_instance" else [k])]
    open_cases = l2_cases.open_counts(now, enable)
    fs = findings(now, enable)
    stale = stale_locations(now, enable)
    ops = l2_improve.opportunities(now, enable) if activity == "improve" else []
    rows = []
    for k in kids:
        if activity == "improve":
            mine = [o for o in ops if o["object"] == k["id"] or (X.node(E, o["object"]) and k["id"] in ancestors(E, o["object"]))]
            status = "amber" if mine else "green"
            sort_key = -sum(o["size_n"] for o in mine)
        else:
            if pillar in ("summary", "performance"):
                s = perf_score(E, k, now, window, enable)
                s1 = perf_score(E, k, now, "1h", enable)
                s = None if s is None else min(s, s1 if s1 is not None else s)
                status = X.status_of(s)
            else:
                status = "green"
                s = None
            under_f = [f for f in fs if (k["id"] in f["under"] or f["object"] == k["id"]) and (pillar in ("summary", "performance") or f["pillar"] == pillar)
                       and (f["window"] == ("7d" if window == "7d" else "24h") or window not in ("1h", "24h", "7d"))]
            status = WORST([status] + [f["severity"] for f in under_f])
            sort_key = (-open_cases.get(k["id"], 0) if activity == "troubleshoot" else RANK.get(status, 3), s if s is not None else 100)
        if stale & (ancestors(E, k["id"]) | {k["id"]}):
            status = "no_data"
        rows.append({"id": k["id"], "kind": k["kind"], "name": k.get("appliance_name") and f"{k['name']}" or k["name"],
                     "status": status, "open_cases": open_cases.get(k["id"], 0),
                     "expandable": k["kind"] not in TREE_LEAF_KINDS and bool(X.children(E, view, k["id"])), "_sort": sort_key})
    rows.sort(key=lambda r: (r["_sort"], r["name"]))
    for r in rows:
        r.pop("_sort")
    return {"view": view, "views": [{"id": v, "name": X.VIEW_NAMES[v]} for v in X.VIEWS], "node": node_out(E, view, nid),
            "open_cases": open_cases.get(nid, 0), "children": rows}


def search(q: str, enable=()) -> list:
    E = X.estate(tuple(enable))
    q = (q or "").strip().lower()
    if len(q) < 2:
        return []
    out = []
    for n in E.nodes.values():
        if q in n["id"].lower() or q in str(n.get("name", "")).lower():
            v = X.view_of(E, n["id"])
            out.append({"id": n["id"], "kind": n["kind"], "name": n["name"], "view": v,
                        "path": [p.get("name") for p in X.path(E, v, n["id"])][1:-1]})
            if len(out) >= 20:
                break
    exact = [o for o in out if o["id"].lower() == q]
    return exact + [o for o in out if o not in exact]
