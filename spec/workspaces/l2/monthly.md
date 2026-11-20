---
page: /l2/monthly
question: "How are we doing against this year's goals, and what do we decide for next month?"
role: l2
cadence: [monthly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-043, D-045, D-050]
---

# L2 monthly review

The monthly review is the team meeting (D-043). The page is shown on one screen in the room. PCM prepares it, so the day goes to judgement, not to slides.

## Last month's decisions

```yaml
question: "Did we do what we decided last month?"
role: l2
cadence: [monthly]
reads: [l2.team_decision]
api: /api/l2/monthly
```

- **The pack opens here** (L2 design, 3.14): every open decision with its owner, due date and state (done, open, overdue).
- **Mark done** records who closed it and when.
- **States:** normal, empty ("No decision is open."), loading, error.

## Goals for the year

```yaml
question: "Will we meet this year's goals?"
role: l2
cadence: [monthly]
reads: [goals.status]
```

- **One row per goal:** each month's value so far, the year-end projection, the target, the status.
- **The projection is the same number the CIO sees** (one definition, goals.status).
- **States:** normal, loading, error.

## Baselines: one year

```yaml
question: "What does a year show that a week did not?"
role: l2
cadence: [monthly]
reads: [l2.weekly_measures, l2.repeated_escalations, l2.slipped_alerts]
```

- **Twelve months of the four L2 outcomes** (L2 design, 2), one small chart each.
- **Repeated escalations by problem type,** with whether the loop closed: a check rule or an SOP added.
- **Alerts that slipped through,** per month.
- **States:** normal, loading, error.

## Configuration risk and capacity outlook

```yaml
question: "Is risk going down, and what does the Capacity team expect?"
role: l2
cadence: [monthly]
reads: [l2.configuration_review, capacity.purchase_plan]
```

- **Configuration risk:** open findings by group (correct it, update it, simplify it, optimize it) now.
- **Capacity outlook,** read from the Capacity workspace, never recomputed: groups in the next round, peak warnings. L2 does not plan capacity (D-014).
- **States:** normal, loading, error.

## Decisions for next month

```yaml
question: "What do we decide, who owns it, and by when?"
role: l2
cadence: [monthly]
reads: [l2.team_decision]
```

- **Record a decision:** what, owner, due date. All three are required: a decision without an owner comes back unchanged next month (D-043).
- **States:** normal, loading, error.
