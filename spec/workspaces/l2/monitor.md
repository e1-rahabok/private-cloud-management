---
page: /l2/monitor/{view}/{object}/{pillar}
question: "What is wrong, at risk or wasteful under this object?"
role: l2
cadence: [daily, weekly, monthly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-039, D-042, D-083, D-086, D-088]
---

# L2 Monitor

Top down over the whole estate (L2 design, 4). The landing page of the workspace: the estate, Summary, 24 hours. SP5: the daily check first thing in the morning, before the first problem.

## Summary tab

```yaml
question: "How is each pillar under this object?"
role: l2
cadence: [daily]
reads: [l2.pillar_status, l2.findings]
api: /api/l2/monitor/{view}/{object}/summary
```

- **One row per pillar:** Availability, Performance, Capacity, Security, Configuration, Inventory. Each row has its status chip, its headline in one sentence, and its count of findings. A click opens the pillar's tab.
- **Never one combined score** (L2 design, 3.3).
- **Findings, worst first,** all pillars, under the object, for the window (below).
- **At the estate root with the 1-year window,** the four L2 measures over twelve months, and repeated problems by type with whether the loop closed (l2.measures, l2.repeated_problems).
- **States:** normal; empty ("Nothing needs you under this object."); stale; loading; error.

## Pillar tab: summary, children, detail

```yaml
question: "Which children are worst on this pillar, and how many sit just above the line?"
role: l2
cadence: [daily, weekly]
reads: [l2.node_summary, l2.node_score, l2.iceberg]
api: /api/l2/monitor/{view}/{object}/{pillar}
```

- **Summary:** the object's own value for the pillar over the window, with a trend; and the count of children outside the green zone, over the window.
- **The iceberg** (Performance): the count of children just above the green line (75 to 80) now, and its trend. "Rising" or "steady" in words.
- **Children, worst first:** one row per child with its score over the window (l2.node_score), its score over the last hour, its status chip (the worse of the two), and its red and orange alerts. A click selects the child in the tree.
  - Host rows add: host model, ESXi build, running VMs.
  - VM rows add: vCPU, memory, class, environment, Guest OS.
- **Group by** (l2.slice_attributes): a picker above the children. Grouped, each row is one attribute value: how many objects, how many below green, the worst score. Default: no grouping.
  - Group by reads every VM under the object, not only direct children. Each group shows its VMs, hosts, how many sit below green and just above the line, the worst score, and how many VMs are wider than their host's NUMA node.
- **Pillar content:**
  - **Availability** (l2.availability_events): VMs down this month, counted or not; hosts not connected; HA restarts.
  - **Performance:** as above.
  - **Capacity** (l2.short_term_capacity): per cluster, CPU and memory utilization, average and 95th percentile across its hosts, and the imbalance. A cluster whose VMs wait says "Full now".
  - **Security** (l2.security_hygiene): hosts with SSH or ESXi Shell on outside a window, lockdown off, root logins, certificates near expiry.
  - **Configuration** (l2.configuration_variance): drift against the standard, and the variance across peers (ESXi builds, VMware Tools versions) with counts.
  - **Inventory** (l2.inventory_counts, l2.change_explanation): children by type with the change over the window; distribution across children; unexplained changes listed one by one, production and Gold first, with "This was expected" (reason required); explained changes counted by type.
- **States:** normal; empty; stale ("No data" for a location whose VCF Operations is not answering, never green); loading; error.

## Findings

```yaml
question: "What did the checks find here, and where does each go?"
role: l2
cadence: [daily, weekly]
reads: [l2.findings, l2.slipped_alerts]
```

- **One row per finding under the object,** filtered to the tab's pillar (all pillars on Summary), worst first:
  - status chip, pillar, path, object, one-line summary;
  - the window that found it (daily or weekly);
  - for the 7-day window: the kind (slow drift, hidden in the average, configuration drift) and its evidence (seven nightly values, or the instance against the VM average).
- **Where it goes** (l2.findings outcomes):
  - a problem: **"Troubleshoot this"**, which opens a case with the finding as its trigger; once open, a link to the case;
  - an opportunity or a risk: **"Improve this"**, which opens Improve on the same object and pillar.
- **Explained by the calendar:** the entry is named, and the finding sorts last.
- **24-hour window:** the daily check's findings. **7-day window:** what a day cannot show, never a repeat of a daily finding.
- **Alerts that slipped through:** alerts no finding predicted, each with "What would have caught it" and a link to Rules.
- **Agent E2:** "Explain this finding" on any row.
- **States:** normal; empty ("Nothing needs you under this object."); loading; error.
