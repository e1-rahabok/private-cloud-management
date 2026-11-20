# Capacity workspace

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

Path: `privatecloud.acme.com/capacity` (D-028).

## 1. The role

- **SP5 People: Capacity**
  - Plans the supply side with the Architecture role, and the demand side with the business and sales.
  - Works with IT Finance on purchasing.
  - **Does not take part in day-to-day capacity.** A host in maintenance mode is an operations problem, not a capacity planning one.
- **Cadence:**
  - **Weekly (D-014):** reclamation, rightsizing, outlook.
  - **Twice a year:** procurement rounds, each after a decision on technology refresh.
  - **Yearly:** demand gathering from January to March, check points in June and December, adjustment in August. The hardware standard is set once a year.
- **Scope (D-014, D-019, D-023):**
  - what-if analysis
  - hardware refresh
  - **cost** as line items: what the company pays for hardware and software
  - sizing of migrations into VMware (OpenShift first)
- **Not in scope:**
  - price, which belongs to FinOps after 1.0 (D-027)
  - value, which belongs to the Executive workspace (D-019)
  - stopping provisioning on a cluster that cannot serve its current VMs: that is day-to-day work for L1 and L2 (D-040)

**Why this workspace matters**
- Capacity mistakes are the slowest to fix and the most expensive.
- Too little: a procurement cycle takes months, and the business waits.
- Too much: hardware and per-core licences paid for years and never used.
- Every other workspace only reads the result of capacity decisions. This one makes them.

## 2. What the Capacity team is measured by

| Outcome | Measure | Why it is the right measure |
|---|---|---|
| No shortage | Clusters that reached their decision date without a purchase in flight | The one failure the business sees. |
| No waste | Usable capacity unused for months, in money | Low use that stays low is waste, not health (SP5). It is shown in money because the CFO acts on money, not percentages. |
| Plan matches reality | Forecast error at each check point | A plan that misses by a wide margin must be reset early. Example: a project planned for a year reaches 70% use at 25% of its users. |
| Waste kept down | Reclaimed capacity per week, and waste trend | Waste grows back without a weekly rhythm (SP5 annual cadence). |

## 3. Design considerations

### 3.1 The cluster is the unit, never the data centre

- **What:** every number is per cluster, or per group of clusters that can take each other's workload. There is no data-centre-wide "capacity remaining" figure.
- **Why:**
  - HA, DRS and DPM work inside a cluster, so capacity does too.
  - SP5 example: cluster A is short of memory and disk, cluster B of CPU and disk, cluster C of CPU and memory. The average across them shows plenty of everything, and each cluster is nearly full.
  - A data-centre average is the most common way a capacity report lies.

### 3.2 Usable capacity is a chosen constant, shown with its parts

- **What:** each cluster shows how total capacity becomes usable capacity, step by step:
  - total
  - minus the HA host
  - minus the maintenance host
  - minus the hypervisor (in planning only)
  - minus the buffer

  Each step can be changed in what-if analysis.
- **Why:**
  - A stable 100% anchors both capacity and cost accounting. If usable capacity moved with load, every percentage would move too, and nobody could compare weeks.
  - **The HA host does not cover maintenance.** HA admission control leaves hosts in maintenance mode out of its count. A plan that uses the HA host as the maintenance host leaves VMs short when a host fails during a patch window.
    - Large estates patch every week (D-042), so this case is common, not rare.
    - PCM plans one host for HA and one for maintenance by default.
  - Showing each step stops the common double count: the hypervisor subtracted from supply *and* counted in measured utilization.

### 3.3 Two numbers, read together

- **What:** the cluster list plots each cluster on two axes: **Capacity Remaining** and **Time Remaining**.

  | Capacity remaining | Time remaining | Meaning | Colour |
  |---|---|---|---|
  | Low | High | Ideal: well used, slow growth | Green |
  | Low | Low | Buy now, or close the cluster | Red |
  | High | High, for months | Waste, unless the cluster is new or holds DR | Dark grey |

- **Why:**
  - High remaining capacity looks good on a traditional dashboard. Usually it is unused money.
  - SP5 colours it dark grey, not green. PCM does the same, so waste cannot pass as health.

### 3.4 Contention overrides the forecast

- **What:** each cluster also shows Cluster Performance (%) and Cluster Risk (%). If the cluster's VMs are waiting, it is marked full, whatever the forecast says.
- **Why:**
  - Both capacity numbers read utilization against usable capacity. Neither reads contention.
  - A cluster with 200 days remaining can still be full today because its VMs wait for CPU (SP5: contention is the override).
  - Capacity reads this signal. It does not own it: performance stays with L2 (L2 design, 3.3).

### 3.5 PCM keeps years of history, because the forecast needs it

- **What:**
  - Forecasts use PCM's own history (D-006), at least 13 months, so that quarter-end and year-end peaks are inside the data.
  - One-off peaks barely move the projection. Periodic peaks stay in it.
  - Without 3 months of data, PCM sizes on the 97th percentile instead of projecting.
- **Why:**
  - VCF Operations 9.1.1 forecasts from at most 90 days of data. That covers one quarter-end and no year-end.
  - A retailer's December or a bank's year-end close is outside its view. The forecast would be wrong exactly when it matters most.
  - This is one of the clearest reasons PCM needs its own database.

### 3.6 Demand nobody can see in the data is entered by hand

- **What:** a demand register holds what no forecast can contain:
  - committed projects;
  - migration waves into VMware (D-023), sized from the source platform;
  - DR demand, from Site Recovery Manager recovery plans, with each VM counted once even when it is in several plans;
  - new VMs that will grow to their full size over the coming months.

  Each entry has a cluster, a date, a size and an owner.
- **Why:**
  - SP5: the projection holds only the past. "The project starting next month" is not in it.
  - Most shortages in large estates do not come from organic growth. They come from a large project or a migration that the capacity planner heard about too late.
  - The register turns hearing about it into a recorded commitment with a name on it.

### 3.7 The output is a decision date, not a percentage

- **What:** per cluster and per resource, PCM shows:
  - the **run-out date**: when usable capacity is used up, including the demand register;
  - the **decision date**: run-out date minus procurement lead time.

  The cluster list sorts by decision date.
- **Why:**
  - "72% used" does not tell anyone what to do. "Order memory for cluster X by 14 March; delivery takes 4 months" does.
  - The Executive Dashboard already uses this idea for the CIO. The Capacity workspace is where the date is calculated and defended.

### 3.8 The plan follows the procurement rounds

- **What:** `/capacity/plan` answers one question: which clusters must be in the next procurement round, with what hardware, and at what cost?
- **Why:**
  - Supply is bought twice a year (SP5 cadence). A cluster that misses a round waits six months.
  - The team works toward a fixed deadline, not a continuous stream of alarms.
  - The plan shows **cost line items** (D-019): servers, memory, storage, VCF licences per core, support, and facilities where known.
    - IT Finance works from this list (SP5 People).
    - The total, not the lines, goes to the Executive workspace as value.

### 3.9 Hardware refresh is a continuous flow, combined with growth

- **What:**
  - PCM tracks the age, warranty end and depreciation end of every host.
  - Refresh is planned together with growth. Replacing old hosts with new ones often covers the growth by itself.
- **Why:**
  - At 1,200 hosts on 5-year depreciation, 240 hosts are replaced a year, about 20 a month (SP5). Refresh is part of every month, not a project.
  - New hardware gives about twice the capacity at the same cost (SP5). Planning growth and refresh separately buys hardware twice.
  - The useful what-if is "refresh X hosts with the new standard: does that cover next year's growth?" It is often cheaper than expanding.

### 3.10 What-if uses the SP5 planning model, not guesses

- **What:** each scenario changes one or more inputs and compares the result with today's plan. Inputs:
  - demand added (a project, a migration wave);
  - hosts removed (refresh, retirement);
  - a new host specification;
  - a class-of-service change;
  - a buffer change.

  The calculator returns six numbers per host: allocation, reservation and utilization, for CPU and memory. The first to reach 100% sets how many VMs fit, and shows which resource limits it.
- **Why:**
  - A what-if on one number (usually allocation) gives the wrong hardware.
  - SP5 example: sizing Bronze on allocation alone overbuys 381 GB of RAM per host, because Bronze fills on CPU utilization long before its 3:1 allocation.
  - **Host specification is derived, not chosen.** CPU sets how many VMs of a class fit; RAM is bought to match those VMs. RAM beyond that cannot be sold with vCPUs.
  - **Licensing is part of the model.** VCF 9 is licensed per physical core, with a minimum of 16 cores per CPU. Core count changes the cost line directly.

### 3.11 Waste is shown in money, easiest first

- **What:** the waste page lists the five reclamation areas, easiest to hardest:
  1. orphaned files and unmapped blocks
  2. powered-off VMs
  3. idle VMs
  4. oversized VMs
  5. unused VMs

  Inside each area, the largest VMs come first. Every row shows the capacity freed and its cost.
- **Why:**
  - Twenty large VMs cut by 10 vCPUs each free as much as 100 small VMs cut by 2. They need 80 fewer change requests, and large VMs also hurt their neighbours (co-stop, migrations between sockets).
  - SP5: do not force developers to shrink. Show the CFO the cost of waste. The CFO holds the budget and makes each business line act. Money is the language that works.
  - **What is freed is shown honestly:**
    - powering off an idle 10-vCPU VM frees memory and allocation, not CPU cycles;
    - a powered-off VM frees disk only when deleted.

    Overstating the gain destroys trust in the next request.

### 3.12 Capacity sets reclamation policy; PCM carries it out

- **What:**
  - The Capacity team sets the definitions:
    - idle (in MHz, every day, for N days);
    - powered-off period;
    - snapshot age;
    - exclusions.
  - PCM applies them (D-039 daily check). Actions go through the action tiers (D-029). L2 approves until an action type is made automatic (L2 design, 3.7).
- **Why:**
  - SP5 People: Capacity does not run day-to-day work.
  - The definitions are a formal policy. Measurable definitions stop owners from disputing them.
  - Separating "who defines" from "who acts" keeps the weekly rhythm going without the Capacity team doing operations work.

### 3.13 Storage is not projected like compute

- **What:**
  - Datastores and vSAN show space headroom against a hard floor, not only a projection.
  - Thin provisioning is shown on both layers (virtual disk and array) where data exists.
- **Why:**
  - Compute that runs short makes VMs wait. Storage that reaches 0 bytes stops IO, and everything on it stops.
  - A burst of writes or snapshots can fill a datastore long before its "60 days remaining".
  - Thin on thin hides the real exposure unless both layers are read together.

### 3.14 Network gets little space

- **What:** network capacity appears only as host uplink headroom and NSX Edge headroom.
- **Why:** hosts with 50 Gb rarely run out (SP5). Space on the page goes where shortages actually happen.

### 3.15 The landing page shows what changed this week

- **What:** `/capacity` opens on the changes since last week:
  - clusters that moved into their decision window;
  - forecasts that shifted;
  - new demand in the register;
  - reclamation done and waste trend;
  - the next procurement round and its deadline.
- **Why:**
  - Capacity moves slowly. A page that shows the same 300 clusters every week becomes wallpaper.
  - On a weekly rhythm, the delta is the news.

### 3.16 No live data, no alerts

- **What:** the workspace shows nothing real-time and sends no notifications.
  - Capacity guard rails (a cluster at red) are alerts for L1 and L2.
- **Why:**
  - SP5: capacity changes over hours and days. Real-time data adds noise and load, and no capacity decision depends on the last 5 minutes.
  - "Alert on capacity running low months ahead" is an SP5 misconception: an alert must be urgent.

### 3.17 Vocabulary: technical, with SP5 units

- **What:**
  - Full technical terms.
  - CPU in physical threads (GHz only for reservation).
  - Memory in DRAM.
  - Overcommit per thread.
- **Why:**
  - Capacity planners are technical (D-051 applies only to Executive).
  - The units must be exact. 3:1 per thread is 6:1 per core with Hyper-Threading. Mixing them doubles or halves a plan.

### 3.18 Agent E2: runs the calculator, explains, drafts

- **Agent E2 may:**
  - run the planning calculator for a scenario;
  - explain why a resource limits the cluster;
  - draft the purchase justification for IT Finance.
- **Agent E2 may not:**
  - approve a purchase plan;
  - change the capacity model of a cluster.

  The human who asked is recorded with each task (D-050).

## 4. Pages

| Path | Job | Main question |
|---|---|---|
| `/capacity` | This week | What changed since last week? |
| `/capacity/clusters` | All clusters | Which clusters need a decision, and by when? |
| `/capacity/cluster/{id}` | One cluster | How does total become usable, what limits it, and when does it run out? |
| `/capacity/demand` | Demand register | What demand is coming that the data cannot show? |
| `/capacity/what-if` | Scenarios | What happens if we add, remove or change something? |
| `/capacity/refresh` | Hardware life cycle and host standard | Which hosts age out, and what replaces them? |
| `/capacity/plan` | Procurement round, with cost line items | What do we buy in the next round, and what does it cost? |
| `/capacity/waste` | Reclamation, in money | What can we reclaim, starting where? |

## 5. Settled questions

- Capacity settings per cluster: the Capacity team (D-054).
- Purchase plan: a document for IT Finance in 1.0 (D-055).
- Chargeback: VMs are free in 1.0, so the platform team may reclaim (D-056).
- Storage: vSAN and datastore space in 1.0; arrays later (D-057).
