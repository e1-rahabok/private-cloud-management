---
page: /capacity/waste
question: "What can we reclaim, starting where?"
role: capacity
cadence: [weekly]
vocabulary: catalog/vocabulary/capacity.yaml
design: design/capacity-workspace.md
decisions: [D-056, D-060]
---

# Capacity: waste and reclamation

## Reclamation

```yaml
question: "What can we reclaim, starting where?"
role: capacity
cadence: [weekly]
reads: [capacity.reclamation]
api: /api/capacity/waste
```

- **Per group, the five SP5 areas, easiest first.** Each shows its count and what it frees, honestly: an idle VM powered off frees memory and allocation, not CPU cycles.
- **The run-out before and after reclaiming.**
- **Cost avoidance:** shown only when reclaiming moves the group out of the round. It is valued at the round's cost for that group (D-060).
- **The word "saving" is never used.**
- **States:** normal, empty ("Nothing planted to reclaim."), loading, error.
