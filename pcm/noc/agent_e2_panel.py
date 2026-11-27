"""Agent E2 at the NOC desk: the panel's question, as L1 (D-098).

GENERATED from pcm/noc/spec/pages/desktop.md (Agent E2 mark and panel), incident.md, alerts.md, shift.md and pcm/noc/spec/api.yaml.
Do not edit by hand (D-070).

PCM rebuilds L1's facts on the server: scores from 0 to 100, the SOP and its results, never a raw counter.
Every answer is checked against the NOC vocabulary; one that keeps an avoided word after one more try is not shown.
Agent E2 does not set severity, act outside the SOP or close an alert (NOC design, 3.8).
"""
from __future__ import annotations

from datetime import datetime

import yaml

from ..core import agent_e2, generator
from . import noc
from ..l2.agent_e2_panel import service_url

KINDS = ("page", "tile", "cluster", "incident", "step")
PAGES = {"screens": "Screens", "alerts": "Alerts", "alert": "Incident", "shift": "Shift handover"}
SCREENS = {"up": "Availability", "fast": "Performance", "safe": "Security", "changed": "Volatility", "set_right": "Configuration", "capacity": "Capacity"}
L1_RULE = ("Answer for a Level 1 NOC operator who follows the SOP: plain, short sentences; scores from 0 to 100; "
           "never suggest an action outside the SOP; never use these words: {avoided}.")


def _avoided() -> list:
    return yaml.safe_load((noc.SPEC / "vocabulary.yaml").read_text())["avoided"]


def _tile(t: dict) -> dict:
    """A tile as L1 sees it: no trend points, no raw counter."""
    return {k: v for k, v in t.items() if k not in ("trend",)}


def _cluster(d: dict) -> dict:
    return {"cluster": d["cluster"], "location": d.get("location"), "class": d.get("class"), "status": d["status"],
            "score_now": round(d["score"]), "score_an_hour_ago": round(d["trend"][0]["v"]) if d.get("trend") else None,
            "villains": d.get("villains", []), "victims": d.get("victims", [])}


def facts_for(nd: dict, ctx: dict) -> tuple[int, dict]:
    kind = ctx.get("kind") or "page"
    if kind not in KINDS:
        return 400, {"error": "context kind must be one of " + ", ".join(KINDS)}
    if kind in ("incident", "step"):
        d = noc.incident_detail(nd, ctx.get("incident") or "")
        if not d:
            return 404, {"error": "no such incident"}
        facts = {"incident": agent_e2.facts_for(d)}
        label = f"{d['title']}: {d['root_object']}"
        if kind == "step":
            steps = d["sop"]["steps"]
            i = ctx.get("step")
            if not isinstance(i, int) or not 0 <= i < len(steps):
                return 404, {"error": "no such step"}
            facts["asked_about_step"] = {"number": i + 1, **facts["incident"]["sop_steps"][i]}
            label += f" · SOP step {i + 1}"
        return 200, {"facts": facts, "label": label}
    if kind == "cluster":
        d = noc.cluster_detail(nd, ctx.get("cluster") or "")
        if not d:
            return 404, {"error": "no such cluster"}
        return 200, {"facts": {"cluster": _cluster(d)}, "label": f"{d['cluster']} · Is it fast?"}
    w = noc.wall(nd)
    if kind == "tile":
        screen = w["screens"].get(ctx.get("screen") or "")
        tiles = [t for t in (screen or {}).get("tiles", []) if t.get("location") == ctx.get("location")]
        if not tiles:
            return 404, {"error": "no such tile"}
        return 200, {"facts": {"screen": SCREENS[ctx["screen"]], "tiles": [_tile(t) for t in tiles]},
                     "label": f"{tiles[0]['name']} · {SCREENS[ctx['screen']]}"}
    page = ctx.get("page") or "screens"
    if page not in PAGES:
        return 404, {"error": "no such page"}
    if page == "screens":
        sc = ctx.get("screen") if ctx.get("screen") in SCREENS else "fast"
        s = w["screens"][sc]
        facts = {"page": "Screens", "strip": [{"screen": SCREENS[x["screen"]], "status": x["status"], "in_hand": x.get("in_hand")} for x in w["strip"]],
                 "screen": SCREENS[sc], "tiles": [_tile(t) for t in s["tiles"]], "stale_locations": w.get("stale_locations")}
        return 200, {"facts": facts, "label": f"Screens · {SCREENS[sc]}"}
    if page == "shift":
        s = noc.shift_view(nd)
        return 200, {"facts": {"page": "Shift handover", "shift": {k: s[k] for k in ("region", "shift_ends", "open", "acknowledged", "waiting_on_l2", "limits_expiring")}},
                     "label": "Shift handover"}
    keep = ("id", "severity", "title", "root_object", "location_name", "alert_count", "opened_at", "state", "acknowledged_by")
    return 200, {"facts": {"page": "Alerts", "incidents": [{k: i.get(k) for k in keep} for i in noc.incident_list(nd)]}, "label": "Alerts"}


def ask(nd: dict, body: dict) -> tuple[int, dict]:
    question = (body.get("question") or "").strip()
    if not question:
        return 400, {"error": "A question is required."}
    ctx = body.get("context") or {"kind": "page"}
    if not isinstance(ctx, dict):
        return 400, {"error": "context must be an object"}
    code, got = facts_for(nd, ctx)
    if code != 200:
        return code, got
    st, now = nd["settings"], nd["now"]
    avoided = _avoided()
    turns = [t for t in (body.get("turns") or []) if isinstance(t, str)] or None
    history = agent_e2.history_of(body)
    if history is None:
        return 400, {"error": "history must be a list of {question, answer}."}
    choice = agent_e2.topic_choice_of(body)
    if choice is None:
        return 400, {"error": "topic_choice must be auto, new or continue."}
    rule = L1_RULE.format(avoided=", ".join(avoided))
    url = service_url(generator.load_spec()["settings"])
    out = agent_e2.ask_service(url, f"{question}\n\n{rule}", got["facts"], "l1", turns=turns, history=history, topic_choice=choice)
    if out["source"] == "service":
        bad = agent_e2.avoided_found(((out.get("lead") or "") + "\n" + (out.get("content") or "")).strip(), avoided)
        if bad:  # asked once more, naming the words (D-098)
            again = (f"{question}\n\n{rule}\nYour last answer used {', '.join(bad)}. Say the same without those words, "
                     "in scores from 0 to 100.")
            out = agent_e2.ask_service(url, again, got["facts"], "l1", turns=turns, history=history, topic_choice=choice)
            if out["source"] == "service" and agent_e2.avoided_found(((out.get("lead") or "") + "\n" + (out.get("content") or "")).strip(), avoided):
                out = {**out, "source": "vocabulary", "content": "", "lead": "", "computed": [], "questions": []}
    target = ctx.get("incident") or ctx.get("cluster") or ctx.get("location") or ctx.get("page") or "noc"
    human = body.get("actor_human") or st["noc.actor_default"]
    with noc.STATE.lock:
        rec = noc.record("agent_ask", target, human, question, ctx.get("kind") or "page", out["source"], now,
                         actor_agent="agent-e2", incident=ctx.get("incident"))
        noc.STATE.save()
    return 200, {**out, "label": got["label"], "links": [], "record": rec}
