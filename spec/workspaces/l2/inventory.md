---
page: /l2/inventory
question: "What changed, and is that expected?"
role: l2
cadence: [daily, weekly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-020, D-050, D-062, D-063]
---

# L2 detailed inventory and changes

Detailed inventory tracks change for analysis (D-020). The NOC sees the last hour as a count. L2 sees the week, with the explanation of each change.

## What exists

```yaml
question: "How much of each object is there, per location?"
role: l2
cadence: [weekly]
reads: [l2.inventory_counts]
api: /api/l2/inventory
```

- **Per location:** hosts, clusters, VMs, datastores, and the change since the start of the window.
- **States:** normal, stale, loading, error.

## Changes, and their explanation

```yaml
question: "Is every change explained?"
role: l2
cadence: [daily, weekly]
reads: [l2.change_explanation]
```

- **Each change is matched to what explains it,** in this order:
  - the PCM action record (an action by a person, Agent E2 or a policy);
  - an approved change window in the ITSM change calendar (D-062);
  - a self-service request in VCF Automation;
  - DRS, for moves inside a cluster.
- **Explained changes are counted,** per type and day. Nobody reads 40 DRS moves an hour one by one.
- **Unexplained changes are listed one by one,** production first, with who made them and through which interface.
- **"This was expected"** records the reason and the person. The change then counts as explained by L2.
- **Window:** 7 days by default, 30 days as an option.
- **States:** normal, empty ("Every change in this window is explained."), loading, error.
