"""L2 workspace data behind Monitor, Improve and Rules: the daily and weekly check runs, proposals, action policies,
configuration, calendar, threshold replay, decisions and detailed inventory (prototype). Cases are in l2_cases.py.

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
    FIELDS = ("proposals", "closures", "calendar_added", "policies", "replays", "extra_approvals", "standards", "thresholds",
              "weekly_assigned", "decisions_done", "inventory_expected")

    def __init__(self):
        self.lock = threading.RLock()
        self.load()

    def _defaults(self):
        self.proposals, self.closures, self.calendar_added = {}, {}, []
        self.policies, self.replays, self.extra_approvals = {}, {}, {}
        self.standards, self.thresholds = {}, {}
        self.weekly_assigned, self.decisions_done, self.inventory_expected = {}, {}, {}

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
        store.execute("DELETE FROM team_decision")


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
                  "summary": "Memory is the tightest resource, and the Capacity workspace already has it in the next purchase round."})
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


# Planted background findings; their standards come from catalog/standards.yaml (Docs design, 2.8).
CONFIG_BASE = [
    {"id": "c-esx-version", "group": "update_it", "object": "VA-B-01, VA-B-02", "objects": ["VA-B-01", "VA-B-02"], "setting": "esxi_version", "actual": "8.0 U3 (N-2) on every host"},
    {"id": "c-tools-variants", "group": "simplify_it", "object": "Estate", "objects": ["estate"], "setting": "vmware_tools_variants", "actual": "5 versions"},
]


def configuration(now: datetime, enable=()) -> dict:
    act = stories(enable)
    items = []
    if "L-3" in act:
        for i, d in enumerate(act["L-3"]["plant"]["drift"]):
            items.append({"id": f"c-va-esx-142-{i + 1}", "group": "correct_it", "object": "va-esx-142 (VA-G-05)",
                          "objects": [act["L-3"]["objects"]["host"]], "setting": d["setting"], "actual": d["actual"]})
    if "L-10" in act:
        o, d = act["L-10"]["objects"], act["L-10"]["plant"]["drift"]
        items.append({"id": "c-ld-b-01-patch", "group": "simplify_it", "object": o["cluster"], "objects": [o["cluster"]],
                      "setting": "esxi_version", "actual": f"{d['behind_peers']} hosts one patch behind the rest of the cluster"})
    items += [dict(c) for c in CONFIG_BASE]
    std = generator.load_spec()["standards"]
    for it in items:
        it["standard"] = std[it["setting"]]["value"]
        it["setting_label"] = std[it["setting"]]["title"]
        it["standard_version"] = STATE.standards.get(it["setting"], 1)
        it["decision"] = next((p.get("choice") for p in STATE.proposals.values() if p.get("config_id") == it["id"]), None)
    groups = {g: [i for i in items if i["group"] == g] for g in ("correct_it", "update_it", "simplify_it", "optimize_it")}
    return {"groups": groups, "filter_default": "gold"}


THRESHOLDS = {k: {f: v[f] for f in ("metric", "operator", "value", "version")}
              for k, v in generator.load_spec()["thresholds"].items()}  # catalog/thresholds.yaml


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
        if path[:1] == ["weekly"] and len(path) == 3 and path[2] == "assign":
            fid = path[1]
            if fid not in {f["id"] for f in weekly(now, enable)["findings"]}:
                return 404, {"error": "no such finding"}
            if not body.get("owner") or not body.get("action"):
                return 400, {"error": "A weekly finding needs an owner and an action."}
            STATE.weekly_assigned[fid] = {"owner": body["owner"], "action": body["action"], "by": human, "at": now.isoformat()}
            rec("assign_weekly_finding", fid, body["action"], "open", f"assigned to {body['owner']}")
            return 200, STATE.weekly_assigned[fid]
        if path == ["monthly", "decisions"]:
            return add_decision(now, body, human, rec)
        if path[:2] == ["monthly", "decisions"] and len(path) == 4 and path[3] == "done":
            did = path[2]
            if did not in {d["id"] for d in decisions(now, enable)}:
                return 404, {"error": "no such decision"}
            STATE.decisions_done[did] = {"by": human, "at": now.isoformat()}
            rec("decision_done", did, "", "open", "done")
            return 200, {"state": "done"}
        if path[:1] == ["inventory"] and len(path) == 3 and path[2] == "expected":
            cid = path[1]
            if cid not in {c["id"] for c in inventory(now, 30, enable)["unexplained"]}:
                return 404, {"error": "no unexplained change with that id"}
            if not body.get("reason"):
                return 400, {"error": "A reason is required: it says why the change was expected."}
            STATE.inventory_expected[cid] = {"reason": body["reason"], "by": human, "at": now.isoformat()}
            rec("change_expected", cid, body["reason"], "unexplained", "expected")
            return 200, {"explanation": "l2_expected"}
    return 404, {"error": "unknown action"}


# ---------------------------------------------------------------- weekly check (D-042)

def is_drift(nightly: list, min_steps: int = 5, min_change: float = 0.10) -> bool:
    """l2.weekly_check drift rule: same direction on at least 5 of the 6 steps, total change at least 10% of night 1."""
    steps = [b - a for a, b in zip(nightly, nightly[1:])]
    same = max(sum(1 for d in steps if d > 0), sum(1 for d in steps if d < 0))
    change = abs(nightly[-1] - nightly[0]) / abs(nightly[0]) if nightly[0] else 0.0
    return same >= min_steps and change >= min_change


def is_hidden(peak: float, red: float, vm_status: str) -> bool:
    """l2.weekly_check hidden rule: one instance at or above red at peak while the VM total is green."""
    return peak >= red and vm_status == "green"


def last_sunday_run(now: datetime, tz: str = "Asia/Singapore") -> datetime:
    local = now.astimezone(ZoneInfo(tz))
    d = local - timedelta(days=(local.weekday() + 1) % 7)
    run = d.replace(hour=2, minute=0, second=0, microsecond=0)
    return run if run <= local else run - timedelta(days=7)


def _bg_l2():
    return generator.load_spec()["stories"]["background"]["l2"]


def weekly(now: datetime, enable=()) -> dict:
    act, bg = stories(enable), _bg_l2()
    f = []
    if "L-8" in act:
        p, o = act["L-8"]["plant"], act["L-8"]["objects"]
        n = p["nightly_used_percent"]
        rate = (n[-1] - n[0]) / (len(n) - 1)
        days_full = int((100 - n[-1]) / rate) if rate > 0 else None
        f.append({"id": "w-sg-ds-11", "kind": "slow_drift", "object": o["datastore"], "parent_chain": ["Singapore", o["cluster"], o["datastore"]],
                  "summary": f"Used space up {sum(1 for a, b in zip(n, n[1:]) if b > a)} of 6 nights, {n[0]}% to {n[-1]}%. "
                             f"At this rate it is full in about {days_full} days.",
                  "cause": f"On {o['vm']}: {p['cause']}.", "evidence": {"nightly": n, "unit": "% used"},
                  "drift": is_drift(n), "days_to_full": days_full})
    for sid, fid, chain in (("L-9", "w-sg-db-044", ["Singapore", "SG-G-01", "sg-db-044"]),
                            ("L-5", "w-va-db-033", ["Virginia", "va-db-033"])):
        if sid not in act:
            continue
        h = act[sid]["plant"]["hidden_in_average"]
        unit = "ms" if h["metric"] == "disk_latency_ms" else "%"
        what = "latency" if unit == "ms" else "usage"
        f.append({"id": fid, "kind": "hidden_in_average", "object": chain[-1], "parent_chain": chain,
                  "summary": f"{h['instance']}: peak {what} {h['peak']} {unit}, red at {h['red']} {unit}, while the VM average is {h['vm_average']} {unit}.",
                  "cause": act[sid]["plant"].get("cause", "The VM-level number averages this instance away, so no VM alert fires.")
                           .rstrip(".") + ".",
                  "evidence": h, "hidden": is_hidden(h["peak"], h["red"], "green")})
    if "L-10" in act:
        o, d = act["L-10"]["objects"], act["L-10"]["plant"]["drift"]
        f.append({"id": "w-ld-b-01", "kind": "configuration_drift", "object": o["cluster"], "parent_chain": ["London", o["cluster"]],
                  "summary": f"{d['behind_peers']} hosts ({', '.join(o['hosts'])}) are behind the other {d['peers']} on ESXi patches.",
                  "cause": "Hosts at different patch levels in one cluster behave differently under vMotion and HA, and hide known bugs.",
                  "evidence": d})
    for x in f:
        x["cause"] = x["cause"][:1].upper() + x["cause"][1:]
        x["assigned"] = STATE.weekly_assigned.get(x["id"])
    f.sort(key=lambda x: (x["assigned"] is not None, ["slow_drift", "hidden_in_average", "configuration_drift"].index(x["kind"])))
    slipped = []
    if "L-5" in act:
        sl = act["L-5"]["plant"]["slipped"]
        slipped.append({"object": sl["object"], "title": sl["title"], "raised": generator.rel(sl["raised"], now).isoformat(),
                        "caught_by": "hidden_in_average" if "L-5" in act else None, "finding": "w-va-db-033",
                        "would_have_caught_it": "A check rule on each virtual disk's latency, not the VM average."})
    run = last_sunday_run(now)
    return {"run": {"kind": "weekly", "region": "Asia Pacific", "started_at": run.isoformat(),
                    "finished_at": (run + timedelta(hours=3, minutes=10)).isoformat(), "review": "About 1 hour."},
            "measures": {"week": bg["week"], "last_week": bg["last_week"]}, "findings": f, "slipped_alerts": slipped}


# ---------------------------------------------------------------- monthly review (D-043)

def decision_state(due: datetime, done: bool, now: datetime) -> str:
    """l2.team_decision: done, overdue (open past its due date) or open."""
    return "done" if done else "overdue" if due < now else "open"


def decisions(now: datetime, enable=()) -> list:
    act = stories(enable)
    out = []
    for d in (act["L-12"]["plant"]["decisions"] if "L-12" in act else []):
        done = STATE.decisions_done.get(d["id"]) or ({"by": d["done_by"], "at": generator.rel(d["done"], now).isoformat()} if d.get("done") else None)
        out.append({"id": d["id"], "what": d["what"], "owner": d["owner"], "made": generator.rel(d["made"], now).isoformat(),
                    "due": generator.rel(d["due"], now).isoformat(), "done": done})
    for r in store.rows("SELECT * FROM team_decision ORDER BY id"):
        out.append({**{k: r[k] for k in ("id", "what", "owner", "made", "due")}, "done": STATE.decisions_done.get(r["id"])})
    for d in out:
        d["state"] = decision_state(datetime.fromisoformat(d["due"]), bool(d["done"]), now)
    return sorted(out, key=lambda d: (["overdue", "open", "done"].index(d["state"]), d["due"]))


def add_decision(now: datetime, body: dict, human: str, rec) -> tuple[int, dict]:
    if not all(body.get(k) for k in ("what", "owner", "due")):
        return 400, {"error": "A decision needs what, an owner and a due date."}
    try:
        due = datetime.fromisoformat(body["due"])
    except ValueError:
        return 400, {"error": "due must be YYYY-MM-DD"}
    if due.tzinfo is None:
        due = due.replace(hour=18, tzinfo=now.tzinfo)
    n = store.rows("SELECT COUNT(*) AS n FROM team_decision")[0]["n"]
    did = f"d-{n + 1:03d}"
    store.execute("INSERT INTO team_decision (id, made, what, owner, due, by) VALUES (?, ?, ?, ?, ?, ?)",
                  (did, now.isoformat(), body["what"], body["owner"], due.isoformat(), human))
    rec("record_decision", did, body["what"], "-", f"owner {body['owner']}, due {due.date().isoformat()}")
    return 200, {"id": did, "state": decision_state(due, False, now)}


def _month_label(now: datetime, back: int) -> str:
    y, m = now.year, now.month - back
    while m < 1:
        y, m = y - 1, m + 12
    return f"{y}-{m:02d}"


def monthly(now: datetime, enable=()) -> dict:
    from . import capacity
    ds = generator.generate(now, enable=enable)
    bg = _bg_l2()
    goals = []
    for g in ds["goals"]:
        jan = bg["goal_january"][g["id"]]
        line = lambda m: round(jan + (g["current"] - jan) * (m - 1) / 11)  # m: month of this year; counts and whole percent
        goals.append({**g, "months": [{"month": f"{now.year}-{m:02d}", "v": line(m)} for m in range(1, now.month + 1)],
                      "projected_year_end": g["current"]})
    by_id = {g["id"]: g for g in ds["goals"]}
    line12 = lambda gid: [round(bg["goal_january"][gid] + (by_id[gid]["current"] - bg["goal_january"][gid]) * (now.month - 11 + i - 1) / 11)
                          for i in range(12)]
    months = [_month_label(now, 11 - i) for i in range(12)]
    closure = STATE.closures.get("inc-fr-s-02")
    reps = []
    for r in bg["repeated_escalations"]:
        closed = r["closed_by"]
        if r["type"] == "class_mismatch" and closure and closure.get("detection") in ("new_check_rule", "new_sop"):
            closed = f"Check rule added this month: {closure['detection_note']}"
        reps.append({**r, "closed_by": closed, "loop_closed": bool(closed)})
    cfg = configuration(now, enable)
    week = capacity.week(now, enable)
    return {"now": now.isoformat(), "month": _month_label(now, 0), "decisions": decisions(now, enable), "goals": goals,
            "baselines": {"months": months, "urgent_alerts": line12("g-alerts"), "found_by_check_percent": line12("g-found-first"),
                          "repeated_escalations": bg["repeated_escalations_12m"], "diagnose_known_minutes": bg["diagnose_known_minutes_12m"],
                          "slipped_alerts": bg["slipped_alerts_12m"]},
            "repeated_escalations": reps,
            "configuration": {k: len(v) for k, v in cfg["groups"].items()},
            "capacity": {"next_round_closes": week["next_round_closes"], "groups_in_round": week["groups_in_round"],
                         "peak_warnings": [g["id"] for g in week["peak_warnings"]], "waste": [g["id"] for g in week["waste"]]}}


# ---------------------------------------------------------------- detailed inventory (D-020)

EXPLANATION_ORDER = ("pcm_action", "change_window", "request", "drs", "l2_expected")
CHANGE_ACTIONS = {"time_boxed_limit": "limit_set", "stop_provisioning": "provisioning_closed", "reopen_provisioning": "provisioning_opened",
                  "move_vms_between_clusters": "moved", "set_host_setting": "setting_changed"}
# Hourly rates per location are the NOC's expected counts (noc.CHANGE_TYPES); each type's usual explanation.
USUAL = {"created": {"request": 1.0}, "deleted": {"request": 1.0}, "powered_off": {"request": 0.7, "change_window": 0.3},
         "moved": {"drs": 1.0}, "resized": {"request": 1.0}}
HOURLY = {"created": 6, "deleted": 2, "powered_off": 3, "moved": 40, "resized": 1}


def explain(matches) -> str | None:
    """l2.change_explanation: the first explanation in the fixed order, or None (unexplained)."""
    return next((e for e in EXPLANATION_ORDER if e in set(matches)), None)


def inventory(now: datetime, days: int = 7, enable=()) -> dict:
    nd = noc.build(now, enable)
    ds, est, act = nd["ds"], generator.load_spec()["estate"], stories(enable)
    start = now - timedelta(days=days)
    layout, per = est["cluster_layout"]["share_of_hosts"], est["vms"]["per_host_average"]
    rng = random.Random(f"inventory-{now.date()}-{days}")
    counts, daily_totals, by_type = [], [], {t: {} for t in HOURLY}
    for lid, loc in ds["locations"].items():
        vms = round(sum(loc["hosts"] * layout[c] * per[c] for c in per))
        created = deleted = 0
        for d in range(days):
            for t, h in HOURLY.items():
                n = max(0, round(h * 24 * rng.uniform(0.85, 1.15)))
                created += n if t == "created" else 0
                deleted += n if t == "deleted" else 0
                for e, share in USUAL[t].items():
                    by_type[t][e] = by_type[t].get(e, 0) + round(n * share)
        counts.append({"location": lid, "name": loc["name"], "hosts": loc["hosts"],
                       "clusters": sum(1 for c in nd["clusters"] if c["location"] == lid),
                       "vms": vms, "datastores": round(loc["hosts"] * est["datastores"]["tb_per_host"] / est["datastores"]["average_tb"]),
                       "vms_change": created - deleted})
    for d in range(days):
        day = (now - timedelta(days=days - 1 - d)).date().isoformat()
        daily_totals.append({"day": day, **{t: round(HOURLY[t] * 24 * len(ds["locations"]) * random.Random(f"{day}-{t}").uniform(0.9, 1.1)) for t in HOURLY}})
    # PCM's own actions, from the action record: explained, listed with both identity fields.
    pcm = []
    for r in noc.STATE.history:
        if r["action"] in CHANGE_ACTIONS and datetime.fromisoformat(r["at"]) >= start:
            pcm.append({"id": f"rec-{r['action']}-{r['target']}", "at": r["at"], "object": r["target"], "type": CHANGE_ACTIONS[r["action"]],
                        "detail": r["after"], "by": r["actor_human"], "agent": r.get("actor_agent"), "via": "PCM",
                        "explanation": explain({"pcm_action"})})
    unexplained, expected = [], []
    if "L-11" in act:
        c = act["L-11"]["plant"]["change"]
        at = generator.rel(c["at"], now)
        if at >= start:
            unexplained.append({"id": c["id"], "at": at.isoformat(), "object": act["L-11"]["objects"]["vm"], "type": c["type"], "detail": c["detail"],
                                "by": c["by"], "via": c["via"], "environment": c["environment"], "class": c["class"], "count": 1})
    if "N-3" in act:
        p = act["N-3"]["plant"]
        unexplained.append({"id": "chg-tk-deleted", "at": generator.rel(p["deleted_within"], now).isoformat(), "object": "Tokyo",
                            "type": "deleted", "detail": f"{p['deleted_last_hour']} VMs deleted in one hour; {p['expected_deleted']} expected",
                            "by": p["by"], "via": p["via"], "environment": "unknown", "class": None, "count": p["deleted_last_hour"]})
    for c in list(unexplained):
        if c["id"] in STATE.inventory_expected:
            unexplained.remove(c)
            expected.append({**c, "explanation": "l2_expected", **{"expected": STATE.inventory_expected[c["id"]]}})
    unexplained.sort(key=lambda c: (c["environment"] != "production", c["class"] != "gold", c["at"]), reverse=False)
    return {"now": now.isoformat(), "days": days, "counts": counts, "daily": daily_totals,
            "explained_by_type": by_type, "pcm_actions": pcm, "expected_by_l2": expected, "unexplained": unexplained}

