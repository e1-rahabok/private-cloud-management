"""Catalog and PCM scenario story tests for the Capacity workspace.

GENERATED. Do not edit by hand (D-070). Expected values come from pcm/capacity/spec/acceptance-tests.yaml (D-071).
Run from the repository root:  python3 -m unittest pcm.capacity.tests.test_capacity -v
"""
from __future__ import annotations

import re
import unittest
from datetime import timedelta
from pathlib import Path

import os
os.environ["PCM_DB"] = ":memory:"  # tests never touch the working database

import yaml

from pcm.core import generator
from pcm.capacity import capacity
from pcm.executive import api

HERE = Path(__file__).resolve().parents[1]  # the workspace folder
SPEC = yaml.safe_load((HERE / "spec/acceptance-tests.yaml").read_text())
NOW = generator.parse_now(SPEC["now"])
SETTINGS = generator.load_spec()["settings"]
T = {t["id"]: t for level in ("catalog", "scenario_story") for t in SPEC[level]}


def grp(view, gid):
    return next(g for g in view["groups"] if g["id"] == gid)


class Base(unittest.TestCase):
    def setUp(self):
        capacity.STATE.reset()


class Catalog(Base):
    def _six(self, tid):
        g = T[tid]["given"]
        return capacity.planning_six_numbers(g["class"], g["cores"], g["base_ghz"], g["memory_gb"], SETTINGS), T[tid]["expect"]

    def test_KCAT_1_silver_six_numbers(self):
        r, e = self._six("KCAT-1")
        for k in ("cpu_allocation", "cpu_reservation", "cpu_utilization", "mem_allocation", "mem_reservation", "mem_utilization"):
            self.assertAlmostEqual(r["numbers"][k], e[k], places=1, msg=k)
        self.assertEqual(r["binds"], e["binds"])
        self.assertEqual(r["matching_dram_gb"], e["matching_dram_gb"])

    def test_KCAT_2_gold_dram(self):
        r, e = self._six("KCAT-2")
        self.assertEqual(r["matching_dram_gb"], e["matching_dram_gb"])

    def test_KCAT_3_bronze_dram(self):
        r, e = self._six("KCAT-3")
        self.assertEqual(r["matching_dram_gb"], e["matching_dram_gb"])

    def test_KCAT_4_usable(self):
        g = T["KCAT-4"]["given"]
        u = capacity.usable(g["hosts"], g["clusters"], {"threads": g["threads_per_host"], "memory_gb": 768}, 100,
                            {"compute": g["buffer_percent"], "memory": 0, "storage": 10})
        self.assertAlmostEqual(u["compute"]["usable"], T["KCAT-4"]["expect"]["compute_usable"])

    def test_KCAT_5_close_week_left_out_of_trend(self):
        weekly = [{"t": "", "v": 100 + 2 * i, "close": False} for i in range(30)]
        spiked = [dict(p) for p in weekly]
        spiked[20].update(v=500, close=True)
        self.assertAlmostEqual(capacity.trend(weekly, 26)[1], capacity.trend(spiked, 26)[1], places=6)


class ScenarioStory(Base):
    def test_KST_1_sg_silver_in_round(self):
        e = T["KST-1"]["expect"]
        g = grp(capacity.groups_view(NOW), e["group"])
        self.assertEqual((g["decision_days"], g["in_plan"], g["round_on_time"]), (e["decision_days"], e["in_plan"], e["round_on_time"]))

    def test_KST_2_tk_gold_waste(self):
        e = T["KST-2"]["expect"]
        self.assertEqual(grp(capacity.groups_view(NOW), e["group"])["quadrant"], e["quadrant"])

    def test_KST_3_peak_warning_not_purchase(self):
        e = T["KST-3"]["expect"]
        d = capacity.group_detail(NOW, e["group"])
        r = d["resources"][d["peak_warning"]["resource"]]
        self.assertEqual(generator.parse_now(r["peak_cross_date"]).month, e["peak_warning_month"])
        self.assertIsNone(r["run_out_90d_days"])
        self.assertGreater(d["decision_days"], d["peak_warning"]["days"])
        self.assertFalse(d["in_plan"])

    def test_KST_4_migration_moves_fr_silver(self):
        e = T["KST-4"]["expect"]
        d = capacity.group_detail(NOW, e["group"])
        self.assertLessEqual(d["resources"][d["tightest"]]["run_out_days"], e["run_out_days_at_most"])
        self.assertEqual(d["in_plan"], e["in_plan"])
        self.assertEqual(d["register"][0]["owner"], "migration-team")
        moved = next(m for m in capacity.week(NOW)["moved"] if m["group"] == e["group"])
        self.assertEqual(moved["because_of"], [e["week_moved_earlier_because_of"]])
        self.assertGreater(moved["days_earlier"], 0)

    def test_KST_5_refresh_covers_growth(self):
        g, e = T["KST-5"]["given"], T["KST-5"]["expect"]
        r = capacity.what_if_refresh(capacity.build(NOW), g["location"], g["replace"], g["new"])
        self.assertEqual(r["covers_next_year_growth"], e["covers_next_year_growth"])
        self.assertEqual((r["before"]["cores_licensed"], r["after"]["cores_licensed"]), (e["licensed_cores_before"], e["licensed_cores_after"]))
        self.assertFalse(capacity.what_if_refresh(capacity.build(NOW), "ld", 90, 60)["covers_next_year_growth"])

    def test_KST_6_reclamation_defers_round(self):
        e = T["KST-6"]["expect"]
        w = capacity.waste_view(NOW)
        r = next(x for x in w["reclamation"] if x["group"] == e["group"])
        self.assertEqual(r["defers_next_round"], e["defers_next_round"])
        plan = next(p for p in capacity.plan_view(NOW)["rows"] if p["group"] == e["group"])
        self.assertEqual(r["cost_avoidable"], plan["total"])
        self.assertEqual(next(a for a in r["areas"] if a["area"] == "Powered-off VMs")["memory_gb"], e["powered_off_frees_memory_gb"])

    def test_KST_7_the_check_overrides_the_forecast(self):
        """Closed for new VMs is read from the check (l2.cluster_check), one definition with L2 (D-094)."""
        e = T["KST-7"]["expect"]
        groups = capacity.groups_view(NOW)
        for gid, x in e.items():
            g = grp(groups, gid)
            self.assertEqual([c["cluster"] for c in g["closed_for_new_vms"]], x["closed_for_new_vms"], gid)
            self.assertNotIn("full_now", g)
        self.assertEqual([c["cluster"] for c in capacity.group_detail(NOW, "LD-Bronze")["closed_for_new_vms"]], e["LD-Bronze"]["closed_for_new_vms"])

    def test_KST_8_one_definition_with_cio_page(self):
        ds = generator.generate(NOW)
        view = capacity.groups_view(NOW)
        for lid, loc in ds["locations"].items():
            earliest = min(g["decision_days"] for g in view["groups"] if g["location"] == lid and g["decision_days"] is not None)
            self.assertEqual((loc["decision"]["date"] - NOW).days, earliest, lid)

    def test_register_add_moves_forecast(self):
        before = grp(capacity.groups_view(NOW), "VA-Silver")["decision_days"]
        code, out = capacity.add_demand(NOW, {"kind": "project", "group": "VA-Silver", "date": (NOW + timedelta(days=60)).date().isoformat(),
                                              "owner": "apps-team", "memory_gb": 20000}, ())
        self.assertEqual(code, 200)
        self.assertLess(out["group"]["decision_days"], before)
        self.assertEqual(capacity.add_demand(NOW, {"kind": "project"}, ())[0], 400)

    def test_plan_is_cost_not_price(self):
        p = capacity.plan_view(NOW)
        self.assertEqual(p["total"], sum(r["total"] for r in p["rows"]))
        self.assertEqual(api.value_detail(generator.generate(NOW), "cost")["cost"]["cost_avoidable_next_round"]["value"],
                         sum(r["cost_avoidable"] for r in capacity.waste_view(NOW)["reclamation"]))


class SpecRules(unittest.TestCase):
    def test_KPG_1_every_page_and_section_names_question_role_cadence(self):
        for f in (HERE / "spec/pages").glob("*.md"):
            text = f.read_text()
            self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(text.split("---")[1])), f.name)
            for b in re.findall(r"```yaml\n(.*?)```", text, re.S):
                self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(b)), f.name)


if __name__ == "__main__":
    unittest.main()
