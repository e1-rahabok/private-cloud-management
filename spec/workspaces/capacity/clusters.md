---
page: /capacity/clusters
question: "Which cluster groups need a decision, and by when?"
role: capacity
cadence: [weekly]
vocabulary: catalog/vocabulary/capacity.yaml
design: design/capacity-workspace.md
decisions: [D-054, D-056]
---

# Capacity: cluster groups

## Remaining capacity against time remaining

```yaml
question: "Which cluster groups need a decision, and by when?"
role: capacity
cadence: [weekly]
reads: [capacity.remaining_percent, capacity.time_remaining_days, capacity.quadrant, noc.cluster_performance]
api: /api/capacity/groups
```

- **A scatter plot:** x is time remaining (days, capped at 13 months), y is capacity remaining (%). One dot per cluster group, read from its tightest resource.
  - **Red:** needs a decision soon and is not in the plan.
  - **Teal:** in the plan, or healthy.
  - **Dark grey:** waste, never green (Capacity design, 3.3).
- **A table below, sorted by decision date:**
  - group;
  - tightest resource;
  - remaining;
  - run-out;
  - decision date;
  - in the plan, and whether the round is on time;
  - status.
- **Contention overrides the forecast** (Capacity design, 3.4).
  - When a cluster in the group is not serving its VMs well now (Cluster Performance orange or red), the row says "Full now: VMs waiting" with the cluster and its score, whatever the forecast says.
- **Never a data-centre or location total** (Capacity design, 3.1).
- **States:** normal, loading, error.
