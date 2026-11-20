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

from . import agent_e2, generator, noc, store

SPEC = Path(__file__).resolve().parents[2] / "spec"


class State:
    """L2 workflow state, kept in the PCM database (store.py, D-080)."""
    FIELDS = ("proposals", "closures", "calendar_added", "policies", "replays", "extra_approvals", "standards", "thresholds")

    def __init__(self):
        self.lock = threading.RLock()
        self.load()

    def _defaults(self):
        self.proposals, self.closures, self.calendar_added = {}, {}, []
        self.policies, self.replays, self.extra_approvals = {}, {}, {}
        self.standards, self.thresholds = {}, {}

    def load(self):
        self._defaults()
        for k, v in store.load_state("l2").items():
            if k in self.FIELDS:
                setattr(self, k, v)

    def save(self):
        store.save_state("l2", {k: getattr(self, k) for k in self.FIELDS})

    def reset(self):
        """Prototype and test reset only."""
        self._defaults()
        store.clear_state("l2")


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


def guardrail_block(policy: dict, run: dict) -> str | None:
    """l2.action_policy: the first guardrail a run breaks, or None. Guardrails, not approvals, gate automatic runs (D-079)."""
    g = policy.get("guardrails", {})
    if "max_vms_per_cluster_per_hour" in g and run.get("vms", 0) > g["max_vms_per_cluster_per_hour"]:
        return "max_vms_per_cluster_per_hour"
    if g.get("same_class_of_service_only") and not run.get("same_class", True):
        return "same_class_of_service_only"
    if g.get("not_in_close_week") and run.get("in_close_week"):
        return "not_in_close_week"
    if g.get("environment") == "non_production" and run.get("environment") == "production":
        return "environment"
    return None


def accountable(policy: dict, action_type: str) -> str:
    """D-050 for automatic runs: the policy owner and the policy version."""
    return f"policy {action_type} v{policy['version']}, owner {policy['owner']}"


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


def policies(enable=()) -> list:
    """Action policies (catalog/policies/actions.yaml) with published changes, plus the record as evidence."""
    base = yaml.safe_load((SPEC / "catalog/policies/actions.yaml").read_text())["policies"]
    l4 = stories(enable).get("L-4")
    rec = {"move_vms_between_clusters": (l4["plant"]["record"] if l4 else {"approvals": 0, "rejections": 0, "rollbacks": 0}),
           "power_off_idle_vm": {"approvals": 8, "rejections": 0, "rollbacks": 0},
           "delete_old_snapshot": {"approvals": 31, "rejections": 2, "rollbacks": 2}}
    out = []
    for t, p in base.items():
        cur = {**p, **STATE.policies.get(t, {})}
        r = dict(rec.get(t, {"approvals": 0, "rejections": 0, "rollbacks": 0}))
        r["approvals"] = r.get("approvals", 0) + STATE.extra_approvals.get(t, 0)
        out.append({"action_type": t, "tier": cur["tier"], "guardrails": cur["guardrails"], "version": cur["version"],
                    "owner": cur["owner"], "workspace": cur.get("workspace"), "record": r})
    return out


def history_runs(action_type: str, enable=()) -> list:
    """The recent runs a policy replay reads. Synthetic: built from story L-4's counts."""
    l4 = stories(enable).get("L-4")
    if action_type != "move_vms_between_clusters" or not l4:
        return []
    h = l4["plant"]["history"]
    runs = []
    for i in range(h["moves"]):
        run = {"vms": 4 + i % 5, "same_class": True, "in_close_week": False}
        if i < h["more_than_10_vms"]:
            run["vms"] = 12 + i
        elif i < h["more_than_10_vms"] + h["across_classes"]:
            run["same_class"] = False
        elif i < h["more_than_10_vms"] + h["across_classes"] + h["in_close_week"]:
            run["in_close_week"] = True
        runs.append(run)
    return runs


def policy_replay(action_type: str, proposed: dict, enable=()) -> dict:
    """l2.policy_replay: what the proposed policy would have run automatically, and what each guardrail stops."""
    runs = history_runs(action_type, enable)
    stopped = {}
    auto = 0
    for r in runs:
        b = guardrail_block(proposed, r)
        if b:
            stopped[b] = stopped.get(b, 0) + 1
        elif proposed.get("tier") == "automatic":
            auto += 1
    return {"action_type": action_type, "runs": len(runs), "would_run_automatically": auto, "stopped": stopped,
            "proposed": proposed}


def proposals(enable=()) -> list:
    l4 = stories(enable).get("L-4")
    out = []
    if l4:
        p = l4["plant"]["proposal"]
        state = STATE.proposals.get(p["id"], {"state": "waiting"})
        out.append({"id": p["id"], "action_type": p["action_type"], "targets": [p["from"], p["to"]],
                    "run": {"vms": p["vms"], "same_class": p["same_class"], "in_close_week": p["in_close_week"]},
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
            "policies": policies(enable)}


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
    """Every L2 action is saved to the PCM database before the answer goes back. L2 also changes NOC state."""
    with noc.STATE.lock, STATE.lock:
        out = _act(now, path, body, enable)
        STATE.save()
        noc.STATE.save()
    return out


def _act(now: datetime, path: list, body: dict, enable=()) -> tuple[int, dict]:
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
        if path[:1] == ["policies"] and len(path) == 3 and path[2] in ("replay", "publish"):
            t = path[1]
            cur = next((x for x in policies(enable) if x["action_type"] == t), None)
            if not cur:
                return 404, {"error": "no such action type"}
            proposed = {"tier": body.get("tier", cur["tier"]), "guardrails": body.get("guardrails", cur["guardrails"])}
            if proposed["tier"] not in ("automatic", "approval", "never"):
                return 400, {"error": "tier must be automatic, approval or never"}
            if path[2] == "replay":
                out = policy_replay(t, proposed, enable)
                STATE.replays[t] = proposed
                return 200, out
            if STATE.replays.get(t) != proposed:
                return 400, {"error": "Replay the proposed policy before publishing it."}
            if not body.get("reason"):
                return 400, {"error": "A reason is required to publish a policy change."}
            new = {**proposed, "version": cur["version"] + 1, "owner": human}
            STATE.policies[t] = new
            STATE.replays.pop(t, None)
            rec("publish_policy", t, body["reason"], f"v{cur['version']} {cur['tier']}", f"v{new['version']} {new['tier']}")
            ran = []
            if new["tier"] == "automatic":
                for p in proposals(enable):
                    if p["action_type"] == t and p.get("state") == "waiting" and p.get("run") and not guardrail_block(new, p["run"]):
                        STATE.proposals[p["id"]] = {**STATE.proposals.get(p["id"], {}), "state": "ran_automatically",
                                                    "accountable": accountable(new, t)}
                        noc.record(t, p["id"], accountable(new, t), "policy run", "waiting", "ran automatically", now,
                                   actor_agent="pcm-policy")
                        ran.append(p["id"])
            return 200, {**new, "ran_automatically": ran}
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
