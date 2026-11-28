---
page: /l2/monitor/{view}/{object}/{pillar}
question: "What is wrong, at risk or wasteful under this object?"
role: l2
cadence: [daily, weekly, monthly]
vocabulary: pcm/l2/spec/vocabulary.yaml
design: pcm/l2/design-note.md
decisions: [D-039, D-042, D-083, D-086, D-088, D-091, D-092, D-094, D-095, D-097, D-100, D-109]
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
reads: [l2.node_summary, l2.node_score, l2.object_kpis, l2.iceberg]
api: /api/l2/monitor/{view}/{object}/{pillar}
```

- **Summary, Performance tab, cluster and below (not a VM)** (l2.object_kpis, D-100): the object's KPI over the window, first on the tab, one chart per KPI with its three figures, as on the VM tab. Never a card with one number.
  - **Agent E2 mark** at the right of each KPI's name: "Ask Agent E2 about {KPI}" (frame.md; D-117). PCM sends the KPI's points, Now, Worst, the percentile figure, the other KPIs of the tab, and the parts at the KPI's worst point when it has a Details fold (D-111). The parts in the fold get no mark.
  - Cluster: Cluster Performance, then Cluster Risk. ESXi host: ESXi Performance. Datastore, resource pool: Worst VM Performance. Port group: its cluster's Cluster Performance and Cluster Risk. Guest OS: Guest OS Performance. Virtual disk, vNIC: VM Performance.
  - **Details** (l2.kpi_details, D-106): under the chart of Cluster Performance and of Cluster Risk, a fold named "Details", **closed when the page opens** and left to the reader: a good value needs no explanation. Its header reads "Details", then "What {KPI} is made of. Lower is better for every part." Opened, one chart per part, as the parts of Consumption on the Capacity tab: Now, Worst (with its time), the percentile figure, the same points as the KPI. A fold the person opened stays open when the window or the time changes. **An ESXi host has the same fold under ESXi Performance, with nine parts over the VMs on the host (D-108).** Every part carries the band of its band ends (the Agent E2 catalog rows of the object, 20-second levels applied to the 5-minute peak): the figures are band pills, the chart has the four tinted zones and its line takes the band of each value, as a KPI does. Not on a datastore, resource pool, Guest OS, virtual disk or vNIC. On a VM, the counters with catalog band ends (Run Queue per vCPU 2, 4, 8, from the adapter's Guest OS Performance table; Paging, CPU Ready, CPU Co-Stop, Memory Wait, Disk Latency) are drawn the same way; Context Switches has none and stays plain. **A metric card puts its title on its own full-width row, on one line, above the figures and the chart, so every chart starts at the same height and a pair (Guest OS Performance, VM Performance) has the same height.**
    - **Cluster Performance, 9 parts** (the contention of the VMs, then the worst host): worst and 90th percentile of vCPU Ready, vCPU Co-stop, memory wait and disk latency (the 90th percentile of the disk is over virtual disks), and the highest ESXi network packets (error + dropped). Bands: none, because the catalog has levels for 20-second points only. The packets part has 5-minute levels (ends 0.2, 0.4, 0.8) and carries its band.
    - **Cluster Risk, the catalog's 12 parts** (the worst host; knowledge/catalog/thresholds-risk.yaml, D-113): CPU thread utilization, CPU imbalance, memory ballooned, swapped + zipped memory, active memory of tiered hosts, NVMe read latency, CPU reservation, memory reservation, CPU overcommit ratio, memory overcommit ratio, CPU monster VM : host ratio, memory monster VM : host ratio, under the catalog names. Each carries its band from the catalog's limits. The two memory tiering parts only where a host has a tier: none in the estate yet, so a cluster shows 10. DRAM memory consumed is not a Risk part (Agent E2, 2026-11-22).
    - **PCM scenario story M-5 (D-109):** for SG-S-01, sg-esx-110 and sg-api-1617 the parts are the rows the KPI was computed from, not values derived from it; on sg-api-1617 each of the Virtual Motherboard layer's nine metrics is read from the row of VM Performance it comes from, under the catalog's name; no metric shows twice.
    - **Release 1.0:** the values are placeholders derived from the KPI's series, as the parts of Consumption are, until PCM reads the parts from VCF Operations. Never an average. No cause: what moved, not why (D-084).
  - Under the charts, one sentence: "{n} of {m} children outside green: over the {window}, or in the last hour."
- **No "Just above the line" section** on the Performance tab (D-105): the chart of VMs between 75 and 80 and its sentence are removed. l2.iceberg is still read for the headline and the Group by counts.
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
- **The two Performance (%) scores first** (D-100), in a section "Performance" above the layers: Guest OS Performance, then VM Performance, stacked, each with its chart and figures. They say whether anything is wrong; the layers say where.
- **Tabs:** Summary, Availability, Performance, Capacity, Security, Configuration. No Inventory (D-092).
- **Layer 1, Guest OS** (status chip in its heading, from Guest OS Performance): the four sub-metrics of the KPI (Peak vCPU run queue length, per vCPU; Peak disk queue length; Free memory; Memory page-out rate) and Context Switches. Limits and units: the adapter's guest-os-performance.md. Free memory is higher-is-better: its limits are lower limits (green from 512 MB, yellow from 256, orange from 128, red below).
- **Layer 2, Virtual Motherboard** (status chip in its heading, from VM Performance): the nine sub-metrics of the KPI: Peak CPU Co-stop among any vCPU, Peak CPU Ready among any vCPU, Peak CPU Overlap, Memory wait, Peak read/write latency among vDisks, Peak network TX dropped packets, CPU Net Run, VM Memory Ballooned, VM swapped + zipped memory. Limits and units: the adapter's vm-performance.md. Memory Wait is the memory row of VM Performance: Memory Contention plus NVMe wait (D-114). On a host without memory tiering it equals Memory Contention.
- **One chart per metric,** over the window picked at the top. Points as in D-091 (5 minutes for 1 hour and 24 hours, 1 hour for 7 days, 4 hours for 30 days, 1 day for 1 year); a point holds the worst value inside it. The two Performance scores use the 0 to 100% scale and the band colors.
- **Three named figures beside each chart,** each with its unit after the number:
  - **Now:** the latest point.
  - **Worst:** the worst point of the window, with its time.
  - **Percentile figure:** the value that 95% of the points were better than, named by direction (l2.statistics, D-131): "5th percentile" where higher is better (the Performance scores, Guest OS free memory), "95th percentile" where higher is worse.
  - **Never an average.** It hides the peak the VM's owner felt.
  - **Band figures** (D-100): on a 0 to 100% KPI each figure shows the band of its value, as a tinted pill with dark text, a bar in the band color and the band's name (visual-style.md, Band figures). Counters without bands stay plain.
- **Agent E2 mark** at the right of each layer heading: "Ask Agent E2 about the {layer} layer", for a question about the layer as a whole (frame.md; D-097).
- **Agent E2 mark** at the right of each metric's name: "Ask Agent E2 about {metric}" (frame.md, Agent E2 mark; D-097). PCM sends the metric's points, Now, Worst with its time, the percentile figure, which way is better, the layer and its status, the other metrics of both layers, and the calendar entries in the window.
- **Names and units:** a sub-metric with an Agent E2 catalog line takes the catalog name, as written there (D-115); any other counter is in Title Case. Abbreviations in capitals (CPU, VM, OS, vCPU). The unit follows the number and is never part of the name: "Peak CPU Ready among any vCPU 2.5%", "Peak read/write latency among vDisks 5.6 ms", "Context Switches 7,346/s".
- **Under the layers:** "Log a complaint about this VM"; Children, worst first (the Guest OS); Findings.
- **States:** normal; stale; loading; error. A metric with no data in the window shows "No data" in place of its chart, never a flat line.

## Capacity tab on a cluster

```yaml
question: "Can this cluster take more VMs now, what is driving it, and is it heading to closed?"
role: l2
cadence: [daily, weekly]
reads: [l2.capacity_remaining, l2.cluster_check, l2.contention_now, noc.cluster_performance, l2.cluster_kpi_series, l2.consumption_parts, l2.usable_capacity, l2.host_spread, l2.capacity_hosts]
api: /api/l2/monitor/{view}/{object}/capacity
decisions: [D-094, D-095, D-100]
```

On a cluster. On a host, VM or Guest OS, the tab shows its cluster's page with the host marked. L2 design, 4.3.3 and 4.3.4.

- **On a VM (l2.vm_capacity, D-126):** the VM's own counters, not its cluster's. After the summary, Key Trends: CPU (VM Net Run, Guest OS CPU Run Queue) and Memory (Guest OS Used Memory, Peak Guest OS Paging activity), each with Now, Worst, the percentile figure and a chart. Bands only where the catalog has band ends (Used Memory has none). No verdict, usable capacity, host spread or host list; one sentence links to the cluster's Capacity tab.
- **Summary first** (l2.capacity_remaining, D-100), on a VM, ESXi host and cluster, headed "Summary" and the kind of object:
  - VM: Capacity Remaining (%), Time Remaining (days).
  - ESXi host, cluster: Capacity Remaining (%), Time Remaining (days), VM Remaining.
  - One card each, the unit after the number. Under them, nothing while the values are placeholders. Once real: "From VCF Operations, {time}."
  - No band colors: VCF Operations' capacity bands are not in the catalog, and none is invented here.
  - On a VM or host page, the cluster's page follows under "Its cluster, {cluster}".

- **Verdict, in words** (l2.cluster_check, l2.contention_now):
  - Open: "Open for new VMs at the check of the {period} to {end time}."
  - Closed: "Closed for new VMs since the check of {date} ({n} checks). {Reason}."
    - Reason, by the rule that matched: "Consumption {v}% is above 80%"; "Performance {v}% is below 20%"; "Consumption {c}% and Performance {p}% are both orange, and Risk {r}% is above 60%".
  - No data: "No check for the {period} to {end time}: {KPI} has no data." Never "Open".
  - Beside it, when Performance over the last hour is orange or red: a chip "Contention now" in the band colour of its value (orange or red), with the value and its time.
  - **How the check decides, as a diagram** (l2.cluster_check_diagram, D-121), under the verdict chip, which opens and closes it (open when the cluster is closed). One line first: "{Reason}. Based on the {period} to {end time}. The worst {n}% of samples are left out." (no reason when open).
    - Three paths into one outcome, as vCommunity's capacity model draws them: Consumption; Performance; "Both orange?" then Risk. The outcome is a circle: Open or Closed.
    - Each KPI node holds the check's value, its closure level ("closes above 80%") and the distance to it, in whole points from the value as shown: "✓ 29 points away" or "✕ above by 2 points". A node past its level is red, and its arrow to the outcome is red.
    - "Both orange?" holds its two tests with their values ("Consumption 51% above 60% ✕"). When both pass it turns orange and Risk is checked; else Risk is greyed and reads "not checked". Risk alone never closes a cluster.
    - One Risk level for every cluster: orange (above 60%), as vCommunity. No production and non-production split.
    - Not in the diagram: the last hour. "Contention now" stays the chip beside the verdict.
    - The values and levels are the published ones (l2.cluster_check); the page compares them to draw the path and never decides.
    - Phone width: the nodes stack, no arrows, the outcome is a full-width bar.
  - The tab's status is the worse of the check and the last hour.
- **Three charts, one per KPI** (l2.cluster_kpi_series): Cluster Consumption, Cluster Performance, Cluster Risk, in that order, one above the other, one time axis.
  - 0 to 100%. Display bands as background. The two closure levels as dashed lines, labelled "Closes above 80%" and "Orange for closure above 60%" (Performance: below 20% and below 40%).
  - Points as on the Performance tab: 5 minutes for 1 hour and 24 hours, 1 hour for 7 days, 4 hours for 30 days, 1 day for 1 year. A point holds the worst value inside it.
  - Beside each chart: **Now**, **Worst** (with its time), the **percentile figure** (5th percentile for Cluster Performance, 95th for Consumption and Risk; l2.statistics, D-131), as band figures (D-100). The first label (Now) sits level with the top of the chart, and the figures are indented by 2 characters from the title (D-110). The check's value is not repeated here: on the 24-hour window it equals the 95th percentile. Never an average. Percentages show whole numbers (D-101, D-116): KPIs, the parts of Consumption, and the Details parts whose band ends are whole; a part with a fractional band end keeps its decimals. The chart fills the height of its card.
  - **Agent E2 mark** at the right of each KPI's name: "Ask Agent E2 about {KPI}". PCM sends the KPI's points, Now, Worst, the percentile figure, the check's value and its closure levels, the verdict and its reason (D-097).
- **Check strip** under the three charts (l2.cluster_check): one cell per check period in the window, closed (labelled) or open, aligned with the time axis; a cell with no check is grey "No data".
  - Fewer than 7 check periods in the window (1 hour, 24 hours): words instead of the strip: the latest check and the one before it.
- **What consumption is made of** (l2.consumption_parts): one chart per part, each in % of usable capacity, with Now, Worst, the percentile figure: CPU Thread Utilization, Memory Consumed, Memory Ballooned, Memory Zip Swap, and, where the hosts have a tier, DRAM Consumed and Memory Tiering Consumption (NVMe in use ÷ usable DRAM).
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
reads: [l2.closed_count, l2.consumption_spread, l2.near_closure, l2.capacity_clusters_at, l2.cluster_check, l2.contention_now, noc.cluster_performance]
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
- **Not on this tab:** the spread of Cluster Performance and Cluster Risk (they are on the Performance tab); any total, sum or average of consumption across clusters; any forecast, run-out date, decision date, Capacity Remaining, Time Remaining or VM Remaining (D-100 keeps these to one VM, host or cluster).
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
  - Every chip on the Capacity tab has a finding row under it, and every capacity finding has its chip. Outside the 24-hour window, a closed cluster's finding is the daily one: a line links to it, never a repeat. "Nothing needs you under this object" never shows beside a capacity chip.
- **Explained by the calendar:** the entry is named, and the finding sorts last.
- **24-hour window:** the daily check's findings. **7-day window:** what a day cannot show, never a repeat of a daily finding.
- **Alerts that slipped through:** alerts no finding predicted, each with "What would have caught it" and a link to Rules.
- **Agent E2 mark** on every row: "Ask Agent E2 about this finding". It opens the panel with the finding as context; PCM sends the finding, its evidence and the calendar entry that explains it, if any (D-097).
- **States:** normal; empty ("Nothing needs you under this object."); loading; error.
