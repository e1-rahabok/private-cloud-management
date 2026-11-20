# Decisions

Decisions on PCM scope and design. One entry each. Newest at the bottom. A changed decision is edited in place; git keeps the history.

| ID | Date | Decision | Reason |
|---|---|---|---|
| D-001 | 2026-11-20 | The product is named **PCM** (Private Cloud Management). | Short, vendor-neutral. |
| D-002 | 2026-11-20 | PCM is not a Broadcom product. It is free, and customers download it. | It helps customers grow VMware into their complete private cloud. |
| D-003 | 2026-11-20 | Scope is the whole private cloud, not only VMware. A private cloud has dozens of vendors, competitors included. PCM connects to them, for example ITSM, CMDB and email. | VMware is the core, not the whole estate. |
| D-004 | 2026-11-20 | On-premises only. Customers own the full source code and personalize it. | Customer data stays on site. Large enterprises adapt tools to their own process. |
| D-005 | 2026-11-20 | Target: large global enterprises, not small companies. | Their need for role-specific operations is greatest. |
| D-006 | 2026-11-20 | PCM uses VCF Operations as a data source and has its own database. It does not depend 100% on VCF Operations. | VCF Operations covers only the VMware part, and PCM keeps its own data. |
| D-007 | 2026-11-20 | PCM replaces the VCF Operations presentation layer for capacity, cost, performance, inventory, configuration and availability management. Compliance follows D-022. | These are the operations areas PCM serves by role. |
| D-008 | 2026-11-20 | Out of scope: VCF lifecycle management (the SDDC Manager part) and security operations. | Lifecycle is Broadcom software management. Security operations is a different field with different expertise. |
| D-009 | 2026-11-20 | New capabilities: an executive dashboard, multiple VCF Operations instances, and documentation for the private cloud. | Starting points: [VMW-Executive-Dashboard](https://github.com/e1-rahabok/VMW-Executive-Dashboard), [VMW-Federated-VCF-Operations](https://github.com/e1-rahabok/VMW-Federated-VCF-Operations), [private-cloud-explained](https://github.com/e1-rahabok/private-cloud-explained). Ideas are also borrowed from https://isvara.io. |
| D-010 | 2026-11-20 | The specification is the maintained artifact. AI writes 100% of the code. Developers do not maintain code. | Generating code is cheap. The specification is what has to stay correct. |
| D-011 | 2026-11-20 | Each role gets a workspace with its own URL. Workspaces share no menu. | One common UI for all roles weakens the experience for each of them. |
| D-012 | 2026-11-20 | Workspaces are per role, not per pillar of operations management. First four: **NOC** (L1 operators), **L2**, **Capacity**, **Executive**. | Enterprise IT is run by people in different roles. Each role gets its own workspace. |
| D-013 | 2026-11-20 | NOC: a few pages. L1 operators have simple needs and follow the SOP. | L1 work is SOP-driven. |
| D-014 | 2026-11-20 | Capacity Management runs weekly, not daily. It includes what-if analysis and hardware refresh. | Capacity decisions follow a weekly cadence. |
| D-015 | 2026-11-20 | Executive: one page, with drill-down to the next level. The [Executive Dashboard export](https://e1-rahabok.github.io/VMW-Executive-Dashboard/design/export/) is the starting point. | The CIO has no time for detail. |
| D-016 | 2026-11-20 | PCM takes actions, not only reads. | Operations work needs action, not only viewing. |
| D-017 | 2026-11-20 | PCM includes a local LLM, for example Agent E2. | On-premises only (D-004). |
| D-018 | 2026-11-20 | The prototype uses synthetic ACME data. A lab with a full VCF 9.1 instance follows later. | No customer data is needed for the prototype. |
| D-019 | 2026-11-20 | Money has three parts. **Cost** is what the company pays: hardware and software line items, used in Capacity Management. **Price** is what tenants pay: per VM, per Kubernetes pod and so on. **Value** is what the Executive sees: total cost, ROI, TCO, with no line items. | Each part answers a different role's question. |
| D-020 | 2026-11-20 | Inventory has two parts. **Basic inventory** is foundational: every workspace has its own purpose-built variant. **Detailed inventory** tracks changes for analysis and belongs to the L2 role. | Every role needs to know what exists. Only L2 analyses how it changes. |
| D-021 | 2026-11-20 | The L2 role covers escalation (reactive) and proactive health checks, across availability, performance and configuration. | L2 is the expert behind the NOC. |
| D-022 | 2026-11-20 | Compliance is parked under security, after release 1.0. | It needs security expertise (D-008). |
| D-023 | 2026-11-20 | VMware is mandatory. Competitors are included only for migration into VMware, not for management. Migration runs one way only: into VMware. Red Hat OpenShift is the first. | The goal is to bring the whole private cloud infrastructure onto VMware (D-002). |
| D-024 | 2026-11-20 | Documentation has its own URL, for example `privatecloud.acme.com/docs`. | Follows D-011. |
| D-025 | 2026-11-20 | PCM runs actions directly through vCenter and VCF APIs, not through ITSM or automation tools. | Those tools are too slow for self-driving operations. |
| D-026 | 2026-11-20 | Upgrading a customer-personalized specification is deferred until after the prototype is approved. | The prototype comes first. Large open-source products such as Odoo and Linux live with the same problem. |
| D-027 | 2026-11-20 | The FinOps role owns Price: cost accounting and chargeback. FinOps works with the Capacity team. Its workspace comes after release 1.0. | Price is a FinOps job, not a Capacity or Executive one. |
| D-028 | 2026-11-20 | All workspaces run on one host, each under its own path: `privatecloud.acme.com/noc`, `/l2`, `/capacity`, `/exec`, `/docs`. No shared menu. | One host to deploy and secure. Separate paths keep each role's experience separate (D-011). |
| D-029 | 2026-11-20 | Action governance lives inside PCM. Each action has a tier: automatic, approval in PCM, or never automatic. A fixed policy sets the tier; the LLM only proposes. Every action is written to an audit log in PCM. | Direct actions (D-025) still need control and an answer to "who changed what, why, and who approved". |
| D-030 | 2026-11-20 | Management scope is Broadcom VMware only; competitors appear only for migration (D-023). Out of scope: end-user help desk (for example "my laptop is not working") and business transactions (for example "the payment system is slow"). Scope guide: https://isvara.io/read/part-2/role-based-contents | PCM manages the VMware private cloud, not the applications or end-user devices on it. |
| D-031 | 2026-11-20 | L1 works in three shifts; someone always watches. Fewer people per shift than today (D-046). No mobile push for L1; mobile push is for L2. | The NOC is staffed 24x7, so L1 does not need to be paged. Even with AI, people stay on every shift: not all operational context is in a computer, so AI does not have all of it. |
| D-032 | 2026-11-20 | L1 has two UIs. **Wall screen**: a large TV that streams the present, with no mouse and no keyboard; it auto-rotates about every 60 seconds through Inventory, Availability, Performance, Security, Compliance, Configuration. **Desktop dashboard**, assisted by Agent E2. Live screen practice: https://isvara.io/read/part-2/proactive-operations | A static screen bores the viewer. The wall is for watching; the desk is for working. |
| D-033 | 2026-11-20 | A workspace shows only the data its role acts on. The NOC shows no cost or price data. | L1 does not decide anything with cost. Data a role does not act on is noise. |
| D-034 | 2026-11-20 | PCM manages VMware infrastructure only. Not the mainframe, not VDI, not applications. | Keeps PCM focused on the VMware private cloud (D-030). |
| D-035 | 2026-11-20 | L1 and the CIO see health as three plain questions, in this order: **Is it up? Is it fast? Is it safe?** They are not shown the split between security and compliance. Source: SP5 framework, https://github.com/e1-rahabok/agent-e2/tree/main/knowledge/sp5-framework | A system that is down has no security or performance problem. Up is not fast. Fast is not safe. The split between security and compliance helps experts, not L1 or the CIO. |
| D-036 | 2026-11-20 | The NOC wall rotates through 5 screens, each titled as a question: **What changed?** (inventory), **Is it up?**, **Is it fast?**, **Is it safe?** (security and compliance together, VMware only), **Is it set right?** (configuration). This changes the 6-screen order in D-032. | Follows D-035: L1 does not need the split between security and compliance. Compliance changes slowly; a compliance drift that happens now is a safety event. Fewer screens means a shorter cycle, so red stays off screen for less time. |
| D-037 | 2026-11-20 | The Operations Manager role has no workspace in release 1.0. | Scope control. The four workspaces come first. |
| D-038 | 2026-11-20 | The Guest OS is in scope, limited to Windows and Linux at the OS level. Applications inside the Guest OS are out. macOS is out. | IT owns the OS build standard (SP5 People: OS teams). Applications belong to their owners (D-034). macOS on ESXi is rare in enterprises. See Rationale. |
| D-039 | 2026-11-20 | The daily check is run by PCM, not by a person. It runs before the start and before the end of each region's business day. Platform (L2) owns the review, not L1. The human review takes about 10 minutes when there is no problem. | See Rationale. |
| D-040 | 2026-11-20 | L1 acts only through SOP buttons in PCM, never through vCenter. The L1 action set is small, reversible and set by class of service. | See Rationale. |
| D-041 | 2026-11-20 | Wall behaviour: a fixed status strip on every screen; red interrupts the rotation until acknowledged; stale data turns the wall grey, never green; with five or more displays, nothing rotates. | See Rationale. |
| D-042 | 2026-11-20 | PCM also runs the weekly check, a deeper analysis. It runs when load is low, by default Sunday early morning in each region's local time. Platform (L2) reviews the result in about 1 hour. | The weekly check loads the systems it reads. See Rationale. |

| D-043 | 2026-11-20 | The monthly review (1 day) is also the bigger team meeting: everyone meets to discuss important but not urgent matters, plan the next month, and review progress for the year against goals. PCM prepares the review pack; L2 (Platform) hosts it. | See Rationale. |
| D-044 | 2026-11-20 | A suspected breach is not investigated in PCM. L2 secures the evidence and hands it to the security team. Security is parked until after release 1.0. | "Is it breached?" is a forensic investigation, not troubleshooting (SP5), and needs security expertise (D-008, D-022). |
| D-045 | 2026-11-20 | L2 owns PCM's own settings (class-of-service definitions, action tiers) in release 1.0. After 1.0, the Operations Manager approves changes. | L2 knows what the settings do. A second approver comes with the Operations Manager workspace. |
| D-046 | 2026-11-20 | PCM is designed for a lean team of senior, highly experienced people. L2 is not 100% dedicated to operations; it also does architecture and engineering. Most routine and easy work is assisted by AI. | In the agentic AI era, the team is likely a few times smaller than today. |
| D-047 | 2026-11-20 | Agent E2 is a core team member, not a tool. Assume it knows vSphere, Windows, Linux, networking and the rest of the stack, even though today it knows only vSphere. | AI does the routine work the lean team (D-046) no longer has people for. |
| D-048 | 2026-11-20 | PCM assumes a two-layer organization. Today's top layers are cut the most. The middle layer becomes the new upper layer. | In a large IT organization with 8 layers, the top 3 are the highest paid and the furthest from ground reality: they neither do the work nor know the technology. AI removes the need for them first. |
| D-049 | 2026-11-20 | In release 1.0, "Is it safe?" shows VMware platform hygiene only: root logins, ESXi Shell or SSH enabled, lockdown mode off, certificates near expiry. No attack or breach detection (D-044). | These are configuration checks L2 already runs. They are among the most common causes of outages and audit findings in VMware estates. Health keeps its three questions (D-035). |
| D-050 | 2026-11-20 | Agent E2 cannot carry responsibility. Every Agent E2 task, action or change records two fields: Agent E2's own ID, and the human who ordered it. That human varies by task. Agent E2 can serve several managers at once, because it tracks who ordered what. | Accountability stays with a person. The audit log answers "who ordered this", not only "what did it". |
| D-051 | 2026-11-20 | The Executive workspace uses plain language with basic IT words. Technical terms are kept to a minimum, including in the drill-down. Allowed: server, storage, network, data centre, application, backup, recovery, outage, capacity, cost, upgrade, version, virtual machine (VM). Avoided: ESXi, vSAN, NSX, DRS, HA, vCPU, IOPS, latency, contention, cluster, host, datastore, resource pool, RTO, RPO, snapshot. A build test fails if an avoided term appears in the page text. The list lives in the specification, so customers can change it. | The CIO presents this page upward to the CEO, CFO and board. Basic IT words are understood there; product and engineering terms are not. CEOs and CFOs hear "virtual machine" in budget discussions. |
| D-052 | 2026-11-20 | Every visual answers a named question, for a named role, at a named cadence. A visual that cannot name all three is cut. | A rich UI turns into decoration without this rule. It also gives each regeneration from the specification (D-010) a test that a visual can pass or fail. |
| D-053 | 2026-11-20 | The prototype is built in this order: Executive, NOC, L2, then Capacity. All four stay in release 1.0 (D-012). | See Rationale. |
| D-054 | 2026-11-20 | The Capacity team owns the capacity settings of each cluster: buffer, procurement lead time, procurement round dates. Class-of-service definitions stay with L2 (D-045). | The people who answer for the purchase date set the inputs to it. |
| D-055 | 2026-11-20 | In release 1.0 the purchase plan is a document for IT Finance. PCM does not connect to procurement systems. | Procurement systems differ by customer and are slow to integrate. A clear document already removes most of the work. |
| D-056 | 2026-11-20 | Release 1.0 assumes VMs are free to tenants (no chargeback). So the platform team may reclaim. | This is the most common case today (SP5). Price and chargeback come with FinOps after 1.0 (D-027). |
| D-057 | 2026-11-20 | Storage capacity in release 1.0 covers vSAN and datastore space as vSphere sees it. External arrays come later. | Array capacity needs a vendor adapter per array. vSAN is in VCF already. |
| D-058 | 2026-11-20 | The FinOps team owns the public-cloud comparison. In release 1.0 FinOps has no workspace (D-027), so it maintains the comparison as an input to PCM. The comparison covers the whole estate over the depreciation period, component by component. | Source: Cost n Price n Value. Comparing one VM for one day flatters whichever side picks the VM. The whole estate over 5 years, with each component marked included or excluded, is the honest comparison. |
| D-059 | 2026-11-20 | The Executive recovery card shows site recovery test results only: VMware Live Site Recovery (formerly Site Recovery Manager) recovery plans, last test date, recovery time achieved and target, and the share of protected VMs tested. It is labelled site recovery. Backup is not claimed. | See Rationale. |
| D-060 | 2026-11-20 | PCM follows the cost model in Cost n Price n Value. There is no VM cost: unit cost is on the provider (ESXi host, then cluster); price is on the consumer. Cost has three parts: product, service, people. Reclamation is cost avoidance, valued at today's price of new capacity in that location, and counted only when it defers a purchase. | See Rationale. |
| D-061 | 2026-11-20 | CPU unit cost is always per physical thread. Cores are used only for licensing. | A vCPU runs on a thread, so capacity is counted in threads (Capacity design, 3.17). Cost uses the same unit, so cost and capacity can be compared. |
| D-062 | 2026-11-20 | No check of the VCF APIs for now. They are checked later against a live VCF 9.1 system the author provides. | A live system gives a firmer answer than reading API references. |
## Rationale

Longer reasons for decisions that need them.

### D-038 Guest OS, limited

- SP5 separates the VM from the Guest OS: they are different realms. The hypervisor does not see what runs inside Windows or Linux.
- PCM keeps that split. The VM (the virtual motherboard) and the Guest OS are **separate objects**, each with its own health.
  - A Guest OS that is slow because of its own run queue or paging does not turn the VM or the ESXi host red.
  - This stops the most common false escalation in large estates: "the app is slow, so the host is bad".
- Guest OS counters in scope are the ones SP5 lists for the OS teams: CPU run queue, context switches, memory paging, disk queue and free space.
  - These are the evidence for "it is on my court" when L2 hands a problem to the Windows or Linux team.
- Out of scope: processes, services and application counters. They lead into application monitoring (D-034).

### D-039 The daily check

**Time budget**
- Human time follows the SP5 24-hour timeline: daily check 10 minutes, weekly check 1 hour, monthly review 1 day. The NOC live screen is always on.
- PCM's run happens before that, in the hour before 09:00. The human starts from results, not from raw dashboards.
- The 10 minutes are for judgement, not for walking the estate:
  - read the verdicts (present health, risk, efficiency);
  - read the alert trend;
  - weigh the day's business context;
  - approve or reject the fixes PCM proposes (D-029).
- When the check finds a problem, the 10 minutes end and troubleshooting starts. That takes as long as the problem needs.

**Why PCM runs it, not a person**
- At 6,000 hosts, 300 clusters and 100,000 VMs, nobody walks the estate by hand in 10 minutes.
- The walk is possible only through the KPI models: 0–100%, worst first, built from the worst VM and the 90th percentile, never from averages.
- Once the models exist, a machine can walk them. The person reads only the exceptions. SP5 describes this: a script runs from 08:00 to 09:00, the expert reviews at 09:00, and the environment is prepared for the day by 10:00.

**Why the owner is Platform (L2), not L1**
- The check produces insight, not alerts.
- An insight needs knowledge of the environment and of the day's business context. Example: total IOPS is low on the day before a retail holiday. That means sales are not happening.
- L1 follows the SOP and does not have that context.
- The SP5 path ("L1 runs it once confident") was a workaround for a manual check. PCM does the walking, so L1 does not have to.

**Why two runs a day, per region**
- Start of day: prepare for the load expected today, for example approving a rebalance between clusters.
- End of day: matters more than it looks. Nights have the fewest experts on site, only L1 and the L2 on call.
  - Fixing an emerging problem at 17:00 prevents a page at 02:00.
- A global enterprise runs both checks in each region's local time, because business load and change windows follow local time.

**Each run also lists the alerts that slipped through**
- It shows the alerts from the previous period that the check did not predict.
- This is SP5's weekly improvement loop, applied every day.
- Over months, fewer alerts slip through.

### D-040 L1 actions

**Principles, from large-scale VMware operations**
- **L1 never logs in to vCenter.**
  - Every L1 action is an SOP button in PCM. PCM runs it with its own service account and writes the audit record (D-029).
  - A shift of junior operators with vCenter admin rights is how large estates get unexplained changes at 03:00.
- **Every L1 action is reversible and limited in reach.** If the action cannot be undone, or can affect more than one cluster, it is L2's.
- **The action depends on class of service.** The same contention needs a different response for a Gold production VM than for a test VM.

**The L1 action set in release 1.0**

| Action | Scope | Why it is safe for L1 |
|---|---|---|
| Acknowledge, annotate, escalate | Any alert | Escalation carries the evidence automatically: the L1 exit criteria are the L2 entry criteria. PCM routes it to the right L2 group (platform, storage, network) by object type. |
| Close an alert | Any alert | Only with a root cause chosen from a list. SP5: close when the cause is known, not when the symptom goes away. |
| Stop provisioning (close a cluster), then reopen it | Cluster | No running VM is touched. It stops new load from landing on a cluster whose VMs are already waiting for resources. SP5 names this as a NOC action. |
| Time-boxed limit on a "villain" VM | Non-production VMs only | Limits are the classic forgotten setting: an old limit causes mystery contention months later. PCM sets the limit with an expiry, removes it itself, and logs both actions. On production VMs a limit is L2's call. |
| Restart an unresponsive VM | Non-production VMs only, and only when VMware Tools heartbeat is lost | A hung non-production VM is an availability fix of the kind an SOP covers. A production restart needs the application owner, so it goes to L2. |

**Not for L1, and why**
- **Manual vMotion.** In a fully automated DRS cluster, DRS moves the VM back. Moving to another cluster touches networks, storage, licensing and affinity rules.
- **Host maintenance mode.** It moves load and uses up HA failover capacity. Proactive HA already handles predicted hardware failure automatically.
- **Snapshot deletion.** Consolidation can stun the VM at peak time, and backups own the snapshots.
- **Any change to vCenter, NSX or vSAN configuration.**

**Where the actions are defined**
- These actions live in the SOPs.
- L2 adds an action when it turns a solved problem into an SOP (SP5: L2 updates the guide so L1 can handle the case next time).
- The action tier (D-029) still decides whether L1 may run it.

### D-041 Wall behaviour

**Fixed status strip**
- Every screen carries a strip of five chips, one per question, each showing that screen's worst state.
- A red on another screen is never more than a glance away, even while it is off the wall.

**Red interrupts the rotation**
- When a screen turns red, the rotation stops on it.
- It resumes when L1 **acknowledges** the red on the desktop. It does not wait for the red to clear.
- Reason: pinning until the red clears would hide every other screen for the hours a fix can take. The wall's job is to show what is new.
- After acknowledgement, the chip stays red and is marked as being worked on. A new red interrupts the rotation again.
- With more than one red, the rotation cycles through the red screens only.

**Stale data turns grey**
- The most dangerous wall is one that shows green because it is blind: a collector down, a VCF Operations instance not answering, a stuck browser.
- Every screen shows how old its data is.
- Data older than two collection cycles turns the screen **grey with "No data"**, never green.
- A grey screen is itself something L1 escalates.

**No rotation on large walls**
- Large NOCs have video walls with several displays.
- With five or more displays, each question gets its own display and nothing rotates.
- Rotation is a workaround for having one display.

**Why all green by default**
- A wall that is often red teaches the room to ignore red.
- Red on the wall is only for what L1 can act on the same day (SP5).
- Everything else goes to the daily check (D-039) or to an alert.

### D-042 The weekly check

**Why it loads the systems it reads**
- It covers a week of 5-minute data per object, not one day. That is about 2,000 points per metric per object.
- It reads per-instance metrics, for example each virtual disk and each vCPU, not just per-VM totals. These are the leading indicators SP5 uses for insight.
- It scans the full configuration of every object against the baseline. That means many vCenter and NSX API calls.
- It scans a week of logs.
- In a large estate this is millions of data points, and heavy API load on VCF Operations and vCenter.
  - vCenter is not just a data source. It also runs DRS, HA and provisioning. Slowing it during business hours slows operations.

**Why Sunday early morning, configurable**
- It is the lowest business load in most regions.
- It is also when backups and patching usually run, because of the same low load. PCM must not compete with them.
- So the schedule is set per region and avoids that region's backup and maintenance windows. Sunday early morning is only the default.

**What it adds over the daily check**
- Patterns a day cannot show: weekly cycles, slow drifts, VMs that are slightly worse every day.
- A review of the alerts that slipped through all week, used to improve the checks.
- Each finding goes to L2 with an owner and an action.

### D-043 The monthly review

**What it is**
- More than a long check. It is the one time each month the whole team meets: L1 leads, L2, the Capacity team, Architecture, and others as needed.
- It has three jobs:
  - discuss important but not urgent matters;
  - plan the next month;
  - check progress for the year against goals.

**Why PCM prepares the pack**
- A day of the whole team is the most expensive hour of the month. It should be spent on judgement and decisions, not on building slides.
- PCM produces the pack the same way it produces the daily and weekly checks:
  - one year of baselines and trends;
  - repeated escalations;
  - alerts that slipped through;
  - configuration risk progress;
  - the capacity outlook from the Capacity team's weekly work.

**Why yearly goals live in PCM**
- SP5 Day 0: goals follow SMART criteria, with metrics to measure success.
- A goal written in a slide deck in January is forgotten by March. A goal held in PCM is measured every month from the same data.
- Example goals:
  - fewer alerts;
  - fewer repeated escalations;
  - more problems found by a check than by an alert;
  - versions at N or N-1.

**Why the meeting records decisions and owners**
- A meeting without recorded actions repeats itself next month.
- Each decision gets an owner and a due date in PCM. The next month's pack opens with their status.

**Why L2 hosts it**
- SP5: deep analysis and long-term planning (1 week to 1 year) is done by the L2 team.
- The review is shown on one screen in the room as a live dashboard, not a PDF. SP5 IT management: a monthly presentation supported by a live dashboard for an interactive discussion.
- Other roles attend without needing a workspace of their own (D-037).

### D-053 Prototype build order

**The goal of the prototype is approval** (D-026). The order follows who approves and what each step proves.

1. **Executive first.**
   - The people who approve PCM read this page.
   - A mockup already exists (D-015). It needs aligning with D-019, D-035, D-049 and D-051, not inventing.
   - It is the fastest way to show something real.
2. **NOC second.**
   - It is the opposite end of every scale: live versus monthly, junior versus senior, a wall TV versus a desk.
   - Shown next to Executive, it proves the core idea of PCM: one data core, completely different experiences per role (D-011).
   - It is also small: five wall screens and a few desk pages.
3. **L2 third.**
   - It proves the PCM core works: the automated daily check, the action tiers, the escalation loop, and Agent E2 as a team member.
   - It is the deepest workspace, so it comes once the pattern is proven.
4. **Capacity fourth.**
   - It needs its own engine: a forecast over 13 months of history, the what-if model and the demand register.
   - Its synthetic data is the hardest to make believable, because it needs a year of seasonal history.
   - Building it last lets it reuse everything the first three proved.

**Why not build all four at once**
- Code is cheap (D-010), but verification is not. Each workspace needs its numbers checked against the specification.
- Four at once means four sets of mistakes found at the same time.
- In this order, each step fixes the shared core before the next one depends on it.

### D-059 The recovery card

- The board asks "can we recover?". The honest answer from PCM's data is narrower: "the site recovery plans were tested on this date, and recovered in this time".
- Site recovery test results are VMware data (D-034). Backup products are not, so PCM cannot prove backups.
- **Labelling decides trust.** A card titled "Recovery" with a green status lets the board assume backups are covered too. When a ransomware event shows they were not, the page loses all credibility. A card titled "Site recovery tested" claims only what it shows.
- **The share of protected VMs tested matters more than the last test date.** In large estates, the common gap is a recovery plan that was tested once and then grew by hundreds of VMs that were never tested.
- An untested plan shows amber, however recent the last test. A test older than the policy period (for example 12 months) shows red.

### D-060 The cost model

Source: Cost n Price n Value (in `sources/`).

**No VM cost**
- Delete every VM today and the company saves nothing: the multi-year contracts are already paid.
- So cost is never divided per VM. Unit cost belongs to the provider:
  - CPU per physical thread, always (D-061); memory per GB; disk per GB;
  - at the ESXi host, rolled up to the cluster.
- Price belongs to the consumer, and is a separate number set by FinOps after 1.0 (D-027).
- "Unallocated cost" does not exist. Unsold capacity lowers revenue; it does not create cost.

**Three parts of cost**
- **Product:** hardware and software, from vendor contracts.
- **Service:** data centre facilities, managed services.
- **People:** the fully loaded cost of everyone who designs, builds and runs the private cloud, including the share of IT leadership time.
- The Executive cost breakdown uses these three. It replaces the mockup's four categories (people, hardware, facilities, software).

**Reclamation is cost avoidance, not cost saving**
- Deleting files saves nothing by itself. It becomes money only when it defers a purchase.
- The value is today's price of the capacity not bought, not what the old hardware cost five years ago.
  - Example: hardware bought for $3M five years ago is now replaced by a $1M equivalent. Reclamation that defers the purchase avoids $1M, not $3M.
- It is counted per location. Spare memory in Singapore does not serve VMs in Frankfurt.
- The Capacity waste page (Capacity design, 3.11) and the Executive cost card (Executive design, 4.6) show it this way.

