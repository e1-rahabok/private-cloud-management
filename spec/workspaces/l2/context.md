---
page: /l2/context
question: "What is expected this week?"
role: l2
cadence: [weekly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-031]
---

# L2 business calendar

## Calendar

```yaml
question: "What is expected this week?"
role: l2
cadence: [weekly]
api: /api/l2/calendar
```

- **Entries for the next 14 days and the last 7 days:** kind, location, time, note, and who added each one.
- **An Add form:** kind, location, start, end, note. The next check run reads new entries.
- **Each entry shows which findings it explained** in the latest check.
- **States:** normal, empty ("Nothing on the calendar. The checks judge without business context."), loading, error.
