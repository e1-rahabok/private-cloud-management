---
page: /capacity/group/{id}
question: "How does total become usable, what limits it, and when does it run out?"
role: capacity
cadence: [weekly]
vocabulary: pcm/capacity/spec/vocabulary.yaml
design: pcm/capacity/design-note.md
decisions: [D-054, D-061, D-065]
---

# Capacity: one cluster group

## Usable capacity

```yaml
question: "How does total capacity become usable capacity?"
role: capacity
cadence: [weekly]
reads: [capacity.usable]
api: /api/capacity/groups/{id}
```

- **Per resource, the steps:** total, minus HA, minus maintenance, minus buffer, equals usable.
- **Units:** threads, GB of DRAM, TB.
- **States:** normal, unknown group ("No such group"), loading, error.

## Forecast

```yaml
question: "When does it run out, and what does a 90-day view miss?"
role: capacity
cadence: [weekly]
reads: [capacity.weekly_peak, capacity.forecast, capacity.forecast_90d, capacity.seasonal_uplift, capacity.run_out_date]
```

- **One chart per resource:**
  - 13 months of weekly peaks;
  - the forecast for the next 13 months, with the usable line;
  - the 90-day trend for comparison.
- **The run-out and decision dates.**
- **A peak warning**, when only a close week crosses.
- **The demand register entries** that affect the group.
- **States:** normal, loading, error.
