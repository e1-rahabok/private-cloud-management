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
| D-009 | 2026-11-20 | New capabilities: an executive dashboard, multiple VCF Operations instances, and documentation for the private cloud. Revised by D-082: documentation for colleagues is private-cloud-explained, a separate product; PCM documents only its own objects. | Starting points: [VMW-Executive-Dashboard](https://github.com/e1-rahabok/VMW-Executive-Dashboard), [VMW-Federated-VCF-Operations](https://github.com/e1-rahabok/VMW-Federated-VCF-Operations), [private-cloud-explained](https://github.com/e1-rahabok/private-cloud-explained). Ideas are also borrowed from https://isvara.io. |
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
| D-021 | 2026-11-20 | The L2 role covers escalation (reactive) and proactive health checks, across availability, performance and configuration. Revised by D-083 and D-084: L2 works in three activities (Monitor, Troubleshoot, Improve); escalation is one trigger of troubleshooting. | L2 is the expert behind the NOC. |
| D-022 | 2026-11-20 | Compliance is parked under security, after release 1.0. | It needs security expertise (D-008). |
| D-023 | 2026-11-20 | VMware is mandatory. Competitors are included only for migration into VMware, not for management. Migration runs one way only: into VMware. Red Hat OpenShift is the first. | The goal is to bring the whole private cloud infrastructure onto VMware (D-002). |
| D-024 | 2026-11-20 | Documentation has its own URL, for example `privatecloud.acme.com/docs`. Revised by D-082: `/docs` documents PCM's own objects only. | Follows D-011. |
| D-025 | 2026-11-20 | PCM runs actions directly through vCenter and VCF APIs, not through ITSM or automation tools. | Those tools are too slow for self-driving operations. |
| D-026 | 2026-11-20 | Upgrading a customer-personalized specification is deferred until after the prototype is approved. | The prototype comes first. Large open-source products such as Odoo and Linux live with the same problem. |
| D-027 | 2026-11-20 | The FinOps role owns Price: cost accounting and chargeback. FinOps works with the Capacity team. Its workspace comes after release 1.0. | Price is a FinOps job, not a Capacity or Executive one. |
| D-028 | 2026-11-20 | All workspaces run on one host, each under its own path: `privatecloud.acme.com/noc`, `/l2`, `/capacity`, `/exec`, `/docs`. No shared menu. | One host to deploy and secure. Separate paths keep each role's experience separate (D-011). |
| D-029 | 2026-11-20 | Action governance lives inside PCM as policy as code. Each action type has a tier (automatic, approval, never) and guardrails, versioned in the catalog with an owner. An automatic action never records an approval: if an approval could be automated, it is not needed, so it is removed from the policy. Every action is written to the action history. Revised by D-079. | Direct actions (D-025) still need control. Guardrails reduce risk; approval records do not. |
| D-030 | 2026-11-20 | Management scope is Broadcom VMware only; competitors appear only for migration (D-023). Out of scope: end-user help desk (for example "my laptop is not working") and business transactions (for example "the payment system is slow"). Scope guide: https://isvara.io/read/part-2/role-based-contents | PCM manages the VMware private cloud, not the applications or end-user devices on it. |
| D-031 | 2026-11-20 | L1 works in three shifts; someone always watches. Fewer people per shift than today (D-046). No mobile push for L1; mobile push is for L2. | The NOC is staffed 24x7, so L1 does not need to be paged. Even with AI, people stay on every shift: not all operational context is in a computer, so AI does not have all of it. |
| D-032 | 2026-11-20 | L1 has two UIs. **Wall screen**: a large TV that streams the present, with no mouse and no keyboard; it auto-rotates about every 60 seconds through Inventory, Availability, Performance, Security, Compliance, Configuration. **Desktop dashboard**, assisted by Agent E2. Live screen practice: https://isvara.io/read/part-2/proactive-operations | A static screen bores the viewer. The wall is for watching; the desk is for working. |
| D-033 | 2026-11-20 | A workspace shows only the data its role acts on. The NOC shows no cost or price data. | L1 does not decide anything with cost. Data a role does not act on is noise. |
| D-034 | 2026-11-20 | PCM manages VMware infrastructure only. Not the mainframe, not VDI, not applications. | Keeps PCM focused on the VMware private cloud (D-030). |
| D-035 | 2026-11-20 | L1 and the CIO see health as three plain questions, in this order: **Is it up? Is it fast? Is it safe?** They are not shown the split between security and compliance. Source: SP5 framework, https://github.com/e1-rahabok/agent-e2/tree/main/knowledge/sp5-framework | A system that is down has no security or performance problem. Up is not fast. Fast is not safe. The split between security and compliance helps experts, not L1 or the CIO. |
| D-036 | 2026-11-20 | The NOC wall rotates through 5 screens, each titled as a question: **What changed?** (inventory), **Is it up?**, **Is it fast?**, **Is it safe?** (security and compliance together, VMware only), **Is it set right?** (configuration). This changes the 6-screen order in D-032. | Follows D-035: L1 does not need the split between security and compliance. Compliance changes slowly; a compliance drift that happens now is a safety event. Fewer screens means a shorter cycle, so red stays off screen for less time. |
| D-037 | 2026-11-20 | The Operations Manager role has no workspace in release 1.0. | Scope control. The four workspaces come first. |
| D-038 | 2026-11-20 | The Guest OS is in scope, limited to Windows and Linux at the OS level. Applications inside the Guest OS are out. macOS is out. | IT owns the OS build standard (SP5 People: OS teams). Applications belong to their owners (D-034). macOS on ESXi is rare in enterprises. See Rationale. |
| D-039 | 2026-11-20 | The daily check is run by PCM, not by a person. It runs before the start and before the end of each region's business day. Platform (L2) owns the review, not L1. The human review takes about 10 minutes when there is no problem. Revised by D-083: the result is what Monitor shows for the 24-hour window; there is no daily-check page. | See Rationale. |
| D-040 | 2026-11-20 | L1 acts only through SOP buttons in PCM, never through vCenter. The L1 action set is small, reversible and set by class of service. | See Rationale. |
| D-041 | 2026-11-20 | Wall behaviour: a fixed status strip on every screen; red interrupts the rotation until acknowledged; stale data turns the wall grey, never green; with five or more displays, nothing rotates. | See Rationale. |
| D-042 | 2026-11-20 | PCM also runs the weekly check, a deeper analysis. It runs when load is low, by default Sunday early morning in each region's local time. Platform (L2) reviews the result in about 1 hour. Revised by D-083: the result is what Monitor shows for the 7-day window; there is no weekly-check page. | The weekly check loads the systems it reads. See Rationale. |

| D-043 | 2026-11-20 | The monthly review (1 day) is also the bigger team meeting: everyone meets to discuss important but not urgent matters, plan the next month, and review progress for the year against goals. PCM prepares the review pack; L2 (Platform) hosts it. Revised by D-083: the pack is Improve's decision register and Monitor at the estate root with the 1-year window, on one screen; there is no monthly page (L2 design, 6.4). | See Rationale. |
| D-044 | 2026-11-20 | A suspected breach is not investigated in PCM. L2 secures the evidence and hands it to the security team. Security is parked until after release 1.0. | "Is it breached?" is a forensic investigation, not troubleshooting (SP5), and needs security expertise (D-008, D-022). |
| D-045 | 2026-11-20 | L2 owns PCM's own settings (class-of-service definitions, action tiers) in release 1.0. After 1.0, the Operations Manager approves changes. | L2 knows what the settings do. A second approver comes with the Operations Manager workspace. |
| D-046 | 2026-11-20 | PCM is designed for a lean team of senior, highly experienced people. L2 is not 100% dedicated to operations; it also does architecture and engineering. Most routine and easy work is assisted by AI. | In the agentic AI era, the team is likely a few times smaller than today. |
| D-047 | 2026-11-20 | Agent E2 is a core team member, not a tool. Assume it knows vSphere, Windows, Linux, networking and the rest of the stack, even though today it knows only vSphere. | AI does the routine work the lean team (D-046) no longer has people for. |
| D-048 | 2026-11-20 | PCM assumes a two-layer organization. Today's top layers are cut the most. The middle layer becomes the new upper layer. | In a large IT organization with 8 layers, the top 3 are the highest paid and the furthest from ground reality: they neither do the work nor know the technology. AI removes the need for them first. |
| D-049 | 2026-11-20 | In release 1.0, "Is it safe?" shows VMware platform hygiene only: root logins, ESXi Shell or SSH enabled, lockdown mode off, certificates near expiry. No attack or breach detection (D-044). | These are configuration checks L2 already runs. They are among the most common causes of outages and audit findings in VMware estates. Health keeps its three questions (D-035). |
| D-050 | 2026-11-20 | Agent E2 cannot carry responsibility. Every task, action or change records two fields: the actor (a person, Agent E2's ID, or PCM running a policy) and the accountable party. For a person or Agent E2, the accountable party is the human who ordered it, which varies by task; Agent E2 can serve several managers at once. For an automatic run, it is the policy owner and the policy version. Revised by D-079. | Accountability stays with a person, and the action history answers "who ordered this", or "which policy, owned by whom", not only "what did it". |
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
| D-063 | 2026-11-20 | The audit log as a compliance record (retention policy, tamper evidence, export for auditors) is phase 2, with security and compliance. Release 1.0 keeps an operational action history: what was done, to which object, by whom (both fields, D-050), why, before and after. | See Rationale. |
| D-064 | 2026-11-20 | PCM has no collectors of its own. It reads through each region's VCF Operations, which already has a collector per region. PCM talks directly to vCenter and NSX only for actions (D-025) and for reads VCF Operations does not hold. | No duplicate collection: a second collector doubles the API load on every vCenter and adds a component to run in every region. |
| D-065 | 2026-11-20 | ACME Corp, the synthetic customer, is a global bank. | Banking load follows a strong calendar: end-of-day batch at night, payday, month-end, quarter-end and financial year-end close, which differs by country. Banks also face the strictest regulators, so recovery and safety stories carry weight with the approval audience. |
| D-066 | 2026-11-20 | Data residency is beyond release 1.0. Release 1.0 runs one central PCM that stores results from every region. | Scope control. Keeping detailed data in its region, with only model results sent to the central PCM, is the later option. |
| D-067 | 2026-11-20 | The synthetic data uses the present time. "Now" is an input to the generator: the demo uses the present, and each acceptance test passes a fixed "now". Stories are written relative to now and to the real calendar, never to a named date or weekday. | A live demo convinces more than a frozen one. Tests stay exact because each sets its own clock. |
| D-068 | 2026-11-20 | The NOC wall shows every location by default. Limiting a NOC to its region is a setting, not a separate design. An alert belongs to the region of its object; that region's shift acknowledges it. | See Rationale. |
| D-069 | 2026-11-20 | PCM groups alerts into one incident by object relationship and time, using fixed rules, not the LLM. L1 can split an incident; L1 cannot merge alerts by hand. | See Rationale. |
| D-070 | 2026-11-20 | The specification is organised as in `design/specification-structure.md`: `design/` holds the why, `spec/` holds the what. Pages name a catalog entry instead of defining numbers; every page and visual names its question, role and cadence; every state is specified, including stale; tests run at three levels (catalog, story, page); code is never edited by hand. | An AI builder implements what it is told and invents the rest. These rules leave it as little to invent as possible, and make each build checkable. |
| D-071 | 2026-11-20 | The prototype uses: Python standard library plus PyYAML for the data generator and the mock API; plain HTML, CSS, JavaScript and SVG for the pages, with no framework and no build step; Python unittest for catalog and story tests; Playwright for page tests. Generated code lives in `build/`. This choice is for the prototype only; the product stack stays deferred (PCM core, section 5). | See Rationale. |
| D-072 | 2026-11-20 | "Is it fast?" is a KPI, not an SLA. Performance has no target and no SLA (SP5). The Executive headline is the production KPI (average of VM daily KPIs, 0 to 100). Status uses only the SP5 bands and the SP5 class promise: red if any class group is orange or red; amber if any class group is yellow, or the order Gold, Silver, Bronze is broken; green otherwise. The earlier 99% target is withdrawn. | See `design/service-levels.md`, section 2. |
| D-073 | 2026-11-20 | "Is it safe?" is the SP5 Security SLA, measured as unsecured time per VM per calendar month, including the VM's surroundings (host, vSAN, distributed switch, vCenter, NSX Manager), with maintenance windows excluded. Contract 99.95% for every class; internal KSI 100%. Release 1.0 checks: SSH or ESXi Shell running, lockdown off, certificate expired, root login not yet closed by L2. A certificate expiring soon is a risk, shown beside the SLA. The card is red when any production VM is below 99.95% this month. Phase 2 adds the full benchmark with the same formula. | See `design/service-levels.md`, section 3. |
| D-074 | 2026-11-20 | Three rules from the first build's review: times are shown in the viewer's time zone with the zone named; a value that leaves out stale locations says which ones; no request leaves the PCM host, so fonts and scripts ship with the build. | A global team reads one page from several zones. A headline that changes without a reason looks like a real change. An on-premises customer may have no internet access (D-004). |
| D-075 | 2026-11-20 | Every red on the NOC wall belongs to something L1 can acknowledge. When a screen turns red with no alert behind it (unexpected VM changes, a risky configuration change), PCM opens a wall-finding incident with its own SOP. | Red stops the rotation until acknowledged (D-041). Inventory changes raise no alert (SP5), so without a wall finding a red "What changed?" screen could never be acknowledged, and the rotation would stay stuck. |
| D-076 | 2026-11-20 | For demos, Agent E2 calls a model through Vercel AI Gateway, as in Agent E2's own benchmark and lab. PCM talks to Agent E2's model through one OpenAI-compatible client: the endpoint and the model are settings. Customer sites point it at a local model server (D-004, D-017). | See Rationale. |
| D-077 | 2026-11-20 | "Is it up?" follows the SP5 Availability SLA: Operational Availability per VM per calendar month, against the class target (Gold 99.975%, Silver 99.95%, Bronze 99.9%). Downtime inside an approved change window does not count; downtime outside it counts, even when planned. PCM reads approved change windows from the ITSM change calendar through a connector, or from its own business calendar where no ITSM is connected. Actual Availability is shown in the drill-down. A VM breaches when its counted minutes exceed the allowance for the whole calendar month; the same rule now applies to the Security SLA. | See `design/service-levels.md`, section 4. |
| D-078 | 2026-11-20 | Agent E2 is a service behind PCM: it owns the knowledge base, the reading plan, the flow executor and the model call, behind one HTTP endpoint (`POST /v1/answer`, Agent E2 `harness/answer_service.py`). PCM owns the data, the actions, the user's identity and every screen, and sends the question with the live facts and the role. The Agent E2 repository becomes part of PCM eventually. | See Rationale. |
| D-079 | 2026-11-20 | Replace the trust ladder with policy as code. No "Make automatic" button and no promotion thresholds. The approval and rollback record per action type is evidence for L2, never a gate. L2 changes an action type's tier and guardrails through "Propose a policy change": versioned, replayed against recent history, owned (L2 in 1.0; the Operations Manager reviews after 1.0). Guardrails make automatic safe: blast-radius limits, maintenance windows, class-of-service conditions, automatic expiry and undo, and a service account scoped to the action type. | See Rationale. |
| D-080 | 2026-11-20 | The prototype keeps what people and policies do in SQLite: the action record (append-only), the demand register, and workflow state. Synthetic metrics are generated from "now" and never stored. Plain SQL, so the schema ports to the product database. This does not choose the product database (PCM core, 5). | See Rationale. |
| D-081 | 2026-11-20 | Detailed inventory matches every change to what explains it, in a fixed order: the PCM action record, an approved change window, a VCF Automation request, DRS. Explained changes are counted; unexplained ones are listed one by one, production and Gold first. L2 can record an unexplained change as expected, with a reason. | Tens of thousands of changes a week cannot be read one by one. L2's question is "is it expected?", so PCM answers it and shows only the exceptions. Details: L2 design, 4.7 and 5.7. |
| D-082 | 2026-11-20 | PCM `/docs` documents only what PCM owns and acts on: the definition of every number, SOPs, action policies, thresholds, configuration standards and settings, each with version, owner, where it is used and its change history. It is read-only: each object is changed in the workspace that owns it. Documentation for colleagues (architecture, decisions, guides, team structure, learning modes) is private-cloud-explained, a separate product. PCM exports its objects as Markdown into private-cloud-explained, through its review. | See Rationale. |
| D-083 | 2026-11-21 | L2 works in three activities, SP5's Day 2 verbs: **Monitor**, **Troubleshoot**, **Improve**. They are the top bar of the L2 workspace. Monitoring ends in a problem (→ Troubleshoot) or an opportunity (→ Improve). Daily, weekly and monthly are time windows, not activities and not pages: PCM still runs the checks (D-039, D-042), and Monitor shows their results by window. | See Rationale. |
| D-084 | 2026-11-21 | Every troubleshooting effort is a case, with one of three triggers: a complaint that L2 logs in PCM, an L1 escalation, or a monitoring finding. Escalation is a handover with entry criteria, not an activity. A case builds a chain of causes over several layers, as a graph: main and contributing causes, ruled-out links kept. It closes only with confirmed causes, a corrective action and a detection decision. | See Rationale. |
| D-085 | 2026-11-21 | Troubleshooting covers infrastructure only: server, storage as ESXi sees it, network, Windows and Linux. No application troubleshooting and no business transaction correlation. A chain starts at the Guest OS. When the evidence points outside scope (the Guest OS, the storage array, the application), the case hands the evidence to the owning team. | Follows D-030, D-034 and D-038. The infrastructure team can act on these layers; it can only hand over the others. |
| D-086 | 2026-11-21 | The L2 workspace has four dimensions, each in its own place: **activity** in the top bar; **object** in the left pane, where the inventory tree is the menu; **pillar** as tabs in Monitor and Improve (Summary, Availability, Performance, Capacity, Security, Configuration, Inventory); **time** as one picker per page. Troubleshoot has no pillar tabs: a case crosses pillars. Compliance is left out until after 1.0 (D-022). Cost, price and value are FinOps (D-027). | One menu that mixes time, activity and pillar tells the user none of them. vCenter and VCF Operations are the starting point; their top bar groups product functions, and their tabs mix pillars with types of data. L2 design, 3. |
| D-087 | 2026-11-21 | The inventory tree has five views: Compute (Estate → Region → Location → VCF instance → Workload domain → Cluster → ESXi host → VM → Guest OS), Storage, Network, Class of service, and Management (the appliances that run VCF). Attributes such as host model, firmware, ESXi build and Tools version are not trees; every list can be grouped by them. | Each view is a hierarchy operations uses; vCenter's datacenters and folders are admin constructs. SP5's two sides of VCF need the Management view. Grouping by attribute is how a shared cause is found across the estate. L2 design, 3.2. |
| D-088 | 2026-11-21 | Monitor works on the whole estate, top down: on every node, a summary, its children worst first, and the detail one level down. An object's score over a window is its 95th percentile. Monitor shows the count just below each red line and its trend, not only what crossed it. | SP5: insight is top down and needs the whole data set; an alert is the tip of the iceberg. Source: the author's sample dashboards in `sources/`. L2 design, 4. |
| D-089 | 2026-11-21 | Agent E2's flows decide the order of checks in a case: at each node the SP5 order, and a failed step proposes the next object. Agent E2 proposes links with evidence; L2 confirms or rules them out. Agent E2 never closes a case. | The flows are already written and benchmarked in Agent E2. PCM supplies the data; Agent E2 supplies the order (D-078). A human confirmation keeps a wrong link out of the SOPs (D-050). |
| D-090 | 2026-11-21 | The L2 demo's troubleshooting stories come from Agent E2's benchmark, renamed into the ACME estate: `L4-037` (complaint), `L4-074` (L1 escalation), `L4-049` and `L4-045` (monitoring findings). | Each has several layers, causes that build up over time, and red herrings. Together they show all three triggers. L2 design, 11. |
| D-091 | 2026-11-21 | The Performance tab above the cluster is two sections, consumer first: **VM**, then **Cluster**. VM: how many VMs were hit at each moment and how many different VMs over the window, and the worst VMs with the time and the cluster. Cluster: two charts on the same 0 to 100% scale, actual slowness (worst Cluster Performance and its 10th percentile) and potential slowness (worst Cluster Risk and its 90th percentile), the same metrics as vCommunity's Worst and Worst 10 Percent. A click on a time lists every cluster at that time. A class of service filter scopes both sections; Gold is the default. Monitoring shows what, when, where and how wide; never why. | Cluster Performance is built from its VMs' contention, so the consumer is read first. A large cluster can stay green while many of its VMs take turns. The worst line says whether anything is wrong; the percentile line says whether it is narrow or wide. Gold is the class that must always be green; Bronze is read when there is time. The why is the case's job (D-084). L2 design, 4.3. |
| D-092 | 2026-11-21 | The Performance tab of a VM shows detail, not a summary: two stacked layers of trend charts, **Guest OS** on top and **Virtual Motherboard** (the VM's virtual hardware) under it, because the Guest OS runs on the Virtual Motherboard. Each metric has its own chart over the window, and its figures say which statistic they are: now, worst, 95th percentile. Never an average. A VM page has no Group by and no Inventory tab, and the cards that count VMs go too: they describe a group. A number always carries its unit, after the number; a metric name is Title Case and never holds its unit; abbreviations are capitals (CPU, VM, OS). | A single figure such as "CPU Ready 2.5" does not say whether it is now, the worst or a percentile, and an average hides the peak that the VM's owner felt. The Guest OS is not beside the Virtual Motherboard: it is on top of it, and a wait in one shows in the other. Group by, the VM counts and Inventory describe more than one object. Rationale: D-092. |
| D-093 | 2026-11-21 | In the L2 frame the window is a drop-down, the pillars are tabs joined to a panel, and moving between pages does not load the page. The window list is Last hour, 24 hours, 7 days, 30 days, last year; a custom range comes later. Every tab shows its status dot on every page. The run line under the path is removed. | A pill row for time and a pill row for pillars looked alike, and a full page load on every click lost the tree and the scroll. See Rationale. |
| D-094 | 2026-11-21 | The L2 Capacity tab shows capacity over time and reads vCommunity's capacity model: **Cluster Consumption** (against usable capacity: total, minus HA, minus buffer), **Cluster Performance** (contention), **Cluster Risk**, and the **Periodic Cluster Check**'s Close for Business. **On a cluster:** the check's verdict and the rule that decided it, beside contention now (Cluster Performance over the last hour); one chart per KPI with the closure levels and the check's verdict under them; what consumption is made of; the spread between hosts; the hosts. **Above the cluster:** clusters closed per check; the highest Cluster Consumption and its 90th percentile; every cluster at a selected time; open clusters near closure; one class of service filter. PCM reads the check and never recomputes it or sets it. The tab shows no forecast, run-out date, decision date, Capacity Remaining or Time Remaining: those belong to the Capacity workspace. | A snapshot table cannot say whether 90% is rising, flat or one spike, and capacity is managed on its trend. vCommunity already decides, every period, whether each cluster takes new VMs; a second rule in PCM would give two answers for one cluster. A cluster is a group of hosts, so the page goes down to them. The boundary keeps two horizons apart: L2 answers "can it take more VMs now, and is it heading to closed?"; Capacity answers "when do we buy?". Rationale: D-094. |
| D-095 | 2026-11-21 | Which statistic, on which axis. **Over time, on one object:** a point holds the worst value of its slot (D-091); the figures are Now, Worst (with its time) and 95th percentile (D-092); the object's status over the window is its 95th percentile (D-088), and the worse of that and its last hour. **Across objects, at one time:** the worst object, and the 10th or 90th percentile at the bad end (D-091). **Never an average** on either axis, and never a sum or average of percentages across clusters. vCommunity's "Worst" check values are a percentile of the check period; PCM names them by what they are ("95th percentile, 24 hours to 08:00"), never "Worst". | The two axes answer different questions. Over time, one bad 5 minutes is too noisy to decide on, but it must stay visible: the chart shows every point and Worst names the peak. Across objects, the worst one is a real cluster with real VMs, and the percentile says how wide. One word for two statistics (vCommunity's Worst is a percentile, PCM's Worst is a peak) makes the same cluster read two ways. Rationale: D-095. |
| D-096 | 2026-11-21 | vCommunity is part of PCM, not a third-party source. PCM requires it, and it will be renamed the **PCM adapter**. Its metrics are PCM's definitions; its settings and thresholds are PCM settings, set in the adapter and listed in the catalog with their owner. PCM still reads them through VCF Operations (D-064), where the adapter runs. | The capacity model, the KPIs and the Periodic Cluster Check are already built in vCommunity. A second copy in PCM would give two answers for one cluster. Spec rule 6 holds: every threshold is a named setting; it is set in one place, the adapter. Rationale: D-096. |
| D-097 | 2026-11-21 | Agent E2 is on every L2 page, in one place. An **E2 mark** in the top bar says whether it is available; the same mark sits on each metric, KPI, finding, chain link and layer, where the question comes up. A click opens the **Agent E2 panel**, docked on the right: it pushes the content, never covers it, and the inventory tree folds to a narrow strip while it is open. PCM sends the facts of what was clicked; Agent E2 answers with its sources. The panel stays open across pages. Revises the L2 frame rule "no other item in the top bar". | The screen is full, and a panel on top would hide the chart being asked about. While L2 talks to Agent E2 they are not browsing the tree. An avatar mark, not a sparkle: Agent E2 is a team member who explains with sources (D-047), not magic. See Rationale. |
| D-098 | 2026-11-22 | The NOC desk has the same Agent E2 mark and panel as L2 (D-097): the mark in the top bar, on each tile, on the cluster drill-down, on each incident row, on the incident header and on each SOP step. PCM sends L1's facts (scores from 0 to 100, the SOP and its results) with the role l1. Every answer is checked against the NOC vocabulary; one that still uses an L2 word after one rewrite is not shown. "Explain this incident" and "Draft the escalation note" become the panel's first suggestions on an incident. The wall has no mark. | One mark and one panel for every workspace: an operator who moves to L2 already knows them. L1 must never get raw counters (NOC vocabulary), and must never be told to act outside the SOP (NOC design, 3.8). The wall has no mouse or keyboard (D-032). |
| D-099 | 2026-11-22 | In the Agent E2 panel an answer shows its sources behind a closed control, "Sources (n)", where n is the number of knowledge files it read. One click opens the list as chips. Applies to L2 and the NOC desk. Refines D-097 ("answers with its sources"): the sources are still there, one click away. | An answer reads 10 or more knowledge files. Showing them all as chips crowded a 400 px panel and pushed the answer and the footer out of sight. The file list is for checking an answer, not for reading it. |
| D-100 | 2026-11-22 | The L2 Performance and Capacity tabs lead with the object's KPI over time. **Performance:** on a VM the two Performance (%) scores (Guest OS Performance, VM Performance) come first, above the layers; on a cluster and anything under it, the object's own KPI as a trend chart (Cluster Performance and Cluster Risk, ESXi Performance), in place of the four summary cards. **Capacity:** on a VM, ESXi host and cluster, a summary first: Capacity Remaining (%) and Time Remaining (days), plus VM Remaining on a host and a cluster, read from VCF Operations, placeholder values in release 1.0. **KPI figures** (Now, Worst, 95th percentile) carry the band of their value. Revises D-092 (order of the VM tab) and D-094 (no Capacity Remaining or Time Remaining on L2), for VM, host and cluster only. | The author: the trend chart on the Capacity tab says more than four cards with one number each; the Performance (%) KPI is the main counter, so it goes first; L2 wants the remaining figures before the detail. |
| D-101 | 2026-11-22 | L2 percentages: Consumption, Performance and Risk (%) show whole numbers (63%, not 63.1%), because the decimal is not significant. A value above 0 that shows as 0 reads 0.0+% (0.00+% at two decimals), never a plain 0%. The Capacity tab's placeholder line under the summary is removed. | The author: a decimal on a KPI that moves by a fraction a day is noise; a tiny value must not read as exactly zero; the placeholder line added nothing the page did not already show. |
| D-102 | 2026-11-22 | Agent E2 panel: it is fixed to the window (below the demo bar when shown) and its answers scroll inside it. Each question with its answer is a fold: the newest open, older ones one line. The context label shows on a question only when it differs from the one above. | The author: a long answer pushed the panel off screen and could not scroll; the same context line repeated on every question. Cause of the first: `align-self: start` in l2.css shrank the fixed panel to its content. |
| D-103 | 2026-11-22 | Every question to Agent E2 carries the **screen**: who asks, the page (object, tab, window), what was clicked, what that card shows, the object a KPI belongs to when it is not the page's, and for a KPI where to look next (drill_down) with what PCM does not show yet. Whether a KPI moved enough to be a drop is Agent E2's to decide, from its knowledge base (a KPI change level per KPI) and its calculator, not PCM's. | Agent E2 answered "Why the worst at 18 Oct, 10:10?" on a steady Cluster Performance chart (80.2% to 82.2% all day) by explaining a "dip", spoke of "the provided JSON" to an engineer who had typed one line, and pointed at knowledge-base flows instead of a PCM tab. The model saw data, not a screen; and no rule said what size of move is a drop. PCM owns the screens (D-078), so it describes them; Agent E2 owns the domain knowledge. See Rationale. |
| D-104 | 2026-11-22 | Band figures do not write the band's name. A figure in a band (green, yellow, orange, red) is a tinted pill with a bar; the word GREEN, YELLOW, ORANGE or RED after it, in the figure and in the chart tooltip and the risk sentence, is removed, on every object. The four parts of Cluster Consumption (CPU Thread Utilization, Memory Consumed, Memory Ballooned, Memory Zip Swap, and Memory Tiering) now carry a band too, from the Agent E2 catalog knowledge/catalog/thresholds-capacity.yaml (band ends 55/70/85, 70/80/90, 1/2/4, 0.25/0.5/1, 25/50/75). Revises D-100 (the name beside the figure). | The author: the color already says it, the word repeats it. Exception to the rule that color is never the only signal; the pill and bar stay, and the author owns the call. |

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

### D-063 Action history in 1.0, audit log in phase 2

- The author parked the audit log with security and compliance (D-022, D-044).
- Several 1.0 decisions still need a record of each action. Without it, they do not work:
  - **D-040:** a limit on a villain VM expires and is undone automatically. The engine must remember what it set and when.
  - **D-050:** every Agent E2 task names the human who ordered it. That name must be stored to mean anything.
  - **L2 design, 6.3:** an action type earns automation through its record of approvals and rollbacks. No record, no automation.
  - **L2 design, 5.9:** escalations close with a cause and a fix. That history is what the monthly review reads.
- So the split is by purpose:
  - **1.0, the action history:** an operational record that the engines and people use day to day.
  - **Phase 2, the audit log:** the same events, with what an auditor needs: a retention policy, proof nothing was altered, and export to the security team's tools.

### D-068 Global wall, regional scope as a setting

- **Banks run both models.** Some run one central NOC, some run regional NOCs that follow the sun, and many run a mix: a central NOC with regional hubs, sometimes because a regulator expects local staff. PCM cannot assume one.
- **So scope is a setting, not a fork.** The same five screens and the same pages serve a global and a regional NOC. A fork would double what the specification must hold (D-010) for no gain in the experience.
- **Global by default, because some failures cross regions.** Examples: NSX Federation's global manager, identity services, the WAN between sites, or a bad configuration pushed to every region at once. A wall limited to one region shows each region a small problem and nobody the whole picture.
- **Ownership follows the object.** An alert belongs to the region where its object lives, and that region's shift acknowledges it. This holds even when the global wall shows it to everyone, so a red on a shared wall is never "someone else's".
- **Handover across regions uses the shift page** (NOC design, 3.9). In a follow-the-sun model, the handover note goes to the next region's shift, not only to the next shift in the same room.

### D-069 Alert grouping

- **Why group at all.** One host failure raises an alert for the host and for each of its 40 VMs. Forty-one items in the queue hide the one cause. SP5: L1 may group alerts rather than escalate each one.
- **Grouped by relationship and time.** Alerts join an incident when their objects are related, and they fire within a short window of the first alert. Related means a host and its VMs, a datastore and the VMs on it, or a cluster and its hosts. The relationships come from VCF Operations.
  - The incident is named after the parent object, the likely cause.
  - The escalation routes by that object's type (NOC design, 3.7).
- **Fixed rules, not the LLM.** L1 must be able to see why alerts were grouped. A rule ("VM alerts within 5 minutes of their host's alert") can be read and tested. An LLM grouping cannot, and a wrong grouping hides a second problem inside the first.
- **Split yes, merge no.**
  - **Splitting is safe.** If two alerts were grouped by coincidence, splitting shows more, not less.
  - **Merging by hand loses information.** It folds a second, unrelated problem into an incident that will be closed with the first problem's cause. The second problem then has no cause recorded and comes back.
  - A manual merge also breaks the rule that every alert closes with its own cause.
- **Grouping is tuned by L2.** The rules live in the catalog (PCM core, 3.6). A split by L1 is recorded, and frequent splits of the same kind tell L2 a rule is wrong.

### D-071 Prototype technology

- **Fewest moving parts.** The goal is approval (D-026), not scale. Each extra tool is one more thing that can fail during a demo or on a reviewer's laptop.
- **No framework and no build step for the pages.** The mockup is already plain HTML and SVG, and it is accessible. A framework would add a toolchain to install and update, and nothing the prototype needs.
- **Python standard library for the server.** It runs anywhere Python runs, which suits on-premises customers (D-004). It needs no package beyond PyYAML to read the specification.
- **The tests read the specification directly.** The expected values in `spec/tests/` are not copied into test code. Changing a test means changing the specification, which keeps D-070's rule that the specification is the only place anyone edits.
- **Not the product stack.** At 30,000 VMs and 13 months of history, the product needs a real database and a real server (PCM core, 3.3). That choice waits for the live system (D-062).

### D-076 Agent E2 in the demo, through Vercel AI Gateway

- **Why the gateway for demos.** The prototype runs on a laptop or a cloud session with no GPU. The gateway gives the same OpenAI-compatible interface the local server will give, so the code path is the one customers run. Only the endpoint changes. Agent E2's benchmark and lab already work this way.
- **Why this does not break "customer data stays on site" (D-004).** The demo sends only synthetic ACME data. Agent E2's lab already holds the same exception for the author's own lab data. Customer sites keep a local model and the rule.
- **The model is a setting.** The demo default is one of Agent E2's local candidates, not the frontier model. The approval audience should see what a customer would get on site, not a better model they will never run. The frontier model can be switched on for a comparison.
- **Agent E2 sees only what the person sees.** It gets facts from the PCM API with the permissions of the human who asked (PCM core, 3.12; D-050). It does not search the estate on its own.
- **Agent E2 drafts. It never decides.** It writes an explanation or an escalation note, marked as a draft. It does not set severity, press an SOP button or close an incident (NOC design, 3.8).
- **Its words are checked like a page's words.** The output is scanned against the workspace's vocabulary list. If it uses an avoided word, Agent E2 is asked once to rewrite. If it fails again, the page shows the fixed template instead. A model must not leak raw counters onto an L1 screen any more than a page may.
- **Each draft is recorded with both identity fields:** Agent E2's ID and the person who asked (D-050).
- **If the gateway fails, the demo still works.** The page shows the fixed template, labelled "Agent E2 is not available", never an empty box or an error.

### D-078 Agent E2 as a service behind PCM

- **Why a service, not shared code.**
  - Agent E2's own live-lab design planned a web server, login, a VCF Operations connector, a database and a UI. PCM already owns all of these, so building both would duplicate them.
  - A service boundary keeps each side testable on its own: Agent E2's benchmark measures the same pipeline PCM calls.
- **What crosses the boundary:** the question, the live facts as JSON and the role of the person asking. Back come the answer, the knowledge files it read and the facts it computed.
  - The facts arrive as data under a fixed heading, never as instructions.
  - Web lookup is off in the service, so live facts never reach a web search (D-004).
- **Two Agent E2 paths in PCM, for now:**
  - Short drafts (an incident explanation, an escalation note, an RCA draft) use the direct model client of D-076: fast, with facts only.
  - "Why" questions that need the knowledge base use the service: slower, about 30 seconds, but grounded in SP5 with sources.
- **Eventually one repository (author).** When Agent E2 moves into PCM, D-010 (the specification is the maintained artifact) meets a knowledge base that is the author's own writing, not generated. The knowledge base stays authored; only the code follows D-010. How and when the move happens is open.

### D-079 Policy as code, not a trust ladder

**Why the ladder was wrong**
- The first L2 design (3.7) let an action type "earn" automation: after enough approvals with no rollbacks, PCM offered a "Make automatic" button.
- That makes approval a counter. If a counter can decide that approval is no longer needed, approval was never doing any work: people were clicking through a step that carried no judgement.
- Automatic approval is a contradiction. If an approval can be automated, it is not needed, so it is removed from the policy instead.
- Approval logs that nobody reads add compliance bulk with no reduction in risk. The industry is moving to policy as code, guardrail governance and lean ITSM.

**What makes an automatic action safe: guardrails**

| Guardrail | Example |
|---|---|
| Blast radius | At most 10 VMs moved per cluster per hour |
| Time | Not inside a location's close week; only inside a maintenance window where the policy says so |
| Class of service | Only between clusters of the same class; only on non-production VMs |
| Expiry and undo | A limit expires at the end of the shift; every action has a defined undo |
| Service account | One account per action type, with only the rights that action needs (PCM core, 3.7) |

- The guardrails sit in the policy next to the tier. A run that breaks a guardrail is not run; it becomes a proposal for a person, with the guardrail named.

**How a policy changes**
- **"Propose a policy change":** L2 edits the tier and guardrails of one action type.
- **Replay:** PCM replays the proposed policy against recent action history and shows what would have run automatically, and what each guardrail would have stopped.
- **Publish:** the new version gets an owner and a time.
  - L2 owns it in 1.0.
  - After 1.0, the Operations Manager reviews it (D-045).
- **Rollback of a policy** is publishing the previous version again.

**The record per action type stays, as evidence only.** Approvals, rejections and rollbacks help L2 decide whether to propose a change. They never unlock anything by themselves.

**Accountability (D-050) for automatic runs:** the second field is the policy owner and the policy version, for example "policy move-vms v2, owner l2-engineer-1". There is no approval record for an automatic run, because no one approved it: the policy did.

### D-080 A small database for the prototype

**The problem it solves**
- The prototype kept everything people did in memory. A restart lost the demand register, escalations, published policies and the action record.
- A lost action record is the worst of these: D-079 makes the record the evidence, and evidence that disappears on restart is not evidence.

**Why SQLite**
- It ships with Python: no server, no install, no account. One file in `var/`.
- It is real SQL with constraints and triggers, so the database itself checks correctness:
  - the action record refuses UPDATE and DELETE (append-only);
  - a register entry needs a known kind, an owner, and at least one amount, none negative.
- Tests run on an in-memory database, so they never touch working data.

**What is stored, and what is not**
- **Stored:** what people and policies do. Actions, acknowledgements, escalations, closures, proposals, published policies and thresholds, calendar entries, limits, demand register entries.
- **Not stored:** synthetic metrics and planted stories. They are generated from "now" (D-067). Storing them would freeze the clock, and the stories would stop holding on another day.

**Trade-offs, accepted for now**
- Workflow state is one JSON document per name, not one table each. That keeps the prototype code close to what it was, so the time goes to functionality. The product gets proper tables.
- One process writes. A second PCM server on the same file is not supported.
- A reset for tests drops the action record. Nothing else can delete from it.

**What it does not decide**
- The product database stays open (PCM core, section 5). The schema uses only TEXT, INTEGER and REAL, and ISO 8601 times, so it ports to a relational product database without redesign. The append-only trigger has a direct equivalent there.

### D-082 PCM documents its own objects; private-cloud-explained documents the private cloud

**Why not one documentation product**
- The two products have opposite sources of truth. private-cloud-explained takes what people wrote (email, Confluence, Office files, meetings). PCM takes the live estate.
- Merging breaks both:
  - private-cloud-explained would need vCenter credentials. A read-only, low-risk site becomes a high-risk one, and its stated non-goal (no live connection) falls.
  - PCM would need an ingestion pipeline for documents. That is a large project with no operational value.
- The readers differ. private-cloud-explained serves every employee, in two tiers. PCM serves operations roles (D-011).

**Why PCM still needs `/docs`**
- Every number on every PCM page needs its definition one click away. A number nobody can explain is not trusted.
- PCM owns objects that act: an SOP drives L1's buttons, a policy decides what runs automatically, a threshold raises alerts. Their documentation must be the object itself, or the text and the behaviour drift apart.
- "Where is it used" answers the question before every change: which pages and which roles see a different number if this changes.

**Why read-only**
- Each object already has one place where it is changed, with a replay and a record: L2 publishes thresholds and policies, Capacity owns its settings. A second edit path in `/docs` would bypass them.

**What PCM exports to private-cloud-explained, and why**
- SOPs, action policies, thresholds and settings, and the inventory summary. These are the overlaps where a hand-written copy goes stale.
- PCM's SOPs start from an alert. In private-cloud-explained's content model that is a runbook, not an SOP. They are exported as runbooks.
- The export is Markdown with private-cloud-explained's front matter, and it goes through the same pull-request review as every other page.
- Two changes are needed on the private-cloud-explained side: a source type `pcm` and an origin `generated`. Neither exists in its content model today.

### D-083 Three activities, not three cadences

**What was wrong**
- The first L2 build had one menu row: Today, Weekly, Monthly, Escalations, Configuration, Inventory, Calendar, Thresholds.
- That row mixes three things: time (Today, Weekly, Monthly), activity (Escalations) and pillar (Configuration, Inventory).
- The landing page mixed the activities too: its top finding was a cluster "escalated to you by the NOC", an escalation inside a proactive check.

**Why activities**
- SP5 Monitor and Troubleshoot are different jobs: what against why, top down against bottom up, one KPI against many metrics, minutes against days, logs optional against logs required.
- SP5 Optimize is the third job: nothing is broken, but something can be better.
- A user needs to know first whether they are looking for problems, solving one, or improving.

**Why cadence is a window**
- Daily, weekly and monthly are when PCM runs and how far back it reads. The work is the same work: monitoring.
- A page per cadence repeats the same views with a different window, and teaches people to read the same finding three times.

### D-084 Troubleshooting is the activity; escalation is a trigger

**What was wrong**
- The first build investigated one object at one point in time: five steps, pass or fail, and it stopped at the first failure.
- Its stories had one link each: "Bronze VM in a Silver cluster", "the cause is inside the Guest OS".
- A complaint had no way in. Only L1 escalations existed.

**What troubleshooting is (SP5)**
- It starts with a complaint from users or a manager, or an escalation from L1 after its SOP, or a problem found by monitoring. It does not start with a raw alert: L1 handles alerts.
- The root cause is usually several layers down: A is caused by B, which is caused by C, which is caused by D.
- It is rarely a single chain. Several changes and events over weeks meet on one day. SP5's story: "it was not slow yesterday", but VMs were added for months and soft errors were investigated for weeks.
- The root cause is often on another object, and starts as a log message that never became an alarm.

**What PCM does**
- One case model for all three triggers, so every open problem is in one place, and the trigger mix measures prevention (L2 design, 2).
- The chain is a graph with link states (proposed, confirmed, ruled out), one timeline across its objects, and the layers each with its own verdict.
- Details: L2 design, 5.

### D-091 The Performance tab: consumer, then provider

**What was wrong**
- The tab showed one rolled-up score for the object ("68"), mixing two windows, with no unit and no direction.
- Its trend had no scale. "2 of 3 children outside green" counted regions, which says nothing.
- Region scores averaged their clusters, so a bad cluster read "Good" from above.
- No moment in time could be picked, so nobody could see which objects were hit together.

**Consumer first**
- Cluster Performance is made of consumer metrics: the worst VM and the 90th percentile of the VMs' CPU Ready, Co-Stop, memory and disk latency (vCommunity Cluster Performance).
- In a large cluster many VMs can be hit while the cluster stays green. The VM section shows it first.
- Different VMs taking turns is a cluster pattern. VMs hit at the same time point to something common. Different times point to one cluster or one VM.
- The VM owner may not have noticed yet. That is the point: proactive.

**Provider: two lines on one 0 to 100% chart**
- **Worst:** the lowest Cluster Performance of the clusters in scope at each time. Good means nothing is wrong. With every class in scope it equals vCommunity `Worst Cluster Performance` on vSphere World.
- **10th percentile:** the edge of the worst 10% of clusters (nearest rank). Bad too means a wide problem. Good means it is narrow: a few clusters, or one. With every class in scope it equals vCommunity `Worst 10 Percent Cluster Performance`.
- **Potential slowness** reads Cluster Risk, where higher is worse: the highest, and the 90th percentile (vCommunity `Worst Cluster Risk` and `Worst 10 Percent Cluster Risk`).
- 10%, not 5%, so PCM matches the metric vCommunity already publishes. vCommunity publishes it across all clusters, so for one class PCM computes the same metric from each cluster's score.

**Class of service**
- One filter for the whole tab. Gold by default: every Gold cluster is expected to score high. Silver and Bronze are read when there is time. All is the vSphere World view.
- A Bronze cluster runs hotter by design. Mixing classes would put Bronze at the bottom every day and hide a Gold problem.

**What, not why**
- Monitoring shows what was hit, when, where, and how wide. Whether a VM caused its own wait (a limit, too many vCPUs) is a cause, so it belongs to the case, not to this tab.

**Out of scope for 1.0**
- Kubernetes: a logical entity with its own view.

### D-092 The VM's Performance tab: two layers, with their statistic

**What was wrong**
- Guest OS and VM sat side by side, as if they were peers. The Guest OS runs on the Virtual Motherboard.
- Each metric was one number: "cpu ready percent 2.5". It did not say whether it was now, the worst of 24 hours, or a percentile. An average is no use here: a VM is felt at its peak.
- No unit after the number, lower case names, "cpu" for CPU.
- Group by, "Just above the line" and "Children outside green" count VMs. On one VM they describe a group.
- Inventory counts objects and their changes. It belongs to provider objects.

**Now**
- **Two layers, one over the other.** Guest OS first: Run Queue, Context Switches, Paging, Guest OS Performance. Virtual Motherboard under it: CPU Ready, Co-Stop, Memory Wait, Disk Latency, VM Performance.
- **One chart per metric,** over the window, one point per slot as in D-091: a point holds the worst value inside it. Beside it three named figures: Now, Worst (with its time), 95th percentile. No average.
- **95th percentile** is the value that 95% of the points were better than. For a metric where higher is better (the two Performance scores) it is the value that 95% of the points were above.
- **Unit after the number,** attached for % and per second ("2.5%", "7,346/s"), a space otherwise ("5.6 ms"). The name never holds the unit: "CPU Ready", not "CPU Ready %".

**Which tabs**
- VM, Guest OS, virtual disk and vNIC have no Inventory tab. Inventory stays on estate, region, location, VCF instance, workload domain, cluster, host, datastore and the other provider objects.

**Not changed**
- The case page keeps its own VM and Guest OS cards (case.md). Its layout is the case's decision.

### D-093 Window drop-down, pillar tabs, no page load

**What was wrong**
- Two rows of pills sat in one header, and the selected one in each was black. The reader could not tell which one titled the page below.
- Every pill was a link that loaded the whole page. The tree closed, the scroll went to the top, the fonts and scripts loaded again.
- Five fixed windows took the width of a row, and left no room for more.
- The status dot showed on the selected tab only, so a pillar page hid the state of the others.
- The run line under the path said which check run the page read. It was noise on every page.

**Now**
- **Window:** one light drop-down button. The list is Last hour, 24 hours, 7 days, 30 days, last year. A custom range comes later: it needs the API to take a range.
- **Tabs:** the selected tab and the panel are one shape. The tab is the panel's title.
- **Moving:** in-page. The address changes; the header, top bar and tree stay; the last click wins.
- **Dots:** on every tab, on every page.

**Not changed**
- The API still returns the run line's data. The page no longer shows it.
- The NOC and Capacity workspaces keep their pills. This is L2 only.

### D-094 The Capacity tab: three KPIs over time, and the check that closes a cluster

**What was wrong**
- The tab was one table of today's numbers: CPU and memory, average and 95th percentile across hosts, and an "imbalance". No time axis anywhere.
  - 90% memory cannot be read without its trend: rising for a week, flat for a year, or one spike last night.
- An average across hosts hides the hot host. The tab's own rule (D-092) forbids averages.
- "Imbalance" meant the spread between hosts. vCommunity's CPU Imbalance is a different metric: running threads per running core. One word, two meanings.
- A "Memory above 90%" chip had no rule and no finding behind it. The same page said "Nothing needs you under this object."
- The group page was the same table with more rows. Nothing showed how many clusters were closed, whether that count was rising, or how wide the pressure was.
- Utilization against total capacity is not consumption. HA and the buffer are not available to VMs (vCommunity capacity model).

**Why vCommunity's model**
- It is already built, documented and running: `docs/concepts/capacity-management.md` in VCF-vCommunity-Adapter.
- Three measures, one scale, one rule:
  - **Consumption:** how much of the usable capacity is used, cluster-wide.
  - **Contention:** whether VMs wait now. This is the SLA, and it caps consumption: no consumption level is safe if VMs wait.
  - **Risk:** how close the cluster is to contention, from its worst host.
- **Close for Business** turns them into a daily decision per cluster, closed when:
  - Consumption is red, or Contention is red;
  - or both are orange and Risk is orange or red.
- The levels sit inside the bands (80 and 60; 20 and 40), so a cluster does not flip on a small change.
- **PCM reads the decision; it does not make it.** A second implementation would give two answers for one cluster, and placement automation already reads vCommunity's.
  - PCM can say which rule matched: the three inputs are published beside the decision, and the rule is fixed.

**The check and "now" are both shown**
- The check reads the worst end of its period, ignoring the worst 5% of samples (70 minutes a day). It ignores a spike, and it decides once per period.
- So a cluster can be open at the check and have contention now. Story N-1: FR-S-02 fell to 22 twenty minutes ago.
- The tab shows both: the check's verdict, and "Contention now" from Cluster Performance in the last hour.
  - Not "VMs waiting": that reads as VMs queued for deployment. A deployment is never stuck on a closed cluster; placement picks another one.
  - The status is the worse of the two, as on every L2 row (l2.node_score).
- PCM does not recompute the check from the last hour. Stopping provisioning on a contended cluster is the NOC's SOP (D-040), not a capacity decision.

**On a cluster**
- **One chart per KPI,** in the rule's order: Consumption, then Performance, then Risk. Each shows the closure levels as lines, and its Now, Worst and 95th percentile (D-092, D-095).
- **The check's verdict** runs as a strip under the charts, one cell per check period, so a closure lines up with the KPI that caused it.
- **Under consumption:** its parts, each against usable capacity, and the usable capacity itself (total, HA, buffer).
- **Spread between hosts:** the busiest and the least busy host over time. A wide spread says DRS is not balancing; a pinned VM, affinity or reservations are typical causes. Why is the case's job.
- **The hosts,** worst first. A cluster is a group of hosts (source: `sources/Cluster Capacity v5.html`).

**Above the cluster**
- **Clusters closed,** per check period, with how many closed and opened since the previous check (vCommunity Cluster Delta Close and Open Count).
- **Highest Cluster Consumption and its 90th percentile** across the clusters in scope: the same two lines as D-091, the same meaning (vCommunity Highest Cluster Utilization and Highest 10 Percent Cluster Utilization).
- **Every cluster at a selected time,** closed first.
- **Near closure:** open clusters whose Consumption is above the orange closure level. This is the iceberg (D-088) for capacity.
- **Performance and Risk are not repeated.** Their spread is on the Performance tab (D-091). Here they appear per cluster, as inputs to its verdict.
- **Never a total.** No consumption is summed or averaged across clusters (Capacity design, 3.1).

**The boundary with the Capacity workspace**

| | L2, Monitor, Capacity tab | Capacity workspace |
|---|---|---|
| Question | Can this cluster take more VMs now, and is it heading to closed? | When does the group run out, and what do we buy? |
| Time | The window, up to now. No projection. | 13 months back, 13 months ahead. |
| Unit | One cluster, or the clusters under any node | The cluster group: location and class |
| Measure | Consumption, against usable (total, HA, buffer), as running | Weekly peak demand, against usable that also holds back a maintenance host, as planned |
| Output | Open or closed; a finding to Troubleshoot or Improve | Run-out date, decision date, purchase plan |
| Owner of the rule | vCommunity's check, read by PCM | The Capacity team (D-054) |

- The two usable capacities differ on purpose. Planning holds back a maintenance host before it happens. Running measures the hosts that run: a host in maintenance mode already drops out.
- L2 shows no run-out date, decision date, Capacity Remaining or Time Remaining. One sentence points to the Capacity workspace. Revised by D-100: a VM, host and cluster show VCF Operations' Capacity Remaining, Time Remaining and VM Remaining as a summary; a group still shows none.
  - A forecast on two pages becomes two forecasts.
  - Capacity Remaining in VCF Operations comes from its own engine, which reads at most 90 days (Capacity design, 3.5).

**Findings**
- **Closed at the latest check:**
  - closed with contention (Performance red, or rule 2): a problem, so Troubleshoot;
  - closed on Consumption alone: a risk, so Improve (rebalance, reclaim), with the Capacity workspace one click away.
- **Heading to closed** (7-day window): the check's Consumption drifts up, by the drift rule L2 already uses (l2.findings).
- **Every chip has a finding,** and every finding has a chip. A chip with no rule behind it is removed.

**Not in this step**
- PCM does not close the cluster in vCenter or VCF Automation. Placement reads vCommunity's metric.
- Storage space (D-057) is not one of the three KPIs. It stays with the datastore and the Capacity workspace (Capacity design, 3.13).

### D-095 Which statistic, on which axis

**What was wrong**
- Three rules existed, each right in its place, with nothing joining them:
  - D-088: an object's score over a window is its 95th percentile;
  - D-091: across clusters, the worst and the 10th or 90th percentile;
  - D-092: a metric's figures are Now, Worst and 95th percentile.
- vCommunity calls a percentile "Worst": Worst Cluster Consumption is the 95th percentile of the check period. PCM calls the single highest point "Worst". On one page the same cluster would show two different "Worst" values.

**The rule**

| Axis | Point | Figures | Status | Source |
|---|---|---|---|---|
| Over time, one object | The worst value in its slot | Now; Worst, with its time; 95th percentile | The 95th percentile over the window, and the worse of that and its last hour | D-088, D-091, D-092 |
| Across objects, one time | One value per object | The worst object; the 10th percentile (higher is better) or 90th (higher is worse) | Each object keeps its own | D-091 |

- **Nearest rank** everywhere, as vCommunity: sort, take the value at position p% of the count, rounded up.
- **The check value is a 95th percentile of the check period.** With a 24-hour period and Worst Percent 5, it equals the 95th percentile of that day's 5-minute points.
  - PCM labels it "95th percentile, 24 hours to 08:00", never "Worst".
  - If vCommunity's Worst Percent is changed, the label follows: Worst Percent 10 reads "90th percentile".
- **Never an average.** Not over time (it hides the peak the VM felt), not across hosts (it hides the hot host), not across clusters (it hides the full one).
- **Never a sum of percentages across clusters.** A data-centre figure hides which cluster is full (Capacity design, 3.1).

**Why not the worst point for status**
- One bad 5 minutes would turn a cluster red for the whole window. vCommunity ignores 70 minutes a day for the same reason.
- Nothing is hidden: the chart shows every point, and Worst names the peak and its time.

**Why the worst object across objects**
- The worst cluster is a real cluster with real VMs, not a statistical tail.
- The percentile line beside it says whether it is alone or one of many.

**Why the last hour too**
- A 24-hour percentile ignores a problem that started 20 minutes ago. The last hour is the NOC's view; L2 sees it as well.

### D-096 vCommunity is part of PCM

**What it changes**
- vCommunity was treated as an outside source PCM reads. It is PCM's own collection part: it computes the KPIs, the capacity model and the Periodic Cluster Check inside VCF Operations.
- Its name will change to the PCM adapter.

**Settings and thresholds**
- Spec rule 6 asks for every threshold as a named setting with an owner. The adapter's thresholds are those settings.
- **Set in one place: the adapter.** `catalog/settings.yaml` lists each one with its default, its owner and where it is set. PCM never holds a second value.
  - A second value in PCM could disagree with what the adapter already decided and published.
- **Owner:** L2 for the check and its closure levels (D-045); the Capacity team for the buffer (D-054), which VCF Operations' capacity policy applies.

**Not changed**
- PCM still has no collectors of its own (D-064). The adapter runs in VCF Operations and publishes there; PCM reads through VCF Operations.

### D-097 Agent E2 in the L2 frame

**The mark**
- "E2" in a small rounded square, like a colleague's initials. It says who answers, not that "AI" is here.
- In the top bar it shows whether the service answers (PCM asks `GET /v1/health`). Grey: not available. A grey mark on a card still opens the panel, which says so.
- On a card it sits at the right of the card's title, so the question and its object are one click apart.

**Why a panel, and why it pushes**
- Agent E2's own demos all keep the conversation in a right column. The L2 page has no free column.
- On top of the content, the panel would cover the right half of the chart being asked about.
- The tree is the menu (D-086). While L2 reads an answer they do not navigate; the tree folds to a strip and opens on hover or focus. The content loses about 50 px, not 400.

**Whole-page questions** (added the same day)
- The top bar mark asks about the page. On a VM's Performance tab, the page facts carry both layers' figures; on Summary, every pillar's status. Otherwise "Is this VM fine?" is answered without the numbers on screen.
- A mark on each layer heading sits between one metric and the whole page.

**Facts, not screenshots**
- PCM owns the data (D-078). It rebuilds the facts from what was clicked (object, tab, window, metric), never from numbers the browser sends.
- Agent E2 returns its sources, the values its code computed, and at most one round of clarifying questions.

**Not changed**
- Agent E2 explains, proposes and drafts. It never confirms a link, sets a severity, approves an action or closes a case (L2 design, 8).
- Every question is recorded with Agent E2 as the actor and the person who asked (D-050).

### D-098 Agent E2 at the NOC desk

**Same mark, same panel**
- One mark and one panel in every workspace (D-097). Shared code; each workspace says only what its pages send and suggest.
- On the desk the content has no tree to fold. The panel pushes the content: the page gives up 400 px on the right.

**L1's words, not L2's**
- Agent E2's knowledge base speaks Level 400: CPU Ready, latency in ms. The NOC vocabulary bans those words on L1 screens.
- PCM sends the role l1 and adds the rule to the question: scores from 0 to 100, plain words, follow the SOP, never these words.
- PCM checks the answer. One that uses an avoided word is asked for once more, naming the words. If it fails again, the panel says so and shows no answer, and points to escalation. A wrong word on an L1 screen is worse than no answer: L1 cannot check it.

**The drafts stay drafts**
- "Explain this incident" and "Draft the escalation note" keep their own path (D-076): the direct model call with the fixed template behind it. In the panel they are the first two suggestions on an incident.

**Not changed**
- Agent E2 does not set severity, choose an action outside the SOP or close an alert (NOC design, 3.8). The panel has no action button.

### D-100 The KPI first: Performance and Capacity tabs

**What was wrong**
- On a cluster or host the Performance tab opened with four cards: the score, a sparkline with no axis, "Children outside green" and "Just above the line". One number each, no time axis. The Capacity tab already showed its KPIs as trend charts, and they read better.
- On a VM the two Performance (%) scores sat last in their layers, under the counters. They are the KPI: they say whether anything is wrong. The counters say where.
- A KPI's Now, Worst and 95th percentile were plain black numbers. Whether 52.4 is fine had to be read off the chart's bands.
- The Capacity tab went straight into the cluster's detail. On a VM or a host it opened with the cluster's verdict, not with the object asked about.

**Now: Performance tab**
- **On a VM:** a Performance section first, Guest OS Performance then VM Performance, stacked, each with its chart and figures. Then the two layers, each with its counters only. The layer chips stay; the layer order stays (D-092).
- **On a cluster and anything under it, not a VM:** the object's KPI over the window, the same chart and figures as the Capacity tab. Cluster: Cluster Performance, then Cluster Risk. ESXi host: ESXi Performance. Datastore and resource pool: Worst VM Performance (they have no KPI of their own; l2.node_score). Port group: its cluster's.
  - Cluster Performance on both tabs is one series (l2.cluster_kpi_series), so the two tabs show one number for "now".
  - "Children outside green" becomes one sentence; the children table under it is already worst first.
  - "Just above the line" becomes a chart: VMs between 75 and 80, one point a day for 7 days, with its count and direction in words.
- **Above the cluster:** unchanged (D-091).

**Now: band figures**
- Now, Worst and 95th percentile of a 0 to 100% KPI (the Performance scores, Cluster Consumption, Cluster Performance, Cluster Risk) show the band of their value: green, yellow, orange, red.
- Visible on white: a tinted pill with dark text of the same hue (6.2:1 to 7.5:1), a bar in the band color, and the band's name. The band yellow on white is 3.0:1, too faint for text, so no figure is written in a band color.
- Counters without bands (CPU Ready, Disk Latency, the parts of Consumption) stay black. No threshold is invented for them.

**Now: Capacity tab**
- **On a VM:** Capacity Remaining (%) and Time Remaining (days). **On an ESXi host and a cluster:** the same, and VM Remaining. Then the cluster's page as before (D-094), headed with the cluster's name on a VM or host page.
- **Source: VCF Operations,** its own capacity engine. PCM shows the values; it does not compute them (spec rule 1).
- **Release 1.0: placeholder values,** stable per object, and the page says so under them. The real values replace them when PCM reads VCF Operations (D-062).
- **Above the cluster:** unchanged. No Capacity Remaining, Time Remaining or VM Remaining on a group (D-094).

**What D-094 warned of, and how it is held**
- A forecast on two pages becomes two forecasts. VCF Operations' Time Remaining reads at most 90 days; the Capacity workspace's forecast reads 13 months. They can disagree on the same cluster.
  - The L2 figures name their source, VCF Operations. The purchase decision stays in the Capacity workspace, and the tab's one sentence still points there.
  - Open: when the connector is live, compare the two for the same cluster. If they disagree often, the author decides which one L2 shows.

**Not changed**
- The cluster's verdict, the three KPI charts, the check strip, the parts, usable capacity, the host spread and the hosts table (D-094).
- No average anywhere (D-095).

### D-103 Agent E2 sees the screen, not the data

**What went wrong (2026-11-22, VM fr-bat-6839, Capacity tab, Cluster Performance of FR-B-04, last 24 hours)**
- The question: "Why the worst at 18 Oct, 10:10?". The answer: "The cause of the performance dip cannot be identified with the provided data", then three steps from the knowledge base.
- Three errors. There was no dip: the line held 80.2% to 82.2% all day, all green, and the check the day before read 80.4%. The answer named the 9 sub-metrics but not where L2 can look in PCM. And it spoke of "the provided JSON" to a person who typed one line.

**Where each fix lives**
- **The screen: PCM.** Only PCM knows the page, the tab, what was clicked and what the card shows. It sends a `screen` block with every question (frame.md, Agent E2 panel).
- **Where to look next: PCM.** A KPI's drill_down names the page and tab and what PCM does not show yet. Today the sub-metrics of Cluster Performance are on no PCM page; the cluster's Performance tab shows the KPI and the hosts worst first.
- **What counts as a drop: Agent E2.** A KPI change level per KPI in its catalog (Cluster Performance: 5 points from the median of the window), the rule in its knowledge base, and a calculator that reads the points PCM already sends and boxes the verdict under "Computed, not written by the model". PCM computes no verdict: one owner for domain knowledge (D-078).
- **How Agent E2 speaks to a screen: Agent E2.** Its service tells the model the person sees the page, not the data, and rewrites once an answer that still says JSON, payload or "the data provided".

**Not done**
- No sub-metric chart for Cluster Performance on any PCM page. If L2 needs it to answer "which resource moved", it is a page change, decided separately.
- PCM's red and orange levels for the cluster KPIs stay in PCM's settings. If a PCM page ever marks a drop on a chart, it reads the change level from Agent E2, not a copy.

