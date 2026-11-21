---
page: /l2/*
question: "Where am I: which activity, which object, which pillar, which period?"
role: l2
cadence: [live]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-083, D-086, D-087]
---

# L2 frame

Every L2 page sits in one frame. Each of the four dimensions has its own place, so they never mix in one menu (L2 design, 3).

```text
┌ L2 Platform  [Monitor] [Troubleshoot] [Improve]                    Rules  Calendar ┐
├ View ▾  ┬ Object path                                                  [window ▾]  ┤
│ tree    │ tabs (Monitor and Improve only)                                          │
│ search  │ content                                                                  │
└─────────┴──────────────────────────────────────────────────────────────────────────┘
```

## Top bar

```yaml
question: "Am I looking for problems, solving one, or improving?"
role: l2
cadence: [live]
reads: [l2.pillars]
```

- **Activities, left:** Monitor, Troubleshoot, Improve. The current one is marked.
  - Troubleshoot shows the number of open cases.
- **Utilities, right, set apart:** Rules, Calendar.
- **Switching activity keeps the selected object, view and window** (D-086).
- No other item in the top bar. Weekly, monthly, escalations, configuration and inventory are not menu items.

## Inventory tree

```yaml
question: "Where in the estate am I?"
role: l2
cadence: [live]
reads: [l2.tree, l2.pillar_status]
api: /api/l2/tree
```

- **Left pane.** A view picker above the tree: Compute (default), Storage, Network, Class of service, Management.
- **The root is the estate.** The tree expands down to the cluster. A cluster's hosts, a host's VMs and a VM's Guest OS are listed in the content area, worst first, not in the tree.
- **Each node shows:**
  - its name;
  - a status dot for the current pillar and window (Summary uses the worst pillar);
  - the count of open cases on it and below it, when there are any.
- **Children are sorted by activity** (l2.tree child_sort): Monitor worst first; Troubleshoot open cases first; Improve largest opportunity first.
- **Selecting a node** changes the object of the current page and keeps the activity, pillar and window.
- **Search** under the tree finds any object in any view by name. Picking a result selects it.
- **States:** normal; stale (a location whose VCF Operations is not answering shows grey with "No data", never green: D-041); loading; error.

## Object header

```yaml
question: "Which object and which period is this page about?"
role: l2
cadence: [live]
reads: [l2.time_window]
```

- **The path** of the selected object, estate first, each part a link.
- **The window picker:** 1 hour, 24 hours, 7 days, 30 days, 1 year. Default: 24 hours in Monitor, 30 days in Improve.
  - The window stays when the object or tab changes.
  - Inside a case the picker is replaced by the case window, fixed.
- **The run line** under the path, in Monitor: which check run the window reads, for which region, and when.

## Tabs

```yaml
question: "Which pillar am I reading?"
role: l2
cadence: [live]
reads: [l2.pillars]
```

- **Monitor and Improve only:** Summary, Availability, Performance, Capacity, Security, Configuration, Inventory.
- **Troubleshoot has no tabs.** A case crosses pillars.
- **No tab for compliance, cost or price.**

## Addresses

- Every page is a URL of activity, view, object, pillar and window, so any state can be shared or reopened (L2 design, 10).

| Path | Page |
|---|---|
| `/l2` | Redirects to `/l2/monitor/compute/estate/summary` |
| `/l2/monitor/{view}/{object}/{pillar}?window=` | monitor.md |
| `/l2/troubleshoot/{view}/{object}` | troubleshoot.md |
| `/l2/troubleshoot/new` | troubleshoot.md, Log complaint |
| `/l2/troubleshoot/case/{case}` | case.md |
| `/l2/improve/{view}/{object}/{pillar}?window=` | improve.md |
| `/l2/rules` | rules.md |
| `/l2/calendar` | calendar.md |

- `now` and `enable` (synthetic only) are kept on every link, as on every PCM page.
