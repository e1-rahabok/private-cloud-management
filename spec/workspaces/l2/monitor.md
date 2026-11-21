---
page: /l2/monitor/{view}/{object}/{pillar}
question: "What is wrong, at risk or wasteful under this object?"
role: l2
cadence: [daily, weekly, monthly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-039, D-042, D-083, D-086, D-088, D-091]
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
  - **Performance:** as above at the cluster and below. Above the cluster: the next section.
  - **Capacity** (l2.short_term_capacity): per cluster, CPU and memory utilization, average and 95th percentile across its hosts, and the imbalance. A cluster whose VMs wait says "Full now".
  - **Security** (l2.security_hygiene): hosts with SSH or ESXi Shell on outside a window, lockdown off, root logins, certificates near expiry.
  - **Configuration** (l2.configuration_variance): drift against the standard, and the variance across peers (ESXi builds, VMware Tools versions) with counts.
  - **Inventory** (l2.inventory_counts, l2.change_explanation): children by type with the change over the window; distribution across children; unexplained changes listed one by one, production and Gold first, with "This was expected" (reason required); explained changes counted by type.
- **States:** normal; empty; stale ("No data" for a location whose VCF Operations is not answering, never green); loading; error.

## Performance tab above the cluster

```yaml
question: "Were VMs hit, when, where and how wide; and is any cluster heading toward contention?"
role: l2
cadence: [daily, weekly]
reads: [l2.consumer_hits, l2.worst_vms, l2.provider_spread, l2.clusters_at, l2.iceberg]
api: /api/l2/monitor/{view}/{object}/performance
decisions: [D-091]
```

On every node above the cluster: estate, region, location, VCF instance, workload domain, class of service. L2 design, 4.3.1.

- **Class of service** (query `class`): Gold, Silver, Bronze, All. Default Gold. One filter for both sections. A VM counts by its own class; a cluster by its class.
- **Selected time** (query `at`): one time for the page, set by a click on any chart. Default: the worst point of Worst Cluster Performance in the window. "Back to the worst time" clears it.
- **Points:** 5 minutes for 1 hour and 24 hours; 1 hour for 7 days; 4 hours for 30 days; 1 day for 1 year. A point holds the worst value inside it.

### VM

- **Hit over time** (l2.consumer_hits): one chart, one count axis.
  - Line 1: VMs below green at that point.
  - Line 2: different VMs hit since the start of the window.
  - Under it, in words: "{different} different VMs were hit; never more than {most} at once, at {time}."
- **Worst VMs** (l2.worst_vms): 20 rows, worst first, and the count of all.
  - VM, worst VM Performance, the time of it, cluster, location, class.
  - Hit in the same 5 minutes: how many other VMs in scope were below green at that time.
  - With a selected time: the VMs below green at that time instead, worst first.
- **Just above the line** (l2.iceberg): VMs between 75 and 80, in scope.
- **Group by** stays with this section: it reads every VM under the node.

### Cluster

- **Actual slowness** (l2.provider_spread): one chart, 0 to 100%.
  - Solid: Worst Cluster Performance. Dashed: its 10th percentile across the clusters in scope, as vCommunity's Worst 10 Percent.
  - Each segment takes the band color of its value: green, yellow, orange, red.
  - In words: the worst value, when, which cluster; and the 10th percentile at the same time.
- **Potential slowness** (l2.provider_spread): the same, for Cluster Risk. Solid: the highest. Dashed: the 90th percentile.
- **Clusters at {selected time}** (l2.clusters_at): every cluster in scope, worst Performance first.
  - Cluster, location, class, Performance at the time, Risk at the time, VMs below green at the time, different VMs hit over the window.
  - A click on a cluster selects it in the tree.
- **States:** normal; empty ("No {class} cluster under this object."); stale (a location without data is left out and named); loading; error.

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
