"""Tests for the prototype database (store.py).

GENERATED. Do not edit by hand (D-070). Expected values come from spec/tests/database.yaml.
Run from the repository root:  python3 -m unittest build.tests.test_store -v
"""
from __future__ import annotations

import os
os.environ["PCM_DB"] = ":memory:"  # tests never touch the working database
import sqlite3
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

import yaml

from build.pcm_proto import capacity, generator, l2, l2_cases, noc, store

ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((ROOT / "spec/tests/database.yaml").read_text())
NOW = generator.parse_now(SPEC["now"])
T = {t["id"]: t for t in SPEC["catalog"]}


class OnFile(unittest.TestCase):
    """Each test runs on its own database file, so a restart can be simulated."""
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        store.close()
        os.environ["PCM_DB"] = str(Path(self.dir.name) / "pcm.sqlite")
        for s in (noc.STATE, l2.STATE, l2_cases.STATE, capacity.STATE):
            s.reset()

    def tearDown(self):
        store.close()
        os.environ["PCM_DB"] = ":memory:"
        noc.STATE.load(); l2.STATE.load(); l2_cases.STATE.load()
        self.dir.cleanup()

    def restart(self):
        store.close()
        noc.STATE.load()
        l2.STATE.load()
        l2_cases.STATE.load()

    def test_DB_1_record_append_only(self):
        noc.record("acknowledge", "inc-x", "operator-1", "", "open", "acknowledged", NOW)
        with self.assertRaises(sqlite3.DatabaseError):
            store.execute("UPDATE action_record SET actor_human = 'someone-else'")
        with self.assertRaises(sqlite3.DatabaseError):
            store.execute("DELETE FROM action_record")
        self.assertEqual(store.records()[0]["actor_human"], "operator-1")

    def test_DB_2_survives_restart(self):
        e = T["DB-2"]["expect"]
        noc.act(noc.build(NOW), ["incidents", "inc-fr-s-02", "escalate"], {})
        prop = generator.load_spec()["stories"]["stories"]["L-4"]["plant"]["proposed_policy"]
        l2.act(NOW, ["policies", "move_vms_between_clusters", "replay"], prop)
        self.assertEqual(l2.act(NOW, ["policies", "move_vms_between_clusters", "publish"], {**prop, "reason": "Guardrails"})[0], 200)
        code, _ = capacity.add_demand(NOW, {"kind": "project", "group": "VA-Silver", "owner": "apps-team", "memory_gb": 20000,
                                            "date": (NOW + timedelta(days=60)).date().isoformat()})
        self.assertEqual(code, 200)
        before = next(g for g in capacity.groups_view(NOW)["groups"] if g["id"] == "VA-Silver")["decision_days"]
        n_records = len(noc.STATE.history)

        self.restart()
        self.assertIn(e["escalated"], noc.STATE.escalated)
        pol = next(p for p in l2.policies() if p["action_type"] == "move_vms_between_clusters")
        self.assertEqual(pol["version"], e["policy_version"])
        self.assertEqual(len(capacity.STATE.added), e["register_entries"])
        self.assertEqual(len(noc.STATE.history), n_records)
        self.assertGreaterEqual(n_records, e["records_at_least"])
        self.assertEqual(noc.STATE.history[0]["actor_agent"], "pcm-policy")
        after = next(g for g in capacity.groups_view(NOW)["groups"] if g["id"] == "VA-Silver")["decision_days"]
        self.assertEqual(before, after)
        self.assertIn("case-inc-fr-s-02", [x["id"] for x in l2_cases.list_cases(NOW)])  # the escalation is a case after a restart

    def test_DB_3_register_checks(self):
        e = T["DB-3"]["expect"]
        base = {"kind": "project", "group": "VA-Silver", "owner": "apps-team", "date": "2027-01-15"}
        self.assertEqual(capacity.add_demand(NOW, base)[0], e["no_amount"])
        self.assertEqual(capacity.add_demand(NOW, {**base, "memory_gb": -5})[0], e["negative_amount"])
        self.assertEqual(capacity.add_demand(NOW, {**base, "kind": "wish", "memory_gb": 5})[0], e["unknown_kind"])
        self.assertEqual(capacity.STATE.added, [])

    def test_DB_4_synthetic_not_stored(self):
        e = T["DB-4"]["expect"]
        capacity.build(NOW)
        self.assertEqual(store.rows("SELECT COUNT(*) AS n FROM demand_register")[0]["n"], 0)
        tables = sorted(r["name"] for r in store.rows("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"))
        self.assertEqual(tables, sorted(e["tables"]))


if __name__ == "__main__":
    unittest.main()
