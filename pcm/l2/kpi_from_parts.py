"""PCM scenario story M-5: one Silver cluster, one host and one VM with a 24-hour PCM scenario story that the scores can be rebuilt from.

SG-S-01 (12 hosts, 344 VMs), its host sg-esx-110 (28 VMs) and the VM sg-api-1617 (8 vCPU). Three objects, each with
its own component rows; the KPI of each is computed from its rows with the vCommunity scoring (kpi_score.py of the
vCommunity pack: five limits per row, weight 2^((100 - score) / 25), weighted average, rows marked "skip when green"
left out while green). The objects share only the PCM scenario story clock and one pressure curve, so each can be read alone.

The PCM scenario story is relative to "now": the window opens 24 hours before it and holds 288 points of 5 minutes, the last at
"now". Spec: pcm/core/spec/demo-data/scenario-stories.yaml, PCM scenario story M-5. Before the PCM scenario story and for a window longer than 24 hours, the objects are
calm. A point holds the worst value inside it (D-091), so a longer window reads the worst of the PCM scenario story's points.
"""
from __future__ import annotations

import math
import random
from functools import lru_cache
from typing import NamedTuple

CLUSTER, HOST, VM = "SG-S-01", "sg-esx-110", "sg-api-1617"
N = 288
POINT_SECONDS = 300


# ---------------------------------------------------------------- the vCommunity scoring

class Row(NamedTuple):
    name: str
    best: float
    green: float
    yellow: float
    orange: float
    zero_at: float
    skip: bool = False


def _score(r: Row, v: float) -> float:
    if v <= r.best:
        return 100.0
    start = r.best
    for (_, s0), end in zip((("g", 100.0), ("y", 75.0), ("o", 50.0), ("r", 25.0)), (r.green, r.yellow, r.orange, r.zero_at)):
        if end == start:
            continue
        if v < end or s0 == 25.0:
            return s0 - min((v - start) / (end - start), 1.0) * 25.0
        start = end
    return 0.0


def kpi(rows: list, values: dict) -> float:
    num = den = 0.0
    any_data = False
    for r in rows:
        v = values.get(r.name)
        if v is None:
            continue
        v = round(v, 2)
        any_data = True
        if r.skip and v < r.green or (r.skip and v <= r.best):
            continue
        s = _score(r, v)
        w = 2 ** ((100.0 - s) / 25.0)
        num, den = num + s * w, den + w
    return 100.0 if not den and any_data else round(num / den, 2)


# Rows, named by the keys of the monitor's parts (monitor.PERFORMANCE_PARTS, HOST_PARTS, RISK_PARTS).
# best, green, yellow, orange, zero-at, skip when green.
PERF_ROWS = [Row("worst_vcpu_ready", 0, 4, 8, 16, 32), Row("worst_vcpu_costop", 0, 2, 4, 8, 16),
        Row("worst_memory_wait", 0, 1, 2, 4, 8), Row("worst_disk_latency", 0, 40, 80, 160, 320),
        Row("p90_vcpu_ready", 0, 1, 2, 4, 8), Row("p90_vcpu_costop", 0, .5, 1, 2, 4),
        Row("p90_memory_wait", 0, .5, 1, 2, 4), Row("p90_disk_latency", 0, 20, 40, 60, 80),
        Row("highest_esxi_packets", 0, 0, .2, .4, .8, True)]
HOST_ROWS = [Row(r.name.replace("memory_wait", "memory_latency").replace("highest_esxi_packets", "esxi_packets"), *r[1:]) for r in PERF_ROWS]
VMROWS = [Row("co_stop", 0, 1, 2, 4, 8), Row("cpu_ready", 0, 2, 4, 8, 16), Row("cpu_overlap", 0, .5, 1, 2, 4, True),
          Row("memory_wait", 0, .5, 1, 2, 4), Row("disk_latency", 0, 10, 20, 40, 80), Row("dropped_tx", 0, 0, .5, 1, 2, True),
          Row("cpu_run", 0, 95, 97, 99, 100, True), Row("ballooned", 0, 2, 4, 8, 16), Row("zip_swap", 0, .25, .5, 1, 2)]
RISK_ROWS = [Row("highest_esxi_cpu_thread_utilization", 0, 60, 80, 90, 95, True), Row("worst_esxi_cpu_imbalance", 1, 1, 1.3, 1.6, 2),
        Row("worst_esxi_memory_ballooned", 0, 1, 2, 4, 8),
        Row("worst_esxi_swapped_zipped_memory", 0, .25, .5, 1, 2), Row("highest_esxi_cpu_reservation", 0, 10, 40, 60, 80, True),
        Row("highest_esxi_memory_reservation", 0, 10, 40, 60, 80, True), Row("highest_esxi_cpu_overcommit", 0, 1, 2, 3, 4, True),
        Row("highest_esxi_memory_overcommit", 0, 1, 1.4, 1.8, 2.2, True), Row("highest_cpu_monster_vm_host_ratio", 0, 1, 2, 3, 4),
        Row("highest_memory_monster_vm_host_ratio", 0, 1, 2, 3, 4)]


# ---------------------------------------------------------------- the PCM scenario story

# Hours before now -> pressure on sg-esx-110 (0 calm, 1 worst). The window opens at 24: calm. At 17.5 the release lands
# (6 VMs power on, with reservations, DRS places them on the host); the load builds through the evening; the end-of-day
# batch adds to it; the worst is at 4: DRS moves 3 VMs off, so there is partial relief.
_T = [0, 5, 7, 9, 12, 15, 18, 20, 21, 22, 24]
_S = [0, 0.04, 0.17, 0.31, 0.47, 0.62, 0.80, 0.95, 1.0, 0.97, 0.90]
RELEASE_HOURS = 6.5  # after the window opens


def _interp(x: float) -> float:
    for k in range(len(_T) - 1):
        if _T[k] <= x <= _T[k + 1]:
            f = (x - _T[k]) / (_T[k + 1] - _T[k])
            f = f * f * (3 - 2 * f)
            return _S[k] + f * (_S[k + 1] - _S[k])
    return _S[-1]


def _hours(i: int) -> float:
    return (i + 1) * 5 / 60


def _pressure() -> tuple:
    rng, drift, s = random.Random(110), 0.0, []
    for i in range(N):
        drift = 0.9 * drift + rng.gauss(0, 0.012)
        s.append(max(0.0, _interp(_hours(i)) + drift))
    m, mem = 0.0, []  # memory is reclaimed slowly: it builds in about 4 hours and eases in about 14
    for v in s:
        m += (v - m) * (5 / 60) / (4.0 if v > m else 14.0)
        mem.append(m)
    top = max(mem)
    return s, [x / top * 0.95 for x in mem]


def _vm_rows(s, m) -> list:
    rng, out = random.Random(1617), []
    for si, mi in zip(s, m):
        spike = 1 + (rng.random() ** 8) * 0.55  # rare higher peaks inside a 5-minute point
        n = lambda a=0.12: 1 + rng.gauss(0, a)
        out.append({"co_stop": max(0, (0.15 + 5.2 * si ** 2.0) * n() * spike),
                    "cpu_ready": max(0, (0.9 + 10.0 * si ** 1.5) * n() * spike),
                    "cpu_overlap": max(0, (0.12 + 0.55 * si) * n()),
                    "memory_wait": max(0, (0.03 + 3.2 * mi ** 2.4) * n(0.15)),
                    "disk_latency": max(0, (3.6 + 34 * si ** 1.5) * n() * spike),
                    "dropped_tx": max(0, 0.0 if si < 0.8 else (si - 0.8) * 1.6 * n(0.3)),
                    "cpu_run": min(99.5, (38 + 40 * si) * n(0.04)),
                    "ballooned": max(0, 6.5 * mi ** 1.6 * n(0.1)),
                    "zip_swap": max(0, 0.0 if mi < 0.4 else (mi - 0.4) * 1.1 * n(0.12))})
    return out


def _host_rows(vm, s) -> list:
    rng, out = random.Random(111), []
    for v, si in zip(vm, s):  # the other 27 VMs are hit too, less: the host's 90th percentile follows the pressure
        pk = 0.0 if si < 0.62 else (si - 0.62) * 0.95 * (1 + rng.gauss(0, .15))
        out.append({"worst_vcpu_ready": v["cpu_ready"], "worst_vcpu_costop": v["co_stop"],
                    "worst_memory_latency": v["memory_wait"], "worst_disk_latency": v["disk_latency"],
                    "p90_vcpu_ready": 0.7 + 0.34 * (v["cpu_ready"] - 0.9) + 0.25,
                    "p90_vcpu_costop": 0.15 + 0.30 * (v["co_stop"] - 0.15),
                    "p90_memory_latency": 0.02 + 0.33 * (v["memory_wait"] - 0.03),
                    "p90_disk_latency": 6 + 0.45 * (v["disk_latency"] - 3.6),
                    "esxi_packets": max(0, pk)})
    return out


def _cluster_rows(host) -> list:
    rng, out = random.Random(1), []
    for i, h in enumerate(host):
        bg = lambda base, a=0.15: base * (1 + rng.gauss(0, a))
        day = 1.0 + 0.25 * math.sin((i / 288 * 2 * math.pi) - 1.2) ** 2  # the business day shows in the background
        out.append({
            "worst_vcpu_ready": max(h["worst_vcpu_ready"], bg(2.2 * day)),
            "worst_vcpu_costop": max(h["worst_vcpu_costop"], bg(.35 * day)),
            "worst_memory_wait": max(h["worst_memory_latency"], bg(.05)),
            "worst_disk_latency": max(h["worst_disk_latency"], bg(14 * day)),
            # 28 of 344 VMs sit on the host: just under the 10% that sets the 90th percentile, so it rises a little
            "p90_vcpu_ready": bg(.55 * day) + 0.28 * (h["p90_vcpu_ready"] - .6),
            "p90_vcpu_costop": bg(.08 * day) + 0.28 * (h["p90_vcpu_costop"] - .1),
            "p90_memory_wait": bg(.01) + 0.28 * (h["p90_memory_latency"] - .02),
            "p90_disk_latency": bg(5 * day) + 0.28 * (h["p90_disk_latency"] - 6),
            "highest_esxi_packets": h["esxi_packets"]})
    return out


def _risk_rows(s, m) -> list:
    rng, out = random.Random(2), []
    for i, (si, mi) in enumerate(zip(s, m)):
        t = _hours(i)
        ramp = min(1.0, max(0.0, (t - RELEASE_HOURS) / 1.5))  # the release: 6 VMs with reservations power on
        after = 1 if t >= RELEASE_HOURS else 0
        n = lambda a=0.02: 1 + rng.gauss(0, a)
        util = 44 + 6 * math.sin((i / 288 * 2 * math.pi) - 1.2) ** 2 + 36 * (0.5 * mi + 0.5 * si) ** 1.1
        out.append({"highest_esxi_cpu_thread_utilization": min(99, util * n()),
                    "worst_esxi_cpu_imbalance": 1.02 + 0.40 * mi ** 1.2 * n(0.03),
                    "worst_esxi_memory_ballooned": max(0, 6.0 * mi ** 1.5 * n(0.08)),
                    "worst_esxi_swapped_zipped_memory": max(0, 0 if mi < 0.35 else (mi - 0.35) * 1.5 * n(0.1)),
                    "highest_esxi_cpu_reservation": 8 + 20 * ramp, "highest_esxi_memory_reservation": 9 + 38 * ramp,
                    "highest_esxi_cpu_overcommit": 0.95 + 1.15 * ramp, "highest_esxi_memory_overcommit": 0.9 + 0.5 * ramp * n(0.005),
                    "highest_cpu_monster_vm_host_ratio": 0.12 + 0.02 * after, "highest_memory_monster_vm_host_ratio": 0.30 + 0.05 * after})
    return out


# Decimals each row is shown with. Rows are rounded to them before scoring, so the KPI is exactly the score of the parts
# as the page shows them (the adapter does the same: it rounds a value to two decimals, then scores it).
DECIMALS = {"highest_esxi_packets": 2, "esxi_packets": 2, "worst_esxi_cpu_imbalance": 2, "worst_esxi_memory_ballooned": 2,
            "worst_esxi_swapped_zipped_memory": 2, "highest_esxi_memory_overcommit": 2, "dropped_tx": 2, "zip_swap": 2}


def _shown(rows: list) -> list:
    return [{k: round(v, DECIMALS.get(k, 1)) for k, v in r.items()} for r in rows]


@lru_cache(maxsize=1)
def scenario_story() -> dict:
    """The 288 points of every row and every KPI, oldest first. Computed once; relative to now."""
    s, m = _pressure()
    vm = _shown(_vm_rows(s, m))
    host_r = _shown(_host_rows(vm, s))
    cl, rk = _shown(_cluster_rows(host_r)), _shown(_risk_rows(s, m))
    return {"vm_rows": vm, "host_rows": host_r, "cluster_rows": cl, "risk_rows": rk,
            "vm_performance": [kpi(VMROWS, r) for r in vm], "esxi_performance": [kpi(HOST_ROWS, r) for r in host_r],
            "cluster_performance": [kpi(PERF_ROWS, r) for r in cl], "cluster_risk": [round(100 - kpi(RISK_ROWS, r), 2) for r in rk]}


# ---------------------------------------------------------------- reading the PCM scenario story in any window

def slot_values(series: list, now_ts: float, start: float, L: float, n: int, better: str, calm: float | None = None) -> list:
    """The window's points: each holds the worst of the PCM scenario story's 5-minute points inside it (D-091). Before the PCM scenario story:
    calm, the median of its first four hours."""
    if calm is None:
        head = sorted(series[:48])
        calm = head[len(head) // 2]
    out = []
    for i in range(n):
        lo, hi = start + i * L, start + (i + 1) * L
        vals = [series[j] for j in range(N) if lo < now_ts - (N - 1 - j) * POINT_SECONDS <= hi]
        out.append((max(vals) if better == "lower" else min(vals)) if vals else calm)
    return out


def is_scenario_story_object(kind: str, nid: str) -> bool:
    return (kind, nid) in (("cluster", CLUSTER), ("host", HOST), ("vm", VM))


def window_score(series: list, hours: int, now_ts: float, start: float, L: float, n: int) -> float:
    """l2.node_score over the window: the value met or beaten 95% of the time (the 5th percentile of the points)."""
    pts = sorted(slot_values(series, now_ts, start, L, n, "higher"))
    return float(pts[int(0.05 * len(pts))])


def enabled() -> bool:
    from ..core import generator
    s = generator.load_spec()["scenario_stories"]["scenario_stories"].get("M-5")
    return bool(s) and s.get("enabled_by_default", True)


def value_at(key: str, at_ts: float, now_ts: float) -> float:
    """The KPI at one moment (the NOC reads the cluster minute by minute): the nearest 5-minute point; calm before."""
    series = scenario_story()[key]
    j = N - 1 - round((now_ts - at_ts) / POINT_SECONDS)
    if j < 0:
        head = sorted(series[:48])
        return head[len(head) // 2]
    return series[min(j, N - 1)]


# The metric keys the monitor shows -> the PCM scenario story's row keys.
VM_LAYER_KEYS = {"cpu_ready_percent": "cpu_ready", "co_stop_percent": "co_stop", "memory_wait_percent": "memory_wait",
                 "disk_latency_ms": "disk_latency"}
# Rows of VM Performance that the VM tab does not show by default: (key, label, unit, decimals, band ends, PCM scenario story row).
VM_EXTRA_ROWS = (("cpu_overlap_percent", "CPU Overlap", "%", 1, [0.5, 1, 2], "cpu_overlap"),
                 ("network_dropped_tx_percent", "Network Dropped Tx", "%", 2, [0, 0.5, 1], "dropped_tx"),
                 ("cpu_run_percent", "CPU Run", "%", 1, [95, 97, 99], "cpu_run"),
                 ("memory_ballooned_percent", "Memory Ballooned", "%", 1, [2, 4, 8], "ballooned"),
                 ("memory_zip_swap_percent", "Memory Zip Swap", "%", 2, [0.25, 0.5, 1], "zip_swap"))


def part_series(rows_key: str, now_ts: float, start: float, L: float, n: int) -> dict:
    """Every row of an object over the window, one list per row, worst inside each point (lower is better)."""
    rows = scenario_story()[rows_key]
    return {k: slot_values([r[k] for r in rows], now_ts, start, L, n, "lower") for k in rows[0]}
