# L2 workspace (Platform)

Status: draft for the author's review. Rewritten around the three L2 activities (D-083 to D-090). Sections 3.1 to 3.17 of the first version are replaced; section 12 lists where each went.

Path: `privatecloud.acme.com/l2` (D-028).

## 1. The role

- SP5 calls this role **Platform**. It is the specialist behind L1.
- **What it does** (SP5 People):
  - Focuses on insight, not alerts. Looks at the big picture to stop alerts from happening.
  - Owns risk: configuration risk, and short-term capacity risk.
  - Advanced troubleshooting, often with logs.
  - Writes the knowledge base and the SOPs, and automates the SOPs.
  - After each problem it solves, updates the troubleshooting guide so L1 can handle the case next time.
  - Designs and maintains dashboards and alerts. It sets the thresholds L1 works with.
  - May specialize: storage, network.
- **Three activities** (SP5 Day 2, D-083): **Monitor**, **Troubleshoot**, **Improve**.

| | Monitor | Troubleshoot |
|---|---|---|
| Question | What is the problem? | Why does it happen? |
| Direction | Top down: the whole estate first | Bottom up: one symptom, then its causes |
| Nature | Proactive, on a cadence | Started by a known problem |
| Metric | One KPI per object, worst first | Many metrics, layer by layer |
| Logs | Rarely needed | Almost always needed |
| Data | Massive: every object, compared | Deep: the objects in one chain, over weeks |
| Ends in | A problem (→ Troubleshoot) or an opportunity (→ Improve) | A root cause, a corrective action and a detection |

  - **Improve** acts on what monitoring found that is not broken: risk (configuration, short-term capacity) and efficiency (reclaim, rebalance, standardize, update).
- **Cadence is a time window, not an activity** (D-083).
  - PCM still runs the daily check twice a day (D-039) and the weekly check on Sunday (D-042).
  - Their results are what Monitor shows for the 24-hour and 7-day windows. There is no page per cadence.
- **Scope** (D-034, D-038, D-085): infrastructure only.
  - In: server, storage as ESXi sees it, network, Windows, Linux.
  - Out: applications, business transactions, compliance (until after 1.0, D-022), cost, price and value (FinOps, D-027).

**Why this role is the centre of PCM**
- L1 runs what L2 writes: SOPs, thresholds, actions.
- The Executive reads what L2 keeps healthy.
- If the L2 workspace is weak, every other workspace runs on stale rules.

## 2. What L2 is measured by

Everything in this workspace serves these outcomes. Each outcome is a number PCM can show.

| Outcome | Measure | Why it is the right measure |
|---|---|---|
| Fewer alerts | Alert count and intensity, trend over months | SP5: well-run operations have few alerts. Insight replaces most yellow alerts. |
| Fewer repeats of the same problem | Repeat cases per problem type | Each solved problem should become a detection and an SOP. A repeat means the loop did not close. |
| Problems found before customers notice | Share of troubleshooting cases started by a monitoring finding, against those started by a complaint or an escalation | The case's trigger says who knew first (5.1). This is the prevention window. |
| Second time is fast | Time to diagnose a known problem | SP5: the first incident is forgivable. The second is known within minutes. |

- What L2 is **not** measured by: tickets closed. SP5 aims to remove tickets, not to process them faster.

## 3. The frame: four dimensions (D-086)

A page is where four dimensions meet. The navigation shows each dimension in its own place, so they never mix in one menu. The first version mixed them: Today, Weekly and Monthly (time), Escalations (activity), Configuration and Inventory (pillar) in one row.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ L2 Platform   [Monitor] [Troubleshoot] [Improve]            Rules  Calendar│  ← activity
├───────────────┬──────────────────────────────────────────────────────────┤
│ View: Compute▾│ FR-S-02 · Frankfurt › VCF fr-01 › wld-fr-prod      [24H▾] │  ← object, time
│ ▸ Asia Pacific│ Summary Availability Performance Capacity Security Config │  ← pillar
│ ▾ Europe      │          Inventory                                         │
│   ▾ Frankfurt │                                                            │
│     ▾ fr-01   │  Summary of this object                                    │
│       FR-S-02 │  Children, worst first                                     │
│       FR-G-01 │  Detail of the selected child                              │
│   ▸ London    │                                                            │
│ ▸ Americas    │                                                            │
│ [search]      │                                                            │
└───────────────┴──────────────────────────────────────────────────────────┘
```

### 3.1 Activity: the top bar

- **What:** Monitor, Troubleshoot, Improve. Rules and Calendar sit apart, at the right, as utilities (section 7).
- **Why:**
  - L2 switches activity many times a day. The activity is the first thing a user needs to know: "am I looking for problems, solving one, or improving?"
  - VCF Operations' top bar (Operate, Manage, Protect, Build) groups product functions. "Manage" is too broad to tell a user what to do there.
  - The three words are SP5's own Day 2 verbs. Each names one job.

### 3.2 Object: the inventory tree is the menu

- **What:** the left pane is the inventory tree. Selecting a node scopes every view to it. The root is the whole estate.
  - Switching activity keeps the selected object. Selecting another object keeps the activity. Neither nests inside the other.
- **Why:**
  - Inventory has two jobs. It is a pillar L2 manages (counts, distribution, churn), and it is how anyone moves around the estate. vCenter and VCF Operations both work this way; users already know it.
  - An object scoped once, then read through every activity, keeps context. Changing tools and re-finding the object loses it.

**Five views** (D-087). Each is a hierarchy operations uses. vCenter's datacenters and folders are admin constructs and are left out; the workload domain is VCF's unit and stays.

| View | Path | Why |
|---|---|---|
| **Compute** (default) | Estate → Region → Location → VCF instance → Workload domain → Cluster → ESXi host → VM → Guest OS | The cluster is the unit of performance and capacity. Regions already scope the checks (D-039, D-042) and the NOC (D-068). |
| **Storage** | Estate → Location → vSAN cluster or datastore (vSAN, VMFS, NFS) → VM → virtual disk | Latency is judged per virtual disk. A datastore shows every VM on it, from any cluster. The array itself is out (5.6). |
| **Network** | Estate → Location → distributed switch or NSX segment → port group → VM → vNIC | Drops are judged per vNIC. Flow dependencies are visible here: an NSX Edge on another cluster serves this VM. |
| **Class of service** | Gold, Silver, Bronze → Location → Cluster → VM | Targets are set per class. Gold first in a large estate. |
| **Management** | Location → VCF instance → appliances (vCenter, NSX Manager, NSX Edge, SDDC Manager, VCF Operations, VCF Automation) | SP5's second side of VCF: the software that runs the IaaS. A grey screen (story N-2) belongs here. |

- **The VM and the Guest OS are two nodes** (D-038). The Guest OS is the VM's child, never merged into it.
- **An appliance appears twice:** as a VM in Compute (in the management domain) and as an appliance in Management. It is one object; both nodes open the same record.
- **Each node shows** its status for the current pillar and time window, and its count of open cases.
- **Children are sorted by the activity:**
  - Monitor: worst first on the current pillar.
  - Troubleshoot: objects with open cases first.
  - Improve: largest opportunity first.
- **Scale:** the tree expands down to the cluster. Below that, children show as a list with search. VCF Operations does the same once a section has more than 10 objects.
- **Search** covers all five views.

**A tree shows structure; a slice shows attributes.**
- Structure: where an object sits. The tree.
- Attributes: what objects share. Host model, BIOS and firmware, ESXi build, VMware Tools version, virtual hardware version, Guest OS type, environment. These are not trees. Every list has **Group by** on them (4.2).

### 3.3 Pillar: the tabs

- **What:** in Monitor and Improve, the tabs are the L2 pillars. The first tab, **Summary**, shows one line per pillar for the selected object. There is never one combined score.

| Pillar | Monitor | Troubleshoot | Improve |
|---|---|---|---|
| Availability | Yes | Yes | Partial: restore and HA tests |
| Performance | Yes | Yes | Yes |
| Capacity (short term only; long term is the Capacity workspace, D-014) | Yes | No (SP5) | Yes: reclaim, rebalance |
| Security (present: platform hygiene, D-049) | Yes | A breach goes to the security team (D-044) | No |
| Configuration | Drift and variance against the standard | Evidence: the cause is often here | Correct, update, simplify, optimize |
| Inventory | Count, distribution, churn, unexplained changes | Evidence: what changed over the weeks | Stock-take, orphaned objects |

- **Troubleshoot has no pillar tabs.** One case crosses pillars: a performance symptom, a configuration cause, an inventory change three weeks earlier. The pillars appear inside the case as kinds of evidence.
- **Configuration and inventory are not SP5 pillars** but L2 manages them. SP5: configuration is "both the problem and solution to all the above pillars".
- **Left out:** compliance (after 1.0, D-022); cost, price and value (FinOps, D-027, D-056).
- **Why:**
  - SP5's own table (Day 2 monitoring, troubleshooting and optimizing against the pillars) is not uniform. Capacity and compliance are not troubleshot. Pages follow that table instead of offering every tab everywhere.
  - VCF Operations' object tabs mix pillars (Capacity) with types of data (Metrics, Logs, Events). A user must know which tool answers a question. PCM's tabs are questions; the data comes to them.

### 3.4 Time: one picker per page

- **What:** one time window per page, in the object header: 1 hour, 24 hours, 7 days, 30 days, 1 year, custom.
  - It stays when the object or the tab changes.
  - Inside a troubleshooting case, the window is the case's own and is fixed.
- **Defaults follow the activity:**

| Activity | Default window | Why |
|---|---|---|
| Monitor | 24 hours, from the latest daily check run | The daily check is the morning's starting point (SP5). 7 days shows the weekly check; 1 year shows baselines. |
| Troubleshoot | The case window: from "fine until" to now, plus the weeks before for changes | Causes can build up over weeks. Metrics need the complaint window; changes need the weeks before it. |
| Improve | 30 days | Opportunities and risk move slowly. |

- **Performance reads the 20-second peak** of each 5-minute interval, not the 5-minute average. A spike of a few seconds disappears in 300 seconds of average.
- **Over a window, an object's score is its 95th percentile:** not the average (it hides problems), not the worst (too noisy). This is the rule of the author's sample dashboard (`sources/Cluster Performance v2.html`).
- **Why:** in vCenter and VCF Operations, time is set per chart or per widget. Moving between them resets it. One window per page keeps every number on the page about the same period.

### 3.5 Pages are addressed by the four dimensions

- Every page is a URL of activity, view, object, pillar and window, so any state can be shared or reopened. Section 10 lists the routes.

## 4. Monitor

The question: **what is wrong, at risk or wasteful, across the whole estate?** Monitoring is top down and works on massive data. One object over a threshold is the tip of the iceberg; Monitor shows the iceberg.

### 4.1 Summary, then children worst first, then detail

- **What:** every node shows the same three parts. This follows the author's sample dashboards.
  - **Summary:** the node's trend for the pillar, and the count of children outside the green zone over time.
  - **Children, worst first:** each child's score (95th percentile over the window), with its red and orange alerts.
  - **Detail:** the selected child's trend and its own children. Going down one level is going one level deeper into vSphere.
- **At the root this is the estate:** 1,200 hosts, all clusters, all VMs of the synthetic ACME estate.
- **Why:**
  - SP5: "insight is top down; alert is bottom up". A list of alerts shows only what crossed a line.
  - Worst first at every level means L2 walks only the branches that matter. At 100,000 VMs, starting from a VM is a needle in a haystack.

### 4.2 The iceberg and the shared cause

- **The iceberg:** for each KPI, the number of objects just below the red line, and its trend. A rising count under the waterline warns before any alert fires.
- **Group by** (3.2) on any list. It answers SP5's insight question: "Is performance degrading? Is there a common pattern and cause?"
  - Example (story M-1, section 11): clusters in the middle of a hardware refresh show more remote memory. Grouped by host model, the pattern is on the older hosts only.
- **Why:** preventing a widespread problem needs insight from the whole data set. One object's chart cannot show that 40 clusters share a firmware version and a rising error count.

### 4.3 The KPI model

From SP5 Performance Management and the vCommunity pack (`VCF-vCommunity-Adapter`, `docs/concepts/kpi-scoring-models.md`):
- **Every KPI is 0 to 100% with the same four bands:** green 100 to 75, yellow 75 to 50, orange 50 to 25, red 25 to 0. Performance is higher-is-better. Risk is higher-is-worse, so its bands run the other way: green 0 to 25, red 75 to 100.
- **A KPI is a weighted average of its sub-metrics,** and a worse sub-metric weighs more (1 at 100, 16 at 0). One red sub-metric among green ones still shows.
- **VM KPI** includes the Guest OS, because the VM and its Guest OS are one logical entity for monitoring. The two stay separate objects for troubleshooting (5.6).
- **Cluster Performance** uses only the contention of its running VMs, never utilization: the worst VM and the 90th percentile of CPU Ready, Co-Stop, memory latency and disk latency, plus the worst host's bad packets. It is a consumer metric, rolled up to the provider.
- **Cluster Risk** is the leading indicator: how close the cluster is to contention, from its worst host (utilization, imbalance, ballooning, overcommit, reservations, monster VMs).
- **vSAN KPI** uses the disk latency of every VM on the vSAN datastore, from any cluster.
- **NSX KPI** is separate, because NSX has a many-to-many relation to clusters. NSX, vSAN and top-of-rack switch metrics come from vCommunity.
- **The internal threshold is stricter than the SLA.** SP5: proactive work needs a line that is crossed before the contract is.
- **Leading indicators** (SP5's "kitchen" metrics) sit under each KPI: per vCPU, per virtual disk, per vNIC. The weekly check reads them (D-042).
- **Kubernetes** is a logical entity with its own view. Not in 1.0.

### 4.3.1 The Performance tab above the cluster (D-091)

- **Two perspectives, consumer first:** VM, then Cluster. Cluster Performance is made of VM contention, so the VM section explains the cluster lines underneath.
- **One class of service filter** scopes both sections. Gold by default. Silver, Bronze and All (the vSphere World view) are one click away.
- **VM section:**
  - **No VM chart.** A count-over-time chart does not scale to a large estate. The table below carries the detail.
  - **In words:** "412 different VMs were hit; never more than 37 at once."
  - **Worst VMs:** the VM, its worst VM Performance, the time, its cluster and location, and how many other VMs were hit in the same 5 minutes. The same time on many rows points to something common; the cluster lines should show it. Different times point to one cluster or one VM.
  - **Just above the line:** the iceberg (4.2).
- **Cluster section:**
  - **Actual slowness:** one chart, 0 to 100%, two lines. Worst Cluster Performance (solid) and the 10th percentile across clusters (dashed), as vCommunity's Worst 10 Percent. Each line takes the band color of its value.
    - The worst line is good: no issue.
    - The worst line is bad and the 10th percentile is good: a narrow problem, a few clusters or one.
    - Both are bad: a wide problem.
  - **Potential slowness:** the same chart for Cluster Risk. The highest (solid) and the 90th percentile (dashed).
  - **Clusters at a time:** a click on either chart, or on the VM chart, picks a time. The table lists every cluster in scope at that time, worst first: Performance, Risk, VMs hit at that time, and different VMs hit over the window. Before any click, the time is the worst point of the window.
  - A click on a cluster opens it in the tree: its hosts, then vSAN, NSX and the switches underneath.
- **What, not why:** the tab says what was hit, when, where and how wide. Causes, including a VM that slows itself (a limit, too many vCPUs), are the case's (D-084).
- **At the cluster and below,** the tab stays as 4.1: the summary, the children worst first, the detail.

### 4.3.2 The Performance tab on a VM (D-092)

- **Two layers, one over the other.** The Guest OS runs on the Virtual Motherboard (the VM's virtual hardware), so the Guest OS comes first and the Virtual Motherboard under it. Never side by side.
- **One chart per metric,** over the window. Beside it, three named figures: Now, Worst (with its time) and 95th percentile. Never an average: a VM is felt at its peak.
- **Group by, "Just above the line", "Children outside green" and Inventory are not on a VM.** They describe a group of objects.
- **Names and units:** Title Case, capitals for abbreviations, the unit after the number, never inside the name ("CPU Ready 2.5%", "Disk Latency 5.6 ms").

### 4.4 What each window adds

| Window | Shows | Source |
|---|---|---|
| 24 hours | The latest daily check: findings worst first, the day ahead using the last week's pattern, business context | D-039 |
| 7 days | What a day cannot show: slow drift (5 of 6 nights the same way, 10% in total), hidden in the average (one vCPU or one virtual disk at its line while the VM is green), configuration drift | D-042 |
| 1 year | Baselines per KPI, for consumers and providers; quarterly and yearly patterns | SP5 monthly: "overall performance analysis and baselining" |

- **No finding is repeated across windows.** The 7-day window shows only what the 24-hour window cannot.

### 4.5 Where a finding goes

- **A problem** (present health: down, slow, a security event) → **"Troubleshoot this"** opens a case with the finding as its trigger (5.1), its object and its window.
- **A risk or an opportunity** (configuration drift, capacity trend, waste) → **Improve**, on the same object.
- **Explained by the calendar:** a finding that business context explains shows the calendar entry and drops to the bottom (7.2).
- **Why:** SP5: monitoring ends either in a problem to troubleshoot or in an opportunity to improve. A finding that goes nowhere is noise.

### 4.6 Alerts that slipped through

- **What:** alerts since the previous run that no finding predicted. Each links to the rule that would have caught it (7.1).
- **Why:** SP5's improvement loop. Over months, fewer alerts slip through.

### 4.7 The inventory and configuration tabs

- **Inventory:** counts per node and change since the start of the window; distribution across children (SP5: keep it balanced); every change matched to what explains it (D-081). Explained changes are counted; unexplained ones are listed, production and Gold first.
- **Configuration:** drift against the standard and variance across peers (SP5: keep variance minimal). Example: one host in a cluster with a different NTP server.

## 5. Troubleshoot

The question: **why is it down or slow?** Troubleshooting is bottom up, deep and rarely simple.

### 5.1 Escalation is one trigger; troubleshooting is the activity (D-084)

- **What:** every troubleshooting effort is a **case**. A case has one of three triggers:

| Trigger | Who starts it | What it carries |
|---|---|---|
| **Complaint** | L2 logs it in PCM (5.2) | Who complained, which VM, the symptom, since when, what the requester already checked |
| **L1 escalation** | L1, after its SOP (D-040) | The SOP steps and results, villains and victims, what L1 already did (5.3) |
| **Monitoring finding** | L2, from Monitor (4.5) | The finding, its object, its window, its evidence |

- **Why:**
  - The activity is the question "why", whoever asked it. An escalation is a handover with entry criteria, not a way of working.
  - SP5: troubleshooting is best done "proactively, quietly, with no one rushing you". A case from a finding is that kind.
  - One case model gives one place for every open problem, and the trigger mix is an L2 measure (section 2).
- **The case list:** open cases first, then closed, scoped to the selected object and its children. Each row shows the trigger, the object, the symptom, the age and the current link of the chain.

### 5.2 Logging a complaint

- **What:** "Log complaint" in Troubleshoot. Fields:
  - the VM (or Guest OS) named in the complaint; a complaint about an application is logged against its VMs;
  - who complained, and through whom (for example the owner's manager);
  - the symptom: slow or down;
  - since when, and "fine until";
  - what the requester says they already checked.
- **Why:**
  - SP5 "A day in the life of a cloud admin": the application team arrives having "verified" the CPU, the disk latency, the patches and the reboots, and blames the shared platform. Recording what they checked is the start of the evidence, not the end.
  - A complaint does not start with an alert: L1 did not see it. Without a form, it lives in chat and email, and the second time is not faster.

### 5.3 An escalation arrives complete

- **What:** an L1 escalation arrives with its evidence already gathered (D-040). L2 accepts it, or rejects it with a reason. Rejection should be rare, because PCM fills the evidence.
- **Why:** SP5 Exit and Entry criteria: L1's exit criteria are L2's entry criteria. A rejection for missing evidence points to a gap in the SOP and feeds back into authoring (7.1).

### 5.4 The chain of causes

- **What:** the case page builds the chain of causes, one link at a time.
  - Problem A is caused by B, which is caused by C, which is caused by D.
  - It is a graph, not a line. Several causes can meet: a leftover snapshot (main cause) and a VM split across two NUMA nodes (contributing cause) both slow the same database.
  - Each link has a state: **proposed**, **confirmed** with its evidence, or **ruled out** with its evidence. Ruled-out links stay visible.
  - **Red herrings** are ruled-out links. Example: receive drops on another VM; "add vCPUs and a host" proposed by a manager.
  - Each node of the chain is an inventory object. Clicking it moves the tree to that object, with the case window held.
- **Why:**
  - SP5: "there is a good chance that the root cause is different than the symptoms. It may happen on a different object altogether."
  - The first version investigated one object at one point in time and ended at the first failed step. Real problems have several layers and several causes.
  - Keeping ruled-out links stops two engineers from checking the same wrong idea, and shows the requester what was proven, not only what was found.

### 5.5 The SP5 order at every node, with Agent E2 flows (D-089)

- **What:** at each node, the checks run in the SP5 order.
  - **Down:** log → saturation → configuration → known bug.
  - **Slow:** contention → consumption → configuration → known bug → log.
  - PCM pre-runs the steps it has data for and shows which pass. L2 starts at the first failed step.
- **Agent E2's flows decide the next node.**
  - Each flow is an expert's order of checks (Agent E2 `REPOSITORY-MAP.md`, Flows). A complaint about a slow VM starts at `vm-slow`. A step of one flow opens another flow on another object: the CPU flow, the storage flow, the cluster flow.
  - This is how a chain grows: a failed step on the VM proposes a link to its datastore, and the storage flow runs there.
  - Agent E2 **proposes** a link and its evidence. L2 **confirms** or **rules it out**. Agent E2 never closes a case (section 8).
- **Why:**
  - Experts under pressure skip steps. The classic skip is "CPU is at 100%" when there is no contention: that is a busy VM, not a slow one.
  - A fixed order makes two engineers reach the same conclusion.
  - The flows already exist and are tested in Agent E2's benchmark. PCM supplies the data; Agent E2 supplies the order.

### 5.6 Layers and realms

- **What:** the case shows the layers in scope, each with its own "on my court" verdict:
  1. Guest OS (Windows, Linux): run queue, context switches, paging, disk queue.
  2. VM: CPU Ready, Co-stop, Overlap, Other Wait; memory latency, swapped, ballooned; disk latency per virtual disk; drops per vNIC; vMotion stun time.
  3. ESXi host, and the physical server: ESXi Performance; hardware, firmware and driver versions.
  4. Cluster: Cluster Performance; imbalance across hosts.
  5. Storage as ESXi sees it: adapter, path, device and kernel latency; vSAN; datastore.
  6. Network: vNIC, port group, distributed switch, NSX, physical NIC.
- **The chain starts at the Guest OS** (step 1 of Agent E2's `vm-slow` flow): quantify the slowness where the requester sees it, then read the VM.
- **Handing out of scope:** when the evidence points outside the infrastructure, the case says so and hands the evidence over.
  - The Guest OS waits and the VM does not → the Windows or Linux team.
  - The storage device latency is high and the ESXi layers are clean → the storage team, for the array.
  - Every layer is clean → the application owner. PCM says what was checked and that vSphere has no counter for what is left.
- **Why:**
  - SP5: performance troubleshooting is an exercise in elimination, layer by layer. Each layer needs one verdict.
  - With both sides' evidence shown, the argument is about data, not reputation: the conversation takes minutes, not days of ping-pong.
  - Scope (D-085): no application troubleshooting, no business transaction correlation. Applications enter a case only as the words of the complaint.

### 5.7 One timeline across the chain

- **What:** one timeline for every object in the chain, over the case window and the weeks before it:
  - metric anomalies at the 20-second peak;
  - events: vMotion, snapshot taken or left, host maintenance, HA restart;
  - log messages, including on objects that never raised an alarm;
  - changes, matched to what explains them (D-081): the PCM action record, a change window, a VCF Automation request, DRS;
  - business calendar entries;
  - alerts.
- **Why:**
  - SP5's story: "it was not slow yesterday", but VMs were added for months and soft errors were investigated for weeks. The cause is often several changes over weeks that meet on one day.
  - In vCenter and VCF Operations, metrics, events, logs and changes are separate tabs or tools. Moving between them loses the object and the time. The timeline puts them on one axis.

### 5.8 Breadth: who else

- **What:** for any symptom in the case, "Who else?" runs the same test across the estate: other VMs on the same cluster, datastore, host model, ESXi build or change.
- **Why:**
  - Agent E2's `vm-slow` flow, step 3: several slow VMs point to a shared cause; tuning one VM would not help.
  - This is where Troubleshoot uses Monitor's data. One complaint can reveal a pattern that becomes a monitoring finding on its own.

### 5.9 Closing a case

- **What:** a case closes only with:
  1. the root cause, and any contributing causes, as confirmed links of the chain;
  2. a corrective action that prevents a repeat;
  3. a decision on detection: a new check rule, a new alert, a new or updated SOP, or none with a reason.
- **Log-based detection is validated first:** PCM counts the proposed message on healthy objects over the last 5 working days. A message seen 1,000 times on healthy hosts is noise (SP5's VDI example).
- **Why:**
  - SP5: an RCA is done when the alert that detects a recurrence is set up, not when the cause is named.
  - The detection feeds Monitor (a check rule) and L1 (an SOP), so the second time is fast.

### 5.10 A suspected breach goes to the security team (D-044)

- **What:** when a finding points to a breach, L2 secures the evidence and hands it over: the logs, the events, and the configuration at that point in time. PCM does not investigate the breach.
- **Why:** SP5: a breach is a forensic investigation, not troubleshooting. An L2 engineer who "just checks" can destroy the trail.

## 6. Improve

The question: **what should be better, though nothing is broken?** SP5 Optimize: "you may discover nothing to fix, but you discover the opportunity to improve."

### 6.1 What lands here

- **Risk:** configuration drift and variance; short-term capacity (a cluster that will not serve the expected load this week).
- **Efficiency:** reclaim powered-off, idle and oversized VMs; rebalance between clusters; standardize; update versions.
- **Lessons:** corrective actions from closed cases that are larger than one fix.
- **Framed in capacity, never in money.** Reclaim shows what it frees and how far it moves the next purchase decision (Capacity workspace). Money is FinOps (D-027).
- Opportunities roll up the tree: each node shows the count and size of what lies below it.

### 6.2 Configuration by urgency, against a standard

- **What:** configuration opportunities are ordered by the SP5 time dimension:
  1. **Correct it:** wrong, insecure, against the standard.
  2. **Update it:** old versions, oldest first, out of support first.
  3. **Simplify it:** variance and complexity.
  4. **Optimize it:** capacity.

  Every item offers two choices: fix the setting, or fix the standard.
- **Why:** grouping thousands of settings by product feature hides urgency. Drift means nothing without a documented standard, and sometimes the standard is the one out of date.

### 6.3 Policy as code decides what runs automatically (D-079)

- **What:** proposed fixes carry an action type. Each action type has a policy: its tier (automatic, approval, never), its guardrails, its version and its owner.
  - A fix whose action type is automatic, and that passes every guardrail, runs. A fix that breaks a guardrail becomes a proposal for L2, with the guardrail named.
  - The approval, rejection and rollback record per action type is evidence, never a gate.
  - Policies are edited in Rules (7.1): "Propose a policy change", replay, publish.
- **Why:** automatic approval is a contradiction. Guardrails make automation safe; a count of past clicks does not.

### 6.4 The decision register (D-043)

- **What:** a decision is an improvement with an owner and a due date. The register lists them: overdue, open, done. Recording one needs what, an owner and a due date.
- **The monthly review is Improve and Monitor on one screen in the room:** the decision register first, then Monitor at the estate root with the 1-year window. PCM prepares it; there is no separate monthly page.
- **Why:** a meeting that starts with new topics never checks the old ones. Decisions without owners come back unchanged next month.

## 7. Utilities: Rules and Calendar

Neither is an activity. Each is opened from the top bar, and also from where it applies.

### 7.1 Rules: L2 authors what L1 and PCM run

- **What:** SOPs (in `/docs`, D-082), check rules, thresholds, alerts, the SOP buttons L1 may press, and action policies.
  - A case closed with a detection (5.9) opens the matching rule as a draft. Agent E2 drafts an SOP from the closed case; L2 reviews and publishes it.
  - Every published change is versioned.
  - **Any threshold change is replayed against the last 30 days first.** PCM shows how many alerts the new value would have raised.
- **Why:**
  - SP5 People: L2 develops and automates the SOPs and sets the thresholds L1 uses.
  - Alert storms come from thresholds set conservatively and never measured. If a threshold cannot be shown to be rare, it should not ship.

### 7.2 Calendar: business context is an input, not a memory

- **What:** L2 records the expected events: month-end and quarter-end close, payday, end-of-day batch, a planned migration, a DR test, a maintenance window. Monitor reads them when it judges what is abnormal; a case shows them on its timeline.
- **Why:**
  - SP5: an insight is useless to someone who does not know the environment. Low IOPS on the day before a holiday sale means sales are not happening.
  - Today this context lives in one senior engineer's head. That fails SP5's acid test: the lead takes a long holiday and nobody calls them.

## 8. Agent E2: explains, proposes and drafts, never decides

- **Agent E2 may:**
  - explain a finding with the knowledge base and today's business context;
  - run its flows to propose the next link of a chain, with evidence (5.5);
  - draft the RCA and the SOP;
  - answer "why" questions with sources.
- **Agent E2 may not:**
  - confirm or rule out a link;
  - set a severity;
  - approve an action;
  - change an action policy;
  - close a case.
- **Accountability (D-050):** each Agent E2 task records Agent E2's ID and the human who ordered it. For automatic runs, the second field is the policy owner and the policy version (D-079).
- **Why:** a confident wrong answer at L2 level spreads: it becomes an SOP that L1 runs at 03:00. Grounding in the knowledge base plus a human confirmation keeps the knowledge correct.

## 9. Specialty lenses are views

- **What:** storage and network specialists use the Storage and Network views of the same workspace (3.2), not separate workspaces.
- **Why:**
  - With vSAN and NSX, storage and network are software in the same stack. One case often crosses all three.
  - Separate workspaces bring back the "ping-pong between teams" SP5 calls the manual stage of maturity.
  - One workspace means one evidence set, one timeline, one RCA.

## 10. Routes

| Path | What |
|---|---|
| `/l2` | Redirects to `/l2/monitor`, estate root, Summary, 24 hours |
| `/l2/monitor/{view}/{object}/{pillar}?window=` | Monitor on one object and pillar |
| `/l2/troubleshoot/{view}/{object}` | Cases on an object and its children |
| `/l2/troubleshoot/new` | Log complaint |
| `/l2/troubleshoot/case/{case}` | One case: chain, timeline, layers, close |
| `/l2/improve/{view}/{object}/{pillar}?window=` | Opportunities on one object and pillar, and the decision register |
| `/l2/rules` | SOPs, check rules, thresholds, alerts, L1 actions, action policies |
| `/l2/calendar` | Business calendar |

- `{view}` is one of `compute`, `storage`, `network`, `class`, `management`. `{object}` is the object's ID; `estate` is the root.
- Landing on Monitor follows SP5: the daily check first thing in the morning, "before you jump into the first problem".

## 11. Demo stories (D-090)

The troubleshooting stories come from Agent E2's benchmark (`benchmark/questions/`). Each has several layers, events spread over time and red herrings. The specification renames them into the ACME estate.

| Story | Trigger | Agent E2 source | What it shows |
|---|---|---|---|
| **T-1** | Complaint, logged by L2 | `L4-037` ERP slow after the change window | A chain over several layers. A snapshot the backup left on Sunday doubles the datastore reads: disk latency, Co-stop, Other Wait and System time rise. Contributing: the VM spans two NUMA nodes. Ruled out: receive drops on another VM; "add 8 vCPUs and a ninth host". |
| **T-2** | L1 escalation | `L4-074` Web applications slow on Monday | Every web VM shows Ready on every host while hosts run at 30-48%. The pool runs flat at 40 GHz: a weekend change script put the CPU limit on the wrong pool. Ruled out: "add two hosts". |
| **M-1** | Monitoring finding | `L4-049` vNUMA after a move to an older host | Monitor, grouped by host model, shows remote memory rising on clusters mid-refresh. The case: DRS moved a database VM to an older host; its virtual NUMA layout was fixed at power-on on a newer one. The estate's two host generations (`spec/data/estate.yaml`) carry it. |
| **M-2** | Monitoring finding | `L4-045` Other Wait after the weekend backup | One symptom on two VMs, two causes: a real wait from a leftover snapshot, and an accounting issue of an older ESXi build on an idle VM. Not every high number is a problem. |

- Existing stories stay where they still fit: L-1 (an escalation) becomes a case; L-2 (Guest OS cause) becomes a short case that ends in a hand-over; L-3, L-6, L-8 and L-9 feed Monitor and Improve.

## 12. What this replaces

| First version | Now |
|---|---|
| 3.1 Landing page is the check result | Section 10: landing on Monitor, 24 hours |
| 3.2 Three verdicts, never one score | 3.3: Summary tab, one line per pillar; 4.5: problem → Troubleshoot, risk and efficiency → Improve |
| 3.3 Top down, worst first; on Performance, consumer before provider (D-091) | 4.1, 4.3, 4.3.1 |
| 3.4 One fixed order of checks | 5.5, now at every node of a chain |
| 3.5 VM and Guest OS side by side | 5.6 |
| 3.6 Business context | 7.2 |
| 3.7 Policy as code | 6.3, 7.1 |
| 3.8 Escalations arrive complete | 5.1, 5.3, 5.9 |
| 3.9 L2 authors what L1 runs | 7.1 |
| 3.10 Configuration by urgency | 6.2 |
| 3.11 Specialty lenses | Section 9: views |
| 3.12 Time windows follow the job | 3.4 |
| 3.13 Logs beside metrics | 5.7: one timeline |
| 3.14 Monthly review | 6.4 |
| 3.15 Breach handover | 5.10 |
| 3.16 Agent E2 | Section 8 |
| 3.17 Weekly, monthly, inventory build | 4.4, 4.7, 6.4 |
| Pages: Today, Weekly, Monthly, Escalations, Investigate, Configuration, Inventory, Calendar, Thresholds | Section 10 |

## 13. Open questions for the author

1. **Who owns PCM's own configuration** (class-of-service definitions, action tiers)?
   - Proposal: L2 proposes changes; the Operations Manager approves them after 1.0. Until then, L2 owns them (D-045).
