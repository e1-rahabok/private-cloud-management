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
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import api, generator, noc

WEB = Path(__file__).resolve().parents[1] / "web"


def route(path: str, query: dict):
    now = generator.parse_now(query.get("now", [None])[0])
    enable = tuple(s for s in query.get("enable", [""])[0].split(",") if s)
    ds = generator.generate(now, enable=enable)
    parts = [p for p in path.split("/") if p]
    if parts[:2] == ["api", "noc"]:
        return noc_get(parts[2:], now, enable)
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


PAGES = {"/exec": "/exec/index.html", "/noc": "/noc/index.html", "/noc/wall": "/noc/wall.html",
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
        path = PAGES.get(path, path)
        f = (WEB / path.lstrip("/")).resolve()
        if WEB not in f.parents or not f.is_file():
            return self.send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        return self.send(200, f.read_bytes(), ctype)


    def do_POST(self):
        u = urlparse(self.path)
        parts = [p for p in u.path.split("/") if p]
        if parts[:2] != ["api", "noc"]:
            return self.send(404, b'{"error":"not found"}', "application/json")
        q = parse_qs(u.query)
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self.send(400, b'{"error":"bad json"}', "application/json")
        if parts[2:] == ["_reset"]:
            noc.STATE.reset()
            return self.send(200, b'{"reset":true}', "application/json")
        now = generator.parse_now(q.get("now", [None])[0])
        enable = tuple(x for x in q.get("enable", [""])[0].split(",") if x)
        code, data = noc.act(noc.build(now, enable), parts[2:], body)
        return self.send(code, json.dumps(data).encode(), "application/json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
