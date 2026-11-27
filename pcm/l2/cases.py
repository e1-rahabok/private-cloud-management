"""L2 Troubleshoot: cases (pcm/l2/design-note.md, section 5; D-084, D-085, D-089).

GENERATED from pcm/l2/spec/pages/troubleshoot.md and case.md, pcm/l2/spec/catalog.yaml and pcm/core/spec/demo-data/scenario-stories.yaml.
Do not edit by hand (D-070).

A case has one trigger (a complaint L2 logs, an L1 escalation, or a monitoring finding), an object, a chain of
causes that Agent E2's flows propose and L2 confirms, the layers, one timeline, who else, and a close.
"""
from __future__ import annotations

import threading
from datetime import datetime, timedelta

import yaml

from ..core import agent_e2, generator, store
from . import l2, inventory_tree as X, monitor as M
from ..noc import noc

TRIGGERS = ("complaint", "escalation", "finding")
DETECTIONS = ("new_check_rule", "new_alert", "new_sop", "sop_updated", "none_with_reason")
LAYERS = ("guest_os", "vm", "host", "cluster", "storage", "network")
CASE_WORK = ("open_case", "agent_propose", "confirm_link", "rule_out_link", "close_case", "agent_draft", "agent_ask",
             "accept_escalation", "reject_escalation")  # L2's work on a case, not a change to the estate
NOISE = {"resuming traffic on dv port": 1043}  # SP5's VDI example: seen over 1,000 times on healthy desktops in 5 days


class State:
    """Cases L2 opened, and every decision on every case, in the PCM database (D-080)."""
    FIELDS = ("cases", "proposed", "links", "closures", "accepted", "seq", "drafts_published")

    def __init__(self):
        self.lock = threading.RLock()
        self.load()

    def _defaults(self):
        self.cases, self.proposed, self.links, self.closures, self.accepted = {}, {}, {}, {}, {}
        self.seq, self.drafts_published = 0, {}

    def load(self):
        self._defaults()
        for k, v in store.load_state("l2cases").items():
            if k in self.FIELDS:
                setattr(self, k, v)

    def save(self):
        store.save_state("l2cases", {k: getattr(self, k) for k in self.FIELDS})

    def reset(self):
        self._defaults()
        store.clear_state("l2cases")


STATE = State()


# ---------------------------------------------------------------- which PCM scenario story drives a case

def _scenario_story(case: dict, act: dict) -> dict | None:
    """The planted PCM scenario story behind a case, if any; its chain is what Agent E2's flows propose."""
    for sid in ("T-1", "L-2"):
        s = act.get(sid)
        if s and case["trigger"] == "complaint" and case["object"] == s["objects"]["vm"]:
            return s
    if case["trigger"] == "escalation":
        if case.get("incident") == "inc-fr-s-02" and act.get("L-1"):
            return act["L-1"]
        if case.get("incident") == "inc-tk-s-03" and act.get("T-2"):
            return act["T-2"]
    if case["trigger"] == "finding":
        for sid, fid in (("M-1", "f-m1-remote-memory"), ("M-2", "f-m2-other-wait")):
            if case.get("finding") == fid and act.get(sid):
                return act[sid]
    return None


def _generic_chain(E, vm: dict, now: datetime, act: dict) -> list:
    """No PCM scenario story: the SP5 order on the VM's own counters, as Agent E2's vm-slow flow would read them."""
    score = M.perf_score(E, vm, now, "24h")
    g, v = M.guest_os_values(vm, act), M.vm_values(vm, score, act)
    os_name = vm["guest_os"].capitalize()
    links = [{"id": "g-guest", "effect": "symptom", "cause": f"{os_name} waits inside the Guest OS", "object": vm["id"], "layer": "guest_os",
              "step": "contention", "flow": "vm-slow, step 1", "kind": "main",
              "expert": "confirmed" if g["guest_os_performance"] < 75 else "ruled_out",
              "evidence": [f"Run queue {g['run_queue_per_vcpu']} per vCPU", f"Paging {g['paging_per_s']} per second"]},
             {"id": "g-vm", "effect": "symptom", "cause": "The VM waits for the platform", "object": vm["id"], "layer": "vm",
              "step": "contention", "flow": "vm-slow, step 4", "kind": "main",
              "expert": "confirmed" if score < 75 else "ruled_out",
              "evidence": [f"CPU Ready {v['cpu_ready_percent']}%, Co-stop {v['co_stop_percent']}%", f"Disk latency {v['disk_latency_ms']} ms",
                           f"VM Performance {round(score)}"]},
             {"id": "g-config", "effect": "symptom", "cause": "A limit, a reservation or an old version on the VM", "object": vm["id"],
              "layer": "vm", "step": "configuration", "flow": "vm-slow, step 6", "kind": "main", "expert": "ruled_out",
              "evidence": ["No limit, normal shares", f"VMware Tools {vm['tools_version']}"]}]
    if g["guest_os_performance"] >= 75 and score >= 75:
        links.append({"id": "g-outside", "effect": "symptom", "cause": "Nothing in vSphere explains it: the application or a dependency",
                      "object": vm["id"], "layer": "vm", "step": "log", "flow": "vm-slow, step 8", "kind": "main", "expert": "confirmed",
                      "evidence": ["No contention, normal queues, clean configuration, no known bug, no event in the window"]})
    return links


def _chain(case: dict, E, now: datetime, act: dict) -> list:
    s = _scenario_story(case, act)
    if s and s.get("plant", {}).get("chain"):
        return [dict(x) for x in s["plant"]["chain"]]
    vm = E.nodes.get(case["object"])
    if vm and vm["kind"] == "vm":
        return _generic_chain(E, vm, now, act)
    return []


# ---------------------------------------------------------------- the cases

def _planted(now: datetime, act: dict) -> list:
    out = []
    l2s = act.get("L-2")
    if l2s:
        c = l2s["complaint"]
        out.append({"id": "case-sg-app-117", "trigger": "complaint", "object": l2s["objects"]["vm"], "symptom": "slow",
                    "title": "Payments screens slow on sg-app-117", "opened_at": generator.rel(c["opened"], now).isoformat(),
                    "opened_by": "l2-engineer-2", "window_from": generator.rel(c["fine_until"], now).isoformat(),
                    "complaint": {"requester": c["requester"], "via": None, "since": generator.rel(c["since"], now).isoformat(),
                                  "fine_until": generator.rel(c["fine_until"], now).isoformat(), "already_checked": c["already_checked"]},
                    "planted": True, "proposed_default": len(l2s["plant"]["chain"])})
    t2 = act.get("T-2")
    if t2:
        e = t2["plant"]["escalated"]
        out.append({"id": "case-inc-tk-s-03", "trigger": "escalation", "incident": "inc-tk-s-03", "object": t2["objects"]["cluster"],
                    "symptom": "slow", "title": "Every web application is slow: TK-S-03 not serving its VMs well",
                    "opened_at": generator.rel(e["at"], now).isoformat(), "opened_by": e["by"],
                    "window_from": generator.rel(t2["plant"]["cluster_performance"]["before"]["until"], now).isoformat(),
                    "escalation": {"by": e["by"], "route": e["route"], **t2["plant"]["l1_evidence"]}, "planted": True})
    return out


def _from_noc(now: datetime, enable=()) -> list:
    """An escalation from the NOC is a case as soon as L1 escalates it (D-040)."""
    out = []
    nd = noc.build(now, enable)
    for iid in noc.STATE.escalated:
        d = noc.incident_detail(nd, iid)
        if not d:
            continue
        ev = {"by": next((h["actor_human"] for h in d["history"] if h["action"] == "escalate"), "operator-1"), "route": d["escalation_route"],
              "sop_steps": [{"text": s["text"], "result": s.get("result")} for s in d["sop"]["steps"] if s.get("result")],
              "l1_actions": [{"action": h["action"], "target": h["target"], "by": h["actor_human"], "after": h["after"]}
                             for h in d["history"] if h["action"] not in ("agent_draft", "escalate") + CASE_WORK],
              "victims": [], "villains": []}
        if iid == "inc-fr-s-02":
            ev["villains"] = [{"vm": "fr-bat-017", "class": "bronze", "environment": "production", "cpu_usage_percent": 95.0, "vcpu": 16, "cpu_ready_percent": 1.2}]
            ev["victims"] = [{"vm": vm, "cpu_ready_percent": r, "co_stop_percent": c, "vm_performance": p}
                             for vm, r, c, p in (("fr-app-101", 9.8, 1.1, 31), ("fr-app-114", 8.1, 0.9, 36), ("fr-db-022", 7.4, 0.6, 41))]
        at = next((h["at"] for h in d["history"] if h["action"] == "escalate"), now.isoformat())
        out.append({"id": f"case-{iid}", "trigger": "escalation", "incident": iid, "object": d["root_object"], "symptom": "slow",
                    "title": f"{d['title']}: {d['root_object']}", "opened_at": at, "opened_by": ev["by"],
                    "window_from": d["opened_at"] if isinstance(d["opened_at"], str) else d["opened_at"].isoformat(),
                    "escalation": ev, "planted": False})
    return out


def all_cases(now: datetime, enable=()) -> list:
    act = X.active_scenario_stories(enable)
    cases = {c["id"]: c for c in _planted(now, act) + _from_noc(now, enable)}
    cases.update({cid: dict(c) for cid, c in STATE.cases.items()})
    return list(cases.values())


def get(now: datetime, cid: str, enable=()) -> dict | None:
    return next((c for c in all_cases(now, enable) if c["id"] == cid), None)


def _links_state(case: dict, chain: list) -> list:
    n = STATE.proposed.get(case["id"], case.get("proposed_default", 0))
    out = []
    for link in chain[:n]:
        d = STATE.links.get(case["id"], {}).get(link["id"], {})
        out.append({**{k: v for k, v in link.items() if k != "expert"}, "state": d.get("state", "proposed"),
                    "decided_by": d.get("by"), "reason": d.get("reason")})
    return out


def summary(now: datetime, case: dict, E, act: dict) -> dict:
    chain = _chain(case, E, now, act)
    links = _links_state(case, chain)
    n = X.node(E, case["object"])
    return {"id": case["id"], "trigger": case["trigger"], "object": case["object"], "object_kind": n["kind"] if n else None,
            "path": [p["name"] for p in X.path(E, X.view_of(E, case["object"]), case["object"])] if n else [],
            "symptom": case["symptom"], "title": case["title"], "opened_at": case["opened_at"], "opened_by": case["opened_by"],
            "state": "closed" if case["id"] in STATE.closures else "open",
            "links": {"confirmed": sum(1 for x in links if x["state"] == "confirmed"),
                      "proposed": sum(1 for x in links if x["state"] == "proposed"),
                      "ruled_out": sum(1 for x in links if x["state"] == "ruled_out")}}


def list_cases(now: datetime, node_id: str = "estate", enable=()) -> list:
    E, act = X.estate(tuple(enable)), X.active_scenario_stories(enable)
    rows = []
    for c in all_cases(now, enable):
        if node_id != "estate" and not (X.node(E, c["object"]) and (c["object"] == node_id or node_id in M.ancestors(E, c["object"]))):
            continue
        rows.append(summary(now, c, E, act))
    rows.sort(key=lambda r: (r["state"] != "open", r["opened_at"]), reverse=False)
    opens = sorted([r for r in rows if r["state"] == "open"], key=lambda r: r["opened_at"], reverse=True)
    closed = sorted([r for r in rows if r["state"] == "closed"], key=lambda r: r["opened_at"], reverse=True)
    return opens + closed


def open_counts(now: datetime, enable=()) -> dict:
    """Open cases per node, counted on the object and every node above it (the tree's badges)."""
    E = X.estate(tuple(enable))
    out = {}
    for c in all_cases(now, enable):
        if c["id"] in STATE.closures or not X.node(E, c["object"]):
            continue
        for a in M.ancestors(E, c["object"]) | {c["object"]}:
            out[a] = out.get(a, 0) + 1
    return out


def _layers(case, E, now, act, scenario_story) -> list:
    if scenario_story and scenario_story.get("plant", {}).get("layers"):
        L = scenario_story["plant"]["layers"]
        return [{"layer": k, **L[k]} for k in LAYERS if k in L]
    vm = E.nodes.get(case["object"])
    if not vm or vm["kind"] != "vm":
        return []
    score = M.perf_score(E, vm, now, "24h")
    g = M.guest_os_values(vm, act)
    host, cl = E.nodes[vm["host"]], E.nodes[vm["cluster"]]
    hs, cs = M.perf_score(E, host, now, "24h"), M.perf_score(E, cl, now, "24h")
    v = M.vm_values(vm, score, act)
    w = lambda ok: "clear" if ok else "waiting"
    return [{"layer": "guest_os", "verdict": w(g["guest_os_performance"] >= 75), "values": f"Run queue {g['run_queue_per_vcpu']} per vCPU; paging {g['paging_per_s']} per second"},
            {"layer": "vm", "verdict": w(score >= 75), "values": f"VM Performance {round(score)}; CPU Ready {v['cpu_ready_percent']}%"},
            {"layer": "host", "verdict": w(hs >= 75), "values": f"{host['id']}: ESXi Performance {round(hs)}"},
            {"layer": "cluster", "verdict": w(cs >= 75), "values": f"{cl['id']}: Cluster Performance {round(cs)}"},
            {"layer": "storage", "verdict": w(v["disk_latency_ms"] < 20), "values": f"Disk latency {v['disk_latency_ms']} ms"},
            {"layer": "network", "verdict": "clear", "values": "No drops"}]


def _hand_over(layers: list) -> str | None:
    v = {x["layer"]: x["verdict"] for x in layers}
    if v.get("guest_os") == "waiting" and v.get("vm") == "clear":
        return "The cause is inside the Guest OS. Hand this evidence to the Windows or Linux team."
    if layers and all(x["verdict"] in ("clear", "not_read") for x in layers):
        return "Every layer is clear. Hand this to the application owner, with what was checked: vSphere has no counter for what is left."
    return None


def _timeline(case, E, now, act, scenario_story, links) -> list:
    out = []
    for e in (scenario_story or {}).get("plant", {}).get("events", []):
        out.append({"at": generator.rel(e["at"], now).isoformat(), "object": e["object"], "kind": e["kind"], "text": e["text"],
                    "explained_by": e.get("explained_by")})
    if not scenario_story:
        out.append({"at": case.get("complaint", {}).get("since") or case["opened_at"], "object": case["object"], "kind": "complaint",
                    "text": "Symptom reported", "explained_by": None})
    objs = {case["object"]} | {x["object"] for x in links}
    for r in noc.STATE.history:
        if r["action"] in CASE_WORK or r["target"].startswith(case["id"]):
            continue  # the case's own work is on the case, not on the estate's timeline
        if r["target"] in objs or (case.get("incident") and r.get("incident") == case.get("incident")):
            out.append({"at": r["at"], "object": r["target"], "kind": "pcm_action", "text": f"{r['action'].replace('_', ' ')}: {r['after']}",
                        "explained_by": "pcm_action"})
    for c in l2.calendar(now):
        if c["location"] is None or c["location"] == (X.node(E, case["object"]) or {}).get("location"):
            if datetime.fromisoformat(c["starts_at"]) <= now:
                out.append({"at": c["starts_at"], "object": c["location"] or "all", "kind": "calendar", "text": c["note"], "explained_by": None})
    out.append({"at": case["opened_at"], "object": case["object"], "kind": "case", "text": f"Case opened ({case['trigger']}) by {case['opened_by']}",
                "explained_by": None})
    out.sort(key=lambda e: e["at"])
    lb = now - timedelta(days=generator.load_spec()["settings"].get("l2.timeline_lookback_days", 42))
    return [e for e in out if datetime.fromisoformat(e["at"]) >= lb]


def detail(now: datetime, cid: str, enable=()) -> dict | None:
    E, act = X.estate(tuple(enable)), X.active_scenario_stories(enable)
    case = get(now, cid, enable)
    if not case:
        return None
    scenario_story = _scenario_story(case, act)
    chain = _chain(case, E, now, act)
    links = _links_state(case, chain)
    layers = _layers(case, E, now, act, scenario_story)
    vm = E.nodes.get(case["object"])
    realms = None
    if vm and vm["kind"] == "vm":
        score = M.perf_score(E, vm, now, "24h")
        g = M.guest_os_values(vm, act)
        realms = {"vm": {"status": X.status_of(score), **M.vm_values(vm, round(score, 1), act)},
                  "guest_os": {"status": X.status_of(g["guest_os_performance"]), **g}}
    we = (scenario_story or {}).get("plant", {}).get("who_else")
    if not we and vm and vm["kind"] == "vm":
        vs = M._vm_scores(tuple(enable), M._key(now), "24h")
        same = [x for h in E.nodes[vm["cluster"]]["hosts"] for x in h["vms"] if x != vm["id"] and vs[x] < 75]
        we = {"test": f"another VM in {vm['cluster']} below the green line", "objects": same[:10], "count": len(same)}
    out = summary(now, case, E, act)
    out.update({"window_from": case["window_from"], "window_to": now.isoformat(), "complaint": case.get("complaint"),
                "escalation": case.get("escalation"), "incident": case.get("incident"), "finding": case.get("finding"),
                "accepted": STATE.accepted.get(cid), "chain": links, "chain_total": len(chain),
                "more_to_propose": len(links) < len(chain), "layers": layers, "hand_over": _hand_over(layers), "realms": realms,
                "timeline": _timeline(case, E, now, act, scenario_story, links), "who_else": we, "closure": STATE.closures.get(cid),
                "root_cause_prefill": "; ".join(x["cause"] for x in links if x["state"] == "confirmed" and x["kind"] == "main"
                                                and not any(y["effect"] == x["id"] and y["state"] == "confirmed" for y in links)),
                "detections": list(DETECTIONS)})
    if case.get("finding"):
        f = next((x for x in M.findings(now, enable) if x["id"] == case["finding"]), None)
        out["finding_detail"] = f and {k: f[k] for k in ("id", "summary", "pillar", "window", "object", "evidence")}
    return out


# ---------------------------------------------------------------- actions

def log_validation(message: str, settings: dict) -> dict:
    """l2.log_validation: the count on healthy objects over the last 5 working days."""
    n = NOISE.get(message.strip().lower(), int(X._h(message.strip().lower()) * 7))
    return {"message": message, "healthy_count_5_days": n, "limit": settings["l2.log_noise_max"],
            "noise": n > settings["l2.log_noise_max"]}


def act(now: datetime, path: list, body: dict, enable=()) -> tuple[int, dict]:
    with STATE.lock, noc.STATE.lock, l2.STATE.lock:
        out = _act(now, path, body, enable)
        STATE.save()
        noc.STATE.save()
        l2.STATE.save()
    return out


def _act(now, path, body, enable):
    st = generator.load_spec()["settings"]
    human = body.get("actor_human") or "l2-engineer-1"
    rec = lambda a, target, reason, before, after, **k: noc.record(a, target, human, reason, before, after, now, **k)
    E, act_ = X.estate(tuple(enable)), X.active_scenario_stories(enable)
    if path == []:  # POST /api/l2/cases: open a case
        trig = body.get("trigger")
        if trig == "complaint":
            vm_id = (body.get("vm") or "").strip()
            n = X.node(E, vm_id)
            if n and n["kind"] == "guest_os":
                vm_id, n = n["vm"], E.nodes[n["vm"]]
            if not n or n["kind"] != "vm":
                return 400, {"error": "Name a VM. A complaint about an application is logged against its VMs.", "field": "vm"}
            for f in ("requester", "symptom", "since"):
                if not body.get(f):
                    return 400, {"error": f"Missing: {f}.", "field": f}
            if body["symptom"] not in ("slow", "down"):
                return 400, {"error": "symptom must be slow or down", "field": "symptom"}
            try:
                since = _parse(body["since"], now)
                fine = _parse(body["fine_until"], now) if body.get("fine_until") else since - timedelta(hours=1)
            except ValueError:
                return 400, {"error": "since and fine until must be dates and times", "field": "since"}
            STATE.seq += 1
            cid = f"case-{STATE.seq:03d}"
            checked = body.get("already_checked") or []
            if isinstance(checked, str):
                checked = [x.strip() for x in checked.splitlines() if x.strip()]
            STATE.cases[cid] = {"id": cid, "trigger": "complaint", "object": vm_id, "symptom": body["symptom"],
                                "title": body.get("title") or f"{'Slow' if body['symptom'] == 'slow' else 'Down'}: {vm_id}, reported by {body['requester']}",
                                "opened_at": now.isoformat(), "opened_by": human, "window_from": fine.isoformat(),
                                "complaint": {"requester": body["requester"], "via": body.get("via"), "since": since.isoformat(),
                                              "fine_until": fine.isoformat(), "already_checked": checked}}
            rec("open_case", cid, f"complaint about {vm_id}", "-", "open")
            return 200, {"id": cid}
        if trig == "finding":
            f = next((x for x in M.findings(now, enable) if x["id"] == body.get("finding")), None)
            if not f:
                return 400, {"error": "No such finding.", "field": "finding"}
            if f["outcome"] != "problem":
                return 400, {"error": "This finding is a risk or an opportunity: it goes to Improve, not to a case."}
            if f.get("case"):
                return 200, {"id": f["case"]}
            STATE.seq += 1
            cid = f"case-{STATE.seq:03d}"
            obj = f["object"]
            s = act_.get(f.get("scenario_story") or "")
            if s and s["objects"].get("vm"):
                obj = s["objects"]["vm"]
            STATE.cases[cid] = {"id": cid, "trigger": "finding", "finding": f["id"], "object": obj, "symptom": "slow",
                                "title": f["summary"].split(". ")[0], "opened_at": now.isoformat(), "opened_by": human,
                                "window_from": (now - timedelta(hours=X.WINDOW_HOURS[f["window"]])).isoformat()}
            rec("open_case", cid, f"finding {f['id']}", "-", "open")
            return 200, {"id": cid}
        return 400, {"error": "trigger must be complaint or finding (an escalation comes from L1)", "field": "trigger"}
    cid = path[0]
    case = get(now, cid, enable)
    if not case:
        return 404, {"error": "No such case"}
    verb = path[1] if len(path) > 1 else None
    chain = _chain(case, E, now, act_)
    if verb == "propose":
        n = STATE.proposed.get(cid, case.get("proposed_default", 0))
        if n >= len(chain):
            return 200, {"link": None, "message": "Agent E2 has nothing more to propose from its flows."}
        STATE.proposed[cid] = n + 1
        link = chain[n]
        rec("agent_propose", cid, f"{link['flow']}: {link['cause']}", "-", "proposed", actor_agent="agent-e2")
        return 200, {"link": {k: v for k, v in link.items() if k != "expert"} | {"state": "proposed"}}
    if verb == "links" and len(path) == 4:
        lid, what = path[2], path[3]
        shown = {x["id"] for x in _links_state(case, chain)}
        if lid not in shown:
            return 404, {"error": "No such link on this case"}
        if what == "confirm":
            STATE.links.setdefault(cid, {})[lid] = {"state": "confirmed", "by": human}
            rec("confirm_link", f"{cid}/{lid}", "", "proposed", "confirmed")
            return 200, {"state": "confirmed"}
        if what == "rule-out":
            if not body.get("reason"):
                return 400, {"error": "A reason is required to rule a link out: it stays visible, with why."}
            STATE.links.setdefault(cid, {})[lid] = {"state": "ruled_out", "by": human, "reason": body["reason"]}
            rec("rule_out_link", f"{cid}/{lid}", body["reason"], "proposed", "ruled out")
            return 200, {"state": "ruled_out"}
    if verb in ("accept", "reject"):
        if case["trigger"] != "escalation":
            return 400, {"error": "Only an escalation is accepted or rejected."}
        if verb == "reject" and not body.get("reason"):
            return 400, {"error": "A reason is required: a rejected escalation points to a gap in the SOP."}
        STATE.accepted[cid] = {"state": "accepted" if verb == "accept" else "rejected", "by": human, "reason": body.get("reason")}
        rec(f"{verb}_escalation", cid, body.get("reason", ""), "escalated", verb + "ed")
        return 200, STATE.accepted[cid]
    if verb == "close":
        need = ("root_cause", "corrective_action", "detection", "detection_note")
        missing = [k for k in need if not body.get(k)]
        if missing:
            return 400, {"error": f"Missing: {', '.join(missing).replace('_', ' ')}. A case closes with a cause, a fix and a detection decision."}
        if body["detection"] not in DETECTIONS:
            return 400, {"error": "detection must be one of " + ", ".join(DETECTIONS)}
        links = _links_state(case, chain)
        if not any(x["state"] == "confirmed" and x["kind"] == "main" for x in links):
            return 400, {"error": "Confirm at least one main link before closing: the root cause is a confirmed link of the chain."}
        STATE.closures[cid] = {k: body[k] for k in need} | {"by": human, "at": now.isoformat()}
        if case.get("incident"):
            noc.STATE.closed[case["incident"]] = body["root_cause"]
            l2.STATE.closures[case["incident"]] = {k: body[k] for k in need} | {"by": human}
        rec("close_case", cid, body["root_cause"], "open", "closed", incident=case.get("incident"))
        return 200, {"state": "closed"}
    if verb == "draft":
        confirmed = [x for x in _links_state(case, chain) if x["state"] == "confirmed"]
        vocab = yaml.safe_load((l2.SPEC / "vocabulary.yaml").read_text())
        facts = {"case": {k: case.get(k) for k in ("title", "object", "symptom", "trigger")}, "confirmed_links": confirmed}
        template = ("Draft by Agent E2, to review: " + case["object"] + ": "
                    + ("; ".join(f"{x['cause']} ({x['kind']})" for x in confirmed) if confirmed else "no confirmed link yet")
                    + ". Corrective action and detection: to decide.")
        out = agent_e2.draft_facts(facts, "rca_draft", st, vocab["avoided"], template)
        r = rec("agent_draft", cid, "rca_draft", "-", out["source"], actor_agent="agent-e2", incident=case.get("incident"))
        return 200, {**out, "record": r}
    return 404, {"error": "unknown action"}


def _parse(v: str, now: datetime) -> datetime:
    if v.startswith("now"):
        return generator.rel(v, now)
    d = datetime.fromisoformat(v)
    return d if d.tzinfo else d.replace(tzinfo=now.tzinfo)


def rule_drafts(now: datetime, enable=()) -> list:
    out = []
    for c in all_cases(now, enable):
        cl = STATE.closures.get(c["id"])
        if cl and cl["detection"] != "none_with_reason":
            out.append({"case": c["id"], "title": c["title"], "detection": cl["detection"], "note": cl["detection_note"],
                        "closed_by": cl["by"], "state": "published" if c["id"] in STATE.drafts_published else "draft"})
    return out
