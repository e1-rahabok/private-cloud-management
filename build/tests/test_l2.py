"""Catalog and story tests for the L2 workspace.

GENERATED. Do not edit by hand (D-070). Expected values come from spec/tests/l2.yaml (D-071).
Run from the repository root:  python3 -m unittest build.tests.test_l2 -v
"""
from __future__ import annotations

import os
import re
import unittest
from pathlib import Path
from unittest import mock

import os
os.environ["PCM_DB"] = ":memory:"  # tests never touch the working database

import yaml

from build.pcm_proto import api, generator, l2, noc

ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((ROOT / "spec/tests/l2.yaml").read_text())
NOW = generator.parse_now(SPEC["now"])
REAL_SPEC = generator.load_spec()
SETTINGS = REAL_SPEC["settings"]
T = {t["id"]: t for level in ("catalog", "story") for t in SPEC[level]}


class Base(unittest.TestCase):
    def setUp(self):
        noc.STATE.reset()
        l2.STATE.reset()


class Catalog(Base):
    def test_LCAT_1_three_verdicts(self):
        self.assertEqual(l2.verdicts(T["LCAT-1"]["given"]["findings"]), T["LCAT-1"]["expect"])

    def test_LCAT_2_guardrails_gate_automatic_runs(self):
        g = T["LCAT-2"]["given"]
        for r in g["runs"]:
            blocked = l2.guardrail_block(g["policy"], r)
            self.assertEqual("run" if blocked is None else f"stopped: {blocked}", r["expect"], r)

    def test_LCAT_3_replay(self):
        g, e = T["LCAT-3"]["given"], T["LCAT-3"]["expect"]
        r = l2.replay(NOW, g["threshold"], g["new"], SETTINGS)
        self.assertEqual(r["days"], e["days"])
        self.assertEqual(len(r["per_day"]), e["days"])
        self.assertGreaterEqual(r["total_new"], r["total_current"])


class Story(Base):
    def test_LST_1_escalation_loop(self):
        e = T["LST-1"]["expect"]
        self.assertEqual(l2.escalations(NOW), [])
        noc.act(noc.build(NOW), ["incidents", "inc-fr-s-02", "escalate"], {})
        esc = l2.escalations(NOW)
        self.assertEqual([x["id"] for x in esc], ["inc-fr-s-02"])
        self.assertTrue(esc[0]["evidence"]["villains"][0]["cpu_ready_percent"] is not None)
        self.assertEqual(l2.act(NOW, ["escalations", "inc-fr-s-02", "close"], {"root_cause": "noisy neighbour"})[0],
                         e["close_without_detection"])
        body = {"root_cause": "Bronze batch VM in a Silver cluster", "corrective_action": "Move fr-bat-017 to FR-B-02",
                "detection": "new_check_rule", "detection_note": "Daily check flags class mismatch on placement"}
        self.assertEqual(l2.act(NOW, ["escalations", "inc-fr-s-02", "close"], body)[0], e["close_complete"])
        self.assertEqual(next(i for i in noc.build(NOW)["incidents"] if i["id"] == "inc-fr-s-02")["state"], "closed")

    def test_LST_2_guest_os_realm(self):
        e = T["LST-2"]["expect"]
        d = l2.investigate(NOW, "sg-app-117")
        self.assertEqual(d["realm_verdict"], e["realm_verdict"])
        self.assertEqual(d["realms"]["vm"]["status"], e["vm_status"])
        self.assertEqual(d["realms"]["guest_os"]["status"], e["guest_os_status"])
        self.assertIsNone(d["first_failing"])

    def test_LST_3_configuration(self):
        e = T["LST-3"]["expect"]
        cfg = l2.configuration(NOW)
        self.assertEqual(len(cfg["groups"]["correct_it"]), e["correct_it_count"])
        code, out = l2.act(NOW, ["configuration", "c-va-esx-142-1", "decide"], {"choice": "fix_the_setting"})
        self.assertTrue(code == 200 and any(p["id"] == out["proposal"] for p in l2.proposals()))
        code, out = l2.act(NOW, ["configuration", "c-va-esx-142-2", "decide"], {"choice": "fix_the_standard"})
        self.assertEqual(out["standard_version"], 2)

    def test_LST_4_policy_change(self):
        e = T["LST-4"]["expect"]
        prop = generator.load_spec()["stories"]["stories"]["L-4"]["plant"]["proposed_policy"]
        t = "move_vms_between_clusters"
        self.assertEqual(l2.act(NOW, ["policies", t, "publish"], {**prop, "reason": "x"})[0], e["publish_without_replay"])
        code, rep = l2.act(NOW, ["policies", t, "replay"], prop)
        self.assertEqual(rep["would_run_automatically"], e["replay_would_run"])
        self.assertEqual(rep["stopped"], e["replay_stopped"])
        self.assertEqual(l2.act(NOW, ["policies", t, "publish"], prop)[0], e["publish_without_reason"])
        code, out = l2.act(NOW, ["policies", t, "publish"], {**prop, "reason": "Guardrails replace approval"})
        self.assertEqual((code, out["tier"], out["version"]), (200, e["tier_after"], e["version_after"]))
        p = next(x for x in l2.proposals() if x["id"] == "p-move-sg-s-04")
        self.assertEqual(p["state"], e["proposal_state_after"])
        self.assertEqual(p["accountable"], e["accountable_after"])
        rec = next(h for h in noc.STATE.history if h["target"] == "p-move-sg-s-04")
        self.assertEqual(rec["actor_human"], e["accountable_after"])
        self.assertEqual(rec["actor_agent"], "pcm-policy")
        self.assertFalse(any(h["action"] == "approve" and h["target"] == "p-move-sg-s-04" for h in noc.STATE.history))

    def test_no_promotion_left(self):
        self.assertFalse(hasattr(l2, "promotion_offered"))
        self.assertNotIn("l2.promotion_min_approvals", SETTINGS)

    def test_LST_5_daily_verdicts(self):
        e = T["LST-5"]["expect"]
        d = l2.daily(NOW)
        for v in ("present_health", "risk", "efficiency"):
            self.assertEqual(d["verdicts"][v], e[v])
        self.assertEqual(d["findings"][0]["verdict"], e["first_finding_verdict"])

    def test_LST_6_calendar_explains(self):
        f = l2.daily(NOW)["findings"]
        self.assertTrue(f[-1].get("explained_by"))
        self.assertEqual(f[-1]["explained_by"]["kind"], T["LST-6"]["expect"]["explained_by_kind"])

    def test_LST_7_reject_needs_reason(self):
        self.assertEqual(l2.act(NOW, ["proposals", "p-move-sg-s-04", "reject"], {})[0], T["LST-7"]["expect"]["reject_without_reason"])

    def test_LST_8_same_numbers(self):
        d = l2.daily(NOW)
        nd = noc.build(NOW)
        wall_fr = next(t for t in noc.wall(nd)["screens"]["fast"]["tiles"] if t.get("cluster") == "FR-S-02")
        self.assertEqual(next(x for x in d["findings"] if x["id"] == "f-fr-s-02")["score"], wall_fr["score"])
        cio = api.summary(nd["ds"])["health"]["safe"]["open_findings"]["ssh_or_shell_enabled"]["value"]
        self.assertEqual(next(x for x in d["findings"] if x["id"] == "f-ld-ssh")["ssh_count"], cio)

    def test_rca_draft_recorded(self):
        noc.act(noc.build(NOW), ["incidents", "inc-fr-s-02", "escalate"], {})
        with mock.patch.dict(os.environ, {"PCM_AGENT_E2_MODE": "mock"}):
            code, out = l2.act(NOW, ["escalations", "inc-fr-s-02", "agent"], {})
        self.assertEqual(code, 200)
        self.assertEqual(out["record"]["actor_agent"], "agent-e2")


class AskWhy(Base):
    def test_service_unavailable(self):
        st = dict(SETTINGS, **{"agent_e2.service_url": "http://127.0.0.1:9"})
        with mock.patch.object(generator, "load_spec", lambda: {**REAL_SPEC, "settings": st}):
            code, out = l2.act(NOW, ["investigate", "sg-app-117", "ask"], {"question": "Why?"})
        self.assertEqual((code, out["source"]), (200, "unavailable"))
        self.assertEqual(noc.STATE.history[0]["actor_agent"], "agent-e2")

    def test_service_answer_passes_facts_and_role(self):
        seen = {}
        def fake(url, body, timeout):
            seen.update(body)
            return {"type": "answer", "content": "Inside the Guest OS.", "files_read": ["sp5-framework/performance/vm-slow"], "model": "m"}
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = l2.act(NOW, ["investigate", "sg-app-117", "ask"], {"question": "Is the platform the cause?"})
        self.assertEqual(out["source"], "service")
        self.assertEqual(seen["role"], "l2")
        self.assertEqual(seen["facts"]["realm_verdict"], "guest_os")


class SpecRules(unittest.TestCase):
    def test_LPG_1_every_page_and_section_names_question_role_cadence(self):
        for f in (ROOT / "spec/workspaces/l2").glob("*.md"):
            text = f.read_text()
            self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(text.split("---")[1])), f.name)
            for b in re.findall(r"```yaml\n(.*?)```", text, re.S):
                self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(b)), f.name)


if __name__ == "__main__":
    unittest.main()
