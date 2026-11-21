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
- **The root is the estate.** In Compute the tree follows vCenter: Region (folder), Location (datacenter), vCenter Server (one per workload domain), Cluster, ESXi host. The VCF instance is not a level. A host's VMs and a VM's Guest OS are listed in the content area, not in the tree.
- **Each object has its vCenter icon,** so the tree reads like the vSphere Client.
- **Each node shows:**
  - its name and icon. No status dot: in a large estate the upper levels are always red, and a dot that never changes carries nothing;
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
- **The window picker is a drop-down** at the right of the path: one light button that names the window ("Last 24 hours") and opens a list: Last hour, Last 24 hours, Last 7 days, Last 30 days, Last year. The chosen one is ticked. Default: 24 hours in Monitor, 30 days in Improve.
  - The window stays when the object or tab changes.
  - Inside a case the picker is replaced by the case window, fixed.
  - It is a button with a list: the arrow keys move in the list, Enter chooses, Esc closes and returns to the button.
  - A custom range ("from, to" and "last N units") comes later. It needs the API to take a range (L2 design, 3.4).
- **No run line.** The page does not say which check run it reads. The tab and the window say what the page is about.

## Tabs

```yaml
question: "Which pillar am I reading?"
role: l2
cadence: [live]
reads: [l2.pillars]
```

- **Monitor and Improve only:** Summary, Availability, Performance, Capacity, Security, Configuration, Inventory, in that order.
  - **Inventory is a provider tab.** A VM, Guest OS, virtual disk or vNIC does not have it (l2.pillars, D-092).
- **Troubleshoot has no tabs.** A case crosses pillars.
- **No tab for compliance, cost or price.**
- **The tabs are the titles of the panel under them.** The selected tab and the panel are one shape: the tab has the panel's colour, a dark top edge, and no line between it and the panel. The other tabs are flat and grey. Everything the tab owns (message, notes, tables, charts, findings) is inside the panel; the object's name and the window are outside it.
- **Every tab shows its status dot,** on every page, not only the selected one. Summary shows the worst of the others. The dot is named for a screen reader.
- **Roles:** tab list, tab, tab panel. The arrow keys move between tabs; Enter opens one.

## Moving between pages

- **No page load.** A tab, the window, the tree, a table link, Group by, the class filter and a click on a chart change the content under the header; the header, the top bar and the tree stay. The tree keeps what the user opened.
- **The address still changes** on every move, so Back, Forward, a copied link and a reload all work (L2 design, 10).
- **While data is on its way** the selected tab and the window answer at once, and the panel dims. Nothing goes blank.
- **The last click wins.** A slow answer for a page the user has left never replaces the page they are on.
- **Keyboard focus** returns to the selected tab or to the window button after the move.

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
