---
page: /l2
question: "What needs me today?"
role: l2
cadence: [daily]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-039, D-045, D-046, D-052]
---

# L2 daily check result

L2 opens on the check result, not the alert list (L2 design, 3.1). L2 also does architecture and engineering (D-046), so the page fits a 10-minute review (D-039).

## Verdicts

```yaml
question: "Is anything wrong now, at risk, or wasteful?"
role: l2
cadence: [daily]
reads: [l2.daily_check]
api: /api/l2/daily
```

- **Three cards: Present health, Risk, Efficiency.** Each has a status chip and its count of findings.
- **Never one combined score** (L2 design, 3.2).
- **The run line:** when PCM ran the check, for which region, and how long the human review is expected to take ("about 10 minutes when nothing needs you").
- **States:** normal, empty ("Nothing needs you this morning."), stale, loading, error.

## Findings

```yaml
question: "Which findings need a human, worst first?"
role: l2
cadence: [daily]
reads: [l2.daily_check]
```

- **One row per finding**, worst first:
  - verdict;
  - pillar;
  - the object, with its parent chain (cluster, then host, then VM);
  - a one-line summary;
  - a link to investigate.
- **Explained by the calendar:** a finding that business context explains shows the calendar entry next to it, and drops to the bottom (L2 design, 3.6).
- **Proposed fix:** where a finding has one, the row shows it with Approve and Reject buttons. Reject asks for a reason.
- **Agent E2:** "Explain this finding" (D-076).
- **States:** normal, empty, loading, error.

## Trust ladder

```yaml
question: "Which action types have earned automation?"
role: l2
cadence: [weekly]
reads: [l2.offer_promotion]
api: /api/l2/action-types
```

- **One row per action type:**
  - tier;
  - approvals;
  - rollbacks;
  - whether promotion is offered.
- **"Make automatic"** appears only when promotion is offered. It asks for a reason, and states: "You will be the person accountable for its automatic runs" (D-050).
- **States:** normal, empty, loading, error.

## Slipped alerts

```yaml
question: "What did the check miss?"
role: l2
cadence: [daily]
reads: [l2.slipped_alerts]
```

- **Alerts since the previous run that no finding predicted** (D-039). Each row links to add a check rule.
- **States:** normal, empty ("The check predicted every alert."), loading, error.
