"""The prototype database: SQLite, one file, standard library only (D-080).

GENERATED from spec/database/schema.sql. Do not edit by hand (D-070).
Path: environment variable PCM_DB, else var/pcm.sqlite at the repository root. PCM_DB=:memory: for tests.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = (ROOT / "spec/database/schema.sql").read_text()
_lock = threading.RLock()
_conn: sqlite3.Connection | None = None


def path() -> str:
    return os.environ.get("PCM_DB") or str(ROOT / "var/pcm.sqlite")


def db() -> sqlite3.Connection:
    global _conn
    with _lock:
        if _conn is None:
            p = path()
            if p != ":memory:":
                Path(p).parent.mkdir(parents=True, exist_ok=True)
            _conn = sqlite3.connect(p, check_same_thread=False, isolation_level=None)
            _conn.row_factory = sqlite3.Row
            _conn.execute("PRAGMA journal_mode=WAL" if p != ":memory:" else "PRAGMA journal_mode=MEMORY")
            _conn.executescript(SCHEMA)
        return _conn


def close():
    """Forget the connection: the next call opens the file again, as after a restart."""
    global _conn
    with _lock:
        if _conn is not None:
            _conn.close()
            _conn = None


def execute(sql: str, args=()) -> sqlite3.Cursor:
    with _lock:
        return db().execute(sql, args)


def rows(sql: str, args=()) -> list[dict]:
    with _lock:
        return [dict(r) for r in db().execute(sql, args).fetchall()]


# ---- the action record (append-only)

RECORD_FIELDS = ("at", "action", "target", "incident", "actor_agent", "actor_human", "reason", "before", "after", "expires_at")


def append_record(rec: dict) -> None:
    execute(f"INSERT INTO action_record ({', '.join(RECORD_FIELDS)}) VALUES ({', '.join('?' * len(RECORD_FIELDS))})",
            [None if rec.get(k) is None else str(rec[k]) for k in RECORD_FIELDS])


def records() -> list[dict]:
    """Newest first, as the pages show it."""
    return rows(f"SELECT {', '.join(RECORD_FIELDS)} FROM action_record ORDER BY seq DESC")


def clear_records() -> None:
    """Prototype and test reset only. Append-only holds for everything else."""
    with _lock:
        db().executescript("DROP TABLE IF EXISTS action_record;")
        db().executescript(SCHEMA)


# ---- workflow state

def save_state(workspace: str, values: dict) -> None:
    with _lock:
        c = db()
        c.execute("BEGIN")
        for k, v in values.items():
            c.execute("INSERT INTO workflow_state (workspace, name, value) VALUES (?, ?, ?) "
                      "ON CONFLICT (workspace, name) DO UPDATE SET value = excluded.value", (workspace, k, json.dumps(v)))
        c.execute("COMMIT")


def load_state(workspace: str) -> dict:
    return {r["name"]: json.loads(r["value"]) for r in rows("SELECT name, value FROM workflow_state WHERE workspace = ?", (workspace,))}


def clear_state(workspace: str) -> None:
    execute("DELETE FROM workflow_state WHERE workspace = ?", (workspace,))
