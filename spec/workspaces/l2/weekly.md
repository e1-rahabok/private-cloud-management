---
page: /l2/weekly
question: "What does a week show that a day did not?"
role: l2
cadence: [weekly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-039, D-042, D-046]
---

# L2 weekly check result

PCM runs the weekly check early Sunday in each region's local time (D-042). L2 reviews it in about 1 hour. The page shows only what the daily check cannot see; anything the daily check already reports is not repeated.

## This week's measures

```yaml
question: "Is the platform getting quieter and are we finding problems first?"
role: l2
cadence: [weekly]
reads: [l2.weekly_measures]
api: /api/l2/weekly
```

- **The four L2 outcomes** (L2 design, 2), this week against last week:
  - urgent alerts;
  - repeated escalations;
  - share of problems found by a check before an alert or a complaint;
  - median time to diagnose a known problem.
- **The run line:** when PCM ran, for which region, and the expected review time.
- **States:** normal, stale, loading, error.

## Patterns a day cannot show

```yaml
question: "What drifts, hides inside an average, or gets worse every day?"
role: l2
cadence: [weekly]
reads: [l2.weekly_check]
```

- **Three kinds of finding, each with its evidence:**
  - **Slow drift:** a metric that moves the same way on most days of the week. Seven nightly points, not one.
  - **Hidden in the average:** one vCPU or one virtual disk at its limit while the VM total looks normal. The VM-level number would never alert.
  - **Configuration drift:** the full configuration scan against the baseline, objects that drifted this week.
- **Each finding needs an owner and an action** (D-042). "Assign" asks for both; a finding without them stays open and shows first next week.
- **States:** normal, empty ("The week shows nothing the daily check did not."), loading, error.

## Alerts that slipped through

```yaml
question: "Which alerts did no check predict, and what would have caught them?"
role: l2
cadence: [weekly]
reads: [l2.slipped_alerts]
```

- **One row per alert** raised this week that no check finding predicted.
- **What would have caught it,** where the weekly check found the cause, with a link to change the check rule.
- **States:** normal, empty ("Every alert this week was predicted."), loading, error.
