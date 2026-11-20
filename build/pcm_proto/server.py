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

from . import api, generator

WEB = Path(__file__).resolve().parents[1] / "web"


def route(path: str, query: dict):
    now = generator.parse_now(query.get("now", [None])[0])
    enable = tuple(s for s in query.get("enable", [""])[0].split(",") if s)
    ds = generator.generate(now, enable=enable)
    parts = [p for p in path.split("/") if p]
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


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # quiet
        pass

    def send(self, code, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

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
        if path == "/exec":
            path = "/exec/index.html"
        f = (WEB / path.lstrip("/")).resolve()
        if WEB not in f.parents or not f.is_file():
            return self.send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
        return self.send(200, f.read_bytes(), ctype)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
