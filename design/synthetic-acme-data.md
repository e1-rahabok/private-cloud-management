# Synthetic ACME data

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

The prototype runs on synthetic data (D-018), served through the same API contract as real collection (PCM core, 3.13). This document sets what that data must be and why.

## 1. Principle: the data is a script of stories, not random numbers

- **What:**
  - The dataset is a believable estate with planted **stories**: situations each workspace must show and handle.
  - Each story names:
    - its question (D-052)
    - its role
    - its cadence
    - the objects involved
    - the expected result
  - The expected result is also an acceptance test.
- **Why:**
  - **Random data gives a demo where nothing happens.** A believable estate is mostly green (SP5: by default all green). The approval audience must still see the moments that make PCM valuable: a red that interrupts the wall, a decision date inside the next purchase round, a slow application proven to be inside the Guest OS.
  - **Planted stories have known answers.** Each regeneration from the specification (D-010) is checked against them automatically. Random data has no right answer to check against.
  - **One dataset serves all four workspaces.** The NOC's red cluster at 10:05 is the same cluster in L2's investigation, and the same one whose run-out date the Executive sees. That proves the core idea: one number, one definition (PCM core, 1).

## 2. The estate

| Item | Value | Why |
|---|---|---|
| Company | ACME Corp (fictional), a global bank (D-065) | Already used in the Executive mockup. Banking gives the strongest calendar-driven load and the strictest regulators, so the stories matter more. |
| Locations | Singapore, Virginia, Frankfurt, Tokyo, London | Already in the mockup. Three regions (Asia Pacific, Americas, Europe) exercise federation and local time. |
| VCF Operations instances | 3, one per region | Exercises federation (D-009), including one instance that goes stale. |
| VCF instances | 5, one per location | A global enterprise usually runs one per site. |
| ESXi hosts | About 1,200 | The SP5 example of a large estate: 1,200 hosts on 5-year depreciation, about 20 replaced a month. Large enough that manual walking fails, which is the point of the daily check (D-039). |
| Host specification | 2 × 32 cores, Hyper-Threading on (128 threads), 768 GB DRAM. Older generation: 2 × 20 cores, 512 GB. | Two generations make hardware refresh (Capacity design, 3.9) and unit cost per thread (D-061) show real differences. |
| Clusters | About 100: workload clusters by class of service, plus management and NSX Edge clusters | Cluster is the unit (Capacity design, 3.1). Several per location and class makes "groups of clusters that can take each other's workload" real. |
| Class of service | Gold, Silver, Bronze, mostly one class per cluster, with a few mixed clusters | SP5: one class per cluster is the design; mixed is a compromise. A few mixed clusters show why. |
| VMs | About 30,000 | About 25 per host. Plausible for a Silver-heavy estate (Capacity design, SP5 host example). |
| Guest OS | Windows and Linux only (D-038) | Scope. |
| History | 13 months hourly for all clusters and hosts; 45 days at 5 minutes for clusters, hosts and the VMs in stories | Matches the store design (PCM core, 3.3). Raw data for all 30,000 VMs adds volume without adding a story. |
| Clock | The present time; "now" is an input, so tests can fix it | See section 4. |

- The mockup's top-line numbers (76,800 units, 480 TB, 21 PB) are replaced by values derived from this estate.
- **Why:** the mockup never defined "units" (Executive design, 4.8). Derived values make every number on the Executive page trace back to hosts and clusters, and that tracing is what the prototype must prove.

## 3. Realism rules from SP5

The generator must follow these rules. A synthetic estate that breaks them teaches the wrong lessons to everyone who sees the prototype.

| Rule | Why |
|---|---|
| Banking load pattern, in each location's local time: online banking by day; the end-of-day batch at night (about 22:00 to 03:00), which is often the daily peak; payday peaks; month-end and quarter-end close; financial year-end close (December in Singapore, Virginia, Frankfurt and London; March in Tokyo) | Patterns are what the weekly check and the forecast look for (D-042, Capacity design 3.5). In a bank, night is not quiet: a design that assumes it is would schedule the weekly check (D-042) into the batch window. |
| Contention stays near zero until utilization nears saturation, then rises sharply | SP5: capacity to performance is non-linear. Linear synthetic data would teach that high utilization is bad. |
| Memory consumed is high on most hosts and is not a problem | SP5: memory is a cache. A prototype that shows high consumed memory as red repeats the most common misreading. |
| Bronze clusters run hotter than Gold and score a higher Cluster Risk (%) | By design (SP5 class of service). Equal scores would hide what the classes mean. |
| Idle VMs are idle every day for the whole window, not on average | SP5 idle definition. The month-end payroll VM is idle 29 days and must not be flagged. |
| Most objects are green most of the time | SP5: by default all green. A prototype full of red teaches the audience that red is normal. |
| Health of a cluster comes from its VMs (worst VM and 90th percentile) | SP5 parent and child rule. |

## 4. Time: the present, with the clock as an input (D-067)

- **What:**
  - "Now" is an input to the generator, next to the seed and the story file. The same three inputs always give the same data.
  - The demo uses the present time by default. Acceptance tests pass a fixed "now" of their own.
  - Stories are written relative to "now". Examples: "SSH enabled 8 hours ago", "decision date in 4 weeks", "contention starts 20 minutes ago".
  - Calendar patterns follow the real calendar:
    - the end-of-day batch at local night;
    - payday, month-end and quarter-end;
    - year-end in December, or March for Tokyo.
  - Stories tied to a day are written as "the most recent" or "the next": the most recent daily check, the next quarter-end. They never name a weekday.
  - The wall is live: data is generated forward, minute by minute, from the present.
- **Why:**
  - **A live demo is more convincing than a frozen one.** The date on the screen is today, and the wall moves because time moves.
  - **Tests stay exact.** Each test sets its own "now", so the expected answer is known.
  - **13 months of history always holds one December and one March,** so the year-end stories (C-3) hold on any date.
  - **Weekday-free stories survive a demo on any day.** A "Monday morning" story shown on a Saturday would contradict the date on the screen.
- **Cost:** generation runs at start-up instead of once. VMs get full detail only where a story needs it, so this takes minutes. The result is cached per day.

## 5. Stories

Each story is one or more objects with a planted condition, and the expected result in each workspace that sees it.

### NOC

| ID | Story | Expected result |
|---|---|---|
| N-1 | Cluster FR-S-02 (Frankfurt, Silver): VM contention starts rising 20 minutes before now, after a batch job starts on a Bronze VM placed in the wrong cluster | "Is it fast?" turns red and interrupts the rotation (D-041). The SOP offers a time-boxed limit only if the villain is non-production (D-040). Here it is production, so the SOP escalates to L2 with evidence. |
| N-2 | The Europe VCF Operations instance stops answering for 20 minutes | Frankfurt and London tiles turn grey "No data", never green (D-041). L1 escalates the grey. |
| N-3 | 40 VMs are deleted in Tokyo within 10 minutes, with no change planned in the calendar | "What changed?" shows the deletions as unexpected. |
| N-4 | Three ESXi hosts in London have had SSH enabled for the last 8 hours | "Is it safe?" shows amber with the count (D-049). |

### L2

| ID | Story | Expected result |
|---|---|---|
| L-1 | The escalation from N-1 arrives | Evidence is filled automatically: VM owner and the VM metrics showing it is not the cause. Agent E2 drafts the cause: a Bronze VM in a Silver cluster. L2 closes it with a cause, a fix and a new check rule (L2 design, 5.9). |
| L-2 | An application owner complains that VM SG-APP-117 is slow | VM health is green; Guest OS run queue is high. The page shows the cause is inside the Guest OS, with evidence for the Windows team (L2 design, 5.6). |
| L-3 | Daily check: one host in cluster VA-G-05 has a different NTP and log configuration from its peers | Configuration, "Correct it" (L2 design, 6.2). Option: fix the host, or fix the standard. |
| L-4 | Daily check proposes moving 6 VMs from the hot cluster SG-S-04 to SG-S-06 | The proposal waits for L2 approval under policy v1 (tier approval). The record (23 approvals, 0 rollbacks) is evidence. L2 proposes policy v2 (automatic, with guardrails), replays it, publishes it; the waiting move then runs under v2 with no approval record (D-079). |
| L-5 | An alert 4 days ago was not predicted by any check | It appears in "slipped through" (D-039). |
| L-6 | Business calendar: the next quarter-end close in all locations, and the next payday in Singapore | The checks explain the rise instead of flagging an anomaly (L2 design, 7.2). |
| L-7 | The end-of-day batch in London ran 40 minutes longer last night; a datastore behind it shows rising latency | The daily check flags it as insight, before the batch window closes late and hits the start of business (SP5 prevention window). |
| T-1 | The general ledger is slow since the weekend change window (from Agent E2 `L4-037`) | L2 logs the complaint against sg-gl-db-01. Agent E2 proposes nine links: Windows, VM CPU and "add vCPUs" are ruled out; a snapshot the backup left doubles the reads (root cause); a NUMA split on a previous-generation host contributes. |
| T-2 | Every web application in Tokyo is slow (from Agent E2 `L4-074`) | L1 escalated it. Web VMs wait on every host while hosts run at 30 to 48%. A change script put the 200 GHz limit on the web pool instead of the batch pool. "Add two hosts" is ruled out. |
| M-1 | Remote memory rises on large VMs on older hosts in London (from Agent E2 `L4-049`) | Monitor, 7 days, grouped by host model: 9 VMs wider than a Gen-2019 NUMA node. The case: the virtual NUMA layout was built at power-on on a newer host; DRS moved the VM. |
| M-2 | Other Wait on two VMs after the weekend backup (from Agent E2 `L4-045`) | One symptom, two causes: a real wait from a leftover snapshot, and an accounting issue of an older ESXi build on an idle VM. |
| M-3 | Gold takes three different hits in one day, and one cluster drifts toward contention | The Performance tab's teaching day: a wide hit (8 Gold clusters at once: both lines drop), a narrow hit (one cluster: only the worst line drops), VMs taking turns in one cluster, and one cluster's Risk rising over 7 days. |

### Capacity

| ID | Story | Expected result |
|---|---|---|
| C-1 | Cluster group SG-Silver: memory runs out in 5 months; procurement lead time is 4 months | The decision date is in 4 weeks, before the next purchase round closes. It is at the top of the cluster list and in the plan (Capacity design, 3.7–3.8). |
| C-2 | Cluster group TK-Gold: 60% capacity remaining for 9 months, slow growth | Dark grey, waste. Not green (Capacity design, 3.3). |
| C-3 | Year-end close: December in Virginia, March in Tokyo | A 90-day forecast misses both; the 13-month forecast catches them and moves the decision dates of VA-Silver and TK-Silver earlier (Capacity design, 3.5). Two different year-ends prove the forecast follows each location's own calendar. |
| C-4 | Demand register: an OpenShift migration wave of 800 VMs to Frankfurt in May | FR-Silver's run-out date moves earlier. The register shows the owner (Capacity design, 3.6). |
| C-5 | 90 older hosts in London, most of its fleet, reach end of depreciation within 12 months | The what-if shows that replacing them with the new standard covers London's growth without expansion (Capacity design, 3.9). |
| C-6 | Reclamation: 300 powered-off VMs, 900 idle VMs, 60 large oversized VMs | Shown easiest first, largest first. Cost avoidance counts only the purchase it defers: SG-Silver moves out of the purchase round (D-060). |

### Executive

| ID | Story | Expected result |
|---|---|---|
| E-1 | Overall health: up and fast green, safe amber (N-4, certificates) | Three cards; safe is amber with a plain sentence (Executive design, 4.1). |
| E-2 | Room to grow: Singapore's earliest date is C-1, already in the next purchase round | Shown as "in the plan", not as an alarm (Executive design, 4.4). |
| E-3 | Site recovery: Frankfurt's plan last tested 4 months ago, but 220 VMs added since were never tested | Amber, with the share of protected VMs tested (D-059). For a bank this is a regulator question: regulators require tested recovery for critical systems. |
| E-4 | Cost avoided this year from reclamation, valued at today's price (C-6) | Shown as cost avoided, not saving (D-060). |
| E-5 | Goals: "fewer alerts" on track; "versions at N or N-1" at risk | Goals row (Executive design, 4.7). |

## 6. How the data is made

- **What:**
  - A generator script in the repository builds the dataset from a fixed seed and a story file.
  - Same seed and story file, same data: byte for byte.
  - Output: files served by a mock API that follows the PCM API contract.
- **Why:**
  - **Reproducible.** A test that fails must fail the same way every time.
  - **Stories as a file.** Adding a story means editing the file, not the generator. The author can add stories from field experience without code.
  - **Generated, not hand-written.** 30,000 VMs and 13 months of history cannot be written by hand. A generator that follows the realism rules (section 3) keeps the background believable around the stories.

## 7. Open questions for the author

1. **More stories.** Which situations from your field experience must the approval audience see? Add them to section 5, or tell me and I will write them.
