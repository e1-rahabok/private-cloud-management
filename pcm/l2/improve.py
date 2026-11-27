"""L2 Improve: risk and efficiency, not broken things (pcm/l2/design-note.md, section 6).

GENERATED from pcm/l2/spec/pages/improve.md, pcm/l2/spec/catalog.yaml and pcm/core/spec/demo-data/scenario-stories.yaml.
Do not edit by hand (D-070). Framed in capacity, never in money (D-027).
"""
from __future__ import annotations

from datetime import datetime

from ..capacity import capacity
from . import l2, inventory_tree as X, monitor as M

PILLARS = M.PILLARS


def opportunities(now: datetime, enable=()) -> list:
    """l2.opportunities: every risk and opportunity in the estate, with its object and size."""
    act = X.active_scenario_stories(enable)
    out = []
    c6 = act.get("C-6")
    if c6:
        p = c6["plant"]
        waste = {g["id"]: g for g in capacity.week(now, enable)["waste"]}
        g = waste.get(c6["objects"]["cluster_group"], {})
        n = p["powered_off_vms"] + p["idle_vms"] + p["oversized_large_vms"]
        out.append({"id": "o-sg-silver-reclaim", "pillar": "capacity", "object": "class-silver/sg", "object_name": "SG-Silver",
                    "what": f"Reclaim {p['powered_off_vms']} powered-off, {p['idle_vms']} idle and {p['oversized_large_vms']} large oversized VMs",
                    "why": "It moves the memory decision past the next purchase round (Capacity workspace).",
                    "size": f"{n:,} VMs", "size_n": n, "detail": g.get("note")})
    l4 = act.get("L-4")
    if l4:
        prop = l2.proposals(enable)[0]
        out.append({"id": "o-sg-s-04-rebalance", "pillar": "capacity", "object": l4["plant"]["proposal"]["from"],
                    "object_name": l4["plant"]["proposal"]["from"],
                    "what": prop["reason"], "why": "Cluster Performance fell to 68 at the end-of-day batch peak; a neighbour has room in the same class.",
                    "size": f"{l4['plant']['proposal']['vms']} VMs", "size_n": l4["plant"]["proposal"]["vms"], "proposal": prop})
    l8 = act.get("L-8")
    if l8:
        n = l8["plant"]["nightly_used_percent"]
        out.append({"id": "o-sg-ds-11-snapshot", "pillar": "capacity", "object": l8["objects"]["datastore"], "object_name": l8["objects"]["datastore"],
                    "what": f"Remove the snapshot the backup left on {l8['objects']['vm']}", "why": f"Used space {n[0]}% to {n[-1]}% in 7 nights.",
                    "size": f"{round(n[-1] - n[0], 1)}% of the datastore", "size_n": n[-1] - n[0]})
    m1 = act.get("M-1")
    if m1:
        o = m1["plant"]["opportunity"]
        out.append({"id": "o-ld-numa-rule", "pillar": o["pillar"], "object": m1["objects"]["location"], "object_name": "London",
                    "what": o["text"], "why": "VMs wider than a Gen-2019 NUMA node lose local memory after a move.",
                    "size": o["size"], "size_n": len(m1["objects"]["affected_vms"])})
    t1 = act.get("T-1")
    if t1:
        out.append({"id": "o-sg-gl-db-01-numa", "pillar": "performance", "object": t1["objects"]["vm"], "object_name": t1["objects"]["vm"],
                    "what": f"Keep {t1['objects']['vm']} (24 vCPUs) on Gen-2024 hosts, or size it to 20 vCPUs or fewer",
                    "why": "It spans two NUMA nodes on Gen-2019 hosts.", "size": "1 VM", "size_n": 1})
    out.append({"id": "o-tk-restore-test", "pillar": "availability", "object": "tk", "object_name": "Tokyo",
                "what": "Run the monthly restore test", "why": "SP5 monthly: a backup is proven only by a restore. Last run 35 days ago.",
                "size": "1 test", "size_n": 1})
    out.append({"id": "o-ld-ds-07-orphans", "pillar": "inventory", "object": "LD-DS-07", "object_name": "LD-DS-07",
                "what": "Remove 18 orphaned virtual disk files", "why": "No VM uses them; the space is lost to every VM.",
                "size": "18 files", "size_n": 18})
    for g, items in l2.configuration(now, enable)["groups"].items():
        for it in items:
            out.append({"id": "o-" + it["id"], "pillar": "configuration", "object": it["objects"][0], "object_name": it["object"],
                        "what": f"{it['setting_label']}: {it['actual']}", "why": f"Standard: {it['standard']} (v{it['standard_version']}).",
                        "size": f"{len(it['objects'])} object{'s' if len(it['objects']) != 1 else ''}", "size_n": len(it["objects"]),
                        "group": g, "config": it})
    return out


def view(now: datetime, view_name: str, nid: str, pillar: str, window: str, enable=()) -> dict | None:
    E = X.estate(tuple(enable))
    if X.node(E, nid) is None or (pillar != "summary" and pillar not in PILLARS):
        return None
    ops = [o for o in opportunities(now, enable) if nid == "estate" or o["object"] == nid or (X.node(E, o["object"]) and nid in M.ancestors(E, o["object"]))]
    findings = [f for f in M.findings(now, enable) if f["outcome"] == "improve" and (nid == "estate" or nid in f["under"] or f["object"] == nid)]
    out = {"object": M.node_out(E, view_name, nid), "window": window, "pillar": pillar,
           "pillars": [{"pillar": p, "opportunities": sum(1 for o in ops if o["pillar"] == p),
                        "risks": sum(1 for f in findings if f["pillar"] == p)} for p in PILLARS]}
    if pillar == "summary":
        out["opportunities"] = sorted(ops, key=lambda o: -o["size_n"])
        out["findings"] = findings
        if nid == "estate":
            out["decisions"] = l2.decisions(now, enable)
        return out
    out["opportunities"] = sorted([o for o in ops if o["pillar"] == pillar], key=lambda o: -o["size_n"])
    out["findings"] = [f for f in findings if f["pillar"] == pillar]
    if pillar == "configuration":
        groups = {g: [] for g in ("correct_it", "update_it", "simplify_it", "optimize_it")}
        for it in M.config_items_under(E, nid, now, enable):
            groups[it["group"]].append(it)
        out["configuration"] = groups
    return out
