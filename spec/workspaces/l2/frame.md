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
- **The same mark and panel are on the NOC desk** (D-098). One shared piece of code; each workspace says only what its pages send, name and suggest.
- **In the top bar:** the mark with a status dot, named "Agent E2" for a screen reader.
  - Available (the service answers its health check): dark mark, green dot, tooltip "Agent E2 is available. Ask about this page."
  - Not available: grey mark, grey dot, tooltip "Agent E2 is not available".
  - Checked when the workspace opens and each time the panel opens. Never a guess.
  - A click opens the panel about the current page: object, tab and window, or the case.
- **On a card:** the same mark, small, at the right of the title of:
  - each layer heading of a VM's Performance tab, Guest OS and Virtual Motherboard (monitor.md);
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
- **Fits the window.** The panel is fixed to the window, below the demo bar when it is shown. The answers scroll inside it; the head and the question box stay in view. A long answer never pushes the panel off screen.
- **One fold per question.** Each question with its answer is a fold: the newest is open, older ones show only the question, one line. A click opens or closes any of them and the choice is kept. The context (object · tab · window) is shown on a question only when it differs from the one above it.
- **Head:** "Agent E2", the context in one line (object · tab · window, or the case), and Close (×). Esc closes it and returns the focus to the mark that opened it.
- **The panel stays open across pages** (no page load). Its context follows the page. Each context (object and tab, or case) keeps its own conversation for the browser session.
- **Suggested questions** when a conversation starts, and again when its context changes (another card or the page itself), three at most, by what was clicked:
  - metric or KPI: "Is {95th percentile} a problem for this {kind}?", "Why the worst at {time}?", "What should I check next?";
  - layer of a VM: "Is the {layer} layer the problem?", "Which of its metrics matters most here?", "What should I check next?";
  - finding: "Explain this finding.", "What should I check next?";
  - case, chain link or case layer: "Is the VMware platform the cause?", "What should I check next?";
  - page, on a VM's Performance tab: "Is this VM performing well over the {window}?", "Which layer is the problem, if any?", "What should I check next?";
  - page, anywhere else: "What needs me on this {kind}?", "What should I check next?".
  - A click sends it. The question box under them takes any question; Enter sends.
- **What PCM sends for a whole-page question** (the top bar mark), so an overall question is answered from the numbers on screen:
  - always: the object and its path, the tab, the window, the tab's status and score, the findings under the object (ten at most), the worst children (ten at most), the calendar entries in the window;
  - on the Summary tab: every pillar with its status and headline;
  - on a VM's Performance tab: both layers, each with its status and, per metric, Now, Worst with its time, 95th percentile and which way is better. No points: those go with a question about one metric.
- **What PCM sends for a layer of a VM:** that layer's status and every metric with its points, Now, Worst, 95th percentile; the other layer's status and figures without points.
- **What PCM sends with every question: the screen** (D-103), so Agent E2 speaks of what the person sees, never of the data behind it ("the provided JSON"):
  - who asks (an L2 platform engineer) and that they typed only the question;
  - the page: the object, its kind, the tab and the window, as in the panel's context line;
  - what was clicked: the top bar mark (the whole page), or the mark on a chart, layer, finding or case, by its name;
  - what that card shows, in one line: for a trend chart, the KPI over the window, how often a point comes and that a point holds the worst value inside it, and Now, Worst and 95th percentile in their band colours;
  - for a KPI that belongs to another object than the page (a cluster's KPI on a VM's Capacity tab), the object it belongs to, by name;
  - for a KPI, where to look next (drill_down): the page and tab that take it further, what that page shows, and what PCM does not show yet. Cluster Performance and Cluster Risk: the cluster's Performance tab (the two KPIs over the window, then the hosts worst first with their scores); PCM does not show the sub-metrics of Cluster Performance yet. Cluster Consumption: "What makes up Consumption" on the cluster's Capacity tab.
- **Not PCM's to send:** whether a move of a KPI is a drop. That is domain knowledge, Agent E2's (D-078): its KPI change level and its calculator read the points PCM sends.
- **While Agent E2 works:** "Agent E2 is reading the knowledge base and the facts PCM sent." with the seconds elapsed. A local model takes 10 to 40 seconds; no made-up progress steps.
- **An answer:**
  - the text, direct answer first, as Agent E2 wrote it;
  - each value its code computed, boxed, under "Computed, not written by the model";
  - "Sources (n)": a control, closed by default, with the number of knowledge files Agent E2 read. Open, it shows the files as chips. Closed, the answer is the text, the computed values and the footer, so a long list of files does not crowd the panel (D-099). One click answers "from which sources?";
  - an object of the estate named in the text is a link to it, on the same tab and window;
  - footer: model, knowledge version, asked by, "recorded in the action history".
- **Clarifying questions** (at most one round): shown as a list under "Agent E2 asks"; the next question sent is the reply, with the earlier turns.
- **Only on a finding that is a problem:** "Troubleshoot this", as on the finding row.
- **No action that decides:** nothing in the panel confirms, rules out, approves or closes (L2 design, 8).
- **States:** empty (the suggestions); waiting; answer; clarify; not available ("The Agent E2 service is not available." and no answer); model not reachable, when the service answers but its model does not ("Agent E2 is running, but its model cannot be reached." and no answer); error (the error, and the question kept in the box).
- **Which part is down** decides the words, so the person who installs PCM looks in the right place: no service is the Agent E2 service (deploy/README.md, Agent E2); no model is its key or its network.
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
