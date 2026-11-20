"""Catalog and story tests for the Docs workspace.

GENERATED. Do not edit by hand (D-070). Expected values come from spec/tests/docs.yaml.
Run from the repository root:  python3 -m unittest build.tests.test_docs -v
"""
from __future__ import annotations

import os
os.environ["PCM_DB"] = ":memory:"  # tests never touch the working database
import re
import tempfile
import unittest
from pathlib import Path

import yaml

from build.pcm_proto import docs, generator, l2, noc

ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((ROOT / "spec/tests/docs.yaml").read_text())
NOW = generator.parse_now(SPEC["now"])
T = {t["id"]: t for level in ("catalog", "story") for t in SPEC[level]}
CAT = ROOT / "spec/catalog"


class Base(unittest.TestCase):
    def setUp(self):
        noc.STATE.reset()
        l2.STATE.reset()


class Catalog(Base):
    def test_DCAT_1_every_object_has_a_page(self):
        c = docs.index()["counts"]
        self.assertEqual(list(c), T["DCAT-1"]["expect"]["kinds"])
        y = lambda p: yaml.safe_load((CAT / p).read_text())
        self.assertEqual(c["measure"], sum(len(y(f"{f}.yaml")["entries"]) for f in docs.MEASURE_FILES))
        self.assertEqual(c["sop"], len(list((CAT / "sops").glob("*.yaml"))))
        self.assertEqual(c["policy"], len(y("policies/actions.yaml")["policies"]))
        self.assertEqual(c["threshold"], len(y("thresholds.yaml")["thresholds"]))
        self.assertEqual(c["standard"], len(y("standards.yaml")["standards"]))
        self.assertEqual(c["setting"], len(y("settings.yaml")["settings"]))

    def test_DCAT_2_no_dangling_reads(self):
        self.assertEqual(docs.dangling_reads(), T["DCAT-2"]["expect"]["dangling_reads"])

    def test_DCAT_4_one_definition_per_id(self):
        seen, twice = {}, []
        for f in docs.MEASURE_FILES:
            for k in yaml.safe_load((CAT / f"{f}.yaml").read_text())["entries"]:
                if k in seen:
                    twice.append(f"{k} in {seen[k]} and {f}")
                seen[k] = f
        self.assertEqual(twice, T["DCAT-4"]["expect"]["ids_defined_twice"])

    def test_DCAT_3_no_value_only_in_code(self):
        src = (ROOT / "build/pcm_proto/l2.py").read_text()
        self.assertNotRegex(src, r'"value":\s*50')
        self.assertNotIn("ntp.acme.internal", src)
        std = generator.load_spec()["standards"]
        for item in [i for g in l2.configuration(NOW)["groups"].values() for i in g]:
            self.assertEqual(item["standard"], std[item["setting"]]["value"])
        self.assertEqual(l2.THRESHOLDS["th-cluster-perf-red"]["value"], generator.load_spec()["thresholds"]["th-cluster-perf-red"]["value"])


class Story(Base):
    def test_DST_1_threshold_used_on_and_history(self):
        e = T["DST-1"]["expect"]
        d = docs.detail("threshold", "th-cluster-perf-red")
        self.assertIn(e["used_on_includes"], [u["page"] for u in d["used_on"]])
        self.assertEqual(d["history"], [])
        l2.act(NOW, ["thresholds", "th-cluster-perf-red", "publish"], {"value": 60, "reason": "Replayed before publishing"})
        d, x = docs.detail("threshold", "th-cluster-perf-red"), e["after_l2_publishes_60"]
        self.assertEqual((d["version"], d["body"]["value"]), (x["version"], x["value"]))
        h = d["history"][0]
        self.assertEqual((h["before"], h["after"], h["actor_human"]), (x["history_before"], x["history_after"], x["by"]))

    def test_DST_2_policy_version(self):
        e = T["DST-2"]["expect"]
        prop = generator.load_spec()["stories"]["stories"]["L-4"]["plant"]["proposed_policy"]
        t = "move_vms_between_clusters"
        l2.act(NOW, ["policies", t, "replay"], prop)
        l2.act(NOW, ["policies", t, "publish"], {**prop, "reason": "Guardrails replace approval"})
        d = docs.detail("policy", t)
        self.assertEqual((d["version"], d["body"]["tier"]), (e["version"], e["tier"]))
        self.assertEqual([h["action"] for h in d["history"]], e["history_actions"])

    def test_DST_3_proposals_visible(self):
        for oid, status in T["DST-3"]["expect"].items():
            self.assertEqual(docs.detail("setting", oid)["status"], status, oid)

    def test_DST_4_export(self):
        e = T["DST-4"]["expect"]
        with tempfile.TemporaryDirectory() as tmp:
            files = docs.export(Path(tmp), NOW)
            self.assertEqual(len([f for f in files if f.startswith("content/runbooks/")]), e["runbooks"])
            heads = {"runbook": e["runbook_headings"], "operations-plan": e["operations_plan_headings"], "bom": e["bom_headings"]}
            for f in files:
                text = (Path(tmp) / f).read_text()
                fm = yaml.safe_load(text.split("---")[1])
                self.assertEqual(list(fm), e["front_matter_fields"], f)
                self.assertEqual((fm["access_scope"], fm["origin"]), (e["access_scope"], e["origin"]), f)
                self.assertEqual(fm["domain"], f.split("/")[1], f)
                self.assertEqual(re.findall(r"^## (.+)$", text, re.M), heads[fm["doc_type"]], f)
                self.assertNotRegex(text, r"\bD-\d{3}\b", f)

    def test_detail_has_no_decision_ids(self):
        for o in docs.objects():
            self.assertNotRegex(str(o), r"\bD-\d{3}\b", o["id"])


class SpecRules(unittest.TestCase):
    def test_DPG_1_every_page_and_section_names_question_role_cadence(self):
        for f in (ROOT / "spec/workspaces/docs").glob("*.md"):
            text = f.read_text()
            self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(text.split("---")[1])), f.name)
            for b in re.findall(r"```yaml\n(.*?)```", text, re.S):
                self.assertTrue({"question", "role", "cadence"} <= set(yaml.safe_load(b)), f.name)


if __name__ == "__main__":
    unittest.main()
