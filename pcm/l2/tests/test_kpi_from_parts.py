"""PCM scenario story M-5: SG-S-01, sg-esx-110 and sg-api-1617. Each KPI is the vCommunity scoring of its parts, point by point."""
import os
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault("PCM_DB", ":memory:")
from pcm.l2 import inventory_tree as X, monitor as M, kpi_from_parts as S  # noqa: E402
from pcm.noc import noc  # noqa: E402

NOW = datetime(2026, 10, 19, 10, 0, tzinfo=ZoneInfo("Asia/Singapore"))
E = X.estate(())


def rebuilt(rows, parts, i, flip=False):
    k = S.kpi(rows, {p["key"]: p["points"][i]["v"] for p in parts})
    return round(100 - k, 1) if flip else round(k, 1)


class KpiFromPartsTest(unittest.TestCase):
    def test_cluster_shape(self):
        perf, risk = M.object_kpis(E, E.nodes["SG-S-01"], NOW, "24h")
        self.assertTrue(88 <= perf["points"][0]["v"] <= 93)
        self.assertTrue(38 <= perf["worst"]["v"] <= 46)
        self.assertTrue(50 <= perf["now"] <= 60)
        self.assertLess(risk["points"][0]["v"], 25)           # green
        self.assertTrue(50 <= risk["now"] < 75)                # orange

    def test_every_point_is_its_parts(self):
        for nid, rows, flip in (("SG-S-01", S.PERF_ROWS, False), ("sg-esx-110", S.HOST_ROWS, False)):
            kpi = M.object_kpis(E, E.nodes[nid], NOW, "24h")[0]
            self.assertEqual(len(kpi["details"]), 9)
            for i in range(0, 288, 7):
                self.assertAlmostEqual(kpi["points"][i]["v"], rebuilt(rows, kpi["details"], i), delta=0.25, msg=f"{nid} point {i}")
        risk = M.object_kpis(E, E.nodes["SG-S-01"], NOW, "24h")[1]
        self.assertEqual(len(risk["details"]), 10)  # the catalog's 12 less the two memory tiering ones: no tiered host (D-113)
        for i in range(0, 288, 7):
            self.assertAlmostEqual(risk["points"][i]["v"], rebuilt(S.RISK_ROWS, risk["details"], i, True), delta=0.25)

    def test_vm_is_its_rows(self):
        own = M.perf_score(E, E.nodes["sg-api-1617"], NOW, "24h")
        layers = M.vm_layers(E.nodes["sg-api-1617"], NOW, "24h", X.active_scenario_stories(()), own)
        vm = {m["key"]: m for m in layers[1]["metrics"]}
        self.assertEqual(len(vm), 10)                           # nine rows and the score
        self.assertEqual(len(layers[1]["metrics"]), 10)         # and no metric shows twice
        base = {k: lab for k, lab, *_x in M.LAYER_METRICS[1][2]}
        self.assertEqual({k: m["label"] for k, m in vm.items()}, base)  # under the catalog's names
        names = {"cpu_ready_percent": "cpu_ready", "co_stop_percent": "co_stop", "memory_wait_percent": "memory_wait", "disk_latency_ms": "disk_latency"}
        names.update({k: r for k, *_x, r in S.VM_EXTRA_ROWS})
        for i in range(0, 288, 7):
            rows = {r: vm[k]["points"][i]["v"] for k, r in names.items()}
            self.assertAlmostEqual(vm["vm_performance"]["points"][i]["v"], round(S.kpi(S.VMROWS, rows), 1), delta=0.35)
        self.assertEqual(layers[0]["status"], "green")          # the Guest OS is fine: the wait is the platform's
        self.assertEqual(layers[1]["status"], "red")

    def test_one_definition(self):
        # the node scores, the NOC and the tab read the same series
        v = noc.cluster_score({"id": "SG-S-01", "base": 90}, NOW, None, NOW, 7)
        self.assertAlmostEqual(v, M.object_kpis(E, E.nodes["SG-S-01"], NOW, "24h")[0]["now"], delta=0.1)
        self.assertLess(M.perf_score(E, E.nodes["sg-api-1617"], NOW, "24h"), 40)

    def test_longer_windows_are_calm_before_the_scenario_story(self):
        k = M.object_kpis(E, E.nodes["SG-S-01"], NOW, "7d")[0]
        self.assertGreater(k["points"][0]["v"], 85)
        self.assertAlmostEqual(k["worst"]["v"], 41.9, delta=1.5)


if __name__ == "__main__":
    unittest.main()
