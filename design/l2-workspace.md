# L2 workspace (Platform)

Status: draft for the author's review. Decisions proposed here move to [`decisions.md`](../decisions.md) once accepted.

Path: `privatecloud.acme.com/l2` (D-028).

## 1. The role

- SP5 calls this role **Platform**. It takes over when Level 1 cannot solve the problem.
- **What it does** (SP5 People):
  - Focuses on insight, not alerts. Looks at the big picture to stop alerts from happening.
  - Owns risk: configuration risk, and compliance risk after release 1.0 (D-022).
  - Advanced troubleshooting, often with logs.
  - Writes the knowledge base and the SOPs, and automates the SOPs.
  - After each problem it solves, updates the troubleshooting guide so L1 can handle the case next time.
  - Designs and maintains dashboards and alerts. It sets the thresholds L1 works with.
  - May specialize: vSAN, networking.
- **Cadence:**
  - daily check, 10 minutes, twice a day (D-039)
  - weekly check, 1 hour (D-042)
  - monthly review, 1 day
  - escalations at any time
  - mobile push for red alerts (D-031)
- **Scope:** VMware infrastructure (D-034), plus the Guest OS at OS level (D-038). Not applications.

**Why this role is the centre of PCM**
- L1 runs what L2 writes: SOPs, thresholds, actions.
- The Executive reads what L2 keeps healthy.
- If the L2 workspace is weak, every other workspace runs on stale rules.

## 2. What L2 is measured by

Everything in this workspace serves these outcomes. Each outcome is a number PCM can show.

| Outcome | Measure | Why it is the right measure |
|---|---|---|
| Fewer alerts | Alert count and intensity, trend over months | SP5: well-run operations have few alerts. Insight replaces most yellow alerts. |
| Fewer escalations of the same kind | Repeat escalations per problem type | Each solved problem should become an SOP that L1 can run. A repeat means the loop did not close. |
| Problems found before customers notice | Share of issues first found by a check, not by an alert or a complaint | This is the prevention window: the time between "we know" and "the customer knows". |
| Second time is fast | Time to diagnose a known problem | SP5: the first incident is forgivable once. The second is known within minutes. |

- What L2 is **not** measured by: tickets closed. SP5 aims to remove tickets, not to process them faster (why-a-new-framework).

## 3. Design considerations

### 3.1 The landing page is the check result, not the alert list

- **What:** `/l2` opens on the latest daily check: what needs a human, worst first.
- **Why:**
  - An alert is bottom up. One object crossed a threshold. It is the tip of the iceberg; many objects sit just below.
  - An alert list says nothing about the whole environment, and L2's job is the whole environment.
  - Opening on alerts trains L2 into reactive work. Opening on the check trains it into prevention.
  - Alerts are still one click away. They are a guard rail, not the starting point.

### 3.2 Three verdicts, never one health score

- **What:** the check result shows three separate verdicts.
  - **Present health:** is it up, is it fast, is it safe.
  - **Risk:** configuration, capacity trend, and compliance after 1.0.
  - **Efficiency:** waste.
- **Why:**
  - A single score drops on risk and waste too. It reads low while everything runs well, and soon nobody trusts it.
  - The three verdicts lead to different actions with different urgency:
    - present health means fix today;
    - risk means plan a change;
    - efficiency means reclaim when convenient.

  Mixing them hides which kind of work is waiting.

### 3.3 Top down, worst first, provider before consumer

- **What:** every list starts at the cluster, sorted by its worst KPI. From a failing cluster, PCM goes to its hosts, then to its VMs.
  - When a single VM is investigated, PCM first shows whether its cluster and host are serving their VMs well.
- **Why:**
  - At 100,000 VMs, starting from a VM is a needle in a haystack. A parent's verdict tells where to look next.
  - "Clear the infrastructure first." If the cluster fails most of its VMs, troubleshooting one VM wastes hours.
  - Cluster and host health is judged from their VMs (worst VM and 90th percentile), never from cluster averages. An average hides the victim.

### 3.4 One fixed order of checks, the what before the why

- **What:** the investigation view always follows the SP5 order.
  - **Down:** log → saturation → configuration → known bug.
  - **Slow:** contention → consumption → configuration → known bug → log.
  - Configuration and known bugs sit inside each pillar, not after it.
- **Why:**
  - Experts under pressure skip steps. The classic skip is jumping to "CPU is at 100%" when there is no contention: that is a busy VM, not a slow one.
  - A fixed order makes two engineers reach the same conclusion. It also lets PCM pre-run the steps and show which ones pass, so L2 starts at the first failed step.
  - The same order appears in L1's SOPs, in the daily check and in troubleshooting. One mental model across the team.

### 3.5 The VM and the Guest OS are separate, with evidence for each side

- **What:** investigation pages show VM health and Guest OS health side by side, as two objects. Each has its "on my court" evidence:
  - VM: CPU Ready, Co-stop, Overlap, Other Wait; memory latency, swapped, ballooned; disk latency; vMotion stun time.
  - Guest OS: run queue, context switches, paging.
- **Why:**
  - "A day in the life of a cloud admin" (SP5 source): the application team proves the Guest OS is fine and blames the shared platform. Without evidence on both sides, the argument is about reputation, not data.
  - With both sides shown, the conversation takes minutes:
    - The VM is not waiting → the cause is inside Windows or Linux, and the evidence goes to the OS team.
    - The VM is waiting → it is the platform's problem, and L2 owns it.

### 3.6 Business context is an input, not a memory

- **What:** L2 records the expected events: month-end batch, a planned migration, a retail peak, a DR test, a maintenance window. PCM reads them when it judges what is abnormal.
- **Why:**
  - SP5: an insight is useless to someone who does not know the environment. Anomaly detection by mathematics alone gives false positives, because it has no business context.
  - Today this context lives in one senior engineer's head. That fails SP5's acid test: the lead takes a long holiday and nobody calls them.
  - Written down, the context serves:
    - the daily check, which knows that low IOPS on a sale day is bad;
    - Agent E2, which explains a finding with today's context;
    - the next engineer on shift.

### 3.7 PCM proposes, L2 approves; trust in an action is earned

- **What:**
  - The daily and weekly checks come with proposed fixes. L2 approves or rejects each one (D-029).
  - PCM keeps a record per action type: how often it was approved, and how often it was rolled back.
  - When an action type has a clean record, L2 can promote it to automatic. This is an explicit change by L2, recorded in the audit log. PCM never promotes on its own.
- **Why:**
  - Self-driving operations (D-025) are earned one action type at a time. Turning on automation for everything on day one is how a bad rule moves 500 VMs at 10:00.
  - SP5: the rules are finite, and the usual fix is moving VMs out of a cluster. These are exactly the actions that build a clean record quickly.
  - A rejection with a reason is data. It tells L2 which rule is wrong.

### 3.8 Escalations arrive complete, and the loop closes

- **What:**
  - An L1 escalation arrives with its evidence already gathered (D-040).
  - L2 accepts it or rejects it with a reason. Rejection should be rare, because PCM fills the evidence.
  - An escalation closes only with:
    1. a root cause;
    2. a corrective action that prevents a repeat;
    3. a decision on detection: a new check step, a new alert, or a new SOP so L1 can handle it next time.
- **Why:**
  - SP5: an RCA is done when the alert that detects a recurrence is set up, not when the cause is named.
  - L2 then becomes measurably less needed for known problems (section 2). Without this rule, L2 solves the same problem every month.
  - An L1 escalation that L2 rejects for missing evidence points to a gap in the SOP. It is fed back into SOP authoring.

### 3.9 L2 authors what L1 runs: SOPs, thresholds, actions

- **What:**
  - L2 writes and edits SOPs (in `/docs`), check rules, thresholds and the SOP buttons L1 may press.
  - Agent E2 drafts an SOP from a closed RCA. L2 reviews and publishes it. The NOC sees the new SOP at once.
  - Every published change is versioned.
- **Why:**
  - SP5 People: L2 develops and automates the SOPs, and sets the thresholds L1 uses.
  - Documentation and action in one place (D-024). The SOP that L1 reads is the same object that drives L1's buttons, so they cannot drift apart.
  - Any threshold change is tested against the last 30 days first. PCM shows how many alerts the new value would have raised.
    - Reason: alert storms come from thresholds set conservatively and never measured. If a threshold cannot be shown to be rare, it should not ship.

### 3.10 Configuration is reviewed by urgency, against a standard

- **What:** the configuration page orders findings by the SP5 time dimension:
  1. **Correct it:** wrong, insecure, against the standard.
  2. **Update it:** old versions, oldest first, out of support first.
  3. **Simplify it:** variance and complexity.
  4. **Optimize it:** cost and capacity.

  Every finding offers two choices: fix the setting, or fix the standard.
- **Why:**
  - Thousands of settings exist. Grouping them by product feature hides urgency. Grouping by Day 2 impact shows it.
  - Drift means nothing without a documented standard. When reality differs, one of the two is wrong. Sometimes the standard is out of date. Offering "fix the standard" stops L2 from forcing a bad standard onto a good estate.
  - Default filter is the Gold class of service, so critical workloads come first in a large estate.

### 3.11 One workspace, with specialty lenses

- **What:** one L2 workspace. Storage and network specialists use lenses inside it (the default is platform), not separate workspaces.
- **Why:**
  - With vSAN and NSX, storage and network are software in the same stack. One incident often crosses all three.
  - Separate workspaces bring back the "ping-pong between teams" that SP5 calls the manual stage of maturity. Each team proves "it is not on my court" with a different screen.
  - One workspace means one evidence set, one timeline, one RCA.
  - The lens changes the default view, not the data. SP5's storage test: agree within 1 minute whether a problem is storage.
  - This follows D-011 (one workspace per role): storage and network specialists share the Platform role.

### 3.12 Time windows follow the job

| Job | Default window | Why |
|---|---|---|
| Troubleshooting | Last 8–24 hours, any point in the past | Older data rarely matters for a live problem. By the time someone looks, the problem may be gone, so going back to any point in time is a must. |
| Daily check | Next 12 hours, from 1 week of data | Prevent today's alerts. |
| Weekly check | 1 week, per-instance metrics | Patterns a day cannot show (D-042). |
| Monthly review | 1 year | Baselines, quarterly patterns, large problems. |

- Performance reads the **20-second peak** of each 5-minute interval, not the 5-minute average. A spike of a few seconds disappears in 300 seconds of average.

### 3.13 Logs beside metrics

- **What:** every investigation shows the log events of the same object and time window next to its metrics.
- **Why:**
  - Availability lives mostly in logs, not metrics.
  - The root cause is often a log message on another object that never became an alarm.
  - SP5 check before turning a log message into an alert: count how often it appears on healthy objects over a week. PCM runs this count when L2 proposes a log-based alert. A message seen 1,000 times in 5 days on healthy hosts is noise.

### 3.14 Agent E2: explains and drafts, never decides

- **Agent E2 may:**
  - explain a finding in the context of the knowledge base and today's business context;
  - suggest the next check step;
  - draft the RCA and the SOP;
  - answer "why" questions with sources.
- **Agent E2 may not:**
  - set a severity;
  - approve an action;
  - promote an action to automatic;
  - close an escalation.
- **Why:**
  - A confident wrong answer from an LLM at L2 level spreads: it becomes an SOP that L1 runs at 03:00.
  - Grounding in the knowledge base plus a human approval keeps the knowledge correct.

## 4. Pages

| Path | Job | Main question |
|---|---|---|
| `/l2` | Daily check result | What needs me today? |
| `/l2/escalations` | Escalations from L1 | What did L1 hand over, and is it complete? |
| `/l2/investigate/{object}` | Troubleshooting | Why is it down or slow? |
| `/l2/weekly` | Weekly check result | What does a week show that a day did not? |
| `/l2/monthly` | Monthly review | What larger problem should we fix this month? |
| `/l2/configuration` | Configuration risk | What is wrong, outdated, complex or wasteful? |
| `/l2/inventory` | Detailed inventory and changes (D-020) | What changed, and is that expected? |
| `/l2/context` | Business calendar (3.6) | What is expected this week? |
| `/l2/authoring` | SOPs, check rules, thresholds, L1 actions, alerts | What should L1 and PCM do next time? |

- Nine pages, compared with five for NOC. L2's work is broader and deeper: the NOC answers one question in the present; L2 owns past, present and future.
- No capacity planning pages: that is the Capacity workspace (D-014).
- SP5 People: capacity "does not get involved in the day-to-day capacity". The reverse also holds: day-to-day capacity (a cluster that cannot serve its current demand) is a performance matter for L2, not a planning matter.

## 5. Open questions for the author

1. **Monthly review attendees.** SP5 says monthly work solves "larger, more complex and political problems". Usually that needs Architecture in the room.
   - Proposal: the review runs in the L2 workspace. Architecture joins, but has no workspace in 1.0.
2. **Security forensics.** "Is it breached" is a forensic investigation, not troubleshooting (SP5), and security operations is out of scope (D-008).
   - Proposal: when a "safe" finding points to a breach, L2 secures the evidence and hands over to the security team. PCM does not investigate the breach.
3. **Who owns PCM's own configuration** (class-of-service definitions, action tiers)?
   - Proposal: L2 proposes changes. The Operations Manager approves them after 1.0. Until then, L2 owns them.
