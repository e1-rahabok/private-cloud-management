# NOC workspace

Status: draft for the author's review. This document gathers the NOC decisions (D-013, D-030 to D-036, D-040, D-041, D-049, D-050) in one place, with their reasons, and adds what they leave open. New proposals move to [`decisions.md`](../decisions.md) once accepted.

Path: `privatecloud.acme.com/noc` (D-028).

## 1. The role

- **Level 1 operators** (SP5 People):
  - deal with the production environment;
  - perform simple troubleshooting by SOP, usually without reading logs;
  - close alerts only when the cause is known;
  - focus on availability, performance and safety.
- **Three shifts.** Someone is always watching, with fewer people per shift than today (D-031, D-046).
- **No mobile push.** The NOC is staffed; push is for L2 (D-031).
- **Junior, and follows the SOP.** L1 sees health as three plain questions (D-035).
- **Two UIs** (D-032):
  - the wall, a TV with no mouse and no keyboard;
  - the desktop, assisted by Agent E2.
- **Scope:** VMware infrastructure only (D-030, D-034). No end-user help desk, no business transactions.

**Why this workspace matters**
- The NOC is the only role that watches every minute of every day.
- If the NOC misses a red, nobody else sees it until a customer calls.
- If the NOC escalates noise, L2's time goes to triage instead of prevention. L2 also does architecture and engineering (D-046), so that is time it cannot spare.

## 2. What the NOC is measured by

| Outcome | Measure | Why it is the right measure |
|---|---|---|
| Nothing missed | Reds acknowledged within minutes, on every shift | The wall exists to make red impossible to miss. |
| Good escalations | Share of escalations L2 accepts without asking for more | SP5: L2 does not accept an escalation without its context. A rejected escalation costs both teams time. |
| Known problems solved at L1 | Share of alerts L1 closes by SOP, without L2, trend over months | Each solved problem should become an SOP that L1 can run (L2 design, 3.8). |
| Alerts closed with a cause | Share of alerts closed with a root cause, not because the symptom went away | SP5: closing without knowing why prevents learning and can backfire. |

## 3. Design considerations

### 3.1 The wall answers five questions, in a fixed order (D-035, D-036)

| Screen | Question | What it shows | Why this content |
|---|---|---|---|
| 1 | **What changed?** | VM changes in the last hour against what is expected: created, deleted, powered off, moved, resized. Planned work from the business calendar is excluded. | SP5: many VMs deleted while no deletion is planned means something is wrong. Inventory gets no alert (SP5), so the wall is where unexpected change is seen. |
| 2 | **Is it up?** | Per location: VMs down without a plan, hosts not responding, clusters that lost HA failover capacity, VCF management components down, datastores unreachable | A system that is down has no performance or safety problem. Mostly from events and logs, not metrics (SP5). |
| 3 | **Is it fast?** | Per cluster, as a heat map: the share of VMs not served well (Cluster Performance %). The top "villain" VMs, those using the most, and "victim" VMs, those waiting the most. | SP5 L1 dashboards: "Is our IaaS performing?" If 10% of a cluster's VMs are not served, the tile turns fully red. Victims and villains give L1 a direct starting point. |
| 4 | **Is it safe?** | Platform hygiene only (D-049): root logins, ESXi Shell or SSH on, lockdown mode off, certificates near expiry | Security operations is after 1.0 (D-044). These are the safety items L1 can act on, or escalate, the same day. |
| 5 | **Is it set right?** | Configuration changes in the last hour that break the standard; high-risk settings only | SP5: configuration alerts are for high-risk settings only. A live drift is caught on the day it happens, not the next morning. |

- The order follows SP5: first what exists, then up, fast, safe, and finally what may cause tomorrow's problem.

### 3.2 Wall rules (SP5 live screen, D-041)

- **Zero interaction.** No buttons, filters or menus. Nobody can click a TV.
- **Large numbers, scores from 0 to 100%.** Designed on a 14-inch screen to get the real space.
  - SP5: give L1 scores from 0 to 100%, not raw counters, which need context to read.
- **Now.** The last 5 minutes, with the next hour projected where possible. Refreshed every minute.
- **All green by default.** Red only for what L1 can act on the same day. A tile that is often red is ignored.
- **The 5-second test.** A screen nobody can read in 5 seconds is redesigned, not explained.
- **Fixed status strip.** All five questions are always visible as chips, one per screen.
- **Red stops the rotation** until it is acknowledged on the desktop, not until it clears.
  - Several reds: the rotation cycles through the red screens only.
- **Stale data is grey, "No data", never green.** A grey screen is itself something L1 escalates.
- **No rotation on a wall of five or more displays.** Each question gets its own display.
- **PCM's own health is shown.** If PCM is down, the wall says so, and the SOP falls back to the native VCF Operations screens (PCM core, 3.11).
- **Not for visitors.** If the CIO visits, a separate view is shown for the visit. It does not stay on the wall.

### 3.3 The desktop: the same five screens, plus the work

- **What:** the desktop opens the same five screens with drill-down: from a red tile to the cluster, then the hosts, then the VMs. Around them sits the work: alerts, SOPs, escalation, the shift.
- **Why:**
  - **The wall and the desk must say the same thing.** An operator who sees red on the wall and green on the desk stops trusting both.
  - **Drill-down is top down,** the same order L2 uses (L2 design, 3.3). An escalation then starts where L2 would start.

### 3.4 Only urgent alerts reach the NOC

- **What:**
  - The NOC alert list holds red alerts (act within 1 to 2 hours) and orange alerts (act by the end of the day).
  - Yellow is not an alert. It is an insight for the daily check (D-039).
  - PCM groups alerts on the same cause into one incident. Example: one host failure, not 40 VM alerts.
- **Why:**
  - SP5: an alert must be rapid, real and rare. Yellow is a symptom, possibly a false positive. Sending it to L1 teaches L1 to ignore alerts.
  - Grouping lets L1 handle the cause once instead of escalating each symptom. SP5: L1 may group alerts rather than escalate each one.

### 3.5 The SOP is the page

- **What:** opening an alert opens its SOP as a sequence of steps:
  - **Diagnosis steps** show live data and mark each check pass or fail.
  - **Action steps** have buttons. Each button is allowed or not by the action tier (D-029) and the L1 action set (D-040).
  - **Verification** re-checks automatically after an action.
- **Why:**
  - SP5 People: SOPs are ideally automated and take inputs, so human error stays low.
  - The SOP L1 reads and the buttons L1 presses are the same object, so they cannot drift apart.
  - When L2 updates the SOP after solving a problem (L2 design, 3.9), the NOC sees the new steps at once.

### 3.6 L1 acts only through PCM, within a small set (D-040)

| Action | Scope |
|---|---|
| Acknowledge, annotate, escalate | Any alert |
| Close an alert | Only with a root cause chosen from a list |
| Stop provisioning on a cluster, and reopen it | Cluster |
| Time-boxed limit on a "villain" VM, removed by PCM at expiry | Non-production VMs only |
| Restart an unresponsive VM | Non-production VMs only, and only when the VMware Tools heartbeat is lost |

- **L1 never logs in to vCenter.** Every action runs through the action engine (PCM core, 3.7) and is written to the action history (D-063).
- **Why:**
  - Every L1 action is reversible and limited in reach.
  - A shift of junior operators with vCenter admin rights is how large estates get unexplained changes at 03:00.
  - Not for L1, with reasons in D-040: manual vMotion, host maintenance mode, snapshot deletion, any configuration change.

### 3.7 Escalation arrives complete, at the right L2 group

- **What:**
  - One button escalates.
  - PCM fills the L1 exit criteria, which are the L2 entry criteria (SP5):
    - the VM owner;
    - the steps already run and their results;
    - the "on my court" metrics for that object type.
  - PCM routes the escalation by object type to the right L2 lens: platform, storage or network (L2 design, 3.11).
- **Why:**
  - SP5: L2 does not accept an escalation without its context.
  - L1 is a generalist and often cannot tell which specialist group to escalate to. PCM can, from the object type.
  - Automatic evidence makes rejection rare. When a rejection does happen, it points to a gap in the SOP, not to the operator.

### 3.8 Agent E2 at the NOC desk

- **Agent E2 may:**
  - explain the alert in plain words;
  - point to the SOP;
  - run diagnosis steps;
  - draft the escalation note.
- **Agent E2 acts with the limits of the operator who asked it** (D-050). The action history shows both fields: Agent E2's ID and the operator's name.
- **Agent E2 does not:**
  - set severity;
  - choose an action outside the SOP;
  - close an alert.
- **Why:** L1 is junior and follows the SOP. An assistant that goes beyond the SOP would make L1 depend on judgement that L1 cannot check.

### 3.9 The shift page: handover, not the daily check

- **What:** `/noc/shift` holds:
  - what is open;
  - what was acknowledged and by whom;
  - what is waiting on L2;
  - the handover note to the next shift or region.
- **Why:**
  - Three shifts mean two handovers a day (D-031). A handover that depends on memory loses the open items at 03:00.
  - The daily check is L2's, not L1's (D-039). The NOC sees its result only when it creates work for L1.

### 3.10 What the NOC does not see

| Item | Why not |
|---|---|
| Cost and price | No L1 decision uses cost (D-033). |
| Capacity planning | It changes over hours and days; the wall is about minutes (SP5). Capacity guard rails reach L1 as alerts. |
| Daily check insights | They need expertise and environment context. They are L2's (D-039). |
| Trends beyond the last hour, on the wall | The wall is now. Trends are on the desktop drill-down. |
| Attack and breach data | Security is after 1.0 (D-044). |

## 4. Pages

| Path | UI | Main question |
|---|---|---|
| `/noc/wall` | Wall | The five questions, rotating (3.1, 3.2) |
| `/noc` | Desktop | The same five questions, with drill-down (3.3) |
| `/noc/alerts` | Desktop | What urgent issue is waiting, grouped by cause? (3.4) |
| `/noc/alert/{id}` | Desktop | What does the SOP say, and what may I do? (3.5–3.8) |
| `/noc/shift` | Desktop | What do I hand over? (3.9) |

- Five pages. SP5: L1 has simple needs. More pages would mean less use of each.

## 5. Open questions for the author

1. **One global NOC or regional NOCs?**
   - The design works for both: the wall shows every location, and a NOC can be scoped to its region.
   - Which is more common in your target banks?
   - Proposal: one global wall by default, with a per-region scope as a setting.
2. **Alert grouping.** PCM groups alerts on the same cause into one incident (3.4).
   - Proposal: PCM groups alerts by object relationship, for example a host failure and the alerts of its VMs.
   - L1 can split a group, but not merge alerts by hand. Manual merging hides unrelated problems inside one incident.
