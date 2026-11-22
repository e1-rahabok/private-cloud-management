"""Agent E2 in the L2 workspace: the mark's health check and the panel's question (D-078, D-097).

GENERATED from spec/workspaces/l2/frame.md (Agent E2 mark, Agent E2 panel), monitor.md, case.md and spec/api/l2.yaml.
Do not edit by hand (D-070).

PCM owns the data: the facts are rebuilt here from what was clicked, never taken from the browser.
Agent E2 explains; it never decides (L2 design, 8). Every question is recorded with both identity fields (D-050).
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta

from . import agent_e2, generator, l2, l2_cases as C, l2_estate as X, l2_monitor as M, noc

KINDS = ("page", "vm_layer", "metric", "kpi", "finding", "case", "link", "layer")
HEALTH_SECONDS = 3  # spec: never cached longer than 30 seconds
_HEALTH: dict = {}
HUMAN = "l2-engineer-1"
PNAME = {"summary": "Summary", "availability": "Availability", "performance": "Performance", "capacity": "Capacity",
         "security": "Security", "configuration": "Configuration", "inventory": "Inventory"}
WNAME = {"1h": "Last hour", "24h": "Last 24 hours", "7d": "Last 7 days", "30d": "Last 30 days", "1y": "Last year"}
LAYER = {"guest_os": "Guest OS", "virtual_motherboard": "Virtual Motherboard", "vm": "VM", "host": "Host", "cluster": "Cluster",
         "storage": "Storage", "network": "Network"}


def service_url(settings: dict) -> str:
    return os.environ.get("PCM_AGENT_E2_URL") or settings["agent_e2.service_url"]


def health(settings: dict) -> dict:
    """GET /v1/health with a 2-second limit. Kept a few seconds so a page of marks asks once."""
    url = service_url(settings)
    hit = _HEALTH.get(url)
    if hit and time.monotonic() - hit[0] < HEALTH_SECONDS:
        return hit[1]
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/v1/health", timeout=2) as r:
            body = json.loads(r.read())
        out = {"available": bool(body.get("ok")), "model": body.get("model")}
    except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, OSError):
        out = {"available": False, "model": None}
    _HEALTH[url] = (time.monotonic(), out)
    return out


# ---------------------------------------------------------------- the facts, rebuilt from the context

def _obj(E, view: str, nid: str) -> dict | None:
    n = X.node(E, nid)
    if n is None:
        return None
    v = X.view_of(E, nid, view)
    return {"id": n["id"], "name": n["name"], "kind": n["kind"], "path": [p["name"] for p in X.path(E, v, nid)]}


def _calendar(now: datetime, window: str, enable) -> list:
    start = now - timedelta(hours=X.WINDOW_HOURS[window])
    keep = ("kind", "location", "starts_at", "ends_at", "note")
    return [{k: c[k] for k in keep} for c in l2.calendar(now, enable)
            if datetime.fromisoformat(c["starts_at"]) <= now and datetime.fromisoformat(c["ends_at"]) >= start]


def _finding(f: dict) -> dict:
    keep = ("id", "severity", "pillar", "window", "kind", "object", "object_name", "path", "summary", "evidence", "outcome", "explained_by")
    return {k: f.get(k) for k in keep if f.get(k) is not None}


def _metric(m: dict, full: bool) -> dict:
    out = {"name": m["label"], "unit": m["unit"].strip(), "better": m["better"], "now": m["now"],
           "worst": m["worst"], "percentile_95": m["percentile_95"]}
    if full:
        # Values only, oldest first, one per point_minutes from first_point: a timestamp per point would triple the size.
        out["point_minutes"] = m["minutes"]
        out["first_point"] = m["points"][0]["t"] if m["points"] else None
        out["values"] = [p["v"] for p in m["points"]]
        out["each_point_holds"] = "the worst value inside it"
    return out


def _layer(x: dict) -> dict:
    """A layer's status and its figures, without points."""
    return {"layer": LAYER[x["key"]], "status": x["status"], "metrics": [_metric(m, False) for m in x["metrics"]]}


def facts_for(now: datetime, ctx: dict, enable=()) -> tuple[int, dict]:
    """Returns (status, {facts, label, finding?}) or (status, {error}). The facts open with the screen (D-102)."""
    code, got = _facts(now, ctx, enable)
    if code == 200:
        got["facts"] = {"screen": screen(ctx, got), **got["facts"]}
    return code, got


# ---------------------------------------------------------------- the screen (D-102): what the person sees, not the data

CLICKED = {"page": "the E2 mark in the top bar: a question about the whole page",
           "finding": "the E2 mark on a finding row", "case": "the E2 mark on the case",
           "link": "the E2 mark on a link of the case's chain", "layer": "the E2 mark on a layer of the case"}
# Where a KPI goes further, and what PCM does not show yet (frame.md, Agent E2 panel).
DRILL = {
    "performance": ("Performance", "Cluster Performance and Cluster Risk over the window, then the cluster's hosts worst first, "
                    "each with its score over the window and over the last hour",
                    "the 9 sub-metrics of Cluster Performance: no PCM page shows them yet"),
    "risk": ("Performance", "Cluster Performance and Cluster Risk over the window, then the cluster's hosts worst first, "
             "each with its score over the window and over the last hour",
             "the parts of Cluster Risk: no PCM page shows them yet"),
    "consumption": ("Capacity", "What makes up Consumption: each part as % of usable capacity, over the window", None),
}


def _minutes(times: list) -> int | None:
    try:
        return int((datetime.fromisoformat(times[1]) - datetime.fromisoformat(times[0])).total_seconds() // 60)
    except (IndexError, TypeError, ValueError):
        return None


def _chart(name: str, window: str, minutes, banded: bool) -> str:
    every = f", one point every {minutes} minutes, each point the worst value inside it" if minutes else ""
    band = ", each in its band colour" if banded else ""  # a KPI has bands; a counter has none (D-100)
    return f"a trend chart of {name} over the {window.lower()}{every}; beside it Now, Worst and 95th percentile{band}"


def screen(ctx: dict, got: dict) -> dict:
    """What the person sees: who asks, the page, what was clicked, what that card shows, and for a KPI where to look next."""
    kind, f = ctx.get("kind") or "page", got["facts"]
    o = f.get("object") or {}
    page = got["label"] if kind in ("case", "link", "layer") else \
        f"{o.get('name')} ({o.get('kind')}) · {PNAME.get(ctx.get('pillar'), f.get('pillar'))} tab · {f.get('window')}"
    out = {"workspace": "L2 Platform", "asked_by": "an L2 platform engineer, who typed only the question", "page": page,
           "clicked": CLICKED.get(kind, "")}
    if kind == "kpi":
        k = f["asked_about_kpi"]
        out["clicked"] = f"the E2 mark on the {k['label']} chart"
        out["card_shows"] = _chart(k["label"], f["window"], _minutes([p[0] for p in k["points"][:2]]), True)
        cl = f.get("cluster")
        if cl and o.get("kind") != "cluster":
            out["kpi_belongs_to"] = f"the cluster {cl}, not the {o.get('kind')} {o.get('name')}: it is the cluster's KPI, shown on this page"
        d = DRILL.get(ctx.get("metric"))
        if d and cl:
            out["drill_down"] = {"page": f"{cl} (cluster) · {d[0]} tab · {f['window']}", "shows": d[1]}
            if d[2]:
                out["drill_down"]["not_shown_yet"] = d[2]
    elif kind == "metric":
        m = f["asked_about_metric"]
        out["clicked"] = f"the E2 mark on the {m['name']} chart, in the {f['layer']} layer"
        out["card_shows"] = _chart(m["name"], f["window"], m.get("point_minutes"), m.get("unit") == "%" and "Performance" in m["name"])
    elif kind == "vm_layer":
        out["clicked"] = f"the E2 mark on the {f['asked_about_layer']['layer']} layer"
        out["card_shows"] = "the layer's status and one trend chart per metric, each with Now, Worst and 95th percentile"
    return out


def _facts(now: datetime, ctx: dict, enable=()) -> tuple[int, dict]:
    kind = ctx.get("kind") or "page"
    if kind not in KINDS:
        return 400, {"error": "context kind must be one of " + ", ".join(KINDS)}
    E = X.estate(tuple(enable))
    window = ctx.get("window") if ctx.get("window") in X.WINDOWS else "24h"
    view = ctx.get("view") or "compute"
    if kind in ("case", "link", "layer"):
        d = C.detail(now, ctx.get("case") or "", enable)
        if not d:
            return 404, {"error": "no such case"}
        keep = ("id", "title", "symptom", "trigger", "object", "path", "state", "window_from", "complaint", "escalation", "finding_detail",
                "chain", "layers", "hand_over", "realms", "timeline", "who_else")
        facts = {"case": {k: d.get(k) for k in keep if d.get(k) is not None}}
        label = f"Case: {d['title']}"
        if kind == "link":
            link = next((x for x in d["chain"] if x["id"] == ctx.get("link")), None)
            if not link:
                return 404, {"error": "no such link in this case"}
            facts["asked_about_link"] = link
            label += f" · link: {link['cause']}"
        if kind == "layer":
            layer = next((x for x in d["layers"] if x["layer"] == ctx.get("layer")), None)
            if not layer:
                return 404, {"error": "no such layer in this case"}
            facts["asked_about_layer"] = layer
            label += f" · {LAYER.get(layer['layer'], layer['layer'])} layer"
        return 200, {"facts": facts, "label": label}
    if kind == "finding":
        f = next((x for x in M.findings(now, enable) if x["id"] == ctx.get("finding")), None)
        if not f:
            return 404, {"error": "no such finding"}
        return 200, {"facts": {"finding": _finding(f), "calendar_in_window": _calendar(now, f.get("window") or "24h", enable)},
                     "label": f"Finding: {f['object_name']} · {PNAME.get(f['pillar'], f['pillar'])}", "finding": f}
    o = _obj(E, view, ctx.get("object") or "estate")
    if o is None:
        return 404, {"error": "no such object"}
    pillar = ctx.get("pillar") if ctx.get("pillar") in PNAME else "summary"
    where = f"{o['name']} · {PNAME[pillar]} · {WNAME[window]}"
    base = {"object": o, "pillar": PNAME[pillar], "window": WNAME[window], "calendar_in_window": _calendar(now, window, enable)}
    if kind == "metric":
        pv = M.pillar_view(now, view, o["id"], "performance", window, enable=enable)
        layers = (pv or {}).get("layers") or []
        layer = next((x for x in layers if x["key"] == ctx.get("layer")), None)
        m = next((x for x in (layer or {}).get("metrics", []) if x["key"] == ctx.get("metric")), None)
        if not m:
            return 404, {"error": "no such metric on this object"}
        others = {LAYER[x["key"]]: {"status": x["status"], "metrics": [_metric(y, False) for y in x["metrics"] if y is not m]} for x in layers}
        facts = {**base, "pillar": "Performance", "layer": LAYER[layer["key"]], "layer_status": layer["status"],
                 "asked_about_metric": _metric(m, True), "other_metrics": others}
        return 200, {"facts": facts, "label": f"{m['label']} · {o['name']} · Performance · {WNAME[window]}"}
    if kind == "vm_layer":
        pv = M.pillar_view(now, view, o["id"], "performance", window, enable=enable)
        layers = (pv or {}).get("layers") or []
        layer = next((x for x in layers if x["key"] == ctx.get("layer")), None)
        if not layer:
            return 404, {"error": "no such layer on this object"}
        facts = {**base, "pillar": "Performance", "asked_about_layer": {"layer": LAYER[layer["key"]], "status": layer["status"],
                                                                      "metrics": [_metric(m, True) for m in layer["metrics"]]},
                 "other_layers": [_layer(x) for x in layers if x is not layer]}
        return 200, {"facts": facts, "label": f"{LAYER[layer['key']]} layer · {o['name']} · Performance · {WNAME[window]}"}
    if kind == "kpi":
        pv = M.pillar_view(now, view, o["id"], "capacity", window, enable=enable)
        cap = (pv or {}).get("capacity") or {}
        k = next((x for x in cap.get("kpis") or [] if x["key"] == ctx.get("metric")), None)
        if not k:
            return 404, {"error": "no such KPI on this object"}
        kpi = {key: k.get(key) for key in ("label", "better", "now", "worst", "percentile_95", "check_value", "closure_levels")}
        kpi["unit"] = "%"
        kpi["points"] = [[p["t"], p["v"]] for p in k.get("points", [])]
        facts = {**base, "pillar": "Capacity", "cluster": cap.get("cluster"), "check": cap.get("check"),
                 "contention_now": cap.get("contention_now"), "asked_about_kpi": kpi,
                 "other_kpis": [{key: x.get(key) for key in ("label", "now", "worst", "percentile_95", "check_value")} for x in cap["kpis"] if x is not k]}
        return 200, {"facts": facts, "label": f"{k['label']} · {o['name']} · Capacity · {WNAME[window]}"}
    # page: what the page shows, so an overall question is answered from the numbers on screen (frame.md, Agent E2 panel)
    pv = M.pillar_view(now, view, o["id"], pillar, window, enable=enable) if pillar != "summary" else None
    found = M.findings_under(now, o["id"], enable, None if pillar == "summary" else pillar, window)
    facts = {**base, "status": (pv or {}).get("status"), "score": (pv or {}).get("score"),
             "findings": [_finding(f) for f in found[:10]],
             "worst_children": [{k: c.get(k) for k in ("name", "kind", "status", "score")} for c in ((pv or {}).get("children") or [])[:10]]}
    if pillar == "summary":
        sm = M.summary(now, view, o["id"], window, enable) or {}
        facts["pillars"] = [{k: x.get(k) for k in ("pillar", "status", "headline", "findings")} for x in sm.get("pillars", [])]
    if (pv or {}).get("layers"):
        facts["layers"] = [_layer(x) for x in pv["layers"]]
    return 200, {"facts": facts, "label": where}


# ---------------------------------------------------------------- object names in the answer become links

_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+")


def links_in(text: str, enable=()) -> list:
    E = X.estate(tuple(enable))
    by_name = {}
    for n in E.nodes.values():
        by_name.setdefault(n["name"].lower(), n)
    out, seen = [], set()
    for t in _TOKEN.findall(text or ""):
        n = by_name.get(t.lower())
        if n and n["id"] not in seen:
            seen.add(n["id"])
            out.append({"name": t, "id": n["id"], "view": X.view_of(E, n["id"])})
    return out


def ask(now: datetime, body: dict, enable=()) -> tuple[int, dict]:
    question = (body.get("question") or "").strip()
    if not question:
        return 400, {"error": "A question is required."}
    ctx = body.get("context") or {"kind": "page"}
    if not isinstance(ctx, dict):
        return 400, {"error": "context must be an object"}
    code, got = facts_for(now, ctx, enable)
    if code != 200:
        return code, got
    settings = generator.load_spec()["settings"]
    turns = [t for t in (body.get("turns") or []) if isinstance(t, str)]
    out = agent_e2.ask_service(service_url(settings), question, got["facts"], "l2", turns=turns or None)
    target = ctx.get("case") or ctx.get("finding") or ctx.get("object") or "estate"
    with noc.STATE.lock:
        rec = noc.record("agent_ask", target, HUMAN, question, ctx.get("kind") or "page", out["source"], now, actor_agent="agent-e2")
        noc.STATE.save()
    f = got.get("finding")
    return 200, {**out, "label": got["label"], "links": links_in(out.get("content", ""), enable) if out["source"] == "service" else [],
                 "finding": {"id": f["id"], "outcome": f.get("outcome")} if f else None, "record": rec}
