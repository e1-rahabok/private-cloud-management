# Service levels: is it fast, is it safe

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

Source: the SP5 framework in the Agent E2 knowledge base, in particular:
- `sp5-framework/concepts/sla-metrics`
- `sp5-framework/performance/kpi-vs-sla`
- `sp5-framework/performance/performance-kpi-design`
- `sp5-framework/concepts/class-of-service`

This document sets how PCM answers "Is it fast?" and "Is it safe?" for every workspace. The Executive page is the first user.

## 1. The SP5 rules that apply

- **An SLA is a contract between two parties**, with a metric, an object, a target, a window and a penalty. An intention without a number is not an SLA.
- **An SLA is only on the consumer's object:** the VM or the pod. Never on a cluster, an ESXi host or a management component. Provider objects carry a KPI and a KAI, never an SLA.
- **An SLA is monthly, on the calendar month.** A yearly window allows the longest outage. A daily window leaves no room for error.
- **Promise and reality are different numbers.**
  - The promise is one number per class of service.
  - The reality is one number per VM, calculated at month end. A Gold VM can fail while a Bronze VM passes.
- **Operations do not run on the SLA.** Each pillar has its own operational indicator:
  - performance: KPI;
  - availability: KAI;
  - security: KSI.
- **The IaaS contract has three SLAs:** availability, security and service. **Performance has none.**

## 2. "Is it fast?" is a KPI, not an SLA

### 2.1 Why there is no target

- SP5: "Performance has no SLA: fast is defined by the KPI." No SLI, no SLO.
- **The 99% target I proposed was an SLA under another name.** I withdraw it. Its settings `fast.target_percent` and `fast.amber_margin_percent` are removed.
- **Why SP5 is right.**
  - The provider's compute is only part of the path. Storage and network are partly outside its control, so even Gold with no CPU overcommit cannot promise perfect performance.
  - A contract counts pass or fail once a month against one line. Performance needs "how bad, now, on which object".
- **The KPI is a baseline, not a target.** It has one set of levels for every class:
  - green 100–75
  - yellow 75–50
  - orange 50–25
  - red 25–0

  The levels and the per-metric limits come from the Agent E2 catalog `thresholds-performance`, so nothing is invented here.

### 2.2 What the class of service promises

- The promise is **relative contention**: Gold 1x, Silver 2x, Bronze 3x.
- It is not a minimum KPI per class. Gold scores higher because its design causes less contention: less overcommit, more reservation, more shares.
- **SP5's check of the promise:** group the VMs per class and compare the group KPIs. Gold should score above Silver, and Silver above Bronze.

### 2.3 Definition for PCM

| Entry | Definition |
|---|---|
| VM daily KPI | VM Performance (%) for one VM and one day: the 99th percentile of the day's 288 scores, counted from the worst. The 2 worst intervals are ignored. SP5: never the average of the day. |
| Class group KPI | The average of the daily KPIs of the production VMs in one class, over the window. SP5: "a super metric that averages each group's KPI". |
| Production KPI | The same average over all production VMs. This is the Executive headline. |
| Promise kept | Gold group KPI ≥ Silver ≥ Bronze. |

**Status rule for the Executive card**

| Status | Rule | Why |
|---|---|---|
| Red | The lowest class group KPI is in the orange or red band | A whole class is getting a poor service. |
| Amber | The lowest class group KPI is yellow, **or** the class order is broken | Either a class is degrading, or a lower class is being served better than a higher one, which means the price difference is not delivered. |
| Green | Every class group KPI is green, and the order holds | |

- **The status uses only SP5 bands and the SP5 promise.** No new threshold.
- **The order check matters to the CIO.** If Bronze scores above Gold, the bank is paying Gold prices for nothing. That is a value question, not only a performance one.
- **Window:** the last 7 days, with 30 days in the drill-down. The KPI is read daily (SP5), so a calendar month is too slow for it.

## 3. "Is it safe?" is a Security SLA, measured as unsecured time

### 3.1 The SP5 definition

| Item | SP5 |
|---|---|
| Name | Security SLA, not Compliance SLA. It covers settings and activity. |
| Metric | Secured time: the share of the month the VM was compliant with the agreed security policy or benchmark |
| Object | The VM, including its surroundings: if its ESXi host, vSAN, distributed switch or storage is not secure, the VM's score reflects it |
| Nature | Binary at each moment: compliant or not |
| Window | Calendar month. The maintenance window is always excluded. |
| Contract value | 99.95%, the same for every class. Not 100%: a contract with 100% is broken by a one-second-old reading. |
| Internal KSI | 100%. A non-compliant setting can be a door for an attack. |
| Excluded | What the provider does not control. |

- **Allowed unsecured time at 99.95%:** 21.6 minutes in a 30-day month (SP5 time window table).

### 3.2 Formulation for PCM

```text
Secured time (%) of one VM, one calendar month
  = (minutes in month − unsecured minutes outside maintenance windows) / minutes in month × 100

A minute is unsecured when, at that minute, any check fails for the VM or its surroundings:
  - its ESXi host, the vSAN cluster and datastore it uses, its distributed switch and port group;
  - the vCenter and NSX Manager that manage them.
```

**The benchmark grows by phase. The formula does not change.**

| Phase | Checks | Kind |
|---|---|---|
| 1.0 | ESXi Shell or SSH running; lockdown mode off where the standard requires it on; a certificate expired on the host, vCenter or NSX Manager | Settings |
| 1.0 | A root login on the host outside the maintenance window. Unsecured from the login until L2 closes the finding with a reason. | Activity |
| 2 | The full benchmark: the vSphere security configuration guide, CIS, DISA, PCI DSS, the internal standard | Settings, with compliance (D-022) |
| 2 | Guest OS compliance (Group Policy, configuration management), if the Guest OS is in the service | Settings |

**Why these choices**
- **Surroundings count.** A VM on a host with SSH open is exposed, whatever its own settings say. SP5 says so explicitly.
  - It also makes the number honest for the platform team. Most of what makes a VM unsecure in a VMware estate is on the host or the management plane, which the platform team owns.
- **Activity counts until explained.** SP5: security covers activity, not only settings.
  - A root login is not a failure in itself; it can be legitimate. But until someone has said why it happened, nobody knows.
  - Counting the time until L2 closes it rewards quick review. It also makes a forgotten review expensive, which is the point.
- **A certificate expiring soon is a risk, not unsecured time.** SP5 separates present health from risk (future health).
  - An expired certificate is unsecured now.
  - A certificate expiring in 21 days is a warning. It is shown next to the SLA, not inside it.
- **The maintenance window comes from the business calendar** (L2 design, 3.6). SSH turned on for patching inside the window is agreed change, not a breach. Turned on outside it, the time counts.
- **Phase 1.0 is a small benchmark, with the same formula as later.** When compliance arrives in phase 2, more checks feed the same number. The Executive page, the trend and the goals keep their meaning. Starting with a different formula would break the trend when phase 2 arrives.

### 3.3 Reading it: promise, reality, KSI

| Number | Scope | Target | Who reads it |
|---|---|---|---|
| Security SLA, reality | Per VM, per calendar month | 99.95% (contract) | Monthly review; Executive drill-down: how many VMs are below |
| Security KSI | Production VMs, weighted by minutes | 100% (internal) | Executive headline, L2 |
| Open findings | Now | 0 | NOC "Is it safe?" screen, L2 |
| Risk | Next 30 days, for example certificates expiring | 0 | L2, Executive sentence |

**Status rule for the Executive card**

| Status | Rule | Why |
|---|---|---|
| Green | KSI is 100% this month: no unsecured minute | The internal target is met. |
| Amber | KSI below 100%, but every production VM is still at or above 99.95% for the month | The contract holds, but the internal target was missed. |
| Red | At least one production VM is below 99.95% for the month | The contract is broken for that VM. Within a month this cannot recover, so red is honest from the moment it happens. |

**Why the VM-level rule decides red, not the estate average**
- An estate average of 99.99% hides 72 VMs that were exposed for 8 hours.
- SP5: the reality is per VM. The application owner whose VM was exposed does not care that the estate average looks fine.

## 4. Proposal: align "Is it up?" with the Availability SLA

- Today the Executive "Is it up?" card uses a 7-day estate figure against 99.95%, taken from the mockup. That does not follow SP5. SP5 says:
  - the availability SLA is per VM, per calendar month, as **operational availability**;
  - it is measured on the Guest OS answering ping, since the Guest OS is in scope (D-038);
  - the target depends on the class: Gold 99.975%, Silver 99.950%, Bronze 99.900%.
- **Proposal: the same shape as "Is it safe?":**
  - headline: KAI, production VM operational availability this month;
  - red when any production VM is below its class SLA for the month;
  - amber when below 100% but every VM is within its class SLA;
  - green at 100%.
- I have not changed it yet. The author confirmed only the other three settings. **This needs the author's yes.**
