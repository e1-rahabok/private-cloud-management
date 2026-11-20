"""Catalog and story tests for the Executive workspace.

GENERATED. Do not edit by hand (D-070). Expected values are read from spec/tests/executive.yaml,
never copied into this file (D-071).

Run from the repository root:  python3 -m unittest build/tests/test_executive.py -v
"""
from __future__ import annotations

import re
import unittest
from datetime import timedelta
from pathlib import Path

import os
os.environ["PCM_DB"] = ":memory:"  # tests never touch the working database

import yaml

from build.pcm_proto import api, catalog, generator

ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((ROOT / "spec/tests/executive.yaml").read_text())
NOW = generator.parse_now(SPEC["now"])
SETTINGS = generator.load_spec()["settings"]


def rel_days(expr: str) -> int:
    return (generator.rel(expr, NOW).date() - NOW.date()).days


def resolve(obj, path: str):
    """Resolve 'a.b[key=val].c' against nested dicts and lists."""
    for part in re.findall(r"[^.\[\]]+(?:\[[^\]]+\])?", path):
        m = re.fullmatch(r"([^\[]+)(?:\[(\w+)=([^\]]+)\])?", part)
        obj = obj[m.group(1)]
        if m.group(2):
            def key_of(x, k=m.group(2)):
                v = x.get(k)
                return v.get("value") if isinstance(v, dict) else v
            obj = next(x for x in obj if str(key_of(x)) == m.group(3))
    return obj


class Catalog(unittest.TestCase):
    pass


def make_catalog_test(t):
    def test(self):
        g, e = t["given"], t["expect"]
        entry = t["entry"]
        if entry == "capacity.decision_date":
            got = catalog.decision_date(generator.rel(g["run_out_date"], NOW), g["procurement_lead_time_days"])
            self.assertEqual((got.date() - NOW.date()).days, rel_days(e))
        elif entry == "capacity.location_decision":
            ds = {k: generator.rel(v, NOW) for k, v in g["decision_dates"].items()}
            got = catalog.location_decision(ds, set(g["next_round_groups"]), NOW, SETTINGS)
            for k, v in e.items():
                if k == "date":
                    self.assertEqual(got["days"], rel_days(v))
                else:
                    self.assertEqual(got[k], v, k)
        elif entry == "safe.ksi_percent":
            self.assertEqual(catalog.ksi_status(g["vm_unsecured_minutes"], g["days_in_month"], SETTINGS), e["status"])
        elif entry == "up.sla_allowance_minutes":
            self.assertEqual(catalog.sla_allowance_minutes(SETTINGS["up.sla_percent"][g["class"]], g["days_in_month"]), e)
        elif entry == "up.vm_counted_downtime_minutes":
            self.assertEqual(catalog.counted_downtime_minutes(g["downtime_minutes"], g["inside_approved_window_minutes"]), e)
        elif entry == "safe.vm_secured_time_percent":
            got = catalog.vm_secured_time_percent(g["minutes_in_month_so_far"], g["unsecured_minutes"],
                                                  g["unsecured_inside_maintenance_window"])
            self.assertEqual(got, e)
        elif entry == "fast.production_kpi":
            got = catalog.fast_status(g["class_group_kpi"])
            for k, v in e.items():
                self.assertEqual(got[k], v, k)
        elif entry == "recovery.site_recovery":
            got = catalog.site_recovery(g["last_test_days_ago"], g["recovery_minutes"], g["target_minutes"],
                                        g["protected_vms"], g["vms_in_test"], SETTINGS)
            for k, v in e.items():
                self.assertEqual(got[k], v, k)
        elif entry == "value.public_cloud_comparison":
            got = catalog.public_cloud_comparison(g["cost_annual"], g["depreciation_years"], g["public_cloud_estimate"])
            for k, v in e.items():
                self.assertEqual(got[k], v, k)
        elif entry == "goals.status":
            self.assertEqual(catalog.goal_status(g["target"], g["direction"], g["projected_year_end"]), e)
        elif entry == "up.availability_percent":
            self.assertEqual(catalog.kai_status(g["vm_counted_minutes"], g["classes"], g["days_in_month"], SETTINGS), e["status"])
        elif entry == "scale.compute_cores":
            est = generator.load_spec()["estate"]
            self.assertEqual(catalog.compute_cores(est["locations"], est["host_generations"]), e)
        else:
            self.fail(f"No adapter for catalog entry {entry}")
    return test


for _t in SPEC["catalog"]:
    setattr(Catalog, f"test_{_t['id'].replace('-', '_')}", make_catalog_test(_t))


class Story(unittest.TestCase):
    pass


def call(ds, path):
    parts = [p for p in path.split("/") if p][2:]
    if parts == ["summary"]:
        return api.summary(ds)
    if parts[0] == "value":
        return api.value_detail(ds, parts[1])
    if parts[0] == "capacity":
        return api.capacity_detail(ds)
    if parts[0] == "locations":
        return api.location_detail(ds, parts[1])
    raise ValueError(path)


def make_story_test(t):
    def test(self):
        ds = generator.generate(NOW, seed=SPEC["seed"], enable=tuple(t.get("enable", [])))
        exp = dict(t["expect"])
        if "rule" in exp and t["id"] == "ST-9":
            h = api.summary(ds)["health"]["up"]
            self.assertLess(h["actual_percent"]["value"], h["headline"]["value"])
            self.assertLess(h["headline"]["value"], 100.0)
            ev = api.health_detail(ds, "up")["events"]
            self.assertTrue(any(not e["counted"] and e["change_ref"] == "CHG0041042" for e in ev))
            return
        if "rule" in exp and t["id"] == "ST-8":  # estate KSI above contract, card red
            h = api.summary(ds)["health"]["safe"]["headline"]
            self.assertGreaterEqual(h["value"], SETTINGS["safe.sla_contract_percent"])
            self.assertLess(h["value"], 100.0)
            self.assertEqual(h["status"], "red")
            return
        if "rule" in exp:  # ST-7: same number in every place
            a = api.summary(ds)["scale"]["locations"]
            a = next(x for x in a if x["id"] == "sg")["decision"]
            b = api.location_detail(ds, "sg")["location"]["decision"]
            c = next(x for x in api.capacity_detail(ds)["locations"] if x["location"] == "sg")
            self.assertEqual(a, b)
            self.assertEqual(a, c)
            return
        path = exp.pop("api")
        if "rule_cost_avoidable" in exp:  # ST-4: one definition with the capacity purchase plan
            exp.pop("rule_cost_avoidable")
            plan = next(x for x in ds["capacity"]["plan"] if x["group"] == "SG-Silver")
            self.assertEqual(api.value_detail(ds, "value/cost".split("/")[1])["cost"]["cost_avoidable_next_round"]["value"], plan["total"])
        resp = call(ds, path)
        summary = api.summary(ds)
        for k, v in exp.items():
            target = summary if k.startswith("summary.") else resp
            key = k[len("summary."):] if k.startswith("summary.") else k
            self.assertEqual(resolve(target, key), v, k)
    return test


for _t in SPEC["story"]:
    setattr(Story, f"test_{_t['id'].replace('-', '_')}", make_story_test(_t))


class SpecRules(unittest.TestCase):
    def test_PG_1_every_section_names_question_role_cadence(self):
        text = (ROOT / "spec/workspaces/executive/page.md").read_text()
        blocks = re.findall(r"```yaml\n(.*?)```", text, re.S)
        sections = re.findall(r"^### \d+\. ", text, re.M)
        self.assertEqual(len(blocks), len(sections))
        for b in blocks:
            self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(b)))

    def test_same_inputs_same_data(self):
        a = api.summary(generator.generate(NOW, seed=SPEC["seed"]))
        b = api.summary(generator.generate(NOW, seed=SPEC["seed"]))
        self.assertEqual(a, b)

    def test_stories_hold_on_another_day(self):
        """D-067: stories are relative to now, so they hold at any 'now'."""
        other = NOW + timedelta(days=137, hours=5)
        s = api.summary(generator.generate(other, seed=SPEC["seed"]))
        self.assertEqual(s["room_to_grow"]["estate_decision"]["date"]["days_from_now"], 30)
        self.assertEqual(s["health"]["safe"]["headline"]["status"], "red")


if __name__ == "__main__":
    unittest.main()
