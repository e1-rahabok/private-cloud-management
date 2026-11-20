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
| D-007 | 2026-11-20 | PCM replaces the VCF Operations presentation layer for capacity, cost, performance, inventory, configuration, compliance and availability management. | These are the operations areas PCM serves by role. |
| D-008 | 2026-11-20 | Out of scope: VCF lifecycle management (the SDDC Manager part) and security operations. | Lifecycle is Broadcom software management. Security operations is a different field with different expertise. |
| D-009 | 2026-11-20 | New capabilities: an executive dashboard, multiple VCF Operations instances, and documentation for the private cloud. | Starting points: [VMW-Executive-Dashboard](https://github.com/e1-rahabok/VMW-Executive-Dashboard), [VMW-Federated-VCF-Operations](https://github.com/e1-rahabok/VMW-Federated-VCF-Operations), [private-cloud-explained](https://github.com/e1-rahabok/private-cloud-explained). Ideas are also borrowed from https://isvara.io. |
| D-010 | 2026-11-20 | The specification is the maintained artifact. AI writes 100% of the code. Developers do not maintain code. | Generating code is cheap. The specification is what has to stay correct. |
| D-011 | 2026-11-20 | Each role gets a workspace with its own URL. Workspaces share no menu. | One common UI for all roles weakens the experience for each of them. |
| D-012 | 2026-11-20 | First four workspaces: **NOC**, **Performance Management**, **Capacity Management**, **Executive**. | Together they cover the range from live operations to executive review. |
| D-013 | 2026-11-20 | NOC: a few pages. L1 operators have simple needs and follow the SOP. | L1 work is SOP-driven. |
| D-014 | 2026-11-20 | Capacity Management runs weekly, not daily. It includes what-if analysis and hardware refresh. | Capacity decisions follow a weekly cadence. |
| D-015 | 2026-11-20 | Executive: one page, with drill-down to the next level. The [Executive Dashboard export](https://e1-rahabok.github.io/VMW-Executive-Dashboard/design/export/) is the starting point. | The CIO has no time for detail. |
| D-016 | 2026-11-20 | PCM takes actions, not only reads. | Operations work needs action, not only viewing. |
| D-017 | 2026-11-20 | PCM includes a local LLM, for example Agent E2. | On-premises only (D-004). |
| D-018 | 2026-11-20 | The prototype uses synthetic ACME data. A lab with a full VCF 9.1 instance follows later. | No customer data is needed for the prototype. |
