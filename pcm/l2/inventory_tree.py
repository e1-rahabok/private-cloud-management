"""The L2 inventory tree: every region, location, VCF instance, workload domain, cluster, host, VM and datastore
of the synthetic ACME estate, in five views (l2.tree, D-087), with the scores Monitor reads (l2.node_score).

GENERATED from pcm/core/spec/demo-data/estate.yaml (l2_tree), pcm/core/spec/demo-data/scenario-stories.yaml and pcm/l2/spec/catalog.yaml.
Do not edit by hand (D-070).

The structure does not depend on "now", so it is built once per set of enabled PCM scenario stories and cached.
Scores depend on the window and on PCM scenario stories planted relative to "now".
"""
from __future__ import annotations

import math
import random
from datetime import datetime
from functools import lru_cache

from ..core import generator
from ..executive import catalog

CLASS_LETTER = {"gold": "G", "silver": "S", "bronze": "B", "mixed": "X", "management": "M", "edge": "E"}
CLUSTER_ORDER = ("management", "edge", "gold", "silver", "bronze", "mixed")
WORKLOADS = ("gold", "silver", "bronze", "mixed")
WINDOWS = ("1h", "24h", "7d", "30d", "1y")
VIEWS = ("compute", "storage", "network", "class", "management")
VIEW_NAMES = {"compute": "Compute", "storage": "Storage", "network": "Network", "class": "Class of service", "management": "Management"}
APPLIANCE_NAMES = {"vcenter-mgmt": "vCenter (management)", "vcenter-wld": "vCenter (workloads)", "nsx-manager-1": "NSX Manager 1",
                   "nsx-manager-2": "NSX Manager 2", "nsx-manager-3": "NSX Manager 3", "nsx-edge-1": "NSX Edge 1",
                   "nsx-edge-2": "NSX Edge 2", "sddc-manager": "SDDC Manager", "vcf-operations": "VCF Operations",
                   "vcf-automation": "VCF Automation"}


def _h(*parts) -> float:
    """A stable number in [0, 1) from its parts: cheap, deterministic noise."""
    x = 2166136261
    for p in "|".join(map(str, parts)).encode():
        x = ((x ^ p) * 16777619) & 0xFFFFFFFF
    return x / 4294967296.0


def active_scenario_stories(enable=()) -> dict:
    s = generator.load_spec()["scenario_stories"]["scenario_stories"]
    return {k: v for k, v in s.items() if v.get("enabled_by_default", True) or k in enable}


class Estate:
    """Nodes by id, children per view, and the indexes Monitor and cases read."""

    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.children: dict[str, dict[str, list]] = {v: {} for v in VIEWS}
        self.parent: dict[str, dict[str, str]] = {v: {} for v in VIEWS}

    def add(self, node: dict, parents: dict) -> dict:
        self.nodes[node["id"]] = node
        for view, p in parents.items():
            self.parent[view][node["id"]] = p
            self.children[view].setdefault(p, []).append(node["id"])
        return node

    def kids(self, view: str, nid: str) -> list:
        return [self.nodes[c] for c in self.children[view].get(nid, [])]

    def path(self, view: str, nid: str) -> list:
        out = []
        cur = nid
        while cur is not None:
            out.append(cur)
            cur = self.parent[view].get(cur)
        return list(reversed(out))

    def descendants(self, view: str, nid: str, kind: str) -> list:
        """Every descendant of one kind. Uses the indexes for the kinds that matter at scale."""
        n = self.nodes[nid]
        if n["kind"] == kind:
            return [n]
        stack, out = [nid], []
        while stack:
            cur = stack.pop()
            for c in self.children[view].get(cur, []):
                cn = self.nodes[c]
                if cn["kind"] == kind:
                    out.append(cn)
                else:
                    stack.append(c)
        return out


def _split(total: int, parts: int) -> list:
    base, extra = divmod(total, parts)
    return [base + (1 if i < extra else 0) for i in range(parts)]


@lru_cache(maxsize=8)
def estate(enable: tuple = (), seed: int = 7) -> Estate:
    spec = generator.load_spec()
    est, rules = spec["estate"], spec["estate"]["l2_tree"]
    gens, layout = est["host_generations"], est["cluster_layout"]["share_of_hosts"]
    per_host = est["vms"]["per_host_average"]
    builds = rules["esxi_builds"]
    act = active_scenario_stories(enable)
    E = Estate()
    E.add({"id": "estate", "kind": "estate", "name": "ACME estate"}, {})
    for v in VIEWS:
        E.parent[v]["estate"] = None
    for rid, r in est["regions"].items():
        E.add({"id": rid, "kind": "region", "name": r["name"], "vcf_operations": r["vcf_operations_instance"]}, {"compute": "estate"})
    for cls in WORKLOADS:
        E.add({"id": f"class-{cls}", "kind": "class_of_service", "name": cls.capitalize()}, {"class": "estate"})

    vm_pins = {k: v for k, v in rules["vm_pins"].items() if k != "note"}
    host_pins = {k: v for k, v in rules["host_pins"].items() if k != "note"}
    roles = rules["vm_roles"]
    tools = rules["tools_versions"]

    for lid, loc in est["locations"].items():
        rng = random.Random(f"{seed}-l2-{lid}")
        E.add({"id": lid, "kind": "location", "name": loc["name"], "region": loc["region"], "time_zone": loc["time_zone"]},
              {"compute": loc["region"], "storage": "estate", "network": "estate", "management": "estate"})
        vcf = rules["vcf_instance"].format(loc=lid)
        E.add({"id": vcf, "kind": "vcf_instance", "name": vcf, "location": lid}, {"compute": lid, "management": lid})
        wld_of = {}
        for key, w in rules["workload_domains"].items():
            wid = w["id"].format(loc=lid)
            E.add({"id": wid, "kind": "workload_domain", "name": wid, "location": lid, "purpose": key}, {"compute": vcf})
            for c in w["classes"]:
                wld_of[c] = wid
            dvs = f"{lid}-vds-{key}"
            E.add({"id": dvs, "kind": "distributed_switch", "name": dvs, "location": lid}, {"network": lid})
        # Hosts per class, summing to the location's hosts (largest remainder).
        total = sum(loc["hosts"].values())
        raw = {c: total * layout[c] for c in CLUSTER_ORDER}
        n_cls = {c: int(raw[c]) for c in CLUSTER_ORDER}
        for c in sorted(CLUSTER_ORDER, key=lambda c: raw[c] - n_cls[c], reverse=True)[: total - sum(n_cls.values())]:
            n_cls[c] += 1
        prev_share = loc["hosts"]["previous"] / total
        host_no, ds_no, vm_no = 0, 0, 1000
        loc_clusters = []
        for cls in CLUSTER_ORDER:
            n = max(1, round(total * layout[cls] / 12))  # the same rule as the NOC's clusters
            sizes = _split(max(n_cls[cls], n), n)
            n_prev = round(sum(sizes) * prev_share) if cls in WORKLOADS else 0
            prev_left = n_prev
            gen_of = {}
            for i in range(n, 0, -1):  # previous generation fills from the last cluster backwards
                take = min(prev_left, sizes[i - 1])
                gen_of[i] = take
                prev_left -= take
            for i in range(1, n + 1):
                cid = f"{lid.upper()}-{CLASS_LETTER[cls]}-{i:02d}"
                base = random.Random(f"{seed}-{cid}").uniform(84, 98)  # the NOC's base for the same cluster
                c = E.add({"id": cid, "kind": "cluster", "name": cid, "location": lid, "class": cls, "base": base,
                           "workload_domain": wld_of[cls]}, {"compute": wld_of[cls], **({"class": f"class-{cls}/{lid}"} if cls in WORKLOADS else {})})
                loc_clusters.append(c)
                pg = f"pg-{cid.lower()}"
                E.add({"id": pg, "kind": "port_group", "name": pg, "cluster": cid}, {"network": f"{lid}-vds-{[k for k, w in rules['workload_domains'].items() if cls in w['classes']][0]}"})
                c["port_group"] = pg
                c["hosts"] = []
                n_prev_here = gen_of[i]
                for j in range(sizes[i - 1]):
                    host_no += 1
                    gen = "previous" if j >= sizes[i - 1] - n_prev_here else "current"
                    c["hosts"].append({"id": f"{lid}-esx-{host_no:03d}", "kind": "host", "cluster": cid, "location": lid, "generation": gen})
                # Datastores.
                c["datastores"] = []
                n_ds = max(1, sizes[i - 1] // 4) if cls == "gold" else 1
                for _ in range(n_ds):
                    ds_no += 1
                    c["datastores"].append({"id": f"{lid.upper()}-DS-{ds_no:02d}", "kind": "datastore", "cluster": cid, "location": lid,
                                            "type": "VMFS" if cls == "gold" else "vSAN"})
        # Class view: one grouping node per class and location.
        for cls in WORKLOADS:
            E.add({"id": f"class-{cls}/{lid}", "kind": "location", "name": f"{loc['name']}", "location": lid, "class": cls},
                  {"class": f"class-{cls}"})
        # Pins: swap PCM scenario story host and datastore names into their clusters.
        by_id = {c["id"]: c for c in loc_clusters}
        all_hosts = [h for c in loc_clusters for h in c["hosts"]]
        for name, pin in host_pins.items():
            if not name.startswith(lid + "-") or pin["cluster"] not in by_id:
                continue
            target = by_id[pin["cluster"]]
            holder = next((h for h in all_hosts if h["id"] == name), None)
            slot = next(h for h in target["hosts"] if h["id"] not in host_pins and h is not holder)
            if holder is not None and holder is not slot:
                holder["id"], slot["id"] = slot["id"], name
            else:
                slot["id"] = name
            if "generation" in pin:
                slot["generation"] = pin["generation"]
            slot["pinned_build"] = pin.get("esxi_build")
        all_ds = [d for c in loc_clusters for d in c["datastores"]]
        for name, cid in rules["datastore_pins"].items():
            if not name.startswith(lid.upper() + "-") or cid not in by_id:
                continue
            slot = by_id[cid]["datastores"][0]
            holder = next((d for d in all_ds if d["id"] == name), None)
            if holder is not None and holder is not slot:
                holder["id"], slot["id"] = slot["id"], name
            else:
                slot["id"] = name
        # Hosts, datastores and VMs as nodes.
        ssh = rules["ssh_hosts"]
        for c in loc_clusters:
            cls = c["class"]
            for k, h in enumerate(c["hosts"]):
                g = gens[h["generation"]]
                build = builds["n" if h["generation"] == "current" else "n_minus_1"]
                if c["id"] in rules["esxi_build_overrides"]:
                    build = builds[rules["esxi_build_overrides"][c["id"]]]
                if h.get("pinned_build"):
                    build = builds[h["pinned_build"]]
                h.update(name=h["id"], host_model=g["model"], firmware=g["firmware"], esxi_build=build, cores=g["cores"],
                         cores_per_numa_node=g["cores_per_numa_node"], memory_gb=g["memory_gb"], class_of_service=cls,
                         ssh_on=(ssh["scenario_story"] in act and c["id"] == ssh["cluster"] and k < ssh["first"]), vms=[])
                h.pop("pinned_build", None)
                E.add(h, {"compute": c["id"]})
            for d in c["datastores"]:
                d.update(name=d["id"], vms=[])
                E.add(d, {"storage": lid})
            # Generated VMs, placed round-robin on the cluster's hosts.
            if cls in WORKLOADS:
                crng = random.Random(f"{seed}-vms-{c['id']}")
                n_vms = round(len(c["hosts"]) * per_host[cls])
                for v in range(n_vms):
                    vm_no += 1
                    role = roles[crng.randrange(len(roles))]
                    vcls = cls if cls != "mixed" else ("silver", "bronze")[crng.randrange(2)]
                    vcpu = rules["vm_vcpu"][cls][crng.randrange(len(rules["vm_vcpu"][cls]))]
                    r = crng.random()
                    base = (crng.uniform(55, 74.5) if r < 0.01 else crng.uniform(75, 79.9) if r < 0.04
                            else min(99.5, max(80.5, c["base"] + crng.uniform(-4, 4))))
                    host = c["hosts"][v % len(c["hosts"])]
                    ds = c["datastores"][v % len(c["datastores"])]
                    vm = {"id": f"{lid}-{role}-{vm_no:04d}", "kind": "vm", "cluster": c["id"], "host": host["id"], "datastore": ds["id"],
                          "location": lid, "role": role, "class_of_service": vcls, "vcpu": vcpu,
                          "memory_gb": vcpu * (8 if vcls == "gold" else 4),
                          "environment": "production" if crng.random() < est["vms"]["production_share"] else "non_production",
                          "guest_os": "windows" if crng.random() < est["vms"]["guest_os"]["windows"] else "linux",
                          "tools_version": tools[min(len(tools) - 1, int(crng.expovariate(1.3)))],
                          "base": base, "vol": crng.uniform(0.5, 1.5)}
                    _add_vm(E, vm, c)
        # Management appliances: VMs of the management cluster, and nodes of the Management view.
        mc = by_id[f"{lid.upper()}-M-01"]
        apps = list(rules["appliances"]["per_location"])
        apps += [a for a in rules["appliances"]["per_region"] if rules["appliances"]["region_home"][loc["region"]] == lid]
        for a in apps:
            aid = (est["regions"][loc["region"]]["vcf_operations_instance"] if a == "vcf-operations"
                   else f"vcf-auto-{loc['region']}" if a == "vcf-automation" else f"{a}-{lid}")
            vm = {"id": aid, "kind": "vm", "cluster": mc["id"], "host": mc["hosts"][len(E.children["management"].get(vcf, [])) % len(mc["hosts"])]["id"],
                  "datastore": mc["datastores"][0]["id"], "location": lid, "role": "appliance", "appliance": a,
                  "appliance_name": APPLIANCE_NAMES[a], "class_of_service": "management", "vcpu": 8, "memory_gb": 32,
                  "environment": "production", "guest_os": "linux", "tools_version": tools[0], "base": 96.0, "vol": 0.5}
            _add_vm(E, vm, mc, management_parent=vcf)
    # Resource pools (T-2): the pools and the VMs they hold.
    t2 = act.get("T-2")
    if t2:
        o = t2["objects"]
        c = E.nodes[o["cluster"]]
        for pid, members in ((o["pool_web"], [f"tk-web-{i:03d}" for i in range(1, o["web_vms"] + 1)]),
                             (o["pool_batch"], [f"tk-bat-{i:03d}" for i in range(1, o["batch_vms"] + 1)])):
            E.add({"id": pid, "kind": "resource_pool", "name": pid, "cluster": c["id"], "location": c["location"],
                   "limit_ghz": t2["plant"]["pools"][pid]["limit_ghz"], "members": members}, {"compute": c["id"]})
            for k, name in enumerate(members):
                if name in E.nodes:
                    continue
                host = c["hosts"][k % len(c["hosts"])]["id"]
                vm = {"id": name, "kind": "vm", "cluster": c["id"], "host": host, "datastore": c["datastores"][0]["id"],
                      "location": "tk", "role": name.split("-")[1], "class_of_service": "silver", "vcpu": 4, "memory_gb": 16,
                      "environment": "production", "guest_os": "linux", "tools_version": "12.5", "base": 93.0, "vol": 0.6,
                      "scenario_story": True, "resource_pool": pid}
                _add_vm(E, vm, c)
    # PCM scenario story VMs.
    first_silver = {}
    for c in (n for n in E.nodes.values() if n["kind"] == "cluster" and n["class"] == "silver"):
        first_silver.setdefault(c["location"], c)
    named = _scenario_story_vm_names(act)
    for name in named:
        if name in E.nodes:
            continue
        pin = vm_pins.get(name, {})
        loc = name.split("-")[0]
        c = E.nodes[pin["cluster"]] if pin.get("cluster") in E.nodes else first_silver[loc]
        hosts = c["hosts"]
        host = pin.get("host") or hosts[int(_h(name) * len(hosts))]["id"]
        ds = pin.get("datastore") or c["datastores"][0]["id"]
        cls = pin.get("class") or (c["class"] if c["class"] != "mixed" else "silver")
        vcpu = pin.get("vcpu", 8)
        role = pin.get("role") or name.split("-")[1]
        vm = {"id": name, "kind": "vm", "cluster": c["id"], "host": host, "datastore": ds, "location": loc, "role": role,
              "class_of_service": cls, "vcpu": vcpu, "memory_gb": pin.get("memory_gb", vcpu * 4), "environment": "production",
              "guest_os": "windows" if _h(name, "os") < 0.45 else "linux", "tools_version": "12.5",
              "base": min(98.0, max(81.0, c["base"] + 2)), "vol": 0.6, "scenario_story": True}
        _add_vm(E, vm, c)
    # Class view clusters: attach after their grouping nodes exist.
    for c in [n for n in E.nodes.values() if n["kind"] == "cluster" and n["class"] in WORKLOADS]:
        key = f"class-{c['class']}/{c['location']}"
        if c["id"] not in E.parent["class"]:
            E.parent["class"][c["id"]] = key
            E.children["class"].setdefault(key, []).append(c["id"])
    # PCM scenario story VM attributes (T-1, M-1, M-2).
    _apply_scenario_story_vms(E, act)
    return E


def _add_vm(E: Estate, vm: dict, c: dict, management_parent: str | None = None):
    vm["name"] = vm["id"]
    parents = {"compute": vm["host"], "storage": vm["datastore"], "network": c["port_group"]}
    if c["class"] in WORKLOADS:
        parents["class"] = c["id"]
    if management_parent:
        parents["management"] = management_parent
    E.add(vm, parents)
    E.nodes[vm["host"]]["vms"].append(vm["id"])
    E.nodes[vm["datastore"]]["vms"].append(vm["id"])


def _scenario_story_vm_names(act: dict) -> list:
    """Every VM a PCM scenario story names, so it exists in the tree."""
    spec = generator.load_spec()
    names = [k for k in spec["estate"]["l2_tree"]["vm_pins"] if k != "note"]
    for sid, s in act.items():
        o = s.get("objects", {})
        for k in ("vm", "villain"):
            v = o.get(k)
            if isinstance(v, dict):
                v = v.get("vm")
            if isinstance(v, str):
                names.append(v)
        for k in ("victims", "vms", "app_vms", "affected_vms"):
            if isinstance(o.get(k), list):
                names += [x for x in o[k] if isinstance(x, str)]
        for k in ("busy_vm", "idle_vm", "web_example"):
            if isinstance(o.get(k), str):
                names.append(o[k])
        we = s.get("plant", {}).get("who_else")
        if we:
            names += we["objects"]
    out = []
    for n in names:
        if n not in out and n.split("-")[0] in ("sg", "va", "fr", "tk", "ld") and "-esx-" not in n and not n.startswith(("rp-",)):
            out.append(n)
    return out


def _apply_scenario_story_vms(E: Estate, act: dict):
    t1 = act.get("T-1")
    if t1:
        vm = E.nodes[t1["objects"]["vm"]]
        p = t1["plant"]["vm"]
        vm.update(vcpu=p["vcpu"], memory_gb=p["memory_gb"], guest_os=p["guest_os"], class_of_service=p["class"], role=p["role"])
    m1 = act.get("M-1")
    if m1:
        prev_hosts = [h for c in m1["plant"]["mixed_generation_clusters"] for h in E.kids("compute", c)
                      if h["kind"] == "host" and h["generation"] == "previous"]
        for k, name in enumerate(m1["objects"]["affected_vms"]):
            vm = E.nodes[name]
            vm.update(vcpu=m1["plant"]["vm"]["vcpu"], memory_gb=m1["plant"]["vm"]["memory_gb"], class_of_service="gold", role="sql")
            if name != m1["objects"]["vm"] and prev_hosts:
                _move_vm(E, vm, prev_hosts[k % len(prev_hosts)])
    m2 = act.get("M-2")
    if m2:
        for key in ("busy_vm", "idle_vm"):
            vm = E.nodes[m2["objects"][key]]
            p = m2["plant"][key]
            vm.update(vcpu=p["vcpu"], role=p["role"], class_of_service=p["class"], environment=p["environment"])


def _move_vm(E: Estate, vm: dict, host: dict):
    old = vm["host"]
    E.children["compute"][old].remove(vm["id"])
    E.nodes[old]["vms"].remove(vm["id"])
    E.children["compute"].setdefault(host["id"], []).append(vm["id"])
    E.parent["compute"][vm["id"]] = host["id"]
    host["vms"].append(vm["id"])
    vm["host"], vm["cluster"] = host["id"], host["cluster"]


# ---------------------------------------------------------------- lazy leaf nodes (Guest OS, disks, vNICs)

def node(E: Estate, nid: str) -> dict | None:
    if nid in E.nodes:
        return E.nodes[nid]
    if "/" in nid:
        vm_id, leaf = nid.split("/", 1)
        vm = E.nodes.get(vm_id)
        if vm and vm["kind"] == "vm":
            if leaf == "os":
                return {"id": nid, "kind": "guest_os", "name": f"{vm_id} Guest OS ({vm['guest_os'].capitalize()})", "vm": vm_id}
            if leaf.startswith("disk-"):
                return {"id": nid, "kind": "virtual_disk", "name": f"{vm_id} {leaf.replace('disk-', 'scsi0:')}", "vm": vm_id}
            if leaf == "nic-1":
                return {"id": nid, "kind": "vnic", "name": f"{vm_id} Network adapter 1", "vm": vm_id}
    return None


def leaf_children(E: Estate, view: str, vm: dict) -> list:
    if view == "compute":
        return [node(E, vm["id"] + "/os")]
    if view == "storage":
        return [node(E, f"{vm['id']}/disk-{i}") for i in range(min(3, 1 + vm["vcpu"] // 8))]
    if view == "network":
        return [node(E, vm["id"] + "/nic-1")]
    return []


def children(E: Estate, view: str, nid: str) -> list:
    n = node(E, nid)
    if n is None:
        return []
    if n["kind"] == "vm":
        return leaf_children(E, view, n)
    return E.kids(view, nid)


def path(E: Estate, view: str, nid: str) -> list:
    if nid in E.nodes:
        if nid not in E.parent[view] and nid != "estate":
            view = "compute"
        return [node(E, x) for x in E.path(view, nid)]
    n = node(E, nid)
    if n is None:
        return []
    return path(E, view, n["vm"]) + [n]


def view_of(E: Estate, nid: str, prefer: str = "compute") -> str:
    """The view an object sits in: the preferred one if it is there."""
    base = nid if nid in E.nodes else nid.split("/")[0]
    if base in E.parent[prefer] or base == "estate":
        return prefer
    return next((v for v in VIEWS if base in E.parent[v]), "compute")


# ---------------------------------------------------------------- scores (l2.node_score)

def p95_score(samples: list) -> float:
    """l2.node_score: the value met or beaten 95% of the time (the 5th percentile of the KPI samples)."""
    s = sorted(samples)
    return float(s[int(0.05 * len(s))])


def band(score: float | None) -> str:
    """SP5 bands, as the NOC: green, yellow, orange, red (catalog.kpi_band)."""
    return "no_data" if score is None else catalog.kpi_band(score)


def status_of(score: float | None) -> str:
    """Status chips: yellow shows amber; orange and red show red (the NOC's mapping)."""
    b = band(score)
    return {"green": "green", "yellow": "amber", "orange": "red", "red": "red"}.get(b, "no_data")


def _spread(window: str) -> float:
    return float(generator.load_spec()["estate"]["l2_tree"]["vm_performance"]["window_spread"][window])


WINDOW_HOURS = {"1h": 1, "24h": 24, "7d": 168, "30d": 720, "1y": 8760}


def in_window(at: datetime, now: datetime, window: str) -> bool:
    return (now - at).total_seconds() <= WINDOW_HOURS[window] * 3600


def kpi_from_parts_score(key: str, now: datetime, window: str) -> float:
    """l2.node_score of an object of PCM scenario story M-5, from its own 5-minute points (kpi_from_parts.py)."""
    from . import performance_tab as P, kpi_from_parts as S
    start, L, n = P._slots(now, window)
    return round(S.window_score(S.scenario_story()[key], WINDOW_HOURS[window], now.timestamp(), start, L, n), 1)


def vm_score(E: Estate, vm: dict, now: datetime, window: str, act: dict) -> float:
    """VM Performance over the window. Planted VMs carry their PCM scenario story's value while the PCM scenario story's time is in the window."""
    name = vm["id"]
    if act.get("M-5") and name == "sg-api-1617":
        return kpi_from_parts_score("vm_performance", now, window)
    n1 = act.get("N-1")
    if n1:
        o = n1["objects"]
        if name == o["villain"]["vm"]:
            return float(n1["plant"]["villain_score"])
        if name in o["victims"]:
            return float(n1["plant"]["victim_scores"][o["victims"].index(name)])
    t1 = act.get("T-1")
    if t1 and name == t1["objects"]["vm"]:
        return float(t1["plant"]["vm"]["vm_performance"])
    t2 = act.get("T-2")
    if t2 and vm.get("resource_pool") == t2["objects"]["pool_web"]:
        named = {v["vm"]: v["vm_performance"] for v in t2["plant"]["l1_evidence"]["victims"]}
        return float(named.get(name, 45 + 25 * _h(name, "t2")))
    m1 = act.get("M-1")
    if m1 and name in m1["objects"]["affected_vms"]:
        v = m1["plant"]["affected_vm_performance"][m1["objects"]["affected_vms"].index(name)]
        return float(v + 4 if window in ("1h", "24h") else v)
    m2 = act.get("M-2")
    if m2 and name in (m2["objects"]["busy_vm"], m2["objects"]["idle_vm"]):
        key = "busy_vm" if name == m2["objects"]["busy_vm"] else "idle_vm"
        return float(m2["plant"][key]["vm_performance"])
    l2s = act.get("L-2")
    if l2s and name == l2s["objects"]["vm"]:
        return float(l2s["plant"]["vm"]["vm_performance"])
    return round(max(0.0, vm["base"] - _spread(window) * vm["vol"] * (0.6 + 0.8 * _h(name, window))), 1)


def cluster_score(E: Estate, c: dict, now: datetime, window: str, act: dict) -> float:
    """Cluster Performance over the window, from the same function as the NOC wall (one definition)."""
    from ..noc import noc
    if act.get("M-5") and c["id"] == "SG-S-01":
        return kpi_from_parts_score("cluster_performance", now, window)
    scenario_story = next((s for s in act.values() if s.get("objects", {}).get("cluster") == c["id"]
                  and "cluster_performance" in s.get("plant", {})), None)
    hours = WINDOW_HOURS[window]
    if scenario_story or window == "1h":
        steps = 12 if hours <= 1 else 48
        samples = [noc.cluster_score({"id": c["id"], "base": c["base"]}, now - _td(hours * i / steps), scenario_story, now, 7)
                   for i in range(steps + 1)]
        s = p95_score(samples)
    else:
        s = round(max(0.0, c["base"] - _spread(window) * 0.7), 1)
    dip = next((x["plant"]["window_dip"] for x in act.values() if x.get("plant", {}).get("window_dip", {}).get("cluster") == c["id"]), None)
    if dip and in_window(generator.rel(dip["at"], now), now, window):
        s = min(s, float(dip["value"]))
    return s


def _td(hours: float):
    from datetime import timedelta
    return timedelta(hours=hours)


def host_score(E: Estate, h: dict, now: datetime, window: str, act: dict) -> float:
    """ESXi Performance: the contention of its VMs, bottom up (the 10th percentile of its VMs)."""
    if act.get("M-5") and h["id"] == "sg-esx-110":
        return kpi_from_parts_score("esxi_performance", now, window)
    vals = sorted(vm_score(E, E.nodes[v], now, window, act) for v in h["vms"])
    if not vals:
        return 99.0
    return vals[max(0, int(len(vals) * 0.1) - 1)] if len(vals) > 3 else vals[0]
