---
page: /l2/calendar
question: "What is expected this week?"
role: l2
cadence: [weekly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-031, D-065]
---

# L2 Calendar

A utility, not an activity. Business context is an input, not a memory (L2 design, 7.2).

## Calendar

```yaml
question: "What is expected this week?"
role: l2
cadence: [weekly]
reads: [l2.findings]
api: /api/l2/calendar
```

- **Entries for the next 14 days and the last 7 days:** kind, location, time, note, who added it.
- **An Add form:** kind, location, start, end, note. The next check run reads new entries; cases show them on their timeline.
- **Each entry shows which findings it explained** in the latest run.
- **States:** normal; empty ("Nothing on the calendar. The checks judge without business context."); loading; error.
