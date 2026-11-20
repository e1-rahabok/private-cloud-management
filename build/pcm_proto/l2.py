"""L2 workspace data, the daily check, proposals, the trust ladder, escalations, configuration,
calendar and threshold replay (prototype).

GENERATED from spec/catalog/l2.yaml, spec/data/stories.yaml and spec/workspaces/l2/.
Do not edit by hand (D-070). State is in memory, like the NOC (noc.STATE).
"""
from __future__ import annotations

import random
import threading
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import agent_e2, generator, noc

SPEC = Path(__file__).resolve().parents[2] / "spec"


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        self.proposals, self.closures, self.calendar_added = {}, {}, []
        self.tiers, self.extra_approvals, self.promoted_by = {}, {}, {}
        self.standards, self.thresholds = {}, {}


STATE = State()


def stories(enable=()):
    s = generator.load_spec()["stories"]["stories"]
    return {k: v for k, v in s.items() if v.get("enabled_by_default", True) or k in enable}


# ---------------------------------------------------------------- catalog functions

def verdicts(findings: list) -> dict:
    """l2.daily_check: three verdicts, never one score."""
    out = {}
    for v in ("present_health", "risk", "efficiency"):
        sev = [f["severity"] for f in findings if f["verdict"] == v]
        out[v] = "red" if "red" in sev else "amber" if "amber" in sev else "green"
    return out


def promotion_offered(approvals: int, rollbacks: int, settings: dict) -> bool:
    """l2.offer_promotion."""
    return approvals >= settings["l2.promotion_min_approvals"] and rollbacks <= settings["l2.promotion_max_rollbacks"]


def next_quarter_end(now: datetime, tz: str) -> datetime:
    local = now.astimezone(ZoneInfo(tz))
    for m in (3, 6, 9, 12):
        end = local.replace(month=m, day=31 if m in (3, 12) else 30, hour=18, minute=0, second=0, microsecond=0)
        if end > local:
            return end
    return local.replace(year=local.year + 1, month=3, day=31, hour=18, minute=0, second=0, microsecond=0)


def next_25th(now: datetime, tz: str) -> datetime:
    local = now.astimezone(ZoneInfo(tz))
    d = local.replace(day=25, hour=0, minute=0, second=0, microsecond=0)
    if d <= local:
        d = (d.replace(day=1) + timedelta(days=32)).replace(day=25)
    return d


# ---------------------------------------------------------------- data

def calendar(now: datetime, enable=()) -> list:
    out = []
    l6 = stories(enable).get("L-6")
    if l6:
        for i, c in enumerate(l6["plant"]["calendar"]):
            when = next_quarter_end(now, "Asia/Singapore") if c["when"] == "next_quarter_end" else next_25th(now, "Asia/Singapore")
            out.append({"id": f"cal-{i + 1}", "kind": c["kind"], "location": c["location"], "starts_at": when.isoformat(),
                        "ends_at": (when + timedelta(hours=12)).isoformat(), "note": c["note"], "added_by": "l2-engineer-1"})
    return out + STATE.calendar_added


def action_types(settings: dict, enable=()) -> list:
    l4 = stories(enable).get("L-4")
    base = {"move_vms_between_clusters": {"approvals": 23, "rollbacks": 0},
            "power_off_idle_vm": {"approvals": 8, "rollbacks": 0},
            "delete_old_snapshot": {"approvals": 31, "rollbacks": 2}}
    if not l4:
        base.pop("move_vms_between_clusters")
    out = []
    for t, r in base.items():
        approvals = r["approvals"] + STATE.extra_approvals.get(t, 0)
        tier = STATE.tiers.get(t, "approval")
        out.append({"action_type": t, "tier": tier, "approvals": approvals, "rollbacks": r["rollbacks"],
                    "promotion_offered": tier != "automatic" and promotion_offered(approvals, r["rollbacks"], settings),
                    "promoted_by": STATE.promoted_by.get(t)})
    return out


def proposals(enable=()) -> list:
    l4 = stories(enable).get("L-4")
    out = []
    if l4:
        p = l4["plant"]["proposal"]
        state = STATE.proposals.get(p["id"], {"state": "waiting"})
        out.append({"id": p["id"], "action_type": p["action_type"], "targets": [p["from"], p["to"]],
                    "reason": f"{p['from']} is running hot. Move {p['vms']} VMs to {p['to']}, which has room in the same class.",
                    **state})
    for pid, p in STATE.proposals.items():
        if p.get("from_config"):
            out.append(p)
    return out


def daily(now: datetime, enable=()) -> dict:
    nd = noc.build(now, enable)
    ds, st, act = nd["ds"], nd["settings"], stories(enable)
    cal = calendar(now, enable)
    f = []
    if "N-1" in act:
        c = next(x for x in nd["clusters"] if x["id"] == "FR-S-02")
        esc = "Escalated to you by the NOC." if "inc-fr-s-02" in noc.STATE.escalated else "Open at the NOC, not yet escalated."
        f.append({"id": "f-fr-s-02", "verdict": "present_health", "pillar": "performance", "severity": "red",
                  "object": "FR-S-02", "object_type": "cluster", "parent_chain": ["Frankfurt", "FR-S-02"],
                  "summary": f"Cluster Performance {round(c['score'])}: VMs waiting for CPU. {esc}",
                  "investigate": "FR-S-02", "score": c["score"]})
    if "N-4" in act:
        s = ds["health"]["safe"]
        f.append({"id": "f-ld-ssh", "verdict": "present_health", "pillar": "security", "severity": "red",
                  "object": "London ESXi hosts", "object_type": "host", "parent_chain": ["London"],
                  "summary": f"SSH on {nd['safe']['ld']['ssh_or_shell_enabled']} hosts outside the maintenance window. "
                             f"{s['vms_below_sla']} VMs below the Security SLA this month.",
                  "ssh_count": nd["safe"]["ld"]["ssh_or_shell_enabled"]})
    if "L-4" in act:
        p = proposals(enable)[0]
        f.append({"id": "f-sg-s-04", "verdict": "present_health", "pillar": "performance", "severity": "amber",
                  "object": "SG-S-04", "object_type": "cluster", "parent_chain": ["Singapore", "SG-S-04"],
                  "summary": "Cluster Performance 68 at the end-of-day batch peak; a neighbour cluster has room.",
                  "proposal": p})
    if "L-7" in act:
        f.append({"id": "f-ld-ds-03", "verdict": "present_health", "pillar": "performance", "severity": "amber",
                  "object": "LD-DS-03", "object_type": "datastore", "parent_chain": ["London", "LD-DS-03"],
                  "summary": "London end-of-day batch ran 40 minutes longer; read latency on LD-DS-03 rising for 3 nights. "
                             "At this rate the batch runs into the start of business."})
    if "L-3" in act:
        f.append({"id": "f-va-esx-142", "verdict": "risk", "pillar": "configuration", "severity": "amber",
                  "object": "va-esx-142", "object_type": "host", "parent_chain": ["Virginia", "VA-G-05", "va-esx-142"],
                  "summary": "NTP server and syslog target differ from the other hosts in VA-G-05."})
    if "C-1" in act:
        d = ds["locations"]["sg"]["decision"]
        f.append({"id": "f-sg-silver", "verdict": "risk", "pillar": "capacity", "severity": "amber",
                  "object": "SG-Silver", "object_type": "cluster_group", "parent_chain": ["Singapore", "SG-Silver"],
                  "summary": f"Memory decision date in {d['days']} days; already in the next purchase round."})
    if "L-6" in act:
        qe = next(c for c in cal if c["kind"] == "quarter_end_close")
        f.append({"id": "f-va-s-03", "verdict": "risk", "pillar": "capacity", "severity": "amber",
                  "object": "VA-S-03", "object_type": "cluster", "parent_chain": ["Virginia", "VA-S-03"],
                  "summary": act["L-6"]["plant"]["finding"]["summary"] + ".", "explained_by": qe})
    if "C-6" in act:
        c6 = act["C-6"]["plant"]
        f.append({"id": "f-sg-silver-waste", "verdict": "efficiency", "pillar": "capacity", "severity": "amber",
                  "object": "SG-Silver", "object_type": "cluster_group", "parent_chain": ["Singapore", "SG-Silver"],
                  "summary": f"{c6['powered_off_vms']} powered-off, {c6['idle_vms']} idle and {c6['oversized_large_vms']} large oversized VMs. "
                             "Reclaiming them moves the memory decision past the purchase round."})
    order = {"red": 0, "amber": 1}
    f.sort(key=lambda x: (1 if x.get("explained_by") else 0, order[x["severity"]]))
    slipped = []
    if "L-5" in act:
        s = act["L-5"]["plant"]["slipped"]
        slipped.append({"object": s["object"], "title": s["title"], "raised": generator.rel(s["raised"], now).isoformat()})
    started = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=2)
    return {"run": {"kind": "daily", "region": "Asia Pacific", "started_at": started.isoformat(),
                    "finished_at": (started + timedelta(minutes=41)).isoformat(),
                    "review": "About 10 minutes when nothing needs you."},
            "verdicts": verdicts(f), "findings": f, "slipped_alerts": slipped,
            "action_types": action_types(st, enable)}


def escalations(now: datetime, enable=()) -> list:
    nd = noc.build(now, enable)
    out = []
    for iid, route in noc.STATE.escalated.items():
        d = noc.incident_detail(nd, iid)
        if not d:
            continue
        ev = {"sop_steps": [{"kind": s["kind"], "text": s["text"], "result": s.get("result"), "passed": s.get("passed")}
                            for s in d["sop"]["steps"]],
              "l1_actions": [{"action": h["action"], "target": h["target"], "by": h["actor_human"], "after": h["after"]}
                             for h in d["history"] if h["action"] not in ("agent_draft",)],
              "villains": [], "victims": []}
        if iid == "inc-fr-s-02":
            ev["villains"] = [{"vm": "fr-bat-017", "class": "bronze", "environment": "production",
                               "cpu_usage_percent": 95.0, "vcpu": 16, "cpu_ready_percent": 1.2}]
            ev["victims"] = [{"vm": vm, "cpu_ready_percent": r, "co_stop_percent": c, "vm_performance": p}
                             for vm, r, c, p in (("fr-app-101", 9.8, 1.1, 31), ("fr-app-114", 8.1, 0.9, 36),
                                                 ("fr-db-022", 7.4, 0.6, 41))]
        out.append({**{k: d[k] for k in ("id", "title", "root_object", "severity", "location_name", "escalation_route")},
                    "evidence": ev, "closure": STATE.closures.get(iid), "agent_history":
                    [h for h in d["history"] if h["action"] == "agent_draft"]})
    return out


def investigate(now: datetime, obj: str, enable=()) -> dict | None:
    act = stories(enable)
    nd = noc.build(now, enable)
    if obj == "sg-app-117" and "L-2" in act:
        p = act["L-2"]["plant"]
        return {"object": obj, "object_type": "vm",
                "parents": [{"object": "SG-S-07", "kind": "cluster", "status": "green", "note": "Cluster Performance 92: the cluster serves its VMs well."},
                            {"object": "sg-esx-088", "kind": "host", "status": "green", "note": "ESXi Performance 94."}],
                "steps": [
                    {"step": "contention", "status": "pass", "values": f"CPU Ready {p['vm']['cpu_ready_percent']}%, Co-stop {p['vm']['co_stop_percent']}%, memory wait {p['vm']['memory_wait_percent']}%, disk latency {p['vm']['disk_latency_ms']} ms"},
                    {"step": "consumption", "status": "pass", "values": "CPU usage 35% of 8 vCPU; memory 61% of 32 GB"},
                    {"step": "configuration", "status": "pass", "values": "No limit, normal shares, VMware Tools current"},
                    {"step": "known_bug", "status": "pass", "values": "No known issue for this ESXi build"},
                    {"step": "log", "status": "pass", "values": "No vSphere log events for this VM in the window"}],
                "first_failing": None,
                "realms": {"vm": {"status": "green", **p["vm"]}, "guest_os": {"status": "red", **p["guest_os"]}},
                "realm_verdict": "guest_os",
                "conclusion": "The cause is inside the Guest OS. Hand this evidence to the Windows or Linux team.",
                "logs": [{"at": (now - timedelta(minutes=50)).isoformat(), "text": "No vSphere events for sg-app-117 in the last 24 hours."}]}
    if obj == "FR-S-02" and "N-1" in act:
        c = next(x for x in nd["clusters"] if x["id"] == "FR-S-02")
        return {"object": obj, "object_type": "cluster", "parents": [],
                "steps": [
                    {"step": "contention", "status": "fail", "values": f"Cluster Performance {round(c['score'])}. Worst VM CPU Ready 9.8%, 90th percentile CPU Ready 6.8%"},
                    {"step": "consumption", "status": "fail", "values": "fr-bat-017 uses 95% of its 16 vCPU since its batch started"},
                    {"step": "configuration", "status": "fail", "values": "fr-bat-017 is a Bronze VM in a Silver cluster: wrong placement for its class"},
                    {"step": "known_bug", "status": "pass", "values": "No known issue for this ESXi build"},
                    {"step": "log", "status": "info", "values": "DRS migrations in FR-S-02 three times the usual rate in the last hour"}],
                "first_failing": "contention",
                "realms": None, "realm_verdict": "platform",
                "conclusion": "The platform is the cause: contention from one oversized Bronze VM placed in a Silver cluster.",
                "logs": [{"at": (now - timedelta(minutes=21)).isoformat(), "text": "fr-bat-017 powered on job batch-eod-fr (vCenter task)."},
                         {"at": (now - timedelta(minutes=15)).isoformat(), "text": "DRS: 14 migrations in FR-S-02 in 15 minutes."}]}
    return None


CONFIG_BASE = [
    {"id": "c-esx-version", "group": "update_it", "object": "VA-B-01, VA-B-02", "setting": "ESXi version",
     "actual": "N-2 on 18 hosts", "standard": "N or N-1"},
    {"id": "c-tools-variants", "group": "simplify_it", "object": "Estate", "setting": "VMware Tools versions",
     "actual": "5 versions", "standard": "3 versions (current plus two)"},
]


def configuration(now: datetime, enable=()) -> dict:
    act = stories(enable)
    items = []
    if "L-3" in act:
        for i, d in enumerate(act["L-3"]["plant"]["drift"]):
            items.append({"id": f"c-va-esx-142-{i + 1}", "group": "correct_it", "object": "va-esx-142 (VA-G-05)",
                          "setting": d["setting"], "actual": d["actual"], "standard": d["standard"]})
    items += CONFIG_BASE
    for it in items:
        it["standard_version"] = STATE.standards.get(it["setting"], 1)
        it["decision"] = next((p.get("choice") for p in STATE.proposals.values() if p.get("config_id") == it["id"]), None)
    groups = {g: [i for i in items if i["group"] == g] for g in ("correct_it", "update_it", "simplify_it", "optimize_it")}
    return {"groups": groups, "filter_default": "gold"}


THRESHOLDS = {"th-cluster-perf-red": {"metric": "Cluster Performance", "operator": "below", "value": 50, "version": 1}}


def replay(now: datetime, tid: str, new_value: float, settings: dict, seed: int = 7) -> dict:
    """l2.threshold_replay: alert episodes (consecutive hours under the value) per day, current and new."""
    t = {**THRESHOLDS[tid], **STATE.thresholds.get(tid, {})}
    days = settings["l2.replay_days"]
    clusters = [f"{loc}-{c}-{i:02d}" for loc in ("SG", "VA", "FR", "TK", "LD") for c in "GSB" for i in (1, 2, 3)]
    per_day = []
    for d in range(days, 0, -1):
        day = (now - timedelta(days=d)).date()
        cur = new = 0
        for cid in clusters:
            rng = random.Random(f"{seed}-{cid}-{day}")
            prev_cur = prev_new = False
            for h in range(24):
                dip = rng.random() < 0.004
                score = rng.uniform(70, 97) - (rng.uniform(25, 45) if dip else 0)
                below_cur, below_new = score < t["value"], score < new_value
                cur += below_cur and not prev_cur
                new += below_new and not prev_new
                prev_cur, prev_new = below_cur, below_new
        per_day.append({"date": day.isoformat(), "current": cur, "new": new})
    return {"threshold": tid, **t, "new_value": new_value, "days": days, "per_day": per_day,
            "total_current": sum(x["current"] for x in per_day), "total_new": sum(x["new"] for x in per_day)}


# ---------------------------------------------------------------- actions

def act(now: datetime, path: list, body: dict, enable=()) -> tuple[int, dict]:
    st = generator.load_spec()["settings"]
    human = body.get("actor_human") or st["noc.actor_default"].replace("operator", "l2-engineer")
    rec = lambda a, target, reason, before, after, **k: noc.record(a, target, human, reason, before, after, now, **k)
    with STATE.lock:
        if path[:1] == ["proposals"] and len(path) == 3:
            pid, verb = path[1], path[2]
            p = next((x for x in proposals(enable) if x["id"] == pid), None)
            if not p:
                return 404, {"error": "no such proposal"}
            if verb == "approve":
                STATE.proposals[pid] = {**STATE.proposals.get(pid, {}), "state": "approved", "decided_by": human}
                STATE.extra_approvals[p["action_type"]] = STATE.extra_approvals.get(p["action_type"], 0) + 1
                rec("approve", pid, p["reason"], "waiting", "approved")
                return 200, {"state": "approved"}
            if verb == "reject":
                if not body.get("reason"):
                    return 400, {"error": "A reason is required to reject: it tells L2 which rule is wrong."}
                STATE.proposals[pid] = {**STATE.proposals.get(pid, {}), "state": "rejected", "decided_by": human,
                                        "rejection_reason": body["reason"]}
                rec("reject", pid, body["reason"], "waiting", "rejected")
                return 200, {"state": "rejected"}
        if path[:1] == ["action-types"] and len(path) == 3 and path[2] == "promote":
            t = next((x for x in action_types(st, enable) if x["action_type"] == path[1]), None)
            if not t or not t["promotion_offered"]:
                return 403, {"error": "Promotion is not offered for this action type."}
            if not body.get("reason"):
                return 400, {"error": "A reason is required: you become accountable for its automatic runs."}
            STATE.tiers[path[1]] = "automatic"
            STATE.promoted_by[path[1]] = human
            rec("promote", path[1], body["reason"], "approval", "automatic")
            return 200, {"tier": "automatic", "promoted_by": human}
        if path[:1] == ["escalations"] and len(path) == 3:
            iid, verb = path[1], path[2]
            esc = next((e for e in escalations(now, enable) if e["id"] == iid), None)
            if not esc:
                return 404, {"error": "no such escalation"}
            if verb == "close":
                need = ("root_cause", "corrective_action", "detection", "detection_note")
                missing = [k for k in need if not body.get(k)]
                if missing:
                    return 400, {"error": f"Missing: {', '.join(missing)}. An escalation closes with a cause, a fix and a detection decision."}
                STATE.closures[iid] = {k: body[k] for k in need} | {"by": human}
                noc.STATE.closed[iid] = body["root_cause"]
                rec("close_escalation", iid, body["root_cause"], "escalated", "closed", incident=iid)
                return 200, {"state": "closed"}
            if verb == "agent":
                vocab = yaml.safe_load((SPEC / "catalog/vocabulary/l2.yaml").read_text())
                facts = {"incident": {k: esc[k] for k in ("title", "root_object", "location_name", "escalation_route")},
                         "evidence": esc["evidence"],
                         "investigation": investigate(now, esc["root_object"], enable)}
                template = (f"Draft by Agent E2, to review: {esc['root_object']}: contention from fr-bat-017, a production Bronze VM "
                            "placed in a Silver cluster. Corrective action: move it to a Bronze cluster. Detection: a check rule "
                            "for class mismatch on placement.")
                out = agent_e2.draft_facts(facts, "rca_draft", st, vocab["avoided"], template)
                r = rec("agent_draft", iid, "rca_draft", "-", out["source"], actor_agent="agent-e2", incident=iid)
                return 200, {**out, "record": r}
        if path[:1] == ["configuration"] and len(path) == 3 and path[2] == "decide":
            cfg = configuration(now, enable)
            item = next((i for g in cfg["groups"].values() for i in g if i["id"] == path[1]), None)
            if not item:
                return 404, {"error": "no such finding"}
            choice = body.get("choice")
            if choice == "fix_the_setting":
                pid = "p-" + item["id"]
                STATE.proposals[pid] = {"id": pid, "action_type": "set_host_setting", "targets": [item["object"]],
                                        "reason": f"Set {item['setting']} to the standard: {item['standard']}.",
                                        "state": "waiting", "from_config": True, "config_id": item["id"], "choice": choice}
                rec("propose_fix", item["id"], item["setting"], item["actual"], item["standard"])
                return 200, {"proposal": pid}
            if choice == "fix_the_standard":
                v = STATE.standards.get(item["setting"], 1) + 1
                STATE.standards[item["setting"]] = v
                STATE.proposals["s-" + item["id"]] = {"config_id": item["id"], "choice": choice}
                rec("change_standard", item["setting"], body.get("reason", ""), item["standard"], item["actual"])
                return 200, {"standard_version": v}
            return 400, {"error": "choice must be fix_the_setting or fix_the_standard"}
        if path[:1] == ["investigate"] and len(path) == 3 and path[2] == "ask":
            facts = investigate(now, path[1], enable)
            if not facts or not body.get("question"):
                return 400, {"error": "an object this page knows and a question are required"}
            out = agent_e2.ask_service(st["agent_e2.service_url"], body["question"], facts, "l2")
            r = rec("agent_ask", path[1], body["question"], "-", out["source"], actor_agent="agent-e2")
            return 200, {**out, "record": r}
        if path == ["calendar"]:
            need = ("kind", "starts_at", "ends_at", "note")
            if any(not body.get(k) for k in need):
                return 400, {"error": "kind, starts_at, ends_at and note are required"}
            entry = {"id": f"cal-x{len(STATE.calendar_added) + 1}", **{k: body[k] for k in need},
                     "location": body.get("location"), "added_by": human}
            STATE.calendar_added.append(entry)
            rec("add_calendar_entry", entry["id"], entry["note"], "-", entry["kind"])
            return 200, entry
        if path[:1] == ["thresholds"] and len(path) == 3 and path[2] == "publish":
            tid = path[1]
            if tid not in THRESHOLDS or "value" not in body:
                return 400, {"error": "threshold and value are required"}
            cur = {**THRESHOLDS[tid], **STATE.thresholds.get(tid, {})}
            STATE.thresholds[tid] = {"value": float(body["value"]), "version": cur["version"] + 1}
            rec("publish_threshold", tid, body.get("reason", ""), str(cur["value"]), str(body["value"]))
            return 200, STATE.thresholds[tid]
    return 404, {"error": "unknown action"}
