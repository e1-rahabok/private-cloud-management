---
page: /l2/monitor/{view}/{object}/{pillar}
question: "What is wrong, at risk or wasteful under this object?"
role: l2
cadence: [daily, weekly, monthly]
vocabulary: catalog/vocabulary/l2.yaml
design: design/l2-workspace.md
decisions: [D-039, D-042, D-083, D-086, D-088, D-091, D-092, D-094, D-095]
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
- **Group by** (l2.slice_attributes): a picker above the children. Not on a VM, Guest OS, virtual disk or vNIC: it groups objects, and these are one object (D-092). Grouped, each row is one attribute value: how many objects, how many below green, the worst score. Default: no grouping.
  - Group by reads every VM under the object, not only direct children. Each group shows its VMs, hosts, how many sit below green and just above the line, the worst score, and how many VMs are wider than their host's NUMA node.
- **Pillar content:**
  - **Availability** (l2.availability_events): VMs down this month, counted or not; hosts not connected; HA restarts.
  - **Performance:** as above at the cluster and below. Above the cluster: the next section.
  - **Capacity:** the next two sections (D-094). Never a snapshot table.
  - **Security** (l2.security_hygiene): hosts with SSH or ESXi Shell on outside a window, lockdown off, root logins, certificates near expiry.
  - **Configuration** (l2.configuration_variance): drift against the standard, and the variance across peers (ESXi builds, VMware Tools versions) with counts.
  - **Inventory** (provider objects only; l2.inventory_counts, l2.change_explanation): children by type with the change over the window; distribution across children; unexplained changes listed one by one, production and Gold first, with "This was expected" (reason required); explained changes counted by type.
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

- **Hit in words** (l2.consumer_hits): no chart. A per-VM trend does not scale to a large estate; the Worst VMs table carries the detail.
  - "{different} different VMs were hit; never more than {most} at once, at {time}."
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

## Performance tab on a VM

```yaml
question: "Where is this VM slow, at which layer, and when?"
role: l2
cadence: [daily, weekly]
reads: [l2.realms, l2.node_score]
api: /api/l2/monitor/{view}/{object}/performance
decisions: [D-092]
```

On a VM, the tab shows detail. The Guest OS runs on top of the Virtual Motherboard, so the page is two layers, one over the other, never side by side.

- **No Group by, no "Just above the line", no "Children outside green", no trend card.** They describe a group; this is one VM.
- **Tabs:** Summary, Availability, Performance, Capacity, Security, Configuration. No Inventory (D-092).
- **Layer 1, Guest OS** (status chip in its heading): Run Queue, Context Switches, Paging, Guest OS Performance.
- **Layer 2, Virtual Motherboard** (status chip in its heading): CPU Ready, CPU Co-Stop, Memory Wait, Disk Latency, VM Performance.
- **One chart per metric,** over the window picked at the top. Points as in D-091 (5 minutes for 1 hour and 24 hours, 1 hour for 7 days, 4 hours for 30 days, 1 day for 1 year); a point holds the worst value inside it. The two Performance scores use the 0 to 100% scale and the band colors.
- **Three named figures beside each chart,** each with its unit after the number:
  - **Now:** the latest point.
  - **Worst:** the worst point of the window, with its time.
  - **95th percentile:** the value that 95% of the points were better than.
  - **Never an average.** It hides the peak the VM's owner felt.
- **Names and units:** Title Case; abbreviations in capitals (CPU, VM, OS, vCPU); the unit follows the number and is never part of the name: "CPU Ready 2.5%", "Disk Latency 5.6 ms", "Context Switches 7,346/s".
- **Under the layers:** "Log a complaint about this VM"; Children, worst first (the Guest OS); Findings.
- **States:** normal; stale; loading; error. A metric with no data in the window shows "No data" in place of its chart, never a flat line.

## Capacity tab on a cluster

```yaml
question: "Can this cluster take more VMs now, what is driving it, and is it heading to closed?"
role: l2
cadence: [daily, weekly]
reads: [l2.cluster_check, l2.contention_now, l2.cluster_kpi_series, l2.consumption_parts, l2.usable_capacity, l2.host_spread, l2.capacity_hosts]
api: /api/l2/monitor/{view}/{object}/capacity
decisions: [D-094, D-095]
```

On a cluster. On a host, VM or Guest OS, the tab shows its cluster's page with the host marked. L2 design, 4.3.3 and 4.3.4.

- **Verdict, in words** (l2.cluster_check, l2.contention_now):
  - Open: "Open for new VMs at the check of the {period} to {end time}."
  - Closed: "Closed for new VMs since the check of {date} ({n} checks). {Reason}."
    - Reason, by the rule that matched: "Consumption {v}% is above 80%"; "Performance {v}% is below 20%"; "Consumption {c}% and Performance {p}% are both orange, and Risk {r}% is above 60%".
  - No data: "No check for the {period} to {end time}: {KPI} has no data." Never "Open".
  - Beside it, when Performance over the last hour is orange or red: a chip "Contention now", with the value and its time.
  - The tab's status is the worse of the check and the last hour.
- **Three charts, one per KPI** (l2.cluster_kpi_series): Cluster Consumption, Cluster Performance, Cluster Risk, in that order, one above the other, one time axis.
  - 0 to 100%. Display bands as background. The two closure levels as dashed lines, labelled "Closes above 80%" and "Orange for closure above 60%" (Performance: below 20% and below 40%).
  - Points as on the Performance tab: 5 minutes for 1 hour and 24 hours, 1 hour for 7 days, 4 hours for 30 days, 1 day for 1 year. A point holds the worst value inside it.
  - Beside each chart: **Now**, **Worst** (with its time), **95th percentile**, and the check's value labelled by its percentile and period: "95th percentile, 24 hours to 08:00 GMT+8: 84%". Never "Worst" for a check value. Never an average.
- **Check strip** under the three charts (l2.cluster_check): one cell per check period in the window, closed (labelled) or open, aligned with the time axis; a cell with no check is grey "No data".
  - Fewer than 7 check periods in the window (1 hour, 24 hours): words instead of the strip: the latest check and the one before it.
- **What consumption is made of** (l2.consumption_parts): one chart per part, each in % of usable capacity, with Now, Worst, 95th percentile: CPU Thread Utilization, Memory Consumed, Memory Ballooned, Memory Zip Swap, and Memory Tiering where the hosts have a tier.
- **Usable capacity** (l2.usable_capacity): for CPU threads and DRAM GB: total, minus HA, minus buffer, equals usable; running hosts of all hosts. The buffer links to the Capacity team's setting; it is not edited here.
- **Spread between hosts** (l2.host_spread): two charts, CPU Thread Utilization and Memory Consumed, in % of each host's own capacity. Two lines each: the highest host and the lowest host at each point, named in the tooltip. No average line.
- **Hosts, worst first** (l2.capacity_hosts): host; CPU Thread Utilization and Memory Consumed, each 95th percentile and Worst, with a sparkline; running VMs; CPU and Memory Overcommit; state (running, maintenance mode, disconnected, not responding). A click selects the host. On a host, VM or Guest OS page, that host's row is marked.
- **Months ahead:** one sentence, "Months ahead, and when to buy, are in the Capacity workspace", linked to the cluster's group there. No date or remaining figure from it.
- **Words:** "Spread between hosts" for highest against lowest host. "CPU Imbalance" only for vCommunity's running threads per running core. Never "imbalance" alone.
- **States:** normal; closed; no check; stale (the location's VCF Operations is not answering: grey, "No data", never the last verdict); a KPI with no data shows "No data" in place of its chart; loading; error.

## Capacity tab above the cluster

```yaml
question: "How many clusters are closed or near closure, is that rising, and how wide is the pressure?"
role: l2
cadence: [daily, weekly]
reads: [l2.closed_count, l2.consumption_spread, l2.near_closure, l2.capacity_clusters_at, l2.cluster_check]
api: /api/l2/monitor/{view}/{object}/capacity
decisions: [D-091, D-094, D-095]
```

On every node above the cluster: estate, region, location, VCF instance, workload domain, class of service. L2 design, 4.3.5.

- **Class of service** (query `class`): Gold, Silver, Bronze, All. One filter for the tab. Default Gold, always: it is the class that matters most. Mixed clusters count under All only.
- **Selected time** (query `at`): one time for the page, set by a click on any chart. Default: the highest point of the Highest Cluster Consumption line. "Back to the highest point" clears it.
- **Clusters closed for new VMs** (l2.closed_count): one bar per check period, the count of closed clusters in scope.
  - In words: "{closed} of {all} {class} clusters closed at the latest check; {n} closed and {m} opened since the check before."
  - Fewer than 7 check periods in the window: the words only.
- **Consumption across clusters** (l2.consumption_spread): one chart, 0 to 100%, closure levels as dashed lines.
  - Solid: the highest Cluster Consumption. Dashed: its 90th percentile across the clusters in scope.
  - Each segment takes the band color of its value.
  - In words: the highest value, when, which cluster; the 90th percentile at the same time.
- **Near closure** (l2.near_closure): open clusters whose Consumption at the latest check is above 60%, and the count at each check over the window, in words: "rising", "steady" or "falling".
- **Clusters at {selected time}** (l2.capacity_clusters_at): every cluster in scope. Closed first, then near closure, then highest Consumption.
  - Cluster, location, class; verdict at the latest check and since when; Consumption, Performance and Risk at the selected time; Consumption sparkline over the window; "Contention now" where it applies.
  - A click on a cluster selects it in the tree.
- **Not on this tab:** the spread of Cluster Performance and Cluster Risk (they are on the Performance tab); any total, sum or average of consumption across clusters; any forecast, run-out date, decision date, Capacity Remaining or Time Remaining.
- **Months ahead:** one sentence linking to the Capacity workspace's clusters page, filtered to the node's location and class.
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
- **Capacity findings** (l2.capacity_findings, D-094):
  - 24-hour window: a cluster closed at the latest check. Closed on Consumption alone: amber, "Improve this". Closed with Performance red, or by rule 2: red, "Troubleshoot this".
  - 7-day window: a cluster whose check Consumption drifts up, by the drift rule (l2.findings), while still open: amber, "Improve this".
  - Every chip on the Capacity tab has a finding row under it, and every capacity finding has its chip. "Nothing needs you under this object" never shows beside a capacity chip.
- **Explained by the calendar:** the entry is named, and the finding sorts last.
- **24-hour window:** the daily check's findings. **7-day window:** what a day cannot show, never a repeat of a daily finding.
- **Alerts that slipped through:** alerts no finding predicted, each with "What would have caught it" and a link to Rules.
- **Agent E2:** "Explain this finding" on any row.
- **States:** normal; empty ("Nothing needs you under this object."); loading; error.
