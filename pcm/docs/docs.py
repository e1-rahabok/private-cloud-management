"""Docs workspace: read-only documentation of PCM's own objects (pcm/docs/design-note.md, D-082).

GENERATED from every workspace's spec/ folder, pcm/core/spec/catalog/ and the action record. Do not edit by hand (D-070).

Export for private-cloud-explained (Docs design, 2.7):
    python3 -m pcm.docs.docs --export <folder> [--now 2026-10-19T10:05:00+08:00]
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

import yaml

from ..core import generator
from ..l2 import l2
from ..noc import noc

PCM = Path(__file__).resolve().parents[1]  # the pcm folder: one folder per workspace, and core
KINDS = ("measure", "sop", "policy", "threshold", "standard", "setting")
MEASURE_FILES = ("executive", "noc", "l2", "capacity")
# Where each kind is changed (Docs design, 2.2). None: nothing in PCM changes it; the specification does.
CHANGED_AT = {"policy": "/l2/rules", "threshold": "/l2/rules", "standard": "/l2/improve/compute/estate/configuration"}
HISTORY_ACTIONS = {"policy": ("publish_policy",), "threshold": ("publish_threshold",), "standard": ("change_standard",)}


def _y(p):
    return yaml.safe_load((PCM / p).read_text())


def page_files() -> list:
    """Every page specification, workspace by workspace."""
    return sorted(PCM.glob("*/spec/pages/*.md"))


def clean(text):
    """Builder rule 9: no decision ID in page text. Drops a parenthesis that names one, then any left over."""
    if not isinstance(text, str):
        return text
    text = re.sub(r"\s*\([^()]*\bD-\d{3}\b[^()]*\)", "", text)
    return re.sub(r",?\s*\bD-\d{3}\b", "", text).strip()


def _clean_all(v):
    if isinstance(v, dict):
        return {k: _clean_all(x) for k, x in v.items() if k != "decisions"}
    if isinstance(v, list):
        return [_clean_all(x) for x in v]
    return clean(v)


# ---------------------------------------------------------------- what reads what (Docs design, 2.3)

def page_reads() -> list:
    """Every page section with its reads, from the page specifications."""
    out = []
    for f in page_files():
        text = f.read_text()
        head = yaml.safe_load(text.split("---")[1])
        for m in re.finditer(r"```yaml\n(.*?)```", text, re.S):
            block = yaml.safe_load(m.group(1))
            section = (re.findall(r"^## (.+)$", text[:m.start()], re.M) or [head.get("page")])[-1]
            out.append({"page": head["page"], "workspace": f.parents[2].name, "section": section, "question": block.get("question"),
                        "role": block.get("role"), "cadence": block.get("cadence"), "reads": block.get("reads") or []})
    return out


def measures() -> dict:
    out = {}
    for f in MEASURE_FILES:
        for k, v in _y(f"{f}/spec/catalog.yaml")["entries"].items():
            out[k] = {**v, "file": f}
    return out


def dangling_reads() -> list:
    ids = set(measures())
    return sorted({r for p in page_reads() for r in p["reads"] if r not in ids})


def used_on(kind: str, oid: str, obj: dict) -> list:
    ids = {oid}
    if kind == "threshold":
        ids = {obj["measure"]}
    if kind == "sop":
        return [{"page": "/noc/alert/{id}", "workspace": "noc", "section": "Steps", "question": "What do I do now?",
                 "role": "l1", "cadence": ["live"]}]
    if kind == "policy":
        return [{"page": "/l2/rules", "workspace": "l2", "section": "Action policies", "question": "What runs automatically, and within which guardrails?",
                 "role": "l2", "cadence": ["weekly"]},
                {"page": "/l2/improve/{view}/{object}/{pillar}", "workspace": "l2", "section": "Opportunities", "question": "Which risks and opportunities sit under this object, largest first?",
                 "role": "l2", "cadence": ["weekly"]}]
    if kind in ("setting", "standard"):
        # Settings and standards are read by the engine; list the specifications that name them.
        hits = []
        for f in page_files() + sorted(PCM.glob("*/spec/catalog.yaml")) + [PCM / "core/spec/catalog/thresholds.yaml"]:
            if re.search(rf"\b{re.escape(oid)}\b", f.read_text()):
                hits.append({"page": str(f.relative_to(PCM.parent)), "workspace": "specification", "section": "mentions it",
                             "question": None, "role": None, "cadence": None})
        return hits
    return [{k: p[k] for k in ("page", "workspace", "section", "question", "role", "cadence")} for p in page_reads() if ids & set(p["reads"])]


# ---------------------------------------------------------------- the objects

def _status(source: str | None) -> str:
    return "proposal" if source and "proposal" in source.lower() else "confirmed"


def _first_sentence(text: str, limit: int = 160) -> str:
    """The first sentence, cut at a word boundary: a title cut mid-word reads as a fault."""
    t = clean(" ".join(str(text).split())).split(". ")[0].rstrip(".")
    return t if len(t) <= limit else t[:limit].rsplit(" ", 1)[0] + " …"


def objects(enable=()) -> list:
    out = []
    for k, v in measures().items():
        shown = re.search(r'[Ss]hown as "([^"]+)"', v.get("description", ""))
        out.append({"kind": "measure", "id": k, "title": _first_sentence(v.get("description", "")), "version": None,
                    "owner": f"pcm/{v['file']}/spec/catalog.yaml", "status": "confirmed", "shown_as": shown.group(1) if shown else None,
                    "body": _clean_all({x: y for x, y in v.items() if x not in ("file",)}), "group": v["file"]})
    for f in sorted((PCM / "noc/spec/sops").glob("*.yaml")):
        s = yaml.safe_load(f.read_text())
        out.append({"kind": "sop", "id": s["id"], "title": s["title"], "version": s.get("version", 1), "owner": "l2", "status": "confirmed",
                    "body": _clean_all({k: v for k, v in s.items() if k not in ("id", "title", "version")})})
    for p in l2.policies(enable):
        out.append({"kind": "policy", "id": p["action_type"], "title": p["action_type"].replace("_", " ").capitalize(),
                    "version": p["version"], "owner": p["owner"], "status": "confirmed",
                    "body": _clean_all({"tier": p["tier"], "guardrails": p["guardrails"], "record": p["record"]})})
    spec = generator.load_spec()
    for k, v in spec["thresholds"].items():
        cur = {**v, **l2.STATE.thresholds.get(k, {})}
        out.append({"kind": "threshold", "id": k, "title": f"{v['metric']} {v['operator']} {cur['value']}", "version": cur["version"],
                    "owner": v["owner"], "status": _status(v.get("source")), "body": _clean_all({x: cur[x] for x in cur if x not in ("owner", "version")})})
    for k, v in spec["standards"].items():
        out.append({"kind": "standard", "id": k, "title": f"{v['title']}: {v['value']}", "version": l2.STATE.standards.get(k, v["version"]),
                    "owner": v["owner"], "status": "confirmed", "body": _clean_all({x: v[x] for x in v if x not in ("owner", "version")})})
    for k, v in _y("core/spec/catalog/settings.yaml")["settings"].items():
        out.append({"kind": "setting", "id": k, "title": _first_sentence(v.get("description", k)), "version": None, "owner": v.get("owner"),
                    "status": _status(v.get("source")), "body": _clean_all({x: y for x, y in v.items() if x != "owner"})})
    return out


def index(enable=()) -> dict:
    objs = objects(enable)
    groups = {k: [{f: o[f] for f in ("id", "title", "version", "owner", "status")} for o in objs if o["kind"] == k] for k in KINDS}
    return {"groups": groups, "counts": {k: len(v) for k, v in groups.items()}}


def history(kind: str, oid: str) -> list:
    acts = HISTORY_ACTIONS.get(kind, ())
    return [{k: r.get(k) for k in ("at", "action", "actor_human", "actor_agent", "reason", "before", "after")}
            for r in noc.STATE.history if r["action"] in acts and r["target"] == oid]


def detail(kind: str, oid: str, enable=()) -> dict | None:
    o = next((x for x in objects(enable) if x["kind"] == kind and x["id"] == oid), None)
    if o is None:
        return None
    raw = generator.load_spec()["thresholds"].get(oid, {}) if kind == "threshold" else {}
    return {**o, "changed_at": CHANGED_AT.get(kind), "used_on": used_on(kind, oid, raw or o.get("body", {})), "history": history(kind, oid)}


# ---------------------------------------------------------------- export to private-cloud-explained (Docs design, 2.7)

def _front(title, doc_type, domain, sid, version, owner, now):
    fm = {"title": title, "doc_type": doc_type, "domain": domain, "priority": "high", "audience": ["admin", "engineer"],
          "access_scope": "infra-team", "sources": [{"type": "pcm", "id": sid, "version": version}],
          "last_ingested": now.isoformat(), "origin": "generated", "reviewed_by": "", "reviewed_on": "", "owner": owner}
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) + "---\n\n"


IMPACT = {"cluster": "VMs on the cluster wait for CPU or memory; the cluster is red on the NOC wall.",
          "datastore": "VMs on the datastore stop writing, and pause, when it fills.",
          "vcf_operations_instance": "PCM shows No data for the locations behind the instance; nothing there is measured.",
          "wall_finding": "A change outside the plan. Its effect depends on what changed; the wall shows it until it is explained."}


def _impact(applies_to: dict) -> str:
    return IMPACT.get(applies_to.get("root_object_type") or applies_to.get("kind"), "See the NOC incident for the objects affected.")


def _sop_md(s, now):
    steps = s["body"]["steps"]
    by = lambda k: [x for x in steps if x["kind"] == k]
    li = lambda xs: "\n".join(f"{i + 1}. {x['text']}" + (f" Only when: {x['when']}." if x.get("when") else "") for i, x in enumerate(xs)) or "None."
    acts = s["body"].get("actions", {})
    return (_front(s["title"], "runbook", "runbooks", f"sop/{s['id']}", s["version"], "l2", now)
            + f"# {s['title']}\n\nGenerated by PCM from its SOP `{s['id']}`, version {s['version']}. Change it in PCM, not here.\n\n"
            + f"## Trigger\n\n{'; '.join(f'{k.replace(chr(95), chr(32))}: {v}' for k, v in s['body'].get('applies_to', {}).items())}.\n\n"
            + f"## Impact\n\n{_impact(s['body'].get('applies_to', {}))}\n\n"
            + f"## Diagnosis\n\n{li(by('diagnosis'))}\n\n"
            + f"## Actions\n\n{li(by('action'))}\n\n"
            + ("Allowed actions, and who may press them:\n\n" + "\n".join(f"- `{k}`: tier {v.get('tier')}, for {', '.join(v.get('allowed_for', []))}" for k, v in acts.items()) + "\n\n" if acts else "")
            + f"## Escalation\n\n{li(by('escalate'))}\n\n"
            + f"## Verification\n\n{li(by('verify'))}\n\n"
            + "## Follow-up\n\nL2 reviews every escalation of this kind; a repeat means the SOP or a check rule changes.\n")


def _plan_md(title, sid, scope, objectives, roles, procedure, testing, now):
    return (_front(title, "operations-plan", "operations", sid, 1, "l2", now) + f"# {title}\n\nGenerated by PCM. Change it in PCM, not here.\n\n"
            + f"## Scope\n\n{scope}\n\n## Objectives\n\n{objectives}\n\n## Roles\n\n{roles}\n\n## Procedure\n\n{procedure}\n\n"
            + f"## Testing\n\n{testing}\n\n## Review\n\nThe owner reviews these in the monthly review. Every change is in PCM's action record.\n")


def export(out: Path, now: datetime, enable=()) -> list:
    objs = objects(enable)
    files = {}
    for s in [o for o in objs if o["kind"] == "sop"]:
        files[f"content/runbooks/pcm-{s['id']}.md"] = _sop_md(s, now)
    pol = [o for o in objs if o["kind"] == "policy"]
    files["content/operations/pcm-action-policies.md"] = _plan_md(
        "PCM action policies", "policy", "Every action PCM may take on the estate, its tier and its guardrails.",
        "Automatic where guardrails make it safe; a person decides everything else. No approval is recorded for an automatic run.",
        "L2 owns the policies; PCM runs them; the policy owner and version are accountable for an automatic run.",
        "\n".join(f"- `{p['id']}` v{p['version']}, owner {p['owner']}: tier {p['body']['tier']}; guardrails: "
                  + "; ".join(f"{k} {v}" for k, v in p["body"]["guardrails"].items()) for p in pol),
        "Every policy change is replayed against recent history before it is published.", now)
    th = [o for o in objs if o["kind"] in ("threshold", "standard")]
    files["content/operations/pcm-thresholds-and-standards.md"] = _plan_md(
        "PCM thresholds and configuration standards", "thresholds-standards", "Alert thresholds and configuration standards PCM checks the estate against.",
        "Alert on what needs a person; keep every host and VM on one known configuration.", "L2 owns both.",
        "\n".join(f"- `{o['id']}` v{o['version']}: {o['title']}" for o in th),
        "A threshold is replayed against 30 days of history before it is published.", now)
    st = [o for o in objs if o["kind"] == "setting"]
    files["content/operations/pcm-settings.md"] = _plan_md(
        "PCM settings", "settings", "Every target and threshold PCM's models use, with its owner and status.",
        "No number in PCM is invented: each setting names its source, or says it is a proposal.",
        "Each setting names its owning role.",
        "\n".join(f"- `{o['id']}` ({o['status']}, owner {o['owner']}): {o['title']}" for o in st),
        "Settings marked proposal are confirmed by their owner before go-live.", now)
    inv = l2.inventory(now, 7, enable)
    rows = "\n".join(f"| {c['name']} | {c['hosts']} | {c['clusters']} | {c['vms']} | {c['datastores']} |" for c in inv["counts"])
    files["content/inventory/pcm-inventory-summary.md"] = (
        _front("Private cloud inventory summary", "bom", "inventory", "inventory/summary", 1, "l2", now)
        + "# Private cloud inventory summary\n\nGenerated by PCM from the live estate. Change nothing here: it is overwritten on the next export.\n\n"
        + "## Scope\n\nHosts, clusters, VMs and datastores per location.\n\n"
        + f"## Register\n\n| Location | Hosts | Clusters | VMs | Datastores |\n|---|---|---|---|---|\n{rows}\n\n"
        + "## Compatibility\n\nNot in this export. Host versions are in PCM's configuration review.\n\n"
        + "## Support status\n\nNot in this export.\n\n"
        + f"## Source export\n\nPCM, {now.isoformat()}.\n")
    for rel, text in files.items():
        p = out / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description="Export PCM's own objects as Markdown for private-cloud-explained.")
    ap.add_argument("--export", required=True, help="the private-cloud-explained checkout, or any folder")
    ap.add_argument("--now", default=None)
    a = ap.parse_args()
    for f in export(Path(a.export), generator.parse_now(a.now)):
        print(f)


if __name__ == "__main__":
    main()
