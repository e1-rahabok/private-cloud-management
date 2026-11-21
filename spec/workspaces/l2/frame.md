---
page: /l2/*
question: "Where am I: which activity, which object, which pillar, which period?"
role: l2
cadence: [live]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-083, D-086, D-087, D-097]
---

# L2 frame

Every L2 page sits in one frame. Each of the four dimensions has its own place, so they never mix in one menu (L2 design, 3).

```text
┌ L2 Platform  [Monitor] [Troubleshoot] [Improve]           [E2●]  Rules  Calendar ┐
├ View ▾  ┬ Object path                                                [window ▾]  ┤
│ tree    │ tabs (Monitor and Improve only)                                        │
│ search  │ content                                                                │
└─────────┴────────────────────────────────────────────────────────────────────────┘
```

With the Agent E2 panel open (D-097):

```text
┌ L2 Platform  [Monitor] [Troubleshoot] [Improve]           [E2●]  Rules  Calendar ┐
├──┬ Object path                       [window ▾] ┬ Agent E2                     × ┤
│▸ │ tabs                                         │ context: object · tab · window │
│● │ content; the card asked about is outlined    │ conversation                   │
│● │                                              │ [question…]             [Ask]  │
└──┴──────────────────────────────────────────────┴────────────────────────────────┘
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
- **Utilities, right, set apart:** the Agent E2 mark, then Rules, Calendar.
- **Switching activity keeps the selected object, view and window** (D-086).
- No other item in the top bar. Weekly, monthly, escalations, configuration and inventory are not menu items.

## Agent E2 mark

```yaml
question: "Is Agent E2 here to help, and where do I ask it?"
role: l2
cadence: [live]
api: /api/l2/agent/health
```

- **The mark:** "E2" in a small rounded square, like a colleague's initials (D-097). Never a sparkle or a robot.
- **In the top bar:** the mark with a status dot, named "Agent E2" for a screen reader.
  - Available (the service answers its health check): dark mark, green dot, tooltip "Agent E2 is available. Ask about this page."
  - Not available: grey mark, grey dot, tooltip "Agent E2 is not available".
  - Checked when the workspace opens and each time the panel opens. Never a guess.
  - A click opens the panel about the current page: object, tab and window, or the case.
- **On a card:** the same mark, small, at the right of the title of:
  - each metric of a VM's Performance tab (monitor.md);
  - each KPI of the Capacity tab on a cluster (monitor.md);
  - each finding row, in Monitor and Improve (monitor.md, Findings);
  - the case header, each chain link and each layer row (case.md).
  - Its name says what it asks about: "Ask Agent E2 about Run Queue".
  - It stays visible, quiet, at rest; it is not hidden until hover.
- **Not available:** the marks on cards stay, so the panel can say why there is no answer.

## Agent E2 panel

```yaml
question: "What does Agent E2 say about what I clicked, and from which sources?"
role: l2
cadence: [live]
api: /api/l2/agent/ask
```

- **Docked on the right, 400 px.** It pushes the content; it never covers it. While it is open:
  - the inventory tree folds to a 48 px strip with one button, "Show the inventory"; hover or focus opens it over the content, and a click on a node still navigates;
  - the card asked about has an outline, until another card is asked about or the panel closes.
- **Head:** "Agent E2", the context in one line (object · tab · window, or the case), and Close (×). Esc closes it and returns the focus to the mark that opened it.
- **The panel stays open across pages** (no page load). Its context follows the page. Each context (object and tab, or case) keeps its own conversation for the browser session.
- **Suggested questions** when a conversation starts, three at most, by what was clicked:
  - metric or KPI: "Is {95th percentile} a problem for this {kind}?", "Why the worst at {time}?", "What should I check next?";
  - finding: "Explain this finding.", "What should I check next?";
  - case, chain link or layer: "Is the VMware platform the cause?", "What should I check next?";
  - page: "What needs me on this {kind}?".
  - A click sends it. The question box under them takes any question; Enter sends.
- **While Agent E2 works:** "Agent E2 is reading the knowledge base and the facts PCM sent." with the seconds elapsed. A local model takes 10 to 40 seconds; no made-up progress steps.
- **An answer:**
  - the text, direct answer first, as Agent E2 wrote it;
  - each value its code computed, boxed, under "Computed, not written by the model";
  - "Sources": the knowledge files it read, as chips;
  - an object of the estate named in the text is a link to it, on the same tab and window;
  - footer: model, knowledge version, asked by, "recorded in the action history".
- **Clarifying questions** (at most one round): shown as a list under "Agent E2 asks"; the next question sent is the reply, with the earlier turns.
- **Only on a finding that is a problem:** "Troubleshoot this", as on the finding row.
- **No action that decides:** nothing in the panel confirms, rules out, approves or closes (L2 design, 8).
- **States:** empty (the suggestions); waiting; answer; clarify; not available ("The Agent E2 service is not available." and no answer); error (the error, and the question kept in the box).
- **Narrow screen (under 900 px):** the panel is a full-width sheet over the page, with Close at the top.

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
- **The Agent E2 panel stays** as it is; only its context line changes (D-097).

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
- The Agent E2 panel is not in the address: it is a conversation, not a page.
