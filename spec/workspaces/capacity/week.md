---
page: /capacity
question: "What changed since last week?"
role: capacity
cadence: [weekly]
vocabulary: catalog/vocabulary/capacity.yaml
design: design/capacity-workspace.md
decisions: [D-014, D-054, D-055]
---

# Capacity: this week

Capacity moves slowly, so the change is the news (Capacity design, 3.15).

## Changes

```yaml
question: "What changed since last week?"
role: capacity
cadence: [weekly]
reads: [capacity.run_out_date, capacity.purchase_plan, capacity.quadrant]
api: /api/capacity/week
```

- **Next procurement round:** when it closes, and how many groups are in it.
- **Decision dates that moved:** each group whose decision date moved by 7 days or more against last week, with the cause.
  - New demand in the register, for example: "FR-Silver: 130 days earlier because of dr-ocp-wave-2 (OpenShift migration)".
- **Groups that entered their decision window this week.**
- **Peak warnings:** a close week crosses usable capacity while the trend does not. Recommendation: borrow hosts, burst, or limit other work. No purchase.
- **Waste:** groups in dark grey, with the remaining capacity.
- **States:** normal, empty ("No change since last week."), loading, error.
