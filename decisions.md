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
| D-031 | 2026-11-20 | L1 works in three shifts; someone always watches. No mobile push for L1; mobile push is for L2. | The NOC is staffed 24x7, so L1 does not need to be paged. |
| D-032 | 2026-11-20 | L1 has two UIs. **Wall screen**: a large TV that streams the present, with no mouse and no keyboard; it auto-rotates about every 60 seconds through Inventory, Availability, Performance, Security, Compliance, Configuration. **Desktop dashboard**, assisted by Agent E2. Live screen practice: https://isvara.io/read/part-2/proactive-operations | A static screen bores the viewer. The wall is for watching; the desk is for working. |
