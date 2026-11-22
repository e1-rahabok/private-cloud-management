"""NOC data, incidents, SOPs and the action engine (prototype).

GENERATED from spec/catalog/noc.yaml, spec/catalog/sops/, spec/data/stories.yaml and
spec/workspaces/noc/. Do not edit by hand (D-070).

State (acknowledgements, actions, notes) is held in memory by the mock server. Real PCM keeps it
in its store (PCM core, 3.3) and writes every action to the action history (D-063).
"""
from __future__ import annotations

import random
import threading
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import agent_e2, api, catalog, generator, store

SPEC = Path(__file__).resolve().parents[2] / "spec"
SCREENS = ("up", "fast", "safe", "changed", "set_right", "capacity")
CHANGE_TYPES = ("created", "deleted", "powered_off", "moved", "resized")
CLASS_LETTER = {"gold": "G", "silver": "S", "bronze": "B", "mixed": "M"}
ROOT_CAUSES = ("noisy_neighbour", "hardware_fault", "configuration_change", "planned_work_not_in_calendar",
               "data_collection_failure", "other_explained")
ROUTES = {"cluster": "platform", "host": "platform", "vm": "platform", "datastore": "storage",
          "distributed_switch": "network", "nsx_edge": "network", "vcf_operations_instance": "platform",
          "location": "platform"}


def load_sops() -> dict:
    return {d["id"]: d for d in (yaml.safe_load(p.read_text()) for p in (SPEC / "catalog/sops").glob("*.yaml"))}


SOPS = load_sops()


# ---------------------------------------------------------------- state (action engine memory)

class State:
    """NOC workflow state, kept in the PCM database (store.py, D-080). The action record is its own table."""
    FIELDS = ("acks", "escalated", "closed", "notes", "provisioning_stopped", "limits")

    def __init__(self):
        self.lock = threading.RLock()
        self.load()

    def _defaults(self):
        self.acks, self.escalated, self.closed = {}, {}, {}
        self.notes, self.provisioning_stopped, self.limits = [], set(), {}

    def load(self):
        self._defaults()
        for k, v in store.load_state("noc").items():
            if k in self.FIELDS:
                setattr(self, k, set(v) if k == "provisioning_stopped" else v)
        self.history = store.records()

    def save(self):
        store.save_state("noc", {k: sorted(getattr(self, k)) if k == "provisioning_stopped" else getattr(self, k)
                                 for k in self.FIELDS})

    def reset(self):
        """Prototype and test reset only."""
        self._defaults()
        self.history = []
        store.clear_state("noc")
        store.clear_records()


STATE = State()


def record(action, target, actor_human, reason, before, after, now, actor_agent=None, expires_at=None, incident=None):
    """One action history entry with both identity fields (D-050, D-063)."""
    rec = {"at": now.isoformat(), "action": action, "target": target, "incident": incident,
           "actor_agent": actor_agent, "actor_human": actor_human, "reason": reason,
           "before": before, "after": after, "expires_at": expires_at.isoformat() if expires_at else None}
    store.append_record(rec)
    STATE.history.insert(0, rec)
    return rec


# ---------------------------------------------------------------- catalog functions

def wall_status_from_kpi(score: float) -> str:
    """noc.cluster_performance status on the wall: yellow is amber; orange and red are red."""
    band = catalog.kpi_band(score)
    return {"green": "green", "yellow": "amber"}.get(band, "red")


def changed_status(count: int, expected: float, settings: dict) -> str:
    """noc.changed_status."""
    if count > settings["noc.unexpected_change_factor"] * expected and count - expected >= settings["noc.unexpected_change_min"]:
        return "red"
    return "green"


def group_alerts(alerts: list, window_minutes: int) -> list:
    """noc.grouping_rule (D-069). Fixed rules: parent relationship and time window."""
    incidents = []
    for a in sorted(alerts, key=lambda x: x["raised"]):
        home = None
        for inc in incidents:
            first = inc["alerts"][0]["raised"]
            related = a.get("parent") == inc["root_object"] or a["object"] == inc["root_object"]
            if related and (a["raised"] - first) <= timedelta(minutes=window_minutes):
                home = inc
                break
        if home:
            home["alerts"].append(a)
            if a["severity"] == "red":
                home["severity"] = "red"
        else:
            incidents.append({"root_object": a["object"], "root_object_type": a["object_type"],
                              "severity": a["severity"], "alerts": [a], "kind": a.get("kind", "alert"),
                              "location": a.get("location"), "title": a["title"], "sop": a.get("sop")})
    return incidents


def shift_end(now: datetime, tz: str, shift_times: dict) -> datetime:
    """noc.limit_expiry: the end of the current shift in the region's local time."""
    local = now.astimezone(ZoneInfo(tz))
    starts = sorted(datetime.combine(local.date(), datetime.strptime(t, "%H:%M").time(), tzinfo=local.tzinfo)
                    for t in shift_times.values())
    for s in starts:
        if s > local:
            return s
    return starts[0] + timedelta(days=1)


# ---------------------------------------------------------------- data

def clusters(ds: dict, seed: int) -> list:
    est = generator.load_spec()["estate"]
    layout = est["cluster_layout"]["share_of_hosts"]
    out = []
    for lid, loc in ds["locations"].items():
        for cls in ("gold", "silver", "bronze", "mixed"):
            n = max(1, round(loc["hosts"] * layout[cls] / 12))
            for i in range(1, n + 1):
                cid = f"{lid.upper()}-{CLASS_LETTER[cls]}-{i:02d}"
                rng = random.Random(f"{seed}-{cid}")
                out.append({"id": cid, "location": lid, "class": cls, "base": rng.uniform(84, 98)})
    return out


def cluster_score(c: dict, t: datetime, story: dict | None, now: datetime, seed: int) -> float:
    from . import l2_story_m5
    if c["id"] == l2_story_m5.CLUSTER and l2_story_m5.enabled():  # story M-5: the cluster's own 24 hours
        return round(l2_story_m5.value_at("cluster_performance", t.timestamp(), now.timestamp()), 1)
    if story and c["id"] == story["objects"]["cluster"]:
        p = story["plant"]["cluster_performance"]
        start = generator.rel(p["before"]["until"], now)
        if t <= start:
            return float(p["before"]["value"])
        frac = (t - start) / (now - start)
        return round(p["before"]["value"] + (p["now"] - p["before"]["value"]) * frac, 1)
    minute = int(t.timestamp() // 60)
    return round(min(100.0, c["base"] + random.Random(f"{seed}-{c['id']}-{minute}").uniform(-2.5, 2.5)), 1)


def build(now: datetime, enable: tuple = (), seed: int = 7) -> dict:
    """Everything the NOC pages read, at this 'now'."""
    ds = generator.generate(now, seed=seed, enable=enable)
    spec = generator.load_spec()
    st, stories, est = ds["settings"], spec["stories"]["stories"], spec["estate"]
    active = {k: v for k, v in stories.items() if v.get("enabled_by_default", True) or k in enable
              or (v.get("same_as") in enable)}
    locs = ds["locations"]
    stale = {lid: l["stale"] for lid, l in locs.items()}
    n1 = active.get("N-1")

    # 1. What changed?
    changed = {}
    for lid in locs:
        rows = {}
        for t in CHANGE_TYPES:
            rng = random.Random(f"{seed}-{lid}-{t}-{now.hour}")
            expected = {"created": 6, "deleted": 2, "powered_off": 3, "moved": 40, "resized": 1}[t]
            count = max(0, round(expected + rng.uniform(-1.5, 1.5)))
            rows[t] = {"count": count, "expected": expected}
        changed[lid] = rows
    if "N-3" in active:
        n3 = active["N-3"]["plant"]
        changed["tk"]["deleted"] = {"count": n3["deleted_last_hour"], "expected": n3["expected_deleted"]}
    for lid, rows in changed.items():
        for t, r in rows.items():
            r["status"] = changed_status(r["count"], r["expected"], st)

    # 3. Is it fast?
    cl = clusters(ds, seed)
    # Any active story that plants a cluster's performance (N-1, T-2) drives that cluster, here and in L2.
    planted = {s["objects"]["cluster"]: s for s in active.values()
               if "cluster_performance" in s.get("plant", {}) and s.get("objects", {}).get("cluster")}
    for c in cl:
        story = planted.get(c["id"])
        c["score"] = cluster_score(c, now, story, now, seed)
        c["trend"] = [{"t": (now - timedelta(minutes=m)).isoformat(),
                       "v": cluster_score(c, now - timedelta(minutes=m), story, now, seed)} for m in range(60, -1, -5)]
        c["status"] = wall_status_from_kpi(c["score"])

    # 4. Is it safe? (same numbers as the CIO page: one definition)
    safe = {lid: {"ssh_or_shell_enabled": 0, "lockdown_off": 0, "certificates_expired": 0, "root_logins_open": 0}
            for lid in locs}
    if "N-4" in active:
        safe[active["N-4"]["objects"]["location"]]["ssh_or_shell_enabled"] = active["N-4"]["objects"]["hosts"]
    for lid, f in safe.items():
        f["status"] = "red" if f["certificates_expired"] else ("amber" if any(f.values()) else "green")

    # Alerts and incidents.
    alerts = []
    if n1:
        for a in n1["plant"]["alerts"]:
            alerts.append({**a, "raised": generator.rel(a["raised"], now), "location": "fr",
                           "sop": "sop-cluster-contention" if a["object_type"] == "cluster" else None})
    if "T-2" in active:
        for a in active["T-2"]["plant"]["alerts"]:
            alerts.append({**a, "raised": generator.rel(a["raised"], now), "location": "tk", "sop": "sop-cluster-contention"})
    if "O-1" in active:
        for a in active["O-1"]["plant"]["alerts"]:
            alerts.append({**a, "raised": generator.rel(a["raised"], now), "location": "ld", "sop": "sop-datastore-space"})
    incidents = group_alerts(alerts, st["noc.grouping_window_minutes"])
    # Wall findings (D-075).
    for lid, rows in changed.items():
        if any(r["status"] == "red" for r in rows.values()) and not stale[lid]:
            incidents.append({"root_object": lid, "root_object_type": "location", "severity": "red",
                              "kind": "wall_finding", "screen": "changed", "location": lid,
                              "title": f"Unexpected VM changes in {locs[lid]['name']}",
                              "sop": "sop-unexpected-change",
                              "alerts": [{"object": lid, "object_type": "location", "severity": "red",
                                          "title": "Unexpected VM changes",
                                          "raised": generator.rel(active["N-3"]["plant"]["deleted_within"], now) if "N-3" in active else now}]})
    for region, is_stale in ds["region_stale"].items():
        if is_stale:
            inst = est["regions"][region]["vcf_operations_instance"]
            incidents.append({"root_object": inst, "root_object_type": "vcf_operations_instance", "severity": "red",
                              "kind": "alert", "location": None, "title": "No data from VCF Operations",
                              "sop": "sop-no-data",
                              "alerts": [{"object": inst, "object_type": "vcf_operations_instance", "severity": "red",
                                          "title": "No data from VCF Operations", "raised": now - timedelta(minutes=10)}]})
    for inc in incidents:
        inc["id"] = "inc-" + inc["root_object"].lower()
        inc["escalation_route"] = ROUTES[inc["root_object_type"]]
        inc["sop"] = inc["sop"] or "sop-cluster-contention"
        inc["opened_at"] = min(a["raised"] for a in inc["alerts"])
        if not inc.get("screen"):
            inc["screen"] = {"cluster": "fast", "vm": "fast", "host": "up", "datastore": "up",
                             "vcf_operations_instance": "up"}.get(inc["root_object_type"], "up")
        # A stale location hides its incidents: the wall shows only what it knows (N-2 note).
        if inc.get("location") and stale.get(inc["location"]):
            inc["hidden_by_stale"] = True
        planted_esc = any(s.get("plant", {}).get("escalated") and s["objects"].get("cluster") == inc["root_object"]
                          for s in active.values())
        inc["state"] = ("closed" if inc["id"] in STATE.closed else "escalated" if inc["id"] in STATE.escalated or planted_esc
                        else "acknowledged" if inc["id"] in STATE.acks else "new")
        inc["acknowledged_by"] = STATE.acks.get(inc["id"])

    # Scale and capacity per location (noc.running_counts, noc.capacity_status).
    vm_cfg, layout = est["vms"], est["cluster_layout"]["share_of_hosts"]
    scale, capacity = {}, {}
    for lid, loc in locs.items():
        vms = sum(round(loc["hosts"] * layout[c] * vm_cfg["per_host_average"][c]) for c in ("gold", "silver", "bronze", "mixed"))
        scale[lid] = {"vms_running": vms, "hosts_running": loc["hosts"]}
        groups = [g for g in ds["capacity"]["groups"] if g["location"] == lid]
        days = [g["resources"][g["tightest"]]["run_out_days"] for g in groups]
        known = [d for d in days if d is not None]
        capacity[lid] = {"in_use": dict(loc["in_use"]),
                         "days_remaining": min(known) if known else None,
                         "status": "red" if any(g["quadrant"] == "red" for g in groups) else "green"}
    return {"ds": ds, "now": now, "settings": st, "locations": locs, "stale": stale, "changed": changed,
            "scale": scale, "capacity": capacity, "clusters": cl, "safe": safe, "incidents": incidents, "n1": n1,
            "risk_certificates": ds["health"]["safe"]["risk_certificates"]}


# ---------------------------------------------------------------- API shapes

def _tile(nd, lid, status, **extra):
    loc = nd["locations"][lid]
    if nd["stale"][lid]:
        return {"location": lid, "name": loc["name"], "status": "no_data", "last_good": loc["as_of"].isoformat()}
    return {"location": lid, "name": loc["name"], "status": status, **extra}


def worst(statuses):
    order = ["red", "amber", "green"]
    live = [s for s in statuses if s != "no_data"]
    if not live:
        return "no_data"
    return min(live, key=order.index)


def performance_trend(nd: dict) -> dict:
    """noc.performance_trend: per 5-minute point of the last hour, the average and the lowest cluster score.
    Clusters of a location with no data are left out and counted."""
    clusters = nd["clusters"]
    live = [c for c in clusters if not nd["stale"][c["location"]]]
    pts = []
    if live:
        for i in range(len(live[0]["trend"])):
            vals = [(c["trend"][i]["v"], c["id"]) for c in live]
            low = min(vals)
            pts.append({"t": live[0]["trend"][i]["t"], "average": round(sum(v for v, _ in vals) / len(vals), 1),
                        "lowest": low[0], "lowest_cluster": low[1]})
    return {"points": pts, "clusters_counted": len(live), "clusters_left_out": len(clusters) - len(live)}


def wall(nd: dict) -> dict:
    open_inc = [i for i in nd["incidents"] if i["state"] != "closed" and not i.get("hidden_by_stale")]
    screens = {
        "changed": {"tiles": [_tile(nd, lid, worst([r["status"] for r in rows.values()]), rows=rows)
                              for lid, rows in nd["changed"].items()]},
        "up": {"tiles": [_tile(nd, lid, "green", total=0,
                               items={"vms_down_unplanned": 0, "hosts_not_responding": 0, "clusters_lost_ha": 0,
                                      "management_down": 0, "datastores_unreachable": 0})
                         for lid in nd["locations"]]},
        "fast": {"tiles": [_tile(nd, c["location"], c["status"], cluster=c["id"], score=c["score"], trend=c["trend"])
                           for c in nd["clusters"]]},
        "safe": {"tiles": [_tile(nd, lid, f["status"], findings={k: v for k, v in f.items() if k != "status"})
                           for lid, f in nd["safe"].items()],
                 "risk_certificates": nd["risk_certificates"]},
        "set_right": {"tiles": [_tile(nd, lid, "green", count=0) for lid in nd["locations"]]},
        "capacity": {"tiles": [_tile(nd, lid, c["status"], in_use=c["in_use"], days_remaining=c["days_remaining"])
                               for lid, c in nd["capacity"].items()]},
    }
    screens["fast"]["trend"] = performance_trend(nd)
    est = generator.load_spec()["estate"]
    screens["up"]["no_data_sources"] = [
        {"region": est["regions"][r]["name"],
         "last_good": min(l["as_of"] for l in nd["locations"].values() if l["region"] == r).isoformat()}
        for r, st_ in nd["ds"]["region_stale"].items() if st_]
    # A stale VCF Operations instance shows on "Is it up?" as red until acknowledged (sop-no-data).
    strip, pins = [], []
    for name in SCREENS:
        status = worst([t["status"] for t in screens[name]["tiles"]])
        open_inc_on = [i for i in open_inc if i["screen"] == name]
        reds = [i for i in open_inc_on if i["severity"] == "red"]
        if reds and status != "no_data":
            status = "red"
        if reds and all(t["status"] == "no_data" for t in screens[name]["tiles"]):
            status = "red"
        unacked = [i for i in reds if i["state"] == "new"]
        in_hand = status == "red" and bool(reds) and not unacked
        if unacked:
            pins.append(name)
        strip.append({"screen": name, "status": status, "in_hand": in_hand, "open_incidents": len(open_inc_on)})
        screens[name]["status"] = status
    live = [lid for lid in nd["locations"] if not nd["stale"][lid]]
    scale = {"vms_running": sum(nd["scale"][l]["vms_running"] for l in live) if live else None,
             "hosts_running": sum(nd["scale"][l]["hosts_running"] for l in live) if live else None,
             "locations_without_data": [nd["locations"][l]["name"] for l in nd["locations"] if nd["stale"][l]]}
    return {"updated_at": nd["now"].isoformat(), "pcm_ok": True, "strip": strip, "scale": scale,
            "rotation_seconds": nd["settings"]["noc.rotation_seconds"],
            "refresh_seconds": nd["settings"]["noc.refresh_seconds"],
            "pin": pins[0] if pins else None, "pins": pins, "screens": screens,
            "stale_locations": [l for l, s in nd["stale"].items() if s]}


def incident_list(nd: dict) -> list:
    rows = [i for i in nd["incidents"] if i["state"] != "closed" and not i.get("hidden_by_stale")]
    rows.sort(key=lambda i: (0 if i["severity"] == "red" else 1, i["opened_at"]))
    return [summary_of(i, nd) for i in rows]


def summary_of(i, nd):
    return {"id": i["id"], "root_object": i["root_object"], "root_object_type": i["root_object_type"],
            "kind": i["kind"], "severity": i["severity"], "title": i["title"],
            "location": i.get("location"), "location_name": nd["locations"][i["location"]]["name"] if i.get("location") else None,
            "alert_count": len(i["alerts"]), "opened_at": i["opened_at"].isoformat(),
            "state": i["state"], "acknowledged_by": i["acknowledged_by"], "escalation_route": i["escalation_route"]}


def villain_of(nd):
    n1 = nd["n1"]
    if not n1:
        return None
    v = n1["objects"]["villain"]
    return {"vm": v["vm"], "class": v["class"], "environment": v["environment"], "score": n1["plant"]["villain_score"]}


def cluster_detail(nd: dict, cid: str) -> dict | None:
    c = next((x for x in nd["clusters"] if x["id"] == cid), None)
    if not c:
        return None
    out = {"cluster": cid, "location": c["location"], "class": c["class"], "score": c["score"],
           "status": c["status"], "trend": c["trend"], "villains": [], "victims": []}
    n1 = nd["n1"]
    if n1 and cid == n1["objects"]["cluster"]:
        v = villain_of(nd)
        out["villains"] = [{"vm": v["vm"], "class": v["class"], "environment": v["environment"],
                            "usage_score": v["score"], "note": "Using the most computing power in the cluster"}]
        out["victims"] = [{"vm": vm, "class": "silver", "environment": "production", "score": s}
                          for vm, s in zip(n1["objects"]["victims"], n1["plant"]["victim_scores"])]
    return out


def limit_check(nd: dict, target: str) -> tuple[bool, str]:
    """Is a time-boxed limit allowed on this VM for L1? (D-040)"""
    v = villain_of(nd)
    if v and target == v["vm"] and v["environment"] == "production":
        return False, "Production VM: escalate instead"
    return True, ""


def incident_detail(nd: dict, iid: str) -> dict | None:
    i = next((x for x in nd["incidents"] if x["id"] == iid), None)
    if not i:
        return None
    sop = SOPS[i["sop"]]
    v = villain_of(nd) if i["sop"] == "sop-cluster-contention" else None
    c = next((x for x in nd["clusters"] if x["id"] == i["root_object"]), None)
    steps = []
    for s in sop["steps"]:
        step = {"kind": s["kind"], "text": s["text"]}
        if s["kind"] in ("diagnosis", "verify") and c and s.get("check") == "noc.cluster_performance":
            ok = c["score"] < 50 if s["kind"] == "diagnosis" else c["score"] >= 75
            step.update(result=f"Cluster score now {round(c['score'])} out of 100", passed=ok)
        elif s["kind"] == "diagnosis" and s.get("check") == "noc.villains" and v:
            step.update(result=f"Top villain: {v['vm']} ({v['class'].capitalize()} VM in a Silver cluster)", passed=True)
        elif s["kind"] == "diagnosis" and s.get("check") == "vm.environment" and v:
            step.update(result=f"{v['vm']} is {v['environment'].replace('_', '-')}", passed=None if s.get("branch") else v["environment"] != "production")
        elif s["kind"] == "diagnosis" and s.get("check") == "meta.stale":
            step.update(result="Last good data more than two collection cycles ago", passed=True)
        elif s["kind"] == "diagnosis" and s.get("check") == "business_calendar.planned_now":
            step.update(result="No planned work in the business calendar now", passed=True)
        if s["kind"] == "action":
            act = s["action"]
            target = v["vm"] if act == "time_boxed_limit" and v else i["root_object"]
            allowed, why = (limit_check(nd, target) if act == "time_boxed_limit" else (True, ""))
            if act == "stop_provisioning" and i["root_object"] in STATE.provisioning_stopped:
                allowed, why = False, "Already stopped"
            step.update(action=act, target=target, allowed=allowed, refusal=why)
        if s["kind"] == "escalate":
            applies = not s.get("when") or (v and v["environment"] == "production") or not v
            step.update(route=i["escalation_route"], applies=bool(applies))
        steps.append(step)
    hist = [h for h in STATE.history if h["incident"] == iid]
    return {**summary_of(i, nd), "alerts": [{"object": a["object"], "title": a["title"], "severity": a["severity"],
                                              "raised": a["raised"].isoformat()} for a in i["alerts"]],
            "sop": {"id": sop["id"], "title": sop["title"], "version": sop["version"], "steps": steps},
            "history": hist, "root_causes": list(ROOT_CAUSES),
            "agent_draft": ("Draft by Agent E2, to review: cluster " + i["root_object"] + " is not serving its VMs well. "
                            + (f"The top villain {v['vm']} is a production Bronze VM placed in a Silver cluster. " if v else "")
                            + "Steps run and results are attached. Escalating to " + i["escalation_route"].capitalize() + ".")}


def shift_view(nd: dict) -> dict:
    st = nd["settings"]
    tz = "Asia/Singapore"
    end = shift_end(nd["now"], tz, st["noc.shift_times"])
    rows = [summary_of(i, nd) for i in nd["incidents"] if not i.get("hidden_by_stale")]
    return {"region": "apj", "time_zone": tz, "shift_ends": end.isoformat(),
            "open": [r for r in rows if r["state"] == "new"],
            "acknowledged": [r for r in rows if r["state"] == "acknowledged"],
            "waiting_on_l2": [r for r in rows if r["state"] == "escalated"],
            "limits_expiring": [{"target": t, **l} for t, l in STATE.limits.items()],
            "notes": STATE.notes}


# ---------------------------------------------------------------- actions (action engine, PCM core 3.7)

def act(nd: dict, path: list, body: dict) -> tuple[int, dict]:
    """Every action is saved to the PCM database before the answer goes back."""
    with STATE.lock:
        out = _act(nd, path, body)
        STATE.save()
    return out


def _act(nd: dict, path: list, body: dict) -> tuple[int, dict]:
    now, st = nd["now"], nd["settings"]
    human = body.get("actor_human") or st["noc.actor_default"]
    agent = body.get("actor_agent")
    with STATE.lock:
        if path[0] == "incidents" and len(path) == 3:
            iid, verb = path[1], path[2]
            inc = next((x for x in nd["incidents"] if x["id"] == iid), None)
            if not inc:
                return 404, {"error": "no such incident"}
            if verb == "agent":
                task = body.get("task", "explain")
                if task not in agent_e2.TASKS:
                    return 400, {"error": "task must be explain or escalation_note"}
                vocab = yaml.safe_load((SPEC / "catalog/vocabulary/noc.yaml").read_text())
                detail = incident_detail(nd, iid)
                out = agent_e2.draft(detail, task, st, vocab["avoided"])
                rec = record("agent_draft", iid, human, task, "-", out["source"], now, actor_agent="agent-e2", incident=iid)
                return 200, {**out, "record": rec}
            if verb == "acknowledge":
                STATE.acks[iid] = human
                record("acknowledge", iid, human, body.get("note", ""), inc["state"], "acknowledged", now, agent, incident=iid)
                return 200, {"state": "acknowledged"}
            if verb == "escalate":
                STATE.escalated[iid] = inc["escalation_route"]
                STATE.acks.setdefault(iid, human)
                record("escalate", iid, human, f"to {inc['escalation_route']} with evidence", inc["state"], "escalated", now, agent, incident=iid)
                return 200, {"state": "escalated", "to": inc["escalation_route"]}
            if verb == "close":
                cause = body.get("root_cause")
                if cause not in ROOT_CAUSES:
                    return 400, {"error": "A root cause from the list is required to close."}
                STATE.closed[iid] = cause
                record("close", iid, human, cause, inc["state"], "closed", now, agent, incident=iid)
                return 200, {"state": "closed"}
        if path[0] == "actions" and len(path) == 2:
            action, target, iid = path[1], body.get("target"), body.get("incident")
            if action == "time_boxed_limit":
                ok, why = limit_check(nd, target)
                if not ok:
                    return 403, {"error": why}
                exp = shift_end(now, "Asia/Singapore", st["noc.shift_times"])
                STATE.limits[target] = {"expires_at": exp.isoformat(), "set_by": human}
                record(action, target, human, body.get("note", "SOP step"), "no limit", "limit until end of shift", now, agent, exp, iid)
                return 200, {"expires_at": exp.isoformat()}
            if action in ("stop_provisioning", "reopen_provisioning"):
                stopped = action == "stop_provisioning"
                before = "closed to new VMs" if target in STATE.provisioning_stopped else "open to new VMs"
                (STATE.provisioning_stopped.add if stopped else STATE.provisioning_stopped.discard)(target)
                record(action, target, human, body.get("note", "SOP step"), before,
                       "closed to new VMs" if stopped else "open to new VMs", now, agent, incident=iid)
                return 200, {"target": target, "provisioning": "stopped" if stopped else "open"}
            if action == "restart_vm":
                return 403, {"error": "Restart is allowed only for a non-production VM whose VMware Tools heartbeat is lost."}
        if path == ["shift"]:
            STATE.notes.insert(0, {"at": now.isoformat(), "by": human, "note": body.get("note", "")})
            return 200, {"saved": True}
    return 404, {"error": "unknown action"}
