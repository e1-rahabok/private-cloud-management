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
    """Returns (status, {facts, label, finding?}) or (status, {error}). The facts open with the screen (D-103)."""
    code, got = _facts(now, ctx, enable)
    if code == 200:
        got["facts"] = {"screen": screen(ctx, got), **got["facts"]}
    return code, got


# ---------------------------------------------------------------- the screen (D-103): what the person sees, not the data

CLICKED = {"page": "the E2 mark in the top bar: a question about the whole page",
           "finding": "the E2 mark on a finding row", "case": "the E2 mark on the case",
           "link": "the E2 mark on a link of the case's chain", "layer": "the E2 mark on a layer of the case"}
# Where a KPI goes further, and what PCM does not show yet (frame.md, Agent E2 panel). The parts of Cluster Performance
# and Cluster Risk are in the Details fold under each KPI on the cluster's Performance tab (D-106, D-111).
DRILL = {
    "performance": ("Performance", "Cluster Performance and Cluster Risk over the window; under Cluster Performance the fold "
                    "Details (closed until opened): one chart per part, the 9 parts with Now, Worst and 95th percentile (lower is better for every part); "
                    "then the cluster's hosts worst first, each with its score over the window and over the last hour", None),
    "risk": ("Performance", "Cluster Performance and Cluster Risk over the window; under Cluster Risk the fold Details (closed "
             "until opened): one chart per part, with Now, Worst and 95th percentile; then the cluster's hosts worst first, "
             "each with its score over the window and over the last hour", None),
    "consumption": ("Capacity", "What makes up Consumption: each part as % of usable capacity, over the window", None),
}
KPI_KEY = {"performance": "cluster_performance", "risk": "cluster_risk"}


def _median(xs: list):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else round((xs[n // 2 - 1] + xs[n // 2]) / 2, 3)


def parts_at_worst(E, now: datetime, cluster: str, metric: str, window: str, enable=()) -> dict | None:
    """The parts of a cluster KPI at the KPI's worst point of the window (D-111): the values the Details fold shows at
    that time, each with the part's median and worst of the window. Names are the Agent E2 catalog's. No score, no
    ranking, no verdict: scoring the parts is domain knowledge, Agent E2's (D-078)."""
    n = X.node(E, cluster) if cluster else None
    key = KPI_KEY.get(metric)
    if n is None or key is None:
        return None
    return _parts(n, next((x for x in M.object_kpis(E, n, now, window, enable) if x["key"] == key), None))


def _parts(n: dict, k: dict | None) -> dict | None:
    """The parts of an object's Performance tab KPI at its worst point (a cluster's two KPIs, an ESXi host's; D-108, D-111)."""
    if not k or not k.get("details") or not k.get("worst"):
        return None
    times = [p["t"] for p in k["points"]]
    if k["worst"]["t"] not in times:
        return None
    i = times.index(k["worst"]["t"])
    parts = []
    for d in k["details"]:
        vals = [p["v"] for p in d["points"]]
        parts.append({"name": d["label"], "unit": d["unit"].strip(), "better": "lower", "value": vals[i], "median": _median(vals),
                      "worst": (d.get("worst") or {}).get("v"), "worst_time": (d.get("worst") or {}).get("t")})
    kind = "ESXi host" if n["kind"] == "host" else n["kind"]
    return {"kpi": k["label"], "time": k["worst"]["t"], "kpi_value": k["worst"]["v"],
            "shown_in": f"{n['name']} ({kind}) · Performance tab · Details under {k['label']}", "parts": parts}


def _hourly_parts(k: dict) -> dict | None:
    """The parts of a KPI once an hour over the window, the value at the end of each hour (D-125): the same parts as the
    Details fold, so Agent E2 can score them before and after the moment the KPI changed level, not only at its worst
    point. Values only, no score: scoring is Agent E2's."""
    det = k.get("details") or []
    pts = k.get("points") or []
    m = _minutes([p["t"] for p in pts[:2]])
    if not det or not m:
        return None
    every = max(1, 60 // m)
    idx = list(range(every - 1, len(pts), every))
    return {"times": [pts[i]["t"] for i in idx],
            "rows": [{"name": d["label"], "unit": d["unit"].strip(), "hourly": [d["points"][i]["v"] for i in idx if i < len(d["points"])]}
                     for d in det]}


def _minutes(times: list) -> int | None:
    try:
        return int((datetime.fromisoformat(times[1]) - datetime.fromisoformat(times[0])).total_seconds() // 60)
    except (IndexError, TypeError, ValueError):
        return None


def percentile_name(better) -> str:
    """The label of the percentile figure beside a chart, by direction (l2.statistics, D-131): the value 95% of the points
    were better than is the 5th percentile where higher is better, the 95th where higher is worse."""
    return "5th percentile" if better == "higher" else "95th percentile"


def _chart(name: str, window: str, minutes, banded: bool, better=None) -> str:
    every = f", one point every {minutes} minutes, each point the worst value inside it" if minutes else ""
    band = ", each in its band colour" if banded else ""  # a KPI has bands; a counter has none (D-100)
    return (f"a trend chart of {name} over the {window.lower()}{every}; beside it Now, Worst and {percentile_name(better)} "
            f"(the value 95% of the points were better than){band}")


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
        out["card_shows"] = _chart(k["label"], f["window"], _minutes([p[0] for p in k["points"][:2]]), True, k.get("better"))
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
        out["card_shows"] = _chart(m["name"], f["window"], m.get("point_minutes"), m.get("unit") == "%" and "Performance" in m["name"],
                                  m.get("better"))
    elif kind == "vm_layer":
        out["clicked"] = f"the E2 mark on the {f['asked_about_layer']['layer']} layer"
        out["card_shows"] = ("the layer's status and one trend chart per metric, each with Now, Worst and its percentile figure: the 5th "
                            "percentile where higher is better, the 95th where higher is worse")
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
    if kind == "kpi" and pillar == "performance":
        # The KPIs at the top of a cluster's or an ESXi host's Performance tab (D-100, D-117).
        ks = M.object_kpis(E, X.node(E, o["id"]), now, window, enable)
        k = next((x for x in ks if x["key"] == ctx.get("metric")), None)
        if not k:
            return 404, {"error": "no such KPI on this object"}
        kpi = {key: k.get(key) for key in ("label", "better", "now", "worst", "percentile_95")}
        kpi["unit"] = "%"
        kpi["points"] = [[p["t"], p["v"]] for p in k.get("points", [])]
        parts = _parts(X.node(E, o["id"]), k)
        if parts:
            kpi["parts_at_worst"] = parts
        hourly = _hourly_parts(k)
        if hourly:
            kpi["parts_hourly"] = hourly
        # The other KPIs with their series, compact: a question such as "Risk rose but Performance did not drop: why?"
        # needs to see both lines (D-125).
        facts = {**base, "pillar": "Performance", "asked_about_kpi": kpi,
                 "other_kpis": [{**{key: x.get(key) for key in ("now", "worst", "percentile_95")}, **_compact(x)} for x in ks if x is not k]}
        return 200, {"facts": facts, "label": f"{k['label']} · {o['name']} · Performance · {WNAME[window]}"}
    if kind == "kpi":
        pv = M.pillar_view(now, view, o["id"], "capacity", window, enable=enable)
        cap = (pv or {}).get("capacity") or {}
        k = next((x for x in cap.get("kpis") or [] if x["key"] == ctx.get("metric")), None)
        if not k:
            return 404, {"error": "no such KPI on this object"}
        kpi = {key: k.get(key) for key in ("label", "better", "now", "worst", "percentile_95", "check_value", "closure_levels")}
        kpi["unit"] = "%"
        kpi["points"] = [[p["t"], p["v"]] for p in k.get("points", [])]
        parts = parts_at_worst(E, now, cap.get("cluster"), ctx.get("metric"), window, enable)
        if parts:
            kpi["parts_at_worst"] = parts
        facts = {**base, "pillar": "Capacity", "cluster": cap.get("cluster"), "check": cap.get("check"),
                 "contention_now": cap.get("contention_now"), "asked_about_kpi": kpi,
                 "consumption_parts": [_figures(p) for p in cap.get("parts") or []],  # what Consumption is made of (D-127)
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
    sf = suggest_facts(now, ctx, enable)  # the page's KPI series: a suggested question asks how they moved (D-124)
    if sf and sf["kpis"]:
        facts.update({k: v for k, v in sf.items() if k in ("kpis", "parts_at_worst", "consumption_parts", "check")})
    return 200, {"facts": facts, "label": where}


# ---------------------------------------------------------------- suggested questions for the whole page (D-124)

SUGGEST_PAGES = {("cluster", "performance"), ("cluster", "capacity"), ("host", "performance"), ("vm", "performance")}
VM_KPIS = ("vm_performance", "guest_os_performance")
CARD_KINDS = ("kpi", "metric", "link", "layer")  # cards with a showcase question from Agent E2 (D-127)


def _compact(k: dict) -> dict:
    """A KPI series as Agent E2 reads it, compact: the values with the first point's time and the minutes between points.
    Time and value pairs cost about five times the tokens and overflowed the model's context on the Capacity tab."""
    pts = k.get("points") or []
    ts = [p["t"] for p in pts]
    return {"label": k["label"], "better": k.get("better", "higher"), "unit": "%", "first_point": ts[0] if ts else None,
            "point_minutes": _minutes(ts), "values": [p["v"] for p in pts]}


def _figures(k: dict) -> dict:
    return {"label": k["label"], **{x: k.get(x) for x in ("now", "worst", "percentile_95") if k.get(x) is not None}}


def suggest_facts(now: datetime, ctx: dict, enable=()) -> dict | None:
    """The page's KPI series, as the page draws them, for Agent E2 to read the situation from. None for a page outside
    release 1.0 (SUGGEST_PAGES). PCM sends values only: no band, no verdict, no rule (D-078, D-124). The same facts go with a
    whole-page question, with the main KPI's parts at its worst point (cluster, host) or what Consumption is made of."""
    E = X.estate(tuple(enable))
    window = ctx.get("window") if ctx.get("window") in X.WINDOWS else "24h"
    o = _obj(E, ctx.get("view") or "compute", ctx.get("object") or "estate")
    pillar = ctx.get("pillar")
    if o is None or (o["kind"], pillar) not in SUGGEST_PAGES:
        return None
    extra = {}
    if pillar == "capacity":
        if X.node(E, o["id"]).get("class") not in X.WORKLOADS:  # no Periodic Cluster Check on this cluster
            return None
        cap = (M.pillar_view(now, ctx.get("view") or "compute", o["id"], "capacity", window, enable=enable) or {}).get("capacity") or {}
        ks = [_compact(k) for k in cap.get("kpis") or []]
        extra["consumption_parts"] = [_figures(p) for p in cap.get("parts") or []]  # what Consumption is made of, % of usable
        extra["check"] = cap.get("check")  # the latest Periodic Cluster Check: state, rule, reason, its inputs
    elif o["kind"] == "vm":
        pv = M.pillar_view(now, ctx.get("view") or "compute", o["id"], "performance", window, enable=enable) or {}
        ks = [_compact(m) for layer in pv.get("layers") or [] for m in layer.get("metrics", []) if m.get("key") in VM_KPIS]
    else:
        raw = M.object_kpis(E, X.node(E, o["id"]), now, window, enable)
        ks = [_compact(k) for k in raw]
        parts = _parts(X.node(E, o["id"]), raw[0]) if raw else None  # the main KPI's parts at its worst point (D-111)
        if parts:
            extra["parts_at_worst"] = parts
    return {"object": {"name": o["name"], "kind": o["kind"]}, "pillar": PNAME[pillar], "window": WNAME[window], "kpis": ks, **extra}


def suggest(now: datetime, body: dict, enable=()) -> tuple[int, dict]:
    """POST /api/l2/agent/suggest: Agent E2's three questions for the page, by its situation. Not recorded: nothing is asked."""
    ctx = body.get("context") or {}
    kind = (ctx.get("kind") or "page") if isinstance(ctx, dict) else None
    if kind in CARD_KINDS:  # one card: its showcase question, from the facts a question about it would send (D-127)
        code, got = facts_for(now, ctx, enable)
        if code != 200:
            return code, got
        f = got["facts"]
        name = (f.get("asked_about_kpi") or {}).get("label") or (f.get("asked_about_metric") or {}).get("name")
        settings = generator.load_spec()["settings"]
        return 200, agent_e2.card_service(service_url(settings), f, {"kind": kind, "name": name})
    if kind != "page":
        return 400, {"error": "context kind must be page, " + ", ".join(CARD_KINDS)}
    facts = suggest_facts(now, ctx, enable)
    if facts is None:
        return 200, {"questions": [], "situation": None, "source": "not_in_release"}
    settings = generator.load_spec()["settings"]
    slim = {k: facts[k] for k in ("object", "pillar", "window", "kpis")}  # the situation is read from the series alone
    return 200, agent_e2.suggest_service(service_url(settings), slim)


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



def topic(body: dict) -> tuple[int, dict]:
    """POST /api/l2/agent/topic and /api/noc/agent/topic (D-130): Agent E2's topic decision alone, before the answer.
    Not recorded: nothing is answered."""
    question = (body.get("question") or "").strip()
    if not question:
        return 400, {"error": "A question is required."}
    history = agent_e2.history_of(body)
    if history is None:
        return 400, {"error": "history must be a list of {question, answer}."}
    if not history:
        return 200, {"continues": False, "by": "first", "source": "pcm"}
    return 200, agent_e2.topic_service(service_url(generator.load_spec()["settings"]), question, history)


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
    history = agent_e2.history_of(body)
    if history is None:
        return 400, {"error": "history must be a list of {question, answer}."}
    choice = agent_e2.topic_choice_of(body)
    if choice is None:
        return 400, {"error": "topic_choice must be auto, new or continue."}
    out = agent_e2.ask_service(service_url(settings), question, got["facts"], "l2", turns=turns or None, history=history, topic_choice=choice)
    target = ctx.get("case") or ctx.get("finding") or ctx.get("object") or "estate"
    with noc.STATE.lock:
        rec = noc.record("agent_ask", target, HUMAN, question, ctx.get("kind") or "page", out["source"], now, actor_agent="agent-e2")
        noc.STATE.save()
    f = got.get("finding")
    return 200, {**out, "label": got["label"], "links": links_in(out.get("content", ""), enable) if out["source"] == "service" else [],
                 "finding": {"id": f["id"], "outcome": f.get("outcome")} if f else None, "record": rec}
