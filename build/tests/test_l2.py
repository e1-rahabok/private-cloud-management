"""Catalog and story tests for the L2 workspace: Monitor, Troubleshoot, Improve (D-083 to D-090).

GENERATED. Do not edit by hand (D-070). Expected values come from spec/tests/l2.yaml (D-071).
Run from the repository root:  python3 -m unittest build.tests.test_l2 -v
"""
from __future__ import annotations

import json
import os
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

os.environ["PCM_DB"] = ":memory:"  # tests never touch the working database

import yaml

from build.pcm_proto import generator, l2, l2_agent as A, l2_capacity as CAP, l2_cases as C, l2_estate as X, l2_improve as I, l2_monitor as M, l2_performance as P, noc

ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((ROOT / "spec/tests/l2.yaml").read_text())
NOW = generator.parse_now(SPEC["now"])
REAL_SPEC = generator.load_spec()
SETTINGS = REAL_SPEC["settings"]
CATALOG = yaml.safe_load((ROOT / "spec/catalog/l2.yaml").read_text())["entries"]
STORIES = REAL_SPEC["stories"]["stories"]
T = {t["id"]: t for level in ("catalog", "story") for t in SPEC[level]}
E = X.estate(())


class Base(unittest.TestCase):
    def setUp(self):
        noc.STATE.reset()
        l2.STATE.reset()
        C.STATE.reset()


class Catalog(Base):
    def test_LCAT_1_pillar_status(self):
        st = M.pillar_status(T["LCAT-1"]["given"]["findings"])
        for k, v in T["LCAT-1"]["expect"].items():
            self.assertEqual(st[k], v, k)

    def test_LCAT_2_guardrails_gate_automatic_runs(self):
        g = T["LCAT-2"]["given"]
        for r in g["runs"]:
            blocked = l2.guardrail_block(g["policy"], r)
            self.assertEqual("run" if blocked is None else f"stopped: {blocked}", r["expect"], r)

    def test_LCAT_3_replay(self):
        g, e = T["LCAT-3"]["given"], T["LCAT-3"]["expect"]
        r = l2.replay(NOW, g["threshold"], g["new"], SETTINGS)
        self.assertEqual(len(r["per_day"]), e["days"])
        self.assertGreaterEqual(r["total_new"], r["total_current"])

    def test_LCAT_4_weekly_rules(self):
        g, e = T["LCAT-4"]["given"], T["LCAT-4"]["expect"]
        self.assertEqual(l2.is_drift(g["drift"]), e["drift"])
        self.assertEqual(l2.is_drift(g["noise"]), e["noise"])
        self.assertEqual(l2.is_hidden(g["hidden"]["peak"], g["hidden"]["red"], g["hidden"]["vm_status"]), e["hidden"])

    def test_LCAT_5_decision_state(self):
        self.assertEqual(l2.decision_state(NOW - timedelta(days=1), False, NOW), T["LCAT-5"]["expect"]["state"])
        self.assertEqual(l2.decision_state(NOW + timedelta(days=1), False, NOW), "open")
        self.assertEqual(l2.decision_state(NOW - timedelta(days=1), True, NOW), "done")

    def test_LCAT_6_explanation_order(self):
        self.assertEqual(l2.explain({"request", "pcm_action"}), T["LCAT-6"]["expect"]["explanation"])
        self.assertIsNone(l2.explain(set()))

    def test_LCAT_7_node_score_is_met_95_percent_of_the_time(self):
        t = T["LCAT-7"]
        self.assertEqual(X.p95_score(t["given"]["samples"]), t["expect"]["score"])

    def test_LCAT_8_iceberg(self):
        self.assertEqual(M.near_line_count(T["LCAT-8"]["given"]["scores"]), T["LCAT-8"]["expect"]["near_line"])

    def test_LCAT_10_worst_and_percentile(self):
        g, e = T["LCAT-10"]["given"], T["LCAT-10"]["expect"]
        self.assertEqual(min(g["performance"]), e["worst"])
        self.assertEqual(P.nearest_rank(g["performance"], 10), e["percentile_10_of_three"])
        self.assertEqual(P.nearest_rank(g["twenty"], 10), e["percentile_10_of_twenty"])
        self.assertEqual(P.nearest_rank(g["twenty"], 90), e["percentile_90_of_twenty"])
        self.assertEqual(P.PERCENTILE, {"performance": 10, "risk": 90})
        b = e["bands"]
        self.assertEqual((P.perf_band(74), P.risk_band(74), P.risk_band(20), P.perf_band(20)),
                         (b["performance_74"], b["risk_74"], b["risk_20"], b["performance_20"]))

    def test_LCAT_11_weighted_average_by_color(self):
        self.assertEqual(round(P.kpi(T["LCAT-11"]["given"]["scores"]), 2), T["LCAT-11"]["expect"]["kpi"])

    def test_LCAT_9_tree(self):
        e = T["LCAT-9"]["expect"]
        self.assertEqual(CATALOG["l2.tree"]["views"]["compute"], e["compute_levels"])
        self.assertEqual(list(CATALOG["l2.tree"]["views"]), e["views"])
        self.assertEqual(list(X.VIEWS), e["views"])
        p = [n["kind"] for n in X.path(E, "compute", "sg-app-117/os")]
        self.assertEqual(p, e["compute_levels"])
        self.assertEqual(X.path(E, "compute", "sg-app-117/os")[-2]["id"], "sg-app-117")


class Estate(Base):
    def test_LST_1_the_whole_estate(self):
        e = T["LST-1"]["expect"]
        self.assertEqual(sum(1 for n in E.nodes.values() if n["kind"] == "host"), e["hosts"])
        self.assertEqual([n["id"] for n in E.kids("compute", "estate")], e["root_children_compute"])
        noc_ids = {c["id"] for c in noc.build(NOW)["clusters"]}
        self.assertTrue(noc_ids <= {n["id"] for n in E.nodes.values() if n["kind"] == "cluster"})
        named = set(X._story_vm_names(X.active_stories(())))
        for k in ("host_pins", "datastore_pins"):
            named |= {x for x in REAL_SPEC["estate"]["l2_tree"][k] if x != "note"}
        missing = [x for x in named if x not in E.nodes]
        self.assertEqual(missing, [])
        for name, pin in REAL_SPEC["estate"]["l2_tree"]["host_pins"].items():
            if name != "note":
                self.assertEqual(E.nodes[name]["cluster"], pin["cluster"], name)

    def test_LST_2_same_numbers_as_the_noc(self):
        nd = noc.build(NOW)
        fr = next(c for c in nd["clusters"] if c["id"] == "FR-S-02")
        self.assertEqual(M.perf_score(E, E.nodes["FR-S-02"], NOW, "1h"), fr["score"])
        tk = next(c for c in nd["clusters"] if c["id"] == "TK-S-03")
        self.assertEqual(tk["status"], T["LST-2"]["expect"]["TK-S-03_noc_status"])
        inc = next(i for i in nd["incidents"] if i["id"] == "inc-tk-s-03")
        self.assertEqual((inc["severity"], inc["state"]), ("orange", "escalated"))
        self.assertEqual(noc.incident_list(nd)[0]["id"], "inc-fr-s-02")  # red first: the NOC's demo order holds


class Monitor(Base):
    def test_LST_3_estate_summary(self):
        e = T["LST-3"]["expect"]
        s = M.summary(NOW, "compute", "estate", "24h")
        st = {p["pillar"]: p["status"] for p in s["pillars"]}
        self.assertEqual(st["performance"], e["performance_status"])
        self.assertEqual(st["security"], e["security_status"])
        self.assertEqual(s["findings"][0]["object"], e["first_finding_object"])
        out = {f["id"]: f["outcome"] for f in M.findings(NOW)}
        for k, v in e["outcomes"].items():
            self.assertEqual(out[k], v, k)
        self.assertNotIn("score", {k for p in s["pillars"] for k in p})  # never one combined score

    def test_LST_4_seven_days_adds_what_a_day_cannot(self):
        e = T["LST-4"]["expect"]
        week = M.findings_under(NOW, "estate", (), None, "7d")
        self.assertEqual({f["object"]: f["kind"] for f in week}, e["kinds"])
        day = {(f["object"], f["pillar"]) for f in M.findings_under(NOW, "estate", (), None, "24h")}
        self.assertFalse(day & {(f["object"], f["pillar"]) for f in week})

    def test_LST_5_group_by_host_model(self):
        rows = M.group_by(E, "compute", "ld", "host_model", NOW, "7d")
        got = {r["value"]: r["wider_than_numa_node"] for r in rows}
        self.assertEqual(got, T["LST-5"]["expect"]["group_by_host_model_wider_than_numa_node"])

    def test_LST_6_calendar_explains(self):
        f = M.summary(NOW, "compute", "estate", "24h")["findings"]
        self.assertTrue(f[-1].get("explained_by"))
        self.assertEqual(f[-1]["explained_by"]["kind"], T["LST-6"]["expect"]["explained_by_kind"])

    def test_findings_show_under_their_ancestors_only(self):
        fr = [f["id"] for f in M.findings_under(NOW, "emea", (), None, "24h")]
        self.assertIn("f-fr-s-02", fr)
        self.assertNotIn("f-sg-s-04", fr)
        self.assertIn("f-sg-silver-waste", [f["id"] for f in M.findings_under(NOW, "sg", (), None, "24h")])

    def test_tree_sorts_by_activity_and_counts_cases(self):
        t = M.tree(NOW, "compute", "estate", "monitor", "summary", "24h")
        self.assertEqual(t["children"][0]["status"], "red")
        t = M.tree(NOW, "compute", "estate", "troubleshoot", "summary", "24h")
        self.assertEqual(t["children"][0]["id"], "apj")  # two open cases: T-2 and L-2
        self.assertEqual(t["children"][0]["open_cases"], 2)

    def test_stale_location_is_grey_never_green(self):
        t = M.tree(NOW, "compute", "emea", "monitor", "performance", "24h", ("E-7",))
        self.assertEqual({c["status"] for c in t["children"]}, {"no_data"})

    def test_vm_page_shows_both_realms(self):
        d = M.pillar_view(NOW, "compute", "sg-app-117", "performance", "24h")
        self.assertEqual((d["realms"]["vm"]["status"], d["realms"]["guest_os"]["status"]), ("green", "red"))


class Troubleshoot(Base):
    def test_LST_7_complaint_and_chain(self):
        e = T["LST-7"]["expect"]
        self.assertEqual(C.act(NOW, [], {"trigger": "complaint", "requester": "x", "symptom": "slow", "since": "now - 1 hours"})[0], e["complaint_without_vm"])
        self.assertEqual(C.act(NOW, [], {"trigger": "complaint", "vm": "General ledger", "requester": "x", "symptom": "slow", "since": "now - 1 hours"})[0],
                         e["complaint_with_application_name_only"])
        code, out = C.act(NOW, [], {"trigger": "complaint", "vm": "sg-gl-db-01", "requester": "General ledger owner", "symptom": "slow",
                                    "since": "now - 65 minutes", "fine_until": "now - 26 hours"})
        self.assertEqual(code, 200)
        cid = out["id"]
        self.assertEqual(C.detail(NOW, cid)["trigger"], e["case_trigger"])
        order = []
        while True:
            link = C.act(NOW, [cid, "propose"], {})[1]["link"]
            if not link:
                break
            order.append(link["id"])
        self.assertEqual(order, e["proposals_in_order"])
        self.assertIn(e["after_all"], C.act(NOW, [cid, "propose"], {})[1]["message"])
        self.assertEqual(C.act(NOW, [cid, "links", "t1-guest", "rule-out"], {})[0], e["rule_out_without_reason"])
        full = {"root_cause": "Snapshot left by the backup", "corrective_action": "Consolidate; fix the job",
                "detection": "new_check_rule", "detection_note": "Snapshot older than its backup job"}
        self.assertEqual(C.act(NOW, [cid, "close"], full)[0], e["close_without_confirmed_main"])
        expert = {x["id"]: x["expert"] for x in STORIES["T-1"]["plant"]["chain"]}
        for lid, verdict in expert.items():
            if verdict == "confirmed":
                C.act(NOW, [cid, "links", lid, "confirm"], {})
            else:
                C.act(NOW, [cid, "links", lid, "rule-out"], {"reason": "the evidence"})
        d = C.detail(NOW, cid)
        self.assertEqual(d["root_cause_prefill"], next(x["cause"] for x in STORIES["T-1"]["plant"]["chain"] if x["id"] == "t1-backup"))
        self.assertEqual(C.act(NOW, [cid, "close"], {k: v for k, v in full.items() if k != "detection"})[0], e["close_missing_detection"])
        self.assertEqual(C.act(NOW, [cid, "close"], full)[0], e["close_complete"])
        self.assertTrue(any(datetime.fromisoformat(x["at"]) < datetime.fromisoformat(d["window_from"]) for x in d["timeline"]))
        self.assertEqual(C.rule_drafts(NOW)[0]["detection"], "new_check_rule")
        self.assertFalse(any(x["kind"] == "pcm_action" and x["object"].startswith(cid) for x in C.detail(NOW, cid)["timeline"]))

    def test_LST_8_escalation_is_a_case(self):
        e = T["LST-8"]["expect"]
        ids = {c["id"]: c for c in C.list_cases(NOW)}
        self.assertEqual(ids["case-inc-tk-s-03"]["trigger"], e["t2_case_trigger"])
        self.assertNotIn("case-inc-fr-s-02", ids)
        noc.act(noc.build(NOW), ["incidents", "inc-fr-s-02", "escalate"], {})
        d = C.detail(NOW, "case-inc-fr-s-02")
        self.assertEqual(d["trigger"], "escalation")
        self.assertEqual(d["escalation"]["villains"][0]["vm"], "fr-bat-017")
        self.assertEqual(C.act(NOW, ["case-inc-fr-s-02", "reject"], {})[0], e["reject_without_reason"])
        self.assertEqual(C.act(NOW, ["case-inc-fr-s-02", "accept"], {})[0], 200)
        for _ in range(4):
            C.act(NOW, ["case-inc-fr-s-02", "propose"], {})
        C.act(NOW, ["case-inc-fr-s-02", "links", "l1-class", "confirm"], {})
        code, _ = C.act(NOW, ["case-inc-fr-s-02", "close"], {"root_cause": "Bronze batch VM in a Silver cluster", "corrective_action": "Move it",
                                                              "detection": "new_check_rule", "detection_note": "Class check on placement"})
        self.assertEqual(code, 200)
        self.assertEqual(next(i for i in noc.build(NOW)["incidents"] if i["id"] == "inc-fr-s-02")["state"], "closed")
        t2 = [x["id"] for x in STORIES["T-2"]["plant"]["chain"]]
        got = [C.act(NOW, ["case-inc-tk-s-03", "propose"], {})[1]["link"]["id"] for _ in t2]
        self.assertEqual(got, STORIES["T-2"]["expect"]["proposals_in_order"])

    def test_LST_9_finding_opens_a_case(self):
        e = T["LST-9"]["expect"]
        code, out = C.act(NOW, [], {"trigger": "finding", "finding": "f-m1-remote-memory"})
        self.assertEqual(code, 200)
        d = C.detail(NOW, out["id"])
        self.assertEqual((d["trigger"], d["object"]), (e["m1_case_trigger"], STORIES["M-1"]["objects"]["vm"]))
        got = [C.act(NOW, [out["id"], "propose"], {})[1]["link"]["id"] for _ in e["m1_proposals"]]
        self.assertEqual(got, e["m1_proposals"])
        self.assertEqual(next(f for f in M.findings(NOW) if f["id"] == "f-m1-remote-memory")["case"], out["id"])
        self.assertEqual(C.act(NOW, [], {"trigger": "finding", "finding": "f-m1-remote-memory"})[1]["id"], out["id"])
        self.assertEqual(C.act(NOW, [], {"trigger": "finding", "finding": "f-sg-silver-waste"})[0], 400)  # an opportunity, not a case

    def test_LST_10_guest_os_hand_over(self):
        e = T["LST-10"]["expect"]
        d = C.detail(NOW, "case-sg-app-117")
        self.assertEqual(d["trigger"], e["case_trigger"])
        self.assertIn("inside the Guest OS", d["hand_over"])
        self.assertEqual((d["realms"]["vm"]["status"], d["realms"]["guest_os"]["status"]), (e["vm_status"], e["guest_os_status"]))

    def test_generic_complaint_runs_the_sp5_order(self):
        vm = next(n["id"] for n in E.nodes.values() if n["kind"] == "vm" and not n.get("story") and n["base"] > 90)
        cid = C.act(NOW, [], {"trigger": "complaint", "vm": vm, "requester": "x", "symptom": "slow", "since": "now - 2 hours"})[1]["id"]
        links = [C.act(NOW, [cid, "propose"], {})[1]["link"] for _ in range(4)]
        self.assertEqual([x["step"] for x in links], ["contention", "contention", "configuration", "log"])
        self.assertIn("Nothing in vSphere", links[-1]["cause"])
        self.assertIn("application owner", C.detail(NOW, cid)["hand_over"])

    def test_LST_11_repeated_problem_loop(self):
        e = T["LST-11"]["expect"]
        rep = lambda: next(r for r in l2.monthly(NOW)["repeated_escalations"] if r["type"] == "class_mismatch")["loop_closed"]
        self.assertEqual(rep(), e["class_mismatch_closed_before"])
        noc.act(noc.build(NOW), ["incidents", "inc-fr-s-02", "escalate"], {})
        C.act(NOW, ["case-inc-fr-s-02", "propose"], {})
        C.act(NOW, ["case-inc-fr-s-02", "links", "l1-wait", "confirm"], {})
        C.act(NOW, ["case-inc-fr-s-02", "close"], {"root_cause": "Bronze batch VM in a Silver cluster", "corrective_action": "Move it",
                                                    "detection": "new_check_rule", "detection_note": "Class check on placement"})
        self.assertEqual(rep(), e["class_mismatch_closed_after_close"])

    def test_LST_16_log_validation(self):
        for msg, verdict in T["LST-16"]["expect"].items():
            self.assertEqual("noise" if C.log_validation(msg, SETTINGS)["noise"] else "rare", verdict)

    def test_agent_calls_are_recorded(self):
        with mock.patch.dict(os.environ, {"PCM_AGENT_E2_MODE": "mock"}):
            code, out = C.act(NOW, ["case-sg-app-117", "draft"], {})
        self.assertEqual((code, out["record"]["actor_agent"]), (200, "agent-e2"))

    def test_suggest_sends_the_page_kpis_to_agent_e2(self):
        """D-124: on a release 1.0 page PCM sends the KPI series, points only, and shows Agent E2's questions; elsewhere no call."""
        seen = {}
        def fake(url, body, timeout):
            seen["url"], seen["body"] = url, body
            return {"situation": {"level": "bad", "movement": "declining"}, "questions": ["Why is performance declining?", "a", "b", "c"]}
        cl = E.nodes["SG-S-01"]
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = A.suggest(NOW, {"context": {"kind": "page", "object": cl["id"], "pillar": "performance", "window": "24h"}})
        self.assertEqual((code, out["source"], len(out["questions"])), (200, "service", 3))
        self.assertTrue(seen["url"].endswith("/v1/suggest"))
        f = seen["body"]["facts"]
        self.assertEqual((f["object"]["kind"], f["pillar"]), ("cluster", "Performance"))
        self.assertEqual([k["label"] for k in f["kpis"]], ["Cluster Performance", "Cluster Risk"])
        self.assertTrue(all(set(k) == {"label", "better", "unit", "first_point", "point_minutes", "values"} for k in f["kpis"]))  # no band, no verdict
        self.assertEqual(set(f), {"object", "pillar", "window", "kpis"})
        seen.clear()
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = A.suggest(NOW, {"context": {"kind": "page", "object": cl["id"], "pillar": "security", "window": "24h"}})
        self.assertEqual((out["source"], out["questions"], seen), ("not_in_release", [], {}))
        code, _ = A.suggest(NOW, {"context": {"kind": "finding", "object": cl["id"]}})
        self.assertEqual(code, 400)

    def test_kpi_question_sends_hourly_parts_and_the_other_kpi_series(self):
        """D-125: Agent E2 needs the parts over time and the other KPI's line to explain a change of level."""
        code, got = A.facts_for(NOW, {"kind": "kpi", "view": "compute", "object": "SG-S-01", "pillar": "performance", "window": "24h",
                                      "metric": "cluster_risk"}, ("M-5",))
        f = got["facts"]
        h = f["asked_about_kpi"]["parts_hourly"]
        self.assertEqual(len(h["times"]), 24)
        self.assertTrue(all(len(r["hourly"]) == 24 and "score" not in r for r in h["rows"]))
        o = f["other_kpis"][0]
        self.assertEqual((o["label"], len(o["values"]), o["point_minutes"]), ("Cluster Performance", 288, 5))
        self.assertEqual([c["kind"] for c in f["calendar_in_window"]], ["release"])

    def test_card_suggestion_sends_the_card_facts(self):
        """D-127: a card's showcase question is Agent E2's, from the facts a question about the card would send."""
        seen = {}
        def fake(url, body, timeout):
            seen.update(body)
            return {"question": "Risk went from green to yellow, but Performance did not drop. Explain to me why.", "card": "Cluster Risk"}
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = A.suggest(NOW, {"context": {"kind": "kpi", "object": "SG-S-01", "pillar": "performance", "window": "24h",
                                                   "metric": "cluster_risk"}}, ("M-5",))
        self.assertEqual((code, len(out["questions"])), (200, 1))
        self.assertEqual(seen["card"], {"kind": "kpi", "name": "Cluster Risk"})
        self.assertIn("parts_hourly", seen["facts"]["asked_about_kpi"])

    def test_suggest_without_agent_e2(self):
        cl = E.nodes["SG-S-01"]
        with mock.patch.dict(os.environ, {"PCM_AGENT_E2_URL": "http://127.0.0.1:9"}):
            code, out = A.suggest(NOW, {"context": {"kind": "page", "object": cl["id"], "pillar": "capacity", "window": "24h"}})
        self.assertEqual((code, out["source"], out["questions"]), (200, "unavailable", []))

    def test_LST_27_agent_e2_facts_rebuilt_by_pcm(self):
        """LST-27 (D-097): the facts come from PCM, never from the browser; the question is recorded with both identity fields."""
        t, seen = T["LST-27"], {}
        e = t["expect"]
        def fake(url, body, timeout):
            seen.clear(); seen.update(body)
            return {"type": "answer", "content": "Not a shortage on fr-svc-5526; check fr-esx-218.", "files_read": ["guest-os/cpu/metrics/run-queue"],
                    "lead": "Run queue is 1.5 threads waiting.", "computed": ["0.38 per vCPU"], "model": "m", "knowledge_commit": "abc"}
        g = t["given"]["metric"]
        ctx = {"kind": "metric", "object": g["object"], "pillar": g["pillar"], "window": g["window"], "layer": g["layer"], "metric": g["metric"],
               "now": g["now_sent_by_browser"]}
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = A.ask(NOW, {"question": "Is it a problem?", "context": ctx})
        self.assertEqual(code, 200)
        self.assertEqual(out["lead"], "Run queue is 1.5 threads waiting.")  # D-119: the opening reaches the panel
        facts = seen["facts"]
        m = facts["asked_about_metric"]
        keys = set(facts) | set(m) | set(facts["object"]) | {"metric" if m.get("name") else None, "layer_status" if facts.get("layer_status") else None,
                                                             "calendar" if "calendar_in_window" in facts else None}
        for k in e["metric_facts"]:
            self.assertIn(k, keys, k)
        self.assertEqual(m["name"], "Peak vCPU run queue length")
        self.assertNotEqual(m["now"], g["now_sent_by_browser"])  # the browser's number is ignored
        self.assertEqual(len(m["values"]), 288)
        self.assertEqual(seen["role"], e["role"])
        r = out["record"]
        self.assertEqual((r["action"], r["actor_agent"], r["actor_human"]), (e["recorded"]["action"], e["recorded"]["actor_agent"], e["recorded"]["actor_human"]))
        self.assertEqual([x["id"] for x in out["links"]], ["fr-svc-5526", "fr-esx-218"])
        self.assertEqual(out["label"], "Peak vCPU run queue length · fr-svc-5526 · Performance · Last 24 hours")
        # a finding and a case link: their own facts
        f = M.findings(NOW)[0]
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = A.ask(NOW, {"question": "Explain this finding.", "context": {"kind": "finding", "finding": f["id"]}})
        self.assertEqual((code, seen["facts"]["finding"]["id"], out["finding"]["id"]), (200, f["id"], f["id"]))
        chain = C.detail(NOW, "case-sg-app-117")["chain"]
        link = chain[0] if chain else C.act(NOW, ["case-sg-app-117", "propose"], {})[1]["link"]
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = A.ask(NOW, {"question": "Is the platform the cause?", "context": {"kind": "link", "case": "case-sg-app-117", "link": link["id"]}})
        self.assertEqual((code, seen["facts"]["asked_about_link"]["id"]), (200, link["id"]))
        self.assertIn("inside the Guest OS", seen["facts"]["case"]["hand_over"])
        # a clarifying round: the turns go to the service
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            A.ask(NOW, {"question": "The VM one", "context": {"kind": "case", "case": "case-sg-app-117"}, "turns": ["Which counter?", "Guest OS or VM?", "The VM one"]})
        self.assertEqual(seen["turns"], ["Which counter?", "Guest OS or VM?", "The VM one"])
        # the whole conversation goes with a follow-up, every turn (D-128)
        hist = [{"question": f"Q{i}?", "answer": f"A{i}."} for i in range(30)]
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            A.ask(NOW, {"question": "Explain again.", "context": {"kind": "case", "case": "case-sg-app-117"}, "history": hist})
        self.assertEqual(seen["history"], hist)
        # the topic choice goes as sent (D-129); auto when none; any other value is refused
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            A.ask(NOW, {"question": "Why?", "context": {"kind": "case", "case": "case-sg-app-117"}, "history": hist, "topic_choice": "new"})
        self.assertEqual(seen["topic_choice"], "new")
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            A.ask(NOW, {"question": "Why?", "context": {"kind": "case", "case": "case-sg-app-117"}})
        self.assertEqual(seen["topic_choice"], "auto")
        self.assertEqual(A.ask(NOW, {"question": "Why?", "context": {"kind": "case", "case": "case-sg-app-117"}, "topic_choice": "maybe"})[0], 400)
        self.assertEqual(A.ask(NOW, {"question": "Why?", "context": {"kind": "case", "case": "case-sg-app-117"}, "history": [{"question": "Q"}]})[0], 400)
        # the topic decision alone, before the answer (D-130): sent to /v1/topic; none from an older service or a down one
        calls = []
        def topic_fake(url, body, timeout):
            calls.append(url)
            return {"continues": False, "by": "model"}
        with mock.patch("build.pcm_proto.agent_e2._post_raw", topic_fake):
            self.assertEqual(A.topic({"question": "What is VM CPU Ready?", "history": hist[:1]}), (200, {"continues": False, "by": "model", "source": "service"}))
            self.assertEqual(A.topic({"question": "Why?"})[1]["by"], "first")
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].endswith("/v1/topic"))
        self.assertEqual(A.topic({"question": " ", "history": hist})[0], 400)
        self.assertEqual(A.topic({"question": "Why?", "history": [{"question": "Q"}]})[0], 400)
        with mock.patch.dict(os.environ, {"PCM_AGENT_E2_URL": "http://127.0.0.1:9"}):
            self.assertEqual(A.topic({"question": "Why?", "history": hist[:1]})[1]["continues"], None)
        # refusals and the service down
        self.assertEqual(A.ask(NOW, {"question": "x", "context": {"kind": "nope"}})[0], e["unknown_context"])
        self.assertEqual(A.ask(NOW, {"question": "x", "context": {**ctx, "metric": "no_such_metric"}})[0], e["unknown_metric"])
        self.assertEqual(A.ask(NOW, {"question": " ", "context": ctx})[0], 400)
        with mock.patch.dict(os.environ, {"PCM_AGENT_E2_URL": "http://127.0.0.1:9"}):
            code, out = A.ask(NOW, {"question": "Why?", "context": {"kind": "case", "case": "case-sg-app-117"}})
            self.assertFalse(A.health(SETTINGS)["available"])
        self.assertEqual((code, out["source"], out["content"]), (e["service_down"]["status"], e["service_down"]["source"], e["service_down"]["content"]))
        import io, urllib.error
        def model_down(url, body, timeout):
            raise urllib.error.HTTPError(url, e["model_down"]["service_status"], "Bad Gateway", {}, io.BytesIO(b'{"error": "model unavailable"}'))
        with mock.patch("build.pcm_proto.agent_e2._post_raw", model_down):
            code, out = A.ask(NOW, {"question": "Why?", "context": {"kind": "case", "case": "case-sg-app-117"}})
        self.assertEqual((code, out["source"], out["content"]), (200, e["model_down"]["source"], e["model_down"]["content"]))


    def test_LST_28_whole_page_question_carries_the_page(self):
        """LST-28 (D-097): an overall question is answered from the numbers on screen."""
        t = T["LST-28"]; g, e = t["given"], t["expect"]
        code, got = A.facts_for(NOW, g["vm_performance"])
        f = got["facts"]
        self.assertEqual(code, 200)
        self.assertEqual([x["layer"] for x in f["layers"]], e["vm_performance_layers"])
        self.assertEqual(sum(len(x["metrics"]) for x in f["layers"]), e["vm_performance_metrics"])
        self.assertTrue(all("values" not in m and "worst" in m and "percentile_95" in m for x in f["layers"] for m in x["metrics"]))
        code, got = A.facts_for(NOW, g["vm_summary"])
        self.assertEqual([x["pillar"] for x in got["facts"]["pillars"]], e["vm_summary_pillars"])
        code, got = A.facts_for(NOW, g["vm_layer"])
        f = got["facts"]
        self.assertEqual((code, got["label"]), (200, "Guest OS layer · fr-svc-5526 · Performance · Last 24 hours"))
        self.assertEqual(sum(1 for m in f["asked_about_layer"]["metrics"] if len(m["values"]) == 288), e["vm_layer_metrics_with_points"])
        self.assertTrue(all("values" not in m for x in f["other_layers"] for m in x["metrics"]))
        self.assertEqual(A.facts_for(NOW, {**g["vm_layer"], "layer": "no_such_layer"})[0], e["unknown_layer"])

    def test_LST_32_vm_capacity_is_the_vms_own(self):
        """D-126: a VM's Capacity tab reads the VM's counters, never its cluster's."""
        t = T["LST-32"]; g, e = t["given"], t["expect"]
        d = M.pillar_view(NOW, "compute", g["vm"], "capacity", g["window"])
        c = d["capacity"]
        self.assertEqual(c["kind"], e["kind"])
        self.assertEqual([m["key"] for m in c["metrics"]], e["metrics"])
        self.assertEqual([m["label"] for m in c["metrics"]], e["labels"])
        for m in c["metrics"]:
            want = e["band_ends"][m["key"]]
            self.assertEqual(m.get("band_ends", "none"), "none" if want == "none" else want, m["key"])
        self.assertEqual([x["key"] for x in c["remaining"]["values"]], e["remaining"])
        for w in e["forbidden_fields"]:
            self.assertNotIn(w, c, w)
        perf = {m["key"]: m for layer in M.pillar_view(NOW, "compute", g["vm"], "performance", g["window"])["layers"] for m in layer["metrics"]}
        by = {m["key"]: m for m in c["metrics"]}
        for k in e["same_points_as_performance_tab"]:
            self.assertEqual(by[k]["points"], perf[k]["points"], k)
        free = perf["free_memory_mb"]["points"]
        used = by["guest_os_used_memory_mb"]["points"]
        self.assertTrue(all(u["v"] + f["v"] == d["capacity"]["memory_gb"] * 1024 for u, f in zip(used, free)))

    def test_LST_31_every_question_carries_the_screen(self):
        """LST-31 (D-103): Agent E2 is told what the person sees, not only the data; whether a move is a drop is Agent E2's."""
        t = T["LST-31"]; g, e = t["given"], t["expect"]
        code, got = A.facts_for(NOW, g["kpi"])
        self.assertEqual(code, 200)
        self.assertEqual(next(iter(got["facts"])), e["first_key"])
        s = got["facts"]["screen"]
        self.assertEqual((s["asked_by"], s["page"], s["clicked"]), (e["asked_by"], e["kpi_page"], e["kpi_clicked"]))
        self.assertIn(f"one point every {e['kpi_point_minutes']} minutes", s["card_shows"])
        self.assertIn(e["kpi_belongs_to"], s["kpi_belongs_to"])
        self.assertEqual(s["drill_down"]["page"], e["kpi_drill_down_page"])
        self.assertIn(e["kpi_drill_down_shows"], s["drill_down"]["shows"])
        self.assertEqual("not_shown_yet" not in s["drill_down"], e["kpi_nothing_not_shown"])
        # D-111: the parts at the KPI's worst point, the values the Details fold shows, no score or ranking.
        m5 = A.facts_for(NOW, g["kpi_m5"])[1]["facts"]["asked_about_kpi"]
        pw, x = m5["parts_at_worst"], e["kpi_parts_at_worst"]
        self.assertEqual((len(pw["parts"]), pw["time"], pw["kpi_value"], pw["parts"][0]["name"]),
                         (x["count"], x["time"], x["kpi_value"], x["first_part"]))
        self.assertEqual(pw["time"], m5["worst"]["t"])
        self.assertTrue(all(set(e["kpi_part_fields"]) <= set(p) for p in pw["parts"]))
        self.assertFalse(any(k in p for p in pw["parts"] for k in ("score", "band", "rank")))
        flat = json.dumps(got["facts"]).lower()
        self.assertEqual(not re.search(r"\b(?:verdict|steady|drop)\b", flat), e["no_drop_verdict_from_pcm"])  # "dropped" packets is a part name
        self.assertEqual(A.facts_for(NOW, g["metric"])[1]["facts"]["screen"]["clicked"], e["metric_clicked"])
        self.assertEqual(A.facts_for(NOW, g["page"])[1]["facts"]["screen"]["clicked"], e["page_clicked"])
        # D-117: the KPIs at the top of a cluster's and an ESXi host's Performance tab, with their parts at the worst point.
        for ctx, n in zip(g["perf_kpis"], e["perf_kpi_parts"]):
            code, pk = A.facts_for(NOW, ctx)
            self.assertEqual(code, 200, ctx)
            k, s = pk["facts"]["asked_about_kpi"], pk["facts"]["screen"]
            self.assertEqual(s["clicked"], e["perf_kpi_clicked"].format(label=k["label"]))
            self.assertIn(e["perf_kpi_page_tab"], s["page"])
            self.assertEqual(len(k["parts_at_worst"]["parts"]), n)
            self.assertEqual(k["parts_at_worst"]["time"], k["worst"]["t"])


class Improve(Base):
    def test_LST_12_policy_change(self):
        e = T["LST-12"]["expect"]
        prop = STORIES["L-4"]["plant"]["proposed_policy"]
        t = "move_vms_between_clusters"
        self.assertEqual(l2.act(NOW, ["proposals", "p-move-sg-s-04", "reject"], {})[0], e["reject_without_reason"])
        self.assertEqual(l2.act(NOW, ["policies", t, "publish"], {**prop, "reason": "x"})[0], e["publish_without_replay"])
        rep = l2.act(NOW, ["policies", t, "replay"], prop)[1]
        self.assertEqual((rep["would_run_automatically"], rep["stopped"]), (e["replay_would_run"], e["replay_stopped"]))
        self.assertEqual(l2.act(NOW, ["policies", t, "publish"], prop)[0], e["publish_without_reason"])
        self.assertEqual(l2.act(NOW, ["policies", t, "publish"], {**prop, "reason": "Guardrails replace approval"})[0], 200)
        o = next(x for x in I.opportunities(NOW) if x["id"] == "o-sg-s-04-rebalance")
        self.assertEqual((o["proposal"]["state"], o["proposal"]["accountable"]), (e["proposal_state_after"], e["accountable_after"]))
        self.assertFalse(any(h["action"] == "approve" and h["target"] == "p-move-sg-s-04" for h in noc.STATE.history))

    def test_LST_13_configuration_scoped(self):
        e = T["LST-13"]["expect"]
        self.assertEqual(len(I.view(NOW, "compute", "VA-G-05", "configuration", "30d")["configuration"]["correct_it"]), e["correct_it_under_VA-G-05"])
        self.assertEqual(len(I.view(NOW, "compute", "sg", "configuration", "30d")["configuration"]["correct_it"]), e["correct_it_under_sg"])
        self.assertTrue(l2.act(NOW, ["configuration", "c-va-esx-142-1", "decide"], {"choice": "fix_the_setting"})[1]["proposal"])
        self.assertEqual(l2.act(NOW, ["configuration", "c-va-esx-142-2", "decide"], {"choice": "fix_the_standard"})[1]["standard_version"], 2)

    def test_LST_14_decision_register(self):
        e = T["LST-14"]["expect"]
        d = I.view(NOW, "compute", "estate", "summary", "30d")["decisions"]
        self.assertEqual({x["id"]: x["state"] for x in d}, e["decisions"])
        self.assertEqual(d[0]["id"], "d-snapshots")
        self.assertEqual(l2.act(NOW, ["monthly", "decisions"], {"what": "x", "due": "2026-11-30"})[0], e["decision_without_owner"])
        self.assertNotIn("decisions", I.view(NOW, "compute", "sg", "summary", "30d"))

    def test_LST_15_changes_under_the_object(self):
        e = T["LST-15"]["expect"]
        c = M.inventory_content(E, "compute", "estate", NOW, "24h")
        self.assertEqual(c["unexplained"][0]["id"], e["unexplained_first_under_estate"])
        self.assertEqual([x["id"] for x in M.inventory_content(E, "compute", "tk", NOW, "24h")["unexplained"]], e["under_tk"])
        self.assertEqual(l2.act(NOW, ["inventory", "chg-tk-deleted", "expected"], {})[0], e["expected_without_reason"])
        self.assertEqual(l2.act(NOW, ["inventory", "chg-tk-deleted", "expected"], {"reason": "Decommissioning, request filed late"})[0], 200)
        c = M.inventory_content(E, "compute", "tk", NOW, "24h")
        self.assertEqual([x["explanation"] for x in c["expected_by_l2"]], [e["expected_with_reason_explained_by"]])

    def test_improve_never_shows_money(self):
        text = str(I.view(NOW, "compute", "estate", "summary", "30d"))
        self.assertNotRegex(text, r"\$|USD|\bcost\b|\bprice\b")


class PerformanceTab(Base):
    """M-3: the Performance tab above the cluster, VM then Cluster (D-091)."""

    @classmethod
    def setUpClass(cls):
        cls.d = P.view(NOW, "compute", "estate", "24h", enable=())

    def _at(self, rel):
        t = generator.rel(rel, NOW).isoformat()
        return next(p for p in self.d["provider"]["performance"] if p["t"] >= t)

    def test_LST_17_actual_slowness(self):
        e = T["LST-17"]["expect"]
        self.assertEqual(self.d["class"], e["default_class"])
        self.assertEqual(self.d["provider"]["clusters"], e["gold_clusters"])
        self.assertEqual(P.view(NOW, "compute", "estate", "24h", "all")["provider"]["clusters"], e["all_clusters"])
        n = self._at(e["at_narrow"]["at"])
        self.assertEqual((n["worst_cluster"], P.perf_band(n["worst"]), P.perf_band(n["percentile"])),
                         (e["at_narrow"]["worst_cluster"], e["at_narrow"]["worst_band"], e["at_narrow"]["percentile_band"]))
        w = self._at(e["at_wide"]["at"])
        self.assertEqual((P.perf_band(w["worst"]), P.perf_band(w["percentile"])), (e["at_wide"]["worst_band"], e["at_wide"]["percentile_band"]))
        self.assertTrue(self.d["selected"]["default"])
        self.assertEqual(self.d["clusters_at"][0]["cluster"], e["default_selected"]["cluster_first"])
        lo, hi = (generator.rel(x, NOW) for x in e["default_selected"]["within"])
        self.assertTrue(lo <= datetime.fromisoformat(self.d["selected"]["t"]) <= hi + timedelta(minutes=5))

    def test_LST_18_potential_slowness(self):
        e = T["LST-18"]["expect"]
        r = self.d["provider"]["risk"][-1]
        self.assertEqual((r["worst_cluster"], P.risk_band(r["worst"]), P.risk_band(r["percentile"])),
                         (e["highest_now"], e["highest_band"], e["percentile_band"]))

    def test_LST_19_taking_turns_and_together(self):
        e = T["LST-19"]["expect"]
        s = P._cluster_series((), NOW.isoformat(), "24h")["VA-G-03"]
        row = next(r for r in self.d["clusters_at"] if r["cluster"] == "VA-G-03")
        self.assertGreaterEqual(s["different"], e["VA-G-03"]["different_vms_at_least"])
        self.assertLessEqual(max(s["hit"]), e["VA-G-03"]["most_at_once_at_most"])
        self.assertEqual(row["performance_band"], e["VA-G-03"]["performance_band_at_default"])
        c = self.d["consumer"]
        self.assertGreaterEqual(c["most_at_once"], e["most_at_once_at_least"])
        lo, hi = (generator.rel(x, NOW) for x in e["most_at_within"])
        self.assertTrue(lo <= datetime.fromisoformat(c["most_at"]) <= hi + timedelta(minutes=5))
        self.assertTrue(all(v["together"] >= 0 and v["cluster"] for v in c["worst_vms"]))

    def test_LST_20_time_and_class_are_checked(self):
        from build.pcm_proto import server
        q = lambda **k: {key: [v] for key, v in k.items()}
        for query in (q(**{"class": "platinum"}), q(at=(NOW - timedelta(days=3)).isoformat()), q(**{"class": "gold"}, at="yesterday")):
            with self.assertRaises(ValueError):
                server.l2_get(["monitor", "compute", "estate", "performance"], NOW, (), query)
        with self.assertRaises(ValueError):
            server.l2_get(["monitor", "compute", "estate", "security"], NOW, (), q(**{"class": "gold"}))
        t = self.d["provider"]["performance"][100]["t"]
        d = server.l2_get(["monitor", "compute", "estate", "performance"], NOW, (), q(at=t))["perf"]
        self.assertEqual((d["selected"]["index"], d["selected"]["default"], d["consumer"]["worst_vms_mode"]), (100, False, "at"))

    def test_LST_21_a_vm_has_two_layers_with_statistics_and_units(self):
        e = T["LST-21"]["expect"]
        d = M.pillar_view(NOW, "compute", T["LST-21"]["given"]["object"], "performance", T["LST-21"]["given"]["window"], "host_model")
        self.assertEqual([l["key"] for l in d["layers"]], e["layer_order"])
        self.assertNotIn("group_by", d)
        self.assertEqual([m["key"] for m in d["layers"][0]["metrics"]], e["guest_os_metrics"])
        self.assertEqual([m["key"] for m in d["layers"][1]["metrics"]], e["virtual_motherboard_metrics"])
        realm = {**d["realms"]["guest_os"], **d["realms"]["vm"]}
        for l in d["layers"]:
            for m in l["metrics"]:
                vals = [p["v"] for p in m["points"]]
                self.assertEqual(len(vals), e["points"])
                self.assertEqual(m["now"], realm[m["key"]])
                self.assertEqual(m["worst"]["v"], min(vals) if m["better"] == "higher" else max(vals))
                self.assertTrue({"now", "worst", "percentile_95"} <= set(m) and "average" not in m)
                self.assertTrue(m["label"][0].isupper() and not any(u in m["label"] for u in ("percent", " ms", "per s")), m["label"])
                self.assertTrue(m["unit"].strip(), m["key"])
        self.assertIsNone(M.pillar_view(NOW, "compute", "sg-app-117", "inventory", "24h"))
        self.assertIsNotNone(M.pillar_view(NOW, "compute", "fr", "inventory", "24h"))
        self.assertNotIn("inventory", [r["pillar"] for r in M.summary(NOW, "compute", "sg-app-117", "24h")["pillars"]])

    def test_performance_tab_only_above_the_cluster(self):
        self.assertIn("perf", M.pillar_view(NOW, "compute", "fr", "performance", "24h"))
        self.assertNotIn("perf", M.pillar_view(NOW, "compute", "FR-G-04", "performance", "24h"))


class CapacityTab(Base):
    """The Capacity tab (D-094, D-095, D-096): LCAT-12 to LCAT-16, LST-22 to LST-26."""

    def test_LCAT_12_the_rule_gives_the_adapters_answers(self):
        for r in T["LCAT-12"]["given"]["rows"]:
            d = CAP.decide(r["performance"], r["risk"], r["consumption"])
            e = r["expect"]
            if "state" in e:
                self.assertEqual(d["state"], e["state"], r)
                continue
            self.assertEqual(d["close"], e["close"], r)
            if "rule" in e:
                self.assertEqual(d["rule"], e["rule"], r)

    def test_LCAT_13_statistics_and_their_names(self):
        e = T["LCAT-13"]["expect"]
        xs = list(range(1, 289))
        self.assertEqual(P.nearest_rank(xs, 95), e["percentile_95_higher_is_worse"])
        self.assertEqual(-P.nearest_rank([-x for x in xs], 95), e["percentile_95_higher_is_better"])
        times = [str(i) for i in xs]
        self.assertEqual(CAP.figures(xs, times, True)["worst"]["v"], e["worst_higher_is_worse"])
        self.assertEqual(CAP.figures(xs, times, False)["worst"]["v"], e["worst_higher_is_better"])
        self.assertEqual(CAP.figures(xs, times, False)["percentile_95"], e["percentile_95_higher_is_better"])
        self.assertNotIn("average", CAP.figures(xs, times, True))
        self.assertEqual(CAP.check_label(5, 24), e["label_worst_percent_5"])
        self.assertEqual(CAP.check_label(10, 24), e["label_worst_percent_10"])
        self.assertNotIn(e["label_never"], CAP.check_label(5, 24))
        self.assertEqual(CAP.check_label(5, 24, higher_is_better=True), e["label_higher_is_better_worst_percent_5"])

    def test_LCAT_14_capacity_findings(self):
        for g in T["LCAT-14"]["given"]:
            if g["state"] == "closed" and "performance" in g:
                d = CAP.decide(g["performance"], 10 if g["rule"] == 1 else 65, g["consumption"])
                self.assertEqual(d["rule"], g["rule"], g)
                self.assertEqual(CAP.finding_kind(d), g["expect"], g)
            else:
                checks = g["consumption_checks"]
                rows = [{"consumption": v, "state": g["state"]} for v in reversed(checks)]
                want = g.get("expect_7d", g.get("expect"))
                self.assertEqual("heading_to_closed" if CAP.heading_to_closed(rows) else None, want, g)

    def test_LCAT_15_gold_first_always(self):
        self.assertEqual((P.DEFAULT_CLASS, CAP.DEFAULT_CLASS), ("gold", "gold"))
        d = M.pillar_view(NOW, "compute", "wld-fr-gen", "capacity", "7d")["capacity"]
        self.assertEqual((d["class"], d["clusters"]), ("gold", 0))

    def test_LCAT_16_highest_and_percentile_never_average(self):
        g, e = T["LCAT-16"]["given"]["consumption"], T["LCAT-16"]["expect"]
        self.assertEqual((max(g), P.nearest_rank(g, 90)), (e["highest"], e["percentile_90"]))
        d = M.pillar_view(NOW, "compute", "estate", "capacity", "24h", cls="all")["capacity"]
        self.assertTrue(all(set(p) == {"t", "highest", "highest_cluster", "percentile"} for p in d["spread"]["points"]))

    def test_LST_22_ld_b_01_closes_on_memory(self):
        e, g = T["LST-22"]["expect"], T["LST-22"]["given"]
        d = M.pillar_view(NOW, "compute", g["object"], "capacity", g["window"])["capacity"]
        ck = d["check"]
        self.assertEqual((ck["state"], ck["rule"], ck["reason"], ck["checks_closed"]),
                         (e["latest_check"]["state"], e["latest_check"]["rule"], e["latest_check"]["reason"], e["latest_check"]["checks_closed"]))
        self.assertEqual((ck["previous"]["state"], ck["previous"]["consumption"]), (e["check_before"]["state"], e["check_before"]["consumption"]))
        self.assertEqual(X.band(100 - ck["previous"]["consumption"]), e["check_before"]["consumption_band"])
        self.assertEqual([k["key"] for k in d["kpis"]], e["kpi_order"])
        for k in d["kpis"]:
            self.assertTrue({"now", "worst", "percentile_95", "check_value"} <= set(k) and "average" not in k)
        for key, start in e["check_value_labels_start"].items():
            self.assertTrue(ck["labels"][key].startswith(start), ck["labels"])
        self.assertEqual(len(d["strip"]), e["strip_cells"])
        self.assertEqual(d["strip"][-1]["state"], "closed")
        over = [p["key"] for p in d["parts"] if p["percentile_95"] > 80]
        self.assertEqual(over[0], e["parts_first_over_80"])
        self.assertEqual(list(k for k in ("total", "ha", "buffer", "usable") if k in d["usable"]["memory"]), e["usable_steps"])
        u = d["usable"]["memory"]
        self.assertEqual(u["total"] - u["ha"] - u["buffer"], u["usable"])
        self.assertEqual(sorted(k for k in d["spread"]["memory_consumed"][0] if not k.endswith("_host") and k != "t"), sorted(x.split("_")[0] for x in e["host_spread_lines"]))
        at = {h["host"]: h["memory_consumed"]["at_check_percentile_95"] for h in d["hosts"]}
        hs = e["host_spread_memory"]
        self.assertEqual(max(at, key=at.get), hs["highest"])
        self.assertEqual((at[hs["highest"]], min(at.values())), (hs["highest_percent"], hs["lowest_percent"]))
        self.assertEqual(d["hosts"][0]["host"], e["hosts_first"])
        f = [x for x in M.findings_under(NOW, g["object"], (), "capacity", "24h") if x["object"] == g["object"]]
        self.assertEqual([(x["kind"], x["window"], x["severity"], x["outcome"]) for x in f],
                         [(e["finding"]["kind"], e["finding"]["window"], e["finding"]["severity"], e["finding"]["outcome"])])
        flat = str(d).lower()
        for w in e["forbidden_fields"]:
            self.assertNotIn(f"'{w}'", flat, w)
        r = d["remaining"]
        self.assertEqual(([x["key"] for x in r["values"]], r["source"], r["placeholder"]),
                         (e["remaining"]["figures"], e["remaining"]["source"], e["remaining"]["placeholder"]))

    def test_LST_23_frankfurt_general_on_bronze(self):
        e, g = T["LST-23"]["expect"], T["LST-23"]["given"]
        d = M.pillar_view(NOW, "compute", g["object"], "capacity", g["window"], cls=g["class"])["capacity"]
        self.assertEqual(d["closed"]["now"], e["closed_latest"])
        self.assertEqual(d["near_closure"]["clusters"], e["near_closure"])
        self.assertEqual(d["near_closure"]["direction"], e["near_closure_words"])
        self.assertEqual(d["clusters_at"][0]["cluster"], e["clusters_at_first"])
        fs = {f["object"]: f for f in M.findings_under(NOW, g["object"], (), "capacity", "7d")}
        f = fs["FR-B-04"]
        self.assertEqual((f["kind"], f["window"], f["severity"], f["outcome"]), tuple(e["FR-B-04_finding"][k] for k in ("kind", "window", "severity", "outcome")))
        self.assertNotIn("FR-B-03", fs)
        self.assertNotIn("FR-X-01", [r["cluster"] for r in d["clusters_at"]])
        a = M.pillar_view(NOW, "compute", g["object"], "capacity", g["window"], cls="all")["capacity"]
        self.assertIn("FR-X-01", [r["cluster"] for r in a["clusters_at"]])
        none = M.pillar_view(NOW, "compute", g["object"], "capacity", g["window"])["capacity"]
        self.assertEqual((none["class"], none["clusters"]), (e["without_class"]["class"], 0))
        for w in e["forbidden_fields"]:
            self.assertNotIn(f"'{w}'", str(d), w)

    def test_LST_24_fr_s_02_open_at_the_check_with_contention_now(self):
        e, g = T["LST-24"]["expect"], T["LST-24"]["given"]
        d = M.pillar_view(NOW, "compute", g["object"], "capacity", g["window"])
        c = d["capacity"]
        self.assertEqual(c["check"]["state"], e["check_state"])
        self.assertEqual(c["contention_now"]["value"], e["contention_value"])
        self.assertEqual(c["kpis"][1]["now"], e["contention_value"])
        self.assertEqual(d["status"], e["status"])

    def test_LST_25_a_host_shows_its_cluster(self):
        e, g = T["LST-25"]["expect"], T["LST-25"]["given"]
        c = M.pillar_view(NOW, "compute", g["object"], "capacity", g["window"])["capacity"]
        self.assertEqual((c["cluster"], c["marked_host"]), (e["cluster"], e["marked_host"]))
        self.assertEqual([h["host"] for h in c["hosts"] if h["marked"]], [e["marked_host"]])

    def test_LST_26_the_estate_matches_vsphere_worlds_definitions(self):
        d = M.pillar_view(NOW, "compute", "estate", "capacity", "24h", cls="all")["capacity"]
        cs = CAP._cons_series((), NOW.isoformat(), "24h")
        ids = [r["cluster"] for r in d["clusters_at"]]
        for i in (0, 100, 287):
            vals = [cs[c][i] for c in ids]
            p = d["spread"]["points"][i]
            self.assertEqual((p["highest"], p["percentile"]), (max(vals), P.nearest_rank(vals, 90)))
        ck = CAP.checks(NOW)
        self.assertEqual(d["closed"]["closed_since_previous"], [c for c in ids if ck[c][0]["state"] == "closed" and ck[c][1]["state"] == "open"])


class SpecRules(unittest.TestCase):
    def test_LPG_1_every_page_and_section_names_question_role_cadence(self):
        for f in (ROOT / "spec/workspaces/l2").glob("*.md"):
            text = f.read_text()
            self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(text.split("---")[1])), f.name)
            for b in re.findall(r"```yaml\n(.*?)```", text, re.S):
                self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(b)), f.name)

    def test_reads_name_catalog_entries(self):
        from build.pcm_proto import docs
        self.assertEqual(docs.dangling_reads(), [])


if __name__ == "__main__":
    unittest.main()


class KpiFirst(Base):
    """D-100: the KPI first on the Performance tab; VCF Operations' remaining figures first on the Capacity tab."""

    def test_LST_29_cluster_and_host_open_with_their_kpi(self):
        t = T["LST-29"]; g, e = t["given"], t["expect"]
        c = M.pillar_view(NOW, "compute", g["cluster"], "performance", g["window"])
        self.assertEqual([k["label"] for k in c["kpis"]], e["cluster_kpis"])
        cp = c["kpis"][0]
        self.assertEqual({"now": cp["now"], "worst": cp["worst"]["v"], "percentile_95": cp["percentile_95"]}, e["cluster_performance"])
        cap = {k["key"]: k for k in M.pillar_view(NOW, "compute", g["cluster"], "capacity", g["window"])["capacity"]["kpis"]}["performance"]
        self.assertEqual(cp["points"] == cap["points"] and cp["percentile_95"] == cap["percentile_95"], e["cluster_performance_same_as_capacity_tab"])
        h = M.pillar_view(NOW, "compute", g["host"], "performance", g["window"])
        self.assertEqual([k["label"] for k in h["kpis"]], e["host_kpis"])
        for k in c["kpis"] + h["kpis"]:
            self.assertEqual(len(k["points"]), e["points_24h"])
            self.assertTrue(set(e["figures"]) <= set(k) and "average" not in k)
            self.assertTrue(all(0 <= p["v"] <= 100 for p in k["points"] if p["v"] is not None))
        for k in c["kpis"] + h["kpis"]:
            self.assertEqual(len(k["details"]), e["kpi_details"][k["key"] if k in c["kpis"] else "host"])
            for part in k["details"]:
                self.assertEqual(len(part["points"]), e["points_24h"])
                self.assertTrue(set(e["kpi_details_figures"]) <= set(part) and "average" not in part)
                self.assertEqual(part["now"], part["points"][-1]["v"])
        self.assertTrue(all(p.get("band_ends") for k in c["kpis"] + h["kpis"] for p in k["details"]))
        self.assertEqual(len(c["content"]["iceberg"]["points_7_days"]), e["iceberg_points"])
        self.assertEqual("kpis" in M.pillar_view(NOW, "compute", g["vm"], "performance", g["window"]), e["vm_has_kpis"])

    def test_LST_30_remaining_from_vcf_operations_on_one_object_only(self):
        t = T["LST-30"]; g, e = t["given"], t["expect"]
        for kind in ("vm", "host", "cluster"):
            r = M.pillar_view(NOW, "compute", g[kind], "capacity", g["window"])["capacity"]["remaining"]
            self.assertEqual([x["key"] for x in r["values"]], e[kind], kind)
            self.assertEqual((r["source"], r["placeholder"]), (e["source"], e["placeholder"]))
            again = M.pillar_view(NOW, "compute", g[kind], "capacity", "7d")["capacity"]["remaining"]
            self.assertEqual(again == r, e["stable"])
        grp = M.pillar_view(NOW, "compute", g["group"], "capacity", g["window"])["capacity"]
        self.assertNotIn("remaining", grp)

