"""Catalog and story tests for the L2 workspace: Monitor, Troubleshoot, Improve (D-083 to D-090).

GENERATED. Do not edit by hand (D-070). Expected values come from spec/tests/l2.yaml (D-071).
Run from the repository root:  python3 -m unittest build.tests.test_l2 -v
"""
from __future__ import annotations

import os
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

os.environ["PCM_DB"] = ":memory:"  # tests never touch the working database

import yaml

from build.pcm_proto import generator, l2, l2_cases as C, l2_estate as X, l2_improve as I, l2_monitor as M, l2_performance as P, noc

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
        day = {f["object"] for f in M.findings_under(NOW, "estate", (), None, "24h")}
        self.assertFalse(day & {f["object"] for f in week})

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
        st = dict(SETTINGS, **{"agent_e2.service_url": "http://127.0.0.1:9"})
        with mock.patch.object(generator, "load_spec", lambda: {**REAL_SPEC, "settings": st}):
            code, out = C.act(NOW, ["case-sg-app-117", "ask"], {"question": "Why?"})
        self.assertEqual((code, out["source"]), (200, "unavailable"))

    def test_ask_passes_case_facts_and_role(self):
        seen = {}
        def fake(url, body, timeout):
            seen.update(body)
            return {"type": "answer", "content": "Inside the Guest OS.", "files_read": ["sp5-framework/performance/vm-slow"], "model": "m"}
        with mock.patch("build.pcm_proto.agent_e2._post_raw", fake):
            code, out = C.act(NOW, ["case-sg-app-117", "ask"], {"question": "Is the platform the cause?"})
        self.assertEqual((out["source"], seen["role"]), ("service", "l2"))
        self.assertIn("inside the Guest OS", seen["facts"]["hand_over"])


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
            server.l2_get(["monitor", "compute", "estate", "capacity"], NOW, (), q(**{"class": "gold"}))
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
