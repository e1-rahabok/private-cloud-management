"""Mock PCM API and static page server for the prototype.

GENERATED. Do not edit by hand (D-070).

Run from the repository root:
    python3 -m build.pcm_proto.server --port 8080
Then open http://localhost:8080/exec

Synthetic-only query parameters (spec/api/openapi.yaml): now=<ISO time>, enable=<story,story>.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import api, capacity, docs, generator, l2, noc

WEB = Path(__file__).resolve().parents[1] / "web"


def route(path: str, query: dict):
    now = generator.parse_now(query.get("now", [None])[0])
    enable = tuple(s for s in query.get("enable", [""])[0].split(",") if s)
    ds = generator.generate(now, enable=enable)
    parts = [p for p in path.split("/") if p]
    if parts[:2] == ["api", "noc"]:
        return noc_get(parts[2:], now, enable)
    if parts[:2] == ["api", "l2"]:
        return l2_get(parts[2:], now, enable, query)
    if parts[:2] == ["api", "docs"]:
        rest = parts[2:]
        if not rest:
            return docs.index(enable)
        if len(rest) == 2 and rest[0] in docs.KINDS:
            return docs.detail(rest[0], rest[1], enable)
        return None
    if parts[:2] == ["api", "capacity"]:
        return capacity_get(parts[2:], now, enable, query)
    if parts[:2] != ["api", "exec"]:
        return None
    rest = parts[2:]
    if rest == ["summary"]:
        return api.summary(ds)
    if len(rest) == 2 and rest[0] == "locations" and rest[1] in ds["locations"]:
        return api.location_detail(ds, rest[1])
    if len(rest) == 2 and rest[0] == "health" and rest[1] in ("up", "fast", "safe"):
        return api.health_detail(ds, rest[1], int(query.get("window_days", ["7"])[0]))
    if rest == ["capacity"]:
        return api.capacity_detail(ds)
    if len(rest) == 2 and rest[0] == "value" and rest[1] in ("cost", "site_recovery", "speed"):
        return api.value_detail(ds, rest[1])
    return None


def noc_get(rest, now, enable):
    nd = noc.build(now, enable)
    if rest == ["wall"]:
        return noc.wall(nd)
    if rest == ["incidents"]:
        return noc.incident_list(nd)
    if len(rest) == 2 and rest[0] == "incidents":
        return noc.incident_detail(nd, rest[1])
    if len(rest) == 2 and rest[0] == "clusters":
        return noc.cluster_detail(nd, rest[1])
    if rest == ["shift"]:
        return noc.shift_view(nd)
    if rest == ["history"]:
        return noc.STATE.history
    return None


def l2_get(rest, now, enable, query):
    st = generator.load_spec()["settings"]
    if rest == ["daily"]:
        return l2.daily(now, enable)
    if rest == ["policies"]:
        return l2.policies(enable)
    if rest == ["escalations"]:
        return l2.escalations(now, enable)
    if len(rest) == 2 and rest[0] == "investigate":
        return l2.investigate(now, rest[1], enable)
    if rest == ["configuration"]:
        return l2.configuration(now, enable)
    if rest == ["calendar"]:
        return l2.calendar(now, enable)
    if rest == ["weekly"]:
        return l2.weekly(now, enable)
    if rest == ["monthly"]:
        return l2.monthly(now, enable)
    if rest == ["inventory"]:
        days = int(query.get("days", ["7"])[0])
        if days not in (7, 30):
            raise ValueError("days must be 7 or 30")
        return l2.inventory(now, days, enable)
    if rest == ["thresholds"]:
        return [{"id": k, **v, **l2.STATE.thresholds.get(k, {})} for k, v in l2.THRESHOLDS.items()]
    if len(rest) == 3 and rest[0] == "thresholds" and rest[2] == "replay" and rest[1] in l2.THRESHOLDS:
        return l2.replay(now, rest[1], float(query.get("value", ["50"])[0]), st)
    return None


def capacity_get(rest, now, enable, query):
    st = generator.load_spec()["settings"]
    if rest == ["week"]:
        return capacity.week(now, enable)
    if rest == ["groups"]:
        return capacity.groups_view(now, enable)
    if len(rest) == 2 and rest[0] == "groups":
        return capacity.group_detail(now, rest[1], enable)
    if rest == ["demand"]:
        return capacity.demand(now, enable)
    if rest == ["plan"]:
        return capacity.plan_view(now, enable)
    if rest == ["waste"]:
        return capacity.waste_view(now, enable)
    if rest == ["what-if", "refresh"]:
        g = lambda k, d: query.get(k, [d])[0]
        return capacity.what_if_refresh(capacity.build(now, enable), g("location", "ld"), int(g("replace", "90")), int(g("new", "75")))
    if rest == ["what-if", "host"]:
        g = lambda k, d: query.get(k, [d])[0]
        cls = g("class", "silver")
        if cls not in capacity.CLASSES:
            raise ValueError("class must be gold, silver or bronze")
        return capacity.planning_six_numbers(cls, int(g("cores", "64")), float(g("base_ghz", "2.5")), float(g("memory_gb", "768")), st)
    return None


PAGES = {"/docs": "/docs/index.html", "/capacity": "/capacity/index.html", "/capacity/clusters": "/capacity/clusters.html", "/capacity/demand": "/capacity/demand.html",
         "/capacity/what-if": "/capacity/what-if.html", "/capacity/plan": "/capacity/plan.html", "/capacity/waste": "/capacity/waste.html",
         "/l2": "/l2/index.html", "/l2/weekly": "/l2/weekly.html", "/l2/monthly": "/l2/monthly.html", "/l2/inventory": "/l2/inventory.html", "/l2/escalations": "/l2/escalations.html", "/l2/configuration": "/l2/configuration.html",
         "/l2/context": "/l2/context.html", "/l2/authoring": "/l2/authoring.html","/exec": "/exec/index.html", "/noc": "/noc/index.html", "/noc/wall": "/noc/wall.html",
         "/noc/alerts": "/noc/alerts.html", "/noc/shift": "/noc/shift.html"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # quiet
        pass

    def send(self, code, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the browser left the page before the answer arrived

    def do_GET(self):
        u = urlparse(self.path)
        if u.path.startswith("/api/"):
            try:
                data = route(u.path, parse_qs(u.query))
            except ValueError as e:
                return self.send(400, json.dumps({"error": str(e)}).encode(), "application/json")
            if data is None:
                return self.send(404, b'{"error":"not found"}', "application/json")
            return self.send(200, json.dumps(data).encode(), "application/json")
        path = u.path.rstrip("/") or "/exec"
        if path.startswith("/noc/alert/"):
            path = "/noc/alert.html"
        if path.startswith("/l2/investigate/"):
            path = "/l2/investigate.html"
        if path.startswith("/docs/") and path.count("/") == 3:
            path = "/docs/object.html"
        if path.startswith("/capacity/group/"):
            path = "/capacity/group.html"
        path = PAGES.get(path, path)
        f = (WEB / path.lstrip("/")).resolve()
        if WEB not in f.parents or not f.is_file():
            return self.send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        body = f.read_bytes()
        if f.suffix == ".html" and os.environ.get("PCM_DEMO_SWITCHER") != "0":
            # Demo only: a thin role switcher on every page. The generated pages stay untouched.
            body = body.replace(b"</body>", b'<script src="/demo/switcher.js"></script></body>', 1)
        return self.send(200, body, ctype)


    def do_POST(self):
        u = urlparse(self.path)
        parts = [p for p in u.path.split("/") if p]
        if parts[:2] not in (["api", "noc"], ["api", "l2"], ["api", "capacity"]):
            return self.send(404, b'{"error":"not found"}', "application/json")
        q = parse_qs(u.query)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self.send(400, b'{"error":"bad json"}', "application/json")
        if parts[2:] == ["_reset"]:
            noc.STATE.reset()
            l2.STATE.reset()
            capacity.STATE.reset()
            return self.send(200, b'{"reset":true}', "application/json")
        now = generator.parse_now(q.get("now", [None])[0])
        enable = tuple(x for x in q.get("enable", [""])[0].split(",") if x)
        if parts[1] == "capacity":
            if parts[2:] != ["demand"]:
                return self.send(404, b'{"error":"not found"}', "application/json")
            code, data = capacity.add_demand(now, body, enable)
        elif parts[1] == "l2":
            code, data = l2.act(now, parts[2:], body, enable)
        else:
            code, data = noc.act(noc.build(now, enable), parts[2:], body)
        return self.send(code, json.dumps(data).encode(), "application/json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1",
                    help="address to listen on; 127.0.0.1 by default. Use 0.0.0.0 on a lab VM (deploy/README.md): there is no sign-in yet.")
    args = ap.parse_args()
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
