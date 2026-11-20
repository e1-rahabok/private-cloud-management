"""Catalog and story tests for the NOC workspace.

GENERATED. Do not edit by hand (D-070). Expected values come from spec/tests/noc.yaml (D-071).
Run from the repository root:  python3 -m unittest build.tests.test_noc -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

import os
from unittest import mock

from build.pcm_proto import agent_e2, api, generator, noc

ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((ROOT / "spec/tests/noc.yaml").read_text())
NOW = generator.parse_now(SPEC["now"])
SETTINGS = generator.load_spec()["settings"]


def tests(level):
    return {t["id"]: t for t in SPEC[level]}


class Catalog(unittest.TestCase):
    T = tests("catalog")

    def test_NCAT_1_kpi_bands_on_the_wall(self):
        t = self.T["NCAT-1"]
        self.assertEqual([noc.wall_status_from_kpi(s) for s in t["given"]["scores"]], t["expect"]["wall_status"])

    def test_NCAT_2_and_3_unexpected_change(self):
        for k in ("NCAT-2", "NCAT-3"):
            g = self.T[k]["given"]
            self.assertEqual(noc.changed_status(g["count"], g["expected"], SETTINGS), self.T[k]["expect"], k)

    def test_NCAT_4_grouping(self):
        t = self.T["NCAT-4"]
        alerts = [{**a, "object_type": a.get("object_type", "vm"), "severity": "red", "title": "x",
                   "raised": generator.rel(a["raised"], NOW)} for a in t["given"]["alerts"]]
        inc = noc.group_alerts(alerts, SETTINGS["noc.grouping_window_minutes"])
        self.assertEqual(len(inc), t["expect"]["incidents"])
        self.assertEqual([a["id"] for a in inc[0]["alerts"]], t["expect"]["first_incident_alerts"])

    def test_NCAT_5_route(self):
        t = self.T["NCAT-5"]
        self.assertEqual(noc.ROUTES[t["given"]["root_object_type"]], t["expect"])

    def test_NCAT_6_limit_expires_at_end_of_shift(self):
        t = self.T["NCAT-6"]
        end = noc.shift_end(NOW, "Asia/Singapore", t["given"]["shift_times"])
        self.assertEqual(end.strftime("%H:%M"), t["expect"])


def resolve(obj, path):
    for part in re.findall(r"[^.\[\]]+(?:\[[^\]]+\])?", path):
        m = re.fullmatch(r"([^\[]+)(?:\[(\w+)=([^\]]+)\])?", part)
        obj = obj[m.group(1)]
        if m.group(2):
            obj = next(x for x in obj if str(x.get(m.group(2))) == m.group(3))
    return obj


class Story(unittest.TestCase):
    T = tests("story")

    def setUp(self):
        noc.STATE.reset()

    def view(self, enable=()):
        nd = noc.build(NOW, enable)
        return nd, {"wall": noc.wall(nd), "incidents": noc.incident_list(nd)}

    def check_paths(self, t, enable=()):
        _, v = self.view(enable)
        for k, exp in t["expect"].items():
            if k == "wall.pins_contains":
                self.assertIn(exp, v["wall"]["pins"])
            elif k.startswith(("wall.", "incidents")):
                self.assertEqual(resolve(v, k), exp, k)

    def test_NST_1(self):
        self.check_paths(self.T["NST-1"])

    def test_NST_2_limit_refused_stop_allowed(self):
        e = self.T["NST-2"]["expect"]
        nd, _ = self.view()
        code, _ = noc.act(nd, ["actions", e["action"]["name"]], {"target": e["action"]["target"], "incident": "inc-fr-s-02"})
        self.assertEqual(code, e["action"]["status"])
        code, _ = noc.act(nd, ["actions", e["action_2"]["name"]], {"target": e["action_2"]["target"], "incident": "inc-fr-s-02"})
        self.assertEqual(code, e["action_2"]["status"])
        h = noc.STATE.history[0]
        self.assertTrue("actor_human" in h and "actor_agent" in h and h["actor_human"])

    def test_NST_3_ack_unpins(self):
        e = self.T["NST-3"]["expect"]
        nd, _ = self.view()
        noc.act(nd, ["incidents", "inc-" + e["after_ack_of"].lower(), "acknowledge"], {})
        noc.act(nd, ["incidents", "inc-tk", "acknowledge"], {})  # N-3 also pins; acknowledge it too
        _, v = self.view()
        self.assertIsNone(v["wall"]["pin"])
        self.assertEqual(resolve(v, "wall.strip[screen=fast].status"), "red")
        self.assertTrue(resolve(v, "wall.strip[screen=fast].in_hand"))

    def test_NST_4_close_needs_cause(self):
        e = self.T["NST-4"]["expect"]
        nd, _ = self.view()
        self.assertEqual(noc.act(nd, ["incidents", "inc-fr-s-02", "close"], {})[0], e["close_without_cause"])
        self.assertEqual(noc.act(nd, ["incidents", "inc-fr-s-02", "close"], {"root_cause": "noisy_neighbour"})[0], e["close_with_cause"])

    def test_NST_5(self):
        self.check_paths(self.T["NST-5"])

    def test_NST_6(self):
        _, v = self.view(("E-7",))
        e = self.T["NST-6"]["expect"]
        tiles = v["wall"]["screens"]["up"]["tiles"]
        for loc in ("fr", "ld"):
            self.assertEqual(next(t for t in tiles if t["location"] == loc)["status"], "no_data")
        self.assertEqual(resolve(v, "incidents[root_object=vcf-ops-emea].severity"), e["incidents[root_object=vcf-ops-emea].severity"])

    def test_NST_7_orange_does_not_pin(self):
        self.check_paths(self.T["NST-7"])
        _, v = self.view()
        self.assertNotIn("up", v["wall"]["pins"])

    def test_NST_8_same_safe_numbers_as_cio_page(self):
        nd, v = self.view()
        ld = next(t for t in v["wall"]["screens"]["safe"]["tiles"] if t["location"] == "ld")
        cio = api.summary(nd["ds"])["health"]["safe"]["open_findings"]["ssh_or_shell_enabled"]["value"]
        self.assertEqual(ld["findings"]["ssh_or_shell_enabled"], cio)


class AgentE2(unittest.TestCase):
    T = tests("story")

    def setUp(self):
        noc.STATE.reset()
        self.nd = noc.build(NOW)

    def test_NST_9_draft_recorded_and_changes_nothing(self):
        with mock.patch.dict(os.environ, {"PCM_AGENT_E2_MODE": "mock"}):
            before = noc.incident_list(self.nd)[0]["state"]
            code, out = noc.act(self.nd, ["incidents", "inc-fr-s-02", "agent"], {"task": "explain"})
        e = self.T["NST-9"]["expect"]
        self.assertEqual(code, 200)
        rec = out["record"]
        self.assertEqual(rec["action"], e["record_action"])
        self.assertEqual(rec["actor_agent"], e["actor_agent"])
        self.assertTrue(rec["actor_human"])
        self.assertEqual(noc.incident_list(noc.build(NOW))[0]["state"], before)

    def test_NST_10_vocabulary_fallback(self):
        answers = iter(self.T["NST-10"]["given"]["model_answers"])
        fake = lambda *a, **k: {"choices": [{"message": {"content": next(answers)}}]}
        with mock.patch.dict(os.environ, {"AI_GATEWAY_API_KEY": "test", "PCM_AGENT_E2_MODE": "live"}), \
             mock.patch.object(agent_e2, "_post", fake):
            code, out = noc.act(self.nd, ["incidents", "inc-fr-s-02", "agent"], {"task": "explain"})
        self.assertEqual(out["source"], self.T["NST-10"]["expect"]["source"])

    def test_NST_11_unavailable_fallback(self):
        env = {k: v for k, v in os.environ.items() if k not in ("AI_GATEWAY_API_KEY", "PCM_AGENT_E2_MODE")}
        with mock.patch.dict(os.environ, env, clear=True):
            code, out = noc.act(self.nd, ["incidents", "inc-fr-s-02", "agent"], {"task": "explain"})
        self.assertEqual(out["source"], self.T["NST-11"]["expect"]["source"])

    def test_NST_12_done_kept_apart_from_available(self):
        facts = agent_e2.facts_for(noc.incident_detail(self.nd, "inc-fr-s-02"))
        e = self.T["NST-12"]["expect"]
        for k in e["facts_have"]:
            self.assertIn(k, facts)
        self.assertTrue(any(e["sop_action_field"] in st for st in facts["sop_steps"]))
        self.assertFalse(any("allowed" in st for st in facts["sop_steps"]))


class SpecRules(unittest.TestCase):
    def test_NPG_1_every_page_and_section_names_question_role_cadence(self):
        for f in (ROOT / "spec/workspaces/noc").glob("*.md"):
            text = f.read_text()
            front = yaml.safe_load(text.split("---")[1])
            self.assertTrue({"question", "role", "cadence"} <= set(front), f.name)
            for b in re.findall(r"```yaml\n(.*?)```", text, re.S):
                self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(b)), f.name)


if __name__ == "__main__":
    unittest.main()
