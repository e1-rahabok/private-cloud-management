---
page: /capacity/clusters
question: "Which cluster groups need a decision, and by when?"
role: capacity
cadence: [weekly]
vocabulary: pcm/capacity/spec/vocabulary.yaml
design: pcm/capacity/design-note.md
decisions: [D-054, D-056, D-094]
---

# Capacity: cluster groups

## Remaining capacity against time remaining

```yaml
question: "Which cluster groups need a decision, and by when?"
role: capacity
cadence: [weekly]
reads: [capacity.remaining_percent, capacity.time_remaining_days, capacity.quadrant, l2.cluster_check]
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
- **The check overrides the forecast** (Capacity design, 3.4; l2.cluster_check).
  - When a cluster in the group is closed at the latest Periodic Cluster Check, the row says "Closed for new VMs" with the cluster and since when, whatever the forecast says.
  - Never "Full now" or "VMs waiting". No contention of the last hour on this page (Capacity design, 3.16).
- **Never a data-centre or location total** (Capacity design, 3.1).
- **States:** normal, loading, error.
